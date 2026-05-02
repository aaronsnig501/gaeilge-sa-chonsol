"""Seed or refresh Supabase string rows from repo CSVs."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cli.games import ps1  # noqa: F401
from cli.games.registry import GAME_REGISTRY, GameDefinition
from cli.strings import read_translation_csv

try:
    from supabase import Client, create_client
except ImportError as error:  # pragma: no cover - dependency is installed in CI
    raise SystemExit(
        "Missing dependency: supabase. Install it with `python3 -m pip install supabase`."
    ) from error


UPSERT_BATCH_SIZE = 500


@dataclass(frozen=True, slots=True)
class SeedResult:
    """Summary for one seeded game."""

    game: str
    row_count: int


def get_required_env(name: str) -> str:
    """Read a required environment variable or exit with a clear error."""
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def get_supabase_client() -> Client:
    """Construct an admin Supabase client for seed operations."""
    url = get_required_env("SUPABASE_URL")
    key = get_required_env("SUPABASE_SERVICE_KEY")
    return create_client(url, key)


def iter_registered_games() -> Iterable[GameDefinition]:
    """Yield games that have a registered translation CSV."""
    for key in sorted(GAME_REGISTRY):
        game = GAME_REGISTRY[key]
        if game.string_table is None:
            continue
        yield game


def build_payloads(game: GameDefinition) -> list[dict[str, object]]:
    """Build Supabase upsert rows from a game's CSV."""
    assert game.string_table is not None
    rows = read_translation_csv(
        REPO_ROOT / game.string_table.csv_path,
        source_path=REPO_ROOT / game.string_table.source_path,
        category_groups=game.string_table.category_groups,
    )
    short_game_id = game.key.split(".", 1)[1]
    return [
        {
            "game_id": short_game_id,
            "offset": row.offset,
            "english": row.english,
            "irish": row.irish or None,
            "budget": row.budget,
            "verified": row.verified,
            "compromised": row.compromised,
            "note": row.note or None,
        }
        for row in rows
    ]


def chunked(items: list[dict[str, object]], size: int) -> Iterable[list[dict[str, object]]]:
    """Yield lists in bounded chunks for API upserts."""
    for index in range(0, len(items), size):
        yield items[index : index + size]


def seed_game(client: Client, game: GameDefinition) -> SeedResult:
    """Upsert one game's CSV rows into Supabase."""
    payloads = build_payloads(game)
    if payloads:
        for batch in chunked(payloads, UPSERT_BATCH_SIZE):
            (
                client.table("strings")
                .upsert(batch, on_conflict="game_id,offset")
                .execute()
            )
    return SeedResult(game=game.key, row_count=len(payloads))


def main() -> None:
    """CLI entry point for seeding all registered games into Supabase."""
    client = get_supabase_client()
    results = [seed_game(client, game) for game in iter_registered_games()]
    for result in results:
        print(f"{result.game}: upserted {result.row_count} rows into Supabase")


if __name__ == "__main__":
    main()
