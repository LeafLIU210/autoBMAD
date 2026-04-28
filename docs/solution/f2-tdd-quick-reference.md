# F2 TDD 快速参考卡片

## 🎯 一句话目标

> 将 `pipelines.current_node` 从**双重来源**改造为**state_json 单一真相源**

---

## 📋 实施检查清单

### Phase 1: 止血 (P0) - Week 1

```
□ 1. 创建测试文件
    □ tests/storage/test_state_consistency_detection.py
    □ tests/storage/test_state_manager_sync_update.py

□ 2. 运行测试确认失败 (Red)
    pytest tests/storage/test_state_consistency_detection.py -v

□ 3. 实现功能 (Green)
    □ _verify_state_consistency() 方法
    □ update_pipeline_status() 同步更新 state_json

□ 4. 重构优化 (Refactor)
    □ 提取 _update_state_json_partial() 辅助方法
    □ 添加适当的日志

□ 5. 验证所有测试通过
    pytest tests/storage/test_state_consistency*.py -v
```

### Phase 2: 迁移 (P1) - Week 2-3

```
□ 1. 创建测试文件
    □ tests/storage/test_state_access_view.py
    □ tests/storage/test_unified_state_read.py
    □ tests/storage/test_backward_compatibility.py

□ 2. 实现 PipelineStateView
    □ class PipelineStateView
    □ current_node 属性从 state_json 读取
    □ is_node_completed() 方法

□ 3. 实现统一读取 API
    □ get_current_node() - 从 state_json
    □ get_pipeline_status() - 从 state_json
    □ update_pipeline_state() - 统一写入入口

□ 4. 标记废弃
    □ update_pipeline_status() 添加 DeprecationWarning

□ 5. 更新调用点
    □ cli/commands/status.py 使用 PipelineStateView
    □ pipeline/orchestrator.py 使用新 API
```

### Phase 3: 清理 (P2) - Week 4

```
□ 1. 数据库迁移
    □ 编写迁移脚本删除 current_node 列
    □ 测试数据迁移

□ 2. 移除废弃代码
    □ 删除 update_pipeline_status() 方法
    □ 删除顶层字段相关逻辑

□ 3. 最终验证
    □ 运行所有测试
    □ 集成测试通过
```

---

## 🔑 关键代码片段

### 1. 一致性检查 (Phase 1)

```python
def _verify_state_consistency(self, pipeline_id: str) -> None:
    """运行时一致性检查"""
    pipeline = self._get_raw_pipeline(pipeline_id)
    top_current_node = pipeline["current_node"]
    state = json.loads(pipeline["state_json"] or "{}")
    state_current_node = state.get("current_node")
    
    if top_current_node != state_current_node:
        logger.warning("state_inconsistency_detected",
                      pipeline_id=pipeline_id,
                      top_current_node=top_current_node,
                      state_current_node=state_current_node)
```

### 2. 同步更新 (Phase 1)

```python
def update_pipeline_status(self, pipeline_id, status, current_node=None):
    # 1. 更新顶层字段（兼容）
    self._update_top_level(pipeline_id, status, current_node)
    
    # 2. 同步更新 state_json（新增）
    state_update = {"status": status}
    if current_node is not None:
        state_update["current_node"] = current_node
    self._update_state_json_partial(pipeline_id, state_update)
```

### 3. 状态视图 (Phase 2)

```python
class PipelineStateView:
    def __init__(self, pipeline_data):
        self._data = pipeline_data
        self._state = pipeline_data.get("state", {})
    
    @property
    def current_node(self) -> str | None:
        """从 state_json 读取"""
        return self._state.get("current_node")
```

### 4. 统一写入 (Phase 2)

```python
def update_pipeline_state(self, pipeline_id, state_update):
    """统一状态写入入口"""
    return self._update_state_json_partial(pipeline_id, state_update)
```

---

## 🧪 常用测试命令

