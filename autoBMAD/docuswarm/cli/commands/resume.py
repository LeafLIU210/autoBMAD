"""Resume command for DocuSwarm CLI."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console

from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

console = Console()


@click.command()
@click.argument("pipeline_id")
@click.option(
    "--node",
    "-n",
    "node_id",
    default=None,
    type=click.Choice(PIPELINE_NODES),
    help="Restart from a specific node (instead of resuming from last checkpoint)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force resume even if pipeline is running",
)
def resume(pipeline_id: str, node_id: str | None, force: bool) -> None:
    """Resume an interrupted pipeline from its last checkpoint.
    
    Use --node to restart from a specific node instead of resuming.
    Use --force to resume a running pipeline.
    """
    service = PipelineService()
    
    try:
        pipeline = service.status(pipeline_id)
        
        if pipeline is None:
            console.print(f"[red]Error: Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")

        current_status = pipeline["status"]

        if current_status == "completed":
            console.print("[yellow]Warning: Pipeline already completed[/yellow]")
            raise click.ClickException(f"Pipeline already completed: {pipeline_id}")

        if current_status == "running" and not force:
            console.print("[yellow]Warning: Pipeline is already running[/yellow]")
            raise click.ClickException(f"Pipeline is already running: {pipeline_id}")

        if node_id:
            _ = asyncio.run(service.restart_from_node(pipeline_id, node_id))
            console.print(f"[green]+[/green] Pipeline restarted: [bold]{pipeline_id}[/bold]")
            console.print(f"  Restarting from node: {node_id}")
        else:
            current_node = pipeline.get("current_node", "")
            _ = asyncio.run(service.resume(pipeline_id))
            console.print(f"[green]+[/green] Pipeline resumed: [bold]{pipeline_id}[/bold]")
            console.print(f"  Previous status: {current_status}")
            console.print(f"  Resuming from node: {current_node or 'start'}")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to resume pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to resume pipeline: {e}") from e
