# Epic 5: Quality Control & Iteration

**Epic ID**: EPIC-05  
**Version**: 1.0  
**Date**: 2026-02-19  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 1 Week (Week 8)

---

## 1. Epic Overview

### 1.1 Summary

Implement the quality control system including iteration handling, evaluation thresholds, escalation mechanisms, and the question answering workflow. This epic ensures deliverables meet quality standards through the iterative dual-agent review process.

### 1.2 Business Value

- **Quality Assurance**: Deliverables meet defined thresholds
- **Cost Control**: Max iterations prevent runaway costs
- **User Control**: Escalation and questions engage user when needed
- **Transparency**: Clear verdicts and scores

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Average alignment score | ≥ 0.70 |
| First-pass approval rate | ≥ 60% |
| Max iterations respected | 100% |
| Escalation handled | All BLOCKED verdicts pause |

### 1.4 Dependencies

- **Requires**: Epic 2 (Agent System), Epic 3 (Node Execution), Epic 4 (Isolation)
- **Final**: This is the last MVP epic

---

## 2. Architecture Context

### 2.1 Quality Control Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Quality Control System (Epic 5)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Node Execution                                                              │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EVALUATION DECISION                               │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Alignment Score >= 0.70                                     │   │   │
│  │  │                     │                                        │   │   │
│  │  │           ┌─────────┴─────────┐                             │   │   │
│  │  │           ▼                   ▼                             │   │   │
│  │  │       YES: APPROVED       NO: Check Iteration               │   │   │
│  │  │           │                   │                             │   │   │
│  │  │           ▼                   ▼                             │   │   │
│  │  │     Complete Node     Iteration < 3?                        │   │   │
│  │  │     Save Deliverable         │                              │   │   │
│  │  │     Next Node          ┌─────┴─────┐                        │   │   │
│  │  │                        ▼           ▼                        │   │   │
│  │  │                   YES: Iterate  NO: Force Complete          │   │   │
│  │  │                   NEEDS_REVISION or Escalate                │   │   │
│  │  │                        │           │                        │   │   │
│  │  │                        ▼           ▼                        │   │   │
│  │  │                   Re-execute   Score >= 0.50?               │   │   │
│  │  │                   with feedback    │                        │   │   │
│  │  │                                    ▼                        │   │   │
│  │  │                          YES: Force Complete with Warning   │   │   │
│  │  │                          NO: BLOCKED - Escalate to User     │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Question Handling                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐ │   │
│  │  │    BLOCKING       │  │    CLARIFYING     │  │    OPTIONAL     │ │   │
│  │  │  Must be answered │  │  Recommended      │  │  Can be skipped │ │   │
│  │  │  before proceed   │  │  for quality      │  │                 │ │   │
│  │  └───────────────────┘  └───────────────────┘  └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `docuswarm/nodes/iteration.py` | Iteration control logic |
| `docuswarm/node_execution/quality.py` | Quality thresholds and verdicts |
| `docuswarm/node_execution/questions.py` | Question handling workflow |
| `docuswarm/node_execution/escalation.py` | Escalation handling |

---

## 3. User Stories

### Story 5.1: Evaluation Threshold Configuration

**ID**: US-5.1  
**As a** developer  
**I want to** configure evaluation thresholds  
**So that** quality decisions are consistent

**Acceptance Criteria**:
- [ ] Approval threshold configurable (default 0.70)
- [ ] Escalation threshold configurable (default 0.50)
- [ ] Per-node threshold overrides
- [ ] Thresholds loaded from configuration

**Technical Tasks**:
1. Create `node_execution/quality.py`
2. Implement threshold configuration
3. Implement verdict determination
4. Write tests

