# DocuSwarm Session 执行失败修复 - 测试驱动方案

**基于研究文档**: `docs/research/session-execution-failure-solution.md`  
**方案日期**: 2026-04-05  
**优先级**: P0（阻断性）  
**目标版本**: 立即修复  

---

## 1. 执行摘要

本方案提供针对 DocuSwarm Session 执行失败问题的完整测试驱动修复计划。该问题导致第二次运行中所有节点出现 `llm_call_error` → `independent_agent_failed` → `node_execution_failed` 失败链。

### 1.1 修复范围

| Bug ID | 问题描述 | 目标文件 | 修复类型 |
|--------|----------|----------|----------|
| BUG-1 | `ClaudeSessionWrapper.prompt()` 调用不存在的 SDK 方法 | `session_manager.py` | 方法替换 |
| BUG-2 | `independent.py` 错误地对异步生成器使用 `await` | `independent.py` | 语法修正 |
| BUG-3 | `ANTHROPIC_MODEL_NAME` 环境变量逻辑需移除 | `session_manager.py` | 逻辑删除 |

### 1.2 测试目标

- **单元测试**: 验证每个修复点的行为符合预期
- **集成测试**: 验证修复后的组件协同工作
- **回归测试**: 确保修复不引入新问题
- **端到端测试**: 验证完整 pipeline 不再出现失败链

---

## 2. 测试策略

### 2.1 测试分层架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: 端到端测试 (E2E)                                │
│  - 完整 Pipeline 运行验证                                 │
│  - 失败链消除验证                                        │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│  Layer 3: 集成测试 (Integration)                         │
│  - SessionManager + ClaudeSessionWrapper                 │
│  - IndependentAgent + SessionManager                     │
│  - 真实 SDK 连接（可选）                                  │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│  Layer 2: 组件测试 (Component)                           │
│  - _create_options() 行为验证                            │
│  - prompt() 异步生成器验证                               │
│  - _call_llm_with_prompts() 调用模式验证                  │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 单元测试 (Unit)                                │
│  - 同步代码逻辑验证                                      │
│  - Mock 依赖验证                                         │
│  - 边界条件测试                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 测试执行顺序

采用 **自底向上** 的测试策略：

1. **Phase 1**: Fix-3 测试（移除 model 字段）- 基础配置变更
2. **Phase 2**: Fix-1 测试（prompt 方法修复）- 核心 SDK 交互
3. **Phase 3**: Fix-2 测试（await 移除）- 调用模式修正
4. **Phase 4**: 集成与回归测试 - 全链路验证

---

## 3. Fix-3 测试方案：移除 ANTHROPIC_MODEL_NAME

### 3.1 测试目标

验证 `_create_options()` 方法：
1. 不再读取 `ANTHROPIC_MODEL_NAME` 环境变量
2. 不再检查 `self._config.model` 属性
3. 返回的 `ClaudeAgentOptions` 中 `model` 字段为 `None`
4. 移除 `import os`（如未在其他地方使用）

### 3.2 测试用例设计

#### TEST-F3-001: _create_options 不读取环境变量

```python
@pytest.mark.parametrize("env_value", ["claude-3-opus", "", None])
def test_create_options_ignores_env_variable(
    monkeypatch, 
    temp_test_dir: Path,
    env_value: str | None
):
    """验证 _create_options 忽略 ANTHROPIC_MODEL_NAME 环境变量"""
    # Arrange
    if env_value is not None:
        monkeypatch.setenv("ANTHROPIC_MODEL_NAME", env_value)
    else:
        monkeypatch.delenv("ANTHROPIC_MODEL_NAME", raising=False)
    
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    sm = SessionManager(work_dir=temp_test_dir)
    
    # Act
    options = sm._create_options(mode="agent", yolo=True)
    
    # Assert
    assert options.model is None, f"model should be None, got {options.model}"
```

#### TEST-F3-002: _create_options 不检查 config.model

