# F8: 文档层漂移与收敛深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm 文档层
> 核心问题: 文档层存在漂移与质量退化信号

---

## 1. 执行摘要

### 1.1 核心发现

文档层存在**历史债务**和**状态标记缺失**问题：

1. **docs/design.md** 和 **docs/architecture.md** 仍把中间态实现细节写成设计事实
2. **仓内历史研究文档** 大量描述旧决策（checkpoint 作为主恢复视角、ToolOk/ToolError 示例）
3. **缺乏"当前生效决策索引"**，读者容易被带回旧路径

### 1.2 关键代码证据

```markdown
# docs/design.md:448
shared_context={},  # ❌ 文档描述与代码一致，但都是问题状态

# docs/design.md:557-559
original_context={},
shared_context={},

# docs/architecture.md:3
> **Version**: 2.0 (Aligned with NodeExecutionContext Protocol)

# docs/architecture.md:13
1. **Single Context Protocol**: `NodeExecutionContext` is the unified contract...
```

---

## 2. 详细分析

### 2.1 文档漂移全景

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          文档层现状                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  设计文档 (docs/)                                                        │
│  ├── design.md                                                        │
│  │   ├── EvaluatorAgentInput 定义 (TypedDict)                         │
│  │   ├── ContextManager.build_evaluator_input()                       │
│  │   └── ❌ shared_context={} 代码示例（与问题实现一致）                  │
│  │                                    但未标注是问题                    │
│  ├── architecture.md                                                  │
│  │   ├── Version 2.0 (NodeExecutionContext Protocol)                  │
│  │   ├── NodeExecutionContext 详细定义                                 │
│  │   └── ❌ 未标记某些部分已过时或需修复                                │
│  └── (其他设计文档)                                                     │
│                                                                         │
│  历史研究文档 (docs/research/, autoBMAD/docuswarm/docs/)                │
│  ├── DocuSwarm-CLI-Research-Report.md                                 │
│  │   └── checkpoint_state = pipeline.get("state", {})                 │
│  │                                    ❌ 描述旧实现                      │
│  ├── DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md                    │
│  │   └── return ToolOk(output=...)                                    │
│  │                                    ❌ ToolOk 示例                     │
│  └── ... 更多历史文档                                                   │
│                                                                         │
│  缺少:                                                                   │
│  ├── 当前生效决策索引 (Decision Index)                                   │
│  ├── 历史文档 archived/superseded 标记                                  │
│  └── 文档与代码一致性检查机制                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 具体漂移案例

#### 2.2.1 design.md 中的问题代码示例

```markdown
# docs/design.md:520-531
```python
class EvaluatorAgentInput(TypedDict):
    task_name: str
    task_description: str
    original_context_summary: str  # P0-2: 原始需求摘要
    deliverable_artifact: dict[str, Any]  # 交付物元数据
    deliverable_body: str  # 交付物正文（从文件读取）
    criteria: list[dict[str, Any]]
```

**问题**: 文档本身正确，但引用这段文档的代码可能实现不正确（如 F3 发现的 EvaluatorAgent 置空 original_context）。

#### 2.2.2 architecture.md 的版本声明

```markdown
# docs/architecture.md:3
> **Version**: 2.0 (Aligned with NodeExecutionContext Protocol)
```

**问题**: 版本号声明了协议对齐，但未指明哪些部分仍在迁移中，哪些已稳定。

#### 2.2.3 历史研究文档的旧决策

```markdown
# autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md:269
checkpoint_state = pipeline.get("state", {})

# 同上:685
3. 从 `state_json` 解析 `completed_nodes`
```

**问题**: 描述的是 checkpoint 作为恢复依据的旧实现，与 F1 决策（state_json 为主真相源）不一致。

### 2.3 文档漂移影响

| 读者类型 | 影响 |
|----------|------|
| 新开发者 | 被旧决策误导，实现与当前决策不一致的代码 |
| 维护者 | 难以判断文档是否仍然有效 |
| 架构师 | 无法快速了解当前生效的设计决策 |
| 测试人员 | 基于过时文档编写无效测试 |

---

## 3. 收敛方案

### 3.1 建立"当前生效决策索引"

创建 `docs/DECISIONS.md` 作为单一真相源：

```markdown
# DocuSwarm 架构决策索引

> **版本**: 2026-03-17
> **状态**: 生效中

## 生效中的核心决策

### F1: 状态持久化
- **决策**: state_json 是唯一业务真相源
- **状态**: ✅ 生效
- **相关文档**: 
  - 实现: F1 研究报告
  - 代码: `storage/state_manager.py`, `pipeline/orchestrator.py`
