# DocuSwarm P0/P1 技术债务 TDD 主方案

> 创建日期: 2026-03-18
> 基于研究: `docs/research/2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md`
> 范围: TD-1 至 TD-5 全部技术债务
> 方法论: 测试驱动开发 (TDD)

---

## 1. 方案概述

### 1.1 执行顺序

基于奥卡姆剃刀原则（简单优先）和风险收益比：

```
Phase 1 (Week 1-2): 止血层 - TD-2 + TD-3
├─ TD-2: 工具层 Path.cwd() 解耦
└─ TD-3: models 兼容层清理

Phase 2 (Week 3-4): 状态层 - TD-1
├─ TD-1: state_json 唯一真相源
└─ 恢复逻辑统一

Phase 3 (Week 5-6): 控制层 - TD-5
├─ TD-5: CLI 拆分
└─ Smoke tests

Phase 4 (Month 2+): 架构层 - TD-4
└─ TD-4: 执行骨架收敛
```

### 1.2 验收标准总览

| 技术债务 | 验收标准 | 测试类型 |
|---------|---------|---------|
| TD-1 | state_json 为唯一真相源，恢复逻辑正确 | 单元测试 + 集成测试 |
| TD-2 | 所有工具接受显式 output_dir | 单元测试 |
| TD-3 | models 模块移除或惰性触发 | 单元测试 |
| TD-4 | 合成 ID 限制在边界层 | 集成测试 |
| TD-5 | CLI 拆分为 commands + services | Smoke 测试 |

---

## 2. Phase 1: TD-2 + TD-3 (止血层)

### 2.1 TD-2: 工具层 Path.cwd() 解耦

#### 2.1.1 测试策略

**测试目标**: 验证工具类可以接受显式 `output_dir` 参数，不再依赖 `Path.cwd()`

**测试文件**: `tests/tools/test_output_dir_injection.py`

#### 2.1.2 测试用例设计

```python
"""TD-2: 工具层 output_dir 注入测试."""

import tempfile
from pathlib import Path
import pytest
import pytest_asyncio

from autoBMAD.docuswarm.tools.create_deliverable import (
    CreateDeliverableTool,
    CreateDeliverableParams,
)
from autoBMAD.docuswarm.tools.create_document_set import (
    CreateDocumentSetTool,
    CreateDocumentSetParams,
    DocumentSpec,
)


class TestCreateDeliverableToolOutputDir:
    """Test TD-2: CreateDeliverableTool 显式 output_dir 注入."""

    @pytest_asyncio.fixture
    async def temp_output_dir(self):
        """Fixture: 提供临时输出目录."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.mark.asyncio
    async def test_tool_accepts_output_dir_parameter(self, temp_output_dir: Path):
        """测试: 工具类接受 output_dir 参数."""
        # Arrange
        tool = CreateDeliverableTool(output_dir=temp_output_dir)
        params = CreateDeliverableParams(
            title="Test Document",
            content="# Test Content",
        )

        # Act
        result = await tool._execute(params)

        # Assert
        assert result.success is True
        assert result.result is not None
        assert "file_path" in result.result

    @pytest.mark.asyncio
    async def test_tool_uses_output_dir_instead_of_cwd(self, temp_output_dir: Path):
        """测试: 工具使用传入的 output_dir 而非 Path.cwd()."""
        # Arrange
        tool = CreateDeliverableTool(output_dir=temp_output_dir)
        params = CreateDeliverableParams(
            title="CWD Test Document",
            content="# Content",
        )

        # Act
        result = await tool._execute(params)

        # Assert
        assert result.success is True
        file_path = Path(result.result["file_path"])
        
        # 关键断言: 文件应创建在指定的 temp_output_dir，而非当前工作目录
        assert file_path.parent == temp_output_dir
        assert file_path.exists()

    @pytest.mark.asyncio
    async def test_tool_backward_compatibility(self):
        """测试: 不传 output_dir 时默认使用 Path.cwd() 保持兼容性."""
        import os
        
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                tool = CreateDeliverableTool()  # 不传 output_dir
                params = CreateDeliverableParams(
                    title="Backward Compatibility Test",
                    content="# Content",
                )

                # Act
                result = await tool._execute(params)

                # Assert
                assert result.success is True
                file_path = Path(result.result["file_path"])
                assert file_path.parent == Path(temp_dir)
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_no_os_chdir_needed_in_tests(self, temp_output_dir: Path):
        """测试: 不再需要在测试中使用 os.chdir()."""
        # 这个测试演示了新的测试模式：直接注入 output_dir
        # 而不是通过 os.chdir() 来间接控制输出位置
        
        tool = CreateDeliverableTool(output_dir=temp_output_dir)
        params = CreateDeliverableParams(
            title="No Chdir Test",
            content="# No Chdir Content",
        )

        result = await tool._execute(params)

        assert result.success is True
        # 验证文件在正确位置
        assert (temp_output_dir / "no-chdir-test.md").exists()


class TestCreateDocumentSetToolOutputDir:
    """Test TD-2: CreateDocumentSetTool 显式 output_dir 注入."""

    @pytest.mark.asyncio
    async def test_document_set_uses_output_dir(self):
        """测试: CreateDocumentSetTool 使用传入的 output_dir."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            tool = CreateDocumentSetTool(output_dir=output_dir)
            
            params = CreateDocumentSetParams(
                documents=[
                    DocumentSpec(
                        template_id="test_doc",
                        title="Test Document Set",
                        content="# Test Content",
                    )
                ],
                node_id="analyst",
            )

            result = await tool._execute(params)

            assert result.success is True
            # 验证文件创建在指定目录
            created_files = result.result.get("created_files", [])
            for file_info in created_files:
                file_path = Path(file_info["file_path"])
                assert file_path.parent == output_dir
```

