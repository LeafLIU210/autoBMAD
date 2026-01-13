# 方案4：Epic 运行前数据库自动初始化实施方案

## 一、问题背景

### 1.1 当前问题
- 数据库保留大量历史运行记录（298 条）
- 包含当前 Epic 的旧失败记录
- 包含 `%TEMP%` 路径的测试/临时记录
- 包含已删除文件的"僵尸记录"

### 1.2 影响
- **数据污染**：旧失败记录覆盖当前成功结果
- **性能浪费**：StatusUpdateAgent 处理大量无效记录
- **日志噪音**：大量 "Story file does not exist" 警告

### 1.3 设计目标
**每次 epic_driver 运行前，自动清理"本次不需要的数据"，为当前 Epic 创建干净的数据环境。**

## 二、解决方案

### 2.1 核心原则

**不是"彻底删库重建"，而是"按规则清理垃圾数据"。**

- ✅ 清理：当前 Epic 的旧处理状态记录
- ✅ 清理：`%TEMP%` 路径的临时记录
- ✅ 清理：带测试标记的 Story 记录
- ❌ 不清理：其他 Epic 的历史记录（为后续分析保留）

### 2.2 初始化时机

在 epic_driver 启动后，Dev-QA 循环开始前：

```
epic_driver.py 启动
    ↓
日志系统初始化
    ↓
StateManager 初始化
    ↓
解析 Epic 文件 → 得到 Story ID 列表
    ↓
【新增】数据库自动初始化清理  ← 在此插入
    ↓
进入 Dev-QA 循环
```

### 2.3 清理规则设计

#### 2.3.1 规则 1：清理当前 Epic Story 的旧记录

**目标：** 确保本次运行不被历史处理状态污染

**SQL 逻辑：**
```sql
DELETE FROM stories
WHERE epic_id = ?
  AND story_id IN (?, ?, ?, ?)
```

**参数：**
- `epic_id`: 当前 Epic 标识（如 `'epic-1-core-algorithm-foundation'`）
- `story_id IN (...)`: 本次需要处理的 Story 列表（如 `'1.1', '1.2', '1.3', '1.4'`）

**效果：**
- 删除这 4 条 Story 的所有历史记录
- 为本次运行创建"从零开始"的处理状态空间

#### 2.3.2 规则 2：清理 %TEMP% 路径记录

**目标：** 移除测试/临时 Story 的僵尸记录

**SQL 逻辑：**
```sql
DELETE FROM stories
WHERE file_path LIKE '%\Temp\%'
   OR file_path LIKE '%\AppData\Local\Temp\%'
```

**匹配示例：**
- `C:\Users\Administrator\AppData\Local\Temp\tmpxxxx\stories\test_story.md`
- `C:\Temp\some-test-epic\story-1.1.md`

**效果：**
- 清理所有临时目录下的 Story 记录
- 避免 StatusUpdateAgent 为这些不存在的文件调用 SDK

#### 2.3.3 规则 3：清理测试标记的 Story

**目标：** 移除明显的测试记录

**SQL 逻辑：**
```sql
DELETE FROM stories
WHERE story_id LIKE '%test%'
   OR story_id LIKE 'test_%'
   OR file_path LIKE '%test_story%'
```

**匹配示例：**
- `story_id = 'test_story_1'`
- `story_id = '1.1-test'`
- `file_path = '.../stories/test_story.md'`

**效果：**
- 清理带明显测试标记的记录
- 可根据项目实际命名规范调整规则

### 2.4 可选：保留策略（白名单）

如果某些历史记录需要保留，可以增加排除条件：

```sql
DELETE FROM stories
WHERE epic_id = ?
  AND story_id IN (?, ?, ?, ?)
  AND created_at < ?  -- 只删除本次运行之前的记录
```

或使用白名单表：

```sql
DELETE FROM stories
WHERE story_id NOT IN (
    SELECT story_id FROM protected_stories
)
AND (epic_id = ? AND story_id IN (...))
```

## 三、实施步骤

### 3.1 Phase 1：StateManager 新增清理方法

**位置：** `autoBMAD/epic_automation/state_manager.py`

#### 3.1.1 方法 1：清理当前 Epic Story 旧记录

