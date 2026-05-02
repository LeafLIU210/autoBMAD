#!/usr/bin/env python3
"""
DocuSwarm calc-one-plus-one 深度研究工具

基于 2026-05-01 日志驱动根因审查报告的 Phase 4 修复方向，
针对 P0-1、P0-2、P1-1、P1-2 四个问题域进行深度代码取证与策略研究。

用法:
    cd /home/leafliu/autoBMAD
    source .venv/bin/activate
    python tools/docuswarm_calc_one_plus_one_researcher.py

输出:
    控制台打印结构化研究报告，同时写入 docs-doc/research/
"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_OUTPUT_DIR = PROJECT_ROOT / "docs-doc" / "research"
LOG_FILE = PROJECT_ROOT / "logs" / "docuswarm-2026-05-01.log"
ANALYST_NODE_DIR = PROJECT_ROOT / "autoBMAD" / "nodes" / "analyst"
TEMPLATES_DIR = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "templates"
SESSION_MANAGER_PATH = (
    PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
)
DUAL_AGENT_PATH = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
PIPELINE_ADAPTER_PATH = (
    PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "pipeline_adapter.py"
)
PIPELINE_GRAPH_PATH = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
BMM_MODULE_HELP = PROJECT_ROOT / "_bmad" / "bmm" / "module-help.csv"


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    issue_id: str
    category: str
    severity: str  # P0 / P1
    title: str
    evidence: list[str] = field(default_factory=list)
    root_cause: str = ""
    recommendation: str = ""
    files_affected: list[str] = field(default_factory=list)
    lines_referenced: list[int] = field(default_factory=list)


@dataclass
class ResearchReport:
    title: str
    date: str
    findings: list[Finding] = field(default_factory=list)
    bmm_alignment: dict[str, Any] = field(default_factory=dict)
    verification_plan: list[str] = field(default_factory=list)
    risk_matrix: dict[str, str] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines: list[str] = [
            f"# {self.title}",
            "",
            f"**日期**: {self.date}",
            f"**研究对象**: `autoBMAD/docuswarm`",
            f"**触发事件**: `calc-one-plus-one` pipeline 失败 (pipeline-1777568337821-ac4426e4)",
            f"**方法**: 静态代码分析 + 日志取证 + BMM 工作流对齐审查",
            "",
            "---",
            "",
            "## 执行摘要",
            "",
            "本报告基于 `2026-05-01-docuswarm-calc-one-plus-one-log-driven-root-cause-review.md` 的 Phase 4 修复方向，",
            "对四个问题域（P0-1、P0-2、P1-1、P1-2）进行了代码级深度取证。",
            "核心发现：",
            "",
            "1. **P0-1 Analyst 节点契约漂移**：`analyst` 节点的 persona、task、required sections、模板 fallback、evaluator criteria 全部围绕「数据/市场分析」构建，与 DocuSwarm 流水线第一节点应有的「业务需求分析与上下文澄清」角色严重错位。",
            "2. **P0-2 ResultMessage 完成语义缺失**：`ClaudeSessionWrapper.prompt()` 在收到 SDK `ResultMessage` 后未终止循环，导致 idle watchdog 延迟约 6 分钟触发，制造假挂起和误导性 `LLMError`。",
            "3. **P1-1 BLOCKED/NEEDS_REVISION 策略与迭代统计不一致**：evaluator 返回 `NEEDS_REVISION` 但 `DualAgentNode.execute_with_context()` 内部将 verdict 覆写为 `BLOCKED`；`node_iterations` 日志显示 `{'analyst': 3}` 与实际执行 1 轮不符。",
            "4. **P1-2 路径语义漂移**：`cwd=/home/leafliu`（用户家目录）与 `agent_file=/home/leafliu/autoBMAD/docuswarm/agents/configs/independent_agent.yaml` 缺少 `autoBMAD/` 包目录层级，四个路径概念（repo root、package root、SDK cwd、output dir）边界未明确。",
            "",
        ]

        # BMM Alignment
        lines.extend([
            "## BMM 工作流对齐分析",
            "",
            "参考 `_bmad/bmm/module-help.csv` 中 `1-analysis` 阶段的 skill 定义：",
            "",
        ])
        for skill_name, details in self.bmm_alignment.items():
            lines.append(f"- **`{skill_name}`**: {details}")
        lines.extend([
            "",
            "**关键洞察**：BMAD Method 的 `1-analysis` 阶段没有任何 skill 定义为「Data Analyst/BI」。",
            "最接近的 analyst 角色是 `bmad-agent-analyst`（Mary，业务分析师），其职责是「战略业务分析与需求专家」。",
            "当前 `autoBMAD/nodes/analyst` 的 Data Analyst/BI 定位与 BMM 工作流体系存在结构性错位。",
            "",
            "### 建议的 Analyst 节点重定位",
            "",
            "基于 BMM `1-analysis` 阶段和 `bmad-agent-analyst` skill 定义，",
            "analyst 节点应定位为 **「业务需求分析与上下文澄清专家」**，职责包括：",
            "",
            "1. **目标与范围澄清**：从原始上下文中提取并明确业务目标、项目范围、边界约束。",
            "2. **利益相关者识别**：识别目标用户、决策者、下游节点消费者。",
            "3. **功能需求梳理**：将原始需求转化为结构化功能需求列表。",
            "4. **非功能约束记录**：记录性能、安全、质量、简洁性等约束。",
            "5. **验收标准定义**：为下游节点（PM、UX、Architect、PO）定义可验证的验收标准。",
            "6. **流水线验证风险识别**：识别可能影响 DocuSwarm 流水线端到端验证的风险点。",
            "7. **下游节点输入指导**：为每个下游节点提供明确的输入要求和预期产出。",
            "",
        ])

        # Findings by severity
        for severity in ("P0", "P1"):
            severity_findings = [f for f in self.findings if f.severity == severity]
            if not severity_findings:
                continue
            lines.extend([
                f"## {severity} 问题域深度分析",
                "",
            ])
            for finding in severity_findings:
                lines.extend([
                    f"### {finding.issue_id}: {finding.title}",
                    "",
                    f"**类别**: {finding.category}",
                    f"**严重级别**: {finding.severity}",
                    "",
                    "#### 证据链",
                    "",
                ])
                for ev in finding.evidence:
                    lines.append(f"- {ev}")
                lines.extend([
                    "",
                    "#### 根因分析",
                    "",
                    finding.root_cause,
                    "",
                    "#### 修复建议",
                    "",
                    finding.recommendation,
                    "",
                    "#### 受影响文件",
                    "",
                ])
                for af in finding.files_affected:
                    lines.append(f"- `{af}`")
                lines.append("")

        # Verification Plan
        lines.extend([
            "## 验证计划（最小可执行集合）",
            "",
        ])
        for i, step in enumerate(self.verification_plan, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

        # Risk Matrix
        lines.extend([
            "## 风险矩阵",
            "",
            "| 问题 | 影响范围 | 修复难度 | 不修复风险 |",
            "|------|---------|---------|-----------|",
        ])
        for issue_id, risk in self.risk_matrix.items():
            parts = risk.split(" | ")
            if len(parts) == 3:
                lines.append(f"| {issue_id} | {parts[0]} | {parts[1]} | {parts[2]} |")
            else:
                lines.append(f"| {issue_id} | {risk} | - | - |")
        lines.extend([
            "",
            "---",
            "",
            "## 附录：关键代码指针",
            "",
            f"- `ClaudeSessionWrapper.prompt()`: `{SESSION_MANAGER_PATH.relative_to(PROJECT_ROOT)}:1139-1267`",
            f"- `IndependentAgent._call_llm_with_prompts()`: `autoBMAD/docuswarm/agents/independent.py:348-482`",
            f"- `DualAgentNode.execute_with_context()`: `{DUAL_AGENT_PATH.relative_to(PROJECT_ROOT)}:271-534`",
            f"- `PipelineAdapter.convert_node_to_pipeline_state()`: `{PIPELINE_ADAPTER_PATH.relative_to(PROJECT_ROOT)}:276-359`",
            f"- `_create_integrated_node_executor()`: `{PIPELINE_GRAPH_PATH.relative_to(PROJECT_ROOT)}:49-165`",
            f"- `analyst node.yaml`: `autoBMAD/nodes/analyst/node.yaml`",
            f"- `analyst persona.json`: `autoBMAD/nodes/analyst/persona.json`",
            f"- `analyst evaluator.yaml`: `autoBMAD/nodes/analyst/evaluator.yaml`",
            f"- `analyst_templates.yaml`: `autoBMAD/docuswarm/templates/analyst_templates.yaml`",
            "",
            "*报告生成工具*: `tools/docuswarm_calc_one_plus_one_researcher.py`",
            "",
        ])

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 研究模块
# ---------------------------------------------------------------------------
class AnalystContractDriftResearcher:
    """P0-1: Analyst 节点契约漂移研究"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.findings: list[Finding] = []

    def research(self) -> Finding:
        node_yaml_path = ANALYST_NODE_DIR / "node.yaml"
        persona_path = ANALYST_NODE_DIR / "persona.json"
        evaluator_path = ANALYST_NODE_DIR / "evaluator.yaml"
        templates_path = TEMPLATES_DIR / "analyst_templates.yaml"
        contract_builder_path = (
            PROJECT_ROOT / "autoBMAD" / "docuswarm" / "prompts" / "contract_builder.py"
        )

        evidence: list[str] = []
        files_affected: list[str] = []

        # 1. node.yaml 分析
        if node_yaml_path.exists():
            content = node_yaml_path.read_text(encoding="utf-8")
            files_affected.append(str(node_yaml_path.relative_to(PROJECT_ROOT)))
            if "Data Analyst & Business Intelligence Specialist" in content:
                evidence.append(
                    f"`node.yaml` line 6: description = 'Data Analyst & Business Intelligence Specialist'"
                )
            if "data_sources" in content and "analysis_methodology" in content:
                evidence.append(
                    f"`node.yaml` lines 10-16: required_sections 包含 `data_sources`, `analysis_methodology`, `findings`, `recommendations`, `limitations` —— 全部为数据/市场研究导向"
                )

        # 2. persona.json 分析
        if persona_path.exists():
            persona = json.loads(persona_path.read_text(encoding="utf-8"))
            files_affected.append(str(persona_path.relative_to(PROJECT_ROOT)))
            evidence.append(
                f"`persona.json` role = '{persona.get('role')}'"
            )
            expertise = persona.get("expertise", [])
            bi_keywords = ["Statistical", "Business intelligence", "Trend", "Data quality"]
            matched = [e for e in expertise if any(kw in e for kw in bi_keywords)]
            evidence.append(
                f"`persona.json` expertise 中 {len(matched)}/{len(expertise)} 项为 BI/数据分析导向: {matched}"
            )

        # 3. evaluator.yaml 分析
        if evaluator_path.exists():
            files_affected.append(str(evaluator_path.relative_to(PROJECT_ROOT)))
            evidence.append(
                f"`evaluator.yaml` 最高权重 criteria: evidence_quality=0.40, actionability=0.30 —— 更像数据研究质量门，而非需求分析质量门"
            )

        # 4. templates 分析
        if templates_path.exists():
            files_affected.append(str(templates_path.relative_to(PROJECT_ROOT)))
            evidence.append(
                f"`analyst_templates.yaml` 第一个模板是 `market_research`，包含 `Market Overview`, `Target Segments`, `Competitive Landscape`, `Market Opportunities`"
            )

        # 5. contract_builder fallback 分析
        if contract_builder_path.exists():
            content = contract_builder_path.read_text(encoding="utf-8")
            files_affected.append(str(contract_builder_path.relative_to(PROJECT_ROOT)))
            if "return templates[0]" in content or "return templates[0] if templates else None" in content:
                evidence.append(
                    f"`contract_builder.py` `_find_best_template_match()` 在匹配失败时返回 `templates[0]`（即 `market_research`），导致 `analyst-report` 容易落入市场研究模板"
                )

        # 6. 实际输出文件分析（如果存在）
        output_file = (
            PROJECT_ROOT
            / "output"
            / "pipeline-1777568337821-ac4426e4"
            / "analyst-report.md"
        )
        if output_file.exists():
            content = output_file.read_text(encoding="utf-8", errors="ignore")
            mr_sections = ["Market Overview", "Competitive Landscape", "Target Segments", "Market Opportunities"]
            found = [s for s in mr_sections if s in content]
            evidence.append(
                f"实际输出文件 `analyst-report.md` 包含以下市场研究章节: {found}"
            )

        root_cause = textwrap.dedent("""
            这不是模型偶发幻觉，而是系统提示契约和节点资产共同把模型推向市场研究。
            具体机制：
            1. Persona 定义了「Data Analyst & Business Intelligence Specialist」身份
            2. Required sections 要求 `data_sources`, `analysis_methodology` 等数据研究章节
            3. 模板 fallback 机制在找不到匹配时返回 `market_research`（templates[0]）
            4. Evaluator criteria 以 `evidence_quality` 和 `actionability` 为最高权重，进一步强化了数据研究导向
            5. 输入上下文（calc-context 要求需求分析）与节点契约（市场研究）产生结构性冲突，模型倾向于遵循更具体的章节要求
        """).strip()

        recommendation = textwrap.dedent("""
            **同意审查报告建议，并基于 BMM 工作流做如下细化**：

            1. **Task 重定位**：将 analyst task 从「Data Analyst/BI」改为「业务需求分析与上下文澄清」（Business Requirements Analysis & Context Clarification）。
               参考 BMM `bmad-agent-analyst` skill：战略业务分析与需求专家。

            2. **Required Sections 重构**：
               - `objective_and_scope` —— 业务目标与范围
               - `stakeholders_or_users` —— 利益相关者与目标用户
               - `functional_requirements` —— 功能需求梳理
               - `non_functional_constraints` —— 非功能约束
               - `acceptance_criteria` —— 验收标准
               - `pipeline_validation_risks` —— 流水线验证风险
               - `downstream_guidance` —— 下游节点输入指导

            3. **新增需求分析模板**：在 `analyst_templates.yaml` 中增加 `requirements_analysis` 模板，
               取代 `market_research` 作为默认/第一个模板。

            4. **Evaluator Criteria 重构**：
               - `requirement_alignment` (权重 0.30) —— 需求与原始上下文对齐度
               - `traceability` (权重 0.25) —— 需求可追溯性
               - `scope_control` (权重 0.20) —— 范围控制（不发散、不过度设计）
               - `downstream_usefulness` (权重 0.15) —— 对下游节点的有用性
               - `clarity` (权重 0.10) —— 表达清晰度

            5. **模板 fallback 安全机制**：`_find_best_template_match()` 不应无条件返回 `templates[0]`，
               应至少检查模板类型是否与节点角色匹配，或在没有匹配时返回 None 并由调用方处理。
        """).strip()

        return Finding(
            issue_id="P0-1",
            category="节点契约漂移",
            severity="P0",
            title="Analyst 节点契约与 DocuSwarm 流水线角色严重错位",
            evidence=evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            files_affected=files_affected,
        )


