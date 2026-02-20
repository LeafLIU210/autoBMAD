# Ready for Review 状态处理Bug修复方案

**模块**: autoBMAD/epic_automation  
**文件**: epic_driver.py  
**日期**: 2026-02-17  
**严重级别**: Critical

---

## 一、问题概述

| 项目 | 说明 |
|------|------|
| Bug类型 | 代码重构不完整 |
| 根因 | `epic_driver.py` 对 "Ready for Review" 状态调用废弃的 `execute_qa_phase()` 而非 `execute_dev_phase()` |
| 影响范围 | 所有处于 "Ready for Review" 状态的 Story 无法完成 QA 流程 |
| 表现 | Story 在 Dev-QA 循环中无限循环直到达到最大迭代次数 (10次) |

---

## 二、技术分析

### 2.1 调用链路

```
EpicDriver._execute_story_processing()
  │
  ├─ status == "Draft" / "Ready for Development" / "In Progress" / "Failed"
  │   └─ execute_dev_phase() ✓ 正确调用 DevQaController
  │
  └─ status == "Ready for Review"
      └─ execute_qa_phase() ✗ 调用废弃的空方法
```

### 2.2 问题代码

**文件**: `epic_driver.py` Line 1798-1802

```python
elif current_status == "Ready for Review":
    # 需要 QA
    logger.info(f"[Cycle {iteration}] Executing QA phase (status: {current_status})")
    await self.execute_qa_phase(story_path)  # ← BUG
    # ⚠️ 不检查返回值，继续循环
```

### 2.3 废弃方法实现

**文件**: `epic_driver.py` Line 1639-1656

```python
async def execute_qa_phase(self, story_path: str) -> bool:
    """
    Note: This method is now deprecated. QA is handled by DevQaController
    in the execute_dev_phase method.
    """
    logger.warning(
        f"execute_qa_phase is deprecated. QA is now handled by DevQaController. "
        f"Use execute_dev_phase which manages the complete Dev-QA cycle."
    )
    return True  # No-op - QA is handled in DevQaController
```

### 2.4 正确实现参考

**文件**: `controllers/devqa_controller.py` Line 218-233

```python
elif current_status == "Ready for Review":
    # 需要 QA
    self._log_execution("[Decision] Ready for Review → QA phase")
    story_path = self._story_path

    async def call_qa_agent():
        return await self.qa_agent.execute(story_path)

    qa_result = await self._execute_within_taskgroup(call_qa_agent)

    # QA完成后更新处理状态
    await self._update_processing_status_after_qa(story_path, qa_result)

    # QA 完成后，再次查询状态
    return await self._make_decision("AfterQA")
```

---

## 三、架构背景

### 3.1 重构历史

Epic Automation 模块经历了以下架构演进：

| 阶段 | 架构 | QA处理方式 |
|------|------|------------|
| V1 | 直接调用 Agent | `qa_agent.execute()` |
| V2 | Controller 封装 | `DevQaController` 统一管理 Dev + QA |
| 当前 | 混合状态 | `execute_dev_phase()` 使用新架构，`execute_qa_phase()` 未迁移 |

### 3.2 设计意图

`DevQaController` 设计为状态机驱动的统一控制器：

```
┌─────────────────────────────────────────────────────────────┐
│                    DevQaController                          │
├─────────────────────────────────────────────────────────────┤
│  _make_decision(current_state)                              │
│    │                                                        │
│    ├─ "Draft" / "Ready for Development" → dev_agent.execute │
│    ├─ "In Progress"                     → dev_agent.execute │
│    ├─ "Ready for Review"                → qa_agent.execute  │
│    └─ "Done" / "Ready for Done"         → return (终态)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、修复方案

### 4.1 修改位置

**文件**: `autoBMAD/epic_automation/epic_driver.py`  
**行号**: 1801

### 4.2 修改内容

```python
# 修改前 (Line 1798-1802)
elif current_status == "Ready for Review":
    # 需要 QA
    logger.info(f"[Cycle {iteration}] Executing QA phase (status: {current_status})")
    await self.execute_qa_phase(story_path)
    # ⚠️ 不检查返回值，继续循环

# 修改后
elif current_status == "Ready for Review":
    # 需要 QA - DevQaController 内部会调用 qa_agent
    logger.info(f"[Cycle {iteration}] Executing QA phase (status: {current_status})")
    await self.execute_dev_phase(story_path, iteration)
    # ⚠️ 不检查返回值，继续循环
```

### 4.3 修改说明

| 项目 | 说明 |
|------|------|
| 修改范围 | 单行代码替换 |
| 兼容性 | 完全兼容，`execute_dev_phase` 已处理所有状态 |
| 风险等级 | 低 - 仅更改方法调用 |

---

## 五、验证方案

### 5.1 单元测试

```bash
cd D:\GITHUB\wuwa_skillplayer
.\venv\Scripts\Activate.ps1
python -m pytest autoBMAD/epic_automation/tests/ -v -k "qa" --tb=short
```

### 5.2 集成测试

创建测试 Story 文件，状态设为 "Ready for Review"，运行 Epic Driver 验证 QA 流程执行。

### 5.3 日志验证

修复后运行 Epic，日志应显示：

```
# 修复前 (错误)
[Cycle N] Executing QA phase (status: Ready for Review)
execute_qa_phase is deprecated...  ← 废弃警告

# 修复后 (正确)
[Cycle N] Executing QA phase (status: Ready for Review)
[DevQaController] [Decision] Ready for Review → QA phase  ← 实际执行
```

---

## 六、后续建议

### 6.1 清理废弃代码

完成修复验证后，建议删除或标记废弃方法：

```python
@deprecated("Use execute_dev_phase instead")
async def execute_qa_phase(self, story_path: str) -> bool:
    raise NotImplementedError(
        "execute_qa_phase is deprecated. Use execute_dev_phase."
    )
```

### 6.2 状态路由统一

考虑将 `_execute_story_processing` 中的状态分支简化为统一调用：

```python
# 所有非终态统一调用 execute_dev_phase
if current_status not in ["Done", "Ready for Done"]:
    await self.execute_dev_phase(story_path, iteration)
```

---

## 七、相关文件

| 文件 | 作用 |
|------|------|
| `epic_driver.py` | Epic 执行主驱动 |
| `controllers/devqa_controller.py` | Dev-QA 统一控制器 |
| `agents/qa_agent.py` | QA 代理实现 |
| `agents/dev_agent.py` | Dev 代理实现 |

---

*文档生成: 2026-02-17*
