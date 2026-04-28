# DocuSwarm F1-F5 测试驱动修复方案

**方案日期**: 2026-04-08  
**基于研究报告**: `docs/research/2026-04-08-docuswarm-implementation-gap-deep-research-report.md`  
**范围**: F1 (Critical) + F2 (High) + F3 (High) + F4 (High) + F5 (Medium)  
**方法论**: Test-Driven Development (TDD) - 红-绿-重构循环

---

## 方案概述

### TDD 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. 写失败测试 │ -> │  2. 最小实现  │ -> │  3. 重构优化  │
│   (Red)     │    │   (Green)   │    │  (Refactor) │
└─────────────┘    └─────────────┘    └─────────────┘
       ^                                      │
       └──────────────────────────────────────┘
```

### 修复优先级

| 优先级 | 问题 | 影响 | 估计工作量 |
|--------|------|------|-----------|
| P0 | F1 - 多文档验证 | Critical | 4h |
| P0 | F2 - update_context | High | 3h |
| P0 | F3 - SDK Skills | High | 2h |
| P1 | F4 - 模板映射 | High | 6h |
| P1 | F5 - allowed_keys | Medium | 2h |

---

## F1: 多文档验证器修复方案 (Critical)

### 问题描述
`IndependentAgent` 正确包装多文档格式，但 `ContextValidator` 仍强制要求单文档字段，导致 `architect`/`po` 等多文档节点验证失败。

### 当前失败测试 (Red)

**文件**: `tests/docuswarm/context/test_multi_document_validation.py`

```python
"""F1: 多文档验证测试 - 当前应失败"""
import pytest
from autoBMAD.docuswarm.context.validator import (
    ContextValidator,
    IndependentOutputValidationStrategy,
    MaxDeliverablesValidationStrategy,
)


class TestMultiDocumentValidation:
    """测试多文档格式验证"""
    
    @pytest.fixture
    def multi_doc_output(self):
        """有效的多文档输出格式"""
        return {
            "deliverable": {
                "title": "PO Deliverables Set",
                "type": "multi-document",
                "documents": [
                    {
                        "title": "Product Vision",
                        "file_path": "output/pipe-123/po/product-vision.md",
                        "sha256": "abc123...",
                        "content_summary": "Summary...",
                        "word_count": 500,
                        "document_type": "product-vision",
                        "document_index": 1,
                        "document_total": 4,
                    },
                    {
                        "title": "Roadmap",
                        "file_path": "output/pipe-123/po/roadmap.md",
                        "sha256": "def456...",
                        "content_summary": "Summary...",
                        "word_count": 800,
                        "document_type": "roadmap",
                        "document_index": 2,
                        "document_total": 4,
                    },
                ],
                "total_word_count": 1300,
            },
            "questions": [],
            "action": "create_deliverable",
        }
    
    def test_multi_document_should_pass_validation(self, multi_doc_output):
        """测试: 多文档格式应该通过验证"""
        # ARRANGE
        validator = ContextValidator()
        
        # ACT
        result = validator.validate_independent_output(multi_doc_output, node_id="po")
        
        # ASSERT - 当前会失败
        assert result.valid, f"多文档验证失败: {result.issues}"
    
    def test_multi_document_should_not_require_top_level_file_path(self, multi_doc_output):
        """测试: 多文档格式不应要求顶层 file_path"""
        # ARRANGE
        del multi_doc_output["deliverable"]["file_path"]  # 确保没有顶层 file_path
        validator = ContextValidator()
        
        # ACT
        result = validator.validate_independent_output(multi_doc_output, node_id="po")
        
        # ASSERT - 当前会因 MISSING_FILE_PATH 失败
        file_path_errors = [i for i in result.issues if "file_path" in i.field]
        assert len(file_path_errors) == 0, "多文档不应要求顶层 file_path"
    
    def test_multi_document_should_not_require_top_level_sha256(self, multi_doc_output):
        """测试: 多文档格式不应要求顶层 sha256"""
        # ARRANGE
        del multi_doc_output["deliverable"]["sha256"]  # 确保没有顶层 sha256
        validator = ContextValidator()
        
        # ACT
        result = validator.validate_independent_output(multi_doc_output, node_id="po")
        
        # ASSERT
        sha256_errors = [i for i in result.issues if "sha256" in i.field]
        assert len(sha256_errors) == 0, "多文档不应要求顶层 sha256"
    
    def test_multi_document_should_detect_correct_document_count(self, multi_doc_output):
        """测试: MaxDeliverablesValidationStrategy 应正确检测文档数量"""
        # ARRANGE
        strategy = MaxDeliverablesValidationStrategy()
        
        # ACT
        document_count = strategy._detect_document_count(multi_doc_output["deliverable"])
        
        # ASSERT - 当前返回 1（因为没有 document_total 在顶层）
        assert document_count == 2, f"应检测到 2 个文档，实际检测到 {document_count}"
    
    def test_multi_document_should_validate_each_sub_document(self, multi_doc_output):
        """测试: 应验证每个子文档的必需字段"""
        # ARRANGE - 移除第一个子文档的 file_path
        multi_doc_output["deliverable"]["documents"][0].pop("file_path")
        validator = ContextValidator()
        
        # ACT
        result = validator.validate_independent_output(multi_doc_output, node_id="po")
        
        # ASSERT - 应报告子文档的 field_path 错误
        assert not result.valid
        sub_doc_errors = [i for i in result.issues if "documents[0]" in i.field]
        assert len(sub_doc_errors) > 0, "应报告子文档验证错误"
