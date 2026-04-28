# BMM NodeExecutor 重构研究报告 Part 4: 节点功能精简与移除方案

**文档编号**: BMM-Research-04
**日期**: 2026-03-02
**范围**: 识别并移除不必要功能，精简节点执行链路
**修订**: v2 - 确保功能精简后 `autoBMAD/docuswarm` 运行时零外部依赖

---

## 0. 核心约束

> **`autoBMAD/docuswarm` 运行时绝不引用 `_bmad` 或任何外部文件夹。**
>
> 功能精简必须同时修复已有的 `_bmad` 路径引用违规，并确保新设计不引入外部依赖。

---

## 1. 已有 `_bmad` 依赖违规（必须优先修复）

### 1.1 templates/*.yaml 中的外部路径引用

**5个文件均包含违规引用**:

| 文件 | 行号 | 违规内容 |
|------|------|----------|
| `autoBMAD/docuswarm/templates/analyst_templates.yaml` | 62 | `style_guide: "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"` |
| `autoBMAD/docuswarm/templates/pm_templates.yaml` | 54 | 同上 |
| `autoBMAD/docuswarm/templates/ux_templates.yaml` | 67 | 同上 |
| `autoBMAD/docuswarm/templates/architect_templates.yaml` | 59 | 同上 |
| `autoBMAD/docuswarm/templates/po_templates.yaml` | 66 | 同上 |

**修复方案**:

| 方案 | 内容 | 推荐度 |
|------|------|--------|
| A. 删除字段 | 移除 `standards.style_guide` 字段 | 中（如果运行时不使用） |
| B. 内联标准 | 将文档标准内容内联到 `autoBMAD/` 内的公共配置 | 中 |
| C. 整体移除 | 移除 `autoBMAD/docuswarm/templates/` 整个目录 | **高（推荐）** |

