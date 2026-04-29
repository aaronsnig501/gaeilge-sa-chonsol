"""Typer entry point for the Gaeilge sa Chonsol CLI."""

from typer import Typer

from cli.commands import extract, init, mount, patch, release, validate, wad
from cli.games import ps1  # noqa: F401

app = Typer(
    help="Gaeilge sa Chonsol ROM hacking CLI.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

init.register(app)
app.add_typer(extract.app, name="extract")
app.add_typer(patch.app, name="patch")
app.add_typer(mount.app, name="mount")
app.add_typer(wad.app, name="wad")
app.add_typer(validate.app, name="validate")
app.add_typer(release.app, name="release")


def run() -> None:
    """Console script entry point."""
    app()


if __name__ == "__main__":
    run()
