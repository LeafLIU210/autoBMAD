# 2026-04-28 DocuSwarm 日志驱动深度审查报告

审查对象：`autoBMAD/docuswarm`

触发日志：`logs/docuswarm-2026-04-28.log`

审查时间：2026-04-28

审查方法：`systematic-debugging` 根因追踪 + `code-review-pro` 代码审查

## 结论摘要

本次日志对应的失败不是 Claude SDK transport、不是 API 凭证、也不是缺少 `evaluator.yaml` 文件本身。根因是 **节点配置目录的 root 语义分裂**：

- 节点配置真实位置是 `autoBMAD/nodes/{node_id}/...`。
- 运行时 `NodeExecutor` 把 repo root `/home/leafliu/autoBMAD` 作为 `project_root` 传给 Agent。
- `IndependentAgent`、`EvaluatorAgent`、`PersonaLoader`、`CriteriaLoader`、`PromptTemplateEngine` 又按 `project_root / "nodes"` 拼路径。
- 因此运行时访问的是不存在的 `/home/leafliu/autoBMAD/nodes/{node_id}/...`。

直接后果是五个节点全部在初始化阶段失败，且没有进入真实文档生成和评估。更严重的是，pipeline 状态仍被污染为：

- `completed_nodes` 包含全部五个节点
- `failed_nodes` 也包含全部五个节点
- `status` 为 `completed`
- `deliverables` 为空
- `error` 又保留失败信息

所以当前最高优先级不是继续调 LLM，而是先修复路径契约、节点状态契约和 `NodeConfig` schema 漂移。否则即使把路径改对，下一层也会因 `NodeConfig.task`、`evaluator.threshold`、`evaluator.max_iterations` 等不存在字段继续失败或静默退回默认值。

健康评分：32 / 100

优先级判断：

- P0：统一节点配置路径解析；修复失败节点被标记完成；补齐 `NodeConfig` schema 与消费者合同。
- P1：让 graph 具备依赖/失败短路；CLI 返回真实失败状态；补充运行时端到端测试。
- P2：收敛重复 loader；清理 fallback 静默吞错；补齐 summary cache 的输入语义。

## 日志事实

### 1. 上下文验证成功，说明输入文件不是根因

日志显示 pipeline 启动前的上下文验证通过：

- `logs/docuswarm-2026-04-28.log:5`：`single_prompt_start`
- `logs/docuswarm-2026-04-28.log:9`：`single_prompt_result ... "valid": true`
- `logs/docuswarm-2026-04-28.log:11`：`single_prompt_complete`

这排除了 “context 文件不可读或缺关键需求信息” 作为第一根因。

### 2. pipeline 创建成功，但引用文档总结为空

- `logs/docuswarm-2026-04-28.log:21`：创建 pipeline work dir。
- `logs/docuswarm-2026-04-28.log:23`：加载 summary agent 配置。
- `logs/docuswarm-2026-04-28.log:25`：`no_referenced_files_found`
- `logs/docuswarm-2026-04-28.log:27`：`documents_summarized count=0`

这不是本次 P0 根因，但说明 summary cache 没有从 `subject_context.context_file` 提取 `docs/calc-one-plus-one/calc-context.md`，只扫描 `content` 里的引用文件名。

### 3. 五个节点以同一模式失败

所有节点都先报 persona 路径错误，再报 evaluator 路径错误：

| 节点 | persona fallback | evaluator failure |
| --- | --- | --- |
| analyst | `logs/docuswarm-2026-04-28.log:39` | `logs/docuswarm-2026-04-28.log:43` |
| pm | `logs/docuswarm-2026-04-28.log:53` | `logs/docuswarm-2026-04-28.log:57` |
| ux | `logs/docuswarm-2026-04-28.log:67` | `logs/docuswarm-2026-04-28.log:71` |
| architect | `logs/docuswarm-2026-04-28.log:81` | `logs/docuswarm-2026-04-28.log:85` |
| po | `logs/docuswarm-2026-04-28.log:95` | `logs/docuswarm-2026-04-28.log:99` |

