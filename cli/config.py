"""Local project configuration helpers."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / ".gsc"
CONFIG_PATH = CONFIG_DIR / "config.toml"
MOUNT_STATE_PATH = CONFIG_DIR / "mount.toml"


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Local CLI configuration."""

    console: str
    game: str
    rom: Path
    mountpoint: Path


@dataclass(frozen=True, slots=True)
class MountState:
    """Persisted mount state for gsc mount/umount."""

    game: str
    iso: Path
    mountpoint: Path


def default_mountpoint(game: str) -> Path:
    """Build the default mount point for a game."""
    return Path("/mnt") / game


def render_config(console: str, game: str, rom: Path, mountpoint: Path | None = None) -> str:
    """Render the local project config in TOML format."""
    resolved_mountpoint = mountpoint or default_mountpoint(game)
    return (
        "[game]\n"
        f'console = "{console}"\n'
        f'game = "{game}"\n'
        f'rom = "{rom}"\n'
        "\n[mount]\n"
        f'mountpoint = "{resolved_mountpoint}"\n'
    )


def write_config(console: str, game: str, rom: Path, mountpoint: Path | None = None) -> Path:
    """Persist the local project config to the repo root."""
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_PATH.write_text(render_config(console, game, rom, mountpoint), encoding="utf-8")
    return CONFIG_PATH


def read_config() -> ProjectConfig:
    """Load the local project config from the repo root."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")

    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    game = data["game"]
    mount = data.get("mount", {})
    return ProjectConfig(
        console=game["console"],
        game=game["game"],
        rom=Path(game["rom"]).expanduser().resolve(),
        mountpoint=Path(mount.get("mountpoint", default_mountpoint(game["game"]))).expanduser().resolve(),
    )


def write_mount_state(game: str, iso: Path, mountpoint: Path) -> Path:
    """Persist the current mount state."""
    CONFIG_DIR.mkdir(exist_ok=True)
    MOUNT_STATE_PATH.write_text(
        (
            "[mount]\n"
            f'game = "{game}"\n'
            f'iso = "{iso}"\n'
            f'mountpoint = "{mountpoint}"\n'
        ),
        encoding="utf-8",
    )
    return MOUNT_STATE_PATH


def read_mount_state() -> MountState:
    """Read persisted mount state."""
    if not MOUNT_STATE_PATH.exists():
        raise FileNotFoundError(f"Missing mount state: {MOUNT_STATE_PATH}")

    data = tomllib.loads(MOUNT_STATE_PATH.read_text(encoding="utf-8"))["mount"]
    return MountState(
        game=data["game"],
        iso=Path(data["iso"]).expanduser().resolve(),
        mountpoint=Path(data["mountpoint"]).expanduser().resolve(),
    )


def clear_mount_state() -> None:
    """Remove persisted mount state."""
    if MOUNT_STATE_PATH.exists():
        MOUNT_STATE_PATH.unlink()
