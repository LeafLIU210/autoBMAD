# DocuSwarm Agent System Design Analysis

**Version**: 3.0 (kimi-agent-sdk)  
**Date**: 2026-02-20  
**Category**: Agent System Design  
**Topics Covered**: 2.1 - 2.7  
**Status**: Analysis Complete - Simplified

---

## Executive Summary

This analysis covers 7 topics related to agent design within DocuSwarm's **dual-agent pattern** (simplified from triple-agent). The dual-agent pattern consists of:

1. **Independent Agent**: Creates deliverables + generates questions (embedded capability)
2. **Evaluator Agent**: Reviews deliverables against criteria (context-isolated)

**Key Simplifications from Occam's Razor Analysis**:
- Questioner Agent eliminated - question generation embedded in Independent Agent
- LangGraph StateGraph replaces custom NodeExecutor for agent orchestration
- State-based coordination only for MVP (mailbox pattern deferred)
- OpenAI Functions for MVP → CallableTool2 (kimi-agent-sdk 原生工具体系)
- Memory architecture simplified for dual-agent pattern

**Key Findings**:
- Full BMAD persona XML embedding is feasible with Kimi K2.5's 256K context window
- Hybrid evaluation criteria (universal framework + node-specific weights) provides optimal balance
- Question generation as embedded Independent Agent capability maintains quality while reducing complexity
- State-based coordination is sufficient for MVP sequential execution

**Critical Dependencies**: Architecture decisions (Section 1) with LangGraph framework.

**Development Time Savings**: ~4-6 weeks compared to original triple-agent design.

---

## Topic 2.1: Independent Agent Persona Extraction & Question Generation

### Context

**Simplified Design**: Independent Agent now handles both deliverable creation AND question generation. This eliminates the separate Questioner Agent while maintaining output quality.

BMAD agents have rich XML-structured personas containing:
- Role definition
- Identity and expertise
- Communication style
- Guiding principles
- Domain-specific knowledge

DocuSwarm needs to convert these personas into effective LLM system prompts that also incorporate question generation capabilities.

### Research Findings

**Persona Token Analysis**:

| BMAD Agent | Persona Size | Estimated Tokens |
|------------|--------------|------------------|
| Analyst (Mary) | ~8KB | ~2,000 tokens |
| PM (John) | ~10KB | ~2,500 tokens |
| Designer (Alex) | ~7KB | ~1,750 tokens |
| Architect (Archie) | ~12KB | ~3,000 tokens |
| PO (Jordan) | ~9KB | ~2,250 tokens |

**Kimi K2.5 Context Efficiency**:
- 256K context window accommodates full personas + question generation prompts
- Context caching: $0.10/M tokens (cache hit) vs $0.60/M (cache miss)
- Full persona embedding enables 83% cost reduction on repeated calls

**Dual-Agent vs Triple-Agent Output Quality**:

| Aspect | Triple-Agent | Dual-Agent (Embedded Questions) |
|--------|--------------|--------------------------------|
| Question Relevance | High (dedicated agent) | High (same context) |
| Deliverable Quality | High | High |
| Context Coherence | Medium (agent handoff) | High (unified context) |
| Token Efficiency | Low (3 agents) | High (2 agents) |
| Implementation Complexity | High | Medium |

### Implementation Guidance

**Persona Extraction with Question Generation (Python/LangGraph)**:

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import re

@dataclass
class AgentPersona:
    role: str
    identity: str
    expertise: str
    communication_style: str
    principles: List[str]
    domain_knowledge: str

