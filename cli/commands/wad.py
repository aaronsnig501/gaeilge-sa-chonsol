"""WAD handling commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

from cli.config import REPO_ROOT, read_config, read_mount_state
from cli.games.registry import get_game_by_parts
from cli.wad import extract_wad, pack_wad, read_wad_entries

app = Typer(help="Inspect and unpack WAD archives.")


def _load_game():
    try:
        config = read_config()
    except FileNotFoundError as error:
        raise typer.BadParameter("Missing .gsc/config.toml. Run `gsc init` first.") from error

    try:
        return get_game_by_parts(config.console, config.game)
    except KeyError as error:
        raise typer.BadParameter(f"Unsupported game: {config.console}.{config.game}") from error


def _mounted_wad_path(archive_path: Path) -> Path:
    try:
        state = read_mount_state()
    except FileNotFoundError as error:
        raise typer.BadParameter("No active mount state found. Run `gsc mount` first.") from error
    return state.mountpoint / archive_path


@app.command("list")
def list_wad() -> None:
    """List WAD subfiles with sizes and known descriptions."""
    game = _load_game()
    if game.wad is None:
        raise typer.BadParameter(f"No WAD metadata configured for {game.key}")

    archive = _mounted_wad_path(game.wad.archive_path)
    if not archive.exists():
        raise typer.BadParameter(f"WAD archive does not exist: {archive}")

    entries = read_wad_entries(archive)
    for entry in entries:
        description = game.wad.known_subfiles.get(entry.index, "")
        suffix = f" - {description}" if description else ""
        print(f"sf_{entry.index}: {entry.size} bytes{suffix}")


@app.command("extract")
def extract(
    output_dir: Path = typer.Option(REPO_ROOT / "wad_subfiles", "--output", "-o", help="Directory to extract into."),
    subfile: int | None = typer.Option(None, "--subfile", help="Extract a specific subfile number."),
) -> None:
    """Extract WAD subfiles from the mounted disc."""
    game = _load_game()
    if game.wad is None:
        raise typer.BadParameter(f"No WAD metadata configured for {game.key}")

    archive = _mounted_wad_path(game.wad.archive_path)
    if not archive.exists():
        raise typer.BadParameter(f"WAD archive does not exist: {archive}")

    try:
        resolved_output = output_dir.expanduser().resolve()
        extracted = extract_wad(archive, resolved_output, subfile=subfile)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    if subfile is not None:
        print(f"[green]Extracted[/green] sf_{subfile}.bin to [bold]{resolved_output}[/bold]")
    else:
        print(f"[green]Extracted[/green] {len(extracted)} subfiles to [bold]{resolved_output}[/bold]")


@app.command("pack")
def pack(
    input_dir: Path = typer.Argument(..., exists=True, file_okay=False, help="Directory with sf_*.bin files."),
    output: Path = typer.Option(Path("new_WAD.WAD"), "--output", "-o", help="Output WAD file path."),
) -> None:
    """Pack a directory of subfiles into a new WAD archive."""
    try:
        entries = pack_wad(input_dir.expanduser().resolve(), output.expanduser().resolve())
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    print(f"[green]Packed[/green] {len(entries)} subfiles into [bold]{output.expanduser().resolve()}[/bold]")
