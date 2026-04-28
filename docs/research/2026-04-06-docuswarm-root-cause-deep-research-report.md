# DocuSwarm 根因深度研究报告

**研究日期**: 2026-04-06
**研究工具**: `tools/docuswarm_root_cause_deep_researcher.py`
**研究范围**: autoBMAD/docuswarm 核心模块
**特别说明**: 本报告所有超时配置已统一调整为 **60s** (调试/测试配置)

---

## 执行摘要

本次深度研究确认了 **5** 个根因:
- **P0 CRITICAL**: 2
- **P1 HIGH**: 2
- **P2 MEDIUM**: 1

### 根因关系与触发链

```
RC-1 (工具不可见: cwd 职责未拆分)
  -> LLM 无法调用 create_deliverable
RC-2 (超时 60s)
  -> LLM 在 ThinkingBlock 阶段被中断
RC-4 (ThinkingBlock 被 str 化)
  -> messages 包含非 JSON 内容
RC-3 (fallback 覆盖不足)
  -> parse_json 失败
RC-5 (流水线继续 - 设计允许)
  -> 后续节点同样失败
```

### 修复状态总览

| 根因 | 优先级 | 状态 | 修复建议 |
|------|--------|------|----------|
| RC-1 | P0 | confirmed | 3 项 |
| RC-2 | P0 | confirmed | 2 项 |
| RC-3 | P1 | confirmed | 2 项 |
| RC-4 | P1 | confirmed | 2 项 |
| RC-5 | P2 | confirmed | 3 项 |

---

## RC-1: create_deliverable tool invisible to LLM (cwd responsibility split issue)

**严重程度**: P0
**确认状态**: confirmed

### 证据

- agent_file setting 1 includes autoBMAD/ layer
- agent_file setting 2 includes autoBMAD/ layer
- options.cwd = self._work_dir, where work_dir = output/pipeline_id
- Tool module autoBMAD.docuswarm.tools.create_deliverable cannot be imported from output/pipeline_id
- Tool registered: autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool
- Tool module file exists: D:\GITHUB\DocuSwarm\autoBMAD\docuswarm\tools\create_deliverable.py
- CreateDeliverableTool supports output_dir parameter (Fix-2B prerequisite satisfied)
- work_dir has dual responsibility: (1) SDK cwd (affects Python import); (2) File output directory
- Two responsibilities need different paths: cwd should be repo root, output dir should be output/pipeline_id

### 相关代码

**agent_file_set_1**:
```python
self._agent_file = (
            self.project_root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
        )
```

**agent_file_set_2**:
```python
self._agent_file = (
            self.project_root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
        )
```

**_create_options**:
```python
def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
        """Create ClaudeAgentOptions from configuration.

        Args:
            mode: Session mode ("instant", "thinking", or "agent").
            yolo: Whether to auto-approve tool calls.

        Returns:
            ClaudeAgentOptions instance with MCP server configuration.
        """
        # Determine permission mode based on yolo
        permission_mode = "bypassPermissions" if yolo else "defaul
```

**independent_agent_yaml**:
```python
# Agent file for Independent Agent
# This file configures the tools available to the Independent Agent
# Format follows kimi-agent-sdk agent_file specification
# 
# NOTE: This is a docs-free configuration per P1-2 decision.
# All output is directed to the pipeline output directory.

version: 1

agent:
  extend: default
  tools:
    - "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "autoBMAD.docuswarm.tools.update_context:UpdateContextTool"
    - "autoBMAD.docuswarm.tool
```

### 修复建议

- Use CreateDeliverableTool(output_dir=output_dir) to pass output directory explicitly
- Fix-2B: Change SessionManager work_dir to repo root (for import)
- Fix-2B: Pass output_dir=output/pipeline_id explicitly to CreateDeliverableTool

---

## RC-2: DEFAULT_PROMPT_TIMEOUT=60s

**严重程度**: P0
**确认状态**: confirmed
**特别说明**: 当前配置为 60s（测试/调试配置）

