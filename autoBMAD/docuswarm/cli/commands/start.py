"""Start command for DocuSwarm CLI."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console

from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService

console = Console()


@click.command()
@click.option(
    "--context",
    "-c",
    "context_file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the context file for the pipeline",
)
def start(context_file: str) -> None:
    """Start a new pipeline with the provided context file."""
    service = PipelineService()
    
    try:
        pipeline_id = asyncio.run(service.start(context_file))
        console.print(f"[green]+[/green] Pipeline started: [bold]{pipeline_id}[/bold]")
        console.print(f"  Context: {context_file}")
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e
    except Exception as e:
        console.print(f"[red]Error: Failed to start pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to start pipeline: {e}") from e
