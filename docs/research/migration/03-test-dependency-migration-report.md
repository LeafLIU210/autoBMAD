# DocuSwarm 测试依赖完全移除报告

> **奥卡姆剃刀原则**: 如无必要，勿增实体  
> **决策**: 完全移除 kimi-agent-sdk mock，使用统一测试框架  
> **研究日期**: 2026-03-02  
> **主题**: 从 kimi-agent-sdk mock 迁移到统一测试框架

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [当前测试依赖分析](#2-当前测试依赖分析)
3. [目标测试架构](#3-目标测试架构)
4. [完全移除方案](#4-完全移除方案)
5. [代码迁移示例](#5-代码迁移示例)
6. [文件修改清单](#6-文件修改清单)
7. [风险评估](#7-风险评估)
8. [测试验证策略](#8-测试验证策略)
9. [结论](#9-结论)

---

## 1. 执行摘要

### 1.1 目标

完全移除 DocuSwarm 项目中测试代码对 `kimi-agent-sdk` 的 mock 依赖。

### 1.2 关键发现

| 维度 | 评估 |
|-----|------|
| **受影响测试文件** | 19 个 |
| **Mock 复杂度** | 🔴 高 - 涉及 Session、Message、Tool 多层 mock |
| **全局配置影响** | `conftest.py` 的 autouse fixture 影响所有测试 |
| **迁移工作量** | 中等 |
| **策略** | **完全移除，无兼容层** |

### 1.3 决策

**不使用兼容层，完全移除**:
- ❌ 不保留 Kimi SDK mock fixtures
- ❌ 不使用 autouse 强制 mock
- ❌ 不提供 UnifiedMock 适配层
- ✅ 使用标准 Python mock
- ✅ 按需创建简单 fixtures
- ✅ 直接测试目标代码

---

## 2. 当前测试依赖分析

### 2.1 全局 Mock 配置（将被移除）

```python
# tests/conftest.py (将被移除的部分)

import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def mock_kimi_sdk():
    """全局自动 mock kimi-agent-sdk - 将被完全移除
    
    此 fixture 的问题：
    1. autouse=True 强制应用到所有测试
    2. 使用 MagicMock 导致类型检查失效
    3. 与 SessionManager 实际实现冲突
    """
    with patch.dict("sys.modules", {"kimi_agent_sdk": MagicMock()}):
        mock_sdk = MagicMock()
        
        # Mock Message 类
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = "Mocked response"
        mock_sdk.Message = mock_message
        
        # Mock Session 类
        mock_session = MagicMock()
        mock_session.id = "mock-session-id"
        mock_sdk.Session = mock_session
        
        # Mock MessageAggregator
        mock_aggregator = MagicMock()
        mock_aggregator.feed.return_value = [mock_message]
        mock_aggregator.flush.return_value = []
        mock_sdk._aggregator.MessageAggregator = mock_aggregator
        
        yield mock_sdk
```

### 2.2 测试文件依赖清单（需要修改）

| 测试文件 | Mock 类型 | 依赖 SDK 组件 | 操作 |
|---------|----------|--------------|------|
| `conftest.py` | 全局 | Session, Message, MessageAggregator | **完全移除** |
| `test_session_manager.py` | 局部 | Session.create, MessageAggregator | **完全重写** |
| `test_independent_agent_refactor.py` | 局部 | Session, Message | **完全重写** |
| `test_tool_result_extractor.py` | 无/数据 | Message content | **更新格式** |
| `test_orchestrator_*.py` | 混合 | SessionManager | **重写** |

---

## 3. 目标测试架构

### 3.1 新 conftest.py 设计

```python
# tests/conftest.py (新方案)

import pytest
from unittest.mock import AsyncMock, MagicMock


# ============ 简单 Fixtures ============

@pytest.fixture
def mock_sdk_result():
    """SDK 执行结果 mock"""
    from autoBMAD.docuswarm.llm.response import SDKResult
    
    return SDKResult(
        success=True,
        content="Mock response",
        error=None,
        duration=0.1,
        messages=[],
        tool_calls=[]
    )


@pytest.fixture
def mock_session_manager():
    """SessionManager mock - 返回标准格式"""
    manager = AsyncMock()
    
    # 返回 dict 列表而非 Message 对象
    manager.single_prompt.return_value = [
        {"role": "assistant", "content": "Mock response"}
    ]
    
    return manager


@pytest.fixture
def mock_deliverable_message():
    """包含交付物工具调用的消息"""
    return {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Creating deliverable"},
            {
                "type": "tool_use",
                "name": "create_deliverable",
                "input": {
                    "title": "Test Deliverable",
                    "content": "Test content"
                },
                "id": "call_123"
            }
        ]
    }
```

### 3.2 Mock 数据类

```python
# tests/mocks.py (新方案)

"""简单 mock 数据类 - 无 SDK 依赖"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MockSDKResult:
    """SDK 结果 mock"""
    success: bool = True
    content: str | None = None
    error: str | None = None
    duration: float = 0.1
    messages: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class MockMessage:
    """消息 mock"""
    role: str = "assistant"
    content: str | list[dict[str, Any]] = ""
    
    def get_tool_calls(self) -> list[dict[str, Any]]:
        """获取工具调用"""
        calls = []
        if isinstance(self.content, list):
            for block in self.content:
                if block.get("type") == "tool_use":
                    calls.append({
                        "name": block.get("name"),
                        "input": block.get("input", {}),
                        "id": block.get("id")
                    })
        return calls
```

---

## 4. 完全移除方案

### 4.1 移除内容清单

**完全移除（无替代）**:
- `autouse=True` 的 `mock_kimi_sdk` fixture
- `kimi_agent_sdk` 模块 mock
- `Message` 类 mock
- `Session` 类 mock
- `MessageAggregator` mock

**新实现**:
- 简单的 `mock_sdk_result` fixture
- 简单的 `mock_session_manager` fixture
- 标准 Python mock 工具

### 4.2 迁移策略

```
迁移路线图
═══════════════════════════════════════════════════════════════════

Phase 1: conftest.py 重构 (Week 1)
────────────────────────────────────────────────────────────────────
□ 移除 autouse 的 kimi_sdk mock
□ 添加简单的 fixtures
□ 编写新 fixtures 的单元测试

Phase 2: 测试文件迁移 (Week 2)
────────────────────────────────────────────────────────────────────
□ test_session_manager.py - 使用标准 mock
□ test_independent_agent_refactor.py - 使用标准 mock
□ test_tool_result_extractor.py - 更新格式
□ test_orchestrator_*.py - 使用标准 mock

Phase 3: 验证 (Week 3)
────────────────────────────────────────────────────────────────────
□ 运行完整测试套件
□ 验证覆盖率
□ 修复失败的测试
```

---

## 5. 代码迁移示例

### 5.1 test_session_manager.py 迁移

```python
# BEFORE: 完全移除

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestKimiSessionManager:
    """使用大量 patch - 将被移除"""
    
    @pytest.mark.asyncio
    async def test_single_prompt(self):
        with patch("autoBMAD.docuswarm.llm.session_manager.Session") as mock_sess:
            with patch("autoBMAD.docuswarm.llm.session_manager.MessageAggregator") as mock_agg:
                mock_instance = AsyncMock()
                mock_instance.prompt.return_value = []
                mock_sess.create.return_value = mock_instance
                
                manager = KimiSessionManager(work_dir=MagicMock())
                result = await manager.single_prompt("test")
                
                assert result is not None
```

```python
# AFTER: 新实现

import pytest
from unittest.mock import AsyncMock, MagicMock

class TestSessionManager:
    """使用标准 mock"""
    
    @pytest.mark.asyncio
    async def test_single_prompt(self, mock_sdk_wrapper):
        """使用简单的 mock fixture"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        manager = SessionManager(work_dir="/tmp/test")
        manager._sdk_wrapper = mock_sdk_wrapper
        
        result = await manager.single_prompt("test")
        
        # 验证返回的是 dict 列表
        assert isinstance(result, list)
        assert all(isinstance(m, dict) for m in result)
```

### 5.2 test_independent_agent.py 迁移

```python
# BEFORE: 完全移除

@pytest.fixture
def mock_session_manager():
    """复杂的 mock 配置 - 将被移除"""
    sm = AsyncMock()
    
    # 需要模拟 Session 和 MessageAggregator
    mock_session = AsyncMock()
    mock_session.prompt = AsyncMock(return_value=[])
    
    sm.create_session.return_value = mock_session
    
    return sm

@pytest.mark.asyncio
async def test_execute(self, mock_session_manager):
    agent = IndependentAgent(
        config=MagicMock(),
        session_manager=mock_session_manager,
        node_id="test"
    )
    # 测试...
```

```python
# AFTER: 新实现

@pytest.fixture
def mock_session_manager_with_deliverable():
    """简洁的 mock - 返回标准格式"""
    manager = AsyncMock()
    
    # 返回 dict 格式消息
    manager.single_prompt.return_value = [
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Creating deliverable"},
                {
                    "type": "tool_use",
                    "name": "create_deliverable",
                    "input": {"title": "Analysis Report", "content": "# Analysis"}
                }
            ]
        },
        {
            "role": "assistant",
            "content": '{"deliverable": {"title": "Analysis Report"}, "questions": []}'
        }
    ]
    
    return manager

@pytest.mark.asyncio
async def test_execute_creates_deliverable(
    self, 
    mock_session_manager_with_deliverable
):
    """测试 Agent 执行"""
    from autoBMAD.docuswarm.agents.independent import IndependentAgent
    
    agent = IndependentAgent(
        config=MagicMock(),
        session_manager=mock_session_manager_with_deliverable,
        node_id="test"
    )
    
    result = await agent.execute({
        "task": "Create analysis",
        "pipeline_id": "test-123",
        "subject_context": {"subject": "test"}
    })
    
    # 验证结果
    assert "deliverable" in result
    assert result["deliverable"]["title"] == "Analysis Report"
```

---

## 6. 文件修改清单

| 优先级 | 文件 | 修改类型 | 预计工作量 |
|-------|------|---------|-----------|
| 🔴 高 | `conftest.py` | 重写 | 2d |
| 🔴 高 | `test_session_manager.py` | 重写 | 2d |
| 🔴 高 | `test_independent_agent_refactor.py` | 重写 | 2d |
| 🟡 中 | `test_tool_result_extractor.py` | 更新 | 1d |
| 🟡 中 | `test_orchestrator_*.py` (3个) | 重写 | 3d |
| 🟢 低 | 其他单元测试 | 更新 | 2d |
| 🟢 低 | 集成测试 | 更新 | 1d |

---

## 7. 风险评估

### 7.1 技术风险矩阵

| 风险项 | 概率 | 影响 | 等级 | 缓解措施 |
|-------|------|------|------|---------|
| Mock 行为不一致 | 中 | 高 | 🔴 高 | 严格验证 mock 行为 |
| 测试覆盖率下降 | 中 | 高 | 🔴 高 | 增加测试用例 |
| 开发人员混淆 | 低 | 低 | 🟢 低 | 文档更新 |

### 7.2 关键风险点

**风险: Mock 行为与实际代码不匹配**

移除全局 mock 后，某些测试可能依赖了 mock 的特定行为。

**缓解**: 逐步运行测试，修复失败的用例。

---

## 8. 测试验证策略

### 8.1 新 Fixtures 测试

```python
# tests/unit/test_fixtures.py

import pytest
from tests.mocks import MockSDKResult, MockMessage


class TestMocks:
    """Mock 类单元测试"""
    
    def test_mock_sdk_result(self):
        """测试 SDKResult mock"""
        result = MockSDKResult(
            success=True,
            content="Test",
            messages=[{"role": "assistant", "content": "Hi"}]
        )
        
        assert result.success is True
        assert result.content == "Test"
        assert len(result.messages) == 1
    
    def test_mock_message_tool_calls(self):
        """测试 Message mock 工具调用"""
        msg = MockMessage(
            role="assistant",
            content=[
                {"type": "tool_use", "name": "test", "input": {"arg": 1}}
            ]
        )
        
        calls = msg.get_tool_calls()
        assert len(calls) == 1
        assert calls[0]["name"] == "test"
```

### 8.2 集成验证

```bash
# 运行完整测试套件
pytest tests/ -v --tb=short

# 验证覆盖率
pytest tests/ --cov=autoBMAD --cov-report=html

# 验证特定模块
coverage report --include="*/docuswarm/*"
```

---

## 9. 结论

### 9.1 结论

1. **测试 mock 依赖是迁移的重要组成部分**：全局 autouse mock 需要完全移除。

2. **标准 mock 足够使用**：不需要创建复杂的 UnifiedMock 层。

3. **迁移需要 2-3 周**：主要是测试文件的重写。

4. **风险可控**：标准 Python mock 更易于理解和维护。

### 9.2 建议

**立即执行**:
1. 重写 `conftest.py`，移除全局 mock
2. 创建简单的 `tests/mocks.py`
3. 逐个更新测试文件
4. 保持测试覆盖率

**监控指标**:
- 测试通过率
- 代码覆盖率
- 测试执行时间

---

*报告完成日期: 2026-03-02*  
*文档版本: 2.0 (完全移除版)*