### 证据

- DEFAULT_PROMPT_TIMEOUT = 60s (测试配置)
- NodeLoader reads runtime.timeout from node.yaml (默认 60s)
- analyst node config timeout = 60s
- No code passes node_config.runtime.timeout to session.prompt()
- Actual timeout is always DEFAULT_PROMPT_TIMEOUT (60s)
- Timeout trigger location: ClaudeSessionWrapper.prompt() asyncio.timeout()

### 相关代码

**DEFAULT_PROMPT_TIMEOUT**:
```python
DEFAULT_PROMPT_TIMEOUT: int = 60
```

**timeout_mechanism**:
```python
async with asyncio.timeout(effective_timeout):
```

### 修复建议

- Fix-1A: In executor.py or dual_agent.py, read node_config.runtime.timeout and pass to session.prompt(timeout=...)
- Fix-1B: 如需调整，将 DEFAULT_PROMPT_TIMEOUT 从 60s 改为其他值

---

## RC-3: _parse_response fallback doesn't handle plain text/English prose format

**严重程度**: P1
**确认状态**: confirmed

### 证据

- fallback condition 1: content.startswith(('#', '##', '###'))
- fallback condition 2: 'Summary' in content[:100]
- fallback doesn't handle plain English prose format (e.g., 'The tools appear to have...')
- _extract_create_deliverable_result() can extract tool results from messages
- Observed error content: 'The tools appear to have some issues, but I need to complete...'

### 相关代码

**_parse_response**:
```python
def _parse_response(self, response: list[dict[str, Any]]) -> IndependentOutput:
        """Parse and validate LLM response against IndependentOutput schema.

        Args:
            response: The list[dict[str, Any]] from the LLM.

        Returns:
            Parsed and validated output dictionary.

        Raises:
            ResponseParseAgentError: If parsing or validation fails.
        """
        content = self._extract_content_from_messages(response)

        if not content or not cont
```

### 修复建议

- Fix-3: Extend fallback condition with 'not content.strip().startswith("{")' check
- Fix-3: Any non-JSON content should attempt tool result extraction from messages

---

## RC-4: ThinkingBlock filtered -> incomplete message content

**严重程度**: P1
**确认状态**: confirmed

### 证据

- ThinkingBlock filtered to None by _convert_content_block
- duck typing fallback converts non-text types to {type: item_type, content: str(item)}
- ThinkingBlock.type='thinking' enters messages through fallback
- Error is 'No JSON found' not 'Empty response', messages is not empty
- Messages content is ThinkingBlock str-ed non-JSON text
- RC-4 actual root cause: Tool invisible (RC-1) -> LLM can't call tools -> response all ThinkingBlock
- ThinkingBlock str-ed enters messages -> extract_json can't find JSON -> parse fails

### 相关代码

**_convert_content_block**:
```python
def _convert_content_block(self, item: Any) -> dict[str, Any] | None:
        """Convert a content block to dict format.

        Fix: 使用 isinstance 判断类型，而非依赖 type 属性。
        ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock

        Args:
            item: Content block from SDK.

        Returns:
            Dict representation of content block or None.
        """
        converted = None

        try:
            from claude_agent_sdk.types import (
                T
```

### 修复建议

- Fix-2B (RC-1 fix): After tools visible, LLM calls tools normally, ThinkingBlock issue resolved
- Optional: Keep ThinkingBlock in _convert_content_block for debugging

---

## RC-5: analyst failure continues pipeline (design behavior)

**严重程度**: P2
**确认状态**: confirmed

### 证据

- Using LangGraph StateGraph for node execution management
- Log evidence: after analyst node_execution_failed, pm node_execution_started immediately
- Design intent: Pipeline nodes execute independently, predecessor failure doesn't force interrupt
- Design rationale: Allow partial output

### 修复建议

- Current behavior is by design, not mandatory to fix
- Fix-4 (optional): Add fail_fast: true option in node.yaml for forced interruption
- Fix-4 implementation: In pipeline/graph.py, interrupt when node fails and fail_fast=true

