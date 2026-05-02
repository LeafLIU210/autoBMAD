# DocuSwarm 超时 & 工具不可见根因深度分析报告

**分析日期**: 2026-04-06  
**触发场景**: `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md`  
**调试工具**: `tools/timeout_incomplete_response_analyzer.py`  
**报告状态**: 失败点 A 已修复；失败点 B（SDK `cwd` 职责拆分）方案已确定，待实施

---

## 一、问题现象

### 1.1 错误链（来自日志 docuswarm-2026-04-06.log）

```
16:05:07  analyst  node_execution_started
16:05:07  analyst  session_created
16:05:07  analyst  (开始流式接收消息)
...13 条消息接收...
16:06:07  orchestrator  prompt_timeout          ← 精确 60s 触发
16:06:07  analyst  llm_call_error (60s timeout)
16:06:07  analyst  response_parse_failed: "No JSON found in response"
16:06:07  analyst  independent_agent_failed
16:06:07  analyst  node_execution_failed
16:06:07  pm       node_execution_started       ← 立即进入下一节点
...（pm 节点同样超时失败）
```

### 1.2 超时时的关键上下文

来自终端输出的完整错误信息：

```
content=ThinkingBlock(thinking="The tools appear to have some issues,
but I need to complete my task. The instructions say I should use
the 'create_deliverable' tool to save my document, but I don't see that
error=No JSON found in response
```

**三个关键信号**：
1. LLM 在说"工具有问题" → 工具对 LLM **不可见**
2. LLM 在 ThinkingBlock 阶段（仍在推理，未完成）
3. 响应是纯英文散文，非 JSON → parse 必然失败

---

## 二、根因分析

### RC-1 (P0 CRITICAL): create_deliverable 工具对 LLM 不可见

#### 证据
- LLM 明确输出：`"The tools appear to have some issues, but I don't see that [tool]"`
- 超时前 `messages_received=13`，但无任何 `tool_use` 日志记录
- LLM 知道应该调用工具但无法找到它

#### 根因分析

**调用链**：
```
independent.py:execute_with_input()
  → self._agent_file = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"  ✅ 已修复
  → SessionManager(work_dir=output_dir, agent_file=self._agent_file)
  → session_manager._create_options()
  → options.cwd = self._work_dir  ← output/pipeline_id（仍是问题所在）
  → options.tools = [str(effective_agent_file)]
  → ClaudeSDKClient(options=options)
  → client.connect()  ← SDK 在 cwd 环境下加载 agent_file 并 import 工具模块
```

**两个潜在失败点**：

**失败点 A**: `project_root` 路径解析问题
```python
# independent.py:L622-624 (已修复)
# project_root = D:\GITHUB\DocuSwarm (repo root, 由 executor.py 传入)
self._agent_file = (
    self.project_root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
)
```
- 修复前缺少 `autoBMAD/` 层级，路径为 `DocuSwarm/docuswarm/...` → **路径不存在**
- 修复后路径为 `DocuSwarm/autoBMAD/docuswarm/...` → **路径正确**

**失败点 B（待修复）**: `cwd = output/pipeline_id` 导致工具模块 import 失败
```yaml
# independent_agent.yaml
tools:
  - "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"
```
- 工具以 Python 模块路径方式注册，SDK 需要能 `import autoBMAD.docuswarm.tools.create_deliverable`
- `options.cwd` 当前设为 `output/pipeline_id`，该目录下 `autoBMAD` 包不存在
- SDK 在此 `cwd` 下 import 工具模块，静默失败 → LLM 看不到任何工具

**根因（奥卡姆剃刀分析）**：`work_dir` 当前同时承担两个职责：
1. SDK 进程工作目录（影响 Python import 路径）→ 应为**仓库根目录**
2. 文件输出目录（`create_deliverable` 写文件位置）→ 应为 **`output/pipeline_id`**

两个职责需要不同的路径，必须拆分。`CreateDeliverableTool` 已有 `output_dir` 参数支持显式传入，`cwd` 只需改为仓库根目录即可解决 import 问题，无需引入任何新实体。

