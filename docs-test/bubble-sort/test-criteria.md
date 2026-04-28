# DocuSwarm Pipeline Evaluation Criteria — Bubble Sort Project

**Document Type**: Evaluator Reference  
**Version**: 1.0.0  
**Audience**: EvaluatorAgent for all pipeline nodes  
**Purpose**: Define what constitutes a high-quality deliverable for each pipeline stage

---

## Overview

This document provides the evaluation criteria that the EvaluatorAgent should apply when
reviewing Independent Agent deliverables at each pipeline node. Criteria are organized by
node and scored on alignment (0–100).

A deliverable scoring **< 60** should trigger a revision request.  
A deliverable scoring **>= 60** passes the quality gate and allows pipeline progression.

---

## Node 1: Analyst — Domain Analysis Report

### Objective
The Analyst deliverable should demonstrate thorough understanding of the Bubble Sort domain,
stakeholders, and business context. It should go beyond algorithmic description and identify
real-world use cases, competitive context, and strategic recommendations.

### Required Sections

| Section                  | Weight | Description                                                    |
|--------------------------|--------|----------------------------------------------------------------|
| Executive Summary        | 10%    | 3–5 sentences summarizing findings and recommendations         |
| Stakeholder Analysis     | 20%    | Identifies ≥ 3 distinct stakeholder groups with needs          |
| Domain Overview          | 15%    | Explains algorithm theory in non-technical business language   |
| Use Case Analysis        | 20%    | ≥ 3 concrete use cases with user stories                       |
| Competitive Landscape    | 15%    | Compares to other educational sorting tools or packages        |
| Risks & Constraints      | 10%    | Identifies ≥ 2 technical and ≥ 2 business risks               |
| Recommendations          | 10%    | Actionable next steps for the PM stage                         |

### Scoring Rubric

| Score Range | Meaning                                                              |
|-------------|----------------------------------------------------------------------|
| 85–100      | All sections present, stakeholder analysis is insightful, use cases are specific and grounded |
| 70–84       | Most sections present, minor gaps in stakeholder depth or use case specificity |
| 60–69       | Core sections present but shallow; lacks competitive context or concrete use cases |
| < 60        | Missing critical sections; analysis is superficial or algorithm-focused only |

### Red Flags (auto-fail conditions)
- Deliverable is only a restatement of the algorithm without business analysis
- No stakeholder identification
- Word count < 400

---

## Node 2: PM — Product Requirements Document (PRD)

### Objective
The PM deliverable should be a structured PRD that a development team can implement from.
It must translate the analyst's findings into concrete, testable requirements.

### Required Sections

| Section                  | Weight | Description                                                    |
|--------------------------|--------|----------------------------------------------------------------|
| Product Vision           | 10%    | One-sentence vision + 2–3 sentence elaboration                 |
| Problem Statement        | 10%    | Clear articulation of the problem being solved                 |
| Target Users             | 10%    | Personas or user segments with specific needs                  |
| Feature List             | 25%    | P0/P1/P2 prioritized features with acceptance criteria         |
| Non-Functional Requirements | 10% | Performance, quality, compatibility NFRs                      |
| Release Scope            | 15%    | What's in v1.0 vs. future releases                             |
| Success Metrics          | 10%    | Measurable KPIs for product success                            |
| Out of Scope             | 10%    | Explicit exclusions to prevent scope creep                     |

### Scoring Rubric

| Score Range | Meaning                                                              |
|-------------|----------------------------------------------------------------------|
| 85–100      | Comprehensive PRD, all features have clear acceptance criteria, NFRs are specific |
| 70–84       | Good PRD with minor gaps; some features lack acceptance criteria     |
| 60–69       | PRD present but acceptance criteria are vague; NFRs missing          |
| < 60        | Missing feature list or acceptance criteria; cannot be implemented   |

### Red Flags (auto-fail conditions)
- Features listed without acceptance criteria
- No P0/P1/P2 prioritization
- Missing non-functional requirements

---

## Node 3: UX — Interface Design Specification

### Objective
The UX deliverable should define the user experience for both the CLI tool and Python API.
It should follow established UX conventions and provide concrete interface specifications.

### Required Sections

| Section                  | Weight | Description                                                    |
|--------------------------|--------|----------------------------------------------------------------|
| Design Principles        | 10%    | 3–5 guiding UX principles for the project                     |
| CLI Design               | 30%    | Command syntax, flags, examples, help text format              |
| Python API Design        | 30%    | Function signatures, return types, error handling conventions  |
| Error Message Design     | 15%    | Error message templates for common failure modes               |
| Visualization Design     | 15%    | Step-by-step output format specification                       |

### Scoring Rubric

