# Claude Agent SDK Skills 技能引入方案研究报告

## 1. 概述

### 1.1 研究目标

研究如何在 DocuSwarm 的独立 Agent（IndependentAgent）中引入 Claude Agent SDK 的 Skills 技能命令，建立从 SDK 原生 Skills 机制到 DocuSwarm 节点工具权限系统的完整集成方案。

### 1.2 研究背景

**当前现状**：
- DocuSwarm 项目存在 50+ 个预定义的 BMAD 技能（`.claude/skills/` 目录）
- 独立 Agent 通过 SessionManager 调用 Claude Agent SDK
- 已实现节点级工具权限系统（node.yaml → tools 配置）
- MCP 工具（文件读取、搜索）已集成，通过 NodeToolFilter 管理

**存在的问题**：
- SDK 中的 Skills 原生发现和启用机制（`setting_sources` + `allowed_tools["Skill"]`）尚未被利用
- 系统 prompt 中 Skills 描述通过手工注入实现，效率低且易出错
- Skills 发现和加载流程不透明，缺乏统一的元数据管理
- 无法充分利用 SDK 内置的 Skills 自动发现和管理能力

---

## 2. SDK Skills 机制深度分析

### 2.1 Skills 自动发现机制

根据 `autoBMAD/agentdocs/22_skills.md` 和 `05_python.md` 的官方文档分析：

#### 2.1.1 Skills 定义形式

```
.claude/skills/{skill_name}/
└── SKILL.md              # YAML 前置元数据 + Markdown 内容

SKILL.md 结构:
  ┌─────────────────────────────────────────┐
  │ ---                                      │
  │ name: skill-name                         │  ← 技能唯一标识
  │ description: "何时触发此技能"             │  ← 关键：Claude 用于决策
  │ ---                                      │
  │                                          │
  │ # 技能名称                               │
  │ ## 详细说明（Markdown）...              │
  │ ...                                      │
  └─────────────────────────────────────────┘
```

#### 2.1.2 设置源（Setting Sources）

Claude Agent SDK 支持三个设置源：

| 源 | 位置 | 用途 | 共享范围 |
|---|------|------|--------|
| `"project"` | `.claude/skills/` | 项目级技能 | 通过 git 与团队共享 |
| `"user"` | `~/.claude/skills/` | 用户级技能 | 跨所有项目的个人技能 |
| `"local"` | CLI 本地配置 | 本地临时技能 | 仅限当前会话 |

**关键点**：默认情况下 SDK 不加载任何技能源。必须显式配置 `setting_sources` 才能启用。

#### 2.1.3 Skills 发现流程时间线

```
初始化时（启动时）:
  ┌─────────────────────────────────────┐
  │ 1. 扫描 setting_sources 中的目录    │
  ├─────────────────────────────────────┤
  │ 2. 读取所有 SKILL.md 文件头元数据   │  ← 快速，仅前置信息
  ├─────────────────────────────────────┤
  │ 3. 构建技能索引（name, description）│
  ├─────────────────────────────────────┤
  │ 4. 将索引发送给 Claude              │  ← 包含在上下文中
  └─────────────────────────────────────┘

使用时（Claude 决策调用）:
  ┌─────────────────────────────────────┐
  │ 1. Claude 根据提示选择技能          │
  ├─────────────────────────────────────┤
  │ 2. SDK 按需加载完整 SKILL.md 内容   │  ← 延迟加载，节省上下文
  ├─────────────────────────────────────┤
  │ 3. 将完整指令发送给 Claude          │
  ├─────────────────────────────────────┤
  │ 4. Claude 执行技能中的工作流        │
  └─────────────────────────────────────┘
```

### 2.2 Skills 调用方式和工具启用

#### 2.2.1 工具启用配置

```python
# Python SDK 中启用 Skills
options = ClaudeAgentOptions(
    cwd="/path/to/project",                    # 指向包含 .claude/skills/ 的目录
    setting_sources=["user", "project"],       # 启用设置源
    allowed_tools=["Skill", "Read", "Write", "Bash"]  # 必须包含 "Skill"
)

async for message in query(
    prompt="请使用合适的技能来处理这个任务",
    options=options
):
    print(message)
```

**关键配置项**：

| 配置项 | 必需 | 说明 |
|-------|------|------|
| `cwd` | 否 | 工作目录，用于定位 `.claude/skills/`。默认为当前目录 |
| `setting_sources` | 必需 | 要加载的设置源列表 |
| `allowed_tools` | 必需 | 必须包含 `"Skill"` 才能启用 Skills 工具 |

#### 2.2.2 Skills 在 allowed_tools 中的表示

```python
# 正确配置 - Skills 为一个通用工具名
allowed_tools=[
    "Skill",                    # ← 启用所有可用 Skills
    "Read",
    "Write",
    "Bash",
]

# 无法按单个 Skill 过滤
# allowed_tools 中不存在 "mcp__skills__bmad-agent-analyst" 这样的格式
# Skills 不像 MCP 工具那样有命名空间和细粒度控制
```