#### 影响
LLM 无法调用 `create_deliverable` 工具 → 无法保存文档 → 无法生成 JSON 执行报告 → 60s 内无法完成任务 → 超时 → parse 失败

---

### RC-2 (P0 CRITICAL): DEFAULT_PROMPT_TIMEOUT=60s 对文档生成任务过短

#### 证据
- 日志时间戳：`16:05:07 → 16:06:07`，精确 60s 触发
- LLM 在 60s 内仍处于 `ThinkingBlock` 推理阶段（未完成）
- 节点 yaml 配置 `runtime.timeout: 300`，但此值**从未被代码读取使用**

#### 根因分析

**超时值来源**：
```python
# llm/session_manager.py:L730
class ClaudeSessionWrapper:
    DEFAULT_PROMPT_TIMEOUT: int = 60  # 调试期临时设置（待恢复到合理值）
```

**节点配置超时从未生效**：
```python
# nodes/loader.py:L389-392
runtime_config = NodeRuntimeConfig(
    timeout=runtime_data.get("timeout", 300),  # analyst 配置为 300s
    ...
)
```

```python
# 搜索结果: 代码库中无任何地方读取 node_config.runtime.timeout
# 并传入 session.prompt(timeout=...) 调用
```

- `NodeRuntimeConfig.timeout=300` 被正确加载，但**从未传入 `ClaudeSessionWrapper.prompt(timeout=...)` 调用**
- 实际使用的超时值始终是 `ClaudeSessionWrapper.DEFAULT_PROMPT_TIMEOUT`（60s）
- 这是**设计缺陷**：节点级别的超时配置与实际执行超时断开连接

> ⚠️ **当前 60s 是调试期临时设置**，适合文档生成的合理值至少 300s。

---

### RC-3 (P1 HIGH): _parse_response fallback 未处理纯文本格式

#### 证据
```python
# independent.py:L467-468
if content.strip().startswith(("#", "##", "###")) or "Summary" in content[:100]:
    # 触发 markdown_fallback
```

实际内容：`"The tools appear to have some issues..."` 
- 不以 `#` 开头 ✗
- 不含 `"Summary"` ✗
- **fallback 不触发** → 直接抛出 `response_parse_failed`

#### 根因
fallback 机制假设 LLM 返回 Markdown 格式，但未处理：
- 纯英文说明性文本
- ThinkingBlock 内容
- 任何以字母开头的非 JSON 响应

即使工具已成功调用（file_path 存在于消息历史中），此类响应也会导致 parse 失败。

---

### RC-4 (P1 HIGH): ThinkingBlock 被过滤 → 消息内容不完整

#### ThinkingBlock 过滤设计

ThinkingBlock 被过滤是**设计如此**——`_convert_content_block` 中显式 `return None`，不将 ThinkingBlock 的推理过程纳入消息内容。

#### messages 列表并非为空的真实原因

实际代码中，`ThinkingBlock` 在 duck typing fallback 阶段（L667-672）会被捕获：

```python
# session_manager.py:L667-672 (duck typing final fallback)
else:
    item_type = getattr(item, "type", "text")
    if item_type == "text":
        converted = {"type": "text", "text": getattr(item, "text", str(item))}
    else:
        converted = {"type": item_type, "content": str(item)}  # ThinkingBlock 走这里
```

`ThinkingBlock.type` 为 `"thinking"` → 最终生成 `{"type": "thinking", "content": str(item)}`，**仍会被追加进 messages**。

因此 messages 不会为空。`response_parse_failed: "No JSON found"` 的原因是：
- messages 中有内容，但全部是 ThinkingBlock 的 `str(item)` 字符串化内容（非 JSON）
- `extract_json()` 在这些内容中找不到 JSON → 抛出 `No JSON found`

#### 实际根因
工具不可见（RC-1）→ LLM 无法调用工具 → 响应全为 ThinkingBlock 推理文本 → 无 JSON → parse 失败

