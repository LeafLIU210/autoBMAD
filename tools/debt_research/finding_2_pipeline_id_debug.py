#!/usr/bin/env python3
"""
Finding 2 深度调试工具: 自定义 Pipeline ID 功能损坏分析

问题: 数据库创建的 ID 与后续更新使用的 ID 不一致

研究目标:
1. 分析 create_pipeline() 的 ID 生成逻辑
2. 验证 update_pipeline_status() 的 ID 使用逻辑
3. 检查自定义 pipeline_id 参数的处理流程
4. 提出移除或修复方案
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoBMAD.docuswarm.storage.state_manager import StateManager


class PipelineIdDebugger:
    """Pipeline ID 功能调试器."""

    def __init__(self):
        self.findings: list[dict[str, Any]] = []

    def analyze_create_pipeline(self) -> dict[str, Any]:
        """分析 create_pipeline 方法的 ID 处理."""
        print("=" * 70)
        print("FINDING 2: 自定义 Pipeline ID 功能损坏分析")
        print("=" * 70)

        print("\n[1] StateManager.create_pipeline() ID 生成分析:")

        # 读取源代码
        state_manager_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
        source = state_manager_path.read_text(encoding="utf-8")
        lines = source.split("\n")

        # 查找 create_pipeline 方法
        in_method = False
        method_lines = []
        pipeline_id_generation_line = 0

        for i, line in enumerate(lines):
            if "def create_pipeline(" in line:
                in_method = True
                start_line = i
            if in_method:
                method_lines.append((i + 1, line))
                if "_generate_pipeline_id" in line:
                    pipeline_id_generation_line = i + 1
                    print(f"    ID 生成位置: 第 {i+1} 行")
                    print(f"    代码: {line.strip()}")

                # 方法结束
                if line.strip() and not line.startswith(" ") and not line.startswith("\t") and "def " in line and i > start_line:
                    break
                if i - start_line > 50:  # 安全限制
                    break

        return {
            "method": "create_pipeline",
            "id_generation_line": pipeline_id_generation_line,
            "supports_custom_id": False,  # 当前不支持自定义 ID
        }

    def analyze_orchestrator_id_handling(self) -> dict[str, Any]:
        """分析 orchestrator 中的 ID 处理."""
        print("\n[2] HybridOrchestrator.start_pipeline() ID 处理分析:")

        orchestrator_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
        source = orchestrator_path.read_text(encoding="utf-8")
        lines = source.split("\n")

        findings = {
            "db_pipeline_id_creation": None,
            "final_pipeline_id_assignment": None,
            "issue": None,
        }

        for i, line in enumerate(lines):
            # 查找 db_pipeline_id 创建
            if "db_pipeline_id = self._state_manager.create_pipeline" in line:
                findings["db_pipeline_id_creation"] = i + 1
                print(f"    数据库 Pipeline ID 创建: 第 {i+1} 行")

            # 查找 final_pipeline_id 赋值
            if "final_pipeline_id = pipeline_id or db_pipeline_id" in line:
                findings["final_pipeline_id_assignment"] = i + 1
                print(f"    Final Pipeline ID 赋值: 第 {i+1} 行")
                print(f"    代码: {line.strip()}")

                # 显示上下文
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 5)
                print("    上下文:")
                for j in range(context_start, context_end):
                    marker = ">>> " if j == i else "    "
                    print(f"    {marker}{lines[j]}")

            # 查找 update_pipeline_status 调用
            if "self._state_manager.update_pipeline_status(" in line and "final_pipeline_id" in line:
                print(f"    使用 final_pipeline_id 调用 update: 第 {i+1} 行")

        # 判断问题
        if findings["db_pipeline_id_creation"] and findings["final_pipeline_id_assignment"]:
            issue = {
                "type": "ID 不一致",
                "description": (
                    f"数据库写入使用自动生成的 ID (第 {findings['db_pipeline_id_creation']} 行)，"
                    f"但后续更新使用可能不同的 final_pipeline_id (第 {findings['final_pipeline_id_assignment']} 行)。"
                    "如果传入自定义 pipeline_id，数据库中不存在该 ID，导致更新失败。"
                ),
                "severity": "P0",
            }
            findings["issue"] = issue
            print(f"\n    ⚠️  发现问题: {issue['type']}")
            print(f"        {issue['description']}")

        return findings

    def simulate_failure(self) -> dict[str, Any]:
        """模拟失败场景."""
        print("\n[3] 失败场景模拟:")

        # 创建内存数据库
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            state_manager = StateManager(db_path=db_path)

            # 场景 1: 正常流程（不传入自定义 ID）
            print("    场景 1: 正常流程（不传入自定义 ID）")
            db_id = state_manager.create_pipeline(subject="Test Subject")
            print(f"        生成的 ID: {db_id}")
            state_manager.update_pipeline_status(db_id, status="running")
            print("        状态更新: 成功")

            # 场景 2: 尝试更新不存在的自定义 ID
            print("\n    场景 2: 尝试更新不存在的自定义 ID")
            custom_id = "my-custom-pipeline-id"
            try:
                state_manager.update_pipeline_status(custom_id, status="running")
                print("        状态更新: 成功 (意外)")
            except Exception as e:
                print(f"        状态更新: 失败")
                print(f"        错误: {e}")

            return {
                "scenario_1": "pass",
                "scenario_2": "fail",
                "conclusion": "自定义 pipeline_id 功能当前不可用",
            }

        finally:
            os.unlink(db_path)

    def generate_solution(self) -> dict[str, Any]:
        """生成解决方案."""
        print("\n" + "=" * 70)
        print("解决方案建议 (基于移除向后兼容和统一原则)")
        print("=" * 70)

        solutions = {
            "preferred": {
                "title": "方案 A: 移除自定义 ID 参数 (推荐)",
                "description": "完全移除 pipeline_id 参数，强制使用数据库生成的 UUID",
                "rationale": [
                    "简化架构，消除 ID 不一致风险",
                    "UUID 天然适合分布式环境",
                    "移除未使用的功能和兼容代码",
                ],
                "changes": [
                    "1. 从 start_pipeline() 签名中移除 pipeline_id 参数",
                    "2. 移除 final_pipeline_id 变量，直接使用 db_pipeline_id",
                    "3. 删除所有与自定义 ID 相关的 backward compatibility 代码",
                    "4. 更新文档和类型注解",
                ],
                "breaking_changes": True,
            },
            "alternative": {
                "title": "方案 B: 支持显式 ID 创建",
                "description": "在 StateManager.create_pipeline() 层支持显式传入 ID",
                "changes": [
                    "1. 修改 StateManager.create_pipeline() 添加可选 pipeline_id 参数",
                    "2. 如果传入，使用传入 ID；否则生成 UUID",
                    "3. 添加 ID 唯一性检查和冲突处理",
                ],
            },
        }

        for key, sol in solutions.items():
            print(f"\n[{sol['title']}]")
            print(f"  描述: {sol['description']}")
            print(f"  理由:" if key == "preferred" else "  变更:")
            for item in sol.get("rationale" if key == "preferred" else "changes", []):
                print(f"    - {item}")

        return solutions

    def run_full_analysis(self) -> dict[str, Any]:
        """运行完整分析."""
        result = {
            "finding_id": "F2",
            "title": "自定义 Pipeline ID 功能损坏",
            "severity": "P0",
            "analysis": {
                "create_pipeline": self.analyze_create_pipeline(),
                "orchestrator_id_handling": self.analyze_orchestrator_id_handling(),
                "simulation": self.simulate_failure(),
            },
            "solutions": self.generate_solution(),
        }
        return result


async def main():
    """主函数."""
    debugger = PipelineIdDebugger()
    result = debugger.run_full_analysis()
    return result


if __name__ == "__main__":
    asyncio.run(main())
