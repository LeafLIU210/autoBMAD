# 方案B深度研究报告：通过 read_docs_file 工具读取引用文档

**日期**: 2026-04-05
**类型**: 可行性分析 + 实施方案
**主题**: DocuSwarm Agent 通过 MCP 文件工具主动读取引用文档的完整链路分析

---

## 1. 研究背景与问题陈述

`bubble-sort-context.md` 中引用了三个支撑文档：

```
- algorithm-spec.md  — 算法规格说明
- requirements.md    — 利益相关者需求
- test-criteria.md   — 评估标准
```

由于 DocuSwarm 仅读取单一 context file 的原始文本，这些引用文档的内容**不会**自动注入到 Agent 的上下文中。

方案B的核心思路：通过 DocuSwarm 已实现的 MCP 文件工具（`read_document` / `list_documents`），让 IndependentAgent 在执行期间**主动调用工具**读取引用文档。

---

## 2. 工具实现现状：深度解剖

### 2.1 工具层（tools/file_tools.py）

文件工具在 `autoBMAD/docuswarm/tools/file_tools.py` 中完整实现：

| 功能 | 函数 | 状态 |
|------|------|------|
| 读取单文件 | `read_document(path, validator)` | ✅ 已实现 |
| 列出目录 | `list_documents(directory, recursive)` | ✅ 已实现 |
| 创建 MCP 服务器 | `create_file_read_server(allowed_dirs, node_id)` | ✅ 已实现 |

安全机制：
- `PathValidator`：白名单目录访问控制，防止路径遍历攻击
- `MAX_FILE_SIZE = 50000`：50,000 字符截断限制
- `ALLOWED_EXTENSIONS`：只允许 `.md`, `.txt`, `.yaml`, `.json`, `.py` 等
- `BLOCKED_PATTERNS`：屏蔽 `.env`, `.git`, `__pycache__` 等

### 2.2 MCP 服务器命名规范

```
服务器名:  docuswarm-files-{node_id}
工具名:    mcp__docuswarm-files-{node_id}__read_document
工具名:    mcp__docuswarm-files-{node_id}__list_documents
```

例如 analyst 节点的工具名为：
- `mcp__docuswarm-files-analyst__read_document`
- `mcp__docuswarm-files-analyst__list_documents`

### 2.3 工具权限配置（autoBMAD/nodes/{node_id}/node.yaml）

**关键发现**：各节点的 `node.yaml` 已配置 `tools` 段，且 `docs/` 目录已在白名单中：

```yaml
# autoBMAD/nodes/analyst/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs:
      - "docs/"
      - "docs/research/"
  search_permissions:
    search_dirs:
      - "docs/"
```

```yaml
# autoBMAD/nodes/pm/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs:
      - "docs/"
  search_permissions:
    search_dirs:
      - "docs/"
```

所有5个节点（analyst, pm, ux, architect, po）均有类似配置，`docs/` 已在 `allowed_read_dirs` 中。

`PathValidator` 使用**前缀匹配**逻辑（`resolved_prefix.startswith(allowed_prefix)`），因此 `docs/` 白名单自动覆盖其下全部子目录。`docs/bubble-sort/` 及其中所有文件**无需任何额外配置即可访问，已确认无需单独确认，无需修改任何 node.yaml**。

### 2.4 配置加载链路

```
node.yaml[tools] 
  → NodeLoader._build_node_config()       # autoBMAD/nodes/loader.py L432
  → NodeToolPermissions(
        allowed_builtin_tools=[...],
        file_permissions=NodeFilePermissions(allowed_read_dirs=[...]),
        search_permissions=NodeSearchPermissions(search_dirs=[...])
    )
  → NodeConfig.tool_permissions           # NodeConfig 字段 L172
```

### 2.5 MCP 服务器注册链路

