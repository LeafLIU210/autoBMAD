# Finding 1-5 实施指南

**文档目的**: 提供详细的代码级实施步骤，用于修复 Finding 1-5  
**目标读者**: 开发人员  
**前提条件**: 已阅读 `2026-03-29-finding-1-2-3-4-5-deep-research-report.md`

---

## 阶段 0: 紧急修复（P0）- Finding 1 & 2

### 任务 1: 修复 ContextValidator（Finding 1）

**文件**: `autoBMAD/docuswarm/context/validator.py`

#### 步骤 1.1: 修改 `__init__` 方法

```python
# BEFORE (约 line 200-250)
class ContextValidator:
    def __init__(
        self,
        session_manager: KimiSessionManager | None = None,
        llm_validation_strategy: LLMContextValidationStrategy | None = None,
    ) -> None:
        self._session_manager = session_manager
        self._llm_validation_strategy = llm_validation_strategy
        if self._llm_validation_strategy is None and session_manager is not None:
            self._llm_validation_strategy = LLMContextValidationStrategy(
                session_manager=session_manager
            )
        # ... backward compatibility code ...

# AFTER
class ContextValidator:
    def __init__(self) -> None:
        """Initialize ContextValidator.
        
        Note: session_manager is no longer stored in the validator.
        It must be passed to validate_context_with_llm().
        """
        self._validation_registry = ValidationRuleRegistry()
        self._load_default_rules()
```

#### 步骤 1.2: 修改 `validate_context_with_llm` 方法

```python
# BEFORE (约 line 1510-1544)
async def validate_context_with_llm(
    self,
    subject_context: dict[str, Any],
    node_id: str = "context_validation",
) -> ValidationResult:
    """Validate context using LLM."""
    if self._session_manager is None or self._llm_validation_strategy is None:
        raise RuntimeError("session_manager is required for LLM validation")
    
    config = {"session_manager": self._session_manager}
    result = await self._llm_validation_strategy.validate(subject_context, config)
    # ...

# AFTER
async def validate_context_with_llm(
    self,
    subject_context: dict[str, Any],
    session_manager: KimiSessionManager,
    node_id: str = "context_validation",
) -> ValidationResult:
    """Validate context using LLM.
    
    Args:
        subject_context: Context to validate
        session_manager: Session manager for LLM calls (required)
        node_id: Node identifier for logging
    
    Returns:
        ValidationResult with validation outcome
    """
    strategy = LLMContextValidationStrategy(session_manager=session_manager)
    config = {"session_manager": session_manager}
    result = await strategy.validate(subject_context, config)
    
    # Add metadata
    result.metadata["node_id"] = node_id
    result.metadata["validation_type"] = "llm_context"
    
    # Raise exception if validation failed
    if not result.valid:
        from autoBMAD.docuswarm.exceptions import ContextValidationError
        error_msg = result.issues[0].message if result.issues else "Context validation failed"
        raise ContextValidationError(error_msg)
    
    return result
```

#### 步骤 1.3: 删除相关实例变量和方法

删除以下实例变量:
- `self._session_manager`
- `self._llm_validation_strategy`

删除或简化相关方法中的 backward compatibility 代码。

### 任务 2: 修复 HybridOrchestrator（Finding 1 & 2）

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

#### 步骤 2.1: 修改 `__init__` 方法

```python
# BEFORE (约 line 90-138)
def __init__(
    self,
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | SqliteSaver | None = None,
    session_manager: KimiSessionManager | None = None,
    work_dir: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    context_validator: ContextValidator | None = None,
) -> None:
    # ...
    self._session_manager = session_manager
    # ...
    # Initialize context validator (injected or created)
    if context_validator is not None:
        self._context_validator = context_validator
    else:
        self._context_validator = ContextValidator(session_manager=session_manager)

# AFTER
def __init__(
    self,
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | SqliteSaver | None = None,
    session_manager: KimiSessionManager | None = None,
    work_dir: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> None:
    """Initialize HybridOrchestrator.
    
    Args:
        db_path: Path to SQLite database
        checkpointer: Optional checkpointer for LangGraph
        session_manager: Optional session manager (will be created if None)
        work_dir: Optional working directory
        api_key: Optional API key
        base_url: Optional API base URL
    """
    self._db_path = db_path or "docuswarm.db"
    self._checkpointer = checkpointer
    self._session_manager = session_manager
    # ... 其他初始化 ...
    
    # Initialize state manager
    self._state_manager = StateManager(db_path=self._db_path)
    
    # Initialize context validator (no session_manager needed)
    self._context_validator = ContextValidator()
```

