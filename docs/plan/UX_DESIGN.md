# DocuSwarm UX Design Document

**Version**: 2.1  
**Date**: 2026-02-20  
**Status**: PO Approved  
**Author**: UX Designer  

---

## 1. Executive Summary

### 1.1 UX Vision

DocuSwarm provides a **streamlined, confidence-inspiring experience** for node-driven document generation. Users explicitly choose which BMAD node to execute, gaining precise control over each deliverable. The interface prioritizes:

- **Transparency**: Clear visibility into node run progress and agent decisions
- **Confidence**: Quality scores and evaluations build trust in outputs
- **Control**: User chooses which node to run, with automatic context chaining

### 1.2 Design Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| **Progressive Disclosure** | Show details on demand | Node overview → Run details → Iteration history |
| **Status Visibility** | Always show system state | Real-time progress, clear status indicators |
| **Error Prevention** | Guide users away from mistakes | Validation before node execution, clear warnings |
| **Recovery Support** | Easy recovery from interruptions | One-click resume, clear checkpoint information |

### 1.3 Target User Profiles

| Persona | Technical Level | Primary Goal | Key Concern |
|---------|----------------|--------------|-------------|
| **Dev Dave** | High | Fast document generation | Output quality and accuracy |
| **PM Paula** | Medium | Structured PRD creation | Completeness of requirements |
| **Lead Lisa** | High | Team workflow oversight | Quality control and approval |

---

## 2. Information Architecture

### 2.1 Core Navigation Structure

```
DocuSwarm
├── Node Overview
│   ├── Available Nodes (analyst/pm/ux/architect/po)
│   ├── Latest Run Status per Node
│   └── Quick Start (select node)
│
├── Node Run View
│   ├── Run History
│   ├── Run Details
│   │   ├── Deliverable
│   │   ├── Questions
│   │   └── Evaluation
│   └── Actions
│       ├── Re-run Node
│       └── Export
│
├── Deliverables
│   ├── Analyst Report
│   ├── PRD
│   ├── UX Design
│   ├── Architecture
│   └── Epics/Stories
│
└── Settings
    ├── Node Configuration
    ├── Quality Thresholds
    └── Export Preferences
```

### 2.2 State Model

```
Node Run States:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  PENDING ──▶ RUNNING ──▶ COMPLETED                           │
│              │    │                                          │
│              │    └──▶ NEEDS_REVISION ──▶ ITERATING          │
│              │              │                │                │
│              │              └────────────────┘                │
│              │                                                │
│              └──▶ FAILED                                     │
│              │                                                │
│              └──▶ BLOCKED ──▶ MANUAL_REVIEW                │
└─────────────────────────────────────────────────────────────┘

Note: Each "docuswarm start <node>" creates a NEW run instance.
Runs are immutable; re-execution creates a new run_id.
```

---

## 3. User Flows

### 3.1 Primary Flow: Execute a Node

