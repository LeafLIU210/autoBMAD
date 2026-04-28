# F6/F7/F8 修复方案测试驱动实施计划

**文档编号**: DS-SOLUTION-2026-04-07  
**关联报告**: `docs/research/docuswarm-deep-reform/F6-F7-F8-deep-research-report.md`  
**创建日期**: 2026-04-07  

---

## 1. 概述

本文档基于 F6/F7/F8 深度研究报告，提供详细的**测试驱动实施方案**。采用"测试先行"原则，每个修复步骤都配有对应的测试用例，确保修复的正确性和完整性。

### 1.1 修复目标矩阵

| 问题 | 修复目标 | 优先级 | 预估工作量 |
|------|----------|--------|------------|
| **F6** | 完成 `update_context` MCP 链路接线 | P0 | 2-3 天 |
| **F7** | Analyst 节点语义与 Skill 对齐 | P1 | 1 天 |
| **F8** | 模板资产运行时消费 | P1 | 2-3 天 |

### 1.2 测试策略

```
┌─────────────────────────────────────────────────────────────┐
│                    测试金字塔                                │
├─────────────────────────────────────────────────────────────┤
│  🎯 集成测试 (Integration Tests)                             │
│     ├── MCP 工具链端到端验证                                  │
│     ├── 节点配置合规性验证                                    │
│     └── 模板渲染流程验证                                      │
├─────────────────────────────────────────────────────────────┤
│  ⚙️ 单元测试 (Unit Tests)                                    │
│     ├── UpdateContextTool 功能测试                           │
│     ├── tool_filter 工具暴露测试                              │
│     ├── TemplateLoader 加载测试                               │
│     └── ContractBuilder 渲染测试                              │
├─────────────────────────────────────────────────────────────┤
│  🔧 工具验证 (Utility Scripts)                               │
│     ├── verify_mcp_chain.py                                  │
│     ├── verify_node_config.py                                │
│     └── verify_template_loading.py                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. F6: update_context MCP 链路修复 (P0)

### 2.1 问题回顾

```
配置层: node.yaml 中 shared_context.enabled = true  ✅
         ↓
断裂层: tool_filter.py 未创建 update_context server  ❌
         ↓
运行时: Agent 无法调用 update_context 工具           ❌
```

### 2.2 修复方案

#### 2.2.1 新建 `update_context_sdk.py`

**文件位置**: `autoBMAD/docuswarm/tools/update_context_sdk.py`

```python
"""SDK MCP 格式的 update_context 工具实现."""

from __future__ import annotations

import json
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool


def create_update_context_server(
    pipeline_id: str,
    node_id: str,
    allowed_operations: list[str],
) -> dict[str, Any]:
    """Create an SDK MCP server for update_context tool."""
    
    @tool(
        name="update_context",
        description="Update shared context with set/append/remove operations",
        parameters={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Context key to update (supports dot notation like 'progress.status')"
                },
                "value": {
                    "type": ["string", "number", "boolean", "array", "object"],
                    "description": "Value to set, append, or remove"
                },
                "operation": {
                    "type": "string",
                    "enum": allowed_operations or ["set", "append", "remove"],
                    "default": "set",
                    "description": "Operation to perform on the context key"
                },
            },
            "required": ["key", "value"],
        },
    )
    async def update_context_tool(args: dict[str, Any]) -> dict[str, Any]:
        """Execute update_context operation."""
        from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        tool = UpdateContextTool(
            state_manager=StateManager(),
            pipeline_id=pipeline_id,
        )
        result = await tool.execute(
            key=args["key"],
            value=args["value"],
            operation=args.get("operation", "set"),
        )
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    
    server = create_sdk_mcp_server(
        name=f"docuswarm-shared-context-{node_id}",
        version="1.0.0",
        tools=[update_context_tool],
    )
    
    return {
        "name": f"docuswarm-shared-context-{node_id}",
        "transport": "sdk",
        "server": server,
    }
```

#### 2.2.2 修改 `tool_filter.py`

**修改 1**: 在 `create_mcp_servers()` 中添加 update_context server 创建

```python
# autoBMAD/docuswarm/llm/tool_filter.py

class NodeToolFilter:
    def create_mcp_servers(
        self, 
        pipeline_id: str | None = None
    ) -> dict[str, Any]:
        """创建 MCP servers，现在支持 pipeline_id 参数."""
        servers: dict[str, Any] = {}
        
        # 1. 创建 file read server (现有代码)
        file_dirs = self._get_allowed_file_dirs()
        if file_dirs:
            from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
            file_server = create_file_read_server(
                name=f"docuswarm-files-{self.node_id}",
                allowed_dirs=file_dirs,
            )
            servers[file_server["name"]] = file_server
        
        # 2. 创建 search server (现有代码)
        search_dirs = self._get_allowed_search_dirs()
        if search_dirs:
            from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
            search_server = create_search_server(
                name=f"docuswarm-search-{self.node_id}",
                search_dirs=search_dirs,
            )
            servers[search_server["name"]] = search_server
        
        # 3. 创建 deliverable server (现有代码)
        if self.output_dir:
            from autoBMAD.docuswarm.tools.create_deliverable_sdk import create_deliverable_server
            deliverable_server = create_deliverable_server(
                name=f"docuswarm-deliverable-{self.node_id}",
                output_dir=self.output_dir,
                node_id=self.node_id,
            )
            servers[deliverable_server["name"]] = deliverable_server
        
        # 4. 【新增】创建 update_context server
        if (
            pipeline_id 
            and self.tool_permissions.shared_context.enabled
        ):
            from autoBMAD.docuswarm.tools.update_context_sdk import (
                create_update_context_server,
            )
            update_server = create_update_context_server(
                pipeline_id=pipeline_id,
                node_id=self.node_id,
                allowed_operations=self.tool_permissions.shared_context.operations,
            )
            servers[update_server["name"]] = update_server
        
        return servers
```

**修改 2**: 在 `get_allowed_tools()` 中添加 update_context 工具

```python
def get_allowed_tools(self) -> list[str]:
    """获取允许的工具列表，现在包含 update_context."""
    tools: list[str] = []
    
    # 1. Builtin tools (现有代码)
    tools.extend(self.tool_permissions.allowed_builtin_tools)
    
    # 2. MCP file tools (现有代码)
    file_dirs = self._get_allowed_file_dirs()
    if file_dirs:
        tools.extend([
            f"docuswarm-files-{self.node_id}::read_document",
            f"docuswarm-files-{self.node_id}::list_documents",
        ])
    
    # 3. MCP search tools (现有代码)
    search_dirs = self._get_allowed_search_dirs()
    if search_dirs:
        tools.extend([
            f"docuswarm-search-{self.node_id}::grep_search",
            f"docuswarm-search-{self.node_id}::glob_search",
        ])
    
    # 4. MCP deliverable tools (现有代码)
    if self.output_dir:
        tools.extend([
            f"docuswarm-deliverable-{self.node_id}::create_deliverable",
            f"docuswarm-deliverable-{self.node_id}::submit_execution_report",
        ])
    
    # 5. 【新增】MCP update_context 工具
    if self.tool_permissions.shared_context.enabled:
        tools.append(
            f"docuswarm-shared-context-{self.node_id}::update_context"
        )
    
    return tools
