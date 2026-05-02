# Finding 1-5 TDD 快速参考

**一键查阅**: 核心问题、解决方案、关键代码变更

---

## Finding 1: Session Manager 初始化 [P0]

### 核心问题
```python
# 顺序错误: 先验证，后创建 session_manager
await self._context_validator.validate_context_with_llm(subject_context)  # ❌ 报错
session_manager = self._get_or_create_session_manager()  # 创建太晚
```

### 解决方案
```python
# 延迟注入: 将 session_manager 从构造函数移到方法参数
session_manager = self._get_or_create_session_manager()  # ✅ 先创建
await self._context_validator.validate_context_with_llm(
    subject_context,
    session_manager=session_manager  # ✅ 显式传入
)
```

### 关键变更
| 文件 | 变更 | 行数 |
|------|------|------|
| `context/validator.py` | 移除 `__init__` 的 `session_manager` 参数 | ~-20 |
| `context/validator.py` | `validate_context_with_llm` 添加 `session_manager` 参数 | ~+5 |
| `pipeline/orchestrator.py` | 调整 `start_pipeline` 调用顺序 | ~+3 |

### 测试要点
```python
def test_start_pipeline_without_session_manager():
    orchestrator = HybridOrchestrator(db_path=":memory:")
    # 不应抛出 RuntimeError
    pipeline_id = await orchestrator.start_pipeline({"subject": "test"})
```

---

## Finding 2: Pipeline ID 一致性 [P0]

### 核心问题
```python
# ID 不一致: 写入用生成 ID，更新用自定义 ID
db_pipeline_id = self._state_manager.create_pipeline(...)  # 生成: pipeline-xxx
final_pipeline_id = pipeline_id or db_pipeline_id  # 可能是自定义 ID ❌
self._state_manager.update_pipeline_status(final_pipeline_id, ...)  # 找不到！
```

### 解决方案
```python
# 移除自定义 ID 参数，强制使用数据库生成 ID
async def start_pipeline(self, subject_context: dict) -> str:  # 无 pipeline_id 参数
    pipeline_id = self._state_manager.create_pipeline(...)  # ✅ 直接使用
    self._state_manager.update_pipeline_status(pipeline_id, ...)  # ✅ 一致
```

### 关键变更
| 文件 | 变更 | 行数 |
|------|------|------|
| `pipeline/orchestrator.py` | 移除 `pipeline_id` 参数 | ~-5 |
| `cli/services/pipeline_service.py` | 更新调用点 | ~-1 |

### 测试要点
```python
def test_created_pipeline_id_matches_returned_id():
    pipeline_id = await orchestrator.start_pipeline({"subject": "test"})
    pipeline = orchestrator._state_manager.get_pipeline(pipeline_id)
    assert pipeline["pipeline_id"] == pipeline_id  # 必须一致
```

---

## Finding 3: 统一节点执行器 [P1]

### 核心问题
```python
# node_execution/executor.py 和 nodes/dual_agent.py 各有一套
# 配置来源还不同！

# executor.py: 使用 load_config()
config = load_config()

# dual_agent.py: 直接读环境变量
api_key = os.environ.get("ANTHROPIC_API_KEY")  # ❌ 不一致
```

### 解决方案
```python
# 删除 dual_agent.py 中的重复代码
# 仅保留 node_execution/executor.py 作为唯一入口

# nodes/dual_agent.py 只保留:
__all__ = ["NodeResult", "create_dual_agent_node"]  # 无 create_node_executor
```

### 关键变更
| 文件 | 变更 | 行数 |
|------|------|------|
| `nodes/dual_agent.py` | 删除 `create_node_executor` | ~-30 |
| `nodes/dual_agent.py` | 删除 `_execute_node` | ~-100 |
| `nodes/dual_agent.py` | 删除 `_get_config` | ~-20 |
| `nodes/dual_agent.py` | 删除 legacy 桥接 (lines 204-249) | ~-45 |

### 测试要点
```python
def test_no_duplicate_executor():
    from autoBMAD.docuswarm.nodes import dual_agent
    assert not hasattr(dual_agent, 'create_node_executor')  # 必须不存在
```

---

## Finding 4: 统一状态模型 [P1]

### 核心问题
```python
# 双轨模型: state_json + 顶层列
# 读写来源不一致

# 写入: 顶层列 + 同步 state_json
UPDATE pipelines SET status=?, current_node=?  -- 顶层列
_update_state_json_partial(...)  -- state_json

# 读取 get_pipeline: 从 state_json
# 读取 list_pipelines: 从顶层列  # ❌ 可能不一致！
```

### 解决方案
```python
# state_json 作为唯一事实源
# 顶层列只保留: pipeline_id, subject, created_at, updated_at

def update_pipeline_status(self, pipeline_id, status, current_node=None):
    # 只更新 state_json
    state = json.loads(row["state_json"])
    state["status"] = status
    state["current_node"] = current_node
    UPDATE pipelines SET state_json = ?  # ✅ 唯一来源
```

