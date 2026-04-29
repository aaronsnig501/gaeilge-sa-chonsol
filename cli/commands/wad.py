"""WAD handling commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

app = Typer(help="Inspect and unpack WAD archives.")


@app.command("unpack")
def unpack_wad(
    archive: Path = typer.Argument(..., exists=False, help="WAD archive path."),
    output_dir: Path = typer.Argument(..., help="Directory to unpack into."),
) -> None:
    """Stub WAD unpack command."""
    print(f"[bold yellow]Not implemented:[/bold yellow] unpack {archive} into {output_dir}")
