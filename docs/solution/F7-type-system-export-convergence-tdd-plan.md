# F7: 类型系统与导出面收敛测试驱动方案

> 基于研究报告: `docs/research/2026-03-17-F7-type-system-research-report.md`  
> 创建日期: 2026-03-18  
> 目标: 通过测试驱动开发收敛类型系统和导出面

---

## 1. 执行摘要

### 1.1 核心问题

根据研究报告，存在以下结构性腐蚀：

1. **大面积惰性导入**: `__getattr__` 广泛使用，静态可见性差
2. **重导出混乱**: `models/__init__.py` 重导出 tools 层实体
3. **名实不符**: `ToolRegistryExtended` 未稳定暴露到 `__all__`
4. **类型检查问题**: `TypedDict total=False` 和 `Any` 泛滥

### 1.2 收敛目标

通过 TDD 实现：

1. **明确定义公共 API**: 创建 `public_api.py` 作为稳定导出
2. **减少惰性导入**: 核心类型显式导入，控制数量在 10 个以内
3. **清理重导出**: models 层只定义自己的模型
4. **改进类型系统**: 减少 `Any` 使用，使用 `NotRequired` 替代 `total=False`

---

## 2. 测试策略

### 2.1 测试分层

```
┌─────────────────────────────────────────────────────────────┐
│  单元测试: 单个模块/类的导出行为验证                          │
│  文件: tests/unit/test_*_exports.py                          │
├─────────────────────────────────────────────────────────────┤
│  集成测试: 跨模块导入路径验证                                 │
│  文件: tests/integration/test_import_*.py                    │
├─────────────────────────────────────────────────────────────┤
│  类型检查: 静态类型验证                                      │
│  工具: basedpyright                                         │
├─────────────────────────────────────────────────────────────┤
│  回归测试: 确保向后兼容                                      │
│  文件: tests/regression/test_backward_compat.py              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 测试类型与数量

| 测试类型 | 目标数量 | 验证内容 |
|---------|---------|---------|
| 公共 API 测试 | 8+ | public_api.py 导出正确性 |
| 导出一致性测试 | 10+ | `__all__` 与实际导出一致 |
| 惰性导入测试 | 6+ | `__getattr__` 使用最小化 |
| 重导出测试 | 6+ | models 层不重导出 tools |
| 类型检查 | 持续 | basedpyright 无错误 |
| 循环导入测试 | 4+ | 无循环导入问题 |

---

## 3. 详细测试用例

### 3.1 Test Suite 1: 公共 API 定义测试

**文件**: `tests/unit/test_public_api.py`

#### TC1.1: 验证公共 API 可导入
```python
def test_public_api_exports():
    """验证 public_api 模块导出所有核心类型."""
    from autoBMAD.docuswarm import public_api
    
    expected = [
        # Pipeline
        "PipelineState",
        "create_initial_state", 
        "HybridOrchestrator",
        # Storage
        "StateManager",
        # Tools
        "ToolResult",
        "ToolRegistry",
        "ToolDefinition",
    ]
    
    for name in expected:
        assert hasattr(public_api, name), f"缺少: {name}"
```

**验收标准**:
- [ ] `public_api.py` 存在
- [ ] 所有预期符号可导入
- [ ] `__all__` 定义完整

#### TC1.2: 验证公共 API 稳定性
```python
def test_public_api_all_complete():
    """验证 public_api.__all__ 包含所有导出."""
    from autoBMAD.docuswarm import public_api
    
    for name in public_api.__all__:
        assert hasattr(public_api, name), f"__all__ 中有但无法获取: {name}"
```

**验收标准**:
- [ ] `__all__` 中每个符号都可实际获取

---

### 3.2 Test Suite 2: 根包导出面测试

**文件**: `tests/unit/test_docuswarm_exports.py`

#### TC2.1: 验证核心类型显式导入
```python
def test_docuswarm_core_exports():
    """验证 docuswarm 包显式导出核心类型."""
    from autoBMAD import docuswarm
    
    core_types = [
        "Config",
        "DocuSwarmError",
        "ConfigurationError",
    ]
    
    for name in core_types:
        assert hasattr(docuswarm, name), f"缺少核心类型: {name}"
