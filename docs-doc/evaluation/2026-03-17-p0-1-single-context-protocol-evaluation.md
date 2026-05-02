# P0-1 评估报告：收敛为单一上下文协议

> 评估日期：2026-03-17
> 评估对象：`docs/research/2026-03-13-docuswarm-context-refactor-overview.md` 中的 `P0-1: 收敛为单一上下文协议`
> 评估结论：**未完成**
> 完成度判断：**约 60%**

## 1. 结论摘要

当前代码库已经落地了 `NodeExecutionContext`、`NodeExecutionContextBuilder`、`DualAgentNode.execute_with_context()`、`IndependentAgent.execute_with_input()`、`EvaluatorAgent.execute_with_input()` 等新协议骨架，说明 P0-1 已经进入实现阶段，并且主执行入口也开始接入新链路。

但按照 P0-1 文档中定义的目标，“消除字符串化、重复包装、隐式猜测，真正收敛为单一协议”，现状仍未达到“完成”标准。主要原因有四个：

1. 主执行链路中的原始上下文在真实运行态会被错误裁剪，导致 `IndependentAgent` 看不到应有的原始上下文。
2. 单节点执行流与流水线执行流对 `context_file` 的语义不一致，一个传路径、一个传 JSON，协议入口仍然不统一。
3. 旧协议路径仍完整保留在 `DualAgentNode.execute()`、`DualAgentNode.execute_with_iteration()`、`IndependentAgent.execute()`、`EvaluatorAgent.execute()` 中，代码库并未真正“收敛为单一协议”。
4. 文档要求去除 `_extract_task_from_state()` 主导语义，但该函数仍存在于代码库中，完成标准未满足。

因此，本次评估判断：**P0-1 已部分实现，但不能视为已完成。**

## 2. 评估依据

本次评估主要依据以下文档与代码：

- `docs/research/2026-03-13-docuswarm-context-refactor-overview.md`
- `docs/research/2026-03-13-p0-single-context-protocol-deep-research-report.md`
- `docs/research/2026-03-13-p0-single-context-protocol-implementation-design.md`
- `autoBMAD/docuswarm/node_execution/contracts.py`
- `autoBMAD/docuswarm/node_execution/context_builder.py`
- `autoBMAD/docuswarm/node_execution/executor.py`
- `autoBMAD/docuswarm/context/isolation.py`
- `autoBMAD/docuswarm/nodes/dual_agent.py`
- `autoBMAD/docuswarm/agents/independent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/node_execution/flow.py`
- `tests/unit/test_node_execution_context.py`
- `tests/unit/test_contract_builder.py`
- `tests/unit/test_single_context_protocol_completion.py`

## 3. P0-1 完成标准回放

结合 Overview / Deep Research / Implementation Design，P0-1 至少应满足以下判断条件：

1. `executor` 不再从运行态字符串或序列化 state 猜测任务语义，而是显式构建统一的 `NodeExecutionContext`。
2. `DualAgentNode` 不再做 `{subject, task}` 二次包装。
3. `IndependentAgent` 不再依赖 JSON 反解析、嵌套字段探测来恢复上下文。
4. 节点契约信息应能稳定进入 prompt，包括 `task_name`、`task_description`、`deliverable.required_sections` 等。
5. 代码库应收敛到单一协议主链，旧协议最多作为明确适配层存在，而不是继续并行承担真实执行职责。

## 4. 已完成部分

以下工作已经落地，说明 P0-1 不是“未开始”，而是“部分完成”：

### 4.1 新协议核心结构已存在

- `autoBMAD/docuswarm/node_execution/contracts.py:22-56` 已定义 `NodeExecutionContext`
- `autoBMAD/docuswarm/node_execution/contracts.py:59-84` 已定义 `IndependentAgentInput` 和 `EvaluatorAgentInput`
- `autoBMAD/docuswarm/node_execution/context_builder.py:16-107` 已实现 `NodeExecutionContextBuilder`

### 4.2 主执行入口已接入新链路

`autoBMAD/docuswarm/node_execution/executor.py:107-147` 已从：

- 解析运行态输入
- 构建 `execution_context`
- 调用 `node.execute_with_context(execution_context)`