**Implementation**:
```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class QualityThresholds:
    """Quality threshold configuration."""
    approval: float = 0.70
    escalation: float = 0.50

class QualityConfig:
    """Quality control configuration."""
    
    # Default thresholds
    DEFAULT_THRESHOLDS = QualityThresholds(
        approval=0.70,
        escalation=0.50
    )
    
    # Node-specific overrides
    NODE_THRESHOLDS: Dict[str, QualityThresholds] = {
        "analyst": QualityThresholds(approval=0.70, escalation=0.50),
        "pm": QualityThresholds(approval=0.70, escalation=0.50),
        "ux": QualityThresholds(approval=0.70, escalation=0.50),
        "architect": QualityThresholds(approval=0.75, escalation=0.55),  # Stricter
        "po": QualityThresholds(approval=0.70, escalation=0.50),
    }
    
    @classmethod
    def get_thresholds(cls, node_id: str) -> QualityThresholds:
        """Get thresholds for a specific node."""
        return cls.NODE_THRESHOLDS.get(node_id, cls.DEFAULT_THRESHOLDS)

class VerdictDeterminer:
    """Determines verdict based on evaluation scores."""
    
    def determine_verdict(
        self, 
        alignment_score: float,
        node_id: str,
        iteration: int,
        max_iterations: int = 3
    ) -> str:
        """Determine verdict based on score and iteration."""
        thresholds = QualityConfig.get_thresholds(node_id)
        
        if alignment_score >= thresholds.approval:
            return "APPROVED"
        
        if iteration >= max_iterations:
            if alignment_score >= thresholds.escalation:
                return "FORCE_APPROVED"  # Complete with warning
            else:
                return "BLOCKED"  # Escalate to user
        
        return "NEEDS_REVISION"
```

**Definition of Done**:
- Thresholds configurable
- Verdict determination correct
- Tests pass

---

### Story 5.2: Iteration Control Implementation

**ID**: US-5.2  
**As a** developer  
**I want to** control iteration flow  
**So that** nodes iterate until approved or max reached

**Acceptance Criteria**:
- [ ] Track iteration count per node
- [ ] Max 3 iterations enforced
- [ ] Feedback passed to next iteration
- [ ] Iteration history preserved

**Technical Tasks**:
1. Create `nodes/iteration.py`
2. Implement IterationController class
3. Implement feedback accumulation
4. Write tests

**Implementation**:
```python
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class IterationHistory:
    """History of a single iteration."""
    iteration: int
    deliverable_summary: str
    alignment_score: float
    verdict: str
    issues: List[str]
    feedback: str

@dataclass
class NodeIterationState:
    """Iteration state for a node."""
    node_id: str
    current_iteration: int = 0
    max_iterations: int = 3
    history: List[IterationHistory] = field(default_factory=list)
    final_verdict: Optional[str] = None

class IterationController:
    """Controls iteration flow within a node."""
    
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.states: Dict[str, NodeIterationState] = {}
        self.logger = structlog.get_logger().bind(component="IterationController")
    
    def start_iteration(self, node_id: str) -> int:
        """Start a new iteration for a node."""
        if node_id not in self.states:
            self.states[node_id] = NodeIterationState(
                node_id=node_id,
                max_iterations=self.max_iterations
            )
        
        state = self.states[node_id]
        state.current_iteration += 1
        
        self.logger.info(
            "Iteration started",
            node_id=node_id,
            iteration=state.current_iteration
        )
        
        return state.current_iteration
    
    def record_iteration(
        self,
        node_id: str,
        evaluation: dict,
        deliverable_summary: str
    ) -> None:
        """Record iteration result."""
        state = self.states[node_id]
        
        history = IterationHistory(
            iteration=state.current_iteration,
            deliverable_summary=deliverable_summary,
            alignment_score=evaluation["alignment_score"],
            verdict=evaluation["verdict"],
            issues=evaluation.get("issues_found", []),
            feedback=self._generate_feedback(evaluation)
        )
        
        state.history.append(history)
        self.logger.info(
            "Iteration recorded",
            node_id=node_id,
            iteration=state.current_iteration,
            verdict=evaluation["verdict"]
        )
    
    def should_iterate(self, node_id: str, verdict: str) -> bool:
        """Determine if another iteration should occur."""
        state = self.states[node_id]
        
        if verdict == "APPROVED":
            return False
        
        if state.current_iteration >= self.max_iterations:
            self.logger.warning(
                "Max iterations reached",
                node_id=node_id,
                iteration=state.current_iteration
            )
            return False
        
        return verdict == "NEEDS_REVISION"
    
    def get_accumulated_feedback(self, node_id: str) -> str:
        """Get accumulated feedback from all iterations."""
        state = self.states[node_id]
        
        if not state.history:
            return ""
        
        feedback_parts = []
        for h in state.history:
            feedback_parts.append(
                f"## Iteration {h.iteration} Feedback\n"
                f"Score: {h.alignment_score:.2f}\n"
                f"Issues: {', '.join(h.issues)}\n"
                f"Guidance: {h.feedback}"
            )
        
        return "\n\n".join(feedback_parts)
    
    def _generate_feedback(self, evaluation: dict) -> str:
        """Generate iteration feedback from evaluation."""
        issues = evaluation.get("issues_found", [])
        suggestions = evaluation.get("suggestions", [])
        
        feedback = "Please address the following:\n"
        for issue in issues:
            feedback += f"- Issue: {issue}\n"
        for suggestion in suggestions:
            feedback += f"- Suggestion: {suggestion}\n"
        
        return feedback
```

