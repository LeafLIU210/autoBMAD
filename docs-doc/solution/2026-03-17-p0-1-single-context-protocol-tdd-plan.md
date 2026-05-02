# P0-1 单一上下文协议收尾测试驱动方案

> 日期：2026-03-17
> 来源：`docs/evaluation/2026-03-17-p0-1-single-context-protocol-evaluation.md`
> 目标：把 `P0-1: 收敛为单一上下文协议` 从“部分实现”推进到“可验收完成”
> 方法：严格按测试驱动开发执行，先定义失败测试，再实现最小修复，再跑回归

## 1. 背景

评估报告确认了 P0-1 当前的四类核心缺口：

1. `original_context` 在真实主链路中会丢失或被错误解释。
2. `context_file` 在 pipeline / standalone 两条入口上的语义不统一。
3. `Evaluator` 相关契约没有真正走完结构化链路。
4. 旧协议入口仍在并行执行，代码没有真正收敛。

本方案的目标不是继续增加“新路径”，而是通过测试驱动把真实执行链路彻底压到单一上下文协议上。

## 2. 总体策略

按四个规格分批推进，每个规格都遵循：

1. 先写失败测试，锁定真实缺口
2. 再做最小实现，使测试转绿
3. 最后重构代码，去掉重复逻辑和旧协议残留

## 3. 规格分解

### Spec A: 统一 `original_context` 归一化

**目标**

- `executor` 无论收到的是：
  - pipeline 累计上下文 JSON 字符串
  - 单节点 context 文件路径
  - 直接文本
- 都能归一化为统一的 `NodeExecutionContext.original_context`
- 并且稳定产出顶层 `content`

**测试范围**

- `executor._parse_original_context()` 或其替代实现
- `pipeline.graph._convert_pipeline_to_node_state() -> executor -> ContextManager`
- `node_execution.flow.execute_node_flow()` 的 standalone 输入形状

**新增/修改测试**

- `tests/unit/test_single_context_protocol_tdd.py`
  - `test_pipeline_context_file_is_normalized_with_top_level_content`
  - `test_file_path_context_file_is_loaded_from_disk`
  - `test_context_manager_uses_normalized_original_content`
  - `test_pipeline_node_state_roundtrip_keeps_user_context_visible`

**验收标准**

- pipeline 场景下 `original_context_summary` 不为空，且包含真实用户上下文正文
- standalone 场景下 `original_context_summary` 不等于文件路径字符串
- `NodeExecutionContext.original_context["content"]` 在两种入口中都存在

### Spec B: 闭合 Evaluator 契约

**目标**

- `evaluator_criteria` 从 `node.yaml/evaluator.yaml` 进入 `NodeExecutionContext`
- `ContextManager.build_evaluator_input()` 返回真实 criteria
- `EvaluatorAgent.execute_with_input()` 不再依赖运行时偷偷向 `NodeExecutionContext` 塞未声明字段

**测试范围**

- `NodeExecutionContextBuilder`
- `ContextManager.build_evaluator_input`
- `NodePromptContractBuilder.build_evaluator_contract`

**新增/修改测试**

- `tests/unit/test_single_context_protocol_tdd.py`
  - `test_context_builder_populates_evaluator_criteria`
  - `test_context_manager_passes_evaluator_criteria`
  - `test_evaluator_contract_uses_structured_criteria_from_execution_context`

**验收标准**

- `execution_context` 中可直接读取 evaluator criteria
- `EvaluatorAgentInput.criteria` 不再是空列表
- evaluator prompt 中包含节点真实 criteria，而不是“未配置评分标准”

### Spec C: 收敛旧执行入口

**目标**

- `DualAgentNode.execute()` 从旧签名适配到 `execute_with_context()`，不再手工构造 `{subject, task}`
- `DualAgentNode.execute_with_iteration()` 内部切换到结构化 `IndependentAgentInput` / `EvaluatorAgentInput`
- 避免继续通过旧 `build_independent_context()` / `build_evaluator_context()` 承担真实执行职责

**测试范围**

- `DualAgentNode.execute`
- `DualAgentNode.execute_with_iteration`
- 旧接口与新接口的适配行为