**重要限制**：根据 `agentdocs/22_skills.md` 第 84-95 行，SKILL.md 中的 `allowed-tools` 前置元数据字段**仅在 Claude Code CLI 中受支持**，通过 SDK 使用时不适用。工具权限通过 `ClaudeAgentOptions.allowed_tools` 全局控制。

### 2.3 Skills 元数据格式

#### 2.3.1 SKILL.md 前置元数据字段

```yaml
---
name: skill-unique-name              # 技能在系统中的唯一标识
description: |                       # 关键字段：Claude 用于判断何时触发该技能
  "简明描述此技能的用途和适用场景。应包含关键词便于 Claude 理解。"
---
```

#### 2.3.2 前置元数据最佳实践

根据 `.claude/skills/` 目录中的 50+ 个 SKILL.md 文件分析，有效的 description 示例：

```yaml
# bmad-product-brief/SKILL.md
description: Create or update product briefs through guided or autonomous 
discovery. Use when the user requests to create or update a Product Brief.

# bmad-create-prd/SKILL.md
description: Create a PRD from scratch. Use when the user says "lets create 
a product requirements document" or "I want to create a new PRD"

# bmad-domain-research/SKILL.md
description: Conduct comprehensive domain research to identify market trends, 
competitive landscape, and emerging opportunities.
```

**特点**：
- 包含明确的触发条件（"Use when..."）
- 包含关键动词（Create, Research, Review, Validate）
- 相对简洁（1-2 句）
- 使用用户可能的自然语言表述

---

## 3. 当前 Agent 实现分析

### 3.1 IndependentAgent 的 LLM 调用方式

#### 3.1.1 调用流程

根据 `autoBMAD/docuswarm/agents/independent.py` 的实现：

```python
async def _call_llm_with_prompts(
    self,
    system_prompt_append: str,      # Layers 2+3+4 (Persona + Task + Skills)
    user_prompt: str,
    timeout: int = 300,
) -> list[dict[str, Any]]:
    """
    使用 Four-Layer Architecture 调用 LLM (Story 29.6)
    
    当前实现：
    1. 创建 SessionManager.create_session()
    2. 通过 session.prompt() 发送提示
    3. 收集所有返回消息
    """
    session = await sm.create_session(
        mode="agent",                          # 自动工具使用
        yolo=True,                             # 自动批准工具调用
        agent_file=self._agent_file,
        system_prompt=system_prompt_append,    # Layers 2+3+4
    )
    
    async for msg in session.prompt(user_prompt, timeout=timeout):
        messages.append(msg)
    
    return messages
```

#### 3.1.2 ClaudeAgentOptions 当前使用

在 `SessionManager._create_options()` 中（lines 171-260）：

```python
def _create_options(self, mode: str, yolo: bool) -> ClaudeAgentOptions:
    """构建 ClaudeAgentOptions"""
    
    options_dict = {
        "cwd": self._cwd,                      # L178: 指向项目根目录
        "permission_mode": "bypassPermissions" if yolo else "default",
        # ... MCP 服务器和 allowed_tools 配置 ...
    }
    
    if system_prompt:
        options.system_prompt = {
            "type": "preset",
            "preset": "claude_code",
            "append": system_prompt_append,    # 层次 2+3+4
        }
```

**当前问题**：
- `setting_sources` 未配置，Skills 自动发现机制未启用
- `"Skill"` 未添加到 `allowed_tools`，Claude 无法触发任何技能

### 3.2 工具配置和加载机制

#### 3.2.1 当前工具注册流程

```
node.yaml 中的工具配置
    ↓
NodeLoader._build_node_config()          # autoBMAD/nodes/loader.py
    ↓
NodeConfig.tool_permissions (NodeToolPermissions)
    ↓
SessionManager.create_session(node_id, tool_permissions)
    ↓
NodeToolFilter.create_mcp_servers()      # autoBMAD/docuswarm/llm/tool_filter.py
    ↓
ClaudeAgentOptions.mcp_servers           # 注册 MCP 服务器
ClaudeAgentOptions.allowed_tools         # 构建工具名列表
```

#### 3.2.2 node.yaml 中的工具配置示例

```yaml
# nodes/analyst/node.yaml
tools:
  allowed_builtin_tools:
    - "Read"
    - "Glob"
  file_permissions:
    allowed_read_dirs:
      - "docs/"
      - "docs/research/"
  search_permissions:
    search_dirs:
      - "docs/"
  # 注意：当前版本中没有 skills 配置
```

**现状**：
- 内置工具（Read, Glob）已配置
- MCP 工具（文件读取、搜索）已实现
- **Skills 配置缺失**：node.yaml 中没有 skills 相关字段

---

## 4. Skills 引入方案设计

基于前面的分析，提出三种主要方案，对标的是如何在 DocuSwarm 中启用 Claude Agent SDK 的原生 Skills 机制。

### 4.1 方案 A: 通过 SDK setting_sources 原生引入（推荐）

#### 4.1.1 方案设计

在 `SessionManager._create_options()` 中启用 `setting_sources` 和 `"Skill"` 工具：