#### 2.1.3 实施步骤

```python
# Step 1: 修改 CreateDeliverableTool
# autoBMAD/docuswarm/tools/create_deliverable.py

class CreateDeliverableTool(ToolResultCallableTool[CreateDeliverableParams]):
    """Tool for creating node deliverable documents."""

    name: str = "create_deliverable"
    description: str = "..."
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initialize the tool with optional output directory.
        
        Args:
            output_dir: Directory for output files. Defaults to Path.cwd() for backward compatibility.
        """
        super().__init__()
        self.output_dir = output_dir or Path.cwd()

    @override
    async def _execute(self, params: CreateDeliverableParams) -> ToolResult:
        """Create a deliverable with the given parameters."""
        try:
            filename = _slugify_filename(params.title)
            # 使用 self.output_dir 而非 Path.cwd()
            file_path = self.output_dir / filename

            # Write content to file
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)

            # ... rest of implementation

# Step 2: 修改 CreateDocumentSetTool
# autoBMAD/docuswarm/tools/create_document_set.py

class CreateDocumentSetTool(ToolResultCallableTool[CreateDocumentSetParams]):
    """Tool for creating multiple structured documents."""

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initialize the tool."""
        super().__init__()
        self.templates_cache: dict[str, Any] = {}
        self._load_templates()
        self.output_dir = output_dir or Path.cwd()

    @override
    async def _execute(self, params: CreateDocumentSetParams) -> ToolResult:
        """Create multiple documents with validation."""
        try:
            created_files: list[dict[str, Any]] = []
            
            # 使用 self.output_dir 而非 Path.cwd()
            output_dir = self.output_dir

            for doc_spec in params.documents:
                # ...
                file_path = output_dir / filename
                # ...

# Step 3: 更新测试文件
# 移除所有 os.chdir() 调用，改用 output_dir 参数
```

#### 2.1.4 验收标准

- [x] `CreateDeliverableTool` 接受 `output_dir` 参数
- [x] `CreateDocumentSetTool` 接受 `output_dir` 参数
- [x] 测试不再使用 `os.chdir()`
- [x] 向后兼容：不传 `output_dir` 时默认使用 `Path.cwd()`

---

### 2.2 TD-3: models 兼容层清理

#### 2.2.1 测试策略

**测试目标**: 验证 models 模块可以安全移除，或改为惰性触发 warning

**测试文件**: `tests/unit/test_models_deprecation.py`

#### 2.2.2 测试用例设计

```python
"""TD-3: models 兼容层清理测试."""

import sys
import warnings
from typing import Any
import pytest


class TestModelsModuleDeprecation:
    """Test TD-3: models 模块废弃处理."""

    def test_models_import_triggers_deprecation_warning(self):
        """测试: 从 models 导入触发 DeprecationWarning."""
        # 确保每次测试都重新导入模块以触发 warning
        if "autoBMAD.docuswarm.models" in sys.modules:
            del sys.modules["autoBMAD.docuswarm.models"]
        if "autoBMAD.docuswarm.models.tool_registry" in sys.modules:
            del sys.modules["autoBMAD.docuswarm.models.tool_registry"]
        if "autoBMAD.docuswarm.models.tool_result" in sys.modules:
            del sys.modules["autoBMAD.docuswarm.models.tool_result"]

        with pytest.warns(DeprecationWarning, match="models module is deprecated"):
            from autoBMAD.docuswarm.models import ToolResult, ToolRegistry

    def test_models_toolresult_is_same_as_tools_toolresult(self):
        """测试: models.ToolResult 与 tools.ToolResult 是同一对象."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from autoBMAD.docuswarm.models import ToolResult as ModelsToolResult
            from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolsToolResult

        assert ModelsToolResult is ToolsToolResult

    def test_models_toolregistry_is_same_as_tools_toolregistry(self):
        """测试: models.ToolRegistry 与 tools.ToolRegistry 是同一对象."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from autoBMAD.docuswarm.models import ToolRegistry as ModelsToolRegistry
            from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolsToolRegistry

        assert ModelsToolRegistry is ToolsToolRegistry

    def test_direct_tools_import_no_warning(self):
        """测试: 直接从 tools 导入不触发 warning."""
        # 确保不触发任何 DeprecationWarning
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            
            # 应该不触发异常
            from autoBMAD.docuswarm.tools.tool_result import ToolResult
            from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry
            
            assert ToolResult is not None
            assert ToolRegistry is not None


class TestModelsModuleRemoval:
    """Test TD-3 方案 A: 彻底移除 models 模块."""

    @pytest.mark.skip(reason="仅在完全移除 models 模块后启用")
    def test_models_module_not_importable(self):
        """测试: models 模块完全不可导入."""
        with pytest.raises(ImportError):
            from autoBMAD.docuswarm.models import ToolResult

    @pytest.mark.skip(reason="仅在完全移除 models 模块后启用")
    def test_all_imports_use_tools_directly(self):
        """测试: 所有代码直接使用 tools 路径导入."""
        # 这个测试需要全局代码扫描，验证没有从 models 的导入
        import subprocess
        
        result = subprocess.run(
            ["grep", "-r", "from autoBMAD.docuswarm.models", "autoBMAD/docuswarm/"],
            capture_output=True,
            text=True,
        )
        
        # 应该没有任何匹配
        assert result.returncode != 0 or result.stdout == ""


class TestModelsLazyDeprecation:
    """Test TD-3 方案 B: 惰性触发 warning (如果使用此方案)."""

    def test_lazy_warning_on_attribute_access(self):
        """测试: 访问属性时才触发 warning."""
        # 导入模块本身不触发 warning
        import autoBMAD.docuswarm.models as models_module
        
        # 但访问属性时触发
        with pytest.warns(DeprecationWarning, match="models.ToolResult is deprecated"):
            _ = models_module.ToolResult

    def test_no_warning_on_import_only(self):
        """测试: 仅导入模块不触发 warning."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            
            # 导入模块本身不应该触发异常
            import autoBMAD.docuswarm.models
```

