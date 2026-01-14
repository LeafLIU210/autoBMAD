"""Module for parsing and extracting structured information from documents."""

from pathlib import Path


class DocumentParser:
    """A class to parse and extract structured information from documents."""

    def __init__(self, file_path: Path):
        """Initialize the DocumentParser with a file path.

        Args:
            file_path: Path to the document to be parsed.
        """
        self.file_path = file_path
        self.content: str = ""
        self.structure: dict[str, list[str]] = {}

    def read_file(self) -> str:
        """Read the content of the file.

        Returns:
            The content of the file as a string.
        """
        try:
            with open(self.file_path, encoding="utf-8") as f:
                self.content = f.read()
            return self.content
        except Exception:
            self.content = ""
            return ""

    def extract_headings(self) -> list[str]:
        """Extract headings from the content.

        Returns:
            A list of headings found in the content.
        """
        if not self.content:
            return []
        lines = self.content.splitlines()
        headings = []
        for line in lines:
            if line.startswith("#"):
                headings.append(line.lstrip("#").strip())
        return headings

    def extract_sections(self) -> dict[str, str]:
        """Extract sections from the content based on headings.

        Returns:
            A dictionary where keys are headings and values are the section content.
        """
        sections = {}
        if not self.content:
            return sections
        lines = self.content.splitlines()
        current_heading = None
        current_section = []
        for line in lines:
            if line.startswith("#"):
                if current_heading:
                    sections[current_heading] = "\n".join(current_section).strip()
                current_heading = line
                current_section = []
            else:
                current_section.append(line)
        if current_heading:
            sections[current_heading] = "\n".join(current_section).strip()
        return sections

    def parse(self) -> dict[str, list[dict[str, str]]]:
        """Parse the document and return its structure.

        Returns:
            A dictionary containing the headings and sections of the document.
        """
        if not self.content:
            self.read_file()
        return {
            "headings": self.extract_headings(),
            "sections": self.extract_sections(),
        }
