# Epic 2: Agent System

**Epic ID**: EPIC-02  
**Version**: 1.0  
**Date**: 2026-02-19  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2 Weeks (Week 3-4)

---

## 1. Epic Overview

### 1.1 Summary

Implement the dual-agent system that powers each DocuSwarm node. This includes the Independent Agent (creates deliverables and questions) and Evaluator Agent (reviews and scores deliverables), along with BMAD persona loading and LLM client integration.

### 1.2 Business Value

- **Quality First**: Dual-agent pattern ensures deliverable quality
- **BMAD Compliance**: Persona-based agents match methodology
- **Simplified Design**: Two-agent pattern (vs three) reduces complexity by 33%
- **Context Isolation**: Built-in separation between creator and reviewer

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Independent Agent | Creates valid deliverable with questions |
| Evaluator Agent | Returns scored evaluation with verdict |
| Persona Loading | All 5 BMAD personas load correctly |
| LLM Integration | Kimi K2.5 API calls succeed |

### 1.4 Dependencies

- **Requires**: Epic 1 (Core Infrastructure) completed
- **Blocks**: Epic 3 (Node Execution Orchestration)

---

## 2. Architecture Context

### 2.1 Dual-Agent Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dual-Agent System (Epic 2)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Subject Context                                                             │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      INDEPENDENT AGENT                               │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  • BMAD Persona (from persona.json)                           │  │   │
│  │  │  • Kimi K2.5 Agent Mode (temperature 0.7)                     │  │   │
│  │  │  • Tool calling (create_deliverable, update_context)          │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Output:                                                       │  │   │
│  │  │  ├── deliverable (markdown content)                           │  │   │
│  │  │  ├── questions (blocking, clarifying, optional)               │  │   │
│  │  │  └── private_reasoning (NOT shared with Evaluator)            │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         │  [Context Filter - removes private_reasoning]                     │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       EVALUATOR AGENT                                │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  • Evaluation Criteria (from evaluator.yaml)                  │  │   │
│  │  │  • Kimi K2.5 Thinking Mode (temperature 0.5)                  │  │   │
│  │  │  • Restricted context (no private_reasoning)                  │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Output:                                                       │  │   │
│  │  │  ├── criterion_scores (0.0-1.0 per criterion)                 │  │   │
│  │  │  ├── alignment_score (weighted average)                       │  │   │
│  │  │  ├── verdict (APPROVED | NEEDS_REVISION | BLOCKED)           │  │   │
│  │  │  └── feedback (issues, suggestions)                           │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `docuswarm/agents/base.py` | BaseAgent abstract class |
| `docuswarm/agents/independent.py` | Independent Agent implementation |
| `docuswarm/agents/evaluator.py` | Evaluator Agent implementation |
| `docuswarm/agents/persona.py` | BMAD persona loader |
| `docuswarm/llm/client.py` | LLM client wrapper |
| `docuswarm/llm/tools.py` | Tool definitions |
| `docuswarm/llm/response.py` | Response parsing |
| `nodes/*/persona.json` | BMAD persona configurations |
| `nodes/*/evaluator.yaml` | Evaluation criteria |

---

## 3. User Stories

### Story 2.1: Base Agent Abstract Class

**ID**: US-2.1  
**As a** developer  
**I want to** have a base agent class with common functionality  
**So that** all agents share consistent behavior

**Acceptance Criteria**:
- [ ] Abstract `execute()` method defined
- [ ] Common initialization (config, logger)
- [ ] LLM client injection
- [ ] Type hints throughout

**Technical Tasks**:
1. Create `agents/base.py`
2. Define abstract `BaseAgent` class
3. Add common initialization logic
4. Add type annotations

**Implementation**:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict
import structlog