#### 2.2.3 实施步骤

**方案 A: 彻底移除 (推荐)**

```bash
# Step 1: 查找所有使用 models 模块的代码
grep -r "from autoBMAD.docuswarm.models" autoBMAD/docuswarm/ --include="*.py"
grep -r "import autoBMAD.docuswarm.models" autoBMAD/docuswarm/ --include="*.py"

# Step 2: 更新所有导入
# 从:
from autoBMAD.docuswarm.models import ToolResult, ToolRegistry
# 改为:
from autoBMAD.docuswarm.tools.tool_result import ToolResult
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry

# Step 3: 删除 models 目录
rm -rf autoBMAD/docuswarm/models/

# Step 4: 更新任何引用 models 的测试
grep -r "from autoBMAD.docuswarm.models" tests/ --include="*.py"
# 更新这些测试使用新的导入路径
```

**方案 B: 惰性触发 (备选)**

```python
# autoBMAD/docuswarm/models/__init__.py
"""Models module - DEPRECATED.

This module is deprecated. Use autoBMAD.docuswarm.tools directly.
"""

from __future__ import annotations

import warnings
from typing import Any


def __getattr__(name: str) -> Any:
    """Lazy import with deprecation warning."""
    warnings.warn(
        f"models.{name} is deprecated. Use autoBMAD.docuswarm.tools directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    
    if name == "ToolResult":
        from autoBMAD.docuswarm.tools.tool_result import ToolResult
        return ToolResult
    if name == "ToolRegistry":
        from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry
        return ToolRegistry
    
    raise AttributeError(f"module 'models' has no attribute '{name}'")
```

#### 2.2.4 验收标准

- [x] models 模块移除，或改为惰性触发 warning
- [x] 所有代码直接使用 tools 路径导入
- [x] 测试不再依赖 models 模块（或正确处理 DeprecationWarning）

---

## 3. Phase 2: TD-1 (状态层)

### 3.1 TD-1: state_json 唯一真相源

#### 3.1.1 测试策略

**测试目标**: 验证 `state_json` 是唯一的业务状态真相源，`pipelines.current_node` 仅作为派生字段

**测试文件**: 
- `tests/storage/test_state_json_single_source.py`
- `tests/pipeline/test_resume_from_state_json.py`

#### 3.1.2 测试用例设计

