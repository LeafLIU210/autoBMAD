"""
Unit tests for EpicParser functionality.

Tests cover:
- Epic document parsing
- Story extraction using regex pattern matching
- Story-to-file-path mapping
- Format validation
- Edge case handling (empty files, malformed content, etc.)
"""

import pytest
import tempfile
import os
from pathlib import Path

from autoBMAD.epic_automation.epic_driver import EpicParser


class TestEpicParser:
    """Test suite for EpicParser class."""

    def test_init_default(self):
        """Test initialization with default epic directory."""
        parser = EpicParser()
        assert parser.epic_dir == Path("docs/epics")

    def test_init_custom_epic_dir(self):
        """Test initialization with custom epic directory."""
        parser = EpicParser("custom/epics")
        assert parser.epic_dir == Path("custom/epics")

    def test_read_epic_success(self):
        """Test successful reading of an epic file."""
        epic_content = "# Test Epic\n\n### Story 1: Test Story\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_path = f.name

        try:
            parser = EpicParser()
            content = parser.read_epic(temp_path)
            assert content == epic_content
        finally:
            os.unlink(temp_path)

    def test_read_epic_file_not_found(self):
        """Test reading a non-existent epic file raises FileNotFoundError."""
        parser = EpicParser()
        with pytest.raises(FileNotFoundError):
            parser.read_epic("/nonexistent/path/epic.md")

    def test_read_epic_io_error(self):
        """Test handling of IO errors when reading epic."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name

        try:
            # Remove the file to cause IO error
            os.unlink(temp_path)

            parser = EpicParser()
            with pytest.raises(IOError):
                parser.read_epic(temp_path)
        except Exception:
            pass

    def test_extract_stories_single_story(self):
        """Test extraction of a single story."""
        epic_content = """# Test Epic

### Story 1: Calculate Button Implementation

**As a** user,
**I want to** click a calculate button,
**So that** I can perform calculations.

---

### Story 2: Input Validation

**As a** user,
**I want to** validate inputs,
**So that** I can prevent errors.
"""

        parser = EpicParser()
        stories = parser.extract_stories(epic_content)

        assert len(stories) == 2
        assert stories[0] == (1, 'Calculate Button Implementation')
        assert stories[1] == (2, 'Input Validation')

    def test_extract_stories_multiple_stories(self):
        """Test extraction of multiple stories."""
        epic_content = """# Epic: Test

### Story 1: First Story
### Story 2: Second Story
### Story 3: Third Story
"""

        parser = EpicParser()
        stories = parser.extract_stories(epic_content)

        assert len(stories) == 3
        for i, (story_num, title) in enumerate(stories, 1):
            assert story_num == i
            expected_title = ['First', 'Second', 'Third'][i-1]
            assert title == f"{expected_title} Story"

    def test_extract_stories_no_matches(self):
        """Test extraction returns empty list when no story headers found."""
        epic_content = "# Test Epic\n\nNo stories here.\n"

        parser = EpicParser()
        stories = parser.extract_stories(epic_content)

        assert stories == []

    def test_validate_epic_format_valid(self):
        """Test validation of a properly formatted epic."""
        epic_content = """# Epic: Test Epic

**Epic ID**: EPIC-001

### Story 1: Test Story
"""

        parser = EpicParser()
        is_valid, errors = parser.validate_epic_format(epic_content)

        assert is_valid is True
        assert errors == []

    def test_validate_epic_format_missing_header(self):
        """Test validation fails when epic header is missing."""
        epic_content = "### Story 1: Test Story\n"

        parser = EpicParser()
        is_valid, errors = parser.validate_epic_format(epic_content)

        assert is_valid is False
        assert any("Missing or invalid epic header" in error for error in errors)

    def test_validate_epic_format_missing_epic_id(self):
        """Test validation fails when Epic ID is missing."""
        epic_content = """# Epic: Test

### Story 1: Test Story
"""

        parser = EpicParser()
        is_valid, errors = parser.validate_epic_format(epic_content)

        assert is_valid is False
        assert any("Missing or invalid Epic ID" in error for error in errors)

    def test_validate_epic_format_no_stories(self):
        """Test validation fails when no stories found."""
        epic_content = """# Epic: Test

**Epic ID**: EPIC-001

Just some content without stories.
"""

        parser = EpicParser()
        is_valid, errors = parser.validate_epic_format(epic_content)

        assert is_valid is False
        assert any("No stories found" in error for error in errors)

    def test_validate_epic_format_duplicate_story_numbers(self):
        """Test validation fails when duplicate story numbers exist."""
        epic_content = """# Epic: Test

**Epic ID**: EPIC-001

### Story 1: First Story
### Story 1: Duplicate Story
"""

        parser = EpicParser()
        is_valid, errors = parser.validate_epic_format(epic_content)

        assert is_valid is False
        assert any("not sequential" in error for error in errors)

    def test_map_story_paths(self):
        """Test mapping of story numbers to file paths."""
        stories = [(1, 'First Story'), (2, 'Second Story'), (5, 'Fifth Story')]

        parser = EpicParser()
        story_infos = parser.map_story_paths(stories, "docs/stories")

        assert len(story_infos) == 3

        # Check that the stories are mapped correctly
        assert story_infos[0].number == 1
        assert story_infos[0].title == 'First Story'
        assert 'story_001.md' in story_infos[0].file_path

        assert story_infos[1].number == 2
        assert story_infos[1].title == 'Second Story'
        assert 'story_002.md' in story_infos[1].file_path

        assert story_infos[2].number == 5
        assert story_infos[2].title == 'Fifth Story'
        assert 'story_005.md' in story_infos[2].file_path

    def test_parse_epic_success(self):
        """Test the main parse_epic method with valid epic."""
        epic_content = """# Epic: Test