| Score Range | Meaning                                                              |
|-------------|----------------------------------------------------------------------|
| 85–100      | Both CLI and API fully designed with examples; error messages are clear and actionable |
| 70–84       | Good design with minor gaps; one interface may be less detailed       |
| 60–69       | Basic interface defined but lacks examples or error design            |
| < 60        | Missing CLI or API design; insufficient for implementation            |

### Red Flags (auto-fail conditions)
- No CLI command syntax defined
- No Python API function signatures
- Missing examples

---

## Node 4: Architect — Technical Architecture Document

### Objective
The Architect deliverable should provide a complete technical design that developers can
implement without ambiguity. It should define module structure, data models, and
integration points.

### Required Sections

| Section                  | Weight | Description                                                    |
|--------------------------|--------|----------------------------------------------------------------|
| Architecture Overview    | 10%    | High-level diagram or description of module structure          |
| Module Structure         | 20%    | Package layout with file names and responsibilities            |
| Data Models              | 15%    | `SortMetrics` and other data structures with field types       |
| Core Algorithm Design    | 20%    | How standard and optimized variants are implemented            |
| CLI Architecture         | 15%    | CLI framework choice, entry point setup, argument parsing      |
| Testing Architecture     | 10%    | Test file structure, coverage tooling setup                    |
| Build & Distribution     | 10%    | `pyproject.toml` config, package metadata, entry points        |

### Scoring Rubric

| Score Range | Meaning                                                              |
|-------------|----------------------------------------------------------------------|
| 85–100      | Complete architecture; module structure is clear; data models are typed; build config specified |
| 70–84       | Good architecture with minor gaps; one section may be underdeveloped |
| 60–69       | Basic structure present but data models or build config missing      |
| < 60        | Architecture too vague to implement from; missing critical sections  |

### Red Flags (auto-fail conditions)
- No module/package structure defined
- `SortMetrics` data model missing
- No testing architecture

---

## Node 5: PO — Epics and User Stories

### Objective
The PO deliverable should produce a prioritized product backlog ready for sprint planning.
Each story must be independently implementable and testable.

### Required Sections

| Section                  | Weight | Description                                                    |
|--------------------------|--------|----------------------------------------------------------------|
| Epic List                | 10%    | ≥ 3 epics covering setup, core algorithm, CLI, testing         |
| Story Count              | 15%    | ≥ 8 user stories total across all epics                        |
| Story Format             | 20%    | Each story: "As a [role], I want [feature], so that [benefit]" |
| Acceptance Criteria      | 25%    | Each story has ≥ 2 specific, testable acceptance criteria       |
| Story Sizing             | 15%    | Relative sizing (S/M/L or story points) applied                |
| Definition of Done       | 15%    | Clear DoD applicable to all stories                            |

### Scoring Rubric

| Score Range | Meaning                                                              |
|-------------|----------------------------------------------------------------------|
| 85–100      | All stories follow format; acceptance criteria are specific and testable; backlog is sprint-ready |
| 70–84       | Good backlog; most stories have AC but some are vague                |
| 60–69       | Stories present but acceptance criteria weak; sizing missing         |
| < 60        | Stories too vague or missing acceptance criteria; not sprint-ready   |

### Red Flags (auto-fail conditions)
- Fewer than 5 user stories
- Stories without acceptance criteria
- No epics to group stories

---

## Cross-Node Evaluation Principles

All EvaluatorAgent decisions should follow these general principles:

1. **Completeness over perfection**: A complete deliverable with minor issues scores higher
   than a brilliant but incomplete deliverable missing required sections.

2. **Actionability**: Deliverables must provide enough specificity for the next agent (or a
   human developer) to act on them without returning to ask clarifying questions.

3. **Coherence**: The deliverable should be internally consistent — sections should not
   contradict each other.

4. **Alignment with context**: The deliverable must address the specific Bubble Sort project
   context, not provide generic templates.

5. **Language quality**: Deliverables should be written in clear, professional English.
   Minor grammatical issues do not reduce the score significantly, but clarity does matter.

---

## Evaluation Response Format

The EvaluatorAgent must return a structured JSON verdict:

```json
{
  "verdict": "pass" | "revise",
  "alignment_score": 0-100,
  "issues_found": [
    "Missing stakeholder analysis section",
    "Use cases are too abstract — no concrete user scenarios"
  ],
  "suggestions": [
    "Add at least 3 concrete use cases with user stories",
    "Include competitive analysis comparing to other Python sorting packages"
  ],
  "strengths": [
    "Executive summary is clear and concise",
    "Risk analysis is thorough"
  ]
}
```

A score of **< 60** MUST use `"verdict": "revise"`.  
A score of **>= 60** SHOULD use `"verdict": "pass"` unless critical red flags are present.
