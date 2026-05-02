"""Translation status command."""

from collections import OrderedDict

import typer
from rich.console import Console
from rich import print
from rich.rule import Rule

from cli.config import REPO_ROOT, read_config
from cli.games.registry import find_game_by_short_name, get_game_by_parts
from cli.strings import normalize_translation_status, read_translation_csv, validate_translation_rows

BAR_WIDTH = 20
console = Console()


def _render_bar(progress: float) -> str:
    filled = round(progress * BAR_WIDTH)
    return ("█" * filled) + ("░" * (BAR_WIDTH - filled))


def _styled(text: str, style: str) -> str:
    return f"[{style}]{text}[/{style}]"


def _status_breakdown(rows: list) -> dict[str, int]:
    counts = {
        "verified": 0,
        "draft": 0,
        "compromised": 0,
        "untranslated": 0,
    }
    for row in rows:
        counts[normalize_translation_status(row.status, row.irish)] += 1
    return counts


def _status_breakdown_text(counts: dict[str, int]) -> str:
    return (
        f"fíoraithe: {counts['verified']} · "
        f"dréacht: {counts['draft']} · "
        f"comhréiteach: {counts['compromised']} · "
        f"gan aistriú: {counts['untranslated']}"
    )


def _load_game(game: str | None):
    if game:
        try:
            return find_game_by_short_name(game)
        except (KeyError, ValueError) as error:
            raise typer.BadParameter(str(error)) from error

    try:
        config = read_config()
    except FileNotFoundError as error:
        raise typer.BadParameter("Missing .gsc/config.toml. Run `gsc init` first or pass --game.") from error

    try:
        return get_game_by_parts(config.console, config.game)
    except KeyError as error:
        raise typer.BadParameter(f"Unsupported game: {config.console}.{config.game}") from error


def register(app: typer.Typer) -> None:
    """Register the status command on the root app."""

    @app.command("status")
    def show_status(
        game: str | None = typer.Option(None, "--game", help="Short game key, e.g. spyro1."),
    ) -> None:
        """Show translation progress grouped by category."""
        game_definition = _load_game(game)
        if game_definition.string_table is None:
            raise typer.BadParameter(f"No string table configured for {game_definition.key}")

        csv_path = REPO_ROOT / game_definition.string_table.csv_path
        if not csv_path.exists():
            raise typer.BadParameter(f"Translations CSV does not exist: {csv_path}")

        rows = read_translation_csv(
            csv_path,
            source_path=game_definition.string_table.source_path,
            category_groups=game_definition.string_table.category_groups,
        )
        try:
            validation = validate_translation_rows(rows)
        except ValueError as error:
            raise typer.BadParameter(str(error)) from error

        over_budget_offsets = {violation.offset for violation in validation.over_budget}
        category_rows: OrderedDict[str, list] = OrderedDict()
        for row in validation.rows:
            category_rows.setdefault(row.category, []).append(row)

        label_width = max([len(category) for category in category_rows] + [len("Overall")]) + 2
        theme = game_definition.theme

        console.print(
            Rule(
                _styled(f"{game_definition.title} ({game_definition.console.upper()}) - Translation Status", theme.header_style),
                style=theme.rule_style,
            )
        )

        for category, category_group in category_rows.items():
            translated = sum(1 for row in category_group if row.irish.strip())
            total = len(category_group)
            progress = translated / total if total else 0.0
            over_budget = sum(1 for row in category_group if row.offset in over_budget_offsets)
            statuses = _status_breakdown(category_group)
            status_text = _status_breakdown_text(statuses)
            status_suffix = f" {_styled(status_text, theme.accent_style)}"
            suffix = f" {_styled(f'! {over_budget} over budget', 'red')}" if over_budget else ""
            print(
                f"{_styled(f'{category:<{label_width}}', theme.accent_style)} "
                f"{_styled(_render_bar(progress), theme.header_style)} "
                f"{_styled(f'{progress * 100:>3.0f}% ({translated}/{total})', theme.success_style)}"
                f"{status_suffix}{suffix}"
            )

        overall_total = len(validation.rows)
        overall_translated = len(validation.translated_rows)
        overall_progress = overall_translated / overall_total if overall_total else 0.0
        overall_label = f"{'Overall':<{label_width}}"
        console.print(Rule(style=theme.rule_style))
        print(
            f"{_styled(overall_label, theme.accent_style)} "
            f"{_styled(_render_bar(overall_progress), theme.header_style)} "
            f"{_styled(f'{overall_progress * 100:>3.0f}% ({overall_translated}/{overall_total})', theme.success_style)}"
        )
        statuses = validation.status_counts
        print(
            _styled(
                f"Status breakdown: {_status_breakdown_text(statuses)}",
                theme.accent_style,
            )
        )

        if validation.over_budget:
            print("")
            print(_styled(f"{len(validation.over_budget)} strings over budget:", "red"))
            for violation in validation.over_budget:
                print(
                    f"  {_styled(violation.offset, theme.accent_style)}: {violation.encoded} "
                    f"{_styled(f'({violation.encoded_length} bytes, budget {violation.budget})', 'red')}"
                )
