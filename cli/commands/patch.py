"""Patch commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

from cli.config import REPO_ROOT, read_config
from cli.games.registry import get_game_by_parts
from cli.strings import (
    apply_translations_to_rom,
    build_sync_map,
    copy_rom,
    read_translation_csv,
    validate_translation_rows,
    verify_formula,
)

app = Typer(help="Apply or build binary patches.", invoke_without_command=True)


@app.callback()
def build_patch(
    ctx: typer.Context,
    output: Path = typer.Option(Path("spyro_gaeilge.bin"), "--output", "-o", help="Patched BIN output path."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be patched without writing."),
) -> None:
    """Apply valid translations from CSV to a copied ROM image."""
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

    rows = read_translation_csv(csv_path)
    try:
        validation = validate_translation_rows(rows)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    try:
        verify_formula(game.string_table, build_sync_map(config.rom.read_bytes()))
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    translated = len(validation.translated_rows)
    applied = translated - len(validation.over_budget)
    output_path = output.expanduser().resolve()

    print("[green]Sector formula verified[/green]")
    if dry_run:
        print(f"Would patch [bold]{applied}[/bold] strings into [bold]{output_path}[/bold]")
    else:
        copy_rom(config.rom, output_path)
        applied, skipped = apply_translations_to_rom(output_path, game.string_table, rows)
        print(f"[green]Patched[/green] {applied} strings into [bold]{output_path}[/bold]")
        validation = validation.__class__(
            rows=validation.rows,
            translated_rows=validation.translated_rows,
            untranslated_count=validation.untranslated_count,
            over_budget=skipped,
        )

    if validation.over_budget:
        print(f"[yellow]Skipped[/yellow] {len(validation.over_budget)} strings that exceed budget:")
        for violation in validation.over_budget:
            print(
                f"   {violation.offset}: {violation.encoded} "
                f"({violation.encoded_length} bytes, budget {violation.budget})"
            )
    else:
        print("[green]Skipped[/green] 0 strings")
