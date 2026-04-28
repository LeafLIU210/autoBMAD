# Epic 19: Test Dependency Migration

> **⚠️ 完全移除**: 本 Epic 完全移除 `kimi-agent-sdk` mock，使用统一测试框架  
> **决策**: 零向后兼容，移除全局 autouse mock，使用标准 Python mock  
> **参考**: [测试依赖迁移研究报告](../research/migration/03-test-dependency-migration-report.md)

**Epic ID**: EPIC-19  
**Version**: 1.0 (完全移除版)  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 2 (Kimi SDK Removal)

---

## 1. Epic Overview

### 1.1 Summary

**完全移除** `kimi-agent-sdk` 的测试 mock，将 DocuSwarm 测试套件从 Kimi SDK mock 迁移到标准 Python mock。包括移除 `conftest.py` 中的全局 `autouse` mock，重写测试文件使用标准 mock。

### 1.2 Business Value

- **完全移除 Kimi SDK**: 消除对 `kimi_agent_sdk` mock 的依赖
- **简化测试**: 标准 Python mock 更易于理解和维护
- **提高可靠性**: 移除全局 mock 避免副作用
- **加快测试**: 减少不必要的 mock 层

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 全局 mock 移除 | `conftest.py` 无 `autouse=True` mock |
| 测试文件更新 | 所有 19 个测试文件更新 |
| 测试通过率 | 100% |
| 代码覆盖率 | ≥80% |

### 1.4 Dependencies

- **Requires**: Epic 17 (Message Format), Epic 18 (Tool Migration) completed
- **Blocks**: Epic 20 (Exception Migration)

---

## 2. Architecture Context

### 2.1 Migration Overview

```
Before (v4.x - 迁移中):
  ┌─────────────────────────────────────────────────────────────┐
  │  conftest.py                                                │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ @pytest.fixture(autouse=True)                      │   │
  │  │ def mock_kimi_sdk():                               │   │
  │  │     with patch.dict("sys.modules", {...}):         │   │
  │  │         # 全局 mock 影响所有测试                   │   │
  │  │         yield                                        │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  问题:                                                      │
  │  - autouse=True 强制应用到所有测试                         │
  │  - MagicMock 导致类型检查失效                              │
  │  - 与 SessionManager 实际实现冲突                          │
  └─────────────────────────────────────────────────────────────┘

After (v5.0 - 完全移除):
  ┌─────────────────────────────────────────────────────────────┐
  │  标准 Python mock                                           │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ @pytest.fixture                                    │   │
  │  │ def mock_sdk_result():                             │   │
  │  │     return MockSDKResult(...)                      │   │
  │  │                                                    │   │
  │  │ @pytest.fixture                                    │   │
  │  │ def mock_session_manager():                        │   │
  │  │     return AsyncMock(...)                          │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  优势:                                                      │
  │  - 按需使用，无副作用                                      │
  │  - 类型清晰，易于维护                                      │
  │  - 与实际代码行为一致                                      │
  └─────────────────────────────────────────────────────────────┘
```

### 2.2 Test Files Affected

| 测试文件 | Mock 类型 | 操作 |
|---------|----------|------|
| `conftest.py` | 全局 | **完全重写** |
| `test_session_manager.py` | 局部 | **完全重写** |
| `test_independent_agent_refactor.py` | 局部 | **完全重写** |
| `test_tool_result_extractor.py` | 无/数据 | **更新格式** |
| `test_orchestrator_*.py` (3个) | 混合 | **重写** |
| 其他单元测试 | 局部 | **更新** |

---

## 3. User Stories

### Story 19.1: Conftest.py Refactoring

**ID**: US-19.1  
**As a** developer  
**I want to** remove global Kimi SDK mock from conftest.py  
**So that** tests use standard Python mock

**Acceptance Criteria**:
- [ ] 移除 `mock_kimi_sdk` fixture 的 `autouse=True`
- [ ] 移除 `kimi_agent_sdk` 模块 mock
- [ ] 创建简单的 `mock_sdk_result` fixture
- [ ] 创建 `mock_session_manager` fixture
- [ ] 创建 `mock_deliverable_message` fixture

