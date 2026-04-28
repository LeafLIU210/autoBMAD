> **⚠️ 已更新**: 本 Epic 已更新为使用 claude-agent-sdk + Kimi Code API 方案。详见 [EPIC-16-SDK-WRAPPER.md](EPIC-16-SDK-WRAPPER.md)。

# Epic 11: Node Executor Integration Fix (方案C)

**Epic ID**: EPIC-11  
**Version**: 1.1  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 1 (Critical Fix)

---

## 1. Epic Overview

### 1.1 Summary

Fix the critical integration gap between `pipeline/graph.py` and `node_execution/executor.py` by implementing **方案C (SessionManager + dynamic work_dir)**. Currently, pipeline execution shows false success (假性成功) — nodes report `completed` status while producing empty deliverables `{}` because the DualAgentNode is never invoked. This epic enables actual Agent execution and file output by activating the claude-agent-sdk `SessionManager` + `work_dir` mechanism.

### 1.2 Business Value

- **Eliminates False Success**: Pipeline nodes will produce real LLM-generated deliverables instead of empty placeholders
- **Activates Existing Code**: CreateDeliverableTool and node_execution systems are fully implemented but unused — this epic connects them
- **Leverages SDK Native Capabilities**: Uses claude-agent-sdk's SessionManager + work_dir design pattern rather than custom workarounds
- **Unblocks All Downstream Development**: Context chaining, quality control, and export features all depend on actual deliverable content

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Deliverable content | All 5 nodes produce non-empty markdown content |
| File output | Files written to `output/{pipeline_id}/` directory |
| Tool invocation | CreateDeliverableTool invoked at least once per node execution |
| False success eliminated | No empty `{}` deliverables in completed pipeline runs |
| Integration test | End-to-end test passes: `proposal.md` → `output/{pipeline_id}/*.md` |

### 1.4 Dependencies

- **Requires**: Epic 6 (SDK Preparation) completed — claude-agent-sdk installed and operational
- **Requires**: Epic 2 (Agent System) — DualAgentNode, IndependentAgent, EvaluatorAgent implemented
- **Requires**: Epic 3 (Pipeline Orchestration) — LangGraph pipeline graph exists
- **Blocks**: Epic 4 (Context Isolation) — needs real deliverable content for isolation testing
- **Blocks**: Epic 5 (Quality Control) — needs real evaluation scores

### 1.5 Source Reference

Based on: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md` — Section 6.3 (方案C) and Section 7 (Implementation Guide)

---

## 2. Architecture Context

### 2.1 Problem: Dual Execution System Gap

```
CURRENT STATE (Broken):

  pipeline/graph.py                      node_execution/executor.py
  ┌─────────────────────┐               ┌─────────────────────────┐
  │ _create_default_     │               │ create_node_executor()  │
  │   node_executor()    │               │   ↓                     │
  │   ↓                  │    ✗ NOT      │ DualAgentNode.execute() │
  │ node_executor_func   │    CONNECTED  │   ↓                     │
  │   is None            │──────────────→│ IndependentAgent        │
  │   ↓                  │               │   ↓                     │
  │ deliverables[id] = {}│               │ EvaluatorAgent          │
  │ status = "completed" │               │   ↓                     │
  │ (FALSE SUCCESS)      │               │ Real deliverable        │
  └─────────────────────┘               └─────────────────────────┘
```

### 2.2 Solution: 方案C (SessionManager + work_dir)

```
TARGET STATE (Fixed):

  pipeline/graph.py
  ┌──────────────────────────────────────────────────────────────────┐
  │ _create_integrated_node_executor(node_id, session_manager)      │
  │   ↓                                                              │
  │ create_node_executor(node_id, session_manager)                   │
  │   ↓                                                              │
  │ DualAgentNode.execute(subject_context)                           │
  │   ↓                                                              │
  │ IndependentAgent                                                 │
  │   ├── SessionManager initialized with work_dir                   │
  │   ├── Prompt: "MUST use create_deliverable tool"                │
  │   ├── SDK query() returns AsyncGenerator                        │
  │   └── CreateDeliverableTool writes to work_dir                   │
  │   ↓                                                              │
  │ EvaluatorAgent                                                   │
  │   └── Reviews actual deliverable content                         │
  │   ↓                                                              │
  │ Output: output/{pipeline_id}/analyst-report.md                   │
  └──────────────────────────────────────────────────────────────────┘
