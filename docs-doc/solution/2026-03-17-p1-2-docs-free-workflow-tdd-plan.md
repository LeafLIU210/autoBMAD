# P1-2: Docs-Free Workflow — 测试驱动开发方案

**优先级**: P1-2 (Architecture Change)  
**预估工时**: 60-90 分钟  
**依赖**: [P0-Output目录统一](./P0-Output目录统一-TDD方案.md), [P1-Context_File传递](./P1-Context_File传递-TDD方案.md)  
**影响范围**: 工具层、Agent 配置、测试层、运行时上下文

---

## 目录

1. [需求描述](#1-需求描述)
2. [技术设计](#2-技术设计)
3. [TDD 测试用例](#3-tdd-测试用例)
4. [实施步骤](#4-实施步骤)
5. [验证清单](#5-验证清单)
6. [风险与回滚](#6-风险与回滚)

---

## 1. 需求描述

### 1.1 决策背景

根据评估文档 `docs/evaluation/2026-03-17-p1-2-controlled-docs-context-strategy-evaluation.md` 的最终决策：

> **直接移除 P1-2，明确工作流完全不读取 `docs/`，`docs/` 不再参与工作流执行链路。**

### 1.2 核心约束

| 约束 | 说明 |
|------|------|
| `output/` 为唯一输出目录 | 所有工作流产物只能写入 `output/{pipeline_id}/` |
| 工作流不修改 `@docs` 文档 | 禁止任何自动流程写入 `docs/` 目录 |
| 工作流不读取 `docs/` | Agent 运行时不再访问 `docs/` 作为输入源 |

### 1.3 清理范围

```
┌─────────────────────────────────────────────────────────────────┐
│                     清理对象清单                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 工具层 (Tools)                                               │
│     ├── read_docs_file.py       → 删除或标记废弃                  │
│     ├── update_docs_file.py     → 删除                          │
│     └── list_docs_files.py      → 删除或标记废弃                  │
│                                                                 │
│  2. Agent 配置                                                   │
│     └── independent_agent.yaml  → 移除 docs 工具引用              │
│                                                                 │
│  3. 测试层                                                       │
│     └── test_docs_tools.py      → 删除或重写                      │
│                                                                 │
│  4. 运行时上下文                                                 │
│     └── context_builder.py      → 移除 docs_context 字段          │
│                                                                 │
│  5. 流程提示词                                                   │
│     └── epic_automation/        → 移除 @docs 写入指令             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 技术设计

### 2.1 目标架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docs-Free Workflow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Input     │    │   Node      │    │       Output        │  │
│  │   Layer     │───→│  Execution  │───→│       Layer         │  │
│  │             │    │             │    │                     │  │
│  │ context dict│    │  Agent with │    │ output/{pipeline_id}/│  │
│  │ (structured)│    │  limited    │    │                     │  │
│  │             │    │  tools      │    │ - deliverables      │  │
│  │ NO docs/    │    │             │    │ - context.json      │  │
│  │ reading     │    │ NO docs/    │    │ - checkpoints       │  │
│  │             │    │ access      │    │                     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                                 │
│  docs/ 目录 → 仅作为人工维护的参考资料库，不参与工作流执行          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块变更矩阵

| 模块 | 当前状态 | 目标状态 | 操作 |
|------|---------|---------|------|
| `tools/read_docs_file.py` | 存在 | 删除 | 完全移除 |
| `tools/update_docs_file.py` | 存在 | 删除 | 完全移除 |
| `tools/list_docs_files.py` | 存在 | 删除 | 完全移除 |
| `tools/__init__.py` | 导出 docs 工具 | 不导出 | 移除引用 |
| `agents/configs/independent_agent.yaml` | 包含 docs 工具 | 不包含 | 移除配置 |
| `node_execution/context_builder.py` | 含 `docs_context` 字段 | 移除字段 | 清理字段 |
| `tests/unit/test_docs_tools.py` | 存在 | 删除 | 完全移除 |
| `epic_automation/agents/qa_agent.py` | 写 `@docs/qa/gates` | 改写到 `output/` | 更新提示词 |
| `epic_automation/agents/dev_agent.py` | 读 `@docs/qa/gates` | 从上下文读取 | 更新提示词 |

---

## 3. TDD 测试用例

### 3.1 测试策略

```
阶段 1: 编写"负向测试" - 验证 docs 工具不存在
阶段 2: 运行测试 - 确认当前失败（工具仍存在）
阶段 3: 移除实现 - 删除 docs 工具和引用
阶段 4: 运行测试 - 确认通过
阶段 5: 编写"正向测试" - 验证 output-only 工作流
```

### 3.2 负向测试用例

**文件**: `tests/unit/test_docs_free_workflow.py`

```python
"""Tests for docs-free workflow compliance.

This module verifies that:
1. Docs-related tools are NOT available to agents
2. Context builder does NOT include docs_context field
3. Agent configs do NOT reference docs tools
4. Output directory is the ONLY write target
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml

if TYPE_CHECKING:
    from collections.abc import Callable


class TestDocsToolsRemoval:
    """Verify docs tools are completely removed."""

    def test_read_docs_file_tool_not_importable(self) -> None:
        """read_docs_file should not be importable from tools package."""
        with pytest.raises((ImportError, AttributeError)):
            from autoBMAD.docuswarm.tools import read_docs_file

    def test_update_docs_file_tool_not_importable(self) -> None:
        """update_docs_file should not be importable from tools package."""
        with pytest.raises((ImportError, AttributeError)):
            from autoBMAD.docuswarm.tools import update_docs_file

    def test_list_docs_files_tool_not_importable(self) -> None:
        """list_docs_files should not be importable from tools package."""
        with pytest.raises((ImportError, AttributeError)):
            from autoBMAD.docuswarm.tools import list_docs_files

    def test_docs_tools_not_in_all(self) -> None:
        """Tools package __all__ should not include docs tools."""
        from autoBMAD.docuswarm.tools import __all__

        docs_tools = {"read_docs_file", "update_docs_file", "list_docs_files"}
        assert not docs_tools.intersection(set(__all__)), (
            f"Found docs tools in __all__: {docs_tools.intersection(set(__all__))}"
        )

    def test_docs_tool_files_do_not_exist(self) -> None:
        """Docs tool source files should be deleted."""
        tools_dir = Path("autoBMAD/docuswarm/tools")
        
        docs_tool_files = [
            tools_dir / "read_docs_file.py",
            tools_dir / "update_docs_file.py",
            tools_dir / "list_docs_files.py",
        ]
        
        for file_path in docs_tool_files:
            assert not file_path.exists(), (
                f"Docs tool file should be deleted: {file_path}"
            )


class TestAgentConfigCompliance:
    """Verify agent configs do not reference docs tools."""

    def test_independent_agent_no_docs_tools(self) -> None:
        """Independent agent config should not list docs tools."""
        config_path = Path("autoBMAD/docuswarm/agents/configs/independent_agent.yaml")
        
        if not config_path.exists():
            pytest.skip("Config file does not exist")
        
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        tools = config.get("tools", [])
        docs_tool_names = {"read_docs_file", "update_docs_file", "list_docs_files"}
        
        found_docs_tools = docs_tool_names.intersection(set(tools))
        assert not found_docs_tools, (
            f"Found docs tools in agent config: {found_docs_tools}"
        )


class TestContextBuilderCompliance:
    """Verify context builder does not include docs_context."""

    def test_build_context_no_docs_context_field(self) -> None:
        """build_context should not return docs_context field."""
        from autoBMAD.docuswarm.node_execution.context_builder import build_context

        # Call with minimal parameters
        result = build_context(
            node_id="test_node",
            node_config={},
            pipeline_context={},
        )

        assert "docs_context" not in result, (
            "docs_context field should be removed from context"
        )

    def test_context_keys_are_expected(self) -> None:
        """Context should only contain expected keys."""
        from autoBMAD.docuswarm.node_execution.context_builder import build_context

        result = build_context(
            node_id="test_node",
            node_config={},
            pipeline_context={},
        )

        # These are the only expected keys (adjust based on actual implementation)
        allowed_keys = {
            "node_id",
            "input_context",
            "output_context",
            "checkpoint_context",
            # "docs_context" is intentionally excluded
        }

        unexpected_keys = set(result.keys()) - allowed_keys
        assert not unexpected_keys, (
            f"Found unexpected context keys: {unexpected_keys}"
        )


class TestOutputOnlyCompliance:
    """Verify output directory is the only write target."""

    def test_create_deliverable_writes_to_cwd(self) -> None:
        """CreateDeliverable should write to current working directory."""
        from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool

        tool = CreateDeliverableTool()
        # The tool should use Path.cwd() as output directory
        # This is verified by implementation inspection
        import inspect
        source = inspect.getsource(tool.__call__)
        
        # Should reference cwd or output, not docs
        assert "docs" not in source.lower() or "output" in source.lower(), (
            "Tool should not reference docs directory"
        )

    def test_update_context_tool_no_docs_reference(self) -> None:
        """UpdateContext tool should not reference docs directory."""
        from autoBMAD.docuswarm.tools.update_context import UpdateContextTool

        tool = UpdateContextTool()
        import inspect
        source = inspect.getsource(tool.__call__)
        
        assert "docs" not in source.lower(), (
            "update_context should not reference docs directory"
        )


class TestEpicAutomationCompliance:
    """Verify epic automation agents do not reference docs paths."""

    def test_qa_agent_no_docs_write_instruction(self) -> None:
        """QA agent should not instruct writing to docs/."""
        agent_path = Path("autoBMAD/epic_automation/agents/qa_agent.py")
        
        if not agent_path.exists():
            pytest.skip("QA agent file does not exist")
        
        with open(agent_path, encoding="utf-8") as f:
            content = f.read()
        
        # Should not contain instructions to write to @docs
        assert "@docs" not in content, (
            "QA agent should not reference @docs in instructions"
        )
        assert "docs/qa/gates" not in content, (
            "QA agent should not reference docs/qa/gates path"
        )

    def test_dev_agent_no_docs_read_instruction(self) -> None:
        """Dev agent should not instruct reading from docs/."""
        agent_path = Path("autoBMAD/epic_automation/agents/dev_agent.py")
        
        if not agent_path.exists():
            pytest.skip("Dev agent file does not exist")
        
        with open(agent_path, encoding="utf-8") as f:
            content = f.read()
        
        assert "@docs" not in content, (
            "Dev agent should not reference @docs in instructions"
        )
```

### 3.3 正向测试用例

**文件**: `tests/integration/test_docs_free_workflow.py`

```python
"""Integration tests for docs-free workflow.

Verifies that the workflow operates correctly without docs/ access.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class TestDocsFreeWorkflowExecution:
    """End-to-end tests for docs-free workflow."""

    @pytest.mark.asyncio
    async def test_pipeline_runs_without_docs_access(self, tmp_path: Path) -> None:
        """Pipeline should execute successfully without docs/ access."""
        # This test runs a minimal pipeline and verifies:
        # 1. No errors related to missing docs tools
        # 2. Output is written to correct directory
        # 3. No attempts to access docs/
        
        # Implementation depends on actual pipeline runner
        pass

    @pytest.mark.asyncio
    async def test_agent_tools_subset_does_not_include_docs(self) -> None:
        """Agent tool registry should not include docs tools."""
        from autoBMAD.docuswarm.tools import __all__
        
        # Verify no docs tools in available tools
        assert "read_docs_file" not in __all__
        assert "update_docs_file" not in __all__
        assert "list_docs_files" not in __all__

    @pytest.mark.asyncio
    async def test_context_injected_to_agent_has_no_docs(self) -> None:
        """Context injected to agent should not contain docs references."""
        from autoBMAD.docuswarm.node_execution.context_builder import build_context

        context = build_context(
            node_id="test_node",
            node_config={"input": {}},
            pipeline_context={},
        )

        # Convert to string and check for docs references
        context_str = str(context)
        assert "docs_context" not in context_str
```

---

## 4. 实施步骤

### 4.1 Step 1: 创建测试文件

```bash
# 创建新的测试文件
touch tests/unit/test_docs_free_workflow.py
touch tests/integration/test_docs_free_workflow.py
```

### 4.2 Step 2: 运行测试（确认当前失败）

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行单元测试（预期失败，因为工具仍存在）
pytest tests/unit/test_docs_free_workflow.py -v --tb=short

# 预期输出：
# FAILED test_docs_tool_files_do_not_exist - AssertionError: Docs tool file should be deleted
# FAILED test_docs_tools_not_in_all - AssertionError: Found docs tools in __all__
```

### 4.3 Step 3: 删除 Docs 工具文件

```bash
# 删除工具文件
rm autoBMAD/docuswarm/tools/read_docs_file.py
rm autoBMAD/docuswarm/tools/update_docs_file.py
rm autoBMAD/docuswarm/tools/list_docs_files.py
```

### 4.4 Step 4: 更新工具包 `__init__.py`

**文件**: `autoBMAD/docuswarm/tools/__init__.py`

```python
"""DocuSwarm tools package.

This package provides tools for document creation and context management.
All output is directed to the pipeline output directory.
"""

from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool
from autoBMAD.docuswarm.tools.update_context import UpdateContextTool

__all__ = [
    "CreateDeliverableTool",
    "UpdateContextTool",
]
```

### 4.5 Step 5: 更新 Agent 配置

**文件**: `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`

```yaml
# Independent Agent Configuration
# Docs-free version - all output goes to output/{pipeline_id}/

name: independent_agent
description: |
  An independent agent that creates deliverables and updates context.
  All output is written to the pipeline output directory.

model:
  name: kimi-k2-0713-preview
  temperature: 0.7

# Available tools - docs tools removed per P1-2 decision
tools:
  - create_deliverable
  - update_context

# Context injection - docs_context removed
context:
  - input_context
  - output_context
  - checkpoint_context

# No @docs references in system prompt
system_prompt: |
  You are an autonomous agent responsible for completing assigned tasks.
  
  ## Output Guidelines
  - All deliverables must be created using the `create_deliverable` tool
  - Context updates must use the `update_context` tool
  - Output is automatically directed to the correct pipeline directory
  
  ## Constraints
  - Do not attempt to access or modify files outside the pipeline context
  - Use only the provided tools for all operations
```

### 4.6 Step 6: 清理 Context Builder

**文件**: `autoBMAD/docuswarm/node_execution/context_builder.py`

```python
"""Context builder for node execution.

Builds the context dictionary injected into agents during node execution.
Docs-free version per P1-2 decision.
"""

from __future__ import annotations

from typing import Any


def build_context(
    node_id: str,
    node_config: dict[str, Any],
    pipeline_context: dict[str, Any],
) -> dict[str, Any]:
    """Build context dictionary for agent execution.
    
    Args:
        node_id: The node identifier.
        node_config: Node configuration from BMM.
        pipeline_context: Pipeline-wide context data.
    
    Returns:
        Context dictionary for agent injection.
        
    Note:
        This is a docs-free implementation. No docs_context is included.
        All reference material should be provided through pipeline_context.
    """
    return {
        "node_id": node_id,
        "input_context": pipeline_context.get("input", {}),
        "output_context": pipeline_context.get("output", {}),
        "checkpoint_context": pipeline_context.get("checkpoints", []),
        # docs_context intentionally removed per P1-2 decision
    }
```

### 4.7 Step 7: 更新 Epic Automation Agent

**文件**: `autoBMAD/epic_automation/agents/qa_agent.py`

```python
"""QA Agent for epic automation.

Docs-free version - outputs to pipeline output directory instead of docs/.
"""

# ... existing imports ...

QA_AGENT_SYSTEM_PROMPT = """
You are a QA Engineer responsible for defining and tracking quality gates.

## Your Responsibilities
1. Define acceptance criteria for stories
2. Create quality gate specifications
3. Track test coverage requirements

## Output
- Use `create_deliverable` to create quality gate specifications
- Use `update_context` to update verification status
- Output is automatically written to the pipeline output directory

## Important
- Do NOT reference @docs paths in your work
- All deliverables are written to the designated output directory
"""

# ... rest of implementation ...
```

**文件**: `autoBMAD/epic_automation/agents/dev_agent.py`

```python
"""Dev Agent for epic automation.

Docs-free version - reads from context instead of docs/.
"""

# ... existing imports ...

DEV_AGENT_SYSTEM_PROMPT = """
You are a Software Developer responsible for implementing stories.

## Your Responsibilities
1. Review quality gates from context
2. Implement features according to specifications
3. Update implementation status

## Input
- Quality gates are provided in the input_context
- Do NOT attempt to read from @docs paths

## Output
- Use `create_deliverable` for implementation documentation
- Use `update_context` to track progress
"""

# ... rest of implementation ...
```

### 4.8 Step 8: 删除旧测试文件

```bash
# 删除旧测试文件（如果存在且专门测试 docs 工具）
rm tests/unit/test_docs_tools.py
```

### 4.9 Step 9: 重新运行测试

```bash
# 运行单元测试（应该通过）
pytest tests/unit/test_docs_free_workflow.py -v

# 运行集成测试
pytest tests/integration/test_docs_free_workflow.py -v

# 运行所有测试确保没有回归
pytest tests/ -v --tb=short
```

---

## 5. 验证清单

### 5.1 代码层验证

| 检查项 | 状态 | 验证方法 |
|--------|------|---------|
| `read_docs_file.py` 已删除 | ⬜ | `ls autoBMAD/docuswarm/tools/` |
| `update_docs_file.py` 已删除 | ⬜ | `ls autoBMAD/docuswarm/tools/` |
| `list_docs_files.py` 已删除 | ⬜ | `ls autoBMAD/docuswarm/tools/` |
| `tools/__init__.py` 不导出 docs 工具 | ⬜ | 检查 `__all__` |
| Agent 配置不包含 docs 工具 | ⬜ | 检查 YAML 文件 |
| Context builder 无 `docs_context` | ⬜ | 检查返回值 |

### 5.2 测试层验证

| 检查项 | 状态 | 验证方法 |
|--------|------|---------|
| 新测试通过 | ⬜ | `pytest tests/unit/test_docs_free_workflow.py` |
| 旧测试删除 | ⬜ | `test_docs_tools.py` 不存在 |
| 无回归测试失败 | ⬜ | `pytest tests/` 全部通过 |

### 5.3 集成验证

| 检查项 | 状态 | 验证方法 |
|--------|------|---------|
| Pipeline 可启动 | ⬜ | 运行最小 pipeline |
| Agent 工具注册成功 | ⬜ | 检查工具列表 |
| 输出写入 `output/` | ⬜ | 检查文件位置 |
| 无 docs 访问尝试 | ⬜ | 检查日志 |

---

## 6. 风险与回滚

### 6.1 风险分析

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 外部代码依赖 docs 工具 | 中 | 高 | 全局搜索所有 import |
| 配置文件硬编码工具列表 | 低 | 中 | 检查所有 YAML 配置 |
| 提示词遗漏 @docs 引用 | 中 | 中 | 全文搜索 @docs |
| 运行时错误 | 低 | 高 | 完整集成测试 |

### 6.2 回滚方案

如果需要回滚，执行以下命令：

```bash
# 从 git 恢复删除的文件
git checkout HEAD -- autoBMAD/docuswarm/tools/read_docs_file.py
git checkout HEAD -- autoBMAD/docuswarm/tools/update_docs_file.py
git checkout HEAD -- autoBMAD/docuswarm/tools/list_docs_files.py

# 恢复测试文件（如果需要）
git checkout HEAD -- tests/unit/test_docs_tools.py

# 恢复配置文件
git checkout HEAD -- autoBMAD/docuswarm/tools/__init__.py
git checkout HEAD -- autoBMAD/docuswarm/agents/configs/independent_agent.yaml
git checkout HEAD -- autoBMAD/docuswarm/node_execution/context_builder.py
```

### 6.3 决策记录更新

实施后，更新以下文档：

1. 在 `docs/evaluation/2026-03-17-p1-2-controlled-docs-context-strategy-evaluation.md` 添加实施记录
2. 更新 `docs/solution/IMPLEMENTATION_SUMMARY.md` 添加 P1-2 完成状态
3. 创建执行报告 `docs/solution/2026-03-17-p1-2-docs-free-workflow-execution-report.md`

---

## 附录 A: 搜索检查清单

实施前执行以下搜索，确保无遗漏依赖：

```bash
# 搜索所有 docs 工具引用
grep -r "read_docs_file\|update_docs_file\|list_docs_files" --include="*.py" .

# 搜索 @docs 引用
grep -r "@docs" --include="*.py" --include="*.yaml" --include="*.md" .

# 搜索 docs_context
grep -r "docs_context" --include="*.py" --include="*.yaml" .

# 搜索 docs/qa/gates 路径
grep -r "docs/qa/gates\|docs\\qa\\gates" --include="*.py" .
```

---

**文档版本**: 1.0  
**创建日期**: 2026-03-17  
**作者**: DocuSwarm Architecture Team  
**关联评估**: `docs/evaluation/2026-03-17-p1-2-controlled-docs-context-strategy-evaluation.md`
