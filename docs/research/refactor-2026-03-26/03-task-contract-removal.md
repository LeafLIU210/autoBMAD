# Task 契约彻底移除方案研究报告

**文档版本**: 1.0.0  
**日期**: 2026-03-26  
**作者**: James (Backend Dev)  
**任务 ID**: #4  
**状态**: 草稿

---

## 1. 执行摘要

### 1.1 问题背景

DocuSwarm 的 `contracts.py` 模块定义了 6 个 TypedDict 类，共计约 50 个字段。诊断工具扫描显示，这些契约与各节点的 `persona.json` / `node.yaml` 配置之间存在**结构性的 DRY 违反**：

- `node.yaml` 中的 `deliverable.required_sections` 字段与 `DeliverableRequirements.required_sections` **语义重复**
- `persona.json` 中的 `output_format.sections` 与 `DeliverableRequirements.required_sections` **语义等价**  
- `IndependentAgentInput` 中的 `role_supplement`、`deliverable_requirements` 等字段完全来源于节点配置，却再次打包为契约字段传递
- `EvaluatorAgentInput.criteria` 可直接从 `evaluator.yaml` 加载，无需通过 `NodeExecutionContext` 中转

当一个节点（如 `analyst`）需要修改交付物章节要求时，开发者必须同步修改以下 **3 处**：
1. `persona.json → output_format.sections`
2. `node.yaml → deliverable.required_sections`
3. 运行时 `DeliverableRequirements`（由 `context_builder.py` 从 node.yaml 读取）

这一三重冗余是典型的 DRY 违反，也是潜在 Bug 的根源。

### 1.2 移除目标

| 目标 | 预期收益 |
|------|---------|
| 以 `persona.json` + `node.yaml` 作为单一配置真相源 | 消除三重冗余，修改成本降低 66% |
| 简化 `NodeExecutionContext` 协议，移除 Task 相关字段 | 协议字段从 15 个缩减至 9 个 |
| `IndependentAgentInput` 中的 persona 字段直接从配置加载 | 消除中间层传递，减少序列化/反序列化开销 |
| 统一 `evaluator_criteria` 加载路径 | `evaluator.yaml` 成为唯一的评估标准来源 |

### 1.3 移除范围

**可安全移除的字段**（从 `NodeExecutionContext` 中移出）：

- `task_name`（移至 `node.yaml → task.name`）
- `task_description`（移至 `node.yaml → description`）
- `role_supplement`（移至 `node.yaml → task.role_supplement`）
- `deliverable_type`（已存在于 `node.yaml`）
- `deliverable_requirements`（已完全由 `node.yaml → deliverable` 覆盖）
- `evaluator_criteria`（移至 `evaluator.yaml`，已存在）

**必须保留的字段**（运行时动态数据，无法静态配置）：

- `pipeline_id`、`node_id`、`node_name`、`node_order`（身份标识）
- `original_context`、`chained_deliverables`、`shared_context`（运行时上下文）
- `iteration_feedback`（迭代状态）
- `docs_context`（扩展文档上下文）

---

## 2. 现状分析

### 2.1 contracts.py 中所有 Task 相关类的完整定义

**文件位置**: `autoBMAD/docuswarm/node_execution/contracts.py`（共 125 行）

#### 2.1.1 DeliverableRequirements（第 13-19 行）

```python
class DeliverableRequirements(TypedDict, total=False):
    """交付物要求"""
    required_sections: list[str]    # ← 与 node.yaml.deliverable.required_sections 重复
    template_title: str              # ← 与 node.yaml.deliverable_type 语义等价
    output_filename: str             # ← node.yaml 中无对应字段（独有字段）
    format_hints: dict[str, Any]     # ← node.yaml 中无对应字段（独有字段）
```

#### 2.1.2 DeliverableArtifact（第 22-36 行）

```python
class DeliverableArtifact(TypedDict):
    """交付物元数据 - 文件层为唯一真相"""
    title: str           # 运行时生成
    summary: str         # 运行时生成（1-2句摘要）
    file_path: str       # 运行时生成（磁盘路径）
    sha256: str          # 运行时生成（内容哈希）
    word_count: int      # 运行时生成
    section_index: list[str]  # 运行时生成
    content_type: str    # 固定值 "markdown"（可从 persona 读取）
```

