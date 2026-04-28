# F5: ToolResult 协议统一深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm 工具返回协议
> 核心问题: ToolResult / ToolResultExtractor / 工具返回格式之间已经分叉

---

## 1. 执行摘要

### 1.1 核心发现

工具返回协议存在**三叉分裂**问题：

1. **结构化 Python dataclass / ToolResult**: 系统内部推荐使用，但未全面采用
2. **字符串内嵌 METADATA: JSON**: 边界兼容层，依赖脆弱
3. **kimi SDK ToolOk/ToolError**: SDK 边界使用，但不应作为系统内部格式

当前代码同时存在三种格式，导致转换、解析逻辑复杂且易出错。

### 1.2 关键代码证据

```python
# autoBMAD/docuswarm/tools/tool_result.py:8
@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    result: Any = None
    error: str | None = None

# autoBMAD/docuswarm/tools/create_deliverable.py:169
# ❌ 使用 METADATA: JSON 字符串
output_text = (
    f"Deliverable '{params.title}' saved to {file_path}\n\n"
    f"METADATA: {json.dumps(metadata, ensure_ascii=False)}"
)
return ToolOk(output=output_text)  # ❌ 返回 SDK 类型

# autoBMAD/docuswarm/tools/update_context.py:198
# ✅ 返回结构化 ToolResult（不一致！）
return ToolResult(
    success=True,
    result={"message": "Context updated", ...},
)
```

---

## 2. 详细分析

### 2.1 工具返回格式全景

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          工具返回格式现状                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  工具实现层                                                              │
│  ├── create_deliverable.py                                            │
│  │   └── return ToolOk(output="...METADATA: {...}")  ❌ SDK 类型       │
│  │                                                  + 字符串 METADATA   │
│  ├── create_document_set.py                                           │
│  │   └── return ToolOk(output=...)                   ❌ SDK 类型        │
│  └── update_context.py                                                │
│      └── return ToolResult(...)                      ✅ 结构化          │
│                     ⚠️ 不一致！                                         │
│                                                                         │
│  解析/提取层                                                             │
│  ├── ToolResultExtractor                                              │
│  │   ├── isinstance(response, ToolResult)  ←─ 处理结构化               │
│  │   ├── ToolResult.from_dict(response)    ←─ 处理字典                 │
│  │   └── ToolResult(success=True, result=response)  ←─ 兜底            │
│  └── parse_deliverable_metadata()            ←─ 解析 METADATA 字符串    │
│                                                                         │
│  消费层 (Agent)                                                         │
│  └── 需要处理多种格式：ToolResult | ToolOk | ToolError | dict | str     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 三种格式详细分析

#### 2.2.1 结构化 ToolResult（推荐）

```python
# tools/tool_result.py
@dataclass
class ToolResult:
    success: bool
    result: Any = None
    error: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {"success": self.success, "result": self.result, "error": self.error}
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolResult":
        return cls(
            success=data.get("success", False),
            result=data.get("result"),
            error=data.get("error"),
        )
```

**优点**:
- 类型可检查、IDE 友好
- 便于测试和序列化
- 能自然承载 file_path / sha256 / section_index / warnings 等结构化字段

**缺点**:
- 若外部 SDK 边界只接受文本，需要额外适配层

#### 2.2.2 METADATA: JSON 字符串

```python
# create_deliverable.py 中的实现
output_text = (
    f"Deliverable '{params.title}' saved to {file_path}\n\n"
    f"METADATA: {json.dumps(metadata, ensure_ascii=False)}"
)
return ToolOk(output=output_text)
```

**解析代码**:

```python
# tools/__init__.py
def parse_deliverable_metadata(output: str) -> dict[str, Any]:
    if "METADATA:" not in output:
        return {}
    json_part = output.split("METADATA:")[1].strip()
    return json.loads(json_part)
```

**问题**:
- 依赖字符串分隔符，天然脆弱
- 容易被文案或换行污染
- 迫使 ToolResultExtractor、测试和 Agent 一起承担文本解析负担

