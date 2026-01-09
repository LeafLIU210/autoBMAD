"""
Document Parser for spec_automation module.

Parses Markdown planning documents (Sprint Change Proposals, Functional Specs, Technical Plans)
and extracts structured information: title, requirements, acceptance criteria, implementation steps.
"""

import re
import logging
from typing import Dict, List, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for extracting structured information from Markdown planning documents."""

    def __init__(self):
        """Initialize the DocumentParser."""
        pass

    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Markdown document and extract structured information.

        Args:
            file_path: Path to the Markdown document

        Returns:
            Dictionary containing parsed document information:
            - title: Document title
            - requirements: List of requirements
            - acceptance_criteria: List of acceptance criteria
            - implementation_steps: List of implementation steps
            - tasks: List of tasks (alias for implementation_steps)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self._parse_content(content)
        except FileNotFoundError:
            logger.error(f"Document not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            raise

    def parse_string(self, content: str) -> Dict[str, Any]:
        """
        Parse Markdown content from a string.

        Args:
            content: Markdown content as string

        Returns:
            Dictionary containing parsed document information
        """
        return self._parse_content(content)

    def _parse_content(self, content: str) -> Dict[str, Any]:
        """
        Internal method to parse Markdown content.

        Args:
            content: Markdown content

        Returns:
            Dictionary containing parsed information
        """
        implementation_steps = self._extract_implementation_steps(content)
        result = {
            "title": self._extract_title(content),
            "requirements": self._extract_requirements(content),
            "acceptance_criteria": self._extract_acceptance_criteria(content),
            "implementation_steps": implementation_steps,
            # Add 'tasks' as an alias for backward compatibility
            "tasks": implementation_steps,
        }

        return result

    def _extract_title(self, content: str) -> str:
        """
        Extract document title from Markdown content.

        Args:
            content: Markdown content

        Returns:
            Document title
        """
        lines = content.split("\n")

        for line in lines:
            line_stripped = line.strip()

            # Skip BMAD header comments
            if "Powered by BMAD" in line_stripped or "BMAD™" in line_stripped:
                continue

            # Skip empty lines
            if not line_stripped:
                continue

            # Match H1 header
            h1_match = re.match(r"^#\s+(.+)$", line_stripped)
            if h1_match:
                title = h1_match.group(1).strip()
                # Skip if title is just a comment
                if title.startswith("<!--") and title.endswith("-->"):
                    continue
                return title

        # Fallback: first non-empty line that's not a comment
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith("<!--"):
                return line_stripped

        return "Untitled Document"

    def _extract_requirements(self, content: str) -> list[str]:
        """
        Extract requirements from Markdown content.

        Args:
            content: Markdown content

        Returns:
            List of requirements
        """
        requirements: list[str] = []
        lines = content.split("\n")
        in_requirements_section = False

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check for "Requirements" section (main or sub-section)
            if re.match(
                r"^#+\s*(?:Requirements?|Functional Requirements?|Non-Functional Requirements?)",
                line_stripped,
                re.IGNORECASE,
            ):
                in_requirements_section = True
                continue

            # Check for "As a... I want" pattern (user story format)
            if re.match(r"^#+\s*As a", line_stripped, re.IGNORECASE):
                in_requirements_section = True
                continue

            # Check for end of requirements section (major non-requirements section)
            if in_requirements_section and re.match(
                r"^##\s+(?!.*Requirements?)",
                line_stripped,
            ):
                # Only stop on H2, not H3 subsections
                in_requirements_section = False
                continue

            # Extract bullet points or numbered items
            if in_requirements_section:
                # Bullet points with various formats
                bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", line_stripped)
                if bullet_match:
                    req = bullet_match.group(1).strip()
                    if req:
                        requirements.append(req)
                    continue

                # Numbered items
                num_match = re.match(r"^\s*\d+\.\s+(.+)$", line_stripped)
                if num_match:
                    req = num_match.group(1).strip()
                    if req:
                        requirements.append(req)
                    continue

        return requirements

    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """
        Extract acceptance criteria from Markdown content.

        Args:
            content: Markdown content

        Returns:
            List of acceptance criteria
        """
        criteria = []
        lines = content.split("\n")
        in_criteria_section = False

        for line in lines:
            line_stripped = line.strip()

            # Check for "Acceptance Criteria" section
            if re.match(
                r"^#+\s*(?:Acceptance Criteria|Acceptance)",
                line_stripped,
                re.IGNORECASE,
            ):
                in_criteria_section = True
                continue

            # Check for end of acceptance criteria section
            if in_criteria_section and re.match(r"^#+\s+(?!.*criteria)", line_stripped):
                in_criteria_section = False
                continue

            # Extract bullet points or numbered items
            if in_criteria_section:
                # Bullet points with various formats
                bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", line_stripped)
                if bullet_match:
                    criterion = bullet_match.group(1).strip()
                    if criterion:
                        criteria.append(criterion)
                    continue

                # Numbered items
                num_match = re.match(r"^\s*\d+\.\s+(.+)$", line_stripped)
                if num_match:
                    criterion = num_match.group(1).strip()
                    if criterion:
                        criteria.append(criterion)
                    continue

        return criteria

    def _extract_implementation_steps(self, content: str) -> List[str]:
        """
        Extract implementation steps from Markdown content.

        Args:
            content: Markdown content

        Returns:
            List of implementation steps
        """
        steps = []
        lines = content.split("\n")
        in_steps_section = False

        for line in lines:
            line_stripped = line.strip()

            # Check for various section headers that might contain steps
            if re.match(
                r"^#+\s*(?:Tasks?|Subtasks?|Implementation|Steps?)",
                line_stripped,
                re.IGNORECASE,
            ):
                in_steps_section = True
                continue

            # Check for end of steps section (next major section that's not a subtask)
            if in_steps_section and re.match(
                r"^#+\s+(?!.*Step|Task|Subtask|Implementation)", line_stripped
            ):
                in_steps_section = False
                continue

            # Extract bullet points or numbered items
            if in_steps_section:
                # Bullet points with various formats
                bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", line_stripped)
                if bullet_match:
                    step = bullet_match.group(1).strip()
                    if step:
                        steps.append(step)
                    continue

                # Numbered items
                num_match = re.match(r"^\s*\d+\.\s+(.+)$", line_stripped)
                if num_match:
                    step = num_match.group(1).strip()
                    if step:
                        steps.append(step)
                    continue

        return steps

    def validate_parsed_document(
        self, parsed_doc: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate parsed document structure.

        Args:
            parsed_doc: Parsed document dictionary

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check title
        if not parsed_doc.get("title"):
            issues.append("Missing document title")

        # Check lists (they can be empty but should exist)
        if not isinstance(parsed_doc.get("requirements"), list):
            issues.append("Requirements is not a list")

        if not isinstance(parsed_doc.get("acceptance_criteria"), list):
            issues.append("Acceptance criteria is not a list")

        if not isinstance(parsed_doc.get("implementation_steps"), list):
            issues.append("Implementation steps is not a list")

        return len(issues) == 0, issues


# Backward compatibility alias
DocParser = DocumentParser