**Definition of Done**:
- Iteration count tracked
- Max iterations enforced
- Feedback accumulated correctly

---

### Story 5.3: Escalation Handling

**ID**: US-5.3  
**As a** developer  
**I want to** handle escalation to user  
**So that** critical issues are addressed

**Acceptance Criteria**:
- [ ] BLOCKED verdict triggers escalation
- [ ] Node run marks as blocked on escalation
- [ ] User can provide guidance
- [ ] Node can be re-run after user input

**Technical Tasks**:
1. Create `node_execution/escalation.py`
2. Implement EscalationHandler class
3. Implement block/re-run flow
4. Write tests

**Implementation**:
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class EscalationReason(Enum):
    """Reasons for escalation."""
    MAX_ITERATIONS = "max_iterations_reached"
    BLOCKED_VERDICT = "blocked_verdict"
    CRITICAL_ISSUE = "critical_issue"
    USER_REQUESTED = "user_requested"

@dataclass
class Escalation:
    """Escalation record."""
    run_id: str
    node_id: str
    reason: EscalationReason
    details: str
    alignment_score: float
    issues: list
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None

class EscalationHandler:
    """Handles escalation to user."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.escalations: Dict[str, Escalation] = {}
        self.logger = structlog.get_logger().bind(component="EscalationHandler")
    
    async def escalate(
        self,
        run_id: str,
        node_id: str,
        reason: EscalationReason,
        evaluation: dict
    ) -> Escalation:
        """Create escalation and pause node run."""
        self.logger.warning(
            "Escalation triggered",
            run_id=run_id,
            node_id=node_id,
            reason=reason.value
        )
        
        escalation = Escalation(
            run_id=run_id,
            node_id=node_id,
            reason=reason,
            details=self._format_details(evaluation),
            alignment_score=evaluation["alignment_score"],
            issues=evaluation.get("issues_found", []),
            created_at=datetime.now()
        )
        
        self.escalations[run_id] = escalation
        
        # Update node run status
        await self.state_manager.update_node_run_status(
            run_id=run_id,
            status="blocked"
        )
        
        return escalation
    
    async def resolve(
        self,
        run_id: str,
        resolution: str,
        guidance: str = None
    ) -> None:
        """Resolve escalation and update node run."""
        escalation = self.escalations.get(run_id)
        if not escalation:
            raise ValueError(f"No escalation found for run {run_id}")
        
        escalation.resolved_at = datetime.now()
        escalation.resolution = resolution
        
        self.logger.info(
            "Escalation resolved",
            run_id=run_id,
            resolution=resolution
        )
        
        # Update node run with user guidance if provided
        if guidance:
            await self.state_manager.update_node_run_answers(
                run_id=run_id,
                key="user_guidance",
                value=guidance
            )
        
        # Update node run status to allow continuation
        await self.state_manager.update_node_run_status(
            run_id=run_id,
            status="running"
        )
    
    def _format_details(self, evaluation: dict) -> str:
        """Format escalation details for user."""
        return (
            f"Alignment Score: {evaluation['alignment_score']:.2f}\n"
            f"Issues Found:\n" +
            "\n".join(f"- {issue}" for issue in evaluation.get("issues_found", []))
        )
```

**Acceptance Criteria**:
- [ ] Escalation creates record
- [ ] Node run status updated to blocked
- [ ] Resolution updates node run status
- [ ] User guidance incorporated

---

### Story 5.4: Question Handling Workflow

**ID**: US-5.4  
**As a** developer  
**I want to** handle questions from agents  
**So that** user input improves quality

**Acceptance Criteria**:
- [ ] Questions categorized by priority
- [ ] Blocking questions prevent progression
- [ ] User can answer questions via CLI
- [ ] Answers incorporated into context

**Technical Tasks**:
1. Create `node_execution/questions.py`
2. Implement QuestionHandler class
3. Implement question storage and retrieval
4. Implement answer incorporation
5. Write tests

**Implementation**:
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class QuestionPriority(Enum):
    """Question priority levels."""
    BLOCKING = "blocking"      # Must answer to proceed
    CLARIFYING = "clarifying"  # Should answer for quality
    OPTIONAL = "optional"      # Nice to have

@dataclass
class Question:
    """A question from an agent."""
    id: str
    run_id: str
    node_id: str
    priority: QuestionPriority
    question: str
    context: str
    answer: Optional[str] = None
    answered_at: Optional[datetime] = None

class QuestionHandler:
    """Handles question collection and answering."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.questions: Dict[str, List[Question]] = {}
        self.logger = structlog.get_logger().bind(component="QuestionHandler")
    
    def collect_questions(
        self,
        run_id: str,
        node_id: str,
        questions: List[dict]
    ) -> List[Question]:
        """Collect questions from agent output."""
        collected = []
        
        for i, q in enumerate(questions):
            question = Question(
                id=f"{node_id}_{run_id[:8]}_{i}",
                run_id=run_id,
                node_id=node_id,
                priority=QuestionPriority(q.get("priority", "optional")),
                question=q["question"],
                context=q.get("context", "")
            )
            collected.append(question)
        
        if run_id not in self.questions:
            self.questions[run_id] = []
        self.questions[run_id].extend(collected)
        
        self.logger.info(
            "Questions collected",
            run_id=run_id,
            node_id=node_id,
            count=len(collected)
        )
        
        return collected
    
    def get_unanswered_questions(
        self,
        run_id: str,
        priority: QuestionPriority = None
    ) -> List[Question]:
        """Get unanswered questions, optionally filtered by priority."""
        questions = self.questions.get(run_id, [])
        unanswered = [q for q in questions if q.answer is None]
        
        if priority:
            unanswered = [q for q in unanswered if q.priority == priority]
        
        return unanswered
    
    def has_blocking_questions(self, run_id: str) -> bool:
        """Check if there are unanswered blocking questions."""
        blocking = self.get_unanswered_questions(
            run_id, 
            QuestionPriority.BLOCKING
        )
        return len(blocking) > 0
    
    async def answer_question(
        self,
        question_id: str,
        answer: str
    ) -> None:
        """Record answer to a question."""
        # Find question
        for questions in self.questions.values():
            for q in questions:
                if q.id == question_id:
                    q.answer = answer
                    q.answered_at = datetime.now()
                    
                    # Update subject context with answer
                    await self._incorporate_answer(q)
                    
                    self.logger.info(
                        "Question answered",
                        question_id=question_id
                    )
                    return
        
        raise ValueError(f"Question not found: {question_id}")
    
    async def _incorporate_answer(self, question: Question) -> None:
        """Incorporate answer into node run answers."""
        await self.state_manager.update_node_run_answers(
            run_id=question.run_id,
            key=f"answer_{question.id}",
            value={
                "question": question.question,
                "answer": question.answer,
                "context": question.context
            }
        )
