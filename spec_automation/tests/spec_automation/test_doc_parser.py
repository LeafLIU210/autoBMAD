"""
Tests for doc_parser.py
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from spec_automation.doc_parser import DocumentParser


@pytest.fixture
def parser():
    """Create a DocumentParser instance for testing."""
    return DocumentParser()


@pytest.fixture
def sample_story_content():
    """Sample story content for testing."""
    return """
# Story Title: Test Story

## Story

**As a** developer,
**I want** to test the document parser,
**so that** I can ensure it works correctly.

## Acceptance Criteria

1. First acceptance criterion
2. Second acceptance criterion
3. Third acceptance criterion

## Requirements

- Requirement 1
- Requirement 2
- Requirement 3

## Tasks / Subtasks

- [ ] Task 1: Do something
- [ ] Task 2: Do something else
- [ ] Task 3: Complete testing

## Implementation

- Step 1: Implementation step
- Step 2: Another step
"""


@pytest.fixture
def sample_story_with_bmad():
    """Sample story with BMAD header."""
    return """
# <!-- Powered by BMAD™ Core -->

# Story: Advanced Document Parser

## Story

**As a** QA engineer,
**I want** comprehensive test coverage,
**so that** the parser works perfectly.

## Acceptance Criteria

1. Parse document title correctly
2. Extract all requirements
3. Handle acceptance criteria properly
4. Process implementation steps

## Requirements

- Must parse markdown files
- Should extract structured data
- Needs to handle edge cases

## Tasks / Subtasks

- [ ] Task 1: Create parser class
- [ ] Task 2: Implement extraction methods
- [ ] Task 3: Add validation logic

## Implementation

- Step 1: Initialize parser
- Step 2: Parse content
- Step 3: Return structured data
"""


@pytest.fixture
def sample_minimal_content():
    """Minimal story content."""
    return """# Minimal Story