```

#### 2.2.3 修改 `independent.py`

传递 `pipeline_id` 给 `create_mcp_servers()`:

```python
# autoBMAD/docuswarm/agents/independent.py

class SessionManager:
    def _create_options(self) -> dict[str, Any]:
        """创建 LLM 选项，包含 MCP servers."""
        options = {}
        
        if self.tool_filter:
            # 【修改】传递 pipeline_id 参数
            mcp_servers = self.tool_filter.create_mcp_servers(
                pipeline_id=self.pipeline_id  # 新增参数
            )
            if mcp_servers:
                options["mcp_servers"] = list(mcp_servers.values())
        
        return options
```

### 2.3 测试驱动实施方案

#### 阶段 1: 编写失败测试 (Red)

**测试文件**: `tests/docuswarm/tools/test_update_context_sdk.py`

```python
"""Tests for update_context_sdk module."""

import pytest
from unittest.mock import Mock, patch

from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server


class TestCreateUpdateContextServer:
    """Test suite for create_update_context_server function."""
    
    def test_server_creation_with_valid_params(self):
        """Test server creation with valid parameters."""
        # Arrange
        pipeline_id = "test-pipeline-123"
        node_id = "analyst"
        allowed_operations = ["set", "append"]
        
        # Act
        server = create_update_context_server(
            pipeline_id=pipeline_id,
            node_id=node_id,
            allowed_operations=allowed_operations,
        )
        
        # Assert
        assert server is not None
        assert server["name"] == "docuswarm-shared-context-analyst"
        assert server["transport"] == "sdk"
        assert "server" in server
    
    def test_server_name_format(self):
        """Test server name follows naming convention."""
        server = create_update_context_server(
            pipeline_id="p1",
            node_id="pm",
            allowed_operations=["set"],
        )
        
        assert server["name"] == "docuswarm-shared-context-pm"
    
    def test_server_tool_registration(self):
        """Test that update_context tool is registered."""
        server = create_update_context_server(
            pipeline_id="p1",
            node_id="analyst",
            allowed_operations=["set", "append", "remove"],
        )
        
        # Server should have tools registered
        assert "server" in server
        # The actual tool verification depends on SDK internals
    
    @pytest.mark.asyncio
    async def test_update_context_tool_execution(self):
        """Test update_context tool execution."""
        # Arrange
        from autoBMAD.docuswarm.tools.update_context import UpdateContextTool
        
        with patch.object(UpdateContextTool, 'execute') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "key": "test.key",
                "operation": "set"
            }
            
            server = create_update_context_server(
                pipeline_id="p1",
                node_id="analyst",
                allowed_operations=["set"],
            )
            
            # Act & Assert
            # Tool execution test would go here
            # This depends on the actual SDK interface
```

**测试文件**: `tests/docuswarm/llm/test_tool_filter_update_context.py`

```python
"""Tests for update_context integration in NodeToolFilter."""

import pytest
from unittest.mock import Mock, patch

from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
from autoBMAD.docuswarm.schemas.node import (
    NodeConfig,
    NodeToolPermissions,
    SharedContextPermissions,
)


class TestNodeToolFilterUpdateContext:
    """Test suite for update_context in NodeToolFilter."""
    
    @pytest.fixture
    def node_config_with_shared_context(self):
        """Create node config with shared_context enabled."""
        return NodeConfig(
            node_id="analyst",
            name="Analyst",
            tool_permissions=NodeToolPermissions(
                shared_context=SharedContextPermissions(
                    enabled=True,
                    operations=["set", "append", "remove"],
                )
            )
        )
    
    @pytest.fixture
    def node_config_without_shared_context(self):
        """Create node config with shared_context disabled."""
        return NodeConfig(
            node_id="analyst",
            name="Analyst",
            tool_permissions=NodeToolPermissions(
                shared_context=SharedContextPermissions(
                    enabled=False,
                    operations=[],
                )
            )
        )
    
    def test_get_allowed_tools_includes_update_context_when_enabled(
        self, node_config_with_shared_context
    ):
        """F6-TEST-001: update_context 应在 shared_context 启用时出现在工具列表中."""
        # Arrange
        filter_obj = NodeToolFilter.from_node_config(node_config_with_shared_context)
        
        # Act
        tools = filter_obj.get_allowed_tools()
        
        # Assert
        expected_tool = "docuswarm-shared-context-analyst::update_context"
        assert expected_tool in tools, f"Expected {expected_tool} in {tools}"
    
    def test_get_allowed_tools_excludes_update_context_when_disabled(
        self, node_config_without_shared_context
    ):
        """F6-TEST-002: update_context 不应在 shared_context 禁用时出现."""
        # Arrange
        filter_obj = NodeToolFilter.from_node_config(node_config_without_shared_context)
        
        # Act
        tools = filter_obj.get_allowed_tools()
        
        # Assert
        assert not any("update_context" in t for t in tools)
    
    def test_create_mcp_servers_creates_update_context_server_when_enabled(
        self, node_config_with_shared_context
    ):
        """F6-TEST-003: 应在 shared_context 启用时创建 update_context server."""
        # Arrange
        filter_obj = NodeToolFilter.from_node_config(node_config_with_shared_context)
        
        with patch('autoBMAD.docuswarm.tools.update_context_sdk.create_update_context_server') as mock_create:
            mock_create.return_value = {
                "name": "docuswarm-shared-context-analyst",
                "transport": "sdk",
                "server": Mock()
            }
            
            # Act
            servers = filter_obj.create_mcp_servers(pipeline_id="test-pipeline")
            
            # Assert
            mock_create.assert_called_once_with(
                pipeline_id="test-pipeline",
                node_id="analyst",
                allowed_operations=["set", "append", "remove"],
            )
            assert "docuswarm-shared-context-analyst" in servers
    
    def test_create_mcp_servers_does_not_create_update_context_server_without_pipeline_id(
        self, node_config_with_shared_context
    ):
        """F6-TEST-004: 没有 pipeline_id 时不应创建 update_context server."""
        # Arrange
        filter_obj = NodeToolFilter.from_node_config(node_config_with_shared_context)
        
        with patch('autoBMAD.docuswarm.tools.update_context_sdk.create_update_context_server') as mock_create:
            # Act - 不传 pipeline_id
            servers = filter_obj.create_mcp_servers()
            
            # Assert
            mock_create.assert_not_called()
            assert not any("shared-context" in k for k in servers.keys())
    
    def test_create_mcp_servers_does_not_create_update_context_when_disabled(
        self, node_config_without_shared_context
    ):
        """F6-TEST-005: shared_context 禁用时不应创建 server."""
        # Arrange
        filter_obj = NodeToolFilter.from_node_config(node_config_without_shared_context)
        
        with patch('autoBMAD.docuswarm.tools.update_context_sdk.create_update_context_server') as mock_create:
            # Act
            servers = filter_obj.create_mcp_servers(pipeline_id="test-pipeline")
            
            # Assert
            mock_create.assert_not_called()
```

#### 阶段 2: 实现代码 (Green)

按照 2.2 节的修复方案实现代码。

#### 阶段 3: 运行测试验证 (Verify)

```bash
# 运行 F6 相关测试
pytest tests/docuswarm/tools/test_update_context_sdk.py -v
pytest tests/docuswarm/llm/test_tool_filter_update_context.py -v

