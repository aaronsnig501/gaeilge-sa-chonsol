"""Sync game notes markdown from project docs into SvelteKit routes."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cli.games import ps1  # noqa: F401
from cli.games.registry import GAME_REGISTRY


WEB_ROUTES_ROOT = REPO_ROOT / "web" / "src" / "routes" / "games"


def source_notes_path(project_dir: Path) -> Path:
    """Return the canonical notes markdown file for a game."""
    return REPO_ROOT / project_dir / "notes" / "notes.md"


def destination_notes_path(console: str, game: str) -> Path:
    """Return the rendered route path for a game's notes page."""
    return WEB_ROUTES_ROOT / console / game / "notes" / "+page.md"


def build_frontmatter(title: str) -> str:
    """Build minimal mdsvex frontmatter."""
    return f"---\ntitle: {title} Notes\n---\n\n"


def sync_notes() -> list[Path]:
    """Copy all available game notes into web routes."""
    written: list[Path] = []

    for key in sorted(GAME_REGISTRY):
        game = GAME_REGISTRY[key]
        short_name = key.split(".", 1)[1]
        source = source_notes_path(game.project_dir)
        if not source.exists():
            continue

        destination = destination_notes_path(game.console, short_name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = build_frontmatter(game.title) + source.read_text(encoding="utf-8").strip() + "\n"
        destination.write_text(content, encoding="utf-8")
        written.append(destination)

    return written


def main() -> None:
    """CLI entry point."""
    for path in sync_notes():
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