```

**Definition of Done**:
- Questions stored correctly
- Blocking questions detected
- Answers incorporated

---

### Story 5.5: Force Completion Logic

**ID**: US-5.5  
**As a** developer  
**I want to** force completion at max iterations  
**So that** node run doesn't get stuck

**Acceptance Criteria**:
- [ ] Force complete if score ≥ escalation threshold
- [ ] Generate warning for force completion
- [ ] Record force completion in metadata
- [ ] User notified of quality concern

**Technical Tasks**:
1. Implement force completion in iteration controller
2. Generate completion warnings
3. Record in node results
4. Write tests

**Implementation**:
```python
@dataclass
class ForceCompletion:
    """Force completion record."""
    node_id: str
    final_score: float
    threshold: float
    iterations: int
    warning: str
    issues_remaining: List[str]

class ForceCompletionHandler:
    """Handles force completion of nodes."""
    
    def should_force_complete(
        self,
        node_id: str,
        alignment_score: float,
        iteration: int,
        max_iterations: int
    ) -> bool:
        """Determine if force completion should occur."""
        if iteration < max_iterations:
            return False
        
        thresholds = QualityConfig.get_thresholds(node_id)
        return alignment_score >= thresholds.escalation
    
    def create_force_completion(
        self,
        node_id: str,
        evaluation: dict,
        iteration: int
    ) -> ForceCompletion:
        """Create force completion record with warning."""
        thresholds = QualityConfig.get_thresholds(node_id)
        
        warning = (
            f"Node '{node_id}' force completed after {iteration} iterations. "
            f"Final score {evaluation['alignment_score']:.2f} is below approval "
            f"threshold {thresholds.approval:.2f} but above escalation threshold "
            f"{thresholds.escalation:.2f}. The following issues remain unresolved: "
            f"{', '.join(evaluation.get('issues_found', []))}"
        )
        
        return ForceCompletion(
            node_id=node_id,
            final_score=evaluation["alignment_score"],
            threshold=thresholds.approval,
            iterations=iteration,
            warning=warning,
            issues_remaining=evaluation.get("issues_found", [])
        )
