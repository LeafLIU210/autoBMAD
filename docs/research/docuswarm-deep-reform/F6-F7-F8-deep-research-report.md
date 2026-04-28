# F6/F7/F8 深度研究报告：运行时链路断裂与语义重构缺口

**报告编号**: DS-2026-04-07-F678  
**研究日期**: 2026-04-07  
**审查基线**: `docs/evaluation/2026-04-07-docuswarm-deep-reform-implementation-review.md`  
**涉及文档**:
- `05-shared-context-update-mechanism.md`
- `02-node-task-skill-mapping.md`
- `03-document-creation-constraints.md`

---

## 执行摘要

本报告针对 DocuSwarm Deep Reform 实施审查中发现的三个关键问题进行深度代码级分析：

| 问题 | 严重程度 | 核心缺陷 | 影响范围 |
|------|----------|----------|----------|
| **F6** | High | `update_context` 工具未进入 MCP 运行时链路 | Shared Context 更新机制无法工作 |
| **F7** | Medium | Analyst 任务语义未按方案重构 | 角色职责与 Skill 能力错位 |
| **F8** | Medium | 模板对齐停留在配置层，未接线到运行时 | BMAD 模板资产未充分利用 |

**关键发现**: 这三个问题共同指向一个系统性缺口——**配置模型层与运行时执行层之间存在"最后一公里"断裂**。配置字段已完备，但运行时接线未完成。

---

## F6: `update_context` 工具 MCP 暴露链路断裂

### 1.1 问题描述

**方案期望** (来自 `05-shared-context-update-mechanism.md`):
- 节点可按 `shared_context` 权限配置使用 `update_context` 工具
- tool permissions、state persistence、agent runtime 三者闭环

**实际实现状态**:
- ✅ `UpdateContextTool` 实现完整（`update_context.py:54-256`）
- ✅ 白名单、set/append/remove 操作、StateManager 持久化均已实现
- ✅ 节点配置支持 `tools.shared_context` 字段
- ❌ **运行时 MCP 暴露缺失**

### 1.2 代码级根因分析

#### 1.2.1 `NodeToolFilter.create_mcp_servers()` 未创建 update_context server

```python
# autoBMAD/docuswarm/llm/tool_filter.py:171-245

def create_mcp_servers(self) -> dict[str, Any]:
    servers: dict[str, Any] = {}
    
    # 1. 创建 file read server
    if file_dirs:
        file_server = create_file_read_server(...)
        servers[server_name] = file_server
    
    # 2. 创建 search server  
    if search_dirs:
        search_server = create_search_server(...)
        servers[server_name] = search_server
    
    # 3. 创建 deliverable server
    if self.output_dir:
        deliverable_server = create_deliverable_server(...)
        servers[server_name] = deliverable_server
    
    # ❌ 缺失: 没有创建 update_context server!
    return servers
```

**问题**: `create_mcp_servers()` 仅创建了 file、search、deliverable 三个 server，完全遗漏了 `update_context` server 的创建。

#### 1.2.2 `NodeToolFilter.get_allowed_tools()` 未暴露 update_context 工具

```python
# autoBMAD/docuswarm/llm/tool_filter.py:101-169

def get_allowed_tools(self) -> list[str]:
    tools: list[str] = []
    
    # 1. Builtin tools
    tools.extend(self.tool_permissions.allowed_builtin_tools)
    
    # 2. MCP file tools
    if file_dirs:
        tools.extend(["read_document", "list_documents"])
    
    # 3. MCP search tools
    if search_dirs:
        tools.extend(["grep_search", "glob_search"])
    
    # 4. MCP deliverable tools
    if self.output_dir:
        tools.extend([
            "create_deliverable",
            "submit_execution_report"  # F2 fix 已添加
        ])
    
    # ❌ 缺失: 没有添加 update_context 工具!
    return tools
```

**问题**: `get_allowed_tools()` 返回的允许工具列表中不包含 `update_context`，即使节点配置了 `shared_context.enabled: true`。

