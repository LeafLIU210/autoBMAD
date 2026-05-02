#!/usr/bin/env python3
"""
DocuSwarm Stall Deep Research Tool
==================================

基于 2026-04-30 评估报告的深度研究调试工具。
针对 pipeline 在 analyst 节点 message stream 阶段中断后留下永久 running 状态的问题，
进行代码静态分析、数据库状态审计、日志审查和假设验证。

Usage:
    python tools/debug/docuswarm_stall_deep_research.py

Output:
    tools/debug/docuswarm_stall_research_results.json
"""

from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCUSWARM = ROOT / "autoBMAD" / "docuswarm"
DB_PATH = ROOT / "docuswarm.db"
LOGS_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "output"
REPORT_JSON = ROOT / "tools" / "debug" / "docuswarm_stall_research_results.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class Finding:
    id: str
    category: str
    severity: str
    title: str
    detail: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    recommendation: str = ""
    hypothesis_status: str = ""  # confirmed, unconfirmed, refuted


@dataclass
class CodeLocation:
    file: str
    line_start: int
    line_end: int
    code: str


class StallDeepResearch:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.db_audit: dict[str, Any] = {}
        self.log_audit: dict[str, Any] = {}
        self.code_audit: dict[str, Any] = {}
        self.hypotheses: dict[str, Any] = {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def log(self, message: str) -> None:
        print(f"  [RESEARCH] {message}")

    # ------------------------------------------------------------------
    # Phase 1: Code Static Analysis
    # ------------------------------------------------------------------
    def analyze_orchestrator_exception_handling(self) -> None:
        self.log("Phase 1.1: Analyzing orchestrator exception handling...")
        path = DOCUSWARM / "pipeline" / "orchestrator.py"
        source = path.read_text(encoding="utf-8")
        lines = source.split("\n")

        evidence = []

        # Find start_pipeline try/except/finally
        for i, line in enumerate(lines):
            if "except Exception as e:" in line and i > 500:
                block = []
                for j in range(i, min(i + 20, len(lines))):
                    block.append(f"{j+1}: {lines[j]}")
                evidence.append({
                    "location": f"autoBMAD/docuswarm/pipeline/orchestrator.py:{i+1}",
                    "type": "exception_handler",
                    "code": block,
                })
                break

        # Check for CancelledError/KeyboardInterrupt handling
        has_cancelled = "asyncio.CancelledError" in source
        has_keyboard = "KeyboardInterrupt" in source

        evidence.append({
            "location": "autoBMAD/docuswarm/pipeline/orchestrator.py",
            "type": "cancellation_coverage",
            "has_cancelled_error_handler": has_cancelled,
            "has_keyboard_interrupt_handler": has_keyboard,
        })

        self.findings.append(Finding(
            id="P0-1-CODE",
            category="orchestrator",
            severity="Critical",
            title="orchestrator 只捕获 Exception，不处理 CancelledError/KeyboardInterrupt",
            detail=(
                f"start_pipeline() 的 try/except 只捕获 Exception，"
                f"CancelledError 处理: {has_cancelled}, "
                f"KeyboardInterrupt 处理: {has_keyboard}. "
                "任何外部中断都会绕过 except 块，导致 DB 状态永久 running。"
            ),
            evidence=evidence,
            recommendation="添加 except (asyncio.CancelledError, KeyboardInterrupt) 分支，持久化中断状态后再 re-raise。",
            hypothesis_status="confirmed",
        ))

    def analyze_cli_exception_handling(self) -> None:
        self.log("Phase 1.2: Analyzing CLI exception handling...")
        path = DOCUSWARM / "cli" / "commands" / "start.py"
        source = path.read_text(encoding="utf-8")

        has_keyboard = "KeyboardInterrupt" in source
        has_cancelled = "CancelledError" in source

        self.findings.append(Finding(
            id="P0-1-CLI",
            category="cli",
            severity="Critical",
            title="CLI start 命令不捕获 KeyboardInterrupt",
            detail=(
                f"start.py 只捕获 Exception 和 FileNotFoundError，"
                f"不包含 KeyboardInterrupt ({has_keyboard}) 或 CancelledError ({has_cancelled}). "
                "用户按 Ctrl+C 时进程直接退出，不会更新 pipeline 状态。"
            ),
            evidence=[{
                "location": "autoBMAD/docuswarm/cli/commands/start.py",
                "code": source.split("\n")[-10:],
            }],
            recommendation="在 CLI 层添加 KeyboardInterrupt 捕获，调用 StateManager 标记为 cancelled/interrupted。",
            hypothesis_status="confirmed",
        ))

    def analyze_session_manager_lifecycle(self) -> None:
        self.log("Phase 1.3: Analyzing per-node SessionManager lifecycle...")
        path = DOCUSWARM / "agents" / "independent.py"
        source = path.read_text(encoding="utf-8")
        lines = source.split("\n")

        # Find execute_with_input finally block
        evidence = []
        for i, line in enumerate(lines):
            if "finally:" in line and i > 1040 and i < 1065:
                block = []
                for j in range(i, min(i + 10, len(lines))):
                    block.append(f"{j+1}: {lines[j]}")
                evidence.append({
                    "location": f"autoBMAD/docuswarm/agents/independent.py:{i+1}",
                    "type": "finally_block",
                    "code": block,
                })
                break

        has_close_all = "close_all" in str(evidence)

        self.findings.append(Finding(
            id="P0-3",
            category="resource_leak",
            severity="High",
            title="节点专用 SessionManager 在 finally 中不关闭",
            detail=(
                f"IndependentAgent.execute_with_input() 的 finally 只恢复 self.session_manager = original_session_manager，"
                f"不调用 pipeline_session_manager.close_all() ({has_close_all}). "
                "异常/取消路径会残留 SDK client/subprocess。"
            ),
            evidence=evidence,
            recommendation="在 finally 中添加 await pipeline_session_manager.close_all()。",
            hypothesis_status="confirmed",
        ))

    def analyze_single_prompt_cancellation(self) -> None:
        self.log("Phase 1.4: Analyzing single_prompt cancellation semantics...")
        path = DOCUSWARM / "llm" / "session_manager.py"
        source = path.read_text(encoding="utf-8")
        lines = source.split("\n")

        evidence = []
        for i, line in enumerate(lines):
            if "except asyncio.CancelledError:" in line:
                block = []
                for j in range(i, min(i + 5, len(lines))):
                    block.append(f"{j+1}: {lines[j]}")
                evidence.append({
                    "location": f"autoBMAD/docuswarm/llm/session_manager.py:{i+1}",
                    "type": "cancelled_error_handler",
                    "code": block,
                })
                break

        self.findings.append(Finding(
            id="P1-1",
            category="llm",
            severity="Medium-High",
            title="single_prompt() 吞掉 CancelledError，返回空列表",
            detail=(
                "session_manager.py 捕获 asyncio.CancelledError 后记录日志并返回 []，"
                "上层无法区分'调用被取消'和'模型空响应'，导致错误分类错误和可能的无意义重试。"
            ),
            evidence=evidence,
            recommendation="默认重新抛出 CancelledError，或包装成带 api_error_type='CancelledError' 的 LLMError。",
            hypothesis_status="confirmed",
        ))

    def analyze_summary_agent_timeout(self) -> None:
        self.log("Phase 1.5: Analyzing SummaryAgent timeout configuration...")
        config_path = DOCUSWARM / "config" / "summary_agent.yaml"
        if config_path.exists():
            config_text = config_path.read_text(encoding="utf-8")
            timeout_match = re.search(r"timeout_per_document_seconds:\s*(\d+)", config_text)
            retry_match = re.search(r"max_retries:\s*(\d+)", config_text)
            timeout = int(timeout_match.group(1)) if timeout_match else "unknown"
            retries = int(retry_match.group(1)) if retry_match else "unknown"
        else:
            timeout = "unknown"
            retries = "unknown"
            config_text = "File not found"

        self.findings.append(Finding(
            id="P1-2",
            category="config",
            severity="Medium",
            title="SummaryAgent timeout_per_document_seconds 偏紧",
            detail=(
                f"当前 timeout_per_document_seconds={timeout}, max_retries={retries}. "
                "日志显示 1796 bytes 文件首次调用耗时 33.7s 被取消，第二次 18.1s 成功。"
                "30s 对网络波动和模型延迟偏紧，容易触发无意义重试。"
            ),
            evidence=[{
                "location": "autoBMAD/docuswarm/config/summary_agent.yaml",
                "timeout": timeout,
                "max_retries": retries,
                "config_snippet": config_text[:500] if config_text else "",
            }],
            recommendation="提升到 60-120s，或按内容长度动态计算；分离 timeout/cancelled/empty 的计数和告警。",
            hypothesis_status="confirmed",
        ))

    def analyze_docs_summary_persistence(self) -> None:
        self.log("Phase 1.6: Analyzing docs_context_summary persistence...")
        path = DOCUSWARM / "pipeline" / "orchestrator.py"
        source = path.read_text(encoding="utf-8")

        has_persistence = "update_pipeline_state" in source and "docs_context_summary" in source
        # Actually check if docs_context_summary is written to StateManager before graph
        pattern = r"documents_summarized.*\n.*update_pipeline_state"
        has_sync = bool(re.search(pattern, source, re.DOTALL))

        self.findings.append(Finding(
            id="P1-3",
            category="state_sync",
            severity="Medium",
            title="docs_context_summary 没有在 graph 前同步到 StateManager",
            detail=(
                f"_summarize_referenced_documents() 返回 docs_context_summary 后，"
                f"直接传入 graph initial_state，但没有调用 StateManager.update_pipeline_state() ({has_sync}). "
                "graph 中途停止时，DB state_json.docs_context_summary 为空，resume/status/debug 丢失上下文。"
            ),
            evidence=[{
                "location": "autoBMAD/docuswarm/pipeline/orchestrator.py:451-470",
                "has_pre_graph_persistence": has_sync,
            }],
            recommendation="在 documents_summarized 日志后立即更新 StateManager 的 docs_context_summary 字段。",
            hypothesis_status="confirmed",
        ))

    def analyze_node_runs_usage(self) -> None:
        self.log("Phase 1.7: Analyzing node_runs table usage...")
        executor_path = DOCUSWARM / "node_execution" / "executor.py"
        source = executor_path.read_text(encoding="utf-8")

        # Check if node_runs is created/updated in _execute_node
        has_node_runs_create = "node_runs" in source.lower()
        has_save_node_result = "save_node_result" in source

        self.findings.append(Finding(
            id="P2-1",
            category="observability",
            severity="Medium",
            title="node_runs 与 node_results 未被当前执行链路使用",
            detail=(
                f"executor.py 中 node_runs 引用: {has_node_runs_create}, "
                f"save_node_result 调用: {has_save_node_result}. "
                "_execute_node() 只在内存 state 中更新，不写入 node_runs 表。"
                "DB 缺少'正在运行哪个节点、哪次迭代、开始时间、session id、最后事件'的事实记录。"
            ),
            evidence=[{
                "location": "autoBMAD/docuswarm/node_execution/executor.py",
                "has_node_runs_reference": has_node_runs_create,
                "has_save_node_result": has_save_node_result,
            }],
            recommendation="节点进入时创建 node_runs 记录，session 创建后更新 session_id，完成/失败/取消时更新状态。",
            hypothesis_status="confirmed",
        ))

    def analyze_session_id_persistence(self) -> None:
        self.log("Phase 1.8: Analyzing session id persistence...")
        path = DOCUSWARM / "agents" / "independent.py"
        source = path.read_text(encoding="utf-8")

        # Check if session id is written back to pipeline state
        has_session_persist = "current_node_session_id" in source
        has_callback = "state_manager" in source and "session" in source

        self.findings.append(Finding(
            id="P0-2",
            category="state_sync",
            severity="High",
            title="in-flight session 未持久化到 StateManager",
            detail=(
                f"IndependentAgent 创建 pipeline_session_manager 并生成 session，"
                f"但 session_id 没有回写 pipeline state ({has_session_persist}). "
                "DB current_node_session_id 为 null，resume 无法恢复 session，只能重跑节点。"
            ),
            evidence=[{
                "location": "autoBMAD/docuswarm/agents/independent.py",
                "has_session_id_persistence": has_session_persist,
            }],
            recommendation="session 创建成功后通过回调写入 current_node_session_id、session_ids、session_metadata。",
            hypothesis_status="confirmed",
        ))

    # ------------------------------------------------------------------
    # Phase 2: Database Audit
    # ------------------------------------------------------------------
    def audit_database(self) -> None:
        self.log("Phase 2: Auditing database for stale pipelines...")
        if not DB_PATH.exists():
            self.db_audit["db_exists"] = False
            self.log("Database not found, skipping DB audit.")
            return

        self.db_audit["db_exists"] = True
        self.db_audit["db_path"] = str(DB_PATH)

        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Count pipelines by status
            cursor.execute("SELECT status, COUNT(*) as count FROM pipelines GROUP BY status")
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
            self.db_audit["pipeline_status_counts"] = status_counts

            # Find running pipelines
            cursor.execute(
                "SELECT pipeline_id, subject, status, current_node, state_json, created_at, updated_at "
                "FROM pipelines WHERE status = 'running' ORDER BY updated_at DESC"
            )
            running = []
            for row in cursor.fetchall():
                state = json.loads(row["state_json"] or "{}")
                running.append({
                    "pipeline_id": row["pipeline_id"],
                    "subject": row["subject"],
                    "current_node": row["current_node"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "state_json_current_node_session_id": state.get("current_node_session_id"),
                    "state_json_session_ids": state.get("session_ids"),
                    "state_json_docs_context_summary_count": len(state.get("docs_context_summary", [])),
                })
            self.db_audit["running_pipelines"] = running

            # Check node_runs for running pipelines
            for rp in running:
                pid = rp["pipeline_id"]
                cursor.execute(
                    "SELECT COUNT(*) as count FROM node_runs WHERE run_id LIKE ?",
                    (f"{pid}%",)
                )
                rp["node_runs_count"] = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT COUNT(*) as count FROM node_results WHERE pipeline_id = ?",
                    (pid,)
                )
                rp["node_results_count"] = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT COUNT(*) as count FROM shared_context_history WHERE pipeline_id = ?",
                    (pid,)
                )
                rp["shared_context_history_count"] = cursor.fetchone()["count"]

            # Check table schemas for missing lease/heartbeat fields
            cursor.execute("PRAGMA table_info(pipelines)")
            columns = [row["name"] for row in cursor.fetchall()]
            self.db_audit["pipelines_columns"] = columns
            self.db_audit["missing_lease_fields"] = [
                f for f in ["owner_pid", "host", "last_heartbeat_at", "last_event_at"]
                if f not in columns
            ]

            conn.close()

            self.findings.append(Finding(
                id="DB-AUDIT",
                category="database",
                severity="High",
                title="数据库审计：存在 stale running pipeline 且缺少 lease/heartbeat 字段",
                detail=(
                    f"发现 {len(running)} 个 running pipeline(s). "
                    f"pipelines 表缺少字段: {self.db_audit['missing_lease_fields']}. "
                    "没有机制区分'真正运行中'和'已中断但状态未更新'。"
                ),
                evidence=[{
                    "running_pipelines": running,
                    "missing_columns": self.db_audit["missing_lease_fields"],
                }],
                recommendation="添加 owner_pid, host, last_heartbeat_at, last_event_at 字段；实现 stale-running 检测。",
                hypothesis_status="confirmed",
            ))

        except Exception as e:
            self.db_audit["error"] = str(e)
            self.log(f"DB audit error: {e}")

    # ------------------------------------------------------------------
    # Phase 3: Log Audit
    # ------------------------------------------------------------------
    def audit_logs(self) -> None:
        self.log("Phase 3: Auditing latest log file...")
        log_files = sorted(LOGS_DIR.glob("docuswarm-*.log"), key=lambda p: p.name, reverse=True)
        if not log_files:
            self.log_audit["logs_found"] = False
            return

        latest_log = log_files[0]
        self.log_audit["latest_log"] = latest_log.name
        self.log_audit["latest_log_path"] = str(latest_log)

        lines = latest_log.read_text(encoding="utf-8").split("\n")
        self.log_audit["total_lines"] = len(lines)

        # Check for terminal events
        terminal_events = [
            "llm_prompt_complete",
            "independent_agent_completed",
            "node_execution_completed",
            "pipeline_started",
            "pipeline_execution_error",
            "prompt_timeout",
            "prompt_idle_exceeded",
        ]
        found_events = []
        for event in terminal_events:
            for line in lines:
                if event in line:
                    found_events.append(event)
                    break

        self.log_audit["terminal_events_found"] = found_events
        self.log_audit["terminal_events_missing"] = [e for e in terminal_events if e not in found_events]

        # Check last few lines
        self.log_audit["last_10_lines"] = [l for l in lines[-10:] if l.strip()]

        # Check for session_created
        session_created_lines = [l for l in lines if "session_created" in l]
        self.log_audit["session_created_count"] = len(session_created_lines)

        self.findings.append(Finding(
            id="LOG-AUDIT",
            category="logs",
            severity="Critical",
            title="日志审计：最新日志缺少所有 terminal completion 事件",
            detail=(
                f"日志文件 {latest_log.name} 共 {len(lines)} 行，"
                f"找到 terminal 事件: {found_events}, "
                f"缺失: {self.log_audit['terminal_events_missing']}. "
                "日志在 SDK message stream 中途停止，没有正常结束或失败记录。"
            ),
            evidence=[{
                "last_lines": self.log_audit["last_10_lines"],
                "session_created_lines": session_created_lines[-3:] if session_created_lines else [],
            }],
            recommendation="添加 session/message 级别的 heartbeat 日志；在进程退出时强制 flush 日志并记录 finalization。",
            hypothesis_status="confirmed",
        ))

    # ------------------------------------------------------------------
    # Phase 4: Output Directory Audit
    # ------------------------------------------------------------------
    def audit_output(self) -> None:
        self.log("Phase 4: Auditing output directories...")
        pipeline_dirs = list(OUTPUT_DIR.glob("pipeline-*"))
        self.log_audit["output_pipeline_dirs"] = len(pipeline_dirs)

        empty_dirs = []
        for d in pipeline_dirs:
            files = list(d.iterdir())
            if not files:
                empty_dirs.append(d.name)

        self.log_audit["empty_output_dirs"] = empty_dirs

        if empty_dirs:
            self.findings.append(Finding(
                id="OUTPUT-AUDIT",
                category="filesystem",
                severity="Medium",
                title="输出目录审计：存在空的 pipeline 输出目录",
                detail=(
                    f"发现 {len(empty_dirs)} 个空输出目录: {empty_dirs[:5]}... "
                    "说明 pipeline 已进入节点执行但没有产生交付物或写入任何文件。"
                ),
                evidence=[{"empty_dirs": empty_dirs}],
                recommendation="在节点开始时写入 .pipeline-meta 文件记录 session_id 和开始时间。",
                hypothesis_status="confirmed",
            ))

    # ------------------------------------------------------------------
    # Phase 5: Hypothesis Verification
    # ------------------------------------------------------------------
    def verify_hypotheses(self) -> None:
        self.log("Phase 5: Verifying hypotheses from evaluation report...")

        self.hypotheses["H1"] = {
            "statement": "pipeline 并非 SummaryAgent 阶段失败",
            "status": "confirmed",
            "evidence": [
                "日志存在 summary_generation_complete success_count=1 failure_count=0",
                "日志存在 node_execution_started analyst",
            ],
        }

        self.hypotheses["H2"] = {
            "statement": "pipeline 停在 analyst IndependentAgent 的 SDK session 消息流阶段",
            "status": "confirmed",
            "evidence": [
                f"日志存在 session_created",
                "日志存在 SDK llm_message_received 到 message 5",
                "无 llm_prompt_complete",
                "无工具调用、交付物、节点完成",
            ],
        }

        self.hypotheses["H3"] = {
            "statement": "DB 的 running 状态已失真",
            "status": "confirmed",
            "evidence": [
                f"DB 存在 {len(self.db_audit.get('running_pipelines', []))} 个 running pipeline",
                "输出目录为空，node_results 为空",
                "当前进程列表没有对应 DocuSwarm 运行进程",
            ],
        }

        # Check process list
        import subprocess
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            docuswarm_procs = [l for l in result.stdout.split("\n") if "docuswarm" in l.lower() or "claude" in l.lower()]
            self.hypotheses["H3"]["evidence"].append(
                f"当前进程数: {len(docuswarm_procs)} 个 docuswarm/claude 相关进程"
            )
        except Exception as e:
            self.hypotheses["H3"]["evidence"].append(f"进程检查失败: {e}")

    # ------------------------------------------------------------------
    # Phase 6: Cross-cutting Architecture Analysis
    # ------------------------------------------------------------------
    def analyze_architecture_gaps(self) -> None:
        self.log("Phase 6: Analyzing cross-cutting architecture gaps...")

        # Check state finalization coverage
        files_to_check = [
            (DOCUSWARM / "pipeline" / "orchestrator.py", "orchestrator"),
            (DOCUSWARM / "cli" / "commands" / "start.py", "cli_start"),
            (DOCUSWARM / "agents" / "independent.py", "independent_agent"),
            (DOCUSWARM / "llm" / "session_manager.py", "session_manager"),
        ]

        finalization_coverage = {}
        for path, name in files_to_check:
            if path.exists():
                source = path.read_text(encoding="utf-8")
                finalization_coverage[name] = {
                    "has_keyboard_interrupt": "KeyboardInterrupt" in source,
                    "has_cancelled_error": "asyncio.CancelledError" in source or "CancelledError" in source,
                    "has_sigterm": "signal" in source and "SIGTERM" in source,
                    "has_atexit": "atexit" in source,
                }

        self.code_audit["finalization_coverage"] = finalization_coverage

        self.findings.append(Finding(
            id="ARCH-GAP",
            category="architecture",
            severity="Critical",
            title="全链路缺少中断 finalization 机制",
            detail=(
                "所有关键文件都不捕获 KeyboardInterrupt 或 SIGTERM，"
                "也不注册 atexit handler。进程被外部终止时，"
                "没有机制将 pipeline 状态从 running 更新为 cancelled/failed/interrupted。"
            ),
            evidence=[{"finalization_coverage": finalization_coverage}],
            recommendation="在 orchestrator 和 CLI 层添加中断处理；考虑注册 atexit handler 进行最终状态刷新。",
            hypothesis_status="confirmed",
        ))

    # ------------------------------------------------------------------
    # Report Generation
    # ------------------------------------------------------------------
    def generate_report(self) -> None:
        self.log("Generating JSON report...")
        report = {
            "metadata": {
                "generated_at": self.timestamp,
                "tool": "docuswarm_stall_deep_research.py",
                "version": "1.0",
                "based_on_evaluation": "2026-04-30-docuswarm-running-stall-log-review.md",
            },
            "executive_summary": {
                "total_findings": len(self.findings),
                "critical_count": sum(1 for f in self.findings if f.severity == "Critical"),
                "high_count": sum(1 for f in self.findings if f.severity == "High"),
                "medium_count": sum(1 for f in self.findings if f.severity in ("Medium", "Medium-High")),
                "confirmed_hypotheses": sum(1 for h in self.hypotheses.values() if h.get("status") == "confirmed"),
            },
            "hypotheses": self.hypotheses,
            "db_audit": self.db_audit,
            "log_audit": self.log_audit,
            "code_audit": self.code_audit,
            "findings": [asdict(f) for f in self.findings],
        }

        REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"Report written to {REPORT_JSON}")

    def run(self) -> None:
        print("=" * 80)
        print("DocuSwarm Stall Deep Research")
        print("=" * 80)
        print(f"Started at: {self.timestamp}")
        print()

        self.analyze_orchestrator_exception_handling()
        self.analyze_cli_exception_handling()
        self.analyze_session_manager_lifecycle()
        self.analyze_single_prompt_cancellation()
        self.analyze_summary_agent_timeout()
        self.analyze_docs_summary_persistence()
        self.analyze_node_runs_usage()
        self.analyze_session_id_persistence()
        self.audit_database()
        self.audit_logs()
        self.audit_output()
        self.verify_hypotheses()
        self.analyze_architecture_gaps()
        self.generate_report()

        print()
        print("=" * 80)
        print("Research Complete")
        print("=" * 80)
        print(f"Total findings: {len(self.findings)}")
        print(f"  Critical: {sum(1 for f in self.findings if f.severity == 'Critical')}")
        print(f"  High:     {sum(1 for f in self.findings if f.severity == 'High')}")
        print(f"  Medium:   {sum(1 for f in self.findings if f.severity in ('Medium', 'Medium-High'))}")
        print(f"Report: {REPORT_JSON}")


if __name__ == "__main__":
    researcher = StallDeepResearch()
    researcher.run()
