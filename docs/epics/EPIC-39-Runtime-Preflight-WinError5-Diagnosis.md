# EPIC-39: Runtime Preflight与WinError 5 Transport诊断

**Epic ID**: EPIC-39  
**Epic 名称**: Runtime Preflight与WinError 5 Transport诊断  
**优先级**: P0（CRITICAL）  
**状态**: ❌ READY FOR IMPLEMENTATION（未实现 / 0% complete as of 2026-04-28）  
**创建日期**: 2026-04-28  
**研究来源**: `docs/research/2026-04-28-winerror5-architecture-refactor/01-transport-preflight-winerror5-diagnosis.md`  
**预估工作量**: ~6 hours (~1 day)

---

## Epic 概述

当前 `python -m autoBMAD.docuswarm start` 在 Windows 下触发 `[WinError 5] 拒绝访问` 时，五个业务节点（analyst、pm、ux、architect、po）逐一失败，缺乏统一 fail-fast 机制。每个节点独立调用 `SessionManager.create_session()` 时重复触发同一错误，产生 5 次重复失败 + 5 次重复日志 + 状态语义污染。

**核心问题**：
- 架构缺少 `runtime preflight`，导致底层 transport 错误被放大为全图故障
- `anyio.open_process()` 在 Windows 特定环境下被操作系统拒绝
- 错误发生时 `completed_nodes` 与 `failed_nodes` 同时包含全部节点，`status='completed'` 与 `error` 并存

**推荐方案**：在流水线启动前引入 `runtime_preflight` 模块，执行分层能力探针，将"五个节点重复失败"压缩为"一次预检失败"。

---

## 背景与技术分析

### 问题现象与日志证据

`logs/docuswarm-2026-04-28.log` 关键时间线：

```text
09:52:53.269  single_prompt_start    (ContextValidator 验证阶段)
09:52:53.300  single_prompt_sdk_error: Failed to start Claude Code: [WinError 5] 拒绝访问。
09:52:53.331  analyst  node_execution_started
09:52:53.370  analyst  creating_session ... mode=agent
              → 重复出现 session_creation_failed (WinError 5)
              → pm, ux, architect, po 同理
```

最终 `pipeline_started` 日志中 `result` 同时断言"全部完成"和"全部失败"，状态语义遭到污染。

### 分层复现实验结论

| 层级 | 方法 | 结果 | 结论 |
|------|------|------|------|
| Layer 1 | `claude --version` | ✅ 成功 | CLI 本身存在且可执行 |
| Layer 2 | `subprocess.Popen` | ✅ 成功 | 标准库同步子进程无权限问题 |
| Layer 3 | `anyio.open_process` | ❌ WinError 5 | **任何使用 anyio 的代码路径在 Windows 当前环境都会被拒绝** |
| Layer 4 | `ClaudeSDKClient.connect()` | ❌ CLIConnectionError | SDK 是 Layer 3 的调用方 |

### 根因链

```text
Claude Agent SDK → SubprocessCLITransport.connect()
→ anyio.open_process(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=..., env=..., user=...)
→ Windows CreateProcessW (via asyncio subprocess on Windows)
→ PermissionError [WinError 5] 拒绝访问
```

---

## Stories

### Story 39.1: 实现 TransportPreflight 四层探针

