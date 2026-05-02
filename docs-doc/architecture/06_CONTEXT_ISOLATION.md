# DocuSwarm Context Isolation Architecture

**Version**: 2.2 (BMM NodeExecutor Refactor)  
**Date**: 2026-03-02  
**Status**: Approved  
**Author**: Solution Architect  

> **Note**: 本文档已更新以反映 BMM-aligned System Prompt 结构。详见 [TDD-BMM-02: Persona & System Prompt 重构](../solution/TDD-BMM-02-Persona-SystemPrompt-Refactor.md)。  

---

## 1. Overview

This document details the three-layer context isolation architecture that ensures the Evaluator Agent cannot access the Independent Agent's private reasoning, preventing evaluation bias.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **Defense in Depth** | Multiple isolation layers prevent leakage |
| **Separation of Concerns** | Clear boundaries between agent contexts |
| **Minimal Exposure** | Evaluator sees only what's necessary |
| **Verifiable Isolation** | Audit trail for compliance checking |

### 1.2 Isolation Requirement

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Context Isolation Requirement                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WHY ISOLATION?                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Without isolation, Evaluator could be biased by:                     │ │
│  │  • Knowing the Independent Agent's reasoning process                 │ │
│  │  • Seeing intermediate drafts or rejected options                    │ │
│  │  • Being influenced by tool call history                             │ │
│  │                                                                        │ │
│  │  With isolation:                                                       │ │
│  │  • Evaluator assesses ONLY the final deliverable                     │ │
│  │  • Evaluation is objective (based on content, not intent)            │ │
│  │  • Quality assessment is independent and unbiased                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  WHAT IS ISOLATED?                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  Independent Agent                    Evaluator Agent                  │ │
│  │  ┌──────────────────┐                ┌──────────────────┐             │ │
│  │  │ PRIVATE:         │      ❌        │ CAN SEE:         │             │ │
│  │  │ • reasoning      │  ──────────▶   │ • subject_context│             │ │
│  │  │ • tool_calls     │  NOT SHARED    │ • deliverable    │             │ │
│  │  │ • drafts         │                │                  │             │ │
│  │  │ • iteration_fb   │                │ CANNOT SEE:      │             │ │
│  │  │                  │                │ • reasoning ❌   │             │ │
│  │  │ SHARED:          │      ✓         │ • tool_calls ❌  │             │ │
│  │  │ • subject_context│  ──────────▶   │ • drafts ❌      │             │ │
│  │  │ • deliverable    │  SHARED        │ • feedback ❌    │             │ │
│  │  │ • questions      │                │                  │             │ │
│  │  └──────────────────┘                └──────────────────┘             │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Three-Layer Isolation Architecture

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Three-Layer Context Isolation                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: PROMPT TEMPLATE SEPARATION                                 │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  • Separate system prompts for each agent                     │  │   │
│  │  │  • Independent Agent prompt includes private fields           │  │   │
│  │  │  • Evaluator prompt explicitly excludes private fields        │  │   │
│  │  │  • Templates are code-level constants                         │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 2: RUNTIME ACCESS CONTROL                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  • ContextManager builds agent-specific contexts              │  │   │
│  │  │  • build_independent_context() → Full access                  │  │   │
│  │  │  • build_evaluator_context() → Filtered access                │  │   │
│  │  │  • Type system enforces contract at compile time              │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 3: MESSAGE-LEVEL FILTERING                                    │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  • ContextFilter sanitizes data before Evaluator call         │  │   │
│  │  │  • Removes any private_reasoning fields                       │  │   │
│  │  │  • Strips iteration feedback from context                     │  │   │
│  │  │  • Audit log records what was filtered                        │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow with Isolation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Data Flow Through Isolation Layers                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT: Subject Context                                                     │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INDEPENDENT AGENT                                 │   │
│  │                                                                      │   │
│  │  Input (Layer 2):                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  {                                                           │    │   │
│  │  │    "subject_context": { ... },  // Full project context     │    │   │
│  │  │    "previous_deliverables": { ... },  // Prior node outputs │    │   │
│  │  │    "iteration_feedback": { ... }  // If iterating           │    │   │
│  │  │  }                                                           │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  Output:                                                             │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  {                                                           │    │   │
│  │  │    "deliverable": { ... },     // SHARED with Evaluator     │    │   │
│  │  │    "questions": [ ... ],       // SHARED with Evaluator     │    │   │
│  │  │    "private_reasoning": "..."  // NOT SHARED ❌             │    │   │
│  │  │  }                                                           │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              CONTEXT FILTER (Layer 3)                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  def filter_for_evaluator(independent_output, context):     │    │   │
│  │  │      return {                                                │    │   │
│  │  │          "subject_context": context["subject_context"],     │    │   │
│  │  │          "deliverable": independent_output["deliverable"],  │    │   │
│  │  │          # private_reasoning: REMOVED                       │    │   │
│  │  │          # iteration_feedback: REMOVED                      │    │   │
│  │  │      }                                                       │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EVALUATOR AGENT                                   │   │
│  │                                                                      │   │
│  │  Input (Filtered):                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │  {                                                           │    │   │
│  │  │    "subject_context": { ... },  // Project info only        │    │   │
│  │  │    "deliverable": { ... }       // Final output to review   │    │   │
│  │  │    // NO private_reasoning                                  │    │   │
│  │  │    // NO iteration_feedback                                 │    │   │
│  │  │    // NO tool_call_history                                  │    │   │
│  │  │  }                                                           │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1: Prompt Template Separation

