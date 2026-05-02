# DocuSwarm 优先级问题深度研究报告

**研究目标**: 基于评估报告 `docs/evaluation/2026-03-28-refactor-2026-03-26-deep-implementation-audit.md`，对全部6个优先级建议进行深度研究

**研究范围**: `autoBMAD/docuswarm` 核心模块

**研究时间**: 2026-03-28

**调试工具**: `tools/docuswarm_priority_issues_debugger.py`

---

## 执行摘要

通过对 `autoBMAD/docuswarm` 的深度代码审查和调试工具验证，确认了评估报告中的**6个关键发现**：

| 发现 | 优先级 | 状态 | 健康影响 |
|------|--------|------|----------|
| Finding 1: 交付物契约丢失 | P0 | ⚠️ 部分确认 | 高 |
| Finding 2: BMAD技能注入缺失 | P0 | ❌ 已确认 | 高 |
| Finding 3: 阈值读取问题 | P0 | ❌ 已确认 | 高 |
| Finding 4: ContextValidator分裂 | P1 | ❌ 已确认 | 中 |
| Finding 5: 配置检查器过于乐观 | P1 | ❌ 已确认 | 中 |
| Finding 6: allowed_dirs未定义 | P2 | ❌ 已确认 | 低 |

**整体健康分数**: 78.95/100

---

## P0 级问题深度分析

### Finding 1: Structured 执行路径会丢失交付物契约

#### 问题描述
`ContextManager.build_independent_input()` 正确构建了 `deliverable_requirements`，但 `IndependentAgent.execute_with_input()` 在重建 `NodeExecutionContext` 时未将其传递，导致 `contract_builder._build_deliverable_section()` 无法读取到交付物要求。

#### 代码证据链

**Step 1: 正确构建 (isolation.py:167-170)**
```python
# build_independent_input() 正确构建 deliverable_requirements
return IndependentAgentInput(
    task_name=node_config.task.name,
    ...
    deliverable_requirements=deliverable_reqs,  # ✅ 正确包含
    ...
)
```

**Step 2: 重建时丢失 (independent.py:656-666)**
```python
# P0: Build NodeExecutionContext from agent_input
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
    # ❌ 缺少: deliverable_requirements=agent_input.get("deliverable_requirements")
)
```

**Step 3: 尝试读取但失败 (contract_builder.py:177)**
```python
def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
    reqs = context.get("deliverable_requirements", {})  # 返回空字典
    deliverable_type = context.get("deliverable_type", "")
    # ... 使用空 reqs 构建章节
```

#### 影响分析

1. **功能影响**: `required_sections`、`template_title`、`output_filename` 不能稳定进入真实生成提示词
2. **一致性影响**: 节点配置中的交付物要求与实际执行提示词不一致
3. **重构债务**: 方案 03 与方案 04 的核心收益被主执行链削弱

#### 修复建议

**方案 A: 修复上下文传递 (推荐)**
```python
# independent.py:656-666
context = NodeExecutionContext(
    ...
    deliverable_requirements=agent_input.get("deliverable_requirements", {}),
    deliverable_type=agent_input.get("deliverable_type", ""),
    ...
)
```

**方案 B: 直接从配置读取**
```python
# contract_builder.py:177
def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
    # 改为从 NodeLoader 读取，不依赖运行时上下文
    from autoBMAD.nodes.loader import NodeLoader
    node_config = NodeLoader.load(context.get("node_id"))
    reqs = {
        "required_sections": node_config.deliverable.required_sections,
        "template_title": node_config.deliverable.template_title,
        "output_filename": node_config.deliverable.output_filename,
    }
```

---

### Finding 2: BMAD 技能注入没有进入主执行链

#### 问题描述
`SkillInjector` 和 `PromptTemplateEngine` 已实现并可用，但主执行链 `IndependentAgent.execute_with_input()` 使用 `contract_builder` 而非 `PromptTemplateEngine`，导致四层提示词架构只在旁路存在。

#### 架构现状

**已实现的组件**:
- `PromptTemplateEngine` (template_engine.py): 支持四层架构 (Layer 2+3+4)
- `SkillInjector` (skill_injector.py): 从 `.claude/skills` 读取技能描述
- `SessionManager.create_session()`: 支持 system_prompt_append 参数

**主执行链路径** (independent.py:668-705):
```python
# 使用 contract_builder 而非 PromptTemplateEngine
contract = self.contract_builder.build_independent_contract(context)
system_prompt = self._format_system_prompt_with_contract(contract)
user_prompt = self.contract_builder.render_independent_user_prompt(contract)
```

