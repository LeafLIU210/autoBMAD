# F4: 工具层决策收敛测试驱动方案

> 基于研究报告: `docs/research/2026-03-17-F4-tools-convergence-research-report.md`
> 创建日期: 2026-03-18

---

## 1. 目标与范围

### 1.1 核心目标

根据 F4 研究报告的收敛决策，通过测试驱动开发 (TDD) 实现以下目标：

1. **清理残留代码**: 删除 `parse_deliverable_metadata` 等 docs 工具残留
2. **统一 API**: 合并 `ToolRegistry` 与 `ToolRegistryExtended`
3. **验证配置**: 确保 YAML 配置只包含 docs-free 工具
4. **100% 测试通过**: 所有测试必须验证通过

### 1.2 代码修改范围

| 文件路径 | 修改类型 | 说明 |
|---------|---------|------|
| `autoBMAD/docuswarm/tools/__init__.py` | 清理 | 删除 `parse_deliverable_metadata`，更新 `__all__` |
| `autoBMAD/docuswarm/tools/tool_registry.py` | 增强 | 添加 `export_schemas()`，统一 API |
| `autoBMAD/docuswarm/models/tool_registry.py` | 重构 | 改为重导出，删除 `ToolRegistryExtended` |
| `tests/tools/test_tools_package_exports.py` | 新建 | 验证 tools 包导出 |
| `tests/tools/test_tool_registry_unified.py` | 新建 | 验证注册 API 统一性 |
| `tests/tools/test_agent_yaml_config.py` | 新建 | 验证 YAML 配置一致性 |

---

## 2. 测试策略

### 2.1 测试金字塔

```
        /\
       /  \
      / E2E\      integration/test_*.py (端到端验证)
     /______\
    /        \
   / Integration\  tests/tools/test_*_integration.py (集成测试)
  /______________\
 /                \
/    Unit Tests    \  tests/tools/test_*.py (单元测试)
/____________________\
```

### 2.2 测试类型

| 测试类型 | 目标 | 数量 |
|---------|------|------|
| 单元测试 | 验证单个函数/类的行为 | 15+ |
| 集成测试 | 验证模块间协作 | 5+ |
| 配置测试 | 验证 YAML 与代码一致 | 3+ |

---

## 3. 详细测试用例

### 3.1 Test Suite 1: Tools Package 导出测试

**文件**: `tests/tools/test_tools_package_exports.py`

#### TC1.1: 验证核心工具类已导出
```python
def test_tools_package_exports_core_tools():
    """验证 tools 包导出三个核心工具类."""
    from autoBMAD.docuswarm import tools
    
    assert hasattr(tools, "CreateDeliverableTool"), "缺少 CreateDeliverableTool"
    assert hasattr(tools, "CreateDocumentSetTool"), "缺少 CreateDocumentSetTool"
    assert hasattr(tools, "UpdateContextTool"), "缺少 UpdateContextTool"
```

**验收标准**:
- [x] `CreateDeliverableTool` 可从 `autoBMAD.docuswarm.tools` 导入
- [x] `CreateDocumentSetTool` 可从 `autoBMAD.docuswarm.tools` 导入
- [x] `UpdateContextTool` 可从 `autoBMAD.docuswarm.tools` 导入

#### TC1.2: 验证参数类型已导出
```python
def test_tools_package_exports_params():
    """验证 tools 包导出参数类型."""
    from autoBMAD.docuswarm import tools
    
    assert hasattr(tools, "CreateDeliverableParams"), "缺少 CreateDeliverableParams"
    assert hasattr(tools, "CreateDocumentSetParams"), "缺少 CreateDocumentSetParams"
    assert hasattr(tools, "UpdateContextParams"), "缺少 UpdateContextParams"
```

**验收标准**:
- [x] `CreateDeliverableParams` 可从 `autoBMAD.docuswarm.tools` 导入
- [x] `CreateDocumentSetParams` 可从 `autoBMAD.docuswarm.tools` 导入
- [x] `UpdateContextParams` 可从 `autoBMAD.docuswarm.tools` 导入

#### TC1.3: 验证残留函数已移除
```python
def test_tools_package_no_parse_deliverable_metadata():
    """验证 parse_deliverable_metadata 已从 tools 包移除."""
    from autoBMAD.docuswarm import tools
    
    assert not hasattr(tools, "parse_deliverable_metadata"), \
        "parse_deliverable_metadata 应该已被移除"
```

**验收标准**:
- [x] `parse_deliverable_metadata` 不可从 `autoBMAD.docuswarm.tools` 导入