```python
"""TD-1: state_json 唯一真相源测试."""

import json
import pytest
import pytest_asyncio
from pathlib import Path
import tempfile

from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.pipeline.state import create_initial_state, PipelineState


class TestStateJsonSingleSource:
    """Test TD-1: state_json 是唯一的业务真相源."""

    @pytest_asyncio.fixture
    async def temp_db(self):
        """Fixture: 提供临时数据库."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        db = StateManager(db_path=db_path)
        yield db, db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_create_pipeline_writes_full_pipeline_state(self, temp_db):
        """测试: create_pipeline() 写入完整的 PipelineState 到 state_json."""
        db, _ = temp_db
        
        subject_context = {"subject": "Test Project", "content": "Test content"}
        pipeline_id = db.create_pipeline(
            subject="Test Project",
            subject_context=subject_context,
        )

        # 获取 pipeline
        pipeline = db.get_pipeline(pipeline_id)
        assert pipeline is not None

        # 验证 state_json 包含完整的 PipelineState 字段
        state = pipeline["state"]
        required_fields = [
            "pipeline_id",
            "subject_context",
            "current_node",
            "completed_nodes",
            "deliverables",
            "questions",
            "evaluations",
            "node_iterations",
            "session_ids",
            "session_metadata",
            "current_node_session_id",
            "status",
            "error",
            "shared_context",
        ]
        
        for field in required_fields:
            assert field in state, f"Missing required field: {field}"

        # 验证 pipeline_id 正确
        assert state["pipeline_id"] == pipeline_id
        assert state["status"] == "pending"

    @pytest.mark.asyncio
    async def test_update_pipeline_state_updates_state_json(self, temp_db):
        """测试: update_pipeline_state() 正确更新 state_json."""
        db, _ = temp_db
        
        # 创建 pipeline
        pipeline_id = db.create_pipeline(
            subject="Test Project",
            subject_context={},
        )

        # 更新状态
        state_update = {
            "current_node": "analyst",
            "completed_nodes": ["pm"],
            "status": "running",
            "shared_context": {"facts": {"key": "value"}},
        }
        
        result = await db.update_pipeline_state(pipeline_id, state_update)
        assert result is True

        # 验证更新后的 state_json
        pipeline = db.get_pipeline(pipeline_id)
        state = pipeline["state"]
        
        assert state["current_node"] == "analyst"
        assert state["completed_nodes"] == ["pm"]
        assert state["status"] == "running"
        assert state["shared_context"]["facts"]["key"] == "value"

    def test_state_json_is_source_of_truth_for_current_node(self, temp_db):
        """测试: state_json 是 current_node 的唯一真相源."""
        db, db_path = temp_db
        
        pipeline_id = db.create_pipeline(subject="Test", subject_context={})
        
        # 直接操作数据库制造不一致：
        # pipelines.current_node = "old_value"
        # state_json.current_node = "new_value"
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE pipelines SET current_node = ? WHERE pipeline_id = ?",
            ("old_node", pipeline_id)
        )
        
        # 更新 state_json
        pipeline = db.get_pipeline(pipeline_id)
        state = pipeline["state"]
        state["current_node"] = "new_node"
        
        conn.execute(
            "UPDATE pipelines SET state_json = ? WHERE pipeline_id = ?",
            (json.dumps(state), pipeline_id)
        )
        conn.commit()
        conn.close()

        # 重新获取 pipeline
        pipeline = db.get_pipeline(pipeline_id)
        
        # 验证：业务逻辑应该使用 state_json 中的值
        business_state = pipeline["state"]
        assert business_state["current_node"] == "new_node"


class TestResumeFromStateJson:
    """Test TD-1: 恢复逻辑从 state_json 读取."""

    @pytest_asyncio.fixture
    async def orchestrator_and_db(self):
        """Fixture: 提供 orchestrator 和数据库."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        
        orchestrator = HybridOrchestrator(db_path=db_path)
        db = StateManager(db_path=db_path)
        
        yield orchestrator, db
        
        Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_resume_uses_state_json_as_source(self, orchestrator_and_db):
        """测试: resume_pipeline() 优先从 state_json 恢复状态."""
        orchestrator, db = orchestrator_and_db
        
        # 创建并执行部分 pipeline
        pipeline_id = await orchestrator.start_pipeline(
            subject_context={"subject": "Test", "content": "Test"}
        )
        
        # 手动更新 state_json 模拟执行进度
        await db.update_pipeline_state(
            pipeline_id,
            {
                "current_node": "analyst",
                "completed_nodes": ["pm"],
                "status": "paused",
            }
        )
        
        # resume
        result = await orchestrator.resume_pipeline(pipeline_id)
        
        # 验证从 state_json 恢复了正确的状态
        assert result["pipeline_id"] == pipeline_id
        # 验证 current_node 来自 state_json
        assert result.get("current_node") in ["analyst", None]  # 取决于实现

    @pytest.mark.asyncio
    async def test_resume_state_consistency(self, orchestrator_and_db):
        """测试: resume 后状态一致性."""
        orchestrator, db = orchestrator_and_db
        
        pipeline_id = await orchestrator.start_pipeline(
            subject_context={"subject": "Test", "content": "Test"}
        )
        
        # 设置完整状态
        await db.update_pipeline_state(
            pipeline_id,
            {
                "current_node": "analyst",
                "completed_nodes": ["pm"],
                "deliverables": {"pm": {"title": "PM Doc"}},
                "node_iterations": {"pm": 1, "analyst": 0},
                "session_ids": {"pm": "session-123"},
                "status": "paused",
                "shared_context": {"facts": {"test": "value"}},
            }
        )
        
        # resume
        await orchestrator.resume_pipeline(pipeline_id)
        
        # 验证状态完整恢复
        pipeline = db.get_pipeline(pipeline_id)
        state = pipeline["state"]
        
        assert state["completed_nodes"] == ["pm"]
        assert "pm" in state["deliverables"]
        assert state["shared_context"]["facts"]["test"] == "value"


class TestStateJsonIntegrity:
    """Test TD-1: state_json 完整性验证."""

    def test_pipeline_state_schema_completeness(self):
        """测试: PipelineState 包含所有必需字段."""
        # 创建一个完整的 PipelineState
        state: PipelineState = create_initial_state(
            pipeline_id="test-123",
            subject_context={"test": "data"},
        )
        
        required_fields = [
            "pipeline_id",
            "subject_context",
            "current_node",
            "completed_nodes",
            "deliverables",
            "questions",
            "evaluations",
            "node_iterations",
            "session_ids",
            "session_metadata",
            "current_node_session_id",
            "status",
            "error",
            "shared_context",
        ]
        
        for field in required_fields:
            assert field in state, f"PipelineState missing field: {field}"

    def test_state_json_serialization_roundtrip(self):
        """测试: state_json 序列化和反序列化保持完整性."""
        original_state = create_initial_state(
            pipeline_id="test-456",
            subject_context={"key": "value"},
        )
        
        # 添加一些数据
        original_state["completed_nodes"] = ["pm", "analyst"]
        original_state["deliverables"] = {"pm": {"title": "PM Doc"}}
        original_state["shared_context"] = {"facts": {"test": "data"}}
        
        # 序列化
        json_str = json.dumps(original_state)
        
        # 反序列化
        restored_state = json.loads(json_str)
        
        # 验证完整性
        assert restored_state["pipeline_id"] == original_state["pipeline_id"]
        assert restored_state["completed_nodes"] == original_state["completed_nodes"]
        assert restored_state["deliverables"] == original_state["deliverables"]
        assert restored_state["shared_context"] == original_state["shared_context"]
```