```python
def _create_options(self, mode: str, yolo: bool) -> ClaudeAgentOptions:
    options_dict = {
        "cwd": self._cwd,
        "permission_mode": "bypassPermissions" if yolo else "default",
        
        # ← 新增：启用 SDK 原生 Skills 机制
        "setting_sources": ["project"],  # 加载 .claude/skills/
        
        # ← 更新：添加 "Skill" 工具
        "allowed_tools": self._build_allowed_tools(),
    }
    
    # ... 其他配置 ...
    return ClaudeAgentOptions(**options_dict)

def _build_allowed_tools(self) -> list[str]:
    """构建允许的工具列表，包括 Skills 和 MCP 工具"""
    tools = ["Skill"]  # ← 启用 SDK 原生 Skills
    tools.extend(self._get_mcp_tools())
    tools.extend(self._get_builtin_tools())
    return tools
```

#### 4.1.2 node.yaml 扩展

```yaml
# nodes/analyst/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/", "docs/research/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  # 新增：Skills 配置
  skills:
    # 模式选择：
    # - "auto"：SDK 自动发现所有 .claude/skills/
    # - "whitelist"：仅启用指定的技能
    mode: "whitelist"                    # 默认：whitelist（更安全）
    
    enabled_skills:
      - bmad-agent-analyst
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
      # 注意：不包括 bmad-create-prd, bmad-product-brief 
      # （这些是 PM/PO 节点的工作）
```

#### 4.1.3 优势

| 优势 | 说明 |
|------|------|
| **充分利用 SDK 能力** | 使用官方提供的 Skills 自动发现机制 |
| **架构一致性** | 与 SDK 的设计理念一致，无需自定义逻辑 |
| **按需加载** | SDK 自动实现 Skills 内容的延迟加载，节省上下文 |
| **自动索引** | SDK 自动维护技能索引，Claude 能准确决策 |
| **配置清晰** | 在 node.yaml 中明确声明节点可用的技能 |
| **安全隔离** | 可按节点限制技能可用性，防止误用 |

#### 4.1.4 劣势

| 劣势 | 说明 |
|------|------|
| **功能受限** | SDK 的 Skills 机制相对简单，无法实现复杂的条件逻辑 |
| **配置灵活性** | 难以对单个技能进行细粒度配置（如参数约束、前置条件） |
| **迁移成本** | 需要调整现有的 System Prompt 注入逻辑 |

### 4.2 方案 B: 通过 System Prompt 注入技能内容（传统方式）

#### 4.2.1 方案设计

保持现有的手工系统 prompt 注入方式，但改进元数据管理：

```python
# autoBMAD/docuswarm/prompts/skill_injector.py （新增）

class SkillInjector:
    """从 .claude/skills/ 中提取技能内容并注入到 system prompt"""
    
    @staticmethod
    def build_skills_section(
        node_id: str,
        enabled_skills: list[str] | None = None,
        project_root: Path | None = None
    ) -> str:
        """构建技能注入部分（作为 Layer 4）"""
        project_root = project_root or Path.cwd()
        skills_dir = project_root / ".claude" / "skills"
        
        if not skills_dir.exists():
            return ""
        
        skills_content = []
        
        for skill_name in enabled_skills or []:
            skill_path = skills_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                content = skill_path.read_text(encoding="utf-8")
                # 提取元数据后的内容
                skills_content.append(f"## {skill_name}\n\n{content}")
        
        return "\n\n---\n\n".join(skills_content) if skills_content else ""

# 在 IndependentAgent._call_llm_with_prompts() 中使用
system_prompt_append = "\n\n".join([
    persona_section,                    # Layer 2
    task_section,                       # Layer 3
    SkillInjector.build_skills_section(self.node_id, enabled_skills),  # Layer 4
])
```

#### 4.2.2 node.yaml 配置

```yaml
# nodes/analyst/node.yaml
tools:
  # ... 其他工具配置 ...
  skills:
    mode: "manual"                     # 手工系统 prompt 注入
    enabled_skills:
      - bmad-agent-analyst
      - bmad-domain-research
      - bmad-market-research
```

#### 4.2.3 优势

| 优势 | 说明 |
|------|------|
| **完全控制** | 可精确控制每个技能的呈现形式和顺序 |
| **灵活定制** | 可添加节点特定的技能变体或上下文 |
| **兼容性强** | 不依赖 SDK 的 Skills 机制，自主实现 |
| **调试简便** | 技能内容在 system prompt 中完全可见 |

#### 4.2.4 劣势

| 劣势 | 说明 |
|------|------|
| **上下文浪费** | 所有技能内容预加载到 system prompt，无法延迟加载 |
| **维护复杂** | 需自行管理技能索引、版本控制、重复检测 |
| **性能问题** | 上下文占用大（每个技能可能 500-1000 tokens） |
| **架构冗余** | SDK 已提供的功能被忽视，重复开发 |

### 4.3 方案 C: 混合方案（最优平衡）

#### 4.3.1 方案设计

结合方案 A 和 B 的优势：

