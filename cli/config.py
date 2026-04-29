"""Local project configuration helpers."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / ".gsc"
CONFIG_PATH = CONFIG_DIR / "config.toml"


def render_config(console: str, game: str, rom: Path) -> str:
    """Render the local project config in TOML format."""
    return (
        "[game]\n"
        f'console = "{console}"\n'
        f'game = "{game}"\n'
        f'rom = "{rom}"\n'
    )


def write_config(console: str, game: str, rom: Path) -> Path:
    """Persist the local project config to the repo root."""
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_PATH.write_text(render_config(console, game, rom), encoding="utf-8")
    return CONFIG_PATH
