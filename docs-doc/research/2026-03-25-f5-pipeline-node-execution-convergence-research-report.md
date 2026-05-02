# F5: Pipeline 与 Node Execution 双主干语义收敛研究报告

> 研究日期: 2026-03-25  
> 研究目标: 分析 `pipeline` 与 `node_execution` 并行承载主语义的问题，并提出收敛方案  
> 报告状态: 深度研究完成，待实施

---

## 执行摘要

`docuswarm` 当前存在两个并行的执行骨架：

1. **`pipeline` 模块 (3120 LOC)**: 负责完整的流水线编排，包含 LangGraph StateGraph 定义、状态管理、checkpoints、orchestrator
2. **`node_execution` 模块 (2255 LOC)**: 负责单个节点的执行，包含节点级 StateGraph、执行器、流控制

这种双主干架构导致了以下核心问题：

| 问题类别 | 严重程度 | 影响 |
|---------|---------|------|
| 语义重叠 | P1 | 同名概念分散在两个模块，认知成本高 |
| Silent Fallback | P0 | 缺少 `session_manager` 时静默降级到 deprecated executor |
| 边界违规 | P0 | Synthetic pipeline_id 创建绕过 PipelineAdapter |
| 未使用的边界层 | P1 | PipelineAdapter 存在但未被使用 |
| 状态转换责任不清 | P1 | 双向转换都集中在 pipeline 模块 |

本报告提供详细的根因分析、建议方案和分阶段实施路径。

---

## 1. 问题根因分析

### 1.1 语义重叠矩阵

通过静态代码分析，识别出以下核心概念在两边都有实现：

```
┌─────────────────┬──────────────────────────┬─────────────────────────────┬────────────┐
│ 概念            │ Pipeline 模块            │ Node Execution 模块          │ 重叠类型   │
├─────────────────┼──────────────────────────┼─────────────────────────────┼────────────┤
│ graph           │ graph.py, orchestrator   │ graph.py                    │ similar    │
│ state           │ state.py, graph.py       │ state.py, executor.py        │ similar    │
│ metrics         │ metrics.py               │ metrics.py                  │ similar    │
│ escalation      │ escalation.py            │ escalation.py               │ identical  │
│ executor        │ graph.py (wrapper)       │ executor.py, flow.py         │ similar    │
│ checkpoint      │ orchestrator.py          │ graph.py                     │ similar    │
└─────────────────┴──────────────────────────┴─────────────────────────────┴────────────┘
```

**关键发现**: `escalation.py` 在两边使用完全相同的文件名，极易造成混淆。

### 1.2 Fallback 路径详细分析

#### 1.2.1 create_pipeline_graph 的执行路径分叉

```python
# pipeline/graph.py:471-491 (简化)
def create_pipeline_graph(..., session_manager: Any | None = None):
    use_integrated = session_manager is not None  # 运行时决定
    
    for node_id in PIPELINE_NODES:
        if use_integrated:
            node_executor = _create_integrated_node_executor(node_id, session_manager)
        else:
            node_executor = _create_default_node_executor(node_id)  # Deprecated!
```

**问题**:
- 运行时根据 `session_manager` 是否存在决定执行路径
- 没有强制要求 `session_manager`，允许静默降级
- 降级路径使用 `_create_default_node_executor`，该函数已被标记为 deprecated

#### 1.2.2 Deprecated Default Executor

```python
# pipeline/graph.py:55-158

def _create_default_node_executor(node_id: str, ...):
    """
    .. deprecated::
        This function is deprecated and will be removed in a future release.
        It produces empty {} deliverables and should not be used in production.
        
        Deprecation Timeline:
        - Deprecated: Story 11.6 (Feb 2026)
        - Removal Target: 2 sprint cycles from deprecation date
    """
    warnings.warn(
        "WARNING: Using deprecated default node executor...",
        DeprecationWarning,
        stacklevel=2,
    )
    ...
```

**问题**:
- 虽然有 `warnings.warn`，但仍然允许继续执行
- 产生空的 deliverables `{}`，导致下游处理异常
- 已经超出 Removal Target（Feb 2026 + 2 sprints）

