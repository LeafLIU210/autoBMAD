# DocuSwarm 重构方案实施深度审查报告

**审查对象**
- 方案文档：`docs/research/refactor-2026-03-26/00-refactoring-roadmap.md` 及 01-05 子报告
- 实现范围：`autoBMAD/docuswarm`、`autoBMAD/nodes`

**审查日期**
- 2026-03-28

**审查方式**
- 静态代码审查
- 配置与调用链核对
- 目标性命令验证
- 尝试运行 `pytest`，但被测试装载错误阻断

---

## 关键立场声明

**本报告拒绝任何形式的向后兼容要求。**

重构方案的目标是将架构完成度从 70% 提升至 95%，而非维护历史包袱。所有"兼容别名"、"v1/v2 双读"、"渐进式迁移"等设计均与这一目标相悖。以下审查结论基于**不兼容迁移**的前提。

---

## 1. 执行结论

基于当前代码状态，我的结论是：

- `MemoryManager` 移除：**已完成**
- `ContextValidator` 提取：**已完成**
- Task 契约瘦身与单一运行时上下文：**已完成**
- 节点配置 v2 升级：**表层完成，运行时消费仍有缺口**
- Claude Agent SDK 增强：**文件已落地，但关键能力未真正接入主执行链**
- Phase 5 回归验证：**当前不能宣称完成**

如果按路线图的目标来衡量，这次重构的**"结构落地度"明显高于 2026-03-26 之前，但"端到端闭环完成度"仍不足以判定为 fully done**。更准确的判断是：

- **Phase 1 基本完成**
- **Phase 2 完成**
- **Phase 3 部分完成**
- **Phase 4 仅部分完成，且存在主链路未接线问题**
- **Phase 5 未完成**

---

## 2. 最高优先级发现

### Finding 1: 主执行链没有真正启用节点级 MCP 文件/搜索工具，T-G 只能算"代码存在"，不能算"能力生效"

**严重级别**：高

**为什么这是问题**

路线图 Phase 4/T-G 的核心目标不是"把 `tool_filter.py`、`file_tools.py`、`search_tools.py` 放进仓库"，而是让节点在真实运行时具备受控的文件读取/搜索能力。

当前主链路中：

- `IndependentAgent.execute_with_input()` 在真实节点执行路径下重新创建 `SessionManager`，但没有传入 `node_id` 和 `allowed_dirs`
  - `autoBMAD/docuswarm/agents/independent.py:678-682`
- `SessionManager` 只有在 `self._node_id and self._allowed_dirs` 同时存在时才会配置 `mcp_servers` 和 `allowed_tools`
  - `autoBMAD/docuswarm/llm/session_manager.py:157-158`
- 五个节点的 `node.yaml` 已经声明了 `tools` 权限
  - 例如 `autoBMAD/nodes/analyst/node.yaml:49-58`

这意味着：

- `NodeLoader` 已经能解析 `tools`
- `NodeToolFilter` 已经能生成 MCP 工具名和服务
- 但真实的 `execute_with_input()` 路径**没有把这些权限带进会话**
- 因此路线图声称的"文件工具/搜索工具集成"在主执行链上**没有闭环**

**影响**

- 节点无法按设计使用受控的 `read_document` / `list_documents` / `grep_search` / `glob_search`
- Phase 4 的"SDK 能力激活"结论会被高估
- 相关单测更像是在验证 `SessionManager`/`NodeToolFilter` 的孤立能力，而不是实际流水线接线

**补充观察**

即使后续把 `allowed_dirs` 传进来，`SessionManager` 目前仍用同一份 `allowed_dirs` 同时构造 file/search 权限：

- `autoBMAD/docuswarm/llm/session_manager.py:174-177`

这会抹平 `file_permissions.allowed_read_dirs` 与 `search_permissions.search_dirs` 的差异。以 analyst 为例，配置里：

- file 允许：`docs/`、`docs/research/`
- search 只允许：`docs/`
  - `autoBMAD/nodes/analyst/node.yaml:50-58`

但当前 `SessionManager` 的构造方式会把 search 权限放宽到和 file 权限一样。

---

### Finding 2: v2 `deliverable` 增强字段没有进入运行时对象，Schema v2 只是"写进 YAML"，不是"被系统消费"

**严重级别**：高

**为什么这是问题**

路线图明确把 `deliverable.template_title`、`deliverable.output_filename`、`deliverable.format_hints` 视为 v2 升级的一部分。