1. **核心层**：使用 SDK 原生 `setting_sources` + `"Skill"` 工具启用 Skills 自动发现
2. **增强层**：在系统 prompt 中额外注入"快速参考"（技能名称 + 关键特性）
3. **配置层**：在 node.yaml 中精确控制节点可用的技能子集

```python
# 改进的 SessionManager._create_options()

def _create_options(self, mode: str, yolo: bool) -> ClaudeAgentOptions:
    options_dict = {
        "cwd": self._cwd,
        "permission_mode": "bypassPermissions" if yolo else "default",
        
        # ← 层级 1：启用 SDK 原生 Skills 机制（自动发现 + 延迟加载）
        "setting_sources": ["project"],
        
        # ← 层级 2：添加 Skill 工具
        "allowed_tools": self._build_allowed_tools(),
    }
    
    # ← 层级 3：在 system prompt 中添加技能快速参考
    if system_prompt:
        skills_quick_ref = self._build_skills_quick_reference(node_id)
        options.system_prompt = {
            "type": "preset",
            "preset": "claude_code",
            "append": system_prompt_append + "\n\n" + skills_quick_ref,
        }

def _build_skills_quick_reference(self, node_id: str) -> str:
    """构建技能快速参考（仅名称 + 简短描述，无完整内容）"""
    return """
## Available Skills

You have access to the following BMAD skills:
- bmad-agent-analyst: Conduct comprehensive domain and market analysis
- bmad-domain-research: Deep-dive research into specific domains
- ... (其他技能列表)

To use a skill, mention it by name and describe your intent.
The system will automatically load the full skill definition.
"""
```

#### 4.3.2 node.yaml 配置

```yaml
# nodes/analyst/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/", "docs/research/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  skills:
    # 启用 SDK 原生机制
    sdk_native: true                   # ← 使用 setting_sources + allowed_tools["Skill"]
    
    # 允许的技能子集（过滤层）
    whitelist:
      - bmad-agent-analyst
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
    
    # 快速参考配置
    quick_reference:
      enabled: true                    # 在 system prompt 中显示技能列表
      include_descriptions: true       # 包含简短描述
```

#### 4.3.3 优势

| 优势 | 说明 |
|------|------|
| **最佳性能** | 结合了自动发现的延迟加载和快速参考的便利性 |
| **充分利用 SDK** | 用好官方提供的 Skills 机制 |
| **用户友好** | Claude 能看到可用的技能列表，快速定位 |
| **安全隔离** | node.yaml 中的 whitelist 防止越权使用技能 |
| **可扩展** | 可逐步过渡到完全的 SDK 原生方式 |

#### 4.3.4 劣势

| 劣势 | 说明 |
|------|------|
| **实现复杂** | 需要同时处理 SDK 机制和快速参考逻辑 |
| **维护成本** | 需维护快速参考的准确性和一致性 |

### 4.4 方案对比表

| 维度 | 方案 A（SDK 原生） | 方案 B（系统 Prompt） | 方案 C（混合）|
|------|------------------|------------------|------------|
| **充分利用 SDK** | ✅ 完全 | ❌ 忽视 | ✅ 充分 |
| **上下文效率** | ✅ 最佳（延迟加载） | ❌ 差（预加载） | ✅ 很好 |
| **配置灵活性** | ⚠️ 中等 | ✅ 最高 | ✅ 高 |
| **实现复杂度** | ✅ 低 | ⚠️ 中等 | ⚠️ 中高 |
| **安全隔离** | ✅ 好 | ✅ 好 | ✅✅ 最好 |
| **错误恢复** | ⚠️ 依赖 SDK | ✅ 自主控制 | ✅ 两者兼备 |
| **未来可维护性** | ✅ 高（标准方案） | ⚠️ 中 | ✅ 高 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 5. 推荐方案详细设计：方案 C（混合方案）

### 5.1 核心设计原则

1. **渐进迁移**：逐步过渡到 SDK 原生方式，现阶段采用混合策略
2. **向后兼容**：现有的系统 prompt 注入逻辑继续工作，无需大改
3. **安全第一**：通过 node.yaml 中的 whitelist 严格控制技能可用性
4. **性能优先**：利用 SDK 的延迟加载减少上下文占用

### 5.2 需要修改的文件列表

| 文件 | 变更类型 | 优先级 | 说明 |
|------|--------|--------|------|
| `autoBMAD/nodes/loader.py` | 扩展 | P0 | 在 NodeToolPermissions 中添加 skills 配置 |
| `nodes/{node_id}/node.yaml` | 新增 | P0 | 在 tools 块中添加 skills 配置（5 个节点） |
| `autoBMAD/docuswarm/llm/session_manager.py` | 更新 | P0 | 启用 setting_sources 和 "Skill" 工具 |
| `autoBMAD/docuswarm/prompts/skill_injector.py` | 新增 | P1 | 新增技能快速参考构建器 |
| `autoBMAD/docuswarm/agents/independent.py` | 更新 | P1 | 集成技能快速参考到系统 prompt |
| `tests/test_skills_integration.py` | 新增 | P1 | 添加集成测试 |

