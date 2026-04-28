"""Answer command for DocuSwarm CLI."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console

from autoBMAD.docuswarm.pipeline.questions import QuestionHandler
from autoBMAD.docuswarm.storage.state_manager import StateManager

console = Console()


@click.command("answer")
@click.argument("question_id")
@click.argument("answer", required=False)
@click.option("--text", "-t", help="Answer text (alternative to positional argument)")
def answer(question_id: str, answer_text: str | None, text: str | None) -> None:
    """Record an answer to a question.

    QUESTION_ID: The unique question ID (format: pipeline_id_node_index)
    ANSWER: The answer text, or use --text / -t option
    """
    answer_str = answer_text or text
    if not answer_str:
        console.print(
            "[red]Error: Answer text is required. Provide as positional argument or use --text/-t option.[/red]"
        )
        raise click.ClickException("Answer text is required")

    try:
        parts = question_id.rsplit("_", 2)
        if len(parts) < 3:
            console.print(f"[red]Error: Invalid question ID format: {question_id}[/red]")
            console.print(
                "[dim]Expected format: pipeline_id_node_index (e.g., abc123_analyst_0)[/dim]"
            )
            raise click.ClickException(f"Invalid question ID format: {question_id}")

        pipeline_id = "_".join(parts[:-2])

        state_manager = StateManager()
        question_handler = QuestionHandler(state_manager=state_manager)

        try:
            answered_question = asyncio.run(
                question_handler.answer_question(pipeline_id, question_id, answer_str)
            )
        except ValueError as ve:
            console.print(f"[red]Error: {ve}[/red]")
            raise click.ClickException(str(ve)) from ve

        console.print("[green]✓[/green] Answer recorded successfully")
        console.print(f"  Question ID: [cyan]{answered_question.question_id}[/cyan]")
        console.print(f"  Answer: {answer_str}")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to record answer: {e}[/red]")
        raise click.ClickException(f"Failed to record answer: {e}") from e