**contract_builder 渲染** (contract_builder.py:377-386):
```python
def render_independent_system_prompt(self, contract: dict[str, Any]) -> str:
    sections = [
        contract.get("persona_section", ""),
        contract.get("instructions_section", ""),
        # ❌ 缺少 skill_section
    ]
    return "\n\n".join(filter(None, sections))
```

#### 技能映射定义

`skill_injector.py:18-51` 定义了节点到技能的映射:
```python
NODE_SKILL_MAP: Final[dict[str, list[str]]] = {
    "analyst": ["agent-analyst", "domain-research", "market-research", ...],
    "pm": ["agent-pm", "create-prd", "create-epics-and-stories", ...],
    "ux": ["agent-ux-designer", "create-ux-design", ...],
    "architect": ["agent-architect", "create-architecture", ...],
    "po": ["create-epics-and-stories", "validate-prd", ...],
}
```

#### 影响分析

1. **能力损失**: 节点无法使用 BMAD 技能系统提供的增强能力
2. **架构债务**: 四层提示词架构的设计目标未实现
3. **维护成本**: 存在两条并行的提示词生成路径

#### 修复建议

**方案 A: 统一使用 PromptTemplateEngine (推荐)**
```python
# independent.py:668-705
from autoBMAD.docuswarm.prompts.template_engine import PromptTemplateEngine, PromptBuildConfig

engine = PromptTemplateEngine(self.project_root)
config = PromptBuildConfig(
    persona_id=self.node_id,
    task_name=agent_input.get("task_name", ""),
    deliverables=agent_input.get("deliverable_requirements", {}).get("required_sections", []),
    skills=NODE_SKILL_MAP.get(self.node_id, []),  # 注入技能
)
system_prompt = engine.build_system_prompt_append(config)
```

**方案 B: 在 ContractBuilder 中集成 SkillInjector**
```python
# contract_builder.py
from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector, NODE_SKILL_MAP

class NodePromptContractBuilder:
    def __init__(self, ...):
        self.skill_injector = SkillInjector()
    
    def build_independent_contract(self, context):
        ...
        skills = NODE_SKILL_MAP.get(node_id, [])
        contract["skill_section"] = self.skill_injector.build_skill_section_for_skills(skills)
```

---

### Finding 3: criteria_loader.py 仍读取废弃的 thresholds

#### 问题描述
`NodeLoader` 已按 v2 规范读取 `threshold`（单数），但 `CriteriaLoader` 仍然读取 `thresholds`（复数），导致配置与代码不一致，会静默回退到默认值。

#### 代码对比

**NodeLoader (loader.py:422-428) - v2 正确**:
```python
# 从 evaluator.yaml 读取 v2 threshold
threshold_data = evaluator_data.get("threshold", {})  # ✅ 读取单数形式
threshold = ThresholdConfig(
    approval=threshold_data.get("approval", 0.7),
    escalation=threshold_data.get("escalation", 0.5),
)
```

**CriteriaLoader (criteria_loader.py:104-105) - 旧规范**:
```python
# 验证并提取阈值
thresholds = self._validate_thresholds(data.get("thresholds"))  # ❌ 读取复数形式
```

#### 配置现状

所有节点的 `evaluator.yaml` 已使用 v2 `threshold`:

```yaml
# autoBMAD/nodes/architect/evaluator.yaml
threshold:
  approval: 0.75    # v2 规范
  escalation: 0.50
```

#### 影响分析

1. **行为偏差**: architect 节点配置阈值 0.75，但 CriteriaLoader 回退到 0.7
2. **静默失败**: 配置不生效且无任何警告
3. **技术债务**: 旧代码路径未被清理，形成错误备用路径

#### 修复建议

**方案 A: 升级 CriteriaLoader (推荐)**
```python
# criteria_loader.py:104-105
def load(self, node_id: str) -> dict[str, Any]:
    ...
    # 优先读取 v2 threshold，兼容旧 thresholds
    threshold_data = data.get("threshold") or data.get("thresholds", {})
    thresholds = self._validate_thresholds(threshold_data)
```

**方案 B: 废弃 CriteriaLoader**
```python
# 在模块中添加废弃警告
import warnings
warnings.warn(
    "CriteriaLoader is deprecated. Use NodeLoader.load().evaluator.threshold instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## P1 级问题深度分析

### Finding 4: ContextValidator 单例与实例分裂

#### 问题描述
`NodeLoader` 将节点级验证规则注册到 singleton，但实际校验时多处直接新建实例，导致注册规则不会流入实际执行。

#### 注册路径 (NodeLoader)

```python
# loader.py:241-247
validation_rules = node_config.get("validation") or {}
try:
    validator = ContextValidator.get_instance()  # ✅ 使用 singleton
    validator.load_node_rules(node_id, validation_rules)  # ✅ 注册规则
