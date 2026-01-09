# BasedPyright 检查报告

**生成时间**: 2025-10-29 14:09:26

**检查时间**: 2025-10-29T14:09:25.973701
**检查目录**: `src`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 107 |
| ❌ 错误 (Error) | 96 |
| ⚠️ 警告 (Warning) | 3373 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 9.23 秒 |

## 🔴 错误详情

共发现 **96** 个错误

### 按文件分组

- `d:\Python\fcmrawler\src\models\database.py`: 22 个错误
- `d:\Python\fcmrawler\src\services\page_structure_analyzer.py`: 22 个错误
- `d:\Python\fcmrawler\src\services\api_test_service.py`: 12 个错误
- `d:\Python\fcmrawler\src\services\url_service.py`: 12 个错误
- `d:\Python\fcmrawler\src\services\cms_detector.py`: 5 个错误
- `d:\Python\fcmrawler\src\services\custom_report_generator.py`: 4 个错误
- `d:\Python\fcmrawler\src\services\batch_crawl_service.py`: 3 个错误
- `d:\Python\fcmrawler\src\services\__init__.py`: 2 个错误
- `d:\Python\fcmrawler\src\services\batch_analysis_service.py`: 2 个错误
- `d:\Python\fcmrawler\src\services\crawl_execution_service.py`: 2 个错误
- `d:\Python\fcmrawler\src\services\data_query_service.py`: 2 个错误
- `d:\Python\fcmrawler\src\services\field_management_service.py`: 2 个错误
- `d:\Python\fcmrawler\src\services\time_series_analyzer.py`: 2 个错误
- `d:\Python\fcmrawler\src\legacy\__init__.py`: 1 个错误
- `d:\Python\fcmrawler\src\models\entities.py`: 1 个错误
- `d:\Python\fcmrawler\src\services\change_detector.py`: 1 个错误
- `d:\Python\fcmrawler\src\services\version_manager.py`: 1 个错误

### 按规则分组

- `reportArgumentType`: 31 次
- `reportAttributeAccessIssue`: 25 次
- `reportOperatorIssue`: 10 次
- `reportIndexIssue`: 7 次
- `reportImportCycles`: 5 次
- `reportMissingImports`: 4 次
- `reportOptionalOperand`: 4 次
- `reportCallIssue`: 3 次
- `reportReturnType`: 2 次
- `reportPossiblyUnboundVariable`: 2 次
- `reportOptionalSubscript`: 1 次
- `reportOptionalMemberAccess`: 1 次
- `reportInvalidTypeForm`: 1 次

### 详细错误列表

#### 1. d:\Python\fcmrawler\src\legacy\__init__.py:30

- **规则**: `reportMissingImports`
- **位置**: 第 30 行, 第 9 列
- **错误信息**: 无法解析导入 ".report_generator"

#### 2. d:\Python\fcmrawler\src\models\database.py:1

- **规则**: `reportImportCycles`
- **位置**: 第 1 行, 第 0 列
- **错误信息**: 导入链中检测到循环导入
  d:\Python\fcmrawler\src\models\database.py
  d:\Python\fcmrawler\src\models\field_schema_migration.py

#### 3. d:\Python\fcmrawler\src\models\database.py:1

- **规则**: `reportImportCycles`
- **位置**: 第 1 行, 第 0 列
- **错误信息**: 导入链中检测到循环导入
  d:\Python\fcmrawler\src\models\database.py
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py

#### 4. d:\Python\fcmrawler\src\models\database.py:1265

- **规则**: `reportArgumentType`
- **位置**: 第 1265 行, 第 65 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "_set_as_default_config_atomic" 中 "int" 类型的形参 "config_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 5. d:\Python\fcmrawler\src\models\database.py:3776

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3776 行, 第 48 列
- **错误信息**: 无法访问 "Config" 类的 "config_data" 属性
  属性 "config_data" 未知

#### 6. d:\Python\fcmrawler\src\models\database.py:3786

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3786 行, 第 32 列
- **错误信息**: 无法访问 "Config" 类的 "name" 属性
  属性 "name" 未知

#### 7. d:\Python\fcmrawler\src\models\database.py:3786

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3786 行, 第 58 列
- **错误信息**: 无法访问 "Config" 类的 "is_default" 属性
  属性 "is_default" 未知

#### 8. d:\Python\fcmrawler\src\models\database.py:3790

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3790 行, 第 30 列
- **错误信息**: 无法访问 "Config" 类的 "is_default" 属性
  属性 "is_default" 未知

#### 9. d:\Python\fcmrawler\src\models\database.py:3791

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3791 行, 第 80 列
- **错误信息**: 无法访问 "Config" 类的 "url_id" 属性
  属性 "url_id" 未知

#### 10. d:\Python\fcmrawler\src\models\database.py:3793

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3793 行, 第 82 列
- **错误信息**: 无法访问 "Config" 类的 "url_id" 属性
  属性 "url_id" 未知

#### 11. d:\Python\fcmrawler\src\models\database.py:3802

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3802 行, 第 32 列
- **错误信息**: 无法访问 "Config" 类的 "url_id" 属性
  属性 "url_id" 未知

#### 12. d:\Python\fcmrawler\src\models\database.py:3802

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3802 行, 第 47 列
- **错误信息**: 无法访问 "Config" 类的 "name" 属性
  属性 "name" 未知

#### 13. d:\Python\fcmrawler\src\models\database.py:3802

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3802 行, 第 73 列
- **错误信息**: 无法访问 "Config" 类的 "is_default" 属性
  属性 "is_default" 未知

#### 14. d:\Python\fcmrawler\src\models\database.py:3807

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3807 行, 第 30 列
- **错误信息**: 无法访问 "Config" 类的 "is_default" 属性
  属性 "is_default" 未知

#### 15. d:\Python\fcmrawler\src\models\database.py:3808

- **规则**: `reportArgumentType`
- **位置**: 第 3808 行, 第 62 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "_set_default_config_atomic" 中 "int" 类型的形参 "config_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 16. d:\Python\fcmrawler\src\models\database.py:3808

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3808 行, 第 80 列
- **错误信息**: 无法访问 "Config" 类的 "url_id" 属性
  属性 "url_id" 未知

#### 17. d:\Python\fcmrawler\src\models\database.py:3810

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3810 行, 第 84 列
- **错误信息**: 无法访问 "Config" 类的 "url_id" 属性
  属性 "url_id" 未知

#### 18. d:\Python\fcmrawler\src\models\database.py:3811

- **规则**: `reportReturnType`
- **位置**: 第 3811 行, 第 27 列
- **错误信息**: "int | None" 类型不匹配返回类型 "int"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 19. d:\Python\fcmrawler\src\models\database.py:3914

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3914 行, 第 48 列
- **错误信息**: 无法访问 "Config" 类的 "config_data" 属性
  属性 "config_data" 未知

#### 20. d:\Python\fcmrawler\src\models\database.py:3922

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3922 行, 第 28 列
- **错误信息**: 无法访问 "Config" 类的 "name" 属性
  属性 "name" 未知

#### 21. d:\Python\fcmrawler\src\models\database.py:3922

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3922 行, 第 54 列
- **错误信息**: 无法访问 "Config" 类的 "is_default" 属性
  属性 "is_default" 未知

#### 22. d:\Python\fcmrawler\src\models\database.py:3926

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3926 行, 第 26 列
- **错误信息**: 无法访问 "Config" 类的 "is_default" 属性
  属性 "is_default" 未知

#### 23. d:\Python\fcmrawler\src\models\database.py:3927

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 3927 行, 第 76 列
- **错误信息**: 无法访问 "Config" 类的 "url_id" 属性
  属性 "url_id" 未知

#### 24. d:\Python\fcmrawler\src\models\entities.py:1

- **规则**: `reportImportCycles`
- **位置**: 第 1 行, 第 0 列
- **错误信息**: 导入链中检测到循环导入
  d:\Python\fcmrawler\src\models\entities.py
  d:\Python\fcmrawler\src\services\field_validator.py

#### 25. d:\Python\fcmrawler\src\services\__init__.py:1

- **规则**: `reportImportCycles`
- **位置**: 第 1 行, 第 0 列
- **错误信息**: 导入链中检测到循环导入
  d:\Python\fcmrawler\src\services\__init__.py
  d:\Python\fcmrawler\src\services\cms_detector.py

#### 26. d:\Python\fcmrawler\src\services\__init__.py:1

- **规则**: `reportImportCycles`
- **位置**: 第 1 行, 第 0 列
- **错误信息**: 导入链中检测到循环导入
  d:\Python\fcmrawler\src\services\__init__.py
  d:\Python\fcmrawler\src\services\config_generator.py
  d:\Python\fcmrawler\src\services\cms_detector.py

#### 27. d:\Python\fcmrawler\src\services\api_test_service.py:190

- **规则**: `reportArgumentType`
- **位置**: 第 190 行, 第 25 列
- **错误信息**: "str | APIProvider" 类型的实参无法赋值给函数 "__init__" 中 "APIProvider" 类型的形参 "provider"
  "str | APIProvider" 类型与 "APIProvider" 类型不兼容
    "str" 与 "APIProvider" 不兼容

#### 28. d:\Python\fcmrawler\src\services\api_test_service.py:339

- **规则**: `reportIndexIssue`
- **位置**: 第 339 行, 第 16 列
- **错误信息**: "str" 类型上未定义 "__setitem__" 方法

#### 29. d:\Python\fcmrawler\src\services\api_test_service.py:339

- **规则**: `reportIndexIssue`
- **位置**: 第 339 行, 第 16 列
- **错误信息**: "int" 类型上未定义 "__setitem__" 方法

#### 30. d:\Python\fcmrawler\src\services\api_test_service.py:339

- **规则**: `reportIndexIssue`
- **位置**: 第 339 行, 第 16 列
- **错误信息**: "float" 类型上未定义 "__setitem__" 方法

#### 31. d:\Python\fcmrawler\src\services\api_test_service.py:339

- **规则**: `reportOptionalSubscript`
- **位置**: 第 339 行, 第 16 列
- **错误信息**: 不能取 `None` 类型对象的下标

#### 32. d:\Python\fcmrawler\src\services\api_test_service.py:340

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 340 行, 第 62 列
- **错误信息**: 无法访问 "str" 类的 "get" 属性
  属性 "get" 未知

#### 33. d:\Python\fcmrawler\src\services\api_test_service.py:340

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 340 行, 第 62 列
- **错误信息**: 无法访问 "int" 类的 "get" 属性
  属性 "get" 未知

#### 34. d:\Python\fcmrawler\src\services\api_test_service.py:340

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 340 行, 第 62 列
- **错误信息**: 无法访问 "float" 类的 "get" 属性
  属性 "get" 未知

#### 35. d:\Python\fcmrawler\src\services\api_test_service.py:340

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 340 行, 第 62 列
- **错误信息**: `None` 没有 "get" 属性

#### 36. d:\Python\fcmrawler\src\services\api_test_service.py:446

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 446 行, 第 41 列
- **错误信息**: 无法访问 "str" 类的 "value" 属性
  属性 "value" 未知

#### 37. d:\Python\fcmrawler\src\services\api_test_service.py:517

- **规则**: `reportArgumentType`
- **位置**: 第 517 行, 第 92 列
- **错误信息**: "CIMultiDictProxy[str]" 类型的实参无法赋值给函数 "_parse_rate_limit_headers" 中 "Dict[str, str]" 类型的形参 "headers"
  "CIMultiDictProxy[str]" 与 "Dict[str, str]" 不兼容

#### 38. d:\Python\fcmrawler\src\services\api_test_service.py:649

- **规则**: `reportReturnType`
- **位置**: 第 649 行, 第 15 列
- **错误信息**: "None" 类型不匹配返回类型 "bool"
  "None" 与 "bool" 不兼容

#### 39. d:\Python\fcmrawler\src\services\batch_analysis_service.py:274

- **规则**: `reportInvalidTypeForm`
- **位置**: 第 274 行, 第 63 列
- **错误信息**: 类型表达式中不允许使用变量

#### 40. d:\Python\fcmrawler\src\services\batch_analysis_service.py:367

- **规则**: `reportArgumentType`
- **位置**: 第 367 行, 第 20 列
- **错误信息**: "Unknown | BaseException" 类型的实参无法赋值给函数 "__setitem__" 中 "Dict[str, Any]" 类型的形参 "value"
  "Unknown | BaseException" 类型与 "Dict[str, Any]" 类型不兼容
    "BaseException" 与 "Dict[str, Any]" 不兼容

#### 41. d:\Python\fcmrawler\src\services\batch_crawl_service.py:293

- **规则**: `reportArgumentType`
- **位置**: 第 293 行, 第 27 列
- **错误信息**: "int | Unknown | None" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "session_id"
  "int | Unknown | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 42. d:\Python\fcmrawler\src\services\batch_crawl_service.py:311

- **规则**: `reportArgumentType`
- **位置**: 第 311 行, 第 48 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "query_batch_crawl_tasks" 中 "int" 类型的形参 "session_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 43. d:\Python\fcmrawler\src\services\batch_crawl_service.py:435

- **规则**: `reportArgumentType`
- **位置**: 第 435 行, 第 39 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "complete_task" 中 "int" 类型的形参 "result_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 44. d:\Python\fcmrawler\src\services\change_detector.py:878

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 878 行, 第 20 列
- **错误信息**: "json" 可能未绑定

#### 45. d:\Python\fcmrawler\src\services\cms_detector.py:145

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 145 行, 第 34 列
- **错误信息**: "html_match_score" 可能未绑定

#### 46. d:\Python\fcmrawler\src\services\cms_detector.py:408

- **规则**: `reportOptionalOperand`
- **位置**: 第 408 行, 第 67 列
- **错误信息**: `None` 不支持 "<" 运算符

#### 47. d:\Python\fcmrawler\src\services\cms_detector.py:408

- **规则**: `reportOptionalOperand`
- **位置**: 第 408 行, 第 83 列
- **错误信息**: `None` 不支持 ">" 运算符

#### 48. d:\Python\fcmrawler\src\services\cms_detector.py:413

- **规则**: `reportOptionalOperand`
- **位置**: 第 413 行, 第 75 列
- **错误信息**: `None` 不支持 "<" 运算符

#### 49. d:\Python\fcmrawler\src\services\cms_detector.py:413

- **规则**: `reportOptionalOperand`
- **位置**: 第 413 行, 第 94 列
- **错误信息**: `None` 不支持 ">" 运算符

#### 50. d:\Python\fcmrawler\src\services\crawl_execution_service.py:571

- **规则**: `reportArgumentType`
- **位置**: 第 571 行, 第 22 列
- **错误信息**: "str | Unknown | int | Dict[str, Any] | Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str | None" 类型的形参 "title"
  "str | Unknown | int | Dict[str, Any] | Any | None" 类型与 "str | None" 类型不兼容
    "int" 类型与 "str | None" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "None" 不兼容

#### 51. d:\Python\fcmrawler\src\services\crawl_execution_service.py:579

- **规则**: `reportArgumentType`
- **位置**: 第 579 行, 第 29 列
- **错误信息**: "str | Unknown | int | Dict[str, Any]" 类型的实参无法赋值给函数 "__init__" 中 "str | None" 类型的形参 "content_hash"
  "str | Unknown | int | Dict[str, Any]" 类型与 "str | None" 类型不兼容
    "int" 类型与 "str | None" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "None" 不兼容

#### 52. d:\Python\fcmrawler\src\services\custom_report_generator.py:49

- **规则**: `reportMissingImports`
- **位置**: 第 49 行, 第 11 列
- **错误信息**: 无法解析导入 "weasyprint"

#### 53. d:\Python\fcmrawler\src\services\custom_report_generator.py:215

