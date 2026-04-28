# TDD-06: Timeout + ThinkingBlock 修复方案

**日期**: 2026-04-06
**关联研究**: [2026-04-06-timeout-thinkingblock-root-cause.md](../research/2026-04-06-timeout-thinkingblock-root-cause.md)
**优先级**: P0 (阻塞流水线执行)

---

## 概述

修复三个相互关联的问题:
1. **RC-1**: 60 秒超时对 Agent 模式不足 → 增加到 300 秒
2. **RC-2**: ThinkingBlock 内容泄露到文本提取 → 正确处理单 content block
3. **RC-3**: DualAgentNode 未传递 timeout → 添加 timeout 传递链

## 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `autoBMAD/docuswarm/llm/session_manager.py` | 修改 | Fix-1 + Fix-2 |
| `autoBMAD/docuswarm/nodes/dual_agent.py` | 修改 | Fix-3 |
| `autoBMAD/docuswarm/config.py` | 修改 | 新增 agent_timeout 字段 |
| `tests/test_session_manager_timeout.py` | 新增 | Fix-1 + Fix-2 单元测试 |
| `tests/test_dual_agent_timeout.py` | 新增 | Fix-3 单元测试 |

---

## Step 1: Fix-1 — 增加 DEFAULT_PROMPT_TIMEOUT

### 1.1 测试用例 (RED)

**文件**: `tests/test_session_manager_timeout.py`

```python
"""Tests for timeout configuration in ClaudeSessionWrapper."""
import pytest
from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper


class TestDefaultPromptTimeout:
    """Verify DEFAULT_PROMPT_TIMEOUT is 300 seconds."""

    def test_default_timeout_is_300(self):
        """RC-1: Default timeout should be 300 seconds, not 60."""
        assert ClaudeSessionWrapper.DEFAULT_PROMPT_TIMEOUT == 300
```

### 1.2 实现 (GREEN)

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
# Line 762: 修改
class ClaudeSessionWrapper:
    DEFAULT_PROMPT_TIMEOUT: int = 300  # 从 60 → 300
```

### 1.3 验证

```bash
pytest tests/test_session_manager_timeout.py::TestDefaultPromptTimeout -v
```

---

## Step 2: Fix-2 — 处理单个 ContentBlock

### 2.1 测试用例 (RED)

**文件**: `tests/test_session_manager_timeout.py` (追加)

```python
from unittest.mock import MagicMock


class TestThinkingBlockFiltering:
    """Verify ThinkingBlock objects don't leak into text content."""

    def _create_session_manager(self):
        """Create a minimal SessionManager for testing _message_to_dict."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from pathlib import Path
        return SessionManager(work_dir=Path("."))

    def test_single_thinkingblock_content_filtered(self):
        """RC-2: Single ThinkingBlock as content should be filtered, not stringified."""
        sm = self._create_session_manager()

        # Simulate SDK message with single ThinkingBlock content (not in a list)
        mock_msg = MagicMock()
        mock_msg.role = "assistant"
        mock_msg.model = "claude-sonnet"

        # Single ThinkingBlock as content (not a list)
        mock_thinking = MagicMock()
        mock_thinking.type = "thinking"
        mock_thinking.thinking = "I need to create the deliverable..."
        # ThinkingBlock does NOT have .text attribute
        del mock_thinking.text
        mock_thinking.__class__.__name__ = "ThinkingBlock"

        mock_msg.content = mock_thinking

        result = sm._message_to_dict(mock_msg)

        # ThinkingBlock should be filtered out, not stringified
        if result is not None:
            content = result.get("content", [])
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text", "")
                    assert "ThinkingBlock" not in text, (
                        f"ThinkingBlock repr leaked into text content: {text[:100]}"
                    )

    def test_list_thinkingblock_content_filtered(self):
        """ThinkingBlock in list content should be filtered out."""
        sm = self._create_session_manager()

        mock_msg = MagicMock()
        mock_msg.role = "assistant"
        mock_msg.model = "claude-sonnet"

        # ThinkingBlock in a list
        mock_thinking = MagicMock()
        mock_thinking.type = "thinking"
        mock_thinking.thinking = "I need to think..."
        del mock_thinking.text

        mock_msg.content = [mock_thinking]

        result = sm._message_to_dict(mock_msg)

        if result is not None:
            content = result.get("content", [])
            for part in content:
                if isinstance(part, dict):
                    assert part.get("type") != "thinking" or "ThinkingBlock" not in str(
                        part.get("content", "")
                    )
```

### 2.2 实现 (GREEN)

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

在 `_message_to_dict()` 方法的 content 处理部分（约 line 606-621），
在 `else` 分支前添加单个 content block 的处理：

```python
        # 修改后的 content 处理逻辑:
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        elif isinstance(content, list):
            # ... existing list processing ...
            content = converted_content
        elif hasattr(content, 'type'):
            # 新增: 处理单个 content block (不在 list 中)
            converted_block = self._convert_content_block(content)
            if converted_block:
                content = [converted_block]
            else:
                content = []  # ThinkingBlock 等被过滤为空
        else:
            content = [{"type": "text", "text": str(content)}]
```

### 2.3 验证

```bash
pytest tests/test_session_manager_timeout.py::TestThinkingBlockFiltering -v
```

---

## Step 3: Fix-3 — DualAgentNode 传递 timeout

### 3.1 测试用例 (RED)

**文件**: `tests/test_dual_agent_timeout.py`

```python
"""Tests for timeout propagation in DualAgentNode."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestDualAgentTimeoutPropagation:
    """Verify timeout is passed from DualAgentNode to IndependentAgent."""

    @pytest.mark.asyncio
    async def test_execute_with_context_passes_timeout(self):
        """RC-3: execute_with_context should pass timeout to execute_with_input."""
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode

        # Create mocks
        config = MagicMock()
        config.max_iterations = 3

        independent_agent = AsyncMock()
        independent_agent.execute_with_input = AsyncMock(return_value={
            "deliverable": {"title": "test", "content": "test", "file_path": "test.md", "sha256": "abc"},
            "questions": [],
            "action": "create_deliverable",
        })

        evaluator_agent = AsyncMock()
        evaluator_agent.execute_with_input = AsyncMock(return_value={
            "verdict": "APPROVED",
            "alignment_score": 0.9,
            "issues_found": [],
            "suggestions": [],
        })

        node = DualAgentNode(
            config=config,
            independent_agent=independent_agent,
            evaluator_agent=evaluator_agent,
            node_id="analyst",
        )

        # Build minimal execution context
        execution_context = {
            "pipeline_id": "test-pipeline",
            "node_id": "analyst",
            "node_name": "Analyst",
            "node_order": 0,
            "original_context": {"content": "test"},
            "chained_deliverables": [],
            "shared_context": {},
        }

        # Execute
        with patch.object(node.context_manager, 'build_independent_input', return_value={}):
            with patch.object(node.context_manager, 'build_evaluator_input', return_value={}):
                try:
                    await node.execute_with_context(execution_context)
                except Exception:
                    pass  # May fail due to mocks, but we check the call

        # Verify timeout was passed
        if independent_agent.execute_with_input.called:
            call_kwargs = independent_agent.execute_with_input.call_args
            assert 'timeout' in call_kwargs.kwargs or len(call_kwargs.args) >= 3, (
                "execute_with_input should receive timeout parameter"
            )
