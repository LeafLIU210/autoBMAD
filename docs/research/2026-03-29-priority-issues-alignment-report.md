# DocuSwarm 优先级问题文档对齐报告

**报告日期**: 2026-03-29  
**基于方案**: `docs/solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md`  
**关联研究**: `docs/research/2026-03-28-docuswarm-priority-issues-deep-research.md`  

---

## 执行摘要

本报告记录了基于测试驱动修复方案对 DocuSwarm 文档体系进行的系统性对齐更新。

| 问题 | 优先级 | 文档更新范围 | 状态 |
|------|--------|-------------|------|
| F1: 交付物契约传递 | P0 | 系统架构、Agent架构 | ✅ 已对齐 |
| F2: BMAD技能注入 | P0 | Agent架构 | ✅ 已对齐 |
| F3: 阈值读取修复 | P0 | Agent架构 | ✅ 已对齐 |
| F4: ContextValidator统一 | P1 | 上下文隔离架构 | ✅ 已对齐 |
| F5: 检查器语义增强 | P1 | 设计约束 | ✅ 已对齐 |
| F6: SessionManager清理 | P2 | 设计约束 | ✅ 已对齐 |

---

## 详细更新记录

### 1. docs/architecture/01_SYSTEM_ARCHITECTURE.md

**更新位置**: 文档末尾 Alignment Notice

**新增内容**:
```markdown
> **2026-03-29 Priority Issues Fix Update**: 基于 `../research/2026-03-28-docuswarm-priority-issues-deep-research.md` 的6个关键问题已制定测试驱动修复方案：
> - **F1 (P0)**: 交付物契约传递修复 - `NodeExecutionContext` 现在正确传递 `deliverable_requirements` 和 `deliverable_type`
> - **F2 (P0)**: BMAD 技能注入修复 - 主执行链统一使用 `PromptTemplateEngine` 注入技能
> - **F3 (P0)**: 阈值读取修复 - `CriteriaLoader` 优先读取 v2 `threshold`（单数）配置
> - **F4 (P1)**: ContextValidator 统一 - 全仓统一使用 `ContextValidator.get_instance()` 单例
> - **F5 (P1)**: 检查器语义验证增强 - `node_config_completeness_checker` 新增跨文件语义一致性检测
> - **F6 (P2)**: SessionManager 清理 - 删除未定义的 `allowed_dirs` 属性
> - 实施详情参考 `../solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md`
```

**对齐原因**: 系统架构文档作为顶层架构描述，需要记录所有 P0/P1/P2 级别的关键修复。

---

### 2. docs/architecture/02_AGENT_ARCHITECTURE.md

#### 更新 2.1: 文档末尾 Alignment Notice

**新增内容**:
```markdown
> **2026-03-29 Priority Issues Fix Update**: Agent 层关键修复已对齐：
> - **F1 (P0)**: `IndependentAgent.execute_with_input()` 现在正确传递 `deliverable_requirements` 到 `NodeExecutionContext`，确保交付物要求进入最终提示词
> - **F2 (P0)**: 主执行链已统一使用 `PromptTemplateEngine` 替代 `contract_builder`，BMAD 技能（来自 `.claude/skills/`）正确注入系统提示词
> - **F3 (P0)**: 评估阈值读取已修复，`CriteriaLoader` 优先读取 v2 `threshold`（单数）配置，与 `NodeLoader` 保持一致
> - **F4 (P1)**: `ContextValidator` 单例模式已统一，所有模块使用 `ContextValidator.get_instance()` 确保验证规则正确传播
> - 详细修复方案参考 `../solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md`
```

#### 更新 2.2: System Prompt Structure (F2 修复)

**修改章节**: 3.2 System Prompt Structure

**变更**: 从三层结构升级为四层架构

| 层级 | 之前 | 之后 |
|------|------|------|
| Layer 1 | (未明确) | Preset (`claude_code`) |
| Layer 2 | Persona | Persona (BMM Role Context) |
| Layer 3 | Task Assignment | **Skills** (BMAD 技能) |
| Layer 4 | Deliverable Requirements | Task & Deliverable Requirements |

**新增 NODE_SKILL_MAP 定义**:
```python
NODE_SKILL_MAP: Final[dict[str, list[str]]] = {
    "analyst": ["agent-analyst", "domain-research", "market-research", ...],
    "pm": ["agent-pm", "create-prd", "create-epics-and-stories", ...],
    "ux": ["agent-ux-designer", "create-ux-design", ...],
    "architect": ["agent-architect", "create-architecture", ...],
    "po": ["create-epics-and-stories", "validate-prd", ...],
}
```