---

### RC-5 (P2 MEDIUM): analyst 失败后流水线继续运行

#### 现象
```
16:06:07  analyst  node_execution_failed
16:06:07  pm       node_execution_started  ← 立即启动
```

> **此行为是允许的**：流水线各节点独立执行，前序节点失败不强制中断后续节点，符合当前设计目标（允许部分产出）。

当 RC-1/RC-2 修复后（工具可见 + 超时合理），各节点应能正常完成，此问题自然消除。若需要强制中断，可在 `node.yaml` 中增加 `fail_fast` 选项作为可选扩展（低优先级）。

---

## 三、根因关系图

```
RC-1 (工具不可见: _agent_file 路径错误 + cwd 导致 import 失败)
  ↓ LLM 无法调用工具，陷入推理循环
RC-2 (超时过短 60s，调试临时值)
  ↓ 60s 内 ThinkingBlock 未结束
  ↓ asyncio.TimeoutError
  ↓ messages = ThinkingBlock str 化内容（非 JSON）
RC-3 (fallback 覆盖不足)
  ↓ 非 JSON 散文不触发 markdown_fallback
  ↓ extract_json() → No JSON found
RC-4 (ThinkingBlock 被设计过滤，duck typing fallback 将其 str 化追加)
  ↓ messages 内容为推理文本，无法 parse
  ↓
response_parse_failed → independent_agent_failed → node_execution_failed
  ↓
RC-5 (流水线继续运行，设计允许)
  ↓
后续节点同样因 RC-1/RC-2 失败
```

---

## 四、修复方案

### Fix-1 (P0): 接入节点超时配置（`node.yaml` → `session.prompt()`）

**当前状态**：`DEFAULT_PROMPT_TIMEOUT=60s` 为调试期临时值，适合文档生成的合理值至少 300s。

**方案 A（推荐）**：让 `executor.py` 将 `node_config.runtime.timeout` 传入 `session.prompt()`

```python
# node_execution/executor.py 或 nodes/dual_agent.py
node_config = NodeLoader.load(node_id)
node_timeout = node_config.runtime.timeout  # 读取节点配置的 timeout

# 调用时传入
async for msg in session.prompt(user_prompt, timeout=node_timeout):
    ...
```

**方案 B（临时兜底）**：将 `DEFAULT_PROMPT_TIMEOUT` 恢复到合理值

```python
# llm/session_manager.py
DEFAULT_PROMPT_TIMEOUT: int = 600  # 10 分钟，适合文档生成
```

> ⚠️ **当前值 60s 是调试期临时修改**，Fix-2B 实施后同步恢复。

---

### Fix-2 (P0): 修复工具加载 — 拆分 `cwd` 职责

**Fix-2A（已实施）**: 补全 `_agent_file` 路径中的 `autoBMAD/` 层级
```python
# independent.py (两处均已修复)
self._agent_file = (
    self.project_root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
)
# 实际路径: D:\GITHUB\DocuSwarm\autoBMAD\docuswarm\agents\configs\independent_agent.yaml ✅
```

**Fix-2B（待实施）**: 将 `cwd` 改为仓库根目录，让工具输出路径独立传入

`work_dir` 当前同时被用作 SDK `cwd` 和文件输出目录，两者需要不同路径，必须拆分：

```python
# independent.py: execute_with_input() 中，SessionManager 的 work_dir 改为仓库根目录
# repo_root = self.project_root  (已由 executor.py 正确传入)
pipeline_session_manager = self._create_pipeline_session_manager(
    work_dir=self.project_root,   # ← 改为仓库根目录，保证 import autoBMAD 可用
    ...
)
```

同时，`CreateDeliverableTool` 实例化时显式传入 `output_dir`（工具已原生支持此参数）：
```python
# tools/sdk_adapter.py 或工具注册入口
tool = CreateDeliverableTool(output_dir=output_dir)  # output_dir = output/pipeline_id
```

这样两个职责完全解耦，无需引入新实体，符合奥卡姆剃刀原则。

