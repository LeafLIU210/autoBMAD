# TDD-BMM-01: NodeLoader 配置加载系统重构

## 文档信息

| 属性 | 值 |
|------|-----|
| **方案编号** | TDD-BMM-01 |
| **关联研究** | Part 1 (配置加载), Part 2 (节点角色), Part 4 (功能精简) |
| **优先级** | P0 - Critical |
| **状态** | 待实施 |

---

## 1. 目标

重构 `NodeLoader` 以支持新的 BMM 对齐配置格式：
1. 移除废弃字段 (`questions`, `dependencies`)
2. 新增 `NodeTaskConfig` 数据类
3. 扩展 `NodeDeliverableConfig` 支持模板标题和输出文件名
4. 保持向后兼容性

---

## 2. 当前状态分析

### 2.1 现有 NodeConfig 结构

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

### 2.2 目标 NodeConfig 结构

```python
@dataclass
class NodeConfig:
    node_id: str
    name: str
    sequence: int
    deliverable: NodeDeliverableConfig  # 扩展字段
    agent: NodeAgentConfig
    task: NodeTaskConfig | None = None       # 新增
    evaluator: NodeEvaluatorConfig | None = None
    persona: dict[str, Any] | None = None    # 内联persona
    # 移除: description, questions, dependencies
```

---

## 3. 测试先行的重构计划

### Phase 1: 编写新配置格式的测试 (Red)

#### Test 1.1: NodeTaskConfig 数据类测试

```python
# tests/nodes/test_node_task_config.py
"""Tests for NodeTaskConfig dataclass."""

import pytest
from autoBMAD.docuswarm.nodes.loader import NodeTaskConfig


class TestNodeTaskConfig:
    """Test NodeTaskConfig creation and validation."""

    def test_minimal_task_config(self):
        """Test creating task config with minimal fields."""
        config = NodeTaskConfig(
            name="create-product-brief",
            description="Create comprehensive product briefs"
        )
        assert config.name == "create-product-brief"
        assert config.description == "Create comprehensive product briefs"
        assert config.role_supplement == ""  # 默认值

    def test_full_task_config(self):
        """Test creating task config with all fields."""
        config = NodeTaskConfig(
            name="create-prd",
            description="Create PRD through structured workflow",
            role_supplement="You are a PM facilitator collaborating with a peer"
        )
        assert config.role_supplement == "You are a PM facilitator collaborating with a peer"

    def test_task_config_from_dict(self):
        """Test creating task config from dictionary."""
        data = {
            "name": "create-ux-design",
            "description": "Create UX design specifications",
            "role_supplement": "UX design facilitator role"
        }
        config = NodeTaskConfig(**data)
        assert config.name == "create-ux-design"
```

#### Test 1.2: 扩展的 NodeDeliverableConfig 测试

```python
# tests/nodes/test_deliverable_config.py
"""Tests for extended NodeDeliverableConfig."""

import pytest
from autoBMAD.docuswarm.nodes.loader import NodeDeliverableConfig


class TestNodeDeliverableConfig:
    """Test extended deliverable configuration."""

    def test_deliverable_with_template_title(self):
        """Test deliverable config with template title."""
        config = NodeDeliverableConfig(
            type="product-brief",
            required_sections=["executive_summary", "core_vision"],
            template_title="Product Brief: {project_name}",
            output_filename="product-brief-{project_name}.md"
        )
        assert config.template_title == "Product Brief: {project_name}"
        assert config.output_filename == "product-brief-{project_name}.md"

    def test_deliverable_backward_compatibility(self):
        """Test old format still works (backward compatibility)."""
        config = NodeDeliverableConfig(
            type="analyst-report",
            required_sections=["summary", "findings"]
        )
        assert config.template_title == ""
        assert config.output_filename == ""
```

#### Test 1.3: 新 NodeConfig 结构测试

