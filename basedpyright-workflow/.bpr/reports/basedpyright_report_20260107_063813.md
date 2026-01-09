# BasedPyright 检查报告
**生成时间**: 2026-01-07 06:38:13
**检查时间**: 2026-01-07T06:38:13.066143
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 5 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.02 秒 |

## 🔴 错误详情

共发现 **5** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 2 个错误

### 按规则分组

- `reportUnknownVariableType`: 1 次
- `reportUnknownMemberType`: 1 次
- `reportAttributeAccessIssue`: 1 次
- `reportIndexIssue`: 1 次
- `reportUnusedVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:340

- **规则**: `reportUnknownVariableType`
- **位置**: 第 340 行, 第 12 列
- **错误信息**: "timeout_context" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:340

- **规则**: `reportUnknownMemberType`
- **位置**: 第 340 行, 第 30 列
- **错误信息**: "timeout" 类型未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:340

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 340 行, 第 38 列
- **错误信息**: "timeout" 不是 "asyncio" 模块的已知属性

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:184

- **规则**: `reportIndexIssue`
- **位置**: 第 184 行, 第 9 列
- **错误信息**: 在 "tuple" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:241

- **规则**: `reportUnusedVariable`
- **位置**: 第 241 行, 第 20 列
- **错误信息**: 变量 "story_id" 未使用

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\code_quality_agent.py`
4. `..\autoBMAD\epic_automation\dev_agent.py`
5. `..\autoBMAD\epic_automation\epic_driver.py`
6. `..\autoBMAD\epic_automation\init_db.py`
7. `..\autoBMAD\epic_automation\log_manager.py`
8. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
9. `..\autoBMAD\epic_automation\qa_agent.py`
10. `..\autoBMAD\epic_automation\qa_tools_integration.py`
11. `..\autoBMAD\epic_automation\sdk_session_manager.py`
12. `..\autoBMAD\epic_automation\sdk_wrapper.py`
13. `..\autoBMAD\epic_automation\sm_agent.py`
14. `..\autoBMAD\epic_automation\state_manager.py`
15. `..\autoBMAD\epic_automation\test_automation_agent.py`
16. `..\autoBMAD\epic_automation\test_logging.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:340:13 - error: "timeout_context" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:340:31 - error: "timeout" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:340:39 - error: "timeout" 不是 "asyncio" 模块的已知属性 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:184:10 - error: 在 "tuple" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:241:21 - error: 变量 "story_id" 未使用 (reportUnusedVariable)
5 errors, 0 warnings, 0 notes
```

