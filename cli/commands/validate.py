"""Validation commands."""

from pathlib import Path

import typer
from typer import Typer
from rich import print

from cli.config import REPO_ROOT, read_config
from cli.games.registry import get_game_by_parts
from cli.strings import read_translation_csv
from cli.text import encode_rom_text

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

    rows = read_translation_csv(resolved_csv)
    total = len(rows)
    translated_rows = [row for row in rows if row.irish.strip()]
    untranslated = total - len(translated_rows)

    over_budget: list[tuple[str, str, int, int]] = []
    for row in translated_rows:
        encoded = encode_rom_text(row.irish.strip())
        try:
            encoded_bytes = encoded.encode("ascii")
        except UnicodeEncodeError as error:
            raise typer.BadParameter(f"{row.offset}: translation contains unsupported characters") from error
        encoded_length = len(encoded_bytes)
        if encoded_length > row.budget:
            over_budget.append((row.offset, encoded, encoded_length, row.budget))

    progress = (len(translated_rows) / total * 100) if total else 0.0

    print(f"[green]\u2713[/green] {len(translated_rows)} strings translated")
    if over_budget:
        print(f"[red]\u2717[/red] {len(over_budget)} strings exceed budget:")
        for offset, encoded, encoded_length, budget in over_budget:
            print(f"   {offset}: {encoded} ({encoded_length} bytes, budget {budget})")
    else:
        print("[green]\u2713[/green] No strings exceed budget")
    print(f"[yellow]\u25cb[/yellow] {untranslated} strings untranslated")
    print(f"Progress: {progress:.1f}% ({len(translated_rows)}/{total})")

    if over_budget:
        raise typer.Exit(code=1)
