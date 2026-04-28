# DocuSwarm 文档一致性评估报告

**评估日期**: 2026-03-26  
**评估对象**: `autoBMAD/docuswarm`  
**评估口径**: 仅记录可由代码、CLI 行为或最小复现脚本直接证实的问题  
**参考文档范围**:
- `docs/PRD.md`
- `docs/architecture/*`
- `docs/design/README.md`
- `docs/research/README.md`
- `docs/research` 中 2026-03-17 / 2026-03-25 的关键对齐说明

## 结论摘要

当前实现并非“整体失效”，但与文档声明的目标态仍存在明显收口缺口。

- **总体结论**: `部分对齐`
- **确认存在的问题数量**: `2 个 Critical、1 个 High、2 个 Medium`
- **核心判断**:
  - 架构重构方向已经出现，但运行态、CLI 边界、状态读取和遗留能力清理尚未全部闭合
  - 当前更适合继续做“收口型重构”，不适合在现状下继续叠加新的产品叙事

## 已对齐内容

以下内容与文档方向基本一致:

- `create_pipeline_graph(session_manager=...)` 已按 F5 约束变为必填，执行主干不再默默缺省 SessionManager
- `PipelineAdapter` 已作为 pipeline 与 `node_execution` 之间的边界层接入
- 根目录 `nodes/*/node.yaml` 已具备 `task`、`template_title`、`output_filename` 等 BMM 风格关键字段
- `PipelineStateView` 与 `state_json` 相关读取能力已经存在，为 F2 收口打下基础
- `ContextManager`、`ContextFilter`、`IsolationAuditLogger` 等隔离组件已在代码中落地，说明设计方向不是空壳

## 评估方法

本次评估结合三类证据:

1. **静态审查**
   对照 PRD、Architecture、Design、Research 与当前代码实现，检查产品边界、状态语义、配置链路和迁移收口情况。

2. **行为验证**
   通过最小脚本和 CLI 命令验证状态读取行为、命令暴露情况、执行器异常路径以及环境变量消费情况。

3. **测试审阅**
   查看现有测试目录与测试意图，并尝试运行多组 pytest。

补充说明:

- 多组 pytest 被 `pytestqt` 默认临时目录权限问题阻断，这是环境限制，不足以直接判定这些测试本身失败。
- 本报告只保留可以直接证实的问题，不把“看起来像问题但尚未验证”的内容列为正式发现。

## 主要发现

### 1. Critical: LLM 配置链路断裂，真实执行路径会丢失上层配置

**文档期望**

- 文档主叙事强调 Kimi/Claude 路径应收敛为统一可控的 LLM 集成方式
- 运行时不应依赖多套互相冲突的环境变量口径

**代码证据**

