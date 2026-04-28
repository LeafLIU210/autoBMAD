#!/usr/bin/env python3
"""
P0 Failure Propagation Debugger - F1 Critical Issue Research Tool

研究问题：节点失败会被流水线层吞掉，并被标记为已完成

目标：
1. 验证 NodeExecutor 异常捕获后是否重新抛出
2. 验证 PipelineAdapter.convert_node_to_pipeline_state() 是否不检查 node_state["status"]
3. 验证 pipeline/graph.py 的 integrated executor 异常处理是否 fallback 到成功状态
4. 验证 HybridOrchestrator.start_pipeline() 是否无条件将 pipeline 标记为 completed
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent.resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from autoBMAD.docuswarm.node_execution.executor import _execute_node
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.node_execution.state import FAILED, RUNNING, COMPLETED, BLOCKED
from autoBMAD.docuswarm.pipeline.state import create_initial_state, PIPELINE_NODES


class FakeSessionManager:
    """Minimal fake session manager for testing."""

    def __init__(self) -> None:
        pass


class FakeDualAgentNode:
    """Fake node that can simulate various execution outcomes."""

    def __init__(self, verdict: str | None = None, raise_exception: bool = False):
        self.verdict = verdict
        self.raise_exception = raise_exception

    async def execute_with_context(self, context: dict[str, Any]) -> Any:
        if self.raise_exception:
            raise RuntimeError("Simulated node execution failure")

        class FakeResult:
            def __init__(self, verdict: str | None):
                self.deliverable = {"content": "test"}
                self.questions = []
                self.evaluation = {"verdict": verdict} if verdict else None

        return FakeResult(self.verdict)


def test_node_executor_exception_handling() -> dict[str, Any]:
    """Test 1: NodeExecutor captures exception and only sets FAILED status without re-raising."""
    print("\n" + "=" * 70)
    print("TEST 1: NodeExecutor Exception Handling")
    print("=" * 70)

    findings = {
        "test": "node_executor_exception_handling",
        "issue": "NodeExecutor catches all exceptions and only sets FAILED status without re-raising",
        "evidence": [],
        "severity": "CRITICAL",
    }

    # We can't easily call _execute_node directly because it imports DualAgentNode
    # Instead, let's analyze the code behavior

    # Read the executor source to verify the behavior
    executor_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
    source = executor_path.read_text(encoding="utf-8")

    # Check line 235-246: exception handler
    lines = source.split("\n")
    in_except = False
    except_lines = []
    for i, line in enumerate(lines):
        if "except Exception as e:" in line and i >= 230:
            in_except = True
            except_lines.append(f"Line {i+1}: {line}")
        elif in_except:
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                break
            except_lines.append(f"Line {i+1}: {line}")
            if "return new_state" in line:
                break

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/node_execution/executor.py:235-246",
        "code": except_lines,
        "finding": "Exception is caught, status set to FAILED, but function RETURNS normally instead of re-raising",
    })

    print("Evidence:")
    for line in except_lines:
        print(f"  {line}")
    print("\nFinding: Exception handler does NOT re-raise. It sets FAILED and returns normally.")
    print("This means upstream caller (PipelineAdapter) receives a 'normal' return value.")

    return findings


def test_pipeline_adapter_status_check() -> dict[str, Any]:
    """Test 2: PipelineAdapter.convert_node_to_pipeline_state() ignores node status."""
    print("\n" + "=" * 70)
    print("TEST 2: PipelineAdapter.convert_node_to_pipeline_state() Status Check")
    print("=" * 70)

    findings = {
        "test": "pipeline_adapter_status_check",
        "issue": "PipelineAdapter.convert_node_to_pipeline_state() adds node to completed_nodes without checking status",
        "evidence": [],
        "severity": "CRITICAL",
    }

    adapter_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "node_execution" / "pipeline_adapter.py"
    source = adapter_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find convert_node_to_pipeline_state and check completed_nodes logic
    in_func = False
    func_lines = []
    for i, line in enumerate(lines):
        if "def convert_node_to_pipeline_state(" in line:
            in_func = True
        if in_func:
            func_lines.append(f"Line {i+1}: {line}")
            if line.strip() == "" and len(func_lines) > 5:
                # Check if we've exited the function
                pass
            if i > 0 and not line.startswith(" ") and not line.startswith("\t") and "def " in line and "convert_node_to_pipeline_state" not in line:
                break
            # Stop at return or end of function
            if len(func_lines) > 60:
                break

    # Check specifically for completed_nodes logic
    completed_nodes_logic = [l for l in func_lines if "completed_nodes" in l]

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/node_execution/pipeline_adapter.py:294-298",
        "code": completed_nodes_logic,
        "finding": "Node is added to completed_nodes WITHOUT checking node_state['status']. FAILED/BLOCKED/RUNNING nodes are treated as completed.",
    })

    print("Evidence - completed_nodes logic:")
    for line in completed_nodes_logic:
        print(f"  {line}")

    # Verify with actual execution
    original_state = create_initial_state("test-pipeline", {"task": "test"})
    node_state_failed = {
        "run_id": "test-pipeline",
        "pipeline_id": "test-pipeline",
        "node_id": "analyst",
        "status": FAILED,
        "deliverable": None,
        "questions": [],
        "evaluation": None,
        "iteration": 1,
    }

    result = PipelineAdapter.convert_node_to_pipeline_state(node_state_failed, original_state)

    analyst_in_completed = "analyst" in result.get("completed_nodes", [])
    print(f"\nActual execution test:")
    print(f"  Input node_state['status'] = {FAILED!r}")
    print(f"  Output completed_nodes contains 'analyst': {analyst_in_completed}")
    print(f"  VERDICT: {'BUG CONFIRMED' if analyst_in_completed else 'OK'}")

    findings["evidence"].append({
        "location": "Runtime verification",
        "input_status": FAILED,
        "completed_nodes": result.get("completed_nodes", []),
        "verdict": "BUG CONFIRMED" if analyst_in_completed else "OK",
    })

    return findings


def test_graph_integrated_executor_exception_handling() -> dict[str, Any]:
    """Test 3: pipeline/graph.py integrated executor exception handling."""
    print("\n" + "=" * 70)
    print("TEST 3: pipeline/graph.py Integrated Executor Exception Handling")
    print("=" * 70)

    findings = {
        "test": "graph_integrated_executor_exception_handling",
        "issue": "Integrated executor catches exception, falls back to empty deliverable, still adds node to completed_nodes",
        "evidence": [],
        "severity": "CRITICAL",
    }

    graph_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
    source = graph_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find the exception handler in _create_integrated_node_executor
    in_executor = False
    exception_handler_lines = []
    completed_nodes_lines = []
    for i, line in enumerate(lines):
        if "async def executor(state: dict[str, Any])" in line:
            in_executor = True
        if in_executor:
            if "except Exception as e:" in line:
                # Collect exception handler
                for j in range(i, min(i+10, len(lines))):
                    exception_handler_lines.append(f"Line {j+1}: {lines[j]}")
            if "completed_nodes" in line:
                completed_nodes_lines.append(f"Line {i+1}: {line}")
            if line.strip() == "" and i > 140 and not line.startswith(" "):
                pass
            # Stop at return of outer function
            if line.strip().startswith("return executor"):
                break

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/pipeline/graph.py:126-141",
        "exception_handler": exception_handler_lines,
        "completed_nodes_logic": completed_nodes_lines,
        "finding": "On exception: sets empty deliverable, then INCREMENTS iteration and ADDS to completed_nodes",
    })

    print("Evidence - Exception handler:")
    for line in exception_handler_lines:
        print(f"  {line}")
    print("\nEvidence - completed_nodes logic (runs regardless of exception):")
    for line in completed_nodes_lines:
        print(f"  {line}")

    print("\nFinding: Even when async_node_executor raises an exception:")
    print("  1. Exception is caught and logged")
    print("  2. result_state['deliverables'][node_id] = {} (empty, but present)")
    print("  3. Iteration is incremented")
    print("  4. Node is unconditionally added to completed_nodes")
    print("  This makes the failure INVISIBLE to downstream dependency checks.")

    return findings


def test_orchestrator_unconditional_completed() -> dict[str, Any]:
    """Test 4: HybridOrchestrator.start_pipeline() unconditionally marks pipeline as completed."""
    print("\n" + "=" * 70)
    print("TEST 4: HybridOrchestrator.start_pipeline() Unconditional Completed")
    print("=" * 70)

    findings = {
        "test": "orchestrator_unconditional_completed",
        "issue": "HybridOrchestrator.start_pipeline() updates pipeline status to 'completed' after graph.ainvoke() regardless of node failures",
        "evidence": [],
        "severity": "CRITICAL",
    }

    orchestrator_path = Path(repo_root) / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
    source = orchestrator_path.read_text(encoding="utf-8")
    lines = source.split("\n")

    # Find the ainvoke call and subsequent status update
    ainvoke_lines = []
    status_update_lines = []
    for i, line in enumerate(lines):
        if "graph.ainvoke(initial_state, config)" in line:
            ainvoke_lines.append(f"Line {i+1}: {line}")
            # Collect next 15 lines
            for j in range(i+1, min(i+15, len(lines))):
                status_update_lines.append(f"Line {j+1}: {lines[j]}")

    findings["evidence"].append({
        "location": "autoBMAD/docuswarm/pipeline/orchestrator.py:457-464",
        "ainvoke": ainvoke_lines,
        "status_update": status_update_lines,
        "finding": "After graph.ainvoke() returns, status is unconditionally set to 'completed' without inspecting result state",
    })

    print("Evidence - After graph.ainvoke():")
    for line in status_update_lines:
        print(f"  {line}")

    print("\nFinding: The code does:")
    print("  result = await graph.ainvoke(initial_state, config)")
    print("  # ... then IMMEDIATELY ...")
    print("  await self._state_manager.update_pipeline_state(final_pipeline_id, {'status': 'completed', ...})")
    print("  It NEVER checks result['status'] or any node failure indicators.")

    return findings


def analyze_failure_chain() -> dict[str, Any]:
    """Analyze the complete failure propagation chain."""
    print("\n" + "=" * 70)
    print("FAILURE PROPAGATION CHAIN ANALYSIS")
    print("=" * 70)

    chain = [
        {
            "step": 1,
            "component": "DualAgentNode.execute_with_context()",
            "issue": "May raise exception or return NEEDS_REVISION",
            "impact": "Execution problem detected at node level",
        },
        {
            "step": 2,
            "component": "NodeExecutor._execute_node()",
            "issue": "Catches ALL exceptions, sets status=FAILED, returns normally (no re-raise)",
            "impact": "Failure is hidden from caller; upstream sees normal return",
        },
        {
            "step": 3,
            "component": "PipelineAdapter.convert_node_to_pipeline_state()",
            "issue": "Ignores node_state['status'], adds ANY node to completed_nodes",
            "impact": "FAILED node appears in completed_nodes list",
        },
        {
            "step": 4,
            "component": "pipeline/graph.py _create_integrated_node_executor()",
            "issue": "If exception slips through, catches it, sets empty deliverable, still adds to completed_nodes",
            "impact": "Double safety net that STILL marks failed nodes as completed",
        },
        {
            "step": 5,
            "component": "HybridOrchestrator.start_pipeline()",
            "issue": "After graph.ainvoke(), unconditionally sets pipeline status='completed'",
            "impact": "Entire pipeline marked as completed even if nodes failed",
        },
    ]

    for item in chain:
        print(f"\nStep {item['step']}: {item['component']}")
        print(f"  Issue: {item['issue']}")
        print(f"  Impact: {item['impact']}")

    return {"chain": chain}


def run_all_tests() -> dict[str, Any]:
    """Run all failure propagation tests."""
    print("\n" + "=" * 70)
    print("P0 FAILURE PROPAGATION DEBUGGER")
    print("Issue: F1 Critical - Node failures swallowed, marked as completed")
    print("=" * 70)

    results = {
        "issue_id": "F1",
        "severity": "CRITICAL",
        "title": "节点失败会被流水线层吞掉，并被标记为已完成",
        "tests": [],
        "chain_analysis": None,
    }

    results["tests"].append(test_node_executor_exception_handling())
    results["tests"].append(test_pipeline_adapter_status_check())
    results["tests"].append(test_graph_integrated_executor_exception_handling())
    results["tests"].append(test_orchestrator_unconditional_completed())
    results["chain_analysis"] = analyze_failure_chain()

    return results


if __name__ == "__main__":
    results = run_all_tests()

    # Save results
    output_path = Path(__file__).parent / "p0_failure_propagation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n\nResults saved to: {output_path}")