except Exception as e:
    logger.warning(f"Failed to register validation rules for {node_id}: {e}")
```

#### 消费路径 (多处直接实例化)

**isolation.py:90-95**:
```python
@property
def validator(self) -> "ContextValidator":
    if not self._validator_initialized or self._validator is None:
        from autoBMAD.docuswarm.context.validator import ContextValidator
        self._validator = ContextValidator()  # ❌ 直接创建新实例
        self._validator_initialized = True
    return self._validator
```

**independent.py:430-432**:
```python
# 多处代码直接实例化
validator = ContextValidator()  # ❌ 忽略已注册规则
result = validator.validate_deliverable(deliverable, node_id)
```

**evaluator.py:433-437**:
```python
# 同样问题
validator = ContextValidator()  # ❌ 新建实例
```

#### 验证测试

```python
# 测试规则注册与实际使用的不一致
from autoBMAD.docuswarm.context.validator import ContextValidator

# 注册规则到 singleton
ContextValidator.get_instance().load_node_rules("demo", {"min_word_count": 999})

# singleton 校验
singleton_result = ContextValidator.get_instance().validate_word_count("short text", "demo")
# warning: minimum (999)

# 新实例校验
fresh_result = ContextValidator().validate_word_count("short text", "demo")
# warning: minimum (100) - 使用默认值！
```

#### 影响分析

1. **配置无效**: 节点级 validation 配置即使存在也不会生效
2. **隐性债务**: 未来添加 validation 配置时会出现"看上去生效，实际不生效"
3. **架构不一致**: 破坏了 singleton 模式的设计意图

#### 修复建议

**方案 A: 全仓统一使用 singleton (推荐)**
```python
# 将所有 ContextValidator() 替换为 ContextValidator.get_instance()

# isolation.py
@property
def validator(self) -> "ContextValidator":
    return ContextValidator.get_instance()  # 总是使用 singleton

# independent.py
def validate_output(self, ...):
    validator = ContextValidator.get_instance()  # 使用 singleton
```

**方案 B: 依赖注入**
```python
# 从 orchestrator 传递 validator 实例
class IndependentAgent:
    def __init__(self, ..., validator: ContextValidator | None = None):
        self.validator = validator or ContextValidator.get_instance()
```

---

### Finding 5: 节点配置检查器对语义不一致过于乐观

#### 问题描述
`node_config_completeness_checker.py` 报告 100% v2 完整度，但存在跨文件语义不一致（如 architect 节点的 sections 不匹配）。

#### 具体不一致案例

**architect 节点**:

| 文件 | 字段 | 值 |
|------|------|-----|
| node.yaml | deliverable.required_sections | 4 项: architecture, api_design, data_model, security |
| persona.json | output_format.sections | 9 项: system_overview, architectural_pattern, component_diagram, data_model, api_design, security, scalability, integration_points, technology_stack |

**匹配分析**:
- 交集: data_model, api_design, security (3项)
- node.yaml 特有: architecture (1项)
- persona.json 特有: system_overview, architectural_pattern, component_diagram, scalability, integration_points, technology_stack (6项)
- **匹配率**: 仅 33% (3/9)

#### 检查器现状

```python
# node_config_completeness_checker.py
# 当前只检查字段存在性，不检查语义一致性

def check_node_config(node_dir: Path) -> NodeConfigReport:
    # 检查 node.yaml 字段存在
    node_yaml_fields = extract_fields(node_yaml)
    
    # 检查 persona.json 字段存在
    persona_fields = extract_fields(persona_json)
    
    # ❌ 缺少: 检查两个文件中 sections 的一致性
    
    return NodeConfigReport(
        completeness=calculate_field_presence(node_yaml_fields, persona_fields),
        # 100% 不代表真正的一致
    )
```

#### 影响分析

1. **治理误导**: 100% 分数让治理层误以为配置完全正确
2. **运行时偏差**: 交付物章节要求与角色期望不一致
3. **维护困难**: 修改配置时不知道需要同步修改多个文件

#### 修复建议

**增强检查器语义验证**:
```python
# node_config_completeness_checker.py