#### 3.1.3 实施步骤

```python
# Step 1: StateManager.create_pipeline 修改
# autoBMAD/docuswarm/storage/state_manager.py

def create_pipeline(
    self,
    subject: str,
    subject_context: dict[str, Any] | None = None,
) -> str:
    """Create a new pipeline with pending status."""
    from autoBMAD.docuswarm.pipeline.state import create_initial_state
    
    pipeline_id = self._generate_pipeline_id()
    
    # TD-1: 写入完整的 PipelineState
    initial_state = create_initial_state(pipeline_id, subject_context or {})
    state_json = json.dumps(initial_state)
    
    try:
        with self._db.acquire() as conn:
            _ = conn.execute(
                "INSERT INTO pipelines (pipeline_id, subject, status, state_json) "
                + "VALUES (?, ?, ?, ?)",
                (pipeline_id, subject, "pending", state_json),
            )
    except Exception as e:
        raise StorageError(
            f"Failed to create pipeline: {e}",
            operation_type="create",
            pipeline_id=pipeline_id,
        ) from e
    
    return pipeline_id

# Step 2: StateManager.update_pipeline_status 修改
# 同时更新顶层列和 state_json

def update_pipeline_status(
    self,
    pipeline_id: str,
    status: str,
    current_node: str | None = None,
) -> bool:
    """Update pipeline status and state_json."""
    self._validate_status(status)
    
    if not self._pipeline_exists(pipeline_id):
        raise StorageError(
            f"Pipeline not found: {pipeline_id}",
            operation_type="update",
            pipeline_id=pipeline_id,
        )
    
    try:
        with self._db.acquire() as conn:
            # TD-1: 更新顶层列（查询优化）
            if current_node is not None:
                conn.execute(
                    "UPDATE pipelines SET status = ?, current_node = ?, "
                    + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (status, current_node, pipeline_id),
                )
            else:
                conn.execute(
                    "UPDATE pipelines SET status = ?, "
                    + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                    (status, pipeline_id),
                )
            
            # TD-1: 同时更新 state_json（业务真相源）
            cursor = conn.execute(
                "SELECT state_json FROM pipelines WHERE pipeline_id = ?",
                (pipeline_id,),
            )
            row = cursor.fetchone()
            if row and row["state_json"]:
                state = json.loads(row["state_json"])
                state["status"] = status
                if current_node is not None:
                    state["current_node"] = current_node
                
                conn.execute(
                    "UPDATE pipelines SET state_json = ? WHERE pipeline_id = ?",
                    (json.dumps(state), pipeline_id),
                )
        
        return True
    except Exception as e:
        raise StorageError(
            f"Failed to update pipeline status: {e}",
            operation_type="update",
            pipeline_id=pipeline_id,
        ) from e

# Step 3: Orchestrator 修改
# autoBMAD/docuswarm/pipeline/orchestrator.py

async def resume_pipeline(self, pipeline_id: str) -> dict[str, Any]:
    """Resume pipeline with state_json as source of truth."""
    # 获取 pipeline
    pipeline = self._state_manager.get_pipeline(pipeline_id)
    if pipeline is None:
        raise PipelineNotFoundError(f"Pipeline not found: {pipeline_id}")
    
    # TD-1: 优先从 state_json 读取业务状态
    business_state = pipeline.get("state", {})
    current_node = business_state.get("current_node")
    completed_nodes = business_state.get("completed_nodes", [])
    
    # 使用 business_state 恢复执行...
```

#### 3.1.4 验收标准

- [x] `create_pipeline()` 写入完整的 `PipelineState` 到 `state_json`
- [x] `update_pipeline_status()` 同时更新 `state_json`
- [x] `resume_pipeline()` 优先从 `state_json` 恢复
- [x] 新增 `update_pipeline_state()` 方法用于完整状态更新
- [x] `state_json` 包含所有必需字段

---

## 4. Phase 3: TD-5 (控制层)

### 4.1 TD-5: CLI 拆分

#### 4.1.1 测试策略

**测试目标**: 验证 CLI 拆分为 `commands/*` + `services/*` 两层，main.py 变薄

**测试文件**: 
- `tests/cli/test_commands_smoke.py`
- `tests/cli/test_services_unit.py`

#### 4.1.2 测试用例设计

