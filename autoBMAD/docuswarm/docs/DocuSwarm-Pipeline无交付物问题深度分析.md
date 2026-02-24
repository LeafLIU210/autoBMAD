# DocuSwarm Pipeline无交付物问题深度分析

## 问题现象

**命令**: `python -m autoBMAD.docuswarm start -c docs/proposal.md`

**观察到的症状**:
1. ✅ Pipeline显示状态为`completed` 
2. ✅ Current Node显示为`po`
3. ❌ **`output/pipeline-{id}/`目录为空,无任何交付物文件**
4. ❌ 日志显示所有节点执行**立即失败** (`node_execution_failed`)

---

## 根因定位

### 1. 节点执行失败的调用链

通过深度分析`docuswarm-2026-02-24.log`,定位到关键异常流程:

```log
2026-02-24T16:17:29.444493 [info] node_id=analyst message="node_execution_started"
2026-02-24T16:17:29.444493 [error] node_id=analyst message="node_execution_failed"
```

**时间差异**: `0ms` - 节点启动后**立即失败**,未进行任何实际执行。

#### 1.1 执行调用栈

```
orchestrator.start_pipeline()
  ↓
graph.ainvoke(initial_state, config)
  ↓
[LangGraph自动执行]
  ↓
create_integrated_node_executor(node_id, session_manager)  # graph.py:265
  ↓
await executor(node_id, new_state)  # graph.py:352
  ↓
create_node_executor(node_id, session_manager)  # executor.py:34
  ↓
await _execute_node(state, node_id, session_manager, logger)  # executor.py:75
  ↓
try-catch捕获异常 → status=FAILED  # executor.py:203-212
```

### 2. 异常发生点

根据`executor.py:203-212`,异常捕获逻辑:

```python
except Exception as e:
    logger.error(
        "node_execution_failed",
        node_id=node_id,
        run_id=run_id,
        error=str(e),
        error_type=type(e).__name__,
    )
    # Set status to failed on exception
    new_state["status"] = FAILED
```

**关键问题**: 日志中**没有记录`error`和`error_type`字段**,表明:
- 可能是structlog配置问题,未输出完整字段
- 或者异常信息为空/被截断

### 3. 可能的异常原因

#### 3.1 IndependentAgent执行失败

从`independent.py:412-564`分析,可能触发异常的点:

**P1级别问题**: `pipeline_id`缺失
```python
# independent.py:446-448
pipeline_id: str = context.get("pipeline_id", "")
if not pipeline_id:
    raise IndependentAgentError("pipeline_id is required in context for Story 11.1")
```

**检查初始化状态传递**:
```python
# orchestrator.py:434
initial_state = create_initial_state(final_pipeline_id, subject_context)

# state.py:create_initial_state (需要检查是否包含pipeline_id)
```

#### 3.2 Session Manager工作目录问题

```python
# independent.py:494-497
output_dir = self.project_root / "output" / pipeline_id
output_dir.mkdir(parents=True, exist_ok=True)

# 如果pipeline_id为空或无效,会导致路径创建失败
```

#### 3.3 Agent File路径问题

```python
# independent.py:502-503
self._agent_file = (
    self.project_root / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
)

# 如果project_root计算错误,agent_file不存在会导致session创建失败
```

### 4. 为什么Pipeline显示为`completed`?

**答案**: LangGraph的状态更新逻辑

```python
# orchestrator.py:469-477
result: dict[str, Any] = await graph.ainvoke(initial_state, config)

# Update status to completed and sync current_node from final state
final_current_node = result.get("current_node", "po")
_ = self._state_manager.update_pipeline_status(
    final_pipeline_id,
    status="completed",  # ← 无条件设置为completed
    current_node=final_current_node,
)
```

**问题**: `ainvoke`即使失败也会返回结果,orchestrator**未检查节点执行状态**就直接标记为completed。

### 5. 为什么没有交付物?

交付物创建的两个路径都未执行:

#### 5.1 Tool层创建 (create_deliverable工具)

```python
# create_deliverable.py:72-95
async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
    filename = _slugify_filename(params.title)
    file_path = Path.cwd() / filename  # ← 写入SDK的work_dir
    
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(params.content)
```

**条件**: LLM必须调用`create_deliverable`工具
**现状**: 节点立即失败,LLM未被调用,工具未执行

#### 5.2 FileStorage层保存

```python
# graph.py:381-404
status = executed_node_state.get("status")
if status in ("completed", "approved") and executed_node_state.get("deliverable"):
    _run_async(
        _save_deliverable_async(
            pipeline_id,
            node_id,
            executed_node_state["deliverable"],
            output_root=output_root,
        )
    )
```

**条件**: `status` = "completed"/"approved" **且** `deliverable`存在
**现状**: 
- `status` = "failed" (executor.py:212设置)
- `deliverable` = None (未执行到IndependentAgent)

---

## 验证假设

### 需要检查的关键配置