### 3.1 Independent Agent Prompt

```python
INDEPENDENT_AGENT_PROMPT = """
# Agent Identity

{persona}

---

# DocuSwarm Independent Agent Instructions

You are operating as an Independent Agent within the DocuSwarm multi-agent system.

## Your Responsibilities

### 1. Create Deliverable
- Create high-quality deliverable based on Subject Context
- Focus on thoroughness, accuracy, and actionability
- Apply your persona's expertise to the task

### 2. Generate Questions (MANDATORY)
After creating your deliverable, generate at least 3 questions:
- **Blocking**: Critical, must be answered before proceeding
- **Clarifying**: Improve quality but don't block progress
- **Optional**: Nice-to-have for completeness

## Response Format

You MUST respond with valid JSON:

```json
{
  "deliverable": {
    "title": "...",
    "content": "... (markdown formatted)",
    "metadata": { "version": "1.0", "status": "draft" }
  },
  "questions": [
    {
      "id": "q1",
      "category": "blocking|clarifying|optional",
      "text": "...",
      "context": "..."
    }
  ],
  "private_reasoning": "Your internal analysis (NOT shared with Evaluator)"
}
```

## IMPORTANT PRIVACY NOTICE

Your `private_reasoning` field is completely PRIVATE:
- It will NOT be seen by the Evaluator Agent
- Use it to document your thought process
- Include any reasoning, alternatives considered, or uncertainty
- The Evaluator only sees your final deliverable

This isolation ensures objective evaluation of your output.
"""
```

### 3.2 Evaluator Agent Prompt

```python
EVALUATOR_AGENT_PROMPT = """
# Evaluator Agent

You are reviewing a deliverable from an Independent Agent.

## Your Role

- Evaluate the deliverable against provided criteria
- Assign scores (0.0-1.0) for each criterion
- Calculate weighted alignment score
- Provide specific, actionable feedback

## Context Isolation Notice

You do NOT have access to:
- The Independent Agent's reasoning process
- Draft versions of the deliverable
- Tool call history
- Why certain decisions were made

Evaluate ONLY what is present in the final deliverable.
Base your assessment on the content itself, not on assumed intent.

## Evaluation Criteria

{criteria}

## Response Format

```json
{
  "criterion_scores": {
    "completeness": 0.85,
    "clarity": 0.90,
    "consistency": 0.80,
    "actionability": 0.75,
    "evidence_quality": 0.70
  },
  "alignment_score": 0.80,
  "verdict": "APPROVED|NEEDS_REVISION|BLOCKED",
  "issues_found": [
    {
      "severity": "major|minor",
      "description": "...",
      "location": "Section X",
      "remediation": "..."
    }
  ],
  "suggestions": ["...", "..."]
}
```

## IMPORTANT

Base your evaluation ONLY on what you can observe in the deliverable.
Do NOT speculate about the author's intent or process.
Your assessment must be objective and evidence-based.
"""
```