### 5.3 关键代码改动

#### 5.3.1 扩展 NodeToolPermissions（loader.py）

```python
# autoBMAD/nodes/loader.py

from dataclasses import dataclass, field
from typing import Any

@dataclass
class NodeSkillsConfig:
    """节点 Skills 配置"""
    
    # 是否启用 SDK 原生 Skills 机制
    sdk_native: bool = True
    
    # 允许的技能白名单
    # 如果为空列表，表示不允许任何技能
    whitelist: list[str] = field(default_factory=list)
    
    # 快速参考配置
    quick_reference_enabled: bool = True
    quick_reference_include_descriptions: bool = True

# 在现有 NodeToolPermissions 中添加
@dataclass
class NodeToolPermissions:
    """Complete tool permissions configuration for a node."""
    allowed_builtin_tools: list[str] = field(default_factory=list)
    file_permissions: NodeFilePermissions = field(default_factory=NodeFilePermissions)
    search_permissions: NodeSearchPermissions = field(default_factory=NodeSearchPermissions)
    
    # ← 新增：Skills 配置
    skills: NodeSkillsConfig = field(default_factory=NodeSkillsConfig)
```

在 NodeLoader._build_node_config() 中解析 skills 部分：

```python
# 在 _build_node_config() 中添加

# Build tool permissions config (optional, backward compatible)
tools_data = config.get("tools", {})
if tools_data:
    # ... 现有文件和搜索权限解析代码 ...
    
    # ← 新增：解析 skills 配置
    skills_data = tools_data.get("skills", {})
    skills_config = NodeSkillsConfig(
        sdk_native=skills_data.get("sdk_native", True),
        whitelist=skills_data.get("whitelist", []),
        quick_reference_enabled=skills_data.get("quick_reference_enabled", True),
        quick_reference_include_descriptions=skills_data.get("quick_reference_include_descriptions", True),
    )
    
    tool_permissions_config = NodeToolPermissions(
        allowed_builtin_tools=tools_data.get("allowed_builtin_tools", []),
        file_permissions=NodeFilePermissions(...),
        search_permissions=NodeSearchPermissions(...),
        skills=skills_config,                # ← 添加到配置中
    )
```

#### 5.3.2 node.yaml 配置示例（5 个节点）

```yaml
# nodes/analyst/node.yaml
node_id: analyst
name: Analyst
# ... 其他配置 ...

tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/", "docs/research/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  # ← 新增：Skills 配置
  skills:
    sdk_native: true
    whitelist:
      - bmad-agent-analyst
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
    quick_reference_enabled: true
    quick_reference_include_descriptions: true

---

# nodes/pm/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  skills:
    sdk_native: true
    whitelist:
      - bmad-create-prd
      - bmad-edit-prd
      - bmad-validate-prd
      - bmad-advanced-elicitation
    quick_reference_enabled: true

---

# nodes/ux/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  skills:
    sdk_native: true
    whitelist:
      - bmad-create-ux-design
      - bmad-advanced-elicitation
    quick_reference_enabled: true

---

# nodes/architect/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  skills:
    sdk_native: true
    whitelist:
      - bmad-create-architecture
      - bmad-technical-research
      - bmad-advanced-elicitation
    quick_reference_enabled: true

---

# nodes/po/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/"]
  search_permissions:
    search_dirs: ["docs/"]
  
  skills:
    sdk_native: true
    whitelist:
      - bmad-validate-prd
      - bmad-sprint-planning
    quick_reference_enabled: true
```

#### 5.3.3 SessionManager 中启用 SDK Skills（session_manager.py）

```python
# autoBMAD/docuswarm/llm/session_manager.py

def _create_options(self, mode: str, yolo: bool) -> ClaudeAgentOptions:
    """Create ClaudeAgentOptions with SDK native Skills support"""
    
    options_dict: dict[str, Any] = {
        "cwd": self._cwd,
        "permission_mode": "bypassPermissions" if yolo else "default",
    }
    
    # ← 新增：启用 SDK 原生 Skills 机制
    # 关键：这启用了 .claude/skills/ 的自动发现
    options_dict["setting_sources"] = ["project"]
    
    # ... 其他配置代码 ...
    
    # ← 更新：构建 allowed_tools，包括 "Skill"
    allowed_tools = self._build_allowed_tools()
    if allowed_tools:
        options_dict["allowed_tools"] = allowed_tools
    
    # ... 继续其他配置 ...
    return ClaudeAgentOptions(**options_dict)

def _build_allowed_tools(self) -> list[str]:
    """构建完整的允许工具列表"""
    tools = []
    
    # ← 新增：添加 SDK 原生 Skill 工具
    tools.append("Skill")
    
    # 添加现有的 MCP 工具
    mcp_tools = self._get_mcp_tools()
    if mcp_tools:
        tools.extend(mcp_tools)
    
    # 添加内置工具
    builtin_tools = self._get_builtin_tools()
    if builtin_tools:
        tools.extend(builtin_tools)
    
    return tools

def _get_builtin_tools(self) -> list[str]:
    """获取允许的内置工具（从工具权限中）"""
    if self._tool_permissions:
        return self._tool_permissions.allowed_builtin_tools
    return []
```

