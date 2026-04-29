"""Project initialization command."""

from pathlib import Path

import typer
from rich import print

from cli.config import write_config
from cli.games.registry import GameDefinition, get_game_by_parts

ROM_SNIFF_BYTES = 1024 * 1024


def _read_rom_window(rom: Path) -> bytes:
    with rom.open("rb") as handle:
        return handle.read(ROM_SNIFF_BYTES)


def _validate_rom(game: GameDefinition, rom: Path) -> None:
    rom_bytes = _read_rom_window(rom)
    if game.rom_markers and not any(marker in rom_bytes for marker in game.rom_markers):
        marker_list = ", ".join(marker.decode("ascii", errors="ignore") for marker in game.rom_markers)
        raise typer.BadParameter(
            f"ROM does not match {game.title} ({game.serial}); expected one of: {marker_list}"
        )


def register(app: typer.Typer) -> None:
    """Register the init command on the root app."""

    @app.command("init")
    def init_project(
        console: str = typer.Option(..., help="Console key, e.g. ps1."),
        game: str = typer.Option(..., help="Game key, e.g. spyro1."),
        rom: Path = typer.Option(..., exists=True, dir_okay=False, readable=True, help="Path to the source ROM."),
        yes: bool = typer.Option(False, "--yes", help="Skip the confirmation prompt."),
    ) -> None:
        """Register a ROM with the local project."""
        try:
            game_definition = get_game_by_parts(console, game)
        except KeyError as error:
            raise typer.BadParameter(f"Unsupported game: {console}.{game}") from error
        rom_path = rom.expanduser().resolve()
        _validate_rom(game_definition, rom_path)

        print(f"[green]Validated ROM[/green]: {game_definition.title} ({game_definition.serial})")
        print(f"Config target: [bold].gsc/config.toml[/bold]")
        print(f"ROM path: [bold]{rom_path}[/bold]")

        if not yes and not typer.confirm("Write local config?", default=True):
            raise typer.Exit(code=1)

        config_path = write_config(console, game, rom_path)
        print(f"[green]Wrote config[/green]: {config_path}")
