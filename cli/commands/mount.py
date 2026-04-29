"""Disc mounting commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

app = Typer(help="Mount or inspect supported disc images.")


@app.command("disc")
def mount_disc(
    image: Path = typer.Argument(..., exists=False, help="Disc image to mount."),
    mountpoint: Path = typer.Argument(..., help="Target mount directory."),
) -> None:
    """Stub mount command."""
    print(f"[bold yellow]Not implemented:[/bold yellow] mount {image} at {mountpoint}")