这说明新协议已经不是纯文档设计，而是实际进入主 node executor。

### 4.3 `DualAgentNode` 已增加新执行方法

`autoBMAD/docuswarm/nodes/dual_agent.py:506-649` 已实现 `execute_with_context()`，并在新路径中：

- 通过 `ContextManager.build_independent_input()` 构建独立 agent 输入
- 通过 `ContextManager.build_evaluator_input()` 构建评审 agent 输入
- 调用 `IndependentAgent.execute_with_input()`
- 调用 `EvaluatorAgent.execute_with_input()`

这部分符合“协议先行，agent 接收结构化输入”的方向。

### 4.4 节点配置已接入 builder

`NodeLoader` 已能从 `node.yaml` 读取 `task` / `deliverable` 段，`NodeExecutionContextBuilder` 也会把它们映射为：

- `task_name`
- `task_description`
- `role_supplement`
- `deliverable_requirements`

这满足了“节点契约不再只停留在配置文件中”的基本前提。

## 5. 核心未完成项

以下问题足以阻止 P0-1 被判定为完成。

### 5.1 主链路会丢失原始上下文，导致新协议不自洽

这是当前最严重的问题。

`pipeline` 主流程构造 `NodeRunState` 时，`context_file` 保存的是“累计上下文 JSON 字符串”，不是单纯的 `{ "content": ... }`：

- `autoBMAD/docuswarm/pipeline/graph.py:191-194`

```python
accumulated = accumulate_context(subject_context, deliverables, node_id)
context_file = json.dumps(accumulated)
```

其真实结构类似：

```json
{
  "subject_context": {
    "task": "...",
    "content": "..."
  }
}
```

但 `ContextManager.build_independent_input()` 取原始上下文摘要时只读取顶层 `original_context["content"]`：

- `autoBMAD/docuswarm/context/isolation.py:85-88`

```python
original = execution_context["original_context"]
summary = original.get("content", "") if isinstance(original, dict) else str(original)
```

这意味着只要 `original_context` 是真实的 pipeline 结构，`summary` 就会变成空字符串。

我做了最小复现，结果如下：

```text
node_state.context_file= {"subject_context": {"task": "Build app", "content": "User wants a collaborative task app"}}
parsed= {'subject_context': {'task': 'Build app', 'content': 'User wants a collaborative task app'}}
original_context_summary= ''
```

这直接说明：

- 新协议链路虽然存在
- 但在真实主流程中，`IndependentAgent` 实际拿不到原始上下文正文
- 因此“单一上下文协议”在主链路上并未真正收敛成功

这也意味着 P0-1 验收标准中“任意节点运行时 prompt 能稳定看到节点契约和上下文”没有被满足。

### 5.2 `context_file` 语义仍然分裂，不是单一协议入口

`context_file` 在两个入口中的含义完全不同：

流水线执行流：

- `autoBMAD/docuswarm/pipeline/graph.py:191-194`
- 含义：累计上下文的 JSON 字符串

单节点执行流：

- `autoBMAD/docuswarm/node_execution/flow.py:268-274`
- 含义：磁盘上的 context 文件路径字符串

```python
initial_state = create_node_run_state(
    ...
    context_file=str(context_file_path),
)
```

而 `executor._parse_original_context()` 的实现又把它统一当成“JSON 字符串或原始文本”解析：

- `autoBMAD/docuswarm/node_execution/executor.py:219-239`

这会产生两个不同错误：

1. 流水线场景：累计上下文 JSON 会被保留为多层结构，但下游摘要器不会正确抽取。
2. 单节点场景：文件路径无法解析为 JSON，最终被包装成 `{"content": "<路径>"}`，把文件路径误当成正文。

最小复现结果如下：

```text
parsed= {'content': 'd:\\tmp\\context.json'}
original_context_summary= 'd:\\tmp\\context.json'
```

这说明“单一上下文协议”的入口语义还没有统一，仍然存在协议断裂。

### 5.3 旧协议路径仍然完整并行存在，代码库尚未真正“收敛”

P0-1 的目标不是“增加一个新路径”，而是“收敛为单一协议”。

