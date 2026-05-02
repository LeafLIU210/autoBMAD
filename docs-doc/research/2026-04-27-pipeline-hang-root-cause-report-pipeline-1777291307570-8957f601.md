# DocuSwarm Pipeline 挂起深度根因研究报告（修订版）

**报告日期**: 2026-04-27 22:05
**Pipeline ID**: `pipeline-1777291307570-8957f601`
**Subject**: calc-context
**修订说明**: v1 错误将超时配置定性为根因；本版通过对 `claude-agent-sdk` transport 层源码审计与日志模式分析，纠正根因链至 **transport/子进程阻塞** 层面，超时配置降级为"掩盖因素"。

---

## 一、症状重述

| 维度 | 证据 |
|---|---|
| Pipeline 启动 | `2026-04-27T20:01:47.574` `pipeline_work_dir_created` |
| Session 创建 | `20:01:48.022` `session_created` |
| 最后一条日志 | `20:08:54.370` `llm_message_received`（msg_index 未知） |
| 此后静默 | 100.9 分钟，进程未退出，无 error/timeout/complete 日志 |
| DB 状态 | `pipelines.status=pending`，`updated_at=13:44:03`（UTC），`node_results=0`，`checkpoints=2` |
| 日志消息总数 | 95（其中 67 条 `llm_message_received`） |

**关键异常：消息间隔模式**（20:08:54 之前）

| 时段 | gap |
|---|---|
| 20:03:44 → 20:04:38 | 54s |
| 20:04:51 → 20:05:46 | 55s |
| 20:05:57 → 20:06:53 | 56s |
| 20:07:34 → 20:08:02 | 28s |
| **20:08:54 → ∞** | **100+ 分钟** |

~55s 的规律 gap 表明存在 **多轮 LLM round-trip**（每轮 tool_use → SDK 工具执行 → tool_result → 下一轮 API 请求）。最后一条消息后突然完全静默，意味着 **某次 round-trip 未能完成**。

---

## 二、真正的根因链（自底向上重建）

### 层级 L0：Claude Agent SDK 的 Transport 架构（结构性基础）

通过对 `venv/Lib/site-packages/claude_agent_sdk/_internal/transport/subprocess_cli.py` 的源码审计，确认：

```
父进程 (docuswarm Python)
  │
  ├── ClaudeSDKClient
  │     └── Query._message_receive (anyio memory object stream)
  │           └── _read_messages_impl()
  │                 └── async for line in self._stdout_stream:   ← **阻塞点**
  │                       self._stdout_stream = TextReceiveStream(process.stdout)
  │
  └── [subprocess pipe]
        │
        ▼
  子进程 `claude --output-format stream-json --input-format stream-json`
        │
        └── 内部 HTTP 客户端 → Kimi 网关 (https://api.kimi.com/coding/)
              └── 流式响应 (SSE/chunked HTTP)
```

**关键事实**：
1. `ClaudeSDKClient.receive_messages()` 不是直接与 LLM API 通信，而是 **读取 `claude` CLI 子进程的 stdout**。
2. 读取终止条件是子进程输出 `{"type": "end"}` 或关闭 stdout。
3. **父进程对子进程内部的 HTTP 状态完全不可见**。

### 层级 L1：直接触发原因（最可能）— 上游 HTTP 流式响应半开

`claude` CLI 子进程向 Kimi 网关发起的某一轮请求，TCP 连接进入**半开状态**（half-open）：
- 中间代理（企业 proxy、Kimi 侧 gateway、ISP 中转）因 idle 超时悄然 RST 或丢弃连接；
- 子进程的 HTTP 客户端（很可能 undici/fetch）未收到 FIN，`recv()` 无限等待；
- 子进程 stdout 无新内容 → 父进程 `TextReceiveStream` 的 `async for line` 阻塞；
- 父进程 `receive_messages()` → `independent.py:434` `async for msg in session.prompt(...)` 阻塞。

**佐证**：
- 日志中存在 ~55s 的周期性 gap — 符合 "等待上游模型长推理 + 一次工具 round-trip" 模式；
- 最后两条消息间隔仅 10ms（20:08:54.360 → 20:08:54.370），**典型的 assistant text + tool_use 连发**；
- 静默期开始于 tool_use 发出后，表明 SDK 可能正在等待执行完 tool 的 LLM 下一轮响应；
- 最后 msg_index 未打印到文本日志（`llm_message_received` 只保留了字面消息，`msg_type` 字段被结构化序列化丢失），无法直接确认最后消息类型，但 10ms 连发极强暗示 tool_use pair。

### 层级 L2：并发备选原因（可能性递减）

| 备选假设 | 证据支持度 | 备注 |
|---|---|---|
| A. CLI 子进程内部死锁（stdout buffer 阻塞） | 低 | TextReceiveStream 基于 anyio 非阻塞 I/O，子进程 stdout 有输出时应立即 flush |
| B. in-process MCP 工具死循环 | 低 | `create_deliverable_tool` / `submit_execution_report_tool` 为纯文件写+JSON，无阻塞 I/O |
| C. Kimi 网关主动 hold 连接（长推理 > 100min） | 很低 | 正常 thinking 最多几十秒 |
| D. 上游网关 RST 未到达（半开连接） | **高** | 与日志模式完全吻合；Windows + 代理环境易发 |
| E. asyncio 事件循环饿死 | 极低 | 循环中只有 await，无 CPU 密集 |

