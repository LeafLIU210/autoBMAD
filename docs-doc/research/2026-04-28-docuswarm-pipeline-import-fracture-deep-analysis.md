# DocuSwarm Pipeline Import Fracture — Deep Analysis Report

**Report Date**: 2026-04-28  
**Severity**: CRITICAL (Pipeline Execution Blocker)  
**Scope**: `autoBMAD.docuswarm.nodes` package, `autoBMAD.nodes.loader`, and cascading import chain  
**Tools Used**: `tools/import_fracture_detector.py`, `tools/pipeline_import_tracer.py`, `git`, `grep`, `ast`  

---

## 1. Executive Summary

On 2026-04-28 at 20:18:36, the DocuSwarm hybrid orchestrator failed to execute a pipeline with the error:

```
cannot import name 'NodeValidationError' from 'autoBMAD.nodes.loader'
```

This report demonstrates that the failure is **not an isolated symbol-missing bug**, but rather the **tip of a systemic import-fracture iceberg** caused by an **incomplete refactoring** in commit `6a4c3ca`. The commit deleted `autoBMAD/docuswarm/nodes/loader.py` (the original home of `NodeValidationError`) and rewired imports in `autoBMAD/docuswarm/nodes/__init__.py` to point at `autoBMAD.nodes.loader`, but the target module never contained `NodeValidationError`. Additionally, `autoBMAD/nodes/__init__.py` still references the obsolete top-level `nodes.loader` path, creating a secondary fracture.

**Immediate Impact**: Pipeline execution is completely blocked. Any code path that triggers `import autoBMAD.docuswarm.nodes` (or any sub-module thereof) will crash.

**Secondary Impact**: 46 distinct import fractures were detected across the codebase, including missing symbols (`NodeFilePermissions`, `NodeSearchPermissions`, `NodeToolPermissions`, `NodeSharedContextConfig`) that were defined in the deleted loader but are still imported by production code, tools, and documentation.

---

## 2. Problem Phenomenon

### 2.1 Log Evidence

Source: `logs/docuswarm-2026-04-28.log`

```
2026-04-28T20:18:36.435944+08:00 [error] run_id=pipeline-1777378716418-91f0fcac \
  node_id=orchestrator message="pipeline_execution_error" \
  error=cannot import name 'NodeValidationError' from 'autoBMAD.nodes.loader' \
  (/home/leafliu/autoBMAD/autoBMAD/nodes/loader.py)
```

Preceding log lines show the pipeline successfully:
1. Initialized the hybrid orchestrator
2. Validated subject context via LLM
3. Created pipeline work directory
4. Loaded summary agent config
5. Chose the integrated node executor

**The crash occurs at the exact moment the LangGraph state machine attempts to lazily import the real node executor**, confirming this is a late-stage import fracture rather than a startup configuration error.

### 2.2 Reproduction

```python
>>> from autoBMAD.docuswarm.nodes import NodeValidationError
ImportError: cannot import name 'NodeValidationError' from 'autoBMAD.nodes.loader'

>>> from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
ImportError: cannot import name 'NodeValidationError' from 'autoBMAD.nodes.loader'
```

Note that even importing `dual_agent` directly fails because Python executes `autoBMAD/docuswarm/nodes/__init__.py` **before** loading the sub-module.

---

## 3. Root Cause Deep Analysis

### 3.1 The Trigger Chain (Step-by-Step)

```
1. orchestrator.start_pipeline(subject_context)
   └── 2. graph.create_pipeline_graph(session_manager=sm)
        └── 3. _create_integrated_node_executor("analyst", sm)
             └── [LAZY IMPORT at runtime]
                 4. from autoBMAD.docuswarm.node_execution.executor import create_node_executor
                     └── 5. from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
                          └── [Python package init rule]
                              6. autoBMAD/docuswarm/nodes/__init__.py executes FIRST
                                  └── 7. line 14: from autoBMAD.nodes.loader import NodeConfig, NodeLoader, NodeValidationError
                                      └── 8. autoBMAD/nodes/__init__.py executes
                                          └── 9. line 3: from nodes.loader import (...)
                                              └── [circular re-entry or missing module]
                                                  10. FAIL: NodeValidationError not found
```

**Key Insight**: The failure happens in step 7, but step 9 (`autoBMAD/nodes/__init__.py`) also contains a fracture (`from nodes.loader import ...`) that will surface as soon as the `NodeValidationError` issue is resolved.

