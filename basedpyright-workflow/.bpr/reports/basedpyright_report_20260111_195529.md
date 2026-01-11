# BasedPyright 检查报告
**生成时间**: 2026-01-11 19:55:29
**检查时间**: 2026-01-11T19:55:28.854709
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 25 |
| ❌ 错误 (Error) | 4 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.76 秒 |

## 🔴 错误详情

共发现 **4** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 4 个错误

### 按规则分组

- `reportUnknownArgumentType`: 3 次
- `reportAttributeAccessIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1876

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1876 行, 第 62 列
- **错误信息**: "get_cancellation_manager" 不是 "autoBMAD.epic_automation.monitoring" 模块的已知属性

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1885

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1885 行, 第 32 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参
  参数类型为 "Unknown | Any"

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1887

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1887 行, 第 29 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "o" 形参
  参数类型为 "Unknown | Any"

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1889

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1889 行, 第 54 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "iterable" 形参
  参数类型为 "Unknown | Any"

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents\__init__.py`
3. `..\autoBMAD\epic_automation\agents\base_agent.py`
4. `..\autoBMAD\epic_automation\agents\dev_agent.py`
5. `..\autoBMAD\epic_automation\agents\qa_agent.py`
6. `..\autoBMAD\epic_automation\agents\quality_agents.py`
7. `..\autoBMAD\epic_automation\agents\sm_agent.py`
8. `..\autoBMAD\epic_automation\agents\state_agent.py`
9. `..\autoBMAD\epic_automation\controllers\__init__.py`
10. `..\autoBMAD\epic_automation\controllers\base_controller.py`
11. `..\autoBMAD\epic_automation\controllers\devqa_controller.py`
12. `..\autoBMAD\epic_automation\controllers\quality_controller.py`
13. `..\autoBMAD\epic_automation\controllers\sm_controller.py`
14. `..\autoBMAD\epic_automation\core\__init__.py`
15. `..\autoBMAD\epic_automation\core\cancellation_manager.py`
16. `..\autoBMAD\epic_automation\core\safe_claude_sdk.py`
17. `..\autoBMAD\epic_automation\core\sdk_executor.py`
18. `..\autoBMAD\epic_automation\core\sdk_result.py`
19. `..\autoBMAD\epic_automation\epic_driver.py`
20. `..\autoBMAD\epic_automation\init_db.py`
21. `..\autoBMAD\epic_automation\log_manager.py`
22. `..\autoBMAD\epic_automation\monitoring\__init__.py`
23. `..\autoBMAD\epic_automation\monitoring\resource_monitor.py`
24. `..\autoBMAD\epic_automation\sdk_wrapper.py`
25. `..\autoBMAD\epic_automation\state_manager.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1876:63 - error: "get_cancellation_manager" 不是 "autoBMAD.epic_automation.monitoring" 模块的已知属性 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1885:33 - error: 部分参数的类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1887:30 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "o" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1889:55 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
4 errors, 0 warnings, 0 notes
```

