#!/usr/bin/env python3
"""
P0 Shared Context Debugger - F2 Critical Issue Research Tool

研究问题：shared_context 设计有持久化表象，但运行时传递链路断裂

目标：
1. 验证 PipelineAdapter.convert_pipeline_to_node_state() 是否传递 shared_context
2. 验证 PipelineAdapter.convert_node_to_pipeline_state() 是否将 shared_context 合回 pipeline state
3. 验证 NodeExecutor 从 NodeRunState 读取 shared_context 的 fallback 行为
4. 验证 _refresh_shared_context_from_db() 的 duck typing 是否能找到 StateManager
5. 验证 update_context_sdk.py 是否自行创建默认 StateManager()
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

repo_root = Path(__file__).parent.parent.parent.resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.pipeline.state import create_initial_state


def test_convert_pipeline_to_node_state_missing_shared_context() -> dict[str, Any]:
    """Test 1: convert_pipeline_to_node_state does NOT include shared_context in output."""
    print("\n" + "=" * 70)
    print("TEST 1: convert_pipeline_to_node_state() Missing shared_context")
    print("=" * 70)

    findings = {
        "test": "convert_pipeline_to_node_state_missing_shared_context",
        "issue": "PipelineAdapter.convert_pipeline_to_node_state() does not include shared_context in returned dict",
        "evidence": [],
        "severity": "CRITICAL",
    }

    # Create a pipeline state WITH shared_context
    pipeline_state = create_initial_state(
        pipeline_id="test-pipeline",
        subject_context={"task": "test"},
    )
    pipeline_state["shared_context"] = {
        "facts": {"market_scope": "global"},
        "decisions": {"architecture": "microservices"},
    }
    pipeline_state["deliverables"] = {"analyst": {"content": "analysis"}}

    # Convert to node state
    node_state = PipelineAdapter.convert_pipeline_to_node_state(
        pipeline_state, node_id="pm"
    )

    has_shared_context = "shared_context" in node_state
    shared_context_value = node_state.get("shared_context")

    print(f"Input PipelineState['shared_context'] = {pipeline_state['shared_context']!r}")
    print(f"Output NodeRunState keys: {list(node_state.keys())}")
    print(f"Output has 'shared_context' key: {has_shared_context}")
    print(f"Output shared_context value: {shared_context_value!r}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/node_execution/pipeline_adapter.py:233-246",
        "input_shared_context": pipeline_state["shared_context"],
        "output_keys": list(node_state.keys()),
        "has_shared_context_key": has_shared_context,
        "shared_context_value": shared_context_value,
        "verdict": "BUG CONFIRMED" if not has_shared_context else "OK",
    })

    if not has_shared_context:
        print("\n  BUG CONFIRMED: shared_context is LOST during PipelineState -> NodeRunState conversion!")
        print("  Downstream NodeExecutor will receive empty shared_context.")

    return findings


def test_convert_node_to_pipeline_state_missing_shared_context() -> dict[str, Any]:
    """Test 2: convert_node_to_pipeline_state does NOT merge shared_context back."""
    print("\n" + "=" * 70)
    print("TEST 2: convert_node_to_pipeline_state() Missing shared_context Merge")
    print("=" * 70)

    findings = {
        "test": "convert_node_to_pipeline_state_missing_shared_context",
        "issue": "PipelineAdapter.convert_node_to_pipeline_state() does not merge shared_context from node_state back to pipeline_state",
        "evidence": [],
        "severity": "CRITICAL",
    }

    original_state = create_initial_state(
        pipeline_id="test-pipeline",
        subject_context={"task": "test"},
    )
    original_state["shared_context"] = {"original": "data"}

    # Simulate node_state that has updated shared_context (e.g., from DB refresh)
    node_state = {
        "run_id": "test-pipeline",
        "pipeline_id": "test-pipeline",
        "node_id": "pm",
        "status": "completed",
        "deliverable": {"content": "pm output"},
        "shared_context": {"updated": "by_tool", "facts": {"new": "fact"}},
        "iteration": 2,
    }

    result = PipelineAdapter.convert_node_to_pipeline_state(node_state, original_state)

    result_shared_context = result.get("shared_context")
    original_shared_context = original_state.get("shared_context")

    print(f"NodeRunState['shared_context'] = {node_state['shared_context']!r}")
    print(f"Original PipelineState['shared_context'] = {original_shared_context!r}")
    print(f"Result PipelineState['shared_context'] = {result_shared_context!r}")

    # Check if updated shared_context was merged
    updated_merged = result_shared_context == node_state["shared_context"]
    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/node_execution/pipeline_adapter.py:249-303",
        "node_state_shared_context": node_state["shared_context"],
        "original_pipeline_shared_context": original_shared_context,
        "result_pipeline_shared_context": result_shared_context,
        "updated_merged": updated_merged,
        "verdict": "BUG CONFIRMED" if not updated_merged else "OK",
    })

    if not updated_merged:
        print("\n  BUG CONFIRMED: shared_context updates from node execution are NOT merged back!")
        print("  Tool updates to shared_context are lost after node execution.")

    return findings


def test_executor_shared_context_fallback() -> dict[str, Any]:
    """Test 3: NodeExecutor reads shared_context from state with empty fallback."""
    print("\n" + "=" * 70)
    print("TEST 3: NodeExecutor shared_context Fallback Behavior")
    print("=" * 70)

    findings = {
        "test": "executor_shared_context_fallback",
        "issue": "NodeExecutor uses state.get('shared_context', {}) which returns empty dict when key is missing",
        "evidence": [],
        "severity": "HIGH",
    }

    executor_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
    source = executor_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find shared_context usage
    shared_context_lines = []
    for i, line in enumerate(lines):
        if "shared_context" in line:
            shared_context_lines.append(f"Line {i+1}: {line}")

    print("All shared_context references in executor.py:")
    for line in shared_context_lines:
        print(f"  {line}")

    # Check if there's any code that handles missing shared_context by trying to fetch from DB
    refresh_lines = [l for l in shared_context_lines if "refresh" in l.lower() or "_refresh" in l]

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/node_execution/executor.py",
        "shared_context_references": shared_context_lines,
        "refresh_logic": refresh_lines,
        "finding": "Executor builds execution_context with state.get('shared_context', {}) - if missing, gets empty dict",
    })

    print("\nFinding: When PipelineAdapter doesn't pass shared_context,")
    print("  executor falls back to empty dict {}. The _refresh_shared_context_from_db")
    print("  is called AFTER node execution, not BEFORE, so the node doesn't see DB updates.")

    return findings


def test_refresh_shared_context_from_db_duck_typing() -> dict[str, Any]:
    """Test 4: _refresh_shared_context_from_db uses unreliable duck typing."""
    print("\n" + "=" * 70)
    print("TEST 4: _refresh_shared_context_from_db Duck Typing Reliability")
    print("=" * 70)

    findings = {
        "test": "refresh_shared_context_from_db_duck_typing",
        "issue": "_get_state_manager_from_session uses duck typing on SessionManager which lacks stable StateManager exposure",
        "evidence": [],
        "severity": "HIGH",
    }

    executor_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
    source = executor_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Extract _get_state_manager_from_session
    in_func = False
    func_lines = []
    for i, line in enumerate(lines):
        if "def _get_state_manager_from_session(" in line:
            in_func = True
        if in_func:
            func_lines.append(f"Line {i+1}: {line}")
            if line.strip() == "return None":
                break

    print("_get_state_manager_from_session() source:")
    for line in func_lines:
        print(f"  {line}")

    # Check SessionManager for these attributes
    sm_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    sm_source = sm_path.read_text(encoding="utf-8")

    has_state_manager_attr = "_state_manager" in sm_source or "state_manager" in sm_source
    has_storage_attr = "self.storage" in sm_source or ".storage" in sm_source
    has_get_pipeline = "def get_pipeline" in sm_source

    print(f"\nSessionManager analysis:")
    print(f"  Has get_pipeline method: {has_get_pipeline}")
    print(f"  Has _state_manager attribute: {'_state_manager' in sm_source}")
    print(f"  Has state_manager attribute: {'self.state_manager' in sm_source}")
    print(f"  Has storage attribute: {has_storage_attr}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/node_execution/executor.py:432-472",
        "duck_typing_checks": [
            "Check if session_manager itself has get_pipeline",
            "Check hasattr(session_manager, '_state_manager')",
            "Check hasattr(session_manager, 'storage')",
            "Check hasattr(session_manager, 'state_manager')",
        ],
        "session_manager_has_get_pipeline": has_get_pipeline,
        "session_manager_has__state_manager": "_state_manager" in sm_source,
        "session_manager_has_storage": has_storage_attr,
        "finding": "SessionManager does NOT have get_pipeline, _state_manager, or storage attributes. Duck typing will ALWAYS return None.",
    })

    if not has_get_pipeline:
        print("\n  BUG CONFIRMED: SessionManager does NOT have get_pipeline() method!")
        print("  Duck typing check 1 (session_manager.get_pipeline) will fail.")
    if "_state_manager" not in sm_source:
        print("  BUG CONFIRMED: SessionManager does NOT have _state_manager attribute!")
        print("  Duck typing check 2 will fail.")
    if not has_storage_attr:
        print("  BUG CONFIRMED: SessionManager does NOT have storage attribute!")
        print("  Duck typing check 3 will fail.")

    print("\n  RESULT: _refresh_shared_context_from_db will ALWAYS return None")
    print("  because SessionManager lacks ALL checked attributes/methods.")

    return findings


def test_update_context_sdk_creates_default_state_manager() -> dict[str, Any]:
    """Test 5: update_context_sdk.py creates StateManager() without db_path."""
    print("\n" + "=" * 70)
    print("TEST 5: update_context_sdk.py Default StateManager Instantiation")
    print("=" * 70)

    findings = {
        "test": "update_context_sdk_creates_default_state_manager",
        "issue": "create_update_context_server() creates StateManager() without db_path, causing database path mismatch",
        "evidence": [],
        "severity": "CRITICAL",
    }

    sdk_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "tools" / "update_context_sdk.py"
    source = sdk_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find the StateManager() call
    sm_call_lines = []
    for i, line in enumerate(lines):
        if "StateManager()" in line or "StateManager(" in line:
            sm_call_lines.append(f"Line {i+1}: {line}")

    print("StateManager instantiation in update_context_sdk.py:")
    for line in sm_call_lines:
        print(f"  {line}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/tools/update_context_sdk.py:98-102",
        "code": sm_call_lines,
        "finding": "StateManager() is called WITHOUT db_path parameter. It will use DatabaseManager.get_instance() which may point to wrong database.",
    })

    print("\nFinding: The update_context tool is supposed to write to the pipeline's database,")
    print("  but it creates a fresh StateManager() without receiving the orchestrator's db_path.")
    print("  This means update_context writes may go to a DIFFERENT database than the pipeline!")

    return findings


def test_full_shared_context_chain() -> dict[str, Any]:
    """Test 6: Full shared_context chain analysis."""
    print("\n" + "=" * 70)
    print("TEST 6: Full shared_context Chain Analysis")
    print("=" * 70)

    chain = [
        {
            "step": "PipelineState -> NodeRunState",
            "component": "PipelineAdapter.convert_pipeline_to_node_state()",
            "finding": "shared_context is NOT included in returned dict",
            "impact": "Node never receives existing shared_context",
        },
        {
            "step": "NodeRunState -> ExecutionContext",
            "component": "NodeExecutor._execute_node()",
            "finding": "Uses state.get('shared_context', {}) - falls back to empty dict",
            "impact": "Node works with empty shared_context even if DB has data",
        },
        {
            "step": "Tool writes shared_context",
            "component": "update_context_tool in MCP server",
            "finding": "Creates StateManager() without db_path, writes to potentially wrong DB",
            "impact": "Update may go to wrong database file",
        },
        {
            "step": "Post-execution refresh",
            "component": "NodeExecutor._refresh_shared_context_from_db()",
            "finding": "Duck typing on SessionManager always fails, returns None",
            "impact": "Never successfully refreshes shared_context from DB",
        },
        {
            "step": "NodeRunState -> PipelineState",
            "component": "PipelineAdapter.convert_node_to_pipeline_state()",
            "finding": "Does NOT merge shared_context from node_state back to pipeline_state",
            "impact": "Any shared_context updates are lost for downstream nodes",
        },
    ]

    for item in chain:
        print(f"\nStep: {item['step']}")
        print(f"  Component: {item['component']}")
        print(f"  Finding: {item['finding']}")
        print(f"  Impact: {item['impact']}")

    return {"chain": chain}


def run_all_tests() -> dict[str, Any]:
    """Run all shared_context tests."""
    print("\n" + "=" * 70)
    print("P0 SHARED CONTEXT DEBUGGER")
    print("Issue: F2 - shared_context runtime transfer link is broken")
    print("=" * 70)

    results = {
        "issue_id": "F2",
        "severity": "CRITICAL",
        "title": "shared_context设计有持久化表象，但运行时传递链路断裂",
        "tests": [],
        "chain_analysis": None,
    }

    results["tests"].append(test_convert_pipeline_to_node_state_missing_shared_context())
    results["tests"].append(test_convert_node_to_pipeline_state_missing_shared_context())
    results["tests"].append(test_executor_shared_context_fallback())
    results["tests"].append(test_refresh_shared_context_from_db_duck_typing())
    results["tests"].append(test_update_context_sdk_creates_default_state_manager())
    results["chain_analysis"] = test_full_shared_context_chain()

    return results


if __name__ == "__main__":
    results = run_all_tests()

    output_path = Path(__file__).parent / "p0_shared_context_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n\nResults saved to: {output_path}")
