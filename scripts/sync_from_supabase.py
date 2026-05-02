"""Sync translated string data from Supabase back into repo CSVs."""

from __future__ import annotations

import csv
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

try:
    from supabase import Client, create_client
except ImportError as error:  # pragma: no cover - dependency is installed in CI
    raise SystemExit(
        "Missing dependency: supabase. Install it with `python3 -m pip install supabase`."
    ) from error


EXPECTED_FIELDS = ["offset", "budget", "english", "irish", "verified", "compromised", "note"]


@dataclass(frozen=True, slots=True)
class SyncResult:
    """Result summary for one synced game CSV."""

    game: str
    csv_path: Path
    changed_rows: int
    missing_rows: int


def get_required_env(name: str) -> str:
    """Read a required environment variable or exit with a clear error."""
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def get_supabase_client() -> Client:
    """Construct an admin Supabase client for CI sync operations."""
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


def normalize_flag(value: object) -> str:
    """Normalize a boolean-ish value for CSV storage."""
    return "true" if bool(value) else ""


def normalize_text(value: object) -> str:
    """Normalize nullable text values for CSV storage."""
    if value is None:
        return ""
    return str(value)


def fetch_supabase_rows(client: Client, game_id: str) -> dict[str, dict[str, object]]:
    """Fetch all string rows for a game keyed by lowercase offset."""
    response = (
        client.table("strings")
        .select("game_id,offset,irish,verified,compromised,note")
        .eq("game_id", game_id)
        .execute()
    )
    rows = response.data or []
    return {
        str(row["offset"]).lower(): row
        for row in rows
        if row.get("offset")
    }


def sync_game_csv(client: Client, game: GameDefinition) -> SyncResult:
    """Update one game's CSV from Supabase row data."""
    assert game.string_table is not None
    csv_path = REPO_ROOT / game.string_table.csv_path
    supabase_rows = fetch_supabase_rows(client, game.key.split(".", 1)[1])

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_FIELDS:
            raise SystemExit(
                f"{csv_path.relative_to(REPO_ROOT)} has unexpected columns: {reader.fieldnames!r}"
            )
        rows = list(reader)

    changed_rows = 0
    missing_rows = 0
    for row in rows:
        offset_key = row["offset"].lower()
        supabase_row = supabase_rows.get(offset_key)
        if supabase_row is None:
            missing_rows += 1
            continue

        updated_fields = {
            "irish": normalize_text(supabase_row.get("irish")),
            "verified": normalize_flag(supabase_row.get("verified")),
            "compromised": normalize_flag(supabase_row.get("compromised")),
            "note": normalize_text(supabase_row.get("note")),
        }

        if any(row[field] != value for field, value in updated_fields.items()):
            row.update(updated_fields)
            changed_rows += 1

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return SyncResult(
        game=game.key,
        csv_path=csv_path,
        changed_rows=changed_rows,
        missing_rows=missing_rows,
    )


def main() -> None:
    """CLI entry point for syncing all registered game CSVs."""
    client = get_supabase_client()
    results = [sync_game_csv(client, game) for game in iter_registered_games()]

    for result in results:
        rel_path = result.csv_path.relative_to(REPO_ROOT)
        print(
            f"{result.game}: updated {result.changed_rows} rows in {rel_path}"
            f" ({result.missing_rows} offsets not present in Supabase)"
        )


if __name__ == "__main__":
    main()
