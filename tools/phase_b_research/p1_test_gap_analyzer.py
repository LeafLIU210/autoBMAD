"""
Phase B - P1-3 测试缺口分析工具
================================
分析主路径测试覆盖缺口，为 start/resume/cancel/escalation 提供测试建议

使用方法:
    python tools/phase_b_research/p1_test_gap_analyzer.py
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
AUTO_BMAD = PROJECT_ROOT / "autoBMAD" / "docuswarm"
TESTS_DIR = PROJECT_ROOT / "tests"


def find_test_files() -> list[Path]:
    """Find all test files in the tests directory."""
    test_files = []
    if TESTS_DIR.exists():
        test_files = list(TESTS_DIR.rglob("test_*.py"))
    return test_files


def analyze_existing_tests() -> dict[str, Any]:
    """Analyze existing test coverage."""
    print("\n[Phase B - P1-3] 分析现有测试...")
    
    test_files = find_test_files()
    findings = {
        "total_test_files": len(test_files),
        "test_files": [str(f.relative_to(PROJECT_ROOT)) for f in test_files],
        "orchestrator_tests": [],
        "pipeline_service_tests": [],
        "dual_agent_tests": [],
        "escalation_tests": [],
    }
    
    # Categorize tests
    for test_file in test_files:
        content = test_file.read_text(encoding="utf-8")
        rel_path = str(test_file.relative_to(PROJECT_ROOT))
        
        if "orchestrat" in content.lower():
            findings["orchestrator_tests"].append(rel_path)
        if "pipeline_service" in content.lower() or "pipeline" in rel_path.lower():
            findings["pipeline_service_tests"].append(rel_path)
        if "dual_agent" in content.lower():
            findings["dual_agent_tests"].append(rel_path)
        if "escalat" in content.lower():
            findings["escalation_tests"].append(rel_path)
    
    print(f"  总测试文件数: {findings['total_test_files']}")
    print(f"  Orchestrator 相关测试: {len(findings['orchestrator_tests'])}")
    for t in findings["orchestrator_tests"]:
        print(f"    - {t}")
    print(f"  Pipeline Service 相关测试: {len(findings['pipeline_service_tests'])}")
    for t in findings["pipeline_service_tests"]:
        print(f"    - {t}")
    print(f"  Dual Agent 相关测试: {len(findings['dual_agent_tests'])}")
    for t in findings["dual_agent_tests"]:
        print(f"    - {t}")
    print(f"  Escalation 相关测试: {len(findings['escalation_tests'])}")
    for t in findings["escalation_tests"]:
        print(f"    - {t}")
    
    return findings


def analyze_orchestrator_main_paths() -> dict[str, Any]:
    """Analyze orchestrator main paths that need testing."""
    print("\n[Phase B - P1-3] 分析 Orchestrator 主路径...")
    
    path = AUTO_BMAD / "pipeline" / "orchestrator.py"
    if not path.exists():
        return {"error": "orchestrator.py not found"}
    
    tree = ast.parse(path.read_text(encoding="utf-8"))
    
    findings = {
        "file": "autoBMAD/docuswarm/pipeline/orchestrator.py",
        "main_methods": [],
        "methods_needing_tests": [],
    }
    
    key_methods = [
        "start_pipeline",
        "resume_pipeline",
        "restart_from_node",
        "cancel_pipeline",
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
            if node.name in key_methods:
                method_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "complexity": estimate_complexity(node),
                }
                findings["main_methods"].append(method_info)
    
    print(f"  发现 {len(findings['main_methods'])} 个关键方法:")
    for method in findings["main_methods"]:
        async_marker = "async" if method["is_async"] else "sync"
        print(f"    - {method['name']} (第 {method['line']} 行, {async_marker}, 复杂度: {method['complexity']})")
    
    return findings


def estimate_complexity(node: ast.AsyncFunctionDef | ast.FunctionDef) -> str:
    """Estimate method complexity based on AST."""
    try_nodes = len([n for n in ast.walk(node) if isinstance(n, ast.Try)])
    if_nodes = len([n for n in ast.walk(node) if isinstance(n, ast.If)])
    loop_nodes = len([n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))])
    
    score = try_nodes * 2 + if_nodes + loop_nodes * 1.5
    
    if score > 20:
        return "高"
    elif score > 10:
        return "中"
    else:
        return "低"


def analyze_pipeline_service_methods() -> dict[str, Any]:
    """Analyze PipelineService methods."""
    print("\n[Phase B - P1-3] 分析 PipelineService 方法...")
    
    path = AUTO_BMAD / "cli" / "services" / "pipeline_service.py"
    if not path.exists():
        return {"error": "pipeline_service.py not found"}
    
    tree = ast.parse(path.read_text(encoding="utf-8"))
    
    findings = {
        "file": "autoBMAD/docuswarm/cli/services/pipeline_service.py",
        "methods": [],
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                findings["methods"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                })
    
    print(f"  发现 {len(findings['methods'])} 个公开方法:")
    for method in findings["methods"]:
        async_marker = "async" if method["is_async"] else "sync"
        print(f"    - {method['name']} (第 {method['line']} 行, {async_marker})")
    
    return findings


def analyze_escalation_handler() -> dict[str, Any]:
    """Analyze EscalationHandler for test requirements."""
    print("\n[Phase B - P1-3] 分析 EscalationHandler...")
    
    path = AUTO_BMAD / "pipeline" / "escalation.py"
    if not path.exists():
        return {"error": "escalation.py not found"}
    
    tree = ast.parse(path.read_text(encoding="utf-8"))
    
    findings = {
        "file": "autoBMAD/docuswarm/pipeline/escalation.py",
        "methods": [],
        "critical_paths": [],
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            findings["methods"].append({
                "name": node.name,
                "line": node.lineno,
                "is_async": True,
            })
            if node.name in ["escalate", "resolve"]:
                findings["critical_paths"].append(node.name)
    
    print(f"  发现 {len(findings['methods'])} 个异步方法:")
    for method in findings["methods"]:
        critical = " (关键路径)" if method["name"] in findings["critical_paths"] else ""
        print(f"    - {method['name']} (第 {method['line']} 行){critical}")
    
    return findings


def generate_smoke_test_specs() -> dict[str, Any]:
    """Generate smoke test specifications for main paths."""
    print("\n[Phase B - P1-3] 生成冒烟测试规范...")
    
    specs = {
        "test_start_pipeline": {
            "file": "tests/smoke/test_start_pipeline.py",
            "description": "测试主启动路径",
            "scenarios": [
                {
                    "name": "正常启动",
                    "setup": "创建有效上下文文件",
                    "action": "调用 orchestrator.start_pipeline()",
                    "expected": "返回 pipeline_id, 状态为 running 或 completed",
                },
                {
                    "name": "无效上下文",
                    "setup": "创建无效上下文文件",
                    "action": "调用 start_pipeline()",
                    "expected": "抛出 ContextValidationError",
                },
                {
                    "name": "自定义 pipeline_id",
                    "setup": "提供自定义 pipeline_id",
                    "action": "调用 start_pipeline(pipeline_id='custom-id')",
                    "expected": "使用自定义 ID 创建 pipeline",
                },
            ],
            "mocks_needed": [
                "StateManager",
                "ContextValidator",
                "SessionManager",
                "LangGraph checkpointer",
            ],
        },
        "test_resume_pipeline": {
            "file": "tests/smoke/test_resume_pipeline.py",
            "description": "测试恢复路径",
            "scenarios": [
                {
                    "name": "正常恢复",
                    "setup": "创建 paused 状态的 pipeline",
                    "action": "调用 orchestrator.resume_pipeline()",
                    "expected": "pipeline 恢复执行，返回最终状态",
                },
                {
                    "name": "已完成的 pipeline",
                    "setup": "创建 completed 状态的 pipeline",
                    "action": "调用 resume_pipeline()",
                    "expected": "抛出 PipelineAlreadyCompletedError",
                },
                {
                    "name": "不存在的 pipeline",
                    "setup": "使用不存在的 pipeline_id",
                    "action": "调用 resume_pipeline()",
                    "expected": "抛出 PipelineNotFoundError",
                },
            ],
            "mocks_needed": [
                "StateManager (已有 paused 状态)",
                "Checkpoint 恢复",
            ],
        },
        "test_cancel_pipeline": {
            "file": "tests/smoke/test_cancel_pipeline.py",
            "description": "测试取消路径",
            "scenarios": [
                {
                    "name": "正常取消",
                    "setup": "创建 running 状态的 pipeline",
                    "action": "调用 PipelineService.cancel()",
                    "expected": "状态变为 cancelled",
                },
                {
                    "name": "取消已完成 pipeline",
                    "setup": "创建 completed 状态的 pipeline",
                    "action": "调用 cancel()",
                    "expected": "抛出 ValueError",
                },
                {
                    "name": "批量取消",
                    "setup": "创建多个 running pipeline",
                    "action": "调用 PipelineService.cancel_all()",
                    "expected": "所有 pipeline 状态变为 cancelled",
                },
            ],
            "mocks_needed": [
                "StateManager (返回各种状态)",
            ],
        },
        "test_escalation": {
            "file": "tests/smoke/test_escalation.py",
            "description": "测试升级路径",
            "scenarios": [
                {
                    "name": "触发升级",
                    "setup": "配置低质量阈值，模拟 BLOCKED 节点",
                    "action": "节点执行达到阈值",
                    "expected": "调用 EscalationHandler.escalate(), 状态变为 paused",
                },
                {
                    "name": "解决升级",
                    "setup": "创建 escalated 状态的 pipeline",
                    "action": "调用 EscalationHandler.resolve()",
                    "expected": "pipeline 可恢复执行",
                },
            ],
            "mocks_needed": [
                "EscalationHandler",
                "StateManager",
                "QualityGate",
            ],
            "note": "需要确保 escalate() 被 await",
        },
    }
    
    for test_name, spec in specs.items():
        print(f"\n  {test_name}:")
        print(f"    文件: {spec['file']}")
        print(f"    描述: {spec['description']}")
        print(f"    场景:")
        for scenario in spec['scenarios']:
            print(f"      - {scenario['name']}: {scenario['expected']}")
    
    return specs


def create_test_implementation_plan() -> dict[str, Any]:
    """Create a detailed implementation plan for tests."""
    return {
        "phase_b_test_tasks": [
            {
                "priority": "P0",
                "file": "tests/smoke/test_start_pipeline.py",
                "estimated_effort": "4 小时",
                "dependencies": ["修复 orchestrator.py asyncio.run 问题"],
                "key_assertions": [
                    "assert pipeline_id is not None",
                    "assert status in ['running', 'completed']",
                    "mock_context_validator.validate_context_with_llm.assert_called_once()",
                ],
            },
            {
                "priority": "P0",
                "file": "tests/smoke/test_resume_pipeline.py",
                "estimated_effort": "3 小时",
                "dependencies": ["修复 orchestrator.py asyncio.run 问题"],
                "key_assertions": [
                    "assert result['status'] == 'completed'",
                    "mock_checkpoint.get_latest.assert_called()",
                ],
            },
            {
                "priority": "P1",
                "file": "tests/smoke/test_cancel_pipeline.py",
                "estimated_effort": "2 小时",
                "dependencies": ["移除 _run_async bridge"],
                "key_assertions": [
                    "assert cancelled is True",
                    "assert pipeline['status'] == 'cancelled'",
                ],
            },
            {
                "priority": "P1",
                "file": "tests/smoke/test_escalation.py",
                "estimated_effort": "4 小时",
                "dependencies": ["修复 dual_agent.py escalate await 问题"],
                "key_assertions": [
                    "mock_escalation_handler.escalate.assert_awaited_once()",
                    "assert escalation_record.status == 'pending'",
                ],
            },
        ],
        "common_fixtures": [
            "tests/conftest.py: mock_state_manager",
            "tests/conftest.py: mock_context_validator",
            "tests/conftest.py: mock_session_manager",
            "tests/conftest.py: mock_checkpointer",
        ],
        "verification": [
            "pytest tests/smoke/ -v 应该全部通过",
            "coverage run -m pytest tests/smoke/",
            "coverage report -m autoBMAD/docuswarm/pipeline/orchestrator.py 应该 > 40%",
        ],
    }


def main() -> int:
    """Run all Phase B test gap analysis."""
    print("=" * 70)
    print("Phase B 测试缺口分析")
    print("=" * 70)
    print("目标: 分析主路径测试缺口，为 Phase B 提供测试补充计划")
    
    report = {
        "title": "Phase B 测试缺口深度分析报告",
        "description": "针对 Finding P1-3 的测试覆盖分析和补充计划",
        "timestamp": "2026-04-04",
        "findings": {},
    }
    
    # Analyze existing tests
    report["findings"]["existing_tests"] = analyze_existing_tests()
    
    # Analyze orchestrator
    report["findings"]["orchestrator_paths"] = analyze_orchestrator_main_paths()
    
    # Analyze pipeline service
    report["findings"]["pipeline_service"] = analyze_pipeline_service_methods()
    
    # Analyze escalation
    report["findings"]["escalation"] = analyze_escalation_handler()
    
    # Generate smoke test specs
    report["smoke_test_specs"] = generate_smoke_test_specs()
    
    # Implementation plan
    report["implementation_plan"] = create_test_implementation_plan()
    
    # Write report
    output_path = PROJECT_ROOT / "docs" / "research" / "phase_b_test_gap_analysis.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[完成] 分析报告已保存: {output_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Phase B 测试缺口摘要")
    print("=" * 70)
    
    existing = report["findings"]["existing_tests"]
    print(f"\n现有测试:")
    print(f"  - 总测试文件: {existing['total_test_files']}")
    print(f"  - Orchestrator 测试: {len(existing['orchestrator_tests'])}")
    print(f"  - Escalation 测试: {len(existing['escalation_tests'])}")
    
    print(f"\n需要补充的冒烟测试:")
    for task in report["implementation_plan"]["phase_b_test_tasks"]:
        print(f"  [{task['priority']}] {task['file']}")
        print(f"    预计工作量: {task['estimated_effort']}")
        if task['dependencies']:
            print(f"    依赖: {', '.join(task['dependencies'])}")
    
    print("\n" + "=" * 70)
    print("关键路径测试建议:")
    print("  1. start_pipeline: 验证正常启动、无效上下文、自定义 ID")
    print("  2. resume_pipeline: 验证恢复、已完成 pipeline、不存在 pipeline")
    print("  3. cancel_pipeline: 验证取消、批量取消、已完成 pipeline 处理")
    print("  4. escalation: 验证升级触发、升级解决 (需确保 await)")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
