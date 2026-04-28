# 2026-03-17 P1-2 受控 Docs 上下文策略评估与决策记录

## 1. 评估目标

本报告用于评估以下修改任务是否应当对 `### P1-2: 把 docs 工具升级为受控上下文扩展策略` 做“修改”还是“移除”：

- 目标文档 1: `docs/research/2026-03-13-docuswarm-context-refactor-overview.md`
- 目标文档 2: `docs/research/2026-03-13-p1-controlled-docs-context-strategy-plan.md`

新增约束如下：

1. 工作流输出目录 `output/` 为唯一目录
2. 工作流不应当修改 `@docs` 文档

本文件先形成评估结论，后在 2026-03-17 补充最终决策记录。

## 2. 决策更新

最终决策：**选择选项 A，直接移除 P1-2。**

本次决策新增前提为：

- 产品已经决定“工作流完全不读取 `docs/`”
- `docs/` 不再属于工作流参考输入层
- 任何面向 workflow runtime 的 docs 读取、列举、写回能力都应视为移除对象或迁移债务

因此，本文件原始评估中对选项 C 的推荐已被覆盖。后续所有代码、测试和研究工作都应以“docs-free workflow”为基线推进。

相关后续研究报告：

- `docs/research/2026-03-17-docs-free-workflow-dependency-research.md`

## 3. 原始评估摘要（存档）

原始评估结论：**不建议直接移除 P1-2，建议将 P1-2 改写为“受控只读参考上下文策略”**，并明确它只负责 `docs` 的读取、筛选、摘要和注入，不再承载任何写入 `docs/` 的能力。

原因如下：

- `P1-2` 的“读侧目标”仍然成立：节点确实需要一个受策略约束的文档参考输入层，而不是放任 agent 随意读 `docs/`。
- `P1-2` 的“写侧含义”已经与新约束冲突：一旦工作流输出只能进入 `output/`，并且流程不得修改 `@docs`，那么 `update_docs_file` 及任何把 `docs/` 当作工作流产物落盘目录的设计都应退出该方案。
- 如果直接删除 `P1-2`，虽然能快速避开冲突，但会同时丢掉对 `@docs/...` 显式引用、节点级 allowlist、摘要限流、`docs_context` 注入边界这些仍然有价值的治理能力。

因此，最合理的方向不是“保留原样”或“整体删除”，而是**把 P1-2 收敛为只读策略，并把所有产物写入责任彻底归并到 `output/` 体系**。

## 4. 原始 P1-2 在文档中的含义

### 4.1 总览文档中的定位

`docs/research/2026-03-13-docuswarm-context-refactor-overview.md` 将 `P1-2` 定义为：

- “把 docs 工具升级为受控上下文扩展策略”
- 目标是“docs 不再是随缘外挂工具，而是受策略约束的上下文扩展层”

同时在目标架构中保留了这一句：

- `docs expansion governed by DocsContextPolicy`

并把 `P1-2` 放在以下依赖链的最后一环：

1. 单一上下文协议
2. prompt 注入
3. 单一交付物真相
4. `update_context` 持久化
5. docs 扩展策略

这个排序本身是合理的，说明原文作者也认为 docs 能力必须建立在主链路稳定之后。

### 4.2 P1-2 细化方案中的定位

`docs/research/2026-03-13-p1-controlled-docs-context-strategy-plan.md` 里，`P1-2` 的核心设计包括：

- 节点级 allowlist
- docs 读取顺序
- 大小限制
- 摘要化注入
- `read_docs_file` 作为 fallback 工具
- 把 `update_docs_file` 从默认工具集中移出
- 未来允许 `@docs/...` 显式引用接入同一策略

这份方案的原始重心其实是“**控制 docs 如何进入上下文**”，而不是“鼓励把 docs 当输出目录”。因此它并非整体失效，而是需要收缩边界。

## 5. 与新增约束的冲突分析

### 5.1 与“`output/` 为唯一输出目录”的冲突

当前仓库中，交付物主路径已经明确偏向 `output/{pipeline_id}/`：

- `docs/plan/PRD.md` 明确写到“Deliverable 文件实际写入 `output/{pipeline_id}/` 目录”
- `tests/integration/test_single_truth_workflow.py` 多处断言 `file_path` 位于 `output/pipeline-123/...`
- `autoBMAD/docuswarm/tools/create_deliverable.py` 通过 `Path.cwd()` 写文件，注释也说明写入 SDK `work_dir`

这说明“文件层单一真相 = `output/`”已经是当前主线设计。

与此相对，当前 `docs` 工具体系中存在真实写入能力：

- `autoBMAD/docuswarm/tools/update_docs_file.py` 直接把目标根目录固定为项目 `docs/`
- 默认独立代理配置 `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` 仍然暴露了 `update_docs_file`