#### 2.2.3 kimi SDK ToolOk/ToolError

```python
# kimi_agent_sdk types
class ToolOk:
    def __init__(self, output: str, message: str = ""):
        self.output = output
        self.message = message

class ToolError:
    def __init__(self, output: str, message: str, brief: str = ""):
        self.output = output
        self.message = message
        self.brief = brief
```

**问题**:
- 把系统内部事实格式绑死到特定 SDK 类型
- 已经与 ToolResult/dataclass 和 METADATA 文本兼容层形成三叉分裂

### 2.3 当前代码中的混乱

#### 2.3.1 同一目录下的不一致

```python
# create_deliverable.py - 使用 ToolOk + METADATA 字符串
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue

async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
    # ...
    return ToolOk(output=output_text)

# update_context.py - 使用 ToolResult
from autoBMAD.docuswarm.models.tool import ToolResult

async def update_context(params: UpdateContextParams) -> ToolResult:
    # ...
    return ToolResult(success=True, result={...})
```

#### 2.3.2 ToolResultExtractor 的适配负担

```python
# tools/tool_result_extractor.py:103-109
if isinstance(response, ToolResult):
    return response
elif isinstance(response, dict):
    return ToolResult.from_dict(response)
else:
    return ToolResult(success=True, result=response)
```

**问题**: 需要处理多种输入类型，增加复杂性和维护成本。

---

## 3. 收敛方案

### 3.1 决策：结构化 ToolResult 为主协议

| 格式 | 适配结论 | 用途 |
|------|----------|------|
| **结构化 Python dataclass / ToolResult** | ✅ 推荐为主协议 | 系统内部稳定演进契约 |
| **字符串内嵌 METADATA: JSON** | ⚠️ 仅边界兼容层 | SDK 边界适配 |
| **kimi SDK ToolOk/ToolError** | ❌ 明确拒绝 | SDK 调用边界，不扩散到内部 |

### 3.2 具体收敛动作

#### 3.2.1 统一工具返回类型

```python
# tools/create_deliverable.py - 修改后
from autoBMAD.docuswarm.tools.tool_result import ToolResult

class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    # ...
    
    async def __call__(self, params: CreateDeliverableParams) -> ToolResult:  # ✅ 统一
        try:
            # ... 写入文件 ...
            
            metadata = {
                "title": params.title,
                "file_path": str(file_path),
                "sha256": sha256_hash,
                "word_count": word_count,
                "section_index": section_index,
            }
            
            # ✅ 返回结构化 ToolResult
            return ToolResult(
                success=True,
                result=metadata,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )
```

#### 3.2.2 统一 create_document_set.py

```python
# tools/create_document_set.py - 修改后
async def __call__(self, params: CreateDocumentSetParams) -> ToolResult:
    try:
        # ... 创建文档集 ...
        
        return ToolResult(
            success=True,
            result={
                "document_set_id": doc_set_id,
                "documents": created_docs,
            },
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e),
        )
```

#### 3.2.3 SDK 边界适配层

```python
# tools/sdk_adapter.py - 新增
"""SDK 边界适配层 - 将内部 ToolResult 转换为 SDK 所需格式."""

from kimi_agent_sdk import ToolOk, ToolError, ToolReturnValue
from autoBMAD.docuswarm.tools.tool_result import ToolResult

def adapt_to_sdk(result: ToolResult) -> ToolReturnValue:
    """将内部 ToolResult 转换为 SDK ToolReturnValue.
    
    这是唯一的 SDK 适配点，所有工具内部返回 ToolResult。
    """
    if result.success:
        # 将结构化结果序列化为 JSON 字符串
        import json
        output = json.dumps(result.result, ensure_ascii=False) if result.result else ""
        return ToolOk(output=output)
    else:
        return ToolError(
            output="",
            message=result.error or "Unknown error",
            brief="Tool execution failed",
        )


def adapt_from_sdk(response: ToolReturnValue) -> ToolResult:
    """将 SDK 响应转换为内部 ToolResult.
    
    用于处理 SDK 返回的 ToolOk/ToolError。
    """
    if isinstance(response, ToolOk):
        # 尝试解析 JSON 输出
        import json
        try:
            result = json.loads(response.output) if response.output else None
        except json.JSONDecodeError:
            result = {"output": response.output}
        
        return ToolResult(success=True, result=result)
    
    elif isinstance(response, ToolError):
        return ToolResult(
            success=False,
            error=response.message,
        )
    
    else:
        return ToolResult(
            success=False,
            error=f"Unknown response type: {type(response)}",
        )
```