### 3.2 Python Import Mechanism Detail

Python's import system has a critical behavior that amplifies this bug:

> When importing `autoBMAD.docuswarm.nodes.dual_agent`, the interpreter **always** executes `autoBMAD/docuswarm/nodes/__init__.py` before loading `dual_agent.py`, because `dual_agent` is a submodule of the `nodes` package.

This means:
- **Every** import of `dual_agent` or `iteration` triggers the broken `__init__.py`
- Even "direct" imports like `from autoBMAD.docuswarm.nodes.dual_agent import X` are blocked
- The `__init__.py` is essentially a **mandatory gate** that cannot be bypassed

### 3.3 Git Historical Evidence

Commit `6a4c3ca` (2026-04-28 12:18:28) — *"refactor(docuswarm): 重构项目为DocuSwarm多代理文档编排系统"*

```bash
$ git show 6a4c3ca --name-status | grep -E "nodes/__init__|nodes/loader"
M    autoBMAD/docuswarm/nodes/__init__.py
D    autoBMAD/docuswarm/nodes/loader.py
```

**Diff of `autoBMAD/docuswarm/nodes/__init__.py` in 6a4c3ca:**

```diff
-from autoBMAD.docuswarm.nodes.loader import NodeConfig, NodeLoader, NodeValidationError
+from autoBMAD.nodes.loader import NodeConfig, NodeLoader, NodeValidationError
```

**The problem**: The old module (`autoBMAD.docuswarm.nodes.loader`) was deleted, and the import was redirected to `autoBMAD.nodes.loader`. However, `NodeValidationError` was **never** defined in `autoBMAD/nodes/loader.py` (confirmed by AST scan and runtime inspection).

Historical presence of `NodeValidationError`:

```bash
$ git show 3c1f84f:autoBMAD/docuswarm/nodes/loader.py | grep -n "class NodeValidationError"
16:class NodeValidationError(Exception):
```

The class existed in the **deleted** `autoBMAD/docuswarm/nodes/loader.py` but was **not migrated** to the new canonical module `autoBMAD/nodes/loader.py`.

### 3.4 Code-Level Evidence

**Current `autoBMAD/docuswarm/nodes/__init__.py` (line 14):**

```python
from autoBMAD.nodes.loader import NodeConfig, NodeLoader, NodeValidationError
```

**Current `autoBMAD/nodes/loader.py` (symbol inventory):**

```python
NodeAgentConfig
NodeTaskConfig
NodeDeliverableConfig
NodeQuestionConfig
NodeQuestionsConfig
NodeDependenciesConfig
NodeEvaluatorConfig
NodeConfig
NodeLoader
# NodeValidationError — ABSENT
# NodeFilePermissions — ABSENT
# NodeSearchPermissions — ABSENT
# NodeToolPermissions — ABSENT
# NodeSharedContextConfig — ABSENT
# NodeRuntimeConfig — ABSENT
# NodeSkillsConfig — ABSENT
```

**Current `autoBMAD/nodes/__init__.py` (line 3):**

```python
from nodes.loader import (
    NodeAgentConfig,
    NodeConfig,
    ...
)
```

This uses the absolute import name `nodes.loader`, which resolves to the **top-level** `nodes/` package in the project root. That package **no longer exists** (it was part of the legacy structure). This import will fail with `ModuleNotFoundError: No module named 'nodes'` in any environment where the project root is not on `sys.path` and the legacy `nodes/` directory is absent.

---

## 4. Debugging Tools & Methodology

Two new tools were created to systematize the investigation.

### 4.1 `tools/import_fracture_detector.py`

**Purpose**: Static + runtime hybrid scanner that detects broken imports across the entire codebase.

**Method**:
1. Recursively parses all `.py` files using the `ast` module
2. Extracts `Import` and `ImportFrom` nodes
3. Filters for project-internal imports
4. Attempts runtime `importlib.import_module()` for each target
5. Validates that imported symbols actually exist via `hasattr()`
6. Cross-references with `git diff HEAD~1 --name-status` to flag imports from recently deleted modules

**Key Results**:
- **252 files scanned**, **1,806 imports checked**
- **46 fractures detected** (37 Critical, 9 High)
- **16 modules deleted** in the last commit still have dangling imports

