# DocuSwarm 综合深度研究报告

日期: 2026-05-01
研究范围: `autoBMAD/docuswarm`
数据来源:
- `docs/evaluation/2026-05-01-docuswarm-blocking-question-removal-review.md`
- `docs-doc/evaluation/2026-05-01-docuswarm-pipeline-1777610205512-deep-evaluation.md`
- 运行日志: `logs/docuswarm-2026-05-01.log`
- 运行数据库: `docuswarm.db`
- 源代码静态分析

调试工具:
- `tools/docuswarm_blocking_question_deep_researcher.py`
- `tools/docuswarm_pipeline_state_deep_researcher.py`
- `tools/docuswarm_summary_agent_deep_researcher.py`
- `tools/docuswarm_sdk_security_deep_researcher.py`
- `tools/docuswarm_evaluator_quality_deep_researcher.py`

---

## 执行摘要

本次研究基于两份独立评估报告的全部问题，通过静态代码分析、日志取证和数据库取证三重手段进行深度验证。研究发现以下核心结论:

1. **blocking question 交互机制是一个"虚假承诺"**: 从 prompt、schema、README 到 CLI 命令，全链路都在描述一个可交互的问答系统，但底层实现缺少持久化、状态机和恢复路径。代理仍会生成 blocking 问题，但 pipeline 直接忽略它们并标记为 completed。

2. **pipeline 状态语义存在系统性偏差**: `current_node` 在完成后未清空、`node_iterations` 与实际 iteration 不一致、`pipeline_started` 事件在结束后触发、emergency finalize 写入非法状态并破坏单一状态源。

3. **SummaryAgent 结构化输出是已知残留问题**: 该问题已被历史报告提及，但仍靠重试运气过关，每次 fenced JSON 响应浪费一次 LLM 调用。

4. **Evaluator 质量门缺少 hard gate**: 所有节点 alignment_score > 0.91，但 factual error、blocking question、AC 歧义等离散缺陷未被阻止。

5. **SDK 权限边界比实际需要更宽**: cwd 被提升到 repo parent，auto_approve_tools 依赖 allowed_tools 正确生成。

---

## 研究方法论

### 静态代码分析
- 对报告中提及的 20+ 个源文件进行逐行分析
- 使用正则表达式提取关键代码路径（QuestionHandler、StateManager、DualAgentNode、SummaryAgent、EvaluatorAgent）
- 交叉引用代码中 `blocking` 关键字出现位置（共 24 处）

### 日志取证
- 解析 `docuswarm-2026-05-01.log`（147,638 字符）
- 提取 final state、alignment_score、iteration 计数、JSON 解析错误等关键事件
- 确认 `pipeline_started` 事件出现在日志 89.9% 位置（即末尾）

### 数据库取证
- 读取 `docuswarm.db` pipelines 表
- 对比 top-level columns（status, current_node）与 `state_json` 内嵌字段的一致性
- 确认 completed pipeline 中仍包含 2 条 blocking questions

---

## 第一部分: Blocking Question 机制研究

### 1.1 Finding F1: QuestionHandler 没有持久化（High）

**证据:**

```python
# autoBMAD/docuswarm/pipeline/questions.py
self._questions: dict[str, list[Question]] = {}
```

`QuestionHandler` 仅维护一个内存字典。每次 CLI 执行 `docuswarm answer` 或 `docuswarm questions` 时:

```python
# autoBMAD/docuswarm/cli/commands/answer.py:44-45
state_manager = StateManager()
question_handler = QuestionHandler(state_manager=state_manager)
```

都会创建一个全新的 `QuestionHandler` 实例。这意味着:
- 同一 pipeline 运行时收集的问题在 CLI 进程中不可见
- `get_unanswered_questions()` 对历史 pipeline 永远返回空列表
- `answer_question()` 永远抛出 `ValueError: Question not found`

**数据库验证:** 从 DB 读取的 pipeline state 包含 15 个问题，但 CLI 无法通过 `QuestionHandler` 访问其中任何一个。

### 1.2 Finding F2: create_dual_agent_node 未注入 QuestionHandler（High）

**证据:**

```python
# autoBMAD/docuswarm/nodes/dual_agent.py:830-888
def create_dual_agent_node(...) -> DualAgentNode:
    ...
    return DualAgentNode(
        config=config,
        independent_agent=independent_agent,
        evaluator_agent=evaluator_agent,
        node_id=node_id,
        max_iterations=max_iterations,
    )
```

