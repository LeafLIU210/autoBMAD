# SDK MCP 迁移文档对齐总结

**日期**: 2026-04-05  
**迁移方案**: [Test-Driven SDK MCP Migration Plan](./test-driven-sdk-mcp-migration-plan.md)  
**研究文档**: 
- [FastMCP SDK 兼容性研究报告](../research/fastmcp-sdk-compatibility-issue.md)
- [SDK MCP 迁移方案 A](../research/sdk-mcp-migration-plan-a.md)

---

## 修改概述

根据 SDK MCP 迁移方案，已对以下文档进行对齐修改，确保文档与新的 SDK MCP 格式保持一致。

---

## 1. PRD (docs/prd.md)

### 修改内容

1. **Phase 3 更新**:
   - 更新 Out of Scope 中的 MCP 描述
   - 添加已完成 SDK MCP 迁移的说明

2. **新增 Phase 14 (P13)**:
   - 添加 SDK MCP 格式迁移作为独立 Phase
   - 包含详细的迁移范围、技术变更、工具命名约定
   - 包含验收标准和参考文档

### 关键变更

```markdown
| **Phase 14 (P13)** | **SDK MCP 格式迁移** | **[Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md)** - FastMCP → SDK MCP 迁移 | 🔴 **Critical** |
```

---

## 2. LLM Integration Architecture (docs/architecture/05_LLM_INTEGRATION.md)

### 修改内容

1. **SessionManager._create_options() 方法**:
   - 更新文档字符串，说明 SDK MCP 格式
   - 简化代码示例，直接使用 dict 赋值
   - 添加迁移说明注释

2. **新增 SDK MCP Migration 章节**:
   - 对比 FastMCP 和 SDK MCP 格式
   - 列出服务器名称、工具命名的变更
   - 提供 SDK MCP Server 结构示例

### 关键变更

```python
# SDK MCP Format: create_mcp_servers() returns dict[str, Any] (not list[FastMCP])
mcp_servers_dict = node_filter.create_mcp_servers()
options_dict["mcp_servers"] = mcp_servers_dict  # Direct assignment
```

---

## 3. System Architecture (docs/architecture/01_SYSTEM_ARCHITECTURE.md)

### 修改内容

1. **Integration Layer 更新**:
   - 更新 MCP Protocol Migration 状态为已完成

### 关键变更

```markdown
│  │  │  ~~Phase 2: MCP Protocol Migration~~ → SDK MCP 格式迁移完成 │  │   │
```

---

## 4. Agent Architecture (docs/architecture/02_AGENT_ARCHITECTURE.md)

### 修改内容

1. **文档末尾添加更新日志**:
   - 添加 2026-04-05 SDK MCP Migration Update
   - 列出 FastMCP 兼容性问题的解决
   - 说明 SDK MCP 格式变更要点

### 关键变更

```markdown
> **2026-04-05 SDK MCP Migration Update**: Agent 层 MCP 工具格式已从 FastMCP 迁移到 SDK MCP：
> - **FastMCP 兼容性问题解决**: `TypeError: Object of type FastMCP is not JSON serializable` 已修复
> - **SDK MCP 格式**: `create_mcp_servers()` 现在返回 `dict[str, Any]` (SDK MCP server dict)
```

---

## 5. Design README (docs/design/README.md)

### 修改内容

1. **MCP Server Key 命名规范更新**:
   - 添加 2026-04-05 Update 说明
   - 更新工具名格式为 SDK MCP 约定
   - 添加 FastMCP → SDK MCP 迁移要点表格

2. **新增 SDK MCP 工具实现示例**:
   - 提供完整的 `@tool` 装饰器示例
   - 展示 `create_sdk_mcp_server()` 用法

3. **新增 SDK MCP 迁移设计约束章节**:
   - 概述迁移背景和目标
   - 列出核心变更文件
   - 提供设计约束和验证清单

### 关键变更

```python
# allowed_tools 中的工具名格式 (SDK MCP 约定)
allowed_tools = [
    "Read",                                               # builtin
    "Glob",                                               # builtin
    f"mcp__docuswarm-files-{node_id}__read_document",     # MCP file (SDK format)
    f"mcp__docuswarm-search-{node_id}__grep_search",      # MCP search (SDK format)
]
```

---

## 6. Reference Docs Preload (docs/architecture/07_REFERENCE_DOCS_PRELOAD.md)

### 修改内容

1. **Problem Statement 更新**:
   - 标注 Before Step 2 的 MCP 工具调用为过时方式
   - 添加 SDK MCP 兼容性说明

### 关键变更

```markdown
**Before Step 2**:
- ~~Agent 需要通过 MCP 工具主动调用 `read_document` 读取引用文档~~
- ...

**After Step 2**:
- ...
- **SDK MCP 兼容**: 预加载机制与 SDK MCP 格式完全兼容
```

---

## 7. Tech Stack (docs/architecture/tech-stack.md)

### 修改内容

1. **MCP Protocol Note 更新**:
   - 说明已实现 SDK MCP 格式迁移
   - 添加 FastMCP JSON 序列化问题的引用

### 关键变更

```markdown
> **Note**: MCP Protocol 已实现 SDK MCP 格式迁移。FastMCP 格式导致 
> `TypeError: Object of type FastMCP is not JSON serializable`，现已迁移到 SDK MCP 格式...
```

---

## 文档对齐检查清单

| 文档 | 状态 | 主要修改 |
|-----|------|---------|
| PRD (prd.md) | ✅ | 新增 Phase 14，更新 MCP 描述 |
| LLM Integration (05_LLM_INTEGRATION.md) | ✅ | 更新 SessionManager，新增 SDK MCP 章节 |
| System Architecture (01_SYSTEM_ARCHITECTURE.md) | ✅ | 更新 MCP Protocol 状态 |
| Agent Architecture (02_AGENT_ARCHITECTURE.md) | ✅ | 添加 SDK MCP Migration Update |
| Design README (design/README.md) | ✅ | 更新 MCP Server Key，新增迁移章节 |
| Reference Docs Preload (07_REFERENCE_DOCS_PRELOAD.md) | ✅ | 更新 Problem Statement |
| Tech Stack (tech-stack.md) | ✅ | 更新 MCP Protocol Note |

---

## 参考文档

- [Test-Driven SDK MCP Migration Plan](./test-driven-sdk-mcp-migration-plan.md)
- [FastMCP SDK Compatibility Issue](../research/fastmcp-sdk-compatibility-issue.md)
- [SDK MCP Migration Plan A](../research/sdk-mcp-migration-plan-a.md)

---

**Document End**
