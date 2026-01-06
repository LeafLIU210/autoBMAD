# BasedPyright 检查报告
**生成时间**: 2026-01-06 22:31:50
**检查时间**: 2026-01-06T22:29:05.713859
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 4 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.05 秒 |

## 🔴 错误详情

共发现 **4** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 4 个错误

### 按规则分组

- `reportUnknownMemberType`: 1 次
- `reportAttributeAccessIssue`: 1 次
- `reportOptionalCall`: 1 次
- `reportArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349

- **规则**: `reportUnknownMemberType`
- **位置**: 第 349 行, 第 17 列
- **错误信息**: "timeout" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 349 行, 第 25 列
- **错误信息**: "timeout" 不是 "asyncio" 模块的已知属性

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:490

- **规则**: `reportOptionalCall`
- **位置**: 第 490 行, 第 24 列
- **错误信息**: `None` 不支持调用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:500

- **规则**: `reportArgumentType`
- **位置**: 第 500 行, 第 51 列
- **错误信息**: "object" 类型的实参无法赋值给函数 "wait_for" 中 "_FutureLike[_T@wait_for]" 类型的形参 "fut"
  "object" 类型与 "_FutureLike[_T@wait_for]" 类型不兼容
    "object" 与 Protocol 类 "Awaitable[_T@wait_for]" 不兼容
      "__await__" 不存在
    "object" 与 "Future[_T@wait_for]" 不兼容
    "object" 与 Protocol 类 "Generator[Any, None, _T@wait_for]" 不兼容
      "__next__" 不存在
      "send" 不存在
      "throw" 不存在
  ...

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349:18 - error: "timeout" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349:26 - error: "timeout" 不是 "asyncio" 模块的已知属性 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:490:25 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:500:52 - error: "object" 类型的实参无法赋值给函数 "wait_for" 中 "_FutureLike[_T@wait_for]" 类型的形参 "fut"
    "object" 类型与 "_FutureLike[_T@wait_for]" 类型不兼容
      "object" 与 Protocol 类 "Awaitable[_T@wait_for]" 不兼容
        "__await__" 不存在
      "object" 与 "Future[_T@wait_for]" 不兼容
      "object" 与 Protocol 类 "Generator[Any, None, _T@wait_for]" 不兼容
        "__next__" 不存在
        "send" 不存在
        "throw" 不存在
    ... (reportArgumentType)
4 errors, 0 warnings, 0 notes
```

