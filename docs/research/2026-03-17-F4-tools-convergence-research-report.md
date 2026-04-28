# F4: 工具层决策收敛深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm tools 包
> 核心问题: 工具层处于产品决策未收敛状态

---

## 1. 执行摘要

### 1.1 核心发现

工具层存在**决策未收敛**和**实现分裂**问题：

1. **产品决策**: 运行期 agent 配置已朝 docs-free 收敛，但代码和导出仍有残留
2. **API 分裂**: `tool_registry.py`（全局注册器）与 `models/tool_registry.py`（扩展定义）并存，语义分叉
3. **向后兼容负担**: `parse_deliverable_metadata` 等兼容代码增加了维护成本

### 1.2 关键代码证据

```python
# autoBMAD/docuswarm/tools/__init__.py:23
# ❌ 残留兼容函数
def parse_deliverable_metadata(output: str) -> dict[str, Any]:
    """Parse metadata from create_deliverable tool output."""
    if "METADATA:" not in output:
        return {}
    json_part = output.split("METADATA:")[1].strip()
    return json.loads(json_part)

# autoBMAD/docuswarm/agents/configs/independent_agent.yaml:5
# ✅ 已配置 docs-free
# NOTE: This is a docs-free configuration per P1-2 decision.
tools:
  - "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"
  - "autoBMAD.docuswarm.tools.update_context:UpdateContextTool"
  - "autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool"

# autoBMAD/docuswarm/tools/tool_registry.py:8
class ToolRegistry:
    """工具注册器（全局）"""

# autoBMAD/docuswarm/models/tool_registry.py:26
class ToolRegistryExtended(ToolRegistry):
    """扩展工具注册器（模型层）"""
```

---

## 2. 详细分析

### 2.1 工具层现状全图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          工具层架构现状                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  tools/ 目录                                                            │
│  ├── __init__.py                                                        │
│  │   ├── CreateDeliverableTool        ✅ 保留（docs-free 核心）         │
│  │   ├── CreateDocumentSetTool        ✅ 保留（docs-free 核心）         │
│  │   ├── UpdateContextTool            ✅ 保留（docs-free 核心）         │
│  │   └── parse_deliverable_metadata() ❌ 移除（METADATA 解析残留）       │
│  ├── create_deliverable.py            ✅ CallableTool2 实现            │
│  ├── create_document_set.py           ✅ CallableTool2 实现            │
│  ├── update_context.py                ✅ CallableTool2 实现            │
│  ├── tool_registry.py                 ⚠️  合并/简化                    │
│  ├── tool_result.py                   ✅ 保留                          │
│  └── tool_result_extractor.py         ⚠️  边界层适配                   │
│                                                                         │
│  models/ 目录                                                           │
│  ├── tool_registry.py                 ❌ 合并到 tools/                  │
│  │   └── ToolRegistryExtended                                       │
│  └── tool.py                          ⚠️  检查冗余                      │
│                                                                         │
│  agents/configs/independent_agent.yaml                                 │
│  └── tools: [create_deliverable, update_context, create_document_set]  │
│                                     ✅ 已配置 docs-free                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 工具注册 API 分裂分析

#### 2.2.1 tools/tool_registry.py

```python
# tool_registry.py
class ToolRegistry:
    """Global tool registry for managing tool definitions."""
    
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
    
    def register(self, name: str, func: Callable, ...) -> None:
        self._tools[name] = ToolDefinition(...)
    
    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

# 全局实例
_tool_registry: ToolRegistry | None = None

def get_tool_registry() -> ToolRegistry:
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry

def register_tool(name: str) -> Callable:
    """Decorator for registering tools."""
    def decorator(func: Callable) -> Callable:
        get_tool_registry().register(name, func)
        return func
    return decorator
```

**定位**: 运行时工具注册管理

#### 2.2.2 models/tool_registry.py

```python
# models/tool_registry.py
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry, ToolDefinition

class ToolRegistryExtended(ToolRegistry):
    """Extended tool registry with additional capabilities."""
    
    def register_with_schema(self, name: str, schema: dict, ...) -> None:
        """Register with explicit schema."""
        ...
    
    def export_openapi(self) -> dict:
        """Export as OpenAPI spec."""
        ...
```

**问题**: 
- 继承自 `tools.tool_registry.ToolRegistry`
- 但 `__all__` 中又重导出 `ToolRegistry`，可能造成循环引用
- 功能边界不清晰

### 2.3 残留兼容代码分析

#### 2.3.1 parse_deliverable_metadata

```python
# tools/__init__.py:23-44
def parse_deliverable_metadata(output: str) -> dict[str, Any]:
    """Parse metadata from create_deliverable tool output.
    
    Args:
        output: The tool output string containing METADATA JSON.
    
    Returns:
        Parsed metadata dictionary.
    
    Example:
        >>> output = "Deliverable saved...\\n\\nMETADATA: {\\"file_path\\": ...}"
        >>> metadata = parse_deliverable_metadata(output)
        >>> metadata["file_path"]
        '/path/to/file.md'
    """
    import json
    
    if "METADATA:" not in output:
        return {}
    
    json_part = output.split("METADATA:")[1].strip()
    return json.loads(json_part)
```

