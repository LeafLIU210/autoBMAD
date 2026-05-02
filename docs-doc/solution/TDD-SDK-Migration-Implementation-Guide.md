# TDD SDK 迁移实施指南

**配套文档**: [TDD-SDK-Migration-2026-03-25.md](./TDD-SDK-Migration-2026-03-25.md)  
**目标读者**: 开发人员  
**目标**: 逐步实施 SDK 迁移

---

## 快速开始

### 1. 准备工作

```bash
# 1. 确保当前工作目录是项目根目录
cd D:\GITHUB\DocuSwarm

# 2. 创建功能分支
git checkout -b feature/sdk-migration-tdd

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 验证当前漂移状态
python tools/dependency_analysis/migration_tracker.py
```

### 2. 运行初始测试 (应该失败)

```bash
# 所有测试应该失败 (Red phase)
pytest tests/llm/test_session_manager_tdd.py -v
```

预期输出:
```
FAILED tests/llm/test_session_manager_tdd.py::TestSessionManagerImports::test_no_kimi_sdk_imports
FAILED tests/llm/test_session_manager_tdd.py::TestSessionManagerImports::test_claude_sdk_imports_present
...
```

---

## 实施步骤详解

### Step 4.1: SessionManager - 导入迁移

**测试**: `tests/llm/test_session_manager_tdd.py::TestSessionManagerImports`

**实施**:

```python
# autoBMAD/docuswarm/llm/session_manager.py

# BEFORE:
from kaos.path import KaosPath
from kimi_agent_sdk import (
    ApprovalHandlerFn, ChatProviderError, Config, ConfigError,
    InvalidToolError, MaxStepsReached, Message, RunCancelled,
    Session, WireMessage,
)
from kimi_agent_sdk._aggregator import MessageAggregator

# AFTER:
from pathlib import Path
from typing import Any, AsyncIterator
from claude_agent_sdk import ResultMessage, query
from claude_agent_sdk import (
    AssistantMessage, SystemMessage, TextBlock,
    ThinkingBlock, ToolResultBlock, ToolUseBlock, UserMessage
)
import structlog
```

**验证**:
```bash
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerImports -v
# 应该通过
```

---

### Step 4.2: SessionManager - 类定义迁移

**测试**: `tests/llm/test_session_manager_tdd.py::TestSessionManagerInitialization`

**实施**:

```python
# BEFORE:
class KimiSessionManager:
    def __init__(
        self,
        work_dir: KaosPath,
        agent_file: Path | None = None,
        config: ConfigParam = None,
        ...
    ) -> None:
        self._work_dir = work_dir

# AFTER:
class SessionManager:
    """Manages LLM sessions using claude-agent-sdk."""
    
    def __init__(
        self,
        work_dir: Path,  # Changed from KaosPath
        agent_file: Path | None = None,
        config: dict[str, Any] | None = None,  # Changed from Config
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._work_dir = work_dir
        self._agent_file = agent_file
        self._config = config or self._build_default_config(api_key, base_url)
        self._active_sessions: dict[str, Any] = {}
        self._logger = structlog.get_logger(__name__)
    
    def _build_default_config(self, api_key: str | None, base_url: str | None) -> dict[str, Any]:
        """Build default config for claude-agent-sdk."""
        return {
            "model": "kimi-for-coding",
            "api_key": api_key or os.environ.get("KIMI_API_KEY"),
            "base_url": base_url or os.environ.get("KIMI_BASE_URL", "https://api.kimi.com/coding/"),
        }
```

**验证**:
```bash
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerInitialization -v
```

---

### Step 4.3: SessionManager - single_prompt 方法

**测试**: `tests/llm/test_session_manager_tdd.py::TestSessionManagerSinglePrompt`

**实施**:

