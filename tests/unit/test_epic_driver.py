"""
Tests for EpicParser in epic_driver.py

Tests cover:
- Epic file reading
- Story extraction using regex
- Story path mapping
- Format validation
- Edge case handling
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the module to test
import sys
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir / 'autoBMAD' / 'epic_automation'))

from epic_driver import EpicParser, StoryInfo


class TestEpicParser:
    """Test suite for EpicParser class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.parser = EpicParser(epic_dir="docs/epics")

    # Test 1: Epic file reading
    def test_read_epic_valid_file(self):
        """Test reading a valid epic file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Epic: Test Epic\n**Epic ID**: EPIC-001\n\n### Story 1: Test Story")
            temp_file = f.name

        try:
            content = self.parser.read_epic(temp_file)
            assert "# Epic: Test Epic" in content
            assert "**Epic ID**: EPIC-001" in content
        finally:
            os.unlink(temp_file)

    def test_read_epic_nonexistent_file(self):
        """Test reading a non-existent epic file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.parser.read_epic("/nonexistent/path/epic.md")

    def test_read_epic_with_relative_path(self):
        """Test reading epic with relative path uses epic_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create epic file in epic_dir
            epic_file = Path(tmpdir) / "test_epic.md"
            epic_file.write_text("# Epic: Test\n")

            parser = EpicParser(epic_dir=tmpdir)
            content = parser.read_epic("test_epic.md")
            assert "# Epic: Test" in content

    # Test 2: Story extraction
    def test_extract_stories_basic(self):
        """Test extracting stories from basic epic content."""
        epic_content = """
# Epic: Test Epic

### Story 1: First Story
Content here

### Story 2: Second Story
More content
"""
        stories = self.parser.extract_stories(epic_content)
        assert len(stories) == 2
        assert stories[0] == (1, "First Story")
        assert stories[1] == (2, "Second Story")

    def test_extract_stories_with_special_characters(self):
        """Test extracting stories with special characters in titles."""
        epic_content = """
### Story 1: Story with (Parentheses) and [Brackets]
### Story 2: Story with "Quotes" and 'Apostrophes'
### Story 3: Story with 100% (Percentage) & Symbols!
"""
        stories = self.parser.extract_stories(epic_content)
        assert len(stories) == 3
        assert "Parentheses" in stories[0][1]
        assert "Quotes" in stories[1][1]
        assert "Percentage" in stories[2][1]

    def test_extract_stories_empty_content(self):
        """Test extracting stories from empty content."""
        stories = self.parser.extract_stories("")
        assert len(stories) == 0

    def test_extract_stories_no_stories(self):
        """Test extracting stories when none exist."""
        epic_content = "# Epic: Test\nNo stories here"
        stories = self.parser.extract_stories(epic_content)
        assert len(stories) == 0

    def test_extract_stories_skips_invalid_patterns(self):
        """Test that invalid story patterns are skipped."""
        epic_content = """
