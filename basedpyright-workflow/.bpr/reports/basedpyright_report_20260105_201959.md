# BasedPyright 检查报告
**生成时间**: 2026-01-05 20:19:59
**检查时间**: 2026-01-05T20:19:58.582270
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 8 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.64 秒 |

## 🔴 错误详情

共发现 **8** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 8 个错误

### 按规则分组

- `reportUnknownMemberType`: 3 次
- `reportUnknownParameterType`: 1 次
- `reportInvalidTypeForm`: 1 次
- `reportOptionalCall`: 1 次
- `reportUnknownArgumentType`: 1 次
- `reportAttributeAccessIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:55

- **规则**: `reportUnknownParameterType`
- **位置**: 第 55 行, 第 46 列
- **错误信息**: "options" 参数的类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:55

- **规则**: `reportInvalidTypeForm`
- **位置**: 第 55 行, 第 56 列
- **错误信息**: 类型表达式中不允许使用变量

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:70

- **规则**: `reportOptionalCall`
- **位置**: 第 70 行, 第 24 列
- **错误信息**: `None` 不支持调用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:70

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 70 行, 第 53 列
- **错误信息**: 参数类型未知
  实参对应于 "query" 函数中的 "options" 形参

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:74

- **规则**: `reportUnknownMemberType`
- **位置**: 第 74 行, 第 22 列
- **错误信息**: "aclose" 类型未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:74

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 74 行, 第 32 列
- **错误信息**: 无法访问 "AsyncIterator[Message]" 类的 "aclose" 属性
  属性 "aclose" 未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:467

- **规则**: `reportUnknownMemberType`
- **位置**: 第 467 行, 第 23 列
- **错误信息**: "claude_sdk_context" 的类型部分未知
  "claude_sdk_context" 为 "(prompt: str, options: Unknown) -> _AsyncGeneratorContextManager[AsyncIterator[UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent], None]" 类型

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:531

- **规则**: `reportUnknownMemberType`
- **位置**: 第 531 行, 第 31 列
- **错误信息**: "claude_sdk_context" 的类型部分未知
  "claude_sdk_context" 为 "(prompt: str, options: Unknown) -> _AsyncGeneratorContextManager[AsyncIterator[UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent], None]" 类型

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\code_quality_agent.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
6. `..\autoBMAD\epic_automation\qa_agent.py`
7. `..\autoBMAD\epic_automation\qa_tools_integration.py`
8. `..\autoBMAD\epic_automation\sm_agent.py`
9. `..\autoBMAD\epic_automation\state_manager.py`
10. `..\autoBMAD\epic_automation\test_automation_agent.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:55:47 - error: "options" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:55:57 - error: 类型表达式中不允许使用变量 (reportInvalidTypeForm)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:70:25 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:70:54 - error: 参数类型未知
    实参对应于 "query" 函数中的 "options" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:74:23 - error: "aclose" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:74:33 - error: 无法访问 "AsyncIterator[Message]" 类的 "aclose" 属性
    属性 "aclose" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:467:24 - error: "claude_sdk_context" 的类型部分未知
    "claude_sdk_context" 为 "(prompt: str, options: Unknown) -> _AsyncGeneratorContextManager[AsyncIterator[UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent], None]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:531:32 - error: "claude_sdk_context" 的类型部分未知
    "claude_sdk_context" 为 "(prompt: str, options: Unknown) -> _AsyncGeneratorContextManager[AsyncIterator[UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent], None]" 类型 (reportUnknownMemberType)
8 errors, 0 warnings, 0 notes
```