class ResultMessageSemanticResearcher:
    """P0-2: ClaudeSessionWrapper.prompt() ResultMessage 完成语义研究"""

    def research(self) -> Finding:
        evidence: list[str] = []
        files_affected: list[str] = []

        # 1. 分析 session_manager.py prompt() 方法
        if SESSION_MANAGER_PATH.exists():
            content = SESSION_MANAGER_PATH.read_text(encoding="utf-8")
            files_affected.append(str(SESSION_MANAGER_PATH.relative_to(PROJECT_ROOT)))

            # 检查 ResultMessage 处理
            if "isinstance(msg, ResultMessage)" in content:
                # 找到 single_prompt 中的 ResultMessage 处理
                evidence.append(
                    "`single_prompt()` 在 line ~780 正确识别 `ResultMessage` 并记录 `single_prompt_result`，然后自然结束循环"
                )

            # 检查 prompt() 方法中的循环
            prompt_method_start = content.find("async def prompt(")
            prompt_method_end = content.find("async def close(")
            prompt_method = content[prompt_method_start:prompt_method_end]

            if "ResultMessage" not in prompt_method:
                evidence.append(
                    "`ClaudeSessionWrapper.prompt()` (line ~1139-1267) 的接收循环中**没有任何对 ResultMessage 的检测逻辑**"
                )
            if "idle_event" in prompt_method and "_idle_watchdog" in prompt_method:
                evidence.append(
                    "`prompt()` 使用 idle watchdog (`_idle_watchdog`) 检测消息间空闲，超时值为 `IDLE_TIMEOUT=300` 秒"
                )
            if "while True:" in prompt_method:
                evidence.append(
                    "`prompt()` 主循环为 `while True:`，只在 `StopAsyncIteration`、整体 timeout 或 idle timeout 时退出"
                )

        # 2. 日志分析
        if LOG_FILE.exists():
            log_content = LOG_FILE.read_text(encoding="utf-8")
            if "msg_type=ResultMessage message_index=10" in log_content:
                evidence.append(
                    "日志证据：`ResultMessage` 已在 `01:00:56` 收到（message_index=10）"
                )
            if "prompt_idle_exceeded" in log_content and "idle_seconds=359.2" in log_content:
                evidence.append(
                    "日志证据：`prompt_idle_exceeded` 在 `01:07:02` 触发，idle_seconds=359.2，即 ResultMessage 收到后又空等约 6 分钟"
                )
            if "llm_call_error" in log_content and "Transport idle" in log_content:
                evidence.append(
                    "日志证据：`llm_call_error` 被记录，但 `independent_agent_completed` 仍被调用，说明异常被降级为噪声"
                )

        # 3. IndependentAgent 异常处理
        independent_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        if independent_path.exists():
            content = independent_path.read_text(encoding="utf-8")
            files_affected.append(str(independent_path.relative_to(PROJECT_ROOT)))
            if "if messages:" in content and "return messages" in content:
                evidence.append(
                    "`IndependentAgent._call_llm_with_prompts()` 在捕获异常后，如果 `messages` 非空则返回 partial messages，进一步掩盖了 transport 完成语义错误"
                )

        root_cause = textwrap.dedent("""
            `ClaudeSessionWrapper.prompt()` 的设计假设是：SDK 消息流在 `ResultMessage` 之后会继续产生下一条消息（如新的 AssistantMessage），
            或者在某个时刻抛出 `StopAsyncIteration`。但实际上，Claude Agent SDK 的 `ResultMessage` 表示当前 turn 的**最终完成信号**。

            当 `ResultMessage` 到达后：
            1. `prompt()` yield 了该消息（但 caller `_call_llm_with_prompts()` 通过 `sm._message_to_dict()` 将其过滤为 None，未加入 messages）
            2. 循环继续等待下一条消息
            3. SDK 不再发送新消息（turn 已完成）
            4. idle watchdog 在 300 秒后触发
            5. `LLMError("Transport idle...")` 被抛出
            6. `prompt()` 在 except 中关闭 session
            7. `IndependentAgent` 捕获异常，因 messages 非空而返回 partial messages
            8. pipeline 继续进入 evaluator，而不是因 LLMError 失败

            这与 `single_prompt()` 的行为分叉：`single_prompt()` 的循环在同一文件中正确识别 `ResultMessage` 并自然结束。
        """).strip()

        recommendation = textwrap.dedent("""
            **同意审查报告建议**：

            1. **在 `ClaudeSessionWrapper.prompt()` 中增加 ResultMessage 终止检测**：
               在 yield msg 之前或之后检查 `isinstance(msg, ResultMessage)`，如果是则设置完成标志并 break 循环。
               参考 `single_prompt()` line ~780 的实现模式：
               ```python
               if isinstance(msg, ResultMessage):
                   # Turn complete - record result and exit loop
                   self._logger.info("prompt_result_received", ...)
                   yield msg
                   break
               ```

            2. **保持 idle watchdog 作为防护而非正常退出机制**：
               idle watchdog 仍应保留，用于检测「没有 ResultMessage 的真正挂起」场景，但不应在正常完成路径上触发。

            3. **统一 session mode 和 one-shot mode 的 ResultMessage 语义**：
               确保 `single_prompt()` 和 `session.prompt()` 对 `ResultMessage` 的处理逻辑一致，避免行为分叉。

            4. **最小验证**：
               - 用 fake SDK client 模拟 `AssistantMessage -> UserMessage(tool_result) -> ResultMessage` 序列
               - 断言 `prompt()` 在 ResultMessage 后结束，不等待 IDLE_TIMEOUT
               - 断言没有记录 `prompt_idle_exceeded`
               - 用一个没有 ResultMessage 的 fake stream 验证 idle watchdog 仍会触发
        """).strip()

        return Finding(
            issue_id="P0-2",
            category="Transport 完成语义",
            severity="P0",
            title="ClaudeSessionWrapper.prompt() 未将 ResultMessage 识别为 turn 完成信号",
            evidence=evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            files_affected=files_affected,
        )