```python
def cleanup_epic_stories(self, epic_id: str, story_ids: List[str]) -> int:
    """
    清理当前 Epic 相关 Story 的历史记录
    
    Args:
        epic_id: Epic 标识
        story_ids: Story ID 列表
        
    Returns:
        删除的记录数
    """
    if not story_ids:
        logger.info("[Cleanup] No stories to cleanup")
        return 0
    
    placeholders = ','.join(['?'] * len(story_ids))
    query = f"""
        DELETE FROM stories
        WHERE epic_id = ?
          AND story_id IN ({placeholders})
    """
    params = [epic_id] + story_ids
    
    deleted_count = self._execute_delete(query, params)
    
    logger.info(
        f"[Cleanup] Removed {deleted_count} old records for "
        f"Epic '{epic_id}' Stories {story_ids}"
    )
    
    return deleted_count
```

#### 3.1.2 方法 2：清理 TEMP 路径记录

```python
def cleanup_temp_stories(self) -> int:
    """
    清理临时目录下的 Story 记录
    
    Returns:
        删除的记录数
    """
    query = """
        DELETE FROM stories
        WHERE file_path LIKE '%\\Temp\\%'
           OR file_path LIKE '%\\AppData\\Local\\Temp\\%'
           OR file_path LIKE '/tmp/%'  -- Linux 临时目录
    """
    
    deleted_count = self._execute_delete(query, [])
    
    logger.info(f"[Cleanup] Removed {deleted_count} temp story records")
    
    return deleted_count
```

#### 3.1.3 方法 3：清理测试标记记录

```python
def cleanup_test_stories(self) -> int:
    """
    清理带测试标记的 Story 记录
    
    Returns:
        删除的记录数
    """
    query = """
        DELETE FROM stories
        WHERE story_id LIKE '%test%'
           OR story_id LIKE 'test_%'
           OR file_path LIKE '%test_story%'
    """
    
    deleted_count = self._execute_delete(query, [])
    
    logger.info(f"[Cleanup] Removed {deleted_count} test story records")
    
    return deleted_count
```

#### 3.1.4 统一入口方法

```python
def initialize_for_epic(self, epic_id: str, story_ids: List[str]) -> Dict[str, int]:
    """
    为当前 Epic 运行初始化数据库
    
    执行清理：
    1. 当前 Epic Story 的旧记录
    2. TEMP 路径记录
    3. 测试标记记录
    
    Args:
        epic_id: 当前 Epic 标识
        story_ids: 当前 Epic 的 Story 列表
        
    Returns:
        清理统计：{
            'epic_stories': 删除数,
            'temp_stories': 删除数,
            'test_stories': 删除数,
            'total': 总删除数
        }
    """
    logger.info(f"[Init] Starting database initialization for Epic '{epic_id}'")
    
    stats = {}
    
    # 清理 1：当前 Epic Story 旧记录
    stats['epic_stories'] = self.cleanup_epic_stories(epic_id, story_ids)
    
    # 清理 2：TEMP 路径
    stats['temp_stories'] = self.cleanup_temp_stories()
    
    # 清理 3：测试标记
    stats['test_stories'] = self.cleanup_test_stories()
    
    # 汇总
    stats['total'] = sum(stats.values())
    
    logger.info(
        f"[Init] Database cleanup completed: "
        f"{stats['total']} records removed "
        f"(Epic: {stats['epic_stories']}, "
        f"Temp: {stats['temp_stories']}, "
        f"Test: {stats['test_stories']})"
    )
    
    return stats
```

### 3.2 Phase 2：EpicDriver 调用初始化

**位置：** `autoBMAD/epic_automation/epic_driver.py`

**修改点：在 Epic 解析后，Dev-QA 前插入初始化**

```python
async def run_epic(self, epic_file: str):
    """运行 Epic 自动化流程"""
    
    # Step 1: 初始化日志和 StateManager
    self._initialize_logging(epic_file)
    self.state_manager = StateManager(db_path='progress.db')
    
    # Step 2: 解析 Epic
    epic_id, stories = await self._parse_epic(epic_file)
    story_ids = [story.id for story in stories]
    
    logger.info(f"Epic '{epic_id}' parsed: {len(stories)} stories found")
    
    # Step 3: 【新增】数据库初始化清理
    cleanup_stats = self.state_manager.initialize_for_epic(
        epic_id=epic_id,
        story_ids=story_ids
    )
    
    logger.info(
        f"Database initialized: {cleanup_stats['total']} old records removed"
    )
    
    # Step 4: 进入 Dev-QA 循环（现在使用干净的数据环境）
    await self._run_dev_qa_phase(stories)
    
    # ...后续阶段
```

