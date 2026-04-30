"""Validation commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

from cli.config import REPO_ROOT, read_config
from cli.games.registry import get_game_by_parts
from cli.strings import read_translation_csv, validate_translation_rows

app = Typer(help="Validate ROMs, patches, and project data.", invoke_without_command=True)


@app.callback()
def validate_translations(
    ctx: typer.Context,
    csv_path: Path | None = typer.Option(None, "--csv", help="Custom translations CSV path."),
) -> None:
    """Validate that translations fit within their byte budgets."""
    if ctx.invoked_subcommand is not None:
        return

    try:
        config = read_config()
    except FileNotFoundError as error:
        raise typer.BadParameter("Missing .gsc/config.toml. Run `gsc init` first.") from error

    try:
        game = get_game_by_parts(config.console, config.game)
    except KeyError as error:
        raise typer.BadParameter(f"Unsupported game: {config.console}.{config.game}") from error

    if game.string_table is None:
        raise typer.BadParameter(f"No string table configured for {game.key}")

    resolved_csv = csv_path.expanduser().resolve() if csv_path else REPO_ROOT / game.string_table.csv_path
    if not resolved_csv.exists():
        raise typer.BadParameter(f"Translations CSV does not exist: {resolved_csv}")

    try:
        validation = validate_translation_rows(read_translation_csv(resolved_csv))
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error

    total = len(validation.rows)
    progress = (len(validation.translated_rows) / total * 100) if total else 0.0

    print(f"[green]\u2713[/green] {len(validation.translated_rows)} strings translated")
    if validation.over_budget:
        print(f"[red]\u2717[/red] {len(validation.over_budget)} strings exceed budget:")
        for violation in validation.over_budget:
            print(
                f"   {violation.offset}: {violation.encoded} "
                f"({violation.encoded_length} bytes, budget {violation.budget})"
            )
    else:
        print("[green]\u2713[/green] No strings exceed budget")
    print(f"[yellow]\u25cb[/yellow] {validation.untranslated_count} strings untranslated")
    print(f"Progress: {progress:.1f}% ({len(validation.translated_rows)}/{total})")

    if validation.over_budget:
        raise typer.Exit(code=1)