```python
def test_create_options_ignores_config_model(temp_test_dir: Path):
    """验证 _create_options 不检查 config.model 属性"""
    # Arrange
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    
    # 创建带有 model 属性的 mock config
    mock_config = Mock()
    mock_config.model = "claude-3-sonnet-20240229"
    
    sm = SessionManager(work_dir=temp_test_dir, config=mock_config)
    
    # Act
    options = sm._create_options(mode="agent", yolo=True)
    
    # Assert - 即使有 model 属性也应该被忽略
    assert options.model is None, f"model should be None even if config has model attr"
```

#### TEST-F3-003: os 导入被移除

```python
def test_os_import_removed():
    """验证 session_manager.py 不再导入 os 模块（如果仅用于 model 逻辑）"""
    import ast
    import inspect
    from autoBMAD.docuswarm.llm import session_manager
    
    source_file = Path(inspect.getfile(session_manager))
    source = source_file.read_text()
    tree = ast.parse(source)
    
    # 检查 import os 是否存在
    os_imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == 'os'
    ]
    
    # 如果 os 仅用于 model 逻辑，应该被移除
    # 如果 os 还有其他用途，则需要保留
    # 此测试作为提醒，需要人工确认 os 的使用情况
    os_usage_count = source.count("os.")
    if os_usage_count == 0:
        assert len(os_imports) == 0, "os import should be removed if not used"
```

### 3.3 实现验证代码

```python
# tests/unit/test_fix3_model_removal.py
"""Fix-3: 移除 ANTHROPIC_MODEL_NAME 相关逻辑的测试"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch


class TestCreateOptionsModelRemoval:
    """测试 _create_options 方法移除 model 相关逻辑"""
    
    def test_create_options_returns_none_model(self, temp_test_dir: Path):
        """TEST-F3-001: _create_options 返回 model=None"""
        # Arrange
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        # Act
        options = sm._create_options(mode="agent", yolo=True)
        
        # Assert
        assert options.model is None
    
    @pytest.mark.parametrize("env_value", [
        "claude-3-opus-20240229",
        "claude-3-5-sonnet",
        "",
    ])
    def test_create_options_ignores_env_with_value(
        self, 
        monkeypatch, 
        temp_test_dir: Path,
        env_value: str
    ):
        """TEST-F3-002: 即使设置环境变量也忽略"""
        # Arrange
        monkeypatch.setenv("ANTHROPIC_MODEL_NAME", env_value)
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        # Act
        options = sm._create_options(mode="agent", yolo=True)
        
        # Assert
        assert options.model is None
    
    def test_create_options_ignores_config_with_model(self, temp_test_dir: Path):
        """TEST-F3-003: 即使 config 有 model 属性也忽略"""
        # Arrange
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        mock_config = Mock(spec=["model"])
        mock_config.model = "claude-3-haiku"
        
        sm = SessionManager(work_dir=temp_test_dir, config=mock_config)
        
        # Act
        options = sm._create_options(mode="agent", yolo=True)
        
        # Assert
        assert options.model is None
    
    def test_create_options_permission_mode_bypass(self, temp_test_dir: Path):
        """TEST-F3-004: yolo=True 时 permission_mode 为 bypassPermissions"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="agent", yolo=True)
        
        assert options.permission_mode == "bypassPermissions"
    
    def test_create_options_permission_mode_default(self, temp_test_dir: Path):
        """TEST-F3-005: yolo=False 时 permission_mode 为 default"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="agent", yolo=False)
        
        assert options.permission_mode == "default"


class TestCreateOptionsBackwardCompatibility:
    """测试 _create_options 保持向后兼容的其他字段"""
    
    def test_create_options_cwd_is_set(self, temp_test_dir: Path):
        """TEST-F3-006: cwd 字段正确设置"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="agent", yolo=True)
        
        assert options.cwd == temp_test_dir
    
    def test_create_options_with_agent_file(self, temp_test_dir: Path):
        """TEST-F3-007: agent_file 正确传递给 options"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        agent_file = temp_test_dir / "agent.yaml"
        agent_file.write_text("test: true")
        
        sm = SessionManager(work_dir=temp_test_dir, agent_file=agent_file)
        options = sm._create_options(mode="agent", yolo=True)
        
        assert options.tools == [str(agent_file)]
    
    def test_create_options_thinking_mode(self, temp_test_dir: Path):
        """TEST-F3-008: thinking 模式正确设置"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="thinking", yolo=True)
        
        assert options.thinking is True
```

