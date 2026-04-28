# P0-1 单一上下文协议收尾 TDD 执行报告

> 日期：2026-03-17
> 对应方案：`docs/solution/2026-03-17-p0-1-single-context-protocol-tdd-plan.md`

## 1. 执行结果

本次 TDD 收尾已完成方案中的四个规格：

1. `Spec A: 统一 original_context 归一化`
2. `Spec B: 闭合 Evaluator 契约`
3. `Spec C: 收敛旧执行入口`
4. `Spec D: 清理遗留与补强回归`

整体状态：**已执行完成**

## 2. 新增与修改的测试

### 新增

- `tests/unit/test_single_context_protocol_tdd.py`

覆盖内容：

- pipeline 累计 JSON 上下文归一化
- standalone 文件路径上下文归一化
- `ContextManager` 对归一化上下文的消费
- `evaluator_criteria` 从 execution context 到 evaluator input 的透传
- `DualAgentNode.execute()` 对 `execute_with_context()` 的适配
- `DualAgentNode.execute_with_iteration()` 对结构化输入链路的使用
- `executor.py` 中删除 `_extract_task_from_state()`

### 修改

- `tests/unit/test_node_execution_context.py`

调整内容：

- 将一个依赖宿主临时目录权限的文件路径测试改为使用仓库内 `.tmp/`，避免环境权限噪音影响协议验证

## 3. 实现变更

### 上下文协议

- `autoBMAD/docuswarm/node_execution/contracts.py`
  - 为 `NodeExecutionContext` 增加可选 `evaluator_criteria`

- `autoBMAD/docuswarm/node_execution/context_builder.py`
  - 在构建 execution context 时注入 evaluator criteria

- `autoBMAD/docuswarm/node_execution/executor.py`
  - 让 `_parse_original_context()` 同时支持：
    - pipeline 累计 JSON
    - standalone context 文件路径
    - 原始文本
  - 新增归一化逻辑，确保顶层 `content` 稳定存在
  - 删除 `_extract_task_from_state()`

### ContextManager / Evaluator

- `autoBMAD/docuswarm/context/isolation.py`
  - 增强 `original_context_summary` 提取逻辑，兼容真实 pipeline 结构
  - `build_evaluator_input()` 传递真实 criteria，而不是空列表

- `autoBMAD/docuswarm/agents/evaluator.py`
  - `execute_with_input()` 优先使用结构化传入的 criteria，空时回退到 `self.criteria`

### 旧入口收敛

- `autoBMAD/docuswarm/nodes/dual_agent.py`
  - 新增 legacy -> SCP 的 execution context 适配逻辑
  - `execute()` 变为对 `execute_with_context()` 的薄适配层
  - `execute_with_iteration()` 切换到 `build_independent_input()` / `build_evaluator_input()` 和 `execute_with_input()` 链路

## 4. 测试结果

执行通过的目标测试集：

```bash
pytest -q -p no:pytestqt tests/unit/test_node_execution_context.py tests/unit/test_contract_builder.py tests/unit/test_single_context_protocol_completion.py tests/unit/test_single_context_protocol_tdd.py
```

执行通过的语法检查：

```bash
python -m py_compile autoBMAD/docuswarm/node_execution/contracts.py autoBMAD/docuswarm/node_execution/context_builder.py autoBMAD/docuswarm/node_execution/executor.py autoBMAD/docuswarm/context/isolation.py autoBMAD/docuswarm/nodes/dual_agent.py autoBMAD/docuswarm/agents/evaluator.py tests/unit/test_node_execution_context.py tests/unit/test_single_context_protocol_tdd.py
```

## 5. 已关闭的问题

本次执行直接关闭了评估报告中的以下问题：

- pipeline 主链路中 `original_context_summary` 为空
- standalone 流程把 context 文件路径误当正文
- `evaluator_criteria` 未进入结构化上下文
- `ContextManager.build_evaluator_input()` 返回空 criteria
- `DualAgentNode.execute()` 仍使用 `{subject, task}` 旧包装
- `DualAgentNode.execute_with_iteration()` 仍使用旧 context builder
- `executor.py` 中残留 `_extract_task_from_state()`

## 6. 残余风险

### 环境噪音

- 当前仓库对 `.pytest_cache` 目录仍存在宿主权限警告
- 这不会影响本次目标测试集是否通过，但会在 pytest 输出中出现 warning

### 未覆盖面

- 本次主要完成了 P0-1 收敛链路
- `shared_context` / `docs_context` 的完整消费闭环仍属于后续范围，不在本次收尾主目标内

## 7. 结论

按本次方案定义的完成标准，P0-1 的收尾修复已经完成核心闭环：

- 真实上下文入口已统一到单一协议可消费形状
- evaluator 契约已结构化透传
- 旧执行入口已收敛为适配层
- 遗留 task 猜测 helper 已删除
- 目标回归测试集已通过
