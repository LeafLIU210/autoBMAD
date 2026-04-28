# 2026-03-17 DocuSwarm 全量审查报告（修订版）

> 审查对象：`autoBMAD/docuswarm`
> 初始审查日期：2026-03-17
> 本次修订：根据后续决策与约束收敛结论
> 审查方式：静态代码审查、运行产物核对、架构与技术债评估
> 修订结论：**项目可继续演进，不建议重写；应以“单一业务状态真相源 + docs-free 工具面 + 结构化工具契约”作为后续收敛主线**

## 1. 执行摘要

`docuswarm` 已经具备明确的系统骨架：5 节点流水线、双 Agent 协作、SQLite 状态持久化、文件落盘交付物，以及围绕 Single Context Protocol 的结构化重构。代码库已明显超过原型阶段，核心风险也不再是“功能缺失”，而是“重构后契约尚未完全收敛”。

本次修订后，报告结论收敛为四条主线：

1. 业务状态真相源应统一到 `state_json`，LangGraph checkpoint 只保留为执行期恢复快照，不再与业务状态并列。
2. `shared_context` 与 Evaluator 输入链路的建议维持不变，应继续补齐贯穿执行闭环。
3. 工具层产品决策明确选择 **docs-free**，只保留 `create_deliverable` / `create_document_set` / `update_context`。
4. 工具返回协议应收敛到**结构化 Python dataclass 风格**，拒绝把 kimi SDK `ToolOk/ToolError` 作为系统主契约；字符串内嵌 `METADATA:` JSON 仅可作为过渡兼容层，不应继续扩张。

换句话说，当前最重要的不是继续横向加功能，而是把“状态、上下文、工具协议”三条主契约彻底收敛成一条稳定主线。

## 2. 审查范围与说明

本次重点审查的代码范围包括：

- 入口与配置：`main.py`、`__main__.py`、`config.py`
- 流水线与状态：`pipeline/*`、`storage/*`
- 节点执行：`node_execution/*`、`nodes/dual_agent.py`
- Agent 与 prompt：`agents/*`、`context/isolation.py`、`prompts/contract_builder.py`
- 工具层：`tools/*`、`models/*`
- 运行证据：`docuswarm.db`

补充说明：

- 初始审查阶段曾结合当时测试输出、静态检查和数据库内容形成问题判断。
- 关于测试体系，本修订版采用你的最新说明：**测试文件已重建，原先混杂环境噪音与历史契约冲突的旧测试，不再作为当前质量门基线**。
- 因此本报告中涉及测试的内容，统一按“历史问题画像与后续治理原则”来表述，而不再把旧测试结果当作当前仓库现状结论。

## 3. 正向评价

项目有几个值得保留的基础：

- 分层意图清晰。`pipeline`、`node_execution`、`agents`、`storage`、`tools` 的职责边界总体合理。
- 关键业务概念已经显式化。`NodeExecutionContext`、`DeliverableArtifact`、`EvaluatorAgentInput` 等类型定义方向正确。
- “文件层承载正文，状态层承载元数据”的设计方向优于把完整交付物长期塞进状态层。
- 工程上已经明显进入体系化开发阶段，后续更需要做的是“收敛”和“删减”，不是推倒重来。

因此，本报告的总体基调不是否定项目，而是帮助其从“重构中段”走向“运行契约稳定期”。

## 4. 关键发现

以下按严重程度排序。

### F1. 状态持久化与恢复链路没有闭环，这是当前最危险的系统性问题

关键位置：