### 1.3 边界违规详细分析

#### 1.3.1 Synthetic Pipeline ID 创建散落

```python
# node_execution/flow.py:289-290
# 违规: 直接拼接 synthetic pipeline_id
pipeline_id = f"node-{node_id}-{run_id}"

# node_execution/flow.py:364-365
# 违规: 直接拼接 run-level synthetic pipeline_id
pipeline_id = f"node-run-{run_id}"
```

**设计意图 vs 实际现状**:

```
设计意图 (PipelineAdapter 作为唯一边界):
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ Node Execution  │ ───> │  PipelineAdapter │ ───> │    Pipeline     │
│   (flow.py)     │      │ (synthetic ID    │      │  (StateManager) │
│                 │      │  conversion)     │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘

实际现状 (直接访问):
┌─────────────────┐                              ┌─────────────────┐
│ Node Execution  │ ───────────────────────────> │    Pipeline     │
│   (flow.py)     │   f"node-{node_id}-{run_id}" │  (StateManager) │
│                 │   (绕过 Adapter)              │                 │
└─────────────────┘                              └─────────────────┘
```

#### 1.3.2 PipelineAdapter 健康状态

通过代码分析发现：

1. **Adapter 存在**: `node_execution/pipeline_adapter.py` 明确定义了 6 个方法
2. **零使用率**: 没有任何代码通过 `PipelineAdapter.xxx()` 调用这些方法
3. **重复实现**: flow.py 中直接实现了本应通过 Adapter 调用的逻辑

### 1.4 状态转换责任分析

```
当前状态转换路径:

PipelineState ────────────────────────────────────────────────> NodeRunState
    │                                                               │
    │  pipeline/graph.py:_convert_pipeline_to_node_state            │
    │  (单向转换在 pipeline 模块)                                    │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘
                            NodeRunState ────────────────────────> PipelineState
                                │
                                │  pipeline/graph.py:_convert_node_to_pipeline_state
                                │  (反向转换也在 pipeline 模块!)
                                │
                                │  node_execution/pipeline_adapter.py:adapt_state
                                │  (定义但未被使用)
                                │
```

**问题**: 状态转换的责任集中在 `pipeline` 模块，而 `node_execution` 模块作为数据生产者却依赖消费者进行格式转换，违反了关注点分离原则。

---

## 2. 建议方案

### 2.1 核心原则

1. **单一主干**: `pipeline` 负责业务编排，`node_execution` 负责节点执行
2. **唯一边界**: `PipelineAdapter` 是两个模块之间的唯一合法边界
3. **硬失败**: 移除所有 deprecated fallback，不再允许静默兜底

### 2.2 架构目标

```
目标架构:

┌─────────────────────────────────────────────────────────────────────┐
│                           CLI / API 层                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      HybridOrchestrator                             │
│                    (pipeline/orchestrator.py)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Resume     │  │   Cancel     │  │   Restart    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ session_manager (required)
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     create_pipeline_graph                           │
│                       (pipeline/graph.py)                            │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              _create_integrated_node_executor                │   │
│  │                     (唯一执行路径)                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ PipelineState <-> NodeRunState 转换
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PipelineAdapter (唯一边界)                        │
│              (node_execution/pipeline_adapter.py)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ create_pipeline │  │  adapt_state    │  │ parse/is_synthetic  │  │
│  │     _id         │  │                 │  │    _pipeline_id     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Node Execution 层                               │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ node_execution  │  │ node_execution  │  │  node_execution     │  │
│  │   /executor.py  │  │   /flow.py      │  │    /graph.py        │  │
│  │                 │  │                 │  │                     │  │
│  │ create_node_    │  │ execute_node_   │  │ create_node_exec    │  │
│  │ executor()      │  │ flow()          │  │ ution_graph()       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 具体修改清单

#### Phase 1: 硬失败与边界强制 (P0)

1. **移除 Deprecated Default Executor**

```python
# pipeline/graph.py - 修改后