**推荐方案C的理由**:
1. 这些模板配置（market_research, user_personas, api_specification等）与BMM workflow交付物不对齐
2. 重构后 `node.yaml.deliverable` 已包含 `required_sections`，templates/*.yaml 属于重复配置（DRY违反）
3. 没有代码实际使用这些模板配置来构建交付物

---

## 2. 功能移除优先级矩阵

| 优先级 | 目标 | 影响范围 | 风险 | 修复 _bmad 依赖 |
|--------|------|----------|------|----------------|
| **P0-Critical** | 修复 templates/*.yaml 中 `_bmad` 引用 | 5个yaml文件 | 低 | **是** |
| **P0-Critical** | 废弃executor函数移除 | pipeline/graph.py | 低 | 否 |
| **P0-Critical** | 预定义questions配置移除 | loader.py + node.yaml | 低 | 否 |
| **P1-High** | dependencies配置移除 | loader.py + node.yaml | 低 | 否 |
| **P1-High** | dual_agent.py 中冗余executor移除 | dual_agent.py | 中 | 否 |
| **P2-Medium** | templates/*.yaml 整体评估移除 | templates/ 目录 | 中 | **是** |
| **P3-Low** | MockNodeExecutor对齐 | pipeline/graph.py | 低 | 否 |

---

## 3. P0-Critical: 废弃函数移除

### 3.1 `_create_default_node_executor()` - pipeline/graph.py

**现状**: 已标记 `@deprecated`（Story 11.6, Feb 2026），产生空 `{}` 交付物。

**调用路径**:
```
create_pipeline_graph(session_manager=None)
  → 回退到 _create_default_node_executor  # 产生空交付物
```

**移除方案**:
- 删除 `_create_default_node_executor()` 函数体（约100行）
- `create_pipeline_graph()` 的 `session_manager` 改为必需参数
- 删除 `session_manager=None` 时的回退逻辑

### 3.2 `create_enhanced_node_executor()` - pipeline/graph.py

**现状**: 
```python
def create_enhanced_node_executor(node_id):
    return _create_default_node_executor(node_id, None)  # 调用deprecated函数
```

**移除方案**: 直接删除。搜索确认无外部调用。

### 3.3 预定义 questions 配置

**当前**: `node.yaml` 中每个节点定义3-4个预定义问题。

**问题**:
- 自动化管道中，问题由IndependentAgent在运行时动态生成
- 预定义问题被 `NodeLoader.load()` 解析后无任何消费者
- `_validate()` 要求 `questions` 必须存在（即使无用）

**移除清单**:

| 文件 | 变更 |
|------|------|
| `loader.py` | 删除 `NodeQuestionConfig` dataclass |
| `loader.py` | 删除 `NodeQuestionsConfig` dataclass |
| `loader.py` | 从 `NodeConfig` 删除 `questions` 字段 |
| `loader.py` | 从 `_validate()` 删除 questions 验证 |
| `loader.py` | 从 `_build_node_config()` 删除 questions 构建 |
| `nodes/*/node.yaml` | 删除所有 `questions:` 配置块 |

---

## 4. P1-High: dependencies 配置移除

**当前**: `node.yaml` 中每个节点定义 `dependencies: []` 或 `dependencies: [analyst, pm, ...]`

**问题**:
- 管道依赖关系在 `pipeline/graph.py` 中通过 `graph.add_edge()` 硬编码
- `NodeDependenciesConfig` 被解析后无任何消费者
- 两处定义同一信息 = DRY违反

**移除清单**:

| 文件 | 变更 |
|------|------|
| `loader.py` | 删除 `NodeDependenciesConfig` dataclass |
| `loader.py` | 从 `NodeConfig` 删除 `dependencies` 字段 |
| `loader.py` | 从 `_validate()` 删除 dependencies 验证 |
| `loader.py` | 从 `_build_node_config()` 删除 dependencies 构建 |
| `nodes/*/node.yaml` | 删除所有 `dependencies:` 配置块 |

---

## 5. P1-High: 执行链路简化

### 5.1 当前三层executor嵌套

```
create_pipeline_graph()                                      # 层0: 构建图
  → _create_integrated_node_executor(node_id, sm)            # 层1: pipeline/graph.py
    → node_execution.executor.create_node_executor(node_id, sm)  # 层2: node_execution/executor.py
      → DualAgentNode.execute()                               # 层3: nodes/dual_agent.py
```

### 5.2 dual_agent.py 中的冗余 create_node_executor

`dual_agent.py` 中存在一套与 `node_execution/executor.py` **功能重叠**的函数：

| dual_agent.py 函数 | executor.py 对应函数 | 区别 |
|--------------------|--------------------|------|
| `create_node_executor()` (line ~836) | `create_node_executor()` (line 34) | 操作PipelineState vs NodeRunState |
| `_execute_node()` (line ~871) | `_execute_node()` (line 75) | 同上 |
| `_get_config()` (line ~971) | `_get_config()` (line 267) | 完全相同 |

**当前使用**: pipeline/graph.py 通过 `_create_integrated_node_executor` 调用 `node_execution/executor.py` 版本。dual_agent.py 版本在 `__all__` 中导出但**无外部调用**。

**移除方案**:

| 文件 | 行号范围 | 代码 | 理由 |
|------|---------|------|------|
| `nodes/dual_agent.py` | ~836-868 | `create_node_executor()` | 无外部调用 |
| `nodes/dual_agent.py` | ~871-968 | `_execute_node()` | 无外部调用 |
| `nodes/dual_agent.py` | ~971-991 | `_get_config()` | 与executor.py重复 |
| `nodes/dual_agent.py` | `__all__` | 移除 `create_node_executor` 导出 | 配合删除 |

---

## 6. P2-Medium: templates/*.yaml 整体评估

### 6.1 当前 templates/*.yaml 分析

| 文件 | 模板ID | 与BMM对齐 |
|------|--------|-----------|
| analyst_templates.yaml | market_research, user_personas, risk_assessment | **不对齐** (BMM=product-brief) |
| pm_templates.yaml | prd, risk_assessment | **部分对齐** (有prd但sections不同) |
| ux_templates.yaml | user_personas, user_flows, wireframes, usability_testing | **不对齐** (BMM=ux-design-specification) |
| architect_templates.yaml | system_architecture, api_specification, database_schema | **不对齐** (BMM=architecture-decision) |
| po_templates.yaml | product_vision, roadmap, epic_list, story_list | **不对齐** (BMM=epics-stories) |

### 6.2 与 node.yaml.deliverable 的重复

重构后 `node.yaml` 的 `deliverable` 块已包含：
- `type`: 交付物类型
- `template_title`: 模板标题
- `required_sections`: section列表
- `output_filename`: 输出文件名

这与 `templates/*.yaml` 中的 `template_id`, `title`, `filename_pattern`, `sections` **完全重复**。

### 6.3 推荐处理

**方案C（推荐）: 整体移除 `autoBMAD/docuswarm/templates/` 目录**

理由：
1. 消除DRY违反（配置集中在 `node.yaml.deliverable`）
2. 消除 `_bmad` 外部路径引用违规
3. 当前无代码从这些模板配置实际生成文档
4. BMM交付物信息已嵌入 `node.yaml`

**前置检查**: 确认 `autoBMAD/docuswarm/` 中无代码 import 或加载这些yaml文件。

---

## 7. 完整移除清单

### 7.1 待删除代码

| 文件 | 行号范围 | 代码 | 理由 |
|------|---------|------|------|
| `pipeline/graph.py` | ~56-159 | `_create_default_node_executor()` | deprecated |
| `pipeline/graph.py` | ~473-489 | `create_enhanced_node_executor()` | 调用deprecated |
| `nodes/dual_agent.py` | ~836-868 | `create_node_executor()` | 无外部调用 |
| `nodes/dual_agent.py` | ~871-968 | `_execute_node()` | 无外部调用 |
| `nodes/dual_agent.py` | ~971-991 | `_get_config()` | 与executor.py重复 |
| `nodes/loader.py` | dataclass | `NodeQuestionConfig` | 自动化不使用 |
| `nodes/loader.py` | dataclass | `NodeQuestionsConfig` | 自动化不使用 |
| `nodes/loader.py` | dataclass | `NodeDependenciesConfig` | graph边管理 |

### 7.2 待修改代码

| 文件 | 变更 | 理由 |
|------|------|------|
| `nodes/loader.py` | NodeConfig删除questions/dependencies字段 | 无消费者 |
| `nodes/loader.py` | _validate()删除questions/dependencies验证 | 配合删除 |
| `nodes/loader.py` | _build_node_config()删除questions/dependencies | 配合删除 |
| `nodes/loader.py` | 新增NodeTaskConfig加载 | Part 1方案 |
| `pipeline/graph.py` | session_manager改为必需参数 | 删除回退路径 |
| `pipeline/graph.py` | `__all__`清理导出 | 删除deprecated引用 |
| `nodes/dual_agent.py` | `__all__`移除`create_node_executor` | 删除冗余导出 |

### 7.3 待修改配置文件

| 文件 | 变更 |
|------|------|
| `nodes/analyst/node.yaml` | 删除questions, dependencies; 新增task块; 对齐deliverable |
| `nodes/pm/node.yaml` | 同上 |
| `nodes/ux/node.yaml` | 同上 |
| `nodes/architect/node.yaml` | 同上 |
| `nodes/po/node.yaml` | 同上 |
| `nodes/analyst/persona.json` | 预处理嵌入BMM analyst.md角色上下文 |
| `nodes/pm/persona.json` | 预处理嵌入BMM pm.md角色上下文 |
| `nodes/ux/persona.json` | 预处理嵌入BMM ux-designer.md角色上下文 |
| `nodes/architect/persona.json` | 预处理嵌入BMM architect.md角色上下文 |
| `nodes/po/persona.json` | 预处理嵌入BMM pm.md角色上下文（名称PO） |

### 7.4 待删除/修复的外部依赖

| 文件 | 变更 | 类型 |
|------|------|------|
| `templates/analyst_templates.yaml` | 删除整个文件（方案C）或移除style_guide | 修复 _bmad 违规 |
| `templates/pm_templates.yaml` | 同上 | 修复 _bmad 违规 |
| `templates/ux_templates.yaml` | 同上 | 修复 _bmad 违规 |
| `templates/architect_templates.yaml` | 同上 | 修复 _bmad 违规 |
| `templates/po_templates.yaml` | 同上 | 修复 _bmad 违规 |

---

## 8. 代码量影响估算

| 类型 | 行数 | 说明 |
|------|------|------|
| **删除Python代码** | ~250行 | deprecated函数 + 冗余executor + 冗余dataclass |
| **删除YAML配置** | ~330行 | 5个templates/*.yaml（如采用方案C） |
| **新增Python代码** | ~80行 | NodeTaskConfig + NodeLoader扩展 + Persona扩展 |
| **修改Python代码** | ~60行 | NodeConfig字段 + _validate() + _format_system_prompt() |
| **修改YAML/JSON** | ~150行 | 5个node.yaml + 5个persona.json |
| **净减少** | **~290行** | 整体代码精简 |

---

## 9. 实施顺序

```
Phase 1 (P0): 安全移除 + 外部依赖修复
  ├── 1.1 修复/移除 templates/*.yaml 中 _bmad 引用 ⚠️ 外部依赖修复
  ├── 1.2 删除 _create_default_node_executor + create_enhanced_node_executor
  ├── 1.3 session_manager 改为必需参数
  ├── 1.4 删除 NodeQuestionConfig/NodeQuestionsConfig/NodeDependenciesConfig
  └── 1.5 更新 node.yaml 删除 questions/dependencies

Phase 2 (P1): 配置对齐（预处理嵌入BMM内容）
  ├── 2.1 重写5个 persona.json（嵌入BMM角色上下文）
  ├── 2.2 重构5个 node.yaml（新增task块 + 对齐deliverable）
  ├── 2.3 NodeLoader新增NodeTaskConfig加载
  └── 2.4 NodeConfig新增task字段

Phase 3 (P1): 执行链路精简
  ├── 3.1 删除 dual_agent.py 中冗余 create_node_executor/_execute_node/_get_config
  ├── 3.2 简化 _create_integrated_node_executor
  └── 3.3 NodeConfig实际传递给 DualAgentNode

Phase 4 (P1): System Prompt 重构
  ├── 4.1 Persona dataclass 新增 communication_style
  ├── 4.2 IndependentAgent._format_system_prompt() 使用BMM角色上下文+task说明
  ├── 4.3 模板结构信息传递到prompt
  └── 4.4 evaluator.yaml 描述微调

Phase 5 (P2): 交付物系统清理
  ├── 5.1 评估并移除 templates/ 目录（方案C）
  ├── 5.2 MockNodeExecutor 对齐BMM交付物
  └── 5.3 确认无遗留 _bmad 引用

Phase 6: 验证
  ├── 6.1 外部依赖扫描 (grep -r "_bmad" autoBMAD/)
  ├── 6.2 单元测试更新（NodeLoader、PersonaLoader）
  ├── 6.3 集成测试（双代理流程端到端）
  └── 6.4 质量门控（basedpyright + ruff）
```

### 依赖关系

```
Phase 1 ──→ Phase 2 ──→ Phase 3
              │            │
              ↓            ↓
           Phase 4 ──→ Phase 5 ──→ Phase 6
```

- **Phase 1 必须首先执行**（修复 _bmad 外部依赖违规 + 安全移除deprecated代码）
- Phase 2-4 可部分并行
- **Phase 6.1 是关键验证**: 扫描确认 `autoBMAD/` 目录内零 `_bmad` 引用

---

## 10. 验证检查清单

重构完成后的最终验证：

```bash
# 1. 外部依赖扫描（应返回0结果）
grep -r "_bmad" autoBMAD/ --include="*.py" --include="*.yaml" --include="*.json"

# 2. 类型检查
basedpyright autoBMAD/docuswarm/

# 3. 代码风格
ruff check --fix autoBMAD/docuswarm/

# 4. 测试
pytest tests/ -v --tb=short

# 5. 确认NodeLoader不加载_bmad路径
grep -r "bmm" autoBMAD/docuswarm/ --include="*.py"  # 应无运行时路径引用
```


---

## 7. 解决方案文档

本文档的研究结果（废弃代码移除、功能精简）已转化为测试驱动的实施方案：

| 方案文档 | 内容 | 位置 |
|----------|------|------|
| **TDD-BMM-03** | 废弃代码移除与功能精简 | [`docs/solution/TDD-BMM-03-Deprecated-Code-Removal.md`](../solution/TDD-BMM-03-Deprecated-Code-Removal.md) |
| **TDD-BMM-05** | BMM NodeExecutor 重构主实施指南 | [`docs/solution/TDD-BMM-05-Master-Implementation-Guide.md`](../solution/TDD-BMM-05-Master-Implementation-Guide.md) |

**移除组件清单**:
- `templates/*.yaml` - DRY violation, `_bmad` references
- `_create_default_node_executor()` - Created empty deliverables
- `NodeQuestionConfig`, `NodeQuestionsConfig`, `NodeDependenciesConfig` - Unused
- `node.yaml.description` - Redundant with task
- `node.yaml.questions`, `node.yaml.dependencies` - Not used in automation

**架构文档更新**:
- [`docs/architecture/01_SYSTEM_ARCHITECTURE.md`](../architecture/01_SYSTEM_ARCHITECTURE.md) - 系统架构 (v3.0)
- [`docs/architecture/03_PIPELINE_ARCHITECTURE.md`](../architecture/03_PIPELINE_ARCHITECTURE.md) - 节点执行架构 (v2.3)

---

**文档结束**