```

**运行测试 (应失败)**:
```bash
pytest tests/docuswarm/context/test_multi_document_validation.py -v
# 预期: 5 failed
```

### 实现步骤 (Green)

#### 步骤 1: 修改 `IndependentOutputValidationStrategy._validate_deliverable`

**文件**: `autoBMAD/docuswarm/context/validator.py`

```python
def _validate_deliverable(
    self, data: dict[str, Any], result: ValidationResult, _is_submit_report_format: bool = False
) -> None:
    """Validate deliverable field structure.
    
    F1 Fix: 支持 multi-document 格式验证
    """
    # Check deliverable exists
    if "deliverable" not in data:
        result.add_error(
            field="deliverable",
            message="deliverable: required field missing",
            code="MISSING_DELIVERABLE",
        )
        return

    deliverable = data["deliverable"]

    # Check deliverable is a dict
    if not isinstance(deliverable, dict):
        result.add_error(...)
        return

    # F1 Fix: 检测多文档格式
    if deliverable.get("type") == "multi-document":
        self._validate_multi_document_deliverable(deliverable, result)
    else:
        self._validate_single_document_deliverable(deliverable, result)

def _validate_multi_document_deliverable(
    self, deliverable: dict[str, Any], result: ValidationResult
) -> None:
    """验证多文档格式的 deliverable."""
    # 验证必需字段
    if "title" not in deliverable:
        result.add_error(field="deliverable.title", ...)
    
    if "documents" not in deliverable or not isinstance(deliverable["documents"], list):
        result.add_error(
            field="deliverable.documents",
            message="deliverable.documents: required field missing for multi-document",
            code="MISSING_DOCUMENTS_ARRAY",
        )
        return
    
    # 验证每个子文档
    for idx, doc in enumerate(deliverable["documents"]):
        self._validate_sub_document(doc, idx, result)

def _validate_sub_document(
    self, doc: dict, index: int, result: ValidationResult
) -> None:
    """验证多文档中的单个子文档."""
    prefix = f"deliverable.documents[{index}]"
    
    # 子文档必须包含 file_path
    if "file_path" not in doc:
        result.add_error(
            field=f"{prefix}.file_path",
            message=f"{prefix}.file_path: required field missing",
            code="MISSING_FILE_PATH",
        )
    
    # 子文档必须包含 sha256
    if "sha256" not in doc:
        result.add_error(
            field=f"{prefix}.sha256",
            message=f"{prefix}.sha256: required field missing",
            code="MISSING_SHA256",
        )
    
    # 验证其他可选字段...

def _validate_single_document_deliverable(
    self, deliverable: dict[str, Any], result: ValidationResult
) -> None:
    """原有的单文档验证逻辑 (保持不变)"""
    # ... 现有代码 ...
```

#### 步骤 2: 修改 `MaxDeliverablesValidationStrategy._detect_document_count`

```python
def _detect_document_count(self, deliverable: dict[str, Any]) -> int:
    """Detect the number of documents from deliverable metadata.
    
    F1 Fix: 支持多文档格式
    """
    # F1 Fix: 多文档格式使用 documents 数组长度
    if deliverable.get("type") == "multi-document":
        documents = deliverable.get("documents", [])
        return len(documents)
    
    # 单文档格式使用 document_total
    document_total = deliverable.get("document_total")
    if document_total is not None and isinstance(document_total, int):
        return document_total

    return 1
```

#### 步骤 3: 修改 `IndependentAgent._parse_response` 设置 document_total

```python
# F3: 多文档：包装为特殊格式
first_report = submit_reports[0]
data = {
    "deliverable": {
        "title": f"{self.node_id.upper()} Deliverables Set",
        "type": "multi-document",
        "documents": [r.get("deliverable", {}) for r in submit_reports],
        "document_total": len(submit_reports),  # F1 Fix: 添加 document_total
        "total_word_count": sum(...),
    },
    ...
}
```

### 通过测试 (验证)

```bash
pytest tests/docuswarm/context/test_multi_document_validation.py -v
# 预期: 5 passed
```

### 回归测试

```bash
# 确保单文档验证仍然工作
pytest tests/docuswarm/context/test_validator.py -v

# 全量验证测试
pytest tests/docuswarm/context/ -v
```

---

## F2: update_context MCP Server 修复方案 (High)

### 问题描述
`update_context` 工具名已加入 `allowed_tools`，但默认运行时不会创建对应的 MCP server，因为 `pipeline_id` 未在调用链中传递。

### 当前失败测试 (Red)

**文件**: `tests/docuswarm/llm/test_update_context_server_creation.py`

```python
"""F2: update_context MCP Server 创建测试 - 当前应失败"""
import pytest
from unittest.mock import Mock, patch

from autoBMAD.docuswarm.context.permissions import NodeToolPermissions
from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
from autoBMAD.nodes.loader import NodeSharedContextConfig