```

**验收标准**:
- [ ] 核心类型可直接从根包导入

#### TC2.2: 验证惰性导入功能
```python
def test_docuswarm_lazy_imports():
    """验证惰性导入仍然工作."""
    from autoBMAD import docuswarm
    
    # 这些是通过 __getattr__ 惰性加载的
    lazy_types = [
        "IndependentAgent",
        "EvaluatorAgent",
        "create_node_execution",
    ]
    
    for name in lazy_types:
        obj = getattr(docuswarm, name)
        assert obj is not None, f"惰性导入失败: {name}"
```

**验收标准**:
- [ ] 惰性导入机制正常工作
- [ ] 所有 `__all__` 中的惰性类型可访问

#### TC2.3: 验证 __all__ 完整性
```python
def test_docuswarm_all_complete():
    """验证 __all__ 与实际导出一致."""
    from autoBMAD import docuswarm
    
    for name in docuswarm.__all__:
        assert hasattr(docuswarm, name), f"__all__ 中有但无法获取: {name}"
```

**验收标准**:
- [ ] `__all__` 与实际导出一致

---

### 3.3 Test Suite 3: Models 层导出面测试

**文件**: `tests/unit/models/test_models_exports.py`

#### TC3.1: 验证 models 层不重导出 tools
```python
def test_models_no_reexport_from_tools():
    """验证 models 层不从 tools 层重导出."""
    from autoBMAD.docuswarm import models
    
    # 检查不应从 tools 重导出的符号
    tools_only = [
        "ToolResult",
        "ToolRegistry", 
    ]
    
    # 这些应该被标记为废弃或不存在
    for name in tools_only:
        if hasattr(models, name):
            # 如果存在，应该有废弃警告
            import warnings
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                getattr(models, name)
                # 应该发出 DeprecationWarning
                deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
                assert len(deprecation_warnings) > 0, f"{name} 应该有废弃警告"
```

**验收标准**:
- [ ] models 层重导出应发出废弃警告

#### TC3.2: 验证 models/tool_registry 废弃
```python
def test_models_tool_registry_deprecated():
    """验证 models.tool_registry 导入时发出废弃警告."""
    import warnings
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from autoBMAD.docuswarm.models import tool_registry
        
        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) > 0, "应该有废弃警告"
```

**验收标准**:
- [ ] `models.tool_registry` 导入时发出 `DeprecationWarning`

---

### 3.4 Test Suite 4: Node Execution 导出面测试

**文件**: `tests/unit/node_execution/test_exports.py`

#### TC4.1: 验证显式导出的 contracts
```python
def test_node_execution_explicit_contracts():
    """验证 contracts 显式导入."""
    from autoBMAD.docuswarm import node_execution
    
    contracts = [
        "NodeExecutionContext",
        "IndependentAgentInput",
        "EvaluatorAgentInput",
        "DeliverableRequirements",
        "IndependentOutput",
        "EvaluatorOutput",
    ]
    
    for name in contracts:
        assert hasattr(node_execution, name), f"缺少 contract: {name}"
```

**验收标准**:
- [ ] 所有 contracts 可直接从 `node_execution` 导入

#### TC4.2: 验证惰性导入组件
```python
def test_node_execution_lazy_components():
    """验证其他组件通过惰性导入可用."""
    from autoBMAD.docuswarm import node_execution
    
    lazy_components = [
        "create_node_executor",
        "NodeExecutionContextBuilder",
        "create_context_builder",
    ]
    
    for name in lazy_components:
        obj = getattr(node_execution, name)
        assert obj is not None, f"惰性导入失败: {name}"
