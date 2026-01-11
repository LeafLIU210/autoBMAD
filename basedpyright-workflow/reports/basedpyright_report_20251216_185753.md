# BasedPyright 检查报告
**生成时间**: 2025-12-16 18:57:53
**检查时间**: 2025-12-16T18:57:53.553879
**检查目录**: `src`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 34 |
| ❌ 错误 (Error) | 196 |
| ⚠️ 警告 (Warning) | 1603 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.05 秒 |

## 🔴 错误详情

共发现 **196** 个错误

### 按文件分组

- `d:\GITHUB\wuwa_actionseq_player\src\main.py`: 126 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py`: 14 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py`: 11 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py`: 7 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py`: 6 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py`: 6 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py`: 5 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py`: 4 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py`: 3 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py`: 2 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py`: 1 个错误
- `d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py`: 1 个错误

### 按规则分组

- `reportOptionalMemberAccess`: 80 次
- `reportAttributeAccessIssue`: 32 次
- `reportImplicitRelativeImport`: 26 次
- `reportArgumentType`: 23 次
- `reportMissingTypeArgument`: 14 次
- `reportUninitializedInstanceVariable`: 4 次
- `reportAssignmentType`: 4 次
- `reportOptionalCall`: 4 次
- `reportConstantRedefinition`: 3 次
- `reportMissingImports`: 3 次
- `reportGeneralTypeIssues`: 1 次
- `reportOperatorIssue`: 1 次
- `reportCallIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:54

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 54 行, 第 51 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 2. d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:139

- **规则**: `reportArgumentType`
- **位置**: 第 139 行, 第 83 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "Exception" 类型的参数
  "None" 与 "Exception" 不兼容

#### 3. d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:163

- **规则**: `reportArgumentType`
- **位置**: 第 163 行, 第 53 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "Exception" 类型的参数
  "None" 与 "Exception" 不兼容

#### 4. d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:375

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 375 行, 第 33 列
- **错误信息**: 无法为 "type[EnhancedErrorHandler]" 类的 "_instance" 属性赋值
  属性 "_instance" 未知

#### 5. d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:376

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 376 行, 第 36 列
- **错误信息**: 无法访问 "type[EnhancedErrorHandler]" 类的 "_instance" 属性
  属性 "_instance" 未知

#### 6. d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:165

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 165 行, 第 49 列
- **错误信息**: "Callable" 泛型类应有类型参数

#### 7. d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:223

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 223 行, 第 47 列
- **错误信息**: 此处应为类而非 "(iterable: Iterable[object], /) -> bool"

#### 8. d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:304

- **规则**: `reportUninitializedInstanceVariable`
- **位置**: 第 304 行, 第 17 列
- **错误信息**: 实例变量 "_progress_bounds" 未在类体或 `__init__` 方法中初始化

#### 9. d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:321

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 321 行, 第 44 列
- **错误信息**: "Callable" 泛型类应有类型参数

#### 10. d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:330

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 330 行, 第 43 列
- **错误信息**: "Callable" 泛型类应有类型参数

#### 11. d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:106

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 106 行, 第 31 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 12. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:259

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 259 行, 第 33 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 13. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:311

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 311 行, 第 45 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 14. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:130

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 130 行, 第 59 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 15. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:154

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 154 行, 第 40 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 16. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:209

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 209 行, 第 47 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 17. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:249

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 249 行, 第 41 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 18. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:293

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 293 行, 第 38 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 19. d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:317

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 317 行, 第 45 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 20. d:\GITHUB\wuwa_actionseq_player\src\main.py:23

- **规则**: `reportConstantRedefinition`
- **位置**: 第 23 行, 第 4 列
- **错误信息**: 不能重新定义常量 "APPLICATION_PATH"（全大写名称）

#### 21. d:\GITHUB\wuwa_actionseq_player\src\main.py:72

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 72 行, 第 9 列
- **错误信息**: 从 "system_services.cross_platform_color_patch" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.cross_platform_color_patch" 作为相对导入
  或指定完整模块路径："src.system_services.cross_platform_color_patch"

#### 22. d:\GITHUB\wuwa_actionseq_player\src\main.py:73

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 73 行, 第 9 列
- **错误信息**: 从 "system_services.decryption_service" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.decryption_service" 作为相对导入
  或指定完整模块路径："src.system_services.decryption_service"

#### 23. d:\GITHUB\wuwa_actionseq_player\src\main.py:74

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 74 行, 第 9 列
- **错误信息**: 从 "models.enums" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".models.enums" 作为相对导入
  或指定完整模块路径："src.models.enums"

#### 24. d:\GITHUB\wuwa_actionseq_player\src\main.py:75

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 75 行, 第 9 列
- **错误信息**: 从 "models.script_action" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".models.script_action" 作为相对导入
  或指定完整模块路径："src.models.script_action"

#### 25. d:\GITHUB\wuwa_actionseq_player\src\main.py:76

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 76 行, 第 9 列
- **错误信息**: 从 "models.validation_models" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".models.validation_models" 作为相对导入
  或指定完整模块路径："src.models.validation_models"

#### 26. d:\GITHUB\wuwa_actionseq_player\src\main.py:77

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 77 行, 第 9 列
- **错误信息**: 从 "models.script_metadata" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".models.script_metadata" 作为相对导入
  或指定完整模块路径："src.models.script_metadata"

#### 27. d:\GITHUB\wuwa_actionseq_player\src\main.py:78

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 78 行, 第 9 列
- **错误信息**: 从 "business_logic.script_validator" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.script_validator" 作为相对导入
  或指定完整模块路径："src.business_logic.script_validator"

#### 28. d:\GITHUB\wuwa_actionseq_player\src\main.py:79

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 79 行, 第 9 列
- **错误信息**: 从 "business_logic.state_manager" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.state_manager" 作为相对导入
  或指定完整模块路径："src.business_logic.state_manager"

#### 29. d:\GITHUB\wuwa_actionseq_player\src\main.py:80

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 80 行, 第 9 列
- **错误信息**: 从 "business_logic.action_matcher" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.action_matcher" 作为相对导入
  或指定完整模块路径："src.business_logic.action_matcher"

#### 30. d:\GITHUB\wuwa_actionseq_player\src\main.py:81

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 81 行, 第 9 列
- **错误信息**: 从 "business_logic.script_player_engine" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.script_player_engine" 作为相对导入
  或指定完整模块路径："src.business_logic.script_player_engine"

#### 31. d:\GITHUB\wuwa_actionseq_player\src\main.py:82

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 82 行, 第 9 列
- **错误信息**: 从 "business_logic.character_mapper" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.character_mapper" 作为相对导入
  或指定完整模块路径："src.business_logic.character_mapper"

#### 32. d:\GITHUB\wuwa_actionseq_player\src\main.py:83

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 83 行, 第 9 列
- **错误信息**: 从 "business_logic.metadata_manager" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.metadata_manager" 作为相对导入
  或指定完整模块路径："src.business_logic.metadata_manager"

#### 33. d:\GITHUB\wuwa_actionseq_player\src\main.py:84

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 84 行, 第 9 列
- **错误信息**: 从 "ui.metadata_display_widget" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".ui.metadata_display_widget" 作为相对导入
  或指定完整模块路径："src.ui.metadata_display_widget"

#### 34. d:\GITHUB\wuwa_actionseq_player\src\main.py:85

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 85 行, 第 9 列
- **错误信息**: 从 "ui.enhanced_file_dialog" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".ui.enhanced_file_dialog" 作为相对导入
  或指定完整模块路径："src.ui.enhanced_file_dialog"

#### 35. d:\GITHUB\wuwa_actionseq_player\src\main.py:86

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 86 行, 第 9 列
- **错误信息**: 从 "ui.format_indicator_widget" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".ui.format_indicator_widget" 作为相对导入
  或指定完整模块路径："src.ui.format_indicator_widget"

#### 36. d:\GITHUB\wuwa_actionseq_player\src\main.py:87

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 87 行, 第 9 列
- **错误信息**: 从 "ui.widgets.script_preview" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".ui.widgets.script_preview" 作为相对导入
  或指定完整模块路径："src.ui.widgets.script_preview"

#### 37. d:\GITHUB\wuwa_actionseq_player\src\main.py:88

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 88 行, 第 9 列
- **错误信息**: 从 "business_logic.script_format_detector" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.script_format_detector" 作为相对导入
  或指定完整模块路径："src.business_logic.script_format_detector"

#### 38. d:\GITHUB\wuwa_actionseq_player\src\main.py:89

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 89 行, 第 9 列
- **错误信息**: 从 "business_logic.loading_state_manager" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.loading_state_manager" 作为相对导入
  或指定完整模块路径："src.business_logic.loading_state_manager"

#### 39. d:\GITHUB\wuwa_actionseq_player\src\main.py:90

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 90 行, 第 9 列
- **错误信息**: 从 "business_logic.error_handler" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".business_logic.error_handler" 作为相对导入
  或指定完整模块路径："src.business_logic.error_handler"

#### 40. d:\GITHUB\wuwa_actionseq_player\src\main.py:91

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 91 行, 第 9 列
- **错误信息**: 从 "models.enums" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".models.enums" 作为相对导入
  或指定完整模块路径："src.models.enums"

#### 41. d:\GITHUB\wuwa_actionseq_player\src\main.py:274

- **规则**: `reportOperatorIssue`
- **位置**: 第 274 行, 第 20 列
- **错误信息**: "int | Unknown | str | None" 与 "int" 类型不支持 "+=" 运算符
  "str" 与 "int" 类型不支持 "+" 运算符
  "None" 与 "int" 类型不支持 "+" 运算符

#### 42. d:\GITHUB\wuwa_actionseq_player\src\main.py:309

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 309 行, 第 21 列
- **错误信息**: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.color_config" 作为相对导入
  或指定完整模块路径："src.system_services.color_config"

#### 43. d:\GITHUB\wuwa_actionseq_player\src\main.py:363

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 363 行, 第 27 列
- **错误信息**: 无法访问 "QObject" 类的 "color_manager" 属性
  属性 "color_manager" 未知

#### 44. d:\GITHUB\wuwa_actionseq_player\src\main.py:375

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 375 行, 第 27 列
- **错误信息**: 无法访问 "QObject" 类的 "color_manager" 属性
  属性 "color_manager" 未知

#### 45. d:\GITHUB\wuwa_actionseq_player\src\main.py:593

- **规则**: `reportArgumentType`
- **位置**: 第 593 行, 第 51 列
- **错误信息**: "(state: LoadingState, message: str, progress: int) -> None" 类型的实参无法赋值给函数 "add_progress_callback" 中 "(LoadingState, int, str) -> None" 类型的形参 "callback"
  "(state: LoadingState, message: str, progress: int) -> None" 类型与 "(LoadingState, int, str) -> None" 类型不兼容
    第 2 个参数："int" 类型与 "str" 类型不兼容
      "int" 与 "str" 不兼容
    第 3 个参数："str" 类型与 "int" 类型不兼容
      "str" 与 "int" 不兼容

#### 46. d:\GITHUB\wuwa_actionseq_player\src\main.py:885

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 885 行, 第 25 列
- **错误信息**: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.color_config" 作为相对导入
  或指定完整模块路径："src.system_services.color_config"

#### 47. d:\GITHUB\wuwa_actionseq_player\src\main.py:960

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 960 行, 第 29 列
- **错误信息**: 无法为 "ScriptPlayer*" 类的 "loop_checkbox" 属性赋值
  "QPushButton" 类型与 "QCheckBox | None" 类型不兼容
    "QPushButton" 与 "QCheckBox" 不兼容
    "QPushButton" 与 "None" 不兼容

#### 48. d:\GITHUB\wuwa_actionseq_player\src\main.py:961

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 961 行, 第 27 列
- **错误信息**: `None` 没有 "setCheckable" 属性

#### 49. d:\GITHUB\wuwa_actionseq_player\src\main.py:962

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 962 行, 第 27 列
- **错误信息**: `None` 没有 "setChecked" 属性

#### 50. d:\GITHUB\wuwa_actionseq_player\src\main.py:963

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 963 行, 第 27 列
- **错误信息**: `None` 没有 "clicked" 属性

#### 51. d:\GITHUB\wuwa_actionseq_player\src\main.py:965

- **规则**: `reportArgumentType`
- **位置**: 第 965 行, 第 30 列
- **错误信息**: "QCheckBox | None" 类型的实参无法赋值给函数 "addWidget" 中 "QWidget" 类型的形参 "arg__1"
  "QCheckBox | None" 类型与 "QWidget" 类型不兼容
    "None" 与 "QWidget" 不兼容

#### 52. d:\GITHUB\wuwa_actionseq_player\src\main.py:1077

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 1077 行, 第 21 列
- **错误信息**: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.color_config" 作为相对导入
  或指定完整模块路径："src.system_services.color_config"

#### 53. d:\GITHUB\wuwa_actionseq_player\src\main.py:1527

- **规则**: `reportUninitializedInstanceVariable`
- **位置**: 第 1527 行, 第 17 列
- **错误信息**: 实例变量 "_last_space_check" 未在类体或 `__init__` 方法中初始化

#### 54. d:\GITHUB\wuwa_actionseq_player\src\main.py:1667

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1667 行, 第 34 列
- **错误信息**: `None` 没有 "show_loading_state" 属性

#### 55. d:\GITHUB\wuwa_actionseq_player\src\main.py:1669

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1669 行, 第 34 列
- **错误信息**: `None` 没有 "show_loading_state" 属性

#### 56. d:\GITHUB\wuwa_actionseq_player\src\main.py:1671

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1671 行, 第 34 列
- **错误信息**: `None` 没有 "show_loading_state" 属性

#### 57. d:\GITHUB\wuwa_actionseq_player\src\main.py:1673

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1673 行, 第 34 列
- **错误信息**: `None` 没有 "show_loading_state" 属性

#### 58. d:\GITHUB\wuwa_actionseq_player\src\main.py:1701

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1701 行, 第 30 列
- **错误信息**: `None` 没有 "show_error_state" 属性

#### 59. d:\GITHUB\wuwa_actionseq_player\src\main.py:1704

- **规则**: `reportArgumentType`
- **位置**: 第 1704 行, 第 51 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "show_error_dialog" 中 "ErrorType" 类型的形参 "error_type"
  "str" 与 "ErrorType" 不兼容

#### 60. d:\GITHUB\wuwa_actionseq_player\src\main.py:1730

- **规则**: `reportArgumentType`
- **位置**: 第 1730 行, 第 20 列
- **错误信息**: "Literal['不支持的文件格式']" 类型的实参无法赋值给函数 "show_error_dialog" 中 "ErrorType" 类型的形参 "error_type"
  "Literal['不支持的文件格式']" 与 "ErrorType" 不兼容

#### 61. d:\GITHUB\wuwa_actionseq_player\src\main.py:1731

- **规则**: `reportArgumentType`
- **位置**: 第 1731 行, 第 20 列
- **错误信息**: "Literal['请选择 .json 或 .wuwa_enc 格式的脚本文件']" 类型的实参无法赋值给函数 "show_error_dialog" 中 "Exception" 类型的形参 "original_error"
  "Literal['请选择 .json 或 .wuwa_enc 格式的脚本文件']" 与 "Exception" 不兼容

#### 62. d:\GITHUB\wuwa_actionseq_player\src\main.py:1736

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1736 行, 第 34 列
- **错误信息**: `None` 没有 "update_format" 属性

#### 63. d:\GITHUB\wuwa_actionseq_player\src\main.py:1747

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1747 行, 第 42 列
- **错误信息**: `None` 没有 "show_error_state" 属性

#### 64. d:\GITHUB\wuwa_actionseq_player\src\main.py:1753

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1753 行, 第 42 列
- **错误信息**: `None` 没有 "show_error_state" 属性

#### 65. d:\GITHUB\wuwa_actionseq_player\src\main.py:1763

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1763 行, 第 42 列
- **错误信息**: `None` 没有 "update_format" 属性

#### 66. d:\GITHUB\wuwa_actionseq_player\src\main.py:1766

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1766 行, 第 42 列
- **错误信息**: `None` 没有 "update_format" 属性

#### 67. d:\GITHUB\wuwa_actionseq_player\src\main.py:1769

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1769 行, 第 34 列
- **错误信息**: `None` 没有 "setText" 属性

#### 68. d:\GITHUB\wuwa_actionseq_player\src\main.py:1773

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1773 行, 第 79 列
- **错误信息**: 无法访问 "MetadataManager" 类的 "metadata" 属性
  属性 "metadata" 未知

#### 69. d:\GITHUB\wuwa_actionseq_player\src\main.py:1774

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1774 行, 第 70 列
- **错误信息**: 无法访问 "MetadataManager" 类的 "metadata" 属性
  属性 "metadata" 未知

#### 70. d:\GITHUB\wuwa_actionseq_player\src\main.py:1778

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 1778 行, 第 35 列
- **错误信息**: `None` 没有 "setEnabled" 属性

#### 71. d:\GITHUB\wuwa_actionseq_player\src\main.py:1937

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1937 行, 第 38 列
- **错误信息**: 无法为 "MetadataManager" 类的 "metadata" 属性赋值
  属性 "metadata" 未知

#### 72. d:\GITHUB\wuwa_actionseq_player\src\main.py:2140

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2140 行, 第 30 列
- **错误信息**: 无法访问 "QTableWidget" 类的 "set_character_mapping" 属性
  属性 "set_character_mapping" 未知

#### 73. d:\GITHUB\wuwa_actionseq_player\src\main.py:2140

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2140 行, 第 30 列
- **错误信息**: `None` 没有 "set_character_mapping" 属性

#### 74. d:\GITHUB\wuwa_actionseq_player\src\main.py:2210

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2210 行, 第 26 列
- **错误信息**: `None` 没有 "setText" 属性

#### 75. d:\GITHUB\wuwa_actionseq_player\src\main.py:2217

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2217 行, 第 27 列
- **错误信息**: `None` 没有 "setEnabled" 属性

#### 76. d:\GITHUB\wuwa_actionseq_player\src\main.py:2268

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2268 行, 第 30 列
- **错误信息**: 无法访问 "QTableWidget" 类的 "update_script_data" 属性
  属性 "update_script_data" 未知

#### 77. d:\GITHUB\wuwa_actionseq_player\src\main.py:2268

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2268 行, 第 30 列
- **错误信息**: `None` 没有 "update_script_data" 属性

#### 78. d:\GITHUB\wuwa_actionseq_player\src\main.py:2277

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2277 行, 第 30 列
- **错误信息**: 无法为 "QTableWidget" 类的 "_last_script_actions" 属性赋值
  属性 "_last_script_actions" 未知

#### 79. d:\GITHUB\wuwa_actionseq_player\src\main.py:2277

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2277 行, 第 30 列
- **错误信息**: `None` 没有 "_last_script_actions" 属性

#### 80. d:\GITHUB\wuwa_actionseq_player\src\main.py:2278

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2278 行, 第 30 列
- **错误信息**: 无法为 "QTableWidget" 类的 "_last_current_index" 属性赋值
  属性 "_last_current_index" 未知

#### 81. d:\GITHUB\wuwa_actionseq_player\src\main.py:2278

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2278 行, 第 30 列
- **错误信息**: `None` 没有 "_last_current_index" 属性

#### 82. d:\GITHUB\wuwa_actionseq_player\src\main.py:2279

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2279 行, 第 30 列
- **错误信息**: 无法为 "QTableWidget" 类的 "_last_script_status" 属性赋值
  属性 "_last_script_status" 未知

#### 83. d:\GITHUB\wuwa_actionseq_player\src\main.py:2279

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2279 行, 第 30 列
- **错误信息**: `None` 没有 "_last_script_status" 属性

#### 84. d:\GITHUB\wuwa_actionseq_player\src\main.py:2280

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2280 行, 第 30 列
- **错误信息**: 无法为 "QTableWidget" 类的 "_last_has_start_events" 属性赋值
  属性 "_last_has_start_events" 未知

#### 85. d:\GITHUB\wuwa_actionseq_player\src\main.py:2280

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2280 行, 第 30 列
- **错误信息**: `None` 没有 "_last_has_start_events" 属性

#### 86. d:\GITHUB\wuwa_actionseq_player\src\main.py:2281

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2281 行, 第 30 列
- **错误信息**: 无法为 "QTableWidget" 类的 "_last_loop_start_index" 属性赋值
  属性 "_last_loop_start_index" 未知

#### 87. d:\GITHUB\wuwa_actionseq_player\src\main.py:2281

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2281 行, 第 30 列
- **错误信息**: `None` 没有 "_last_loop_start_index" 属性

#### 88. d:\GITHUB\wuwa_actionseq_player\src\main.py:2282

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2282 行, 第 30 列
- **错误信息**: 无法为 "QTableWidget" 类的 "_last_current_loop" 属性赋值
  属性 "_last_current_loop" 未知

#### 89. d:\GITHUB\wuwa_actionseq_player\src\main.py:2282

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2282 行, 第 30 列
- **错误信息**: `None` 没有 "_last_current_loop" 属性

#### 90. d:\GITHUB\wuwa_actionseq_player\src\main.py:2445

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2445 行, 第 47 列
- **错误信息**: `None` 没有 "isChecked" 属性

#### 91. d:\GITHUB\wuwa_actionseq_player\src\main.py:2465

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2465 行, 第 26 列
- **错误信息**: `None` 没有 "setEnabled" 属性

#### 92. d:\GITHUB\wuwa_actionseq_player\src\main.py:2466

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2466 行, 第 27 列
- **错误信息**: `None` 没有 "setEnabled" 属性

#### 93. d:\GITHUB\wuwa_actionseq_player\src\main.py:2467

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2467 行, 第 26 列
- **错误信息**: `None` 没有 "setEnabled" 属性

#### 94. d:\GITHUB\wuwa_actionseq_player\src\main.py:2471

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2471 行, 第 30 列
- **错误信息**: `None` 没有 "setText" 属性

#### 95. d:\GITHUB\wuwa_actionseq_player\src\main.py:2473

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2473 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 96. d:\GITHUB\wuwa_actionseq_player\src\main.py:2474

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2474 行, 第 35 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 97. d:\GITHUB\wuwa_actionseq_player\src\main.py:2475

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2475 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 98. d:\GITHUB\wuwa_actionseq_player\src\main.py:2477

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2477 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 99. d:\GITHUB\wuwa_actionseq_player\src\main.py:2478

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2478 行, 第 35 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 100. d:\GITHUB\wuwa_actionseq_player\src\main.py:2479

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2479 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 101. d:\GITHUB\wuwa_actionseq_player\src\main.py:2480

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2480 行, 第 31 列
- **错误信息**: `None` 没有 "setText" 属性

#### 102. d:\GITHUB\wuwa_actionseq_player\src\main.py:2482

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2482 行, 第 30 列
- **错误信息**: `None` 没有 "setText" 属性

#### 103. d:\GITHUB\wuwa_actionseq_player\src\main.py:2484

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2484 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 104. d:\GITHUB\wuwa_actionseq_player\src\main.py:2485

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2485 行, 第 35 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 105. d:\GITHUB\wuwa_actionseq_player\src\main.py:2486

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2486 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 106. d:\GITHUB\wuwa_actionseq_player\src\main.py:2488

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2488 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 107. d:\GITHUB\wuwa_actionseq_player\src\main.py:2489

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2489 行, 第 35 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 108. d:\GITHUB\wuwa_actionseq_player\src\main.py:2490

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2490 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 109. d:\GITHUB\wuwa_actionseq_player\src\main.py:2491

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2491 行, 第 31 列
- **错误信息**: `None` 没有 "setText" 属性

#### 110. d:\GITHUB\wuwa_actionseq_player\src\main.py:2493

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2493 行, 第 30 列
- **错误信息**: `None` 没有 "setText" 属性

#### 111. d:\GITHUB\wuwa_actionseq_player\src\main.py:2495

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2495 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 112. d:\GITHUB\wuwa_actionseq_player\src\main.py:2496

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2496 行, 第 35 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 113. d:\GITHUB\wuwa_actionseq_player\src\main.py:2497

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2497 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 114. d:\GITHUB\wuwa_actionseq_player\src\main.py:2499

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2499 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 115. d:\GITHUB\wuwa_actionseq_player\src\main.py:2500

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2500 行, 第 35 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 116. d:\GITHUB\wuwa_actionseq_player\src\main.py:2501

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2501 行, 第 34 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 117. d:\GITHUB\wuwa_actionseq_player\src\main.py:2502

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2502 行, 第 31 列
- **错误信息**: `None` 没有 "setText" 属性

#### 118. d:\GITHUB\wuwa_actionseq_player\src\main.py:2509

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2509 行, 第 31 列
- **错误信息**: `None` 没有 "setEnabled" 属性

#### 119. d:\GITHUB\wuwa_actionseq_player\src\main.py:2534

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2534 行, 第 42 列
- **错误信息**: `None` 没有 "setText" 属性

#### 120. d:\GITHUB\wuwa_actionseq_player\src\main.py:2542

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 2542 行, 第 33 列
- **错误信息**: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.color_config" 作为相对导入
  或指定完整模块路径："src.system_services.color_config"

#### 121. d:\GITHUB\wuwa_actionseq_player\src\main.py:2546

- **规则**: `reportArgumentType`
- **位置**: 第 2546 行, 第 51 列
- **错误信息**: "Literal['bg']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['bg']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['bg']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['bg']" 与 "slice[Any, Any, Any]" 不兼容

#### 122. d:\GITHUB\wuwa_actionseq_player\src\main.py:2547

- **规则**: `reportArgumentType`
- **位置**: 第 2547 行, 第 51 列
- **错误信息**: "Literal['border']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['border']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['border']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['border']" 与 "slice[Any, Any, Any]" 不兼容

#### 123. d:\GITHUB\wuwa_actionseq_player\src\main.py:2550

- **规则**: `reportArgumentType`
- **位置**: 第 2550 行, 第 40 列
- **错误信息**: "Literal['text']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['text']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['text']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['text']" 与 "slice[Any, Any, Any]" 不兼容

#### 124. d:\GITHUB\wuwa_actionseq_player\src\main.py:2554

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2554 行, 第 50 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 125. d:\GITHUB\wuwa_actionseq_player\src\main.py:2556

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2556 行, 第 50 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 126. d:\GITHUB\wuwa_actionseq_player\src\main.py:2571

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 2571 行, 第 33 列
- **错误信息**: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.color_config" 作为相对导入
  或指定完整模块路径："src.system_services.color_config"

#### 127. d:\GITHUB\wuwa_actionseq_player\src\main.py:2575

- **规则**: `reportArgumentType`
- **位置**: 第 2575 行, 第 51 列
- **错误信息**: "Literal['bg']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['bg']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['bg']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['bg']" 与 "slice[Any, Any, Any]" 不兼容

#### 128. d:\GITHUB\wuwa_actionseq_player\src\main.py:2576

- **规则**: `reportArgumentType`
- **位置**: 第 2576 行, 第 51 列
- **错误信息**: "Literal['border']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['border']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['border']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['border']" 与 "slice[Any, Any, Any]" 不兼容

#### 129. d:\GITHUB\wuwa_actionseq_player\src\main.py:2579

- **规则**: `reportArgumentType`
- **位置**: 第 2579 行, 第 40 列
- **错误信息**: "Literal['text']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['text']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
    "Literal['text']" 与 Protocol 类 "SupportsIndex" 不兼容
      "__index__" 不存在
    "Literal['text']" 与 "slice[Any, Any, Any]" 不兼容

#### 130. d:\GITHUB\wuwa_actionseq_player\src\main.py:2582

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2582 行, 第 50 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 131. d:\GITHUB\wuwa_actionseq_player\src\main.py:2584

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2584 行, 第 50 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 132. d:\GITHUB\wuwa_actionseq_player\src\main.py:2594

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2594 行, 第 42 列
- **错误信息**: `None` 没有 "setText" 属性

#### 133. d:\GITHUB\wuwa_actionseq_player\src\main.py:2599

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2599 行, 第 41 列
- **错误信息**: `None` 没有 "setMaximum" 属性

#### 134. d:\GITHUB\wuwa_actionseq_player\src\main.py:2600

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2600 行, 第 41 列
- **错误信息**: `None` 没有 "setValue" 属性

#### 135. d:\GITHUB\wuwa_actionseq_player\src\main.py:2602

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2602 行, 第 41 列
- **错误信息**: `None` 没有 "setMaximum" 属性

#### 136. d:\GITHUB\wuwa_actionseq_player\src\main.py:2603

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2603 行, 第 41 列
- **错误信息**: `None` 没有 "setValue" 属性

#### 137. d:\GITHUB\wuwa_actionseq_player\src\main.py:2618

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2618 行, 第 34 列
- **错误信息**: `None` 没有 "setText" 属性

#### 138. d:\GITHUB\wuwa_actionseq_player\src\main.py:2623

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2623 行, 第 36 列
- **错误信息**: `None` 没有 "setText" 属性

#### 139. d:\GITHUB\wuwa_actionseq_player\src\main.py:2625

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2625 行, 第 36 列
- **错误信息**: `None` 没有 "setText" 属性

#### 140. d:\GITHUB\wuwa_actionseq_player\src\main.py:2660

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2660 行, 第 36 列
- **错误信息**: `None` 没有 "setText" 属性

#### 141. d:\GITHUB\wuwa_actionseq_player\src\main.py:2667

- **规则**: `reportImplicitRelativeImport`
- **位置**: 第 2667 行, 第 25 列
- **错误信息**: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
  请改用 ".system_services.color_config" 作为相对导入
  或指定完整模块路径："src.system_services.color_config"

#### 142. d:\GITHUB\wuwa_actionseq_player\src\main.py:2672

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 2672 行, 第 36 列
- **错误信息**: `None` 没有 "setStyleSheet" 属性

#### 143. d:\GITHUB\wuwa_actionseq_player\src\main.py:2783

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2783 行, 第 24 列
- **错误信息**: 无法访问 "QCoreApplication" 类的 "style" 属性
  属性 "style" 未知

#### 144. d:\GITHUB\wuwa_actionseq_player\src\main.py:2791

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2791 行, 第 24 列
- **错误信息**: 无法访问 "QCoreApplication" 类的 "setStyle" 属性
  属性 "setStyle" 未知

#### 145. d:\GITHUB\wuwa_actionseq_player\src\main.py:2795

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 2795 行, 第 28 列
- **错误信息**: 无法访问 "QCoreApplication" 类的 "setStyle" 属性
  属性 "setStyle" 未知

#### 146. d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130

- **规则**: `reportArgumentType`
- **位置**: 第 130 行, 第 21 列
- **错误信息**: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "title"
  "Any | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 147. d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130

- **规则**: `reportArgumentType`
- **位置**: 第 130 行, 第 21 列
- **错误信息**: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "description"
  "Any | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 148. d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130

- **规则**: `reportArgumentType`
- **位置**: 第 130 行, 第 21 列
- **错误信息**: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "Dict[str, str]" 类型的形参 "characters"
  "Any | None" 类型与 "Dict[str, str]" 类型不兼容
    "None" 与 "Dict[str, str]" 不兼容

#### 149. d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130

- **规则**: `reportArgumentType`
- **位置**: 第 130 行, 第 21 列
- **错误信息**: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "version"
  "Any | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 150. d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130

- **规则**: `reportArgumentType`
- **位置**: 第 130 行, 第 21 列
- **错误信息**: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "author"
  "Any | None" 类型与 "str" 类型不兼容
    "None" 与 "str" 不兼容

#### 151. d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130

- **规则**: `reportArgumentType`
- **位置**: 第 130 行, 第 21 列
- **错误信息**: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "List[str]" 类型的形参 "tags"
  "Any | None" 类型与 "List[str]" 类型不兼容
    "None" 与 "List[str]" 不兼容

#### 152. d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:167

- **规则**: `reportArgumentType`
- **位置**: 第 167 行, 第 64 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "Dict[str, Any]" 类型的参数
  "None" 与 "Dict[str, Any]" 不兼容

#### 153. d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:201

- **规则**: `reportArgumentType`
- **位置**: 第 201 行, 第 44 列
- **错误信息**: 无法将 "None" 类型的表达式赋值给 "Dict[str, Any]" 类型的参数
  "None" 与 "Dict[str, Any]" 不兼容

#### 154. d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:18

- **规则**: `reportConstantRedefinition`
- **位置**: 第 18 行, 第 4 列
- **错误信息**: 不能重新定义常量 "_COLOR_CONFIG_AVAILABLE"（全大写名称）

#### 155. d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:24

- **规则**: `reportConstantRedefinition`
- **位置**: 第 24 行, 第 4 列
- **错误信息**: 不能重新定义常量 "_COLOR_PATCH_AVAILABLE"（全大写名称）

#### 156. d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:296

- **规则**: `reportAssignmentType`
- **位置**: 第 296 行, 第 21 列
- **错误信息**: "str | dict[str, str]" 类型不匹配声明的 "Dict[str, str]" 类型
  "str | dict[str, str]" 类型与 "Dict[str, str]" 类型不兼容
    "str" 与 "Dict[str, str]" 不兼容

#### 157. d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:298

- **规则**: `reportAssignmentType`
- **位置**: 第 298 行, 第 21 列
- **错误信息**: "str | dict[str, str]" 类型不匹配声明的 "Dict[str, str]" 类型
  "str | dict[str, str]" 类型与 "Dict[str, str]" 类型不兼容
    "str" 与 "Dict[str, str]" 不兼容

#### 158. d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:17

- **规则**: `reportAssignmentType`
- **位置**: 第 17 行, 第 30 列
- **错误信息**: "type[src.system_services.color_config.ColorConfig]" 类型不匹配声明的 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型
  "src.system_services.color_config.ColorConfig" 与 "src.system_services.cross_platform_color_patch.ColorConfig" 不兼容
  "type[src.system_services.color_config.ColorConfig]" 类型与 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型不兼容

#### 159. d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:21

- **规则**: `reportAssignmentType`
- **位置**: 第 21 行, 第 30 列
- **错误信息**: "type[src.system_services.color_config.ColorConfig]" 类型不匹配声明的 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型
  "src.system_services.color_config.ColorConfig" 与 "src.system_services.cross_platform_color_patch.ColorConfig" 不兼容
  "type[src.system_services.color_config.ColorConfig]" 类型与 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型不兼容

#### 160. d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:151

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 151 行, 第 37 列
- **错误信息**: 无法访问 "type[ColorConfig]" 类的 "get_action_bar_style" 属性
  属性 "get_action_bar_style" 未知

#### 161. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:17

- **规则**: `reportMissingImports`
- **位置**: 第 17 行, 第 5 列
- **错误信息**: 无法解析导入 "cryptography.hazmat.primitives.ciphers"

#### 162. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:18

- **规则**: `reportMissingImports`
- **位置**: 第 18 行, 第 5 列
- **错误信息**: 无法解析导入 "cryptography.hazmat.primitives"

#### 163. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:19

- **规则**: `reportMissingImports`
- **位置**: 第 19 行, 第 5 列
- **错误信息**: 无法解析导入 "cryptography.hazmat.backends"

#### 164. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:87

- **规则**: `reportOptionalCall`
- **位置**: 第 87 行, 第 16 列
- **错误信息**: `None` 不支持调用

#### 165. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:98

- **规则**: `reportOptionalCall`
- **位置**: 第 98 行, 第 16 列
- **错误信息**: `None` 不支持调用

#### 166. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:103

- **规则**: `reportOptionalCall`
- **位置**: 第 103 行, 第 16 列
- **错误信息**: `None` 不支持调用

#### 167. d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:113

- **规则**: `reportOptionalCall`
- **位置**: 第 113 行, 第 16 列
- **错误信息**: `None` 不支持调用

#### 168. d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:70

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 70 行, 第 49 列
- **错误信息**: 无法访问 "type[QFrame]" 类的 "StyledPanel" 属性
  属性 "StyledPanel" 未知

#### 169. d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:79

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 79 行, 第 43 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
  属性 "AlignCenter" 未知

#### 170. d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:117

- **规则**: `reportCallIssue`
- **位置**: 第 117 行, 第 50 列
- **错误信息**: 需要传入 1 个位置参数

#### 171. d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:121

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 121 行, 第 35 列
- **错误信息**: 无法访问 "type[QFileDialog]" 类的 "DontUseNativeDialog" 属性
  属性 "DontUseNativeDialog" 未知

#### 172. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:40

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 40 行, 第 34 列
- **错误信息**: 无法访问 "type[QFrame]" 类的 "StyledPanel" 属性
  属性 "StyledPanel" 未知

#### 173. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:50

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 50 行, 第 40 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
  属性 "AlignCenter" 未知

#### 174. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:55

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 55 行, 第 42 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignVCenter" 属性
  属性 "AlignVCenter" 未知

#### 175. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:60

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 60 行, 第 40 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignVCenter" 属性
  属性 "AlignVCenter" 未知

#### 176. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:107

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 107 行, 第 22 列
- **错误信息**: `None` 没有 "update" 属性

#### 177. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:139

- **规则**: `reportUninitializedInstanceVariable`
- **位置**: 第 139 行, 第 13 列
- **错误信息**: 实例变量 "animation" 未在类体或 `__init__` 方法中初始化

#### 178. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:143

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 143 行, 第 51 列
- **错误信息**: 无法访问 "type[QEasingCurve]" 类的 "OutQuad" 属性
  属性 "OutQuad" 未知

#### 179. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:214

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 214 行, 第 29 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
  属性 "AlignCenter" 未知

#### 180. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:275

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 275 行, 第 61 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 181. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:351

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 351 行, 第 34 列
- **错误信息**: 无法访问 "type[QFrame]" 类的 "NoFrame" 属性
  属性 "NoFrame" 未知

#### 182. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:360

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 360 行, 第 41 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
  属性 "AlignCenter" 未知

#### 183. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:368

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 368 行, 第 44 列
- **错误信息**: 无法访问 "type[Qt]" 类的 "AlignVCenter" 属性
  属性 "AlignVCenter" 未知

#### 184. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:451

- **规则**: `reportArgumentType`
- **位置**: 第 451 行, 第 33 列
- **错误信息**: "str | bool" 类型的实参无法赋值给函数 "setText" 中 "str" 类型的形参 "arg__1"
  "str | bool" 类型与 "str" 类型不兼容
    "bool" 与 "str" 不兼容

#### 185. d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:467

- **规则**: `reportArgumentType`
- **位置**: 第 467 行, 第 37 列
- **错误信息**: "str | bool" 类型的实参无法赋值给函数 "setVisible" 中 "bool" 类型的形参 "visible"
  "str | bool" 类型与 "bool" 类型不兼容
    "str" 与 "bool" 不兼容

#### 186. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:133

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 133 行, 第 25 列
- **错误信息**: `None` 没有 "setText" 属性

#### 187. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:137

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 137 行, 第 31 列
- **错误信息**: `None` 没有 "setText" 属性

#### 188. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:148

- **规则**: `reportUninitializedInstanceVariable`
- **位置**: 第 148 行, 第 13 列
- **错误信息**: 实例变量 "animation" 未在类体或 `__init__` 方法中初始化

#### 189. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:158

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 158 行, 第 25 列
- **错误信息**: `None` 没有 "setText" 属性

#### 190. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:159

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 159 行, 第 31 列
- **错误信息**: `None` 没有 "setText" 属性

#### 191. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:204

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 204 行, 第 35 列
- **错误信息**: `None` 没有 "setMaximumHeight" 属性

#### 192. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:205

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 205 行, 第 35 列
- **错误信息**: `None` 没有 "setMinimumHeight" 属性

#### 193. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:208

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 208 行, 第 35 列
- **错误信息**: `None` 没有 "setMaximumHeight" 属性

#### 194. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:209

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 209 行, 第 35 列
- **错误信息**: `None` 没有 "setMinimumHeight" 属性

#### 195. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:212

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 212 行, 第 35 列
- **错误信息**: `None` 没有 "setMaximumHeight" 属性

#### 196. d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:213

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 213 行, 第 35 列
- **错误信息**: `None` 没有 "setMinimumHeight" 属性

## ⚠️ 警告详情

共发现 **1603** 个警告

1. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:9` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
2. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:9` - 此类型自 Python 3.10 起已弃用；请改用 "| None" (`reportDeprecated`)
3. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:10` - "ActionType" 导入项未使用 (`reportUnusedImport`)
4. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:16` - 此类型自 Python 3.10 起已弃用；请改用 "| None" (`reportDeprecated`)
5. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:24` - 由于这个类未使用 `@final` 装饰，其 `action_callback` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
6. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:25` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
7. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:26` - 由于这个类未使用 `@final` 装饰，其 `short_press_threshold` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
8. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:29` - 由于这个类未使用 `@final` 装饰，其 `valid_character_keys` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
9. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:30` - 由于这个类未使用 `@final` 装饰，其 `valid_skill_keys` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
10. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:31` - 由于这个类未使用 `@final` 装饰，其 `valid_mouse_button` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
11. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:79` - "x" 未使用 (`reportUnusedParameter`)
12. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:79` - "y" 未使用 (`reportUnusedParameter`)
13. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:115` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
14. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:143` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
15. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:7` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
16. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:17` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
17. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:20` - 由于这个类未使用 `@final` 装饰，其 `action_display_mapping` 属性需要类型注解 (`reportUnannotatedClassAttribute`)
18. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:26` - 此类型自 Python 3.9 起已弃用；请改用 "dict" (`reportDeprecated`)
19. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:54` - "characters" 参数的类型部分未知
  参数为 "dict[Unknown, Unknown]" 类型 (`reportUnknownParameterType`)