`create_dual_agent_node()` 是主执行路径的节点工厂函数，但它**没有**传递 `question_handler` 参数。因此:
- `DualAgentNode.question_handler` 永远为 `None`
- `collect_questions()` 在 `execute_with_iteration()` 中被调用，但条件是 `if self.question_handler and final_questions`，所以永远不会执行
- 问题仍会通过 `NodeResult.questions` 进入 pipeline state，但**不经过 `QuestionHandler` 的内存管理**

这意味着 CLI `questions` 命令和 pipeline state 中的 `questions` 是完全隔离的两套数据模型。

### 1.3 Finding F3: README 与代码不一致（High）

**证据:**

README 承诺:
- `questions` 命令列出未回答问题
- `answer` 命令回答问题
- `paused` 表示等待回答
- blocking 问题会自动暂停

实际代码:
- `QuestionHandler` 不持久化（F1）
- `create_dual_agent_node()` 不接入 `QuestionHandler`（F2）
- pipeline 没有基于 blocking question 转为 `paused` 的主路径
- `StateManager.PIPELINE_STATUSES` 包含 `paused`，但没有代码将其与 blocking question 关联

### 1.4 Finding F4: blocking 语义污染成功输出（Medium）

**证据:**

DB 取证显示 completed pipeline 中存在 2 条 blocking questions:

| 节点 | 优先级 | 问题内容摘要 |
|------|--------|-------------|
| ux | blocking | PM 提供的 PRD 中是否已将输出格式 `1 + 1 = 2` 与退出码 0 列为验收标准？ |
| po | blocking | 上游交付物在文件系统中未找到实物文件，是否应以提示中提供的「上游交付物摘要」... |

Prompt、工具 schema 和 validator 三处都明确接受 `blocking`:

```python
# autoBMAD/docuswarm/context/validator.py:586
VALID_PRIORITIES: set[str] = {"blocking", "clarifying", "optional"}

# autoBMAD/docuswarm/tools/create_deliverable_sdk.py:107
"enum": ["blocking", "clarifying", "optional"],

# autoBMAD/docuswarm/prompts/contract_builder.py:721
- **blocking**: Must be answered before proceeding
```

**结论**: blocking 问题被鼓励生成、被 validator 接受、被记录到 state，但**不被执行系统识别**。这是一个完整的语义断裂。

### 1.5 Finding F5: 两套 QuestionPriority 定义分叉（Medium）

**证据:**

```python
# pipeline/questions.py:30-41
class QuestionPriority(Enum):
    BLOCKING = "BLOCKING"
    CLARIFYING = "CLARIFYING"
    OPTIONAL = "OPTIONAL"

# llm/response.py:13
QuestionPriority = Literal["low", "medium", "high", "critical"]
```

这两套定义互不兼容:
- 前者用于 pipeline 问题管理（大写，三档）
- 后者用于 LLM 响应解析（小写，四档，完全不同的语义）
- validator 使用第三套小写集合 `{"blocking", "clarifying", "optional"}`
- `questions.py` 通过 `.upper()` 兼容层掩盖分歧

### 1.6 Finding F6: questions 字段审计价值（Medium）

**证据:**

DB pipeline state 的 questions 分布:

| 节点 | 总数 | blocking | clarifying | optional |
|------|------|----------|------------|----------|
| analyst | 3 | 0 | 2 | 1 |
| pm | 3 | 0 | 1 | 2 |
| ux | 3 | 1 | 1 | 1 |
| architect | 3 | 0 | 2 | 1 |
| po | 3 | 1 | 1 | 1 |
| **总计** | **15** | **2** | **7** | **6** |

这些问题暴露了:
- 上游上下文缺口（po 质疑交付物文件是否存在）
- 代理做的默认假设（analyst 假设 sys.exit(0) 行为）
- 后续自动化改进点（测试脚本、可访问性）

**不应一刀切删除**，但应去掉"必须回答"语义。

---

## 第二部分: Pipeline 状态一致性研究

### 2.1 Finding STATE-1: current_node 在 completed 状态未清空（High）

**证据:**

```
DB state_json:    status='completed', current_node='po'
DB top-level:     status='completed', current_node='po'
completed_nodes:  ['analyst', 'pm', 'ux', 'architect', 'po']
```

代码路径:
1. `graph.py:83` 每个节点执行时设置 `new_state["current_node"] = node_id`
2. `orchestrator.py:497` final write 时读取 `result.get("current_node", "po")`
3. 没有任何 finalize 阶段清空 `current_node`

