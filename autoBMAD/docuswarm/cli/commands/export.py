"""Export command for DocuSwarm CLI."""

from __future__ import annotations

import shutil
from pathlib import Path

import click
from rich.console import Console

from autoBMAD.docuswarm.storage.files import FileStorage

console = Console()


@click.command("export")
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
def export(
    pipeline_id: str, output_dir: str, output_path: str | None, include_metadata: bool
) -> None:
    """Export all deliverables to the specified output directory."""
    try:
        dest_dir = Path(output_path) if output_path else Path(output_dir)
        if output_path and output_dir != ".":
            dest_dir = Path(output_path)

        storage = FileStorage()
        pipeline_source = storage.output_root / pipeline_id

        if not pipeline_source.exists():
            console.print(f"[red]Error: Pipeline '{pipeline_id}' not found[/red]")
            raise click.ClickException(f"Pipeline '{pipeline_id}' not found")

        dest_dir.mkdir(parents=True, exist_ok=True)
        md_files = list(pipeline_source.glob("*.md"))

        if not md_files:
            console.print(
                f"[yellow]Warning: No deliverables found for pipeline '{pipeline_id}'[/yellow]"
            )

        exported_count = 0
        for md_file in md_files:
            dest_file = dest_dir / md_file.name
            shutil.copy2(src=md_file, dst=dest_file)
            exported_count += 1

        metadata_file = pipeline_source / "_metadata.json"
        if include_metadata and metadata_file.exists():
            shutil.copy2(src=metadata_file, dst=dest_dir / "_metadata.json")

        console.print(f"[green]✓[/green] Exported pipeline '{pipeline_id}' to '{dest_dir}'")
        console.print(f"  Deliverables: {exported_count}")
        if include_metadata:
            console.print("  Metadata: included")
        else:
            console.print("  Metadata: excluded (use --include-metadata to include)")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: Failed to export pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to export pipeline: {e}") from e
