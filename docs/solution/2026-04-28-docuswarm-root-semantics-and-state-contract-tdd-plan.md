# DocuSwarm 根语义与状态契约修复 — 测试驱动方案

> 来源：`docs-doc/evaluation/2026-04-28-docuswarm-log-driven-deep-review.md`
>
> 目标：按 P0 → P1 → P2 顺序，以“先写失败测试、再修实现、再补回归”的 TDD 节奏，修复节点配置路径分裂、`NodeConfig` schema 漂移、graph 状态机双写三条合同断裂。

---

## 目录

1. [方案总览](#方案总览)
2. [P0 Sprint：让 Pipeline 真实失败或真实成功](#p0-sprint-让-pipeline-真实失败或真实成功)
   - [P0-T1：路径解析统一测试](#p0-t1-路径解析统一测试)
   - [P0-T2：NodeConfig Schema 补齐测试](#p0-t2-nodeconfig-schema-补齐测试)
   - [P0-T3：Graph 状态机不变量测试](#p0-t3-graph-状态机不变量测试)
   - [P0-T4：Finalizer 状态判定测试](#p0-t4-finalizer-状态判定测试)
   - [P0-T5：端到端初始化契约测试](#p0-t5-端到端初始化契约测试)
3. [P1 Sprint：恢复可观测性和用户信任](#p1-sprint-恢复可观测性和用户信任)
   - [P1-T1：依赖失败短路测试](#p1-t1-依赖失败短路测试)
   - [P1-T2：CLI 失败状态暴露测试](#p1-t2-cli-失败状态暴露测试)
   - [P1-T3：SummaryAgent context_file 解析测试](#p1-t3-summaryagent-context_file-解析测试)
   - [P1-T4：Runtime Contract 回归测试](#p1-t4-runtime-contract-回归测试)
4. [P2 Sprint：降低重复实现风险](#p2-sprint-降低重复实现风险)
   - [P2-T1：Loader 收敛与单一事实来源测试](#p2-t1-loader-收敛与单一事实来源测试)
   - [P2-T2：NodeConfig 消费者合同测试](#p2-t2-nodeconfig-消费者合同测试)
   - [P2-T3：Legacy 路径隔离测试](#p2-t3-legacy-路径隔离测试)
5. [测试执行与回归策略](#测试执行与回归策略)
6. [验收标准](#验收标准)

---

## 方案总览

### 核心问题

本次审查发现三条并行的合同断裂：

| 维度 | 根因 | 当前表现 |
|------|------|----------|
| **配置路径** | `project_root` 在 `NodeExecutor` 中表示 repo root，在 Agent loader 中被解释为 `project_root / "nodes"` | 运行时访问 `/home/leafliu/autoBMAD/nodes/...`，实际文件在 `autoBMAD/nodes/...` |
| **Schema 漂移** | `NodeConfig` 缺少 `task`、`evaluator.threshold`、`evaluator.max_iterations` | 路径修复后仍会因 `AttributeError` 失败，或静默退回默认值 |
| **状态机双写** | graph 层无条件把节点加入 `completed_nodes`，finalizer 无条件标记 `COMPLETED` | 五个失败节点同时出现在 `completed_nodes` 和 `failed_nodes`，`status='completed'` 与空 `deliverables` 并存 |

### TDD 节奏

```
红 → 绿 → 重构（每个 Sprint 内部循环）
   ↓
P0 Sprint：先写失败测试暴露根因 → 修复实现 → 测试变绿
P1 Sprint：在 P0 绿的基础上写新失败测试 → 修复 → 绿
P2 Sprint：收敛与清理 → 绿
```

### 命名约定

- 测试文件：`tests/test_docuswarm_p0_path_resolution.py`
- 测试函数：`test_{模块}_{场景}_{预期行为}`
- 辅助 Fixture：`conftest.py` 中提供 `fake_node_config`、`mock_project_root`、`temp_nodes_dir`

---

## P0 Sprint：让 Pipeline 真实失败或真实成功

> **目标**：同一 context 文件运行时，要么生成五个交付物，要么在第一失败点明确 `failed`，不能再出现 `completed`/`failed` 双写。

---

### P0-T1：路径解析统一测试

**对应修复**：`NodeExecutor`、`PersonaLoader`、`CriteriaLoader`、`PromptTemplateEngine`、`EvaluatorAgent` 统一使用 `NodeLoader` 或单一 `NodeConfigResolver`。

#### 测试 T1.1：`test_criteria_loader_from_repo_root_fails`

- **前置条件**：
  - 当前工作目录为 `/home/leafliu/autoBMAD`（repo root）。
  - `autoBMAD/nodes/analyst/evaluator.yaml` 存在且有效。
- **步骤**：
  ```python
  from pathlib import Path
  from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import load_criteria
  load_criteria("analyst", Path.cwd())
  ```
- **预期结果（修复前）**：
  - 抛出 `FileNotFoundError`，路径为 `/home/leafliu/autoBMAD/nodes/analyst/evaluator.yaml`。
- **预期结果（修复后）**：
  - 成功返回字典，包含 `node_id='analyst'`、`criteria` 列表、`thresholds` 字典。

#### 测试 T1.2：`test_persona_loader_from_repo_root_returns_real_persona`

- **前置条件**：同上。
- **步骤**：
  ```python
  from autoBMAD.docuswarm.agents.persona import PersonaLoader
  persona = PersonaLoader.load("analyst", project_root=Path.cwd())
  ```
- **预期结果（修复前）**：
  - 返回默认 persona，角色为 `"Default Agent General Assistant"`。
- **预期结果（修复后）**：
  - 返回真实 persona，角色为 `"Analyst Data Analyst & Business Intelligence Specialist"`。

#### 测试 T1.3：`test_node_executor_initialization_loads_real_evaluator_and_persona`

- **前置条件**：
  - 使用真实文件系统，不 mock loader。
  - 从 repo root 启动。
- **步骤**：
  ```python
  from autoBMAD.docuswarm.node_execution.executor import NodeExecutor
  executor = NodeExecutor("analyst", context={"content": "test"})
  ```
- **断言**：
  - `executor._evaluator is not None`
  - `executor._evaluator.criteria` 非空列表
  - `executor._persona.name` 不等于 `"Default Agent"`

#### 测试 T1.4：`test_no_implicit_path_cwd_fallback_in_production`

- **目标**：禁止生产主路径默认回退到 `Path.cwd()`。
- **步骤**：
  - 调用 `CriteriaLoader.load("analyst")`（不传 `project_root`）。
- **断言**：
  - 抛出 `TypeError` 或 `ValueError`，要求显式传入 `package_root` / `repo_root`。

---

### P0-T2：NodeConfig Schema 补齐测试

**对应修复**：`NodeConfig` 显式包含 `task: NodeTaskConfig`；统一 `threshold`/`thresholds`；`NodeEvaluatorConfig` 加入 `max_iterations`。

#### 测试 T2.1：`test_node_config_has_task_attribute`

- **前置条件**：
  - `autoBMAD/nodes/analyst/node.yaml` 包含 `task` 字段。
- **步骤**：
  ```python
  from autoBMAD.nodes.loader import NodeLoader
  config = NodeLoader().load("analyst")
  ```
- **断言**：
  - `hasattr(config, "task")` 为 `True`
  - `config.task.name` 非空（或按实际 schema）

#### 测试 T2.2：`test_context_manager_build_independent_input_does_not_raise_on_task`

- **前置条件**：
  - 使用真实 `NodeLoader` 加载的 `NodeConfig`。
- **步骤**：
  ```python
  from autoBMAD.docuswarm.node_execution.context_builder import create_context_builder
  from autoBMAD.docuswarm.context.isolation import ContextManager
  ctx = create_context_builder().build("pipeline-1", "analyst", {"content": "x"}, repo_root=None)
  result = ContextManager().build_independent_input(ctx)
  ```
- **预期结果（修复前）**：
  - 抛出 `AttributeError: 'NodeConfig' object has no attribute 'task'`
- **预期结果（修复后）**：
  - 返回字典，包含 `task` 相关字段。

#### 测试 T2.3：`test_node_evaluator_config_has_threshold_and_max_iterations`

- **步骤**：
  ```python
  config = NodeLoader().load("analyst")
  ```
- **断言**：
  - `hasattr(config.evaluator, "threshold")` 或 `hasattr(config.evaluator, "thresholds")`（按统一后的命名）
  - `hasattr(config.evaluator, "max_iterations")`
  - `config.evaluator.max_iterations >= 1`

#### 测试 T2.4：`test_thresholds_loaded_from_evaluator_yaml`

- **目标**：确保配置文件的修改能反映到运行时。
- **步骤**：
  - 读取 `autoBMAD/nodes/analyst/evaluator.yaml`。
  - 对比 `NodeLoader().load("analyst").evaluator.thresholds`。
- **断言**：
  - YAML 中的 `approval` 和 `escalation` 值与 dataclass 实例一致。

---

### P0-T3：Graph 状态机不变量测试

**对应修复**：删除 graph 层无条件加入 `completed_nodes` 的逻辑；`node_status != COMPLETED` 时停止顺序执行。

#### 测试 T3.1：`test_failed_node_not_in_completed_nodes`

- **前置条件**：
  - 使用 mock `NodeExecutor`，让它对 `analyst` 抛出异常。
- **步骤**：
  - 运行 graph 到 `analyst` 节点。
- **断言**：
  - `state.failed_nodes` 包含 `"analyst"`
  - `state.completed_nodes` **不包含** `"analyst"`

#### 测试 T3.2：`test_completed_nodes_is_subset_of_deliverables_keys`

- **断言**：
  ```python
  set(state.completed_nodes) <= set(state.deliverables.keys())
  ```

#### 测试 T3.3：`test_status_completed_implies_empty_failed_nodes`

- **断言**：
  ```python
  if state.status == "completed":
      assert len(state.failed_nodes) == 0
      assert set(state.completed_nodes) == set(state.deliverables.keys())
  ```

#### 测试 T3.4：`test_first_failed_node_stops_sequential_execution`

- **前置条件**：
  - 静态流水线：`analyst -> pm -> ux -> architect -> po`
  - `analyst` 模拟失败。
- **步骤**：
  - 启动 graph 执行。
- **断言**：
  - `pm`、`ux`、`architect`、`po` 均**未执行**（或标记为 `skipped`）。
  - `state.first_failed_node == "analyst"`

---

### P0-T4：Finalizer 状态判定测试

**对应修复**：`finalize_pipeline_state()` 根据 `failed_nodes`、`error`、`completed_nodes`、`PIPELINE_NODES` 共同判定最终状态。

#### 测试 T4.1：`test_finalizer_marks_failed_when_failed_nodes_present`

- **前置条件**：
  - 构造一个包含 `failed_nodes=['analyst']` 的中间状态。
- **步骤**：
  - 调用 `finalize_pipeline_state()`。
- **断言**：
  - `result["status"] == "failed"`
  - `result["error"]` 非空

#### 测试 T4.2：`test_finalizer_validates_state_invariants`

- **目标**：`validate_state()` 在 finalizer 中被强制调用。
- **步骤**：
  - 构造违反不变量的状态（如 `completed_nodes` 含 `analyst` 但 `deliverables` 不含）。
- **断言**：
  - 抛出 `PipelineStateError` 或类似异常，而不是静默修正为 `completed`。

#### 测试 T4.3：`test_finalizer_completed_requires_all_pipeline_nodes`

- **前置条件**：
  - `PIPELINE_NODES = ['analyst', 'pm', 'ux', 'architect', 'po']`
  - 全部成功且 `deliverables` 包含五个节点产出。
- **断言**：
  - `result["status"] == "completed"`
  - `len(result["deliverables"]) == 5`

---

### P0-T5：端到端初始化契约测试

**目标**：不调用 LLM，验证从 repo root 启动 `NodeExecutor("analyst")` 时，所有初始化依赖都能解析。

#### 测试 T5.1：`test_analyst_node_executor_from_repo_root`

- **步骤**：
  ```python
  executor = NodeExecutor("analyst", context={"content": "calc 1+1"})
  ```
- **断言**：
  - `executor._evaluator.criteria` 长度 > 0
  - `executor._persona.name` == "Analyst"
  - `executor._node_config.task` 存在

#### 测试 T5.2：`test_all_pipeline_nodes_initializable`

- **步骤**：
  - 对 `PIPELINE_NODES` 中每个 `node_id` 实例化 `NodeExecutor`。
- **断言**：
  - 无一抛出 `FileNotFoundError` 或 `AttributeError`。

#### 测试 T5.3：`test_log_scenario_regression`

- **目标**：固化 `logs/docuswarm-2026-04-28.log` 场景的回归。
- **前置条件**：
  - 模拟与日志相同的输入 context。
  - 使用真实文件系统，但**不**调用 LLM（mock `IndependentAgent` / `EvaluatorAgent` 的执行方法）。
- **步骤**：
  - 调用 `HybridOrchestrator.start_pipeline()`。
- **断言（修复前）**：
  - `result.status == 'completed'`（错误）
  - `result.failed_nodes` 包含全部五个节点（错误）
  - `result.completed_nodes` 包含全部五个节点（错误）
- **断言（修复后）**：
  - `result.status == 'failed'`
  - `result.first_failed_node == 'analyst'`
  - `result.failed_nodes == ['analyst']`（若实现短路）
  - `result.completed_nodes == []`
  - `result.deliverables == {}`

---

## P1 Sprint：恢复可观测性和用户信任

> **目标**：CLI 能报告真实失败；graph 能在上游失败后短路；SummaryAgent 不遗漏 `context_file`；测试覆盖 runtime contract。

---

### P1-T1：依赖失败短路测试

**对应修复**：LangGraph 节点后使用 conditional edge；`_check_dependencies()` 接入 graph 或删除；下游节点标记 `skipped_due_to_dependency`。

#### 测试 T1.1：`test_downstream_nodes_skipped_on_dependency_failure`

- **前置条件**：
  - `analyst` 失败，`pm` 依赖 `analyst`。
- **步骤**：
  - 执行 graph。
- **断言**：
  - `pm` 的状态为 `skipped` 或 `skipped_due_to_dependency`。
  - `pm` 不调用 LLM，不执行 evaluator。

#### 测试 T1.2：`test_no_cascade_failure_noise_in_logs`

- **目标**：日志中只记录一个真实失败，其余是 `skipped`。
- **断言**：
  - 日志中 `node_failed` 事件仅出现 1 次（`analyst`）。
  - `node_skipped` 事件出现 4 次。

#### 测试 T1.3：`test_conditional_edge_respects_status`

- **目标**：验证 LangGraph conditional edge 逻辑。
- **步骤**：
  - 对 `COMPLETED`、`FAILED`、`BLOCKED` 三种状态分别调用 edge 函数。
- **断言**：
  - `COMPLETED` → 下一节点
  - `FAILED` / `BLOCKED` → `END` 或 `PAUSE`

---

### P1-T2：CLI 失败状态暴露测试

**对应修复**：`start_pipeline()` 返回 `{pipeline_id, status, failed_nodes, error}`；CLI 输出失败信息并返回非 0 exit code。

#### 测试 T2.1：`test_cli_start_shows_failed_on_sync_failure`

- **前置条件**：
  - 使用 mock orchestrator，让它返回 `status='failed'`。
- **步骤**：
  - 调用 `start` 命令。
- **断言**：
  - 标准输出包含 `"Pipeline failed"` 或 `"failed_nodes"`。
  - exit code != 0（至少为 1）。

#### 测试 T2.2：`test_start_pipeline_returns_status_dict`

- **目标**：`HybridOrchestrator.start_pipeline()` 不再只返回 `pipeline_id`。
- **步骤**：
  - 调用 `start_pipeline()`。
- **断言**：
  - 返回值为字典。
  - 包含 `pipeline_id`、`status`、`failed_nodes`、`error`。

#### 测试 T2.3：`test_cli_does_not_print_started_when_failed`

- **断言**：
  - 当 `status == 'failed'` 时，标准输出**不包含** `"Pipeline started successfully"` 或 `"completed"`。

---

### P1-T3：SummaryAgent context_file 解析测试

**对应修复**：`SummaryAgent` 同时支持 `context_file`、显式 `referenced_files`、`content` 内引用三种来源。

#### 测试 T3.1：`test_summary_agent_includes_context_file`

- **前置条件**：
  - `subject_context.context_file = 'docs/calc-one-plus-one/calc-context.md'`
  - 文件存在且有内容。
- **步骤**：
  - 调用 `SummaryAgent.summarize_documents(subject_context)`。
- **断言**：
  - 返回的 `referenced_files` 包含 `calc-context.md`。
  - `documents_summarized count >= 1`。

#### 测试 T3.2：`test_referenced_files_parsing_shared_between_summary_and_context_builder`

- **目标**：同一解析函数被复用。
- **断言**：
  - `ContextBuilder._extract_referenced_files` 与 `SummaryAgent._extract_referenced_files` 指向同一函数对象（或同一模块内的函数）。

---

### P1-T4：Runtime Contract 回归测试

**对应修复**：增加不调用 LLM 的 runtime contract tests，用 fake agents/session manager 覆盖 graph。

#### 测试 T4.1：`test_graph_execution_with_fake_agents`

- **前置条件**：
  - mock `SessionManager`：只记录调用，不操作数据库。
  - mock `IndependentAgent.execute()`：返回固定字符串 `"FAKE_DELIVERABLE"`。
  - mock `EvaluatorAgent.evaluate()`：返回 `EvaluationResult(passed=True, score=1.0)`。
- **步骤**：
  - 运行完整 graph。
- **断言**：
  - `state.status == 'completed'`
  - `state.deliverables['analyst'] == 'FAKE_DELIVERABLE'`
  - 五个节点全部在 `completed_nodes` 中。

#### 测试 T4.2：`test_graph_execution_with_fake_failing_evaluator`

- **前置条件**：
  - `EvaluatorAgent.evaluate()` 返回 `passed=False`。
- **断言**：
  - 节点进入 `failed_nodes`。
  - 若实现重试，则 `iteration` 递增到 `max_iterations` 后失败。

#### 测试 T4.3：`test_node_config_consumer_contract`

- **目标**：枚举所有消费者读取的字段，确保 dataclass 存在。
- **步骤**：
  ```python
  config = NodeLoader().load("analyst")
  consumers = [
      ("task", ["ContextManager.build_independent_input", "NodePromptContractBuilder"]),
      ("evaluator.threshold", ["EvaluatorAgent", "QualityGate"]),
      ("evaluator.max_iterations", ["DualAgentNode"]),
  ]
  ```
- **断言**：
  - 对每个 `(field, consumers)`，验证 `config` 可通过该路径访问。

---

## P2 Sprint：降低重复实现风险

> **目标**：收敛重复 loader；清理旧 legacy prompt/template 路径；给 `NodeConfig` consumers 建立合同测试。

---

### P2-T1：Loader 收敛与单一事实来源测试

**对应修复**：`PersonaLoader` 和 `CriteriaLoader` 不再各自拼路径，统一委托 `NodeLoader` 或 `NodeConfigResolver`。

#### 测试 T1.1：`test_persona_loader_uses_node_loader`

- **目标**：`PersonaLoader.load()` 内部调用 `NodeLoader`。
- **断言**：
  - `PersonaLoader.load("analyst")` 的调用栈中（通过 mock）包含 `NodeLoader.load`。

#### 测试 T1.2：`test_criteria_loader_uses_node_loader`

- **断言**：同上，针对 `CriteriaLoader`。

#### 测试 T1.3：`test_no_duplicate_path_join_logic`

- **目标**：生产代码中不存在两处以上拼接 `"nodes" / node_id` 的逻辑。
- **步骤**：
  - 搜索源码中 `Path(...) / "nodes"` 或 `"nodes" / node_id` 模式。
- **断言**：
  - 仅 `NodeLoader`（或统一 `NodeConfigResolver`）一处有该拼接逻辑。

---

### P2-T2：NodeConfig 消费者合同测试

**对应修复**：通过反射/AST 扫描，确保 dataclass 字段与消费者引用一致。

#### 测试 T2.1：`test_all_node_config_fields_have_yaml_source`

- **步骤**：
  - 读取 `autoBMAD/nodes/{node}/node.yaml`。
  - 对比 `NodeConfig` dataclass 的 `__annotations__`。
- **断言**：
  - dataclass 中每个非可选字段，YAML 中必须有对应值（或 loader 中有明确 fallback）。

#### 测试 T2.2：`test_all_consumer_references_exist_on_dataclass`

- **步骤**：
  - 静态扫描 `autoBMAD/docuswarm/` 下所有 `.py` 文件中的 `node_config\.` 属性访问。
  - 排除测试文件和 mock 对象。
- **断言**：
  - 每个被访问的属性（如 `.task`、`.evaluator.threshold`）在 `NodeConfig` 或嵌套 dataclass 中存在。

---

### P2-T3：Legacy 路径隔离测试

**对应修复**：删除或隔离旧 legacy prompt/template 路径；fallback 不再静默吞错。

#### 测试 T3.1：`test_no_silent_fallback_on_missing_persona_in_primary_path`

- **目标**：节点主路径缺失 persona 时，不应返回默认 agent。
- **步骤**：
  - 临时重命名 `autoBMAD/nodes/analyst/persona.json`。
  - 调用 `PersonaLoader.load("analyst", package_root=...)`。
- **断言**：
  - 抛出 `FileNotFoundError` 或 `PersonaNotFoundError`，而不是返回默认 persona。
- **清理**：恢复文件。

#### 测试 T3.2：`test_legacy_prompt_paths_marked_deprecated`

- **步骤**：
  - 搜索 `prompts/` 下未被 `NodePromptContractBuilder` 引用的旧模板文件。
- **断言**：
  - 遗留文件被移动到 `legacy/` 子目录，或在文件头添加 `DEPRECATED` 标记。

---

## 测试执行与回归策略

### 测试分层

| 层级 | 范围 | 速度 | 触发时机 |
|------|------|------|----------|
| **Unit** | Loader、State、Contract | < 1s | 每次 commit（pre-commit hook） |
| **Integration** | NodeExecutor + 真实 FS，mock LLM | < 5s | PR CI |
| **E2E** | CLI + 完整 pipeline + fake agents | < 30s | 每日或发布前 |

### 回归要求

1. **日志场景固化**：
   - 对 `logs/docuswarm-2026-04-28.log` 中的输入参数，编写 `test_log_2026_04_28_regression`。
   - 该测试必须：路径正确 → 只失败 analyst → status = failed → `completed_nodes` 为空。

2. **文件系统隔离**：
   - 所有修改真实文件的测试必须使用 `tmp_path` fixture，并在测试后清理。
   - 读取真实配置的测试可以保留，但不应修改原文件。

3. **Mock 策略**：
   - LLM 调用必须被 mock（`anthropic.Anthropic.messages.create` 或 SDK wrapper）。
   - 数据库/SessionManager 建议使用内存 mock，避免测试间状态污染。

### 执行命令

```bash
# P0 单元测试
.venv/bin/python -m pytest tests/test_docuswarm_p0_path_resolution.py -v

# P0 集成测试
.venv/bin/python -m pytest tests/test_docuswarm_p0_integration.py -v

# P1 CLI 测试
.venv/bin/python -m pytest tests/test_docuswarm_p1_cli_status.py -v

# P2 合同测试
.venv/bin/python -m pytest tests/test_docuswarm_p2_consumer_contract.py -v

# 全量回归（修复完成后应达到）
.venv/bin/python -m pytest tests/ -q --tb=short
# 预期：当前 25 passed → 新增 30+ passed，覆盖率从 21% 提升到 60%+
```

---

## 验收标准

### P0 验收（阻塞发布）

- [ ] `NodeExecutor("analyst")` 从 repo root 启动时，能加载真实 persona 和 evaluator，不再访问 `/home/leafliu/autoBMAD/nodes/...`。
- [ ] `NodeConfig` 包含 `task`、`evaluator.threshold(s)`、`evaluator.max_iterations`，`ContextManager.build_independent_input()` 不再抛 `AttributeError`。
- [ ] 任何节点初始化失败时，`completed_nodes` 为空，`status='failed'`，`deliverables` 为空。
- [ ] 新增 P0 测试全部通过，原有 25 个测试不回归失败。

### P1 验收（恢复信任）

- [ ] 上游节点失败后，下游节点标记为 `skipped`，不执行。
- [ ] CLI 对失败 pipeline 显示 `"Pipeline failed"` 并返回非 0 exit code。
- [ ] `SummaryAgent` 将 `context_file` 纳入 `documents_summarized`。
- [ ] 存在至少一个使用 fake agents 的 graph E2E 测试。

### P2 验收（工程健康）

- [ ] `PersonaLoader` 和 `CriteriaLoader` 内部使用 `NodeLoader`，不自行拼路径。
- [ ] 通过静态扫描或反射测试，确保 `NodeConfig` 字段与消费者引用一致。
- [ ] 生产主路径中的裸 `except Exception: return default` 被移除或改为记录后抛出。

---

## 附录：测试文件清单建议

```
tests/
├── conftest.py                              # 共享 fixtures：fake_node_config, temp_repo_root, mock_llm
├── test_docuswarm_p0_path_resolution.py     # P0-T1
├── test_docuswarm_p0_node_config_schema.py  # P0-T2
├── test_docuswarm_p0_state_invariants.py    # P0-T3, P0-T4
├── test_docuswarm_p0_integration.py         # P0-T5
├── test_docuswarm_p1_graph_dependencies.py  # P1-T1
├── test_docuswarm_p1_cli_status.py          # P1-T2
├── test_docuswarm_p1_summary_agent.py       # P1-T3
├── test_docuswarm_p1_runtime_contract.py    # P1-T4
├── test_docuswarm_p2_loader_convergence.py  # P2-T1
├── test_docuswarm_p2_consumer_contract.py   # P2-T2
└── test_docuswarm_p2_legacy_cleanup.py      # P2-T3
```

---

## 参考

- 根因报告：`docs-doc/evaluation/2026-04-28-docuswarm-log-driven-deep-review.md`
- 触发日志：`logs/docuswarm-2026-04-28.log`
- 关键源码位置（报告中已标注行号）：
  - `autoBMAD/docuswarm/node_execution/executor.py:125-147`
  - `autoBMAD/docuswarm/agents/evaluator.py:99-198`
  - `autoBMAD/docuswarm/agents/persona.py:135-139`
  - `autoBMAD/docuswarm/pipeline/graph.py:146-150`
  - `autoBMAD/docuswarm/pipeline/state.py:285-310`
  - `autoBMAD/nodes/loader.py:95-326`