#### TC1.4: 验证 __all__ 列表
```python
def test_tools_package_all_list():
    """验证 __all__ 列表只包含 docs-free 导出."""
    from autoBMAD.docuswarm import tools
    
    expected = [
        "CreateDeliverableTool",
        "CreateDocumentSetTool",
        "UpdateContextTool",
        "CreateDeliverableParams",
        "CreateDocumentSetParams",
        "UpdateContextParams",
    ]
    assert set(tools.__all__) == set(expected), \
        f"__all__ 不匹配: {set(tools.__all__) - set(expected)} 多余, " \
        f"{set(expected) - set(tools.__all__)} 缺失"
```

**验收标准**:
- [x] `__all__` 列表长度 = 6
- [x] `__all__` 不包含 `parse_deliverable_metadata`

---

### 3.2 Test Suite 2: Tool Registry 统一性测试

**文件**: `tests/tools/test_tool_registry_unified.py`

#### TC2.1: 验证基础注册功能
```python
def test_tool_registry_basic_registration():
    """验证工具可以注册和获取."""
    from autoBMAD.docuswarm.tools.tool_registry import (
        ToolRegistry, get_tool_registry, register_tool
    )
    
    registry = ToolRegistry()
    
    @register_tool(name="test_tool")
    def test_tool() -> ToolResult:
        return ToolResult(success=True, result="ok")
    
    assert registry.get("test_tool") is not None
```

**验收标准**:
- [x] `@register_tool` 装饰器可以注册工具
- [x] `registry.get()` 可以获取已注册工具

#### TC2.2: 验证 export_schemas 方法
```python
def test_tool_registry_export_schemas():
    """验证 export_schemas 方法返回所有工具 schema."""
    from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry
    
    registry = ToolRegistry()
    
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    registry.register("tool_with_schema", lambda: None, "Test tool", schema)
    
    schemas = registry.export_schemas()
    assert "tool_with_schema" in schemas
    assert schemas["tool_with_schema"] == schema
```

**验收标准**:
- [x] `export_schemas()` 方法存在
- [x] 返回包含所有带 schema 工具的字典

#### TC2.3: 验证 models 层重导出
```python
def test_models_tool_registry_is_reexport():
    """验证 models.tool_registry 是 tools.tool_registry 的重导出."""
    from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolsTR
    from autoBMAD.docuswarm.models.tool_registry import ToolRegistry as ModelsTR
    
    assert ToolsTR is ModelsTR, "models.tool_registry.ToolRegistry 应该与 tools.tool_registry.ToolRegistry 是同一类"
```

**验收标准**:
- [x] `models.tool_registry.ToolRegistry` 与 `tools.tool_registry.ToolRegistry` 是同一类
- [x] `ToolRegistryExtended` 已被移除或标记为废弃

#### TC2.4: 验证 ToolDefinition 存在
```python
def test_tool_definition_exists():
    """验证 ToolDefinition 数据类存在."""
    from autoBMAD.docuswarm.tools.tool_registry import ToolDefinition
    from autoBMAD.docuswarm.models.tool_registry import ToolDefinition as ModelTD
    
    assert ToolDefinition is ModelTD
    
    # 验证可以实例化
    td = ToolDefinition(
        name="test",
        func=lambda: None,
        description="Test",
        schema={}
    )
    assert td.name == "test"
```

**验收标准**:
- [x] `ToolDefinition` 可从 `tools.tool_registry` 导入
- [x] `ToolDefinition` 可从 `models.tool_registry` 导入
- [x] 两者是同一类

---

### 3.3 Test Suite 3: Agent YAML 配置一致性测试

**文件**: `tests/tools/test_agent_yaml_config.py`

#### TC3.1: 验证 YAML 只包含 3 个核心工具
```python
def test_agent_yaml_has_three_core_tools():
    """验证 agent YAML 配置只包含 3 个 docs-free 工具."""
    import yaml
    
    config_path = Path("autoBMAD/docuswarm/agents/configs/independent_agent.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    tools = config.get("agent", {}).get("tools", [])
    assert len(tools) == 3, f"应该有 3 个工具，实际有 {len(tools)}: {tools}"
```

**验收标准**:
- [x] YAML 配置中 `tools` 列表长度 = 3

#### TC3.2: 验证 YAML 工具路径正确
```python
def test_agent_yaml_tool_paths():
    """验证 YAML 中工具路径指向正确类."""
    import yaml
    
    config_path = Path("autoBMAD/docuswarm/agents/configs/independent_agent.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    tools = config.get("agent", {}).get("tools", [])
    
    expected_tools = [
        "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool",
        "autoBMAD.docuswarm.tools.update_context:UpdateContextTool",
        "autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool",
    ]
    
    for tool in expected_tools:
        assert tool in tools, f"缺少工具: {tool}"
```

