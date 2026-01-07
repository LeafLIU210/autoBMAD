# 移除外部超时后的重试机制设计建议

**项目**: autoBMAD Epic Automation
**日期**: 2026-01-07
**版本**: 1.0
**关联**: Cancel Scope错误分析报告

---

## 目录

1. [背景](#1-背景)
2. [当前重试机制分析](#2-当前重试机制分析)
3. [移除外部超时的风险评估](#3-移除外部超时的风险评估)
4. [建议的重试机制设计](#4-建议的重试机制设计)
5. [具体实施方案](#5-具体实施方案)
6. [安全性保障](#6-安全性保障)
7. [实施优先级](#7-实施优先级)

---

## 1. 背景

### 1.1 问题描述

根据《Cancel Scope错误分析报告》，外部超时设计是导致Cancel Scope错误的主要原因之一。移除外部超时是根本解决方案，但需要重新设计重试机制以保障系统稳定性。

### 1.2 设计原则

1. **不依赖外部超时** - 避免Cancel Scope错误
2. **防止无限循环** - 确保系统能够终止
3. **避免永久阻塞** - 防止SDK会话卡死
4. **保持功能完整** - 维持dev-qa循环的核心能力
5. **简化代码** - 降低系统复杂度

---

## 2. 当前重试机制分析

### 2.1 多层级重试结构

```python
# Epic Driver级别 (CLI参数)
max_iterations = 3  # 故事重试次数

# Dev-QA循环级别 (硬编码)
max_dev_qa_cycles = 10  # 内部循环保护

# Dev Agent级别
max_retries = 1  # SDK调用重试
retry_delay = 1.0  # 重试间隔

# QA Agent级别
max_retries = 2  # QA重试次数
delay = 2 ** retry_count  # 指数退避

# SDK会话级别 (外部超时)
asyncio.wait_for(timeout=2700s)  # 45分钟
asyncio.wait_for(timeout=2800s)  # 46.7分钟
STORY_TIMEOUT = 14400s  # 4小时
```

### 2.2 重试触发条件

| 层级 | 触发条件 | 当前行为 |
|------|----------|----------|
| **Epic级别** | 故事处理失败 | 重新开始整个Dev-QA循环 |
| **循环级别** | QA未通过且未达最大循环 | 继续下一轮Dev→QA |
| **Dev Agent** | SDK调用失败/超时 | 最多重试1次 |
| **QA Agent** | QA执行失败/异常 | 最多重试2次（指数退避） |
| **SDK会话** | 超时/取消 | 强制取消生成器 |

### 2.3 问题识别

1. **重试层次过多** - 5个层级可能导致过度重试
2. **外部超时依赖** - SDK会话级别的超时是Cancel Scope错误的根源
3. **Agent重试价值低** - dev_agent的1次重试对稳定性提升有限
4. **保护机制冲突** - shield + wait_for嵌套导致scope问题

---

## 3. 移除外部超时的风险评估

### 3.1 移除内容

| 项目 | 位置 | 移除原因 |
|------|------|----------|
| **SDK wait_for包装** | dev_agent.py, qa_agent.py | 防止超时取消生成器 |
| **故事处理超时** | epic_driver.py | 防止4小时超时触发 |
| **外部超时保护** | sdk_wrapper.py | 防止scope冲突 |
| **会话取消机制** | epic_driver.py | 防止cancel scope传播 |

### 3.2 风险识别

#### 🔴 高风险

| 风险 | 描述 | 影响 |
|------|------|------|
| **永久阻塞** | SDK会话因等待用户输入而卡死 | 系统无法继续，永久等待 |
| **无限循环** | dev-qa循环无法结束 | 资源耗尽，系统挂起 |
| **对话失控** | Claude无限制地进行对话 | 消耗大量API配额 |

#### 🟡 中风险

| 风险 | 描述 | 影响 |
|------|------|------|
| **资源泄漏** | 长时间运行导致资源累积 | 性能下降 |
| **用户体验差** | 无进度反馈，用户不知道系统状态 | 用户焦虑，可能误判为卡死 |

#### 🟢 低风险

| 风险 | 描述 | 影响 |
|------|------|------|
| **正常失败** | 因真实错误而失败 | 原本就会失败，无额外影响 |

### 3.3 风险缓解策略

```
风险识别 → 机制设计 → 安全保障 → 监控告警
    ↓           ↓           ↓           ↓
  永久阻塞  → 循环保护   → 进度监控   → 超时终止
  无限循环  → 次数限制   → 状态检查   → 自动恢复
  对话失控  → 轮数限制   → 对话监控   → 配额告警
```

---

## 4. 建议的重试机制设计

### 4.1 重新设计的重试架构

```python
# 简化后的重试结构
Epic级别 (CLI参数)
├── max_iterations = 3  # 保留，故事重试
└── max_dev_qa_cycles = 10  # 保留，内部循环保护

Agent级别 (完全移除)
├── dev_agent: max_retries = 0  # 移除，简化
└── qa_agent: max_retries = 0  # 移除，简化

SDK级别 (改为限制模式)
└── max_turns = 1000  # 保留，对话轮数限制
```

### 4.2 核心设计决策

#### 决策1：保留循环保护，移除超时保护

**原因**：
- 循环保护防止无限执行
- 超时保护导致Cancel Scope错误
- SDK内部机制更稳定

#### 决策2：移除Agent重试，依赖循环重试

**原因**：
- 减少重试层次
- dev-qa循环本身就是重试机制
- 单次SDK调用失败应立即失败

#### 决策3：引入max_turns限制

**原因**：
- 防止对话无限进行
- 比外部超时更温和
- SDK内部机制，不会导致scope问题

### 4.3 新的执行流程

```python
async def process_story(story):
    """新的故事处理流程 - 无外部超时"""

    # 外部重试：max_iterations
    for iteration in range(1, max_iterations + 1):
        try:
            # 内部循环保护：max_dev_qa_cycles
            result = await run_dev_qa_cycles(story, max_cycles=10)
            if result:
                return True  # 成功

        except PermanentFailure:
            # 永久性错误，不重试
            return False

        except RetryableError:
            # 可重试错误，继续下一次重试
            continue

    # 所有重试都失败
    return False

async def run_dev_qa_cycles(story, max_cycles):
    """Dev-QA循环 - 内部保护"""

    for cycle in range(1, max_cycles + 1):
        # Dev阶段 - 无重试
        dev_result = await execute_dev(story)

        # QA阶段 - 无重试
        qa_result = await execute_qa(story)

        # 检查是否完成
        if qa_result.passed and is_story_done(story):
            return True

    return False  # 达到最大循环次数

async def execute_dev(story):
    """Dev执行 - 无超时包装"""

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        max_turns=1000,  # 对话轮数限制
        cwd=str(Path.cwd())
    )

    # 直接执行，无wait_for或shield
    sdk = SafeClaudeSDK(prompt, options)
    return await sdk.execute()
```

---

## 5. 具体实施方案

### 5.1 修改清单

#### Epic Driver级别

**文件**: `epic_driver.py`

**修改1**: 移除故事处理的外部超时
```python
# 修改前
return await asyncio.wait_for(
    self._process_story_impl(story),
    timeout=STORY_TIMEOUT
)

# 修改后
return await self._process_story_impl(story)
```

**修改2**: 移除shield包装（可选）
```python
# 修改前
return await asyncio.shield(self._execute_story_processing(story))

# 修改后
return await self._execute_story_processing(story)
```

#### Dev Agent级别

**文件**: `dev_agent.py`

**修改1**: 移除外部超时和重试
```python
# 修改前
result = await asyncio.wait_for(
    asyncio.shield(self._session_manager.execute_isolated(...)),
    timeout=2800.0
)

# 修改后
sdk = SafeClaudeSDK(prompt, options, timeout=None)
return await sdk.execute()
```

**修改2**: 移除重试循环
```python
# 修改前
max_retries = 1
for attempt in range(max_retries):
    # 重试逻辑
    pass

# 修改后
# 直接执行，无重试
return await sdk.execute()
```

#### QA Agent级别

**文件**: `qa_agent.py`

**修改**: 简化重试逻辑
```python
# 修改前
while retry_count <= max_retries:
    # 重试逻辑
    pass

# 修改后
# 单次执行，无重试
result = await execute_qa_review(story_path)
return result.to_dict()
```

#### SDK Wrapper级别

**文件**: `sdk_wrapper.py`

**修改**: 移除外部超时参数
```python
# 修改前
class SafeClaudeSDK:
    def __init__(self, prompt, options, timeout=1800.0):
        self.timeout = timeout

# 修改后
class SafeClaudeSDK:
    def __init__(self, prompt, options, timeout=None):
        self.timeout = timeout  # 保留但不使用
```

### 5.2 新增配置

#### SDK配置增强

```python
# 新的SDK选项
SDK_OPTIONS = {
    "max_turns": 1000,           # 对话轮数限制
    "permission_mode": "bypassPermissions",  # 权限模式
    "cwd": str(Path.cwd()),      # 工作目录
    "max_tool_calls": 500,       # 工具调用限制（如果支持）
    "enable_thinking": True      # 思考模式
}
```


---

## 6. 安全性保障

### 6.1 多层防护机制

```python
# 防护层级
┌─────────────────────────────────────────┐
│ L1: max_iterations (Epic级别)           │
│ - 防止在无效故事上浪费资源              │
│ - 默认3次，可配置                       │
├─────────────────────────────────────────┤
│ L2: max_dev_qa_cycles (循环级别)        │
│ - 防止单次重试内的无限循环              │
│ - 硬编码10次                           │
├─────────────────────────────────────────┤
│ L3: max_turns (SDK级别)                │
│ - 防止对话无限进行                     │
│ - 默认1000轮                            │
├─────────────────────────────────────────┤
```

### 6.2 永久阻塞的检测与处理

#### 6.2.1 检测机制

```python
class SDKProgressMonitor:
    """SDK进度监控器"""

    def __init__(self):
        self.last_activity = time.time()
        self.message_count = 0
        self.max_inactive = 1800  # 30分钟

    async def check_progress(self):
        """检查SDK是否在正常进行"""

        # 检查消息数量变化
        if self.sdk_has_new_message():
            self.last_activity = time.time()
            return True

        # 检查无活动时间
        inactive_time = time.time() - self.last_activity
        if inactive_time > self.max_inactive:
            logger.warning(f"SDK inactive for {inactive_time}s")
            return False

        return True

    def sdk_has_new_message(self) -> bool:
        """检查是否有新消息（需要与SDK集成）"""
        # 实现消息计数检查
        pass
```

#### 6.2.2 处理策略

```python
# 处理策略
async def handle_sdk_stuck():
    """处理SDK卡死"""


    # 策略: 标记为失败并继续下一个故事
    await mark_story_as_failed("SDK timeout/stuck")
```

### 6.3 资源保护机制

#### 6.3.1 内存保护

```python
# 限制并发故事数量
MAX_CONCURRENT_STORIES = 1  # 串行处理

# 清理历史记录
MAX_HISTORY_SIZE = 100
```

#### 6.3.2 API配额保护

```python
# 预算保护
DAILY_API_BUDGET = 1000  # 美元
MAX_TOKENS_PER_STORY = 50000

# 告警阈值
BUDGET_ALERT_THRESHOLD = 0.8  # 80%
```

---

## 7. 实施优先级

### Phase 1: 核心修改 (高优先级)

**目标**: 移除外部超时，消除Cancel Scope错误

| 任务 | 负责人 | 工作量 | 风险 |
|------|--------|--------|------|
| 移除SDK调用的wait_for | 开发团队 | 1天 | 低 |
| 移除故事处理的超时 | 开发团队 | 1天 | 低 |
| 配置max_turns | 开发团队 | 0.5天 | 低 |
| 更新文档 | 技术文档 | 0.5天 | 低 |

**验收标准**:
- [ ] 代码中无asyncio.wait_for包装SDK调用
- [ ] 所有SDK调用配置了max_turns
- [ ] 运行测试无Cancel Scope错误

### Phase 2: 重试机制简化 (中优先级)

**目标**: 简化重试逻辑，降低复杂度

| 任务 | 负责人 | 工作量 | 风险 |
|------|--------|--------|------|
| 移除dev_agent重试 | 开发团队 | 0.5天 | 低 |
| 简化qa_agent重试 | 开发团队 | 0.5天 | 低 |
| 清理相关备份文件 | 开发团队 | 0.5天 | 低 |
| 更新日志输出 | 开发团队 | 0.5天 | 低 |

**验收标准**:
- [ ] Agent中无重试循环
- [ ] 重试仅通过Epic级别的max_iterations
- [ ] 日志清晰反映重试逻辑


### 实施风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| SDK真的卡死 | 中 | 高 | 保留max_turns保护 |
| 功能回退 | 低 | 高 | 充分测试 |

### 测试计划

#### 单元测试

1. **SDK调用测试**
   - 测试无超时保护的SDK调用
   - 测试max_turns限制
   - 测试正常完成场景

2. **重试逻辑测试**
   - 测试max_iterations限制
   - 测试循环保护
   - 测试失败场景

#### 集成测试

1. **完整工作流测试**
   - 测试正常故事处理
   - 测试失败故事重试
   - 测试边界条件

2. **性能测试**
   - 测试长时间运行稳定性
   - 测试资源使用情况
   - 测试并发安全

#### 压力测试

1. **极端场景测试**
   - 测试无效故事的多次重试
   - 测试网络异常恢复
   - 测试SDK异常行为

---

## 结论

### 核心建议

1. **立即实施Phase 1** - 移除外部超时是消除Cancel Scope错误的根本方案
2. **保留必要保护** - max_iterations, max_dev_qa_cycles, max_turns是安全保障
3. **简化重试机制** - 减少不必要的重试层次

### 预期收益

- ✅ **完全消除Cancel Scope错误** - 移除外部超时
- ✅ **代码复杂度降低** - 减少重试层次
- ✅ **调试难度降低** - 更清晰的控制流
- ✅ **资源使用优化** - 减少不必要的重试
- ⚠️ **永久阻塞风险** - 通过max_turns缓解

### 后续行动

1. 评审并批准此设计建议
2. 开始Phase 1实施
3. 进行全面测试
4. 根据测试结果调整
5. 考虑Phase 3增强功能

---

*报告生成时间: 2026-01-07*
*与Cancel Scope错误分析报告配套使用*
