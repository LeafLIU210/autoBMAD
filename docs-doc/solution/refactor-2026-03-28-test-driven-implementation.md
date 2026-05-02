# DocuSwarm 重构测试驱动实施方案

**日期**: 2026-03-28  
**方案编号**: solution-2026-03-28-tdd  
**关联研究**: `docs/research/refactor-2026-03-28-implementation-requirements.md`  
**方法论**: Test-Driven Development (TDD) - Red/Green/Refactor

---

## 执行摘要

本方案采用测试驱动开发(TDD)方法，为重构研究报告中的5项要求提供可验证的实施路径。每个要求都遵循"测试先行"原则：先编写失败的测试，再实现代码使其通过，最后重构优化。

### TDD 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. Red     │ -> │  2. Green   │ -> │ 3. Refactor │
│  编写失败测试│    │  实现通过测试│    │  优化代码   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 实施矩阵

| 要求 | 测试文件 | 测试类 | 预估测试数 | 实施顺序 |
|------|----------|--------|-----------|----------|
| 1. system_prompt preset/append | test_session_manager_prompts.py | TestSystemPromptStructure | 6 | Phase 2 |
| 2. node.yaml evaluator | test_node_loader_evaluator.py | TestEvaluatorInlineConfig | 5 | Phase 2 |
| 3. SessionManager 主执行链接入 | test_independent_agent_execution.py | TestExecutionChainInjection | 8 | Phase 3 |
| 4. tests/__init__.py 修复 | N/A (语法检查) | N/A | 1 | Phase 1 |
| 5. NodeDeliverableConfig 扩展 | test_node_deliverable_config.py | TestDeliverableExtendedFields | 6 | Phase 1 |

---

## Phase 1: 基础修复测试（无依赖）

### 4. tests/__init__.py 语法错误修复

#### TDD 循环 4.1: 语法检查测试

**测试类型**: 静态语法验证（无需 pytest）

**验证命令**:
```bash
# Red: 当前会失败
python -c "import ast; ast.parse(open('tests/__init__.py').read())"
# SyntaxError: invalid syntax

# Green: 修复后应该成功
python -c "import ast; ast.parse(open('tests/__init__.py').read()); print('OK')"
# OK
```

**测试实现**:
```python
# tests/test_syntax_validation.py
import ast
import pytest
from pathlib import Path

def test_tests_init_syntax():
    """Verify tests/__init__.py has valid Python syntax."""
    init_file = Path(__file__).parent / "__init__.py"
    content = init_file.read_text(encoding="utf-8")
    
    # Should not raise SyntaxError
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"tests/__init__.py has syntax error: {e}")

def test_tests_init_importable():
    """Verify tests package can be imported."""
    import tests
    assert tests is not None
```

**生产代码修复**:
```python
# tests/__init__.py
"""DocuSwarm test suite."""
```

**验收标准**:
- [ ] `python -c "import tests"` 成功
- [ ] `python -m pytest tests/ --collect-only` 能发现测试
- [ ] `pytest tests/test_syntax_validation.py -v` 通过

---

### 5. NodeDeliverableConfig 扩展字段

#### TDD 循环 5.1: 数据类字段存在性测试

**测试文件**: `tests/unit/nodes/test_node_deliverable_config.py`

```python
"""Tests for NodeDeliverableConfig extended fields."""
import pytest
from dataclasses import fields
from autoBMAD.nodes.loader import NodeDeliverableConfig


class TestDeliverableExtendedFields:
    """TDD tests for deliverable config field extensions."""
    
    def test_template_title_field_exists(self):
        """Red: template_title field should exist."""
        field_names = {f.name for f in fields(NodeDeliverableConfig)}
        assert "template_title" in field_names, \
            "NodeDeliverableConfig missing template_title field"
    
    def test_output_filename_field_exists(self):
        """Red: output_filename field should exist."""
        field_names = {f.name for f in fields(NodeDeliverableConfig)}
        assert "output_filename" in field_names, \
            "NodeDeliverableConfig missing output_filename field"
    
    def test_format_hints_field_exists(self):
        """Red: format_hints field should exist."""
        field_names = {f.name for f in fields(NodeDeliverableConfig)}
        assert "format_hints" in field_names, \
            "NodeDeliverableConfig missing format_hints field"
    
    def test_template_title_default_none(self):
        """template_title should default to None."""
        config = NodeDeliverableConfig(type="test")
        assert config.template_title is None
    
    def test_output_filename_default_none(self):
        """output_filename should default to None."""
        config = NodeDeliverableConfig(type="test")
        assert config.output_filename is None
    
    def test_format_hints_default_empty_dict(self):
        """format_hints should default to empty dict."""
        config = NodeDeliverableConfig(type="test")
        assert config.format_hints == {}
```

