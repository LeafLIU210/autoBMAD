# BasedPyright 检查报告
**生成时间**: 2026-01-07 08:05:06
**检查时间**: 2026-01-07T08:05:06.402247
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 5 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.05 秒 |

## 🔴 错误详情

共发现 **5** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 1 个错误

### 按规则分组

- `reportUnknownMemberType`: 1 次
- `reportAttributeAccessIssue`: 1 次
- `reportUnusedImport`: 1 次
- `reportUnusedVariable`: 1 次
- `reportPrivateUsage`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1235

- **规则**: `reportUnknownMemberType`
- **位置**: 第 1235 行, 第 20 列
- **错误信息**: "flush" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1235

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1235 行, 第 37 列
- **错误信息**: 无法访问 "LogManager" 类的 "flush" 属性
  属性 "flush" 未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:19

- **规则**: `reportUnusedImport`
- **位置**: 第 19 行, 第 23 列
- **错误信息**: "asynccontextmanager" 导入项未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:625

- **规则**: `reportUnusedVariable`
- **位置**: 第 625 行, 第 12 列
- **错误信息**: 变量 "gate_paths" 未使用

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:488

- **规则**: `reportPrivateUsage`
- **位置**: 第 488 行, 第 33 列
- **错误信息**: "_stop_event" 在声明它受到保护的类之外被使用

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1235:21 - error: "flush" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1235:38 - error: 无法访问 "LogManager" 类的 "flush" 属性
    属性 "flush" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:19:24 - error: "asynccontextmanager" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:625:13 - error: 变量 "gate_paths" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:488:34 - error: "_stop_event" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
5 errors, 0 warnings, 0 notes
```

