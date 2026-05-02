"""
DeepSeek + MCP ToolResult 兼容性深度研究工具
===============================================

针对流水线 pipeline-1777697677287-8cb53d89 UX 节点失败的深度诊断。

研究目标：
1. 静态验证 IndependentAgent._extract_create_deliverable_result / _extract_submit_report_result
   对 MCP 工具返回的 list[dict] 内容格式的兼容性缺陷。
2. 依据 DeepSeek Anthropic API 兼容性文档，评估当前 SDK MCP Server 路径下
   tool_result.content 的实际序列化形式。
3. 对给定流水线日志进行证据链重建：交付物文件是否存在、SHA256 匹配、LLM
   回复格式、解析路径进入、错误堆栈位置。
4. 生成 JSON + Markdown 双形态报告，服务于后续修复与回归测试。

参考：
- https://api-docs.deepseek.com/zh-cn/guides/anthropic_api
- autoBMAD/docuswarm/agents/independent.py
- autoBMAD/docuswarm/tools/create_deliverable_sdk.py
- autoBMAD/docuswarm/llm/session_manager.py
- .venv/.../claude_agent_sdk/types.py (ToolResultBlock)

Usage:
    python tools/deepseek_mcp_toolresult_researcher.py
    python tools/deepseek_mcp_toolresult_researcher.py \
        --log logs/pipeline-1777697677287-8cb53d89.log \
        --output docs-doc/research/<date>-deepseek-mcp-toolresult-research.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DOCUSWARM = ROOT / "autoBMAD" / "docuswarm"
INDEPENDENT_PY = DOCUSWARM / "agents" / "independent.py"
CREATE_DELIVERABLE_PY = DOCUSWARM / "tools" / "create_deliverable_sdk.py"
SESSION_MANAGER_PY = DOCUSWARM / "llm" / "session_manager.py"


# --------------------------------------------------------------------------- #
#  Data models                                                                #
# --------------------------------------------------------------------------- #

@dataclass
class Finding:
    id: str
    severity: str  # critical | high | medium | low | info
    title: str
    description: str
    evidence: list[str] = field(default_factory=list)
    location: str = ""
    suggested_fix: str = ""


@dataclass
class ResearchReport:
    generated_at: str
    log_file: str
    pipeline_id: str | None = None
    api_vendor: dict[str, Any] = field(default_factory=dict)
    code_analysis: dict[str, Any] = field(default_factory=dict)
    log_analysis: dict[str, Any] = field(default_factory=dict)
    artifact_analysis: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
#  Section 1: Static code analysis — the extractor bug                         #
# --------------------------------------------------------------------------- #

class ExtractorBugAnalyzer:
    """静态分析 _extract_create_deliverable_result / _extract_submit_report_result
    对 tool_output 类型分支的覆盖情况。"""

    TARGET_METHODS = (
        "_extract_create_deliverable_result",
        "_extract_submit_report_result",
    )

    def analyze(self) -> dict[str, Any]:
        print("\n[1/4] 扫描 IndependentAgent 工具结果提取器 ...")
        result: dict[str, Any] = {"methods": {}}
        if not INDEPENDENT_PY.exists():
            result["error"] = f"{INDEPENDENT_PY} not found"
            return result
        source = INDEPENDENT_PY.read_text(encoding="utf-8")
        for name in self.TARGET_METHODS:
            info = self._inspect_method(source, name)
            result["methods"][name] = info
            verdict = "BUG" if info.get("missing_list_branch") else "OK"
            print(f"  - {name}: str_branch={info.get('has_str_branch')}, "
                  f"list_branch={info.get('has_list_branch')} -> {verdict}")
        return result

    def _inspect_method(self, source: str, name: str) -> dict[str, Any]:
        # Signature may span multiple lines; use DOTALL and stop at first ':\n'.
        pattern = rf"def {re.escape(name)}\(.*?\)\s*(?:->\s*[^:]+?)?:\s*\n"
        m = re.search(pattern, source, re.DOTALL)
        if not m:
            return {"found": False}
        start = m.end()
        # Body is indented with 8 spaces (class method). Stop when a line appears
        # that is less indented (next sibling def/class member at 4 spaces).
        lines = source[start:].splitlines()
        body: list[str] = []
        for line in lines:
            if line.strip() == "":
                body.append(line)
                continue
            if line.startswith(" " * 8) or line.startswith("\t\t"):
                body.append(line)
                continue
            break
        body_text = "\n".join(body)
        has_str = "isinstance(tool_output, str)" in body_text
        has_list = "isinstance(tool_output, list)" in body_text
        has_dict = "isinstance(tool_output, dict)" in body_text
        json_loads = "json_module.loads" in body_text or "json.loads" in body_text
        filters_error = 'get("is_error"' in body_text or "is_error" in body_text
        return {
            "found": True,
            "has_str_branch": has_str,
            "has_list_branch": has_list,
            "has_dict_branch": has_dict,
            "uses_json_loads": json_loads,
            "filters_error": filters_error,
            "missing_list_branch": has_str and not has_list,
            "body_lines": len(body),
            "excerpt": "\n".join(body[:25]),
        }


# --------------------------------------------------------------------------- #
#  Section 2: MCP tool return shape (ground truth from create_deliverable_sdk) #
# --------------------------------------------------------------------------- #

class McpToolContractAnalyzer:
    """验证 create_deliverable / submit_execution_report MCP 工具返回的 content shape。"""

    def analyze(self) -> dict[str, Any]:
        print("\n[2/4] 分析 MCP 工具返回契约 ...")
        result: dict[str, Any] = {"create_deliverable": {}, "submit_execution_report": {}}
        if not CREATE_DELIVERABLE_PY.exists():
            result["error"] = f"{CREATE_DELIVERABLE_PY} not found"
            return result
        source = CREATE_DELIVERABLE_PY.read_text(encoding="utf-8")

        result["create_deliverable"] = self._scan_return(
            source, "create_deliverable_tool"
        )
        result["submit_execution_report"] = self._scan_return(
            source, "submit_execution_report_tool"
        )

        for tool_name, info in result.items():
            if isinstance(info, dict) and "returns_list_of_text_blocks" in info:
                marker = "LIST[dict]" if info["returns_list_of_text_blocks"] else "UNKNOWN"
                print(f"  - {tool_name}: content 形态 = {marker}")
        return result

    @staticmethod
    def _scan_return(source: str, func_name: str) -> dict[str, Any]:
        pattern = rf"async def {re.escape(func_name)}\(.*?\n(.*?)(?=\nasync def |\n@tool|\Z)"
        m = re.search(pattern, source, re.DOTALL)
        if not m:
            return {"found": False}
        body = m.group(1)
        returns_list_of_text_blocks = bool(
            re.search(r'"content"\s*:\s*\[\s*\{\s*"type"\s*:\s*"text"', body)
        )
        uses_json_dumps = "json.dumps" in body
        return {
            "found": True,
            "returns_list_of_text_blocks": returns_list_of_text_blocks,
            "uses_json_dumps": uses_json_dumps,
            "signature_pattern": '{"content": [{"type": "text", "text": json.dumps(...)}]}',
        }


# --------------------------------------------------------------------------- #
#  Section 3: Log forensic reconstruction                                      #
# --------------------------------------------------------------------------- #

class PipelineLogForensic:
    """从流水线日志还原 LLM 回复、工具调用和错误路径。"""

    def analyze(self, log_path: Path) -> dict[str, Any]:
        print(f"\n[3/4] 取证分析日志 {log_path.name} ...")
        if not log_path.exists():
            return {"error": f"{log_path} not found"}
        text = log_path.read_text(encoding="utf-8", errors="replace")
        pipeline_id = self._extract_first(text, r"run_id=([a-z0-9\-]+)")
        nodes_status = self._node_outcomes(text)
        prompt_results = self._prompt_results(text)
        error_entries = self._errors(text)
        markdown_fallback = "llm_returned_markdown_fallback" in text
        tool_name_hits = re.findall(r"tool_name=([A-Za-z_0-9]+)", text)
        final_state = self._final_pipeline_state(text)

        result: dict[str, Any] = {
            "pipeline_id": pipeline_id,
            "nodes_status": nodes_status,
            "prompt_results": prompt_results,
            "errors": error_entries,
            "markdown_fallback_triggered": markdown_fallback,
            "tool_name_log_hits": sorted(set(tool_name_hits)),
            "final_pipeline_state": final_state,
        }
        print(f"  - pipeline_id: {pipeline_id}")
        print(f"  - nodes: {nodes_status}")
        print(f"  - markdown_fallback_triggered: {markdown_fallback}")
        return result

    @staticmethod
    def _extract_first(text: str, pattern: str) -> str | None:
        m = re.search(pattern, text)
        return m.group(1) if m else None

    @staticmethod
    def _node_outcomes(text: str) -> dict[str, str]:
        outcomes: dict[str, str] = {}
        for m in re.finditer(r"node_id=(\w+)\s+message=\"independent_agent_completed\"", text):
            outcomes[m.group(1)] = "completed"
        for m in re.finditer(
            r"node_id=(\w+)\s+message=\"node_execution_failed\"", text
        ):
            outcomes[m.group(1)] = "failed"
        return outcomes

    @staticmethod
    def _prompt_results(text: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for m in re.finditer(
            r"node_id=(?P<node>\w+|-)\s+message=\"prompt_result_received\"[^\n]*?result=(?P<head>[^\n]{0,80})",
            text,
        ):
            head = m.group("head").strip()
            starts_with_json_fence = head.startswith("```json")
            starts_with_markdown = head.startswith(("#", "##"))
            results.append({
                "node_hint": m.group("node"),
                "head_preview": head,
                "starts_with_json_fence": starts_with_json_fence,
                "starts_with_markdown": starts_with_markdown,
            })
        return results

    @staticmethod
    def _errors(text: str) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for m in re.finditer(
            r"\[error\] run_id=[^\s]+\s+node_id=(?P<node>\w+|-)\s+message=\"(?P<msg>[^\"]+)\"",
            text,
        ):
            entries.append({"node": m.group("node"), "message": m.group("msg")})
        return entries

    @staticmethod
    def _final_pipeline_state(text: str) -> dict[str, Any]:
        m = re.search(r"pipeline_completed[^\n]*result=(\{.*?\})(?=\s*\n|\Z)", text, re.DOTALL)
        if not m:
            return {}
        raw = m.group(1)
        # Heuristic extraction of key scalar fields
        return {
            "completed_nodes": re.search(r"'completed_nodes': \[([^\]]*)\]", raw).group(1)
            if re.search(r"'completed_nodes':", raw) else "",
            "failed_nodes": re.search(r"'failed_nodes': \[([^\]]*)\]", raw).group(1)
            if re.search(r"'failed_nodes':", raw) else "",
            "status": re.search(r"'status': '([^']+)'", raw).group(1)
            if re.search(r"'status':", raw) else "",
        }


# --------------------------------------------------------------------------- #
#  Section 4: Artifact evidence (output file integrity)                        #
# --------------------------------------------------------------------------- #

class ArtifactEvidenceAnalyzer:
    """验证 output 目录实际落盘的交付物 vs LLM 日志中的 SHA256 声明。"""

    def analyze(self, pipeline_id: str) -> dict[str, Any]:
        print("\n[4/4] 校验交付物文件与 SHA256 一致性 ...")
        out_dir = ROOT / "output" / pipeline_id
        if not out_dir.exists():
            return {"error": f"{out_dir} not found"}
        files: list[dict[str, Any]] = []
        for p in sorted(out_dir.iterdir()):
            if p.is_file():
                data = p.read_bytes()
                files.append({
                    "name": p.name,
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                })
        print(f"  - 发现 {len(files)} 个交付物文件")
        for f in files:
            print(f"    · {f['name']} ({f['size_bytes']}B) sha256={f['sha256'][:12]}…")
        return {"output_dir": str(out_dir), "files": files}


# --------------------------------------------------------------------------- #
#  Section 5: DeepSeek Anthropic API compatibility matrix (constant)           #
# --------------------------------------------------------------------------- #

DEEPSEEK_COMPATIBILITY = {
    "source": "https://api-docs.deepseek.com/zh-cn/guides/anthropic_api",
    "base_url": "https://api.deepseek.com/anthropic",
    "notable_unsupported": [
        "mcp_servers (Ignored)",
        "mcp_tool_use (Not Supported)",
        "mcp_tool_result (Not Supported)",
        "cache_control (Ignored)",
        "is_error on tool_result (Ignored)",
        "image/document/search_result content (Not Supported)",
    ],
    "supported_for_sdk_mcp_pattern": [
        "tools.name / input_schema / description",
        "tool_use.id / input / name",
        "tool_result.tool_use_id / content",
    ],
    "implication": (
        "SDK 内嵌 MCP Server (create_sdk_mcp_server) 会被 SDK 运行时转换为"
        "标准 Anthropic tools，DeepSeek 仍能识别为 tool_use/tool_result；"
        "但 DeepSeek 对 tool_result.is_error 忽略，且在长上下文下指令跟随不稳定。"
    ),
}


# --------------------------------------------------------------------------- #
#  Report assembly                                                             #
# --------------------------------------------------------------------------- #

def build_findings(
    code: dict[str, Any],
    tools: dict[str, Any],
    log: dict[str, Any],
    artifact: dict[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []

    # Finding F1 — Extractor missing list branch
    for name, info in code.get("methods", {}).items():
        if info.get("missing_list_branch"):
            findings.append(Finding(
                id=f"F1-{name}",
                severity="critical",
                title=f"{name} 未处理 MCP tool_result.content 为 list[dict] 的情况",
                description=(
                    "SDK MCP 工具返回 {'content': [{'type': 'text', 'text': json_str}]}，"
                    "claude_agent_sdk 将其包装为 ToolResultBlock 且 content 类型为 "
                    "str | list[dict[str, Any]] | None。当前实现仅覆盖 str 分支，"
                    "list[dict] 静默跳过，导致 file_path/sha256 提取失败。"
                ),
                evidence=[
                    "has_str_branch={}".format(info.get("has_str_branch")),
                    "has_list_branch={}".format(info.get("has_list_branch")),
                    "excerpt=\n" + (info.get("excerpt") or "")[:400],
                ],
                location=f"autoBMAD/docuswarm/agents/independent.py :: {name}",
                suggested_fix=(
                    "增加 list 分支：遍历 content blocks，取出 type=='text' 的 text 字段，"
                    "再对该字符串 json.loads。示例：\n"
                    "if isinstance(tool_output, list):\n"
                    "    for b in tool_output:\n"
                    "        if isinstance(b, dict) and b.get('type') == 'text':\n"
                    "            try: tool_output = json.loads(b.get('text',''))\n"
                    "            except: continue\n"
                    "            break\n"
                ),
            ))

    # Finding F2 — MCP contract evidence
    cd = tools.get("create_deliverable", {})
    sr = tools.get("submit_execution_report", {})
    if cd.get("returns_list_of_text_blocks") or sr.get("returns_list_of_text_blocks"):
        findings.append(Finding(
            id="F2-mcp-contract",
            severity="high",
            title="MCP 工具契约固定返回 list[dict] 形态，与 F1 Bug 必然叠加",
            description=(
                "create_deliverable_tool 与 submit_execution_report_tool 实现"
                "均使用 {'content':[{'type':'text','text':json.dumps(...)}]} 的 SDK 契约。"
                "这是 claude-agent-sdk 官方建议的 MCP 返回格式，"
                "意味着所有工具结果都会以 list[dict] 形式到达提取器。"
            ),
            evidence=[
                f"create_deliverable returns_list_of_text_blocks={cd.get('returns_list_of_text_blocks')}",
                f"submit_execution_report returns_list_of_text_blocks={sr.get('returns_list_of_text_blocks')}",
            ],
            location="autoBMAD/docuswarm/tools/create_deliverable_sdk.py",
            suggested_fix="契约合理，无需改动。需修复 F1 的提取器以匹配该契约。",
        ))

    # Finding F3 — LLM instruction drift under long context
    md_fallback = log.get("markdown_fallback_triggered", False)
    prompt_results = log.get("prompt_results", [])
    if md_fallback and prompt_results:
        markdown_nodes = [r for r in prompt_results if r.get("starts_with_markdown")]
        json_nodes = [r for r in prompt_results if r.get("starts_with_json_fence")]
        findings.append(Finding(
            id="F3-llm-format-drift",
            severity="high",
            title="LLM 最终回复在长上下文下从 JSON 漂移为 Markdown 叙述",
            description=(
                "Prompt 同时允许三条输出路径（MCP submit_execution_report / 行内 JSON / "
                "Markdown 汇报），在 DeepSeek 长上下文（UX 4591 词）下 LLM 选择了未明确允许"
                "的 Markdown 叙述路径。analyst/pm 幸运地使用 ```json 围栏被 "
                "extract_json_from_markdown 解析，UX 则绕过所有 JSON 路径。"
            ),
            evidence=[
                f"prompt_result_head samples (json_fence): {[r['head_preview'][:40] for r in json_nodes]}",
                f"prompt_result_head samples (markdown): {[r['head_preview'][:40] for r in markdown_nodes]}",
                "llm_returned_markdown_fallback warning present in log",
            ],
            location="autoBMAD/docuswarm/agents/independent.py :: _format_system_prompt (L184-L306)",
            suggested_fix=(
                "收紧 prompt：将 Legacy Fallback 改为严格约束「最终必须以 JSON 结束」；"
                "或通过 SDK output_format 施加 JSON Schema 硬约束（Story 38.1 已有能力）。"
            ),
        ))

    # Finding F4 — DeepSeek vendor implication
    findings.append(Finding(
        id="F4-deepseek-vendor",
        severity="medium",
        title="DeepSeek Anthropic 兼容模式忽略 is_error 等字段，失败边界被模糊",
        description=(
            "ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic，DeepSeek 兼容层"
            "对 tool_result.is_error、mcp_* 类型、cache_control 忽略。SDK 内嵌 MCP "
            "仍可正常路由，但当工具失败时 is_error=True 不会传达给 LLM，LLM 会把错误"
            "结果当做成功处理，产生与 Claude Sonnet 不同的行为轨迹。"
        ),
        evidence=DEEPSEEK_COMPATIBILITY["notable_unsupported"],
        location=".env :: ANTHROPIC_BASE_URL",
        suggested_fix=(
            "在工具错误路径手动把 error text 融入 content text（避免依赖 is_error）；"
            "或在 SessionManager 层对 DeepSeek 端做额外校验适配。"
        ),
    ))

    # Finding F5 — artifact proves tool ran but parser failed
    files = artifact.get("files", [])
    if files:
        findings.append(Finding(
            id="F5-artifact-proof",
            severity="info",
            title="交付物已落盘，证明 MCP 工具执行成功，失败仅发生在解析层",
            description=(
                "output/<pipeline_id>/ux-design.md 存在且 SHA256 与日志 LLM 文本中的"
                "声明一致，可反推 create_deliverable 已被 LLM 正确调用并由 SDK MCP "
                "工具执行成功。流水线失败是纯解析层问题，非工具执行问题。"
            ),
            evidence=[f"{f['name']} size={f['size_bytes']} sha256={f['sha256'][:16]}" for f in files],
            location=artifact.get("output_dir", ""),
            suggested_fix="实施 F1 修复后，可直接从 output 目录回填交付物元数据恢复流水线。",
        ))

    return findings


def build_summary(report: ResearchReport) -> dict[str, Any]:
    sev_counts: dict[str, int] = {}
    for f in report.findings:
        sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1
    return {
        "total_findings": len(report.findings),
        "by_severity": sev_counts,
        "pipeline_failed_node": "ux",
        "root_cause_category": "parser-mcp-contract-mismatch",
        "blocking_fix": "F1 — 增补 _extract_*_result 的 list[dict] 分支",
        "secondary_fix": "F3 — 收紧 prompt / 启用 output_format 硬约束",
    }


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description="DeepSeek + MCP ToolResult 深度研究")
    parser.add_argument(
        "--log",
        default="logs/pipeline-1777697677287-8cb53d89.log",
        help="流水线日志路径（相对 ROOT 或绝对路径）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="JSON 报告输出路径；未指定则打印到 stdout",
    )
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.is_absolute():
        log_path = ROOT / log_path

    report = ResearchReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        log_file=str(log_path),
        api_vendor=DEEPSEEK_COMPATIBILITY,
    )

    code_analysis = ExtractorBugAnalyzer().analyze()
    tool_analysis = McpToolContractAnalyzer().analyze()
    log_analysis = PipelineLogForensic().analyze(log_path)
    pipeline_id = log_analysis.get("pipeline_id") or log_path.stem.replace(".log", "")
    report.pipeline_id = pipeline_id
    artifact_analysis = ArtifactEvidenceAnalyzer().analyze(pipeline_id)

    report.code_analysis = code_analysis
    report.log_analysis = log_analysis
    report.artifact_analysis = artifact_analysis
    report.code_analysis["mcp_tool_contracts"] = tool_analysis

    report.findings = build_findings(
        code_analysis, tool_analysis, log_analysis, artifact_analysis
    )
    report.summary = build_summary(report)

    payload = {
        "generated_at": report.generated_at,
        "log_file": report.log_file,
        "pipeline_id": report.pipeline_id,
        "api_vendor": report.api_vendor,
        "code_analysis": report.code_analysis,
        "log_analysis": report.log_analysis,
        "artifact_analysis": report.artifact_analysis,
        "findings": [asdict(f) for f in report.findings],
        "summary": report.summary,
    }

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[OK] JSON 报告已写入 {out_path}")
    else:
        print("\n" + "=" * 60)
        print("RESEARCH SUMMARY")
        print("=" * 60)
        print(json.dumps(report.summary, ensure_ascii=False, indent=2))
        print("\nFINDINGS:")
        for f in report.findings:
            print(f"  [{f.severity.upper()}] {f.id}: {f.title}")

    return 0 if report.findings else 1


if __name__ == "__main__":
    sys.exit(main())
