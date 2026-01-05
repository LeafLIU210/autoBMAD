# BasedPyright 检查报告
**生成时间**: 2026-01-05 22:20:16
**检查时间**: 2026-01-05T22:20:15.959077
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 2 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.73 秒 |

## 🔴 错误详情

共发现 **2** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 2 个错误

### 按规则分组

- `reportUnknownMemberType`: 1 次
- `reportAttributeAccessIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:505

- **规则**: `reportUnknownMemberType`
- **位置**: 第 505 行, 第 31 列
- **错误信息**: "timeout" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:505

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 505 行, 第 39 列
- **错误信息**: "timeout" 不是 "asyncio" 模块的已知属性

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:505:32 - error: "timeout" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:505:40 - error: "timeout" 不是 "asyncio" 模块的已知属性 (reportAttributeAccessIssue)
2 errors, 0 warnings, 0 notes
```

