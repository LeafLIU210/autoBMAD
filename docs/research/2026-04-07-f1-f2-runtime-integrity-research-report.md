# F1/F2 运行时完整性深度研究报告

**报告编号**: DS-2026-04-07-F1F2-001  
**研究日期**: 2026-04-07  
**研究工具**: `tools/f1_f2_deep_dive_analyzer.py`  
**关联审查报告**: `docs/evaluation/2026-04-07-docuswarm-deep-reform-implementation-review.md`  
**关联方案文档**: `docs/research/docuswarm-deep-reform/` 全部文档  

---

## 执行摘要

本研究针对 DocuSwarm Deep Reform 实现审查报告中识别的两个关键问题（F1 和 F2）进行了深入的运行时完整性分析。通过静态代码分析、配置审查和运行时路径追踪，确认了以下核心发现：

| 问题 | 严重程度 | 状态 | 影响范围 |
|------|---------|------|---------|
| **F1**: Skills 白名单与 sdk_native 开关未真正生效 | CRITICAL | 已确认 | 全部5个节点 |
| **F2**: submit_execution_report 已实现但未被允许调用 | CRITICAL | 已确认 | JSON/MCP 闭环断裂 |

**核心结论**: 
- 配置到运行时的闭环存在多处断裂
- 方案文档描述的能力与实际运行时不一致
- 需要紧急修复以确保 Deep Reform 成果真正可用

---

## 目录

