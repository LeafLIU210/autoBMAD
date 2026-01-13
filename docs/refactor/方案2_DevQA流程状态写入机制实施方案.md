# 方案2：Dev-QA 流程状态写入机制实施方案

## 一、问题背景

### 1.1 当前问题
- Dev-QA 成功完成后，数据库"处理状态值"未被正确更新
- 导致 StatusUpdateAgent 同步时仍读取到旧的 `failed` 状态
- 最终把已完成的 Story 从 `Ready for Done` 回写为 `Failed`

### 1.2 根本原因
- Dev/QA Agent 执行完成后，只更新了 Markdown 的核心状态
- 但未通过 StateManager 同步更新数据库的处理状态值
- 状态同步阶段以"数据库为真源"，导致旧失败记录覆盖当前成功结果

## 二、解决方案

### 2.1 核心原则

**由 StateManager 负责处理状态写入，DevQaController 在关键节点触发更新。**

### 2.2 处理状态流转规则

```
Story 开始
    ↓
processing_status = 'in_progress'  (Dev-QA 循环启动)
    ↓
Dev 执行
    ↓
    ├─ Dev 成功 → processing_status = 'review'
    │             (进入 QA 评审阶段)
    │             ↓
    │             QA 执行
    │             ↓
    │             ├─ QA 通过 → processing_status = 'completed'
    │             │            (Story 完成)
    │             │
    │             └─ QA 不通过 → processing_status = 'in_progress'
    │                           (回到开发阶段)
    │
    └─ Dev 失败 → processing_status = 'in_progress'
                  (继续开发)
```

### 2.3 状态值语义

| 处理状态值 | 含义 | 对应核心状态 | 终态？ |
|-----------|------|-------------|--------|
| `in_progress` | 开发中或需要返工 | Ready for Development | 否 |
| `review` | Dev 完成，等待 QA | Ready for Review | 否 |
| `completed` | QA 通过，Story 完成 | Ready for Done / Done | 是 |

**设计说明：**
- `in_progress` 复用于"Dev失败"和"QA不通过"两种场景，强调"仍需继续工作"
- 不单独设置 `failed` 终态，避免失败固化，支持容错重试
- 与现有"容错机制：以获取有效结果为核心"的原则一致

## 三、实施步骤

### 3.1 Phase 1：DevQaController 增加状态写入调用

**位置：** `autoBMAD/epic_automation/controllers/dev_qa_controller.py`

**修改点 1：Dev-QA 循环开始时**

```python
def execute_dev_qa_cycle(self, story_id: str):
    """执行 Dev-QA 循环"""
    
    # 新增：标记开始处理
    self.state_manager.update_story_status(
        story_id=story_id,
        processing_status='in_progress',
        timestamp=datetime.now()
    )
    
    # 原有逻辑：进入循环
    while not self._is_terminal_state(current_status):
        # ...
```

**修改点 2：Dev 阶段完成后**

```python
def _execute_dev_phase(self, story_id: str) -> bool:
    """执行 Dev 阶段"""
    
    # 调用 DevAgent
    dev_result = self.dev_agent.execute(story_id)
    
    # 新增：根据结果更新处理状态
    if dev_result.success:
        self.state_manager.update_story_status(
            story_id=story_id,
            processing_status='review',  # Dev 成功 → 进入评审
            timestamp=datetime.now()
        )
        return True
    else:
        self.state_manager.update_story_status(
            story_id=story_id,
            processing_status='in_progress',  # Dev 失败 → 继续开发
            timestamp=datetime.now()
        )
        return False
```

**修改点 3：QA 阶段完成后**

```python
def _execute_qa_phase(self, story_id: str) -> bool:
    """执行 QA 阶段"""
    
    # 调用 QAAgent
    qa_result = self.qa_agent.execute(story_id)
    
    # 新增：根据结果更新处理状态
    if qa_result.passed:
        self.state_manager.update_story_status(
            story_id=story_id,
            processing_status='completed',  # QA 通过 → 完成
            timestamp=datetime.now()
        )
        return True
    else:
        self.state_manager.update_story_status(
            story_id=story_id,
            processing_status='in_progress',  # QA 不通过 → 返工
            timestamp=datetime.now()
        )
        return False
```

**修改点 4：到达终态时的最终确认**

```python
def _finalize_story(self, story_id: str, final_core_status: str):
    """Story 到达终态，做最终处理"""
    
    # 根据核心状态确定最终处理状态
    if final_core_status == 'Ready for Done':
        final_processing_status = 'completed'
    else:
        # 异常终止场景（如超时、手动取消）
        final_processing_status = 'in_progress'
    
    # 写入数据库
    self.state_manager.update_story_status(
        story_id=story_id,
        processing_status=final_processing_status,
        timestamp=datetime.now()
    )
```