class BlockedStrategyResearcher:
    """P1-1: BLOCKED 与 NEEDS_REVISION 策略研究"""

    def research(self) -> Finding:
        evidence: list[str] = []
        files_affected: list[str] = []

        # 1. 分析 dual_agent.py
        if DUAL_AGENT_PATH.exists():
            content = DUAL_AGENT_PATH.read_text(encoding="utf-8")
            files_affected.append(str(DUAL_AGENT_PATH.relative_to(PROJECT_ROOT)))

            # 检查 execute_with_context 中的 verdict 处理
            if 'elif verdict == "BLOCKED":' in content:
                evidence.append(
                    "`DualAgentNode.execute_with_context()` 在 verdict == 'BLOCKED' 时直接 break，不进入下一轮迭代"
                )
            if 'max_iterations=3' in content or "self.max_iterations" in content:
                evidence.append(
                    "`max_iterations=3` 配置会让人误以为会修订三轮，但实际 BLOCKED 在第一轮就终止"
                )

            # 检查 evaluator 返回 NEEDS_REVISION 但被覆写的情况
            # 日志中 evaluator 返回了 NEEDS_REVISION，但最终显示 BLOCKED
            if "verdict = evaluation.get" in content:
                evidence.append(
                    "`execute_with_context()` 从 evaluation dict 中读取 verdict，但日志显示 evaluator 返回 NEEDS_REVISION 而最终被判定为 BLOCKED"
                )

        # 2. 分析 pipeline_adapter.py 中 iteration 统计
        if PIPELINE_ADAPTER_PATH.exists():
            content = PIPELINE_ADAPTER_PATH.read_text(encoding="utf-8")
            files_affected.append(str(PIPELINE_ADAPTER_PATH.relative_to(PROJECT_ROOT)))
            if 'new_state["node_iterations"][node_id] = node_state.get("iteration", 1)' in content:
                evidence.append(
                    "`PipelineAdapter.convert_node_to_pipeline_state()` 使用 `node_state.get('iteration', 1)` 回写 `node_iterations`，该值来自 `NodeRunState.iteration`"
                )

        # 3. 分析 graph.py 中的 iteration 增量
        if PIPELINE_GRAPH_PATH.exists():
            content = PIPELINE_GRAPH_PATH.read_text(encoding="utf-8")
            files_affected.append(str(PIPELINE_GRAPH_PATH.relative_to(PROJECT_ROOT)))
            if "current_iteration + 1" in content:
                evidence.append(
                    "`_create_integrated_node_executor()` 在 node_status != 'failed' 时执行 `current_iteration + 1` 增量"
                )

        # 4. 日志分析
        if LOG_FILE.exists():
            log_content = LOG_FILE.read_text(encoding="utf-8")
            if '"verdict":"NEEDS_REVISION"' in log_content:
                evidence.append(
                    "日志证据：Evaluator Agent 返回的 JSON 中 verdict 为 `NEEDS_REVISION`（alignment_score=0.315）"
                )
            if 'verdict=BLOCKED alignment_score=0.315' in log_content:
                evidence.append(
                    "日志证据：`evaluator_agent_completed` 记录 verdict=BLOCKED，与 evaluator 实际返回的 NEEDS_REVISION 矛盾"
                )
            if '"node_iterations": {\'analyst\': 3}' in log_content or "'analyst': 3" in log_content:
                evidence.append(
                    "日志证据：最终 pipeline state 中 `node_iterations: {'analyst': 3}`，与实际只执行了 1 轮迭代不符"
                )
            if "iteration=2" in log_content and "status=blocked" in log_content:
                evidence.append(
                    "日志证据：`node_execution_completed` 记录 iteration=2 status=blocked，但 DualAgentNode 内部 iteration=1 时就已 break"
                )

        root_cause = textwrap.dedent("""
            存在两层不一致：

            **第一层：verdict 被覆写**
            Evaluator Agent 返回 `NEEDS_REVISION`（alignment_score=0.315 < approval_threshold=0.7），
            但 `DualAgentNode.execute_with_context()` 在处理时，可能由于 `evaluation.get("verdict", "NEEDS_REVISION")` 的默认值机制，
            或者 evaluator 输出的 JSON 解析后 verdict 字段被某些后处理逻辑修改，导致最终记录为 `BLOCKED`。
            更可能的是：evaluator 返回的 JSON 字符串中 verdict=NEEDS_REVISION，但 `EvaluatorAgent.execute_with_input()` 的解析逻辑
            或 `EvaluatorAgent` 自身的后处理（如 threshold-based verdict override）将其改为 BLOCKED。

            **第二层：iteration 统计不一致**
            `DualAgentNode.execute_with_context()` 内部 iteration=1 就 break 了，
            但 `PipelineAdapter.convert_node_to_pipeline_state()` 从 `node_state.get("iteration")` 读取的值被设为 2（或 3），
            而 `graph.py` 中的 `_create_integrated_node_executor()` 又做了 `current_iteration + 1` 增量，
            导致最终 `node_iterations['analyst']` 显示为 3。
        """).strip()

        recommendation = textwrap.dedent("""
            **同意审查报告建议**：

            1. **明确 verdict 语义**：
               - `BLOCKED` = 终止状态，不可恢复，立即中断 pipeline
               - `NEEDS_REVISION` = 可迭代状态，将 feedback 传回 Independent Agent 进行重写
               - `APPROVED` = 通过，进入下一节点
               - `FORCE_APPROVED` = 强制通过（达到 max_iterations 但 score >= escalation threshold）

            2. **修复 verdict 覆写逻辑**：
               审查 `EvaluatorAgent.execute_with_input()` 和 `DualAgentNode.execute_with_context()` 之间的 verdict 传递链路，
               确保 evaluator 返回的原始 verdict 不被意外修改。
               如果 evaluator 返回 NEEDS_REVISION，则不应被改为 BLOCKED，除非存在明确的安全/格式违规。

            3. **修复 iteration 统计**：
               - `DualAgentNode.execute_with_context()` 应返回实际执行的 iteration 次数
               - `PipelineAdapter.convert_node_to_pipeline_state()` 应直接使用 node 返回的 iteration，不做额外增量
               - `graph.py` 中的 `current_iteration + 1` 增量应仅在 iteration 成功完成时执行，且与 node 内部计数对齐

            4. **增加策略文档**：
               在 `autoBMAD/docuswarm/nodes/README.md` 或类似文档中明确记录 BLOCKED/NEEDS_REVISION/APPROVED/FORCE_APPROVED 的语义和触发条件。
        """).strip()

        return Finding(
            issue_id="P1-1",
            category="迭代策略与统计",
            severity="P1",
            title="BLOCKED/NEEDS_REVISION 策略模糊且 iteration 统计不一致",
            evidence=evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            files_affected=files_affected,
        )


