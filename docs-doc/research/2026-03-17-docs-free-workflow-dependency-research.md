# DocuSwarm Docs-Free Workflow Dependency Research

## Scope

- Decision baseline: Option A is adopted for P1-2.
- Product decision: workflow execution must never read `docs/`.
- Analysis scope: `autoBMAD/docuswarm`, `tests`, and debugging tools under `tools/`.

## Executive Summary

- The runtime still exposes docs read/write capabilities, so the current codebase does not enforce the docs-free workflow decision.
- The test suite explicitly preserves docs tools and their registration, so Option A requires coordinated test removal or rewrite.
- The execution contract still carries `docs_context`, even though current runtime only passes empty lists.
- Existing debug tooling still points investigators toward docs expansion rather than docs removal.
- `create_document_set` is adjacent but should remain governed by `output/`, not removed with docs tooling.

## Inventory

- Runtime files with docs-related hits: 9
- Test files with docs-related hits: 9
- Debug/tooling files with docs-related hits: 3

### Runtime Hit Map

- `autoBMAD\docuswarm\agents\configs\independent_agent.yaml` -> 3 hit(s)
- `autoBMAD\docuswarm\agents\evaluator.py` -> 1 hit(s)
- `autoBMAD\docuswarm\agents\independent.py` -> 1 hit(s)
- `autoBMAD\docuswarm\node_execution\context_builder.py` -> 1 hit(s)
- `autoBMAD\docuswarm\node_execution\contracts.py` -> 1 hit(s)
- `autoBMAD\docuswarm\tools\__init__.py` -> 3 hit(s)
- `autoBMAD\docuswarm\tools\list_docs_files.py` -> 3 hit(s)
- `autoBMAD\docuswarm\tools\read_docs_file.py` -> 7 hit(s)
- `autoBMAD\docuswarm\tools\update_docs_file.py` -> 3 hit(s)

### Tests Hit Map

- `tests\integration\test_single_truth_workflow.py` -> 1 hit(s)
- `tests\unit\agents\test_evaluator_reads_file.py` -> 2 hit(s)
- `tests\unit\nodes\test_dual_agent_single_truth.py` -> 1 hit(s)
- `tests\unit\test_contract_builder.py` -> 2 hit(s)
- `tests\unit\test_node_execution_context.py` -> 4 hit(s)
- `tests\unit\tools\test_explicit_registration.py` -> 24 hit(s)
- `tests\unit\tools\test_list_docs_files.py` -> 52 hit(s)
- `tests\unit\tools\test_read_docs_file.py` -> 37 hit(s)
- `tests\unit\tools\test_update_docs_file.py` -> 42 hit(s)

### Tools Hit Map

- `tools\README.md` -> 2 hit(s)
- `tools\context_injection_auditor.py` -> 6 hit(s)
- `tools\node_execution_context_researcher.py` -> 1 hit(s)

## Findings

### D001 [HIGH] Runtime still exposes docs read/write tools as workflow capabilities

- Summary: Under Option A, the workflow must not read docs/. The current runtime still exposes read_docs_file, list_docs_files, and update_docs_file through the Independent agent configuration and package exports.
- Impact: If P1-2 is removed but these capabilities remain, the system contract will still permit docs/ access at runtime and the product decision cannot be enforced.
- Recommendation: Remove docs read/write tools from the default runtime surface: agent config, tool exports, and any registration path that makes them discoverable to workflow execution.
- Evidence:
  - `autoBMAD\docuswarm\agents\configs\independent_agent.yaml:12` -> `- "autoBMAD.docuswarm.tools.read_docs_file:ReadDocsFileTool"`
  - `autoBMAD\docuswarm\agents\configs\independent_agent.yaml:13` -> `- "autoBMAD.docuswarm.tools.update_docs_file:UpdateDocsFileTool"`
  - `autoBMAD\docuswarm\agents\configs\independent_agent.yaml:14` -> `- "autoBMAD.docuswarm.tools.list_docs_files:ListDocsFilesTool"`
  - `autoBMAD\docuswarm\tools\__init__.py:16` -> `ListDocsFilesTool,`
  - `autoBMAD\docuswarm\tools\__init__.py:20` -> `ReadDocsFileTool,`
  - `autoBMAD\docuswarm\tools\__init__.py:28` -> `UpdateDocsFileTool,`
  - `autoBMAD\docuswarm\tools\__init__.py:62` -> `"ListDocsFilesTool",`
  - `autoBMAD\docuswarm\tools\__init__.py:64` -> `"ReadDocsFileTool",`
  - `autoBMAD\docuswarm\tools\__init__.py:68` -> `"UpdateDocsFileTool",`

