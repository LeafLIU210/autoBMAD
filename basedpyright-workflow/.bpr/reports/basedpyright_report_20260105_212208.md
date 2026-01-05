# BasedPyright 检查报告
**生成时间**: 2026-01-05 21:22:08
**检查时间**: 2026-01-05T21:22:08.425313
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 3 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.64 秒 |

## 🔴 错误详情

共发现 **3** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py`: 3 个错误

### 按规则分组

- `reportUnknownVariableType`: 2 次
- `reportGeneralTypeIssues`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:285

- **规则**: `reportUnknownVariableType`
- **位置**: 第 285 行, 第 16 列
- **错误信息**: "all_passed" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:285

- **规则**: `reportUnknownVariableType`
- **位置**: 第 285 行, 第 28 列
- **错误信息**: "failed_stories" 类型未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:285

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 285 行, 第 45 列
- **错误信息**: "CoroutineType[Any, Any, Tuple[bool, List[str]]]" 不支持迭代
  未定义 "__iter__" 方法

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:285:17 - error: "all_passed" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:285:29 - error: "failed_stories" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:285:46 - error: "CoroutineType[Any, Any, Tuple[bool, List[str]]]" 不支持迭代
    未定义 "__iter__" 方法 (reportGeneralTypeIssues)
3 errors, 0 warnings, 0 notes
```