#### 步骤 2.2: 修改 `start_pipeline` 方法（Finding 1 & 2）

```python
# BEFORE (约 line 301-393)
async def start_pipeline(
    self,
    subject_context: dict,
    pipeline_id: str | None = None,  # ← 删除此参数
) -> str:
    logger.info("starting_pipeline", subject_context=subject_context)
    
    # Step 1: Validate context using LLM
    await self._context_validator.validate_context_with_llm(subject_context)  # ← 在 session_manager 前
    
    # Step 2: Create pipeline in database
    subject = subject_context.get("subject", "Untitled")
    db_pipeline_id = self._state_manager.create_pipeline(...)
    
    # Use provided pipeline_id or generated one  # ← 删除此逻辑
    final_pipeline_id = pipeline_id or db_pipeline_id  # ← 删除此行
    
    # Step 3: Update status
    _ = self._state_manager.update_pipeline_status(
        final_pipeline_id,  # ← 使用 db_pipeline_id
        ...
    )
    
    # Step 4: Create and execute graph
    session_manager = self._get_or_create_session_manager()  # ← 在验证后
    ...

# AFTER
async def start_pipeline(
    self,
    subject_context: dict,
) -> str:
    """Start a new pipeline execution.
    
    Args:
        subject_context: Context information about the subject
    
    Returns:
        The pipeline ID
    """
    logger.info("starting_pipeline", subject_context=subject_context)
    
    # Step 1: Ensure session_manager exists (before validation)
    session_manager = self._get_or_create_session_manager()
    
    # Step 2: Validate context using LLM (with session_manager)
    await self._context_validator.validate_context_with_llm(
        subject_context,
        session_manager=session_manager,
    )
    
    # Step 3: Create pipeline in database
    subject = subject_context.get("subject", "Untitled")
    pipeline_id = self._state_manager.create_pipeline(
        subject=subject,
        subject_context=subject_context,
    )
    
    # Step 4: Update status to running
    _ = self._state_manager.update_pipeline_status(
        pipeline_id,  # 直接使用数据库生成的 ID
        status=RUNNING,
        current_node=PIPELINE_NODES[0],
    )
    
    # ... 其余逻辑保持不变 ...
```

#### 步骤 2.3: 更新所有调用点

**文件**: `autoBMAD/docuswarm/cli/services/pipeline_service.py`

```python
# BEFORE (约 line 53-58)
orchestrator = HybridOrchestrator(
    db_path=db_path,
    work_dir=str(work_dir),
)
pipeline_id = await orchestrator.start_pipeline(
    subject_context,
    pipeline_id=custom_id,  # ← 删除此参数
)

# AFTER
orchestrator = HybridOrchestrator(
    db_path=db_path,
    work_dir=str(work_dir),
)
pipeline_id = await orchestrator.start_pipeline(subject_context)
```

### 任务 3: 验证修复

创建测试文件 `tests/unit/test_finding_1_2_fix.py`:

```python
import pytest
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


@pytest.mark.asyncio
async def test_start_pipeline_without_session_manager():
    """Test that start_pipeline works without explicitly passing session_manager."""
    orchestrator = HybridOrchestrator(db_path=":memory:")
    
    # This should not raise RuntimeError
    # Note: This test requires mocking LLM calls
    with mock.patch.object(
        orchestrator._context_validator,
        'validate_context_with_llm',
        return_value=mock.AsyncMock()
    ):
        pipeline_id = await orchestrator.start_pipeline(
            {"subject": "Test Subject"}
        )
    
    assert pipeline_id is not None
    assert pipeline_id.startswith("pipeline-")


def test_context_validator_no_session_manager_in_init():
    """Test that ContextValidator doesn't require session_manager in init."""
    from autoBMAD.docuswarm.context.validator import ContextValidator
    
    # Should not raise
    validator = ContextValidator()
    
    # validate_context_with_llm should require session_manager parameter
    import inspect
    sig = inspect.signature(validator.validate_context_with_llm)
    assert 'session_manager' in sig.parameters
```