当前实现里：

- `architect/node.yaml` 已经写入了 `template_title` 和 `output_filename`
  - `autoBMAD/nodes/architect/node.yaml:22-29`
- 但 `NodeDeliverableConfig` 只定义了 `type`、`format`、`required_sections`
  - `autoBMAD/nodes/loader.py:60-64`
- `NodeLoader._build_node_config()` 也只把 `required_sections` 填入 `deliverable_config`
  - `autoBMAD/nodes/loader.py:379-383`
- `ContextManager.build_independent_input()` 只能通过 `hasattr(...)` 试探这些字段，失败后回退
  - `autoBMAD/docuswarm/context/isolation.py:141-161`
- `contract_builder` 虽然支持展示 `template_title` / `output_filename` / `format_hints`，但前提是这些字段已经进入 `deliverable_requirements`
  - `autoBMAD/docuswarm/prompts/contract_builder.py:177-205`

这形成了一个很典型的"配置写了，运行时没读"的断层：

- 文档层宣称 v2 已升级
- 配置文件层确实补了字段
- 运行时对象层并未承接
- Prompt/工具层拿不到这些值

**影响**

- `output_filename`、`template_title` 等 v2 承诺无法稳定传递到实际生成流程
- Phase 3/T-F 只能算"配置文件形式升级"，不能算"配置-代码真正对齐"

---

### Finding 3: 当前测试套件无法启动，Phase 5 的"已完成回归验证"没有证据支撑

**严重级别**：高

**证据**

我尝试执行：

```bash
python -m pytest tests/unit/llm/test_session_manager_mcp_integration.py -q
python -m pytest tests/unit/prompts/test_independent_agent_refactor.py -q
```

两次都在测试装载阶段失败，不是业务断言失败，而是：

- `tests/__init__.py:1` 内容为 `: DocuSwarm test suite.`
- 这是无效 Python 语法

对应文件：

- `tests/__init__.py:1`

**影响**

- 当前无法以 pytest 结果证明路线图中的 Phase 5 门禁已经通过
- "新增大量测试文件"不等于"测试资产可执行"
- 任何"重构已通过回归验证"的结论都需要保留

---

## 3. 重要发现：两项待明确的设计决策

以下两项需要实现负责人明确确认是"方案未完全落地"还是"设计已经调整但文档未更新"。

---

### Decision 1: 四层提示词架构是否使用 SDK preset/append 结构

**方案文档承诺**

报告 05 (T-H) 明确要求使用 Claude Agent SDK 的 `system_prompt` 高级结构：

```python
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",  # Layer 1
        "append": persona_prompt + task_context + skill_section  # Layer 2+3+4
    }
)
```

四层结构：
- Layer 1: `claude_code` preset（工具说明）
- Layer 2: Persona（角色身份）
- Layer 3: Task Context（任务上下文）
- Layer 4: Skill Injection（BMAD 技能）

**当前实现**

`SessionManager._create_options()` 直接将字符串赋给 `options.system_prompt`：

```python
# session_manager.py:276-278
options_dict["system_prompt"] = system_prompt  # 纯字符串，非 dict 结构
```

这导致：
1. 未使用 `claude_code` preset 的工具说明
2. system_prompt 和 user_prompt 未真正分离
3. 无法实现四层的清晰分层

**评估结论**

| 选项 | 建议 | 理由 |
|------|------|------|
| A. 按文档落地 preset/append | **暂不推荐** | 需要验证当前使用的 SDK 版本是否支持该结构；如不支持，需评估升级成本 |
| B. 放弃该设计，更新文档 | **当前可行** | 现有字符串拼接方式在功能上可等效实现，只需确保内容分层清晰即可 |

**建议行动**：
- 若确认当前 SDK 支持 `system_prompt` dict 结构，应在 T-H 阶段完成迁移
- 若 SDK 不支持或存在兼容问题，应更新报告 05 和路线图，明确采用字符串拼接方案，但保留内容分层约定

---

### Decision 2: `node.yaml` 是否保留 `evaluator` 内联/引用字段

**方案文档承诺**

报告 04 的 Schema v2 设计在 `node.yaml` 中新增 `evaluator` 内联引用段：

```yaml
evaluator:
  criteria_file: evaluator.yaml  # 引用外部文件
  threshold: 0.70
  max_iterations: 3
  model: sonnet
```

