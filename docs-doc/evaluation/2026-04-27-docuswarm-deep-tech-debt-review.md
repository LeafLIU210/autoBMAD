# 2026-04-27 DocuSwarm 深度技术债审查报告

审查对象：`autoBMAD/docuswarm`  
审查日期：2026-04-27  
审查视角：技术债 / 产品债 / 可运维性 / 演进风险  
审查基准：当前工作区代码状态。当前仓库存在大量未提交迁移与文档搬迁改动，本报告只评价当前可见文件，不假设其已经进入主干。

## 结论摘要

`autoBMAD/docuswarm` 已经形成了完整的多 Agent 文档流水线骨架，但当前主要风险不在“缺少功能代码”，而在运行时合同没有闭环：节点失败会被流水线层吞掉，共享上下文链路无法可靠传递，工具权限配置被 `SessionManager` 放大，SQLite 单例会跨数据库路径污染状态。现有 52 个 `tests/docuswarm` 测试全部通过，但覆盖率只有 24%，且大量核心路径为 0% 覆盖，无法证明真实流水线可靠。

总体判断：不建议重写。应做 2-4 周的增量偿债，先修 P0 正确性和权限边界，再压缩兼容层和重复工具实现。

健康评分：45 / 100

优先级判断：
- P0：失败传播、共享上下文、工具权限、数据库实例隔离。
- P1：交付物元数据与文件冲突、CLI 配置边界、测试覆盖门禁。
- P2：拆分巨型类、收敛 legacy / sdk 双实现、静态检查清零。

## 审查方法

本次审查使用以下证据来源：

- 结构盘点：`autoBMAD/docuswarm`、`tests/docuswarm` 文件数、行数、热点模块。
- 静态检查：`ruff`、`basedpyright`。
- 回归测试：`pytest tests/docuswarm`。
- 运行时最小验证：数据库单例路径、`PipelineAdapter` shared_context 传递。
- 关键链路走读：CLI -> PipelineService -> HybridOrchestrator -> LangGraph -> NodeExecutor -> DualAgentNode -> SessionManager -> MCP tools -> StateManager。

已执行验证：

```text
python -m pytest tests/docuswarm -q --basetemp=.tmp/pytest-docuswarm-review
结果：52 passed，覆盖率 24%，pytest cache 写入出现 WinError 5 警告

python -m ruff check autoBMAD/docuswarm tests/docuswarm
结果：185 errors，其中 170 个可自动修复

python -m basedpyright autoBMAD/docuswarm tests/docuswarm
结果：17 errors，279 warnings
```

## 代码规模与风险轮廓

`autoBMAD/docuswarm` 当前有 101 个 Python 文件，约 27,424 行；`tests/docuswarm` 只有 13 个 Python 文件，约 955 行。测试规模相对生产代码约 3.5%，并且覆盖偏向近期修复点，而不是核心流水线行为。

最大文件 / 类集中度：

| 组件 | 规模 | 风险 |
| --- | ---: | --- |
| `context/validator.py` | 1,960 行 | 多策略、大量规则集中在一个文件，变更耦合高 |
| `storage/state_manager.py` | 1,306 行 | 同时负责 pipeline、node run、shared_context、history |
| `agents/independent.py` | 1,198 行 | prompt、skills、session、解析、fallback 混合 |
| `pipeline/orchestrator.py` | 1,086 行 | 启动、恢复、总结、checkpoint、状态更新混合 |
| `llm/session_manager.py` | 1,049 行 | 权限、MCP server、SDK session、message 转换混合 |
| `prompts/contract_builder.py` | 920 行 | 模板查找、映射、渲染与 fallback 混合 |
| `nodes/dual_agent.py` | 896 行 | 两套执行循环并存，语义不一致 |

重复实现热点：

| 工具族 | legacy 文件 | SDK 文件 | 合计行数 |
| --- | --- | --- | ---: |
| file tools | `tools/file_tools.py` | `tools/file_tools_sdk.py` | 936 |
| search tools | `tools/search_tools.py` | `tools/search_tools_sdk.py` | 973 |
| deliverable | `tools/create_deliverable.py` | `tools/create_deliverable_sdk.py` | 661 |
| update_context | `tools/update_context.py` | `tools/update_context_sdk.py` | 454 |