---

## 阶段 1: 主干收敛（P1）- Finding 3

### 任务 4: 删除 nodes/dual_agent.py 中的重复执行器

**文件**: `autoBMAD/docuswarm/nodes/dual_agent.py`

#### 步骤 4.1: 删除执行器函数

删除以下函数（约 line 926-1079，共约 150 行）:

```python
# 删除这些函数
def create_node_executor(node_id: str, session_manager: KimiSessionManager):
    """Delete this function - use node_execution.executor.create_node_executor instead."""
    ...

async def _execute_node(...):
    """Delete this function."""
    ...

def _get_config():
    """Delete this function - use Config.load_config() instead."""
    ...
```

#### 步骤 4.2: 删除 legacy 桥接代码

删除 line 204-249 的 legacy 参数桥接代码。

#### 步骤 4.3: 更新 `__all__`

```python
# BEFORE
__all__ = [
    "NodeResult",
    "create_dual_agent_node",
    "create_node_executor",  # ← 删除
]

# AFTER
__all__ = [
    "NodeResult",
    "create_dual_agent_node",
]
```

### 任务 5: 验证执行路径

确认 `pipeline/graph.py` 使用正确的执行器:

```python
# 应该使用 node_execution/executor.py 的 create_node_executor
from autoBMAD.docuswarm.node_execution.executor import create_node_executor
```

---

## 阶段 1: 主干收敛（P1）- Finding 4

### 任务 6: 统一状态创建

**文件**: `autoBMAD/docuswarm/storage/state_manager.py`

#### 步骤 6.1: 删除 `_create_initial_state`

```python
# 删除整个方法 (line 98-127)
# def _create_initial_state(self, pipeline_id, subject_context):
#     ...
```

#### 步骤 6.2: 导入并使用统一函数

```python
# 在文件顶部添加导入
from autoBMAD.docuswarm.pipeline.state import create_initial_state
```

#### 步骤 6.3: 修改 `create_pipeline`

```python
# BEFORE
def create_pipeline(self, subject, subject_context=None):
    pipeline_id = self._generate_pipeline_id()
    initial_state = self._create_initial_state(pipeline_id, subject_context or {})  # ← 使用本地方法
    state_json = json.dumps(initial_state)
    ...

# AFTER
def create_pipeline(self, subject, subject_context=None):
    pipeline_id = self._generate_pipeline_id()
    initial_state = create_initial_state(pipeline_id, subject_context or {})  # ← 使用统一函数
    state_json = json.dumps(initial_state)
    ...
```

### 任务 7: 统一状态读写

#### 步骤 7.1: 修改 `update_pipeline_status`

```python
# BEFORE (line 239-309)
def update_pipeline_status(self, pipeline_id, status, current_node=None):
    """DEPRECATED: 此方法保留用于向后兼容..."""
    warnings.warn("...", DeprecationWarning)
    
    # 更新顶层列
    with self._db.acquire() as conn:
        conn.execute(
            "UPDATE pipelines SET status = ?, current_node = ? ...",
            (status, current_node, pipeline_id)
        )
    
    # 同步更新 state_json
    self._update_state_json_partial(pipeline_id, {...})

# AFTER - 简化，只更新 state_json
def update_pipeline_status(self, pipeline_id, status, current_node=None) -> bool:
    """Update pipeline status.
    
    Note: Only updates state_json, top-level columns will be deprecated.
    """
    import warnings
    warnings.warn(
        "update_pipeline_status() is deprecated, use update_pipeline_state() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    
    self._validate_status(status)
    
    if not self._pipeline_exists(pipeline_id):
        raise StorageError(f"Pipeline not found: {pipeline_id}")
    
    try:
        with self._db.acquire() as conn:
            # Read current state
            row = conn.execute(
                "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                (pipeline_id,)
            ).fetchone()
            
            if not row:
                return False
            
            # Update state
            state = json.loads(row["state_json"] or "{}")
            state["status"] = status
            if current_node is not None:
                state["current_node"] = current_node
            
            # Write back
            updated_json = json.dumps(state)
            conn.execute(
                "UPDATE pipelines SET state_json = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE pipeline_id = ?",
                (updated_json, pipeline_id)
            )
        
        return True
    except Exception as e:
        raise StorageError(f"Failed to update pipeline status: {e}") from e
```

