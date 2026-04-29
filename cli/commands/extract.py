"""Extraction commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

app = Typer(help="Extract files and assets from supported games.")


@app.command("game")
def extract_game(
    game: str = typer.Argument(..., help="Game registry key, e.g. ps1.spyro1."),
    source: Path = typer.Argument(..., exists=False, help="Path to the source disc image."),
) -> None:
    """Stub extraction command."""
    print(f"[bold yellow]Not implemented:[/bold yellow] extract {game} from {source}")