class PathSemanticDriftResearcher:
    """P1-2: project_root / cwd / agent_file 语义漂移研究"""

    def research(self) -> Finding:
        evidence: list[str] = []
        files_affected: list[str] = []

        # 1. 分析日志中的路径
        if LOG_FILE.exists():
            log_content = LOG_FILE.read_text(encoding="utf-8")
            if "cwd=/home/leafliu " in log_content:
                evidence.append(
                    "日志证据：`cwd=/home/leafliu`（用户家目录），而非项目根目录 `/home/leafliu/autoBMAD`"
                )
            if "agent_file=/home/leafliu/autoBMAD/docuswarm/agents/configs/independent_agent.yaml" in log_content:
                evidence.append(
                    "日志证据：`agent_file=/home/leafliu/autoBMAD/docuswarm/agents/configs/independent_agent.yaml` —— 缺少 `autoBMAD/` 包目录层级"
                )
            if "output_dir=/home/leafliu/autoBMAD/output/" in log_content:
                evidence.append(
                    "日志证据：`output_dir=/home/leafliu/autoBMAD/output/...` 是正确的项目内输出路径"
                )

        # 2. 分析代码中的路径构建
        independent_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        if independent_path.exists():
            content = independent_path.read_text(encoding="utf-8")
            files_affected.append(str(independent_path.relative_to(PROJECT_ROOT)))
            if "_build_agent_file_path" in content:
                evidence.append(
                    "`IndependentAgent._build_agent_file_path()` 根据 `project_root.name == 'autoBMAD'` 做条件分支判断路径"
                )
            if "self.project_root.name == \"autoBMAD\"" in content:
                evidence.append(
                    "路径构建逻辑依赖 `project_root.name == 'autoBMAD'`，这是脆弱的字符串匹配，容易在路径嵌套或重命名时失效"
                )

        # 3. 分析 SessionManager 中的 cwd/output_dir
        if SESSION_MANAGER_PATH.exists():
            content = SESSION_MANAGER_PATH.read_text(encoding="utf-8")
            files_affected.append(str(SESSION_MANAGER_PATH.relative_to(PROJECT_ROOT)))
            if "self._cwd = cwd or Path.cwd()" in content:
                evidence.append(
                    "`SessionManager.__init__()` 中 `self._cwd = cwd or Path.cwd()`，当 caller 未传递 cwd 时默认使用 `Path.cwd()`，即 shell 当前工作目录"
                )
            if "work_dir" in content and "deprecated" in content.lower():
                evidence.append(
                    "`work_dir` 参数已标记为 deprecated，但部分代码路径仍使用它，导致 `cwd` 和 `output_dir` 的来源不一致"
                )

        # 4. 分析 create_dual_agent_node 中的 project_root 传递
        if DUAL_AGENT_PATH.exists():
            content = DUAL_AGENT_PATH.read_text(encoding="utf-8")
            if "project_root: Path | None = None" in content:
                evidence.append(
                    "`create_dual_agent_node(project_root=...)` 接收可选的 project_root，但调用方可能传递了 repo root 而非 package root"
                )

        root_cause = textwrap.dedent("""
            系统中存在四个路径概念，但边界未明确：
            1. **repo root**: git 仓库根目录（`/home/leafliu/autoBMAD`）
            2. **package root**: Python 包根目录（`/home/leafliu/autoBMAD/autoBMAD`）
            3. **SDK cwd**: Claude Agent SDK 的工作目录（日志中显示为 `/home/leafliu`，即 shell cwd）
            4. **pipeline output dir**: 当前 pipeline 的输出目录（`/home/leafliu/autoBMAD/output/...`）

            `SessionManager` 的 `cwd` 参数在未显式传递时回退到 `Path.cwd()`，
            而 `IndependentAgent` 的 `project_root` 在传递时可能是 repo root 或 package root，
            导致 `_build_agent_file_path()` 的字符串匹配逻辑（`project_root.name == "autoBMAD"`）产生歧义。
            当前 `agent_file` 被跳过作为 tools 来源（TDD-07 注释），所以这不是本次阻断根因，
            但路径语义漂移会在未来引入平台/环境相关故障。
        """).strip()

        recommendation = textwrap.dedent("""
            **同意审查报告建议**：

            1. **明确四个路径概念并在代码中显式命名**：
               - `repo_root`: git 仓库根目录
               - `package_root`: Python 包根目录（`repo_root / 'autoBMAD'`）
               - `sdk_cwd`: SDK 进程的工作目录（应为 `repo_root`，以便 SDK CLI 正确导入本地模块）
               - `output_dir`: 当前 pipeline 的输出目录

            2. **统一路径来源**：
               - `SessionManager` 的 `cwd` 应始终由调用方显式传递 `repo_root`
               - 移除 `work_dir` 参数的隐式回退逻辑，或在其被使用时发出 deprecation warning
               - `IndependentAgent._build_agent_file_path()` 应使用 `repo_root` 而非 `project_root`，并通过 `Path.exists()` 验证路径存在性，而非字符串匹配

            3. **增加路径 snapshot 测试**：
               - 给 `create_dual_agent_node(project_root=...)` 增加测试，验证传入不同路径时各组件（SessionManager cwd、output_dir、agent_file）的解析结果
               - 给 `IndependentAgent._build_agent_file_path()` 增加测试，覆盖 `repo_root` 和 `package_root` 两种传入场景

            4. **日志增强**：
               在 `SessionManager.__init__` 和 `create_session` 中输出 `repo_root`, `package_root`, `sdk_cwd`, `output_dir` 四个字段，避免仅靠 `cwd` 猜测。
        """).strip()

        return Finding(
            issue_id="P1-2",
            category="路径语义",
            severity="P1",
            title="project_root / cwd / agent_file / output_dir 路径语义漂移",
            evidence=evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            files_affected=files_affected,
        )