```

**Definition of Done**:
- Force completion logic correct
- Warning generated clearly
- Record preserved

---

### Story 5.6: Quality Metrics Collection

**ID**: US-5.6  
**As a** developer  
**I want to** collect quality metrics  
**So that** I can monitor node execution quality

**Acceptance Criteria**:
- [ ] Track scores per node
- [ ] Track iterations per node
- [ ] Calculate averages per context_hash
- [ ] Generate quality report

**Technical Tasks**:
1. Create `node_execution/metrics.py`
2. Implement metrics collection
3. Implement report generation
4. Write tests

**Implementation**:
```python
from dataclasses import dataclass, field
from typing import Dict, List
from statistics import mean

@dataclass
class NodeMetrics:
    """Metrics for a single node."""
    node_id: str
    final_score: float
    iterations: int
    verdict: str
    force_completed: bool = False

@dataclass
class NodeRunMetrics:
    """Metrics for a single node run."""
    run_id: str
    node_id: str
    final_score: float
    iterations: int
    verdict: str
    force_completed: bool = False

class MetricsCollector:
    """Collects and reports quality metrics."""
    
    def __init__(self):
        self.node_runs: Dict[str, NodeRunMetrics] = {}
    
    def record_node_completion(
        self,
        run_id: str,
        node_id: str,
        evaluation: dict,
        iterations: int,
        force_completed: bool = False
    ) -> None:
        """Record node run completion metrics."""
        self.node_runs[run_id] = NodeRunMetrics(
            run_id=run_id,
            node_id=node_id,
            final_score=evaluation["alignment_score"],
            iterations=iterations,
            verdict=evaluation["verdict"],
            force_completed=force_completed
        )
    
    def finalize_node_run(
        self,
        run_id: str,
        status: str
    ) -> None:
        """Mark node run as complete."""
        if run_id in self.node_runs:
            # Update status in node_runs table via state_manager
            pass
    
    def generate_report(self, run_id: str) -> dict:
        """Generate quality report for node run."""
        metrics = self.node_runs.get(run_id)
        if not metrics:
            return {"error": "Node run not found"}
        
        return {
            "run_id": run_id,
            "node_id": metrics.node_id,
            "summary": {
                "iterations": metrics.iterations,
                "final_score": round(metrics.final_score, 3),
                "verdict": metrics.verdict,
                "force_completed": metrics.force_completed
            }
        }
    
    def generate_node_aggregate_report(self, node_id: str) -> dict:
        """Generate aggregate report for all runs of a node."""
        node_metrics = [m for m in self.node_runs.values() if m.node_id == node_id]
        
        if not node_metrics:
            return {"error": "No runs found for node"}
        
        return {
            "node_id": node_id,
            "total_runs": len(node_metrics),
            "average_score": round(mean(m.final_score for m in node_metrics), 3),
            "average_iterations": round(mean(m.iterations for m in node_metrics), 1),
            "force_completions": sum(1 for m in node_metrics if m.force_completed)
        }
