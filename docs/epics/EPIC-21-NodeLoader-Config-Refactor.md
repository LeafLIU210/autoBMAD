# Epic 21: NodeLoader 配置加载系统重构

**Epic ID**: EPIC-21  
**Version**: 1.0  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days

---

## 1. Epic Overview

### 1.1 Summary

重构 NodeLoader 以支持新的 BMM 对齐配置格式，实现配置加载系统的现代化升级。

### 1.2 Business Value

- **配置现代化**: 支持新的 task 配置块，移除废弃字段
- **向后兼容**: 确保旧配置格式仍可正常加载
- **BMM 对齐**: 配置结构与 BMM 方法论保持一致

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| NodeTaskConfig 实现 | 数据类可正常创建和序列化 |
| NodeDeliverableConfig 扩展 | 支持 template_title 和 output_filename |
| NodeConfig 重构 | 不再包含废弃字段 |
| 配置加载 | 新格式和旧格式都能正常加载 |
| 测试覆盖率 | 新增代码 >90% |

### 1.4 Dependencies

- **Prerequisites**: TDD-BMM-01 方案已批准
- **Blocks**: EPIC-22 (Persona 重构), EPIC-23 (废弃代码移除)

---

## 2. Stories

### Story 21.1: 添加 NodeTaskConfig 数据类

As a developer,  
I want to add the NodeTaskConfig dataclass,  
So that we can store task-specific configuration for each node.

**Acceptance Criteria:**

**Given** the loader.py file exists  
**When** I add the NodeTaskConfig dataclass with name, description, and role_supplement fields  
**Then** the class can be instantiated with minimal fields (name, description)  
**And** the role_supplement field defaults to empty string

**Given** a NodeTaskConfig instance  
**When** I serialize it to dict  
**Then** all fields are properly exported

**Implementation Details:**
```python
@dataclass
class NodeTaskConfig:
    """BMM task configuration for a node.
    
    Contains task-specific instructions extracted from BMM workflows.
    All content is pre-processed from _bmad/bmm/ and embedded here.
    
    Attributes:
        name: Task identifier (e.g., "create-product-brief")
        description: Task description from BMM workflow
        role_supplement: Additional role context for this specific task
    """
    name: str
    description: str
    role_supplement: str = ""
```

---

### Story 21.2: 扩展 NodeDeliverableConfig

As a developer,  
I want to extend NodeDeliverableConfig with new fields,  
So that we can support template titles and output filenames.

**Acceptance Criteria:**

**Given** the NodeDeliverableConfig dataclass  
**When** I add template_title and output_filename fields with empty string defaults  
**Then** existing code continues to work (backward compatible)  
**And** new fields can be populated from YAML config

**Given** a deliverable config with template_title "Product Brief: {project_name}"  
**When** I access the template_title property  
**Then** the placeholder is preserved for later formatting

**Implementation Details:**
```python
@dataclass
class NodeDeliverableConfig:
    """Deliverable configuration with BMM template alignment.
    
    Attributes:
        type: Deliverable type (e.g., "product-brief", "prd")
        required_sections: List of required section IDs
        template_title: Template title with placeholders (e.g., "Product Brief: {project_name}")
        output_filename: Output filename pattern (e.g., "product-brief-{project_name}.md")
    """
    type: str
    required_sections: list[str]
    template_title: str = ""           # 新增
    output_filename: str = ""          # 新增
```

---

### Story 21.3: 重构 NodeConfig 结构

As a developer,  
I want to refactor NodeConfig to remove deprecated fields and add new ones,  
So that the configuration aligns with BMM requirements.

**Acceptance Criteria:**

**Given** the current NodeConfig dataclass  
**When** I remove description, questions, and dependencies fields  
**And** add task (NodeTaskConfig | None) and persona (dict | None) fields  
**Then** the dataclass can be instantiated with the new structure  
**And** existing tests that don't use deprecated fields still pass

**Given** a NodeConfig instance without task  
**When** I access the task property  
**Then** it returns None without error

**Implementation Details:**

