# TDD-BMM-03: 废弃代码移除与功能精简

## 文档信息

| 属性 | 值 |
|------|-----|
| **方案编号** | TDD-BMM-03 |
| **关联研究** | Part 4 (功能精简与移除方案) |
| **优先级** | P0 - Critical |
| **状态** | 待实施 |

---

## 1. 目标

移除废弃代码和无用功能，修复 `_bmad` 外部依赖违规：
1. 移除废弃函数 (`_create_default_node_executor`, `create_enhanced_node_executor`)
2. 移除无用配置数据类 (`NodeQuestionConfig`, `NodeQuestionsConfig`, `NodeDependenciesConfig`)
3. 修复/移除 `templates/*.yaml` 中的 `_bmad` 引用违规
4. 移除 `dual_agent.py` 中的冗余 executor 函数
5. 确保 `session_manager` 成为必需参数

---

## 2. 移除清单

### 2.1 P0-Critical: 废弃函数移除

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

### 2.2 P0-Critical: `_bmad` 引用违规修复

| 文件 | 违规内容 | 行号 | 修复方案 |
|------|---------|------|---------|
| `templates/analyst_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 62 | 整体移除 templates/ 目录 |
| `templates/pm_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 54 | 整体移除 templates/ 目录 |
| `templates/ux_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 67 | 整体移除 templates/ 目录 |
| `templates/architect_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 59 | 整体移除 templates/ 目录 |
| `templates/po_templates.yaml` | `style_guide: "_bmad/_memory/..."` | 66 | 整体移除 templates/ 目录 |

---

## 3. 测试先行的移除计划

### Phase 1: 废弃函数移除测试

#### Test 1.1: 验证废弃函数不存在

```python
# tests/pipeline/test_deprecated_functions_removed.py
"""Tests to verify deprecated functions are removed."""

import pytest


class TestDeprecatedFunctionsRemoved:
    """Verify deprecated functions no longer exist."""

    def test_create_default_node_executor_removed(self):
        """Verify _create_default_node_executor is removed from graph.py."""
        from autoBMAD.docuswarm.pipeline import graph
        
        assert not hasattr(graph, '_create_default_node_executor'), \
            "_create_default_node_executor should be removed"

    def test_create_enhanced_node_executor_removed(self):
        """Verify create_enhanced_node_executor is removed from graph.py."""
        from autoBMAD.docuswarm.pipeline import graph
        
        assert not hasattr(graph, 'create_enhanced_node_executor'), \
            "create_enhanced_node_executor should be removed"

    def test_session_manager_is_required(self):
        """Verify session_manager is now a required parameter."""
        from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
        import inspect
        
        sig = inspect.signature(create_pipeline_graph)
        params = list(sig.parameters.keys())
        
        # session_manager should not have default value
        session_param = sig.parameters.get('session_manager')
        assert session_param is not None
        assert session_param.default is inspect.Parameter.empty, \
            "session_manager should be required (no default)"
```

#### Test 1.2: 数据类移除测试

```python
# tests/nodes/test_dataclasses_removed.py
"""Tests to verify deprecated dataclasses are removed."""

import pytest


class TestDataclassesRemoved:
    """Verify deprecated dataclasses no longer exist."""

    def test_node_question_config_removed(self):
        """Verify NodeQuestionConfig is removed."""
        from autoBMAD.docuswarm.nodes import loader
        
        assert not hasattr(loader, 'NodeQuestionConfig'), \
            "NodeQuestionConfig should be removed"

    def test_node_questions_config_removed(self):
        """Verify NodeQuestionsConfig is removed."""
        from autoBMAD.docuswarm.nodes import loader
        
        assert not hasattr(loader, 'NodeQuestionsConfig'), \
            "NodeQuestionsConfig should be removed"

    def test_node_dependencies_config_removed(self):
        """Verify NodeDependenciesConfig is removed."""
        from autoBMAD.docuswarm.nodes import loader
        
        assert not hasattr(loader, 'NodeDependenciesConfig'), \
            "NodeDependenciesConfig should be removed"
```

#### Test 1.3: dual_agent.py 冗余函数移除测试

