"""Release commands."""

from pathlib import Path
import random
import shutil
import subprocess
import threading
import time

import typer
from typer import Typer
from rich.console import Console
from rich import print
from rich.rule import Rule

from cli.config import CONFIG_DIR, REPO_ROOT, read_config
from cli.games.registry import get_game_by_parts
from cli.strings import (
    apply_translations_to_rom,
    build_sync_map,
    copy_rom,
    read_translation_csv,
    validate_translation_rows,
    verify_formula,
)

app = Typer(help="Build release artifacts.", invoke_without_command=True)
console = Console()
DEFAULT_RELEASE_MESSAGES = (
    "Preparing patch data...",
    "Comparing original and patched ROM...",
    "Building distributable BPS patch...",
)
DEFAULT_RELEASE_MESSAGE_INTERVAL_RANGE = (5.0, 8.0)
BPS_MODES = {
    "compact": "--bps",
    "fast": "--bps-linear",
}


def _default_bps_output(project_dir: Path, game_key: str, version: str | None) -> Path:
    short_name = game_key.split(".", 1)[1]
    suffix = f"_v{version}" if version else ""
    return REPO_ROOT / project_dir / "patches" / f"{short_name}_gaeilge{suffix}.bps"


def _require_command(name: str, install_hint: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise typer.BadParameter(f"{name} is not installed. {install_hint}")
    return executable


def _create_github_release(version: str, output_path: Path) -> None:
    gh = _require_command("gh", "Install GitHub CLI or omit --github-release.")
    tag = f"v{version}"
    title = f"Release {tag}"
    try:
        subprocess.run(
            [gh, "release", "create", tag, str(output_path), "--title", title, "--generate-notes"],
            check=True,
        )
    except subprocess.CalledProcessError as error:
        raise typer.BadParameter(f"Failed to create GitHub release {tag}") from error


def _release_messages(game) -> tuple[str, ...]:
    messages = game.release_messages or DEFAULT_RELEASE_MESSAGES
    return messages


def _release_message_interval_range(game) -> tuple[float, float]:
    low, high = game.release_message_interval_range
    if low <= 0 or high < low:
        return DEFAULT_RELEASE_MESSAGE_INTERVAL_RANGE
    return low, high


def _styled(text: str, style: str) -> str:
    return f"[{style}]{text}[/{style}]"


@app.callback()
def build_release(
    ctx: typer.Context,
    version: str | None = typer.Option(None, "--version", help="Release version, e.g. 1.0."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output BPS patch path."),
    mode: str | None = typer.Option(None, "--mode", help="BPS creation mode: fast or compact."),
    github_release: bool = typer.Option(False, "--github-release", help="Create a GitHub release with the patch."),
) -> None:
    """Generate a distributable BPS patch file."""
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

    csv_path = REPO_ROOT / game.string_table.csv_path
    if not csv_path.exists():
        raise typer.BadParameter(f"Translations CSV does not exist: {csv_path}")

    if github_release and not version:
        raise typer.BadParameter("--github-release requires --version")
    if mode is None:
        raise typer.BadParameter("--mode is required. Choose one of: fast, compact")
    if mode not in BPS_MODES:
        raise typer.BadParameter("--mode must be one of: fast, compact")

    try:
        flips = _require_command("flips", "Install Flips to generate BPS patches.")
        rows = read_translation_csv(csv_path)
        validation = validate_translation_rows(rows)
        verify_formula(game.string_table, build_sync_map(config.rom.read_bytes()))
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    if validation.over_budget:
        print(f"[red]\u2717[/red] {len(validation.over_budget)} strings exceed budget:")
        for violation in validation.over_budget:
            print(
                f"   {violation.offset}: {violation.encoded} "
                f"({violation.encoded_length} bytes, budget {violation.budget})"
            )
        raise typer.Exit(code=1)

    theme = game.theme
    console.print(Rule(_styled(f"{game.title} Release Build", theme.header_style), style=theme.rule_style))
    print(_styled("\u2713 Validation passed", theme.success_style))
    print(_styled("\u2713 Sector formula verified", theme.success_style))

    output_path = (
        output.expanduser().resolve()
        if output
        else _default_bps_output(game.project_dir, game.key, version)
    )
    temp_dir = CONFIG_DIR / "release"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_bin = temp_dir / f"{game.key.split('.', 1)[1]}_patched.bin"

    copy_rom(config.rom, temp_bin)
    applied, skipped = apply_translations_to_rom(temp_bin, game.string_table, rows)
    if skipped:
        raise typer.BadParameter("Release aborted because some strings were skipped unexpectedly.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        start = time.monotonic()
        messages = _release_messages(game)
        interval_low, interval_high = _release_message_interval_range(game)
        process = subprocess.Popen(
            [flips, "--create", BPS_MODES[mode], str(config.rom), str(temp_bin), str(output_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stop_event = threading.Event()

        def update_status() -> None:
            index = 0
            next_rotation = random.uniform(interval_low, interval_high)
            while not stop_event.wait(0.5):
                elapsed = time.monotonic() - start
                if elapsed >= next_rotation:
                    index += 1
                    next_rotation = elapsed + random.uniform(interval_low, interval_high)
                message = messages[index % len(messages)]
                status.update(
                    f"{_styled(message, theme.accent_style)} {_styled(f'{elapsed:.1f}s elapsed', theme.success_style)}"
                )

        with console.status(
            f"{_styled(messages[0], theme.accent_style)} {_styled('0.0s elapsed', theme.success_style)}",
            spinner="dots",
            spinner_style=theme.spinner_style,
        ) as status:
            status_thread = threading.Thread(target=update_status, daemon=True)
            status_thread.start()
            stdout, stderr = process.communicate()
            stop_event.set()
            status_thread.join(timeout=1)
        elapsed = time.monotonic() - start
        result = subprocess.CompletedProcess(
            process.args,
            process.returncode,
            stdout=stdout,
            stderr=stderr,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            message = f"Failed to generate BPS patch: {output_path}"
            if detail:
                message = f"{message}\n{detail}"
            raise typer.BadParameter(message)
    finally:
        if temp_bin.exists():
            temp_bin.unlink()

    patch_size = output_path.stat().st_size
    print(_styled(f"Patched {applied} strings", theme.success_style))
    print(_styled(f"BPS mode {mode}", theme.success_style))
    print(_styled(f"BPS generation time {elapsed:.1f}s", theme.success_style))
    print(_styled(f"Created {output_path} ({patch_size} bytes)", theme.header_style))

    if github_release:
        _create_github_release(version, output_path)
        print(_styled(f"Published GitHub release v{version}", theme.success_style))