**生产代码实现**:
```python
# autoBMAD/nodes/loader.py

@dataclass
class NodeDeliverableConfig:
    """Configuration for the node's deliverable."""
    type: str
    format: str = "markdown"
    required_sections: list[str] = field(default_factory=list)
    template_title: str | None = None  # Green: 新增
    output_filename: str | None = None  # Green: 新增  
    format_hints: dict[str, Any] = field(default_factory=dict)  # Green: 新增
```

#### TDD 循环 5.2: NodeLoader 解析测试

```python
# tests/unit/nodes/test_node_loader_parsing.py

class TestNodeLoaderDeliverableParsing:
    """TDD tests for NodeLoader deliverable field parsing."""
    
    @pytest.fixture
    def mock_node_yaml_with_extended_fields(self, tmp_path):
        """Create mock node.yaml with extended deliverable fields."""
        node_dir = tmp_path / "nodes" / "test_node"
        node_dir.mkdir(parents=True)
        
        yaml_content = """
node_id: test_node
name: Test Node
sequence: 1
deliverable_type: test-report
schema_version: "2.0"

task:
  name: test-task
  description: Test task description

deliverable:
  required_sections:
    - section_a
    - section_b
  template_title: "Custom Test Report"
  output_filename: "test-report.md"
  format_hints:
    max_words: 1000
    target_audience: "Developers"
    tone: "technical"

agent:
  type: independent
  model: sonnet
  temperature: 0.7

questions: []
dependencies: []
"""
        (node_dir / "node.yaml").write_text(yaml_content)
        (node_dir / "persona.json").write_text('{"name": "Test"}')
        (node_dir / "evaluator.yaml").write_text('criteria: []')
        
        return node_dir
    
    def test_loader_parses_template_title(self, mock_node_yaml_with_extended_fields, monkeypatch):
        """Red: NodeLoader should parse template_title from node.yaml."""
        from autoBMAD.nodes.loader import NodeLoader
        
        # Mock the base path
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_yaml_with_extended_fields.parent)
        
        config = NodeLoader.load("test_node")
        
        assert config.deliverable.template_title == "Custom Test Report", \
            "NodeLoader should parse template_title from node.yaml"
    
    def test_loader_parses_output_filename(self, mock_node_yaml_with_extended_fields, monkeypatch):
        """Red: NodeLoader should parse output_filename from node.yaml."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_yaml_with_extended_fields.parent)
        
        config = NodeLoader.load("test_node")
        
        assert config.deliverable.output_filename == "test-report.md", \
            "NodeLoader should parse output_filename from node.yaml"
    
    def test_loader_parses_format_hints(self, mock_node_yaml_with_extended_fields, monkeypatch):
        """Red: NodeLoader should parse format_hints from node.yaml."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_yaml_with_extended_fields.parent)
        
        config = NodeLoader.load("test_node")
        
        expected_hints = {
            "max_words": 1000,
            "target_audience": "Developers", 
            "tone": "technical"
        }
        assert config.deliverable.format_hints == expected_hints, \
            "NodeLoader should parse format_hints from node.yaml"
```

**生产代码实现**:
```python
# autoBMAD/nodes/loader.py - _build_node_config 方法

# Build deliverable config
deliverable_data = config["deliverable"]
deliverable_config = NodeDeliverableConfig(
    type=config["deliverable_type"],
    required_sections=deliverable_data.get("required_sections", []),
    template_title=deliverable_data.get("template_title"),  # Green: 新增
    output_filename=deliverable_data.get("output_filename"),  # Green: 新增
    format_hints=deliverable_data.get("format_hints", {}),  # Green: 新增
)
```

#### TDD 循环 5.3: 消费者传递测试

```python
# tests/unit/context/test_deliverable_requirements_passing.py

class TestDeliverableRequirementsPassing:
    """TDD tests for deliverable fields passing through ContextManager."""
    
    def test_context_manager_passes_template_title(self):
        """Red: ContextManager should pass template_title to deliverable_requirements."""
        from autoBMAD.docuswarm.context.isolation import ContextManager
        from autoBMAD.nodes.loader import NodeConfig, NodeDeliverableConfig, NodeTaskConfig
        
        # Mock node config
        mock_config = NodeConfig(
            node_id="test",
            name="Test",
            description="Test",
            sequence=1,
            deliverable_type="test-report",
            task=NodeTaskConfig(name="test-task"),
            deliverable=NodeDeliverableConfig(
                type="test-report",
                template_title="Custom Report Title"
            )
        )
        
        # Verify deliverable_requirements would include template_title
        reqs = {
            "required_sections": mock_config.deliverable.required_sections,
            "template_title": mock_config.deliverable.template_title,
        }
        
        assert reqs["template_title"] == "Custom Report Title"
```

