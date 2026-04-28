# BMAD Methodology Deep Research & DocuSwarm Alignment Report

**Version**: 1.0  
**Date**: 2026-02-19  
**Project**: DocuSwarm Multi-Agent Document Orchestration System  
**Scope**: BMAD Framework Analysis, `_bmad` / `_bmad-output` Deep Research, DocuSwarm Product Alignment  
**Status**: Complete

---

## 1. Executive Summary

### 1.1 Research Objective

This report provides a deep-dive analysis of the **BMAD (BMad Method)** framework infrastructure as installed in the ClawTeams workspace (`_bmad/` and `_bmad-output/`), evaluates its architectural patterns, agent design, workflow orchestration mechanisms, and memory systems, and synthesizes actionable recommendations for how **DocuSwarm** should leverage, extend, or diverge from BMAD to realize its product requirements as defined in `DOCUSWARM_RESEARCH_REPORT.md`.

### 1.2 Key Findings

| Dimension | Finding | DocuSwarm Impact |
|-----------|---------|------------------|
| **BMAD Agent Architecture** | Human-in-the-loop, persona-driven, menu-based interaction | DocuSwarm requires fully autonomous node execution |
| **BMAD Workflow Engine** | XML-based `workflow.xml` with YAML configs, step-file micro-architecture | Reusable pattern for DocuSwarm pipeline state machine |
| **BMAD Phase Pipeline** | 4-phase linear: Analysis → Planning → Solutioning → Implementation | DocuSwarm maps directly to phases 1-3 (front-half) |
| **BMAD Module System** | 5 modules: core, bmm, cis, bmb, tea (v6.0.1) | DocuSwarm should be a new BMAD module or VCPToolBox plugin |
| **BMAD Output Structure** | 4 artifact categories, empty `_bmad-output` | DocuSwarm pipeline-state.yaml fits naturally here |
| **BMAD Memory System** | Sidecar memory per agent, documentation standards | DocuSwarm needs shared subject context, not per-agent silos |

### 1.3 Strategic Recommendations

| Priority | Recommendation | Rationale |
|----------|---------------|-----------|
| **Critical** | Adopt BMAD's phase pipeline (Analysis → Plan → Solution) as DocuSwarm's node graph skeleton | Direct 1:1 mapping eliminates design ambiguity |
| **Critical** | Reuse BMAD's workflow.xml execution engine pattern for DocuSwarm's NodeExecutor | Proven step-sequential execution with state tracking |
| **High** | Transform BMAD agents from interactive to autonomous by wrapping personas as system prompts | Preserves domain expertise, eliminates human-in-the-loop dependency |
| **High** | Place DocuSwarm output in `_bmad-output/planning-artifacts/` | Consistent with BMAD ecosystem conventions |
| **Medium** | Build DocuSwarm as a BMAD module (via bmb module-builder pattern) | Native integration, leverages BMAD installer/manifest |
| **Medium** | Replace BMAD's per-agent memory with DocuSwarm's shared Subject Context | Required for context isolation architecture |

---

## 2. BMAD Framework Deep Analysis

### 2.1 Installation & Module Architecture

The BMAD installation (v6.0.1, installed 2026-02-18) contains **5 modules**:

```
_bmad/
├── core/      v6.0.1  (built-in)  — Master orchestrator, tasks, core workflows
├── bmm/       v6.0.1  (built-in)  — BMad Method: full SDLC pipeline
├── cis/       v0.1.6  (external)  — Creative Intelligence Suite
├── bmb/       v0.1.6  (external)  — BMAD Builder: meta-module for creating agents/workflows
└── tea/       v1.2.1  (external)  — Test Architecture Enterprise
```

**Key Observation**: BMAD is a **modular, extensible platform** with a manifest-driven architecture. Each module registers agents, workflows, and configs via YAML/CSV manifests. DocuSwarm could be implemented as a **6th module** following this pattern.

### 2.2 Agent Inventory & Persona Analysis

BMAD defines **21 agents** across 5 modules, each with XML-structured persona definitions:

| Module | Agent | Name | Role | DocuSwarm Mapping |
|--------|-------|------|------|-------------------|
| core | bmad-master | 🧙 BMad Master | Workflow Orchestrator | → **Orchestrator Agent** |
| bmm | analyst | 📊 Mary | Business Analyst | → **Analyst Node (Independent)** |
| bmm | pm | 📋 John | Product Manager | → **PM Node (Independent)** |
| bmm | ux-designer | 🎨 Sally | UX Designer | → **UX Node (Independent)** |
| bmm | architect | 🏗️ Winston | System Architect | → **Architect Node (Independent)** |
| bmm | sm | 🏃 Bob | Scrum Master | → **PO Node (Independent)** |
| bmm | dev | 💻 Amelia | Developer Agent | Not in DocuSwarm front-half |
| bmm | qa | 🧪 Quinn | QA Engineer | Not in DocuSwarm front-half |
| bmm | tech-writer | 📚 Paige | Technical Writer | Potential future node |
| bmm | quick-flow-solo-dev | 🚀 Barry | Quick Flow Specialist | Not applicable |
| cis | brainstorming-coach | 🧠 Carson | Brainstorming Facilitator | Potential Questioner enhancement |
| cis | creative-problem-solver | 🔬 Dr. Quinn | Problem Solver | Not applicable |
| cis | design-thinking-coach | 🎨 Maya | Design Thinking Expert | Potential UX Evaluator |
| cis | innovation-strategist | ⚡ Victor | Innovation Strategist | Not applicable |
| cis | presentation-master | 🎨 Caravaggio | Visual Communication | Not applicable |
| cis | storyteller | 📖 Sophia | Master Storyteller | Not applicable |
| bmb | agent-builder | 🤖 Bond | Agent Architect | For building DocuSwarm agents |
| bmb | module-builder | 🏗️ Morgan | Module Architect | For building DocuSwarm module |
| bmb | workflow-builder | 🔄 Wendy | Workflow Architect | For building DocuSwarm workflows |
| tea | tea | 🧪 Murat | Master Test Architect | Quality validation integration |

### 2.3 Agent Architecture Pattern

Every BMAD agent follows an identical XML structure:

```
Agent Definition (*.md):
├── Frontmatter (name, description)
├── XML Agent Tag
│   ├── activation (mandatory startup sequence)
│   │   ├── step 1: Load persona
│   │   ├── step 2: Load config.yaml (CRITICAL)
│   │   ├── step 3-N: Initialize session
│   │   └── menu-handlers (exec, workflow, data, action)
│   ├── rules (communication language, character persistence)
│   ├── persona
│   │   ├── role
│   │   ├── identity
│   │   ├── communication_style
│   │   └── principles
│   └── menu (user-facing command options)
```

**Critical Insight for DocuSwarm**: BMAD agents are designed for **interactive, human-in-the-loop** operation. They:
1. Wait for user menu selection before executing
2. Communicate in a specific personality style
3. Load resources at runtime, never pre-load
4. Follow deterministic step sequences within workflows

DocuSwarm needs to **transform this pattern** from interactive to autonomous while preserving the domain expertise encoded in each persona.

### 2.4 Workflow Engine Deep Dive

The core workflow execution engine (`_bmad/core/tasks/workflow.xml`) is a 235-line XML task definition that serves as the **BMAD operating system** for all workflow processing:

```
Workflow Execution Model:
├── Step 1: Load & Initialize
│   ├── 1a: Load workflow.yaml, resolve config variables
│   ├── 1b: Load instructions, templates, validation paths
│   └── 1c: Initialize output file from template
├── Step 2: Process Each Instruction Step
│   ├── 2a: Handle attributes (optional, if, for-each, repeat)
│   ├── 2b: Execute step content (action, check, ask, invoke-*)
│   ├── 2c: Handle template-output tags (save checkpoint)
│   └── 2d: Step completion (continue/edit confirmation)
└── Step 3: Completion (confirm saved, report done)

Execution Modes:
├── normal: Full user interaction at EVERY template-output
└── yolo: Skip confirmations, simulate expert user
```

**Supported Tags**: `action`, `check`, `ask`, `goto`, `invoke-workflow`, `invoke-task`, `invoke-protocol`

**Reusable Protocols**: `discover_inputs` — Smart file discovery with three strategies:
- `FULL_LOAD`: Load all files in sharded directory
- `SELECTIVE_LOAD`: Load specific shard via template variable
- `INDEX_GUIDED`: Load index.md, analyze relevance, load matching docs

**DocuSwarm Relevance**: The workflow engine's step-sequential model with state tracking, checkpoint saves, and invocation chaining is **directly applicable** to DocuSwarm's NodeExecutor. The key transformation needed:
- Replace `ask` (user input) with autonomous decision-making
- Replace `template-output` (user confirmation) with Evaluator Agent review
- Keep `invoke-workflow` for sub-pipeline execution
- Keep `discover_inputs` protocol for document loading

### 2.5 BMAD Phase Pipeline