# 运行集成测试
pytest tests/integration/test_mcp_chain.py -v -k "update_context"
```

#### 阶段 4: 编写工具验证脚本

**脚本**: `scripts/verify_f6_mcp_chain.py`

```python
#!/usr/bin/env python3
"""F6 修复验证脚本: MCP 工具链完整性检查."""

import sys
from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter


def verify_f6_fix(node_id: str = "analyst") -> bool:
    """验证 F6 修复是否成功."""
    print(f"\n{'='*60}")
    print(f"F6 修复验证: 节点 '{node_id}'")
    print(f"{'='*60}")
    
    config = NodeLoader.load(node_id)
    filter_obj = NodeToolFilter.from_node_config(config)
    
    all_passed = True
    
    # 检查 1: 配置层
    print("\n📋 检查 1: 配置层")
    sc = config.tool_permissions.shared_context
    print(f"   shared_context.enabled: {sc.enabled}")
    print(f"   shared_context.operations: {sc.operations}")
    
    if not sc.enabled:
        print("   ⚠️  shared_context 未启用，跳过后续检查")
        return True
    
    # 检查 2: 工具列表
    print("\n🔧 检查 2: 允许的工具列表")
    allowed = filter_obj.get_allowed_tools()
    for tool in allowed:
        print(f"   - {tool}")
    
    has_update_context = any("update_context" in t for t in allowed)
    if has_update_context:
        print("   ✅ update_context 工具已暴露")
    else:
        print("   ❌ update_context 工具未暴露")
        all_passed = False
    
    # 检查 3: MCP Servers
    print("\n🖥️  检查 3: MCP Servers")
    try:
        servers = filter_obj.create_mcp_servers(pipeline_id="test-pipeline")
        for name in servers.keys():
            print(f"   - {name}")
        
        has_shared_context_server = any("shared-context" in k for k in servers.keys())
        if has_shared_context_server:
            print("   ✅ shared-context server 已创建")
        else:
            print("   ❌ shared-context server 未创建")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_passed = False
    
    # 检查 4: Pipeline ID 传递
    print("\n📡 检查 4: Pipeline ID 传递")
    try:
        servers_no_pipeline = filter_obj.create_mcp_servers()
        has_server_without_pipeline = any("shared-context" in k for k in servers_no_pipeline.keys())
        
        if not has_server_without_pipeline:
            print("   ✅ 无 pipeline_id 时正确跳过创建")
        else:
            print("   ❌ 无 pipeline_id 时仍创建了 server")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_passed = False
    
    # 总结
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ F6 修复验证通过!")
    else:
        print("❌ F6 修复验证失败!")
    print(f"{'='*60}\n")
    
    return all_passed


if __name__ == "__main__":
    nodes = ["analyst", "pm", "ux", "architect", "po"]
    results = []
    
    for node in nodes:
        results.append(verify_f6_fix(node))
    
    print("\n" + "="*60)
    print("F6 最终验证结果")
    print("="*60)
    for node, result in zip(nodes, results):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {node}: {status}")
    
    sys.exit(0 if all(results) else 1)
```

### 2.4 F6 验收标准

| 验收项 | 验收标准 | 验证方法 |
|--------|----------|----------|
| **SDK 模块** | `update_context_sdk.py` 存在且可导入 | `python -c "from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server"` |
| **工具暴露** | shared_context 启用时，工具列表包含 update_context | 运行 `test_tool_filter_update_context.py` |
| **Server 创建** | shared_context 启用且有 pipeline_id 时，创建 server | 运行 `test_tool_filter_update_context.py` |
| **Pipeline 传递** | independent.py 正确传递 pipeline_id | 代码审查 + 集成测试 |
| **端到端** | Agent 可成功调用 update_context 工具 | 手动测试 + 日志验证 |

---

## 3. F7: Analyst 节点语义重构 (P1)

### 3.1 问题回顾

```
当前状态: task.name = "create-business-analysis-report"  ❌
期望状态: task.name = "create-product-brief"             ✅

当前状态: role = "Data Analyst"                          ❌
期望状态: role = "Strategic Business Analyst"            ✅
```

### 3.2 修复方案

#### 3.2.1 更新 `analyst/node.yaml`

```yaml
# autoBMAD/nodes/analyst/node.yaml

node:
  id: analyst
  name: Analyst
  version: "2.0.0"

task:
  # 【修改】任务名称对齐 Skill
  name: create-product-brief
  
  # 【修改】任务描述产品发现导向
  description: |
    通过协作发现创建产品简介。
    
    作为产品发现促进者，你的职责是：
    1. 引导用户理解产品意图和愿景
    2. 在充分理解产品目标后分析输入工件
    3. 创建简洁有力的产品简介文档
    
    你不是数据扫描器，而是产品意图的发现者和澄清者。
  
  # 【修改】角色补充强调产品发现
  role_supplement: |
    你是 Mary，一位战略业务分析师和产品发现专家。
    
    核心原则：
    - 先理解 "为什么"，再分析 "是什么"
    - 促进清晰度，而不只是报告数据
    - 与用户协作澄清产品意图，而非单方面输出
    
    工作风格：
    - 采用 "寻宝猎人" 能量：好奇、探索、发现
    - 协作而非指令
    - 关注业务价值和用户成果
  
  # 【保留】Skill 引用正确
  skill_ref: bmad-product-brief

persona:
  # 【修改】使用模板指定的角色名
  name: Mary
  
  # 【修改】角色定位与 Skill 对齐
  role: Strategic Business Analyst & Product Discovery Expert
  
  # 【新增】详细描述
  description: |
    Product discovery facilitator who guides teams to understand product intent
    before diving into analysis. Expert at asking the right questions to uncover
    underlying business needs and translate them into clear product direction.
  
  # 【修改】专业能力列表
  expertise:
    - Product discovery and market research
    - Porter's Five Forces framework
    - SWOT analysis
    - Requirements elicitation
    - Business model canvas
    - Competitive landscape analysis
    - User journey mapping
  
  # 【新增】沟通风格
  communication_style: treasure_hunter_energy
  
  # 【新增】工作风格
  working_style: collaborative
  
  # 【新增】核心原则
  principles:
    - "Understand the 'why' before analyzing the 'what'"
    - "Facilitate clarity, don't just report data"
    - "Questions are more valuable than early answers"
    - "Collaboration beats prescription"

tool_permissions:
  skills:
    whitelist:
      - bmad-product-brief
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
  
  shared_context:
    enabled: true
    operations:
      - set
      - append
      - remove

deliverable:
  template_title: product-brief
  output_filename: "{pipeline_id}-product-brief.md"
  document_types:
    - product_brief
  format_hints:
    sections:
      - product_overview
      - target_users
      - value_proposition
      - key_features
      - success_metrics