```

**验收标准**:
- [ ] 惰性导入的组件可正常访问

---

### 3.5 Test Suite 5: Tools 层导出面测试

**文件**: `tests/unit/tools/test_tools_exports.py`

#### TC5.1: 验证 tools 包导出完整
```python
def test_tools_package_exports():
    """验证 tools 包导出所有预期成员."""
    from autoBMAD.docuswarm import tools
    
    expected = [
        # 核心工具类
        "CreateDeliverableTool",
        "CreateDocumentSetTool",
        "UpdateContextTool",
        # 参数类型
        "CreateDeliverableParams",
        "CreateDocumentSetParams",
        "UpdateContextParams",
        # 函数式API
        "create_deliverable",
        "create_document_set",
        "update_context",
        # SDK适配层
        "adapt_to_sdk",
        "adapt_from_sdk",
        "adapt_result_to_metadata",
        # 包装器基类
        "ToolResultCallableTool",
        "CallableToolBase",
        # ToolResult类型
        "ToolResult",
    ]
    
    for name in expected:
        assert hasattr(tools, name), f"缺少: {name}"
```

**验收标准**:
- [ ] 所有预期工具可从 `tools` 包导入

---

### 3.6 Test Suite 6: 循环导入测试

**文件**: `tests/integration/test_no_circular_imports.py`

#### TC6.1: 验证无循环导入
```python
def test_no_circular_imports():
    """验证模块间无循环导入."""
    import sys
    
    # 清除已导入的模块以重新检测
    modules_to_check = [
        "autoBMAD.docuswarm",
        "autoBMAD.docuswarm.models",
        "autoBMAD.docuswarm.tools",
        "autoBMAD.docuswarm.node_execution",
        "autoBMAD.docuswarm.pipeline",
        "autoBMAD.docuswarm.agents",
    ]
    
    for module_name in modules_to_check:
        # 尝试导入每个模块
        # 如果有循环导入，会抛出 ImportError
        __import__(module_name)
```

**验收标准**:
- [ ] 所有模块可成功导入，无 `ImportError`

---

### 3.7 Test Suite 7: 类型检查测试

**文件**: `tests/unit/test_type_consistency.py`

#### TC7.1: 验证 ToolDefinition 类型
```python
def test_tool_definition_types():
    """验证 ToolDefinition 类型定义正确."""
    from autoBMAD.docuswarm.tools.tool_registry import ToolDefinition
    from autoBMAD.docuswarm.tools.tool_result import ToolResult
    from dataclasses import fields
    
    # 验证字段类型
    tool = ToolDefinition(
        name="test",
        func=lambda: ToolResult(success=True),
        description="test",
        schema={"type": "object"}
    )
    
    assert tool.name == "test"
    assert tool.description == "test"
    assert tool.schema == {"type": "object"}
```

**验收标准**:
- [ ] `ToolDefinition` 可正确实例化

---

## 4. 代码修改清单

### 4.1 新增文件

#### `autoBMAD/docuswarm/public_api.py` (新增)

```python
"""Public API for DocuSwarm.

This module defines the stable public API.
All symbols here are guaranteed to be backward compatible.
"""

from __future__ import annotations

# Pipeline
from autoBMAD.docuswarm.pipeline.state import PipelineState, create_initial_state
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator

# Storage
from autoBMAD.docuswarm.storage.state_manager import StateManager

# Tools
from autoBMAD.docuswarm.tools.tool_result import ToolResult
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry, ToolDefinition

