"""CreateDocumentSetTool - 创建多个结构化文档的工具.

This module provides a tool for creating multiple documents based on
node templates with structure validation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, override

import aiofiles
import yaml
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class DocumentSpec(BaseModel):
    """Single document specification.

    Attributes:
        template_id: Template identifier from templates YAML.
        title: Document title (overrides template default).
        content: Document content in Markdown.
        metadata: Additional metadata.
    """

    template_id: str = Field(description="Template ID from node templates")
    title: str | None = Field(default=None, description="Custom title (optional)")
    content: str = Field(description="Document content in Markdown")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CreateDocumentSetParams(BaseModel):
    """Parameters for creating a document set.

    Attributes:
        documents: List of documents to create (1-10).
        node_id: Node identifier for template loading.
    """

    documents: list[DocumentSpec] = Field(
        description="List of documents to create", min_length=1, max_length=10
    )
    node_id: str = Field(
        default="unknown",
        description="Node identifier for template loading (analyst, pm, ux, architect, po)",
    )


def _slugify_filename(title: str) -> str:
    """Convert title to a valid filename slug.

    Args:
        title: The document title.

    Returns:
        A slugified filename with .md extension.
    """
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.md" if slug else "document.md"


class CreateDocumentSetTool(CallableTool2[CreateDocumentSetParams]):
    """Tool for creating multiple structured documents based on templates.

    This tool extends create_deliverable to support:
    - Multiple document creation in one call
    - Template-based validation
    - Mermaid diagram validation
    - Documentation standards enforcement

    Features:
    - Template loading from YAML files
    - Required section validation
    - Mermaid diagram syntax checking
    - Automatic filename generation
    """

    name: str = "create_document_set"
    description: str = "Create multiple structured documents based on node templates"
    params: type[CreateDocumentSetParams] = CreateDocumentSetParams

    def __init__(self) -> None:
        """Initialize the tool with template loading."""
        super().__init__()
        self.templates_cache: dict[str, Any] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all node template configurations."""
        # Compute templates directory
        current_file = Path(__file__)
        templates_dir = current_file.parent.parent / "templates"

        if not templates_dir.exists():
            return

        # Load all YAML template files
        for template_file in templates_dir.glob("*_templates.yaml"):
            try:
                with open(template_file, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    node_id = config.get("node_id")
                    if node_id:
                        self.templates_cache[node_id] = config
            except (yaml.YAMLError, OSError):
                pass  # Skip invalid template files

    def _get_template(self, node_id: str, template_id: str) -> dict[str, Any] | None:
        """Get template configuration.

        Args:
            node_id: Node identifier.
            template_id: Template identifier.

        Returns:
            Template config dict or None if not found.
        """
        node_templates = self.templates_cache.get(node_id)
        if not node_templates:
            return None

        for template in node_templates.get("templates", []):
            if template.get("template_id") == template_id:
                return template

        return None

    def _validate_content_structure(
        self, content: str, template: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate document content against template structure.

        Args:
            content: Document content.
            template: Template configuration.

        Returns:
            Tuple of (is_valid, list of missing sections).
        """
        missing_sections: list[str] = []

        required_sections = [
            section["heading"]
            for section in template.get("sections", [])
            if section.get("required", False)
        ]

        for section in required_sections:
            # Check for heading (both ## and # formats)
            patterns = [f"## {section}", f"# {section}", f"### {section}"]
            if not any(pattern in content for pattern in patterns):
                missing_sections.append(section)

        return len(missing_sections) == 0, missing_sections

    def _validate_mermaid_diagrams(self, content: str) -> tuple[bool, list[str]]:
        """Validate Mermaid diagram syntax.

        Args:
            content: Document content.

        Returns:
            Tuple of (is_valid, list of errors).
        """
        errors: list[str] = []

        # Extract mermaid code blocks
        mermaid_pattern = r"```mermaid\s*\n(.*?)\n```"
        diagrams = re.findall(mermaid_pattern, content, re.DOTALL)

        valid_diagram_types = [
            "flowchart",
            "sequenceDiagram",
            "classDiagram",
            "erDiagram",
            "stateDiagram-v2",
            "gitGraph",
            "graph",
            "pie",
            "journey",
            "gantt",
        ]

        for i, diagram in enumerate(diagrams):
            first_line = diagram.strip().split("\n")[0].strip()

            # Check if starts with valid diagram type
            if not any(first_line.startswith(dtype) for dtype in valid_diagram_types):
                errors.append(
                    f"Mermaid block {i + 1}: Missing diagram type. Found: '{first_line[:30]}...'"
                )

        return len(errors) == 0, errors

    @override
    async def __call__(self, params: CreateDocumentSetParams) -> ToolReturnValue:
        """Create multiple documents with validation.

        Args:
            params: Validated parameters.

        Returns:
            ToolOk on success, ToolError on failure.
        """
        try:
            created_files: list[str] = []
            validation_warnings: list[str] = []

            # Get current working directory (should be pipeline output dir)
            output_dir = Path.cwd()

            for doc_spec in params.documents:
                # Get template
                template = self._get_template(params.node_id, doc_spec.template_id)

                # Determine filename
                if template and "filename_pattern" in template:
                    filename = template["filename_pattern"]
                elif doc_spec.title:
                    filename = _slugify_filename(doc_spec.title)
                else:
                    filename = _slugify_filename(doc_spec.template_id)

                # Validate content structure (if template exists)
                if template:
                    is_valid, missing = self._validate_content_structure(doc_spec.content, template)
                    if not is_valid:
                        for section in missing:
                            validation_warnings.append(
                                f"{filename}: Missing required section '{section}'"
                            )

                # Validate Mermaid diagrams
                is_valid, mermaid_errors = self._validate_mermaid_diagrams(doc_spec.content)
                if not is_valid:
                    for error in mermaid_errors:
                        validation_warnings.append(f"{filename}: {error}")

                # Write file
                file_path = output_dir / filename
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(doc_spec.content)

                created_files.append(filename)

            # Build result message
            result_msg = f"Created {len(created_files)} document(s):\n"
            result_msg += "\n".join(f"  - {f}" for f in created_files)

            if validation_warnings:
                result_msg += "\n\nValidation Warnings:\n"
                result_msg += "\n".join(f"  - {w}" for w in validation_warnings)

            return ToolOk(output=result_msg)

        except PermissionError as e:
            return ToolError(
                output="", message=f"Permission denied: {e}", brief="Permission denied"
            )
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Failed to create document set")
