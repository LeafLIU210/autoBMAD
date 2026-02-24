"""Main CLI module for DocuSwarm."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any, cast

import click
from rich.console import Console
from rich.table import Table

from autoBMAD.docuswarm import __version__
from autoBMAD.docuswarm.config import load_config
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.pipeline.questions import QuestionHandler, QuestionPriority
from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES
from autoBMAD.docuswarm.storage.files import FileStorage
from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.utils.logging import configure_logging

console = Console()

# Type alias for context object
ContextDict = dict[str, Any]


class CliContext:
    """Type-safe context object for CLI commands."""

    def __init__(self, verbose: bool) -> None:
        self.verbose = verbose
        self.config = None  # Will be set after loading config


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
    ctx.obj = CliContext(verbose=verbose)

    # Load configuration from .env and YAML
    config = load_config()
    ctx.obj.config = config  # Store config in context for other commands

    # Initialize logging
    log_dir = Path(log_file) if log_file else None
    level = "DEBUG" if verbose else log_level
    _ = configure_logging(
        log_level=level,
        log_dir=log_dir,
        json_format=json_log,
    )


@cli.command()
@click.option(
    "--context",
    "-c",
    "context_file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the context file for the pipeline",
)
@click.pass_context
def start(ctx: click.Context, context_file: str) -> None:
    """Start a new pipeline with the provided context file."""
    verbose: bool = cast(CliContext, ctx.obj).verbose

    # Validate context file
    context_path = Path(context_file)
    if not context_path.exists():
        console.print(f"[red]Error: Context file not found: {context_file}[/red]")
        raise click.ClickException(f"Context file not found: {context_file}")

    if not context_path.is_file():
        console.print(f"[red]Error: Context path is not a file: {context_file}[/red]")
        raise click.ClickException(f"Context path is not a file: {context_file}")

    # Read context file
    try:
        with open(context_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        console.print(f"[red]Error: Failed to read context file: {e}[/red]")
        raise click.ClickException(f"Failed to read context file: {e}") from e

    # Create pipeline using HybridOrchestrator
    try:
        # Extract subject from context file (first line or filename)
        subject = context_path.stem

        if verbose:
            console.print(f"[dim]Creating pipeline for subject: {subject}[/dim]")

        # Use HybridOrchestrator to start the pipeline
        config = load_config()
        orchestrator = HybridOrchestrator(
            db_path=str(config.db_path),
            api_key=config.api_key,
            base_url=config.base_url,
        )

        # Prepare subject context
        subject_context = {
            "subject": subject,
            "context_file": str(context_path),
            "content": content,
        }

        # Run async start_pipeline
        pipeline_id = asyncio.run(orchestrator.start_pipeline(subject_context))

        console.print(f"[green]+[/green] Pipeline started: [bold]{pipeline_id}[/bold]")
        console.print(f"  Subject: {subject}")
        console.print(f"  Context: {context_file}")

    except Exception as e:
        console.print(f"[red]Error: Failed to start pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to start pipeline: {e}") from e


@cli.command()
@click.argument("pipeline_id")
@click.pass_context
def status(ctx: click.Context, pipeline_id: str) -> None:
    """Show detailed progress of the specified pipeline."""
    verbose: bool = cast(CliContext, ctx.obj).verbose

    try:
        state_manager = StateManager()
        pipeline: dict[str, Any] | None = state_manager.get_pipeline(pipeline_id)

        if pipeline is None:
            console.print(f"[red]Error: Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")

        # Create rich table for pipeline details
        table = Table(title=f"Pipeline Status: {pipeline_id}", show_header=True)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        pipeline_id_val: str = str(cast(str, pipeline["pipeline_id"]))
        pipeline_subject: str = str(cast(str, pipeline["subject"]))
        pipeline_status: str = str(cast(str, pipeline["status"]))
        table.add_row("Pipeline ID", pipeline_id_val)
        table.add_row("Subject", pipeline_subject)
        table.add_row("Status", f"[bold]{pipeline_status}[/bold]")

        # Format timestamps
        created_at: str = str(cast(str, pipeline.get("created_at")) or "N/A")
        updated_at: str = str(cast(str, pipeline.get("updated_at")) or "N/A")
        table.add_row("Created At", created_at)
        table.add_row("Updated At", updated_at)

        console.print(table)

        # Get pipeline state for node status
        pipeline_state: dict[str, Any] = pipeline.get("state", {})
        current_node: str = str(cast(str, pipeline.get("current_node")) or "")
        completed_nodes: list[str] = pipeline_state.get("completed_nodes", [])
        node_iterations: dict[str, int] = pipeline_state.get("node_iterations", {})

        # Create node status table showing all 5 nodes
        nodes_table = Table(title="Node Status", show_header=True)
        nodes_table.add_column("Node", style="cyan")
        nodes_table.add_column("Status", style="green")
        nodes_table.add_column("Iteration", style="yellow")

        # Determine status for each node
        for node_id in PIPELINE_NODES:
            if node_id in completed_nodes:
                # Completed node
                status_display = "✓ Completed"
                iteration = str(node_iterations.get(node_id, 1))
            elif node_id == current_node:
                # Currently running
                status_display = "→ Running"
                iteration = str(node_iterations.get(node_id, 1))
            else:
                # Pending node
                status_display = "○ Pending"
                iteration = "-"

            nodes_table.add_row(node_id, status_display, iteration)

        console.print(nodes_table)

        # Show current node at bottom
        console.print(f"Current Node: {current_node or 'N/A'}")

        # Show node results if any
        node_results: list[dict[str, Any]] = (
            cast(list[dict[str, Any]], pipeline.get("node_results")) or []
        )
        if node_results and verbose:
            results_table = Table(title="Node Results (Verbose)", show_header=True)
            results_table.add_column("Node", style="cyan")
            results_table.add_column("Iteration", style="yellow")
            results_table.add_column("Status", style="green")

            for result in node_results:
                node_id: str = str(cast(str, result.get("node_id")) or "unknown")
                iteration: str = str(cast(int, result.get("iteration")) or 1)
                status_val: str = str(cast(str, result.get("status")) or "unknown")
                results_table.add_row(node_id, iteration, status_val)

            console.print(results_table)

        if verbose:
            console.print(f"[dim]State: {pipeline.get('state', {})}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: Failed to get pipeline status: {e}[/red]")
        raise click.ClickException(f"Failed to get pipeline status: {e}") from e


@cli.command()
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
@click.pass_context
def resume(ctx: click.Context, pipeline_id: str, node_id: str | None, force: bool) -> None:
    """Resume an interrupted pipeline from its last checkpoint.

    Use --node to restart from a specific node instead of resuming.
    Use --force to resume a running pipeline.
    """
    verbose: bool = cast(CliContext, ctx.obj).verbose

    try:
        state_manager = StateManager()
        pipeline: dict[str, Any] | None = state_manager.get_pipeline(pipeline_id)

        if pipeline is None:
            console.print(f"[red]Error: Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")

        current_status: str = str(cast(str, pipeline["status"]))

        # Check if pipeline can be resumed
        if current_status == "completed":
            console.print("[yellow]Warning: Pipeline already completed[/yellow]")
            raise click.ClickException(f"Pipeline already completed: {pipeline_id}")

        if current_status == "running" and not force:
            console.print("[yellow]Warning: Pipeline is already running[/yellow]")
            raise click.ClickException(f"Pipeline is already running: {pipeline_id}")

        # Use HybridOrchestrator for resume
        orchestrator = HybridOrchestrator()

        if node_id:
            # Restart from specific node
            if verbose:
                console.print(f"[dim]Restarting from node: {node_id}[/dim]")

            _ = asyncio.run(orchestrator.restart_from_node(pipeline_id, node_id))
            console.print(f"[green]+[/green] Pipeline restarted: [bold]{pipeline_id}[/bold]")
            console.print(f"  Restarting from node: {node_id}")
        else:
            # Regular resume from checkpoint
            current_node: str = str(cast(str, pipeline.get("current_node")) or "")
            state: dict[str, Any] = cast(dict[str, Any], pipeline.get("state")) or {}

            if verbose:
                console.print("[dim]Resuming from checkpoint...[/dim]")
                console.print(f"[dim]Current node: {current_node}[/dim]")
                console.print(f"[dim]Saved state: {state}[/dim]")

            _ = asyncio.run(orchestrator.resume_pipeline(pipeline_id))
            console.print(f"[green]+[/green] Pipeline resumed: [bold]{pipeline_id}[/bold]")
            console.print(f"  Previous status: {current_status}")
            console.print(f"  Resuming from node: {current_node or 'start'}")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to resume pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to resume pipeline: {e}") from e


@cli.command()
@click.argument("pipeline_id")
@click.argument("output_dir", default=".", required=False)
@click.option(
    "--output",
    "-o",
    "output_path",
    default=None,
    help="Custom destination directory for exported files",
)
@click.option(
    "--include-metadata",
    is_flag=True,
    default=False,
    help="Include _metadata.json in the export",
)
@click.pass_context
def export(
    ctx: click.Context,
    pipeline_id: str,
    output_dir: str,
    output_path: str | None,
    include_metadata: bool,
) -> None:
    """Export all deliverables to the specified output directory."""
    verbose: bool = cast(CliContext, ctx.obj).verbose

    # Determine destination path
    dest_dir = Path(output_path) if output_path else Path(output_dir)
    if output_path and output_dir != ".":
        dest_dir = Path(output_path)

    # Use default output location relative to current working directory
    storage = FileStorage()

    # Source pipeline directory
    pipeline_source = storage.output_root / pipeline_id

    if not pipeline_source.exists():
        click.echo(f"Error: Pipeline '{pipeline_id}' not found in output directory.", err=True)
        click.echo(f"Expected location: {pipeline_source}", err=True)
        raise click.ClickException(f"Pipeline '{pipeline_id}' not found")

    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Find all markdown files to export
    md_files: list[Path] = list(pipeline_source.glob("*.md"))

    if not md_files:
        click.echo(f"Warning: No deliverables found for pipeline '{pipeline_id}'", err=True)

    # Export deliverables
    exported_count = 0
    for md_file in md_files:
        dest_file = dest_dir / md_file.name
        name = str(md_file.name)
        _: Path | str = shutil.copy2(src=md_file, dst=dest_file)
        exported_count += 1
        if verbose:
            click.echo(f"Exported: {name}")

    # Export metadata if requested
    metadata_file: Path = pipeline_source / "_metadata.json"
    if include_metadata and metadata_file.exists():
        _: Path | str = shutil.copy2(src=metadata_file, dst=dest_dir / "_metadata.json")
        if verbose:
            click.echo("Exported metadata")

    # Show summary
    click.echo(f"Exported pipeline '{pipeline_id}' to '{dest_dir}'")
    click.echo(f"  Deliverables: {exported_count}")
    if include_metadata:
        click.echo("  Metadata: included")
    else:
        click.echo("  Metadata: excluded (use --include-metadata to include)")


@cli.command()
@click.option(
    "--status",
    "-s",
    "status_filter",
    default=None,
    type=click.Choice(["pending", "running", "completed", "failed", "paused"]),
    help="Filter pipelines by status",
)
@click.pass_context
def list_pipelines(ctx: click.Context, status_filter: str | None) -> None:
    """Show all pipelines with their status, optionally filtered by status."""
    verbose: bool = cast(CliContext, ctx.obj).verbose

    try:
        state_manager = StateManager()
        pipelines: list[dict[str, Any]] = state_manager.list_pipelines(status=status_filter)

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
            # Color code status
            status: str = str(cast(str, pipeline["status"]))
            status_style: str = {
                "pending": "yellow",
                "running": "blue",
                "completed": "green",
                "failed": "red",
                "paused": "magenta",
            }.get(status, "white")

            pipeline_id_val: str = str(cast(str, pipeline["pipeline_id"]))
            pipeline_subject: str = str(cast(str, pipeline["subject"]))
            current_node_val: str = str(cast(str, pipeline.get("current_node")) or "-")
            created_at_val: str = str(cast(str, pipeline.get("created_at")) or "")

            table.add_row(
                pipeline_id_val,
                pipeline_subject,
                f"[{status_style}]{status}[/{status_style}]",
                current_node_val,
                created_at_val,
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(pipelines)} pipeline(s)[/dim]")

        if verbose and status_filter:
            console.print(f"[dim]Filtered by status: {status_filter}[/dim]")

    except Exception as e:
        console.print(f"[red]Error: Failed to list pipelines: {e}[/red]")
        raise click.ClickException(f"Failed to list pipelines: {e}") from e


@cli.command()
@click.argument("pipeline_id")
@click.option(
    "--run",
    "-r",
    "run_id",
    default=None,
    help="Query a specific run ID instead of latest",
)
@click.pass_context
def questions(ctx: click.Context, pipeline_id: str, run_id: str | None) -> None:
    """List all unanswered questions for the specified pipeline.

    Displays questions sorted by priority: blocking (red), clarifying (yellow), optional (dimmed).

    Use --run to query questions from a specific run instead of the latest.
    """
    verbose: bool = cast(CliContext, ctx.obj).verbose

    try:
        # Initialize QuestionHandler with StateManager for context updates
        state_manager = StateManager()
        question_handler = QuestionHandler(state_manager=state_manager)

        # Get all unanswered questions (optionally filtered by run_id)
        all_questions = question_handler.get_unanswered_questions(pipeline_id, run_id=run_id)

        # Build run info string for display
        run_info = f" (Run: {run_id})" if run_id else " (Latest)"

        if not all_questions:
            console.print(
                f"[dim]No unanswered questions for pipeline: {pipeline_id}{run_info}[/dim]"
            )
            return

        # Sort questions by priority (blocking first)
        priority_order = {
            QuestionPriority.BLOCKING: 0,
            QuestionPriority.CLARIFYING: 1,
            QuestionPriority.OPTIONAL: 2,
        }
        sorted_questions = sorted(all_questions, key=lambda q: priority_order[q.priority])

        # Display questions
        console.print(
            f"\n[bold]Unanswered Questions for Pipeline: {pipeline_id}{run_info}[/bold]\n"
        )

        for question in sorted_questions:
            # Apply styling based on priority
            if question.priority == QuestionPriority.BLOCKING:
                priority_style = "[bold red]"
                priority_icon = "⚠️  "
                priority_label = "BLOCKING"
            elif question.priority == QuestionPriority.CLARIFYING:
                priority_style = "[yellow]"
                priority_icon = "ℹ️  "
                priority_label = "CLARIFYING"
            else:  # OPTIONAL
                priority_style = "[dim]"
                priority_icon = "○  "
                priority_label = "OPTIONAL"

            console.print(f"{priority_icon}{priority_style}{priority_label}[/{priority_style}]")
            console.print(f"  ID: [cyan]{question.question_id}[/cyan]")
            console.print(f"  Question: {question.question_text}")
            console.print(f"  From node: [dim]{question.node_id}[/dim]")

            # Show context if available
            if question.context:
                console.print(f"  Context: [dim]{question.context}[/dim]")

            console.print()  # Blank line between questions

        console.print(f"[dim]Total: {len(all_questions)} unanswered question(s)[/dim]")

        if verbose:
            console.print("[dim]Retrieved from QuestionHandler[/dim]")

    except Exception as e:
        console.print(f"[red]Error: Failed to get questions: {e}[/red]")
        raise click.ClickException(f"Failed to get questions: {e}") from e


@cli.command()
@click.argument("question_id")
@click.argument("answer", required=False)
@click.option("--text", "-t", help="Answer text (alternative to positional argument)")
@click.pass_context
def answer(ctx: click.Context, question_id: str, answer: str | None, text: str | None) -> None:
    """Record an answer to a question.

    QUESTION_ID: The unique question ID (format: pipeline_id_node_index)

    ANSWER: The answer text, or use --text / -t option
    """
    verbose: bool = cast(CliContext, ctx.obj).verbose

    # Determine answer text
    answer_text = answer or text
    if not answer_text:
        console.print(
            "[red]Error: Answer text is required. Provide as positional argument or use --text/-t option.[/red]"
        )
        raise click.ClickException("Answer text is required")

    try:
        # Parse question_id to get pipeline_id
        # Format: {pipeline_id}_{node_id}_{index}
        parts = question_id.rsplit("_", 2)
        if len(parts) < 3:
            console.print(f"[red]Error: Invalid question ID format: {question_id}[/red]")
            console.print(
                "[dim]Expected format: pipeline_id_node_index (e.g., abc123_analyst_0)[/dim]"
            )
            raise click.ClickException(f"Invalid question ID format: {question_id}")

        pipeline_id = "_".join(parts[:-2])  # Rejoin in case pipeline_id has underscores

        # Initialize QuestionHandler with StateManager for context updates
        state_manager = StateManager()
        question_handler = QuestionHandler(state_manager=state_manager)

        # Answer the question (async call)
        try:
            answered_question = asyncio.run(
                question_handler.answer_question(pipeline_id, question_id, answer_text)
            )
        except ValueError as ve:
            console.print(f"[red]Error: {ve}[/red]")
            raise click.ClickException(str(ve)) from ve

        # Show success message
        console.print("[green]✓[/green] Answer recorded successfully")
        console.print(f"  Question ID: [cyan]{answered_question.question_id}[/cyan]")
        console.print(f"  Answer: {answer_text}")

        if verbose:
            console.print("[dim]Answer incorporated into pipeline context[/dim]")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to record answer: {e}[/red]")
        raise click.ClickException(f"Failed to record answer: {e}") from e


@cli.command("cancel")
@click.argument("pipeline_id")
@click.pass_context
def cancel_pipeline(_ctx: click.Context, pipeline_id: str) -> None:
    """Cancel a running pipeline.

    This will stop the pipeline execution and mark it as cancelled."""
    try:
        state_manager = StateManager()
        pipeline = state_manager.get_pipeline(pipeline_id)

        if pipeline is None:
            console.print(f"[red]Error: Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")

        current_status = pipeline["status"]
        if current_status == "cancelled":
            console.print("[yellow]Pipeline is already cancelled[/yellow]")
            return

        if current_status == "completed":
            console.print("[yellow]Cannot cancel a completed pipeline[/yellow]")
            return

        # Update status to cancelled
        state_manager.update_pipeline_status(
            pipeline_id=pipeline_id,
            status="cancelled",
        )

        console.print(f"[green]✓[/green] Pipeline cancelled: [bold]{pipeline_id}[/bold]")
        console.print(f"  Previous status: {current_status}")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to cancel pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to cancel pipeline: {e}") from e


@cli.command("cancel-all")
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
@click.pass_context
def cancel_all_pipelines(_ctx: click.Context, status: str | None, confirm: bool) -> None:
    """Cancel all pipelines (or filter by status).

    Examples:
        # Cancel all pending pipelines
        python -m autoBMAD.docuswarm cancel-all --status pending --confirm

        # Cancel all pipelines with confirmation
        python -m autoBMAD.docuswarm cancel-all
    """
    try:
        state_manager = StateManager()

        # Get all pipelines
        pipelines = state_manager.list_pipelines(status=status)

        if not pipelines:
            console.print("[yellow]No pipelines found to cancel[/yellow]")
            return

        # Filter out already cancelled and completed
        cancellable = [p for p in pipelines if p["status"] not in ["cancelled", "completed"]]

        if not cancellable:
            console.print("[yellow]No cancellable pipelines found[/yellow]")
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

        # Cancel each pipeline
        cancelled_count = 0
        for p in cancellable:
            try:
                state_manager.update_pipeline_status(
                    pipeline_id=p["pipeline_id"],
                    status="cancelled",
                )
                cancelled_count += 1
            except Exception as e:
                console.print(f"[red]Failed to cancel {p['pipeline_id']}: {e}[/red]")

        console.print(f"\n[green]✓[/green] Cancelled {cancelled_count} pipeline(s)")

    except Exception as e:
        console.print(f"[red]Error: Failed to cancel pipelines: {e}[/red]")
        raise click.ClickException(f"Failed to cancel pipelines: {e}") from e


@cli.command("clean")
@click.option(
    "--status",
    type=click.Choice(["pending", "cancelled", "failed", "completed"], case_sensitive=False),
    default=None,
    help="Only delete pipelines with this status",
)
@click.option(
    "--older-than-days",
    type=int,
    default=None,
    help="Only delete pipelines older than N days",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def clean_pipelines(
    _ctx: click.Context, status: str | None, older_than_days: int | None, confirm: bool
) -> None:
    """Delete pipelines from database.

    WARNING: This permanently deletes pipeline data!

    Examples:
        # Delete all cancelled and failed pipelines
        python -m autoBMAD.docuswarm clean --status cancelled --confirm

        # Delete completed pipelines older than 7 days
        python -m autoBMAD.docuswarm clean --status completed --older-than-days 7
    """
    try:
        state_manager = StateManager()
        db = state_manager.db

        # Build query
        query = "SELECT pipeline_id, subject, status, created_at FROM pipelines WHERE 1=1"
        params: list[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if older_than_days:
            from datetime import UTC, datetime, timedelta

            cutoff_date = (datetime.now(UTC) - timedelta(days=older_than_days)).isoformat()
            query += " AND created_at < ?"
            params.append(cutoff_date)

        # Get pipelines to delete
        with db.acquire() as conn:
            cursor = conn.execute(query, params)
            pipelines = cursor.fetchall()

        if not pipelines:
            console.print("[yellow]No pipelines found to delete[/yellow]")
            return

        # Show what will be deleted
        console.print(
            f"\n[bold red]WARNING: About to PERMANENTLY DELETE {len(pipelines)} pipeline(s):[/bold red]"
        )
        for p in pipelines:
            console.print(f"  - {p['pipeline_id']} ({p['status']}) - {p['created_at']}")

        # Confirmation
        if not confirm:
            if not click.confirm(
                "\n[red]This cannot be undone. Do you want to proceed?[/red]", default=False
            ):
                console.print("[yellow]Cancelled by user[/yellow]")
                return

        # Delete pipelines
        deleted_count = 0
        with db.acquire() as conn:
            for p in pipelines:
                try:
                    # Delete node results first (foreign key)
                    conn.execute(
                        "DELETE FROM node_results WHERE pipeline_id = ?", (p["pipeline_id"],)
                    )
                    # Delete pipeline
                    conn.execute("DELETE FROM pipelines WHERE pipeline_id = ?", (p["pipeline_id"],))
                    deleted_count += 1
                except Exception as e:
                    console.print(f"[red]Failed to delete {p['pipeline_id']}: {e}[/red]")

        console.print(f"\n[green]✓[/green] Deleted {deleted_count} pipeline(s)")

    except Exception as e:
        console.print(f"[red]Error: Failed to clean pipelines: {e}[/red]")
        raise click.ClickException(f"Failed to clean pipelines: {e}") from e


if __name__ == "__main__":
    cli()
