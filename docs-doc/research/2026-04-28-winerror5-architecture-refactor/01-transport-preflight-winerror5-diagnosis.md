# 研究报告 01：Transport Preflight 与 WinError 5 深度诊断

**日期**: 2026-04-28  
**研究对象**: `autoBMAD/docuswarm` LLM Transport 层  
**关联问题**: `python -m autoBMAD.docuswarm start` 在 Windows 下触发 `[WinError 5] 拒绝访问`  
**研究工具**: `tools/winerror5_architecture_research_tool.py --mode transport`

---

## 执行摘要

本报告通过系统化的预检诊断，确认 `WinError 5` 的根本原因是 **Windows 环境下 Python `anyio.open_process()` 在创建带 PIPE 的异步子进程时被操作系统拒绝**，而非 Claude Code CLI 未安装、任务内容错误或 LangGraph 图执行缺陷。

直接后果是：五个业务节点（analyst、pm、ux、architect、po）在各自创建 `ClaudeSDKClient` session 时逐一触发同一错误，缺乏统一 fail-fast 机制。

**核心建议**：在流水线启动前引入 `runtime_preflight` 模块，执行分层能力探针，将"五个节点重复失败"压缩为"一次预检失败"。

---

## 1. 问题现象与日志证据

### 1.1 真实日志路径

`logs/docuswarm-2026-04-28.log`

### 1.2 关键时间线

```text
09:52:53.269  single_prompt_start    (ContextValidator 验证阶段)
09:52:53.300  single_prompt_sdk_error: Failed to start Claude Code: [WinError 5] 拒绝访问。
09:52:53.331  analyst  node_execution_started
09:52:53.370  analyst  creating_session ... mode=agent
              → 重复出现 session_creation_failed (WinError 5)
              → pm, ux, architect, po 同理
```

### 1.3 矛盾结果

最终 `pipeline_started` 日志中的 `result` 包含：

- `completed_nodes=['analyst','pm','ux','architect','po']`
- `failed_nodes=['analyst','pm','ux','architect','po']`
- `status='completed'`
- `error={'node_id':'analyst','status':'failed',...}`

这组数据同时断言"全部完成"和"全部失败"，说明失败被识别后，状态语义遭到污染。

---

## 2. 分层复现实验

在同一 Windows 工作区和同一 `venv` 中执行以下四层探针：

### 2.1 Layer 1: Direct CLI

```powershell
> claude --version
2.1.92 (Claude Code)
```

**结果**: ✅ 成功  
**结论**: CLI 本身存在且可执行，PATH 正确。

### 2.2 Layer 2: subprocess.Popen

```python
import subprocess
proc = subprocess.Popen(
    ['claude', '--version'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
stdout, stderr = proc.communicate()
# returncode 0, stdout "2.1.92 (Claude Code)"
```

**结果**: ✅ 成功  
**结论**: 标准库同步子进程创建无权限问题。

### 2.3 Layer 3: anyio.open_process

```python
import anyio, asyncio

async def probe():
    proc = await anyio.open_process(
        ['claude', '--version'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    ...

asyncio.run(probe())
# PermissionError: [WinError 5] 拒绝访问。
```

**结果**: ❌ 失败，抛出 `PermissionError [WinError 5]`  
**结论**: **任何使用 `anyio.open_process(..., stdin=PIPE, stdout=PIPE, stderr=PIPE)` 的代码路径在 Windows 当前环境中都会被拒绝。**

### 2.4 Layer 4: ClaudeSDKClient.connect()

```python
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import ClaudeAgentOptions

options = ClaudeAgentOptions(cwd=Path.cwd())
client = ClaudeSDKClient(options=options)
await client.connect()  # → CLIConnectionError: Failed to start Claude Code: [WinError 5] 拒绝访问。
```

**结果**: ❌ 失败  
**结论**: SDK 是 Layer 3 的调用方，错误被包装为 `CLIConnectionError`。

---

## 3. 根因分析

### 3.1 直接根因链

```text
Claude Agent SDK → SubprocessCLITransport.connect()
→ anyio.open_process(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=..., env=..., user=...)
→ Windows CreateProcessW (via asyncio subprocess on Windows)
→ PermissionError [WinError 5] 拒绝访问
```

### 3.2 为什么 subprocess.Popen 成功而 anyio 失败？

在 Windows 上，`asyncio` 默认使用 `ProactorEventLoop`（Python 3.8+），其 `subprocess_exec` 实现与 `subprocess.Popen` 的底层调用存在差异：

1. **Handle 继承策略**: `anyio.open_process` / `asyncio.create_subprocess_exec` 对 stdio handle 的继承标志设置与同步 `subprocess.Popen` 不同。某些 Windows 安全策略（如 EDR、防病毒软件、组策略）会拦截带有特定 handle 继承模式的异步进程创建。
2. **`user` 参数**: Claude Agent SDK 的 `anyio.open_process` 调用传入了 `user=self._options.user`。在 Windows 上，`asyncio` 对 `user` 参数的处理路径可能触发额外的权限检查。
3. **`cwd` 与路径解析**: `anyio.open_process` 的 `cwd` 参数在 Windows 上的路径解析可能与 `subprocess.Popen` 存在微妙差异，尤其是当 `cmd` 是相对路径或 PATH 中的命令时。

### 3.3 为什么不是其他原因？

| 假设 | 验证 | 结论 |
|------|------|------|
| `claude.exe` 不存在 | `claude --version` 成功 | ❌ 排除 |
| PATH 配置错误 | `where claude` 找到可执行文件 | ❌ 排除 |
| 任务内容导致失败 | WinError 5 在 session 创建阶段即触发，与 prompt 内容无关 | ❌ 排除 |
| 单个节点代码错误 | 五个节点都失败，且错误相同 | ❌ 排除 |
| LangGraph 本身问题 | 错误发生在图节点执行前（SDK connect） | ❌ 排除 |
| Kimi YAML 兼容问题 | 日志已确认 agent_file 被跳过，当前使用 MCP server | ❌ 排除 |