---

## 4. Layer 2: Runtime Access Control

### 4.1 Context Manager Implementation

```python
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    INDEPENDENT = "independent"
    EVALUATOR = "evaluator"

@dataclass
class IndependentContext:
    """Full context for Independent Agent."""
    subject_context: dict
    previous_deliverables: Dict[str, dict]
    iteration_feedback: Optional[dict] = None
    private_memory: Optional[dict] = None

@dataclass
class EvaluatorContext:
    """Restricted context for Evaluator Agent."""
    subject_context: dict
    deliverable: dict
    evaluation_criteria: dict
    # NO private_reasoning
    # NO iteration_feedback
    # NO tool_call_history

class ContextManager:
    """Manages context building with isolation enforcement."""
    
    def __init__(self, state_manager, memory_manager):
        self.state_manager = state_manager
        self.memory_manager = memory_manager
    
    def build_independent_context(
        self,
        run_id: str,
        node_id: str,
        iteration_feedback: dict = None
    ) -> IndependentContext:
        """Build full context for Independent Agent."""
        
        # Load shared context
        subject_context = self.memory_manager.load_shared_memory(run_id)
        
        # Load previous deliverables
        node_run_state = self.state_manager.get_node_run(run_id)
        previous_deliverables = {
            nid: node["deliverable"]
            for nid, node in node_run_state.get("nodes", {}).items()
            if node.get("status") == "completed"
        }
        
        # Load private memory
        agent_id = f"{run_id}_{node_id}_independent"
        private_memory = self.memory_manager.get_private_memory(agent_id)
        
        return IndependentContext(
            subject_context=subject_context,
            previous_deliverables=previous_deliverables,
            iteration_feedback=iteration_feedback,
            private_memory=private_memory
        )
    
    def build_evaluator_context(
        self,
        run_id: str,
        node_id: str,
        deliverable: dict,
        evaluation_criteria: dict
    ) -> EvaluatorContext:
        """Build restricted context for Evaluator Agent.
        
        CRITICAL: This method enforces context isolation.
        Do NOT add private_reasoning, iteration_feedback, or
        any other Independent Agent internals.
        """
        
        # Load ONLY subject context (project info)
        subject_context = self.memory_manager.load_shared_memory(run_id)
        
        # Return restricted context
        return EvaluatorContext(
            subject_context=subject_context,
            deliverable=deliverable,
            evaluation_criteria=evaluation_criteria
            # ISOLATION: No private data included
        )
```

### 4.2 Type Safety

```python
from typing import Protocol, TypedDict

class IndependentAgentInput(TypedDict):
    """Type definition for Independent Agent input."""
    subject_context: dict
    previous_deliverables: dict
    iteration_feedback: dict  # Optional
    private_memory: dict  # Optional

class EvaluatorAgentInput(TypedDict):
    """Type definition for Evaluator Agent input.
    
    Note: This type explicitly EXCLUDES private fields.
    Any attempt to add private_reasoning will cause a type error.
    """
    subject_context: dict
    deliverable: dict
    evaluation_criteria: dict
    # private_reasoning: NOT ALLOWED
    # iteration_feedback: NOT ALLOWED

class ContextBuilder(Protocol):
    """Protocol for context builders with type enforcement."""
    
    def build_for_independent(self) -> IndependentAgentInput: ...
    def build_for_evaluator(self) -> EvaluatorAgentInput: ...
```

---

## 5. Layer 3: Message-Level Filtering

### 5.1 Context Filter Implementation