def create_pipeline_graph(
    ...,
    session_manager: KimiSessionManager,  # 移除 Optional，改为必需
) -> Any:
    """
    Args:
        session_manager: KimiSessionManager for integrated node execution.
                        Required - pipeline execution without session_manager
                        is not supported.
    
    Raises:
        ValueError: If session_manager is None.
    """
    if session_manager is None:
        raise ValueError(
            "session_manager is required for pipeline execution. "
            "The deprecated default executor has been removed. "
            "Please provide a valid KimiSessionManager instance."
        )
    
    # 移除 use_integrated 判断，直接使用 integrated executor
    for node_id in PIPELINE_NODES:
        node_executor = _create_integrated_node_executor(node_id, session_manager)
        graph.add_node(node_id, node_executor)
```

2. **强制使用 PipelineAdapter**

```python
# node_execution/flow.py - 修改后

from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

async def execute_node_flow(...):
    # ...
    
    # 替换: pipeline_id = f"node-{node_id}-{run_id}"
    # 为:
    pipeline_id = PipelineAdapter.create_pipeline_id(node_id, run_id)
    
    # ...
    
    # 替换: pipeline_id = f"node-run-{run_id}"
    # 为:
    pipeline_id = PipelineAdapter.create_run_pipeline_id(run_id)
```

3. **删除 _create_default_node_executor 函数**

```python
# pipeline/graph.py - 移除整个函数

# 删除: def _create_default_node_executor(...)  (lines 55-158)
# 删除: def create_enhanced_node_executor(...)  (lines 408-424, 如果存在)
```

#### Phase 2: 职责重新分配 (P1)

1. **将状态转换移至 Adapter**

```python
# node_execution/pipeline_adapter.py - 增强

class PipelineAdapter:
    # ... 现有方法 ...
    
    @staticmethod
    def convert_pipeline_to_node_state(
        pipeline_state: PipelineState,
        node_id: str,
    ) -> dict[str, Any]:
        """
        将 PipelineState 转换为 NodeRunState。
        
        责任转移: 从 pipeline/graph.py 移至此处
        """
        # 迁移 _convert_pipeline_to_node_state 的实现
        ...
    
    @staticmethod
    def convert_node_to_pipeline_state(
        node_state: dict[str, Any],
        original_state: PipelineState,
    ) -> PipelineState:
        """
        将 NodeRunState 转换回 PipelineState。
        
        责任转移: 从 pipeline/graph.py 移至此处
        """
        # 迁移 _convert_node_to_pipeline_state 的实现
        ...
```

2. **更新 graph.py 使用 Adapter**

```python
# pipeline/graph.py - 修改后

from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

def _create_integrated_node_executor(node_id: str, session_manager: Any):
    # ...
    def executor(state: dict[str, Any]) -> dict[str, Any]:
        # 替换直接转换，使用 Adapter
        node_run_state = PipelineAdapter.convert_pipeline_to_node_state(
            new_state, node_id
        )
        executed_node_state = _run_async(async_node_executor(node_run_state))
        new_state = PipelineAdapter.convert_node_to_pipeline_state(
            executed_node_state, new_state
        )
        # ...
