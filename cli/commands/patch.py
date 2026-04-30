"""Patch commands."""

from pathlib import Path

import typer
from typer import Typer
from rich.console import Console
from rich import print
from rich.rule import Rule

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
console = Console()


def _styled(text: str, style: str) -> str:
    return f"[{style}]{text}[/{style}]"


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
    theme = game.theme

    console.print(
        Rule(
            _styled(f"{game.title} Patch Build", theme.header_style),
            style=theme.rule_style,
        )
    )
    print(_styled("✓ Sector formula verified", theme.success_style))
    if dry_run:
        print(_styled(f"Would patch {applied} strings into {output_path}", theme.header_style))
    else:
        copy_rom(config.rom, output_path)
        applied, skipped = apply_translations_to_rom(output_path, game.string_table, rows)
        print(_styled(f"Patched {applied} strings into {output_path}", theme.success_style))
        validation = validation.__class__(
            rows=validation.rows,
            translated_rows=validation.translated_rows,
            untranslated_count=validation.untranslated_count,
            over_budget=skipped,
        )

    if validation.over_budget:
        print(_styled(f"Skipped {len(validation.over_budget)} strings that exceed budget:", "yellow"))
        for violation in validation.over_budget:
            print(
                f"   {_styled(violation.offset, theme.accent_style)}: {violation.encoded} "
                f"{_styled(f'({violation.encoded_length} bytes, budget {violation.budget})', 'yellow')}"
            )
    else:
        print(_styled("Skipped 0 strings", theme.success_style))
