"""Clean command for DocuSwarm CLI."""

from __future__ import annotations

from typing import Any

import click
from rich.console import Console

from autoBMAD.docuswarm.storage.state_manager import StateManager

console = Console()


@click.command("clean")
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
def clean(status: str | None, older_than_days: int | None, confirm: bool) -> None:
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
                    conn.execute(
                        "DELETE FROM node_results WHERE pipeline_id = ?", (p["pipeline_id"],)
                    )
                    conn.execute(
                        "DELETE FROM pipelines WHERE pipeline_id = ?", (p["pipeline_id"],)
                    )
                    deleted_count += 1
                except Exception as e:
                    console.print(f"[red]Failed to delete {p['pipeline_id']}: {e}[/red]")

        console.print(f"\n[green]✓[/green] Deleted {deleted_count} pipeline(s)")

    except Exception as e:
        console.print(f"[red]Error: Failed to clean pipelines: {e}[/red]")
        raise click.ClickException(f"Failed to clean pipelines: {e}") from e
