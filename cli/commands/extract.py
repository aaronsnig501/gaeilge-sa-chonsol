"""Extraction commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

from cli.config import REPO_ROOT, read_config
from cli.games.registry import get_game_by_parts
from cli.strings import extract_strings, write_translation_csv

app = Typer(help="Extract files and assets from supported games.", invoke_without_command=True)


@app.callback()
def extract_strings_command(
    ctx: typer.Context,
    output: Path | None = typer.Option(None, "--output", "-o", help="Custom CSV output path."),
) -> None:
    """Extract all translatable strings for the configured game."""
    if ctx.invoked_subcommand is not None:
        return

    try:
        config = read_config()
    except FileNotFoundError as error:
        raise typer.BadParameter("Missing .gsc/config.toml. Run `gsc init` first.") from error

    if not config.rom.exists():
        raise typer.BadParameter(f"Configured ROM does not exist: {config.rom}")

    try:
        game = get_game_by_parts(config.console, config.game)
    except KeyError as error:
        raise typer.BadParameter(f"Unsupported game: {config.console}.{config.game}") from error

    if game.string_table is None:
        raise typer.BadParameter(f"No string table configured for {game.key}")

    output_path = output.expanduser().resolve() if output else REPO_ROOT / game.string_table.csv_path
    rows = extract_strings(config.rom, game.string_table)
    write_translation_csv(rows, output_path)

    print(f"[green]Extracted {len(rows)} strings[/green] from {game.title}")
    print(f"Output: [bold]{output_path}[/bold]")