---

## 4. Fix-1 测试方案：修复 prompt() 方法

### 4.1 测试目标

验证 `ClaudeSessionWrapper.prompt()` 方法：
1. 使用正确的 SDK API：`query()` 而非 `send_message()`
2. 使用正确的流式 API：`receive_messages()` 而非 `messages()`
3. 是 async generator 而非普通 async function
4. 正确yield消息对象

### 4.2 测试用例设计

#### TEST-F1-001: prompt 使用 query API

```python
@pytest.mark.asyncio
async def test_prompt_uses_query_api(temp_test_dir: Path):
    """验证 prompt() 使用 query() 而非 send_message()"""
    from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
    
    mock_client = AsyncMock()
    mock_client.query = AsyncMock()
    mock_client.receive_messages = Mock(return_value=async_iter(["msg1", "msg2"]))
    
    wrapper = ClaudeSessionWrapper(
        client=mock_client,
        session_id="test-001",
        work_dir=temp_test_dir
    )
    
    # Act
    async for _ in wrapper.prompt("test message"):
        pass
    
    # Assert
    mock_client.query.assert_called_once_with("test message")
    mock_client.send_message.assert_not_called()  # 旧API不应被调用
```

#### TEST-F1-002: prompt 使用 receive_messages

```python
@pytest.mark.asyncio
async def test_prompt_uses_receive_messages(temp_test_dir: Path):
    """验证 prompt() 使用 receive_messages() 而非 messages()"""
    from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
    
    mock_client = AsyncMock()
    mock_client.query = AsyncMock()
    mock_client.receive_messages = Mock(return_value=async_iter([]))
    mock_client.messages = Mock(return_value=async_iter([]))  # 旧API
    
    wrapper = ClaudeSessionWrapper(
        client=mock_client,
        session_id="test-001",
        work_dir=temp_test_dir
    )
    
    async for _ in wrapper.prompt("test"):
        pass
    
    mock_client.receive_messages.assert_called_once()
    mock_client.messages.assert_not_called()  # 旧API不应被调用
```

#### TEST-F1-003: prompt 是 async generator

```python
import inspect

def test_prompt_is_async_generator(temp_test_dir: Path):
    """验证 prompt() 返回 async generator"""
    from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
    
    mock_client = AsyncMock()
    wrapper = ClaudeSessionWrapper(
        client=mock_client,
        session_id="test-001",
        work_dir=temp_test_dir
    )
    
    gen = wrapper.prompt("test")
    
    assert inspect.isasyncgen(gen), "prompt() must return async generator"
    assert not inspect.iscoroutine(gen), "prompt() must not return coroutine"
```

### 4.3 实现验证代码

