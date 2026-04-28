"""Questions command for DocuSwarm CLI."""

from __future__ import annotations

import click
from rich.console import Console

from autoBMAD.docuswarm.pipeline.questions import QuestionHandler, QuestionPriority
from autoBMAD.docuswarm.storage.state_manager import StateManager

console = Console()


@click.command("questions")
@click.argument("pipeline_id")
@click.option(
    "--run",
    "-r",
    "run_id",
    default=None,
    help="Query a specific run ID instead of latest",
)
def questions(pipeline_id: str, run_id: str | None) -> None:
    """List all unanswered questions for the specified pipeline.

    Displays questions sorted by priority: blocking (red), clarifying (yellow), optional (dimmed).
    """
    try:
        state_manager = StateManager()
        question_handler = QuestionHandler(state_manager=state_manager)

        all_questions = question_handler.get_unanswered_questions(pipeline_id, run_id=run_id)

        run_info = f" (Run: {run_id})" if run_id else " (Latest)"

        if not all_questions:
            console.print(
                f"[dim]No unanswered questions for pipeline: {pipeline_id}{run_info}[/dim]"
            )
            return

        priority_order = {
            QuestionPriority.BLOCKING: 0,
            QuestionPriority.CLARIFYING: 1,
            QuestionPriority.OPTIONAL: 2,
        }
        sorted_questions = sorted(all_questions, key=lambda q: priority_order[q.priority])

        console.print(
            f"\n[bold]Unanswered Questions for Pipeline: {pipeline_id}{run_info}[/bold]\n"
        )

        for question in sorted_questions:
            if question.priority == QuestionPriority.BLOCKING:
                priority_style = "[bold red]"
                priority_icon = "⚠️  "
                priority_label = "BLOCKING"
            elif question.priority == QuestionPriority.CLARIFYING:
                priority_style = "[yellow]"
                priority_icon = "ℹ️  "
                priority_label = "CLARIFYING"
            else:
                priority_style = "[dim]"
                priority_icon = "○  "
                priority_label = "OPTIONAL"

            console.print(f"{priority_icon}{priority_style}{priority_label}[/{priority_style}]")
            console.print(f"  ID: [cyan]{question.question_id}[/cyan]")
            console.print(f"  Question: {question.question_text}")
            console.print(f"  From node: [dim]{question.node_id}[/dim]")

            if question.context:
                console.print(f"  Context: [dim]{question.context}[/dim]")

            console.print()

        console.print(f"[dim]Total: {len(all_questions)} unanswered question(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Error: Failed to get questions: {e}[/red]")
        raise click.ClickException(f"Failed to get questions: {e}") from e
