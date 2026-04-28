#!/usr/bin/env python3
"""DocuSwarm Context 链路追踪工具 (F2, F3 Research Tool).

该工具用于追踪 shared_context 和 Evaluator 输入契约的数据流，
帮助诊断 context 是否在链路中丢失。

用法:
    python tools/docuswarm_context_tracer.py --check-shared-context
    python tools/docuswarm_context_tracer.py --check-evaluator-input
    python tools/docuswarm_context_tracer.py --trace-all
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent / "autoBMAD" / "docuswarm"


def analyze_file(filepath: Path, patterns: dict[str, str]) -> dict[str, Any]:
    """分析文件中的特定模式.
    
    Args:
        filepath: 文件路径
        patterns: 要查找的模式字典 {名称: 模式}
        
    Returns:
        分析结果
    """
    results = {
        "file": str(filepath),
        "found_patterns": {},
        "issues": [],
    }
    
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # 查找赋值语句
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Constant) and target.value in patterns:
                        results["found_patterns"][target.value] = ast.dump(node.value)
            
            # 查找字典键
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if isinstance(key, ast.Constant) and key.value in patterns:
                        results["found_patterns"][key.value] = "found"
        
        # 文本搜索特定模式
        for name, pattern in patterns.items():
            if pattern in content:
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if pattern in line:
                        results["issues"].append({
                            "pattern": name,
                            "line": i,
                            "code": line.strip(),
                        })
                        
    except Exception as e:
        results["error"] = str(e)
    
    return results


def check_shared_context_flow() -> dict[str, Any]:
    """检查 shared_context 数据流.
    
    Returns:
        分析结果
    """
    results = {
        "title": "Shared Context 链路分析 (F2)",
        "stages": {},
        "issues": [],
    }
    
    # Stage 1: StateManager 写入
    state_manager_file = PROJECT_ROOT / "storage" / "state_manager.py"
    if state_manager_file.exists():
        content = state_manager_file.read_text()
        if "async def update_shared_context" in content:
            results["stages"]["state_manager_write"] = {
                "status": "✅ 已实现",
                "file": str(state_manager_file),
            }
        else:
            results["stages"]["state_manager_write"] = {
                "status": "❌ 未找到",
                "file": str(state_manager_file),
            }
    
    # Stage 2: ContextManager 传递
    isolation_file = PROJECT_ROOT / "context" / "isolation.py"
    if isolation_file.exists():
        content = isolation_file.read_text()
        if 'execution_context.get("shared_context", {})' in content:
            results["stages"]["context_manager_pass"] = {
                "status": "✅ 已传递",
                "file": str(isolation_file),
            }
        else:
            results["stages"]["context_manager_pass"] = {
                "status": "❌ 未传递",
                "file": str(isolation_file),
            }
    
    # Stage 3: IndependentAgent 消费 - 问题核心
    independent_file = PROJECT_ROOT / "agents" / "independent.py"
    if independent_file.exists():
        content = independent_file.read_text()
        
        # 检查是否读取 shared_context
        if 'agent_input.get("shared_context"' in content:
            results["stages"]["agent_consume"] = {
                "status": "✅ 已读取",
                "file": str(independent_file),
            }
        else:
            results["stages"]["agent_consume"] = {
                "status": "❌ 未读取",
                "file": str(independent_file),
                "issue": "execute_with_input() 未从 agent_input 读取 shared_context",
            }
            results["issues"].append({
                "file": str(independent_file),
                "issue": "shared_context 在消费层丢失",
                "fix": "修改 shared_context={} 为 shared_context=agent_input.get('shared_context', {})",
            })
        
        # 检查是否重置为空
        if "shared_context={}" in content:
            # 找到行号
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "shared_context={}" in line and "#" not in line:
                    results["issues"].append({
                        "file": str(independent_file),
                        "line": i,
                        "code": line.strip(),
                        "issue": "shared_context 被重置为空字典",
                    })
    
    return results


def check_evaluator_input_contract() -> dict[str, Any]:
    """检查 Evaluator 输入契约.
    
    Returns:
        分析结果
    """
    results = {
        "title": "Evaluator 输入契约分析 (F3)",
        "stages": {},
        "issues": [],
    }
    
    # Stage 1: ContextManager 构建
    isolation_file = PROJECT_ROOT / "context" / "isolation.py"
    if isolation_file.exists():
        content = isolation_file.read_text()
        checks = {
            "file_path required": 'file_path = deliverable.get("file_path")' in content,
            "read file": "path.read_text" in content,
            "original_context_summary": "original_context_summary" in content,
        }
        results["stages"]["context_manager_build"] = {
            "status": "✅ 已实现" if all(checks.values()) else "⚠️  部分实现",
            "checks": checks,
        }
    
    # Stage 2: EvaluatorAgent 消费 - 问题核心
    evaluator_file = PROJECT_ROOT / "agents" / "evaluator.py"
    if evaluator_file.exists():
        content = evaluator_file.read_text()
        
        # 检查是否读取 original_context_summary
        if 'agent_input.get("original_context_summary"' in content:
            results["stages"]["agent_consume"] = {
                "status": "✅ 已读取",
                "file": str(evaluator_file),
            }
        else:
            results["stages"]["agent_consume"] = {
                "status": "❌ 未读取",
                "file": str(evaluator_file),
                "issue": "execute_with_input() 未从 agent_input 读取 original_context_summary",
            }
            results["issues"].append({
                "file": str(evaluator_file),
                "issue": "original_context_summary 在消费层丢失",
                "fix": "修改 original_context={} 为 original_context={'content': agent_input.get('original_context_summary', '')}",
            })
        
        # 检查是否重置为空
        if "original_context={}" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "original_context={}" in line:
                    results["issues"].append({
                        "file": str(evaluator_file),
                        "line": i,
                        "code": line.strip(),
                        "issue": "original_context 被重置为空字典",
                    })
    
    return results


def print_shared_context_analysis(results: dict[str, Any]) -> None:
    """打印 shared_context 分析结果."""
    print("=" * 70)
    print(results["title"])
    print("=" * 70)
    print()
    
    print("链路阶段:")
    print("-" * 70)
    for stage, info in results["stages"].items():
        print(f"  {stage}:")
        print(f"    状态: {info['status']}")
        if "file" in info:
            print(f"    文件: {info['file']}")
        if "checks" in info:
            for check, status in info["checks"].items():
                symbol = "✅" if status else "❌"
                print(f"    {symbol} {check}")
        print()
    
    if results["issues"]:
        print("⚠️  发现的问题:")
        print("-" * 70)
        for issue in results["issues"]:
            print(f"  文件: {issue['file']}")
            if "line" in issue:
                print(f"  行号: {issue['line']}")
            print(f"  问题: {issue['issue']}")
            if "code" in issue:
                print(f"  代码: {issue['code']}")
            if "fix" in issue:
                print(f"  建议修复: {issue['fix']}")
            print()


def print_evaluator_analysis(results: dict[str, Any]) -> None:
    """打印 Evaluator 分析结果."""
    print("=" * 70)
    print(results["title"])
    print("=" * 70)
    print()
    
    print("链路阶段:")
    print("-" * 70)
    for stage, info in results["stages"].items():
        print(f"  {stage}:")
        print(f"    状态: {info['status']}")
        if "file" in info:
            print(f"    文件: {info['file']}")
        if "checks" in info:
            for check, status in info["checks"].items():
                symbol = "✅" if status else "❌"
                print(f"    {symbol} {check}")
        print()
    
    if results["issues"]:
        print("⚠️  发现的问题:")
        print("-" * 70)
        for issue in results["issues"]:
            print(f"  文件: {issue['file']}")
            if "line" in issue:
                print(f"  行号: {issue['line']}")
            print(f"  问题: {issue['issue']}")
            if "code" in issue:
                print(f"  代码: {issue['code']}")
            if "fix" in issue:
                print(f"  建议修复: {issue['fix']}")
            print()


def main() -> int:
    """主函数."""
    parser = argparse.ArgumentParser(
        description="DocuSwarm Context 链路追踪工具"
    )
    parser.add_argument(
        "--check-shared-context",
        action="store_true",
        help="检查 shared_context 链路 (F2)",
    )
    parser.add_argument(
        "--check-evaluator-input",
        action="store_true",
        help="检查 Evaluator 输入契约 (F3)",
    )
    parser.add_argument(
        "--trace-all",
        action="store_true",
        help="检查所有 Context 链路",
    )
    
    args = parser.parse_args()
    
    if args.trace_all or (not args.check_shared_context and not args.check_evaluator_input):
        args.check_shared_context = True
        args.check_evaluator_input = True
    
    if args.check_shared_context:
        results = check_shared_context_flow()
        print_shared_context_analysis(results)
        print()
    
    if args.check_evaluator_input:
        results = check_evaluator_input_contract()
        print_evaluator_analysis(results)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
