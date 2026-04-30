"""Spyro the Dragon configuration and offsets."""

from pathlib import Path

from cli.games.registry import GameDefinition, StringTableDefinition, register_game

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
        rom_markers=(
            b"SCES_014.38",
            b"SPYRO",
        ),
        string_table=StringTableDefinition(
            source_path=Path("ps1/spyro/1/data/strings.py"),
            csv_path=Path("ps1/spyro/1/data/strings.csv"),
            executable_iso_offset=0xC000,
            category_groups={
                "Game state": "UI Strings",
                "Intro / navigation": "UI Strings",
                "HUD / treasure": "UI Strings",
                "Pause menu": "UI Strings",
                "Save/load": "UI Strings",
                "Navigation": "UI Strings",
                "Flight level HUD (0x6c*** region - 8-byte slots)": "UI Strings",
                "Pause/options menu (0x6c*** region)": "UI Strings",
                "Flight level continue prompt": "UI Strings",
                "Homeworld transition screens (French slots repurposed)": "Homeworlds",
                "Homeworld short labels (minimap/inventory)": "Homeworlds",
                "Dragon names section": "Homeworlds",
                "Balloonist": "Balloonist",
                "Balloonist dialogue - first visit": "Balloonist",
                "Balloonist dialogue - second visit": "Balloonist",
                "Balloonist dialogue - prove your worth": "Balloonist",
                "Level names - Gnasty's World": "Level Names",
                "Level names - Peace Keepers": "Level Names",
                "Level names - Beast Makers": "Level Names",
                "Level names - Magic Crafters": "Level Names",
                "Level names - Gnasty's World continued": "Level Names",
                "Level names - Artisans": "Level Names",
            },
            preserve_metadata={
                0x6C17C: 5,
                0x6C1A4: 6,
                0x6C1CC: 7,
                0x6C264: 6,
                0x6C2A4: 4,
                0x6C2EC: 6,
                0x6C30C: 7,
                0x6C38C: 5,
                0x6C3E4: 5,
                0x6C3F4: 7,
                0x6BFA0: 4,
                0x6BFA8: 7,
                0x6BFC0: 5,
                0x6BFF4: 7,
                0x6C01C: 5,
                0x6C05C: 6,
                0x6C064: 5,
                0x6C0CC: 6,
                0x6C0D4: 6,
                0x6C0DC: 6,
                0x6C0E4: 7,
                0x6BFE0: 3,
                0x6BFF0: 2,
                0x6C6A8: 4,
            },
            formula_checks=(
                (0x10B0, 0xEFA8),
                (0x2430, 0x10588),
            ),
        ),
    )
)