```

### 2.3 Key Files

| File | Purpose | Change Type |
|------|---------|-------------|
| `autoBMAD/docuswarm/agents/independent.py` | IndependentAgent — add work_dir support | Modify |
| `autoBMAD/docuswarm/pipeline/graph.py` | Pipeline graph — integrate node_execution | Modify |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Orchestrator — pass session_manager | Modify |
| `autoBMAD/docuswarm/tools/create_deliverable.py` | CreateDeliverableTool — use work_dir path | Modify |
| `tests/integration/test_node_executor_integration.py` | E2E integration test | Create |

---

## 3. User Stories

### Story 11.1: Enable work_dir on IndependentAgent

**ID**: US-11.1  
**As a** system  
**I want to** have the IndependentAgent SessionManager initialized with `work_dir` parameter  
**So that** the SDK directs file output to the correct directory

**Acceptance Criteria**:
- [ ] `IndependentAgent.execute()` passes `work_dir` to `SessionManager`
- [ ] `work_dir` set to `output/{pipeline_id}/` for file output isolation
- [ ] SessionManager creation succeeds without errors
- [ ] SDK environment variables configured (`ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`)

**Technical Tasks**:
1. Modify `IndependentAgent.execute()` to compute `output_dir = Path("output") / pipeline_id`
2. Create output directory with `mkdir(parents=True, exist_ok=True)`
3. Initialize `SessionManager` with `work_dir=output_dir`
4. Configure environment variables for Kimi Code API:
   - `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`
   - `ANTHROPIC_API_KEY=<your-kimi-api-key>`

**Implementation Reference**:
```python
# autoBMAD/docuswarm/agents/independent.py
async def execute(self, subject_context: str, task: str, feedback: str = "") -> dict:
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "output" / self.pipeline_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    session_manager = SessionManager(
        work_dir=output_dir,
        base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding/"),
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
    )
    
    # Use session_manager for SDK calls
    result = await session_manager.single_prompt(
        prompt=full_prompt,
        agent_name="docuswarm",
        timeout=1800.0,
    )
```

**Definition of Done**:
- SessionManager created with work_dir
- Output directory created at expected path
- SDK environment variables configured

---

### Story 11.2: Modify IndependentAgent Prompt for Tool Calling

**ID**: US-11.2  
**As a** system  
**I want to** have the IndependentAgent prompt instruct the LLM to use `create_deliverable` tool  
**So that** the LLM produces deliverables via tool calls instead of inline JSON

**Acceptance Criteria**:
- [ ] "Respond only with JSON" / "Respond with valid JSON" directive removed from system prompt
- [ ] New directive: "You MUST use the `create_deliverable` tool to save your deliverable"
- [ ] Prompt clarifies that questions should be returned as structured output alongside tool calls
- [ ] LLM successfully calls `create_deliverable` tool during execution
- [ ] No more inline JSON deliverable responses

**Technical Tasks**:
1. Locate current SECTION 3: RESPONSE FORMAT in IndependentAgent system prompt
2. Remove "Respond with valid JSON" directive
3. Add tool-calling instructions:
   - "You MUST use the `create_deliverable` tool to save your work"
   - "Do NOT return deliverable content as JSON — use the tool to write files"
4. Keep questions as structured return (SDK supports mixed tool calls + text output)
5. Test with a single node to verify LLM behavior change

**Prompt Change**:
```
BEFORE:
  ## Response Format
  Respond with valid JSON:
  {"deliverable": {...}, "questions": [...], "private_reasoning": "..."}

AFTER:
  ## Deliverable Output
  You MUST use the 'create_deliverable' tool to save your deliverable document.
  Do NOT return deliverable content in JSON format — use the tool to write files.
  
  After creating your deliverable via the tool:
  1. Generate follow-up questions (blocking, clarifying, optional)
  2. Return a summary of what you created and your questions
