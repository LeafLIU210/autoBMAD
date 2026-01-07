# BasedPyright 检查报告
**生成时间**: 2026-01-07 11:48:29
**检查时间**: 2026-01-07T11:48:29.587679
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 2 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.10 秒 |

## 🔴 错误详情

共发现 **2** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 2 个错误

### 按规则分组

- `reportUnusedImport`: 1 次
- `reportAssignmentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:18

- **规则**: `reportUnusedImport`
- **位置**: 第 18 行, 第 49 列
- **错误信息**: "Callable" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:122

- **规则**: `reportAssignmentType`
- **位置**: 第 122 行, 第 49 列
- **错误信息**: "object" 类型不匹配声明的 "Awaitable[Any]" 类型
  "object" 与 Protocol 类 "Awaitable[Any]" 不兼容
    "__await__" 不存在

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:18:50 - error: "Callable" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:122:50 - error: "object" 类型不匹配声明的 "Awaitable[Any]" 类型
    "object" 与 Protocol 类 "Awaitable[Any]" 不兼容
      "__await__" 不存在 (reportAssignmentType)
2 errors, 0 warnings, 0 notes
```

