"""
Tests for DocumentParser module.
"""

import pytest
from pathlib import Path
from spec_automation.doc_parser import DocumentParser


class TestDocumentParser:
    """Test suite for DocumentParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DocumentParser()

    def test_init(self):
        """Test parser initialization."""
        assert isinstance(self.parser, DocumentParser)

    def test_parse_string_simple(self):
        """Test parsing simple markdown content."""
        content = """# Test Title

## Requirements
- Requirement 1
- Requirement 2

## Acceptance Criteria
- Criterion 1
- Criterion 2

## Tasks
- Task 1
- Task 2
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Test Title"
        assert len(result["requirements"]) == 2
        assert "Requirement 1" in result["requirements"]
        assert "Requirement 2" in result["requirements"]
        assert len(result["acceptance_criteria"]) == 2
        assert "Criterion 1" in result["acceptance_criteria"]
        assert "Criterion 2" in result["acceptance_criteria"]
        assert len(result["implementation_steps"]) == 2
        assert "Task 1" in result["implementation_steps"]
        assert "Task 2" in result["implementation_steps"]

    def test_parse_string_with_bmad_header(self):
        """Test parsing with BMAD header."""
        content = """# <!-- Powered by BMAD™ Core -->

# Test Document

## Requirements
- Req 1
- Req 2
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Test Document"
        assert len(result["requirements"]) == 2

    def test_parse_string_with_numbered_lists(self):
        """Test parsing with numbered lists."""
        content = """# Numbered Lists

## Requirements
1. First requirement
2. Second requirement
3. Third requirement

## Acceptance Criteria
1. First criterion
2. Second criterion
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Numbered Lists"
        assert len(result["requirements"]) == 3
        assert "First requirement" in result["requirements"]
        assert len(result["acceptance_criteria"]) == 2
        assert "First criterion" in result["acceptance_criteria"]

    def test_parse_string_empty_sections(self):
        """Test parsing with empty sections."""
        content = """# Empty Sections

## Requirements

## Acceptance Criteria

## Tasks
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Empty Sections"
        assert result["requirements"] == []
        assert result["acceptance_criteria"] == []
        assert result["implementation_steps"] == []

    def test_parse_string_no_title(self):
        """Test parsing without explicit title."""
        content = """Some random text

## Requirements
- Req 1
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Some random text"
        assert len(result["requirements"]) == 1

    def test_parse_string_fallback_title(self):
        """Test fallback to first non-empty line."""
        content = """

First line

## Requirements
- Req 1
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "First line"

    def test_parse_string_default_title(self):
        """Test default title when no content."""
        content = ""
        result = self.parser.parse_string(content)

        assert result["title"] == "Untitled Document"
        assert result["requirements"] == []
        assert result["acceptance_criteria"] == []
        assert result["implementation_steps"] == []

    def test_parse_string_as_a_i_want_format(self):
        """Test parsing As a... I want... format."""
        content = """# Story Title

As a developer,
I want to implement features,
so that users can benefit.

## Requirements
- Feature 1
- Feature 2

## Acceptance Criteria
- Criteria 1
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Story Title"
        assert len(result["requirements"]) == 2
        assert "Feature 1" in result["requirements"]

    def test_parse_string_with_subtasks(self):
        """Test parsing Tasks/Subtasks sections."""
        content = """# Task Test

## Tasks / Subtasks
- [ ] Task 1
- [ ] Subtask 1.1
- [ ] Subtask 1.2
- [ ] Task 2

## Implementation
- Implementation step 1
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Task Test"
        assert len(result["implementation_steps"]) >= 4
        assert any("Task 1" in step for step in result["implementation_steps"])

    def test_parse_string_mixed_bullets(self):
        """Test parsing mixed bullet styles."""
        content = """# Mixed Bullets

## Requirements
* Star bullet
+ Plus bullet
- Dash bullet
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Mixed Bullets"
        assert len(result["requirements"]) == 3
        assert "Star bullet" in result["requirements"]
        assert "Plus bullet" in result["requirements"]
        assert "Dash bullet" in result["requirements"]

    def test_parse_string_whitespace_handling(self):
        """Test handling of extra whitespace."""
        content = """# Whitespace Test

## Requirements

    - Indented requirement 1

  - Requirement 2

"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Whitespace Test"
        assert len(result["requirements"]) == 1
        assert "Requirement 2" in result["requirements"]

    def test_parse_string_unicode_characters(self):
        """Test parsing with unicode characters."""
        content = """# Unicode Title 测试

## Requirements
- Requirement with émoji 😀
- Chinese: 测试
- Special chars: ©®™