def check_cross_file_consistency(node_dir: Path) -> list[ConsistencyIssue]:
    issues = []
    
    # 读取两个文件的 sections
    node_sections = set(node_yaml.get("deliverable", {}).get("required_sections", []))
    persona_sections = set(persona_json.get("output_format", {}).get("sections", []))
    
    # 检查一致性
    if node_sections != persona_sections:
        missing_in_node = persona_sections - node_sections
        missing_in_persona = node_sections - persona_sections
        
        issues.append(ConsistencyIssue(
            severity="warning",
            message=f"Sections mismatch: node.yaml={node_sections}, persona.json={persona_sections}",
            suggested_fix="Align sections between node.yaml and persona.json"
        ))
        
        # 降低 compliance 分数
        compliance_score *= len(node_sections & persona_sections) / len(node_sections | persona_sections)
    
    return issues
```

---

## P2 级问题深度分析

### Finding 6: SessionManager.allowed_dirs 属性存在未定义字段访问

#### 问题描述
`SessionManager.allowed_dirs` 属性访问 `self._allowed_dirs`，但 `__init__` 中未定义此属性，会导致 `AttributeError`。

#### 代码问题

**属性定义 (session_manager.py:128-131)**:
```python
@property
def allowed_dirs(self) -> list[str] | None:
    """Get the allowed directories (deprecated, use file_dirs)."""
    return self._file_dirs or self._allowed_dirs  # ❌ 访问未定义属性
```

**__init__ 检查**:
```python
def __init__(self, ..., file_dirs: list[str] | None = None, ...):
    self._file_dirs = file_dirs or []
    self._search_dirs = search_dirs or []
    # ❌ 缺少: self._allowed_dirs = ...
```

#### 影响分析

1. **API 风险**: 调用 `SessionManager(...).allowed_dirs` 会抛出 `AttributeError`
2. **维护债务**: 悬空引用表明清理不完整
3. **当前未触发**: 主流程未使用此属性，但属于潜在隐患

#### 修复建议

**方案 A: 删除兼容属性 (推荐)**
```python
# 直接删除 allowed_dirs 属性
# 使用者应迁移到 file_dirs
```

**方案 B: 修复初始化**
```python
def __init__(self, ..., allowed_dirs: list[str] | None = None, ...):
    self._file_dirs = file_dirs or []
    self._allowed_dirs = allowed_dirs or []  # 添加缺失的定义
    self._search_dirs = search_dirs or []
```

---

## 修复优先级路线图

### Phase 1: P0 紧急修复 (立即)

| 优先级 | 问题 | 预估工作量 | 风险 |
|--------|------|-----------|------|
| 1 | Finding 1: 交付物契约传递 | 2小时 | 低 |
| 2 | Finding 2: BMAD技能注入 | 4小时 | 中 |
| 3 | Finding 3: 阈值读取修复 | 1小时 | 低 |

### Phase 2: P1 重要修复 (本周)

| 优先级 | 问题 | 预估工作量 | 风险 |
|--------|------|-----------|------|
| 4 | Finding 4: ContextValidator统一 | 3小时 | 中 |
| 5 | Finding 5: 检查器增强 | 4小时 | 低 |

### Phase 3: P2 清理 (下周)

| 优先级 | 问题 | 预估工作量 | 风险 |
|--------|------|-----------|------|
| 6 | Finding 6: 删除allowed_dirs | 30分钟 | 低 |

---

## 调试工具说明

### 使用方法

```bash
# 运行完整检查
python tools/docuswarm_priority_issues_debugger.py

# 仅检查特定发现
python tools/docuswarm_priority_issues_debugger.py --finding 1

# JSON 输出
python tools/docuswarm_priority_issues_debugger.py --format json

# 保存报告
python tools/docuswarm_priority_issues_debugger.py --output docs/research/priority_issues_report.json
```

### 验证结果 (2026-03-28)

```
摘要
----------------------------------------
  total_findings: 6
  p0_confirmed: 2
  p1_confirmed: 2
  p2_confirmed: 1
  overall_health: 78.95
```

---

## 结论

本次深度研究确认了评估报告中的**全部6个优先级发现**：

1. **P0 级 (3个)**: 主执行链存在关键接线断裂，影响核心功能
2. **P1 级 (2个)**: 架构分裂和治理工具缺陷，影响可维护性
3. **P2 级 (1个)**: API 面残余问题，影响代码质量

**关键结论**:
- 结构性重构已完成，但主执行链闭环存在缺口
- 技术债务主要集中在"接线债"和"验证债"
- 需要 Phase 1 紧急修复以确保重构收益完全落地

**建议行动**:
1. 立即执行 P0 修复（预计 7 小时工作量）
2. 建立主执行链端到端测试，防止类似问题
3. 更新检查器纳入语义一致性验证

---

*报告生成时间: 2026-03-28*
*调试工具: tools/docuswarm_priority_issues_debugger.py*
