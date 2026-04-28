from __future__ import annotations

import argparse
import json
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
    impact: str
    recommendation: str
    evidences: list[Evidence]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _find_lines(path: Path, patterns: Iterable[str]) -> list[Evidence]:
    if not path.exists():
        return []

    lines = _read_text(path).splitlines()
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


def _count_hits(paths: Iterable[Path], patterns: Iterable[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for path in paths:
        if not path.exists():
            continue
        count = len(_find_lines(path, patterns))
        if count:
            result[str(path.relative_to(PROJECT_ROOT))] = count
    return dict(sorted(result.items()))


def _build_target_paths() -> dict[str, list[Path]]:
    runtime = [
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "independent.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "evaluator.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "context_builder.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "__init__.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "read_docs_file.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "list_docs_files.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "update_docs_file.py",
        PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "create_document_set.py",
    ]

    tests = [
        PROJECT_ROOT / "tests" / "unit" / "tools" / "test_read_docs_file.py",
        PROJECT_ROOT / "tests" / "unit" / "tools" / "test_list_docs_files.py",
        PROJECT_ROOT / "tests" / "unit" / "tools" / "test_update_docs_file.py",
        PROJECT_ROOT / "tests" / "unit" / "tools" / "test_explicit_registration.py",
        PROJECT_ROOT / "tests" / "unit" / "test_contract_builder.py",
        PROJECT_ROOT / "tests" / "unit" / "test_node_execution_context.py",
        PROJECT_ROOT / "tests" / "unit" / "nodes" / "test_dual_agent_single_truth.py",
        PROJECT_ROOT / "tests" / "unit" / "agents" / "test_evaluator_reads_file.py",
        PROJECT_ROOT / "tests" / "integration" / "test_single_truth_workflow.py",
    ]

    tools = [
        PROJECT_ROOT / "tools" / "README.md",
        PROJECT_ROOT / "tools" / "context_injection_auditor.py",
        PROJECT_ROOT / "tools" / "node_execution_context_researcher.py",
    ]

    return {"runtime": runtime, "tests": tests, "tools": tools}


def build_findings() -> tuple[list[Finding], dict[str, dict[str, int]]]:
    targets = _build_target_paths()

    findings: list[Finding] = []

    findings.append(
        Finding(
            finding_id="D001",
            severity="high",
            title="Runtime still exposes docs read/write tools as workflow capabilities",
            summary=(
                "Under Option A, the workflow must not read docs/. The current runtime still exposes "
                "read_docs_file, list_docs_files, and update_docs_file through the Independent agent "
                "configuration and package exports."
            ),
            impact=(
                "If P1-2 is removed but these capabilities remain, the system contract will still permit "
                "docs/ access at runtime and the product decision cannot be enforced."
            ),
            recommendation=(
                "Remove docs read/write tools from the default runtime surface: agent config, tool exports, "
                "and any registration path that makes them discoverable to workflow execution."
            ),
            evidences=[
                *_find_lines(
                    targets["runtime"][0],
                    ["read_docs_file", "list_docs_files", "update_docs_file"],
                ),
                *_find_lines(
                    targets["runtime"][5],
                    ["ReadDocsFileTool", "ListDocsFilesTool", "UpdateDocsFileTool"],
                ),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="D002",
            severity="high",
            title="docs/ is still hard-coded as a filesystem dependency in runtime tool modules",
            summary=(
                "Three runtime modules compute the project docs root directly and implement list/read/write "
                "behavior against that directory."
            ),
            impact=(
                "These modules are no longer dormant implementation details once they are registered; they are "
                "a direct contradiction of the decision that workflows never read docs/."
            ),
            recommendation=(
                "Delete or quarantine read_docs_file.py, list_docs_files.py, and update_docs_file.py from the "
                "workflow runtime. Keep them only if a separate non-workflow maintenance surface truly needs them."
            ),
            evidences=[
                *_find_lines(
                    targets["runtime"][6],
                    ['return project_root / "docs"', 'name: str = "read_docs_file"'],
                ),
                *_find_lines(
                    targets["runtime"][7],
                    ['self.docs_root = project_root / "docs"', 'name: str = "list_docs_files"'],
                ),
                *_find_lines(
                    targets["runtime"][8],
                    ['self.docs_root = project_root / "docs"', 'name: str = "update_docs_file"'],
                ),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="D003",
            severity="medium",
            title="Execution contracts still reserve docs_context even though no docs-free runtime should use it",
            summary=(
                "The NodeExecutionContext schema and agent fallbacks still carry docs_context, but current code "
                "fills it with empty lists only."
            ),
            impact=(
                "Leaving this field in place after removing P1-2 risks future reintroduction of docs reads and "
                "keeps the execution contract wider than the product decision requires."
            ),
            recommendation=(
                "Decide whether docs_context should be removed from contracts entirely or explicitly marked as "
                "deprecated and forbidden for workflow use."
            ),
            evidences=[
                *_find_lines(targets["runtime"][3], ["docs_context: list[dict[str, Any]]"]),
                *_find_lines(targets["runtime"][4], ["docs_context=[]"]),
                *_find_lines(targets["runtime"][1], ["docs_context=[]"]),
                *_find_lines(targets["runtime"][2], ["docs_context=[]"]),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="D004",
            severity="high",
            title="Tests explicitly lock in docs tool existence and registration",
            summary=(
                "The test suite contains dedicated unit tests for read_docs_file, list_docs_files, and "
                "update_docs_file, plus registration tests that assert these tools must exist."
            ),
            impact=(
                "Option A cannot be implemented safely without deleting or rewriting these tests. Otherwise the "
                "test suite will preserve the old contract by design."
            ),
            recommendation=(
                "Remove dedicated docs-tool test suites and update registration tests to reflect a workflow "
                "surface that no longer includes docs read/write tools."
            ),
            evidences=[
                *_find_lines(
                    targets["tests"][0],
                    ["read_docs_file function", 'ToolRegistry.get("read_docs_file")'],
                ),
                *_find_lines(
                    targets["tests"][1],
                    ["list_docs_files function", 'ToolRegistry.get("list_docs_files")'],
                ),
                *_find_lines(
                    targets["tests"][2],
                    ["update_docs_file function", 'ToolRegistry.get("update_docs_file")'],
                ),
                *_find_lines(
                    targets["tests"][3],
                    ['"read_docs_file"', '"list_docs_files"', '"update_docs_file"'],
                ),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="D005",
            severity="medium",
            title="Docs-tool tests are already drifting from the current runtime implementation",
            summary=(
                "Several tests assume an async function-based docs API and the absence of kimi_agent_sdk imports, "
                "while the current modules still expose CallableTool2 classes."
            ),
            impact=(
                "This drift means the docs-tool tests should not be carried forward into a docs-free workflow. "
                "Deleting them is lower risk than trying to repair a capability the product no longer wants."
            ),
            recommendation=(
                "Treat docs-tool tests as removal candidates, not migration candidates. The product decision "
                "eliminates their target behavior."
            ),
            evidences=[
                *_find_lines(
                    targets["tests"][0],
                    ["from docuswarm.tools.read_docs_file import ReadDocsFileParams, read_docs_file"],
                ),
                *_find_lines(
                    targets["tests"][0],
                    ["assert not hasattr(module, 'CallableTool2')"],
                ),
                *_find_lines(targets["runtime"][6], ["from kimi_agent_sdk import CallableTool2"]),
                *_find_lines(
                    targets["tests"][2],
                    ["assert not hasattr(module, 'CallableTool2')"],
                ),
                *_find_lines(targets["runtime"][8], ["from kimi_agent_sdk import CallableTool2"]),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="D006",
            severity="medium",
            title="Existing debug tooling still assumes docs expansion is a viable direction",
            summary=(
                "The current tools README and context audit utility still frame docs expansion as something to "
                "design and improve, which conflicts with the new product decision."
            ),
            impact=(
                "If debugging tools keep recommending docs expansion, future investigations may accidentally "
                "re-open a capability that should be retired."
            ),
            recommendation=(
                "Update research/debug tooling so the new baseline is explicit: workflow execution must not "
                "read docs/, and any remaining docs references are migration debt."
            ),
            evidences=[
                *_find_lines(
                    targets["tools"][0],
                    ["docs expansion paths", "docs 工具是否具备受控扩展策略"],
                ),
                *_find_lines(
                    targets["tools"][1],
                    ["docs tools exist", "Introduce a docs retrieval policy layer"],
                ),
                *_find_lines(
                    targets["tools"][2],
                    ["docs_context", "source\": \"docs tools\""],
                ),
            ],
        )
    )

    findings.append(
        Finding(
            finding_id="D007",
            severity="info",
            title="create_document_set is adjacent to docs tooling but is not a docs-read dependency",
            summary=(
                "create_document_set writes to the current working directory rather than reading from docs/. "
                "It should not be removed solely because P1-2 is removed."
            ),
            impact=(
                "A broad cleanup could accidentally delete a still-valid output-side capability if docs tools "
                "and multi-file output are treated as the same concern."
            ),
            recommendation=(
                "Keep create_document_set under output/work_dir governance and decouple it from any docs-specific "
                "cleanup work."
            ),
            evidences=_find_lines(targets["runtime"][9], ["output_dir = Path.cwd()"]),
        )
    )

    inventory = {
        "runtime": _count_hits(
            targets["runtime"],
            ["read_docs_file", "list_docs_files", "update_docs_file", "docs_context", '"docs"', "docs/"],
        ),
        "tests": _count_hits(
            targets["tests"],
            ["read_docs_file", "list_docs_files", "update_docs_file", "docs_context"],
        ),
        "tools": _count_hits(
            targets["tools"],
            ["read_docs_file", "list_docs_files", "update_docs_file", "docs_context", "docs expansion"],
        ),
    }

    return findings, inventory


def render_markdown(findings: list[Finding], inventory: dict[str, dict[str, int]]) -> str:
    runtime_files = len(inventory["runtime"])
    test_files = len(inventory["tests"])
    tool_files = len(inventory["tools"])

    lines: list[str] = []
    lines.append("# DocuSwarm Docs-Free Workflow Dependency Research")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Decision baseline: Option A is adopted for P1-2.")
    lines.append("- Product decision: workflow execution must never read `docs/`.")
    lines.append("- Analysis scope: `autoBMAD/docuswarm`, `tests`, and debugging tools under `tools/`.")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        "- The runtime still exposes docs read/write capabilities, so the current codebase does not enforce the docs-free workflow decision."
    )
    lines.append(
        "- The test suite explicitly preserves docs tools and their registration, so Option A requires coordinated test removal or rewrite."
    )
    lines.append(
        "- The execution contract still carries `docs_context`, even though current runtime only passes empty lists."
    )
    lines.append(
        "- Existing debug tooling still points investigators toward docs expansion rather than docs removal."
    )
    lines.append(
        "- `create_document_set` is adjacent but should remain governed by `output/`, not removed with docs tooling."
    )
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    lines.append(f"- Runtime files with docs-related hits: {runtime_files}")
    lines.append(f"- Test files with docs-related hits: {test_files}")
    lines.append(f"- Debug/tooling files with docs-related hits: {tool_files}")
    lines.append("")

    for section_name in ("runtime", "tests", "tools"):
        lines.append(f"### {section_name.title()} Hit Map")
        lines.append("")
        for path, count in inventory[section_name].items():
            lines.append(f"- `{path}` -> {count} hit(s)")
        lines.append("")

    lines.append("## Findings")
    lines.append("")
    for finding in findings:
        lines.append(f"### {finding.finding_id} [{finding.severity.upper()}] {finding.title}")
        lines.append("")
        lines.append(f"- Summary: {finding.summary}")
        lines.append(f"- Impact: {finding.impact}")
        lines.append(f"- Recommendation: {finding.recommendation}")
        lines.append("- Evidence:")
        for evidence in finding.evidences:
            lines.append(f"  - `{evidence.path}:{evidence.line}` -> `{evidence.snippet}`")
        lines.append("")

    lines.append("## Removal Implications")
    lines.append("")
    lines.append("- Delete or isolate runtime docs tool modules from workflow execution surfaces.")
    lines.append("- Remove docs tool entries from default agent configuration.")
    lines.append("- Rewrite tool registration expectations in tests to drop docs tool names.")
    lines.append("- Decide whether `docs_context` should be removed or deprecated from execution contracts.")
    lines.append("- Update debug tooling so future audits treat docs references as debt, not roadmap.")
    lines.append("- Keep `create_document_set` as an output-side capability if multi-file output is still needed.")
    lines.append("")
    lines.append("## Recommended Next Step Order")
    lines.append("")
    lines.append("1. Freeze the decision in research/evaluation docs.")
    lines.append("2. Remove docs tool exposure from runtime configs and exports.")
    lines.append("3. Delete or rewrite docs-tool test suites and registration expectations.")
    lines.append("4. Clean up `docs_context` contract residue.")
    lines.append("5. Rebaseline debug tooling and architecture research assumptions.")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit DocuSwarm runtime/test dependencies that conflict with a docs-free workflow."
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Optional file path for the generated report")
    args = parser.parse_args()

    findings, inventory = build_findings()

    if args.format == "json":
        payload = {
            "findings": [
                {
                    "finding_id": finding.finding_id,
                    "severity": finding.severity,
                    "title": finding.title,
                    "summary": finding.summary,
                    "impact": finding.impact,
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
            "inventory": inventory,
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(findings, inventory)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
