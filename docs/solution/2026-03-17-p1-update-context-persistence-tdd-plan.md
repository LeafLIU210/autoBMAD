# P1 Update Context Persistence - 测试驱动方案

> **关联文档**: [研究文档](../research/2026-03-13-p1-update-context-persistence-plan.md)  
> **状态**: 规划中  
> **创建日期**: 2026-03-17

---

## 1. 概述

### 1.1 目标

为 `update_context` 工具实现真正的持久化功能，使其能够将 agent 更新的上下文写入 `pipelines.state_json.shared_context`，并确保后续节点可以读取这些更新。

### 1.2 核心改动范围

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `autoBMAD/docuswarm/tools/update_context.py` | 重写 | 实现真实的持久化逻辑 |
| `autoBMAD/docuswarm/storage/state_manager.py` | 新增方法 | 添加 `update_shared_context()` 方法 |
| `autoBMAD/docuswarm/agents/independent.py` | 修改 | 注入 `pipeline_id` 到工具执行环境 |
| `autoBMAD/docuswarm/nodes/dual_agent.py` | 修改 | 确保工具实例带有 `pipeline_id` |

### 1.3 推荐数据模型

```python
shared_context = {
    "facts": {},           # 关键事实，如 {"market_scope": "enterprise"}
    "decisions": {},       # 已做出的决策
    "open_questions": [],  # 待解决问题列表
    "doc_summaries": {},   # 文档摘要
    "notes": []            # 一般性笔记
}
```

---

## 2. 测试策略

### 2.1 测试分层

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3: E2E / 回归测试                                 │
│  - 完整 pipeline 执行验证                                │
│  - 现有功能不受影响                                      │
├─────────────────────────────────────────────────────────┤
│  Layer 2: 集成测试                                       │
│  - Node A 写入 → Node B 读取                             │
│  - 数据库持久化验证                                      │
├─────────────────────────────────────────────────────────┤
│  Layer 1: 单元测试 (核心)                                │
│  - update_context 工具逻辑                               │
│  - StateManager 新方法                                   │
│  - 白名单验证                                            │
└─────────────────────────────────────────────────────────┘
```

### 2.2 测试优先级

1. **P0 - 阻塞**: 核心单元测试（必须首先通过）
2. **P1 - 高**: 集成测试（验证跨节点数据流）
3. **P2 - 中**: 回归测试（确保不破坏现有功能）

---

## 3. 详细测试用例

### 3.1 单元测试 - `tests/unit/tools/test_update_context_persistence.py`

#### 3.1.1 `TestUpdateContextValidation` - 参数验证

```python
class TestUpdateContextValidation:
    """验证 key 白名单和操作类型"""
    
    @pytest.mark.parametrize("valid_key", [
        "facts.test_key",
        "decisions.output_mode", 
        "open_questions",
        "doc_summaries.overview",
        "notes",
    ])
    async def test_valid_key_patterns_accepted(self, valid_key):
        """TC-V01: 白名单内的 key 应该被接受"""
        
    @pytest.mark.parametrize("invalid_key", [
        "subject_context",
        "deliverables.node_1",
        "evaluations.score",
        "shared_context.facts",  # 不允许嵌套 shared_context
        "unknown_namespace.key",
    ])
    async def test_invalid_key_patterns_rejected(self, invalid_key):
        """TC-V02: 白名单外的 key 应该被拒绝并返回错误"""
        
    @pytest.mark.parametrize("operation", ["set", "append", "remove"])
    async def test_valid_operations_accepted(self, operation):
        """TC-V03: 有效的操作类型应该被接受"""
        
    async def test_invalid_operation_rejected(self):
        """TC-V04: 无效的操作类型应该被拒绝"""
