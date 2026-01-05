# BasedPyright 检查报告
**生成时间**: 2026-01-05 22:49:04
**检查时间**: 2026-01-05T22:49:04.094764
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 4 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.66 秒 |

## 🔴 错误详情

共发现 **4** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 4 个错误

### 按规则分组

- `reportPossiblyUnboundVariable`: 3 次
- `reportUnusedVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:499

- **规则**: `reportUnusedVariable`
- **位置**: 第 499 行, 第 16 列
- **错误信息**: 变量 "message_count" 未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:508

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 508 行, 第 28 列
- **错误信息**: "message_count" 可能未绑定

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:519

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 519 行, 第 27 列
- **错误信息**: "message_count" 可能未绑定

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:520

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 520 行, 第 79 列
- **错误信息**: "message_count" 可能未绑定

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\code_quality_agent.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
6. `..\autoBMAD\epic_automation\qa_agent.py`
7. `..\autoBMAD\epic_automation\qa_tools_integration.py`
8. `..\autoBMAD\epic_automation\sm_agent.py`
9. `..\autoBMAD\epic_automation\state_manager.py`
10. `..\autoBMAD\epic_automation\test_automation_agent.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:499:17 - error: 变量 "message_count" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:508:29 - error: "message_count" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:519:28 - error: "message_count" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:520:80 - error: "message_count" 可能未绑定 (reportPossiblyUnboundVariable)
4 errors, 0 warnings, 0 notes
```

