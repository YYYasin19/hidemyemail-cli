"""Hide My Email management commands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from hidemyemail.config import get_default_username
from hidemyemail.core.exceptions import (
    AliasOperationError,
    AuthenticationError,
    CredentialsNotFoundError,
)
from hidemyemail.core.hidemyemail import HideMyEmailService
from hidemyemail.core.icloud_client import ICloudClient

app = typer.Typer(help="Manage Hide My Email aliases")
console = Console()


def get_service() -> HideMyEmailService:
    """Get authenticated HideMyEmail service."""
    username = get_default_username()
    if username is None:
        console.print("[red]No account configured.[/red]")
        console.print("Run 'hme setup' first to configure your Apple ID.")
        raise typer.Exit(1)

    client = ICloudClient()

    def get_2fa_code() -> str:
        return Prompt.ask("Enter 2FA code from your device")

    try:
        client.authenticate(username, twofa_callback=get_2fa_code)
    except CredentialsNotFoundError:
        console.print("[red]No credentials found.[/red]")
        console.print("Run 'hme setup' to configure your Apple ID.")
        raise typer.Exit(1)
    except AuthenticationError as e:
        console.print(f"[red]Authentication failed:[/red] {e}")
        raise typer.Exit(1)

    return HideMyEmailService(client)


@app.command("list")
def list_emails(
    active_only: Annotated[
        bool, typer.Option("--active", "-a", help="Show only active aliases")
    ] = False,
    limit: Annotated[
        int, typer.Option("--limit", "-n", help="Maximum number to display")
    ] = 50,
) -> None:
    """List all Hide My Email aliases."""
    with console.status("Fetching aliases..."):
        service = get_service()
        aliases = list(service.list_all())

    if active_only:
        aliases = [a for a in aliases if a.is_active]

    total = len(aliases)
    aliases = aliases[:limit]

    if not aliases:
        console.print("[yellow]No aliases found.[/yellow]")
        return

    table = Table(title=f"Hide My Email Aliases ({len(aliases)} of {total})")
    table.add_column("Email", style="cyan", no_wrap=True)
    table.add_column("Label", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Created", style="dim")

    for alias in aliases:
        status = "[green]Active[/green]" if alias.is_active else "[red]Inactive[/red]"
        table.add_row(
            alias.email,
            alias.label or "(no label)",
            status,
            alias.created_at.strftime("%Y-%m-%d"),
        )

    console.print(table)

    if total > limit:
        console.print(f"\n[dim]Showing {limit} of {total} aliases. Use --limit to see more.[/dim]")


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search term (matches label, email, or note)")],
) -> None:
    """Search for aliases by label, email, or note."""
    with console.status(f"Searching for '{query}'..."):
        service = get_service()
        results = list(service.search(query))

    if not results:
        console.print(f"[yellow]No aliases found matching '{query}'[/yellow]")
        return

    table = Table(title=f"Search Results: '{query}' ({len(results)} found)")
    table.add_column("Email", style="cyan", no_wrap=True)
    table.add_column("Label", style="green")
    table.add_column("Note", style="dim", max_width=30)
    table.add_column("Status", style="yellow")

    for alias in results:
        status = "[green]Active[/green]" if alias.is_active else "[red]Inactive[/red]"
        note = alias.note[:30] + "..." if len(alias.note) > 30 else alias.note
        table.add_row(alias.email, alias.label, note, status)

    console.print(table)


@app.command()
def create(
    label: Annotated[str, typer.Argument(help="Label for the new alias (e.g., 'Netflix')")],
    note: Annotated[str | None, typer.Option("--note", "-n", help="Optional note")] = None,
) -> None:
    """Create a new Hide My Email alias."""
    with console.status("Generating new alias..."):
        service = get_service()
        try:
            alias = service.create(label, note or "")
        except AliasOperationError as e:
            console.print(f"[red]Failed to create alias:[/red] {e}")
            raise typer.Exit(1)

    console.print(f"[green]✓[/green] Created new alias:")
    console.print(f"  Email: [cyan]{alias.email}[/cyan]")
    console.print(f"  Label: [green]{alias.label}[/green]")
    if alias.note:
        console.print(f"  Note:  {alias.note}")

    # Copy to clipboard hint
    console.print(f"\n[dim]Tip: Copy the email with: echo '{alias.email}' | pbcopy[/dim]")


@app.command()
def deactivate(
    email_or_id: Annotated[str, typer.Argument(help="Email address or anonymous ID")],
) -> None:
    """Deactivate an alias (stops forwarding, can be reactivated)."""
    with console.status("Looking up alias..."):
        service = get_service()
        alias = service.get_by_email_or_id(email_or_id)

    if not alias:
        console.print(f"[red]Alias not found: {email_or_id}[/red]")
        raise typer.Exit(1)

    if not alias.is_active:
        console.print(f"[yellow]Alias is already inactive: {alias.email}[/yellow]")
        return

    if Confirm.ask(f"Deactivate [cyan]{alias.email}[/cyan]?"):
        with console.status("Deactivating..."):
            if service.deactivate(alias.anonymous_id):
                console.print(f"[green]✓[/green] Deactivated {alias.email}")
            else:
                console.print("[red]Failed to deactivate alias[/red]")
                raise typer.Exit(1)


@app.command()
def reactivate(
    email_or_id: Annotated[str, typer.Argument(help="Email address or anonymous ID")],
) -> None:
    """Reactivate a deactivated alias."""
    with console.status("Looking up alias..."):
        service = get_service()
        alias = service.get_by_email_or_id(email_or_id)

    if not alias:
        console.print(f"[red]Alias not found: {email_or_id}[/red]")
        raise typer.Exit(1)

    if alias.is_active:
        console.print(f"[yellow]Alias is already active: {alias.email}[/yellow]")
        return

    with console.status("Reactivating..."):
        if service.reactivate(alias.anonymous_id):
            console.print(f"[green]✓[/green] Reactivated {alias.email}")
        else:
            console.print("[red]Failed to reactivate alias[/red]")
            raise typer.Exit(1)


@app.command()
def delete(
    email_or_id: Annotated[str, typer.Argument(help="Email address or anonymous ID")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Permanently delete an alias."""
    with console.status("Looking up alias..."):
        service = get_service()
        alias = service.get_by_email_or_id(email_or_id)

    if not alias:
        console.print(f"[red]Alias not found: {email_or_id}[/red]")
        raise typer.Exit(1)

    if not force:
        console.print(f"[bold red]Warning:[/bold red] This will permanently delete the alias.")
        console.print(f"  Email: [cyan]{alias.email}[/cyan]")
        console.print(f"  Label: {alias.label}")
        if not Confirm.ask("Are you sure?"):
            raise typer.Abort()

    with console.status("Deleting..."):
        if service.delete(alias.anonymous_id):
            console.print(f"[green]✓[/green] Deleted {alias.email}")
        else:
            console.print("[red]Failed to delete alias[/red]")
            raise typer.Exit(1)


@app.command()
def update(
    email_or_id: Annotated[str, typer.Argument(help="Email address or anonymous ID")],
    label: Annotated[str | None, typer.Option("--label", "-l", help="New label")] = None,
    note: Annotated[str | None, typer.Option("--note", "-n", help="New note")] = None,
) -> None:
    """Update an alias label or note."""
    if label is None and note is None:
        console.print("[yellow]Specify at least --label or --note to update[/yellow]")
        raise typer.Exit(1)

    with console.status("Looking up alias..."):
        service = get_service()
        alias = service.get_by_email_or_id(email_or_id)

    if not alias:
        console.print(f"[red]Alias not found: {email_or_id}[/red]")
        raise typer.Exit(1)

    new_label = label if label is not None else alias.label
    new_note = note if note is not None else alias.note

    with console.status("Updating..."):
        if service.update(alias.anonymous_id, new_label, new_note):
            console.print(f"[green]✓[/green] Updated {alias.email}")
            if label is not None:
                console.print(f"  Label: {new_label}")
            if note is not None:
                console.print(f"  Note: {new_note}")
        else:
            console.print("[red]Failed to update alias[/red]")
            raise typer.Exit(1)
