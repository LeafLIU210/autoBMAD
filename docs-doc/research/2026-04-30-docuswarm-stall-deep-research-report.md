# 2026-04-30 DocuSwarm Pipeline Stall 深度研究报告

> **研究目标**: 基于 `docs-doc/evaluation/2026-04-30-docuswarm-running-stall-log-review.md` 进行深度根因分析与可执行方案设计  
> **研究工具**: `tools/debug/docuswarm_stall_deep_research.py` (新建)  
> **数据来源**: 代码静态分析、SQLite DB 审计、日志审计、进程状态检查、文件系统审计  
> **报告时间**: 2026-04-30 CST  

---

## 目录

1. [执行摘要](#执行摘要)
2. [研究方法论](#研究方法论)
3. [假设验证结果](#假设验证结果)
4. [根因链深度分析](#根因链深度分析)
5. [P0 关键问题详解](#p0-关键问题详解)
6. [P1 重要问题详解](#p1-重要问题详解)
7. [P2 一般问题详解](#p2-一般问题详解)
8. [架构层面分析](#架构层面分析)
9. [修复方案与实施指导](#修复方案与实施指导)
10. [测试矩阵](#测试矩阵)
11. [风险评估与影响面](#风险评估与影响面)
12. [附录：调试工具输出](#附录调试工具输出)

---

## 执行摘要

本次深度研究通过 **代码静态分析** + **运行时数据审计** + **架构交叉验证** 的三重方法，对 2026-04-30 的 DocuSwarm pipeline stall 事件进行了系统性根因追踪。

### 核心结论

DocuSwarm 当前面临的根本问题不是"某个 agent 失败了"，而是 **pipeline 执行链路缺少中断 finalization 机制**。这导致任何外部中断（用户 Ctrl+C、进程被杀、容器停止、IDE 终止）都会让 DB 中的 pipeline 永久停留在 `running` 状态，且无法恢复。

### 关键数据

| 指标 | 数值 |
|------|------|
| DB 中 `running` pipeline 数量 | **5 个** |
| 其中空输出目录的 pipeline | **2 个** |
| 当前实际运行的 DocuSwarm 进程 | **0 个** |
| 最新日志 terminal 事件 | **全部缺失** |
| 代码中中断处理覆盖率 | **0%** (orchestrator/CLI/agent 层) |

### 发现分类

| 严重度 | 数量 | 代表问题 |
|--------|------|----------|
| Critical | 4 | 永久 running、日志中断、全链路无 finalization、CLI 不捕获中断 |
| High | 3 | SessionManager 泄漏、session 未持久化、DB 缺少 lease 机制 |
| Medium | 5 | 取消语义丢失、SummaryAgent 超时、summary 未同步、node_runs 未使用、空输出目录 |

### 修复优先级

1. **第一优先级**：添加中断 finalization（orchestrator + CLI + atexit）
2. **第二优先级**：添加 stale-running 检测与 lease/heartbeat 机制
3. **第三优先级**：持久化 in-flight session 与节点运行记录
4. **第四优先级**：修复资源生命周期（SessionManager close_all）
5. **第五优先级**：修正错误语义（cancellation vs empty response）与 SummaryAgent 稳定性

---

## 研究方法论

### 使用的工具

| 工具 | 路径 | 用途 |
|------|------|------|
| `docuswarm_stall_deep_research.py` | `tools/debug/` (本次新建) | 综合静态分析与数据审计 |
| SQLite3 | `docuswarm.db` | DB 状态审计 |
| 日志分析 | `logs/docuswarm-2026-04-30.log` | 运行时轨迹验证 |
| 代码阅读 | 8 个核心源文件 | 异常处理路径验证 |

### 分析维度

1. **异常处理路径扫描**：检查所有关键文件的 `try/except/finally` 结构，验证是否覆盖 `Exception` 以外的中断类型
2. **状态持久化审计**：验证 graph 执行前、中、后各阶段的状态写入点
3. **资源生命周期追踪**：验证 SessionManager 的创建、使用、销毁全链路
4. **数据库一致性检查**：验证 `pipelines` / `node_runs` / `node_results` / `shared_context_history` 四表的数据完整性
5. **日志终止事件分析**：检查预期应出现但未出现的日志事件
6. **假设验证**：对评估报告中的 H1/H2/H3 进行数据层面的确认或证伪

---

## 假设验证结果

### H1: pipeline 并非 SummaryAgent 阶段失败

**状态**: ✅ **已确认**

**证据链**:

```text
日志: summary_generation_complete success_count=1 failure_count=0
日志: documents_summarized count=1
日志: node_execution_started node_id=analyst
```

SummaryAgent 虽然第一次调用被取消（33.7s 超时），但第二次重试在 18.1s 成功返回 JSON summary。pipeline 明确进入了 `analyst` 节点执行阶段。

### H2: pipeline 停在 analyst IndependentAgent 的 SDK session 消息流阶段

**状态**: ✅ **已确认**

**证据链**:

```text
日志: session_created session_id=session_5d79b774cc4f
日志: llm_message_received message_index=1..5 (System, Assistant, Assistant, User, Assistant)
缺失: llm_prompt_complete
缺失: llm_tool_call
缺失: independent_agent_completed
缺失: node_execution_completed
缺失: pipeline_started
```

日志在 `2026-04-30T19:25:12.241100+08:00` 收到第 5 条 AssistantMessage 后完全停止。此后没有任何 terminal event。

### H3: DB 的 running 状态已失真

**状态**: ✅ **已确认**

**证据链**:

```text
DB: 5 个 status=running 的 pipeline
进程: 0 个 docuswarm/claude 相关进程
输出目录: 2 个空目录 (pipeline-1777548246143-43a13bf8 等)
node_runs 表: 所有 running pipeline 的 node_runs_count=0
node_results 表: 所有 running pipeline 的 node_results_count=0
```

这 5 个 running pipeline 已经没有任何进程持有，是典型的 **stale running** 状态。

---

## 根因链深度分析

### 完整根因链

```
用户/外部触发中断 (Ctrl+C / kill / 容器停止 / IDE 终止)
    ↓
Python 进程收到 KeyboardInterrupt 或 SIGTERM
    ↓
asyncio event loop 取消正在运行的 coroutine
    ↓
graph.ainvoke() 抛出 asyncio.CancelledError
    ↓
HybridOrchestrator.start_pipeline() 的 except Exception 无法捕获 CancelledError
    ↓
不会执行 update_pipeline_state(status="failed/cancelled")
    ↓
DB 仍保留 graph 前写入的 status=running, current_node=analyst
    ↓
finally 块只关闭 checkpointer conn，不更新状态
    ↓
CLI start.py 的 except Exception 同样无法捕获 KeyboardInterrupt
    ↓
进程直接退出，DB 状态永久失真
```

### 为什么不是 SummaryAgent 的问题？

SummaryAgent 的第一次 `single_prompt_cancelled` 发生在 `19:24:06` 到 `19:24:39`，第二次重试成功在 `19:24:57`。而 analyst session 创建于 `19:25:00`，日志停止于 `19:25:12`。两者相隔约 15 分钟内的不同时间点，SummaryAgent 的问题已被 retry 恢复，不是最终阻断点。

### 为什么不是 SDK timeout/idle 的问题？

如果 SDK idle timeout 或 total timeout 触发，日志应出现：
- `prompt_idle_exceeded`
- `prompt_timeout`
- `llm_call_error`

这些日志全部缺失。因此不是 SDK 内部 timeout 机制触发的中断。

### 为什么不是节点逻辑错误？

如果 analyst 节点内部逻辑出错（如 JSON 解析失败、工具调用失败），日志应出现：
- `node_execution_failed`
- `integrated_executor_error`
- `evaluator_agent_failed`

这些日志也全部缺失。因此不是节点执行逻辑错误。

### 最可能的外部中断原因

当前证据无法 100% 确定是哪一种外部中断，但以下都是合理候选：

| 候选原因 | 可能性 | 说明 |
|----------|--------|------|
| 用户手动 Ctrl+C | 中 | CLI 运行中最常见的中断方式 |
| IDE/编辑器终止进程 | 中 | 开发测试时常见 |
| 容器/宿主机资源回收 | 低 | 当前环境非容器化 |
| 外部 supervisor kill | 低 | 无 supervisor 配置证据 |
| Claude SDK 子进程异常退出 | 低 | 父进程应记录相关错误日志 |

**关键洞察**：无论具体是哪种外部中断，系统都应该有能力 **最终化状态**，而不是让状态永久失真。这是本次研究的核心结论。

---

## P0 关键问题详解

### P0-1: graph 执行中断会留下永久 running 的 pipeline

#### 代码证据

**`orchestrator.py:512-525`**

```python
except Exception as e:
    logger.error("pipeline_execution_error", error=str(e))
    _ = await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        {"status": "failed"},
    )
    return {
        "pipeline_id": final_pipeline_id,
        "status": FAILED,
        ...
    }
finally:
    # Close checkpointer connection to prevent process hang
    if checkpointer is not None and hasattr(checkpointer, "conn"):
        try:
            await checkpointer.conn.close()
        except Exception:
            pass
```

**问题分析**:

1. `except Exception` 在 Python 3.8+ 的 async 代码中**不捕获 `asyncio.CancelledError`**（PEP 479 之后 `CancelledError` 继承自 `BaseException`）
2. 即使 `KeyboardInterrupt`（继承自 `BaseException`）也不会被捕获
3. `finally` 块只关闭 checkpointer，不更新 pipeline 状态
4. 这意味着**任何 BaseException 都会绕过状态更新**

**`cli/commands/start.py:28-53`**

```python
def start(context_file: str) -> None:
    service = PipelineService()
    try:
        result = asyncio.run(service.start(context_file))
        ...
    except click.ClickException:
        raise
    except FileNotFoundError as e:
        ...
    except Exception as e:
        console.print(f"[red]Error: Failed to start pipeline: {e}[/red]")
        raise click.ClickException(f"Failed to start pipeline: {e}") from e
```

**问题分析**:

1. `asyncio.run()` 在用户按 Ctrl+C 时会将 `KeyboardInterrupt` 传播到调用者
2. CLI 没有 `except KeyboardInterrupt` 分支
3. 即使 orchestrator 层修复了 `CancelledError` 处理，CLI 层的 `KeyboardInterrupt` 仍然会直接退出

#### 影响面

- `docuswarm list --status running` 展示已不存在的 pipeline
- `docuswarm resume` 可能误报 "already running"
- 用户无法判断 pipeline 是否真的在运行
- 自动化调度和清理逻辑会累积 stale pipeline

#### 修复方案

**方案 A: orchestrator 层添加 CancelledError 处理** (推荐，最小侵入)

```python
# orchestrator.py:512
except asyncio.CancelledError as e:
    logger.warning("pipeline_cancelled", error_type=type(e).__name__)
    _ = await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        {
            "status": "cancelled",
            "error": {"message": str(e), "type": type(e).__name__},
        },
    )
    raise  # Re-raise after state update

except KeyboardInterrupt:
    logger.warning("pipeline_interrupted", error_type="KeyboardInterrupt")
    _ = await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        {
            "status": "interrupted",
            "error": {"message": "User interrupted", "type": "KeyboardInterrupt"},
        },
    )
    raise

except Exception as e:
    # 原有逻辑不变
    ...
```

**方案 B: CLI 层添加 KeyboardInterrupt 处理**

```python
# cli/commands/start.py
def start(context_file: str) -> None:
    service = PipelineService()
    try:
        result = asyncio.run(service.start(context_file))
        ...
    except KeyboardInterrupt:
        # asyncio.run 已经将 CancelledError 转换为 KeyboardInterrupt
        console.print("[yellow]Pipeline interrupted by user[/yellow]")
        # Note: 如果 orchestrator 已经处理了状态更新，这里不需要重复
        # 但如果 orchestrator 没来得及处理（如 SIGKILL），这里可以作为兜底
        raise click.ClickException("Pipeline interrupted")
```

**方案 C: 添加 atexit handler 作为最后兜底**

```python
# pipeline_service.py 或 orchestrator.py
import atexit
import os

class PipelineService:
    def __init__(self, db_path: str | None = None) -> None:
        ...
        self._current_pipeline_id: str | None = None
    
    async def start(self, context_file: str) -> dict[str, Any]:
        ...
        self._current_pipeline_id = result.get("pipeline_id")
        # Register atexit for this pipeline
        atexit.register(self._emergency_finalize, self._current_pipeline_id)
        try:
            result = await orchestrator.start_pipeline(subject_context)
        finally:
            atexit.unregister(self._emergency_finalize)
            self._current_pipeline_id = None
        return result
    
    def _emergency_finalize(self, pipeline_id: str | None) -> None:
        """Emergency finalization on unclean exit."""
        if pipeline_id is None:
            return
        # atexit 中不能调用 async，需要同步方式
        try:
            import sqlite3
            conn = sqlite3.connect(str(self._db_path))
            conn.execute(
                "UPDATE pipelines SET status = 'interrupted', updated_at = CURRENT_TIMESTAMP "
                "WHERE pipeline_id = ? AND status = 'running'",
                (pipeline_id,)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
```

> **注意**: atexit 对 `SIGKILL` 无效，但对 `SIGTERM` 和正常进程退出有效。

---

### P0-2: in-flight session 未持久化，resume 无法恢复当前节点会话

#### 代码证据

**`agents/independent.py:1035-1061`**

```python
pipeline_session_manager = self._create_pipeline_session_manager(
    work_dir=output_dir,
    node_id=node_id,
    ...
)

original_session_manager = self.session_manager
self.session_manager = pipeline_session_manager

try:
    response = await self._call_llm_with_prompts(
        system_prompt_append=system_prompt,
        user_prompt=user_prompt,
        timeout=timeout,
    )
finally:
    # Restore original session_manager
    self.session_manager = original_session_manager

# Parse and validate response
output = self._parse_response(response)
```

**问题分析**:

1. `_create_pipeline_session_manager()` 内部调用 `SessionManager(...)` 创建新实例
2. `SessionManager.create_session()` 生成 session_id 后只保存在内存 `_active_clients` / `_active_wrappers` 中
3. `IndependentAgent` 没有任何代码将 session_id 回写到 pipeline state
4. `HybridOrchestrator.resume_pipeline()` 期望从 `checkpoint_state.get("current_node_session_id")` 读取 session_id，但永远是 `null`

#### 影响面

- `resume` 功能名存实亡：即使日志里有 `session_created session_5d79b774cc4f`，系统持久化状态不知道它
- 中断后只能重跑整个节点，无法恢复已有的 LLM 对话上下文
- 对于需要多轮迭代的节点，重复工作成本高

#### 修复方案

在 session 创建后添加状态回写：

```python
# agents/independent.py 中 session 创建后
session_id = await pipeline_session_manager.create_session(...)

# 回写 pipeline state
if pipeline_id and self.state_manager:  # 需要传递 state_manager 引用
    await self.state_manager.update_pipeline_state(
        pipeline_id,
        {
            "current_node_session_id": session_id,
            "session_ids": {node_id: session_id},
            "session_metadata": {
                node_id: {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "cwd": str(cwd),
                    "output_dir": str(output_dir),
                    "allowed_tools": [...],
                }
            }
        }
    )
```

同时需要修改 `orchestrator.py` 在 `_execute_node` 或 graph 层面传递 `state_manager` 引用给 `IndependentAgent`。

---

### P0-3: 节点专用 SessionManager 没有在 finally 中关闭

#### 代码证据

见 P0-2 的代码片段，`finally` 中只有：

```python
finally:
    # Restore original session_manager
    self.session_manager = original_session_manager
```

缺少：

```python
    await pipeline_session_manager.close_all()
```

**问题分析**:

1. 节点专用 `pipeline_session_manager` 持有 Claude SDK client 和可能的 subprocess
2. 正常路径中，`_call_llm_with_prompts()` 返回后 `_parse_response()` 执行，然后 `execute_with_input()` 返回
3. 但返回后没有关闭 `pipeline_session_manager`
4. 异常/取消路径中，`finally` 只恢复引用，不关闭资源
5. `PipelineService.start()` 的 `finally` 只关闭外层全局 `session_manager`，关闭不到节点内部创建的 manager

#### 影响面

- 残留 Claude CLI subprocess，消耗系统资源
- 残留网络连接（如果 SDK client 持有长连接）
- 多次运行后可能触发进程数/文件描述符限制
- 虽然本次审查时未发现仍存活进程，但这是结构性资源生命周期缺口

#### 修复方案

```python
# agents/independent.py
try:
    response = await self._call_llm_with_prompts(...)
finally:
    self.session_manager = original_session_manager
    await pipeline_session_manager.close_all()
```

并添加单元测试验证三种路径：

```python
async def test_session_manager_closes_on_all_paths():
    # 1. 成功路径
    # 2. LLMError 路径
    # 3. asyncio.CancelledError 路径
    # 断言: mock_pipeline_session_manager.close_all.assert_called_once()
    # 断言: agent.session_manager 恢复为 original
```

---

## P1 重要问题详解

### P1-1: `single_prompt()` 吞掉 cancellation，导致真实取消被误报为空响应

#### 代码证据

**`llm/session_manager.py:824-826`**

```python
except asyncio.CancelledError:
    self._logger.info("single_prompt_cancelled")
    return []
```

**问题分析**:

1. `asyncio.CancelledError` 被捕获后返回空列表 `[]`
2. 上层 `SummaryAgent._generate_summary()` 调用 `_extract_text_from_response(response)`
3. 空列表导致 `summary_text` 为空，触发 `raise LLMSummaryError("Empty response from LLM")`
4. 日志最终显示 `llm_call_failed error=Empty response from LLM error_type=LLMSummaryError`
5. 调用方完全丢失了"这是被取消"的真实语义

#### 影响面

- 错误分类错误：cancelled 被记录为 empty response
- 可能触发无意义重试：如果 cancellation 来自外部（如用户中断），重试是无意义的
- 调试困难：运维人员看到 "Empty response" 会怀疑 API/网络问题，而不是执行被取消

#### 修复方案

**方案 A: 重新抛出 CancelledError** (推荐)

```python
except asyncio.CancelledError:
    self._logger.info("single_prompt_cancelled")
    raise  # Re-raise 让上层决定如何处理
```

上层 `SummaryAgent` 需要相应处理：

```python
except asyncio.CancelledError:
    # 不记录为 Empty response，直接传播
    raise
except LLMSummaryError:
    # 真正的 LLM 错误才重试
    ...
```

**方案 B: 包装成带类型的 LLMError**

```python
except asyncio.CancelledError as e:
    self._logger.info("single_prompt_cancelled")
    raise LLMError(
        "LLM prompt was cancelled",
        api_error_type="CancelledError",
    ) from e
```

这样上层可以区分：

```python
try:
    response = await self.session_manager.single_prompt(...)
except LLMError as e:
    if e.api_error_type == "CancelledError":
        # 不重试，直接传播
        raise
    # 其他错误才重试
```

---

### P1-2: SummaryAgent 每文档 30 秒 timeout 偏紧

#### 数据证据

| 指标 | 数值 |
|------|------|
| 文件大小 | 1796 bytes |
| 首次调用耗时 | 33.7s (被取消) |
| 第二次调用耗时 | 18.1s (成功) |
| 配置 timeout | 30s |
| 配置 max_retries | 2 |

**问题分析**:

1. 对 1796 bytes 的小文件，33.7s 的首次调用耗时超出了 30s 阈值
2. 这很可能不是"模型慢"，而是**网络波动**或**首次连接建立开销**
3. 30s 的 timeout 通过 `asyncio.wait_for()` 在外部强制取消，导致 `single_prompt()` 抛出 `CancelledError`
4. 由于 P1-1 的问题，这个 cancellation 被包装成 "Empty response from LLM"
5. 第二次重试在同一文档上 18.1s 成功，说明不是模型能力问题

#### 影响面

- 无意义重试增加 API 调用成本和延迟
- 日志噪声：每次超时都会产生 warning/error 级别日志
- 多文档并发时问题放大

#### 修复方案

1. **提升 timeout**: `timeout_per_document_seconds=90` 或 `120`
2. **动态计算**: `timeout = max(30, len(content) / 100)` 或类似公式
3. **区分重试原因**:
   - timeout/cancelled: 不立即重试，或延长 timeout 后重试
   - empty response / JSON parse error: 正常重试
4. **使用 SDK output_format**: 如果 Claude SDK 支持 `output_format="json"`，可以减少格式相关重试

---

### P1-3: `docs_context_summary` 没有在 graph 前同步到 StateManager

#### 代码证据

**`orchestrator.py:451-470`**

```python
# Step 4.6: Generate document summaries before graph execution
docs_context_summary = await self._summarize_referenced_documents(
    subject_context=subject_context,
    repo_root=Path(self._work_dir).parent,
    session_manager=session_manager,
)

# Step 5: Create and execute the pipeline graph
initial_state = create_initial_state(
    final_pipeline_id,
    subject_context,
    docs_context_summary=docs_context_summary,
)
```

**问题分析**:

1. `docs_context_summary` 只在 `create_initial_state()` 中传入 graph state
2. `StateManager.update_pipeline_state()` 没有在 graph 前被调用同步 summary
3. 如果 graph 在 `analyst` 节点中断，DB `state_json` 中的 `docs_context_summary` 是 `[]`
4. 虽然 LangGraph checkpoint 中可能有这个值，但 StateManager 是用户可见状态的主要来源

#### 影响面

- `status` / `resume` / `debug` 命令看不到已成功生成的 summary
- 需要依赖 LangGraph checkpoint 恢复，增加调试复杂度
- state 双轨问题：checkpoint 和 state_json 不一致

#### 修复方案

```python
docs_context_summary = await self._summarize_referenced_documents(...)

# 立即同步到 StateManager
current_state = self._state_manager.get_pipeline_state(final_pipeline_id)
if current_state:
    current_state["docs_context_summary"] = docs_context_summary
    await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        current_state,
    )
```

---

## P2 一般问题详解

### P2-1: `node_results` 与 `node_runs` 未被当前执行链路使用

#### 代码证据

**`node_execution/executor.py:80-246`** (完整 `_execute_node`)

搜索 `node_runs`、`save_node_result`、`node_run` 等关键词，结果均为 **False**。

**数据库 schema** (`storage/database.py:178-207`):

```sql
CREATE TABLE IF NOT EXISTS node_results (...)
CREATE TABLE IF NOT EXISTS node_runs (...)
CREATE TABLE IF NOT EXISTS node_run_metrics (...)
```

表存在但数据为空。

**问题分析**:

1. `_execute_node()` 在内存 `NodeRunState` dict 中更新状态
2. 返回给 LangGraph 后，状态通过 checkpoint 机制持久化
3. 但 `StateManager` 的 `save_node_result()`、`create_node_run()` 等方法没有被调用
4. 这导致 DB 层面缺少节点级的执行历史和生命周期记录

#### 影响面

- 无法回答"哪个节点在什么时间开始、什么 session、什么状态"
- 无法做节点级的性能分析（`node_run_metrics` 同样未使用）
- 与 Story 3.9/5.6 的设计意图不符

#### 修复方案

在 `_execute_node()` 中添加 node run 追踪：

```python
# 节点开始时
node_run_id = f"{pipeline_id}-{node_id}-{iteration}"
state_manager.create_node_run(
    run_id=node_run_id,
    node_id=node_id,
    pipeline_id=pipeline_id,
    status="running",
    start_time=datetime.now(timezone.utc).isoformat(),
)

# session 创建后 (需要在 IndependentAgent 中传递 callback)
state_manager.update_node_run(
    run_id=node_run_id,
    session_id=session_id,
)

# 节点完成/失败时
state_manager.update_node_run(
    run_id=node_run_id,
    status="completed" / "failed" / "cancelled",
    end_time=datetime.now(timezone.utc).isoformat(),
    deliverable_json=json.dumps(deliverable),
    error=str(error) if error else None,
)
```

---

## 架构层面分析

### 状态持久化的"断层"模型

当前 DocuSwarm 的状态持久化呈现明显的 **断层结构**：

```
[Pipeline Start]
    ↓
StateManager: status=running, current_node=analyst  ← 唯一一次 DB 写入
    ↓
LangGraph Checkpoint: 每步写入 SQLite  ← 内部机制，用户不可见
    ↓
[Graph 执行中...]
    ↓  ← 中断发生在这里，上面两层之间有 gap
Memory State: docs_context_summary, session_ids, current_node_session_id  ← 丢失
    ↓
StateManager: 只有 graph 完成后才再次写入  ← 永远不会执行
```

**断层 1**: StateManager 只在 graph 前后写入，graph 执行期间不更新  
**断层 2**: LangGraph checkpoint 与 StateManager state_json 不同步  
**断层 3**: 节点级运行记录（node_runs）完全缺失  
**断层 4**: session 生命周期与 pipeline 状态没有关联  

### 中断传播路径的"真空地带"

```
KeyboardInterrupt / SIGTERM
    ↓
Python 解释器
    ↓
asyncio event loop
    ↓
    ├─→ task.cancel() → CancelledError  ← 不被 except Exception 捕获
    │       ↓
    │   ClaudeSessionWrapper.prompt() 中的 async for
    │       ↓
    │   single_prompt() 捕获 CancelledError → 返回 []  ← 语义丢失
    │       ↓
    │   SummaryAgent 看到 Empty response → 重试  ← 无意义行为
    │       ↓
    │   ...
    │
    └─→ 如果发生在 graph.ainvoke() 中
            ↓
        直接穿透 except Exception
            ↓
        finally 只关闭 checkpointer
            ↓
        进程退出，DB 状态=running  ← 最终问题
```

### 建议的新架构模式：租约 + 心跳 + 最终化

```
Pipeline Execution Lifecycle
============================

[Create]
    ↓
StateManager: status=pending
    ↓
[Start]
    ↓
StateManager: status=running, owner_pid=1234, last_heartbeat=now
    ↓
[Node Enter]
    ↓
StateManager: node_runs 记录创建, current_node_session_id=session_xxx
    ↓
[Heartbeat - every 30s]
    ↓
StateManager: last_heartbeat=now, last_event="message_received"
    ↓
[Complete / Fail / Cancel]
    ↓
StateManager: status=completed/failed/cancelled, owner_pid=null
    ↓
[Cleanup]
    ↓
SessionManager.close_all(), checkpointer.close()
```

**Stale Running Detection**:

```python
def detect_stale_pipelines(threshold_seconds: int = 300) -> list[dict]:
    """Find pipelines that are running but have no alive owner."""
    stale = []
    for pipeline in state_manager.list_pipelines(status="running"):
        owner_pid = pipeline.get("owner_pid")
        last_heartbeat = pipeline.get("last_heartbeat_at")
        
        # Check if owner process still exists
        owner_alive = owner_pid and _pid_exists(owner_pid)
        
        # Check if heartbeat expired
        heartbeat_expired = last_heartbeat and (
            datetime.now() - parse(last_heartbeat)
        ).total_seconds() > threshold_seconds
        
        if not owner_alive or heartbeat_expired:
            stale.append(pipeline)
    return stale
```

---

## 修复方案与实施指导

### 实施优先级矩阵

| 优先级 | 问题 | 工作量 | 风险 | 影响 |
|--------|------|--------|------|------|
| P0 | P0-1 中断 finalization | 小 | 低 | 极高 |
| P0 | P0-3 SessionManager 关闭 | 小 | 低 | 高 |
| P0 | stale-running 检测 | 中 | 低 | 高 |
| P1 | P0-2 session 持久化 | 中 | 中 | 高 |
| P1 | P1-1 取消语义修复 | 小 | 低 | 中 |
| P2 | P1-3 summary 同步 | 小 | 低 | 中 |
| P2 | P1-2 timeout 调整 | 极小 | 低 | 中 |
| P3 | P2-1 node_runs 使用 | 中 | 中 | 中 |

### 第一周实施计划

**Day 1-2: P0-1 中断 finalization**

1. 修改 `orchestrator.py`:
   - `except Exception` 之前添加 `except asyncio.CancelledError` 和 `except KeyboardInterrupt`
   - 两种情况下都先更新 StateManager 状态，然后 `raise`
2. 修改 `cli/commands/start.py`:
   - 添加 `except KeyboardInterrupt` 分支
   - 输出友好的中断提示
3. 添加 atexit handler 作为兜底
4. **测试**: 模拟 `graph.ainvoke()` 抛出 `CancelledError`，断言 DB 状态为 `cancelled`

**Day 3: P0-3 SessionManager 生命周期**

1. 修改 `agents/independent.py`:
   - `finally` 块中添加 `await pipeline_session_manager.close_all()`
2. **测试**: mock `SessionManager`，验证三种路径都调用 `close_all()`

**Day 4-5: stale-running 检测**

1. 修改 `storage/database.py`:
   - 添加 `owner_pid`, `host`, `last_heartbeat_at`, `last_event_at` 字段（使用 ALTER TABLE）
2. 修改 `orchestrator.py`:
   - pipeline 启动时写入 `owner_pid` 和 `last_heartbeat_at`
3. 添加 heartbeat 任务（可在 orchestrator 中使用 `asyncio.create_task()`）
4. 修改 `cli/commands/status.py` 和 `list.py`:
   - 显示 stale 标记
5. **测试**: 构造 running pipeline，模拟进程消失，断言 status 命令显示 stale

### 第二周实施计划

**Day 6-7: P0-2 session 持久化**

1. 修改 `agents/independent.py`:
   - 接受 `state_manager` 和 `pipeline_id` 参数
   - session 创建后回调更新 StateManager
2. 修改 `node_execution/executor.py`:
   - 传递 state_manager 到 `node.execute_with_context()`
3. **测试**: mock session 创建，断言 `current_node_session_id` 写入 DB

**Day 8: P1-1 取消语义**

1. 修改 `llm/session_manager.py`:
   - `except asyncio.CancelledError` 中 `raise` 而不是 `return []`
2. 修改 `agents/summary.py`:
   - 区分 `CancelledError`、`TimeoutError`、空响应、JSON 解析错误
3. **测试**: mock `query()` 抛出 `CancelledError`，断言不返回 `[]`

**Day 9: P1-2 timeout + P1-3 summary 同步**

1. 修改 `config/summary_agent.yaml`:
   - `timeout_per_document_seconds: 90`
2. 修改 `orchestrator.py`:
   - `documents_summarized` 后调用 `update_pipeline_state`
3. **测试**: 验证 summary 超时不再轻易触发；验证中断后 DB 有 summary

**Day 10: P2-1 node_runs**

1. 修改 `node_execution/executor.py`:
   - 节点开始时创建 `node_runs` 记录
   - 完成/失败时更新状态
2. **测试**: 验证节点执行后 `node_runs` 表有记录

---

## 测试矩阵

### T1: Graph Cancellation Finalizes Pipeline

```python
async def test_graph_cancellation_updates_status():
    """模拟 graph.ainvoke() 抛出 CancelledError。"""
    orchestrator = HybridOrchestrator(...)
    
    with mock.patch.object(orchestrator, '_create_checkpointer'):
        with mock.patch('create_pipeline_graph') as mock_graph:
            mock_graph.return_value.ainvoke.side_effect = asyncio.CancelledError()
            
            with pytest.raises(asyncio.CancelledError):
                await orchestrator.start_pipeline(subject_context)
    
    pipeline = orchestrator._state_manager.get_pipeline(pipeline_id)
    assert pipeline["status"] in ("cancelled", "interrupted", "failed")
    assert pipeline["error"]["type"] == "CancelledError"
```

### T2: CLI KeyboardInterrupt Finalizes Pipeline

```python
def test_cli_keyboard_interrupt():
    """模拟用户 Ctrl+C。"""
    runner = CliRunner()
    
    with mock.patch('PipelineService.start') as mock_start:
        mock_start.side_effect = KeyboardInterrupt()
        result = runner.invoke(start, ['--context', 'test.md'])
    
    # 应该显示中断提示，而不是 traceback
    assert result.exit_code != 0
    assert 'interrupted' in result.output.lower() or 'cancelled' in result.output.lower()
```

### T3: Stale-Running Detection

```python
def test_stale_running_detection():
    """构造 running pipeline，owner pid 不存在。"""
    state_manager = StateManager(...)
    pipeline_id = state_manager.create_pipeline("test")
    state_manager.update_pipeline_state(pipeline_id, {
        "status": "running",
        "owner_pid": 99999,  # 不存在的 PID
        "last_heartbeat_at": (datetime.now() - timedelta(hours=1)).isoformat(),
    })
    
    stale = detect_stale_pipelines()
    assert any(p["pipeline_id"] == pipeline_id for p in stale)
```

### T4: Session ID Persistence

```python
async def test_session_id_persistence():
    """mock session 创建，验证 DB 写入。"""
    agent = IndependentAgent(...)
    
    with mock.patch.object(agent, '_create_pipeline_session_manager') as mock_mgr:
        mock_session_mgr = mock.AsyncMock()
        mock_session_mgr.create_session.return_value = "session_test_123"
        mock_mgr.return_value = mock_session_mgr
        
        await agent.execute_with_input(...)
    
    pipeline = state_manager.get_pipeline(pipeline_id)
    assert pipeline["state"]["current_node_session_id"] == "session_test_123"
    assert pipeline["state"]["session_ids"]["analyst"] == "session_test_123"
```

### T5: Per-Node SessionManager Closes on All Paths

```python
async def test_session_manager_closes_on_cancel():
    """验证 CancelledError 路径也调用 close_all。"""
    agent = IndependentAgent(...)
    mock_mgr = mock.AsyncMock()
    agent.session_manager = mock_mgr
    
    with mock.patch.object(agent, '_call_llm_with_prompts') as mock_call:
        mock_call.side_effect = asyncio.CancelledError()
        
        with pytest.raises(asyncio.CancelledError):
            await agent.execute_with_input(...)
    
    mock_mgr.close_all.assert_called_once()
    assert agent.session_manager is mock_mgr  # 已恢复
```

### T6: Cancellation Is Not Empty Response

```python
async def test_cancellation_not_empty_response():
    """mock query 抛出 CancelledError。"""
    session_mgr = SessionManager(...)
    
    with mock.patch('claude_agent_sdk.query') as mock_query:
        mock_query.side_effect = asyncio.CancelledError()
        
        with pytest.raises((asyncio.CancelledError, LLMError)):
            await session_mgr.single_prompt("test")
    
    # 不应该返回 []
    # 日志不应该记录 "Empty response from LLM"
```

---

## 风险评估与影响面

### 用户可见风险

| 风险 | 严重度 | 说明 |
|------|--------|------|
| 假 running pipeline 累积 | 高 | `list --status running` 展示已经不存在的 pipeline |
| resume 误导 | 高 | 用户无法判断 pipeline 是否真的在运行 |
| 输出目录为空但状态 running | 中 | 容易误判为"仍在生成" |
| 调度混乱 | 中 | 自动化系统可能基于错误状态做决策 |

### 工程风险

| 风险 | 严重度 | 说明 |
|------|--------|------|
| 资源泄漏 | 中 | SessionManager 未关闭，残留 subprocess |
| 可恢复性不足 | 高 | session id 未持久化，resume 无法恢复 |
| 可观测性不足 | 高 | 消息流中断没有 last event/heartbeat |
| 错误分类不足 | 中 | cancellation 被包装成 empty response |
| 状态双轨 | 中 | LangGraph checkpoint 与 StateManager 不同步 |

### 业务风险

| 风险 | 严重度 | 说明 |
|------|--------|------|
| API 成本增加 | 低 | SummaryAgent 无意义重试增加 token 消耗 |
| 调试时间成本 | 高 | 运维人员花大量时间分析 "Empty response" 假阳性 |
| 用户体验下降 | 高 | pipeline 频繁中断且无法恢复，降低系统可信度 |

---

## 附录：调试工具输出

### 工具信息

- **工具路径**: `tools/debug/docuswarm_stall_deep_research.py`
- **生成时间**: `2026-04-30T11:46:21.028019+00:00`
- **输出路径**: `tools/debug/docuswarm_stall_research_results.json`

### DB 审计摘要

```json
{
  "pipeline_status_counts": {
    "completed": 6,
    "failed": 3,
    "pending": 4,
    "running": 5
  },
  "missing_lease_fields": [
    "owner_pid",
    "host",
    "last_heartbeat_at",
    "last_event_at"
  ]
}
```

### 日志审计摘要

```json
{
  "latest_log": "docuswarm-2026-04-30.log",
  "total_lines": 156,
  "terminal_events_found": [],
  "terminal_events_missing": [
    "llm_prompt_complete",
    "independent_agent_completed",
    "node_execution_completed",
    "pipeline_started",
    "pipeline_execution_error",
    "prompt_timeout",
    "prompt_idle_exceeded"
  ]
}
```

### 代码审计摘要

```json
{
  "finalization_coverage": {
    "orchestrator": {
      "has_keyboard_interrupt": false,
      "has_cancelled_error": false,
      "has_sigterm": false,
      "has_atexit": false
    },
    "cli_start": {
      "has_keyboard_interrupt": false,
      "has_cancelled_error": false,
      "has_sigterm": false,
      "has_atexit": false
    },
    "independent_agent": {
      "has_keyboard_interrupt": false,
      "has_cancelled_error": false,
      "has_sigterm": false,
      "has_atexit": false
    },
    "session_manager": {
      "has_keyboard_interrupt": false,
      "has_cancelled_error": true,
      "has_sigterm": false,
      "has_atexit": false
    }
  }
}
```

> **注意**: `session_manager` 中的 `has_cancelled_error: true` 是指它捕获了 `CancelledError`，但它是**吞掉**而不是**正确处理**了它。这不算有效的中断处理。

---

## 结论

本次深度研究通过代码分析、数据库审计、日志审查和架构交叉验证，**完全确认了** 2026-04-30 评估报告中的所有关键假设和发现。

DocuSwarm 当前面临的核心问题是 **pipeline 执行链路缺少中断 finalization 机制**。这不是一个局部 bug，而是一个**架构层面的韧性缺口**。任何外部中断都会导致 DB 状态永久失真，且系统没有任何自愈或检测能力。

**最紧迫的修复**是：

1. 在 orchestrator 和 CLI 层添加 `CancelledError` / `KeyboardInterrupt` 处理
2. 添加 pipeline lease / heartbeat 机制
3. 实现 stale-running 检测

这些修复工作量小（第一周可完成）、风险低、影响极高，应该立即排入开发计划。

次要修复（session 持久化、资源生命周期、错误语义）应在第一批次完成后跟进，以构建完整的可观测、可恢复、可最终化的 pipeline 执行系统。