```python
# tests/unit/test_fix1_prompt_method.py
"""Fix-1: ClaudeSessionWrapper.prompt() 方法修复测试"""

import inspect
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from typing import AsyncIterator


async def async_iter(items: list):
    """辅助函数：创建异步迭代器"""
    for item in items:
        yield item


class TestPromptMethodAPI:
    """测试 prompt() 方法使用正确的 SDK API"""
    
    @pytest.mark.asyncio
    async def test_prompt_calls_query_not_send_message(self, temp_test_dir: Path):
        """TEST-F1-001: prompt() 调用 query() 而非 send_message()"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-001",
            work_dir=temp_test_dir
        )
        
        async for _ in wrapper.prompt("hello world"):
            pass
        
        # 验证使用新API
        mock_client.query.assert_awaited_once_with("hello world")
        # 验证不使用旧API
        mock_client.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_prompt_uses_receive_messages_not_messages(self, temp_test_dir: Path):
        """TEST-F1-002: prompt() 使用 receive_messages() 而非 messages()"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        mock_client.messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-002",
            work_dir=temp_test_dir
        )
        
        async for _ in wrapper.prompt("test"):
            pass
        
        mock_client.receive_messages.assert_called_once()
        mock_client.messages.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_prompt_yields_all_messages(self, temp_test_dir: Path):
        """TEST-F1-003: prompt() 正确 yield 所有消息"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        expected_messages = [
            {"role": "assistant", "content": "Hello"},
            {"role": "assistant", "content": "World"},
        ]
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter(expected_messages))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-003",
            work_dir=temp_test_dir
        )
        
        received = []
        async for msg in wrapper.prompt("test"):
            received.append(msg)
        
        assert received == expected_messages


class TestPromptMethodSignature:
    """测试 prompt() 方法签名和类型"""
    
    def test_prompt_is_async_generator(self, temp_test_dir: Path):
        """TEST-F1-004: prompt() 是 async generator 函数"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = Mock()
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-004",
            work_dir=temp_test_dir
        )
        
        # 调用返回的是 async generator，不是 coroutine
        result = wrapper.prompt("test")
        assert inspect.isasyncgen(result)
        assert not inspect.iscoroutine(result)
    
    def test_prompt_accepts_message_param(self, temp_test_dir: Path):
        """TEST-F1-005: prompt() 接受 message 参数"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = Mock()
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-005",
            work_dir=temp_test_dir
        )
        
        # 验证可以接受消息参数
        gen = wrapper.prompt("test message")
        assert inspect.isasyncgen(gen)


class TestPromptMethodEdgeCases:
    """测试 prompt() 边界情况"""
    
    @pytest.mark.asyncio
    async def test_prompt_with_empty_message(self, temp_test_dir: Path):
        """TEST-F1-006: prompt() 处理空消息"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-006",
            work_dir=temp_test_dir
        )
        
        messages = []
        async for msg in wrapper.prompt(""):
            messages.append(msg)
        
        mock_client.query.assert_awaited_once_with("")
        assert messages == []
    
    @pytest.mark.asyncio
    async def test_prompt_with_large_message(self, temp_test_dir: Path):
        """TEST-F1-007: prompt() 处理大消息"""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        large_message = "x" * 10000
        mock_client = AsyncMock()
        mock_client.receive_messages = Mock(return_value=async_iter([]))
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-007",
            work_dir=temp_test_dir
        )
        
        async for _ in wrapper.prompt(large_message):
            pass
        
        mock_client.query.assert_awaited_once_with(large_message)
```

---

## 5. Fix-2 测试方案：移除 await 前缀

### 5.1 测试目标

验证 `independent.py` 中的 `_call_llm_with_prompts()` 方法：
1. 不再对 `session.prompt()` 使用 `await`
2. 直接使用 `async for` 迭代 `session.prompt()` 的结果
3. 正确处理异步生成器的消息流

### 5.2 测试用例设计

#### TEST-F2-001: 不使用 await 调用 prompt

```python
@pytest.mark.asyncio
async def test_call_llm_no_await_on_prompt(temp_test_dir: Path):
    """验证 _call_llm_with_prompts 不对 session.prompt() 使用 await"""
    from autoBMAD.docuswarm.agents.independent import IndependentAgent
    from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
    
    # 创建一个会检测 await 使用的 mock
    class DetectAwaitMock:
        def __init__(self):
            self._awaited = False
        
        def __await__(self):
            self._awaited = True
            yield from []  # 空生成器
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            raise StopAsyncIteration
    
    mock_session = Mock(spec=ClaudeSessionWrapper)
    mock_prompt_result = DetectAwaitMock()
    mock_session.prompt = Mock(return_value=mock_prompt_result)
    
    # 如果代码使用 await session.prompt()，会触发 __await__
    # 如果代码使用 async for，会触发 __aiter__
```

#### TEST-F2-002: 直接使用 async for