**新增/修改测试**

- `tests/unit/test_single_context_protocol_tdd.py`
  - `test_dual_agent_execute_adapts_to_execute_with_context`
  - `test_dual_agent_iteration_path_uses_structured_inputs`

**验收标准**

- `DualAgentNode.execute()` 不再在源代码中出现 `{"subject": ..., "task": ...}` 旧包装
- `execute_with_iteration()` 不再调用旧 context builder 方法
- 旧入口保留兼容性，但只作为薄适配层

### Spec D: 清理遗留与补强回归

**目标**

- 删除 `_extract_task_from_state()`
- 用真实状态形状补齐回归测试
- 让完成标准从“注释和命名看起来像完成”提升为“真实主链路可验证”

**测试范围**

- `executor.py`
- `tests/unit/test_single_context_protocol_completion.py`
- 新增的 end-to-end style unit tests

**新增/修改测试**

- `tests/unit/test_single_context_protocol_completion.py`
  - 强化为“代码中不再存在 `_extract_task_from_state`”
- `tests/unit/test_single_context_protocol_tdd.py`
  - 覆盖真实 `PipelineState -> NodeRunState -> executor/context extraction`

**验收标准**

- `executor.py` 中不再定义 `_extract_task_from_state`
- 新增测试可以证明主链路上下文不会丢失
- 目标测试集全绿

## 4. 实施顺序

### 阶段 1：红灯

1. 新建 `tests/unit/test_single_context_protocol_tdd.py`
2. 写出 Spec A / B / C / D 的失败测试
3. 运行目标测试，记录失败点

### 阶段 2：绿灯

1. 修复 `executor` 的上下文归一化
2. 补齐 `NodeExecutionContext` 的 evaluator criteria
3. 让 `ContextManager` 和 `EvaluatorAgentInput` 使用真实 criteria
4. 收敛 `DualAgentNode` 旧执行路径到新协议
5. 删除 `_extract_task_from_state()`

### 阶段 3：重构

1. 提炼 legacy-to-SCP 适配逻辑，避免在多个入口重复解析
2. 清理注释和文档中与旧行为不一致的描述
3. 保留兼容接口，但让兼容层足够薄

## 5. 目标测试集

执行时至少覆盖以下测试：

```bash
pytest -q -p no:pytestqt tests/unit/test_node_execution_context.py
pytest -q -p no:pytestqt tests/unit/test_contract_builder.py
pytest -q -p no:pytestqt tests/unit/test_single_context_protocol_completion.py
pytest -q -p no:pytestqt tests/unit/test_single_context_protocol_tdd.py
```

如有需要，再补跑：

```bash
python -m py_compile autoBMAD/docuswarm/node_execution/contracts.py autoBMAD/docuswarm/node_execution/context_builder.py autoBMAD/docuswarm/node_execution/executor.py autoBMAD/docuswarm/context/isolation.py autoBMAD/docuswarm/nodes/dual_agent.py autoBMAD/docuswarm/agents/evaluator.py
```

## 6. 预期代码变更

预计会修改以下文件：

- `autoBMAD/docuswarm/node_execution/contracts.py`
- `autoBMAD/docuswarm/node_execution/context_builder.py`
- `autoBMAD/docuswarm/node_execution/executor.py`
- `autoBMAD/docuswarm/context/isolation.py`
- `autoBMAD/docuswarm/nodes/dual_agent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `tests/unit/test_single_context_protocol_completion.py`
- `tests/unit/test_single_context_protocol_tdd.py`

## 7. 完成定义

只有当以下条件同时成立时，本方案才算执行完成：

1. `pipeline` 与 `standalone` 两种入口都能产出统一、可消费的 `original_context`
2. `EvaluatorAgentInput.criteria` 从 execution context 直接获得
3. `DualAgentNode` 旧入口不再承担旧协议逻辑，只做适配
4. `_extract_task_from_state()` 已从代码中删除
5. 目标测试集通过

## 8. 交付物

本次执行完成后应产出：

1. 本 TDD 方案文档
2. 新增/更新的回归测试
3. 协议收敛实现代码
4. 测试执行结果总结
