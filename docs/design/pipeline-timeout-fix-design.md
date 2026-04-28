# Pipeline Timeout Fix - Design Document

**版本**: 1.0  
**日期**: 2026-04-06  
**状态**: ✅ 已实施  
**相关文档**: [测试驱动方案](../solution/pipeline-timeout-test-driven-solution.md)

---

## 1. 概述

本文档描述 Pipeline 超时与 MISSING_FILE_PATH 错误修复的设计方案。这些修复解决了 DocuSwarm Pipeline 在处理任务时所有节点都超时失败的问题。

### 1.1 问题摘要

- **症状**: 所有 5 个节点（analyst → pm → ux → architect → po）均超时（1200s）
- **错误码**: `MISSING_FILE_PATH` 
- **根本原因**: 
  1. JSON 示例缺少 `file_path` 和 `sha256` 字段
  2. 超时后 markdown_fallback 无法正确提取工具返回
  3. 超时日志缺少诊断信息

### 1.2 修复概览

| 修复 | 优先级 | 描述 | 状态 |
|------|--------|------|------|
| Fix-1 | P0 | contract_builder JSON 示例 | ✅ |
| Fix-2 | P0 | markdown_fallback + 工具提取 | ✅ |
| Fix-3 | P1 | 超时诊断日志 | ✅ |
| Fix-4 | P1 | CreateDeliverableTool output_dir | ✅ |
| Fix-6 | P1 | system_prompt 路径对齐 | ✅ |

---

## 2. Fix-1: JSON 示例修复

### 2.1 设计目标
确保 LLM 明确知道需要在 JSON 响应中包含 `file_path` 和 `sha256`。

### 2.2 实现

**文件**: `autoBMAD/docuswarm/prompts/contract_builder.py`

**修改**: `_build_instructions_section()` 方法

```python
def _build_instructions_section(self) -> str:
    return """## Agent Instructions

## Execution Workflow

1. **Create Deliverable**: Use the 'create_deliverable' tool
   - The tool returns metadata including: file_path, sha256

2. **Return Execution Report**: After using tools, return JSON

## CRITICAL: Output Format

```json
{
  "deliverable": {
    "title": "Brief title",
    "content": "Brief summary",
    "file_path": "path/returned/by/create_deliverable/tool.md",
    "sha256": "hash_returned_by_create_deliverable_tool"
  },
  "questions": [...],
  "action": "create_deliverable"
}
```

**IMPORTANT**:
- You MUST include "file_path" and "sha256" from the create_deliverable tool output
"""
```

### 2.3 测试
- `test_instructions_section_contains_file_path_example`
- `test_instructions_section_contains_sha256_example`
- `test_complete_json_example_is_valid_json`

---

## 3. Fix-2: Tool Result Extraction

### 3.1 设计目标
超时或 LLM 返回 Markdown 时，能从工具返回中提取 `file_path` 和 `sha256`。

### 3.2 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Response Parsing Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LLM Response                                               │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                       │
│  │ extract_json()  │◀── 首选路径                          │
│  └────────┬────────┘                                       │
│           │ 失败                                            │
│           ▼                                                 │
│  ┌─────────────────────────┐                               │
│  │ markdown_fallback       │                               │
│  │                         │                               │
│  │ 1. _extract_create_    │◀── NEW: 从工具返回提取        │
│  │    deliverable_result() │                               │
│  │    - Parse tool_result  │                               │
│  │    - json.loads()       │                               │
│  │    - Extract file_path  │                               │
│  │                         │                               │
│  │ 2. If found: Build dict │                               │
│  │    with file_path/sha256│                               │
│  │                         │                               │
│  │ 3. If not found: Raise  │                               │
│  │    ResponseParseError   │                               │
│  └─────────────────────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 关键实现

**文件**: `autoBMAD/docuswarm/agents/independent.py`

```python
def _extract_create_deliverable_result(
    self, messages: list[dict[str, Any]]
) -> tuple[str | None, str | None]:
    """从 messages 中提取 create_deliverable 工具的返回结果.
    
    关键: tool_result["content"] 是 JSON字符串，必须先 json.loads()
    """
    for msg in messages:
        for block in msg.get("content", []):
            if block.get("type") != "tool_result" or block.get("is_error"):
                continue
            
            tool_output = block.get("content", {})
            
            # 关键修复: content 是 JSON字符串
            if isinstance(tool_output, str):
                tool_output = json.loads(tool_output)
            
            if isinstance(tool_output, dict) and "file_path" in tool_output:
                return tool_output["file_path"], tool_output.get("sha256", "")
    
    return None, None
```

### 3.4 测试
- `test_extract_from_json_string_content_case_a`
- `test_extract_from_dict_content_case_b`
- `test_extract_skips_error_results`
- `test_markdown_fallback_uses_extracted_tool_result`

---

## 4. Fix-3: Timeout Diagnostics

### 4.1 设计目标
超时日志包含诊断信息，便于分析超时原因。

### 4.2 实现

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
async def prompt(self, message: str, timeout: int | None = None):
    messages_received = 0  # 新增计数器
    
    try:
        async with asyncio.timeout(effective_timeout):
            async for msg in self._client.receive_messages():
                messages_received += 1  # 计数
                yield msg
    except TimeoutError:
        self._logger.error(
            "prompt_timeout",
            timeout_seconds=effective_timeout,
            message_length=len(message),
            messages_received_before_timeout=messages_received,  # 新增
        )
        raise LLMError(...)
```

### 4.3 测试
- `test_timeout_log_contains_messages_received_count`
- `test_timeout_log_contains_message_length`

---

## 5. Fix-4 & Fix-6: 验证项

### 5.1 CreateDeliverableTool output_dir

**状态**: ✅ 已验证支持

```python
# 测试验证
tool = CreateDeliverableTool(output_dir=Path("/output/pipeline-xxx"))
result = await tool._execute(params)
assert Path(result.result["file_path"]).parent == Path("/output/pipeline-xxx")
```

### 5.2 System Prompt 路径对齐

**状态**: ✅ Fix-1 自动覆盖

两条路径现在都包含完整的 `file_path` 和 `sha256` 示例：
- `contract_builder._build_instructions_section()` (生产路径)
- `_format_system_prompt()` (内部路径)

---

## 6. 测试策略

### 6.1 测试结构

```
tests/
├── unit/prompts/
│   ├── test_contract_builder_fix1.py      (6 tests)
│   └── test_contract_builder_regression.py (3 tests)
├── unit/agents/
│   ├── test_independent_agent_fix2.py     (7 tests)
│   └── test_prompt_path_alignment_fix6.py (2 tests)
├── unit/llm/
│   └── test_session_manager_fix3.py       (3 tests)
└── unit/tools/
    └── test_create_deliverable_fix4.py    (4 tests)
```

### 6.2 测试执行

```bash
# 运行全部修复测试
pytest tests/unit/prompts/ tests/unit/agents/ tests/unit/llm/ tests/unit/tools/ -v

# 结果: 25/25 passed
```

---

## 7. 部署影响

### 7.1 向后兼容
- ✅ 修复仅增强现有功能，不破坏 API
- ✅ 所有现有测试通过

### 7.2 监控建议
- 监控 `MISSING_FILE_PATH` 错误率
- 观察超时日志中的 `messages_received_before_timeout`
- 验证文件是否正确写入 `output/{pipeline_id}/`

---

## 8. 参考

- [根因分析报告](../research/pipeline-timeout-root-cause-analysis.md)
- [测试驱动方案](../solution/pipeline-timeout-test-driven-solution.md)
- [修复验证报告](../solution/fix-verification-report.md)
