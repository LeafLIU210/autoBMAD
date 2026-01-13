# 方案3：StatusUpdateAgent 状态映射机制实施方案

## 一、问题背景

### 1.1 当前问题
- StatusUpdateAgent 生成核心状态时，可能参考了：
  - 历史失败记录
  - 旧表字段
  - 临时/测试记录
  - 甚至 Markdown 当前文本
- 导致状态来源混乱，无法保证一致性

### 1.2 设计目标
**StatusUpdateAgent 只从"数据库最新处理状态值"映射到"核心状态"，不使用任何其他数据源。**

## 二、解决方案

### 2.1 核心原则

```
数据库处理状态（processing_status）
         ↓
    [映射表查询]
         ↓
    核心状态（Core Status）
         ↓
   Markdown Status 文本
```

**单一真源：** 数据库的 `processing_status` 字段（最新记录）

### 2.2 状态映射表设计

#### 2.2.1 基础映射规则

| 处理状态值 | 核心状态 | 说明 |
|-----------|---------|------|
| `in_progress` | `Ready for Development` | 开发中或需返工 |
| `review` | `Ready for Review` | Dev 完成，等待 QA |
| `completed` | `Ready for Done` | QA 通过，Story 完成 |
| `cancelled` | `Ready for Development` | 被取消，支持重新开始 |
| `error` | `Ready for Development` | 执行出错，支持重试 |

**设计说明：**
- 与方案2 的处理状态流转规则一致
- `cancelled` / `error` 映射回 `Ready for Development`，符合"容错机制"记忆
- 不设置 `Failed` 映射，避免失败固化

#### 2.2.2 映射实现（代码结构）

```python
class StatusUpdateAgent:
    """状态同步代理"""
    
    # 状态映射表（常量）
    PROCESSING_TO_CORE_STATUS = {
        'in_progress': 'Ready for Development',
        'review': 'Ready for Review',
        'completed': 'Ready for Done',
        'cancelled': 'Ready for Development',  # 容错
        'error': 'Ready for Development',      # 容错
    }
    
    def _map_to_core_status(self, processing_status: str) -> str:
        """
        将处理状态映射为核心状态
        
        Args:
            processing_status: 数据库中的处理状态值
            
        Returns:
            对应的核心状态文本
            
        Raises:
            ValueError: 处理状态值非法
        """
        if processing_status not in self.PROCESSING_TO_CORE_STATUS:
            raise ValueError(
                f"Unknown processing_status: {processing_status}. "
                f"Valid values: {list(self.PROCESSING_TO_CORE_STATUS.keys())}"
            )
        
        return self.PROCESSING_TO_CORE_STATUS[processing_status]
```

### 2.3 StatusUpdateAgent 完整工作流

```python
def sync_stories(self, epic_id: str, story_ids: List[str]):
    """
    同步指定 Epic 的 Story 状态
    
    核心流程：
    1. 从数据库查询最新处理状态
    2. 通过映射表转换为核心状态
    3. 生成 Markdown Status 文本
    4. 调用 SDK 更新 Story 文档
    """
    
    # Step 1: 查询数据库（方案1 保证范围限制）
    story_records = self.state_manager.get_stories_by_ids(
        epic_id=epic_id,
        story_ids=story_ids
    )
    
    # Step 2-4: 逐个处理
    for record in story_records:
        try:
            # Step 2: 映射处理状态 → 核心状态
            processing_status = record['processing_status']
            core_status = self._map_to_core_status(processing_status)
            
            # Step 3: 生成 Markdown 文本
            status_text = self._generate_status_markdown(core_status)
            
            # Step 4: 通过 SDK 更新文档
            self._update_story_file(
                file_path=record['file_path'],
                new_status_text=status_text
            )
            
            logger.info(
                f"[StatusUpdate] {record['story_id']}: "
                f"{processing_status} → {core_status}"
            )
            
        except Exception as e:
            logger.error(
                f"[StatusUpdate] Failed to update {record['story_id']}: {e}"
            )
            # 单条失败不中断整个同步流程
            continue
```

### 2.4 禁止使用的数据源（反模式）

**以下行为必须避免：**