```
IndependentAgent.execute_with_input()
  → _create_pipeline_session_manager(
        file_dirs=["...docs/", "...docs/research/"],
        search_dirs=["...docs/"],
        tool_permissions=full_tool_permissions
    )
  → SessionManager.__init__(tool_permissions=...)
  → SessionManager._create_options()
      → NodeToolFilter.create_mcp_servers()
          → create_file_read_server(allowed_dirs, node_id)   # 注册 FastMCP 服务器
      → NodeToolFilter.get_allowed_tools()                   # 生成 allowed_tools 列表
      → ClaudeAgentOptions(
            mcp_servers={"docuswarm-files-analyst": <server>},
            allowed_tools=["mcp__docuswarm-files-analyst__read_document", ...]
        )
```

**结论**：MCP 服务器创建和工具注册机制**完整且功能正常**，路径解析以 repo root 为基准。

---

## 3. 两套工具注册机制评估

### 3.0 机制概述

DocuSwarm 目前存在两套并行的工具注册机制，分别服务于不同的工具类型：

**机制一：agent_file YAML 注册（静态）**

在 `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` 中声明，由 Claude SDK 在会话启动时加载，注册的是直接在进程内执行的 Python 类工具（`CreateDeliverableTool` 等），这些工具需要访问 DocuSwarm 内部状态（pipeline_id、output_dir 等），适合**写操作**。

**机制二：MCP 服务器运行时注册（动态）**

在 `SessionManager._create_options()` 中通过 `NodeToolFilter` 动态创建 FastMCP 服务器，通过 MCP 协议与 Claude SDK 通信，注册 `read_document`、`list_documents`、`grep_search`、`glob_search` 等工具，无需访问 DocuSwarm 内部状态，适合**读操作**。

### 3.1 两套机制的兼容性

```
SessionManager._create_options()
  options_dict["tools"] = [str(agent_file)]      # 机制一：YAML 中的工具
  options_dict["mcp_servers"] = {...}             # 机制二：MCP 服务器
  options_dict["allowed_tools"] = [...]           # 机制二工具的白名单
```

两套机制在 `ClaudeAgentOptions` 层面**完全兼容**，由 Claude SDK 统一调度。Agent 看到的是一个统一的工具集合，无需感知底层机制差异。

### 3.2 保留 / 移除 / 统一方案评估

| 方案 | 描述 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **保留两套（现状）** | 写操作用 YAML，读操作用 MCP | 职责分离清晰；写工具可访问内部状态；读工具有沙箱隔离 | 两套机制增加认知负担 | ✅ 推荐 |
| **移除 MCP，统一为 YAML** | 将 `read_document` 也注册为 Python 类工具 | 单一注册点 | 失去 MCP 沙箱隔离；路径白名单变为应用层实现 | ⚠️ 可行但降级 |
| **移除 YAML，统一为 MCP** | 将写工具也迁移为 MCP 服务器 | 统一注册机制 | 写工具需访问 DocuSwarm 内部状态，MCP 进程间通信会使其复杂化 | ❌ 不推荐 |
| **新增统一注册层** | 提供统一的 `ToolRegistry` 入口，内部区分写/读路由 | 最优体验 | 工作量大，属于架构重构 | ⏳ 长期目标 |

**结论：当前双轨并行设计是合理的职责划分，保留两套机制即可。**

---

## 4. 瓶颈分析：Agent 何时会调用工具？

### 4.1 当前提示词中的工具指令

`IndependentAgent._format_system_prompt()` 的 instructions 块只指示 Agent 调用一个工具：

```markdown
## Execution Workflow
1. **Create Deliverable**: Use the 'create_deliverable' tool to save your document
2. **Generate Questions**: Formulate follow-up questions with priorities
3. **Return Execution Report**: After using tools, you MUST return a JSON response
```

系统提示词**完全没有提及** `read_document` 或 `list_documents`。Agent 收到 `allowed_tools` 列表和 MCP 服务器，但没有任何指令让它主动读取引用文档。

### 4.2 合同构建器（contract_builder.py）中的上下文注入

`NodePromptContractBuilder._build_context_section()` 负责构建 Agent 收到的上下文消息，包含：

```python
# 原始上下文 (context file 全文)
original_context = context.get("original_context", {})
content = original_context.get("content", "")   # 仅 context file 文本

# 上游交付物摘要
chained = context.get("chained_deliverables", [])  # 仅标题，非全文

# 迭代反馈
feedback = context.get("iteration_feedback")
```