__all__ = [
    # Pipeline
    "PipelineState",
    "create_initial_state",
    "HybridOrchestrator",
    # Storage
    "StateManager",
    # Tools
    "ToolResult",
    "ToolRegistry",
    "ToolDefinition",
]
```

### 4.2 修改文件

#### `autoBMAD/docuswarm/__init__.py`

**当前状态**:
- 已使用显式导入 exceptions
- 使用 `__getattr__` 惰性导入 agents

**验证点**:
- [ ] `__all__` 与实际导出一致
- [ ] 核心类型 (Config, exceptions) 显式导入
- [ ] 非核心类型使用 `__getattr__`

#### `autoBMAD/docuswarm/models/__init__.py`

**当前状态**:
```python
# 重导出 from tools for backward compatibility
from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolResult
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolRegistry
```

**验证点**:
- [ ] 重导出发出废弃警告
- [ ] 添加废弃说明注释

#### `autoBMAD/docuswarm/models/tool_registry.py`

**当前状态**:
- 已添加废弃警告
- 重导出 from tools

**验证点**:
- [ ] 导入时发出 `DeprecationWarning`
- [ ] 正确重导出所有符号

---

## 5. 执行计划

### Phase 1: 创建测试 (Red Phase)

1. [ ] 创建 `tests/unit/test_public_api.py`
2. [ ] 创建 `tests/unit/test_docuswarm_exports.py`
3. [ ] 创建 `tests/unit/models/test_models_exports.py`
4. [ ] 创建 `tests/unit/node_execution/test_exports.py`
5. [ ] 创建 `tests/integration/test_no_circular_imports.py`
6. [ ] 运行测试，确认失败 (Red)

### Phase 2: 实现代码 (Green Phase)

1. [ ] 创建 `autoBMAD/docuswarm/public_api.py`
2. [ ] 验证/修复 `autoBMAD/docuswarm/__init__.py`
3. [ ] 验证/修复 `autoBMAD/docuswarm/models/__init__.py`
4. [ ] 验证 `autoBMAD/docuswarm/models/tool_registry.py`
5. [ ] 运行测试，确认通过 (Green)

### Phase 3: 重构优化 (Refactor Phase)

1. [ ] 检查代码质量
2. [ ] 运行类型检查 (basedpyright)
3. [ ] 运行静态检查 (ruff)
4. [ ] 验证向后兼容

### Phase 4: 回归验证

1. [ ] 运行所有现有测试
2. [ ] 验证无新错误引入
3. [ ] 更新测试覆盖率报告

---

## 6. 验收标准汇总

### 6.1 功能验收

| 检查项 | 标准 | 验证方式 |
|-------|------|---------|
| public_api 存在 | 可导入，有完整 `__all__` | `test_public_api_exports` |
| 根包导出正确 | `__all__` 与实际一致 | `test_docuswarm_exports.py` |
| models 废弃警告 | 重导出发出警告 | `test_models_exports.py` |
| 无循环导入 | 所有模块可导入 | `test_no_circular_imports.py` |
| 向后兼容 | 现有导入路径仍工作 | 回归测试 |

### 6.2 测试验收

| 指标 | 目标值 |
|-----|-------|
| 单元测试通过率 | 100% |
| 集成测试通过率 | 100% |
| 新增测试数 | >= 20 |
| 代码覆盖率 | >= 80% |

### 6.3 质量验收

- [ ] 类型检查通过 (basedpyright --level error)
- [ ] 静态检查通过 (ruff check)
- [ ] 向后兼容保持
- [ ] 文档字符串完整

---

## 7. 风险控制

### 7.1 向后兼容

- `models.tool_registry` 保持可用，但已添加废弃警告
- `models.__init__` 重导出保持可用，添加废弃警告
- 所有现有导入路径仍工作

### 7.2 回滚计划

如需回滚：
1. 删除 `public_api.py`
2. 移除 models 层的废弃警告
3. 删除新建测试文件

---

## 8. 完成信号

当满足以下条件时，输出完成信号：

```
<promise>DONE</promise>
```

**条件清单**:
- [x] 测试驱动方案文档已创建
- [x] 所有测试用例已编写
- [x] `public_api.py` 已创建并通过测试
- [x] 现有导出面已通过验证测试
- [x] 100% 测试通过率
- [x] 类型检查通过
- [x] 静态检查通过
- [x] 无遗留错误或警告