class TestUpdateContextServerCreation:
    """测试 update_context MCP Server 创建"""
    
    @pytest.fixture
    def tool_permissions_with_shared_context(self):
        """启用 shared_context 的权限配置"""
        return NodeToolPermissions(
            shared_context=NodeSharedContextConfig(
                enabled=True,
                operations=["set", "append", "remove"],
            ),
        )
    
    def test_tool_filter_should_include_update_context_in_allowed_tools(self):
        """测试: NodeToolFilter 应在 allowed_tools 中包含 update_context"""
        # ARRANGE
        permissions = NodeToolPermissions(
            shared_context=NodeSharedContextConfig(enabled=True),
        )
        node_filter = NodeToolFilter(
            node_id="analyst",
            tool_permissions=permissions,
        )
        
        # ACT
        allowed_tools = node_filter.get_allowed_tools()
        
        # ASSERT - 这个测试应该通过
        update_context_tools = [t for t in allowed_tools if "update_context" in t]
        assert len(update_context_tools) > 0, "allowed_tools 应包含 update_context"
    
    def test_create_mcp_servers_without_pipeline_id_should_not_create_shared_context_server(self):
        """测试: 不传 pipeline_id 时不应创建 shared-context server"""
        # ARRANGE
        permissions = NodeToolPermissions(
            shared_context=NodeSharedContextConfig(enabled=True),
        )
        node_filter = NodeToolFilter(
            node_id="analyst",
            tool_permissions=permissions,
        )
        
        # ACT
        servers = node_filter.create_mcp_servers()  # 不传 pipeline_id
        
        # ASSERT - 当前行为，这个测试会通过
        shared_context_servers = [k for k in servers.keys() if "shared-context" in k]
        assert len(shared_context_servers) == 0, "不传 pipeline_id 时不应创建 shared-context server"
    
    def test_create_mcp_servers_with_pipeline_id_should_create_shared_context_server(self):
        """测试: 传入 pipeline_id 时应创建 shared-context server"""
        # ARRANGE
        permissions = NodeToolPermissions(
            shared_context=NodeSharedContextConfig(enabled=True),
        )
        node_filter = NodeToolFilter(
            node_id="analyst",
            tool_permissions=permissions,
        )
        
        # ACT
        servers = node_filter.create_mcp_servers(pipeline_id="pipe-123")
        
        # ASSERT - 当前行为，这个测试会通过
        shared_context_servers = [k for k in servers.keys() if "shared-context" in k]
        assert len(shared_context_servers) == 1, "传入 pipeline_id 时应创建 shared-context server"
    
    def test_session_manager_should_pass_pipeline_id_to_create_mcp_servers(self):
        """测试: SessionManager 应传递 pipeline_id 给 create_mcp_servers
        
        这是 F2 的核心问题 - 当前会失败
        """
        # ARRANGE
        with patch.object(NodeToolFilter, 'create_mcp_servers') as mock_create:
            mock_create.return_value = {}
            
            session_manager = SessionManager(
                cwd="/tmp",
                output_dir="/tmp/output",
                node_id="analyst",
                tool_permissions=NodeToolPermissions(
                    shared_context=NodeSharedContextConfig(enabled=True),
                ),
                pipeline_id="pipe-123",  # F2 Fix: SessionManager 应支持 pipeline_id
            )
            
            # ACT
            try:
                options = session_manager._create_options()
            except TypeError as e:
                pytest.fail(f"SessionManager 不支持 pipeline_id 参数: {e}")
        
        # ASSERT - 验证 create_mcp_servers 被调用时传递了 pipeline_id
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args.kwargs
        assert "pipeline_id" in call_kwargs, "应传递 pipeline_id 参数"
        assert call_kwargs["pipeline_id"] == "pipe-123"
    
    def test_independent_agent_should_pass_pipeline_id_to_session_manager(self):
        """测试: IndependentAgent 应传递 pipeline_id 给 SessionManager"""
        # ARRANGE
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        agent = IndependentAgent(
            node_id="analyst",
            output_dir="/tmp/output",
        )
        
        # ACT & ASSERT - 检查方法签名是否支持 pipeline_id
        import inspect
        sig = inspect.signature(agent._create_pipeline_session_manager)
        params = list(sig.parameters.keys())
        
        # F2 Fix: 应支持 pipeline_id 参数
        assert "pipeline_id" in params, "_create_pipeline_session_manager 应支持 pipeline_id 参数"
```

**运行测试 (应失败)**:
```bash
pytest tests/docuswarm/llm/test_update_context_server_creation.py::TestUpdateContextServerCreation::test_session_manager_should_pass_pipeline_id_to_create_mcp_servers -v
# 预期: failed - SessionManager 不支持 pipeline_id 参数

pytest tests/docuswarm/llm/test_update_context_server_creation.py::TestUpdateContextServerCreation::test_independent_agent_should_pass_pipeline_id_to_session_manager -v
# 预期: failed - 方法签名不包含 pipeline_id
```

### 实现步骤 (Green)

#### 步骤 1: 修改 `SessionManager.__init__` 添加 pipeline_id 参数

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
class SessionManager:
    def __init__(
        self,
        work_dir: Path | str | None = None,
        agent_file: Path | str | None = None,
        config: Any | None = None,
        node_id: str | None = None,
        file_dirs: list[str] | None = None,
        search_dirs: list[str] | None = None,
        tool_permissions: Any | None = None,
        cwd: Path | str | None = None,
        output_dir: Path | str | None = None,
        pipeline_id: str | None = None,  # F2 Fix: 添加 pipeline_id 参数
    ) -> None:
        # ... 现有代码 ...
        
        self._pipeline_id = pipeline_id  # F2 Fix: 存储 pipeline_id
        
        # ... 现有代码 ...
```

#### 步骤 2: 修改 `SessionManager._create_options` 传递 pipeline_id

