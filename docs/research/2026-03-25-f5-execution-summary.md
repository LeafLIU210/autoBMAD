# F5 研究执行摘要

> 日期: 2026-03-25  
> 研究目标: Pipeline 与 Node Execution 双主干语义收敛  
> 状态: 研究完成，待实施

---

## 研究成果概览

本次研究针对评估报告 F5 项（`pipeline` 与 `node_execution` 仍在并行承载主语义）进行了深度分析，产出如下成果：

| 产出物 | 路径 | 说明 |
|-------|------|------|
| 深度研究报告 | `docs/research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md` | 根因分析、现状诊断、建议方案 |
| 设计规范 | `docs/research/2026-03-25-f5-unified-design-spec.md` | 详细接口规范、代码示例、迁移清单 |
| 分析工具 | `tools/pipeline_node_execution_analyzer.py` | 静态分析工具，检测语义重叠、fallback 路径、边界违规 |
| 迁移脚本 | `tools/migrate_f5_convergence.py` | 迁移检查工具，识别需修改的代码位置 |
| 分析结果 | `docs/research/f5_pipeline_node_execution_analysis_report.json` | 当前代码库分析原始数据 |

---

## 关键发现

### 1. 语义重叠（6 对）

```
概念           Pipeline 模块                    Node Execution 模块               重叠类型
────────────────────────────────────────────────────────────────────────────────────────────
graph          graph.py, orchestrator.py        graph.py                          similar
state          state.py, graph.py               state.py, executor.py             similar  
metrics        metrics.py                       metrics.py                        similar
escalation     escalation.py                    escalation.py                     identical ⚠️
executor       graph.py                         executor.py, flow.py              similar
checkpoint     graph.py, orchestrator.py        graph.py                          similar
```

**最严重的重叠**: `escalation.py` 两边使用完全相同的文件名，极易混淆。

### 2. Fallback 路径（4 处）

| 位置 | 类型 | 问题 |
|-----|------|------|
| `graph.py:326` | Silent | ThreadPoolExecutor fallback 路径 |
| `graph.py:450` | BackwardCompat | 明确说明使用 deprecated executor |
| `graph.py:472` | Conditional | 运行时根据 session_manager 选择执行路径 |
| `graph.py:481` | Silent | falling_back_to_default_executor 日志 |

### 3. 边界违规（4 处）

```python
# node_execution/flow.py:290 - 直接创建 synthetic ID (违规)
pipeline_id = f"node-{node_id}-{run_id}"

# node_execution/flow.py:365 - 直接创建 run-level synthetic ID (违规)  
pipeline_id = f"node-run-{run_id}"
```

**关键问题**: `PipelineAdapter` 存在但完全未被使用（6 个方法，0 处使用）。

### 4. 状态转换责任不清

- `PipelineState -> NodeRunState`: `pipeline/graph.py` 负责
- `NodeRunState -> PipelineState`: `pipeline/graph.py` 负责
- `PipelineAdapter.adapt_state`: 定义但未被使用

违反关注点分离原则。

---

## 核心建议

### 立即执行（Phase 1 - 1 周）

1. **强制 session_manager 必填**
   - 修改 `create_pipeline_graph()` 签名
   - `session_manager: Any | None = None` → `session_manager: KimiSessionManager`
   - 为 None 时抛出 `ValueError` 而非静默降级

2. **删除 Deprecated Default Executor**
   - 删除 `_create_default_node_executor()` 函数 (lines 55-158)
   - 删除 `create_enhanced_node_executor()` 函数 (lines 408-424)

3. **强制使用 PipelineAdapter**
   - `flow.py` 导入 `PipelineAdapter`
   - 替换所有 `f"node-{...}"` 为 `PipelineAdapter.create_pipeline_id()`

### 边界巩固（Phase 2 - 1 周）

4. **迁移状态转换到 Adapter**
   - `_convert_pipeline_to_node_state` → `PipelineAdapter.convert_pipeline_to_node_state`
   - `_convert_node_to_pipeline_state` → `PipelineAdapter.convert_node_to_pipeline_state`

5. **更新调用点**
   - 修改 `graph.py` 使用 Adapter 方法
   - 更新 `orchestrator.py` 和其他调用者

### 清理债务（Phase 3 - 1 周）

6. **重命名冲突文件**
   - `node_execution/escalation.py` → `node_execution/node_escalation.py`

7. **添加架构守护测试**
   - 创建 `tests/architecture/test_boundary_enforcement.py`
   - 添加 CI 检查

---

## 度量指标

| 指标 | 当前值 | 目标值 |
|-----|--------|--------|
| Deprecated fallback 路径数 | 4 | 0 |
| Synthetic ID 边界违规数 | 4 | 0 |
| PipelineAdapter 方法使用率 | 0% | 100% |
| 语义重叠文件对数 | 6 | 2 |

---

## 工具使用指南

### 1. 运行分析工具

```bash
# 完整分析
python tools/pipeline_node_execution_analyzer.py --mode all

# 仅检查边界违规
python tools/pipeline_node_execution_analyzer.py --mode boundary

# 仅检查 fallback 路径
python tools/pipeline_node_execution_analyzer.py --mode fallback
```

### 2. 运行迁移检查

```bash
# 检查迁移状态
python tools/migrate_f5_convergence.py --check

# 验证迁移完成
python tools/migrate_f5_convergence.py --verify

# 生成补丁建议
python tools/migrate_f5_convergence.py --generate-patch
```

---

## 下一步行动

1. **评审设计规范** (`2026-03-25-f5-unified-design-spec.md`)
2. **批准后开始 Phase 1 实施**
3. **每阶段完成后运行验证工具**
4. **全部完成后更新架构文档**

---

## 参考链接

- 原始评估报告: `docs/evaluation/2026-03-25-docuswarm-deep-evaluation-report.md`
- 深度研究报告: `docs/research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md`
- 设计规范: `docs/research/2026-03-25-f5-unified-design-spec.md`
