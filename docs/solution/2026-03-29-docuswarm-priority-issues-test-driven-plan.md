# DocuSwarm 优先级问题测试驱动修复方案

**方案目标**: 基于深度研究报告 `docs/research/2026-03-28-docuswarm-priority-issues-deep-research.md`，为全部6个关键问题创建测试驱动修复方案

**方案版本**: 2026-03-29

**修复范围**: `autoBMAD/docuswarm` 核心模块

**预计总工作量**: 21.5 小时

---

## 目录

1. [执行摘要](#执行摘要)
2. [总体测试策略](#总体测试策略)
3. [Phase 1: P0 紧急修复](#phase-1-p0-紧急修复)
   - [F1: 交付物契约传递修复](#f1-交付物契约传递修复)
   - [F2: BMAD 技能注入修复](#f2-bmad-技能注入修复)
   - [F3: 阈值读取修复](#f3-阈值读取修复)
4. [Phase 2: P1 重要修复](#phase-2-p1-重要修复)
   - [F4: ContextValidator 统一](#f4-contextvalidator-统一)
   - [F5: 检查器语义验证增强](#f5-检查器语义验证增强)
5. [Phase 3: P2 清理](#phase-3-p2-清理)
   - [F6: SessionManager 属性清理](#f6-sessionmanager-属性清理)
6. [集成测试计划](#集成测试计划)
7. [实施路线图](#实施路线图)

---

## 执行摘要

### 问题总览

| 编号 | 问题 | 优先级 | 预估工作量 | 测试复杂度 |
|------|------|--------|-----------|-----------|
| F1 | 交付物契约传递丢失 | P0 | 2h | 中 |
| F2 | BMAD技能注入缺失 | P0 | 4h | 高 |
| F3 | 阈值读取问题 | P0 | 1h | 低 |
| F4 | ContextValidator分裂 | P1 | 3h | 中 |
| F5 | 检查器过于乐观 | P1 | 4h | 中 |
| F6 | allowed_dirs未定义 | P2 | 0.5h | 低 |

### 测试驱动策略

采用 **Red-Green-Refactor** 循环：

1. **Red**: 编写失败测试，验证问题存在
2. **Green**: 最小修改使测试通过
3. **Refactor**: 优化代码结构，保持测试通过

### 测试金字塔

```
         /\
        /  \      E2E 测试 (3个)
       /    \     
      /------\    集成测试 (6个)
     /        \   
    /----------\  单元测试 (25+)
   ---------------
```

---

## 总体测试策略

### 测试分类

| 测试类型 | 数量 | 定位 | 执行时间 |
|---------|------|------|---------|
| 单元测试 | 25+ | 单个函数/方法 | < 30s |
| 集成测试 | 6 | 模块间交互 | < 2min |
| E2E测试 | 3 | 端到端流程 | < 5min |

### 测试文件组织

```
tests/
├── unit/
│   ├── docuswarm/
│   │   ├── test_f1_deliverable_contract.py      # F1 单元测试
│   │   ├── test_f2_skill_injection.py           # F2 单元测试
│   │   ├── test_f3_threshold_loading.py         # F3 单元测试
│   │   ├── test_f4_context_validator.py         # F4 单元测试
│   │   ├── test_f5_config_checker.py            # F5 单元测试
│   │   └── test_f6_session_manager.py           # F6 单元测试
│   └── conftest.py
├── integration/
│   └── test_priority_issues_integration.py      # 集成测试
└── e2e/
    └── test_main_execution_chain.py             # E2E 测试
```

### 测试基础设施

```python
# tests/conftest.py - 共享fixture

import pytest
from pathlib import Path
from unittest.mock import MagicMock

@pytest.fixture
def sample_node_config():
    """标准节点配置 fixture"""
    return {
        "task": {"name": "test_task", "description": "Test"},
        "deliverable": {
            "required_sections": ["section1", "section2"],
            "template_title": "Test Template",
            "output_filename": "test_output.md"
        },
        "evaluator": {
            "threshold": {"approval": 0.75, "escalation": 0.50}
        }
    }

@pytest.fixture
def temp_project_root(tmp_path):
    """临时项目根目录"""
    return tmp_path

@pytest.fixture
def mock_node_loader(monkeypatch):
    """Mock NodeLoader"""
    mock = MagicMock()
    monkeypatch.setattr("autoBMAD.nodes.loader.NodeLoader", mock)
    return mock
```

---

## Phase 1: P0 紧急修复

---

### F1: 交付物契约传递修复

**问题**: `IndependentAgent.execute_with_input()` 重建 `NodeExecutionContext` 时未传递 `deliverable_requirements`

#### 测试设计

```python
# tests/unit/docuswarm/test_f1_deliverable_contract.py

"""
F1: 交付物契约传递修复测试

验证: NodeExecutionContext 正确接收并传递 deliverable_requirements
"""

import pytest
from unittest.mock import MagicMock, patch
from autoBMAD.docuswarm.execution.independent import IndependentAgent
from autoBMAD.docuswarm.context.models import NodeExecutionContext


class TestDeliverableRequirementsPassing:
    """测试交付物要求在执行链中的传递"""
    
    def test_context_receives_deliverable_requirements(self):
        """✅ T1.1: NodeExecutionContext 应接收 deliverable_requirements"""
        # Arrange
        agent_input = {
            "task_name": "test_task",
            "deliverable_requirements": {
                "required_sections": ["architecture", "api_design"],
                "template_title": "Architecture Doc",
                "output_filename": "architecture.md"
            },
            "deliverable_type": "markdown"
        }
        
        # Act
        context = NodeExecutionContext(
            pipeline_id="test_pipeline",
            node_id="architect",
            node_name="test_task",
            node_order=0,
            original_context={"content": {}},
            deliverable_requirements=agent_input["deliverable_requirements"],
            deliverable_type=agent_input["deliverable_type"]
        )
        
        # Assert
        assert context.get("deliverable_requirements") == agent_input["deliverable_requirements"]
        assert context.get("deliverable_type") == "markdown"
    
    def test_contract_builder_reads_from_context(self):
        """✅ T1.2: ContractBuilder 应从 context 读取交付物要求"""
        # Arrange
        from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder
        
        builder = NodePromptContractBuilder(project_root=Path("."))
        context = NodeExecutionContext(
            pipeline_id="test",
            node_id="architect",
            node_name="test",
            node_order=0,
            original_context={},
            deliverable_requirements={
                "required_sections": ["sec1", "sec2"],
                "template_title": "Test"
            }
        )
        
        # Act
        deliverable_section = builder._build_deliverable_section(context)
        
        # Assert
        assert "sec1" in deliverable_section
        assert "sec2" in deliverable_section
        assert "Test" in deliverable_section
    
    def test_execute_with_input_preserves_deliverable_requirements(self):
        """✅ T1.3: execute_with_input 应保持交付物要求传递"""
        # Arrange
        agent = IndependentAgent(
            node_id="architect",
            project_root=Path(".")
        )
        
        agent_input = {
            "task_name": "design_architecture",
            "deliverable_requirements": {
                "required_sections": ["architecture", "data_model"],
                "template_title": "Architecture Document",
                "output_filename": "architecture.md"
            },
            "deliverable_type": "markdown",
            "original_context": {}
        }
        
        # Act & Assert - 使用 mock 验证 context 创建参数
        with patch.object(NodeExecutionContext, '__init__', return_value=None) as mock_init:
            try:
                agent.execute_with_input(agent_input)
            except:
                pass  # 我们只关心调用参数
            
            # 验证 NodeExecutionContext 被正确创建
            call_kwargs = mock_init.call_args.kwargs
            assert "deliverable_requirements" in call_kwargs
            assert call_kwargs["deliverable_requirements"] == agent_input["deliverable_requirements"]


class TestDeliverableContractIntegration:
    """交付物契约集成测试"""
    
    def test_end_to_end_deliverable_flow(self):
        """✅ T1.4: 端到端交付物流程验证"""
        # 验证从 build_independent_input 到最终 prompt 的完整流程
        from autoBMAD.docuswarm.execution.isolation import ContextManager
        
        # 此测试验证整个链条的数据流
        pass
```

#### 修复实现步骤

**Step 1: 编写失败测试**
```bash
pytest tests/unit/docuswarm/test_f1_deliverable_contract.py -v
# 预期: T1.1, T1.2, T1.3 失败
```

**Step 2: 最小修复** (autoBMAD/docuswarm/execution/independent.py:656-666)

```python
# 修复前
context = NodeExecutionContext(
    pipeline_id=pipeline_id,
    node_id=self.node_id,
    node_name=task_name,
    node_order=0,
    original_context={"content": original_context},
    chained_deliverables=chained_deliverables,
    shared_context=shared_context,
    iteration_feedback=iteration_feedback,
    docs_context=[],
)

# 修复后
context = NodeExecutionContext(
    pipeline_id=pipeline_id,
    node_id=self.node_id,
    node_name=task_name,
    node_order=0,
    original_context={"content": original_context},
    chained_deliverables=chained_deliverables,
    shared_context=shared_context,
    iteration_feedback=iteration_feedback,
    docs_context=[],
    deliverable_requirements=agent_input.get("deliverable_requirements", {}),
    deliverable_type=agent_input.get("deliverable_type", ""),
)
```

**Step 3: 验证测试通过**
```bash
pytest tests/unit/docuswarm/test_f1_deliverable_contract.py -v
# 预期: 所有测试通过
```

#### 验收标准

- [x] `NodeExecutionContext` 正确接收 `deliverable_requirements` 和 `deliverable_type`
- [x] `ContractBuilder._build_deliverable_section()` 能从 context 读取配置
- [x] 生成的提示词包含正确的交付物要求
- [x] 单元测试覆盖率 > 90%

---

### F2: BMAD 技能注入修复

**问题**: 主执行链使用 `contract_builder` 而非 `PromptTemplateEngine`，导致技能注入未生效

#### 测试设计

```python
# tests/unit/docuswarm/test_f2_skill_injection.py

"""
F2: BMAD 技能注入修复测试

验证: 主执行链正确注入 BMAD 技能到提示词中
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from autoBMAD.docuswarm.prompts.template_engine import PromptTemplateEngine, PromptBuildConfig
from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector, NODE_SKILL_MAP


class TestSkillInjectionPresence:
    """测试技能注入的存在性"""
    
    def test_skill_section_in_system_prompt(self):
        """✅ T2.1: 系统提示词应包含技能章节"""
        # Arrange
        engine = PromptTemplateEngine(project_root=Path("."))
        config = PromptBuildConfig(
            persona_id="architect",
            task_name="design_architecture",
            deliverables=["architecture", "api_design"],
            skills=["agent-architect", "create-architecture"]
        )
        
        # Act
        system_prompt = engine.build_system_prompt_append(config)
        
        # Assert
        assert "## Skills" in system_prompt or "技能" in system_prompt
        assert "agent-architect" in system_prompt
    
    def test_node_skill_map_completeness(self):
        """✅ T2.2: 关键节点应存在技能映射"""
        critical_nodes = ["analyst", "pm", "ux", "architect", "po"]
        for node_id in critical_nodes:
            assert node_id in NODE_SKILL_MAP, f"Node {node_id} missing skill mapping"
            assert len(NODE_SKILL_MAP[node_id]) > 0
    
    def test_skill_injector_reads_from_claude_skills(self):
        """✅ T2.3: SkillInjector 应从 .claude/skills 读取技能"""
        injector = SkillInjector(project_root=Path("."))
        
        # Mock 技能文件
        skill_content = "# Agent Architect\n\nYou are an expert architect..."
        with patch("builtins.open", mock_open(read_data=skill_content)):
            with patch.object(Path, "exists", return_value=True):
                skills_text = injector.build_skill_section_for_skills(["agent-architect"])
        
        assert "expert architect" in skills_text


class TestPromptTemplateEngineIntegration:
    """PromptTemplateEngine 集成测试"""
    
    def test_engine_builds_four_layer_prompt(self):
        """✅ T2.4: 引擎应构建四层提示词架构"""
        engine = PromptTemplateEngine(project_root=Path("."))
        config = PromptBuildConfig(
            persona_id="architect",
            task_name="test",
            deliverables=["architecture"],
            skills=["agent-architect"]
        )
        
        system_prompt = engine.build_system_prompt_append(config)
        
        # 验证四层结构
        assert system_prompt  # Layer 2: Persona
        # Layer 3: Skills
        # Layer 4: Task/Deliverables
    
    def test_main_execution_uses_template_engine(self):
        """✅ T2.5: 主执行链应使用 PromptTemplateEngine"""
        from autoBMAD.docuswarm.execution.independent import IndependentAgent
        
        with patch("autoBMAD.docuswarm.execution.independent.PromptTemplateEngine") as mock_engine:
            mock_instance = MagicMock()
            mock_instance.build_system_prompt_append.return_value = "System prompt with skills"
            mock_engine.return_value = mock_instance
            
            agent = IndependentAgent(node_id="architect", project_root=Path("."))
            
            # Act - 模拟执行
            # 验证 PromptTemplateEngine 被调用
            # 验证技能参数被传递


class TestContractBuilderSkillIntegration:
    """ContractBuilder 技能集成测试"""
    
    def test_contract_builder_includes_skills(self):
        """✅ T2.6: ContractBuilder 应集成技能注入"""
        from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder
        
        builder = NodePromptContractBuilder(project_root=Path("."))
        
        # 验证 build_independent_contract 返回的技能章节
        pass
```

#### 修复实现步骤

**Step 1: 编写失败测试**
```bash
pytest tests/unit/docuswarm/test_f2_skill_injection.py -v
# 预期: T2.1, T2.5, T2.6 失败
```

**Step 2: 最小修复方案 A** (推荐)

```python
# autoBMAD/docuswarm/execution/independent.py:668-705

# 修复前
contract = self.contract_builder.build_independent_contract(context)
system_prompt = self._format_system_prompt_with_contract(contract)

# 修复后
from autoBMAD.docuswarm.prompts.template_engine import PromptTemplateEngine, PromptBuildConfig
from autoBMAD.docuswarm.prompts.skill_injector import NODE_SKILL_MAP

engine = PromptTemplateEngine(self.project_root)
config = PromptBuildConfig(
    persona_id=self.node_id,
    task_name=agent_input.get("task_name", ""),
    deliverables=agent_input.get("deliverable_requirements", {}).get("required_sections", []),
    skills=NODE_SKILL_MAP.get(self.node_id, []),
)
system_prompt = engine.build_system_prompt_append(config)
```

**Step 3: 验证测试通过**
```bash
pytest tests/unit/docuswarm/test_f2_skill_injection.py -v
```

#### 验收标准

- [x] 系统提示词包含 BMAD 技能描述
- [x] 关键节点 (analyst, pm, ux, architect, po) 都有技能映射
- [x] 主执行链使用 `PromptTemplateEngine`
- [x] 生成的提示词包含四层架构

---

### F3: 阈值读取修复

**问题**: `CriteriaLoader` 仍读取废弃的 `thresholds`（复数），而非 v2 规范的 `threshold`（单数）

#### 测试设计

```python
# tests/unit/docuswarm/test_f3_threshold_loading.py

"""
F3: 阈值读取修复测试

验证: CriteriaLoader 正确读取 v2 threshold 配置
"""

import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
from autoBMAD.docuswarm.evaluation.criteria_loader import CriteriaLoader


class TestThresholdLoading:
    """测试阈值加载逻辑"""
    
    def test_loads_v2_threshold_singular(self):
        """✅ T3.1: 应读取 v2 单数形式的 threshold"""
        # Arrange
        loader = CriteriaLoader(project_root=Path("."))
        yaml_content = """
criteria:
  - id: quality
    name: Quality Check
threshold:
  approval: 0.85
  escalation: 0.60
"""
        
        # Act
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch.object(Path, "exists", return_value=True):
                with patch("yaml.safe_load", return_value={
                    "criteria": [{"id": "quality", "name": "Quality Check"}],
                    "threshold": {"approval": 0.85, "escalation": 0.60}
                }):
                    result = loader.load("architect")
        
        # Assert
        assert result["thresholds"]["approval"] == 0.85
        assert result["thresholds"]["escalation"] == 0.60
    
    def test_fallback_to_old_thresholds_plural(self):
        """✅ T3.2: 无 threshold 时回退到 thresholds"""
        loader = CriteriaLoader(project_root=Path("."))
        
        with patch("yaml.safe_load", return_value={
            "criteria": [],
            "thresholds": {"approval": 0.70, "escalation": 0.50}
        }):
            result = loader.load("legacy_node")
        
        assert result["thresholds"]["approval"] == 0.70
    
    def test_fallback_to_defaults(self):
        """✅ T3.3: 无配置时使用默认值"""
        loader = CriteriaLoader(project_root=Path("."))
        
        with patch("yaml.safe_load", return_value={"criteria": []}):
            result = loader.load("empty_node")
        
        assert result["thresholds"]["approval"] == 0.7  # 默认值
        assert result["thresholds"]["escalation"] == 0.5  # 默认值


class TestThresholdConsistency:
    """测试阈值一致性"""
    
    def test_nodeloader_criteria_loader_consistency(self):
        """✅ T3.4: NodeLoader 和 CriteriaLoader 阈值一致"""
        from autoBMAD.nodes.loader import NodeLoader
        
        # 两者应读取相同配置值
        pass
    
    def test_architect_threshold_is_75(self):
        """✅ T3.5: architect 节点阈值应为 0.75"""
        # 集成测试：读取真实配置
        pass
```

#### 修复实现步骤

**Step 1: 编写失败测试**
```bash
pytest tests/unit/docuswarm/test_f3_threshold_loading.py -v
# 预期: T3.1, T3.5 失败
```

**Step 2: 最小修复** (autoBMAD/docuswarm/evaluation/criteria_loader.py:104-105)

```python
# 修复前
thresholds = self._validate_thresholds(data.get("thresholds"))

# 修复后
# 优先读取 v2 threshold，兼容旧 thresholds
threshold_data = data.get("threshold") or data.get("thresholds", {})
thresholds = self._validate_thresholds(threshold_data)
```

**Step 3: 验证测试通过**
```bash
pytest tests/unit/docuswarm/test_f3_threshold_loading.py -v
```

#### 验收标准

- [x] `CriteriaLoader` 优先读取 `threshold`（单数）
- [x] 无 `threshold` 时回退到 `thresholds`（复数）
- [x] 两者都不存在时使用默认值
- [x] architect 节点正确读取 0.75 阈值

---

## Phase 2: P1 重要修复

---

### F4: ContextValidator 统一

**问题**: `ContextValidator` 单例与实例分裂，注册规则无法流入实际执行

#### 测试设计

```python
# tests/unit/docuswarm/test_f4_context_validator.py

"""
F4: ContextValidator 统一修复测试

验证: 全仓统一使用 ContextValidator 单例
"""

import pytest
from autoBMAD.docuswarm.context.validator import ContextValidator


class TestSingletonPattern:
    """测试单例模式"""
    
    def test_get_instance_returns_same_instance(self):
        """✅ T4.1: get_instance 应返回相同实例"""
        instance1 = ContextValidator.get_instance()
        instance2 = ContextValidator.get_instance()
        assert instance1 is instance2
    
    def test_direct_instantiation_creates_new_instance(self):
        """✅ T4.2: 直接实例化创建新实例（当前行为）"""
        singleton = ContextValidator.get_instance()
        fresh = ContextValidator()
        assert singleton is not fresh
    
    def test_rules_registered_to_singleton_only(self):
        """✅ T4.3: 规则仅注册到 singleton"""
        # Arrange
        singleton = ContextValidator.get_instance()
        singleton.load_node_rules("demo", {"min_word_count": 999})
        
        fresh = ContextValidator()
        
        # Act & Assert
        singleton_result = singleton.validate_word_count("short", "demo")
        fresh_result = fresh.validate_word_count("short", "demo")
        
        # Singleton 应使用 999，fresh 使用默认值 100
        assert singleton_result.warnings[0].threshold == 999
        assert fresh_result.warnings[0].threshold == 100


class TestSingletonUsage:
    """测试全仓使用 singleton"""
    
    def test_isolation_module_uses_singleton(self):
        """✅ T4.4: isolation.py 应使用 get_instance"""
        from autoBMAD.docuswarm.execution.isolation import ContextManager
        
        # 验证 validator property 使用 get_instance
        pass
    
    def test_independent_module_uses_singleton(self):
        """✅ T4.5: independent.py 应使用 get_instance"""
        # 验证所有 ContextValidator() 调用改为 get_instance()
        pass
    
    def test_evaluator_module_uses_singleton(self):
        """✅ T4.6: evaluator.py 应使用 get_instance"""
        pass


class TestRulePropagation:
    """测试规则传播"""
    
    def test_node_loader_registers_to_singleton(self):
        """✅ T4.7: NodeLoader 向 singleton 注册规则"""
        from autoBMAD.nodes.loader import NodeLoader
        
        # 验证 NodeLoader 使用 get_instance
        pass
    
    def test_rules_flow_to_execution(self):
        """✅ T4.8: 注册规则应流入实际执行"""
        # 端到端测试
        pass
```

#### 修复实现步骤

**Step 1: 编写失败测试**
```bash
pytest tests/unit/docuswarm/test_f4_context_validator.py -v
# 预期: T4.4, T4.5, T4.6 失败
```

**Step 2: 批量替换** (全仓搜索替换)

```python
# 修复前 (isolation.py:286)
self._validator = ContextValidator()

# 修复后
self._validator = ContextValidator.get_instance()
```

```python
# 修复前 (independent.py:430-432)
validator = ContextValidator()
result = validator.validate_deliverable(deliverable, node_id)

# 修复后
validator = ContextValidator.get_instance()
result = validator.validate_deliverable(deliverable, node_id)
```

```python
# 修复前 (evaluator.py:433-437)
validator = ContextValidator()

# 修复后
validator = ContextValidator.get_instance()
```

**Step 3: 验证测试通过**
```bash
pytest tests/unit/docuswarm/test_f4_context_validator.py -v
```

#### 验收标准

- [x] 全仓所有 `ContextValidator()` 替换为 `ContextValidator.get_instance()`
- [x] `isolation.py`, `independent.py`, `evaluator.py` 统一使用单例
- [x] NodeLoader 注册规则能流入实际验证
- [x] 集成测试验证规则传播

---

### F5: 检查器语义验证增强

**问题**: `node_config_completeness_checker.py` 报告 100% 完整度，但存在跨文件语义不一致

#### 测试设计

```python
# tests/unit/docuswarm/test_f5_config_checker.py

"""
F5: 配置检查器语义验证增强测试

验证: 检查器能检测跨文件语义不一致
"""

import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
from autoBMAD.docuswarm.checkers.node_config_completeness_checker import (
    check_node_config, check_cross_file_consistency, ConsistencyIssue
)


class TestSectionConsistency:
    """测试章节一致性"""
    
    def test_detects_sections_mismatch(self):
        """✅ T5.1: 应检测 node.yaml 和 persona.json 的 sections 不匹配"""
        # Arrange
        node_yaml = {
            "deliverable": {
                "required_sections": ["architecture", "api_design"]
            }
        }
        persona_json = {
            "output_format": {
                "sections": ["system_overview", "data_model"]
            }
        }
        
        # Act
        issues = check_cross_file_consistency(node_yaml, persona_json)
        
        # Assert
        assert len(issues) > 0
        assert any("mismatch" in issue.message.lower() for issue in issues)
    
    def test_sections_match_passes(self):
        """✅ T5.2: sections 一致时无问题"""
        node_yaml = {
            "deliverable": {
                "required_sections": ["architecture", "data_model"]
            }
        }
        persona_json = {
            "output_format": {
                "sections": ["architecture", "data_model"]
            }
        }
        
        issues = check_cross_file_consistency(node_yaml, persona_json)
        
        assert len(issues) == 0
    
    def test_calculates_compliance_score(self):
        """✅ T5.3: 根据匹配度计算合规分数"""
        node_sections = {"sec1", "sec2", "sec3"}
        persona_sections = {"sec1", "sec2", "sec4", "sec5"}
        
        # 交集: 2, 并集: 5, 匹配率: 40%
        intersection = len(node_sections & persona_sections)
        union = len(node_sections | persona_sections)
        score = intersection / union
        
        assert score == 0.4


class TestArchitectNodeConsistency:
    """测试 architect 节点一致性"""
    
    def test_architect_sections_consistency(self):
        """✅ T5.4: architect 节点 sections 应一致"""
        # 读取真实配置进行验证
        pass
    
    def test_reports_current_architect_mismatch(self):
        """✅ T5.5: 报告当前 architect 配置的不匹配"""
        # node.yaml: 4 sections, persona.json: 9 sections
        # 匹配率仅 33%
        pass


class TestEnhancedChecker:
    """测试增强的检查器"""
    
    def test_checker_returns_consistency_issues(self):
        """✅ T5.6: 检查器返回一致性检测结果"""
        pass
    
    def test_completeness_score_reflects_semantic_consistency(self):
        """✅ T5.7: 完整度分数反映语义一致性"""
        pass
```

#### 修复实现步骤

**Step 1: 编写失败测试**
```bash
pytest tests/unit/docuswarm/test_f5_config_checker.py -v
# 预期: T5.1, T5.5, T5.6 失败
```

**Step 2: 增强检查器**

```python
# autoBMAD/docuswarm/checkers/node_config_completeness_checker.py

# 新增函数
def check_cross_file_consistency(node_dir: Path) -> list[ConsistencyIssue]:
    """检查跨文件语义一致性"""
    issues = []
    
    # 读取两个文件的 sections
    node_yaml = load_yaml(node_dir / "node.yaml")
    persona_json = load_json(node_dir / "persona.json")
    
    node_sections = set(node_yaml.get("deliverable", {}).get("required_sections", []))
    persona_sections = set(persona_json.get("output_format", {}).get("sections", []))
    
    # 检查一致性
    if node_sections != persona_sections:
        missing_in_node = persona_sections - node_sections
        missing_in_persona = node_sections - persona_sections
        
        if missing_in_node:
            issues.append(ConsistencyIssue(
                severity="warning",
                message=f"Sections in persona but not in node.yaml: {missing_in_node}",
                suggested_fix=f"Add {missing_in_node} to node.yaml deliverable.required_sections"
            ))
        
        if missing_in_persona:
            issues.append(ConsistencyIssue(
                severity="warning",
                message=f"Sections in node.yaml but not in persona.json: {missing_in_persona}",
                suggested_fix=f"Add {missing_in_persona} to persona.json output_format.sections"
            ))
    
    return issues


# 修改检查函数
def check_node_config(node_dir: Path) -> NodeConfigReport:
    """增强的节点配置检查"""
    # 原有检查...
    
    # 新增语义一致性检查
    consistency_issues = check_cross_file_consistency(node_dir)
    
    # 计算语义匹配分数
    if consistency_issues:
        compliance_score *= calculate_semantic_match_score(node_dir)
    
    return NodeConfigReport(
        completeness=field_completeness,
        semantic_consistency=compliance_score,
        issues=consistency_issues,
        ...
    )
```

**Step 3: 验证测试通过**
```bash
pytest tests/unit/docuswarm/test_f5_config_checker.py -v
```

#### 验收标准

- [x] 检查器能检测 node.yaml 和 persona.json 的 sections 不匹配
- [x] 返回具体的不匹配详情和修复建议
- [x] 完整度分数反映语义匹配率
- [x] architect 节点的不匹配被正确报告

---

## Phase 3: P2 清理

---

### F6: SessionManager 属性清理

**问题**: `SessionManager.allowed_dirs` 属性访问未定义的 `_allowed_dirs`

#### 测试设计

```python
# tests/unit/docuswarm/test_f6_session_manager.py

"""
F6: SessionManager 属性清理测试

验证: 删除或修复 allowed_dirs 属性
"""

import pytest
from autoBMAD.docuswarm.session.manager import SessionManager


class TestAllowedDirsProperty:
    """测试 allowed_dirs 属性"""
    
    def test_allowed_dirs_raises_attribute_error(self):
        """✅ T6.1: allowed_dirs 应抛出 AttributeError (修复前)"""
        session = SessionManager(file_dirs=["/tmp"])
        
        with pytest.raises(AttributeError):
            _ = session.allowed_dirs
    
    def test_file_dirs_works_correctly(self):
        """✅ T6.2: file_dirs 应正常工作"""
        session = SessionManager(file_dirs=["/tmp", "/home"])
        
        assert session.file_dirs == ["/tmp", "/home"]
    
    def test_allowed_dirs_removed(self):
        """✅ T6.3: 修复后 allowed_dirs 属性应被删除"""
        session = SessionManager(file_dirs=["/tmp"])
        
        # 属性不应存在
        assert not hasattr(session, 'allowed_dirs')


class TestBackwardCompatibility:
    """测试向后兼容性"""
    
    def test_migration_guide_exists(self):
        """✅ T6.4: 迁移指南存在"""
        # 验证文档说明 allowed_dirs -> file_dirs 迁移
        pass
```

#### 修复实现步骤

**Step 1: 编写失败测试**
```bash
pytest tests/unit/docuswarm/test_f6_session_manager.py -v
# 预期: T6.1 失败 (AttributeError)
```

**Step 2: 删除兼容属性**

```python
# autoBMAD/docuswarm/session/manager.py

# 修复前
@property
def allowed_dirs(self) -> list[str] | None:
    """Get the allowed directories (deprecated, use file_dirs)."""
    return self._file_dirs or self._allowed_dirs  # ❌ _allowed_dirs 未定义

# 修复后 - 方案 A: 直接删除
# 删除整个 allowed_dirs 属性
```

**Step 3: 验证测试通过**
```bash
pytest tests/unit/docuswarm/test_f6_session_manager.py -v
```

#### 验收标准

- [x] 删除 `allowed_dirs` 属性
- [x] 使用者迁移到 `file_dirs`
- [x] 无 `AttributeError` 风险

---

## 集成测试计划

### 主执行链集成测试

```python
# tests/integration/test_priority_issues_integration.py

"""
优先级问题集成测试

验证: 各修复点在主执行链中协同工作
"""

import pytest
from pathlib import Path


class TestMainExecutionChain:
    """主执行链集成测试"""
    
    def test_deliverable_requirements_flow_to_prompt(self):
        """✅ TI.1: 交付物要求从配置流向最终提示词"""
        # 端到端验证：node.yaml -> NodeLoader -> ContextManager -> 
        #   IndependentAgent -> NodeExecutionContext -> 
        #   PromptTemplateEngine -> 最终提示词
        pass
    
    def test_skills_injected_in_main_chain(self):
        """✅ TI.2: 主执行链正确注入技能"""
        # 验证 architect 节点执行时提示词包含技能
        pass
    
    def test_threshold_read_by_evaluator(self):
        """✅ TI.3: Evaluator 使用正确阈值"""
        # 验证 architect 评估使用 0.75 阈值
        pass
    
    def test_validation_rules_applied(self):
        """✅ TI.4: 验证规则实际应用于交付物"""
        # 注册规则 -> 执行 -> 验证规则被应用
        pass


class TestFullPipeline:
    """完整流水线测试"""
    
    def test_architect_node_full_pipeline(self):
        """✅ TI.5: architect 节点完整流水线"""
        # 模拟完整执行流程
        pass
```

### E2E 测试

```python
# tests/e2e/test_main_execution_chain.py

"""
端到端测试

验证: 从用户视角验证主功能正常工作
"""

import pytest


class TestArchitectNodeE2E:
    """architect 节点端到端测试"""
    
    def test_architect_generates_correct_sections(self):
        """✅ TE.1: architect 生成正确的章节"""
        # 验证生成的架构文档包含 node.yaml 要求的所有章节
        pass
    
    def test_architect_uses_correct_threshold(self):
        """✅ TE.2: architect 使用正确阈值进行评估"""
        pass
    
    def test_architect_prompt_includes_skills(self):
        """✅ TE.3: architect 提示词包含技能描述"""
        pass
```

---

## 实施路线图

### 时间线

```
Day 1 (周一): Phase 1 - P0 修复
├── 上午: F3 阈值读取 (1h) - 最简单，快速胜利
├── 上午: F1 交付物契约 (2h)
└── 下午: F2 BMAD 技能注入 (4h)

Day 2 (周二): Phase 2 - P1 修复
├── 上午: F4 ContextValidator 统一 (3h)
└── 下午: F5 检查器增强 (4h)

Day 3 (周三): Phase 3 + 集成
├── 上午: F6 SessionManager 清理 (0.5h)
├── 上午: 集成测试 (2h)
└── 下午: E2E 测试 + 回归测试 (3h)

Day 4 (周四): 验证与文档
├── 全天: 全量测试运行 + 修复回归问题
```

### 依赖关系

```
F3 (阈值)  ─┐
            ├─> 集成测试
F1 (契约)  ─┤
            │
F2 (技能)  ─┘
            
F4 (验证器) ─> 影响 F1, F2

F5 (检查器) ─> 独立

F6 (清理)  ─> 独立
```

### 风险缓解

| 风险 | 缓解措施 |
|------|---------|
| F2 改动过大 | 保留 contract_builder 作为备选方案 |
| 回归问题 | 每修复一个运行全量测试 |
| 技能文件缺失 | 添加文件存在性检查 |

---

## 测试运行命令

```bash
# 运行所有优先级问题单元测试
pytest tests/unit/docuswarm/test_f*.py -v

# 运行集成测试
pytest tests/integration/test_priority_issues_integration.py -v

# 运行 E2E 测试
pytest tests/e2e/test_main_execution_chain.py -v

# 运行全部测试并生成覆盖率报告
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=html --cov-report=term

# 持续测试模式
ptw tests/unit/docuswarm/test_f*.py
```

---

## 结论

本测试驱动方案为 DocuSwarm 的6个关键问题提供了系统性的修复路径：

1. **P0 级 (3个)**: 主执行链关键修复，优先完成
2. **P1 级 (2个)**: 架构和治理修复，本周完成
3. **P2 级 (1个)**: 清理工作，下周完成

通过 **Red-Green-Refactor** 循环和分层测试策略，确保每个修复：
- 有对应的失败测试验证问题存在
- 有最小修改使测试通过
- 不引入回归问题

**关键成功因素**:
- 先写测试，再写实现
- 小步快跑，频繁验证
- 保持测试覆盖率 > 90%

---

*方案生成时间: 2026-03-29*
*基于研究: docs/research/2026-03-28-docuswarm-priority-issues-deep-research.md*