> **注意**: `DeliverableArtifact` 是运行时产物，字段均为执行后生成，不与 persona 重叠。**此类保留**。

#### 2.1.3 NodeExecutionContextRequired（第 39-74 行）

```python
class NodeExecutionContextRequired(TypedDict):
    # === 身份标识 ===（运行时动态，必须保留）
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int

    # === 任务契约 ===（可从 node.yaml 消除）
    task_name: str          # ← 重复：node.yaml.task.name / node.yaml.name
    task_description: str   # ← 重复：node.yaml.description
    role_supplement: str    # ← 重复：node.yaml.task.role_supplement（当前为空）

    # === 交付物契约 ===（可从 node.yaml 消除）
    deliverable_type: str             # ← 重复：node.yaml.deliverable_type
    deliverable_requirements: DeliverableRequirements  # ← 重复（见上）

    # === 上下文数据 ===（运行时动态，必须保留）
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]

    # === 迭代状态 ===（运行时动态，必须保留）
    iteration_feedback: dict[str, Any] | None

    # === 扩展上下文 ===（运行时动态，必须保留）
    docs_context: list[dict[str, Any]]
```

#### 2.1.4 NodeExecutionContext（第 76-80 行）

```python
class NodeExecutionContext(NodeExecutionContextRequired, total=False):
    """Extended execution context fields."""
    evaluator_criteria: list[dict[str, Any]]  # ← 重复：evaluator.yaml.criteria
```

#### 2.1.5 IndependentAgentInput（第 82-95 行）

```python
class IndependentAgentInput(TypedDict, total=False):
    task_name: str                           # ← 从 NodeExecutionContext 复制
    task_description: str                    # ← 从 NodeExecutionContext 复制
    role_supplement: str                     # ← 从 NodeExecutionContext 复制
    deliverable_requirements: DeliverableRequirements  # ← 从 NodeExecutionContext 复制
    original_context_summary: str            # 运行时派生（摘要）
    chained_deliverables_summary: list[...]  # 运行时派生（摘要）
    iteration_feedback: dict[str, Any] | None  # 运行时传递
    persona_context: dict[str, Any]          # ← 已注释为 "由 IndependentAgent 自行加载"，实为空 {}
    shared_context: dict[str, Any]           # 运行时传递
```

> **关键问题**: `persona_context` 字段在 `isolation.py` 中被设为空字典 `{}`（第 113 行），说明此字段已经没有实际意义，但仍然作为协议字段传递。

#### 2.1.6 EvaluatorAgentInput（第 98-108 行）

```python
class EvaluatorAgentInput(TypedDict, total=False):
    task_name: str               # ← 从 NodeExecutionContext 复制
    task_description: str        # ← 从 NodeExecutionContext 复制
    original_context_summary: str  # 运行时派生
    deliverable_artifact: dict[str, Any]  # 运行时交付物
    deliverable_body: str        # 运行时读取（从文件）
    criteria: list[dict[str, Any]]  # ← 可直接从 evaluator.yaml 加载
```

### 2.2 基于诊断工具的使用点清单

诊断工具扫描 137 个 Python 文件，发现以下使用分布：

| 文件 | 导入数 | 使用点数 | 主要用途 |
|------|--------|---------|---------|
| `context/isolation.py` | 3 | 12 | 构建 Independent/Evaluator 输入 |
| `prompts/contract_builder.py` | 1 | 10 | 构建 Prompt 章节 |
| `nodes/dual_agent.py` | 1 | 6 | 执行协议入口 |
| `node_execution/context_builder.py` | 1 | 4 | 构建执行上下文 |
| `agents/evaluator.py` | 2 | 1 | 类型注解 |
| `agents/independent.py` | 2 | 1 | 类型注解 |
| `node_execution/__init__.py` | 1 | 0 | 重导出 |
| `node_execution/contracts.py` | 0 | 2 | 自引用 |
| `node_execution/executor.py` | 0 | 2 | dict_access |

**使用类型分布**：
- 类型注解 (type_annotation): 23 处
- 字典访问 (dict_access): 15 处
- 实例化 (instantiation): 0 处（全部使用字面量 `{}` 构造）

