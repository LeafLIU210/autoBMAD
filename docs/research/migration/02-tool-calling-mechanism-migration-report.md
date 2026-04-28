# DocuSwarm Tool 调用机制完全移除报告

> **奥卡姆剃刀原则**: 如无必要，勿增实体  
> **决策**: 完全移除 kimi-agent-sdk CallableTool2，使用函数式工具  
> **研究日期**: 2026-03-02  
> **主题**: 从 kimi-agent-sdk CallableTool2 迁移到函数式工具

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [当前 Tool 机制分析](#2-当前-tool-机制分析)
3. [目标 Tool 机制](#3-目标-tool-机制)
4. [完全移除方案](#4-完全移除方案)
5. [代码迁移示例](#5-代码迁移示例)
6. [文件修改清单](#6-文件修改清单)
7. [风险评估](#7-风险评估)
8. [测试策略](#8-测试策略)
9. [结论](#9-结论)

---

## 1. 执行摘要

### 1.1 目标

完全移除 DocuSwarm 项目中 `kimi-agent-sdk` 的 `CallableTool2` 工具调用机制。

### 1.2 关键发现

| 维度 | 评估 |
|-----|------|
| **机制差异程度** | 🔴 高 - 类继承 vs 函数式 |
| **影响工具数** | 6 个核心工具 |
| **影响文件数** | 8 个文件 |
| **迁移复杂度** | 🔴 高 |
| **策略** | **完全移除，使用纯函数** |

### 1.3 决策

**不使用兼容层，完全移除**:
- ❌ 不保留 `CallableTool2` 兼容包装
- ❌ 不使用双轨制
- ❌ 不提供类继承接口
- ✅ 使用纯函数实现
- ✅ Pydantic 模型参数验证
- ✅ 简单函数注册机制

---

## 2. 当前 Tool 机制分析

### 2.1 CallableTool2 机制（将被移除）

```python
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue
from pydantic import BaseModel, Field

class CreateDeliverableParams(BaseModel):
    """参数模型"""
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content")
    metadata: dict[str, Any] = Field(default_factory=dict)

class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    """工具类 - 继承 CallableTool2（将被移除）"""
    
    name: str = "create_deliverable"
    description: str = "Create a node deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams
    
    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        """执行工具"""
        try:
            filename = _slugify_filename(params.title)
            file_path = Path.cwd() / filename
            
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)
            
            return ToolOk(output=f"Deliverable saved to {file_path}")
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to write deliverable"
            )
```

### 2.2 当前工具列表（全部需要修改）

| 工具文件 | 基类 | 操作 |
|---------|------|------|
| `create_deliverable.py` | `CallableTool2` | **完全重写** |
| `create_document_set.py` | `CallableTool2` | **完全重写** |
| `read_docs_file.py` | `CallableTool2` | **完全重写** |
| `list_docs_files.py` | `CallableTool2` | **完全重写** |
| `update_docs_file.py` | `CallableTool2` | **完全重写** |
| `update_context.py` | `CallableTool2` | **完全重写** |

---

## 3. 目标 Tool 机制

### 3.1 函数式工具（新方案）

```python
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """统一工具返回结果（新）"""
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] | None = None


class CreateDeliverableParams(BaseModel):
    """创建交付物参数"""
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(default_factory=dict)


async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    """创建交付物 - 纯函数实现（新）
    
    Args:
        params: 创建参数
        
    Returns:
        ToolResult 统一结果
    """
    try:
        filename = _slugify_filename(params.title)
        file_path = Path.cwd() / filename
        
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(params.content)
        
        return ToolResult(
            success=True,
            output=f"Deliverable '{params.title}' saved to {file_path}",
            metadata={"file_path": str(file_path), "title": params.title}
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            output="",
            error=str(exc),
            metadata={"title": params.title}
        )
```

### 3.2 工具注册（新方案）

```python
# models/tool_registry.py

from typing import Callable, Awaitable, Any
from dataclasses import dataclass


@dataclass
class ToolDefinition:
    """工具定义（新）"""
    name: str
    description: str
    parameters: type[BaseModel]
    handler: Callable[[Any], Awaitable[ToolResult]]


class ToolRegistry:
    """工具注册表（新）"""
    
    _tools: dict[str, ToolDefinition] = {}
    
    @classmethod
    def register(cls, definition: ToolDefinition) -> None:
        """注册工具"""
        cls._tools[definition.name] = definition
    
    @classmethod
    def get(cls, name: str) -> ToolDefinition | None:
        """获取工具"""
        return cls._tools.get(name)
    
    @classmethod
    def get_all(cls) -> list[ToolDefinition]:
        """获取所有工具"""
        return list(cls._tools.values())


# 注册工具（新方式）
ToolRegistry.register(ToolDefinition(
    name="create_deliverable",
    description="Create a deliverable document",
    parameters=CreateDeliverableParams,
    handler=create_deliverable
))
```

---

## 4. 完全移除方案

### 4.1 差异对比

| 特性 | Kimi SDK (移除) | 新方案 |
|-----|----------------|--------|
| **实现方式** | 类继承 + 泛型 | 纯函数 |
| **参数验证** | Pydantic 模型 | Pydantic 模型 |
| **返回类型** | `ToolOk` / `ToolError` | `ToolResult` dataclass |
| **注册方式** | YAML 配置 + 类发现 | 显式代码注册 |
| **类型安全** | 高（Generic[T]） | 中（函数签名） |
| **测试难度** | 中（需要实例化类） | 低（直接调用函数） |

### 4.2 移除内容清单

**完全移除（无替代）**:
- `kimi_agent_sdk.CallableTool2` 基类
- `kimi_agent_sdk.ToolOk` 返回类型
- `kimi_agent_sdk.ToolError` 返回类型
- `kimi_agent_sdk.ToolReturnValue` 类型别名
- 类继承模型
- YAML 工具配置

**新实现**:
- `ToolResult` dataclass
- 纯异步函数
- `ToolRegistry` 注册表

---

## 5. 代码迁移示例

### 5.1 create_deliverable 完全迁移

```python
# BEFORE: 完全移除

from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue
from pydantic import BaseModel, Field

class CreateDeliverableParams(BaseModel):
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content")
    metadata: dict[str, Any] = Field(default_factory=dict)

class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    """CallableTool2 实现（将被移除）"""
    
    name: str = "create_deliverable"
    description: str = "Create a node deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams
    
    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        try:
            filename = _slugify_filename(params.title)
            file_path = Path.cwd() / filename
            
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)
            
            return ToolOk(output=f"Deliverable saved to {file_path}")
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to write deliverable"
            )
```

```python
# AFTER: 新实现

"""Create Deliverable Tool - 完全重写版

本模块提供函数式工具实现，无类继承，无 SDK 依赖。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from dataclasses import dataclass

import aiofiles
from pydantic import BaseModel, Field


class CreateDeliverableParams(BaseModel):
    """创建交付物参数"""
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


@dataclass
class ToolResult:
    """工具返回结果"""
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] | None = None


def _slugify_filename(title: str) -> str:
    """转换标题为文件名"""
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.md"


async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    """创建交付物 - 纯函数实现
    
    这是唯一的工具接口，不依赖任何 SDK。
    
    Args:
        params: 创建参数
        
    Returns:
        ToolResult 统一结果
    """
    try:
        filename = _slugify_filename(params.title)
        file_path = Path.cwd() / filename
        
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(params.content)
        
        return ToolResult(
            success=True,
            output=f"Deliverable '{params.title}' saved to {file_path}",
            metadata={
                "file_path": str(file_path),
                "title": params.title
            }
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            output="",
            error=str(exc),
            metadata={"title": params.title}
        )


# 导出
__all__ = [
    "CreateDeliverableParams",
    "ToolResult",
    "create_deliverable",
]
```

### 5.2 工具注册机制迁移

```python
# BEFORE: 完全移除

# agents/configs/independent_agent.yaml
tools:
  - create_deliverable
  - create_document_set
  # SDK 通过类名发现并实例化

# KimiSessionManager
session = await Session.create(
    work_dir=work_dir,
    agent_file=agent_file,  # YAML 包含工具列表
    yolo=True
)
```

```python
# AFTER: 新实现

# models/tool_registry.py

from typing import Any, Callable, Awaitable
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    parameters: type[BaseModel]
    handler: Callable[[Any], Awaitable[Any]]


class ToolRegistry:
    """工具注册表 - 统一管理所有工具"""
    
    _tools: dict[str, ToolDefinition] = {}
    
    @classmethod
    def register(cls, tool: ToolDefinition) -> ToolDefinition:
        """注册工具"""
        cls._tools[tool.name] = tool
        return tool
    
    @classmethod
    def get(cls, name: str) -> ToolDefinition | None:
        """获取工具"""
        return cls._tools.get(name)
    
    @classmethod
    def get_all(cls) -> list[ToolDefinition]:
        """获取所有工具"""
        return list(cls._tools.values())


# 注册所有工具（新方式）
from autoBMAD.docuswarm.tools.create_deliverable import (
    create_deliverable, CreateDeliverableParams
)

ToolRegistry.register(ToolDefinition(
    name="create_deliverable",
    description="Create a deliverable document",
    parameters=CreateDeliverableParams,
    handler=create_deliverable
))
```

---

## 6. 文件修改清单

| 优先级 | 文件 | 修改类型 | 说明 |
|-------|------|---------|------|
| 🔴 高 | `tools/create_deliverable.py` | 重写 | 函数式实现 |
| 🔴 高 | `tools/create_document_set.py` | 重写 | 函数式实现 |
| 🔴 高 | `tools/read_docs_file.py` | 重写 | 函数式实现 |
| 🔴 高 | `tools/list_docs_files.py` | 重写 | 函数式实现 |
| 🔴 高 | `tools/update_docs_file.py` | 重写 | 函数式实现 |
| 🔴 高 | `tools/update_context.py` | 重写 | 函数式实现 |
| 🔴 高 | `models/tool_registry.py` | 新增 | 工具注册表 |
| 🔴 高 | `agents/configs/*.yaml` | 删除 | 移除 YAML 配置 |
| 🟡 中 | `llm/session_manager.py` | 修改 | 使用新工具注册 |

---

## 7. 风险评估

### 7.1 技术风险矩阵

| 风险项 | 概率 | 影响 | 等级 | 缓解措施 |
|-------|------|------|------|---------|
| 参数验证不一致 | 中 | 高 | 🔴 高 | 统一 Pydantic 模型验证 |
| 返回格式不兼容 | 高 | 高 | 🔴 极高 | 完整功能测试 |
| 工具注册失败 | 中 | 高 | 🔴 高 | 显式注册验证 |
| 性能下降 | 低 | 中 | 🟢 低 | 基准测试监控 |

### 7.2 关键风险点

**风险: 参数验证差异**

Kimi SDK 在类级别定义参数模型，新方案需要在注册时显式指定。

**缓解**: 使用 Pydantic 模型，在 `ToolDefinition` 中强制要求。

---

## 8. 测试策略

### 8.1 单元测试

```python
# tests/unit/test_tools.py

import pytest
from autoBMAD.docuswarm.tools.create_deliverable import (
    create_deliverable, CreateDeliverableParams, ToolResult
)


class TestCreateDeliverable:
    """创建交付物工具测试"""
    
    @pytest.mark.asyncio
    async def test_create_success(self, tmp_path):
        """测试成功创建"""
        params = CreateDeliverableParams(
            title="Test Doc",
            content="# Test Content"
        )
        
        result = await create_deliverable(params)
        
        assert result.success is True
        assert "Test Doc" in result.output
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_create_validation_error(self):
        """测试参数验证错误"""
        with pytest.raises(ValidationError):
            CreateDeliverableParams(
                title=None,  # 无效参数
                content="Content"
            )
```

### 8.2 集成测试

```python
# tests/integration/test_tool_registry.py

import pytest
from autoBMAD.docuswarm.models.tool_registry import ToolRegistry, ToolDefinition


class TestToolRegistry:
    """工具注册表集成测试"""
    
    def test_register_and_get(self):
        """测试注册和获取"""
        async def mock_handler(params):
            return ToolResult(success=True, output="OK")
        
        ToolRegistry.register(ToolDefinition(
            name="test_tool",
            description="Test tool",
            parameters=MockParams,
            handler=mock_handler
        ))
        
        tool = ToolRegistry.get("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"
```

---

## 9. 结论

### 9.1 结论

1. **Tool 机制差异是迁移的核心难点**：类继承 vs 函数式需要完全重写。

2. **完全移除是最佳方案**：避免维护兼容层的复杂性。

3. **迁移需要 2-3 周**：包括工具重写和测试更新。

4. **风险可控**：函数式实现更易于测试和维护。

### 9.2 建议

**立即执行**:
1. 创建 `models/tool_registry.py`
2. 重写 `create_deliverable.py` 作为模板
3. 依次重写其他工具
4. 删除 YAML 配置文件

**监控指标**:
- 工具调用成功率
- 参数验证错误率
- 端到端测试通过率

---

*报告完成日期: 2026-03-02*  
*文档版本: 2.0 (完全移除版)*
