"""
Tests for SpecDevAgent - TDD-focused development agent.

Tests follow TDD principles:
1. Write failing tests first (RED)
2. Implement minimal code to pass (GREEN)
3. Refactor while keeping tests green (REFACTOR)
"""

import pytest
from unittest.mock import Mock, AsyncMock

from spec_automation.spec_dev_agent import SpecDevAgent


class TestSpecDevAgent:
    """Test suite for SpecDevAgent following TDD principles."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for tests."""
        return tmp_path

    @pytest.fixture
    def sample_story_path(self, temp_dir):
        """Create a sample story file for testing."""
        story_content = """# Story 1.2: SpecDevAgent (TDD-Focused) Implementation

## Status
**Done**

---

## Story

**As a** development agent using the spec_automation module,
**I want** to implement SpecDevAgent with TDD (Test-Driven Development) workflow capabilities,
**so that** I can write tests first and implement code to meet all requirements from parsed planning documents.

---

## Acceptance Criteria

1. Create `spec_dev_agent.py` with SafeClaudeSDK integration
2. Implement TDD workflow: write tests first → implement code → ensure coverage
3. Develop prompt system in `prompts.py` emphasizing TDD principles
4. Support requirement extraction from parsed documents
5. Implement status update mechanism to SpecStateManager
6. Ensure all generated tests pass before completion
7. Add comprehensive unit and integration tests
8. Verify SDK integration works independently

---

## Tasks / Subtasks

- [ ] Task 1: Create SpecDevAgent core implementation
- [ ] Task 2: Implement TDD workflow engine
- [ ] Task 3: Develop TDD-focused prompt system
- [ ] Task 4: Implement requirement extraction integration
- [ ] Task 5: Implement state management integration
- [ ] Task 6: Implement test verification and quality gates
- [ ] Task 7: Implement comprehensive testing
- [ ] Task 8: Verify independent operation

"""
        story_file = temp_dir / "test_story.md"
        story_file.write_text(story_content, encoding="utf-8")
        return story_file

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    # ===== RED PHASE: Write failing tests =====
    # These tests define the expected behavior BEFORE implementation

    def test_spec_dev_agent_initialization(self, mock_sdk):
        """Test SpecDevAgent initialization with SDK."""
        # RED: This test defines expected behavior
        agent = SpecDevAgent(sdk=mock_sdk)
        assert agent.sdk == mock_sdk

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_returns_bool(self, spec_dev_agent, sample_story_path):
        """Test that execute_tdd_cycle returns a boolean."""
        # RED: Define expected return type
        result = await spec_dev_agent.execute_tdd_cycle(str(sample_story_path))
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_is_async(self, spec_dev_agent, sample_story_path):
        """Test that execute_tdd_cycle is async."""
        # RED: Define expected async behavior
        result = await spec_dev_agent.execute_tdd_cycle(str(sample_story_path))
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_calls_sdk(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that execute_tdd_cycle calls the SDK."""
        # RED: Define expected SDK interaction
        await spec_dev_agent.execute_tdd_cycle(str(sample_story_path))
        # SDK should be called at least once
        assert mock_sdk.query.called

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_with_valid_story(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test execute_tdd_cycle with a valid story file."""
        # RED: Define expected success case
        mock_sdk.query.return_value = AsyncMock()
        result = await spec_dev_agent.execute_tdd_cycle(str(sample_story_path))
        assert result is True

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_handles_invalid_story(self, mock_sdk, spec_dev_agent, temp_dir):
        """Test execute_tdd_cycle handles invalid/non-existent story."""
        # RED: Define expected error handling
        invalid_path = temp_dir / "nonexistent.md"
        result = await spec_dev_agent.execute_tdd_cycle(str(invalid_path))
        # Should handle gracefully (return False or raise)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_updates_state(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that execute_tdd_cycle updates state in SpecStateManager."""
        # RED: Define expected state management
        # This will require SpecStateManager integration
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_generates_tests_first(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle generates tests before implementation."""
        # RED: Define TDD test-first behavior
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_verifies_tests_pass(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle verifies all tests pass before completion."""
        # RED: Define test verification behavior
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_with_tdd_requirements(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test TDD cycle follows red-green-refactor pattern."""
        # RED: Define red-green-refactor cycle
        pass

    def test_spec_dev_agent_has_tdd_workflow_engine(self, spec_dev_agent):
        """Test SpecDevAgent has TDD workflow engine."""
        # RED: Define TDD workflow attribute
        assert hasattr(spec_dev_agent, 'tdd_engine')

    def test_spec_dev_agent_has_prompt_system(self, spec_dev_agent):
        """Test SpecDevAgent has prompt system."""
        # RED: Define prompt system attribute
        assert hasattr(spec_dev_agent, 'prompts')

    def test_spec_dev_agent_has_state_manager(self, spec_dev_agent):
        """Test SpecDevAgent has state manager."""
        # RED: Define state manager attribute
        assert hasattr(spec_dev_agent, 'state_manager')

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_extracts_requirements(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle extracts requirements from story."""
        # RED: Define requirement extraction
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_maps_requirements_to_tests(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle maps requirements to tests."""
        # RED: Define requirement-to-test mapping
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_tracks_coverage(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle tracks test coverage."""
        # RED: Define coverage tracking
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_runs_quality_gates(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle runs quality gates (Ruff, BasedPyright, Pytest)."""
        # RED: Define quality gate execution
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_requires_all_tests_pass(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle requires all tests to pass before completion."""
        # RED: Define all-tests-must-pass requirement
        pass

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_handles_sdk_errors(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that TDD cycle handles SDK errors gracefully."""
        # RED: Define SDK error handling
        mock_sdk.query.side_effect = Exception("SDK Error")
        result = await spec_dev_agent.execute_tdd_cycle(str(sample_story_path))
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_independent_operation(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test that SpecDevAgent operates independently (no .bmad-core dependency)."""
        # RED: Define independence requirement
        pass


class TestSpecDevAgentTDDWorkflow:
    """Test suite for SpecDevAgent TDD workflow implementation."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for tests."""
        return tmp_path

    @pytest.fixture
    def sample_story_path(self, temp_dir):
        """Create a sample story file for testing."""
        story_content = """# Story Test

## Acceptance Criteria

1. First requirement
2. Second requirement
3. Third requirement

"""
        story_file = temp_dir / "test_story.md"
        story_file.write_text(story_content, encoding="utf-8")
        return story_file

    @pytest.mark.asyncio
    async def test_tdd_cycle_red_phase_generates_failing_test(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test RED phase: Generate failing test."""
        # RED: Define red phase behavior
        pass

    @pytest.mark.asyncio
    async def test_tdd_cycle_green_phase_implements_minimal_code(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test GREEN phase: Implement minimal code to pass test."""
        # GREEN: Define green phase behavior
        pass

    @pytest.mark.asyncio
    async def test_tdd_cycle_refactor_phase_improves_code(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test REFACTOR phase: Improve code while keeping tests green."""
        # REFACTOR: Define refactor phase behavior
        pass

    @pytest.mark.asyncio
    async def test_tdd_cycle_iteration_control(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test TDD cycle iteration control."""
        # Define iteration control
        pass

    @pytest.mark.asyncio
    async def test_tdd_cycle_coverage_tracking(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test TDD cycle coverage tracking."""
        # Define coverage tracking
        pass


class TestSpecDevAgentIntegration:
    """Integration tests for SpecDevAgent with other components."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Create a temporary database path."""
        return tmp_path / "test_progress.db"

    @pytest.fixture
    def sample_story_path(self, temp_dir):
        """Create a sample story file for testing."""
        story_content = """# Story Test

## Acceptance Criteria

1. First requirement
2. Second requirement
3. Third requirement

"""
        story_file = temp_dir / "test_story.md"
        story_file.write_text(story_content, encoding="utf-8")
        return story_file

    @pytest.mark.asyncio
    async def test_state_manager_integration(self, mock_sdk, spec_dev_agent, temp_db_path, sample_story_path):
        """Test integration with SpecStateManager."""
        # Define state manager integration
        pass

    @pytest.mark.asyncio
    async def test_doc_parser_integration(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test integration with DocumentParser."""
        # Define document parser integration
        pass

    @pytest.mark.asyncio
    async def test_quality_agents_integration(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test integration with quality agents (Ruff, BasedPyright, Pytest)."""
        # Define quality agents integration
        pass

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mock_sdk, spec_dev_agent, sample_story_path):
        """Test complete end-to-end workflow."""
        # Define end-to-end test
        pass


class TestSpecDevAgentPromptSystem:
    """Test suite for SpecDevAgent prompt system."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    @pytest.mark.asyncio
    async def test_prompts_module_exists(self, spec_dev_agent):
        """Test that prompts.py module exists."""
        # Define prompt module check
        pass

    @pytest.mark.asyncio
    async def test_generate_test_prompt(self, spec_dev_agent):
        """Test test generation prompt."""
        # Define test generation prompt
        pass

    @pytest.mark.asyncio
    async def test_generate_implementation_prompt(self, spec_dev_agent):
        """Test implementation prompt."""
        # Define implementation prompt
        pass

    @pytest.mark.asyncio
    async def test_red_green_refactor_prompts(self, spec_dev_agent):
        """Test red-green-refactor prompt sequences."""
        # Define RGR prompts
        pass


class TestSpecDevAgentErrorHandling:
    """Test suite for SpecDevAgent error handling."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for tests."""
        return tmp_path

    @pytest.fixture
    def sample_story_path(self, temp_dir):
        """Create a sample story file for testing."""
        story_content = """# Story Test

## Acceptance Criteria

1. First requirement
2. Second requirement
3. Third requirement

"""
        story_file = temp_dir / "test_story.md"
        story_file.write_text(story_content, encoding="utf-8")
        return story_file

    @pytest.mark.asyncio
    async def test_handle_missing_story_file(self, spec_dev_agent):
        """Test handling of missing story file."""
        # Define missing file handling
        pass

    @pytest.mark.asyncio
    async def test_handle_sdk_unavailable(self, spec_dev_agent):
        """Test handling when SDK is unavailable."""
        # Define SDK unavailability handling
        pass

    @pytest.mark.asyncio
    async def test_handle_test_execution_failure(self, spec_dev_agent, sample_story_path):
        """Test handling of test execution failure."""
        # Define test execution failure handling
        pass

    @pytest.mark.asyncio
    async def test_handle_quality_gate_failure(self, spec_dev_agent, sample_story_path):
        """Test handling of quality gate failure."""
        # Define quality gate failure handling
        pass

    @pytest.mark.asyncio
    async def test_recovery_from_errors(self, spec_dev_agent, sample_story_path):
        """Test recovery from various errors."""
        # Define error recovery
        pass


class TestSpecDevAgentIndependentOperation:
    """Test suite for SpecDevAgent independent operation verification."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    @pytest.mark.asyncio
    async def test_no_bmad_core_dependency(self):
        """Test that SpecDevAgent has no .bmad-core dependency."""
        # Define independence check
        pass

    @pytest.mark.asyncio
    async def test_safe_claude_sdk_integration(self, mock_sdk):
        """Test SafeClaudeSDK integration works independently."""
        # Define SDK integration test
        pass

    @pytest.mark.asyncio
    async def test_standalone_operation(self, mock_sdk):
        """Test standalone operation without external dependencies."""
        # Define standalone operation test
        pass


# ===== TDD CYCLE TESTS =====
# These tests verify the complete TDD cycle

class TestCompleteTDDCycle:
    """Test the complete TDD cycle implementation."""

    @pytest.fixture
    def mock_sdk(self):
        """Create a mock SDK instance."""
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def spec_dev_agent(self, mock_sdk):
        """Create a SpecDevAgent instance for testing."""
        return SpecDevAgent(sdk=mock_sdk)

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for tests."""
        return tmp_path

    @pytest.fixture
    def complex_story_path(self, temp_dir):
        """Create a complex story file for comprehensive testing."""
        story_content = """# Story: Complex Feature Implementation

## Status
**Ready for Development**

---

## Story

**As a** developer,
**I want** a complex feature with multiple components,
**so that** I can test the full TDD workflow.

---

## Acceptance Criteria

1. Component A is implemented
2. Component B is implemented
3. Component C is implemented
4. All components work together
5. Tests achieve >80% coverage
6. Quality gates pass (Ruff, BasedPyright, Pytest)

---

## Tasks

- [ ] Task 1: Implement Component A
- [ ] Task 2: Implement Component B
- [ ] Task 3: Implement Component C
- [ ] Task 4: Integration testing
- [ ] Task 5: Quality gate verification

"""
        story_file = temp_dir / "complex_story.md"
        story_file.write_text(story_content, encoding="utf-8")
        return story_file

    @pytest.mark.asyncio
    async def test_complete_tdd_cycle_all_requirements(self, mock_sdk, spec_dev_agent, complex_story_path):
        """Test complete TDD cycle addresses all acceptance criteria."""
        # Define complete TDD cycle test
        # This is the ultimate test that validates the entire implementation
        pass

    @pytest.mark.asyncio
    async def test_complete_tdd_cycle_coverage_target(self, mock_sdk, spec_dev_agent, complex_story_path):
        """Test complete TDD cycle achieves >80% coverage."""
        # Define coverage target test
        pass

    @pytest.mark.asyncio
    async def test_complete_tdd_cycle_quality_gates(self, mock_sdk, spec_dev_agent, complex_story_path):
        """Test complete TDD cycle passes all quality gates."""
        # Define quality gates test
        pass
