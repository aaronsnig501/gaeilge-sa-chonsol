"""String table loading and extraction helpers."""

from __future__ import annotations

import ast
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from cli.config import REPO_ROOT
from cli.games.registry import StringTableDefinition

SYNC_PATTERN = re.compile(b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00")


@dataclass(frozen=True, slots=True)
class StringEntry:
    """A translatable string entry."""

    offset: int
    budget: int


@dataclass(frozen=True, slots=True)
class CsvTranslationRow:
    """A translation row from the extracted CSV."""

    offset: str
    budget: int
    english: str
    irish: str


def load_string_entries(source_path: Path) -> list[StringEntry]:
    """Load offset and budget data from an existing TRANSLATIONS table."""
    source_path = source_path if source_path.is_absolute() else REPO_ROOT / source_path
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TRANSLATIONS":
                    translations = ast.literal_eval(node.value)
                    return [
                        StringEntry(offset=offset, budget=value[3])
                        for offset, value in sorted(translations.items())
                    ]
    raise ValueError(f"TRANSLATIONS table not found in {source_path}")


def load_existing_irish(csv_path: Path) -> dict[str, str]:
    """Load any existing Irish translations keyed by offset string."""
    if not csv_path.exists():
        return {}

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {
            row["offset"].lower(): row.get("irish", "")
            for row in reader
            if row.get("offset")
        }


def read_ps1_string(rom_bytes: bytes, *, executable_iso_offset: int, offset: int, budget: int, syncs: list[int]) -> str:
    """Read a null-terminated ASCII string from a PS1 BIN image."""
    iso_offset = executable_iso_offset + offset
    iso_sector = iso_offset // 2048
    byte_in_sector = iso_offset % 2048
    bin_offset = syncs[iso_sector] + byte_in_sector + 24
    data = rom_bytes[bin_offset : bin_offset + budget]
    raw = data.split(b"\x00", 1)[0]
    return raw.decode("ascii", errors="ignore").strip()


def build_sync_map(rom_bytes: bytes) -> list[int]:
    """Find PS1 BIN sector sync headers for ISO-to-BIN conversion."""
    return [match.start() for match in SYNC_PATTERN.finditer(rom_bytes)]


def extract_strings(rom_path: Path, table: StringTableDefinition) -> list[dict[str, str | int]]:
    """Extract all configured strings from a PS1 ROM image."""
    rom_bytes = rom_path.read_bytes()
    syncs = build_sync_map(rom_bytes)
    entries = load_string_entries(table.source_path)

    rows: list[dict[str, str | int]] = []
    for entry in entries:
        rows.append(
            {
                "offset": f"0x{entry.offset:x}",
                "budget": entry.budget,
                "english": read_ps1_string(
                    rom_bytes,
                    executable_iso_offset=table.executable_iso_offset,
                    offset=entry.offset,
                    budget=entry.budget,
                    syncs=syncs,
                ),
            }
        )
    return rows


def write_translation_csv(rows: list[dict[str, str | int]], output_path: Path) -> None:
    """Write extracted strings to CSV, preserving any existing Irish values."""
    existing_irish = load_existing_irish(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["offset", "budget", "english", "irish"])
        writer.writeheader()
        for row in rows:
            offset_key = str(row["offset"]).lower()
            writer.writerow(
                {
                    "offset": row["offset"],
                    "budget": row["budget"],
                    "english": row["english"],
                    "irish": existing_irish.get(offset_key, ""),
                }
            )


def read_translation_csv(csv_path: Path) -> list[CsvTranslationRow]:
    """Read translation CSV rows."""
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            CsvTranslationRow(
                offset=row["offset"],
                budget=int(row["budget"]),
                english=row["english"],
                irish=row.get("irish", ""),
            )
            for row in reader
        ]
