# Epic 18: Tool Calling Mechanism Migration

> **⚠️ 完全移除**: 本 Epic 完全移除 `kimi-agent-sdk` CallableTool2，使用函数式工具  
> **决策**: 零向后兼容，完全移除类继承模型，使用纯函数  
> **参考**: [Tool 调用机制迁移研究报告](../research/migration/02-tool-calling-mechanism-migration-report.md)

**Epic ID**: EPIC-18  
**Version**: 1.0 (完全移除版)  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 2 (Kimi SDK Removal)

---

## 1. Epic Overview

### 1.1 Summary

**完全移除** `kimi-agent-sdk` 的 `CallableTool2` 类继承模型，将所有工具迁移到纯函数实现。这是 Kimi SDK 完全移除的核心步骤之一，标志着从类继承模式向函数式编程模式的转变。

### 1.2 Business Value

- **完全移除 Kimi SDK**: 消除对 `kimi_agent_sdk.CallableTool2` 的依赖
- **简化架构**: 函数式实现比类继承更简单
- **易于测试**: 纯函数更容易单元测试
- **类型安全**: 使用 Pydantic 模型进行参数验证

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| CallableTool2 移除 | 项目中无 `kimi_agent_sdk.CallableTool2` 导入 |
| 工具重写 | 所有 6 个工具重写为函数式 |
| YAML 配置移除 | 删除所有 YAML 工具配置 |
| 功能保持 | 所有工具功能正常工作 |

### 1.4 Dependencies

- **Requires**: Epic 17 (Message Format Migration) completed
- **Blocks**: Epic 19 (Test Migration)

---

## 2. Architecture Context

### 2.1 Migration Overview

```
Before (v4.x - 迁移中):
  ┌─────────────────────────────────────────────────────────────┐
  │  CallableTool2 类继承模型                                    │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ class MyTool(CallableTool2[Params]):               │   │
  │  │     name = "my_tool"                               │   │
  │  │     params = Params                                │   │
  │  │                                                    │   │
  │  │     async def __call__(self, params) -> ToolOk:   │   │
  │  │         ...                                        │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  YAML 配置: tools/my_tool.yaml                              │
  └─────────────────────────────────────────────────────────────┘

After (v5.0 - 完全移除):
  ┌─────────────────────────────────────────────────────────────┐
  │  函数式工具模型                                              │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ @dataclass                                          │   │
  │  │ class ToolResult:                                   │   │
  │  │     success: bool                                   │   │
  │  │     output: str                                     │   │
  │  │     error: str | None                               │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  async def my_tool(params: Params) -> ToolResult:          │
  │      ...                                                    │
  │      return ToolResult(success=True, output="...")         │
  │                                                             │
  │  ToolRegistry.register(ToolDefinition(...))                │
  └─────────────────────────────────────────────────────────────┘
```

### 2.2 Key Changes

| 组件 | 当前 (Kimi SDK) | 目标 (新方案) |
|------|----------------|--------------|
| 实现方式 | 类继承 + 泛型 | 纯函数 |
| 返回类型 | `ToolOk` / `ToolError` | `ToolResult` dataclass |
| 注册方式 | YAML 配置 + 类发现 | 显式代码注册 |
| 参数验证 | Pydantic 模型 | Pydantic 模型 |

### 2.3 Tool List

| 工具文件 | 当前基类 | 操作 |
|---------|----------|------|
| `tools/create_deliverable.py` | `CallableTool2` | **完全重写** |
| `tools/create_document_set.py` | `CallableTool2` | **完全重写** |
| `tools/read_docs_file.py` | `CallableTool2` | **完全重写** |
| `tools/list_docs_files.py` | `CallableTool2` | **完全重写** |
| `tools/update_docs_file.py` | `CallableTool2` | **完全重写** |
| `tools/update_context.py` | `CallableTool2` | **完全重写** |

---

## 3. User Stories

### Story 18.1: ToolResult Dataclass Creation

**ID**: US-18.1  
**As a** developer  
**I want to** create a unified ToolResult dataclass  
**So that** all tools return consistent results

**Acceptance Criteria**:
- [ ] 创建 `ToolResult` dataclass
- [ ] 包含 `success`, `output`, `error`, `metadata` 字段
- [ ] 支持 JSON 序列化
- [ ] 提供清晰的文档字符串

**Technical Tasks**:
1. 创建 `docuswarm/models/tool.py`
2. 定义 `ToolResult` dataclass
3. 添加字段验证
4. 编写单元测试

**Implementation**:

```python
# docuswarm/models/tool.py

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """统一工具返回结果。
    
    所有工具函数必须返回此类型，提供一致的接口。
    
    Attributes:
        success: 工具执行是否成功
        output: 工具输出内容
        error: 错误信息（如果失败）
        metadata: 附加元数据
    """
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }
```

