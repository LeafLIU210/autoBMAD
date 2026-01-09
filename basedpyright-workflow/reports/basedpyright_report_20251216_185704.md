# BasedPyright 检查报告
**生成时间**: 2025-12-16 18:57:04
**检查时间**: 2025-12-10T10:19:43.637590
**检查目录**: `Project_recorder`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 116 |
| ❌ 错误 (Error) | 97 |
| ⚠️ 警告 (Warning) | 3 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 6.50 秒 |

## 🔴 错误详情

共发现 **97** 个错误

### 按文件分组

- `d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py`: 35 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py`: 12 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py`: 11 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py`: 8 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py`: 7 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py`: 6 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_manager_unified.py`: 2 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_integration_service.py`: 2 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_ui_controller.py`: 2 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_validation_service.py`: 2 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_script_editor_main.py`: 2 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\core\application.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\import_adapter.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\main_window.py`: 1 个错误
- `d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_core.py`: 1 个错误

### 按规则分组

- `reportAttributeAccessIssue`: 62 次
- `reportUndefinedVariable`: 22 次
- `reportMissingImports`: 8 次
- `reportCallIssue`: 2 次
- `reportArgumentType`: 1 次
- `reportReturnType`: 1 次
- `reportOperatorIssue`: 1 次

### 详细错误列表

#### 1. d:\Python\wuwa_actionseq_recorder\Project_recorder\core\application.py:72

- **规则**: `reportArgumentType`
- **位置**: 第 72 行, 第 61 列
- **错误信息**: "None" 类型的实参无法赋值给函数 "resolve" 中 "type[T@resolve]" 类型的形参 "service_type"
  "None" 类型与 "type[T@resolve]" 类型不兼容

#### 2. d:\Python\wuwa_actionseq_recorder\Project_recorder\import_adapter.py:35

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 35 行, 第 24 列
- **错误信息**: "_MEIPASS" 不是 "sys" 模块的已知属性

#### 3. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_manager_unified.py:474

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 474 行, 第 17 列
- **错误信息**: 无法访问 "UnifiedScriptDataManager*" 类的 "mode_changed" 属性
  属性 "mode_changed" 未知

#### 4. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_manager_unified.py:474

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 474 行, 第 40 列
- **错误信息**: 无法访问 "UnifiedScriptDataManager*" 类的 "get_mode" 属性
  属性 "get_mode" 未知

#### 5. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model.py:213

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 213 行, 第 31 列
- **错误信息**: 无法访问 "ScriptData" 类的 "mode" 属性
  属性 "mode" 未知

#### 6. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:711

- **规则**: `reportReturnType`
- **位置**: 第 711 行, 第 15 列
- **错误信息**: "None" 类型不匹配返回类型 "bool"
  "None" 与 "bool" 不兼容

#### 7. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:34

- **规则**: `reportMissingImports`
- **位置**: 第 34 行, 第 9 列
- **错误信息**: 无法解析导入 ".script_event_utils"

#### 8. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:266

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 266 行, 第 24 列
- **错误信息**: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
  属性 "edit_history" 未知

#### 9. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:281

- **规则**: `reportUndefinedVariable`
- **位置**: 第 281 行, 第 39 列
- **错误信息**: "EditHistory" 未定义

#### 10. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:283

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 283 行, 第 20 列
- **错误信息**: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
  属性 "edit_history" 未知

#### 11. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:287

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 287 行, 第 13 列
- **错误信息**: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
  属性 "edit_history" 未知

#### 12. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:296

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 296 行, 第 43 列
- **错误信息**: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
  属性 "edit_history" 未知

#### 13. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:298

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 298 行, 第 35 列
- **错误信息**: 无法访问 "ScriptEditorCore*" 类的 "last_operation" 属性
  属性 "last_operation" 未知

#### 14. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:298

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 298 行, 第 64 列
- **错误信息**: 无法访问 "ScriptEditorCore*" 类的 "last_operation" 属性
  属性 "last_operation" 未知

#### 15. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_integration_service.py:23

- **规则**: `reportMissingImports`
- **位置**: 第 23 行, 第 5 列
- **错误信息**: 无法解析导入 "Project_recorder.script_event_utils"

#### 16. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_integration_service.py:490

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 490 行, 第 40 列
- **错误信息**: 无法访问 "ScriptData" 类的 "mode" 属性
  属性 "mode" 未知

#### 17. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:252

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 252 行, 第 31 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 18. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:164

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 164 行, 第 27 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 19. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:185

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 185 行, 第 26 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 20. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:206

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 206 行, 第 27 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 21. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:223

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 223 行, 第 28 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 22. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:240

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 240 行, 第 27 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 23. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:257

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 257 行, 第 27 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 24. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:424

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 424 行, 第 17 列
- **错误信息**: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
  属性 "repository" 未知

#### 25. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_ui_controller.py:253

- **规则**: `reportCallIssue`
- **位置**: 第 253 行, 第 71 列
- **错误信息**: 需要传入 5 个位置参数

#### 26. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_ui_controller.py:602

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 602 行, 第 64 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 27. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_validation_service.py:157

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 157 行, 第 21 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 28. d:\Python\wuwa_actionseq_recorder\Project_recorder\script_validation_service.py:158

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 158 行, 第 57 列
- **错误信息**: 无法访问 "ScriptEvent" 类的 "event_type" 属性
  属性 "event_type" 未知

#### 29. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:30

- **规则**: `reportUndefinedVariable`
- **位置**: 第 30 行, 第 23 列
- **错误信息**: "QTableWidget" 未定义

#### 30. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:54

- **规则**: `reportUndefinedVariable`
- **位置**: 第 54 行, 第 34 列
- **错误信息**: "QTableWidget" 未定义

#### 31. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:55

- **规则**: `reportUndefinedVariable`
- **位置**: 第 55 行, 第 30 列
- **错误信息**: "QTableWidget" 未定义

#### 32. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:61

- **规则**: `reportUndefinedVariable`
- **位置**: 第 61 行, 第 39 列
- **错误信息**: "QHeaderView" 未定义

#### 33. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:62

- **规则**: `reportUndefinedVariable`
- **位置**: 第 62 行, 第 39 列
- **错误信息**: "QHeaderView" 未定义

#### 34. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:63

- **规则**: `reportUndefinedVariable`
- **位置**: 第 63 行, 第 39 列
- **错误信息**: "QHeaderView" 未定义

#### 35. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:64

- **规则**: `reportUndefinedVariable`
- **位置**: 第 64 行, 第 39 列
- **错误信息**: "QHeaderView" 未定义

#### 36. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:65

- **规则**: `reportUndefinedVariable`
- **位置**: 第 65 行, 第 39 列
- **错误信息**: "QHeaderView" 未定义

#### 37. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:140

- **规则**: `reportUndefinedVariable`
- **位置**: 第 140 行, 第 33 列
- **错误信息**: "QTableWidgetItem" 未定义

#### 38. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:143

- **规则**: `reportUndefinedVariable`
- **位置**: 第 143 行, 第 24 列
- **错误信息**: "QTableWidgetItem" 未定义

#### 39. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:148

- **规则**: `reportUndefinedVariable`
- **位置**: 第 148 行, 第 33 列
- **错误信息**: "QTableWidgetItem" 未定义

#### 40. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:151

- **规则**: `reportUndefinedVariable`
- **位置**: 第 151 行, 第 33 列
- **错误信息**: "QTableWidgetItem" 未定义

#### 41. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:155

- **规则**: `reportUndefinedVariable`
- **位置**: 第 155 行, 第 33 列
- **错误信息**: "QTableWidgetItem" 未定义

#### 42. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:217

- **规则**: `reportUndefinedVariable`
- **位置**: 第 217 行, 第 25 列
- **错误信息**: "cast" 未定义

#### 43. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:242

- **规则**: `reportUndefinedVariable`
- **位置**: 第 242 行, 第 33 列
- **错误信息**: "cast" 未定义

#### 44. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:283

- **规则**: `reportUndefinedVariable`
- **位置**: 第 283 行, 第 25 列
- **错误信息**: "cast" 未定义

#### 45. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:297

- **规则**: `reportUndefinedVariable`
- **位置**: 第 297 行, 第 28 列
- **错误信息**: "UndoRedoManager" 未定义

#### 46. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:370

- **规则**: `reportUndefinedVariable`
- **位置**: 第 370 行, 第 28 列
- **错误信息**: "QTableWidget" 未定义

#### 47. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:405

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 405 行, 第 53 列
- **错误信息**: 无法访问 "ScriptEditor*" 类的 "on_event_selected" 属性
  属性 "on_event_selected" 未知

#### 48. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:412

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 412 行, 第 58 列
- **错误信息**: 无法访问 "ScriptEditor*" 类的 "on_operation_executed" 属性
  属性 "on_operation_executed" 未知

#### 49. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:413

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 413 行, 第 55 列
- **错误信息**: 无法访问 "ScriptEditor*" 类的 "update_history_display" 属性
  属性 "update_history_display" 未知

#### 50. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:416

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 416 行, 第 50 列
- **错误信息**: 无法访问 "ScriptEditor*" 类的 "auto_save" 属性
  属性 "auto_save" 未知

#### 51. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:424

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 424 行, 第 13 列
- **错误信息**: 无法访问 "ScriptEditor*" 类的 "update_info_display" 属性
  属性 "update_info_display" 未知

#### 52. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:548

- **规则**: `reportUndefinedVariable`
- **位置**: 第 548 行, 第 17 列
- **错误信息**: "ScriptValidator" 未定义

#### 53. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:565

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 565 行, 第 13 列
- **错误信息**: 无法访问 "ScriptEditor*" 类的 "update_info_display" 属性
  属性 "update_info_display" 未知

#### 54. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:593

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 593 行, 第 57 列
- **错误信息**: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
  属性 "ENDING" 未知

#### 55. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:802

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 802 行, 第 56 列
- **错误信息**: 无法访问 "ScriptData" 类的 "is_segmented" 属性
  属性 "is_segmented" 未知

#### 56. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:824

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 824 行, 第 59 列
- **错误信息**: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
  属性 "ENDING" 未知

#### 57. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1003

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1003 行, 第 40 列
- **错误信息**: 无法访问 "ScriptData" 类的 "is_segmented" 属性
  属性 "is_segmented" 未知

#### 58. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1023

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1023 行, 第 56 列
- **错误信息**: 无法访问 "ScriptData" 类的 "is_segmented" 属性
  属性 "is_segmented" 未知

#### 59. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1167

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1167 行, 第 52 列
- **错误信息**: 无法访问 "ScriptData" 类的 "is_segmented" 属性
  属性 "is_segmented" 未知

#### 60. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1194

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1194 行, 第 33 列
- **错误信息**: 无法为 "ScriptData" 类的 "is_segmented" 属性赋值
  属性 "is_segmented" 未知

#### 61. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1206

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1206 行, 第 56 列
- **错误信息**: 无法访问 "ScriptData" 类的 "is_segmented" 属性
  属性 "is_segmented" 未知

#### 62. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1227

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1227 行, 第 33 列
- **错误信息**: 无法为 "ScriptData" 类的 "is_segmented" 属性赋值
  属性 "is_segmented" 未知

#### 63. d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1239

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1239 行, 第 56 列
- **错误信息**: 无法访问 "ScriptData" 类的 "is_segmented" 属性
  属性 "is_segmented" 未知

#### 64. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py:547

- **规则**: `reportUndefinedVariable`
- **位置**: 第 547 行, 第 11 列
- **错误信息**: "is_segmented" 未定义

#### 65. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:235

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 235 行, 第 16 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 66. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:246

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 246 行, 第 16 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 67. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:259

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 259 行, 第 16 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 68. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:282

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 282 行, 第 25 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 69. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:285

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 285 行, 第 16 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 70. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338

- **规则**: `reportCallIssue`
- **位置**: 第 338 行, 第 12 列
- **错误信息**: "mode" 参数不存在

#### 71. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 338 行, 第 22 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 72. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:342

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 342 行, 第 16 列
- **错误信息**: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
  属性 "mode" 未知

#### 73. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:498

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 498 行, 第 17 列
- **错误信息**: 无法访问 "ScriptDataModel" 类的 "mode" 属性
  属性 "mode" 未知

#### 74. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:536

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 536 行, 第 17 列
- **错误信息**: 无法访问 "ScriptDataModel" 类的 "mode" 属性
  属性 "mode" 未知

#### 75. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:549

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 549 行, 第 26 列
- **错误信息**: 无法访问 "ScriptDataModel" 类的 "mode" 属性
  属性 "mode" 未知

#### 76. d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:630

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 630 行, 第 26 列
- **错误信息**: 无法访问 "ScriptDataModel" 类的 "mode" 属性
  属性 "mode" 未知

#### 77. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\main_window.py:341

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 341 行, 第 36 列
- **错误信息**: 无法访问 "MainUIController" 类的 "is_developer_mode_enabled" 属性
  属性 "is_developer_mode_enabled" 未知

#### 78. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:41

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 41 行, 第 71 列
- **错误信息**: "EditOperation" 是未知的导入符号

#### 79. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:43

- **规则**: `reportMissingImports`
- **位置**: 第 43 行, 第 13 列
- **错误信息**: 无法解析导入 "Project_recorder.undo_redo_manager"

#### 80. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:48

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 48 行, 第 75 列
- **错误信息**: "EditOperation" 是未知的导入符号

#### 81. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:50

- **规则**: `reportMissingImports`
- **位置**: 第 50 行, 第 17 列
- **错误信息**: 无法解析导入 "undo_redo_manager"

#### 82. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:67

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 67 行, 第 75 列
- **错误信息**: "EditOperation" 是未知的导入符号

#### 83. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:69

- **规则**: `reportMissingImports`
- **位置**: 第 69 行, 第 17 列
- **错误信息**: 无法解析导入 "Project_recorder.undo_redo_manager"

#### 84. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:73

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 73 行, 第 75 列
- **错误信息**: "EditOperation" 是未知的导入符号

#### 85. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:75

- **规则**: `reportMissingImports`
- **位置**: 第 75 行, 第 17 列
- **错误信息**: 无法解析导入 "undo_redo_manager"

#### 86. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:103

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 103 行, 第 57 列
- **错误信息**: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
  属性 "ENDING" 未知

#### 87. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:172

- **规则**: `reportUndefinedVariable`
- **位置**: 第 172 行, 第 24 列
- **错误信息**: "ScriptEventTable" 未定义

#### 88. d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:344

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 344 行, 第 59 列
- **错误信息**: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
  属性 "ENDING" 未知

#### 89. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_core.py:473

- **规则**: `reportOperatorIssue`
- **位置**: 第 473 行, 第 32 列
- **错误信息**: "float" 与 "float | None" 类型不支持 "-" 运算符
  "-" 运算符不支持将 "float" 类型和 "None" 类型计算为目标类型 "ConvertibleToInt"

#### 90. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:164

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 164 行, 第 37 列
- **错误信息**: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
  "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 91. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:168

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 168 行, 第 37 列
- **错误信息**: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
  "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 92. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1004

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1004 行, 第 37 列
- **错误信息**: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
  "List[List[int | str]]" 与 "List[Dict[str, Any]]" 不兼容
    类型参数 "_T@list" 是不变（`Invariant`）的，但 "List[int | str]" 与 "Dict[str, Any]" 不同
    请考虑将 `list` 换成协变的 `Sequence`

#### 93. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1093

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1093 行, 第 21 列
- **错误信息**: 无法访问 "WuwaRecorderUI*" 类的 "set_as_start_events" 属性
  属性 "set_as_start_events" 未知

#### 94. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1114

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1114 行, 第 44 列
- **错误信息**: 无法访问 "ScriptDataModel" 类的 "create_segments_from_selection" 属性
  属性 "create_segments_from_selection" 未知

#### 95. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1147

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1147 行, 第 44 列
- **错误信息**: 无法访问 "ScriptDataModel" 类的 "create_segments_from_selection" 属性
  属性 "create_segments_from_selection" 未知

#### 96. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_script_editor_main.py:32

- **规则**: `reportMissingImports`
- **位置**: 第 32 行, 第 5 列
- **错误信息**: 无法解析导入 "Project_recorder.script_editor"

#### 97. d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_script_editor_main.py:34

- **规则**: `reportMissingImports`
- **位置**: 第 34 行, 第 5 列
- **错误信息**: 无法解析导入 "Project_recorder.script_library"

## ⚠️ 警告详情

共发现 **3** 个警告

1. `d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:125` - "KeyCombination" 已在 `__all__` 中声明，但未在模块中定义 (`reportUnsupportedDunderAll`)
2. `d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:125` - "KeyEventData" 已在 `__all__` 中声明，但未在模块中定义 (`reportUnsupportedDunderAll`)
3. `d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:125` - "MouseEventData" 已在 `__all__` 中声明，但未在模块中定义 (`reportUnsupportedDunderAll`)

## 📁 检查的文件列表

1. `Project_recorder\__init__.py`
2. `Project_recorder\about_dialog.py`
3. `Project_recorder\analysis_dialog.py`
4. `Project_recorder\calculator-1.py`
5. `Project_recorder\character_list_management_dialog.py`
6. `Project_recorder\character_manager.py`
7. `Project_recorder\character_selection_dialog.py`
8. `Project_recorder\color_config.py`
9. `Project_recorder\config_manager.py`
10. `Project_recorder\conflict_detector.py`
11. `Project_recorder\core\application.py`
12. `Project_recorder\core\application_container.py`
13. `Project_recorder\core\application_factory.py`
14. `Project_recorder\core\bootstrap.py`
15. `Project_recorder\core\service_discovery.py`
16. `Project_recorder\cross_platform_color_patch.py`
17. `Project_recorder\dpi_manager.py`
18. `Project_recorder\duplicate_detector.py`
19. `Project_recorder\fix_hardcoded_imports.py`
20. `Project_recorder\fix_imports_clean.py`
21. `Project_recorder\fix_imports_comprehensive.py`
22. `Project_recorder\font_manager.py`
23. `Project_recorder\global_hotkey_manager.py`
24. `Project_recorder\hotkey_config_manager.py`
25. `Project_recorder\hotkey_integration.py`
26. `Project_recorder\hotkey_models.py`
27. `Project_recorder\hotkey_ui.py`
28. `Project_recorder\import_adapter.py`
29. `Project_recorder\material_design_components.py`
30. `Project_recorder\pyinstaller_runtime_hook.py`
31. `Project_recorder\report_generator.py`
32. `Project_recorder\responsive_layout_manager.py`
33. `Project_recorder\script_analyzer.py`
34. `Project_recorder\script_data_manager.py`
35. `Project_recorder\script_data_manager_unified.py`
36. `Project_recorder\script_data_model.py`
37. `Project_recorder\script_data_model_services.py`
38. `Project_recorder\script_data_model_unified.py`
39. `Project_recorder\script_editor_core.py`
40. `Project_recorder\script_file_manager.py`
41. `Project_recorder\script_file_manager_ui.py`
42. `Project_recorder\script_integration_service.py`
43. `Project_recorder\script_migration_service.py`
44. `Project_recorder\script_migration_tool.py`
45. `Project_recorder\script_path_dialog.py`
46. `Project_recorder\script_performance_service.py`
47. `Project_recorder\script_preview_table.py`
48. `Project_recorder\script_service.py`
49. `Project_recorder\script_service_core.py`
50. `Project_recorder\script_services_consolidated.py`
51. `Project_recorder\script_ui_controller.py`
52. `Project_recorder\script_validation_service.py`
53. `Project_recorder\segment_editor.py`
54. `Project_recorder\services\__init__.py`
55. `Project_recorder\services\backup_security_service.py`
56. `Project_recorder\services\character_service.py`
57. `Project_recorder\services\config_service.py`
58. `Project_recorder\services\hotkey_service.py`
59. `Project_recorder\services\input_base.py`
60. `Project_recorder\services\input_events.py`
61. `Project_recorder\services\input_permission_service.py`
62. `Project_recorder\services\input_service.py`
63. `Project_recorder\services\input_types.py`
64. `Project_recorder\services\keyboard_listener_service.py`
65. `Project_recorder\services\log_formatter_service.py`
66. `Project_recorder\services\log_storage_service.py`
67. `Project_recorder\services\logging_service.py`
68. `Project_recorder\services\mouse_listener_service.py`
69. `Project_recorder\services\path_service.py`
70. `Project_recorder\services\performance_monitoring_service.py`
71. `Project_recorder\services\script_data_service.py`
72. `Project_recorder\services\script_library_service.py`
73. `Project_recorder\services\script_migration_service.py`
74. `Project_recorder\services\script_model_service.py`
75. `Project_recorder\services\script_performance_service.py`
76. `Project_recorder\services\script_validation_service.py`
77. `Project_recorder\services\user_communication_service.py`
78. `Project_recorder\services\validation_service.py`
79. `Project_recorder\settings_dialog.py`
80. `Project_recorder\sub_window_manager.py`
81. `Project_recorder\system_tray_manager.py`
82. `Project_recorder\ui\__init__.py`
83. `Project_recorder\ui\compatibility_layer.py`
84. `Project_recorder\ui\components\__init__.py`
85. `Project_recorder\ui\components\cross_platform_color_patch.py`
86. `Project_recorder\ui\components\dpi_manager.py`
87. `Project_recorder\ui\components\font_manager.py`
88. `Project_recorder\ui\components\material_design_components.py`
89. `Project_recorder\ui\components\responsive_layout_manager.py`
90. `Project_recorder\ui\controllers\__init__.py`
91. `Project_recorder\ui\controllers\base_ui_controller.py`
92. `Project_recorder\ui\controllers\library_ui_controller.py`
93. `Project_recorder\ui\controllers\main_ui_controller.py`
94. `Project_recorder\ui\controllers\script_ui_controller.py`
95. `Project_recorder\ui\controllers\timeline_ui_controller.py`
96. `Project_recorder\ui\dialogs\__init__.py`
97. `Project_recorder\ui\dialogs\about_dialog.py`
98. `Project_recorder\ui\dialogs\analysis_dialog.py`
99. `Project_recorder\ui\dialogs\character_list_management_dialog.py`
100. `Project_recorder\ui\dialogs\character_selection_dialog.py`
101. `Project_recorder\ui\dialogs\event_edit_dialog.py`
102. `Project_recorder\ui\dialogs\script_path_dialog.py`
103. `Project_recorder\ui\dialogs\settings_dialog.py`
104. `Project_recorder\ui\dialogs\usage_instruction_dialog.py`
105. `Project_recorder\ui\legacy_adapter.py`
106. `Project_recorder\ui\main_window.py`
107. `Project_recorder\ui\widgets\__init__.py`
108. `Project_recorder\ui\widgets\hotkey_ui.py`
109. `Project_recorder\ui\widgets\script_file_manager_ui.py`
110. `Project_recorder\ui\widgets\script_preview_table.py`
111. `Project_recorder\ui\widgets\segment_editor.py`
112. `Project_recorder\usage_instruction_dialog.py`
113. `Project_recorder\wuwa_recorder.py`
114. `Project_recorder\wuwa_recorder_core.py`
115. `Project_recorder\wuwa_recorder_ui_merged.py`
116. `Project_recorder\wuwa_script_editor_main.py`

## 📄 原始检查输出

```
d:\Python\wuwa_actionseq_recorder\Project_recorder\core\application.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\core\application.py:72:62 - error: "None" 类型的实参无法赋值给函数 "resolve" 中 "type[T@resolve]" 类型的形参 "service_type"
    "None" 类型与 "type[T@resolve]" 类型不兼容 (reportArgumentType)