```python
@pytest.mark.asyncio
async def test_call_llm_uses_async_for_directly():
    """验证 _call_llm_with_prompts 直接使用 async for"""
    from autoBMAD.docuswarm.agents.independent import IndependentAgent
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    from autoBMAD.docuswarm.config import Config
    
    # 创建 mock session manager
    mock_sm = AsyncMock(spec=SessionManager)
    mock_session = AsyncMock()
    
    # session.prompt 返回 async generator
    async def mock_prompt(msg):
        yield {"role": "assistant", "content": "test"}
    
    mock_session.prompt = mock_prompt
    mock_sm.create_session = AsyncMock(return_value=mock_session)
    
    # 创建 agent
    config = Config()
    agent = IndependentAgent(
        config=config,
        session_manager=mock_sm,
        node_id="test-node"
    )
    
    # 设置必要的实例变量
    agent._agent_file = temp_test_dir / "agent.yaml"
    agent._work_dir = temp_test_dir
    
    # 调用 - 如果代码有 await session.prompt() 会抛出 TypeError
    messages = await agent._call_llm_with_prompts(
        system_prompt_append="system",
        user_prompt="user"
    )
    
    assert len(messages) > 0
```

### 5.3 实现验证代码

```python
# tests/unit/test_fix2_await_removal.py
"""Fix-2: independent.py await 移除测试"""

import ast
import inspect
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


class TestAwaitRemoval:
    """测试 _call_llm_with_prompts 方法中的 await 移除"""
    
    def test_source_code_no_await_on_prompt(self):
        """TEST-F2-001: 源代码中没有 await session.prompt()"""
        from autoBMAD.docuswarm.agents import independent
        
        source_file = Path(inspect.getfile(independent))
        source = source_file.read_text()
        
        # 检查是否有 await session.prompt 模式
        # 注意：这是一种简单的字符串检查，可能产生假阳性/假阴性
        # 更准确的方法是使用 AST
        lines = source.split('\n')
        for i, line in enumerate(lines, 1):
            if 'await' in line and 'session.prompt' in line:
                # 排除注释行
                stripped = line.strip()
                if not stripped.startswith('#') and not stripped.startswith('//'):
                    pytest.fail(
                        f"Line {i} contains 'await' before 'session.prompt': {line.strip()}"
                    )
    
    def test_source_code_async_for_pattern(self):
        """TEST-F2-002: 源代码使用 async for session.prompt() 模式"""
        from autoBMAD.docuswarm.agents import independent
        
        source_file = Path(inspect.getfile(independent))
        tree = ast.parse(source_file.read_text())
        
        # 查找 _call_llm_with_prompts 函数
        found_async_for = False
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFor):
                # 检查迭代目标是否包含 session.prompt
                iter_str = ast.unparse(node.iter)
                if 'session.prompt' in iter_str:
                    found_async_for = True
                    break
        
        assert found_async_for, "Should find async for session.prompt() pattern"
    
    @pytest.mark.asyncio
    async def test_call_llm_handles_async_generator(self, temp_test_dir: Path):
        """TEST-F2-003: _call_llm_with_prompts 正确处理 async generator"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        # 创建 mock session
        mock_session = AsyncMock()
        
        async def mock_prompt(message: str):
            """模拟 session.prompt 返回 async generator"""
            yield {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]}
            yield {"role": "assistant", "content": [{"type": "text", "text": "World"}]}
        
        mock_session.prompt = mock_prompt
        
        # 创建 mock session manager
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        # 创建 agent
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        # 设置必要的路径
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        # 调用方法 - 如果 await 未移除会抛出 TypeError
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="system prompt",
            user_prompt="user prompt"
        )
        
        assert isinstance(messages, list)
        assert len(messages) == 2
    
    @pytest.mark.asyncio
    async def test_call_llm_no_type_error_on_prompt(self, temp_test_dir: Path):
        """TEST-F2-004: 调用不抛出 TypeError: object async_generator can't be used in 'await' expression"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        mock_session = AsyncMock()
        
        # 模拟返回 async generator（不可 await）
        async def async_gen_func():
            yield {"role": "assistant", "content": "test"}
        
        mock_session.prompt = async_gen_func
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        # 如果 await 未正确移除，这里会抛出 TypeError
        try:
            await agent._call_llm_with_prompts(
                system_prompt_append="system",
                user_prompt="user"
            )
        except TypeError as e:
            if "async_generator" in str(e) and "await" in str(e):
                pytest.fail(f"await not removed from session.prompt() call: {e}")
            raise


class TestMessageCollection:
    """测试消息收集逻辑"""
    
    @pytest.mark.asyncio
    async def test_dict_messages_collected(self, temp_test_dir: Path):
        """TEST-F2-005: dict 类型的消息被正确收集"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        mock_session = AsyncMock()
        
        async def mock_prompt(message: str):
            yield {"role": "assistant", "content": "dict message"}
        
        mock_session.prompt = mock_prompt
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="system",
            user_prompt="user"
        )
        
        assert len(messages) == 1
        assert messages[0]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_object_messages_converted(self, temp_test_dir: Path):
        """TEST-F2-006: 对象类型的消息被转换为 dict"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        class MockMessage:
            def __init__(self, role, content):
                self.role = role
                self.content = content
        
        mock_session = AsyncMock()
        
        async def mock_prompt(message: str):
            yield MockMessage("assistant", [{"type": "text", "text": "hello"}])
        
        mock_session.prompt = mock_prompt
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="system",
            user_prompt="user"
        )
        
        assert len(messages) == 1
        assert isinstance(messages[0], dict)
        assert messages[0]["role"] == "assistant"
        assert messages[0]["content"] == [{"type": "text", "text": "hello"}]
```