### 3.2 Phase 2：StateManager 完善 update_story_status 方法

**位置：** `autoBMAD/epic_automation/state_manager.py`

**接口规范：**

```python
def update_story_status(
    self,
    story_id: str,
    processing_status: str,
    timestamp: datetime,
    epic_id: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    更新 Story 的处理状态
    
    Args:
        story_id: Story 标识
        processing_status: 处理状态值 ('in_progress' | 'review' | 'completed')
        timestamp: 更新时间
        epic_id: Epic 标识（可选）
        metadata: 额外元数据（如错误信息、重试次数等）
        
    Returns:
        是否更新成功
    """
    
    # 参数校验
    valid_statuses = {'in_progress', 'review', 'completed'}
    if processing_status not in valid_statuses:
        raise ValueError(f"Invalid processing_status: {processing_status}")
    
    # 更新数据库
    query = """
        UPDATE stories
        SET processing_status = ?,
            updated_at = ?,
            metadata = ?
        WHERE story_id = ?
    """
    params = [
        processing_status,
        timestamp.isoformat(),
        json.dumps(metadata or {}),
        story_id
    ]
    
    return self._execute_update(query, params)
```

**关键要点：**
1. **幂等性**：多次调用相同参数，结果一致
2. **事务性**：使用数据库事务确保原子性
3. **日志记录**：每次更新记录详细日志，便于追溯

### 3.3 Phase 3：增加状态转换日志

**目的：** 方便调试和问题追溯

**实现位置：** DevQaController 各状态写入点

```python
def update_story_status(self, story_id: str, processing_status: str, ...):
    """更新处理状态并记录日志"""
    
    logger.info(
        f"[StateTransition] Story {story_id}: "
        f"{old_status} → {processing_status}"
    )
    
    success = self.state_manager.update_story_status(...)
    
    if success:
        logger.info(f"[StateTransition] Status updated successfully")
    else:
        logger.error(f"[StateTransition] Status update failed")
    
    return success
```

**日志示例：**
```
[StateTransition] Story 1.1: None → in_progress
[StateTransition] Status updated successfully
[StateTransition] Story 1.1: in_progress → review
[StateTransition] Status updated successfully
[StateTransition] Story 1.1: review → completed
[StateTransition] Status updated successfully
```

## 四、验证方案

### 4.1 单元测试

**测试用例 1：Dev 成功 → QA 通过的正常流程**

```python
def test_dev_qa_success_flow():
    """验证完整成功流程的状态转换"""
    controller = DevQaController()
    
    # Mock DevAgent 和 QAAgent 都成功
    controller.dev_agent.execute = Mock(return_value=Success())
    controller.qa_agent.execute = Mock(return_value=Passed())
    
    # 执行循环
    controller.execute_dev_qa_cycle('1.1')
    
    # 断言状态转换序列
    status_history = controller.state_manager.get_status_history('1.1')
    assert status_history == [
        'in_progress',  # 开始
        'review',       # Dev 成功
        'completed'     # QA 通过
    ]
```

**测试用例 2：Dev 失败重试流程**

```python
def test_dev_failure_retry():
    """验证 Dev 失败后状态保持 in_progress"""
    controller = DevQaController()
    
    # Mock DevAgent 第一次失败，第二次成功
    controller.dev_agent.execute = Mock(side_effect=[
        Failure(),
        Success()
    ])
    controller.qa_agent.execute = Mock(return_value=Passed())
    
    controller.execute_dev_qa_cycle('1.1')
    
    # 断言状态包含失败重试
    status_history = controller.state_manager.get_status_history('1.1')
    assert status_history == [
        'in_progress',  # 开始
        'in_progress',  # Dev 失败，保持 in_progress
        'review',       # Dev 重试成功
        'completed'     # QA 通过
    ]
```

**测试用例 3：QA 不通过返工流程**

```python
def test_qa_rejection_rework():
    """验证 QA 不通过后回到 in_progress"""
    controller = DevQaController()
    
    controller.dev_agent.execute = Mock(return_value=Success())
    controller.qa_agent.execute = Mock(side_effect=[
        Rejected(),  # 第一次 QA 不通过
        Passed()     # 返工后通过
    ])
    
    controller.execute_dev_qa_cycle('1.1')
    
    status_history = controller.state_manager.get_status_history('1.1')
    assert status_history == [
        'in_progress',  # 开始
        'review',       # Dev 成功
        'in_progress',  # QA 不通过，回到开发
        'review',       # 返工完成
        'completed'     # QA 通过
    ]
```

