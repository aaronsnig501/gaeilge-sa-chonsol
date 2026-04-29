"""Release commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

app = Typer(help="Build release artifacts.")


@app.command("build")
def build_release(
    game: str = typer.Argument(..., help="Game registry key, e.g. ps1.spyro1."),
    output_dir: Path = typer.Argument(..., help="Directory for release artifacts."),
) -> None:
    """Stub release command."""
    print(f"[bold yellow]Not implemented:[/bold yellow] build release for {game} in {output_dir}")