典型错误：

```text
Criteria file not found: /home/leafliu/autoBMAD/nodes/analyst/evaluator.yaml
```

但实际文件存在于：

```text
autoBMAD/nodes/analyst/evaluator.yaml
autoBMAD/nodes/analyst/persona.json
```

所以这是路径解析错误，不是配置文件缺失。

### 4. 最终状态自相矛盾

`logs/docuswarm-2026-04-28.log:101` 中的 result 同时包含：

```text
completed_nodes: ['analyst', 'pm', 'ux', 'architect', 'po']
failed_nodes: ['analyst', 'pm', 'ux', 'architect', 'po']
deliverables: {}
status: 'completed'
error: {'node_id': 'analyst', 'status': 'failed', ...}
```

这说明 graph 层和 finalizer 层仍在覆盖 adapter 层的失败语义。

## 最小复现

### 路径错误复现

命令：

```bash
.venv/bin/python -c "from pathlib import Path; from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import load_criteria; print(load_criteria('analyst', Path.cwd()))"
```

结果：

```text
FileNotFoundError: Criteria file not found: /home/leafliu/autoBMAD/nodes/analyst/evaluator.yaml
```

同一 loader 传入 `Path.cwd() / "autoBMAD"` 后成功：

```bash
.venv/bin/python -c "from pathlib import Path; from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import load_criteria; result=load_criteria('analyst', Path.cwd() / 'autoBMAD'); print(result['node_id'], len(result['criteria']), result['thresholds'])"
```

结果：

```text
analyst 5 {'approval': 0.7, 'escalation': 0.5}
```

### persona fallback 复现

repo root 作为 `project_root` 时：

```text
Default Agent General Assistant
```

`autoBMAD/` 作为 `project_root` 时：

```text
Analyst Data Analyst & Business Intelligence Specialist
```

这与日志中的 `Persona file not found, using default` 完全吻合。

### 下一层 schema 漂移复现

即使绕过 evaluator 初始化，运行时构建 IndependentAgent 输入也会失败：

```bash
.venv/bin/python -c "from autoBMAD.docuswarm.node_execution.context_builder import create_context_builder; from autoBMAD.docuswarm.context.isolation import ContextManager; ctx=create_context_builder().build('p','analyst',{'content':'x'}, repo_root=None); print(ctx['node_name']); print(ContextManager().build_independent_input(ctx))"
```

结果：

```text
AttributeError: 'NodeConfig' object has no attribute 'task'
Analyst
```

这证明当前日志暴露的是第一道失败门；修完路径后还会遇到 schema 合同断裂。

## 根因链路

### 入口链路

`PipelineService.start()`：

- 读取 context 文件并构造 `subject_context`：`autoBMAD/docuswarm/cli/services/pipeline_service.py:47`
- 创建 `SessionManager(work_dir=output)`：`autoBMAD/docuswarm/cli/services/pipeline_service.py:64`
- 创建 `HybridOrchestrator`：`autoBMAD/docuswarm/cli/services/pipeline_service.py:68`

`HybridOrchestrator.start_pipeline()`：

- 默认 `work_dir` 为 `autoBMAD/output`：`autoBMAD/docuswarm/pipeline/orchestrator.py:121`
- summary 阶段传入 `repo_root=Path(self._work_dir).parent`，即 `autoBMAD/`：`autoBMAD/docuswarm/pipeline/orchestrator.py:444`
- graph 执行创建静态五节点流水线：`autoBMAD/docuswarm/pipeline/orchestrator.py:470`

### 路径分裂发生点

`NodeExecutor` 计算 root：

- `auto_bmad_root = Path(__file__).parent.parent.parent.resolve()`：`autoBMAD/docuswarm/node_execution/executor.py:125`
- `repo_root = auto_bmad_root.parent if auto_bmad_root.name == "autoBMAD" else auto_bmad_root`：`autoBMAD/docuswarm/node_execution/executor.py:126`
- 传给 `create_dual_agent_node(... project_root=repo_root)`：`autoBMAD/docuswarm/node_execution/executor.py:147`