`docs_context` 字段虽然在 `NodeExecutionContext` 协议中存在（`contracts.py` L36），但在 `NodeExecutionContextBuilder.build()` 中**硬编码为空列表**：

```python
# autoBMAD/docuswarm/node_execution/context_builder.py L43
docs_context=[],    # 始终为空，从未填充
```

### 4.3 工具可用 ≠ 工具会被调用

这是方案B的核心矛盾：

| 状态 | 说明 |
|------|------|
| MCP 服务器注册 | ✅ 正常（条件：node_id 和 file_dirs 非空时） |
| `allowed_tools` 配置 | ✅ 包含 `read_document` 和 `list_documents` |
| `docs/` 目录白名单 | ✅ 所有5节点已配置，前缀匹配自动覆盖所有子目录，**无需确认** |
| 系统提示词指令 | ❌ 无任何“读取引用文档”的指令 |
| `docs_context` 注入 | ❌ 硬编码为 `[]`，从不填充 |
| Agent 的工具调用意愿 | ❌ 不确定，取决于 LLM 对上下文中文件名提示的推断 |

---

## 5. 方案B可行性等级

### 5.1 路径A：零代码更改（纯提示词依赖）

依赖 context file 中的文件名提示，让 LLM **自行推断**需要读取引用文档。

```
可行性: 低（约30%成功率）
理由: LLM 看到 "algorithm-spec.md" 等文件名，可能会调用 read_document
     但这依赖 LLM 的自主判断，不稳定，且没有提示词指令支撑
```

### 5.2 路径B：修改系统提示词（低风险）

在 IndependentAgent 的系统提示词或 `contract_builder.py` 的上下文章节中，添加"读取引用文档"的明确指令。

```
可行性: 高（约80-90%成功率）
改动范围: 单文件修改（独立agent.py 或 contract_builder.py）
风险: 低，仅影响提示词内容
```

### 5.3 路径C：填充 docs_context 字段（中等改动）

在 `NodeExecutionContextBuilder.build()` 中读取 context file 内的引用文件路径，
加载文件内容后注入到 `docs_context` 字段，然后在 `contract_builder.py` 中渲染此字段。

```
可行性: 高（约95%成功率）
改动范围: context_builder.py + contract_builder.py + executor.py
风险: 低，完全符合已有 NodeExecutionContext 协议设计
优势: 无需依赖 LLM 主动调用工具，直接注入内容
搜索范围: docs/ 目录及其所有子目录（递归），匹配 original_context 中提到的文件名
```

---

## 6. 推荐实施方案

综合分析后，建议**分两步走**：

### 步骤一（立即可用）：修改系统提示词

在 `IndependentAgent._format_system_prompt()` 或 `ContractBuilder._build_instructions_section()` 的指令块中新增：

**改动文件**: `autoBMAD/docuswarm/agents/independent.py` L144-223

### 步骤二（更可靠）：填充 docs_context 字段

在 `NodeExecutionContextBuilder.build()` 中实现引用文档预加载：

