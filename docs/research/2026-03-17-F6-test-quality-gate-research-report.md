# F6: 测试体系质量门深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm 测试体系
> 核心问题: 测试体系不能再把历史红灯直接当作当前质量门

---

## 1. 执行摘要

### 1.1 核心发现

当前工作区存在**测试真空**状态：

1. **当前工作区可见测试文件数: 0**
2. **历史测试已清理并重建**
3. **无法使用仓内旧测试直接证明当前回归状态**

这意味着需要建立全新的测试体系，而非修复旧测试。

### 1.2 关键数据

| 指标 | 数值 | 说明 |
|------|------|------|
| pipelines 条数 | 51 | 数据库中存在 |
| checkpoints 条数 | 128 | 历史运行记录 |
| 当前工作区测试文件 | 0 | 需要重建 |
| 历史红灯 | N/A | 不应作为当前质量门 |

---

## 2. 详细分析

### 2.1 测试体系现状

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          测试体系现状                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  当前状态: 测试真空                                                       │
│                                                                         │
│  tests/ 目录                                                             │
│  ├── (空或不存在)                                                        │
│                                                                         │
│  历史状态: 已清理                                                         │
│  ├── 旧测试基于历史双轨假设（checkpoint 主真相、ToolOk 内部格式等）         │
│  ├── 与当前决策（state_json 主真相、ToolResult 内部格式）不一致           │
│  └── 重建比修复更合理                                                     │
│                                                                         │
│  质量门现状: 失效                                                         │
│  ├── 无法运行回归测试                                                     │
│  ├── 无法验证当前实现正确性                                                │
│  └── 需要建立新的质量门                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 不应复用的历史假设

| 历史假设 | 当前决策 | 冲突 |
|----------|----------|------|
| checkpoint 是主要恢复依据 | state_json 是业务真相源 | ✅ 冲突 |
| ToolOk/ToolError 是内部格式 | ToolResult 是内部格式 | ✅ 冲突 |
| docs 工具存在 | docs-free | ✅ 冲突 |
| 双轨状态管理 | 单一真相源 | ✅ 冲突 |

### 2.3 新的质量门需求

基于 F1-F5 的决策，测试体系需要覆盖：

1. **F1 - 状态持久化**: state_json 写入和恢复测试
2. **F2 - shared_context**: 端到端链路测试
3. **F3 - Evaluator 契约**: Prompt 内容快照测试
4. **F4 - 工具收敛**: docs-free 工具导出测试
5. **F5 - ToolResult 协议**: 工具返回格式一致性测试

---

## 3. 收敛方案

### 3.1 测试体系重建原则

1. **围绕当前有效决策**: 只测试当前生效的架构决策
2. **分层测试**: 契约测试、集成测试、端到端测试分层
3. **环境敏感隔离**: 环境依赖测试与核心契约测试分离
4. **契约优先**: 优先补齐契约测试，而非历史兼容测试

### 3.2 测试金字塔

```
                    ┌─────────┐
                    │  E2E   │  ← 关键流程端到端 (少量)
                    │  测试  │
                   ┌┴─────────┴┐
                   │  集成测试  │  ← 组件协作 (适量)
                   │ (API/DB) │
                  ┌┴───────────┴┐
                  │   契约测试   │  ← 数据结构/Prompt (大量)
                  │  (快照/单元) │
                 ┌┴─────────────┴┐
                 │    单元测试    │  ← 纯函数/工具 (大量)
                 └───────────────┘
```

### 3.3 具体测试规划

#### 3.3.1 契约测试（最高优先级）

```python
# tests/contracts/test_state_contracts.py
"""F1: 状态持久化契约测试"""

def test_pipeline_state_schema():
    """验证 PipelineState 包含所有必需字段."""
    from autoBMAD.docuswarm.pipeline.state import PipelineState
    
    required_fields = [
        "pipeline_id", "subject_context", "current_node",
        "completed_nodes", "deliverables", "questions",
        "evaluations", "node_iterations", "session_ids",
        "session_metadata", "current_node_session_id",
        "status", "error", "shared_context",
    ]
    
    for field in required_fields:
        assert field in PipelineState.__annotations__, f"Missing: {field}"

def test_state_json_completeness():
    """验证 state_json 包含完整 PipelineState."""
    # 创建 pipeline 并验证 state_json 字段
    pass

# tests/contracts/test_shared_context_contracts.py
"""F2: shared_context 契约测试"""

def test_shared_context_propagation():
    """验证 shared_context 从写入到消费的链路."""
    pass

def test_shared_context_persistence():
    """验证 resume 后 shared_context 仍然可用."""
    pass

# tests/contracts/test_evaluator_contracts.py
"""F3: Evaluator 输入契约测试"""

def test_evaluator_prompt_contains_original_context(snapshot):
    """验证 Evaluator prompt 包含原始上下文（快照测试）."""
    pass

def test_evaluator_agent_input_completeness():
    """验证 EvaluatorAgentInput 字段都有消费点."""
    pass

# tests/contracts/test_tools_contracts.py
"""F4: 工具层契约测试"""

def test_docs_free_tool_exports():
    """验证只导出 docs-free 工具."""
    from autoBMAD.docuswarm import tools
    
    expected = {"CreateDeliverableTool", "CreateDocumentSetTool", "UpdateContextTool"}
    actual = {name for name in tools.__all__ if not name.endswith("Params")}
    
    assert actual == expected

# tests/contracts/test_toolresult_contracts.py
"""F5: ToolResult 协议契约测试"""

def test_all_tools_return_toolresult():
    """验证所有工具内部返回 ToolResult."""
    pass
```

