# BasedPyright 检查报告
**生成时间**: 2026-01-12 19:24:19
**检查时间**: 2026-01-12T19:24:18.180209
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 25 |
| ❌ 错误 (Error) | 29 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.82 秒 |

## 🔴 错误详情

共发现 **29** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py`: 5 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py`: 5 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\devqa_controller.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\sm_controller.py`: 1 个错误

### 按规则分组

- `reportUnusedImport`: 7 次
- `reportUnknownArgumentType`: 5 次
- `reportArgumentType`: 4 次
- `reportAttributeAccessIssue`: 3 次
- `reportReturnType`: 2 次
- `reportInvalidStringEscapeSequence`: 2 次
- `reportUnknownParameterType`: 1 次
- `reportMissingParameterType`: 1 次
- `reportConstantRedefinition`: 1 次
- `reportOptionalCall`: 1 次
- `reportIncompatibleMethodOverride`: 1 次
- `reportGeneralTypeIssues`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:134

- **规则**: `reportUnknownParameterType`
- **位置**: 第 134 行, 第 32 列
- **错误信息**: "message" 参数的类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:134

- **规则**: `reportMissingParameterType`
- **位置**: 第 134 行, 第 32 列
- **错误信息**: "message" 参数缺少类型注解

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:141

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 141 行, 第 34 列
- **错误信息**: 参数类型未知
  实参对应于 "__new__" 函数中的 "object" 形参

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:9

- **规则**: `reportUnusedImport`
- **位置**: 第 9 行, 第 7 列
- **错误信息**: "anyio" 导入项未使用

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py:35

- **规则**: `reportConstantRedefinition`
- **位置**: 第 35 行, 第 4 列
- **错误信息**: 不能重新定义常量 "SDK_AVAILABLE"（全大写名称）

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py:122

- **规则**: `reportArgumentType`
- **位置**: 第 122 行, 第 24 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__init__" 中 "PermissionMode | None" 类型的形参 "permission_mode"
  "str" 类型与 "PermissionMode | None" 类型不兼容
    "str" 与 "None" 不兼容
    "str" 与 "Literal['default']" 类型不兼容
    "str" 与 "Literal['acceptEdits']" 类型不兼容
    "str" 与 "Literal['plan']" 类型不兼容
    "str" 与 "Literal['bypassPermissions']" 类型不兼容

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py:132

- **规则**: `reportOptionalCall`
- **位置**: 第 132 行, 第 14 列
- **错误信息**: `None` 不支持调用

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "os" 导入项未使用

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 7 列
- **错误信息**: "time" 导入项未使用

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:745

- **规则**: `reportUnusedImport`
- **位置**: 第 745 行, 第 40 列
- **错误信息**: "PathlibPath" 导入项未使用

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\devqa_controller.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 7 列
- **错误信息**: "anyio" 导入项未使用

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:12

- **规则**: `reportUnusedImport`
- **位置**: 第 12 行, 第 7 列
- **错误信息**: "anyio" 导入项未使用

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:46

- **规则**: `reportIncompatibleMethodOverride`
- **位置**: 第 46 行, 第 14 列
- **错误信息**: 此 "execute" 方法以不兼容的方式覆写了 "BaseController" 类中的同名方法
  返回类型不匹配：基类方法返回 "CoroutineType[Any, Any, bool]" 类型，覆写方法返回 "CoroutineType[Any, Any, Dict[str, Any]]" 类型
    "CoroutineType[Any, Any, Dict[str, Any]]" 与 "CoroutineType[Any, Any, bool]" 不兼容
      类型参数 "_ReturnT_nd_co@CoroutineType" 是协变（`Covariant`）的，但 "Dict[str, Any]" 不是 "bool" 的子类
        "Dict[str, Any]" 与 "bool" 不兼容

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:90

- **规则**: `reportArgumentType`
- **位置**: 第 90 行, 第 31 列
- **错误信息**: "str | None" 类型的实参无法赋值给函数 "execute" 中 "str" 类型的形参 "source_dir"
  "str | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:101

- **规则**: `reportArgumentType`
- **位置**: 第 101 行, 第 31 列
- **错误信息**: "str | None" 类型的实参无法赋值给函数 "execute" 中 "str" 类型的形参 "source_dir"
  "str | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:111

- **规则**: `reportArgumentType`
- **位置**: 第 111 行, 第 35 列
- **错误信息**: "str | None" 类型的实参无法赋值给函数 "execute" 中 "str" 类型的形参 "source_dir"
  "str | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\sm_controller.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 7 列
- **错误信息**: "anyio" 导入项未使用

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:206

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 206 行, 第 35 列
- **错误信息**: "AsyncIterator[Any]" 不支持 `await`
  "AsyncIterator[Any]" 与 Protocol 类 "Awaitable[_T_co@Awaitable]" 不兼容
    "__await__" 不存在

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:249

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 249 行, 第 25 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "messages" 形参
  参数类型为 "list[Unknown]"

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:252

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 252 行, 第 23 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "errors" 形参
  参数类型为 "list[Unknown]"

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:266

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 266 行, 第 25 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "messages" 形参
  参数类型为 "list[Unknown]"

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:268

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 268 行, 第 23 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "errors" 形参
  参数类型为 "list[Unknown]"

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1124

- **规则**: `reportReturnType`
- **位置**: 第 1124 行, 第 57 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1175

- **规则**: `reportReturnType`
- **位置**: 第 1175 行, 第 78 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:585

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 585 行, 第 34 列
- **错误信息**: 无法访问 "CancellationManager" 类的 "check_cancellation_type" 属性
  属性 "check_cancellation_type" 未知

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:589

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 589 行, 第 30 列
- **错误信息**: 无法访问 "CancellationManager" 类的 "wait_for_cancellation_complete" 属性
  属性 "wait_for_cancellation_complete" 未知

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:600

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 600 行, 第 26 列
- **错误信息**: 无法访问 "CancellationManager" 类的 "wait_for_cancellation_complete" 属性
  属性 "wait_for_cancellation_complete" 未知

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 732 行, 第 61 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:134:33 - error: "message" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:134:33 - error: "message" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:141:35 - error: 参数类型未知
    实参对应于 "__new__" 函数中的 "object" 形参 (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:9:8 - error: "anyio" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py:35:5 - error: 不能重新定义常量 "SDK_AVAILABLE"（全大写名称） (reportConstantRedefinition)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py:122:25 - error: "str" 类型的实参无法赋值给函数 "__init__" 中 "PermissionMode | None" 类型的形参 "permission_mode"
    "str" 类型与 "PermissionMode | None" 类型不兼容
      "str" 与 "None" 不兼容
      "str" 与 "Literal['default']" 类型不兼容
      "str" 与 "Literal['acceptEdits']" 类型不兼容
      "str" 与 "Literal['plan']" 类型不兼容
      "str" 与 "Literal['bypassPermissions']" 类型不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sdk_helper.py:132:15 - error: `None` 不支持调用 (reportOptionalCall)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:8:8 - error: "os" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:10:8 - error: "time" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:745:41 - error: "PathlibPath" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\devqa_controller.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\devqa_controller.py:10:8 - error: "anyio" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:12:8 - error: "anyio" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:46:15 - error: 此 "execute" 方法以不兼容的方式覆写了 "BaseController" 类中的同名方法
    返回类型不匹配：基类方法返回 "CoroutineType[Any, Any, bool]" 类型，覆写方法返回 "CoroutineType[Any, Any, Dict[str, Any]]" 类型
      "CoroutineType[Any, Any, Dict[str, Any]]" 与 "CoroutineType[Any, Any, bool]" 不兼容
        类型参数 "_ReturnT_nd_co@CoroutineType" 是协变（`Covariant`）的，但 "Dict[str, Any]" 不是 "bool" 的子类
          "Dict[str, Any]" 与 "bool" 不兼容 (reportIncompatibleMethodOverride)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:90:32 - error: "str | None" 类型的实参无法赋值给函数 "execute" 中 "str" 类型的形参 "source_dir"
    "str | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:101:32 - error: "str | None" 类型的实参无法赋值给函数 "execute" 中 "str" 类型的形参 "source_dir"
    "str | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\quality_controller.py:111:36 - error: "str | None" 类型的实参无法赋值给函数 "execute" 中 "str" 类型的形参 "source_dir"
    "str | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\sm_controller.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\sm_controller.py:11:8 - error: "anyio" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:206:36 - error: "AsyncIterator[Any]" 不支持 `await`
    "AsyncIterator[Any]" 与 Protocol 类 "Awaitable[_T_co@Awaitable]" 不兼容
      "__await__" 不存在 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:249:26 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "messages" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:252:24 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:266:26 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "messages" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\core\sdk_executor.py:268:24 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1124:58 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1175:79 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:585:35 - error: 无法访问 "CancellationManager" 类的 "check_cancellation_type" 属性
    属性 "check_cancellation_type" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:589:31 - error: 无法访问 "CancellationManager" 类的 "wait_for_cancellation_complete" 属性
    属性 "wait_for_cancellation_complete" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:600:27 - error: 无法访问 "CancellationManager" 类的 "wait_for_cancellation_complete" 属性
    属性 "wait_for_cancellation_complete" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732:62 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732:64 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
29 errors, 0 warnings, 0 notes
```