BMAD's BMM module defines a **4-phase SDLC pipeline** that maps directly to DocuSwarm's intended pipeline:

```
Phase 1: Analysis          Phase 2: Planning         Phase 3: Solutioning       Phase 4: Implementation
├── Brainstorm Project     ├── Create PRD            ├── Create Architecture    ├── Sprint Planning
├── Market Research        ├── Validate PRD          ├── Create Epics+Stories   ├── Create Story
├── Domain Research        ├── Edit PRD              ├── Check Implementation   ├── Dev Story
├── Technical Research     ├── Create UX Design      │   Readiness              ├── QA Automation
└── Create Product Brief   │                         │                          ├── Code Review
                           │                         │                          └── Retrospective
```

**DocuSwarm Pipeline Mapping**:

| BMAD Phase | BMAD Agent | DocuSwarm Node | DocuSwarm Agent Pattern |
|------------|-----------|----------------|-------------------------|
| 1-Analysis | Mary (Analyst) | `analyst` node | Independent: Research + Brief → Evaluator: Alignment check → Questioner: Clarification |
| 2-Planning (PRD) | John (PM) | `pm` node | Independent: PRD creation → Evaluator: Completeness review → Questioner: Requirements gaps |
| 2-Planning (UX) | Sally (UX) | `ux` node | Independent: UX Design → Evaluator: Usability review → Questioner: User journey gaps |
| 3-Solutioning (Arch) | Winston (Architect) | `architect` node | Independent: Architecture doc → Evaluator: Technical review → Questioner: Decision gaps |
| 3-Solutioning (Epics) | John (PM) | `po` node | Independent: Epics+Stories → Evaluator: Coverage review → Questioner: Acceptance criteria gaps |

### 2.6 Workflow Step-File Architecture

BMAD workflows use a **micro-file architecture** where each workflow step is an isolated instruction file:

```
create-product-brief/
├── workflow.md                     # Entry point & rules
└── steps/
    ├── step-01-init.md             # Configuration, greeting, context loading
    ├── step-02-discovery.md        # User interview, requirements elicitation
    ├── step-03-analysis.md         # Market/domain analysis
    └── step-04-synthesis.md        # Document generation
```

**Core Principles**:
1. **Micro-file Design**: Each step is self-contained
2. **Just-In-Time Loading**: Only current step in memory
3. **Sequential Enforcement**: No skipping or optimization
4. **State Tracking**: Progress tracked in output frontmatter (`stepsCompleted` array)
5. **Append-Only Building**: Documents built incrementally

**DocuSwarm Relevance**: This pattern maps to DocuSwarm's node configuration YAML files. Each DocuSwarm node (analyst, pm, ux, architect, po) can be configured as a series of micro-steps that the Independent Agent executes sequentially.

---

## 3. `_bmad-output` Analysis

### 3.1 Current State

The `_bmad-output` directory is **empty** (freshly installed, no workflows have been executed):

```
_bmad-output/
├── bmb-creations/           # Empty — BMB module outputs
├── implementation-artifacts/ # Empty — Phase 4 outputs
├── planning-artifacts/       # Empty — Phases 1-3 outputs
└── test-artifacts/           # Empty — TEA module outputs
```

### 3.2 Intended Content Structure

Based on BMAD configuration analysis:

| Directory | Purpose | Populated By | DocuSwarm Relevance |
|-----------|---------|-------------|---------------------|
| `planning-artifacts/` | PRD, Architecture, Epics, UX Design, Product Brief | Phases 1-3 workflows | **Primary** — All DocuSwarm deliverables go here |
| `implementation-artifacts/` | Sprint status, story files, dev records | Phase 4 workflows | Secondary — DocuSwarm front-half doesn't reach Phase 4 |
| `test-artifacts/` | Test designs, reviews, traceability matrices | TEA workflows | Tertiary — For DocuSwarm quality validation |
| `bmb-creations/` | New agents, modules, workflows created via BMB | BMB builder workflows | Meta — For building DocuSwarm module itself |

### 3.3 DocuSwarm Output Recommendation

DocuSwarm should place its pipeline output in alignment with BMAD conventions:

```yaml
# Recommended DocuSwarm output structure
_bmad-output/
├── planning-artifacts/
│   ├── pipeline-state.yaml          # DocuSwarm single source of truth
│   ├── analyst-report.md            # Analyst node deliverable
│   ├── prd.md                       # PM node deliverable
│   ├── ux-design.md                 # UX node deliverable
│   ├── architecture.md              # Architect node deliverable
│   └── epics-and-stories.md         # PO node deliverable
└── docuswarm/                       # DocuSwarm-specific artifacts
    ├── context-snapshots/           # Context isolation snapshots
    ├── review-history/              # Evaluator Agent review records
    └── question-logs/               # Questioner Agent question history
```

