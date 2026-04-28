# F6/F7/F8 研究执行摘要

**研究日期**: 2026-04-07  
**研究范围**: `docs/evaluation/2026-04-07-docuswarm-deep-reform-implementation-review.md` 中的 F6、F7、F8 问题  
**研究方法**: 静态代码分析 + 动态调试工具验证

---

## 核心发现

通过深度代码分析和调试工具验证，确认三个问题均为**配置层完备但运行时接线缺失**的系统性问题。

| 问题 | 严重程度 | 状态 | 根因 |
|------|----------|------|------|
| **F6** | High | **确认存在** | `update_context` 未进入 MCP 运行时链路 |
| **F7** | Medium | **确认存在** | Analyst 任务名称和描述未按方案更新 |
| **F8** | Medium | **确认存在** | 模板路径配置错误，运行时未加载模板 |

---

## 调试工具验证结果

### 1. MCP 工具链验证 (F6)

```bash
$ python tools/debug/verify_mcp_tool_chain.py analyst

📊 1. 配置层检查
   shared_context.enabled: True  ✅
   shared_context.operations: ['set', 'append', 'remove']  ✅

📊 2. 允许的工具列表检查
   📋 Allowed tools (6 total):
      - Read
      - Glob
      - mcp__docuswarm-files-analyst__read_document
      - mcp__docuswarm-files-analyst__list_documents
      - mcp__docuswarm-search-analyst__grep_search
      - mcp__docuswarm-search-analyst__glob_search
      ❌ update_context 工具缺失

📊 3. MCP Server 检查
   🔌 MCP Servers (2 total):
      - docuswarm-files-analyst
      - docuswarm-search-analyst
      ❌ docuswarm-shared-context-analyst server 缺失

📊 4. 验证结果
   ❌ shared_context 已启用，但 update_context 工具未暴露
   ❌ shared_context 已启用，但 update_context server 未创建
```

**关键证据**:
- `tool_filter.py:get_allowed_tools()` 返回 6 个工具，**不包含** `update_context`
- `tool_filter.py:create_mcp_servers()` 创建 2 个 server，**不包含** `docuswarm-shared-context`
- 缺少 `update_context_sdk.py` 工厂函数

---

### 2. 节点配置验证 (F7)

```bash
$ python tools/debug/verify_node_reform_config.py analyst

📋 F7 检查: Analyst 任务语义重构
   ❌ task.name = 'create-business-analysis-report' (期望: 'create-product-brief')
   ✅ task.skill_ref = 'bmad-product-brief'

   Skills 白名单:
     ✅ bmad-product-brief
     ✅ bmad-domain-research
     ✅ bmad-market-research
     ✅ bmad-advanced-elicitation
```

**关键证据**:
- `analyst/node.yaml:13` 仍为 `name: create-business-analysis-report`
- 研究方案要求重构为 `create-product-brief`
- Skill 引用正确，但任务描述与 Skill 能力错位

---

### 3. 模板对齐验证 (F8)

```bash
$ python tools/debug/verify_node_reform_config.py analyst

📋 F8 检查: 模板对齐配置
   template_title: (未设置)
   ✅ 模板文件存在: autoBMAD\docuswarm\templates\analyst_templates.yaml
   定义模板数: 3
     - market_research: Market Research Report
     - user_personas: User Persona Analysis
     - risk_assessment: Risk Assessment Report

   TemplateLoader 默认路径:
     当前: D:\GITHUB\DocuSwarm\autoBMAD\docuswarm\prompts\templates
     期望: D:\GITHUB\DocuSwarm\autoBMAD\docuswarm\templates

❌ TemplateLoader 路径不匹配 - 当前指向 prompts/templates/，但模板文件在 docuswarm/templates/
```

**关键证据**:
- 模板文件存在于 `docuswarm/templates/analyst_templates.yaml`
- `TemplateLoader.DEFAULT_TEMPLATES_DIR` 指向 `prompts/templates/` (错误路径)
- 3 个模板定义无法被加载到运行时

---

## 运行时链路分析

通过 `trace_runtime_chain.py` 端到端追踪，确认以下断裂点：

```
IndependentAgent.execute_with_input()
  ↓
[OK] NodeLoader.load() → 配置完整
  ↓
[OK] NodeToolFilter.from_node_config() → 创建成功
  ↓
[FAIL] filter_obj.get_allowed_tools() → 不包含 update_context
  ↓
[FAIL] filter_obj.create_mcp_servers() → 不创建 shared-context server
  ↓
SessionManager() → 工具权限不完整
  ↓
LLM 无法调用 update_context
```