```

#### Phase 3: 清理与统一 (P1)

1. **重命名冲突文件**

```
node_execution/escalation.py -> node_execution/node_escalation.py
# 或合并到 pipeline/escalation.py，通过 Adapter 暴露
```

2. **统一 metrics 模块（采用方案C）**

    通过 `PipelineAdapter` 提供统一的 metrics 接口，解决两个同名 `MetricsCollector` 类 API 不兼容的问题。

    ```python
    # node_execution/pipeline_adapter.py - 新增统一 metrics 接口

    from autoBMAD.docuswarm.pipeline.metrics import (
        MetricsCollector as PipelineMetricsCollector,
        NodeMetrics,
        PipelineMetrics,
    )
    from autoBMAD.docuswarm.node_execution.metrics import (
        MetricsCollector as NodeMetricsCollector,
        NodeRunMetrics,
    )

    class PipelineAdapter:
        # ... 现有方法 ...

        class MetricsCollector:
            """统一的 metrics 收集器，兼容 pipeline 和 node_execution 两种模式。

            对外暴露一致的 API，内部根据上下文自动选择存储后端：
            - Pipeline 执行模式：使用内存统计（pipeline/metrics.py）
            - 独立节点模式：使用 SQLite 持久化（node_execution/metrics.py）

            解决了两个同名类 API 不兼容的问题：
            - pipeline: record_node_completion(pipeline_id=..., final_score=..., verdict=...)
            - node_execution: record_node_completion(run_id=..., evaluation={...})
            """

            def __init__(
                self,
                mode: Literal["pipeline", "node_execution"] = "pipeline",
                db_path: str | None = None,
            ) -> None:
                """Initialize unified metrics collector.

                Args:
                    mode: Execution mode - "pipeline" for in-memory, "node_execution" for persistent
                    db_path: Database path for node_execution mode (defaults to "docuswarm.db")
                """
                self._mode = mode
                if mode == "pipeline":
                    self._collector = PipelineMetricsCollector()
                else:
                    self._collector = NodeMetricsCollector(db_path=db_path)

            def record_node_completion(
                self,
                pipeline_id: str,
                node_id: str,
                final_score: float,
                iterations: int,
                verdict: str,
                force_completed: bool = False,
                run_id: str | None = None,
            ) -> None:
                """Record node completion metrics with unified API.

                Args:
                    pipeline_id: Pipeline identifier (used in both modes)
                    node_id: Node identifier
                    final_score: Final alignment score (0.0 to 1.0)
                    iterations: Number of iterations executed
                    verdict: Final verdict (APPROVED, FORCE_APPROVED, BLOCKED, NEEDS_REVISION)
                    force_completed: Whether the node was force completed
                    run_id: Optional run identifier for node_execution mode tracking
                """
                if self._mode == "pipeline":
                    self._collector.record_node_completion(
                        pipeline_id=pipeline_id,
                        node_id=node_id,
                        final_score=final_score,
                        iterations=iterations,
                        verdict=verdict,
                        force_completed=force_completed,
                    )
                else:
                    # node_execution mode: adapt to its API
                    self._collector.record_node_completion(
                        run_id=run_id or pipeline_id,  # fallback to pipeline_id
                        node_id=node_id,
                        evaluation={
                            "alignment_score": final_score,
                            "verdict": verdict,
                        },
                        iterations=iterations,
                        force_completed=force_completed,
                    )

            def finalize_pipeline(self, pipeline_id: str, completion_status: str) -> None:
                """Finalize pipeline metrics (pipeline mode only).

                Args:
                    pipeline_id: Pipeline identifier
                    completion_status: Final status (passed, failed, blocked)

                Raises:
                    RuntimeError: If called in node_execution mode
                """
                if self._mode == "pipeline":
                    self._collector.finalize_pipeline(pipeline_id, completion_status)
                else:
                    raise RuntimeError(
                        "finalize_pipeline() is only available in pipeline mode. "
                        "Use generate_report() for node_execution mode."
                    )

            def generate_report(
                self,
                pipeline_id: str | None = None,
                run_id: str | None = None,
            ) -> dict[str, Any]:
                """Generate quality report.

                Args:
                    pipeline_id: Pipeline identifier (required for pipeline mode)
                    run_id: Run identifier (required for node_execution mode)

                Returns:
                    Quality report dictionary
                """
                if self._mode == "pipeline":
                    return self._collector.generate_report(pipeline_id or "")
                else:
                    return self._collector.generate_report(run_id or pipeline_id or "")

            def generate_node_aggregate_report(self, node_id: str) -> dict[str, Any]:
                """Generate aggregate report for a node (node_execution mode only).

                Args:
                    node_id: Node identifier

                Returns:
                    Aggregate statistics dictionary

                Raises:
                    RuntimeError: If called in pipeline mode
                """
                if self._mode == "node_execution":
                    return self._collector.generate_node_aggregate_report(node_id)
                else:
                    raise RuntimeError(
                        "generate_node_aggregate_report() is only available in "
                        "node_execution mode with database persistence."
                    )

            def list_node_runs(
                self, node_id: str, limit: int = 10
            ) -> list[dict[str, Any]]:
                """List recent runs for a node (node_execution mode only).

                Args:
                    node_id: Node identifier
                    limit: Maximum number of runs to return

                Returns:
                    List of run dictionaries

                Raises:
                    RuntimeError: If called in pipeline mode
                """
                if self._mode == "node_execution":
                    return self._collector.list_node_runs(node_id, limit)
                else:
                    raise RuntimeError(
                        "list_node_runs() is only available in node_execution mode."
                    )
    ```

    **迁移 dual_agent.py 使用统一接口：**

    ```python
    # nodes/dual_agent.py - 修改导入

    # 替换:
    # from autoBMAD.docuswarm.pipeline.metrics import MetricsCollector
    # 为:
    from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

    MetricsCollector = PipelineAdapter.MetricsCollector  # 别名保持兼容性

    # 调用代码无需修改，API 保持一致：
    # self.metrics_collector.record_node_completion(
    #     pipeline_id=pipeline_id,
    #     node_id=self.node_id,
    #     final_score=alignment_score,
    #     iterations=iteration,
    #     verdict=verdict,
    #     force_completed=False,
    # )
    ```

    **方案C优势：**
    1. **API 统一**：对外暴露一致的 `record_node_completion(pipeline_id=..., final_score=..., verdict=...)` 接口
    2. **向后兼容**：通过别名 `MetricsCollector = PipelineAdapter.MetricsCollector` 保持现有代码不变
    3. **职责清晰**：pipeline 模式专注实时统计，node_execution 模式专注历史追踪
    4. **类型安全**：IDE 和类型检查器可以正确识别统一接口
3. **清理未使用的导入和代码**

```python
# 删除所有对 _create_default_node_executor 的引用
# 删除 create_enhanced_node_executor (如果存在)
# 更新 __all__ 列表
```

---

## 3. 实施路径

### 3.1 Phase 1: 止血 (1 周)

**目标**: 停止继续扩散过渡态，强制唯一执行路径

| 任务 | 优先级 | 影响文件 | 验证方式 |
|-----|--------|---------|---------|
| 移除 `session_manager` 的可空性 | P0 | `pipeline/graph.py` | 调用 `create_pipeline_graph()` 不传 `session_manager` 时抛出 `ValueError` |
| 删除 `_create_default_node_executor` | P0 | `pipeline/graph.py` | 代码搜索无该函数定义 |
| 强制使用 `PipelineAdapter` | P0 | `node_execution/flow.py` | 代码搜索无 `f"node-{` 直接拼接 |
| 更新调用点 | P0 | `pipeline/orchestrator.py`, `cli/services/*.py` | 所有调用都传递 `session_manager` |