**验收标准**:
- [ ] `pytest tests/unit/nodes/test_node_deliverable_config.py -v` 全部通过
- [ ] `pytest tests/unit/nodes/test_node_loader_parsing.py -v` 全部通过
- [ ] 所有 node.yaml 已更新包含 deliverable 扩展字段

---

## Phase 2: 配置层改造测试

### 2. node.yaml evaluator 内联引用段

#### TDD 循环 2.1: NodeEvaluatorConfig 字段测试

**测试文件**: `tests/unit/nodes/test_node_evaluator_config.py`

```python
"""Tests for NodeEvaluatorConfig extended fields."""
import pytest
from dataclasses import fields
from autoBMAD.nodes.loader import NodeEvaluatorConfig


class TestEvaluatorConfigFields:
    """TDD tests for evaluator config fields."""
    
    def test_model_field_exists(self):
        """Red: model field should exist in NodeEvaluatorConfig."""
        field_names = {f.name for f in fields(NodeEvaluatorConfig)}
        assert "model" in field_names, "NodeEvaluatorConfig missing model field"
    
    def test_criteria_file_field_exists(self):
        """Red: criteria_file field should exist."""
        field_names = {f.name for f in fields(NodeEvaluatorConfig)}
        assert "criteria_file" in field_names, \
            "NodeEvaluatorConfig missing criteria_file field"
    
    def test_model_defaults_to_none(self):
        """model should default to None."""
        config = NodeEvaluatorConfig()
        assert config.model is None
    
    def test_criteria_file_defaults_to_none(self):
        """criteria_file should default to None."""
        config = NodeEvaluatorConfig()
        assert config.criteria_file is None
```

**生产代码**:
```python
# autoBMAD/nodes/loader.py

@dataclass
class NodeEvaluatorConfig:
    """Configuration for the evaluator agent."""
    criteria: list[dict[str, Any]] = field(default_factory=list)
    threshold: dict[str, float] = field(default_factory=dict)
    max_iterations: int = 3
    model: str | None = None  # Green: 新增
    criteria_file: str | None = None  # Green: 新增
```

#### TDD 循环 2.2: NodeLoader evaluator 解析测试

```python
# tests/unit/nodes/test_node_loader_evaluator.py

class TestNodeLoaderEvaluatorParsing:
    """TDD tests for NodeLoader evaluator inline config parsing."""
    
    @pytest.fixture
    def mock_node_with_inline_evaluator(self, tmp_path):
        """Create mock node.yaml with inline evaluator config."""
        node_dir = tmp_path / "nodes" / "test_node"
        node_dir.mkdir(parents=True)
        
        yaml_content = """
node_id: test_node
name: Test Node
sequence: 1
deliverable_type: test-report
schema_version: "2.1"

task:
  name: test-task

deliverable:
  required_sections: []

agent:
  type: independent
  model: sonnet
  temperature: 0.7

evaluator:
  criteria_file: evaluator.yaml
  threshold:
    approval: 0.75
    escalation: 0.55
  max_iterations: 5
  model: haiku

questions: []
dependencies: []
"""
        (node_dir / "node.yaml").write_text(yaml_content)
        (node_dir / "persona.json").write_text('{"name": "Test"}')
        (node_dir / "evaluator.yaml").write_text("""
criteria:
  - name: quality
    weight: 1.0
""")
        
        return node_dir
    
    def test_loader_reads_criteria_file_reference(self, mock_node_with_inline_evaluator, monkeypatch):
        """Red: NodeLoader should read criteria_file from inline config."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_with_inline_evaluator.parent)
        
        config = NodeLoader.load("test_node")
        
        assert config.evaluator.criteria_file == "evaluator.yaml"
    
    def test_loader_reads_inline_threshold(self, mock_node_with_inline_evaluator, monkeypatch):
        """Red: NodeLoader should read threshold from inline config."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_with_inline_evaluator.parent)
        
        config = NodeLoader.load("test_node")
        
        assert config.evaluator.threshold["approval"] == 0.75
        assert config.evaluator.threshold["escalation"] == 0.55
    
    def test_loader_reads_inline_max_iterations(self, mock_node_with_inline_evaluator, monkeypatch):
        """Red: NodeLoader should read max_iterations from inline config."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_with_inline_evaluator.parent)
        
        config = NodeLoader.load("test_node")
        
        assert config.evaluator.max_iterations == 5
    
    def test_loader_reads_inline_model(self, mock_node_with_inline_evaluator, monkeypatch):
        """Red: NodeLoader should read model from inline config."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_with_inline_evaluator.parent)
        
        config = NodeLoader.load("test_node")
        
        assert config.evaluator.model == "haiku"
    
    def test_loader_merges_criteria_from_file(self, mock_node_with_inline_evaluator, monkeypatch):
        """Red: NodeLoader should merge criteria from referenced file."""
        from autoBMAD.nodes.loader import NodeLoader
        
        monkeypatch.setattr(NodeLoader, "_base_path", mock_node_with_inline_evaluator.parent)
        
        config = NodeLoader.load("test_node")
        
        # Should have criteria from evaluator.yaml
        assert len(config.evaluator.criteria) == 1
        assert config.evaluator.criteria[0]["name"] == "quality"
```

