# 方案1：StatusUpdateAgent 同步范围限制实施方案

## 一、问题背景

### 1.1 当前问题
- StatusUpdateAgent 每次运行扫描数据库全部 298 条 Story 记录
- 导致单次 Epic 运行耗时过长（20+ 分钟状态同步）
- 大量历史/临时 Story 记录干扰当前 Epic 结果

### 1.2 影响范围
- 性能：每条记录 SDK 调用耗时 6-100 秒
- 可维护性：日志充斥无关 Story 的处理信息
- 数据一致性：历史记录可能覆盖当前运行结果

## 二、解决方案

### 2.1 核心原则
**StatusUpdateAgent 只处理当前 Epic 涉及的 Story ID 列表，不扫描全库记录。**

### 2.2 数据流设计

```
EpicDriver 解析 Epic
    ↓
提取 Story ID 列表：['1.1', '1.2', '1.3', '1.4']
    ↓
传递给 StatusUpdateAgent(epic_story_ids)
    ↓
StatusUpdateAgent 查询数据库：
  WHERE story_id IN ('1.1', '1.2', '1.3', '1.4')
    ↓
仅对这 4 条记录执行状态同步
```

### 2.3 接口设计

#### 2.3.1 StatusUpdateAgent 输入参数调整

**修改前：**
```python
# StatusUpdateAgent 自行扫描全库
status_agent = StatusUpdateAgent()
status_agent.sync_all_stories()  # 处理所有记录
```

**修改后：**
```python
# 接受显式的 Story ID 列表
status_agent = StatusUpdateAgent()
status_agent.sync_stories(
    epic_id='epic-1-core-algorithm-foundation',
    story_ids=['1.1', '1.2', '1.3', '1.4']
)
```

#### 2.3.2 StateManager 查询接口

**新增方法：**
```python
def get_stories_by_ids(self, epic_id: str, story_ids: List[str]) -> List[StoryRecord]:
    """
    根据 Epic ID 和 Story ID 列表查询处理状态
    
    Args:
        epic_id: 当前 Epic 标识
        story_ids: Story ID 列表
        
    Returns:
        符合条件的 Story 记录列表（含最新处理状态）
    """
    # SQL: SELECT * FROM stories 
    #      WHERE epic_id = ? AND story_id IN (?, ?, ...)
    #      ORDER BY updated_at DESC
```

## 三、实施步骤

### 3.1 Phase 1：修改 EpicDriver 调用逻辑

**位置：** `autoBMAD/epic_automation/epic_driver.py`

**变更点：**
1. 在 Epic 解析完成后，保存 `epic_id` 和 `story_ids`
2. 调用 StatusUpdateAgent 时传入这两个参数

**伪代码：**
```python
# 解析 Epic
epic_id, stories = parse_epic(epic_file)
story_ids = [story.id for story in stories]

# Phase 2: 质量门控
run_quality_gates()

# Phase 3: 状态同步（修改此处）
status_agent = StatusUpdateAgent()
status_agent.sync_stories(
    epic_id=epic_id,
    story_ids=story_ids  # 显式传入
)
```

### 3.2 Phase 2：修改 StatusUpdateAgent 内部逻辑

**位置：** `autoBMAD/epic_automation/agents/status_update_agent.py`

**变更点：**
1. 移除 `sync_all_stories()` 方法或标记为 deprecated
2. 新增 `sync_stories(epic_id, story_ids)` 方法
3. 查询数据库时添加 WHERE 过滤条件

**伪代码：**
```python
def sync_stories(self, epic_id: str, story_ids: List[str]):
    """只同步指定 Epic 的 Story 列表"""
    
    # 从 StateManager 获取这批 Story 的最新处理状态
    story_records = self.state_manager.get_stories_by_ids(
        epic_id=epic_id,
        story_ids=story_ids
    )
    
    # 对每条记录：处理状态 → 核心状态 → 写回 Markdown
    for record in story_records:
        processing_status = record.processing_status
        core_status = self._map_to_core_status(processing_status)
        
        # 通过 SDK 更新 Story 文档
        self._update_story_markdown(
            story_path=record.file_path,
            new_status=core_status
        )
```

