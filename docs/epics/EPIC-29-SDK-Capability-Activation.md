# Epic 29: SDK 能力激活

**Epic ID**: EPIC-29  
**关联方案**: [05-claude-agent-sdk-reform.md](../research/refactor-2026-03-26/05-claude-agent-sdk-reform.md)  
**Version**: 1.0  
**Date**: 2026-03-26  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 5-6 Days  
**Priority**: P1 - Phase 4 能力增强  

---

## 1. Epic Overview

### 1.1 Summary

激活 Claude Agent SDK 当前未使用的核心能力：(1) 通过 MCP 工具注册文件读取和搜索工具，使各节点 Agent 按权限访问项目文档；(2) 将 47 个 BMAD 斜杠命令中的核心命令注入各节点 system_prompt；(3) 将提示词架构从扁平字符串拼接重构为四层分层结构（preset + persona + task + skills）。**不保留旧版 `_call_llm_via_session` 作为 fallback**，直接替换为新架构。

### 1.2 Business Value

- **文档引用能力**: Agent 可主动读取已授权文件，输出质量从"依赖 context 注入"提升为"主动引用"
- **搜索能力**: 按节点配置限定范围的 grep/glob 搜索
- **BMAD 技能利用**: 核心 BMAD 命令注入后，Agent 输出可参考标准化工作流框架
- **提示词语义分离**: system_prompt 和 user_prompt 分离传递，Claude 正确区分身份指令和任务内容
- **SDK 能力实现率**: 从 58.3%（7/12）提升至 83%+（10/12）

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| SDK 总体能力实现率 | ≥ 10/12（83%+） |
| `ClaudeAgentOptions` 字段使用率 | ≥ 8/17（47%+，从 23.5%） |
| BMAD 命令利用率 | ≥ 5/47（核心命令全覆盖） |
| 文件读取工具覆盖节点数 | 5/5 |
| system_prompt 含 BMAD 技能标记 | 5/5 |
| persona 不出现在 user_prompt 中 | 5/5 |

### 1.4 Dependencies

- **Requires**: EPIC-26（node.yaml v2 提供 `tools` 配置块）、EPIC-28（Task 契约消除后 task 信息从 NodeConfig 读取）
- **Blocks**: EPIC-30（集成验证含 SDK 功能测试）

---

## 2. Architecture Context

### 2.1 Component Overview

```
四层 System Prompt 架构:
  ┌─────────────────────────────────────────────────┐
  │ Layer 1: claude_code preset（工具说明、安全指令） │  ← SDK 内置
  ├─────────────────────────────────────────────────┤
  │ Layer 2: Persona（角色身份、专业领域、行为准则）  │  ← persona.json
  ├─────────────────────────────────────────────────┤
  │ Layer 3: Task Context（任务名、交付物要求）       │  ← node.yaml task{}
  ├─────────────────────────────────────────────────┤
  │ Layer 4: Skill Injection（BMAD 命令描述）         │  ← .claude/skills/
  └─────────────────────────────────────────────────┘

工具权限体系:
  node.yaml → tools:
    ├── allowed_builtin_tools: [Read, Glob]
    ├── file_permissions:
    │     └── allowed_read_dirs: [docs/, docs/research/]
    ├── search_permissions:
    │     └── search_dirs: [docs/]
    └── skills:
          └── commands: [bmad-agent-analyst, bmad-domain-research, ...]
```

### 2.2 Key Files

| File | Action | Purpose |
|------|--------|---------|
| `autoBMAD/docuswarm/tools/__init__.py` | **新建** | 工具模块初始化 |
| `autoBMAD/docuswarm/tools/file_tools.py` | **新建** | 文件读取 MCP 服务器（read_document, list_documents） |
| `autoBMAD/docuswarm/tools/search_tools.py` | **新建** | 搜索工具 MCP 服务器（grep_search, glob_search） |
| `autoBMAD/docuswarm/llm/tool_filter.py` | **新建** | NodeToolFilter 统一权限管理 |
| `autoBMAD/docuswarm/prompts/skill_injector.py` | **新建** | SkillInjector BMAD 技能注入器 |
| `autoBMAD/docuswarm/prompts/template_engine.py` | **新建** | PromptTemplateEngine 提示词模板引擎 |
| `autoBMAD/docuswarm/agents/independent.py` | **修改** | 四层 system_prompt 架构，删除旧 `full_prompt` 拼接 |
| `autoBMAD/docuswarm/llm/session_manager.py` | **修改** | 注册 MCP 服务器、新增 node_id/allowed_dirs 参数 |
| `autoBMAD/nodes/loader.py` | **修改** | 新增 NodeToolPermissions 数据类 |

---

## 3. User Stories

### Story 29.1: 文件读取 MCP 工具实现

**Story Points**: 3  
**Priority**: P0  
**Description**: As a node agent, I want to read project documents within my permission scope, so that I can produce higher quality output by directly referencing source materials.

**Acceptance Criteria**:

- [ ] `tools/file_tools.py` 实现 `create_file_read_server(allowed_dirs, node_id)`
- [ ] 提供 `read_document` 工具（路径白名单检查 + 内容返回）
- [ ] 提供 `list_documents` 工具（列出允许目录内的文件）
- [ ] 路径遍历防护：所有路径通过 `os.path.abspath()` 规范化后白名单前缀匹配
- [ ] 文件大小限制：单文件最大 50000 字符
- [ ] 越权访问返回明确的权限拒绝消息

---

### Story 29.2: 搜索工具 MCP 实现