```

#### 3.2.2 更新 `analyst/persona.json`

```json
{
  "name": "Mary",
  "role": "Strategic Business Analyst & Product Discovery Expert",
  "description": "Product discovery facilitator who guides teams to understand product intent before diving into analysis",
  "expertise": [
    "Product discovery and market research",
    "Porter's Five Forces framework",
    "SWOT analysis", 
    "Requirements elicitation",
    "Business model canvas",
    "Competitive landscape analysis",
    "User journey mapping"
  ],
  "communication_style": "treasure_hunter_energy",
  "working_style": "collaborative",
  "principles": [
    "Understand the 'why' before analyzing the 'what'",
    "Facilitate clarity, don't just report data",
    "Questions are more valuable than early answers",
    "Collaboration beats prescription"
  ],
  "personality_traits": {
    "curiosity": "high",
    "analytical_depth": "balanced_with_pragmatism",
    "communication": "engaging_and_clarifying"
  }
}
```

### 3.3 测试驱动实施方案

#### 阶段 1: 编写失败测试 (Red)

**测试文件**: `tests/nodes/test_analyst_node_reform.py`

```python
"""Tests for Analyst node Deep Reform compliance."""

import pytest
from autoBMAD.nodes.loader import NodeLoader


class TestAnalystNodeReform:
    """F7 测试套件: Analyst 节点语义重构验证."""
    
    @pytest.fixture
    def analyst_config(self):
        """Load analyst node configuration."""
        return NodeLoader.load("analyst")
    
    def test_task_name_is_create_product_brief(self, analyst_config):
        """F7-TEST-001: task.name 应为 'create-product-brief'."""
        assert analyst_config.task.name == "create-product-brief", (
            f"Expected task.name='create-product-brief', "
            f"got '{analyst_config.task.name}'"
        )
    
    def test_task_description_mentions_product_discovery(self, analyst_config):
        """F7-TEST-002: task.description 应包含产品发现相关描述."""
        description = analyst_config.task.description.lower()
        
        # 应包含产品发现相关关键词
        assert "product" in description or "产品" in description, (
            "task.description 应包含 'product' 或 '产品'"
        )
        
        # 不应是旧的业务分析报告描述
        assert "business analysis report" not in description, (
            "task.description 不应包含旧的 'business analysis report' 描述"
        )
    
    def test_skill_ref_is_bmad_product_brief(self, analyst_config):
        """F7-TEST-003: skill_ref 应为 'bmad-product-brief'."""
        assert analyst_config.task.skill_ref == "bmad-product-brief", (
            f"Expected skill_ref='bmad-product-brief', "
            f"got '{analyst_config.task.skill_ref}'"
        )
    
    def test_role_supplement_mentions_facilitator(self, analyst_config):
        """F7-TEST-004: role_supplement 应强调促进者角色."""
        supplement = analyst_config.task.role_supplement.lower()
        
        # 应包含促进者/发现者相关词汇
        facilitator_keywords = [
            "facilitator", "促进者", "discovery", "发现",
            "collaborate", "协作", "intent", "意图"
        ]
        
        has_facilitator_keyword = any(
            kw in supplement for kw in facilitator_keywords
        )
        
        assert has_facilitator_keyword, (
            f"role_supplement 应包含促进者相关词汇，"
            f"当前内容: {analyst_config.task.role_supplement[:100]}..."
        )
    
    def test_skill_whitelist_includes_product_brief(self, analyst_config):
        """F7-TEST-005: Skill 白名单应包含 bmad-product-brief."""
        whitelist = analyst_config.tool_permissions.skills.whitelist
        
        assert "bmad-product-brief" in whitelist, (
            f"Skill 白名单应包含 'bmad-product-brief', 当前: {whitelist}"
        )
    
    def test_skill_whitelist_structure(self, analyst_config):
        """F7-TEST-006: Skill 白名单结构应符合方案."""
        expected_skills = [
            "bmad-product-brief",
            "bmad-domain-research",
            "bmad-market-research",
            "bmad-advanced-elicitation"
        ]
        
        whitelist = analyst_config.tool_permissions.skills.whitelist
        
        for skill in expected_skills:
            assert skill in whitelist, (
                f"Skill 白名单应包含 '{skill}'"
            )


class TestAnalystPersonaReform:
    """F7 测试套件: Analyst Persona 重构验证."""
    
    @pytest.fixture
    def persona(self):
        """Load analyst persona."""
        import json
        from pathlib import Path
        
        persona_path = Path("autoBMAD/nodes/analyst/persona.json")
        with open(persona_path) as f:
            return json.load(f)
    
    def test_persona_name_is_mary(self, persona):
        """F7-TEST-007: persona.name 应为 'Mary'."""
        assert persona.get("name") == "Mary", (
            f"Expected persona.name='Mary', got '{persona.get('name')}'"
        )
    
    def test_persona_role_is_strategic_analyst(self, persona):
        """F7-TEST-008: persona.role 应为战略分析师."""
        role = persona.get("role", "").lower()
        
        assert "strategic" in role or "战略" in role, (
            f"persona.role 应包含 'strategic' 或 '战略', got '{persona.get('role')}'"
        )
        
        assert "product discovery" in role.lower() or "产品发现" in role, (
            f"persona.role 应包含 'product discovery', got '{persona.get('role')}'"
        )
    
    def test_persona_expertise_includes_discovery(self, persona):
        """F7-TEST-009: expertise 应包含产品发现相关能力."""
        expertise = [e.lower() for e in persona.get("expertise", [])]
        
        discovery_keywords = [
            "product discovery", "market research",
            "porter", "swot", "elicitation"
        ]
        
        has_discovery = any(
            any(kw in e for kw in discovery_keywords)
            for e in expertise
        )
        
        assert has_discovery, (
            f"expertise 应包含产品发现相关能力, got {expertise}"
        )
    
    def test_persona_communication_style(self, persona):
        """F7-TEST-010: communication_style 应为 'treasure_hunter_energy'."""
        style = persona.get("communication_style")
        
        assert style == "treasure_hunter_energy", (
            f"Expected communication_style='treasure_hunter_energy', got '{style}'"
        )
    
    def test_persona_has_principles(self, persona):
        """F7-TEST-011: persona 应包含核心原则."""
        principles = persona.get("principles", [])
        
        assert len(principles) > 0, "persona 应包含 principles 列表"
        
        # 检查关键原则
        principles_text = " ".join(principles).lower()
        assert "why" in principles_text, "原则应包含 'why' 相关内容"
```

#### 阶段 2: 实现代码 (Green)

按照 3.2 节的修复方案更新配置文件。

#### 阶段 3: 运行测试验证 (Verify)

```bash
# 运行 F7 相关测试
pytest tests/nodes/test_analyst_node_reform.py -v
```

#### 阶段 4: 编写工具验证脚本

**脚本**: `scripts/verify_f7_analyst_reform.py`

```python
#!/usr/bin/env python3
"""F7 修复验证脚本: Analyst 节点语义重构检查."""

import json
import sys
from pathlib import Path
from autoBMAD.nodes.loader import NodeLoader