**目标**：新建 `runtime_preflight.py` 模块，实现 Direct CLI → subprocess.Popen → anyio.open_process → SDK connect 的分层探针。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/llm/runtime_preflight.py`）

#### 验收标准

- [ ] 定义 `PreflightResult` TypedDict，包含 `success`, `category`, `platform`, `cli_path`, `direct_cli_ok`, `subprocess_popen_ok`, `anyio_open_process_ok`, `sdk_connect_ok`, `error`, `recommendations` 字段
- [ ] 定义 `TransportPreflight` Protocol，包含 `async def check(self, cwd: Path | None = None) -> PreflightResult`
- [ ] 实现 `TransportPreflightImpl` 类，四层探针顺序执行
- [ ] 早期退出：任何一层失败即返回，不继续执行后续探针
- [ ] 结构化诊断：明确区分 `direct_cli_ok=true, subprocess_popen_ok=true, anyio_open_process_ok=false` 的情况
- [ ] 平台感知：Windows 下额外检测 `sys.platform == "win32"` 并附加针对性建议
- [ ] 短超时：每层探针设置 10-15 秒超时，避免 preflight 本身挂起
- [ ] 错误分类：`category` 支持 `"ok"`, `"transport_permission_denied"`, `"cli_not_found"`, `"sdk_connect_failed"`

#### 技术规格

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

#### 测试要求

- 单元测试：`tests/test_llm/test_runtime_preflight.py`
  - 测试四层探针全部通过时返回 `success=True, category="ok"`
  - 测试 `direct_cli_ok=true, subprocess_popen_ok=true, anyio_open_process_ok=false` 时返回 `category="transport_permission_denied"`
  - 测试 Windows 平台下返回额外针对性建议
  - 测试超时机制（使用 `asyncio.wait_for` 模拟）

---

### Story 39.2: 集成 Preflight 到 Orchestrator.start_pipeline()

**目标**：在 `HybridOrchestrator.start_pipeline()` 入口调用 preflight，失败时不进入 LangGraph。

**涉及文件**：1 个（`autoBMAD/docuswarm/pipeline/orchestrator.py`）

#### 验收标准

- [ ] `HybridOrchestrator.__init__()` 接受可选的 `preflight: TransportPreflight | None = None` 参数
- [ ] `start_pipeline()` 在创建 graph 之前执行 `await self._preflight.check(cwd=...)`
- [ ] preflight 失败时：
  - 不调用 `create_pipeline_graph()`
  - 不调用 `graph.ainvoke()`
  - 记录结构化错误日志（包含 `direct_cli_ok`, `subprocess_popen_ok`, `anyio_open_process_ok`）
  - 向 DB 写入 `status=FAILED` 的 pipeline 记录
  - 抛出 `OrchestratorError` 包含诊断信息
- [ ] preflight 成功时正常进入 graph 执行流程
- [ ] 向后兼容：`preflight=None` 时跳过预检（保留现有行为）

#### 技术规格

```python
# orchestrator.py start_pipeline() 入口
async def start_pipeline(self, subject_context, pipeline_id=None):
    # Step 0: Runtime preflight
    if self._preflight:
        preflight_result = await self._preflight.check(cwd=Path(self._work_dir))
        if not preflight_result["success"]:
            logger.error("preflight_failed", **preflight_result)
            await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                {"status": FAILED, "error": preflight_result},
            )
            raise OrchestratorError(
                f"Runtime preflight failed: {preflight_result['error']}"
            )
    # ... 继续原有流程
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_preflight_integration.py`
  - 测试 preflight 失败时 graph 从未被创建或调用
  - 测试 preflight 失败时 DB 中 pipeline status 为 `failed`
  - 测试 preflight 失败时 `completed_nodes` 为空列表
  - 测试 preflight 成功时正常进入 graph 执行

---

### Story 39.3: Windows 特定缓解措施与诊断建议

**目标**：为 Windows 环境下 `anyio.open_process` 不可用但 `subprocess.Popen` 可用的情况提供诊断建议和缓解方案文档。

**涉及文件**：2 个（`autoBMAD/docuswarm/llm/runtime_preflight.py` + 新建 `docs/troubleshooting/winerror5.md`）

#### 验收标准

- [ ] preflight 检测到 `anyio_open_process_ok=false` 且 `subprocess_popen_ok=true` 时，返回 Windows 特定的诊断建议
- [ ] 建议包含：检查 Windows Defender / EDR 拦截、检查 `claude.exe` Zone.Identifier、尝试管理员权限运行
- [ ] 创建故障排除文档 `docs/troubleshooting/winerror5.md`，包含根因说明、四层探针解释、缓解措施
- [ ] 建议中包含向 `claude_agent_sdk` 维护者反馈的模板

#### 技术规格

Windows 特定建议列表：

```python
WINDOWS_ANYIO_FAILURE_RECOMMENDATIONS = [
    "Windows Defender 或 EDR 可能拦截了 Python 异步子进程创建，尝试将 Python 和 claude.exe 加入白名单",
    "检查 claude.exe 是否被标记为'从网络下载'（Zone.Identifier），右键属性解除锁定",
    "尝试以管理员权限运行命令提示符（临时诊断用）",
    "向 claude_agent_sdk 维护者报告 Windows anyio.open_process 兼容性问题",
]
```

---

## 依赖关系

```
Story 39.1 → Story 39.2  (先实现探针，再集成到 Orchestrator)
Story 39.3 → Story 39.1  (诊断建议依赖探针实现)
```

---

## 实施阶段划分

### 阶段 1（P0 修复，优先级最高）

- **Story 39.1**：实现 TransportPreflight 四层探针
- **Story 39.2**：集成到 Orchestrator.start_pipeline()

**预期收益**：WinError 5 发生时从 5 次节点重复失败压缩为 1 次清晰预检失败，无状态污染。

### 阶段 2（文档与诊断）

- **Story 39.3**：Windows 特定缓解措施与故障排除文档

**预期收益**：用户收到可操作的诊断建议，知道如何自行排查或向 SDK 维护者反馈。

---

## 验证标准

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

## 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| preflight 本身在 Windows 上挂起 | LOW | 每层 10-15 秒超时 |
| preflight 通过但节点执行时仍失败 | LOW | preflight 包含 SDK connect 探针，与真实 session 创建路径一致 |
| 向后兼容性破坏 | LOW | `preflight=None` 时跳过预检 |

---

## 排除范围（已裁剪）

| 排除项 | 排除原因 |
|--------|---------|
| subprocess.Popen Fallback Provider | 属于 EPIC-41 (Provider 边界重构) 的可选方案，非本 Epic 核心目标 |
| 移除 LangGraph | 超出当前证据要求范围 |
| 迁移到 TypeScript | 超出当前证据要求范围 |

---

## 相关文件

| 文件 | 角色 |
|------|------|
| `autoBMAD/docuswarm/llm/runtime_preflight.py` | Story 39.1 新建文件 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Story 39.2 集成点 |
| `logs/docuswarm-2026-04-28.log` | 问题日志证据 |
| `venv/Lib/site-packages/claude_agent_sdk/_internal/transport/subprocess_cli.py` | SDK transport 实现参考 |