**生产代码**:
```python
# autoBMAD/nodes/loader.py - _build_node_config 方法

# 从 node.yaml 读取 evaluator 配置（优先）
evaluator_data = config.get("evaluator", {})

# 如果指定了 criteria_file 或没有 evaluator 段，从文件加载
if evaluator_data.get("criteria_file") or not evaluator_data:
    criteria_file = evaluator_data.get("criteria_file", "evaluator.yaml")
    evaluator_file = node_dir / criteria_file
    if evaluator_file.exists():
        file_evaluator = cls._load_yaml(evaluator_file)
        # 合并配置（node.yaml 优先）
        evaluator_data = {**file_evaluator, **evaluator_data}

# 构建 evaluator config
evaluator_config = NodeEvaluatorConfig(
    criteria=evaluator_data.get("criteria", []),
    threshold=evaluator_data.get("threshold", {"approval": 0.7, "escalation": 0.5}),
    max_iterations=evaluator_data.get("max_iterations", 3),
    model=evaluator_data.get("model"),  # Green: 新增
    criteria_file=evaluator_data.get("criteria_file"),  # Green: 新增
)
```

**验收标准**:
- [ ] 所有5个 node.yaml 已添加 evaluator 段
- [ ] `pytest tests/unit/nodes/test_node_evaluator_config.py -v` 通过
- [ ] `pytest tests/unit/nodes/test_node_loader_evaluator.py -v` 通过

---

### 1. Claude Agent SDK system_prompt preset/append 高级结构

#### TDD 循环 1.1: SessionManager.create_session 签名测试

**测试文件**: `tests/unit/llm/test_session_manager_prompts.py`

```python
"""Tests for SessionManager system_prompt preset/append structure."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path


class TestSystemPromptStructure:
    """TDD tests for system_prompt preset/append structure."""
    
    @pytest.fixture
    def session_manager(self):
        """Create SessionManager instance for testing."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        return SessionManager(work_dir=Path("/tmp"))
    
    def test_create_session_accepts_dict_system_prompt(self, session_manager):
        """Red: create_session should accept dict system_prompt parameter."""
        import inspect
        sig = inspect.signature(session_manager.create_session)
        
        system_prompt_param = sig.parameters.get("system_prompt")
        assert system_prompt_param is not None, \
            "create_session missing system_prompt parameter"
        
        # Check annotation accepts dict
        annotation = system_prompt_param.annotation
        assert "dict" in str(annotation), \
            f"system_prompt parameter should accept dict, got {annotation}"
    
    @pytest.mark.asyncio
    async def test_dict_system_prompt_uses_preset_structure(self, session_manager):
        """Red: Dict system_prompt should be used as-is with preset structure."""
        with patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            mock_client.return_value = mock_instance
            
            dict_prompt = {
                "type": "preset",
                "preset": "claude_code",
                "append": "Custom append content"
            }
            
            await session_manager.create_session(system_prompt=dict_prompt)
            
            # Verify options were created with dict system_prompt
            call_args = mock_client.call_args
            options = call_args.kwargs.get("options") or call_args[1]["options"]
            
            assert isinstance(options.system_prompt, dict), \
                "system_prompt should be dict when dict passed"
            assert options.system_prompt.get("type") == "preset", \
                "system_prompt should have type: preset"
            assert options.system_prompt.get("preset") == "claude_code", \
                "system_prompt should have preset: claude_code"
    
    @pytest.mark.asyncio
    async def test_string_system_prompt_wraps_to_preset(self, session_manager):
        """Red: String system_prompt should wrap to preset/append structure."""
        with patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            mock_client.return_value = mock_instance
            
            string_prompt = "Custom system prompt content"
            
            await session_manager.create_session(system_prompt=string_prompt)
            
            call_args = mock_client.call_args
            options = call_args.kwargs.get("options") or call_args[1]["options"]
            
            assert isinstance(options.system_prompt, dict), \
                "String system_prompt should be wrapped to dict"
            assert options.system_prompt.get("type") == "preset", \
                "Wrapped system_prompt should have type: preset"
            assert options.system_prompt.get("preset") == "claude_code", \
                "Wrapped system_prompt should have preset: claude_code"
            assert options.system_prompt.get("append") == string_prompt, \
                "String content should be in append field"
    
    @pytest.mark.asyncio
    async def test_none_system_prompt_not_set(self, session_manager):
        """Red: None system_prompt should not set options.system_prompt."""
        with patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            mock_client.return_value = mock_instance
            
            await session_manager.create_session(system_prompt=None)
            
            call_args = mock_client.call_args
            options = call_args.kwargs.get("options") or call_args[1]["options"]
            
            # system_prompt should not be set or be None
            assert getattr(options, "system_prompt", None) is None, \
                "None system_prompt should not be set on options"
```

