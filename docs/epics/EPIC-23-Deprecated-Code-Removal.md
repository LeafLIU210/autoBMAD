# Epic 23: 废弃代码移除与功能精简

**Epic ID**: EPIC-23  
**Version**: 1.0  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 1-2 Days

---

## 1. Epic Overview

### 1.1 Summary

移除废弃代码和无用功能，修复 _bmad 外部依赖违规，实现代码库的精简和清理。

### 1.2 Business Value

- **代码精简**: 移除不再使用的数据类和函数
- **依赖修复**: 消除 _bmad 外部引用违规
- **维护简化**: 减少代码复杂度，提高可维护性

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 废弃函数移除 | _create_default_node_executor, create_enhanced_node_executor 已移除 |
| 废弃数据类移除 | NodeQuestionConfig, NodeQuestionsConfig, NodeDependenciesConfig 已移除 |
| dual_agent 清理 | create_node_executor, _execute_node, _get_config 已移除 |
| 外部依赖清理 | autoBMAD 目录中无 _bmad 引用 |
| 功能完整性 | 移除后系统仍能正常运行 |

### 1.4 Dependencies

- **Prerequisites**: EPIC-21, EPIC-22 完成 (结构稳定后才能移除)
- **Blocks**: EPIC-24 (集成测试)

---

## 2. Stories

### Story 23.1: 移除 loader.py 废弃数据类

As a developer,
I want to remove deprecated dataclasses from loader.py,
So that the codebase is cleaner and only contains used structures.

**Acceptance Criteria:**

**Given** the loader.py file contains NodeQuestionConfig, NodeQuestionsConfig, NodeDependenciesConfig
**When** I remove these three dataclass definitions
**And** remove any imports or references to them
**Then** the file no longer contains these class definitions
**And** basedpyright reports no type errors

**Given** the NodeConfig dataclass
**When** I remove the questions and dependencies fields
**Then** NodeConfig can still be instantiated with remaining fields
**And** no code references the removed fields

---

### Story 23.2: 移除 graph.py 废弃函数

As a developer,
I want to remove deprecated functions from graph.py,
So that only current executor logic remains.

**Acceptance Criteria:**

**Given** the graph.py file contains _create_default_node_executor
**When** I remove the entire function definition (lines ~56-159)
**Then** the function no longer exists in the module
**And** no other code references this function

**Given** the graph.py file contains create_enhanced_node_executor
**When** I remove the entire function definition (lines ~473-489)
**Then** the function no longer exists in the module
**And** no other code references this function

**Given** the create_pipeline_graph function
**When** I change session_manager parameter from optional to required
**Then** the function signature shows session_manager: KimiSessionManager (no default)
**And** the function no longer has fallback logic for None session_manager

---

### Story 23.3: 移除 dual_agent.py 冗余函数

As a developer,
I want to remove redundant functions from dual_agent.py,
So that it only contains the DualAgentNode class.

**Acceptance Criteria:**

**Given** the dual_agent.py file contains create_node_executor (lines ~836-868)
**When** I remove the entire function definition
**Then** the function no longer exists in the module

**Given** the dual_agent.py file contains _execute_node (lines ~871-968)
**When** I remove the entire function definition
**Then** the function no longer exists in the module

**Given** the dual_agent.py file contains _get_config (lines ~971-991)
**When** I remove the entire function definition
**Then** the function no longer exists in the module

**Given** the __all__ export list in dual_agent.py
**When** I remove the deleted function names from __all__
**Then** __all__ only contains existing exports

---

### Story 23.4: 移除 templates 目录

As a developer,
I want to remove the templates directory,
So that _bmad references are eliminated.

**Acceptance Criteria:**

**Given** the autoBMAD/docuswarm/templates/ directory exists
**When** I delete the entire directory and its contents
**Then** the directory no longer exists
**And** no code references files in this directory

**Given** the templates directory contained files with _bmad references
**When** I verify _bmad references in autoBMAD
**Then** no _bmad references remain in .py, .yaml, .json, or .md files

---

### Story 23.5: 更新 node.yaml 移除废弃字段

As a developer,
I want to remove deprecated fields from all node.yaml files,
So that configurations only contain valid fields.

**Acceptance Criteria:**

**Given** the five node.yaml files (analyst, pm, ux, architect, po)
**When** I remove the description field from each
**Then** the files no longer contain this field
**And** NodeLoader still loads them successfully

**Given** the five node.yaml files
**When** I remove the questions block from each
**Then** the files no longer contain questions configuration
**And** no errors occur during loading

**Given** the five node.yaml files
**When** I remove the dependencies block from each
**Then** the files no longer contain dependencies configuration
**And** pipeline graph construction still works

---

### Story 23.6: 编写移除验证测试

As a developer,
I want to write tests to verify all deprecated code is removed,
So that we can confirm the cleanup is complete.

**Acceptance Criteria:**

**Given** the test file tests/pipeline/test_deprecated_functions_removed.py
**When** I run the tests
**Then** they verify _create_default_node_executor is removed
**And** they verify create_enhanced_node_executor is removed
**And** they verify session_manager is now required

**Given** the test file tests/nodes/test_dataclasses_removed.py
**When** I run the tests
**Then** they verify NodeQuestionConfig is removed
**And** they verify NodeQuestionsConfig is removed
**And** they verify NodeDependenciesConfig is removed

**Given** the test file tests/nodes/test_dual_agent_cleanup.py
**When** I run the tests
**Then** they verify create_node_executor is removed from dual_agent
**And** they verify _execute_node is removed
**And** they verify _get_config is removed

**Given** the test file tests/test_no_bmad_references.py
**When** I run the tests
**Then** they scan autoBMAD for _bmad references
**And** they verify templates directory is removed