这类重复不是单纯“代码多”，而是同一行为存在多套合同，容易让测试覆盖了 A 路径，真实 Agent 跑 B 路径。

## 关键发现

### F1. Critical：节点失败会被流水线层吞掉，并被标记为已完成

证据：

- `NodeExecutor` 捕获任何异常后只把 `new_state["status"] = FAILED`，没有重新抛出：`autoBMAD/docuswarm/node_execution/executor.py:235`。
- `PipelineAdapter.convert_node_to_pipeline_state()` 不读取 `node_state["status"]`，直接把节点加入 `completed_nodes`：`autoBMAD/docuswarm/node_execution/pipeline_adapter.py:294`。
- `pipeline/graph.py` 在 integrated executor 捕获异常后只记录日志并 fallback 到默认状态：`autoBMAD/docuswarm/pipeline/graph.py:126`。
- `HybridOrchestrator.start_pipeline()` 在 `graph.ainvoke()` 返回后无条件把 pipeline 状态更新为 `completed`：`autoBMAD/docuswarm/pipeline/orchestrator.py:459`。

影响：

- 任意节点内部失败可能被最终包装成“节点完成 / pipeline completed”。
- 下游节点可能拿到空 deliverable 继续跑，生成低质量或误导性文档。
- 事故不可见，用户看到的是“成功结束”，但核心产物缺失。
- 这会直接腐蚀状态机可信度，是当前最高优先级技术债。

建议：

- `NodeExecutor` 对不可恢复异常应返回 `FAILED` 且携带 `error`，或直接抛出。
- `PipelineAdapter.convert_node_to_pipeline_state()` 只允许 `COMPLETED` / `FORCE_APPROVED` 进入 `completed_nodes`。
- `pipeline/graph.py` 不应 fallback 成成功状态；失败应进入 pipeline `failed` 或 `paused`。
- 增加回归测试：模拟 `async_node_executor` 抛错、返回 `FAILED`、返回 `RUNNING/NEEDS_REVISION`，验证 pipeline 不会 completed。

### F2. Critical：shared_context 设计有持久化表象，但运行时传递链路断裂

证据：

- `PipelineAdapter.convert_pipeline_to_node_state()` 从 pipeline state 构造 NodeRunState 时没有把 `shared_context` 放入返回值：`autoBMAD/docuswarm/node_execution/pipeline_adapter.py:233`。
- `NodeExecutor` 后续从 NodeRunState 读取 `state.get("shared_context", {})` 构造执行上下文，因此实际总是容易退回空对象：`autoBMAD/docuswarm/node_execution/executor.py:357`。
- `_refresh_shared_context_from_db()` 试图从 `SessionManager` 上 duck typing 找 `StateManager`，但真实 `SessionManager` 没有稳定暴露 `_state_manager/storage/state_manager`：`autoBMAD/docuswarm/node_execution/executor.py:432`。
- `create_update_context_server()` 在 MCP tool 内部直接 `StateManager()`，没有接收当前 orchestrator 的 `db_path` 或 state manager：`autoBMAD/docuswarm/tools/update_context_sdk.py:98`。
- `DatabaseManager.get_instance()` 是单全局实例，第一次 db_path 会污染后续 StateManager：`autoBMAD/docuswarm/storage/database.py:64`。最小验证显示先创建 `one.db` 再创建 `two.db`，第二个实例仍指向 `one.db`。

影响：

- Agent 可能成功调用 `update_context`，但下游节点看不到更新。
- 非默认数据库路径、测试数据库、并行 pipeline 会互相污染或写错库。
- shared_context history 表有记录能力，但业务链路无法可靠消费它。
- 这会让“共享上下文”变成产品债：界面和文档声称支持协作记忆，真实输出不稳定。

建议：

- `PipelineAdapter.convert_pipeline_to_node_state()` 必须传递 `shared_context`。
- `convert_node_to_pipeline_state()` 必须把刷新后的 `shared_context` 合回 pipeline state。
- `SessionManager` 构造时接收 `state_manager` 或 `db_path`，MCP server factory 不应自行创建默认 `StateManager()`。
- `DatabaseManager` 改成按 `resolved_db_path` 缓存实例，或取消全局单例，至少对不同路径显式报错。
- 增加端到端测试：analyst 调 `update_context` 写入事实，pm 节点输入必须包含该事实。