### 3.3 Phase 3：增加初始化日志摘要

**目的：** 在运行开始时明确告知清理结果

**日志格式：**
```
=== Database Initialization ===
Cleanup Rules:
  1. Current Epic stories: epic-1-core-algorithm-foundation [1.1, 1.2, 1.3, 1.4]
  2. TEMP path stories: %\Temp\%, %\AppData\Local\Temp\%
  3. Test-marked stories: *test*, test_*

Cleanup Results:
  - Epic stories removed: 4
  - Temp stories removed: 287
  - Test stories removed: 3
  - Total removed: 294

Database ready for Epic execution.
===============================
```

**实现：**
```python
def _log_cleanup_summary(self, epic_id: str, story_ids: List[str], stats: Dict):
    """记录清理摘要"""
    
    logger.info("=== Database Initialization ===")
    logger.info("Cleanup Rules:")
    logger.info(f"  1. Current Epic stories: {epic_id} {story_ids}")
    logger.info(f"  2. TEMP path stories: %\\Temp\\%, %\\AppData\\Local\\Temp\\%")
    logger.info(f"  3. Test-marked stories: *test*, test_*")
    logger.info("")
    logger.info("Cleanup Results:")
    logger.info(f"  - Epic stories removed: {stats['epic_stories']}")
    logger.info(f"  - Temp stories removed: {stats['temp_stories']}")
    logger.info(f"  - Test stories removed: {stats['test_stories']}")
    logger.info(f"  - Total removed: {stats['total']}")
    logger.info("")
    logger.info("Database ready for Epic execution.")
    logger.info("=" * 31)
```

### 3.4 Phase 4：增加配置开关（可选）

**目的：** 允许临时禁用自动初始化

**配置文件：** `config.py` 或环境变量

```python
# config.py
DB_AUTO_INIT_ENABLED = True  # 是否启用自动初始化

# 可选：更细粒度控制
DB_CLEANUP_EPIC_STORIES = True   # 清理当前 Epic 旧记录
DB_CLEANUP_TEMP_STORIES = True   # 清理 TEMP 路径
DB_CLEANUP_TEST_STORIES = True   # 清理测试标记
```

**在 EpicDriver 中使用：**
```python
if config.DB_AUTO_INIT_ENABLED:
    cleanup_stats = self.state_manager.initialize_for_epic(...)
else:
    logger.warning("[Init] Database auto-initialization is DISABLED")
```

## 四、验证方案

### 4.1 单元测试

**测试用例 1：清理当前 Epic Story**

```python
def test_cleanup_epic_stories():
    """验证当前 Epic Story 旧记录被清理"""
    state_mgr = StateManager(':memory:')
    
    # 准备：插入历史记录
    state_mgr.insert_story('epic-1', '1.1', processing_status='failed')
    state_mgr.insert_story('epic-1', '1.2', processing_status='completed')
    state_mgr.insert_story('epic-2', '2.1', processing_status='in_progress')
    
    # 执行清理（只清理 epic-1 的 1.1 和 1.2）
    deleted = state_mgr.cleanup_epic_stories('epic-1', ['1.1', '1.2'])
    
    # 断言
    assert deleted == 2
    
    # 验证：epic-1 的记录被删除
    assert state_mgr.get_story('epic-1', '1.1') is None
    assert state_mgr.get_story('epic-1', '1.2') is None
    
    # 验证：epic-2 的记录仍然存在
    assert state_mgr.get_story('epic-2', '2.1') is not None
```

**测试用例 2：清理 TEMP 路径**

```python
def test_cleanup_temp_stories():
    """验证 TEMP 路径记录被清理"""
    state_mgr = StateManager(':memory:')
    
    # 准备
    state_mgr.insert_story(
        'epic-1', '1.1',
        file_path='D:\\GITHUB\\pytQt_template\\docs\\stories\\1.1.md'
    )
    state_mgr.insert_story(
        'epic-test', 'test-1',
        file_path='C:\\Users\\Admin\\AppData\\Local\\Temp\\tmp123\\test_story.md'
    )
    
    # 执行清理
    deleted = state_mgr.cleanup_temp_stories()
    
    # 断言
    assert deleted == 1
    
    # 验证：正常路径保留
    assert state_mgr.get_story('epic-1', '1.1') is not None
    # 验证：TEMP 路径删除
    assert state_mgr.get_story('epic-test', 'test-1') is None
```