#### 1.2.3 缺失 `create_update_context_server()` 工厂函数

对比其他工具都有对应的 MCP server 工厂函数：

| 工具 | 工厂函数 | 位置 |
|------|----------|------|
| read_document/list_documents | `create_file_read_server()` | `file_tools_sdk.py:307` |
| grep_search/glob_search | `create_search_server()` | `search_tools_sdk.py:306` |
| create_deliverable/submit_execution_report | `create_deliverable_server()` | `create_deliverable_sdk.py:251` |
| **update_context** | **❌ 缺失** | **需要新建** |

### 1.3 运行时链路验证

即使 `independent.py` 中保留了 `shared_context` 配置：

```python
# autoBMAD/docuswarm/agents/independent.py:967-979

# F1 Fix: 使用 dataclasses.replace 保留 skills 和 shared_context
full_tool_permissions = replace(
    node_config.tool_permissions,
    file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
    search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
    # shared_context 被保留，但没有被使用!
)
```

**运行时流程**:
```
IndependentAgent.execute_with_input()
  ↓
replace() 保留 shared_context 配置
  ↓
SessionManager(work_dir, tool_permissions=full_tool_permissions)
  ↓
_create_options() → NodeToolFilter.create_mcp_servers()
  ↓
❌ 没有创建 update_context server!
```

### 1.4 修复方案

#### 方案 A: 在 tool_filter.py 中集成 update_context (推荐)

```python
# autoBMAD/docuswarm/llm/tool_filter.py

class NodeToolFilter:
    def create_mcp_servers(self, pipeline_id: str | None = None) -> dict[str, Any]:
        # ... 现有 server 创建 ...
        
        # 新增: 创建 update_context server (当 shared_context 启用时)
        if self.tool_permissions.shared_context.enabled and pipeline_id:
            from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server
            
            update_server = create_update_context_server(
                pipeline_id=pipeline_id,
                node_id=self.node_id,
                allowed_operations=self.tool_permissions.shared_context.operations,
            )
            servers[update_server["name"]] = update_server
    
    def get_allowed_tools(self) -> list[str]:
        # ... 现有工具 ...
        
        # 新增: 添加 update_context 工具
        if self.tool_permissions.shared_context.enabled:
            tools.append(
                MCP_TOOL_NAME_FORMAT.format(
                    type="shared-context", node_id=self.node_id, tool_name="update_context"
                )
            )
```

#### 方案 B: 新建 `update_context_sdk.py`

创建 `autoBMAD/docuswarm/tools/update_context_sdk.py`，实现：

```python
"""SDK MCP 格式的 update_context 工具实现."""

from claude_agent_sdk import create_sdk_mcp_server, tool

def create_update_context_server(
    pipeline_id: str,
    node_id: str,
    allowed_operations: list[str],
) -> McpSdkServerConfig:
    """Create an SDK MCP server for update_context tool."""
    
    @tool(
        "update_context",
        "Update shared context with key-value operations",
        {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Context key to update"},
                "value": {"type": "any", "description": "Value to set/append/remove"},
                "operation": {
                    "type": "string",
                    "enum": allowed_operations,
                    "default": "set"
                },
            },
            "required": ["key", "value"],
        },
    )
    async def update_context_tool(args: dict[str, Any]) -> dict[str, Any]:
        from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        tool = UpdateContextTool(
            state_manager=StateManager(),
            pipeline_id=pipeline_id,
        )
        result = await tool.execute(args)
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    
    return create_sdk_mcp_server(
        name=f"docuswarm-shared-context-{node_id}",
        version="1.0.0",
        tools=[update_context_tool],
    )
```

### 1.5 影响评估

| 维度 | 影响 |
|------|------|
| **功能影响** | `shared_context` 更新机制完全不可用，节点无法共享上下文 |
| **用户感知** | 节点执行时 `update_context` 工具不可见，Agent 无法调用 |
| **数据一致性** | 即使 StateManager 支持持久化，Agent 无法触发更新 |
| **修复优先级** | **P0** - 阻断 Shared Context 核心功能 |