```
┌─────────────────────────────────────────────────────────────┐
│                  EXECUTE A NODE                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  1. SELECT NODE AND PROVIDE CONTEXT                         │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  Available Nodes:                                   │ │
│     │  [analyst] [pm] [ux] [architect] [po]              │ │
│     │                                                     │ │
│     │  Selected: [analyst ▼]                             │ │
│     │  Context File: [my-project.yaml ________]          │ │
│     │                                                     │ │
│     │  Options:                                           │ │
│     │  [x] Auto-chain predecessor deliverables           │ │
│     │  [ ] No chain (use context file only)              │ │
│     │                                                     │ │
│     │         [Validate Context]  [Start Node]           │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. CONTEXT VALIDATION (Automatic)                          │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  ✓ Context file provided and readable              │ │
│     │  ✓ Context has sufficient detail (>100 chars)      │ │
│     │  ✓ Node configuration found (nodes/analyst/)       │ │
│     │  ⚠ No predecessor run found (first node)          │ │
│     │                                                     │ │
│     │  Context Score: 85% - Ready to proceed             │ │
│     │                                                     │ │
│     │         [Edit Context]  [Confirm & Start]          │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. NODE EXECUTION VIEW                                     │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  Node: analyst                                     │ │
│     │  Run ID: a3f7b2c1                                  │ │
│     │  Status: RUNNING                                   │ │
│     │                                                     │ │
│     │  Chained Context: (none - first node)              │ │
│     │                                                     │ │
│     │  Current: Iteration 1/3                            │ │
│     │  ├── Independent Agent: Creating deliverable...    │ │
│     │  └── Time elapsed: 00:45                           │ │
│     │                                                     │ │
│     │         [Cancel]                                   │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. NODE COMPLETION NOTIFICATION                            │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  ✓ Analyst Node Complete                           │ │
│     │                                                     │ │
│     │  Run ID: a3f7b2c1                                  │ │
│     │  Verdict: APPROVED                                 │ │
│     │  Score: 0.85                                       │ │
│     │  Iterations: 1                                     │ │
│     │                                                     │ │
│     │  Questions Generated:                              │ │
│     │  🔴 1 Blocking  🟡 2 Clarifying  🟢 1 Optional    │ │
│     │                                                     │ │
│     │  [View Deliverable]  [Answer Questions]            │ │
│     │  [Export]                                          │ │
│     │                                                     │ │
│     │  Suggested next: docuswarm start pm --context ...  │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Secondary Flow: View Node Run History

```
┌─────────────────────────────────────────────────────────────┐
│                  NODE RUN HISTORY                            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  1. SELECT NODE TO INSPECT                                  │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  Node Run History:                                 │ │
│     │                                                     │ │
│     │  ┌────────────────────────────────────────────────┐│ │
│     │  │ analyst                                       ││ │
│     │  │ Latest Run: a3f7b2c1                          ││ │
│     │  │ Status: COMPLETED  Score: 0.85                ││ │
│     │  │ Iterations: 1  Created: 2 hours ago           ││ │
│     │  │                                                ││ │
│     │  │       [View Details]  [Re-run]  [Export]      ││ │
│     │  └────────────────────────────────────────────────┘│ │
│     │                                                     │ │
│     │  ┌────────────────────────────────────────────────┐│ │
│     │  │ analyst (previous run)                        ││ │
│     │  │ Run: 9e2d4f6a  Status: FAILED  Score: 0.42   ││ │
│     │  │ ...                                            ││ │
│     │  └────────────────────────────────────────────────┘│ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. RUN DETAIL VIEW                                         │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  Node: analyst  Run: a3f7b2c1                      │ │
│     │                                                     │ │
│     │  Run Information:                                  │ │
│     │  ├── Status: COMPLETED ✓                          │ │
│     │  ├── Score: 0.85                                   │ │
│     │  ├── Iterations: 1                                 │ │
│     │  ├── Context: my-project.yaml                     │ │
│     │  └── Chained: (none - first node)                 │ │
│     │                                                     │ │
│     │  Tabs: [Deliverable] [Questions] [Evaluation]     │ │
│     │                                                     │ │
│     │         [Export]  [Re-run Node]                    │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Secondary Flow: Answer Clarifying Questions