#### 5.3.4 技能快速参考构建器（新增文件）

```python
# autoBMAD/docuswarm/prompts/skill_injector.py （新增）

from pathlib import Path
from typing import Any
import structlog

logger = structlog.get_logger(__name__)

class SkillInjector:
    """提取和注入 BMAD 技能的快速参考"""
    
    @staticmethod
    def build_skills_quick_reference(
        node_id: str,
        node_skill_config: Any,  # NodeSkillsConfig
        project_root: Path | None = None,
    ) -> str:
        """
        构建技能快速参考部分（插入 Layer 4）
        
        Args:
            node_id: 节点 ID
            node_skill_config: 节点的 Skills 配置对象
            project_root: 项目根目录
        
        Returns:
            技能快速参考的 Markdown 文本
        """
        if not node_skill_config.quick_reference_enabled:
            return ""
        
        project_root = project_root or Path.cwd()
        skills_dir = project_root / ".claude" / "skills"
        
        if not skills_dir.exists():
            logger.warning("skills_dir_not_found", skills_dir=str(skills_dir))
            return ""
        
        # 获取该节点允许的技能列表
        whitelist = node_skill_config.whitelist
        if not whitelist:
            logger.info("node_has_no_skills", node_id=node_id)
            return ""
        
        # 构建参考文本
        reference_lines = ["## Available BMAD Skills"]
        reference_lines.append("")
        reference_lines.append("You have access to the following BMAD skills:")
        reference_lines.append("")
        
        for skill_name in whitelist:
            skill_path = skills_dir / skill_name / "SKILL.md"
            
            if not skill_path.exists():
                logger.warning("skill_file_not_found", skill_name=skill_name, skill_path=str(skill_path))
                reference_lines.append(f"- {skill_name} (definition not found)")
                continue
            
            # 提取元数据
            try:
                content = skill_path.read_text(encoding="utf-8")
                description = SkillInjector._extract_description(content, skill_name)
                
                if node_skill_config.quick_reference_include_descriptions and description:
                    reference_lines.append(f"- **{skill_name}**: {description}")
                else:
                    reference_lines.append(f"- {skill_name}")
                    
            except Exception as e:
                logger.error("failed_to_extract_skill_metadata", skill_name=skill_name, error=str(e))
                reference_lines.append(f"- {skill_name}")
        
        reference_lines.append("")
        reference_lines.append("To use a skill, mention its name in your response or explicitly")
        reference_lines.append("request to use it for a specific task. The system will automatically")
        reference_lines.append("load the full skill definition.")
        
        return "\n".join(reference_lines)
    
    @staticmethod
    def _extract_description(skill_md_content: str, skill_name: str) -> str:
        """从 SKILL.md 的 YAML 前置元数据中提取 description 字段"""
        import re
        import yaml
        
        # 提取 YAML 前置元数据
        pattern = r"^---\n(.*?)\n---"
        match = re.match(pattern, skill_md_content, re.DOTALL)
        
        if not match:
            return f"Skill: {skill_name}"
        
        try:
            metadata = yaml.safe_load(match.group(1))
            description = metadata.get("description", f"Skill: {skill_name}")
            
            # 去除多余换行和空格
            description = " ".join(description.split())
            
            # 限制长度（避免 quick reference 过长）
            if len(description) > 150:
                description = description[:147] + "..."
            
            return description
        except Exception:
            return f"Skill: {skill_name}"
```

#### 5.3.5 独立 Agent 中集成快速参考（independent.py）

```python
# autoBMAD/docuswarm/agents/independent.py

async def _call_llm_with_prompts(
    self,
    system_prompt_append: str,
    user_prompt: str,
    timeout: int = 300,
) -> list[dict[str, Any]]:
    """Call LLM with Four-Layer Architecture (Story 29.6 + Skills)"""
    
    # ← 新增：构建技能快速参考
    from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector
    
    node_config = NodeLoader.load(self.node_id)
    skills_quick_ref = SkillInjector.build_skills_quick_reference(
        node_id=self.node_id,
        node_skill_config=node_config.tool_permissions.skills,
        project_root=self.project_root,
    )
    
    # ← 更新：将快速参考附加到系统 prompt
    if skills_quick_ref:
        system_prompt_append = system_prompt_append + "\n\n" + skills_quick_ref
    
    # ... 继续现有的 LLM 调用逻辑 ...
    session = await sm.create_session(
        mode="agent",
        yolo=True,
        system_prompt=system_prompt_append,
    )
    
    # ... 收集消息并返回 ...
```

### 5.4 集成验证步骤

#### 5.4.1 单元测试用例