这里的 `repo_root` 是 `/home/leafliu/autoBMAD`。

但 Agent loader 的假设是 `project_root / "nodes"`：

- `PersonaLoader.load()`：`autoBMAD/docuswarm/agents/persona.py:135` 到 `autoBMAD/docuswarm/agents/persona.py:139`
- `EvaluatorAgent._load_criteria()`：`autoBMAD/docuswarm/agents/evaluator.py:99` 到 `autoBMAD/docuswarm/agents/evaluator.py:142`
- `CriteriaLoader.load()`：`autoBMAD/docuswarm/agents/evaluator_config/criteria_loader.py:64` 到 `autoBMAD/docuswarm/agents/evaluator_config/criteria_loader.py:86`
- `PromptTemplateEngine._load_persona()`：`autoBMAD/docuswarm/prompts/template_engine.py:119`
- `NodePromptContractBuilder._build_persona_section()` 没传 project root，默认 `Path.cwd()`：`autoBMAD/docuswarm/prompts/contract_builder.py:153`

这使 runtime 访问 `/home/leafliu/autoBMAD/nodes/...`，与真实目录 `autoBMAD/nodes/...` 不一致。

### 同一链路中存在正确实现

`NodeLoader` 的默认路径是正确的：

- `_get_base_path()` 默认返回 `Path(__file__).parent.parent`，即包内 `autoBMAD/`：`autoBMAD/nodes/loader.py:136`
- `NodeLoader.load()` 读取 `base_path / "nodes" / node_id`：`autoBMAD/nodes/loader.py:157`

`NodeExecutionContextBuilder` 已经通过 `NodeLoader` 正确读到节点名：

- `node_config = self.loader.load(node_id)`：`autoBMAD/docuswarm/node_execution/context_builder.py:56`
- 日志也出现 `execution_context_built node_name=Analyst`：`logs/docuswarm-2026-04-28.log:35`

因此根因不是 “没有 canonical loader”，而是 canonical loader 没有贯穿到 Agent、Prompt、Evaluator 的所有消费者。

## 关键发现

### P0-1：节点配置 root 语义不统一，导致所有节点初始化失败

严重性：Critical

证据：

- 日志五个节点全部访问 `/home/leafliu/autoBMAD/nodes/{node}/evaluator.yaml` 并失败。
- 实际文件位于 `autoBMAD/nodes/{node}/evaluator.yaml`。
- `NodeExecutor` 把 repo root 传给 Agent：`autoBMAD/docuswarm/node_execution/executor.py:151`。
- `EvaluatorAgent` 按 `project_root / "nodes"` 拼路径：`autoBMAD/docuswarm/agents/evaluator.py:139`。

影响：

- 当前 pipeline 完全无法生成任何节点交付物。
- `IndependentAgent` 会悄悄退回 `Default Agent`，即使 evaluator 路径修复前不致命，也会造成角色上下文丢失。
- 路径语义在代码中被多处注释“修复”过，但各模块对 `project_root` 的解释相互冲突。

建议：

1. 建立单一 `NodeConfigResolver` 或复用 `NodeLoader`，所有 persona、evaluator、prompt template 统一从它读取。
2. 明确命名两个 root：`repo_root` 与 `package_root`，不要再用含糊的 `project_root`。
3. `PersonaLoader` 不应在生产主路径默认吞掉缺失文件；至少节点主路径应 fail-fast。
4. 增加测试：从 repo root 启动 `NodeExecutor("analyst")` 时必须能加载真实 persona/evaluator。

### P0-2：失败节点被 graph 层重新加入 `completed_nodes`

严重性：Critical

证据：