**高频访问字段**：
- `task_name`: 5 处访问
- `task_description`: 2 处访问

### 2.3 各节点 persona.json 字段分析

所有 5 个节点（analyst, architect, pm, po, ux）的 `persona.json` 具有**一致的 schema**：

| 字段 | 类型 | 示例（analyst） |
|------|------|----------------|
| `name` | string | `"Analyst"` |
| `role` | string | `"Data Analyst & Business Intelligence Specialist"` |
| `identity` | string | 角色身份描述（多行） |
| `expertise` | list[string] | 专业领域列表 |
| `principles` | list[string] | 工作原则列表 |
| `tools` | list[string] | 工具列表 |
| `output_format.type` | string | `"analyst-report"` |
| `output_format.sections` | list[string] | 章节列表 |
| `output_format.format` | string | `"markdown"` |

---

## 3. DRY 违反分析

### 3.1 字段对比表

以下表格对 `contracts.py` 中的 Task 相关字段与 `persona.json` / `node.yaml` 进行逐项对比：

#### DeliverableRequirements vs 配置文件

| 契约字段 | 类型 | persona.json 对应 | node.yaml 对应 | DRY 状态 |
|---------|------|-----------------|----------------|---------|
| `required_sections` | list[str] | `output_format.sections` | `deliverable.required_sections` | **三重重复** |
| `template_title` | str | `output_format.type` | `deliverable_type` | **双重重复（语义等价）** |
| `output_filename` | str | 无 | 无 | **契约独有（需迁移）** |
| `format_hints` | dict | 无 | 无 | **契约独有（需迁移）** |

#### NodeExecutionContextRequired 的"任务契约"组 vs node.yaml

| 契约字段 | 类型 | node.yaml 对应字段 | 当前值来源 | DRY 状态 |
|---------|------|--------------------|-----------|---------|
| `task_name` | str | `task.name` 或 `name` | `context_builder.py` 第 62 行 | **重复** |
| `task_description` | str | `description` | `context_builder.py` 第 63 行 | **重复** |
| `role_supplement` | str | `task.role_supplement` | `context_builder.py` 第 64 行 | **重复（当前为空字符串）** |
| `deliverable_type` | str | `deliverable_type` | `context_builder.py` 第 66 行 | **重复** |

#### NodeExecutionContext 可选字段 vs evaluator.yaml

| 契约字段 | 类型 | evaluator.yaml 对应字段 | DRY 状态 |
|---------|------|----------------------|---------|
| `evaluator_criteria` | list[dict] | `criteria`（全部 5 个节点均已配置） | **重复（加载后原样传递）** |

#### IndependentAgentInput 中的无效字段

| 字段 | 当前赋值 | 问题 |
|------|---------|------|
| `persona_context` | `{}` (空字典) | **无效字段**：注释为"由 IndependentAgent 自行加载"，实际从未被 IndependentAgent 使用 |

### 3.2 不一致字段分析

#### 契约有但 persona.json 没有的字段

| 字段 | 所在类 | 性质 |
|------|--------|------|
| `pipeline_id` | `NodeExecutionContextRequired` | 运行时生成，合理 |
| `node_order` | `NodeExecutionContextRequired` | 运行时生成，合理 |
| `original_context` | `NodeExecutionContextRequired` | 运行时输入，合理 |
| `chained_deliverables` | `NodeExecutionContextRequired` | 运行时动态，合理 |
| `shared_context` | `NodeExecutionContextRequired` | 运行时动态，合理 |
| `iteration_feedback` | `NodeExecutionContextRequired` | 运行时迭代，合理 |
| `docs_context` | `NodeExecutionContextRequired` | 运行时动态，合理 |
| `output_filename` | `DeliverableRequirements` | **需迁移到 node.yaml** |
| `format_hints` | `DeliverableRequirements` | **需迁移到 node.yaml** |

#### persona.json 有但契约没有的字段