```bash
# 运行 Phase 1 测试
pytest tests/storage/test_state_consistency_detection.py tests/storage/test_state_manager_sync_update.py -v

# 运行 Phase 2 测试
pytest tests/storage/test_state_access_view.py tests/storage/test_unified_state_read.py -v

# 运行所有 F2 测试
pytest tests/storage/test_state*.py tests/storage/test_unified*.py tests/storage/test_backward*.py -v

# 生成覆盖率报告
pytest tests/storage/ --cov=autoBMAD.docuswarm.storage --cov-report=html

# 调试单个测试
pytest tests/storage/test_state_consistency_detection.py::TestStateConsistencyDetection::test_detect_inconsistency -v -s
```

---

## 🚨 常见陷阱

### 陷阱 1: 直接从顶层读取

```python
# ❌ 错误
pipeline = state_manager.get_pipeline(pipeline_id)
current_node = pipeline["current_node"]  # 从顶层读取

# ✅ 正确
current_node = pipeline["state"]["current_node"]  # 从 state_json
# 或
view = PipelineStateView(pipeline)
current_node = view.current_node
```

### 陷阱 2: 忘记同步更新

```python
# ❌ 错误 - 只更新顶层
conn.execute("UPDATE pipelines SET current_node = ?", (node_id,))

# ✅ 正确 - 同时更新 state_json
conn.execute("UPDATE pipelines SET current_node = ?", (node_id,))
self._update_state_json_partial(pipeline_id, {"current_node": node_id})
```

### 陷阱 3: 破坏向后兼容

```python
# ❌ 错误 - 直接删除旧方法
def update_pipeline_status(...):  # 删除了！
    ...

# ✅ 正确 - 先标记废弃
def update_pipeline_status(...):
    warnings.warn("deprecated", DeprecationWarning)
    return self.update_pipeline_state(...)
```

---

## 📊 测试覆盖率目标

| 模块 | 目标覆盖率 | 关键路径 |
|------|-----------|----------|
| storage/state_manager.py | 90% | update_pipeline_state, _verify_state_consistency |
| storage/state_access.py | 95% | PipelineStateView 所有方法 |
| pipeline/orchestrator.py | 80% | restart_from_node, cancel_current_node |
| cli/commands/status.py | 85% | status 命令 |

---

## 🔗 相关文件

| 文件 | 作用 | 修改阶段 |
|------|------|----------|
| `storage/state_manager.py` | 核心状态管理 | Phase 1, 2 |
| `storage/state_access.py` | 状态访问视图 | Phase 2 |
| `cli/commands/status.py` | 状态显示 | Phase 2 |
| `pipeline/orchestrator.py` | 编排逻辑 | Phase 2 |
| `storage/database.py` | Schema | Phase 3 |

---

## 📞 调试技巧

### 启用详细日志

```python
import logging
logging.getLogger("autoBMAD.docuswarm.storage").setLevel(logging.DEBUG)
```

### 检查数据库状态

```python
import sqlite3
conn = sqlite3.connect("docuswarm.db")
cursor = conn.execute("SELECT pipeline_id, current_node, state_json FROM pipelines")
for row in cursor:
    print(f"ID: {row[0]}, Top: {row[1]}, State: {json.loads(row[2]).get('current_node')}")
conn.close()
```

### 使用调试工具

```bash
python tools/f2_state_consistency_analyzer.py --db docuswarm.db
```

---

## ✅ 完成标准

### Phase 1 完成标准
- [ ] 一致性检查测试全部通过
- [ ] 同步更新测试全部通过
- [ ] 代码审查通过
- [ ] Staging 环境运行 24 小时无告警

### Phase 2 完成标准
- [ ] PipelineStateView 测试全部通过
- [ ] 统一读取 API 测试全部通过
- [ ] 向后兼容性测试全部通过
- [ ] 所有调用点更新完成

### Phase 3 完成标准
- [ ] 最终一致性测试全部通过
- [ ] 数据库迁移成功
- [ ] 生产环境无回归
