# F5 TDD 实施方案 - 执行摘要

> 完整方案: `docs/solution/2026-03-25-f5-test-driven-implementation-plan.md`

---

## 🎯 核心目标

通过 **Test-Driven Development** 完成 F5 双主干语义收敛：

```
Pipeline 模块 (编排) ←── PipelineAdapter ──→ Node Execution 模块 (执行)
                              ↑
                         唯一合法边界
```

---

## 📋 快速开始

### 1. 克隆测试文件模板

```bash
# Phase 1 测试
cp docs/solution/tdd-templates/phase1/* tests/

# Phase 2 测试  
cp docs/solution/tdd-templates/phase2/* tests/

# Phase 3 测试
cp docs/solution/tdd-templates/phase3/* tests/
```

### 2. 运行测试 (Red Phase)

```bash
# 所有测试应该失败 (这是正确的！)
pytest tests/pipeline/test_create_pipeline_graph_signature.py -v
pytest tests/pipeline/test_no_deprecated_executor.py -v
pytest tests/architecture/test_pipeline_adapter_usage.py -v
```

### 3. 实现代码 (Green Phase)

按照 `test-driven-implementation-plan.md` 中的 "GREEN" 章节逐步实现。

### 4. 验证 (Refactor Phase)

```bash
# 所有测试应该通过
python tools/migrate_f5_convergence.py --verify
```

---

## 📊 TDD 任务看板

### Phase 1: 硬失败与边界强制 (P0) - 第 1 周

| # | 测试文件 | 目标 | 状态 |
|---|---------|------|------|
| 1.1 | `test_create_pipeline_graph_signature.py` | session_manager 必填 | ⬜ Red |
| 1.2 | `test_no_deprecated_executor.py` | 删除 deprecated 函数 | ⬜ Red |
| 1.3 | `test_pipeline_adapter_usage.py` | 强制使用 Adapter | ⬜ Red |
| 1.4 | `test_phase1_convergence.py` | 集成验证 | ⬜ Red |

### Phase 2: 职责重新分配 (P1) - 第 2 周

| # | 测试文件 | 目标 | 状态 |
|---|---------|------|------|
| 2.1 | `test_pipeline_adapter_state_conversion.py` | 状态转换移至 Adapter | ⬜ Red |
| 2.2 | `test_graph_uses_adapter.py` | graph.py 使用 Adapter | ⬜ Red |

### Phase 3: 清理与统一 (P1) - 第 3 周

| # | 测试文件 | 目标 | 状态 |
|---|---------|------|------|
| 3.1 | `test_no_filename_conflicts.py` | 重命名冲突文件 | ⬜ Red |
| 3.2 | `test_unified_metrics.py` | 统一 metrics 模块 | ⬜ Red |
| 3.3 | `test_architecture_guard.py` | 架构守护测试 | ⬜ Red |

---

## 🔑 关键测试速查

### 测试 1: session_manager 必填

```python
# RED: 这个测试必须先写，应该失败
def test_session_manager_none_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        create_pipeline_graph(session_manager=None)
    
    assert "session_manager is required" in str(exc_info.value)
```

**实现后验证**:
```bash
pytest tests/pipeline/test_create_pipeline_graph_signature.py::TestCreatePipelineGraphSessionManagerRequired::test_session_manager_none_raises_value_error -v
```

### 测试 2: Deprecated 函数已删除

```python
# RED: 这个测试必须先写，应该失败
def test_create_default_node_executor_removed():
    from autoBMAD.docuswarm.pipeline import graph as graph_module
    assert not hasattr(graph_module, '_create_default_node_executor')
```

**实现后验证**:
```bash
pytest tests/pipeline/test_no_deprecated_executor.py::TestNoDeprecatedExecutor::test_create_default_node_executor_removed -v
```

### 测试 3: PipelineAdapter 被使用

```python
# RED: 这个测试必须先写，应该失败
def test_no_direct_node_prefix_fstrings():
    # 扫描代码中不应有 f"node-{...}" 模式
    assert 'f"node-' not in flow_py_content
```

**实现后验证**:
```bash
pytest tests/architecture/test_pipeline_adapter_usage.py::TestPipelineAdapterBoundaryEnforcement::test_no_direct_node_prefix_fstrings -v
```

### 测试 4: 状态转换在 Adapter

```python
# RED: 这个测试必须先写，应该失败
def test_convert_pipeline_to_node_state_exists():
    assert hasattr(PipelineAdapter, 'convert_pipeline_to_node_state')
```

**实现后验证**:
```bash
pytest tests/node_execution/test_pipeline_adapter_state_conversion.py::TestPipelineAdapterStateConversion::test_convert_pipeline_to_node_state_exists -v
```

---

## ⚠️ 常见陷阱

### 陷阱 1: 先实现后补测试

❌ **错误做法**:
```bash
# 先改代码
vim autoBMAD/docuswarm/pipeline/graph.py

# 后补测试 (反 TDD)
vim tests/test_something.py
```

