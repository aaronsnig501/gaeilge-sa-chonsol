"""Registry types for supported games."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StringTableDefinition:
    """Metadata required to extract a game's translatable string table."""

    source_path: Path
    csv_path: Path
    executable_iso_offset: int
    category_groups: dict[str, str] = field(default_factory=dict)
    preserve_metadata: dict[int, int] = field(default_factory=dict)
    formula_checks: tuple[tuple[int, int], ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class WadDefinition:
    """Metadata for a game's WAD archive."""

    archive_path: Path
    known_subfiles: dict[int, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ThemeDefinition:
    """Presentation theme for game-specific CLI styling."""

    header_style: str = "bold"
    accent_style: str = "cyan"
    success_style: str = "green"
    spinner_style: str = "cyan"
    rule_style: str = "dim"


@dataclass(frozen=True, slots=True)
class GameDefinition:
    """Metadata for a supported game target."""

    key: str
    title: str
    console: str
    region: str
    serial: str
    project_dir: Path
    notes: tuple[str, ...] = field(default_factory=tuple)
    rom_markers: tuple[bytes, ...] = field(default_factory=tuple)
    release_messages: tuple[str, ...] = field(default_factory=tuple)
    release_message_interval_range: tuple[float, float] = (5.0, 8.0)
    theme: ThemeDefinition = field(default_factory=ThemeDefinition)
    string_table: StringTableDefinition | None = None
    wad: WadDefinition | None = None


GAME_REGISTRY: dict[str, GameDefinition] = {}


def register_game(game: GameDefinition) -> GameDefinition:
    """Register a game definition for CLI lookup."""
    GAME_REGISTRY[game.key] = game
    return game


def get_game(key: str) -> GameDefinition:
    """Look up a game by registry key."""
    return GAME_REGISTRY[key]


def get_game_by_parts(console: str, game: str) -> GameDefinition:
    """Look up a game by console and short game name."""
    return get_game(f"{console}.{game}")


def find_game_by_short_name(game: str) -> GameDefinition:
    """Find a game by its short name when it is unique in the registry."""
    matches = [definition for key, definition in GAME_REGISTRY.items() if key.split(".", 1)[1] == game]
    if not matches:
        raise KeyError(game)
    if len(matches) > 1:
        raise ValueError(f"Ambiguous game name: {game}")
    return matches[0]