| 字段 | 所在 persona | 含义 | 当前使用方式 |
|------|-------------|------|------------|
| `identity` | 所有节点 | 角色身份描述 | `PersonaLoader.format_system_prompt()` 使用 |
| `expertise` | 所有节点 | 专业领域 | `PersonaLoader.format_system_prompt()` 使用 |
| `principles` | 所有节点 | 工作原则 | `PersonaLoader.format_system_prompt()` 使用 |
| `tools` | 所有节点 | 可用工具 | `PersonaLoader.format_system_prompt()` 使用 |
| `output_format.format` | 所有节点 | 输出格式 | 用于 prompt 生成 |

### 3.3 语义等价但命名不同的字段

| 契约字段 | persona.json 字段 | node.yaml 字段 | 语义 |
|---------|-----------------|----------------|------|
| `task_name` | `name` | `name` | 节点名称/任务名称 |
| `deliverable_type` | `output_format.type` | `deliverable_type` | 交付物类型 |
| `deliverable_requirements.required_sections` | `output_format.sections` | `deliverable.required_sections` | 必须包含的章节 |
| `deliverable_requirements.template_title` | `output_format.type` | `deliverable_type` | 模板标题/类型名 |
| `evaluator_criteria` | 无 | `evaluator.yaml → criteria` | 评估标准列表 |

---

## 4. 替代方案设计

### 4.1 设计原则

**单一真相源层次**：

```
配置层（静态）：persona.json + node.yaml + evaluator.yaml
      ↓
运行时层（动态）：pipeline_id, original_context, chained_deliverables...
      ↓
协议层（精简）：NodeExecutionContext（仅包含运行时字段）
```

### 4.2 精简后的 NodeExecutionContext 定义

```python
# 目标设计（移除所有可静态配置的字段）
class NodeExecutionContext(TypedDict):
    """精简版统一节点执行上下文 - 仅包含运行时动态字段。
    
    所有静态配置（task_name, task_description, role_supplement,
    deliverable_type, deliverable_requirements, evaluator_criteria）
    均由 DualAgentNode/IndependentAgent 直接从 node.yaml / persona.json
    / evaluator.yaml 读取，不再通过此协议传递。
    """
    # === 身份标识（运行时生成）===
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int

    # === 运行时上下文数据 ===
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]

    # === 迭代状态 ===
    iteration_feedback: dict[str, Any] | None

    # === 扩展上下文 ===
    docs_context: list[dict[str, Any]]
```

字段数：从 15（必填）+ 1（可选）= **16 个**，精简至 **9 个**（减少 44%）。

### 4.3 从 persona 加载配置的实现方案

#### 方案 A：延迟加载（Lazy Loading）

由消费端（`IndependentAgent`、`EvaluatorAgent`）在需要时各自加载 persona：

```python
# 当前实现（已存在于 contract_builder.py 第 111-116 行）
class NodePromptContractBuilder:
    def _build_persona_section(self, context: NodeExecutionContext) -> str:
        from autoBMAD.docuswarm.agents.persona import PersonaLoader
        node_id = context["node_id"]
        persona = PersonaLoader.load(node_id=node_id, use_cache=True)  # 已有缓存
        return PersonaLoader.format_system_prompt(persona, max_tokens=2000)
```

**优点**：改动最小，无需修改 `NodeExecutionContext` 协议；`PersonaLoader.load()` 已有 `use_cache=True` 缓存机制，性能影响可忽略。

**缺点**：各消费端各自加载，存在多次文件 I/O（但有缓存，实际影响极小）。

#### 方案 B：预加载合并（Eager Loading）

由 `NodeExecutionContextBuilder.build()` 提前加载 persona，合并到 `NodeExecutionContext`：

```python
class NodeExecutionContextBuilder:
    def build(self, ...) -> NodeExecutionContext:
        node_config = self.loader.load(node_id)
        # persona 已由 node_config 加载，不再需要额外步骤
        return NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id=node_id,
            node_name=node_config.name,
            node_order=node_config.sequence,
            original_context=original_context,
            chained_deliverables=chained_deliverables or [],
            shared_context=shared_context or {},
            iteration_feedback=iteration_feedback,
            docs_context=[],
        )
```

**推荐：方案 A**，因为 `PersonaLoader` 的缓存机制已经存在，而且方案 A 的改动范围更小、风险更低。

### 4.4 需要扩展 persona schema 的字段

