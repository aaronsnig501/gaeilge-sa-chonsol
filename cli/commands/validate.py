"""Validation commands."""

from pathlib import Path

import typer
from typer import Typer
from rich.console import Console
from rich import print
from rich.rule import Rule

from cli.config import REPO_ROOT, read_config
from cli.games.registry import get_game_by_parts
from cli.strings import read_translation_csv, validate_translation_rows

app = Typer(help="Validate ROMs, patches, and project data.", invoke_without_command=True)
console = Console()


def _styled(text: str, style: str) -> str:
    return f"[{style}]{text}[/{style}]"


def _status_summary(validation) -> list[str]:
    counts = validation.status_counts
    return [
        f"✓ {counts['verified']} fíoraithe",
        f"↺ {counts['draft']} dréacht",
        f"⚠ {counts['compromised']} comhréiteach",
        f"○ {counts['untranslated']} gan aistriú",
    ]


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
    theme = game.theme

    console.print(
        Rule(
            _styled(f"{game.title} Validation", theme.header_style),
            style=theme.rule_style,
        )
    )
    print(_styled(f"\u2713 {len(validation.translated_rows)} strings translated", theme.success_style))
    if validation.over_budget:
        print(_styled(f"\u2717 {len(validation.over_budget)} strings exceed budget:", "red"))
        for violation in validation.over_budget:
            print(
                f"   {_styled(violation.offset, theme.accent_style)}: {violation.encoded} "
                f"{_styled(f'({violation.encoded_length} bytes, budget {violation.budget})', 'red')}"
            )
    else:
        print(_styled("\u2713 No strings exceed budget", theme.success_style))
    for summary in _status_summary(validation):
        print(_styled(summary, theme.accent_style))
    print(_styled(f"Progress: {progress:.1f}% ({len(validation.translated_rows)}/{total})", theme.header_style))

    if validation.over_budget:
        raise typer.Exit(code=1)