**Given** the verify_removal.py script
**When** I run it
**Then** it reports all deprecated code successfully removed

---

## 3. Implementation Notes

### 3.1 移除清单

| 文件 | 函数/代码 | 行号范围 | 移除理由 |
|------|----------|---------|---------|
| `pipeline/graph.py` | `_create_default_node_executor()` | ~56-159 | 已标记 @deprecated，产生空交付物 |
| `pipeline/graph.py` | `create_enhanced_node_executor()` | ~473-489 | 调用 deprecated 函数 |
| `nodes/loader.py` | `NodeQuestionConfig` dataclass | - | 自动化不使用 |
| `nodes/loader.py` | `NodeQuestionsConfig` dataclass | - | 自动化不使用 |
| `nodes/loader.py` | `NodeDependenciesConfig` dataclass | - | 由 graph.py 边定义管理 |
| `nodes/dual_agent.py` | `create_node_executor()` | ~836-868 | 无外部调用，与 executor.py 重复 |
| `nodes/dual_agent.py` | `_execute_node()` | ~871-968 | 无外部调用 |
| `nodes/dual_agent.py` | `_get_config()` | ~971-991 | 与 executor.py 重复 |

### 3.2 _bmad 引用违规修复

| 文件 | 违规内容 | 行号 | 修复方案 |
|------|---------|------|---------|
| `templates/analyst_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 62 | 整体移除 templates/ 目录 |
| `templates/pm_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 54 | 整体移除 templates/ 目录 |
| `templates/ux_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 67 | 整体移除 templates/ 目录 |
| `templates/architect_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 59 | 整体移除 templates/ 目录 |
| `templates/po_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 66 | 整体移除 templates/ 目录 |

### 3.3 验证脚本

```python
# scripts/verify_removal.py
"""Script to verify all deprecated code is removed."""

import sys
from pathlib import Path


def check_file_does_not_contain(file_path: Path, patterns: list[str]) -> list[str]:
    """Check that file doesn't contain any of the patterns."""
    violations = []
    
    if not file_path.exists():
        return [f"File not found: {file_path}"]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for pattern in patterns:
                if pattern in content:
                    violations.append(f"{file_path}: contains '{pattern}'")
    except Exception as e:
        violations.append(f"{file_path}: error reading - {e}")
    
    return violations


def main():
    """Run all removal verifications."""
    violations = []
    
    base_dir = Path("autoBMAD/docuswarm")
    
    # Check loader.py doesn't have deprecated classes
    loader_file = base_dir / "nodes" / "loader.py"
    violations.extend(check_file_does_not_contain(loader_file, [
        "class NodeQuestionConfig",
        "class NodeQuestionsConfig", 
        "class NodeDependenciesConfig",
    ]))
    
    # Check graph.py doesn't have deprecated functions
    graph_file = base_dir / "pipeline" / "graph.py"
    violations.extend(check_file_does_not_contain(graph_file, [
        "def _create_default_node_executor",
        "def create_enhanced_node_executor",
    ]))
    
    # Check templates directory doesn't exist
    templates_dir = base_dir / "templates"
    if templates_dir.exists():
        violations.append(f"{templates_dir}: directory should be removed")
    
    # Check for _bmad references
    for py_file in base_dir.rglob("*.py"):
        violations.extend(check_file_does_not_contain(py_file, ["_bmad"]))
    
    for yaml_file in base_dir.rglob("*.yaml"):
        violations.extend(check_file_does_not_contain(yaml_file, ["_bmad"]))
    
    if violations:
        print("❌ Removal verification FAILED:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("✅ All deprecated code successfully removed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 移除后代码无法运行 | 中 | 高 | 先完成 EPIC-21 和 EPIC-22，确保结构稳定 |
| 外部引用未清理完 | 中 | 中 | 扫描脚本验证，手动复查 |
| 功能完整性破坏 | 低 | 高 | 运行功能完整性测试 |

---

## 5. 回滚计划

如果移除后出现问题，按以下顺序回滚：

1. **恢复 node.yaml 中的字段** (如果验证逻辑依赖)
2. **恢复 dual_agent.py 中的函数** (如果需要)
3. **恢复 graph.py 中的函数** (最后手段)

所有更改应通过 git 管理，确保可以回滚。

---

## 6. 验证命令

```bash
# 运行移除验证测试
pytest tests/pipeline/test_deprecated_functions_removed.py -v
pytest tests/nodes/test_dataclasses_removed.py -v
pytest tests/nodes/test_dual_agent_cleanup.py -v
pytest tests/test_no_bmad_references.py -v

# 运行验证脚本
python scripts/verify_removal.py

# 手动扫描 _bmad 引用 (应该返回空)
grep -r "_bmad" autoBMAD/ --include="*.py" --include="*.yaml" --include="*.json"

# 类型检查
basedpyright autoBMAD/docuswarm/nodes/loader.py
basedpyright autoBMAD/docuswarm/pipeline/graph.py
basedpyright autoBMAD/docuswarm/nodes/dual_agent.py
```

---

## 7. 相关文档

- [TDD-BMM-03: 废弃代码移除与功能精简](../solution/TDD-BMM-03-Deprecated-Code-Removal.md)
- [EPIC-21: NodeLoader 配置加载系统重构](./EPIC-21-NodeLoader-Config-Refactor.md)
- [EPIC-22: Persona 角色上下文与 System Prompt 重构](./EPIC-22-Persona-SystemPrompt-Refactor.md)
- [EPIC-24: 双代理流程集成与端到端测试](./EPIC-24-DualAgent-Integration-E2E.md)
