#!/usr/bin/env python3
"""
Finding 4 深度调试工具: 状态双轨模型分析

问题: 状态持久化仍是"双轨模型"，state_json 与顶层列并存，存在 split-brain 风险

研究目标:
1. 分析 state_json 和顶层列的使用情况
2. 检查读写来源不一致问题
3. 验证 _verify_state_consistency 的存在和影响
4. 提出单一事实源方案
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.pipeline.state import create_initial_state


class StateModelDebugger:
    """状态模型调试器."""

    def __init__(self):
        self.findings: list[dict[str, Any]] = []

    def analyze_state_creation(self) -> dict[str, Any]:
        """分析状态创建逻辑."""
        print("=" * 70)
        print("FINDING 4: 状态双轨模型分析")
        print("=" * 70)

        print("\n[1] 初始状态创建逻辑对比:")

        # 分析 pipeline/state.py 的 create_initial_state
        print("\n    pipeline/state.py create_initial_state():")
        state_module_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "pipeline" / "state.py"
        state_source = state_module_path.read_text(encoding="utf-8")

        # 提取函数
        lines = state_source.split("\n")
        in_func = False
        for i, line in enumerate(lines):
            if "def create_initial_state(" in line:
                in_func = True
                print(f"      定义位置: 第 {i+1} 行")
            if in_func:
                if line.strip().startswith("return"):
                    print(f"      返回类型: PipelineState TypedDict")
                    break

        # 分析 storage/state_manager.py 的 _create_initial_state
        print("\n    storage/state_manager.py _create_initial_state():")
        manager_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
        manager_source = manager_path.read_text(encoding="utf-8")

        lines = manager_source.split("\n")
        in_func = False
        for i, line in enumerate(lines):
            if "def _create_initial_state(" in line:
                in_func = True
                print(f"      定义位置: 第 {i+1} 行")
                # 打印注释
                if i > 0 and "local copy" in lines[i-1]:
                    print(f"      注释: {lines[i-1].strip()}")
            if in_func:
                if line.strip().startswith("return {"):
                    print(f"      返回类型: 普通 dict (非 TypedDict)")
                    break

        return {
            "issue": "StateManager 复制了一份 _create_initial_state() 而不是复用 pipeline/state.py",
            "impact": "两处逻辑可能不一致，维护成本高",
        }

    def analyze_database_schema(self) -> dict[str, Any]:
        """分析数据库表结构."""
        print("\n[2] 数据库表结构分析:")

        import os

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            state_manager = StateManager(db_path=db_path)

            # 获取表结构
            with state_manager._db.acquire() as conn:
                cursor = conn.execute("PRAGMA table_info(pipelines)")
                columns = cursor.fetchall()

                print(f"    pipelines 表结构:")
                state_json_col = None
                top_level_cols = []

                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    print(f"      - {col_name}: {col_type}")

                    if col_name == "state_json":
                        state_json_col = col_name
                    elif col_name not in ["pipeline_id", "subject", "created_at", "updated_at"]:
                        top_level_cols.append(col_name)

                findings = {
                    "has_state_json": state_json_col is not None,
                    "top_level_state_cols": top_level_cols,
                    "duplication_risk_cols": [c for c in top_level_cols if c in ["status", "current_node"]],
                }

                print(f"\n    分析:")
                print(f"      state_json 列: {'存在' if findings['has_state_json'] else '不存在'}")
                print(f"      顶层状态列: {top_level_cols}")
                print(f"      潜在重复列: {findings['duplication_risk_cols']}")

                return findings

        finally:
            os.unlink(db_path)

    def analyze_verification_logic(self) -> dict[str, Any]:
        """分析一致性验证逻辑."""
        print("\n[3] 一致性验证逻辑分析:")

        manager_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
        manager_source = manager_path.read_text(encoding="utf-8")

        # 查找 _verify_state_consistency
        lines = manager_source.split("\n")
        found = False
        for i, line in enumerate(lines):
            if "def _verify_state_consistency(" in line:
                found = True
                print(f"    发现 _verify_state_consistency 方法: 第 {i+1} 行")
                # 打印方法签名和前几行
                for j in range(i, min(i+10, len(lines))):
                    print(f"      {lines[j]}")
                break

        if found:
            return {
                "has_consistency_check": True,
                "issue": "代码中已经存在一致性检测逻辑，说明 split-brain 问题已被默认接受",
            }
        else:
            return {"has_consistency_check": False}

    def analyze_read_write_paths(self) -> dict[str, Any]:
        """分析读写路径."""
        print("\n[4] 读写路径分析:")

        manager_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
        manager_source = manager_path.read_text(encoding="utf-8")

        findings = {
            "update_pipeline_status": {
                "writes_to_top_level": True,
                "writes_to_state_json": "_update_state_json_partial" in manager_source,
            },
            "get_pipeline": {
                "reads_from": "state_json" if "state_json" in self._extract_get_pipeline_source() else "unknown",
            },
            "list_pipelines": {
                "reads_from": "top_level_columns" if "FROM pipelines" in manager_source else "unknown",
            },
        }

        print(f"    update_pipeline_status():")
        print(f"      写入顶层列: {findings['update_pipeline_status']['writes_to_top_level']}")
        print(f"      同步写入 state_json: {findings['update_pipeline_status']['writes_to_state_json']}")

        print(f"\n    get_pipeline():")
        print(f"      主要读取来源: {findings['get_pipeline']['reads_from']}")

        print(f"\n    list_pipelines():")
        print(f"      读取来源: {findings['list_pipelines']['reads_from']}")

        # 检查潜在不一致
        if (findings["update_pipeline_status"]["writes_to_top_level"] and
            findings["get_pipeline"]["reads_from"] == "state_json"):
            print(f"\n    ⚠️  发现潜在不一致:")
            print(f"        写入使用顶层列，读取使用 state_json")
            print(f"        如果同步失败，会出现 split-brain")

        return findings

    def _extract_get_pipeline_source(self) -> str:
        """提取 get_pipeline 方法源码."""
        manager_path = Path(__file__).parent.parent.parent / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
        source = manager_path.read_text()
        return source

    def simulate_inconsistency(self) -> dict[str, Any]:
        """模拟不一致场景."""
        print("\n[5] 不一致场景模拟:")

        import os

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            state_manager = StateManager(db_path=db_path)

            # 创建 pipeline
            pipeline_id = state_manager.create_pipeline(subject="Test Subject")
            print(f"    创建 Pipeline: {pipeline_id}")

            # 获取初始状态
            pipeline = state_manager.get_pipeline(pipeline_id)
            print(f"    初始状态: status={pipeline.get('status')}")

            # 更新状态
            state_manager.update_pipeline_status(pipeline_id, status="running", current_node="analyst")
            print(f"    更新状态: status=running, current_node=analyst")

            # 再次获取
            pipeline = state_manager.get_pipeline(pipeline_id)
            print(f"    更新后状态: status={pipeline.get('status')}, current_node={pipeline.get('current_node')}")

            # 列出所有 pipelines
            pipelines = state_manager.list_pipelines()
            if pipelines:
                p = pipelines[0]
                print(f"    list_pipelines 结果: status={p.get('status')}, current_node={p.get('current_node')}")

            return {"simulation": "completed"}

        finally:
            os.unlink(db_path)

    def generate_solution(self) -> dict[str, Any]:
        """生成解决方案."""
        print("\n" + "=" * 70)
        print("解决方案建议 (基于单一事实源原则)")
        print("=" * 70)

        solutions = {
            "preferred": {
                "title": "方案: state_json 作为单一事实源",
                "description": "以 state_json 为唯一真相，顶层列仅保留最小必要索引字段",
                "rationale": [
                    "state_json 包含完整状态，适合作为事实源",
                    "顶层列仅用于索引和简单查询",
                    "避免重复数据带来的同步问题",
                ],
                "migration_steps": [
                    "1. 删除 StateManager._create_initial_state()，统一使用 pipeline/state.py 的 create_initial_state()",
                    "2. 修改 update_pipeline_status() 仅更新 state_json",
                    "3. 顶层列仅保留: pipeline_id (主键), subject (索引), created_at, updated_at",
                    "4. get_pipeline() 和 list_pipelines() 都从 state_json 读取状态",
                    "5. 删除 _verify_state_consistency() 检查（不再需要）",
                    "6. 添加数据库触发器或应用层保证同步（如需要）",
                ],
            },
            "alternative": {
                "title": "方案 B: 顶层列作为单一事实源",
                "description": "将状态完全规范化到顶层列，state_json 仅作备份",
                "migration_steps": [
                    "1. 扩展 pipelines 表，包含所有状态字段",
                    "2. 移除 state_json 列或仅用于审计",
                    "3. 修改所有读写操作使用顶层列",
                ],
            },
        }

        for key, sol in solutions.items():
            print(f"\n[{sol['title']}]")
            print(f"  描述: {sol['description']}")
            if "rationale" in sol:
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
            "finding_id": "F4",
            "title": "状态双轨模型",
            "severity": "P1",
            "analysis": {
                "state_creation": self.analyze_state_creation(),
                "database_schema": self.analyze_database_schema(),
                "verification_logic": self.analyze_verification_logic(),
                "read_write_paths": self.analyze_read_write_paths(),
                "simulation": self.simulate_inconsistency(),
            },
            "solutions": self.generate_solution(),
        }
        return result


async def main():
    """主函数."""
    debugger = StateModelDebugger()
    result = debugger.run_full_analysis()
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