---

## 4. BMAD-to-DocuSwarm Architecture Alignment

### 4.1 Pattern Mapping Matrix

| BMAD Concept | BMAD Implementation | DocuSwarm Equivalent | Transformation Required |
|-------------|--------------------|--------------------|------------------------|
| **Agent Persona** | XML persona block (role, identity, style, principles) | Independent Agent system prompt | Strip menu/activation, keep persona |
| **Workflow Engine** | `workflow.xml` (step processor) | NodeExecutor | Replace user interaction with autonomous execution |
| **Step Files** | Micro-file architecture | Node configuration YAML | Convert step instructions to agent directives |
| **Menu Handlers** | exec, workflow, data, action | Tool calling interface | Map to MCP/function calling |
| **Config System** | Per-module config.yaml | DocuSwarm pipeline config | Extend with pipeline-state.yaml |
| **Output Structure** | `_bmad-output/planning-artifacts/` | DocuSwarm deliverables | Direct reuse |
| **Discovery Protocol** | `discover_inputs` (FULL/SELECTIVE/INDEX_GUIDED) | Subject Context loader | Adapt for context isolation |
| **State Tracking** | Frontmatter `stepsCompleted` array | `pipeline-state.yaml` node status | Elevate to first-class state management |
| **YOLO Mode** | Skip confirmations, auto-proceed | Default DocuSwarm mode (autonomous) | DocuSwarm is "always YOLO" for automation |
| **Party Mode** | Multi-agent group discussion | Not applicable (different paradigm) | DocuSwarm uses structured triple-agent instead |

### 4.2 Gap Analysis

