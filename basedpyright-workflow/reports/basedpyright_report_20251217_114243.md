# BasedPyright 检查报告
**生成时间**: 2025-12-17 11:42:43
**检查时间**: 2025-12-17T11:42:43.719248
**检查目录**: `Project_recorder`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 189 |
| ❌ 错误 (Error) | 212 |
| ⚠️ 警告 (Warning) | 3 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 3.93 秒 |

## 🔴 错误详情

共发现 **212** 个错误

### 按文件分组

- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py`: 57 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py`: 36 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py`: 22 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py`: 14 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py`: 12 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py`: 12 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py`: 11 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py`: 10 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py`: 9 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py`: 3 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py`: 3 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\segment_edit_dialog.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree_phase2.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\export_encrypted_script.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\character_selection_dialog.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_style_cache.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\responsive_input_scaler.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\styles_manager.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\undo_redo_manager.py`: 1 个错误

### 按规则分组

- `reportAttributeAccessIssue`: 112 次
- `reportArgumentType`: 53 次
- `reportOptionalMemberAccess`: 12 次
- `reportAssignmentType`: 9 次
- `reportCallIssue`: 6 次
- `reportReturnType`: 5 次
- `reportUndefinedVariable`: 4 次
- `reportGeneralTypeIssues`: 3 次
- `reportMissingImports`: 3 次
- `reportIndexIssue`: 2 次
- `reportRedeclaration`: 2 次
- `reportOperatorIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\export_encrypted_script.py:31

- **规则**: `reportArgumentType`
- **位置**: 第 31 行, 第 85 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
  "None" 与 "str" 不兼容

#### 2. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:26

- **规则**: `reportAssignmentType`
- **位置**: 第 26 行, 第 8 列
- **错误信息**: "type[ScriptData]" 类型不匹配声明的 "() -> dict[str, Unknown]" 类型
  "type[ScriptData]" 类型与 "() -> dict[str, Unknown]" 类型不兼容
    函数返回类型 "ScriptData" 与 "dict[str, Unknown]" 类型不兼容
      "ScriptData" 与 "dict[str, Unknown]" 不兼容

#### 3. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:312

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 312 行, 第 35 列
- **错误信息**: 无法访问 "dict[str, Unknown]" 类的 "add_event" 属性
  属性 "add_event" 未知

#### 4. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:312

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 312 行, 第 35 列
- **错误信息**: 无法访问 "dict[Unknown, Unknown]" 类的 "add_event" 属性
  属性 "add_event" 未知

#### 5. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:315

- **规则**: `reportOperatorIssue`
- **位置**: 第 315 行, 第 23 列
- **错误信息**: "Literal['events']" 与 "ScriptSegment | dict[str, Unknown] | Any | dict[Unknown, Unknown]" 类型不支持 "not in" 运算符
  "Literal['events']" 与 "ScriptSegment" 类型不支持 "not in" 运算符

#### 6. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:316

- **规则**: `reportIndexIssue`
- **位置**: 第 316 行, 第 24 列
- **错误信息**: "ScriptSegment" 类型上未定义 "__setitem__" 方法

#### 7. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:317

- **规则**: `reportIndexIssue`
- **位置**: 第 317 行, 第 20 列
- **错误信息**: "ScriptSegment" 类型上未定义 "__getitem__" 方法

#### 8. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:320

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 320 行, 第 31 列
- **错误信息**: 无法访问 "dict[str, Unknown]" 类的 "sort_events" 属性
  属性 "sort_events" 未知

#### 9. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:320

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 320 行, 第 31 列
- **错误信息**: 无法访问 "dict[Unknown, Unknown]" 类的 "sort_events" 属性
  属性 "sort_events" 未知

#### 10. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:454

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 454 行, 第 49 列
- **错误信息**: 无法为 "dict[str, Unknown]" 类的 "events" 属性赋值
  属性 "events" 未知

#### 11. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:456

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 456 行, 第 53 列
- **错误信息**: 无法访问 "dict[str, Unknown]" 类的 "update_duration" 属性
  属性 "update_duration" 未知

#### 12. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:464

- **规则**: `reportAssignmentType`
- **位置**: 第 464 行, 第 17 列
- **错误信息**: "(title: str = "新脚本", author: str = "") -> ScriptData" 类型不匹配声明的 "() -> dict[str, Unknown]" 类型
  "(title: str = "新脚本", author: str = "") -> ScriptData" 类型与 "() -> dict[str, Unknown]" 类型不兼容
    函数返回类型 "ScriptData" 与 "dict[str, Unknown]" 类型不兼容
      "ScriptData" 与 "dict[str, Unknown]" 不兼容

#### 13. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:133

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 133 行, 第 33 列
- **错误信息**: 无法访问 "ScriptData" 类的 "characters" 属性
  属性 "characters" 未知

#### 14. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:141

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 141 行, 第 33 列
- **错误信息**: 无法访问 "ScriptData" 类的 "characters" 属性
  属性 "characters" 未知

#### 15. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:264

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 264 行, 第 15 列
- **错误信息**: 无法为 "ScriptData" 类的 "characters" 属性赋值
  属性 "characters" 未知

#### 16. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:282

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 282 行, 第 15 列
- **错误信息**: 无法为 "ScriptData" 类的 "characters" 属性赋值
  属性 "characters" 未知

#### 17. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:251

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 251 行, 第 42 列
- **错误信息**: 无法访问 "str" 类的 "value" 属性
  属性 "value" 未知

#### 18. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:382

- **规则**: `reportUndefinedVariable`
- **位置**: 第 382 行, 第 26 列
- **错误信息**: "time" 未定义

#### 19. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:388

- **规则**: `reportUndefinedVariable`
- **位置**: 第 388 行, 第 25 列
- **错误信息**: "time" 未定义

#### 20. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:165

- **规则**: `reportArgumentType`
- **位置**: 第 165 行, 第 50 列
- **错误信息**: "ScriptData" 类型的实参无法赋值给函数 "save_script" 中 "str" 类型的形参 "script_path"
  "ScriptData" 与 "str" 不兼容

#### 21. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:165

- **规则**: `reportArgumentType`
- **位置**: 第 165 行, 第 58 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "save_script" 中 "Dict[str, Any]" 类型的形参 "script_data"
  "str" 与 "Dict[str, Any]" 不兼容

#### 22. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:175

- **规则**: `reportReturnType`
- **位置**: 第 175 行, 第 19 列
- **错误信息**: "ScriptOperationResult" 类型不匹配返回类型 "bool"
  "ScriptOperationResult" 与 "bool" 不兼容

#### 23. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:192

- **规则**: `reportReturnType`
- **位置**: 第 192 行, 第 19 列
- **错误信息**: "ScriptOperationResult" 类型不匹配返回类型 "ScriptData | None"
  "ScriptOperationResult" 类型与 "ScriptData | None" 类型不兼容
    "ScriptOperationResult" 与 "ScriptData" 不兼容
    "ScriptOperationResult" 与 "None" 不兼容

#### 24. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:213

- **规则**: `reportReturnType`
- **位置**: 第 213 行, 第 19 列
- **错误信息**: "Dict[str, Any]" 类型不匹配返回类型 "bool"
  "Dict[str, Any]" 与 "bool" 不兼容

#### 25. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:224

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 224 行, 第 39 列
- **错误信息**: 无法访问 "ScriptDataService" 类的 "get_script_metadata" 属性
  属性 "get_script_metadata" 未知

#### 26. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:241

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 241 行, 第 38 列
- **错误信息**: 无法访问 "ScriptDataService" 类的 "get_all_scripts" 属性
  属性 "get_all_scripts" 未知

#### 27. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:258

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 258 行, 第 38 列
- **错误信息**: 无法访问 "ScriptDataService" 类的 "search_scripts" 属性
  属性 "search_scripts" 未知

#### 28. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:483

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 483 行, 第 15 列
- **错误信息**: 无法为 "ScriptData" 类的 "characters" 属性赋值
  属性 "characters" 未知

#### 29. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:509

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 509 行, 第 15 列
- **错误信息**: 无法为 "ScriptData" 类的 "characters" 属性赋值
  属性 "characters" 未知

#### 30. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:120

- **规则**: `reportArgumentType`
- **位置**: 第 120 行, 第 23 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "process_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 31. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:494

- **规则**: `reportCallIssue`
- **位置**: 第 494 行, 第 12 列
- **错误信息**: "update" 的重载与提供的参数不匹配

#### 32. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:494

- **规则**: `reportArgumentType`
- **位置**: 第 494 行, 第 25 列
- **错误信息**: "dict[str, int | str | bool]" 类型的实参无法赋值给函数 "update" 中 "Iterable[tuple[str, int]]" 类型的形参 "m"
  "Literal['total_loggers']" 与 "tuple[str, int]" 不兼容
  "Literal['buffer_size']" 与 "tuple[str, int]" 不兼容
  "Literal['log_directory']" 与 "tuple[str, int]" 不兼容
  "Literal['console_output']" 与 "tuple[str, int]" 不兼容

#### 33. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:663

- **规则**: `reportArgumentType`
- **位置**: 第 663 行, 第 23 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "process_id"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 34. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:110

- **规则**: `reportCallIssue`
- **位置**: 第 110 行, 第 28 列
- **错误信息**: "get" 的重载与提供的参数不匹配

#### 35. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:110

- **规则**: `reportArgumentType`
- **位置**: 第 110 行, 第 47 列
- **错误信息**: "LogLevel" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
  "LogLevel" 与 "str" 不兼容

#### 36. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:140

- **规则**: `reportArgumentType`
- **位置**: 第 140 行, 第 17 列
- **错误信息**: "Literal['DEBUG']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
  "Literal['DEBUG']" 与 "LogLevel" 不兼容

#### 37. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:144

- **规则**: `reportArgumentType`
- **位置**: 第 144 行, 第 17 列
- **错误信息**: "Literal['INFO']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
  "Literal['INFO']" 与 "LogLevel" 不兼容

#### 38. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:148

- **规则**: `reportArgumentType`
- **位置**: 第 148 行, 第 17 列
- **错误信息**: "Literal['WARNING']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
  "Literal['WARNING']" 与 "LogLevel" 不兼容

#### 39. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:153

- **规则**: `reportArgumentType`
- **位置**: 第 153 行, 第 17 列
- **错误信息**: "Literal['ERROR']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
  "Literal['ERROR']" 与 "LogLevel" 不兼容

#### 40. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:158

- **规则**: `reportArgumentType`
- **位置**: 第 158 行, 第 17 列
- **错误信息**: "Literal['CRITICAL']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
  "Literal['CRITICAL']" 与 "LogLevel" 不兼容

#### 41. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:166

- **规则**: `reportArgumentType`
- **位置**: 第 166 行, 第 51 列
- **错误信息**: "LogLevel" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
  "LogLevel" 与 "str" 不兼容

#### 42. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:184

- **规则**: `reportArgumentType`
- **位置**: 第 184 行, 第 26 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__init__" 中 "LogLevel" 类型的形参 "level"
  "str" 与 "LogLevel" 不兼容

#### 43. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:206

- **规则**: `reportCallIssue`
- **位置**: 第 206 行, 第 16 列
- **错误信息**: "logger_name" 参数不存在

#### 44. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:219

- **规则**: `reportArgumentType`
- **位置**: 第 219 行, 第 26 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__init__" 中 "LogLevel" 类型的形参 "level"
  "str" 与 "LogLevel" 不兼容

#### 45. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:259

- **规则**: `reportArgumentType`
- **位置**: 第 259 行, 第 26 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__init__" 中 "LogLevel" 类型的形参 "level"
  "str" 与 "LogLevel" 不兼容

#### 46. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:361

- **规则**: `reportCallIssue`
- **位置**: 第 361 行, 第 28 列
- **错误信息**: "get" 的重载与提供的参数不匹配

#### 47. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:361

- **规则**: `reportArgumentType`
- **位置**: 第 361 行, 第 47 列
- **错误信息**: "LogLevel" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
  "LogLevel" 与 "str" 不兼容

#### 48. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338

- **规则**: `reportCallIssue`
- **位置**: 第 338 行, 第 12 列
- **错误信息**: "characters" 参数不存在

#### 49. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 338 行, 第 28 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "characters" 属性
  属性 "characters" 未知

#### 50. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:371

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 371 行, 第 14 列
- **错误信息**: 无法为 "ScriptDataModel*" 类的 "characters" 属性赋值
  属性 "characters" 未知

#### 51. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:436

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 436 行, 第 14 列
- **错误信息**: 无法为 "ScriptDataModel" 类的 "characters" 属性赋值
  属性 "characters" 未知

#### 52. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py:117

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 117 行, 第 11 列
- **错误信息**: 无法为 "WuwaRecorderUI" 类的 "logger" 属性赋值
  无法将 "None" 类型的表达式赋值给 "WuwaRecorderUI" 类的 "logger" 属性
    "None" 与 "Logger" 不兼容

#### 53. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\character_selection_dialog.py:257

- **规则**: `reportRedeclaration`
- **位置**: 第 257 行, 第 8 列
- **错误信息**: "accept_selection" 方法的声明被同名声明遮蔽

#### 54. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:21

- **规则**: `reportAssignmentType`
- **位置**: 第 21 行, 第 59 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型不匹配声明的 "type[Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent]" 类型
  "Project_recorder.script_data_model_unified.ScriptEvent" 与 "Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型与 "type[Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent]" 类型不兼容

#### 55. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:42

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 42 行, 第 21 列
- **错误信息**: 无法为 "EnhancedEventEditDialog*" 类的 "event" 属性赋值
  "ScriptEvent" 类型与 "(event: QEvent, /) -> bool" 类型不兼容

#### 56. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:216

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 216 行, 第 67 列
- **错误信息**: "QRegularExpression" 是未知的导入符号

#### 57. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:218

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 218 行, 第 41 列
- **错误信息**: `None` 没有 "setValidator" 属性

#### 58. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:229

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 229 行, 第 45 列
- **错误信息**: 无法访问 "MethodType" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 59. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:232

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 232 行, 第 46 列
- **错误信息**: 无法访问 "MethodType" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 60. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:234

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 234 行, 第 52 列
- **错误信息**: 无法访问 "MethodType" 类的 "timestamp" 属性
  属性 "timestamp" 未知

#### 61. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:291

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 291 行, 第 33 列
- **错误信息**: 无法访问 "MethodType" 类的 "timestamp" 属性
  属性 "timestamp" 未知

#### 62. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:321

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 321 行, 第 19 列
- **错误信息**: 无法为 "MethodType" 类的 "action_name" 属性赋值
  属性 "action_name" 未知

#### 63. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:322

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 322 行, 第 19 列
- **错误信息**: 无法为 "MethodType" 类的 "relative_time" 属性赋值
  属性 "relative_time" 未知

#### 64. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:323

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 323 行, 第 19 列
- **错误信息**: 无法为 "MethodType" 类的 "remark" 属性赋值
  属性 "remark" 未知

#### 65. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:325

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 325 行, 第 23 列
- **错误信息**: 无法为 "MethodType" 类的 "duration" 属性赋值
  属性 "duration" 未知

#### 66. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\segment_edit_dialog.py:23

- **规则**: `reportAssignmentType`
- **位置**: 第 23 行, 第 59 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型不匹配声明的 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment]" 类型
  "Project_recorder.script_data_model_unified.ScriptSegment" 与 "Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型与 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment]" 类型不兼容

#### 67. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\segment_edit_dialog.py:23

- **规则**: `reportAssignmentType`
- **位置**: 第 23 行, 第 74 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型不匹配声明的 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegmentType]" 类型
  "Project_recorder.script_data_model_unified.ScriptSegmentType" 与 "Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegmentType" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型与 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegmentType]" 类型不兼容

#### 68. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_style_cache.py:194

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 194 行, 第 43 列
- **错误信息**: 此处应为类而非 "(iterable: Iterable[object], /) -> bool"

#### 69. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:33

- **规则**: `reportMissingImports`
- **位置**: 第 33 行, 第 9 列
- **错误信息**: 无法解析导入 "..components.dpi_manager"

#### 70. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:42

- **规则**: `reportMissingImports`
- **位置**: 第 42 行, 第 9 列
- **错误信息**: 无法解析导入 "...services.infrastructure.logging_manager"

#### 71. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:43

- **规则**: `reportMissingImports`
- **位置**: 第 43 行, 第 9 列
- **错误信息**: 无法解析导入 "...services.infrastructure.performance_monitor"

#### 72. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:245

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 245 行, 第 2 列
- **错误信息**: f-string 的表达式部分中使用转义序列 `\` 需要 Python 3.12 或更高版本

#### 73. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:533

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 533 行, 第 63 列
- **错误信息**: 无法访问 "str" 类的 "value" 属性
  属性 "value" 未知

#### 74. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1078

- **规则**: `reportArgumentType`
- **位置**: 第 1078 行, 第 35 列
- **错误信息**: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
  "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
    "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
    "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容

#### 75. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1078

- **规则**: `reportArgumentType`
- **位置**: 第 1078 行, 第 53 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
  "int | None" 类型与 "str | InputSize" 类型不兼容
    "int" 类型与 "str | InputSize" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputSize" 不兼容

#### 76. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1081

- **规则**: `reportArgumentType`
- **位置**: 第 1081 行, 第 34 列
- **错误信息**: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
  "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
    "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
    "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容

#### 77. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1081

- **规则**: `reportArgumentType`
- **位置**: 第 1081 行, 第 52 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
  "int | None" 类型与 "str | InputSize" 类型不兼容
    "int" 类型与 "str | InputSize" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputSize" 不兼容

#### 78. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1084

- **规则**: `reportArgumentType`
- **位置**: 第 1084 行, 第 34 列
- **错误信息**: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
  "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
    "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
    "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容

#### 79. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1084

- **规则**: `reportArgumentType`
- **位置**: 第 1084 行, 第 52 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
  "int | None" 类型与 "str | InputSize" 类型不兼容
    "int" 类型与 "str | InputSize" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputSize" 不兼容

#### 80. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1087

- **规则**: `reportArgumentType`
- **位置**: 第 1087 行, 第 37 列
- **错误信息**: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
  "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
    "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
    "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容

#### 81. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1087

- **规则**: `reportArgumentType`
- **位置**: 第 1087 行, 第 55 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
  "int | None" 类型与 "str | InputSize" 类型不兼容
    "int" 类型与 "str | InputSize" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputSize" 不兼容

#### 82. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1090

- **规则**: `reportArgumentType`
- **位置**: 第 1090 行, 第 35 列
- **错误信息**: "Literal[InputSize.SMALL]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
  "Literal[InputSize.SMALL]" 类型与 "str | InputState" 类型不兼容
    "Literal[InputSize.SMALL]" 与 "str" 不兼容
    "Literal[InputSize.SMALL]" 与 "InputState" 不兼容

#### 83. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1090

- **规则**: `reportArgumentType`
- **位置**: 第 1090 行, 第 52 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
  "int | None" 类型与 "str | InputSize" 类型不兼容
    "int" 类型与 "str | InputSize" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputSize" 不兼容

#### 84. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1093

- **规则**: `reportArgumentType`
- **位置**: 第 1093 行, 第 35 列
- **错误信息**: "Literal[InputSize.LARGE]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
  "Literal[InputSize.LARGE]" 类型与 "str | InputState" 类型不兼容
    "Literal[InputSize.LARGE]" 与 "str" 不兼容
    "Literal[InputSize.LARGE]" 与 "InputState" 不兼容

#### 85. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1093

- **规则**: `reportArgumentType`
- **位置**: 第 1093 行, 第 52 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
  "int | None" 类型与 "str | InputSize" 类型不兼容
    "int" 类型与 "str | InputSize" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputSize" 不兼容

#### 86. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1095

- **规则**: `reportArgumentType`
- **位置**: 第 1095 行, 第 69 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_area_style" 中 "str | InputState" 类型的形参 "state"
  "int | None" 类型与 "str | InputState" 类型不兼容
    "int" 类型与 "str | InputState" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputState" 不兼容

#### 87. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1096

- **规则**: `reportArgumentType`
- **位置**: 第 1096 行, 第 74 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_text_area_style" 中 "str | InputState" 类型的形参 "state"
  "int | None" 类型与 "str | InputState" 类型不兼容
    "int" 类型与 "str | InputState" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputState" 不兼容

#### 88. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1099

- **规则**: `reportArgumentType`
- **位置**: 第 1099 行, 第 69 列
- **错误信息**: "Literal[InputState.NORMAL]" 类型的实参无法赋值给函数 "get_slider_style" 中 "str" 类型的形参 "orientation"
  "Literal[InputState.NORMAL]" 与 "str" 不兼容

#### 89. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1100

- **规则**: `reportArgumentType`
- **位置**: 第 1100 行, 第 65 列
- **错误信息**: "Literal[InputState.NORMAL]" 类型的实参无法赋值给函数 "get_slider_style" 中 "str" 类型的形参 "orientation"
  "Literal[InputState.NORMAL]" 与 "str" 不兼容

#### 90. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1103

- **规则**: `reportArgumentType`
- **位置**: 第 1103 行, 第 75 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "get_search_input_style" 中 "str | InputState" 类型的形参 "state"
  "int | None" 类型与 "str | InputState" 类型不兼容
    "int" 类型与 "str | InputState" 类型不兼容
      "int" 与 "str" 不兼容
      "int" 与 "InputState" 不兼容

#### 91. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\responsive_input_scaler.py:292

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 292 行, 第 43 列
- **错误信息**: 此处应为类而非 "(iterable: Iterable[object], /) -> bool"

#### 92. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\styles_manager.py:104

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 104 行, 第 30 列
- **错误信息**: 无法访问 "QCoreApplication" 类的 "allWidgets" 属性
  属性 "allWidgets" 未知

#### 93. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32

- **规则**: `reportAssignmentType`
- **位置**: 第 32 行, 第 8 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptData]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptData]" 类型
  "Project_recorder.script_data_model_unified.ScriptData" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptData" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptData]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptData]" 类型不兼容

#### 94. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32

- **规则**: `reportAssignmentType`
- **位置**: 第 32 行, 第 20 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegment]" 类型
  "Project_recorder.script_data_model_unified.ScriptSegment" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptSegment" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegment]" 类型不兼容

#### 95. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32

- **规则**: `reportAssignmentType`
- **位置**: 第 32 行, 第 35 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptEvent]" 类型
  "Project_recorder.script_data_model_unified.ScriptEvent" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptEvent" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptEvent]" 类型不兼容

#### 96. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32

- **规则**: `reportAssignmentType`
- **位置**: 第 32 行, 第 48 列
- **错误信息**: "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegmentType]" 类型
  "Project_recorder.script_data_model_unified.ScriptSegmentType" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptSegmentType" 不兼容
  "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegmentType]" 类型不兼容

#### 97. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:156

- **规则**: `reportArgumentType`
- **位置**: 第 156 行, 第 25 列
- **错误信息**: "QPlainTextEdit | None" 类型的实参无法赋值给函数 "addWidget" 中 "QWidget" 类型的形参 "arg__1"
  "QPlainTextEdit | None" 类型与 "QWidget" 类型不兼容
    "None" 与 "QWidget" 不兼容

#### 98. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:330

- **规则**: `reportArgumentType`
- **位置**: 第 330 行, 第 72 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
  "None" 与 "str" 不兼容

#### 99. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:409

- **规则**: `reportArgumentType`
- **位置**: 第 409 行, 第 8 列
- **错误信息**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "int" 类型的形参 "value"
  "float" 与 "int" 不兼容

#### 100. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:410

- **规则**: `reportArgumentType`
- **位置**: 第 410 行, 第 8 列
- **错误信息**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "int" 类型的形参 "value"
  "float" 与 "int" 不兼容

#### 101. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:411

- **规则**: `reportArgumentType`
- **位置**: 第 411 行, 第 8 列
- **错误信息**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "int" 类型的形参 "value"
  "float" 与 "int" 不兼容

#### 102. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:439

- **规则**: `reportArgumentType`
- **位置**: 第 439 行, 第 71 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
  "None" 与 "List[str]" 不兼容

#### 103. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:439

- **规则**: `reportArgumentType`
- **位置**: 第 439 行, 第 108 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
  "None" 与 "List[str]" 不兼容

#### 104. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:480

- **规则**: `reportArgumentType`
- **位置**: 第 480 行, 第 63 列
- **错误信息**: "ScriptSegment" 类型的实参无法赋值给函数 "create_segment_item" 中 "ScriptSegment" 类型的形参 "segment"
  "Project_recorder.ui.widgets.script_preview_tree.ScriptSegment" 与 "Project_recorder.script_data_model_unified.ScriptSegment" 不兼容

#### 105. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:599

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 599 行, 第 74 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 106. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:600

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 600 行, 第 50 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 107. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:603

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 603 行, 第 85 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 108. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:605

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 605 行, 第 37 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
  属性 "event_id" 未知

#### 109. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:605

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 605 行, 第 37 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
  "event_id" 为只读属性

#### 110. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:606

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 606 行, 第 50 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 111. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:619

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 619 行, 第 37 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 112. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:624

- **规则**: `reportRedeclaration`
- **位置**: 第 624 行, 第 8 列
- **错误信息**: "_find_tree_item_by_event_id" 方法的声明被同名声明遮蔽

#### 113. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:651

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 651 行, 第 37 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 114. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:658

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 658 行, 第 77 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 115. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:661

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 661 行, 第 29 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
  属性 "event_id" 未知

#### 116. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:661

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 661 行, 第 29 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
  "event_id" 为只读属性

#### 117. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:663

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 663 行, 第 59 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 118. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:993

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 993 行, 第 34 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 119. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1011

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1011 行, 第 38 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 120. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1015

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1015 行, 第 42 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 121. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1018

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1018 行, 第 42 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 122. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1021

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1021 行, 第 82 列
- **错误信息**: 无法访问 "ScriptData" 类的 "metadata" 属性
  属性 "metadata" 未知

#### 123. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1022

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1022 行, 第 55 列
- **错误信息**: 无法访问 "ScriptData" 类的 "metadata" 属性
  属性 "metadata" 未知

#### 124. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1024

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1024 行, 第 42 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 125. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1026

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1026 行, 第 42 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 126. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1028

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1028 行, 第 38 列
- **错误信息**: `None` 没有 "setPlainText" 属性

#### 127. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1060

- **规则**: `reportArgumentType`
- **位置**: 第 1060 行, 第 41 列
- **错误信息**: "Project_recorder.ui.widgets.tree_items.ScriptEvent | Project_recorder.script_data_model_unified.ScriptEvent" 类型的实参无法赋值给函数 "__init__" 中 "ScriptEvent" 类型的形参 "event"
  "Project_recorder.ui.widgets.tree_items.ScriptEvent | Project_recorder.script_data_model_unified.ScriptEvent" 类型与 "ScriptEvent" 类型不兼容
    "Project_recorder.ui.widgets.tree_items.ScriptEvent" 与 "Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent" 不兼容

#### 128. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1074

- **规则**: `reportArgumentType`
- **位置**: 第 1074 行, 第 35 列
- **错误信息**: "ScriptSegment" 类型的实参无法赋值给函数 "__init__" 中 "ScriptSegment" 类型的形参 "segment"
  "Project_recorder.script_data_model_unified.ScriptSegment" 与 "Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment" 不兼容

#### 129. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1074

- **规则**: `reportArgumentType`
- **位置**: 第 1074 行, 第 57 列
- **错误信息**: "Self@EnhancedScriptPreviewTree" 类型的实参无法赋值给函数 "__init__" 中 "QDialog | None" 类型的形参 "parent"
  "Self@EnhancedScriptPreviewTree" 类型与 "QDialog | None" 类型不兼容
    "EnhancedScriptPreviewTree*" 与 "QDialog" 不兼容
    "EnhancedScriptPreviewTree*" 与 "None" 不兼容

#### 130. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1139

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1139 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 131. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1160

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1160 行, 第 33 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "action_name" 属性赋值
  属性 "action_name" 未知

#### 132. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1160

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1160 行, 第 33 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "action_name" 属性赋值
  "action_name" 为只读属性

#### 133. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1180

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1180 行, 第 69 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 134. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1182

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1182 行, 第 27 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
  属性 "event_id" 未知

#### 135. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1182

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1182 行, 第 27 列
- **错误信息**: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
  "event_id" 为只读属性

#### 136. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1183

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1183 行, 第 34 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 137. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1273

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1273 行, 第 29 列
- **错误信息**: 无法访问 "EnhancedScriptPreviewTree*" 类的 "events_delete_requested_by_index" 属性
  属性 "events_delete_requested_by_index" 未知

#### 138. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1387

- **规则**: `reportArgumentType`
- **位置**: 第 1387 行, 第 72 列
- **错误信息**: "Literal['normal']" 类型的实参无法赋值给函数 "_convert_events_to_segment_type" 中 "ScriptSegmentType" 类型的形参 "target_segment_type"
  "Literal['normal']" 与 "ScriptSegmentType" 不兼容

#### 139. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1409

- **规则**: `reportArgumentType`
- **位置**: 第 1409 行, 第 72 列
- **错误信息**: "Literal['loop']" 类型的实参无法赋值给函数 "_convert_events_to_segment_type" 中 "ScriptSegmentType" 类型的形参 "target_segment_type"
  "Literal['loop']" 与 "ScriptSegmentType" 不兼容

#### 140. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1429

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1429 行, 第 62 列
- **错误信息**: 无法访问 "ScriptSegmentType" 类的 "value" 属性
  属性 "value" 未知

#### 141. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1450

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1450 行, 第 81 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 142. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1472

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1472 行, 第 40 列
- **错误信息**: 无法为 "ScriptData" 类的 "segments" 属性赋值
  "builtins.list" 与 "builtins.list" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "Project_recorder.ui.widgets.script_preview_tree.ScriptSegment" 与 "Project_recorder.script_data_model_unified.ScriptSegment" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 143. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1544

- **规则**: `reportReturnType`
- **位置**: 第 1544 行, 第 19 列
- **错误信息**: "Literal['normal']" 类型不匹配返回类型 "ScriptSegmentType"
  "Literal['normal']" 与 "ScriptSegmentType" 不兼容

#### 144. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1552

- **规则**: `reportReturnType`
- **位置**: 第 1552 行, 第 15 列
- **错误信息**: "Literal['normal']" 类型不匹配返回类型 "ScriptSegmentType"
  "Literal['normal']" 与 "ScriptSegmentType" 不兼容

#### 145. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1561

- **规则**: `reportCallIssue`
- **位置**: 第 1561 行, 第 20 列
- **错误信息**: "get" 的重载与提供的参数不匹配

#### 146. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1561

- **规则**: `reportArgumentType`
- **位置**: 第 1561 行, 第 35 列
- **错误信息**: "ScriptSegmentType" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
  "ScriptSegmentType" 与 "str" 不兼容

#### 147. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1565

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1565 行, 第 53 列
- **错误信息**: `None` 没有 "segments" 属性

#### 148. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1778

- **规则**: `reportUndefinedVariable`
- **位置**: 第 1778 行, 第 36 列
- **错误信息**: "traceback" 未定义

#### 149. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1811

- **规则**: `reportArgumentType`
- **位置**: 第 1811 行, 第 27 列
- **错误信息**: "Project_recorder.ui.widgets.script_preview_tree.ScriptData | Project_recorder.script_data_model_unified.ScriptData | None" 类型的实参无法赋值给函数 "save_to_file" 中 "ScriptData" 类型的形参 "script"
  "Project_recorder.ui.widgets.script_preview_tree.ScriptData | Project_recorder.script_data_model_unified.ScriptData | None" 类型与 "ScriptData" 类型不兼容
    "Project_recorder.ui.widgets.script_preview_tree.ScriptData" 与 "Project_recorder.script_data_model_unified.ScriptData" 不兼容

#### 150. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree_phase2.py:675

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 675 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 151. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree_phase2.py:725

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 725 行, 第 38 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "with_changes" 属性
  属性 "with_changes" 未知

#### 152. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:134

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 134 行, 第 23 列
- **错误信息**: 无法访问 "QObject" 类的 "controller" 属性
  属性 "controller" 未知

#### 153. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:136

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 136 行, 第 23 列
- **错误信息**: 无法访问 "QObject" 类的 "insert_segment_event" 属性
  属性 "insert_segment_event" 未知

#### 154. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:163

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 163 行, 第 23 列
- **错误信息**: 无法访问 "QObject" 类的 "controller" 属性
  属性 "controller" 未知

#### 155. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:165

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 165 行, 第 23 列
- **错误信息**: 无法访问 "QObject" 类的 "modify_segment_event" 属性
  属性 "modify_segment_event" 未知

#### 156. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:177

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 177 行, 第 23 列
- **错误信息**: 无法访问 "QObject" 类的 "controller" 属性
  属性 "controller" 未知

#### 157. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:179

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 179 行, 第 23 列
- **错误信息**: 无法访问 "QObject" 类的 "delete_segment_events" 属性
  属性 "delete_segment_events" 未知

#### 158. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:196

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 196 行, 第 19 列
- **错误信息**: 无法访问 "QObject" 类的 "controller" 属性
  属性 "controller" 未知

#### 159. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:209

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 209 行, 第 19 列
- **错误信息**: 无法访问 "QObject" 类的 "controller" 属性
  属性 "controller" 未知

#### 160. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:211

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 211 行, 第 19 列
- **错误信息**: 无法访问 "QObject" 类的 "paste_events_at_index" 属性
  属性 "paste_events_at_index" 未知

#### 161. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:208

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 208 行, 第 39 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 162. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:209

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 209 行, 第 47 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 163. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:217

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 217 行, 第 35 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 164. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:218

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 218 行, 第 64 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 165. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:218

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 218 行, 第 88 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 166. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:219

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 219 行, 第 45 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 167. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:239

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 239 行, 第 30 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 168. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:243

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 243 行, 第 30 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 169. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:258

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 258 行, 第 41 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
  属性 "timestamp" 未知

#### 170. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:260

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 260 行, 第 43 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 171. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:261

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 261 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 172. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:262

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 262 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 173. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:263

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 263 行, 第 38 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "remark" 属性
  属性 "remark" 未知

#### 174. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:264

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 264 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "duration" 属性
  属性 "duration" 未知

#### 175. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:265

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 265 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "parameters" 属性
  属性 "parameters" 未知

#### 176. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:272

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 272 行, 第 41 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
  属性 "timestamp" 未知

#### 177. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:273

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 273 行, 第 45 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 178. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:274

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 274 行, 第 43 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 179. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:275

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 275 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 180. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:276

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 276 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 181. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:277

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 277 行, 第 38 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "remark" 属性
  属性 "remark" 未知

#### 182. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:279

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 279 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "parameters" 属性
  属性 "parameters" 未知

#### 183. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:286

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 286 行, 第 41 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
  属性 "timestamp" 未知

#### 184. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:287

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 287 行, 第 45 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 185. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:289

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 289 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 186. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:290

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 290 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 187. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:291

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 291 行, 第 38 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "remark" 属性
  属性 "remark" 未知

#### 188. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:292

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 292 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "duration" 属性
  属性 "duration" 未知

#### 189. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:293

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 293 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "parameters" 属性
  属性 "parameters" 未知

#### 190. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:300

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 300 行, 第 41 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
  属性 "timestamp" 未知

#### 191. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:301

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 301 行, 第 45 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
  属性 "relative_time" 未知

#### 192. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:302

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 302 行, 第 43 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "action_name" 属性
  属性 "action_name" 未知

#### 193. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:303

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 303 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 194. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:304

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 304 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_id" 属性
  属性 "event_id" 未知

#### 195. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:306

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 306 行, 第 40 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "duration" 属性
  属性 "duration" 未知

#### 196. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:307

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 307 行, 第 42 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "parameters" 属性
  属性 "parameters" 未知

#### 197. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\undo_redo_manager.py:21

- **规则**: `reportUndefinedVariable`
- **位置**: 第 21 行, 第 44 列
- **错误信息**: "EditOperation" 未定义

#### 198. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py:39

- **规则**: `reportArgumentType`
- **位置**: 第 39 行, 第 66 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
  "None" 与 "List[str]" 不兼容

#### 199. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py:39

- **规则**: `reportArgumentType`
- **位置**: 第 39 行, 第 94 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
  "None" 与 "List[str]" 不兼容

#### 200. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py:40

- **规则**: `reportArgumentType`
- **位置**: 第 40 行, 第 35 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
  "None" 与 "List[str]" 不兼容

#### 201. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:162

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 162 行, 第 37 列
- **错误信息**: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
  "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 202. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:166

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 166 行, 第 37 列
- **错误信息**: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
  "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 203. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:428

- **规则**: `reportArgumentType`
- **位置**: 第 428 行, 第 46 列
- **错误信息**: "dict[str, Unknown]" 类型的实参无法赋值给函数 "set_script_data" 中 "ScriptData" 类型的形参 "script_data"
  "dict[str, Unknown]" 与 "ScriptData" 不兼容

#### 204. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:542

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 542 行, 第 44 列
- **错误信息**: `None` 没有 "get_selected_events" 属性

#### 205. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:898

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 898 行, 第 30 列
- **错误信息**: `None` 没有 "set_recording_state" 属性

#### 206. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:942

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 942 行, 第 30 列
- **错误信息**: `None` 没有 "set_recording_state" 属性

#### 207. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1100

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1100 行, 第 37 列
- **错误信息**: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
  "List[List[int | str]]" 与 "List[Dict[str, Any]]" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "List[int | str]" 与 "Dict[str, Any]" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 208. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1218

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1218 行, 第 47 列
- **错误信息**: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
  属性 "get_selected_rows" 未知

#### 209. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1251

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1251 行, 第 47 列
- **错误信息**: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
  属性 "get_selected_rows" 未知

#### 210. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1284

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1284 行, 第 47 列
- **错误信息**: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
  属性 "get_selected_rows" 未知

#### 211. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1326

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1326 行, 第 47 列
- **错误信息**: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
  属性 "get_selected_rows" 未知

#### 212. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1335

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1335 行, 第 108 列
- **错误信息**: 无法访问 "type[ScriptSegmentType]" 类的 "START" 属性
  属性 "START" 未知

## ⚠️ 警告详情

共发现 **3** 个警告

1. `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176` - "KeyCombination" 已在 `__all__` 中声明，但未在模块中定义 (`reportUnsupportedDunderAll`)
2. `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176` - "KeyEventData" 已在 `__all__` 中声明，但未在模块中定义 (`reportUnsupportedDunderAll`)
3. `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176` - "MouseEventData" 已在 `__all__` 中声明，但未在模块中定义 (`reportUnsupportedDunderAll`)

## 📁 检查的文件列表

1. `Project_recorder\__init__.py`
2. `Project_recorder\about_dialog.py`
3. `Project_recorder\analysis_dialog.py`
4. `Project_recorder\build_with_pyinstaller.py`
5. `Project_recorder\calculator-1.py`
6. `Project_recorder\character_list_management_dialog.py`
7. `Project_recorder\character_manager.py`
8. `Project_recorder\character_selection_dialog.py`
9. `Project_recorder\cleanup_legacy_services.py`
10. `Project_recorder\color_config.py`
11. `Project_recorder\config\validation_rules.py`
12. `Project_recorder\config_manager.py`
13. `Project_recorder\conflict_detector.py`
14. `Project_recorder\core\application.py`
15. `Project_recorder\core\application_container.py`
16. `Project_recorder\core\application_factory.py`
17. `Project_recorder\core\bootstrap.py`
18. `Project_recorder\core\event_index_manager.py`
19. `Project_recorder\core\service_discovery.py`
20. `Project_recorder\core\ultra_compact_collection.py`
21. `Project_recorder\core\unified_application.py`
22. `Project_recorder\core\unified_application_factory.py`
23. `Project_recorder\cross_platform_color_patch.py`
24. `Project_recorder\dpi_manager.py`
25. `Project_recorder\duplicate_detector.py`
26. `Project_recorder\export_encrypted_script.py`
27. `Project_recorder\final_migration.py`
28. `Project_recorder\fix_hardcoded_imports.py`
29. `Project_recorder\fix_imports_clean.py`
30. `Project_recorder\fix_imports_comprehensive.py`
31. `Project_recorder\font_manager.py`
32. `Project_recorder\global_hotkey_manager.py`
33. `Project_recorder\hotkey_config_manager.py`
34. `Project_recorder\hotkey_integration.py`
35. `Project_recorder\hotkey_models.py`
36. `Project_recorder\hotkey_ui.py`
37. `Project_recorder\import_adapter.py`
38. `Project_recorder\material_design_components.py`
39. `Project_recorder\performance_benchmark.py`
40. `Project_recorder\performance_test_unified.py`
41. `Project_recorder\pyinstaller_main.py`
42. `Project_recorder\pyinstaller_runtime_hook.py`
43. `Project_recorder\pyinstaller_spec_optimized.py`
44. `Project_recorder\report_generator.py`
45. `Project_recorder\responsive_layout_manager.py`
46. `Project_recorder\script_analyzer.py`
47. `Project_recorder\script_data_manager.py`
48. `Project_recorder\script_data_manager_unified.py`
49. `Project_recorder\script_data_model.py`
50. `Project_recorder\script_data_model_services.py`
51. `Project_recorder\script_data_model_unified.py`
52. `Project_recorder\script_editor_core.py`
53. `Project_recorder\script_event_utils.py`
54. `Project_recorder\script_file_manager.py`
55. `Project_recorder\script_file_manager_ui.py`
56. `Project_recorder\script_integration_service.py`
57. `Project_recorder\script_migration_service.py`
58. `Project_recorder\script_migration_tool.py`
59. `Project_recorder\script_path_dialog.py`
60. `Project_recorder\script_performance_service.py`
61. `Project_recorder\script_service.py`
62. `Project_recorder\script_service_core.py`
63. `Project_recorder\script_services_consolidated.py`
64. `Project_recorder\script_ui_controller.py`
65. `Project_recorder\script_validation_service.py`
66. `Project_recorder\segment_editor.py`
67. `Project_recorder\services\__init__.py`
68. `Project_recorder\services\adapters\__init__.py`
69. `Project_recorder\services\adapters\script_data_access_adapter.py`
70. `Project_recorder\services\adapters\script_integration_adapter.py`
71. `Project_recorder\services\adapters\script_performance_adapter.py`
72. `Project_recorder\services\backup_security_service.py`
73. `Project_recorder\services\character_service.py`
74. `Project_recorder\services\config_service.py`
75. `Project_recorder\services\hotkey_service.py`
76. `Project_recorder\services\infrastructure\__init__.py`
77. `Project_recorder\services\infrastructure\cache_manager.py`
78. `Project_recorder\services\infrastructure\config_manager.py`
79. `Project_recorder\services\infrastructure\logging_manager.py`
80. `Project_recorder\services\infrastructure\logging_manager_unified.py`
81. `Project_recorder\services\infrastructure\performance_monitor.py`
82. `Project_recorder\services\input_base.py`
83. `Project_recorder\services\input_events.py`
84. `Project_recorder\services\input_permission_service.py`
85. `Project_recorder\services\input_service.py`
86. `Project_recorder\services\input_types.py`
87. `Project_recorder\services\keyboard_listener_service.py`
88. `Project_recorder\services\log_formatter_service.py`
89. `Project_recorder\services\log_storage_service.py`
90. `Project_recorder\services\logging_service.py`
91. `Project_recorder\services\mouse_listener_service.py`
92. `Project_recorder\services\path_service.py`
93. `Project_recorder\services\performance_monitoring_service.py`
94. `Project_recorder\services\script_data_service.py`
95. `Project_recorder\services\script_library_service.py`
96. `Project_recorder\services\script_migration_service.py`
97. `Project_recorder\services\script_model_service.py`
98. `Project_recorder\services\script_performance_service.py`
99. `Project_recorder\services\segment_editor_service.py`
100. `Project_recorder\services\unified_script_service.py`
101. `Project_recorder\services\user_communication_service.py`
102. `Project_recorder\services\validation_service.py`
103. `Project_recorder\settings_dialog.py`
104. `Project_recorder\sub_window_manager.py`
105. `Project_recorder\system_tray_manager.py`
106. `Project_recorder\test_encrypt.py`
107. `Project_recorder\test_fixes.py`
108. `Project_recorder\test_fixes_v2.py`
109. `Project_recorder\tests\test_character_hierarchy.py`
110. `Project_recorder\ui\__init__.py`
111. `Project_recorder\ui\compatibility_layer.py`
112. `Project_recorder\ui\components\__init__.py`
113. `Project_recorder\ui\components\cross_platform_color_patch.py`
114. `Project_recorder\ui\components\dpi_manager.py`
115. `Project_recorder\ui\components\font_manager.py`
116. `Project_recorder\ui\components\material_design_components.py`
117. `Project_recorder\ui\components\responsive_layout_manager.py`
118. `Project_recorder\ui\controllers\__init__.py`
119. `Project_recorder\ui\controllers\base_ui_controller.py`
120. `Project_recorder\ui\controllers\library_ui_controller.py`
121. `Project_recorder\ui\controllers\main_ui_controller.py`
122. `Project_recorder\ui\controllers\script_ui_controller.py`
123. `Project_recorder\ui\controllers\segment_editor_controller.py`
124. `Project_recorder\ui\controllers\timeline_ui_controller.py`
125. `Project_recorder\ui\dialogs\__init__.py`
126. `Project_recorder\ui\dialogs\about_dialog.py`
127. `Project_recorder\ui\dialogs\analysis_dialog.py`
128. `Project_recorder\ui\dialogs\character_list_management_dialog.py`
129. `Project_recorder\ui\dialogs\character_selection_dialog.py`
130. `Project_recorder\ui\dialogs\event_edit_dialog.py`
131. `Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py`
132. `Project_recorder\ui\dialogs\script_path_dialog.py`
133. `Project_recorder\ui\dialogs\segment_edit_dialog.py`
134. `Project_recorder\ui\dialogs\settings_dialog.py`
135. `Project_recorder\ui\dialogs\usage_instruction_dialog.py`
136. `Project_recorder\ui\legacy_adapter.py`
137. `Project_recorder\ui\main_window.py`
138. `Project_recorder\ui\main_window_styled.py`
139. `Project_recorder\ui\styles\__init__.py`
140. `Project_recorder\ui\styles\components\__init__.py`
141. `Project_recorder\ui\styles\components\button_styles.py`
142. `Project_recorder\ui\styles\components\card_styles.py`
143. `Project_recorder\ui\styles\components\dialog_styles.py`
144. `Project_recorder\ui\styles\components\input_style_cache.py`
145. `Project_recorder\ui\styles\components\input_styles.py`
146. `Project_recorder\ui\styles\components\label_styles.py`
147. `Project_recorder\ui\styles\components\responsive_input_scaler.py`
148. `Project_recorder\ui\styles\layouts\__init__.py`
149. `Project_recorder\ui\styles\layouts\form_layouts.py`
150. `Project_recorder\ui\styles\layouts\grid_layouts.py`
151. `Project_recorder\ui\styles\layouts\main_window_layouts.py`
152. `Project_recorder\ui\styles\layouts\responsive_layouts.py`
153. `Project_recorder\ui\styles\main_window\__init__.py`
154. `Project_recorder\ui\styles\main_window\control_panel_styles.py`
155. `Project_recorder\ui\styles\main_window\main_window_styles.py`
156. `Project_recorder\ui\styles\main_window\preview_panel_styles.py`
157. `Project_recorder\ui\styles\main_window\recording_panel_styles.py`
158. `Project_recorder\ui\styles\styles_manager.py`
159. `Project_recorder\ui\styles\themes\__init__.py`
160. `Project_recorder\ui\styles\themes\color_system.py`
161. `Project_recorder\ui\styles\themes\material_theme.py`
162. `Project_recorder\ui\styles\themes\theme_manager.py`
163. `Project_recorder\ui\widgets\__init__.py`
164. `Project_recorder\ui\widgets\base_event_table.py`
165. `Project_recorder\ui\widgets\hotkey_ui.py`
166. `Project_recorder\ui\widgets\script_event_table.py`
167. `Project_recorder\ui\widgets\script_file_manager_ui.py`
168. `Project_recorder\ui\widgets\script_preview_tree.py`
169. `Project_recorder\ui\widgets\script_preview_tree_phase2.py`
170. `Project_recorder\ui\widgets\segment_editor.py`
171. `Project_recorder\ui\widgets\segment_event_table.py`
172. `Project_recorder\ui\widgets\segment_properties_dialog.py`
173. `Project_recorder\ui\widgets\tree_items.py`
174. `Project_recorder\undo_redo_manager.py`
175. `Project_recorder\usage_instruction_dialog.py`
176. `Project_recorder\utils\__init__.py`
177. `Project_recorder\utils\encryption_helper.py`
178. `Project_recorder\utils\ui_helpers.py`
179. `Project_recorder\validators\__init__.py`
180. `Project_recorder\validators\base_validator.py`
181. `Project_recorder\validators\consistency_validator.py`
182. `Project_recorder\validators\event_validator.py`
183. `Project_recorder\validators\metadata_validator.py`
184. `Project_recorder\validators\segment_validator.py`
185. `Project_recorder\validators\validation_types.py`
186. `Project_recorder\wuwa_recorder.py`
187. `Project_recorder\wuwa_recorder_core.py`
188. `Project_recorder\wuwa_recorder_ui_merged.py`
189. `Project_recorder\wuwa_script_editor_main.py`

## 📄 原始检查输出

```
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\export_encrypted_script.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\export_encrypted_script.py:31:86 - error: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
    "None" 与 "str" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:26:9 - error: "type[ScriptData]" 类型不匹配声明的 "() -> dict[str, Unknown]" 类型
    "type[ScriptData]" 类型与 "() -> dict[str, Unknown]" 类型不兼容
      函数返回类型 "ScriptData" 与 "dict[str, Unknown]" 类型不兼容
        "ScriptData" 与 "dict[str, Unknown]" 不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:312:36 - error: 无法访问 "dict[str, Unknown]" 类的 "add_event" 属性
    属性 "add_event" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:312:36 - error: 无法访问 "dict[Unknown, Unknown]" 类的 "add_event" 属性
    属性 "add_event" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:315:24 - error: "Literal['events']" 与 "ScriptSegment | dict[str, Unknown] | Any | dict[Unknown, Unknown]" 类型不支持 "not in" 运算符
    "Literal['events']" 与 "ScriptSegment" 类型不支持 "not in" 运算符 (reportOperatorIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:316:25 - error: "ScriptSegment" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:317:21 - error: "ScriptSegment" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:320:32 - error: 无法访问 "dict[str, Unknown]" 类的 "sort_events" 属性
    属性 "sort_events" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:320:32 - error: 无法访问 "dict[Unknown, Unknown]" 类的 "sort_events" 属性
    属性 "sort_events" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:454:50 - error: 无法为 "dict[str, Unknown]" 类的 "events" 属性赋值
    属性 "events" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:456:54 - error: 无法访问 "dict[str, Unknown]" 类的 "update_duration" 属性
    属性 "update_duration" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:464:18 - error: "(title: str = "新脚本", author: str = "") -> ScriptData" 类型不匹配声明的 "() -> dict[str, Unknown]" 类型
    "(title: str = "新脚本", author: str = "") -> ScriptData" 类型与 "() -> dict[str, Unknown]" 类型不兼容
      函数返回类型 "ScriptData" 与 "dict[str, Unknown]" 类型不兼容
        "ScriptData" 与 "dict[str, Unknown]" 不兼容 (reportAssignmentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:133:34 - error: 无法访问 "ScriptData" 类的 "characters" 属性
    属性 "characters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:141:34 - error: 无法访问 "ScriptData" 类的 "characters" 属性
    属性 "characters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:264:16 - error: 无法为 "ScriptData" 类的 "characters" 属性赋值
    属性 "characters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py:282:16 - error: 无法为 "ScriptData" 类的 "characters" 属性赋值
    属性 "characters" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:251:43 - error: 无法访问 "str" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:382:27 - error: "time" 未定义 (reportUndefinedVariable)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:388:26 - error: "time" 未定义 (reportUndefinedVariable)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:165:51 - error: "ScriptData" 类型的实参无法赋值给函数 "save_script" 中 "str" 类型的形参 "script_path"
    "ScriptData" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:165:59 - error: "str" 类型的实参无法赋值给函数 "save_script" 中 "Dict[str, Any]" 类型的形参 "script_data"
    "str" 与 "Dict[str, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:175:20 - error: "ScriptOperationResult" 类型不匹配返回类型 "bool"
    "ScriptOperationResult" 与 "bool" 不兼容 (reportReturnType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:192:20 - error: "ScriptOperationResult" 类型不匹配返回类型 "ScriptData | None"
    "ScriptOperationResult" 类型与 "ScriptData | None" 类型不兼容
      "ScriptOperationResult" 与 "ScriptData" 不兼容
      "ScriptOperationResult" 与 "None" 不兼容 (reportReturnType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:213:20 - error: "Dict[str, Any]" 类型不匹配返回类型 "bool"
    "Dict[str, Any]" 与 "bool" 不兼容 (reportReturnType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:224:40 - error: 无法访问 "ScriptDataService" 类的 "get_script_metadata" 属性
    属性 "get_script_metadata" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:241:39 - error: 无法访问 "ScriptDataService" 类的 "get_all_scripts" 属性
    属性 "get_all_scripts" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:258:39 - error: 无法访问 "ScriptDataService" 类的 "search_scripts" 属性
    属性 "search_scripts" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:483:16 - error: 无法为 "ScriptData" 类的 "characters" 属性赋值
    属性 "characters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:509:16 - error: 无法为 "ScriptData" 类的 "characters" 属性赋值
    属性 "characters" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176:5 - warning: "KeyCombination" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176:37 - warning: "KeyEventData" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176:53 - warning: "MouseEventData" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:120:24 - error: "int | None" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "process_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:494:13 - error: "update" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:494:26 - error: "dict[str, int | str | bool]" 类型的实参无法赋值给函数 "update" 中 "Iterable[tuple[str, int]]" 类型的形参 "m"
    "Literal['total_loggers']" 与 "tuple[str, int]" 不兼容
    "Literal['buffer_size']" 与 "tuple[str, int]" 不兼容
    "Literal['log_directory']" 与 "tuple[str, int]" 不兼容
    "Literal['console_output']" 与 "tuple[str, int]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\infrastructure\logging_manager_unified.py:663:24 - error: "int | None" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "process_id"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:110:29 - error: "get" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:110:48 - error: "LogLevel" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
    "LogLevel" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:140:18 - error: "Literal['DEBUG']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
    "Literal['DEBUG']" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:144:18 - error: "Literal['INFO']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
    "Literal['INFO']" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:148:18 - error: "Literal['WARNING']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
    "Literal['WARNING']" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:153:18 - error: "Literal['ERROR']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
    "Literal['ERROR']" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:158:18 - error: "Literal['CRITICAL']" 类型的实参无法赋值给函数 "log" 中 "LogLevel" 类型的形参 "level"
    "Literal['CRITICAL']" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:166:52 - error: "LogLevel" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
    "LogLevel" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:184:27 - error: "str" 类型的实参无法赋值给函数 "__init__" 中 "LogLevel" 类型的形参 "level"
    "str" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:206:17 - error: "logger_name" 参数不存在 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:219:27 - error: "str" 类型的实参无法赋值给函数 "__init__" 中 "LogLevel" 类型的形参 "level"
    "str" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:259:27 - error: "str" 类型的实参无法赋值给函数 "__init__" 中 "LogLevel" 类型的形参 "level"
    "str" 与 "LogLevel" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:361:29 - error: "get" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\logging_service.py:361:48 - error: "LogLevel" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
    "LogLevel" 与 "str" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338:13 - error: "characters" 参数不存在 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338:29 - error: 无法访问 "ScriptDataModel*" 类的 "characters" 属性
    属性 "characters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:371:15 - error: 无法为 "ScriptDataModel*" 类的 "characters" 属性赋值
    属性 "characters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:436:15 - error: 无法为 "ScriptDataModel" 类的 "characters" 属性赋值
    属性 "characters" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py:117:12 - error: 无法为 "WuwaRecorderUI" 类的 "logger" 属性赋值
    无法将 "None" 类型的表达式赋值给 "WuwaRecorderUI" 类的 "logger" 属性
      "None" 与 "Logger" 不兼容 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\character_selection_dialog.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\character_selection_dialog.py:257:9 - error: "accept_selection" 方法的声明被同名声明遮蔽 (reportRedeclaration)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:21:60 - error: "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型不匹配声明的 "type[Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent]" 类型
    "Project_recorder.script_data_model_unified.ScriptEvent" 与 "Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型与 "type[Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:42:22 - error: 无法为 "EnhancedEventEditDialog*" 类的 "event" 属性赋值
    "ScriptEvent" 类型与 "(event: QEvent, /) -> bool" 类型不兼容 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:216:68 - error: "QRegularExpression" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:218:42 - error: `None` 没有 "setValidator" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:229:46 - error: 无法访问 "MethodType" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:232:47 - error: 无法访问 "MethodType" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:234:53 - error: 无法访问 "MethodType" 类的 "timestamp" 属性
    属性 "timestamp" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:291:34 - error: 无法访问 "MethodType" 类的 "timestamp" 属性
    属性 "timestamp" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:321:20 - error: 无法为 "MethodType" 类的 "action_name" 属性赋值
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:322:20 - error: 无法为 "MethodType" 类的 "relative_time" 属性赋值
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:323:20 - error: 无法为 "MethodType" 类的 "remark" 属性赋值
    属性 "remark" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py:325:24 - error: 无法为 "MethodType" 类的 "duration" 属性赋值
    属性 "duration" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\segment_edit_dialog.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\segment_edit_dialog.py:23:60 - error: "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型不匹配声明的 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment]" 类型
    "Project_recorder.script_data_model_unified.ScriptSegment" 与 "Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型与 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\dialogs\segment_edit_dialog.py:23:75 - error: "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型不匹配声明的 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegmentType]" 类型
    "Project_recorder.script_data_model_unified.ScriptSegmentType" 与 "Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegmentType" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型与 "type[Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegmentType]" 类型不兼容 (reportAssignmentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_style_cache.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_style_cache.py:194:44 - error: 此处应为类而非 "(iterable: Iterable[object], /) -> bool" (reportGeneralTypeIssues)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:33:10 - error: 无法解析导入 "..components.dpi_manager" (reportMissingImports)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:42:10 - error: 无法解析导入 "...services.infrastructure.logging_manager" (reportMissingImports)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:43:10 - error: 无法解析导入 "...services.infrastructure.performance_monitor" (reportMissingImports)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:245:3 - error: f-string 的表达式部分中使用转义序列 `\` 需要 Python 3.12 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:533:64 - error: 无法访问 "str" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1078:36 - error: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
    "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
      "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
      "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1078:54 - error: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
    "int | None" 类型与 "str | InputSize" 类型不兼容
      "int" 类型与 "str | InputSize" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputSize" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1081:35 - error: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
    "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
      "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
      "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1081:53 - error: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
    "int | None" 类型与 "str | InputSize" 类型不兼容
      "int" 类型与 "str | InputSize" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputSize" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1084:35 - error: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
    "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
      "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
      "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1084:53 - error: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
    "int | None" 类型与 "str | InputSize" 类型不兼容
      "int" 类型与 "str | InputSize" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputSize" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1087:38 - error: "Literal[InputSize.MEDIUM]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
    "Literal[InputSize.MEDIUM]" 类型与 "str | InputState" 类型不兼容
      "Literal[InputSize.MEDIUM]" 与 "str" 不兼容
      "Literal[InputSize.MEDIUM]" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1087:56 - error: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
    "int | None" 类型与 "str | InputSize" 类型不兼容
      "int" 类型与 "str | InputSize" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputSize" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1090:36 - error: "Literal[InputSize.SMALL]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
    "Literal[InputSize.SMALL]" 类型与 "str | InputState" 类型不兼容
      "Literal[InputSize.SMALL]" 与 "str" 不兼容
      "Literal[InputSize.SMALL]" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1090:53 - error: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
    "int | None" 类型与 "str | InputSize" 类型不兼容
      "int" 类型与 "str | InputSize" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputSize" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1093:36 - error: "Literal[InputSize.LARGE]" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputState" 类型的形参 "state"
    "Literal[InputSize.LARGE]" 类型与 "str | InputState" 类型不兼容
      "Literal[InputSize.LARGE]" 与 "str" 不兼容
      "Literal[InputSize.LARGE]" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1093:53 - error: "int | None" 类型的实参无法赋值给函数 "get_text_input_style" 中 "str | InputSize" 类型的形参 "size"
    "int | None" 类型与 "str | InputSize" 类型不兼容
      "int" 类型与 "str | InputSize" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputSize" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1095:70 - error: "int | None" 类型的实参无法赋值给函数 "get_text_area_style" 中 "str | InputState" 类型的形参 "state"
    "int | None" 类型与 "str | InputState" 类型不兼容
      "int" 类型与 "str | InputState" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1096:75 - error: "int | None" 类型的实参无法赋值给函数 "get_text_area_style" 中 "str | InputState" 类型的形参 "state"
    "int | None" 类型与 "str | InputState" 类型不兼容
      "int" 类型与 "str | InputState" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputState" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1099:70 - error: "Literal[InputState.NORMAL]" 类型的实参无法赋值给函数 "get_slider_style" 中 "str" 类型的形参 "orientation"
    "Literal[InputState.NORMAL]" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1100:66 - error: "Literal[InputState.NORMAL]" 类型的实参无法赋值给函数 "get_slider_style" 中 "str" 类型的形参 "orientation"
    "Literal[InputState.NORMAL]" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\input_styles.py:1103:76 - error: "int | None" 类型的实参无法赋值给函数 "get_search_input_style" 中 "str | InputState" 类型的形参 "state"
    "int | None" 类型与 "str | InputState" 类型不兼容
      "int" 类型与 "str | InputState" 类型不兼容
        "int" 与 "str" 不兼容
        "int" 与 "InputState" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\responsive_input_scaler.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\components\responsive_input_scaler.py:292:44 - error: 此处应为类而非 "(iterable: Iterable[object], /) -> bool" (reportGeneralTypeIssues)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\styles_manager.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\styles\styles_manager.py:104:31 - error: 无法访问 "QCoreApplication" 类的 "allWidgets" 属性
    属性 "allWidgets" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32:9 - error: "type[Project_recorder.script_data_model_unified.ScriptData]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptData]" 类型
    "Project_recorder.script_data_model_unified.ScriptData" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptData" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptData]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptData]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32:21 - error: "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegment]" 类型
    "Project_recorder.script_data_model_unified.ScriptSegment" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptSegment" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptSegment]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegment]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32:36 - error: "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptEvent]" 类型
    "Project_recorder.script_data_model_unified.ScriptEvent" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptEvent" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptEvent]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptEvent]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:32:49 - error: "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型不匹配声明的 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegmentType]" 类型
    "Project_recorder.script_data_model_unified.ScriptSegmentType" 与 "Project_recorder.ui.widgets.script_preview_tree.ScriptSegmentType" 不兼容
    "type[Project_recorder.script_data_model_unified.ScriptSegmentType]" 类型与 "type[Project_recorder.ui.widgets.script_preview_tree.ScriptSegmentType]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:156:26 - error: "QPlainTextEdit | None" 类型的实参无法赋值给函数 "addWidget" 中 "QWidget" 类型的形参 "arg__1"
    "QPlainTextEdit | None" 类型与 "QWidget" 类型不兼容
      "None" 与 "QWidget" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:330:73 - error: 无法将 "None" 类型的表达式赋值给 "str" 类型的参数
    "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:409:9 - error: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "int" 类型的形参 "value"
    "float" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:410:9 - error: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "int" 类型的形参 "value"
    "float" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:411:9 - error: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "int" 类型的形参 "value"
    "float" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:439:72 - error: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
    "None" 与 "List[str]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:439:109 - error: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
    "None" 与 "List[str]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:480:64 - error: "ScriptSegment" 类型的实参无法赋值给函数 "create_segment_item" 中 "ScriptSegment" 类型的形参 "segment"
    "Project_recorder.ui.widgets.script_preview_tree.ScriptSegment" 与 "Project_recorder.script_data_model_unified.ScriptSegment" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:599:75 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:600:51 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:603:86 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:605:38 - error: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:605:38 - error: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
    "event_id" 为只读属性 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:606:51 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:619:38 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:624:9 - error: "_find_tree_item_by_event_id" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:651:38 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:658:78 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:661:30 - error: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:661:30 - error: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
    "event_id" 为只读属性 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:663:60 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:993:35 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1011:39 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1015:43 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1018:43 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1021:83 - error: 无法访问 "ScriptData" 类的 "metadata" 属性
    属性 "metadata" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1022:56 - error: 无法访问 "ScriptData" 类的 "metadata" 属性
    属性 "metadata" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1024:43 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1026:43 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1028:39 - error: `None` 没有 "setPlainText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1060:42 - error: "Project_recorder.ui.widgets.tree_items.ScriptEvent | Project_recorder.script_data_model_unified.ScriptEvent" 类型的实参无法赋值给函数 "__init__" 中 "ScriptEvent" 类型的形参 "event"
    "Project_recorder.ui.widgets.tree_items.ScriptEvent | Project_recorder.script_data_model_unified.ScriptEvent" 类型与 "ScriptEvent" 类型不兼容
      "Project_recorder.ui.widgets.tree_items.ScriptEvent" 与 "Project_recorder.ui.dialogs.event_edit_dialog_enhanced.ScriptEvent" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1074:36 - error: "ScriptSegment" 类型的实参无法赋值给函数 "__init__" 中 "ScriptSegment" 类型的形参 "segment"
    "Project_recorder.script_data_model_unified.ScriptSegment" 与 "Project_recorder.ui.dialogs.segment_edit_dialog.ScriptSegment" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1074:58 - error: "Self@EnhancedScriptPreviewTree" 类型的实参无法赋值给函数 "__init__" 中 "QDialog | None" 类型的形参 "parent"
    "Self@EnhancedScriptPreviewTree" 类型与 "QDialog | None" 类型不兼容
      "EnhancedScriptPreviewTree*" 与 "QDialog" 不兼容
      "EnhancedScriptPreviewTree*" 与 "None" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1139:43 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1160:34 - error: 无法为 "ScriptEvent" 类的 "action_name" 属性赋值
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1160:34 - error: 无法为 "ScriptEvent" 类的 "action_name" 属性赋值
    "action_name" 为只读属性 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1180:70 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1182:28 - error: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1182:28 - error: 无法为 "ScriptEvent" 类的 "event_id" 属性赋值
    "event_id" 为只读属性 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1183:35 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1273:30 - error: 无法访问 "EnhancedScriptPreviewTree*" 类的 "events_delete_requested_by_index" 属性
    属性 "events_delete_requested_by_index" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1387:73 - error: "Literal['normal']" 类型的实参无法赋值给函数 "_convert_events_to_segment_type" 中 "ScriptSegmentType" 类型的形参 "target_segment_type"
    "Literal['normal']" 与 "ScriptSegmentType" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1409:73 - error: "Literal['loop']" 类型的实参无法赋值给函数 "_convert_events_to_segment_type" 中 "ScriptSegmentType" 类型的形参 "target_segment_type"
    "Literal['loop']" 与 "ScriptSegmentType" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1429:63 - error: 无法访问 "ScriptSegmentType" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1450:82 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1472:41 - error: 无法为 "ScriptData" 类的 "segments" 属性赋值
    "builtins.list" 与 "builtins.list" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "Project_recorder.ui.widgets.script_preview_tree.ScriptSegment" 与 "Project_recorder.script_data_model_unified.ScriptSegment" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1544:20 - error: "Literal['normal']" 类型不匹配返回类型 "ScriptSegmentType"
    "Literal['normal']" 与 "ScriptSegmentType" 不兼容 (reportReturnType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1552:16 - error: "Literal['normal']" 类型不匹配返回类型 "ScriptSegmentType"
    "Literal['normal']" 与 "ScriptSegmentType" 不兼容 (reportReturnType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1561:21 - error: "get" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1561:36 - error: "ScriptSegmentType" 类型的实参无法赋值给函数 "get" 中 "str" 类型的形参 "key"
    "ScriptSegmentType" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1565:54 - error: `None` 没有 "segments" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1778:37 - error: "traceback" 未定义 (reportUndefinedVariable)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1811:28 - error: "Project_recorder.ui.widgets.script_preview_tree.ScriptData | Project_recorder.script_data_model_unified.ScriptData | None" 类型的实参无法赋值给函数 "save_to_file" 中 "ScriptData" 类型的形参 "script"
    "Project_recorder.ui.widgets.script_preview_tree.ScriptData | Project_recorder.script_data_model_unified.ScriptData | None" 类型与 "ScriptData" 类型不兼容
      "Project_recorder.ui.widgets.script_preview_tree.ScriptData" 与 "Project_recorder.script_data_model_unified.ScriptData" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree_phase2.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree_phase2.py:675:43 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree_phase2.py:725:39 - error: 无法访问 "ScriptEvent" 类的 "with_changes" 属性
    属性 "with_changes" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:134:24 - error: 无法访问 "QObject" 类的 "controller" 属性
    属性 "controller" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:136:24 - error: 无法访问 "QObject" 类的 "insert_segment_event" 属性
    属性 "insert_segment_event" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:163:24 - error: 无法访问 "QObject" 类的 "controller" 属性
    属性 "controller" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:165:24 - error: 无法访问 "QObject" 类的 "modify_segment_event" 属性
    属性 "modify_segment_event" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:177:24 - error: 无法访问 "QObject" 类的 "controller" 属性
    属性 "controller" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:179:24 - error: 无法访问 "QObject" 类的 "delete_segment_events" 属性
    属性 "delete_segment_events" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:196:20 - error: 无法访问 "QObject" 类的 "controller" 属性
    属性 "controller" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:209:20 - error: 无法访问 "QObject" 类的 "controller" 属性
    属性 "controller" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_event_table.py:211:20 - error: 无法访问 "QObject" 类的 "paste_events_at_index" 属性
    属性 "paste_events_at_index" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:208:40 - error: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:209:48 - error: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:217:36 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:218:65 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:218:89 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:219:46 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:239:31 - error: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:243:31 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:258:42 - error: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
    属性 "timestamp" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:260:44 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:261:43 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:262:41 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:263:39 - error: 无法访问 "ScriptEvent" 类的 "remark" 属性
    属性 "remark" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:264:41 - error: 无法访问 "ScriptEvent" 类的 "duration" 属性
    属性 "duration" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:265:43 - error: 无法访问 "ScriptEvent" 类的 "parameters" 属性
    属性 "parameters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:272:42 - error: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
    属性 "timestamp" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:273:46 - error: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:274:44 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:275:43 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:276:41 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:277:39 - error: 无法访问 "ScriptEvent" 类的 "remark" 属性
    属性 "remark" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:279:43 - error: 无法访问 "ScriptEvent" 类的 "parameters" 属性
    属性 "parameters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:286:42 - error: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
    属性 "timestamp" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:287:46 - error: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:289:43 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:290:41 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:291:39 - error: 无法访问 "ScriptEvent" 类的 "remark" 属性
    属性 "remark" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:292:41 - error: 无法访问 "ScriptEvent" 类的 "duration" 属性
    属性 "duration" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:293:43 - error: 无法访问 "ScriptEvent" 类的 "parameters" 属性
    属性 "parameters" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:300:42 - error: 无法访问 "ScriptEvent" 类的 "timestamp" 属性
    属性 "timestamp" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:301:46 - error: 无法访问 "ScriptEvent" 类的 "relative_time" 属性
    属性 "relative_time" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:302:44 - error: 无法访问 "ScriptEvent" 类的 "action_name" 属性
    属性 "action_name" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:303:43 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:304:41 - error: 无法访问 "ScriptEvent" 类的 "event_id" 属性
    属性 "event_id" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:306:41 - error: 无法访问 "ScriptEvent" 类的 "duration" 属性
    属性 "duration" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\tree_items.py:307:43 - error: 无法访问 "ScriptEvent" 类的 "parameters" 属性
    属性 "parameters" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\undo_redo_manager.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\undo_redo_manager.py:21:45 - error: "EditOperation" 未定义 (reportUndefinedVariable)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py:39:67 - error: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
    "None" 与 "List[str]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py:39:95 - error: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
    "None" 与 "List[str]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\validators\validation_types.py:40:36 - error: 无法将 "None" 类型的表达式赋值给 "List[str]" 类型的参数
    "None" 与 "List[str]" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:162:38 - error: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
    "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:166:38 - error: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
    "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:428:47 - error: "dict[str, Unknown]" 类型的实参无法赋值给函数 "set_script_data" 中 "ScriptData" 类型的形参 "script_data"
    "dict[str, Unknown]" 与 "ScriptData" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:542:45 - error: `None` 没有 "get_selected_events" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:898:31 - error: `None` 没有 "set_recording_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:942:31 - error: `None` 没有 "set_recording_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1100:38 - error: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
    "List[List[int | str]]" 与 "List[Dict[str, Any]]" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "List[int | str]" 与 "Dict[str, Any]" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1218:48 - error: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
    属性 "get_selected_rows" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1251:48 - error: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
    属性 "get_selected_rows" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1284:48 - error: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
    属性 "get_selected_rows" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1326:48 - error: 无法访问 "EnhancedScriptPreviewTree" 类的 "get_selected_rows" 属性
    属性 "get_selected_rows" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1335:109 - error: 无法访问 "type[ScriptSegmentType]" 类的 "START" 属性
    属性 "START" 未知 (reportAttributeAccessIssue)
212 errors, 3 warnings, 0 notes
```