20. `d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:60` - "dict[Unknown, Unknown]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (`reportUnnecessaryIsInstance`)

... 还有 1583 个警告未显示

## 📁 检查的文件列表

1. `src\__init__.py`
2. `src\business_logic\__init__.py`
3. `src\business_logic\action_matcher.py`
4. `src\business_logic\character_mapper.py`
5. `src\business_logic\error_handler.py`
6. `src\business_logic\loading_state_manager.py`
7. `src\business_logic\loop_controller.py`
8. `src\business_logic\metadata_manager.py`
9. `src\business_logic\script_format_detector.py`
10. `src\business_logic\script_player_engine.py`
11. `src\business_logic\script_validator.py`
12. `src\business_logic\state_manager.py`
13. `src\main.py`
14. `src\models\__init__.py`
15. `src\models\enums.py`
16. `src\models\script_action.py`
17. `src\models\script_metadata.py`
18. `src\models\script_models.py`
19. `src\models\validation_models.py`
20. `src\qa\__init__.py`
21. `src\qa\qa_key_recognition_test.py`
22. `src\services\error_handling_service.py`
23. `src\services\loading_state_manager.py`
24. `src\services\script_format_detector.py`
25. `src\system_services\__init__.py`
26. `src\system_services\color_config.py`
27. `src\system_services\cross_platform_color_patch.py`
28. `src\system_services\decryption_service.py`
29. `src\ui\__init__.py`
30. `src\ui\enhanced_file_dialog.py`
31. `src\ui\format_indicator_widget.py`
32. `src\ui\metadata_display_widget.py`
33. `src\ui\widgets\__init__.py`
34. `src\ui\widgets\script_preview.py`