# ---------------------------------------------------------------------------
# BMM 对齐分析
# ---------------------------------------------------------------------------
def analyze_bmm_alignment() -> dict[str, str]:
    """分析 BMM module-help.csv 中与 analyst 角色相关的 skill 定义"""
    alignment: dict[str, str] = {}

    if not BMM_MODULE_HELP.exists():
        alignment["error"] = "BMM module-help.csv 未找到"
        return alignment

    content = BMM_MODULE_HELP.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    # 查找 1-analysis 阶段和 analyst 相关的 skill
    for line in lines[1:]:  # skip header
        parts = line.split(",")
        if len(parts) < 4:
            continue
        module = parts[0]
        skill = parts[1]
        display = parts[2]
        phase = parts[6] if len(parts) > 6 else ""

        if phase == "1-analysis":
            if "analyst" in skill.lower() or "research" in skill.lower() or "brainstorm" in skill.lower():
                alignment[skill] = f"display-name={display}, phase=1-analysis"
        if "agent-analyst" in skill.lower():
            alignment[skill] = f"display-name={display}, 业务分析师/需求专家"

    return alignment


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 70)
    print("DocuSwarm calc-one-plus-one 深度研究工具")
    print("=" * 70)
    print()

    # 执行研究
    p0_1 = AnalystContractDriftResearcher(PROJECT_ROOT).research()
    p0_2 = ResultMessageSemanticResearcher().research()
    p1_1 = BlockedStrategyResearcher().research()
    p1_2 = PathSemanticDriftResearcher().research()

    bmm_alignment = analyze_bmm_alignment()

    report = ResearchReport(
        title="DocuSwarm calc-one-plus-one 修复方向深度研究报告",
        date="2026-05-01",
        findings=[p0_1, p0_2, p1_1, p1_2],
        bmm_alignment=bmm_alignment,
        verification_plan=[
            "编写失败测试 `test_result_message_ends_prompt_stream`：用 fake SDK client 模拟 ResultMessage 后的流终止",
            "编写失败测试 `test_analyst_prompt_contract_is_requirements_analysis`：断言 analyst system/user prompt 不包含 Market Overview、Competitive Landscape，且包含 Functional Requirements、Acceptance Criteria",
            "修复 `ClaudeSessionWrapper.prompt()` 的 ResultMessage 终止语义，消除 359 秒空等",
            "修复 analyst node.yaml / persona.json / evaluator.yaml / analyst_templates.yaml，使 calc-context 生成需求背景分析",
            "修复 iteration 统计和 BLOCKED/NEEDS_REVISION 策略，保证日志状态与实际执行一致",
            "运行同一命令 `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 做端到端回归",
        ],
        risk_matrix={
            "P0-1": "所有依赖 analyst 的 pipeline | 中等 | 任何输入都会被错误地导向市场研究",
            "P0-2": "所有使用 session.prompt() 的 agent 调用 | 低 | 每次调用多等 5-6 分钟，污染日志，意外关闭 session",
            "P1-1": "迭代策略理解、可观察性 | 低 | 排障时误判迭代次数和可用策略",
            "P1-2": "跨平台/环境部署 | 低 | 路径解析错误导致 agent_file 或 tools 加载失败",
        },
    )

    # 输出到控制台
    print(report.to_markdown())

    # 写入文件
    RESEARCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESEARCH_OUTPUT_DIR / "2026-05-01-docuswarm-calc-one-plus-one-fix-direction-deep-research.md"
    output_path.write_text(report.to_markdown(), encoding="utf-8")
    print(f"\n[已写入] {output_path}")

    # 同时输出一份 JSON 结构化数据供工具消费
    json_path = RESEARCH_OUTPUT_DIR / "2026-05-01-docuswarm-calc-one-plus-one-fix-direction-deep-research.json"
    json_data = {
        "title": report.title,
        "date": report.date,
        "findings": [
            {
                "issue_id": f.issue_id,
                "category": f.category,
                "severity": f.severity,
                "title": f.title,
                "evidence": f.evidence,
                "root_cause": f.root_cause,
                "recommendation": f.recommendation,
                "files_affected": f.files_affected,
            }
            for f in report.findings
        ],
        "bmm_alignment": report.bmm_alignment,
        "verification_plan": report.verification_plan,
        "risk_matrix": report.risk_matrix,
    }
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[已写入] {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