**生产代码**:
```python
# autoBMAD/docuswarm/llm/session_manager.py

async def create_session(
    self,
    mode: str = "agent",
    yolo: bool = True,
    max_steps: int | None = None,
    agent_file: Path | None = None,
    approval_handler_fn: Any | None = None,
    system_prompt: str | dict[str, Any] | None = None,  # Green: 支持 dict
) -> ClaudeSessionWrapper:
    # ...
    
    # Set system_prompt if provided
    if system_prompt is not None:
        if isinstance(system_prompt, dict):
            # 已经是 dict 格式 (preset/append)
            options.system_prompt = system_prompt
        else:
            # 字符串格式 - 包装为 append 结构
            options.system_prompt = {
                "type": "preset",
                "preset": "claude_code",
                "append": system_prompt
            }
```

#### TDD 循环 1.2: 四层架构集成测试

```python
# tests/unit/prompts/test_four_layer_architecture.py

class TestFourLayerArchitecture:
    """TDD tests for Four-Layer prompt architecture integration."""
    
    @pytest.mark.asyncio
    async def test_independent_agent_uses_preset_structure(self):
        """Red: IndependentAgent should use preset/append in _call_llm_with_prompts."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        # This test verifies the integration between IndependentAgent and SessionManager
        # It will fail until both components are properly implemented
        
        with patch.object(SessionManager, "create_session") as mock_create_session:
            mock_session = AsyncMock()
            mock_session.prompt = AsyncMock(return_value=[])
            mock_create_session.return_value = mock_session
            
            # Create agent and call with test input
            agent = IndependentAgent(
                config=MagicMock(),
                session_manager=MagicMock(),
                node_id="analyst"
            )
            
            # The call should use dict format for system_prompt
            await agent._call_llm_with_prompts(
                system_prompt_append="Test persona + task + skills",
                user_prompt="Test user content"
            )
            
            # Verify create_session was called with dict system_prompt
            call_kwargs = mock_create_session.call_args.kwargs
            system_prompt = call_kwargs.get("system_prompt")
            
            assert isinstance(system_prompt, dict), \
                "IndependentAgent should pass dict system_prompt to create_session"
            assert system_prompt.get("type") == "preset", \
                "system_prompt should use preset type"
```

**验收标准**:
- [ ] `pytest tests/unit/llm/test_session_manager_prompts.py -v` 通过
- [ ] `pytest tests/unit/prompts/test_four_layer_architecture.py -v` 通过

---

## Phase 3: 执行层整合测试

### 3. 主执行链 SessionManager 接入 node_id 和 tool_permissions

#### TDD 循环 3.1: SessionManager 初始化参数测试

**测试文件**: `tests/unit/llm/test_session_manager_injection.py`

```python
"""Tests for SessionManager node_id and tool_permissions injection."""
import pytest
from pathlib import Path


class TestSessionManagerInjectionParams:
    """TDD tests for SessionManager injection parameters."""
    
    def test_session_manager_accepts_node_id(self):
        """Red: SessionManager should accept node_id parameter."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            work_dir=Path("/tmp"),
            node_id="analyst"
        )
        
        assert sm.node_id == "analyst"
    
    def test_session_manager_accepts_file_dirs(self):
        """Red: SessionManager should accept file_dirs parameter."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            work_dir=Path("/tmp"),
            file_dirs=["docs/", "docs/research/"]
        )
        
        assert sm.file_dirs == ["docs/", "docs/research/"]
    
    def test_session_manager_accepts_search_dirs(self):
        """Red: SessionManager should accept search_dirs parameter."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            work_dir=Path("/tmp"),
            search_dirs=["docs/"]
        )
        
        assert sm.search_dirs == ["docs/"]
    
    def test_file_dirs_defaults_to_empty_list(self):
        """file_dirs should default to empty list."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(work_dir=Path("/tmp"))
        
        assert sm.file_dirs == []
    
    def test_search_dirs_defaults_to_empty_list(self):
        """search_dirs should default to empty list."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(work_dir=Path("/tmp"))
        
        assert sm.search_dirs == []
```