```
┌─────────────────────────────────────────────────────────────┐
│                  ANSWER QUESTIONS                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  QUESTIONS PANEL                                            │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  Node: Analyst                                     │ │
│     │  Questions: 4 total (1 blocking)                   │ │
│     │                                                     │ │
│     │  🔴 BLOCKING (must answer before continue)         │ │
│     │  ┌────────────────────────────────────────────────┐│ │
│     │  │ Q1: What is the expected user volume for       ││ │
│     │  │     the initial launch?                        ││ │
│     │  │                                                ││ │
│     │  │ Context: This affects architecture decisions   ││ │
│     │  │ for database and caching strategy.             ││ │
│     │  │                                                ││ │
│     │  │ Answer: [____________________________]         ││ │
│     │  │                                                ││ │
│     │  │ [ ] Skip (will mark as "Not Specified")       ││ │
│     │  └────────────────────────────────────────────────┘│ │
│     │                                                     │ │
│     │  🟡 CLARIFYING (recommended)                       │ │
│     │  ┌────────────────────────────────────────────────┐│ │
│     │  │ Q2: Should the system support offline mode?    ││ │
│     │  │     Answer: [____________________________]     ││ │
│     │  └────────────────────────────────────────────────┘│ │
│     │  ┌────────────────────────────────────────────────┐│ │
│     │  │ Q3: What authentication method is preferred?   ││ │
│     │  │     Answer: [OAuth 2.0 ▼]                      ││ │
│     │  └────────────────────────────────────────────────┘│ │
│     │                                                     │ │
│     │  🟢 OPTIONAL (can skip)                            │ │
│     │  ┌────────────────────────────────────────────────┐│ │
│     │  │ Q4: Any branding guidelines to follow?         ││ │
│     │  │     Answer: [____________________________]     ││ │
│     │  └────────────────────────────────────────────────┘│ │
│     │                                                     │ │
│     │  Answered: 2/4 (blocking answered: 0/1)            │ │
│     │                                                     │ │
│     │         [Save & Continue Later]  [Submit All]      │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Interface Components

### 4.1 Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  DocuSwarm Dashboard                          [?] [⚙]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Quick Start                                                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  [+]             │  │  [↻]             │                │
│  │  Run Node        │  │  View Runs       │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Node Overview                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Node        Latest Run   Status      Score          │   │
│  │ ───────────────────────────────────────────────────  │   │
│  │ analyst     a3f7b2c1     completed   0.85           │   │
│  │ pm          b4e8c3d2     completed   0.78           │   │
│  │ ux          (none)       -           -              │   │
│  │ architect   (none)       -           -              │   │
│  │ po          (none)       -           -              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Recent Completions (5)                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ analyst  a3f7b2c1  ✓  Score: 0.85   2 hours ago    │   │
│  │ pm       b4e8c3d2  ✓  Score: 0.78   1 hour ago     │   │
│  │ analyst  9e2d4f6a  ✕  Score: 0.42   1 day ago      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Statistics (Last 30 Days)                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │    18    │  │   87%    │  │  0.84    │  │  $4.56   │   │
│  │ Node Runs│  │ Success  │  │ Avg Score│  │ Total Cost│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Node Execution View

```
┌─────────────────────────────────────────────────────────────┐
│  Node: analyst  Run: a3f7b2c1                    [✕]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Status: RUNNING                                            │
│                                                             │
│  Context: my-project.yaml                                   │
│  Chained: (none - first node)                               │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Current Iteration: 2/3                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ Iteration 1                                 │    │   │
│  │  │ ├── Score: 0.62                             │    │   │
│  │  │ ├── Verdict: NEEDS_REVISION                 │    │   │
│  │  │ └── Issues: Missing market analysis section │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ Iteration 2 (Current)                       │    │   │
│  │  │ ├── Independent Agent: Revising...         │    │   │
│  │  │ └── Time elapsed: 01:23                    │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  Estimated remaining: ~45 seconds                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Node Detail View

```
┌─────────────────────────────────────────────────────────────┐
│  Node: PM - Product Requirements                 [←] [↓]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Tabs: [Deliverable] [Questions] [Evaluation]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
│  DELIVERABLE                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  # Product Requirements Document                     │   │
│  │                                                      │   │
│  │  ## 1. Executive Summary                            │   │
│  │                                                      │   │
│  │  This document outlines the product requirements    │   │
│  │  for the my-project system, a web application       │   │
│  │  designed to...                                     │   │
│  │                                                      │   │
│  │  ## 2. User Stories                                 │   │
│  │                                                      │   │
│  │  ### US-001: User Registration                      │   │
│  │  As a new user, I want to register an account       │   │
│  │  so that I can access the system.                   │   │
│  │                                                      │   │
│  │  **Acceptance Criteria:**                           │   │
│  │  - User can provide email and password              │   │
│  │  - Email verification required                      │   │
│  │  - ...                                              │   │
│  │                                                      │   │
│  │  [... scrollable ...]                               │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Actions: [Copy to Clipboard] [Export as MD] [Edit]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Evaluation Summary Component

```
┌─────────────────────────────────────────────────────────────┐
│  Evaluation Summary                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Verdict: ✓ APPROVED                                        │
│  Alignment Score: 0.78 / 1.00                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Criterion Scores                                    │   │
│  │                                                      │   │
│  │ Completeness  ████████████████████░░░░  0.80        │   │
│  │ Clarity       ███████████████████░░░░░  0.75        │   │
│  │ Consistency   █████████████████░░░░░░░  0.70        │   │
│  │ Actionability ████████████████████████  0.90        │   │
│  │ Evidence      ███████████████░░░░░░░░░  0.65        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Issues Found (2):                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ⚠ Minor: Section 3.2 lacks specific metrics        │   │
│  │ ⚠ Minor: User story US-005 missing acceptance      │   │
│  │         criteria                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Suggestions:                                               │
│  • Add quantifiable success metrics to Section 3.2         │
│  • Complete acceptance criteria for all user stories       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Visual Design System