```

**Definition of Done**:
- LLM invokes `create_deliverable` tool during node execution
- Tool receives non-empty `title` and `content` parameters
- No JSON-formatted deliverable in LLM response text

---

### Story 11.3: Update CreateDeliverableTool for work_dir

**ID**: US-11.3  
**As a** system  
**I want to** have CreateDeliverableTool write files relative to the SDK `work_dir`  
**So that** deliverable files are saved to `output/{pipeline_id}/`

**Acceptance Criteria**:
- [ ] Tool writes markdown file to `work_dir` path
- [ ] Filename derived from `title` parameter: `{title-slug}.md`
- [ ] File content is non-empty markdown
- [ ] Tool returns success status with file path on success
- [ ] Tool returns error status with clear message on failure
- [ ] Multiple deliverable files for different nodes coexist in same directory

**Technical Tasks**:
1. Modify `CreateDeliverableTool.__call__()` to write relative to `Path.cwd()` (SDK sets cwd to work_dir)
2. Generate filename from title: `title.lower().replace(' ', '-') + '.md'`
3. Write content using `aiofiles` for async I/O
4. Return success status with created file path
5. Handle write errors with error status
6. Unit test with mock work_dir

**Implementation Reference**:
```python
class CreateDeliverableTool:
    async def __call__(self, params: CreateDeliverableParams) -> dict:
        filename = f"{params.title.lower().replace(' ', '-')}.md"
        file_path = Path.cwd() / filename  # Relative to SDK work_dir
        
        try:
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(params.content)
            return {"success": True, "output": f"Deliverable '{params.title}' saved to {file_path}"}
        except Exception as exc:
            return {"success": False, "error": str(exc), "message": "Failed to write deliverable"}
```

**Definition of Done**:
- Markdown file created at `output/{pipeline_id}/{title-slug}.md`
- File content matches what LLM passed to the tool
- Success status returned with correct file path

---

### Story 11.4: Integrate node_execution into Pipeline Graph

**ID**: US-11.4  
**As a** system  
**I want to** have `pipeline/graph.py` use `node_execution/executor.py` for actual node execution  
**So that** the DualAgentNode is invoked during pipeline runs

**Acceptance Criteria**:
- [ ] `create_pipeline_graph()` accepts optional `session_manager` parameter
- [ ] When `session_manager` is provided, uses `_create_integrated_node_executor()`
- [ ] When `session_manager` is `None`, falls back to existing empty executor (backward compatibility)
- [ ] `_create_integrated_node_executor()` calls `create_node_executor()` from node_execution
- [ ] State conversion: PipelineState → NodeRunState → PipelineState
- [ ] `orchestrator.py` passes session_manager when invoking `create_pipeline_graph()`
- [ ] File output via `FileStorage.save_deliverable()` after successful node execution

**Technical Tasks**:
1. Add `session_manager` parameter to `create_pipeline_graph()`
2. Create `_create_integrated_node_executor(node_id, session_manager)` function
3. Implement `_convert_pipeline_to_node_state()` state converter
4. Implement `_convert_node_to_pipeline_state()` state converter
5. Modify `orchestrator.py` to call `self._get_or_create_session_manager()` and pass it
6. Integration test: single node execution through pipeline path

**Implementation Reference**:
```python
# pipeline/graph.py

def create_pipeline_graph(
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
    compile_graph: bool = True,
    session_manager: SessionManager | None = None,  # NEW
) -> Any:
    graph = StateGraph(PipelineState)
    
    for node_id in PIPELINE_NODES:
        if session_manager is not None:
            node_executor = _create_integrated_node_executor(node_id, session_manager)
        else:
            node_executor = _create_default_node_executor(node_id)
        graph.add_node(node_id, node_executor)
    # ... rest unchanged


def _create_integrated_node_executor(node_id, session_manager):
    from autoBMAD.docuswarm.node_execution.executor import create_node_executor
    
    async def executor(state: dict[str, Any]) -> dict[str, Any]:
        node_run_state = _convert_pipeline_to_node_state(state, node_id)
        node_executor = create_node_executor(node_id, session_manager)
        result_state = await node_executor(node_run_state)
        return _convert_node_to_pipeline_state(result_state, state)
    
    return executor
