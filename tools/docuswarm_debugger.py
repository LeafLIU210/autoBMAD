from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class Finding:
    severity: str
    title: str
    detail: str


@dataclass
class RegistrySnapshot:
    before_import_count: int
    after_import_count: int
    tool_names: list[str]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _load_pipeline(conn: sqlite3.Connection, pipeline_id: str) -> dict[str, Any] | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT pipeline_id, subject, status, current_node, state_json, created_at, updated_at "
        "FROM pipelines WHERE pipeline_id = ?",
        (pipeline_id,),
    ).fetchone()
    if row is None:
        return None

    data = dict(row)
    state_raw = data.get("state_json") or "{}"
    try:
        data["state"] = json.loads(state_raw)
    except json.JSONDecodeError:
        data["state"] = {"_parse_error": "invalid state_json", "_raw": state_raw}
    return data


def _find_latest_pipeline_id(conn: sqlite3.Connection) -> str | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT pipeline_id FROM pipelines ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return str(row["pipeline_id"])


def _load_node_results(conn: sqlite3.Connection, pipeline_id: str) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT pipeline_id, node_id, iteration, status, created_at, updated_at, "
        "deliverable_json, questions_json, evaluation_json "
        "FROM node_results WHERE pipeline_id = ? ORDER BY created_at ASC",
        (pipeline_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def _load_node_runs(conn: sqlite3.Connection, pipeline_id: str) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT run_id, node_id, status, start_time, end_time, deliverable_json, evaluation_json "
        "FROM node_runs WHERE run_id = ? OR run_id LIKE ? ORDER BY start_time ASC",
        (pipeline_id, f"{pipeline_id}%"),
    ).fetchall()
    return [dict(row) for row in rows]


def _collect_log_files(project_root: Path, extra_log: Path | None) -> list[Path]:
    log_files: list[Path] = []

    root_logger = project_root / "logger.log"
    if root_logger.exists():
        log_files.append(root_logger)

    logs_dir = project_root / "logs"
    if logs_dir.exists():
        log_files.extend(sorted(logs_dir.glob("*.log")))

    if extra_log and extra_log.exists() and extra_log not in log_files:
        log_files.append(extra_log)

    seen: set[Path] = set()
    deduped: list[Path] = []
    for path in log_files:
        if path not in seen:
            deduped.append(path)
            seen.add(path)
    return deduped


def _extract_pipeline_log_lines(log_text: str, pipeline_id: str | None) -> list[str]:
    lines = [line for line in log_text.splitlines() if line.strip()]
    if pipeline_id:
        return [line for line in lines if pipeline_id in line]
    return lines