**问题**: 
- 这是为了解析 `ToolOk(output="...METADATA: {...}")` 的字符串输出
- 如果采用结构化 `ToolResult`，不再需要字符串解析

#### 2.3.2 导出列表

```python
# tools/__init__.py:47-55
__all__ = [
    "CreateDeliverableParams",
    "CreateDeliverableTool",
    "CreateDocumentSetParams",
    "CreateDocumentSetTool",
    "UpdateContextParams",
    "UpdateContextTool",
    "parse_deliverable_metadata",  # ❌ 应该移除
]
```

### 2.4 决策矩阵

| 决策项 | 当前状态 | 目标状态 |
|--------|----------|----------|
| 工具数量 | 3个核心 + 残留 | 3个核心（docs-free） |
| 注册 API | 2个（tool_registry + ToolRegistryExtended） | 1个统一 API |
| 返回格式 | ToolOk + METADATA 字符串 | ToolResult（结构化） |
| 元数据解析 | parse_deliverable_metadata 函数 | 不再需要 |

---

## 3. 收敛方案

### 3.1 最终决策

**采用方案 A：坚持 docs-free**

1. **只保留三个工具**: `create_deliverable`, `update_context`, `create_document_set`
2. **工具注册 API 收敛成一种用法**
3. **删除 docs 工具相关残留**

### 3.2 具体收敛动作

#### 3.2.1 清理 tools/__init__.py

```python
# tools/__init__.py - 清理后
"""DocuSwarm tools package.

This package contains CallableTool2-based tools for the DocuSwarm SDK.
All output is directed to the pipeline output directory (docs-free workflow).

Available Tools:
    - CreateDeliverableTool: Create node deliverable documents
    - UpdateContextTool: Update shared context with persistence
    - CreateDocumentSetTool: Create multiple related documents
"""

from autoBMAD.docuswarm.tools.create_deliverable import (
    CreateDeliverableParams,
    CreateDeliverableTool,
)
from autoBMAD.docuswarm.tools.create_document_set import (
    CreateDocumentSetParams,
    CreateDocumentSetTool,
)
from autoBMAD.docuswarm.tools.update_context import (
    UpdateContextParams,
    UpdateContextTool,
)

__all__ = [
    # 核心工具类
    "CreateDeliverableTool",
    "CreateDocumentSetTool",
    "UpdateContextTool",
    # 参数类型
    "CreateDeliverableParams",
    "CreateDocumentSetParams",
    "UpdateContextParams",
]
```

#### 3.2.2 合并 ToolRegistry

```python
# tools/tool_registry.py - 合并后
"""Unified Tool Registry for DocuSwarm.

This module provides a single, unified tool registration API.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """Definition of a registered tool."""
    name: str
    func: Callable[..., Any]
    description: str
    schema: dict[str, Any] | None = None


class ToolRegistry:
    """Unified tool registry for managing tool definitions.
    
    This is the single source of truth for tool registration.
    All tool registration should go through this class.
    """
    
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
    
    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
        schema: dict[str, Any] | None = None,
    ) -> None:
        """Register a tool."""
        self._tools[name] = ToolDefinition(
            name=name,
            func=func,
            description=description,
            schema=schema,
        )
    
    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def export_schemas(self) -> dict[str, dict]:
        """Export all tool schemas."""
        return {
            name: tool.schema
            for name, tool in self._tools.items()
            if tool.schema
        }


# 全局注册器实例
_global_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(
    name: str,
    description: str = "",
    schema: dict[str, Any] | None = None,
) -> Callable[[Callable], Callable]:
    """Decorator for registering tools.
    
    Example:
        @register_tool(name="my_tool", description="Does something")
        def my_tool(param: str) -> ToolResult:
            ...
    """
    def decorator(func: Callable) -> Callable:
        get_tool_registry().register(name, func, description, schema)
        return func
    return decorator


def list_registered_tools() -> list[str]:
    """List all registered tool names."""
    return get_tool_registry().list_tools()


__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
    "list_registered_tools",
]
```

#### 3.2.3 删除或合并 models/tool_registry.py

```python
# models/tool_registry.py - 删除或改为重导出
"""Tool registry re-export for backward compatibility.

DEPRECATED: Use autoBMAD.docuswarm.tools.tool_registry directly.
This module will be removed in a future version.
"""

import warnings

warnings.warn(
    "models.tool_registry is deprecated. Use tools.tool_registry instead.",
    DeprecationWarning,
    stacklevel=2,
)

# 重导出
from autoBMAD.docuswarm.tools.tool_registry import (
    ToolDefinition,
    ToolRegistry,
    get_tool_registry,
    register_tool,
)

__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
]
```

### 3.3 工具 YAML 配置确认

