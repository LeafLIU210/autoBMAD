# Finding B 深度研究报告：兼容层仍然停留在主路径

**研究日期**: 2026-04-04  
**研究范围**: `autoBMAD/docuswarm` 兼容层分布与影响分析  
**报告位置**: `docs/research/2026-04-04-finding-b-compatibility-layer-deep-dive.md`

---

## 执行摘要

本研究基于技术债审查报告 Finding B 进行深度分析。研究发现 DocuSwarm 项目中存在 **23 处明确的兼容层标记**，分布在 **7 个核心文件**中，其中 **10 处为高风险**兼容层，直接影响主执行路径。

核心发现：
- **SessionManager** 和 **DualAgentNode** 是兼容层最集中的两个模块
- 存在 **5 条主要的兼容层调用链**，其中 2 条为高风险
- 兼容层导致明显的**行为分叉**和**理解成本增加**

---

## 一、研究方法

本研究采用以下方法进行深度分析：

1. **静态代码扫描**：使用正则表达式匹配 `deprecated`、`legacy`、`backward compatibility` 等关键词
2. **调用链追踪**：手工分析从旧 API 到新 API 的转换路径
3. **影响范围分析**：识别哪些代码路径经过兼容层
4. **风险评估**：基于主路径接近度和数据转换复杂度进行风险评级

使用的调试工具：
- `tools/debt_research/compatibility_layer_analyzer.py` - 兼容层分布扫描
- `tools/debt_research/compatibility_call_chain_tracer.py` - 调用链追踪

---

## 二、兼容层统计概览

### 2.1 整体分布

| 指标 | 数值 |
|------|------|
| 兼容层标记总数 | 23 处 |
| 涉及文件数 | 7 个 |
| 高风险 (high) | 10 处 |
| 中风险 (medium) | 1 处 |
| 低风险 (low) | 12 处 |

### 2.2 按类别分布

| 类别 | 数量 | 说明 |
|------|------|------|
| alias | 10 | 函数/命令别名 |
| method | 5 | 兼容处理方法 |
| parameter | 5 | 兼容参数 |
| exception | 2 | 兼容异常类 |
| data | 1 | 数据字段兼容 |

### 2.3 按文件分布

| 文件 | 兼容层数量 | 最高风险级别 |
|------|-----------|-------------|
| `llm/session_manager.py` | 5 | high |
| `nodes/dual_agent.py` | 4 | high |
| `tools/*.py` | 6 | low |
| `context/validator.py` | 1 | medium |
| `storage/state_manager.py` | 1 | medium |
| `exceptions.py` | 2 | low |
| `nodes/loader.py` | 1 | low |
| `cli/main.py` | 1 | low |
| `pipeline/orchestrator.py` | 1 | low |
| `context/audit.py` | 1 | low |

---

## 三、高风险兼容层详细分析

### 3.1 SessionManager Legacy 参数链

**位置**: `llm/session_manager.py:70-210`

**问题描述**:

```python
# 入口：__init__ 同时接受新参数和 legacy 参数
def __init__(
    self,
    work_dir: Path,
    agent_file: Path | None = None,
    config: Any | None = None,
    api_key: str | None = None,        # ← deprecated
    base_url: str | None = None,       # ← deprecated  
    node_id: str | None = None,
    allowed_dirs: list[str] | None = None,  # ← deprecated
    file_dirs: list[str] | None = None,
    search_dirs: list[str] | None = None,
    tool_permissions: NodeToolPermissions | None = None,
):
```

**桥接逻辑**:

```python
# 第 99 行：参数回退
self._file_dirs = file_dirs or allowed_dirs or []

# 第 131 行：deprecated 属性暴露
@property
def allowed_dirs(self) -> list[str] | None:
    """Get the allowed directories (deprecated, use file_dirs)."""
    return self._file_dirs
```

**影响分析**:

1. **配置源混乱**：三种配置方式并存
   - 新方式：`config` 对象 + `tool_permissions`
   - 过渡方式：`file_dirs` + `search_dirs`
   - 旧方式：`api_key` + `base_url` + `allowed_dirs`

2. **回退逻辑风险**：`file_dirs or allowed_dirs or []` 的优先级可能导致意外行为

3. **理解成本**：开发者需要了解参数的历史演进才能正确使用

**清理建议**:

```python
# 目标状态：只保留新方式
def __init__(
    self,
    work_dir: Path,
    agent_file: Path | None = None,
    config: Any | None = None,
    node_id: str | None = None,
    tool_permissions: NodeToolPermissions | None = None,
):
```

**预估清理工作量**: 2-3 天（含测试更新）

---

### 3.2 DualAgentNode Legacy 执行链

**位置**: `nodes/dual_agent.py:203-334`

**问题描述**:

```python
# 入口：execute() 保持旧签名
async def execute(
    self,
    subject_context: Any,  # ← legacy 参数
    task: str = "",         # ← legacy 参数
    pipeline_id: str = "",  # ← legacy 参数
) -> NodeResult:
    # ... 第 329 行
    execution_context = self._build_execution_context_from_legacy(...)
    return await self.execute_with_context(execution_context)
```

**桥接方法**:

```python
# 第 203-225 行：legacy 数据规范化
def _normalize_legacy_subject_context(self, subject_context: Any) -> dict[str, Any]:
    """Normalize legacy subject_context payloads into original_context shape."""
    # 处理 dict、str、json 解析等多种情况
    
# 第 227-248 行：从 legacy 构建 execution context
def _build_execution_context_from_legacy(
    self,
    *,
    subject_context: Any,
    task: str = "",
    pipeline_id: str,
    iteration_feedback: dict[str, Any] | None = None,
) -> NodeExecutionContext:
```

**影响分析**:

1. **执行路径分叉**：所有节点调用都有两条路径
   - `execute()` → `_build_execution_context_from_legacy()` → `execute_with_context()`
   - 直接调用 `execute_with_context()`

2. **数据转换风险**：运行时转换可能丢失信息

3. **测试负担**：需要测试两条路径的等价性

**调用关系图**:

```
PipelineOrchestrator
    ↓
DualAgentNode.execute(subject_context, task, pipeline_id)
    ↓
_build_execution_context_from_legacy()
    ↓ (calls)
_normalize_legacy_subject_context()
    ↓
execute_with_context(NodeExecutionContext) ← 新 API 入口
```

**清理建议**:

1. 移除 `execute()` 方法或将其标记为 deprecated
2. 所有调用方直接构建 `NodeExecutionContext`
3. 统一使用 `execute_with_context()`

**预估清理工作量**: 3-5 天（需更新所有调用方）

---

### 3.3 Context Validator 兼容参数

**位置**: `context/validator.py:1412-1429`

**问题描述**:

```python
def validate_execution_context(
    self,
    context: dict[str, Any],
    node_id: str | None = None,  # ← deprecated 参数
) -> ValidationResult:
    """Validate a NodeExecutionContext protocol.
    
    Args:
        context: The execution context dictionary to validate
        node_id: Optional node ID for node-specific rules (deprecated, kept for compatibility)
    """
    return cast(ValidationResult, self._node_execution_strategy.validate(context))
```

**问题**：`node_id` 参数被标记为 deprecated 但仍保留，实际验证逻辑并未使用它。

**清理建议**: 直接移除 `node_id` 参数

---

### 3.4 StateManager State 字段保留

**位置**: `storage/state_manager.py:388-389`

**问题描述**:

```python
result = {
    "evaluations": state.get("evaluations", {}),
    "node_iterations": state.get("node_iterations", {}),
    # ... 扁平化字段
    "state": state,  # ← Keep state field for backward compatibility
    "node_results": node_results,
}
```

**问题**：同时返回扁平化字段和完整的 `state` dict，造成数据冗余。

**风险**：
- 两处数据可能不一致
- 增加序列化开销
- 调用方可能依赖错误的数据源