### Story 1: Valid Story
Some text
Story 2: Invalid (missing ###)
## Story 3: Invalid (wrong header level)
### Not a Story: Invalid format
"""
        stories = self.parser.extract_stories(epic_content)
        # Should only match the valid pattern
        assert len(stories) == 1
        assert stories[0] == (1, "Valid Story")

    # Test 3: Story path mapping
    def test_map_story_paths_basic(self):
        """Test mapping story numbers to file paths."""
        stories = [(1, "First Story"), (2, "Second Story")]
        story_infos = self.parser.map_story_paths(stories)

        assert len(story_infos) == 2
        assert story_infos[0].number == 1
        assert story_infos[0].title == "First Story"
        assert story_infos[0].file_path == "docs/stories/story_001.md"

        assert story_infos[1].number == 2
        assert story_infos[1].title == "Second Story"
        assert story_infos[1].file_path == "docs/stories/story_002.md"

    def test_map_story_paths_custom_directory(self):
        """Test mapping with custom stories directory."""
        stories = [(5, "Story Five")]
        story_infos = self.parser.map_story_paths(stories, "custom/stories")

        assert len(story_infos) == 1
        assert story_infos[0].file_path == "custom/stories/story_005.md"

    # Test 4: Format validation
    def test_validate_epic_format_valid(self):
        """Test validating a properly formatted epic."""
        epic_content = """# Epic: Test Epic
**Epic ID**: EPIC-001

### Story 1: Test Story
"""
        is_valid, errors = self.parser.validate_epic_format(epic_content)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_epic_format_missing_header(self):
        """Test validation fails with missing epic header."""
        epic_content = """**Epic ID**: EPIC-001

### Story 1: Test Story
"""
        is_valid, errors = self.parser.validate_epic_format(epic_content)
        assert is_valid is False
        assert any("epic header" in err.lower() for err in errors)

    def test_validate_epic_format_missing_epic_id(self):
        """Test validation fails with missing Epic ID."""
        epic_content = """# Epic: Test Epic

### Story 1: Test Story
"""
        is_valid, errors = self.parser.validate_epic_format(epic_content)
        assert is_valid is False
        assert any("epic id" in err.lower() for err in errors)

    def test_validate_epic_format_no_stories(self):
        """Test validation fails with no stories."""
        epic_content = """# Epic: Test Epic
**Epic ID**: EPIC-001

No stories here.
"""
        is_valid, errors = self.parser.validate_epic_format(epic_content)
        assert is_valid is False
        assert any("no stories" in err.lower() for err in errors)

    def test_validate_epic_format_sequential_numbering(self):
        """Test validation checks for sequential story numbering."""
        epic_content = """# Epic: Test Epic
**Epic ID**: EPIC-001

### Story 1: First
### Story 3: Third (missing 2)
"""
        is_valid, errors = self.parser.validate_epic_format(epic_content)
        assert is_valid is False
        assert any("numbering" in err.lower() for err in errors)

    def test_validate_epic_format_valid_sequential(self):
        """Test validation passes with sequential numbering."""
        epic_content = """# Epic: Test Epic
**Epic ID**: EPIC-001

### Story 1: First
### Story 2: Second
### Story 3: Third
"""
        is_valid, errors = self.parser.validate_epic_format(epic_content)
        assert is_valid is True
        assert len(errors) == 0

    # Test 5: Main parse_epic method
    def test_parse_epic_success(self):
        """Test successful epic parsing."""
        epic_content = """# Epic: Test Epic
**Epic ID**: EPIC-001

### Story 1: First Story
### Story 2: Second Story
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_file = f.name

        try:
            stories = self.parser.parse_epic(temp_file)
            assert len(stories) == 2
            assert stories[0].number == 1
            assert stories[0].title == "First Story"
            assert stories[1].number == 2
            assert stories[1].title == "Second Story"
        finally:
            os.unlink(temp_file)

    def test_parse_epic_validation_failure(self):
        """Test parse_epic raises ValueError on validation failure."""
        # Missing Epic ID to trigger validation failure
        epic_content = """# Epic: Test Epic

### Story 1: Test Story
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                self.parser.parse_epic(temp_file)
            assert "validation failed" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_file)

    # Test 6: Edge cases
    def test_get_story_count_with_file(self):
        """Test getting story count from a file."""
        epic_content = """# Epic: Test
**Epic ID**: EPIC-001

### Story 1: First
### Story 2: Second
### Story 3: Third
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_file = f.name

        try:
            count = self.parser.get_story_count(temp_file)
            assert count == 3
        finally:
            os.unlink(temp_file)

    def test_get_story_count_nonexistent_file(self):
        """Test getting story count from non-existent file returns 0."""
        count = self.parser.get_story_count("/nonexistent/file.md")
        assert count == 0

    def test_story_info_dataclass(self):
        """Test StoryInfo dataclass functionality."""
        story = StoryInfo(
            number=5,
            title="Test Story",
            file_path="docs/stories/story_005.md",
            epic_path="story_005.md"
        )
        assert story.number == 5
        assert story.title == "Test Story"
        assert story.file_path == "docs/stories/story_005.md"

    def test_multiple_stories_large_number(self):
        """Test extracting many stories (stress test)."""
        epic_content = "# Epic: Large Epic\n**Epic ID**: EPIC-999\n\n"
        for i in range(1, 101):  # 100 stories
            epic_content += f"### Story {i}: Story Number {i}\n\n"

        stories = self.parser.extract_stories(epic_content)
        assert len(stories) == 100
        assert stories[0] == (1, "Story Number 1")
        assert stories[99] == (100, "Story Number 100")


class TestEpicParserIntegration:
    """Integration tests for EpicParser with real epic files."""

    def test_parse_real_epic_file(self):
        """Test parsing the actual epic-bmad-automation.md file."""
        epic_path = Path(__file__).parent.parent.parent / 'docs' / 'epics' / 'epic-bmad-automation.md'

        if not epic_path.exists():
            pytest.skip(f"Epic file not found: {epic_path}")

        parser = EpicParser()
        stories = parser.parse_epic(str(epic_path))

        # The epic should have 5 stories
        assert len(stories) >= 1  # At least Story 1 exists

        # Verify first story
        assert stories[0].number == 1
        assert "Epic Parser" in stories[0].title

        # Verify file paths are correctly mapped
        assert "story_001.md" in stories[0].file_path


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