### 5.1 Color Palette

| Purpose | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| **Primary** | Deep Blue | #2563EB | Actions, links, active states |
| **Success** | Green | #10B981 | Approved, completed, positive |
| **Warning** | Amber | #F59E0B | Needs revision, caution |
| **Error** | Red | #EF4444 | Blocked, failed, critical |
| **Neutral** | Gray | #6B7280 | Text, borders, inactive |
| **Background** | Light Gray | #F9FAFB | Page background |
| **Surface** | White | #FFFFFF | Card backgrounds |

### 5.2 Status Indicators

| Status | Icon | Color | Usage |
|--------|------|-------|-------|
| Pending | ○ | Gray | Node not yet started |
| Executing | ● (pulse) | Blue | Node currently running |
| Approved | ✓ | Green | Node passed evaluation |
| Needs Revision | ↻ | Amber | Iterating for improvement |
| Blocked | ✕ | Red | Node cannot proceed |
| Completed | ✓✓ | Green | All nodes completed (user-driven) |

### 5.3 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 (Page Title) | Inter | 24px | Bold (700) |
| H2 (Section) | Inter | 20px | Semibold (600) |
| H3 (Subsection) | Inter | 16px | Semibold (600) |
| Body | Inter | 14px | Regular (400) |
| Caption | Inter | 12px | Regular (400) |
| Code | JetBrains Mono | 13px | Regular (400) |

### 5.4 Spacing System

| Size | Pixels | Usage |
|------|--------|-------|
| xs | 4px | Inline spacing |
| sm | 8px | Component padding |
| md | 16px | Card padding |
| lg | 24px | Section spacing |
| xl | 32px | Page margins |
| 2xl | 48px | Major sections |

---

## 6. Interaction Patterns

### 6.1 Node Execution Progress

```
Node Execution Indicator:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Iteration Progress (within a single node run):            │
│                                                             │
│  Iteration 1 ──▶ Iteration 2 ──▶ Iteration 3 (max)       │
│  ↑                                                          │
│  Current iteration has animated border                      │
│  Completed iterations show score badge                      │
│  Future iterations are grayed out                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Progress Bar Behavior:
- Smooth animation between iteration updates
- Color gradient indicates health (green → amber if iterating)
- Hover shows detailed breakdown
```

### 6.2 Real-time Updates

```
WebSocket Events (Future):
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Node Status Updates:                                       │
│  • Slide-in notification when node completes               │
│  • Score badge animates into view                          │
│  • Questions badge pulses if blocking questions exist      │
│                                                             │
│  MVP (Polling):                                             │
│  • Poll every 5 seconds during execution                   │
│  • UI updates smoothly with transition animations          │
│  • Loading spinner during poll requests                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Error Handling Patterns

```
Error States:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  API Error:                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ⚠ Connection error. Retrying... (attempt 2/3)      │   │
│  │                                                      │   │
│  │ [Cancel] [Retry Now]                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Blocked Node:                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✕ Node blocked after 3 iterations                   │   │
│  │                                                      │   │
│  │ The Evaluator Agent could not approve this          │   │
│  │ deliverable. Manual review required.                │   │
│  │                                                      │   │
│  │ [View Issues] [Retry with Modified Context]         │   │
│  │               [Force Approve] [Cancel Node Run]     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. CLI Interface Design (MVP)

### 7.1 Command Structure

```bash
# Initialize project
docuswarm init

# List available nodes and their latest run status
docuswarm nodes

# Execute a specific node
docuswarm start <node> --context project-context.yaml [--no-chain]

# View node run history
docuswarm runs <node> [--limit N]

# View node run status
docuswarm status <node> [--run <run-id>] [--verbose]

# Export node deliverables
docuswarm export <node> [--run <run-id>] --output ./output/

# View node questions
docuswarm questions <node> [--run <run-id>]

# Answer a question
docuswarm answer <question-id> "answer text"
```

### 7.2 CLI Output Format