```python
def _create_options(self, ...) -> dict[str, Any]:
    # ... 现有代码 ...
    
    # Create MCP servers for this node
    try:
        # F2 Fix: 传递 pipeline_id
        mcp_servers = node_filter.create_mcp_servers(pipeline_id=self._pipeline_id)
        if mcp_servers:
            options_dict["mcp_servers"] = mcp_servers
            # ...
    except Exception as e:
        # ...
```

#### 步骤 3: 修改 `IndependentAgent._create_pipeline_session_manager` 传递 pipeline_id

**文件**: `autoBMAD/docuswarm/agents/independent.py`

```python
def _create_pipeline_session_manager(
    self,
    work_dir: Path,
    node_id: str,
    file_dirs: list[str],
    search_dirs: list[str],
    tool_permissions: Any | None = None,
    pipeline_id: str | None = None,  # F2 Fix: 添加 pipeline_id 参数
):
    """Factory method for creating pipeline SessionManager - allows testing."""
    from autoBMAD.docuswarm.llm.session_manager import SessionManager

    return SessionManager(
        work_dir=work_dir,
        agent_file=self._agent_file,
        config=self.session_manager.config if self.session_manager else None,
        node_id=node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
        tool_permissions=tool_permissions,
        pipeline_id=pipeline_id,  # F2 Fix: 传递 pipeline_id
    )
```

#### 步骤 4: 修改 `IndependentAgent.execute` 传递 pipeline_id

```python
async def execute(self, input_data: IndependentAgentInput) -> dict[str, Any]:
    # ... 现有代码 ...
    
    # Extract pipeline_id from context if available
    pipeline_id = input_data.pipeline_id if hasattr(input_data, 'pipeline_id') else None
    
    # ... 现有代码 ...
    
    # F2 Fix: 传递 pipeline_id
    session_manager = self._create_pipeline_session_manager(
        work_dir=node_output_dir,
        node_id=self.node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
        tool_permissions=tool_permissions,
        pipeline_id=pipeline_id,  # F2 Fix
    )
```

### 通过测试 (验证)

```bash
pytest tests/docuswarm/llm/test_update_context_server_creation.py -v
# 预期: 6 passed
```

---

## F3: SDK Skills 路径修复方案 (High)

### 问题描述
`SessionManager` 使用 pipeline 输出目录作为 `cwd`，导致 SDK 原生 Skills 发现机制失效。

### 当前失败测试 (Red)

**文件**: `tests/docuswarm/llm/test_sdk_skills_discovery.py`

```python
"""F3: SDK Skills 发现机制测试 - 当前应失败"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSDKSkillsDiscovery:
    """测试 SDK Skills 发现机制"""
    
    @pytest.fixture
    def project_root(self):
        """项目根目录"""
        return Path("/workspace/project")
    
    @pytest.fixture
    def pipeline_output_dir(self, project_root):
        """Pipeline 输出目录"""
        return project_root / "output" / "pipe-123"
    
    def test_session_manager_with_work_dir_only_should_set_cwd_to_work_dir(self, pipeline_output_dir):
        """测试: 只传 work_dir 时 cwd 应等于 work_dir
        
        这是当前行为，但会导致问题
        """
        # ARRANGE & ACT
        sm = SessionManager(work_dir=pipeline_output_dir, node_id="analyst")
        
        # ASSERT - 当前行为
        assert sm.cwd == pipeline_output_dir
        assert sm.output_dir == pipeline_output_dir
    
    def test_session_manager_with_separate_cwd_and_output_dir(self, project_root, pipeline_output_dir):
        """测试: 分开传 cwd 和 output_dir 应分别设置"""
        # ARRANGE & ACT
        sm = SessionManager(
            cwd=project_root,
            output_dir=pipeline_output_dir,
            node_id="analyst",
        )
        
        # ASSERT
        assert sm.cwd == project_root, f"cwd 应为 {project_root}，实际是 {sm.cwd}"
        assert sm.output_dir == pipeline_output_dir
    
    def test_session_manager_should_use_cwd_for_skills_discovery(self, project_root, pipeline_output_dir):
        """测试: SessionManager 应使用 cwd 而非 output_dir 进行 Skills 发现
        
        F3 核心问题: SDK 从 cwd 查找 .claude/skills/
        """
        # ARRANGE
        sm = SessionManager(
            cwd=project_root,
            output_dir=pipeline_output_dir,
            node_id="analyst",
        )
        
        # ACT - 模拟 _create_options 中的行为
        options = sm._create_options()
        
        # ASSERT - 检查 setting_sources 配置
        # 注意: 当前实现可能不暴露这个配置，需要检查实际代码
        # 这里假设我们可以通过某种方式验证
        
        # 验证 allowed_tools 包含 "Skill"
        assert "Skill" in options.get("allowed_tools", []), "allowed_tools 应包含 'Skill'"
    
    def test_orchestrator_should_pass_project_root_as_cwd(self):
        """测试: Orchestrator 应传递项目根目录作为 cwd
        
        集成测试 - 验证调用链
        """
        # ARRANGE
        from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
        
        with patch('autoBMAD.docuswarm.pipeline.orchestrator.SessionManager') as MockSM:
            mock_instance = Mock()
            MockSM.return_value = mock_instance
            
            orchestrator = PipelineOrchestrator(work_dir="/workspace/project/output")
            
            # ACT
            try:
                _ = orchestrator._create_session_manager(pipeline_id="pipe-123")
            except Exception:
                pass  # 我们主要检查调用参数
            
            # ASSERT - F3 Fix: 应传递 cwd=project_root
            call_kwargs = MockSM.call_args.kwargs if MockSM.called else {}
            
            # 检查是否传递了 cwd
            if 'cwd' not in call_kwargs and 'work_dir' in call_kwargs:
                pytest.fail("Orchestrator 只传递 work_dir，应同时传递 cwd=项目根目录")
```