---

## 4. 架构缺陷放大效应

当前架构缺少 `runtime preflight`，导致一个底层 transport 错误被放大为全图故障：

```text
[缺少 Preflight]
    ↓
Orchestrator.start_pipeline() 直接创建 graph
    ↓
LangGraph 顺序执行 analyst → pm → ux → architect → po
    ↓
每个节点独立调用 SessionManager.create_session()
    ↓
每个节点独立触发 anyio.open_process() WinError 5
    ↓
5 次重复失败 + 5 次重复日志 + 状态语义污染
```

如果存在 preflight：

```text
[存在 Preflight]
    ↓
start_pipeline() 首先执行 runtime_preflight.check()
    ↓
Layer 3 探针 anyio.open_process() 失败
    ↓
立即返回结构化诊断，不进入 LangGraph
    ↓
0 次节点执行、1 次清晰错误、无状态污染
```

---

## 5. 推荐实现：runtime_preflight.py

### 5.1 文件位置

```text
autoBMAD/docuswarm/llm/runtime_preflight.py
```

### 5.2 核心接口

```python
from typing import Protocol, TypedDict
from pathlib import Path

class PreflightResult(TypedDict):
    success: bool
    category: str  # "ok" | "transport_permission_denied" | "cli_not_found" | "sdk_connect_failed"
    platform: str
    cli_path: str | None
    direct_cli_ok: bool
    subprocess_popen_ok: bool
    anyio_open_process_ok: bool
    sdk_connect_ok: bool
    error: str
    recommendations: list[str]

class TransportPreflight(Protocol):
    async def check(self, cwd: Path | None = None) -> PreflightResult: ...
```

### 5.3 实现要点

1. **四层探针顺序执行**：Direct CLI → subprocess.Popen → anyio.open_process → SDK connect。
2. **早期退出**：任何一层失败即返回，不继续执行后续探针（避免重复错误）。
3. **结构化诊断**：明确区分 `direct_cli_ok=true, subprocess_popen_ok=true, anyio_open_process_ok=false` 的情况。
4. **平台感知**：Windows 下额外检测 `sys.platform == "win32"` 并附加针对性建议。
5. **短超时**：每层探针设置 10-15 秒超时，避免 preflight 本身挂起。

### 5.4 集成点

在 `HybridOrchestrator.start_pipeline()` 中：

```python
# Step 0: Runtime preflight
preflight = TransportPreflightImpl()
preflight_result = await preflight.check(cwd=Path(self._work_dir))
if not preflight_result["success"]:
    logger.error("preflight_failed", **preflight_result)
    # Create failed pipeline state without entering graph
    await self._state_manager.update_pipeline_state(
        final_pipeline_id,
        {"status": FAILED, "error": preflight_result},
    )
    raise OrchestratorError(f"Runtime preflight failed: {preflight_result['error']}")
```

---

## 6. Windows 特定缓解措施

如果 preflight 确认 `anyio.open_process` 不可用但 `subprocess.Popen` 可用，可考虑：

### 6.1 方案 A：subprocess.Popen Fallback（Provider 层）

在 `ClaudeAgentSDKProvider` 中，当 `anyio.open_process` 失败时，尝试使用 `subprocess.Popen` 包装一个异步接口。这是**窄修复**，仅影响 transport 启动方式。

### 6.2 方案 B：上游 SDK 反馈

向 `claude_agent_sdk` 维护者报告 Windows `anyio.open_process` 兼容性问题，建议支持可选的 `use_sync_subprocess` 参数。

### 6.3 方案 C：环境修复

- 检查 Windows Defender / EDR 是否拦截了 Python 的异步子进程创建。
- 尝试以管理员权限运行（不推荐作为长期方案）。
- 检查 `claude.exe` 是否被标记为"从网络下载"（Zone.Identifier），解除锁定。

---

## 7. 验证标准

实施 preflight 后，必须满足以下验证条件：

| 验证项 | 期望结果 |
|--------|----------|
| Windows anyio spawn 失败时 | 仅产生一次 preflight error |
| `completed_nodes` | 为空列表 `[]` |
| `failed_nodes` | 不包含五个业务节点（除非真的执行过） |
| pipeline DB status | `failed` |
| 错误消息 | 包含 `[WinError 5] 拒绝访问` 和诊断建议 |
| 日志字段 | 包含 `direct_cli_ok`, `subprocess_popen_ok`, `anyio_open_process_ok` |

---

## 8. 结论

`WinError 5` 不是 DocuSwarm 业务逻辑错误，而是 **Windows/Python/AnyIO transport 启动能力问题**。当前架构因缺少统一预检和 provider 边界，将一次底层失败放大为五节点全图失败和状态污染。

最小充分的修复是：

1. **新增 `runtime_preflight.py`**：四层探针，fail-fast。
2. **在 `start_pipeline()` 入口调用 preflight**：失败时不进入 LangGraph。
3. **保留 Claude Agent SDK**：问题在 transport 层，不在 SDK 抽象模型。
4. **不迁移 TypeScript / 不移除 LangGraph**：这些改动超出当前证据要求的范围。

---

## 参考资料

- `logs/docuswarm-2026-04-28.log`
- `venv/Lib/site-packages/claude_agent_sdk/_internal/transport/subprocess_cli.py`
- `autoBMAD/docuswarm/llm/session_manager.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- Python `asyncio` Windows subprocess 实现：`Lib/asyncio/windows_events.py`