**Story Points**: 3  
**Priority**: P0  
**Description**: As a node agent, I want to search document contents within my permission scope, so that I can find relevant information without reading entire files.

**Acceptance Criteria**:

- [ ] `tools/search_tools.py` 实现 `create_search_server(search_dirs, node_id)`
- [ ] 提供 `grep_search` 工具（正则搜索 + 权限检查 + 结果上限）
- [ ] 提供 `glob_search` 工具（文件路径匹配 + 权限检查）
- [ ] 搜索结果上限默认 20 条
- [ ] 正则表达式编译失败返回友好错误消息

---

### Story 29.3: 节点工具权限配置

**Story Points**: 2  
**Priority**: P0  
**Description**: As the system, I want each node's tool permissions defined in node.yaml, so that tool access is declarative and auditable.

**Acceptance Criteria**:

- [ ] `loader.py` 新增 `NodeToolPermissions` 数据类
- [ ] `NodeConfig` 新增 `tool_permissions: NodeToolPermissions` 字段
- [ ] 5 个节点的 `node.yaml` 均添加 `tools` 配置块
- [ ] 权限映射：analyst 仅读 `docs/`, `docs/research/`；po 可读 `docs/` 全部
- [ ] `llm/tool_filter.py` 实现 `NodeToolFilter`，从 `NodeToolPermissions` 构建 MCP 服务器和 allowed_tools 列表

---

### Story 29.4: SessionManager MCP 集成

**Story Points**: 2  
**Priority**: P0  
**Description**: As the session manager, I want to register node-specific MCP servers, so that file and search tools are available during agent execution.

**Acceptance Criteria**:

- [ ] `SessionManager.__init__` 新增 `node_id` 和 `allowed_dirs` 参数
- [ ] `_create_options` 中注册 MCP 服务器到 `ClaudeAgentOptions.mcp_servers`
- [ ] `allowed_tools` 包含 MCP 工具的完整命名（`mcp__docuswarm-files-{node_id}__read_document` 等）
- [ ] 所有工具仅在有 `node_id` 和权限配置时才注册

---

### Story 29.5: BMAD 技能注入器实现

**Story Points**: 3  
**Priority**: P0  
**Description**: As a node agent, I want relevant BMAD skill descriptions injected into my system prompt, so that I can leverage standardized workflow frameworks.

**Acceptance Criteria**:

- [ ] `prompts/skill_injector.py` 实现 `SkillInjector` 类
- [ ] 从 `.claude/skills/{command}/SKILL.md` 读取技能描述（前 300 字符）
- [ ] `NODE_SKILL_MAP` 定义 5 个节点各自的技能命令列表
- [ ] `build_skill_section(node_id)` 返回格式化的技能描述文本
- [ ] 技能注入文本包含 `## 可用 BMAD 技能` 标记
- [ ] analyst 注入 4 命令（agent-analyst, domain-research, market-research, advanced-elicitation）
- [ ] pm 注入 4 命令（agent-pm, create-prd, create-epics-and-stories, validate-prd）
- [ ] ux 注入 4 命令（agent-ux-designer, create-ux-design, advanced-elicitation, review-edge-case-hunter）
- [ ] architect 注入 5 命令（agent-architect, create-architecture, technical-research, review-adversarial-general, check-implementation-readiness）
- [ ] po 注入 5 命令（create-epics-and-stories, validate-prd, check-implementation-readiness, sprint-planning, distillator）

---

### Story 29.6: 提示词四层架构重构

**Story Points**: 5  
**Priority**: P0  
**Description**: As the agent system, I want the prompt architecture restructured into 4 layers, so that Claude correctly distinguishes identity instructions from task content.

**Acceptance Criteria**:

- [ ] `prompts/template_engine.py` 实现 `PromptTemplateEngine` 和 `PromptBuildConfig`
- [ ] `build_system_prompt_append` 组装 Layer 2（Persona）+ Layer 3（Task）+ Layer 4（Skills）
- [ ] `build_user_prompt` 仅包含纯任务内容（上下文、交付物、迭代反馈）
- [ ] `IndependentAgent._call_llm_with_prompts` 使用 `ClaudeAgentOptions(system_prompt={"type": "preset", "preset": "claude_code", "append": ...})`
- [ ] 旧实现 `full_prompt = f"{system_prompt}\n\n{user_prompt}"` **删除**
- [ ] 旧 `_call_llm_via_session` 方法**删除**（不保留 fallback）
- [ ] persona 内容不再出现在 user_prompt 中
- [ ] 总 system_prompt Token 预算 ≤ 3200 tokens

---

### Story 29.7: 安全验证测试

**Story Points**: 2  
**Priority**: P0  
**Description**: As a security engineer, I want path traversal and permission boundary tests, so that the tool system is provably secure.

**Acceptance Criteria**:

- [ ] 测试 `../` 路径遍历攻击被拒绝
- [ ] 测试白名单外目录访问被拒绝
- [ ] 测试 `.env`、`*.db` 等敏感文件被拒绝
- [ ] 测试超过 50000 字符的文件被截断
- [ ] 测试 analyst 无法访问 `docs/stories/`
- [ ] 测试 po 可以访问 `docs/` 全部

---

## 4. 质量门禁

```bash
python -m pytest tests/unit/tools/ -v
python tools/agent_sdk_capability_auditor.py
# 预期: 能力实现率 >= 10/12

# 验证 system_prompt 结构
python -c "
from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector
from pathlib import Path
si = SkillInjector(Path('.'))
section = si.build_skill_section('analyst')
assert '## 可用 BMAD 技能' in section
print('skill injection OK')
"
```