### 层级 L3：掩盖因素（**不是**根因，但使故障变成永久挂起）

以下 3 个被 v1 报告误认为根因的问题，本质上是"让故障从可恢复变成永久"的**放大器**：

1. **timeout 传递链污染**（`nodes/dual_agent.py:343`）
   ```python
   timeout=getattr(self.config, "agent_timeout", 300)  # 传入 7200s
   ```
   这使 `session.prompt()` 的 `asyncio.timeout(7200)` 覆盖了默认 900s 保护。但即使是 900s，也无法解除**子进程 stdout 层的阻塞**——`asyncio.timeout` 取消的是父进程的 task，子进程依然残留运行。

2. **Node 级无 wait_for 包裹**（`node_execution/executor.py:155`）
   ```python
   result_dict = await node.execute_with_context(execution_context)  # 裸 await
   ```
   缺少节点级独立超时控制。

3. **Pipeline 级无总超时**（`pipeline/orchestrator.py:477`）
   ```python
   await graph.ainvoke(initial_state, config)  # 裸 await
   ```
   缺少 LangGraph 执行的总预算守护。

**关键澄清**：即使立刻修复上述三处，也只能实现"在 15–120 分钟后强制 cancel"，**不能阻止挂起本身发生**，也无法自动清理残留的 `claude` CLI 子进程。

### 层级 L4：可观测性与架构缺陷（为什么难以诊断）

| 缺陷 | 影响 |
|---|---|
| `llm_message_received` 日志未落地 `msg_type` 字段 | 无法区分 last message 是 text / tool_use / result |
| 未捕获 CLI 子进程 stderr | 子进程若打印 HTTP 错误/警告，Python 端完全看不到 |
| 无 idle timeout（上次消息时间戳） | 即使 stdout 静默 5 分钟，系统也不告警 |
| 无子进程健康检测（poll returncode） | 无法感知子进程是否僵死 |
| LangGraph checkpoint 写入但 `node_results` 为 0 | DB 层对"节点未完成但在执行"的状态不可查询 |
| pipeline DB 的 `updated_at` 不随日志滚动刷新 | 无法从 DB 侧识别"活跃但卡住"的 pipeline |

---

## 三、根因关系图

```
                   [根因 R1 - 直接触发]
               上游 HTTP 流式连接半开 (Kimi 网关)
                            │
                            ▼
                claude CLI 子进程 stdout 静默
                            │
                            ▼
           父进程 TextReceiveStream 永久阻塞
                            │
                            ▼
       ClaudeSDKClient.receive_messages() 不产出消息
                            │
                            ▼
            [掩盖因素 M1-M3] 放大挂起窗口
   ┌──────────────┼──────────────────┐
   │              │                  │
  prompt 级     node 级           pipeline 级
  timeout 被    无 wait_for        无总预算
  污染为 7200s   (executor:155)    (orchestrator:477)
  (dual_agent:343)
                            │
                            ▼
                Pipeline 永久挂起 100+ 分钟
```

---

## 四、修复策略（按优先级）

### P0 — 针对真正根因 R1（transport 层）

#### F1：在 `receive_messages` 循环中添加 idle watchdog
**位置**: `autoBMAD/docuswarm/llm/session_manager.py:1030-1045`

```python
async def prompt(self, message, timeout=None):
    effective_timeout = timeout if timeout is not None else self.DEFAULT_PROMPT_TIMEOUT
    IDLE_TIMEOUT = 120  # 单条消息间最大静默

    await self._client.query(message)
    last_msg_time = asyncio.get_event_loop().time()
    messages_received = 0

    async def _idle_watchdog():
        while True:
            await asyncio.sleep(IDLE_TIMEOUT / 2)
            idle = asyncio.get_event_loop().time() - last_msg_time
            if idle > IDLE_TIMEOUT:
                self._logger.error("prompt_idle_exceeded", idle_seconds=idle)
                raise LLMError(f"No message for {idle}s — transport likely stalled")

    try:
        async with asyncio.timeout(effective_timeout):
            watchdog = asyncio.create_task(_idle_watchdog())
            try:
                async for msg in self._client.receive_messages():
                    last_msg_time = asyncio.get_event_loop().time()
                    messages_received += 1
                    yield msg
            finally:
                watchdog.cancel()
```

#### F2：显式释放 subprocess 子进程
**位置**: `session_manager.py:1048-1050` 的 `close()`

增加 `process.kill()` 兜底（检测 `returncode is None` 时强制终止），防止 cancel 后子进程残留。

#### F3：捕获并记录 CLI 子进程 stderr
通过 `claude_agent_sdk.ClaudeAgentOptions(stderr=<callback>)` 或打开 transport 层日志，把 CLI 子进程的错误/警告流入项目日志。

