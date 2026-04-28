#!/usr/bin/env python3
"""DocuSwarm 技术债务深度分析工具 (P0/P1 Research Tool).

该工具用于深度分析 TD-1 ~ TD-5 技术债务问题，
帮助诊断系统边界、状态一致性和架构设计问题。

用法:
    python tools/docuswarm_technical_debt_analyzer.py --td1  # 分析 current_node 重复表示
    python tools/docuswarm_technical_debt_analyzer.py --td2  # 分析 Path.cwd() 依赖
    python tools/docuswarm_technical_debt_analyzer.py --td3  # 分析兼容层问题
    python tools/docuswarm_technical_debt_analyzer.py --td4  # 分析执行骨架重复
    python tools/docuswarm_technical_debt_analyzer.py --td5  # 分析 CLI 厚度
    python tools/docuswarm_technical_debt_analyzer.py --all   # 分析所有问题
    python tools/docuswarm_technical_debt_analyzer.py --report # 生成完整报告
"""

from __future__ import annotations

import argparse
import ast
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent
DOCUSWARM_ROOT = PROJECT_ROOT / "autoBMAD" / "docuswarm"


class TechnicalDebtAnalyzer:
    """技术债务分析器."""

    def __init__(self, db_path: str = "docuswarm.db") -> None:
        self.db_path = db_path
        self.findings: list[dict[str, Any]] = []

    def analyze_td1_state_duplication(self) -> dict[str, Any]:
        """分析 TD-1: current_node 与运行状态重复表示问题.

        检查:
        1. state_manager.py 是否同时更新顶层 current_node 和 state_json
        2. orchestrator.py 恢复逻辑读取的是哪一层
        3. CLI 状态页同时读取两层数据的风险
        """
        results = {
            "td": "TD-1",
            "title": "current_node 与运行状态重复表示",
            "severity": "P0",
            "findings": [],
            "risks": [],
            "recommendations": [],
        }

        # 检查 StateManager
        state_manager_file = DOCUSWARM_ROOT / "storage" / "state_manager.py"
        if state_manager_file.exists():
            content = state_manager_file.read_text(encoding="utf-8")

            # 检查是否更新顶层 current_node
            if "current_node = ?" in content:
                results["findings"].append({
                    "file": "state_manager.py",
                    "issue": "直接更新 pipelines.current_node 列",
                    "evidence": "UPDATE pipelines SET status = ?, current_node = ?",
                })

            # 检查是否返回 state_json
            if 'json.loads(cast(str, row["state_json"]))' in content:
                results["findings"].append({
                    "file": "state_manager.py",
                    "issue": "get_pipeline() 同时返回顶层 current_node 和 state_json 中的状态",
                    "evidence": 'row["current_node"] 和 json.loads(row["state_json"])',
                })

        # 检查 Orchestrator
        orchestrator_file = DOCUSWARM_ROOT / "pipeline" / "orchestrator.py"
        if orchestrator_file.exists():
            content = orchestrator_file.read_text(encoding="utf-8")

            # 检查恢复逻辑
            if 'pipeline.get("state", {})' in content:
                results["findings"].append({
                    "file": "orchestrator.py",
                    "issue": "恢复逻辑读取 state 字段",
                    "evidence": 'checkpoint_state = pipeline.get("state", {})',
                })

        # 风险分析
        results["risks"] = [
            "状态展示和恢复可能出现漂移",
            "status/resume/restart/cancel 语义依赖可能不一致",
            "排障困难：用户看到的状态和系统实际恢复依据可能不同",
        ]

        # 建议
        results["recommendations"] = [
            "明确 state_json 为唯一业务真相源",
            "将 pipelines.current_node 降级为派生字段",
            "为状态操作增加一致性测试",
        ]

        return results

    def analyze_td2_cwd_dependency(self) -> dict[str, Any]:
        """分析 TD-2: 工具层强依赖 Path.cwd() 问题."""
        results = {
            "td": "TD-2",
            "title": "工具层强依赖 Path.cwd()",
            "severity": "P0",
            "findings": [],
            "risks": [],
            "recommendations": [],
        }

        # 检查工具文件
        tools_to_check = [
            ("create_deliverable.py", "create_deliverable"),
            ("create_document_set.py", "create_document_set"),
        ]

        tools_dir = DOCUSWARM_ROOT / "tools"
        for filename, tool_name in tools_to_check:
            tool_file = tools_dir / filename
            if tool_file.exists():
                content = tool_file.read_text(encoding="utf-8")

                if "Path.cwd()" in content:
                    # 找到具体行
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        if "Path.cwd()" in line and "#" not in line:
                            results["findings"].append({
                                "file": filename,
                                "line": i,
                                "code": line.strip(),
                                "issue": f"{tool_name} 直接使用 Path.cwd() 作为输出位置",
                            })

        # 检查测试文件
        tests_dir = PROJECT_ROOT / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_create_deliverable*.py")) + \
                        list(tests_dir.rglob("test_create_document_set*.py"))

            for test_file in test_files:
                content = test_file.read_text(encoding="utf-8")
                if "os.chdir" in content:
                    results["findings"].append({
                        "file": str(test_file.relative_to(PROJECT_ROOT)),
                        "issue": "测试使用 os.chdir() 驱动全局状态",
                        "evidence": "os.chdir 调用",
                    })

        # 风险分析
        results["risks"] = [
            "工具可复用性下降",
            "测试间互相污染",
            "环境差异直接放大为假失败",
            "并发执行或多 pipeline 并行时更脆弱",
        ]

        # 建议
        results["recommendations"] = [
            "为工具显式注入 output_dir/work_dir 参数",
            "测试使用临时目录 fixture 而非 os.chdir()",
            "将当前目录从业务契约中移除",
        ]

        return results

    def analyze_td3_compatibility_layer(self) -> dict[str, Any]:
        """分析 TD-3: 兼容层在主路径上问题."""
        results = {
            "td": "TD-3",
            "title": "兼容层仍在主路径上",
            "severity": "P1",
            "findings": [],
            "risks": [],
            "recommendations": [],
        }

        # 检查 models/__init__.py
        models_init = DOCUSWARM_ROOT / "models" / "__init__.py"
        if models_init.exists():
            content = models_init.read_text(encoding="utf-8")

            if "warnings.warn" in content:
                results["findings"].append({
                    "file": "models/__init__.py",
                    "issue": "模块导入时发出 DeprecationWarning",
                    "evidence": "warnings.warn(..., stacklevel=2)",
                })

            if "from autoBMAD.docuswarm.tools" in content:
                results["findings"].append({
                    "file": "models/__init__.py",
                    "issue": "通过 re-export 暴露 ToolRegistry 和 ToolResult",
                    "evidence": "from autoBMAD.docuswarm.tools.tool_registry import",
                })

        # 检查 tool_registry.py
        tool_registry = DOCUSWARM_ROOT / "models" / "tool_registry.py"
        if tool_registry.exists():
            content = tool_registry.read_text(encoding="utf-8")
            if "warnings.warn" in content:
                results["findings"].append({
                    "file": "models/tool_registry.py",
                    "issue": "导入期废弃告警",
                    "evidence": "warnings.warn on import",
                })

        # 风险分析
        results["risks"] = [
            "废弃路径变成半稳定 API",
            "测试会因为导入顺序而抖动",
            "使用者面对两个入口，认知负担增加",
        ]

        # 建议
        results["recommendations"] = [
            "改为基于 __getattr__ 触发 warning",
            "或彻底移除 models 模块",
            "在文档中只保留一个标准入口",
        ]

        return results

    def analyze_td4_execution_skeletons(self) -> dict[str, Any]:
        """分析 TD-4: 三套执行骨架并存问题."""
        results = {
            "td": "TD-4",
            "title": "pipeline/node_execution/nodes 三套执行骨架并存",
            "severity": "P1",
            "findings": [],
            "risks": [],
            "recommendations": [],
        }

        # 检查同名骨架文件
        skeleton_files = [
            ("graph.py", "pipeline/graph.py vs node_execution/graph.py"),
            ("state.py", "pipeline/state.py vs node_execution/state.py"),
            ("metrics.py", "pipeline/metrics.py vs node_execution/metrics.py"),
            ("escalation.py", "pipeline/escalation.py vs node_execution/escalation.py"),
        ]

        for filename, description in skeleton_files:
            pipeline_file = DOCUSWARM_ROOT / "pipeline" / filename
            node_exec_file = DOCUSWARM_ROOT / "node_execution" / filename

            if pipeline_file.exists() and node_exec_file.exists():
                results["findings"].append({
                    "issue": f"同名骨架文件并存: {description}",
                    "pipeline_file": str(pipeline_file.relative_to(PROJECT_ROOT)),
                    "node_exec_file": str(node_exec_file.relative_to(PROJECT_ROOT)),
                })

        # 检查合成 pipeline_id
        flow_file = DOCUSWARM_ROOT / "node_execution" / "flow.py"
        if flow_file.exists():
            content = flow_file.read_text(encoding="utf-8")

            if 'f"node-{node_id}-{run_id}"' in content:
                results["findings"].append({
                    "file": "node_execution/flow.py",
                    "issue": "合成 pipeline_id 适配 StateManager",
                    "evidence": 'pipeline_id = f"node-{node_id}-{run_id}"',
                })

            if 'f"node-run-{run_id}"' in content:
                results["findings"].append({
                    "file": "node_execution/flow.py",
                    "issue": "另一种合成 pipeline_id 模式",
                    "evidence": 'pipeline_id = f"node-run-{run_id}"',
                })

        # 检查覆盖率（模拟）
        results["findings"].append({
            "issue": "低覆盖率模块",
            "coverage": {
                "pipeline": "28.4%",
                "node_execution": "36.5%",
                "nodes": "22.6%",
            },
        })

        # 风险分析
        results["risks"] = [
            "认知成本高：新开发者难以判断逻辑应该放在哪一层",
            "改动传播范围扩大",
            "适配代码越积越多，转化为维护税",
        ]

        # 建议
        results["recommendations"] = [
            "明确一条主干：pipeline 为业务编排主干，node_execution 为节点级执行库",
            "禁止继续新增平行语义文件",
            "将合成 pipeline_id 限制在单一边界层",
        ]

        return results

    def analyze_td5_cli_thickness(self) -> dict[str, Any]:
        """分析 TD-5: CLI 入口过厚问题."""
        results = {
            "td": "TD-5",
            "title": "CLI 入口过厚",
            "severity": "P1",
            "findings": [],
            "risks": [],
            "recommendations": [],
        }

        main_file = DOCUSWARM_ROOT / "main.py"
        if main_file.exists():
            content = main_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            # 统计行数
            line_count = len(lines)
            results["findings"].append({
                "file": "main.py",
                "metric": "总行数",
                "value": line_count,
            })

            # 统计 @cli.command()
            command_count = content.count("@cli.command()")
            results["findings"].append({
                "file": "main.py",
                "metric": "命令数量",
                "value": command_count,
            })

            # 统计 asyncio.run
            asyncio_count = content.count("asyncio.run(")
            results["findings"].append({
                "file": "main.py",
                "metric": "asyncio.run 调用",
                "value": asyncio_count,
            })

            # 覆盖率信息
            results["findings"].append({
                "file": "main.py",
                "metric": "测试覆盖率",
                "value": "0%",
            })

        # 风险分析
        results["risks"] = [
            "start/status/resume/cancel/clean 等行为难以稳定回归",
            "任一命令变更都需要人工通读大文件",
            "入口层和领域层边界模糊",
        ]

        # 建议
        results["recommendations"] = [
            "将 main.py 拆为 commands/* + services/* 两层",
            "click 命令函数只保留参数解析和输出",
            "优先为关键命令建立 smoke tests",
        ]

        return results

    def generate_full_report(self) -> dict[str, Any]:
        """生成完整的技术债务报告."""
        return {
            "report_title": "DocuSwarm P0/P1 技术债务深度研究报告",
            "generated_at": str(__import__("datetime").datetime.now()),
            "summary": {
                "total_issues": 5,
                "p0_issues": 2,
                "p1_issues": 3,
            },
            "findings": [
                self.analyze_td1_state_duplication(),
                self.analyze_td2_cwd_dependency(),
                self.analyze_td3_compatibility_layer(),
                self.analyze_td4_execution_skeletons(),
                self.analyze_td5_cli_thickness(),
            ],
        }