当前 `persona.json` 缺少以下字段，移除 Task 契约后需要补充：

#### 需要扩展到 node.yaml 的字段

| 字段 | 目标位置 | 示例值 |
|------|---------|-------|
| `output_filename` | `node.yaml → deliverable.output_filename` | `"analyst-report.md"` |
| `format_hints` | `node.yaml → deliverable.format_hints` | `{"max_sections": 6}` |
| `task_name` | `node.yaml → task.name`（可选，回退到 `name`） | `"Business Analysis"` |
| `task.role_supplement` | `node.yaml → task.role_supplement` | `""` |

#### 扩展后的 node.yaml schema 示例（以 analyst 为例）

```yaml
# analyst/node.yaml - 扩展后
node_id: analyst
name: Analyst
description: Data Analyst & Business Intelligence Specialist
sequence: 1
deliverable_type: analyst-report
task:
  name: "Business Intelligence Analysis"   # 新增（可选，回退到 name）
  role_supplement: ""                       # 新增（已有但为空）
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations
  output_filename: "analyst-report.md"      # 新增
  format_hints: {}                          # 新增（可选）
agent:
  type: independent
  model: sonnet
  temperature: 0.7
```

---

## 5. 迁移实施步骤

### 5.1 阶段概览

```
阶段1: 扩展 node.yaml schema（0 风险）
  ↓
阶段2: 修改 context_builder.py（读取新字段）
  ↓
阶段3: 精简 NodeExecutionContext（移除 Task 字段）
  ↓
阶段4: 更新所有消费者模块
  ↓
阶段5: 删除 contracts.py 中的冗余类
```

### 5.2 阶段1：扩展 node.yaml schema（添加 Task 独有字段）

**目标文件**：所有 5 个节点的 `node.yaml`  
**风险**：无（只新增字段，不修改现有字段）

**修改示例（analyst/node.yaml）**：

```yaml
# Before
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    ...

# After
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    ...
  output_filename: "analyst-report.md"   # 新增
  format_hints: {}                        # 新增（空，保留扩展性）
task:
  role_supplement: ""                     # 显式声明（原来由代码 fallback ""）
```

**受影响文件**：5 个 `node.yaml` 文件  
**测试要求**：无需修改任何测试，因为现有逻辑已兼容额外字段

### 5.3 阶段2：修改 NodeExecutionContextBuilder 读取 node.yaml

**目标文件**：`autoBMAD/docuswarm/node_execution/context_builder.py`

**修改前**：

```python
def build(self, pipeline_id, node_id, original_context, ...) -> NodeExecutionContext:
    node_config = self.loader.load(node_id)
    deliverable_reqs = self._build_deliverable_requirements(node_config)
    return NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=node_id,
        node_name=node_config.name,
        node_order=node_config.sequence,
        task_name=node_config.task.get("name", node_config.name),          # ← 移除
        task_description=node_config.description or ...,                    # ← 移除
        role_supplement=node_config.task.get("role_supplement", ""),       # ← 移除
        deliverable_type=node_config.deliverable_type,                      # ← 移除
        deliverable_requirements=deliverable_reqs,                          # ← 移除
        original_context=original_context,
        chained_deliverables=chained_deliverables or [],
        shared_context=shared_context or {},
        iteration_feedback=iteration_feedback,
        docs_context=[],
        evaluator_criteria=node_config.evaluator.get("criteria", []),       # ← 移除
    )
```

**修改后**：

```python
def build(self, pipeline_id, node_id, original_context, ...) -> NodeExecutionContext:
    node_config = self.loader.load(node_id)
    return NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=node_id,
        node_name=node_config.name,
        node_order=node_config.sequence,
        original_context=original_context,
        chained_deliverables=chained_deliverables or [],
        shared_context=shared_context or {},
        iteration_feedback=iteration_feedback,
        docs_context=[],
    )
```

**影响分析**：

- `_build_deliverable_requirements()` 方法可删除（或保留供外部调用）
- `node_config.evaluator.get("criteria", [])` 的读取移至 `ContextManager.build_evaluator_input()`

### 5.4 阶段3：更新 contracts.py 中的 NodeExecutionContext 定义

**目标文件**：`autoBMAD/docuswarm/node_execution/contracts.py`