- `NodeExecutor` 捕获异常后设置 `new_state["status"] = FAILED`：`autoBMAD/docuswarm/node_execution/executor.py:235`
- `PipelineAdapter.convert_node_to_pipeline_state()` 已经只在 `COMPLETED` 时加入 `completed_nodes`，否则加入 `failed_nodes`：`autoBMAD/docuswarm/node_execution/pipeline_adapter.py:322`
- 但 graph 层之后无条件执行：
  - 递增 iteration：`autoBMAD/docuswarm/pipeline/graph.py:146`
  - 加入 `completed_nodes`：`autoBMAD/docuswarm/pipeline/graph.py:150`
- 日志结果中五个节点同时出现在 `completed_nodes` 和 `failed_nodes`：`logs/docuswarm-2026-04-28.log:101`

影响：

- 用户、CLI、checkpoint、后续恢复逻辑无法相信 `completed_nodes`。
- 下游节点会在上游失败后继续运行，产生级联失败。
- 空 `deliverables` 与全量 `completed_nodes` 并存，破坏状态机不变量。

建议：

1. 删除 graph 层无条件加入 completed 的逻辑，只信任 `PipelineAdapter`。
2. `node_status != COMPLETED` 时立即停止顺序执行，进入 failed/paused finalizer。
3. 增加状态不变量测试：
   - failed node 不得进入 `completed_nodes`
   - `completed_nodes` 必须是 `deliverables.keys()` 的子集
   - `status=completed` 时 `failed_nodes` 必须为空

### P0-3：finalizer 无条件把失败 pipeline 标记为 completed

严重性：Critical

证据：

- `finalize_pipeline_state()` 无条件 `result["status"] = COMPLETED`：`autoBMAD/docuswarm/pipeline/state.py:285` 到 `autoBMAD/docuswarm/pipeline/state.py:310`
- `HybridOrchestrator._determine_final_status()` 只在 graph 返回后修正数据库状态：`autoBMAD/docuswarm/pipeline/orchestrator.py:152`
- 但日志记录的 graph result 仍是 `status='completed'`：`logs/docuswarm-2026-04-28.log:101`

影响：

- DB 状态、LangGraph checkpoint、日志 result 可能不一致。
- resume/export/status 如果读取不同来源，会给出不同答案。
- 事故分析困难：日志一边说 completed，一边携带 error。

建议：

1. finalizer 根据 `failed_nodes`、`error`、`completed_nodes`、`PIPELINE_NODES` 共同判定最终状态。
2. finalizer 不应修正失败为成功，应该成为状态完整性守门人。
3. `validate_state()` 当前只检查 completed 是否是 deliverable 子集，但真实 graph 绕过了它；应在 finalizer 和测试中强制调用。

### P0-4：`NodeConfig` schema 与生产消费者不一致，路径修复后仍会失败

严重性：Critical

证据：

`NodeConfig` dataclass 当前字段：

- 有 `deliverable`、`agent`、`questions`、`dependencies`、`evaluator`、`persona`、`tool_permissions`：`autoBMAD/nodes/loader.py:102`
- 没有 `task` 字段。

但生产代码大量读取 `node_config.task`：

- `ContextManager.build_independent_input()`：`autoBMAD/docuswarm/context/isolation.py:170`
- `ContextManager.build_evaluator_input()`：`autoBMAD/docuswarm/context/isolation.py:233`
- `NodePromptContractBuilder`：`autoBMAD/docuswarm/prompts/contract_builder.py:166`、`autoBMAD/docuswarm/prompts/contract_builder.py:189`、`autoBMAD/docuswarm/prompts/contract_builder.py:744`

最小复现已经证明 `ContextManager().build_independent_input(ctx)` 会抛：

```text
AttributeError: 'NodeConfig' object has no attribute 'task'
```

此外，`NodeEvaluatorConfig` 只有 `criteria` 和 `thresholds`：

- `autoBMAD/nodes/loader.py:95`
- `autoBMAD/nodes/loader.py:326`

但消费者读取不存在字段：

