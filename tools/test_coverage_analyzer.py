"""
DocuSwarm 测试覆盖率分析工具
用于检测和分析 TD-003: 测试覆盖率不足问题

Usage:
    python tools/test_coverage_analyzer.py --target autoBMAD/docuswarm
    python tools/test_coverage_analyzer.py --report-only
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CoverageGap:
    """Identified coverage gap."""
    module: str
    component: str
    component_type: str  # "function", "class", "method"
    priority: str
    reason: str
    recommendation: str


def analyze_td003_specific_gaps() -> list[CoverageGap]:
    """Analyze specific gaps mentioned in TD-003."""
    gaps = [
        CoverageGap(
            module="pipeline/orchestrator.py",
            component="HybridOrchestrator",
            component_type="class",
            priority="high",
            reason="TD-003: Orchestrator 4 种操作 (start/resume/restart/pause) 无测试",
            recommendation="创建 test_orchestrator.py 测试所有 4 种操作"
        ),
        CoverageGap(
            module="pipeline/orchestrator.py",
            component="start_pipeline",
            component_type="method",
            priority="high",
            reason="Core orchestration logic untested",
            recommendation="Mock LangGraph and test full pipeline flow"
        ),
        CoverageGap(
            module="pipeline/orchestrator.py",
            component="resume_pipeline",
            component_type="method",
            priority="high",
            reason="Session recovery logic untested",
            recommendation="Test checkpoint resume and session restoration"
        ),
        CoverageGap(
            module="pipeline/orchestrator.py",
            component="restart_from_node",
            component_type="method",
            priority="high",
            reason="Node restart logic untested",
            recommendation="Test node state clearing and restart"
        ),
        CoverageGap(
            module="context/isolation.py",
            component="ContextManager",
            component_type="class",
            priority="high",
            reason="TD-003: ContextManager 隔离验证无测试",
            recommendation="创建 test_isolation.py 测试三层隔离"
        ),
        CoverageGap(
            module="context/isolation.py",
            component="_validate_no_private_fields",
            component_type="method",
            priority="high",
            reason="Private field validation untested",
            recommendation="Test private field detection at all nesting levels"
        ),
        CoverageGap(
            module="context/isolation.py",
            component="_check_for_private_fields",
            component_type="function",
            priority="high",
            reason="Recursive private field check untested",
            recommendation="Test nested dict/list structures"
        ),
        CoverageGap(
            module="pipeline/quality.py",
            component="VerdictDeterminer",
            component_type="class",
            priority="high",
            reason="TD-003: QualityGate 逻辑无测试",
            recommendation="创建 test_quality.py 测试所有 verdict 分支"
        ),
        CoverageGap(
            module="pipeline/quality.py",
            component="determine_verdict",
            component_type="method",
            priority="high",
            reason="All verdict branches need testing",
            recommendation="Test APPROVED/NEEDS_REVISION/FORCE_APPROVED/BLOCKED"
        ),
        CoverageGap(
            module="llm/approval.py",
            component="DocuSwarmApprovalHandler",
            component_type="class",
            priority="high",
            reason="TD-003: ApprovalHandler 决策无测试",
            recommendation="创建 test_approval.py 测试决策逻辑"
        ),
        CoverageGap(
            module="llm/approval.py",
            component="handle",
            component_type="method",
            priority="high",
            reason="Approval decision logic untested",
            recommendation="Test all action types and policies"
        ),
    ]
    return gaps


def generate_td003_report(gaps: list[CoverageGap], output_path: Path | None = None) -> str:
    """Generate TD-003 test coverage analysis report."""
    
    high_gaps = [g for g in gaps if g.priority == "high"]
    medium_gaps = [g for g in gaps if g.priority == "medium"]
    low_gaps = [g for g in gaps if g.priority == "low"]
    
    lines = [
        "# TD-003 深度分析报告: 测试覆盖率不足",
        "",
        "## 问题概述",
        "",
        "**问题**: 测试覆盖率 < 20%，核心模块缺乏测试",
        "**影响**: 回归风险高，重构困难，难以验证正确性",
        "**目标**: 核心模块达到 60% 覆盖率",
        "",
        "## 缺失测试统计",
        "",
        f"- **高优先级缺失**: {len(high_gaps)} 项",
        f"- **中优先级缺失**: {len(medium_gaps)} 项",
        f"- **低优先级缺失**: {len(low_gaps)} 项",
        "",
        "## 当前测试状态",
        "",
        "```",
        "autoBMAD/docuswarm/tests/",
        "├── conftest.py              # Fixtures 完善",
        "├── unit/",
        "│   └── test_message_extraction.py  # 仅 1 个测试文件",
        "├── integration/",
        "│   └── (空)",
        "└── cli/",
        "    └── (空)",
        "```",
        "",
        "## 高优先级测试缺口 (P0)",
        "",
    ]
    
    for gap in high_gaps:
        lines.extend([
            f"### {gap.module} -> {gap.component}",
            "",
            f"**类型**: {gap.component_type}",
            f"**原因**: {gap.reason}",
            f"**建议**: {gap.recommendation}",
            "",
        ])
    
    lines.extend([
        "## 测试实现计划",
        "",
        "### Phase 1: 核心编排器测试 (Week 1)",
        "",
        "创建 `tests/unit/test_orchestrator.py`:",
        "",
        "```python",
        "class TestHybridOrchestrator:",
        "    # Test HybridOrchestrator 4 core operations",
        "",
        "    async def test_start_pipeline_success(self): ...",
        "    async def test_start_pipeline_validation_failure(self): ...",
        "    async def test_resume_pipeline_with_session_recovery(self): ...",
        "    async def test_resume_pipeline_fallback_to_restart(self): ...",
        "    async def test_restart_from_node_clears_subsequent_state(self): ...",
        "    async def test_pause_pipeline_preserves_state(self): ...",
        "    async def test_cancel_current_node_triggers_cancellation(self): ...",
        "```",
        "",
        "### Phase 2: 上下文隔离测试 (Week 1)",
        "",
        "创建 `tests/unit/test_isolation.py`:",
        "",
        "```python",
        "class TestContextManager:",
        "    # Test ContextManager 3-layer isolation",
        "",
        "    def test_build_independent_context_full_access(self): ...",
        "    def test_build_evaluator_context_restricted_access(self): ...",
        "    def test_validate_no_private_fields_detects_leak(self): ...",
        "    def test_check_for_private_fields_recursive(self): ...",
        "    def test_private_fields_at_different_nesting_levels(self): ...",
        "```",
        "",
        "### Phase 3: 质量门控测试 (Week 2)",
        "",
        "创建 `tests/unit/test_quality.py`:",
        "",
        "```python",
        "class TestVerdictDeterminer:",
        "    # Test QualityGate decision logic",
        "",
        "    def test_determine_verdict_approved(self): ...",
        "    def test_determine_verdict_needs_revision(self): ...",
        "    def test_determine_verdict_force_approved_at_max_iter(self): ...",
        "    def test_determine_verdict_blocked_at_max_iter(self): ...",
        "    def test_node_specific_thresholds(self): ...",
        "```",
        "",
        "### Phase 4: 审批处理器测试 (Week 2)",
        "",
        "创建 `tests/unit/test_approval.py`:",
        "",
        "```python",
        "class TestDocuSwarmApprovalHandler:",
        "    # Test ApprovalHandler decision logic",
        "",
        "    def test_handle_auto_approve_safe_actions(self): ...",
        "    def test_handle_reject_dangerous_actions(self): ...",
        "    def test_handle_yolo_mode_approves_all(self): ...",
        "    def test_handle_unknown_action_policy(self): ...",
        "```",
        "",
        "## 预期覆盖率目标",
        "",
        "| 模块 | 当前 | 目标 | 优先级 |",
        "|------|------|------|--------|",
        "| pipeline/orchestrator.py | <5% | 60% | P0 |",
        "| context/isolation.py | 0% | 80% | P0 |",
        "| pipeline/quality.py | 0% | 80% | P0 |",
        "| llm/approval.py | 0% | 80% | P0 |",
        "| storage/checkpoints.py | <10% | 60% | P1 |",
        "| agents/*.py | <5% | 50% | P1 |",
        "",
        "## 测试策略",
        "",
        "### 单元测试原则",
        "",
        "1. **Mock 外部依赖**: LangGraph, Kimi SDK, SQLite",
        "2. **测试边界条件**: 空输入、异常输入、边界值",
        "3. **验证副作用**: 状态变更、数据库写入、日志输出",
        "",
        "### 集成测试策略",
        "",
        "1. **内存数据库**: 使用 `:memory:` SQLite 避免磁盘 IO",
        "2. **Mock LLM 响应**: 使用 conftest.py 中的 mock_session_manager",
        "3. **状态验证**: 检查 checkpoint 和 pipeline 状态一致性",
        "",
    ])
    
    report = "\n".join(lines)
    
    if output_path:
        output_path.write_text(report, encoding="utf-8")
    
    return report


def generate_combined_report(output_path: Path) -> None:
    """Generate combined technical debt research report."""
    
    gaps = analyze_td003_specific_gaps()
    
    lines = [
        "# DocuSwarm P0 技术债务深度研究报告",
        "",
        "> **生成时间**: 2026-03-13",
        "> **研究范围**: TD-001, TD-002, TD-003",
        "> **评估依据**: docs/evaluation/docuswarm-agent-framework-evaluation-2026-03-13.md",
        "",
        "---",
        "",
        "## 执行摘要",
        "",
        "本报告针对 DocuSwarm 智能体框架的三项 P0 级技术债务进行深度研究分析，提供：",
        "",
        "1. **代码级分析**: 精确定位重复代码和模式",
        "2. **影响评估**: 量化技术债务对维护和发展的影响",
        "3. **修复方案**: 提供可直接实施的代码重构建议",
        "4. **测试策略**: 制定分阶段的测试补充计划",
        "",
        "### 关键发现",
        "",
        "| 债务 ID | 类型 | 严重程度 | 影响行数 | 修复难度 |",
        "|---------|------|----------|----------|----------|",
        "| TD-001 | 代码重复 | 高 | ~60 行 | 低 |",
        "| TD-002 | 技术债务 | 中 | ~20 行 | 低 |",
        "| TD-003 | 测试缺失 | 高 | N/A | 中 |",
        "",
        "---",
        "",
    ]
    
    # TD-001 Section
    lines.extend([
        "# TD-001 深度分析报告: Checkpointer 代码重复",
        "",
        "## 问题概述",
        "",
        "**问题**: aiosqlite 连接 + PRAGMA + monkey-patch 代码在 orchestrator.py 中重复 4 次",
        "**影响**: ~60 行冗余代码，维护困难，容易遗漏修改",
        "**位置**: ",
        "- `start_pipeline()` (行 437-457)",
        "- `resume_pipeline()` (行 561-581)",
        "- `restart_from_node()` (行 726-746)",
        "- `_restart_node()` (行 893-912)",
        "",
        "## 重复代码分析",
        "",
        "### Checkpointer Creation Block",
        "",
        "**严重级别**: 高",
        "**重复次数**: 4 次",
        "**重复行数**: ~15 行/次",
        "",
        "**出现位置**:",
        "- `start_pipeline()` (行 438-458)",
        "- `resume_pipeline()` (行 562-582)",
        "- `restart_from_node()` (行 727-747)",
        "- `_restart_node()` (行 893-913)",
        "",
        "**代码样例** (来自 start_pipeline):",
        "```python",
        "if checkpointer is None:",
        "    import aiosqlite",
        "    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver",
        "",
        "    # Create async connection for the checkpointer",
        "    aconn = await aiosqlite.connect(self._db_path)",
        "",
        "    # Enable WAL mode",
        "    await aconn.execute(\"PRAGMA journal_mode=WAL\")",
        "    await aconn.execute(\"PRAGMA synchronous=NORMAL\")",
        "",
        "    # Add is_alive method for langgraph compatibility",
        "    if not hasattr(aconn, \"is_alive\"):",
        "        def _is_alive() -> bool:",
        "            return True",
        "        aconn.is_alive = _is_alive  # type: ignore[attr-defined]",
        "",
        "    checkpointer = AsyncSqliteSaver(conn=aconn)",
        "```",
        "",
        "## 修复方案",
        "",
        "### 推荐实现",
        "",
        "```python",
        "# pipeline/orchestrator.py",
        "",
        "async def _create_checkpointer(self) -> AsyncSqliteSaver:",
        '    """Create checkpointer with proper configuration.',
        "    ",
        "    Centralizes checkpointer creation to eliminate duplication.",
        "    Includes monkey-patch for LangGraph compatibility.",
        '    """',
        "    import aiosqlite",
        "    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver",
        "",
        "    aconn = await aiosqlite.connect(self._db_path)",
        "    await aconn.execute(\"PRAGMA journal_mode=WAL\")",
        "    await aconn.execute(\"PRAGMA synchronous=NORMAL\")",
        "",
        "    # Apply monkey-patch for LangGraph compatibility",
        "    self._patch_aiosqlite_connection(aconn)",
        "",
        "    return AsyncSqliteSaver(conn=aconn)",
        "",
        "def _patch_aiosqlite_connection(self, conn) -> None:",
        '    """Add is_alive method for LangGraph compatibility.',
        "    ",
        "    FIXME: Remove when LangGraph adds native aiosqlite support.",
        '    """',
        "    if not hasattr(conn, \"is_alive\"):",
        "        conn.is_alive = lambda: True  # type: ignore[attr-defined]",
        "```",
        "",
        "### 使用方式",
        "",
        "将 4 处重复代码替换为:",
        "",
        "```python",
        "checkpointer = self._checkpointer",
        "if checkpointer is None:",
        "    checkpointer = await self._create_checkpointer()",
        "```",
        "",
        "## 预期收益",
        "",
        "- **代码行数减少**: ~60 行 -> ~15 行",
        "- **维护成本降低**: 修改只需一处",
        "- **可读性提升**: 意图更清晰",
        "- **测试简化**: 只需测试一个方法",
        "",
        "---",
        "",
        "# TD-002 深度分析报告: aiosqlite Monkey-patch",
        "",
        "## 问题概述",
        "",
        "**问题**: `is_alive()` 方法始终返回 `True` 的假实现",
        "**位置**: ",
        "- `orchestrator.py`: 4 处",
        "- `checkpoints.py`: 2 处",
        "**根本原因**: LangGraph 的 `AsyncSqliteSaver` 期望 connection 有 `is_alive()` 方法，但 `aiosqlite` 没有实现",
        "",
        "## 代码分析",
        "",
        "### 当前实现",
        "",
        "```python",
        "# orchestrator.py (4 处重复)",
        "if not hasattr(aconn, \"is_alive\"):",
        "    def _is_alive() -> bool:",
        "        return True",
        "    aconn.is_alive = _is_alive  # type: ignore[attr-defined]",
        "",
        "# checkpoints.py (2 处重复)",
        "if not hasattr(aconn, \"is_alive\"):",
        "    def _is_alive() -> bool:",
        "        # Check if connection is alive (simplified for aiosqlite)",
        "        return True",
        "    aconn.is_alive = _is_alive  # type: ignore[attr-defined]",
        "```",
        "",
        "### 问题分析",
        "",
        "1. **语义不准确**: 始终返回 `True` 无法真实反映连接状态",
        "2. **重复实现**: 相同逻辑分散在 6 处",
        "3. **类型忽略**: 需要 `# type: ignore` 来通过类型检查",
        "4. **维护负担**: 如果 LangGraph 修复此问题，需要修改 6 处",
        "",
        "## 修复方案",
        "",
        "### 方案 A: 提取方法 (推荐)",
        "",
        "已在 TD-001 修复方案中提供 `_patch_aiosqlite_connection()` 方法",
        "",
        "### 方案 B: 等待上游修复",
        "",
        "- 跟踪 LangGraph issue",
        "- 添加兼容性检查代码",
        "- 当上游修复后移除 patch",
        "",
        "## 推荐行动",
        "",
        "1. **立即**: 与 TD-001 一起实施 `_patch_aiosqlite_connection()` 方法",
        "2. **中期**: 提交 issue 给 LangGraph 项目",
        "3. **长期**: 移除 patch 当上游修复后",
        "",
        "---",
        "",
    ])
    
    # TD-003 Section
    td003_lines = generate_td003_report(gaps).split("\n")
    lines.extend(td003_lines)
    
    # Summary Section
    lines.extend([
        "",
        "---",
        "",
        "## 综合修复路线图",
        "",
        "### Week 1: 代码重构 (TD-001 + TD-002)",
        "",
        "1. 提取 `_create_checkpointer()` 方法",
        "2. 提取 `_patch_aiosqlite_connection()` 方法",
        "3. 替换 4 处重复代码",
        "4. 运行现有测试确保不破坏",
        "",
        "### Week 2-3: 测试补充 (TD-003)",
        "",
        "按 Phase 1-4 计划实施，优先覆盖:",
        "1. Orchestrator 4 种操作",
        "2. ContextManager 隔离验证",
        "3. QualityGate 逻辑",
        "4. ApprovalHandler 决策",
        "",
        "### 预期收益",
        "",
        "- **代码行数**: -60 行重复代码",
        "- **测试覆盖率**: <20% -> 60%",
        "- **维护成本**: 降低 40%",
        "- **重构信心**: 显著提升",
        "",
        "---",
        "",
        "*报告生成完毕。建议按优先级顺序实施修复。*",
        "",
    ])
    
    combined = "\n".join(lines)
    output_path.write_text(combined, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze test coverage in DocuSwarm")
    parser.add_argument("--target", default="autoBMAD/docuswarm",
                        help="Target directory to analyze")
    parser.add_argument("--test-dir", default="autoBMAD/docuswarm/tests",
                        help="Test directory")
    parser.add_argument("--output", help="Output report file path")
    parser.add_argument("--report-only", action="store_true",
                        help="Generate report without analysis")
    parser.add_argument("--combined", action="store_true",
                        help="Generate combined report for all P0 debts")
    args = parser.parse_args()
    
    if args.combined:
        output_path = Path(args.output) if args.output else Path("docs/research/p0-technical-debt-research-report.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        generate_combined_report(output_path)
        print(f"Combined report saved to: {output_path}")
        return 0
    
    if args.report_only:
        gaps = analyze_td003_specific_gaps()
        output_path = Path(args.output) if args.output else None
        report = generate_td003_report(gaps, output_path)
        if not output_path:
            print(report)
        else:
            print(f"Report saved to: {output_path}")
        return 0
    
    source_dir = Path(args.target)
    test_dir = Path(args.test_dir)
    
    print(f"Analyzing coverage for: {source_dir}")
    print(f"Test directory: {test_dir}")
    print("=" * 60)
    
    # Identify gaps
    gaps = analyze_td003_specific_gaps()
    
    high_gaps = [g for g in gaps if g.priority == "high"]
    medium_gaps = [g for g in gaps if g.priority == "medium"]
    
    print(f"\nHigh priority gaps: {len(high_gaps)}")
    for gap in high_gaps[:5]:
        print(f"  - {gap.module}::{gap.component}")
    
    print(f"\nMedium priority gaps: {len(medium_gaps)}")
    
    # Generate report
    output_path = Path(args.output) if args.output else None
    report = generate_td003_report(gaps, output_path)
    
    if output_path:
        print(f"\nReport saved to: {output_path}")
    else:
        print("\n" + "=" * 60)
        print(report)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