- **规则**: `reportArgumentType`
- **位置**: 第 215 行, 第 47 列
- **错误信息**: "list[str]" 类型的实参无法赋值给函数 "__init__" 中 "Axes | None" 类型的形参 "columns"
  "list[str]" 类型与 "Axes | None" 类型不兼容
    "list[str]" 与 "ExtensionArray" 不兼容
    "list[str]" 与 "ndarray[_AnyShape, dtype[Any]]" 不兼容
    "list[str]" 与 "Index" 不兼容
    "list[str]" 与 "Series" 不兼容
    "list[str]" 与 Protocol 类 "SequenceNotStr[Unknown]" 不兼容
      "index" 类型不兼容
        "(value: str, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize, /) -> int" 类型与 "(value: Any, /, start: int = 0, stop: int = ...) -> int" 类型不兼容
  ...

#### 54. d:\Python\fcmrawler\src\services\custom_report_generator.py:871

- **规则**: `reportArgumentType`
- **位置**: 第 871 行, 第 36 列
- **错误信息**: "BytesIO" 类型的实参无法赋值给函数 "__new__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
  "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
    "BytesIO" 与 "str" 不兼容
    "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
      "__fspath__" 不存在
    "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
      "truncate" 类型不兼容
        "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
          缺少关键字参数 "size"
  ...

#### 55. d:\Python\fcmrawler\src\services\custom_report_generator.py:871

- **规则**: `reportArgumentType`
- **位置**: 第 871 行, 第 36 列
- **错误信息**: "BytesIO" 类型的实参无法赋值给函数 "__init__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
  "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
    "BytesIO" 与 "str" 不兼容
    "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
      "__fspath__" 不存在
    "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
      "truncate" 类型不兼容
        "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
          缺少关键字参数 "size"

#### 56. d:\Python\fcmrawler\src\services\data_query_service.py:657

- **规则**: `reportArgumentType`
- **位置**: 第 657 行, 第 36 列
- **错误信息**: "BytesIO" 类型的实参无法赋值给函数 "__new__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
  "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
    "BytesIO" 与 "str" 不兼容
    "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
      "__fspath__" 不存在
    "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
      "truncate" 类型不兼容
        "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
          缺少关键字参数 "size"
  ...

#### 57. d:\Python\fcmrawler\src\services\data_query_service.py:657

- **规则**: `reportArgumentType`
- **位置**: 第 657 行, 第 36 列
- **错误信息**: "BytesIO" 类型的实参无法赋值给函数 "__init__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
  "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
    "BytesIO" 与 "str" 不兼容
    "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
      "__fspath__" 不存在
    "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
      "truncate" 类型不兼容
        "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
          缺少关键字参数 "size"

#### 58. d:\Python\fcmrawler\src\services\field_management_service.py:772

- **规则**: `reportArgumentType`
- **位置**: 第 772 行, 第 52 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "_import_fields_with_merge_strategy" 中 "int" 类型的形参 "field_list_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 59. d:\Python\fcmrawler\src\services\field_management_service.py:1179

- **规则**: `reportArgumentType`
- **位置**: 第 1179 行, 第 24 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "update_field" 中 "int" 类型的形参 "field_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 60. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:331

- **规则**: `reportArgumentType`
- **位置**: 第 331 行, 第 39 列
- **错误信息**: "list[Any]" 类型的实参无法赋值给函数 "get" 中 "_AttributeValue | None" 类型的形参 "default"
  "list[Any]" 类型与 "_AttributeValue | None" 类型不兼容
    "list[Any]" 与 "str" 不兼容
    "list[Any]" 与 "AttributeValueList" 不兼容
    "list[Any]" 与 "None" 不兼容

#### 61. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:350

- **规则**: `reportArgumentType`
- **位置**: 第 350 行, 第 39 列
- **错误信息**: "list[Any]" 类型的实参无法赋值给函数 "get" 中 "_AttributeValue | None" 类型的形参 "default"
  "list[Any]" 类型与 "_AttributeValue | None" 类型不兼容
    "list[Any]" 与 "str" 不兼容
    "list[Any]" 与 "AttributeValueList" 不兼容
    "list[Any]" 与 "None" 不兼容

#### 62. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:390

- **规则**: `reportArgumentType`
- **位置**: 第 390 行, 第 43 列
- **错误信息**: "list[Any]" 类型的实参无法赋值给函数 "get" 中 "_AttributeValue | None" 类型的形参 "default"
  "list[Any]" 类型与 "_AttributeValue | None" 类型不兼容
    "list[Any]" 与 "str" 不兼容
    "list[Any]" 与 "AttributeValueList" 不兼容
    "list[Any]" 与 "None" 不兼容

#### 63. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:430

- **规则**: `reportArgumentType`
- **位置**: 第 430 行, 第 23 列
- **错误信息**: "Literal['tag']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['tag']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['tag']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['tag']" 与 "slice[Any, Any, Any]" 不兼容

#### 64. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:431

- **规则**: `reportArgumentType`
- **位置**: 第 431 行, 第 27 列
- **错误信息**: "Literal['classes']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['classes']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['classes']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['classes']" 与 "slice[Any, Any, Any]" 不兼容

#### 65. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:432

- **规则**: `reportArgumentType`
- **位置**: 第 432 行, 第 25 列
- **错误信息**: "Literal['xpath']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['xpath']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['xpath']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['xpath']" 与 "slice[Any, Any, Any]" 不兼容

#### 66. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:434

- **规则**: `reportArgumentType`
- **位置**: 第 434 行, 第 31 列
- **错误信息**: "Literal['text_length']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['text_length']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['text_length']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['text_length']" 与 "slice[Any, Any, Any]" 不兼容

#### 67. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:435

- **规则**: `reportArgumentType`
- **位置**: 第 435 行, 第 31 列
- **错误信息**: "Literal['child_count']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['child_count']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['child_count']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['child_count']" 与 "slice[Any, Any, Any]" 不兼容

#### 68. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:436

- **规则**: `reportArgumentType`
- **位置**: 第 436 行, 第 25 列
- **错误信息**: "Literal['depth']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['depth']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['depth']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['depth']" 与 "slice[Any, Any, Any]" 不兼容

#### 69. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:498

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 498 行, 第 63 列
- **错误信息**: 无法访问 "list[dict[str, Unknown]]" 类的 "items" 属性
  属性 "items" 未知

#### 70. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:498

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 498 行, 第 63 列
- **错误信息**: 无法访问 "list[Unknown]" 类的 "items" 属性
  属性 "items" 未知

#### 71. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:501

- **规则**: `reportIndexIssue`
- **位置**: 第 501 行, 第 44 列
- **错误信息**: "int" 类型上未定义 "__getitem__" 方法

#### 72. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:505

- **规则**: `reportArgumentType`
- **位置**: 第 505 行, 第 24 列
- **错误信息**: "Literal[0]" 类型的实参无法赋值给函数 "__getitem__" 中 "str" 类型的形参 "key"
  "Literal[0]" 与 "str" 不兼容

#### 73. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:506

- **规则**: `reportIndexIssue`
- **位置**: 第 506 行, 第 15 列
- **错误信息**: "int" 类型上未定义 "__getitem__" 方法

#### 74. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:506

- **规则**: `reportCallIssue`
- **位置**: 第 506 行, 第 15 列
- **错误信息**: "__getitem__" 的重载与提供的参数不匹配

#### 75. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:506

- **规则**: `reportArgumentType`
- **位置**: 第 506 行, 第 15 列
- **错误信息**: "Literal['classes']" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
  "Literal['classes']" 与 "slice[Any, Any, Any]" 不兼容

#### 76. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:507

- **规则**: `reportIndexIssue`
- **位置**: 第 507 行, 第 45 列
- **错误信息**: "int" 类型上未定义 "__getitem__" 方法

#### 77. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:507

- **规则**: `reportCallIssue`
- **位置**: 第 507 行, 第 45 列
- **错误信息**: "__getitem__" 的重载与提供的参数不匹配

#### 78. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:507

- **规则**: `reportArgumentType`
- **位置**: 第 507 行, 第 45 列
- **错误信息**: "Literal['classes']" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
  "Literal['classes']" 与 "slice[Any, Any, Any]" 不兼容

#### 79. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:509

- **规则**: `reportIndexIssue`
- **位置**: 第 509 行, 第 41 列
- **错误信息**: "int" 类型上未定义 "__getitem__" 方法

#### 80. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:509

- **规则**: `reportCallIssue`
- **位置**: 第 509 行, 第 41 列
- **错误信息**: "__getitem__" 的重载与提供的参数不匹配

#### 81. d:\Python\fcmrawler\src\services\page_structure_analyzer.py:509

- **规则**: `reportArgumentType`
- **位置**: 第 509 行, 第 41 列
- **错误信息**: "Literal['tag']" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
  "Literal['tag']" 与 "slice[Any, Any, Any]" 不兼容

#### 82. d:\Python\fcmrawler\src\services\time_series_analyzer.py:20

- **规则**: `reportMissingImports`
- **位置**: 第 20 行, 第 5 列
- **错误信息**: 无法解析导入 "scipy"

#### 83. d:\Python\fcmrawler\src\services\time_series_analyzer.py:21

- **规则**: `reportMissingImports`
- **位置**: 第 21 行, 第 5 列
- **错误信息**: 无法解析导入 "scipy.signal"

#### 84. d:\Python\fcmrawler\src\services\url_service.py:708

- **规则**: `reportOperatorIssue`
- **位置**: 第 708 行, 第 20 列
- **错误信息**: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "int" 类型不支持 "+" 运算符

#### 85. d:\Python\fcmrawler\src\services\url_service.py:713

- **规则**: `reportOperatorIssue`
- **位置**: 第 713 行, 第 20 列
- **错误信息**: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "int" 类型不支持 "+" 运算符

#### 86. d:\Python\fcmrawler\src\services\url_service.py:720

- **规则**: `reportOperatorIssue`
- **位置**: 第 720 行, 第 24 列
- **错误信息**: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符

#### 87. d:\Python\fcmrawler\src\services\url_service.py:725

- **规则**: `reportOperatorIssue`
- **位置**: 第 725 行, 第 28 列
- **错误信息**: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "int" 类型不支持 "+" 运算符

#### 88. d:\Python\fcmrawler\src\services\url_service.py:726

- **规则**: `reportOperatorIssue`
- **位置**: 第 726 行, 第 28 列
- **错误信息**: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "int" 类型不支持 "+" 运算符

#### 89. d:\Python\fcmrawler\src\services\url_service.py:730

- **规则**: `reportOperatorIssue`
- **位置**: 第 730 行, 第 24 列
- **错误信息**: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符

#### 90. d:\Python\fcmrawler\src\services\url_service.py:731

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 731 行, 第 40 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 91. d:\Python\fcmrawler\src\services\url_service.py:734

- **规则**: `reportOperatorIssue`
- **位置**: 第 734 行, 第 20 列
- **错误信息**: "int | Unknown | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符

#### 92. d:\Python\fcmrawler\src\services\url_service.py:736

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 736 行, 第 36 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 93. d:\Python\fcmrawler\src\services\url_service.py:740

- **规则**: `reportOperatorIssue`
- **位置**: 第 740 行, 第 15 列
- **错误信息**: "int | Unknown | list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符
  "list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符

#### 94. d:\Python\fcmrawler\src\services\url_service.py:754

- **规则**: `reportOperatorIssue`
- **位置**: 第 754 行, 第 28 列
- **错误信息**: "int | Unknown | list[Unknown]" 与 "Literal[1048576]" 类型不支持 "/" 运算符
  "list[Unknown]" 与 "Literal[1048576]" 类型不支持 "/" 运算符

#### 95. d:\Python\fcmrawler\src\services\url_service.py:755

- **规则**: `reportOperatorIssue`
- **位置**: 第 755 行, 第 51 列
- **错误信息**: "int | Unknown | list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符
  "list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符

#### 96. d:\Python\fcmrawler\src\services\version_manager.py:339

- **规则**: `reportArgumentType`
- **位置**: 第 339 行, 第 56 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "delete_field_version" 中 "int" 类型的形参 "version_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

## ⚠️ 警告详情

共发现 **3373** 个警告

1. `d:\Python\fcmrawler\src\__init__.py:14` - "Config" 导入项未使用 (`reportUnusedImport`)
2. `d:\Python\fcmrawler\src\__init__.py:15` - "ConfigManager" 导入项未使用 (`reportUnusedImport`)
3. `d:\Python\fcmrawler\src\__init__.py:16` - "Url" 导入项未使用 (`reportUnusedImport`)
4. `d:\Python\fcmrawler\src\__init__.py:19` - "get_cms_detector" 导入项未使用 (`reportUnusedImport`)
5. `d:\Python\fcmrawler\src\__init__.py:20` - "get_config_generator" 导入项未使用 (`reportUnusedImport`)
6. `d:\Python\fcmrawler\src\__init__.py:21` - "get_config_quality_assessor" 导入项未使用 (`reportUnusedImport`)
7. `d:\Python\fcmrawler\src\__init__.py:22` - "get_domain_analyzer" 导入项未使用 (`reportUnusedImport`)
8. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:18` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
9. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:18` - 此类型自 Python 3.9 起已弃用；请改用 "list" (`reportDeprecated`)
10. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:18` - 此类型自 Python 3.10 起已弃用；请改用 "| None" (`reportDeprecated`)
11. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:37` - 此类型自 Python 3.10 起已弃用；请改用 "| None" (`reportDeprecated`)
12. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:37` - 此类型自 Python 3.10 起已弃用；请改用 "| None" (`reportDeprecated`)
13. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:52` - 由于这个类未使用 `@final` 装饰，其 `output_dir` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
14. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:61` - 由于这个类未使用 `@final` 装饰，其 `template_dir` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
15. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:71` - 由于这个类未使用 `@final` 装饰，其 `env` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
16. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:74` - 由于这个类未使用 `@final` 装饰，其 `template_available` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
17. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
18. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164` - 不允许使用 `Any` 类型 (`reportExplicitAny`)
19. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
20. `d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164` - 不允许使用 `Any` 类型 (`reportExplicitAny`)

... 还有 3353 个警告未显示

## 📁 检查的文件列表

