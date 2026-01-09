"""
Tests for SpecDriver - Workflow orchestrator for spec automation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.spec_automation.spec_driver import SpecDriver
from autoBMAD.spec_automation.doc_parser import DocParser
from autoBMAD.spec_automation.spec_dev_agent import SpecDevAgent
from autoBMAD.spec_automation.spec_qa_agent import SpecQAAgent
from autoBMAD.spec_automation.quality_gates import QualityGateRunner
from autoBMAD.spec_automation.spec_state_manager import SpecStateManager


class TestSpecDriver:
    """Test suite for SpecDriver."""

    @pytest.fixture
    def mock_sdk(self):
        sdk = Mock()
        sdk.query = AsyncMock()
        return sdk

    @pytest.fixture
    def temp_dir(self, tmp_path):
        return tmp_path

    @pytest.fixture
    def sample_story_path(self, temp_dir):
        story_content = """# Story 1.4: SpecDriver Orchestrator Implementation

## Status
**Ready for Development**

---

## Acceptance Criteria

1. Create spec_driver.py with complete orchestration logic
2. Implement workflow: Document Parse → Dev Development → QA Review → Quality Gates
3. Coordinate Dev-QA cycles until all acceptance criteria met
4. Integrate Ruff, BasedPyright, and Pytest quality gates
5. Implement iteration control to prevent infinite loops
6. Generate comprehensive execution summary reports
7. Error handling and recovery mechanisms
8. End-to-end workflow testing
"""
        story_file = temp_dir / "test_story.md"
        story_file.write_text(story_content)
        return story_file

    @pytest.fixture
    def mock_db_path(self, temp_dir):
        return temp_dir / "test.db"

    @pytest.fixture
    def spec_driver(self, mock_sdk, mock_db_path):
        return SpecDriver(sdk=mock_sdk, db_path=str(mock_db_path))

    def test_spec_driver_initialization(self, mock_sdk, mock_db_path):
        """Test SpecDriver initialization with SDK and database."""
        driver = SpecDriver(sdk=mock_sdk, db_path=str(mock_db_path))
        assert driver.sdk == mock_sdk
        assert driver.db_path == str(mock_db_path)

    def test_spec_driver_has_doc_parser(self, spec_driver):
        """Test that SpecDriver has DocParser instance."""
        assert hasattr(spec_driver, 'doc_parser')
        assert isinstance(spec_driver.doc_parser, DocParser)

    def test_spec_driver_has_dev_agent(self, spec_driver):
        """Test that SpecDriver has SpecDevAgent instance."""
        assert hasattr(spec_driver, 'dev_agent')
        assert isinstance(spec_driver.dev_agent, SpecDevAgent)

    def test_spec_driver_has_qa_agent(self, spec_driver):
        """Test that SpecDriver has SpecQAAgent instance."""
        assert hasattr(spec_driver, 'qa_agent')
        assert isinstance(spec_driver.qa_agent, SpecQAAgent)

    def test_spec_driver_has_quality_gates(self, spec_driver):
        """Test that SpecDriver has QualityGateRunner instance."""
        assert hasattr(spec_driver, 'quality_gates')
        assert isinstance(spec_driver.quality_gates, QualityGateRunner)

    def test_spec_driver_has_state_manager(self, spec_driver):
        """Test that SpecDriver has SpecStateManager instance."""
        assert hasattr(spec_driver, 'state_manager')
        assert isinstance(spec_driver.state_manager, SpecStateManager)

    @pytest.mark.asyncio
    async def test_execute_workflow_returns_dict(self, spec_driver, sample_story_path):
        """Test that execute_workflow returns a dictionary."""
        result = await spec_driver.execute_workflow(str(sample_story_path))
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_workflow_has_success_key(self, spec_driver, sample_story_path):
        """Test that execute_workflow result has success key."""
        result = await spec_driver.execute_workflow(str(sample_story_path))
        assert 'success' in result

    @pytest.mark.asyncio
    async def test_iteration_control_has_max_limit(self, spec_driver):
        """Test that iteration control has maximum iteration limit."""
        assert hasattr(spec_driver, 'max_iterations')
        assert spec_driver.max_iterations > 0

    @pytest.mark.asyncio
    async def test_iteration_control_prevents_infinite_loops(self, spec_driver):
        """Test that iteration control prevents infinite loops."""
        with patch.object(spec_driver, 'max_iterations', 3):
            result = spec_driver._should_continue_iteration(
                iteration_count=3,
                max_iterations=3,
                previous_results=[]
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_workflow_state_machine_has_correct_phases(self, spec_driver):
        """Test that workflow has correct phases defined."""
        assert hasattr(spec_driver, 'PHASES')
        assert 'document_parse' in spec_driver.PHASES
        assert 'development' in spec_driver.PHASES
        assert 'qa_review' in spec_driver.PHASES
        assert 'quality_gates' in spec_driver.PHASES

    @pytest.mark.asyncio
    async def test_quality_gates_enforce_standards(self, spec_driver, sample_story_path):
        """Test that quality gates enforce standards before completion."""
        with patch.object(spec_driver.doc_parser, 'parse_document', return_value={}):
            with patch.object(spec_driver.quality_gates, 'run_all_gates', return_value=True) as mock_gates:
                result = await spec_driver.execute_workflow(str(sample_story_path))
                assert result['quality_gates']['passed'] is True
                mock_gates.assert_called_once()