---

## 6. 集成测试方案

### 6.1 SessionManager + ClaudeSessionWrapper 集成

```python
# tests/integration/test_session_execution_fix.py
"""Session 执行失败修复的集成测试"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


class TestSessionManagerIntegration:
    """测试 SessionManager 和 ClaudeSessionWrapper 集成"""
    
    @pytest.mark.asyncio
    async def test_create_session_with_fixed_options(self, temp_test_dir: Path):
        """TEST-INT-001: create_session 使用修复后的 _create_options"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(work_dir=temp_test_dir)
        
        # Mock SDK client
        with patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSDKClient') as MockClient:
            mock_client = AsyncMock()
            MockClient.return_value = mock_client
            
            session = await sm.create_session(mode="agent", yolo=True)
            
            # 验证创建的选项没有 model 字段
            call_args = MockClient.call_args
            options = call_args.kwargs.get('options') or call_args[0][0]
            assert options.model is None
    
    @pytest.mark.asyncio
    async def test_session_prompt_integration(self, temp_test_dir: Path):
        """TEST-INT-002: SessionManager 创建的 session 的 prompt 方法工作正常"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(work_dir=temp_test_dir)
        
        with patch('autoBMAD.docuswarm.llm.session_manager.ClaudeSDKClient') as MockClient:
            mock_client = AsyncMock()
            
            async def mock_receive():
                yield {"role": "assistant", "content": "Hello"}
            
            mock_client.receive_messages = Mock(return_value=mock_receive())
            MockClient.return_value = mock_client
            
            session = await sm.create_session(mode="agent", yolo=True)
            
            # 验证 prompt 方法可以迭代
            messages = []
            async for msg in session.prompt("test"):
                messages.append(msg)
            
            assert len(messages) == 1


class TestIndependentAgentIntegration:
    """测试 IndependentAgent 集成"""
    
    @pytest.mark.asyncio
    async def test_agent_uses_correct_prompt_pattern(self, temp_test_dir: Path):
        """TEST-INT-003: IndependentAgent 使用正确的 prompt 调用模式"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        # 设置 persona 目录
        persona_dir = temp_test_dir / "nodes" / "test-node"
        persona_dir.mkdir(parents=True)
        persona_file = persona_dir / "persona.json"
        persona_file.write_text('''
        {
            "name": "Test Analyst",
            "role": "test",
            "identity": {"expertise": ["testing"], "principles": []}
        }
        ''')
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_session = AsyncMock()
        
        async def mock_prompt(msg):
            yield {"role": "assistant", "content": '{"deliverable": {"title": "Test"}, "questions": [], "action": "create_deliverable"}'}
        
        mock_session.prompt = mock_prompt
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        # 创建必要的目录和文件
        agent_file = temp_test_dir / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
        agent_file.parent.mkdir(parents=True)
        agent_file.write_text("tools: []")
        
        output_dir = temp_test_dir / "output" / "test-pipeline"
        output_dir.mkdir(parents=True)
        
        agent._agent_file = agent_file
        agent._work_dir = output_dir
        
        # 执行 - 不应抛出 TypeError
        result = await agent._call_llm_with_prompts(
            system_prompt_append="system",
            user_prompt="user"
        )
        
        assert isinstance(result, list)
```