```python
# tests/nodes/test_dual_agent_cleanup.py
"""Tests to verify dual_agent.py cleanup."""

import pytest


class TestDualAgentCleanup:
    """Verify redundant functions removed from dual_agent.py."""

    def test_create_node_executor_removed(self):
        """Verify create_node_executor removed from dual_agent.py."""
        from autoBMAD.docuswarm.nodes import dual_agent
        
        assert not hasattr(dual_agent, 'create_node_executor'), \
            "create_node_executor should be removed from dual_agent"

    def test_execute_node_private_removed(self):
        """Verify _execute_node (dual_agent version) is removed."""
        from autoBMAD.docuswarm.nodes import dual_agent
        
        # Should only have execute_node from executor.py
        # The dual_agent version should be removed
        assert not hasattr(dual_agent, '_execute_node'), \
            "_execute_node should be removed from dual_agent"

    def test_get_config_removed(self):
        """Verify _get_config removed from dual_agent.py."""
        from autoBMAD.docuswarm.nodes import dual_agent
        
        assert not hasattr(dual_agent, '_get_config'), \
            "_get_config should be removed from dual_agent"

    def test_all_exports_clean(self):
        """Verify __all__ doesn't contain removed functions."""
        from autoBMAD.docuswarm.nodes.dual_agent import __all__
        
        assert 'create_node_executor' not in __all__, \
            "create_node_executor should not be in __all__"
```

### Phase 2: 外部依赖违规修复测试

#### Test 2.1: `_bmad` 引用扫描测试

```python
# tests/test_no_bmad_references.py
"""Tests to verify no _bmad references in autoBMAD."""

import pytest
import os
from pathlib import Path


class TestNoBmadReferences:
    """Verify no _bmad references in autoBMAD codebase."""

    EXCLUDED_PATTERNS = [
        "__pycache__",
        ".pyc",
        ".pyo",
        ".pyd",
        ".so",
        ".dll",
    ]

    def scan_directory(self, directory: Path) -> list[tuple[Path, int, str]]:
        """Scan directory for _bmad references."""
        violations = []
        
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_PATTERNS]
            
            for file in files:
                if any(file.endswith(ext) for ext in ['.py', '.yaml', '.yml', '.json', '.md']):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if '_bmad' in line.lower():
                                    violations.append((file_path, line_num, line.strip()))
                    except (UnicodeDecodeError, IOError):
                        continue
        
        return violations

    def test_no_bmad_in_autoBMAD(self):
        """Verify no _bmad references in autoBMAD directory."""
        autoBMAD_dir = Path(__file__).parent.parent / "autoBMAD"
        
        if not autoBMAD_dir.exists():
            pytest.skip("autoBMAD directory not found")
        
        violations = self.scan_directory(autoBMAD_dir)
        
        if violations:
            violation_messages = [
                f"{path}:{line}: {content}"
                for path, line, content in violations[:10]  # 最多显示10个
            ]
            pytest.fail(
                f"Found {len(violations)} _bmad references:\n" +
                "\n".join(violation_messages)
            )

    def test_templates_directory_removed(self):
        """Verify templates/ directory is removed."""
        templates_dir = Path(__file__).parent.parent / "autoBMAD" / "docuswarm" / "templates"
        
        assert not templates_dir.exists(), \
            "templates/ directory should be removed (contains _bmad references)"
```

### Phase 3: 功能完整性测试

#### Test 3.1: 移除后功能完整性验证

```python
# tests/integration/test_removal_functionality.py
"""Tests to verify functionality after removal."""

import pytest
from unittest.mock import Mock, AsyncMock


class TestFunctionalityAfterRemoval:
    """Verify system still works after removing deprecated code."""

    @pytest.mark.asyncio
    async def test_pipeline_graph_works_without_deprecated(self):
        """Verify pipeline graph works without deprecated functions."""
        from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
        
        mock_sm = Mock()
        mock_sm.work_dir = Mock()
        
        # Should not raise when session_manager is provided
        graph = create_pipeline_graph(session_manager=mock_sm)
        assert graph is not None

    def test_node_loader_works_without_questions(self):
        """Verify NodeLoader works without questions config."""
        from autoBMAD.docuswarm.nodes.loader import NodeLoader, NodeConfig
        
        # Mock loading a node without questions
        # Should work without errors
        # This is an integration test that requires actual node configs
        pass  # Implement based on actual test setup

    def test_dual_agent_node_still_works(self):
        """Verify DualAgentNode still works after cleanup."""
        from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
        
        # Verify DualAgentNode can still be instantiated
        # This verifies we didn't remove too much
        assert hasattr(DualAgentNode, 'execute')
        assert hasattr(DualAgentNode, '__init__')
```