### F3. Critical：工具权限配置被 SessionManager 放大，节点白名单没有成为真实边界

证据：

- 节点配置只允许内置工具 `Read`、`Glob`，例如 `autoBMAD/nodes/analyst/node.yaml:77`。
- `SessionManager._get_builtin_tools()` 对所有 session 固定开放 `Read`, `Glob`, `Grep`, `Edit`, `Bash`：`autoBMAD/docuswarm/llm/session_manager.py:168`。
- `_build_allowed_tools()` 无条件加入这些内置工具，再把 `NodeToolFilter` 里重复的 builtin 过滤掉：`autoBMAD/docuswarm/llm/session_manager.py:199`。
- `_create_options()` 在 `yolo=True` 时设置 `permission_mode = "bypassPermissions"`：`autoBMAD/docuswarm/llm/session_manager.py:245`。

影响：

- 配置层声明“只读”，运行层却可 `Edit` / `Bash`。
- Agent 可以在生成文档时修改文件或执行 shell，破坏隔离预期。
- 安全审计和节点权限文档会失真。

建议：

- `_get_builtin_tools()` 不应是全局默认；应从 `NodeToolPermissions.allowed_builtin_tools` 派生。
- 默认禁用 `Edit` 和 `Bash`，除非节点配置显式授权。
- `yolo=True` 不应与高危工具共存；对 Bash/Edit 建议引入单独 allowlist。
- 为每个节点增加权限快照测试：读取 `node.yaml`，断言 SDK options 中实际 `allowed_tools` 等于配置展开结果。

### F4. High：交付物工具丢弃元数据且会覆盖同名文件，多文档能力不闭环

证据：

