"""Registry types for supported games."""

from dataclasses import dataclass, field
from pathlib import Path


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
