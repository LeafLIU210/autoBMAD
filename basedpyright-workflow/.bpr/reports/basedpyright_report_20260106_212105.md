# BasedPyright 检查报告
**生成时间**: 2026-01-06 21:21:05
**检查时间**: 2026-01-06T21:21:05.558384
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 9 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.07 秒 |

## 🔴 错误详情

共发现 **9** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 9 个错误

### 按规则分组

- `reportUnknownLambdaType`: 4 次
- `reportUnknownMemberType`: 4 次
- `reportUnknownArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 794 行, 第 43 列
- **错误信息**: "c" 参数的类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 794 行, 第 46 列
- **错误信息**: 该 `lambda` 的返回类型 "Unknown | Literal[True]" 部分未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownMemberType`
- **位置**: 第 794 行, 第 58 列
- **错误信息**: "strip" 类型未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownMemberType`
- **位置**: 第 794 行, 第 58 列
- **错误信息**: "startswith" 类型未知

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 795 行, 第 34 列
- **错误信息**: "c" 参数的类型未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownMemberType`
- **位置**: 第 795 行, 第 49 列
- **错误信息**: "lower" 类型未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:796

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 796 行, 第 41 列
- **错误信息**: "c" 参数的类型未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:796

- **规则**: `reportUnknownMemberType`
- **位置**: 第 796 行, 第 48 列
- **错误信息**: "split" 类型未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:796

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 796 行, 第 48 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794:44 - error: "c" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794:47 - error: 该 `lambda` 的返回类型 "Unknown | Literal[True]" 部分未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794:59 - error: "strip" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794:59 - error: "startswith" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795:35 - error: "c" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795:50 - error: "lower" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:796:42 - error: "c" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:796:49 - error: "split" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:796:49 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
9 errors, 0 warnings, 0 notes
```

