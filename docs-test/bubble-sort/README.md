# Bubble Sort Test Fixture — DocuSwarm Pipeline Test

This folder contains a complete set of documents for testing the DocuSwarm pipeline using
the Bubble Sort algorithm as the subject domain.

---

## File Structure

```
docs/bubble-sort/
├── README.md                  ← This file
├── bubble-sort-context.md     ← PRIMARY: DocuSwarm context file (pipeline entry point)
├── algorithm-spec.md          ← Reference: Formal algorithm specification
├── requirements.md            ← Reference: Stakeholder requirements and acceptance criteria
└── test-criteria.md           ← Reference: Per-node evaluation rubrics for EvaluatorAgent
```

---

## How to Run the Pipeline

### Prerequisites

```bash
# Ensure your environment is activated and API key is set
venv\Scripts\activate           # Windows
source venv/bin/activate        # Linux/macOS
# ANTHROPIC_API_KEY should be set in .env file
```

### Start Pipeline

```bash
python -m autoBMAD.docuswarm start --context docs/bubble-sort/bubble-sort-context.md
```

The pipeline will:
1. Read `bubble-sort-context.md` as the subject context
2. Set `subject = "bubble-sort-context"` (file stem)
3. Pass the full content through all 5 pipeline nodes
4. Save deliverables to `output/<pipeline_id>/`

### Monitor Progress

```bash
# Check status
python -m autoBMAD.docuswarm status <pipeline_id>

# List all pipelines
python -m autoBMAD.docuswarm list

# Resume if paused (e.g. awaiting answers to questions)
python -m autoBMAD.docuswarm resume <pipeline_id>

# Answer a blocking question
python -m autoBMAD.docuswarm answer <pipeline_id> <question_id> "your answer"
```

### Export Results

```bash
python -m autoBMAD.docuswarm export <pipeline_id> --output docs/bubble-sort/output/
```

---

## Document Roles

### `bubble-sort-context.md` (Context File)

This is the **primary input** to DocuSwarm. It is read by `PipelineService.start()` and
becomes `subject_context["content"]`. All pipeline agents receive this as their
"original context."

The context file defines:
- Project overview and domain
- Functional + non-functional requirements summary
- Constraints and success criteria
- References to supporting documents (for human readers; agents receive full content)

### `algorithm-spec.md` (Reference Document)

Formal algorithm specification including pseudocode, Python reference implementation,
complexity tables, and public API contract. Intended to help the Architect agent produce
a technically accurate architecture document.

### `requirements.md` (Reference Document)

Detailed stakeholder analysis and requirements specification with:
- Stakeholder profiles and needs
- Functional requirements (FR-01 through FR-07)
- Non-functional requirements
- Acceptance test matrix

Intended to ground the Analyst and PM agents in concrete, traceable requirements.

### `test-criteria.md` (Reference Document)

Per-node evaluation rubrics for the EvaluatorAgent. Defines:
- Required sections per deliverable
- Scoring rubric (0–100 scale)
- Red flag conditions (auto-fail)
- Cross-node evaluation principles

This document is intended as a reference for humans reviewing EvaluatorAgent decisions.
It mirrors the implicit criteria the EvaluatorAgent should apply.

---

## Expected Pipeline Outputs

After a successful run, `output/<pipeline_id>/` should contain:

| File                  | Node      | Description                                      |
|-----------------------|-----------|--------------------------------------------------|
| `analyst-report.md`   | analyst   | Domain analysis, stakeholder map, use cases      |
| `prd.md`              | pm        | Product requirements document                    |
| `ux-design.md`        | ux        | CLI and Python API interface design               |
| `architecture.md`     | architect | Technical architecture and module structure       |
| `epics-stories.md`    | po        | Prioritized epic and user story backlog           |
| `_metadata.json`      | system    | Pipeline metadata, timestamps, deliverable index  |

---

## Test Validation Checklist

After the pipeline completes, verify the following:

- [ ] All 5 deliverable files exist in `output/<pipeline_id>/`
- [ ] `analyst-report.md` contains stakeholder analysis (not just algorithm description)
- [ ] `prd.md` contains prioritized feature list with acceptance criteria
- [ ] `ux-design.md` contains CLI command syntax and Python function signatures
- [ ] `architecture.md` contains module structure and `SortMetrics` data model
- [ ] `epics-stories.md` contains ≥ 8 user stories with acceptance criteria
- [ ] No pipeline node ended in error state (`status != "failed"`)
- [ ] EvaluatorAgent scores are ≥ 60 for all nodes

---

## Troubleshooting

### Pipeline paused with questions

Some agents may ask clarifying questions before proceeding:

```bash
python -m autoBMAD.docuswarm questions <pipeline_id>
python -m autoBMAD.docuswarm answer <pipeline_id> <question_id> "answer text"
```

### Pipeline failed

```bash
# Check status for error details
python -m autoBMAD.docuswarm status <pipeline_id>

# Resume from the failed node
python -m autoBMAD.docuswarm resume <pipeline_id>
```

### Common Issues

| Symptom                              | Likely Cause                          | Fix                              |
|--------------------------------------|---------------------------------------|----------------------------------|
| `FileNotFoundError`                  | Wrong path to context file            | Use absolute path or run from project root |
| `No create_deliverable tool called`  | API key issue or model configuration  | Check `ANTHROPIC_API_KEY` in `.env` |
| All nodes show `completed` but empty | LangGraph state not persisted         | See `docs-test/research/_debug-snapshot-bubble-sort-cli-arch.md` |