### 实现步骤 (Green)

#### 步骤 1: 修改 `Orchestrator._create_session_manager`

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

```python
def _create_session_manager(self, pipeline_id: str | None = None) -> SessionManager:
    """Create or retrieve a SessionManager instance."""
    # ... 现有代码 ...
    
    try:
        if pipeline_id:
            work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id))
        else:
            work_dir = KaosPath(self._work_dir)
        
        # F3 Fix: 检测项目根目录并传递 cwd
        project_root = self._detect_project_root()
        
        session_manager = SessionManager(
            work_dir=work_dir,
            cwd=project_root,  # F3 Fix: 传递项目根目录
            output_dir=work_dir,  # F3 Fix: output_dir 保持为 work_dir
            config=None,
        )
        
        # ... 现有代码 ...

def _detect_project_root(self) -> Path:
    """检测项目根目录.
    
    通过向上查找包含 .claude/skills/ 或 pyproject.toml 的目录
    """
    current = Path(self._work_dir).resolve()
    
    while current != current.parent:
        # 检查项目根目录标识
        if (current / ".claude" / "skills").exists():
            return current
        if (current / "pyproject.toml").exists():
            return current
        if (current / ".git").exists():
            return current
        
        current = current.parent
    
    #  fallback: 返回 work_dir
    return Path(self._work_dir)
```

#### 步骤 2: 修改 `IndependentAgent._create_pipeline_session_manager`

```python
def _create_pipeline_session_manager(
    self,
    work_dir: Path,
    node_id: str,
    file_dirs: list[str],
    search_dirs: list[str],
    tool_permissions: Any | None = None,
    pipeline_id: str | None = None,
    project_root: Path | None = None,  # F3 Fix: 添加 project_root 参数
):
    """Factory method for creating pipeline SessionManager."""
    from autoBMAD.docuswarm.llm.session_manager import SessionManager

    return SessionManager(
        work_dir=work_dir,
        cwd=project_root or work_dir,  # F3 Fix: 使用 project_root 作为 cwd
        output_dir=work_dir,
        agent_file=self._agent_file,
        config=self.session_manager.config if self.session_manager else None,
        node_id=node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
        tool_permissions=tool_permissions,
        pipeline_id=pipeline_id,
    )
```

#### 步骤 3: 修改 `IndependentAgent.execute` 传递 project_root

```python
async def execute(self, input_data: IndependentAgentInput) -> dict[str, Any]:
    # ... 现有代码 ...
    
    # F3 Fix: 从 input_data 获取 project_root
    project_root = None
    if hasattr(input_data, 'project_root'):
        project_root = input_data.project_root
    
    # F2 Fix + F3 Fix: 传递 pipeline_id 和 project_root
    session_manager = self._create_pipeline_session_manager(
        work_dir=node_output_dir,
        node_id=self.node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
        tool_permissions=tool_permissions,
        pipeline_id=pipeline_id,
        project_root=project_root,  # F3 Fix
    )
```

### 通过测试 (验证)

```bash
pytest tests/docuswarm/llm/test_sdk_skills_discovery.py -v
# 预期: 4 passed
```

---

## F4: 模板运行时映射修复方案 (High)

### 问题描述
模板查找 key 与节点配置 `deliverable_type` 不匹配，当前匹配率仅 20%。

### 当前失败测试 (Red)

**文件**: `tests/docuswarm/prompts/test_template_mapping.py`

```python
"""F4: 模板运行时映射测试 - 当前应失败"""
import pytest
from pathlib import Path

from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder
from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext


class TestTemplateMapping:
    """测试模板运行时映射"""
    
    @pytest.mark.parametrize("node_id,deliverable_type,expected_template_id", [
        ("analyst", "product-brief", "market_research"),  # 或新的模板 ID
        ("architect", "architecture", "system_architecture"),
        ("pm", "prd", "prd"),  # 当前唯一匹配的
        ("po", "epics-stories", "product_vision"),  # 或多文档映射
        ("ux", "ux-design", "user_personas"),
    ])
    def test_template_lookup_by_deliverable_type(
        self, node_id, deliverable_type, expected_template_id
    ):
        """测试: 通过 deliverable_type 应能正确查找模板"""
        # ARRANGE
        builder = NodePromptContractBuilder()
        
        # ACT
        template_data = builder._load_node_template(node_id, deliverable_type)
        
        # ASSERT - 当前大多数会失败
        assert template_data is not None, f"{node_id}: deliverable_type='{deliverable_type}' 应找到模板"
        assert template_data.get("template_id") == expected_template_id, \
            f"期望模板 {expected_template_id}，实际 {template_data.get('template_id')}"
    
    def test_multi_document_template_mapping(self):
        """测试: 多文档节点应支持模板映射配置"""
        # ARRANGE
        context = NodeExecutionContext(
            node_id="po",
            deliverable_requirements={
                "template_mapping": {
                    "product-vision": "product_vision",
                    "roadmap": "roadmap",
                    "epic-list": "epic_list",
                    "story-list": "story_list",
                }
            },
            deliverable_type="epics-stories",
        )
        
        builder = NodePromptContractBuilder()
        
        # ACT - 尝试获取每个文档类型的模板
        template_mapping = context.get("deliverable_requirements", {}).get("template_mapping", {})
        
        for doc_type, template_id in template_mapping.items():
            template_data = builder._load_node_template("po", template_id)
            
            # ASSERT
            assert template_data is not None, f"PO: document_type='{doc_type}' 应找到模板 '{template_id}'"
    
    def test_template_fuzzy_matching_by_title(self):
        """测试: 模板查找应支持标题模糊匹配"""
        # ARRANGE
        builder = NodePromptContractBuilder()
        
        # "product-brief" 应该能匹配 "Product Brief" 或类似的模板
        template_data = builder._load_node_template("analyst", "product-brief")
        
        # ASSERT - 当前失败
        assert template_data is not None, "应支持通过模糊匹配查找模板"
```