```

**Definition of Done**:
- Metrics collected correctly
- Report generated
- Statistics accurate

---

### Story 5.7: CLI Question Commands

**ID**: US-5.7  
**As a** user  
**I want to** answer questions via CLI  
**So that** I can provide input to improve quality

**Acceptance Criteria**:
- [ ] `docuswarm questions <node>` lists questions for node's latest run
- [ ] `docuswarm answer <question-id> <answer>` provides answer
- [ ] Questions displayed with context
- [ ] Blocking questions highlighted

**Technical Tasks**:
1. Add `questions` command to CLI
2. Add `answer` command to CLI
3. Format question display
4. Write tests

**CLI Commands**:
```python
@cli.command()
@click.argument("node")
@click.option("--run", help="Specific run ID (default: latest)")
def questions(node: str, run: str = None):
    """List questions for a node."""
    handler = QuestionHandler(state_manager)
    
    # Get run_id (latest if not specified)
    if not run:
        latest_run = state_manager.get_latest_run(node)
        run = latest_run.run_id if latest_run else None
    
    if not run:
        console = Console()
        console.print(f"[red]No runs found for node {node}[/]")
        return
    
    # Get questions by priority
    blocking = handler.get_unanswered_questions(
        run, QuestionPriority.BLOCKING
    )
    clarifying = handler.get_unanswered_questions(
        run, QuestionPriority.CLARIFYING
    )
    optional = handler.get_unanswered_questions(
        run, QuestionPriority.OPTIONAL
    )
    
    console = Console()
    
    if blocking:
        console.print("[red bold]⚠ Blocking Questions (must answer):[/]")
        for q in blocking:
            console.print(f"  [{q.id}] {q.question}")
            if q.context:
                console.print(f"      Context: {q.context}")
    
    if clarifying:
        console.print("[yellow]📝 Clarifying Questions:[/]")
        for q in clarifying:
            console.print(f"  [{q.id}] {q.question}")
    
    if optional:
        console.print("[dim]💡 Optional Questions:[/]")
        for q in optional:
            console.print(f"  [{q.id}] {q.question}")
    
    if not (blocking or clarifying or optional):
        console.print("[green]✓ No unanswered questions[/]")


@cli.command()
@click.argument("question_id")
@click.argument("answer")
def answer(question_id: str, answer: str):
    """Answer a question."""
    handler = QuestionHandler(state_manager)
    
    try:
        asyncio.run(handler.answer_question(question_id, answer))
        console = Console()
        console.print(f"[green]✓ Answer recorded for {question_id}[/]")
    except ValueError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/]")
