"""P0: StateManager consistency tests (C3 + C4).

Ensures update_pipeline_state synchronizes top-level columns,
get_pipeline returns state snapshot, and explicit pipeline_id works.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestStateManagerGetAndListStatusConsistency:
    """T3.1: create → update running → list running must be consistent."""

    @pytest.mark.asyncio
    async def test_update_running_then_list_running_finds_pipeline(self) -> None:
        """After update_pipeline_state(status='running'), list_pipelines('running') must find it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            pipeline_id = sm.create_pipeline(subject="consistency")

            await sm.update_pipeline_state(
                pipeline_id, {"status": "running", "current_node": "analyst"}
            )

            running = sm.list_pipelines(status="running")
            ids = [p["pipeline_id"] for p in running]
            assert pipeline_id in ids, f"Expected {pipeline_id} in running list, got {ids}"

    def test_get_pipeline_returns_state_key(self) -> None:
        """get_pipeline() must include 'state' key with full state snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            pipeline_id = sm.create_pipeline(subject="state-key")
            pipeline = sm.get_pipeline(pipeline_id)
            assert "state" in pipeline, "get_pipeline() must return 'state' key"
            assert pipeline["state"]["status"] == "pending"


class TestStartPipelineWithExplicitPipelineId:
    """T4.1: create_pipeline with explicit pipeline_id must use that ID."""

    def test_create_pipeline_with_explicit_id(self) -> None:
        """Passing pipeline_id must create row with that exact ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            custom_id = "my-custom-pipeline-123"
            returned_id = sm.create_pipeline(
                subject="custom-id", pipeline_id=custom_id
            )
            assert returned_id == custom_id
            pipeline = sm.get_pipeline(custom_id)
            assert pipeline is not None
            assert pipeline["pipeline_id"] == custom_id

    @pytest.mark.asyncio
    async def test_update_pipeline_state_with_explicit_id(self) -> None:
        """Updating a pipeline created with explicit ID must succeed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            custom_id = "my-custom-pipeline-456"
            sm.create_pipeline(subject="custom-id", pipeline_id=custom_id)
            ok = await sm.update_pipeline_state(
                custom_id, {"status": "running", "current_node": "analyst"}
            )
            assert ok is True
            pipeline = sm.get_pipeline(custom_id)
            assert pipeline["status"] == "running"
            assert pipeline["current_node"] == "analyst"