**测试用例 3：清理测试标记**

```python
def test_cleanup_test_stories():
    """验证测试标记记录被清理"""
    state_mgr = StateManager(':memory:')
    
    # 准备
    state_mgr.insert_story('epic-1', '1.1')
    state_mgr.insert_story('epic-test', 'test_story_1')
    state_mgr.insert_story('epic-test', '1.1-test')
    
    # 执行清理
    deleted = state_mgr.cleanup_test_stories()
    
    # 断言
    assert deleted == 2
    
    # 验证：正常 Story 保留
    assert state_mgr.get_story('epic-1', '1.1') is not None
    # 验证：测试 Story 删除
    assert state_mgr.get_story('epic-test', 'test_story_1') is None
    assert state_mgr.get_story('epic-test', '1.1-test') is None
```

**测试用例 4：initialize_for_epic 统一入口**

```python
def test_initialize_for_epic():
    """验证统一初始化方法"""
    state_mgr = StateManager(':memory:')
    
    # 准备：混合数据
    state_mgr.insert_story('epic-1', '1.1', processing_status='failed')  # 旧记录
    state_mgr.insert_story('epic-1', '1.2', file_path='C:\\Temp\\test.md')  # TEMP
    state_mgr.insert_story('epic-2', 'test_story')  # 测试标记
    state_mgr.insert_story('epic-2', '2.1')  # 其他 Epic（应保留）
    
    # 执行初始化
    stats = state_mgr.initialize_for_epic('epic-1', ['1.1', '1.2'])
    
    # 断言清理统计
    assert stats['epic_stories'] == 1  # 只清理了 1.1（1.2 被 TEMP 规则清理）
    assert stats['temp_stories'] == 1  # 1.2
    assert stats['test_stories'] == 1  # test_story
    assert stats['total'] == 3
    
    # 验证：epic-2 的正常 Story 保留
    assert state_mgr.get_story('epic-2', '2.1') is not None
```

### 4.2 集成测试

**测试场景：完整 Epic 运行前初始化**

```python
def test_epic_driver_with_initialization():
    """验证 EpicDriver 运行前自动初始化"""
    
    # 准备：数据库有历史垃圾
    state_mgr = StateManager('test_progress.db')
    for i in range(100):
        state_mgr.insert_story(
            'epic-old',
            f'old-{i}',
            file_path=f'C:\\Temp\\old-{i}.md'
        )
    
    # 执行：运行新 Epic
    driver = EpicDriver()
    driver.run_epic('docs/epics/epic-1.md')
    
    # 验证：旧记录被清理
    old_records = state_mgr.get_stories_by_epic('epic-old')
    assert len(old_records) == 0
    
    # 验证：新 Epic 有干净的初始状态
    new_records = state_mgr.get_stories_by_epic('epic-1')
    assert all(r['processing_status'] in ['in_progress', 'review', 'completed']
               for r in new_records)
```

### 4.3 端到端验证

**验证目标：** 确认初始化后不再出现旧问题

**步骤：**
1. **准备阶段**：
   - 手动在数据库插入 100 条 TEMP 路径记录
   - 手动插入当前 Epic (1.1-1.4) 的旧 `failed` 记录

2. **运行 Epic**：
   ```powershell
   .\.venv\Scripts\activate
   python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-1.md
   ```

3. **观察日志**：
   ```
   === Database Initialization ===
   Cleanup Results:
     - Epic stories removed: 4
     - Temp stories removed: 100
     - Test stories removed: 5
     - Total removed: 109
   Database ready for Epic execution.
   ```

4. **验证结果**：
   - Dev-QA 阶段：无旧状态干扰，4/4 成功
   - 状态同步阶段：
     - 日志中只有 4 条 `StatusUpdateAgent-X.X`
     - 无 "Story file does not exist" 警告
     - 所有 Story 状态为 `Ready for Done`（不是 `Failed`）

## 五、风险与缓解

### 5.1 风险点

**R1：误删重要历史数据**
- 影响：其他 Epic 的进度记录被意外清理
- 缓解：
  - 清理规则严格限定在当前 Epic、TEMP 路径、测试标记
  - 增加配置开关，允许临时禁用
  - 清理前记录日志，便于事后恢复

