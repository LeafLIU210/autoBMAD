# 脚本预览树"添加事件"按钮功能实现方案

## 项目概述

为鸣潮技能录制器的脚本预览树组件添加"添加事件"按钮功能，实现事件的手动添加和编辑。该功能遵循奥卡姆剃刀原则，提供简洁高效的用户体验。

## 技术背景

### 当前代码架构
- **数据模型**: `Project_recorder/script_data_model_unified.py` - 简化版ScriptEvent（3字段：action_name、number、remark）
- **UI组件**: `Project_recorder/ui/widgets/script_preview_tree.py` - 树形预览组件
- **事件编辑**: `Project_recorder/ui/dialogs/event_edit_dialog_enhanced.py` - EnhancedEventEditDialog
- **数据管理**: `Project_recorder/script_data_manager_unified.py` - UnifiedScriptDataManager

### 现有功能状态
- ✅ 树形组件显示3列：["序号", "动作", "备注"]
- ✅ 工具栏已有按钮：删除事件、删除分段、设为普通、设为循环、保存、打开、清空脚本
- ✅ 事件编辑对话框已实现
- ✅ 数据管理器的add_event方法已实现
- ❌ **缺失功能**：工具栏中无"添加事件"按钮

## 实施方案

### 1. UI设计

#### 1.1 工具栏按钮添加
在`script_preview_tree.py`的`_create_toolbar()`方法中，删除按钮之前添加"添加事件"按钮：

```python
def _create_toolbar(self) -> None:
    """创建增强的工具栏"""
    self.toolbar = QToolBar()
    self.toolbar.setMovable(False)
    self.toolbar.setIconSize(self.toolbar.iconSize() * 0.8)

    # 添加事件按钮（新增）
    self.add_event_action = QAction("添加事件", self)
    self.add_event_action.setStatusTip("添加新事件到脚本")
    self.add_event_action.setToolTip("添加新事件到脚本")
    self.toolbar.addAction(self.add_event_action)

    # 现有按钮...
    self.delete_action = QAction("删除事件", self)
    # ...
```

#### 1.2 按钮样式规范
- 文本："添加事件"
- 工具提示：简洁描述功能
- 图标：复用项目中现有图标或使用默认图标
- 状态：初始禁用，事件选中时启用

#### 1.3 按钮状态管理
在`_update_toolbar_states()`方法中添加状态更新逻辑：

```python
def _update_toolbar_states(self) -> None:
    """更新工具栏按钮状态"""
    # 已有逻辑...

    # 添加事件按钮状态
    has_selection = len(self.tree_widget.selectedItems()) > 0
    self.add_event_action.setEnabled(has_selection and self.script_data is not None)
```

### 2. 交互逻辑设计

#### 2.1 选中状态检测
使用现有的选择模型检测：

```python
def _on_selection_changed(self):
    """处理选择变更"""
    # 已有逻辑...

    # 更新工具栏状态
    self._update_toolbar_states()
```

#### 2.2 事件添加流程
1. 用户选中事件行
2. "添加事件"按钮激活
3. 点击按钮弹出事件编辑对话框
4. 用户编辑事件属性
5. 计算插入位置（选中事件的下一行）
6. 创建新事件（自动分配编号）
7. 插入到脚本数据
8. 更新UI显示

#### 2.3 插入位置计算
```python
def _get_insert_position(self) -> tuple[int, Optional[int]]:
    """计算事件插入位置

    Returns:
        tuple: (segment_index, event_index_in_segment)
               segment_index为None表示插入到主事件列表
               event_index为None表示插入到末尾
    """
    selected_items = self.tree_widget.selectedItems()
    if not selected_items:
        return None, None

    # 获取第一个选中项
    item = selected_items[0]

    # 判断是事件项还是分段项
    if isinstance(item, EventTreeItem):
        # 获取父分段
        segment_item = item.parent()
        if segment_item and isinstance(segment_item, SegmentTreeItem):
            segment_index = self._get_segment_index(segment_item)
            event_index = segment_item.indexOfChild(item)
            return segment_index, event_index + 1
        else:
            # 在主事件列表中插入
            event_index = item.data(0, Qt.ItemDataRole.UserRole)  # 存储事件索引
            return None, event_index + 1

    elif isinstance(item, SegmentTreeItem):
        # 在分段末尾插入
        segment_index = self._get_segment_index(item)
        return segment_index, None

    return None, None
```

