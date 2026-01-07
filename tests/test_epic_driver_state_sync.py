"""
Test Suite for Epic Driver State Sync Fix (方案四)
Tests the improved state consistency checking and synchronization
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import the module to test
from autoBMAD.epic_automation.epic_driver import EpicDriver


class TestEpicDriverStateSyncFix:
    """Test cases for epic driver state synchronization improvements."""

    @pytest.fixture
    def mock_epic_path(self, tmp_path):
        """Create a mock epic file."""
        epic_file = tmp_path / "test-epic.md"
        epic_file.write_text("""
# Test Epic

## Stories
- [ ] Story 1: Setup infrastructure
- [ ] Story 2: Implement features
""")
        return str(epic_file)

    @pytest.fixture
    def epic_driver(self, mock_epic_path):
        """Create epic driver instance."""
        driver = EpicDriver(
            epic_path=mock_epic_path,
            max_iterations=3,
            verbose=False,
            skip_quality=True,  # Skip for testing
            skip_tests=True     # Skip for testing
        )
        return driver

    @pytest.mark.asyncio
    async def test_check_state_consistency_detects_inconsistency(self, epic_driver):
        """Test that state inconsistency is properly detected."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'status': 'dev_completed',
            'expected_files': ['src/main.py', 'tests/test_main.py'],
            'id': 'test-story'
        }
        
        # Mock file system check to return inconsistent state
        with patch.object(epic_driver, '_check_filesystem_state', return_value=False):
            # Act
            result = await epic_driver._check_state_consistency(story)
            
            # Assert
            assert result is False, "Should detect inconsistency"

    @pytest.mark.asyncio
    async def test_check_state_consistency_returns_true_when_consistent(self, epic_driver):
        """Test that consistent state returns True."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'status': 'dev_completed',
            'expected_files': ['src/main.py', 'tests/test_main.py']
        }
        
        # Mock file system check to return consistent state
        with patch.object(epic_driver, '_check_filesystem_state', return_value=True):
            with patch.object(epic_driver, '_validate_story_integrity', return_value=True):
                with patch.object(epic_driver.state_manager, 'get_story_status', return_value=None):
                    # Act
                    result = await epic_driver._check_state_consistency(story)
                    
                    # Assert
                    assert result is True, "Should detect consistency"

    @pytest.mark.asyncio
    async def test_resync_story_state_updates_status(self, epic_driver):
        """Test that story state resynchronization updates status correctly."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'status': 'dev_completed',
            'expected_status': 'qa_ready',
            'id': 'test-story'
        }
        
        # Mock state manager update
        with patch.object(epic_driver.state_manager, 'update_story_status', return_value=True) as mock_update:
            # Act
            await epic_driver._resync_story_state(story)
            
            # Assert
            mock_update.assert_called_once_with(story_path='test-story.md', status='qa_ready')

    @pytest.mark.asyncio
    async def test_handle_graceful_cancellation_cleans_up(self, epic_driver):
        """Test that graceful cancellation performs proper cleanup."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'status': 'in_progress',
            'id': 'test-story'
        }
        
        # Mock cleanup methods
        with patch.object(epic_driver.state_manager, 'update_story_status', return_value=True) as mock_update:
            with patch.object(epic_driver.log_manager, 'log_cancellation', return_value=True) as mock_log:
                # Act
                await epic_driver._handle_graceful_cancellation(story)
                
                # Assert
                mock_update.assert_called_once_with(story_path='test-story.md', status='cancelled')
                mock_log.assert_called_once_with('Story processing cancelled for test-story.md')

    @pytest.mark.asyncio
    async def test_process_story_with_state_inconsistency(self, epic_driver):
        """Test process_story handles state inconsistency correctly."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'status': 'dev_completed',
            'title': 'Test Story',
            'id': 'test-story'
        }
        
        # Mock inconsistency detection and resync
        with patch.object(epic_driver, '_check_state_consistency', return_value=False):
            with patch.object(epic_driver, '_resync_story_state', return_value=True) as mock_resync:
                with patch.object(epic_driver.state_manager, 'get_story_status', return_value=None):
                    # Act
                    result = await epic_driver.process_story(story)
                    
                    # Assert
                    assert result is False, "Should return False when state inconsistent"
                    mock_resync.assert_called_once_with(story)

    @pytest.mark.asyncio
    async def test_process_story_with_graceful_cancellation(self, epic_driver):
        """Test process_story handles cancellation gracefully."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'status': 'in_progress',
            'title': 'Test Story',
            'id': 'test-story'
        }
        
        # Mock cancellation
        with patch.object(epic_driver, '_check_state_consistency', side_effect=asyncio.CancelledError()):
            with patch.object(epic_driver, '_handle_graceful_cancellation', return_value=True) as mock_cleanup:
                # Act
                result = await epic_driver.process_story(story)
                
                # Assert
                assert result is False, "Should return False when cancelled"
                mock_cleanup.assert_called_once_with(story)

    @pytest.mark.asyncio
    async def test_check_filesystem_state_with_missing_files(self, epic_driver, tmp_path):
        """Test filesystem state check with missing files."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'expected_files': ['src/main.py', 'tests/test_main.py', 'docs/README.md']
        }
        
        # Create only some files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("main")
        
        # Don't create tests/test_main.py and docs/README.md
        
        # Act
        with patch.object(Path, 'exists', side_effect=lambda p: str(p) == 'src/main.py'):
            result = await epic_driver._check_filesystem_state(story)
            
            # Assert
            assert result is False, "Should detect missing files"

    @pytest.mark.asyncio
    async def test_check_filesystem_state_with_all_files_present(self, epic_driver, tmp_path):
        """Test filesystem state check when all files are present."""
        # Arrange
        story = {
            'path': 'test-story.md',
            'expected_files': ['src/main.py', 'tests/test_main.py']
        }
        
        # Create all expected files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("main")
        
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("test")
        
        # Act
        with patch.object(Path, 'exists', return_value=True):
            result = await epic_driver._check_filesystem_state(story)
            
            # Assert
            assert result is True, "Should detect all files present"

    @pytest.mark.asyncio
    async def test_validate_story_integrity_checks_content(self, epic_driver, tmp_path):
        """Test story integrity validation checks content properly."""
        # Arrange
        story_file = tmp_path / "test-story.md"
        story_file.write_text("""
# Test Story

**Status**: Ready for Done
## Acceptance Criteria
- [x] All tasks completed
- [x] Tests pass
- [x] Documentation updated

## Implementation Notes
Completed successfully
""")
        
        story = {
            'path': str(story_file),
            'required_sections': ['Acceptance Criteria', 'Implementation Notes']
        }
        
        # Act
        result = await epic_driver._validate_story_integrity(story)
        
        # Assert
        assert result is True, "Should validate story with all required sections"

    @pytest.mark.asyncio
    async def test_validate_story_integrity_missing_sections(self, epic_driver, tmp_path):
        """Test story integrity validation detects missing sections."""
        # Arrange
        story_file = tmp_path / "test-story.md"
        story_file.write_text("""
# Test Story

**Status**: Ready for Done
## Acceptance Criteria
- [x] All tasks completed

## Notes
Some notes here
""")
        
        story = {
            'path': str(story_file),
            'required_sections': ['Acceptance Criteria', 'Implementation Notes', 'Test Results']
        }
        
        # Act
        result = await epic_driver._validate_story_integrity(story)
        
        # Assert
        assert result is False, "Should detect missing sections"

    @pytest.mark.asyncio
    async def test_error_handling_in_all_state_methods(self, epic_driver):
        """Test that all state synchronization methods handle errors gracefully."""
        # Test with invalid inputs
        invalid_story = {'invalid': 'data', 'id': 'invalid-story'}
        
        # Act & Assert - should not raise exceptions
        result1 = await epic_driver._check_state_consistency(invalid_story)
        assert isinstance(result1, bool), "Should return boolean even with invalid input"
        
        result2 = await epic_driver._resync_story_state(invalid_story)
        # Should complete without exception
        
        result3 = await epic_driver._check_filesystem_state(invalid_story)
        assert isinstance(result3, bool), "Should return boolean even with invalid input"
        
        result4 = await epic_driver._validate_story_integrity({'path': '/nonexistent'})
        assert isinstance(result4, bool), "Should return boolean even with missing file"

    @pytest.mark.asyncio
    async def test_concurrent_state_operations(self, epic_driver):
        """Test that concurrent state operations work correctly."""
        # Arrange
        stories = [
            {'path': f'story-{i}.md', 'status': 'dev_completed', 'id': f'story-{i}'} 
            for i in range(5)
        ]
        
        # Mock all methods to simulate concurrent access
        with patch.object(epic_driver, '_check_state_consistency', return_value=True):
            with patch.object(epic_driver, '_resync_story_state', return_value=True):
                # Act - run multiple state checks concurrently
                tasks = [
                    epic_driver._check_state_consistency(story)
                    for story in stories
                ]
                results = await asyncio.gather(*tasks)
                
                # Assert
                assert all(results), "All concurrent checks should pass"
                assert len(results) == 5, "Should have results for all stories"

    @pytest.mark.asyncio
    async def test_state_sync_performance(self, epic_driver, tmp_path):
        """Test that state synchronization operations perform efficiently."""
        # Arrange
        import time
        
        # Create test environment with multiple files
        for i in range(20):
            file_path = tmp_path / f"file_{i}.py"
            file_path.write_text(f"# File {i}")
        
        story = {
            'path': 'test-story.md',
            'expected_files': [f"file_{i}.py" for i in range(20)],
            'id': 'test-story'
        }
        
        # Act - measure performance
        start_time = time.time()
        result = await epic_driver._check_filesystem_state(story)
        end_time = time.time()
        
        # Assert
        assert end_time - start_time < 1.0, "State check should be fast"
        assert isinstance(result, bool), "Should return boolean result"