---

## 四、中低风险兼容层

### 4.1 Tools Function-Style API

**位置**: `tools/create_deliverable.py:182-197`

用于测试兼容的函数式 API：

```python
# Backward compatibility: function-style API for tests
async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    tool = CreateDeliverableTool()
    return await tool._execute(params)
```

类似模式还存在于：
- `tools/create_document_set.py:310`
- `tools/update_context.py:177-192`

**风险**：低，主要影响测试代码

### 4.2 SDK Adapter 别名

**位置**: `tools/sdk_adapter.py:131-139`

```python
# Backward compatibility aliases
adapt_to_sdk = adapt_to_claude
adapt_from_sdk = adapt_from_claude

__all__ = [
    "adapt_to_claude",
    "adapt_from_claude",
    "adapt_to_sdk",  # Backward compatibility
    "adapt_from_sdk",  # Backward compatibility
    ...
]
```

### 4.3 异常类兼容

**位置**: `exceptions.py:497-575`

```python
class AgentError(DocuSwarmError):
    """This exception is kept for backward compatibility with existing code."""
    
class ValidationError(DocuSwarmError):
    """This exception is kept for backward compatibility with existing code."""
```

### 4.4 CLI 命令别名

**位置**: `cli/main.py:84`

```python
cli.add_command(list_pipelines, name="list-pipelines")  # Backward compatibility alias
```

### 4.5 Node Loader Re-export Facade

**位置**: `nodes/loader.py:1-34`

```python
"""Node Configuration Loader - Re-export from new v2 location.

This module re-exports from autoBMAD.nodes.loader for backward compatibility.
All new code should import directly from autoBMAD.nodes.loader.
"""

from autoBMAD.nodes.loader import (  # noqa: F401
    NodeAgentConfig,
    NodeConfig,
    ...
)
```

---

## 五、行为分叉分析

### 5.1 参数处理分叉

**场景**: SessionManager 初始化

```python
# 调用方 A（新方式）
session = SessionManager(
    work_dir=path,
    config=config,
    tool_permissions=permissions
)

# 调用方 B（旧方式）
session = SessionManager(
    work_dir=path,
    api_key="xxx",  # 被忽略？
    allowed_dirs=["/tmp"]  # 回退到 file_dirs
)
```

**风险**: 两种方式的配置结果可能不同

### 5.2 执行入口分叉

**场景**: DualAgentNode 调用

```python
# 路径 A（旧方式）
result = await node.execute(
    subject_context=context,
    task="task",
    pipeline_id="pipe_001"
)

# 路径 B（新方式）
execution_context = NodeExecutionContext(...)
result = await node.execute_with_context(execution_context)
```

**风险**: 
- 旧方式需要经过数据转换，可能丢失信息
- 两种路径的异常处理可能不同
- 调试时需要理解转换逻辑

### 5.3 数据模型分叉

**场景**: PipelineState 访问

```python
pipeline = state_manager.get_pipeline("pipe_001")

# 方式 A（新）：访问扁平化字段
evaluations = pipeline["evaluations"]

# 方式 B（旧）：访问 state 字段
evaluations = pipeline["state"]["evaluations"]
```

**风险**: 两处数据可能不一致

---

## 六、理解成本分析

### 6.1 新增开发者认知负担

一个新开发者需要理解：

1. **为什么有多个入口？** `execute()` vs `execute_with_context()`
2. **参数优先级是什么？** `file_dirs or allowed_dirs or []`
3. **应该使用哪个？** 文档可能不一致
4. **转换逻辑是什么？** 需要阅读 `_build_execution_context_from_legacy()`

### 6.2 维护成本

每次修改核心逻辑时：

1. 需要考虑两条执行路径
2. 需要测试兼容层的行为
3. 需要更新可能过时的文档

### 6.3 决策成本

增加新特性时：

- 是否需要支持旧参数？
- 是否需要添加新的兼容层？
- 如何标记 deprecated？

---

