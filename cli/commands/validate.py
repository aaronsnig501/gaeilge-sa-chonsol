"""Validation commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

app = Typer(help="Validate ROMs, patches, and project data.")


@app.command("image")
def validate_image(
    game: str = typer.Argument(..., help="Game registry key, e.g. ps1.spyro1."),
    image: Path = typer.Argument(..., exists=False, help="Disc image to validate."),
) -> None:
    """Stub image validation command."""
    print(f"[bold yellow]Not implemented:[/bold yellow] validate {image} for {game}")