---

## 4. 实现步骤

### Step 1: 移除 loader.py 中的废弃数据类

```python
# autoBMAD/docuswarm/nodes/loader.py

# 删除以下数据类:
# @dataclass
# class NodeQuestionConfig:
#     ...

# @dataclass  
# class NodeQuestionsConfig:
#     ...

# @dataclass
# class NodeDependenciesConfig:
#     ...

# 从 NodeConfig 中移除:
# questions: NodeQuestionsConfig
# dependencies: NodeDependenciesConfig
# description: str  # 同时移除

# 从 _validate() 中移除相关验证
# 从 _build_node_config() 中移除相关构建逻辑
```

### Step 2: 移除 pipeline/graph.py 中的废弃函数

```python
# autoBMAD/docuswarm/pipeline/graph.py

# 删除 _create_default_node_executor() 函数体
# 删除 create_enhanced_node_executor() 函数体

# 修改 create_pipeline_graph():
def create_pipeline_graph(
    session_manager: KimiSessionManager,  # 移除默认值，改为必需
) -> StateGraph:
    """Create pipeline graph with integrated node executor.
    
    Args:
        session_manager: Required session manager instance.
    """
    # 移除 session_manager=None 时的回退逻辑
    # 直接继续正常流程
```

### Step 3: 移除 dual_agent.py 中的冗余函数

```python
# autoBMAD/docuswarm/nodes/dual_agent.py

# 删除以下函数:
# - create_node_executor() (line ~836-868)
# - _execute_node() (line ~871-968)
# - _get_config() (line ~971-991)

# 更新 __all__:
__all__ = [
    "DualAgentNode",
    # "create_node_executor",  # 移除
    # ... other exports
]
```

### Step 4: 移除 templates/ 目录

```bash
# 删除整个 templates 目录
rm -rf autoBMAD/docuswarm/templates/

# 或者使用 Python
# import shutil
# shutil.rmtree("autoBMAD/docuswarm/templates")
```

### Step 5: 从 node.yaml 文件中移除废弃字段

```yaml
# 所有 nodes/*/node.yaml 文件:
# 移除:
# - description 字段
# - questions 块
# - dependencies 块

# 保留:
# - node_id
# - name
# - sequence
# - agent
# - task (新增)
# - deliverable (扩展)
```

---

## 5. 验证脚本

### 5.1 移除验证脚本

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

## 6. 实施清单

| 步骤 | 任务 | 测试 | 实现 | 状态 |
|------|------|------|------|------|
| 1 | 废弃函数移除测试 | `test_deprecated_functions_removed.py` | - | ⬜ |
| 2 | 数据类移除测试 | `test_dataclasses_removed.py` | - | ⬜ |
| 3 | dual_agent 清理测试 | `test_dual_agent_cleanup.py` | - | ⬜ |
| 4 | _bmad 引用扫描测试 | `test_no_bmad_references.py` | - | ⬜ |
| 5 | 功能完整性测试 | `test_removal_functionality.py` | - | ⬜ |
| 6 | 移除 loader.py 数据类 | - | `loader.py` | ⬜ |
| 7 | 移除 graph.py 废弃函数 | - | `graph.py` | ⬜ |
| 8 | 清理 dual_agent.py | - | `dual_agent.py` | ⬜ |
| 9 | 移除 templates/ 目录 | - | 目录删除 | ⬜ |
| 10 | 更新 node.yaml 文件 | - | `nodes/*/node.yaml` | ⬜ |
| 11 | 运行验证脚本 | `verify_removal.py` | - | ⬜ |

---

## 7. 回滚计划

如果移除后出现问题，按以下顺序回滚：

1. **恢复 node.yaml 中的字段** (如果验证逻辑依赖)
2. **恢复 dual_agent.py 中的函数** (如果需要)
3. **恢复 graph.py 中的函数** (最后手段)

所有更改应通过 git 管理，确保可以回滚。

---

## 8. 验证命令

```bash
# 运行移除验证测试
pytest tests/pipeline/test_deprecated_functions_removed.py -v
pytest tests/nodes/test_dataclasses_removed.py -v
pytest tests/nodes/test_dual_agent_cleanup.py -v
pytest tests/test_no_bmad_references.py -v
pytest tests/integration/test_removal_functionality.py -v

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

**文档结束**