**现有 NodeConfig 结构:**
```python
@dataclass
class NodeConfig:
    node_id: str
    name: str
    description: str          # 将被移除
    sequence: int
    deliverable: NodeDeliverableConfig
    agent: NodeAgentConfig
    questions: NodeQuestionsConfig      # 将被移除
    dependencies: NodeDependenciesConfig # 将被移除
    evaluator: NodeEvaluatorConfig | None = None
```

**目标 NodeConfig 结构:**
```python
@dataclass
class NodeConfig:
    """Complete node configuration (BMM-aligned).
    
    Refactored to remove deprecated fields (description, questions, dependencies)
    and add BMM task configuration.
    
    Attributes:
        node_id: Unique node identifier
        name: Display name
        sequence: Execution sequence number
        deliverable: Deliverable configuration
        agent: Agent configuration
        task: Optional BMM task configuration
        evaluator: Optional evaluator configuration
        persona: Optional inline persona data
    """
    node_id: str
    name: str
    sequence: int
    deliverable: NodeDeliverableConfig
    agent: NodeAgentConfig
    task: NodeTaskConfig | None = None       # 新增
    evaluator: NodeEvaluatorConfig | None = None
    persona: dict[str, Any] | None = None    # 新增，内联persona
```

---

### Story 21.4: 更新 NodeLoader 加载逻辑

As a developer,  
I want to update NodeLoader to handle the new config format,  
So that it can load both old and new YAML configurations.

**Acceptance Criteria:**

**Given** a node.yaml file with the new task block  
**When** NodeLoader.load() is called  
**Then** it correctly parses the task configuration  
**And** creates a NodeTaskConfig instance

**Given** a node.yaml file without the task block (legacy format)  
**When** NodeLoader.load() is called  
**Then** it sets task to None  
**And** does not raise an error

**Given** a node.yaml file with the new deliverable fields  
**When** NodeLoader.load() is called  
**Then** it correctly parses template_title and output_filename

**Implementation Details:**
```python
class NodeLoader:
    """Loads node configuration from YAML/JSON files."""

    @classmethod
    def load(cls, node_id: str) -> NodeConfig:
        """Load node configuration.
        
        Supports both new format (with task block) and legacy format
        for backward compatibility.
        """
        node_path = NODES_DIR / node_id
        if not node_path.exists():
            raise NodeLoadError(f"Node directory not found: {node_id}")

        # Load node.yaml
        node_yaml_path = node_path / "node.yaml"
        if not node_yaml_path.exists():
            raise NodeLoadError(f"node.yaml not found for node: {node_id}")

        with open(node_yaml_path, encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        # Build configuration
        return cls._build_node_config(node_id, yaml_data, node_path)

    @classmethod
    def _build_node_config(
        cls, node_id: str, yaml_data: dict, node_path: Path
    ) -> NodeConfig:
        """Build NodeConfig from YAML data."""
        
        # Build deliverable config (支持新字段)
        deliverable_data = yaml_data.get("deliverable", {})
        deliverable = NodeDeliverableConfig(
            type=deliverable_data.get("type", "document"),
            required_sections=deliverable_data.get("required_sections", []),
            template_title=deliverable_data.get("template_title", ""),
            output_filename=deliverable_data.get("output_filename", ""),
        )

        # Build task config (新增)
        task_data = yaml_data.get("task")
        task = None
        if task_data:
            task = NodeTaskConfig(
                name=task_data.get("name", ""),
                description=task_data.get("description", ""),
                role_supplement=task_data.get("role_supplement", ""),
            )

        # Build agent config
        agent_data = yaml_data.get("agent", {})
        agent = NodeAgentConfig(
            type=agent_data.get("type", "independent"),
            model=agent_data.get("model", "sonnet"),
            temperature=agent_data.get("temperature", 0.7),
        )

        # Load optional evaluator config
        evaluator_path = node_path / "evaluator.yaml"
        evaluator = None
        if evaluator_path.exists():
            evaluator = cls._load_evaluator(evaluator_path)

        # Load optional inline persona
        persona_path = node_path / "persona.json"
        persona = None
        if persona_path.exists():
            with open(persona_path, encoding="utf-8") as f:
                persona = json.load(f)

        return NodeConfig(
            node_id=node_id,
            name=yaml_data.get("name", node_id),
            sequence=yaml_data.get("sequence", 0),
            deliverable=deliverable,
            agent=agent,
            task=task,
            evaluator=evaluator,
            persona=persona,
        )
```