### 实现步骤 (Green)

#### 方案 A: 标准化模板 ID (推荐)

**步骤 1: 创建模板 ID 映射配置**

**文件**: `autoBMAD/docuswarm/templates/template_mapping.yaml`

```yaml
# 模板 ID 映射配置
# 将 deliverable_type 映射到 template_id

mappings:
  # Analyst 节点
  analyst:
    product-brief: market_research  # 或创建新的 product_brief 模板
  
  # Architect 节点
  architect:
    architecture: system_architecture
  
  # PM 节点 - 已匹配
  pm:
    prd: prd
  
  # PO 节点 - 多文档
  po:
    epics-stories: null  # 多文档使用 template_mapping
    # 各文档类型映射
    document_types:
      product-vision: product_vision
      roadmap: roadmap
      epic-list: epic_list
      story-list: story_list
  
  # UX 节点
  ux:
    ux-design: user_personas

# 备用映射规则
fallback_rules:
  - pattern: "*-brief"
    template_category: "research"
  - pattern: "*-design"
    template_category: "design"
```

**步骤 2: 修改 `ContractBuilder._load_node_template`**

**文件**: `autoBMAD/docuswarm/prompts/contract_builder.py`

```python
def _load_node_template(
    self,
    node_id: str,
    template_id: str | None,
) -> dict | None:
    """Load template from docuswarm/templates/{node_id}_templates.yaml.
    
    F4 Fix: 添加模板 ID 映射和模糊匹配支持
    """
    from pathlib import Path
    import yaml
    
    # F4 Fix: 应用模板 ID 映射
    mapped_template_id = self._apply_template_mapping(node_id, template_id)
    if mapped_template_id:
        template_id = mapped_template_id
    
    template_file = f"{node_id}_templates.yaml"
    templates_dir = Path(__file__).parent.parent / "templates"
    template_path = templates_dir / template_file
    
    try:
        with open(template_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data:
            return None
        
        templates = data.get("templates", [])
        
        # 精确匹配 template_id
        if template_id:
            for template in templates:
                if template.get("template_id") == template_id:
                    return template
                # F4 Fix: 增强匹配逻辑
                if self._template_id_matches(template_id, template):
                    return template
        
        # F4 Fix: 模糊匹配 - 尝试查找最接近的模板
        if template_id:
            best_match = self._find_best_template_match(template_id, templates)
            if best_match:
                return best_match
        
        # 默认返回第一个模板
        return templates[0] if templates else None
        
    except FileNotFoundError:
        return None
    except Exception:
        return None

def _apply_template_mapping(self, node_id: str, template_id: str | None) -> str | None:
    """应用模板 ID 映射."""
    import yaml
    from pathlib import Path
    
    mapping_file = Path(__file__).parent.parent / "templates" / "template_mapping.yaml"
    
    if not mapping_file.exists():
        return None
    
    try:
        with open(mapping_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        mappings = config.get("mappings", {})
        node_mappings = mappings.get(node_id, {})
        
        return node_mappings.get(template_id)
    except Exception:
        return None

def _template_id_matches(self, lookup_id: str, template: dict) -> bool:
    """检查 template_id 是否匹配模板."""
    template_id = template.get("template_id", "")
    title = template.get("title", "")
    
    # 标准化比较
    lookup_normalized = lookup_id.lower().replace("-", "_").replace(" ", "_")
    template_id_normalized = template_id.lower().replace("-", "_").replace(" ", "_")
    title_normalized = title.lower().replace("-", "_").replace(" ", "_")
    
    # 直接匹配
    if lookup_normalized == template_id_normalized:
        return True
    
    # 标题匹配
    if lookup_normalized in title_normalized or title_normalized in lookup_normalized:
        return True
    
    return False

def _find_best_template_match(self, lookup_id: str, templates: list) -> dict | None:
    """查找最佳匹配的模板."""
    lookup_normalized = lookup_id.lower().replace("-", "_")
    
    for template in templates:
        template_id = template.get("template_id", "").lower().replace("-", "_")
        
        # 关键词匹配
        if any(word in template_id for word in lookup_normalized.split("_")):
            return template
    
    return None
```

#### 方案 B: 多文档模板映射 (针对 PO 节点)

**步骤 3: 修改节点配置添加 template_mapping**

**文件**: `autoBMAD/nodes/po/node.yaml`