**Technical Tasks**:
1. 备份 `conftest.py`
2. 移除全局 Kimi mock
3. 创建新的简单 fixtures
4. 更新所有测试文件
5. 验证所有测试通过

**Before/After**:

```python
# BEFORE: 完全移除

@pytest.fixture(autouse=True)
def mock_kimi_sdk():
    """全局自动 mock kimi-agent-sdk - 将被完全移除"""
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

```python
# AFTER: 新实现

# ============ 简单 Fixtures ============

@pytest.fixture
def mock_sdk_result():
    """SDK 执行结果 mock。"""
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
    """SessionManager mock - 返回标准格式。"""
    manager = AsyncMock()
    
    # 返回 dict 列表而非 Message 对象
    manager.single_prompt.return_value = [
        {"role": "assistant", "content": "Mock response"}
    ]
    
    return manager


@pytest.fixture
def mock_deliverable_message():
    """包含交付物工具调用的消息。"""
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

**Definition of Done**:
- `conftest.py` 无全局 Kimi mock
- 新的 fixtures 可用
- 所有测试通过

---

### Story 19.2: Mock Data Classes Creation

**ID**: US-19.2  
**As a** developer  
**I want to** create simple mock data classes  
**So that** tests can use them for data setup

**Acceptance Criteria**:
- [ ] 创建 `MockSDKResult` dataclass
- [ ] 创建 `MockMessage` dataclass
- [ ] 支持工具调用提取
- [ ] 支持 JSON 序列化

**Technical Tasks**:
1. 创建 `tests/mocks.py`
2. 定义 mock dataclasses
3. 添加辅助方法
4. 编写单元测试

**Implementation**:

```python
# tests/mocks.py

"""简单 mock 数据类 - 无 SDK 依赖。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MockSDKResult:
    """SDK 结果 mock。"""
    success: bool = True
    content: str | None = None
    error: str | None = None
    duration: float = 0.1
    messages: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class MockMessage:
    """消息 mock。"""
    role: str = "assistant"
    content: str | list[dict[str, Any]] = ""
    
    def get_tool_calls(self) -> list[dict[str, Any]]:
        """获取工具调用。"""
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


# 预定义的 mock 数据

MOCK_DELIVERABLE_MESSAGE = {
    "role": "assistant",
    "content": [
        {"type": "text", "text": "Creating deliverable"},
        {
            "type": "tool_use",
            "name": "create_deliverable",
            "input": {
                "title": "Test Deliverable",
                "content": "# Test Content"
            },
            "id": "call_123"
        }
    ]
}

MOCK_EVALUATION_RESPONSE = {
    "role": "assistant",
    "content": """{
        "criterion_scores": {"completeness": 0.8, "clarity": 0.9},
        "alignment_score": 0.85,
        "verdict": "APPROVED",
        "issues_found": [],
        "suggestions": []
    }"""
}
```

**Definition of Done**:
- `tests/mocks.py` 创建完成
- 所有 mock 类可用
- 单元测试通过

---

### Story 19.3: SessionManager Tests Update

**ID**: US-19.3  
**As a** developer  
**I want to** update SessionManager tests to use standard mock  
**So that** they don't depend on Kimi SDK mock

**Acceptance Criteria**:
- [ ] 移除 Kimi SDK mock 导入
- [ ] 使用 `AsyncMock` 替代 Session mock
- [ ] 使用 `mock_sdk_wrapper` fixture
- [ ] 验证返回格式为 dict

**Technical Tasks**:
1. 修改 `tests/unit/test_session_manager.py`
2. 更新所有测试用例
3. 使用新的 fixtures
4. 验证测试通过

**Before/After**:

```python
# BEFORE: 完全移除

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

**Definition of Done**:
- SessionManager 测试使用标准 mock
- 所有测试通过
- 代码覆盖率保持

---

### Story 19.4: IndependentAgent Tests Update

**ID**: US-19.4  
**As a** developer  
**I want to** update IndependentAgent tests to use standard mock  
**So that** they don't depend on Kimi SDK mock

**Acceptance Criteria**:
- [ ] 移除 Kimi SDK mock 导入
- [ ] 使用 `mock_session_manager` fixture
- [ ] 验证 dict 格式消息处理
- [ ] 验证工具调用提取

**Technical Tasks**:
1. 修改 `tests/unit/test_independent_agent_refactor.py`
2. 更新所有测试用例
3. 使用新的 fixtures
4. 验证测试通过

**Before/After**:

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

**Definition of Done**:
- IndependentAgent 测试使用标准 mock
- 所有测试通过
- 代码覆盖率保持

---

### Story 19.5: Remaining Test Files Update

**ID**: US-19.5  
**As a** developer  
**I want to** update remaining test files to use standard mock  
**So that** no test depends on Kimi SDK mock

**Acceptance Criteria**:
- [ ] `test_tool_result_extractor.py` 更新格式
- [ ] `test_orchestrator_*.py` 更新 mock
- [ ] 其他单元测试更新
- [ ] 集成测试更新

**Technical Tasks**:
1. 更新 `tests/unit/test_tool_result_extractor.py`
2. 更新 `tests/unit/test_orchestrator_*.py`
3. 更新其他单元测试
4. 更新集成测试
5. 运行完整测试套件

**Implementation Pattern**:

```python
# 所有测试遵循相同模式

# 1. 移除 Kimi SDK mock 导入
# 2. 使用标准 Python mock
from unittest.mock import AsyncMock, MagicMock, patch

# 3. 使用简单的 fixtures
@pytest.fixture
def mock_sdk_wrapper():
    wrapper = AsyncMock()
    wrapper.execute.return_value = MockSDKResult(
        success=True,
        content="Mock response",
        messages=[]
    )
    return wrapper

# 4. 测试使用标准 mock
@pytest.mark.asyncio
async def test_function(mock_sdk_wrapper):
    result = await some_function()
    assert result.success is True
```

**Definition of Done**:
- 所有测试文件更新
- 完整测试套件通过
- 代码覆盖率 ≥80%

---

## 4. Technical Specifications

### 4.1 New Files

| File | Location | Purpose |
|------|----------|---------|
| `mocks.py` | `tests/mocks.py` | Mock 数据类 |

### 4.2 Modified Files

| File | Location | Changes |
|------|----------|---------|
| `conftest.py` | `tests/conftest.py` | 移除全局 mock |
| `test_session_manager.py` | `tests/unit/` | 使用标准 mock |
| `test_independent_agent_refactor.py` | `tests/unit/` | 使用标准 mock |
| `test_tool_result_extractor.py` | `tests/unit/` | 更新格式 |
| `test_orchestrator_*.py` | `tests/unit/` | 更新 mock |

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Unit tests | `pytest tests/unit/ -v` | 100% pass |
| Integration tests | `pytest tests/integration/ -v` | 100% pass |
| Coverage | `pytest --cov=autoBMAD` | ≥80% |
| Test time | `pytest tests/` | ≤5 min |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Mock 行为不一致 | 中 | 高 | 严格验证 mock 行为 |
| 测试覆盖率下降 | 中 | 高 | 增加测试用例 |
| 测试失败 | 高 | 中 | 逐步运行测试，修复失败用例 |
| 开发人员混淆 | 低 | 低 | 文档更新 |

---

## 6. Definition of Done (Epic Level)

- [ ] 所有 Story 完成并测试通过
- [ ] `conftest.py` 无全局 Kimi mock
- [ ] `autouse=True` 的 `mock_kimi_sdk` fixture 已移除
- [ ] 新的 `tests/mocks.py` 创建完成
- [ ] 所有 19 个测试文件更新
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码覆盖率 ≥80%
- [ ] 测试执行时间 ≤5 min

---

## 7. References

| Document | Location |
|----------|----------|
| 测试依赖迁移报告 | `docs/research/migration/03-test-dependency-migration-report.md` |
| Epic 17 Message 迁移 | `docs/epics/EPIC-17-MESSAGE-FORMAT-MIGRATION.md` |
| Epic 18 Tool 迁移 | `docs/epics/EPIC-18-TOOL-CALLING-MIGRATION.md` |
| Pytest 文档 | https://docs.pytest.org/ |

---

**Epic End**