d:\Python\wuwa_actionseq_recorder\Project_recorder\import_adapter.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\import_adapter.py:35:25 - error: "_MEIPASS" 不是 "sys" 模块的已知属性 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_manager_unified.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_manager_unified.py:474:18 - error: 无法访问 "UnifiedScriptDataManager*" 类的 "mode_changed" 属性
    属性 "mode_changed" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_manager_unified.py:474:41 - error: 无法访问 "UnifiedScriptDataManager*" 类的 "get_mode" 属性
    属性 "get_mode" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model.py:213:32 - error: 无法访问 "ScriptData" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:711:16 - error: "None" 类型不匹配返回类型 "bool"
    "None" 与 "bool" 不兼容 (reportReturnType)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:34:10 - error: 无法解析导入 ".script_event_utils" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:266:25 - error: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
    属性 "edit_history" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:281:40 - error: "EditHistory" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:283:21 - error: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
    属性 "edit_history" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:287:14 - error: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
    属性 "edit_history" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:296:44 - error: 无法访问 "ScriptEditorCore*" 类的 "edit_history" 属性
    属性 "edit_history" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:298:36 - error: 无法访问 "ScriptEditorCore*" 类的 "last_operation" 属性
    属性 "last_operation" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py:298:65 - error: 无法访问 "ScriptEditorCore*" 类的 "last_operation" 属性
    属性 "last_operation" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_integration_service.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_integration_service.py:23:6 - error: 无法解析导入 "Project_recorder.script_event_utils" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_integration_service.py:490:41 - error: 无法访问 "ScriptData" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py:252:32 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:164:28 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:185:27 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:206:28 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:223:29 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:240:28 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:257:28 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_services_consolidated.py:424:18 - error: 无法访问 "ConsolidatedScriptServices*" 类的 "repository" 属性
    属性 "repository" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_ui_controller.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_ui_controller.py:253:72 - error: 需要传入 5 个位置参数 (reportCallIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_ui_controller.py:602:65 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\script_validation_service.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_validation_service.py:157:22 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\script_validation_service.py:158:58 - error: 无法访问 "ScriptEvent" 类的 "event_type" 属性
    属性 "event_type" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:30:24 - error: "QTableWidget" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:54:35 - error: "QTableWidget" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:55:31 - error: "QTableWidget" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:61:40 - error: "QHeaderView" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:62:40 - error: "QHeaderView" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:63:40 - error: "QHeaderView" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:64:40 - error: "QHeaderView" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:65:40 - error: "QHeaderView" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:140:34 - error: "QTableWidgetItem" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:143:25 - error: "QTableWidgetItem" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:148:34 - error: "QTableWidgetItem" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:151:34 - error: "QTableWidgetItem" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:155:34 - error: "QTableWidgetItem" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:217:26 - error: "cast" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:242:34 - error: "cast" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:283:26 - error: "cast" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:297:29 - error: "UndoRedoManager" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:370:29 - error: "QTableWidget" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:405:54 - error: 无法访问 "ScriptEditor*" 类的 "on_event_selected" 属性
    属性 "on_event_selected" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:412:59 - error: 无法访问 "ScriptEditor*" 类的 "on_operation_executed" 属性
    属性 "on_operation_executed" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:413:56 - error: 无法访问 "ScriptEditor*" 类的 "update_history_display" 属性
    属性 "update_history_display" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:416:51 - error: 无法访问 "ScriptEditor*" 类的 "auto_save" 属性
    属性 "auto_save" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:424:14 - error: 无法访问 "ScriptEditor*" 类的 "update_info_display" 属性
    属性 "update_info_display" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:548:18 - error: "ScriptValidator" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:565:14 - error: 无法访问 "ScriptEditor*" 类的 "update_info_display" 属性
    属性 "update_info_display" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:593:58 - error: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
    属性 "ENDING" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:802:57 - error: 无法访问 "ScriptData" 类的 "is_segmented" 属性
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:824:60 - error: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
    属性 "ENDING" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1003:41 - error: 无法访问 "ScriptData" 类的 "is_segmented" 属性
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1023:57 - error: 无法访问 "ScriptData" 类的 "is_segmented" 属性
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1167:53 - error: 无法访问 "ScriptData" 类的 "is_segmented" 属性
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1194:34 - error: 无法为 "ScriptData" 类的 "is_segmented" 属性赋值
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1206:57 - error: 无法访问 "ScriptData" 类的 "is_segmented" 属性
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1227:34 - error: 无法为 "ScriptData" 类的 "is_segmented" 属性赋值
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\segment_editor.py:1239:57 - error: 无法访问 "ScriptData" 类的 "is_segmented" 属性
    属性 "is_segmented" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:125:5 - warning: "KeyCombination" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:125:37 - warning: "KeyEventData" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:125:53 - warning: "MouseEventData" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py:547:12 - error: "is_segmented" 未定义 (reportUndefinedVariable)
d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:235:17 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:246:17 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:259:17 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:282:26 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:285:17 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338:13 - error: "mode" 参数不存在 (reportCallIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:338:23 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:342:17 - error: 无法访问 "ScriptDataModel*" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:498:18 - error: 无法访问 "ScriptDataModel" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:536:18 - error: 无法访问 "ScriptDataModel" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:549:27 - error: 无法访问 "ScriptDataModel" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\services\script_model_service.py:630:27 - error: 无法访问 "ScriptDataModel" 类的 "mode" 属性
    属性 "mode" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\main_window.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\main_window.py:341:37 - error: 无法访问 "MainUIController" 类的 "is_developer_mode_enabled" 属性
    属性 "is_developer_mode_enabled" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:41:72 - error: "EditOperation" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:43:14 - error: 无法解析导入 "Project_recorder.undo_redo_manager" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:48:76 - error: "EditOperation" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:50:18 - error: 无法解析导入 "undo_redo_manager" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:67:76 - error: "EditOperation" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:69:18 - error: 无法解析导入 "Project_recorder.undo_redo_manager" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:73:76 - error: "EditOperation" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:75:18 - error: 无法解析导入 "undo_redo_manager" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:103:58 - error: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
    属性 "ENDING" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:172:25 - error: "ScriptEventTable" 未定义 (reportUndefinedVariable)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\ui\widgets\segment_editor.py:344:60 - error: 无法访问 "type[ScriptSegmentType]" 类的 "ENDING" 属性
    属性 "ENDING" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_core.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_core.py:473:33 - error: "float" 与 "float | None" 类型不支持 "-" 运算符
    "-" 运算符不支持将 "float" 类型和 "None" 类型计算为目标类型 "ConvertibleToInt" (reportOperatorIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:164:38 - error: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
    "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:168:38 - error: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
    "List[ScriptEvent]" 与 "List[Dict[str, Any]]" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "ScriptEvent" 与 "Dict[str, Any]" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1004:38 - error: 无法为 "WuwaRecorderUI*" 类的 "script_events" 属性赋值
    "List[List[int | str]]" 与 "List[Dict[str, Any]]" 不兼容
      类型参数 "_T@list" 是不变（`Invariant`）的，但 "List[int | str]" 与 "Dict[str, Any]" 不同
      请考虑将 `list` 换成协变的 `Sequence` (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1093:22 - error: 无法访问 "WuwaRecorderUI*" 类的 "set_as_start_events" 属性
    属性 "set_as_start_events" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1114:45 - error: 无法访问 "ScriptDataModel" 类的 "create_segments_from_selection" 属性
    属性 "create_segments_from_selection" 未知 (reportAttributeAccessIssue)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_recorder_ui_merged.py:1147:45 - error: 无法访问 "ScriptDataModel" 类的 "create_segments_from_selection" 属性
    属性 "create_segments_from_selection" 未知 (reportAttributeAccessIssue)
d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_script_editor_main.py
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_script_editor_main.py:32:6 - error: 无法解析导入 "Project_recorder.script_editor" (reportMissingImports)
  d:\Python\wuwa_actionseq_recorder\Project_recorder\wuwa_script_editor_main.py:34:6 - error: 无法解析导入 "Project_recorder.script_library" (reportMissingImports)
97 errors, 3 warnings, 0 notes
```

