"""Main CLI application entry point."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from hidemyemail import __version__
from hidemyemail.commands import auth, emails

app = typer.Typer(
    name="hide-my-email",
    help="Hide My Email CLI - Manage your Apple Hide My Email aliases",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"hide-my-email version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version", "-v", callback=version_callback, help="Show version and exit"
        ),
    ] = None,
) -> None:
    """Hide My Email CLI - Manage your Apple Hide My Email aliases."""
    pass


# Add auth subcommands
app.add_typer(auth.app, name="auth", help="Authentication commands")

# Expose main commands at root level for convenience
app.command("setup")(auth.setup)
app.command("logout")(auth.logout)
app.command("status")(auth.status)

# Email commands at root level
app.command("list")(emails.list_emails)
app.command("search")(emails.search)
app.command("create")(emails.create)
app.command("deactivate")(emails.deactivate)
app.command("reactivate")(emails.reactivate)
app.command("delete")(emails.delete)
app.command("update")(emails.update)


if __name__ == "__main__":
    app()
