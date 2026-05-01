"""Validate changed translation CSVs and emit a PR comment summary."""

from __future__ import annotations

import csv
import io
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cli.games import ps1  # noqa: F401
from cli.games.registry import GAME_REGISTRY, GameDefinition
from cli.strings import BudgetViolation, read_translation_csv, validate_translation_rows


COMMENT_MARKER = "<!-- gsc-translation-validation -->"


@dataclass(frozen=True, slots=True)
class ValidationReport:
    game: GameDefinition
    translated: int
    translated_delta: int
    untranslated: int
    total: int
    over_budget: list[BudgetViolation]


def run_git(*args: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def changed_translation_files(base_sha: str, head_sha: str) -> list[Path]:
    """List changed translation CSVs between base and head."""
    output = run_git("diff", "--name-only", base_sha, head_sha)
    return [
        Path(line.strip())
        for line in output.splitlines()
        if line.strip() and line.strip().endswith((".csv",))
    ]


def game_for_csv(csv_path: Path) -> GameDefinition | None:
    """Find the registered game that owns a CSV path."""
    normalized = csv_path.as_posix()
    for game in GAME_REGISTRY.values():
        if game.string_table and game.string_table.csv_path.as_posix() == normalized:
            return game
    return None


def parse_rows_from_content(content: str) -> list[dict[str, str]]:
    """Parse CSV rows from git-show content."""
    if not content.strip():
        return []
    handle = io.StringIO(content)
    return list(csv.DictReader(handle))


def translated_count_from_rows(rows: list[dict[str, str]]) -> int:
    """Count translated rows from raw CSV dictionaries."""
    return sum(1 for row in rows if row.get("irish", "").strip())


def base_translated_count(base_sha: str, csv_path: Path) -> int:
    """Load translated count for the base revision of a CSV."""
    try:
        content = run_git("show", f"{base_sha}:{csv_path.as_posix()}")
    except subprocess.CalledProcessError:
        return 0
    return translated_count_from_rows(parse_rows_from_content(content))


def validate_game_csv(game: GameDefinition, base_sha: str) -> ValidationReport:
    """Validate one game's translation CSV."""
    assert game.string_table is not None
    csv_path = REPO_ROOT / game.string_table.csv_path
    rows = read_translation_csv(csv_path)
    validation = validate_translation_rows(rows)
    translated = len(validation.translated_rows)
    total = len(validation.rows)
    base_translated = base_translated_count(base_sha, game.string_table.csv_path)
    return ValidationReport(
        game=game,
        translated=translated,
        translated_delta=translated - base_translated,
        untranslated=validation.untranslated_count,
        total=total,
        over_budget=validation.over_budget,
    )


def heading_for_game(game: GameDefinition) -> str:
    """Build a readable game heading for the PR comment."""
    short_name = game.key.split(".", 1)[1]
    if short_name.startswith("spyro") and short_name[-1].isdigit():
        return f"Spyro {short_name[-1]}"
    return game.title


def render_report(report: ValidationReport) -> str:
    """Render one game's markdown report block."""
    progress = (report.translated / report.total * 100) if report.total else 0.0
    delta = f" ({report.translated_delta:+d} from this PR)"
    lines = [f"## Translation Validation - {heading_for_game(report.game)}", ""]
    lines.append(f"✓ {report.translated} strings translated{delta}")
    if report.over_budget:
        lines.append(f"✗ {len(report.over_budget)} strings exceed budget")
        for violation in report.over_budget:
            lines.append(
                f"- `{violation.offset}`: `{violation.encoded}` ({violation.encoded_length} bytes, budget {violation.budget})"
            )
    else:
        lines.append("✓ All strings within budget")
    lines.append(f"○ {report.untranslated} strings untranslated")
    lines.append("")
    lines.append(f"Progress: {progress:.0f}% ({report.translated}/{report.total})")
    return "\n".join(lines)


def build_comment(reports: list[ValidationReport]) -> str:
    """Build the full PR comment body."""
    blocks = [COMMENT_MARKER, ""]
    for index, report in enumerate(reports):
        if index:
            blocks.extend(["", "---", ""])
        blocks.append(render_report(report))
    return "\n".join(blocks) + "\n"


def main() -> int:
    """Validate changed translation CSVs for a PR."""
    if len(sys.argv) != 4:
        print("usage: validate_translations_pr.py <base-sha> <head-sha> <comment-output>", file=sys.stderr)
        return 2

    base_sha = sys.argv[1]
    head_sha = sys.argv[2]
    comment_output = Path(sys.argv[3]).expanduser().resolve()

    changed_files = changed_translation_files(base_sha, head_sha)
    games: list[GameDefinition] = []
    for csv_path in changed_files:
        game = game_for_csv(csv_path)
        if game and game not in games:
            games.append(game)

    if not games:
        comment_output.parent.mkdir(parents=True, exist_ok=True)
        comment_output.write_text(f"{COMMENT_MARKER}\n\nNo registered translation CSV changes detected.\n", encoding="utf-8")
        return 0

    reports = [validate_game_csv(game, base_sha) for game in games]
    comment_output.parent.mkdir(parents=True, exist_ok=True)
    comment_output.write_text(build_comment(reports), encoding="utf-8")
    return 1 if any(report.over_budget for report in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