---

## F7: Analyst 节点任务语义未按方案重构

### 2.1 问题描述

**方案期望** (来自 `02-node-task-skill-mapping.md`):
- Analyst 从 `create-business-analysis-report` 重构为 `create-product-brief`
- 任务语义与 `bmad-product-brief` skill 对齐

**当前配置** (`autoBMAD/nodes/analyst/node.yaml`):
```yaml
task:
  name: create-business-analysis-report          # ❌ 旧任务名
  description: Transform raw data into actionable business insights...  # ❌ 旧描述
  role_supplement: Focus on evidence-based conclusions...
  skill_ref: bmad-product-brief                   # ✅ Skill 引用正确
```

### 2.2 语义错位分析

#### 2.2.1 任务名称错位

| 维度 | 当前值 | 方案要求值 |
|------|--------|------------|
| **task.name** | `create-business-analysis-report` | `create-product-brief` |
| **task.description** | 数据分析报告描述 | 产品简介创建描述 |
| **角色定位** | Data Analyst | Strategic Business Analyst & Product Discovery Expert |

#### 2.2.2 BMAD Skill 工作流期望

根据 `_bmad/bmm/agents/bmad-product-brief/`:
- 5阶段工作流: Discovery → Elicitation → Review → Finalize
- 输出: 1-2 页 executive brief
- 角色名: "Mary" (模板指定)

#### 2.2.3 当前 vs 期望 Persona 对比

```json
// 当前 persona.json (推测)
{
  "name": "Analyst",
  "role": "Data Analyst",
  "expertise": ["statistical analysis", "data visualization"]
}

// 方案期望 persona.json
{
  "name": "Mary",
  "role": "Strategic Business Analyst & Product Discovery Expert",
  "expertise": [
    "Product discovery and market research",
    "Porter's Five Forces and SWOT analysis",
    "Requirements elicitation"
  ],
  "communication_style": "treasure_hunter_energy"
}
```

### 2.3 运行时影响

**混合态问题**:
```
任务描述:  "创建业务分析报告" (数据分析师视角)
Skill 引用: bmad-product-brief (产品发现促进者视角)
Persona:   Data Analyst (旧角色)

结果: Agent 行为落在 "旧 analyst 职责 + 新 skill 能力" 的混合态
```

### 2.4 修复方案

#### 步骤 1: 更新 node.yaml

```yaml
# autoBMAD/nodes/analyst/node.yaml

task:
  name: create-product-brief
  description: |
    通过协作发现创建产品简介。作为产品发现促进者，
    引导用户理解产品意图，理解产品愿景后再分析工件。
  role_supplement: |
    你是产品发现促进者，不是数据扫描器。
    先与用户协作澄清产品意图，再基于澄清后的理解分析工件。
  skill_ref: bmad-product-brief
```

#### 步骤 2: 更新 persona.json

```json
{
  "name": "Mary",
  "role": "Strategic Business Analyst & Product Discovery Expert",
  "description": "Product discovery facilitator who guides teams to understand product intent",
  "expertise": [
    "Product discovery and market research",
    "Porter's Five Forces framework",
    "SWOT analysis",
    "Requirements elicitation",
    "Business model canvas"
  ],
  "communication_style": "treasure_hunter_energy",
  "working_style": "collaborative",
  "principles": [
    "Understand the 'why' before analyzing the 'what'",
    "Facilitate clarity, don't just report data"
  ]
}
```

#### 步骤 3: 验证 Skill 对齐

```python
# 测试脚本
from autoBMAD.nodes.loader import NodeLoader

config = NodeLoader.load("analyst")
assert config.task.name == "create-product-brief"
assert config.task.skill_ref == "bmad-product-brief"
assert config.tool_permissions.skills.whitelist == [
    "bmad-product-brief",
    "bmad-domain-research",
    "bmad-market-research",
    "bmad-advanced-elicitation"
]
```

---

