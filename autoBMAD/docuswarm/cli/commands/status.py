"""Status command for DocuSwarm CLI."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES

console = Console()


@click.command()
@click.argument("pipeline_id")
def status(pipeline_id: str) -> None:
    """Show detailed progress of the specified pipeline."""
    service = PipelineService()
    
    try:
        pipeline = service.status(pipeline_id)
        
        if pipeline is None:
            console.print(f"[red]Error: Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")

        # Create rich table for pipeline details
        table = Table(title=f"Pipeline Status: {pipeline_id}", show_header=True)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Pipeline ID", str(pipeline["pipeline_id"]))
        table.add_row("Subject", str(pipeline["subject"]))
        table.add_row("Status", f"[bold]{pipeline['status']}[/bold]")
        table.add_row("Created At", str(pipeline.get("created_at", "N/A")))
        table.add_row("Updated At", str(pipeline.get("updated_at", "N/A")))

        console.print(table)

        # Get pipeline state for node status
        pipeline_state = pipeline.get("state", {})
        current_node = pipeline.get("current_node", "")
        completed_nodes = pipeline_state.get("completed_nodes", [])
        node_iterations = pipeline_state.get("node_iterations", {})

        # Create node status table showing all 5 nodes
        nodes_table = Table(title="Node Status", show_header=True)
        nodes_table.add_column("Node", style="cyan")
        nodes_table.add_column("Status", style="green")
        nodes_table.add_column("Iteration", style="yellow")

        for node_id in PIPELINE_NODES:
            if node_id in completed_nodes:
                status_display = "✓ Completed"
                iteration = str(node_iterations.get(node_id, 1))
            elif node_id == current_node:
                status_display = "→ Running"
                iteration = str(node_iterations.get(node_id, 1))
            else:
                status_display = "○ Pending"
                iteration = "-"

            nodes_table.add_row(node_id, status_display, iteration)

        console.print(nodes_table)

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to get pipeline status: {e}[/red]")
        raise click.ClickException(f"Failed to get pipeline status: {e}") from e