#### 3.2.4 CallableTool2 包装器

```python
# tools/callable_tool_wrapper.py - 新增
"""CallableTool2 包装器 - 内部 ToolResult 与 SDK 的桥梁."""

from typing import TypeVar, Generic
from kimi_agent_sdk import CallableTool2, ToolReturnValue
from autoBMAD.docuswarm.tools.tool_result import ToolResult
from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_sdk

P = TypeVar("P")

class ToolResultCallableTool(CallableTool2[P], Generic[P]):
    """Base class for tools that internally use ToolResult.
    
    Subclasses implement _execute() returning ToolResult,
    this wrapper handles SDK adaptation.
    """
    
    async def __call__(self, params: P) -> ToolReturnValue:
        """Execute tool and adapt result to SDK format."""
        result = await self._execute(params)
        return adapt_to_sdk(result)
    
    async def _execute(self, params: P) -> ToolResult:
        """Execute tool and return ToolResult.
        
        Subclasses must implement this method.
        """
        raise NotImplementedError
```

#### 3.2.5 修改后的工具实现示例

```python
# tools/create_deliverable.py - 使用包装器
from autoBMAD.docuswarm.tools.callable_tool_wrapper import ToolResultCallableTool
from autoBMAD.docuswarm.tools.tool_result import ToolResult

class CreateDeliverableTool(ToolResultCallableTool[CreateDeliverableParams]):
    name: str = "create_deliverable"
    description: str = "Create a node deliverable document..."
    params: type[CreateDeliverableParams] = CreateDeliverableParams
    
    async def _execute(self, params: CreateDeliverableParams) -> ToolResult:
        """Internal execution returning ToolResult."""
        try:
            filename = _slugify_filename(params.title)
            file_path = Path.cwd() / filename
            
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)
            
            metadata = {
                "title": params.title,
                "file_path": str(file_path),
                "sha256": _compute_sha256(params.content),
                "word_count": _count_words(params.content),
                "section_index": _extract_section_index(params.content),
            }
            
            return ToolResult(success=True, result=metadata)
            
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))
```

### 3.3 ToolResultExtractor 简化

```python
# tools/tool_result_extractor.py - 简化后
"""Tool Result Extractor - simplified version.

All tools now return ToolResult, so this module is mainly for
legacy compatibility and type checking.
"""

from autoBMAD.docuswarm.tools.tool_result import ToolResult


class ToolResultExtractor:
    """Extract ToolResult from various response formats (legacy support)."""
    
    @staticmethod
    def extract(response: ToolResult | dict | Any) -> ToolResult:
        """Extract ToolResult from response.
        
        All internal tools should return ToolResult directly.
        This method handles legacy formats for backward compatibility.
        """
        if isinstance(response, ToolResult):
            return response
        
        if isinstance(response, dict):
            return ToolResult.from_dict(response)
        
        # Legacy: wrap unknown types
        return ToolResult(success=True, result=response)
```

---

## 4. 测试建议

### 4.1 工具返回类型一致性测试

