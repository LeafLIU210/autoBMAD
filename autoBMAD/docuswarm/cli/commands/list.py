"""List command for DocuSwarm CLI."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService

console = Console()


@click.command("list")
@click.option(
    "--status",
    "-s",
    "status_filter",
    default=None,
    type=click.Choice(["pending", "running", "completed", "failed", "paused"]),
    help="Filter pipelines by status",
)
def list_pipelines(status_filter: str | None) -> None:
    """Show all pipelines with their status, optionally filtered by status."""
    service = PipelineService()
    
    try:
        pipelines = service.list_pipelines(status=status_filter)

        if not pipelines:
            if status_filter:
                console.print(f"[yellow]No pipelines found with status: {status_filter}[/yellow]")
            else:
                console.print("[yellow]No pipelines found[/yellow]")
            return

        # Create rich table
        table = Table(title="Pipelines", show_header=True)
        table.add_column("Pipeline ID", style="cyan")
        table.add_column("Subject", style="white")
        table.add_column("Status", style="green")
        table.add_column("Current Node", style="yellow")
        table.add_column("Created", style="dim")

        for pipeline in pipelines:
            status = str(pipeline["status"])
            status_style = {
                "pending": "yellow",
                "running": "blue",
                "completed": "green",
                "failed": "red",
                "paused": "magenta",
            }.get(status, "white")

            table.add_row(
                str(pipeline["pipeline_id"]),
                str(pipeline["subject"]),
                f"[{status_style}]{status}[/{status_style}]",
                str(pipeline.get("current_node", "-")),
                str(pipeline.get("created_at", "")),
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(pipelines)} pipeline(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Error: Failed to list pipelines: {e}[/red]")
        raise click.ClickException(f"Failed to list pipelines: {e}") from e