#### 3.3.2 集成测试

```python
# tests/integration/test_state_persistence.py
"""F1: 状态持久化集成测试"""

import pytest

@pytest.mark.asyncio
async def test_pipeline_create_and_restore(db_connection):
    """验证 pipeline 创建和从 state_json 恢复."""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    
    sm = StateManager(db_path=db_connection)
    
    # 创建
    pipeline_id = sm.create_pipeline(
        subject="Test",
        subject_context={"task": "test task"},
    )
    
    # 更新状态
    await sm.update_pipeline_state(pipeline_id, {
        "current_node": "analyst",
        "completed_nodes": ["analyst"],
        "deliverables": {"analyst": {"title": "Analysis"}},
    })
    
    # 读取并验证
    pipeline = sm.get_pipeline(pipeline_id)
    state = pipeline["state"]
    
    assert state["current_node"] == "analyst"
    assert "analyst" in state["completed_nodes"]

# tests/integration/test_shared_context_integration.py
"""F2: shared_context 集成测试"""

@pytest.mark.asyncio
async def test_shared_context_end_to_end(orchestrator, db_connection):
    """验证 shared_context 端到端链路."""
    # 1. 创建 pipeline
    # 2. 写入 shared_context
    # 3. 验证下一个节点能看到
    pass

# tests/integration/test_evaluator_integration.py
"""F3: Evaluator 集成测试"""

@pytest.mark.asyncio
async def test_evaluator_with_original_context():
    """验证 Evaluator 评审时考虑原始上下文."""
    pass
```

#### 3.3.3 端到端测试

```python
# tests/e2e/test_full_pipeline.py
"""完整管道端到端测试"""

import pytest

@pytest.mark.asyncio
@pytest.mark.slow
async def test_full_pipeline_execution():
    """验证完整 pipeline 执行（简化版）."""
    # 使用 mock LLM 或快速模式
    pass

@pytest.mark.asyncio
@pytest.mark.slow
async def test_pipeline_resume():
    """验证 pipeline 暂停和恢复."""
    pass
```

### 3.4 测试分层策略

| 层级 | 范围 | 数量 | 运行时机 | 示例 |
|------|------|------|----------|------|
| 单元 | 纯函数、工具 | 大量 | 每次提交 | `test_slugify_filename` |
| 契约 | 数据结构、Prompt | 大量 | 每次提交 | `test_pipeline_state_schema` |
| 集成 | 组件协作 | 适量 | PR 前 | `test_pipeline_create_and_restore` |
| E2E | 完整流程 | 少量 | CI/发布 | `test_full_pipeline_execution` |

### 3.5 环境敏感测试隔离

```python
# tests/conftest.py

import pytest

@pytest.fixture
def mock_llm():
    """Mock LLM 用于不依赖外部服务的测试."""
    pass

@pytest.fixture
def in_memory_db():
    """内存数据库用于快速测试."""
    pass

@pytest.fixture
def isolated_output_dir(tmp_path):
    """隔离的输出目录."""
    pass

# 标记环境敏感测试
@pytest.mark.requires_llm
async def test_with_real_llm():
    """需要真实 LLM 的测试."""
    pass

@pytest.mark.requires_filesystem
async def test_file_operations():
    """需要文件系统的测试."""
    pass
```

---

## 4. 测试建议（实施顺序）

### 4.1 第一阶段：契约测试（立即开始）

1. **状态契约**: PipelineState schema 完整性
2. **工具契约**: docs-free 导出、ToolResult 返回
3. **Context 契约**: shared_context、Evaluator 输入

### 4.2 第二阶段：集成测试

1. **StateManager 集成**: 数据库读写
2. **Context 集成**: shared_context 端到端
3. **Agent 集成**: Prompt 构建

### 4.3 第三阶段：E2E 测试

1. **完整流程**: Mock LLM 下的 pipeline 执行
2. **恢复场景**: pause/resume/restart

---

## 5. 质量门定义

### 5.1 提交前检查

```bash
# 本地提交前运行
pytest tests/unit tests/contracts -v --tb=short
basedpyright autoBMAD/docuswarm/
ruff check autoBMAD/docuswarm/
```

### 5.2 PR 前检查

```bash
# PR 前运行
pytest tests/ -v --tb=short --ignore=tests/e2e
# 包含单元、契约、集成测试
```

### 5.3 CI 检查

```bash
# CI 运行全部测试
pytest tests/ -v --tb=short
# 包含 E2E 测试
```

---

## 6. 结论

1. **历史测试不应复用**，基于旧架构决策
2. **当前是测试真空状态**，需要重建测试体系
3. **优先补齐契约测试**，确保 F1-F5 决策被正确实现
4. **分层测试策略**：契约 → 集成 → E2E
5. **环境敏感测试隔离**，避免噪音和真实回归混在一起

---

## 附录: 测试文件结构

```
tests/
├── conftest.py                      # 共享 fixtures
├── unit/                            # 单元测试
│   ├── test_tool_result.py
│   ├── test_state_manager_utils.py
│   └── ...
├── contracts/                       # 契约测试
│   ├── test_state_contracts.py      # F1
│   ├── test_shared_context_contracts.py  # F2
│   ├── test_evaluator_contracts.py  # F3
│   ├── test_tools_contracts.py      # F4
│   └── test_toolresult_contracts.py # F5
├── integration/                     # 集成测试
│   ├── test_state_persistence.py    # F1
│   ├── test_shared_context_integration.py  # F2
│   ├── test_evaluator_integration.py  # F3
│   └── ...
└── e2e/                             # 端到端测试
    └── test_full_pipeline.py
```