## F8: 模板对齐停留在配置层，未接线到运行时

### 3.1 问题描述

**方案期望** (来自 `03-document-creation-constraints.md`):
- BMAD 模板对齐不应只停留在 `template_title` 文字提示
- 独立模板资源应可被运行时消费

**当前实现状态**:
- ✅ `template_title`、`output_filename`、`format_hints` 进入 deliverable requirements
- ✅ `autoBMAD/docuswarm/templates/*.yaml` 模板文件存在
- ❌ **模板文件未被 IndependentAgent prompt 生成流程装载**

### 3.2 代码级分析

#### 3.2.1 TemplateLoader 默认路径

```python
# autoBMAD/docuswarm/prompts/template_loader.py:88

class TemplateLoader:
    DEFAULT_TEMPLATES_DIR = Path(__file__).parent / "templates"
    # → autoBMAD/docuswarm/prompts/templates/
```

**问题**: `DEFAULT_TEMPLATES_DIR` 指向 `prompts/templates/`，但实际模板文件位于：
- `autoBMAD/docuswarm/templates/analyst_templates.yaml`
- `autoBMAD/docuswarm/templates/pm_templates.yaml`
- ...

#### 3.2.2 ContractBuilder 模板引用

```python
# autoBMAD/docuswarm/prompts/contract_builder.py:216-237

def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
    # template_title (回退到 deliverable_type)
    template_title = reqs.get("template_title") or deliverable_type
    if template_title:
        sections.append(f"\n**文档标题**: {template_title}")
    
    # required_sections
    required_sections = reqs.get("required_sections", [])
    if required_sections:
        sections.append("\n**必须包含以下章节**:")
        for section in required_sections:
            sections.append(f"- {section}")
```

**问题**: 仅使用 `template_title` 字段的文本值，未加载和解析 `analyst_templates.yaml` 中的结构化模板定义。

#### 3.2.3 模板文件内容 vs 运行时消费

```yaml
# autoBMAD/docuswarm/templates/analyst_templates.yaml

templates:
  - template_id: market_research
    title: "Market Research Report"
    filename_pattern: "market-research-report.md"
    sections:
      - heading: "Executive Summary"
        required: true
        description: "High-level overview of findings"
      # ... 更多结构化定义

standards:
  style_guide: "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"
  diagram_format: "mermaid"
```

**当前运行时行为**:
```
TemplateLoader 从 prompts/templates/ 加载 (空或不存在)
  ↓
ContractBuilder 只使用 node.yaml 中的 template_title 文本
  ↓
System Prompt 只有: "**文档标题**: analyst-report"
  ↓
❌ 没有加载 analyst_templates.yaml 的章节定义和标准
```

### 3.3 运行时接线缺口

| 模板资产 | 位置 | 当前消费方式 | 应有消费方式 |
|----------|------|--------------|--------------|
| `analyst_templates.yaml` | `docuswarm/templates/` | ❌ 未消费 | ✅ 加载 sections 到 prompt |
| `pm_templates.yaml` | `docuswarm/templates/` | ❌ 未消费 | ✅ 加载 PRD 模板 |
| `ux_templates.yaml` | `docuswarm/templates/` | ❌ 未消费 | ✅ 加载 UX 规范模板 |
| standards.style_guide | 模板文件内引用 | ❌ 未消费 | ✅ 注入格式要求 |

### 3.4 修复方案

#### 方案 A: 修改 TemplateLoader 默认路径

```python
# autoBMAD/docuswarm/prompts/template_loader.py

class TemplateLoader:
    # 从 docuswarm/templates/ 加载，而不是 prompts/templates/
    DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
```

#### 方案 B: 扩展 ContractBuilder 加载模板

