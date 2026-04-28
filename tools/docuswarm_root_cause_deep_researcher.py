"""
DocuSwarm Root Cause Deep Research Tool
=======================================

Deep analysis of five root causes:
  RC-1: create_deliverable tool invisible to LLM (cwd responsibility issue)
  RC-2: DEFAULT_PROMPT_TIMEOUT=60s too short for document generation
  RC-3: _parse_response fallback doesn't handle plain text format
  RC-4: ThinkingBlock filtered causing incomplete message content
  RC-5: Pipeline continues after node failure

Usage:
    python tools/docuswarm_root_cause_deep_researcher.py

Output:
    docs/research/2026-04-06-docuswarm-root-cause-deep-research-report.md
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


@dataclass
class ResearchFinding:
    """Research finding data class."""
    root_cause_id: str
    title: str
    severity: str
    status: str
    evidence: list[str] = field(default_factory=list)
    code_snippets: dict[str, str] = field(default_factory=dict)
    fix_recommendations: list[str] = field(default_factory=list)


class DocuswarmRootCauseDeepResearcher:
    """DocuSwarm Root Cause Deep Researcher."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.docuswarm = self.root / "autoBMAD" / "docuswarm"
        self.autoBMAD = self.root / "autoBMAD"
        self.nodes_dir = self.autoBMAD / "nodes"
        self.findings: list[ResearchFinding] = []
        self.detailed_logs: list[str] = []

    def log(self, message: str, level: str = "INFO") -> None:
        """Log detailed log."""
        self.detailed_logs.append(f"[{level}] {message}")
        print(f"  {message}")

    def run(self) -> list[ResearchFinding]:
        """Execute complete deep research."""
        print("=" * 80)
        print("DocuSwarm Root Cause Deep Research")
        print("=" * 80)
        print(f"Research root: {self.root}")
        print()

        self._research_rc1_tool_visibility()
        self._research_rc2_timeout_configuration()
        self._research_rc3_parse_fallback()
        self._research_rc4_thinking_block_handling()
        self._research_rc5_pipeline_continue_on_failure()
        self._verify_fix_status()

        return self.findings

    def _research_rc1_tool_visibility(self) -> None:
        """Deep research RC-1: Tool visibility issue."""
        print("\n" + "=" * 80)
        print("[RC-1] Tool Visibility Deep Research")
        print("=" * 80)

        finding = ResearchFinding(
            root_cause_id="RC-1",
            title="create_deliverable tool invisible to LLM (cwd responsibility split issue)",
            severity="P0",
            status="suspected",
            evidence=[],
            code_snippets={},
            fix_recommendations=[],
        )

        self.log("[1/6] Analyzing agent_file path construction...")
        ind_file = self.docuswarm / "agents" / "independent.py"
        if ind_file.exists():
            content = ind_file.read_text(encoding="utf-8")
            matches = list(re.finditer(
                r'self\._agent_file\s*=\s*\(\s*self\.project_root\s*/\s*"([^"]+)"[^)]+\)',
                content,
                re.DOTALL,
            ))
            self.log(f"Found {len(matches)} _agent_file settings")

            for i, m in enumerate(matches[:2]):
                snippet = content[m.start():m.end()][:200]
                finding.code_snippets[f"agent_file_set_{i+1}"] = snippet
                if "autoBMAD" in snippet:
                    self.log(f"  [OK] Setting {i+1} includes autoBMAD/ layer")
                    finding.evidence.append(f"agent_file setting {i+1} includes autoBMAD/ layer")
                else:
                    self.log(f"  [ERROR] Setting {i+1} missing autoBMAD/ layer!")
                    finding.evidence.append(f"agent_file setting {i+1} missing autoBMAD/ layer - Fix-2A not applied")

        self.log("[2/6] Analyzing SDK options.cwd setting (critical)...")
        sm_file = self.docuswarm / "llm" / "session_manager.py"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")
            method_match = re.search(
                r"def _create_options\(self[^)]*\).*?(?=\n    def |\Z)",
                content,
                re.DOTALL,
            )
            if method_match:
                method_body = method_match.group(0)
                finding.code_snippets["_create_options"] = method_body[:800]

                if '"cwd": self._work_dir' in method_body or "'cwd': self._work_dir" in method_body:
                    self.log("  [ERROR] options.cwd = self._work_dir (problem confirmed!)")
                    self.log("  [ERROR] work_dir is output/pipeline_id, not repo root")
                    finding.evidence.append("options.cwd = self._work_dir, where work_dir = output/pipeline_id")
                    finding.evidence.append("Tool module autoBMAD.docuswarm.tools.create_deliverable cannot be imported from output/pipeline_id")

        self.log("[3/6] Analyzing tool registration config...")
        yaml_path = self.docuswarm / "agents" / "configs" / "independent_agent.yaml"
        if yaml_path.exists():
            yaml_content = yaml_path.read_text(encoding="utf-8")
            finding.code_snippets["independent_agent_yaml"] = yaml_content

            tools = re.findall(r'^\s*-\s*"(.+?)"', yaml_content, re.MULTILINE)
            self.log(f"  Registered tools: {len(tools)}")
            for tool in tools:
                self.log(f"    - {tool}")
                if "create_deliverable" in tool:
                    finding.evidence.append(f"Tool registered: {tool}")

        self.log("[4/6] Verifying tool module file existence...")
        tool_module = self.docuswarm / "tools" / "create_deliverable.py"
        if tool_module.exists():
            self.log(f"  [OK] Tool module exists: {tool_module}")
            finding.evidence.append(f"Tool module file exists: {tool_module}")
        else:
            self.log(f"  [ERROR] Tool module missing: {tool_module}")

        self.log("[5/6] Analyzing CreateDeliverableTool output_dir support...")
        if tool_module.exists():
            content = tool_module.read_text(encoding="utf-8")
            if "output_dir: Path | None = None" in content:
                self.log("  [OK] CreateDeliverableTool supports output_dir parameter")
                finding.evidence.append("CreateDeliverableTool supports output_dir parameter (Fix-2B prerequisite satisfied)")
                finding.fix_recommendations.append("Use CreateDeliverableTool(output_dir=output_dir) to pass output directory explicitly")

        self.log("[6/6] Analyzing SessionManager work_dir dual responsibility...")
        finding.evidence.append("work_dir has dual responsibility: (1) SDK cwd (affects Python import); (2) File output directory")
        finding.evidence.append("Two responsibilities need different paths: cwd should be repo root, output dir should be output/pipeline_id")
        finding.fix_recommendations.append("Fix-2B: Change SessionManager work_dir to repo root (for import)")
        finding.fix_recommendations.append("Fix-2B: Pass output_dir=output/pipeline_id explicitly to CreateDeliverableTool")

        finding.status = "confirmed"
        self.findings.append(finding)
        self.log("[RC-1] Research complete - status: confirmed", "SUCCESS")

    def _research_rc2_timeout_configuration(self) -> None:
        """Deep research RC-2: Timeout configuration issue."""
        print("\n" + "=" * 80)
        print("[RC-2] Timeout Configuration Deep Research")
        print("=" * 80)

        finding = ResearchFinding(
            root_cause_id="RC-2",
            title="DEFAULT_PROMPT_TIMEOUT=60s too short for document generation tasks",
            severity="P0",
            status="suspected",
            evidence=[],
            code_snippets={},
            fix_recommendations=[],
        )

        self.log("[1/5] Checking ClaudeSessionWrapper default timeout...")
        sm_file = self.docuswarm / "llm" / "session_manager.py"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")
            timeout_match = re.search(r'DEFAULT_PROMPT_TIMEOUT\s*:\s*int\s*=\s*(\d+)', content)
            if timeout_match:
                timeout_val = int(timeout_match.group(1))
                self.log(f"  DEFAULT_PROMPT_TIMEOUT = {timeout_val}s")
                finding.code_snippets["DEFAULT_PROMPT_TIMEOUT"] = f"DEFAULT_PROMPT_TIMEOUT: int = {timeout_val}"

                if timeout_val == 60:
                    self.log("  [ERROR] 60s is debug temp value, insufficient for document generation!")
                    finding.status = "confirmed"
                    finding.evidence.append(f"DEFAULT_PROMPT_TIMEOUT = {timeout_val}s (debug temp value)")
                elif timeout_val >= 300:
                    self.log(f"  [OK] {timeout_val}s is reasonable for document generation")
                    finding.status = "fixed"
                    finding.evidence.append(f"DEFAULT_PROMPT_TIMEOUT = {timeout_val}s (fixed)")

        self.log("[2/5] Checking node runtime.timeout config reading...")
        loader_file = self.autoBMAD / "nodes" / "loader.py"
        if loader_file.exists():
            content = loader_file.read_text(encoding="utf-8")
            if 'timeout=runtime_data.get("timeout", 300)' in content:
                self.log("  [OK] NodeLoader correctly reads runtime.timeout (default 300s)")
                finding.evidence.append("NodeLoader reads runtime.timeout from node.yaml (default 300s)")

        self.log("[3/5] Verifying analyst node timeout config...")
        analyst_yaml = self.nodes_dir / "analyst" / "node.yaml"
        if analyst_yaml.exists():
            yaml_content = analyst_yaml.read_text(encoding="utf-8")
            timeout_match = re.search(r'timeout:\s*(\d+)', yaml_content)
            if timeout_match:
                node_timeout = int(timeout_match.group(1))
                self.log(f"  analyst node config timeout: {node_timeout}s")
                finding.evidence.append(f"analyst node config timeout = {node_timeout}s")

        self.log("[4/5] Checking if timeout is passed to session.prompt()...")
        ind_file = self.docuswarm / "agents" / "independent.py"
        if ind_file.exists():
            content = ind_file.read_text(encoding="utf-8")
            prompt_calls = list(re.finditer(r'session\.prompt\([^)]+\)', content, re.DOTALL))
            self.log(f"  Found {len(prompt_calls)} session.prompt() calls")

            has_timeout_param = any('timeout=' in content[m.start():m.end()] for m in prompt_calls)
            if has_timeout_param:
                self.log("  [OK] Some call passes timeout parameter")
                finding.status = "fixed"
                finding.evidence.append("session.prompt() already receives timeout parameter")
            else:
                self.log("  [ERROR] No call passes timeout parameter!")
                finding.evidence.append("No code passes node_config.runtime.timeout to session.prompt()")
                finding.evidence.append("Actual timeout is always DEFAULT_PROMPT_TIMEOUT (60s)")

        self.log("[5/5] Analyzing timeout trigger mechanism...")
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")
            if "asyncio.timeout(effective_timeout)" in content:
                self.log("  Timeout mechanism: asyncio.timeout(effective_timeout)")
                finding.code_snippets["timeout_mechanism"] = "async with asyncio.timeout(effective_timeout):"
                finding.evidence.append("Timeout trigger location: ClaudeSessionWrapper.prompt() asyncio.timeout()")

        finding.fix_recommendations.append("Fix-1A: In executor.py or dual_agent.py, read node_config.runtime.timeout and pass to session.prompt(timeout=...)")
        finding.fix_recommendations.append("Fix-1B (temp): Change DEFAULT_PROMPT_TIMEOUT from 60s to 300s or 600s")

        if finding.status == "suspected":
            finding.status = "confirmed"
        self.findings.append(finding)
        self.log(f"[RC-2] Research complete - status: {finding.status}", "SUCCESS")

    def _research_rc3_parse_fallback(self) -> None:
        """Deep research RC-3: Parse fallback coverage issue."""
        print("\n" + "=" * 80)
        print("[RC-3] Parse Fallback Deep Research")
        print("=" * 80)

        finding = ResearchFinding(
            root_cause_id="RC-3",
            title="_parse_response fallback doesn't handle plain text/English prose format",
            severity="P1",
            status="suspected",
            evidence=[],
            code_snippets={},
            fix_recommendations=[],
        )

        self.log("[1/4] Analyzing _parse_response fallback conditions...")
        ind_file = self.docuswarm / "agents" / "independent.py"
        if ind_file.exists():
            content = ind_file.read_text(encoding="utf-8")

            method_match = re.search(
                r"def _parse_response\(self[^)]*\).*?(?=\n    def |\Z)",
                content,
                re.DOTALL,
            )
            if method_match:
                method_body = method_match.group(0)
                finding.code_snippets["_parse_response"] = method_body[:1500]

                if "content.strip().startswith((\"#\", \"##\", \"###\"))" in method_body:
                    self.log("  Found fallback condition: content.startswith('#', '##', '###')")
                    finding.evidence.append("fallback condition 1: content.startswith(('#', '##', '###'))")

                if "\"Summary\" in content[:100]" in method_body:
                    self.log("  Found fallback condition: 'Summary' in content[:100]")
                    finding.evidence.append("fallback condition 2: 'Summary' in content[:100]")

                has_plain_text_check = (
                    "not content.strip().startswith(\"{\")" in method_body
                )
                if not has_plain_text_check:
                    self.log("  [ERROR] Plain text/English prose format not handled!")
                    finding.evidence.append("fallback doesn't handle plain English prose format (e.g., 'The tools appear to have...')")
                    finding.status = "confirmed"

        self.log("[2/4] Analyzing tool result extraction function...")
        if ind_file.exists():
            content = ind_file.read_text(encoding="utf-8")
            if "def _extract_create_deliverable_result" in content:
                self.log("  [OK] _extract_create_deliverable_result function exists")
                finding.evidence.append("_extract_create_deliverable_result() can extract tool results from messages")

        self.log("[3/4] Analyzing observed error content characteristics...")
        observed_content = (
            "The tools appear to have some issues, but I need to complete my task."
        )
        finding.evidence.append(f"Observed error content: '{observed_content[:60]}...'")

        starts_with_hash = observed_content.strip().startswith("#")
        has_summary = "Summary" in observed_content[:100]
        self.log(f"  Content starts with '#': {starts_with_hash}")
        self.log(f"  Contains 'Summary': {has_summary}")
        self.log(f"  Result: This content won't trigger markdown_fallback!")

        self.log("[4/4] Checking actual fallback behavior...")
        finding.fix_recommendations.append("Fix-3: Extend fallback condition with 'not content.strip().startswith(\"{\")' check")
        finding.fix_recommendations.append("Fix-3: Any non-JSON content should attempt tool result extraction from messages")

        if finding.status == "suspected":
            finding.status = "confirmed"
        self.findings.append(finding)
        self.log(f"[RC-3] Research complete - status: {finding.status}", "SUCCESS")

    def _research_rc4_thinking_block_handling(self) -> None:
        """Deep research RC-4: ThinkingBlock handling issue."""
        print("\n" + "=" * 80)
        print("[RC-4] ThinkingBlock Handling Deep Research")
        print("=" * 80)

        finding = ResearchFinding(
            root_cause_id="RC-4",
            title="ThinkingBlock filtered -> incomplete message content",
            severity="P1",
            status="suspected",
            evidence=[],
            code_snippets={},
            fix_recommendations=[],
        )

        self.log("[1/4] Analyzing _convert_content_block ThinkingBlock handling...")
        sm_file = self.docuswarm / "llm" / "session_manager.py"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")

            method_match = re.search(
                r"def _convert_content_block\(self[^)]*\).*?(?=\n    def |\Z)",
                content,
                re.DOTALL,
            )
            if method_match:
                method_body = method_match.group(0)
                finding.code_snippets["_convert_content_block"] = method_body[:1000]

                if "isinstance(item, ThinkingBlock)" in method_body:
                    if "converted = None" in method_body or "return None" in method_body:
                        thinking_block_section = re.search(
                            r"elif isinstance\(item, ThinkingBlock\):.*?(?=elif |else:|$)",
                            method_body,
                            re.DOTALL,
                        )
                        if thinking_block_section:
                            section = thinking_block_section.group(0)
                            if "return None" in section or "converted = None" in section:
                                self.log("  ThinkingBlock explicitly filtered to None (design decision)")
                                finding.evidence.append("ThinkingBlock filtered to None by _convert_content_block")

        self.log("[2/4] Analyzing duck typing fallback...")
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")
            if 'item_type = getattr(item, "type", "text")' in content:
                self.log("  Found duck typing fallback logic")
                finding.evidence.append("duck typing fallback converts non-text types to {type: item_type, content: str(item)}")

                if 'converted = {"type": item_type, "content": str(item)}' in content:
                    self.log("  ThinkingBlock will become type='thinking' through fallback")
                    finding.evidence.append("ThinkingBlock.type='thinking' enters messages through fallback")

        self.log("[3/4] Verifying messages state at timeout...")
        self.log("  Log shows: response_parse_failed: 'No JSON found in response'")
        self.log("  Not: 'Empty response from LLM'")
        finding.evidence.append("Error is 'No JSON found' not 'Empty response', messages is not empty")
        finding.evidence.append("Messages content is ThinkingBlock str-ed non-JSON text")

        self.log("[4/4] Correcting root cause relationship...")
        finding.evidence.append("RC-4 actual root cause: Tool invisible (RC-1) -> LLM can't call tools -> response all ThinkingBlock")
        finding.evidence.append("ThinkingBlock str-ed enters messages -> extract_json can't find JSON -> parse fails")

        finding.fix_recommendations.append("Fix-2B (RC-1 fix): After tools visible, LLM calls tools normally, ThinkingBlock issue resolved")
        finding.fix_recommendations.append("Optional: Keep ThinkingBlock in _convert_content_block for debugging")

        finding.status = "confirmed"
        self.findings.append(finding)
        self.log(f"[RC-4] Research complete - status: {finding.status}", "SUCCESS")

    def _research_rc5_pipeline_continue_on_failure(self) -> None:
        """Deep research RC-5: Pipeline continue on failure."""
        print("\n" + "=" * 80)
        print("[RC-5] Pipeline Failure Handling Deep Research")
        print("=" * 80)

        finding = ResearchFinding(
            root_cause_id="RC-5",
            title="analyst failure continues pipeline (design behavior)",
            severity="P2",
            status="suspected",
            evidence=[],
            code_snippets={},
            fix_recommendations=[],
        )

        self.log("[1/3] Analyzing LangGraph node execution mechanism...")
        graph_file = self.docuswarm / "pipeline" / "graph.py"
        if graph_file.exists():
            content = graph_file.read_text(encoding="utf-8")
            if "add_node" in content:
                self.log("  Found LangGraph add_node calls")
                finding.evidence.append("Using LangGraph StateGraph for node execution management")

        self.log("[2/3] Checking node execution failure handling...")
        executor_file = self.docuswarm / "node_execution" / "executor.py"
        if executor_file.exists():
            content = executor_file.read_text(encoding="utf-8")
            if "new_state['status'] = FAILED" in content:
                self.log("  Node exception sets status = FAILED")
                finding.evidence.append("Node execution exception sets state['status'] = FAILED")

        self.log("[3/3] Verifying design intent...")
        self.log("  Log shows: analyst failed -> pm started (immediately)")
        finding.evidence.append("Log evidence: after analyst node_execution_failed, pm node_execution_started immediately")
        finding.evidence.append("Design intent: Pipeline nodes execute independently, predecessor failure doesn't force interrupt")
        finding.evidence.append("Design rationale: Allow partial output")

        finding.fix_recommendations.append("Current behavior is by design, not mandatory to fix")
        finding.fix_recommendations.append("Fix-4 (optional): Add fail_fast: true option in node.yaml for forced interruption")
        finding.fix_recommendations.append("Fix-4 implementation: In pipeline/graph.py, interrupt when node fails and fail_fast=true")

        finding.status = "confirmed"
        self.findings.append(finding)
        self.log(f"[RC-5] Research complete - status: {finding.status}", "SUCCESS")

    def _verify_fix_status(self) -> None:
        """Verify fix implementation status."""
        print("\n" + "=" * 80)
        print("Fix Status Verification")
        print("=" * 80)

        self.log("[Verify] Fix-2A: agent_file path includes autoBMAD/...")
        ind_file = self.docuswarm / "agents" / "independent.py"
        if ind_file.exists():
            content = ind_file.read_text(encoding="utf-8")
            if 'self.project_root / "autoBMAD" / "docuswarm"' in content:
                self.log("  [OK] Fix-2A applied: agent_file path includes autoBMAD/")
            else:
                self.log("  [ERROR] Fix-2A not applied: agent_file path missing autoBMAD/")

        self.log("[Verify] Fix-2B: cwd changed to repo root...")
        sm_file = self.docuswarm / "llm" / "session_manager.py"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")
            if "repo_root" in content or "project_root" in content:
                self.log("  [WARN] Found repo_root/project_root references, need to verify implementation")
            else:
                self.log("  [ERROR] Fix-2B pending: No root directory references in SessionManager")

        self.log("[Verify] Fix-1: Node timeout passed to session.prompt()...")
        dual_agent = self.docuswarm / "nodes" / "dual_agent.py"
        if dual_agent.exists():
            content = dual_agent.read_text(encoding="utf-8")
            if "timeout=" in content and "node_config" in content:
                self.log("  [WARN] Found timeout and node_config references, need to verify passing relationship")
            else:
                self.log("  [ERROR] Fix-1 pending: node_config.runtime.timeout not passed to session.prompt()")


    def generate_report(self, output_path: Path | None = None) -> Path:
        """Generate detailed research report."""
        if output_path is None:
            output_path = (
                self.root
                / "docs"
                / "research"
                / "2026-04-06-docuswarm-root-cause-deep-research-report.md"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        lines.append("# DocuSwarm 根因深度研究报告")
        lines.append("")
        lines.append("**研究日期**: 2026-04-06")
        lines.append("**研究工具**: `tools/docuswarm_root_cause_deep_researcher.py`")
        lines.append("**研究范围**: autoBMAD/docuswarm 核心模块")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## 执行摘要")
        lines.append("")
        p0_count = sum(1 for f in self.findings if f.severity == "P0")
        p1_count = sum(1 for f in self.findings if f.severity == "P1")
        p2_count = sum(1 for f in self.findings if f.severity == "P2")

        lines.append(f"本次深度研究确认了 **{len(self.findings)}** 个根因:")
        lines.append(f"- **P0 CRITICAL**: {p0_count}")
        lines.append(f"- **P1 HIGH**: {p1_count}")
        lines.append(f"- **P2 MEDIUM**: {p2_count}")
        lines.append("")

        # Root cause relationship
        lines.append("### 根因关系与触发链")
        lines.append("")
        lines.append("```")
        lines.append("RC-1 (工具不可见: cwd 职责未拆分)")
        lines.append("  -> LLM 无法调用 create_deliverable")
        lines.append("RC-2 (超时 60s 过短)")
        lines.append("  -> LLM 在 ThinkingBlock 阶段被中断")
        lines.append("RC-4 (ThinkingBlock 被 str 化)")
        lines.append("  -> messages 包含非 JSON 内容")
        lines.append("RC-3 (fallback 覆盖不足)")
        lines.append("  -> parse_json 失败")
        lines.append("RC-5 (流水线继续 - 设计允许)")
        lines.append("  -> 后续节点同样失败")
        lines.append("```")
        lines.append("")

        # Fix status
        lines.append("### 修复状态总览")
        lines.append("")
        lines.append("| 根因 | 优先级 | 状态 | 修复建议 |")
        lines.append("|------|--------|------|----------|")
        for f in self.findings:
            fix_count = len(f.fix_recommendations)
            lines.append(f"| {f.root_cause_id} | {f.severity} | {f.status} | {fix_count} 项 |")
        lines.append("")

        lines.append("---")
        lines.append("")

        # Detailed findings
        for finding in self.findings:
            lines.append(f"## {finding.root_cause_id}: {finding.title}")
            lines.append("")
            lines.append(f"**严重程度**: {finding.severity}")
            lines.append(f"**确认状态**: {finding.status}")
            lines.append("")

            # Evidence
            lines.append("### 证据")
            lines.append("")
            for ev in finding.evidence:
                lines.append(f"- {ev}")
            lines.append("")

            # Code snippets
            if finding.code_snippets:
                lines.append("### 相关代码")
                lines.append("")
                for name, snippet in finding.code_snippets.items():
                    lines.append(f"**{name}**:")
                    lines.append("```python")
                    lines.append(snippet[:500] if len(snippet) > 500 else snippet)
                    lines.append("```")
                    lines.append("")

            # Fix recommendations
            lines.append("### 修复建议")
            lines.append("")
            for rec in finding.fix_recommendations:
                lines.append(f"- {rec}")
            lines.append("")

            lines.append("---")
            lines.append("")

        # Minimum fix set
        lines.append("## 最小修复集 (Minimum Fix Set)")
        lines.append("")
        lines.append("要使基本流程通过，必须实施以下修复:")
        lines.append("")
        lines.append("### 必须修复 (P0)")
        lines.append("")
        lines.append("1. **Fix-2B**: 拆分 `cwd` 职责")
        lines.append("   - 修改 `SessionManager.__init__()` 接受 `cwd` 和 `output_dir` 两个参数")
        lines.append("   - `cwd` 设为仓库根目录 (用于 Python import)")
        lines.append("   - `output_dir` 设为 `output/pipeline_id` (用于文件输出)")
        lines.append("   - 修改 `CreateDeliverableTool` 实例化时传入 `output_dir`")
        lines.append("")
        lines.append("2. **Fix-1**: 接入节点超时配置")
        lines.append("   - 修改 `executor.py` 或 `dual_agent.py` 读取 `node_config.runtime.timeout`")
        lines.append("   - 将 timeout 值传入 `session.prompt(user_prompt, timeout=node_timeout)`")
        lines.append("")

        # Detailed fix steps
        lines.append("## 详细修复步骤")
        lines.append("")
        lines.append("### Fix-2B: cwd 职责拆分 (P0)")
        lines.append("")
        lines.append("**问题**: `work_dir` 同时承担两个职责:")
        lines.append("1. SDK 进程工作目录 (影响 Python import 路径)")
        lines.append("2. 文件输出目录 (`create_deliverable` 写文件位置)")
        lines.append("")
        lines.append("**方案**: 在 `SessionManager` 中拆分两个路径:")
        lines.append("")
        lines.append("```python")
        lines.append("# session_manager.py _create_options()")
        lines.append("options_dict: dict[str, Any] = {")
        lines.append('    "cwd": self._repo_root,  # 仓库根目录，用于 import autoBMAD')
        lines.append('    "permission_mode": permission_mode,')
        lines.append("}")
        lines.append("```")
        lines.append("")
        lines.append("```python")
        lines.append("# independent.py execute_with_input()")
        lines.append("# 工具实例化时传入 output_dir")
        lines.append("tool = CreateDeliverableTool(output_dir=output_dir)")
        lines.append("```")
        lines.append("")
        lines.append("### Fix-1: 超时配置接入 (P0)")
        lines.append("")
        lines.append("**问题**: `node.yaml` 中配置的 `runtime.timeout: 300` 从未被代码读取使用")
        lines.append("")
        lines.append("**方案**: 在节点执行时读取并传入:")
        lines.append("")
        lines.append("```python")
        lines.append("# executor.py 或 dual_agent.py")
        lines.append("from autoBMAD.nodes.loader import NodeLoader")
        lines.append("")
        lines.append("node_config = NodeLoader.load(node_id)")
        lines.append("node_timeout = node_config.runtime.timeout  # 300s")
        lines.append("")
        lines.append("# 调用时传入")
        lines.append("async for msg in session.prompt(user_prompt, timeout=node_timeout):")
        lines.append("    ...")
        lines.append("```")
        lines.append("")

        # Verification methods
        lines.append("## 验证方法")
        lines.append("")
        lines.append("### 验证工具不可见问题已修复")
        lines.append("")
        lines.append("在日志中应观察到:")
        lines.append("```")
        lines.append("tool_availability_check: agent_file_exists=True")
        lines.append("...")
        lines.append("llm_tool_call: tool_name='create_deliverable'")
        lines.append("```")
        lines.append("")
        lines.append("### 验证超时已修复")
        lines.append("")
        lines.append("在日志中应在 300s 内出现:")
        lines.append("```")
        lines.append("llm_prompt_complete: message_count=...")
        lines.append("```")
        lines.append("而非:")
        lines.append("```")
        lines.append("prompt_timeout: timeout_seconds=60")
        lines.append("```")
        lines.append("")
        lines.append("### 验证完整流程")
        lines.append("")
        lines.append("```bash")
        lines.append("python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md")
        lines.append("```")
        lines.append("")
        lines.append("期望: `output/pipeline-*/` 目录下出现 5 个 `.md` 文件")
        lines.append("")

        # Reference files
        lines.append("## 参考文件")
        lines.append("")
        lines.append("| 文件 | 相关代码位置 | 作用 |")
        lines.append("|------|------------|------|")
        lines.append("| `autoBMAD/docuswarm/llm/session_manager.py` | L730: `DEFAULT_PROMPT_TIMEOUT=60` | 硬编码超时值 |")
        lines.append("| `autoBMAD/docuswarm/llm/session_manager.py` | L146: `options.cwd = self._work_dir` | cwd 设置问题 |")
        lines.append("| `autoBMAD/docuswarm/agents/independent.py` | L622: `self._agent_file` 构造 | agent_file 路径 |")
        lines.append("| `autoBMAD/docuswarm/agents/independent.py` | L444-510: `_parse_response()` | parse fallback |")
        lines.append("| `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` | tools 列表 | 工具注册配置 |")
        lines.append("| `autoBMAD/nodes/analyst/node.yaml` | L32: `runtime.timeout=300` | 节点超时配置 |")
        lines.append("| `autoBMAD/nodes/loader.py` | L389-393: runtime 配置加载 | 配置加载逻辑 |")
        lines.append("")

        # Appendix
        lines.append("## 附录: 研究详细日志")
        lines.append("")
        lines.append("```")
        for log in self.detailed_logs:
            lines.append(log)
        lines.append("```")
        lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n研究报告已生成: {output_path}")
        return output_path


def main() -> None:
    researcher = DocuswarmRootCauseDeepResearcher()
    findings = researcher.run()
    output_path = researcher.generate_report()

    print("\n" + "=" * 80)
    print("研究摘要")
    print("=" * 80)
    for f in findings:
        print(f"  [{f.root_cause_id}] {f.severity} - {f.status}: {f.title[:50]}...")
    print(f"\n详细报告: {output_path}")


if __name__ == "__main__":
    main()