```python
# tests/test_skills_integration.py

import pytest
from pathlib import Path
from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector
from autoBMAD.nodes.loader import NodeSkillsConfig, NodeLoader

def test_skill_injector_builds_quick_reference():
    """测试技能快速参考构建器"""
    config = NodeSkillsConfig(
        sdk_native=True,
        whitelist=["bmad-domain-research", "bmad-market-research"],
        quick_reference_enabled=True,
    )
    
    reference = SkillInjector.build_skills_quick_reference(
        node_id="analyst",
        node_skill_config=config,
        project_root=Path("/path/to/project"),
    )
    
    assert "Available BMAD Skills" in reference
    assert "bmad-domain-research" in reference
    assert "bmad-market-research" in reference

def test_node_config_loads_skills():
    """测试 node.yaml 中的 skills 配置加载"""
    node_config = NodeLoader.load("analyst")
    
    assert node_config.tool_permissions.skills.sdk_native is True
    assert "bmad-agent-analyst" in node_config.tool_permissions.skills.whitelist

def test_session_manager_enables_skill_tool():
    """测试 SessionManager 启用 Skill 工具"""
    from autoBMAD.docuswarm.llm.session_manager import SessionManager
    
    session_manager = SessionManager()
    options = session_manager._create_options(mode="agent", yolo=True)
    
    # 验证启用了 setting_sources
    assert options.setting_sources == ["project"]
    
    # 验证 allowed_tools 包含 "Skill"
    assert "Skill" in options.allowed_tools
```

#### 5.4.2 集成测试

```python
def test_independent_agent_with_skills():
    """端到端：独立 Agent 与 Skills 集成"""
    # 1. 加载节点配置
    node_config = NodeLoader.load("analyst")
    
    # 2. 创建 session manager
    session_manager = SessionManager(
        work_dir=Path("/tmp/test"),
        node_id="analyst",
        tool_permissions=node_config.tool_permissions,
    )
    
    # 3. 创建独立 Agent
    agent = IndependentAgent(
        config=AgentConfig(),
        session_manager=session_manager,
        node_id="analyst",
        project_root=Path("/path/to/project"),
    )
    
    # 4. 验证系统 prompt 包含技能快速参考
    system_prompt = agent._format_system_prompt()
    assert "Available BMAD Skills" in system_prompt
    assert "bmad-domain-research" in system_prompt
```

---

## 6. 风险评估

### 6.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|--------|
| SDK `setting_sources` 加载失败 | 中 | 高 | 1. 验证 cwd 指向正确的项目根目录 2. 检查 `.claude/skills/` 目录结构 3. 添加 fallback 到系统 prompt 注入 |
| Skills 索引过大导致上下文溢出 | 中 | 高 | 1. 实施 whitelist 机制严格限制技能数量 2. 监控 SDK 的索引大小 3. 使用快速参考代替完整内容 |
| Claude 不准确地选择技能 | 中 | 中 | 1. 优化 SKILL.md 中的 description 字段 2. 在快速参考中添加使用场景提示 3. 定期审计技能使用日志 |
| 性能下降（多技能加载） | 低 | 中 | 1. 限制每个节点的技能数量（≤10 个） 2. 缓存技能索引 3. 定期性能测试 |

### 6.2 运维风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|--------|
| 技能定义不一致 | 低 | 中 | 1. 建立 SKILL.md 的模板和规范 2. 添加自动验证脚本 3. Code Review 前检查 |
| node.yaml 配置错误 | 中 | 中 | 1. Schema 验证（Pydantic） 2. 提供清晰的错误信息 3. 文档和示例 |
| 新增技能被遗漏 | 低 | 低 | 1. 自动化发现未在任何 node.yaml 中使用的技能 2. 定期审计技能库 |

### 6.3 兼容性风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|--------|
| 现有系统 prompt 冲突 | 低 | 高 | 1. 保持向后兼容，旧的注入方式继续工作 2. 逐步迁移，不一次性切换 3. 完整的集成测试 |
| SDK 版本升级导致 API 变化 | 低 | 高 | 1. 监控 SDK changelog 2. 维护兼容性 wrapper 3. 单元测试覆盖 SDK 调用 |

---

## 7. 实施路线图

### Phase 1: 基础设施（1-2 天）

**目标**：完成代码层面的实现和测试

**步骤**：
1. 扩展 `NodeToolPermissions` 和 `NodeSkillsConfig` 数据类
2. 在 `NodeLoader` 中实现 YAML 解析
3. 实现 `SkillInjector` 类
4. 更新 `SessionManager._create_options()` 启用 SDK Skills

**输出**：
- 更新的 `loader.py`
- 新增的 `skill_injector.py`
- 更新的 `session_manager.py`
- 基础单元测试

**验证标准**：
- 单元测试全部通过
- 基本功能验证（配置加载、快速参考生成）

### Phase 2: 配置迁移（1 天）

**目标**：更新所有 node.yaml 文件和独立 Agent

**步骤**：
1. 为 5 个节点的 `node.yaml` 添加 `tools.skills` 配置
2. 在 `IndependentAgent` 中集成技能快速参考
3. 完成集成测试

**输出**：
- 5 个节点的更新 node.yaml
- 更新的 `independent.py`
- 集成测试用例

**验证标准**：
- 所有节点配置有效
- 快速参考成功注入系统 prompt
- 端到端集成测试通过