**生产代码**:
```python
# autoBMAD/docuswarm/llm/session_manager.py

class SessionManager:
    def __init__(
        self,
        work_dir: Path,
        agent_file: Path | None = None,
        config: Any | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        node_id: str | None = None,
        file_dirs: list[str] | None = None,  # Green: 新增
        search_dirs: list[str] | None = None,  # Green: 新增
    ) -> None:
        # ...
        self._node_id = node_id
        self._file_dirs = file_dirs or []  # Green: 新增
        self._search_dirs = search_dirs or []  # Green: 新增
    
    @property
    def file_dirs(self) -> list[str]:  # Green: 新增
        return self._file_dirs
    
    @property
    def search_dirs(self) -> list[str]:  # Green: 新增
        return self._search_dirs
```

#### TDD 循环 3.2: _create_options MCP 配置测试

```python
# tests/unit/llm/test_session_manager_mcp_config.py

class TestSessionManagerMCPConfig:
    """TDD tests for SessionManager MCP configuration with separated permissions."""
    
    def test_create_options_with_node_id_and_file_dirs(self):
        """Red: _create_options should configure MCP with file_dirs."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            work_dir=Path("/tmp"),
            node_id="analyst",
            file_dirs=["docs/", "docs/research/"]
        )
        
        options = sm._create_options()
        
        # Should have MCP servers configured
        assert hasattr(options, "mcp_servers"), \
            "options should have mcp_servers"
        assert options.mcp_servers, \
            "mcp_servers should not be empty when node_id and file_dirs provided"
    
    def test_create_options_with_search_dirs(self):
        """Red: _create_options should configure search tools with search_dirs."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            work_dir=Path("/tmp"),
            node_id="analyst",
            file_dirs=["docs/"],
            search_dirs=["docs/research/"]  # Different from file_dirs
        )
        
        options = sm._create_options()
        
        # Should have both file and search MCP servers
        assert options.mcp_servers, "mcp_servers should be configured"
        # The servers should reflect the different permissions
        server_names = list(options.mcp_servers.keys())
        assert any("files" in name for name in server_names), \
            "Should have file server"
        assert any("search" in name for name in server_names), \
            "Should have search server"
    
    def test_create_options_without_node_id_skips_mcp(self):
        """Red: _create_options should skip MCP config without node_id."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            work_dir=Path("/tmp"),
            file_dirs=["docs/"]
        )
        
        options = sm._create_options()
        
        # Should not have MCP servers without node_id
        assert not options.mcp_servers, \
            "mcp_servers should be empty without node_id"
```

**生产代码**:
```python
# autoBMAD/docuswarm/llm/session_manager.py - _create_options

# Configure MCP servers and allowed tools if node_id provided
if self._node_id:
    from autoBMAD.nodes.loader import (
        NodeFilePermissions,
        NodeSearchPermissions,
        NodeToolPermissions,
    )
    
    # Create tool permissions with separated file/search dirs
    tool_permissions = NodeToolPermissions(
        file_permissions=NodeFilePermissions(allowed_read_dirs=self._file_dirs),
        search_permissions=NodeSearchPermissions(search_dirs=self._search_dirs),
    )
    
    # Create NodeToolFilter for this node
    node_filter = NodeToolFilter(
        node_id=self._node_id,
        tool_permissions=tool_permissions,
    )
    
    # Create MCP servers
    mcp_servers = node_filter.create_mcp_servers()
    if mcp_servers:
        # Convert list to dict for ClaudeAgentOptions
        options_dict["mcp_servers"] = {
            f"docuswarm-{server.__class__.__name__.lower()}-{self._node_id}": server
            for server in mcp_servers
        }
    
    # Generate allowed tools
    allowed_tools = node_filter.get_allowed_tools()
    if allowed_tools:
        options_dict["allowed_tools"] = allowed_tools
```

#### TDD 循环 3.3: IndependentAgent.execute_with_input 集成测试

**测试文件**: `tests/unit/agents/test_independent_agent_execution.py`