```python
from typing import Dict, Any, List
from dataclasses import dataclass
import copy
import logging

logger = logging.getLogger(__name__)

@dataclass
class FilterResult:
    """Result of context filtering."""
    filtered_data: dict
    removed_fields: List[str]
    audit_log: List[str]

class ContextFilter:
    """Filters context data to enforce isolation."""
    
    # Fields that must be removed before Evaluator sees data
    PRIVATE_FIELDS = {
        "private_reasoning",
        "iteration_feedback",
        "tool_call_history",
        "intermediate_results",
        "agent_reasoning",
        "thought_process",
        "internal_notes"
    }
    
    # Fields to keep for Evaluator
    ALLOWED_FIELDS = {
        "subject_context",
        "deliverable",
        "evaluation_criteria",
        "questions"  # Questions are public output
    }
    
    def filter_for_evaluator(
        self,
        independent_output: dict,
        context: dict
    ) -> FilterResult:
        """Filter context for Evaluator Agent.
        
        This is the last line of defense for isolation.
        Removes all private fields regardless of how they got there.
        """
        removed_fields = []
        audit_log = []
        
        # Deep copy to avoid mutation
        filtered = copy.deepcopy({
            "subject_context": context.get("subject_context", {}),
            "deliverable": independent_output.get("deliverable", {})
        })
        
        # Remove private fields from deliverable (in case embedded)
        filtered["deliverable"] = self._remove_private_fields(
            filtered["deliverable"],
            removed_fields,
            audit_log
        )
        
        # Remove private fields from context
        filtered["subject_context"] = self._remove_private_fields(
            filtered["subject_context"],
            removed_fields,
            audit_log
        )
        
        # Verify no private data leaked
        self._verify_isolation(filtered, audit_log)
        
        return FilterResult(
            filtered_data=filtered,
            removed_fields=removed_fields,
            audit_log=audit_log
        )
    
    def _remove_private_fields(
        self,
        data: dict,
        removed: List[str],
        audit: List[str]
    ) -> dict:
        """Recursively remove private fields from dict."""
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            # Check if field should be removed
            if key in self.PRIVATE_FIELDS:
                removed.append(key)
                audit.append(f"REMOVED: {key} (private field)")
                continue
            
            # Check for suspicious field names
            if self._is_suspicious_field(key):
                removed.append(key)
                audit.append(f"REMOVED: {key} (suspicious field name)")
                continue
            
            # Recursively filter nested dicts
            if isinstance(value, dict):
                result[key] = self._remove_private_fields(value, removed, audit)
            elif isinstance(value, list):
                result[key] = [
                    self._remove_private_fields(item, removed, audit)
                    if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def _is_suspicious_field(self, field_name: str) -> bool:
        """Check if field name suggests private data."""
        suspicious_patterns = [
            "reasoning",
            "thought",
            "internal",
            "private",
            "hidden",
            "draft",
            "intermediate"
        ]
        
        field_lower = field_name.lower()
        return any(pattern in field_lower for pattern in suspicious_patterns)
    
    def _verify_isolation(self, data: dict, audit: List[str]):
        """Final verification that no private data leaked."""
        data_str = str(data).lower()
        
        # Check for private field names in serialized data
        for private_field in self.PRIVATE_FIELDS:
            if private_field in data_str:
                audit.append(f"WARNING: Potential leak detected - {private_field}")
                logger.warning(f"Context isolation warning: {private_field} may have leaked")
```

### 5.2 Audit Logging

```python
import json
from datetime import datetime
from pathlib import Path

class IsolationAuditLogger:
    """Logs context isolation events for compliance."""
    
    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def log_filter_event(
        self,
        run_id: str,
        node_id: str,
        filter_result: FilterResult
    ):
        """Log a filtering event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "context_filter",
            "run_id": run_id,
            "node_id": node_id,
            "removed_fields": filter_result.removed_fields,
            "audit_log": filter_result.audit_log,
            "isolation_verified": len(filter_result.removed_fields) > 0 or True
        }
        
        log_file = self.log_dir / f"{run_id}_isolation.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def get_isolation_report(self, run_id: str) -> List[dict]:
        """Get all isolation events for a node run."""
        log_file = self.log_dir / f"{run_id}_isolation.jsonl"
        
        if not log_file.exists():
            return []
        
        events = []
        with open(log_file) as f:
            for line in f:
                events.append(json.loads(line))
        
        return events
    
    def verify_isolation_compliance(self, run_id: str) -> dict:
        """Verify that isolation was maintained throughout node run."""
        events = self.get_isolation_report(run_id)
        
        warnings = []
        for event in events:
            for log_entry in event.get("audit_log", []):
                if "WARNING" in log_entry:
                    warnings.append({
                        "timestamp": event["timestamp"],
                        "node_id": event["node_id"],
                        "warning": log_entry
                    })
        
        return {
            "run_id": run_id,
            "total_filter_events": len(events),
            "warnings": warnings,
            "isolation_maintained": len(warnings) == 0
        }
```