```python
# tests/nodes/test_node_config_structure.py
"""Tests for refactored NodeConfig structure."""

import pytest
from autoBMAD.docuswarm.nodes.loader import (
    NodeConfig, NodeTaskConfig, NodeDeliverableConfig, NodeAgentConfig
)


class TestNodeConfigStructure:
    """Test refactored NodeConfig without deprecated fields."""

    def test_node_config_without_deprecated_fields(self):
        """Test NodeConfig can be created without questions/dependencies."""
        config = NodeConfig(
            node_id="analyst",
            name="Analyst",
            sequence=1,
            deliverable=NodeDeliverableConfig(
                type="product-brief",
                required_sections=["executive_summary"]
            ),
            agent=NodeAgentConfig(type="independent", model="sonnet"),
            task=NodeTaskConfig(
                name="create-product-brief",
                description="Create product briefs"
            )
        )
        assert config.node_id == "analyst"
        assert config.task is not None
        assert config.task.name == "create-product-brief"

    def test_node_config_optional_task(self):
        """Test NodeConfig works without task (backward compatibility)."""
        config = NodeConfig(
            node_id="pm",
            name="PM",
            sequence=2,
            deliverable=NodeDeliverableConfig(type="prd", required_sections=[]),
            agent=NodeAgentConfig(type="independent", model="sonnet"),
            task=None  # Optional
        )
        assert config.task is None
```

#### Test 1.4: YAML 配置加载测试

```python
# tests/nodes/test_yaml_loading.py
"""Tests for loading new YAML format."""

import pytest
from pathlib import Path
from autoBMAD.docuswarm.nodes.loader import NodeLoader


class TestNewYamlFormatLoading:
    """Test loading new node.yaml format with task block."""

    @pytest.fixture
    def temp_node_dir(self, tmp_path):
        """Create temporary node directory with new format YAML."""
        node_dir = tmp_path / "analyst"
        node_dir.mkdir()
        
        # New format node.yaml
        yaml_content = """
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
"""
        (node_dir / "node.yaml").write_text(yaml_content)
        
        # Minimal persona.json
        persona_content = '{"name": "Mary", "role": "Business Analyst"}'
        (node_dir / "persona.json").write_text(persona_content)
        
        # Minimal evaluator.yaml
        evaluator_content = """
criteria:
  - name: completeness
    description: "All required sections present"
    weight: 0.2
"""
        (node_dir / "evaluator.yaml").write_text(evaluator_content)
        
        return node_dir

    def test_load_new_yaml_format(self, temp_node_dir, monkeypatch):
        """Test NodeLoader can load new YAML format with task block."""
        # Mock NODES_DIR
        monkeypatch.setattr(
            "autoBMAD.docuswarm.nodes.loader.NODES_DIR",
            temp_node_dir.parent
        )
        
        config = NodeLoader.load("analyst")
        
        assert config.node_id == "analyst"
        assert config.task is not None
        assert config.task.name == "create-product-brief"
        assert config.deliverable.template_title == "Product Brief: {project_name}"
```

### Phase 2: 实现新的数据类 (Green)

#### Implementation 2.1: NodeTaskConfig 数据类

```python
# autoBMAD/docuswarm/nodes/loader.py

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

#### Implementation 2.2: 扩展 NodeDeliverableConfig

```python
# autoBMAD/docuswarm/nodes/loader.py

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

#### Implementation 2.3: 重构 NodeConfig

```python
# autoBMAD/docuswarm/nodes/loader.py

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

### Phase 3: 更新 NodeLoader 加载逻辑

```python
# autoBMAD/docuswarm/nodes/loader.py

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

    @classmethod
    def _load_evaluator(cls, path: Path) -> NodeEvaluatorConfig:
        """Load evaluator configuration from YAML."""
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        criteria = [
            EvaluationCriterion(
                name=c.get("name", ""),
                description=c.get("description", ""),
                weight=c.get("weight", 0.2),
            )
            for c in data.get("criteria", [])
        ]

        thresholds_data = data.get("thresholds", {})
        thresholds = EvaluationThresholds(
            approval=thresholds_data.get("approval", 0.7),
            revision=thresholds_data.get("revision", 0.4),
        )

        return NodeEvaluatorConfig(criteria=criteria, thresholds=thresholds)
```

### Phase 4: 向后兼容性测试

```python
# tests/nodes/test_backward_compatibility.py
"""Tests for backward compatibility with old YAML format."""

import pytest
from autoBMAD.docuswarm.nodes.loader import NodeLoader