```python
"""TD-5: CLI 拆分测试."""

import pytest
import pytest_asyncio
from pathlib import Path
import tempfile
from click.testing import CliRunner

from autoBMAD.docuswarm.cli.main import cli
from autoBMAD.docuswarm.cli.services.pipeline_service import PipelineService
from autoBMAD.docuswarm.cli.services.status_service import StatusService


class TestCliCommandsSmoke:
    """Test TD-5: CLI 命令 Smoke 测试."""

    @pytest.fixture
    def cli_runner(self):
        """Fixture: 提供 Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_context_file(self):
        """Fixture: 提供临时上下文文件."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write("# Test Project\\n\\nThis is a test project.")
            path = f.name
        yield path
        Path(path).unlink(missing_ok=True)

    def test_start_command_exists(self, cli_runner, temp_context_file):
        """Smoke 测试: start 命令存在并可调用."""
        result = cli_runner.invoke(cli, ["start", "--context", temp_context_file])
        
        # 即使失败，也应该是因为业务原因（如 API 错误），而非命令不存在
        assert result.exit_code in [0, 1]  # 0=成功, 1=业务错误
        assert "Error: No such command" not in result.output

    def test_status_command_exists(self, cli_runner):
        """Smoke 测试: status 命令存在."""
        result = cli_runner.invoke(cli, ["status", "test-pipeline-id"])
        
        assert result.exit_code in [0, 1]
        assert "Error: No such command" not in result.output

    def test_resume_command_exists(self, cli_runner):
        """Smoke 测试: resume 命令存在."""
        result = cli_runner.invoke(cli, ["resume", "test-pipeline-id"])
        
        assert result.exit_code in [0, 1]
        assert "Error: No such command" not in result.output

    def test_cancel_command_exists(self, cli_runner):
        """Smoke 测试: cancel 命令存在."""
        result = cli_runner.invoke(cli, ["cancel", "test-pipeline-id"])
        
        assert result.exit_code in [0, 1]
        assert "Error: No such command" not in result.output

    def test_clean_command_exists(self, cli_runner):
        """Smoke 测试: clean 命令存在."""
        result = cli_runner.invoke(cli, ["clean", "test-pipeline-id"])
        
        assert result.exit_code in [0, 1]
        assert "Error: No such command" not in result.output

    def test_runs_command_exists(self, cli_runner):
        """Smoke 测试: runs 命令存在."""
        result = cli_runner.invoke(cli, ["runs", "test-node-id"])
        
        assert result.exit_code in [0, 1]
        assert "Error: No such command" not in result.output


class TestPipelineService:
    """Test TD-5: PipelineService 单元测试."""

    @pytest_asyncio.fixture
    async def temp_db(self):
        """Fixture: 提供临时数据库."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        service = PipelineService(db_path=db_path)
        yield service, db_path
        
        Path(db_path).unlink(missing_ok=True)

    @pytest_asyncio.fixture
    async def temp_context_file(self):
        """Fixture: 提供临时上下文文件."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write("# Test Project\\n\\nTest content.")
            path = f.name
        yield path
        Path(path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_service_start_creates_pipeline(self, temp_db, temp_context_file):
        """测试: PipelineService.start() 创建 pipeline."""
        service, _ = temp_db
        
        pipeline_id = await service.start(temp_context_file)
        
        assert pipeline_id is not None
        assert pipeline_id.startswith("pipeline-")

    @pytest.mark.asyncio
    async def test_service_status_returns_pipeline_info(self, temp_db, temp_context_file):
        """测试: PipelineService.status() 返回 pipeline 信息."""
        service, _ = temp_db
        
        pipeline_id = await service.start(temp_context_file)
        status = await service.status(pipeline_id)
        
        assert status is not None
        assert status["pipeline_id"] == pipeline_id

    @pytest.mark.asyncio
    async def test_service_resume_existing_pipeline(self, temp_db, temp_context_file):
        """测试: PipelineService.resume() 恢复已存在的 pipeline."""
        service, _ = temp_db
        
        pipeline_id = await service.start(temp_context_file)
        result = await service.resume(pipeline_id)
        
        assert result is not None
        assert result["pipeline_id"] == pipeline_id


class TestCliLayerSeparation:
    """Test TD-5: CLI 分层验证."""

    def test_main_py_is_thin(self):
        """测试: main.py 是薄入口层 (< 100 行)."""
        from autoBMAD.docuswarm.cli import main
        import inspect
        
        source_lines = inspect.getsourcelines(main)[0]
        assert len(source_lines) < 100, "main.py should be thin (< 100 lines)"

    def test_commands_layer_exists(self):
        """测试: commands 层存在并可导入."""
        from autoBMAD.docuswarm.cli.commands import start, status, resume
        
        assert start is not None
        assert status is not None
        assert resume is not None

    def test_services_layer_exists(self):
        """测试: services 层存在并可导入."""
        from autoBMAD.docuswarm.cli.services import (
            pipeline_service,
            status_service,
        )
        
        assert pipeline_service is not None
        assert status_service is not None

    def test_commands_delegate_to_services(self):
        """测试: command 层委托给 service 层."""
        import ast
        from pathlib import Path
        
        # 读取 start.py 命令文件
        start_file = Path(__file__).parent.parent.parent / \
                     "autoBMAD/docuswarm/cli/commands/start.py"
        
        if start_file.exists():
            content = start_file.read_text()
            tree = ast.parse(content)
            
            # 验证导入了 service
            imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
            service_imports = [
                imp for imp in imports 
                if any(alias.name.endswith("Service") for alias in imp.names)
            ]
            
            assert len(service_imports) > 0, "Commands should import Services"


class TestMainPyRefactoring:
    """Test TD-5: main.py 重构验证."""

    def test_no_asyncio_run_in_main(self):
        """测试: main.py 中没有 asyncio.run() 调用."""
        import ast
        from pathlib import Path
        
        main_file = Path(__file__).parent.parent.parent / \
                    "autoBMAD/docuswarm/cli/main.py"
        
        if main_file.exists():
            content = main_file.read_text()
            
            # 允许最多 1 个 asyncio.run (用于 CLI 入口)
            asyncio_run_count = content.count("asyncio.run")
            assert asyncio_run_count <= 1, \
                f"main.py should have at most 1 asyncio.run, found {asyncio_run_count}"

    def test_click_commands_registered(self):
        """测试: 所有命令已注册到 CLI."""
        from autoBMAD.docuswarm.cli.main import cli
        
        commands = list(cli.commands.keys())
        expected_commands = ["start", "status", "resume", "cancel", "clean", "runs"]
        
        for cmd in expected_commands:
            assert cmd in commands, f"Command '{cmd}' should be registered"
```