| DocuSwarm Requirement | BMAD Coverage | Gap | Recommendation |
|----------------------|---------------|-----|----------------|
| **Triple-Agent Pattern (I+E+Q)** | None — single agent per workflow | Full gap | Build custom NodeExecutor |
| **Context Isolation** | Partial — agents load specific files via `discover_inputs` | Significant gap | Build ContextManager with strict enforcement |
| **Questioner Unconditional** | None — no questioner concept | Full gap | Build QuestionerAgent as mandatory post-processor |
| **Evaluator Review** | Partial — `validate-prd`, `check-implementation-readiness` workflows exist | Partial gap | Extract validation patterns, generalize to EvaluatorAgent |
| **DAG Dependency Graph** | None — sequential pipeline | Full gap | Build DependencyGraph (Kahn's algorithm) |
| **Pipeline State YAML** | None — uses frontmatter tracking per document | Moderate gap | Build StateAgent with centralized YAML |
| **Response Compiler** | None — single response per agent | Full gap | Build ResponseCompiler (triple response contract) |
| **Autonomous Execution** | Partial — YOLO mode exists but still template-driven | Moderate gap | Build autonomous execution loop |
| **User Intent Recognition** | None — menu-based explicit selection | Full gap | Build OrchestratorAgent with intent parsing |

### 4.3 Reuse Assessment

```
BMAD → DocuSwarm Reuse Map:

REUSE DIRECTLY (25%)
├── Agent persona definitions (analyst, pm, ux, architect, po)
├── Workflow step-file micro-architecture pattern
├── Output directory structure (_bmad-output/planning-artifacts/)
├── Config.yaml variable resolution pattern
└── Discover_inputs protocol for document loading

ADAPT & EXTEND (35%)
├── workflow.xml engine → Autonomous NodeExecutor
├── YOLO mode → Default autonomous execution
├── validate-prd workflow → EvaluatorAgent pattern
├── check-implementation-readiness → Cross-node validation
├── Agent persona XML → System prompt extraction
└── Frontmatter state tracking → pipeline-state.yaml fields

BUILD NEW (40%)
├── Triple-agent NodeExecutor (I+E+Q encapsulation)
├── ContextManager (strict isolation enforcement)
├── QuestionerAgent (unconditional question generation)
├── ResponseCompiler (triple response contract)
├── DependencyGraph (DAG + Kahn's topological sort)
├── OrchestratorAgent (intent recognition + node routing)
├── StateAgent (pipeline-state.yaml CRUD)
└── Pipeline resume/checkpoint system
```

---

## 5. DocuSwarm Product Recommendations

### 5.1 Architecture Decision: Module vs Plugin

| Approach | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **BMAD Module** (via bmb) | Native BMAD integration, manifest-driven, installer support | Tied to BMAD ecosystem, may constrain architecture | For BMAD-centric deployments |
| **VCPToolBox Plugin** | Independent lifecycle, access to RAG/WebSocket/Plugin ecosystem | Separate from BMAD, requires bridge | For production deployments |
| **Hybrid** | Best of both — BMAD module for agent definitions, VCP plugin for runtime | More complex setup | **Recommended** |

**Recommendation**: Build DocuSwarm as a **BMAD module** for agent/workflow definitions and a **VCPToolBox plugin** for runtime execution. This preserves BMAD's rich agent personas and workflow patterns while gaining VCPToolBox's production infrastructure.

### 5.2 Agent Design Recommendations

#### 5.2.1 Extract BMAD Personas for DocuSwarm Independent Agents

Each BMAD agent's persona should be extracted and used as the system prompt for the corresponding DocuSwarm Independent Agent:

```yaml
# Example: Analyst Node Independent Agent
analyst_independent:
  system_prompt:
    role: "Strategic Business Analyst + Requirements Expert"
    identity: >
      Senior analyst with deep expertise in market research, 
      competitive analysis, and requirements elicitation. 
      Specializes in translating vague needs into actionable specs.
    principles:
      - "Channel expert business analysis frameworks: Porter's Five Forces, 
         SWOT analysis, root cause analysis"
      - "Articulate requirements with absolute precision"
      - "Ensure all stakeholder voices heard"
    communication_style: >
      Speaks with the excitement of a treasure hunter - thrilled by every clue, 
      energized when patterns emerge.
  
  # DocuSwarm additions
  context_access: [subject_context, independent_context]
  tools: [create_document, query_rag, update_pipeline_state]
  output_type: "analyst-report.md"
```

#### 5.2.2 Build Evaluator Agents from BMAD Validation Patterns

BMAD already has validation workflows that can inform Evaluator Agent design:

| BMAD Validation | Pattern | DocuSwarm Evaluator Adaptation |
|----------------|---------|-------------------------------|
| `validate-prd` | Check comprehensiveness, lean organization, cohesion | PM node Evaluator: alignment scoring against original intent |
| `check-implementation-readiness` | Adversarial review of PRD + Arch + Epics alignment | Cross-node Evaluator: verify inter-deliverable consistency |
| `code-review` | Adversarial senior developer review, find 3-10 issues | Template for Evaluator's issue-finding mandate |
| `editorial-review-prose` | Clinical copy-editor communication review | Document quality Evaluator component |
| `editorial-review-structure` | Structural reorganization, cut/simplify | Document structure Evaluator component |
| `review-adversarial-general` | Cynical review, produce findings | General-purpose Evaluator backbone |

**Recommendation**: Compose DocuSwarm Evaluators from multiple BMAD review patterns. For example, the PM node Evaluator should combine `validate-prd` logic + `review-adversarial-general` + `editorial-review-structure` patterns.

#### 5.2.3 Questioner Agent Design

BMAD has no direct Questioner concept, but several patterns inform its design:

1. **BMAD's `ask` tag** in workflow.xml — pauses for user input with structured options
2. **BMAD's `advanced-elicitation` workflow** — structured technique for deeper discovery
3. **BMAD's analyst persona** — "thrilled by every clue, energized when patterns emerge"

**Recommendation**: The Questioner Agent should combine:
- BMAD's elicitation techniques (from `advanced-elicitation` workflow)
- Structured question categorization (blocking/clarifying/optional from DocuSwarm spec)
- BMAD analyst's curiosity-driven persona as a base
- Unconditional execution regardless of node status (per DocuSwarm architecture mandate)

### 5.3 Pipeline Execution Recommendations

#### 5.3.1 Leverage BMAD's Phase Ordering

BMAD's BMM module enforces a specific phase sequence via `bmad-help.csv`:

```
Phase 1-Analysis:  seq 10-30  (Brainstorm → Research → Brief)
Phase 2-Planning:  seq 10-30  (Create PRD → Validate → UX)
Phase 3-Solutioning: seq 10-70  (Architecture → Epics → Readiness Check)
Phase 4-Implementation: seq 10-60 (Sprint Plan → Story → Dev → QA → Review → Retro)
```

DocuSwarm should **preserve this ordering** as its default pipeline while enabling DAG-based overrides for parallel-capable nodes:

```
Default Sequential: Analyst → PM → UX → Architect → PO
DAG Override:       Analyst → [PM ∥ UX] → Architect → PO
                    (PM and UX can execute in parallel after Analyst)
```

#### 5.3.2 Adopt BMAD's YOLO Mode as Default

BMAD's YOLO mode (`workflow.xml` execution mode) skips user confirmations and simulates expert user responses. DocuSwarm should operate in **permanent YOLO mode** with the Evaluator Agent replacing user confirmation:

| BMAD Normal Mode | DocuSwarm Autonomous Mode |
|-----------------|--------------------------|
| User confirms template-output | Evaluator Agent reviews deliverable |
| User selects [a]dvanced/[c]ontinue/[y]olo | OrchestratorAgent routes based on Evaluator verdict |
| User provides input at `ask` tags | Intent + Subject Context provides input |
| User decides to proceed or revise | Evaluator verdict (APPROVED/NEEDS_REVISION/BLOCKED) drives decision |

#### 5.3.3 State Management Enhancement

BMAD tracks state in document frontmatter (`stepsCompleted` array). DocuSwarm should elevate this to a centralized `pipeline-state.yaml`:

```yaml
# DocuSwarm pipeline-state.yaml (extending BMAD patterns)
version: "1.0"
pipeline_id: "ds-2026-02-19-001"
created_at: "2026-02-19T10:00:00Z"

# From BMAD config.yaml
project_name: "ClawTeams"
communication_language: "Chinese"
document_output_language: "English"

# DocuSwarm-specific
intent:
  original_request: "User's initial request"
  interpreted_goal: "System's understanding"

current_node: "pm"
execution_mode: "dependency_aware"

nodes:
  analyst:
    status: "completed"
    steps_completed: ["init", "discovery", "analysis", "synthesis"]  # From BMAD pattern
    deliverables:
      - path: "_bmad-output/planning-artifacts/analyst-report.md"
        checksum: "sha256:..."
    review_history:
      - iteration: 1
        verdict: "APPROVED"
        alignment_score: 0.92
    questions_generated: 5
    
  pm:
    status: "in_progress"
    steps_completed: ["init", "discovery"]
    dependencies_met: true
    current_iteration: 1

subject_context:
  project_name: "ClawTeams"
  key_requirements: []
  constraints: []
```

### 5.4 Context Isolation Recommendations

BMAD's `discover_inputs` protocol provides a foundation for context loading but lacks isolation:

| BMAD Behavior | DocuSwarm Required Behavior |
|--------------|---------------------------|
| Agent loads any file via `discover_inputs` | Subject Context: shared; Independent Context: private |
| No access control between agents | Evaluator sees deliverables but NOT Independent reasoning |
| Full file content loaded | Questioner sees role + subject + deliverables only |

**Recommendation**: Build a ContextManager that wraps BMAD's `discover_inputs` with access control layers:

```
ContextManager
├── SubjectContext (accessible by ALL agents)
│   ├── Loaded via discover_inputs FULL_LOAD strategy
│   ├── Contains: project knowledge, requirements, constraints
│   └── Source: _bmad-output/planning-artifacts/ + docs/
│
├── IndependentContext (accessible by Independent Agent ONLY)
│   ├── Contains: private reasoning, drafts, tool call history
│   ├── Source: in-memory during node execution
│   └── Discarded after deliverable finalization
│
├── EvaluatorContext (accessible by Evaluator Agent ONLY)
│   ├── Contains: SubjectContext + deliverables
│   ├── Excludes: Independent Agent's private reasoning
│   └── Built from: SubjectContext + completed deliverable
│
└── QuestionerContext (accessible by Questioner Agent ONLY)
    ├── Contains: role definition + SubjectContext + deliverables
    ├── Excludes: Independent Agent's private reasoning
    └── Built from: node role + SubjectContext + deliverable
```

### 5.5 Module Integration Strategy

#### 5.5.1 Building DocuSwarm as a BMAD Module

Using BMAD's `bmb` (Builder) module, DocuSwarm can be scaffolded as a proper BMAD module:

```
_bmad/docuswarm/                         # New BMAD module
├── config.yaml                          # Module configuration
├── module-help.csv                      # Help index
├── agents/
│   ├── orchestrator.md                  # OrchestratorAgent (extends bmad-master pattern)
│   ├── node-executor.md                 # NodeExecutor agent
│   └── response-compiler.md             # ResponseCompiler agent
├── workflows/
│   ├── pipeline-init/                   # Initialize DocuSwarm pipeline
│   │   ├── workflow.md
│   │   └── steps/
│   ├── node-execute/                    # Execute a pipeline node
│   │   ├── workflow.yaml
│   │   ├── instructions.md
│   │   └── node-configs/
│   │       ├── analyst.yaml
│   │       ├── pm.yaml
│   │       ├── ux.yaml
│   │       ├── architect.yaml
│   │       └── po.yaml
│   └── pipeline-review/                 # Cross-node validation
│       ├── workflow.yaml
│       └── instructions.md
└── data/
    ├── pipeline-state-template.yaml
    └── triple-response-schema.yaml
```

#### 5.5.2 Registering in BMAD Manifest

```csv
# Addition to _bmad/_config/agent-manifest.csv
"docuswarm-orchestrator","DocuSwarm","DocuSwarm Pipeline Orchestrator","🐝","pipeline orchestration, intent recognition, node routing","Orchestrator","...","...","...","docuswarm","_bmad/docuswarm/agents/orchestrator.md"
```

---

## 6. Risk Analysis & Mitigation

### 6.1 Architecture Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **BMAD persona extraction loses nuance** | Medium | Medium | Use full persona XML as system prompt, not summarized version |
| **Autonomous YOLO mode produces lower quality** | High | High | Evaluator Agent must enforce quality gates before proceeding |
| **Context isolation adds latency** | Medium | Low | Cache Subject Context across agents within same node |
| **BMAD module coupling limits DocuSwarm evolution** | Medium | Medium | Maintain abstraction layer; DocuSwarm runtime decoupled from BMAD definitions |
| **pipeline-state.yaml concurrent access** | Medium | High | Implement atomic YAML operations with file-level locking |

### 6.2 Integration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **BMAD version upgrade breaks DocuSwarm** | Low | High | Pin BMAD version, abstract away direct dependencies |
| **VCPToolBox plugin conflicts with BMAD agent system** | Medium | Medium | Use separate execution paths: BMAD for definitions, VCP for runtime |
| **_bmad-output directory structure changes** | Low | Low | Use config-driven paths, not hardcoded |

---

## 7. Implementation Roadmap

### 7.1 Phase 0: Foundation (1-2 weeks)

| Task | Description | BMAD Component Leveraged |
|------|-------------|-------------------------|
| 0.1 | Extract BMAD agent personas into DocuSwarm node configs | `bmm/agents/*.md` persona blocks |
| 0.2 | Create pipeline-state.yaml template | BMAD frontmatter pattern + DocuSwarm spec |
| 0.3 | Build ContextManager skeleton | BMAD `discover_inputs` protocol |
| 0.4 | Design DocuSwarm module structure | BMB module pattern |

### 7.2 Phase 1: Core Execution (2-3 weeks)

| Task | Description | BMAD Component Leveraged |
|------|-------------|-------------------------|
| 1.1 | Build NodeExecutor (triple-agent encapsulation) | BMAD `workflow.xml` step processor |
| 1.2 | Build StateAgent (pipeline-state.yaml CRUD) | BMAD frontmatter state tracking |
| 1.3 | Build ContextManager (isolation enforcement) | BMAD `discover_inputs` + access control |
| 1.4 | Build QuestionerAgent | BMAD `advanced-elicitation` + analyst persona |

### 7.3 Phase 2: Agent Layer (2-3 weeks)

| Task | Description | BMAD Component Leveraged |
|------|-------------|-------------------------|
| 2.1 | Build EvaluatorAgent | BMAD `validate-prd`, `review-adversarial-general` |
| 2.2 | Build ResponseCompiler | DocuSwarm triple response spec |
| 2.3 | Build OrchestratorAgent | BMAD `bmad-master` orchestration pattern |
| 2.4 | Configure 5 pipeline nodes | BMAD agent personas + workflow step patterns |

### 7.4 Phase 3: Integration (2 weeks)

| Task | Description | BMAD Component Leveraged |
|------|-------------|-------------------------|
| 3.1 | Build DependencyGraph (DAG) | New (informed by STORY_DEPENDENCY_ORCHESTRATION_SOLUTION) |
| 3.2 | End-to-end pipeline testing | BMAD `check-implementation-readiness` pattern |
| 3.3 | VCPToolBox plugin integration | VCPToolBox Plugin.js lifecycle |
| 3.4 | Register as BMAD module | BMB manifest pattern |

---

## 8. Conclusions

### 8.1 Key Takeaways

1. **BMAD provides ~60% of DocuSwarm's architectural foundation** — agent personas, workflow patterns, output structure, config systems, and validation workflows are directly reusable or adaptable.

2. **The critical gap is the triple-agent pattern** — BMAD's single-agent-per-workflow model must be transformed into DocuSwarm's Independent+Evaluator+Questioner encapsulation.

3. **BMAD's YOLO mode is a direct precursor to DocuSwarm's autonomous execution** — the concept of skipping human confirmation and simulating expert responses is exactly what DocuSwarm needs as its default behavior.

4. **BMAD's phase pipeline is the correct skeleton for DocuSwarm** — the Analysis → Planning → Solutioning flow maps 1:1 to DocuSwarm's Analyst → PM → UX → Architect → PO pipeline.

5. **DocuSwarm should be built as a BMAD module + VCPToolBox plugin hybrid** — leveraging BMAD for agent definitions and VCPToolBox for production runtime.

6. **Context isolation is the largest new capability to build** — BMAD has no concept of restricting what context an agent can access. DocuSwarm's strict isolation requirement (Independent vs Evaluator vs Questioner contexts) must be built from scratch.

### 8.2 Final Architecture Recommendation

```
DocuSwarm = BMAD Personas + BMAD Workflows + Custom Triple-Agent + VCPToolBox Runtime

┌──────────────────────────────────────────────────────────────────┐
│                    DocuSwarm Architecture                          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              BMAD Module Layer (Definitions)                 │ │
│  │  Agent Personas │ Node Configs │ Validation Patterns         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │            DocuSwarm Custom Layer (New Build)                │ │
│  │  NodeExecutor │ ContextManager │ ResponseCompiler            │ │
│  │  StateAgent   │ QuestionerAgent│ EvaluatorAgent              │ │
│  │  DependencyGraph │ OrchestratorAgent                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           VCPToolBox Runtime Layer (Infrastructure)          │ │
│  │  Plugin.js │ TagMemo RAG │ WebSocket │ AgentAssistant        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Output: _bmad-output/planning-artifacts/ + pipeline-state.yaml  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Appendix A: BMAD Agent Persona Extraction Reference

| Agent | Persona Extraction Key | Recommended DocuSwarm System Prompt Focus |
|-------|----------------------|------------------------------------------|
| Mary (Analyst) | Treasure hunter excitement, pattern recognition | Emphasize curiosity, evidence-based analysis, framework application |
| John (PM) | Detective "WHY?", data-sharp | Emphasize user-centric discovery, Jobs-to-be-Done, iteration |
| Sally (UX) | Empathetic storytelling, user advocacy | Emphasize user needs, simplicity, feedback-driven evolution |
| Winston (Architect) | Calm pragmatism, "boring technology" | Emphasize scalability trade-offs, developer productivity, business value |
| Bob (SM) | Crisp checklist-driven, zero ambiguity | Emphasize clear acceptance criteria, story completeness |

## Appendix B: BMAD Workflow Engine Tag Reference for DocuSwarm

| BMAD Tag | DocuSwarm Usage | Transformation |
|----------|----------------|----------------|
| `<action>` | Independent Agent task execution | Direct reuse |
| `<check if="...">` | Conditional node routing | Adapt for pipeline branching |
| `<ask>` | **Remove** — replace with autonomous decision | Evaluator verdict drives decisions |
| `<template-output>` | Deliverable checkpoint | Auto-save + Evaluator review trigger |
| `<invoke-workflow>` | Sub-pipeline execution | Reuse for nested node execution |
| `<invoke-task>` | Tool execution | Map to MCP tool calling |
| `<invoke-protocol>` | `discover_inputs` for context loading | Adapt with isolation enforcement |
| `<goto>` | Pipeline state machine transitions | Map to node routing in DAG |

## Appendix C: Cross-Reference with Existing Reports

| Report | Key Contribution to This Analysis |
|--------|----------------------------------|
| `DOCUSWARM_RESEARCH_REPORT.md` | Product requirements, technology stack, architecture design |
| `AGENT_ORCHESTRATION_RESEARCH_REPORT.md` | Multi-agent patterns, parallel execution, coordination mechanisms |
| `ORCHESTRATION_ENHANCEMENT_REVIEW.md` | Feasibility assessment, Phase 0 prerequisites, risk refinement |
| `STORY_DEPENDENCY_ORCHESTRATION_SOLUTION.md` | DAG design, Kahn's algorithm, layered parallel execution |
| `KIMI_K25_DOCUSWARM_INTEGRATION_REPORT.md` | LLM provider selection, API integration, mode mapping |

---

**Report Generated**: 2026-02-19  
**Version**: 1.0  
**Author**: Research Agent  
**Methodology**: Deep analysis of `_bmad/` directory (21 agents, 51 workflows, 5 modules), `_bmad-output/` structure, and 4 existing research reports, synthesized against DocuSwarm product requirements.
