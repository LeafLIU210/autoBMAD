"""Specification parsing functionality."""

import re
from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class SpecificationData:
    """Represents a specification document."""

    name: str
    version: str
    description: str
    requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "requirements": self.requirements,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpecificationData":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description", ""),
            requirements=data.get("requirements", []),
        )


class SpecParser:
    """Parser for specification documents."""

    def __init__(self) -> None:
        """Initialize the parser."""
        pass

    def parse(self, content: str) -> SpecificationData:
        """Parse specification content.

        Args:
            content: The specification content to parse

        Returns:
            SpecificationData object
        """
        # Try YAML format first
        if self._is_yaml(content):
            return self._parse_yaml(content)

        # Otherwise parse as markdown
        return self._parse_markdown(content)

    def _is_yaml(self, content: str) -> bool:
        """Check if content is YAML format."""
        content = content.strip()
        # Simple heuristic: starts with name: or has proper YAML structure
        return content.startswith("name:") or content.startswith("---\n")

    def _parse_yaml(self, content: str) -> SpecificationData:
        """Parse YAML format specification."""
        try:
            # Remove YAML delimiters if present
            content = content.strip()
            if content.startswith("---"):
                content = content[3:]
            if content.endswith("---"):
                content = content[:-3]

            # Remove leading indentation from all lines (handle indented YAML)
            lines = content.split('\n')
            dedented_lines = []
            for line in lines:
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                # Remove leading spaces (at least 2, or all if less)
                if leading_spaces >= 2:
                    dedented_lines.append(line[2:])
                else:
                    dedented_lines.append(line)
            content = '\n'.join(dedented_lines)

            data = yaml.safe_load(content)
            return SpecificationData.from_dict(data)
        except Exception:
            # Fall back to markdown parsing
            return self._parse_markdown(content)

    def _parse_markdown(self, content: str) -> SpecificationData:
        """Parse markdown format specification."""
        lines = content.split("\n")

        name = ""
        version = ""
        description = ""

        # Track current section
        current_section = None
        description_lines = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check for section headers
            if line_stripped.startswith("## Name"):
                current_section = "name"
                continue
            elif line_stripped.startswith("## Version"):
                current_section = "version"
                continue
            elif line_stripped.startswith("## Description"):
                current_section = "description"
                continue
            elif line_stripped.startswith("## Requirements"):
                current_section = "requirements"
                continue
            elif line_stripped.startswith("# ") and i == 0:
                # Single # header (title) at the start - this is the name
                name = line_stripped[2:].strip()
                continue

            # Check for "Version: x.y.z" format (can appear outside sections)
            if not version and line_stripped.startswith("Version:"):
                version = line_stripped[8:].strip()
                continue

            # Process content based on current section
            if current_section == "name":
                if line_stripped and not line_stripped.startswith("##"):
                    # Non-empty line that's not a section header
                    name = line_stripped
                    current_section = None  # Done with name
            elif current_section == "version":
                if line_stripped and not line_stripped.startswith("##"):
                    # Non-empty line that's not a section header
                    version = line_stripped
                    current_section = None  # Done with version
            elif current_section == "description":
                if line_stripped.startswith("##"):
                    # Next section - done with description
                    current_section = None
                else:
                    # Add to description
                    description_lines.append(line)
            elif current_section == "requirements":
                # Requirements are handled by extract_requirements
                pass

        # Join description lines
        description = "\n".join(description_lines).strip()

        # Extract requirements
        requirements = extract_requirements(content)

        return SpecificationData(
            name=name,
            version=version,
            description=description,
            requirements=requirements,
        )


def parse_specification(content: str) -> SpecificationData:
    """Parse specification content.

    Args:
        content: The specification content to parse

    Returns:
        SpecificationData object
    """
    parser = SpecParser()
    return parser.parse(content)


def validate_specification(spec: SpecificationData) -> "ValidationResult":
    """Validate a specification.

    Args:
        spec: The specification to validate

    Returns:
        ValidationResult object
    """
    validator = SpecValidator()
    return validator.validate(spec)


def extract_requirements(text: str) -> list[str]:
    """Extract requirements from text.

    Args:
        text: The text to extract requirements from

    Returns:
        List of requirements
    """
    requirements = []

    # Match bullet points: - Requirement, * Requirement, or numbered lists
    bullet_pattern = r"^\s*[-*+]\s+(.+)$"
    numbered_pattern = r"^\s*\d+\.\s+(.+)$"

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        bullet_match = re.match(bullet_pattern, line)
        numbered_match = re.match(numbered_pattern, line)

        if bullet_match:
            req = bullet_match.group(1).strip()
            if req:
                requirements.append(req)
        elif numbered_match:
            req = numbered_match.group(1).strip()
            if req:
                requirements.append(req)

    return requirements


# Import at the end to avoid circular dependency
from autoBMAD.spec_automation.spec_validator import SpecValidator, ValidationResult
