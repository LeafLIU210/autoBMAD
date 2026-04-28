# F2 问题分析摘要（可视化）

## 双重来源问题图解

```
┌─────────────────────────────────────────────────────────────────┐
│                    Database Schema                               │
│                    pipelines 表                                  │
├─────────────────────────────────────────────────────────────────┤
│  pipeline_id  │  status  │  current_node  │  state_json         │
│  (PRIMARY KEY)│  (顶层)   │  (顶层/冗余)   │  (真相源)           │
├───────────────┼──────────┼────────────────┼─────────────────────┤
│  pipe-001     │  running │  analyst       │  {                  │
│               │          │                │    "current_node":  │
│               │          │                │      "analyst",     │
│               │          │                │    "status":        │
│               │          │                │      "running",     │
│               │          │                │    "completed_":    │
│               │          │                │      [...]          │
│               │          │                │  }                  │
└───────────────┴──────────┴────────────────┴─────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ 读取顶层  │   │ 读取JSON │   │ 两者都读  │
        │ (危险)   │   │ (正确)   │   │ (危险)   │
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             ▼              ▼              ▼
        ┌─────────────────────────────────────┐
        │          状态不一致风险               │
        │   展示 vs 恢复 vs 取消 使用不同数据    │
        └─────────────────────────────────────┘
```

## 状态访问路径矩阵

### current_node 读写矩阵

| 操作 | 读来源 | 写目标 | 风险等级 |
|:----:|:------:|:------:|:--------:|
| `update_pipeline_status` | - | **TOP** | 🔴 HIGH |
| `start_pipeline` | - | **TOP** | 🔴 HIGH |
| `restart_from_node` | JSON | **TOP+JSON** | 🔴 CRITICAL |
| `cancel_current_node` | JSON | **TOP** | 🔴 CRITICAL |
| `get_pipeline` | **BOTH** | - | 🔴 CRITICAL |
| `get_pipeline_status` | **TOP** | - | 🟡 HIGH |
| `status` 命令 | **BOTH** | - | 🔴 CRITICAL |
| `node_executor` | - | JSON | 🟢 LOW |

### 风险场景示例

```
场景: 从 analyst 节点重启到 pm 节点

Timeline:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

T1: Pipeline 运行到 analyst 节点
    ┌─────────────────────────────────────────┐
    │ 顶层 current_node = "analyst"           │
    │ state_json.current_node = "analyst"     │
    │ ✓ 一致                                  │
    └─────────────────────────────────────────┘

T2: 调用 restart_from_node("pm")
    ┌─────────────────────────────────────────┐
    │ 读取: state_json.current_node           │
    │       → "analyst" (正确)                │
    │                                         │
    │ 写入: 顶层 current_node = "pm"           │
    │       state_json.current_node = "pm"     │
    │                                         │
    │ 问题: 只更新了部分状态，其他字段未清理   │
    └─────────────────────────────────────────┘

T3: 状态命令查询
    ┌─────────────────────────────────────────┐
    │ status 命令: 使用顶层 current_node      │
    │              → 显示 "pm"                │
    │                                         │
    │ 恢复逻辑: 使用 state_json               │
    │           → 可能显示 "analyst"          │
    │                                         │
    │ ✗ 不一致！用户困惑                     │
    └─────────────────────────────────────────┘
```

## 统一设计方案对比

### 方案A: state_json 唯一真相源（推荐）

```
Before:                          After:
┌───────────────┐                ┌───────────────┐
│  pipelines    │                │  pipelines    │
├───────────────┤                ├───────────────┤
│ pipeline_id   │                │ pipeline_id   │
│ status        │                │ status        │
│ current_node  │───删除───▶     │ state_json    │──┐
│ state_json    │──┐             │ created_at    │  │
└───────────────┘  │             └───────────────┘  │
                   │                                │
                   └──────────真相源───────────────┘
```

**优点**:
- ✅ 单一写入点，无不一致风险
- ✅ 代码简化，维护成本低
- ✅ 符合原始设计意图

**缺点**:
- ⚠️ 需要数据库迁移
- ⚠️ 需要修改所有调用点

### 方案B: 顶层字段作为缓存

```
┌───────────────┐
│  pipelines    │
├───────────────┤
│ pipeline_id   │
│ status        │◄──同步──┐
│ current_node  │◄──同步──┤
│ state_json    │─────┐   │
└───────────────┘     │   │
                      │   │
                   真相源  │
                   写入点  │
                         查询优化
```

**优点**:
- ✅ 查询性能更好
- ✅ 迁移成本低

**缺点**:
- ❌ 需要维护同步逻辑
- ❌ 同步 bug 导致不一致
- ❌ 长期维护成本高

## 实施路线图

```
Phase 1: 基础设施 (Week 1-2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✓] 创建调试工具
[ ] 实现 update_pipeline_state()
[ ] 添加一致性检查
[ ] 创建 PipelineStateView
[ ] 编写数据迁移脚本

Phase 2: 调用点迁移 (Week 3-5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] 迁移 orchestrator.py
[ ] 迁移 cli/commands/status.py
[ ] 迁移其他 CLI 命令
[ ] 迁移 graph.py

Phase 3: 数据迁移 (Week 6)
━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] 执行数据迁移脚本
[ ] 验证数据一致性

Phase 4: 清理 (Week 7)
━━━━━━━━━━━━━━━━━━━━━━
[ ] 删除 current_node 列
[ ] 删除废弃方法
[ ] 更新文档

Phase 5: 验证 (Week 8)
━━━━━━━━━━━━━━━━━━━━━━
[ ] 全量测试
[ ] 回归测试
[ ] 发布
```

## 关键代码片段

### 问题代码示例

```python
# ❌ 问题：混合使用双重来源
# cli/commands/status.py:41-43
pipeline_state = pipeline.get("state", {})           # 从 state_json
current_node = pipeline.get("current_node", "")      # 从顶层！
completed_nodes = pipeline_state.get("completed_nodes", [])
```

### 修复后代码

```python
# ✅ 正确：统一从 state_json 读取
from autoBMAD.docuswarm.storage.state_access import PipelineStateView

view = PipelineStateView(pipeline)
current_node = view.current_node                     # 从 state_json
completed_nodes = view.completed_nodes               # 从 state_json
```

### 新的状态更新接口

```python
# ✅ 推荐：使用新的统一接口
await state_manager.update_pipeline_state(
    pipeline_id,
    {
        "status": "running",
        "current_node": "analyst",
        "completed_nodes": ["pm"]
    }
)
```

## 监控指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 状态不一致检测 | 0 | 运行时一致性检查触发的告警次数 |
| 双重来源访问 | 0 | 代码中读取顶层字段的位置数 |
| state_json 覆盖率 | 100% | 所有状态字段都存储在 state_json |
| 废弃方法调用 | 0 | 旧 API 的调用次数（通过日志监控）|

## 联系与反馈

如有问题或建议，请参考：
- [完整研究报告](./2026-03-25-f2-state-json-consistency-research-report.md)
- [技术规范文档](./2026-03-25-f2-unified-design-spec.md)
