"""
Test Suite for QA Agent Fallback Fix (方案三)
Tests the improved fallback QA review when SDK fails or gates are missing
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import the module to test
from autoBMAD.epic_automation.qa_agent import QAAgent


class TestQAAgentFallbackFix:
    """Test cases for QA agent fallback and降级处理 improvements."""

    @pytest.fixture
    def qa_agent(self):
        """Create QA agent instance."""
        return QAAgent()

    @pytest.fixture
    def mock_story_path(self, tmp_path):
        """Create a mock story file."""
        story_file = tmp_path / "test-story.md"
        story_file.write_text("""
# Test Story

**Status**: In Progress

## Description
Test story description
""")
        return str(story_file)

    @pytest.mark.asyncio
    async def test_fallback_qa_review_when_sdk_fails(self, qa_agent, mock_story_path):
        """Test that fallback QA review is used when SDK execution fails."""
        # Arrange
        with patch.object(qa_agent, '_execute_qa_review', return_value=False) as mock_review:
            # Act
            result = await qa_agent.execute(
                story_content="test content",
                story_path=mock_story_path
            )
            
            # Assert
            assert result['passed'] is False, "Should fail when SDK review fails"
            assert result['needs_fix'] is True, "Should need fix when SDK fails"
            mock_review.assert_called_once_with(mock_story_path)

    @pytest.mark.asyncio
    async def test_fallback_qa_review_when_sdk_cancelled(self, qa_agent, mock_story_path):
        """Test that cancelled SDK execution is handled gracefully."""
        # Arrange
        with patch.object(qa_agent, '_execute_qa_review', side_effect=asyncio.CancelledError()):
            # Act
            result = await qa_agent.execute(
                story_content="test content",
                story_path=mock_story_path
            )
            
            # Assert
            assert result['passed'] is False, "Should fail when SDK cancelled"
            assert result['needs_fix'] is True, "Should need fix when cancelled"
            assert result.get('cancelled') is True, "Should indicate cancellation"

    @pytest.mark.asyncio
    async def test_fallback_qa_review_with_no_gate_files(self, qa_agent, mock_story_path, tmp_path):
        """Test behavior when no QA gate files exist."""
        # Arrange - ensure no gate files exist
        gates_dir = tmp_path / "docs" / "qa" / "gates"
        gates_dir.mkdir(parents=True, exist_ok=True)
        
        with patch.object(qa_agent, '_execute_qa_review', return_value=True):
            with patch.object(qa_agent, '_collect_qa_gate_paths', return_value=[]) as mock_collect:
                # Act
                result = await qa_agent.execute(
                    story_content="test content",
                    story_path=mock_story_path
                )
                
                # Assert
                assert result['passed'] is False, "Should fail when no gates found"
                assert result['needs_fix'] is True, "Should need fix when no gates"
                assert result['gate_paths'] == [], "Should have empty gate paths"
                mock_collect.assert_called_once()

    @pytest.mark.asyncio
    async def test_perform_fallback_qa_review_basic_checks(self, qa_agent, mock_story_path, tmp_path):
        """Test the fallback QA review basic checks functionality."""
        # Arrange
        src_dir = tmp_path / "src"
        src_dir.mkdir(exist_ok=True)
        test_dir = tmp_path / "tests"
        test_dir.mkdir(exist_ok=True)
        
        # Create some basic files for testing
        (src_dir / "main.py").write_text("# Main file")
        (test_dir / "test_main.py").write_text("# Test file")
        
        # Act - call the private fallback method
        result = await qa_agent._perform_fallback_qa_review(mock_story_path)
        
        # Assert
        assert isinstance(result, dict), "Should return dict result"
        assert 'passed' in result, "Should have passed field"
        assert 'needs_fix' in result, "Should have needs_fix field"

    @pytest.mark.asyncio
    async def test_check_code_quality_basics(self, qa_agent, mock_story_path, tmp_path):
        """Test code quality basic checks."""
        # Arrange
        src_dir = tmp_path / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create Python files with different quality levels
        (src_dir / "good_file.py").write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"
""")
        
        (src_dir / "bad_file.py").write_text("""
def hello( name ):
return "Hello"
""")
        
        # Act
        with patch('autoBMAD.epic_automation.qa_agent.Path') as mock_path:
            mock_path.return_value = src_dir
            result = await qa_agent._check_code_quality_basics(mock_story_path)
        
        # Assert
        assert isinstance(result, dict), "Should return dict result"
        assert 'passed' in result, "Should have passed status"

    @pytest.mark.asyncio
    async def test_check_test_files_exist(self, qa_agent, mock_story_path, tmp_path):
        """Test test files existence check."""
        # Arrange
        test_dir = tmp_path / "tests"
        test_dir.mkdir(exist_ok=True)
        
        # Create test files
        (test_dir / "test_module.py").write_text("def test_something(): pass")
        (test_dir / "test_other.py").write_text("def test_other(): pass")
        
        # Act
        with patch('autoBMAD.epic_automation.qa_agent.Path') as mock_path:
            mock_path.return_value = test_dir
            result = await qa_agent._check_test_files_exist(mock_story_path)
        
        # Assert
        assert isinstance(result, dict), "Should return dict result"
        assert result.get('passed', False), "Should pass when test files exist"
        assert 'test_count' in result, "Should include test count"

    @pytest.mark.asyncio
    async def test_check_documentation_updated(self, qa_agent, mock_story_path):
        """Test documentation updated check."""
        # Arrange - story file already has basic content
        
        # Act
        result = await qa_agent._check_documentation_updated(mock_story_path)
        
        # Assert
        assert isinstance(result, dict), "Should return dict result"
        assert 'passed' in result, "Should have passed status"
        assert 'last_updated' in result, "Should include last updated time"

    @pytest.mark.asyncio
    async def test_collect_qa_gate_paths_creates_directory(self, qa_agent, tmp_path):
        """Test that _collect_qa_gate_paths creates directory if it doesn't exist."""
        # Arrange - ensure directory doesn't exist
        gates_dir = tmp_path / "docs" / "qa" / "gates"
        assert not gates_dir.exists(), "Gate directory should not exist initially"
        
        with patch('autoBMAD.epic_automation.qa_agent.Path') as mock_path_class:
            # Mock Path to return our tmp_path based paths
            def mock_path_factory(path_str):
                if path_str == "docs/qa/gates":
                    return gates_dir
                return Path(path_str)
            
            mock_path_class.return_value = gates_dir
            mock_path_class.__truediv__ = lambda self, other: gates_dir / other
            
            # Act
            result = await qa_agent._collect_qa_gate_paths()
            
            # Assert
            assert gates_dir.exists(), "Should create gates directory"
            assert result == [], "Should return empty list for new directory"

    @pytest.mark.asyncio
    async def test_story_status_ready_for_done_detection(self, qa_agent, tmp_path):
        """Test Ready for Done status detection."""
        # Arrange - create story with Ready for Done status
        story_file = tmp_path / "ready-story.md"
        story_file.write_text("""
# Ready Story

**Status**: Ready for Done

## Description
This story is ready
""")
        
        # Act
        result = await qa_agent._check_story_status(str(story_file))
        
        # Assert
        assert result is True, "Should detect Ready for Done status"

    @pytest.mark.asyncio
    async def test_story_status_alternative_format_detection(self, qa_agent, tmp_path):
        """Test alternative Ready for Done status format detection."""
        # Arrange - create story with alternative format
        story_file = tmp_path / "ready-story-alt.md"
        story_file.write_text("""
# Ready Story Alt

## Status
Ready for Done

## Description
This story is ready with alt format
""")
        
        # Act
        result = await qa_agent._check_story_status(str(story_file))
        
        # Assert
        assert result is True, "Should detect alternative Ready for Done format"

    @pytest.mark.asyncio
    async def test_error_handling_in_all_methods(self, qa_agent):
        """Test that all methods handle errors gracefully."""
        # Test with invalid paths
        invalid_path = "/nonexistent/path/story.md"
        
        # Act & Assert - should not raise exceptions
        result1 = await qa_agent._check_story_status(invalid_path)
        assert result1 is False, "Should return False for invalid path"
        
        result2 = await qa_agent._collect_qa_gate_paths()
        assert isinstance(result2, list), "Should return list even on error"
        
        # Test fallback review with invalid input
        result3 = await qa_agent._perform_fallback_qa_review("")
        assert isinstance(result3, dict), "Should return dict even with empty input"


