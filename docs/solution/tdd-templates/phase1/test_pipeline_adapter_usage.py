"""Test PipelineAdapter is used for all synthetic ID creation.

TDD Phase 1.3: No direct f-string synthetic ID creation allowed.

Usage:
    1. Copy to tests/architecture/test_pipeline_adapter_usage.py
    2. Run: pytest tests/architecture/test_pipeline_adapter_usage.py -v
    3. Expected: 3 failed (Red phase)
    4. Update flow.py to use PipelineAdapter
    5. Run again: Expected 3 passed (Green phase)
"""

import ast
import pytest
from pathlib import Path


class TestPipelineAdapterBoundaryEnforcement:
    """Test suite: PipelineAdapter is the single boundary."""

    def test_no_direct_node_prefix_fstrings(self):
        """RED: No file should contain f\"node-{...}\" patterns.
        
        All synthetic pipeline_id creation must use PipelineAdapter.
        """
        project_root = Path(__file__).parents[3]
        ne_path = project_root / "autoBMAD" / "docuswarm" / "node_execution"
        
        violations = []
        
        for py_file in ne_path.glob("*.py"):
            if py_file.name == "pipeline_adapter.py":
                continue  # Adapter itself is allowed to create these
            if "__pycache__" in str(py_file):
                continue
            
            content = py_file.read_text()
            lines = content.split("\n")
            
            for i, line in enumerate(lines, 1):
                # Check for f"node- or f'node- patterns
                if ('f\"node-' in line or "f'node-" in line or 
                    'f"node-run-' in line or "f'node-run-" in line):
                    # Check if this line uses PipelineAdapter
                    if "PipelineAdapter" not in line and "create_pipeline_id" not in line:
                        violations.append(f"{py_file.name}:{i}: {line.strip()}")
        
        assert not violations, f"Direct synthetic ID creation found: {violations}"

    def test_flow_py_uses_adapter(self):
        """RED: flow.py must import and use PipelineAdapter.
        
        This is a specific check for the main violation found in research.
        """
        project_root = Path(__file__).parents[3]
        flow_path = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "flow.py"
        
        assert flow_path.exists(), "flow.py must exist"
        
        content = flow_path.read_text()
        
        # Must import PipelineAdapter
        assert "from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter" in content, \\
            "flow.py must import PipelineAdapter"
        
        # Must use create_pipeline_id
        assert "PipelineAdapter.create_pipeline_id(" in content, \\
            "flow.py must use PipelineAdapter.create_pipeline_id()"
        
        assert "PipelineAdapter.create_run_pipeline_id(" in content, \\
            "flow.py must use PipelineAdapter.create_run_pipeline_id()"

    def test_adapter_methods_are_used(self):
        """RED: PipelineAdapter methods must have at least one usage.
        
        Verifies the adapter is actually being used, not just imported.
        """
        project_root = Path(__file__).parents[3]
        docuswarm_path = project_root / "autoBMAD" / "docuswarm"
        adapter_path = docuswarm_path / "node_execution" / "pipeline_adapter.py"
        
        # Parse adapter to get method names
        adapter_content = adapter_path.read_text()
        tree = ast.parse(adapter_content)
        
        static_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's a staticmethod
                decorators = [d for d in node.decorator_list 
                             if isinstance(d, ast.Name) and d.id == "staticmethod"]
                if decorators:
                    static_methods.append(node.name)
        
        # Check each method is used somewhere
        unused_methods = []
        for method_name in static_methods:
            found_usage = False
            for py_file in docuswarm_path.rglob("*.py"):
                if py_file.name == "pipeline_adapter.py":
                    continue
                if "__pycache__" in str(py_file):
                    continue
                
                content = py_file.read_text()
                if f"PipelineAdapter.{method_name}(" in content:
                    found_usage = True
                    break
            
            if not found_usage:
                unused_methods.append(method_name)
        
        assert not unused_methods, f"PipelineAdapter methods not used: {unused_methods}"
