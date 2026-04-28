#!/usr/bin/env python3
"""
Finding 1 深度调试工具: Session Manager 初始化链路分析

问题: start_pipeline() 在未显式注入 session_manager 时会先触发 LLM 校验，再直接报错

研究目标:
1. 确认 ContextValidator 在 session_manager=None 时的行为
2. 验证 validate_context_with_llm() 的调用时机和依赖关系
3. 检查 orchestrator 初始化流程的问题
4. 提出统一的解决方案
"""

from __future__ import annotations

import asyncio
import inspect
import sys
from pathlib import Path
from typing import Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoBMAD.docuswarm.context.validator import ContextValidator
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class SessionManagerDebugger:
    """Session Manager 初始化链路调试器."""

    def __init__(self):
        self.findings: list[dict[str, Any]] = []
        self.recommendations: list[str] = []

    def analyze_context_validator_init(self) -> dict[str, Any]:
        """分析 ContextValidator 的初始化逻辑."""
        print("=" * 70)
        print("FINDING 1: Session Manager 初始化链路分析")
        print("=" * 70)

        # 获取 ContextValidator.__init__ 的签名
        sig = inspect.signature(ContextValidator.__init__)
        params = list(sig.parameters.items())

        result = {
            "component": "ContextValidator",
            "issue": "session_manager 允许为 None 但后续调用要求非 None",
            "parameters": [(name, param.default) for name, param in params],
        }

        print("\n[1] ContextValidator.__init__ 参数分析:")
        for name, param in params:
            default = param.default if param.default is not param.empty else "REQUIRED"
            print(f"    - {name}: default={default}")

        # 检查 validate_context_with_llm 方法
        print("\n[2] validate_context_with_llm 方法分析:")
        source = inspect.getsource(ContextValidator.validate_context_with_llm)
        lines = source.split("\n")
        for i, line in enumerate(lines):
            if "session_manager is required" in line:
                print(f"    第 {i+1} 行发现硬性检查:")
                print(f"    {line.strip()}")
                result["error_line"] = line.strip()
                break

        return result

    def analyze_orchestrator_init(self) -> dict[str, Any]:
        """分析 HybridOrchestrator 的初始化逻辑."""
        print("\n[3] HybridOrchestrator 初始化分析:")

        # 读取 orchestrator.py 的初始化代码
        orchestrator_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
        source = orchestrator_path.read_text(encoding="utf-8")

        # 查找关键代码段
        lines = source.split("\n")

        findings = {
            "context_validator_creation_line": None,
            "session_manager_check_line": None,
            "issue": None,
        }

        for i, line in enumerate(lines):
            # 查找 ContextValidator 创建位置
            if "self._context_validator = ContextValidator" in line:
                findings["context_validator_creation_line"] = i + 1
                print(f"    ContextValidator 创建位置: 第 {i+1} 行")
                # 打印上下文
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                print("    上下文代码:")
                for j in range(context_start, context_end):
                    marker = ">>> " if j == i else "    "
                    print(f"    {marker}{lines[j]}")

            # 查找 session_manager 检查
            if "_get_or_create_session_manager" in line and "def " in line:
                findings["session_manager_check_line"] = i + 1
                print(f"\n    _get_or_create_session_manager 定义位置: 第 {i+1} 行")

        return findings

    def analyze_start_pipeline_flow(self) -> dict[str, Any]:
        """分析 start_pipeline 的调用流程."""
        print("\n[4] start_pipeline() 调用流程分析:")

        orchestrator_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
        source = orchestrator_path.read_text()
        lines = source.split("\n")

        # 查找 start_pipeline 方法
        in_start_pipeline = False
        start_line = 0
        validate_call_line = 0
        session_manager_get_line = 0

        for i, line in enumerate(lines):
            if "async def start_pipeline(" in line:
                in_start_pipeline = True
                start_line = i + 1
                print(f"    start_pipeline 方法开始: 第 {i+1} 行")

            if in_start_pipeline:
                if "validate_context_with_llm" in line:
                    validate_call_line = i + 1
                    print(f"    LLM 校验调用: 第 {i+1} 行")
                    print(f"    代码: {line.strip()}")

                if "_get_or_create_session_manager" in line and "=" in line:
                    session_manager_get_line = i + 1
                    print(f"    SessionManager 获取/创建: 第 {i+1} 行")

                # 方法结束判断（简单的缩进检查）
                if i > start_line and line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                    if "def " in line or "class " in line:
                        break

        # 判断问题
        issue = None
        if validate_call_line > 0 and session_manager_get_line > 0:
            if validate_call_line < session_manager_get_line:
                issue = {
                    "type": "顺序错误",
                    "description": f"validate_context_with_llm() 在第 {validate_call_line} 行调用，"
                                   f"但 session_manager 确保在第 {session_manager_get_line} 行才创建",
                    "severity": "P0",
                }
                print(f"\n    ⚠️  发现问题: {issue['type']}")
                print(f"        {issue['description']}")

        return {
            "validate_call_line": validate_call_line,
            "session_manager_get_line": session_manager_get_line,
            "issue": issue,
        }

    def generate_solution(self) -> dict[str, Any]:
        """生成解决方案."""
        print("\n" + "=" * 70)
        print("解决方案建议 (基于统一重复功能和架构原则)")
        print("=" * 70)

        solutions = {
            "preferred": {
                "title": "方案 A: 延迟初始化模式 (推荐)",
                "description": "移除 ContextValidator 对 session_manager 的构造函数依赖，改为调用时注入",
                "changes": [
                    "1. ContextValidator.__init__() 不再接收 session_manager 参数",
                    "2. validate_context_with_llm() 方法增加 session_manager 参数",
                    "3. HybridOrchestrator.start_pipeline() 先获取/创建 session_manager，再调用校验",
                ],
                "migration_steps": [
                    "修改 ContextValidator 构造函数，移除 session_manager 参数",
                    "修改 validate_context_with_llm 签名，添加 session_manager: KimiSessionManager 参数",
                    "修改 HybridOrchestrator.start_pipeline() 调用顺序",
                    "删除所有 backward compatibility 代码",
                ],
            },
            "alternative": {
                "title": "方案 B: 提前初始化模式",
                "description": "HybridOrchestrator.__init__() 中确保 session_manager 已创建",
                "changes": [
                    "1. HybridOrchestrator.__init__() 中调用 _get_or_create_session_manager()",
                    "2. 使用创建的 session_manager 初始化 ContextValidator",
                ],
            },
        }

        for key, sol in solutions.items():
            print(f"\n[{sol['title']}]")
            print(f"  描述: {sol['description']}")
            print(f"  变更:")
            for change in sol.get("changes", []):
                print(f"    - {change}")

        return solutions

    def run_full_analysis(self) -> dict[str, Any]:
        """运行完整分析."""
        print("\n" + "=" * 70)
        print("FINDING 1: Session Manager 初始化问题深度研究")
        print("=" * 70)

        result = {
            "finding_id": "F1",
            "title": "Session Manager 初始化链路故障",
            "severity": "P0",
            "analysis": {
                "context_validator": self.analyze_context_validator_init(),
                "orchestrator_init": self.analyze_orchestrator_init(),
                "start_pipeline_flow": self.analyze_start_pipeline_flow(),
            },
            "solutions": self.generate_solution(),
        }

        return result


async def main():
    """主函数."""
    debugger = SessionManagerDebugger()
    result = debugger.run_full_analysis()
    return result


if __name__ == "__main__":
    asyncio.run(main())