## Acceptance Criteria
- Criteria with ümlaut
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Unicode Title 测试"
        assert len(result["requirements"]) == 3
        assert "测试" in result["requirements"]
        assert "😀" in result["requirements"]

    def test_validate_parsed_document_valid(self):
        """Test validation of valid parsed document."""
        parsed = {
            "title": "Test",
            "requirements": ["Req 1"],
            "acceptance_criteria": ["Crit 1"],
            "implementation_steps": ["Step 1"]
        }

        is_valid, issues = self.parser.validate_parsed_document(parsed)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_parsed_document_invalid_missing_title(self):
        """Test validation with missing title."""
        parsed = {
            "requirements": ["Req 1"],
            "acceptance_criteria": ["Crit 1"],
            "implementation_steps": ["Step 1"]
        }

        is_valid, issues = self.parser.validate_parsed_document(parsed)

        assert is_valid is False
        assert len(issues) == 1
        assert "Missing document title" in issues

    def test_validate_parsed_document_invalid_wrong_types(self):
        """Test validation with wrong types."""
        parsed = {
            "title": "Test",
            "requirements": "not a list",
            "acceptance_criteria": 123,
            "implementation_steps": None
        }

        is_valid, issues = self.parser.validate_parsed_document(parsed)

        assert is_valid is False
        assert len(issues) == 3
        assert any("Requirements is not a list" in issue for issue in issues)
        assert any("Acceptance criteria is not a list" in issue for issue in issues)
        assert any("Implementation steps is not a list" in issue for issue in issues)

    def test_parse_document_file_not_found(self):
        """Test parsing non-existent file raises error."""
        fake_path = Path("/nonexistent/file.md")

        with pytest.raises(FileNotFoundError):
            self.parser.parse_document(fake_path)

    def test_parse_document_with_file(self, tmp_path):
        """Test parsing actual file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""# File Test

## Requirements
- File requirement 1
- File requirement 2

## Acceptance Criteria
- File criterion 1
""", encoding="utf-8")

        result = self.parser.parse_document(test_file)

        assert result["title"] == "File Test"
        assert len(result["requirements"]) == 2
        assert "File requirement 1" in result["requirements"]
        assert len(result["acceptance_criteria"]) == 1
        assert "File criterion 1" in result["acceptance_criteria"]

    def test_parse_document_with_encoding(self, tmp_path):
        """Test parsing file with UTF-8 encoding."""
        test_file = tmp_path / "test_encoding.md"
        test_file.write_text("""# 文件测试

## Requirements
- 需求 1
- 需求 2

## Acceptance Criteria
- 标准 1
""", encoding="utf-8")

        result = self.parser.parse_document(test_file)

        assert result["title"] == "文件测试"
        assert len(result["requirements"]) == 2
        assert "需求 1" in result["requirements"]

    def test_complex_document_structure(self):
        """Test parsing complex real-world document."""
        content = """# <!-- Powered by BMAD™ Core -->

# Story 1.1: Module Foundation and Document Parser Implementation

## Status
**In Progress** (QA Review: CONCERNS)

---

## Story

**As a** developer working on the spec_automation workflow module,
**I want** to create the foundational structure for the spec_automation module and implement the document parser component,
**so that** the module can independently process planning documents without dependency on .bmad-core.

---

## Acceptance Criteria

1. Create `autoBMAD/spec_automation/` directory structure with all required files
2. Implement `doc_parser.py` with the ability to parse Markdown planning documents
3. Extract and structure: document title, requirements list, acceptance criteria, implementation steps
4. Create `spec_state_manager.py` with independent database (spec_progress.db)

---

## Tasks / Subtasks

- [ ] Task 1: Create module directory structure (AC: #1)
  - [ ] Subtask 1.1: Create autoBMAD/spec_automation/ directory
  - [ ] Subtask 1.2: Design directory structure to mirror epic_automation patterns

- [ ] Task 2: Implement document parser core (AC: #2, #3)
  - [ ] Subtask 2.1: Create doc_parser.py with Markdown parsing capability
  - [ ] Subtask 2.2: Implement document title extraction
"""
        result = self.parser.parse_string(content)

        assert result["title"] == "Story 1.1: Module Foundation and Document Parser Implementation"
        assert len(result["acceptance_criteria"]) == 4
        assert "Create `autoBMAD/spec_automation/` directory structure" in result["acceptance_criteria"]
        assert len(result["implementation_steps"]) >= 4
        assert any("Create module directory structure" in step for step in result["implementation_steps"])