---

## 6. Integration in Dual-Agent Node

### 6.1 Node Implementation

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class NodeResult:
    deliverable: dict
    questions: list
    evaluation: dict
    iterations: int
    isolation_verified: bool

class IsolatedDualAgentNode:
    """Dual-agent node with enforced context isolation."""
    
    def __init__(
        self,
        node_id: str,
        context_manager: ContextManager,
        context_filter: ContextFilter,
        audit_logger: IsolationAuditLogger,
        llm_service
    ):
        self.node_id = node_id
        self.context_manager = context_manager
        self.context_filter = context_filter
        self.audit_logger = audit_logger
        self.llm = llm_service
    
    async def execute(
        self,
        run_id: str,
        evaluation_criteria: dict,
        max_iterations: int = 3
    ) -> NodeResult:
        """Execute node with isolation enforcement."""
        
        iteration_feedback = None
        
        for iteration in range(1, max_iterations + 1):
            # STEP 1: Build Independent Agent context (FULL access)
            independent_context = self.context_manager.build_independent_context(
                run_id=run_id,
                node_id=self.node_id,
                iteration_feedback=iteration_feedback
            )
            
            # STEP 2: Execute Independent Agent
            independent_output = await self._run_independent(
                independent_context
            )
            
            # STEP 3: FILTER context for Evaluator (CRITICAL)
            filter_result = self.context_filter.filter_for_evaluator(
                independent_output=independent_output,
                context={
                    "subject_context": independent_context.subject_context
                }
            )
            
            # STEP 4: Log isolation event
            self.audit_logger.log_filter_event(
                run_id=run_id,
                node_id=self.node_id,
                filter_result=filter_result
            )
            
            # STEP 5: Build Evaluator context (RESTRICTED)
            evaluator_context = self.context_manager.build_evaluator_context(
                run_id=run_id,
                node_id=self.node_id,
                deliverable=filter_result.filtered_data["deliverable"],
                evaluation_criteria=evaluation_criteria
            )
            
            # STEP 6: Execute Evaluator Agent
            evaluation = await self._run_evaluator(evaluator_context)
            
            # STEP 7: Check verdict
            if evaluation["verdict"] == "APPROVED":
                return NodeResult(
                    deliverable=independent_output["deliverable"],
                    questions=independent_output["questions"],
                    evaluation=evaluation,
                    iterations=iteration,
                    isolation_verified=True
                )
            
            if evaluation["verdict"] == "BLOCKED":
                break
            
            # NEEDS_REVISION: Prepare feedback for next iteration
            iteration_feedback = {
                "iteration_number": iteration,
                "previous_score": evaluation["alignment_score"],
                "issues": evaluation.get("issues_found", []),
                "suggestions": evaluation.get("suggestions", [])
            }
        
        # Max iterations or blocked
        return NodeResult(
            deliverable=independent_output["deliverable"],
            questions=independent_output["questions"],
            evaluation=evaluation,
            iterations=iteration,
            isolation_verified=True
        )
    
    async def _run_independent(self, context: IndependentContext) -> dict:
        """Execute Independent Agent with full context."""
        # Implementation uses LLM service
        pass
    
    async def _run_evaluator(self, context: EvaluatorContext) -> dict:
        """Execute Evaluator Agent with restricted context."""
        # Implementation uses LLM service
        pass
