"""Generate web status data from registered game CSV files."""

from __future__ import annotations

import json
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cli.games import ps1  # noqa: F401
from cli.games.registry import GAME_REGISTRY, GameDefinition
from cli.strings import derive_translation_status, encoded_irish_length, read_translation_csv


DEFAULT_OUTPUT = REPO_ROOT / "web" / "static" / "status.json"
DEFAULT_REPO_URL = "https://github.com/aaronsnig501/gaeilge-sa-chonsol"
DEFAULT_ISSUES_URL = f"{DEFAULT_REPO_URL}/issues"
STATUS_PLANNED = "planned"
STATUS_IN_PROGRESS = "in-progress"
STATUS_COMPLETE = "complete"


def translated_count(rows: list) -> int:
    """Count rows with a non-empty Irish translation."""
    return sum(1 for row in rows if row.irish.strip())


def percent(translated: int, total: int) -> int:
    """Build a rounded translation percentage."""
    if total <= 0:
        return 0
    return round((translated / total) * 100)


def empty_status_breakdown() -> dict[str, int]:
    """Return an empty per-status counter."""
    return {
        "verified": 0,
        "draft": 0,
        "compromised": 0,
        "untranslated": 0,
    }


def empty_flag_counts() -> dict[str, int]:
    """Return empty per-flag counters."""
    return {
        "verified": 0,
        "compromised": 0,
    }


def build_categories(game: GameDefinition) -> list[dict[str, object]]:
    """Group translation rows by category for a game."""
    assert game.string_table is not None
    rows = read_translation_csv(
        game.string_table.csv_path,
        source_path=game.string_table.source_path,
        category_groups=game.string_table.category_groups,
    )
    grouped: OrderedDict[str, dict[str, object]] = OrderedDict()

    for row in rows:
        category = grouped.setdefault(
            row.category,
            {
                "total": 0,
                "translated": 0,
                "verified": 0,
                "status_breakdown": empty_status_breakdown(),
                "flags": empty_flag_counts(),
                "strings": [],
            },
        )
        status = derive_translation_status(
            irish=row.irish,
            verified=row.verified,
            compromised=row.compromised,
        )
        used = encoded_irish_length(row.irish)
        string_payload: dict[str, object] = {
            "offset": row.offset,
            "budget": row.budget,
            "used": used,
            "english": row.english,
            "irish": row.irish,
            "status": status,
            "verified": row.verified,
            "compromised": row.compromised,
        }
        if row.note.strip():
            string_payload["note"] = row.note.strip()

        category["total"] += 1
        if row.irish.strip():
            category["translated"] += 1
        if row.verified and row.irish.strip():
            category["verified"] += 1
            category["flags"]["verified"] += 1
        if row.compromised and row.irish.strip():
            category["flags"]["compromised"] += 1
        category["status_breakdown"][status] += 1
        category["strings"].append(string_payload)

    return [
        {
            "name": name,
            "total": values["total"],
            "translated": values["translated"],
            "verified": values["verified"],
            "percent": percent(values["translated"], values["total"]),
            "status_breakdown": values["status_breakdown"],
            "flags": values["flags"],
            "strings": values["strings"],
        }
        for name, values in grouped.items()
    ]


def infer_status(progress_percent: int, translated: int) -> str:
    """Infer a site status label from translation progress."""
    if progress_percent >= 100:
        return STATUS_COMPLETE
    if translated > 0:
        return STATUS_IN_PROGRESS
    return STATUS_PLANNED


def find_notes_path(game: GameDefinition) -> str | None:
    """Return a site notes route when a markdown page exists."""
    short_name = game.key.split(".", 1)[1]
    candidate = REPO_ROOT / "web" / "src" / "routes" / "games" / game.console / short_name / "notes" / "+page.md"
    if candidate.exists():
        return f"/games/{game.console}/{short_name}/notes"
    return None


def patch_available(game: GameDefinition) -> bool:
    """Detect whether any BPS patch artifacts exist for a game."""
    patches_dir = REPO_ROOT / game.project_dir / "patches"
    return patches_dir.exists() and any(patches_dir.glob("*.bps"))


def build_game_status(game: GameDefinition) -> dict[str, object]:
    """Build site status data for one registered game."""
    assert game.string_table is not None
    rows = read_translation_csv(
        game.string_table.csv_path,
        source_path=game.string_table.source_path,
        category_groups=game.string_table.category_groups,
    )
    translated = translated_count(rows)
    total = len(rows)
    progress_percent = percent(translated, total)
    short_name = game.key.split(".", 1)[1]
    status_breakdown = empty_status_breakdown()
    flags = empty_flag_counts()
    for row in rows:
        status_breakdown[
            derive_translation_status(
                irish=row.irish,
                verified=row.verified,
                compromised=row.compromised,
            )
        ] += 1
        if row.verified and row.irish.strip():
            flags["verified"] += 1
        if row.compromised and row.irish.strip():
            flags["compromised"] += 1

    payload: dict[str, object] = {
        "id": short_name,
        "title": game.title,
        "console": game.console,
        "console_label": game.console_label or game.console.upper(),
        "status": infer_status(progress_percent, translated),
        "version": game.version,
        "repo_path": game.project_dir.as_posix(),
        "patch_available": patch_available(game),
        "help_wanted": progress_percent < 100,
        "progress": {
            "total": total,
            "translated": translated,
            "percent": progress_percent,
        },
        "status_breakdown": status_breakdown,
        "flags": flags,
        "categories": build_categories(game),
        "region": game.region,
        "serial": game.serial,
        "description": game.description,
        "accent": game.accent,
        "repo_url": DEFAULT_REPO_URL,
        "issues_url": DEFAULT_ISSUES_URL,
    }

    notes_path = find_notes_path(game)
    if notes_path:
        payload["notes_path"] = notes_path

    return payload


def generate_status_payload() -> dict[str, object]:
    """Generate the full site payload from all registered games with CSVs."""
    games = []
    for key in sorted(GAME_REGISTRY):
        game = GAME_REGISTRY[key]
        if game.string_table is None:
            continue
        csv_path = REPO_ROOT / game.string_table.csv_path
        if not csv_path.exists():
            continue
        games.append(build_game_status(game))

    return {
        "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "games": games,
    }


def write_status(output_path: Path) -> Path:
    """Write generated status JSON to disk."""
    payload = generate_status_payload()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    """CLI entry point for local and CI usage."""
    output = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    written = write_status(output)
    print(written.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