- `autoBMAD/docuswarm/storage/state_manager.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `autoBMAD/docuswarm/pipeline/graph.py`

问题表现：

- `StateManager.create_pipeline()` 当前把 `subject_context` 直接写入 `state_json`，并不是完整 `PipelineState`。
- `resume_pipeline()`、重启节点等逻辑，却又从 `get_pipeline()["state"]` 中读取 `current_node`、`completed_nodes`、`deliverables`、`session_ids` 等完整状态字段。
- 数据库抽样也说明，当前 `state_json` 与“完整可恢复业务状态”之间存在明显差距。

这说明项目当前实际上存在两个候选真相源：

- `state_json`
- LangGraph checkpoint

#### 依据奥卡姆剃刀原则的评估

如果只问“哪个更接近运行时真相”，LangGraph checkpoint 看起来更像真实执行快照，因为它由 graph 运行期直接产生。

但如果问题是“哪个更能反映业务真相且长期稳定”，结论应是：**`state_json` 更适合作为唯一业务真相源**。理由如下：

1. `state_json` 是项目自己定义和控制的数据结构，而 checkpoint 属于框架内部恢复机制，天然更耦合 LangGraph 实现细节。
2. `state_json` 更易审计、易查询、易调试，也更适合作为 `status`、`resume`、`restart`、运营排障的统一来源。
3. 当前流水线本质上是固定顺序的 5 节点串行执行，不是高度动态的复杂 graph。对这种业务模型来说，用业务状态重建执行位置，比把框架内部 checkpoint 当作唯一真相更简单、更稳定。
4. 若把 checkpoint 也当业务真相源，系统就必须持续维护“双语义一致性”：一套是业务状态语义，一套是框架恢复语义。这违反奥卡姆剃刀原则，会持续引入额外复杂度。

#### 修订结论

应当明确：

- **`state_json` 是唯一业务状态真相源**
- **LangGraph checkpoint 只是执行期恢复快照**

也就是说：

- `resume/status/restart` 的业务判断，应统一基于 `state_json`
- checkpoint 只用于“如何继续执行”的技术细节，不再用于“系统当前处于什么业务状态”的主判断

对当前项目而言，这比“让 checkpoint 和 `state_json` 同时表达完整真相”更符合奥卡姆剃刀原则，也更符合长期稳定性。

影响判断：

- 这是 **P0 级技术债**
- 它直接影响中断恢复、状态展示、排障与后续所有增量执行能力

建议：

- 统一把 `PipelineState` 作为 `state_json` 的完整结构
- `resume/status/restart` 一律从 `state_json` 读取业务状态
- LangGraph checkpoint 保留为执行期快照，不再作为并列业务真相源
- 若 checkpoint 丢失，系统也应能仅基于 `state_json` 进行“从当前节点重新执行”的恢复

### F2. `shared_context` 只完成了“能写”，没有完成“能持续参与执行”

关键位置：

- `autoBMAD/docuswarm/storage/state_manager.py`
- `autoBMAD/docuswarm/context/isolation.py`
- `autoBMAD/docuswarm/agents/independent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`

问题表现：

- `UpdateContextTool` 已能把内容写入 `state_json.shared_context`
- `ContextManager.build_independent_input()` 也会把 `shared_context` 放入 `IndependentAgentInput`
- 但 Agent 执行链路中仍存在重新构造上下文时将其置空的情况
- 恢复链路也没有稳定回填 `shared_context`

这意味着共享上下文当前只完成了“持久化入口”，没有形成“下游消费”与“恢复延续”的完整闭环。

影响判断：

- 这是 **P0/P1 之间** 的债务
- 它直接削弱跨节点协作与增量补充上下文能力

修订结论：

- **同意原建议，维持不变**

建议：

- 停止在 Agent 层重建一个丢字段的精简版执行上下文
- 让 `shared_context` 从写入、下游 prompt 消费到 resume 恢复形成完整闭环
- 补一条贯穿测试：写入 -> 下一节点可见 -> resume 后仍可见

### F3. Evaluator 的输入契约被重新削弱，原始上下文与交付物真相并未稳定闭环

关键位置：

- `autoBMAD/docuswarm/context/isolation.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/prompts/contract_builder.py`

正向进展：

- `ContextManager.build_evaluator_input()` 已要求 `file_path`
- Evaluator 读取磁盘中的正式正文，而不是退回到摘要评审，这个方向是正确的

核心问题：

- `EvaluatorAgent.execute_with_input()` 后续仍存在重建上下文并丢失原始需求信息的风险
- 因此“输入契约已具备”并不等于“最终 prompt 已稳定携带全部必要事实”

影响判断：

- 这是 **P1 级债务**
- 它会让 Evaluator 偏向评审“文档质量”，而不是评审“是否对齐原始目标”

修订结论：

- **同意原建议，维持不变**

建议：

- `EvaluatorAgent.execute_with_input()` 直接围绕 `EvaluatorAgentInput` 组装 prompt
- 不再重建一个信息更少的 `NodeExecutionContext`
- 增加 prompt 快照测试，断言最终 prompt 必含：
  - 原始上下文摘要
  - 交付物正文
  - 评价标准

### F4. 工具层处于“产品决策未收敛”状态，已经出现新旧约定互相否定

关键位置：

- `autoBMAD/docuswarm/tools/__init__.py`
- `autoBMAD/docuswarm/tools/update_context.py`
- `autoBMAD/docuswarm/models/tool_registry.py`

初始问题画像里，工具层同时承载了两套互相冲突的假设：

- 一套是 docs-free
- 一套是保留 docs 工具与旧注册逻辑

这类双轨并行会造成：

- prompt 契约摇摆
- 工具注册接口难以稳定
- 测试与实现持续背离

#### 修订后的产品决策

本项结论现在明确收敛为：

- **方案 A：坚持 docs-free**
- **只保留 `create_deliverable` / `create_document_set` / `update_context`**
- **不再维持两套互相矛盾的测试一起存在**
- **工具注册 API 必须收敛成一种用法**

这意味着后续应明确下线以下历史残留方向：

- `read_docs_file`
- `list_docs_files`
- `update_docs_file`
- 围绕它们建立的旧式注册、旧式导出、旧式兼容测试

影响判断：

- 这是 **P0/P1 级组织性技术债**
- 一旦收敛，整个 Agent 工具面会立刻变清晰

建议：

- 在代码、文档、测试三个层面同步声明 docs-free 为唯一有效决策
- 工具注册 API 只保留一种风格
- 不再保留“旧 API 可能未来还会回来”的模糊空间

### F5. `ToolResult` / `ToolResultExtractor` / 工具返回格式之间已经分叉

关键位置：

- `autoBMAD/docuswarm/tools/tool_result.py`
- `autoBMAD/docuswarm/tools/tool_result_extractor.py`
- `autoBMAD/docuswarm/tools/create_deliverable.py`

当前工具返回风格曾同时出现三种：

1. 结构化 Python dataclass 风格
2. kimi SDK `ToolOk/ToolError` 风格
3. 字符串里内嵌 `METADATA:` JSON 的兼容风格

#### 修订后的评估结论

本项现在明确拒绝把 **kimi SDK `ToolOk/ToolError`** 作为系统主契约。

在剩余两种方案中，对比如下：

**结构化 Python dataclass 风格**

- 优点：类型明确、IDE 友好、易测试、易序列化、易做系统内稳定演进
- 缺点：如果外部调用面只能接收文本，需要额外加一层适配

**字符串里内嵌 `METADATA:` JSON 的兼容风格**

- 优点：短期兼容已有文本解析逻辑
- 缺点：天然脆弱，容易因文案变更、换行、编码、前缀污染而失稳
- 缺点：解析责任外溢到 Agent、工具提取器、测试层，长期维护成本高

#### 修订结论

- **结构化 Python dataclass 风格应成为唯一主契约**
- `METADATA:` JSON 风格至多只能作为边界兼容适配层
- kimi SDK `ToolOk/ToolError` 风格不应继续作为系统内部主接口扩散

影响判断：

- 这是 **P1 级债务**
- 但一旦收敛，工具层和测试层复杂度会明显下降

建议：

- 把 `ToolResult` 收敛成项目自有的结构化主协议
- `ToolResultExtractor` 仅在必要边界做适配，不再承担主协议翻译角色
- 新工具禁止再引入 `ToolOk/ToolError` 作为项目内部事实格式

### F6. 测试体系同时存在“环境噪音”和“真实回归”，当前红灯不能直接作为回归质量门

本项在初始审查时，确实呈现出“环境噪音 + 历史契约冲突混杂”的问题画像。

但本修订版采用你的最新说明：

- **测试文件已经完全清理**
- **所有测试已经重新建立**

因此本项结论需要调整为：

- 旧测试红灯不再代表当前基线
- 原先的测试问题应被视为“历史债务样本”，不是当前质量门结论

#### 修订结论

当前更重要的不是继续分析旧测试噪音，而是确保新测试体系遵循以下原则：

1. 只围绕现行产品决策建立测试
2. docs-free 是唯一有效工具面
3. 单一状态真相源是 `state_json`
4. 结构化工具协议是唯一主协议
5. 环境敏感测试与核心逻辑测试必须清晰分层

影响判断：

- 旧问题本质上属于 **历史 P1 级测试债**
- 但在你已重建测试体系的前提下，本项应转化为“防止旧问题回流”的治理原则

建议：

- 将新测试体系明确绑定到本报告修订版中的收敛决策
- 不再为历史双轨假设保留并行测试
- 让测试真正成为当前架构的质量门，而不是历史阶段的留声机

### F7. 类型系统、导出面和惰性导入层已经出现腐蚀

问题表现主要集中在：

- `__all__` 与实际导出不一致
- lazy import 侵蚀静态可见性
- 装饰器、override、类型检查之间存在持续摩擦

这类问题短期未必先炸运行，但会持续削弱：

- IDE 可置信度
- 重构反馈速度
- 类型系统作为保护网的价值

影响判断：

- 这是 **P2 级债务**

修订结论：

- **同意原建议，维持不变**

建议：

- 优先把 `error` 级别的类型问题清零
- 对 `__all__`、lazy import、CLI 类型包装做专项收敛

### F8. 文档层也存在漂移与质量退化信号

问题表现包括：

- 设计文档、评估文档与当前生效决策之间存在时间差
- 部分文档仍残留旧阶段表述
- 存在编码与可读性问题

影响判断：

- 这是 **P2 级债务**

修订结论：

- **同意原建议，维持不变**

建议：

- 建立“当前生效决策索引”
- 标记哪些文档已废弃、哪些为历史方案、哪些仍有效
- 清理编码与陈旧内容，避免协作时继续读取过期结论

## 5. 技术债画像

修订后，项目的核心技术债可以收敛为四类：

- **状态债**：业务状态真相源尚未统一
- **上下文债**：`shared_context` 与 Evaluator 输入链路还未完全闭环
- **协议债**：工具返回格式与工具注册方式未完全收敛
- **文档/类型债**：静态边界与文档边界仍有历史漂移

相比初始版本，本修订版已经明确删去了一个模糊点：

- 不是“多种状态源共同竞争”
- 而是“应明确 `state_json` 为唯一业务状态真相源”

这一步非常关键，因为它会反向稳定恢复链路、工具链路和测试链路。

## 6. 优先级建议

不建议大重写，建议按以下顺序增量治理。

### Phase 1：先收敛主契约

1. 把 `state_json` 收敛为完整 `PipelineState`
2. 明确 checkpoint 仅为执行恢复快照
3. 打通 `shared_context` 的写入、消费、恢复闭环
4. 让 Evaluator prompt 稳定携带原始上下文与正式正文
5. 固化 docs-free 工具面

### Phase 2：再收敛工具协议

1. 以结构化 Python dataclass 为唯一主协议
2. 将 `METADATA:` JSON 降级为边界兼容层
3. 拒绝继续扩散 kimi SDK `ToolOk/ToolError` 风格
4. 工具注册 API 收敛成一种用法

### Phase 3：最后收敛工程边界

1. 清理类型系统 `error`
2. 收敛导出面与 lazy import
3. 清理文档漂移与编码问题
4. 让新测试体系与当前决策完全一致

## 7. 业务化表述建议

如果需要向非工程角色解释，可以这样描述：

- 当前工作重点不是“重写系统”，而是“统一系统真正依据哪套规则运行”
- 一旦状态、工具和上下文协议统一，后续开发速度会更快，回归成本会更低
- 这不是纯工程洁癖，而是典型的产品债治理

## 8. 最终结论

`autoBMAD/docuswarm` 值得继续建设，且不需要重写。

本修订版之后，关键方向已经足够明确：

- `state_json` 是唯一业务状态真相源
- LangGraph checkpoint 只是执行恢复快照
- docs-free 是唯一有效工具面
- 结构化 Python dataclass 是唯一主工具协议

只要后续实现持续围绕这四条收敛，项目就会从“重构中段风险区”进入“稳定演进区”。

## 9. 附录：本次修订版保留的高价值证据点

- `storage/state_manager.py`
  - `create_pipeline()` 当前仍未把完整业务状态写入 `state_json`
  - `update_shared_context()` 说明共享上下文已具备持久化入口
- `pipeline/orchestrator.py`
  - `resume_pipeline()` / restart 逻辑当前仍假定可从 `state` 读取完整恢复语义
- `agents/independent.py`
  - 执行链路中仍存在重建上下文并置空字段的风险
- `agents/evaluator.py`
  - Evaluator 执行链路中仍存在上下文重建后信息丢失的风险
- `context/isolation.py`
  - `build_evaluator_input()` 已经朝“评审正式正文而非摘要”方向前进