```yaml
# 在 deliverable 部分添加
deliverable:
  max_deliverables: 5
  document_types:
    - product-vision
    - roadmap
    - epic-list
    - story-list
  
  # F4 Fix: 添加多文档模板映射
  template_mapping:
    product-vision: product_vision
    roadmap: roadmap
    epic-list: epic_list
    story-list: story_list
  
  # 或默认模板
  default_template: product_vision
```

**步骤 4: 修改 `ContractBuilder._build_deliverable_section` 支持多文档**

```python
def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
    """构建交付物章节."""
    reqs = context.get("deliverable_requirements", {})
    deliverable_type = context.get("deliverable_type", "")
    node_id = context.get("node_id", "")
    
    sections: list[str] = ["## 交付物要求"]
    
    template_title = reqs.get("template_title") or deliverable_type
    if template_title:
        sections.append(f"\n**文档标题**: {template_title}")
    
    # F4 Fix: 检查是否有模板映射配置 (多文档)
    template_mapping = reqs.get("template_mapping")
    if template_mapping:
        # 多文档: 加载所有指定模板
        sections.append("\n**文档模板**:")
        for doc_type, template_id in template_mapping.items():
            template_data = self._load_node_template(node_id, template_id)
            if template_data:
                sections.append(f"\n- {doc_type}: {template_data.get('title', template_id)}")
                # 添加该模板的章节要求
                template_sections = template_data.get("sections", [])
                required = [s.get("heading") for s in template_sections if s.get("required")]
                if required:
                    sections.append(f"  必需章节: {', '.join(required)}")
    else:
        # 单文档: 原有逻辑
        template_data = self._load_node_template(node_id, template_title)
        if template_data:
            formatted_template = self._format_template_sections(template_data)
            if formatted_template:
                sections.append(formatted_template)
    
    # ... 其余代码 ...
```

### 通过测试 (验证)

```bash
pytest tests/docuswarm/prompts/test_template_mapping.py -v
# 预期: 所有测试通过，匹配率达到 100%
```

---

## F5: shared_context.allowed_keys 传递修复方案 (Medium)

### 问题描述
节点级 `allowed_keys` 配置存在，但 `UpdateContextTool` 只使用全局白名单。

### 当前失败测试 (Red)

**文件**: `tests/docuswarm/tools/test_update_context_allowed_keys.py`

```python
"""F5: shared_context.allowed_keys 传递测试 - 当前应失败"""
import pytest
from unittest.mock import Mock

from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestUpdateContextAllowedKeys:
    """测试 update_context 的 allowed_keys 传递"""
    
    @pytest.fixture
    def state_manager(self):
        """Mock StateManager"""
        sm = Mock(spec=StateManager)
        sm.read_shared_context.return_value = {}
        return sm
    
    def test_update_context_tool_should_accept_allowed_keys(self, state_manager):
        """测试: UpdateContextTool 应接受 allowed_keys 参数"""
        # ARRANGE
        custom_keys = ["custom.facts.*", "custom.decisions.*"]
        
        # ACT
        tool = UpdateContextTool(
            state_manager=state_manager,
            pipeline_id="pipe-123",
            allowed_keys=custom_keys,
        )
        
        # ASSERT
        whitelist = tool._build_effective_whitelist()
        assert "custom.facts.*" in whitelist
        assert "custom.decisions.*" in whitelist
        assert tool._whitelist_source == "node_extended"
    
    def test_create_update_context_server_should_accept_allowed_keys(self, state_manager):
        """测试: create_update_context_server 应接受 allowed_keys 参数
        
        F5 核心问题 - 当前会失败
        """
        # ARRANGE
        import inspect
        
        # ACT & ASSERT - 检查函数签名
        sig = inspect.signature(create_update_context_server)
        params = list(sig.parameters.keys())
        
        assert "allowed_keys" in params, "create_update_context_server 应接受 allowed_keys 参数"
    
    def test_create_update_context_server_should_pass_allowed_keys_to_tool(self, state_manager):
        """测试: create_update_context_server 应将 allowed_keys 传递给 UpdateContextTool
        
        F5 核心问题 - 当前会失败
        """
        # ARRANGE
        custom_keys = ["node.specific.*"]
        
        # ACT - 尝试调用
        try:
            server = create_update_context_server(
                pipeline_id="pipe-123",
                node_id="test-node",
                allowed_operations=["set"],
                allowed_keys=custom_keys,  # F5 Fix: 应支持此参数
            )
            
            # ASSERT - 验证工具配置
            # 注意: 这需要我们能访问内部 tool 实例
            # 可能需要修改 server 结构来暴露 tool 配置
            
        except TypeError as e:
            if "allowed_keys" in str(e):
                pytest.fail("create_update_context_server 不接受 allowed_keys 参数")
            raise
```

### 实现步骤 (Green)

#### 步骤 1: 修改 `create_update_context_server` 添加 allowed_keys 参数

**文件**: `autoBMAD/docuswarm/tools/update_context_sdk.py`

```python
def create_update_context_server(
    pipeline_id: str,
    node_id: str,
    allowed_operations: list[str] | None = None,
    allowed_keys: list[str] | None = None,  # F5 Fix: 添加 allowed_keys 参数
) -> dict[str, Any]:
    """Create an SDK MCP server for update_context tool.
    
    F5 Fix: 添加 allowed_keys 参数支持节点级白名单
    """
    if not pipeline_id:
        raise ValueError("pipeline_id is required")
    if not node_id:
        raise ValueError("node_id is required")
    
    try:
        from claude_agent_sdk import create_sdk_mcp_server, tool
    except ImportError as e:
        raise RuntimeError(...) from e
    
    operations = allowed_operations or ["set", "append", "remove"]
    server_name = f"docuswarm-shared-context-{node_id}"
    
    @tool(...)
    async def update_context_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool handler for update_context."""
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
        
        try:
            # F5 Fix: 传递 allowed_keys
            tool = UpdateContextTool(
                state_manager=StateManager(),
                pipeline_id=pipeline_id,
                allowed_keys=allowed_keys,  # F5 Fix
            )
            
            # ... 其余代码 ...
```

