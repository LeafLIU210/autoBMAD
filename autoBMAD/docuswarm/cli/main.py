"""Main CLI entry point for DocuSwarm.

This module provides a thin entry point that registers all CLI commands.
Business logic is delegated to services in the services/ module.
Commands are defined in the commands/ module.
"""

from __future__ import annotations

import click

from autoBMAD.docuswarm import __version__
from autoBMAD.docuswarm.cli.commands import (
    answer,
    cancel,
    clean,
    export,
    list_pipelines,
    questions,
    resume,
    start,
    status,
)
from autoBMAD.docuswarm.config import load_config
from autoBMAD.docuswarm.utils.logging import configure_logging


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose debug output")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default=None,
    help="Set logging level (overrides LOG_LEVEL env var)",
)
@click.option(
    "--log-file",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default=None,
    help="Directory for log files (default: ./logs)",
)
@click.option(
    "--json-log",
    is_flag=True,
    help="Use JSON format for log file output",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    log_level: str | None,
    log_file: str | None,
    json_log: bool,
) -> None:
    """DocuSwarm - Multi-Agent Document Orchestration System."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # Load configuration
    _ = load_config()

    # Initialize logging
    from pathlib import Path

    log_dir = Path(log_file) if log_file else None
    level = "DEBUG" if verbose else log_level
    _ = configure_logging(
        log_level=level,
        log_dir=log_dir,
        json_format=json_log,
    )


# Register commands
cli.add_command(start)
cli.add_command(status)
cli.add_command(resume)
cli.add_command(cancel)
cli.add_command(clean)
cli.add_command(list_pipelines)
cli.add_command(export)
cli.add_command(questions)
cli.add_command(answer)

if __name__ == "__main__":
    cli()