**影响**: `status` 命令显示 completed 但 `current_node='po'`，resume/cancel 逻辑可能误判。

### 2.2 Finding STATE-2: node_iterations 与实际 iteration 不一致（High）

**证据:**

```
DB state_json node_iterations: {'analyst': 2, 'pm': 2, 'ux': 2, 'architect': 2, 'po': 2}
Log dual_agent_approved iterations: [1, 1, 1, 1, 1]
```

每个节点都只执行了 1 轮 DualAgent iteration（Independent + Evaluator 一次即 approved），但 DB 记录为 2。

代码路径:
- `graph.py:154` 使用 `executed_node_state.get("iteration", 1)`
- 但 `NodeResult.iteration` 的语义存在 off-by-one 或 adapter 漂移

**影响**: 质量指标失真，成本分析、retry 分析、回归基线全部不可靠。

### 2.3 Finding STATE-3: emergency finalize 写入非法状态（High）

**证据:**

```python
# cli/services/pipeline_service.py:95-99
conn.execute(
    "UPDATE pipelines SET status = 'interrupted', updated_at = CURRENT_TIMESTAMP "
    "WHERE pipeline_id = ? AND status = 'running'",
    (pipeline_id,)
)
```

```python
# storage/state_manager.py:38
PIPELINE_STATUSES = ("pending", "running", "completed", "failed", "paused", "cancelled")
```

`'interrupted'` **不在**合法状态集合中。

更严重的是:
- 只更新顶层 `pipelines.status` 列
- **不更新** `state_json.status`
- 破坏 "state_json 作为单一真实状态源" 的设计原则

### 2.4 Finding STATE-4: StateManager deep merge 保留旧字段（Medium）

**证据:**

```python
# storage/state_manager.py:911-923
def _deep_merge(self, target, source):
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            self._deep_merge(target[key], value)
        else:
            target[key] = value
```

`update_pipeline_state()` 文档称 "Update complete PipelineState"，但实现是 deep merge。

**影响**:
- resume/restart 后可能残留旧 `questions`、`evaluations`、`session_metadata`
- 节点重跑时删除字段不容易生效（merge 不支持删除语义）
- 完整替换和局部 patch 混用

### 2.5 Finding STATE-5: pipeline_started 日志事件名错误（Medium）

**证据:**

```python
# orchestrator.py:506-510
result["status"] = final_status
result["current_node"] = final_current_node
await self._state_manager.update_pipeline_state(...)

logger.info(
    "pipeline_started",   # <-- 事件名错误
    pipeline_id=final_pipeline_id,
    result=result,
)
```

日志文件分析: `"pipeline_started"` 出现在日志 89.9% 位置，即执行完成后。

---

## 第三部分: SummaryAgent 研究

### 3.1 Finding SUM-1: json.loads() 无法处理 fenced JSON（High）

**证据:**

日志显示第一次 LLM 响应:

~~~text
```json
{ "summary": "...", "key_points": [...], "structure": {...} }
```
~~~

SummaryAgent 处理:

```python
# agents/summary.py:468-471
summary_text = self._extract_text_from_response(response)
data = json.loads(summary_text)   # <-- 在第一个反引号处失败
```

错误: `Invalid JSON response: Expecting value: line 1 column 1 (char 0)`

第二次 retry 返回裸 JSON 后通过。此问题在 EvaluatorAgent 中已修复（使用 `extract_json` fallback），但 SummaryAgent 未对齐。

### 3.2 Finding SUM-2: 缓存配置未实现（Medium）

**证据:**

```yaml
# config/summary_agent.yaml
caching:
  enable: true   # 配置声明已启用
```

但 `agents/summary.py` 中:
- 无 cache key 生成逻辑
- 无 ttl/失效策略
- 无 hit/miss 日志
- 每次 pipeline start 都调用 LLM

### 3.3 Finding SUM-3: Evaluator 与 SummaryAgent 结构化输出能力差距（Medium）

| 能力 | EvaluatorAgent | SummaryAgent |
|------|---------------|--------------|
| output_format 参数 | ✅ 有 | ❌ 无 |
| extract_json fallback | ✅ 有 | ❌ 无 |
| structured output 提取 | ✅ 有 | ❌ 无 |

---

## 第四部分: SDK 安全与权限边界研究

### 4.1 Finding SEC-1: SDK cwd 超出 repo root（Medium）

**证据:**

日志显示: `sdk_cwd=output`（相对路径，解析后为 `/home/leafliu/autoBMAD/output`）

但代码中:

```python
# agents/independent.py:1022-1024
repo_root = (
    self.project_root.parent if self.project_root.name == "autoBMAD" else self.project_root
)
```

如果 `project_root` 指向 `/home/leafliu/autoBMAD/autoBMAD`，则 `repo_root` 变成 `/home/leafliu`。

虽然 MCP file tools 有 allowed dirs 校验，但 SDK 进程的 cwd 已在仓库父目录，风险边界扩大。

### 4.2 Finding SEC-2: yolo 模式依赖 allowed_tools 正确生成（Medium）

**证据:**

- `independent.py` 中有 4 处 `yolo=True`
- `auto_approve_tools: true` 与 `yolo=True` 组合使用
- `allowed_tools_generation_failed` 仅产生 warning，未阻止执行

### 4.3 Finding SEC-3: PathValidator 使用 startswith()（Low）

**证据:**

```python
# tools/file_tools_sdk.py
if resolved_prefix.startswith(allowed_prefix) or resolved_path == allowed_dir:
    return resolved_path
```

建议增加 `Path.resolve().is_relative_to()` 作为第二层校验。

---

## 第五部分: Evaluator 质量门研究

### 5.1 Finding QG-1: 容忍度过高（Medium）

**证据:**

```python
# agents/evaluator.py
DEFAULT_APPROVAL_THRESHOLD = 0.70
```

本次 pipeline 所有节点 alignment_score > 0.91:

```
[0.931, 0.9375, 0.9535, 0.92, 0.919]
```

但 evaluator 的 `issues_found` 中已记录:
- PM 关于 `click`/`argparse` 的事实错误
- UX 缺少错误态
- PO 行数限制歧义
- Story-3 优先级不一致

这些离散缺陷未被 score 阈值阻止。

### 5.2 Finding QG-2: 缺少 hard gate（Medium）

**证据:**

Evaluator 按加权均分判定 verdict，没有对 `issues_found` 中的缺陷类型做离散检查。例如:
- `factual_error` 不应被 0.91 的均分掩盖
- `blocking_question` 存在时 verdict 不应为 APPROVED
- `acceptance_criteria_ambiguity` 应至少触发 NEEDS_REVISION

### 5.3 Finding QG-3: 编号体系不一致（Low）

**证据:**

| 交付物 | 编号模式 |
|--------|----------|
| analyst-report.md | `FR-001` (3位) |
| prd.md | `FR-01` (2位) |
| epics-stories.md | Story/Epic 另起编号 |

### 5.4 Finding QG-4: 架构输出过度展开（Low）

**证据:**

`architecture.md` 236 行，包含:
- C4 Context / Container 图
- Sequence diagram
- Mermaid flowchart
- Technology Stack
- Data Flow

对于 10 行以内的 CLI 脚本，这是过度文档化。

---

## 综合修复路线图

### Phase 0: 立即止损（可本周完成）

| 任务 | 文件 | 改动 |
|------|------|------|
| 禁用 blocking priority | `prompts/contract_builder.py`, `agents/independent.py` | 删除 blocking 描述和示例 |
| 拒绝 blocking 输入 | `context/validator.py`, `tools/create_deliverable_sdk.py` | 从 enum/VALID_PRIORITIES 删除 blocking |
| 降级历史 blocking | `pipeline/questions.py` | collect_questions 中将 blocking 降级为 clarifying 并 warning |
| 修复 SummaryAgent JSON | `agents/summary.py` | json.loads -> extract_json |
| 修复日志事件名 | `pipeline/orchestrator.py` | pipeline_started -> pipeline_completed |

### Phase 1: 状态语义修复（2-3 天）

| 任务 | 文件 | 改动 |
|------|------|------|
| 清空 completed current_node | `pipeline/graph.py` 或 `orchestrator.py` | finalize 时写 current_node=None, last_node=po |
| 修复 node_iterations | `nodes/dual_agent.py`, `pipeline/graph.py` | 统一 iteration 语义，禁止二次递增 |
| 修复 emergency finalize | `cli/services/pipeline_service.py` | 改用 StateManager，状态映射为 cancelled/failed |
| 拆分 patch/replace | `storage/state_manager.py` | 新增 replace_pipeline_state()，final write 使用 replace |

### Phase 2: 移除虚假交互系统（3-5 天）