class TestQAAgentIntegration:
    """Integration tests for QA agent fallback mechanisms."""

    @pytest.mark.asyncio
    async def test_complete_fallback_flow(self, tmp_path):
        """Test complete fallback flow from execution to results."""
        # Arrange
        agent = QAAgent()
        
        # Create minimal test environment
        story_file = tmp_path / "test-story.md"
        story_file.write_text("""
# Integration Test Story

**Status**: In Progress

## Acceptance Criteria
- [ ] Basic functionality works
- [ ] Tests pass
- [ ] Documentation updated
""")
        
        # Mock SDK to fail
        with patch.object(agent, '_execute_qa_review', return_value=False):
            # Act
            result = await agent.execute(
                story_content=story_file.read_text(),
                story_path=str(story_file)
            )
            
            # Assert
            assert result['passed'] is False, "Should fail when SDK fails"
            assert result['needs_fix'] is True, "Should require fix"
            assert 'dev_prompt' in result, "Should include dev prompt"

    @pytest.mark.asyncio
    async def test_performance_of_fallback_methods(self, tmp_path):
        """Test that fallback methods perform efficiently."""
        # Arrange
        import time
        
        # Create test environment with many files
        src_dir = tmp_path / "src"
        src_dir.mkdir(exist_ok=True)
        test_dir = tmp_path / "tests"
        test_dir.mkdir(exist_ok=True)
        
        # Create multiple files
        for i in range(10):
            (src_dir / f"module_{i}.py").write_text(f"def func_{i}(): pass")
            (test_dir / f"test_module_{i}.py").write_text(f"def test_func_{i}(): pass")
        
        story_file = tmp_path / "perf-story.md"
        story_file.write_text("# Performance Test Story\n\n**Status**: In Progress")
        
        # Act - measure performance
        start_time = time.time()
        agent = QAAgent()
        result = await agent._perform_fallback_qa_review(str(story_file))
        end_time = time.time()
        
        # Assert
        assert end_time - start_time < 5.0, "Fallback review should be fast"
        assert isinstance(result, dict), "Should return valid result"
        assert 'passed' in result, "Should have passed status"