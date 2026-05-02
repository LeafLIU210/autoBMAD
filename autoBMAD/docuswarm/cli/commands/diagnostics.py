"""Diagnostics command for DocuSwarm CLI.

Phase 2: Replaces the non-functional questions command with a read-only
diagnostics view that displays pipeline state questions as non-blocking
follow-ups for audit purposes.
"""

from __future__ import annotations

import click
from rich.console import Console

from autoBMAD.docuswarm.storage.state_manager import StateManager

console = Console()


@click.command("diagnostics")
@click.argument("pipeline_id")
def diagnostics(pipeline_id: str) -> None:
    """Show pipeline diagnostics including non-blocking follow-up questions.

    Displays questions recorded during pipeline execution as diagnostic
    information. These are clarifying/optional items only — blocking
    priority has been removed.
    """
    try:
        state_manager = StateManager()
        pipeline = state_manager.get_pipeline(pipeline_id)

        if pipeline is None:
            console.print(f"[red]Pipeline not found: {pipeline_id}[/red]")
            raise click.ClickException(f"Pipeline not found: {pipeline_id}")

        state = pipeline.get("state", {}) or {}
        questions = state.get("questions", [])

        console.print(f"\n[bold]Diagnostics for Pipeline: {pipeline_id}[/bold]\n")
        console.print(f"Status: [cyan]{state.get('status', 'unknown')}[/cyan]")
        console.print(f"Current node: [cyan]{state.get('current_node') or 'None'}[/cyan]")
        console.print(f"Completed nodes: {state.get('completed_nodes', [])}")
        console.print()

        if not questions:
            console.print("[dim]No follow-up questions recorded.[/dim]")
            return

        follow_ups = [q for q in questions if q.get("priority") in ("clarifying", "optional")]

        if not follow_ups:
            console.print("[dim]No clarifying/optional questions recorded.[/dim]")
            return

        console.print(f"[bold]Follow-up Questions ({len(follow_ups)}):[/bold]\n")

        for q in follow_ups:
            priority = q.get("priority", "optional")
            if priority == "clarifying":
                style = "[yellow]"
                icon = "ℹ️  "
            else:
                style = "[dim]"
                icon = "○  "

            console.print(f"{icon}{style}{priority.upper()}[/{style}]")
            console.print(f"  Question: {q.get('question_text') or q.get('question', 'N/A')}")
            console.print(f"  From node: [dim]{q.get('node_id', 'unknown')}[/dim]")
            if q.get("context"):
                console.print(f"  Context: [dim]{q['context']}[/dim]")
            console.print()

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to get diagnostics: {e}[/red]")
        raise click.ClickException(f"Failed to get diagnostics: {e}") from e
