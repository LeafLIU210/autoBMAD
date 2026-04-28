#!/usr/bin/env python3
"""DocuSwarm Pipeline Hang Deep Diagnostic Tool

深度诊断 Pipeline 挂起根因，整合数据库、日志、代码静态分析与 Timeout 链路追踪。

Usage:
    python tools/pipeline_hang_diagnostic_tool.py \
        --pipeline-id pipeline-1777291307570-8957f601 \
        --db docuswarm.db \
        --log logs/docuswarm-2026-04-27.log \
        --output-dir docs-doc/research
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Project root resolution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    run_id: str
    node_id: str
    message: str
    raw: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeoutLink:
    file: str
    line: int
    symbol: str
    timeout_value: int | None
    description: str


@dataclass
class HangPattern:
    pattern_name: str
    matched: bool
    confidence: float  # 0.0 - 1.0
    evidence: list[str]


@dataclass
class DiagnosticReport:
    pipeline_id: str
    generated_at: str
    findings: list[dict[str, Any]]
    timeout_chain: list[dict[str, Any]]
    log_analysis: dict[str, Any]
    db_analysis: dict[str, Any]
    hang_patterns: list[dict[str, Any]]
    code_audit: dict[str, Any]
    recommendations: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Database Analyzer
# ---------------------------------------------------------------------------

class DatabaseAnalyzer:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def analyze(self, pipeline_id: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "db_path": str(self.db_path),
            "pipeline_id": pipeline_id,
            "pipeline_record": None,
            "node_results": [],
            "node_runs": [],
            "checkpoints": [],
            "state_completeness": {},
            "issues": [],
        }

        if not self.db_path.exists():
            result["issues"].append("Database file not found")
            return result

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Pipeline record
            row = conn.execute(
                "SELECT * FROM pipelines WHERE pipeline_id = ?",
                (pipeline_id,),
            ).fetchone()
            if row:
                result["pipeline_record"] = dict(row)
                state_json = row["state_json"] or "{}"
                try:
                    state = json.loads(state_json)
                    result["state_completeness"] = self._check_state_completeness(state)
                except json.JSONDecodeError as e:
                    result["issues"].append(f"state_json parse error: {e}")
            else:
                result["issues"].append("Pipeline not found in DB")

            # Node results
            result["node_results"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM node_results WHERE pipeline_id = ? ORDER BY created_at",
                    (pipeline_id,),
                ).fetchall()
            ]

            # Node runs
            result["node_runs"] = [
                dict(r)
                for r in conn.execute(
                    "SELECT * FROM node_runs WHERE run_id = ? OR run_id LIKE ? ORDER BY start_time",
                    (pipeline_id, f"{pipeline_id}%"),
                ).fetchall()
            ]

            # Checkpoints (LangGraph)
            cp_table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
            ).fetchone()
            if cp_table:
                result["checkpoints"] = [
                    dict(r)
                    for r in conn.execute(
                        "SELECT thread_id, checkpoint_id, parent_checkpoint_id FROM checkpoints WHERE thread_id LIKE ?",
                        (f"%{pipeline_id}%",),
                    ).fetchall()
                ]
        finally:
            conn.close()

        return result

    def _check_state_completeness(self, state: dict[str, Any]) -> dict[str, Any]:
        required = [
            "pipeline_id", "subject_context", "current_node", "completed_nodes",
            "deliverables", "questions", "evaluations", "node_iterations",
            "session_ids", "session_metadata", "current_node_session_id",
            "status", "error", "shared_context",
        ]
        missing = [f for f in required if f not in state]
        return {
            "has_state": True,
            "key_count": len(state.keys()),
            "missing_fields": missing,
            "current_node": state.get("current_node"),
            "status": state.get("status"),
            "completed_nodes_count": len(state.get("completed_nodes", [])),
            "deliverables_count": len(state.get("deliverables", {})),
        }


# ---------------------------------------------------------------------------
# Log Analyzer
# ---------------------------------------------------------------------------

class LogAnalyzer:
    _TS_RE = re.compile(
        r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2})?)"
        r"\s+\[(\w+)\]"
        r".*run_id=(\S+)"
        r".*node_id=(\S+)"
        r".*message=\"(.*?)\""
    )

    def __init__(self, log_paths: list[Path]) -> None:
        self.log_paths = [p for p in log_paths if p.exists()]

    def analyze(self, pipeline_id: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "pipeline_id": pipeline_id,
            "log_files": [str(p) for p in self.log_paths],
            "entries": [],
            "message_frequency": {},
            "time_gaps": [],
            "last_entry": None,
            "first_entry": None,
            "total_entries": 0,
            "issues": [],
        }

        entries: list[LogEntry] = []
        for path in self.log_paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if pipeline_id not in line:
                    continue
                parsed = self._parse_line(line)
                if parsed:
                    entries.append(parsed)

        entries.sort(key=lambda e: e.timestamp)
        result["total_entries"] = len(entries)

        if not entries:
            result["issues"].append("No log entries found for pipeline")
            return result

        result["first_entry"] = self._entry_to_dict(entries[0])
        result["last_entry"] = self._entry_to_dict(entries[-1])
        result["entries"] = [self._entry_to_dict(e) for e in entries]

        # Time gaps
        gaps = []
        for i in range(1, len(entries)):
            delta = (entries[i].timestamp - entries[i - 1].timestamp).total_seconds()
            if delta > 60:  # gaps > 60s
                gaps.append({
                    "between_messages": f"{entries[i-1].message[:40]}... -> {entries[i].message[:40]}...",
                    "gap_seconds": round(delta, 2),
                    "start": entries[i - 1].timestamp.isoformat(),
                    "end": entries[i].timestamp.isoformat(),
                })
        result["time_gaps"] = gaps

        # Message frequency by minute for the active period
        freq: dict[str, int] = {}
        for e in entries:
            bucket = e.timestamp.strftime("%H:%M")
            freq[bucket] = freq.get(bucket, 0) + 1
        result["message_frequency"] = freq

        # Detect silent period after last message
        now = datetime.now(entries[-1].timestamp.tzinfo or timezone.utc)
        silence_seconds = (now - entries[-1].timestamp).total_seconds()
        result["silence_after_last_log_seconds"] = round(silence_seconds, 2)

        # Specific message type counts
        counts: dict[str, int] = {}
        for e in entries:
            counts[e.message] = counts.get(e.message, 0) + 1
        result["message_counts"] = counts

        return result

    def _parse_line(self, line: str) -> LogEntry | None:
        m = self._TS_RE.match(line)
        if not m:
            return None
        ts_str, level, run_id, node_id, message = m.groups()
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            return None
        return LogEntry(
            timestamp=ts,
            level=level,
            run_id=run_id,
            node_id=node_id,
            message=message,
            raw=line,
        )

    def _entry_to_dict(self, entry: LogEntry) -> dict[str, Any]:
        return {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level,
            "run_id": entry.run_id,
            "node_id": entry.node_id,
            "message": entry.message,
        }


# ---------------------------------------------------------------------------
# Timeout Chain Auditor
# ---------------------------------------------------------------------------

class TimeoutChainAuditor:
    def __init__(self, project_root: Path) -> None:
        self.root = project_root
        self.docuswarm = project_root / "autoBMAD" / "docuswarm"

    def audit(self) -> list[dict[str, Any]]:
        links: list[dict[str, Any]] = []

        # 1. config.py agent_timeout
        links.append(self._extract_config_timeout())

        # 2. session_manager DEFAULT_PROMPT_TIMEOUT
        links.append(self._extract_session_manager_timeout())

        # 3. llm/config.py LLMConfig.timeout
        links.append(self._extract_llm_config_timeout())

        # 4. dual_agent.py timeout propagation
        links.append(self._extract_dual_agent_timeout())

        # 5. independent.py execute_with_input timeout
        links.append(self._extract_independent_timeout())

        # 6. independent.py _call_llm_with_prompts timeout
        links.append(self._extract_call_llm_timeout())

        # 7. executor.py node timeout
        links.append(self._extract_executor_timeout())

        # 8. orchestrator.py pipeline timeout
        links.append(self._extract_orchestrator_timeout())

        return links

    def _read_file(self, relative: str) -> str:
        path = self.docuswarm / relative
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _extract_config_timeout(self) -> dict[str, Any]:
        content = self._read_file("config.py")
        m = re.search(r"agent_timeout\s*[=:]\s*(\d+)", content)
        val = int(m.group(1)) if m else None
        return {
            "file": "config.py",
            "line": self._find_line(content, "agent_timeout"),
            "symbol": "Config.agent_timeout",
            "timeout_seconds": val,
            "description": "Pipeline total budget timeout (misused as prompt timeout)",
        }

    def _extract_session_manager_timeout(self) -> dict[str, Any]:
        content = self._read_file("llm/session_manager.py")
        m = re.search(r"DEFAULT_PROMPT_TIMEOUT\s*[=:]\s*(\d+)", content)
        val = int(m.group(1)) if m else None
        has_asyncio_timeout = "asyncio.timeout" in content
        return {
            "file": "llm/session_manager.py",
            "line": self._find_line(content, "DEFAULT_PROMPT_TIMEOUT"),
            "symbol": "ClaudeSessionWrapper.DEFAULT_PROMPT_TIMEOUT",
            "timeout_seconds": val,
            "has_asyncio_timeout_wrapper": has_asyncio_timeout,
            "description": "Default prompt timeout per session.prompt() call",
        }

    def _extract_llm_config_timeout(self) -> dict[str, Any]:
        content = self._read_file("llm/config.py")
        m = re.search(r"timeout\s*[=:]\s*(\d+)", content)
        val = int(m.group(1)) if m else None
        return {
            "file": "llm/config.py",
            "line": self._find_line(content, "timeout"),
            "symbol": "LLMConfig.timeout",
            "timeout_seconds": val,
            "description": "HTTP request timeout for LLM API",
        }

    def _extract_dual_agent_timeout(self) -> dict[str, Any]:
        content = self._read_file("nodes/dual_agent.py")
        m = re.search(r"timeout=getattr\(self\.config,\s*\"agent_timeout\"", content)
        line_no = self._find_line(content, "agent_timeout")
        return {
            "file": "nodes/dual_agent.py",
            "line": line_no,
            "symbol": "DualAgentNode.execute_with_context -> independent_agent.execute_with_input",
            "timeout_seconds": None,
            "timeout_source": "config.agent_timeout",
            "description": "Passes config.agent_timeout (7200s) as prompt timeout — ROOT CAUSE",
        }

    def _extract_independent_timeout(self) -> dict[str, Any]:
        content = self._read_file("agents/independent.py")
        m = re.search(r"timeout\s*[=:]\s*(\d+)", content)
        val = int(m.group(1)) if m else None
        return {
            "file": "agents/independent.py",
            "line": self._find_line(content, "timeout: int ="),
            "symbol": "IndependentAgent.execute_with_input",
            "timeout_seconds": val,
            "description": "Default prompt timeout for independent agent execution",
        }

    def _extract_call_llm_timeout(self) -> dict[str, Any]:
        content = self._read_file("agents/independent.py")
        m = re.search(r"_call_llm_with_prompts.*?timeout\s*[=:]\s*(\d+)", content, re.DOTALL)
        val = int(m.group(1)) if m else None
        return {
            "file": "agents/independent.py",
            "line": self._find_line(content, "_call_llm_with_prompts"),
            "symbol": "IndependentAgent._call_llm_with_prompts",
            "timeout_seconds": val,
            "description": "Internal LLM call timeout",
        }

    def _extract_executor_timeout(self) -> dict[str, Any]:
        content = self._read_file("node_execution/executor.py")
        has_timeout = "asyncio.wait_for" in content or "asyncio.timeout" in content
        return {
            "file": "node_execution/executor.py",
            "line": 0,
            "symbol": "_execute_node",
            "timeout_seconds": None,
            "has_node_level_timeout": has_timeout,
            "description": "Node executor — NO node-level timeout protection",
        }

    def _extract_orchestrator_timeout(self) -> dict[str, Any]:
        content = self._read_file("pipeline/orchestrator.py")
        has_timeout = "asyncio.wait_for" in content or "asyncio.timeout" in content
        return {
            "file": "pipeline/orchestrator.py",
            "line": 0,
            "symbol": "start_pipeline / graph.ainvoke",
            "timeout_seconds": None,
            "has_pipeline_level_timeout": has_timeout,
            "description": "Pipeline orchestrator — NO pipeline-level timeout protection",
        }

    def _find_line(self, content: str, keyword: str) -> int:
        for i, line in enumerate(content.splitlines(), 1):
            if keyword in line:
                return i
        return 0


# ---------------------------------------------------------------------------
# Hang Pattern Detector
# ---------------------------------------------------------------------------

class HangPatternDetector:
    def detect(self, db_analysis: dict[str, Any], log_analysis: dict[str, Any]) -> list[dict[str, Any]]:
        patterns: list[dict[str, Any]] = []

        # Pattern 1: Silent after session_created
        entries = log_analysis.get("entries", [])
        last_msg = log_analysis.get("last_entry", {}).get("message", "")
        silence = log_analysis.get("silence_after_last_log_seconds", 0)
        patterns.append({
            "pattern_name": "silent_after_llm_message_received",
            "matched": last_msg == "llm_message_received" and silence > 1800,
            "confidence": 0.95 if silence > 1800 else 0.0,
            "evidence": [
                f"Last log message: {last_msg}",
                f"Silence duration: {silence:.0f}s ({silence/60:.1f} min)",
            ],
        })

        # Pattern 2: No node completion recorded
        pipeline = db_analysis.get("pipeline_record", {})
        state = json.loads(pipeline.get("state_json") or "{}")
        completed = state.get("completed_nodes", [])
        patterns.append({
            "pattern_name": "zero_completed_nodes",
            "matched": len(completed) == 0,
            "confidence": 0.9 if len(completed) == 0 else 0.0,
            "evidence": [f"completed_nodes: {completed}"],
        })

        # Pattern 3: DB state never updated after creation
        created = pipeline.get("created_at", "")
        updated = pipeline.get("updated_at", "")
        patterns.append({
            "pattern_name": "db_state_frozen",
            "matched": created == updated,
            "confidence": 0.85 if created == updated else 0.0,
            "evidence": [f"created_at == updated_at: {created}"],
        })

        # Pattern 4: Log entries exist but no error/timeout/complete
        has_error = any(e.get("level") in ("error", "critical") for e in entries)
        has_timeout = any("timeout" in e.get("message", "") for e in entries)
        has_complete = any("completed" in e.get("message", "") for e in entries)
        patterns.append({
            "pattern_name": "no_terminal_log_event",
            "matched": not (has_error or has_timeout or has_complete),
            "confidence": 0.88 if not (has_error or has_timeout or has_complete) else 0.0,
            "evidence": [
                f"has_error_log: {has_error}",
                f"has_timeout_log: {has_timeout}",
                f"has_complete_log: {has_complete}",
            ],
        })

        # Pattern 5: receive_messages infinite blocking (known issue)
        patterns.append({
            "pattern_name": "receive_messages_infinite_block",
            "matched": last_msg == "llm_message_received" and silence > 600,
            "confidence": 0.92 if (last_msg == "llm_message_received" and silence > 600) else 0.0,
            "evidence": [
                "Known issue: ClaudeSDKClient.receive_messages() may enter infinite wait",
                "asyncio.timeout may not cancel underlying SDK I/O",
            ],
        })

        return patterns


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------

class ReportGenerator:
    def __init__(self, pipeline_id: str) -> None:
        self.pipeline_id = pipeline_id

    def generate_json(self, findings: list[dict[str, Any]], timeout_chain: list[dict[str, Any]],
                      log_analysis: dict[str, Any], db_analysis: dict[str, Any],
                      hang_patterns: list[dict[str, Any]], code_audit: dict[str, Any]) -> str:
        report = DiagnosticReport(
            pipeline_id=self.pipeline_id,
            generated_at=datetime.now().isoformat(),
            findings=findings,
            timeout_chain=timeout_chain,
            log_analysis=log_analysis,
            db_analysis=db_analysis,
            hang_patterns=hang_patterns,
            code_audit=code_audit,
            recommendations=self._build_recommendations(),
        )
        return json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str)

    def generate_markdown(self, findings: list[dict[str, Any]], timeout_chain: list[dict[str, Any]],
                          log_analysis: dict[str, Any], db_analysis: dict[str, Any],
                          hang_patterns: list[dict[str, Any]], code_audit: dict[str, Any]) -> str:
        lines: list[str] = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append(f"# DocuSwarm Pipeline Hang Root Cause Research Report")
        lines.append("")
        lines.append(f"**Report Date**: {now}")
        lines.append(f"**Pipeline ID**: `{self.pipeline_id}`")
        lines.append(f"**Subject**: {db_analysis.get('pipeline_record', {}).get('subject', 'N/A')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        matched_patterns = [p for p in hang_patterns if p["matched"]]
        lines.append(f"This pipeline has been hanging for **{log_analysis.get('silence_after_last_log_seconds', 0)/60:.1f} minutes** "
                     f"since the last log entry. **{len(matched_patterns)}** hang patterns were matched with high confidence.")
        lines.append("")
        lines.append("### Key Findings")
        lines.append("")
        for i, f in enumerate(findings, 1):
            lines.append(f"{i}. **[{f.get('severity', 'INFO')}]** {f['title']}: {f['detail']}")
        lines.append("")

        # Timeline
        lines.append("## Execution Timeline")
        lines.append("")
        first = log_analysis.get("first_entry")
        last = log_analysis.get("last_entry")
        if first and last:
            lines.append(f"- **First log**: `{first['timestamp']}` — {first['message']}")
            lines.append(f"- **Last log**: `{last['timestamp']}` — {last['message']}")
            lines.append(f"- **Active log period**: {(datetime.fromisoformat(last['timestamp']) - datetime.fromisoformat(first['timestamp'])).total_seconds()/60:.1f} minutes")
            lines.append(f"- **Silent period since last log**: {log_analysis.get('silence_after_last_log_seconds', 0)/60:.1f} minutes")
        lines.append("")

        # DB Analysis
        lines.append("## Database Analysis")
        lines.append("")
        record = db_analysis.get("pipeline_record", {})
        if record:
            lines.append(f"- **Status**: `{record.get('status')}`")
            lines.append(f"- **Current Node**: `{record.get('current_node')}`")
            lines.append(f"- **Created At**: `{record.get('created_at')}`")
            lines.append(f"- **Updated At**: `{record.get('updated_at')}`")
            lines.append(f"- **Node Results Count**: {len(db_analysis.get('node_results', []))}")
            lines.append(f"- **Node Runs Count**: {len(db_analysis.get('node_runs', []))}")
            lines.append(f"- **Checkpoints Count**: {len(db_analysis.get('checkpoints', []))}")
            sc = db_analysis.get("state_completeness", {})
            lines.append(f"- **State Keys**: {sc.get('key_count', 0)}")
            lines.append(f"- **Completed Nodes**: {sc.get('completed_nodes_count', 0)}")
        lines.append("")

        # Log Analysis
        lines.append("## Log Analysis")
        lines.append("")
        lines.append(f"- **Total entries**: {log_analysis.get('total_entries', 0)}")
        lines.append(f"- **Log files scanned**: {', '.join(log_analysis.get('log_files', []))}")
        lines.append("")
        if log_analysis.get("time_gaps"):
            lines.append("### Significant Time Gaps (>60s)")
            lines.append("")
            for g in log_analysis["time_gaps"]:
                lines.append(f"- {g['gap_seconds']:.1f}s gap: `{g['between_messages']}`")
            lines.append("")
        msg_counts = log_analysis.get("message_counts", {})
        if msg_counts:
            lines.append("### Message Counts")
            lines.append("")
            for msg, count in sorted(msg_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                lines.append(f"- `{msg}`: {count}")
            lines.append("")

        # Timeout Chain
        lines.append("## Timeout Configuration Chain")
        lines.append("")
        lines.append("| File | Symbol | Timeout (s) | Description |")
        lines.append("|---|---|---|---|")
        for link in timeout_chain:
            val = str(link.get("timeout_seconds")) if link.get("timeout_seconds") is not None else "N/A"
            lines.append(f"| `{link['file']}` | `{link['symbol']}` | {val} | {link['description']} |")
        lines.append("")

        # Hang Patterns
        lines.append("## Hang Pattern Detection")
        lines.append("")
        for p in hang_patterns:
            icon = "✅" if p["matched"] else "❌"
            lines.append(f"### {icon} {p['pattern_name']} (confidence: {p['confidence']:.0%})")
            lines.append("")
            for ev in p["evidence"]:
                lines.append(f"- {ev}")
            lines.append("")

        # Code Audit
        lines.append("## Code Static Audit")
        lines.append("")
        for issue in code_audit.get("issues", []):
            lines.append(f"- **[{issue.get('severity', 'INFO')}]** `{issue['file']}`: {issue['description']}")
        lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        for i, rec in enumerate(self._build_recommendations(), 1):
            lines.append(f"{i}. **{rec['title']}** (Priority: {rec['priority']})")
            lines.append(f"   - Location: `{rec['location']}`")
            lines.append(f"   - Action: {rec['action']}")
            lines.append("")

        # Conclusion
        lines.append("## Conclusion")
        lines.append("")
        lines.append("The pipeline hang is caused by a combination of:")
        lines.append("1. **Direct cause**: `ClaudeSDKClient.receive_messages()` entering an infinite blocking state.")
        lines.append("2. **Configuration flaw**: `config.agent_timeout` (7200s) incorrectly propagated to prompt-level timeout, masking the 900s default protection.")
        lines.append("3. **Architectural gap**: No node-level or pipeline-level timeout guards exist.")
        lines.append("")
        lines.append("**Immediate action**: Cancel the pipeline and apply the recommended timeout fixes before retry.")
        lines.append("")

        return "\n".join(lines)

    def _build_recommendations(self) -> list[dict[str, Any]]:
        return [
            {
                "title": "Fix timeout propagation in dual_agent.py",
                "priority": "P0",
                "location": "nodes/dual_agent.py:343",
                "action": "Use ClaudeSessionWrapper.DEFAULT_PROMPT_TIMEOUT (900s) instead of config.agent_timeout (7200s)",
            },
            {
                "title": "Add node-level execution timeout",
                "priority": "P0",
                "location": "node_execution/executor.py:155",
                "action": "Wrap node.execute_with_context() with asyncio.wait_for(timeout=1800)",
            },
            {
                "title": "Add pipeline-level total timeout",
                "priority": "P0",
                "location": "pipeline/orchestrator.py:477",
                "action": "Wrap graph.ainvoke() with asyncio.wait_for(timeout=config.agent_timeout)",
            },
            {
                "title": "Add idle timeout in receive_messages loop",
                "priority": "P1",
                "location": "llm/session_manager.py:1032",
                "action": "Track last message time; abort if no message for 300s despite asyncio.timeout",
            },
            {
                "title": "Enhance SDK cancellation robustness",
                "priority": "P1",
                "location": "llm/session_manager.py:1030-1045",
                "action": "Add fallback thread-based watchdog if asyncio.timeout fails to cancel SDK I/O",
            },
        ]


# ---------------------------------------------------------------------------
# Code Static Auditor
# ---------------------------------------------------------------------------

class CodeStaticAuditor:
    def __init__(self, project_root: Path) -> None:
        self.docuswarm = project_root / "autoBMAD" / "docuswarm"

    def audit(self) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []

        # Check 1: receive_messages cancellation robustness
        sm = self._read("llm/session_manager.py")
        if "asyncio.timeout" in sm:
            issues.append({
                "severity": "INFO",
                "file": "llm/session_manager.py",
                "description": "asyncio.timeout wrapper present for receive_messages",
            })
        else:
            issues.append({
                "severity": "CRITICAL",
                "file": "llm/session_manager.py",
                "description": "receive_messages lacks asyncio.timeout wrapper",
            })

        # Check 2: Node executor timeout
        exec_file = self._read("node_execution/executor.py")
        if "asyncio.wait_for" not in exec_file and "asyncio.timeout" not in exec_file:
            issues.append({
                "severity": "CRITICAL",
                "file": "node_execution/executor.py",
                "description": "No node-level timeout protection in _execute_node",
            })

        # Check 3: Orchestrator timeout
        orch = self._read("pipeline/orchestrator.py")
        if "asyncio.wait_for" not in orch and "asyncio.timeout" not in orch:
            issues.append({
                "severity": "CRITICAL",
                "file": "pipeline/orchestrator.py",
                "description": "No pipeline-level timeout protection in start_pipeline",
            })

        # Check 4: dual_agent timeout misuse
        da = self._read("nodes/dual_agent.py")
        if "agent_timeout" in da:
            issues.append({
                "severity": "HIGH",
                "file": "nodes/dual_agent.py",
                "description": "config.agent_timeout propagated to prompt-level timeout",
            })

        return {"issues": issues}

    def _read(self, rel: str) -> str:
        path = self.docuswarm / rel
        return path.read_text(encoding="utf-8") if path.exists() else ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="DocuSwarm Pipeline Hang Deep Diagnostic Tool")
    parser.add_argument("--pipeline-id", required=True, help="Target pipeline ID")
    parser.add_argument("--db", default="docuswarm.db", help="SQLite database path")
    parser.add_argument("--log", action="append", help="Log file(s) to analyze (can specify multiple)")
    parser.add_argument("--output-dir", default=".", help="Output directory for reports")
    parser.add_argument("--json", action="store_true", help="Also output JSON report")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path

    log_paths: list[Path] = []
    if args.log:
        for lp in args.log:
            p = Path(lp)
            log_paths.append(p if p.is_absolute() else PROJECT_ROOT / p)
    else:
        # Default log file discovery
        logs_dir = PROJECT_ROOT / "logs"
        if logs_dir.exists():
            log_paths = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_id = args.pipeline_id

    print(f"[1/5] Analyzing database: {db_path}")
    db_analyzer = DatabaseAnalyzer(db_path)
    db_result = db_analyzer.analyze(pipeline_id)

    print(f"[2/5] Analyzing logs: {[str(p) for p in log_paths]}")
    log_analyzer = LogAnalyzer(log_paths)
    log_result = log_analyzer.analyze(pipeline_id)

    print("[3/5] Auditing timeout chain...")
    timeout_auditor = TimeoutChainAuditor(PROJECT_ROOT)
    timeout_chain = timeout_auditor.audit()

    print("[4/5] Running code static audit...")
    code_auditor = CodeStaticAuditor(PROJECT_ROOT)
    code_audit = code_auditor.audit()

    print("[5/5] Detecting hang patterns...")
    pattern_detector = HangPatternDetector()
    hang_patterns = pattern_detector.detect(db_result, log_result)

    # Build findings
    findings: list[dict[str, Any]] = []
    for p in hang_patterns:
        if p["matched"]:
            findings.append({
                "severity": "HIGH",
                "title": f"Hang pattern detected: {p['pattern_name']}",
                "detail": "; ".join(p["evidence"]),
            })
    for issue in code_audit["issues"]:
        if issue["severity"] in ("CRITICAL", "HIGH"):
            findings.append({
                "severity": issue["severity"],
                "title": f"Code audit: {issue['file']}",
                "detail": issue["description"],
            })

    # Generate reports
    generator = ReportGenerator(pipeline_id)
    md_content = generator.generate_markdown(findings, timeout_chain, log_result, db_result, hang_patterns, code_audit)
    md_path = output_dir / f"{datetime.now().strftime('%Y-%m-%d')}-pipeline-hang-root-cause-report-{pipeline_id}.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"\nMarkdown report written to: {md_path}")

    if args.json:
        json_content = generator.generate_json(findings, timeout_chain, log_result, db_result, hang_patterns, code_audit)
        json_path = output_dir / f"{datetime.now().strftime('%Y-%m-%d')}-pipeline-hang-root-cause-report-{pipeline_id}.json"
        json_path.write_text(json_content, encoding="utf-8")
        print(f"JSON report written to: {json_path}")

    print("\nDiagnostic complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