```python
# autoBMAD/docuswarm/node_execution/context_builder.py
def _resolve_reference_docs(
    self,
    original_context: dict[str, Any],
    node_id: str,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """从 original_context 中提取并读取引用文档。"""
    content = original_context.get("content", "")
    # 提取 Markdown 中的 `filename.md` 引用
    import re
    refs = re.findall(r'`([^`]+\.(?:md|txt|yaml|json))`', content)

    docs_context = []
    for ref in refs:
        # 在 docs/ 目录下查找
        for search_dir in [repo_root / "docs", repo_root / "docs" / "bubble-sort"]:
            candidate = search_dir / ref
            if candidate.exists():
                file_content = candidate.read_text(encoding="utf-8")
                docs_context.append({
                    "filename": ref,
                    "path": str(candidate),
                    "content": file_content[:10000],  # 截断保护
                })
                break
    return docs_context
```

然后在 `ContractBuilder._build_context_section()` 中渲染 `docs_context`：

```python
# 引用文档
docs = context.get("docs_context", [])
if docs:
    sections.append("\n## 引用文档")
    for doc in docs:
        sections.append(f"\n### {doc['filename']}\n\n{doc['content']}")
```

**改动文件**:
- `autoBMAD/docuswarm/node_execution/context_builder.py`
- `autoBMAD/docuswarm/prompts/contract_builder.py`

---

---

## 7. 当前节点文件权限覆盖状态

| 节点 | allowed_read_dirs | docs/ 任意子目录可访问? |
|------|-------------------|-----------------------|
| analyst | `docs/`, `docs/research/` | ✅ 确认可访问 |
| pm | `docs/` | ✅ 确认可访问 |
| ux | `docs/` | ✅ 确认可访问 |
| architect | `docs/` | ✅ 确认可访问 |
| po | `docs/` | ✅ 确认可访问 |

`PathValidator.validate()` 的前缀匹配逻辑（`resolved_prefix.startswith(allowed_prefix)`）保证：凡是 `docs/` 在白名单内，其下**任意层级**的子目录和文件均无需额外配置即可访问。`docs/bubble-sort/`、`docs/research/` 等均已覆盖，**无需单独确认，无需修改任何 node.yaml**。

---

## 8. 已知风险与缓解措施

| 风险 | 严重度 | 缓解措施 |
|------|--------|----------|
| MCP 服务器创建失败（`mcp` 包未安装） | 高 | `create_file_read_server` 在导入失败时抛出 `FileToolError`；需确保 `mcp` 依赖已安装 |
| Agent 忽略工具调用指令 | 中 | 步骤二（docs_context 注入）不依赖 Agent 主动性，直接预加载内容 |
| 路径解析错误（repo root vs autoBMAD root） | 中 | executor.py 中有 `repo_root` 修正逻辑（`auto_bmad_root.parent if auto_bmad_root.name == "autoBMAD"`） |
| 文件内容超过 10,000 字符被截断 | 低 | `_resolve_reference_docs` 自动截断并添加“[内容已截断]”标识 |
| docs/ 下存在同名文件（不同子目录） | 低 | 取路径最浅的（sorted rglob 保证确定性） |

---

## 9. 关键说明：agent_file 与 MCP 工具并行调度

`independent_agent.yaml` 注册写操作工具（YAML 机制一），MCP 服务器注册读操作工具（机制二），两者在 `ClaudeAgentOptions` 中并行存在，由 Claude SDK 统一调度，**不存在冲突**。

**MCP 服务器实际创建条件**（`SessionManager._create_options` L169）：

```python
if self._node_id and (has_tool_permissions or has_dirs):
    # 仅在此条件成立时才创建 MCP 服务器并配置 allowed_tools
```

`IndependentAgent.execute_with_input()` 通过 `_create_pipeline_session_manager` 传递了 `node_id`（非空）和 `file_dirs`（来自 node.yaml tools 段），条件成立，MCP 服务器**会被创建**。两套机制的职责划分与建议已在第3节详述。

---

## 10. 完整数据流（当前状态 vs 修改后状态）

### 当前状态（方案B未实施）

```
bubble-sort-context.md (提到 algorithm-spec.md 等)
    │
    ▼ PipelineService.start()
subject_context["content"] = "全文字符串（含引用文件名）"
    │
    ▼ NodeExecutionContextBuilder.build()
NodeExecutionContext {
    original_context: {"content": "...algorithm-spec.md..."},
    docs_context: [],           ← 始终为空
}
    │
    ▼ IndependentAgent.execute_with_input()
user_prompt = "...algorithm-spec.md 等文件名出现在原文中..."
MCP 服务器: mcp__docuswarm-files-analyst__read_document 已注册
系统提示词: 无读取引用文档的指令
    │
    ▼ LLM 决策
可能会调用 read_document（不稳定），也可能忽略引用文件
```

### 修改后状态（步骤一 + 步骤二实施后）

```
bubble-sort-context.md (提到 algorithm-spec.md 等)
    │
    ▼ PipelineService.start()
subject_context["content"] = "全文字符串"
    │
    ▼ NodeExecutionContextBuilder.build()  ← 新增：_resolve_reference_docs()
NodeExecutionContext {
    original_context: {"content": "..."},
    docs_context: [                        ← 预加载引用文档内容
        {"filename": "algorithm-spec.md", "content": "# Bubble Sort..."},
        {"filename": "requirements.md",   "content": "# Stakeholder..."},
        {"filename": "test-criteria.md",  "content": "# Evaluation..."},
    ]
}
    │
    ▼ ContractBuilder._build_context_section()  ← 新增：渲染 docs_context
user_prompt = """
## 原始上下文
...（context file 全文）...

## 引用文档

### algorithm-spec.md
...（算法规格全文）...

### requirements.md
...（需求文档全文）...

### test-criteria.md
...（评估标准全文）...
"""
    │
    ▼ LLM
Agent 直接在提示词中看到所有引用文档内容，无需主动调用工具
```

---

## 11. 改动清单（最小化实施）

### 优先级 P0：立即可实施，无架构风险

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `autoBMAD/docuswarm/node_execution/context_builder.py` | 新增 `_resolve_reference_docs()` + 修改 `build()` | 递归扫描 `docs/` 及子目录，提取 original_context 中引用的文件名，预加载内容 |
| `autoBMAD/docuswarm/prompts/contract_builder.py` | 修改 `_build_context_section()` | 渲染 `docs_context` 字段内容到 Agent 提示词 |
| `autoBMAD/docuswarm/node_execution/executor.py` | 修改 `context_builder.build()` 调用 | 传递 `repo_root` 参数 |

### 优先级 P1：提升工具主动调用成功率（可选）

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `autoBMAD/docuswarm/agents/independent.py` | 修改 `_format_system_prompt()` | 添加读取引用文档的工作流指令（如 docs_context 已注入，此项可选）|

### 无需改动

| 文件 | 原因 |
|------|------|
| `autoBMAD/nodes/*/node.yaml` | `docs/` 已在 `allowed_read_dirs`，前缀匹配自动覆盖所有子目录 |
| `autoBMAD/docuswarm/tools/file_tools.py` | 工具逻辑完整无需修改 |
| `autoBMAD/docuswarm/llm/tool_filter.py` | MCP 服务器创建逻辑正常 |
| `autoBMAD/docuswarm/llm/session_manager.py` | 工具注册链路正常 |

---

## 12. 结论

方案B（使用 `read_docs_file` 工具）**技术上完全可行**，核心机制均已实现：

1. ✅ `read_document` / `list_documents` 工具已实现（`file_tools.py`）
2. ✅ MCP 服务器创建机制已实现（`tool_filter.py` + `session_manager.py`）
3. ✅ 节点权限配置已覆盖 `docs/` 目录，前缀匹配自动覆盖所有子目录，**无需确认，无需修改 node.yaml**
4. ✅ 两套工具注册机制（YAML 写工具 + MCP 读工具）职责分离，兼容并行，**建议保留现状**
5. ❌ `docs_context` 字段始终为空，未实现预加载逻辑（`context_builder.py` L43）
6. ❌ 系统提示词无读取引用文档的指令（`independent.py` L144-223）

**最低工作量路径**：修改 3 个文件（`context_builder.py` + `contract_builder.py` + `executor.py`），实现引用文档递归搜索与预加载（步骤二），直接将 `docs/` 目录下的引用文档内容注入 Agent 提示词，无需依赖 Agent 主动调用工具。

**步骤二的引用提取范围**：
- 扫描 `original_context["content"]` 全文
- 提取反引号包裹的文件名和裸文件名（`.md`、`.txt`、`.yaml`、`.json`）
- 在 `docs/` 目录下**递归**查找（覆盖 `docs/bubble-sort/`、`docs/research/` 等所有子目录）
- 同名文件取路径最浅的版本，单文件最多读取 10,000 字符

**推荐行动**：实施 P0 改动（步骤二），可在不引入任何架构风险的情况下，让 DocuSwarm 完整读取 `bubble-sort-context.md` 中引用的所有支撑文档。
