# BasedPyright 检查报告
**生成时间**: 2025-12-20 12:11:39
**检查时间**: 2025-12-20T12:11:39.163088
**检查目录**: `Project_recorder`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 183 |
| ❌ 错误 (Error) | 11 |
| ⚠️ 警告 (Warning) | 1 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 3.81 秒 |

## 🔴 错误详情

共发现 **11** 个错误

### 按文件分组

- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\controllers\main_ui_controller.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py`: 1 个错误

### 按规则分组

- `reportOptionalMemberAccess`: 4 次
- `reportArgumentType`: 3 次
- `reportCallIssue`: 2 次
- `reportAttributeAccessIssue`: 2 次

### 详细错误列表

#### 1. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:748

- **规则**: `reportCallIssue`
- **位置**: 第 748 行, 第 12 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 2. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:748

- **规则**: `reportArgumentType`
- **位置**: 第 748 行, 第 12 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
  "int | None" 类型与 "SupportsIndex" 类型不兼容
    "None" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在

#### 3. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:752

- **规则**: `reportCallIssue`
- **位置**: 第 752 行, 第 12 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 4. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:752

- **规则**: `reportArgumentType`
- **位置**: 第 752 行, 第 12 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
  "int | None" 类型与 "SupportsIndex" 类型不兼容
    "None" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在

#### 5. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py:179

- **规则**: `reportArgumentType`
- **位置**: 第 179 行, 第 39 列
- **错误信息**: "QTreeWidget" 类型的实参无法赋值给函数 "find_event_items" 中 "SegmentTreeItem" 类型的形参 "segment_item"
  "QTreeWidget" 与 "SegmentTreeItem" 不兼容

#### 6. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\controllers\main_ui_controller.py:181

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 181 行, 第 55 列
- **错误信息**: 无法访问 "ScriptUIController" 类的 "get_preview_component" 属性
  属性 "get_preview_component" 未知

#### 7. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\controllers\main_ui_controller.py:466

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 466 行, 第 47 列
- **错误信息**: 无法访问 "ScriptUIController" 类的 "get_preview_component" 属性
  属性 "get_preview_component" 未知

#### 8. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1471

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1471 行, 第 62 列
- **错误信息**: `None` 没有 "find_event_location" 属性

#### 9. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1477

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1477 行, 第 51 列
- **错误信息**: `None` 没有 "remove_event" 属性

#### 10. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1510

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1510 行, 第 93 列
- **错误信息**: `None` 没有 "segments" 属性

#### 11. d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1513

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1513 行, 第 93 列
- **错误信息**: `None` 没有 "segments" 属性

## ⚠️ 警告详情

共发现 **1** 个警告

1. `d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\utils\encryption_helper.py:36` - 不允许使用通配符（`*`）从库中导入 (`reportWildcardImportFromLibrary`)

## 📁 检查的文件列表

1. `Project_recorder\__init__.py`
2. `Project_recorder\about_dialog.py`
3. `Project_recorder\analysis_dialog.py`
4. `Project_recorder\calculator-1.py`
5. `Project_recorder\character_list_management_dialog.py`
6. `Project_recorder\character_manager.py`
7. `Project_recorder\character_selection_dialog.py`
8. `Project_recorder\cleanup_legacy_services.py`
9. `Project_recorder\color_config.py`
10. `Project_recorder\config\validation_rules.py`
11. `Project_recorder\config_manager.py`
12. `Project_recorder\conflict_detector.py`
13. `Project_recorder\convert_to_absolute_imports.py`
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
24. `Project_recorder\dist\wuwa_recorder.build\scons-debug.py`
25. `Project_recorder\dist\wuwa_recorder.dist\config\validation_rules.py`
26. `Project_recorder\dpi_manager.py`
27. `Project_recorder\duplicate_detector.py`
28. `Project_recorder\export_encrypted_script.py`
29. `Project_recorder\font_manager.py`
30. `Project_recorder\global_hotkey_manager.py`
31. `Project_recorder\hotkey_config_manager.py`
32. `Project_recorder\hotkey_integration.py`
33. `Project_recorder\hotkey_models.py`
34. `Project_recorder\hotkey_ui.py`
35. `Project_recorder\material_design_components.py`
36. `Project_recorder\release\config\validation_rules.py`
37. `Project_recorder\report_generator.py`
38. `Project_recorder\responsive_layout_manager.py`
39. `Project_recorder\restore_backups.py`
40. `Project_recorder\script_analyzer.py`
41. `Project_recorder\script_data_manager.py`
42. `Project_recorder\script_data_manager_unified.py`
43. `Project_recorder\script_data_model.py`
44. `Project_recorder\script_data_model_services.py`
45. `Project_recorder\script_data_model_unified.py`
46. `Project_recorder\script_editor_core.py`
47. `Project_recorder\script_event_utils.py`
48. `Project_recorder\script_file_manager.py`
49. `Project_recorder\script_file_manager_ui.py`
50. `Project_recorder\script_integration_service.py`
51. `Project_recorder\script_path_dialog.py`
52. `Project_recorder\script_performance_service.py`
53. `Project_recorder\script_service.py`
54. `Project_recorder\script_service_core.py`
55. `Project_recorder\script_services_consolidated.py`
56. `Project_recorder\script_ui_controller.py`
57. `Project_recorder\script_validation_service.py`
58. `Project_recorder\segment_editor.py`
59. `Project_recorder\services\__init__.py`
60. `Project_recorder\services\adapters\__init__.py`
61. `Project_recorder\services\adapters\script_data_access_adapter.py`
62. `Project_recorder\services\adapters\script_integration_adapter.py`
63. `Project_recorder\services\adapters\script_performance_adapter.py`
64. `Project_recorder\services\backup_security_service.py`
65. `Project_recorder\services\character_service.py`
66. `Project_recorder\services\config_service.py`
67. `Project_recorder\services\hotkey_service.py`
68. `Project_recorder\services\infrastructure\__init__.py`
69. `Project_recorder\services\infrastructure\cache_manager.py`
70. `Project_recorder\services\infrastructure\config_manager.py`
71. `Project_recorder\services\infrastructure\logging_manager.py`
72. `Project_recorder\services\infrastructure\logging_manager_unified.py`
73. `Project_recorder\services\infrastructure\performance_monitor.py`
74. `Project_recorder\services\input_base.py`
75. `Project_recorder\services\input_events.py`
76. `Project_recorder\services\input_permission_service.py`
77. `Project_recorder\services\input_service.py`
78. `Project_recorder\services\input_types.py`
79. `Project_recorder\services\keyboard_listener_service.py`
80. `Project_recorder\services\log_formatter_service.py`
81. `Project_recorder\services\log_storage_service.py`
82. `Project_recorder\services\logging_service.py`
83. `Project_recorder\services\mouse_listener_service.py`
84. `Project_recorder\services\path_service.py`
85. `Project_recorder\services\performance_monitoring_service.py`
86. `Project_recorder\services\script_data_service.py`
87. `Project_recorder\services\script_library_service.py`
88. `Project_recorder\services\script_migration_service.py`
89. `Project_recorder\services\script_model_service.py`
90. `Project_recorder\services\script_performance_service.py`
91. `Project_recorder\services\segment_editor_service.py`
92. `Project_recorder\services\unified_script_service.py`
93. `Project_recorder\services\user_communication_service.py`
94. `Project_recorder\services\validation_service.py`
95. `Project_recorder\settings_dialog.py`
96. `Project_recorder\sub_window_manager.py`
97. `Project_recorder\system_tray_manager.py`
98. `Project_recorder\test_delete_functionality.py`
99. `Project_recorder\test_fixes.py`
100. `Project_recorder\ui\__init__.py`
101. `Project_recorder\ui\compatibility_layer.py`
102. `Project_recorder\ui\components\__init__.py`
103. `Project_recorder\ui\components\cross_platform_color_patch.py`
104. `Project_recorder\ui\components\dpi_manager.py`
105. `Project_recorder\ui\components\font_manager.py`
106. `Project_recorder\ui\components\material_design_components.py`
107. `Project_recorder\ui\components\responsive_layout_manager.py`
108. `Project_recorder\ui\controllers\__init__.py`
109. `Project_recorder\ui\controllers\base_ui_controller.py`
110. `Project_recorder\ui\controllers\library_ui_controller.py`
111. `Project_recorder\ui\controllers\main_ui_controller.py`
112. `Project_recorder\ui\controllers\script_ui_controller.py`
113. `Project_recorder\ui\controllers\segment_editor_controller.py`
114. `Project_recorder\ui\controllers\timeline_ui_controller.py`
115. `Project_recorder\ui\dialogs\__init__.py`
116. `Project_recorder\ui\dialogs\about_dialog.py`
117. `Project_recorder\ui\dialogs\analysis_dialog.py`
118. `Project_recorder\ui\dialogs\character_list_management_dialog.py`
119. `Project_recorder\ui\dialogs\character_selection_dialog.py`
120. `Project_recorder\ui\dialogs\event_edit_dialog.py`
121. `Project_recorder\ui\dialogs\event_edit_dialog_enhanced.py`
122. `Project_recorder\ui\dialogs\script_path_dialog.py`
123. `Project_recorder\ui\dialogs\segment_edit_dialog.py`
124. `Project_recorder\ui\dialogs\settings_dialog.py`
125. `Project_recorder\ui\dialogs\settings_dialog_fixed.py`
126. `Project_recorder\ui\dialogs\usage_instruction_dialog.py`
127. `Project_recorder\ui\legacy_adapter.py`
128. `Project_recorder\ui\main_window.py`
129. `Project_recorder\ui\main_window_styled.py`
130. `Project_recorder\ui\styles\__init__.py`
131. `Project_recorder\ui\styles\components\__init__.py`
132. `Project_recorder\ui\styles\components\button_styles.py`
133. `Project_recorder\ui\styles\components\card_styles.py`
134. `Project_recorder\ui\styles\components\dialog_styles.py`
135. `Project_recorder\ui\styles\components\input_style_cache.py`
136. `Project_recorder\ui\styles\components\input_styles.py`
137. `Project_recorder\ui\styles\components\label_styles.py`
138. `Project_recorder\ui\styles\components\responsive_input_scaler.py`
139. `Project_recorder\ui\styles\layouts\__init__.py`
140. `Project_recorder\ui\styles\layouts\form_layouts.py`
141. `Project_recorder\ui\styles\layouts\grid_layouts.py`
142. `Project_recorder\ui\styles\layouts\main_window_layouts.py`
143. `Project_recorder\ui\styles\layouts\responsive_layouts.py`
144. `Project_recorder\ui\styles\main_window\__init__.py`
145. `Project_recorder\ui\styles\main_window\control_panel_styles.py`
146. `Project_recorder\ui\styles\main_window\main_window_styles.py`
147. `Project_recorder\ui\styles\main_window\preview_panel_styles.py`
148. `Project_recorder\ui\styles\main_window\recording_panel_styles.py`
149. `Project_recorder\ui\styles\styles_manager.py`
150. `Project_recorder\ui\styles\themes\__init__.py`
151. `Project_recorder\ui\styles\themes\color_system.py`
152. `Project_recorder\ui\styles\themes\material_theme.py`
153. `Project_recorder\ui\styles\themes\theme_manager.py`
154. `Project_recorder\ui\widgets\__init__.py`
155. `Project_recorder\ui\widgets\base_event_table.py`
156. `Project_recorder\ui\widgets\hotkey_ui.py`
157. `Project_recorder\ui\widgets\script_event_table.py`
158. `Project_recorder\ui\widgets\script_file_manager_ui.py`
159. `Project_recorder\ui\widgets\script_preview_tree.py`
160. `Project_recorder\ui\widgets\script_preview_tree_phase2.py`
161. `Project_recorder\ui\widgets\segment_event_table.py`
162. `Project_recorder\ui\widgets\segment_properties_dialog.py`
163. `Project_recorder\ui\widgets\tree_items.py`
164. `Project_recorder\undo_redo_manager.py`
165. `Project_recorder\usage_instruction_dialog.py`
166. `Project_recorder\utils\__init__.py`
167. `Project_recorder\utils\encryption_helper.py`
168. `Project_recorder\utils\ui_helpers.py`
169. `Project_recorder\validate_fix.py`
170. `Project_recorder\validators\__init__.py`
171. `Project_recorder\validators\base_validator.py`
172. `Project_recorder\validators\consistency_validator.py`
173. `Project_recorder\validators\event_validator.py`
174. `Project_recorder\validators\event_validator_broken.py`
175. `Project_recorder\validators\metadata_validator.py`
176. `Project_recorder\validators\segment_validator.py`
177. `Project_recorder\validators\validation_types.py`
178. `Project_recorder\wuwa_recorder.build\scons-debug.py`
179. `Project_recorder\wuwa_recorder.onefile-build\scons-debug.py`
180. `Project_recorder\wuwa_recorder.py`
181. `Project_recorder\wuwa_recorder_core.py`
182. `Project_recorder\wuwa_recorder_ui_merged.py`
183. `Project_recorder\wuwa_script_editor_main.py`

## 📄 原始检查输出

```
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:748:13 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:748:13 - error: "int | None" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
    "int | None" 类型与 "SupportsIndex" 类型不兼容
      "None" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:752:13 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\script_data_model_unified.py:752:13 - error: "int | None" 类型的实参无法赋值给函数 "__setitem__" 中 "SupportsIndex" 类型的形参 "key"
    "int | None" 类型与 "SupportsIndex" 类型不兼容
      "None" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\test_fixes.py:179:40 - error: "QTreeWidget" 类型的实参无法赋值给函数 "find_event_items" 中 "SegmentTreeItem" 类型的形参 "segment_item"
    "QTreeWidget" 与 "SegmentTreeItem" 不兼容 (reportArgumentType)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\controllers\main_ui_controller.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\controllers\main_ui_controller.py:181:56 - error: 无法访问 "ScriptUIController" 类的 "get_preview_component" 属性
    属性 "get_preview_component" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\controllers\main_ui_controller.py:466:48 - error: 无法访问 "ScriptUIController" 类的 "get_preview_component" 属性
    属性 "get_preview_component" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1471:63 - error: `None` 没有 "find_event_location" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1477:52 - error: `None` 没有 "remove_event" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1510:94 - error: `None` 没有 "segments" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\ui\widgets\script_preview_tree.py:1513:94 - error: `None` 没有 "segments" 属性 (reportOptionalMemberAccess)
d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\utils\encryption_helper.py
  d:\GITHUB\wuwa_actionseq_recorder\Project_recorder\utils\encryption_helper.py:36:31 - warning: 不允许使用通配符（`*`）从库中导入 (reportWildcardImportFromLibrary)
11 errors, 1 warning, 0 notes
```