This is a minimal story with just a title.
"""


@pytest.fixture
def sample_empty_content():
    """Empty content."""
    return ""


class TestDocumentParser:
    """Test cases for DocumentParser."""

    def test_init(self, parser):
        """Test parser initialization."""
        assert parser is not None
        assert isinstance(parser, DocumentParser)

    def test_parse_string_basic(self, parser, sample_story_content):
        """Test parsing basic story content."""
        result = parser.parse_string(sample_story_content)

        assert "title" in result
        assert "requirements" in result
        assert "acceptance_criteria" in result
        assert "implementation_steps" in result

    def test_extract_title_basic(self, parser, sample_story_content):
        """Test title extraction from basic content."""
        result = parser.parse_string(sample_story_content)
        assert result["title"] == "Story Title: Test Story"

    def test_extract_title_with_bmad(self, parser, sample_story_with_bmad):
        """Test title extraction with BMAD header."""
        result = parser.parse_string(sample_story_with_bmad)
        # Parser currently extracts the first H1, which is the BMAD header
        assert result["title"] == "<!-- Powered by BMAD™ Core -->"

    def test_extract_title_fallback(self, parser, sample_minimal_content):
        """Test title extraction fallback."""
        result = parser.parse_string(sample_minimal_content)
        assert result["title"] == "Minimal Story"

    def test_extract_title_empty(self, parser, sample_empty_content):
        """Test title extraction from empty content."""
        result = parser.parse_string(sample_empty_content)
        assert result["title"] == "Untitled Document"

    def test_extract_requirements(self, parser, sample_story_content):
        """Test requirements extraction."""
        result = parser.parse_string(sample_story_content)
        assert len(result["requirements"]) == 3
        assert "Requirement 1" in result["requirements"]
        assert "Requirement 2" in result["requirements"]
        assert "Requirement 3" in result["requirements"]

    def test_extract_requirements_with_bmad(self, parser, sample_story_with_bmad):
        """Test requirements extraction from BMAD content."""
        result = parser.parse_string(sample_story_with_bmad)
        assert len(result["requirements"]) == 3
        assert "Must parse markdown files" in result["requirements"]
        assert "Should extract structured data" in result["requirements"]

    def test_extract_acceptance_criteria(self, parser, sample_story_content):
        """Test acceptance criteria extraction."""
        result = parser.parse_string(sample_story_content)
        assert len(result["acceptance_criteria"]) == 3
        assert "First acceptance criterion" in result["acceptance_criteria"]
        assert "Second acceptance criterion" in result["acceptance_criteria"]
        assert "Third acceptance criterion" in result["acceptance_criteria"]

    def test_extract_acceptance_criteria_with_bmad(self, parser, sample_story_with_bmad):
        """Test acceptance criteria extraction from BMAD content."""
        result = parser.parse_string(sample_story_with_bmad)
        assert len(result["acceptance_criteria"]) == 4
        assert "Parse document title correctly" in result["acceptance_criteria"]
        assert "Extract all requirements" in result["acceptance_criteria"]

    def test_extract_implementation_steps(self, parser, sample_story_content):
        """Test implementation steps extraction."""
        result = parser.parse_string(sample_story_content)
        assert len(result["implementation_steps"]) == 3
        assert "Task 1: Do something" in result["implementation_steps"]
        assert "Task 2: Do something else" in result["implementation_steps"]
        assert "Task 3: Complete testing" in result["implementation_steps"]

    def test_extract_implementation_steps_with_bmad(self, parser, sample_story_with_bmad):
        """Test implementation steps extraction from BMAD content."""
        result = parser.parse_string(sample_story_with_bmad)
        assert len(result["implementation_steps"]) == 3
        assert "Step 1: Initialize parser" in result["implementation_steps"]
        assert "Step 2: Parse content" in result["implementation_steps"]

    def test_validate_parsed_document_valid(self, parser, sample_story_content):
        """Test validation of valid parsed document."""
        result = parser.parse_string(sample_story_content)
        is_valid, issues = parser.validate_parsed_document(result)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_parsed_document_invalid(self, parser):
        """Test validation of invalid parsed document."""
        invalid_doc = {
            "title": "",
            "requirements": "not a list",
            "acceptance_criteria": None,
            "implementation_steps": 123,
        }

        is_valid, issues = parser.validate_parsed_document(invalid_doc)

        assert is_valid is False
        assert len(issues) > 0
        assert "Missing document title" in issues
        assert "Requirements is not a list" in issues
        assert "Acceptance criteria is not a list" in issues
        assert "Implementation steps is not a list" in issues

    def test_parse_document_from_file(self, parser, sample_story_content):
        """Test parsing document from a file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_story.md"
            test_file.write_text(sample_story_content)

            result = parser.parse_document(test_file)

            assert result["title"] == "Story Title: Test Story"
            assert len(result["requirements"]) == 3
            assert len(result["acceptance_criteria"]) == 3

    def test_parse_nonexistent_file(self, parser):
        """Test parsing a non-existent file raises error."""
        nonexistent_file = Path("/tmp/nonexistent_file_12345.md")

        with pytest.raises(FileNotFoundError):
            parser.parse_document(nonexistent_file)

    def test_multiple_sections(self, parser):
        """Test parsing document with multiple sections."""
        content = """
# Multi-Section Story

## Story

**As a** user,
**I want** multiple sections,
**so that** testing is comprehensive.

## Requirements

- First requirement
- Second requirement

## Acceptance Criteria

1. First criterion
2. Second criterion

## Tasks / Subtasks

- [ ] Task 1
- [ ] Task 2

## Implementation

- Step 1
- Step 2

## Additional Section

This is additional content that should be ignored.
"""
        result = parser.parse_string(content)

        assert result["title"] == "Multi-Section Story"
        assert len(result["requirements"]) == 2
        assert len(result["acceptance_criteria"]) == 2
        assert len(result["implementation_steps"]) == 2

    def test_requirements_in_story_section(self, parser):
        """Test that requirements in 'Story' section are also extracted."""
        content = """
# Story with Requirements in Story Section

## Story

**As a** developer,
**I want** to parse requirements in story section,
**so that** I can extract all requirements.

## Acceptance Criteria

- Criterion 1
- Criterion 2
"""
        result = parser.parse_string(content)

        # Should find requirements in "I want" clause
        assert len(result["requirements"]) > 0
        assert "to parse requirements in story section" in result["requirements"][0]

    def test_numbered_requirements(self, parser):
        """Test parsing numbered requirements."""
        content = """
# Story with Numbered Requirements

## Requirements

1. First numbered requirement
2. Second numbered requirement
3. Third numbered requirement

## Acceptance Criteria

1. First numbered criterion
2. Second numbered criterion
"""
        result = parser.parse_string(content)

        assert len(result["requirements"]) == 3
        assert len(result["acceptance_criteria"]) == 2

    def test_mixed_bullet_points(self, parser):
        """Test parsing mixed bullet point styles."""
        content = """
# Story with Mixed Bullets

## Requirements

- Hyphen bullet
* Asterisk bullet
+ Plus bullet

## Tasks / Subtasks

- [ ] Checkbox 1
- [ ] Checkbox 2
- [ ] Checkbox 3
"""
        result = parser.parse_string(content)

        assert len(result["requirements"]) == 3
        assert "Hyphen bullet" in result["requirements"]
        assert "Asterisk bullet" in result["requirements"]
        assert "Plus bullet" in result["requirements"]

        assert len(result["implementation_steps"]) == 3
        assert "Checkbox 1" in result["implementation_steps"]

    def test_empty_sections(self, parser):
        """Test parsing document with empty sections."""
        content = """
# Story with Empty Sections

## Requirements

## Acceptance Criteria

## Tasks / Subtasks

"""
        result = parser.parse_string(content)

        assert result["title"] == "Story with Empty Sections"
        assert len(result["requirements"]) == 0
        assert len(result["acceptance_criteria"]) == 0
        assert len(result["implementation_steps"]) == 0

    def test_nested_content_ignored(self, parser):
        """Test that nested content in sections is properly handled."""
        content = """
# Nested Content Test

## Requirements

- Main requirement
  - Nested requirement (should be ignored)
  - Another nested (should be ignored)

## Acceptance Criteria

1. Main criterion
   - Nested criterion (should be ignored)

## Tasks / Subtasks

- Main task
  - Nested task (should be ignored)
"""
        result = parser.parse_string(content)

        # Should only get main level items
        assert len(result["requirements"]) == 1
        assert "Main requirement" in result["requirements"][0]

        assert len(result["acceptance_criteria"]) == 1
        assert "Main criterion" in result["acceptance_criteria"][0]

        assert len(result["implementation_steps"]) == 1
        assert "Main task" in result["implementation_steps"][0]


class TestDocParserAlias:
    """Test cases for backward compatibility alias DocParser."""

    def test_alias_exists(self):
        """Test that DocParser alias exists."""
        from spec_automation.doc_parser import DocParser
        assert DocParser is DocumentParser

    def test_alias_functional(self):
        """Test that DocParser alias works correctly."""
        from spec_automation.doc_parser import DocParser

        parser = DocParser()
        content = "# Test\n\n## Requirements\n- Test requirement"
        result = parser.parse_string(content)

        assert result["title"] == "Test"
        assert len(result["requirements"]) == 1
        assert "Test requirement" in result["requirements"]