✅ **正确做法**:
```bash
# 先写测试 (Red)
vim tests/test_something.py
pytest tests/test_something.py  # 确认失败

# 后写实现 (Green)
vim autoBMAD/docuswarm/pipeline/graph.py
pytest tests/test_something.py  # 确认通过
```

### 陷阱 2: 测试不够具体

❌ **错误示例**:
```python
def test_it_works():
    result = some_function()
    assert result is not None  # 太笼统
```

✅ **正确示例**:
```python
def test_session_manager_none_raises_value_error_with_specific_message():
    with pytest.raises(ValueError) as exc_info:
        create_pipeline_graph(session_manager=None)
    
    error_message = str(exc_info.value)
    assert "session_manager is required" in error_message  # 具体
    assert "deprecated default executor was removed" in error_message  # 具体
```

### 陷阱 3: 忽略架构测试

❌ **错误做法**: 只测试功能，不测试架构约束

✅ **正确做法**:
```python
# 功能测试 + 架构测试
def test_feature_works(): ...

def test_no_deprecated_imports_in_codebase():  # 架构测试
    violations = scan_for_deprecated_imports()
    assert not violations
```

---

## 🛠️ 工具命令速查

### 运行指定测试

```bash
# 单个测试
pytest tests/pipeline/test_create_pipeline_graph_signature.py::TestCreatePipelineGraphSessionManagerRequired::test_session_manager_none_raises_value_error -v

# 整个测试类
pytest tests/pipeline/test_create_pipeline_graph_signature.py::TestCreatePipelineGraphSessionManagerRequired -v

# 整个文件
pytest tests/pipeline/test_create_pipeline_graph_signature.py -v

# 整个目录
pytest tests/pipeline/ -v
```

### 迁移检查

```bash
# 检查当前状态
python tools/migrate_f5_convergence.py --check

# 验证迁移完成
python tools/migrate_f5_convergence.py --verify

# 生成补丁建议
python tools/migrate_f5_convergence.py --generate-patch
```

### 完整验证

```bash
# Phase 1 完整验证
pytest tests/pipeline/test_create_pipeline_graph_signature.py \\
       tests/pipeline/test_no_deprecated_executor.py \\
       tests/architecture/test_pipeline_adapter_usage.py \\
       tests/integration/test_phase1_convergence.py -v

# 所有 F5 测试
pytest tests/ -k "pipeline_graph or deprecated_executor or pipeline_adapter or state_conversion or filename_conflicts" -v
```

---

## 📈 进度追踪

### 每日检查清单

- [ ] 今日编写的测试是否都先运行确认失败？(Red)
- [ ] 实现是否让测试通过？(Green)
- [ ] 是否有重构空间？(Refactor)
- [ ] 是否运行了全量测试确保无回归？
- [ ] 是否更新了迁移检查工具状态？

### 每周里程碑

| 周次 | 目标 | 验证命令 |
|------|------|---------|
| Week 1 | Phase 1 完成 | `pytest tests/pipeline/test_*.py tests/architecture/test_pipeline_adapter_usage.py -v` |
| Week 2 | Phase 2 完成 | `pytest tests/node_execution/test_pipeline_adapter_state_conversion.py -v` |
| Week 3 | Phase 3 完成 | `python tools/migrate_f5_convergence.py --verify` |

---

## 🆘 故障排除

### 问题: 测试通过了但不应该

**可能原因**: 测试描述不清晰，或测试代码有 bug

**解决方案**:
```python
# 添加明确的失败断言验证测试在 Red 阶段确实失败
def test_something():
    # 临时添加，确认测试逻辑正确
    pytest.fail("This test should fail in Red phase")
```

### 问题: 测试总是失败，实现复杂

**可能原因**: 测试太大，需要拆分

**解决方案**: 遵循 AAA 模式 (Arrange, Act, Assert)，每个测试只做一件事

### 问题: 架构测试太慢

**解决方案**: 将架构测试标记为慢测试，CI 运行而非本地每次运行

```python
@pytest.mark.slow  # 自定义标记
def test_no_deprecated_imports_in_codebase():
    ...
```

```bash
# 本地快速测试
pytest tests/ -m "not slow"

# CI 完整测试
pytest tests/
```

---

## 📚 参考资源

| 文档 | 路径 | 用途 |
|------|------|------|
| 完整 TDD 方案 | `docs/solution/2026-03-25-f5-test-driven-implementation-plan.md` | 详细实施步骤 |
| 设计规范 | `docs/research/2026-03-25-f5-unified-design-spec.md` | 接口定义 |
| 研究报告 | `docs/research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md` | 背景分析 |
| 分析工具 | `tools/pipeline_node_execution_analyzer.py` | 静态分析 |
| 迁移检查 | `tools/migrate_f5_convergence.py` | 进度检查 |

---

**Ready to start TDD?** Run the first test now:

```bash
pytest tests/pipeline/test_create_pipeline_graph_signature.py -v
```

Expected: **3 failed** (Red phase - this is correct!)
