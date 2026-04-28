#!/usr/bin/env python3
"""F2 问题深度调试工具：state_json 与 current_node 一致性分析器

该工具专门针对评估报告中的 F2 问题（state_json 单一真相源方向正确，但实现仍未完全收口）
进行深度分析和诊断。

核心功能：
1. 检测 pipelines 表中顶层 current_node 与 state_json 内的 current_node 不一致问题
2. 分析 status/resume/restart/cancel 各路径的状态读写模式
3. 识别 state_json 未完全承载所有状态信息的漏洞
4. 生成统一设计方案的数据依据

用法:
    python tools/f2_state_consistency_analyzer.py --db docuswarm.db
    python tools/f2_state_consistency_analyzer.py --db docuswarm.db --check-inconsistency
    python tools/f2_state_consistency_analyzer.py --db docuswarm.db --analyze-paths
    python tools/f2_state_consistency_analyzer.py --db docuswarm.db --pipeline <pipeline_id> --deep-dive
    python tools/f2_state_consistency_analyzer.py --generate-report
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class StateSource(Enum):
    """状态数据来源类型"""
    TOP_LEVEL = "顶层字段"      # pipelines 表的顶层字段
    STATE_JSON = "state_json"   # state_json 内部
    BOTH = "双重来源"           # 两者都有
    UNKNOWN = "未知"            # 无法确定


class AccessPattern(Enum):
    """状态访问模式"""
    READ = "读取"
    WRITE = "写入"
    READ_WRITE = "读写"


@dataclass
class StateAccess:
    """状态访问记录"""
    operation: str                    # 操作名称：如 start_pipeline, cancel_current_node
    path: str                         # 代码路径
    line_number: int                  # 行号
    source: StateSource               # 数据来源
    field: str                        # 访问的字段
    pattern: AccessPattern            # 访问模式
    notes: str = ""                   # 备注


@dataclass
class PipelineStateAnalysis:
    """单个 Pipeline 的状态分析结果"""
    pipeline_id: str
    subject: str
    status: str
    
    # 顶层字段值
    top_level_current_node: str | None
    top_level_status: str
    
    # state_json 内的值
    state_json: dict[str, Any] = field(default_factory=dict)
    state_current_node: str | None = None
    state_status: str | None = None
    state_completed_nodes: list[str] = field(default_factory=list)
    state_node_iterations: dict[str, int] = field(default_factory=dict)
    
    # 一致性检查结果
    inconsistencies: list[dict[str, Any]] = field(default_factory=list)
    
    def check_consistency(self) -> list[dict[str, Any]]:
        """检查并返回所有不一致问题"""
        issues = []
        
        # 检查 1: current_node 不一致
        if self.top_level_current_node != self.state_current_node:
            issues.append({
                "type": "current_node_mismatch",
                "severity": "HIGH",
                "top_level": self.top_level_current_node,
                "state_json": self.state_current_node,
                "description": f"顶层 current_node({self.top_level_current_node}) "
                              f"与 state_json 内的 current_node({self.state_current_node}) 不一致"
            })
        
        # 检查 2: status 不一致
        if self.state_status and self.top_level_status != self.state_status:
            issues.append({
                "type": "status_mismatch",
                "severity": "HIGH",
                "top_level": self.top_level_status,
                "state_json": self.state_status,
                "description": f"顶层 status({self.top_level_status}) "
                              f"与 state_json 内的 status({self.state_status}) 不一致"
            })
        
        # 检查 3: state_json 完整性
        required_fields = [
            "pipeline_id", "subject_context", "current_node", "completed_nodes",
            "deliverables", "questions", "evaluations", "node_iterations",
            "session_ids", "session_metadata", "current_node_session_id",
            "status", "error", "shared_context"
        ]
        missing_fields = [f for f in required_fields if f not in self.state_json]
        if missing_fields:
            issues.append({
                "type": "incomplete_state_json",
                "severity": "MEDIUM",
                "missing_fields": missing_fields,
                "description": f"state_json 缺少 {len(missing_fields)} 个必需字段"
            })
        
        # 检查 4: completed_nodes 与 current_node 的逻辑一致性
        if self.state_current_node and self.state_completed_nodes:
            if self.state_current_node in self.state_completed_nodes:
                issues.append({
                    "type": "logical_inconsistency",
                    "severity": "MEDIUM",
                    "description": f"current_node({self.state_current_node}) 出现在 completed_nodes 中"
                })
        
        self.inconsistencies = issues
        return issues


class F2StateConsistencyAnalyzer:
    """F2 问题一致性分析器"""
    
    # 已知的代码路径访问模式（基于静态代码分析）
    KNOWN_ACCESS_PATTERNS: list[StateAccess] = [
        # state_manager.py
        StateAccess("update_pipeline_status", "storage/state_manager.py", 138, 
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.WRITE,
                   "直接更新顶层 current_node，不更新 state_json"),
        StateAccess("get_pipeline", "storage/state_manager.py", 253,
                   StateSource.BOTH, "current_node", AccessPattern.READ,
                   "同时返回顶层 current_node 和解析后的 state.current_node"),
        StateAccess("create_pipeline", "storage/state_manager.py", 98,
                   StateSource.STATE_JSON, "full_state", AccessPattern.WRITE,
                   "创建完整 PipelineState 到 state_json"),
        
        # orchestrator.py - start_pipeline
        StateAccess("start_pipeline", "pipeline/orchestrator.py", 449,
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.WRITE,
                   "启动时写入顶层 current_node=PIPELINE_NODES[0]"),
        StateAccess("start_pipeline_complete", "pipeline/orchestrator.py", 495,
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.WRITE,
                   "完成后从 result 获取 current_node 写入顶层"),
        
        # orchestrator.py - resume_pipeline
        StateAccess("resume_pipeline", "pipeline/orchestrator.py", 551,
                   StateSource.STATE_JSON, "current_node", AccessPattern.READ,
                   "从 checkpoint_state.get('current_node') 读取"),
        StateAccess("resume_pipeline", "pipeline/orchestrator.py", 604,
                   StateSource.STATE_JSON, "current_node", AccessPattern.READ,
                   "恢复时从 checkpoint_state 读取 current_node"),
        
        # orchestrator.py - restart_from_node
        StateAccess("restart_from_node", "pipeline/orchestrator.py", 686,
                   StateSource.STATE_JSON, "full_state", AccessPattern.READ,
                   "从 pipeline['state'] 读取所有状态信息"),
        StateAccess("restart_from_node", "pipeline/orchestrator.py", 718,
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.WRITE,
                   "写入顶层 current_node=node_id（目标节点）"),
        StateAccess("restart_from_node", "pipeline/orchestrator.py", 748,
                   StateSource.STATE_JSON, "current_node", AccessPattern.WRITE,
                   "写入 state_json['current_node']=node_id"),
        
        # orchestrator.py - cancel_current_node
        StateAccess("cancel_current_node", "pipeline/orchestrator.py", 988,
                   StateSource.STATE_JSON, "current_node", AccessPattern.READ,
                   "从 state.get('current_node') 读取"),
        StateAccess("cancel_current_node", "pipeline/orchestrator.py", 990,
                   StateSource.STATE_JSON, "current_node_session_id", AccessPattern.READ,
                   "从 state.get('current_node_session_id') 读取"),
        StateAccess("cancel_current_node", "pipeline/orchestrator.py", 1041,
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.WRITE,
                   "取消时写入顶层 current_node"),
        
        # orchestrator.py - get_pipeline_status
        StateAccess("get_pipeline_status", "pipeline/orchestrator.py", 1070,
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.READ,
                   "返回 pipeline.get('current_node')"),
        
        # cli/commands/status.py
        StateAccess("status_command", "cli/commands/status.py", 42,
                   StateSource.STATE_JSON, "completed_nodes", AccessPattern.READ,
                   "从 pipeline_state = pipeline.get('state', {}) 读取"),
        StateAccess("status_command", "cli/commands/status.py", 43,
                   StateSource.TOP_LEVEL, "current_node", AccessPattern.READ,
                   "从 pipeline.get('current_node', '') 读取"),
        
        # graph.py - 节点执行
        StateAccess("node_executor", "pipeline/graph.py", 103,
                   StateSource.STATE_JSON, "current_node", AccessPattern.WRITE,
                   "节点执行时写入 state.current_node = node_id"),
        StateAccess("integrated_executor", "pipeline/graph.py", 354,
                   StateSource.STATE_JSON, "current_node", AccessPattern.WRITE,
                   "集成执行器写入 state.current_node = node_id"),
    ]
    
    def __init__(self, db_path: str = "docuswarm.db"):
        self.db_path = Path(db_path)
        self.pipelines_analysis: list[PipelineStateAnalysis] = []
        self.summary: dict[str, Any] = {}
    
    def analyze_database(self) -> dict[str, Any]:
        """分析数据库中的状态一致性"""
        if not self.db_path.exists():
            return {"error": f"Database not found: {self.db_path}"}
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            # 获取所有 pipeline
            cursor = conn.execute(
                "SELECT pipeline_id, subject, status, current_node, state_json "
                "FROM pipelines ORDER BY created_at DESC"
            )
            
            for row in cursor.fetchall():
                analysis = self._analyze_pipeline_row(row)
                self.pipelines_analysis.append(analysis)
            
            conn.close()
            
            # 生成汇总
            self._generate_summary()
            return self.summary
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_pipeline_row(self, row: sqlite3.Row) -> PipelineStateAnalysis:
        """分析单个 pipeline 行"""
        analysis = PipelineStateAnalysis(
            pipeline_id=row["pipeline_id"],
            subject=row["subject"],
            status=row["status"],
            top_level_current_node=row["current_node"],
            top_level_status=row["status"]
        )
        
        # 解析 state_json
        if row["state_json"]:
            try:
                state = json.loads(row["state_json"])
                analysis.state_json = state
                analysis.state_current_node = state.get("current_node")
                analysis.state_status = state.get("status")
                analysis.state_completed_nodes = state.get("completed_nodes", [])
                analysis.state_node_iterations = state.get("node_iterations", {})
            except json.JSONDecodeError as e:
                analysis.state_json = {"_error": f"JSON decode error: {e}"}
        
        # 执行一致性检查
        analysis.check_consistency()
        
        return analysis
    
    def _generate_summary(self) -> None:
        """生成分析汇总"""
        total = len(self.pipelines_analysis)
        with_inconsistency = sum(1 for p in p.inconsistencies for p in self.pipelines_analysis)
        
        # 按问题类型统计
        issue_types: dict[str, int] = {}
        for p in self.pipelines_analysis:
            for issue in p.inconsistencies:
                issue_type = issue["type"]
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        self.summary = {
            "total_pipelines": total,
            "pipelines_with_inconsistency": with_inconsistency,
            "inconsistency_rate": f"{with_inconsistency/total*100:.1f}%" if total > 0 else "N/A",
            "issue_types": issue_types,
            "access_patterns": len(self.KNOWN_ACCESS_PATTERNS),
            "dual_source_operations": sum(
                1 for a in self.KNOWN_ACCESS_PATTERNS 
                if a.source == StateSource.BOTH or a.field == "current_node"
            )
        }
    
    def print_analysis(self) -> None:
        """打印分析结果"""
        print("=" * 80)
        print("F2 Issue Deep Analysis: state_json Single Source of Truth Convergence")
        print("=" * 80)
        print()
        
        print(f"Database Path: {self.db_path}")
        print(f"Database Exists: {'YES' if self.db_path.exists() else 'NO'}")
        print()
        
        if not self.pipelines_analysis:
            print("No Pipeline data found for analysis")
            return
        
        # 汇总信息
        print("[STATS] Summary Statistics")
        print("-" * 80)
        print(f"Total Pipelines: {self.summary['total_pipelines']}")
        print(f"Pipelines with Inconsistency: {self.summary['pipelines_with_inconsistency']}")
        print(f"Inconsistency Rate: {self.summary['inconsistency_rate']}")
        print()
        
        if self.summary['issue_types']:
            print("[ISSUES] Issue Type Distribution")
            print("-" * 80)
            for issue_type, count in self.summary['issue_types'].items():
                print(f"  - {issue_type}: {count}")
            print()
        
        # 详细分析每个有问题的 pipeline
        problematic = [p for p in self.pipelines_analysis if p.inconsistencies]
        if problematic:
            print("[DETAILS] Problematic Pipeline Details")
            print("-" * 80)
            for p in problematic[:5]:  # 只显示前5个
                print(f"\nPipeline ID: {p.pipeline_id[:40]}...")
                print(f"  Subject: {p.subject}")
                print(f"  Top-level Status: {p.top_level_status} | Current Node: {p.top_level_current_node}")
                print(f"  State Status: {p.state_status} | Current Node: {p.state_current_node}")
                print(f"  Issues Found:")
                for issue in p.inconsistencies:
                    severity_icon = "[HIGH]" if issue['severity'] == 'HIGH' else "[MED]"
                    print(f"    {severity_icon} [{issue['type']}] {issue['description']}")
            print()
    
    def print_access_patterns(self) -> None:
        """打印状态访问模式分析"""
        print("=" * 80)
        print("State Access Pattern Analysis: Identifying Dual Source Issues")
        print("=" * 80)
        print()
        
        # 按来源分组
        by_source: dict[StateSource, list[StateAccess]] = {
            StateSource.TOP_LEVEL: [],
            StateSource.STATE_JSON: [],
            StateSource.BOTH: [],
            StateSource.UNKNOWN: []
        }
        
        for access in self.KNOWN_ACCESS_PATTERNS:
            by_source[access.source].append(access)
        
        print(f"[INFO] Total Known State Access Paths: {len(self.KNOWN_ACCESS_PATTERNS)}")
        print()
        
        print("[CRITICAL] Dual Source Access (Most Dangerous)")
        print("-" * 80)
        for access in by_source[StateSource.BOTH]:
            print(f"  [{access.pattern.value}] {access.operation}")
            print(f"    Location: {access.path}:{access.line_number}")
            print(f"    Field: {access.field}")
            print(f"    Notes: {access.notes}")
            print()
        
        print("[WARNING] Top-Level Field Access Only")
        print("-" * 80)
        for access in by_source[StateSource.TOP_LEVEL]:
            print(f"  [{access.pattern.value}] {access.operation:<30} -> {access.field}")
        print()
        
        print("[OK] State JSON Access Only")
        print("-" * 80)
        for access in by_source[StateSource.STATE_JSON]:
            print(f"  [{access.pattern.value}] {access.operation:<30} -> {access.field}")
        print()
        
        # 风险分析
        print("[RISK] Risk Assessment")
        print("-" * 80)
        print("High Risk Operations (May Read Inconsistent Data):")
        
        # 识别风险：读取操作如果只从一个来源读取，而写入操作写入另一个来源
        read_from_top = set()
        read_from_state = set()
        write_to_top = set()
        write_to_state = set()
        
        for access in self.KNOWN_ACCESS_PATTERNS:
            if access.pattern in (AccessPattern.READ, AccessPattern.READ_WRITE):
                if access.source in (StateSource.TOP_LEVEL, StateSource.BOTH):
                    read_from_top.add(access.field)
                if access.source in (StateSource.STATE_JSON, StateSource.BOTH):
                    read_from_state.add(access.field)
            if access.pattern in (AccessPattern.WRITE, AccessPattern.READ_WRITE):
                if access.source in (StateSource.TOP_LEVEL, StateSource.BOTH):
                    write_to_top.add(access.field)
                if access.source in (StateSource.STATE_JSON, StateSource.BOTH):
                    write_to_state.add(access.field)
        
        # 检查不一致风险
        risk_reads_top_only = read_from_top - read_from_state - write_to_top
        risk_reads_state_only = read_from_state - read_from_top - write_to_state
        
        if risk_reads_top_only:
            print(f"  - Read from top-level only but may be updated via state_json: {risk_reads_top_only}")
        if risk_reads_state_only:
            print(f"  - Read from state_json only but may be updated via top-level: {risk_reads_state_only}")
        
        print()
    
    def generate_recommendations(self) -> list[dict[str, Any]]:
        """生成修复建议"""
        recommendations = []
        
        # 基于访问模式的建议
        top_level_writes = [
            a for a in self.KNOWN_ACCESS_PATTERNS
            if a.source == StateSource.TOP_LEVEL and a.pattern == AccessPattern.WRITE
        ]
        
        if top_level_writes:
            recommendations.append({
                "priority": "P0",
                "title": "消除顶层 current_node 写入",
                "description": f"发现 {len(top_level_writes)} 处直接写入顶层 current_node 的操作",
                "actions": [
                    "修改 update_pipeline_status() 方法，同步更新 state_json",
                    "或完全移除顶层 current_node 字段，只保留 state_json",
                    "确保所有写入操作只更新 state_json"
                ],
                "affected_files": list(set(a.path for a in top_level_writes))
            })
        
        # 基于数据分析的建议
        if self.summary.get('pipelines_with_inconsistency', 0) > 0:
            recommendations.append({
                "priority": "P0",
                "title": "修复现有数据不一致",
                "description": f"发现 {self.summary['pipelines_with_inconsistency']} 个 pipeline 存在状态不一致",
                "actions": [
                    "编写数据迁移脚本，将顶层 current_node 同步到 state_json",
                    "或从 state_json 重新计算顶层 current_node",
                    "建立数据一致性检查机制"
                ]
            })
        
        # 统一设计方案建议
        recommendations.append({
            "priority": "P1",
            "title": "统一状态访问模式",
            "description": "建立单一状态访问模式，消除双重来源",
            "actions": [
                "方案A：state_json 作为唯一真相源",
                "  - 删除 pipelines.current_node 列",
                "  - 所有读写都通过 state_json",
                "  - 添加 state_json.current_node 的数据库索引优化查询",
                "",
                "方案B：顶层字段作为缓存",
                "  - 保留顶层 current_node 作为查询优化",
                "  - 所有业务逻辑只读取 state_json",
                "  - 建立触发器或应用层逻辑保持同步",
                "",
                "推荐：方案A（更彻底）"
            ]
        })
        
        return recommendations
    
    def print_recommendations(self) -> None:
        """打印修复建议"""
        recommendations = self.generate_recommendations()
        
        print("=" * 80)
        print("Recommendations")
        print("=" * 80)
        print()
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = "[P0]" if rec['priority'] == 'P0' else "[P1]" if rec['priority'] == 'P1' else "[P2]"
            print(f"{priority_icon} Recommendation {i}: [{rec['priority']}] {rec['title']}")
            print("-" * 80)
            print(f"Description: {rec['description']}")
            print()
            print("Action Items:")
            for action in rec['actions']:
                print(f"  - {action}")
            print()


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="F2 问题深度调试工具：state_json 一致性分析器"
    )
    parser.add_argument(
        "--db",
        default="docuswarm.db",
        help="数据库路径 (默认: docuswarm.db)",
    )
    parser.add_argument(
        "--check-inconsistency",
        action="store_true",
        help="检查数据不一致问题",
    )
    parser.add_argument(
        "--analyze-paths",
        action="store_true",
        help="分析状态访问路径",
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="生成完整报告",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式",
    )
    
    args = parser.parse_args()
    
    analyzer = F2StateConsistencyAnalyzer(db_path=args.db)
    
    # 默认行为：执行全面分析
    if not any([args.check_inconsistency, args.analyze_paths, args.generate_report]):
        args.check_inconsistency = True
        args.analyze_paths = True
    
    if args.check_inconsistency:
        analyzer.analyze_database()
        if args.json:
            print(json.dumps(analyzer.summary, indent=2, ensure_ascii=False))
        else:
            analyzer.print_analysis()
    
    if args.analyze_paths:
        if args.json:
            pass  # JSON 模式下路径分析不输出
        else:
            analyzer.print_access_patterns()
    
    if args.generate_report:
        analyzer.analyze_database()
        if not args.json:
            analyzer.print_analysis()
            analyzer.print_access_patterns()
            analyzer.print_recommendations()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
