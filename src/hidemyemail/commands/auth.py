"""Authentication and setup commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from hidemyemail.auth.keychain import KeychainManager
from hidemyemail.auth.touchid import is_available as touchid_available
from hidemyemail.config import (
    clear_default_username,
    get_default_username,
    set_default_username,
)
from hidemyemail.core.exceptions import AuthenticationError, TwoFactorRequiredError
from hidemyemail.core.icloud_client import ICloudClient

app = typer.Typer(help="Authentication commands")
console = Console()


@app.command()
def setup() -> None:
    """
    Interactive setup to store Apple ID credentials.

    Stores your credentials in the macOS Keychain, protected by Touch ID.
    You'll need to authenticate with Touch ID each time you use the CLI.
    """
    console.print("[bold blue]Hide My Email CLI Setup[/bold blue]\n")

    # Check Touch ID availability
    if touchid_available():
        console.print(
            "[green]✓[/green] Touch ID is available and will be used for authentication"
        )
    else:
        console.print(
            "[yellow]![/yellow] Touch ID not available. "
            "Credentials will be stored in Keychain without biometric protection."
        )
        if not Confirm.ask("Continue without Touch ID protection?"):
            raise typer.Abort()

    # Get credentials
    username = Prompt.ask("Apple ID (email)")
    password = Prompt.ask("Password", password=True)

    # Store in keychain
    keychain = KeychainManager()
    if not keychain.store_password(
        username, password, require_biometry=touchid_available()
    ):
        error_msg = keychain.last_error or "Unknown error"
        console.print(
            f"[red]Failed to store credentials in Keychain:[/red] {error_msg}"
        )
        raise typer.Exit(1)

    console.print("[green]✓[/green] Credentials stored securely")

    # Save as default username
    set_default_username(username)
    console.print(f"[green]✓[/green] Set {username} as default account")

    # Test authentication
    console.print("\nTesting iCloud authentication...")
    client = ICloudClient()

    def get_2fa_code() -> str:
        return Prompt.ask("Enter 2FA code from your device")

    try:
        client.authenticate(username, password, twofa_callback=get_2fa_code)
        console.print("[green]✓[/green] Successfully authenticated with iCloud")
        console.print(
            "\n[bold green]Setup complete![/bold green] Use 'hide-my-email list' to see your email aliases."
        )
    except TwoFactorRequiredError:
        # 2FA was required and handled
        console.print("[green]✓[/green] 2FA verified and session trusted")
        console.print(
            "\n[bold green]Setup complete![/bold green] Use 'hide-my-email list' to see your email aliases."
        )
    except AuthenticationError as e:
        console.print(f"[red]Authentication failed:[/red] {e}")
        # Clean up stored credentials on failure
        keychain.delete_password(username)
        clear_default_username()
        raise typer.Exit(1)


@app.command()
def logout(
    username: str | None = typer.Option(
        None,
        "--username",
        "-u",
        help="Apple ID to remove (defaults to current account)",
    ),
) -> None:
    """Remove stored credentials and session data."""
    if username is None:
        username = get_default_username()
        if username is None:
            console.print("[yellow]No account configured. Nothing to remove.[/yellow]")
            return

    if not Confirm.ask(f"Remove credentials for [cyan]{username}[/cyan]?"):
        raise typer.Abort()

    keychain = KeychainManager()
    client = ICloudClient()

    # Remove keychain entry
    if keychain.delete_password(username):
        console.print(f"[green]✓[/green] Removed credentials for {username}")
    else:
        console.print(f"[yellow]No stored credentials found for {username}[/yellow]")

    # Clear session
    client.clear_session(username)
    console.print("[green]✓[/green] Cleared session data")

    # Clear default username if it matches
    if get_default_username() == username:
        clear_default_username()
        console.print("[green]✓[/green] Cleared default account")


@app.command()
def status() -> None:
    """Show current authentication status."""
    username = get_default_username()

    if username is None:
        console.print("[yellow]No account configured.[/yellow]")
        console.print("Run 'hide-my-email setup' to configure your Apple ID.")
        return

    console.print(f"Account: [cyan]{username}[/cyan]")

    keychain = KeychainManager()
    if keychain.has_password(username):
        console.print("Credentials: [green]Stored in Keychain[/green]")
    else:
        console.print("Credentials: [red]Not found[/red]")

    client = ICloudClient()
    if client.is_session_valid(username):
        console.print("Session: [green]Valid[/green]")
    else:
        console.print("Session: [yellow]Expired or missing[/yellow]")

    if touchid_available():
        console.print("Touch ID: [green]Available[/green]")
    else:
        console.print("Touch ID: [yellow]Not available[/yellow]")
