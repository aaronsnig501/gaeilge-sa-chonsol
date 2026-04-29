"""Local project configuration helpers."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / ".gsc"
CONFIG_PATH = CONFIG_DIR / "config.toml"


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Local CLI configuration."""

    console: str
    game: str
    rom: Path


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


def read_config() -> ProjectConfig:
    """Load the local project config from the repo root."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")

    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    game = data["game"]
    return ProjectConfig(
        console=game["console"],
        game=game["game"],
        rom=Path(game["rom"]).expanduser().resolve(),
    )
