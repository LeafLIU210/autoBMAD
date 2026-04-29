# TDD Fix Plan: Import Fracture Recovery

**Date**: 2026-04-28  
**Based on**: `docs-doc/research/2026-04-28-docuswarm-pipeline-import-fracture-deep-analysis.md`  
**Scope**: `autoBMAD/nodes/`, `autoBMAD/docuswarm/nodes/`, `tests/`  
**Goal**: Unblock pipeline execution and restore all broken import chains  

---

## 1. Problem Statement

Commit `6a4c3ca` deleted `autoBMAD/docuswarm/nodes/loader.py` and rewired imports to `autoBMAD.nodes.loader`, but the target module lacks symbols that production code still expects. This creates a **cascading import fracture**:

- `NodeValidationError` — missing, breaks `autoBMAD.docuswarm.nodes.__init__`
- `NodeFilePermissions`, `NodeSearchPermissions`, `NodeToolPermissions` — missing, breaks `permissions.py`, `session_manager.py`, `tool_filter.py`, `independent.py`
- `NodeSkillsConfig` — implicitly required via `node_config.tool_permissions.skills`
- `autoBMAD/nodes/__init__.py` — uses obsolete absolute import `from nodes.loader import ...`

---

## 2. TDD Strategy

### Phase 1: Write Failing Tests
1. **`tests/test_nodes_loader_symbols.py`** — Assert that `autoBMAD.nodes.loader` exports all required symbols
2. **`tests/test_docuswarm_nodes_import.py`** — Assert that `autoBMAD.docuswarm.nodes` and all submodules import successfully
3. **`tests/test_node_config_tool_permissions.py`** — Assert that `NodeLoader.load("analyst")` returns a `NodeConfig` with accessible `tool_permissions`

### Phase 2: Run Tests (Expect Red)
- All tests should fail, confirming the fractures

### Phase 3: Implement Minimal Fixes
1. **`autoBMAD/nodes/loader.py`** — Add missing dataclasses and exception
2. **`autoBMAD/nodes/loader.py`** — Add `tool_permissions` field to `NodeConfig`
3. **`autoBMAD/nodes/loader.py`** — Parse `tools` section in `_build_node_config`
4. **`autoBMAD/nodes/__init__.py`** — Fix import path to `.loader`
5. **`autoBMAD/docuswarm/nodes/__init__.py`** — Remove `NodeValidationError` re-export

### Phase 4: Run Tests (Expect Green)
- All tests pass

### Phase 5: Integration Verification
- Run `python -c "from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator; print('OK')"`
- Run `python -c "from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node; print('OK')"`

---

## 3. Symbol Specification

### `NodeValidationError(Exception)`
```python
class NodeValidationError(Exception):
    """Raised when node configuration validation fails."""
```

### `NodeFilePermissions`
```python
@dataclass
class NodeFilePermissions:
    allowed_read_dirs: list[str] = field(default_factory=list)
    allowed_write_dirs: list[str] = field(default_factory=list)
```

### `NodeSearchPermissions`
```python
@dataclass
class NodeSearchPermissions:
    search_dirs: list[str] = field(default_factory=list)
```

### `NodeSkillsConfig`
```python
@dataclass
class NodeSkillsConfig:
    sdk_native: bool = False
    whitelist: list[str] = field(default_factory=list)
    quick_reference_enabled: bool = False
    quick_reference_include_descriptions: bool = False
```

### `NodeToolPermissions`
```python
@dataclass
class NodeToolPermissions:
    allowed_builtin_tools: list[str] = field(default_factory=list)
    file_permissions: NodeFilePermissions = field(default_factory=NodeFilePermissions)
    search_permissions: NodeSearchPermissions = field(default_factory=NodeSearchPermissions)
    skills: NodeSkillsConfig = field(default_factory=NodeSkillsConfig)
    shared_context: dict[str, Any] = field(default_factory=dict)
```

### `NodeConfig` extension
```python
@dataclass
class NodeConfig:
    # ... existing fields ...
    tool_permissions: NodeToolPermissions | None = None
```

### `NodeLoader` extension
In `_build_node_config`, parse `config.get("tools", {})`:
```python
tools_data = config.get("tools", {})
skills_data = tools_data.get("skills", {})
skills_config = NodeSkillsConfig(
    sdk_native=skills_data.get("sdk_native", False),
    whitelist=skills_data.get("whitelist", []),
    quick_reference_enabled=skills_data.get("quick_reference_enabled", False),
    quick_reference_include_descriptions=skills_data.get("quick_reference_include_descriptions", False),
)
tool_permissions = NodeToolPermissions(
    allowed_builtin_tools=tools_data.get("allowed_builtin_tools", []),
    file_permissions=NodeFilePermissions(
        allowed_read_dirs=tools_data.get("file_permissions", {}).get("allowed_read_dirs", []),
    ),
    search_permissions=NodeSearchPermissions(
        search_dirs=tools_data.get("search_permissions", {}).get("search_dirs", []),
    ),
    skills=skills_config,
)
```

---

## 4. File Change Checklist

| # | File | Change Type | Description |
|---|------|-------------|-------------|
| 1 | `tests/test_nodes_loader_symbols.py` | Create | Verify all loader symbols exist |
| 2 | `tests/test_docuswarm_nodes_import.py` | Create | Verify docuswarm.nodes import chain |
| 3 | `tests/test_node_config_tool_permissions.py` | Create | Verify NodeConfig.tool_permissions |
| 4 | `autoBMAD/nodes/loader.py` | Modify | Add missing classes + tool_permissions parsing |
| 5 | `autoBMAD/nodes/__init__.py` | Modify | Fix `from nodes.loader` → `from .loader` |
| 6 | `autoBMAD/docuswarm/nodes/__init__.py` | Modify | Remove `NodeValidationError` import/export |

---

## 5. Acceptance Criteria

- [ ] `python -m pytest tests/test_nodes_loader_symbols.py -v` passes
- [ ] `python -m pytest tests/test_docuswarm_nodes_import.py -v` passes
- [ ] `python -m pytest tests/test_node_config_tool_permissions.py -v` passes
- [ ] `python -c "from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node; print('OK')"` succeeds
- [ ] `python -c "from autoBMAD.docuswarm.node_execution.executor import create_node_executor; print('OK')"` succeeds
- [ ] `python -c "from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator; print('OK')"` succeeds
- [ ] `python tools/import_fracture_detector.py` shows **zero critical** fractures in production code
