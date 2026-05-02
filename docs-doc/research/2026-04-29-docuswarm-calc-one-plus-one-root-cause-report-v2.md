# DocuSwarm calc-one-plus-one 根因研究报告 v2

## 执行摘要

执行命令 `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 时，DocuSwarm 经历了从导入崩溃到节点执行挂起再到 API 认证失败的演进问题。本报告基于实际执行和深度代码分析，识别出 5 个阻断性根因。

## 问题现象

### 1. 初始导入阶段（历史问题，已部分修复）
- `kaos` 未声明依赖导致导入链崩溃（RC-A）
- `ANTHROPIC_API_KEY` 缺失导致配置验证失败（RC-B）

### 2. 节点执行阶段（当前核心问题）
- 进程在 analyst 节点执行时挂起，日志停止在 LLM 消息交换后
- 直接测试 CLI 发现 `Not logged in · Please run /login` 错误
- 添加 `--bare` 标志后变为 `403 Request not allowed`
- curl 测试 API endpoint 返回 200，但 `claude-code` CLI 无法通过 Kimi 代理认证

## 根因深度分析

### RC-1: `claude-code` CLI 认证模式不匹配（P0 CRITICAL）

**问题描述**

DocuSwarm 使用 `claude_agent_sdk` 调用 `claude-code` CLI 子进程。在非 `--bare` 模式下，CLI 需要 OAuth 登录（`/login`）。在 `--bare` 模式下，CLI 使用 `ANTHROPIC_API_KEY` 直接调用 Anthropic API。

**根因机制**

| 模式 | 认证方式 | 当前状态 |
|------|---------|---------|
| 默认 | OAuth / Keychain | 失败：未登录 |
| `--bare` | `ANTHROPIC_API_KEY` | 失败：403 Forbidden |

`claude-code` CLI 的 `--bare` 模式发送的请求格式与 Kimi 代理服务 (`https://api.kimi.com/coding/`) 不兼容，导致 403 错误。直接 curl 调用同一 endpoint 返回 200，说明 `claude-code` 的 User-Agent 或请求签名被 Kimi 代理拒绝。

**影响范围**
- 所有使用 `SessionManager.create_session()` 的 LLM 调用均失败
- 5 个节点（analyst, pm, ux, architect, po）全部无法执行
- 无法生成任何交付物

### RC-2: `SessionManager._create_options()` 缺少 `--bare` 标志（P1 HIGH）

**问题描述**

`SessionManager._create_options()` 构建 `ClaudeAgentOptions` 时未传递 `--bare` 标志，导致 CLI 默认使用 OAuth 模式。

**关键代码**

```python
# autoBMAD/docuswarm/llm/session_manager.py L326
options_dict: dict[str, Any] = {
    "cwd": self._cwd,
    "permission_mode": permission_mode,
    # 缺失："extra_args": {"bare": None}
}
```

### RC-3: `orchestrator.py` 工作目录计算错误（P1 HIGH）

**问题描述**

`HybridOrchestrator.__init__` 中 `_work_dir` 的计算基于 `autoBMAD` 包目录而非项目根目录，导致：
- 输出目录：`/home/leafliu/autoBMAD/autoBMAD/output`（错误）
- SummaryAgent 查找文件：`/home/leafliu/autoBMAD/autoBMAD/docs`（错误）

**关键代码**

```python
# orchestrator.py L124
autoBMAD_root = Path(__file__).parent.parent.parent.resolve()
# 从 autoBMAD/docuswarm/pipeline/orchestrator.py 出发：
# → autoBMAD/docuswarm/pipeline → autoBMAD/docuswarm → autoBMAD
# 实际项目根目录是 /home/leafliu/autoBMAD（上级目录）
```

### RC-4: 节点配置路径解析不一致（P1 HIGH，历史回归）

**问题描述**

`executor.py` 在调用 `create_dual_agent_node` 时，错误地将 `project_root` 设为仓库根目录，而节点配置文件（`persona.json`, `evaluator.yaml`）实际存放在 `autoBMAD/nodes/` 目录下。

**关键代码**

```python
# executor.py L125-126
auto_bmad_root = Path(__file__).parent.parent.parent.resolve()
repo_root = auto_bmad_root.parent if auto_bmad_root.name == "autoBMAD" else auto_bmad_root

# executor.py L147-151
node = create_dual_agent_node(
    ...,
    project_root=repo_root,  # ← 错误：应为 auto_bmad_root
)
```

### RC-5: 缺少无 LLM 的端到端测试路径（P2 MEDIUM）

**问题描述**

DocuSwarm 没有提供在无外部 LLM 服务的情况下验证流水线端到端运行的机制。这在 CI/CD 环境或 API 不可用时构成严重障碍。

## 根因定位

**根本原因**: `claude-code` CLI 与 Kimi 代理服务的认证/请求格式不兼容，导致所有 LLM 调用阻断。

**触发条件**: 
1. 环境未配置 `claude-code` OAuth 登录
2. `ANTHROPIC_API_KEY` 指向 Kimi 代理服务而非 Anthropic 官方 API
3. `SessionManager` 未传递 `--bare` 标志

## 修复建议

依据奥卡姆剃刀原则，最简单的修复组合是：

1. **Fix-1**: 在 `SessionManager._create_options()` 中添加 `extra_args={"bare": None}`
2. **Fix-2**: 修正 `orchestrator.py` 的 `_work_dir` 计算，使用项目根目录
3. **Fix-3**: 修正 `executor.py` 的 `project_root` 传入值为 `auto_bmad_root`
4. **Fix-4**: 添加 `DOCUSWARM_MOCK_LLM=1` 环境变量支持，在无 LLM 时生成 mock 交付物
5. **Fix-5**: 创建端到端测试验证 mock 模式

---
*本报告基于实际命令执行、日志分析和代码审查生成。*