---

## 7. 回归测试方案

### 7.1 日志模式验证

```python
# tests/regression/test_failure_chain_elimination.py
"""失败链消除回归测试"""

import pytest
import logging
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


class TestFailureChainElimination:
    """验证 llm_call_error -> independent_agent_failed -> node_execution_failed 链被消除"""
    
    @pytest.mark.asyncio
    async def test_no_llm_call_error_logged(self, temp_test_dir: Path, caplog):
        """TEST-REG-001: 不出现 llm_call_error 日志"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        caplog.set_level(logging.WARNING)
        
        # 设置 persona
        persona_dir = temp_test_dir / "nodes" / "test-node"
        persona_dir.mkdir(parents=True)
        persona_file = persona_dir / "persona.json"
        persona_file.write_text('''
        {
            "name": "Test Analyst",
            "role": "test",
            "identity": {"expertise": ["testing"], "principles": []}
        }
        ''')
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_session = AsyncMock()
        
        async def mock_prompt(msg):
            yield {"role": "assistant", "content": "success"}
        
        mock_session.prompt = mock_prompt
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._agent_file.write_text("tools: []")
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True)
        
        try:
            await agent._call_llm_with_prompts(
                system_prompt_append="system",
                user_prompt="user"
            )
        except Exception:
            pass  # 忽略其他错误，只检查日志
        
        # 检查日志中不应出现 llm_call_error
        llm_call_errors = [r for r in caplog.records if "llm_call_error" in r.message]
        assert len(llm_call_errors) == 0, f"Unexpected llm_call_error logs: {llm_call_errors}"
```

---

## 8. 端到端测试方案

### 8.1 Pipeline 完整运行测试

```python
# tests/e2e/test_session_execution_fix_e2e.py
"""Session 执行失败修复的端到端测试"""

import pytest
import asyncio
from pathlib import Path


class TestPipelineExecution:
    """完整 Pipeline 执行测试"""
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('claude_agent_sdk'),
        reason="claude_agent_sdk not available"
    )
    async def test_pipeline_no_execution_failure(self, temp_test_dir: Path):
        """TEST-E2E-001: Pipeline 运行不出现 node_execution_failed"""
        # 此测试需要完整的环境配置
        # 包括：
        # 1. 有效的 claude_agent_sdk
        # 2. 配置好的 API 端点
        # 3. 测试用的 context 文件
        
        # 简化版本：验证关键组件可以正确初始化
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(work_dir=temp_test_dir)
        
        # 验证 _create_options 不产生 model 字段
        options = sm._create_options(mode="agent", yolo=True)
        assert options.model is None
        
        # 验证可以创建 ClaudeSessionWrapper
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        from unittest.mock import AsyncMock
        
        mock_client = AsyncMock()
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-e2e",
            work_dir=temp_test_dir
        )
        
        # 验证 prompt 是 async generator
        import inspect
        gen = wrapper.prompt("test")
        assert inspect.isasyncgen(gen)
```

---

## 9. 测试执行计划

### 9.1 执行顺序