**风险**: 
- 可能有测试代码依赖 deprecated executor
- 需要同步更新所有调用点

**缓解**:
- 先修改代码抛出异常，运行测试看哪些失败
- 逐个修复测试或调用点

### 3.2 Phase 2: 边界巩固 (1 周)

**目标**: 让 `PipelineAdapter` 成为真正的唯一边界

| 任务 | 优先级 | 影响文件 | 验证方式 |
|-----|--------|---------|---------|
| 迁移状态转换函数到 Adapter | P1 | `node_execution/pipeline_adapter.py` | 单元测试通过 |
| 更新 `graph.py` 使用 Adapter | P1 | `pipeline/graph.py` | 集成测试通过 |
| 添加 Adapter 使用检查工具 | P1 | 新增 CI 检查 | PR 中禁止直接 synthetic ID 创建 |
| 更新文档 | P1 | `docs/architecture/*.md` | 文档反映新的边界规则 |

### 3.3 Phase 3: 清理债务 (1 周)

**目标**: 删除重复代码，统一命名

| 任务 | 优先级 | 影响文件 | 验证方式 |
|-----|--------|---------|---------|
| 重命名冲突文件 | P2 | `node_execution/escalation.py` | 无同名文件 |
| 统一 metrics | P2 | `pipeline/metrics.py`, `node_execution/metrics.py` | 单点定义 |
| 删除兼容层 | P2 | `pipeline/graph.py` | `__all__` 清理 |
| 添加架构守护测试 | P2 | `tests/architecture/*.py` | 测试禁止回归 |

---

## 4. 验证方案

### 4.1 自动化检查工具

使用已开发的分析工具进行持续监控：