### 3. 关键方法实现

#### 3.1 添加事件处理方法
```python
def _on_add_event(self):
    """处理添加事件按钮点击"""
    if not self.script_data:
        QMessageBox.warning(self, "警告", "请先加载或创建脚本")
        return

    # 计算插入位置
    segment_index, event_index = self._get_insert_position()

    # 创建默认事件
    default_event = ScriptEvent(
        action_name="sho_e",  # 默认动作
        number=1,  # 临时编号，稍后重新分配
        remark=""
    )

    # 打开编辑对话框
    dialog = EnhancedEventEditDialog(
        event=default_event,
        action_display_names=self.action_display_names,
        parent=self
    )

    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 获取编辑后的事件
        new_event = dialog.get_modified_event()
        if new_event:
            # 插入事件
            self._insert_event_at_position(new_event, segment_index, event_index)
            # 重新编号所有事件
            self._renumber_all_events()
            # 刷新显示
            self.refresh_display()
            # 发出数据变更信号
            self.script_data_changed.emit()

def _insert_event_at_position(self, event: ScriptEvent, segment_index: Optional[int], event_index: Optional[int]):
    """在指定位置插入事件"""
    # 计算实际插入位置
    if segment_index is not None:
        # 插入到分段
        if event_index is not None:
            self.script_data.segments[segment_index].events.insert(event_index, event)
        else:
            self.script_data.segments[segment_index].events.append(event)
    else:
        # 插入到主事件列表
        if event_index is not None:
            self.script_data.events.insert(event_index, event)
        else:
            self.script_data.events.append(event)

def _renumber_all_events(self):
    """重新编号所有事件"""
    all_events = []

    # 收集所有事件
    for segment in self.script_data.segments:
        all_events.extend(segment.events)
    all_events.extend(self.script_data.events)

    # 重新编号
    for i, event in enumerate(all_events, start=1):
        event.number = i
```

#### 3.2 信号连接
在`__init__`方法中连接信号：

```python
def __init__(self, parent=None):
    super().__init__(parent)
    # 已有初始化...

    # 连接添加事件按钮
    self.add_event_action.triggered.connect(self._on_add_event)

    # 连接选择变更信号
    self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
```

### 4. 信号处理机制

#### 4.1 与数据管理器的交互
```python
def add_event_to_script(self, event: ScriptEvent) -> bool:
    """添加事件到脚本（使用数据管理器）"""
    if not self.script_data:
        return False

    # 使用UnifiedScriptDataManager添加事件
    success = self.data_manager.add_event(
        timestamp=0,  # 忽略，使用简化模型
        relative_time=0,  # 忽略，使用简化模型
        action_name=event.action_name,
        remark=event.remark,
        duration=event.duration
    )

    if success:
        self.script_data_changed.emit()

    return success
```

#### 4.2 UI更新机制
```python
def refresh_display(self):
    """刷新显示"""
    if not self.script_data:
        self.tree_widget.clear()
        return

    # 重建树形结构
    self._build_tree_structure()

    # 更新状态
    self._update_toolbar_states()
```

### 5. 文件修改清单

#### 5.1 主要修改文件
1. **Project_recorder/ui/widgets/script_preview_tree.py**
   - `_create_toolbar()`: 添加"添加事件"按钮
   - `_update_toolbar_states()`: 添加按钮状态管理
   - `_on_add_event()`: 新增事件添加处理方法
   - `_get_insert_position()`: 新增位置计算方法
   - `_insert_event_at_position()`: 新增事件插入方法
   - `_renumber_all_events()`: 新增重新编号方法
   - `__init__()`: 连接信号

#### 5.2 可能需要修改的文件
1. **Project_recorder/ui/dialogs/event_edit_dialog_enhanced.py**
   - 确保对话框返回正确格式的事件对象

2. **Project_recorder/script_data_manager_unified.py**
   - 验证`add_event()`方法与简化数据模型的兼容性

### 6. 与现有功能的集成