---

## 修复优先级与工作量

| 问题 | 优先级 | 估计工作量 | 修复复杂度 |
|------|--------|------------|------------|
| **F6** | P0 | 2-3 天 | 中等 (需新建 SDK 模块) |
| **F7** | P1 | 0.5 天 | 低 (仅配置变更) |
| **F8** | P1 | 1-2 天 | 中等 (需修复路径 + 扩展 ContractBuilder) |

---

## 修复方案速查

### F6: update_context MCP 链路修复

**需要修改的文件**:
1. 新建 `autoBMAD/docuswarm/tools/update_context_sdk.py`
2. 修改 `autoBMAD/docuswarm/llm/tool_filter.py`
3. 可能需要修改 `autoBMAD/docuswarm/agents/independent.py`

**关键代码片段**:
```python
# tool_filter.py:get_allowed_tools() 中添加:
if self.tool_permissions.shared_context.enabled:
    tools.append(
        MCP_TOOL_NAME_FORMAT.format(
            type="shared-context", node_id=self.node_id, tool_name="update_context"
        )
    )

# tool_filter.py:create_mcp_servers() 中添加:
if self.tool_permissions.shared_context.enabled and pipeline_id:
    from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server
    update_server = create_update_context_server(pipeline_id, self.node_id, ...)
    servers[update_server["name"]] = update_server
```

---

### F7: Analyst 任务语义重构

**需要修改的文件**:
- `autoBMAD/nodes/analyst/node.yaml`
- `autoBMAD/nodes/analyst/persona.json` (可选，增强)

**关键变更**:
```yaml
# node.yaml
task:
  name: create-product-brief                    # 变更: create-business-analysis-report
  description: 通过协作发现创建产品简介...        # 更新描述
  role_supplement: 作为产品发现促进者...         # 更新角色补充
  skill_ref: bmad-product-brief                  # 保持不变
```

---

### F8: 模板运行时接线

**需要修改的文件**:
1. `autoBMAD/docuswarm/prompts/template_loader.py`
2. `autoBMAD/docuswarm/prompts/contract_builder.py`

**关键代码片段**:
```python
# template_loader.py 修复路径:
class TemplateLoader:
    DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    # 从 prompts/templates/ 改为 docuswarm/templates/

# contract_builder.py 加载模板:
def _load_node_template(self, node_id: str, template_id: str | None) -> dict | None:
    template_file = f"{node_id}_templates"
    data = self.template_loader.load_template(template_file)
    # 匹配并返回模板定义
```

---

## 调试工具位置

所有调试工具位于 `tools/debug/`:

| 工具 | 用途 | 验证问题 |
|------|------|----------|
| `verify_mcp_tool_chain.py` | MCP 工具链完整性 | F6 |
| `verify_node_reform_config.py` | 节点配置合规 | F7, F8 |
| `trace_runtime_chain.py` | 运行时链路追踪 | F6, F7, F8 |

**使用方法**:
```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; python tools/debug/verify_mcp_tool_chain.py --all
$env:PYTHONIOENCODING="utf-8"; python tools/debug/verify_node_reform_config.py analyst
$env:PYTHONIOENCODING="utf-8"; python tools/debug/trace_runtime_chain.py --node analyst --pipeline test
```

---

## 验证修复的方法

修复完成后，运行调试工具验证:

```bash
# F6 验证
$ python tools/debug/verify_mcp_tool_chain.py analyst
# 期望输出: ✅ update_context 工具: 存在
# 期望输出: ✅ update_context server: 存在

# F7 验证
$ python tools/debug/verify_node_reform_config.py analyst
# 期望输出: ✅ task.name = 'create-product-brief'

# F8 验证
$ python tools/debug/verify_node_reform_config.py analyst
# 期望输出: ✅ TemplateLoader 路径匹配
```

---

## 结论

F6、F7、F8 三个问题均已通过代码分析和调试工具验证确认存在。这些问题共同指向一个模式：**Deep Reform 方案的配置层已完备实现，但运行时执行层存在"最后一公里"接线缺失**。

修复这三个问题将完成 Deep Reform 方案的全面实施，使以下能力真正可用：

1. **F6 修复后**: Shared Context 更新机制可用，节点间可共享上下文
2. **F7 修复后**: Analyst 节点职责与 BMAD Skill 对齐
3. **F8 修复后**: BMAD 模板资产被运行时消费，文档质量提升

---

**研究报告**: `docs/research/docuswarm-deep-reform/F6-F7-F8-deep-research-report.md`  
**调试工具**: `tools/debug/`  
**状态**: 待修复实施