---

### Story 21.5: 重写五个节点的 node.yaml 配置

As a developer,  
I want to rewrite the node.yaml files for all five nodes,  
So that they use the new BMM-aligned configuration format.

**Acceptance Criteria:**

**Given** the analyst node configuration  
**When** I rewrite node.yaml with task block and updated deliverable  
**Then** it includes task.name, task.description, task.role_supplement  
**And** it includes deliverable.template_title and deliverable.output_filename  
**And** it no longer contains description, questions, or dependencies

**Given** the pm, ux, architect, and po node configurations  
**When** I apply the same format changes  
**Then** all five nodes have consistent configuration structure  
**And** each node's task reflects its specific BMM role

**New node.yaml 格式模板:**
```yaml
node_id: analyst
name: Analyst
sequence: 1

agent:
  type: independent
  model: sonnet
  temperature: 0.7

task:
  name: create-product-brief
  description: >
    Create comprehensive product briefs through collaborative
    step-by-step discovery.
  role_supplement: >
    You are a product-focused Business Analyst collaborating
    with an expert peer.

deliverable:
  type: product-brief
  template_title: "Product Brief: {project_name}"
  required_sections:
    - executive_summary
    - core_vision
    - problem_statement
  output_filename: "product-brief-{project_name}.md"
```

**需要更新的节点:**
- `nodes/analyst/node.yaml`
- `nodes/pm/node.yaml`
- `nodes/ux/node.yaml`
- `nodes/architect/node.yaml`
- `nodes/po/node.yaml`

---

### Story 21.6: 编写验证测试

As a developer,  
I want to write comprehensive tests for the config refactoring,  
So that we can ensure correctness and backward compatibility.

**Acceptance Criteria:**

**Given** the new config structure  
**When** I run pytest on tests/nodes/test_node_task_config.py  
**Then** all tests pass with >90% coverage

**Given** the backward compatibility requirement  
**When** I run tests on legacy format configs  
**Then** they load without errors  
**And** deprecated fields are gracefully ignored

**Given** the type safety requirement  
**When** I run basedpyright on loader.py  
**Then** no type errors are reported

**Test Files to Create:**

1. **tests/nodes/test_node_task_config.py** - NodeTaskConfig 数据类测试
```python
class TestNodeTaskConfig:
    def test_minimal_task_config(self):
        config = NodeTaskConfig(
            name="create-product-brief",
            description="Create comprehensive product briefs"
        )
        assert config.name == "create-product-brief"
        assert config.role_supplement == ""  # 默认值

    def test_full_task_config(self):
        config = NodeTaskConfig(
            name="create-prd",
            description="Create PRD through structured workflow",
            role_supplement="You are a PM facilitator collaborating with a peer"
        )
        assert config.role_supplement == "You are a PM facilitator collaborating with a peer"
```

2. **tests/nodes/test_deliverable_config.py** - 扩展的 NodeDeliverableConfig 测试
```python
class TestNodeDeliverableConfig:
    def test_deliverable_with_template_title(self):
        config = NodeDeliverableConfig(
            type="product-brief",
            required_sections=["executive_summary", "core_vision"],
            template_title="Product Brief: {project_name}",
            output_filename="product-brief-{project_name}.md"
        )
        assert config.template_title == "Product Brief: {project_name}"

    def test_deliverable_backward_compatibility(self):
        config = NodeDeliverableConfig(
            type="analyst-report",
            required_sections=["summary", "findings"]
        )
        assert config.template_title == ""  # 默认值
```