```python
async def test_all_tools_return_toolresult():
    """验证所有工具内部返回 ToolResult."""
    from autoBMAD.docuswarm.tools import (
        CreateDeliverableTool,
        CreateDocumentSetTool,
        UpdateContextTool,
    )
    from autoBMAD.docuswarm.tools.tool_result import ToolResult
    
    tools = [
        CreateDeliverableTool(),
        CreateDocumentSetTool(),
        UpdateContextTool(state_manager=mock_state_manager, pipeline_id="test"),
    ]
    
    for tool in tools:
        # 检查 _execute 方法返回类型
        if hasattr(tool, '_execute'):
            import inspect
            sig = inspect.signature(tool._execute)
            # 验证返回类型注解
            assert sig.return_annotation == ToolResult, \
                f"{tool.name}._execute should return ToolResult"
```

### 4.2 SDK 适配层测试

```python
def test_sdk_adapter_roundtrip():
    """验证 ToolResult <-> SDK 类型转换."""
    from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_sdk, adapt_from_sdk
    from autoBMAD.docuswarm.tools.tool_result import ToolResult
    from kimi_agent_sdk import ToolOk
    
    # ToolResult -> SDK
    result = ToolResult(success=True, result={"key": "value"})
    sdk_response = adapt_to_sdk(result)
    assert isinstance(sdk_response, ToolOk)
    
    # SDK -> ToolResult
    recovered = adapt_from_sdk(sdk_response)
    assert recovered.success == result.success
    assert recovered.result == result.result
```

### 4.3 边界兼容性测试

```python
async def test_tool_output_format():
    """验证工具输出格式符合预期."""
    tool = CreateDeliverableTool()
    
    # Mock 参数
    params = CreateDeliverableParams(
        title="Test Document",
        content="# Test\n\nContent",
    )
    
    # 执行（使用 _execute 获取 ToolResult）
    result = await tool._execute(params)
    
    # 验证是 ToolResult
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert "file_path" in result.result
    assert "sha256" in result.result
```

---

## 5. 代码修改清单

### 5.1 新增文件

- [ ] `tools/sdk_adapter.py` - SDK 边界适配层
- [ ] `tools/callable_tool_wrapper.py` - ToolResult CallableTool2 包装器

### 5.2 修改文件

- [ ] `tools/create_deliverable.py`
  - 使用 `ToolResultCallableTool`
  - 实现 `_execute()` 返回 `ToolResult`
  - 移除 `METADATA:` 字符串拼接

- [ ] `tools/create_document_set.py`
  - 同上

- [ ] `tools/update_context.py`
  - 保持一致（已经是 ToolResult）

- [ ] `tools/tool_result_extractor.py`
  - 简化，假设输入主要是 ToolResult

- [ ] `tools/__init__.py`
  - 删除 `parse_deliverable_metadata`
  - 导出 `ToolResult`

### 5.3 测试覆盖

- [ ] 工具返回类型一致性测试
- [ ] SDK 适配层往返测试
- [ ] 边界兼容性测试

---

## 6. 结论

1. **ToolResult 应该成为系统内部唯一协议**，这是类型安全和可维护性的基础
2. **SDK 适配层是唯一转换点**，所有 SDK 边界转换集中管理
3. **METADATA 字符串应该被淘汰**，用结构化数据替代
4. **ToolOk/ToolError 不应扩散到内部**，限制在 SDK 调用边界

---

## 附录: 协议对比图

### 修复前（三叉分裂）

```
工具实现
    ├── create_deliverable: ToolOk + METADATA 字符串
    ├── create_document_set: ToolOk
    └── update_context: ToolResult
            ↓
ToolResultExtractor: 需要处理 3 种格式
    ├── isinstance(response, ToolResult)
    ├── isinstance(response, dict) → from_dict
    └── else: wrap
            ↓
Agent: 接收不确定格式
```

### 修复后（单一协议）

```
工具实现（统一）
    ├── create_deliverable: ToolResult ──┐
    ├── create_document_set: ToolResult ─┼── 内部统一
    └── update_context: ToolResult ──────┘
            ↓
SDK Adapter（唯一转换点）
    └── ToolResult → ToolOk/ToolError（仅在 SDK 边界）
            ↓
Agent: 接收统一 ToolResult
```