```python
# ❌ 错误 1：从 Markdown 读取当前状态作为参考
current_md_status = parse_markdown_status(story_file)
if current_md_status == 'Ready for Done':
    # 保持不变...

# ❌ 错误 2：从 SDK 执行结果推断状态
sdk_result = sdk_executor.call(...)
if 'success' in sdk_result.messages:
    new_status = 'completed'

# ❌ 错误 3：使用历史记录的平均值
history = get_status_history(story_id)
if history.count('failed') > 3:
    new_status = 'Failed'

# ❌ 错误 4：混合旧字段
legacy_status = record.get('old_status_field')
if legacy_status:
    # 优先使用旧字段...
```

**正确做法：**
```python
# ✅ 唯一正确的数据源
processing_status = record['processing_status']  # 来自数据库最新记录
core_status = self._map_to_core_status(processing_status)
```

## 三、实施步骤

### 3.1 Phase 1：定义映射表常量

**位置：** `autoBMAD/epic_automation/agents/status_update_agent.py`

**实现：**
```python
class StatusUpdateAgent:
    """状态同步代理"""
    
    # 映射表：处理状态 → 核心状态
    PROCESSING_TO_CORE_STATUS = {
        'in_progress': 'Ready for Development',
        'review': 'Ready for Review',
        'completed': 'Ready for Done',
        'cancelled': 'Ready for Development',
        'error': 'Ready for Development',
    }
    
    # 可选：反向映射（用于调试/验证）
    CORE_TO_PROCESSING_STATUS = {
        'Ready for Development': 'in_progress',
        'Ready for Review': 'review',
        'Ready for Done': 'completed',
        'Done': 'completed',  # 别名
    }
```

### 3.2 Phase 2：实现映射方法

**方法 1：处理状态 → 核心状态**

```python
def _map_to_core_status(self, processing_status: str) -> str:
    """处理状态 → 核心状态"""
    
    if processing_status not in self.PROCESSING_TO_CORE_STATUS:
        logger.warning(
            f"Unknown processing_status '{processing_status}', "
            f"defaulting to 'Ready for Development'"
        )
        return 'Ready for Development'  # 默认值（容错）
    
    return self.PROCESSING_TO_CORE_STATUS[processing_status]
```

**方法 2：生成 Markdown Status 文本**

```python
def _generate_status_markdown(self, core_status: str) -> str:
    """
    根据核心状态生成 Markdown Status 段落
    
    Args:
        core_status: 核心状态（如 'Ready for Review'）
        
    Returns:
        完整的 Status 段落文本
    """
    return f"""## Status

**Status**: {core_status}

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
```

### 3.3 Phase 3：重构 sync_stories 方法

**移除旧逻辑：**
- ❌ 解析 Markdown 当前状态
- ❌ 从 SDK 消息推断状态
- ❌ 使用历史记录判断

**保留新逻辑：**
- ✅ 只从数据库 `processing_status` 读取
- ✅ 使用映射表转换
- ✅ 写回 Markdown

**完整实现见 2.3 节。**

### 3.4 Phase 4：增加映射验证

**目的：** 确保数据库中不存在非法处理状态值

```python
def validate_processing_statuses(self, epic_id: str, story_ids: List[str]):
    """
    验证数据库中的处理状态值是否合法
    
    Returns:
        (valid_count, invalid_records)
    """
    records = self.state_manager.get_stories_by_ids(epic_id, story_ids)
    
    valid_statuses = set(self.PROCESSING_TO_CORE_STATUS.keys())
    invalid_records = []
    
    for record in records:
        status = record['processing_status']
        if status not in valid_statuses:
            invalid_records.append({
                'story_id': record['story_id'],
                'processing_status': status,
                'file_path': record['file_path']
            })
    
    if invalid_records:
        logger.warning(
            f"Found {len(invalid_records)} stories with invalid processing_status"
        )
        for rec in invalid_records:
            logger.warning(f"  - {rec['story_id']}: {rec['processing_status']}")
    
    return len(records) - len(invalid_records), invalid_records
```