## 七、清理优先级与路线图

### P0 - 立即清理（1-2 周）

| 任务 | 文件 | 工作量 | 影响范围 |
|------|------|--------|---------|
| 移除 SessionManager legacy 参数 | `llm/session_manager.py` | 2-3 天 | 所有会话创建 |
| 移除 DualAgentNode legacy 桥接 | `nodes/dual_agent.py` | 3-5 天 | 所有节点执行 |

### P1 - 近期清理（2-4 周）

| 任务 | 文件 | 工作量 | 影响范围 |
|------|------|--------|---------|
| 移除 validator 兼容参数 | `context/validator.py` | 1 天 | 验证逻辑 |
| 移除 state 字段冗余 | `storage/state_manager.py` | 2 天 | 状态读取 |

### P2 - 计划清理（1-2 月）

| 任务 | 文件 | 工作量 | 影响范围 |
|------|------|--------|---------|
| 移除 tools function-style API | `tools/*.py` | 2-3 天 | 测试代码 |
| 移除 SDK adapter 别名 | `tools/sdk_adapter.py` | 1 天 | SDK 适配 |
| 移除异常类兼容 | `exceptions.py` | 1-2 天 | 错误处理 |
| 移除 CLI 别名 | `cli/main.py` | 0.5 天 | CLI |
| 移除 loader facade | `nodes/loader.py` | 2-3 天 | 导入语句 |

---

## 八、清理实施方案

### 8.1 SessionManager 清理步骤

> **目标：完全移除所有 legacy 参数和兼容代码，不保留 deprecation 警告。**

**阶段 1：识别并更新所有调用方**

首先搜索所有使用旧参数的代码：

```bash
# 查找使用 legacy 参数的调用点
grep -r "api_key=" autoBMAD/docuswarm tests --include="*.py"
grep -r "base_url=" autoBMAD/docuswarm tests --include="*.py"
grep -r "allowed_dirs=" autoBMAD/docuswarm tests --include="*.py"
```

将所有调用方更新为新 API：

```python
# 旧调用方式（需要修改）
session = SessionManager(
    work_dir=path,
    api_key="xxx",  # ← 移除
    allowed_dirs=["/tmp"]  # ← 改为 file_dirs
)

# 新调用方式
from autoBMAD.docuswarm.node_execution.contracts import NodeToolPermissions

tool_permissions = NodeToolPermissions(
    file_dirs=["/tmp"],
    search_dirs=[]
)
session = SessionManager(
    work_dir=path,
    config=config,  # 包含 api_key, base_url
    tool_permissions=tool_permissions
)
```

**阶段 2：移除兼容代码**

直接修改 `__init__` 签名，移除所有 legacy 参数：

```python
# llm/session_manager.py

def __init__(
    self,
    work_dir: Path,
    agent_file: Path | None = None,
    config: Any | None = None,
    node_id: str | None = None,
    tool_permissions: NodeToolPermissions | None = None,
):
    """Initialize session manager.
    
    Args:
        work_dir: Working directory for sessions.
        agent_file: Optional path to agent specification file.
        config: Configuration object containing API settings.
        node_id: Optional node identifier for MCP tool isolation.
        tool_permissions: Complete tool permission configuration.
    """
    self._work_dir = work_dir
    self._agent_file = agent_file
    self._config = config
    self._node_id = node_id
    self._tool_permissions = tool_permissions
    self._file_dirs = tool_permissions.file_dirs if tool_permissions else []
    self._search_dirs = tool_permissions.search_dirs if tool_permissions else []
    # ...

# 同时移除 allowed_dirs property
@property
def file_dirs(self) -> list[str]:
    """Get the file directories."""
    return self._file_dirs

# 删除 allowed_dirs property，不再提供兼容
```

**阶段 3：更新测试**

确保所有测试使用新 API：