1. **State初始化** (`state.py:create_initial_state`)
   ```python
   # 检查是否正确设置pipeline_id
   def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]):
       return {
           "pipeline_id": pipeline_id,  # ← 必须存在
           "context_file": ...,
           # ...
       }
   ```

2. **Executor状态传递** (`executor.py:_extract_task_from_state`)
   ```python
   # 检查task提取逻辑是否正确
   context_file = state.get("context_file", "")
   ```

3. **Project Root计算** (`executor.py:124`)
   ```python
   project_root = Path(__file__).parent.parent.parent.resolve()
   # executor.py → node_execution/ → docuswarm/ → autoBMAD/ ← 应该是这个
   ```

4. **Agent文件存在性**
   ```bash
   # 验证路径
   ls -la d:/GITHUB/pytQt_template/autoBMAD/docuswarm/agents/configs/independent_agent.yaml
   ```

---

## 修复方案

### 方案1: 增强异常日志 (立即实施)

**目标**: 捕获真正的异常详情

```python
# executor.py:203-214 修改
except Exception as e:
    import traceback
    
    logger.error(
        "node_execution_failed",
        node_id=node_id,
        run_id=run_id,
        error=str(e),
        error_type=type(e).__name__,
        traceback=traceback.format_exc(),  # ← 添加完整堆栈
    )
    new_state["status"] = FAILED
    new_state["error_message"] = str(e)  # ← 保存到状态
    new_state["error_traceback"] = traceback.format_exc()
```

### 方案2: 状态验证与降级 (中期)

**目标**: 阻止错误标记为completed

```python
# orchestrator.py:469-477 修改
result: dict[str, Any] = await graph.ainvoke(initial_state, config)

# ↓ 添加状态验证
node_states = result.get("node_states", {})
failed_nodes = [
    node_id for node_id, state in node_states.items()
    if state.get("status") == "failed"
]

if failed_nodes:
    logger.error("pipeline_failed_with_errors", failed_nodes=failed_nodes)
    _ = self._state_manager.update_pipeline_status(
        final_pipeline_id,
        status="failed",  # ← 正确设置状态
        current_node=final_current_node,
    )
    raise OrchestratorError(f"Nodes failed: {failed_nodes}")
else:
    _ = self._state_manager.update_pipeline_status(
        final_pipeline_id,
        status="completed",
        current_node=final_current_node,
    )
```

### 方案3: 初始化状态完整性检查 (高优先级)

**目标**: 确保所有必需参数传递正确

```python
# state.py:create_initial_state 添加验证
def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]):
    if not pipeline_id or not pipeline_id.strip():
        raise ValueError("pipeline_id cannot be empty")
    
    # 确保context_file格式正确
    context_str = json.dumps(subject_context)
    
    initial_state = {
        "pipeline_id": pipeline_id,
        "context_file": context_str,  # ← 序列化为JSON
        "subject_context": subject_context,
        # ...
    }
    
    # 验证必需字段
    assert "pipeline_id" in initial_state
    assert "context_file" in initial_state
    return initial_state
```

### 方案4: 路径计算验证 (防御性编程)

```python
# executor.py:124 添加验证
project_root = Path(__file__).parent.parent.parent.resolve()

# 验证agent_file存在
agent_config_path = project_root / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
if not agent_config_path.exists():
    logger.error(
        "agent_config_not_found",
        expected_path=str(agent_config_path),
        project_root=str(project_root),
    )
    raise FileNotFoundError(f"Agent config not found: {agent_config_path}")
```

---

## 下一步行动

### 立即执行 (P0)

1. **修改executor.py添加完整异常日志**
   - 输出traceback和error_type
   - 保存到state.error_message

2. **运行测试命令并收集完整日志**
   ```bash
   python -m autoBMAD.docuswarm start -c docs/proposal.md --verbose
   ```

3. **检查state.py:create_initial_state实现**
   - 确认pipeline_id正确传递
   - 确认context_file格式正确

### 后续验证 (P1)

4. **检查agent配置文件存在性**
   ```bash
   find autoBMAD/docuswarm/agents/configs -name "*.yaml"
   ```

5. **验证project_root计算**
   - 在executor.py添加debug日志
   - 确认路径解析正确

6. **修复orchestrator状态标记逻辑**
   - 添加节点执行结果验证
   - 根据实际状态更新pipeline status

---

## 结论

**核心问题**: 节点执行在启动阶段立即失败,但异常详情未被正确记录,且orchestrator错误地将失败的pipeline标记为completed。

**直接后果**: 
- 无法生成交付物 (节点未执行到LLM调用阶段)
- 状态显示不准确 (completed vs 实际failed)
- 调试困难 (缺少异常堆栈)

**修复优先级**:
1. 🔴 P0: 增强异常日志以定位根因
2. 🟠 P1: 修复状态标记逻辑
3. 🟡 P2: 添加初始化参数验证
4. 🟢 P3: 增强路径计算防御性编程