```python
# autoBMAD/docuswarm/prompts/contract_builder.py

class NodePromptContractBuilder:
    def __init__(self):
        self.template_loader = TemplateLoader()
    
    def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
        # 现有: 从 node.yaml 获取基础配置
        template_title = reqs.get("template_title")
        
        # 新增: 从模板文件加载结构化定义
        try:
            template_data = self._load_node_template(context.node_id, template_title)
            if template_data:
                sections.append(self._format_template_sections(template_data))
        except Exception:
            pass  # Graceful fallback
    
    def _load_node_template(self, node_id: str, template_id: str | None) -> dict | None:
        """Load template from docuswarm/templates/{node_id}_templates.yaml"""
        template_file = f"{node_id}_templates"
        try:
            data = self.template_loader.load_template(template_file)
            templates = data["raw"].get("templates", [])
            # Find matching template
            for t in templates:
                if template_id is None or t["template_id"] == template_id:
                    return t
        except Exception:
            return None
```

#### 方案 C: 在 IndependentAgent 中集成模板渲染

```python
# autoBMAD/docuswarm/agents/independent.py

class IndependentAgent:
    def _format_system_prompt_with_contract(self, contract):
        system_prompt = self.contract_builder.render_independent_system_prompt(contract)
        
        # 新增: 追加模板指导
        try:
            template_guidance = self._load_template_guidance()
            if template_guidance:
                system_prompt += f"\n\n{template_guidance}"
        except Exception:
            pass  # Graceful degradation
        
        return system_prompt
```

### 3.5 模板对齐完整链路

修复后的完整接线：

```
autoBMAD/docuswarm/templates/
  └── analyst_templates.yaml (模板资产)
        ↓
TemplateLoader (加载)
  ↓
NodePromptContractBuilder (解析)
  ↓
_render_independent_system_prompt() (注入)
  ↓
IndependentAgent System Prompt (运行时可见)
  ↓
LLM 按模板章节和标准生成文档
```

---

## 4. 三问题关联分析

### 4.1 共同的系统性问题

这三个问题共享一个根因模式：

```
┌─────────────────────────────────────────────────────────────┐
│                    配置模型层 (已完备)                        │
│  - node.yaml: shared_context, skill_ref, template_title      │
│  - UpdateContextTool: 实现完整                                │
│  - templates/*.yaml: 模板资产就绪                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │   接线断裂层     │
                    │  (F6, F7, F8)   │
                    └─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    运行时执行层 (缺失)                        │
│  - MCP server 未创建 update_context                          │
│  - Analyst 任务语义未更新                                     │
│  - 模板未加载到 prompt                                        │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 修复优先级矩阵

| 问题 | 业务影响 | 修复复杂度 | 建议优先级 |
|------|----------|------------|------------|
| **F6** | 阻断 Shared Context 功能 | 中等 (需新建 SDK 模块) | **P0** |
| **F7** | 角色职责错位 | 低 (仅配置变更) | **P1** |
| **F8** | 模板价值未发挥 | 中等 (需扩展 ContractBuilder) | **P1** |

---

## 5. 调试与验证工具

### 5.1 MCP 工具链验证脚本

```python
#!/usr/bin/env python3
"""验证 MCP 工具链完整性."""

import asyncio
from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