```python
# tests/unit/llm/test_session_manager.py

# 删除或修改以下测试（如果存在）
# def test_session_manager_accepts_api_key(): ...  # ← 删除
# def test_session_manager_allowed_dirs_fallback(): ...  # ← 删除

def test_session_manager_requires_config_for_auth():
    """Session manager should get API credentials from config only."""
    config = Config(api_key="test-key", base_url="https://api.example.com")
    session = SessionManager(work_dir=tmp_path, config=config)
    assert session.config == config
```

### 8.2 DualAgentNode 清理步骤

> **目标：完全移除 execute() 方法及其 legacy 桥接，统一使用 execute_with_context()。**

**阶段 1：更新 Orchestrator 和所有调用方**

首先修改 `pipeline/orchestrator.py` 和所有使用 `execute()` 的代码：

```python
# pipeline/orchestrator.py（修改前）
result = await node.execute(
    subject_context=context_data,
    task=node_config.task,
    pipeline_id=pipeline_id
)

# pipeline/orchestrator.py（修改后）
from autoBMAD.docuswarm.node_execution.context_builder import create_context_builder

execution_context = create_context_builder().build(
    pipeline_id=pipeline_id,
    node_id=node.node_id,
    original_context={
        "content": node_config.task,
        "task": node_config.task,
        **context_data
    }
)
result = await node.execute_with_context(execution_context)
```

检查所有调用点：

```bash
grep -r "\.execute(" autoBMAD/docuswarm tests --include="*.py" | grep -v "execute_with_context"
```

**阶段 2：移除 execute() 方法和桥接代码**

直接删除 `execute()` 方法及其所有辅助方法：

```python
# nodes/dual_agent.py

# 删除以下方法：
# - execute() - 第 300-334 行
# - _build_execution_context_from_legacy() - 第 227-248 行
# - _normalize_legacy_subject_context() - 第 203-225 行

# 只保留 execute_with_context() 作为唯一执行入口
async def execute_with_context(
    self,
    execution_context: NodeExecutionContext,
) -> NodeResult:
    """Execute the dual-agent pattern using NodeExecutionContext.
    
    This is the ONLY execution entry point after compatibility layer removal.
    """
    # ... 现有实现
```

**阶段 3：更新测试**

```python
# tests/unit/nodes/test_dual_agent.py

# 删除以下测试：
# - test_execute_accepts_legacy_params
# - test_execute_builds_context_correctly
# - test_normalize_legacy_subject_context

# 保留并强化以下测试：
def test_execute_with_context_only_entry_point():
    """execute_with_context should be the only way to execute node."""
    node = DualAgentNode(config)
    
    context = NodeExecutionContext(...)
    result = asyncio.run(node.execute_with_context(context))
    
    assert result.deliverable is not None
    
# 验证 execute 方法不存在
def test_execute_method_removed():
    """Legacy execute method should be completely removed."""
    node = DualAgentNode(config)
    assert not hasattr(node, 'execute') or not callable(getattr(node, 'execute', None))
```

---

## 九、验证策略

### 9.1 兼容性 Burn-down 清单

创建清单追踪清理进度：

```markdown
- [ ] SessionManager.__init__() 移除 api_key 参数
- [ ] SessionManager.__init__() 移除 base_url 参数
- [ ] SessionManager.__init__() 移除 allowed_dirs 参数
- [ ] SessionManager 移除 allowed_dirs 属性
- [ ] DualAgentNode.execute() 标记 deprecated
- [ ] DualAgentNode 移除 _build_execution_context_from_legacy()
- [ ] ...
```

### 9.2 守护测试

对每个移除的兼容层添加测试，**验证兼容代码已被完全移除**：