```

---

## 7. ContextValidator Singleton Pattern (F4 Fix)

> **2026-03-29**: 本文档补充 `ContextValidator` 单例模式使用规范。

### 7.1 Singleton Usage Requirement

为确保节点级验证规则正确传播，全仓必须统一使用 `ContextValidator.get_instance()`：

```python
# ✅ 正确: 使用单例
from autoBMAD.docuswarm.context.validator import ContextValidator

validator = ContextValidator.get_instance()
result = validator.validate_deliverable(deliverable, node_id)
```

```python
# ❌ 错误: 直接实例化 (导致规则不生效)
validator = ContextValidator()  # 创建新实例，忽略已注册规则
result = validator.validate_deliverable(deliverable, node_id)
```

### 7.2 Rule Registration Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContextValidator Rule Registration                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NodeLoader.load(node_id)                                                   │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  validation_rules = node_config.get("validation") or {}             │   │
│  │  validator = ContextValidator.get_instance()  # ✅ 使用单例         │   │
│  │  validator.load_node_rules(node_id, validation_rules)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                     │
│       ▼                                                                     │
│  Singleton 存储规则 {node_id: validation_rules}                             │
│       │                                                                     │
│       ▼                                                                     │
│  实际验证时                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  validator = ContextValidator.get_instance()  # ✅ 读取同一单例     │   │
│  │  result = validator.validate_word_count(text, node_id)              │   │
│  │  # 使用 NodeLoader 注册的规则                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Migration Guide

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| `isolation.py:286` | `self._validator = ContextValidator()` | `self._validator = ContextValidator.get_instance()` |
| `independent.py:430` | `validator = ContextValidator()` | `validator = ContextValidator.get_instance()` |
| `evaluator.py:433` | `validator = ContextValidator()` | `validator = ContextValidator.get_instance()` |

## 8. Verification and Testing

### 7.1 Isolation Verification Tests

```python
import pytest

class TestContextIsolation:
    """Test suite for context isolation."""
    
    def test_evaluator_context_excludes_private_reasoning(self):
        """Verify Evaluator context never includes private_reasoning."""
        context_manager = ContextManager(...)
        
        evaluator_context = context_manager.build_evaluator_context(
            run_id="test",
            node_id="analyst",
            deliverable={"content": "test"},
            evaluation_criteria={}
        )
        
        # Convert to dict and check
        context_dict = evaluator_context.__dict__
        assert "private_reasoning" not in str(context_dict)
        assert "iteration_feedback" not in str(context_dict)
    
    def test_context_filter_removes_private_fields(self):
        """Verify filter removes all private fields."""
        filter = ContextFilter()
        
        independent_output = {
            "deliverable": {"content": "test"},
            "questions": [],
            "private_reasoning": "This should be removed"
        }
        
        result = filter.filter_for_evaluator(
            independent_output,
            {"subject_context": {}}
        )
        
        assert "private_reasoning" not in str(result.filtered_data)
        assert "private_reasoning" in result.removed_fields
    
    def test_nested_private_fields_removed(self):
        """Verify nested private fields are removed."""
        filter = ContextFilter()
        
        independent_output = {
            "deliverable": {
                "content": "test",
                "metadata": {
                    "internal_notes": "Should be removed"
                }
            }
        }
        
        result = filter.filter_for_evaluator(
            independent_output,
            {"subject_context": {}}
        )
        
        assert "internal_notes" not in str(result.filtered_data)
    
    def test_isolation_audit_log_created(self):
        """Verify audit log is created for each filter event."""
        logger = IsolationAuditLogger(log_dir="/tmp/test_audit")
        filter_result = FilterResult(
            filtered_data={},
            removed_fields=["private_reasoning"],
            audit_log=["REMOVED: private_reasoning"]
        )
        
        logger.log_filter_event("test_run", "analyst", filter_result)
        
        events = logger.get_isolation_report("test_run")
        assert len(events) == 1
        assert "private_reasoning" in events[0]["removed_fields"]
```

### 7.2 Integration Test

```python
async def test_full_isolation_workflow():
    """End-to-end test of isolation in dual-agent node."""
    
    # Setup
    node = IsolatedDualAgentNode(...)
    
    # Execute node
    result = await node.execute(
        run_id="test",
        evaluation_criteria={}
    )
    
    # Verify isolation was maintained
    assert result.isolation_verified
    
    # Check audit logs
    audit = IsolationAuditLogger()
    report = audit.verify_isolation_compliance("test")
    
    assert report["isolation_maintained"]
    assert len(report["warnings"]) == 0