```python
"""Tests for IndependentAgent execution chain with full configuration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path


class TestExecutionChainInjection:
    """TDD tests for execute_with_input configuration injection."""
    
    @pytest.fixture
    def mock_node_config(self):
        """Create mock node config with tool permissions."""
        from autoBMAD.nodes.loader import (
            NodeConfig, NodeToolPermissions, NodeFilePermissions,
            NodeSearchPermissions, NodeTaskConfig, NodeDeliverableConfig
        )
        
        return NodeConfig(
            node_id="analyst",
            name="Analyst",
            description="Test analyst",
            sequence=1,
            deliverable_type="analyst-report",
            task=NodeTaskConfig(name="test-task"),
            deliverable=NodeDeliverableConfig(type="analyst-report"),
            tool_permissions=NodeToolPermissions(
                file_permissions=NodeFilePermissions(
                    allowed_read_dirs=["docs/", "docs/research/"]
                ),
                search_permissions=NodeSearchPermissions(
                    search_dirs=["docs/"]
                )
            )
        )
    
    @pytest.mark.asyncio
    async def test_execute_with_input_creates_session_manager_with_node_id(
        self, mock_node_config
    ):
        """Red: execute_with_input should create SessionManager with node_id."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        with patch("autoBMAD.docuswarm.agents.independent.NodeLoader.load") as mock_load:
            mock_load.return_value = mock_node_config
            
            with patch.object(SessionManager, "create_session") as mock_create:
                mock_session = AsyncMock()
                mock_session.prompt = AsyncMock(return_value=[])
                mock_create.return_value = mock_session
                
                agent = IndependentAgent(
                    config=MagicMock(),
                    session_manager=MagicMock(),
                    node_id="analyst",
                    project_root=Path("/project")
                )
                
                await agent.execute_with_input(
                    agent_input={
                        "task_name": "test",
                        "original_context_summary": "",
                        "chained_deliverables_summary": [],
                    },
                    pipeline_id="test-pipeline"
                )
                
                # Verify SessionManager was created with node_id
                # Note: This requires refactoring execute_with_input to inject SessionManager
                # or capturing the constructor call
```

由于 `execute_with_input` 内部创建 `SessionManager` 实例，我们需要重构以支持测试：

**重构方案**:
```python
# autoBMAD/docuswarm/agents/independent.py

async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
) -> IndependentOutput:
    # ... 提取 agent_input 字段 ...
    
    # 加载节点配置
    from autoBMAD.nodes.loader import NodeLoader
    node_config = NodeLoader.load(self.node_id)
    
    # 计算输出目录
    output_dir = self.project_root / "output" / pipeline_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 准备权限目录（绝对路径）
    file_dirs = [
        str(self.project_root / d)
        for d in node_config.tool_permissions.file_permissions.allowed_read_dirs
    ]
    search_dirs = [
        str(self.project_root / d)
        for d in node_config.tool_permissions.search_permissions.search_dirs
    ]
    
    # 创建带完整配置的 SessionManager
    pipeline_session_manager = self._create_pipeline_session_manager(
        work_dir=output_dir,
        node_id=self.node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
    )
    
    # ... 执行流程 ...

def _create_pipeline_session_manager(
    self,
    work_dir: Path,
    node_id: str,
    file_dirs: list[str],
    search_dirs: list[str],
) -> SessionManager:
    """Factory method for creating pipeline SessionManager - allows testing."""
    return SessionManager(
        work_dir=work_dir,
        agent_file=self._agent_file,
        config=self.session_manager.config if self.session_manager else None,
        node_id=node_id,
        file_dirs=file_dirs,
        search_dirs=search_dirs,
    )
```

**更新后的测试**:
```python
    @pytest.mark.asyncio
    async def test_execute_with_input_creates_session_manager_with_node_id(
        self, mock_node_config
    ):
        """Green: execute_with_input should create SessionManager with node_id."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        with patch("autoBMAD.docuswarm.agents.independent.NodeLoader.load") as mock_load:
            mock_load.return_value = mock_node_config
            
            agent = IndependentAgent(
                config=MagicMock(),
                session_manager=MagicMock(),
                node_id="analyst",
                project_root=Path("/project")
            )
            
            # Mock the factory method to capture arguments
            with patch.object(
                agent, 
                "_create_pipeline_session_manager"
            ) as mock_factory:
                mock_sm = MagicMock()
                mock_sm.create_session = AsyncMock()
                mock_sm.create_session.return_value.prompt = AsyncMock(return_value=[])
                mock_factory.return_value = mock_sm
                
                await agent.execute_with_input(
                    agent_input={
                        "task_name": "test",
                        "original_context_summary": "",
                        "chained_deliverables_summary": [],
                    },
                    pipeline_id="test-pipeline"
                )
                
                # Verify factory was called with node_id
                mock_factory.assert_called_once()
                call_kwargs = mock_factory.call_args.kwargs
                
                assert call_kwargs.get("node_id") == "analyst", \
                    "SessionManager should be created with node_id"
                assert "file_dirs" in call_kwargs, \
                    "SessionManager should be created with file_dirs"
                assert "search_dirs" in call_kwargs, \
                    "SessionManager should be created with search_dirs"
```

#### TDD 循环 3.4: 端到端集成测试

```python
# tests/integration/test_execution_chain_e2e.py

class TestExecutionChainE2E:
    """End-to-end tests for execution chain with all configurations."""
    
    @pytest.mark.asyncio
    async def test_full_execution_chain_with_tools(self, tmp_path):
        """Red: Full execution should configure and use MCP tools."""
        # This is a comprehensive integration test
        # Setup: Create minimal node config, mock LLM responses
        # Execute: Run execute_with_input
        # Verify: Check that MCP tools are properly configured
        pass
```