```yaml
# agents/configs/independent_agent.yaml
# NOTE: This is a docs-free configuration per F4 decision.
# Only 3 core tools are registered.

tools:
  - "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"
  - "autoBMAD.docuswarm.tools.update_context:UpdateContextTool"
  - "autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool"
```

---

## 4. 测试建议

### 4.1 工具导出测试

```python
def test_tools_package_exports():
    """验证 tools 包只导出 docs-free 工具."""
    from autoBMAD.docuswarm import tools
    
    # 应该导出的
    assert hasattr(tools, "CreateDeliverableTool")
    assert hasattr(tools, "CreateDocumentSetTool")
    assert hasattr(tools, "UpdateContextTool")
    
    # 不应该导出的（已移除）
    assert not hasattr(tools, "parse_deliverable_metadata")
    
    # 验证 __all__
    expected = [
        "CreateDeliverableTool",
        "CreateDocumentSetTool",
        "UpdateContextTool",
        "CreateDeliverableParams",
        "CreateDocumentSetParams",
        "UpdateContextParams",
    ]
    assert set(tools.__all__) == set(expected)
```

### 4.2 工具注册统一性测试

```python
def test_single_tool_registry_api():
    """验证只有一个工具注册 API."""
    from autoBMAD.docuswarm.tools.tool_registry import (
        ToolRegistry,
        get_tool_registry,
        register_tool,
    )
    
    # 注册工具
    @register_tool(name="test_tool")
    def test_tool():
        pass
    
    # 验证能获取
    registry = get_tool_registry()
    assert registry.get("test_tool") is not None
    
    # 验证 models 层是重导出（如果保留）
    from autoBMAD.docuswarm.models.tool_registry import ToolRegistry as ModelTR
    assert ModelTR is ToolRegistry  # 应该是同一个类
```

### 4.3 YAML 配置一致性测试

```python
import yaml

def test_agent_yaml_docs_free():
    """验证 agent YAML 配置只包含 docs-free 工具."""
    with open("autoBMAD/docuswarm/agents/configs/independent_agent.yaml") as f:
        config = yaml.safe_load(f)
    
    tools = config.get("tools", [])
    
    # 验证只有 3 个工具
    assert len(tools) == 3
    
    # 验证工具路径
    expected_tools = [
        "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool",
        "autoBMAD.docuswarm.tools.update_context:UpdateContextTool",
        "autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool",
    ]
    for tool in expected_tools:
        assert tool in tools, f"Missing tool: {tool}"
```

---

## 5. 代码修改清单

### 5.1 删除/清理

- [ ] `tools/__init__.py`
  - 删除 `parse_deliverable_metadata` 函数
  - 更新 `__all__` 列表

- [ ] `models/tool_registry.py`
  - 删除 `ToolRegistryExtended` 类
  - 改为重导出或删除整个文件

### 5.2 修改/合并

- [ ] `tools/tool_registry.py`
  - 添加 `export_schemas()` 方法
  - 统一注册 API
  - 更新 `__all__`

### 5.3 验证

- [ ] `agents/configs/independent_agent.yaml`
  - 确认只包含 3 个核心工具

- [ ] 测试覆盖
  - 导出测试
  - 注册统一性测试
  - YAML 配置测试

---

## 6. 结论

1. **docs-free 决策已经做出**，需要清理残留代码
2. **工具注册 API 需要统一**，避免双轨维护
3. **修改范围较小**，主要是删除和重导出
4. **测试是关键**，确保 docs-free 决策被正确执行

---

## 相关文档 (2026-03-18 更新)

### 技术债务关联

工具层收敛与 **TD-2** 和 **TD-3** 技术债务直接相关：

| 技术债务 | 关联说明 |
|---------|---------|
| **TD-2** | 工具层需要显式 `output_dir` 注入，移除 `Path.cwd()` 依赖 |
| **TD-3** | `models` 兼容层需要清理，`ToolRegistryExtended` 应合并到 `tools` |

### 参考文档

- [技术债务评估报告](../evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md)
- [技术债务深度研究报告](2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md)
- [P0/P1 TDD 主方案](../solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md)

---

## 附录: 工具层清理前后对比

### 清理前

```
tools/
├── __init__.py
│   ├── CreateDeliverableTool
│   ├── CreateDocumentSetTool
│   ├── UpdateContextTool
│   └── parse_deliverable_metadata  ←─ 残留
├── tool_registry.py                 ←─ 基础注册器
├── models/tool_registry.py          ←─ 扩展注册器（重复）
└── ...

models/
└── tool_registry.py                 ←─ ToolRegistryExtended（应该合并）
```

### 清理后

```
tools/
├── __init__.py
│   ├── CreateDeliverableTool       ✅
│   ├── CreateDocumentSetTool       ✅
│   └── UpdateContextTool           ✅
├── tool_registry.py                ✅ 统一注册器
└── ...

models/
└── (删除 tool_registry.py 或改为重导出)
```
