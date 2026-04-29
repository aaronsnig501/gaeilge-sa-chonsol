"""Spyro the Dragon configuration and offsets."""

from pathlib import Path

from cli.games.registry import GameDefinition, register_game

SPYRO1 = register_game(
    GameDefinition(
        key="ps1.spyro1",
        title="Spyro the Dragon",
        console="ps1",
        region="PAL",
        serial="SCES-01438",
        project_dir=Path("ps1/spyro/1"),
        notes=(
            "Irish replaces the English string slot in SCES_014.38.",
            "Homeworld transition text is patched in the French slot.",
        ),
    )
)