```

**Definition of Done**:
- Pipeline execution invokes DualAgentNode for each node
- State conversions preserve all fields
- Backward compatibility maintained when session_manager is None
- Orchestrator passes session_manager correctly

---

### Story 11.5: End-to-End Integration Test

**ID**: US-11.5  
**As a** developer  
**I want to** have an integration test verifying the complete flow from proposal to file output  
**So that** I can confirm the integration gap is fixed and prevent regression

**Acceptance Criteria**:
- [ ] Test creates a proposal context file
- [ ] Test executes at least one node (analyst) through pipeline
- [ ] Test verifies: deliverable is non-empty in pipeline state
- [ ] Test verifies: markdown file exists in `output/{pipeline_id}/`
- [ ] Test verifies: file content is non-empty and valid markdown
- [ ] Test verifies: CreateDeliverableTool was invoked (not empty placeholder)
- [ ] Test uses `@pytest.mark.integration` marker
- [ ] Test cleans up output directory after execution

**Technical Tasks**:
1. Create `tests/integration/test_node_executor_integration.py`
2. Implement test fixture: create temporary proposal context
3. Implement test: single-node execution → file output
4. Implement test: verify no empty deliverables (`{}`) in pipeline state
5. Implement test: multiple node executions produce isolated files
6. Add cleanup fixture for output directory
7. Add `@pytest.mark.integration` marker (requires API key)

**Test Design**:
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyst_node_produces_deliverable():
    """Verify analyst node produces actual deliverable file (not empty placeholder)."""
    pipeline_id = f"test-{uuid.uuid4().hex[:8]}"
    output_dir = Path("output") / pipeline_id
    
    try:
        # Execute analyst node through pipeline
        result = await execute_single_node(
            node_id="analyst",
            pipeline_id=pipeline_id,
            context={"subject": "Test project for integration verification"},
        )
        
        # Verify deliverable is NOT empty
        assert result["deliverables"]["analyst"] != {}, "Deliverable must not be empty placeholder"
        assert result["deliverables"]["analyst"].get("content", "") != "", "Content must not be empty"
        
        # Verify file output
        output_files = list(output_dir.glob("*.md"))
        assert len(output_files) > 0, f"Expected markdown files in {output_dir}"
        
        # Verify file content
        content = output_files[0].read_text(encoding="utf-8")
        assert len(content) > 100, "Deliverable file must contain substantial content"
    finally:
        if output_dir.exists():
            shutil.rmtree(output_dir)
```

**Definition of Done**:
- Integration test passes with actual Kimi Code API backend
- Test confirms non-empty deliverable content
- Test confirms file written to correct output path
- Test fails gracefully with clear message if API key missing

---

### Story 11.6: Cleanup Dual Execution System

**ID**: US-11.6  
**As a** developer  
**I want to** remove the empty placeholder executor path  
**So that** there is only one execution path and no confusion about which system is active

**Acceptance Criteria**:
- [ ] `_create_default_node_executor()` marked as deprecated or removed
- [ ] `create_pipeline_graph()` requires `session_manager` (no None fallback) for production use
- [ ] Test-only mock executor available for unit tests that don't need real LLM
- [ ] No code path produces empty `{}` deliverables
- [ ] All existing tests updated to use integrated executor or explicit mock

**Technical Tasks**:
1. Mark `_create_default_node_executor()` as `@deprecated` with removal timeline
2. Add warning log when `session_manager=None` is used
3. Update pipeline orchestrator to always provide session_manager
4. Create `MockNodeExecutor` for unit tests
5. Update existing pipeline tests to use mock or integrated executor
6. Verify no empty deliverable paths remain

**Definition of Done**:
- Only one active execution path in production code
- Deprecated path logs warning when used
- All tests pass
- Type checking passes (`basedpyright`)

---

## 4. Technical Specifications

### 4.1 State Conversion