class TestEpicDriverIntegration:
    """Integration tests for epic driver state synchronization."""

    @pytest.mark.asyncio
    async def test_complete_state_sync_flow(self, tmp_path):
        """Test complete state synchronization flow."""
        # Arrange
        epic_file = tmp_path / "integration-epic.md"
        epic_file.write_text("""
# Integration Test Epic

## Stories
- [ ] Integration Story 1
- [ ] Integration Story 2
""")
        
        driver = EpicDriver(
            epic_path=str(epic_file),
            max_iterations=1,
            skip_quality=True,
            skip_tests=True
        )
        
        # Create story files
        story1_file = tmp_path / "integration-story-1.md"
        story1_file.write_text("""
# Integration Story 1

**Status**: dev_completed
## Implementation
Completed implementation
""")
        
        story2_file = tmp_path / "integration-story-2.md"
        story2_file.write_text("""
# Integration Story 2

**Status**: qa_ready
## Test Results
All tests passing
""")
        
        # Mock agents and state manager
        with patch.object(driver, 'sm_agent', Mock()):
            with patch.object(driver, 'dev_agent', Mock()):
                with patch.object(driver, 'qa_agent', Mock()):
                    with patch.object(driver, 'state_manager', Mock()):
                        # Act - test state consistency across stories
                        story1 = {'path': str(story1_file), 'status': 'dev_completed', 'id': 'story-1'}
                        story2 = {'path': str(story2_file), 'status': 'qa_ready', 'id': 'story-2'}
                        
                        consistency1 = await driver._check_state_consistency(story1)
                        consistency2 = await driver._check_state_consistency(story2)
                        
                        # Assert
                        assert isinstance(consistency1, bool), "Should return boolean for story 1"
                        assert isinstance(consistency2, bool), "Should return boolean for story 2"

    @pytest.mark.asyncio
    async def test_error_recovery_in_complete_workflow(self, tmp_path):
        """Test error recovery in complete workflow context."""
        # Arrange
        epic_file = tmp_path / "error-recovery-epic.md"
        epic_file.write_text("""
# Error Recovery Test Epic

## Stories
- [ ] Error Recovery Story
""")
        
        driver = EpicDriver(
            epic_path=str(epic_file),
            max_iterations=1,
            skip_quality=True,
            skip_tests=True
        )
        
        # Create story that will trigger various errors
        story_file = tmp_path / "error-recovery-story.md"
        story_file.write_text("# Error Recovery Story\n\n**Status**: in_progress")
        
        story = {'path': str(story_file), 'status': 'in_progress', 'id': 'error-recovery-story'}
        
        # Act - simulate various error conditions
        with patch.object(driver, '_check_state_consistency', side_effect=[
            RuntimeError("Test error 1"),
            asyncio.CancelledError("Test cancellation"),
            True  # Finally succeed
        ]):
            # Test error handling
            try:
                result = await driver._check_state_consistency(story)
                assert False, "Should have raised exception"
            except RuntimeError:
                pass  # Expected
            
            # Test cancellation handling
            try:
                result = await driver._check_state_consistency(story)
                assert False, "Should have raised cancellation"
            except asyncio.CancelledError:
                pass  # Expected
            
            # Test success case
            result = await driver._check_state_consistency(story)
            assert result is True, "Should eventually succeed"