**修改前**：

```python
class NodeExecutionContextRequired(TypedDict):
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    task_name: str              # ← 移除
    task_description: str       # ← 移除
    role_supplement: str        # ← 移除
    deliverable_type: str       # ← 移除
    deliverable_requirements: DeliverableRequirements  # ← 移除
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]
    iteration_feedback: dict[str, Any] | None
    docs_context: list[dict[str, Any]]

class NodeExecutionContext(NodeExecutionContextRequired, total=False):
    evaluator_criteria: list[dict[str, Any]]  # ← 移除
```

**修改后**：

```python
class NodeExecutionContext(TypedDict):
    """精简统一节点执行上下文 - 仅包含运行时动态字段。
    
    静态配置（task, deliverable, evaluator_criteria）通过 node_id 
    由各消费端直接从配置文件加载，不再通过此协议传递。
    """
    # === 身份标识 ===
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int

    # === 运行时上下文数据 ===
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]

    # === 迭代状态 ===
    iteration_feedback: dict[str, Any] | None

    # === 扩展上下文 ===
    docs_context: list[dict[str, Any]]
```

### 5.5 阶段4：更新所有消费者模块

#### 5.5.1 context/isolation.py

**修改 `build_independent_input`**（当前从 `execution_context` 读取 task 字段，改为从 NodeConfig 读取）：

```python
# Before（从 execution_context 读取）
return IndependentAgentInput(
    task_name=execution_context["task_name"],
    task_description=execution_context["task_description"],
    role_supplement=execution_context["role_supplement"],
    deliverable_requirements=execution_context["deliverable_requirements"],
    ...
)

# After（从 NodeLoader 读取）
from autoBMAD.docuswarm.nodes.loader import NodeLoader
node_config = NodeLoader().load(execution_context["node_id"])
deliverable_reqs = _build_deliverable_requirements(node_config)

return IndependentAgentInput(
    task_name=node_config.task.get("name", node_config.name),
    task_description=node_config.description or "",
    role_supplement=node_config.task.get("role_supplement", ""),
    deliverable_requirements=deliverable_reqs,
    ...
)
```

**修改 `build_evaluator_input`**（criteria 从 evaluator.yaml 读取）：

```python
# Before
criteria=execution_context.get("evaluator_criteria", []),

# After
from autoBMAD.docuswarm.nodes.loader import NodeLoader
node_config = NodeLoader().load(execution_context["node_id"])
evaluator_criteria = node_config.evaluator.get("criteria", [])

criteria=evaluator_criteria,
```

#### 5.5.2 nodes/dual_agent.py

`execute_with_context()` 中访问 `execution_context["task_name"]` 的 3 处需要修改为从 node_config 读取：

```python
# Before（第 368, 395 行）
task_name=execution_context["task_name"],
"task_name": execution_context["task_name"],

# After
node_config = self._loader.load(self.node_id)
task_name = node_config.task.get("name", node_config.name)
task_name=task_name,
"task_name": task_name,
```

#### 5.5.3 node_execution/executor.py

第 128 行的 `task_name=execution_context["task_name"]`（日志记录）：

```python
# Before（日志）
task_name=execution_context["task_name"],

# After
task_name=execution_context["node_name"],  # 用 node_name 代替 task_name 用于日志
```

#### 5.5.4 prompts/contract_builder.py

`_build_task_section()` 已经使用 `.get()` 安全访问，但仍需从 node.yaml 读取：

```python
# Before
task_name = context.get("task_name") or context.get("node_name", "未知任务")
task_description = context.get("task_description") or context.get("description", "")
role_supplement = context.get("role_supplement", "")

# After
from autoBMAD.docuswarm.nodes.loader import NodeLoader
node_config = NodeLoader().load(context["node_id"])
task_name = node_config.task.get("name", node_config.name)
task_description = node_config.description or ""
role_supplement = node_config.task.get("role_supplement", "")
```

### 5.6 阶段5：删除 contracts.py 中的冗余 TypedDict

**可以删除的类**：
- `NodeExecutionContextRequired`（合并到 `NodeExecutionContext` 后不再需要）
- `DeliverableRequirements`（内联为普通 dict，或移至 `node.yaml` loader）