目的是将 evaluator 配置纳入 node.yaml 统一管理，同时通过 `criteria_file` 字段保留引用外部 evaluator.yaml 的灵活性。

**当前实现**

- 5 个节点的 `node.yaml` 均无 `evaluator` 字段
- `evaluator.yaml` 仍是独立文件，位于各节点目录下
- `NodeLoader` 直接固定加载 `evaluator.yaml`：
  ```python
  # loader.py:217-220
  evaluator_file = node_path / "evaluator.yaml"
  if evaluator_file.exists():
      evaluator_config = load_yaml(evaluator_file)
  ```

**评估结论**

| 选项 | 建议 | 理由 |
|------|------|------|
| A. 按文档落地内联/引用设计 | **暂不推荐** | 当前独立 `evaluator.yaml` 模式工作正常，迁移收益有限；且 `threshold`、`max_iterations` 已在 evaluator.yaml 中存在 |
| B. 放弃该设计，更新文档 | **推荐** | 独立文件模式更清晰，便于单独维护评估标准；应更新报告 04 和路线图，移除 `evaluator` 内联引用设计 |

**建议行动**：
- 更新 `04-node-configuration-reform.md`，移除 `node.yaml` 中 `evaluator` 字段的相关设计
- 更新 `00-refactoring-roadmap.md` Phase 3 章节，说明 evaluator 配置保持独立文件模式
- `NodeLoader` 继续按固定路径加载 `evaluator.yaml`，不再支持 `criteria_file` 引用字段

---

## 4. 分项实施状态评估

| 工作流 | 方案目标 | 当前状态 | 结论 |
|---|---|---|---|
| T-A MemoryManager 移除 | 删除死代码与导出 | `context/memory.py` 已不存在；源码树内无活引用 | 完成 |
| T-B/T-E Task 契约瘦身 | `NodeExecutionContext` 仅保留运行时字段；消费者从 NodeLoader 读 task | `contracts.py` 已缩减到 9 个运行时字段；`ContextManager`/`contract_builder` 已从 `NodeLoader` 读 `task` | 完成 |
| T-D ContextValidator 提取 | 验证逻辑统一到 `context/validator.py` | 主体已统一，orchestrator/isolation/output validation 已接入 | 完成 |
| T-C/T-F 节点配置改革 | 5 节点 v2 升级，配置-代码对齐 | 5 节点均为 v2，`task/runtime/tools/max_iterations/threshold` 已到位；但 deliverable 扩展字段未入运行时 | 部分完成 |
| T-G 文件/搜索工具接入 | 节点级 MCP 文件/搜索能力可用 | `tools/*`、`tool_filter.py`、`SessionManager` 支持存在，但主执行链未传 node 权限 | 部分完成，主链路未闭环 |
| T-H 四层提示词架构 | persona/task/skills 通过 system prompt 分层接入 | `PromptTemplateEngine`、`SkillInjector`、`_call_llm_with_prompts()` 已存在；但 preset/append 结构未使用 | 部分完成，需明确设计决策 |
| Phase 5 回归验证 | 端到端与回归测试通过 | `pytest` 当前无法启动 | 未完成 |

---

## 5. 已确认落地的部分

以下内容我认为已经有较强证据表明落地：

### 5.1 MemoryManager 清理

- `autoBMAD/docuswarm/context/memory.py` 已删除
- `context.__all__` 已无 `MemoryManager` / `MemoryScope`
  - `autoBMAD/docuswarm/context/__init__.py:25-39`
- 源码树中已查不到 `MemoryManager` / `MemoryScope` 活引用

### 5.2 NodeExecutionContext 运行时化

- `NodeExecutionContext` 当前仅保留：
  - `pipeline_id`
  - `node_id`
  - `node_name`
  - `node_order`
  - `original_context`
  - `chained_deliverables`
  - `shared_context`
  - `iteration_feedback`
  - `docs_context`
  - 见 `autoBMAD/docuswarm/node_execution/contracts.py:25-36`

### 5.3 任务信息已从配置源读取

- `ContextManager.build_independent_input()` 已改为读 `node_config.task`
  - `autoBMAD/docuswarm/context/isolation.py:166-175`
- `ContextManager.build_evaluator_input()` 已改为读 `node_config.task`
  - `autoBMAD/docuswarm/context/isolation.py:225-235`