- `create_deliverable()` 接收 `metadata`，但 `result_metadata` 没有合并它：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:167`。
- MCP handler 把 `document_index`、`document_total`、`document_type` 合入 `metadata`：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:332`，但随后被底层函数丢弃。
- 文件名只由 title slug 得到，`file_path.write_text()` 会直接覆盖同名文件：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:185`。

影响：

- 多文档输出的文档序号、总数、类型可能不会进入工具返回值。
- Agent 后续提交执行报告时缺少真实元数据，validator 和 evaluator 的判断会变弱。
- 同标题多次迭代会覆盖文件，历史产物和 hash 追踪失真。

建议：

- `result_metadata` 合并安全过滤后的 `metadata`。
- 文件名增加节点、document_type、document_index 或唯一后缀，避免静默覆盖。
- 增加测试：多文档参数应出现在 tool result；同 title 二次调用不应覆盖首次文件。

### F5. High：`DualAgentNode.execute_with_context()` 达到最大迭代后仍可能返回 NEEDS_REVISION

证据：

- `execute_with_context()` 使用 `while iteration < self.max_iterations` 循环：`autoBMAD/docuswarm/nodes/dual_agent.py:310`。
- 当 verdict 持续为 `NEEDS_REVISION` 时，只设置 `previous_feedback` 并继续：`autoBMAD/docuswarm/nodes/dual_agent.py:500`。
- 循环结束后直接构造 `NodeResult` 返回，没有强制完成、阻塞或失败分支：`autoBMAD/docuswarm/nodes/dual_agent.py:513`。
- 同文件另一套 `execute_with_iteration()` 有 force/block 逻辑，但当前 `NodeExecutor` 调用的是 `execute_with_context()`：`autoBMAD/docuswarm/node_execution/executor.py:154`。

影响：

- 节点质量未达标也可返回结果。
- 再叠加 F1，流水线层可能把该节点当完成节点。
- 两套执行循环语义不一致，未来维护者很难判断哪个才是 canonical behavior。

建议：

- 将 `execute_with_iteration()` 的终止语义迁回 `execute_with_context()`，或删除一套循环。
- 达到 max_iterations 时必须产出 `FORCE_APPROVED` 或 `BLOCKED/FAILED`，不能返回未决状态。
- 增加测试：Evaluator 连续返回 `NEEDS_REVISION` 时，最终状态必须可预测。

### F6. Medium：配置包与配置模块同名，靠动态导入和吞异常维持运行

证据：

- 同时存在 `autoBMAD/docuswarm/config.py` 和 `autoBMAD/docuswarm/config/` 包。
- `config/__init__.py` 通过 `importlib.util.spec_from_file_location()` 加载 sibling `config.py`：`autoBMAD/docuswarm/config/__init__.py:31`。
- 导入失败时把 `Config` / `load_config` 置为 `None`，但不显式失败：`autoBMAD/docuswarm/config/__init__.py:45`。

影响：

- 类型系统无法理解真实类型，`basedpyright` 产生大量噪音。
- 导入失败会延迟到运行时的 `NoneType is not callable`。
- 新开发者会误判配置入口，增加维护成本。

建议：

- 将 `config.py` 重命名为 `settings.py` 或 `app_config.py`，让 `config/` 只作为包。
- 移除动态导入和吞异常 fallback。
- 将 `load_config()` 拆成 `load_runtime_config(require_api_key=True)` 和 `load_storage_config(require_api_key=False)`。

### F7. Medium：CLI 只读命令也强制加载 API Key

证据：

- CLI group 入口无条件 `load_config()`：`autoBMAD/docuswarm/cli/main.py:61`。
- `PipelineService.__init__()` 也无条件 `load_config()`：`autoBMAD/docuswarm/cli/services/pipeline_service.py:28`。
- `Config.__post_init__()` 强制要求 `ANTHROPIC_API_KEY`：`autoBMAD/docuswarm/config.py:99`。

影响：

- `status`、`list`、`questions`、`export` 等只读命令理论上不需要 LLM Key，却会因为环境缺失而失败。
- 运维排障时最需要读状态，但状态读取依赖外部 API 凭据，形成不必要耦合。

建议：

- CLI group 只初始化日志，不加载 LLM 凭据。
- start/resume 这类需要 LLM 的命令再加载 `require_api_key=True` 配置。
- `StateManager` 只依赖 storage config。

### F8. Medium：测试通过但覆盖不足，核心路径几乎没有保护

证据：

- `tests/docuswarm` 52 个测试通过。
- 覆盖率总计 24%。
- 关键路径覆盖率：
  - `pipeline/orchestrator.py` 17%
  - `pipeline/graph.py` 24%
  - `node_execution/executor.py` 0%
  - `nodes/dual_agent.py` 0%
  - `storage/state_manager.py` 11%
  - `agents/independent.py` 17%
  - CLI 命令多为 0%

影响：

- 现有测试主要证明近期 F1-F5 修复点存在，不证明端到端流水线正确。
- 失败传播、权限边界、数据库路径隔离、shared_context 消费都缺少红绿测试。
- 重构巨型类时回归风险极高。

建议：

- P0 测试先覆盖行为合同，不追求全量覆盖率：
  - 节点失败不得 completed。
  - shared_context update 必须进入下一节点输入。
  - `allowed_tools` 必须等于节点配置。
  - 非默认 db_path 下 MCP update_context 写入同一数据库。
- 设置阶段性覆盖目标：先把核心链路模块从 0-20% 提到 60%，总覆盖从 24% 提到 40%。

### F9. Medium：静态质量门禁已经失效，噪音掩盖真实问题

证据：

- `ruff`：185 errors，包括未使用导入、import 顺序、空白字符、测试内未使用变量。
- `basedpyright`：17 errors，279 warnings。CLI click 装饰器、动态 config、未标注参数与私有方法测试访问是主要来源。

影响：

- CI 如果未启用这些检查，代码质量债会继续滚大。
- 如果突然启用，会产生大量历史失败，团队会倾向绕过门禁。

建议：

- 先运行 `ruff --fix` 清理安全可修项。
- 为 click 命令与动态 SDK 类型增加局部类型适配，而不是全局关闭。
- 对 `basedpyright` 分层治理：先清 17 个 errors，再逐步处理 warnings。

## 技术债偿还路线图

### P0：先恢复运行时可信度

目标：让系统在失败时失败，在成功时才成功。

建议任务：

1. 修复节点状态传播。
   - `FAILED/BLOCKED/RUNNING` 不得进入 `completed_nodes`。
   - `HybridOrchestrator` 不得无条件写 `completed`。
   - 为失败节点保存 `error`、`node_id`、`verdict`。

2. 修复 shared_context 端到端链路。
   - PipelineState -> NodeRunState -> NodeExecutionContext -> DB refresh -> PipelineState 全链路带 `shared_context`。
   - MCP `update_context` 使用当前 pipeline 的 db_path/state_manager。
   - 修复 `DatabaseManager` 单例按路径污染问题。

3. 收紧工具权限。
   - 从节点配置生成实际 `allowed_tools`。
   - 移除全局默认 `Edit/Bash`。
   - 为高危工具增加显式 allowlist。

验收标准：

- 新增 8-12 个单元/集成测试，覆盖上述失败模式。
- `pytest tests/docuswarm` 通过。
- 手工构造失败节点时 pipeline 状态为 `failed` 或 `paused`，不会 `completed`。

### P1：让交付物、CLI、配置可维护

目标：减少用户可见不一致和运维耦合。

建议任务：

1. `create_deliverable` 保留 metadata，避免文件覆盖。
2. `Config` 拆分 API Key 必需/非必需加载路径。
3. 消除 `config.py` 与 `config/` 同名冲突。
4. 把 `tests/docuswarm` 扩到 CLI 只读命令、pipeline service、state manager 核心路径。
5. 清理 `ruff` 自动修复项。

验收标准：

- `ruff check autoBMAD/docuswarm tests/docuswarm` 不再有 F401/I001/W29x 基础错误。
- CLI `status/list/export` 在无 API Key 时可读取本地状态。
- 多文档产物 metadata 完整进入 execution report。

### P2：降低长期维护成本

目标：删代码、合并合同、让未来功能更便宜。

建议任务：

1. 合并 legacy / sdk 工具实现，保留一个 domain core + 两个薄适配器。
2. 拆分 `ContextValidator`、`StateManager`、`IndependentAgent`、`SessionManager`。
3. 删除或标记废弃的第二套执行循环。
4. 将 prompt/template mapping 规则从私有方法测试转为公开合同测试。

验收标准：

- 单个核心类控制在 300-500 行内。
- 工具族重复行数减少 40% 以上。
- 核心链路覆盖率达到 60%，总覆盖率达到 40% 以上。

## 建议 Backlog

| 优先级 | 项目 | 价值 | 风险降低 |
| --- | --- | --- | --- |
| P0 | 修复失败传播和 completed 判定 | 防止假成功 | 极高 |
| P0 | shared_context 端到端测试与修复 | 恢复跨节点协作记忆 | 极高 |
| P0 | 按配置生成 allowed_tools | 降低误编辑/误执行 shell 风险 | 极高 |
| P0 | DatabaseManager 按路径隔离 | 防止测试/多 pipeline 污染 | 高 |
| P1 | deliverable metadata 与文件冲突修复 | 提升多文档可靠性 | 高 |
| P1 | CLI 配置加载拆分 | 改善运维可用性 | 中 |
| P1 | ruff 基础清理 | 降低代码噪音 | 中 |
| P2 | 工具实现收敛 | 降低长期维护成本 | 中 |
| P2 | 巨型类拆分 | 降低变更耦合 | 中 |

## 不建议事项

- 不建议重写整个 DocuSwarm。当前问题集中在运行时合同和边界层，适合增量修复。
- 不建议先做大规模风格化重构。必须先用测试锁住失败传播、权限、shared_context。
- 不建议继续增加新的 Agent 能力，直到工具权限和 shared_context 链路可信。

## 最终判断

DocuSwarm 当前最值得投入的不是“更多功能”，而是把现有功能的运行合同钉牢：状态机必须诚实，工具权限必须可验证，共享上下文必须端到端可观测。只要 P0 链路修好，这个系统仍然适合继续演进；如果跳过 P0 继续叠功能，维护成本会快速变成产品层面的不稳定和不可解释输出。
