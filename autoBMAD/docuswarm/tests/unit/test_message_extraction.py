"""Unit tests for message content extraction utility.

TDD Phase: RED
Target: autoBMAD.docuswarm.llm.response.extract_text_from_messages

These tests define the expected behavior for extracting text content
from Kimi SDK Message objects, covering all ContentPart types and edge cases.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

# Import HybridOrchestrator only for type hints (avoid runtime overhead)
if TYPE_CHECKING:
    from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator

# ============================================================
# Fixture: Realistic SDK Message Mocks
# ============================================================


def _make_text_part(text: str) -> MagicMock:
    """Create a mock TextPart with proper attributes."""
    part = MagicMock()
    part.type = "text"
    part.text = text
    # isinstance check support
    part.__class__.__name__ = "TextPart"
    return part


def _make_think_part(text: str) -> MagicMock:
    """Create a mock ThinkPart with proper attributes."""
    part = MagicMock()
    part.type = "thinking"
    part.text = text
    part.__class__.__name__ = "ThinkPart"
    return part


def _make_message(
    role: str = "assistant",
    content: list[Any] | None = None,
    has_extract_text: bool = True,
    extract_text_return: str | None = None,
) -> MagicMock:
    """Create a mock Message matching Kimi SDK structure.

    Args:
        role: Message role ("assistant", "user", "system").
        content: list of ContentPart mocks. None means empty list.
        has_extract_text: Whether the message has extract_text() method.
        extract_text_return: Custom return value for extract_text().
    """
    msg = MagicMock()
    msg.role = role
    msg.content = content if content is not None else []

    if has_extract_text:
        if extract_text_return is not None:
            msg.extract_text.return_value = extract_text_return
        else:
            # Simulate SDK behavior: join all TextPart.text values
            text_parts = [
                p.text for p in (content or []) if hasattr(p, "type") and p.type == "text"
            ]
            msg.extract_text.return_value = "".join(text_parts)
    else:
        # Remove extract_text attribute entirely
        del msg.extract_text

    return msg


# ============================================================
# Test Class: extract_text_from_messages 核心功能
# ============================================================


class TestExtractTextFromMessages:
    """Tests for extract_text_from_messages utility function.

    TDD Phase: RED — All tests should FAIL until function is implemented.
    """

    # --- 基础功能测试 ---

    def test_single_text_part(self) -> None:
        """从单个 TextPart 的 assistant 消息中提取文本。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(
            role="assistant",
            content=[_make_text_part("Hello world")],
            extract_text_return="Hello world",
        )
        result = extract_text_from_messages([msg])
        assert result == "Hello world"

    def test_multiple_text_parts(self) -> None:
        """从包含多个 TextPart 的消息中提取并连接文本。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(
            role="assistant",
            content=[_make_text_part("Hello "), _make_text_part("world")],
            extract_text_return="Hello world",
        )
        result = extract_text_from_messages([msg])
        assert result == "Hello world"

    def test_empty_messages_list(self) -> None:
        """空消息列表应返回空字符串。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        result = extract_text_from_messages([])
        assert result == ""

    def test_no_assistant_messages(self) -> None:
        """没有 assistant 消息时应返回空字符串。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        user_msg = _make_message(role="user", content=[_make_text_part("Question?")])
        system_msg = _make_message(role="system", content=[_make_text_part("System init")])
        result = extract_text_from_messages([user_msg, system_msg])
        assert result == ""

    def test_empty_content_list(self) -> None:
        """content 为空列表的 assistant 消息应返回空字符串。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(role="assistant", content=[], extract_text_return="")
        result = extract_text_from_messages([msg])
        assert result == ""

    # --- SDK extract_text() 方法测试 ---

    def test_uses_extract_text_method(self) -> None:
        """优先使用 SDK 的 extract_text() 方法。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(
            role="assistant",
            content=[_make_text_part("Direct text")],
            has_extract_text=True,
            extract_text_return="Extracted via SDK",
        )
        result = extract_text_from_messages([msg])
        assert result == "Extracted via SDK"
        msg.extract_text.assert_called()

    def test_fallback_without_extract_text(self) -> None:
        """当 Message 没有 extract_text() 方法时，回退到手动提取。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(
            role="assistant",
            content=[_make_text_part("Fallback text")],
            has_extract_text=False,
        )
        result = extract_text_from_messages([msg])
        assert result == "Fallback text"

    # --- ThinkPart 处理测试 ---

    def test_ignores_think_parts_with_extract_text(self) -> None:
        """使用 extract_text() 时自动忽略 ThinkPart（SDK 行为）。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(
            role="assistant",
            content=[
                _make_think_part("Let me think..."),
                _make_text_part("Final answer"),
            ],
            extract_text_return="Final answer",
        )
        result = extract_text_from_messages([msg])
        assert result == "Final answer"
        assert "think" not in result.lower() or result == "Final answer"

    def test_ignores_think_parts_manual_extraction(self) -> None:
        """手动提取时也应忽略 ThinkPart，只提取 TextPart。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        think_part = _make_think_part("Let me think...")
        text_part = _make_text_part("Final answer")

        msg = _make_message(
            role="assistant",
            content=[think_part, text_part],
            has_extract_text=False,
        )
        result = extract_text_from_messages([msg])
        # 应只包含 TextPart 的文本，不包含 ThinkPart
        assert "Final answer" in result

    def test_only_think_parts_returns_empty(self) -> None:
        """消息中仅包含 ThinkPart 时，extract_text() 返回空字符串 → 跳过该消息。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = _make_message(
            role="assistant",
            content=[_make_think_part("Internal reasoning only")],
            extract_text_return="",
        )
        result = extract_text_from_messages([msg])
        assert result == ""

    # --- 多消息选择测试 ---

    def test_returns_last_assistant_message(self) -> None:
        """从多条消息中提取最后一条 assistant 消息的内容。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        messages = [
            _make_message(role="user", content=[_make_text_part("Question")]),
            _make_message(
                role="assistant",
                content=[_make_text_part("First response")],
                extract_text_return="First response",
            ),
            _make_message(
                role="assistant",
                content=[_make_text_part("Final response")],
                extract_text_return="Final response",
            ),
        ]
        result = extract_text_from_messages(messages)
        assert result == "Final response"

    def test_skips_empty_last_message_uses_previous(self) -> None:
        """最后一条 assistant 消息为空时，应使用倒数第二条有内容的 assistant 消息。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        messages = [
            _make_message(
                role="assistant",
                content=[_make_text_part("Valid response")],
                extract_text_return="Valid response",
            ),
            _make_message(role="assistant", content=[], extract_text_return=""),
        ]
        result = extract_text_from_messages(messages)
        assert result == "Valid response"

    # --- 类型兼容性测试 ---

    def test_string_content_fallback(self) -> None:
        """当 content 是字符串（旧版兼容）时，直接返回字符串。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        msg = MagicMock()
        msg.role = "assistant"
        msg.content = "Direct string content"
        # 没有 extract_text() 方法
        del msg.extract_text
        result = extract_text_from_messages([msg])
        assert result == "Direct string content"

    # --- JSON 内容提取测试（orchestrator 场景）---

    def test_json_content_extraction(self) -> None:
        """验证 JSON 字符串可以被正确提取（orchestrator 验证场景）。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        json_text = '{"valid": true, "reason": "Context is valid", "missing_info": []}'
        msg = _make_message(
            role="assistant",
            content=[_make_text_part(json_text)],
            extract_text_return=json_text,
        )
        result = extract_text_from_messages([msg])
        assert '"valid": true' in result

    def test_markdown_wrapped_json(self) -> None:
        """验证 Markdown 包裹的 JSON 内容可以被正确提取。"""
        from autoBMAD.docuswarm.llm.response import extract_text_from_messages

        json_text = '```json\n{"valid": true}\n```'
        msg = _make_message(
            role="assistant",
            content=[_make_text_part(json_text)],
            extract_text_return=json_text,
        )
        result = extract_text_from_messages([msg])
        assert "valid" in result


# ============================================================
# Test Class: orchestrator._validate_context 消息提取修复
# ============================================================


class TestOrchestratorValidateContextExtraction:
    """Tests for orchestrator._validate_context message extraction fix.

    TDD Phase: RED — Tests verify that orchestrator correctly handles
    list[ContentPart] from Kimi SDK instead of assuming string content.
    """

    @pytest.fixture
    def orchestrator(self, tmp_path: Path) -> HybridOrchestrator:
        """Create orchestrator with temp database."""
        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator

        return HybridOrchestrator(db_path=str(tmp_path / "test.db"))

    @pytest.fixture
    def mock_session_manager_sdk(self) -> MagicMock:
        """Create a mock session manager that returns SDK-realistic messages.

        Unlike the existing mock_session_manager, this fixture properly
        simulates Kimi SDK Message objects with list[ContentPart] content.
        """
        from unittest.mock import AsyncMock

        json_response = '{"valid": true, "reason": "Context is sufficient", "missing_info": []}'

        # Create realistic Message mock with list[ContentPart]
        text_part = _make_text_part(json_response)
        assistant_msg = _make_message(
            role="assistant",
            content=[text_part],
            extract_text_return=json_response,
        )

        mock = MagicMock()
        mock.single_prompt = AsyncMock(return_value=[assistant_msg])
        mock.close_all = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_validate_context_with_list_content_part(
        self,
        orchestrator: HybridOrchestrator,
        mock_session_manager_sdk: MagicMock,
    ) -> None:
        """验证 _validate_context 能正确处理 list[ContentPart] 类型的 content。

        这是核心回归测试：之前 orchestrator 假设 msg.content 是 str，
        导致 LLM 返回 4 条消息但提取的 content 为空。
        """
        object.__setattr__(orchestrator, "_session_manager", mock_session_manager_sdk)

        result = await object.__getattribute__(orchestrator, "_validate_context")(
            {"subject": "test", "content": "Build a REST API"}
        )

        assert result["valid"] is True
        assert "reason" in result

    @pytest.mark.asyncio
    async def test_validate_context_with_thinking_and_text(
        self,
        orchestrator: HybridOrchestrator,
    ) -> None:
        """验证 _validate_context 在 LLM 返回 ThinkPart + TextPart 时能正确提取文本。"""
        from unittest.mock import AsyncMock

        json_response = '{"valid": true, "reason": "OK", "missing_info": []}'

        msg = _make_message(
            role="assistant",
            content=[
                _make_think_part("Analyzing the context..."),
                _make_text_part(json_response),
            ],
            extract_text_return=json_response,
        )

        mock_sm = MagicMock()
        mock_sm.single_prompt = AsyncMock(return_value=[msg])
        mock_sm.close_all = AsyncMock()
        object.__setattr__(orchestrator, "_session_manager", mock_sm)

        result = await object.__getattribute__(orchestrator, "_validate_context")(
            {"subject": "test", "content": "Test content"}
        )

        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_context_with_empty_content_failopen(
        self,
        orchestrator: HybridOrchestrator,
    ) -> None:
        """验证 content 为空时的 fail-open 策略（返回 valid=True）。"""
        from unittest.mock import AsyncMock

        msg = _make_message(role="assistant", content=[], extract_text_return="")

        mock_sm = MagicMock()
        mock_sm.single_prompt = AsyncMock(return_value=[msg])
        mock_sm.close_all = AsyncMock()
        object.__setattr__(orchestrator, "_session_manager", mock_sm)

        result = await object.__getattribute__(orchestrator, "_validate_context")(
            {"subject": "test", "content": "Test"}
        )

        # fail-open: 应该返回 valid=True
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_context_four_messages_scenario(
        self,
        orchestrator: HybridOrchestrator,
    ) -> None:
        """复现实际场景：LLM 返回 4 条消息（system, user, assistant/think, assistant/text）。

        这是从日志中观察到的真实场景：
        - message_count=4
        - 最后一条 assistant 消息 content 为空列表
        - 倒数第二条 assistant 消息包含 ThinkPart
        """
        from unittest.mock import AsyncMock

        json_response = '{"valid": true, "reason": "OK", "missing_info": []}'

        messages = [
            _make_message(role="system", content=[_make_text_part("System init")]),
            _make_message(role="user", content=[_make_text_part("Validate context")]),
            _make_message(
                role="assistant",
                content=[
                    _make_think_part("Analyzing..."),
                    _make_text_part(json_response),
                ],
                extract_text_return=json_response,
            ),
            _make_message(role="assistant", content=[], extract_text_return=""),
        ]

        mock_sm = MagicMock()
        mock_sm.single_prompt = AsyncMock(return_value=messages)
        mock_sm.close_all = AsyncMock()
        object.__setattr__(orchestrator, "_session_manager", mock_sm)

        result = await object.__getattribute__(orchestrator, "_validate_context")(
            {"subject": "test", "content": "Build a web app"}
        )

        assert result["valid"] is True
        assert "reason" in result


# ============================================================
# Test Class: conftest.py mock 一致性
# ============================================================


class TestMockConsistency:
    """Tests verifying that mock fixtures match SDK behavior.

    These tests ensure the test infrastructure itself is correct.
    """

    def test_mock_message_content_is_list(self) -> None:
        """验证 mock Message 的 content 是 list 类型（与 SDK 一致）。"""
        msg = _make_message(
            role="assistant",
            content=[_make_text_part("test")],
        )
        assert isinstance(msg.content, list)

    def test_mock_message_has_extract_text(self) -> None:
        """验证 mock Message 有 extract_text() 方法。"""
        msg = _make_message(
            role="assistant",
            content=[_make_text_part("test")],
            extract_text_return="test",
        )
        assert hasattr(msg, "extract_text")
        assert msg.extract_text() == "test"

    def test_mock_text_part_has_text_attribute(self) -> None:
        """验证 mock TextPart 有 text 属性。"""
        part = _make_text_part("hello")
        assert hasattr(part, "text")
        assert part.text == "hello"

    def test_mock_think_part_has_thinking_type(self) -> None:
        """验证 mock ThinkPart 的 type 为 'thinking'。"""
        part = _make_think_part("reasoning")
        assert part.type == "thinking"
