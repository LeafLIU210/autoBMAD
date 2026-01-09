# BasedPyright 检查报告
**生成时间**: 2026-01-08 12:29:12
**检查时间**: 2026-01-08T12:29:12.318951
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 15 |
| ❌ 错误 (Error) | 4 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.76 秒 |

## 🔴 错误详情

共发现 **4** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py`: 1 个错误

### 按规则分组

- `reportUnknownArgumentType`: 2 次
- `reportUnnecessaryComparison`: 1 次
- `reportUnusedImport`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:430

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 430 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:84

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 84 行, 第 52 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "generate_test_report" 函数中的 "results" 形参
  参数类型为 "dict[str, str | dict[str, int | float] | list[Unknown]]"

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:184

- **规则**: `reportUnnecessaryComparison`
- **位置**: 第 184 行, 第 19 列
- **错误信息**: 条件的计算结果始终为 `True`，因为类型 "type[ResultMessage]" 和 "None" 之间不存在交集

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:267

- **规则**: `reportUnusedImport`
- **位置**: 第 267 行, 第 19 列
- **错误信息**: "debugpy" 导入项未使用

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\init_db.py`
6. `..\autoBMAD\epic_automation\log_manager.py`
7. `..\autoBMAD\epic_automation\qa_agent.py`
8. `..\autoBMAD\epic_automation\qa_tools_integration.py`
9. `..\autoBMAD\epic_automation\quality_agents.py`
10. `..\autoBMAD\epic_automation\sdk_session_manager.py`
11. `..\autoBMAD\epic_automation\sdk_wrapper.py`
12. `..\autoBMAD\epic_automation\sm_agent.py`
13. `..\autoBMAD\epic_automation\state_manager.py`
14. `..\autoBMAD\epic_automation\test_automation_agent.py`
15. `..\autoBMAD\epic_automation\test_logging.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:430:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:84:53 - error: 部分参数的类型未知
    实参对应于 "generate_test_report" 函数中的 "results" 形参
    参数类型为 "dict[str, str | dict[str, int | float] | list[Unknown]]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:184:20 - error: 条件的计算结果始终为 `True`，因为类型 "type[ResultMessage]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:267:20 - error: "debugpy" 导入项未使用 (reportUnusedImport)
4 errors, 0 warnings, 0 notes
```

