# BasedPyright 检查报告
**生成时间**: 2026-01-11 18:08:55
**检查时间**: 2026-01-11T18:08:55.596960
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 25 |
| ❌ 错误 (Error) | 19 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.77 秒 |

## 🔴 错误详情

共发现 **19** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py`: 10 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 5 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\safe_claude_sdk.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py`: 1 个错误

### 按规则分组

- `reportUnknownArgumentType`: 14 次
- `reportAttributeAccessIssue`: 3 次
- `reportConstantRedefinition`: 2 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:65

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 65 行, 第 37 列
- **错误信息**: 无法访问 "BrokenWorkerInterpreter" 类的 "start" 属性
  属性 "start" 未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:125

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 125 行, 第 38 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Any | Unknown]"

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:126

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 126 行, 第 40 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Any | Unknown]"

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:127

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 127 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "set[Any | Unknown]"

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:127

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 127 行, 第 49 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "iterable" 形参
  参数类型为 "Generator[Any | Unknown, None, None]"

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:129

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 129 行, 第 48 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "Any | list[Unknown]"

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:184

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 184 行, 第 38 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown | Any]"

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:185

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 185 行, 第 40 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown | Any]"

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:186

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 186 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "set[Unknown | Any]"

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:186

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 186 行, 第 49 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "iterable" 形参
  参数类型为 "Generator[Unknown | Any, None, None]"

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:188

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 188 行, 第 48 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "Unknown | Any"

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:59

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 59 行, 第 37 列
- **错误信息**: 无法访问 "BrokenWorkerInterpreter" 类的 "start" 属性
  属性 "start" 未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\safe_claude_sdk.py:25

- **规则**: `reportConstantRedefinition`
- **位置**: 第 25 行, 第 4 列
- **错误信息**: 不能重新定义常量 "SDK_AVAILABLE"（全大写名称）

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\safe_claude_sdk.py:27

- **规则**: `reportConstantRedefinition`
- **位置**: 第 27 行, 第 4 列
- **错误信息**: 不能重新定义常量 "SDK_AVAILABLE"（全大写名称）

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1872

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1872 行, 第 68 列
- **错误信息**: "get_cancellation_manager" 是未知的导入符号

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1881

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1881 行, 第 28 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参
  参数类型为 "Unknown | Any"

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1883

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1883 行, 第 29 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "o" 形参
  参数类型为 "Unknown | Any"

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1885

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1885 行, 第 43 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "iterable" 形参
  参数类型为 "Unknown | Any"

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1887

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 1887 行, 第 60 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown | Any]"

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:65:38 - error: 无法访问 "BrokenWorkerInterpreter" 类的 "start" 属性
    属性 "start" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:125:39 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Any | Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:126:41 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Any | Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:127:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "set[Any | Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:127:50 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "Generator[Any | Unknown, None, None]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:129:49 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "Any | list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:184:39 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown | Any]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:185:41 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown | Any]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:186:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "set[Unknown | Any]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:186:50 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "Generator[Unknown | Any, None, None]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:188:49 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:59:38 - error: 无法访问 "BrokenWorkerInterpreter" 类的 "start" 属性
    属性 "start" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\safe_claude_sdk.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\safe_claude_sdk.py:25:5 - error: 不能重新定义常量 "SDK_AVAILABLE"（全大写名称） (reportConstantRedefinition)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\safe_claude_sdk.py:27:5 - error: 不能重新定义常量 "SDK_AVAILABLE"（全大写名称） (reportConstantRedefinition)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1872:69 - error: "get_cancellation_manager" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1881:29 - error: 部分参数的类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1883:30 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "o" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1885:44 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1887:61 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown | Any]" (reportUnknownArgumentType)
19 errors, 0 warnings, 0 notes
```