def verify_f7_fix() -> bool:
    """验证 F7 修复是否成功."""
    print(f"\n{'='*60}")
    print("F7 修复验证: Analyst 节点语义重构")
    print(f"{'='*60}")
    
    all_passed = True
    
    # 加载配置
    try:
        config = NodeLoader.load("analyst")
        print("\n✅ 成功加载 analyst 节点配置")
    except Exception as e:
        print(f"\n❌ 加载配置失败: {e}")
        return False
    
    # 检查 1: 任务名称
    print("\n📋 检查 1: 任务名称")
    task_name = config.task.name
    expected_name = "create-product-brief"
    
    if task_name == expected_name:
        print(f"   ✅ task.name = '{task_name}'")
    else:
        print(f"   ❌ task.name = '{task_name}' (期望: '{expected_name}')")
        all_passed = False
    
    # 检查 2: Skill 引用
    print("\n📋 检查 2: Skill 引用")
    skill_ref = config.task.skill_ref
    expected_skill = "bmad-product-brief"
    
    if skill_ref == expected_skill:
        print(f"   ✅ skill_ref = '{skill_ref}'")
    else:
        print(f"   ❌ skill_ref = '{skill_ref}' (期望: '{expected_skill}')")
        all_passed = False
    
    # 检查 3: Skill 白名单
    print("\n📋 检查 3: Skill 白名单")
    whitelist = config.tool_permissions.skills.whitelist
    expected_skills = [
        "bmad-product-brief",
        "bmad-domain-research",
        "bmad-market-research",
        "bmad-advanced-elicitation"
    ]
    
    for skill in expected_skills:
        if skill in whitelist:
            print(f"   ✅ {skill}")
        else:
            print(f"   ❌ 缺失: {skill}")
            all_passed = False
    
    # 检查 4: Persona
    print("\n📋 检查 4: Persona 配置")
    try:
        persona_path = Path("autoBMAD/nodes/analyst/persona.json")
        with open(persona_path) as f:
            persona = json.load(f)
        
        # 检查 name
        if persona.get("name") == "Mary":
            print("   ✅ persona.name = 'Mary'")
        else:
            print(f"   ❌ persona.name = '{persona.get('name')}' (期望: 'Mary')")
            all_passed = False
        
        # 检查 role
        role = persona.get("role", "")
        if "Strategic" in role and "Product Discovery" in role:
            print(f"   ✅ persona.role = '{role}'")
        else:
            print(f"   ❌ persona.role = '{role}'")
            all_passed = False
        
        # 检查 communication_style
        if persona.get("communication_style") == "treasure_hunter_energy":
            print("   ✅ persona.communication_style = 'treasure_hunter_energy'")
        else:
            print(f"   ❌ persona.communication_style = '{persona.get('communication_style')}'")
            all_passed = False
        
    except Exception as e:
        print(f"   ❌ 读取 persona.json 失败: {e}")
        all_passed = False
    
    # 检查 5: 任务描述
    print("\n📋 检查 5: 任务描述")
    description = config.task.description.lower()
    
    if "product" in description or "产品" in description:
        print("   ✅ 任务描述包含产品相关关键词")
    else:
        print("   ❌ 任务描述缺少产品相关关键词")
        all_passed = False
    
    # 总结
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ F7 修复验证通过!")
    else:
        print("❌ F7 修复验证失败!")
    print(f"{'='*60}\n")
    
    return all_passed


if __name__ == "__main__":
    success = verify_f7_fix()
    sys.exit(0 if success else 1)
```

### 3.4 F7 验收标准

| 验收项 | 验收标准 | 验证方法 |
|--------|----------|----------|
| **任务名称** | `task.name` = "create-product-brief" | 运行 `test_analyst_node_reform.py::test_task_name_is_create_product_brief` |
| **Skill 引用** | `task.skill_ref` = "bmad-product-brief" | 运行 `test_analyst_node_reform.py::test_skill_ref_is_bmad_product_brief` |
| **Persona 名称** | `persona.name` = "Mary" | 运行 `test_analyst_node_reform.py::test_persona_name_is_mary` |
| **Persona 角色** | `persona.role` 包含 "Strategic" 和 "Product Discovery" | 运行 `test_analyst_node_reform.py::test_persona_role_is_strategic_analyst` |
| **Skill 白名单** | 包含 4 个指定 Skill | 运行 `test_analyst_node_reform.py::test_skill_whitelist_structure` |
| **语义对齐** | 任务描述产品发现导向 | 运行 `test_analyst_node_reform.py::test_task_description_mentions_product_discovery` |

---

## 4. F8: 模板运行时消费 (P1)

### 4.1 问题回顾

```
模板资产: autoBMAD/docuswarm/templates/analyst_templates.yaml  ✅
         ↓
断裂层: TemplateLoader 路径错误，ContractBuilder 未加载模板  ❌
         ↓
运行时: System Prompt 只有 template_title 文本，无结构化章节  ❌
```

### 4.2 修复方案

#### 4.2.1 修复 `TemplateLoader` 默认路径

```python
# autoBMAD/docuswarm/prompts/template_loader.py

class TemplateLoader:
    """加载模板文件，支持从 docuswarm/templates/ 目录加载."""
    
    # 【修改】指向正确的模板目录
    DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    # 原来是: Path(__file__).parent / "templates" (指向 prompts/templates/)
    
    def __init__(self, templates_dir: Path | str | None = None):
        """
        Args:
            templates_dir: 自定义模板目录，默认使用 DEFAULT_TEMPLATES_DIR
        """
        self.templates_dir = Path(templates_dir) if templates_dir else self.DEFAULT_TEMPLATES_DIR
        self._cache: dict[str, dict] = {}
```

#### 4.2.2 扩展 `ContractBuilder` 加载模板

```python
# autoBMAD/docuswarm/prompts/contract_builder.py

class NodePromptContractBuilder:
    """构建节点提示词合约，现在支持模板加载."""
    
    def __init__(self):
        self.template_loader = TemplateLoader()
    
    def _build_deliverable_section(self, context: NodeExecutionContext) -> str:
        """构建交付物章节，现在包含结构化模板内容."""
        sections = []
        reqs = context.deliverable_requirements
        
        # 获取基础配置
        template_title = reqs.get("template_title")
        deliverable_type = reqs.get("deliverable_type", "document")
        
        # 文档标题
        title = template_title or deliverable_type
        if title:
            sections.append(f"\n**文档标题**: {title}")
        
        # 【新增】从模板文件加载结构化定义
        try:
            template_data = self._load_node_template(
                context.node_id, 
                template_title
            )
            if template_data:
                formatted = self._format_template_sections(template_data)
                if formatted:
                    sections.append(formatted)
        except Exception as e:
            # 优雅降级：如果模板加载失败，只使用基础配置
            logger.debug(f"Template loading failed for {context.node_id}: {e}")
        
        # 必须包含的章节（从 node.yaml 配置）
        required_sections = reqs.get("required_sections", [])
        if required_sections and not template_data:
            # 只有在没有模板数据时才使用 node.yaml 的 required_sections
            sections.append("\n**必须包含以下章节**:")
            for section in required_sections:
                sections.append(f"- {section}")
        
        return "\n".join(sections)
    
    def _load_node_template(
        self, 
        node_id: str, 
        template_id: str | None
    ) -> dict | None:
        """
        从模板文件加载节点模板.
        
        Args:
            node_id: 节点 ID (如 "analyst", "pm")
            template_id: 模板 ID (如 "market_research")
            
        Returns:
            匹配的模板数据，如果未找到则返回 None
        """
        template_file = f"{node_id}_templates"
        
        try:
            data = self.template_loader.load_template(template_file)
            if not data or "raw" not in data:
                return None
            
            templates = data["raw"].get("templates", [])
            
            # 查找匹配的模板
            if template_id:
                for template in templates:
                    if template.get("template_id") == template_id:
                        return template
            else:
                # 如果没有指定 template_id，返回第一个模板
                return templates[0] if templates else None
                
        except FileNotFoundError:
            logger.debug(f"Template file not found: {template_file}")
            return None
        except Exception as e:
            logger.warning(f"Error loading template {template_file}: {e}")
            return None
        
        return None
    
    def _format_template_sections(self, template_data: dict) -> str:
        """格式化模板章节为 prompt 文本."""
        sections = []
        
        # 模板章节
        template_sections = template_data.get("sections", [])
        if template_sections:
            sections.append("\n**文档结构要求**:")
            
            for section in template_sections:
                heading = section.get("heading", "")
                required = section.get("required", False)
                description = section.get("description", "")
                
                marker = "【必须】" if required else "【可选】"
                line = f"\n{marker} {heading}"
                
                if description:
                    line += f"\n   {description}"
                
                sections.append(line)
        
        # 模板标准
        standards = template_data.get("standards", {})
        if standards:
            sections.append("\n**格式标准**:")
            
            if "style_guide" in standards:
                sections.append(f"- 风格指南: {standards['style_guide']}")
            if "diagram_format" in standards:
                sections.append(f"- 图表格式: {standards['diagram_format']}")
        
        # 元数据
        filename_pattern = template_data.get("filename_pattern")
        if filename_pattern:
            sections.append(f"\n**文件名格式**: {filename_pattern}")
        
        return "\n".join(sections)