### Phase 3: 验证和优化（1 天）

**目标**：性能测试、文档编写和问题修复

**步骤**：
1. 性能测试（上下文占用、加载时间）
2. 安全审计（技能白名单隔离）
3. 文档编写和示例
4. Bug 修复

**输出**：
- 性能报告
- 使用文档
- 常见问题解答

**验证标准**：
- 性能指标达到预期
- 文档完整清晰
- 无关键 Bug

### Phase 4: 部署和监控（1 天）

**目标**：灰度部署和关键指标监控

**步骤**：
1. 灰度部署（先在 test 环境）
2. 设置关键指标监控（Skills 调用成功率、上下文占用等）
3. 收集反馈
4. 全量部署

**输出**：
- 部署文档
- 监控仪表板
- 运维手册

**总计工时**：约 4 天

---

## 8. 总结与建议

### 8.1 推荐选择

基于前面的深度分析，**强烈推荐采用方案 C（混合方案）**，理由如下：

1. **充分利用 SDK 能力**：通过 `setting_sources` + `allowed_tools["Skill"]` 启用原生 Skills 机制，充分利用自动发现和延迟加载的优势
2. **保持向后兼容**：现有的系统 prompt 注入逻辑继续工作，无需大规模重构
3. **安全隔离**：通过 node.yaml 中的 whitelist 严格控制技能可用性
4. **最优性能**：结合 SDK 的自动发现和本地的快速参考，在上下文效率和用户体验之间找到平衡
5. **渐进迁移**：为未来完全过渡到 SDK 原生方式预留空间

### 8.2 关键成功因素

1. **SKILL.md 质量**：确保所有 SKILL.md 的 `description` 字段准确、简洁、包含关键词
2. **node.yaml 配置精准**：每个节点的 skills.whitelist 要根据其职能精选，不要过度授权
3. **监控和告警**：实施关键指标监控（Skills 调用成功率、Claude 选择错误率等），及时发现问题
4. **文档和培训**：为开发者提供清晰的文档，说明如何创建新 Skill 和如何为节点添加 Skill

### 8.3 后续优化方向

#### 短期（1-3 个月）

- [ ] 完善 SKILL.md 的元数据（description 优化、关键词标注）
- [ ] 建立 SKILL.md 的编写规范和模板
- [ ] 实施自动验证脚本检查 Skills 定义的有效性
- [ ] 添加使用日志和分析（哪些 Skills 被频繁使用、误用情况）

#### 中期（3-6 个月）

- [ ] 实施 Skills 版本管理机制（支持多版本共存）
- [ ] 开发 Skills 管理工具（创建、编辑、发布、版本控制）
- [ ] 集成 Skills 性能基准测试
- [ ] 支持动态技能注入（运行时添加/移除技能）

#### 长期（6+ 个月）

- [ ] 完全迁移到 SDK 原生 Skills 方式（移除手工 prompt 注入）
- [ ] 实施 Skills 推荐系统（根据任务上下文推荐最相关的 Skills）
- [ ] 支持 Skills 链接（一个 Skill 调用另一个 Skill）
- [ ] 社区 Skills 库（与其他 BMAD 项目共享 Skills）

---

## 9. 附录：技术参考

### 9.1 SDK Skills 官方文档引用

- **SDK Skills 主文档**：`autoBMAD/agentdocs/22_skills.md`（本研究中的主要依据）
- **Python SDK 参考**：`autoBMAD/agentdocs/05_python.md`（ClaudeAgentOptions 定义）
- **自定义工具指南**：`autoBMAD/agentdocs/19_custom_tools.md`（MCP 工具扩展）
- **MCP 工具集成**：`autoBMAD/agentdocs/18_mcp.md`（MCP 服务器配置）

### 9.2 当前实现参考

- **Four-Layer Architecture**：`docs/stories/29.6.md`（系统 prompt 分层架构）
- **EPIC-29**：`docs/epics/EPIC-29-SDK-Capability-Activation.md`（SDK 能力激活）
- **节点配置改革**：`docs/research/refactor-2026-03-26/05-claude-agent-sdk-reform.md`（工具权限系统）

### 9.3 现有 Skills 示例

项目中已存在 50+ 个 BMAD Skills，主要分类：

| 分类 | 技能示例 | 数量 |
|------|--------|------|
| 代理技能 | bmad-agent-analyst, bmad-agent-pm, bmad-agent-ux | 6 |
| 文档创建 | bmad-create-prd, bmad-create-architecture, bmad-create-story | 15 |
| 研究技能 | bmad-domain-research, bmad-market-research, bmad-technical-research | 8 |
| 审查技能 | bmad-code-review, bmad-editorial-review-prose, bmad-validate-prd | 10 |
| 流程技能 | bmad-sprint-planning, bmad-retrospective, bmad-party-mode | 8 |
| 其他 | bmad-help, bmad-init, bmad-distillator | 5+ |

---

**报告完成日期**：2026-04-06  
**审查状态**：待批准  
**后续行动**：实施路线图第 Phase 1