```python
# tests/unit/compatibility/test_session_manager_cleanup.py

import inspect
import pytest
from autoBMAD.docuswarm.llm.session_manager import SessionManager


def test_session_manager_init_signature():
    """Verify SessionManager does not accept legacy parameters."""
    sig = inspect.signature(SessionManager.__init__)
    params = list(sig.parameters.keys())
    
    # 这些参数应当被完全移除
    assert 'api_key' not in params, "api_key parameter should be removed"
    assert 'base_url' not in params, "base_url parameter should be removed"
    assert 'allowed_dirs' not in params, "allowed_dirs parameter should be removed"


def test_session_manager_no_allowed_dirs_property():
    """Verify allowed_dirs property is removed."""
    assert not hasattr(SessionManager, 'allowed_dirs'), \
        "allowed_dirs property should be removed"


def test_session_manager_accepts_only_config():
    """Verify SessionManager only accepts config for authentication."""
    from pathlib import Path
    
    # 应当拒绝 legacy 参数
    with pytest.raises(TypeError):
        SessionManager(work_dir=Path("/tmp"), api_key="test")
    
    with pytest.raises(TypeError):
        SessionManager(work_dir=Path("/tmp"), allowed_dirs=["/tmp"])


# tests/unit/compatibility/test_dual_agent_cleanup.py

import inspect
from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode


def test_dual_agent_no_execute_method():
    """Verify legacy execute() method is completely removed."""
    # execute 方法不应存在（或不应是可调用的）
    assert not hasattr(DualAgentNode, 'execute'), \
        "execute() method should be removed, use execute_with_context() only"


def test_dual_agent_no_legacy_helpers():
    """Verify legacy helper methods are removed."""
    assert not hasattr(DualAgentNode, '_build_execution_context_from_legacy'), \
        "_build_execution_context_from_legacy should be removed"
    assert not hasattr(DualAgentNode, '_normalize_legacy_subject_context'), \
        "_normalize_legacy_subject_context should be removed"


# tests/unit/compatibility/test_validator_cleanup.py

def test_validator_no_node_id_param():
    """Verify validate_execution_context does not accept node_id."""
    from autoBMAD.docuswarm.context.validator import ContextValidator
    
    sig = inspect.signature(ContextValidator.validate_execution_context)
    assert 'node_id' not in sig.parameters, "node_id parameter should be removed"


# tests/integration/test_no_compatibility_layer.py

def test_no_legacy_api_usage():
    """Integration test: verify no legacy APIs are used in codebase."""
    # 此测试可以扫描代码，确保没有使用已移除的 API
    import subprocess
    
    result = subprocess.run(
        ['grep', '-r', 'allowed_dirs', 'autoBMAD/docuswarm', '--include=*.py'],
        capture_output=True,
        text=True
    )
    
    # 只应找到在注释或文档中的引用，不应有实际使用
    for line in result.stdout.split('\n'):
        if line and not any(x in line for x in ['deprecated', 'TODO', 'FIXME', 'compatibility']):
            assert False, f"Found legacy API usage: {line}"
```

### 9.3 静态检查

添加 CI 检查**确保已移除的 API 不被使用**：

```yaml
# .github/workflows/compatibility-check.yml

name: Compatibility Layer Check

on: [push, pull_request]

jobs:
  check-removed-apis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check for removed SessionManager parameters
        run: |
          # 这些参数应当完全从代码库中移除
          if grep -r "api_key=" autoBMAD/docuswarm tests --include="*.py" | grep -v "test_session_manager"; then
            echo "ERROR: Found usage of removed 'api_key' parameter"
            exit 1
          fi
          
          if grep -r "allowed_dirs=" autoBMAD/docuswarm tests --include="*.py" | grep -v "deprecated\|compatibility"; then
            echo "ERROR: Found usage of removed 'allowed_dirs' parameter"
            exit 1
          fi
      
      - name: Check for removed DualAgentNode.execute
        run: |
          # 检查是否还有代码调用旧的 execute 方法
          if grep -r "\.execute(" autoBMAD/docuswarm --include="*.py" | grep -v "execute_with_context"; then
            echo "ERROR: Found usage of removed 'execute()' method, use 'execute_with_context()'"
            exit 1
          fi
      
      - name: Check for legacy exception imports
        run: |
          if grep -r "from.*exceptions import.*AgentError\|from.*exceptions import.*ValidationError" autoBMAD/docuswarm --include="*.py"; then
            echo "WARNING: Found import of compatibility exceptions"
            exit 1
          fi
```

