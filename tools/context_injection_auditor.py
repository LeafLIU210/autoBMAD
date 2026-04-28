from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Evidence:
    path: str
    line: int
    snippet: str


@dataclass
class Finding:
    finding_id: str
    severity: str
    title: str
    summary: str
    recommendation: str
    evidences: list[Evidence]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _find_lines(path: Path, patterns: Iterable[str]) -> list[Evidence]:
    text = _read_text(path)
    lines = text.splitlines()
    evidences: list[Evidence] = []
    for idx, line in enumerate(lines, start=1):
        for pattern in patterns:
            if pattern in line:
                evidences.append(
                    Evidence(
                        path=str(path.relative_to(PROJECT_ROOT)),
                        line=idx,
                        snippet=line.strip(),
                    )
                )
                break
    return evidences


def _has_pattern(path: Path, pattern: str) -> bool:
    return pattern in _read_text(path)


def _scan_node_yaml(node_yaml: Path) -> dict[str, object]:
    text = _read_text(node_yaml)
    top_level_keys = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", line):
            key = line.split(":", 1)[0].strip()
            top_level_keys.append(key)

    return {
        "path": str(node_yaml.relative_to(PROJECT_ROOT)),
        "has_task_block": bool(re.search(r"^task\s*:", text, re.MULTILINE)),
        "has_role_supplement": "role_supplement:" in text,
        "has_template_title": "template_title:" in text,
        "has_required_sections": "required_sections:" in text,
        "has_output_filename": "output_filename:" in text,
        "top_level_keys": top_level_keys,
    }


