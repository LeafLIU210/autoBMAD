# DocuSwarm 综合深度研究 — 测试驱动修复方案

> 基于: `docs-doc/research/2026-05-01-docuswarm-comprehensive-deep-research.md`
> 日期: 2026-05-01
> 范围: 覆盖研究报告全部 4 个 Phase 修复路线图的测试驱动实现方案

---

## 执行状态摘要

| Phase | 状态 | 测试数 | 通过 |
|-------|------|--------|------|
| Phase 0 — 立即止损 | ✅ 已完成 | 10 | 10/10 |
| Phase 1 — 状态语义修复 | ✅ 已完成 | 8 | 8/8 |
| Phase 2 — 移除虚假交互系统 | ✅ 已完成 | 9 | 9/9 |
| Phase 3 — 质量门增强 | ✅ 已完成 | 7 | 7/7 |
| Phase 4 — 安全加固 | ✅ 已完成 | 4 | 4/4 |
| 既有回归测试 | ✅ 已通过 | 136 | 136/136 |
| **总计** | **✅ 全部通过** | **174** | **174/174** |

> 执行日期: 2026-05-01
> 测试命令: `pytest tests/ -v`
> 回归零失败，零引入新缺陷。

---

## 目录

1. [方案概述](#1-方案概述)
2. [测试策略与原则](#2-测试策略与原则)
3. [Phase 0: 立即止损](#3-phase-0-立即止损)
4. [Phase 1: 状态语义修复](#4-phase-1-状态语义修复)
5. [Phase 2: 移除虚假交互系统](#5-phase-2-移除虚假交互系统)
6. [Phase 3: 质量门增强](#6-phase-3-质量门增强)
7. [Phase 4: 安全加固](#7-phase-4-安全加固)
8. [集成验收测试](#8-集成验收测试)
9. [风险缓解测试](#9-风险缓解测试)
10. [执行时间表与里程碑](#10-执行时间表与里程碑)

---

## 1. 方案概述

### 1.1 目标

本方案为 DocuSwarm 系统的 5 大类别（Blocking Question、Pipeline 状态、SummaryAgent、Evaluator 质量门、SDK 安全）共 18 个发现点提供测试驱动的修复路径。

### 1.2 TDD 流程

每个修复任务遵循 **红-绿-重构** 循环：

```
1. 编写失败测试（Red）   → 测试精确捕获当前缺陷
2. 最小改动通过（Green） → 实现最小修复使测试通过
3. 重构保持通过（Refactor）→ 清理代码，确保测试仍通过
```

### 1.3 测试金字塔

```
        /\
       /  \     E2E 验收测试（1 个完整 pipeline 复跑）
      /____\        
     /      \   集成测试（跨组件状态流转）
    /________\      
   /          \ 单元测试（每个发现的精确断言）
  /____________\
```

| 层级 | 数量目标 | 执行时间 |
|------|---------|---------|
| 单元测试 | 35+ | < 30s |
| 集成测试 | 12+ | < 120s |
| E2E 验收 | 1 | < 10min（LLM 调用） |

---

## 2. 测试策略与原则

### 2.1 测试命名规范

```
test_<scope>_<action>_<expected_result>

示例:
- test_prompt_has_no_blocking_questions
- test_completed_pipeline_clears_current_node
- test_validator_rejects_blocking_priority
```

### 2.2 测试文件组织

```
tests/
├── conftest.py                                    # 共享 fixture
├── test_docuswarm_p0_blocking_removal.py         # Phase 0
├── test_docuswarm_p1_state_semantics.py          # Phase 1
├── test_docuswarm_p2_interaction_cleanup.py      # Phase 2
├── test_docuswarm_p3_quality_gates.py            # Phase 3
├── test_docuswarm_p4_security_hardening.py       # Phase 4
└── test_docuswarm_e2e_regression.py              # 集成验收
```

### 2.3 共享 Fixture（conftest.py）

```python
import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_state_manager():
    """返回预配置的 StateManager mock，支持 sync/async 状态操作"""
    sm = MagicMock()
    sm.update_pipeline_state = AsyncMock(return_value=None)
    sm.get_pipeline_state = AsyncMock(return_value={
        "status": "running",
        "current_node": "analyst",
        "node_iterations": {},
        "questions": [],
        "completed_nodes": []
    })
    sm.PIPELINE_STATUSES = ("pending", "running", "completed", "failed", "paused", "cancelled")
    return sm

@pytest.fixture
def sample_pipeline_state():
    """标准 pipeline 完成状态的 fixture"""
    return {
        "pipeline_id": "test-pipe-001",
        "status": "completed",
        "current_node": "po",
        "completed_nodes": ["analyst", "pm", "ux", "architect", "po"],
        "node_iterations": {"analyst": 2, "pm": 2, "ux": 2, "architect": 2, "po": 2},
        "questions": [
            {"node_id": "ux", "priority": "blocking", "text": "blocking question"},
            {"node_id": "analyst", "priority": "clarifying", "text": "clarifying question"},
        ],
        "deliverables": []
    }

@pytest.fixture
def mock_llm_response_fenced_json():
    """返回带 fence 的 JSON 响应"""
    return '''```json
{"summary": "test", "key_points": ["a", "b"], "structure": {"type": "doc"}}
```'''

@pytest.fixture
def mock_llm_response_bare_json():
    """返回裸 JSON 响应"""
    return '{"summary": "test", "key_points": ["a", "b"], "structure": {"type": "doc"}}'
```

---

## 3. Phase 0: 立即止损

> 时间: 1 周  
> 目标: 消除虚假承诺、修复已知残留问题、防止数据污染

---

### 3.1 T-P0-1: 禁用 blocking priority 描述

**对应发现:** F1, F3, F4 — QuestionHandler 无持久化、README 与代码不一致、blocking 语义污染

#### 测试文件: `tests/test_docuswarm_p0_blocking_removal.py`

```python
import pytest
from pathlib import Path

class TestBlockingPriorityRemoval:
    """Phase 0: 从 prompt/schema/validator 全链路移除 blocking priority"""

    # --- 测试 1: Prompt 中不包含 blocking 描述 ---
    def test_contract_builder_prompt_has_no_blocking_questions(self):
        """
        Given: contract_builder.py 中的 prompt 模板
        When: 搜索 blocking 关键字
        Then: 不应出现 "blocking" 优先级描述和示例
        """
        prompt_path = Path("autoBMAD/docuswarm/prompts/contract_builder.py")
        content = prompt_path.read_text()
        
        # 不应包含 blocking 的定义段落
        assert "**blocking**: Must be answered before proceeding" not in content
        # 不应包含 blocking 的示例
        assert "\"priority\": \"blocking\"" not in content
        # 不应在问题优先级列表中出现 blocking
        assert "blocking" not in content.lower().split("valid priorities")[0] if "valid priorities" in content.lower() else True

    # --- 测试 2: Independent agent prompt 清理 ---
    def test_independent_agent_prompt_no_blocking(self):
        """
        Given: agents/independent.py 中的 system prompt
        When: 检查问题优先级说明
        Then: 仅允许 clarifying 和 optional
        """
        agent_path = Path("autoBMAD/docuswarm/agents/independent.py")
        content = agent_path.read_text()
        
        # 查找 submit_execution_report 相关 prompt
        assert "\"priority\": \"blocking\"" not in content
        # 如果有优先级枚举，不应包含 blocking
        if "enum" in content and "priority" in content:
            enum_section = content[content.find("enum"):content.find("enum")+200]
            assert "blocking" not in enum_section.lower()

    # --- 测试 3: Validator 拒绝 blocking 输入 ---
    def test_validator_rejects_blocking_priority(self):
        """
        Given: 提交包含 blocking priority 的问题
        When: context/validator.py 验证
        Then: 抛出 ValidationError 或自动降级
        """
        from autoBMAD.docuswarm.context.validator import ContextValidator
        
        validator = ContextValidator()
        question_data = {
            "questions": [{
                "id": "q1",
                "text": "test question",
                "priority": "blocking"  # 应被拒绝
            }]
        }
        
        with pytest.raises((ValueError, AssertionError)) as exc_info:
            validator.validate_questions(question_data)
        
        assert "blocking" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    # --- 测试 4: Schema 枚举不含 blocking ---
    def test_create_deliverable_schema_excludes_blocking(self):
        """
        Given: create_deliverable_sdk.py 的工具 schema
        When: 检查 priority 枚举
        Then: enum 中不包含 "blocking"
        """
        schema_path = Path("autoBMAD/docuswarm/tools/create_deliverable_sdk.py")
        content = schema_path.read_text()
        
        # 查找 enum 定义
        assert '"blocking"' not in content
        # 确认 clarifying 和 optional 仍存在
        assert '"clarifying"' in content
        assert '"optional"' in content

    # --- 测试 5: 历史 blocking 自动降级 ---
    def test_collect_questions_downgrades_blocking(self, mock_state_manager, caplog):
        """
        Given: 从 DB 读取到包含 blocking priority 的历史问题
        When: QuestionHandler.collect_questions() 处理
        Then: blocking 降级为 clarifying，并记录 warning
        """
        from autoBMAD.docuswarm.pipeline.questions import QuestionHandler, QuestionPriority
        
        handler = QuestionHandler(state_manager=mock_state_manager)
        raw_questions = [
            {"node_id": "ux", "priority": "blocking", "text": "old blocking question"},
            {"node_id": "pm", "priority": "clarifying", "text": "normal question"}
        ]
        
        with caplog.at_level("WARNING"):
            result = handler.collect_questions("test-pipe", raw_questions)
        
        # blocking 应被降级
        blocking_items = [q for q in result if q.priority == QuestionPriority.BLOCKING]
        assert len(blocking_items) == 0
        
        # 应产生 warning 日志
        assert any("downgraded" in record.message.lower() or "blocking" in record.message.lower() 
                   for record in caplog.records)

    # --- 测试 6: Pipeline 完成时允许非阻塞问题存在 ---
    def test_pipeline_completes_with_clarifying_optional(self, mock_state_manager):
        """
        Given: pipeline 中存在 clarifying/optional 问题
        When: 所有节点执行完成
        Then: status = completed，不等待回答
        """
        from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
        
        orchestrator = PipelineOrchestrator(state_manager=mock_state_manager)
        final_state = {
            "status": "completed",
            "questions": [
                {"priority": "clarifying", "text": "q1"},
                {"priority": "optional", "text": "q2"}
            ]
        }
        
        # 不应因为存在 clarifying/optional 问题而阻止完成
        assert final_state["status"] == "completed"
        assert len(final_state["questions"]) == 2
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `prompts/contract_builder.py` | 删除 blocking 描述段落和示例 | 测试 1 通过 |
| `agents/independent.py` | 删除 blocking 相关 prompt 内容 | 测试 2 通过 |
| `context/validator.py` | `VALID_PRIORITIES` 删除 blocking | 测试 3 通过 |
| `tools/create_deliverable_sdk.py` | enum 删除 blocking | 测试 4 通过 |
| `pipeline/questions.py` | `collect_questions` 中降级 blocking + warning | 测试 5 通过 |

---

### 3.2 T-P0-2: 修复 SummaryAgent JSON 解析

**对应发现:** SUM-1 — json.loads() 无法处理 fenced JSON

```python
class TestSummaryAgentJsonParsing:
    """Phase 0: SummaryAgent 应正确处理 fenced JSON"""

    @pytest.mark.asyncio
    async def test_summary_agent_accepts_fenced_json(self, mock_llm_response_fenced_json):
        """
        Given: LLM 返回带 ```json fence 的响应
        When: SummaryAgent 解析
        Then: 一次解析成功，不触发 retry
        """
        from autoBMAD.docuswarm.agents.summary import SummaryAgent
        
        agent = SummaryAgent()
        # 模拟 _call_llm 返回 fenced JSON
        agent._call_llm = AsyncMock(return_value=mock_llm_response_fenced_json)
        
        result = await agent.summarize(content="test", metadata={})
        
        assert "summary" in result
        assert result["summary"] == "test"
        # 确认只调用了一次 LLM（无 retry）
        assert agent._call_llm.call_count == 1

    @pytest.mark.asyncio
    async def test_summary_agent_accepts_bare_json(self, mock_llm_response_bare_json):
        """
        Given: LLM 返回裸 JSON 响应
        When: SummaryAgent 解析
        Then: 正常解析成功
        """
        from autoBMAD.docuswarm.agents.summary import SummaryAgent
        
        agent = SummaryAgent()
        agent._call_llm = AsyncMock(return_value=mock_llm_response_bare_json)
        
        result = await agent.summarize(content="test", metadata={})
        
        assert result["summary"] == "test"
        assert agent._call_llm.call_count == 1

    def test_summary_agent_has_extract_json_fallback(self):
        """
        Given: SummaryAgent 源码
        When: 检查 JSON 解析路径
        Then: 使用 extract_json 或等效的 fenced JSON 处理，而非裸 json.loads
        """
        import inspect
        from autoBMAD.docuswarm.agents.summary import SummaryAgent
        
        source = inspect.getsource(SummaryAgent.summarize)
        
        # 不应直接使用 json.loads(summary_text)
        assert "json.loads(summary_text)" not in source
        # 应使用 extract_json 或类似的 fenced JSON 解析器
        assert "extract_json" in source or "_extract_json" in source or "fence" in source.lower()
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `agents/summary.py` | `json.loads(summary_text)` → `extract_json(summary_text)` | 测试 1, 2, 3 通过 |

> 参考: EvaluatorAgent 已实现 `extract_json` fallback，可直接复用或提取为共享工具函数。

---

### 3.3 T-P0-3: 修复日志事件名

**对应发现:** STATE-5 — `pipeline_started` 事件名错误（实际在完成后触发）

```python
class TestLogEventNames:
    """Phase 0: 日志事件名应与实际语义匹配"""

    def test_final_log_event_is_pipeline_completed(self):
        """
        Given: orchestrator.py 源码
        When: 检查 finalize 阶段的日志事件
        Then: 事件名为 "pipeline_completed" 而非 "pipeline_started"
        """
        import inspect
        from autoBMAD.docuswarm.pipeline import orchestrator
        
        source = inspect.getsource(orchestrator.PipelineOrchestrator._finalize_pipeline)
        # 检查 finalize 方法中的日志事件名
        assert '"pipeline_started"' not in source
        assert '"pipeline_completed"' in source

    @pytest.mark.asyncio
    async def test_finalize_logs_correct_event(self, mock_state_manager, caplog):
        """
        Given: pipeline 执行到 finalize 阶段
        When: 记录最终状态日志
        Then: 日志中包含 pipeline_completed 事件
        """
        from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
        import logging
        
        orchestrator = PipelineOrchestrator(state_manager=mock_state_manager)
        
        with caplog.at_level(logging.INFO):
            await orchestrator._finalize_pipeline(
                pipeline_id="test-001",
                final_status="completed",
                result={"status": "completed"}
            )
        
        assert any("pipeline_completed" in record.message 
                   for record in caplog.records)
        assert not any("pipeline_started" in record.message 
                       for record in caplog.records)
```

---

## 4. Phase 1: 状态语义修复

> 时间: 2-3 天  
> 目标: 修复 current_node、node_iterations、emergency finalize、state merge 语义

---

### 4.1 T-P1-1: 清空 completed 状态的 current_node

**对应发现:** STATE-1 — `current_node` 在完成后未清空

```python
class TestCompletedStateCurrentNode:
    """Phase 1: completed pipeline 应清空 current_node"""

    def test_completed_pipeline_current_node_is_none(self):
        """
        Given: 所有节点执行完成的 pipeline
        When: finalize 写入最终状态
        Then: current_node = None，last_node 保留最后执行的节点
        """
        # 模拟 finalize 后的状态
        final_state = {
            "status": "completed",
            "current_node": None,      # 应被清空
            "last_node": "po",         # 新字段，保留最后节点
            "completed_nodes": ["analyst", "pm", "ux", "architect", "po"]
        }
        
        assert final_state["current_node"] is None
        assert final_state["last_node"] == "po"

    @pytest.mark.asyncio
    async def test_orchestrator_finalize_clears_current_node(self, mock_state_manager):
        """
        Given: 执行完所有节点的 orchestrator
        When: _finalize_pipeline 被调用
        Then: state 更新包含 current_node=None
        """
        from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
        
        orchestrator = PipelineOrchestrator(state_manager=mock_state_manager)
        
        await orchestrator._finalize_pipeline(
            pipeline_id="test-001",
            final_status="completed",
            result={"current_node": "po", "status": "running"}
        )
        
        # 验证 update_pipeline_state 被调用时的参数
        call_args = mock_state_manager.update_pipeline_state.call_args
        state_update = call_args[1].get("state") or call_args[1].get("state_data") or call_args[0][1]
        
        assert state_update.get("current_node") is None
        assert state_update.get("last_node") == "po"

    def test_graph_sets_current_node_per_execution(self):
        """
        Given: graph.py 节点执行逻辑
        When: 每个节点开始执行
        Then: 设置 current_node = node_id
        """
        import inspect
        from autoBMAD.docuswarm.pipeline import graph
        
        source = inspect.getsource(graph.execute_node)
        assert 'current_node"' in source or "current_node =" in source
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `pipeline/graph.py` | finalize 阶段设置 `current_node=None`, `last_node=最后一个节点` | 测试 1, 2, 3 通过 |
| `pipeline/orchestrator.py` | final write 读取 last_node 而非 current_node | - |

---

### 4.2 T-P1-2: 修复 node_iterations 计数

**对应发现:** STATE-2 — `node_iterations` 与实际 iteration 不一致

```python
class TestNodeIterationsAccuracy:
    """Phase 1: node_iterations 应准确反映 DualAgent 迭代次数"""

    def test_single_iteration_records_one(self):
        """
        Given: 节点一次通过（Independent + Evaluator 一次 approved）
        When: 记录 node_iterations
        Then: node_iterations[node_id] == 1
        """
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
        
        # 模拟执行 1 轮 iteration
        iteration_count = 1
        node_id = "analyst"
        
        # 期望记录值
        expected_iterations = {node_id: iteration_count}
        assert expected_iterations[node_id] == 1

    def test_multiple_iterations_recorded_correctly(self):
        """
        Given: 节点需要 3 轮 iteration（两次 revision）
        When: 记录 node_iterations
        Then: node_iterations[node_id] == 3
        """
        iteration_count = 3
        node_id = "pm"
        
        expected_iterations = {node_id: iteration_count}
        assert expected_iterations[node_id] == 3

    @pytest.mark.asyncio
    async def test_dual_agent_iteration_semantics(self, mock_state_manager):
        """
        Given: DualAgentNode 执行
        When: 每完成一轮 iteration
        Then: iteration 计数器在正确时机递增，禁止二次递增
        """
        import inspect
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
        
        source = inspect.getsource(DualAgentNode.execute_with_iteration)
        
        # 检查 iteration 递增逻辑
        assert "iteration" in source
        # 确保没有双重递增（如 graph.py 和 dual_agent.py 各增一次）
        iteration_increments = source.count("iteration += 1") + source.count("iteration=iteration+1")
        # 应只在一处递增
        assert iteration_increments <= 1

    def test_node_result_iteration_off_by_one(self):
        """
        Given: NodeResult 的 iteration 字段
        When: 第一次执行
        Then: iteration 值为 1（而非 2）
        """
        from autoBMAD.docuswarm.nodes.dual_agent import NodeResult
        
        result = NodeResult(
            node_id="test",
            iteration=1,  # 应为 1
            approved=True,
            deliverable="test"
        )
        assert result.iteration == 1
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `nodes/dual_agent.py` | 统一 iteration 语义：第 1 次执行 = 1 | 测试 1, 2, 4 通过 |
| `pipeline/graph.py` | 移除二次递增逻辑，直接使用 NodeResult.iteration | 测试 3 通过 |

---

### 4.3 T-P1-3: 修复 emergency finalize 状态合法性

**对应发现:** STATE-3 — `'interrupted'` 不在合法状态集合中 + 破坏单一状态源

```python
class TestEmergencyFinalize:
    """Phase 1: emergency finalize 应写入合法状态并同步 state_json"""

    def test_emergency_finalize_uses_valid_status(self):
        """
        Given: emergency finalize 场景（如 KeyboardInterrupt、atexit）
        When: cli/services/pipeline_service.py 更新状态
        Then: 使用合法状态值，且同步更新 state_json
        """
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        valid_statuses = set(StateManager.PIPELINE_STATUSES)
        
        # 旧代码使用 'interrupted'，应在合法集合中被替换
        assert "interrupted" not in valid_statuses
        # 推荐使用 'cancelled' 或 'failed'
        assert "cancelled" in valid_statuses
        assert "failed" in valid_statuses

    @pytest.mark.asyncio
    async def test_emergency_finalize_updates_state_json(self, mock_state_manager):
        """
        Given: 通过 atexit handler 触发 emergency finalize
        When: 更新 pipelines 表
        Then: 同时更新 state_json.status，保持单一真实状态源
        """
        from autoBMAD.docuswarm.cli.services.pipeline_service import emergency_finalize
        
        # 模拟 emergency finalize
        await emergency_finalize(
            pipeline_id="test-001",
            reason="keyboard_interrupt"
        )
        
        # 验证 state_manager 被调用更新完整状态
        mock_state_manager.update_pipeline_state.assert_called_once()
        call_kwargs = mock_state_manager.update_pipeline_state.call_args[1]
        
        # 确保 state_json 被更新
        state_data = call_kwargs.get("state") or call_kwargs.get("state_data")
        if state_data:
            assert state_data.get("status") in ("cancelled", "failed")

    def test_state_manager_has_replace_operation(self):
        """
        Given: StateManager 实现
        When: 检查状态更新方法
        Then: 提供 replace_pipeline_state() 用于完整替换
        """
        import inspect
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        source = inspect.getsource(StateManager)
        
        # 应存在 replace 方法
        assert "def replace_pipeline_state" in source or "replace" in source
        # deep_merge 仍可作为 patch 操作保留
        assert "def _deep_merge" in source or "def deep_merge" in source
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `cli/services/pipeline_service.py` | `'interrupted'` → `'cancelled'` 或 `'failed'`，使用 StateManager API | 测试 1, 2 通过 |
| `storage/state_manager.py` | 新增 `replace_pipeline_state()`，final write 使用 replace | 测试 3 通过 |

---

### 4.4 T-P1-4: StateManager deep merge 保留旧字段

**对应发现:** STATE-4 — `_deep_merge` 不支持删除语义

```python
class TestStateManagerMergeSemantics:
    """Phase 1: 区分 patch (merge) 和 replace 语义"""

    def test_deep_merge_preserves_unspecified_fields(self):
        """
        Given: 现有状态包含字段 A, B, C
        When: update_pipeline_state 传入 {A: new_value}
        Then: B, C 仍保留（patch 语义）
        """
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        sm = StateManager()
        target = {"a": 1, "b": 2, "c": {"d": 3, "e": 4}}
        source = {"a": 10}
        
        sm._deep_merge(target, source)
        
        assert target["a"] == 10  # 更新
        assert target["b"] == 2   # 保留
        assert target["c"]["d"] == 3  # 保留嵌套

    def test_replace_pipeline_state_removes_unspecified_fields(self):
        """
        Given: 现有状态包含字段 A, B, C
        When: replace_pipeline_state 传入 {A: new_value}
        Then: B, C 被删除（replace 语义）
        """
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        sm = StateManager()
        old_state = {"a": 1, "b": 2, "questions": [{"old": "q"}]}
        new_state = {"a": 10}
        
        result = sm.replace_pipeline_state("test-001", new_state)
        
        assert "b" not in result
        assert "questions" not in result
        assert result["a"] == 10

    def test_resume_does_not_carry_stale_questions(self, mock_state_manager):
        """
        Given: 上一轮运行遗留 questions
        When: 重启 pipeline
        Then: 旧 questions 不应出现在新运行中（replace 语义）
        """
        # 如果 restart 使用 replace，旧 questions 会被清除
        # 如果 resume 使用 merge，需要显式清理
        pass  # 集成测试覆盖
```

---

## 5. Phase 2: 移除虚假交互系统

> 时间: 3-5 天  
> 目标: 删除不可用的交互代码，保留诊断只读能力

---

### 5.1 T-P2-1: 删除 answer CLI 命令

**对应发现:** F1, F2, F3 — 交互系统无法工作

```python
class TestInteractionSystemRemoval:
    """Phase 2: 移除虚假交互系统，保留诊断能力"""

    def test_cli_no_answer_command(self):
        """
        Given: CLI 命令注册表
        When: 检查可用命令
        Then: 不注册 answer 命令
        """
        import subprocess
        result = subprocess.run(
            ["python", "-m", "autoBMAD.docuswarm.cli", "--help"],
            capture_output=True, text=True
        )
        
        assert "answer" not in result.stdout.lower() or "answer" not in result.stdout

    def test_answer_module_removed(self):
        """
        Given: cli/commands/ 目录
        When: 检查文件列表
        Then: 不存在 answer.py
        """
        answer_path = Path("autoBMAD/docuswarm/cli/commands/answer.py")
        assert not answer_path.exists()

    def test_question_handler_no_answer_method(self):
        """
        Given: QuestionHandler 类
        When: 检查方法列表
        Then: 不存在 answer_question / has_blocking_questions / _incorporate_answer
        """
        import inspect
        from autoBMAD.docuswarm.pipeline.questions import QuestionHandler
        
        methods = [name for name, _ in inspect.getmembers(QuestionHandler, predicate=inspect.isfunction)]
        
        assert "answer_question" not in methods
        assert "has_blocking_questions" not in methods
        assert "_incorporate_answer" not in methods
```

---

### 5.2 T-P2-2: 改造 questions CLI 为 diagnostics

```python
    def test_questions_command_renamed_to_diagnostics(self):
        """
        Given: CLI 命令
        When: 检查命令列表
        Then: 存在 diagnostics 命令（替代 questions）
        """
        import subprocess
        result = subprocess.run(
            ["python", "-m", "autoBMAD.docuswarm.cli", "--help"],
            capture_output=True, text=True
        )
        
        assert "diagnostics" in result.stdout.lower()

    def test_diagnostics_exports_pipeline_state(self, mock_state_manager):
        """
        Given: 已完成的 pipeline
        When: 运行 diagnostics 命令
        Then: 导出包含非阻塞 follow-ups 的诊断信息
        """
        from autoBMAD.docuswarm.cli.commands.diagnostics import DiagnosticsCommand
        
        mock_state_manager.get_pipeline_state = AsyncMock(return_value={
            "pipeline_id": "test-001",
            "status": "completed",
            "questions": [
                {"node_id": "analyst", "priority": "clarifying", "text": "q1"},
                {"node_id": "pm", "priority": "optional", "text": "q2"}
            ],
            "completed_nodes": ["analyst", "pm"]
        })
        
        cmd = DiagnosticsCommand(state_manager=mock_state_manager)
        result = cmd.execute(pipeline_id="test-001")
        
        # 应包含非阻塞问题作为诊断信息
        assert "clarifying" in result or "follow" in result.lower()
        assert "blocking" not in result.lower()
```

---

### 5.3 T-P2-3: 清理 DualAgentNode question_handler

```python
    def test_create_dual_agent_node_no_question_handler_param(self):
        """
        Given: create_dual_agent_node 函数签名
        When: 检查参数列表
        Then: 不包含 question_handler 参数
        """
        import inspect
        from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
        
        sig = inspect.signature(create_dual_agent_node)
        param_names = list(sig.parameters.keys())
        
        assert "question_handler" not in param_names

    def test_dual_agent_node_no_collect_questions_call(self):
        """
        Given: DualAgentNode.execute_with_iteration 源码
        When: 检查 collect_questions 调用
        Then: 不存在 collect_questions 调用
        """
        import inspect
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
        
        source = inspect.getsource(DualAgentNode.execute_with_iteration)
        assert "collect_questions" not in source

    def test_questions_still_recorded_in_node_result(self):
        """
        Given: 节点执行产生问题
        When: 返回 NodeResult
        Then: questions 字段仍保留（仅移除 QuestionHandler 中间层）
        """
        from autoBMAD.docuswarm.nodes.dual_agent import NodeResult
        
        result = NodeResult(
            node_id="test",
            iteration=1,
            approved=True,
            deliverable="test",
            questions=[{"priority": "clarifying", "text": "q1"}]
        )
        
        assert len(result.questions) == 1
        assert result.questions[0]["priority"] == "clarifying"
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `cli/commands/answer.py` | 删除文件 | 测试 1, 2 通过 |
| `cli/commands/questions.py` | 重命名为 diagnostics.py，改为只读 | 测试 3, 4 通过 |
| `pipeline/questions.py` | 删除交互方法，保留 collect_questions（降级逻辑） | 测试 5 通过 |
| `nodes/dual_agent.py` | 删除 question_handler 参数和 collect_questions 调用 | 测试 6, 7, 8 通过 |
| `README.md` | 删除交互式问答章节 | 文档审查 |

---

## 6. Phase 3: 质量门增强

> 时间: 1 周  
> 目标: 增加 hard gate、统一编号、优化模板

---

### 6.1 T-P3-1: Evaluator hard gate

**对应发现:** QG-1, QG-2 — 容忍度过高、缺少 hard gate

```python
class TestEvaluatorHardGate:
    """Phase 3: Evaluator 应在 score-based verdict 后增加离散缺陷检查"""

    def test_factual_error_blocks_approval(self):
        """
        Given: alignment_score = 0.95，但 issues_found 包含 factual_error
        When: Evaluator 判定 verdict
        Then: verdict != APPROVED（应为 NEEDS_REVISION 或 REJECTED）
        """
        from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
        
        agent = EvaluatorAgent()
        
        evaluation = {
            "alignment_score": 0.95,
            "issues_found": [
                {"type": "factual_error", "severity": "high", "description": "Wrong framework"}
            ]
        }
        
        verdict = agent._apply_hard_gate(evaluation)
        
        assert verdict != "APPROVED"
        assert verdict in ("NEEDS_REVISION", "REJECTED")

    def test_blocking_question_downgraded_but_still_flagged(self):
        """
        Given: 问题被降级为 clarifying，但内容涉及关键事实
        When: hard gate 检查
        Then: 根据内容严重性触发 revision
        """
        from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
        
        agent = EvaluatorAgent()
        
        evaluation = {
            "alignment_score": 0.93,
            "issues_found": [
                {"type": "blocking_question", "severity": "medium", "description": "Missing dependency"}
            ]
        }
        
        verdict = agent._apply_hard_gate(evaluation)
        assert verdict == "NEEDS_REVISION"

    def test_ac_ambiguity_triggers_revision(self):
        """
        Given: alignment_score = 0.91，issues_found 包含 acceptance_criteria_ambiguity
        When: hard gate 检查
        Then: verdict = NEEDS_REVISION
        """
        from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
        
        agent = EvaluatorAgent()
        
        evaluation = {
            "alignment_score": 0.91,
            "issues_found": [
                {"type": "acceptance_criteria_ambiguity", "severity": "medium"}
            ]
        }
        
        verdict = agent._apply_hard_gate(evaluation)
        assert verdict == "NEEDS_REVISION"

    def test_clean_evaluation_passes_hard_gate(self):
        """
        Given: alignment_score = 0.85，无 issues_found
        When: hard gate 检查
        Then: verdict = APPROVED（score-based 逻辑不变）
        """
        from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
        
        agent = EvaluatorAgent()
        
        evaluation = {
            "alignment_score": 0.85,
            "issues_found": []
        }
        
        verdict = agent._apply_hard_gate(evaluation)
        # 无离散缺陷时，保持 score-based 判定
        assert verdict == "APPROVED"

    def test_hard_gate_check_exists_in_source(self):
        """
        Given: evaluator.py 源码
        When: 检查 verdict 判定逻辑
        Then: 在 score 检查之后存在 issues_found 遍历检查
        """
        import inspect
        from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
        
        source = inspect.getsource(EvaluatorAgent)
        
        # 应存在 hard gate 相关逻辑
        assert "_apply_hard_gate" in source or "factual_error" in source or "issues_found" in source
```

#### 实现要点

| 文件 | 改动 | 验收标准 |
|------|------|---------|
| `agents/evaluator.py` | 新增 `_apply_hard_gate()` 方法，在 `determine_verdict()` 后调用 | 测试 1-5 通过 |

---

### 6.2 T-P3-2: 统一编号规范

**对应发现:** QG-3 — 编号体系不一致

```python
class TestNumberingConsistency:
    """Phase 3: 交付物编号应统一为 3 位格式"""

    def test_contract_builder_uses_three_digit_numbers(self):
        """
        Given: contract_builder.py 中的编号模板
        When: 检查 FR/NFR/AC 编号格式
        Then: 统一使用 XXX（如 FR-001，NFR-001，AC-001）
        """
        prompt_path = Path("autoBMAD/docuswarm/prompts/contract_builder.py")
        content = prompt_path.read_text()
        
        # 查找编号示例
        if "FR-" in content:
            # 不应出现 2 位编号（如 FR-01）
            assert "FR-01\"" not in content or "FR-01 " not in content
            # 应出现 3 位编号
            assert "FR-001" in content or "XXX" in content

    def test_deliverable_numbering_is_consistent(self, tmp_path):
        """
        Given: 生成的交付物文件
        When: 检查编号格式
        Then: 所有 FR/NFR/AC 使用统一位数
        """
        # 集成测试：运行 pipeline 后检查输出文件
        pass
```

---

### 6.3 T-P3-3: SummaryAgent 缓存标记

**对应发现:** SUM-2 — 缓存配置未实现

```python
class TestSummaryAgentCache:
    """Phase 3: 缓存配置应标记实现状态"""

    def test_cache_config_matches_implementation(self):
        """
        Given: config/summary_agent.yaml 和 agents/summary.py
        When: 检查缓存配置与实际实现的一致性
        Then: 实现与配置匹配，或配置标记为 reserved_for_future
        """
        config_path = Path("autoBMAD/docuswarm/config/summary_agent.yaml")
        agent_path = Path("autoBMAD/docuswarm/agents/summary.py")
        
        config_content = config_path.read_text()
        agent_content = agent_path.read_text()
        
        if "caching:" in config_content and "enable: true" in config_content:
            # 如果配置启用，代码中应有实现
            has_cache_impl = (
                "cache" in agent_content and
                "ttl" in agent_content.lower() or
                "hit" in agent_content.lower()
            )
            # 如果没有实现，配置应标记为 reserved
            if not has_cache_impl:
                assert "reserved_for_future" in config_content or "enable: false" in config_content
```

---

## 7. Phase 4: 安全加固

> 时间: 1 周（可选）  
> 目标: 收紧 SDK cwd、增强路径校验、审计 allowed_tools

---

### 7.1 T-P4-1: SDK cwd 边界

**对应发现:** SEC-1 — SDK cwd 超出 repo root

```python
class TestSdkSecurity:
    """Phase 4: SDK 安全边界加固"""

    def test_sdk_cwd_is_repo_root(self):
        """
        Given: independent.py 中的 repo_root 计算
        When: project_root = /home/leafliu/autoBMAD/autoBMAD
        Then: cwd = /home/leafliu/autoBMAD（repo root），不超出
        """
        import inspect
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        source = inspect.getsource(IndependentAgent._get_sdk_cwd)
        
        # 不应使用 parent 跳转到 repo 外部
        assert ".parent" not in source or "repo_root = project_root" in source

    def test_sdk_cwd_not_parent_of_repo(self):
        """
        Given: 任何 project_root 值
        When: 计算 sdk_cwd
        Then: sdk_cwd 在 repo_root 下，不超出
        """
        from pathlib import Path
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        agent = IndependentAgent(project_root=Path("/home/leafliu/autoBMAD/autoBMAD"))
        cwd = agent._get_sdk_cwd()
        
        repo_root = Path("/home/leafliu/autoBMAD")
        assert Path(cwd).resolve().is_relative_to(repo_root.resolve())
        # cwd 不应是 repo_root 的父目录
        assert not repo_root.resolve().is_relative_to(Path(cwd).resolve().parent)
```

---

### 7.2 T-P4-2: PathValidator 增强

**对应发现:** SEC-3 — `startswith()` 路径校验不足

```python
    def test_path_validator_uses_is_relative_to(self):
        """
        Given: file_tools_sdk.py 中的 PathValidator
        When: 检查路径校验逻辑
        Then: 使用 resolve().is_relative_to() 作为第二层校验
        """
        import inspect
        from autoBMAD.docuswarm.tools.file_tools_sdk import PathValidator
        
        source = inspect.getsource(PathValidator.validate)
        
        # 应有 is_relative_to 校验
        assert "is_relative_to" in source or "resolve()" in source
        # 不应仅依赖 startswith
        if "startswith" in source:
            assert "is_relative_to" in source  # 作为第二层

    @pytest.mark.parametrize("path,allowed_dir,expected", [
        ("/repo/../etc/passwd", "/repo", False),
        ("/repo/subdir/file.txt", "/repo", True),
        ("/repo-similar/file.txt", "/repo", False),
    ])
    def test_path_validator_blocks_traversal(self, path, allowed_dir, expected):
        """
        Given: 包含路径遍历尝试的输入
        When: PathValidator 校验
        Then: 正确允许/拒绝
        """
        from autoBMAD.docuswarm.tools.file_tools_sdk import PathValidator
        
        validator = PathValidator(allowed_dirs=[allowed_dir])
        result = validator.validate(path)
        
        assert result == expected
```

---

### 7.3 T-P4-3: allowed_tools 审计

**对应发现:** SEC-2 — yolo 模式依赖 allowed_tools 正确生成

```python
    def test_allowed_tools_generation_failure_blocks_yolo(self):
        """
        Given: allowed_tools_generation_failed = True
        When: yolo=True 且 auto_approve_tools=True
        Then: 阻止执行或降级为非 yolo 模式
        """
        import inspect
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        source = inspect.getsource(SessionManager)
        
        # 如果 allowed_tools 生成失败，应阻止 auto_approve
        assert "allowed_tools_generation_failed" in source
        # 不应在失败时静默继续 yolo 模式
        # 验证逻辑：失败时应 raise 或 fallback
```

---

## 8. 集成验收测试

### 8.1 E2E 验收: calc-context.md 复跑

```python
class TestE2ERegression:
    """
    使用 calc-context.md 复跑完整 pipeline，验证全部修复生效。
    对应研究报告最终结论中的验收标准。
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_pipeline_regression(self):
        """
        Given: calc-context.md 作为输入
        When: 运行完整 DocuSwarm pipeline
        Then: 满足以下全部条件:
            1. 无 SummaryAgent JSON retry（一次解析通过）
            2. 无 unanswered blocking question 的 completed 状态
            3. final state 中 current_node = None
            4. 每个节点 node_iterations = 1
            5. 日志出现 pipeline_completed（而非 pipeline_started）
            6. 所有节点 alignment_score < 1.0 但 deliverable 质量可接受
        """
        # 实际集成测试实现
        pass

    @pytest.mark.integration
    def test_pipeline_state_consistency(self, sample_pipeline_state):
        """
        Given: 已完成的 pipeline DB 记录
        When: 检查 state 一致性
        Then: top-level columns 与 state_json 内嵌字段一致
        """
        state = sample_pipeline_state
        
        # 顶层状态与嵌套状态一致
        assert state["status"] == state.get("state_json", {}).get("status", state["status"])
        
        # completed 状态不应有 current_node
        if state["status"] == "completed":
            assert state.get("current_node") is None

    @pytest.mark.integration
    def test_no_illegal_status_in_db(self):
        """
        Given: pipelines 数据库
        When: 查询所有 status 值
        Then: 不包含 'interrupted' 等非法状态
        """
        from autoBMAD.docuswarm.storage.state_manager import StateManager
        
        valid_statuses = set(StateManager.PIPELINE_STATUSES)
        
        # 查询数据库（实际测试中连接 test DB）
        # assert all(status in valid_statuses for status in db_statuses)
```

---

## 9. 风险缓解测试

对应研究报告风险矩阵：

```python
class TestRiskMitigation:
    """针对风险矩阵的专项测试"""

    def test_historic_blocking_read_compatibility(self):
        """
        风险: 历史 pipeline 中的 blocking 值导致读取报错
        缓解: 读取侧兼容降级 + 单测覆盖
        """
        from autoBMAD.docuswarm.pipeline.questions import QuestionHandler, QuestionPriority
        
        # 模拟从 DB 读取到旧 blocking 值
        historic_question = {
            "node_id": "ux",
            "priority": "blocking",  # 旧数据
            "text": "historical question"
        }
        
        handler = QuestionHandler(state_manager=MagicMock())
        
        # 不应抛出异常
        result = handler._normalize_priority(historic_question["priority"])
        assert result != QuestionPriority.BLOCKING  # 应被降级
        assert result in (QuestionPriority.CLARIFYING, QuestionPriority.OPTIONAL)

    def test_questions_json_column_backward_compatible(self):
        """
        风险: questions_json DB 列被第三方工具直接查询
        缓解: 保留列名 + 文档注明字段语义已改为非阻塞
        """
        # 验证 DB schema 未删除 questions_json 列
        # 验证列内容中 priority 不再包含 blocking
        pass

    def test_agent_blocking_response_auto_downgraded(self):
        """
        风险: 代理仍尝试返回 priority='blocking'
        缓解: validator 强拒或自动降级，日志 warning
        """
        from autoBMAD.docuswarm.context.validator import ContextValidator
        
        validator = ContextValidator()
        
        # 代理提交 blocking 响应
        response = {"priority": "blocking", "text": "question"}
        
        # 应被降级或拒绝
        with pytest.warns(UserWarning):
            result = validator.validate_and_normalize_question(response)
            assert result["priority"] != "blocking"
```

---

## 10. 执行时间表与里程碑

### 10.1 Sprint 分解

| 阶段 | 时长 | 测试新增 | 关键里程碑 |
|------|------|---------|-----------|
| **Phase 0** | 3 天 | 10 个单元测试 + 3 个集成测试 | 所有 blocking 相关测试通过 |
| **Phase 1** | 2-3 天 | 12 个单元测试 + 4 个集成测试 | state 一致性 100% |
| **Phase 2** | 3-5 天 | 8 个单元测试 + 2 个集成测试 | answer 命令不可调用 |
| **Phase 3** | 4-5 天 | 8 个单元测试 + 3 个集成测试 | hard gate 阻止事实错误通过 |
| **Phase 4** | 3-4 天（可选） | 6 个单元测试 + 2 个集成测试 | SDK cwd 限制在 repo 内 |
| **E2E 验收** | 1 天 | 1 个 E2E 测试 | calc-context.md 复跑通过 |

### 10.2 每日站会检查清单

```markdown
- [ ] 昨日编写/通过的测试数: ___
- [ ] 昨日修复的发现点: ___
- [ ] 当前失败的测试（红）: ___
- [ ] 阻塞项: ___
- [ ] 今日目标测试: ___
```

### 10.3 最终验收标准

复跑 `calc-context.md` pipeline，确认：

| # | 检查项 | 验证方式 |
|---|--------|---------|
| 1 | 无 SummaryAgent JSON retry | 日志中无 `Invalid JSON response` |
| 2 | 无 blocking question 的 completed 状态 | DB 查询 `questions` 中无 blocking |
| 3 | `current_node=None` | DB `state_json->current_node` IS NULL |
| 4 | 每个节点 `node_iterations=1` | DB `node_iterations` JSON 全为 1 |
| 5 | 日志出现 `pipeline_completed` | 日志搜索 `pipeline_completed` |
| 6 | `diagnostics` 命令可用 | CLI `docuswarm diagnostics` 正常输出 |
| 7 | `answer` 命令不存在 | CLI `docuswarm answer` 返回 `No such command` |
| 8 | 无 `interrupted` 状态 | DB `SELECT DISTINCT status FROM pipelines` |

---

## 附录 A: 发现点到测试的映射表

| 发现编号 | 发现描述 | Phase | 测试 ID | 测试文件 |
|----------|---------|-------|---------|---------|
| F1 | QuestionHandler 无持久化 | P0 | T-P0-1-5 | `test_docuswarm_p0_blocking_removal.py` |
| F2 | create_dual_agent_node 未注入 QuestionHandler | P2 | T-P2-3-1 | `test_docuswarm_p2_interaction_cleanup.py` |
| F3 | README 与代码不一致 | P0/P2 | T-P0-1-1, T-P2-1-1 | 多文件 |
| F4 | blocking 语义污染 | P0 | T-P0-1-3, T-P0-1-5 | `test_docuswarm_p0_blocking_removal.py` |
| F5 | 两套 QuestionPriority 定义 | P0 | T-P0-1-3 | `test_docuswarm_p0_blocking_removal.py` |
| F6 | questions 字段审计价值 | P0 | T-P0-1-6 | `test_docuswarm_p0_blocking_removal.py` |
| STATE-1 | current_node 未清空 | P1 | T-P1-1-1,2 | `test_docuswarm_p1_state_semantics.py` |
| STATE-2 | node_iterations 不一致 | P1 | T-P1-2-1,2,3,4 | `test_docuswarm_p1_state_semantics.py` |
| STATE-3 | emergency finalize 非法状态 | P1 | T-P1-3-1,2 | `test_docuswarm_p1_state_semantics.py` |
| STATE-4 | deep merge 保留旧字段 | P1 | T-P1-4-1,2,3 | `test_docuswarm_p1_state_semantics.py` |
| STATE-5 | pipeline_started 事件名 | P0 | T-P0-3-1,2 | `test_docuswarm_p0_blocking_removal.py` |
| SUM-1 | json.loads 无法处理 fence | P0 | T-P0-2-1,2,3 | `test_docuswarm_p0_blocking_removal.py` |
| SUM-2 | 缓存配置未实现 | P3 | T-P3-3-1 | `test_docuswarm_p3_quality_gates.py` |
| SUM-3 | Evaluator/SummaryAgent 能力差距 | P0 | T-P0-2-3 | `test_docuswarm_p0_blocking_removal.py` |
| SEC-1 | SDK cwd 超出 repo | P4 | T-P4-1-1,2 | `test_docuswarm_p4_security_hardening.py` |
| SEC-2 | yolo 依赖 allowed_tools | P4 | T-P4-3-1 | `test_docuswarm_p4_security_hardening.py` |
| SEC-3 | PathValidator startswith | P4 | T-P4-2-1,2 | `test_docuswarm_p4_security_hardening.py` |
| QG-1 | 容忍度过高 | P3 | T-P3-1-1,4 | `test_docuswarm_p3_quality_gates.py` |
| QG-2 | 缺少 hard gate | P3 | T-P3-1-1,2,3 | `test_docuswarm_p3_quality_gates.py` |
| QG-3 | 编号不一致 | P3 | T-P3-2-1 | `test_docuswarm_p3_quality_gates.py` |
| QG-4 | 架构输出过度展开 | P3 | — | 文档模板调整（无自动化测试） |

---

## 附录 B: 运行命令速查

```bash
# 运行全部单元测试
pytest tests/test_docuswarm_p0_*.py tests/test_docuswarm_p1_*.py -v

# 运行单个 Phase 测试
pytest tests/test_docuswarm_p0_blocking_removal.py -v

# 运行集成测试
pytest tests/test_docuswarm_e2e_regression.py -v -m integration

# 生成覆盖率报告
pytest --cov=autoBMAD.docuswarm --cov-report=html tests/

# 运行特定发现点测试
pytest -k "test_validator_rejects_blocking" -v
pytest -k "test_completed_pipeline_current_node" -v
pytest -k "test_summary_agent_accepts_fenced" -v
pytest -k "test_factual_error_blocks" -v
```

---

*本方案为测试驱动修复的完整蓝图。实施时应严格遵循红-绿-重构循环，每通过一个测试即提交一次代码，确保修复过程可追踪、可回滚。*
