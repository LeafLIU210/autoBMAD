"""Test deprecated executor has been removed.

TDD Phase 1.2: _create_default_node_executor must not exist.

Usage:
    1. Copy to tests/pipeline/test_no_deprecated_executor.py
    2. Run: pytest tests/pipeline/test_no_deprecated_executor.py -v
    3. Expected: 4 failed (Red phase)
    4. Delete _create_default_node_executor and create_enhanced_node_executor
    5. Run again: Expected 4 passed (Green phase)
"""

import pytest
import ast
from pathlib import Path
from autoBMAD.docuswarm.pipeline import graph as graph_module


class TestNoDeprecatedExecutor:
    """Test suite: deprecated executor functions removed."""

    def test_create_default_node_executor_removed(self):
        """RED: _create_default_node_executor function must not exist.
        
        This function was deprecated in Story 11.6 and must be removed.
        It produced empty deliverables and should not be used in production.
        """
        assert not hasattr(graph_module, '_create_default_node_executor'), \\
            "_create_default_node_executor must be removed"

    def test_create_enhanced_node_executor_removed(self):
        """RED: create_enhanced_node_executor function must not exist.
        
        This was a wrapper around the deprecated default executor.
        """
        assert not hasattr(graph_module, 'create_enhanced_node_executor'), \\
            "create_enhanced_node_executor must be removed"

    def test_default_executor_not_in_all(self):
        """RED: Deprecated functions must not be exported in __all__."""
        if hasattr(graph_module, '__all__'):
            assert '_create_default_node_executor' not in graph_module.__all__
            assert 'create_enhanced_node_executor' not in graph_module.__all__

    def test_no_deprecated_imports_in_codebase(self):
        """RED: No file should import the deprecated functions.
        
        This is an architecture test scanning the codebase.
        """
        project_root = Path(__file__).parents[3]
        docuswarm_path = project_root / "autoBMAD" / "docuswarm"
        
        deprecated_names = [
            '_create_default_node_executor',
            'create_enhanced_node_executor',
        ]
        
        violations = []
        
        for py_file in docuswarm_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Check imports
                    if isinstance(node, ast.ImportFrom):
                        if node.module and 'graph' in node.module:
                            for alias in node.names:
                                if alias.name in deprecated_names:
                                    violations.append(f"{py_file}: imports {alias.name}")
                    
                    # Check function calls
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in deprecated_names:
                                violations.append(f"{py_file}: calls {node.func.id}")
            except Exception:
                continue
        
        assert not violations, f"Found deprecated function usage: {violations}"