```

**Definition of Done**:
- Commands work correctly
- Questions displayed clearly
- Answers recorded

---

### Story 5.8: Integration with DualAgentNode

**ID**: US-5.8  
**As a** developer  
**I want to** integrate quality control with node execution  
**So that** iteration happens automatically

**Acceptance Criteria**:
- [ ] Iteration controller integrated
- [ ] Question handler integrated
- [ ] Escalation handler integrated
- [ ] Metrics collector integrated

**Technical Tasks**:
1. Update DualAgentNode with quality control
2. Implement iteration loop
3. Handle escalation
4. Record metrics
5. Write integration tests

**Implementation**:
```python
class DualAgentNode:
    """Full node with quality control."""
    
    def __init__(
        self,
        node_id: str,
        llm_client: LLMClient,
        context_manager: ContextManager,
        context_filter: ContextFilter,
        audit_logger: IsolationAuditLogger,
        iteration_controller: IterationController,
        question_handler: QuestionHandler,
        escalation_handler: EscalationHandler,
        metrics_collector: MetricsCollector
    ):
        # ... initialization
        pass
    
    async def execute_with_iteration(
        self,
        state: NodeRunState
    ) -> NodeResult:
        """Execute node with full iteration and quality control."""
        run_id = state["run_id"]
        
        while True:
            # Start iteration
            iteration = self.iteration_controller.start_iteration(self.node_id)
            
            # Get accumulated feedback
            feedback = self.iteration_controller.get_accumulated_feedback(
                self.node_id
            )
            
            # Execute single iteration
            result = await self._execute_single_iteration(
                state, iteration, feedback
            )
            
            # Collect questions
            self.question_handler.collect_questions(
                run_id,
                self.node_id,
                result.questions
            )
            
            # Record iteration
            self.iteration_controller.record_iteration(
                self.node_id,
                result.evaluation,
                result.deliverable.get("title", "Untitled")
            )
            
            # Determine verdict
            verdict = VerdictDeterminer().determine_verdict(
                alignment_score=result.evaluation["alignment_score"],
                node_id=self.node_id,
                iteration=iteration
            )
            
            # Handle verdict
            if verdict == "APPROVED":
                self.metrics_collector.record_node_completion(
                    run_id, self.node_id, result.evaluation, iteration
                )
                return result
            
            elif verdict == "FORCE_APPROVED":
                self.metrics_collector.record_node_completion(
                    run_id, self.node_id, result.evaluation, iteration,
                    force_completed=True
                )
                return result
            
            elif verdict == "BLOCKED":
                await self.escalation_handler.escalate(
                    run_id, self.node_id,
                    EscalationReason.MAX_ITERATIONS,
                    result.evaluation
                )
                raise EscalationError(
                    f"Node {self.node_id} blocked - escalation required"
                )
            
            # NEEDS_REVISION - continue loop
            if not self.iteration_controller.should_iterate(
                self.node_id, verdict
            ):
                break
        
        return result
```

**Definition of Done**:
- Full integration complete
- Iteration works automatically
- Escalation triggers correctly
- Metrics recorded

---

## 4. Technical Specifications

### 4.1 Quality Thresholds

| Threshold | Value | Description |
|-----------|-------|-------------|
| Approval | 0.70 | Score required for APPROVED |
| Escalation | 0.50 | Minimum for force completion |

### 4.2 Verdict Values

| Verdict | Condition | Action |
|---------|-----------|--------|
| APPROVED | score ≥ 0.70 | Complete node |
| NEEDS_REVISION | score < 0.70, iteration < 3 | Iterate |
| FORCE_APPROVED | score ≥ 0.50, iteration = 3 | Complete with warning |
| BLOCKED | score < 0.50, iteration = 3 | Escalate to user |

### 4.3 Question Priorities

| Priority | Required | Node Run Behavior |
|----------|----------|-------------------|
| blocking | Yes | Flagged for user before re-run |
| clarifying | No | Recommended, improves quality |
| optional | No | Can be skipped |

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test | Description |
|------|-------------|
| `test_verdict_determination` | Verify correct verdicts |
| `test_iteration_tracking` | Verify iteration counts |
| `test_feedback_accumulation` | Verify feedback builds |
| `test_question_collection` | Verify question handling |
| `test_escalation_creation` | Verify escalation logic |

### 5.2 Integration Tests

| Test | Description |
|------|-------------|
| `test_full_iteration_flow` | Multiple iterations through approval |
| `test_force_completion` | Force complete at max iterations |
| `test_escalation_flow` | Escalate and resolve |
| `test_question_answering` | Answer questions, verify in context |

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Infinite iteration loop | Low | High | Max iterations enforced |
| Threshold too strict | Medium | Medium | Configurable thresholds |
| Escalation not seen | Low | Medium | CLI notifications |
| Questions accumulate | Low | Low | Per-node question limits |

---

## 7. Definition of Done (Epic Level)

- [ ] All 8 stories completed and tested
- [ ] Iteration control works correctly
- [ ] Escalation marks run as blocked
- [ ] Questions handled via CLI
- [ ] Force completion generates warning
- [ ] Metrics collected and reported
- [ ] Integration tests pass
- [ ] End-to-end iteration test passes
- [ ] Documentation complete

---

## 8. References

| Document | Location |
|----------|----------|
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` |
| Node Execution Architecture | `docs/architecture/03_PIPELINE_ARCHITECTURE.md` |
| PRD | `docs/plan/PRD.md` |

---

**Epic End**