但目前旧路径仍然完整存在并可执行：

- `autoBMAD/docuswarm/nodes/dual_agent.py:251-398` 仍保留 `execute(subject_context, task, pipeline_id)`
- `autoBMAD/docuswarm/nodes/dual_agent.py:322-325` 仍然构造 `{"subject": subject_context, "task": task}`
- `autoBMAD/docuswarm/nodes/dual_agent.py:393-396` 仍用旧的 `build_evaluator_context()`
- `autoBMAD/docuswarm/nodes/dual_agent.py:816-849` 的 `execute_with_iteration()` 也仍然走旧上下文构造

对应地，两个 agent 的旧执行接口也仍然在做旧协议解析：

- `autoBMAD/docuswarm/agents/independent.py:447-580`
- `autoBMAD/docuswarm/agents/evaluator.py:478-520`

其中 `IndependentAgent.execute()` 仍保留了典型的旧协议恢复逻辑：

- 读顶层 `task`
- 读 `subject_context.task`
- JSON 反序列化 `subject_context`
- 探测 `subject_context.subject_context.content`
- 回退到 `subject_context.content`

这说明当前状态更接近：

- “新旧两套协议并存”

而不是：

- “已经收敛为单一协议，旧协议只剩薄适配层”

因此，从架构收敛角度看，P0-1 仍未完成。

### 5.4 `_extract_task_from_state()` 仍在代码库中，未达到文档完成标准

Implementation Design 和 Completion 测试都把“删除 `_extract_task_from_state()`”写成完成标准的一部分。

但该函数当前仍保留在代码中：

- `autoBMAD/docuswarm/node_execution/executor.py:264-323`

虽然入口 `_execute_node()` 不再调用它，但文档写的是“不再存在 `_extract_task_from_state()` 主导任务语义”，而不是“保留一个 deprecated 版本也算完成”。按严格验收标准，这一项不能判定为完成。

### 5.5 新协议的字段定义与实际消费存在漂移

`NodeExecutionContext` 并未声明 `evaluator_criteria`：

- `autoBMAD/docuswarm/node_execution/contracts.py:22-56`

但 `NodePromptContractBuilder` 的 evaluator prompt 却尝试从 context 读取它：

- `autoBMAD/docuswarm/prompts/contract_builder.py:277-283`

```python
criteria = context.get("evaluator_criteria", [])
if not criteria:
    return "## 评分标准\n\n未配置评分标准。"
```

而 `EvaluatorAgent.execute_with_input()` 又在运行时临时把 `evaluator_criteria=criteria` 塞进 `NodeExecutionContext(...)`：

- `autoBMAD/docuswarm/agents/evaluator.py:562-578`

这说明：

- 协议类型定义
- prompt builder 消费方式
- agent 运行时构造方式

三者还没有完全对齐。

同时，`ContextManager.build_evaluator_input()` 实际返回的 `criteria` 是空列表：

- `autoBMAD/docuswarm/context/isolation.py:140-145`

```python
return EvaluatorAgentInput(
    ...
    criteria=[],  # 由 EvaluatorAgent 自行加载
)
```

这意味着 evaluator 的结构化输入并没有真正承载完整评审契约，仍然依赖 agent 内部自行加载配置，协议并未完全闭合。

## 6. 次级风险

这些问题未必单独阻断 P0-1 结论，但会显著削弱“已完成”的可信度。

### 6.1 `shared_context` / `docs_context` 只定义不消费

`NodeExecutionContext` 中声明了：

- `shared_context`
- `docs_context`

但当前代码中几乎只在 builder 或 agent 内部重建时赋默认值，没有被真正纳入 prompt 构造或 agent 输入裁剪。说明协议字段已经设计出来，但未形成闭环消费。

### 6.2 测试覆盖偏静态，未覆盖真实运行态数据形状

现有单测大多直接手造：

```python
original_context={"content": "..."}
```

这绕开了真实主流程中的输入形状：

```python
{"subject_context": {...}, "pm_deliverable": {...}}
```

因此测试虽然大量通过，但并没有证明“新协议在真实执行态正确工作”。

