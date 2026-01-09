# BasedPyright 检查报告
**生成时间**: 2025-12-17 13:06:55
**检查时间**: 2025-12-17T13:06:55.165547
**检查目录**: `Project_recorder`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 189 |
| ❌ 错误 (Error) | 21 |
| ⚠️ 警告 (Warning) | 3 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 3.88 秒 |

## 🔴 错误详情

共发现 **21** 个错误

### 按文件分组

- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_editor_core.py`: 11 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_migration_service.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_performance_service.py`: 3 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\export_encrypted_script.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py`: 1 个错误

### 按规则分组

- `reportAttributeAccessIssue`: 12 次
- `reportAssignmentType`: 2 次
- `reportIndexIssue`: 2 次
- `reportUndefinedVariable`: 2 次
- `reportArgumentType`: 1 次
- `reportOperatorIssue`: 1 次
- `reportMissingImports`: 1 次

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

#### 20. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py:45

- **规则**: `reportMissingImports`
- **位置**: 第 45 行, 第 9 列
- **错误信息**: 无法解析导入 "services.infrastructure.event_manager"

#### 21. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py:117

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 117 行, 第 11 列
- **错误信息**: 无法为 "WuwaRecorderUI" 类的 "logger" 属性赋值
  无法将 "None" 类型的表达式赋值给 "WuwaRecorderUI" 类的 "logger" 属性
    "None" 与 "Logger" 不兼容

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
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176:5 - warning: "KeyCombination" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176:37 - warning: "KeyEventData" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\__init__.py:176:53 - warning: "MouseEventData" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\services\script_migration_service.py:45:10 - error: 无法解析导入 "services.infrastructure.event_manager" (reportMissingImports)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py:117:12 - error: 无法为 "WuwaRecorderUI" 类的 "logger" 属性赋值
    无法将 "None" 类型的表达式赋值给 "WuwaRecorderUI" 类的 "logger" 属性
      "None" 与 "Logger" 不兼容 (reportAttributeAccessIssue)
21 errors, 3 warnings, 0 notes
```