- **废弃**: checkpoint 作为主恢复依据

### F2: Shared Context
- **决策**: shared_context 必须贯穿写入、提示词消费、恢复链路
- **状态**: ⚠️ 部分实现（写入✅，消费❌需修复）
- **相关文档**:
  - 实现: F2 研究报告
  - 代码: `agents/independent.py:681`

### F3: Evaluator 输入契约
- **决策**: Evaluator 直接消费 EvaluatorAgentInput，不重建缩水上下文
- **状态**: ⚠️ 需修复
- **相关文档**:
  - 实现: F3 研究报告
  - 代码: `agents/evaluator.py:571-573`

### F4: 工具层收敛
- **决策**: docs-free，只保留 3 个核心工具
- **状态**: ✅ 生效
- **相关文档**:
  - 实现: F4 研究报告
  - 配置: `agents/configs/independent_agent.yaml`

### F5: ToolResult 协议
- **决策**: 系统内部使用结构化 ToolResult，SDK 边界适配
- **状态**: ⚠️ 部分实现
- **相关文档**:
  - 实现: F5 研究报告
  - 代码: `tools/tool_result.py`, `tools/create_deliverable.py`

### F6: 测试体系
- **决策**: 重建测试体系，围绕当前决策
- **状态**: 🔄 进行中
- **相关文档**:
  - 实现: F6 研究报告

### F7: 类型系统
- **决策**: 收敛导出面，减少惰性导入
- **状态**: 🔄 待实施
- **相关文档**:
  - 实现: F7 研究报告

### F8: 文档收敛
- **决策**: 建立决策索引，标记历史文档
- **状态**: 🔄 进行中（本文档）
- **相关文档**:
  - 实现: F8 研究报告

---

## 历史决策

### ❌ 已废弃

| 决策 | 废弃原因 | 替代决策 |
|------|----------|----------|
| checkpoint 作为主恢复依据 | 业务语义不清 | F1: state_json 为主真相源 |
| ToolOk/ToolError 作为内部格式 | 绑定特定 SDK | F5: ToolResult 内部协议 |
| docs 工具 | 简化架构 | F4: docs-free |

### 📦 已归档

| 文档 | 状态 | 说明 |
|------|------|------|
| ... | ... | ... |
```

### 3.2 为历史文档增加状态标记

#### 3.2.1 标记格式

```markdown
# 文档头部标记

---
**文档状态**: 🗄️ 已归档 (Archived)
**归档日期**: 2026-03-17
**替代文档**: F1 研究报告 (2026-03-17-state-persistence-research-report.md)
**说明**: 本文档描述的 checkpoint 主恢复机制已废弃，参见 F1 决策
---

# 原内容...
```

#### 3.2.2 状态标记类型

| 标记 | 含义 | 使用场景 |
|------|------|----------|
| 🟢 现行 | 当前有效 | 最新设计文档 |
| 🟡 迁移中 | 正在过渡 | 部分实现的决策 |
| 🗄️ 已归档 | 历史参考 | 已废弃但保留的文档 |
| ❌ 已废弃 | 明确废弃 | 不应再参考的文档 |

### 3.3 更新核心设计文档

#### 3.3.1 docs/design.md 更新

```markdown
# DocuSwarm Design Document

> **版本**: 3.0 (Aligned with F1-F8 Decisions)
> **最后更新**: 2026-03-17

## 重要说明

本文档已根据 2026-03-17 F1-F8 深度决策研究更新。
历史版本参见归档文档。

## 架构决策索引

参见 [DECISIONS.md](./DECISIONS.md)

## 核心组件

### Pipeline State (F1)

**决策**: state_json 是唯一业务真相源

```python
class PipelineState(TypedDict):
    # 完整字段定义
    ...
```

**注意**: checkpoint 仅作为运行时恢复辅助

### Shared Context (F2)

**决策**: shared_context 贯穿写入、消费、恢复

**实现注意**: 
- ✅ 写入: `StateManager.update_shared_context()`
- ⚠️ 消费: 修复中，参见 F2 研究报告

### Evaluator Input (F3)

**决策**: EvaluatorAgentInput 直接消费，不重建

**实现注意**:
- ✅ 构建: `ContextManager.build_evaluator_input()`
- ⚠️ 消费: 修复中，参见 F3 研究报告

### Tools (F4)

**决策**: docs-free，3个核心工具

```yaml
tools:
  - create_deliverable
  - update_context  
  - create_document_set
```

### ToolResult (F5)

**决策**: 内部使用结构化 ToolResult

```python
@dataclass
class ToolResult:
    success: bool
    result: Any = None
    error: str | None = None
```

