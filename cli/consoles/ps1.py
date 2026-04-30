"""PS1-specific disc handling helpers."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Ps1DiscImage:
    """Represents a PS1 disc image on disk."""

    path: Path
    sector_size: int = 2352
    user_data_offset: int = 24

    def iso_to_bin_offset(self, iso_offset: int, *, sector_index: int) -> int:
        """Convert an ISO offset to a BIN offset for a known sector index."""
        byte_in_sector = iso_offset % 2048
        return (sector_index * self.sector_size) + self.user_data_offset + byte_in_sector


def strip_ps1_bin_to_iso(source: Path, destination: Path) -> None:
    """Strip BIN sector headers and write a mountable ISO image."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as f_in, destination.open("wb") as f_out:
        sector_size = 2352
        header_size = 24
        data_size = 2048
        while True:
            sector = f_in.read(sector_size)
            if len(sector) < sector_size:
                break
            f_out.write(sector[header_size : header_size + data_size])