### 3.3 Phase 3：StateManager 新增查询方法

**位置：** `autoBMAD/epic_automation/state_manager.py`

**变更点：**
1. 新增 `get_stories_by_ids()` 方法
2. 使用参数化查询防止 SQL 注入

**实现要点：**
```python
def get_stories_by_ids(self, epic_id: str, story_ids: List[str]) -> List[Dict]:
    """
    按 Epic ID 和 Story ID 列表查询
    
    返回字段：
    - story_id
    - epic_id
    - processing_status (最新处理状态)
    - file_path (Markdown 路径)
    - updated_at
    """
    placeholders = ','.join(['?'] * len(story_ids))
    query = f"""
        SELECT story_id, epic_id, processing_status, file_path, updated_at
        FROM stories
        WHERE epic_id = ? AND story_id IN ({placeholders})
        ORDER BY updated_at DESC
    """
    params = [epic_id] + story_ids
    return self._execute_query(query, params)
```

## 四、验证方案

### 4.1 单元测试

**测试用例 1：正常场景**
```python
def test_sync_stories_with_specific_ids():
    """验证只处理指定的 Story ID"""
    agent = StatusUpdateAgent()
    
    # 模拟数据库有 10 条记录，当前 Epic 只关心 3 条
    agent.sync_stories(
        epic_id='epic-1',
        story_ids=['1.1', '1.2', '1.3']
    )
    
    # 断言：只调用了 3 次 SDK
    assert agent.sdk_call_count == 3
```

**测试用例 2：空列表**
```python
def test_sync_stories_with_empty_list():
    """验证空列表不触发任何处理"""
    agent = StatusUpdateAgent()
    agent.sync_stories(epic_id='epic-1', story_ids=[])
    
    assert agent.sdk_call_count == 0
```

### 4.2 集成测试

**测试场景：**
1. 准备数据库：插入当前 Epic 4 条 + 历史 Epic 10 条记录
2. 运行 epic_driver，只处理当前 4 条
3. 验证日志：
   - 只有 4 条 "StatusUpdateAgent-X.X" 日志
   - 无历史 Story 的 WARNING

### 4.3 性能验证

**预期效果：**
- 修改前：298 条 × 平均 15 秒 = 74.5 分钟
- 修改后：4 条 × 平均 15 秒 = 1 分钟

**验证指标：**
- 状态同步阶段耗时从 20+ 分钟降至 2 分钟以内
- 日志文件大小显著减少（无大量无关 Story 日志）

## 五、风险与缓解

### 5.1 风险点

**R1：全局状态整理需求未满足**
- 影响：如需要生成"所有 Epic 的状态总览报表"，当前方案无法覆盖
- 缓解：单独设计离线批处理工具（`sync_all_stories_batch.py`）

**R2：Story ID 提取错误**
- 影响：若 Epic 解析阶段漏掉某些 Story，状态同步会遗漏
- 缓解：在 Epic 解析后增加校验步骤，确保所有 Story 都被识别

### 5.2 回滚方案

**如果新方案有问题：**
1. 保留 `sync_all_stories()` 方法为 fallback
2. 添加配置开关：`USE_LEGACY_SYNC_MODE=True`
3. 可临时切回全量扫描模式


## 七、实施时间表

| 阶段 | 任务 | 预计耗时 |
|------|------|---------|
| Phase 1 | 修改 EpicDriver 调用逻辑 | 1 小时 |
| Phase 2 | 修改 StatusUpdateAgent | 2 小时 |
| Phase 3 | StateManager 新增查询方法 | 1 小时 |
| 测试 | 单元测试 + 集成测试 | 2 小时 |
| 验证 | 实际 Epic 运行验证 | 1 小时 |
| **总计** | | **7 小时** |

## 八、成功标准

- ✅ StatusUpdateAgent 仅处理当前 Epic 的 Story（日志可验证）
- ✅ 状态同步阶段耗时 < 2 分钟（对于 4 条 Story 的 Epic）
- ✅ 日志中无历史 Story / Temp Story 的处理记录
- ✅ 当前 Epic 的状态同步结果正确（与数据库处理状态一致）