## 📄 原始检查输出

```
d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:9:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:9:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:10:30 - warning: "ActionType" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:16:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:24:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:25:31 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:26:14 - warning: 由于这个类未使用 `@final` 装饰，其 `short_press_threshold` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:29:14 - warning: 由于这个类未使用 `@final` 装饰，其 `valid_character_keys` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:30:14 - warning: 由于这个类未使用 `@final` 装饰，其 `valid_skill_keys` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:31:14 - warning: 由于这个类未使用 `@final` 装饰，其 `valid_mouse_button` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:79:30 - warning: "x" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:79:38 - warning: "y" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:115:34 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\action_matcher.py:143:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:7:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:17:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:20:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_display_mapping` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:26:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:54:40 - warning: "characters" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:54:52 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:60:27 - warning: "dict[Unknown, Unknown]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:63:17 - warning: "key" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:63:22 - warning: "value" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\character_mapper.py:68:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:15:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:15:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:15:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:15:41 - warning: "Tuple" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:38:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_error_details` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:40:44 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:40:60 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:102:9 - warning: 变量 "error_type" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:139:84 - error: 无法将 "None" 类型的表达式赋值给 "Exception" 类型的参数
    "None" 与 "Exception" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:139:93 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:162:41 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:163:54 - error: 无法将 "None" 类型的表达式赋值给 "Exception" 类型的参数
    "None" 与 "Exception" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:201:51 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:218:9 - warning: "int" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:334:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:334:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:334:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:334:73 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:334:83 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:375:34 - error: 无法为 "type[EnhancedErrorHandler]" 类的 "_instance" 属性赋值
    属性 "_instance" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:376:16 - warning: "_instance" 的类型部分未知
    "_instance" 为 "EnhancedErrorHandler | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:376:16 - warning: 返回类型 "EnhancedErrorHandler | Unknown" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\error_handler.py:376:37 - error: 无法访问 "type[EnhancedErrorHandler]" 类的 "_instance" 属性
    属性 "_instance" 未知 (reportAttributeAccessIssue)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:12:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:12:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:13:18 - warning: "Enum" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:23:14 - warning: 由于这个类未使用 `@final` 装饰，其 `current_state` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:24:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:25:14 - warning: 由于这个类未使用 `@final` 装饰，其 `state_messages` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:26:14 - warning: 由于这个类未使用 `@final` 装饰，其 `state_progress` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:27:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_message` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:28:14 - warning: 由于这个类未使用 `@final` 装饰，其 `script_format` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:29:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_callbacks` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:30:14 - warning: 由于这个类未使用 `@final` 装饰，其 `status_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:31:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_callback` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:33:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:50:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:67:56 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:68:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:69:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:163:9 - warning: "progress_callbacks" 的类型部分未知
    "progress_callbacks" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:163:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:165:40 - warning: "callback" 参数的类型部分未知
    参数为 "(...) -> Unknown" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:165:50 - error: "Callable" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:172:24 - warning: "progress_callbacks" 的类型部分未知
    "progress_callbacks" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:173:13 - warning: "progress_callbacks" 的类型部分未知
    "progress_callbacks" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:173:13 - warning: "remove" 的类型部分未知
    "remove" 为 "(value: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:178:13 - warning: "callback" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:178:25 - warning: "progress_callbacks" 的类型部分未知
    "progress_callbacks" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:223:9 - warning: 返回类型 "Dict[str, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:223:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:223:48 - error: 此处应为类而非 "(iterable: Iterable[object], /) -> bool" (reportGeneralTypeIssues)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:230:16 - warning: 返回类型 "dict[str, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:304:18 - warning: 由于这个类未使用 `@final` 装饰，其 `_progress_bounds` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:304:18 - error: 实例变量 "_progress_bounds" 未在类体或 `__init__` 方法中初始化 (reportUninitializedInstanceVariable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:318:12 - warning: "error_callback" 的类型部分未知
    "error_callback" 为 "((...) -> Unknown) | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:319:13 - warning: "error_callback" 的类型部分未知
    "error_callback" 为 "(...) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:321:35 - warning: "callback" 参数的类型部分未知
    参数为 "(...) -> Unknown" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:321:45 - error: "Callable" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:328:9 - warning: "status_callback" 的类型部分未知
    "status_callback" 为 "(...) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:330:34 - warning: "callback" 参数的类型部分未知
    参数为 "(...) -> Unknown" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:330:44 - error: "Callable" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:337:9 - warning: "error_callback" 的类型部分未知
    "error_callback" 为 "(...) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:339:58 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:350:12 - warning: "status_callback" 的类型部分未知
    "status_callback" 为 "((...) -> Unknown) | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:353:17 - warning: "status_callback" 的类型部分未知
    "status_callback" 为 "(...) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:358:44 - warning: "error_callback" 的类型部分未知
    "error_callback" 为 "((...) -> Unknown) | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loading_state_manager.py:361:17 - warning: "error_callback" 的类型部分未知
    "error_callback" 为 "(...) -> Unknown" 类型 (reportUnknownMemberType)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:8:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:9:30 - warning: "ScriptStatus" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:17:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_current_loop` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:18:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_total_loops` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:19:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:20:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_total_loop_time` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:21:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_is_looping` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:106:9 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:106:32 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\loop_controller.py:113:16 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:9:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:9:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:9:41 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:25:24 - warning: "debug_manager" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:25:24 - warning: "debug_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:32:9 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:32:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:33:14 - warning: 由于这个类未使用 `@final` 装饰，其 `logger` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:35:61 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:35:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:35:80 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:60:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:61:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:61:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:62:17 - warning: 不允许隐式的字符串拼接 (reportImplicitStringConcatenation)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:70:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:70:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:82:24 - warning: 返回类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:87:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:88:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:88:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:95:58 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:95:68 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:109:9 - warning: "meta_data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:113:34 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:116:40 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:121:17 - warning: "key" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:121:22 - warning: "value" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:121:31 - warning: "items" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:122:32 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:122:44 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:126:36 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:129:35 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:132:34 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:132:43 - warning: "tag" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:135:41 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:139:56 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:139:66 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:153:9 - warning: "script_info" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:157:40 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:161:48 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:164:36 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:168:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:168:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:182:9 - warning: "info" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:186:34 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:189:40 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:193:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:193:71 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:213:13 - warning: "header" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:216:38 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:219:44 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:223:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:223:84 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:223:93 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:223:115 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:240:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:242:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:259:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:265:16 - warning: "Dict[str, str]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:266:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:272:24 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:272:52 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:273:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:276:16 - warning: "List[str]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:277:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:283:24 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:284:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:286:24 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:287:59 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:287:79 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "suggestions" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:303:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:303:56 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:330:34 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:333:40 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:341:53 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:345:21 - warning: "key" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:345:26 - warning: "value" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:346:46 - warning: 参数类型未知
    实参对应于 "__new__" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\metadata_manager.py:346:58 - warning: 参数类型未知
    实参对应于 "__new__" 函数中的 "object" 形参 (reportUnknownArgumentType)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:14:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:14:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:14:30 - warning: "Tuple" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:14:37 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:24:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:31:14 - warning: 由于这个类未使用 `@final` 装饰，其 `decryption_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:44:33 - warning: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:86:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:86:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:146:17 - warning: "data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:174:52 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:174:62 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:186:17 - warning: "data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:192:17 - warning: "info" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:193:36 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:194:38 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:195:40 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:199:47 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:203:21 - warning: "segment" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:205:45 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:208:20 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:213:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:213:67 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_format_detector.py:226:13 - warning: 变量 "path" 未使用 (reportUnusedVariable)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:8:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:8:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:24:24 - warning: "debug_manager" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:24:24 - warning: "debug_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:31:9 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:31:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:34:14 - warning: 由于这个类未使用 `@final` 装饰，其 `validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:35:14 - warning: 由于这个类未使用 `@final` 装饰，其 `state_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:36:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_matcher` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:37:14 - warning: 由于这个类未使用 `@final` 装饰，其 `character_mapper` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:40:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:41:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:44:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:45:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:46:35 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:65:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:66:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:66:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:81:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:82:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:82:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:91:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:92:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:92:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:107:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:118:13 - warning: "data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:125:13 - warning: "events" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:125:22 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:125:54 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:128:13 - warning: "events" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:128:22 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:134:13 - warning: "update_character_mapping" 的类型部分未知
    "update_character_mapping" 为 "(characters: dict[Unknown, Unknown]) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:134:60 - warning: 参数类型为 `Any`
    实参对应于 "update_character_mapping" 函数中的 "characters" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:137:13 - warning: 变量 "i" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:137:16 - warning: "event" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:137:35 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "iterable" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:138:20 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:140:35 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "x" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:141:39 - warning: 参数类型为 `Any`
    实参对应于 "__new__" 函数中的 "x" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:142:33 - warning: 参数类型为 `Any`
    实参对应于 "__init__" 函数中的 "action_type" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:143:35 - warning: 参数类型为 `Any`
    实参对应于 "__init__" 函数中的 "key_or_action" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:144:44 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:147:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:149:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:159:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:160:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:160:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:177:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:178:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:178:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:199:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:200:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:200:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:222:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:223:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:223:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:240:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:241:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:241:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:247:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:259:9 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:259:34 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:267:20 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:269:16 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:311:37 - warning: "mapping" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:311:46 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_player_engine.py:318:53 - warning: 部分参数的类型未知
    实参对应于 "set_character_mapping" 函数中的 "mapping" 形参
    参数类型为 "dict[Unknown, Unknown]" (reportUnknownArgumentType)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:33 - warning: "Dict" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:39 - warning: "Any" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:10:44 - warning: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:22:24 - warning: "debug_manager" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:22:24 - warning: "debug_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:23:9 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:23:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:24:14 - warning: 由于这个类未使用 `@final` 装饰，其 `supported_actions` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:34:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_file_size` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:51:13 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:54:48 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:54:56 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "suggestions" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:61:13 - warning: "json_data" 的类型部分未知
    "json_data" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:61:38 - warning: "_validate_json_syntax" 的类型部分未知
    "_validate_json_syntax" 为 "(content: str) -> Tuple[dict[Unknown, Unknown], List[ValidationError]]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:62:13 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:66:58 - warning: 部分参数的类型未知
    实参对应于 "_generate_suggestions" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:67:48 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:70:32 - warning: "_validate_structure" 的类型部分未知
    "_validate_structure" 为 "(data: dict[Unknown, Unknown]) -> List[ValidationError]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:71:13 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:74:29 - warning: "_validate_actions" 的类型部分未知
    "_validate_actions" 为 "(data: dict[Unknown, Unknown]) -> List[ValidationError]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:75:13 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:78:54 - warning: 部分参数的类型未知
    实参对应于 "_generate_suggestions" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:80:28 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:81:47 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:91:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:104:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:109:20 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:114:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:122:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:128:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:130:9 - warning: 返回类型 "Tuple[dict[Unknown, Unknown], List[ValidationError]]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:130:54 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:130:60 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:130:66 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:142:13 - warning: "json_data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:143:20 - warning: 返回类型 "tuple[Any, list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:151:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:152:20 - warning: 返回类型 "tuple[dict[Unknown, Unknown], list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:154:35 - warning: "data" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:154:41 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:154:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:167:13 - warning: 变量 "format_type" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:170:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:176:13 - warning: 变量 "format_type" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:182:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:190:27 - warning: "_validate_characters" 的类型部分未知
    "_validate_characters" 为 "(characters: dict[Unknown, Unknown]) -> List[ValidationError]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:190:53 - warning: 参数类型未知
    实参对应于 "_validate_characters" 函数中的 "characters" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:191:13 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:196:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:203:24 - warning: "segment" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:203:45 - warning: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:204:34 - warning: "_validate_segment" 的类型部分未知
    "_validate_segment" 为 "(segment: dict[Unknown, Unknown], index: int) -> List[ValidationError]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:204:57 - warning: 参数类型未知
    实参对应于 "_validate_segment" 函数中的 "segment" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:205:21 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:207:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:209:36 - warning: "characters" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:209:48 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:209:57 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:220:16 - warning: "dict[Unknown, Unknown]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:221:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:230:13 - warning: "key" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:232:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:239:13 - warning: "key" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:239:18 - warning: "name" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:241:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:247:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:249:33 - warning: "segment" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:249:42 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:249:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:263:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:269:13 - warning: "segment_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:271:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:279:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:285:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:291:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:293:33 - warning: "data" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:293:39 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:293:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:307:17 - warning: "segment" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:309:21 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:309:39 - warning: 参数类型未知
    实参对应于 "extend" 函数中的 "iterable" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:311:16 - warning: "event" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:311:35 - warning: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:312:28 - warning: "_validate_single_action" 的类型部分未知
    "_validate_single_action" 为 "(event: dict[Unknown, Unknown], index: int) -> List[ValidationError]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:312:57 - warning: 参数类型未知
    实参对应于 "_validate_single_action" 函数中的 "event" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:313:13 - warning: "extend" 的类型部分未知
    "extend" 为 "(iterable: Iterable[Unknown], /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:315:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:317:39 - warning: "event" 参数的类型部分未知
    参数为 "dict[Unknown, Unknown]" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:317:46 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:317:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:330:16 - warning: "dict[Unknown, Unknown]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:331:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:339:9 - warning: "timestamp" 的类型部分未知
    "timestamp" 为 "Unknown | None" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:339:21 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:341:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:347:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:354:9 - warning: "relative_time" 的类型部分未知
    "relative_time" 为 "Unknown | None" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:354:25 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:356:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:362:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:369:9 - warning: "action_name" 的类型部分未知
    "action_name" 为 "Unknown | None" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:369:23 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:371:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:377:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:383:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:390:9 - warning: "remark" 的类型部分未知
    "remark" 为 "Unknown | None" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:390:18 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:392:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:398:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:400:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:400:71 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:414:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:417:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:420:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:423:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\script_validator.py:425:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:8:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:8:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:18:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_status` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:19:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_current_action_index` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:20:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_total_actions` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:21:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_current_loop` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:22:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_total_loops` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:23:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:25:24 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:87:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:108:14 - warning: 条件的计算结果始终为 `False`，因为类型 "Literal[ScriptStatus.RUNNING]" 和 "Literal[ScriptStatus.PAUSED]" 之间不存在交集 (reportUnnecessaryComparison)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:157:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\business_logic\state_manager.py:163:50 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\main.py
  d:\GITHUB\wuwa_actionseq_player\src\main.py:13:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:13:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:13:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:13:47 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:13:47 - warning: "Tuple" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:14:25 - warning: "dataclass" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:15:18 - warning: "Enum" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:23:5 - error: 不能重新定义常量 "APPLICATION_PATH"（全大写名称） (reportConstantRedefinition)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:34:33 - warning: "QFrame" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:34:41 - warning: "QFileDialog" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:36:19 - warning: "QTableWidgetItem" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:36:37 - warning: "QHeaderView" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:39:25 - warning: "QObject" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:39:34 - warning: "QThread" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:39:51 - warning: "Slot" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:42:12 - warning: "QPalette" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:42:22 - warning: "QColor" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:42:30 - warning: "QKeySequence" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:42:44 - warning: "QShortcut" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:42:55 - warning: "QPixmap" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:42:64 - warning: "QIcon" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:52:34 - warning: "ActionType" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:54:46 - warning: "ValidationError" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:55:44 - warning: "ScriptMetadata" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:57:50 - warning: "StateManager" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:58:51 - warning: "ActionMatcher" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:59:57 - warning: "ScriptPlayerEngine" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:60:53 - warning: "CharacterMapper" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:72:10 - error: 从 "system_services.cross_platform_color_patch" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.cross_platform_color_patch" 作为相对导入
    或指定完整模块路径："src.system_services.cross_platform_color_patch" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:73:10 - error: 从 "system_services.decryption_service" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.decryption_service" 作为相对导入
    或指定完整模块路径："src.system_services.decryption_service" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:74:10 - error: 从 "models.enums" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".models.enums" 作为相对导入
    或指定完整模块路径："src.models.enums" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:74:30 - warning: "ActionType" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:75:10 - error: 从 "models.script_action" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".models.script_action" 作为相对导入
    或指定完整模块路径："src.models.script_action" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:76:10 - error: 从 "models.validation_models" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".models.validation_models" 作为相对导入
    或指定完整模块路径："src.models.validation_models" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:76:42 - warning: "ValidationError" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:77:10 - error: 从 "models.script_metadata" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".models.script_metadata" 作为相对导入
    或指定完整模块路径："src.models.script_metadata" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:77:40 - warning: "ScriptMetadata" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:78:10 - error: 从 "business_logic.script_validator" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.script_validator" 作为相对导入
    或指定完整模块路径："src.business_logic.script_validator" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:79:10 - error: 从 "business_logic.state_manager" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.state_manager" 作为相对导入
    或指定完整模块路径："src.business_logic.state_manager" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:79:46 - warning: "StateManager" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:80:10 - error: 从 "business_logic.action_matcher" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.action_matcher" 作为相对导入
    或指定完整模块路径："src.business_logic.action_matcher" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:80:47 - warning: "ActionMatcher" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:81:10 - error: 从 "business_logic.script_player_engine" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.script_player_engine" 作为相对导入
    或指定完整模块路径："src.business_logic.script_player_engine" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:81:53 - warning: "ScriptPlayerEngine" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:82:10 - error: 从 "business_logic.character_mapper" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.character_mapper" 作为相对导入
    或指定完整模块路径："src.business_logic.character_mapper" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:82:49 - warning: "CharacterMapper" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:83:10 - error: 从 "business_logic.metadata_manager" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.metadata_manager" 作为相对导入
    或指定完整模块路径："src.business_logic.metadata_manager" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:84:10 - error: 从 "ui.metadata_display_widget" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".ui.metadata_display_widget" 作为相对导入
    或指定完整模块路径："src.ui.metadata_display_widget" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:85:10 - error: 从 "ui.enhanced_file_dialog" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".ui.enhanced_file_dialog" 作为相对导入
    或指定完整模块路径："src.ui.enhanced_file_dialog" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:86:10 - error: 从 "ui.format_indicator_widget" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".ui.format_indicator_widget" 作为相对导入
    或指定完整模块路径："src.ui.format_indicator_widget" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:87:10 - error: 从 "ui.widgets.script_preview" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".ui.widgets.script_preview" 作为相对导入
    或指定完整模块路径："src.ui.widgets.script_preview" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:88:10 - error: 从 "business_logic.script_format_detector" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.script_format_detector" 作为相对导入
    或指定完整模块路径："src.business_logic.script_format_detector" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:89:10 - error: 从 "business_logic.loading_state_manager" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.loading_state_manager" 作为相对导入
    或指定完整模块路径："src.business_logic.loading_state_manager" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:90:10 - error: 从 "business_logic.error_handler" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".business_logic.error_handler" 作为相对导入
    或指定完整模块路径："src.business_logic.error_handler" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:91:10 - error: 从 "models.enums" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".models.enums" 作为相对导入
    或指定完整模块路径："src.models.enums" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:103:24 - warning: "debug_level" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:104:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_level` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:105:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_dir` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:106:14 - warning: 由于这个类未使用 `@final` 装饰，其 `session_log_file` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:107:14 - warning: 由于这个类未使用 `@final` 装饰，其 `key_events_log_file` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:108:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_matches_log_file` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:109:14 - warning: 由于这个类未使用 `@final` 装饰，其 `log_buffer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:110:14 - warning: 由于这个类未使用 `@final` 装饰，其 `max_log_size` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:113:14 - warning: 由于这个类未使用 `@final` 装饰，其 `level_names` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:167:9 - warning: "_write_to_log" 的类型部分未知
    "_write_to_log" 为 "(log_file: Unknown, message: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:167:100 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:172:29 - warning: "log_file" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:172:29 - warning: "log_file" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:172:39 - warning: "message" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:172:39 - warning: "message" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:182:23 - warning: 参数类型未知
    实参对应于 "open" 函数中的 "file" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:183:17 - warning: "int" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:185:29 - warning: 变量 "e" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:211:31 - warning: "level" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:211:31 - warning: "level" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:213:9 - warning: "old_level" 的类型部分未知
    "old_level" 为 "int | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:213:21 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:214:9 - warning: "debug_level" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:222:17 - warning: "_write_to_log" 的类型部分未知
    "_write_to_log" 为 "(log_file: Unknown, message: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:228:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:230:27 - warning: "message" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:230:27 - warning: "message" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:230:36 - warning: "level" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:230:45 - warning: "category" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:232:12 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:235:20 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:242:13 - warning: "formatted_message" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:246:19 - warning: 部分参数的类型未知
    实参对应于 "print" 函数中的 "values" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:249:21 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:251:23 - warning: 部分参数的类型未知
    实参对应于 "print" 函数中的 "values" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:255:17 - warning: "_write_to_log" 的类型部分未知
    "_write_to_log" 为 "(log_file: Unknown, message: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:255:62 - warning: 参数类型未知
    实参对应于 "_write_to_log" 函数中的 "message" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:257:17 - warning: "_write_to_log" 的类型部分未知
    "_write_to_log" 为 "(log_file: Unknown, message: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:257:66 - warning: 参数类型未知
    实参对应于 "_write_to_log" 函数中的 "message" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:259:17 - warning: "_write_to_log" 的类型部分未知
    "_write_to_log" 为 "(log_file: Unknown, message: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:261:33 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:261:43 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:263:9 - warning: "info" 的类型部分未知
    "info" 为 "dict[str, int | Unknown | str | None]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:264:22 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:265:48 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:265:48 - warning: 部分参数的类型未知
    实参对应于 "get" 函数中的 "key" 形参
    参数类型为 "int | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:273:21 - warning: 变量 "root" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:273:27 - warning: 变量 "dirs" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:274:21 - error: "int | Unknown | str | None" 与 "int" 类型不支持 "+=" 运算符
    "str" 与 "int" 类型不支持 "+" 运算符
    "None" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:278:16 - warning: 返回类型 "dict[str, int | Unknown | str | None]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:284:24 - warning: "current_level" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:284:41 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:284:41 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:285:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:291:14 - warning: 由于这个类未使用 `@final` 装饰，其 `selected_level` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:309:22 - error: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.color_config" 作为相对导入
    或指定完整模块路径："src.system_services.color_config" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:320:14 - warning: 由于这个类未使用 `@final` 装饰，其 `button_group` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:329:14 - warning: 由于这个类未使用 `@final` 装饰，其 `radio_buttons` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:341:13 - warning: "radio_buttons" 的类型部分未知
    "radio_buttons" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:358:14 - warning: 由于这个类未使用 `@final` 装饰，其 `ok_button` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:363:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:363:21 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:363:21 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:363:28 - error: 无法访问 "QObject" 类的 "color_manager" 属性
    属性 "color_manager" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:364:42 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:367:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:370:14 - warning: 由于这个类未使用 `@final` 装饰，其 `cancel_button` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:375:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:375:21 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:375:21 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:375:28 - error: 无法访问 "QObject" 类的 "color_manager" 属性
    属性 "color_manager" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:376:46 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:379:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:394:9 - warning: "accept" 方法没有用 `@override` 装饰，但覆写了 "QDialog" 类中的方法 (reportImplicitOverride)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:407:61 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:407:61 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:408:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:409:14 - warning: 由于这个类未使用 `@final` 装饰，其 `validation_result` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:461:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:466:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:479:5 - warning: 由于这个类未使用 `@final` 装饰，其 `ui_update_signal` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:480:5 - warning: 由于这个类未使用 `@final` 装饰，其 `action_match_signal` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:482:24 - warning: "color_manager" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:482:24 - warning: "color_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:491:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:494:14 - warning: 由于这个类未使用 `@final` 装饰，其 `script_validator` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:497:14 - warning: 由于这个类未使用 `@final` 装饰，其 `decryption_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:500:14 - warning: 由于这个类未使用 `@final` 装饰，其 `metadata_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:503:14 - warning: 由于这个类未使用 `@final` 装饰，其 `format_detector` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:506:14 - warning: 由于这个类未使用 `@final` 装饰，其 `loading_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:509:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_handler` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:512:9 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:512:14 - warning: 由于这个类未使用 `@final` 装饰，其 `color_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:518:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:529:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:530:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:531:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:532:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:533:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:534:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:535:25 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:536:24 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:537:29 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:538:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:539:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:540:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:541:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:542:30 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:543:34 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:544:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:545:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:546:28 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:547:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:548:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:551:14 - warning: 由于这个类未使用 `@final` 装饰，其 `character_mapping` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:558:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_display_mapping` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:567:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:576:14 - warning: 由于这个类未使用 `@final` 装饰，其 `is_switching_ui` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:579:14 - warning: 由于这个类未使用 `@final` 装饰，其 `ui_timer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:580:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:584:14 - warning: 由于这个类未使用 `@final` 装饰，其 `health_timer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:585:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:589:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:590:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:593:52 - error: "(state: LoadingState, message: str, progress: int) -> None" 类型的实参无法赋值给函数 "add_progress_callback" 中 "(LoadingState, int, str) -> None" 类型的形参 "callback"
    "(state: LoadingState, message: str, progress: int) -> None" 类型与 "(LoadingState, int, str) -> None" 类型不兼容
      第 2 个参数："int" 类型与 "str" 类型不兼容
        "int" 与 "str" 不兼容
      第 3 个参数："str" 类型与 "int" 类型不兼容
        "str" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:596:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_bar_labels` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:599:14 - warning: 由于这个类未使用 `@final` 装饰，其 `key_press_times` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:600:14 - warning: 由于这个类未使用 `@final` 装饰，其 `key_timeout_ms` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:603:9 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:603:14 - warning: 由于这个类未使用 `@final` 装饰，其 `keyboard_queue` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:604:14 - warning: 由于这个类未使用 `@final` 装饰，其 `keyboard_queue_maxlen` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:606:14 - warning: 由于这个类未使用 `@final` 装饰，其 `keyboard_process_timer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:607:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:610:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:612:31 - warning: "widget" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:612:31 - warning: "widget" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:618:13 - warning: "_" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:618:17 - warning: "isVisible" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:627:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:627:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:627:53 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:648:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:651:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:654:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:659:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:662:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:669:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:703:13 - warning: "action_bar_labels" 的类型部分未知
    "action_bar_labels" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:703:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:715:16 - warning: "action_bar_labels" 的类型部分未知
    "action_bar_labels" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:723:20 - warning: "label" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:723:39 - warning: "action_bar_labels" 的类型部分未知
    "action_bar_labels" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:723:39 - warning: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:725:24 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:725:45 - warning: 参数类型未知
    实参对应于 "is_widget_valid" 函数中的 "widget" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:730:21 - warning: "setText" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:733:21 - warning: "state" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:734:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:735:24 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:737:29 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:737:37 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:737:37 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:739:29 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:739:37 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:739:37 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:741:29 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:741:37 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:741:37 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:743:29 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:743:37 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:743:37 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:745:29 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:745:37 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:745:37 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:746:25 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:750:29 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:760:29 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:770:29 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:780:29 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:790:29 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:801:21 - warning: "setText" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:802:24 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:803:25 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:803:33 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:803:33 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:804:25 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:806:25 - warning: "setStyleSheet" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:821:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:853:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_bar` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:865:68 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:881:16 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:885:26 - error: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.color_config" 作为相对导入
    或指定完整模块路径："src.system_services.color_config" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:903:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:907:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:908:12 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:909:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:909:21 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:909:21 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:910:42 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:922:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:923:12 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:924:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:924:21 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:924:21 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:925:41 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:930:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:934:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:938:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:951:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:960:30 - error: 无法为 "ScriptPlayer*" 类的 "loop_checkbox" 属性赋值
    "QPushButton" 类型与 "QCheckBox | None" 类型不兼容
      "QPushButton" 与 "QCheckBox" 不兼容
      "QPushButton" 与 "None" 不兼容 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:961:28 - error: `None` 没有 "setCheckable" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:962:28 - error: `None` 没有 "setChecked" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:963:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:963:28 - error: `None` 没有 "clicked" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:965:31 - error: "QCheckBox | None" 类型的实参无法赋值给函数 "addWidget" 中 "QWidget" 类型的形参 "arg__1"
    "QCheckBox | None" 类型与 "QWidget" 类型不兼容
      "None" 与 "QWidget" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:971:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:972:12 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:973:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:973:21 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:973:21 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:974:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1073:12 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1077:22 - error: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.color_config" 作为相对导入
    或指定完整模块路径："src.system_services.color_config" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1105:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1106:12 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1107:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1107:21 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1107:21 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1108:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1174:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1179:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1181:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1183:9 - warning: "eventFilter" 方法没有用 `@override` 装饰，但覆写了 "QObject" 类中的方法 (reportImplicitOverride)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1183:27 - warning: "obj" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1183:27 - warning: "obj" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1183:32 - warning: "event" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1183:32 - warning: "event" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1185:12 - warning: "type" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1188:16 - warning: "key" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1188:55 - warning: "key" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1189:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1189:69 - warning: "key" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1189:90 - warning: "text" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1193:36 - warning: 参数类型未知
    实参对应于 "eventFilter" 函数中的 "watched" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1193:41 - warning: 参数类型未知
    实参对应于 "eventFilter" 函数中的 "event" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1197:14 - warning: 由于这个类未使用 `@final` 装饰，其 `keyboard_listener` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1198:14 - warning: 由于这个类未使用 `@final` 装饰，其 `mouse_listener` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1203:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1207:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1209:30 - warning: "on_key_press" 的类型部分未知
    "on_key_press" 为 "(key: Unknown) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1209:30 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "on_press" 形参
    参数类型为 "(key: Unknown) -> Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1210:32 - warning: "on_key_release" 的类型部分未知
    "on_key_release" 为 "(key: Unknown) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1210:32 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "on_release" 形参
    参数类型为 "(key: Unknown) -> Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1213:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1215:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1218:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1220:30 - warning: "on_mouse_click" 的类型部分未知
    "on_mouse_click" 为 "(x: Unknown, y: Unknown, button: Unknown, pressed: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1220:30 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "on_click" 形参
    参数类型为 "(x: Unknown, y: Unknown, button: Unknown, pressed: Unknown) -> None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1223:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1225:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1228:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1234:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1238:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1241:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1244:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1247:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1250:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1256:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1268:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1271:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1280:13 - warning: "key_char" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1280:23 - warning: "press_time" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1280:37 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1282:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1282:37 - warning: 参数类型未知
    实参对应于 "append" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1284:13 - warning: "key_char" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1285:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1285:89 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1286:17 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1288:20 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1295:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1298:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1306:9 - warning: "bool" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1314:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1315:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1319:9 - warning: 返回类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1319:28 - warning: "key" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1319:28 - warning: "key" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1325:24 - warning: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1325:41 - warning: "char" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1326:17 - warning: "key_char" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1326:28 - warning: "char" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1331:21 - warning: "event" 的类型部分未知
    "event" 为 "dict[str, str | Unknown | int]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1337:21 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1337:21 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1338:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1343:21 - warning: "event" 的类型部分未知
    "event" 为 "dict[str, str | Unknown | int]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1349:21 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1349:21 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1350:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1361:21 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1361:21 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1362:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1374:17 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1374:17 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1375:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1385:17 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1385:17 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1386:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1390:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1394:9 - warning: 返回类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1394:30 - warning: "key" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1394:30 - warning: "key" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1400:24 - warning: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1400:41 - warning: "char" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1401:17 - warning: "key_char" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1401:28 - warning: "char" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1411:21 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1411:21 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1412:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1417:21 - warning: "event" 的类型部分未知
    "event" 为 "dict[str, str | Unknown | int]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1423:21 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1423:21 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1424:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1436:17 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1436:17 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1437:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1447:17 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1447:17 - warning: "append" 的类型部分未知
    "append" 为 "(x: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1448:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1452:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:30 - warning: "x" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:30 - warning: "x" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:30 - warning: "x" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:33 - warning: "y" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:33 - warning: "y" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:33 - warning: "y" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:36 - warning: "button" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:36 - warning: "button" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:44 - warning: "pressed" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1456:44 - warning: "pressed" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1475:13 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1476:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1479:26 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1480:17 - warning: "press_time" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1480:30 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1481:17 - warning: "duration" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1483:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1489:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1493:21 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1498:16 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1498:16 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "deque[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1499:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1499:63 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1499:63 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "deque[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1501:23 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1501:23 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "deque[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1502:17 - warning: "old_event" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1502:29 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1503:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1508:16 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1509:31 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1509:31 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "deque[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1510:17 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1511:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1516:15 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1517:13 - warning: "event" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1517:21 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1518:13 - warning: "_process_single_keyboard_event" 的类型部分未知
    "_process_single_keyboard_event" 为 "(event: Unknown) -> Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1518:49 - warning: 参数类型未知
    实参对应于 "_process_single_keyboard_event" 函数中的 "event" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1522:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1527:18 - warning: 由于这个类未使用 `@final` 装饰，其 `_last_space_check` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1527:18 - error: 实例变量 "_last_space_check" 未在类体或 `__init__` 方法中初始化 (reportUninitializedInstanceVariable)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1536:19 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1537:13 - warning: "press_time" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1537:26 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1538:13 - warning: "elapsed" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1541:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1545:21 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1547:9 - warning: 返回类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1547:46 - warning: "event" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1547:46 - warning: "event" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1550:13 - warning: "event_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1551:13 - warning: "key_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1552:13 - warning: "key_char" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1553:13 - warning: "timestamp" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1560:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1566:40 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1567:25 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1568:25 - warning: "key_name" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1569:25 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1579:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1583:36 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1584:25 - warning: "press_time" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1584:38 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1585:25 - warning: "duration" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1597:29 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1599:25 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1601:25 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1608:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1611:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1618:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1622:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1628:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1632:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1638:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1641:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1647:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1648:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1649:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1653:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1656:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1659:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1667:35 - error: `None` 没有 "show_loading_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1669:35 - error: `None` 没有 "show_loading_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1671:35 - error: `None` 没有 "show_loading_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1673:35 - error: `None` 没有 "show_loading_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1698:32 - warning: "error_type" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1701:31 - error: `None` 没有 "show_error_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1704:9 - warning: "int" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1704:52 - error: "str" 类型的实参无法赋值给函数 "show_error_dialog" 中 "ErrorType" 类型的形参 "error_type"
    "str" 与 "ErrorType" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1710:24 - warning: "get_open_file_name_with_preview" 的类型部分未知
    "get_open_file_name_with_preview" 为 "(parent: Unknown | None = None, caption: str = "选择脚本文件", directory: str = "", filter: str = "") -> tuple[str, str]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1728:17 - warning: "int" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1730:21 - error: "Literal['不支持的文件格式']" 类型的实参无法赋值给函数 "show_error_dialog" 中 "ErrorType" 类型的形参 "error_type"
    "Literal['不支持的文件格式']" 与 "ErrorType" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1731:21 - error: "Literal['请选择 .json 或 .wuwa_enc 格式的脚本文件']" 类型的实参无法赋值给函数 "show_error_dialog" 中 "Exception" 类型的形参 "original_error"
    "Literal['请选择 .json 或 .wuwa_enc 格式的脚本文件']" 与 "Exception" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1736:35 - error: `None` 没有 "update_format" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1747:43 - error: `None` 没有 "show_error_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1753:43 - error: `None` 没有 "show_error_state" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1763:43 - error: `None` 没有 "update_format" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1766:43 - error: `None` 没有 "update_format" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1769:35 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1773:58 - warning: "metadata" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1773:80 - error: 无法访问 "MetadataManager" 类的 "metadata" 属性
    属性 "metadata" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1774:21 - warning: "update_team_characters" 的类型部分未知
    "update_team_characters" 为 "(metadata: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1774:49 - warning: "metadata" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1774:49 - warning: 参数类型未知
    实参对应于 "update_team_characters" 函数中的 "metadata" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1774:71 - error: 无法访问 "MetadataManager" 类的 "metadata" 属性
    属性 "metadata" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1777:51 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1778:36 - error: `None` 没有 "setEnabled" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1785:34 - warning: "json_data" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1785:34 - warning: "json_data" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1793:9 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1793:38 - warning: "json_data" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1793:38 - warning: "json_data" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1793:49 - warning: "format_type" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1793:49 - warning: "format_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1798:17 - warning: "segment" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1798:28 - warning: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1799:17 - warning: "segment_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1799:32 - warning: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1800:17 - warning: "events" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1800:26 - warning: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1802:21 - warning: "event" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1804:21 - warning: "event_with_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1804:39 - warning: "copy" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1806:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1806:39 - warning: 参数类型未知
    实参对应于 "append" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1807:20 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1811:35 - warning: "events" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1811:35 - warning: "events" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1811:43 - warning: "event_type" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1811:43 - warning: "event_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1811:43 - warning: "event_type" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1813:13 - warning: "item" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1817:17 - warning: "segment_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1817:32 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1822:31 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1822:31 - warning: 参数类型未知
    实参对应于 "__init__" 函数中的 "timestamp" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1823:35 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1823:35 - warning: 参数类型未知
    实参对应于 "__init__" 函数中的 "relative_time" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1825:35 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1825:35 - warning: 参数类型未知
    实参对应于 "__init__" 函数中的 "key_or_action" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1826:28 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1826:28 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "remark" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1831:52 - warning: 参数类型未知
    实参对应于 "__init__" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1836:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1841:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1845:17 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1856:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1860:17 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1862:17 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1864:17 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1866:17 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1870:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1870:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1877:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1881:13 - warning: "metadata" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1883:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1887:13 - warning: "segments" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1888:54 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1889:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1893:13 - warning: "first_segment" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1895:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1901:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1904:70 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1904:80 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1904:89 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1904:99 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1913:13 - warning: "metadata" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1914:13 - warning: "characters" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1914:26 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1922:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1922:58 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1927:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1930:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1930:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1937:39 - error: 无法为 "MetadataManager" 类的 "metadata" 属性赋值
    属性 "metadata" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1944:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1946:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1950:13 - warning: "characters" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1953:13 - warning: "events_data" 的类型部分未知
    "events_data" 为 "list[Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1953:27 - warning: "parse_events_by_format" 的类型部分未知
    "parse_events_by_format" 为 "(json_data: Unknown, format_type: Unknown) -> list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1961:17 - warning: "segment" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1962:20 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1963:48 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1963:48 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1964:22 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1965:46 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1965:46 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1970:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1970:62 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1971:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1975:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1976:21 - warning: "key" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1976:26 - warning: "name" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1976:34 - warning: "items" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1977:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1979:57 - warning: 参数类型为 `Any`
    实参对应于 "update_character_mapping_from_json" 函数中的 "characters" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1983:13 - warning: "parse_script_events" 的类型部分未知
    "parse_script_events" 为 "(events: Unknown, event_type: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1985:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1991:48 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1993:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1994:17 - warning: "event_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1994:29 - warning: "count" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1995:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:1999:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2006:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2014:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2018:17 - warning: "data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2022:78 - warning: 参数类型为 `Any`
    实参对应于 "extract_metadata" 函数中的 "script_data" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2025:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2027:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2030:27 - warning: "detect_json_format" 的类型部分未知
    "detect_json_format" 为 "(json_data: Unknown) -> Literal['segments']" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2030:51 - warning: 参数类型为 `Any`
    实参对应于 "detect_json_format" 函数中的 "json_data" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2033:13 - warning: "characters" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2033:26 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2035:17 - warning: "characters" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2035:30 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2036:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2039:13 - warning: "events_data" 的类型部分未知
    "events_data" 为 "list[Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2039:27 - warning: "parse_events_by_format" 的类型部分未知
    "parse_events_by_format" 为 "(json_data: Unknown, format_type: Unknown) -> list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2039:55 - warning: 参数类型为 `Any`
    实参对应于 "parse_events_by_format" 函数中的 "json_data" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2047:17 - warning: "segment" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2047:28 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2048:20 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2049:48 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2049:48 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2050:22 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2051:46 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2051:46 - warning: 参数类型为 `Any`
    实参对应于 "len" 函数中的 "obj" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2056:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2057:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2060:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2061:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2062:17 - warning: "key" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2062:22 - warning: "name" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2062:30 - warning: "items" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2063:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2067:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2068:57 - warning: 参数类型为 `Any`
    实参对应于 "update_character_mapping_from_json" 函数中的 "characters" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2069:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2073:13 - warning: "parse_script_events" 的类型部分未知
    "parse_script_events" 为 "(events: Unknown, event_type: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2079:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2081:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2087:48 - warning: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2089:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2090:17 - warning: "event_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2090:29 - warning: "count" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2091:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2094:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2099:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2100:13 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2113:62 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2113:72 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2115:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2128:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2131:17 - warning: "char_name" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2139:46 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2140:13 - warning: "set_character_mapping" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2140:31 - error: 无法访问 "QTableWidget" 类的 "set_character_mapping" 属性
    属性 "set_character_mapping" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2140:31 - error: `None` 没有 "set_character_mapping" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2141:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2147:20 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2151:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2153:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2158:13 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2202:17 - warning: 变量 "slot" 未使用 (reportUnusedVariable)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2210:27 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2216:43 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2217:28 - error: `None` 没有 "setEnabled" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2219:9 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2221:38 - warning: "metadata" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2221:38 - warning: "metadata" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2223:32 - warning: "characters" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2230:13 - warning: "char_key" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2230:23 - warning: "char_name" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2230:36 - warning: "characters" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2230:36 - warning: "items" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2234:57 - warning: 参数类型未知
    实参对应于 "setText" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2236:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2236:52 - warning: "characters" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2264:16 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2268:13 - warning: "update_script_data" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2268:31 - error: 无法访问 "QTableWidget" 类的 "update_script_data" 属性
    属性 "update_script_data" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2268:31 - error: `None` 没有 "update_script_data" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2277:31 - error: 无法为 "QTableWidget" 类的 "_last_script_actions" 属性赋值
    属性 "_last_script_actions" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2277:31 - error: `None` 没有 "_last_script_actions" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2278:31 - error: 无法为 "QTableWidget" 类的 "_last_current_index" 属性赋值
    属性 "_last_current_index" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2278:31 - error: `None` 没有 "_last_current_index" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2279:31 - error: 无法为 "QTableWidget" 类的 "_last_script_status" 属性赋值
    属性 "_last_script_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2279:31 - error: `None` 没有 "_last_script_status" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2280:31 - error: 无法为 "QTableWidget" 类的 "_last_has_start_events" 属性赋值
    属性 "_last_has_start_events" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2280:31 - error: `None` 没有 "_last_has_start_events" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2281:31 - error: 无法为 "QTableWidget" 类的 "_last_loop_start_index" 属性赋值
    属性 "_last_loop_start_index" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2281:31 - error: `None` 没有 "_last_loop_start_index" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2282:31 - error: 无法为 "QTableWidget" 类的 "_last_current_loop" 属性赋值
    属性 "_last_current_loop" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2282:31 - error: `None` 没有 "_last_current_loop" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2289:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2294:13 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2297:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2298:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2299:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2300:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2303:9 - warning: "bool | None" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2306:12 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2307:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2307:65 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2307:65 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "dict_keys[Unknown, Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2308:13 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2310:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2315:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2317:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2322:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2330:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2332:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2391:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2398:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2402:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2409:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2413:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2416:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2419:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2423:21 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2428:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2432:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2445:48 - error: `None` 没有 "isChecked" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2446:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2450:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2455:17 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2456:17 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2457:17 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2465:27 - error: `None` 没有 "setEnabled" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2466:28 - error: `None` 没有 "setEnabled" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2467:27 - error: `None` 没有 "setEnabled" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2471:31 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2472:20 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2473:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2473:49 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2473:49 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2473:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2474:36 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2474:50 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2474:50 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2474:50 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2475:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2475:49 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2475:49 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2475:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2477:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2478:36 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2479:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2480:32 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2482:31 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2483:20 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2484:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2484:49 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2484:49 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2484:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2485:36 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2485:50 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2485:50 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2485:50 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2486:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2486:49 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2486:49 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2486:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2488:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2489:36 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2490:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2491:32 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2493:31 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2494:20 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2495:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2495:49 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2495:49 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2495:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2496:36 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2496:50 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2496:50 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2496:50 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2497:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2497:49 - warning: "color_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2497:49 - warning: "get_button_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2497:49 - warning: 参数类型未知
    实参对应于 "setStyleSheet" 函数中的 "styleSheet" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2499:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2500:36 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2501:35 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2502:32 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2505:47 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2509:32 - error: `None` 没有 "setEnabled" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2515:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2528:17 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2534:43 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2538:24 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2542:34 - error: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.color_config" 作为相对导入
    或指定完整模块路径："src.system_services.color_config" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2546:52 - error: "Literal['bg']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['bg']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['bg']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['bg']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2547:52 - error: "Literal['border']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['border']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['border']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['border']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2550:41 - error: "Literal['text']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['text']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['text']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['text']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2554:51 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2556:51 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2567:24 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2571:34 - error: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.color_config" 作为相对导入
    或指定完整模块路径："src.system_services.color_config" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2575:52 - error: "Literal['bg']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['bg']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['bg']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['bg']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2576:52 - error: "Literal['border']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['border']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['border']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['border']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2579:41 - error: "Literal['text']" 类型的实参无法赋值给函数 "__getitem__" 中 "SupportsIndex | slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['text']" 类型与 "SupportsIndex | slice[Any, Any, Any]" 类型不兼容
      "Literal['text']" 与 Protocol 类 "SupportsIndex" 不兼容
        "__index__" 不存在
      "Literal['text']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2582:51 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2584:51 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2593:18 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2594:43 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2597:16 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2599:42 - error: `None` 没有 "setMaximum" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2600:42 - error: `None` 没有 "setValue" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2602:42 - error: `None` 没有 "setMaximum" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2603:42 - error: `None` 没有 "setValue" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2606:16 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2618:35 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2621:16 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2623:37 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2625:37 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2632:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2634:9 - warning: "closeEvent" 方法没有用 `@override` 装饰，但覆写了 "QWidget" 类中的方法 (reportImplicitOverride)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2634:26 - warning: "event" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2634:26 - warning: "event" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2637:9 - warning: "accept" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2641:9 - warning: "current_level" 的类型部分未知
    "current_level" 为 "int | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2641:25 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2642:38 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "current_level" 形参
    参数类型为 "int | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2646:13 - warning: "set_debug_level" 的类型部分未知
    "set_debug_level" 为 "(level: Unknown) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2651:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2655:52 - warning: "is_widget_valid" 的类型部分未知
    "is_widget_valid" 为 "(widget: Unknown) -> bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2656:13 - warning: "level" 的类型部分未知
    "level" 为 "int | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2656:21 - warning: "debug_level" 的类型部分未知
    "debug_level" 为 "int | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2658:42 - warning: 部分参数的类型未知
    实参对应于 "get" 函数中的 "key" 形参
    参数类型为 "int | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2660:37 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2663:16 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2667:26 - error: 从 "system_services.color_config" 导入会进行隐式的相对导入，如果此文件作为模块导入则会出错
    请改用 ".system_services.color_config" 作为相对导入
    或指定完整模块路径："src.system_services.color_config" (reportImplicitRelativeImport)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2668:54 - warning: 部分参数的类型未知
    实参对应于 "get" 函数中的 "key" 形参
    参数类型为 "int | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2671:36 - warning: 部分参数的类型未知
    实参对应于 "get" 函数中的 "key" 形参
    参数类型为 "int | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2672:37 - error: `None` 没有 "setStyleSheet" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2676:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2681:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2688:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2692:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2697:13 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2701:30 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2701:30 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "deque[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2703:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2704:17 - warning: "keyboard_queue" 的类型部分未知
    "keyboard_queue" 为 "deque[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2708:16 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2709:17 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2709:64 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2709:64 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "dict_keys[Unknown, Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2710:13 - warning: "key_press_times" 的类型部分未知
    "key_press_times" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2715:9 - warning: "debug_print" 的类型部分未知
    "debug_print" 为 "(message: Unknown, level: int = 1, category: str = "GENERAL") -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2718:32 - warning: "app" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2718:32 - warning: "app" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2733:17 - warning: "setStyle" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2737:17 - warning: "setStyle" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2744:9 - warning: "setStyle" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2748:34 - warning: "app" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2748:34 - warning: "app" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2752:5 - warning: "palette" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2752:15 - warning: "palette" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2755:5 - warning: "setColor" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2756:5 - warning: "setColor" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2757:5 - warning: "setColor" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2758:5 - warning: "setColor" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2759:5 - warning: "setColor" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2761:5 - warning: "setPalette" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2765:40 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2765:50 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2779:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2783:13 - warning: "style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2783:21 - warning: "style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2783:25 - error: 无法访问 "QCoreApplication" 类的 "style" 属性
    属性 "style" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2785:17 - warning: "current_style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2785:33 - warning: "objectName" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2785:33 - warning: "lower" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2791:21 - warning: "setStyle" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2791:25 - error: 无法访问 "QCoreApplication" 类的 "setStyle" 属性
    属性 "setStyle" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2792:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2795:25 - warning: "setStyle" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2795:29 - error: 无法访问 "QCoreApplication" 类的 "setStyle" 属性
    属性 "setStyle" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2796:25 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2798:25 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2810:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2811:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2813:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2825:33 - warning: "app" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2825:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2825:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2832:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2832:27 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2840:13 - warning: "issue" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2845:13 - warning: "fix" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\main.py:2858:43 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\models\script_action.py
  d:\GITHUB\wuwa_actionseq_player\src\models\script_action.py:8:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_action.py:21:13 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:9:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:9:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:9:32 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:25:17 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:26:19 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:27:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:30:11 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:38:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:38:61 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:38:83 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:55:17 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:57:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:80:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:80:36 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:108:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:108:40 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130:22 - error: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "title"
    "Any | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130:22 - error: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "description"
    "Any | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130:22 - error: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "Dict[str, str]" 类型的形参 "characters"
    "Any | None" 类型与 "Dict[str, str]" 类型不兼容
      "None" 与 "Dict[str, str]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130:22 - error: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "version"
    "Any | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130:22 - error: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "str" 类型的形参 "author"
    "Any | None" 类型与 "str" 类型不兼容
      "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:130:22 - error: "Any | None" 类型的实参无法赋值给函数 "__init__" 中 "List[str]" 类型的形参 "tags"
    "Any | None" 类型与 "List[str]" 类型不兼容
      "None" 与 "List[str]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:143:9 - warning: "data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:144:30 - warning: 参数类型为 `Any`
    实参对应于 "from_dict" 函数中的 "data" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:146:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:146:48 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:158:36 - warning: 参数类型为 `Any`
    实参对应于 "update" 函数中的 "m" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:172:9 - warning: "__str__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_metadata.py:176:9 - warning: "__repr__" 方法没有用 `@override` 装饰，但覆写了 "object" 类中的方法 (reportImplicitOverride)
d:\GITHUB\wuwa_actionseq_player\src\models\script_models.py
  d:\GITHUB\wuwa_actionseq_player\src\models\script_models.py:19:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\script_models.py:19:20 - warning: "Optional" 导入项未使用 (reportUnusedImport)
d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py
  d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py:8:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py:8:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py:19:18 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py:20:17 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py:30:13 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\models\validation_models.py:31:18 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\qa\__init__.py
  d:\GITHUB\wuwa_actionseq_player\src\qa\__init__.py:14:5 - warning: "run_qa_tests" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\qa\__init__.py:15:5 - warning: "test_key_recognition" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\qa\__init__.py:16:5 - warning: "validate_input_system" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:12:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:12:20 - warning: "List" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:12:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:12:26 - warning: "Dict" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:12:32 - warning: "Any" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:13:25 - warning: "dataclass" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:21:14 - warning: 由于这个类未使用 `@final` 装饰，其 `test_name` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:22:14 - warning: 由于这个类未使用 `@final` 装饰，其 `passed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:23:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_message` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:24:14 - warning: 由于这个类未使用 `@final` 装饰，其 `fix_applied` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:25:14 - warning: 由于这个类未使用 `@final` 装饰，其 `details` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:28:9 - warning: "details" 的类型部分未知
    "details" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:28:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:30:9 - warning: 返回类型 "dict[str, str | bool | list[Unknown]]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:31:16 - warning: 返回类型 "dict[str, str | bool | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:36:24 - warning: "details" 的类型部分未知
    "details" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:43:14 - warning: 由于这个类未使用 `@final` 装饰，其 `test_results` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:44:14 - warning: 由于这个类未使用 `@final` 装饰，其 `script_file` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:45:14 - warning: 由于这个类未使用 `@final` 装饰，其 `backup_file` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:47:9 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:65:9 - warning: "bool" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:67:16 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:67:16 - warning: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:101:9 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:101:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:105:13 - warning: "detail" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:105:23 - warning: "details" 的类型部分未知
    "details" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:131:21 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:146:25 - warning: "json_data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:149:25 - warning: "chars" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:157:33 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:159:61 - warning: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:165:9 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:165:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:169:13 - warning: "detail" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:169:23 - warning: "details" 的类型部分未知
    "details" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:184:21 - warning: "int" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:200:21 - warning: "int" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:214:9 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:214:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:218:13 - warning: "detail" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:218:23 - warning: "details" 的类型部分未知
    "details" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:245:25 - warning: "match" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:245:25 - warning: "match" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:245:25 - warning: "match" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:253:32 - warning: 部分参数的类型未知
    实参对应于 "sub" 函数中的 "repl" 形参
    参数类型为 "(match: Unknown) -> LiteralString" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:283:17 - warning: "CodeType" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:294:9 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:294:9 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:298:13 - warning: "detail" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:298:23 - warning: "details" 的类型部分未知
    "details" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:306:27 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:306:27 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:307:34 - warning: "r" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:307:39 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:307:60 - warning: "passed" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:315:35 - warning: "r" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:315:40 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:315:61 - warning: "fix_applied" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:320:16 - warning: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:320:36 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:320:36 - warning: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:321:37 - warning: "passed" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:322:27 - warning: "test_name" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:323:16 - warning: "error_message" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:324:33 - warning: "error_message" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:327:9 - warning: "report_data" 的类型部分未知
    "report_data" 为 "dict[str, Any | int | float | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:328:26 - warning: "datetime" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:328:26 - warning: "now" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:328:26 - warning: "isoformat" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:333:30 - warning: "to_dict" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:333:46 - warning: "r" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:333:51 - warning: "test_results" 的类型部分未知
    "test_results" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\qa\qa_key_recognition_test.py:349:5 - warning: "success" 的类型部分未知
    "success" 为 "list[Unknown]" 类型 (reportUnknownVariableType)
d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:8:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:8:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:8:31 - warning: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:25:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_patterns` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:38:14 - warning: 由于这个类未使用 `@final` 装饰，其 `error_details` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:87:14 - warning: 由于这个类未使用 `@final` 装饰，其 `default_error` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:112:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:124:33 - warning: "parent_widget" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:124:33 - warning: "parent_widget" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:146:9 - warning: "StandardButton" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:147:13 - warning: 参数类型未知
    实参对应于 "critical" 函数中的 "parent" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:167:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:167:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:167:65 - error: 无法将 "None" 类型的表达式赋值给 "Dict[str, Any]" 类型的参数
    "None" 与 "Dict[str, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:167:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:167:84 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:201:28 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:201:38 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:201:45 - error: 无法将 "None" 类型的表达式赋值给 "Dict[str, Any]" 类型的参数
    "None" 与 "Dict[str, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\services\error_handling_service.py:210:16 - warning: "datetime" 导入项未使用 (reportUnusedImport)
d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:8:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:8:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:24:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:25:30 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:28:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:39:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:57:65 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\loading_state_manager.py:73:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\services\script_format_detector.py
  d:\GITHUB\wuwa_actionseq_player\src\services\script_format_detector.py:9:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\services\script_format_detector.py:9:20 - warning: "Optional" 导入项未使用 (reportUnusedImport)
d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:18:5 - error: 不能重新定义常量 "_COLOR_CONFIG_AVAILABLE"（全大写名称） (reportConstantRedefinition)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:24:5 - error: 不能重新定义常量 "_COLOR_PATCH_AVAILABLE"（全大写名称） (reportConstantRedefinition)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:38:9 - warning: "get_color_scheme" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:39:9 - warning: "get_color_config" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:40:9 - warning: "PRIMARY_BLUE" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:41:9 - warning: "DARK_MODE_COLORS" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:42:9 - warning: "LIGHT_MODE_COLORS" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\__init__.py:46:20 - warning: "apply_cross_platform_patch" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "tuple" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:26 - warning: "Tuple" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:38 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:38 - warning: "List" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:44 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:11:44 - warning: "Union" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:23:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_BLUE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:24:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_GREEN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:25:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_RED` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:26:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_ORANGE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:27:5 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_PURPLE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:34:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DARK_MODE_COLORS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:97:5 - warning: 由于这个类未使用 `@final` 装饰，其 `ACTION_STATES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:135:5 - warning: 由于这个类未使用 `@final` 装饰，其 `BUTTON_STATES` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:169:5 - warning: 由于这个类未使用 `@final` 装饰，其 `SYSTEM_PALETTE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:178:5 - warning: 由于这个类未使用 `@final` 装饰，其 `UI_COMPONENTS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:202:5 - warning: 由于这个类未使用 `@final` 装饰，其 `DEBUG_LEVELS` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:213:42 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:213:52 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:218:22 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:218:32 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:228:17 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:232:13 - warning: "palette_adjustments" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:232:13 - warning: "palette_adjustments" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:232:79 - warning: 类型注释已弃用；请改用类型注解 (reportTypeCommentUsage)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:232:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:232:89 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:237:13 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:238:13 - warning: "palette_adjustments" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:238:79 - warning: 类型注释已弃用；请改用类型注解 (reportTypeCommentUsage)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:238:79 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:238:89 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:296:13 - warning: "config" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:296:22 - error: "str | dict[str, str]" 类型不匹配声明的 "Dict[str, str]" 类型
    "str | dict[str, str]" 类型与 "Dict[str, str]" 类型不兼容
      "str" 与 "Dict[str, str]" 不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:296:75 - warning: 类型注释已弃用；请改用类型注解 (reportTypeCommentUsage)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:296:75 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:298:22 - error: "str | dict[str, str]" 类型不匹配声明的 "Dict[str, str]" 类型
    "str | dict[str, str]" 类型与 "Dict[str, str]" 类型不兼容
      "str" 与 "Dict[str, str]" 不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:298:74 - warning: 类型注释已弃用；请改用类型注解 (reportTypeCommentUsage)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:298:74 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:325:12 - warning: "get" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:378:32 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:378:42 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:402:17 - warning: "QColor" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:406:17 - warning: "QColor" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:407:17 - warning: "QColor" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\color_config.py:408:17 - warning: "QColor" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:26 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:26 - warning: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:36 - warning: 此类型自 Python 3.10 起已弃用；请改用 "|" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:36 - warning: "Union" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:63 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:11:63 - warning: "List" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:14:28 - warning: "Qt" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:17:31 - error: "type[src.system_services.color_config.ColorConfig]" 类型不匹配声明的 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型
    "src.system_services.color_config.ColorConfig" 与 "src.system_services.cross_platform_color_patch.ColorConfig" 不兼容
    "type[src.system_services.color_config.ColorConfig]" 类型与 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:21:31 - error: "type[src.system_services.color_config.ColorConfig]" 类型不匹配声明的 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型
    "src.system_services.color_config.ColorConfig" 与 "src.system_services.cross_platform_color_patch.ColorConfig" 不兼容
    "type[src.system_services.color_config.ColorConfig]" 类型与 "type[src.system_services.cross_platform_color_patch.ColorConfig]" 类型不兼容 (reportAssignmentType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:25:9 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_BLUE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:26:9 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_GREEN` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:27:9 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_RED` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:28:9 - warning: 由于这个类未使用 `@final` 装饰，其 `PRIMARY_ORANGE` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:35:14 - warning: 由于这个类未使用 `@final` 装饰，其 `system` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:36:14 - warning: 由于这个类未使用 `@final` 装饰，其 `qt_version` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:37:14 - warning: 由于这个类未使用 `@final` 装饰，其 `color_adjustments` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:38:14 - warning: 由于这个类未使用 `@final` 装饰，其 `is_windows_dark_mode` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:58:17 - warning: "value" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:59:17 - warning: "is_windows_dark_mode" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:93:21 - warning: "QStyle | None" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:97:25 - warning: "QStyle | None" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:106:17 - warning: "QStyle | None" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:151:13 - warning: "base_style" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:151:26 - warning: "get_action_bar_style" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:151:38 - error: 无法访问 "type[ColorConfig]" 类的 "get_action_bar_style" 属性
    属性 "get_action_bar_style" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:159:16 - warning: 返回类型 "Unknown | str" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:242:59 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:242:69 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:244:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:244:30 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:255:17 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:256:17 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:260:13 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:261:13 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:268:17 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:269:17 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:271:13 - warning: "append" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:299:13 - warning: "issue" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\cross_platform_color_patch.py:304:13 - warning: "rec" 的类型为 `Any` (reportAny)
d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:14:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:14:31 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:17:6 - error: 无法解析导入 "cryptography.hazmat.primitives.ciphers" (reportMissingImports)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:17:52 - warning: "Cipher" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:17:60 - warning: "algorithms" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:17:72 - warning: "modes" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:18:6 - error: 无法解析导入 "cryptography.hazmat.primitives" (reportMissingImports)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:18:44 - warning: "padding" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:19:6 - error: 无法解析导入 "cryptography.hazmat.backends" (reportMissingImports)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:19:42 - warning: "default_backend" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:36:5 - warning: 由于这个类未使用 `@final` 装饰，其 `_ENCRYPTION_KEY` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:38:24 - warning: "debug_manager" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:38:24 - warning: "debug_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:45:9 - warning: "_backend" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:45:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_backend` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:46:9 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:46:14 - warning: 由于这个类未使用 `@final` 装饰，其 `debug_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:49:42 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:49:85 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:49:95 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:65:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:66:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:66:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:87:17 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:98:17 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:103:17 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:105:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:106:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:106:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:113:17 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:141:12 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:142:13 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:142:13 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:161:16 - warning: "debug_manager" 的类型部分未知
    "debug_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:162:17 - warning: "debug_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:162:17 - warning: "debug_print" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:191:55 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:191:65 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:210:13 - warning: "cipher" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:210:29 - warning: "AES" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:210:50 - warning: "CBC" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:210:73 - warning: "_backend" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:211:13 - warning: "decryptor" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:211:25 - warning: "decryptor" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:212:13 - warning: "padded_plaintext" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:212:32 - warning: "update" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:212:63 - warning: "finalize" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:215:13 - warning: "unpadder" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:215:24 - warning: "PKCS7" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:215:24 - warning: "unpadder" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:216:13 - warning: "plaintext" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:216:25 - warning: "update" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:216:61 - warning: "finalize" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:219:13 - warning: "json_str" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:219:24 - warning: "decode" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:220:13 - warning: "script_data" 的类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:220:38 - warning: 参数类型未知
    实参对应于 "loads" 函数中的 "s" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:223:43 - warning: 参数类型为 `Any`
    实参对应于 "_validate_decrypted_data" 函数中的 "script_data" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:225:20 - warning: 返回类型为 `Any` (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:259:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:259:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:269:16 - warning: "Dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:270:13 - warning: 代码不会被执行 (reportUnreachable)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:288:16 - warning: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\system_services\decryption_service.py:292:9 - warning: "first_segment" 类型未知 (reportUnknownVariableType)
d:\GITHUB\wuwa_actionseq_player\src\ui\__init__.py
  d:\GITHUB\wuwa_actionseq_player\src\ui\__init__.py:18:5 - warning: "ScriptPlayer" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\ui\__init__.py:19:5 - warning: "DebugSettingsDialog" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\ui\__init__.py:20:5 - warning: "ValidationErrorDialog" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
  d:\GITHUB\wuwa_actionseq_player\src\ui\__init__.py:21:5 - warning: "ScriptPreviewTable" 已在 `__all__` 中声明，但未在模块中定义 (reportUnsupportedDunderAll)
d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:13:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:13:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:14:21 - warning: "Path" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:17:31 - warning: "QHBoxLayout" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:18:29 - warning: "QDialogButtonBox" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:18:58 - warning: "QWidget" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:20:32 - warning: "QFileInfo" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:30:24 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:30:24 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:37:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:39:14 - warning: 由于这个类未使用 `@final` 装饰，其 `format_detector` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:40:14 - warning: 由于这个类未使用 `@final` 装饰，其 `decryption_service` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:41:14 - warning: 由于这个类未使用 `@final` 装饰，其 `preview_timer` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:43:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:49:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:50:9 - warning: "Connection" 类型调用表达式的结果未使用。如果确有必要，应赋值给变量 `_` (reportUnusedCallResult)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:68:14 - warning: 由于这个类未使用 `@final` 装饰，其 `preview_widget` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:70:43 - warning: "StyledPanel" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:70:43 - warning: 参数类型未知
    实参对应于 "setFrameStyle" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:70:50 - error: 无法访问 "type[QFrame]" 类的 "StyledPanel" 属性
    属性 "StyledPanel" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:75:14 - warning: 由于这个类未使用 `@final` 装饰，其 `preview_title` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:79:41 - warning: "AlignCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:79:41 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:79:44 - error: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
    属性 "AlignCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:83:14 - warning: 由于这个类未使用 `@final` 装饰，其 `info_group` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:86:14 - warning: 由于这个类未使用 `@final` 装饰，其 `file_name_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:87:14 - warning: 由于这个类未使用 `@final` 装饰，其 `file_format_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:88:14 - warning: 由于这个类未使用 `@final` 装饰，其 `file_size_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:89:14 - warning: 由于这个类未使用 `@final` 装饰，其 `file_modified_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:103:14 - warning: 由于这个类未使用 `@final` 装饰，其 `content_group` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:106:14 - warning: 由于这个类未使用 `@final` 装饰，其 `content_preview` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:117:51 - error: 需要传入 1 个位置参数 (reportCallIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:121:24 - warning: "DontUseNativeDialog" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:121:24 - warning: 参数类型未知
    实参对应于 "setOption" 函数中的 "option" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:121:36 - error: 无法访问 "type[QFileDialog]" 类的 "DontUseNativeDialog" 属性
    属性 "DontUseNativeDialog" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:124:14 - warning: 由于这个类未使用 `@final` 装饰，其 `preview_labels` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:165:38 - warning: 参数类型为 `Any`
    实参对应于 "_show_preview_error" 函数中的 "error_message" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:167:45 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:167:55 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:174:38 - warning: 参数类型为 `Any`
    实参对应于 "setText" 函数中的 "arg__1" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:175:40 - warning: 参数类型为 `Any`
    实参对应于 "setText" 函数中的 "arg__1" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:176:38 - warning: 参数类型为 `Any`
    实参对应于 "setText" 函数中的 "arg__1" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:182:60 - warning: 参数类型为 `Any`
    实参对应于 "fromtimestamp" 函数中的 "timestamp" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:187:40 - warning: "file_path" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:187:67 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:187:77 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:204:48 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:204:58 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:214:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:216:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:218:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:220:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:223:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:225:48 - warning: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:227:53 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:227:63 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:237:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:240:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:240:33 - warning: 参数类型为 `Any`
    实参对应于 "append" 函数中的 "object" 形参 (reportAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:243:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:245:13 - warning: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:247:48 - warning: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:249:51 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:249:61 - warning: 不允许使用 `Any` 类型 (reportExplicitAny)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:282:47 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:282:47 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:282:47 - warning: "parent" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:314:30 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:314:30 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\enhanced_file_dialog.py:315:52 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:12:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:12:20 - warning: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:13:31 - warning: "QWidget" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:13:69 - warning: "QVBoxLayout" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:15:34 - warning: "QPalette" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:15:44 - warning: "QColor" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:31:24 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:31:24 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:33:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:34:14 - warning: 由于这个类未使用 `@final` 装饰，其 `current_format` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:40:28 - warning: "StyledPanel" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:40:28 - warning: 参数类型未知
    实参对应于 "setFrameStyle" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:40:35 - error: 无法访问 "type[QFrame]" 类的 "StyledPanel" 属性
    属性 "StyledPanel" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:48:14 - warning: 由于这个类未使用 `@final` 装饰，其 `icon_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:50:38 - warning: "AlignCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:50:38 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:50:41 - error: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
    属性 "AlignCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:54:14 - warning: 由于这个类未使用 `@final` 装饰，其 `format_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:55:40 - warning: "AlignVCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:55:40 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:55:43 - error: 无法访问 "type[Qt]" 类的 "AlignVCenter" 属性
    属性 "AlignVCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:59:14 - warning: 由于这个类未使用 `@final` 装饰，其 `info_label` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:60:38 - warning: "AlignVCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:60:38 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:60:41 - error: 无法访问 "type[Qt]" 类的 "AlignVCenter" 属性
    属性 "AlignVCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:107:23 - error: `None` 没有 "update" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:139:14 - warning: 由于这个类未使用 `@final` 装饰，其 `animation` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:139:14 - error: 实例变量 "animation" 未在类体或 `__init__` 方法中初始化 (reportUninitializedInstanceVariable)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:143:39 - warning: "OutQuad" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:143:39 - warning: 参数类型未知
    实参对应于 "setEasingCurve" 函数中的 "easing" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:143:52 - error: 无法访问 "type[QEasingCurve]" 类的 "OutQuad" 属性
    属性 "OutQuad" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:204:24 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:204:24 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:211:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:213:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_script_format` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:214:27 - warning: "AlignCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:214:27 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:214:30 - error: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
    属性 "AlignCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:255:9 - warning: "format_info" 的类型部分未知
    "format_info" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:255:23 - warning: "_get_format_info" 的类型部分未知
    "_get_format_info" 为 "(format_type: ScriptFormat) -> dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:258:22 - warning: 参数类型未知
    实参对应于 "setText" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:261:25 - warning: 参数类型未知
    实参对应于 "setToolTip" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:275:9 - warning: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:275:62 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:320:9 - warning: "scriptFormat" 方法的声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:333:24 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:333:24 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:340:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:342:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_loading_state` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:343:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_progress` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:344:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_message` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:351:28 - warning: "NoFrame" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:351:28 - warning: 参数类型未知
    实参对应于 "setFrameStyle" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:351:35 - error: 无法访问 "type[QFrame]" 类的 "NoFrame" 属性
    属性 "NoFrame" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:359:14 - warning: 由于这个类未使用 `@final` 装饰，其 `status_icon` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:360:39 - warning: "AlignCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:360:39 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:360:42 - error: 无法访问 "type[Qt]" 类的 "AlignCenter" 属性
    属性 "AlignCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:367:14 - warning: 由于这个类未使用 `@final` 装饰，其 `status_message` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:368:42 - warning: "AlignVCenter" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:368:42 - warning: 参数类型未知
    实参对应于 "setAlignment" 函数中的 "arg__1" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:368:45 - error: 无法访问 "type[Qt]" 类的 "AlignVCenter" 属性
    属性 "AlignVCenter" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:376:14 - warning: 由于这个类未使用 `@final` 装饰，其 `progress_bar` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:451:34 - error: "str | bool" 类型的实参无法赋值给函数 "setText" 中 "str" 类型的形参 "arg__1"
    "str | bool" 类型与 "str" 类型不兼容
      "bool" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:467:38 - error: "str | bool" 类型的实参无法赋值给函数 "setVisible" 中 "bool" 类型的形参 "visible"
    "str | bool" 类型与 "bool" 类型不兼容
      "str" 与 "bool" 不兼容 (reportArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\format_indicator_widget.py:506:9 - warning: "loadingState" 方法的声明被同名声明遮蔽 (reportRedeclaration)
d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:8:20 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:8:30 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:8:30 - warning: "List" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:8:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:8:36 - warning: "Dict" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:10:56 - warning: "QScrollArea" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:11:5 - warning: "QSizePolicy" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:11:18 - warning: "QGridLayout" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:11:31 - warning: "QBoxLayout" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:13:28 - warning: "Qt" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:14:34 - warning: "QPalette" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:14:44 - warning: "QPainter" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:14:54 - warning: "QPen" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:14:60 - warning: "QColor" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:30:5 - warning: 由于这个类未使用 `@final` 装饰，其 `metadata_changed` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:32:24 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:32:24 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:32:37 - warning: "color_manager" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:32:37 - warning: "color_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:40:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:41:9 - warning: "color_manager" 的类型部分未知
    "color_manager" 为 "Unknown | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:41:14 - warning: 由于这个类未使用 `@final` 装饰，其 `color_manager` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:44:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:45:14 - warning: 由于这个类未使用 `@final` 装饰，其 `_is_visible` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:48:27 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:49:33 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:133:26 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:137:32 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:148:14 - warning: 由于这个类未使用 `@final` 装饰，其 `animation` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:148:14 - error: 实例变量 "animation" 未在类体或 `__init__` 方法中初始化 (reportUninitializedInstanceVariable)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:158:26 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:159:32 - error: `None` 没有 "setText" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:164:39 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:195:9 - warning: "resizeEvent" 方法没有用 `@override` 装饰，但覆写了 "QWidget" 类中的方法 (reportImplicitOverride)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:195:27 - warning: "event" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:195:27 - warning: "event" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:197:29 - warning: 参数类型未知
    实参对应于 "resizeEvent" 函数中的 "event" 形参 (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:204:36 - error: `None` 没有 "setMaximumHeight" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:205:36 - error: `None` 没有 "setMinimumHeight" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:208:36 - error: `None` 没有 "setMaximumHeight" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:209:36 - error: `None` 没有 "setMinimumHeight" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:212:36 - error: `None` 没有 "setMaximumHeight" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:213:36 - error: `None` 没有 "setMinimumHeight" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:215:9 - warning: "minimumSizeHint" 方法没有用 `@override` 装饰，但覆写了 "QWidget" 类中的方法 (reportImplicitOverride)
  d:\GITHUB\wuwa_actionseq_player\src\ui\metadata_display_widget.py:222:9 - warning: "sizeHint" 方法没有用 `@override` 装饰，但覆写了 "QWidget" 类中的方法 (reportImplicitOverride)
d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:15:20 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:15:26 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:15:32 - warning: "Any" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:15:37 - warning: 此类型自 Python 3.10 起已弃用；请改用 "| None" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:15:37 - warning: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:35:24 - warning: "parent" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:35:24 - warning: "parent" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:36:26 - warning: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "parent" 形参
    参数类型为 "Unknown | None" (reportUnknownArgumentType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:37:14 - warning: 由于这个类未使用 `@final` 装饰，其 `character_mapping` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:38:14 - warning: 由于这个类未使用 `@final` 装饰，其 `action_display_mapping` 属性需要类型注解 (reportUnannotatedClassAttribute)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:46:36 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:78:46 - warning: 此类型自 Python 3.9 起已弃用；请改用 "dict" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:95:66 - warning: "script_status" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:95:66 - warning: "script_status" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:141:76 - warning: "row_index" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:141:92 - warning: "current_index" 未使用 (reportUnusedParameter)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:166:50 - warning: 此类型自 Python 3.9 起已弃用；请改用 "list" (reportDeprecated)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:166:90 - warning: "script_status" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:166:90 - warning: "script_status" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:178:27 - warning: "get_status_display" 的类型部分未知
    "get_status_display" 为 "(index: int, current_index: int, script_status: Unknown, has_start_events: bool = False, loop_start_index: int = 0, current_loop: int = 0) -> str" 类型 (reportUnknownMemberType)
  d:\GITHUB\wuwa_actionseq_player\src\ui\widgets\script_preview.py:178:69 - warning: 参数类型未知
    实参对应于 "get_status_display" 函数中的 "script_status" 形参 (reportUnknownArgumentType)
196 errors, 1603 warnings, 0 notes
```