def _analyze_pipeline(
    pipeline: dict[str, Any] | None,
    node_results: list[dict[str, Any]],
    node_runs: list[dict[str, Any]],
    log_lines: list[str],
    registry: RegistrySnapshot,
) -> list[Finding]:
    findings: list[Finding] = []
    state = (pipeline or {}).get("state", {}) if pipeline else {}

    if pipeline is None:
        findings.append(
            Finding(
                severity="high",
                title="数据库中未找到目标流水线",
                detail="请确认 pipeline_id 是否正确，或先运行一次 `start` 命令生成记录。",
            )
        )
        return findings

    if pipeline.get("status") == "completed":
        completed_nodes = state.get("completed_nodes")
        deliverables = state.get("deliverables") or {}
        evaluations = state.get("evaluations") or {}
        if not completed_nodes and not deliverables and not evaluations:
            findings.append(
                Finding(
                    severity="high",
                    title="流水线被标记为 completed，但状态快照几乎为空",
                    detail=(
                        "`pipelines.state_json` 只保留了初始上下文，没有同步 LangGraph 最终状态；"
                        "这会让 CLI/排障无法从数据库还原真实执行结果。"
                    ),
                )
            )

    if not node_results and not node_runs and any("node_execution_failed" in line for line in log_lines):
        findings.append(
            Finding(
                severity="high",
                title="节点执行失败已写入日志，但数据库没有对应节点运行记录",
                detail=(
                    "集成执行路径没有把失败节点写入 `node_results`/`node_runs`，"
                    "导致日志、数据库、CLI 状态三者失真。"
                ),
            )
        )

    if any("no_deliverable_tool_called" in line for line in log_lines):
        findings.append(
            Finding(
                severity="high",
                title="IndependentAgent 未触发 `create_deliverable` 工具",
                detail=(
                    "日志显示各节点返回了文本/消息，但 `ToolResultExtractor` 未提取到任何 `create_deliverable` 调用；"
                    "这意味着代理提示词、工具注册、SDK 工具桥接三者至少有一处断链。"
                ),
            )
        )

    permission_lines = [line for line in log_lines if "WinError 5" in line and ".kimi\\sessions" in line]
    if permission_lines:
        findings.append(
            Finding(
                severity="high",
                title="Kimi 会话目录权限错误阻塞启动",
                detail=(
                    "`ContextValidator` 在创建 SDK Session 时尝试写入 `C:\\Users\\Administrator\\.kimi\\sessions`，"
                    "但当前执行环境无权限，导致验证阶段在任何节点启动前就失败。"
                ),
            )
        )

    if any("Connection error." in line for line in log_lines):
        findings.append(
            Finding(
                severity="medium",
                title="修正会话目录后，下一阻塞点是网络/连接失败",
                detail=(
                    "将 `KIMI_SHARE_DIR` 切到仓库内可写目录后，`WinError 5` 消失，"
                    "随后暴露出真实的 LLM 连接错误。"
                ),
            )
        )

    if any("node_execution_failed" in line for line in log_lines) and pipeline.get("status") == "completed":
        findings.append(
            Finding(
                severity="high",
                title="节点失败后流水线仍可能被最终标记为 completed",
                detail=(
                    "当前图执行层把失败节点包装成普通状态返回，且集成执行器无条件追加 `completed_nodes`，"
                    "最终 `finalize_pipeline_state()` 直接把整体状态置为 `completed`。"
                ),
            )
        )

    if registry.before_import_count == 0 and registry.after_import_count > 0:
        findings.append(
            Finding(
                severity="high",
                title="工具注册依赖导入副作用，但生产执行路径没有显式导入工具包",
                detail=(
                    "运行时验证表明 `ToolRegistry` 在默认导入路径下为空，"
                    "只有显式 `import autoBMAD.docuswarm.tools` 后才出现工具；"
                    "这与 `IndependentAgent` 中“工具已通过 ToolRegistry 注册”的假设不一致。"
                ),
            )
        )

    return findings


def _snapshot_tool_registry() -> RegistrySnapshot:
    from autoBMAD.docuswarm.models.tool_registry import ToolRegistry

    before_count = len(ToolRegistry.get_all())
    import autoBMAD.docuswarm.tools  # noqa: F401

    after = ToolRegistry.get_all()
    return RegistrySnapshot(
        before_import_count=before_count,
        after_import_count=len(after),
        tool_names=[tool.name for tool in after],
    )


