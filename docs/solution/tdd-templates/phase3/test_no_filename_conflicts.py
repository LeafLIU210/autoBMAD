"""Test no filename conflicts between pipeline and node_execution.

TDD Phase 3.1: Each module has unique filenames.

Usage:
    1. Copy to tests/architecture/test_no_filename_conflicts.py
    2. Run: pytest tests/architecture/test_no_filename_conflicts.py -v
    3. Expected: 2 failed (Red phase)
    4. Rename node_execution/escalation.py to node_escalation.py
    5. Update all imports
    6. Run again: Expected 2 passed (Green phase)
"""

from pathlib import Path


class TestNoFilenameConflicts:
    """Test suite: No identical filenames in pipeline and node_execution."""

    def test_no_escalation_py_conflict(self):
        """RED: escalation.py must not exist in both modules.
        
        The node_execution version should be renamed to node_escalation.py.
        """
        project_root = Path(__file__).parents[3]
        
        pipeline_escalation = project_root / "autoBMAD" / "docuswarm" / "pipeline" / "escalation.py"
        node_escalation = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "escalation.py"
        
        # Both should not exist simultaneously
        if pipeline_escalation.exists() and node_escalation.exists():
            assert False, (
                "Both pipeline/escalation.py and node_execution/escalation.py exist. "
                "Rename node_execution/escalation.py to node_escalation.py"
            )

    def test_node_escalation_py_exists(self):
        """GREEN: node_escalation.py should exist after rename."""
        project_root = Path(__file__).parents[3]
        node_escalation = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "node_escalation.py"
        
        # After migration, this file should exist
        assert node_escalation.exists(), (
            "node_execution/node_escalation.py should exist after rename"
        )
