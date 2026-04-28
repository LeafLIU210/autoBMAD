---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F1-F8 深度决策研究报告 (2026-03-17-docuswarm-decision-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史审计文档，相关发现已整合到 F1-F8 决策体系中。当前决策以 `docs/DECISIONS.md` 为准。
---

# DocuSwarm Context Injection Audit

## Scope

- Static audit of context contract, prompt assembly, persistence, and docs expansion paths.
- Focused on the current `autoBMAD/docuswarm` implementation and `autoBMAD/nodes/*/node.yaml`.

## Findings

### F001 [HIGH] Node configuration is loaded but not assembled into the prompt contract

- Summary: The executor loads node configuration, but downstream execution still derives the task from serialized runtime state instead of a stable node contract.
- Recommendation: Introduce a single NodeExecutionContext that carries node task, role supplement, deliverable requirements, original context, and chained deliverables end-to-end.
- Evidence:
  - `autoBMAD\docuswarm\node_execution\executor.py:109` -> `node_config = loader.load(node_id)`
  - `autoBMAD\docuswarm\node_execution\executor.py:137` -> `task = _extract_task_from_state(state)`
  - `autoBMAD\docuswarm\nodes\loader.py:7` -> `- node.yaml: Node-specific configuration (node_id, name, sequence, deliverable_type)`
  - `autoBMAD\docuswarm\nodes\loader.py:8` -> `- persona.json: Independent Agent persona configuration`
  - `autoBMAD\docuswarm\nodes\loader.py:9` -> `- evaluator.yaml: Evaluator Agent evaluation criteria`
  - `autoBMAD\docuswarm\nodes\loader.py:34` -> `deliverable_type: Type of deliverable this node produces`
  - `autoBMAD\docuswarm\nodes\loader.py:35` -> `persona: Persona configuration for the Independent Agent`
  - `autoBMAD\docuswarm\nodes\loader.py:36` -> `evaluator: Evaluation criteria configuration for the Evaluator Agent`
  - `autoBMAD\docuswarm\nodes\loader.py:42` -> `deliverable_type: str`
  - `autoBMAD\docuswarm\nodes\loader.py:43` -> `persona: dict[str, Any]`
  - `autoBMAD\docuswarm\nodes\loader.py:44` -> `evaluator: dict[str, Any]`
  - `autoBMAD\docuswarm\nodes\loader.py:58` -> `if not self.deliverable_type:`
  - `autoBMAD\docuswarm\nodes\loader.py:59` -> `raise NodeValidationError("deliverable_type is required")`
  - `autoBMAD\docuswarm\nodes\loader.py:60` -> `if not self.persona:`
  - `autoBMAD\docuswarm\nodes\loader.py:61` -> `raise NodeValidationError("persona is required")`
  - `autoBMAD\docuswarm\nodes\loader.py:62` -> `if "name" not in self.persona:`
  - `autoBMAD\docuswarm\nodes\loader.py:63` -> `raise NodeValidationError("persona must contain 'name' field")`
  - `autoBMAD\docuswarm\nodes\loader.py:64` -> `if "role" not in self.persona:`
  - `autoBMAD\docuswarm\nodes\loader.py:65` -> `raise NodeValidationError("persona must contain 'role' field")`
  - `autoBMAD\docuswarm\nodes\loader.py:66` -> `if not self.evaluator:`
  - `autoBMAD\docuswarm\nodes\loader.py:67` -> `raise NodeValidationError("evaluator is required")`
  - `autoBMAD\docuswarm\nodes\loader.py:68` -> `if "criteria" not in self.evaluator:`
  - `autoBMAD\docuswarm\nodes\loader.py:69` -> `raise NodeValidationError("evaluator must contain 'criteria' field")`
  - `autoBMAD\docuswarm\nodes\loader.py:77` -> `- persona.json: Independent Agent persona`
  - `autoBMAD\docuswarm\nodes\loader.py:78` -> `- evaluator.yaml: Evaluator Agent criteria`
  - `autoBMAD\docuswarm\nodes\loader.py:171` -> `# Load persona.json`
  - `autoBMAD\docuswarm\nodes\loader.py:172` -> `persona_json_path = node_dir / "persona.json"`
  - `autoBMAD\docuswarm\nodes\loader.py:173` -> `persona_data = self._load_json(persona_json_path)`
  - `autoBMAD\docuswarm\nodes\loader.py:175` -> `# Load evaluator.yaml`
  - `autoBMAD\docuswarm\nodes\loader.py:176` -> `evaluator_yaml_path = node_dir / "evaluator.yaml"`
  - `autoBMAD\docuswarm\nodes\loader.py:177` -> `evaluator_data = self._load_yaml(evaluator_yaml_path)`
  - `autoBMAD\docuswarm\nodes\loader.py:184` -> `deliverable_type=node_data.get("deliverable_type", ""),`
  - `autoBMAD\docuswarm\nodes\loader.py:185` -> `persona=persona_data,`
  - `autoBMAD\docuswarm\nodes\loader.py:186` -> `evaluator=evaluator_data,`
  - `autoBMAD\docuswarm\agents\independent.py:125` -> `def _format_system_prompt(self) -> str:`
  - `autoBMAD\docuswarm\agents\independent.py:175` -> `- The "deliverable.content" field is just a SUMMARY, not the full document`

### F002 [HIGH] Task extraction collapses node intent into raw context payload

- Summary: The current task extraction prefers subject context content from serialized state, so node-specific work instructions are replaced by raw input text or previous deliverables.
- Recommendation: Replace `_extract_task_from_state()` with contract-first assembly from node config and a normalized pipeline context object.
- Evidence:
  - `autoBMAD\docuswarm\node_execution\executor.py:217` -> `def _extract_task_from_state(state: NodeRunState) -> str:`
  - `autoBMAD\docuswarm\node_execution\executor.py:234` -> `if isinstance(context_data, dict) and "subject_context" in context_data:`
  - `autoBMAD\docuswarm\node_execution\executor.py:240` -> `if "content" in subject_dict:`
  - `autoBMAD\docuswarm\node_execution\executor.py:241` -> `return str(subject_dict["content"])`
  - `autoBMAD\docuswarm\node_execution\executor.py:259` -> `if "deliverable" in context_data:`

### F003 [HIGH] DualAgentNode re-wraps context and breaks structure expected by IndependentAgent

- Summary: The node wrapper turns subject context into `{subject, task}` and the IndependentAgent then tries to re-discover content through best-effort parsing.
- Recommendation: Pass a structured execution context object directly into both agents. Avoid stringifying and re-wrapping the same payload across layers.
- Evidence:
  - `autoBMAD\docuswarm\nodes\dual_agent.py:323` -> `subject_context={"subject": subject_context, "task": task},`
  - `autoBMAD\docuswarm\nodes\dual_agent.py:327` -> `independent_context["pipeline_id"] = pipeline_id`
  - `autoBMAD\docuswarm\nodes\dual_agent.py:566` -> `subject_context={"subject": subject_context, "task": task},`
  - `autoBMAD\docuswarm\agents\independent.py:453` -> `subject_context_raw = context.get("subject_context", {})`
  - `autoBMAD\docuswarm\agents\independent.py:458` -> `subject_context_data = json_module.loads(subject_context_raw)`
  - `autoBMAD\docuswarm\agents\independent.py:473` -> `nested_ctx = subject_context_data.get("subject_context", {})`
  - `autoBMAD\docuswarm\agents\independent.py:481` -> `raw_content = subject_context_data.get("content")`

### F004 [HIGH] Deliverable persistence currently has two truths

- Summary: The IndependentAgent prompt defines `deliverable.content` as a short summary, but the pipeline graph writes that field back to storage as if it were the canonical deliverable.
- Recommendation: Use tool-written markdown files as the single truth. Keep only metadata, summary, file path, hash, and section inventory in pipeline state.
- Evidence:
  - `autoBMAD\docuswarm\agents\independent.py:175` -> `- The "deliverable.content" field is just a SUMMARY, not the full document`
  - `autoBMAD\docuswarm\agents\independent.py:176` -> `- The full document was already saved via the tool`
  - `autoBMAD\docuswarm\pipeline\graph.py:453` -> `content = deliverable.get("content") or deliverable.get("markdown") or str(deliverable)`
  - `autoBMAD\docuswarm\pipeline\graph.py:454` -> `await storage.save_deliverable(`

### F005 [MEDIUM] update_context is exposed as a capability but does not persist anything

- Summary: The tool acknowledges updates without mutating any shared state, which makes the agent believe it can evolve context while the system remains unchanged.
- Recommendation: Wire the tool to StateManager with a bounded schema and audit trail, or remove it until the real persistence path exists.
- Evidence:
  - `autoBMAD\docuswarm\tools\update_context.py:56` -> `# This is a no-op implementation since there's no actual context store`
  - `autoBMAD\docuswarm\tools\update_context.py:58` -> `return ToolOk(`
  - `autoBMAD\docuswarm\storage\state_manager.py:33` -> `class StateManager:`
  - `autoBMAD\docuswarm\storage\state_manager.py:415` -> `def update_subject_context(self, pipeline_id: str, context_update: dict[str, Any]) -> bool:`

### F006 [MEDIUM] Docs tools exist, but there is no controlled context expansion policy

- Summary: The docs tools are registered, yet the runtime prompt does not define selection order, token budgeting, or when docs content should become part of the working context.
- Recommendation: Introduce a docs retrieval policy layer: list -> select -> read -> summarize -> attach summary to execution context, with per-node allowlists and size limits.
- Evidence:
  - `autoBMAD\docuswarm\agents\configs\independent_agent.yaml:12` -> `- "autoBMAD.docuswarm.tools.read_docs_file:ReadDocsFileTool"`
  - `autoBMAD\docuswarm\agents\configs\independent_agent.yaml:13` -> `- "autoBMAD.docuswarm.tools.update_docs_file:UpdateDocsFileTool"`
  - `autoBMAD\docuswarm\agents\configs\independent_agent.yaml:14` -> `- "autoBMAD.docuswarm.tools.list_docs_files:ListDocsFilesTool"`
  - `autoBMAD\docuswarm\tools\read_docs_file.py:41` -> `name: str = "read_docs_file"`
  - `autoBMAD\docuswarm\tools\list_docs_files.py:47` -> `name: str = "list_docs_files"`

### F007 [MEDIUM] The documented @ path injection entry point is missing in current code

- Summary: Architecture and research docs describe a ContextResolver and @ path injection flow, but the expected module is absent and `main.py` does not integrate it.
- Recommendation: Treat docs injection as a separate controlled stage. Only add a resolver when the design for canonical context assembly is finalized.
- Evidence:
  - `autoBMAD\docuswarm\main.py:109` -> `content = f.read()`
  - `autoBMAD\docuswarm\main.py:131` -> `subject_context = {`

## Node YAML Inventory

### `autoBMAD\nodes\analyst\node.yaml`

- Top-level keys: node_id, name, description, sequence, deliverable_type, deliverable, agent, questions, dependencies
- Has `task` block: False
- Has `role_supplement`: False
- Has `template_title`: False
- Has `required_sections`: True
- Has `output_filename`: False

### `autoBMAD\nodes\architect\node.yaml`

- Top-level keys: node_id, name, description, sequence, deliverable_type, deliverable, agent, questions, dependencies
- Has `task` block: False
- Has `role_supplement`: False
- Has `template_title`: False
- Has `required_sections`: True
- Has `output_filename`: False

### `autoBMAD\nodes\pm\node.yaml`

- Top-level keys: node_id, name, description, sequence, deliverable_type, deliverable, agent, questions, dependencies
- Has `task` block: False
- Has `role_supplement`: False
- Has `template_title`: False
- Has `required_sections`: True
- Has `output_filename`: False

### `autoBMAD\nodes\po\node.yaml`

- Top-level keys: node_id, name, description, sequence, deliverable_type, deliverable, agent, questions, dependencies
- Has `task` block: False
- Has `role_supplement`: False
- Has `template_title`: False
- Has `required_sections`: True
- Has `output_filename`: False

### `autoBMAD\nodes\ux\node.yaml`

- Top-level keys: node_id, name, description, sequence, deliverable_type, deliverable, agent, questions, dependencies
- Has `task` block: False
- Has `role_supplement`: False
- Has `template_title`: False
- Has `required_sections`: True
- Has `output_filename`: False

## Notes

- All current node.yaml files under autoBMAD/nodes still use the older schema without a top-level task block.
- Current node.yaml files do include required_sections, which means prompt injection can be restored without inventing new authoring artifacts.