```

---

## 8. Security Considerations

### 8.1 Threat Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Context Isolation Threats                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  THREAT 1: Direct Field Inclusion                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Attack: Developer accidentally includes private_reasoning            │ │
│  │  Mitigation: Layer 2 type system + Layer 3 runtime filter            │ │
│  │  Detection: Audit log + automated tests                              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  THREAT 2: Embedded in Deliverable                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Attack: Independent Agent embeds reasoning in deliverable content   │ │
│  │  Mitigation: Cannot fully prevent, but LLM prompt instructs against │ │
│  │  Detection: Audit log warnings for suspicious content                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  THREAT 3: Prompt Injection                                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Attack: Malicious content in subject_context                        │ │
│  │  Mitigation: Input validation, sanitization                         │ │
│  │  Detection: Content scanning                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  THREAT 4: State Persistence Leakage                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Attack: Private data persisted to shared storage                    │ │
│  │  Mitigation: Ephemeral private memory, separate storage              │ │
│  │  Detection: Database auditing                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Defense Summary

| Layer | Defense | Effectiveness |
|-------|---------|---------------|
| **Layer 1** | Separate prompt templates | High - structural separation |
| **Layer 2** | Type-safe context builders | High - compile-time checking |
| **Layer 3** | Runtime filtering | Very High - catches everything |
| **Audit** | Logging and verification | Medium - detection after fact |

---

## 9. File Structure

```
docuswarm/context/
├── __init__.py
├── manager.py           # ContextManager class
├── filter.py            # ContextFilter class
├── isolation.py         # IsolatedDualAgentNode
├── audit.py             # IsolationAuditLogger
└── verification.py      # Verification utilities
```

---

## 10. References

### Related Documents

| Document | Location |
|----------|----------|
| System Architecture | `01_SYSTEM_ARCHITECTURE.md` |
| Agent Architecture | `02_AGENT_ARCHITECTURE.md` |
| State Management | `04_STATE_ARCHITECTURE.md` |

### External References

- [Information Isolation Patterns](https://martinfowler.com/eaaCatalog/)
- [Defense in Depth Security](https://en.wikipedia.org/wiki/Defense_in_depth_(computing))

---

**Document End**
> **2026-03-13 Alignment Notice**: Evaluator 的最小暴露原则仍然成立，但 Independent 输入契约、deliverable 真相来源、docs 扩展路径尚未闭环。因此上下文隔离应与 `../research/2026-03-13-p0-single-context-protocol-plan.md` 和 `../research/2026-03-13-p1-controlled-docs-context-strategy-plan.md` 一起阅读。

>
> **2026-03-17 Update**: 产品已决定工作流完全不读取 \docs/\ 目录。因此：
> - P1-2 (受控 docs 上下文策略) 已从重构计划中移除
> - 所有 docs 相关读取/写入能力应进入清理范围
> - \ContextResolver\ 和 \@path\ 注入不再推进
> - 本文档中关于 docs 扩展的描述应被视为待清理而非待实现
> - 推荐的重构路径请参考 \../research/2026-03-13-docuswarm-context-refactor-overview.md

>
> **2026-03-17 TDD Implementation Plan**: 测试驱动实施方案已制定，包括：
> - Phase 2 (P0-3): Evaluator 强制从文件读取正文，禁止 fallback 到摘要
> - Phase 3 (P0-2): EvaluatorAgentInput 添加 `original_context_summary` 字段
> - 详见 `../solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
>
> **2026-03-29 F4 Fix Update**: `ContextValidator` 单例模式已统一：
> - 所有模块统一使用 `ContextValidator.get_instance()` 替代直接实例化
> - 涉及文件：`isolation.py`, `independent.py`, `evaluator.py`
> - NodeLoader 注册的验证规则现在正确流入实际执行
> - 详见 `../solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md` (F4)