1. `src\__init__.py`
2. `src\core\__init__.py`
3. `src\core\ai_analysis_report_generator.py`
4. `src\core\analyzer.py`
5. `src\core\exporters\base_exporter.py`
6. `src\core\exporters\csv_exporter.py`
7. `src\core\exporters\excel_exporter.py`
8. `src\core\exporters\html_report_exporter.py`
9. `src\core\exporters\json_exporter.py`
10. `src\core\extractor.py`
11. `src\core\reporter.py`
12. `src\core\utils\__init__.py`
13. `src\core\utils\diff_analyzer.py`
14. `src\core\utils\template_engine.py`
15. `src\gui\__init__.py`
16. `src\gui\dialogs\__init__.py`
17. `src\gui\dialogs\ai_config_review_dialog.py`
18. `src\gui\dialogs\async_dialog_base.py`
19. `src\gui\dialogs\backup_management_dialog.py`
20. `src\gui\dialogs\batch_analysis_dialog.py`
21. `src\gui\dialogs\batch_crawl_dialog.py`
22. `src\gui\dialogs\config_editor_dialog.py`
23. `src\gui\dialogs\config_preview_dialog.py`
24. `src\gui\dialogs\content_browser_dialog.py`
25. `src\gui\dialogs\content_search_dialog.py`
26. `src\gui\dialogs\custom_report_dialog.py`
27. `src\gui\dialogs\data_export_dialog.py`
28. `src\gui\dialogs\data_query_dialog.py`
29. `src\gui\dialogs\excel_import_dialog.py`
30. `src\gui\dialogs\field_list_manager_dialog.py`
31. `src\gui\dialogs\field_template_dialog.py`
32. `src\gui\dialogs\field_validation_rules_dialog.py`
33. `src\gui\dialogs\settings_dialog.py`
34. `src\gui\dialogs\single_url_analysis_dialog.py`
35. `src\gui\dialogs\single_url_crawl_dialog.py`
36. `src\gui\dialogs\test_results_dialog.py`
37. `src\gui\dialogs\url_comparison_dialog.py`
38. `src\gui\main_window.py`
39. `src\gui\widgets\chart_widget.py`
40. `src\gui\widgets\data_dashboard_widget.py`
41. `src\gui\widgets\time_series_widget.py`
42. `src\legacy\__init__.py`
43. `src\legacy\element_extractor.py`
44. `src\legacy\website_analyzer.py`
45. `src\main.py`
46. `src\models\__init__.py`
47. `src\models\config.py`
48. `src\models\database.py`
49. `src\models\database_exceptions.py`
50. `src\models\entities.py`
51. `src\models\exceptions.py`
52. `src\models\field_change_detection_migration.py`
53. `src\models\field_schema_migration.py`
54. `src\models\url.py`
55. `src\models\url_config_migration.py`
56. `src\services\__init__.py`
57. `src\services\ai_analysis_service.py`
58. `src\services\ai_config_generator_service.py`
59. `src\services\api_test_service.py`
60. `src\services\async_config_bridge.py`
61. `src\services\audit_service.py`
62. `src\services\backup_service.py`
63. `src\services\batch_analysis_service.py`
64. `src\services\batch_crawl_service.py`
65. `src\services\cache_manager.py`
66. `src\services\change_detector.py`
67. `src\services\cms_detector.py`
68. `src\services\config_generator.py`
69. `src\services\config_quality_assessor.py`
70. `src\services\config_service.py`
71. `src\services\config_test_service.py`
72. `src\services\config_validator.py`
73. `src\services\content_deduplication_service.py`
74. `src\services\content_search_service.py`
75. `src\services\crawl_execution_service.py`
76. `src\services\crawl_service.py`
77. `src\services\custom_report_generator.py`
78. `src\services\data_export_service.py`
79. `src\services\data_query_service.py`
80. `src\services\data_statistics_service.py`
81. `src\services\domain_analyzer.py`
82. `src\services\excel_import_service.py`
83. `src\services\field_management_service.py`
84. `src\services\field_template_manager.py`
85. `src\services\field_validator.py`
86. `src\services\kimi_client.py`
87. `src\services\page_structure_analyzer.py`
88. `src\services\persistence_service.py`
89. `src\services\pii_detector.py`
90. `src\services\rate_limiter.py`
91. `src\services\result_formatter.py`
92. `src\services\selector_generator.py`
93. `src\services\selector_optimizer.py`
94. `src\services\selector_tester.py`
95. `src\services\storage_manager.py`
96. `src\services\time_series_analyzer.py`
97. `src\services\url_service.py`
98. `src\services\url_validator.py`
99. `src\services\version_manager.py`
100. `src\utils\__init__.py`
101. `src\utils\async_bridge.py`
102. `src\utils\crypto.py`
103. `src\utils\data_validator.py`
104. `src\utils\key_manager.py`
105. `src\utils\performance_profiler.py`
106. `src\utils\request_rate_limiter.py`
107. `src\utils\retry_strategy.py`

## 📄 原始检查输出