### D002 [HIGH] docs/ is still hard-coded as a filesystem dependency in runtime tool modules

- Summary: Three runtime modules compute the project docs root directly and implement list/read/write behavior against that directory.
- Impact: These modules are no longer dormant implementation details once they are registered; they are a direct contradiction of the decision that workflows never read docs/.
- Recommendation: Delete or quarantine read_docs_file.py, list_docs_files.py, and update_docs_file.py from the workflow runtime. Keep them only if a separate non-workflow maintenance surface truly needs them.
- Evidence:
  - `autoBMAD\docuswarm\tools\read_docs_file.py:41` -> `name: str = "read_docs_file"`
  - `autoBMAD\docuswarm\tools\read_docs_file.py:60` -> `return project_root / "docs"`
  - `autoBMAD\docuswarm\tools\list_docs_files.py:47` -> `name: str = "list_docs_files"`
  - `autoBMAD\docuswarm\tools\list_docs_files.py:56` -> `self.docs_root = project_root / "docs"`
  - `autoBMAD\docuswarm\tools\update_docs_file.py:52` -> `name: str = "update_docs_file"`
  - `autoBMAD\docuswarm\tools\update_docs_file.py:62` -> `self.docs_root = project_root / "docs"`

### D003 [MEDIUM] Execution contracts still reserve docs_context even though no docs-free runtime should use it

- Summary: The NodeExecutionContext schema and agent fallbacks still carry docs_context, but current code fills it with empty lists only.
- Impact: Leaving this field in place after removing P1-2 risks future reintroduction of docs reads and keeps the execution contract wider than the product decision requires.
- Recommendation: Decide whether docs_context should be removed from contracts entirely or explicitly marked as deprecated and forbidden for workflow use.
- Evidence:
  - `autoBMAD\docuswarm\node_execution\contracts.py:73` -> `docs_context: list[dict[str, Any]]`
  - `autoBMAD\docuswarm\node_execution\context_builder.py:75` -> `docs_context=[],`
  - `autoBMAD\docuswarm\agents\independent.py:682` -> `docs_context=[],`
  - `autoBMAD\docuswarm\agents\evaluator.py:574` -> `docs_context=[],`

### D004 [HIGH] Tests explicitly lock in docs tool existence and registration

- Summary: The test suite contains dedicated unit tests for read_docs_file, list_docs_files, and update_docs_file, plus registration tests that assert these tools must exist.
- Impact: Option A cannot be implemented safely without deleting or rewriting these tests. Otherwise the test suite will preserve the old contract by design.
- Recommendation: Remove dedicated docs-tool test suites and update registration tests to reflect a workflow surface that no longer includes docs read/write tools.
- Evidence:
  - `tests\unit\tools\test_read_docs_file.py:5` -> `- read_docs_file function success and error cases`
  - `tests\unit\tools\test_read_docs_file.py:196` -> `tool = ToolRegistry.get("read_docs_file")`
  - `tests\unit\tools\test_list_docs_files.py:5` -> `- list_docs_files function success and error cases`
  - `tests\unit\tools\test_list_docs_files.py:287` -> `tool = ToolRegistry.get("list_docs_files")`
  - `tests\unit\tools\test_update_docs_file.py:5` -> `- update_docs_file function success and error cases`
  - `tests\unit\tools\test_update_docs_file.py:263` -> `tool = ToolRegistry.get("update_docs_file")`
  - `tests\unit\tools\test_explicit_registration.py:41` -> `"read_docs_file",`
  - `tests\unit\tools\test_explicit_registration.py:42` -> `"list_docs_files",`
  - `tests\unit\tools\test_explicit_registration.py:43` -> `"update_docs_file",`
  - `tests\unit\tools\test_explicit_registration.py:85` -> `tool = ToolRegistry.get("read_docs_file")`
  - `tests\unit\tools\test_explicit_registration.py:87` -> `assert tool.name == "read_docs_file"`
  - `tests\unit\tools\test_explicit_registration.py:99` -> `tool = ToolRegistry.get("list_docs_files")`
  - `tests\unit\tools\test_explicit_registration.py:101` -> `assert tool.name == "list_docs_files"`
  - `tests\unit\tools\test_explicit_registration.py:113` -> `tool = ToolRegistry.get("update_docs_file")`
  - `tests\unit\tools\test_explicit_registration.py:115` -> `assert tool.name == "update_docs_file"`
  - `tests\unit\tools\test_explicit_registration.py:236` -> `assert "read_docs_file" in tool_names`
  - `tests\unit\tools\test_explicit_registration.py:237` -> `assert "list_docs_files" in tool_names`
  - `tests\unit\tools\test_explicit_registration.py:238` -> `assert "update_docs_file" in tool_names`
  - `tests\unit\tools\test_explicit_registration.py:249` -> `"read_docs_file",`
  - `tests\unit\tools\test_explicit_registration.py:250` -> `"list_docs_files",`
  - `tests\unit\tools\test_explicit_registration.py:251` -> `"update_docs_file",`