因此，如果继续沿用“docs 工具升级”这类表述而不重写边界，就会把“参考输入目录”和“工作流输出目录”继续混在一起，违背“`output/` 为唯一输出目录”的新要求。

### 5.2 与“工作流不应当修改 `@docs` 文档”的冲突

当前仓库并不只是存在 `update_docs_file` 这个底层能力，部分自动化流程提示词本身也把 `docs/` 当成产物落点：

- `autoBMAD/epic_automation/agents/qa_agent.py` 明确要求 “create or update the story gate yaml file in `@docs\\qa\\gates`”
- `autoBMAD/epic_automation/agents/dev_agent.py` 明确要求检查 `@docs\\qa\\gates`

这意味着新约束一旦成立，影响范围不止 `P1-2` 研究文档，还包括更大范围的工作流假设：

- `docs/` 应当被重新定义为“参考资料库”或“人工维护文档库”
- 工作流自动产物应迁出 `docs/qa/gates`、`docs/evaluation` 等写路径，或者至少不再由自动执行流直接写入

对于 `P1-2` 而言，这意味着：

- `update_docs_file` 不是“默认移出”就够了
- 它应当从工作流语义里被明确排除
- `P1-2` 不应再包含任何“写回 docs”或“把 docs 作为落盘目标”的默认假设

### 5.3 与当前实现现状的关系

当前实现还没有真正完成 `P1-2` 里的“受控扩展”：

- `autoBMAD/docuswarm/node_execution/context_builder.py` 目前只是把 `docs_context=[]` 作为占位值返回
- 还没有看到 `DocsContextPolicy` 或 `ContextResolver` 的实际接入

这反而给了调整空间：因为 `P1-2` 还未深度落地，所以现在改方向的成本低于“先实现再回退”。

## 6. 哪些内容仍然有效，哪些内容应当失效

### 6.1 仍然有效的部分

以下设计在新约束下仍然成立，而且值得保留：

- 节点级 `allowlist`
- 文档读取顺序
- 文档数量和摘要大小限制
- “先摘要后注入”的 `docs_context` 设计
- `@docs/...` 显式引用必须经过统一策略，而不是裸读全量文件
- `read_docs_file` 和 `list_docs_files` 作为只读辅助能力

这些能力解决的是“读侧失控”问题，与“输出目录唯一”和“禁止改 docs”并不矛盾。

### 6.2 应当失效或迁出的部分

以下内容不应继续作为 `P1-2` 的一部分存在：

- `update_docs_file` 作为工作流可用能力
- 任何将 `docs/` 视为流程输出落盘位置的设计
- 把 `create_document_set` 归入“docs 策略”的表述

这里尤其要区分：

- `create_document_set` 当前实现按 `Path.cwd()` 写入工作目录，本质上属于“多文档输出工具”
- 它可以继续存在，但应当被放到“交付物输出策略”或“`output/` 多文件产物策略”下
- 它不应该继续被表述成 `docs` 策略的一部分

## 7. 选项评估

### 7.1 选项 A：直接移除 P1-2

优点：

- 文档修改最简单
- 能快速避免与新约束正面冲突
- 不需要再讨论 `docs` 工具的演化方向

缺点：

- 丢失 `@docs/...` 引用的治理边界
- 丢失 `docs_context` 的入口策略
- 以后如果仍允许读取 `docs/`，系统会再次退回“随缘读文档”的无策略状态

评估：**已采用**。前提已经成立，即产品层已决定“工作流完全不读取 `docs/`”。

### 7.2 选项 B：保留标题和原意，仅做局部微调

优点：

- 修改量小
- 保留现有研究文档结构

缺点：

- 标题里的“docs 工具升级”仍然容易让人理解成“读写都纳入策略”
- 很难明确切断 `docs/` 写入语义
- 会继续混淆“参考源”和“输出目录”

评估：**不推荐**。这会保留歧义。

### 7.3 选项 C：改写为“受控只读参考上下文策略”

建议新名称示例：

- `P1-2: 把 docs 访问收敛为受控只读参考上下文策略`
- 或 `P1-2: 建立 docs 只读参考注入策略`

优点：

- 保留原方案的读侧价值
- 与“`output/` 唯一输出目录”完全兼容
- 与“工作流不修改 `@docs`”完全兼容
- 能自然接住未来的 `@docs/...` 显式引用能力

缺点：

- 需要同步修改原文中若干段措辞和代码边界
- 需要把 `create_document_set` 从该议题中拆出去
- 需要在仓库更大范围内处理现有 `docs/qa/gates` 等写路径遗留设计

评估：**原始评估推荐，但已被最终决策覆盖**。在“工作流完全不读取 `docs/`”的新前提下，该选项不再采用。