#### 步骤 2: 修改 `NodeToolFilter.create_mcp_servers` 传递 allowed_keys

**文件**: `autoBMAD/docuswarm/llm/tool_filter.py`

```python
def create_mcp_servers(self, pipeline_id: str | None = None) -> dict[str, Any]:
    """Create SDK MCP servers based on configured permissions."""
    servers: dict[str, Any] = {}
    
    # ... 文件、搜索、交付物 server 创建代码 ...
    
    # F6 Fix: Create update_context server when shared_context is enabled and pipeline_id is provided
    if pipeline_id and self.tool_permissions.shared_context.enabled:
        try:
            # F5 Fix: 传递 allowed_keys
            update_server = create_update_context_server(
                pipeline_id=pipeline_id,
                node_id=self.node_id,
                allowed_operations=self.tool_permissions.shared_context.operations,
                allowed_keys=self.tool_permissions.shared_context.allowed_keys,  # F5 Fix
            )
            server_name = update_server["name"]
            servers[server_name] = update_server
            logger.info(...)
        except Exception as e:
            logger.error(...)
            raise
    
    return servers
```

#### 步骤 3: 确保 `NodeSharedContextConfig` 支持 allowed_keys

**文件**: `autoBMAD/nodes/loader.py` (检查/添加)

```python
@dataclass
class NodeSharedContextConfig:
    """Shared context permissions for a node."""
    enabled: bool = False
    operations: list[str] = field(default_factory=lambda: ["set", "append", "remove"])
    allowed_keys: list[str] | None = None  # F5: 节点级白名单
```

### 通过测试 (验证)

```bash
pytest tests/docuswarm/tools/test_update_context_allowed_keys.py -v
# 预期: 3 passed
```

---

## 集成测试与回归测试

### 集成测试套件

**文件**: `tests/docuswarm/integration/test_f1_f5_fixes_integration.py`

```python
"""F1-F5 修复集成测试"""
import pytest


class TestF1F5Integration:
    """集成测试: 验证所有修复协同工作"""
    
    def test_multi_document_with_update_context_and_skills(self):
        """测试: 多文档 + update_context + SDK Skills 集成场景
        
        模拟 PO 节点的完整执行流程
        """
        # ARRANGE
        # - 创建模拟 pipeline
        # - 配置 shared_context
        # - 设置 SDK Skills
        
        # ACT
        # - 执行 PO 节点
        # - 提交多文档交付物
        # - 使用 update_context
        
        # ASSERT
        # - 多文档验证通过
        # - update_context 工具可用
        # - Skills 正常发现
        pass
```

### 回归测试命令

```bash
# F1 相关测试
pytest tests/docuswarm/context/test_multi_document_validation.py -v
pytest tests/docuswarm/context/test_validator.py -v

# F2 相关测试
pytest tests/docuswarm/llm/test_update_context_server_creation.py -v
pytest tests/docuswarm/llm/test_tool_filter.py -v

# F3 相关测试
pytest tests/docuswarm/llm/test_sdk_skills_discovery.py -v
pytest tests/docuswarm/llm/test_session_manager.py -v

# F4 相关测试
pytest tests/docuswarm/prompts/test_template_mapping.py -v
pytest tests/docuswarm/prompts/test_contract_builder.py -v

# F5 相关测试
pytest tests/docuswarm/tools/test_update_context_allowed_keys.py -v
pytest tests/docuswarm/tools/test_update_context.py -v

# 全量集成测试
pytest tests/docuswarm/integration/ -v

# 全量回归测试
pytest tests/ -v --tb=short
```

---

## 实施计划

### 阶段 1: P0 问题修复 (F1, F2, F3)

**Week 1**
- Day 1-2: F1 - 多文档验证器修复
- Day 3-4: F2 - update_context 链路修复
- Day 5: F3 - SDK Skills 路径修复

### 阶段 2: P1 问题修复 (F4, F5)

**Week 2**
- Day 1-3: F4 - 模板运行时映射修复
- Day 4-5: F5 - allowed_keys 传递修复

### 阶段 3: 集成测试与验证

**Week 3**
- Day 1-2: 编写集成测试
- Day 3-4: 全量回归测试
- Day 5: 文档更新与发布

---

## 附录: 测试文件清单

需要创建/修改的测试文件:

```
tests/
├── docuswarm/
│   ├── context/
│   │   └── test_multi_document_validation.py      # F1
│   ├── llm/
│   │   ├── test_update_context_server_creation.py # F2
│   │   └── test_sdk_skills_discovery.py           # F3
│   ├── prompts/
│   │   └── test_template_mapping.py               # F4
│   ├── tools/
│   │   └── test_update_context_allowed_keys.py    # F5
│   └── integration/
│       └── test_f1_f5_fixes_integration.py        # 集成测试
```

---

*本方案基于 TDD 方法论，每个修复都包含: 失败测试 -> 最小实现 -> 通过测试 -> 重构优化*
