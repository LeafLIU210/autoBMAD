# F5: ToolResult 协议统一 - 测试驱动解决方案

> 创建日期: 2026-03-18
> 目标: 统一 DocuSwarm 工具返回协议，消除三叉分裂问题

---

## 1. 问题陈述

当前代码存在 **ToolResult 协议三叉分裂**问题：

| 格式 | 使用位置 | 问题 |
|------|----------|------|
| `ToolOk`/`ToolError` (SDK类型) | `create_deliverable.py`, `create_document_set.py`, `update_context.py` | SDK类型渗透到内部代码 |
| `METADATA: JSON` 字符串 | `create_deliverable.py` 返回文本 | 脆弱的字符串解析 |
| `ToolResult` dataclass | `tool_result.py`, `update_context.py` (部分) | 未全面采用 |

---

## 2. 解决方案架构

### 2.1 核心原则

```
┌─────────────────────────────────────────────────────────────────┐
│                    单一协议原则                                   │
├─────────────────────────────────────────────────────────────────┤
│  1. 内部代码统一使用 ToolResult dataclass                        │
│  2. SDK 边界是唯一转换点（sdk_adapter.py）                        │
│  3. 所有 CallableTool2 工具使用统一包装器模式                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 架构图

```
修复前（三叉分裂）:
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ create_deliver  │   │ create_doc_set  │   │ update_context  │
│   ToolOk +      │   │    ToolOk       │   │   ToolResult    │
│ METADATA字符串   │   │                 │   │  (不一致!)      │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                  ┌───────────────────────┐
                  │ ToolResultExtractor   │
                  │ 需要处理 3 种格式      │
                  └───────────────────────┘

修复后（单一协议）:
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ create_deliver  │   │ create_doc_set  │   │ update_context  │
│   ToolResult    │   │   ToolResult    │   │   ToolResult    │
│   (统一!)       │   │   (统一!)       │   │   (统一!)       │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                  ┌───────────────────────┐
                  │ ToolResultAdapter     │
                  │ 统一转换为 SDK 类型    │
                  └───────────────────────┘
```

---

## 3. 实现步骤

### 3.1 新增文件

1. **`tools/sdk_adapter.py`** - SDK 边界适配层
2. **`tools/callable_tool_wrapper.py`** - CallableTool2 统一包装器

### 3.2 修改文件

1. **`tools/create_deliverable.py`**
   - 使用 `ToolResultCallableTool` 基类
   - 实现 `_execute()` 返回 `ToolResult`
   - 移除 `METADATA:` 字符串拼接

2. **`tools/create_document_set.py`**
   - 同上

3. **`tools/update_context.py`**
   - 同上（虽然部分已是 ToolResult）

4. **`tools/__init__.py`**
   - 导出新的适配器和包装器
   - 保持向后兼容

5. **`tools/tool_result_extractor.py`**
   - 简化，假设输入主要是 ToolResult

---

## 4. 测试策略

### 4.1 测试文件清单

| 测试文件 | 测试目标 |
|----------|----------|
| `tests/tools/test_sdk_adapter.py` | SDK 适配层转换正确性 |
| `tests/tools/test_callable_tool_wrapper.py` | 包装器基类功能 |
| `tests/tools/test_toolresult_protocol.py` | 协议一致性验证 |
| `tests/tools/test_create_deliverable_unit.py` | 创建交付物工具单元测试 |
| `tests/tools/test_create_document_set_unit.py` | 创建文档集工具单元测试 |
| `tests/tools/test_update_context_unit.py` | 更新上下文工具单元测试 |

### 4.2 关键测试用例

#### 4.2.1 SDK 适配层测试

```python
# test_sdk_adapter.py
async def test_adapt_to_sdk_success():
    """ToolResult -> ToolOk"""
    result = ToolResult(success=True, result={"key": "value"})
    sdk_val = adapt_to_sdk(result)
    assert isinstance(sdk_val, ToolOk)

async def test_adapt_to_sdk_error():
    """ToolResult -> ToolError"""
    result = ToolResult(success=False, error="failure")
    sdk_val = adapt_to_sdk(result)
    assert isinstance(sdk_val, ToolError)

async def test_adapt_from_sdk_roundtrip():
    """双向转换保持数据完整"""
```

#### 4.2.2 协议一致性测试

```python
# test_toolresult_protocol.py
async def test_all_tools_return_toolresult_via_execute():
    """验证所有工具内部返回 ToolResult"""
    
async def test_no_raw_toolok_in_internal_code():
    """验证内部代码不直接使用 ToolOk/ToolError"""
    
async def test_metadata_is_structured_not_string():
    """验证 metadata 是结构化数据而非字符串"""
```

#### 4.2.3 工具单元测试

```python
# test_create_deliverable_unit.py
async def test_create_deliverable_returns_toolresult():
    """创建交付物返回 ToolResult"""
    
async def test_create_deliverable_metadata_structure():
    """metadata 包含正确字段"""
    
async def test_create_deliverable_file_creation():
    """文件实际被创建"""
```

---

## 5. 验收标准

### 5.1 功能验收

- [ ] 所有工具内部返回 `ToolResult` 类型
- [ ] SDK 边界正确转换（ToolResult <-> ToolOk/ToolError）
- [ ] `METADATA:` 字符串格式被消除
- [ ] 现有功能保持向后兼容

### 5.2 测试验收

- [ ] `tests/tools/test_sdk_adapter.py` 全部通过
- [ ] `tests/tools/test_toolresult_protocol.py` 全部通过
- [ ] 所有工具单元测试通过
- [ ] 现有测试套件不中断

### 5.3 代码质量验收

- [ ] 类型检查通过（basedpyright）
- [ ] 无循环导入
- [ ] 文档字符串完整

---

## 6. 回滚策略

如果出现问题：
1. 保留原有实现作为 `_legacy` 备份
2. 通过 feature flag 切换
3. 快速回滚到 `ToolOk` 直接返回模式

---

## 7. 完成信号

当满足以下条件时，输出完成信号：

```
<promise>DONE</promise>
```

**完成条件：**
1. 所有工具统一使用 ToolResult 协议
2. 所有测试通过（包括新增和现有）
3. 无 `METADATA:` 字符串残留
4. SDK 适配层工作正常
