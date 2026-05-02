"""
DeepSeek + MCP ToolResult 修复方案可行性研究工具
===================================================

输入：研究报告 docs-doc/research/2026-05-02-deepseek-mcp-toolresult-deep-research.md §7 全部修复方案。

目标：
1. 逐项扫描 §7.1 ~ §7.5 落地所需的前置条件就绪度（readiness）：
   - §7.1 提取器 list 分支补丁
   - §7.2 回归测试骨架
   - §7.3 Prompt 收紧 / output_format 启用
   - §7.4 File/SHA256 正则兜底
   - §7.5 DeepSeek 兼容性适配（is_error 嵌入 text、context 裁剪、observability）
2. 为每一项产出 TDD 测试用例清单（文件名、测试类/函数名、AAA 模板提示）。
3. 评估风险级别（low/medium/high）与改造成本。
4. 产出 JSON 报告作为 TDD 方案文档的数据背书。

Usage:
    python tools/deepseek_mcp_toolresult_solution_researcher.py \
        --output docs-doc/solution/2026-05-02-deepseek-mcp-toolresult-solution-readiness.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DOCUSWARM = ROOT / "autoBMAD" / "docuswarm"
INDEPENDENT_PY = DOCUSWARM / "agents" / "independent.py"
EVALUATOR_PY = DOCUSWARM / "agents" / "evaluator.py"
SESSION_MANAGER_PY = DOCUSWARM / "llm" / "session_manager.py"
CREATE_DELIVERABLE_PY = DOCUSWARM / "tools" / "create_deliverable_sdk.py"
CONTRACT_BUILDER_PY = DOCUSWARM / "prompts" / "contract_builder.py"


# --------------------------------------------------------------------------- #
#  Data models                                                                #
# --------------------------------------------------------------------------- #

@dataclass
class TestCase:
    file: str
    class_name: str
    function: str
    arrange: str
    act: str
    assert_: str
    target_symbol: str


@dataclass
class FixReadiness:
    fix_id: str
    title: str
    scope: str
    prereq_status: str  # ready | partial | blocked
    prereq_evidence: list[str] = field(default_factory=list)
    risk: str = "low"
    effort_hours: float = 1.0
    test_cases: list[TestCase] = field(default_factory=list)
    blocking_unknowns: list[str] = field(default_factory=list)


@dataclass
class SolutionReport:
    generated_at: str
    source_report: str
    readiness: list[FixReadiness] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
#  Probes                                                                     #
# --------------------------------------------------------------------------- #

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def probe_extractor_branches() -> dict[str, Any]:
    src = _read(INDEPENDENT_PY)
    result: dict[str, Any] = {}
    for name in ("_extract_create_deliverable_result", "_extract_submit_report_result"):
        m = re.search(
            rf"def {re.escape(name)}\(.*?\)\s*(?:->\s*[^:]+?)?:\s*\n",
            src,
            re.DOTALL,
        )
        if not m:
            result[name] = {"found": False}
            continue
        body = _capture_method_body(src, m.end())
        result[name] = {
            "found": True,
            "has_str_branch": "isinstance(tool_output, str)" in body,
            "has_list_branch": "isinstance(tool_output, list)" in body,
            "has_dict_branch": "isinstance(tool_output, dict)" in body,
            "body_len": len(body.splitlines()),
        }
    return result


def _capture_method_body(src: str, start: int) -> str:
    lines = src[start:].splitlines()
    body: list[str] = []
    for line in lines:
        if line.strip() == "" or line.startswith(" " * 8) or line.startswith("\t\t"):
            body.append(line)
            continue
        break
    return "\n".join(body)


def probe_output_format_integration() -> dict[str, Any]:
    sm = _read(SESSION_MANAGER_PY)
    ind = _read(INDEPENDENT_PY)
    ev = _read(EVALUATOR_PY)
    cb = _read(CONTRACT_BUILDER_PY)
    return {
        "single_prompt_supports_output_format":
            "def single_prompt(" in sm and "output_format" in sm,
        "create_session_supports_output_format":
            bool(re.search(
                r"async def create_session\([^)]*output_format",
                sm,
                re.DOTALL,
            )),
        "claude_session_wrapper_supports_output_format":
            bool(re.search(
                r"class ClaudeSessionWrapper[\s\S]+?output_format",
                sm,
            )),
        "evaluator_uses_output_format": "EVALUATOR_OUTPUT_SCHEMA" in ev,
        "independent_uses_output_format": "output_format=" in ind,
        "contract_builder_has_output_format_section":
            "_build_evaluator_output_format" in cb,
        "sdk_options_injection_pattern":
            'options_dict["output_format"]' in sm
            and '"type": "json_schema"' in sm,
    }


def probe_prompt_legacy_fallback() -> dict[str, Any]:
    src = _read(INDEPENDENT_PY)
    legacy_header = "Legacy Output Format (Fallback)" in src
    legacy_match = re.search(
        r"## Legacy Output Format \(Fallback\)[\s\S]+?(?=##|\Z)",
        src,
    )
    has_file_sha_contract = bool(
        re.search(r"(?i)File:\s*\{.*?file_path", src)
        or re.search(r"(?i)SHA256:\s*\{.*?sha256", src)
    )
    return {
        "legacy_fallback_header_present": legacy_header,
        "legacy_fallback_excerpt": (legacy_match.group(0)[:400] if legacy_match else ""),
        "has_file_sha_contract": has_file_sha_contract,
    }


def probe_mcp_tool_error_paths() -> dict[str, Any]:
    src = _read(CREATE_DELIVERABLE_PY)
    # Error returns currently: {"content":[{"type":"text","text": f"Error: ..."}]} with no is_error
    error_pattern_plain = re.findall(
        r'return \{"content": \[\{"type": "text", "text": f"Error:[^}]+\}\]\}',
        src,
    )
    has_is_error_flag = '"is_error": True' in src or '"is_error":True' in src
    error_embeds_structured_json = '"error":' in src and "json.dumps" in src
    return {
        "error_returns_plain_text_count": len(error_pattern_plain),
        "error_sets_is_error_flag": has_is_error_flag,
        "error_embeds_structured_json": error_embeds_structured_json,
        "error_sample": error_pattern_plain[0] if error_pattern_plain else "",
    }


def probe_tests_skeleton() -> dict[str, Any]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "tests/"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}
    tracked = [f.strip() for f in out.stdout.splitlines() if f.strip()]
    existing = [str(p.relative_to(ROOT)) for p in (ROOT / "tests").glob("*.py")] if (ROOT / "tests").exists() else []
    return {
        "tracked_in_git": tracked,
        "tracked_count": len(tracked),
        "existing_on_disk": existing,
        "existing_count": len(existing),
        "conftest_tracked": any(f.endswith("conftest.py") for f in tracked),
        "deliverable_tools_test_tracked":
            any("deliverable_tools" in f for f in tracked),
    }


# --------------------------------------------------------------------------- #
#  Test case templates                                                        #
# --------------------------------------------------------------------------- #

def make_extractor_tests() -> list[TestCase]:
    base = "tests/test_docuswarm_p0_independent_extractor.py"
    return [
        TestCase(
            file=base,
            class_name="TestExtractCreateDeliverableResult",
            function="test_list_content_with_json_text_block_returns_file_path",
            target_symbol="IndependentAgent._extract_create_deliverable_result",
            arrange=(
                "messages = [{'role':'user','content':[{'type':'tool_result','tool_use_id':'tu1',"
                "'content':[{'type':'text','text': json.dumps({'file_path':'/x/a.md','sha256':'aa'})}],"
                "'is_error':False}]}]"
            ),
            act="file_path, sha = agent._extract_create_deliverable_result(messages)",
            assert_="assert file_path == '/x/a.md' and sha == 'aa'",
        ),
        TestCase(
            file=base,
            class_name="TestExtractCreateDeliverableResult",
            function="test_str_content_backward_compat",
            target_symbol="IndependentAgent._extract_create_deliverable_result",
            arrange=(
                "messages = [{'content':[{'type':'tool_result','tool_use_id':'t',"
                "'content': json.dumps({'file_path':'/x/b.md','sha256':'bb'}),'is_error':False}]}]"
            ),
            act="file_path, sha = agent._extract_create_deliverable_result(messages)",
            assert_="assert file_path == '/x/b.md' and sha == 'bb'",
        ),
        TestCase(
            file=base,
            class_name="TestExtractCreateDeliverableResult",
            function="test_list_content_non_text_block_is_skipped",
            target_symbol="IndependentAgent._extract_create_deliverable_result",
            arrange=(
                "messages=[{'content':[{'type':'tool_result','tool_use_id':'t',"
                "'content':[{'type':'image','source':{...}}],'is_error':False}]}]"
            ),
            act="fp, sh = agent._extract_create_deliverable_result(messages)",
            assert_="assert fp is None and sh is None  # non-text skipped, no crash",
        ),
        TestCase(
            file=base,
            class_name="TestExtractSubmitReportResult",
            function="test_list_content_returns_report",
            target_symbol="IndependentAgent._extract_submit_report_result",
            arrange=(
                "report={'status':'success','report':{'deliverable':{'title':'T','file_path':'/x.md','sha256':'aa'},"
                "'questions':[],'action':'create_deliverable'}}; "
                "messages=[{'content':[{'type':'tool_result','tool_use_id':'t',"
                "'content':[{'type':'text','text':json.dumps(report)}],'is_error':False}]}]"
            ),
            act="reports = agent._extract_submit_report_result(messages)",
            assert_="assert len(reports)==1 and reports[0]['deliverable']['file_path']=='/x.md'",
        ),
        TestCase(
            file=base,
            class_name="TestExtractSubmitReportResult",
            function="test_error_is_error_flag_skipped",
            target_symbol="IndependentAgent._extract_submit_report_result",
            arrange=(
                "messages=[{'content':[{'type':'tool_result','tool_use_id':'t',"
                "'content':[{'type':'text','text':'Error: invalid'}],'is_error':True}]}]"
            ),
            act="reports = agent._extract_submit_report_result(messages)",
            assert_="assert reports == []",
        ),
        TestCase(
            file=base,
            class_name="TestMarkdownFallbackEndToEnd",
            function="test_parse_response_recovers_from_markdown_with_list_tool_result",
            target_symbol="IndependentAgent._parse_response",
            arrange=(
                "messages=[{'content':[{'type':'tool_result','tool_use_id':'t1',"
                "'content':[{'type':'text','text':json.dumps({'file_path':'/o/ux.md','sha256':'ae2e5715'})}]}]},"
                "{'content':[{'type':'text','text':'## Execution Complete\\nI have successfully...'}]}]"
            ),
            act="data = agent._parse_response(messages)",
            assert_=(
                "assert data['deliverable']['file_path']=='/o/ux.md' "
                "and data['deliverable']['sha256']=='ae2e5715' "
                "and data['action']=='create_deliverable'"
            ),
        ),
    ]


def make_prompt_tightening_tests() -> list[TestCase]:
    base = "tests/test_docuswarm_p1_prompt_tightening.py"
    return [
        TestCase(
            file=base,
            class_name="TestLegacyFallbackRemoved",
            function="test_system_prompt_does_not_advertise_legacy_fallback",
            target_symbol="IndependentAgent._format_system_prompt",
            arrange="agent = build_agent(node_id='ux')",
            act="prompt = agent._format_system_prompt()",
            assert_=(
                "assert 'Legacy Output Format' not in prompt "
                "and 'MAY return this JSON structure directly' not in prompt"
            ),
        ),
        TestCase(
            file=base,
            class_name="TestExplicitFileSha256Contract",
            function="test_prompt_requires_file_and_sha256_lines",
            target_symbol="IndependentAgent._format_system_prompt",
            arrange="agent = build_agent(node_id='ux')",
            act="prompt = agent._format_system_prompt()",
            assert_=(
                "assert 'File:' in prompt and 'SHA256:' in prompt  "
                "# enforce fallback-regex harvest contract"
            ),
        ),
        TestCase(
            file=base,
            class_name="TestSubmitReportMandatoryHeader",
            function="test_prompt_still_requires_submit_execution_report",
            target_symbol="IndependentAgent._format_system_prompt",
            arrange="agent = build_agent(node_id='ux')",
            act="prompt = agent._format_system_prompt()",
            assert_="assert 'submit_execution_report' in prompt and 'MANDATORY' in prompt",
        ),
    ]


def make_regex_fallback_tests() -> list[TestCase]:
    base = "tests/test_docuswarm_p1_markdown_regex_fallback.py"
    return [
        TestCase(
            file=base,
            class_name="TestFileShaRegexHarvest",
            function="test_extracts_file_and_sha256_from_markdown_summary",
            target_symbol="IndependentAgent._extract_file_sha_from_markdown",
            arrange=(
                "content = '## Execution Complete\\n\\nFile: /out/ux.md\\nSHA256: "
                "ae2e5715bae2d9e6...'"
            ),
            act="fp, sh = agent._extract_file_sha_from_markdown(content)",
            assert_="assert fp == '/out/ux.md' and sh.startswith('ae2e5715')",
        ),
        TestCase(
            file=base,
            class_name="TestFileShaRegexHarvest",
            function="test_returns_none_when_missing",
            target_symbol="IndependentAgent._extract_file_sha_from_markdown",
            arrange="content = '## Summary\\n\\nNo metadata here.'",
            act="fp, sh = agent._extract_file_sha_from_markdown(content)",
            assert_="assert fp is None and sh is None",
        ),
        TestCase(
            file=base,
            class_name="TestRegexFallbackIntegration",
            function="test_parse_response_uses_regex_when_tool_result_missing",
            target_symbol="IndependentAgent._parse_response",
            arrange=(
                "messages=[{'content':[{'type':'text','text':"
                "'## Done\\nFile: /out/ux.md\\nSHA256: '+'a'*64}]}]"
            ),
            act="data = agent._parse_response(messages)",
            assert_=(
                "assert data['deliverable']['file_path']=='/out/ux.md' "
                "and data['deliverable']['sha256']=='a'*64"
            ),
        ),
    ]


def make_deepseek_adaptation_tests() -> list[TestCase]:
    base = "tests/test_docuswarm_p2_deepseek_adaptation.py"
    return [
        TestCase(
            file=base,
            class_name="TestToolErrorEmbedding",
            function="test_error_response_embeds_structured_json",
            target_symbol="create_deliverable_tool (inside create_deliverable_server)",
            arrange=(
                "server = create_deliverable_server(output_dir='/nonexistent/no-perm')"
            ),
            act="result = await server.tools['create_deliverable'].handler({'title':'x','content':'y'})",
            assert_=(
                "body = json.loads(result['content'][0]['text']); "
                "assert body['error'] and 'hint' in body  # structured, not plain 'Error: ...'"
            ),
        ),
        TestCase(
            file=base,
            class_name="TestToolErrorIsErrorFlag",
            function="test_error_sets_is_error_true",
            target_symbol="create_deliverable_tool",
            arrange="server = create_deliverable_server(output_dir='/nonexistent')",
            act="result = await server.tools['create_deliverable'].handler({'title':'x','content':'y'})",
            assert_="assert result.get('is_error') is True  # honor Anthropic contract even if DeepSeek ignores",
        ),
        TestCase(
            file=base,
            class_name="TestObservabilityToolResultShape",
            function="test_llm_tool_result_logs_content_shape",
            target_symbol="session_manager._convert_content_block",
            arrange="item = ToolResultBlock(tool_use_id='x', content=[{'type':'text','text':'{}'}], is_error=False)",
            act="converted = session_manager._convert_content_block(item); session_manager._logger.info_calls",
            assert_=(
                "# structlog capture asserts a 'tool_result_content_shape' log field "
                "# is emitted with value 'list' when content is list"
            ),
        ),
    ]


def make_output_format_tests() -> list[TestCase]:
    base = "tests/test_docuswarm_p3_output_format_for_independent.py"
    return [
        TestCase(
            file=base,
            class_name="TestCreateSessionOutputFormat",
            function="test_create_session_accepts_output_format",
            target_symbol="SessionManager.create_session",
            arrange="sm = SessionManager(config=...)",
            act=(
                "session = await sm.create_session(mode='agent', yolo=True, "
                "output_format=INDEPENDENT_OUTPUT_SCHEMA)"
            ),
            assert_=(
                "assert session._options.output_format == "
                "{'type':'json_schema','schema':INDEPENDENT_OUTPUT_SCHEMA}"
            ),
        ),
        TestCase(
            file=base,
            class_name="TestIndependentPassesOutputFormat",
            function="test_independent_agent_passes_output_format_through",
            target_symbol="IndependentAgent._call_llm_with_prompts",
            arrange="agent = build_agent(node_id='ux'); patched_create_session = record_calls(sm)",
            act="await agent._call_llm_with_prompts('s','u')",
            assert_=(
                "call = patched_create_session.call_args; "
                "assert 'output_format' in call.kwargs"
            ),
        ),
    ]


# --------------------------------------------------------------------------- #
#  Readiness assembly                                                         #
# --------------------------------------------------------------------------- #

def assemble_readiness() -> list[FixReadiness]:
    extr = probe_extractor_branches()
    of_probe = probe_output_format_integration()
    prompt_probe = probe_prompt_legacy_fallback()
    tool_err_probe = probe_mcp_tool_error_paths()
    tests_probe = probe_tests_skeleton()

    items: list[FixReadiness] = []

    # §7.1
    missing_list = [
        name for name, info in extr.items()
        if info.get("has_str_branch") and not info.get("has_list_branch")
    ]
    items.append(FixReadiness(
        fix_id="7.1",
        title="提取器补齐 list 分支（P0 阻塞级）",
        scope=f"{INDEPENDENT_PY.relative_to(ROOT)} :: {', '.join(missing_list) or 'n/a'}",
        prereq_status="ready" if missing_list else "blocked",
        prereq_evidence=[
            f"{name}: missing_list_branch={not info.get('has_list_branch')}"
            for name, info in extr.items()
        ],
        risk="low",
        effort_hours=1.0,
        test_cases=make_extractor_tests(),
    ))

    # §7.2 — regression tests
    items.append(FixReadiness(
        fix_id="7.2",
        title="回归测试套件（P0 伴生）",
        scope="tests/test_docuswarm_p0_independent_extractor.py",
        prereq_status="ready" if tests_probe.get("conftest_tracked") else "partial",
        prereq_evidence=[
            f"tracked_count={tests_probe.get('tracked_count')}",
            f"conftest_tracked={tests_probe.get('conftest_tracked')}",
            f"deliverable_tools_test_tracked={tests_probe.get('deliverable_tools_test_tracked')}",
            "note: tests/ 当前在本地被删除但 git HEAD 仍保留；重启 TDD 前需 git checkout 恢复",
        ],
        risk="low",
        effort_hours=2.0,
        test_cases=[],  # merged into 7.1 test file
    ))

    # §7.3 — prompt tightening + optional output_format
    blocking: list[str] = []
    if not of_probe.get("create_session_supports_output_format"):
        blocking.append(
            "SessionManager.create_session 尚未接受 output_format 参数，"
            "启用 IndependentAgent 硬约束需先扩展该 API（复用 single_prompt 实现逻辑）。"
        )
    if not of_probe.get("claude_session_wrapper_supports_output_format"):
        blocking.append(
            "ClaudeSessionWrapper 路径可能需要透传 output_format 到 options。"
        )
    items.append(FixReadiness(
        fix_id="7.3",
        title="Prompt 收紧：删除 Legacy Fallback，启用 output_format（P1）",
        scope=(
            f"{INDEPENDENT_PY.relative_to(ROOT)} :: _format_system_prompt, "
            f"{SESSION_MANAGER_PY.relative_to(ROOT)} :: create_session"
        ),
        prereq_status=(
            "partial" if blocking else "ready"
        ),
        prereq_evidence=[
            f"legacy_fallback_header_present={prompt_probe.get('legacy_fallback_header_present')}",
            f"evaluator_uses_output_format={of_probe.get('evaluator_uses_output_format')}",
            f"independent_uses_output_format={of_probe.get('independent_uses_output_format')}",
            f"single_prompt_supports_output_format={of_probe.get('single_prompt_supports_output_format')}",
            f"create_session_supports_output_format={of_probe.get('create_session_supports_output_format')}",
        ],
        risk="medium",
        effort_hours=4.0,
        test_cases=make_prompt_tightening_tests() + make_output_format_tests(),
        blocking_unknowns=blocking,
    ))

    # §7.4 — regex fallback
    items.append(FixReadiness(
        fix_id="7.4",
        title="Markdown 正则兜底抓取 File/SHA256（P1 防御）",
        scope=f"{INDEPENDENT_PY.relative_to(ROOT)} :: _extract_data_from_content",
        prereq_status=(
            "ready" if prompt_probe.get("has_file_sha_contract") else "partial"
        ),
        prereq_evidence=[
            f"has_file_sha_contract_in_prompt={prompt_probe.get('has_file_sha_contract')}",
            "若 prompt 未要求 LLM 打印 'File: / SHA256:'，需在 §7.3 一起加入",
        ],
        risk="low",
        effort_hours=2.0,
        test_cases=make_regex_fallback_tests(),
    ))

    # §7.5 — DeepSeek adaptation
    items.append(FixReadiness(
        fix_id="7.5",
        title="DeepSeek 兼容性适配（P2）",
        scope=(
            f"{CREATE_DELIVERABLE_PY.relative_to(ROOT)} :: create_deliverable_tool/submit_execution_report_tool, "
            f"{SESSION_MANAGER_PY.relative_to(ROOT)} :: _convert_content_block"
        ),
        prereq_status="ready",
        prereq_evidence=[
            f"error_returns_plain_text_count={tool_err_probe.get('error_returns_plain_text_count')}",
            f"error_sets_is_error_flag={tool_err_probe.get('error_sets_is_error_flag')}",
            f"error_embeds_structured_json={tool_err_probe.get('error_embeds_structured_json')}",
            "DeepSeek 忽略 is_error，需要把错误嵌入 text 为 JSON。",
        ],
        risk="medium",
        effort_hours=3.0,
        test_cases=make_deepseek_adaptation_tests(),
    ))

    return items


def build_summary(readiness: list[FixReadiness]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    total_effort = 0.0
    for r in readiness:
        by_status[r.prereq_status] = by_status.get(r.prereq_status, 0) + 1
        total_effort += r.effort_hours
    tc_count = sum(len(r.test_cases) for r in readiness)
    return {
        "total_fix_items": len(readiness),
        "total_test_cases": tc_count,
        "total_effort_hours_estimate": total_effort,
        "by_prereq_status": by_status,
        "critical_path": [r.fix_id for r in readiness if r.prereq_status == "ready"],
        "has_blocking_unknowns": [
            r.fix_id for r in readiness if r.blocking_unknowns
        ],
    }


# --------------------------------------------------------------------------- #
#  Main                                                                       #
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description="DocuSwarm 修复方案可行性研究")
    parser.add_argument(
        "--output",
        default="docs-doc/solution/2026-05-02-deepseek-mcp-toolresult-solution-readiness.json",
    )
    args = parser.parse_args()

    report = SolutionReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_report="docs-doc/research/2026-05-02-deepseek-mcp-toolresult-deep-research.md",
    )
    report.readiness = assemble_readiness()
    report.summary = build_summary(report.readiness)

    payload = {
        "generated_at": report.generated_at,
        "source_report": report.source_report,
        "readiness": [asdict(r) for r in report.readiness],
        "summary": report.summary,
    }
    out = Path(args.output)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("SOLUTION READINESS")
    print("=" * 60)
    for r in report.readiness:
        print(f"  [{r.prereq_status.upper():7s}] §{r.fix_id} {r.title} "
              f"(risk={r.risk}, tc={len(r.test_cases)}, hrs~{r.effort_hours})")
        for b in r.blocking_unknowns:
            print(f"      ⚠ blocking: {b}")
    print("\nSUMMARY:", json.dumps(report.summary, ensure_ascii=False))
    print(f"\n[OK] 报告已写入 {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