- `node_config.evaluator.threshold`：`autoBMAD/docuswarm/agents/evaluator.py:198`
- `node_config.evaluator.threshold`：`autoBMAD/docuswarm/pipeline/quality.py:106`
- `node_config.evaluator.max_iterations`：`autoBMAD/docuswarm/nodes/dual_agent.py:860`

影响：

- 路径修复之后，节点会在构建 prompt/context 时继续失败。
- 阈值和最大迭代次数可能静默退回默认值，导致配置文件修改不生效。
- 测试只覆盖 import 和 tool_permissions，无法捕捉 schema 断裂。

建议：

1. 让 `NodeConfig` 显式包含 `task: NodeTaskConfig`，并从 `node.yaml` 加载。
2. 统一字段名：要么全系统用 `thresholds`，要么迁移到 `threshold` 并保留兼容层。
3. 若需要 `max_iterations`，应加入 `NodeEvaluatorConfig` 并从 `evaluator.yaml` 读取。
4. 移除生产主路径中的裸 `except Exception` fallback；至少记录错误类型并让测试可断言。

### P1-1：graph 没有依赖短路，导致上游失败后下游继续执行

严重性：High

证据：

- graph 固定连线 `analyst -> pm -> ux -> architect -> po`：`autoBMAD/docuswarm/pipeline/graph.py:224`
- `HybridOrchestrator._check_dependencies()` 存在但未参与 graph 执行：`autoBMAD/docuswarm/pipeline/orchestrator.py:328`
- 日志显示 analyst 失败后，pm、ux、architect、po 仍依次启动并失败：`logs/docuswarm-2026-04-28.log:45`、`logs/docuswarm-2026-04-28.log:59`、`logs/docuswarm-2026-04-28.log:73`、`logs/docuswarm-2026-04-28.log:87`

影响：

- 一个 root cause 被放大成五个节点错误。
- 下游节点在缺少上游 deliverable 时运行，没有业务意义。
- 日志噪声增加，用户更难定位第一失败点。

建议：

1. LangGraph 节点后使用 conditional edge：completed 才进入下一节点，failed/blocking question 进入终止或暂停。
2. `_check_dependencies()` 要么接入 graph，要么删除，避免形成“看起来有依赖检查”的假安全感。
3. 节点失败时记录 `first_failed_node`，后续节点应标记为 `skipped_due_to_dependency`，而不是 `failed`。

### P1-2：CLI 对失败 pipeline 仍输出 “Pipeline started”

严重性：High

证据：

- `PipelineService.start()` 只返回 `orchestrator.start_pipeline()` 的 pipeline id：`autoBMAD/docuswarm/cli/services/pipeline_service.py:75`
- `start` 命令只要拿到 id 就打印 `Pipeline started`：`autoBMAD/docuswarm/cli/commands/start.py:29`
- `HybridOrchestrator.start_pipeline()` 在 graph result 失败时仍返回 pipeline id，不抛出或返回状态：`autoBMAD/docuswarm/pipeline/orchestrator.py:478`

影响：

- 用户看到的是启动成功，而不是执行失败。
- 自动化脚本无法通过 CLI exit code 判断 pipeline 是否产出交付物。
- 与日志中的空 `deliverables` 形成产品层误导。

建议：

1. `start_pipeline()` 返回 `{pipeline_id, status, failed_nodes, error}` 或在同步执行失败时抛出领域异常。
2. CLI 输出 “Pipeline failed to execute” 并保留 pipeline id 供排查。
3. 增加 CLI 行为测试：节点初始化失败时 exit code 非 0，或至少明确显示 failed。

### P1-3：SummaryAgent 没有把 `context_file` 当作引用文档

严重性：Medium

证据：

- `subject_context` 明确包含 `context_file='docs/calc-one-plus-one/calc-context.md'`：`logs/docuswarm-2026-04-28.log:3`
- SummaryAgent 只从 `original_context["content"]` 中正则提取文件名：`autoBMAD/docuswarm/agents/summary.py:257`
- 因此日志显示 `no_referenced_files_found`：`logs/docuswarm-2026-04-28.log:25`