### P1 — 针对掩盖因素 M1-M3（已识别）

| ID | 位置 | 动作 |
|---|---|---|
| M1 | `nodes/dual_agent.py:343` | 使用独立 `prompt_timeout=900s`，不要传 `agent_timeout` |
| M2 | `node_execution/executor.py:155` | `asyncio.wait_for(node.execute_with_context(ctx), timeout=1800)` |
| M3 | `pipeline/orchestrator.py:477` | `asyncio.wait_for(graph.ainvoke(...), timeout=config.agent_timeout)` |

### P2 — 可观测性增强

1. **完善 `llm_message_received` 结构化字段**：将 `msg_type`、`has_tool_use`、`tool_name`、`message_length` 写入文本日志格式字符串（当前 structlog 渲染丢失了这些 kwargs）。
2. **DB 心跳**：节点执行过程中每 30s 更新 `pipelines.updated_at`，让 DB 侧可识别"活跃但卡住"。
3. **子进程健康检测**：父进程定期 `process.poll()` / 检测 PID 存活，与 asyncio 协同取消。
4. **Transport 指标**：统计 stdout 每分钟字节数，静默告警。

### P3 — HTTP 层鲁棒性（上游）

- 与 Kimi 网关协商启用 HTTP/2 PING / SSE keepalive，避免中间代理误判 idle；
- 在 `llm/config.py` 暴露 `read_timeout` / `idle_timeout`，透传到 SDK CLI（若 CLI 支持）。

---

## 五、诊断工具产出

本报告基于自主开发的 [`tools/pipeline_hang_diagnostic_tool.py`](../../tools/pipeline_hang_diagnostic_tool.py)（846 行）综合诊断。工具包含：

- `DatabaseAnalyzer` — 扫描 `pipelines` / `node_results` / `node_runs` / `checkpoints`
- `LogAnalyzer` — 解析 structlog 文本日志，计算消息频率与时间 gap
- `TimeoutChainAuditor` — 静态审计 8 处 timeout 配置点
- `HangPatternDetector` — 检测 5 种挂起模式
- `CodeStaticAuditor` — 审计 asyncio.timeout 使用情况

配套结构化数据: [JSON 报告](./2026-04-27-pipeline-hang-root-cause-report-pipeline-1777291307570-8957f601.json)

### 挂起模式检测结果（4/5 匹配）

| 模式 | 置信度 | 证据 |
|---|---|---|
| `silent_after_llm_message_received` | 95% | 静默 6055s |
| `zero_completed_nodes` | 90% | 无任何节点完成 |
| `no_terminal_log_event` | 88% | 无 error/timeout/complete 日志 |
| `receive_messages_infinite_block` | 92% | SDK transport 黑盒阻塞 |
| `db_state_frozen` | 0% | DB `updated_at` ≠ `created_at`（存在外部更新） |

---

## 六、结论

### 6.1 根因陈述（修订版）

**此次挂起的根因不是超时配置错误，而是 `claude-agent-sdk` 的 subprocess+stdio transport 架构 + 上游 HTTP 流式连接半开 的组合脆弱性**。

超时配置错误（agent_timeout=7200s 污染 prompt timeout）**只是让挂起从"15 分钟后自救"变为"永久挂起"的掩盖因素**。

### 6.2 修复优先级

1. **P0 - F1 idle watchdog**：这是**真正解决挂起不被发现**的唯一有效手段；
2. **P0 - F2 subprocess 硬杀**：防止 cancel 后资源泄漏；
3. **P1 - 三处 timeout 修正**：将故障窗口从∞ 收敛到 15 分钟；
4. **P2 - 可观测性**：下一次挂起能在 2 分钟内被诊断工具自动定位。

### 6.3 对 v1 报告的修正点

| 维度 | v1 定性 | 本版定性 |
|---|---|---|
| 根本原因 | timeout 配置错误 | transport 层子进程/HTTP 阻塞 |
| dual_agent.py:343 | ROOT CAUSE | 掩盖因素（放大窗口） |
| executor.py 无超时 | CRITICAL 根因 | 缺失的自救机制 |
| receive_messages 阻塞 | 次要现象 | **直接触发点** |
| 修复路径 | 加超时即可 | 必须增加 idle watchdog + 子进程治理 |

### 6.4 立即行动建议

1. 手动 kill 残留的 `claude` CLI 子进程（Windows: `tasklist | findstr claude` → `taskkill /F /PID ...`）；
2. 实施 P0-F1（idle watchdog），这是单个最高 ROI 的修复；
3. 实施 P1 三处 timeout 修正；
4. 下次执行前，先确认 Kimi 网关侧无代理/proxy 配置异常，或启用 TCP keepalive。

---

**报告作者**: DocuSwarm 深度诊断工具（pipeline_hang_diagnostic_tool.py v1.1）
**源码审计范围**: `autoBMAD/docuswarm/{llm,nodes,agents,node_execution,pipeline,tools}/` + `venv/Lib/site-packages/claude_agent_sdk/_internal/transport/subprocess_cli.py`
