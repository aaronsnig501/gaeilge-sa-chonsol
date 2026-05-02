"""Backfill explicit status/note columns into translation CSV files."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cli.games import ps1  # noqa: F401
from cli.games.registry import GAME_REGISTRY
from cli.strings import derive_translation_status


FIELDNAMES = ["offset", "budget", "english", "irish", "verified", "compromised", "note"]


def backfill_csv(csv_path: Path) -> None:
    """Rewrite one CSV with explicit status/note columns."""
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    normalized_rows = []
    for row in rows:
        irish = (row.get("irish") or "").strip()
        verified = (row.get("verified") or "").strip().lower() in {"1", "true", "yes", "y"}
        compromised = (row.get("compromised") or "").strip().lower() in {"1", "true", "yes", "y"}
        legacy_status = (row.get("status") or "").strip().lower()
        if legacy_status == "verified":
            verified = True
        elif legacy_status == "compromised":
            compromised = True
        elif legacy_status == "untranslated" and not irish:
            verified = False
            compromised = False
        elif legacy_status == "draft":
            verified = False
            compromised = False

        # Force empty rows back to a clean untranslated state.
        if derive_translation_status(irish=irish, verified=verified, compromised=compromised) == "untranslated":
            verified = False
            compromised = False

        normalized_rows.append(
            {
                "offset": row["offset"],
                "budget": row["budget"],
                "english": row["english"],
                "irish": irish,
                "verified": "true" if verified else "",
                "compromised": "true" if compromised else "",
                "note": (row.get("note") or "").strip(),
            }
        )

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(normalized_rows)


def main() -> None:
    """Backfill all registered translation CSV files in the repo."""
    written: list[Path] = []
    for game in GAME_REGISTRY.values():
        if game.string_table is None:
            continue
        csv_path = REPO_ROOT / game.string_table.csv_path
        if not csv_path.exists():
            continue
        backfill_csv(csv_path)
        written.append(csv_path.relative_to(REPO_ROOT))

    for path in written:
        print(path)


if __name__ == "__main__":
    main()