**Definition of Done**:
- ToolResult dataclass 创建完成
- 所有字段有类型提示
- 单元测试通过

---

### Story 18.2: ToolRegistry Implementation

**ID**: US-18.2  
**As a** developer  
**I want to** create a ToolRegistry for tool registration  
**So that** tools can be registered and discovered

**Acceptance Criteria**:
- [ ] 创建 `ToolDefinition` dataclass
- [ ] 创建 `ToolRegistry` 类
- [ ] 支持 `register()` 方法
- [ ] 支持 `get()` 方法
- [ ] 支持 `get_all()` 方法

**Technical Tasks**:
1. 创建 `docuswarm/models/tool_registry.py`
2. 定义 `ToolDefinition` dataclass
3. 实现 `ToolRegistry` 类
4. 编写单元测试

**Implementation**:

```python
# docuswarm/models/tool_registry.py

from typing import Callable, Awaitable, Any
from dataclasses import dataclass
from pydantic import BaseModel

from autoBMAD.docuswarm.models.tool import ToolResult


@dataclass
class ToolDefinition:
    """工具定义。
    
    描述一个工具的名称、描述、参数模型和处理函数。
    """
    name: str
    description: str
    parameters: type[BaseModel]
    handler: Callable[[Any], Awaitable[ToolResult]]


class ToolRegistry:
    """工具注册表 - 统一管理所有工具。"""
    
    _tools: dict[str, ToolDefinition] = {}
    
    @classmethod
    def register(cls, tool: ToolDefinition) -> ToolDefinition:
        """注册工具。"""
        cls._tools[tool.name] = tool
        return tool
    
    @classmethod
    def get(cls, name: str) -> ToolDefinition | None:
        """获取工具定义。"""
        return cls._tools.get(name)
    
    @classmethod
    def get_all(cls) -> list[ToolDefinition]:
        """获取所有工具定义。"""
        return list(cls._tools.values())
    
    @classmethod
    def clear(cls) -> None:
        """清空注册表（仅用于测试）。"""
        cls._tools.clear()
```

**Definition of Done**:
- ToolRegistry 实现完成
- 所有方法有文档字符串
- 单元测试通过

---

### Story 18.3: CreateDeliverable Tool Migration

**ID**: US-18.3  
**As a** developer  
**I want to** rewrite create_deliverable tool as function  
**So that** it doesn't depend on CallableTool2

**Acceptance Criteria**:
- [ ] 移除 `CallableTool2` 继承
- [ ] 创建 `create_deliverable` 纯函数
- [ ] 使用 `CreateDeliverableParams` Pydantic 模型
- [ ] 返回 `ToolResult` 类型
- [ ] 注册到 `ToolRegistry`

**Technical Tasks**:
1. 修改 `docuswarm/tools/create_deliverable.py`
2. 移除类继承实现
3. 创建纯函数实现
4. 更新导入语句
5. 更新单元测试

**Before/After**:

```python
# BEFORE: 完全移除

from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue

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

"""Create Deliverable Tool - 函数式实现。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field

from autoBMAD.docuswarm.models.tool import ToolResult


class CreateDeliverableParams(BaseModel):
    """创建交付物参数。"""
    title: str = Field(description="交付物标题")
    content: str = Field(description="交付物内容 (Markdown)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="附加元数据"
    )


def _slugify_filename(title: str) -> str:
    """转换标题为文件名。"""
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.md"


async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    """创建交付物 - 纯函数实现。
    
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
    "create_deliverable",
]
```

**Definition of Done**:
- create_deliverable 重写为函数
- 所有功能正常工作
- 单元测试通过

---

### Story 18.4: Other Tools Migration

**ID**: US-18.4  
**As a** developer  
**I want to** rewrite remaining tools as functions  
**So that** no tool depends on CallableTool2

**Acceptance Criteria**:
- [ ] `create_document_set` 重写为函数
- [ ] `read_docs_file` 重写为函数
- [ ] `list_docs_files` 重写为函数
- [ ] `update_docs_file` 重写为函数
- [ ] `update_context` 重写为函数
- [ ] 所有工具注册到 `ToolRegistry`

**Technical Tasks**:
1. 重写 `docuswarm/tools/create_document_set.py`
2. 重写 `docuswarm/tools/read_docs_file.py`
3. 重写 `docuswarm/tools/list_docs_files.py`
4. 重写 `docuswarm/tools/update_docs_file.py`
5. 重写 `docuswarm/tools/update_context.py`
6. 更新单元测试

**Implementation Pattern**:

```python
# 所有工具遵循相同模式

class ToolParams(BaseModel):
    """工具参数。"""
    ...


async def tool_name(params: ToolParams) -> ToolResult:
    """工具函数。"""
    try:
        # 执行逻辑
        return ToolResult(success=True, output="...")
    except Exception as exc:
        return ToolResult(success=False, output="", error=str(exc))
```

**Definition of Done**:
- 所有 6 个工具重写为函数
- 所有工具功能正常工作
- 单元测试通过

---

### Story 18.5: YAML Config Removal

**ID**: US-18.5  
**As a** developer  
**I want to** remove YAML tool configuration files  
**So that** tool configuration is code-based

**Acceptance Criteria**:
- [ ] 删除 `agents/configs/independent_agent.yaml`
- [ ] 删除其他 YAML 工具配置
- [ ] 在代码中显式注册工具
- [ ] 更新所有引用 YAML 的代码

**Technical Tasks**:
1. 识别所有 YAML 配置文件
2. 删除 YAML 文件
3. 在 `__init__.py` 或配置模块中显式注册工具
4. 更新引用代码
5. 更新测试

**Implementation**:

```python
# docuswarm/tools/__init__.py

"""工具模块初始化 - 显式注册所有工具。"""

from autoBMAD.docuswarm.models.tool_registry import ToolRegistry, ToolDefinition

from autoBMAD.docuswarm.tools.create_deliverable import (
    create_deliverable, CreateDeliverableParams
)
from autoBMAD.docuswarm.tools.create_document_set import (
    create_document_set, CreateDocumentSetParams
)
# ... 其他导入


def register_all_tools() -> None:
    """注册所有工具到 ToolRegistry。"""
    ToolRegistry.register(ToolDefinition(
        name="create_deliverable",
        description="Create a deliverable document",
        parameters=CreateDeliverableParams,
        handler=create_deliverable
    ))
    
    ToolRegistry.register(ToolDefinition(
        name="create_document_set",
        description="Create a set of related documents",
        parameters=CreateDocumentSetParams,
        handler=create_document_set
    ))
    
    # ... 其他工具注册


# 自动注册
register_all_tools()
```

**Definition of Done**:
- 所有 YAML 配置删除
- 工具显式注册
- 所有功能正常工作

---

## 4. Technical Specifications

### 4.1 New Modules

| Module | Location | Purpose |
|--------|----------|---------|
| `ToolResult` | `docuswarm/models/tool.py` | 统一工具返回结果 |
| `ToolDefinition` | `docuswarm/models/tool_registry.py` | 工具定义 dataclass |
| `ToolRegistry` | `docuswarm/models/tool_registry.py` | 工具注册表 |

### 4.2 Modified Modules

| Module | Location | Changes |
|--------|----------|---------|
| `create_deliverable` | `docuswarm/tools/create_deliverable.py` | 函数式实现 |
| `create_document_set` | `docuswarm/tools/create_document_set.py` | 函数式实现 |
| `read_docs_file` | `docuswarm/tools/read_docs_file.py` | 函数式实现 |
| `list_docs_files` | `docuswarm/tools/list_docs_files.py` | 函数式实现 |
| `update_docs_file` | `docuswarm/tools/update_docs_file.py` | 函数式实现 |
| `update_context` | `docuswarm/tools/update_context.py` | 函数式实现 |

### 4.3 Removed Files

| File | Reason |
|------|--------|
| `agents/configs/*.yaml` | 使用代码注册替代 |

### 4.4 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/test_tools.py` | 100% pass |
| Integration tests | `pytest tests/integration/` | Pass |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 参数验证不一致 | 中 | 高 | 统一使用 Pydantic 模型 |
| 返回格式不兼容 | 高 | 高 | 完整功能测试 |
| 工具注册失败 | 中 | 高 | 显式注册验证 |
| 性能下降 | 低 | 中 | 基准测试监控 |

---

## 6. Definition of Done (Epic Level)

- [ ] 所有 Story 完成并测试通过
- [ ] 项目中无 `kimi_agent_sdk.CallableTool2` 导入
- [ ] 项目中无 `ToolOk` / `ToolError` 使用
- [ ] 所有 6 个工具重写为函数式
- [ ] ToolResult dataclass 创建完成
- [ ] ToolRegistry 实现完成
- [ ] 所有 YAML 配置删除
- [ ] 所有工具显式注册
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 类型检查通过
- [ ] Linting 通过

---

## 7. References

| Document | Location |
|----------|----------|
| Tool 调用机制迁移报告 | `docs/research/migration/02-tool-calling-mechanism-migration-report.md` |
| Epic 17 Message 迁移 | `docs/epics/EPIC-17-MESSAGE-FORMAT-MIGRATION.md` |
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` |

---

**Epic End**