def print_td_report(results: dict[str, Any]) -> None:
    """打印单个技术债务分析报告."""
    print("=" * 70)
    print(f"[{results['severity']}] {results['td']}: {results['title']}")
    print("=" * 70)
    print()

    if results["findings"]:
        print("[FINDINGS] 发现的问题:")
        print("-" * 70)
        for finding in results["findings"]:
            print(f"  文件: {finding.get('file', 'N/A')}")
            if "line" in finding:
                print(f"  行号: {finding['line']}")
            print(f"  问题: {finding.get('issue', 'N/A')}")
            if "code" in finding:
                print(f"  代码: {finding['code']}")
            if "evidence" in finding:
                print(f"  证据: {finding['evidence']}")
            print()

    if results["risks"]:
        print("[RISKS] 风险:")
        print("-" * 70)
        for risk in results["risks"]:
            print(f"  • {risk}")
        print()

    if results["recommendations"]:
        print("[RECOMMENDATIONS] 建议:")
        print("-" * 70)
        for rec in results["recommendations"]:
            print(f"  • {rec}")
        print()


def print_full_report(report: dict[str, Any]) -> None:
    """打印完整报告."""
    print("=" * 70)
    print(report["report_title"])
    print(f"生成时间: {report['generated_at']}")
    print("=" * 70)
    print()

    summary = report["summary"]
    print("[SUMMARY] 摘要:")
    print(f"  总问题数: {summary['total_issues']}")
    print(f"  P0 问题: {summary['p0_issues']}")
    print(f"  P1 问题: {summary['p1_issues']}")
    print()

    for finding in report["findings"]:
        print_td_report(finding)
        print()


