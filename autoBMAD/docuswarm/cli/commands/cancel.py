"""Cancel command for DocuSwarm CLI."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console

from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService

console = Console()


@click.command("cancel")
@click.argument("pipeline_id")
def cancel(pipeline_id: str) -> None:
    """Cancel a running pipeline.

    This will stop the pipeline execution and mark it as cancelled.
    """
    service = PipelineService()

    try:
        asyncio.run(service.cancel(pipeline_id))
        console.print(f"[green]✓[/green] Pipeline cancelled: [bold]{pipeline_id}[/bold]")
    except ValueError as e:
        console.print(f"[yellow]{e}[/yellow]")
        raise click.ClickException(str(e)) from e
    except Exception as e:
        console.print(f"[red]Error: Failed to cancel pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to cancel pipeline: {e}") from e