**Epic ID**: EPIC-001

### Story 1: Test Story 1
### Story 2: Test Story 2
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_path = f.name

        try:
            parser = EpicParser()
            stories = parser.parse_epic(temp_path, "docs/stories")

            assert len(stories) == 2
            assert stories[0].number == 1
            assert stories[0].title == 'Test Story 1'
            assert stories[1].number == 2
            assert stories[1].title == 'Test Story 2'
        finally:
            os.unlink(temp_path)

    def test_parse_epic_invalid_format(self):
        """Test parse_epic raises ValueError for invalid format."""
        epic_content = "Invalid epic without proper format"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_path = f.name

        try:
            parser = EpicParser()
            with pytest.raises(ValueError):
                parser.parse_epic(temp_path)
        finally:
            os.unlink(temp_path)

    def test_parse_epic_file_not_found(self):
        """Test parse_epic raises FileNotFoundError for non-existent file."""
        parser = EpicParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_epic("/nonexistent/epic.md")

    def test_get_story_count(self):
        """Test getting story count from epic."""
        epic_content = """# Epic: Test

**Epic ID**: EPIC-001

### Story 1: First Story
### Story 2: Second Story
### Story 3: Third Story
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_path = f.name

        try:
            parser = EpicParser()
            count = parser.get_story_count(temp_path)
            assert count == 3
        finally:
            os.unlink(temp_path)

    def test_get_story_count_file_not_found(self):
        """Test get_story_count returns 0 for non-existent file."""
        parser = EpicParser()
        count = parser.get_story_count("/nonexistent/epic.md")
        assert count == 0

    def test_edge_case_story_with_special_characters(self):
        """Test story extraction with special characters in title."""
        epic_content = """# Epic: Test

**Epic ID**: EPIC-001

### Story 1: Test (with parentheses) & symbols!
### Story 2: Story with "quotes" and 'apostrophes'
"""

        parser = EpicParser()
        stories = parser.extract_stories(epic_content)

        assert len(stories) == 2
        assert stories[0][1] == 'Test (with parentheses) & symbols!'
        assert stories[1][1] == 'Story with "quotes" and \'apostrophes\''

    def test_regex_pattern_matches_format(self):
        """Test that the regex pattern correctly matches the expected format."""
        test_cases = [
            ("### Story 1: Title", True, "1", "Title"),
            ("### Story 42: Long Title Here", True, "42", "Long Title Here"),
            ("## Story 1: Different Format", False, None, None),  # Only 2 hashes
            ("### Story 5: Another Title", True, "5", "Another Title"),
        ]

        parser = EpicParser()
        for test_string, should_match, expected_id, expected_title in test_cases:
            if should_match:
                match = parser.story_pattern.search(test_string)
                assert match is not None
                assert match.group(1) == expected_id
                assert match.group(2) == expected_title
            else:
                match = parser.story_pattern.search(test_string)
                assert match is None


class TestEpicParserIntegration:
    """Integration tests for EpicParser with real epic files."""

    def test_parse_example_epic(self):
        """Test parsing the actual example epic file."""
        example_epic_path = Path(__file__).parent.parent.parent / "test-docs" / "epics" / "example-epic.md"

        if not example_epic_path.exists():
            pytest.skip(f"Example epic file not found at {example_epic_path}")

        parser = EpicParser()
        stories = parser.parse_epic(str(example_epic_path), "docs/stories")

        # Example epic has 3 stories
        assert len(stories) == 3
        assert stories[0].number == 1
        assert stories[0].title == 'Calculate Button Implementation'
        assert stories[1].number == 2
        assert stories[1].title == 'Input Field Validation'
        assert stories[2].number == 3
        assert stories[2].title == 'Result Display Enhancement'

    def test_parse_main_epic(self):
        """Test parsing the main epic-bmad-automation.md file."""
        epic_path = Path(__file__).parent.parent.parent / "docs" / "epics" / "epic-bmad-automation.md"

        if not epic_path.exists():
            pytest.skip(f"Epic file not found at {epic_path}")

        parser = EpicParser()
        stories = parser.parse_epic(str(epic_path), "docs/stories")

        # Main epic should have 5 stories
        assert len(stories) == 5
        assert stories[0].number == 1
        assert stories[0].title == 'Epic Parser Implementation'
        assert stories[1].number == 2
        assert stories[1].title == 'BMAD Native Driver Core'
        assert stories[2].number == 3
        assert stories[2].title == 'QA Tools Integration'
        assert stories[3].number == 4
        assert stories[3].title == 'Progress Monitoring & State Management'
        assert stories[4].number == 5
        assert stories[4].title == 'CLI Interface & Documentation'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