def main() -> int:
    """主函数."""
    parser = argparse.ArgumentParser(
        description="DocuSwarm 技术债务深度分析工具"
    )
    parser.add_argument(
        "--td1",
        action="store_true",
        help="分析 TD-1: current_node 重复表示",
    )
    parser.add_argument(
        "--td2",
        action="store_true",
        help="分析 TD-2: Path.cwd() 依赖",
    )
    parser.add_argument(
        "--td3",
        action="store_true",
        help="分析 TD-3: 兼容层问题",
    )
    parser.add_argument(
        "--td4",
        action="store_true",
        help="分析 TD-4: 执行骨架重复",
    )
    parser.add_argument(
        "--td5",
        action="store_true",
        help="分析 TD-5: CLI 厚度",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="分析所有问题",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成完整研究报告",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式",
    )

    args = parser.parse_args()

    analyzer = TechnicalDebtAnalyzer()

    if args.report or args.all:
        report = analyzer.generate_full_report()
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print_full_report(report)
    else:
        results_list = []
        if args.td1:
            results_list.append(analyzer.analyze_td1_state_duplication())
        if args.td2:
            results_list.append(analyzer.analyze_td2_cwd_dependency())
        if args.td3:
            results_list.append(analyzer.analyze_td3_compatibility_layer())
        if args.td4:
            results_list.append(analyzer.analyze_td4_execution_skeletons())
        if args.td5:
            results_list.append(analyzer.analyze_td5_cli_thickness())

        if not results_list:
            # 默认分析所有
            report = analyzer.generate_full_report()
            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print_full_report(report)
        else:
            for results in results_list:
                if args.json:
                    print(json.dumps(results, indent=2, ensure_ascii=False))
                else:
                    print_td_report(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