```
$ docuswarm start analyst --context my-project.yaml

DocuSwarm Node Execution
Node: analyst
Run ID: a3f7b2c1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Context: my-project.yaml
Chained: (none - first node)

Current: Iteration 1/3
├── Status: EXECUTING
├── Agent: Independent Agent (creating deliverable...)
└── Elapsed: 00:45

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Press Ctrl+C to cancel
```

```
$ docuswarm status analyst --verbose

Node: analyst
Latest Run: a3f7b2c1
Status: COMPLETED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Verdict: APPROVED
Alignment Score: 0.85
Iterations: 1
Created: 2026-02-20 10:30

Questions: 4 (1 blocking)

Next suggested: docuswarm start pm --context my-project.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 8. Accessibility Guidelines

### 8.1 WCAG 2.1 AA Compliance

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| **Color Contrast** | 4.5:1 minimum | All text meets contrast ratio |
| **Keyboard Navigation** | Full keyboard access | Tab order, focus indicators |
| **Screen Reader** | Meaningful labels | ARIA labels on all interactive elements |
| **Focus Indicators** | Visible focus | 2px solid outline on focus |

### 8.2 Status Communication

```
Status Indicators for Accessibility:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Visual + Text + Icon:                                      │
│  ✓ Approved (green checkmark + "Approved" text)            │
│  ↻ Iterating (amber cycle + "Needs Revision" text)         │
│  ✕ Blocked (red X + "Blocked" text)                        │
│                                                             │
│  ARIA Announcements:                                        │
│  - "Analyst node complete. Score: 0.85. Approved."         │
│  - "PM node iteration 2 of 3. Addressing feedback."        │
│  - "All 5 nodes completed. Average score: 0.82."          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Responsive Considerations

### 9.1 Breakpoints (Future Web UI)

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Single column, collapsed navigation |
| Tablet | 640-1024px | Two column, sidebar collapsible |
| Desktop | > 1024px | Full layout, fixed sidebar |

### 9.2 MVP Focus

For CLI-first MVP, responsive considerations are deferred. Future web UI will follow mobile-first responsive design principles.

---

## 10. Implementation Priorities

### 10.1 MVP (Phase 1)

| Priority | Component | Rationale |
|----------|-----------|-----------|
| P0 | CLI Node Commands | Core functionality |
| P0 | Progress Output | User feedback |
| P0 | Status Reporting | Node run monitoring |
| P1 | Question Answering | Context refinement |
| P1 | Export Functionality | Output retrieval |
| P2 | Verbose Mode | Debugging support |

### 10.2 Phase 2 (Web UI)

| Priority | Component | Rationale |
|----------|-----------|-----------|
| P0 | Dashboard | Central hub |
| P0 | Node Execution View | Real-time monitoring |
| P1 | Node Detail View | Deliverable access |
| P1 | Question Panel | Interactive Q&A |
| P2 | Settings Panel | Configuration |
| P2 | Export Modal | Bulk export |

---

## 11. Appendices

### Appendix A: CLI Command Reference

| Command | Description | Options |
|---------|-------------|--------|
| `init` | Initialize DocuSwarm project | - |
| `nodes` | List available nodes and latest run status | - |
| `start` | Execute a specific node | `<node>`, `--context`, `--no-chain` |
| `runs` | List node run history | `<node>`, `--limit` |
| `status` | Show node run status | `<node>`, `--run`, `--verbose`, `--json` |
| `questions` | View node questions | `<node>`, `--run` |
| `answer` | Answer a question | `<question-id>`, answer text |
| `export` | Export node deliverables | `<node>`, `--run`, `--output` |

### Appendix B: Keyboard Shortcuts (Future Web UI)

| Shortcut | Action |
|----------|--------|
| `N` | New node run |
| `R` | Resume selected |
| `E` | Export selected |
| `?` | Show help |
| `Esc` | Close modal |
| `Tab` | Navigate fields |

---

**Document End**

*Generated with DocuSwarm BMAD Workflow*
> **2026-03-13 Alignment Notice**: 与节点上下文注入相关的 UX 假设需要按照 `docs/research/2026-03-13-docuswarm-context-refactor-overview.md` 及其配套方案更新。尤其是“节点输出可信性”“文档来源透明性”“docs 引用受控性”这三项，不应再默认当前代码已经满足。