**R2：清理过程失败导致运行中断**
- 影响：初始化失败，Epic 无法运行
- 缓解：
  - 清理方法内部捕获异常，记录错误但不中断主流程
  - 即使清理失败，仍允许 Dev-QA 继续（只是可能有旧数据污染）

**R3：数据库锁冲突**
- 影响：多个 Epic 同时运行可能死锁
- 缓解：
  - 使用短事务，快速完成清理
  - 或每个 Epic 使用独立数据库文件（如 `epic-1.db`）

### 5.2 回滚方案

**如果自动初始化有问题：**
1. 设置环境变量：`DB_AUTO_INIT_ENABLED=False`
2. 手动清理数据库（一次性操作）：
   ```sql
   DELETE FROM stories WHERE file_path LIKE '%\Temp\%';
   ```
3. 恢复到"不初始化"的旧行为

## 六、可选增强功能

### 6.1 清理前备份（推荐）

在清理前自动备份数据库：

```python
def initialize_for_epic(self, epic_id: str, story_ids: List[str]):
    """初始化前先备份"""
    
    # 备份数据库
    backup_path = f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db.bak"
    shutil.copy('progress.db', backup_path)
    logger.info(f"[Init] Database backed up to {backup_path}")
    
    # 执行清理
    stats = self._do_cleanup(epic_id, story_ids)
    
    return stats
```

### 6.2 清理报告生成（可选）

生成清理报告 JSON：

```python
{
    "timestamp": "2026-01-13T17:00:00",
    "epic_id": "epic-1-core-algorithm-foundation",
    "story_ids": ["1.1", "1.2", "1.3", "1.4"],
    "cleanup_stats": {
        "epic_stories": 4,
        "temp_stories": 287,
        "test_stories": 3,
        "total": 294
    },
    "deleted_records": [
        {"story_id": "1.1", "processing_status": "failed", "reason": "epic_old_record"},
        {"story_id": "test_story", "file_path": "C:\\Temp\\...", "reason": "temp_path"},
        ...
    ]
}
```

### 6.3 智能清理策略（高级）

只清理"明确过期"的记录：

```sql
DELETE FROM stories
WHERE epic_id = ?
  AND story_id IN (?, ?, ?, ?)
  AND updated_at < datetime('now', '-7 days')  -- 只删除 7 天前的旧记录
```

## 七、与其他方案的协同

### 7.1 与方案1（范围限制）的配合

- 方案4 清理历史记录，确保数据库只有当前 Epic 相关数据
- 方案1 限制 StatusUpdateAgent 查询范围
- 结合效果：即使方案1 未启用，方案4 也能显著减少无效记录

### 7.2 与方案2（状态写入）的配合

- 方案4 清理旧处理状态，为本次运行创建干净起点
- 方案2 在 Dev-QA 过程中写入新的、正确的处理状态
- 结合效果：数据库状态完全反映本次运行，无历史污染

### 7.3 与方案3（状态映射）的配合

- 方案4 确保数据库中只有合法的处理状态值（本次运行写入的）
- 方案3 从这些干净数据映射到核心状态
- 结合效果：StatusUpdateAgent 读取的数据源既"范围正确"（方案1）又"内容干净"（方案4）

## 八、实施时间表

| 阶段 | 任务 | 预计耗时 |
|------|------|---------|
| Phase 1 | StateManager 清理方法 | 2 小时 |
| Phase 2 | EpicDriver 调用初始化 | 1 小时 |
| Phase 3 | 初始化日志摘要 | 0.5 小时 |
| Phase 4 | 配置开关（可选） | 0.5 小时 |
| 测试 | 单元测试 + 集成测试 | 2 小时 |
| 验证 | E2E 验证 | 1 小时 |
| **总计** | | **7 小时** |

## 九、成功标准

- ✅ 每次 Epic 运行前自动执行数据库初始化
- ✅ 当前 Epic Story 的旧记录被清理
- ✅ TEMP 路径和测试标记的记录被清理
- ✅ 其他 Epic 的记录不受影响
- ✅ 清理统计在日志中明确记录
- ✅ 状态同步阶段无 "Story file does not exist" 警告
- ✅ 成功 Story 不再被旧失败记录覆盖