3. **tests/nodes/test_node_config_structure.py** - 新 NodeConfig 结构测试
```python
class TestNodeConfigStructure:
    def test_node_config_without_deprecated_fields(self):
        config = NodeConfig(
            node_id="analyst",
            name="Analyst",
            sequence=1,
            deliverable=NodeDeliverableConfig(...),
            agent=NodeAgentConfig(...),
            task=NodeTaskConfig(...)
        )
        assert config.task is not None

    def test_node_config_optional_task(self):
        config = NodeConfig(
            node_id="pm",
            name="PM",
            sequence=2,
            deliverable=NodeDeliverableConfig(...),
            agent=NodeAgentConfig(...),
            task=None  # Optional
        )
        assert config.task is None
```

4. **tests/nodes/test_yaml_loading.py** - YAML 配置加载测试
```python
class TestNewYamlFormatLoading:
    def test_load_new_yaml_format(self, temp_node_dir, monkeypatch):
        config = NodeLoader.load("analyst")
        assert config.node_id == "analyst"
        assert config.task is not None
        assert config.task.name == "create-product-brief"
        assert config.deliverable.template_title == "Product Brief: {project_name}"
```

5. **tests/nodes/test_backward_compatibility.py** - 向后兼容性测试
```python
class TestBackwardCompatibility:
    def test_load_legacy_format(self, legacy_node_dir, monkeypatch):
        config = NodeLoader.load("legacy_node")
        assert config.node_id == "legacy_node"
        assert config.task is None  # 应该为None而不是报错
        assert config.deliverable.template_title == ""  # 默认值
```

---

## 3. 实施清单

| Story | 任务 | 测试文件 | 实现文件 | 状态 |
|-------|------|----------|----------|------|
| 21.1 | 创建 NodeTaskConfig 数据类 | `test_node_task_config.py` | `loader.py` | ⬜ |
| 21.2 | 扩展 NodeDeliverableConfig 字段 | `test_deliverable_config.py` | `loader.py` | ⬜ |
| 21.3 | 重构 NodeConfig 结构 | `test_node_config_structure.py` | `loader.py` | ⬜ |
| 21.4 | 更新 NodeLoader 加载逻辑 | `test_yaml_loading.py` | `loader.py` | ⬜ |
| 21.4 | 向后兼容测试 | `test_backward_compatibility.py` | `loader.py` | ⬜ |
| 21.5 | 重写 analyst/node.yaml | - | `nodes/analyst/node.yaml` | ⬜ |
| 21.5 | 重写 pm/node.yaml | - | `nodes/pm/node.yaml` | ⬜ |
| 21.5 | 重写 ux/node.yaml | - | `nodes/ux/node.yaml` | ⬜ |
| 21.5 | 重写 architect/node.yaml | - | `nodes/architect/node.yaml` | ⬜ |
| 21.5 | 重写 po/node.yaml | - | `nodes/po/node.yaml` | ⬜ |

---

## 4. 验证命令

```bash
# 运行 NodeLoader 相关测试
pytest tests/nodes/test_node_task_config.py -v
pytest tests/nodes/test_deliverable_config.py -v
pytest tests/nodes/test_node_config_structure.py -v
pytest tests/nodes/test_yaml_loading.py -v
pytest tests/nodes/test_backward_compatibility.py -v

# 类型检查
basedpyright autoBMAD/docuswarm/nodes/loader.py

# 代码风格检查
ruff check autoBMAD/docuswarm/nodes/loader.py
```

---

## 5. 风险评估

| 风险 | 严重度 | 缓解策略 |
|------|--------|----------|
| 旧配置无法加载 | 高 | 保持向后兼容，task字段可选 |
| 测试覆盖不足 | 中 | 每个新功能必须有测试 |
| 类型检查失败 | 低 | 使用 basedpyright 严格模式 |

---

## 6. 相关文档

- [TDD-BMM-01: NodeLoader 配置加载系统重构](../solution/TDD-BMM-01-NodeLoader-Config-Refactor.md)
- [EPIC-22: Persona 角色上下文与 System Prompt 重构](./EPIC-22-Persona-SystemPrompt-Refactor.md)
- [EPIC-23: 废弃代码移除](./EPIC-23-Deprecated-Code-Removal.md)

---

**文档结束**