---

## 最小修复集 (Minimum Fix Set)

要使基本流程通过，必须实施以下修复:

### 必须修复 (P0)

1. **Fix-2B**: 拆分 `cwd` 职责
   - 修改 `SessionManager.__init__()` 接受 `cwd` 和 `output_dir` 两个参数
   - `cwd` 设为仓库根目录 (用于 Python import)
   - `output_dir` 设为 `output/pipeline_id` (用于文件输出)
   - 修改 `CreateDeliverableTool` 实例化时传入 `output_dir`

2. **Fix-1**: 接入节点超时配置
   - 修改 `executor.py` 或 `dual_agent.py` 读取 `node_config.runtime.timeout`
   - 将 timeout 值传入 `session.prompt(user_prompt, timeout=node_timeout)`
   - **当前配置**: 所有 timeout 统一为 **60s**

## 详细修复步骤

### Fix-2B: cwd 职责拆分 (P0)

**问题**: `work_dir` 同时承担两个职责:
1. SDK 进程工作目录 (影响 Python import 路径)
2. 文件输出目录 (`create_deliverable` 写文件位置)

**方案**: 在 `SessionManager` 中拆分两个路径:

```python
# session_manager.py _create_options()
options_dict: dict[str, Any] = {
    "cwd": self._repo_root,  # 仓库根目录，用于 import autoBMAD
    "permission_mode": permission_mode,
}
```

```python
# independent.py execute_with_input()
# 工具实例化时传入 output_dir
tool = CreateDeliverableTool(output_dir=output_dir)
```

### Fix-1: 超时配置接入 (P0)

**问题**: `node.yaml` 中配置的 `runtime.timeout: 60` 从未被代码读取使用

**方案**: 在节点执行时读取并传入:

```python
# executor.py 或 dual_agent.py
from autoBMAD.nodes.loader import NodeLoader

node_config = NodeLoader.load(node_id)
node_timeout = node_config.runtime.timeout  # 60s

# 调用时传入
async for msg in session.prompt(user_prompt, timeout=node_timeout):
    ...
```

## 验证方法

### 验证工具不可见问题已修复

在日志中应观察到:
```
tool_availability_check: agent_file_exists=True
...
llm_tool_call: tool_name='create_deliverable'
```

### 验证超时已修复

在日志中应在 60s 内出现:
```
llm_prompt_complete: message_count=...
```
而非:
```
prompt_timeout: timeout_seconds=60
```

### 验证完整流程