| 任务 | 文件 | 改动 |
|------|------|------|
| 删除 answer CLI | `cli/commands/answer.py` | 整文件删除 |
| 改造 questions CLI | `cli/commands/questions.py` | 重命名为 diagnostics，读取 pipeline state |
| 删除 QuestionHandler 交互 | `pipeline/questions.py` | 删除 answer_question/has_blocking_questions/_incorporate_answer |
| 清理 DualAgentNode | `nodes/dual_agent.py` | 删除 question_handler 参数和 collect_questions 调用 |
| 更新 README | `README.md` | 删除交互式问答章节 |

### Phase 3: 质量门增强（1 周）

| 任务 | 文件 | 改动 |
|------|------|------|
| 增加 hard gate | `agents/evaluator.py` | issues_found 遍历检查 factual_error/blocking_question/ac_ambiguity |
| 统一编号规范 | `prompts/contract_builder.py` | 统一 FR-001/NFR-001/AC-001 格式 |
| lightweight 模板 | `templates/` | 为 trivial task 增加精简架构模板 |
| SummaryAgent 缓存 | `agents/summary.py` | 实现或标记为 reserved_for_future |

### Phase 4: 安全加固（可选，1 周）

| 任务 | 文件 | 改动 |
|------|------|------|
| 收紧 SDK cwd | `agents/independent.py` | 确保 cwd = repo_root，不超出 |
| 增强 PathValidator | `tools/file_tools_sdk.py` | 增加 resolve().is_relative_to() |
| allowed_tools 审计 | `llm/session_manager.py` | 记录实际生效的 allowed_tools 列表 |

---

## 风险矩阵

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 历史 pipeline 中的 blocking 值导致读取报错 | 中 | 中 | 读取侧兼容降级 + 单测覆盖 |
| 外部脚本依赖 `docuswarm answer` | 低 | 中 | Sprint 1 发版时 deprecation 警告一个 release 后再删 |
| `questions_json` DB 列被第三方工具直接查询 | 低 | 低 | 保留列名 + 文档注明字段语义已改为非阻塞 |
| 代理仍尝试返回 `priority='blocking'` | 高 | 低 | validator 强拒或自动降级，日志 warning |
| 重命名 Phase 3 未完成就被其他特性覆盖 | 中 | 低 | Phase 3 独立 epic 管理 |
| 修复 node_iterations 后破坏历史成本分析 | 中 | 低 | 在 CHANGELOG 中明确标注指标语义变更 |

---

## 回归测试清单

基于本次研究，建议新增以下测试:

### Blocking Question 相关
1. `test_independent_prompt_has_no_blocking_questions` - prompt 不包含 blocking
2. `test_submit_execution_report_rejects_blocking_priority` - validator 拒绝 blocking
3. `test_pipeline_completes_with_followups` - clarifying/optional 不阻断
4. `test_cli_no_answer_command` - CLI 不注册 answer
5. `test_diagnostics_export_includes_followups` - export 展示非阻塞 follow-ups

### Pipeline State 相关
6. `test_completed_pipeline_current_node_is_none` - finalize 后 current_node=None
7. `test_single_iteration_records_one` - 单轮 approved 节点 node_iterations=1
8. `test_emergency_finalize_uses_valid_status` - atexit 写入合法状态且同步 state_json
9. `test_final_log_event_name` - final log 事件为 pipeline_completed

### SummaryAgent 相关
10. `test_summary_agent_accepts_fenced_json` - fake single_prompt 返回 fenced JSON，一次通过
11. `test_summary_agent_uses_structured_output_when_available` - 优先使用 structured output

### Security 相关
12. `test_sdk_cwd_is_repo_root` - SDK cwd 不应是 repo parent

---

## 最终结论

DocuSwarm 是一个已经能端到端产出五类文档的可用系统，但在**运行时语义稳定性**方面存在结构性缺陷。本次研究通过代码分析、日志取证和数据库取证三重验证，确认了以下核心问题:

1. **blocking question 交互机制是虚假承诺** —— 应移除交互代码，保留非阻塞诊断字段
2. **pipeline 状态语义存在系统性偏差** —— 应修复 current_node、node_iterations、status 一致性
3. **SummaryAgent JSON 解析是已知残留问题** —— 应立即替换为 extract_json
4. **Evaluator 缺少 hard gate** —— 应在 score-based verdict 后增加离散缺陷检查层
5. **SDK 权限边界过宽** —— 应收紧 cwd 和增强路径校验

建议将 Phase 0 + Phase 1 作为下一轮 sprint 重点，修完后用同一个 `calc-context.md` 复跑验收: 无 SummaryAgent JSON retry、无 unanswered blocking question 的 completed 状态、`current_node=None`、每个节点 `node_iterations=1`、日志出现 `pipeline_completed`。