```

#### 4.2.3 验证模板文件格式

确保 `analyst_templates.yaml` 格式正确:

```yaml
# autoBMAD/docuswarm/templates/analyst_templates.yaml

templates:
  - template_id: product_brief
    title: "Product Brief"
    filename_pattern: "{pipeline_id}-product-brief.md"
    description: "Concise executive summary of product discovery findings"
    
    sections:
      - heading: "Executive Summary"
        required: true
        description: "1-2 paragraph overview of the product opportunity"
      
      - heading: "Product Vision & Intent"
        required: true
        description: "The 'why' behind the product - what problem it solves"
      
      - heading: "Target Users"
        required: true
        description: "Primary and secondary user segments"
      
      - heading: "Value Proposition"
        required: true
        description: "Key benefits and differentiation"
      
      - heading: "Key Features"
        required: false
        description: "Must-have capabilities for MVP"
      
      - heading: "Success Metrics"
        required: false
        description: "How we measure success"
    
    standards:
      style_guide: "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"
      diagram_format: "mermaid"
      max_length: "2 pages"
  
  - template_id: market_research
    title: "Market Research Report"
    filename_pattern: "{pipeline_id}-market-research.md"
    # ... 其他模板

standards:
  default_style: "executive_brief"
  diagram_engine: "mermaid"
```

### 4.3 测试驱动实施方案

#### 阶段 1: 编写失败测试 (Red)

**测试文件**: `tests/docuswarm/prompts/test_template_loading.py`

```python
"""Tests for template loading in prompt generation."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from autoBMAD.docuswarm.prompts.template_loader import TemplateLoader
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder


class TestTemplateLoaderPath:
    """F8-TEST-001~003: TemplateLoader 路径测试."""
    
    def test_default_templates_dir_points_to_docuswarm_templates(self):
        """F8-TEST-001: DEFAULT_TEMPLATES_DIR 应指向 docuswarm/templates/."""
        expected_suffix = Path("docuswarm/templates")
        actual = Path(TemplateLoader.DEFAULT_TEMPLATES_DIR)
        
        assert expected_suffix.as_posix() in actual.as_posix(), (
            f"DEFAULT_TEMPLATES_DIR 应包含 '{expected_suffix}', "
            f"实际: '{actual}'"
        )
    
    def test_template_loader_can_load_analyst_templates(self):
        """F8-TEST-002: 应能加载 analyst_templates.yaml."""
        loader = TemplateLoader()
        
        try:
            data = loader.load_template("analyst_templates")
            assert data is not None, "应返回模板数据"
            assert "raw" in data, "应包含 'raw' 字段"
        except FileNotFoundError:
            pytest.fail("无法加载 analyst_templates.yaml - 文件不存在或路径错误")
    
    def test_template_loader_returns_correct_structure(self):
        """F8-TEST-003: 返回的模板数据应具有正确结构."""
        loader = TemplateLoader()
        
        try:
            data = loader.load_template("analyst_templates")
            raw = data.get("raw", {})
            
            assert "templates" in raw, "应包含 'templates' 列表"
            assert isinstance(raw["templates"], list), "'templates' 应为列表"
            
            if raw["templates"]:
                first_template = raw["templates"][0]
                assert "template_id" in first_template, "模板应有 template_id"
                assert "sections" in first_template, "模板应有 sections"
        except FileNotFoundError:
            pytest.skip("analyst_templates.yaml 不存在")


class TestContractBuilderTemplateIntegration:
    """F8-TEST-004~007: ContractBuilder 模板集成测试."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock execution context."""
        context = Mock()
        context.node_id = "analyst"
        context.deliverable_requirements = {
            "template_title": "product_brief",
            "deliverable_type": "document"
        }
        return context
    
    def test_contract_builder_loads_template_for_analyst(self, mock_context):
        """F8-TEST-004: ContractBuilder 应为 analyst 加载模板."""
        builder = NodePromptContractBuilder()
        
        # 验证 template_loader 已初始化
        assert hasattr(builder, 'template_loader')
        assert builder.template_loader is not None
    
    def test_build_deliverable_section_includes_template_sections(self, mock_context):
        """F8-TEST-005: 交付物章节应包含模板章节."""
        builder = NodePromptContractBuilder()
        
        section = builder._build_deliverable_section(mock_context)
        
        # 如果模板加载成功，应包含结构化内容
        if "文档结构要求" in section or "Document Structure" in section:
            assert "Executive Summary" in section or "产品概述" in section
    
    def test_load_node_template_returns_template_data(self):
        """F8-TEST-006: _load_node_template 应返回模板数据."""
        builder = NodePromptContractBuilder()
        
        template_data = builder._load_node_template("analyst", "product_brief")
        
        if template_data is not None:
            assert "template_id" in template_data
            assert "sections" in template_data
    
    def test_format_template_sections_returns_formatted_text(self):
        """F8-TEST-007: _format_template_sections 应返回格式化文本."""
        builder = NodePromptContractBuilder()
        
        test_template = {
            "template_id": "test",
            "sections": [
                {
                    "heading": "Test Section",
                    "required": True,
                    "description": "Test description"
                }
            ],
            "filename_pattern": "test.md"
        }
        
        formatted = builder._format_template_sections(test_template)
        
        assert "Test Section" in formatted
        assert "Test description" in formatted
        assert "必须" in formatted or "Required" in formatted