```
PipelineState                        NodeRunState
├── pipeline_id          ──→         ├── run_id (= {pipeline_id}-{node_id})
├── subject_context      ──→         ├── context_file
│   └── content          ──→         ├── task
├── completed_nodes      ──→         ├── chained_context (predecessor deliverables)
├── deliverables                     ├── deliverable (single node)
├── questions                        ├── questions (single node)
├── evaluation_history               ├── evaluation (single node)
└── node_iterations      ──→         ├── iteration
                                     ├── max_iterations (default: 3)
                                     └── status
```

### 4.2 File Output Structure

```
output/
└── {pipeline_id}/               # Per-execution isolation via work_dir
    ├── analyst-report.md        # Created by CreateDeliverableTool
    ├── prd.md
    ├── ux-design.md
    ├── architecture.md
    └── epics-stories.md
```

### 4.3 SDK Integration Points

| Component | SDK Feature | Parameter/Config |
|-----------|-------------|------------------|
| Session Management | SessionManager | `SessionManager(work_dir=Path(f"output/{pipeline_id}/"))` |
| File Output | work_dir | Passed to SessionManager constructor |
| API Endpoint | Environment Variable | `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/` |
| Authentication | Environment Variable | `ANTHROPIC_API_KEY=<your-kimi-api-key>` |
| Tool Execution | query() | `session_manager.single_prompt()` with tool descriptions |

### 4.4 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero new errors |
| Lint | `ruff check docuswarm/` | Zero new errors |
| Unit tests | `pytest tests/unit/ -v` | 100% pass |
| Integration test | `pytest tests/integration/test_node_executor_integration.py -m integration` | 100% pass |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM ignores tool-calling instructions | Medium | High | Prompt engineering iteration; add explicit "MUST use tool" with examples |
| SDK work_dir not setting CWD correctly | Low | High | Verify with smoke test before full integration |
| State conversion data loss | Medium | Medium | Comprehensive unit tests for both conversion functions |
| Backward compatibility breakage | Low | Medium | Keep `_create_default_node_executor` as fallback during transition |
| File write permission errors | Low | Medium | `mkdir(parents=True, exist_ok=True)` + error handling in tool |
| Async context issues in tool | Low | Medium | Use `aiofiles` consistently; test async tool execution |

---

## 6. Implementation Order

```
Story 11.3: CreateDeliverableTool (no external deps, unit testable)
    ↓
Story 11.1: Enable work_dir (requires 11.3)
    ↓
Story 11.2: Modify prompt (requires 11.1)
    ↓
Story 11.4: Integrate into pipeline graph (requires 11.1, 11.2, 11.3)
    ↓
Story 11.5: End-to-end integration test (requires 11.4)
    ↓
Story 11.6: Cleanup dual system (requires 11.5 passing)
```

---

## 7. Definition of Done (Epic Level)

- [ ] All 6 stories completed and tested
- [ ] Pipeline execution produces non-empty deliverables for all 5 nodes
- [ ] Deliverable files written to `output/{pipeline_id}/` directory
- [ ] CreateDeliverableTool invoked during every node execution
- [ ] No empty `{}` deliverables in any code path
- [ ] Integration test passes end-to-end
- [ ] Type checking passes (`basedpyright`)
- [ ] Lint passes (`ruff check`)
- [ ] Existing tests not broken
- [ ] Dual execution system consolidated (deprecated path logged)

---

## 8. References

| Document | Location |
|----------|----------|
| SDK Wrapper Epic | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| Research Report | `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md` |
| System Architecture | `docs/architecture/01_SYSTEM_ARCHITECTURE.md` (Section 9: Known Gaps) |
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` (Section 10: Prompt Conflict) |
| Pipeline Architecture | `docs/architecture/03_PIPELINE_ARCHITECTURE.md` (Section 11: Integration Gap) |
| LLM Integration | `docs/architecture/05_LLM_INTEGRATION.md` (Section 4.4: Tool Status) |
| Course Correction | `docs/plan/CORRECT_COURSE.md` (Section 9: Gap Fix Plan) |
| PRD | `docs/plan/PRD.md` (FR-010: Tool Calling) |

---

**Epic End**
