# BasedPyright 检查报告
**生成时间**: 2026-01-07 18:02:04
**检查时间**: 2026-01-07T18:02:02.233273
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 15 |
| ❌ 错误 (Error) | 1 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.03 秒 |

## 🔴 错误详情

共发现 **1** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 1 个错误

### 按规则分组

- `reportUnusedVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:593

- **规则**: `reportUnusedVariable`
- **位置**: 第 593 行, 第 8 列
- **错误信息**: 变量 "story_id" 未使用

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\init_db.py`
6. `..\autoBMAD\epic_automation\log_manager.py`
7. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
8. `..\autoBMAD\epic_automation\qa_agent.py`
9. `..\autoBMAD\epic_automation\qa_tools_integration.py`
10. `..\autoBMAD\epic_automation\sdk_session_manager.py`
11. `..\autoBMAD\epic_automation\sdk_wrapper.py`
12. `..\autoBMAD\epic_automation\sm_agent.py`
13. `..\autoBMAD\epic_automation\state_manager.py`
14. `..\autoBMAD\epic_automation\test_automation_agent.py`
15. `..\autoBMAD\epic_automation\test_logging.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:593:9 - error: 变量 "story_id" 未使用 (reportUnusedVariable)
1 error, 0 warnings, 0 notes
```