**对齐原因**: F2 修复改变了 Agent 系统提示词的构建方式，架构文档必须反映这一变化。

#### 更新 2.3: Evaluation Criteria (F3 修复)

**修改章节**: 4.3 Evaluation Criteria

**新增内容**:
```markdown
> **2026-03-29 F3 Fix Update**: 阈值配置已统一为 v2 规范，使用单数形式 `threshold`：
> ```yaml
> # evaluator.yaml (v2 规范)
> threshold:
>   approval: 0.75      # 单数形式
>   escalation: 0.50
> ```
> `CriteriaLoader` 优先读取 `threshold`，无配置时回退到 `thresholds`（兼容性），最后使用默认值。
```

**对齐原因**: F3 修复统一了阈值配置的读取逻辑，架构文档需要说明 v2 规范。

---

### 3. docs/architecture/06_CONTEXT_ISOLATION.md

#### 更新 3.1: 文档末尾 Alignment Notice

**新增内容**:
```markdown
> **2026-03-29 F4 Fix Update**: `ContextValidator` 单例模式已统一：
> - 所有模块统一使用 `ContextValidator.get_instance()` 替代直接实例化
> - 涉及文件：`isolation.py`, `independent.py`, `evaluator.py`
> - NodeLoader 注册的验证规则现在正确流入实际执行
> - 详见 `../solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md` (F4)
```

#### 更新 3.2: 新增 ContextValidator Singleton Pattern 章节

**新增章节**: 第7节

**内容要点**:
1. **Singleton Usage Requirement**: 明确必须使用 `get_instance()`
2. **Rule Registration Flow**: 展示规则注册到消费的完整流程
3. **Migration Guide**: 列出所有需要修改的文件和行号

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| `isolation.py:286` | `self._validator = ContextValidator()` | `self._validator = ContextValidator.get_instance()` |
| `independent.py:430` | `validator = ContextValidator()` | `validator = ContextValidator.get_instance()` |
| `evaluator.py:433` | `validator = ContextValidator()` | `validator = ContextValidator.get_instance()` |

**对齐原因**: F4 修复涉及上下文隔离的核心组件，架构文档需要提供使用规范。

---

### 4. docs/design/README.md

#### 更新 4.1: 新增 2026-03-29 优先级问题修复设计约束章节

**新增内容**:

##### F5: 配置检查器语义验证增强 (P1)

**问题描述**: `node_config_completes_checker.py` 报告 100% 完整度，但存在跨文件语义不一致。

**新增设计约束**:

| 检查项 | 说明 | 影响 |
|--------|------|------|
| Sections 一致性 | `node.yaml:deliverable.required_sections` 必须与 `persona.json:output_format.sections` 一致 | 高 |
| 语义匹配分数 | 合规分数 = 交集大小 / 并集大小 | 中 |

**示例不一致检测** (architect 节点):
- node.yaml: 4 sections
- persona.json: 9 sections
- 匹配率: 30% ⚠️

##### F6: SessionManager 属性清理 (P2)

**问题描述**: `SessionManager.allowed_dirs` 属性访问未定义的 `_allowed_dirs`。

**设计变更**:
```python
# ❌ 已删除 (会导致 AttributeError)
@property
def allowed_dirs(self) -> list[str] | None:
    return self._file_dirs or self._allowed_dirs

# ✅ 使用替代属性
@property
def file_dirs(self) -> list[str] | None:
    return self._file_dirs
```

**对齐原因**: F5 和 F6 修复涉及设计和 API 层面的变更，需要在设计文档中记录约束。

---

## 文档对齐检查清单

| 文档 | F1 | F2 | F3 | F4 | F5 | F6 | 状态 |
|------|----|----|----|----|----|----|------|
| 01_SYSTEM_ARCHITECTURE.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ 已更新 |
| 02_AGENT_ARCHITECTURE.md | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ 已更新 |
| 06_CONTEXT_ISOLATION.md | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ 已更新 |
| design/README.md | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ 已更新 |

**说明**: 
- 每个文档只更新与其领域相关的问题
- Agent 架构聚焦 F1-F4（执行链相关）
- 上下文隔离聚焦 F4（验证器相关）
- 设计文档聚焦 F5-F6（检查器和 API 相关）

---

## 后续行动建议

1. **实施阶段**: 按照 `docs/solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md` 执行测试驱动修复
2. **文档同步**: 修复完成后，更新本文档中的状态标记
3. **回归测试**: 确保文档描述与实际代码实现一致

---

**报告结束**