### 4.2 集成测试

**测试场景：完整 Epic 运行**

1. 准备测试 Epic（4 个 Story）
2. 清空数据库旧记录
3. 运行 epic_driver
4. 验证数据库最终状态：
   ```sql
   SELECT story_id, processing_status FROM stories
   WHERE epic_id = 'test-epic'
   ```
   预期结果：所有 Story 的 `processing_status = 'completed'`

5. 验证 Markdown 文件：
   - 所有 Story 的 `## Status` 为 `Ready for Done`

### 4.3 端到端验证

**验证目标：** 确保状态同步阶段不再覆盖成功状态

**步骤：**
1. 运行完整 Epic（包含 Dev-QA + 质量门控 + 状态同步）
2. 观察日志：
   - Dev-QA 阶段：`Story 1.1 ... completed (Status: Ready for Done)`
   - 状态同步阶段：`Successfully updated 1.1.md status to Done`（不应是 Failed）
3. 检查最终文件：
   ```bash
   grep "## Status" docs-test/stories/1.1.md
   ```
   应输出：`**Status**: Done` 或 `Ready for Done`，不应是 `Failed`

## 五、数据库 Schema 调整（如需要）

### 5.1 当前表结构（假设）

```sql
CREATE TABLE stories (
    story_id TEXT PRIMARY KEY,
    epic_id TEXT,
    file_path TEXT,
    processing_status TEXT,  -- 处理状态值
    created_at DATETIME,
    updated_at DATETIME,
    metadata TEXT  -- JSON 格式的额外信息
);
```

### 5.2 可选优化：增加状态历史表

如果需要审计和分析：

```sql
CREATE TABLE story_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT,
    processing_status TEXT,
    changed_at DATETIME,
    changed_by TEXT,  -- 'DevAgent', 'QAAgent', 'Manual' 等
    metadata TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);
```

**用途：**
- 分析 Dev/QA 失败率
- 追溯状态变化原因
- 生成质量报表

## 六、风险与缓解

### 6.1 风险点

**R1：状态写入失败导致流程中断**
- 影响：DevQaController 无法继续后续步骤
- 缓解：
  - StateManager 写入失败时记录错误但不抛异常
  - 允许"弱一致性"：优先保证核心流程完成，事后可修复数据库

**R2：并发写入冲突**
- 影响：多个 Epic 同时运行可能写冲突
- 缓解：
  - 使用数据库行锁：`SELECT ... FOR UPDATE`
  - 或每个 Epic 使用独立数据库文件

**R3：状态枚举值不一致**
- 影响：代码里写了 `'completed'`，数据库里查到 `'Completed'`
- 缓解：
  - 统一使用小写
  - StateManager 做参数校验，拒绝非法值

### 6.2 回滚方案

**如果新逻辑有问题：**
1. 保留原有"只更新 Markdown"的逻辑为 fallback
2. 添加配置开关：`ENABLE_DB_STATUS_SYNC=False`
3. 临时禁用数据库状态写入，不影响核心 Dev-QA 流程

## 七、与其他方案的协同

### 7.1 与方案1（范围限制）的配合

- 方案2 确保数据库状态正确
- 方案1 确保 StatusUpdateAgent 读取这些正确状态
- 两者结合：完整解决"成功被覆盖为失败"的问题

### 7.2 与方案3（状态映射）的配合

- 方案2 定义处理状态值的写入规则
- 方案3 定义处理状态 → 核心状态的映射规则
- 数据流：`DevQaController 写入 → StateManager 存储 → StatusUpdateAgent 读取并映射`

## 八、实施时间表

| 阶段 | 任务 | 预计耗时 |
|------|------|---------|
| Phase 1 | DevQaController 增加状态写入 | 2 小时 |
| Phase 2 | StateManager 完善接口 | 1 小时 |
| Phase 3 | 状态转换日志 | 0.5 小时 |
| 测试 | 单元测试 + 集成测试 | 2 小时 |
| 验证 | E2E 验证 | 1 小时 |
| **总计** | | **6.5 小时** |

## 九、成功标准

- ✅ Dev 成功后数据库处理状态为 `review`
- ✅ QA 通过后数据库处理状态为 `completed`
- ✅ Dev/QA 失败后数据库处理状态保持 `in_progress`
- ✅ 状态转换日志完整记录所有变化
- ✅ 状态同步阶段不再将成功 Story 覆盖为 Failed
- ✅ 数据库状态与 Markdown 核心状态保持一致（通过映射）