#### 步骤 7.2: 修改 `get_pipeline` 和 `list_pipelines`

确保两者都从 `state_json` 读取:

```python
def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
    """Get pipeline from state_json."""
    with self._db.acquire() as conn:
        row = conn.execute(
            "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
            (pipeline_id,)
        ).fetchone()
        
        if row and row["state_json"]:
            return json.loads(row["state_json"])
    return None


def list_pipelines(self, status=None, limit=100) -> list[dict[str, Any]]:
    """List pipelines from state_json."""
    with self._db.acquire() as conn:
        rows = conn.execute(
            "SELECT state_json FROM pipelines ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        
        pipelines = []
        for row in rows:
            if row["state_json"]:
                state = json.loads(row["state_json"])
                if status is None or state.get("status") == status:
                    pipelines.append(state)
        return pipelines
```

#### 步骤 7.3: 删除 `_verify_state_consistency`

```python
# 删除整个方法 (line 167-209)
# def _verify_state_consistency(self, pipeline_id):
#     ...
```

---

## 阶段 2: 清理漂移（P1）- Finding 5

### 任务 8: 移除未声明依赖

#### 步骤 8.1: 移除 `kaos.path`

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

```python
# BEFORE (line 15)
from kaos.path import KaosPath

# AFTER
from pathlib import Path
```

检查 `KaosPath` 的使用并替换为 `Path`。

#### 步骤 8.2: 移除 `kimi_agent_sdk` 残留

**文件**: `autoBMAD/docuswarm/llm/approval.py`

```python
# 移除 kimi_agent_sdk 的引用
# 使用 claude-agent-sdk 的对应类型
```

检查并更新 `session_manager.py` 中的残留导入。

### 任务 9: 统一命名

#### 步骤 9.1: 删除别名

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
# BEFORE (line 687-693)
# Backward compatibility alias
KimiSessionManager = SessionManager

# AFTER - 删除这一行
```

#### 步骤 9.2: 更新所有使用

搜索并替换所有 `KimiSessionManager` 为 `SessionManager`:

```bash
# 使用 grep 查找所有使用
grep -r "KimiSessionManager" --include="*.py" autoBMAD/

# 更新以下文件:
# - pipeline/orchestrator.py
# - node_execution/executor.py
# - nodes/dual_agent.py
```

### 任务 10: 删除 Deprecated/Legacy 代码

搜索并删除所有标记代码:

```bash
# 查找 deprecated
grep -rn "deprecated" --include="*.py" autoBMAD/docuswarm/

# 查找 legacy
grep -rn "legacy" --include="*.py" autoBMAD/docuswarm/

# 查找 backward compatibility
grep -rn "backward" --include="*.py" autoBMAD/docuswarm/
```

逐一审查并删除合适的代码。

### 任务 11: 更新依赖声明

**文件**: `pyproject.toml`

```toml
# 确保所有依赖都已声明
# 移除未使用的依赖