**pre-commit 钩子**：

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: check-removed-compat-apis
        name: Check for removed compatibility APIs
        entry: python tools/debt_research/check_removed_apis.py
        language: system
        pass_filenames: false
        always_run: true
```

```python
# tools/debt_research/check_removed_apis.py

#!/usr/bin/env python3
"""检查是否使用了已移除的兼容层 API。"""

import re
import sys
from pathlib import Path

REMOVED_APIS = {
    "SessionManager(api_key=": "api_key parameter removed, use config",
    "SessionManager(base_url=": "base_url parameter removed, use config",
    "SessionManager(allowed_dirs=": "allowed_dirs parameter removed, use tool_permissions",
    ".allowed_dirs": "allowed_dirs property removed, use file_dirs",
    "_build_execution_context_from_legacy": "Legacy bridge removed",
    "_normalize_legacy_subject_context": "Legacy normalizer removed",
    ".execute(subject_context": "execute() method removed, use execute_with_context()",
}

def check_file(filepath: Path) -> list[tuple[int, str, str]]:
    """检查单个文件中的禁用 API。"""
    issues = []
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    for line_num, line in enumerate(lines, 1):
        for api_pattern, message in REMOVED_APIS.items():
            if api_pattern in line and "# ALLOW-LEGACY" not in line:
                issues.append((line_num, line.strip(), message))
    
    return issues

