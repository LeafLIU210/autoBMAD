#!/usr/bin/env python3
"""
Finding 3 深度调试工具: 双轨节点执行器分析

问题: 节点执行主干并未收敛，存在两套并行执行器

研究目标:
1. 比较 node_execution/executor.py 和 nodes/dual_agent.py 的实现
2. 分析两套 executor 的差异和冲突
3. 确定唯一主执行路径
4. 提出统一和移除 legacy 的方案
"""

from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoBMAD.docuswarm.node_execution import executor as node_executor_module
from autoBMAD.docuswarm.nodes import dual_agent as dual_agent_module


class DualExecutorDebugger:
    """双轨执行器调试器."""

    def __init__(self):
        self.findings: list[dict[str, Any]] = []

    def extract_functions(self, module, function_names: list[str]) -> dict[str, Any]:
        """从模块中提取指定函数的信息."""
        results = {}
        source_path = Path(module.__file__)
        source = source_path.read_text(encoding="utf-8")

        for func_name in function_names:
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                if callable(func):
                    sig = inspect.signature(func)
                    results[func_name] = {
                        "signature": str(sig),
                        "source_file": str(source_path),
                        "line_number": self._get_function_line_number(source, func_name),
                    }
        return results

    def _get_function_line_number(self, source: str, func_name: str) -> int | None:
        """获取函数定义的行号."""
        lines = source.split("\n")
        for i, line in enumerate(lines):
            if f"def {func_name}(" in line or f"async def {func_name}(" in line:
                return i + 1
        return None

    def analyze_executor_differences(self) -> dict[str, Any]:
        """分析两套 executor 的差异."""
        print("=" * 70)
        print("FINDING 3: 双轨节点执行器分析")
        print("=" * 70)

        print("\n[1] 执行器函数对比:")

        # 要比较的函数
        functions_to_compare = [
            "create_node_executor",
            "_execute_node",
            "_get_config",
        ]

        # 提取函数信息
        executor_funcs = self.extract_functions(node_executor_module, functions_to_compare)
        dual_agent_funcs = self.extract_functions(dual_agent_module, functions_to_compare)

        comparison = {}

        for func_name in functions_to_compare:
            print(f"\n    函数: {func_name}")

            exec_info = executor_funcs.get(func_name)
            dual_info = dual_agent_funcs.get(func_name)

            if exec_info:
                print(f"      node_execution/executor.py:")
                print(f"        行号: {exec_info['line_number']}")
                print(f"        签名: {exec_info['signature']}")

            if dual_info:
                print(f"      nodes/dual_agent.py:")
                print(f"        行号: {dual_info['line_number']}")
                print(f"        签名: {dual_info['signature']}")

            if exec_info and dual_info:
                comparison[func_name] = {
                    "in_both": True,
                    "executor_line": exec_info['line_number'],
                    "dual_agent_line": dual_info['line_number'],
                }
            elif exec_info:
                comparison[func_name] = {"in_both": False, "only_in": "executor"}
            elif dual_info:
                comparison[func_name] = {"in_both": False, "only_in": "dual_agent"}

        return comparison

    def analyze_get_config_implementations(self) -> dict[str, Any]:
        """分析 _get_config 的实现差异."""
        print("\n[2] _get_config() 实现差异分析:")

        # 读取 node_execution/executor.py 的 _get_config
        executor_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
        executor_source = executor_path.read_text(encoding="utf-8")

        # 读取 nodes/dual_agent.py 的 _get_config
        dual_agent_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
        dual_agent_source = dual_agent_path.read_text(encoding="utf-8")

        print("\n    node_execution/executor.py _get_config:")
        # 提取函数内容
        exec_config = self._extract_function_source(executor_source, "_get_config")
        if exec_config:
            for line in exec_config[:10]:  # 前10行
                print(f"      {line}")

        print("\n    nodes/dual_agent.py _get_config:")
        dual_config = self._extract_function_source(dual_agent_source, "_get_config")
        if dual_config:
            for line in dual_config[:10]:  # 前10行
                print(f"      {line}")

        # 检查环境变量使用
        findings = {
            "executor_uses_load_config": "load_config" in executor_source,
            "dual_agent_uses_env_vars": "ANTHROPIC_API_KEY" in dual_agent_source,
            "inconsistency": None,
        }

        if findings["executor_uses_load_config"] and findings["dual_agent_uses_env_vars"]:
            findings["inconsistency"] = {
                "type": "配置来源不一致",
                "description": (
                    "node_execution/executor.py 使用 load_config() 加载配置，"
                    "但 nodes/dual_agent.py 直接读取 ANTHROPIC_API_KEY/DB_PATH/OUTPUT_DIR 环境变量。"
                    "这导致配置语义分叉。"
                ),
            }
            print(f"\n    ⚠️  发现问题: {findings['inconsistency']['type']}")
            print(f"        {findings['inconsistency']['description']}")

        return findings

    def _extract_function_source(self, source: str, func_name: str) -> list[str] | None:
        """提取函数源代码."""
        lines = source.split("\n")
        start_idx = None

        for i, line in enumerate(lines):
            if f"def {func_name}(" in line or f"async def {func_name}(" in line:
                start_idx = i
                break

        if start_idx is None:
            return None

        # 找到函数结束（简单缩进检查）
        func_lines = [lines[start_idx]]
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                func_lines.append(line)
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                break
            func_lines.append(line)

        return func_lines

    def analyze_execution_paths(self) -> dict[str, Any]:
        """分析实际执行路径."""
        print("\n[3] 实际执行路径分析:")

        # 检查 pipeline/graph.py 使用哪个执行器
        graph_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
        graph_source = graph_path.read_text(encoding="utf-8")

        findings = {
            "graph_uses_integrated_executor": "create_integrated_node_executor" in graph_source,
            "graph_uses_simple_executor": "create_node_executor" in graph_source and "integrated" not in graph_source,
        }

        print(f"    pipeline/graph.py 分析:")
        if findings["graph_uses_integrated_executor"]:
            print(f"      使用: create_integrated_node_executor (集成执行器)")
        if "create_node_executor" in graph_source:
            print(f"      包含 create_node_executor 引用")

        # 检查 nodes/dual_agent.py 中的 legacy 桥接
        dual_agent_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
        dual_agent_source = dual_agent_path.read_text(encoding="utf-8")

        findings["has_legacy_bridge"] = "legacy" in dual_agent_source.lower() or "backward" in dual_agent_source.lower()

        if findings["has_legacy_bridge"]:
            print(f"\n    ⚠️  发现 Legacy 桥接代码")
            print(f"        nodes/dual_agent.py 包含 legacy/backward compatibility 代码")

        return findings

    def count_lines_of_code(self) -> dict[str, int]:
        """统计代码行数."""
        print("\n[4] 代码量统计:")

        files = {
            "node_execution/executor.py": Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py",
            "nodes/dual_agent.py": Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py",
        }

        stats = {}
        for name, path in files.items():
            if path.exists():
                lines = path.read_text().split("\n")
                code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
                stats[name] = code_lines
                print(f"    {name}: {code_lines} 行有效代码")

        return stats

    def generate_solution(self) -> dict[str, Any]:
        """生成解决方案."""
        print("\n" + "=" * 70)
        print("解决方案建议 (基于统一重复功能和移除 legacy)")
        print("=" * 70)

        solutions = {
            "preferred": {
                "title": "方案: 统一执行入口 (推荐)",
                "description": "移除 nodes/dual_agent.py 中的重复执行器代码，统一使用 node_execution/executor.py",
                "rationale": [
                    "单一职责原则：执行逻辑只应在 node_execution 模块",
                    "nodes/dual_agent.py 应专注于节点业务逻辑",
                    "消除配置来源不一致的风险",
                    "减少维护两套相似代码的成本",
                ],
                "migration_steps": [
                    "1. 确认 pipeline/graph.py 使用 node_execution/executor.py 的 create_node_executor",
                    "2. 从 nodes/dual_agent.py 删除以下函数:",
                    "   - create_node_executor()",
                    "   - _execute_node()",
                    "   - _get_config()",
                    "3. 删除 nodes/dual_agent.py 中所有 legacy/backward compatibility 代码",
                    "4. 更新 nodes/dual_agent.py 的 __all__，移除执行器相关导出",
                    "5. 统一配置获取逻辑，全部使用 Config 类或 load_config()",
                    "6. 运行测试确保功能正常",
                ],
            },
        }

        for key, sol in solutions.items():
            print(f"\n[{sol['title']}]")
            print(f"  描述: {sol['description']}")
            print(f"  理由:")
            for r in sol["rationale"]:
                print(f"    - {r}")
            print(f"  迁移步骤:")
            for step in sol["migration_steps"]:
                print(f"    {step}")

        return solutions

    def run_full_analysis(self) -> dict[str, Any]:
        """运行完整分析."""
        result = {
            "finding_id": "F3",
            "title": "双轨节点执行器",
            "severity": "P1",
            "analysis": {
                "function_comparison": self.analyze_executor_differences(),
                "get_config_analysis": self.analyze_get_config_implementations(),
                "execution_paths": self.analyze_execution_paths(),
                "code_stats": self.count_lines_of_code(),
            },
            "solutions": self.generate_solution(),
        }
        return result


async def main():
    """主函数."""
    debugger = DualExecutorDebugger()
    result = debugger.run_full_analysis()
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