```

#### 3.1.2 `TestUpdateContextOperations` - 核心操作

```python
class TestUpdateContextOperations:
    """测试 set/append/remove 三种操作"""
    
    async def test_set_operation_creates_new_value(self, mock_state_manager):
        """TC-O01: set 操作应该创建新值
        
        Given:
            - pipeline_id: "test-pipeline-001"
            - key: "facts.market_scope"
            - value: "enterprise"
            - operation: "set"
        When:
            - 调用 update_context
        Then:
            - state_manager.update_shared_context 被调用
            - 数据库中 state_json.shared_context.facts.market_scope = "enterprise"
        """
        
    async def test_set_operation_updates_existing_value(self, mock_state_manager):
        """TC-O02: set 操作应该更新已存在的值"""
        
    async def test_append_operation_to_new_list(self, mock_state_manager):
        """TC-O03: append 到不存在的 key 应该创建新列表
        
        Given:
            - key: "open_questions" (初始不存在)
            - value: {"question": "What is the scope?", "priority": "blocking"}
            - operation: "append"
        When:
            - 调用 update_context
        Then:
            - 创建列表 [{...}]
        """
        
    async def test_append_operation_to_existing_list(self, mock_state_manager):
        """TC-O04: append 到已存在的列表应该追加元素"""
        
    async def test_append_operation_to_non_list_fails(self, mock_state_manager):
        """TC-O05: append 到非列表类型应该失败并返回错误"""
        
    async def test_remove_operation_deletes_key(self, mock_state_manager):
        """TC-O06: remove 操作应该删除 key
        
        Given:
            - state_json.shared_context.facts.market_scope 存在
        When:
            - remove key="facts.market_scope"
        Then:
            - 该 key 被删除
        """
        
    async def test_remove_operation_from_list(self, mock_state_manager):
        """TC-O07: remove 从列表中移除指定值"""
        
    async def test_remove_nonexistent_key_silently_succeeds(self, mock_state_manager):
        """TC-O08: 删除不存在的 key 应该静默成功"""
```

#### 3.1.3 `TestUpdateContextErrorHandling` - 错误处理

```python
class TestUpdateContextErrorHandling:
    """错误场景处理"""
    
    async def test_missing_pipeline_id_returns_error(self):
        """TC-E01: 缺少 pipeline_id 应该返回错误"""
        
    async def test_nonexistent_pipeline_returns_error(self, mock_state_manager):
        """TC-E02: 不存在的 pipeline_id 应该返回错误"""
        
    async def test_database_error_handled_gracefully(self, mock_state_manager):
        """TC-E03: 数据库错误应该被优雅处理"""
        
    async def test_invalid_json_in_state_handled(self, mock_state_manager):
        """TC-E04: state_json 中无效的 JSON 应该被处理"""
```

#### 3.1.4 `TestUpdateContextToolIntegration` - 工具集成

```python
class TestUpdateContextToolIntegration:
    """UpdateContextTool 与 StateManager 的集成"""
    
    async def test_tool_calls_state_manager_with_correct_params(self):
        """TC-I01: 工具应该使用正确的参数调用 StateManager"""
        
    async def test_tool_returns_success_result(self):
        """TC-I02: 成功时返回 ToolResult(success=True)"""
        
    async def test_tool_returns_metadata_summary(self):
        """TC-I03: 返回包含更新后 metadata 的摘要"""
```

### 3.2 单元测试 - `tests/unit/storage/test_state_manager_shared_context.py`

#### 3.2.1 `TestStateManagerSharedContext` - StateManager 新方法

```python
class TestStateManagerSharedContext:
    """测试 StateManager.update_shared_context() 方法"""
    
    async def test_update_shared_context_creates_namespace(self, temp_db):
        """TC-SM01: 首次更新时创建 shared_context 命名空间
        
        Given:
            - pipeline 存在但 state_json 为空或为 {}
        When:
            - update_shared_context(pipeline_id, {"facts": {"key": "value"}})
        Then:
            - state_json = {"shared_context": {"facts": {"key": "value"}}}
        """
        
    async def test_update_shared_context_merges_nested_dicts(self, temp_db):
        """TC-SM02: 嵌套字典应该被合并而非替换
        
        Given:
            - 现有: {"shared_context": {"facts": {"a": "1"}}}
        When:
            - 更新: {"facts": {"b": "2"}}
        Then:
            - 结果: {"shared_context": {"facts": {"a": "1", "b": "2"}}}
        """
        
    async def test_update_shared_context_preserves_other_keys(self, temp_db):
        """TC-SM03: 更新只影响 shared_context，保留其他顶层 key
        
        Given:
            - 现有: {"subject_context": {...}, "shared_context": {...}}
        When:
            - 更新 shared_context
        Then:
            - subject_context 保持不变
        """
        
    async def test_update_shared_context_atomic_operation(self, temp_db):
        """TC-SM04: 更新应该是原子操作（事务安全）"""
        
    async def test_update_shared_context_returns_true_on_success(self, temp_db):
        """TC-SM05: 成功返回 True"""
        
    async def test_update_shared_context_raises_on_invalid_pipeline(self, temp_db):
        """TC-SM06: 无效 pipeline_id 抛出 StorageError"""
