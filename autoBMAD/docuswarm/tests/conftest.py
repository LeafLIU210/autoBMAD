"""Shared pytest fixtures for DocuSwarm tests."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES, PipelineState
from autoBMAD.docuswarm.storage.state_manager import StateManager

# ============================================================
# CLI Fixtures
# ============================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def cli_runner_isolated(tmp_path: Path) -> CliRunner:
    """Create an isolated CLI runner with temp directory."""
    return CliRunner(env={"HOME": str(tmp_path)})


# ============================================================
# Database Fixtures
# ============================================================


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_docuswarm.db"


@pytest.fixture
def state_manager(temp_db_path: Path) -> Generator[StateManager, None, None]:
    """Create a StateManager with temporary database."""
    manager = StateManager(db_path=str(temp_db_path))
    yield manager


@pytest.fixture
def state_manager_with_pipeline(
    state_manager: StateManager,
) -> tuple[StateManager, str]:
    """Create a StateManager with a pre-created pipeline."""
    pipeline_id = state_manager.create_pipeline(
        subject="test-subject",
        subject_context={"content": "Test content", "context_file": "test.md"},
    )
    return state_manager, pipeline_id


# ============================================================
# Context File Fixtures
# ============================================================


@pytest.fixture
def valid_context_file(tmp_path: Path) -> Path:
    """Create a valid context file."""
    context_file = tmp_path / "proposal.md"
    context_file.write_text(
        (
            "# Test Proposal\n\n"
            "## Requirements\n"
            "- Build a web application\n"
            "- Support user authentication\n"
            "- Provide REST API\n"
        ),
        encoding="utf-8",
    )
    return context_file


@pytest.fixture
def empty_context_file(tmp_path: Path) -> Path:
    """Create an empty context file."""
    context_file = tmp_path / "empty.md"
    context_file.write_text("", encoding="utf-8")
    return context_file


@pytest.fixture
def invalid_context_file(tmp_path: Path) -> Path:
    """Create an invalid (minimal) context file."""
    context_file = tmp_path / "invalid.md"
    context_file.write_text("Too short", encoding="utf-8")
    return context_file


# ============================================================
# Pipeline State Fixtures
# ============================================================


@pytest.fixture
def initial_pipeline_state() -> PipelineState:
    """Create an initial pipeline state."""
    from autoBMAD.docuswarm.pipeline.state import create_initial_state

    return create_initial_state(
        pipeline_id="test-pipeline-001",
        subject_context={"subject": "test", "content": "Test content"},
    )


@pytest.fixture
def running_pipeline_state() -> PipelineState:
    """Create a running pipeline state with analyst completed."""
    from autoBMAD.docuswarm.pipeline.state import RUNNING, create_initial_state

    state = create_initial_state(
        pipeline_id="test-pipeline-002",
        subject_context={"subject": "test", "content": "Test content"},
    )
    state["status"] = RUNNING
    state["current_node"] = "pm"
    state["completed_nodes"] = ["analyst"]
    state["deliverables"] = {
        "analyst": {"analysis": "Test analysis", "requirements": ["req1", "req2"]}
    }
    state["node_iterations"] = {"analyst": 1}
    return state


@pytest.fixture
def completed_pipeline_state() -> PipelineState:
    """Create a completed pipeline state."""
    from autoBMAD.docuswarm.pipeline.state import COMPLETED, create_initial_state

    state = create_initial_state(
        pipeline_id="test-pipeline-003",
        subject_context={"subject": "test", "content": "Test content"},
    )
    state["status"] = COMPLETED
    state["current_node"] = "po"
    state["completed_nodes"] = PIPELINE_NODES.copy()
    state["deliverables"] = {node: {"output": f"{node} output"} for node in PIPELINE_NODES}
    state["node_iterations"] = {node: 1 for node in PIPELINE_NODES}
    return state


# ============================================================
# Mock Fixtures
# ============================================================


@pytest.fixture
def mock_orchestrator() -> MagicMock:
    """Create a mock HybridOrchestrator."""
    mock = MagicMock()
    mock.start_pipeline = AsyncMock(return_value="test-pipeline-001")
    mock.resume_pipeline = AsyncMock(return_value={"status": "completed"})
    mock.restart_from_node = AsyncMock(return_value={"status": "completed"})
    mock.get_pipeline_status = AsyncMock(
        return_value={
            "pipeline_id": "test-pipeline-001",
            "status": "running",
            "current_node": "pm",
        }
    )
    return mock


@pytest.fixture
def mock_llm_response() -> dict[str, Any]:
    """Create a mock LLM validation response."""
    return {
        "valid": True,
        "reason": "Context is sufficient",
        "missing_info": [],
    }


@pytest.fixture
def mock_session_manager() -> MagicMock:
    """Create a mock KimiSessionManager with SDK-realistic Message objects.

    IMPORTANT: content must be list[ContentPart], not a plain string.
    The real Kimi SDK always returns Message.content as list[ContentPart].
    """
    json_str = '{"valid": true, "reason": "OK", "missing_info": []}'

    # Create realistic TextPart mock
    text_part = MagicMock()
    text_part.type = "text"
    text_part.text = json_str

    # Create realistic Message mock
    assistant_msg = MagicMock()
    assistant_msg.role = "assistant"
    assistant_msg.content = [text_part]  # list[ContentPart], not str
    assistant_msg.extract_text.return_value = json_str

    mock = MagicMock()
    mock.single_prompt = AsyncMock(return_value=[assistant_msg])
    mock.resume_session = AsyncMock(return_value=None)
    mock.close_all = AsyncMock()
    return mock


# ============================================================
# Patch Fixtures
# ============================================================


@pytest.fixture
def patch_orchestrator(mock_orchestrator: MagicMock):
    """Patch HybridOrchestrator for CLI tests."""
    with patch(
        "autoBMAD.docuswarm.main.HybridOrchestrator",
        return_value=mock_orchestrator,
    ) as patched:
        yield patched, mock_orchestrator


@pytest.fixture
def patch_state_manager(state_manager: StateManager):
    """Patch StateManager for CLI tests."""
    with patch(
        "autoBMAD.docuswarm.main.StateManager",
        return_value=state_manager,
    ) as patched:
        yield patched, state_manager