**在 sync_stories 开始时调用：**
```python
def sync_stories(self, epic_id: str, story_ids: List[str]):
    # 可选：验证数据合法性
    valid_count, invalid = self.validate_processing_statuses(epic_id, story_ids)
    if invalid:
        logger.warning(f"Proceeding with {valid_count} valid stories")
    
    # 继续同步流程...
```

## 四、验证方案

### 4.1 单元测试

**测试用例 1：标准映射**

```python
def test_map_to_core_status_standard():
    """验证标准处理状态的映射"""
    agent = StatusUpdateAgent()
    
    assert agent._map_to_core_status('in_progress') == 'Ready for Development'
    assert agent._map_to_core_status('review') == 'Ready for Review'
    assert agent._map_to_core_status('completed') == 'Ready for Done'
```

**测试用例 2：容错映射**

```python
def test_map_to_core_status_error_handling():
    """验证错误状态的容错映射"""
    agent = StatusUpdateAgent()
    
    assert agent._map_to_core_status('cancelled') == 'Ready for Development'
    assert agent._map_to_core_status('error') == 'Ready for Development'
```

**测试用例 3：非法状态处理**

```python
def test_map_to_core_status_invalid():
    """验证非法状态的处理（应返回默认值或抛异常）"""
    agent = StatusUpdateAgent()
    
    # 根据实现决定：返回默认值或抛异常
    result = agent._map_to_core_status('unknown_status')
    assert result == 'Ready for Development'  # 默认值
    
    # 或者
    with pytest.raises(ValueError):
        agent._map_to_core_status('unknown_status')
```

**测试用例 4：映射表完整性**

```python
def test_mapping_table_completeness():
    """验证映射表覆盖所有可能的处理状态"""
    agent = StatusUpdateAgent()
    
    # 所有可能的处理状态（来自方案2）
    expected_statuses = {'in_progress', 'review', 'completed', 'cancelled', 'error'}
    
    actual_statuses = set(agent.PROCESSING_TO_CORE_STATUS.keys())
    
    assert actual_statuses == expected_statuses, \
        f"Missing statuses: {expected_statuses - actual_statuses}"
```

### 4.2 集成测试

**测试场景：数据库 → 映射 → Markdown 完整流程**

```python
def test_sync_stories_full_flow():
    """验证完整的状态同步流程"""
    
    # 准备：数据库有 3 条记录
    db_records = [
        {'story_id': '1.1', 'processing_status': 'completed'},
        {'story_id': '1.2', 'processing_status': 'review'},
        {'story_id': '1.3', 'processing_status': 'in_progress'},
    ]
    state_manager.insert_records(db_records)
    
    # 执行同步
    agent = StatusUpdateAgent()
    agent.sync_stories(epic_id='test-epic', story_ids=['1.1', '1.2', '1.3'])
    
    # 验证 Markdown 文件
    assert 'Ready for Done' in read_file('docs/stories/1.1.md')
    assert 'Ready for Review' in read_file('docs/stories/1.2.md')
    assert 'Ready for Development' in read_file('docs/stories/1.3.md')
```

### 4.3 端到端验证

**目标：** 验证"成功 Story 不再被回写为 Failed"

**步骤：**
1. 运行完整 Epic（Dev-QA 全部成功）
2. 观察数据库：
   ```sql
   SELECT story_id, processing_status FROM stories
   WHERE epic_id = 'epic-1' AND story_id IN ('1.1', '1.2', '1.3', '1.4')
   ```
   预期：所有记录的 `processing_status = 'completed'`

3. 运行状态同步
4. 检查 Markdown：
   ```bash
   grep "Status" docs/stories/*.md
   ```
   预期：所有文件显示 `Ready for Done`，无一显示 `Failed`

5. 检查日志：
   ```
   [StatusUpdate] 1.1: completed → Ready for Done
   [StatusUpdate] 1.2: completed → Ready for Done
   [StatusUpdate] 1.3: completed → Ready for Done
   [StatusUpdate] 1.4: completed → Ready for Done
   ```

## 五、边界场景处理

### 5.1 数据库记录不存在

**场景：** Story ID 在 Epic 中出现，但数据库无记录