#### 6.1 与删除功能的协调
- 添加事件后，选中新添加的事件
- 删除事件后，自动重新编号
- 保持编号连续性

#### 6.2 与分段管理功能的协调
- 支持在分段内添加事件
- 在分段间移动事件时保持编号正确
- 空分段状态处理

#### 6.3 数据一致性保证
- 所有事件操作后触发`_renumber_all_events()`
- 使用`script_data_changed`信号通知外部
- 保持内存中数据与显示同步

### 7. 错误处理

#### 7.1 验证检查
```python
def _validate_event_data(self, event: ScriptEvent) -> tuple[bool, str]:
    """验证事件数据"""
    if not event.action_name or not event.action_name.strip():
        return False, "动作名称不能为空"

    if len(event.action_name) > 100:
        return False, "动作名称过长（最大100字符）"

    return True, ""
```

#### 7.2 用户反馈
```python
def _show_success_message(self, message: str):
    """显示成功消息"""
    self.status_label.setText(f"✓ {message}")

def _show_error_message(self, message: str):
    """显示错误消息"""
    QMessageBox.critical(self, "错误", message)
```

### 8. 测试验证点

#### 8.1 功能测试场景
1. **基本添加功能**
   - 选中事件后点击"添加事件"按钮
   - 编辑事件属性并保存
   - 验证事件插入到正确位置
   - 验证编号自动分配

2. **边界条件**
   - 空脚本状态下添加事件
   - 在分段末尾添加事件
   - 在主事件列表末尾添加事件
   - 连续添加多个事件

3. **编号逻辑**
   - 添加事件后编号正确递增
   - 删除事件后剩余事件重新编号
   - 分段模式下编号连续性

#### 8.2 UI测试
- 按钮启用/禁用状态正确
- 选中状态变化时按钮状态同步更新
- 编辑对话框正确显示和保存数据
- 树形视图正确刷新显示

#### 8.3 集成测试
- 与数据管理器的交互正常
- 信号传递正确
- 数据持久化正常

### 9. 性能考虑

#### 9.1 优化策略
- 使用懒加载减少初始加载时间
- 批量操作时避免频繁UI刷新
- 事件编号使用增量更新而非全量重新计算

#### 9.2 内存管理
- 及时清理不需要的对象引用
- 使用弱引用避免循环引用
- 大脚本场景下的性能优化

### 10. 代码质量要求

#### 10.1 遵循原则
- **DRY**: 避免重复代码，复用现有方法
- **KISS**: 保持实现简洁，避免过度设计
- **YAGNI**: 只实现当前需要的功能
- **奥卡姆剃刀**: 移除不必要的复杂性

#### 10.2 代码规范
- 使用绝对导入（不包含`Project_recorder.`前缀）
- 遵循PEP 8代码风格
- 添加必要的类型注解
- 编写清晰的文档字符串

### 11. 实施步骤

#### 阶段1: UI实现
1. 在工具栏添加"添加事件"按钮
2. 实现按钮状态管理
3. 连接信号槽

#### 阶段2: 核心逻辑
1. 实现事件添加处理方法
2. 实现位置计算逻辑
3. 实现事件插入方法

#### 阶段3: 集成测试
1. 集成数据管理器
2. 完善错误处理
3. 性能优化

#### 阶段4: 文档和测试
1. 更新代码文档
2. 编写单元测试
3. 进行集成测试

### 12. 验收标准

#### 12.1 功能验收
- ✅ "添加事件"按钮正确显示在工具栏
- ✅ 选中事件时按钮启用，未选中时禁用
- ✅ 点击按钮弹出事件编辑对话框
- ✅ 编辑保存后事件正确插入到下一行
- ✅ 事件编号自动分配且连续

#### 12.2 质量验收
- ✅ 代码符合项目规范
- ✅ 无内存泄漏
- ✅ 性能满足要求
- ✅ 错误处理完善

## 总结

本方案基于奥卡姆剃刀原则，提供简洁有效的"添加事件"按钮功能实现。通过复用现有组件和数据模型，最小化代码变更，同时确保功能完整性和用户体验的一致性。方案遵循项目的架构设计和编码规范，易于实施和维护。