影响：

- 当前任务内容已经内联在 `content` 中，所以不是 P0。
- 但对于“context_file 指向主需求文档，content 只包含短描述”的调用方式，summary cache 会漏掉最重要文档。

建议：

1. SummaryAgent 应同时支持 `context_file`、显式 `referenced_files`、content 内引用三种来源。
2. 同一个解析函数应被 SummaryAgent 和 ContextBuilder 复用，避免两套正则逻辑漂移。

### P1-4：测试集覆盖的是 import 和 NodeLoader 局部，不覆盖真实 runtime 合同

严重性：High

证据：

当前 `tests/` 只有三个测试文件：

- `tests/test_docuswarm_nodes_import.py`
- `tests/test_node_config_tool_permissions.py`
- `tests/test_nodes_loader_symbols.py`

已执行：

```bash
.venv/bin/python -m pytest tests/test_docuswarm_nodes_import.py tests/test_node_config_tool_permissions.py tests/test_nodes_loader_symbols.py -q
```

结果：

```text
25 passed
TOTAL 8331 statements, 21% coverage
```

这些测试能证明 import 链和 `NodeLoader.load()` 局部可用，但不能证明：

- `NodeExecutor` 从 repo root 启动能加载 Agent persona/evaluator。
- `ContextManager` 能从 `NodeConfig` 构建 `IndependentAgentInput`。
- failed node 不会进入 `completed_nodes`。
- CLI 能暴露失败状态。

建议：

1. 增加不调用 LLM 的 runtime contract tests，用 fake agents/session manager 覆盖 graph。
2. 增加 `NodeConfig` consumer contract test：枚举所有消费者读取的字段，确保 dataclass 存在。
3. 对 `logs/docuswarm-2026-04-28.log` 这种场景固化回归：缺路径时只失败 analyst，并且 pipeline status 为 failed。

## 系统性调试阶段记录

### Phase 1：根因调查

已完成：

- 读取完整错误日志，定位第一处节点失败为 analyst evaluator path。
- 验证五个节点失败模式相同。
- 验证真实文件在 `autoBMAD/nodes`。
- 用最小命令复现 repo root 读取失败、package root 读取成功。

结论：第一根因是 root 语义分裂。

### Phase 2：模式分析

已完成：

- 找到工作模式：`NodeLoader.load()` 以 `autoBMAD/` 为 base path 正确加载。
- 找到破坏模式：Agent/Prompt/Evaluator 重复按 `project_root / "nodes"` 拼路径。
- 找到下一层 schema 漂移：消费者使用 `task`、`threshold`、`max_iterations`，dataclass 不提供。

结论：问题不是单点路径 typo，而是“节点配置读取”没有单一事实来源。

### Phase 3：假设与测试

假设：

> 我认为所有节点失败的根因是 `project_root` 在 `NodeExecutor` 中表示 repo root，但在 Agent loader 中被解释为包内 root；因此 evaluator 路径漏掉了中间的 `autoBMAD/`。

测试结果：

- `load_criteria('analyst', Path.cwd())` 失败。
- `load_criteria('analyst', Path.cwd() / 'autoBMAD')` 成功。
- `PersonaLoader.load('analyst', Path.cwd())` 返回默认 persona。
- `PersonaLoader.load('analyst', Path.cwd() / 'autoBMAD')` 返回真实 Analyst persona。

假设成立。

### Phase 4：实施建议

本次任务要求创建审查报告，未修改生产代码。建议按 TDD 顺序修复：

1. 先写失败测试：repo root 启动 agent/node executor 能加载真实节点配置。
2. 实现统一 resolver：所有 Agent/Prompt/Evaluator 改用 `NodeLoader` 或同一 `NodeConfigResolver`。
3. 写失败测试：`ContextManager.build_independent_input()` 不抛 `NodeConfig.task` 缺失。
4. 补齐 `NodeConfig.task`、`NodeEvaluatorConfig.thresholds/max_iterations` 合同。
5. 写失败测试：failed node 不进入 `completed_nodes`，final status 为 failed。
6. 修 graph 和 finalizer 状态语义。
7. 写 CLI 测试：同步执行失败时用户能看到 failed，不误报 started/completed。

