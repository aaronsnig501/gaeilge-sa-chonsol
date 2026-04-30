"""String table loading and extraction helpers."""

from __future__ import annotations

import ast
import csv
import shutil
import re
from dataclasses import dataclass
from pathlib import Path

from cli.config import REPO_ROOT
from cli.games.registry import StringTableDefinition
from cli.text import encode_rom_text

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


@dataclass(frozen=True, slots=True)
class BudgetViolation:
    """A translation row that exceeds its byte budget."""

    offset: str
    encoded: str
    encoded_length: int
    budget: int


@dataclass(frozen=True, slots=True)
class TranslationValidation:
    """Summary of translation validation for a CSV."""

    rows: list[CsvTranslationRow]
    translated_rows: list[CsvTranslationRow]
    untranslated_count: int
    over_budget: list[BudgetViolation]


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


def iso_to_bin_offset(iso_offset: int, syncs: list[int]) -> int:
    """Convert an ISO offset to a BIN offset using the sector sync map."""
    iso_sector = iso_offset // 2048
    byte_in_sector = iso_offset % 2048
    return syncs[iso_sector] + byte_in_sector + 24


def verify_formula(table: StringTableDefinition, syncs: list[int]) -> None:
    """Verify known ISO-to-BIN mappings for a game's executable."""
    for offset, expected_bin_offset in table.formula_checks:
        actual = iso_to_bin_offset(table.executable_iso_offset + offset, syncs)
        if actual != expected_bin_offset:
            raise ValueError(
                f"Formula check failed for 0x{offset:x}: expected 0x{expected_bin_offset:x}, got 0x{actual:x}"
            )


def extract_strings(rom_path: Path, table: StringTableDefinition) -> list[dict[str, str | int]]:
    """Extract all configured strings from a PS1 ROM image."""
    rom_bytes = rom_path.read_bytes()
    syncs = build_sync_map(rom_bytes)
    verify_formula(table, syncs)
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


def validate_translation_rows(rows: list[CsvTranslationRow]) -> TranslationValidation:
    """Validate translation rows against byte budgets."""
    translated_rows = [row for row in rows if row.irish.strip()]
    over_budget: list[BudgetViolation] = []

    for row in translated_rows:
        encoded = encode_rom_text(row.irish.strip())
        try:
            encoded_bytes = encoded.encode("ascii")
        except UnicodeEncodeError as error:
            raise ValueError(f"{row.offset}: translation contains unsupported characters") from error
        encoded_length = len(encoded_bytes)
        if encoded_length > row.budget:
            over_budget.append(
                BudgetViolation(
                    offset=row.offset,
                    encoded=encoded,
                    encoded_length=encoded_length,
                    budget=row.budget,
                )
            )

    return TranslationValidation(
        rows=rows,
        translated_rows=translated_rows,
        untranslated_count=len(rows) - len(translated_rows),
        over_budget=over_budget,
    )


def copy_rom(source: Path, output: Path) -> None:
    """Copy the ROM to a new output path before patching."""
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source, output)


def apply_translations_to_rom(
    output_rom: Path,
    table: StringTableDefinition,
    rows: list[CsvTranslationRow],
) -> tuple[int, list[BudgetViolation]]:
    """Apply valid translations to a copied ROM image."""
    rom_bytes = output_rom.read_bytes()
    syncs = build_sync_map(rom_bytes)
    verify_formula(table, syncs)

    validation = validate_translation_rows(rows)
    valid_rows = {
        violation.offset: violation
        for violation in validation.over_budget
    }

    applied = 0
    with output_rom.open("r+b") as handle:
        for row in validation.translated_rows:
            if row.offset in valid_rows:
                continue
            encoded = encode_rom_text(row.irish.strip()).encode("ascii")
            offset = int(row.offset, 16)
            bin_offset = iso_to_bin_offset(table.executable_iso_offset + offset, syncs)
            handle.seek(bin_offset)
            handle.write(encoded)
            if offset in table.preserve_metadata:
                original_len = table.preserve_metadata[offset]
                pad = original_len - len(encoded)
                if pad > 0:
                    handle.write(b"\x00" * pad)
            else:
                handle.write(b"\x00" * (row.budget - len(encoded)))
            applied += 1

    return applied, validation.over_budget