class TestBackwardCompatibility:
    """Ensure old YAML format without task block still works."""

    @pytest.fixture
    def legacy_node_dir(self, tmp_path):
        """Create legacy format node directory."""
        node_dir = tmp_path / "legacy_node"
        node_dir.mkdir()
        
        # Legacy format without task block
        yaml_content = """
node_id: legacy_node
name: Legacy Node
description: Old format description
sequence: 1
deliverable:
  type: legacy-report
  required_sections:
    - section1
    - section2
agent:
  type: independent
  model: sonnet
# 注意: 没有 task 块
# 注意: 可能有 questions/dependencies 但应该被忽略
"""
        (node_dir / "node.yaml").write_text(yaml_content)
        return node_dir

    def test_load_legacy_format(self, legacy_node_dir, monkeypatch):
        """Test loading legacy format without errors."""
        monkeypatch.setattr(
            "autoBMAD.docuswarm.nodes.loader.NODES_DIR",
            legacy_node_dir.parent
        )
        
        config = NodeLoader.load("legacy_node")
        
        assert config.node_id == "legacy_node"
        assert config.task is None  # 应该为None而不是报错
        assert config.deliverable.template_title == ""  # 默认值
```

---

## 4. 配置文件迁移脚本

### 4.1 迁移脚本测试

```python
# tests/nodes/test_config_migration.py
"""Tests for configuration migration from old to new format."""

import pytest
import json
from pathlib import Path


class TestConfigMigration:
    """Test migration of existing configs to new format."""

    def test_migrate_analyst_node(self, tmp_path):
        """Test migrating analyst node config."""
        from autoBMAD.docuswarm.scripts.migrate_config import migrate_node_config
        
        # Create old format config
        old_config = {
            "node_id": "analyst",
            "name": "Analyst",
            "description": "Data Analyst",
            "sequence": 1,
            "deliverable": {
                "type": "analyst-report",
                "required_sections": ["summary", "findings"]
            },
            "agent": {"type": "independent", "model": "sonnet"},
            "questions": [{"id": "q1", "text": "Question?"}],  # 将被移除
            "dependencies": []  # 将被移除
        }
        
        # BMM内容映射（从_bmad/bmm/预处理提取）
        bmm_task = {
            "name": "create-product-brief",
            "description": "Create comprehensive product briefs",
            "role_supplement": "You are a product-focused Business Analyst"
        }
        
        bmm_deliverable = {
            "template_title": "Product Brief: {project_name}",
            "output_filename": "product-brief-{project_name}.md",
            "required_sections": [
                "executive_summary", "core_vision", "problem_statement"
            ]
        }
        
        migrated = migrate_node_config(old_config, bmm_task, bmm_deliverable)
        
        # 验证迁移结果
        assert "task" in migrated
        assert migrated["task"]["name"] == "create-product-brief"
        assert "questions" not in migrated
        assert "dependencies" not in migrated
        assert migrated["deliverable"]["template_title"] == "Product Brief: {project_name}"
```

---

## 5. 实施清单

| 步骤 | 任务 | 测试文件 | 实现文件 | 状态 |
|------|------|----------|----------|------|
| 1 | 创建 NodeTaskConfig 测试 | `test_node_task_config.py` | `loader.py` | ⬜ |
| 2 | 扩展 NodeDeliverableConfig 测试 | `test_deliverable_config.py` | `loader.py` | ⬜ |
| 3 | 新 NodeConfig 结构测试 | `test_node_config_structure.py` | `loader.py` | ⬜ |
| 4 | YAML 加载测试 | `test_yaml_loading.py` | `loader.py` | ⬜ |
| 5 | 向后兼容测试 | `test_backward_compatibility.py` | `loader.py` | ⬜ |
| 6 | 移除废弃数据类 | - | `loader.py` | ⬜ |
| 7 | 更新验证逻辑 | `test_validation.py` | `loader.py` | ⬜ |
| 8 | 迁移脚本测试 | `test_config_migration.py` | `migrate_config.py` | ⬜ |

---

## 6. 验证命令

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

## 7. 风险评估

| 风险 | 严重度 | 缓解策略 |
|------|--------|----------|
| 旧配置无法加载 | 高 | 保持向后兼容，task字段可选 |
| 测试覆盖不足 | 中 | 每个新功能必须有测试 |
| 类型检查失败 | 低 | 使用 basedpyright 严格模式 |

---

**文档结束**
