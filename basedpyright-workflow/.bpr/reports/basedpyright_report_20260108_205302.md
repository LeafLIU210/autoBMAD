# BasedPyright 检查报告
**生成时间**: 2026-01-08 20:53:02
**检查时间**: 2026-01-08T20:53:01.864719
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 18 |
| ❌ 错误 (Error) | 7 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.06 秒 |

## 🔴 错误详情

共发现 **7** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py`: 1 个错误

### 按规则分组

- `reportUnusedVariable`: 4 次
- `reportUnusedImport`: 1 次
- `reportGeneralTypeIssues`: 1 次
- `reportUnknownArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:242

- **规则**: `reportUnusedVariable`
- **位置**: 第 242 行, 第 16 列
- **错误信息**: 变量 "has_test_automation" 未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:244

- **规则**: `reportUnusedVariable`
- **位置**: 第 244 行, 第 16 列
- **错误信息**: 变量 "has_test_automation" 未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1110

- **规则**: `reportUnusedVariable`
- **位置**: 第 1110 行, 第 16 列
- **错误信息**: 变量 "i" 未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:24

- **规则**: `reportUnusedImport`
- **位置**: 第 24 行, 第 24 列
- **错误信息**: "cast" 导入项未使用

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:106

- **规则**: `reportUnusedVariable`
- **位置**: 第 106 行, 第 29 列
- **错误信息**: 变量 "process" 未使用

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:280

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 280 行, 第 43 列
- **错误信息**: "object" 不支持 `await`
  "object" 与 Protocol 类 "Awaitable[_T_co@Awaitable]" 不兼容
    "__await__" 不存在

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py:107

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 107 行, 第 11 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "all" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

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
14. `..\autoBMAD\epic_automation\status_parser.py`
15. `..\autoBMAD\epic_automation\test_automation_agent.py`
16. `..\autoBMAD\epic_automation\test_logging.py`
17. `..\autoBMAD\epic_automation\test_simple.py`
18. `..\autoBMAD\epic_automation\test_status_parser.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:242:17 - error: 变量 "has_test_automation" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:244:17 - error: 变量 "has_test_automation" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1110:17 - error: 变量 "i" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:24:25 - error: "cast" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:106:30 - error: 变量 "process" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:280:44 - error: "object" 不支持 `await`
    "object" 与 Protocol 类 "Awaitable[_T_co@Awaitable]" 不兼容
      "__await__" 不存在 (reportGeneralTypeIssues)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py:107:12 - error: 部分参数的类型未知
    实参对应于 "all" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
7 errors, 0 warnings, 0 notes
```