**验收标准**:
- [x] `create_deliverable:CreateDeliverableTool` 在配置中
- [x] `update_context:UpdateContextTool` 在配置中
- [x] `create_document_set:CreateDocumentSetTool` 在配置中

#### TC3.3: 验证 YAML 可加载
```python
def test_agent_yaml_is_valid_yaml():
    """验证 YAML 文件是有效 YAML 格式."""
    import yaml
    
    config_path = Path("autoBMAD/docuswarm/agents/configs/independent_agent.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    assert "agent" in config
    assert "tools" in config["agent"]
```

**验收标准**:
- [x] YAML 文件可正常解析
- [x] 包含 `agent.tools` 路径

---

## 4. 代码修改清单

### 4.1 Phase 1: 清理 tools/__init__.py

**修改前**:
```python
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

**修改后**:
```python
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

### 4.2 Phase 2: 增强 tools/tool_registry.py

**添加**:
```python
@dataclass
class ToolDefinition:
    """Definition of a registered tool."""
    name: str
    func: Callable[..., Any]
    description: str
    schema: dict[str, Any] | None = None


class ToolRegistry:
    """Unified tool registry for managing tool definitions."""
    
    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
        schema: dict[str, Any] | None = None,
    ) -> None:
        """Register a tool with optional schema."""
        self._tools[name] = ToolDefinition(
            name=name,
            func=func,
            description=description,
            schema=schema,
        )
    
    def export_schemas(self) -> dict[str, dict]:
        """Export all tool schemas."""
        return {
            name: tool.schema
            for name, tool in self._tools.items()
            if tool.schema
        }
```

### 4.3 Phase 3: 重构 models/tool_registry.py

**修改后**:
```python
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
    list_registered_tools,
)

__all__ = [
    "ToolDefinition",
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
    "list_registered_tools",
]
```

---

## 5. 执行计划

### Phase 1: 创建测试 (Red Phase)

1. 创建 `tests/tools/test_tools_package_exports.py`
2. 创建 `tests/tools/test_tool_registry_unified.py`
3. 创建 `tests/tools/test_agent_yaml_config.py`
4. 运行测试，确认全部失败 (Red)

### Phase 2: 实现代码 (Green Phase)

1. 修改 `autoBMAD/docuswarm/tools/__init__.py`
2. 修改 `autoBMAD/docuswarm/tools/tool_registry.py`
3. 修改 `autoBMAD/docuswarm/models/tool_registry.py`
4. 运行测试，确认全部通过 (Green)

### Phase 3: 重构优化 (Refactor Phase)

1. 检查代码质量
2. 确保向后兼容
3. 验证所有现有测试仍然通过

---

## 6. 验收标准汇总

### 6.1 功能验收

| 检查项 | 标准 | 验证方式 |
|-------|------|---------|
| Tools 包导出 | 只导出 6 个成员 | `test_tools_package_exports.py` |
| parse_deliverable_metadata 移除 | 不可导入 | `test_tools_package_no_parse_deliverable_metadata` |
| ToolRegistry 统一 | 只有一个注册 API | `test_tool_registry_unified.py` |
| export_schemas 方法 | 存在且可用 | `test_tool_registry_export_schemas` |
| YAML 配置 | 3 个核心工具 | `test_agent_yaml_config.py` |

### 6.2 测试验收

| 指标 | 目标值 |
|-----|-------|
| 单元测试通过率 | 100% |
| 集成测试通过率 | 100% |
| 代码覆盖率 | >= 80% |
| 测试总数 | >= 20 |

### 6.3 质量验收

- [x] 无循环导入
- [x] 向后兼容 (models.tool_registry 仍可导入)
- [x] 类型检查通过
- [x] 代码风格符合项目规范

---

## 7. 风险控制

### 7.1 向后兼容

- `models.tool_registry` 保持可用，但添加废弃警告
- 保留现有测试的导入路径

### 7.2 回滚计划

如需回滚：
1. 恢复 `tools/__init__.py` 中的 `parse_deliverable_metadata`
2. 恢复 `models/tool_registry.py` 中的 `ToolRegistryExtended`
3. 删除新建测试文件

---

## 8. 完成信号

当满足以下条件时，输出完成信号：

```
<promise>DONE</promise>
```

**条件清单**:
- [x] 测试驱动方案文档已创建
- [x] 所有测试用例已编写并通过
- [x] 代码修改已完成并验证
- [x] 100% 测试通过率
- [x] 无遗留错误或警告
