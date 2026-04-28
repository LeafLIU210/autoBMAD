"""Cancel-all command for DocuSwarm CLI."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console

from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService

console = Console()


@click.command("cancel-all")
@click.option(
    "--status",
    type=click.Choice(["pending", "running", "paused", "failed"], case_sensitive=False),
    default=None,
    help="Only cancel pipelines with this status",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
def cancel_all(status: str | None, confirm: bool) -> None:
    """Cancel all pipelines (or filter by status).

    Examples:
        # Cancel all pending pipelines
        docuswarm cancel-all --status pending --confirm

        # Cancel all pipelines with confirmation
        docuswarm cancel-all
    """
    service = PipelineService()

    try:
        # Get cancellable pipelines
        cancellable, cancelled_count = asyncio.run(service.cancel_all(status=status))

        if not cancellable:
            console.print("[yellow]No pipelines found to cancel[/yellow]")
            return

        # Show what will be cancelled
        console.print(f"\n[bold]About to cancel {len(cancellable)} pipeline(s):[/bold]")
        for p in cancellable:
            console.print(f"  - {p['pipeline_id']} ({p['status']})")

        # Confirmation
        if not confirm:
            if not click.confirm("\nDo you want to proceed?"):
                console.print("[yellow]Cancelled by user[/yellow]")
                return

        console.print(f"\n[green]✓[/green] Cancelled {cancelled_count} pipeline(s)")

    except Exception as e:
        console.print(f"[red]Error: Failed to cancel pipelines: {e}[/red]")
        raise click.ClickException(f"Failed to cancel pipelines: {e}") from e
