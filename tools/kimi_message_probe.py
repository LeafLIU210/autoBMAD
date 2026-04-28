"""
Kimi Message Probe - DocuSwarm 调试工具

深度探测 claude_agent_sdk 与 Kimi API 对接时的消息结构差异，
用于诊断 no_text_extracted / AssistantMessage.role=None 等兼容性问题。

Usage:
    python tools/kimi_message_probe.py
    python tools/kimi_message_probe.py --prompt "你好，请用中文回复一句话"
    python tools/kimi_message_probe.py --full-pipeline
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────── helpers ────────────────────────────────────

def _section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def _ok(msg: str) -> str:
    return f"[OK] {msg}"


def _fail(msg: str) -> str:
    return f"[!!] {msg}"


def _field(name: str, value: Any, indent: int = 0) -> None:
    prefix = "  " * indent
    print(f"{prefix}{name}: {value!r}")


def _env_check() -> dict[str, str]:
    """Check critical environment variables."""
    keys = [
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ENABLE_TOOL_SEARCH",
    ]
    result = {}
    for k in keys:
        v = os.environ.get(k, "NOT SET")
        if "KEY" in k and v != "NOT SET":
            display = v[:12] + "..." + v[-4:]
        else:
            display = v
        result[k] = v
        print(f"  {k}: {display}")
    return result


# ─────────────────────────────── core probe ─────────────────────────────────

async def probe_sdk_message_structure(prompt: str = "Say hello in one word") -> dict[str, Any]:
    """
    Probe the exact message structure returned by claude_agent_sdk when
    using Kimi endpoint. Diagnoses role/content field availability.

    Returns a diagnostic report dict.
    """
    from claude_agent_sdk import query
    from claude_agent_sdk.types import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        SystemMessage,
        UserMessage,
    )

    report: dict[str, Any] = {
        "prompt": prompt,
        "messages": [],
        "issues": [],
        "summary": {},
    }

    opts = ClaudeAgentOptions(
        model="kimi-k2-0711-preview",
        max_turns=1,
    )

    _section("1. RAW SDK MESSAGE STRUCTURE PROBE")
    print(f"  Prompt: {prompt!r}")
    print()

    msg_idx = 0
    has_assistant_with_role = False
    has_assistant_without_role = False
    text_extracted = ""

    async for msg in query(prompt=prompt, options=opts):
        msg_type = type(msg).__name__
        msg_info: dict[str, Any] = {
            "index": msg_idx,
            "type": msg_type,
            "has_role": hasattr(msg, "role"),
            "role_value": getattr(msg, "role", "ATTRIBUTE_MISSING"),
            "has_content": hasattr(msg, "content"),
            "content_type": type(getattr(msg, "content", None)).__name__,
            "content_items": [],
            "has_extract_text": hasattr(msg, "extract_text"),
            "extract_text_result": None,
        }

        print(f"  [{msg_idx}] {msg_type}")
        _field("has_role", msg_info["has_role"], indent=2)
        _field("role", msg_info["role_value"], indent=2)

        # Inspect AssistantMessage
        if isinstance(msg, AssistantMessage):
            content = getattr(msg, "content", None)
            _field("content_type", type(content).__name__, indent=2)

            if isinstance(content, list):
                for i, item in enumerate(content):
                    item_type = type(item).__name__
                    item_attr_type = getattr(item, "type", "NO_TYPE_ATTR")
                    has_text = hasattr(item, "text")
                    has_thinking = hasattr(item, "thinking")

                    item_info = {
                        "index": i,
                        "class": item_type,
                        "type_attr": item_attr_type,
                        "has_text": has_text,
                        "has_thinking": has_thinking,
                        "text_value": getattr(item, "text", None),
                        "thinking_preview": str(getattr(item, "thinking", ""))[:80] if has_thinking else None,
                    }
                    msg_info["content_items"].append(item_info)

                    print(f"      content[{i}]: {item_type}")
                    _field("type attr", item_attr_type, indent=4)
                    _field("has_text", has_text, indent=4)
                    _field("has_thinking", has_thinking, indent=4)
                    if has_text:
                        _field("text", getattr(item, "text", ""), indent=4)

            # Test extract_text()
            if hasattr(msg, "extract_text"):
                try:
                    extracted = msg.extract_text()
                    msg_info["extract_text_result"] = extracted
                    _field("extract_text()", repr(extracted[:80]) if extracted else repr(extracted), indent=2)
                    if extracted:
                        text_extracted = extracted
                except Exception as e:
                    msg_info["extract_text_error"] = str(e)
                    _field("extract_text() ERROR", str(e), indent=2)

            # Track role availability
            role = getattr(msg, "role", None)
            if role == "assistant":
                has_assistant_with_role = True
            else:
                has_assistant_without_role = True

        elif isinstance(msg, SystemMessage):
            _field("subtype", getattr(msg, "subtype", "N/A"), indent=2)

        elif isinstance(msg, ResultMessage):
            result_val = getattr(msg, "result", "N/A")
            _field("result", str(result_val)[:100], indent=2)
            msg_info["result"] = str(result_val)[:200]

        elif isinstance(msg, UserMessage):
            _field("content", str(getattr(msg, "content", ""))[:80], indent=2)

        report["messages"].append(msg_info)
        msg_idx += 1

    # ── Issue detection ──────────────────────────────────────────────────────
    _section("2. ISSUE DETECTION")

    if has_assistant_without_role and not has_assistant_with_role:
        issue = {
            "id": "ISSUE-001",
            "severity": "CRITICAL",
            "title": "AssistantMessage has no 'role' attribute",
            "detail": (
                "Kimi's AssistantMessage dataclass does not include a 'role' field. "
                "extract_text_from_messages() checks `if msg_role != 'assistant': continue`, "
                "which means all AssistantMessage objects are skipped, resulting in no_text_extracted."
            ),
            "affected_code": [
                "autoBMAD/docuswarm/llm/response.py:extract_text_from_messages() L190",
                "autoBMAD/docuswarm/agents/independent.py:_extract_content_from_messages()",
            ],
            "fix": (
                "Replace `if msg_role != 'assistant': continue` with "
                "`if not isinstance(msg, AssistantMessage) and msg_role != 'assistant': continue`. "
                "Or use `isinstance(msg, AssistantMessage)` check directly."
            ),
        }
        report["issues"].append(issue)
        print(f"  {_fail(issue['id'])} [{issue['severity']}]: {issue['title']}")
        print(f"     {issue['detail'][:120]}")
    
    if not text_extracted:
        issue2 = {
            "id": "ISSUE-002",
            "severity": "HIGH",
            "title": "No text extracted from messages via extract_text_from_messages()",
            "detail": (
                "The function iterates messages in reverse and filters by role=='assistant', "
                "but AssistantMessage.role is None in Kimi SDK, so filter skips all messages."
            ),
            "affected_code": [
                "autoBMAD/docuswarm/llm/response.py:extract_text_from_messages()",
                "autoBMAD/docuswarm/context/validator.py:LLMContextValidationStrategy._parse_validation_response()",
            ],
            "fix": "Use isinstance(msg, AssistantMessage) as primary check instead of role string comparison.",
        }
        report["issues"].append(issue2)
        print(f"  {_fail(issue2['id'])} [{issue2['severity']}]: {issue2['title']}")

    # ── single_prompt simulation ─────────────────────────────────────────────
    _section("3. single_prompt() SIMULATION")
    await _simulate_single_prompt(prompt)

    # ── Summary ─────────────────────────────────────────────────────────────
    _section("4. SUMMARY")
    report["summary"] = {
        "total_messages": msg_idx,
        "has_assistant_with_role": has_assistant_with_role,
        "has_assistant_without_role": has_assistant_without_role,
        "text_extracted": bool(text_extracted),
        "text_preview": text_extracted[:100] if text_extracted else "",
        "issue_count": len(report["issues"]),
        "critical_issues": [i for i in report["issues"] if i.get("severity") == "CRITICAL"],
    }

    for k, v in report["summary"].items():
        if k != "critical_issues":
            print(f"  {k}: {v}")

    return report


async def _simulate_single_prompt(prompt: str) -> None:
    """Simulate what SessionManager.single_prompt() does and show where it breaks."""
    from autoBMAD.docuswarm.llm.response import extract_text_from_messages
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    from pathlib import Path

    print("  Running SessionManager.single_prompt()...")

    sm = SessionManager(work_dir=Path.cwd())
    try:
        messages = await sm.single_prompt(prompt=prompt, mode="agent", yolo=True)
        print(f"  Got {len(messages)} messages")

        # Try extract_text_from_messages
        text = extract_text_from_messages(messages)  # type: ignore[arg-type]
        print(f"  extract_text_from_messages() -> {repr(text[:80]) if text else 'EMPTY STRING'}")

        if not text:
            print("  [!!] CONFIRMED: no_text_extracted bug reproduced!")
            print()
            print("  Diagnosing message roles:")
            for i, m in enumerate(messages):
                role = m.get("role", "MISSING_KEY")
                content = m.get("content", [])
                content_types = [c.get("type", "?") for c in content] if isinstance(content, list) else []
                print(f"    [{i}] role={role!r}, content_types={content_types}")
        else:
            print(f"  [OK] Text extracted: {text[:80]!r}")
    except Exception as e:
        print(f"  [!!] single_prompt() ERROR: {type(e).__name__}: {e}")


async def probe_fix_verification(prompt: str = "Say hello in one word") -> None:
    """
    Verify the proposed fix works correctly.

    Root causes identified:
    1. AssistantMessage has NO 'role' attribute -> use isinstance() check
    2. TextBlock/ThinkingBlock have NO 'type' attribute -> use isinstance() check
    """
    from claude_agent_sdk import query
    from claude_agent_sdk.types import AssistantMessage, ClaudeAgentOptions, TextBlock

    _section("5. FIX VERIFICATION - isinstance() based extraction")
    print("  Root cause: AssistantMessage has no 'role' attr; TextBlock has no 'type' attr")
    print("  Fix: use isinstance(msg, AssistantMessage) + isinstance(item, TextBlock)")
    print()

    opts = ClaudeAgentOptions(model="kimi-k2-0711-preview", max_turns=1)
    extracted_texts = []

    async for msg in query(prompt=prompt, options=opts):
        # FIX 1: Use isinstance instead of role string comparison
        if isinstance(msg, AssistantMessage):
            content = getattr(msg, "content", [])
            if isinstance(content, list):
                for item in content:
                    # FIX 2: Use isinstance(item, TextBlock) instead of type attr check
                    if isinstance(item, TextBlock):
                        text = item.text
                        extracted_texts.append(text)
                        print(f"  [OK] Extracted via isinstance(item, TextBlock): {text!r}")
                    elif hasattr(item, "text") and not hasattr(item, "thinking"):
                        # Fallback for unknown text-like blocks
                        text = item.text
                        extracted_texts.append(text)
                        print(f"  [OK] Extracted via has_text fallback: {text!r}")
    
    if extracted_texts:
        print(f"\n  Total text parts extracted: {len(extracted_texts)}")
        print(f"  Combined: {' '.join(extracted_texts)!r}")
        print("  [OK] FIX VERIFIED: isinstance-based extraction works!")
    else:
        print("  [!!] Still no text extracted - deeper issue")


async def probe_full_pipeline_flow() -> None:
    """Probe the complete context validation -> pipeline -> node execution flow."""
    _section("FULL PIPELINE FLOW PROBE")
    print("  This probes the actual docuswarm start command flow")
    print()

    # Step 1: Check ContextValidator single_prompt call
    _section("5a. ContextValidator LLM validation call")
    from autoBMAD.docuswarm.context.validator import LLMContextValidationStrategy
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    from pathlib import Path

    sm = SessionManager(work_dir=Path.cwd())
    strategy = LLMContextValidationStrategy()
    test_context = {
        "subject": "bubble sort algorithm",
        "task": "Create test documentation for bubble sort",
    }

    try:
        result = await strategy.validate(test_context, config={"session_manager": sm})
        print(f"  LLM validation result: valid={result.valid}")
        print(f"  metadata: {result.metadata}")
        if result.issues:
            for issue in result.issues:
                print(f"  [!!] Issue: {issue.message}")
    except Exception as e:
        print(f"  [!!] ERROR: {type(e).__name__}: {e}")


# ─────────────────────────────── main ────────────────────────────────────────

async def main(args: argparse.Namespace) -> None:
    _section("KIMI MESSAGE PROBE - DocuSwarm Debug Tool")
    print(f"  claude_agent_sdk version check...")

    try:
        import claude_agent_sdk
        print(f"  SDK version: {claude_agent_sdk.__version__}")
    except Exception as e:
        print(f"  [!!] SDK import error: {e}")
        return

    _section("ENVIRONMENT CHECK")
    _env_check()

    # Core probe
    report = await probe_sdk_message_structure(args.prompt)

    # Fix verification
    await probe_fix_verification(args.prompt)

    # Full pipeline probe if requested
    if args.full_pipeline:
        await probe_full_pipeline_flow()

    # Save report
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n  Report saved to: {output_path}")

    _section("PROBE COMPLETE")
    issue_count = len(report["issues"])
    if issue_count == 0:
        print("  [OK] No issues detected")
    else:
        print(f"  [!!] {issue_count} issue(s) detected - see ISSUE DETECTION section above")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe Kimi + claude_agent_sdk message structure for DocuSwarm debugging"
    )
    parser.add_argument(
        "--prompt",
        default="Say hello in one word",
        help="Prompt to test with (default: 'Say hello in one word')",
    )
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        help="Also probe the full pipeline flow (context validator etc.)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Save JSON report to this path (optional)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