```

### 3.3 集成测试 - `tests/integration/test_shared_context_flow.py`

#### 3.3.1 `TestSharedContextNodeFlow` - 跨节点数据流

```python
class TestSharedContextNodeFlow:
    """验证节点间的共享上下文传递"""
    
    async def test_node_a_writes_node_b_reads(self, test_db, mock_llm):
        """TC-F01: Node A 写入，Node B 能读取
        
        Scenario:
            1. 创建 pipeline
            2. Node A (analyst) 执行，通过 tool 写入 facts.market_scope = "enterprise"
            3. Node B (architect) 执行，从 shared_context 读取该值
        Expected:
            - Node B 的 prompt 包含 "enterprise"
        """
        
    async def test_multiple_tools_update_same_pipeline(self, test_db):
        """TC-F02: 同一 pipeline 中多个 tool 调用累积更新
        
        Scenario:
            1. Tool 1: set facts.a = "1"
            2. Tool 2: set facts.b = "2"
            3. Tool 3: append open_questions = {...}
        Expected:
            - 最终 state_json.shared_context 包含所有更新
        """
        
    async def test_pipeline_isolation_maintained(self, test_db):
        """TC-F03: 不同 pipeline 间的隔离
        
        Given:
            - Pipeline A 和 Pipeline B 同时运行
        When:
            - Pipeline A 更新 shared_context
        Then:
            - Pipeline B 不受影响
        """
```

### 3.4 回归测试 - `tests/regression/test_update_context_no_regression.py`

```python
class TestUpdateContextNoRegression:
    """确保不破坏现有功能"""
    
    async def test_existing_pipeline_creation_unaffected(self):
        """TC-R01: 现有 pipeline 创建流程不受影响"""
        
    async def test_existing_node_result_saving_unaffected(self):
        """TC-R02: 现有 node result 保存不受影响"""
        
    async def test_existing_subject_context_operations_unaffected(self):
        """TC-R03: 现有的 subject_context 操作不受影响"""
        
    async def test_update_context_backward_compatible(self):
        """TC-R04: 工具接口保持向后兼容
        
        - 参数格式不变
        - 返回值格式不变
        - 旧代码无需修改即可工作
        """
```

---

## 4. 测试基础设施

### 4.1 新增 Fixtures

```python
# tests/conftest.py (新增)

@pytest.fixture
def temp_db(tmp_path):
    """创建临时数据库用于测试"""
    from autoBMAD.docuswarm.storage.database import DatabaseManager
    db_path = tmp_path / "test.db"
    db = DatabaseManager.get_instance(db_path)
    yield db
    DatabaseManager.reset_instance()

@pytest.fixture
def mock_state_manager(temp_db):
    """创建带有 mock 的 StateManager"""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    sm = StateManager(db_path=str(temp_db.db_path))
    return sm

@pytest.fixture
def sample_pipeline(mock_state_manager):
    """创建示例 pipeline 用于测试"""
    pipeline_id = mock_state_manager.create_pipeline(
        subject="Test Subject",
        subject_context={"task": "test task"}
    )
    return pipeline_id

@pytest.fixture
def update_context_tool(mock_state_manager, sample_pipeline):
    """创建已注入 pipeline_id 的 UpdateContextTool 实例"""
    from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
    tool = UpdateContextTool(
        state_manager=mock_state_manager,
        pipeline_id=sample_pipeline
    )
    return tool
```

### 4.2 测试数据工厂

```python
# tests/factories/shared_context_factory.py

class SharedContextFactory:
    """创建测试用的 shared_context 数据"""
    
    @staticmethod
    def create_facts(**kwargs):
        return {
            "market_scope": kwargs.get("market_scope", "enterprise"),
            "target_audience": kwargs.get("target_audience", "technical"),
            **kwargs
        }
    
    @staticmethod
    def create_open_question(text="Test question?", priority="clarifying"):
        return {
            "question": text,
            "priority": priority,
            "context": "Test context"
        }
