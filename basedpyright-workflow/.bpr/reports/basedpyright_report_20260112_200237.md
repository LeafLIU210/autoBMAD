# BasedPyright 检查报告
**生成时间**: 2026-01-12 20:02:37
**检查时间**: 2026-01-12T20:02:37.266962
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 25 |
| ❌ 错误 (Error) | 7 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.82 秒 |

## 🔴 错误详情

共发现 **7** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 2 个错误

### 按规则分组

- `reportUnusedImport`: 3 次
- `reportReturnType`: 2 次
- `reportInvalidStringEscapeSequence`: 2 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "os" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 7 列
- **错误信息**: "time" 导入项未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:742

- **规则**: `reportUnusedImport`
- **位置**: 第 742 行, 第 40 列
- **错误信息**: "PathlibPath" 导入项未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1124

- **规则**: `reportReturnType`
- **位置**: 第 1124 行, 第 57 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1175

- **规则**: `reportReturnType`
- **位置**: 第 1175 行, 第 78 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 732 行, 第 61 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 732 行, 第 63 列
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
10. `..\autoBMAD\epic_automation\controllers\__init__.py`
11. `..\autoBMAD\epic_automation\controllers\base_controller.py`
12. `..\autoBMAD\epic_automation\controllers\devqa_controller.py`
13. `..\autoBMAD\epic_automation\controllers\quality_controller.py`
14. `..\autoBMAD\epic_automation\controllers\sm_controller.py`
15. `..\autoBMAD\epic_automation\core\__init__.py`
16. `..\autoBMAD\epic_automation\core\cancellation_manager.py`
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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:8:8 - error: "os" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:10:8 - error: "time" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:742:41 - error: "PathlibPath" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1124:58 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1175:79 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732:62 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732:64 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
7 errors, 0 warnings, 0 notes
```