## 建议修复路线

### P0 Sprint：让 pipeline 真实失败或真实成功

目标：同一 context 文件运行时，要么生成五个交付物，要么在第一失败点明确 failed，不能再出现 completed/failed 双写。

任务：

1. 新增 `resolve_package_root()` / `resolve_repo_root()`，禁止隐式 `Path.cwd()`。
2. `PersonaLoader`、`EvaluatorAgent`、`CriteriaLoader`、`PromptTemplateEngine` 统一使用 `NodeLoader` 或统一 resolver。
3. `NodeConfig` 补齐 `task`，并让 `node.yaml` 的任务字段成为必填或有明确 fallback。
4. 修复 `threshold`/`thresholds` 和 `max_iterations` 字段读取。
5. graph 删除无条件 completed 写入。
6. finalizer 根据失败状态判定 `FAILED`。

验收：

- analyst 初始化不再找 `/home/leafliu/autoBMAD/nodes/...`。
- 任何节点失败时，`completed_nodes` 不包含该节点。
- `status=completed` 时 `deliverables` 至少包含所有 `PIPELINE_NODES`。

### P1 Sprint：恢复可观测性和用户信任

任务：

1. CLI start 输出最终同步执行状态。
2. 状态导出和日志统一使用 graph 修正后的 final state。
3. 下游节点依赖失败时标记 skipped。
4. SummaryAgent 支持 `context_file` 作为显式文档来源。

验收：

- 日志中有 `first_failed_node`。
- CLI 对当前日志场景显示 failed，而不是单纯 “Pipeline started”。
- summary cache 对 `context_file` 有确定行为。

### P2 Sprint：降低重复实现风险

任务：

1. 收敛重复 loader：`PersonaLoader` 和 `CriteriaLoader` 不再各自拼路径。
2. 删除或隔离旧 legacy prompt/template 路径。
3. 给 `NodeConfig` consumers 建立合同测试，禁止字段漂移。

## 已执行验证

```text
nl -ba logs/docuswarm-2026-04-28.log
读取完整 102 行日志，确认失败模式。

.venv/bin/python -m pytest tests/test_docuswarm_nodes_import.py tests/test_node_config_tool_permissions.py tests/test_nodes_loader_symbols.py -q
结果：25 passed，覆盖率 21%。

.venv/bin/python -c "... load_criteria('analyst', Path.cwd()) ..."
结果：复现 FileNotFoundError，路径为 /home/leafliu/autoBMAD/nodes/analyst/evaluator.yaml。

.venv/bin/python -c "... load_criteria('analyst', Path.cwd() / 'autoBMAD') ..."
结果：成功读取 5 条 criteria 和 thresholds。

.venv/bin/python -c "... ContextManager().build_independent_input(ctx) ..."
结果：复现 AttributeError: 'NodeConfig' object has no attribute 'task'。
```

注意：系统 `python` 不存在，系统 `python3` 未安装 pytest；最终使用项目 `.venv/bin/python` 完成测试。

## 最终判断

当前 `autoBMAD/docuswarm` 的失败不是单个文件缺失，而是配置路径、节点 schema、graph 状态机三条合同同时不闭环。最小修补不应是“把 repo root 改成 autoBMAD root”这一行，因为那只会打开下一层 `NodeConfig.task` 失败。正确修复应以 `NodeLoader`/resolver 为中心，把节点配置变成真正单一事实来源，再收紧 graph 的失败传播语义。

在修复前，不建议把当前 pipeline 运行结果视为有效文档流水线验证；它只验证了 context validation 能跑通，尚未验证任何业务节点能完成交付。