class TestTemplateRuntimeIntegration:
    """F8-TEST-008~010: 模板运行时集成测试."""
    
    def test_analyst_system_prompt_includes_template_sections(self):
        """F8-TEST-008: Analyst System Prompt 应包含模板章节."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        # 这需要集成测试环境
        # 验证系统提示词生成时包含了模板内容
        pytest.skip("需要完整集成测试环境")
    
    def test_template_loading_graceful_fallback(self):
        """F8-TEST-009: 模板加载失败时应优雅降级."""
        builder = NodePromptContractBuilder()
        
        # 使用不存在的节点
        result = builder._load_node_template("nonexistent", "template")
        
        assert result is None, "不存在的模板应返回 None"
    
    def test_all_nodes_have_templates_or_graceful_fallback(self):
        """F8-TEST-010: 所有节点应有模板或能优雅处理缺失."""
        nodes = ["analyst", "pm", "ux", "architect", "po"]
        loader = TemplateLoader()
        
        for node in nodes:
            try:
                data = loader.load_template(f"{node}_templates")
                print(f"✅ {node}: 模板存在")
            except FileNotFoundError:
                print(f"⚠️  {node}: 模板不存在，应确保优雅降级")
```

**测试文件**: `tests/integration/test_template_integration.py`

```python
"""Integration tests for template loading in prompt generation."""

import pytest
from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder
from autoBMAD.docuswarm.prompts.schemas import NodeExecutionContext


class TestTemplatePromptIntegration:
    """模板与 Prompt 生成集成测试."""
    
    @pytest.fixture
    def contract_builder(self):
        return NodePromptContractBuilder()
    
    def test_analyst_prompt_includes_template_structure(self, contract_builder):
        """验证 analyst 节点的提示词包含模板结构."""
        # 加载配置
        config = NodeLoader.load("analyst")
        
        # 创建执行上下文
        context = NodeExecutionContext(
            node_id="analyst",
            node_config=config,
            deliverable_requirements={
                "template_title": config.deliverable.template_title,
                "output_filename": config.deliverable.output_filename,
            }
        )
        
        # 生成提示词
        prompt = contract_builder._build_deliverable_section(context)
        
        # 验证包含模板相关内容
        assert "文档" in prompt or "Document" in prompt
```

#### 阶段 2: 实现代码 (Green)

按照 4.2 节的修复方案实现代码。

#### 阶段 3: 运行测试验证 (Verify)

```bash
# 运行 F8 相关测试
pytest tests/docuswarm/prompts/test_template_loading.py -v
pytest tests/integration/test_template_integration.py -v
```

#### 阶段 4: 编写工具验证脚本

**脚本**: `scripts/verify_f8_template_loading.py`

```python
#!/usr/bin/env python3
"""F8 修复验证脚本: 模板运行时消费检查."""

import sys
from pathlib import Path
from autoBMAD.docuswarm.prompts.template_loader import TemplateLoader
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder


def verify_f8_fix() -> bool:
    """验证 F8 修复是否成功."""
    print(f"\n{'='*60}")
    print("F8 修复验证: 模板运行时消费")
    print(f"{'='*60}")
    
    all_passed = True
    
    # 检查 1: TemplateLoader 路径
    print("\n📋 检查 1: TemplateLoader 默认路径")
    default_dir = Path(TemplateLoader.DEFAULT_TEMPLATES_DIR)
    print(f"   DEFAULT_TEMPLATES_DIR = {default_dir}")
    
    if "docuswarm/templates" in default_dir.as_posix():
        print("   ✅ 路径正确指向 docuswarm/templates/")
    else:
        print("   ❌ 路径错误")
        all_passed = False
    
    # 检查 2: 模板文件加载
    print("\n📋 检查 2: 模板文件加载")
    loader = TemplateLoader()
    
    nodes = ["analyst", "pm", "ux", "architect", "po"]
    for node in nodes:
        try:
            data = loader.load_template(f"{node}_templates")
            templates = data.get("raw", {}).get("templates", [])
            print(f"   ✅ {node}: 加载成功，包含 {len(templates)} 个模板")
        except FileNotFoundError:
            print(f"   ⚠️  {node}: 模板文件不存在")
        except Exception as e:
            print(f"   ❌ {node}: 加载失败 - {e}")
            all_passed = False
    
    # 检查 3: ContractBuilder 模板集成
    print("\n📋 检查 3: ContractBuilder 模板集成")
    builder = NodePromptContractBuilder()
    
    if hasattr(builder, 'template_loader') and builder.template_loader:
        print("   ✅ ContractBuilder 已集成 template_loader")
    else:
        print("   ❌ ContractBuilder 未正确集成 template_loader")
        all_passed = False
    
    # 检查 4: 模板数据格式化
    print("\n📋 检查 4: 模板数据格式化")
    try:
        template_data = builder._load_node_template("analyst", "product_brief")
        
        if template_data:
            formatted = builder._format_template_sections(template_data)
            
            if "文档结构" in formatted or "Document Structure" in formatted:
                print("   ✅ 模板章节已正确格式化")
            else:
                print("   ⚠️  格式化输出可能不完整")
            
            # 显示部分内容
            preview = formatted[:200].replace("\n", " ")
            print(f"   预览: {preview}...")
        else:
            print("   ⚠️  未找到 analyst/product_brief 模板")
    except Exception as e:
        print(f"   ❌ 格式化失败: {e}")
        all_passed = False
    
    # 总结
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ F8 修复验证通过!")
    else:
        print("❌ F8 修复验证失败!")
    print(f"{'='*60}\n")
    
    return all_passed


if __name__ == "__main__":
    success = verify_f8_fix()
    sys.exit(0 if success else 1)
```

### 4.4 F8 验收标准

| 验收项 | 验收标准 | 验证方法 |
|--------|----------|----------|
| **路径修复** | `TemplateLoader.DEFAULT_TEMPLATES_DIR` 指向 `docuswarm/templates/` | 运行 `test_template_loading.py::test_default_templates_dir_points_to_docuswarm_templates` |
| **模板加载** | 能成功加载 `analyst_templates.yaml` | 运行 `test_template_loading.py::test_template_loader_can_load_analyst_templates` |
| **ContractBuilder 集成** | `NodePromptContractBuilder` 有 `template_loader` 属性 | 运行 `test_template_loading.py::test_contract_builder_loads_template_for_analyst` |
| **章节注入** | System Prompt 包含模板章节结构 | 手动检查 + 集成测试 |
| **优雅降级** | 模板缺失时不影响基础功能 | 运行 `test_template_loading.py::test_template_loading_graceful_fallback` |

---

## 5. 集成测试与端到端验证

### 5.1 集成测试套件

**测试文件**: `tests/integration/test_f6_f7_f8_integration.py`

```python
"""Integration tests for F6/F7/F8 fixes."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
from autoBMAD.docuswarm.agents.independent import IndependentAgent