### 关键变更
| 文件 | 变更 | 行数 |
|------|------|------|
| `storage/state_manager.py` | 导入 `create_initial_state` | ~+1 |
| `storage/state_manager.py` | 删除 `_create_initial_state` | ~-30 |
| `storage/state_manager.py` | 修改 `update_pipeline_status` | ~-10 |
| `storage/state_manager.py` | 删除 `_verify_state_consistency` | ~-40 |

### 测试要点
```python
def test_list_and_get_return_consistent_data():
    list_result = state_manager.list_pipelines()
    get_result = state_manager.get_pipeline(pipeline_id)
    assert list_result[0]["status"] == get_result["status"]  # 必须一致
```

---

## Finding 5: 依赖清理 [P1]

### 核心问题
```python
# 未声明依赖
from kaos.path import KaosPath  # ❌ pyproject.toml 未声明

# 命名不一致
KimiSessionManager = SessionManager  # ❌ 别名造成困惑

# 残留 SDK
import kimi_agent_sdk  # ❌ 应已移除
```

### 解决方案
```python
# 标准库替代
from pathlib import Path  # ✅ 标准库

# 删除别名
# 删除: KimiSessionManager = SessionManager

# 统一使用
session_manager: SessionManager  # ✅ 统一名称
```

### 关键变更
| 文件 | 变更 | 行数 |
|------|------|------|
| `pipeline/orchestrator.py` | 替换 `kaos.path` 导入 | ~-1/+1 |
| `llm/session_manager.py` | 删除 `KimiSessionManager` 别名 | ~-1 |
| `llm/approval.py` | 移除 `kimi_agent_sdk` 导入 | ~-1 |
| 多个文件 | 替换 `KimiSessionManager` 为 `SessionManager` | ~-20 |
| `pyproject.toml` | 更新依赖声明 | ~-2 |

### 验证命令
```bash
# 验证无残留
grep -r "from kaos.path" autoBMAD/ || echo "✅ PASS"
grep -r "kimi_agent_sdk" autoBMAD/ || echo "✅ PASS"
grep -r "KimiSessionManager" autoBMAD/ || echo "✅ PASS"
```

---

## TDD 工作流程速记

```
┌─────────────────────────────────────────┐
│  1. RED: 编写失败的测试                  │
│     └── pytest test_xxx.py -v  # 失败   │
│                                         │
│  2. GREEN: 编写最简单的实现代码          │
│     └── pytest test_xxx.py -v  # 通过   │
│                                         │
│  3. REFACTOR: 清理代码                   │
│     └── pytest test_xxx.py -v  # 仍通过 │
└─────────────────────────────────────────┘
```

---

## 命令速查

### 运行测试
```bash
# 单个 Finding 测试
pytest tests/unit/docuswarm/context/test_validator_finding1.py -v
pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py -v
pytest tests/unit/docuswarm/nodes/test_no_duplicate_executor.py -v
pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py -v
pytest tests/unit/test_finding5_dependency_cleanup.py -v

# 所有 TDD 测试
pytest tests/unit/test_*finding*.py -v

# 集成测试
pytest tests/integration/test_findings_1_to_5_integration.py -v

# 覆盖率
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=html
```

### 代码检查
```bash
# 统计代码行数
wc -l autoBMAD/docuswarm/nodes/dual_agent.py

# 查找残留
find autoBMAD/ -name "*.py" -exec grep -l "KimiSessionManager" {} \;
find autoBMAD/ -name "*.py" -exec grep -l "kaos.path" {} \;
find autoBMAD/ -name "*.py" -exec grep -l "kimi_agent_sdk" {} \;
```

---

## 验收标准速查

| Finding | 核心验收点 | 验证命令 |
|---------|-----------|---------|
| F1 | `HybridOrchestrator()` 可直接 `start_pipeline()` | `pytest test_orchestrator_finding1.py::TestOrchestratorStartup -v` |
| F2 | `start_pipeline` 无 `pipeline_id` 参数 | `pytest test_orchestrator_finding2.py::TestPipelineIdParameter -v` |
| F3 | `dual_agent` 无 `create_node_executor` | `pytest test_no_duplicate_executor.py -v` |
| F4 | `list_pipelines` 和 `get_pipeline` 一致 | `pytest test_state_manager_finding4.py::TestStateJsonIsSingleSourceOfTruth -v` |
| F5 | 无 `kaos.path`/`kimi_agent_sdk` | `grep -r "kaos.path" autoBMAD/ \|\| echo PASS` |

---

## 紧急联系

- **阻塞问题**: 记录到检查清单问题跟踪表
- **代码审查**: 创建 PR 并 @ 指定审查人
- **回滚**: `git revert <commit>`