- `pyproject.toml:32` 只声明了 `claude-agent-sdk`
- `autoBMAD/docuswarm/config.py:109`、`autoBMAD/docuswarm/config.py:139`、`autoBMAD/docuswarm/config.py:142` 仍从 `KIMI_API_KEY` / `KIMI_BASE_URL` 取值
- `autoBMAD/docuswarm/llm/session_manager.py:85`、`autoBMAD/docuswarm/llm/session_manager.py:86` 只读取 `CLAUDE_API_KEY` / `CLAUDE_BASE_URL`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:16`、`autoBMAD/docuswarm/pipeline/orchestrator.py:17` 仍直接依赖 `kaos.path` 与 `kimi_agent_sdk`
- `autoBMAD/docuswarm/cli/services/pipeline_service.py:60` 到 `autoBMAD/docuswarm/cli/services/pipeline_service.py:63` 的 `start()` 路径会把 `config.api_key` / `config.base_url` 传入 `HybridOrchestrator`
- `autoBMAD/docuswarm/cli/services/pipeline_service.py:88` 与 `autoBMAD/docuswarm/cli/services/pipeline_service.py:101` 的 `resume()` / `restart_from_node()` 路径没有继续传入这些配置
- `autoBMAD/docuswarm/agents/independent.py:552` 到 `autoBMAD/docuswarm/agents/independent.py:555` 以及 `autoBMAD/docuswarm/agents/independent.py:679` 到 `autoBMAD/docuswarm/agents/independent.py:682` 在执行时重新 new 了 `SessionManager`，但没有把 API key / base URL 继续透传

**直接验证**

- 在已设置 `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` 的环境下，新建 `SessionManager(work_dir=Path("."))` 后，其内部 `_api_key` / `_base_url` 仍为空
- 这说明文档主推的环境变量口径不会被该执行路径正确消费

**影响**

- `start()` 即便上层配置正确，进入 `IndependentAgent` 后也仍可能丢失配置
- `resume()` / `restart_from_node()` 更容易直接落入错误或缺失配置路径
- 最终会出现“模块可以 import，但真实节点运行无法稳定调用 LLM”的断层

**建议**

- 明确保留一套唯一环境变量口径，并在 `Config -> Orchestrator -> SessionManager -> Agent` 全链路透传
- 停止在 Agent 内部重新创建未继承连接配置的 `SessionManager`
- 对 `start / resume / restart_from_node` 三条入口补齐回归测试

### 2. Critical: 集成执行器异常后，节点仍会被写入 `completed_nodes`

**文档期望**

- F5 / Node Execution 文档明确反对 silent fallback 和 false success
- 节点失败时应显式暴露失败，而不是被当作成功完成

**代码证据**

- `autoBMAD/docuswarm/pipeline/graph.py:152` 到 `autoBMAD/docuswarm/pipeline/graph.py:159` 捕获集成执行器异常后，仅记录日志并把 `deliverables[node_id]` 写成空对象
- `autoBMAD/docuswarm/pipeline/graph.py:162` 到 `autoBMAD/docuswarm/pipeline/graph.py:167` 随后仍无条件递增迭代次数，并把该节点加入 `completed_nodes`

**直接验证**

通过最小复现脚本，patch `create_node_executor()` 令其抛出 `RuntimeError("boom")`，返回结果仍然表现为:

- `deliverables["analyst"] == {}`
- `completed_nodes == ["analyst"]`
- `node_iterations == {"analyst": 1}`

**影响**

- Pipeline 会把失败节点当作成功节点继续推进
- 后续节点会在错误上下文上继续执行，污染状态和交付物链
- 这与文档强调的“硬失败”“单一执行主干”“禁止静默降级”直接冲突

**建议**

- 执行器异常时显式标记失败，并阻止节点进入 `completed_nodes`
- 为该路径补一条强制性回归测试，防止再次出现 false success

### 3. High: CLI 仍是 pipeline-centric，未落到 PRD 要求的 node-centric 模型

**文档期望**

- `docs/PRD.md:138` 到 `docs/PRD.md:162` 要求 `docuswarm start <node> --context <file>`
- `docs/PRD.md:159` 到 `docs/PRD.md:161` 要求每次执行创建新的 `run_id`，并支持 `docuswarm runs <node>`
- `docs/architecture/01_SYSTEM_ARCHITECTURE.md:137` 到 `docs/architecture/01_SYSTEM_ARCHITECTURE.md:142` 也把 CLI 命令集合定义为 node-centric

**代码证据**

- `autoBMAD/docuswarm/cli/commands/start.py:15` 到 `autoBMAD/docuswarm/cli/commands/start.py:24` 的 `start` 命令没有 `<node>` 参数，只接收 `--context`
- `autoBMAD/docuswarm/cli/main.py:77` 到 `autoBMAD/docuswarm/cli/main.py:87` 注册了 `start/status/resume/cancel/...`，但没有 `runs`
- `autoBMAD/docuswarm/storage/state_manager.py:951` 到 `autoBMAD/docuswarm/storage/state_manager.py:1017` 实际已经存在 `list_node_runs()` 能力，但 CLI 没有暴露

**直接验证**

- `python -m autoBMAD.docuswarm start analyst --help` 显示的仍是 `start [OPTIONS]`
- `python -m autoBMAD.docuswarm runs --help` 返回 `No such command 'runs'`

**影响**

- 对外暴露的产品入口与 PRD/Architecture 主叙事不一致
- 用户无法按文档描述的方式管理 node run 与 run history
- 产品边界、测试边界、CLI 边界和状态模型没有形成统一口径

**建议**

- 尽快二选一收口
- 方案 A: 实现 node-centric CLI，并补齐 `runs`、run history、按 node 的状态与导出
- 方案 B: 正式修订 PRD / Architecture，把产品定义收回 pipeline-centric

### 4. Medium: `list_pipelines()` 仍读取顶层列，违反 F2 的 `state_json` 单一真相源约束

**文档期望**

- F2 强调状态读取应统一经由 `state_json` / `PipelineStateView` 收口

**代码证据**

- `autoBMAD/docuswarm/storage/state_manager.py:468` 到 `autoBMAD/docuswarm/storage/state_manager.py:505` 的 `list_pipelines()` 仍执行 `SELECT pipeline_id, subject, status, current_node ... FROM pipelines`
- 返回值直接使用 `row["status"]` 与 `row["current_node"]`

**直接验证**

最小脚本执行顺序如下:

1. `create_pipeline()` 创建记录
2. 仅调用 `update_pipeline_state({"status": "running", "current_node": "pm"})`

实际结果:

- `get_pipeline()` 返回 `running / pm`
- `list_pipelines()` 返回 `pending / None`

这说明 `list_pipelines()` 读取到的仍是过时顶层列，而不是 `state_json` 的真实值。

**影响**

- CLI `list` 命令可能向用户展示错误状态
- F2 的“统一读取语义”在列表视图上失效
- 状态层对外行为不一致，容易引发误判和运维成本上升

**建议**

- 让 `list_pipelines()` 也通过 `PipelineStateView` 或统一解析 `state_json` 展开字段
- 对 `get_pipeline()` 与 `list_pipelines()` 增加一致性回归测试

### 5. Medium: docs-free 清理尚未收口，代码中仍保留 docs 相关契约与示例

**文档期望**

- 2026-03-17 之后，多份设计与研究文档都在强调工作流不再读取 `docs/`
- 因此 docs 相关工具、上下文字段和 README 示例应同步收口

**代码证据**

- `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:15` 仍注册 `CreateDocumentSetTool`
- `autoBMAD/docuswarm/tools/update_context.py:21` 白名单仍包含 `doc_summaries.`
- `autoBMAD/docuswarm/node_execution/contracts.py:73` 仍保留 `docs_context`
- `autoBMAD/docuswarm/agents/independent.py:666` 仍向执行上下文传空的 `docs_context=[]`
- `autoBMAD/docuswarm/README.md:157`、`autoBMAD/docuswarm/README.md:158`、`autoBMAD/docuswarm/README.md:371` 仍以 `docs/...` 作为启动示例输入

**影响**

- 文档说“已移除或待移除”的能力，在代码与 README 中仍持续暴露
- 后续开发者容易误判系统边界，继续沿 docs-based 路径扩展
- 迁移收口工作难以判断何时真正完成

**建议**

- 如果 docs-free 已是正式产品决策，应统一清理工具、字段、示例和白名单
- 如果这些能力仍需保留，应同步修订 architecture / design / research，不再将其描述为“已移除”

## 对齐情况矩阵

| 维度 | 结论 | 说明 |
|------|------|------|
| F5 单一执行主干 | 部分对齐 | `session_manager` 必填已落地，但异常路径仍存在 false success |
| F2 `state_json` 单一真相源 | 部分对齐 | `get_pipeline()` / `PipelineStateView` 已收口，`list_pipelines()` 仍未收口 |
| Node-centric 产品边界 | 未对齐 | CLI 仍是 pipeline-centric，缺少 `runs` 命令 |
| docs-free 工作流 | 未对齐 | 工具、上下文字段、README 示例仍保留 docs 痕迹 |
| BMM 节点契约 | 基本对齐 | 根目录 `nodes/*/node.yaml` 已具备核心字段 |
| Context Isolation | 结构上对齐 | 组件存在，但本次未做端到端 LLM 隔离验证 |

## 正向观察

以下内容说明项目不是“方向错误”，而是“收口尚未完成”:

- 执行主干已经开始向单一路径靠拢
- 状态视图抽象已经建立，剩余问题更像是局部读取口径尚未统一
- 节点配置正在向 BMM 约束迁移，节点定义层面比预期更稳定
- 隔离与上下文管理组件已存在，后续可以在真实运行链路上继续做验证

## 优先级建议

### P0

1. 修复 `Config -> Orchestrator -> SessionManager -> Agent` 的配置透传链路，统一环境变量口径
2. 修复 `pipeline/graph.py` 的 false success 行为，禁止失败节点进入 `completed_nodes`

### P1

1. 对产品边界作最终决定: 实现 node-centric CLI，或同步修订 PRD / Architecture
2. 修复 `list_pipelines()`，确保列表读取与 `get_pipeline()` 使用同一真相源

### P2

1. 统一清理 docs-free 残余字段、工具和 README 示例
2. 为上述问题补齐回归测试，尤其是:
   - 执行器异常时不得进入 `completed_nodes`
   - `list_pipelines()` 与 `get_pipeline()` 必须读出同一状态
   - Agent 内部重建 `SessionManager` 时不得丢失 API 配置

## 验证记录

本次已直接验证的命令与行为包括:

- `python -m autoBMAD.docuswarm --version`
- `python -m autoBMAD.docuswarm list --help`
- `python -m autoBMAD.docuswarm start --help`
- `python -m autoBMAD.docuswarm start analyst --help`
- `python -m autoBMAD.docuswarm runs --help`
- 最小脚本验证 `list_pipelines()` 与 `get_pipeline()` 状态不一致
- 最小脚本验证集成执行器异常后仍写入 `completed_nodes`
- 最小脚本验证 `SessionManager` 不消费已设置的 `ANTHROPIC_*` 环境变量

pytest 尝试范围包括:

- `tests/storage`
- `tests/pipeline`
- `tests/architecture`
- `tests/node_execution`
- `tests/cli`
- `tests/agents`
- `tests/llm`
- `tests/tools`

结果说明:

- 多组测试被 `pytestqt` 临时目录权限问题阻断
- 这可以作为环境限制记录，但不能被用来证明这些测试逻辑本身失败

## 最终判断

DocuSwarm 当前最主要的问题不是“缺少方向”，而是**文档目标态、迁移中间态与真实运行态尚未彻底收口**。

如果只看代码组织，项目已经有明显的重构骨架；但如果从真实用户入口、失败语义、状态一致性和配置一致性来看，仍有几处关键断点没有闭合。

因此，当前最合理的推进方式是:

- 先完成配置链路、失败语义、状态读取和产品边界这几项收口
- 再决定是否继续扩展新的产品功能叙事
