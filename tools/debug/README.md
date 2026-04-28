# DocuSwarm Deep Reform 调试工具集

本目录包含用于诊断 F6/F7/F8 问题的调试工具。

## 工具列表

### 1. verify_mcp_tool_chain.py - MCP 工具链验证

验证 `update_context` 工具是否已进入 MCP 运行时链路。

**用途**: 诊断 F6 问题

**用法**:
```bash
# 验证所有节点
python tools/debug/verify_mcp_tool_chain.py --all

# 验证特定节点
python tools/debug/verify_mcp_tool_chain.py analyst
```

**输出示例**:
```
============================================================
🔍 验证节点: ANALYST
============================================================

📊 1. 配置层检查
----------------------------------------
   shared_context.enabled: True
   shared_context.operations: ['set', 'append', 'remove']

📊 2. 允许的工具列表检查
----------------------------------------
  📋 Allowed tools (6 total):
     - Read
     - Glob
     - mcp__docuswarm-files-analyst__read_document
     - mcp__docuswarm-files-analyst__list_documents
     - mcp__docuswarm-search-analyst__grep_search
     - mcp__docuswarm-search-analyst__glob_search

📊 3. MCP Server 检查
----------------------------------------
  🔌 MCP Servers (2 total):
     - docuswarm-files-analyst
     - docuswarm-search-analyst

📊 4. 验证结果汇总
----------------------------------------
   ❌ shared_context 已启用，但 update_context 工具未暴露
   ❌ shared_context 已启用，但 update_context server 未创建
```

---

### 2. verify_node_reform_config.py - 节点配置合规验证

验证节点配置是否符合 Deep Reform 方案要求。

**用途**: 诊断 F7 (Analyst 任务语义) 和 F8 (模板对齐) 问题

**用法**:
```bash
# 验证所有节点
python tools/debug/verify_node_reform_config.py --all

# 验证特定节点
python tools/debug/verify_node_reform_config.py analyst
```

**检查内容**:
- **F6**: Shared Context 配置 (`enabled`, `operations`, `allowed_keys`)
- **F7**: Analyst 任务语义 (`task.name`, `task.skill_ref`, skills whitelist)
- **F8**: 模板配置 (`template_title`, `output_filename`, 模板文件存在性, `TemplateLoader` 路径)

**输出示例**:
```
📋 F7 检查: Analyst 任务语义重构
----------------------------------------
   ❌ task.name = 'create-business-analysis-report' (期望: 'create-product-brief')
   ✅ task.skill_ref = 'bmad-product-brief'

📋 F8 检查: 模板对齐配置
----------------------------------------
   template_title: (未设置)
   ✅ 模板文件存在: autoBMAD\docuswarm\templates\analyst_templates.yaml
   ❌ TemplateLoader 路径不匹配
```

---

### 3. trace_runtime_chain.py - 运行时链路追踪

深度追踪 IndependentAgent 执行时的完整运行时链路。

**用途**: 端到端验证配置是否真正进入运行时

**用法**:
```bash
python tools/debug/trace_runtime_chain.py --node analyst --pipeline debug-001
```

**追踪步骤**:
1. 加载节点配置
2. 创建 NodeToolFilter
3. 生成允许的工具列表
4. 创建 MCP Servers
5. 创建 SessionManager

**输出示例**:
```
📋 步骤 3: 生成允许的工具列表
============================================================
❌ [F6-Check] ❌ 未找到 update_context 或 shared-context 工具
   hint: 需要在 tool_filter.py 的 get_allowed_tools() 中添加
   expected_pattern: mcp__docuswarm-shared-context-{node_id}__update_context

📋 步骤 4: 创建 MCP Servers
============================================================
❌ [F6-Check] ❌ 未创建 shared-context MCP server
   hint: 需要在 tool_filter.py 的 create_mcp_servers() 中添加
   expected_name_pattern: docuswarm-shared-context-{node_id}
```

---

## 快速诊断指南

### 诊断 F6 (update_context MCP 链路)

```bash
# 运行所有三个工具
python tools/debug/verify_mcp_tool_chain.py --all
python tools/debug/trace_runtime_chain.py --node analyst --pipeline test
```

**预期问题**:
- `shared_context.enabled: True` 但 `update_context` 工具未暴露
- `update_context` server 未创建

**根本原因**:
- `tool_filter.py:get_allowed_tools()` 未添加 update_context
- `tool_filter.py:create_mcp_servers()` 未创建 update_context server
- 缺少 `update_context_sdk.py` 工厂函数

---

### 诊断 F7 (Analyst 任务语义)

```bash
python tools/debug/verify_node_reform_config.py analyst
```

**预期问题**:
- `task.name = 'create-business-analysis-report'` (期望: 'create-product-brief')

**根本原因**:
- `analyst/node.yaml` 未按方案更新任务名称和描述

---

### 诊断 F8 (模板对齐)

```bash
python tools/debug/verify_node_reform_config.py analyst
```

**预期问题**:
- `TemplateLoader` 路径指向 `prompts/templates/`，但模板文件在 `docuswarm/templates/`

**根本原因**:
- `TemplateLoader.DEFAULT_TEMPLATES_DIR` 路径配置错误
- `ContractBuilder` 未加载模板文件内容

---

## Windows 用户注意

在 Windows PowerShell 中运行时需要设置编码:

```powershell
$env:PYTHONIOENCODING="utf-8"; python tools/debug/verify_mcp_tool_chain.py --all
```

---

## 修复后验证

修复完成后，再次运行工具验证:

```bash
# 所有检查应该通过
python tools/debug/verify_mcp_tool_chain.py --all
# 输出: ✅ 所有检查通过 - F6 问题已修复

python tools/debug/verify_node_reform_config.py analyst
# 输出: ✅ 所有节点配置检查通过

python tools/debug/trace_runtime_chain.py --node analyst --pipeline test
# 输出: ✅ update_context MCP 链路完整
```