## 8. 已废弃的备选文档改写方向（存档）

### 8.1 对总览文档的建议

建议把 `docs/research/2026-03-13-docuswarm-context-refactor-overview.md` 中的 `P1-2` 改成强调“只读参考”的表述，例如：

- 原标题：`把 docs 工具升级为受控上下文扩展策略`
- 建议标题：`把 docs 访问收敛为受控只读参考上下文策略`

建议同步改写目标描述：

- 原描述：`docs 不再是“随缘外挂工具”，而是受策略约束的上下文扩展层`
- 建议描述：`docs 仅作为只读参考源进入上下文，由策略控制选择、摘要和注入，不参与工作流写入`

建议同步改写目标架构摘要中的最后一行：

- 原句：`docs expansion governed by DocsContextPolicy`
- 建议：`read-only docs references governed by DocsContextPolicy`

依赖顺序可以保留在 `P1-1` 之后，不需要删除。

### 8.2 对 P1-2 详细方案文档的建议

建议把 `docs/research/2026-03-13-p1-controlled-docs-context-strategy-plan.md` 重写为“只读版”：

- 问题定义改为“当前 docs 读取没有策略”
- 设计目标改为“控制 docs 如何被读取和摘要，而不是如何写回”
- 推荐流程保留 `select -> read -> summarize -> inject`
- 明确 `read_docs_file` 只是 fallback 只读工具
- 删除或改写所有涉及 `update_docs_file` 的策略描述
- 将 `create_document_set` 从本文移出，交给 `output/` 输出策略文档处理

### 8.3 对“与 `@docs/...` 的关系”章节的建议

这一节建议明确写死三个边界：

1. `@docs/...` 只表示“显式引用参考资料”，不表示输出目标
2. 即使是显式引用，也要经过 allowlist、大小限制和摘要化边界
3. 所有工作流产物仍然只能写入 `output/{pipeline_id}/`

## 9. 已废弃的验收标准替换稿（存档）

建议将 `P1-2` 的验收标准改为以下方向：

- 每个节点都有可解释的只读 docs 选择策略
- `docs` 内容进入 prompt 前必须先摘要化或裁剪，不能整体灌入
- 默认工作流工具集中不再暴露 `update_docs_file`
- `@docs/...` 显式引用只具备读取语义，不具备写入语义
- 任何节点执行产物、评估产物、中间文档都只落盘到 `output/{pipeline_id}/` 或其受控子路径
- `docs_context` 只保存参考摘要或元数据，不保存“写回 docs”的计划

## 10. 若按备选方案改写时的代码边界评估（存档）

如果按推荐方案改写 `P1-2`，代码边界也应随之调整：

应保留在该议题内的范围：

- `autoBMAD/docuswarm/node_execution/context_builder.py`
- 新增 `docs_policy.py` 或同类策略模块
- 可能新增 `docs_summary.py` 或类似摘要模块
- `read_docs_file` / `list_docs_files` 的只读接入边界

应移出该议题或明确禁用的范围：

- `autoBMAD/docuswarm/tools/update_docs_file.py`
- 默认代理配置中对 `update_docs_file` 的暴露
- 将 `docs/` 作为自动产物目录的提示词和流程约定

应重新归类而非继续挂在 `P1-2` 下的范围：

- `autoBMAD/docuswarm/tools/create_document_set.py`

原因是它属于“多文件输出能力”，不属于“docs 参考上下文策略”。

## 11. 基于最终决策的风险与后续动作

### 11.1 主要风险

- 研究文档如果只改 `P1-2` 标题、不改细节，会留下新的语义歧义
- 仓库内已有若干流程默认写 `docs/qa/gates`，如果不联动治理，新的约束会和旧流程长期冲突
- `docs_context` 目前还是空占位，如果只做文档修改、不做实现治理，后续仍可能回到“agent 自由读 docs”的旧模式

### 11.2 建议后续动作

建议按以下顺序推进：

1. 在研究文档层面明确 `P1-2` 已删除，且工作流完全不读取 `docs/`
2. 从默认代理配置、工具导出和运行时注册路径中移除 docs 相关工具
3. 删除或重写锁定 docs 工具存在性的测试用例与注册断言
4. 决定 `docs_context` 是彻底删除还是显式标记为废弃字段
5. 更新调试工具与研究脚本，使 docs 相关残留被视为清理债务而非未来路线

## 12. 最终建议

最终建议如下：

- **直接删除 `P1-2`**
- **明确工作流完全不读取 `docs/`**
- **将 `docs/` 相关 runtime/test/tooling 依赖统一视为清理对象**

一句话概括就是：

> `docs/` 不再参与工作流执行链路；真正的工作流输入来自结构化上下文，真正的工作流输出目录只能是 `output/`。
