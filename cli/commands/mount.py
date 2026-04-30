"""Disc mount commands."""

from pathlib import Path
import shutil
import subprocess

import typer
from rich import print

from cli.config import CONFIG_DIR, clear_mount_state, read_config, read_mount_state, write_mount_state
from cli.consoles.ps1 import strip_ps1_bin_to_iso
from cli.games.registry import get_game_by_parts


def _run_command(command: list[str], *, error_prefix: str) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise typer.BadParameter(f"{error_prefix}: {' '.join(command)}") from error


def register(app: typer.Typer) -> None:
    """Register mount and umount commands on the root app."""

    @app.command("mount")
    def mount_disc() -> None:
        """Strip a PS1 BIN to ISO and mount it for exploration."""
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

        mountpoint = config.mountpoint
        iso_path = CONFIG_DIR / "mount" / f"{config.game}_stripped.iso"

        print(f"Stripping sectors from [bold]{config.rom}[/bold]...")
        strip_ps1_bin_to_iso(config.rom, iso_path)

        try:
            _run_command(["sudo", "mkdir", "-p", str(mountpoint)], error_prefix="Failed to create mount point")
            _run_command(
                ["sudo", "mount", "-t", "iso9660", "-o", "loop,ro", str(iso_path), str(mountpoint)],
                error_prefix="Failed to mount ISO",
            )
        except typer.BadParameter:
            if iso_path.exists():
                iso_path.unlink()
            subprocess.run(["sudo", "rmdir", str(mountpoint)], check=False)
            raise

        write_mount_state(game.key, iso_path, mountpoint)
        print(f"[green]Mounted[/green] at [bold]{mountpoint}[/bold]")

    @app.command("umount")
    def umount_disc() -> None:
        """Unmount the current mounted ISO and clean up generated files."""
        try:
            state = read_mount_state()
        except FileNotFoundError as error:
            raise typer.BadParameter("No active mount state found.") from error

        _run_command(["sudo", "umount", str(state.mountpoint)], error_prefix="Failed to unmount")

        if state.iso.exists():
            state.iso.unlink()

        try:
            subprocess.run(["sudo", "rmdir", str(state.mountpoint)], check=False)
        finally:
            clear_mount_state()

        print(f"[green]Unmounted[/green] [bold]{state.mountpoint}[/bold]")