class BaseAgent(ABC):
    """Abstract base class for all DocuSwarm agents."""
    
    def __init__(self, config: AgentConfig, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
        self.logger = structlog.get_logger().bind(agent=self.__class__.__name__)
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic and return results."""
        pass
    
    def _format_system_prompt(self) -> str:
        """Format system prompt with persona and instructions."""
        raise NotImplementedError
```

**Definition of Done**:
- Abstract class importable
- Subclasses must implement `execute()`
- Type checking passes

---

### Story 2.2: LLM Client Implementation

**ID**: US-2.2  
**As a** developer  
**I want to** have a unified LLM client for Kimi K2.5  
**So that** all agents use consistent API interaction

**Acceptance Criteria**:
- [ ] Support three modes: Instant, Thinking, Agent
- [ ] Configure temperature per mode
- [ ] Handle tool calling
- [ ] Implement rate limiting (200 RPM)
- [ ] Implement retry with exponential backoff

**Technical Tasks**:
1. Create `llm/config.py` with model configurations
2. Create `llm/client.py` with unified client
3. Create `llm/rate_limit.py` with rate limiter
4. Create `llm/retry.py` with retry handler
5. Write unit tests with mocked API

**LLM Configuration**:
```python
class LLMConfig:
    API_BASE = "https://api.moonshot.cn/v1"
    
    MODELS = {
        "orchestrator": {
            "name": "kimi-k2.5-instant",
            "temperature": 0.3,
            "max_tokens": 4096
        },
        "independent": {
            "name": "kimi-k2.5-agent",
            "temperature": 0.7,
            "max_tokens": 32768
        },
        "evaluator": {
            "name": "kimi-k2.5-thinking",
            "temperature": 0.5,
            "max_tokens": 8000
        }
    }
```

**Definition of Done**:
- API calls succeed with valid API key
- Rate limiting prevents 429 errors
- Retry recovers from transient failures
- All three modes tested

---

### Story 2.3: Tool Definitions

**ID**: US-2.3  
**As a** developer  
**I want to** define tools for Independent Agent  
**So that** it can create deliverables and update context

**Acceptance Criteria**:
- [ ] `create_deliverable` tool defined
- [ ] `update_context` tool defined
- [ ] OpenAI Functions format
- [ ] Tool execution implemented

**Technical Tasks**:
1. Create `llm/tools.py` with tool definitions
2. Implement `ToolExecutor` class
3. Write tool execution tests

**Tool Definitions**:
```python
DOCUSWARM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_deliverable",
            "description": "Create the node's deliverable document",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_context",
            "description": "Update shared subject context",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "object"},
                    "operation": {
                        "type": "string",
                        "enum": ["set", "append", "remove"]
                    }
                },
                "required": ["key", "value"]
            }
        }
    }
]
```

**Definition of Done**:
- Tools in OpenAI Functions format
- Tool execution returns expected results
- Error handling for invalid arguments

---

### Story 2.4: Response Parsing

**ID**: US-2.4  
**As a** developer  
**I want to** parse and validate LLM responses  
**So that** agent outputs are structured correctly

**Acceptance Criteria**:
- [ ] JSON extraction from responses
- [ ] Validation of Independent Agent output
- [ ] Validation of Evaluator Agent output
- [ ] Error handling for malformed responses

**Technical Tasks**:
1. Create `llm/response.py`
2. Implement JSON extraction (direct and from code blocks)
3. Implement response validators
4. Write tests for various response formats

**Response Schemas**:
```python
# Independent Agent Output
class IndependentOutput(TypedDict):
    deliverable: Dict[str, Any]  # title, content, metadata
    questions: List[Dict[str, Any]]  # priority, question, context
    private_reasoning: Optional[str]

# Evaluator Agent Output
class EvaluatorOutput(TypedDict):
    criterion_scores: Dict[str, float]
    alignment_score: float  # 0.0 - 1.0
    verdict: Literal["APPROVED", "NEEDS_REVISION", "BLOCKED"]
    issues_found: List[str]
    suggestions: List[str]
```

**Definition of Done**:
- JSON extracted from various formats
- Invalid responses trigger clear errors
- Validated outputs match schemas

---

### Story 2.5: BMAD Persona Loader

**ID**: US-2.5  
**As a** developer  
**I want to** load BMAD personas from configuration  
**So that** each node uses the correct role and expertise

**Acceptance Criteria**:
- [ ] Load persona from `nodes/{node}/persona.json`
- [ ] Persona includes role, identity, expertise, principles
- [ ] Format persona into system prompt
- [ ] Support all 5 BMAD personas

**Technical Tasks**:
1. Create `agents/persona.py`
2. Implement persona loading
3. Implement prompt formatting
4. Create all 5 persona files

**Persona Schema**:
```json
{
  "name": "BMAD Analyst",
  "role": "Business Analyst",
  "identity": "I am Mary, an expert business analyst...",
  "expertise": [
    "Market research",
    "Requirements analysis",
    "Stakeholder interviews"
  ],
  "principles": [
    "Evidence-based recommendations",
    "User-centric analysis"
  ],
  "communication_style": "Professional, analytical",
  "output_format": "Structured markdown"
}
```

**BMAD Personas**:
| Node | Persona Name | File |
|------|--------------|------|
| Analyst | Mary (Business Analyst) | `nodes/analyst/persona.json` |
| PM | John (Product Manager) | `nodes/pm/persona.json` |
| UX | Alex (UX Designer) | `nodes/ux/persona.json` |
| Architect | Sam (Solution Architect) | `nodes/architect/persona.json` |
| PO | Jordan (Product Owner) | `nodes/po/persona.json` |

**Definition of Done**:
- All 5 personas load without error
- System prompts include full persona
- Prompts are within token limits

---

### Story 2.6: Independent Agent Implementation

**ID**: US-2.6  
**As a** developer  
**I want to** implement the Independent Agent  
**So that** it can create deliverables and generate questions

**Acceptance Criteria**:
- [ ] Load BMAD persona into system prompt
- [ ] Call LLM with Agent mode
- [ ] Support tool calling for deliverable creation
- [ ] Generate questions (blocking, clarifying, optional)
- [ ] Preserve private reasoning

**Technical Tasks**:
1. Create `agents/independent.py`
2. Implement `execute()` method
3. Format system prompt with persona
4. Handle tool calls
5. Parse and validate output
6. Write comprehensive tests

**Implementation**:
```python
class IndependentAgent(BaseAgent):
    """Creates deliverables and generates questions."""
    
    def __init__(self, node_id: str, config: AgentConfig, llm_client: LLMClient):
        super().__init__(config, llm_client)
        self.node_id = node_id
        self.persona = PersonaLoader.load(node_id)
    
    async def execute(self, context: Dict[str, Any]) -> IndependentOutput:
        """Execute deliverable creation."""
        system_prompt = self._format_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(context)}
        ]
        
        response = await self.llm.chat(
            agent_type="independent",
            messages=messages,
            tools=DOCUSWARM_TOOLS
        )
        
        return self._parse_response(response)
```

**Output Format**:
```json
{
  "deliverable": {
    "title": "Analyst Report: Project X",
    "content": "## Executive Summary\n...",
    "metadata": {"version": "1.0", "status": "draft"}
  },
  "questions": [
    {
      "priority": "blocking",
      "question": "What is the target market size?",
      "context": "Required for market analysis section"
    }
  ],
  "private_reasoning": "I chose this approach because..."
}
```

**Definition of Done**:
- Agent creates valid deliverable
- Questions generated with priorities
- Private reasoning preserved
- Tool calls executed correctly

---

### Story 2.7: Evaluator Agent Implementation

**ID**: US-2.7  
**As a** developer  
**I want to** implement the Evaluator Agent  
**So that** it can review and score deliverables

**Acceptance Criteria**:
- [ ] Load evaluation criteria from config
- [ ] Call LLM with Thinking mode
- [ ] Score against criteria (0.0-1.0)
- [ ] Calculate weighted alignment score
- [ ] Return verdict (APPROVED/NEEDS_REVISION/BLOCKED)
- [ ] NO access to private reasoning

**Technical Tasks**:
1. Create `agents/evaluator.py`
2. Implement criteria loading
3. Implement `execute()` method
4. Format evaluation prompt
5. Parse and validate scores
6. Write comprehensive tests

**Evaluation Criteria**:
```yaml
# Universal criteria (all nodes)
universal_criteria:
  completeness:
    description: "All required sections present"
    weight: 0.30
  clarity:
    description: "Clear and unambiguous language"
    weight: 0.20
  consistency:
    description: "Internally consistent information"
    weight: 0.20
  actionability:
    description: "Provides actionable guidance"
    weight: 0.20
  evidence_quality:
    description: "Claims supported by evidence"
    weight: 0.10

# Per-node weight overrides
node_weights:
  analyst:
    evidence_quality: 0.40
    actionability: 0.30
  pm:
    completeness: 0.40
    clarity: 0.30
```

**Implementation**:
```python
class EvaluatorAgent(BaseAgent):
    """Reviews deliverables and provides evaluation."""
    
    async def execute(
        self, 
        subject_context: Dict[str, Any],
        deliverable: Dict[str, Any]
    ) -> EvaluatorOutput:
        """Evaluate deliverable against criteria."""
        # NOTE: NO private_reasoning in input
        
        system_prompt = self._format_evaluation_prompt()
        
        user_message = json.dumps({
            "subject_context": subject_context,
            "deliverable": deliverable,
            "criteria": self.criteria
        })
        
        response = await self.llm.chat(
            agent_type="evaluator",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        return self._parse_evaluation(response)
```

**Output Format**:
```json
{
  "criterion_scores": {
    "completeness": 0.85,
    "clarity": 0.90,
    "consistency": 0.80,
    "actionability": 0.75,
    "evidence_quality": 0.70
  },
  "alignment_score": 0.78,
  "verdict": "NEEDS_REVISION",
  "issues_found": [
    "Market size section lacks quantitative data",
    "Risk analysis incomplete"
  ],
  "suggestions": [
    "Add specific market size figures",
    "Include probability assessments for risks"
  ]
}
```

**Definition of Done**:
- Criteria loaded from configuration
- Scores calculated correctly
- Verdict matches thresholds
- Context isolation verified (no private_reasoning)

---

### Story 2.8: Evaluation Criteria Configuration

**ID**: US-2.8  
**As a** developer  
**I want to** configure evaluation criteria per node  
**So that** each deliverable type is evaluated appropriately

**Acceptance Criteria**:
- [ ] Universal criteria defined
- [ ] Node-specific weight overrides
- [ ] Criteria loaded from YAML
- [ ] Validation of criteria configuration

**Technical Tasks**:
1. Create criteria schema
2. Create `nodes/*/evaluator.yaml` files
3. Implement criteria loader
4. Write validation tests

**Node Criteria Files**:

**Analyst** (`nodes/analyst/evaluator.yaml`):
```yaml
node_id: analyst
criteria_weights:
  completeness: 0.30
  clarity: 0.20
  consistency: 0.20
  actionability: 0.30
  evidence_quality: 0.40

thresholds:
  approval: 0.70
  escalation: 0.50

specific_criteria:
  - market_data_quality
  - requirement_traceability
```

**PM** (`nodes/pm/evaluator.yaml`):
```yaml
node_id: pm
criteria_weights:
  completeness: 0.40
  clarity: 0.30
  consistency: 0.20
  actionability: 0.30
  evidence_quality: 0.20

thresholds:
  approval: 0.70
  escalation: 0.50
```

**Definition of Done**:
- All 5 node criteria files created
- Weights sum to appropriate values
- Criteria loader validates schema
- Tests verify weight application

---

### Story 2.9: Dual-Agent Node Coordinator

**ID**: US-2.9  
**As a** developer  
**I want to** coordinate Independent and Evaluator agents  
**So that** nodes execute the dual-agent pattern

**Acceptance Criteria**:
- [ ] Execute Independent Agent first
- [ ] Filter private reasoning before Evaluator
- [ ] Execute Evaluator Agent
- [ ] Return combined result
- [ ] Support iteration (if NEEDS_REVISION)

**Technical Tasks**:
1. Create `nodes/dual_agent.py`
2. Implement coordination logic
3. Implement context filtering
4. Wire up iteration support (basic)
5. Write integration tests

**Implementation**:
```python
class DualAgentNode:
    """Coordinates Independent and Evaluator agents."""
    
    def __init__(self, node_id: str, llm_client: LLMClient):
        self.node_id = node_id
        self.independent = IndependentAgent(node_id, ..., llm_client)
        self.evaluator = EvaluatorAgent(node_id, ..., llm_client)
    
    async def execute(
        self, 
        state: NodeRunState,
        iteration: int = 1,
        previous_feedback: str = None
    ) -> NodeResult:
        """Execute dual-agent pattern."""
        # 1. Build context for Independent
        context = self._build_independent_context(state, previous_feedback)
        
        # 2. Execute Independent Agent
        independent_output = await self.independent.execute(context)
        
        # 3. Filter context for Evaluator (remove private_reasoning)
        evaluator_context = self._filter_for_evaluator(
            state.subject_context,
            independent_output
        )
        
        # 4. Execute Evaluator Agent
        evaluation = await self.evaluator.execute(
            subject_context=evaluator_context["subject_context"],
            deliverable=evaluator_context["deliverable"]
        )
        
        return NodeResult(
            deliverable=independent_output["deliverable"],
            questions=independent_output["questions"],
            evaluation=evaluation,
            iteration=iteration
        )
```

**Definition of Done**:
- Both agents execute in sequence
- Private reasoning filtered
- Result includes all outputs
- Integration test passes

---

## 4. Technical Specifications

### 4.1 Kimi K2.5 Mode Mapping

| Agent | Kimi Mode | Temperature | Max Tokens | Use Case |
|-------|-----------|-------------|------------|----------|
| Orchestrator | Instant | 0.3 | 4,096 | Routing, classification |
| Independent | Agent | 0.7 | 32,768 | Creation, tool calling |
| Evaluator | Thinking | 0.5 | 8,000 | Analysis, scoring |

### 4.2 Rate Limiting

| Limit | Value |
|-------|-------|
| Concurrent Requests | 20 |
| Requests per Minute | 200 |
| Tokens per Minute | 5,000,000 |

### 4.3 Question Priorities

| Priority | Description | Behavior |
|----------|-------------|----------|
| **blocking** | Critical, blocks node run | Must be answered |
| **clarifying** | Important for quality | Recommended |
| **optional** | Nice to have | Can be skipped |

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test | Description |
|------|-------------|
| `test_persona_loading` | Verify all personas load |
| `test_llm_client_modes` | Verify mode configuration |
| `test_tool_execution` | Verify tool calls work |
| `test_response_parsing` | Verify JSON extraction |
| `test_context_filtering` | Verify private_reasoning removed |

### 5.2 Integration Tests

| Test | Description |
|------|-------------|
| `test_independent_agent_e2e` | Full Independent Agent execution |
| `test_evaluator_agent_e2e` | Full Evaluator Agent execution |
| `test_dual_agent_coordination` | Both agents in sequence |

### 5.3 Mock Strategy

```python
@pytest.fixture
def mock_llm_response():
    """Return mock LLM responses for testing."""
    return {
        "independent": {
            "deliverable": {"title": "Test", "content": "# Test"},
            "questions": [{"priority": "blocking", "question": "Q?"}],
            "private_reasoning": "Because..."
        },
        "evaluator": {
            "criterion_scores": {"completeness": 0.8},
            "alignment_score": 0.78,
            "verdict": "APPROVED"
        }
    }
```

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM response format varies | Medium | Medium | Robust parsing, retry on failure |
| Rate limit exceeded | Low | Medium | Token bucket, request queuing |
| Context isolation failure | Low | High | Unit tests, audit logging |
| Persona prompt too long | Low | Low | Token counting, truncation |

---

## 7. Definition of Done (Epic Level)

- [ ] All 9 stories completed and tested
- [ ] Independent Agent creates valid deliverables
- [ ] Evaluator Agent returns valid evaluations
- [ ] All 5 BMAD personas configured
- [ ] Context isolation verified (private_reasoning not in Evaluator input)
- [ ] LLM integration tested with real API
- [ ] Unit test coverage ≥80%
- [ ] Integration tests pass
- [ ] Type checking passes
- [ ] Documentation complete

---

## 8. References

| Document | Location |
|----------|----------|
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` |
| LLM Integration | `docs/architecture/05_LLM_INTEGRATION.md` |
| Context Isolation | `docs/architecture/06_CONTEXT_ISOLATION.md` |
| Coding Standards | `docs/architecture/coding-standards.md` |

---

**Epic End**