def main():
    project_root = Path(__file__).parent.parent.parent
    source_dir = project_root / "autoBMAD" / "docuswarm"
    test_dir = project_root / "tests"
    
    all_issues = []
    
    for py_file in list(source_dir.rglob("*.py")) + list(test_dir.rglob("*.py")):
        issues = check_file(py_file)
        for line_num, line, message in issues:
            all_issues.append((py_file.relative_to(project_root), line_num, line, message))
    
    if all_issues:
        print("ERROR: Found usage of removed compatibility APIs:")
        for filepath, line_num, line, message in all_issues:
            print(f"  {filepath}:{line_num}")
            print(f"    Code: {line[:80]}")
            print(f"    Issue: {message}")
            print()
        sys.exit(1)
    else:
        print("OK: No removed APIs found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## 十、风险与缓解措施

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 清理破坏现有功能 | 中 | 高 | 1. 渐进式清理 2. 完整测试覆盖 3. 灰度发布 |
| 调用方未完全更新 | 高 | 中 | 1. 先添加 deprecation 警告 2. 给迁移留出时间 |
| 数据转换逻辑有隐藏依赖 | 中 | 高 | 1. 代码审查 2. 集成测试 3. 数据流追踪 |
| 回滚困难 | 低 | 中 | 1. 小步提交 2. 保留分支 3. 特性开关 |

---

## 十一、结论与建议

### 11.1 核心结论

1. **兼容层不是抽象问题，而是运行时的实际负担**
   - 23 处兼容层标记，10 处高风险
   - 直接影响主执行路径

2. **行为分叉真实存在**
   - SessionManager 有三种配置方式
   - DualAgentNode 有两条执行路径
   - 增加了理解和测试成本

3. **清理时机已经成熟**
   - 新 API 已经稳定
   - 代码库已完成主要架构迁移
   - 越早清理成本越低

### 11.2 行动建议

**立即行动（本周）**:
1. 创建兼容性 burn-down 清单
2. **搜索并列出所有需要更新的调用方**（关键：识别所有受影响代码）
3. 准备批量替换脚本

**短期行动（本月）- 完全移除 P0 兼容层**:
1. **完全移除** SessionManager legacy 参数（api_key, base_url, allowed_dirs）
2. **完全移除** DualAgentNode.execute() 及其桥接方法
3. **完全移除** ContextValidator node_id 参数
4. **完全移除** StateManager state 字段冗余
5. 添加守护测试验证移除完成

**中期行动（本季度）- 完全移除 P1/P2 兼容层**:
1. **完全移除** tools function-style API
2. **完全移除** SDK adapter 别名
3. **完全移除** 兼容异常类
4. **完全移除** CLI 命令别名
5. **完全移除** loader facade
6. 更新文档删除所有旧 API 引用
7. 在 CI 中添加检查确保无回归

**重要原则**：
- **不保留 deprecation 警告，直接移除**
- **所有修改在一个 PR 中完成**，避免部分清理导致的中间状态
- **提交前运行完整测试套件**，确保无破坏

### 11.3 最终建议

**核心原则：零容忍兼容层**

1. **本次清理目标：零残留**
   - 所有标记为 deprecated/legacy/compatibility 的代码必须完全移除
   - 不保留警告、不保留别名、不保留桥接方法
   - 代码库中不应存在任何 "deprecated"、"backward compatibility"、"legacy" 注释

2. **不要再增加新的兼容层**
   - 对于任何新特性，直接实现最终设计
   - 如果必须过渡，使用特性开关而非兼容层
   - 禁止引入新的 deprecated 标记

3. **代码审查检查清单**
   ```markdown
   - [ ] PR 中未引入新的兼容代码
   - [ ] 未使用 deprecated/legacy/backward compatibility 等词汇
   - [ ] 未添加函数/参数别名
   - [ ] 所有测试使用新 API
   ```

4. **长期维护**
   - 每月运行 `tools/debt_research/compatibility_layer_analyzer.py` 扫描
   - 发现新兼容层立即修复
   - 将兼容层检查纳入 CI 强制检查

---

## 附录

### A. 完整兼容层标记列表

| 文件 | 行号 | 模式 | 类别 | 严重性 |
|------|------|------|------|--------|
| `llm/session_manager.py` | 85 | api_key deprecated | parameter | high |
| `llm/session_manager.py` | 86 | base_url deprecated | parameter | high |
| `llm/session_manager.py` | 88 | allowed_dirs deprecated | parameter | high |
| `llm/session_manager.py` | 99 | allowed_dirs fallback | parameter | high |
| `llm/session_manager.py` | 131 | allowed_dirs property | property | medium |
| `nodes/dual_agent.py` | 203 | _normalize_legacy_subject_context | method | high |
| `nodes/dual_agent.py` | 227 | _build_execution_context_from_legacy | method | high |
| `nodes/dual_agent.py` | 329 | execute bridge | method | high |
| `nodes/dual_agent.py` | 643 | execute bridge (iteration) | method | high |
| `context/validator.py` | 1424 | node_id parameter | parameter | medium |
| `storage/state_manager.py` | 388 | state field | data | medium |
| `tools/sdk_adapter.py` | 132 | adapt_to_sdk alias | alias | low |
| `tools/sdk_adapter.py` | 133 | adapt_from_sdk alias | alias | low |
| `tools/create_deliverable.py` | 182 | function-style API | alias | low |
| `tools/create_document_set.py` | 310 | function-style API | alias | low |
| `tools/update_context.py` | 177 | function-style API | alias | low |
| `tools/callable_tool_wrapper.py` | 91 | ToolResultCallableTool alias | alias | low |
| `tools/callable_tool_wrapper.py` | 92 | CallableToolBase alias | alias | low |
| `exceptions.py` | 500 | AgentError exception | exception | low |
| `exceptions.py` | 574 | ValidationError exception | exception | low |
| `nodes/loader.py` | 3 | re-export facade | module | low |
| `cli/main.py` | 84 | list-pipelines alias | alias | low |

### B. 相关工具

- `tools/debt_research/compatibility_layer_analyzer.py` - 兼容层扫描
- `tools/debt_research/compatibility_call_chain_tracer.py` - 调用链追踪

### C. 参考文档

- 原始技术债审查报告: `docs/evaluation/2026-04-04-docuswarm-tech-debt-audit.md`
- 架构文档: `docs/architecture/`