def extract_persona(agent_markdown_path: str) -> AgentPersona:
    """Extract BMAD persona from markdown file."""
    with open(agent_markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    def extract_section(content: str, section_name: str) -> str:
        pattern = rf'<{section_name}>(.*?)</{section_name}>'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    return AgentPersona(
        role=extract_section(content, 'role'),
        identity=extract_section(content, 'identity'),
        expertise=extract_section(content, 'expertise'),
        communication_style=extract_section(content, 'communication-style'),
        principles=[p.strip() for p in extract_section(content, 'principles').split('\n') if p.strip()],
        domain_knowledge=extract_section(content, 'domain-knowledge')
    )

def build_independent_agent_prompt(persona: AgentPersona, node_id: str) -> str:
    """Build system prompt with embedded question generation capability."""
    return f"""
# Agent Identity

You are {persona.identity}.

## Role
{persona.role}

## Expertise
{persona.expertise}

## Communication Style
{persona.communication_style}

## Guiding Principles
{chr(10).join(f'- {p}' for p in persona.principles)}

## Domain Knowledge
{persona.domain_knowledge}

---

# DocuSwarm Independent Agent Instructions

You are operating as an Independent Agent within the DocuSwarm multi-agent system.
Your responsibilities are:

## 1. Create Deliverable
- Create high-quality deliverables based on the Subject Context provided
- Focus on thoroughness, accuracy, and actionability
- Apply your persona's expertise to the task

## 2. Generate Questions (MANDATORY)
After creating your deliverable, you MUST generate at least 3 questions.

### Question Categories:
- **Blocking**: Critical questions that MUST be answered before next node
- **Clarifying**: Questions that improve quality but don't block progress
- **Optional**: Nice-to-have clarifications for thoroughness

### Question Requirements:
- Minimum 3 questions total
- At least 1 blocking question
- Questions must be actionable (user can answer)
- Questions must relate to your deliverable content

## Response Format

You MUST respond with valid JSON in this exact format:
```json
{{
  "deliverable": {{
    "title": "...",
    "content": "... (markdown formatted)",
    "metadata": {{
      "version": "1.0",
      "status": "draft"
    }}
  }},
  "questions": [
    {{
      "id": "q1",
      "category": "blocking|clarifying|optional",
      "text": "The actual question",
      "context": "Why this question matters"
    }}
  ],
  "private_reasoning": "Your internal analysis (not shared with Evaluator)"
}}
```

IMPORTANT: 
- Your private_reasoning is NOT visible to the Evaluator Agent
- The Evaluator only sees your deliverable and subject context
- Questions are ALWAYS required, regardless of deliverable quality
""".strip()
```

**LangGraph Independent Agent Node**:

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List, Any
import json

class NodeState(TypedDict):
    subject_context: dict
    deliverable: Optional[dict]
    questions: Optional[List[dict]]
    private_reasoning: Optional[str]
    evaluation: Optional[dict]
    iteration: int

class IndependentAgentNode:
    def __init__(self, node_id: str, persona_path: str, session_manager):
        self.node_id = node_id
        self.persona = extract_persona(persona_path)
        self.system_prompt = build_independent_agent_prompt(self.persona, node_id)
        self.session_mgr = session_manager  # KimiSessionManager
    
    async def execute(self, state: NodeState) -> NodeState:
        """Execute Independent Agent: create deliverable + generate questions."""
        session = await self.session_mgr.create_session(
            session_id=f"docuswarm-{self.node_id}-iter{state.get('iteration', 0)}",
            mode="agent",
        )
        
        async with session:
            messages = []
            async for wire_msg in session.prompt(self._build_task_prompt(state)):
                from kimi_agent_sdk import ApprovalRequest
                from kimi_agent_sdk.types import MessageAggregator
                if isinstance(wire_msg, ApprovalRequest):
                    wire_msg.resolve("approve")
                    continue
                # MessageAggregator 处理...
                messages.append(wire_msg)
        
        # 从 SDK Message 提取结构化内容
        result = self._parse_response(messages)
        
        # Validate questions were generated
        if not result.get("questions") or len(result["questions"]) < 3:
            result["questions"] = self._ensure_minimum_questions(
                result.get("questions", []),
                state["subject_context"],
                result.get("deliverable", {})
            )
        
        return {
            **state,
            "deliverable": result["deliverable"],
            "questions": result["questions"],
            "private_reasoning": result.get("private_reasoning", "")
        }
    
    def _build_task_prompt(self, state: NodeState) -> str:
        context = state["subject_context"]
        iteration = state.get("iteration", 0)
        
        prompt = f"""
## Subject Context
{json.dumps(context, indent=2, ensure_ascii=False)}

## Task
Create the {self.node_id} deliverable based on the subject context above.
"""
        
        if iteration > 0 and state.get("evaluation"):
            prompt += f"""

## Previous Evaluation Feedback
This is iteration {iteration + 1}. Please address the following feedback:
{json.dumps(state["evaluation"], indent=2, ensure_ascii=False)}
"""
        
        return prompt
    
    def _ensure_minimum_questions(
        self, 
        existing: List[dict], 
        context: dict, 
        deliverable: dict
    ) -> List[dict]:
        """Ensure at least 3 questions, with fallbacks if needed."""
        questions = list(existing)
        
        fallbacks = [
            {
                "id": f"fallback_{len(questions)+1}",
                "category": "blocking",
                "text": "Are there any critical constraints or requirements not mentioned in the current context?",
                "context": "Ensuring completeness of requirements"
            },
            {
                "id": f"fallback_{len(questions)+2}",
                "category": "clarifying",
                "text": "Are there specific stakeholders whose input should be incorporated before proceeding?",
                "context": "Stakeholder alignment"
            },
            {
                "id": f"fallback_{len(questions)+3}",
                "category": "optional",
                "text": "Are there any timeline or resource constraints that should influence the approach?",
                "context": "Resource planning"
            }
        ]
        
        while len(questions) < 3:
            questions.append(fallbacks[len(questions)])
        
        return questions
```

### Recommendation

**Full XML Embedding with Embedded Question Generation**.

Rationale:
- 256K context easily accommodates personas + question generation prompts
- Context caching reduces cost by 83% on subsequent calls
- Preserves full behavioral nuance from BMAD personas
- Eliminates Questioner Agent while maintaining output quality
- Questions benefit from same context as deliverable creation

---

## Topic 2.2: Evaluator Agent Review Criteria

### Context

The Evaluator Agent reviews Independent Agent deliverables and produces:
- Verdict (APPROVED, NEEDS_REVISION, BLOCKED)
- Alignment score (0.0-1.0)
- Issues found
- Suggestions for improvement

**Key Principle**: Evaluator does NOT see Independent Agent's private reasoning - context isolation maintained.

### Research Findings

**BMAD Validation Pattern Analysis**:

| BMAD Workflow | Criteria Focus | Applicable To |
|---------------|---------------|---------------|
| validate-prd | Completeness, clarity, technical feasibility | PM node |
| check-implementation-readiness | Cross-document alignment | Architect node |
| review-adversarial-general | Critical thinking, edge cases | All nodes |

**Evaluation Dimension Framework**:

| Dimension | Description | Measurement Method |
|-----------|-------------|-------------------|
| **Completeness** | All required sections present | Checklist |
| **Clarity** | Understandable to target audience | Readability metrics |
| **Consistency** | No internal contradictions | Cross-reference |
| **Actionability** | Clear next steps | Task extraction |
| **Evidence Quality** | Claims backed by data/reasoning | Citation check |

### Implementation Guidance

**Hybrid Criteria Framework (YAML)**:

```yaml
# evaluator-framework.yaml
universal_criteria:
  completeness:
    description: "All required sections present"
    default_weight: 0.20
    measurement: checklist
    
  clarity:
    description: "Understandable to target audience"
    default_weight: 0.20
    measurement: readability_score
    
  consistency:
    description: "Internal coherence, no contradictions"
    default_weight: 0.20
    measurement: cross_reference
    
  actionability:
    description: "Provides clear next steps"
    default_weight: 0.20
    measurement: task_extraction
    
  evidence_quality:
    description: "Claims backed by data/reasoning"
    default_weight: 0.20
    measurement: citation_check

node_overrides:
  analyst:
    weights:
      evidence_quality: 0.40
      completeness: 0.30
      actionability: 0.30
        
  pm:
    weights:
      completeness: 0.40
      clarity: 0.30
      actionability: 0.30
        
  architect:
    weights:
      consistency: 0.35
      completeness: 0.35
      clarity: 0.30

# Simplified verdicts for MVP
verdict_thresholds:
  APPROVED: 0.70          # >= 70% alignment
  NEEDS_REVISION: 0.40    # 40-69% alignment
  BLOCKED: 0.0            # < 40% alignment
```

**LangGraph Evaluator Agent Node**:

```python
class EvaluatorAgentNode:
    def __init__(self, node_id: str, criteria_config: dict, session_manager):
        self.node_id = node_id
        self.criteria = self._load_criteria(criteria_config, node_id)
        self.session_mgr = session_manager  # KimiSessionManager
    
    def _load_criteria(self, config: dict, node_id: str) -> dict:
        """Load criteria with node-specific weight overrides."""
        criteria = config["universal_criteria"].copy()
        
        if node_id in config.get("node_overrides", {}):
            overrides = config["node_overrides"][node_id]
            for criterion, weight in overrides.get("weights", {}).items():
                if criterion in criteria:
                    criteria[criterion]["weight"] = weight
        
        return criteria
    
    async def evaluate(self, state: NodeState) -> NodeState:
        """Evaluate deliverable - NO access to private_reasoning (context isolation)."""
        
        # CRITICAL: Context isolation - only pass subject_context and deliverable
        evaluation_context = {
            "subject_context": state["subject_context"],
            "deliverable": state["deliverable"]
            # NOTE: private_reasoning is NOT included - isolation enforced
        }
        
        system_prompt = self._build_evaluator_prompt()
        user_prompt = f"""
## Subject Context
{json.dumps(evaluation_context["subject_context"], indent=2, ensure_ascii=False)}

## Deliverable to Review
{json.dumps(evaluation_context["deliverable"], indent=2, ensure_ascii=False)}

## Evaluation Criteria
{json.dumps(self.criteria, indent=2, ensure_ascii=False)}

Evaluate the deliverable against each criterion and provide your assessment.
"""
        
        # 使用 prompt() 单次 API + thinking 模式
        messages = await self.session_mgr.single_prompt(
            user_input=user_prompt,
            mode="thinking",
        )
        evaluation = self._parse_evaluation(messages)
        
        return {
            **state,
            "evaluation": evaluation
        }
    
    def _build_evaluator_prompt(self) -> str:
        return """
# Evaluator Agent

You are reviewing a deliverable from an Independent Agent.

## Your Role
- Evaluate the deliverable against the provided criteria
- Assign scores (0.0-1.0) for each criterion
- Calculate weighted alignment score
- Provide specific, actionable feedback

## Context Isolation Notice
You do NOT have access to the Independent Agent's reasoning or drafts.
Evaluate ONLY what is present in the deliverable.

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
  "suggestions": [
    "Specific improvement suggestion 1",
    "Specific improvement suggestion 2"
  ]
}
```

IMPORTANT: Base your evaluation ONLY on the deliverable content, not assumptions about the author's intent.
""".strip()
```

### Recommendation

**Hybrid Framework**: Universal criteria + node-specific weight overrides.

Benefits:
- Consistent baseline across all nodes
- Node-specific tuning for domain relevance
- Transparent scoring methodology
- Context isolation maintained by design

---

## Topic 2.3: Question Generation as Embedded Capability

### Context

**Occam's Razor Simplification**: The separate Questioner Agent has been eliminated. Question generation is now an embedded capability of the Independent Agent.

**Rationale**:
- Questioner used same context as Independent Agent
- No unique persona benefit (generic question generation)
- Embedded approach reduces LLM calls by 33%
- Questions are more contextually relevant when generated alongside deliverable

### Research Findings

**Comparison: Separate vs Embedded Question Generation**:

| Aspect | Separate Questioner Agent | Embedded in Independent Agent |
|--------|--------------------------|------------------------------|
| LLM Calls per Node | 3 | 2 |
| Context Switching | Required | None |
| Question Relevance | High | Higher (same context) |
| Implementation Complexity | High | Medium |
| Token Usage | ~50% higher | Baseline |
| Failure Points | 3 agents | 2 agents |

**Quality Assurance Mechanisms**:

| Mechanism | Purpose | Implementation |
|-----------|---------|----------------|
| **Minimum Count Validation** | Ensure coverage | Response validation |
| **Category Diversity Check** | Mix of question types | Post-processing |
| **Fallback Generation** | Guarantee output | Default questions |

### Implementation Guidance

**Question Generation Validation (Embedded in Node Executor)**:

```python
class QuestionValidator:
    """Validates and ensures question quality in dual-agent pattern."""
    
    MIN_QUESTIONS = 3
    REQUIRED_CATEGORIES = ["blocking"]
    
    def validate_and_augment(
        self, 
        questions: List[dict], 
        context: dict,
        deliverable: dict
    ) -> List[dict]:
        """Validate questions meet requirements, augment if needed."""
        validated = []
        
        for q in questions:
            if self._is_valid_question(q):
                validated.append(q)
        
        # Ensure minimum count
        if len(validated) < self.MIN_QUESTIONS:
            validated.extend(
                self._generate_fallback_questions(
                    self.MIN_QUESTIONS - len(validated),
                    context,
                    deliverable
                )
            )
        
        # Ensure category diversity
        categories = {q.get("category") for q in validated}
        for required in self.REQUIRED_CATEGORIES:
            if required not in categories:
                validated.append(
                    self._generate_category_question(required, context, deliverable)
                )
        
        return validated
    
    def _is_valid_question(self, question: dict) -> bool:
        """Check if question meets basic validity criteria."""
        required_fields = ["id", "category", "text"]
        return all(question.get(f) for f in required_fields)
    
    def _generate_fallback_questions(
        self, 
        count: int, 
        context: dict,
        deliverable: dict
    ) -> List[dict]:
        """Generate fallback questions when LLM output insufficient."""
        fallbacks = [
            {
                "id": "fallback_blocking_1",
                "category": "blocking",
                "text": "Are there any critical constraints or requirements not mentioned that could impact this deliverable?",
                "context": "Ensuring completeness of requirements"
            },
            {
                "id": "fallback_clarifying_1",
                "category": "clarifying",
                "text": "Which stakeholders should review this deliverable before proceeding?",
                "context": "Stakeholder alignment"
            },
            {
                "id": "fallback_optional_1",
                "category": "optional",
                "text": "Are there any timeline or budget constraints that should influence the approach?",
                "context": "Resource planning"
            }
        ]
        return fallbacks[:count]
    
    def _generate_category_question(
        self, 
        category: str, 
        context: dict,
        deliverable: dict
    ) -> dict:
        """Generate a question for a specific category."""
        templates = {
            "blocking": {
                "id": f"required_{category}_1",
                "category": category,
                "text": "What information is absolutely required before proceeding to the next stage?",
                "context": "Critical path validation"
            },
            "clarifying": {
                "id": f"required_{category}_1",
                "category": category,
                "text": "Are there any ambiguous requirements that need clarification?",
                "context": "Requirement refinement"
            },
            "optional": {
                "id": f"required_{category}_1",
                "category": category,
                "text": "Are there any additional considerations for future iterations?",
                "context": "Future planning"
            }
        }
        return templates.get(category, templates["clarifying"])
```

**Dual-Agent Node Execution Flow**:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class DualAgentNode:
    """LangGraph node implementing dual-agent pattern."""
    
    def __init__(self, node_id: str, config: dict, db_path: str = "docuswarm.db"):
        self.node_id = node_id
        self.graph = StateGraph(NodeState)
        self.checkpointer = SqliteSaver.from_conn_string(db_path)
        self.question_validator = QuestionValidator()
        
        # Initialize agents (注入 KimiSessionManager)
        self.independent = IndependentAgentNode(
            node_id, 
            config["persona_path"],
            config["session_manager"]  # KimiSessionManager
        )
        self.evaluator = EvaluatorAgentNode(
            node_id,
            config["criteria"],
            config["session_manager"]  # KimiSessionManager
        )
        
        # Build graph: Independent -> Evaluator -> Decision
        self.graph.add_node("independent", self._run_independent)
        self.graph.add_node("evaluator", self._run_evaluator)
        self.graph.add_node("decide", self._decide_next)
        
        self.graph.set_entry_point("independent")
        self.graph.add_edge("independent", "evaluator")
        self.graph.add_edge("evaluator", "decide")
        self.graph.add_conditional_edges(
            "decide",
            self._should_iterate,
            {
                "iterate": "independent",
                "complete": END
            }
        )
        
        self.compiled = self.graph.compile(checkpointer=self.checkpointer)
    
    async def _run_independent(self, state: NodeState) -> NodeState:
        """Execute Independent Agent: deliverable + questions."""
        result = await self.independent.execute(state)
        
        # Validate and augment questions
        result["questions"] = self.question_validator.validate_and_augment(
            result.get("questions", []),
            state["subject_context"],
            result.get("deliverable", {})
        )
        
        return result
    
    async def _run_evaluator(self, state: NodeState) -> NodeState:
        """Execute Evaluator Agent: review deliverable (context isolated)."""
        return await self.evaluator.evaluate(state)
    
    def _decide_next(self, state: NodeState) -> NodeState:
        """Determine next action based on evaluation."""
        return state
    
    def _should_iterate(self, state: NodeState) -> str:
        """Decide whether to iterate or complete."""
        evaluation = state.get("evaluation", {})
        verdict = evaluation.get("verdict", "NEEDS_REVISION")
        iteration = state.get("iteration", 0)
        max_iterations = 3
        
        if verdict == "APPROVED":
            return "complete"
        elif iteration >= max_iterations:
            return "complete"  # Force completion after max iterations
        else:
            return "iterate"
    
    async def execute(self, initial_context: dict) -> NodeState:
        """Execute the dual-agent node."""
        initial_state: NodeState = {
            "subject_context": initial_context,
            "deliverable": None,
            "questions": None,
            "private_reasoning": None,
            "evaluation": None,
            "iteration": 0
        }
        
        config = {"configurable": {"thread_id": f"{self.node_id}_{id(initial_context)}"}}
        final_state = await self.compiled.ainvoke(initial_state, config)
        
        return final_state
```

### Recommendation

**Embedded Question Generation with Validation Layer**.

Implementation:
- Independent Agent prompt includes question generation requirements
- Validation layer ensures minimum questions and category diversity
- Fallback mechanism guarantees output even if LLM fails
- No separate Questioner Agent - reduced complexity by 33%

---

## Topic 2.4: Agent Tool Calling Interface (kimi-agent-sdk)

### Context

Independent Agents need tools for:
- Document creation (deliverables)
- State updates (pipeline state)
- External data access (if needed)

**kimi-agent-sdk 改造**: 
- CallableTool2 + Pydantic 替代手动 JSON Schema
- agent_file.yaml 声明式注册
- SDK 自动调度 tool_calls，无需手动解析
- RAG queries deferred to Phase 2

### Research Findings

**Tool 定义方式对比**:

| 方式 | Token 开销 | 类型安全 | 自动调度 | 当前状态 |
|------|-----------|---------|---------|---------|
| **手动 JSON Schema (旧)** | 中等 | 无 | 否 | 已废弃 |
| **CallableTool2 + Pydantic (新)** | 低 | 强 | 是 (SDK) | **当前方案** |

**MVP Tool Scope**:

| Tool | MVP Status | 实现方式 |
|------|-----------|---------|
| create_deliverable | Included | CallableTool2 |
| update_context | Included | CallableTool2 |
| query_knowledge_base | Deferred | Phase 2 |

### Implementation Guidance

**CallableTool2 工具定义**:

```python
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue

class CreateDeliverableParams(BaseModel):
    document_type: str = Field(description="Type of document to create")
    title: str = Field(description="Document title")
    content: str = Field(description="Document content in Markdown format")

class CreateDeliverableTool(CallableTool2):
    name: str = "create_deliverable"
    description: str = "Create or update a deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    def __init__(self, output_handler):
        super().__init__()
        self._output_handler = output_handler

    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        try:
            self._output_handler.save(
                doc_type=params.document_type,
                title=params.title,
                content=params.content,
            )
            return ToolOk(output=f"Deliverable '{params.title}' created")
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Create failed")


class UpdateContextParams(BaseModel):
    key: str = Field(description="Context key (e.g., 'constraints', 'requirements')")
    value: dict = Field(description="Value to store")
    operation: str = Field(default="set", description="set | append | remove")

class UpdateContextTool(CallableTool2):
    name: str = "update_context"
    description: str = "Add or update information in the shared subject context"
    params: type[UpdateContextParams] = UpdateContextParams

    def __init__(self, context_store):
        super().__init__()
        self._store = context_store

    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        try:
            self._store.update(key=params.key, value=params.value, operation=params.operation)
            return ToolOk(output=f"Context '{params.key}' updated ({params.operation})")
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Update failed")
```

**agent_file.yaml 注册**:

```yaml
version: 1
agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.update_context:UpdateContextTool"
```

**SDK 自动调度流程**:

```
SDK 接收 ToolCall WireMessage
  → 反序列化参数 (Pydantic BaseModel)
  → 调用 tool.__call__(params)
  → 获取 ToolOk/ToolError
  → 自动发送 ToolResult WireMessage
  → 无需 Agent 代码手动处理
```

### Recommendation

**CallableTool2 + agent_file.yaml** — SDK 原生工具体系。

MVP Scope:
- 2 core tools: create_deliverable, update_context
- No RAG queries (Phase 2)
- SDK 自动调度，无需手动解析 tool_calls
- Pydantic 参数验证保证类型安全

Benefits:
- 代码量减少 (无需 ToolExecutor 手动路由)
- 类型安全 (Pydantic BaseModel)
- 声明式注册 (agent_file.yaml)
- MCP 迁移不再需要

### Implementation Gap (2026-02-23)

> **Reference**: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

**发现**: 上述 CallableTool2 工具实现和 agent_file.yaml 配置已完整，但运行时未被激活。IndependentAgent 创建 Session 时未传入 `agent_file` 和 `work_dir` 参数，导致 SDK 不注册任何工具。同时，Independent Agent 系统提示词存在冲突：要求"使用工具创建 deliverable"的同时要求"只返回 JSON"。

**影响**: 所有 deliverable 产出为空占位符 `{}`（假性成功）。

**修复 (方案C)**: 传入 `agent_file` + 设置 `work_dir` + 修改提示词移除 JSON-only 要求。详见 `02_AGENT_ARCHITECTURE.md` Section 10。

---

## Topic 2.5: Agent Memory Architecture (Simplified)

### Context

DocuSwarm requires:
1. **Shared Subject Context**: Project requirements, constraints, decisions - accessible to all agents
2. **Private Memory**: Independent Agent's reasoning - isolated from Evaluator

**Occam's Razor Simplification**: Memory architecture simplified for dual-agent pattern. No separate Questioner memory needed.

### Research Findings

**Memory Architecture Comparison**:

| Pattern | Consistency | Isolation | Complexity |
|---------|-------------|-----------|------------|
| **Centralized** | Strong | None | Low |
| **Distributed** | Eventual | Strong | High |
| **Hybrid (MVP)** | Strong (shared), Ephemeral (private) | By design | Medium |

### Implementation Guidance

**Simplified Memory Manager**:

```python
from typing import Dict, Any, Optional
import sqlite3
import json

class MemoryManager:
    """Simplified memory manager for dual-agent pattern."""
    
    def __init__(self, db_path: str = "docuswarm.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._initialize_tables()
        self.private_memory: Dict[str, dict] = {}  # In-memory, ephemeral
    
    def _initialize_tables(self):
        """Initialize SQLite tables for subject context."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS subject_context (
                pipeline_id TEXT PRIMARY KEY,
                context_data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    # === Subject Context: Shared across agents ===
    
    def load_subject_context(self, pipeline_id: str) -> dict:
        """Load shared subject context."""
        cursor = self.conn.execute(
            "SELECT context_data FROM subject_context WHERE pipeline_id = ?",
            (pipeline_id,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else {}
    
    def save_subject_context(self, pipeline_id: str, context: dict):
        """Save shared subject context."""
        self.conn.execute("""
            INSERT OR REPLACE INTO subject_context (pipeline_id, context_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (pipeline_id, json.dumps(context, ensure_ascii=False)))
        self.conn.commit()
    
    def update_subject_context(self, pipeline_id: str, key: str, value: Any, operation: str = "set"):
        """Update specific key in subject context."""
        context = self.load_subject_context(pipeline_id)
        
        if operation == "set":
            context[key] = value
        elif operation == "append":
            if key not in context:
                context[key] = []
            context[key].append(value)
        elif operation == "remove":
            context.pop(key, None)
        
        self.save_subject_context(pipeline_id, context)
    
    # === Private Memory: Per-agent, ephemeral ===
    
    def initialize_private_memory(self, agent_id: str):
        """Initialize ephemeral private memory for agent."""
        self.private_memory[agent_id] = {
            "reasoning": [],
            "tool_calls": []
        }
    
    def append_private_memory(self, agent_id: str, memory_type: str, content: Any):
        """Append to agent's private memory."""
        if agent_id not in self.private_memory:
            self.initialize_private_memory(agent_id)
        
        if memory_type in self.private_memory[agent_id]:
            self.private_memory[agent_id][memory_type].append(content)
    
    def get_private_memory(self, agent_id: str) -> Optional[dict]:
        """Get agent's private memory (for Independent Agent only)."""
        return self.private_memory.get(agent_id)
    
    def clear_private_memory(self, agent_id: str):
        """Clear private memory after node completion."""
        self.private_memory.pop(agent_id, None)
    
    # === Context Building for Agents ===
    
    def build_agent_context(
        self, 
        agent_id: str, 
        agent_type: str, 
        pipeline_id: str
    ) -> dict:
        """Build context for agent with appropriate access control."""
        subject_context = self.load_subject_context(pipeline_id)
        
        if agent_type == "independent":
            # Full access: subject + private
            return {
                "subject": subject_context,
                "private": self.get_private_memory(agent_id)
            }
        else:
            # Evaluator: subject only (context isolation)
            return {
                "subject": subject_context
                # NO private - isolation enforced
            }
```

### Recommendation

**Simplified Hybrid Architecture**: Centralized Subject Context (SQLite) + Ephemeral Private Memory (in-memory).

Benefits:
- Subject Context persisted in SQLite with WAL mode
- Private memory is ephemeral (no persistence needed)
- Context isolation enforced by design in build_agent_context
- No Questioner memory management (eliminated agent)

---

## Topic 2.6: Agent Coordination Protocol (Simplified)

### Context

**Occam's Razor Simplification**: MVP uses sequential execution only. DAG-based parallel execution deferred to Phase 2.

For MVP sequential execution, coordination is simple:
- Pipeline progresses node by node
- No parallel execution, no task claiming conflicts
- State-based tracking via SQLite

### Research Findings

**Coordination Patterns**:

| Pattern | Complexity | MVP Fit | When Needed |
|---------|------------|---------|-------------|
| **State-Based** | Low | Excellent | MVP |
| **Mailbox/Actor** | Medium | Deferred | Parallel execution |
| **Event Bus** | High | Overkill | Distributed systems |

### Implementation Guidance

**MVP Sequential Coordinator**:

```python
from enum import Enum
from typing import List, Optional

class NodeStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class SequentialCoordinator:
    """Simple coordinator for MVP sequential execution."""
    
    # Fixed sequential order for MVP
    PIPELINE_SEQUENCE = ["analyst", "pm", "ux", "architect", "po"]
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def get_next_node(self, pipeline_id: str) -> Optional[str]:
        """Get the next node to execute in sequence."""
        state = self.state_manager.load_state(pipeline_id)
        
        for node_id in self.PIPELINE_SEQUENCE:
            node_state = state.get("nodes", {}).get(node_id, {})
            status = node_state.get("status", NodeStatus.PENDING.value)
            
            if status == NodeStatus.PENDING.value:
                return node_id
            elif status == NodeStatus.IN_PROGRESS.value:
                return node_id  # Resume in-progress node
            elif status == NodeStatus.FAILED.value:
                return node_id  # Retry failed node
        
        return None  # All nodes completed
    
    def start_node(self, pipeline_id: str, node_id: str) -> bool:
        """Mark node as in-progress."""
        return self.state_manager.update_node_status(
            pipeline_id, 
            node_id, 
            NodeStatus.IN_PROGRESS.value
        )
    
    def complete_node(self, pipeline_id: str, node_id: str, result: dict) -> bool:
        """Mark node as completed."""
        return self.state_manager.update_node_status(
            pipeline_id,
            node_id,
            NodeStatus.COMPLETED.value,
            result=result
        )
    
    def fail_node(self, pipeline_id: str, node_id: str, error: str) -> bool:
        """Mark node as failed."""
        return self.state_manager.update_node_status(
            pipeline_id,
            node_id,
            NodeStatus.FAILED.value,
            error=error
        )
    
    def is_pipeline_complete(self, pipeline_id: str) -> bool:
        """Check if all nodes are completed."""
        state = self.state_manager.load_state(pipeline_id)
        
        for node_id in self.PIPELINE_SEQUENCE:
            node_state = state.get("nodes", {}).get(node_id, {})
            if node_state.get("status") != NodeStatus.COMPLETED.value:
                return False
        
        return True
```

### Recommendation

**State-Based Sequential Coordination** for MVP.

Benefits:
- Leverages SQLite state management
- Simple to implement and debug
- No race conditions (sequential execution)
- Clear path to Phase 2 parallel execution

Phase 2 Enhancement Path:
- Add DAG dependency resolution
- Implement task claiming with optimistic locking
- Optional mailbox pattern for inter-agent communication

---

## Topic 2.7: Agent Failure Recovery

### Context

Agents may fail due to:
- API errors (rate limits, timeouts)
- Quality issues (low alignment scores)
- Infrastructure problems

Need graceful degradation and recovery.

### Research Findings

**Failure Handling Patterns**:

| Pattern | Recovery Time | Complexity | Reliability |
|---------|--------------|------------|-------------|
| **Immediate Fail** | None | Low | Low |
| **Retry with Backoff** | Seconds-Minutes | Medium | High |
| **Circuit Breaker** | Prevents cascade | Medium | Very High |

**Kimi K2.5 Rate Limits** (Tier 3):
- 20 concurrent requests
- 200 RPM
- 5M TPM

### Implementation Guidance

**Simplified Failure Recovery (MVP)**:

```python
import asyncio
from typing import Callable, Any, Optional

class AgentExecutorWithRecovery:
    """Agent executor with retry and backoff for MVP."""
    
    def __init__(
        self, 
        session_manager,
        max_retries: int = 3,
        backoff_base: float = 1.0
    ):
        self.session_mgr = session_manager  # KimiSessionManager
        self.max_retries = max_retries
        self.backoff_base = backoff_base
    
    async def execute_with_retry(
        self, 
        operation: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Execute operation with retry and exponential backoff."""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
                
            except Exception as e:
                last_error = e
                
                if not self._is_retryable(e):
                    raise
                
                if attempt < self.max_retries:
                    delay = self.backoff_base * (2 ** (attempt - 1))
                    print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        
        raise last_error
    
    def _is_retryable(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        error_str = str(error).lower()
        retryable_indicators = [
            "rate limit",
            "timeout",
            "connection",
            "503",
            "502",
            "429"
        ]
        return any(indicator in error_str for indicator in retryable_indicators)


class DualAgentExecutor:
    """Execute dual-agent pattern with failure recovery."""
    
    def __init__(self, config: dict):
        self.executor = AgentExecutorWithRecovery(
            config["session_manager"],
            max_retries=config.get("max_retries", 3)
        )
        self.max_iterations = config.get("max_iterations", 3)
    
    async def execute_node(
        self, 
        node: 'DualAgentNode', 
        context: dict
    ) -> dict:
        """Execute a dual-agent node with failure handling."""
        try:
            result = await self.executor.execute_with_retry(
                node.execute,
                context
            )
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "recoverable": self.executor._is_retryable(e)
            }
    
    async def execute_with_iteration_limit(
        self,
        node: 'DualAgentNode',
        context: dict
    ) -> dict:
        """Execute with iteration limit for quality issues."""
        state = {"subject_context": context, "iteration": 0}
        
        for iteration in range(self.max_iterations):
            state["iteration"] = iteration
            
            result = await self.execute_node(node, state)
            
            if not result["success"]:
                return result
            
            verdict = result["result"].get("evaluation", {}).get("verdict")
            
            if verdict == "APPROVED":
                return result
            elif verdict == "BLOCKED":
                return {
                    "success": False,
                    "error": "Deliverable blocked by evaluator",
                    "result": result["result"]
                }
            
            # NEEDS_REVISION: continue iteration
            state = result["result"]
        
        # Max iterations reached
        return {
            "success": True,
            "result": state,
            "note": f"Completed after {self.max_iterations} iterations (max reached)"
        }
```

### Recommendation

**Retry with Exponential Backoff + Iteration Limits** for MVP.

Configuration:
- Max retries: 3 (for API errors)
- Backoff base: 1 second
- Max iterations: 3 (for quality improvement)

Benefits:
- Handles transient API failures gracefully
- Prevents infinite iteration loops
- Simple implementation without circuit breaker complexity
- Sufficient for MVP single-user scenarios

Phase 2 Enhancement Path:
- Add circuit breaker for high-traffic scenarios
- Add fallback provider support
- Implement distributed failure tracking

---

## Cross-Topic Dependencies (Updated for Dual-Agent Pattern)

```
2.1 Persona Extraction + Question Generation
 └─→ 1.1 Dual-Agent Pattern (simplified execution)
 └─→ 4.1 LLM Provider (context window requirements)

2.2 Evaluator Criteria
 └─→ 7.1 Alignment Scoring (scoring implementation)
 └─→ 7.2 Quality Gates (threshold definitions)

2.3 Embedded Question Generation
 └─→ 1.1 Dual-Agent Pattern (embedded in Independent Agent)
 └─→ 1.5 Response Structure (dual output format)

2.4 Tool Calling (kimi-agent-sdk)
 └─→ CallableTool2 + Pydantic (SDK 原生)
 └─→ agent_file.yaml 声明式注册
 └─→ MVP scope: 2 core tools only

2.5 Agent Memory (Simplified)
 └─→ 1.2 Context Isolation (isolation enforcement)
 └─→ 1.6 SQLite State Management

2.6 Coordination Protocol (Simplified)
 └─→ 1.7 Sequential Execution (MVP only)
 └─→ Phase 2: DAG support

2.7 Failure Recovery
 └─→ 6.3 Provider Configuration
 └─→ 8.3 Monitoring
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original Design | Simplified Design | Savings |
|-------|----------------|-------------------|---------|
| 2.1 Persona | Independent Agent only | Independent + Question Gen | +1 capability, same agent |
| 2.3 Questioner | Separate agent | Embedded in Independent | -1 agent, -33% LLM calls |
| 2.4 Tools | 4 tools + MCP abstraction | 2 CallableTool2 tools, SDK 原生 | -50% tools, 类型安全 |
| 2.5 Memory | 3-agent memory | 2-agent memory | Simpler lifecycle |
| 2.6 Coordination | State + Mailbox ready | State only | Deferred complexity |
| 2.7 Recovery | Full circuit breaker | Retry + backoff | Simpler MVP |

**Total Estimated Savings**: ~4-6 weeks development time

---

## References

### Research Sources
- Kimi K2.5 Technical Specifications (codecademy.com, 2026)
- LangGraph Documentation (langchain-ai.github.io, 2026)
- Model Context Protocol Specification v2025-06-18

### Related Analysis Documents
- [1_ARCHITECTURE_AND_DESIGN.md](1_ARCHITECTURE_AND_DESIGN.md) - Foundation decisions (v2.0)
- [4_TECHNOLOGY_STACK.md](4_TECHNOLOGY_STACK.md) - LLM provider details
- [7_QUALITY_AND_TESTING.md](7_QUALITY_AND_TESTING.md) - Evaluation implementation

---

**Document Status**: Version 3.0 - kimi-agent-sdk  
**Key Change**: KimiSessionManager 替代 llm_client; CallableTool2 替代 OpenAI Functions  
**Development Time Savings**: ~4-6 weeks compared to original design
