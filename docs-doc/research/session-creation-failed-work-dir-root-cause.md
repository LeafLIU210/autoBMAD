# DocuSwarm `session_creation_failed` 根因分析报告

**日期**: 2026-04-06  
**分析人**: Qoder（深度调试）  
**严重等级**: P0 — 全量节点崩溃，Pipeline 完全无法执行  
**状态**: ✅ 已修复

---

## 一、现象描述

执行以下命令后：

```bash
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

所有节点（analyst / pm / ux / architect / po）均在 `creating_session` 之后立即失败，日志呈如下模式：

```
[debug]  allowed_tools_configured
[error]  session_creation_failed    error='SessionManager' object has no attribute '_work_dir'
[warning] llm_call_error            error=Failed to create session: 'SessionManager' object has no attribute '_work_dir'
[error]  independent_agent_failed   ...
[error]  node_execution_failed      ...
```

失败时间极短（约 350ms），说明在 Claude SDK 发出任何网络请求之前就已崩溃，属于**纯代码级属性错误**，与网络/API Key/超时无关。

---

## 二、错误链追踪

```
IndependentAgent.execute()
  └─ IndependentAgent._llm_call()
       └─ SessionManager.create_session()
            └─ ClaudeSessionWrapper(work_dir=self._work_dir)  ← AttributeError 在此抛出
                 └─ except Exception → LLMError("Failed to create session: ...")
                      └─ 上层捕获 → session_creation_failed / llm_call_error / independent_agent_failed
```

---

## 三、根因定位

### 根因：`SessionManager.__init__` 中删除了 `_work_dir`，但引用点未同步更新

#### 3.1 历史背景

早期版本的 `SessionManager` 使用单一属性 `self._work_dir` 同时承担两个职责：
1. SDK 进程工作目录（`cwd`）—— 影响 Python import 路径
2. 文件输出目录（`output_dir`）—— 影响生成文件的保存位置

#### 3.2 职责分离重构（奥卡姆剃刀原则）

为解决职责混用导致的冲突，`__init__` 被重构为：

```python
# 新版 __init__（正确）
self._cwd = cwd or Path.cwd()          # SDK 工作目录（项目根目录）
self._output_dir = output_dir or self._cwd  # 文件输出目录
```

同时新增了 `work_dir` property（向后兼容）：

```python
@property
def work_dir(self) -> Path:
    return self._output_dir  # 向后兼容
```

#### 3.3 遗漏的引用点（BUG）

`__init__` 中 `self._work_dir` 被删除，但以下两处调用点**未同步更新**：

| 位置 | 行号 | 问题代码 |
|------|------|---------|
| `create_session()` | ~342 | `work_dir=self._work_dir` |
| `resume_session()` | ~384 | `work_dir=self._work_dir` |

两处均传给 `ClaudeSessionWrapper.__init__` 的 `work_dir` 参数。由于 `self._work_dir` 不存在（只有 `self._cwd` 和 `self._output_dir`），Python 在运行时抛出 `AttributeError`。

---

## 四、修复方案

### Fix：将两处 `self._work_dir` 替换为 `self._output_dir`

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

#### create_session() 修复

```python
# 修复前（BUG）
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._work_dir,   # ← AttributeError
    options=options,
)

# 修复后 ✅
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._output_dir,  # ← 使用 _output_dir
    options=options,
)
```

#### resume_session() 修复

```python
# 修复前（BUG）
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._work_dir,   # ← AttributeError
)

# 修复后 ✅
wrapper = ClaudeSessionWrapper(
    client=client,
    session_id=session_id,
    work_dir=self._output_dir,  # ← 使用 _output_dir
)
```

---

## 五、为何是 `_output_dir` 而非 `_cwd`

`ClaudeSessionWrapper._work_dir` 的用途是**文件操作上下文**（即 Agent 生成文件的输出目录），而非 SDK 进程的 `cwd`。

| 属性 | 用途 | 正确传递目标 |
|------|------|------------|
| `self._cwd` | SDK 进程 cwd，保证 Python import 路径正确 | `ClaudeAgentOptions.cwd` |
| `self._output_dir` | Agent 文件输出目录 | `ClaudeSessionWrapper.work_dir` |

因此 `ClaudeSessionWrapper` 应接收 `_output_dir`，SDK options 接收 `_cwd`（已在 `_create_options` 中正确处理）。

---

## 六、影响范围分析

### 受影响的代码路径

```
SessionManager.create_session()   → 所有新建 session 的场景（主路径）
SessionManager.resume_session()   → 所有 resume session 的场景
```

### 受影响的节点

所有调用 `IndependentAgent` 的节点均受影响，包括：
- analyst、pm、ux、architect、po（已在日志中确认全部崩溃）

### 不受影响的路径

- `SessionManager.single_prompt()` — 使用 `query()` 直接调用，不经过 `ClaudeSessionWrapper`，**不受此 bug 影响**

---

## 七、验证方法

修复后，重新执行命令，预期日志变化：

```
# 修复前（错误）
[error] session_creation_failed   error='SessionManager' object has no attribute '_work_dir'

# 修复后（正常）
[info]  session_created           session_id=session_xxxx  mode=agent
[debug] context_build             ...
```

快速验证命令：
```bash
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

---

## 八、根因分类

| 维度 | 分类 |
|------|------|
| 错误类型 | `AttributeError` — 属性不存在 |
| 触发时机 | Runtime（实例化 `ClaudeSessionWrapper` 时） |
| 根本原因 | 重构时遗漏同步更新引用点（不完整的重构） |
| 发现方式 | 错误日志 + 代码静态分析 |
| 修复复杂度 | 极低（2 处字符串替换） |
| 测试覆盖缺失 | `create_session` / `resume_session` 集成路径缺乏 attribute 存在性测试 |

---

## 九、预防建议

1. **单元测试**：为 `SessionManager.create_session()` 和 `resume_session()` 添加测试，验证 `ClaudeSessionWrapper` 可正常实例化（即使 mock SDK client）。
2. **类型检查**：运行 `basedpyright` 对 `session_manager.py` 做静态检查，应能检测到 `self._work_dir` 不存在。
3. **重构规范**：凡删除实例属性，必须全局搜索所有 `self.<attribute_name>` 引用，确保同步更新。

---

## 十、相关文件

| 文件 | 说明 |
|------|------|
| `autoBMAD/docuswarm/llm/session_manager.py` | 主修复文件，第 342 行和第 384 行 |
| `autoBMAD/docuswarm/agents/independent.py` | 调用 `SessionManager.create_session()` 的上层 |
| `logs/docuswarm-2026-04-06.log` | 本次错误的完整日志 |