```python
# BEFORE:
async def single_prompt(
    self,
    prompt: str,
    mode: str = "agent",
    yolo: bool = True,
) -> list[Message]:
    session: Session | None = None
    aggregator: MessageAggregator = MessageAggregator()
    ...
    async for wire_msg in session.prompt(prompt):
        msgs = aggregator.feed(wire_msg)
        messages.extend(msgs)

# AFTER:
async def single_prompt(
    self,
    prompt: str,
    mode: str = "agent",
    yolo: bool = True,
) -> list[dict[str, Any]]:  # Changed return type
    """Execute a single prompt and return messages as dicts."""
    messages: list[dict[str, Any]] = []
    
    try:
        # Use claude-agent-sdk query function
        options = {
            "model": self._config.get("model", "kimi-for-coding"),
            "yolo": yolo,
            "work_dir": str(self._work_dir),
        }
        
        if self._agent_file:
            options["agent_file"] = str(self._agent_file)
        
        async for message in query(prompt=prompt, options=options):
            # Convert SDK message to dict
            msg_dict = self._convert_message_to_dict(message)
            if msg_dict:
                messages.append(msg_dict)
            
            # Check for result
            if isinstance(message, ResultMessage):
                if message.is_error:
                    raise LLMError(f"SDK Error: {message.result}")
                break
        
        return messages
        
    except asyncio.CancelledError:
        self._logger.info("single_prompt_cancelled")
        return []
    except Exception as e:
        self._logger.error("single_prompt_error", error=str(e))
        raise LLMError(f"Single prompt failed: {e}") from e

def _convert_message_to_dict(self, message: Any) -> dict[str, Any] | None:
    """Convert SDK message to dict format."""
    msg_class = message.__class__.__name__
    
    if msg_class == "AssistantMessage":
        content = []
        if hasattr(message, "content"):
            for block in message.content:
                block_type = block.__class__.__name__
                if block_type == "TextBlock":
                    content.append({"type": "text", "text": block.text})
                elif block_type == "ToolUseBlock":
                    content.append({
                        "type": "tool_use",
                        "name": block.name,
                        "input": block.input,
                        "id": block.id,
                    })
        return {"role": "assistant", "content": content}
    
    elif msg_class == "UserMessage":
        return {"role": "user", "content": message.content}
    
    return None
```

**验证**:
```bash
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerSinglePrompt -v
```

---

### Step 7.1: SDK Adapter 迁移

**测试**: `tests/tools/test_sdk_adapter_tdd.py`

**实施**:

```python
# autoBMAD/docuswarm/tools/sdk_adapter.py

# BEFORE:
from kimi_agent_sdk import ToolError, ToolOk, ToolReturnValue

def adapt_to_sdk(result: ToolResult) -> ToolReturnValue:
    if result.success:
        return ToolOk(output=json.dumps(result.result))
    else:
        return ToolError(output="", message=result.error, brief="Tool failed")

# AFTER:
def adapt_to_claude(result: ToolResult) -> dict[str, Any]:
    """Convert ToolResult to Claude SDK format."""
    if result.success:
        return {
            "type": "tool_result",
            "content": result.result if result.result is not None else {},
        }
    else:
        return {
            "type": "tool_result",
            "content": {"error": result.error or "Unknown error"},
            "is_error": True,
        }

def adapt_from_claude(response: dict[str, Any]) -> ToolResult:
    """Convert Claude SDK response to ToolResult."""
    if response.get("is_error"):
        content = response.get("content", {})
        error_msg = content.get("error", "Unknown error") if isinstance(content, dict) else str(content)
        return ToolResult(success=False, error=error_msg)
    
    return ToolResult(success=True, result=response.get("content"))

# Keep old name for backward compatibility during migration
adapt_to_sdk = adapt_to_claude
```

**验证**:
```bash
pytest tests/tools/test_sdk_adapter_tdd.py -v
```

---

### Step 7.2: Callable Tool Wrapper 迁移

**测试**: `tests/tools/test_callable_tool_wrapper_tdd.py`

**实施**:

```python
# autoBMAD/docuswarm/tools/callable_tool_wrapper.py

# BEFORE:
from kimi_agent_sdk import CallableTool2, ToolReturnValue

class ToolResultCallableTool(CallableTool2[P], Generic[P]):
    @override
    async def __call__(self, params: P) -> ToolReturnValue:
        result = await self._execute(params)
        return adapt_to_sdk(result)

# AFTER:
class ToolResultWrapper:
    """Base class for tools using ToolResult internally.
    
    Migration note: Replaces CallableTool2 inheritance with composition.
    """
    
    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute tool and return Claude SDK format."""
        validated_params = self._validate_params(params)
        result = await self._execute(validated_params)
        return adapt_to_claude(result)
    
    def _validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Validate input parameters. Override in subclass."""
        return params
    
    async def _execute(self, params: dict[str, Any]) -> ToolResult:
        """Implement tool logic. Must be overridden."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement _execute()")

# Keep alias for backward compatibility
ToolResultCallableTool = ToolResultWrapper
```

**验证**:
```bash
pytest tests/tools/test_callable_tool_wrapper_tdd.py -v
```

---

### Step 10.1: Independent Agent 迁移

**测试**: `tests/agents/test_independent_agent_tdd.py`

**实施**:

```python
# autoBMAD/docuswarm/agents/independent.py

# BEFORE:
from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator
from kaos.path import KaosPath

# AFTER:
# Removed: kimi_agent_sdk imports
# Removed: kaos.path import
# Using standard dict for messages

class IndependentAgent(BaseAgent):
    """Independent Agent - migrated to claude-agent-sdk."""
    
    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute agent with new SDK."""
        # Implementation uses SessionManager.single_prompt
        # which now returns list[dict] instead of list[Message]
        messages = await self._session_manager.single_prompt(
            prompt=self._build_prompt(input_data),
            mode="agent",
        )
        
        # Process messages as dicts
        return self._process_response(messages)
    
    def _process_response(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Process response messages (now dicts instead of Message objects)."""
        output: dict[str, Any] = {"deliverables": [], "questions": []}
        
        for msg in messages:
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                # Extract text from content blocks
                for block in content:
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        # Parse JSON from text
                        try:
                            parsed = json.loads(text)
                            output.update(parsed)
                        except json.JSONDecodeError:
                            pass
        
        return output
```

**验证**:
```bash
pytest tests/agents/test_independent_agent_tdd.py -v
```

---

## 测试驱动开发循环

### 单个文件迁移流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. RED: 运行测试，确认失败                                  │
│     pytest tests/.../test_X_tdd.py -v                       │
│     # 应该看到 FAILED                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. GREEN: 实现最小代码使测试通过                            │
│     # 修改实现代码                                          │
│     # 不要过度设计                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. VERIFY: 运行测试，确认通过                               │
│     pytest tests/.../test_X_tdd.py -v                       │
│     # 应该看到 PASSED                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. REFACTOR: 重构代码，保持测试通过                         │
│     # 清理代码                                              │
│     # 运行测试确保仍然通过                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. REGRESSION: 运行回归测试                                 │
│     pytest tests/ -v                                        │
│     # 确保没有破坏现有功能                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 常见问题

### Q1: 测试失败但不知道原因

```bash
# 添加详细输出
pytest tests/... -vvs --tb=long

# 使用 pdb
pytest tests/... --pdb

# 只运行特定测试
pytest tests/...::TestClass::test_method -v
```

### Q2: 如何处理复杂依赖

```python
# 使用更大的 mock
@pytest.fixture
def mock_complex_scenario():
    with patch("module.A") as mock_a, \
         patch("module.B") as mock_b:
        mock_a.return_value.method.return_value = "value"
        yield mock_a, mock_b
```

### Q3: 异步测试失败

```python
# 确保使用 pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

---

## 验收清单

### 每个文件迁移完成后检查

- [ ] TDD 测试通过
- [ ] 原始测试通过率未下降
- [ ] 代码审查通过
- [ ] 文档已更新

### 整体迁移完成后检查

- [ ] 所有 TDD 测试通过
- [ ] `python tools/dependency_analysis/migration_tracker.py --check` 通过
- [ ] `python tools/dependency_analysis/dependency_drift_analyzer.py` 显示 Drift Score = 0
- [ ] 完整测试套件通过率 ≥ 95%
- [ ] E2E 测试通过
- [ ] 代码审查通过

---

**最后更新**: 2026-03-25