def build_findings() -> tuple[list[Finding], list[dict[str, object]], list[str]]:
    executor = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
    dual_agent = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
    independent = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    graph = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
    node_loader = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "nodes" / "loader.py"
    state_manager = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
    update_context = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "update_context.py"
    read_docs_file = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "read_docs_file.py"
    list_docs_files = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "list_docs_files.py"
    main_py = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "main.py"
    independent_agent_yaml = (
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
    )

    findings: list[Finding] = []

    findings.append(
        Finding(
            finding_id="F001",
            severity="high",
            title="Node configuration is loaded but not assembled into the prompt contract",
            summary=(
                "The executor loads node configuration, but downstream execution still derives the task "
                "from serialized runtime state instead of a stable node contract."
            ),
            recommendation=(
                "Introduce a single NodeExecutionContext that carries node task, role supplement, "
                "deliverable requirements, original context, and chained deliverables end-to-end."
            ),
            evidences=[
                *_find_lines(executor, ["node_config = loader.load", "task = _extract_task_from_state(state)"]),
                *_find_lines(node_loader, ["deliverable_type", "persona", "evaluator"]),
                *_find_lines(independent, ["def _format_system_prompt", "deliverable.content"]),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="F002",
            severity="high",
            title="Task extraction collapses node intent into raw context payload",
            summary=(
                "The current task extraction prefers subject context content from serialized state, "
                "so node-specific work instructions are replaced by raw input text or previous deliverables."
            ),
            recommendation=(
                "Replace `_extract_task_from_state()` with contract-first assembly from node config and "
                "a normalized pipeline context object."
            ),
            evidences=_find_lines(
                executor,
                [
                    "def _extract_task_from_state",
                    'if isinstance(context_data, dict) and "subject_context" in context_data:',
                    'if "content" in subject_dict:',
                    'return str(subject_dict["content"])',
                    'if "deliverable" in context_data:',
                ],
            ),
        )
    )

    findings.append(
        Finding(
            finding_id="F003",
            severity="high",
            title="DualAgentNode re-wraps context and breaks structure expected by IndependentAgent",
            summary=(
                "The node wrapper turns subject context into `{subject, task}` and the IndependentAgent "
                "then tries to re-discover content through best-effort parsing."
            ),
            recommendation=(
                "Pass a structured execution context object directly into both agents. Avoid stringifying "
                "and re-wrapping the same payload across layers."
            ),
            evidences=[
                *_find_lines(
                    dual_agent,
                    [
                        'subject_context={"subject": subject_context, "task": task}',
                        'independent_context["pipeline_id"] = pipeline_id',
                    ],
                ),
                *_find_lines(
                    independent,
                    [
                        'subject_context_raw = context.get("subject_context", {})',
                        'subject_context_data = json_module.loads(subject_context_raw)',
                        'nested_ctx = subject_context_data.get("subject_context", {})',
                        'raw_content = subject_context_data.get("content")',
                    ],
                ),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="F004",
            severity="high",
            title="Deliverable persistence currently has two truths",
            summary=(
                "The IndependentAgent prompt defines `deliverable.content` as a short summary, but the "
                "pipeline graph writes that field back to storage as if it were the canonical deliverable."
            ),
            recommendation=(
                "Use tool-written markdown files as the single truth. Keep only metadata, summary, file path, "
                "hash, and section inventory in pipeline state."
            ),
            evidences=[
                *_find_lines(
                    independent,
                    [
                        'The "deliverable.content" field is just a SUMMARY',
                        "The full document was already saved via the tool",
                    ],
                ),
                *_find_lines(
                    graph,
                    [
                        'content = deliverable.get("content") or deliverable.get("markdown") or str(deliverable)',
                        "await storage.save_deliverable(",
                    ],
                ),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="F005",
            severity="medium",
            title="update_context is exposed as a capability but does not persist anything",
            summary=(
                "The tool acknowledges updates without mutating any shared state, which makes the agent "
                "believe it can evolve context while the system remains unchanged."
            ),
            recommendation=(
                "Wire the tool to StateManager with a bounded schema and audit trail, or remove it until the "
                "real persistence path exists."
            ),
            evidences=[
                *_find_lines(update_context, ["This is a no-op implementation", "return ToolOk("]),
                *_find_lines(state_manager, ["class StateManager", "def update_subject_context"]),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="F006",
            severity="medium",
            title="Docs tools exist, but there is no controlled context expansion policy",
            summary=(
                "The docs tools are registered, yet the runtime prompt does not define selection order, token "
                "budgeting, or when docs content should become part of the working context."
            ),
            recommendation=(
                "Introduce a docs retrieval policy layer: list -> select -> read -> summarize -> attach "
                "summary to execution context, with per-node allowlists and size limits."
            ),
            evidences=[
                *_find_lines(independent_agent_yaml, ["read_docs_file", "list_docs_files", "update_docs_file"]),
                *_find_lines(read_docs_file, ['name: str = "read_docs_file"']),
                *_find_lines(list_docs_files, ['name: str = "list_docs_files"']),
            ],
        )
    )

    if not (PROJECT_ROOT / "autoBMAD" / "docuswarm" / "utils" / "context_resolver.py").exists():
        findings.append(
            Finding(
                finding_id="F007",
                severity="medium",
                title="The documented @ path injection entry point is missing in current code",
                summary=(
                    "Architecture and research docs describe a ContextResolver and @ path injection flow, but "
                    "the expected module is absent and `main.py` does not integrate it."
                ),
                recommendation=(
                    "Treat docs injection as a separate controlled stage. Only add a resolver when the design "
                    "for canonical context assembly is finalized."
                ),
                evidences=_find_lines(main_py, ["subject_context =", "content ="]),
            )
        )

    node_yaml_dir = PROJECT_ROOT / "autoBMAD" / "nodes"
    node_inventory = sorted(
        (_scan_node_yaml(path) for path in node_yaml_dir.glob("*/node.yaml")),
        key=lambda item: str(item["path"]),
    )

    extra_notes: list[str] = []
    if all(not item["has_task_block"] for item in node_inventory):
        extra_notes.append(
            "All current node.yaml files under autoBMAD/nodes still use the older schema without a top-level task block."
        )
    if any(item["has_required_sections"] for item in node_inventory):
        extra_notes.append(
            "Current node.yaml files do include required_sections, which means prompt injection can be restored without inventing new authoring artifacts."
        )

    return findings, node_inventory, extra_notes


def render_markdown(findings: list[Finding], node_inventory: list[dict[str, object]], notes: list[str]) -> str:
    lines: list[str] = []
    lines.append("# DocuSwarm Context Injection Audit")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Static audit of context contract, prompt assembly, persistence, and docs expansion paths.")
    lines.append("- Focused on the current `autoBMAD/docuswarm` implementation and `autoBMAD/nodes/*/node.yaml`.")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    for finding in findings:
        lines.append(f"### {finding.finding_id} [{finding.severity.upper()}] {finding.title}")
        lines.append("")
        lines.append(f"- Summary: {finding.summary}")
        lines.append(f"- Recommendation: {finding.recommendation}")
        lines.append("- Evidence:")
        for evidence in finding.evidences:
            lines.append(
                f"  - `{evidence.path}:{evidence.line}` -> `{evidence.snippet}`"
            )
        lines.append("")

    lines.append("## Node YAML Inventory")
    lines.append("")
    for item in node_inventory:
        lines.append(f"### `{item['path']}`")
        lines.append("")
        lines.append(f"- Top-level keys: {', '.join(item['top_level_keys'])}")
        lines.append(f"- Has `task` block: {item['has_task_block']}")
        lines.append(f"- Has `role_supplement`: {item['has_role_supplement']}")
        lines.append(f"- Has `template_title`: {item['has_template_title']}")
        lines.append(f"- Has `required_sections`: {item['has_required_sections']}")
        lines.append(f"- Has `output_filename`: {item['has_output_filename']}")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit DocuSwarm context injection, prompt assembly, and persistence contracts."
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Optional file path for the generated report")
    args = parser.parse_args()

    findings, node_inventory, notes = build_findings()

    if args.format == "json":
        result = {
            "findings": [
                {
                    "finding_id": finding.finding_id,
                    "severity": finding.severity,
                    "title": finding.title,
                    "summary": finding.summary,
                    "recommendation": finding.recommendation,
                    "evidences": [
                        {
                            "path": evidence.path,
                            "line": evidence.line,
                            "snippet": evidence.snippet,
                        }
                        for evidence in finding.evidences
                    ],
                }
                for finding in findings
            ],
            "node_inventory": node_inventory,
            "notes": notes,
        }
        output_text = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output_text = render_markdown(findings, node_inventory, notes)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
    else:
        sys.stdout.buffer.write(output_text.encode("utf-8"))
        if not output_text.endswith("\n"):
            sys.stdout.buffer.write(b"\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
