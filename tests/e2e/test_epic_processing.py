"""
End-to-End tests for complete epic processing

Tests cover:
- Full epic processing with quality gates
- Epic with multiple stories
- Error recovery scenarios
- Performance benchmarks
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
import time

# Import the EpicDriver class
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD" / "epic_automation"))

from epic_driver import EpicDriver


@pytest.mark.e2e
class TestEpicProcessingE2E:
    """End-to-End tests for epic processing."""

    @pytest.mark.asyncio
    async def test_epic_with_quality_gates_e2e(self):
        """End-to-end test with quality gates enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: E2E Test Epic

### Story 001: E2E Test Story
**Story ID**: 001

**As a** developer,
**I want to** test the complete workflow end-to-end,
**So that** I can verify all components work together.

## Acceptance Criteria
- [ ] Complete workflow executes
- [ ] All phases complete successfully

## Tasks / Subtasks
- [ ] Task 1: Create test implementation

## Dev Notes
This is an E2E test implementation.
"""
            epic_path.write_text(epic_content)

            # Create story file
            story_content = """# Story 001: E2E Test Story

**Status**: Approved

## Story
**As a** developer,
**I want to** test the complete workflow end-to-end,
**So that** I can verify all components work together.

## Acceptance Criteria
- [ ] Complete workflow executes
- [ ] All phases complete successfully

## Tasks / Subtasks
- [ ] Task 1: Create test implementation

## Dev Notes
This is an E2E test implementation.
"""
            (stories_dir / "001.md").write_text(story_content)

            # Create a simple Python module
            module_content = '''"""
Simple test module for E2E testing.
"""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


if __name__ == "__main__":
    print(add(2, 3))
'''
            (source_dir / "calculator.py").write_text(module_content)
            (source_dir / "__init__.py").write_text('"""Test package."""')

            # Create test file
            test_content = '''"""
Test for calculator module.
"""


def test_add():
    """Test add function."""
    from calculator import add
    assert add(2, 3) == 5


def test_subtract():
    """Test subtract function."""
    from calculator import subtract
    assert subtract(5, 3) == 2
'''
            (test_dir / "test_calculator.py").write_text(test_content)

            # Mock agents to avoid real execution
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class, \
                 patch('autoBMAD.epic_automation.CodeQualityAgent') as quality_agent_class, \
                 patch('autoBMAD.epic_automation.TestAutomationAgent') as test_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                quality_agent = AsyncMock()
                quality_agent.run_quality_gates = AsyncMock(return_value={
                    'status': 'completed',
                    'errors': 0,
                    'basedpyright': {'success': True, 'error_count': 0},
                    'ruff': {'success': True, 'error_count': 0}
                })
                quality_agent_class.return_value = quality_agent

                test_agent = AsyncMock()
                test_agent.run_test_automation = AsyncMock(return_value={
                    'status': 'completed',
                    'pytest': {
                        'summary': {
                            'passed': 2,
                            'failed': 0,
                            'error': 0
                        }
                    }
                })
                test_agent_class.return_value = test_agent

                # Create driver with all features enabled
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=False,
                    skip_tests=False,
                    verbose=True
                )

                start_time = time.time()
                result = await driver.run()
                end_time = time.time()

                # Verify result
                assert result is True

                # Verify execution time is reasonable (< 10 seconds for mocked test)
                execution_time = end_time - start_time
                assert execution_time < 10, f"Execution took too long: {execution_time}s"

                # Verify all phases were invoked
                assert sm_agent.execute.called
                assert dev_agent.execute.called
                assert qa_agent.execute.called
                assert quality_agent.run_quality_gates.called
                assert test_agent.run_test_automation.called

                # Verify progress tracking
                assert driver.state_manager.update_story_status.called

    @pytest.mark.asyncio
    async def test_epic_with_multiple_stories_e2e(self):
        """End-to-end test with multiple stories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file with 5 stories
            epic_content = """# Epic: Multi-Story E2E Test

### Story 001: First Feature
**Story ID**: 001

### Story 002: Second Feature
**Story ID**: 002

### Story 003: Third Feature
**Story ID**: 003

### Story 004: Fourth Feature
**Story ID**: 004

### Story 005: Fifth Feature
**Story ID**: 005
"""
            epic_path.write_text(epic_content)

            # Create all story files
            for i in range(1, 6):
                (stories_dir / f"{i:03d}.md").write_text(f"# Story {i:03d}\n")

            # Create source and test files
            (source_dir / "module.py").write_text("def func(): pass\n")
            (test_dir / "test_module.py").write_text("def test_func(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=True
                )

                result = await driver.run()

                assert result is True
                # Verify all 5 stories were processed
                assert sm_agent.execute.call_count == 5
                assert dev_agent.execute.call_count == 5
                assert qa_agent.execute.call_count == 5

    @pytest.mark.asyncio
    async def test_error_recovery_scenario(self):
        """Test error recovery in workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Error Recovery Test

### Story 001: Error Recovery Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents - QA fails first time, succeeds on retry
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(side_effect=[
                    {"passed": False, "errors": ["Error 1"]},
                    {"passed": True}
                ])
                qa_agent_class.return_value = qa_agent

                # Create driver with retry enabled
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=True,
                    retry_failed=True,
                    max_iterations=3
                )

                result = await driver.run()

                # Should succeed with retry
                assert result is True
                # QA should be called twice
                assert qa_agent.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_performance_benchmark(self):
        """Performance benchmark for epic processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic with 10 stories
            epic_content = "# Epic: Performance Test\n\n"
            for i in range(1, 11):
                epic_content += f"### Story {i:03d}: Test Story {i}\n**Story ID**: {i:03d}\n\n"

            epic_path.write_text(epic_content)

            # Create all story files
            for i in range(1, 11):
                (stories_dir / f"{i:03d}.md").write_text(f"# Story {i:03d}\n")

            # Create source and test files
            (source_dir / "module.py").write_text("def func(): pass\n")
            (test_dir / "test_module.py").write_text("def test_func(): pass\n")

            # Mock agents with minimal processing
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=False  # Reduce logging overhead
                )

                start_time = time.time()
                result = await driver.run()
                end_time = time.time()

                execution_time = end_time - start_time

                # Verify result
                assert result is True

                # Performance assertions
                # With 10 stories and mocked agents, should complete in under 5 seconds
                assert execution_time < 5, f"Performance benchmark failed: {execution_time}s"

                print(f"\n=== Performance Benchmark Results ===")
                print(f"Stories processed: 10")
                print(f"Total execution time: {execution_time:.2f}s")
                print(f"Average time per story: {execution_time/10:.2f}s")
                print(f"Stories per second: {10/execution_time:.2f}")

    @pytest.mark.asyncio
    async def test_backward_compatibility(self):
        """Test that existing CLI options still work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Backward Compatibility Test

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Test all existing CLI options
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    max_iterations=5,
                    retry_failed=True,
                    verbose=True,
                    concurrent=False,
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True
                )

                result = await driver.run()

                assert result is True
                assert driver.max_iterations == 5
                assert driver.retry_failed is True
                assert driver.verbose is True
                assert driver.concurrent is False
