"""WAD archive helpers."""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path


HEADER_ENTRY_COUNT = 512
HEADER_SIZE = HEADER_ENTRY_COUNT * 4
SUBFILE_PATTERN = re.compile(r"^sf_(\d+)\.bin$")


@dataclass(frozen=True, slots=True)
class WadSubfile:
    """A subfile entry in a WAD archive."""

    index: int
    offset: int
    size: int


def read_wad_entries(archive: Path) -> list[WadSubfile]:
    """Read subfile offsets and sizes from a WAD archive header."""
    with archive.open("rb") as handle:
        header = struct.unpack("<" + "I" * HEADER_ENTRY_COUNT, handle.read(HEADER_SIZE))

    entries: list[WadSubfile] = []
    for index in range(HEADER_ENTRY_COUNT // 2):
        offset = header[index * 2]
        size = header[index * 2 + 1]
        if size == 0:
            continue
        entries.append(WadSubfile(index=index + 1, offset=offset, size=size))
    return entries


def extract_wad(archive: Path, output_dir: Path, *, subfile: int | None = None) -> list[WadSubfile]:
    """Extract one or all WAD subfiles."""
    entries = read_wad_entries(archive)
    selected = [entry for entry in entries if subfile is None or entry.index == subfile]
    if subfile is not None and not selected:
        raise ValueError(f"Subfile {subfile} not found in {archive}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with archive.open("rb") as handle:
        for entry in selected:
            handle.seek(entry.offset)
            data = handle.read(entry.size)
            (output_dir / f"sf_{entry.index}.bin").write_bytes(data)
    return selected


def pack_wad(input_dir: Path, output_path: Path) -> list[WadSubfile]:
    """Pack a directory of `sf_*.bin` files into a WAD archive."""
    matched = []
    for path in sorted(input_dir.iterdir()):
        match = SUBFILE_PATTERN.match(path.name)
        if match:
            matched.append((int(match.group(1)), path))

    if not matched:
        raise ValueError(f"No sf_*.bin files found in {input_dir}")

    expected = list(range(1, matched[-1][0] + 1))
    actual = [index for index, _ in matched]
    if actual != expected:
        raise ValueError("Subfiles must be contiguous and start at sf_1.bin")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    header = [0] * HEADER_ENTRY_COUNT
    entries: list[WadSubfile] = []
    offset = HEADER_SIZE

    with output_path.open("wb") as handle:
        handle.write(b"\x00" * HEADER_SIZE)
        for index, path in matched:
            data = path.read_bytes()
            header[(index - 1) * 2] = offset
            header[(index - 1) * 2 + 1] = len(data)
            handle.seek(offset)
            handle.write(data)
            entries.append(WadSubfile(index=index, offset=offset, size=len(data)))
            offset += len(data)

        handle.seek(0)
        handle.write(struct.pack("<" + "I" * HEADER_ENTRY_COUNT, *header))

    return entries
