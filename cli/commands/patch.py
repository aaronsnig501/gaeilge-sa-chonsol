"""Patch commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

app = Typer(help="Apply or build binary patches.")


@app.command("build")
def build_patch(
    game: str = typer.Argument(..., help="Game registry key, e.g. ps1.spyro1."),
    source: Path = typer.Argument(..., exists=False, help="Original game image."),
    output: Path = typer.Argument(..., help="Patched output image."),
) -> None:
    """Stub patch build command."""
    print(f"[bold yellow]Not implemented:[/bold yellow] patch {game} from {source} to {output}")