**验收标准**:
- [ ] `pytest tests/unit/llm/test_session_manager_injection.py -v` 通过
- [ ] `pytest tests/unit/llm/test_session_manager_mcp_config.py -v` 通过
- [ ] `pytest tests/unit/agents/test_independent_agent_execution.py -v` 通过
- [ ] `pytest tests/integration/test_execution_chain_e2e.py -v` 通过

---

## Phase 4: 验证与回归测试

### 审计工具集成测试

```python
# tests/test_refactor_audit_integration.py

class TestRefactorAuditIntegration:
    """Integration test using the audit tool."""
    
    def test_audit_tool_reports_all_pass(self):
        """Verify all refactor requirements are implemented."""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "tools/refactor_implementation_auditor.py"],
            capture_output=True,
            text=True
        )
        
        # Check output for success indicators
        assert "[FAIL]" not in result.stdout, \
            f"Audit tool reported failures:\n{result.stdout}"
        assert "[OK] 所有关键检查通过！" in result.stdout or \
               "[OK]" in result.stdout, \
            f"Audit tool did not report success:\n{result.stdout}"
```

---

## 测试执行顺序

```bash
#!/bin/bash
# run_tdd_tests.sh - TDD 测试执行脚本

echo "=== Phase 1: 基础修复测试 ==="
pytest tests/test_syntax_validation.py -v || exit 1
pytest tests/unit/nodes/test_node_deliverable_config.py -v || exit 1
pytest tests/unit/nodes/test_node_loader_parsing.py -v || exit 1

echo "=== Phase 2: 配置层改造测试 ==="
pytest tests/unit/nodes/test_node_evaluator_config.py -v || exit 1
pytest tests/unit/nodes/test_node_loader_evaluator.py -v || exit 1
pytest tests/unit/llm/test_session_manager_prompts.py -v || exit 1
pytest tests/unit/prompts/test_four_layer_architecture.py -v || exit 1

echo "=== Phase 3: 执行层整合测试 ==="
pytest tests/unit/llm/test_session_manager_injection.py -v || exit 1
pytest tests/unit/llm/test_session_manager_mcp_config.py -v || exit 1
pytest tests/unit/agents/test_independent_agent_execution.py -v || exit 1

echo "=== Phase 4: 集成与回归测试 ==="
pytest tests/integration/test_execution_chain_e2e.py -v || exit 1
pytest tests/test_refactor_audit_integration.py -v || exit 1

echo "=== 所有测试通过！==="
```

---

## 测试覆盖率目标

| 模块 | 目标覆盖率 | 关键测试点 |
|------|-----------|-----------|
| `session_manager.py` | 90%+ | preset/append 结构、MCP 配置、参数传递 |
| `loader.py` | 85%+ | evaluator 解析、deliverable 字段扩展 |
| `independent.py` | 85%+ | execute_with_input、SessionManager 创建 |
| `__init__.py` | N/A | 语法验证 |

---

## 附录: 测试辅助工具

### Mock 数据生成器

```python
# tests/fixtures/node_configs.py

"""Test fixtures for node configurations."""
import pytest
from autoBMAD.nodes.loader import (
    NodeConfig, NodeDeliverableConfig, NodeEvaluatorConfig,
    NodeTaskConfig, NodeToolPermissions, NodeFilePermissions,
    NodeSearchPermissions
)


@pytest.fixture
def minimal_node_config():
    """Minimal valid node config."""
    return NodeConfig(
        node_id="test",
        name="Test Node",
        description="Test",
        sequence=1,
        deliverable_type="test-report",
        task=NodeTaskConfig(name="test-task"),
        deliverable=NodeDeliverableConfig(type="test-report")
    )


@pytest.fixture
def full_node_config():
    """Node config with all extended fields."""
    return NodeConfig(
        node_id="test",
        name="Test Node",
        description="Test",
        sequence=1,
        deliverable_type="test-report",
        task=NodeTaskConfig(name="test-task"),
        deliverable=NodeDeliverableConfig(
            type="test-report",
            template_title="Test Report",
            output_filename="test.md",
            format_hints={"max_words": 1000}
        ),
        evaluator=NodeEvaluatorConfig(
            criteria=[{"name": "quality", "weight": 1.0}],
            threshold={"approval": 0.7, "escalation": 0.5},
            max_iterations=3,
            model="sonnet",
            criteria_file="evaluator.yaml"
        ),
        tool_permissions=NodeToolPermissions(
            file_permissions=NodeFilePermissions(
                allowed_read_dirs=["docs/"]
            ),
            search_permissions=NodeSearchPermissions(
                search_dirs=["docs/"]
            )
        )
    )
```

---

*方案完成*