```
d:\Python\fcmrawler\src\__init__.py
  d:\Python\fcmrawler\src\__init__.py:14:32 - warning: "Config" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\__init__.py:15:32 - warning: "ConfigManager" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\__init__.py:16:29 - warning: "Url" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\__init__.py:19:40 - warning: "get_cms_detector" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\__init__.py:20:44 - warning: "get_config_generator" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\__init__.py:21:51 - warning: "get_config_quality_assessor" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\__init__.py:22:43 - warning: "get_domain_analyzer" 导入项未使用 (reportUnusedImport)
d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:18:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:18:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:18:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:37:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:37:72 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:52:14 - warning: 由于这个类未使用 `@final` 装饰，其 `output_dir` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:61:14 - warning: 由于这个类未使用 `@final` 装饰，其 `template_dir` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:71:18 - warning: 由于这个类未使用 `@final` 装饰，其 `env` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:74:18 - warning: 由于这个类未使用 `@final` 装饰，其 `template_available` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:164:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:165:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:165:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:219:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:219:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:219:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:219:96 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:219:105 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:219:115 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:264:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:264:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:299:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:299:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:299:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:299:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:299:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:299:84 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:300:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:300:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:354:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:354:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:396:25 - warning: "ai_result" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:396:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:396:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:396:52 - warning: "selectors" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:396:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:396:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:397:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:397:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:451:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:451:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:798:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:798:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:798:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:799:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:799:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:838:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:838:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:838:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:838:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:838:85 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:914:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:914:76 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:914:86 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:915:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:915:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:915:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:998:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:998:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:998:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:998:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:998:76 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:998:86 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:999:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:999:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1063:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1063:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1063:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1098:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1098:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1129:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1129:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1129:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1129:96 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1129:106 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1174:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1174:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1174:78 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1265:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1302:12 - warning: 条件的计算结果始终为 `False`，因为类型 "str" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1303:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1341:12 - warning: 条件的计算结果始终为 `False`，因为类型 "str" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1342:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1376:12 - warning: 条件的计算结果始终为 `False`，因为类型 "str" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1377:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1430:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1430:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1440:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\ai_analysis_report_generator.py:1441:13 - warning: 代码不会被执行 (reportUnreachable)
d:\Python\fcmrawler\src\core\analyzer.py
  d:\Python\fcmrawler\src\core\analyzer.py:40:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:49:54 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:78:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\analyzer.py:87:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:93:12 - warning: 条件的计算结果始终为 `False`，因为类型 "dict[str, dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\analyzer.py:97:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:103:12 - warning: 条件的计算结果始终为 `False`，因为类型 "dict[str, dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\analyzer.py:107:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:107:95 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:137:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:154:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:157:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:157:109 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:190:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:212:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:215:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:233:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:233:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\analyzer.py:303:39 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\core\exporters\base_exporter.py
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:20:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:20:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:20:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:20:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:36:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:37:14 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:37:24 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:38:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:39:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:40:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:47:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_memory_mb` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:48:14 - warning: 由于这个类未使用 `@final` 装饰，其 `chunk_size` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:101:14 - warning: 由于这个类未使用 `@final` 装饰，其 `format_name` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:102:14 - warning: 由于这个类未使用 `@final` 装饰，其 `memory_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:103:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_progress_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:104:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_cancel_flag` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:106:37 - warning: "callback" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:88 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:97 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:172:107 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:173:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:173:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:173:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:77 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:198:101 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:85 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:249:95 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:266:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:266:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:266:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:268:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:269:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:269:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:303:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:303:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:303:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:304:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:305:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:305:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:306:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:306:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:306:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:332:20 - warning: "List[Dict[str, Any]]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:333:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:359:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:359:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:359:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:361:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:362:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:362:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:384:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:384:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:384:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:386:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:387:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:387:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:432:29 - warning: 变量 "e" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:439:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:439:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:439:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:448:40 - warning: "output_path" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:448:59 - warning: "fields" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:448:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:458:28 - warning: "chunk" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:458:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:458:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:458:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:458:57 - warning: "is_first_chunk" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:468:38 - warning: "output_path" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:477:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:526:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:526:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:526:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:539:16 - warning: 条件的计算结果始终为 `False`，因为类型 "List[Dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:540:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:542:20 - warning: "List[Dict[str, Any]]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\exporters\base_exporter.py:543:17 - warning: 代码不会被执行 (reportUnreachable)
d:\Python\fcmrawler\src\core\exporters\csv_exporter.py
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:34:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:35:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:39:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:39:89 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:83:9 - warning: "export_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:85:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:88:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:140:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:140:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:159:16 - warning: 条件的计算结果始终为 `False`，因为类型 "list[dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:160:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:187:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:187:103 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:223:52 - warning: 条件的计算结果始终为 `True`，因为类型 "dict[str, Any]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:249:52 - warning: 条件的计算结果始终为 `True`，因为类型 "dict[str, Any]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:258:28 - warning: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:273:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:273:49 - warning: "options" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:273:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:273:87 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:305:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:307:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:328:16 - warning: 条件的计算结果始终为 `False`，因为类型 "list[dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:329:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:391:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:402:9 - warning: 变量 "compact_options" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:411:16 - warning: 条件的计算结果始终为 `True`，因为类型 "ExportMetadata" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:414:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:428:9 - warning: 变量 "custom_options" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:437:16 - warning: 条件的计算结果始终为 `True`，因为类型 "ExportMetadata" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:439:9 - warning: "_write_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:441:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:462:9 - warning: "_validate_file_format" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:487:9 - warning: "get_file_extension" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:491:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:491:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:554:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\csv_exporter.py:561:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\core\exporters\excel_exporter.py
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:15:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:15:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:15:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:15:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:26:8 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:47:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:47:33 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:48:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:48:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:49:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:49:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:49:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:49:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:50:30 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:50:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:50:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:51:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:53:9 - warning: "_write_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:55:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:55:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:55:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:68:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:68:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:68:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:68:82 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:68:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:68:101 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:137:33 - warning: "worksheet" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:137:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:137:81 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:173:41 - warning: "worksheet" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:188:43 - warning: "worksheet" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:197:28 - warning: "worksheet" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:207:37 - warning: "writer" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:229:34 - warning: "writer" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:229:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:229:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:229:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:262:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:262:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:262:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:266:9 - warning: "export_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:268:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:268:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:268:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:269:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:270:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:270:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:271:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:271:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:271:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:307:9 - warning: 变量 "success" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:323:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:323:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:323:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:323:82 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:323:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:323:101 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:342:16 - warning: 条件的计算结果始终为 `False`，因为类型 "List[Dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:343:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:370:9 - warning: "_validate_file_format" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:382:13 - warning: 变量 "df" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:388:9 - warning: "get_file_extension" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:394:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:394:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:394:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:396:29 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:396:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:396:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:397:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:420:16 - warning: 条件的计算结果始终为 `False`，因为类型 "List[Dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:421:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:15 - warning: "data" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:62 - warning: "formatting_options" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:82 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:430:101 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:444:13 - warning: "chunk_processor" 函数未使用 (reportUnusedFunction)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:444:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:444:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:444:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:444:74 - warning: "total_size" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:476:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:476:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:483:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\excel_exporter.py:483:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:19:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:19:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:19:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:19:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:54:14 - warning: 由于这个类未使用 `@final` 装饰，其 `html_config` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:66:14 - warning: 由于这个类未使用 `@final` 装饰，其 `default_template` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:67:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:68:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:69:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:71:9 - warning: "export_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:73:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:73:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:73:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:74:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:75:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:75:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:76:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:76:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:76:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:112:9 - warning: 变量 "success" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:127:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:127:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:127:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:127:98 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:127:107 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:127:117 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:145:16 - warning: 条件的计算结果始终为 `False`，因为类型 "List[Dict[str, Any]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:146:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:173:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:173:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:173:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:173:94 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:173:103 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:173:113 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:207:102 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:246:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:246:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:246:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:246:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:246:75 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:281:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:281:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:281:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:281:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:281:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:297:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:297:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:325:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:325:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:325:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:325:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:325:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:338:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:338:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:349:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:349:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:377:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:377:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:411:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:411:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:411:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:411:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:411:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:424:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:445:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:445:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:445:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:445:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:445:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:471:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:471:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:471:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:471:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:471:84 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:507:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:507:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:507:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:507:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:507:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:521:17 - warning: 变量 "key" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:546:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:546:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:546:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:546:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:546:82 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:590:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:590:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:590:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:590:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:590:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:603:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:603:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:615:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:627:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:627:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:627:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:627:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:658:32 - warning: "value" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:664:30 - warning: "value" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:84 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:93 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:890:103 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:918:9 - warning: "_write_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:920:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:920:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:920:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:943:9 - warning: "_validate_file_format" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:977:9 - warning: "get_file_extension" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:983:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:983:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:983:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:986:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:986:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:986:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:1025:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:1025:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:1032:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\html_report_exporter.py:1032:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\core\exporters\json_exporter.py
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:16:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:16:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:16:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:16:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:44:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:44:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:47:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:47:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:47:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:61:9 - warning: 变量 "pretty_options" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:71:20 - warning: 条件的计算结果始终为 `True`，因为类型 "ExportMetadata" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:76:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:76:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:76:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:87:9 - warning: 变量 "compact_options" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:91:20 - warning: 条件的计算结果始终为 `True`，因为类型 "ExportMetadata" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:98:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:98:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:98:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:100:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:100:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:100:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:121:20 - warning: 条件的计算结果始终为 `True`，因为类型 "ExportMetadata" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:126:9 - warning: "export_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:128:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:128:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:128:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:129:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:130:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:130:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:131:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:131:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:131:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:167:9 - warning: 变量 "success" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:183:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:183:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:183:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:183:78 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:183:87 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:183:97 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:196:9 - warning: 变量 "options" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:199:20 - warning: 条件的计算结果始终为 `True`，因为类型 "ExportMetadata" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:204:9 - warning: "_write_data" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:206:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:206:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:206:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:221:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:221:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:221:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:221:94 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:221:103 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:221:113 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:231:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:231:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:81 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:90 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:253:100 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:267:52 - warning: 条件的计算结果始终为 `True`，因为类型 "Dict[str, Any]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:275:24 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:290:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:290:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:295:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:295:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:309:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:309:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:314:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:314:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:314:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:314:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:314:83 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:314:93 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:326:12 - warning: 条件的计算结果始终为 `False`，因为类型 "Dict[str, Any]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:327:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:330:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:331:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:345:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:345:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:345:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:345:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:381:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:381:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:381:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:381:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:408:9 - warning: "_create_metadata" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:410:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:410:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:410:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:412:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:413:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:413:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:449:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:449:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:449:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:449:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:449:75 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:462:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:462:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:470:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:470:40 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:498:9 - warning: "_validate_file_format" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:519:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:519:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:526:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:526:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:540:9 - warning: "get_file_extension" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:544:9 - warning: "_check_cancellation" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:548:9 - warning: "_update_progress" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\core\exporters\json_exporter.py:554:9 - warning: "_calculate_file_checksum" 方法没有用 `@override` 装饰，但覆写了 "BaseExporter" 类中的方法 (reportImplicitOverride)
d:\Python\fcmrawler\src\core\extractor.py
  d:\Python\fcmrawler\src\core\extractor.py:20:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:20:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:20:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:45:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_extractor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\extractor.py:46:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:47:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_supported_field_types` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\extractor.py:48:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:48:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:48:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:88:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:88:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:91:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:91:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:132:68 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:132:78 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:144:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:144:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:171:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:171:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:171:59 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:171:68 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:171:78 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:172:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:172:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:202:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:202:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:203:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:203:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:203:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:225:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:233:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:233:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:246:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:246:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:246:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:246:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:247:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:247:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:250:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:250:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:250:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:250:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:286:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:286:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:286:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:286:100 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:286:105 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:286:115 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:298:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:298:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:298:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:298:94 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:298:99 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:298:109 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:320:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:320:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:320:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:320:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:365:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:365:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:365:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:365:89 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:375:29 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\extractor.py:413:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\extractor.py:413:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\extractor.py:413:61 - warning: "field_type" 未使用 (reportUnusedParameter)
d:\Python\fcmrawler\src\core\reporter.py
  d:\Python\fcmrawler\src\core\reporter.py:21:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:21:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:21:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:32:14 - warning: 由于这个类未使用 `@final` 装饰，其 `ai_generator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\reporter.py:34:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:34:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:34:53 - warning: "output_path" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:34:73 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\reporter.py:65:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_generator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\reporter.py:66:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:67:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_supported_formats` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\reporter.py:68:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_available_templates` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\reporter.py:69:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:70:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_cache_enabled` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\reporter.py:82:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:82:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:84:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:85:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:85:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:85:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:86:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:151:15 - warning: "analysis_data" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:151:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:151:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:151:58 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:152:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:152:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:182:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:182:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:182:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:182:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:195:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:195:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:205:17 - warning: 变量 "field_type" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\reporter.py:243:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:251:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:259:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:259:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:270:20 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\reporter.py:271:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\reporter.py:295:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:295:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:295:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:295:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:295:95 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:295:104 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:296:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:330:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:330:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:330:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:330:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:331:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:360:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:360:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:360:92 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:396:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:396:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:396:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:396:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:408:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:408:39 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:417:13 - warning: 变量 "total_possible_types" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\reporter.py:475:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:475:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:522:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:522:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:522:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:522:77 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:552:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:552:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:552:56 - warning: "output_dir" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:552:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:552:83 - warning: "options" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:552:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:552:102 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:553:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:567:42 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\reporter.py:574:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:574:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:574:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:574:83 - warning: "options" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:574:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:574:102 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:597:15 - warning: "analysis_data" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:597:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:597:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:597:46 - warning: "url" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:597:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:597:83 - warning: "options" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:597:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:597:102 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:614:15 - warning: "analysis_data" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:614:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:614:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:614:46 - warning: "url" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:614:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:614:83 - warning: "options" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\core\reporter.py:614:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:614:102 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:630:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:630:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:630:85 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:630:95 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:637:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:637:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:637:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:637:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:637:90 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:640:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:640:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:661:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:661:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\reporter.py:705:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\reporter.py:705:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\core\utils\diff_analyzer.py
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:16:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:16:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:16:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:41:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:44:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:44:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:57:16 - warning: 条件的计算结果始终为 `False`，因为类型 "str" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:57:31 - warning: 条件的计算结果始终为 `False`，因为类型 "str" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:58:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:107:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:107:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:153:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:153:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:222:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:226:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:230:39 - warning: "old_soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:230:49 - warning: "new_soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:230:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:230:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:288:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:288:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:288:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:288:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:288:106 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:288:116 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:337:65 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:337:90 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:337:100 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:384:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:384:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:444:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:444:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\diff_analyzer.py:456:20 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
d:\Python\fcmrawler\src\core\utils\template_engine.py
  d:\Python\fcmrawler\src\core\utils\template_engine.py:6:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:13:14 - warning: 由于这个类未使用 `@final` 装饰，其 `content` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:15:24 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:20:25 - warning: "match" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:37:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:37:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:54:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:54:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:59:24 - warning: "match" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:72:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:72:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:76:25 - warning: "match" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:101:25 - warning: 变量 "key" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:110:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:110:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:117:28 - warning: "match" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:122:20 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:140:24 - warning: "loader" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:140:37 - warning: "autoescape" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:141:14 - warning: 由于这个类未使用 `@final` 装饰，其 `loader` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:142:14 - warning: 由于这个类未使用 `@final` 装饰，其 `autoescape` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:143:14 - warning: 由于这个类未使用 `@final` 装饰，其 `templates` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:144:14 - warning: 由于这个类未使用 `@final` 装饰，其 `globals` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:172:14 - warning: 由于这个类未使用 `@final` 装饰，其 `search_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\core\utils\template_engine.py:177:26 - warning: "environment" 未使用 (reportUnusedParameter)
d:\Python\fcmrawler\src\legacy\__init__.py
  d:\Python\fcmrawler\src\legacy\__init__.py:30:10 - error: 无法解析导入 ".report_generator" (reportMissingImports)
d:\Python\fcmrawler\src\legacy\element_extractor.py
  d:\Python\fcmrawler\src\legacy\element_extractor.py:12:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:12:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:12:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:12:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:12:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:18:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:18:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:31:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:31:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:41:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:44:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:51:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:51:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:91:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:91:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:142:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:150:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:150:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:195:14 - warning: 由于这个类未使用 `@final` 装饰，其 `patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:456:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:456:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:494:28 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:515:14 - warning: 由于这个类未使用 `@final` 装饰，其 `validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:516:14 - warning: 由于这个类未使用 `@final` 装饰，其 `matcher` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:517:14 - warning: 由于这个类未使用 `@final` 装饰，其 `extracted_fields` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:519:68 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:519:78 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:538:16 - warning: "List[Dict[str, Any]]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:552:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:552:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:552:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:584:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:584:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:584:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:605:22 - warning: 变量 "selector" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:623:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:623:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:623:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:646:22 - warning: 变量 "source" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:663:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:663:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:663:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:695:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:695:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:695:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:744:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:744:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:744:84 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:823:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:823:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:823:89 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:823:99 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:853:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:853:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:853:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:853:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:855:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:855:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:857:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:857:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\element_extractor.py:864:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\legacy\website_analyzer.py
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:15:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:15:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:15:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:15:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:15:47 - warning: "Union" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:22:8 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:38:14 - warning: 由于这个类未使用 `@final` 装饰，其 `title_patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:50:14 - warning: 由于这个类未使用 `@final` 装饰，其 `date_patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:64:14 - warning: 由于这个类未使用 `@final` 装饰，其 `link_patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:73:14 - warning: 由于这个类未使用 `@final` 装饰，其 `content_patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:80:68 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:129:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:141:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:141:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:141:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:142:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:143:14 - warning: 由于这个类未使用 `@final` 装饰，其 `detector` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:144:14 - warning: 由于这个类未使用 `@final` 装饰，其 `results` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:146:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:146:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:146:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:146:88 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:146:98 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:201:66 - warning: "page_title" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:201:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:201:96 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:310:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:310:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:310:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:310:84 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:357:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:357:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:357:67 - warning: "url" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:357:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:379:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:379:56 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:396:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:396:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:399:24 - warning: "tag_counts" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:399:36 - warning: "tag" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:425:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:425:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:425:80 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:425:97 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:425:102 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:425:112 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:454:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:454:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:454:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:475:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:475:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:475:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:543:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:543:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\legacy\website_analyzer.py:543:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\main.py
  d:\Python\fcmrawler\src\main.py:47:5 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_updated` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:79:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_widget` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:86:14 - warning: 由于这个类未使用 `@final` 装饰，其 `status_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:90:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_bar` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:127:9 - warning: "showEvent" 方法没有用 `@override` 装饰，但覆写了 "QWidget" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\main.py:127:25 - warning: "a0" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\main.py:143:5 - warning: 由于这个类未使用 `@final` 装饰，其 `loading_progress` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:144:5 - warning: 由于这个类未使用 `@final` 装饰，其 `loading_complete` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:145:5 - warning: 由于这个类未使用 `@final` 装饰，其 `loading_error` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:149:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:151:9 - warning: "run" 方法没有用 `@override` 装饰，但覆写了 "QThread" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\main.py:212:24 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\main.py:221:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:222:14 - warning: 由于这个类未使用 `@final` 装饰，其 `start_time` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:231:14 - warning: 由于这个类未使用 `@final` 装饰，其 `splash` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:235:14 - warning: 由于这个类未使用 `@final` 装饰，其 `loader` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\main.py:236:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\models\config.py
  d:\Python\fcmrawler\src\models\config.py:13:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:13:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:13:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:22:9 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:25:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:25:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\config.py:27:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:28:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:46:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:46:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\config.py:59:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:59:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\config.py:75:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:75:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\config.py:91:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:91:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\config.py:143:16 - warning: "int" 一定是 "int" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\config.py:155:16 - warning: "int" 一定是 "int" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\config.py:167:32 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\config.py:179:16 - warning: "bool" 一定是 "bool" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\config.py:180:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\models\config.py:191:16 - warning: "bool" 一定是 "bool" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\config.py:192:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\models\config.py:197:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:263:9 - warning: "__str__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\models\config.py:267:9 - warning: "__repr__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\models\config.py:279:24 - warning: "db_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\config.py:286:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\config.py:338:45 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:362:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\config.py:389:50 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\models\database.py
  d:\Python\fcmrawler\src\models\database.py: error: 导入链中检测到循环导入
    d:\Python\fcmrawler\src\models\database.py
    d:\Python\fcmrawler\src\models\field_schema_migration.py (reportImportCycles)
  d:\Python\fcmrawler\src\models\database.py: error: 导入链中检测到循环导入
    d:\Python\fcmrawler\src\models\database.py
    d:\Python\fcmrawler\src\models\field_change_detection_migration.py (reportImportCycles)
  d:\Python\fcmrawler\src\models\database.py:23:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:23:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "collections.abc.Iterator" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:23:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:23:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:23:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:55:5 - warning: 由于这个类未使用 `@final` 装饰，其 `CURRENT_VERSION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:58:5 - warning: 由于这个类未使用 `@final` 装饰，其 `VERSIONS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:81:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:81:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:94:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:95:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_local` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:96:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:797:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:844:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:873:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:902:21 - warning: "entity_class" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:914:19 - warning: "entity" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:952:35 - warning: "change" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:990:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1044:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1093:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1126:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1159:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1223:9 - warning: "save_url_config" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1223:31 - warning: "config" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:1223:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1265:66 - error: "int | None" 类型的实参无法赋值给函数 "_set_as_default_config_atomic" 中 "int" 类型的形参 "config_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\models\database.py:1273:9 - warning: "get_url_config" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1273:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1273:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1273:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:1307:9 - warning: "get_url_configs_by_url" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1307:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1307:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1307:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:1343:9 - warning: "get_default_url_config" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1343:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1343:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1343:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:1379:9 - warning: "update_url_config" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1379:33 - warning: "config" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:1419:9 - warning: "delete_url_config" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1443:9 - warning: "set_default_url_config" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\models\database.py:1494:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1557:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1592:60 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1592:85 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1638:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1652:73 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1742:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1835:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1888:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1888:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:1924:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1924:53 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1957:45 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:1992:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2080:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2124:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2198:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2253:53 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2283:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2325:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2384:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2415:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2518:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2555:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2555:89 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2603:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2603:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2653:67 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2654:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2669:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2669:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:2705:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2802:53 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2836:56 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2836:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2881:58 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2894:82 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2936:78 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2978:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2978:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2978:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:2978:101 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3022:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3139:73 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3201:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3235:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3305:58 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3305:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3305:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3305:89 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3305:94 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3305:104 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3338:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3338:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3338:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3339:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3339:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3381:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3381:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3381:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3382:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3382:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3462:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3462:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3463:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3463:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3463:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3528:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3528:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3529:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3529:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3529:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3579:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3579:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3580:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3580:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3580:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3636:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3636:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3637:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3637:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3637:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3776:49 - error: 无法访问 "Config" 类的 "config_data" 属性
    属性 "config_data" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3786:33 - error: 无法访问 "Config" 类的 "name" 属性
    属性 "name" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3786:59 - error: 无法访问 "Config" 类的 "is_default" 属性
    属性 "is_default" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3790:31 - error: 无法访问 "Config" 类的 "is_default" 属性
    属性 "is_default" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3791:81 - error: 无法访问 "Config" 类的 "url_id" 属性
    属性 "url_id" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3793:83 - error: 无法访问 "Config" 类的 "url_id" 属性
    属性 "url_id" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3802:33 - error: 无法访问 "Config" 类的 "url_id" 属性
    属性 "url_id" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3802:48 - error: 无法访问 "Config" 类的 "name" 属性
    属性 "name" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3802:74 - error: 无法访问 "Config" 类的 "is_default" 属性
    属性 "is_default" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3807:31 - error: 无法访问 "Config" 类的 "is_default" 属性
    属性 "is_default" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3808:63 - error: "int | None" 类型的实参无法赋值给函数 "_set_default_config_atomic" 中 "int" 类型的形参 "config_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\models\database.py:3808:81 - error: 无法访问 "Config" 类的 "url_id" 属性
    属性 "url_id" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3810:85 - error: 无法访问 "Config" 类的 "url_id" 属性
    属性 "url_id" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3811:28 - error: "int | None" 类型不匹配返回类型 "int"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportReturnType)
  d:\Python\fcmrawler\src\models\database.py:3817:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3817:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3817:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3842:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3842:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3842:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3869:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3869:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:3869:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:3914:49 - error: 无法访问 "Config" 类的 "config_data" 属性
    属性 "config_data" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3922:29 - error: 无法访问 "Config" 类的 "name" 属性
    属性 "name" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3922:55 - error: 无法访问 "Config" 类的 "is_default" 属性
    属性 "is_default" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3926:27 - error: 无法访问 "Config" 类的 "is_default" 属性
    属性 "is_default" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:3927:77 - error: 无法访问 "Config" 类的 "url_id" 属性
    属性 "url_id" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\models\database.py:4019:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:4019:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\database.py:4042:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:4042:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\database.py:4071:53 - warning: "entity_class" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:4079:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:4080:14 - warning: 由于这个类未使用 `@final` 装饰，其 `entity_class` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:4081:14 - warning: 由于这个类未使用 `@final` 装饰，其 `table_name` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:4082:14 - warning: 由于这个类未使用 `@final` 装饰，其 `filters` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\database.py:4084:31 - warning: "entity_class" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:4101:23 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:4109:34 - warning: "_get_connection" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\models\database.py:4136:19 - warning: "entity_id" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:4139:34 - warning: "_get_connection" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\models\database.py:4148:36 - warning: "expr" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\models\database.py:4158:34 - warning: "row" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\models\entities.py
  d:\Python\fcmrawler\src\models\entities.py: error: 导入链中检测到循环导入
    d:\Python\fcmrawler\src\models\entities.py
    d:\Python\fcmrawler\src\services\field_validator.py (reportImportCycles)
  d:\Python\fcmrawler\src\models\entities.py:22:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:22:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:22:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:22:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:70:9 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:74:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:74:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:91:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:91:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:126:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:126:53 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:154:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:154:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:230:13 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:231:11 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:234:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:292:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:308:16 - warning: "UrlCategory" 一定是 "UrlCategory" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\entities.py:346:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:347:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:348:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:349:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:355:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:356:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:357:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:359:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:373:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:389:16 - warning: "CrawlStatus" 一定是 "CrawlStatus" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\models\entities.py:409:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:409:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:465:27 - warning: "reason" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\models\entities.py:465:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:530:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:531:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:532:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:535:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:537:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:540:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:541:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:543:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:544:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:546:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:547:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:558:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:567:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:573:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:573:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:583:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:583:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:588:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:648:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:689:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:689:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:699:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:699:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:709:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:709:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:709:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:719:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:719:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:719:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:741:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:742:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:743:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:744:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:744:21 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:745:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:745:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:751:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:751:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:774:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:775:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:776:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:776:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:776:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:798:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:798:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:812:28 - warning: "encryption_key" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\models\entities.py:812:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:855:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:856:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:866:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:869:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:885:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:885:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:894:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:894:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:899:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:908:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:942:30 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:942:66 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:942:105 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:969:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:996:16 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:997:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1000:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1001:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1005:12 - warning: 条件的计算结果始终为 `True`，因为类型 "int" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\models\entities.py:1007:12 - warning: 条件的计算结果始终为 `True`，因为类型 "int" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\models\entities.py:1009:12 - warning: 条件的计算结果始终为 `True`，因为类型 "int" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\models\entities.py:1048:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1075:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1076:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1090:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1090:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:1099:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1099:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:1134:16 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1135:16 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1137:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1140:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1143:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1144:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1148:12 - warning: 条件的计算结果始终为 `True`，因为类型 "int" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\models\entities.py:1162:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1162:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:1172:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1172:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\entities.py:1199:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1202:30 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1222:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1224:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1225:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1228:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1232:12 - warning: 条件的计算结果始终为 `True`，因为类型 "int" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\models\entities.py:1234:12 - warning: 条件的计算结果始终为 `True`，因为类型 "int" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\models\entities.py:1252:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1268:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1291:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1292:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1293:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1321:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\entities.py:1347:72 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\models\field_change_detection_migration.py
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:21:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:39:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIGRATION_VERSION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:40:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIGRATION_DESCRIPTION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:49:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:348:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:348:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:398:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\field_change_detection_migration.py:398:39 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\models\field_schema_migration.py
  d:\Python\fcmrawler\src\models\field_schema_migration.py:21:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\field_schema_migration.py:39:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIGRATION_VERSION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\field_schema_migration.py:40:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIGRATION_DESCRIPTION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\field_schema_migration.py:49:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\field_schema_migration.py:491:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\models\url.py
  d:\Python\fcmrawler\src\models\url.py:10:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:10:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:20:9 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:23:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:24:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:26:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:27:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:70:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:94:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url.py:94:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\models\url.py:112:9 - warning: "__str__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\models\url.py:117:9 - warning: "__repr__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
d:\Python\fcmrawler\src\models\url_config_migration.py
  d:\Python\fcmrawler\src\models\url_config_migration.py:16:22 - warning: "datetime" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\models\url_config_migration.py:16:32 - warning: "timezone" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\models\url_config_migration.py:20:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\models\url_config_migration.py:20:20 - warning: "Optional" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\models\url_config_migration.py:41:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIGRATION_VERSION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\url_config_migration.py:42:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIGRATION_DESCRIPTION` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\url_config_migration.py:51:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\models\url_config_migration.py:181:38 - warning: "conn" 未使用 (reportUnusedParameter)
d:\Python\fcmrawler\src\services\__init__.py
  d:\Python\fcmrawler\src\services\__init__.py: error: 导入链中检测到循环导入
    d:\Python\fcmrawler\src\services\__init__.py
    d:\Python\fcmrawler\src\services\cms_detector.py (reportImportCycles)
  d:\Python\fcmrawler\src\services\__init__.py: error: 导入链中检测到循环导入
    d:\Python\fcmrawler\src\services\__init__.py
    d:\Python\fcmrawler\src\services\config_generator.py
    d:\Python\fcmrawler\src\services\cms_detector.py (reportImportCycles)
  d:\Python\fcmrawler\src\services\__init__.py:26:21 - warning: "CrawlService" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\Python\fcmrawler\src\services\__init__.py:26:37 - warning: "TaskStatus" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\Python\fcmrawler\src\services\__init__.py:26:51 - warning: "TaskPriority" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\Python\fcmrawler\src\services\ai_analysis_service.py
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:17:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:17:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:42:29 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:42:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:43:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:43:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:44:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:58:14 - warning: 由于这个类未使用 `@final` 装饰，其 `kimi_client` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:59:14 - warning: 由于这个类未使用 `@final` 装饰，其 `page_analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:60:14 - warning: 由于这个类未使用 `@final` 装饰，其 `selector_generator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:61:14 - warning: 由于这个类未使用 `@final` 装饰，其 `report_generator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:64:14 - warning: 由于这个类未使用 `@final` 装饰，其 `enable_cache` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:66:18 - warning: 由于这个类未使用 `@final` 装饰，其 `cache_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:73:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_playwright` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:74:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_playwright_browser` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:75:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_playwright_context` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:78:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_is_analyzing` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:79:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_analysis_cancelled` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:86:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:89:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:89:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:304:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:304:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:322:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:322:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:322:83 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:322:93 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:359:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:359:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:359:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:359:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:388:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:388:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:388:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:388:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:412:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:412:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:412:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:412:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:413:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:413:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:438:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:438:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:438:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:438:91 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:470:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:470:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:470:76 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:470:86 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:506:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:506:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:506:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:524:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:541:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_analysis_service.py:541:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\ai_config_generator_service.py
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:20:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:20:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:20:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:72:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:72:23 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:72:33 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:79:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:79:28 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:83:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:84:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:84:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:97:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:98:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:99:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:100:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:101:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:102:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:116:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:117:14 - warning: 由于这个类未使用 `@final` 装饰，其 `website_analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:118:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:119:14 - warning: 由于这个类未使用 `@final` 装饰，其 `quality_assessor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:120:14 - warning: 由于这个类未使用 `@final` 装饰，其 `rate_limiter` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:121:14 - warning: 由于这个类未使用 `@final` 装饰，其 `analysis_cache` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:123:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:124:14 - warning: "_progress_callback" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:124:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:125:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_cancelled` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:126:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:145:75 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:145:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:145:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:191:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:191:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:191:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:192:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:192:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:192:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:291:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:291:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:291:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:292:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:292:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:292:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:293:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:293:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:385:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:385:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:406:51 - warning: "_build_analysis_prompt" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:407:25 - warning: "_build_analysis_prompt" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:415:25 - warning: "_build_analysis_prompt" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:425:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:425:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:522:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:522:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:537:20 - warning: "Dict[str, Dict[str, Any]]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:581:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:581:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:616:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\ai_config_generator_service.py:616:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\api_test_service.py
  d:\Python\fcmrawler\src\services\api_test_service.py:25:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:25:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:25:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:25:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:64:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:65:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:66:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:67:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:68:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:69:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:70:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:72:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:72:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\api_test_service.py:74:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:74:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\api_test_service.py:79:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:79:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\api_test_service.py:117:24 - warning: "config_service" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\api_test_service.py:124:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\api_test_service.py:125:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:126:14 - warning: 由于这个类未使用 `@final` 装饰，其 `session_timeout` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\api_test_service.py:129:14 - warning: 由于这个类未使用 `@final` 装饰，其 `test_endpoints` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\api_test_service.py:140:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:140:60 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:140:91 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:190:26 - error: "str | APIProvider" 类型的实参无法赋值给函数 "__init__" 中 "APIProvider" 类型的形参 "provider"
    "str | APIProvider" 类型与 "APIProvider" 类型不兼容
      "str" 与 "APIProvider" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\api_test_service.py:204:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:204:76 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:262:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:263:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:263:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\api_test_service.py:339:17 - error: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:339:17 - error: "int" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:339:17 - error: "float" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:339:17 - error: 不能取 `None` 类型对象的下标 (reportOptionalSubscript)
  d:\Python\fcmrawler\src\services\api_test_service.py:340:63 - error: 无法访问 "str" 类的 "get" 属性
    属性 "get" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:340:63 - error: 无法访问 "int" 类的 "get" 属性
    属性 "get" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:340:63 - error: 无法访问 "float" 类的 "get" 属性
    属性 "get" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:340:63 - error: `None` 没有 "get" 属性 (reportOptionalMemberAccess)
  d:\Python\fcmrawler\src\services\api_test_service.py:353:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:372:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:372:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:372:74 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:373:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:404:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:404:77 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:404:87 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\api_test_service.py:446:42 - error: 无法访问 "str" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\api_test_service.py:477:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:478:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:505:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:517:93 - error: "CIMultiDictProxy[str]" 类型的实参无法赋值给函数 "_parse_rate_limit_headers" 中 "Dict[str, str]" 类型的形参 "headers"
    "CIMultiDictProxy[str]" 与 "Dict[str, str]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\api_test_service.py:591:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:591:75 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:591:90 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:617:49 - warning: "response_text" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\api_test_service.py:618:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\api_test_service.py:638:80 - warning: "provider" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\api_test_service.py:649:16 - error: "None" 类型不匹配返回类型 "bool"
    "None" 与 "bool" 不兼容 (reportReturnType)
  d:\Python\fcmrawler\src\services\api_test_service.py:656:26 - warning: "config_service" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\services\async_config_bridge.py
  d:\Python\fcmrawler\src\services\async_config_bridge.py:23:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:23:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:40:40 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:47:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:48:14 - warning: 由于这个类未使用 `@final` 装饰，其 `api_test_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:52:45 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:52:76 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:53:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:53:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:85:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:85:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:85:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:85:91 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:115:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:115:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:193:40 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:200:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:201:14 - warning: 由于这个类未使用 `@final` 装饰，其 `async_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:202:14 - warning: 由于这个类未使用 `@final` 装饰，其 `bridge` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:208:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:208:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:208:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:209:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:210:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:211:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:212:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:231:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:231:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:254:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:254:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:254:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:255:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:256:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:257:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:274:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:274:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:296:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:296:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:296:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:297:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:298:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:315:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:315:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:351:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\async_config_bridge.py:354:45 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\audit_service.py
  d:\Python\fcmrawler\src\services\audit_service.py:28:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:28:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:28:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:28:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:66:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:67:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:70:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:71:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:81:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:82:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:85:16 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:86:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:87:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:88:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:98:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:99:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:101:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:104:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:105:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:106:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:116:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:117:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:120:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:121:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:123:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:124:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:134:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:135:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:139:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:140:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:140:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:140:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:141:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:142:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:152:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:153:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:157:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:158:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:159:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:160:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:178:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:178:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:188:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\audit_service.py:191:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\audit_service.py:192:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\audit_service.py:409:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:409:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:414:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:414:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:463:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:464:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:465:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:466:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:504:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:505:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:506:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:507:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:552:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:553:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:554:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:555:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:596:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:597:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:599:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:644:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:645:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:645:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:645:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:646:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:685:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:686:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:720:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:721:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:722:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:723:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:725:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:725:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:725:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:804:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:804:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:826:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:826:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:861:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:861:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:873:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\audit_service.py:873:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\audit_service.py:999:22 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:999:30 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1004:25 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1004:33 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1009:22 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1009:30 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1014:22 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1014:30 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1019:29 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1019:37 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1024:27 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\audit_service.py:1024:35 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\services\backup_service.py
  d:\Python\fcmrawler\src\services\backup_service.py:28:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:28:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:28:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:28:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:40:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:41:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:41:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:41:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\backup_service.py:42:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:43:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:44:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:44:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\backup_service.py:45:23 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:74:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:76:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:76:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\backup_service.py:81:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:81:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\backup_service.py:100:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:100:45 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:112:14 - warning: 由于这个类未使用 `@final` 装饰，其 `backup_dir` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\backup_service.py:122:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_db` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\backup_service.py:123:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_config_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\backup_service.py:133:18 - warning: "value" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\backup_service.py:143:30 - warning: "value" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\backup_service.py:325:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:380:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:419:50 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:458:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:509:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:574:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:792:77 - warning: "backup_path" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\backup_service.py:863:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:1088:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:1098:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:1116:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:1158:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:1158:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\backup_service.py:1207:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\backup_service.py:1207:45 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
d:\Python\fcmrawler\src\services\batch_analysis_service.py
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:15:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:15:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:15:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:29:9 - warning: "progress_callback" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:32:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:32:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:45:13 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:45:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:45:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:46:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:47:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:48:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:56:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:57:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:106:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:106:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:132:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:136:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:140:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:144:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:148:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:148:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:175:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:179:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:200:14 - warning: 由于这个类未使用 `@final` 装饰，其 `total_urls` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:201:14 - warning: 由于这个类未使用 `@final` 装饰，其 `completed_urls` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:202:14 - warning: 由于这个类未使用 `@final` 装饰，其 `failed_urls` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:203:14 - warning: "start_time" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:203:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:204:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:205:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:213:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:234:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:234:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:274:64 - error: 类型表达式中不允许使用变量 (reportInvalidTypeForm)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:282:14 - warning: 由于这个类未使用 `@final` 装饰，其 `ai_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:283:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_concurrent` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:284:14 - warning: 由于这个类未使用 `@final` 装饰，其 `semaphore` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:285:14 - warning: 由于这个类未使用 `@final` 装饰，其 `queue` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:286:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:289:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_pause_event` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:291:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_is_cancelled` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:316:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:316:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:317:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:317:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:317:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:350:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:350:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:350:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:367:21 - error: "Unknown | BaseException" 类型的实参无法赋值给函数 "__setitem__" 中 "Dict[str, Any]" 类型的形参 "value"
    "Unknown | BaseException" 类型与 "Dict[str, Any]" 类型不兼容
      "BaseException" 与 "Dict[str, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:383:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:384:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:384:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:450:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:450:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:454:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:454:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:473:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_analysis_service.py:473:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\batch_crawl_service.py
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:23:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:23:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:23:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:23:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:28:33 - warning: "Url" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:44:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:64:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:65:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:70:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:91:87 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:157:9 - warning: "db_session" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:158:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:159:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:170:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:171:14 - warning: 由于这个类未使用 `@final` 装饰，其 `crawl_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:172:14 - warning: 由于这个类未使用 `@final` 装饰，其 `rate_limiter` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:175:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:176:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:176:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:176:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:177:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:177:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:178:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:181:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_pause_event` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:183:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_stop_event` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:186:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_statistics` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:189:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:189:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:189:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:192:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_memory_threshold` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:193:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_cleanup_counter` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:194:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_last_cleanup_time` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:196:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:200:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:201:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:203:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:203:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:203:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:265:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:265:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:293:28 - error: "int | Unknown | None" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "session_id"
    "int | Unknown | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:304:40 - warning: "url_ids" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:304:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:304:60 - warning: "config_ids" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:304:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:304:108 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:304:114 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:311:49 - error: "int | None" 类型的实参无法赋值给函数 "query_batch_crawl_tasks" 中 "int" 类型的形参 "session_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:323:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:323:75 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:359:21 - warning: 变量 "priority" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:421:20 - warning: 条件的计算结果始终为 `False`，因为类型 "BatchCrawlSession" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:435:40 - error: "int | None" 类型的实参无法赋值给函数 "complete_task" 中 "int" 类型的形参 "result_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:514:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:514:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:529:13 - warning: 变量 "i" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:572:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:572:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:624:16 - warning: 条件的计算结果始终为 `False`，因为类型 "BatchCrawlSession" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:701:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:701:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:783:31 - warning: "exc_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:783:41 - warning: "exc_val" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\batch_crawl_service.py:783:50 - warning: "exc_tb" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\services\cache_manager.py
  d:\Python\fcmrawler\src\services\cache_manager.py:17:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:17:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:17:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:17:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:25:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cache_manager.py:25:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:26:14 - warning: 由于这个类未使用 `@final` 装饰，其 `value` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:27:14 - warning: 由于这个类未使用 `@final` 装饰，其 `created_at` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:28:14 - warning: 由于这个类未使用 `@final` 装饰，其 `expires_at` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:29:14 - warning: 由于这个类未使用 `@final` 装饰，其 `access_count` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:30:14 - warning: 由于这个类未使用 `@final` 装饰，其 `last_accessed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:56:59 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:64:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_size` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:65:14 - warning: 由于这个类未使用 `@final` 装饰，其 `default_ttl` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:66:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:67:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:68:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_stats` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:72:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cache_manager.py:72:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:102:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:102:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cache_manager.py:221:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:221:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cache_manager.py:271:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:283:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:283:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:283:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cache_manager.py:295:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:311:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:311:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:344:23 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:345:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cache_manager.py:347:71 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:363:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:393:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:393:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cache_manager.py:393:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\change_detector.py
  d:\Python\fcmrawler\src\services\change_detector.py:23:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:23:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:23:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:45:24 - warning: "db_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\change_detector.py:52:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\change_detector.py:53:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\change_detector.py:57:14 - warning: 由于这个类未使用 `@final` 装饰，其 `version_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\change_detector.py:63:18 - warning: 由于这个类未使用 `@final` 装饰，其 `diff_analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\change_detector.py:78:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:78:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:78:83 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:78:93 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:108:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:108:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:132:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:132:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:160:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:160:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:160:88 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:186:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:186:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:222:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:222:39 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:222:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:222:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:223:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:223:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:235:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:235:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:279:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:279:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:280:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:280:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:292:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:292:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:336:35 - warning: "field" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\change_detector.py:336:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:374:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:374:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:374:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:374:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:385:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:385:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:420:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:421:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:424:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:473:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:473:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:473:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:473:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:473:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:474:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:515:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:515:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:515:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:557:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:557:75 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:567:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:567:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:568:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:568:19 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:568:29 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:592:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:593:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:594:9 - warning: "field_type" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\change_detector.py:596:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:596:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:596:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:653:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:712:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:713:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:736:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:736:88 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:736:98 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:768:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:768:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\change_detector.py:789:70 - warning: 类型注释已弃用；请改用类型注解 (reportTypeCommentUsage)
  d:\Python\fcmrawler\src\services\change_detector.py:789:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:795:70 - warning: 类型注释已弃用；请改用类型注解 (reportTypeCommentUsage)
  d:\Python\fcmrawler\src\services\change_detector.py:795:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:812:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:812:85 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\change_detector.py:878:21 - error: "json" 可能未绑定 (reportPossiblyUnboundVariable)
d:\Python\fcmrawler\src\services\cms_detector.py
  d:\Python\fcmrawler\src\services\cms_detector.py:11:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:11:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:11:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:21:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:22:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:23:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:24:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:24:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cms_detector.py:33:14 - warning: 由于这个类未使用 `@final` 装饰，其 `cms_signatures` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\cms_detector.py:35:50 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:98:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:98:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\cms_detector.py:98:87 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:145:35 - error: "html_match_score" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\Python\fcmrawler\src\services\cms_detector.py:165:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:337:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:346:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:361:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\cms_detector.py:374:38 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\cms_detector.py:377:16 - warning: "List[str]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\cms_detector.py:380:16 - warning: "List[str]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\cms_detector.py:383:16 - warning: "Dict[str, str]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\cms_detector.py:386:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\cms_detector.py:389:16 - warning: "float | int" 一定是 "int | float" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\cms_detector.py:408:68 - error: `None` 不支持 "<" 运算符 (reportOptionalOperand)
  d:\Python\fcmrawler\src\services\cms_detector.py:408:84 - error: `None` 不支持 ">" 运算符 (reportOptionalOperand)
  d:\Python\fcmrawler\src\services\cms_detector.py:413:76 - error: `None` 不支持 "<" 运算符 (reportOptionalOperand)
  d:\Python\fcmrawler\src\services\cms_detector.py:413:95 - error: `None` 不支持 ">" 运算符 (reportOptionalOperand)
  d:\Python\fcmrawler\src\services\cms_detector.py:431:40 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\config_generator.py
  d:\Python\fcmrawler\src\services\config_generator.py:11:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:11:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:11:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:31:24 - warning: "db_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\config_generator.py:31:50 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:39:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_generator.py:40:14 - warning: 由于这个类未使用 `@final` 装饰，其 `cms_detector` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_generator.py:41:14 - warning: 由于这个类未使用 `@final` 装饰，其 `domain_analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_generator.py:42:14 - warning: 由于这个类未使用 `@final` 装饰，其 `quality_assessor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_generator.py:43:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_generator.py:47:66 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:139:37 - warning: "cms_signature" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\config_generator.py:139:52 - warning: "url_entity" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\config_generator.py:139:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:139:77 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:166:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:166:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:166:66 - warning: "cms_signature" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\config_generator.py:166:81 - warning: "url_entity" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\config_generator.py:219:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:234:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:234:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:235:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:317:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:386:73 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:386:98 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:386:108 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:457:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:457:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:457:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:457:75 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:458:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:458:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:458:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:537:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_generator.py:537:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_generator.py:565:26 - warning: "db_manager" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\services\config_quality_assessor.py
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:10:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:10:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:24:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:25:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:34:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:119:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:119:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:174:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:174:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:264:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:264:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:264:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:331:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:331:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:331:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:405:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:405:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:451:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:451:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:451:90 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:491:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_quality_assessor.py:491:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
d:\Python\fcmrawler\src\services\config_service.py
  d:\Python\fcmrawler\src\services\config_service.py:22:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:22:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:22:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:22:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:78:40 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:78:73 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:78:82 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:86:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_service.py:88:14 - warning: 由于这个类未使用 `@final` 装饰，其 `encryption_key` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_service.py:89:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:89:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:90:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:120:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:120:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:163:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:235:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:235:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:257:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:268:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:296:78 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:296:87 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:296:97 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:327:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:368:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:368:93 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:368:103 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:464:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:505:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:561:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:561:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:571:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:572:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_service.py:609:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:609:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:632:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:649:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:649:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:674:22 - warning: 变量 "value" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\config_service.py:699:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:727:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:727:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:754:20 - warning: "int" 一定是 "int" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:757:20 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:760:20 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:761:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_service.py:769:17 - warning: 变量 "json_data" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\config_service.py:795:18 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:796:10 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_service.py:819:20 - warning: "int" 一定是 "int" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:822:20 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_service.py:849:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:849:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_service.py:849:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
d:\Python\fcmrawler\src\services\config_test_service.py
  d:\Python\fcmrawler\src\services\config_test_service.py:19:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:19:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:19:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:54:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:55:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:64:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:65:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:77:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:78:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:80:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:96:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MAX_CONCURRENT_TESTS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_test_service.py:100:14 - warning: 由于这个类未使用 `@final` 装饰，其 `profiler` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_test_service.py:101:14 - warning: 由于这个类未使用 `@final` 装饰，其 `optimizer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_test_service.py:102:14 - warning: 由于这个类未使用 `@final` 装饰，其 `url_validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_test_service.py:103:14 - warning: 由于这个类未使用 `@final` 装饰，其 `analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_test_service.py:106:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_semaphore` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_test_service.py:132:71 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:145:59 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:221:101 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:281:102 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:314:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:314:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_test_service.py:327:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:327:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_test_service.py:467:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:467:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:467:39 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_test_service.py:467:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:468:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_test_service.py:485:39 - warning: "config" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\config_test_service.py:485:47 - warning: "url" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\services\config_validator.py
  d:\Python\fcmrawler\src\services\config_validator.py:14:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:14:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:14:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:14:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:32:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIN_TIMEOUT` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_validator.py:33:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MAX_TIMEOUT` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_validator.py:34:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MIN_RETRIES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_validator.py:35:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MAX_RETRIES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_validator.py:38:5 - warning: 由于这个类未使用 `@final` 装饰，其 `CSS_SELECTOR_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_validator.py:39:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DANGEROUS_PATTERNS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\config_validator.py:50:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:50:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:76:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:76:69 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:102:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:102:62 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:115:16 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:116:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:158:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:158:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:170:16 - warning: "Dict[str, str]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:171:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:187:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:187:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:199:16 - warning: "Dict[str, str]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:200:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:203:20 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:203:56 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:227:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:227:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:227:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:239:16 - warning: "Dict[str, int | float]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:240:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:269:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:269:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:269:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:281:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:282:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:312:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:312:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:312:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:324:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:325:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:366:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:366:58 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:379:16 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:380:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:396:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:396:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:396:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:408:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:409:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:469:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:479:16 - warning: "str | Path" 一定是 "str | Path" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:480:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:511:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:521:16 - warning: "str | Path" 一定是 "str | Path" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:522:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:530:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:530:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:530:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:530:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:540:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:541:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:547:20 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:548:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:563:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:563:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:576:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:576:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:586:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\config_validator.py:587:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\config_validator.py:628:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:628:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:628:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:628:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:675:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:675:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\config_validator.py:675:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\config_validator.py:675:93 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\services\content_deduplication_service.py
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:21:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:21:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:21:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:21:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:37:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:37:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:50:14 - warning: 由于这个类未使用 `@final` 装饰，其 `database_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:125:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:125:76 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:159:39 - warning: 变量 "last_seen" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:212:76 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:280:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:280:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:364:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:364:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_deduplication_service.py:364:75 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\content_search_service.py
  d:\Python\fcmrawler\src\services\content_search_service.py:31:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:31:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:31:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:31:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:31:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:54:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DOMAIN_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:57:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DANGEROUS_PATTERNS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:186:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DANGEROUS_COMPONENTS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:209:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:209:62 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:258:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:259:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:260:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:261:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:262:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:302:16 - warning: "SearchType" 一定是 "SearchType" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\content_search_service.py:305:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:305:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:310:12 - warning: "SearchType" 一定是 "SearchType" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\content_search_service.py:334:16 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:335:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:336:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:338:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:338:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:367:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:368:14 - warning: 由于这个类未使用 `@final` 装饰，其 `storage_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:369:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:370:14 - warning: 由于这个类未使用 `@final` 装饰，其 `path_validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\content_search_service.py:533:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:534:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:574:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:633:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:723:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:809:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:909:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:909:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:909:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:960:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:960:82 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:983:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1010:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1038:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1038:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1046:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1046:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1068:38 - warning: 变量 "metadata_path" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\content_search_service.py:1068:53 - warning: 变量 "extracted_path" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\content_search_service.py:1107:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1107:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1115:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1115:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1139:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1139:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1155:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1155:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1180:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1180:83 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1180:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1264:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1264:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1264:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1265:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1265:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1265:21 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1307:36 - warning: "_get_connection" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\content_search_service.py:1309:30 - warning: "conn" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\content_search_service.py:1322:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1322:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1342:17 - warning: 变量 "publish_date" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\content_search_service.py:1446:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1507:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1507:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\content_search_service.py:1521:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\content_search_service.py:1521:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\services\crawl_execution_service.py
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:23:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:23:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:23:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:63:24 - warning: "db_session" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:63:41 - warning: "storage_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:63:63 - warning: "change_detector" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:73:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:74:14 - warning: 由于这个类未使用 `@final` 装饰，其 `storage` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:75:14 - warning: 由于这个类未使用 `@final` 装饰，其 `detector` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:78:14 - warning: 由于这个类未使用 `@final` 装饰，其 `extractor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:79:14 - warning: 由于这个类未使用 `@final` 装饰，其 `analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:101:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:101:85 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:137:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:137:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:150:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:151:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:205:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:316:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:316:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:316:80 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:316:90 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:316:100 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:371:90 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:371:100 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:444:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:444:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:444:89 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:444:99 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:471:25 - warning: 变量 "link" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:489:29 - warning: "config_id" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:489:45 - warning: "field_name" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:502:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:502:89 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:571:23 - error: "str | Unknown | int | Dict[str, Any] | Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str | None" 类型的形参 "title"
    "str | Unknown | int | Dict[str, Any] | Any | None" 类型与 "str | None" 类型不兼容
      "int" 类型与 "str | None" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "None" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:579:30 - error: "str | Unknown | int | Dict[str, Any]" 类型的实参无法赋值给函数 "__init__" 中 "str | None" 类型的形参 "content_hash"
    "str | Unknown | int | Dict[str, Any]" 类型与 "str | None" 类型不兼容
      "int" 类型与 "str | None" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "None" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:593:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:593:101 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:666:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_execution_service.py:666:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\crawl_service.py
  d:\Python\fcmrawler\src\services\crawl_service.py:21:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:21:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:21:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:21:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:59:14 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:59:24 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:61:19 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:62:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:62:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:64:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:65:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:68:13 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:68:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:68:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:68:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:68:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:68:54 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:69:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:70:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:93:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:94:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:94:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:95:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:96:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_max_concurrent_tasks` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:97:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_current_concurrent_tasks` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:98:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:99:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_service_active` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:100:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_task_semaphore` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:101:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:102:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_workers_started` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:105:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:106:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_extractor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:107:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_reporter` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\crawl_service.py:133:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:133:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:176:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:176:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:176:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:231:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:231:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:231:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:231:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:231:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:231:90 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:246:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:246:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:246:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:290:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:290:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:324:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:324:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:390:24 - warning: 条件的计算结果始终为 `True`，因为类型 "PriorityQueue[Tuple[int, str]]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\Python\fcmrawler\src\services\crawl_service.py:517:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:517:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:536:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:536:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:536:80 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:555:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:555:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:674:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:674:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:674:76 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:674:86 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:697:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:697:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\crawl_service.py:697:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\crawl_service.py:697:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\custom_report_generator.py
  d:\Python\fcmrawler\src\services\custom_report_generator.py:20:25 - warning: "TYPE_CHECKING" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:20:40 - warning: "cast" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:44:12 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:49:12 - error: 无法解析导入 "weasyprint" (reportMissingImports)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:55:12 - warning: "openpyxl" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:86:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:116:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:137:14 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:139:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:141:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:151:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:168:21 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:174:22 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:176:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:195:21 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:198:22 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:200:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:215:48 - error: "list[str]" 类型的实参无法赋值给函数 "__init__" 中 "Axes | None" 类型的形参 "columns"
    "list[str]" 类型与 "Axes | None" 类型不兼容
      "list[str]" 与 "ExtensionArray" 不兼容
      "list[str]" 与 "ndarray[_AnyShape, dtype[Any]]" 不兼容
      "list[str]" 与 "Index" 不兼容
      "list[str]" 与 "Series" 不兼容
      "list[str]" 与 Protocol 类 "SequenceNotStr[Unknown]" 不兼容
        "index" 类型不兼容
          "(value: str, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize, /) -> int" 类型与 "(value: Any, /, start: int = 0, stop: int = ...) -> int" 类型不兼容
    ... (reportArgumentType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:227:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:229:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:247:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:280:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:281:14 - warning: 由于这个类未使用 `@final` 装饰，其 `query_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:282:14 - warning: 由于这个类未使用 `@final` 装饰，其 `time_series_analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:283:14 - warning: 由于这个类未使用 `@final` 装饰，其 `statistics_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:286:14 - warning: 由于这个类未使用 `@final` 装饰，其 `jinja_env` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:336:53 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:336:64 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:365:92 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:570:115 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:590:79 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:631:33 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:631:83 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:631:83 - warning: "kwargs" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:719:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:728:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:871:37 - error: "BytesIO" 类型的实参无法赋值给函数 "__new__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
    "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
      "BytesIO" 与 "str" 不兼容
      "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
        "__fspath__" 不存在
      "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
        "truncate" 类型不兼容
          "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
            缺少关键字参数 "size"
    ... (reportArgumentType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:871:37 - error: "BytesIO" 类型的实参无法赋值给函数 "__init__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
    "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
      "BytesIO" 与 "str" 不兼容
      "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
        "__fspath__" 不存在
      "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
        "truncate" 类型不兼容
          "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
            缺少关键字参数 "size" (reportArgumentType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:922:13 - warning: 变量 "fig" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:953:34 - warning: "ax" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:974:33 - warning: "ax" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:995:33 - warning: "ax" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:1003:13 - warning: 变量 "wedges" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:1003:21 - warning: 变量 "texts" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:1003:28 - warning: 变量 "autotexts" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:1015:13 - warning: 变量 "fig" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:1169:97 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\custom_report_generator.py:1189:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\data_export_service.py
  d:\Python\fcmrawler\src\services\data_export_service.py:28:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:28:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:28:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:28:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:28:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:67:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:68:11 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:68:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:68:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:68:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:69:14 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:69:24 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:72:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:73:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:74:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:76:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:77:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:80:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:80:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:120:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:123:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:145:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_concurrent_tasks` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:146:14 - warning: 由于这个类未使用 `@final` 装饰，其 `executor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:149:14 - warning: 由于这个类未使用 `@final` 装饰，其 `exporters` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:157:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:159:14 - warning: "completed_tasks" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\services\data_export_service.py:159:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:160:14 - warning: "export_history" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\services\data_export_service.py:160:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:163:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:163:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:166:14 - warning: 由于这个类未使用 `@final` 装饰，其 `is_running` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:167:14 - warning: 由于这个类未使用 `@final` 装饰，其 `service_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:170:14 - warning: 由于这个类未使用 `@final` 装饰，其 `total_exports` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:171:14 - warning: 由于这个类未使用 `@final` 装饰，其 `successful_exports` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:172:14 - warning: 由于这个类未使用 `@final` 装饰，其 `failed_exports` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_export_service.py:173:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:174:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:214:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:215:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:216:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:216:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:216:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:217:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:217:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:217:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:218:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:256:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:344:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:350:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:358:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:381:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:381:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:589:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:590:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:590:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:590:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:591:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:592:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:592:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:592:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:593:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:593:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:630:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:630:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:630:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:650:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:650:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:650:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_export_service.py:651:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:651:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_export_service.py:672:20 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\data_export_service.py:673:17 - warning: 代码不会被执行 (reportUnreachable)
d:\Python\fcmrawler\src\services\data_query_service.py
  d:\Python\fcmrawler\src\services\data_query_service.py:22:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:22:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:22:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:22:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:22:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:26:12 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\data_query_service.py:40:12 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:64:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:65:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:85:11 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:85:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:85:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:96:27 - warning: "index" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\data_query_service.py:99:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:99:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:99:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:99:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:102:20 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\data_query_service.py:121:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_size` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_query_service.py:122:14 - warning: 由于这个类未使用 `@final` 装饰，其 `ttl_seconds` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_query_service.py:123:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:123:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:123:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:124:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_query_service.py:126:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:126:54 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:131:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:131:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:135:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:135:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:135:53 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:153:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:153:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:153:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:153:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:153:73 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:170:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:170:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:209:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_query_service.py:210:14 - warning: 由于这个类未使用 `@final` 装饰，其 `cache` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_query_service.py:211:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_executor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_query_service.py:214:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:214:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:214:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:312:66 - warning: "prefix" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\data_query_service.py:312:87 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:312:98 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:312:103 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:471:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:471:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:471:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:507:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:507:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:507:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:507:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:511:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:511:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:511:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:511:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:520:59 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:530:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:530:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:534:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:534:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:553:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:553:77 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:594:84 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:622:24 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\data_query_service.py:648:24 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\data_query_service.py:657:37 - error: "BytesIO" 类型的实参无法赋值给函数 "__new__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
    "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
      "BytesIO" 与 "str" 不兼容
      "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
        "__fspath__" 不存在
      "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
        "truncate" 类型不兼容
          "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
            缺少关键字参数 "size"
    ... (reportArgumentType)
  d:\Python\fcmrawler\src\services\data_query_service.py:657:37 - error: "BytesIO" 类型的实参无法赋值给函数 "__init__" 中 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型的形参 "path"
    "BytesIO" 类型与 "FilePath | WriteExcelBuffer | ExcelWriter[Unknown]" 类型不兼容
      "BytesIO" 与 "str" 不兼容
      "BytesIO" 与 Protocol 类 "PathLike[str]" 不兼容
        "__fspath__" 不存在
      "BytesIO" 与 Protocol 类 "WriteExcelBuffer" 不兼容
        "truncate" 类型不兼容
          "(size: int | None = None, /) -> int" 类型与 "(size: int | None = ...) -> int" 类型不兼容
            缺少关键字参数 "size" (reportArgumentType)
  d:\Python\fcmrawler\src\services\data_query_service.py:673:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_query_service.py:678:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:678:62 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\data_query_service.py:688:29 - warning: "min_rate" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\data_query_service.py:688:52 - warning: "max_rate" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\data_query_service.py:698:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:698:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:710:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_query_service.py:710:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\services\data_statistics_service.py
  d:\Python\fcmrawler\src\services\data_statistics_service.py:17:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:17:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:17:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:17:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:33:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:35:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:36:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:36:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:36:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:37:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:37:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:37:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:39:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:39:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:63:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:65:29 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:65:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:153:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:160:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:160:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:160:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:163:23 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:196:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:271:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:297:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:477:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:499:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:499:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:558:45 - warning: "stat" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:558:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:558:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:628:44 - warning: "start_date" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:628:66 - warning: "end_date" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:813:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:813:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:813:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:813:75 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:900:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:900:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1027:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1027:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1119:20 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1188:88 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1188:98 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1217:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1217:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1286:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1286:91 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1286:101 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1303:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1303:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1303:96 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1310:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1343:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1343:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1343:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1350:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1381:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1381:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1381:45 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\data_statistics_service.py:1388:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
d:\Python\fcmrawler\src\services\domain_analyzer.py
  d:\Python\fcmrawler\src\services\domain_analyzer.py:21:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\domain_analyzer.py:23:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\domain_analyzer.py:217:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\domain_analyzer.py:243:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\domain_analyzer.py:293:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\excel_import_service.py
  d:\Python\fcmrawler\src\services\excel_import_service.py:15:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:15:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:15:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:18:8 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\excel_import_service.py:28:14 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:29:11 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:29:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:29:26 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:41:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:42:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:73:5 - warning: 由于这个类未使用 `@final` 装饰，其 `URL_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:78:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MAX_FILE_SIZE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:79:5 - warning: 由于这个类未使用 `@final` 装饰，其 `CHUNK_SIZE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:82:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MALICIOUS_PATTERNS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:126:5 - warning: 由于这个类未使用 `@final` 装饰，其 `MALICIOUS_REGEX` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:129:5 - warning: 由于这个类未使用 `@final` 装饰，其 `SQL_INJECTION_PATTERNS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:146:5 - warning: 由于这个类未使用 `@final` 装饰，其 `SQL_INJECTION_REGEX` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:149:5 - warning: 由于这个类未使用 `@final` 装饰，其 `ALLOWED_EXTENSIONS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:152:5 - warning: 由于这个类未使用 `@final` 装饰，其 `BLOCKED_EXTENSIONS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:173:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:175:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:176:14 - warning: 由于这个类未使用 `@final` 装饰，其 `audit_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\excel_import_service.py:297:17 - warning: 变量 "sheet_name" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\excel_import_service.py:324:17 - warning: 变量 "df" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\excel_import_service.py:334:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:334:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:461:16 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\excel_import_service.py:462:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\excel_import_service.py:560:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:560:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:669:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:669:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:697:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:697:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:709:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:709:49 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:760:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:760:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:760:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:760:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:796:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:796:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:796:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:833:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:833:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:833:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:833:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:833:85 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:890:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:890:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\excel_import_service.py:890:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:890:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:890:94 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:939:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1009:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1009:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1022:31 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1045:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1045:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1150:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\excel_import_service.py:1150:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\field_management_service.py
  d:\Python\fcmrawler\src\services\field_management_service.py:20:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:20:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:20:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:20:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:41:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:48:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_management_service.py:49:14 - warning: 由于这个类未使用 `@final` 装饰，其 `field_validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_management_service.py:50:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_management_service.py:61:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:62:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:64:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:65:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:65:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:65:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:66:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:68:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:126:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:161:45 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\field_management_service.py:161:56 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:221:67 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:221:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:274:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:303:53 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:334:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:373:55 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\field_management_service.py:373:66 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:482:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:519:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:519:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:551:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:582:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:582:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:622:101 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:673:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:673:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:691:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:691:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:735:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:735:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:737:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:772:53 - error: "int | None" 类型的实参无法赋值给函数 "_import_fields_with_merge_strategy" 中 "int" 类型的形参 "field_list_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\field_management_service.py:785:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:862:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:902:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:904:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:949:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:965:74 - warning: "ValidatorValidationResult" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\services\field_management_service.py:982:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:982:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:982:82 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:1040:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:1040:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:1052:20 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\field_management_service.py:1053:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\field_management_service.py:1089:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:1089:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:1101:20 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\field_management_service.py:1102:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\field_management_service.py:1139:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:1139:69 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_management_service.py:1139:79 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_management_service.py:1179:25 - error: "int | None" 类型的实参无法赋值给函数 "update_field" 中 "int" 类型的形参 "field_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\field_management_service.py:1419:29 - warning: "row" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\field_management_service.py:1446:34 - warning: "row" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\field_management_service.py:1458:38 - warning: "row" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\services\field_template_manager.py
  d:\Python\fcmrawler\src\services\field_template_manager.py:18:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:18:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:18:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:41:24 - warning: "db_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\field_template_manager.py:48:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_template_manager.py:49:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_template_manager.py:53:79 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:53:88 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:53:93 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:53:103 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_template_manager.py:98:49 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:110:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:110:68 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:127:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:138:51 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\field_template_manager.py:209:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:209:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:209:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:209:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_template_manager.py:466:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:467:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:529:76 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:570:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:570:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_template_manager.py:581:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:581:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_template_manager.py:617:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:617:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:643:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:643:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_template_manager.py:671:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_template_manager.py:671:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_template_manager.py:685:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
d:\Python\fcmrawler\src\services\field_validator.py
  d:\Python\fcmrawler\src\services\field_validator.py:19:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:19:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:19:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:33:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:34:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:35:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:36:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:36:21 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:37:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:37:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:43:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:43:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:62:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:62:23 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:63:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:64:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:75:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DEFAULT_RULES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_validator.py:106:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\field_validator.py:108:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:149:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:357:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:391:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:391:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:421:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:421:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:421:81 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\field_validator.py:465:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\field_validator.py:465:80 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\kimi_client.py
  d:\Python\fcmrawler\src\services\kimi_client.py:16:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:16:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:16:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:49:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:49:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:49:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:50:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:50:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:50:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:51:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:52:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:53:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:53:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:53:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:67:14 - warning: 由于这个类未使用 `@final` 装饰，其 `api_key` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\kimi_client.py:68:14 - warning: 由于这个类未使用 `@final` 装饰，其 `base_url` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\kimi_client.py:69:23 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:70:14 - warning: 由于这个类未使用 `@final` 装饰，其 `model` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\kimi_client.py:71:14 - warning: 由于这个类未使用 `@final` 装饰，其 `temperature` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\kimi_client.py:72:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_tokens` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\kimi_client.py:73:14 - warning: 由于这个类未使用 `@final` 装饰，其 `timeout` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\kimi_client.py:82:31 - warning: "exc_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\kimi_client.py:82:41 - warning: "exc_val" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\kimi_client.py:82:50 - warning: "exc_tb" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\kimi_client.py:99:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:99:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:99:57 - warning: "max_retries" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\kimi_client.py:187:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:187:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:253:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:253:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:329:31 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\kimi_client.py:387:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:387:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:387:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:387:77 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:387:87 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:388:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:388:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:458:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:458:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\kimi_client.py:458:92 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:458:97 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\kimi_client.py:458:107 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\services\page_structure_analyzer.py
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:16:35 - warning: "cast" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:148:31 - warning: "soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:157:28 - warning: "soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:162:39 - warning: "soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:215:36 - warning: "element" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:253:40 - warning: "element" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:262:31 - warning: "element" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:285:41 - warning: "soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:320:36 - warning: "element" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:331:40 - error: "list[Any]" 类型的实参无法赋值给函数 "get" 中 "_AttributeValue | None" 类型的形参 "default"
    "list[Any]" 类型与 "_AttributeValue | None" 类型不兼容
      "list[Any]" 与 "str" 不兼容
      "list[Any]" 与 "AttributeValueList" 不兼容
      "list[Any]" 与 "None" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:344:43 - warning: "element" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:350:40 - error: "list[Any]" 类型的实参无法赋值给函数 "get" 中 "_AttributeValue | None" 类型的形参 "default"
    "list[Any]" 类型与 "_AttributeValue | None" 类型不兼容
      "list[Any]" 与 "str" 不兼容
      "list[Any]" 与 "AttributeValueList" 不兼容
      "list[Any]" 与 "None" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:362:38 - warning: "soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:381:39 - warning: "soup" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:390:44 - error: "list[Any]" 类型的实参无法赋值给函数 "get" 中 "_AttributeValue | None" 类型的形参 "default"
    "list[Any]" 类型与 "_AttributeValue | None" 类型不兼容
      "list[Any]" 与 "str" 不兼容
      "list[Any]" 与 "AttributeValueList" 不兼容
      "list[Any]" 与 "None" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:412:37 - warning: "html_content" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:430:24 - error: "Literal['tag']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['tag']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['tag']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['tag']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:431:28 - error: "Literal['classes']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['classes']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['classes']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['classes']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:432:26 - error: "Literal['xpath']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['xpath']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['xpath']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['xpath']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:434:32 - error: "Literal['text_length']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['text_length']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['text_length']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['text_length']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:435:32 - error: "Literal['child_count']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['child_count']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['child_count']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['child_count']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:436:26 - error: "Literal['depth']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['depth']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['depth']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['depth']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:445:42 - warning: "area_data" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:445:53 - warning: "structure" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:445:53 - warning: "structure" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:484:39 - warning: "html_content" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:498:64 - error: 无法访问 "list[dict[str, Unknown]]" 类的 "items" 属性
    属性 "items" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:498:64 - error: 无法访问 "list[Unknown]" 类的 "items" 属性
    属性 "items" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:501:45 - error: "int" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:505:25 - error: "Literal[0]" 类型的实参无法赋值给函数 "__getitem__" 中 "str" 类型的形参 "key"
    "Literal[0]" 与 "str" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:506:16 - error: "int" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:506:16 - error: "__getitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:506:16 - error: "Literal['classes']" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
    "Literal['classes']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:507:46 - error: "int" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:507:46 - error: "__getitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:507:46 - error: "Literal['classes']" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
    "Literal['classes']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:509:42 - error: "int" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:509:42 - error: "__getitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\Python\fcmrawler\src\services\page_structure_analyzer.py:509:42 - error: "Literal['tag']" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
    "Literal['tag']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
d:\Python\fcmrawler\src\services\persistence_service.py
  d:\Python\fcmrawler\src\services\persistence_service.py:26:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:26:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:26:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:26:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:63:19 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:64:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:65:14 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:65:24 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\persistence_service.py:69:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:69:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\persistence_service.py:74:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:74:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\persistence_service.py:95:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:102:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:102:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\persistence_service.py:107:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:107:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\persistence_service.py:137:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:137:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:147:14 - warning: 由于这个类未使用 `@final` 装饰，其 `data_dir` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:148:14 - warning: 由于这个类未使用 `@final` 装饰，其 `persistence_dir` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:151:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:152:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:153:14 - warning: 由于这个类未使用 `@final` 装饰，其 `backup_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:156:14 - warning: 由于这个类未使用 `@final` 装饰，其 `current_session_id` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:157:14 - warning: 由于这个类未使用 `@final` 装饰，其 `session_start_time` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\persistence_service.py:211:30 - warning: "_get_connection" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\persistence_service.py:251:30 - warning: "_get_connection" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\persistence_service.py:357:22 - warning: 变量 "value" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\persistence_service.py:504:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:538:58 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:538:83 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:585:29 - warning: "_recreate_database" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\persistence_service.py:600:29 - warning: "_create_database" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\services\persistence_service.py:670:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:771:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:771:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\persistence_service.py:829:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\persistence_service.py:829:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
d:\Python\fcmrawler\src\services\pii_detector.py
  d:\Python\fcmrawler\src\services\pii_detector.py:24:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:24:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:24:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "set" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:43:16 - warning: 此类型自 Python 3.9 起已弃用；请改用 "set" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:44:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:45:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:46:15 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:47:11 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:139:5 - warning: 由于这个类未使用 `@final` 装饰，其 `EMAIL_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\pii_detector.py:145:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PHONE_PATTERNS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\pii_detector.py:157:5 - warning: 由于这个类未使用 `@final` 装饰，其 `ID_CARD_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\pii_detector.py:160:5 - warning: 由于这个类未使用 `@final` 装饰，其 `SSN_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\pii_detector.py:164:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\pii_detector.py:166:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:190:16 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\pii_detector.py:191:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\pii_detector.py:225:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:238:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:272:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:291:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:304:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\pii_detector.py:317:38 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\rate_limiter.py
  d:\Python\fcmrawler\src\services\rate_limiter.py:19:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "collections.deque" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:19:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:19:38 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:30:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:36:81 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:45:14 - warning: 由于这个类未使用 `@final` 装饰，其 `config` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\rate_limiter.py:51:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "collections.deque" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:56:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\rate_limiter.py:195:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:195:39 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\rate_limiter.py:225:31 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\services\rate_limiter.py:266:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_default_config` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\rate_limiter.py:267:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_lock` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\rate_limiter.py:274:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:275:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:276:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:300:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:300:64 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:300:92 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:324:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:324:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\rate_limiter.py:324:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\rate_limiter.py:342:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\result_formatter.py
  d:\Python\fcmrawler\src\services\result_formatter.py:20:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:20:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:20:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:33:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DEFAULT_MAX_LENGTH` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\result_formatter.py:37:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\result_formatter.py:39:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:65:16 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\result_formatter.py:66:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\result_formatter.py:105:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:136:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:137:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:167:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:167:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:167:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\result_formatter.py:167:111 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:167:135 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\result_formatter.py:167:140 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
d:\Python\fcmrawler\src\services\selector_generator.py
  d:\Python\fcmrawler\src\services\selector_generator.py:18:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:18:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:18:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:30:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DYNAMIC_ID_PATTERN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_generator.py:33:5 - warning: 由于这个类未使用 `@final` 装饰，其 `SEMANTIC_TAGS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_generator.py:36:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DATE_PATTERNS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_generator.py:46:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:46:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_generator.py:46:75 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:46:105 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:46:115 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_generator.py:84:18 - warning: "BeautifulSoup" 一定是 "BeautifulSoup" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\selector_generator.py:87:17 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\selector_generator.py:117:90 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_generator.py:117:100 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_generator.py:200:96 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\services\selector_optimizer.py
  d:\Python\fcmrawler\src\services\selector_optimizer.py:14:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:14:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:36:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:42:9 - warning: "__str__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:56:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:75:14 - warning: 由于这个类未使用 `@final` 装饰，其 `slow_threshold` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:76:14 - warning: 由于这个类未使用 `@final` 装饰，其 `broad_threshold` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:83:67 - warning: "html_content" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:84:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:173:103 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:244:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:274:48 - warning: "selector" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:274:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:296:101 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:337:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:368:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:378:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:378:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:397:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_optimizer.py:416:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\services\selector_tester.py
  d:\Python\fcmrawler\src\services\selector_tester.py:16:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:16:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:16:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:32:23 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:33:12 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:37:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:37:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:37:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:37:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_tester.py:56:14 - warning: 由于这个类未使用 `@final` 装饰，其 `analyzer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_tester.py:57:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:58:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:59:14 - warning: 由于这个类未使用 `@final` 装饰，其 `cache_size` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_tester.py:60:14 - warning: 由于这个类未使用 `@final` 装饰，其 `cache_ttl` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\selector_tester.py:98:79 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:110:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\selector_tester.py:113:32 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\selector_tester.py:129:16 - warning: "int" 一定是 "int" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\selector_tester.py:379:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:380:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:421:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:422:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:443:82 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:525:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:525:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_tester.py:577:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:577:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:577:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_tester.py:587:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:587:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_tester.py:607:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:607:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_tester.py:617:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\selector_tester.py:617:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\selector_tester.py:619:32 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
d:\Python\fcmrawler\src\services\storage_manager.py
  d:\Python\fcmrawler\src\services\storage_manager.py:25:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:25:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:25:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:25:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:25:54 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:45:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:58:14 - warning: 由于这个类未使用 `@final` 装饰，其 `base_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\storage_manager.py:100:34 - warning: "url" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\storage_manager.py:100:55 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:118:74 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:149:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:174:72 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:174:82 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:195:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:238:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:238:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:307:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:388:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:388:70 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:404:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:404:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:404:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:404:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:404:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:411:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:411:46 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:411:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:411:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:411:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:457:44 - warning: "url" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\storage_manager.py:457:65 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:474:68 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:474:78 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:511:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:511:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:511:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:537:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:537:90 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:607:75 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:636:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:699:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:699:85 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:699:106 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:765:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:765:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:765:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\storage_manager.py:812:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\storage_manager.py:898:98 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\time_series_analyzer.py
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:17:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:17:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:17:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:20:6 - error: 无法解析导入 "scipy" (reportMissingImports)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:21:6 - error: 无法解析导入 "scipy.signal" (reportMissingImports)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:34:12 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:35:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:35:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:35:34 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:37:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:37:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:47:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:56:20 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:144:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:149:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:149:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:274:29 - warning: "timestamps" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:274:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:274:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:285:20 - warning: 变量 "intercept" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:285:31 - warning: 变量 "r_value" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:285:49 - warning: 变量 "std_err" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:313:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:313:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:313:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:330:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:330:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:330:89 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:393:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:393:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:393:96 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:429:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:429:65 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:430:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:430:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:476:42 - warning: "timestamps" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:476:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:476:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:521:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:550:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:565:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:565:100 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:600:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:600:76 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:650:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:650:90 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:675:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:710:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:725:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:726:10 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:743:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:743:78 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:749:20 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:766:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:766:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:766:78 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:766:88 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\time_series_analyzer.py:770:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\Python\fcmrawler\src\services\url_service.py
  d:\Python\fcmrawler\src\services\url_service.py:15:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:16:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:17:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:18:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "set" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:71:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:103:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\url_service.py:104:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\url_service.py:105:14 - warning: 由于这个类未使用 `@final` 装饰，其 `audit_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\url_service.py:107:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:156:28 - warning: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_service.py:196:24 - warning: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_service.py:237:47 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:277:46 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:307:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:337:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:512:54 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:632:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:632:84 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:632:94 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:708:21 - error: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:713:21 - error: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:720:25 - error: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:725:29 - error: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:726:29 - error: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:730:25 - error: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:731:41 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\url_service.py:734:21 - error: "int | Unknown | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:736:37 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\Python\fcmrawler\src\services\url_service.py:740:16 - error: "int | Unknown | list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符
    "list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:754:29 - error: "int | Unknown | list[Unknown]" 与 "Literal[1048576]" 类型不支持 "/" 运算符
    "list[Unknown]" 与 "Literal[1048576]" 类型不支持 "/" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:755:52 - error: "int | Unknown | list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符
    "list[Unknown]" 与 "Literal[0]" 类型不支持 ">" 运算符 (reportOperatorIssue)
  d:\Python\fcmrawler\src\services\url_service.py:796:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:796:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:909:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:919:16 - warning: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_service.py:920:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\services\url_service.py:955:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_service.py:1006:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:1060:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:1096:59 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1123:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1123:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1123:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:1154:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1154:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1154:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:1226:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1258:28 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_service.py:1304:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1304:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "set" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1332:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1342:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_service.py:1394:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1394:82 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1443:88 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_service.py:1443:98 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\url_service.py:1481:15 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\url_validator.py
  d:\Python\fcmrawler\src\services\url_validator.py:20:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\url_validator.py:38:5 - warning: 由于这个类未使用 `@final` 装饰，其 `BLOCKED_IP_RANGES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\url_validator.py:49:5 - warning: 由于这个类未使用 `@final` 装饰，其 `ALLOWED_SCHEMES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\url_validator.py:53:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\url_validator.py:69:27 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\services\url_validator.py:155:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\services\version_manager.py
  d:\Python\fcmrawler\src\services\version_manager.py:20:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:20:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:20:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:35:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:59:14 - warning: 由于这个类未使用 `@final` 装饰，其 `db_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\version_manager.py:60:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\version_manager.py:64:14 - warning: 由于这个类未使用 `@final` 装饰，其 `default_keep_count` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\version_manager.py:65:14 - warning: 由于这个类未使用 `@final` 装饰，其 `compression_level` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\services\version_manager.py:67:76 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:117:66 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:139:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:160:50 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:160:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:185:57 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:185:82 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:217:56 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:217:81 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:217:86 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:217:96 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\version_manager.py:265:80 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:265:90 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\version_manager.py:314:63 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:339:57 - error: "int | None" 类型的实参无法赋值给函数 "delete_field_version" 中 "int" 类型的形参 "version_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\Python\fcmrawler\src\services\version_manager.py:352:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:352:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\services\version_manager.py:419:80 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:430:102 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:457:68 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\services\version_manager.py:458:10 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\utils\async_bridge.py
  d:\Python\fcmrawler\src\utils\async_bridge.py:31:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "collections.abc.Coroutine" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:31:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:31:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:46:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PENDING` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:47:5 - warning: 由于这个类未使用 `@final` 装饰，其 `RUNNING` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:48:5 - warning: 由于这个类未使用 `@final` 装饰，其 `COMPLETED` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:49:5 - warning: 由于这个类未使用 `@final` 装饰，其 `FAILED` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:50:5 - warning: 由于这个类未使用 `@final` 装饰，其 `CANCELLED` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:63:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:63:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:64:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:65:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:66:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:78:14 - warning: 由于这个类未使用 `@final` 装饰，其 `task_id` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:79:14 - warning: 由于这个类未使用 `@final` 装饰，其 `coro` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:80:14 - warning: 由于这个类未使用 `@final` 装饰，其 `success_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:81:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:82:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:83:14 - warning: 由于这个类未使用 `@final` 装饰，其 `status` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:84:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:85:21 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:86:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:88:9 - warning: "__repr__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
  d:\Python\fcmrawler\src\utils\async_bridge.py:100:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_started` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:101:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_completed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:102:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_failed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:103:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_progress` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:104:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_cancelled` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:108:14 - warning: "loop" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\utils\async_bridge.py:108:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:109:21 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:109:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:110:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_running` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:111:14 - warning: "_shutdown_event" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\Python\fcmrawler\src\utils\async_bridge.py:111:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:112:31 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:113:20 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:145:21 - warning: 变量 "task_id" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\async_bridge.py:176:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:177:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:197:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:255:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:271:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:307:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_completed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:308:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_failed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:309:5 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_updated` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:310:5 - warning: 由于这个类未使用 `@final` 装饰，其 `task_cancelled` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:312:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:322:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_worker_thread` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:323:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_worker` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:339:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_task_counter` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\async_bridge.py:345:25 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:345:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:346:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:347:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:348:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:349:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\async_bridge.py:412:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:413:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:417:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:422:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:427:6 - warning: 未标返回值类型的函数装饰器会遮蔽函数类型，因此已忽略装饰器 (reportUntypedFunctionDecorator)
  d:\Python\fcmrawler\src\utils\async_bridge.py:440:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:440:60 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\async_bridge.py:464:18 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\async_bridge.py:464:26 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\async_bridge.py:491:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\utils\crypto.py
  d:\Python\fcmrawler\src\utils\crypto.py:24:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:24:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:24:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:79:14 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:79:23 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\crypto.py:89:29 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:192:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:192:44 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\crypto.py:217:64 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:217:74 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\crypto.py:263:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\crypto.py:388:17 - warning: 变量 "method" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\crypto.py:388:25 - warning: 变量 "algorithm" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\crypto.py:404:13 - warning: 变量 "method" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\crypto.py:404:21 - warning: 变量 "algorithm" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\crypto.py:514:16 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
d:\Python\fcmrawler\src\utils\data_validator.py
  d:\Python\fcmrawler\src\utils\data_validator.py:88:14 - warning: 由于这个类未使用 `@final` 装饰，其 `validation_rules` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\data_validator.py:91:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:91:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:213:17 - warning: 变量 "detected_format" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\data_validator.py:278:51 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:294:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:299:16 - warning: "list[dict[str, Any]]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\utils\data_validator.py:300:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\Python\fcmrawler\src\utils\data_validator.py:325:20 - warning: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\Python\fcmrawler\src\utils\data_validator.py:364:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:415:57 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:460:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:505:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:539:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:581:40 - warning: "data" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\utils\data_validator.py:581:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:581:68 - warning: "schema" 未使用 (reportUnusedParameter)
  d:\Python\fcmrawler\src\utils\data_validator.py:581:86 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:590:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:624:37 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:661:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:730:28 - warning: 找不到 "pandas" 的存根文件
    从 PyPI 安装 `pandas-stubs` 以修复此问题 (reportMissingTypeStubs)
  d:\Python\fcmrawler\src\utils\data_validator.py:732:21 - warning: 变量 "df" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\data_validator.py:894:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:902:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\data_validator.py:906:35 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
d:\Python\fcmrawler\src\utils\key_manager.py
  d:\Python\fcmrawler\src\utils\key_manager.py:21:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:21:30 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:21:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:44:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:44:48 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:57:14 - warning: 由于这个类未使用 `@final` 装饰，其 `key_file_path` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\key_manager.py:58:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:59:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_key_initialized` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\key_manager.py:228:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:228:41 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\key_manager.py:245:22 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:284:22 - warning: "_encryption_key" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\utils\key_manager.py:285:22 - warning: "_key_initialized" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\Python\fcmrawler\src\utils\key_manager.py:291:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:291:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\key_manager.py:306:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\Python\fcmrawler\src\utils\performance_profiler.py
  d:\Python\fcmrawler\src\utils\performance_profiler.py:15:20 - warning: "Any" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:15:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:15:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:15:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:15:47 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:15:47 - warning: "Union" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:43:29 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:45:27 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:56:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:63:14 - warning: 由于这个类未使用 `@final` 装饰，其 `thresholds` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:64:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:65:14 - warning: 由于这个类未使用 `@final` 装饰，其 `metrics` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:66:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:67:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:189:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:285:24 - warning: "exc_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:285:34 - warning: "exc_val" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\performance_profiler.py:285:43 - warning: "exc_tb" 参数缺少类型注解 (reportMissingParameterType)
d:\Python\fcmrawler\src\utils\request_rate_limiter.py
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:19:25 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:19:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:36:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:37:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:38:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:41:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_default_interval` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:42:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_min_interval` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:43:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_max_interval` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:46:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_antibot_increase_factor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:47:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_antibot_detection_patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:58:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:61:43 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:164:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:165:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:166:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:225:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:225:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:243:39 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:243:49 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:243:59 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:293:71 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\request_rate_limiter.py:317:9 - warning: "__repr__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
d:\Python\fcmrawler\src\utils\retry_strategy.py
  d:\Python\fcmrawler\src\utils\retry_strategy.py:19:35 - warning: 此类型自 Python 3.9 起已弃用；请改用 "type" (reportDeprecated)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:19:35 - warning: "Type" 导入项未使用 (reportUnusedImport)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:25:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:115:34 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:115:42 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:126:21 - warning: 变量 "error_category" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:163:27 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:163:35 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:174:21 - warning: 变量 "error_category" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:235:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_retries` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:236:14 - warning: 由于这个类未使用 `@final` 装饰，其 `backoff_factor` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:237:14 - warning: 由于这个类未使用 `@final` 装饰，其 `initial_delay` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:238:14 - warning: 由于这个类未使用 `@final` 装饰，其 `timeout_multiplier` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:239:14 - warning: 由于这个类未使用 `@final` 装饰，其 `enable_jitter` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:280:14 - warning: 由于这个类未使用 `@final` 装饰，其 `total_attempts` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:281:14 - warning: 由于这个类未使用 `@final` 装饰，其 `successful_retries` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:282:14 - warning: 由于这个类未使用 `@final` 装饰，其 `failed_retries` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:284:14 - warning: 由于这个类未使用 `@final` 装饰，其 `total_delay_time` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:338:34 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:338:42 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:341:17 - warning: 变量 "attempt" 未使用 (reportUnusedVariable)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:357:27 - warning: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:357:35 - warning: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\Python\fcmrawler\src\utils\retry_strategy.py:360:17 - warning: 变量 "attempt" 未使用 (reportUnusedVariable)
96 errors, 3373 warnings, 0 notes
```

