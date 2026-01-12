# BasedPyright 检查报告
**生成时间**: 2026-01-13 06:53:36
**检查时间**: 2026-01-13T06:53:36.798670
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 26 |
| ❌ 错误 (Error) | 8 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.83 秒 |

## 🔴 错误详情

共发现 **8** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 2 个错误

### 按规则分组

- `reportUnknownArgumentType`: 2 次
- `reportReturnType`: 2 次
- `reportInvalidStringEscapeSequence`: 2 次
- `reportUnusedImport`: 1 次
- `reportAttributeAccessIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:890

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 890 行, 第 58 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:901

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 901 行, 第 50 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:7

- **规则**: `reportUnusedImport`
- **位置**: 第 7 行, 第 7 列
- **错误信息**: "asyncio" 导入项未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:76

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 76 行, 第 24 列
- **错误信息**: 无法访问 "BrokenWorkerInterpreter" 类的 "started" 属性
  属性 "started" 未知

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1141

- **规则**: `reportReturnType`
- **位置**: 第 1141 行, 第 57 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1196

- **规则**: `reportReturnType`
- **位置**: 第 1196 行, 第 78 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:766

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 766 行, 第 61 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:766

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 766 行, 第 63 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents\__init__.py`
3. `..\autoBMAD\epic_automation\agents\base_agent.py`
4. `..\autoBMAD\epic_automation\agents\dev_agent.py`
5. `..\autoBMAD\epic_automation\agents\qa_agent.py`
6. `..\autoBMAD\epic_automation\agents\quality_agents.py`
7. `..\autoBMAD\epic_automation\agents\sdk_helper.py`
8. `..\autoBMAD\epic_automation\agents\sm_agent.py`
9. `..\autoBMAD\epic_automation\agents\state_agent.py`
10. `..\autoBMAD\epic_automation\agents\status_update_agent.py`
11. `..\autoBMAD\epic_automation\controllers\__init__.py`
12. `..\autoBMAD\epic_automation\controllers\base_controller.py`
13. `..\autoBMAD\epic_automation\controllers\devqa_controller.py`
14. `..\autoBMAD\epic_automation\controllers\quality_controller.py`
15. `..\autoBMAD\epic_automation\controllers\sm_controller.py`
16. `..\autoBMAD\epic_automation\core\__init__.py`
17. `..\autoBMAD\epic_automation\core\cancellation_manager.py`
18. `..\autoBMAD\epic_automation\core\sdk_executor.py`
19. `..\autoBMAD\epic_automation\core\sdk_result.py`
20. `..\autoBMAD\epic_automation\epic_driver.py`
21. `..\autoBMAD\epic_automation\init_db.py`
22. `..\autoBMAD\epic_automation\log_manager.py`
23. `..\autoBMAD\epic_automation\monitoring\__init__.py`
24. `..\autoBMAD\epic_automation\monitoring\resource_monitor.py`
25. `..\autoBMAD\epic_automation\sdk_wrapper.py`
26. `..\autoBMAD\epic_automation\state_manager.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:890:59 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:901:51 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:7:8 - error: "asyncio" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:76:25 - error: 无法访问 "BrokenWorkerInterpreter" 类的 "started" 属性
    属性 "started" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1141:58 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1196:79 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:766:62 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:766:64 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
8 errors, 0 warnings, 0 notes
```

