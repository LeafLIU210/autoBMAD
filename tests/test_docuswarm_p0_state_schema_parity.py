"""P0: StateManager initial state schema parity tests (H3).

Ensures StateManager.create_pipeline produces the same initial keys as
pipeline.state.create_initial_state.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from autoBMAD.docuswarm.pipeline.state import create_initial_state
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestStateManagerInitialStateSchemaParity:
    """T3.1: DB-created initial state keys must match graph initial state keys."""

    def test_state_manager_initial_state_matches_pipeline_state(self) -> None:
        """StateManager._create_initial_state keys == create_initial_state keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            pipeline_id = sm.create_pipeline(subject="schema-parity")
            with sm.db.acquire() as conn:
                row = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                ).fetchone()
                db_state = json.loads(row["state_json"])

        graph_state = create_initial_state(pipeline_id, {"subject": "schema-parity"})

        db_keys = set(db_state.keys())
        graph_keys = set(graph_state.keys())

        missing_in_db = graph_keys - db_keys
        missing_in_graph = db_keys - graph_keys

        assert not missing_in_db, f"Keys missing from DB initial state: {missing_in_db}"
        assert not missing_in_graph, f"Keys missing from graph initial state: {missing_in_graph}"

    def test_db_initial_state_has_failed_nodes(self) -> None:
        """DB initial state must include failed_nodes list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            pipeline_id = sm.create_pipeline(subject="failed-nodes")
            with sm.db.acquire() as conn:
                row = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                ).fetchone()
                state = json.loads(row["state_json"])
        assert "failed_nodes" in state
        assert state["failed_nodes"] == []

    def test_db_initial_state_has_docs_context_summary(self) -> None:
        """DB initial state must include docs_context_summary list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "test.db")
            sm = StateManager(db_path=db_path)
            pipeline_id = sm.create_pipeline(subject="docs-summary")
            with sm.db.acquire() as conn:
                row = conn.execute(
                    "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                    (pipeline_id,),
                ).fetchone()
                state = json.loads(row["state_json"])
        assert "docs_context_summary" in state
        assert state["docs_context_summary"] == []