---

## 附录: 历史版本

- [v2.0 - 2026-02-XX](): 已归档
```

#### 3.3.2 docs/architecture.md 更新

```markdown
# DocuSwarm Architecture

> **版本**: 3.0 (Aligned with F1-F8 Decisions)
> **最后更新**: 2026-03-17

## 架构概览

### 状态管理 (F1)

```
┌─────────────────────────────────────┐
│           State Manager             │
│  ┌─────────────┐  ┌─────────────┐  │
│  │ state_json  │  │ checkpoint  │  │
│  │ (业务真相)   │  │ (运行辅助)   │  │
│  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────┘
```

### Context 流转 (F2, F3)

```
StateManager → ContextManager → AgentInput → Agent
                    ↓              ↓
              shared_context   original_context
```

### 工具层 (F4, F5)

```
┌─────────────────────────────────────┐
│           Tools Package             │
│  ┌─────────────────────────────┐   │
│  │   ToolResult (内部协议)      │   │
│  │  ┌─────┐ ┌─────┐ ┌────────┐│   │
│  │  │create│ │update│ │create ││   │
│  │  │_deliv│ │_ctx  │ │_docset││   │
│  │  └─────┘ └─────┘ └────────┘│   │
│  └─────────────────────────────┘   │
│           ↓ SDK Adapter            │
│      ToolOk / ToolError            │
└─────────────────────────────────────┘
```
```

### 3.4 文档质量门

建立文档评审检查清单：

```markdown
## 文档质量检查清单

### 新增/修改文档时检查

- [ ] 是否包含文档状态标记（现行/迁移中/已归档）
- [ ] 是否与当前代码实现一致
- [ ] 是否与 DECISIONS.md 一致
- [ ] 代码示例是否可运行
- [ ] 是否引用了相关研究报告

### 定期审计

- [ ] 所有设计文档是否都有状态标记
- [ ] 历史文档是否已归档
- [ ] 文档与代码差异清单
```

---

## 4. 测试建议（文档一致性）

### 4.1 文档-代码一致性检查

```python
def test_documented_fields_match_code():
    """验证文档描述的字段与代码一致."""
    # 解析 PipelineState 字段
    from autoBMAD.docuswarm.pipeline.state import PipelineState
    code_fields = set(PipelineState.__annotations__.keys())
    
    # 解析文档中的字段描述（需要文档结构化）
    doc_fields = parse_documentation_fields("docs/DECISIONS.md", "PipelineState")
    
    assert code_fields == doc_fields, f"Mismatch: {code_fields ^ doc_fields}"
```

### 4.2 决策索引完整性检查

```python
def test_decision_index_complete():
    """验证 DECISIONS.md 包含 F1-F8."""
    with open("docs/DECISIONS.md") as f:
        content = f.read()
    
    for i in range(1, 9):
        assert f"F{i}:" in content, f"Missing F{i} in DECISIONS.md"
```

---

## 5. 代码修改清单

### 5.1 新增文件

- [ ] `docs/DECISIONS.md` - 当前生效决策索引

### 5.2 修改文件

- [ ] `docs/design.md`
  - 添加状态标记
  - 更新与 F1-F5 一致的内容
  - 添加"历史版本"附录

- [ ] `docs/architecture.md`
  - 添加状态标记
  - 更新架构图与 F1-F5 一致
  - 添加"历史版本"附录

### 5.3 归档标记

- [ ] `autoBMAD/docuswarm/docs/*`
  - 添加 🗄️ 已归档标记
  - 指向替代的新文档

- [ ] `docs/research/*` (旧报告)
  - 添加 🗄️ 已归档标记
  - 指向 F1-F8 新报告

---

## 6. 结论

1. **文档是架构的重要组成部分**，需要与代码同步维护
2. **决策索引是文档层的核心**，提供单一真相源
3. **历史文档需要状态标记**，避免误导读者
4. **文档评审应该纳入质量门**，确保与代码和决策一致

---

## 附录: 文档状态标记示例

### 现行文档

```markdown
---
**文档状态**: 🟢 现行 (Current)
**最后更新**: 2026-03-17
**对应决策**: F1-F8
---
```

### 迁移中文档

```markdown
---
**文档状态**: 🟡 迁移中 (In Migration)
**开始迁移**: 2026-03-17
**预计完成**: 2026-03-31
**相关决策**: F2, F3
---
```

### 已归档文档

```markdown
---
**文档状态**: 🗄️ 已归档 (Archived)
**归档日期**: 2026-03-17
**替代文档**: docs/DECISIONS.md
**说明**: 本文档描述的实现已废弃
---
```