[project]
dependencies = [
    "langgraph>=0.2.50,<0.3.0",
    "langgraph-checkpoint-sqlite>=2.0.4,<3.0.0",
    "langchain>=0.3.0,<0.4.0",
    "langchain-core>=0.3.0,<0.4.0",
    "claude-agent-sdk>=0.1.0,<0.2.0",
    # ... 确保没有 kimi-agent-sdk 或 kaos.path
]
```

---

## 测试策略

### 单元测试

每个修改都需要对应的单元测试:

```python
# tests/unit/test_context_validator.py
def test_validate_context_with_llm_requires_session_manager():
    """validate_context_with_llm should require session_manager parameter."""
    validator = ContextValidator()
    
    # Should raise TypeError when session_manager is not provided
    with pytest.raises(TypeError):
        await validator.validate_context_with_llm({})


# tests/unit/test_orchestrator.py
async def test_start_pipeline_generates_consistent_id():
    """Pipeline ID should be consistent between create and update."""
    orchestrator = HybridOrchestrator(db_path=":memory:")
    
    # Mock validation and execution
    with mock.patch(...):
        pipeline_id = await orchestrator.start_pipeline({"subject": "Test"})
    
    # Verify ID format
    assert pipeline_id.startswith("pipeline-")
    
    # Verify can retrieve with same ID
    status = orchestrator.get_pipeline_status(pipeline_id)
    assert status is not None


# tests/unit/test_state_manager.py
def test_state_json_is_single_source_of_truth():
    """All state should come from state_json."""
    sm = StateManager(db_path=":memory:")
    pipeline_id = sm.create_pipeline(subject="Test")
    
    # Update status
    sm.update_pipeline_status(pipeline_id, "running", "analyst")
    
    # Verify get_pipeline returns correct state
    pipeline = sm.get_pipeline(pipeline_id)
    assert pipeline["status"] == "running"
    assert pipeline["current_node"] == "analyst"
    
    # Verify list_pipelines returns same state
    pipelines = sm.list_pipelines()
    assert len(pipelines) == 1
    assert pipelines[0]["status"] == "running"
```

### 集成测试

```python
# tests/integration/test_pipeline_execution.py
async def test_full_pipeline_execution():
    """Test complete pipeline execution with fixes applied."""
    orchestrator = HybridOrchestrator(db_path=":memory:")
    
    # Start pipeline (should work without explicit session_manager)
    pipeline_id = await orchestrator.start_pipeline({
        "subject": "Test Integration",
        "task": "Test task"
    })
    
    # Verify pipeline can be retrieved
    status = await orchestrator.get_pipeline_status(pipeline_id)
    assert status["pipeline_id"] == pipeline_id
```

---

## 回滚计划

如果修复引入严重问题:

1. **立即回滚到上一个稳定版本**
   ```bash
   git revert <commit-hash>
   ```

2. **保留调试信息**
   - 保存日志
   - 记录失败场景

3. **渐进式重新实施**
   - 分更小的 PR 实施
   - 每个 PR 充分测试后再合并

---

## 验收检查清单

### Finding 1
- [ ] `HybridOrchestrator(db_path=":memory:")` 可直接调用 `start_pipeline()` 不报错
- [ ] `ContextValidator` 初始化不再需要 `session_manager` 参数
- [ ] `validate_context_with_llm` 要求传入 `session_manager` 参数

### Finding 2
- [ ] `start_pipeline()` 不再接受 `pipeline_id` 参数
- [ ] 数据库中的 ID 与返回的 ID 始终一致

### Finding 3
- [ ] `nodes/dual_agent.py` 不再包含 `create_node_executor` 等执行器函数
- [ ] `nodes/dual_agent.py` 不再包含 `_get_config` 函数
- [ ] 所有节点执行都通过 `node_execution/executor.py`

### Finding 4
- [ ] 删除 `StateManager._create_initial_state`
- [ ] 统一使用 `pipeline/state.py:create_initial_state`
- [ ] 删除 `_verify_state_consistency` 方法
- [ ] `get_pipeline` 和 `list_pipelines` 返回一致的结果

### Finding 5
- [ ] 无 `kaos.path` 导入
- [ ] 无 `kimi_agent_sdk` 导入
- [ ] 无 `KimiSessionManager` 使用
- [ ] pyproject.toml 声明所有运行时依赖
- [ ] 删除所有 deprecated/legacy 代码