1. [研究范围与方法](#1-研究范围与方法)
2. [F1 深度分析](#2-f1-深度分析)
3. [F2 深度分析](#3-f2-深度分析)
4. [运行时闭环分析](#4-运行时闭环分析)
5. [修复建议](#5-修复建议)
6. [附录](#6-附录)

---

## 1. 研究范围与方法

### 1.1 研究目标

- **F1 验证**: 确认 Skills 白名单与 sdk_native 开关是否在运行时真正生效
- **F2 验证**: 确认 submit_execution_report 工具是否可真正被调用
- **闭环分析**: 追踪从 node.yaml 配置到 SDK 运行时的完整路径
- **断裂定位**: 精确定位配置到运行时的断裂点

### 1.2 研究方法

| 方法 | 描述 | 应用 |
|------|------|------|
| 静态代码分析 | 审查关键方法的实现 | SessionManager, NodeToolFilter, IndependentAgent |
| 配置审查 | 检查 node.yaml 的 skills 配置 | 5个节点的配置文件 |
| 调用链追踪 | 追踪配置如何从 YAML 流向 SDK | loader → agent → session_manager → sdk |
| 运行时模拟 | 验证代码路径的实际行为 | 通过分析器模拟运行时检查 |

### 1.3 分析工具

```bash
# 运行深度分析工具
python tools/f1_f2_deep_dive_analyzer.py
```

该工具会自动：
1. 分析 `SessionManager._build_allowed_tools()` 方法
2. 分析 `SessionManager._create_options()` 方法
3. 分析 `IndependentAgent.execute_with_input()` 中的权限重建
4. 分析 `NodeToolFilter.get_allowed_tools()` 方法
5. 检查所有 node.yaml 的 skills 配置
6. 生成详细的研究报告

---

## 2. F1 深度分析

### 2.1 问题描述

**方案期望** (来自 `01-skills-introduction-mechanism.md`):
- Skills 是否启用应由节点级 `tools.skills.sdk_native` 控制
- Skills 可见范围应受 `tools.skills.whitelist` 限制
- `node.yaml -> SessionManager/ClaudeAgentOptions` 应形成完整闭环

**实际实现问题**:
- `SessionManager._build_allowed_tools()` 无条件加入 `"Skill"`，未检查节点 `sdk_native`
- `SessionManager._create_options()` 无条件启用 `setting_sources=["project"]`
- `IndependentAgent.execute_with_input()` 重建 `NodeToolPermissions` 时丢失了 `skills` 与 `shared_context` 子配置

### 2.2 代码证据

#### 2.2.1 SessionManager._build_allowed_tools() - 无条件启用 Skill

**文件**: `autoBMAD/docuswarm/llm/session_manager.py:173-217`

```python
def _build_allowed_tools(self) -> list[str]:
    """Build the complete list of allowed tools."""
    tools: list[str] = []

    # Add "Skill" tool as first entry for SDK native skills priority
    tools.append("Skill")  # ← 无条件添加，未检查 sdk_native

    # Add built-in tools
    tools.extend(self._get_builtin_tools())

    # Add MCP tools if node_id and tool_permissions are configured
    if self._node_id and self._tool_permissions is not None:
        # ... MCP tools ...
        pass

    return tools
```

**问题分析**:
- 方法在开头就无条件添加 `"Skill"` 到 allowed_tools
- 没有检查 `self._tool_permissions.skills.sdk_native` 的值
- 即使 node.yaml 设置 `sdk_native: false`，Skill 工具仍然会被启用

#### 2.2.2 SessionManager._create_options() - 无条件启用 setting_sources

**文件**: `autoBMAD/docuswarm/llm/session_manager.py:238-243`

```python
options_dict: dict[str, Any] = {
    "cwd": self._cwd,
    "permission_mode": permission_mode,
    "setting_sources": [
        "project"
    ],  # Enable SDK auto-discovery of skills from .claude/skills/
}
```

**问题分析**:
- `setting_sources` 被无条件设置为 `["project"]`
- 这会导致 SDK 自动从 `.claude/skills/` 目录发现所有技能
- 没有检查 `sdk_native` 开关，即使为 false 也会启用技能发现

#### 2.2.3 IndependentAgent.execute_with_input() - 丢失 skills 配置

**文件**: `autoBMAD/docuswarm/agents/independent.py:967-978`

```python
# P0 Fix: Build complete NodeToolPermissions with allowed_builtin_tools
from autoBMAD.nodes.loader import (
    NodeFilePermissions,
    NodeSearchPermissions,
    NodeToolPermissions,
)

full_tool_permissions = NodeToolPermissions(
    allowed_builtin_tools=node_config.tool_permissions.allowed_builtin_tools,
    file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
    search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
    # ← 缺失: skills=node_config.tool_permissions.skills
    # ← 缺失: shared_context=node_config.tool_permissions.shared_context
)
```

**问题分析**:
- 重建 `NodeToolPermissions` 时只传递了 `allowed_builtin_tools`, `file_permissions`, `search_permissions`
- 丢失了 `skills` 和 `shared_context` 配置
- 从 node.yaml 加载的精细配置在运行时丢失

### 2.3 配置与运行时对比

#### Analyst 节点示例

**node.yaml 配置**:
```yaml
tools:
  skills:
    sdk_native: true
    whitelist:
      - bmad-product-brief
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
```

**实际运行时行为**:
| 配置项 | node.yaml 值 | 实际运行时 | 匹配 |
|--------|-------------|-----------|------|
| sdk_native | true | 被忽略（总是启用） | ❌ |
| whitelist | 4个技能 | 仅用于 prompt 注入 | ❌ |
| 实际可用技能 | 应受限制 | 所有 .claude/skills/ 中的技能 | ❌ |

### 2.4 F1 问题影响

1. **安全边界失效**: 白名单仅作为提示词建议，不是真正的权限边界
2. **审计困难**: 无法证明某节点只暴露了其被允许的技能
3. **配置误导**: 用户看到 node.yaml 的配置会误以为有权限控制

---

## 3. F2 深度分析

### 3.1 问题描述

**方案期望** (来自 `2026-04-06-json-retry-mcp-schema-constraint-research-report.md`):
- IndependentAgent 使用 `create_deliverable` 之后，必须继续调用 `submit_execution_report`
- `submit_execution_report` 应成为结构化 execution report 的主路径

**实际实现问题**:
- Agent 系统提示中明确要求两步工具调用序列
- MCP deliverable server 确实注册了 `submit_execution_report`
- 但 `NodeToolFilter.get_allowed_tools()` 只放行 `create_deliverable`，没有放行 `submit_execution_report`

### 3.2 代码证据

#### 3.2.1 IndependentAgent 系统提示 - 要求调用 submit_execution_report

**文件**: `autoBMAD/docuswarm/agents/independent.py:148-171`

```python
instructions = f"""## Agent Instructions

## CRITICAL: Mandatory Tool Call Sequence (Story 38.4)

You MUST follow this exact tool call sequence:

### Step 1: Create Deliverable
Use the '{create_deliverable_tool}' tool to save your document:

### Step 2: Submit Execution Report (MANDATORY)
Use the '{submit_report_tool}' tool to submit your execution report:
"""
```

#### 3.2.2 create_deliverable_sdk.py - 工具已实现并注册

**文件**: `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:288-318`

```python
@tool(
    "submit_execution_report",
    "Submit an execution report with deliverable metadata and follow-up questions. ...",
    SUBMIT_EXECUTION_REPORT_SCHEMA,
)
async def submit_execution_report_tool(args: dict[str, Any]) -> dict[str, Any]:
    """MCP tool handler for submit_execution_report."""
    # ... implementation ...

# 注册到 MCP server
server = create_sdk_mcp_server(
    name=server_name,
    version="1.0.0",
    tools=[create_deliverable_tool, submit_execution_report_tool],  # ← 已注册
)
```

#### 3.2.3 NodeToolFilter.get_allowed_tools() - 未放行 submit_execution_report

**文件**: `autoBMAD/docuswarm/llm/tool_filter.py:153-159`

```python
# TDD-07: Always add deliverable MCP tool when output_dir is configured
if self.output_dir:
    tools.append(
        MCP_TOOL_NAME_FORMAT.format(
            type="deliverable", node_id=self.node_id, tool_name="create_deliverable"
        )
    )
    # ← 缺失: submit_execution_report 没有被添加到 tools 列表
```

**问题分析**:
- 只有 `create_deliverable` 被添加到 allowed_tools
- `submit_execution_report` 虽然已在 MCP server 注册，但不在允许列表中
- Claude SDK 不会向 LLM 暴露不在 allowed_tools 中的工具

### 3.3 F2 问题影响

1. **JSON/MCP 闭环断裂**: 系统提示要求调用的工具，运行时不可用
2. **回退到旧路径**: 运行时会回退到自由文本/JSON 解析路径
3. **约束失效**: `questions[].priority` 的 enum 约束无法被强制执行

---

## 4. 运行时闭环分析

### 4.1 配置到运行时的完整路径

```
node.yaml (配置层)
    ↓ 解析
NodeLoader._build_node_config() (loader.py)
    ↓ 创建
NodeConfig.tool_permissions: NodeToolPermissions (含 skills, shared_context)
    ↓ 传递
IndependentAgent.execute_with_input() (independent.py)
    ↓ 重建 (❌ 断裂点1: 丢失 skills, shared_context)
NodeToolPermissions (重建，仅含 builtin/file/search)
    ↓ 传递
SessionManager (session_manager.py)
    ↓ 调用
_build_allowed_tools() (❌ 断裂点2: 无条件添加 "Skill")
    ↓ 调用
_create_options() (❌ 断裂点3: 无条件设置 setting_sources)
    ↓ 创建
ClaudeAgentOptions
    ↓ 传递
ClaudeSDKClient
    ↓ 运行时
SDK 行为与配置不符
```

### 4.2 submit_execution_report 工具路径

```
create_deliverable_sdk.py (工具定义层)
    ↓ 定义
submit_execution_report 函数 + MCP tool handler
    ↓ 注册
create_deliverable_server() → tools 列表
    ↓ 创建 MCP server
create_sdk_mcp_server(name="docuswarm-deliverable-{node_id}", tools=[...])
    ↓ 传递
NodeToolFilter.create_mcp_servers() (tool_filter.py)
    ↓ 返回
servers dict 包含 deliverable server
    ↓ 设置到
ClaudeAgentOptions.mcp_servers
    ↓ 可用性检查 (❌ 断裂点)
NodeToolFilter.get_allowed_tools()
    ↓ 仅放行 create_deliverable
allowed_tools 列表不包含 submit_execution_report
    ↓ 运行时
Claude SDK 不暴露 submit_execution_report 给 LLM
```

### 4.3 断裂点汇总

| 断裂点 | 位置 | 问题 | 影响 |
|--------|------|------|------|
| 1 | independent.py:974-978 | 重建 NodeToolPermissions 丢失 skills, shared_context | F1 |
| 2 | session_manager.py:187 | 无条件添加 "Skill" | F1 |
| 3 | session_manager.py:241-243 | 无条件设置 setting_sources | F1 |
| 4 | tool_filter.py:153-159 | 不放行 submit_execution_report | F2 |

---

## 5. 修复建议

### 5.1 F1 修复方案

#### 修复 1: SessionManager._build_allowed_tools() 添加 sdk_native 检查

```python
def _build_allowed_tools(self) -> list[str]:
    """Build the complete list of allowed tools."""
    tools: list[str] = []

    # F1 Fix: 检查 sdk_native 开关
    if (self._tool_permissions is not None and 
        self._tool_permissions.skills.sdk_native):
        # Add "Skill" tool as first entry for SDK native skills priority
        tools.append("Skill")
        logger.debug("sdk_native_skills_enabled", node_id=self._node_id)
    else:
        logger.debug("sdk_native_skills_disabled", node_id=self._node_id)

    # Add built-in tools
    tools.extend(self._get_builtin_tools())
    # ... rest of the method
```

#### 修复 2: SessionManager._create_options() 添加 sdk_native 检查

```python
options_dict: dict[str, Any] = {
    "cwd": self._cwd,
    "permission_mode": permission_mode,
}

# F1 Fix: 条件性设置 setting_sources
if (self._tool_permissions is not None and 
    self._tool_permissions.skills.sdk_native):
    options_dict["setting_sources"] = ["project"]
    logger.debug("setting_sources_enabled", node_id=self._node_id)
```

#### 修复 3: IndependentAgent 保留完整 tool_permissions

```python
# F1 Fix: 使用 dataclasses.replace 保留所有配置
from dataclasses import replace

full_tool_permissions = replace(
    node_config.tool_permissions,
    file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
    search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
)
# 这样保留了原有的 skills 和 shared_context 配置
```

### 5.2 F2 修复方案

#### 修复: NodeToolFilter.get_allowed_tools() 放行 submit_execution_report

```python
# TDD-07: Always add deliverable MCP tools when output_dir is configured
if self.output_dir:
    tools.append(
        MCP_TOOL_NAME_FORMAT.format(
            type="deliverable", node_id=self.node_id, tool_name="create_deliverable"
        )
    )
    # F2 Fix: 添加 submit_execution_report 工具
    tools.append(
        MCP_TOOL_NAME_FORMAT.format(
            type="deliverable", node_id=self.node_id, tool_name="submit_execution_report"
        )
    )
```

### 5.3 修复优先级

| 优先级 | 修复项 | 原因 |
|--------|--------|------|
| P0 | F2: 放行 submit_execution_report | 影响 JSON/MCP 闭环，阻塞主路径 |
| P0 | F1: IndependentAgent 保留完整配置 | 导致配置丢失的根本问题 |
| P1 | F1: SessionManager 检查 sdk_native | 完善权限控制 |

---

## 6. 附录

### 6.1 相关文件清单

| 文件 | 作用 | 相关行号 |
|------|------|---------|
| `autoBMAD/docuswarm/llm/session_manager.py` | SessionManager 实现 | 173-217, 238-243 |
| `autoBMAD/docuswarm/llm/tool_filter.py` | NodeToolFilter 实现 | 153-159 |
| `autoBMAD/docuswarm/agents/independent.py` | IndependentAgent 实现 | 148-171, 967-978 |
| `autoBMAD/docuswarm/tools/create_deliverable_sdk.py` | MCP 工具定义 | 288-318 |
| `autoBMAD/nodes/loader.py` | NodeToolPermissions 定义 | 128-188 |

### 6.2 测试建议

```python
# 建议添加的测试用例

# Test 1: sdk_native=false 时不启用 Skill
def test_sdk_native_false_disables_skill():
    """当 sdk_native=false 时，allowed_tools 不应包含 'Skill'"""
    # ...

# Test 2: submit_execution_report 在 allowed_tools 中
def test_submit_execution_report_in_allowed_tools():
    """NodeToolFilter 应放行 submit_execution_report"""
    # ...

# Test 3: IndependentAgent 保留 skills 配置
def test_independent_agent_preserves_skills_config():
    """execute_with_input 应保留 node_config.tool_permissions.skills"""
    # ...
```

### 6.3 验证清单

修复完成后，请验证以下检查项：

- [ ] SessionManager._build_allowed_tools() 检查 sdk_native
- [ ] SessionManager._create_options() 条件设置 setting_sources
- [ ] IndependentAgent 保留完整的 skills 和 shared_context
- [ ] NodeToolFilter.get_allowed_tools() 包含 submit_execution_report
- [ ] 运行时 LLM 可以调用 submit_execution_report
- [ ] sdk_native=false 时 Skill 工具不被添加到 allowed_tools

---

**报告完成**: 2026-04-07  
**研究员**: F1/F2 深度分析工具  
**版本**: 1.0
