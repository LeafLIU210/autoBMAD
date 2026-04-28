# Finding 1-5 测试驱动实施方案（TDD）

**文档版本**: 1.0  
**创建日期**: 2026-03-29  
**依据**: `docs/research/2026-03-29-finding-1-2-3-4-5-deep-research-report.md`  
**方法论**: Red-Green-Refactor TDD  
**核心原则**: 统一重复功能、移除Legacy、移除Deprecated、消除向后兼容

---

## 目录

1. [实施策略概览](#实施策略概览)
2. [Phase 0: 紧急修复 - Finding 1 & 2](#phase-0-紧急修复)
3. [Phase 1: 主干收敛 - Finding 3 & 4](#phase-1-主干收敛)
4. [Phase 2: 清理漂移 - Finding 5](#phase-2-清理漂移)
5. [集成测试方案](#集成测试方案)
6. [验收标准汇总](#验收标准汇总)

---

## 实施策略概览

### TDD 工作流程

每个 Finding 的实施遵循严格的 Red-Green-Refactor 循环：

```
┌─────────────────────────────────────────────────────────────┐
│  Phase N                                                    │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐    │
│  │  RED    │ → │ GREEN   │ → │REFACTOR │ → │ 下一Finding│    │
│  │编写失败测试│   │使测试通过 │   │代码重构  │   │          │    │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 实施顺序

```
Phase 0 (P0) - 必须首先完成
├── Finding 1: Session Manager 初始化 (依赖: 无)
└── Finding 2: Pipeline ID 一致性 (可与F1并行)

Phase 1 (P1) - 主干收敛
├── Finding 3: 统一节点执行器 (依赖: Phase 0)
└── Finding 4: 统一状态模型 (依赖: Phase 0，可与F3并行)

Phase 2 (P1) - 清理漂移
└── Finding 5: 依赖和命名清理 (依赖: Phase 0, 1)
```

### 分支策略

```
main
├── phase0/finding-1-session-manager-fix
├── phase0/finding-2-pipeline-id-fix
├── phase1/finding-3-unify-executor
├── phase1/finding-4-unify-state-model
└── phase2/finding-5-cleanup-drift
```

---

## Phase 0: 紧急修复

### Finding 1: Session Manager 初始化故障 [P0]

#### 问题摘要

`HybridOrchestrator.start_pipeline()` 在未显式注入 `session_manager` 时会先触发 LLM 校验，再直接报错 `RuntimeError: session_manager is required for LLM validation`。

#### RED: 编写失败测试

**测试文件**: `tests/unit/docuswarm/context/test_validator_finding1.py`

```python
"""TDD Tests for Finding 1: Session Manager Initialization Fix."""

import pytest
from unittest.mock import AsyncMock, Mock

from autoBMAD.docuswarm.context.validator import ContextValidator
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestContextValidatorInit:
    """RED Phase: Test ContextValidator initialization without session_manager."""
    
    def test_context_validator_init_does_not_accept_session_manager(self):
        """
        RED: ContextValidator.__init__ should NOT accept session_manager parameter.
        
        After Finding 1 fix, this test should pass by removing the parameter.
        """
        # This should raise TypeError after fix (session_manager param removed)
        with pytest.raises(TypeError):
            ContextValidator(session_manager=Mock(spec=SessionManager))
    
    def test_context_validator_init_without_params_succeeds(self):
        """
        GREEN: ContextValidator should initialize without any parameters.
        
        This is the new expected behavior.
        """
        validator = ContextValidator()
        assert validator is not None
        assert hasattr(validator, '_validation_registry')


class TestValidateContextWithLLM:
    """RED Phase: Test validate_context_with_llm requires session_manager parameter."""
    
    @pytest.mark.asyncio
    async def test_validate_context_with_llm_requires_session_manager_param(self):
        """
        RED: validate_context_with_llm must require session_manager as parameter.
        
        Before fix: Called without session_manager, uses self._session_manager
        After fix: Must pass session_manager explicitly
        """
        validator = ContextValidator()
        
        # Should raise TypeError - missing required session_manager parameter
        with pytest.raises(TypeError) as exc_info:
            await validator.validate_context_with_llm({"subject": "test"})
        
        assert "session_manager" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_validate_context_with_llm_succeeds_with_session_manager(self):
        """
        GREEN: validate_context_with_llm works when session_manager is provided.
        """
        validator = ContextValidator()
        mock_session_manager = Mock(spec=SessionManager)
        
        # Mock the validation strategy
        with pytest.mock.patch(
            'autoBMAD.docuswarm.context.validator.LLMContextValidationStrategy'
        ) as mock_strategy_class:
            mock_strategy = AsyncMock()
            mock_strategy.validate = AsyncMock(return_value=Mock(
                valid=True,
                issues=[],
                metadata={}
            ))
            mock_strategy_class.return_value = mock_strategy
            
            result = await validator.validate_context_with_llm(
                {"subject": "test"},
                session_manager=mock_session_manager
            )
            
            assert result.valid is True
            mock_strategy_class.assert_called_once_with(session_manager=mock_session_manager)


class TestOrchestratorStartup:
    """RED Phase: Test orchestrator can start pipeline without explicit session_manager."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_start_pipeline_without_session_manager(self):
        """
        RED: HybridOrchestrator should work without explicit session_manager in init.
        
        This is the main user-facing fix.
        """
        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        # Mock validation and execution
        with pytest.mock.patch.object(
            orchestrator._context_validator,
            'validate_context_with_llm',
            new_callable=AsyncMock
        ) as mock_validate, \
        pytest.mock.patch(
            'autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph'
        ) as mock_create_graph:
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value={
                "current_node": "po",
                "status": "completed"
            })
            mock_create_graph.return_value = mock_graph
            
            # This should NOT raise RuntimeError after fix
            pipeline_id = await orchestrator.start_pipeline({
                "subject": "Test Subject"
            })
            
            assert pipeline_id is not None
            assert pipeline_id.startswith("pipeline-")
            
            # Verify validate_context_with_llm was called with session_manager
            mock_validate.assert_called_once()
            call_kwargs = mock_validate.call_args
            assert 'session_manager' in call_kwargs.kwargs
```

**测试文件**: `tests/unit/docuswarm/pipeline/test_orchestrator_finding1.py`

```python
"""TDD Tests for Orchestrator Finding 1 Fix."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class TestOrchestratorInit:
    """Test HybridOrchestrator initialization changes."""
    
    def test_orchestrator_init_without_context_validator_param(self):
        """
        RED: HybridOrchestrator should NOT accept context_validator parameter.
        
        This parameter was part of the problematic design.
        """
        from autoBMAD.docuswarm.context.validator import ContextValidator
        
        # After fix, this should raise TypeError
        with pytest.raises(TypeError):
            HybridOrchestrator(
                db_path=":memory:",
                context_validator=ContextValidator()  # Should not be accepted
            )
    
    def test_orchestrator_creates_context_validator_internally(self):
        """
        GREEN: HybridOrchestrator creates ContextValidator internally without params.
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        assert orchestrator._context_validator is not None
        # Should be a ContextValidator instance without session_manager


class TestStartPipelineSessionManagerOrder:
    """Test that session_manager is created before validation."""
    
    @pytest.mark.asyncio
    async def test_session_manager_created_before_validation(self):
        """
        RED: session_manager must be created before calling validate_context_with_llm.
        
        This ensures the fix for the initialization order bug.
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        call_order = []
        
        original_get_or_create = orchestrator._get_or_create_session_manager
        async def tracked_get_or_create():
            call_order.append('get_or_create_session_manager')
            return await original_get_or_create()
        
        original_validate = orchestrator._context_validator.validate_context_with_llm
        async def tracked_validate(*args, **kwargs):
            call_order.append('validate')
            return await original_validate(*args, **kwargs)
        
        orchestrator._get_or_create_session_manager = tracked_get_or_create
        orchestrator._context_validator.validate_context_with_llm = tracked_validate
        
        with patch('autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph') as mock_create:
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value={"current_node": "po"})
            mock_create.return_value = mock_graph
            
            try:
                await orchestrator.start_pipeline({"subject": "test"})
            except:
                pass  # We only care about call order
        
        # Assert correct order
        assert call_order.index('get_or_create_session_manager') < call_order.index('validate')
```

#### GREEN: 实现代码

**Step 1: 修改 ContextValidator**

文件: `autoBMAD/docuswarm/context/validator.py`

```python
# BEFORE
class ContextValidator:
    def __init__(
        self,
        session_manager: KimiSessionManager | None = None,
        llm_validation_strategy: LLMContextValidationStrategy | None = None,
    ) -> None:
        self._session_manager = session_manager
        self._llm_validation_strategy = llm_validation_strategy
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

**Step 2: 修改 validate_context_with_llm 签名**

```python
# BEFORE
async def validate_context_with_llm(
    self,
    subject_context: dict[str, Any],
    node_id: str = "context_validation",
) -> ValidationResult:
    if self._session_manager is None:
        raise RuntimeError("session_manager is required...")
    # ...

# AFTER
async def validate_context_with_llm(
    self,
    subject_context: dict[str, Any],
    session_manager: SessionManager,  # ← 新增必需参数
    node_id: str = "context_validation",
) -> ValidationResult:
    """Validate context using LLM.
    
    Args:
        subject_context: Context to validate
        session_manager: Session manager for LLM calls (required)
        node_id: Node identifier for logging
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

**Step 3: 修改 HybridOrchestrator**

文件: `autoBMAD/docuswarm/pipeline/orchestrator.py`

```python
# BEFORE
class HybridOrchestrator:
    def __init__(
        self,
        db_path: str | None = None,
        checkpointer: BaseCheckpointSaver[Any] | SqliteSaver | None = None,
        session_manager: KimiSessionManager | None = None,
        work_dir: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        context_validator: ContextValidator | None = None,  # ← 删除此参数
    ) -> None:
        # ...
        if context_validator is not None:
            self._context_validator = context_validator
        else:
            self._context_validator = ContextValidator(session_manager=session_manager)

# AFTER
class HybridOrchestrator:
    def __init__(
        self,
        db_path: str | None = None,
        checkpointer: BaseCheckpointSaver[Any] | SqliteSaver | None = None,
        session_manager: KimiSessionManager | None = None,
        work_dir: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize HybridOrchestrator."""
        self._db_path = db_path or "docuswarm.db"
        self._checkpointer = checkpointer
        self._session_manager = session_manager
        
        # ... other init ...
        
        # Initialize context validator (no parameters needed)
        self._context_validator = ContextValidator()
```

**Step 4: 修改 start_pipeline 调用顺序**

```python
# BEFORE
async def start_pipeline(self, subject_context: dict, pipeline_id: str | None = None) -> str:
    # Step 1: Validate (BEFORE session_manager creation - BUG!)
    await self._context_validator.validate_context_with_llm(subject_context)
    
    # ... later ...
    session_manager = self._get_or_create_session_manager()  # ← 创建在验证后

# AFTER
async def start_pipeline(self, subject_context: dict) -> str:
    """Start a new pipeline."""
    logger.info("starting_pipeline", subject_context=subject_context)
    
    # Step 1: Ensure session_manager exists (BEFORE validation)
    session_manager = self._get_or_create_session_manager()
    
    # Step 2: Validate context (with session_manager)
    await self._context_validator.validate_context_with_llm(
        subject_context,
        session_manager=session_manager,  # ← 显式传入
    )
    
    # ... rest of the method
```

#### REFACTOR: 清理遗留代码

1. 删除 `ContextValidator` 中的 `_session_manager` 实例变量
2. 删除 `_llm_validation_strategy` 实例变量
3. 删除所有 backward compatibility 代码块
4. 更新文档字符串

---

### Finding 2: Pipeline ID 一致性 [P0]

#### 问题摘要

自定义 `pipeline_id` 参数从未正常工作，因为数据库写入使用自动生成的 ID，而后续更新可能使用自定义的、不存在的 ID。

#### RED: 编写失败测试

**测试文件**: `tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py`

```python
"""TDD Tests for Finding 2: Pipeline ID Consistency Fix."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestPipelineIdParameter:
    """Test removal of pipeline_id parameter."""
    
    def test_start_pipeline_does_not_accept_pipeline_id_param(self):
        """
        RED: start_pipeline should NOT accept pipeline_id parameter.
        
        This parameter was broken and should be removed.
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        # Should raise TypeError after fix
        with pytest.raises(TypeError):
            orchestrator.start_pipeline(
                {"subject": "test"},
                pipeline_id="custom-id"  # Should not be accepted
            )


class TestPipelineIdConsistency:
    """Test that pipeline_id is consistent throughout the flow."""
    
    @pytest.mark.asyncio
    async def test_created_pipeline_id_matches_returned_id(self):
        """
        RED: The ID returned by start_pipeline must exist in the database.
        
        Before fix: Could return custom_id which doesn't exist in DB
        After fix: Always returns the DB-generated ID
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        with patch.object(
            orchestrator._context_validator,
            'validate_context_with_llm',
            new_callable=AsyncMock
        ), \
        patch('autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph') as mock_create:
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value={
                "current_node": "po",
                "status": "completed"
            })
            mock_create.return_value = mock_graph
            
            pipeline_id = await orchestrator.start_pipeline({
                "subject": "Test Subject"
            })
            
            # Verify ID format (should be auto-generated)
            assert pipeline_id.startswith("pipeline-")
            
            # Verify the ID exists in database
            pipeline = orchestrator._state_manager.get_pipeline(pipeline_id)
            assert pipeline is not None
            assert pipeline["pipeline_id"] == pipeline_id
    
    @pytest.mark.asyncio
    async def test_pipeline_status_update_uses_same_id(self):
        """
        RED: Status updates must use the same ID as the created pipeline.
        
        This tests the core bug in Finding 2.
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        # Track what ID is used for create vs update
        created_ids = []
        updated_ids = []
        
        original_create = orchestrator._state_manager.create_pipeline
        def tracked_create(subject, subject_context=None):
            pipeline_id = original_create(subject, subject_context)
            created_ids.append(pipeline_id)
            return pipeline_id
        
        original_update = orchestrator._state_manager.update_pipeline_status
        def tracked_update(pipeline_id, status, current_node=None):
            updated_ids.append(pipeline_id)
            return original_update(pipeline_id, status, current_node)
        
        orchestrator._state_manager.create_pipeline = tracked_create
        orchestrator._state_manager.update_pipeline_status = tracked_update
        
        with patch.object(
            orchestrator._context_validator,
            'validate_context_with_llm',
            new_callable=AsyncMock
        ), \
        patch('autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph') as mock_create:
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value={"current_node": "po"})
            mock_create.return_value = mock_graph
            
            returned_id = await orchestrator.start_pipeline({
                "subject": "Test"
            })
            
            # Assert all IDs are the same
            assert len(created_ids) == 1
            assert len(updated_ids) >= 1
            assert created_ids[0] == returned_id
            assert all(uid == returned_id for uid in updated_ids)


class TestStateManagerCustomId:
    """Test StateManager custom ID support (if we choose that route)."""
    
    def test_create_pipeline_does_not_accept_custom_id(self):
        """
        RED: StateManager.create_pipeline should NOT accept custom pipeline_id.
        
        We choose to remove custom ID support entirely.
        """
        sm = StateManager(db_path=":memory:")
        
        # Should raise TypeError after fix
        with pytest.raises(TypeError):
            sm.create_pipeline(
                subject="Test",
                pipeline_id="custom-id"  # Should not be accepted
            )
```

#### GREEN: 实现代码

**Step 1: 修改 HybridOrchestrator.start_pipeline 签名**

```python
# BEFORE
async def start_pipeline(
    self,
    subject_context: dict,
    pipeline_id: str | None = None,  # ← 删除此参数
) -> str:

# AFTER
async def start_pipeline(
    self,
    subject_context: dict,
) -> str:
    """Start a new pipeline.
    
    Args:
        subject_context: Context information about the subject
    
    Returns:
        The pipeline ID (auto-generated)
    """
```

**Step 2: 简化 ID 处理逻辑**

```python
# BEFORE
# Step 2: Create pipeline in database
subject = subject_context.get("subject", "Untitled")
db_pipeline_id = self._state_manager.create_pipeline(
    subject=subject,
    subject_context=subject_context,
)

# Use provided pipeline_id or generated one
final_pipeline_id = pipeline_id or db_pipeline_id  # ← 删除此行

# Step 3: Update status to running
_ = self._state_manager.update_pipeline_status(
    final_pipeline_id,  # ← 可能使用不存在的 ID
    status=RUNNING,
    current_node=PIPELINE_NODES[0],
)

# AFTER
# Step 2: Create pipeline in database
subject = subject_context.get("subject", "Untitled")
pipeline_id = self._state_manager.create_pipeline(
    subject=subject,
    subject_context=subject_context,
)  # ← 直接使用返回的 ID

# Step 3: Update status to running
_ = self._state_manager.update_pipeline_status(
    pipeline_id,  # ← 直接使用数据库生成的 ID
    status=RUNNING,
    current_node=PIPELINE_NODES[0],
)

# ... use pipeline_id consistently throughout ...
```

**Step 3: 更新调用点**

文件: `autoBMAD/docuswarm/cli/services/pipeline_service.py`

```python
# BEFORE
pipeline_id = await orchestrator.start_pipeline(
    subject_context,
    pipeline_id=custom_id,  # ← 删除
)

# AFTER
pipeline_id = await orchestrator.start_pipeline(subject_context)
```

#### REFACTOR: 删除相关代码

1. 删除所有 `pipeline_id` 参数相关的文档
2. 删除变量 `final_pipeline_id`
3. 更新类型注解

---

## Phase 1: 主干收敛

### Finding 3: 统一节点执行器 [P1]

#### 问题摘要

`node_execution/executor.py` 和 `nodes/dual_agent.py` 各有一套执行器实现，导致维护困难和配置来源不一致。

#### RED: 编写失败测试

**测试文件**: `tests/unit/docuswarm/nodes/test_no_duplicate_executor.py`

```python
"""TDD Tests for Finding 3: Remove duplicate executor from dual_agent.py."""

import pytest
import inspect

from autoBMAD.docuswarm.nodes import dual_agent


class TestNoDuplicateExecutor:
    """Ensure dual_agent.py does not contain duplicate executor code."""
    
    def test_create_node_executor_not_in_dual_agent(self):
        """
        RED: dual_agent should NOT export create_node_executor.
        
        This function should only exist in node_execution/executor.py
        """
        # Should raise AttributeError after fix
        with pytest.raises(AttributeError):
            dual_agent.create_node_executor
    
    def test_execute_node_not_in_dual_agent(self):
        """RED: _execute_node should not exist in dual_agent module."""
        with pytest.raises(AttributeError):
            dual_agent._execute_node
    
    def test_get_config_not_in_dual_agent(self):
        """RED: _get_config should not exist in dual_agent module."""
        with pytest.raises(AttributeError):
            dual_agent._get_config
    
    def test_dual_agent_all_does_not_include_executor(self):
        """
        RED: dual_agent.__all__ should not include executor functions.
        """
        if hasattr(dual_agent, '__all__'):
            assert 'create_node_executor' not in dual_agent.__all__
            assert '_execute_node' not in dual_agent.__all__
            assert '_get_config' not in dual_agent.__all__


class TestOnlyOneExecutorPath:
    """Ensure only one execution path exists."""
    
    def test_graph_uses_node_execution_executor(self):
        """
        RED: pipeline/graph.py should use node_execution.executor.create_node_executor.
        """
        from autoBMAD.docuswarm.pipeline import graph
        import inspect
        
        source = inspect.getsource(graph)
        
        # Should import from node_execution.executor
        assert 'from autoBMAD.docuswarm.node_execution.executor import' in source or \
               'node_execution.executor' in source
        
        # Should NOT create executor locally
        assert 'def create_node_executor' not in source


class TestNoLegacyBridge:
    """Ensure legacy bridge code is removed."""
    
    def test_no_legacy_bridge_in_dual_agent(self):
        """
        RED: dual_agent.py should not contain legacy bridge code.
        """
        import inspect
        
        source = inspect.getsource(dual_agent)
        
        # Should not contain legacy references
        assert 'legacy' not in source.lower() or 'legacy' not in source
        assert 'backward' not in source.lower()
```

**测试文件**: `tests/unit/docuswarm/node_execution/test_executor_is_unique.py`

```python
"""TDD Tests to ensure node_execution/executor.py is the unique executor."""

import pytest
from unittest.mock import Mock

from autoBMAD.docuswarm.node_execution.executor import create_node_executor
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestExecutorConfiguration:
    """Test that executor uses unified config."""
    
    def test_executor_uses_load_config(self):
        """
        GREEN: Executor should use load_config() for configuration.
        
        This ensures consistency with the main config system.
        """
        import inspect
        from autoBMAD.docuswarm.node_execution import executor
        
        source = inspect.getsource(executor)
        
        # Should use load_config
        assert 'load_config' in source
        
        # Should NOT directly read environment variables
        assert 'ANTHROPIC_API_KEY' not in source or 'os.environ' not in source
```

#### GREEN: 实现代码

**Step 1: 删除 nodes/dual_agent.py 中的重复函数**

```python
# DELETE these functions from nodes/dual_agent.py:
# - create_node_executor()  (lines 926-958)
# - _execute_node()         (lines 961-1058)
# - _get_config()           (lines 1061-1079)

# Keep only:
# - NodeResult
# - DualAgentNode
# - create_dual_agent_node
```

**Step 2: 删除 legacy 桥接代码**

```python
# DELETE lines 204-249 (legacy bridge code)
# This code bridges legacy parameters to NodeExecutionContext
```

**Step 3: 更新 __all__**

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

#### REFACTOR: 验证统一性

1. 运行所有节点执行相关测试
2. 验证 `pipeline/graph.py` 使用正确的导入
3. 确认配置来源统一

---

### Finding 4: 统一状态模型 [P1]

#### 问题摘要

状态同时存储在 `state_json` 和顶层列中，读写来源不一致，存在 split-brain 风险。

#### RED: 编写失败测试

**测试文件**: `tests/unit/docuswarm/storage/test_state_manager_finding4.py`

```python
"""TDD Tests for Finding 4: Unify State Model."""

import pytest
import json
import tempfile
import os

from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.pipeline.state import create_initial_state


class TestNoDuplicateCreateInitialState:
    """Ensure StateManager does not duplicate create_initial_state."""
    
    def test_state_manager_uses_pipeline_state_create_initial(self):
        """
        RED: StateManager should import create_initial_state from pipeline.state.
        """
        import inspect
        
        source = inspect.getsource(StateManager)
        
        # Should import from pipeline.state
        assert 'from autoBMAD.docuswarm.pipeline.state import create_initial_state' in source
        
        # Should NOT define its own _create_initial_state
        assert 'def _create_initial_state' not in source


class TestStateJsonIsSingleSourceOfTruth:
    """Ensure state_json is the single source of truth."""
    
    @pytest.fixture
    def state_manager(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        sm = StateManager(db_path=db_path)
        yield sm
        os.unlink(db_path)
    
    def test_create_pipeline_uses_create_initial_state(self, state_manager):
        """
        RED: create_pipeline should use create_initial_state from pipeline.state.
        """
        pipeline_id = state_manager.create_pipeline(
            subject="Test Subject",
            subject_context={"key": "value"}
        )
        
        # Verify the state has all fields from create_initial_state
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # These fields come from create_initial_state in pipeline.state
        assert "session_ids" in pipeline  # Field from create_initial_state
        assert "shared_context" in pipeline  # Field from create_initial_state
    
    def test_get_pipeline_returns_state_json_data(self, state_manager):
        """
        RED: get_pipeline should return data from state_json.
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # Update status
        state_manager.update_pipeline_status(pipeline_id, "running", "analyst")
        
        # Get pipeline
        pipeline = state_manager.get_pipeline(pipeline_id)
        
        # Should return state from state_json
        assert pipeline["status"] == "running"
        assert pipeline["current_node"] == "analyst"
    
    def test_list_pipelines_returns_state_json_data(self, state_manager):
        """
        RED: list_pipelines should also return data from state_json.
        
        Before fix: list_pipelines reads from top-level columns
        After fix: list_pipelines reads from state_json
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_status(pipeline_id, "running")
        
        pipelines = state_manager.list_pipelines()
        assert len(pipelines) == 1
        
        # Should have full state from state_json
        assert pipelines[0]["status"] == "running"
    
    def test_list_and_get_return_consistent_data(self, state_manager):
        """
        RED: list_pipelines and get_pipeline should return consistent data.
        """
        pipeline_id = state_manager.create_pipeline(subject="Test")
        state_manager.update_pipeline_status(pipeline_id, "completed", "po")
        
        # Get from list_pipelines
        list_result = state_manager.list_pipelines()
        assert len(list_result) == 1
        
        # Get from get_pipeline
        get_result = state_manager.get_pipeline(pipeline_id)
        
        # Should be consistent
        assert list_result[0]["status"] == get_result["status"]
        assert list_result[0]["current_node"] == get_result["current_node"]


class TestNoVerifyStateConsistency:
    """Ensure _verify_state_consistency is removed."""
    
    def test_no_verify_state_consistency_method(self):
        """
        RED: StateManager should not have _verify_state_consistency method.
        
        This method was a workaround for the split-brain problem.
        After fix, it's no longer needed.
        """
        assert not hasattr(StateManager, '_verify_state_consistency')


class TestUpdatePipelineStatusSimplification:
    """Test that update_pipeline_status only updates state_json."""
    
    @pytest.fixture
    def state_manager(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        sm = StateManager(db_path=db_path)
        yield sm
        os.unlink(db_path)
    
    def test_update_only_modifies_state_json(self, state_manager):
        """
        RED: update_pipeline_status should only modify state_json.
        
        It should not update top-level columns.
        """
        import sqlite3
        
        pipeline_id = state_manager.create_pipeline(subject="Test")
        
        # Get raw state_json before update
        with sqlite3.connect(state_manager._db._db_path) as conn:
            conn.row_factory = sqlite3.Row
            row_before = conn.execute(
                "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                (pipeline_id,)
            ).fetchone()
            state_before = json.loads(row_before["state_json"])
        
        # Update
        state_manager.update_pipeline_status(pipeline_id, "running", "analyst")
        
        # Get raw state_json after update
        with sqlite3.connect(state_manager._db._db_path) as conn:
            conn.row_factory = sqlite3.Row
            row_after = conn.execute(
                "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                (pipeline_id,)
            ).fetchone()
            state_after = json.loads(row_after["state_json"])
        
        # Verify state_json was updated
        assert state_after["status"] == "running"
        assert state_after["current_node"] == "analyst"
```

#### GREEN: 实现代码

**Step 1: 导入并使用统一的 create_initial_state**

```python
# autoBMAD/docuswarm/storage/state_manager.py

# ADD import at top
from autoBMAD.docuswarm.pipeline.state import create_initial_state

# DELETE method _create_initial_state (lines 98-127)
```

**Step 2: 修改 create_pipeline**

```python
# BEFORE
def create_pipeline(self, subject, subject_context=None):
    pipeline_id = self._generate_pipeline_id()
    initial_state = self._create_initial_state(pipeline_id, subject_context or {})  # ← 本地方法
    state_json = json.dumps(initial_state)
    # ...

# AFTER
def create_pipeline(self, subject, subject_context=None):
    pipeline_id = self._generate_pipeline_id()
    initial_state = create_initial_state(pipeline_id, subject_context or {})  # ← 统一函数
    state_json = json.dumps(initial_state)
    
    with self._db.acquire() as conn:
        conn.execute(
            "INSERT INTO pipelines (pipeline_id, subject, state_json) "
            "VALUES (?, ?, ?)",
            (pipeline_id, subject, state_json),
        )
    return pipeline_id
```

**Step 3: 修改 update_pipeline_status 只更新 state_json**

```python
# BEFORE
def update_pipeline_status(self, pipeline_id, status, current_node=None):
    # ... deprecation warning ...
    
    # Update top-level columns
    with self._db.acquire() as conn:
        if current_node is not None:
            conn.execute(
                "UPDATE pipelines SET status = ?, current_node = ?, ...",
                (status, current_node, pipeline_id)
            )
    
    # Sync state_json
    self._update_state_json_partial(pipeline_id, {...})

# AFTER
def update_pipeline_status(self, pipeline_id, status, current_node=None):
    """Update pipeline status (deprecated, use update_pipeline_state)."""
    import warnings
    warnings.warn(
        "update_pipeline_status() is deprecated, use update_pipeline_state() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    
    self._validate_status(status)
    
    if not self._pipeline_exists(pipeline_id):
        raise StorageError(f"Pipeline not found: {pipeline_id}")
    
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
```

**Step 4: 修改 get_pipeline 和 list_pipelines**

```python
# get_pipeline - 从 state_json 读取
def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
    with self._db.acquire() as conn:
        row = conn.execute(
            "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
            (pipeline_id,)
        ).fetchone()
        
        if row and row["state_json"]:
            return json.loads(row["state_json"])
    return None

# list_pipelines - 也从 state_json 读取
def list_pipelines(self, status=None, limit=100) -> list[dict[str, Any]]:
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

**Step 5: 删除 _verify_state_consistency**

```python
# DELETE entire method _verify_state_consistency (lines 167-209)
```

#### REFACTOR: 简化代码

1. 删除 `_update_state_json_partial` 方法（如果不再使用）
2. 简化文档字符串
3. 优化 SQL 查询

---

## Phase 2: 清理漂移

### Finding 5: 依赖和命名清理 [P1]

#### 问题摘要

- 使用未声明的依赖 (`kaos.path`, `kimi_agent_sdk`)
- 命名不一致 (`KimiSessionManager` vs `SessionManager`)
- 存在 deprecated/legacy 代码

#### RED: 编写失败测试

**测试文件**: `tests/unit/test_finding5_dependency_cleanup.py`

```python
"""TDD Tests for Finding 5: Dependency and Naming Cleanup."""

import pytest
import ast
from pathlib import Path


class TestNoKaosPath:
    """Ensure no kaos.path imports exist."""
    
    def test_no_kaos_path_in_orchestrator(self):
        """
        RED: orchestrator.py should not import from kaos.path.
        """
        orchestrator_path = Path("autoBMAD/docuswarm/pipeline/orchestrator.py")
        source = orchestrator_path.read_text()
        
        assert "from kaos.path import" not in source
        assert "import kaos.path" not in source
        assert "KaosPath" not in source


class TestNoKimiAgentSdk:
    """Ensure no kimi_agent_sdk imports exist."""
    
    def test_no_kimi_agent_sdk_in_approval(self):
        """RED: approval.py should not import kimi_agent_sdk."""
        approval_path = Path("autoBMAD/docuswarm/llm/approval.py")
        source = approval_path.read_text()
        
        assert "kimi_agent_sdk" not in source
    
    def test_no_kimi_aggregator_in_session_manager(self):
        """RED: session_manager.py should not import kimi_agent_sdk._aggregator."""
        sm_path = Path("autoBMAD/docuswarm/llm/session_manager.py")
        source = sm_path.read_text()
        
        assert "kimi_agent_sdk" not in source
        assert "_aggregator" not in source


class TestNoKimiSessionManagerAlias:
    """Ensure KimiSessionManager alias is removed."""
    
    def test_no_kimi_session_manager_alias(self):
        """
        RED: SessionManager module should not define KimiSessionManager alias.
        """
        from autoBMAD.docuswarm.llm import session_manager
        
        # Should not have KimiSessionManager
        assert not hasattr(session_manager, 'KimiSessionManager')
    
    def test_all_files_use_session_manager(self):
        """
        RED: All files should use SessionManager, not KimiSessionManager.
        """
        import subprocess
        
        result = subprocess.run(
            ["grep", "-r", "KimiSessionManager", "--include=*.py", "autoBMAD/"],
            capture_output=True,
            text=True
        )
        
        # Should have no matches (except possibly in comments)
        assert result.returncode != 0 or result.stdout == ""


class TestPyprojectDependencies:
    """Ensure pyproject.toml declares all dependencies."""
    
    def test_no_undeclared_dependencies(self):
        """
        RED: All runtime dependencies should be declared in pyproject.toml.
        """
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()
        
        # Should not use these without declaration
        assert "kaos.path" not in content or "kaos" in content
        assert "kimi-agent-sdk" not in content


class TestNoDeprecatedCode:
    """Ensure no deprecated/legacy code exists."""
    
    def test_no_backward_compatibility_in_context_validator(self):
        """RED: ContextValidator should not have backward compatibility code."""
        from autoBMAD.docuswarm.context import validator
        import inspect
        
        source = inspect.getsource(validator)
        
        assert "backward" not in source.lower()
        assert "backward compatibility" not in source.lower()
    
    def test_no_legacy_in_dual_agent(self):
        """RED: dual_agent.py should not have legacy bridge code."""
        from autoBMAD.docuswarm.nodes import dual_agent
        import inspect
        
        source = inspect.getsource(dual_agent)
        
        # Allow "legacy" in comments explaining removal
        # But should not have legacy code execution
        lines = source.split('\n')
        for line in lines:
            if 'legacy' in line.lower() and not line.strip().startswith('#'):
                pytest.fail(f"Found legacy code: {line}")
```

#### GREEN: 实现代码

**Step 1: 移除 kaos.path**

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py

# BEFORE
from kaos.path import KaosPath

# AFTER
from pathlib import Path

# Replace all KaosPath usages with Path
```

**Step 2: 移除 kimi_agent_sdk 残留**

```python
# autoBMAD/docuswarm/llm/approval.py
# REMOVE: import kimi_agent_sdk
# REMOVE: Any reference to kimi_agent_sdk types

# autoBMAD/docuswarm/llm/session_manager.py
# REMOVE: import kimi_agent_sdk
# REMOVE: import kimi_agent_sdk._aggregator
```

**Step 3: 删除别名并统一命名**

```python
# autoBMAD/docuswarm/llm/session_manager.py

# BEFORE (end of file)
# Backward compatibility alias
KimiSessionManager = SessionManager

# AFTER
# (delete the alias line)
```

搜索并替换所有 `KimiSessionManager` 为 `SessionManager`:

```bash
# Update all files
sed -i 's/KimiSessionManager/SessionManager/g' autoBMAD/docuswarm/pipeline/orchestrator.py
sed -i 's/KimiSessionManager/SessionManager/g' autoBMAD/docuswarm/node_execution/executor.py
sed -i 's/KimiSessionManager/SessionManager/g' autoBMAD/docuswarm/nodes/dual_agent.py
# ... etc
```

**Step 4: 删除 deprecated/legacy 代码**

逐个审查并删除标记为 deprecated 的代码:

```python
# ContextValidator - remove backward compatibility blocks
# dual_agent.py - remove legacy bridge (lines 204-249)
# Any other files with "deprecated", "legacy", "backward compatibility"
```

**Step 5: 更新 pyproject.toml**

```toml
# Ensure all dependencies are declared
# Remove any kimi-agent-sdk references
# Add any missing dependencies
```

---

## 集成测试方案

### 端到端测试

**测试文件**: `tests/integration/test_findings_1_to_5_integration.py`

```python
"""Integration tests for Finding 1-5 fixes working together."""

import pytest
from pathlib import Path

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class TestFullPipelineExecution:
    """Test complete pipeline with all fixes applied."""
    
    @pytest.mark.asyncio
    async def test_pipeline_execution_without_explicit_session_manager(self):
        """
        Integration: Full pipeline execution without explicit session_manager.
        
        This tests Finding 1 fix.
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        # Mock LLM calls
        with mock.patch(...):
            pipeline_id = await orchestrator.start_pipeline({
                "subject": "Integration Test",
                "task": "Test task"
            })
        
        # Verify ID is auto-generated and consistent
        assert pipeline_id.startswith("pipeline-")
        
        # Verify pipeline exists in DB
        status = await orchestrator.get_pipeline_status(pipeline_id)
        assert status is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_state_consistency(self):
        """
        Integration: Pipeline state is consistent across operations.
        
        This tests Finding 4 fix.
        """
        orchestrator = HybridOrchestrator(db_path=":memory:")
        
        with mock.patch(...):
            pipeline_id = await orchestrator.start_pipeline({"subject": "Test"})
        
        # Get status multiple ways
        status1 = orchestrator._state_manager.get_pipeline(pipeline_id)
        status2_list = orchestrator._state_manager.list_pipelines()
        
        # Should be consistent
        assert len(status2_list) == 1
        assert status1["status"] == status2_list[0]["status"]
        assert status1["pipeline_id"] == status2_list[0]["pipeline_id"]


class TestCodeQuality:
    """Test code quality after all fixes."""
    
    def test_no_duplicate_executor_functions(self):
        """
        Integration: Only one set of executor functions exists.
        
        This tests Finding 3 fix.
        """
        from autoBMAD.docuswarm.node_execution import executor
        from autoBMAD.docuswarm.nodes import dual_agent
        
        # node_execution/executor.py should have create_node_executor
        assert hasattr(executor, 'create_node_executor')
        
        # dual_agent.py should NOT have create_node_executor
        assert not hasattr(dual_agent, 'create_node_executor')
    
    def test_no_undeclared_dependencies(self):
        """
        Integration: No undeclared dependencies exist.
        
        This tests Finding 5 fix.
        """
        import subprocess
        
        # Check for kaos.path usage
        result = subprocess.run(
            ["grep", "-r", "from kaos.path", "--include=*.py", "autoBMAD/"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0 or result.stdout == ""
```

---

## 验收标准汇总

### Finding 1 验收标准

- [ ] `ContextValidator.__init__()` 不再接受 `session_manager` 参数
- [ ] `validate_context_with_llm()` 要求传入 `session_manager` 参数
- [ ] `HybridOrchestrator(db_path=":memory:")` 可直接调用 `start_pipeline()` 不报错
- [ ] 删除所有 backward compatibility 代码

### Finding 2 验收标准

- [ ] `start_pipeline()` 不再接受 `pipeline_id` 参数
- [ ] 数据库中的 ID 与返回的 ID 始终一致
- [ ] 所有调用点已更新

### Finding 3 验收标准

- [ ] `nodes/dual_agent.py` 不再包含 `create_node_executor` 函数
- [ ] `nodes/dual_agent.py` 不再包含 `_get_config` 函数
- [ ] 删除所有 legacy 桥接代码
- [ ] 代码行数减少约 150 行

### Finding 4 验收标准

- [ ] 删除 `StateManager._create_initial_state` 方法
- [ ] 统一使用 `pipeline/state.py:create_initial_state`
- [ ] 删除 `_verify_state_consistency` 方法
- [ ] `get_pipeline` 和 `list_pipelines` 返回一致的结果

### Finding 5 验收标准

- [ ] 无 `kaos.path` 导入
- [ ] 无 `kimi_agent_sdk` 导入
- [ ] 无 `KimiSessionManager` 别名
- [ ] 删除所有 deprecated/legacy 代码
- [ ] `pyproject.toml` 声明所有运行时依赖

---

## 附录

### A. 测试命令速查

```bash
# 运行特定 Finding 的测试
pytest tests/unit/docuswarm/context/test_validator_finding1.py -v
pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py -v
pytest tests/unit/docuswarm/nodes/test_no_duplicate_executor.py -v
pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py -v
pytest tests/unit/test_finding5_dependency_cleanup.py -v

# 运行所有 TDD 测试
pytest tests/unit/test_*finding*.py -v

# 运行集成测试
pytest tests/integration/test_findings_1_to_5_integration.py -v
```

### B. 代码变更统计

| Finding | 预计变更文件数 | 预计新增/删除代码行 |
|---------|---------------|-------------------|
| F1 | 3 | -30/+50 |
| F2 | 2 | -15/+10 |
| F3 | 1 | -150/+0 |
| F4 | 2 | -80/+60 |
| F5 | 5+ | -100/+20 |

### C. 回滚计划

如果实施过程中出现严重问题:

1. **立即回滚**: `git revert <commit-hash>`
2. **隔离问题**: 确定是哪个 Finding 引入的问题
3. **分步实施**: 将问题 Finding 拆分为更小的 PR
4. **重新测试**: 每个小 PR 充分测试后再合并

---

**文档结束**
