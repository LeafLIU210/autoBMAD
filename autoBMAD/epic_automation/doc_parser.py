# doc_parser.py

"""A simple document parser for Markdown files."""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class DocumentParser:
    """A class to parse Markdown documents and extract their structure."""

    def __init__(self, file_path: Path) -> None:
        """Initialize the DocumentParser with the path to the file to parse.

        Args:
            file_path: The path to the file to parse.
        """
        self.file_path = file_path
        self.content: str = ""
        self.structure: Dict[str, Any] = {}

    def read_file(self) -> str:
        """Read the content of the file.

        Returns:
            The content of the file as a string.
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.content = file.read()
        return self.content

    def extract_headings(self) -> List[str]:
        """Extract all headings from the document.

        Returns:
            A list of headings in the order they appear.
        """
        headings = re.findall(r"^#+\s+(.+)$", self.content, re.MULTILINE)
        return headings

    def extract_sections(self) -> Dict[str, str]:
        """Extract all sections from the document.

        Returns:
            A dictionary where keys are section headings and values are section content.
        """
        sections = {}
        lines = self.content.splitlines()
        current_heading: Optional[str] = None
        current_content: List[str] = []

        for line in lines:
            if re.match(r"^#+\s+(.+)$", line):
                if current_heading:
                    sections[current_heading] = "\n".join(current_content)
                current_heading = line.strip()
                current_content = []
            else:
                current_content.append(line)

        if current_heading:
            sections[current_heading] = "\n".join(current_content)

        return sections

    def parse(self) -> Dict[str, Any]:
        """Parse the document and return its structure.

        Returns:
            A dictionary containing the parsed structure of the document.
        """
        self.read_file()
        self.structure = {
            "headings": self.extract_headings(),
            "sections": self.extract_sections(),
        }
        return self.structure