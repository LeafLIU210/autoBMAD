# DocuSwarm calc-one-plus-one 修复测试驱动方案 (TDD Plan)

**日期**: 2026-05-01  
**基于研究报告**: `docs-doc/research/2026-05-01-docuswarm-calc-one-plus-one-fix-direction-deep-research.md`  
**目标**: 为 P0-1、P0-2、P1-1、P1-2 四个问题域提供「先写失败测试 → 再实现修复」的完整方案  
**测试框架**: pytest + pytest-asyncio  
**命名约定**: 延续 `test_docuswarm_p0_*.py` / `test_docuswarm_p1_*.py` 模式

---

## 目录

1. [执行顺序与依赖图](#1-执行顺序与依赖图)
2. [P0-1: Analyst 节点契约漂移](#2-p0-1-analyst-节点契约漂移)
3. [P0-2: ResultMessage 完成语义](#3-p0-2-resultmessage-完成语义)
4. [P1-1: BLOCKED/NEEDS_REVISION 策略](#4-p1-1-blockedneeds_revision-策略)
5. [P1-2: 路径语义漂移](#5-p1-2-路径语义漂移)
6. [端到端回归验证](#6-端到端回归验证)
7. [附录：共享 Fixtures](#7-附录共享-fixtures)

---

## 1. 执行顺序与依赖图

```
Step 1: P0-2 失败测试 (test_docuswarm_p0_result_message_semantic.py)
        │  不依赖其他修复，可最先实施
        ▼
Step 2: P0-1 失败测试 (test_docuswarm_p0_analyst_contract_drift.py)
        │  不依赖其他修复，可与 P0-2 并行
        ▼
Step 3: P1-1 失败测试 (test_docuswarm_p1_verdict_iteration_consistency.py)
        │  依赖 P0-2 修复（需要正常的 prompt 流来模拟 evaluator 调用）
        ▼
Step 4: P1-2 失败测试 (test_docuswarm_p1_path_semantic_drift.py)
        │  可独立实施，但建议在所有 P0 修复之后
        ▼
Step 5: 端到端回归 (test_docuswarm_p0_calc_regression.py)
        └── 使用 mock LLM 验证完整 pipeline 对 calc-context 的正确处理
```

**原则**:
- 每个 Step 必须先有**失败测试**，再修改生产代码
- 修改生产代码后，同一 Step 的测试应**变绿**
- 任何 Step 的修复都不应使之前变绿的测试**变红**

---

## 2. P0-1: Analyst 节点契约漂移

### 2.1 测试文件

**文件**: `tests/test_docuswarm_p0_analyst_contract_drift.py`

### 2.2 测试设计哲学

这些测试不调用 LLM，而是通过以下方式验证契约：
1. **静态断言**: 直接读取 `node.yaml`、`persona.json`、`evaluator.yaml`、模板文件，断言内容不包含市场研究关键词
2. **Prompt Contract 断言**: 使用 `NodePromptContractBuilder` 构建 contract，断言渲染后的 prompt 包含需求分析关键词
3. **模板 Fallback 断言**: 验证 `_find_best_template_match()` 在无法匹配时不会无条件返回 `templates[0]`

### 2.3 失败测试代码

```python
"""P0-1: Analyst node contract drift — TDD failing tests.

Before fix: tests FAIL because analyst node assets describe Data Analyst/BI.
After fix:  tests PASS because analyst node assets describe Requirements Analysis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml


# ---------------------------------------------------------------------------
# T1: Static asset contract tests (no LLM)
# ---------------------------------------------------------------------------

class TestAnalystNodeYamlContract:
    """T1.1-T1.3: node.yaml must describe requirements analysis, not BI."""

    @pytest.fixture
    def analyst_node_yaml(self, repo_root: Path) -> dict[str, Any]:
        path = repo_root / "autoBMAD" / "nodes" / "analyst" / "node.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_description_is_not_data_analyst_bi(self, analyst_node_yaml: dict[str, Any]) -> None:
        """FAIL before fix: description contains 'Data Analyst & Business Intelligence'."""
        desc = analyst_node_yaml.get("description", "")
        assert "Business Intelligence" not in desc, (
            f"analyst node.yaml description must not describe BI: {desc}"
        )
        assert "Data Analyst" not in desc, (
            f"analyst node.yaml description must not describe Data Analyst: {desc}"
        )

    def test_required_sections_are_requirements_not_research(
        self, analyst_node_yaml: dict[str, Any]
    ) -> None:
        """FAIL before fix: required_sections includes data_sources, analysis_methodology."""
        sections = analyst_node_yaml.get("deliverable", {}).get("required_sections", [])
        forbidden = {"data_sources", "analysis_methodology", "findings", "recommendations", "limitations"}
        overlap = set(sections) & forbidden
        assert not overlap, (
            f"analyst required_sections must not contain research-oriented sections: {overlap}"
        )

        required = {"objective_and_scope", "functional_requirements", "acceptance_criteria"}
        missing = required - set(sections)
        assert not missing, (
            f"analyst required_sections missing requirements-oriented sections: {missing}"
        )

    def test_task_description_is_requirements_analysis(
        self, analyst_node_yaml: dict[str, Any]
    ) -> None:
        """FAIL before fix: task.description is Data Analyst/BI oriented."""
        task = analyst_node_yaml.get("task", {})
        task_desc = task.get("description", "")
        assert "需求分析" in task_desc or "Requirements Analysis" in task_desc or "Context Clarification" in task_desc, (
            f"analyst task description must describe requirements analysis, got: {task_desc}"
        )


class TestAnalystPersonaContract:
    """T1.4-T1.5: persona.json must describe requirements analyst, not BI."""

    @pytest.fixture
    def analyst_persona(self, repo_root: Path) -> dict[str, Any]:
        path = repo_root / "autoBMAD" / "nodes" / "analyst" / "persona.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_role_is_not_bi(self, analyst_persona: dict[str, Any]) -> None:
        """FAIL before fix: role = 'Data Analyst & Business Intelligence Specialist'."""
        role = analyst_persona.get("role", "")
        assert "Business Intelligence" not in role, (
            f"analyst persona role must not be BI: {role}"
        )
        assert "需求分析" in role or "Requirements Analysis" in role or "Context Clarification" in role, (
            f"analyst persona role must describe requirements analysis: {role}"
        )

    def test_expertise_not_bi_oriented(self, analyst_persona: dict[str, Any]) -> None:
        """FAIL before fix: expertise contains Statistical analysis, BI reporting, etc."""
        expertise = analyst_persona.get("expertise", [])
        bi_keywords = ["Statistical", "Business intelligence", "Trend identification", "Data quality"]
        matched = [e for e in expertise if any(kw in e for kw in bi_keywords)]
        assert len(matched) <= 1, (
            f"analyst expertise must not be BI-oriented. Found: {matched}"
        )


class TestAnalystEvaluatorContract:
    """T1.6: evaluator.yaml criteria must be requirements-oriented."""

    @pytest.fixture
    def analyst_evaluator(self, repo_root: Path) -> dict[str, Any]:
        path = repo_root / "autoBMAD" / "nodes" / "analyst" / "evaluator.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_criteria_are_requirements_oriented(
        self, analyst_evaluator: dict[str, Any]
    ) -> None:
        """FAIL before fix: top weights are evidence_quality=0.40, actionability=0.30."""
        criteria = analyst_evaluator.get("criteria", [])
        names = [c.get("name") for c in criteria]

        assert "evidence_quality" not in names, (
            "analyst evaluator must not use 'evidence_quality' as primary criterion"
        )

        required_criteria = {"requirement_alignment", "traceability", "scope_control"}
        actual = set(names) & required_criteria
        assert len(actual) >= 2, (
            f"analyst evaluator must have at least 2 requirements-oriented criteria, got: {names}"
        )


class TestAnalystTemplateContract:
    """T1.7-T1.8: analyst_templates.yaml must have requirements_analysis as default."""

    @pytest.fixture
    def analyst_templates(self, repo_root: Path) -> dict[str, Any]:
        path = repo_root / "autoBMAD" / "docuswarm" / "templates" / "analyst_templates.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_first_template_is_not_market_research(
        self, analyst_templates: dict[str, Any]
    ) -> None:
        """FAIL before fix: first template is market_research."""
        templates = analyst_templates.get("templates", [])
        assert len(templates) > 0, "analyst_templates.yaml must have at least one template"
        first_id = templates[0].get("template_id", "")
        assert first_id != "market_research", (
            f"first analyst template must not be market_research, got: {first_id}"
        )
        assert "requirements" in first_id or "analysis" in first_id, (
            f"first analyst template should be requirements-oriented, got: {first_id}"
        )

    def test_no_template_has_market_sections(
        self, analyst_templates: dict[str, Any]
    ) -> None:
        """FAIL before fix: market_research template contains Market Overview sections."""
        templates = analyst_templates.get("templates", [])
        for t in templates:
            sections = [s.get("heading", "") for s in t.get("sections", [])]
            forbidden = {"Market Overview", "Competitive Landscape", "Target Segments", "Market Opportunities"}
            overlap = set(sections) & forbidden
            assert not overlap, (
                f"template '{t.get('template_id')}' contains market research sections: {overlap}"
            )


class TestAnalystPromptContractRendering:
    """T1.9-T1.10: Rendered prompts must contain requirements analysis language."""

    @pytest.fixture
    def calc_context_summary(self) -> str:
        return (
            "Create a minimal Python CLI that calculates 1+1. "
            "This is a pipeline validation task for DocuSwarm."
        )

    @pytest.fixture
    def contract_builder(self) -> Any:
        from autoBMAD.docuswarm.prompts.contract_builder import create_contract_builder
        return create_contract_builder()

    def test_rendered_system_prompt_no_market_terms(
        self,
        contract_builder: Any,
        calc_context_summary: str,
        fake_node_config: Any,
    ) -> None:
        """FAIL before fix: system prompt contains 'Business Intelligence' / 'market research'."""
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext

        context: NodeExecutionContext = {
            "pipeline_id": "test-pipe",
            "node_id": "analyst",
            "node_name": "Analyst",
            "node_order": 0,
            "original_context": {"content": calc_context_summary},
            "chained_deliverables": [],
            "shared_context": {},
            "docs_context": [],
            "deliverable_requirements": {},
            "deliverable_type": "analyst-report",
        }
        contract = contract_builder.build_independent_contract(context)
        system_prompt = contract_builder.render_independent_system_prompt(contract)

        forbidden_terms = ["Business Intelligence", "market research", "Competitive Landscape"]
        for term in forbidden_terms:
            assert term.lower() not in system_prompt.lower(), (
                f"analyst system_prompt must not contain '{term}'"
            )

    def test_rendered_user_prompt_has_requirements_terms(
        self,
        contract_builder: Any,
        calc_context_summary: str,
        fake_node_config: Any,
    ) -> None:
        """FAIL before fix: user prompt lacks functional_requirements / acceptance_criteria."""
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext

        context: NodeExecutionContext = {
            "pipeline_id": "test-pipe",
            "node_id": "analyst",
            "node_name": "Analyst",
            "node_order": 0,
            "original_context": {"content": calc_context_summary},
            "chained_deliverables": [],
            "shared_context": {},
            "docs_context": [],
            "deliverable_requirements": {},
            "deliverable_type": "analyst-report",
        }
        contract = contract_builder.build_independent_contract(context)
        user_prompt = contract_builder.render_independent_user_prompt(contract)

        required_terms = ["functional", "requirement", "acceptance", "scope"]
        found = [t for t in required_terms if t.lower() in user_prompt.lower()]
        assert len(found) >= 2, (
            f"analyst user_prompt must contain requirements-oriented terms, found: {found}"
        )


class TestTemplateFallbackSafety:
    """T1.11: _find_best_template_match must not blindly return templates[0]."""

    def test_fallback_returns_none_when_no_match(
        self, contract_builder: Any
    ) -> None:
        """FAIL before fix: _find_best_template_match returns templates[0] even for unrelated id."""
        # Access private method for safety testing
        result = contract_builder._find_best_template_match(
            "completely_unrelated_xyz", []
        )
        assert result is None, (
            "_find_best_template_match with empty templates must return None, "
            f"got: {result}"
        )

    def test_fallback_with_mismatched_node_role(
        self, contract_builder: Any
    ) -> None:
        """FAIL before fix: returns market_research for 'requirements_analysis' lookup."""
        templates = [
            {"template_id": "market_research", "title": "Market Research"},
            {"template_id": "risk_assessment", "title": "Risk Assessment"},
        ]
        result = contract_builder._find_best_template_match(
            "requirements_analysis", templates
        )
        # After fix: should return None or a requirements-oriented template
        if result is not None:
            assert result.get("template_id") != "market_research", (
                "fallback must not return market_research for requirements_analysis lookup"
            )
```

### 2.4 最小生产代码修复

按以下顺序修改文件，每修改一个文件后运行对应测试：

1. **`autoBMAD/nodes/analyst/node.yaml`**
   - `description`: 改为 `"业务需求分析与上下文澄清专家"`
   - `task.description`: 改为 `"Business Requirements Analysis & Context Clarification Specialist"`
   - `deliverable.required_sections`: 替换为 `[objective_and_scope, stakeholders_or_users, functional_requirements, non_functional_constraints, acceptance_criteria, pipeline_validation_risks, downstream_guidance]`

2. **`autoBMAD/nodes/analyst/persona.json`**
   - `role`: 改为 `"Business Requirements Analysis & Context Clarification Specialist"`
   - `identity`: 改为聚焦需求分析、上下文澄清、验收标准定义
   - `expertise`: 替换为 `["需求分析与上下文澄清", "业务目标与范围定义", "功能需求梳理", "验收标准制定", "非功能约束记录", "下游节点输入指导", "流水线验证风险识别"]`

3. **`autoBMAD/nodes/analyst/evaluator.yaml`**
   - `criteria`: 替换为 5 条 requirements-oriented criteria（requirement_alignment=0.30, traceability=0.25, scope_control=0.20, downstream_usefulness=0.15, clarity=0.10）

4. **`autoBMAD/docuswarm/templates/analyst_templates.yaml`**
   - 将 `requirements_analysis` 模板移到第一位
   - `requirements_analysis` 模板 sections: `[Objective and Scope, Stakeholders and Users, Functional Requirements, Non-Functional Constraints, Acceptance Criteria, Pipeline Validation Risks, Downstream Guidance]`

5. **`autoBMAD/docuswarm/prompts/contract_builder.py`**
   - `_find_best_template_match()`: 当无匹配时返回 `None`（而非 `templates[0]`）
   - `_load_node_template()`: 当 `_find_best_template_match` 返回 `None` 时，回退到 `required_sections` 而非强制使用第一个模板

---

## 3. P0-2: ResultMessage 完成语义

### 3.1 测试文件

**文件**: `tests/test_docuswarm_p0_result_message_semantic.py`

### 3.2 测试设计哲学

使用 fake SDK client 模拟消息流，验证：
1. `prompt()` 在 `ResultMessage` 后正确结束
2. idle watchdog 不会被正常完成触发
3. 没有 `ResultMessage` 的流仍会被 idle watchdog 正确捕获

### 3.3 失败测试代码

```python
"""P0-2: ClaudeSessionWrapper.prompt() must treat ResultMessage as turn-complete signal.

Before fix: prompt() waits for IDLE_TIMEOUT after ResultMessage → test FAIL.
After fix:  prompt() breaks immediately after ResultMessage → test PASS.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Fake SDK types for controlled testing (no real SDK calls)
# ---------------------------------------------------------------------------

class FakeAssistantMessage:
    role = "assistant"
    def __init__(self, content: str = "hello") -> None:
        self.content = [{"type": "text", "text": content}]

class FakeUserMessage:
    role = "user"
    def __init__(self, content: str = "tool result") -> None:
        self.content = content

class FakeResultMessage:
    """Simulates claude_agent_sdk.ResultMessage."""
    def __init__(self, result: str = "success") -> None:
        self.result = result
        self.is_error = False


class FakeSDKClient:
    """Fake client that yields a controlled message sequence."""

    def __init__(self, messages: list[Any], delay: float = 0.01) -> None:
        self._messages = messages
        self._delay = delay
        self._idx = 0

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def query(self, message: str) -> None:
        self._idx = 0

    async def receive_messages(self) -> AsyncIterator[Any]:
        while self._idx < len(self._messages):
            await asyncio.sleep(self._delay)
            msg = self._messages[self._idx]
            self._idx += 1
            yield msg
        # No StopAsyncIteration needed — generator naturally ends


# ---------------------------------------------------------------------------
# T2: ResultMessage termination tests
# ---------------------------------------------------------------------------

class TestResultMessageEndsPromptStream:
    """T2.1-T2.3: prompt() must end when ResultMessage is received."""

    @pytest.fixture
    def fake_result_message_client(self) -> FakeSDKClient:
        """Normal turn: Assistant -> User(tool_result) -> ResultMessage."""
        return FakeSDKClient([
            FakeAssistantMessage("I'll create the deliverable"),
            FakeUserMessage("tool result"),
            FakeAssistantMessage("Done"),
            FakeResultMessage(),
        ], delay=0.01)

    @pytest.mark.asyncio
    async def test_prompt_ends_after_result_message(self, fake_result_message_client: FakeSDKClient) -> None:
        """FAIL before fix: prompt() hangs until IDLE_TIMEOUT (300s) after ResultMessage."""
        from pathlib import Path
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper

        wrapper = ClaudeSessionWrapper(
            client=fake_result_message_client,
            session_id="test-session",
            work_dir=Path("/tmp"),
        )
        # Override IDLE_TIMEOUT to something small for test speed
        wrapper.IDLE_TIMEOUT = 1

        messages = []
        start = asyncio.get_event_loop().time()
        async for msg in wrapper.prompt("test message"):
            messages.append(msg)
        elapsed = asyncio.get_event_loop().time() - start

        # Must complete well before IDLE_TIMEOUT
        assert elapsed < wrapper.IDLE_TIMEOUT * 0.5, (
            f"prompt() took {elapsed:.1f}s, should end immediately after ResultMessage, "
            f"not wait for IDLE_TIMEOUT={wrapper.IDLE_TIMEOUT}s"
        )

        # Must have yielded all messages including ResultMessage
        assert len(messages) == 4, f"Expected 4 messages, got {len(messages)}"
        assert isinstance(messages[-1], FakeResultMessage), (
            f"Last message must be ResultMessage, got {type(messages[-1])}"
        )

    @pytest.mark.asyncio
    async def test_prompt_does_not_log_idle_exceeded_on_normal_completion(self) -> None:
        """FAIL before fix: 'prompt_idle_exceeded' is logged even on normal completion."""
        from pathlib import Path
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        import structlog

        log_records: list[dict[str, Any]] = []

        def capture_log(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
            log_records.append(event_dict)
            return event_dict

        structlog.configure(processors=[capture_log, structlog.dev.ConsoleRenderer()])

        client = FakeSDKClient([
            FakeAssistantMessage("step 1"),
            FakeResultMessage(),
        ], delay=0.01)

        wrapper = ClaudeSessionWrapper(
            client=client,
            session_id="test-session-2",
            work_dir=Path("/tmp"),
        )
        wrapper.IDLE_TIMEOUT = 1

        async for _ in wrapper.prompt("test"):
            pass

        idle_events = [r for r in log_records if r.get("event") == "prompt_idle_exceeded"]
        assert len(idle_events) == 0, (
            f"Must not log 'prompt_idle_exceeded' on normal ResultMessage completion, "
            f"but found {len(idle_events)} events"
        )

    @pytest.mark.asyncio
    async def test_prompt_without_result_message_triggers_idle_watchdog(self) -> None:
        """PASS before and after fix: stream without ResultMessage must trigger idle timeout."""
        from pathlib import Path
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper, LLMError

        # Stream that never sends ResultMessage
        client = FakeSDKClient([
            FakeAssistantMessage("step 1"),
        ], delay=0.01)

        wrapper = ClaudeSessionWrapper(
            client=client,
            session_id="test-session-3",
            work_dir=Path("/tmp"),
        )
        wrapper.IDLE_TIMEOUT = 0.5  # Short for test speed

        with pytest.raises(LLMError) as exc_info:
            async for _ in wrapper.prompt("test"):
                pass

        assert "idle" in str(exc_info.value).lower() or "Transport" in str(exc_info.value), (
            f"Expected idle timeout error, got: {exc_info.value}"
        )


class TestIndependentAgentHandlesResultMessageGracefully:
    """T2.4: IndependentAgent must not treat ResultMessage completion as error."""

    @pytest.mark.asyncio
    async def test_call_llm_returns_messages_without_error_on_result_message(self) -> None:
        """FAIL before fix: _call_llm_with_prompts logs llm_call_error due to idle timeout."""
        from unittest.mock import AsyncMock, patch
        from pathlib import Path
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        # Patch SessionManager.create_session to return a wrapper with our fake client
        fake_client = FakeSDKClient([
            FakeAssistantMessage("I'll analyze"),
            FakeResultMessage(),
        ], delay=0.01)

        # We test at the IndependentAgent level by mocking the session
        from autoBMAD.docuswarm.agents.independent import IndependentAgent

        mock_sm = MagicMock(spec=SessionManager)
        mock_wrapper = MagicMock()

        async def fake_prompt_stream(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
            for msg in fake_client._messages:
                yield msg

        mock_wrapper.prompt = fake_prompt_stream
        mock_sm.create_session = AsyncMock(return_value=mock_wrapper)

        config = MagicMock()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="analyst",
            project_root=Path(__file__).parent.parent.resolve(),
        )

        # This should complete without raising LLMCallError
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="You are a requirements analyst.",
            user_prompt="Analyze this context.",
        )

        # Must return at least one assistant message
        assert len(messages) > 0, "IndependentAgent must return messages on normal completion"
        assert not any("error" in str(m) for m in messages), (
            "Messages must not contain error indicators"
        )
```

### 3.4 最小生产代码修复

修改文件: **`autoBMAD/docuswarm/llm/session_manager.py`**

在 `ClaudeSessionWrapper.prompt()` 的 while 循环中（约 line 1226-1239），在 `yield msg` 之前增加：

```python
# After: last_msg_at = asyncio.get_event_loop().time()
# After: messages_received += 1
# ADD:
if isinstance(msg, ResultMessage):
    self._logger.info(
        "prompt_result_received",
        result=getattr(msg, "result", None),
        messages_received=messages_received,
    )
    yield msg
    break
# existing: yield msg
```

同时确保 `ResultMessage` 被 yield 后，caller (`_call_llm_with_prompts()`) 能正确处理：
- `sm._message_to_dict()` 返回 `None` 对 `ResultMessage` —— 这是当前行为，保持不变
- `IndependentAgent._call_llm_with_prompts()` 的异常处理保留，因为真正无消息的情况仍需报错

---

## 4. P1-1: BLOCKED/NEEDS_REVISION 策略

### 4.1 测试文件

**文件**: `tests/test_docuswarm_p1_verdict_iteration_consistency.py`

### 4.2 测试设计哲学

通过 mock 控制 `IndependentAgent` 和 `EvaluatorAgent` 的输出，验证：
1. Evaluator 返回 `NEEDS_REVISION` 时，DualAgentNode 不应将其覆写为 `BLOCKED`
2. `node_iterations` 计数与实际执行轮次一致
3. 达到 `max_iterations` 仍未通过时，行为符合策略文档

### 4.3 失败测试代码

```python
"""P1-1: Verdict and iteration consistency — TDD failing tests.

Before fix:
- Evaluator returns NEEDS_REVISION but DualAgentNode records BLOCKED
- node_iterations shows 3 while actual execution is 1 round
After fix:
- Verdict is preserved through the pipeline
- node_iterations matches actual rounds executed
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestVerdictPreservation:
    """T3.1-T3.3: Evaluator verdict must not be silently overridden."""

    @pytest.fixture
    def mock_evaluator_needs_revision(self) -> AsyncMock:
        """Evaluator that always returns NEEDS_REVISION."""
        async def evaluate(*args: Any, **kwargs: Any) -> dict[str, Any]:
            return {
                "criterion_scores": {"completeness": 0.5},
                "alignment_score": 0.5,
                "verdict": "NEEDS_REVISION",
                "issues_found": ["needs more detail"],
                "suggestions": ["add examples"],
            }
        return AsyncMock(side_effect=evaluate)

    @pytest.fixture
    def mock_independent_agent(self) -> AsyncMock:
        """Independent agent that returns a basic deliverable."""
        call_count = 0
        async def execute(*args: Any, **kwargs: Any) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            return {
                "deliverable": {
                    "title": f"test-deliverable-v{call_count}",
                    "content": f"Content v{call_count}",
                },
                "questions": [],
                "action": "create_deliverable",
            }
        return AsyncMock(side_effect=execute)

    @pytest.mark.asyncio
    async def test_needs_revision_is_not_overridden_to_blocked(
        self,
        mock_independent_agent: AsyncMock,
        mock_evaluator_needs_revision: AsyncMock,
    ) -> None:
        """FAIL before fix: DualAgentNode converts NEEDS_REVISION to BLOCKED."""
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        config = MagicMock()
        config.agent_timeout = 300

        node = DualAgentNode(
            config=config,
            independent_agent=mock_independent_agent,
            evaluator_agent=MagicMock(execute_with_input=mock_evaluator_needs_revision),
            node_id="analyst",
            max_iterations=3,
        )

        # Build a minimal execution context
        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
        context: NodeExecutionContext = {
            "pipeline_id": "test-pipe",
            "node_id": "analyst",
            "node_name": "Analyst",
            "node_order": 0,
            "original_context": {"content": "test context"},
            "chained_deliverables": [],
            "shared_context": {},
            "docs_context": [],
            "deliverable_requirements": {},
            "deliverable_type": "analyst-report",
        }

        result = await node.execute_with_context(context)

        # With NEEDS_REVISION and max_iterations=3, it should iterate until max
        # But the verdict in the final evaluation must be NEEDS_REVISION, not BLOCKED
        assert result.evaluation.get("verdict") == "NEEDS_REVISION", (
            f"Evaluator returned NEEDS_REVISION but DualAgentNode result has "
            f"verdict={result.evaluation.get('verdict')}. "
            f"Verdict must not be overridden."
        )

    @pytest.mark.asyncio
    async def test_blocked_is_terminal_and_does_not_iterate(
        self,
        mock_independent_agent: AsyncMock,
    ) -> None:
        """PASS before and after fix: BLOCKED verdict must break immediately."""
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode

        async def blocked_evaluate(*args: Any, **kwargs: Any) -> dict[str, Any]:
            return {
                "alignment_score": 0.2,
                "verdict": "BLOCKED",
                "issues_found": ["critical security violation"],
                "suggestions": [],
            }

        config = MagicMock()
        config.agent_timeout = 300

        node = DualAgentNode(
            config=config,
            independent_agent=mock_independent_agent,
            evaluator_agent=MagicMock(execute_with_input=AsyncMock(side_effect=blocked_evaluate)),
            node_id="analyst",
            max_iterations=3,
        )

        from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
        context: NodeExecutionContext = {
            "pipeline_id": "test-pipe",
            "node_id": "analyst",
            "node_name": "Analyst",
            "node_order": 0,
            "original_context": {"content": "test"},
            "chained_deliverables": [],
            "shared_context": {},
            "docs_context": [],
            "deliverable_requirements": {},
            "deliverable_type": "analyst-report",
        }

        result = await node.execute_with_context(context)

        # BLOCKED should stop at iteration 1
        assert result.iteration == 1, (
            f"BLOCKED must stop at iteration 1, got {result.iteration}"
        )
        assert result.evaluation.get("verdict") == "BLOCKED"
        # Independent agent should only be called once
        assert mock_independent_agent.call_count == 1, (
            f"Independent agent called {mock_independent_agent.call_count} times, expected 1"
        )


class TestIterationCountConsistency:
    """T3.4-T3.5: node_iterations must match actual execution rounds."""

    @pytest.mark.asyncio
    async def test_node_iterations_matches_actual_rounds(self) -> None:
        """FAIL before fix: pipeline state shows node_iterations=3 for 1-round execution."""
        from autoBMAD.docuswarm.pipeline.graph import _create_integrated_node_executor
        from autoBMAD.docuswarm.pipeline.state import create_initial_state
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        mock_session = MagicMock(spec=SessionManager)

        async def fake_executor(state: dict[str, Any]) -> dict[str, Any]:
            """Simulates a blocked node after 1 dual-agent iteration."""
            new_state = dict(state)
            new_state["deliverable"] = {"title": "test"}
            new_state["evaluation"] = {"verdict": "BLOCKED", "alignment_score": 0.3}
            new_state["questions"] = []
            # NodeRunState iteration should be 1 (only 1 round executed)
            new_state["iteration"] = 1
            new_state["status"] = "blocked"
            return new_state

        with patch(
            "autoBMAD.docuswarm.node_execution.executor.create_node_executor",
            return_value=fake_executor,
        ):
            executor = _create_integrated_node_executor("analyst", mock_session)
            state = create_initial_state("test-pipe", {"content": "calc 1+1"})
            result = await executor(state)

            # After fix: node_iterations['analyst'] should be 1
            assert result["node_iterations"].get("analyst") == 1, (
                f"node_iterations['analyst'] must be 1 for single-round execution, "
                f"got {result['node_iterations'].get('analyst')}"
            )

    @pytest.mark.asyncio
    async def test_needs_revision_iterations_accumulate_correctly(self) -> None:
        """FAIL before fix: iteration count is wrong for multi-round NEEDS_REVISION."""
        from autoBMAD.docuswarm.pipeline.graph import _create_integrated_node_executor
        from autoBMAD.docuswarm.pipeline.state import create_initial_state
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        mock_session = MagicMock(spec=SessionManager)
        execution_count = 0

        async def fake_executor(state: dict[str, Any]) -> dict[str, Any]:
            nonlocal execution_count
            execution_count += 1
            new_state = dict(state)
            new_state["deliverable"] = {"title": f"v{execution_count}"}
            new_state["evaluation"] = {
                "verdict": "NEEDS_REVISION" if execution_count < 2 else "APPROVED",
                "alignment_score": 0.5 if execution_count < 2 else 0.9,
            }
            new_state["questions"] = []
            new_state["iteration"] = execution_count
            new_state["status"] = "completed"
            return new_state

        with patch(
            "autoBMAD.docuswarm.node_execution.executor.create_node_executor",
            return_value=fake_executor,
        ):
            executor = _create_integrated_node_executor("analyst", mock_session)
            state = create_initial_state("test-pipe", {"content": "calc 1+1"})
            result = await executor(state)

            # After fix: should reflect actual rounds executed by the node executor
            assert result["node_iterations"].get("analyst") == execution_count, (
                f"node_iterations must equal actual execution rounds ({execution_count}), "
                f"got {result['node_iterations'].get('analyst')}"
            )
            assert result["completed_nodes"] == ["analyst"], (
                f"APPROVED node must be in completed_nodes"
            )
```

### 4.4 最小生产代码修复

1. **`autoBMAD/docuswarm/nodes/dual_agent.py`**
   - 在 `execute_with_context()` 中，当 `verdict == "NEEDS_REVISION"` 时，确保 feedback 被正确传递且迭代继续
   - 审查 `EvaluatorAgent.execute_with_input()` 是否有 threshold-based verdict override 逻辑，如有则移除或使其可配置
   - 确保 `NodeResult.iteration` 返回的是实际执行的轮次

2. **`autoBMAD/docuswarm/node_execution/pipeline_adapter.py`**
   - `convert_node_to_pipeline_state()`: 直接使用 `node_state.get("iteration", 1)`，不做额外增量
   - 移除或修正可能导致 iteration 被错误增量的逻辑

3. **`autoBMAD/docuswarm/pipeline/graph.py`**
   - `_create_integrated_node_executor()`: `current_iteration + 1` 增量应在确认 node 成功执行后执行，且不应与 node 内部计数冲突
   - 考虑使用 `node_state.get("iteration")` 直接覆盖而非增量

---

## 5. P1-2: 路径语义漂移

### 5.1 测试文件

**文件**: `tests/test_docuswarm_p1_path_semantic_drift.py`

### 5.2 测试设计哲学

通过传入不同路径组合，验证：
1. `create_dual_agent_node()` 解析的 `agent_file` 始终指向有效路径
2. `SessionManager` 的 `cwd` 和 `output_dir` 可以被独立控制
3. 四个路径概念在日志/状态中可被区分

### 5.3 失败测试代码

```python
"""P1-2: Path semantic drift — TDD failing tests.

Before fix:
- cwd defaults to shell cwd (e.g. /home/leafliu)
- agent_file lacks package directory when repo_root is passed
- project_root string matching is fragile
After fix:
- Four path concepts are explicit and correct
- agent_file resolves correctly regardless of repo_root vs package_root
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


class TestCreateDualAgentNodePathResolution:
    """T4.1-T4.2: create_dual_agent_node must resolve paths correctly."""

    def test_agent_file_exists_when_repo_root_passed(self, repo_root: Path) -> None:
        """FAIL before fix: agent_file path is missing autoBMAD/ package dir."""
        from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        session_manager = MagicMock(spec=SessionManager)
        config = MagicMock()
        config.agent_timeout = 300

        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id="analyst",
            project_root=repo_root,  # repo root = /home/leafliu/autoBMAD
        )

        agent_file = node.independent_agent._agent_file
        assert agent_file is not None, "agent_file must not be None"
        assert agent_file.exists(), (
            f"agent_file must exist: {agent_file}. "
            f"If repo_root={repo_root} was passed, the path should resolve to "
            f"repo_root / 'autoBMAD' / 'docuswarm' / 'agents' / 'configs' / 'independent_agent.yaml'"
        )

    def test_agent_file_exists_when_package_root_passed(self, autoBMAD_root: Path) -> None:
        """FAIL before fix: agent_file path has extra autoBMAD/ dir when package_root passed."""
        from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        session_manager = MagicMock(spec=SessionManager)
        config = MagicMock()
        config.agent_timeout = 300

        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id="analyst",
            project_root=autoBMAD_root,  # package root = /home/leafliu/autoBMAD/autoBMAD
        )

        agent_file = node.independent_agent._agent_file
        assert agent_file is not None, "agent_file must not be None"
        assert agent_file.exists(), (
            f"agent_file must exist when package_root={autoBMAD_root} is passed: {agent_file}"
        )


class TestSessionManagerPathSemantics:
    """T4.3-T4.4: SessionManager must distinguish cwd from output_dir."""

    def test_cwd_and_output_dir_are_independent(self, repo_root: Path) -> None:
        """FAIL before fix: SessionManager cwd and output_dir are conflated."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager

        output_dir = repo_root / "output" / "test-pipeline"
        output_dir.mkdir(parents=True, exist_ok=True)

        sm = SessionManager(
            cwd=repo_root,
            output_dir=output_dir,
        )

        assert sm.cwd == repo_root, f"cwd must be {repo_root}, got {sm.cwd}"
        assert sm.output_dir == output_dir, (
            f"output_dir must be {output_dir}, got {sm.output_dir}"
        )

    def test_session_manager_logs_four_path_concepts(self, repo_root: Path, caplog: Any) -> None:
        """FAIL before fix: logs only show 'cwd', not repo_root/package_root/sdk_cwd/output_dir."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        import structlog
        import logging

        # Configure structlog to capture logs
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        output_dir = repo_root / "output" / "test-pipe"
        output_dir.mkdir(parents=True, exist_ok=True)

        with caplog.at_level(logging.DEBUG):
            sm = SessionManager(
                cwd=repo_root,
                output_dir=output_dir,
                pipeline_id="test-pipe",
            )
            # Force a log by creating a session (with mock client if needed)
            # Just check the init logs for now
            logs = caplog.text

        # After fix: logs should contain explicit path fields
        assert "repo_root" in logs or "package_root" in logs or str(repo_root) in logs, (
            "SessionManager logs must include path resolution details for debugging"
        )


class TestIndependentAgentBuildAgentFilePath:
    """T4.5: _build_agent_file_path must use path existence, not string matching."""

    def test_build_agent_file_path_does_not_use_name_string_matching(
        self, repo_root: Path
    ) -> None:
        """FAIL before fix: _build_agent_file_path uses project_root.name == 'autoBMAD'."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        import inspect

        source = inspect.getsource(IndependentAgent._build_agent_file_path)
        assert '.name == "autoBMAD"' not in source, (
            "_build_agent_file_path must not use fragile string matching on project_root.name"
        )
        assert "Path.exists()" in source or ".exists()" in source, (
            "_build_agent_file_path should verify path existence rather than assuming structure"
        )
```

### 5.4 最小生产代码修复

1. **`autoBMAD/docuswarm/agents/independent.py`**
   - `_build_agent_file_path()`: 移除 `project_root.name == "autoBMAD"` 字符串匹配
   - 改为：先尝试 `project_root / "autoBMAD" / "docuswarm" / ...`，如果 `exists()` 则返回；否则尝试 `project_root / "docuswarm" / ...`

2. **`autoBMAD/docuswarm/llm/session_manager.py`**
   - `__init__`: 在日志中输出 `repo_root`, `package_root`, `sdk_cwd`, `output_dir`
   - 明确文档化四个路径概念
   - `work_dir` deprecated 路径：增加 `warnings.warn("work_dir is deprecated, use cwd and output_dir", DeprecationWarning)`

---

## 6. 端到端回归验证

### 6.1 测试文件

**文件**: `tests/test_docuswarm_p0_calc_regression.py`

### 6.2 测试设计

使用完全 mock 的 LLM 响应，模拟 calc-context 场景，验证：
1. Pipeline 能正确识别 analyst 节点的需求分析角色
2. 不需要等待 idle timeout
3. 迭代计数正确
4. 路径解析正确

```python
"""P0-Regression: End-to-end calc-one-plus-one scenario with mock LLM.

This test simulates the exact calc-context.md scenario without calling real LLM.
All four fixes (P0-1, P0-2, P1-1, P1-2) must be in place for this to pass.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.docuswarm.llm.session_manager import SessionManager
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
from autoBMAD.docuswarm.pipeline.state import create_initial_state


CALC_CONTEXT = {
    "subject": "calc-context",
    "content": (
        "# Python CLI: 计算 1+1\n\n"
        "## Subject\n创建极简 Python CLI 计算 1+1。\n\n"
        "## Functional Requirements\n"
        "1. 执行 1+1 输出到标准输出\n"
        "2. 支持 python calc.py 直接运行\n"
        "3. 输出格式: 1 + 1 = 2\n\n"
        "## Success Criteria\n"
        "流水线运行成功：analyst完成需求分析，PM产出PRD，UX给出设计说明..."
    ),
}


class TestCalcOnePlusOneRegression:
    """Regression: calc-one-plus-one pipeline must complete without idle timeout."""

    @pytest.fixture
    def mock_llm_responses(self) -> dict[str, dict[str, Any]]:
        """Mock responses for each pipeline node."""
        return {
            "analyst": {
                "deliverable": {
                    "title": "requirements-analysis",
                    "content": "## Objective and Scope\nValidate DocuSwarm pipeline...",
                },
                "questions": [],
                "action": "create_deliverable",
            },
            "pm": {
                "deliverable": {"title": "prd", "content": "## PRD\n..."},
                "questions": [],
                "action": "create_deliverable",
            },
            "ux": {
                "deliverable": {"title": "ux-design", "content": "## UX\n..."},
                "questions": [],
                "action": "create_deliverable",
            },
            "architect": {
                "deliverable": {"title": "architecture", "content": "## Arch\n..."},
                "questions": [],
                "action": "create_deliverable",
            },
            "po": {
                "deliverable": {"title": "backlog", "content": "## Backlog\n..."},
                "questions": [],
                "action": "create_deliverable",
            },
        }

    @pytest.fixture
    def mock_evaluations(self) -> dict[str, dict[str, Any]]:
        """Mock evaluations: all APPROVED."""
        return {
            node_id: {
                "alignment_score": 0.85,
                "verdict": "APPROVED",
                "issues_found": [],
                "suggestions": [],
            }
            for node_id in ["analyst", "pm", "ux", "architect", "po"]
        }

    @pytest.mark.asyncio
    async def test_calc_pipeline_completes_all_nodes(
        self,
        mock_llm_responses: dict[str, dict[str, Any]],
        mock_evaluations: dict[str, dict[str, Any]],
    ) -> None:
        """FAIL before fixes: pipeline blocks at analyst or times out."""

        def fake_create_node_executor(node_id: str, session_manager: Any) -> Any:
            async def executor(state: dict[str, Any]) -> dict[str, Any]:
                new_state = dict(state)
                new_state["deliverable"] = mock_llm_responses[node_id]["deliverable"]
                new_state["questions"] = mock_llm_responses[node_id]["questions"]
                new_state["evaluation"] = mock_evaluations[node_id]
                new_state["status"] = "completed"
                # iteration should reflect actual rounds (1 for APPROVED)
                new_state["iteration"] = 1
                return new_state
            return executor

        mock_session = MagicMock(spec=SessionManager)

        with patch(
            "autoBMAD.docuswarm.node_execution.executor.create_node_executor",
            side_effect=fake_create_node_executor,
        ):
            graph = create_pipeline_graph(
                compile_graph=True,
                session_manager=mock_session,
            )
            state = create_initial_state("calc-regression", CALC_CONTEXT)
            result = await graph.ainvoke(
                state,
                {"configurable": {"thread_id": "calc-regression"}},
            )

            # All nodes should complete
            expected_nodes = ["analyst", "pm", "ux", "architect", "po"]
            for node_id in expected_nodes:
                assert node_id in result.get("completed_nodes", []), (
                    f"Node {node_id} must be in completed_nodes"
                )
                assert node_id in result.get("deliverables", {}), (
                    f"Node {node_id} must have a deliverable"
                )
                assert result["node_iterations"].get(node_id) == 1, (
                    f"Node {node_id} should execute exactly 1 iteration"
                )

            assert result.get("status") != "failed", (
                f"Pipeline must not fail. Error: {result.get('error')}"
            )
```

---

## 7. 附录：共享 Fixtures

如果 `conftest.py` 中尚缺以下 fixtures，请补充：

```python
@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def autoBMAD_root(repo_root: Path) -> Path:
    """Return the autoBMAD package root."""
    return repo_root / "autoBMAD"


@pytest.fixture
def contract_builder() -> Any:
    """Return a NodePromptContractBuilder instance."""
    from autoBMAD.docuswarm.prompts.contract_builder import create_contract_builder
    return create_contract_builder()
```

---

## 快速参考：测试 → 修复 映射表

| 测试文件 | 测试类 | 对应修复文件 | 预期修复前状态 |
|---------|--------|-------------|--------------|
| `test_docuswarm_p0_analyst_contract_drift.py` | `TestAnalystNodeYamlContract` | `autoBMAD/nodes/analyst/node.yaml` | FAIL |
| `test_docuswarm_p0_analyst_contract_drift.py` | `TestAnalystPersonaContract` | `autoBMAD/nodes/analyst/persona.json` | FAIL |
| `test_docuswarm_p0_analyst_contract_drift.py` | `TestAnalystEvaluatorContract` | `autoBMAD/nodes/analyst/evaluator.yaml` | FAIL |
| `test_docuswarm_p0_analyst_contract_drift.py` | `TestAnalystTemplateContract` | `autoBMAD/docuswarm/templates/analyst_templates.yaml` | FAIL |
| `test_docuswarm_p0_analyst_contract_drift.py` | `TestTemplateFallbackSafety` | `autoBMAD/docuswarm/prompts/contract_builder.py` | FAIL |
| `test_docuswarm_p0_result_message_semantic.py` | `TestResultMessageEndsPromptStream` | `autoBMAD/docuswarm/llm/session_manager.py` | FAIL |
| `test_docuswarm_p1_verdict_iteration_consistency.py` | `TestVerdictPreservation` | `autoBMAD/docuswarm/nodes/dual_agent.py` | FAIL |
| `test_docuswarm_p1_verdict_iteration_consistency.py` | `TestIterationCountConsistency` | `autoBMAD/docuswarm/pipeline/graph.py`, `pipeline_adapter.py` | FAIL |
| `test_docuswarm_p1_path_semantic_drift.py` | `TestCreateDualAgentNodePathResolution` | `autoBMAD/docuswarm/agents/independent.py` | FAIL |
| `test_docuswarm_p1_path_semantic_drift.py` | `TestSessionManagerPathSemantics` | `autoBMAD/docuswarm/llm/session_manager.py` | FAIL |
| `test_docuswarm_p0_calc_regression.py` | `TestCalcOnePlusOneRegression` | 所有上述文件 | FAIL |

---

*方案生成时间*: 2026-05-01  
*对应研究报告*: `docs-doc/research/2026-05-01-docuswarm-calc-one-plus-one-fix-direction-deep-research.md`