**必须保留的类**：
- `DeliverableArtifact`（运行时产物，仍需要）
- `IndependentAgentInput`（仍作为中间传递结构，可保留或简化）
- `EvaluatorAgentInput`（仍作为中间传递结构，可保留或简化）
- `IndependentOutput`、`EvaluatorOutput`（类型别名，保留）

---

## 6. 向后兼容策略

### 6.1 过渡期的双读机制

为确保迁移期间不破坏现有功能，建议在 `context/isolation.py` 中使用双读模式：

```python
def _get_task_name(execution_context: NodeExecutionContext, node_config: NodeConfig) -> str:
    """双读机制：优先从 node_config 读取，降级到 execution_context 字段。
    
    过渡期保证：移除 task_name 字段前，现有调用仍可正常工作。
    """
    # 优先从 node_config（新路径）
    if hasattr(node_config, 'task') and node_config.task:
        return node_config.task.get("name", node_config.name)
    
    # 降级到 execution_context（旧路径，向后兼容）
    task_name = execution_context.get("task_name")  # type: ignore[call-overload]
    if task_name:
        return task_name
    
    # 最终回退
    return execution_context.get("node_name", "Unknown")
```

### 6.2 配置迁移脚本设计

提供自动化脚本将现有 `node.yaml` 文件迁移到新 schema：

```python
# scripts/migrate_node_yaml.py
import yaml
from pathlib import Path

NODES_DIR = Path("autoBMAD/nodes")

def migrate_node_yaml(node_dir: Path) -> None:
    """迁移单个节点的 node.yaml 到新 schema。"""
    yaml_path = node_dir / "node.yaml"
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    
    # 添加 task 字段（如果不存在）
    if "task" not in config:
        config["task"] = {
            "name": config.get("name", ""),
            "role_supplement": ""
        }
    
    # 添加 deliverable 扩展字段
    if "deliverable" in config:
        deliverable = config["deliverable"]
        if "output_filename" not in deliverable:
            node_id = config.get("node_id", "node")
            deliverable_type = config.get("deliverable_type", "output")
            deliverable["output_filename"] = f"{node_id}-{deliverable_type}.md"
        if "format_hints" not in deliverable:
            deliverable["format_hints"] = {}
    
    with open(yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"[MIGRATED] {yaml_path}")

if __name__ == "__main__":
    for node_dir in NODES_DIR.iterdir():
        if node_dir.is_dir() and (node_dir / "node.yaml").exists():
            migrate_node_yaml(node_dir)
```

### 6.3 版本标记方案

在 `contracts.py` 中为即将废弃的字段添加 `# DEPRECATED` 注释，提供清晰的迁移路径：

```python
class NodeExecutionContextRequired(TypedDict):
    # === 身份标识 ===（保留）
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    
    # === 任务契约 ===（DEPRECATED: 迁移至 node.yaml，见 #4 重构报告）
    task_name: str        # DEPRECATED: use NodeLoader().load(node_id).task["name"]
    task_description: str # DEPRECATED: use NodeLoader().load(node_id).description
    role_supplement: str  # DEPRECATED: use NodeLoader().load(node_id).task["role_supplement"]
    
    # === 交付物契约 ===（DEPRECATED）
    deliverable_type: str              # DEPRECATED: use NodeLoader().load(node_id).deliverable_type
    deliverable_requirements: ...      # DEPRECATED: use NodeLoader().load(node_id).deliverable
    
    # ...（运行时字段保留）
```

---

## 7. 风险评估

### 7.1 数据丢失风险

| 风险点 | 级别 | 说明 | 缓解措施 |
|--------|------|------|---------|
| `task_name` 字段消失 | **低** | 仅用于日志和 prompt 标题，可用 `node_name` 替代 | 双读机制 + 单测覆盖 |
| `role_supplement` 为空 | **低** | 当前所有节点的 `role_supplement` 均为空字符串 | 迁移脚本自动添加 |
| `format_hints` 丢失 | **低** | 当前所有节点的 `format_hints` 均为空 dict | 迁移脚本自动添加 |
| `output_filename` 丢失 | **低** | 当前未被代码使用（`DeliverableRequirements` 中存在但未消费） | 迁移脚本补充 |
| `evaluator_criteria` 加载失败 | **中** | 若 `evaluator.yaml` 路径变化会导致评估无标准 | 添加 fallback 空列表 + 日志告警 |

