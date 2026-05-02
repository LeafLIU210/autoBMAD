# Claude Agent SDK 改造方案研究报告

**日期**: 2026-03-26  
**报告编号**: 05  
**作者**: Nick (General Engineer)  
**前置文档**:
- `docs/evaluation/2026-03-26-docuswarm-deep-architecture-analysis.md`
- `docs/evaluation/2026-03-26-docuswarm-implementation-gap-analysis.md`

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [当前 SDK 能力审计](#2-当前-sdk-能力审计)
3. [文件读取工具集成方案](#3-文件读取工具集成方案)
4. [搜索工具集成方案](#4-搜索工具集成方案)
5. [BMAD 斜杠命令注入方案](#5-bmad-斜杠命令注入方案)
6. [节点级工具权限配置方案](#6-节点级工具权限配置方案)
7. [提示词结构优化设计](#7-提示词结构优化设计)
8. [实施路线图](#8-实施路线图)
9. [风险评估](#9-风险评估)

---

## 1. 执行摘要

### 1.1 当前 SDK 能力现状

基于 `tools/agent_sdk_capability_auditor.py` 自动审计结果（2026-03-26），DocuSwarm 当前 Claude Agent SDK 集成的能力实现率为：

```
能力实现率：7/12（58.3%）
已实现能力：工具注册、权限控制、流式输出、会话管理、提示词注入、系统提示、Hooks 支持
缺失能力：MCP 工具集成、结构化输出（JSON Schema）、子 Agent 调用、思考模式完整配置、斜杠命令发送
斜杠命令总数：47 个（含 44 个 BMAD 工作流命令）
SDK 参考文档：25 个主题（agentdocs/ 目录）
```

### 1.2 改造目标

本次改造的核心目标为两项：

**目标一：启用文件读取和搜索工具**  
当前 `IndependentAgent` 在节点任务执行时无法主动读取项目文档（如 `docs/PRD.md`、`docs/architecture.md`），导致生成内容依赖于 context 注入，缺乏深度引用能力。改造方案通过 Claude Agent SDK 的 MCP 工具集成，注册 `file_read`、`grep_search`、`glob_search` 等工具，使各节点 Agent 能够按权限访问相关文档。

**目标二：注入 BMAD 斜杠命令**  
现有 47 个 BMAD 斜杠命令（位于 `.claude/skills/`）未通过 SDK 注入 Agent 工作流，导致节点无法利用专业化的 BMAD 工作流技能（如 `/bmad-create-prd`、`/bmad-create-architecture`）。改造方案通过 `system_prompt` 的 `append` 机制将命令说明以结构化文本形式注入每个节点的上下文，并在未来通过斜杠命令 API 直接调用。

### 1.3 改造收益预估

| 维度 | 改造前 | 改造后 |
|------|--------|--------|
| 文档引用能力 | 仅限 context 注入 | 主动读取任意已授权文件 |
| 搜索能力 | 无 | 按节点配置限定范围的 grep/glob |
| BMAD 技能利用率 | 0/47（0%） | ≥5/47 个核心命令注入 |
| 提示词结构 | 扁平字符串拼接 | 四层分层架构（身份+上下文+工具+技能） |
| 节点能力差异化 | 仅 persona 差异 | persona + 工具权限 + 专属技能三维差异 |

---

## 2. 当前 SDK 能力审计

### 2.1 已实现能力清单

根据审计工具对 15 个 LLM/Agent 相关文件的扫描结果：

#### 2.1.1 会话管理（Session Management）

| 能力 | 实现文件 | 核心方法 | 状态 |
|------|----------|----------|------|
| 创建新会话 | `llm/session_manager.py:141` | `create_session(mode, yolo)` | ✅ 已实现 |
| 恢复会话 | `llm/session_manager.py:222` | `resume_session(session_id)` | ✅ 已实现 |
| 恢复或新建 | `llm/session_manager.py:263` | `resume_or_create(...)` | ✅ 已实现 |
| 单次提示 | `llm/session_manager.py:309` | `single_prompt(prompt, mode)` | ✅ 已实现 |
| 关闭所有会话 | `llm/session_manager.py:468` | `close_all()` | ✅ 已实现 |
| Orchestrator 会话管理 | `pipeline/orchestrator.py:175` | `_get_or_create_session_manager()` | ✅ 已实现 |

```python
# session_manager.py - _create_options 方法（核心配置构建）
def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
    model = os.environ.get("CLAUDE_MODEL_NAME", "claude-3-opus-20240229")
    permission_mode = "bypassPermissions" if yolo else "default"
    options_dict = {
        "cwd": self._work_dir,
        "model": model,
        "permission_mode": permission_mode,
    }
    if self._agent_file:
        options_dict["tools"] = [str(self._agent_file)]  # 通过 agent_file 注册工具
    return ClaudeAgentOptions(**options_dict)
```

#### 2.1.2 提示词构建（Prompt Injection）

| 能力 | 实现文件 | 核心方法 | 状态 |
|------|----------|----------|------|
| Persona 格式化 | `agents/persona.py:187` | `PersonaLoader.format_system_prompt()` | ✅ 已实现 |
| 系统提示基类 | `agents/base.py:74` | `_format_system_prompt()` | ✅ 已实现（抽象） |
| 独立 Agent 系统提示 | `agents/independent.py:128` | `_format_system_prompt()` | ✅ 已实现 |
| 契约式系统提示 | `agents/independent.py:223` | `_format_system_prompt_with_contract()` | ✅ 已实现 |

#### 2.1.3 权限控制（Permissions）

| 能力 | 实现方式 | 状态 |
|------|----------|------|
| bypassPermissions 模式 | `yolo=True` → `permission_mode="bypassPermissions"` | ✅ 已实现 |
| 默认权限模式 | `yolo=False` → `permission_mode="default"` | ✅ 已实现 |
| approval_handler_fn | `create_session(approval_handler_fn=...)` 参数支持 | ✅ 已实现 |

#### 2.1.4 工具注册（Tool Registration）

当前通过 `agent_file` 方式注册工具：

```python
# session_manager.py:133
if self._agent_file:
    options_dict["tools"] = [str(self._agent_file)]

# session_manager.py:184  
if effective_agent_file:
    options.tools = [str(effective_agent_file)]
```

**局限**：工具注册方式为静态 YAML 文件路径，未使用 `mcp_servers` API 注册动态工具。

### 2.2 缺失能力清单

| 能力 | 缺失程度 | 参考文档 | 优先级 |
|------|----------|----------|--------|
| MCP 工具集成（mcp_servers） | 完全缺失 | `agentdocs/18_mcp.md` | P0 |
| 斜杠命令发送（`/` 前缀） | 完全缺失 | `agentdocs/21_slash_commands.md` | P0 |
| 结构化输出（JSON Schema） | 完全缺失 | `agentdocs/14_structured_outputs.md` | P1 |
| 子 Agent 调用（AgentDefinition） | 完全缺失 | `agentdocs/20_subagents.md` | P2 |
| 思考模式完整配置 | 部分缺失（有 mode 但无 max_thinking_tokens） | `agentdocs/05_python.md` | P2 |

### 2.3 Claude Agent SDK 参考 vs 当前实现差距分析

#### ClaudeAgentOptions 字段使用率

```
ClaudeAgentOptions 全部字段（Python SDK）：
  tools              ✅ 使用（agent_file 方式）
  allowed_tools      ❌ 未使用（应显式指定允许工具）
  system_prompt      ❌ 未通过 ClaudeAgentOptions 传递（通过 prompt 字符串拼接）
  mcp_servers        ❌ 未使用
  permission_mode    ✅ 使用（"bypassPermissions" / "default"）
  resume             ❌ 未使用（通过内部 session_id 机制替代）
  max_turns          ❌ 未使用
  model              ✅ 使用
  cwd                ✅ 使用
  hooks              ❌ 未使用（仅支持 approval_handler_fn）
  agents             ❌ 未使用（子 Agent）
  enable_file_checkpointing ❌ 未使用
  max_thinking_tokens ❌ 未使用
  setting_sources    ❌ 未使用（CLAUDE.md 未读取）
```

**字段使用率**: 4/17（23.5%）— 大量 SDK 能力未被激活

#### 关键差距：system_prompt 注入方式

**当前方式（不推荐）**：
```python
# agents/independent.py:284 - system_prompt 拼接到 user prompt
full_prompt = f"{system_prompt}\n\n{user_prompt}"
messages = await session_manager.single_prompt(full_prompt)
```

**推荐方式（SDK 原生支持）**：
```python
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": persona_prompt + skill_injection
    }
)
```

当前实现将 system_prompt 混入 user prompt，导致：
1. Claude 无法区分"身份指令"与"任务内容"
2. system_prompt 的优先级语义丢失
3. 无法利用 `claude_code` preset 的工具使用说明

---

## 3. 文件读取工具集成方案

### 3.1 Claude Agent SDK 内置文件工具 API 规范

根据 `agentdocs/05_python.md`，Claude Agent SDK 通过 `allowed_tools` 参数启用内置工具：

```python
# 内置工具名称（Claude Code 工具集）
CLAUDE_CODE_BUILT_IN_TOOLS = [
    "Read",       # 读取文件内容
    "Write",      # 写入文件
    "Edit",       # 编辑文件（diff 方式）
    "Bash",       # 执行 bash 命令
    "Glob",       # 文件路径匹配
    "Grep",       # 内容搜索
    "LS",         # 列出目录
    "Task",       # 启动子 Agent
]
```

**文件读取工具注册示例**（Python SDK）：

```python
from claude_agent_sdk.types import ClaudeAgentOptions

# 方式一：通过 allowed_tools 启用内置 Read 工具
options = ClaudeAgentOptions(
    allowed_tools=["Read"],           # 启用文件读取
    permission_mode="acceptEdits",    # 自动批准（不含破坏性操作）
    cwd="/home/project"              # 工作目录
)
```

### 3.2 自定义文件读取工具（MCP 进程内服务器）

对于需要路径白名单控制的场景，推荐通过 `create_sdk_mcp_server` 注册自定义文件读取工具：

```python
# autoBMAD/docuswarm/tools/file_tools.py
from claude_agent_sdk import tool, create_sdk_mcp_server
from pathlib import Path
from typing import Any
import os

def create_file_read_server(allowed_dirs: list[str], node_id: str):
    """创建节点专属文件读取 MCP 服务器。
    
    Args:
        allowed_dirs: 允许读取的目录列表（绝对路径）
        node_id: 节点 ID，用于日志标识
    
    Returns:
        SdkMcpServer 实例
    """
    
    @tool(
        "read_document",
        "读取项目文档内容。仅允许读取预定义的文档目录内的文件。",
        {
            "file_path": str,
            "encoding": str,
        }
    )
    async def read_document(args: dict[str, Any]) -> dict[str, Any]:
        file_path = args["file_path"]
        encoding = args.get("encoding", "utf-8")
        
        # 安全检查：路径遍历防护
        abs_path = os.path.abspath(file_path)
        
        # 路径白名单检查
        is_allowed = any(
            abs_path.startswith(os.path.abspath(d))
            for d in allowed_dirs
        )
        
        if not is_allowed:
            return {
                "content": [{
                    "type": "text",
                    "text": f"权限拒绝：路径 '{file_path}' 不在允许的目录内。"
                              f"允许的目录：{allowed_dirs}"
                }]
            }
        
        # 文件存在性检查
        path = Path(abs_path)
        if not path.exists():
            return {
                "content": [{
                    "type": "text",
                    "text": f"文件不存在：{file_path}"
                }]
            }
        
        if not path.is_file():
            return {
                "content": [{
                    "type": "text",
                    "text": f"路径不是文件：{file_path}"
                }]
            }
        
        try:
            content = path.read_text(encoding=encoding)
            return {
                "content": [{
                    "type": "text",
                    "text": f"文件内容（{file_path}）：\n\n{content}"
                }]
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"读取文件失败：{str(e)}"
                }]
            }

    @tool(
        "list_documents",
        "列出允许目录内的所有文档文件",
        {
            "directory": str,
            "pattern": str,
        }
    )
    async def list_documents(args: dict[str, Any]) -> dict[str, Any]:
        directory = args.get("directory", "")
        pattern = args.get("pattern", "**/*.md")
        
        # 确定基础目录
        if directory:
            abs_dir = os.path.abspath(directory)
        else:
            # 使用第一个允许的目录
            abs_dir = os.path.abspath(allowed_dirs[0]) if allowed_dirs else "."
        
        # 权限检查
        is_allowed = any(
            abs_dir.startswith(os.path.abspath(d))
            for d in allowed_dirs
        )
        if not is_allowed:
            return {
                "content": [{"type": "text", "text": f"权限拒绝：目录 '{directory}' 不在允许范围内"}]
            }
        
        try:
            base = Path(abs_dir)
            files = list(base.glob(pattern))
            file_list = "\n".join(str(f.relative_to(base)) for f in files if f.is_file())
            return {
                "content": [{"type": "text", "text": f"目录 {directory} 下的文件：\n{file_list}"}]
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"列目录失败：{str(e)}"}]
            }

    return create_sdk_mcp_server(
        name=f"docuswarm-files-{node_id}",
        version="1.0.0",
        tools=[read_document, list_documents]
    )
```

### 3.3 权限控制方案：节点-目录映射

根据各节点职责，设计文件读取权限白名单：

| 节点 | 允许读取目录 | 禁止读取 | 理由 |
|------|-------------|----------|------|
| `analyst` | `docs/`, `docs/research/` | `docs/stories/`, `autoBMAD/` | 仅需分析需求和研究文档 |
| `pm` | `docs/`, `docs/analyst/` | `autoBMAD/`, `.env` | 基于需求分析创建 PRD |
| `ux` | `docs/`, `docs/analyst/`, `docs/plan/` | `autoBMAD/` | 需要需求和计划 |
| `architect` | `docs/`, `docs/analyst/`, `docs/plan/`, `docs/design/` | `autoBMAD/` | 需要全部上游输出 |
| `po` | `docs/` (全部) | `autoBMAD/`, `.env`, `*.db` | PO 整合所有文档 |

### 3.4 集成到 SessionManager

```python
# autoBMAD/docuswarm/llm/session_manager.py 改造版本

from autoBMAD.docuswarm.tools.file_tools import create_file_read_server

class SessionManager:
    def __init__(
        self,
        work_dir: Path,
        agent_file: Path | None = None,
        config: Any | None = None,
        node_id: str | None = None,          # 新增：节点 ID
        allowed_dirs: list[str] | None = None, # 新增：文件权限目录
    ) -> None:
        ...
        self._node_id = node_id
        self._allowed_dirs = allowed_dirs or []
    
    def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
        model = os.environ.get("CLAUDE_MODEL_NAME", "claude-3-opus-20240229")
        permission_mode = "bypassPermissions" if yolo else "default"
        
        options_dict: dict[str, Any] = {
            "cwd": self._work_dir,
            "model": model,
            "permission_mode": permission_mode,
            "allowed_tools": ["Read", "Glob"],  # 启用内置工具
        }
        
        # 注册自定义文件读取 MCP 服务器
        if self._node_id and self._allowed_dirs:
            file_server = create_file_read_server(
                allowed_dirs=self._allowed_dirs,
                node_id=self._node_id
            )
            server_name = f"docuswarm-files-{self._node_id}"
            options_dict["mcp_servers"] = {server_name: file_server}
            options_dict["allowed_tools"] = [
                "Read",
                "Glob",
                f"mcp__{server_name}__read_document",
                f"mcp__{server_name}__list_documents",
            ]
        
        return ClaudeAgentOptions(**options_dict)
```

---

## 4. 搜索工具集成方案

### 4.1 Claude Agent SDK 内置搜索工具 API 规范

Claude Code 内置工具 `Grep` 和 `Glob` 支持文件搜索：

```python
# 内置搜索工具使用
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"],
    cwd="/project/docs"    # 限制工作目录为搜索根目录
)
```

工具调用示例（Claude 内部调用格式）：
```json
{
  "tool": "Grep",
  "input": {
    "pattern": "authentication",
    "path": "docs/",
    "include": "*.md",
    "case_sensitive": false
  }
}
```

### 4.2 自定义搜索工具（按节点限定范围）

```python
# autoBMAD/docuswarm/tools/search_tools.py

from claude_agent_sdk import tool, create_sdk_mcp_server
from pathlib import Path
from typing import Any
import re
import fnmatch

def create_search_server(search_dirs: list[str], node_id: str):
    """创建节点专属搜索 MCP 服务器。
    
    Args:
        search_dirs: 允许搜索的目录列表
        node_id: 节点标识
    """
    
    @tool(
        "grep_search",
        "在允许的目录内搜索包含指定模式的文件内容",
        {
            "pattern": str,
            "directory": str,
            "file_pattern": str,
            "case_sensitive": bool,
            "max_results": int,
        }
    )
    async def grep_search(args: dict[str, Any]) -> dict[str, Any]:
        pattern = args["pattern"]
        directory = args.get("directory", search_dirs[0] if search_dirs else ".")
        file_pattern = args.get("file_pattern", "*.md")
        case_sensitive = args.get("case_sensitive", False)
        max_results = args.get("max_results", 20)
        
        # 权限检查
        abs_dir = os.path.abspath(directory)
        is_allowed = any(
            abs_dir.startswith(os.path.abspath(d))
            for d in search_dirs
        )
        if not is_allowed:
            return {
                "content": [{"type": "text", "text": f"权限拒绝：'{directory}' 不在允许的搜索目录内"}]
            }
        
        # 执行搜索
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            compiled = re.compile(pattern, flags)
        except re.error as e:
            return {
                "content": [{"type": "text", "text": f"无效的正则表达式：{e}"}]
            }
        
        base = Path(abs_dir)
        for file_path in base.rglob(file_pattern):
            if not file_path.is_file():
                continue
            try:
                lines = file_path.read_text(encoding="utf-8").splitlines()
                for line_no, line in enumerate(lines, 1):
                    if compiled.search(line):
                        results.append(
                            f"{file_path.relative_to(base)}:{line_no}: {line.strip()}"
                        )
                        if len(results) >= max_results:
                            break
            except Exception:
                continue
            if len(results) >= max_results:
                break
        
        if not results:
            return {"content": [{"type": "text", "text": f"未找到匹配 '{pattern}' 的内容"}]}
        
        output = "\n".join(results)
        return {
            "content": [{
                "type": "text",
                "text": f"搜索结果（共 {len(results)} 条）：\n\n{output}"
            }]
        }
    
    @tool(
        "glob_search",
        "在允许目录内通过 glob 模式查找文件",
        {
            "pattern": str,
            "directory": str,
        }
    )
    async def glob_search(args: dict[str, Any]) -> dict[str, Any]:
        pattern = args["pattern"]
        directory = args.get("directory", search_dirs[0] if search_dirs else ".")
        
        abs_dir = os.path.abspath(directory)
        is_allowed = any(
            abs_dir.startswith(os.path.abspath(d))
            for d in search_dirs
        )
        if not is_allowed:
            return {
                "content": [{"type": "text", "text": f"权限拒绝：'{directory}' 不在允许的搜索目录内"}]
            }
        
        base = Path(abs_dir)
        matches = [str(p.relative_to(base)) for p in base.glob(pattern) if p.is_file()]
        
        if not matches:
            return {"content": [{"type": "text", "text": f"未找到匹配 '{pattern}' 的文件"}]}
        
        return {
            "content": [{
                "type": "text",
                "text": f"匹配文件（{len(matches)} 个）：\n" + "\n".join(matches)
            }]
        }

    return create_sdk_mcp_server(
        name=f"docuswarm-search-{node_id}",
        version="1.0.0",
        tools=[grep_search, glob_search]
    )
```

### 4.3 节点搜索范围配置

| 节点 | 搜索目录 | 典型搜索场景 |
|------|----------|-------------|
| `analyst` | `docs/`, `docs/research/` | 搜索已有研究报告和需求文档 |
| `pm` | `docs/analyst/`, `docs/plan/` | 查找分析师输出，避免重复工作 |
| `ux` | `docs/analyst/`, `docs/plan/` | 了解用户需求和产品目标 |
| `architect` | `docs/` (全范围) | 搜索 PRD、UX 设计、技术约束 |
| `po` | `docs/` (全范围), `docs/epics/` | 搜索所有输出，生成 epics/stories |

### 4.4 搜索工具与文件工具联合注册

```python
# session_manager.py 完整工具注册方案

def _create_options_with_tools(
    self,
    mode: str = "agent",
    yolo: bool = True,
    project_root: Path | None = None,
) -> ClaudeAgentOptions:
    """创建包含文件读取和搜索工具的 ClaudeAgentOptions。"""
    
    base_options = {
        "cwd": self._work_dir,
        "model": os.environ.get("CLAUDE_MODEL_NAME", "claude-3-opus-20240229"),
        "permission_mode": "bypassPermissions" if yolo else "default",
    }
    
    if not self._node_id or not project_root:
        return ClaudeAgentOptions(**base_options)
    
    # 获取节点工具权限配置
    node_config = NODE_TOOL_PERMISSIONS.get(self._node_id, {})
    allowed_dirs = [
        str(project_root / d)
        for d in node_config.get("allowed_read_dirs", [])
    ]
    search_dirs = [
        str(project_root / d)
        for d in node_config.get("search_dirs", [])
    ]
    
    # 创建 MCP 服务器
    mcp_servers = {}
    allowed_tools = ["Read", "Glob"]
    
    if allowed_dirs:
        file_server = create_file_read_server(allowed_dirs, self._node_id)
        file_server_name = f"docuswarm-files-{self._node_id}"
        mcp_servers[file_server_name] = file_server
        allowed_tools += [
            f"mcp__{file_server_name}__read_document",
            f"mcp__{file_server_name}__list_documents",
        ]
    
    if search_dirs:
        search_server = create_search_server(search_dirs, self._node_id)
        search_server_name = f"docuswarm-search-{self._node_id}"
        mcp_servers[search_server_name] = search_server
        allowed_tools += [
            f"mcp__{search_server_name}__grep_search",
            f"mcp__{search_server_name}__glob_search",
        ]
    
    return ClaudeAgentOptions(
        **base_options,
        mcp_servers=mcp_servers,
        allowed_tools=allowed_tools,
    )
```

---

## 5. BMAD 斜杠命令注入方案

### 5.1 可用斜杠命令清单

基于审计结果，项目共有 **47 个斜杠命令**（全部位于 `.claude/skills/`）：

#### BMAD 工作流命令（33 个）

| 命令 | 技能文件 | 功能描述 |
|------|----------|----------|
| `/bmad-advanced-elicitation` | `SKILL.md` | 高级需求引导，通过追问挖掘深层需求 |
| `/bmad-brainstorming` | `SKILL.md` | 结构化头脑风暴，生成创意候选方案 |
| `/bmad-check-implementation-readiness` | `SKILL.md` | 检查实现就绪度，验证开发准备状态 |
| `/bmad-code-review` | `SKILL.md` | 代码审查，评估质量、安全性和规范性 |
| `/bmad-correct-course` | `checklist.md` | 纠偏清单，检测并修正偏离路径的工作 |
| `/bmad-create-architecture` | `architecture-decision-template.md` | 创建系统架构文档 |
| `/bmad-create-epics-and-stories` | `SKILL.md` | 生成 epics 和 user stories |
| `/bmad-create-prd` | `SKILL.md` | 创建产品需求文档 |
| `/bmad-create-story` | `checklist.md` | 创建单个 user story |
| `/bmad-create-ux-design` | `SKILL.md` | 创建 UX 设计文档 |
| `/bmad-dev-story` | `checklist.md` | 开发故事 DoD 检查清单 |
| `/bmad-distillator` | `SKILL.md` | 文档蒸馏器，提取关键信息 |
| `/bmad-document-project` | `checklist.md` | 项目文档化完整流程 |
| `/bmad-domain-research` | `research.template.md` | 领域研究，输出结构化研究报告 |
| `/bmad-edit-prd` | `SKILL.md` | 编辑已有 PRD |
| `/bmad-editorial-review-prose` | `SKILL.md` | 文稿散文质量审查 |
| `/bmad-editorial-review-structure` | `SKILL.md` | 文档结构质量审查 |
| `/bmad-generate-project-context` | `project-context-template.md` | 生成项目上下文文档 |
| `/bmad-help` | `SKILL.md` | 显示 BMAD 方法论帮助 |
| `/bmad-index-docs` | `SKILL.md` | 文档索引生成 |
| `/bmad-init` | `SKILL.md` | BMAD 项目初始化 |
| `/bmad-market-research` | `research.template.md` | 市场研究，输出市场分析报告 |
| `/bmad-party-mode` | `SKILL.md` | Party 模式（多 Agent 协作） |
| `/bmad-product-brief` | `SKILL.md` | 产品简报生成 |
| `/bmad-qa-generate-e2e-tests` | `checklist.md` | 生成 E2E 测试用例 |
| `/bmad-quick-dev` | `SKILL.md` | 快速开发模式 |
| `/bmad-retrospective` | `SKILL.md` | 回顾会议，总结经验教训 |
| `/bmad-review-adversarial-general` | `SKILL.md` | 对抗性通用审查，从批评者角度审查文档 |
| `/bmad-review-edge-case-hunter` | `SKILL.md` | 边界案例猎手，发现遗漏场景 |
| `/bmad-shard-doc` | `SKILL.md` | 文档分片，大文档拆分 |
| `/bmad-sprint-planning` | `checklist.md` | Sprint 规划 |
| `/bmad-sprint-status` | `SKILL.md` | Sprint 状态报告 |
| `/bmad-technical-research` | `research.template.md` | 技术研究，输出技术评估报告 |
| `/bmad-validate-prd` | `SKILL.md` | PRD 验证和质量检查 |

#### BMAD Agent 命令（9 个）

| 命令 | 功能描述 |
|------|----------|
| `/bmad-agent-analyst` | 激活 Analyst Agent 角色模式 |
| `/bmad-agent-architect` | 激活 Architect Agent 角色模式 |
| `/bmad-agent-dev` | 激活 Dev Agent 角色模式 |
| `/bmad-agent-pm` | 激活 PM Agent 角色模式 |
| `/bmad-agent-qa` | 激活 QA Agent 角色模式 |
| `/bmad-agent-quick-flow-solo-dev` | 激活快速流程独立开发 Agent |
| `/bmad-agent-sm` | 激活 Scrum Master Agent |
| `/bmad-agent-tech-writer` | 激活技术写作 Agent |
| `/bmad-agent-ux-designer` | 激活 UX Designer Agent |

#### 项目专属命令（2 个）

| 命令 | 功能描述 |
|------|----------|
| `/autoBMAD-epic-automation` | autoBMAD Epic 自动化流程 |
| `/claude-plan` | Claude 计划模式 |

### 5.2 节点-命令映射表

根据各节点的 `persona.json` 和 `node.yaml` 定义的职责，设计以下命令映射：

#### analyst 节点（sequence: 1）

**职责**：数据分析、业务洞察、需求调研  
**依赖**：无（管道起点）

| 命令 | 用途 | 注入方式 | 优先级 |
|------|------|----------|--------|
| `/bmad-agent-analyst` | 强化分析师角色意识 | system_prompt append | P0 |
| `/bmad-domain-research` | 领域研究任务执行 | user_prompt 提示 | P0 |
| `/bmad-market-research` | 市场研究任务执行 | user_prompt 提示 | P1 |
| `/bmad-advanced-elicitation` | 需求引导时的追问策略 | system_prompt append | P1 |
| `/bmad-brainstorming` | 探索阶段的创意生成 | user_prompt 提示 | P2 |
| `/bmad-distillator` | 压缩大量上下文信息 | user_prompt 提示 | P2 |

**理由**：Analyst 是管道首节点，主要职责是调研和分析，需要 domain/market research 技能以结构化输出研究报告，以及 advanced-elicitation 以挖掘深层需求。

#### pm 节点（sequence: 2）

**职责**：产品需求管理、PRD 编写、里程碑规划  
**依赖**：analyst

| 命令 | 用途 | 注入方式 | 优先级 |
|------|------|----------|--------|
| `/bmad-agent-pm` | 强化 PM 角色意识 | system_prompt append | P0 |
| `/bmad-create-prd` | 创建 PRD 的完整流程 | user_prompt 提示 | P0 |
| `/bmad-create-epics-and-stories` | 从 PRD 生成 epics | user_prompt 提示 | P0 |
| `/bmad-validate-prd` | 自我验证 PRD 质量 | system_prompt append | P1 |
| `/bmad-edit-prd` | 迭代修改 PRD | user_prompt 提示 | P1 |
| `/bmad-sprint-planning` | 规划 Sprint 时间线 | user_prompt 提示 | P2 |

**理由**：PM 节点核心产出是 PRD，需要 create-prd 和 validate-prd 技能形成自我检验闭环，以及 create-epics-and-stories 将需求分解为可执行单元。

#### ux 节点（sequence: 3）

**职责**：用户体验设计、用户画像、交互流程  
**依赖**：analyst, pm

| 命令 | 用途 | 注入方式 | 优先级 |
|------|------|----------|--------|
| `/bmad-agent-ux-designer` | 强化 UX 设计师角色 | system_prompt append | P0 |
| `/bmad-create-ux-design` | 创建 UX 设计文档 | user_prompt 提示 | P0 |
| `/bmad-advanced-elicitation` | 用户需求引导 | system_prompt append | P1 |
| `/bmad-editorial-review-prose` | 用户旅程描述质量检查 | user_prompt 提示 | P2 |
| `/bmad-review-edge-case-hunter` | 发现遗漏的用户场景 | user_prompt 提示 | P2 |

**理由**：UX 节点需要 create-ux-design 技能生成标准化 UX 文档（含 personas、flows、wireframes），review-edge-case-hunter 确保不遗漏特殊用户场景。

#### architect 节点（sequence: 4）

**职责**：系统架构设计、技术选型、API 设计  
**依赖**：analyst, pm, ux

| 命令 | 用途 | 注入方式 | 优先级 |
|------|------|----------|--------|
| `/bmad-agent-architect` | 强化架构师角色意识 | system_prompt append | P0 |
| `/bmad-create-architecture` | 创建架构决策文档 | user_prompt 提示 | P0 |
| `/bmad-technical-research` | 技术选型研究 | user_prompt 提示 | P0 |
| `/bmad-review-adversarial-general` | 架构方案对抗性审查 | user_prompt 提示 | P1 |
| `/bmad-check-implementation-readiness` | 检查架构的实现就绪度 | user_prompt 提示 | P1 |
| `/bmad-review-edge-case-hunter` | 发现架构边界案例 | user_prompt 提示 | P2 |

**理由**：Architect 处于流程中后期，需要 technical-research 进行技术调研，create-architecture 生成决策文档，review-adversarial 确保方案经得起质疑。

#### po 节点（sequence: 5）

**职责**：产品 Backlog 管理、epics/stories 生成、发布规划  
**依赖**：analyst, pm, ux, architect（全部上游）

| 命令 | 用途 | 注入方式 | 优先级 |
|------|------|----------|--------|
| `/bmad-create-epics-and-stories` | 生成完整 epic 和 story 列表 | user_prompt 提示 | P0 |
| `/bmad-validate-prd` | 验证所有需求已被覆盖 | system_prompt append | P0 |
| `/bmad-check-implementation-readiness` | 验证开发就绪度 | user_prompt 提示 | P0 |
| `/bmad-sprint-planning` | 制定 Sprint 计划 | user_prompt 提示 | P1 |
| `/bmad-sprint-status` | 生成 Sprint 状态报告 | user_prompt 提示 | P2 |
| `/bmad-distillator` | 压缩所有上游输出为执行摘要 | user_prompt 提示 | P1 |

**理由**：PO 是流程终点，需要整合所有上游输出（5 个节点），create-epics-and-stories 是核心产出，validate-prd 和 check-implementation-readiness 确保产出可执行。

### 5.3 提示词注入实现

#### 5.3.1 提示词模板设计（System Prompt 结构）

斜杠命令以 `system_prompt` 的 `append` 部分注入，形成如下四层结构：

```
┌─────────────────────────────────────────────────────────────┐
│                    System Prompt 四层结构                    │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Preset（claude_code 工具说明）                      │
│   来源：ClaudeAgentOptions(system_prompt={"preset":"claude_code"})│
│   内容：工具使用说明、安全指令、代码风格规范                   │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Persona（角色身份定义）                             │
│   来源：nodes/{node_id}/persona.json                        │
│   内容：name, role, identity, expertise, principles          │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Task Context（任务上下文）                          │
│   来源：node.yaml + NodeExecutionContext                    │
│   内容：task_name, deliverable_requirements, dependencies   │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Skill Injection（技能注入）                        │
│   来源：.claude/skills/{command}/SKILL.md                   │
│   内容：BMAD 斜杠命令描述 + 使用方式                         │
└─────────────────────────────────────────────────────────────┘
```

#### 5.3.2 斜杠命令 System Prompt 注入实现

```python
# autoBMAD/docuswarm/prompts/skill_injector.py

from pathlib import Path
from typing import Any

# 节点-命令映射表（P0 命令）
NODE_SKILL_MAP: dict[str, list[str]] = {
    "analyst": [
        "bmad-agent-analyst",
        "bmad-domain-research",
        "bmad-market-research",
        "bmad-advanced-elicitation",
    ],
    "pm": [
        "bmad-agent-pm",
        "bmad-create-prd",
        "bmad-create-epics-and-stories",
        "bmad-validate-prd",
    ],
    "ux": [
        "bmad-agent-ux-designer",
        "bmad-create-ux-design",
        "bmad-advanced-elicitation",
        "bmad-review-edge-case-hunter",
    ],
    "architect": [
        "bmad-agent-architect",
        "bmad-create-architecture",
        "bmad-technical-research",
        "bmad-review-adversarial-general",
        "bmad-check-implementation-readiness",
    ],
    "po": [
        "bmad-create-epics-and-stories",
        "bmad-validate-prd",
        "bmad-check-implementation-readiness",
        "bmad-sprint-planning",
        "bmad-distillator",
    ],
}


class SkillInjector:
    """BMAD 技能注入器。
    
    负责从 .claude/skills/ 目录读取技能定义，
    并生成可注入 system_prompt 的技能描述文本。
    """
    
    def __init__(self, project_root: Path) -> None:
        self._skills_dir = project_root / ".claude" / "skills"
        self._skill_cache: dict[str, str] = {}
    
    def _load_skill_description(self, skill_name: str) -> str:
        """加载技能描述。优先读取 SKILL.md，fallback 到第一个 .md 文件。"""
        if skill_name in self._skill_cache:
            return self._skill_cache[skill_name]
        
        skill_dir = self._skills_dir / skill_name
        if not skill_dir.exists():
            return f"/{skill_name}: BMAD 技能（文件未找到）"
        
        # 优先读取 SKILL.md
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            # 查找第一个 .md 文件
            md_files = list(skill_dir.glob("*.md"))
            if md_files:
                skill_file = md_files[0]
            else:
                return f"/{skill_name}: BMAD 技能"
        
        content = skill_file.read_text(encoding="utf-8")
        
        # 提取前 300 字符作为描述（避免 token 过多）
        description = content[:300].strip()
        if len(content) > 300:
            description += "..."
        
        self._skill_cache[skill_name] = description
        return description
    
    def build_skill_section(self, node_id: str) -> str:
        """为指定节点构建技能注入文本。
        
        Args:
            node_id: 节点 ID（analyst/pm/ux/architect/po）
        
        Returns:
            格式化的技能说明文本，用于注入 system_prompt
        """
        skill_names = NODE_SKILL_MAP.get(node_id, [])
        if not skill_names:
            return ""
        
        lines = [
            "\n## 可用 BMAD 技能",
            "",
            "你可以在执行任务时参考以下 BMAD 方法论技能，",
            "这些技能定义了标准化的工作流程和输出格式：",
            "",
        ]
        
        for skill_name in skill_names:
            command = f"/{skill_name}"
            description = self._load_skill_description(skill_name)
            # 提取 name 行（SKILL.md 格式：name: xxx）
            skill_label = skill_name.replace("-", " ").title()
            lines.append(f"### {command}")
            lines.append(f"**用途**: {skill_label}")
            # 提取首行描述
            first_meaningful_line = next(
                (ln.strip() for ln in description.splitlines() if ln.strip()),
                description[:100]
            )
            lines.append(f"**说明**: {first_meaningful_line}")
            lines.append("")
        
        lines.append(
            "**使用方式**: 在你的分析和输出中，引用相关技能的思路和框架，"
            "按照该技能定义的标准格式组织你的输出。"
        )
        
        return "\n".join(lines)
    
    def build_system_prompt_append(
        self,
        node_id: str,
        persona_prompt: str,
        task_context: str = "",
    ) -> str:
        """构建完整的 system_prompt append 内容。
        
        Args:
            node_id: 节点 ID
            persona_prompt: 格式化的 persona 提示词
            task_context: 任务上下文（可选）
        
        Returns:
            用于 ClaudeAgentOptions.system_prompt.append 的字符串
        """
        sections = []
        
        # Layer 2: Persona
        if persona_prompt:
            sections.append(persona_prompt)
        
        # Layer 3: Task Context
        if task_context:
            sections.append(f"\n## 当前任务上下文\n\n{task_context}")
        
        # Layer 4: Skill Injection
        skill_section = self.build_skill_section(node_id)
        if skill_section:
            sections.append(skill_section)
        
        return "\n\n".join(sections)
```

#### 5.3.3 集成到 IndependentAgent

```python
# agents/independent.py 改造版本 - _call_llm_with_prompts 方法

from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector

async def _call_llm_with_prompts(
    self,
    system_prompt: str,
    user_prompt: str,
) -> list[dict[str, Any]]:
    """Call LLM with pre-built system and user prompts (改造版本).
    
    变更：
    1. system_prompt 通过 ClaudeAgentOptions.system_prompt 传递（非拼接）
    2. 注入 BMAD 技能描述到 system_prompt append
    3. 启用 claude_code preset 以获取完整工具说明
    """
    sm = self.session_manager
    assert sm is not None
    
    # 构建技能注入器
    skill_injector = SkillInjector(project_root=self.project_root)
    
    # 构建完整 system_prompt append（persona + task + skills）
    skill_section = skill_injector.build_skill_section(self.node_id)
    full_append = f"{system_prompt}\n\n{skill_section}"
    
    # 构建 ClaudeAgentOptions with system_prompt
    from claude_agent_sdk.types import ClaudeAgentOptions
    
    options = ClaudeAgentOptions(
        cwd=self._work_dir or sm.work_dir,
        model=os.environ.get("CLAUDE_MODEL_NAME", "claude-3-opus-20240229"),
        permission_mode="bypassPermissions",
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": full_append,  # persona + task_context + skills
        },
        allowed_tools=["Read", "Glob", "Write"],
    )
    
    # 直接使用 query() API
    from claude_agent_sdk import query
    
    messages: list[dict[str, Any]] = []
    async for msg in query(prompt=user_prompt, options=options):
        msg_dict = sm._message_to_dict(msg)
        if msg_dict:
            messages.append(msg_dict)
    
    return messages
```

---

## 6. 节点级工具权限配置方案

### 6.1 node.yaml Schema 扩展设计

在现有 `node.yaml` schema 中新增 `tools` 配置块：

```yaml
# 扩展后的 node.yaml schema 示例（analyst 节点）
node_id: analyst
name: Analyst
description: Data Analyst & Business Intelligence Specialist
sequence: 1
deliverable_type: analyst-report
deliverable:
  required_sections:
    - executive_summary
    - data_sources
    - analysis_methodology
    - findings
    - recommendations
    - limitations

# 新增：工具权限配置
tools:
  # 允许的内置工具（Claude Code 工具集）
  allowed_builtin_tools:
    - Read
    - Glob
  
  # 文件读取权限（相对于 project_root）
  file_permissions:
    allowed_read_dirs:
      - docs/
      - docs/research/
    denied_read_dirs:
      - autoBMAD/
      - .env
      - "*.db"
  
  # 搜索权限
  search_permissions:
    search_dirs:
      - docs/
      - docs/research/
    max_results: 30
  
  # BMAD 技能注入
  skills:
    inject_mode: "system_prompt_append"  # system_prompt_append | user_prompt | disabled
    commands:
      - bmad-agent-analyst
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
    priority_commands:  # 在 user_prompt 中额外提示的命令
      - bmad-domain-research

agent:
  type: independent
  model: sonnet
  temperature: 0.7

questions:
  - id: q1
    text: "What is the business context and objectives for this analysis?"
    required: true
```

### 6.2 NodeConfig Dataclass 扩展

```python
# autoBMAD/docuswarm/nodes/loader.py 扩展

from dataclasses import dataclass, field
from typing import Any

@dataclass
class NodeToolPermissions:
    """节点工具权限配置。"""
    allowed_builtin_tools: list[str] = field(default_factory=lambda: ["Read", "Glob"])
    allowed_read_dirs: list[str] = field(default_factory=list)
    denied_read_dirs: list[str] = field(default_factory=list)
    search_dirs: list[str] = field(default_factory=list)
    max_search_results: int = 20
    skill_inject_mode: str = "system_prompt_append"  # "system_prompt_append" | "disabled"
    skill_commands: list[str] = field(default_factory=list)


@dataclass
class NodeConfig:
    """节点配置（扩展版）。"""
    node_id: str
    name: str
    description: str
    sequence: int
    deliverable_type: str
    deliverable: dict[str, Any] = field(default_factory=dict)
    agent: dict[str, Any] = field(default_factory=dict)
    questions: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    task: dict[str, Any] = field(default_factory=dict)
    # 新增：工具权限
    tool_permissions: NodeToolPermissions = field(default_factory=NodeToolPermissions)


class NodeLoader:
    """节点配置加载器（扩展版）。"""
    
    @staticmethod
    def load(node_id: str, project_root: Path) -> NodeConfig:
        """加载节点配置，包含工具权限解析。"""
        node_dir = project_root / "nodes" / node_id
        config_file = node_dir / "node.yaml"
        
        with open(config_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # 解析工具权限
        tools_data = data.get("tools", {})
        tool_permissions = NodeToolPermissions(
            allowed_builtin_tools=tools_data.get("allowed_builtin_tools", ["Read", "Glob"]),
            allowed_read_dirs=tools_data.get("file_permissions", {}).get("allowed_read_dirs", []),
            denied_read_dirs=tools_data.get("file_permissions", {}).get("denied_read_dirs", []),
            search_dirs=tools_data.get("search_permissions", {}).get("search_dirs", []),
            max_search_results=tools_data.get("search_permissions", {}).get("max_results", 20),
            skill_inject_mode=tools_data.get("skills", {}).get("inject_mode", "system_prompt_append"),
            skill_commands=tools_data.get("skills", {}).get("commands", []),
        )
        
        return NodeConfig(
            node_id=data["node_id"],
            name=data["name"],
            description=data.get("description", ""),
            sequence=data.get("sequence", 0),
            deliverable_type=data.get("deliverable_type", ""),
            deliverable=data.get("deliverable", {}),
            agent=data.get("agent", {}),
            questions=data.get("questions", []),
            dependencies=data.get("dependencies", []),
            task=data.get("task", {}),
            tool_permissions=tool_permissions,
        )
```

### 6.3 每个节点的默认工具权限建议

| 节点 | 内置工具 | 文件读取目录 | 搜索目录 | 技能命令数 |
|------|----------|-------------|----------|-----------|
| `analyst` | Read, Glob | docs/, docs/research/ | docs/, docs/research/ | 4 |
| `pm` | Read, Glob, Write | docs/, docs/analyst/ | docs/analyst/, docs/plan/ | 4 |
| `ux` | Read, Glob, Write | docs/, docs/analyst/, docs/plan/ | docs/analyst/, docs/plan/ | 4 |
| `architect` | Read, Glob, Write | docs/ (全部) | docs/ (全部) | 5 |
| `po` | Read, Glob, Write | docs/ (全部) | docs/ (全部), docs/epics/ | 5 |

### 6.4 运行时工具过滤逻辑

```python
# autoBMAD/docuswarm/llm/tool_filter.py

from pathlib import Path
from autoBMAD.docuswarm.nodes.loader import NodeConfig, NodeToolPermissions

class NodeToolFilter:
    """节点运行时工具过滤器。"""
    
    def __init__(self, node_config: NodeConfig, project_root: Path) -> None:
        self._config = node_config
        self._project_root = project_root
        self._permissions = node_config.tool_permissions
    
    def build_mcp_servers(self) -> dict:
        """构建节点专属 MCP 服务器配置。"""
        from autoBMAD.docuswarm.tools.file_tools import create_file_read_server
        from autoBMAD.docuswarm.tools.search_tools import create_search_server
        
        node_id = self._config.node_id
        mcp_servers = {}
        
        # 文件读取服务器
        if self._permissions.allowed_read_dirs:
            abs_dirs = [
                str(self._project_root / d)
                for d in self._permissions.allowed_read_dirs
            ]
            file_server = create_file_read_server(abs_dirs, node_id)
            mcp_servers[f"docuswarm-files-{node_id}"] = file_server
        
        # 搜索服务器
        if self._permissions.search_dirs:
            abs_dirs = [
                str(self._project_root / d)
                for d in self._permissions.search_dirs
            ]
            search_server = create_search_server(abs_dirs, node_id)
            mcp_servers[f"docuswarm-search-{node_id}"] = search_server
        
        return mcp_servers
    
    def build_allowed_tools(self) -> list[str]:
        """构建允许工具列表。"""
        node_id = self._config.node_id
        tools = list(self._permissions.allowed_builtin_tools)
        
        if self._permissions.allowed_read_dirs:
            server_name = f"docuswarm-files-{node_id}"
            tools += [
                f"mcp__{server_name}__read_document",
                f"mcp__{server_name}__list_documents",
            ]
        
        if self._permissions.search_dirs:
            server_name = f"docuswarm-search-{node_id}"
            tools += [
                f"mcp__{server_name}__grep_search",
                f"mcp__{server_name}__glob_search",
            ]
        
        return tools
    
    def should_inject_skills(self) -> bool:
        """检查是否应该注入技能。"""
        return self._permissions.skill_inject_mode == "system_prompt_append"
    
    def get_skill_commands(self) -> list[str]:
        """获取节点的技能命令列表。"""
        return self._permissions.skill_commands
```

---

## 7. 提示词结构优化设计

### 7.1 当前提示词结构分析

**现有问题**（基于 `agents/independent.py:284` 分析）：

```python
# 当前实现 - 扁平拼接（问题所在）
full_prompt = f"{system_prompt}\n\n{user_prompt}"
messages = await sm.single_prompt(full_prompt)
```

**问题列表**：

| 问题 | 影响 | 严重程度 |
|------|------|----------|
| system_prompt 混入 user_prompt | Claude 无法区分身份指令和任务 | 高 |
| 未使用 `claude_code` preset | 工具使用说明缺失 | 中 |
| 无法动态追加技能说明 | BMAD 技能未激活 | 高 |
| persona 格式为纯文本拼接 | 缺乏结构层次 | 中 |
| 无 `setting_sources` | CLAUDE.md 未读取 | 低 |

### 7.2 优化后的提示词架构

```
┌───────────────────────────────────────────────────────────────────┐
│               优化后 ClaudeAgentOptions 结构                       │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  system_prompt: {                                                 │
│    "type": "preset",                                              │
│    "preset": "claude_code",     ← 工具说明 + 安全指令              │
│    "append": """                                                  │
│      [Layer 2] PERSONA SECTION                                    │
│      # 角色定义                                                    │
│      你的名字是 {name}，你是 {role}                                │
│      {identity}                                                   │
│      ## 专业领域                                                   │
│      - {expertise[0]}                                             │
│      ## 行为准则                                                   │
│      - {principles[0]}                                            │
│                                                                   │
│      [Layer 3] TASK CONTEXT SECTION                               │
│      ## 当前节点任务                                               │
│      任务名称: {task_name}                                        │
│      任务描述: {task_description}                                 │
│      交付物要求: {deliverable_requirements}                        │
│                                                                   │
│      [Layer 4] SKILL INJECTION SECTION                            │
│      ## 可用 BMAD 技能                                            │
│      /bmad-agent-analyst: 激活分析师角色...                        │
│      /bmad-domain-research: 领域研究流程...                       │
│      ...                                                          │
│    """                                                            │
│  }                                                                │
│                                                                   │
│  allowed_tools: ["Read", "Glob", "mcp__files__read_document", ...]│
│  mcp_servers: { "docuswarm-files-analyst": ..., ... }            │
│  permission_mode: "bypassPermissions"                             │
│  cwd: output_dir                                                  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│               User Prompt（纯任务内容）                            │
├───────────────────────────────────────────────────────────────────┤
│  {task_description}                                               │
│                                                                   │
│  ## 原始上下文                                                     │
│  {original_context}                                               │
│                                                                   │
│  ## 上游交付物摘要                                                 │
│  - analyst: {analyst_deliverable_summary}                         │
│                                                                   │
│  ## 迭代反馈（若有）                                               │
│  {iteration_feedback}                                             │
└───────────────────────────────────────────────────────────────────┘
```

### 7.3 提示词模板引擎设计

```python
# autoBMAD/docuswarm/prompts/template_engine.py

from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class PromptBuildConfig:
    """提示词构建配置。"""
    node_id: str
    persona_data: dict[str, Any]           # 来自 persona.json
    task_name: str                          # 来自 node.yaml task.name
    task_description: str                   # 来自 node.yaml description
    deliverable_requirements: dict[str, Any] # 来自 node.yaml deliverable
    original_context: str                   # 来自 pipeline context
    chained_deliverables: list[dict[str, Any]] = None  # 上游输出摘要
    iteration_feedback: dict[str, Any] | None = None   # 迭代反馈
    inject_skills: bool = True              # 是否注入技能
    skill_commands: list[str] | None = None # 技能命令列表


class PromptTemplateEngine:
    """提示词模板引擎。
    
    负责将 persona、task context、skills 组装为结构化提示词。
    """
    
    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root
        from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector
        self._skill_injector = SkillInjector(project_root)
    
    def build_system_prompt_append(self, config: PromptBuildConfig) -> str:
        """构建 system_prompt 的 append 部分（Layer 2 + 3 + 4）。"""
        sections = []
        
        # Layer 2: Persona
        persona = config.persona_data
        persona_section = f"""# 角色定义

你的名字是 **{persona.get('name', '')}**，你是 **{persona.get('role', '')}**。

{persona.get('identity', '')}

## 专业领域
{self._format_list(persona.get('expertise', []))}

## 行为准则
{self._format_list(persona.get('principles', []))}"""
        sections.append(persona_section)
        
        # Layer 3: Task Context
        task_section = f"""## 当前节点任务

**任务名称**: {config.task_name}  
**任务描述**: {config.task_description}

### 交付物要求

你需要生成一份 `{config.node_id}-report` 格式的文档，必须包含以下章节：
{self._format_sections(config.deliverable_requirements.get('required_sections', []))}"""
        sections.append(task_section)
        
        # Layer 4: Skill Injection（可选）
        if config.inject_skills:
            skill_commands = config.skill_commands or []
            if skill_commands:
                skill_section = self._skill_injector.build_skill_section_from_commands(
                    skill_commands
                )
                if skill_section:
                    sections.append(skill_section)
        
        return "\n\n---\n\n".join(sections)
    
    def build_user_prompt(self, config: PromptBuildConfig) -> str:
        """构建 user_prompt（纯任务内容）。"""
        sections = []
        
        # 任务描述
        sections.append(f"# 任务：{config.task_name}\n\n{config.task_description}")
        
        # 原始上下文
        if config.original_context:
            sections.append(f"## 原始项目上下文\n\n{config.original_context}")
        
        # 上游交付物
        if config.chained_deliverables:
            upstream_lines = ["## 上游节点交付物摘要\n"]
            for item in config.chained_deliverables:
                upstream_lines.append(
                    f"- **{item.get('node_id', 'unknown')}**: {item.get('title', '')}"
                )
                if item.get('summary'):
                    upstream_lines.append(f"  摘要: {item['summary'][:200]}")
            sections.append("\n".join(upstream_lines))
        
        # 迭代反馈
        if config.iteration_feedback:
            feedback_lines = ["## 迭代反馈（来自 Evaluator）\n"]
            feedback_lines.append(f"上一轮对齐分数: {config.iteration_feedback.get('alignment_score', 0)}/10")
            for issue in config.iteration_feedback.get("issues_found", []):
                feedback_lines.append(f"- 需要改进: {issue}")
            sections.append("\n".join(feedback_lines))
        
        # 输出格式提醒
        sections.append("""## 输出格式要求

使用 `create_deliverable` 工具保存你的文档，然后返回如下 JSON：
```json
{
  "deliverable": {"title": "...", "content": "摘要（非全文）", "file_path": "工具返回的路径", "sha256": "..."},
  "questions": [{"question": "?", "priority": "blocking|clarifying|optional", "context": "..."}],
  "action": "create_deliverable"
}
```""")
        
        return "\n\n".join(sections)
    
    def _format_list(self, items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)
    
    def _format_sections(self, sections: list[str]) -> str:
        return "\n".join(f"{i+1}. `{s}`" for i, s in enumerate(sections))
```

### 7.4 各层级优先级和覆盖规则

| 层级 | 内容 | 覆盖规则 | Token 预算 |
|------|------|----------|-----------|
| Layer 1 (preset) | claude_code 工具说明 | 不可覆盖（系统级） | ~2000 |
| Layer 2 (persona) | 角色身份、专业领域 | 可通过 node.yaml 定制 | ~500 |
| Layer 3 (task) | 任务描述、交付物要求 | 由 NodeExecutionContext 动态生成 | ~300 |
| Layer 4 (skills) | BMAD 命令描述 | 可通过 node.yaml.tools.skills 配置 | ~400 |
| User Prompt | 任务内容、上下文、反馈 | 完全动态 | ~5000 |

**总 System Prompt Token 预算**：约 3200 tokens（占 256K 总量的 1.25%）

---

## 8. 实施路线图

### Phase 1：基础工具注册（2-3天）

**目标**：让所有节点能够使用文件读取和搜索工具

**步骤**：

1. **创建工具模块**
   - `autoBMAD/docuswarm/tools/__init__.py`
   - `autoBMAD/docuswarm/tools/file_tools.py`（`create_file_read_server`）
   - `autoBMAD/docuswarm/tools/search_tools.py`（`create_search_server`）

2. **扩展 node.yaml schema**
   - 为 5 个节点添加 `tools` 配置块
   - 更新 `NodeConfig` dataclass 和 `NodeLoader`

3. **扩展 SessionManager**
   - 新增 `node_id` 和 `allowed_dirs` 参数
   - 更新 `_create_options` 以注册 MCP 服务器

4. **验证标准**：
   - `analyst` 节点能成功调用 `read_document("docs/PRD.md")`
   - `grep_search("authentication", "docs/")` 返回正确结果
   - 越权访问 `autoBMAD/` 时返回权限拒绝

**输入**: 当前 `session_manager.py`, `node.yaml` 文件  
**输出**: 工具模块、扩展的 `node.yaml`、更新的 `SessionManager`

---

### Phase 2：提示词架构重构（2-3天）

**目标**：将 system_prompt 从字符串拼接迁移为四层结构

**步骤**：

1. **创建提示词模块**
   - `autoBMAD/docuswarm/prompts/skill_injector.py`（`SkillInjector`）
   - `autoBMAD/docuswarm/prompts/template_engine.py`（`PromptTemplateEngine`）

2. **改造 IndependentAgent**
   - 修改 `_call_llm_with_prompts` 使用 `ClaudeAgentOptions.system_prompt`
   - 将 `full_prompt = system + user` 分离为独立传递

3. **改造 EvaluatorAgent**（评估者 Agent 独立处理）
   - 评估者仅注入 Evaluator 专用技能（`bmad-review-adversarial-general`）

4. **验证标准**：
   - `IndependentAgent._format_system_prompt()` 输出包含四层标记
   - Claude 响应中能正确引用 BMAD 技能框架
   - Persona 层不再出现在 user_prompt 中

**输入**: Phase 1 产出 + 当前 `independent.py`  
**输出**: 重构的提示词模块、更新的 `IndependentAgent`

---

### Phase 3：BMAD 技能注入（2天）

**目标**：将 BMAD 斜杠命令有效注入各节点 system_prompt

**步骤**：

1. **实现 SkillInjector**
   - 读取 `.claude/skills/` 目录
   - 提取命令描述（前 300 字符）
   - 按节点 `NODE_SKILL_MAP` 过滤

2. **更新 node.yaml**（5 个节点均添加 `tools.skills` 配置）

3. **集成到 PromptTemplateEngine**

4. **验证标准**：
   - `analyst` 节点 system_prompt 包含 `/bmad-domain-research` 说明
   - `pm` 节点 system_prompt 包含 `/bmad-create-prd` 说明
   - 技能注入不超过 400 tokens

**输入**: Phase 2 产出 + `.claude/skills/` 目录  
**输出**: 完整技能注入机制

---

### Phase 4：NodeToolFilter 集成（1天）

**目标**：统一工具权限管理，通过 `NodeToolFilter` 驱动所有工具配置

**步骤**：

1. 创建 `autoBMAD/docuswarm/llm/tool_filter.py`
2. 在 `IndependentAgent.execute()` 中初始化 `NodeToolFilter`
3. 将 MCP 服务器构建委托给 `NodeToolFilter`

**验证标准**：
- `NodeToolFilter.build_mcp_servers()` 返回正确的服务器配置
- 权限边界测试：po 节点可访问 docs/ 全部，analyst 不能访问 docs/stories/

---

### Phase 5：端到端测试（2天）

**目标**：验证完整流水线下的改造效果

**测试用例**：

| 测试场景 | 预期结果 | 验证方式 |
|----------|----------|----------|
| analyst 读取 PRD.md | 成功返回内容 | 单元测试 |
| pm 使用 grep_search 找到 analyst 输出 | 正确返回匹配行 | 单元测试 |
| architect 越权访问 .env | 返回权限拒绝 | 单元测试 |
| analyst system_prompt 含技能注入 | 包含 bmad-domain-research | 提示词验证 |
| 完整流水线运行 | 5 节点均完成，有工具调用日志 | 集成测试 |

---

## 9. 风险评估

### 9.1 Token 消耗增长

| 改造项 | Token 增量估算 | 缓解措施 |
|--------|---------------|----------|
| MCP 工具描述注入 | +500~1500 tokens/请求 | 使用 `ENABLE_TOOL_SEARCH=auto` 按需加载 |
| Skill Injection（每节点 4-5 个命令） | +300~500 tokens/请求 | 限制每个命令描述前 150 字符 |
| claude_code preset | +2000 tokens/会话 | 仅在 Layer 1 注入一次，不重复 |
| 文件读取结果（最大） | +10000 tokens（单文件） | 限制文件读取上限 5000 字符 |

**总计**：最坏情况每次节点执行增加约 14000 tokens（占 256K 总量的 5.5%）  
**Kimi K2.5 Token 费用影响**：在可接受范围内

### 9.2 提示词冲突

| 冲突类型 | 风险场景 | 缓解措施 |
|----------|----------|----------|
| Persona 与 claude_code preset 冲突 | Claude 角色混淆 | Persona 明确标注为 "DocuSwarm 节点角色" |
| 技能注入指令与任务指令重复 | 模型忽视技能说明 | 技能注入使用描述性语言，不使用命令格式 |
| 多节点技能重叠（如 advanced-elicitation） | 节点角色混乱 | 通过 `NODE_SKILL_MAP` 严格隔离 |
| 旧版提示词兼容性 | 改造后行为改变 | 保留 `_call_llm_via_session` 作为 fallback |

### 9.3 工具安全性

| 安全风险 | 风险等级 | 防护措施 |
|----------|----------|----------|
| 路径遍历攻击（`../`） | 高 | `os.path.abspath()` 规范化 + 白名单前缀匹配 |
| 读取敏感文件（`.env`, `*.db`） | 高 | 黑名单检查 + 默认拒绝不在白名单的路径 |
| 大文件读取导致 OOM | 中 | 文件大小限制（最大 1MB）、内容截断（5000字符） |
| 正则表达式 DoS（ReDoS） | 中 | 搜索超时限制（5秒）、结果数量上限 |
| MCP 服务器进程泄漏 | 低 | 在 `SessionManager.__aexit__` 中关闭 MCP 服务器 |

**核心安全原则**：
1. 默认拒绝（Deny by Default）：所有目录默认不可访问，白名单显式授权
2. 最小权限：各节点仅授权其任务所需目录
3. 路径规范化：所有路径在比较前先通过 `os.path.abspath()` 规范化
4. 内容大小限制：单文件读取最大 50000 字符，防止上下文溢出

---

## 参考资料

| 文档 | 路径 | 说明 |
|------|------|------|
| Claude Agent SDK Python 参考 | `autoBMAD/agentdocs/05_python.md` | ClaudeAgentOptions 完整字段 |
| 自定义工具指南 | `autoBMAD/agentdocs/19_custom_tools.md` | MCP 进程内服务器实现 |
| 斜杠命令文档 | `autoBMAD/agentdocs/21_slash_commands.md` | 自定义斜杠命令 |
| 系统提示修改指南 | `autoBMAD/agentdocs/17_modifying_system_prompts.md` | system_prompt append |
| MCP 工具集成 | `autoBMAD/agentdocs/18_mcp.md` | mcp_servers 配置 |
| 能力审计报告 | `.tmp/agent_sdk_audit.json` | 7/12 能力实现详情 |
| 架构分析报告 | `docs/evaluation/2026-03-26-docuswarm-deep-architecture-analysis.md` | 节点文档读取能力评估 |
| 实现差距分析 | `docs/evaluation/2026-03-26-docuswarm-implementation-gap-analysis.md` | EPIC-15 Context Resolver |

---

*报告生成时间：2026-03-26*  
*版本：v1.0.0*  
*下一文档：`06-context-resolver-implementation.md`（如有）*