### D005 [MEDIUM] Docs-tool tests are already drifting from the current runtime implementation

- Summary: Several tests assume an async function-based docs API and the absence of kimi_agent_sdk imports, while the current modules still expose CallableTool2 classes.
- Impact: This drift means the docs-tool tests should not be carried forward into a docs-free workflow. Deleting them is lower risk than trying to repair a capability the product no longer wants.
- Recommendation: Treat docs-tool tests as removal candidates, not migration candidates. The product decision eliminates their target behavior.
- Evidence:
  - `tests\unit\tools\test_read_docs_file.py:49` -> `from docuswarm.tools.read_docs_file import ReadDocsFileParams, read_docs_file`
  - `tests\unit\tools\test_read_docs_file.py:80` -> `from docuswarm.tools.read_docs_file import ReadDocsFileParams, read_docs_file`
  - `tests\unit\tools\test_read_docs_file.py:103` -> `from docuswarm.tools.read_docs_file import ReadDocsFileParams, read_docs_file`
  - `tests\unit\tools\test_read_docs_file.py:127` -> `from docuswarm.tools.read_docs_file import ReadDocsFileParams, read_docs_file`
  - `tests\unit\tools\test_read_docs_file.py:154` -> `from docuswarm.tools.read_docs_file import ReadDocsFileParams, read_docs_file`
  - `tests\unit\tools\test_read_docs_file.py:211` -> `assert not hasattr(module, 'CallableTool2'), "Module should not have CallableTool2"`
  - `autoBMAD\docuswarm\tools\read_docs_file.py:13` -> `from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue`
  - `tests\unit\tools\test_update_docs_file.py:278` -> `assert not hasattr(module, 'CallableTool2'), "Module should not have CallableTool2"`
  - `autoBMAD\docuswarm\tools\update_docs_file.py:14` -> `from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue`

### D006 [MEDIUM] Existing debug tooling still assumes docs expansion is a viable direction

- Summary: The current tools README and context audit utility still frame docs expansion as something to design and improve, which conflicts with the new product decision.
- Impact: If debugging tools keep recommending docs expansion, future investigations may accidentally re-open a capability that should be retired.
- Recommendation: Update research/debug tooling so the new baseline is explicit: workflow execution must not read docs/, and any remaining docs references are migration debt.
- Evidence:
  - `tools\README.md:32` -> `- docs 工具是否具备受控扩展策略`
  - `tools\context_injection_auditor.py:242` -> `"Introduce a docs retrieval policy layer: list -> select -> read -> summarize -> attach "`
  - `tools\node_execution_context_researcher.py:346` -> `{"name": "docs_context", "type": "list", "source": "docs tools", "description": "文档上下文"},`

### D007 [INFO] create_document_set is adjacent to docs tooling but is not a docs-read dependency

- Summary: create_document_set writes to the current working directory rather than reading from docs/. It should not be removed solely because P1-2 is removed.
- Impact: A broad cleanup could accidentally delete a still-valid output-side capability if docs tools and multi-file output are treated as the same concern.
- Recommendation: Keep create_document_set under output/work_dir governance and decouple it from any docs-specific cleanup work.
- Evidence:
  - `autoBMAD\docuswarm\tools\create_document_set.py:217` -> `output_dir = Path.cwd()`

## Removal Implications

- Delete or isolate runtime docs tool modules from workflow execution surfaces.
- Remove docs tool entries from default agent configuration.
- Rewrite tool registration expectations in tests to drop docs tool names.
- Decide whether `docs_context` should be removed or deprecated from execution contracts.
- Update debug tooling so future audits treat docs references as debt, not roadmap.
- Keep `create_document_set` as an output-side capability if multi-file output is still needed.

## Recommended Next Step Order

1. Freeze the decision in research/evaluation docs.
2. Remove docs tool exposure from runtime configs and exports.
3. Delete or rewrite docs-tool test suites and registration expectations.
4. Clean up `docs_context` contract residue.
5. Rebaseline debug tooling and architecture research assumptions.