```
Phase 1: 单元测试（Fix-3 优先）
├── TEST-F3-001 ~ TEST-F3-008: model 移除验证
└── 预期结果: 所有测试通过，_create_options 返回 model=None

Phase 2: 单元测试（Fix-1）
├── TEST-F1-001 ~ TEST-F1-007: prompt 方法修复验证
└── 预期结果: 所有测试通过，使用 query() + receive_messages()

Phase 3: 单元测试（Fix-2）
├── TEST-F2-001 ~ TEST-F2-006: await 移除验证
└── 预期结果: 所有测试通过，async for 直接使用 session.prompt()

Phase 4: 集成测试
├── TEST-INT-001 ~ TEST-INT-003: 组件集成验证
└── 预期结果: SessionManager + ClaudeSessionWrapper + IndependentAgent 协同工作

Phase 5: 回归测试
├── TEST-REG-001: 失败链消除验证
└── 预期结果: 不再出现 llm_call_error → independent_agent_failed → node_execution_failed

Phase 6: 端到端测试（可选）
└── TEST-E2E-001: 完整 Pipeline 验证
```

### 9.2 测试命令

```bash
# 运行所有相关测试
pytest tests/unit/test_fix3_model_removal.py -v
pytest tests/unit/test_fix1_prompt_method.py -v
pytest tests/unit/test_fix2_await_removal.py -v
pytest tests/integration/test_session_execution_fix.py -v
pytest tests/regression/test_failure_chain_elimination.py -v

# 运行所有测试并生成报告
pytest tests/unit/test_fix*.py tests/integration/test_session_execution_fix.py -v --tb=short

# 快速验证（仅单元测试）
pytest tests/unit/test_fix*.py -v --tb=line
```

---

## 10. 测试覆盖率要求

| 文件 | 目标覆盖率 | 重点覆盖行 |
|------|-----------|-----------|
| `session_manager.py` | > 90% | _create_options(), ClaudeSessionWrapper.prompt() |
| `independent.py` | > 85% | _call_llm_with_prompts() |

### 覆盖率检查命令

```bash
pytest tests/unit/test_fix*.py --cov=autoBMAD.docuswarm.llm.session_manager --cov=autoBMAD.docuswarm.agents.independent --cov-report=term-missing
```

---

## 11. 验收标准

### 11.1 功能验收

- [ ] Fix-3: `ClaudeAgentOptions.model` 始终为 `None`
- [ ] Fix-1: `ClaudeSessionWrapper.prompt()` 使用 `query()` + `receive_messages()`
- [ ] Fix-2: `independent.py` 中 `session.prompt()` 调用前无 `await`
- [ ] 集成: 所有组件协同工作无错误

### 11.2 测试验收

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码覆盖率达标
- [ ] 回归测试确认失败链消除

### 11.3 日志验证

运行一次 Pipeline 后，验证日志中：

```bash
# 不应出现以下错误日志
grep -i "llm_call_error" logs/*.log && echo "FAIL: llm_call_error found" || echo "PASS"
grep -i "independent_agent_failed" logs/*.log && echo "FAIL: independent_agent_failed found" || echo "PASS"
grep -i "node_execution_failed" logs/*.log && echo "FAIL: node_execution_failed found" || echo "PASS"

# 应出现正常的 session 创建日志
grep -i "session_created" logs/*.log && echo "PASS" || echo "FAIL: session_created not found"
```

---

## 12. 附录

### 12.1 快速参考：修复代码片段

**Fix-3: session_manager.py**
```python
def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
    """Create ClaudeAgentOptions from configuration."""
    # 删除: model 读取逻辑
    permission_mode = "bypassPermissions" if yolo else "default"
    
    options_dict: dict[str, Any] = {
        "cwd": self._work_dir,
        # 删除: "model": model,
        "permission_mode": permission_mode,
    }
    # ...
```

**Fix-1: session_manager.py ClaudeSessionWrapper.prompt()**
```python
async def prompt(self, message: str) -> Any:
    """Send a prompt and yield streaming responses via SDK query API."""
    await self._client.query(message)
    async for msg in self._client.receive_messages():
        yield msg
```

**Fix-2: independent.py _call_llm_with_prompts()**
```python
# 修改前:
async for msg in await session.prompt(user_prompt):

# 修改后:
async for msg in session.prompt(user_prompt):
```

### 12.2 相关文档链接

- 分析报告: `docs/research/session-execution-failure-analysis.md`
- 修复方案: `docs/research/session-execution-failure-solution.md`
- 本测试方案: `docs/solution/2026-04-05-session-execution-failure-tdd-plan.md`