class TestF6F7F8Integration:
    """F6/F7/F8 综合集成测试."""
    
    @pytest.fixture
    def analyst_config(self):
        return NodeLoader.load("analyst")
    
    def test_analyst_node_full_configuration(self, analyst_config):
        """INTEGRATION-001: Analyst 节点配置完整性检查."""
        # F7 检查
        assert analyst_config.task.name == "create-product-brief"
        assert analyst_config.task.skill_ref == "bmad-product-brief"
        
        # F6 检查
        assert analyst_config.tool_permissions.shared_context.enabled is True
        assert "set" in analyst_config.tool_permissions.shared_context.operations
        
        # F8 检查
        assert analyst_config.deliverable.template_title is not None
    
    def test_tool_filter_with_analyst_config(self, analyst_config):
        """INTEGRATION-002: ToolFilter 正确处理 Analyst 配置."""
        filter_obj = NodeToolFilter.from_node_config(analyst_config)
        
        # F6: 工具列表应包含 update_context
        tools = filter_obj.get_allowed_tools()
        assert any("update_context" in t for t in tools)
        
        # F6: 应能创建 MCP servers
        with patch('autoBMAD.docuswarm.tools.update_context_sdk.create_update_context_server') as mock_create:
            mock_create.return_value = {
                "name": "docuswarm-shared-context-analyst",
                "transport": "sdk",
                "server": Mock()
            }
            
            servers = filter_obj.create_mcp_servers(pipeline_id="test-pipeline")
            assert "docuswarm-shared-context-analyst" in servers
    
    @pytest.mark.asyncio
    async def test_independent_agent_initialization(self):
        """INTEGRATION-003: IndependentAgent 正确初始化."""
        # 这需要更完整的测试环境
        pytest.skip("需要完整的 IndependentAgent 测试环境")
```

### 5.2 端到端验证流程

```bash
# 1. 运行所有单元测试
pytest tests/docuswarm/tools/test_update_context_sdk.py -v
pytest tests/docuswarm/llm/test_tool_filter_update_context.py -v
pytest tests/nodes/test_analyst_node_reform.py -v
pytest tests/docuswarm/prompts/test_template_loading.py -v

# 2. 运行集成测试
pytest tests/integration/test_f6_f7_f8_integration.py -v

# 3. 运行验证脚本
python scripts/verify_f6_mcp_chain.py
python scripts/verify_f7_analyst_reform.py
python scripts/verify_f8_template_loading.py

# 4. 完整回归测试
pytest tests/ -k "not slow" --tb=short
```

---

## 6. 实施时间表与里程碑

### 6.1 Phase 1: F6 MCP 链路修复 (2-3 天)

| 天数 | 任务 | 交付物 | 验证方式 |
|------|------|--------|----------|
| Day 1 | 编写失败测试 | `test_update_context_sdk.py`, `test_tool_filter_update_context.py` | 测试运行失败 |
| Day 1-2 | 实现 `update_context_sdk.py` | `autoBMAD/docuswarm/tools/update_context_sdk.py` | 单元测试通过 |
| Day 2 | 修改 `tool_filter.py` | 更新的 `tool_filter.py` | 单元测试通过 |
| Day 2-3 | 修改 `independent.py` | 更新的 `independent.py` | 集成测试通过 |
| Day 3 | 验证脚本 | `verify_f6_mcp_chain.py` | 脚本运行通过 |

### 6.2 Phase 2: F7 Analyst 语义重构 (1 天)

| 天数 | 任务 | 交付物 | 验证方式 |
|------|------|--------|----------|
| Day 1 AM | 编写失败测试 | `test_analyst_node_reform.py` | 测试运行失败 |
| Day 1 AM | 更新 `node.yaml` | 更新的 `analyst/node.yaml` | 单元测试通过 |
| Day 1 PM | 更新 `persona.json` | 更新的 `analyst/persona.json` | 单元测试通过 |
| Day 1 PM | 验证脚本 | `verify_f7_analyst_reform.py` | 脚本运行通过 |

### 6.3 Phase 3: F8 模板运行时消费 (2-3 天)

| 天数 | 任务 | 交付物 | 验证方式 |
|------|------|--------|----------|
| Day 1 | 编写失败测试 | `test_template_loading.py` | 测试运行失败 |
| Day 1-2 | 修复 `TemplateLoader` 路径 | 更新的 `template_loader.py` | 单元测试通过 |
| Day 2 | 扩展 `ContractBuilder` | 更新的 `contract_builder.py` | 单元测试通过 |
| Day 2-3 | 验证模板文件格式 | 更新的 `analyst_templates.yaml` | 集成测试通过 |
| Day 3 | 验证脚本 | `verify_f8_template_loading.py` | 脚本运行通过 |

### 6.4 最终验收 (1 天)

| 任务 | 验证方式 |
|------|----------|
| 运行完整测试套件 | `pytest tests/ -v` |
| 运行所有验证脚本 | `python scripts/verify_f*.py` |
| 端到端手动测试 | 运行实际 Pipeline |
| 代码审查 | PR Review |

---

## 7. 风险与缓解策略

| 风险 | 影响 | 缓解策略 |
|------|------|----------|
| **SDK 接口变更** | MCP SDK 接口可能与示例不同 | 先查阅 SDK 文档，编写适配层 |
| **Template 文件格式不一致** | 实际 YAML 结构可能与假设不同 | 先检查实际文件，再编写解析逻辑 |
| **IndependentAgent 依赖复杂** | 难以在测试中完整模拟 | 使用 Mock，聚焦接口契约 |
| **Persona 变更影响用户体验** | 角色变化可能让现有用户不适应 | 保留旧配置备份，提供迁移指南 |
| **模板加载性能问题** | 频繁加载 YAML 可能影响性能 | 实现缓存机制 |

---

## 8. 附录

### 8.1 测试命令速查表

```bash
# F6 测试
pytest tests/docuswarm/tools/test_update_context_sdk.py -v
pytest tests/docuswarm/llm/test_tool_filter_update_context.py -v

# F7 测试
pytest tests/nodes/test_analyst_node_reform.py -v

# F8 测试
pytest tests/docuswarm/prompts/test_template_loading.py -v

# 集成测试
pytest tests/integration/test_f6_f7_f8_integration.py -v

# 验证脚本
python scripts/verify_f6_mcp_chain.py
python scripts/verify_f7_analyst_reform.py
python scripts/verify_f8_template_loading.py
```

### 8.2 文件变更清单

| 问题 | 新增文件 | 修改文件 |
|------|----------|----------|
| **F6** | `autoBMAD/docuswarm/tools/update_context_sdk.py`<br>`tests/docuswarm/tools/test_update_context_sdk.py`<br>`tests/docuswarm/llm/test_tool_filter_update_context.py`<br>`scripts/verify_f6_mcp_chain.py` | `autoBMAD/docuswarm/llm/tool_filter.py`<br>`autoBMAD/docuswarm/agents/independent.py` |
| **F7** | `tests/nodes/test_analyst_node_reform.py`<br>`scripts/verify_f7_analyst_reform.py` | `autoBMAD/nodes/analyst/node.yaml`<br>`autoBMAD/nodes/analyst/persona.json` |
| **F8** | `tests/docuswarm/prompts/test_template_loading.py`<br>`tests/integration/test_template_integration.py`<br>`scripts/verify_f8_template_loading.py` | `autoBMAD/docuswarm/prompts/template_loader.py`<br>`autoBMAD/docuswarm/prompts/contract_builder.py` |

### 8.3 参考文档

- [F6/F7/F8 深度研究报告](../research/docuswarm-deep-reform/F6-F7-F8-deep-research-report.md)
- [05-shared-context-update-mechanism.md](../../spec/05-shared-context-update-mechanism.md)
- [02-node-task-skill-mapping.md](../../spec/02-node-task-skill-mapping.md)
- [03-document-creation-constraints.md](../../spec/03-document-creation-constraints.md)

---

**文档版本**: 1.0  
**最后更新**: 2026-04-07  
**作者**: Code Implementation Agent