**处理：**
```python
def sync_stories(self, epic_id: str, story_ids: List[str]):
    records = self.state_manager.get_stories_by_ids(epic_id, story_ids)
    
    # 检查是否有缺失的 Story
    found_ids = {r['story_id'] for r in records}
    missing_ids = set(story_ids) - found_ids
    
    if missing_ids:
        logger.warning(
            f"Stories not found in database: {missing_ids}. "
            f"They will be skipped in status sync."
        )
    
    # 只处理有记录的 Story
    for record in records:
        # ...
```

### 5.2 Markdown 文件不存在

**场景：** 数据库有记录，但对应的 `.md` 文件被删除

**处理：**
```python
def _update_story_file(self, file_path: str, new_status_text: str):
    """更新 Story 文件"""
    
    if not os.path.exists(file_path):
        logger.warning(
            f"Story file does not exist: {file_path}. "
            f"Status sync skipped for this story."
        )
        return False
    
    # 调用 SDK 更新...
```

**注意：** 这种 WARNING 正是你当前日志中看到的 `%TEMP%` 问题的根源，通过方案4 的初始化清理可以减少此类情况。

### 5.3 处理状态为 NULL

**场景：** 数据库记录存在，但 `processing_status` 字段为 NULL

**处理：**
```python
def _map_to_core_status(self, processing_status: Optional[str]) -> str:
    """处理状态映射（支持 NULL）"""
    
    if processing_status is None:
        logger.warning(
            "processing_status is NULL, defaulting to 'Ready for Development'"
        )
        return 'Ready for Development'
    
    # 正常映射逻辑...
```

## 六、与其他方案的协同

### 6.1 与方案1（范围限制）的配合

- 方案1 确保只查询当前 Epic 的记录
- 方案3 确保对这些记录使用正确的映射规则
- 结合效果：StatusUpdateAgent 只处理当前 Epic，且状态来源单一可靠

### 6.2 与方案2（状态写入）的配合

- 方案2 定义 DevQaController 何时写入哪些处理状态值
- 方案3 定义 StatusUpdateAgent 如何读取并映射这些状态值
- 数据流闭环：
  ```
  DevQaController 写入 'completed'
       ↓
  StateManager 存储到数据库
       ↓
  StatusUpdateAgent 读取 'completed'
       ↓
  映射为 'Ready for Done'
       ↓
  写回 Markdown
  ```

### 6.3 与方案4（初始化清理）的配合

- 方案4 清理历史/测试记录，确保数据库干净
- 方案3 从干净的数据库读取，避免被垃圾数据污染
- 结合效果：StatusUpdateAgent 读取的处理状态都是"本次运行真正关心的"

## 七、性能优化（可选）

### 7.1 批量映射

若处理多条记录，可以批量映射：

```python
def _map_multiple_statuses(self, records: List[Dict]) -> List[Tuple[str, str]]:
    """
    批量映射处理状态
    
    Returns:
        [(story_id, core_status), ...]
    """
    return [
        (rec['story_id'], self._map_to_core_status(rec['processing_status']))
        for rec in records
    ]
```

### 7.2 映射缓存（不推荐）

因为映射表是常量，查询本身已经极快，缓存意义不大，且可能引入一致性问题。**不建议使用。**

## 八、实施时间表

| 阶段 | 任务 | 预计耗时 |
|------|------|---------|
| Phase 1 | 定义映射表常量 | 0.5 小时 |
| Phase 2 | 实现映射方法 | 1 小时 |
| Phase 3 | 重构 sync_stories | 1.5 小时 |
| Phase 4 | 映射验证逻辑 | 1 小时 |
| 测试 | 单元测试 + 集成测试 | 2 小时 |
| 验证 | E2E 验证 | 1 小时 |
| **总计** | | **7 小时** |

## 九、成功标准

- ✅ StatusUpdateAgent 只从数据库 `processing_status` 读取状态
- ✅ 映射表覆盖所有合法处理状态值
- ✅ 映射逻辑有完整单元测试（100% 覆盖）
- ✅ 状态同步不再使用 Markdown 当前状态、历史记录、SDK 消息等其他数据源
- ✅ 端到端验证：成功 Story 不被回写为 Failed
- ✅ 日志清晰记录每次映射：`processing_status → core_status`
