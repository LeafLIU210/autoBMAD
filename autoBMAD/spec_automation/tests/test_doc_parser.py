"""
Comprehensive tests for DocumentParser.

This test suite validates:
- Document parsing for various document types
- Extraction of structured data
- Error handling
- Edge cases
"""

import pytest

from spec_automation.doc_parser import DocumentParser


class TestDocumentParser:
    """Test suite for DocumentParser."""

    def test_init(self):
        """Test DocumentParser initialization."""
        parser = DocumentParser()
        assert parser is not None

    def test_parse_string_simple(self):
        """Test parsing a simple document string."""
        content = """# Test Document

## Requirements

1. First requirement
2. Second requirement

## Acceptance Criteria

1. First criterion
2. Second criterion

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        assert "title" in result
        assert "requirements" in result
        assert "acceptance_criteria" in result

    def test_parse_string_with_tasks(self):
        """Test parsing document with tasks/subtasks."""
        content = """# Feature Implementation

## Tasks

- [ ] Task 1
- [ ] Task 2
  - [ ] Subtask 2.1
  - [ ] Subtask 2.2

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        assert "tasks" in result
        assert len(result["tasks"]) > 0

    def test_parse_string_empty_sections(self):
        """Test parsing document with empty sections."""
        content = """# Empty Document

## Requirements

## Acceptance Criteria

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        assert result["requirements"] == []
        assert result["acceptance_criteria"] == []

    def test_parse_string_complex(self):
        """Test parsing a complex document with various sections."""
        content = """# Complex Document

## Status
**In Progress**

## Overview
This is a complex document with multiple sections.

## Requirements

### Functional Requirements

1. User authentication
2. Data validation
3. Error handling

### Non-Functional Requirements

1. Performance: <100ms response time
2. Scalability: Support 1000 concurrent users

## Acceptance Criteria

1. [ ] Users can log in
2. [ ] Data is validated before saving
3. [ ] Errors are logged appropriately

## Implementation Plan

### Phase 1
- [ ] Set up authentication
- [ ] Create user interface

### Phase 2
- [ ] Implement validation
- [ ] Add error handling

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        assert result["title"] == "Complex Document"
        assert len(result["requirements"]) > 0
        assert len(result["acceptance_criteria"]) > 0

    def test_parse_string_special_characters(self):
        """Test parsing document with special characters."""
        content = """# Special Characters: @#$%^&*()

## Requirements

1. Requirement with special chars: !@#$%^&*()
2. Requirement with unicode: 测试 ✓

## Acceptance Criteria

1. First criterion with "quotes"
2. Second criterion with 'apostrophes'

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        assert len(result["requirements"]) == 2
        assert len(result["acceptance_criteria"]) == 2

    def test_parse_string_no_sections(self):
        """Test parsing document without standard sections."""
        content = """# Just a Title

This is just some text without standard sections.
No requirements or acceptance criteria here.

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        # Should still return a valid structure
        assert "title" in result
        assert "requirements" in result
        assert "acceptance_criteria" in result
        assert isinstance(result["requirements"], list)
        assert isinstance(result["acceptance_criteria"], list)

    def test_parse_document_file_exists(self, tmp_path):
        """Test parsing a document file that exists."""
        content = """# File Test

## Requirements

1. File requirement

"""
        file_path = tmp_path / "test.md"
        file_path.write_text(content)

        parser = DocumentParser()
        result = parser.parse_document(file_path)

        assert result["title"] == "File Test"
        assert len(result["requirements"]) == 1

    def test_parse_document_file_not_found(self, tmp_path):
        """Test parsing a document file that doesn't exist."""
        file_path = tmp_path / "nonexistent.md"

        parser = DocumentParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_document(file_path)

    def test_parse_string_multiline_requirements(self):
        """Test parsing requirements that span multiple lines."""
        content = """# Multiline Test

## Requirements

1. This is a requirement that spans
   multiple lines and should be
   captured as a single requirement

2. Second requirement

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        # Should capture the multiline requirement
        assert len(result["requirements"]) >= 1

    def test_parse_string_nested_lists(self):
        """Test parsing with nested lists."""
        content = """# Nested Lists

## Requirements

1. First requirement
   - Nested item 1
   - Nested item 2
2. Second requirement

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        assert len(result["requirements"]) >= 1

    def test_extract_title_from_bmad_header(self):
        """Test extracting title from BMAD-style header."""
        content = """# <!-- Powered by BMAD™ Core -->

# Story: Test Story

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        # Should extract the actual story title, not the BMAD header
        assert "Story" in result["title"]

    def test_acceptance_criteria_with_checkboxes(self):
        """Test parsing acceptance criteria with checkboxes."""
        content = """# Checkbox Test

## Acceptance Criteria

- [ ] First checkbox
- [x] Completed checkbox
- [ ] Another checkbox

"""
        parser = DocumentParser()
        result = parser.parse_string(content)

        # Should capture checkbox items as acceptance criteria
        assert len(result["acceptance_criteria"]) >= 3