```

---

## 5. 实现步骤（TDD 循环）

### Phase 1: 编写失败测试

```bash
# 1. 创建测试文件框架
touch tests/unit/tools/test_update_context_persistence.py
touch tests/unit/storage/test_state_manager_shared_context.py

# 2. 运行测试（预期全部失败）
pytest tests/unit/tools/test_update_context_persistence.py -v --tb=short
pytest tests/unit/storage/test_state_manager_shared_context.py -v --tb=short
```

### Phase 2: StateManager 实现

```python
# autoBMAD/docuswarm/storage/state_manager.py

async def update_shared_context(
    self,
    pipeline_id: str,
    update: dict[str, Any],
    operation: str = "set",
    key_path: str | None = None,
) -> bool:
    """Update shared_context within state_json.
    
    Args:
        pipeline_id: The pipeline to update
        update: The value to set/append/remove
        operation: One of "set", "append", "remove"
        key_path: Dot-separated path like "facts.market_scope"
    
    Returns:
        True if successful
    """
    # Implementation here
```

**验证**:
```bash
pytest tests/unit/storage/test_state_manager_shared_context.py -v
```

### Phase 3: UpdateContextTool 实现

```python
# autoBMAD/docuswarm/tools/update_context.py

class UpdateContextTool(CallableTool2[UpdateContextParams]):
    """Tool for updating shared context with persistence."""
    
    def __init__(
        self,
        state_manager: StateManager | None = None,
        pipeline_id: str | None = None,
    ) -> None:
        self._state_manager = state_manager
        self._pipeline_id = pipeline_id
        
    # ... implementation
```

**验证**:
```bash
pytest tests/unit/tools/test_update_context_persistence.py -v
```

### Phase 4: Agent/Node 集成

修改 `independent.py` 和 `dual_agent.py` 以注入 `pipeline_id`。

**验证**:
```bash
pytest tests/integration/test_shared_context_flow.py -v
```

### Phase 5: 回归测试

```bash
pytest tests/regression/test_update_context_no_regression.py -v
pytest tests/ -k "not slow" --tb=short
```

---

## 6. 验收检查清单

- [ ] **功能验收**
  - [ ] `update_context` 可真实写入 `pipelines.state_json.shared_context`
  - [ ] 下一节点运行时能读到前一节点写入的共享上下文
  - [ ] 非白名单路径会被拒绝
  - [ ] 每次更新都有日志记录

- [ ] **测试覆盖**
  - [ ] 单元测试覆盖率 > 90%
  - [ ] 所有边界情况有测试
  - [ ] 集成测试通过
  - [ ] 回归测试通过

- [ ] **质量验收**
  - [ ] 代码通过 `ruff check`
  - [ ] 代码通过 `mypy` 类型检查
  - [ ] 新增代码有 docstring

---

## 7. 附录

### 7.1 白名单配置

```python
# autoBMAD/docuswarm/tools/update_context.py

ALLOWED_KEY_PREFIXES = [
    "facts.",
    "decisions.",
    "open_questions",
    "doc_summaries.",
    "notes",
]

ALLOWED_LIST_KEYS = [
    "open_questions",
    "notes",
]
```

### 7.2 错误代码定义

```python
class UpdateContextErrorCode:
    INVALID_KEY = "INVALID_KEY"
    INVALID_OPERATION = "INVALID_OPERATION"
    MISSING_PIPELINE_ID = "MISSING_PIPELINE_ID"
    PIPELINE_NOT_FOUND = "PIPELINE_NOT_FOUND"
    TYPE_ERROR = "TYPE_ERROR"  # e.g., append to non-list
    DATABASE_ERROR = "DATABASE_ERROR"
```

### 7.3 相关文件索引

| 文件路径 | 类型 | 相关性 |
|----------|------|--------|
| `autoBMAD/docuswarm/tools/update_context.py` | 源文件 | 核心实现 |
| `autoBMAD/docuswarm/storage/state_manager.py` | 源文件 | 持久化层 |
| `autoBMAD/docuswarm/agents/independent.py` | 源文件 | 工具注入 |
| `autoBMAD/docuswarm/nodes/dual_agent.py` | 源文件 | 工具实例化 |
| `tests/unit/tools/test_update_context.py` | 现有测试 | 向后兼容 |
| `tests/conftest.py` | 测试配置 | fixtures |