```bash
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

期望: `output/pipeline-*/` 目录下出现 5 个 `.md` 文件

## 参考文件

| 文件 | 相关代码位置 | 作用 |
|------|------------|------|
| `autoBMAD/docuswarm/llm/session_manager.py` | L730: `DEFAULT_PROMPT_TIMEOUT=60` | 硬编码超时值 (60s) |
| `autoBMAD/docuswarm/llm/session_manager.py` | L146: `options.cwd = self._work_dir` | cwd 设置问题 |
| `autoBMAD/docuswarm/agents/independent.py` | L622: `self._agent_file` 构造 | agent_file 路径 |
| `autoBMAD/docuswarm/agents/independent.py` | L444-510: `_parse_response()` | parse fallback |
| `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` | tools 列表 | 工具注册配置 |
| `autoBMAD/nodes/analyst/node.yaml` | L32: `runtime.timeout=60` | 节点超时配置 (60s) |
| `autoBMAD/nodes/loader.py` | L389-393: runtime 配置加载 | 配置加载逻辑 |

## 附录: 研究详细日志

```
[INFO] [1/6] Analyzing agent_file path construction...
[INFO] Found 2 _agent_file settings
[INFO]   [OK] Setting 1 includes autoBMAD/ layer
[INFO]   [OK] Setting 2 includes autoBMAD/ layer
[INFO] [2/6] Analyzing SDK options.cwd setting (critical)...
[INFO]   [ERROR] options.cwd = self._work_dir (problem confirmed!)
[INFO]   [ERROR] work_dir is output/pipeline_id, not repo root
[INFO] [3/6] Analyzing tool registration config...
[INFO]   Registered tools: 3
[INFO]     - autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool
[INFO]     - autoBMAD.docuswarm.tools.update_context:UpdateContextTool
[INFO]     - autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool
[INFO] [4/6] Verifying tool module file existence...
[INFO]   [OK] Tool module exists: D:\GITHUB\DocuSwarm\autoBMAD\docuswarm\tools\create_deliverable.py
[INFO] [5/6] Analyzing CreateDeliverableTool output_dir support...
[INFO]   [OK] CreateDeliverableTool supports output_dir parameter
[INFO] [6/6] Analyzing SessionManager work_dir dual responsibility...
[SUCCESS] [RC-1] Research complete - status: confirmed
[INFO] [1/5] Checking ClaudeSessionWrapper default timeout...
[INFO]   DEFAULT_PROMPT_TIMEOUT = 60s
[INFO]   [OK] 60s is current test configuration
[INFO] [2/5] Checking node runtime.timeout config reading...
[INFO]   [OK] NodeLoader correctly reads runtime.timeout (default 60s)
[INFO] [3/5] Verifying analyst node timeout config...
[INFO]   analyst node config timeout: 60s
[INFO] [4/5] Checking if timeout is passed to session.prompt()...
[INFO]   Found 1 session.prompt() calls
[INFO]   [ERROR] No call passes timeout parameter!
[INFO] [5/5] Analyzing timeout trigger mechanism...
[INFO]   Timeout mechanism: asyncio.timeout(effective_timeout)
[SUCCESS] [RC-2] Research complete - status: confirmed
[INFO] [1/4] Analyzing _parse_response fallback conditions...
[INFO]   Found fallback condition: content.startswith('#', '##', '###')
[INFO]   Found fallback condition: 'Summary' in content[:100]
[INFO]   [ERROR] Plain text/English prose format not handled!
[INFO] [2/4] Analyzing tool result extraction function...
[INFO]   [OK] _extract_create_deliverable_result function exists
[INFO] [3/4] Analyzing observed error content characteristics...
[INFO]   Content starts with '#': False
[INFO]   Contains 'Summary': False
[INFO]   Result: This content won't trigger markdown_fallback!
[INFO] [4/4] Checking actual fallback behavior...
[SUCCESS] [RC-3] Research complete - status: confirmed
[INFO] [1/4] Analyzing _convert_content_block ThinkingBlock handling...
[INFO]   ThinkingBlock explicitly filtered to None (design decision)
[INFO] [2/4] Analyzing duck typing fallback...
[INFO]   Found duck typing fallback logic
[INFO]   ThinkingBlock will become type='thinking' through fallback
[INFO] [3/4] Verifying messages state at timeout...
[INFO]   Log shows: response_parse_failed: 'No JSON found in response'
[INFO]   Not: 'Empty response from LLM'
[INFO] [4/4] Correcting root cause relationship...
[SUCCESS] [RC-4] Research complete - status: confirmed
[INFO] [1/3] Analyzing LangGraph node execution mechanism...
[INFO]   Found LangGraph add_node calls
[INFO] [2/3] Checking node execution failure handling...
[INFO] [3/3] Verifying design intent...
[INFO]   Log shows: analyst failed -> pm started (immediately)
[SUCCESS] [RC-5] Research complete - status: confirmed
[INFO] [Verify] Fix-2A: agent_file path includes autoBMAD/...
[INFO]   [OK] Fix-2A applied: agent_file path includes autoBMAD/
[INFO] [Verify] Fix-2B: cwd changed to repo root...
[INFO]   [ERROR] Fix-2B pending: No root directory references in SessionManager
[INFO] [Verify] Fix-1: Node timeout passed to session.prompt()...
[INFO]   [ERROR] Fix-1 pending: node_config.runtime.timeout not passed to session.prompt()
```