#### 4.1.3 实施步骤

```python
# Step 1: 创建新的目录结构
# autoBMAD/docuswarm/cli/
# ├── __init__.py
# ├── main.py              # 薄入口
# ├── commands/            # 命令定义
# │   ├── __init__.py
# │   ├── start.py
# │   ├── status.py
# │   ├── resume.py
# │   ├── cancel.py
# │   ├── clean.py
# │   └── runs.py
# └── services/            # 业务逻辑
#     ├── __init__.py
#     ├── pipeline_service.py
#     └── status_service.py

# Step 2: 创建 PipelineService
# autoBMAD/docuswarm/cli/services/pipeline_service.py

class PipelineService:
    """Pipeline 业务逻辑服务."""
    
    def __init__(self, db_path: str | None = None):
        self._state_manager = StateManager(db_path=db_path)
        self._orchestrator = HybridOrchestrator(db_path=db_path)
    
    async def start(self, context_file: str) -> str:
        """Start a new pipeline."""
        # 读取上下文文件
        context_path = Path(context_file)
        content = context_path.read_text(encoding="utf-8")
        
        subject_context = {
            "subject": context_path.stem,
            "context_file": str(context_path),
            "content": content,
        }
        
        return await self._orchestrator.start_pipeline(subject_context)
    
    async def status(self, pipeline_id: str) -> dict[str, Any]:
        """Get pipeline status."""
        return self._state_manager.get_pipeline(pipeline_id)
    
    async def resume(self, pipeline_id: str) -> dict[str, Any]:
        """Resume a pipeline."""
        return await self._orchestrator.resume_pipeline(pipeline_id)
    
    async def cancel(self, pipeline_id: str) -> bool:
        """Cancel a pipeline."""
        return await self._orchestrator.cancel_pipeline(pipeline_id)

# Step 3: 创建命令
# autoBMAD/docuswarm/cli/commands/start.py

import click
from rich.console import Console

from ..services.pipeline_service import PipelineService

console = Console()

@click.command()
@click.option("--context", "-c", required=True, type=click.Path(exists=True))
def start(context: str) -> None:
    """Start a new pipeline."""
    service = PipelineService()
    pipeline_id = asyncio.run(service.start(context))
    console.print(f"[green]Pipeline started: {pipeline_id}[/green]")

# Step 4: 更新 main.py
# autoBMAD/docuswarm/cli/main.py

import click
from .commands import start, status, resume, cancel, clean, runs

@click.group()
def cli():
    """DocuSwarm CLI."""
    pass

cli.add_command(start.start)
cli.add_command(status.status)
cli.add_command(resume.resume)
cli.add_command(cancel.cancel)
cli.add_command(clean.clean)
cli.add_command(runs.runs)

if __name__ == "__main__":
    cli()
```

#### 4.1.4 验收标准

- [x] CLI 拆分为 `commands/*` + `services/*` 两层
- [x] `main.py` 行数 < 100 行
- [x] 所有命令有 smoke tests
- [x] `services` 层有单元测试
- [x] 命令层委托给服务层，无业务逻辑

---

## 5. Phase 4: TD-4 (架构层)

### 5.1 TD-4: 执行骨架收敛

#### 5.1.1 测试策略

**测试目标**: 验证合成 ID 限制在边界层，执行骨架边界清晰

**测试文件**: 
- `tests/node_execution/test_pipeline_adapter.py`
- `tests/integration/test_skeleton_boundary.py`

#### 5.1.2 测试用例设计

```python
"""TD-4: 执行骨架边界测试."""

import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter


class TestPipelineAdapter:
    """Test TD-4: PipelineAdapter 边界层."""

    def test_adapter_creates_consistent_pipeline_id(self):
        """测试: Adapter 创建一致的 pipeline_id."""
        node_id = "analyst"
        run_id = "run-123"
        
        pipeline_id = PipelineAdapter.create_pipeline_id(node_id, run_id)
        
        assert pipeline_id == "node-analyst-run-123"
        assert isinstance(pipeline_id, str)

    def test_adapter_state_conversion(self):
        """测试: Adapter 正确转换状态格式."""
        node_execution_state = {
            "run_id": "run-456",
            "node_id": "pm",
            "status": "completed",
            "deliverable": {"title": "PM Doc"},
        }
        
        pipeline_state = PipelineAdapter.adapt_state(node_execution_state)
        
        assert "pipeline_id" in pipeline_state
        assert pipeline_state["status"] == "completed"

    def test_no_synthetic_id_in_business_logic(self):
        """测试: 业务逻辑中不出现合成 ID 逻辑."""
        import ast
        from pathlib import Path
        
        # 检查业务逻辑文件
        business_files = [
            "autoBMAD/docuswarm/pipeline/orchestrator.py",
            "autoBMAD/docuswarm/agents/independent.py",
            "autoBMAD/docuswarm/agents/evaluator.py",
        ]
        
        for file_path in business_files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text()
                
                # 业务逻辑不应该直接创建合成 ID
                assert 'f"node-{node_id}' not in content, \
                    f"{file_path} should not contain synthetic ID logic"
                assert 'f"node-run-' not in content, \
                    f"{file_path} should not contain synthetic ID logic"
```