Top fracture categories:

| Category | Count | Description |
|----------|-------|-------------|
| `missing_symbol` | 19 | Symbol no longer exists in target module |
| `broken_import` | 14 | Module cannot be imported at all |
| `init_reexport_broken` | 8 | `__init__.py` re-exports from broken module |
| `init_reexport_missing_symbol` | 1 | `__init__.py` re-exports nonexistent symbol |
| `critical_chain_failure` | 1 | Runtime import of critical module fails |

### 4.2 `tools/pipeline_import_tracer.py`

**Purpose**: Reproduces the exact runtime import chain that leads to the pipeline failure and documents it as a traceable report.

**Method**:
1. Simulates each link in the import chain from `orchestrator` → `graph` → `executor` → `dual_agent` → `nodes.__init__`
2. Captures the actual Python traceback at the fracture point
3. Generates a markdown report with the failure chain, root cause, and recommended fixes

**Key Result**:
- Confirmed the exact line (`autoBMAD/docuswarm/nodes/__init__.py:14`) and symbol (`NodeValidationError`) that breaks the chain
- Discovered the secondary fracture in `autoBMAD/nodes/__init__.py:3`

---

## 5. Impact Scope Assessment

### 5.1 Direct Impact (Runtime)

Any execution path that imports from `autoBMAD.docuswarm.nodes` is blocked:

| Import Path | Status | Notes |
|-------------|--------|-------|
| `autoBMAD.docuswarm.nodes.dual_agent` | **BROKEN** | Triggers `__init__.py` |
| `autoBMAD.docuswarm.nodes.iteration` | **BROKEN** | Triggers `__init__.py` |
| `autoBMAD.docuswarm.node_execution.executor` | **BROKEN** | Imports `dual_agent` |
| `autoBMAD.docuswarm.pipeline.graph` | **DORMANT** | Lazy import defers failure to runtime |
| `autoBMAD.docuswarm.pipeline.orchestrator` | **DORMANT** | Does not import `nodes` at load time |

**Bottom line**: `orchestrator` and `graph` can be *imported* successfully, but as soon as `start_pipeline()` reaches the graph execution phase, the lazy import explodes. This is why the log shows successful initialization followed by a late-stage crash.

### 5.2 Secondary Impact (Code Quality / Maintainability)

The import fracture detector revealed **46 total fractures** across the codebase, indicating the refactoring was far from atomic. Key secondary issues:

| Missing Symbol | Import Locations | Production? |
|----------------|------------------|-------------|
| `NodeFilePermissions` | `permissions.py`, `session_manager.py`, `independent.py`, `tool_filter.py` | **YES** |
| `NodeSearchPermissions` | Same as above | **YES** |
| `NodeToolPermissions` | Same as above + tools | **YES** |
| `NodeSharedContextConfig` | `permissions.py`, `tools/f2_debugger.py`, `tools/f5_debugger.py` | Tools only |
| `NodeValidationError` | `nodes/__init__.py` | **YES** |

These symbols were part of the deleted `autoBMAD/docuswarm/nodes/loader.py` but are still expected by production code. Their absence means even after fixing `NodeValidationError`, other runtime errors will surface as soon as those code paths are exercised.

### 5.3 Tertiary Impact (Documentation / Planning Drift)

Multiple `docs-doc/solution/` and `docs-doc/research/` files still reference the old import paths and symbols. While these do not affect runtime, they create **cognitive debt** and risk misleading future developers or AI agents into implementing against obsolete APIs.

---

## 6. Fix Recommendations

### 6.1 Immediate Fix (Unblock Pipeline)

**File**: `autoBMAD/docuswarm/nodes/__init__.py`

```diff
-from autoBMAD.nodes.loader import NodeConfig, NodeLoader, NodeValidationError
+from autoBMAD.nodes.loader import NodeConfig, NodeLoader

 __all__ = [
     "DualAgentNode",
     "DualAgentNodeError",
     "NodeResult",
     "create_dual_agent_node",
     "IterationController",
     "IterationHistory",
     "NodeIterationState",
     "NodeConfig",
     "NodeLoader",
-    "NodeValidationError",
 ]
```

**Rationale**: `NodeValidationError` is not used anywhere in the current runtime codebase (verified by `grep`). Removing the stale re-export unblocks the import chain immediately.

