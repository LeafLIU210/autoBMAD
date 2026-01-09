# BasedPyright 检查报告
**生成时间**: 2026-01-08 08:00:39
**检查时间**: 2026-01-08T08:00:37.977580
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 13 |
| ❌ 错误 (Error) | 3 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.93 秒 |

## 🔴 错误详情

共发现 **3** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 1 个错误

### 按规则分组

- `reportUnusedImport`: 3 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 7 列
- **错误信息**: "asyncio" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:32

- **规则**: `reportUnusedImport`
- **位置**: 第 32 行, 第 52 列
- **错误信息**: "SDKErrorType" 导入项未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:20

- **规则**: `reportUnusedImport`
- **位置**: 第 20 行, 第 7 列
- **错误信息**: "uuid" 导入项未使用

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\init_db.py`
6. `..\autoBMAD\epic_automation\log_manager.py`
7. `..\autoBMAD\epic_automation\qa_agent.py`
8. `..\autoBMAD\epic_automation\qa_tools_integration.py`
9. `..\autoBMAD\epic_automation\sdk_session_manager.py`
10. `..\autoBMAD\epic_automation\sdk_wrapper.py`
11. `..\autoBMAD\epic_automation\sm_agent.py`
12. `..\autoBMAD\epic_automation\state_manager.py`
13. `..\autoBMAD\epic_automation\test_logging.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:11:8 - error: "asyncio" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:32:53 - error: "SDKErrorType" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:20:8 - error: "uuid" 导入项未使用 (reportUnusedImport)
3 errors, 0 warnings, 0 notes
```

