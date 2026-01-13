# test_doc_parser.py

"""Unit tests for the doc_parser module."""

import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
from autoBMAD.epic_automation.doc_parser import DocumentParser


@pytest.fixture
def sample_markdown_content():
    """Provides sample Markdown content for testing."""
    return """
# Heading 1

This is a paragraph.

## Heading 2

This is another paragraph.

### Heading 3

Yet another paragraph.

# Heading 4

Final paragraph.
"""


@pytest.fixture
def sample_file(tmp_path, sample_markdown_content):
    """Creates a temporary Markdown file for testing."""
    file_path = tmp_path / "test.md"
    with open(file_path, "w") as f:
        f.write(sample_markdown_content)
    return file_path


class TestDocumentParser:
    """Test cases for the DocumentParser class."""

    def test_init(self, sample_file):
        """Test the initialization of DocumentParser."""
        parser = DocumentParser(sample_file)
        assert parser.file_path == sample_file
        assert parser.content == ""
        assert parser.structure == {}

    def test_read_file(self, sample_file):
        """Test the read_file method."""
        parser = DocumentParser(sample_file)
        content = parser.read_file()
        assert content is not None
        assert "# Heading 1" in content

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_read_file_empty(self, mock_file, sample_file):
        """Test read_file with an empty file."""
        parser = DocumentParser(sample_file)
        content = parser.read_file()
        assert content == ""

    def test_extract_headings(self, sample_file):
        """Test the extract_headings method."""
        parser = DocumentParser(sample_file)
        parser.read_file()
        headings = parser.extract_headings()
        assert len(headings) == 4
        assert "Heading 1" in headings
        assert "Heading 2" in headings
        assert "Heading 3" in headings
        assert "Heading 4" in headings

    def test_extract_headings_no_headings(self, tmp_path):
        """Test extract_headings when there are no headings."""
        file_path = tmp_path / "no_headings.md"
        with open(file_path, "w") as f:
            f.write("This is a paragraph with no headings.")

        parser = DocumentParser(file_path)
        parser.read_file()
        headings = parser.extract_headings()
        assert headings == []

    def test_extract_sections(self, sample_file):
        """Test the extract_sections method."""
        parser = DocumentParser(sample_file)
        parser.read_file()
        sections = parser.extract_sections()
        assert len(sections) == 4
        assert "# Heading 1" in sections
        assert "This is a paragraph." in sections["# Heading 1"]

    def test_extract_sections_no_sections(self, tmp_path):
        """Test extract_sections when there are no sections."""
        file_path = tmp_path / "no_sections.md"
        with open(file_path, "w") as f:
            f.write("This is a paragraph with no sections.")

        parser = DocumentParser(file_path)
        parser.read_file()
        sections = parser.extract_sections()
        assert sections == {}

    def test_parse(self, sample_file):
        """Test the parse method."""
        parser = DocumentParser(sample_file)
        structure = parser.parse()
        assert "headings" in structure
        assert "sections" in structure
        assert len(structure["headings"]) == 4
        assert len(structure["sections"]) == 4