**数据丢失风险总结**：**低**。所有"契约独有"字段（`output_filename`, `format_hints`, `role_supplement`）在当前系统中均为空值或未被消费，迁移后不会丢失任何有效数据。

### 7.2 运行时兼容性

| 场景 | 风险 | 说明 |
|------|------|------|
| 现有 pipeline 执行 | **低** | 执行路径为 `executor.py → context_builder → dual_agent → agents`，均在修改范围内 |
| LangGraph 状态机 | **低** | `NodeExecutionContext` 不进入 LangGraph state，仅在单次 node 执行中使用 |
| 测试套件 | **中** | 测试中可能硬编码 `task_name` 等字段的断言，需更新 |
| 序列化/反序列化 | **低** | `NodeExecutionContext` 不持久化，仅在内存中传递 |

### 7.3 测试影响

诊断工具扫描的受影响文件及测试风险：

| 测试文件（预期） | 涉及契约 | 修改必要性 |
|-----------------|---------|-----------|
| `tests/unit/test_context_builder.py` | `NodeExecutionContext` 字段断言 | **必须修改** |
| `tests/unit/test_isolation.py` | `IndependentAgentInput` 字段断言 | **必须修改** |
| `tests/unit/test_dual_agent.py` | `execution_context["task_name"]` 访问 | **必须修改** |
| `tests/unit/test_contract_builder.py` | `NodeExecutionContext` 类型注解 | **需审查** |
| `tests/integration/` | 端到端测试 | **需回归测试** |

### 7.4 移除可行性总结

综合诊断工具的评估结果：

| 契约类 | 移除可行性 | 优先级 |
|--------|-----------|--------|
| `IndependentAgentInput` 的 `persona_context` 字段 | **HIGH** | P0（立即可行） |
| `NodeExecutionContext.evaluator_criteria` | **HIGH** | P1（evaluator.yaml 已完备） |
| `NodeExecutionContext.task_*` 字段组 | **MEDIUM** | P2（需更新消费端） |
| `DeliverableRequirements` 类 | **MEDIUM** | P3（部分字段需迁移） |
| `NodeExecutionContextRequired` 类 | **LOW** | P4（是核心协议，仅精简字段） |

---

## 8. 结论与建议

### 8.1 实施建议

建议按以下优先级分批实施：

**第一批（P0，立即可行，风险极低）**：
1. 删除 `IndependentAgentInput.persona_context` 字段（当前值永远为 `{}`）
2. 将 `evaluator_criteria` 从 `NodeExecutionContext` 中移除，改为 `ContextManager.build_evaluator_input()` 直接从 `evaluator.yaml` 加载

**第二批（P1，需 1-2 天，风险低）**：
3. 运行迁移脚本为所有 `node.yaml` 补充 `output_filename`, `format_hints` 字段
4. 将 `NodeExecutionContext` 中的 `task_*` 字段标记为 `DEPRECATED`
5. 修改消费端（`isolation.py`, `contract_builder.py`）使用双读机制

**第三批（P2，需 3-5 天，需完整测试）**：
6. 从 `NodeExecutionContext` 中完全移除 `task_*` 字段
7. 删除 `NodeExecutionContextRequired` 基类，合并为单一 `NodeExecutionContext`
8. 更新所有相关测试
9. 删除 `DeliverableRequirements` 类（内联为普通 dict 类型注解）

### 8.2 预期收益量化

| 指标 | 当前 | 目标 | 改进幅度 |
|------|------|------|---------|
| `NodeExecutionContext` 字段数 | 16 | 9 | -44% |
| contracts.py 代码行数 | 125 | ~60 | -52% |
| 修改节点配置时需同步修改的文件数 | 3 | 1 | -67% |
| persona/node.yaml 与契约的字段重复率 | 0%（诊断工具报告无直接名称重叠） | 0% | 维持 |
| 语义等价字段数 | 6 | 0 | -100% |

---

*报告结束。总行数：约 420 行。*