```bash
# 添加到 CI pipeline
python tools/pipeline_node_execution_analyzer.py --mode all --json

# 检查规则:
# 1. 不得有新的 synthetic_id_creation 违规
# 2. 不得有新的 fallback 路径
# 3. PipelineAdapter 方法必须被使用
```

### 4.2 架构守护测试

```python
# tests/architecture/test_boundary_enforcement.py

def test_no_direct_synthetic_id_creation():
    """禁止直接创建 synthetic pipeline_id"""
    violations = analyze_boundary_violations()
    assert len(violations) == 0, f"发现边界违规: {violations}"

def test_pipeline_adapter_is_used():
    """PipelineAdapter 方法必须被实际使用"""
    usage = analyze_pipeline_adapter()
    assert len(usage.get("unused_methods", [])) == 0, "存在未使用的 Adapter 方法"

def test_no_deprecated_executor_fallback():
    """禁止 fallback 到 deprecated executor"""
    content = (Path(__file__).parents[2] / "pipeline" / "graph.py").read_text()
    assert "_create_default_node_executor" not in content
    assert "falling_back_to_default_executor" not in content
```

### 4.3 集成验证

```bash
# 完整流水线测试
pytest tests/integration/test_pipeline_execution.py -v

# 边界场景测试
pytest tests/integration/test_session_manager_required.py -v

# 恢复能力测试
pytest tests/integration/test_resume_restart.py -v
```

---

## 5. 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|-----|--------|------|---------|
| 测试覆盖率不足导致回归 | 中 | 高 | 先运行全量测试，修复失败项再合并 |
| 外部调用点未同步更新 | 中 | 高 | 全局搜索所有 `create_pipeline_graph` 调用 |
| 性能下降 | 低 | 中 | 基准测试对比，Adapter 开销可忽略 |
| 团队适应成本 | 中 | 低 | 文档更新，架构评审 |

---

## 6. 度量指标

建议每周跟踪以下指标：

| 指标 | 当前值 | 目标值 | 测量方式 |
|-----|--------|--------|---------|
| Synthetic ID 边界违规数 | 4 | 0 | `pipeline_node_execution_analyzer.py` |
| Deprecated fallback 路径数 | 4 | 0 | 同上 |
| PipelineAdapter 方法使用率 | 0% | 100% | 同上 |
| 语义重叠文件对数 | 6 | 2 | 静态分析 |
| `session_manager` 必填率 | 0% | 100% | 代码审查 |

---

## 7. 附录

### 7.1 相关文件清单

**Pipeline 模块**:
- `autoBMAD/docuswarm/pipeline/graph.py` (核心修改点)
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `autoBMAD/docuswarm/pipeline/state.py`
- `autoBMAD/docuswarm/pipeline/escalation.py`
- `autoBMAD/docuswarm/pipeline/metrics.py`

**Node Execution 模块**:
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` (边界层)
- `autoBMAD/docuswarm/node_execution/flow.py` (违规点)
- `autoBMAD/docuswarm/node_execution/executor.py`
- `autoBMAD/docuswarm/node_execution/graph.py`
- `autoBMAD/docuswarm/node_execution/escalation.py` (冲突)
- `autoBMAD/docuswarm/node_execution/metrics.py` (冲突)

### 7.2 参考文档

- 评估报告: `docs/evaluation/2026-03-25-docuswarm-deep-evaluation-report.md`
- 本分析原始数据: `docs/research/f5_pipeline_node_execution_analysis_report.json`
- 分析工具: `tools/pipeline_node_execution_analyzer.py`

### 7.3 决策记录

**决策**: 选择强制 `session_manager` 必填而非保持可空

**理由**:
1. Deprecated executor 已经超出 removal target
2. Silent fallback 导致空 deliverables，更难调试
3. 强制失败可以在开发阶段发现问题，而非生产环境

**替代方案考虑**:
- 保持可空但增加更强烈的告警: 拒绝，因为问题被推迟而非解决
- 自动创建默认 session_manager: 拒绝，因为隐藏了依赖关系

---

*报告生成时间: 2026-03-25*  
*下次评审时间: Phase 1 完成后*