---

### Fix-3 (P1): 扩展 _parse_response fallback 覆盖范围

```python
# independent.py:_parse_response()
except ResponseParseError as e:
    # 原有条件保留，新增: 任何非 JSON 内容都尝试工具结果提取
    is_non_json_text = (
        content.strip().startswith(("#", "##", "###"))
        or "Summary" in content[:100]
        or not content.strip().startswith("{")  # 新增: 非 JSON 开头的任何内容
    )
    if is_non_json_text:
        file_path, sha256 = self._extract_create_deliverable_result(response)
        if file_path:
            # 构造 JSON（现有逻辑）
            ...
        else:
            # 更友好的错误信息
            raise ResponseParseAgentError(
                f"LLM returned non-JSON content and no tool result found. "
                f"Content type: {'markdown' if content.startswith('#') else 'plain_text'}. "
                f"Preview: {content[:200]}"
            ) from e
```

---

### Fix-4 (P2，可选): 添加 fail-fast 选项

> **当前流水线继续运行是允许的设计行为**。以下为可选扩展，满足需要强制中断场景的未来需求。

```python
# pipeline/orchestrator.py 或 pipeline/graph.py
if node_result.status == "failed" and node_config.runtime.fail_fast:
    self.logger.error("pipeline_aborted_on_failure", node_id=node_id)
    break  # 中止后续节点执行
```

---

## 五、修复优先级与预期效果

| 修复 | 优先级 | 状态 | 预期效果 |
|------|--------|------|----------|
| Fix-1: 接入节点 `runtime.timeout` 配置 | P0 | ⏳ 待实施 | 避免 LLM 推理中途被截断 |
| Fix-2A: `_agent_file` 路径补全 `autoBMAD/` | P0 | ✅ 已实施 | agent_file 可被正确加载 |
| Fix-2B: `cwd` 改为仓库根目录，拆分输出路径 | P0 | ⏳ 待实施 | LLM 能看到并调用工具 |
| Fix-3: fallback 扩展 | P1 | ⏳ 待实施 | 工具已调用时即使格式错误也能恢复 |
| Fix-4: fail-fast（可选扩展） | P2 | ⏳ 待实施 | 满足未来强制中断场景需求 |

**最小修复集**（使基本流程通过）：Fix-1 + Fix-2B

---

## 六、验证方法

### 验证工具不可见问题已修复
在 `independent.py` 的 `_call_llm_with_prompts()` 中添加：
```python
self.logger.info(
    "tool_availability_check",
    agent_file=str(self._agent_file),
    agent_file_exists=self._agent_file.exists() if self._agent_file else False,
)
```
期望日志：`agent_file_exists=True` + 后续出现 `tool_use` 日志

### 验证超时已修复
日志中应在 300s 内出现 `llm_prompt_complete`，而非 `prompt_timeout`。

### 验证完整流程
```bash
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```
期望：`output/pipeline-*/` 目录下出现 5 个 `.md` 文件（每个节点一个交付物）。

---

## 七、参考文件

| 文件 | 相关代码位置 |
|------|------------|
| `autoBMAD/docuswarm/llm/session_manager.py` | L730: `DEFAULT_PROMPT_TIMEOUT=60` |
| `autoBMAD/docuswarm/llm/session_manager.py` | L792: `asyncio.timeout()` |
| `autoBMAD/docuswarm/agents/independent.py` | L622: `self._agent_file` 构造 |
| `autoBMAD/docuswarm/agents/independent.py` | L444-510: `_parse_response()` |
| `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` | 工具注册配置 |
| `autoBMAD/nodes/analyst/node.yaml` | L31-34: `runtime.timeout=300`（未生效） |
| `autoBMAD/nodes/loader.py` | L387-393: runtime 配置加载 |
| `tools/timeout_incomplete_response_analyzer.py` | 本报告对应调试工具 |

---

*报告生成时间: 2026-04-06*  
*分析方法: 源码静态分析 + 运行时日志对比 + 专用调试工具执行*