def verify_mcp_chain(node_id: str = "analyst"):
    """验证节点的 MCP 工具链."""
    config = NodeLoader.load(node_id)
    filter_obj = NodeToolFilter.from_node_config(config)
    
    print(f"\n=== 节点: {node_id} ===")
    
    # 检查配置
    print("\n1. 配置层检查:")
    print(f"   shared_context.enabled: {config.tool_permissions.shared_context.enabled}")
    print(f"   shared_context.operations: {config.tool_permissions.shared_context.operations}")
    
    # 检查允许的工具
    print("\n2. 允许的工具列表:")
    allowed = filter_obj.get_allowed_tools()
    for tool in allowed:
        print(f"   - {tool}")
    
    # 检查 update_context 是否存在
    has_update_context = any("update_context" in t for t in allowed)
    print(f"\n3. update_context 工具: {'✅ 存在' if has_update_context else '❌ 缺失'}")
    
    # 检查 MCP servers
    print("\n4. MCP Servers:")
    try:
        servers = filter_obj.create_mcp_servers()
        for name in servers.keys():
            print(f"   - {name}")
        
        has_shared_context_server = any("shared-context" in k for k in servers.keys())
        print(f"\n5. shared-context server: {'✅ 存在' if has_shared_context_server else '❌ 缺失'}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    for node in ["analyst", "pm", "ux", "architect", "po"]:
        verify_mcp_chain(node)
```

### 5.2 节点配置验证脚本

```python
#!/usr/bin/env python3
"""验证节点 Deep Reform 配置."""

from autoBMAD.nodes.loader import NodeLoader

def verify_node_reform_compliance(node_id: str):
    """验证节点是否符合 Deep Reform 方案."""
    config = NodeLoader.load(node_id)
    
    print(f"\n=== {node_id.upper()} 节点合规检查 ===")
    
    # F7 检查: Analyst 任务语义
    if node_id == "analyst":
        task_name = config.task.name
        expected = "create-product-brief"
        status = "✅" if task_name == expected else "❌"
        print(f"\n[F7] 任务名称: {task_name} (期望: {expected}) {status}")
    
    # F6 检查: Shared Context 配置
    sc = config.tool_permissions.shared_context
    print(f"\n[F6] Shared Context:")
    print(f"     enabled: {sc.enabled}")
    print(f"     operations: {sc.operations}")
    
    # F8 检查: 模板配置
    d = config.deliverable
    print(f"\n[F8] 模板配置:")
    print(f"     template_title: {d.template_title}")
    print(f"     output_filename: {d.output_filename}")
    print(f"     document_types: {d.document_types}")

if __name__ == "__main__":
    for node in ["analyst", "pm", "ux", "architect", "po"]:
        verify_node_reform_compliance(node)
```

---

## 6. 修复实施路线图

### Phase 1: F6 - MCP 链路修复 (2-3 天)

- [ ] 创建 `update_context_sdk.py` 实现 `create_update_context_server()`
- [ ] 修改 `tool_filter.py` 集成 update_context server 创建
- [ ] 修改 `tool_filter.py` 在 `get_allowed_tools()` 中添加 update_context
- [ ] 更新 `independent.py` 传递 `pipeline_id` 给 `create_mcp_servers()`
- [ ] 编写集成测试验证 Shared Context 更新闭环

### Phase 2: F7 - Analyst 语义重构 (1 天)

- [ ] 更新 `analyst/node.yaml`: task.name → `create-product-brief`
- [ ] 更新 `analyst/node.yaml`: task.description (产品发现导向)
- [ ] 更新 `analyst/persona.json`: name → "Mary", role 更新
- [ ] 验证 Skill 白名单对齐

### Phase 3: F8 - 模板运行时接线 (2-3 天)

- [ ] 修复 `TemplateLoader.DEFAULT_TEMPLATES_DIR` 指向
- [ ] 扩展 `ContractBuilder` 加载模板文件
- [ ] 实现 `_load_node_template()` 和 `_format_template_sections()`
- [ ] 验证模板章节注入 System Prompt

---

## 7. 总结

本研究通过对 F6、F7、F8 三个问题的深度代码分析，揭示了 DocuSwarm Deep Reform 实施中的一个共同模式：**配置完备但运行时接线缺失**。

| 问题 | 核心缺口 | 修复关键 |
|------|----------|----------|
| F6 | `update_context` 未创建 MCP server | 新建 `update_context_sdk.py`，集成到 `tool_filter.py` |
| F7 | Analyst 任务描述与 Skill 不对齐 | 更新 `node.yaml` 和 `persona.json` 配置 |
| F8 | 模板文件未加载到 prompt | 修复 `TemplateLoader` 路径，扩展 `ContractBuilder` |

这三个问题的修复将完成 Deep Reform 方案的"最后一公里"，使配置层的改进真正转化为运行时的能力提升。

---

**报告完成**: 2026-04-07  
**研究员**: Code Analysis Agent  
**下次审查**: 修复实施完成后