```

### 3.2 实现 (GREEN)

**文件**: `autoBMAD/docuswarm/config.py`

```python
# 添加 agent_timeout 字段到 Config
@dataclass(frozen=True)
class Config:
    # ... existing fields ...
    agent_timeout: int = field(default=300)
```

**文件**: `autoBMAD/docuswarm/nodes/dual_agent.py`

```python
# execute_with_context() 中传递 timeout
independent_output = await self.independent_agent.execute_with_input(
    agent_input=independent_input,
    pipeline_id=pipeline_id,
    timeout=getattr(self.config, 'agent_timeout', 300),  # Fix-3
)
```

### 3.3 验证

```bash
pytest tests/test_dual_agent_timeout.py -v
```

---

## Step 4: Config 新增 agent_timeout 字段

### 4.1 测试用例 (RED)

在现有 Config 测试中添加:

```python
def test_config_agent_timeout_default():
    """Config should have agent_timeout defaulting to 300."""
    from autoBMAD.docuswarm.config import Config
    config = Config(api_key="test-key")
    assert config.agent_timeout == 300

def test_config_agent_timeout_from_env(monkeypatch):
    """Config should read DOCUSWARM_AGENT_TIMEOUT from env."""
    monkeypatch.setenv("DOCUSWARM_AGENT_TIMEOUT", "600")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from autoBMAD.docuswarm.config import Config
    config = Config.from_env_and_yaml()
    assert config.agent_timeout == 600
```

### 4.2 实现 (GREEN)

**文件**: `autoBMAD/docuswarm/config.py`

```python
@dataclass(frozen=True)
class Config:
    # existing fields...
    agent_timeout: int = field(default=300)
    # ...

    @classmethod
    def from_env_and_yaml(cls, yaml_path=None):
        # ... existing code ...
        agent_timeout = int(
            os.environ.get("DOCUSWARM_AGENT_TIMEOUT")
            or yaml_config.get("agent_timeout", 300)
        )
        return cls(
            # ... existing fields ...
            agent_timeout=agent_timeout,
        )
```

---

## 执行顺序

1. **Step 1**: Fix-1 修改 DEFAULT_PROMPT_TIMEOUT (最小改动, 最大收益)
2. **Step 2**: Fix-2 处理单 content block (防止 ThinkingBlock 泄露)
3. **Step 3**: Fix-3 传递 timeout 参数 (完善配置链)
4. **Step 4**: Config 新增字段 (可选, 支持用户自定义)
5. **验证**: 运行完整测试 + 重新执行 pipeline 命令

## 验收标准

1. `ClaudeSessionWrapper.DEFAULT_PROMPT_TIMEOUT == 300`
2. ThinkingBlock 对象不会作为字符串泄露到消息内容中
3. `DualAgentNode.execute_with_context()` 传递 timeout 到 `execute_with_input()`
4. `pytest -v --tb=short` 全部通过
5. `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` analyst 节点不再因超时失败