## 7. 测试与验证结果

### 7.1 代码导入/编译

对以下文件执行 `python -m py_compile`，结果通过：

- `node_execution/contracts.py`
- `node_execution/context_builder.py`
- `node_execution/executor.py`
- `context/isolation.py`
- `prompts/contract_builder.py`
- `agents/independent.py`
- `agents/evaluator.py`
- `nodes/dual_agent.py`

说明当前实现至少在语法层面可导入。

### 7.2 单元测试

执行：

```bash
pytest -q tests/unit/test_node_execution_context.py tests/unit/test_contract_builder.py tests/unit/test_single_context_protocol_completion.py
```

观察结果：

- 绝大多数断言通过
- 失败来自 `pytest` 使用系统临时目录/基目录时的权限问题
- 失败并未直接指出 P0-1 代码断言不成立

但这组测试本身存在一个明显盲区：它们没有覆盖真实 pipeline 中 `context_file` 的结构，因此未能发现“原始上下文摘要丢失”的问题。

### 7.3 手工最小复现

我执行了两组最小复现：

1. `pipeline.graph._convert_pipeline_to_node_state()` 生成真实 node state，再走 `executor -> builder -> ContextManager`
2. 单节点流传入文件路径字符串，再走同一链路

结果分别证明：

- 流水线主路径下 `original_context_summary == ''`
- 单节点路径下 `original_context_summary == '<context_file path>'`

这两点足以说明新协议链路尚未完成语义统一。

## 8. 完成标准判定表

| 标准 | 判定 | 说明 |
| --- | --- | --- |
| `executor` 不再主导任务猜测 | 部分完成 | 主入口改用 builder，但 `_extract_task_from_state()` 仍保留 |
| `DualAgentNode` 不再做 `{subject, task}` 二次包装 | 部分完成 | `execute_with_context()` 已移除，但旧 `execute()` / `execute_with_iteration()` 仍保留旧包装 |
| `IndependentAgent` 不再做字符串/JSON 反解析 | 部分完成 | `execute_with_input()` 满足，但旧 `execute()` 仍保留复杂恢复逻辑 |
| 节点契约稳定进入 prompt | 部分完成 | `task_name` / `task_description` / `required_sections` 已接入，但真实主流程中原始上下文会丢失 |
| 代码库收敛为单一上下文协议 | 未完成 | 仍存在并行旧协议、分裂的 `context_file` 语义、字段定义漂移 |

## 9. 最终判定

**P0-1 当前不能判定为已完成。**

更准确的表述应为：

> P0-1 已完成“新协议骨架接入”和“部分主链切换”，但尚未完成“协议语义统一”和“旧协议收敛退出”。

如果要把状态改为“已完成”，至少还需要补齐以下收尾动作：

1. 统一 `context_file` 语义，明确它到底是“内容 JSON”还是“文件路径”，不能两种都算。
2. 让 `ContextManager.build_independent_input()` 正确抽取真实 pipeline 结构中的原始上下文，而不是只读顶层 `content`。
3. 处理旧协议收敛，至少把 `DualAgentNode.execute()` / `execute_with_iteration()` 明确改造成适配层，或迁移到新协议后删除。
4. 删除 `_extract_task_from_state()`，或者把文档/完成标准改成“允许保留 deprecated 兼容层”。
5. 对真实 `PipelineState -> NodeRunState -> executor -> agents` 增加集成测试，覆盖当前发现的上下文丢失问题。

## 10. 建议后续动作

建议把 P0-1 拆成两个收尾修复包：

### A. 协议语义修复

- 修复 `original_context` 的规范化逻辑
- 为 pipeline / standalone 两条入口提供统一 adapter
- 补齐 `EvaluatorAgentInput.criteria` 与 `NodeExecutionContext` 的一致性

### B. 协议收敛清理

- 清理 `DualAgentNode` / agents 中的旧执行接口
- 删除 `_extract_task_from_state()`
- 将测试从“手工构造理想输入”升级为“基于真实 state 结构验证”

在这两部分完成前，建议项目状态将 P0-1 标记为：

**`进行中（已实现主骨架，未完成收敛）`**