### 6.2 Secondary Fix (Restore Broken Package)

**File**: `autoBMAD/nodes/__init__.py`

```diff
-from nodes.loader import (
+from autoBMAD.nodes.loader import (
     NodeAgentConfig,
     NodeConfig,
     ...
 )
```

Or better, use relative imports:

```diff
-from nodes.loader import (
+from .loader import (
     NodeAgentConfig,
     ...
 )
```

### 6.3 Tertiary Fix (Restore Missing Symbols)

**File**: `autoBMAD/nodes/loader.py`

Add the missing dataclasses that production code still expects:

```python
class NodeValidationError(Exception):
    """Raised when node configuration validation fails."""
    pass


@dataclass
class NodeFilePermissions:
    allowed_read_dirs: list[str] = field(default_factory=list)
    allowed_write_dirs: list[str] = field(default_factory=list)


@dataclass
class NodeSearchPermissions:
    search_dirs: list[str] = field(default_factory=list)


@dataclass
class NodeToolPermissions:
    allowed_builtin_tools: list[str] = field(default_factory=list)
    file_permissions: NodeFilePermissions = field(default_factory=NodeFilePermissions)
    search_permissions: NodeSearchPermissions = field(default_factory=NodeSearchPermissions)


@dataclass
class NodeSharedContextConfig:
    update_whitelist: list[str] = field(default_factory=list)
    version_controlled: bool = False


@dataclass
class NodeRuntimeConfig:
    timeout_seconds: int = 300
    max_iterations: int = 3


@dataclass
class NodeSkillsConfig:
    sdk_native: bool = False
    whitelist: list[str] = field(default_factory=list)
    quick_reference_enabled: bool = False
    quick_reference_include_descriptions: bool = False
```

> **Note**: The exact field definitions should be cross-referenced with the deleted `autoBMAD/docuswarm/nodes/loader.py` (commit `3c1f84f` or earlier) to ensure compatibility with existing `node.yaml` configurations.

### 6.4 Process Fix (Prevent Recurrence)

1. **Pre-commit hook**: Run `tools/import_fracture_detector.py` before allowing commits that delete or move modules.
2. **CI gate**: Add an import-fracture check to the test pipeline.
3. **Refactoring checklist**: Any commit that deletes a module must include a grep-driven audit of all remaining imports.

---

## 7. Appendix

### A. Git Commands for Verification

```bash
# Verify the deleted module
$ git show 6a4c3ca --name-status | grep loader
D    autoBMAD/docuswarm/nodes/loader.py
M    autoBMAD/docuswarm/nodes/__init__.py

# Verify NodeValidationError existed in the deleted module
$ git show 3c1f84f:autoBMAD/docuswarm/nodes/loader.py | grep -A2 "class NodeValidationError"
class NodeValidationError(Exception):
    """Raised when node configuration validation fails."""
    pass

# Verify it does NOT exist in the current canonical module
$ grep -n "NodeValidationError" autoBMAD/nodes/loader.py
# (no output)
```

### B. Full Error Traceback (Reproduced)

```python
Traceback (most recent call last):
  File "...", line 1, in <module>
    from autoBMAD.docuswarm.nodes import NodeValidationError
  File ".../autoBMAD/docuswarm/nodes/__init__.py", line 14, in <module>
    from autoBMAD.nodes.loader import NodeConfig, NodeLoader, NodeValidationError
ImportError: cannot import name 'NodeValidationError' from 'autoBMAD.nodes.loader'
```

### C. Tool Output Locations

| Tool | Output Path |
|------|-------------|
| `import_fracture_detector.py` | `docs/research/import-fracture-detector-latest.json` |
| `pipeline_import_tracer.py` | `docs/research/pipeline-import-trace-report.md` |

### D. Cross-Reference to Prior Research

This finding validates and extends the analysis in:

- `docs-doc/research/2026-04-07-nodes-tech-debt-dependency-analysis.md` (TD-001: 双目录 NodeLoader 双轨制)
- `docs-doc/research/2026-04-04-finding-b-compatibility-layer-deep-dive.md` (compatibility layer analysis)

The current fracture is a **direct manifestation** of TD-001: the old `autoBMAD/docuswarm/nodes/loader.py` was deleted without fully migrating its symbols to `autoBMAD/nodes/loader.py`, and the `__init__.py` re-export was only partially updated.