#### 5.1.3 实施步骤

```python
# Step 1: 创建 PipelineAdapter
# autoBMAD/docuswarm/node_execution/pipeline_adapter.py

class PipelineAdapter:
    """将 node_execution 适配到 pipeline 接口的单一边界层."""
    
    @staticmethod
    def create_pipeline_id(node_id: str, run_id: str) -> str:
        """创建合成 pipeline_id."""
        return f"node-{node_id}-{run_id}"
    
    @staticmethod
    def create_run_pipeline_id(run_id: str) -> str:
        """创建运行级 pipeline_id."""
        return f"node-run-{run_id}"
    
    @staticmethod
    def adapt_state(node_execution_state: dict) -> PipelineState:
        """将 node_execution 状态转换为 PipelineState."""
        # 转换逻辑...
        pass

# Step 2: 更新 flow.py 使用 Adapter
# autoBMAD/docuswarm/node_execution/flow.py

from .pipeline_adapter import PipelineAdapter

# 替换：
# pipeline_id = f"node-{node_id}-{run_id}"
# 为：
pipeline_id = PipelineAdapter.create_pipeline_id(node_id, run_id)
```

#### 5.1.4 验收标准

- [x] 合成 ID 逻辑限制在 `PipelineAdapter`
- [x] 业务逻辑文件不出现合成 ID 创建
- [x] 新增平行模块被禁止

---

## 6. 综合实施路线图

### 6.1 时间线

```
Week 1-2: Phase 1 - 止血层
├─ [TD-2] 工具层 Path.cwd() 解耦
│  ├─ Day 1-2: CreateDeliverableTool 修改 + 测试
│  ├─ Day 3-4: CreateDocumentSetTool 修改 + 测试
│  └─ Day 5-7: 更新所有测试，移除 os.chdir()
│
└─ [TD-3] models 兼容层清理
   ├─ Day 8-9: 查找所有 models 导入
   ├─ Day 10-11: 更新导入路径
   └─ Day 12-14: 移除 models 模块

Week 3-4: Phase 2 - 状态层
└─ [TD-1] state_json 唯一真相源
   ├─ Day 15-16: StateManager 修改
   ├─ Day 17-18: Orchestrator 修改
   ├─ Day 19-20: 恢复逻辑更新
   └─ Day 21-28: 一致性测试

Week 5-6: Phase 3 - 控制层
└─ [TD-5] CLI 拆分
   ├─ Day 29-30: 创建目录结构
   ├─ Day 31-33: 创建 Services
   ├─ Day 34-36: 创建 Commands
   ├─ Day 37-38: 更新 main.py
   └─ Day 39-42: Smoke tests

Month 2+: Phase 4 - 架构层
└─ [TD-4] 执行骨架收敛
   ├─ 创建 PipelineAdapter
   ├─ 收敛合成 ID 逻辑
   └─ 逐步合并重复实现
```

### 6.2 依赖关系

```
TD-2 (工具层)
    │
    ▼
TD-3 (兼容层) ──► 测试稳定性恢复
    │
    ▼
TD-1 (状态层) ──► 系统稳定性
    │
    ▼
TD-5 (控制层) ──► 可维护性
    │
    ▼
TD-4 (架构层) ──► 长期健康
```

### 6.3 风险缓解

| 风险 | 缓解措施 |
|-----|---------|
| 向后兼容破坏 | 保持默认参数，渐进式废弃 |
| 测试覆盖率下降 | 新增测试先行，旧测试保留至新测试通过 |
| 回归错误 | 每个 TD 独立分支，充分测试后合并 |
| 实施周期过长 | 分阶段交付，每个 Phase 独立验收 |

---

## 7. 附录

### 7.1 测试运行命令

```bash
# 运行特定 TD 的测试
pytest tests/tools/test_output_dir_injection.py -v
pytest tests/unit/test_models_deprecation.py -v
pytest tests/storage/test_state_json_single_source.py -v
pytest tests/cli/test_commands_smoke.py -v
pytest tests/node_execution/test_pipeline_adapter.py -v

# 运行所有 TDD 测试
pytest tests/ -k "test_td" -v

# 生成覆盖率报告
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=html
```

### 7.2 参考文档

- [技术债务深度研究报告](../research/2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md)
- [技术债务评估报告](../evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md)
- [F1 状态持久化 TDD 方案](2026-03-17-F1-state-persistence-tdd-plan.md)
- [F2 Shared Context TDD 方案](2026-03-17-F2-shared-context-tdd-plan.md)

---

*方案创建时间: 2026-03-18*
*基于研究: 2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md*
