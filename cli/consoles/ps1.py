"""PS1-specific disc handling helpers."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Ps1DiscImage:
    """Represents a PS1 disc image on disk."""

    path: Path
    sector_size: int = 2336
    user_data_offset: int = 24

    def iso_to_bin_offset(self, iso_offset: int, *, sector_index: int) -> int:
        """Convert an ISO offset to a BIN offset for a known sector index."""
        byte_in_sector = iso_offset % 2048
        return (sector_index * self.sector_size) + self.user_data_offset + byte_in_sector
