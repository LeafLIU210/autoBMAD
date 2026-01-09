# BasedPyright 检查报告
**生成时间**: 2026-01-07 13:30:25
**检查时间**: 2026-01-07T13:30:25.015887
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 15 |
| ❌ 错误 (Error) | 5 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.03 秒 |

## 🔴 错误详情

共发现 **5** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 5 个错误

### 按规则分组

- `reportUnusedImport`: 1 次
- `reportInvalidTypeVarUse`: 1 次
- `reportAssignmentType`: 1 次
- `reportArgumentType`: 1 次
- `reportGeneralTypeIssues`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:18

- **规则**: `reportUnusedImport`
- **位置**: 第 18 行, 第 59 列
- **错误信息**: "Callable" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:95

- **规则**: `reportInvalidTypeVarUse`
- **位置**: 第 95 行, 第 33 列
- **错误信息**: `TypeVar` "_T" 在泛型函数签名中仅出现了一次
  请改用 ""Never""

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:123

- **规则**: `reportAssignmentType`
- **位置**: 第 123 行, 第 49 列
- **错误信息**: "object" 类型不匹配声明的 "Awaitable[Any]" 类型
  "object" 与 Protocol 类 "Awaitable[Any]" 不兼容
    "__await__" 不存在

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:459

- **规则**: `reportArgumentType`
- **位置**: 第 459 行, 第 44 列
- **错误信息**: "AsyncIterator[Message]" 类型的实参无法赋值给函数 "__init__" 中 "AsyncGenerator[Any, _T@__init__]" 类型的形参 "generator"
  "AsyncIterator[Message]" 与 Protocol 类 "AsyncGenerator[Any, _T@__init__]" 不兼容
    "asend" 不存在
    "athrow" 不存在
    "aclose" 不存在
      "__anext__" 类型不兼容
        "() -> Awaitable[Message]" 类型与 "() -> Coroutine[Any, Any, _YieldT_co@AsyncGenerator]" 类型不兼容
          函数返回类型 "Awaitable[Message]" 与 "Coroutine[Any, Any, _YieldT_co@AsyncGenerator]" 类型不兼容

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:486

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 486 行, 第 33 列
- **错误信息**: "SafeAsyncGenerator" 不支持迭代
  "CoroutineType[Any, Any, SafeAsyncGenerator]" 类型上未定义 "__anext__" 方法

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:18:60 - error: "Callable" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:95:34 - error: `TypeVar` "_T" 在泛型函数签名中仅出现了一次
    请改用 ""Never"" (reportInvalidTypeVarUse)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:123:50 - error: "object" 类型不匹配声明的 "Awaitable[Any]" 类型
    "object" 与 Protocol 类 "Awaitable[Any]" 不兼容
      "__await__" 不存在 (reportAssignmentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:459:45 - error: "AsyncIterator[Message]" 类型的实参无法赋值给函数 "__init__" 中 "AsyncGenerator[Any, _T@__init__]" 类型的形参 "generator"
    "AsyncIterator[Message]" 与 Protocol 类 "AsyncGenerator[Any, _T@__init__]" 不兼容
      "asend" 不存在
      "athrow" 不存在
      "aclose" 不存在
        "__anext__" 类型不兼容
          "() -> Awaitable[Message]" 类型与 "() -> Coroutine[Any, Any, _YieldT_co@AsyncGenerator]" 类型不兼容
            函数返回类型 "Awaitable[Message]" 与 "Coroutine[Any, Any, _YieldT_co@AsyncGenerator]" 类型不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:486:34 - error: "SafeAsyncGenerator" 不支持迭代
    "CoroutineType[Any, Any, SafeAsyncGenerator]" 类型上未定义 "__anext__" 方法 (reportGeneralTypeIssues)
5 errors, 0 warnings, 0 notes
```