def _format_markdown(
    project_root: Path,
    pipeline_id: str | None,
    pipeline: dict[str, Any] | None,
    node_results: list[dict[str, Any]],
    node_runs: list[dict[str, Any]],
    registry: RegistrySnapshot,
    findings: list[Finding],
    log_samples: list[str],
) -> str:
    lines: list[str] = []
    lines.append("# DocuSwarm 离线诊断报告")
    lines.append("")
    lines.append("## 范围")
    lines.append("")
    lines.append(f"- 项目根目录: `{project_root}`")
    lines.append(f"- 目标流水线: `{pipeline_id or 'latest'}`")
    lines.append("")

    lines.append("## 数据库快照")
    lines.append("")
    if pipeline is None:
        lines.append("- 未找到对应流水线记录。")
    else:
        lines.append(f"- pipeline_id: `{pipeline['pipeline_id']}`")
        lines.append(f"- subject: `{pipeline.get('subject')}`")
        lines.append(f"- status: `{pipeline.get('status')}`")
        lines.append(f"- current_node: `{pipeline.get('current_node')}`")
        lines.append(f"- created_at: `{pipeline.get('created_at')}`")
        lines.append(f"- updated_at: `{pipeline.get('updated_at')}`")
        state = pipeline.get("state", {})
        lines.append(f"- state keys: `{sorted(state.keys())}`")
        lines.append(f"- node_results rows: `{len(node_results)}`")
        lines.append(f"- node_runs rows: `{len(node_runs)}`")
    lines.append("")

    lines.append("## 工具注册快照")
    lines.append("")
    lines.append(f"- ToolRegistry before importing tools package: `{registry.before_import_count}`")
    lines.append(f"- ToolRegistry after importing tools package: `{registry.after_import_count}`")
    lines.append(f"- Registered tool names: `{registry.tool_names}`")
    lines.append("")

    lines.append("## 发现")
    lines.append("")
    if not findings:
        lines.append("- 未检测到明显异常。")
    else:
        for finding in findings:
            lines.append(f"- [{finding.severity.upper()}] {finding.title}: {finding.detail}")
    lines.append("")

    lines.append("## 日志样本")
    lines.append("")
    if not log_samples:
        lines.append("- 未找到相关日志样本。")
    else:
        lines.append("```text")
        lines.extend(log_samples[:20])
        lines.append("```")
    lines.append("")

    return "\n".join(lines)


def _format_text(
    pipeline_id: str | None,
    pipeline: dict[str, Any] | None,
    registry: RegistrySnapshot,
    findings: list[Finding],
) -> str:
    lines: list[str] = []
    lines.append(f"Pipeline: {pipeline_id or 'latest'}")
    if pipeline:
        lines.append(
            f"Status={pipeline.get('status')} CurrentNode={pipeline.get('current_node')} Subject={pipeline.get('subject')}"
        )
    lines.append(
        f"ToolRegistry before/after import = {registry.before_import_count}/{registry.after_import_count}"
    )
    lines.append("")
    lines.append("Findings:")
    if not findings:
        lines.append("- none")
    else:
        for finding in findings:
            lines.append(f"- [{finding.severity}] {finding.title}: {finding.detail}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose DocuSwarm pipeline execution from DB and logs.")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--db", default="docuswarm.db", help="SQLite database path")
    parser.add_argument("--pipeline-id", default=None, help="Pipeline ID to inspect (defaults to latest)")
    parser.add_argument("--log", default=None, help="Extra log file to include")
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format",
    )
    parser.add_argument("--output", default=None, help="Optional output file path")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    db_path = (project_root / args.db).resolve() if not Path(args.db).is_absolute() else Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        pipeline_id = args.pipeline_id or _find_latest_pipeline_id(conn)
        pipeline = _load_pipeline(conn, pipeline_id) if pipeline_id else None
        node_results = _load_node_results(conn, pipeline_id) if pipeline_id else []
        node_runs = _load_node_runs(conn, pipeline_id) if pipeline_id else []
    finally:
        conn.close()

    log_files = _collect_log_files(project_root, Path(args.log) if args.log else None)
    log_lines: list[str] = []
    for log_file in log_files:
        scoped = _extract_pipeline_log_lines(_read_text(log_file), pipeline_id)
        log_lines.extend(scoped)

    registry = _snapshot_tool_registry()
    findings = _analyze_pipeline(pipeline, node_results, node_runs, log_lines, registry)

    if args.format == "markdown":
        content = _format_markdown(
            project_root=project_root,
            pipeline_id=pipeline_id,
            pipeline=pipeline,
            node_results=node_results,
            node_runs=node_runs,
            registry=registry,
            findings=findings,
            log_samples=log_lines,
        )
    else:
        content = _format_text(
            pipeline_id=pipeline_id,
            pipeline=pipeline,
            registry=registry,
            findings=findings,
        )

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = project_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
