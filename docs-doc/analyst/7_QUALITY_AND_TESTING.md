# DocuSwarm Quality & Testing Analysis

**Version**: 2.0 (Occam's Razor Simplified)  
**Date**: 2026-02-19  
**Category**: Quality & Testing  
**Topics Covered**: 7.1 - 7.5  
**Status**: Analysis Complete - Simplified

---

## Executive Summary

This analysis covers 5 topics related to quality assurance and testing in DocuSwarm. The focus is on simplified scoring, iteration limits, and pytest-based testing.

**Key Simplifications from Occam's Razor Analysis**:
- Simplified alignment scoring (single threshold approach)
- Fixed iteration limit (max 3) with simple escalation
- Python/pytest testing strategy (not TypeScript/Jest)
- Dual-agent test focus (no Questioner tests)
- Security testing focused on context isolation

**Key Findings**:
- Simple 70% approval threshold is sufficient for MVP quality control
- Max 3 iterations prevents infinite loops while allowing quality improvement
- Context isolation is the primary security concern requiring automated tests
- pytest provides simpler async testing for LangGraph-based code

**Critical Dependencies**: Agent System Design (Section 2) with dual-agent pattern.

**Development Time Savings**: ~2-3 weeks compared to full testing infrastructure.

---

## Topic 7.1: Evaluator Alignment Scoring (Simplified)

### Context

**Occam's Razor Decision**: Simplified scoring with single threshold instead of hybrid rubric system.

### Research Findings

**Scoring Approaches**:

| Approach | Complexity | Accuracy | MVP Fit |
|----------|------------|----------|---------|
| **Pure LLM Judgment** | Low | Variable | Good |
| **Hybrid (70/30)** | Medium | High | Overkill |
| **Simple Threshold** | Low | Good | Excellent |

### Implementation Guidance

**Simplified Alignment Scorer**:

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Verdict(Enum):
    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    BLOCKED = "BLOCKED"

@dataclass
class AlignmentResult:
    alignment_score: float
    verdict: Verdict
    issues: List[str]
    suggestions: List[str]

class SimpleAlignmentScorer:
    """Simplified alignment scoring for MVP."""
    
    # Single threshold approach
    APPROVAL_THRESHOLD = 0.70
    BLOCKED_THRESHOLD = 0.40
    
    def calculate_verdict(self, evaluation: dict) -> AlignmentResult:
        """Calculate verdict from LLM evaluation response."""
        score = evaluation.get("alignment_score", 0.5)
        issues = evaluation.get("issues_found", [])
        suggestions = evaluation.get("suggestions", [])
        
        # Check for critical issues first
        critical_issues = [
            i for i in issues 
            if i.get("severity") == "critical"
        ]
        
        if critical_issues or score < self.BLOCKED_THRESHOLD:
            verdict = Verdict.BLOCKED
        elif score >= self.APPROVAL_THRESHOLD:
            verdict = Verdict.APPROVED
        else:
            verdict = Verdict.NEEDS_REVISION
        
        return AlignmentResult(
            alignment_score=score,
            verdict=verdict,
            issues=[i.get("description", str(i)) for i in issues],
            suggestions=suggestions
        )
```

**Evaluator Prompt (Simplified)**:

```python
EVALUATOR_PROMPT = """
You are evaluating a deliverable for quality and completeness.

## Subject Context
{subject_context}

## Deliverable to Review
{deliverable}

## Evaluation Instructions

Rate the deliverable on a scale of 0.0 to 1.0 based on:
- Completeness: Are all required elements present?
- Clarity: Is the content clear and understandable?
- Consistency: Is there internal consistency?
- Actionability: Does it provide clear next steps?

Return JSON:
```json
{{
  "alignment_score": 0.0-1.0,
  "issues_found": [
    {{"severity": "critical|major|minor", "description": "..."}}
  ],
  "suggestions": ["improvement suggestion 1", "..."]
}}
```

Critical issues (score < 0.4):
- Missing essential sections
- Fundamental contradictions
- Completely off-topic content

IMPORTANT: You do NOT have access to the author's reasoning or drafts.
Evaluate ONLY based on the deliverable content provided.
"""
```

### Recommendation

**Simple threshold scoring** for MVP.

| Score Range | Verdict |
|-------------|---------|
| >= 0.70 | APPROVED |
| 0.40 - 0.69 | NEEDS_REVISION |
| < 0.40 | BLOCKED |

Benefits:
- Simple to implement and debug
- Clear decision boundaries
- Sufficient for MVP quality control

---

## Topic 7.2: Quality Gate Criteria (Simplified)

### Context

**Occam's Razor Decision**: Single-threshold quality gate instead of multi-tier system.

### Implementation Guidance

**Simple Quality Gate**:

```python
class SimpleQualityGate:
    """MVP quality gate - simple threshold-based."""
    
    def __init__(
        self,
        approval_threshold: float = 0.70,
        blocked_threshold: float = 0.40,
        max_iterations: int = 3
    ):
        self.approval_threshold = approval_threshold
        self.blocked_threshold = blocked_threshold
        self.max_iterations = max_iterations
    
    def evaluate(
        self, 
        alignment_score: float, 
        iteration: int,
        critical_issues: List[str] = None
    ) -> dict:
        """Evaluate quality gate."""
        
        # Critical issues always block
        if critical_issues:
            return {
                "verdict": "BLOCKED",
                "reason": "critical_issues",
                "details": critical_issues,
                "action": "Cannot proceed - resolve critical issues"
            }
        
        # Score below blocked threshold
        if alignment_score < self.blocked_threshold:
            return {
                "verdict": "BLOCKED",
                "reason": "score_too_low",
                "score": alignment_score,
                "action": "Major revision required"
            }
        
        # Score meets approval threshold
        if alignment_score >= self.approval_threshold:
            return {
                "verdict": "APPROVED",
                "score": alignment_score,
                "action": "Proceed to next node"
            }
        
        # Needs revision - check iteration limit
        if iteration >= self.max_iterations:
            # Accept with warning if above blocked threshold
            return {
                "verdict": "APPROVED",
                "score": alignment_score,
                "warning": f"Max iterations reached (score: {alignment_score:.2f})",
                "action": "Proceed with current quality"
            }
        
        return {
            "verdict": "NEEDS_REVISION",
            "score": alignment_score,
            "iteration": iteration,
            "remaining_iterations": self.max_iterations - iteration,
            "action": "Iterate with feedback"
        }
```

### Recommendation

**Single threshold with iteration limit**.

Configuration:
- Approval threshold: 0.70
- Blocked threshold: 0.40
- Max iterations: 3

Benefits:
- Simple decision logic
- Clear escalation path
- Prevents infinite loops

---

## Topic 7.3: Testing Strategy (pytest)

### Context

**Occam's Razor Decision**: Python/pytest testing (not TypeScript/Jest) for LangGraph-based implementation.

### Implementation Guidance

**Test Structure**:

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_agents.py          # Agent unit tests
│   ├── test_state.py           # State management tests
│   └── test_context.py         # Context isolation tests
│
├── integration/
│   ├── test_node_execution.py  # Node execution tests
│   ├── test_pipeline.py        # Pipeline integration tests
│   └── test_checkpointing.py   # LangGraph checkpoint tests
│
└── e2e/
    └── test_full_pipeline.py   # End-to-end scenarios
```

**conftest.py (Shared Fixtures)**:

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_session_manager():
    """Mock KimiSessionManager for testing."""
    manager = AsyncMock()
    manager.single_prompt.return_value = [MagicMock(
        content='{"deliverable": {"title": "Test", "content": "Content"}, '
                '"questions": [{"id": "q1", "category": "blocking", "text": "Test?"}], '
                '"evaluation": {"alignment_score": 0.85, "verdict": "APPROVED"}}'
    )]
    return manager

@pytest.fixture
def sample_subject_context():
    """Sample subject context for testing."""
    return {
        "project_name": "TestProject",
        "requirements": ["req1", "req2"],
        "constraints": ["constraint1"]
    }

@pytest.fixture
def sample_deliverable():
    """Sample deliverable for testing."""
    return {
        "title": "Test Deliverable",
        "content": "# Test\n\nThis is test content."
    }
```

**Unit Test Example (Context Isolation)**:

```python
# tests/unit/test_context.py
import pytest
from docuswarm.agents.evaluator import EvaluatorAgentNode

class TestContextIsolation:
    """Test context isolation for security."""
    
    def test_evaluator_does_not_receive_private_reasoning(
        self, 
        mock_session_manager, 
        sample_subject_context,
        sample_deliverable
    ):
        """Evaluator MUST NOT have access to private reasoning."""
        evaluator = EvaluatorAgentNode("analyst", {}, mock_session_manager)
        
        # State with private reasoning
        state = {
            "subject_context": sample_subject_context,
            "deliverable": sample_deliverable,
            "private_reasoning": "SECRET: My internal analysis...",
            "evaluation": None
        }
        
        # Build evaluator context
        eval_context = evaluator._build_evaluation_context(state)
        
        # Verify no private data
        assert "private_reasoning" not in eval_context
        assert "SECRET" not in str(eval_context)
        assert "internal analysis" not in str(eval_context).lower()
    
    def test_evaluator_context_contains_only_subject_and_deliverable(
        self,
        mock_session_manager,
        sample_subject_context,
        sample_deliverable
    ):
        """Evaluator context should contain only subject and deliverable."""
        evaluator = EvaluatorAgentNode("analyst", {}, mock_session_manager)
        
        state = {
            "subject_context": sample_subject_context,
            "deliverable": sample_deliverable,
            "private_reasoning": "SECRET",
            "questions": [{"id": "q1"}],  # Questions from Independent
            "tool_calls": ["call1", "call2"]  # Tool call history
        }
        
        eval_context = evaluator._build_evaluation_context(state)
        
        # Should have these
        assert "subject_context" in eval_context or "subject" in str(eval_context)
        assert "deliverable" in eval_context
        
        # Should NOT have these
        assert "tool_calls" not in eval_context
        assert "questions" not in eval_context  # Questions are Independent's output
```

**Integration Test Example**:

```python
# tests/integration/test_node_execution.py
import pytest
from docuswarm.nodes.dual_agent import DualAgentNode

class TestNodeExecution:
    """Test dual-agent node execution."""
    
    @pytest.mark.asyncio
    async def test_dual_agent_produces_deliverable_and_questions(
        self,
        mock_session_manager,
        sample_subject_context
    ):
        """Node should produce deliverable, questions, and evaluation."""
        node = DualAgentNode("analyst", {"session_manager": mock_session_manager})
        
        result = await node.execute(sample_subject_context)
        
        # Check all outputs present
        assert "deliverable" in result
        assert "questions" in result
        assert "evaluation" in result
        
        # Check questions minimum
        assert len(result["questions"]) >= 3
    
    @pytest.mark.asyncio
    async def test_node_iterates_on_needs_revision(
        self,
        mock_session_manager,
        sample_subject_context
    ):
        """Node should iterate when evaluation returns NEEDS_REVISION."""
        # Configure mock to return NEEDS_REVISION then APPROVED
        responses = [
            '{"alignment_score": 0.5, "verdict": "NEEDS_REVISION", "issues_found": []}',
            '{"alignment_score": 0.85, "verdict": "APPROVED", "issues_found": []}'
        ]
        mock_session_manager.chat.side_effect = [
            MagicMock(content=r) for r in responses
        ]
        
        node = DualAgentNode("analyst", {"session_manager": mock_session_manager})
        result = await node.execute(sample_subject_context)
        
        # Should have iterated
        assert result.get("iteration", 0) >= 1
        assert result["evaluation"]["verdict"] == "APPROVED"
```

**E2E Test Example**:

```python
# tests/e2e/test_full_pipeline.py
import pytest
from docuswarm.pipeline.graph import SequentialPipeline

class TestFullPipeline:
    """End-to-end pipeline tests."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_analyst_to_pm_pipeline(self, mock_session_manager):
        """Test execution from analyst to PM node."""
        pipeline = SequentialPipeline(
            nodes=["analyst", "pm"],
            session_manager=mock_session_manager
        )
        
        result = await pipeline.run({
            "project_name": "Test Project",
            "description": "A test project for validation"
        })
        
        assert result["status"] == "completed"
        assert "analyst" in result["completed_nodes"]
        assert "pm" in result["completed_nodes"]
        assert len(result["deliverables"]) == 2
```

### Recommendation

**pytest with async support** for MVP testing.

Coverage Targets:
- Unit tests: 80% coverage on core logic
- Integration tests: All critical paths
- E2E tests: 3-5 key scenarios

Focus Areas:
1. Context isolation (security-critical)
2. Iteration handling
3. State persistence

---

## Topic 7.4: Performance Benchmarks (Simplified)

### Context

**Occam's Razor Decision**: Simple timing benchmarks instead of full profiling infrastructure.

### Implementation Guidance

**Simple Benchmark Tests**:

```python
# tests/performance/test_benchmarks.py
import pytest
import time
from statistics import mean, stdev

class TestPerformanceBenchmarks:
    """Simple performance benchmarks."""
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_node_execution_time(self, mock_session_manager):
        """Benchmark node execution time."""
        node = DualAgentNode("analyst", {"session_manager": mock_session_manager})
        
        durations = []
        for _ in range(5):
            start = time.time()
            await node.execute({"project_name": "Test"})
            durations.append(time.time() - start)
        
        avg_duration = mean(durations)
        
        print(f"\nNode Execution: avg={avg_duration:.2f}s, stdev={stdev(durations):.2f}s")
        
        # Assert reasonable performance
        assert avg_duration < 30, f"Node execution too slow: {avg_duration}s"
```

**Performance Targets**:

```yaml
# performance-targets.yaml
targets:
  node_execution:
    target_seconds: 30
    warning_seconds: 45
    
  full_pipeline_sequential:
    target_seconds: 300  # 5 minutes
    warning_seconds: 420  # 7 minutes
    
  evaluator_review:
    target_seconds: 10
    warning_seconds: 15
```

### Recommendation

**Simple timing benchmarks** for MVP.

Key Metrics:
- Node execution: < 30 seconds average
- Full pipeline: < 5 minutes (sequential)
- Evaluator review: < 10 seconds

---

## Topic 7.5: Security Audit (Context Isolation Focus)

### Context

**Occam's Razor Decision**: Focus security testing on context isolation only. Other security concerns (injection, etc.) are lower priority for MVP.

### Implementation Guidance

**Context Isolation Security Tests**:

```python
# tests/security/test_context_isolation.py
import pytest

class TestContextIsolationSecurity:
    """Security tests for context isolation - CRITICAL."""
    
    def test_evaluator_cannot_access_private_reasoning(self):
        """SECURITY: Evaluator MUST NOT access private reasoning."""
        from docuswarm.context.manager import ContextManager
        
        cm = ContextManager()
        
        # Build evaluator context with private data in state
        state = {
            "subject_context": {"project": "test"},
            "deliverable": {"title": "Test"},
            "private_reasoning": "My secret reasoning about the problem"
        }
        
        eval_context = cm.build_evaluator_context(state)
        
        # Verify isolation
        assert "private_reasoning" not in eval_context
        assert "secret" not in str(eval_context).lower()
        assert "reasoning" not in str(eval_context).lower()
    
    def test_evaluator_cannot_access_tool_history(self):
        """SECURITY: Evaluator MUST NOT access tool call history."""
        from docuswarm.context.manager import ContextManager
        
        cm = ContextManager()
        
        state = {
            "subject_context": {"project": "test"},
            "deliverable": {"title": "Test"},
            "tool_calls": [
                {"name": "query_database", "result": "sensitive data"}
            ]
        }
        
        eval_context = cm.build_evaluator_context(state)
        
        assert "tool_calls" not in eval_context
        assert "query_database" not in str(eval_context)
        assert "sensitive" not in str(eval_context).lower()
    
    def test_logging_does_not_expose_private_data(self, caplog):
        """SECURITY: Logs MUST NOT contain private reasoning."""
        from docuswarm.nodes.dual_agent import DualAgentNode
        import logging
        
        with caplog.at_level(logging.INFO):
            # Execute node with private reasoning
            # (would need mock setup)
            pass
        
        # Check logs don't contain private data
        for record in caplog.records:
            assert "private_reasoning" not in record.message.lower()
            assert "secret" not in record.message.lower()
```

**Security Checklist**:

```markdown
# Context Isolation Security Checklist

## Critical (Must Pass for MVP)
- [ ] Evaluator context excludes private_reasoning
- [ ] Evaluator context excludes tool_calls
- [ ] Evaluator context excludes draft versions
- [ ] Logs are sanitized (no private data)

## Important (Pre-Production)
- [ ] API keys not logged
- [ ] File paths validated (no traversal)
- [ ] JSON parsing handles malicious input

## Lower Priority (Phase 2)
- [ ] Prompt injection mitigation
- [ ] Rate limiting abuse prevention
- [ ] Comprehensive penetration testing
```

### Recommendation

**Focus on context isolation** for MVP security.

Critical Tests:
1. Evaluator cannot access private_reasoning
2. Evaluator cannot access tool_calls
3. Logs don't expose private data

Phase 2 Enhancements:
- Full security audit
- Penetration testing
- Input validation hardening

---

## Cross-Topic Dependencies (Updated)

```
7.1 Alignment Scoring
 └─→ 2.2 Evaluator Agent
 └─→ Simplified threshold approach

7.2 Quality Gates
 └─→ 3.7 Iteration Handling
 └─→ Simple threshold + iteration limit

7.3 Testing Strategy
 └─→ 4.6 Python/LangGraph
 └─→ pytest framework

7.4 Performance Benchmarks
 └─→ Simple timing tests
 └─→ 5.6 Observability

7.5 Security Audit
 └─→ 1.2 Context Isolation (critical)
 └─→ Focused scope for MVP
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original Design | Simplified Design | Savings |
|-------|----------------|-------------------|---------|
| 7.1 Scoring | Hybrid 70/30 rubric | Simple threshold | ~1 week |
| 7.2 Quality Gates | Multi-tier system | Single threshold + limit | Simpler |
| 7.3 Testing | TypeScript/Jest | Python/pytest | Alignment |
| 7.4 Benchmarks | Full profiling | Simple timing | ~1 week |
| 7.5 Security | Full audit | Context isolation focus | ~1 week |

**Total Estimated Savings**: ~2-3 weeks development time

---

## References

### Research Sources
- pytest Documentation (pytest.org)
- pytest-asyncio Documentation
- OWASP Testing Guidelines

### Related Analysis Documents
- [2_AGENT_SYSTEM_DESIGN.md](2_AGENT_SYSTEM_DESIGN.md) - Dual-agent pattern
- [1_ARCHITECTURE_AND_DESIGN.md](1_ARCHITECTURE_AND_DESIGN.md) - Context isolation

---

**Document Status**: Version 2.0 - Occam's Razor Simplified  
**Key Change**: Simplified scoring, pytest testing, focused security  
**Development Time Savings**: ~2-3 weeks compared to full testing infrastructure