- `NodePromptContractBuilder` 的 task section 已直接用 `NodeLoader.load(node_id)`
  - `autoBMAD/docuswarm/prompts/contract_builder.py:138-173`
  - `autoBMAD/docuswarm/prompts/contract_builder.py:287-315`

### 5.4 五个节点已完成基础 v2 升级

- 所有正式节点都已有：
  - `schema_version: "2.0"`
  - `task.name`
  - `task.description`
  - `runtime`
  - `tools`
  - `evaluator.yaml` 中的 `threshold`
  - `max_iterations: 3`

---

## 6. 与方案文档的偏差清单

### 6.1 文档承诺但代码未兑现

| 文档承诺 | 当前代码状态 | 影响 |
|---|---|---|
| `deliverable.template_title/output_filename/format_hints` 进入 v2 运行时 | YAML 有，Loader 不解析 | 配置-代码未完全对齐 |
| 节点级文件/搜索工具真正可用 | 主执行链没带权限进入 SessionManager | SDK 能力未真正激活 |
| Phase 5 门禁通过 | pytest 无法装载 | 不能宣称验证完成 |
| 四层提示词使用 preset/append 结构 | 直接字符串赋值 | 需明确设计决策 |
| `node.yaml` 包含 `evaluator` 内联/引用字段 | 无该字段，evaluator.yaml 独立 | 需明确设计决策 |

### 6.2 设计已变更但文档未同步

以下项需要明确确认设计取舍并同步更新文档：

1. **四层提示词架构的 SDK 结构**：若确认不使用 preset/append，应更新报告 05
2. **evaluator 配置位置**：若确认保持独立 evaluator.yaml，应更新报告 04 和路线图

---

## 7. 验证记录

### 7.1 已执行的核验

- 核对 `docs/research/refactor-2026-03-26/00-05` 与代码树
- 核对 `autoBMAD/nodes/*` 的 schema v2 配置
- 核对 `ContextValidator`、`ContextManager`、`NodeLoader`、`IndependentAgent`、`SessionManager`、`NodeToolFilter`、`contract_builder`
- 检查 `MemoryManager`/`MemoryScope` 活引用
- 尝试执行针对性 pytest

### 7.2 无法完成的验证

- 无法完成 pytest 级别回归，因为测试装载在 `tests/__init__.py:1` 就已中断

---

## 8. 建议的整改优先级

### P0

1. 修复主执行链的 `SessionManager` 创建，把 `node_id` 和真实的 `tool_permissions` 接入 `execute_with_input()` 路径。
2. 修复 `tests/__init__.py` 语法错误，恢复 pytest 最基本可执行性。
3. 扩展 `NodeDeliverableConfig` 与 `NodeLoader`，把 `template_title`、`output_filename`、`format_hints` 纳入运行时。

### P1

1. **明确设计决策**：四层提示词架构是否使用 SDK preset/append 结构，并同步更新文档。
2. **明确设计决策**：`evaluator` 配置是否保持独立文件模式，并同步更新文档。

### P2

1. 完善测试覆盖，确保 Phase 5 门禁可通过。

---

## 9. 最终判断

这轮重构**不是"没做成"**，相反，基础骨架已经搭起来了，很多关键对象和配置也确实已经迁到了正确方向上；但它也**还不是路线图描述的那个 fully integrated 版本**。

最关键的现实判断是：

- Phase 1 基础清理基本完成
- Phase 2 核心抽象基本成型
- Phase 3/4 仍存在"配置已写、代码未吃"与"能力已建、主链未接"的典型半完成状态
- Phase 5 目前没有可执行证据

如果要对外宣称"`docs/research/refactor-2026-03-26` 重构方案已经完成实施"，我认为**证据不足**。  
如果表述为"已完成大部分结构性重构，仍有若干高优先级接线与验证缺口"，则更符合当前事实。

---

## 附录：设计决策待确认清单

| 决策项 | 方案文档 | 当前状态 | 建议 | 待更新文档 |
|--------|----------|----------|------|-----------|
| 四层提示词 SDK 结构 | 使用 preset/append dict 结构 | 使用字符串赋值 | 明确是否支持 SDK dict 结构 | `05-claude-agent-sdk-reform.md` |
| evaluator 配置位置 | `node.yaml` 内联/引用 | 独立 `evaluator.yaml` | 确认保持独立文件模式 | `04-node-configuration-reform.md`, `00-refactoring-roadmap.md` |
