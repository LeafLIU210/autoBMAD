# Finding B 兼容层清理测试驱动方案

**方案日期**: 2026-04-04  
**目标**: 完全移除所有兼容层代码（零容忍）  
**范围**: P0/P1/P2 全部清理任务  
**方案位置**: `docs/solution/2026-04-04-finding-b-compatibility-cleanup-tdd-plan.md`

---

## 目录

1. [方案概述](#一方案概述)
2. [TDD 流程规范](#二tdd-流程规范)
3. [P0 任务：高风险兼容层清理](#三p0-任务高风险兼容层清理)
4. [P1 任务：中风险兼容层清理](#四p1-任务中风险兼容层清理)
5. [P2 任务：低风险兼容层清理](#五p2-任务低风险兼容层清理)
6. [验收标准](#六验收标准)
7. [回滚策略](#七回滚策略)

---

## 一、方案概述

### 1.1 清理范围

| 优先级 | 任务数 | 影响范围 | 预估工作量 |
|--------|--------|----------|-----------|
| P0 | 2个主要任务 | 核心执行路径 | 7-10天 |
| P1 | 2个主要任务 | 验证/存储层 | 3-4天 |
| P2 | 5个次要任务 | 边缘模块 | 6-8天 |

### 1.2 TDD 核心原则

```
红 → 绿 → 重构
↑___________|
```

1. **红**: 编写失败的测试（验证兼容代码存在）
2. **绿**: 编写最少代码使测试通过（移除兼容代码）
3. **重构**: 优化代码结构

### 1.3 零容忍原则

- 不添加 deprecation 警告，**直接移除**
- 不保留别名，**完全删除**
- 不保留桥接方法，**统一入口**

---

## 二、TDD 流程规范

### 2.1 每个任务的步骤

```
Step 1: 编写"存在性测试"（验证兼容代码当前存在）
Step 2: 运行测试，确认通过（红）
Step 3: 移除兼容代码
Step 4: 修改测试为"移除验证测试"（验证兼容代码已移除）
Step 5: 运行测试，确认通过（绿）
Step 6: 重构优化
Step 7: 提交代码
```

### 2.2 测试文件命名规范

```
tests/unit/compatibility/test_<module>_cleanup.py
tests/integration/compatibility/test_<feature>_cleanup.py
```

### 2.3 测试基类

```python
# tests/unit/compatibility/__init__.py

"""兼容层清理测试基类。"""

import inspect
from typing import Any


class CompatibilityCleanupTestBase:
    """兼容层清理测试基类。"""
    
    def assert_method_removed(self, cls: type, method_name: str) -> None:
        """断言方法已被完全移除。"""
        assert not hasattr(cls, method_name), \
            f"{cls.__name__}.{method_name} 应当被移除"
    
    def assert_param_removed(self, func: Any, param_name: str) -> None:
        """断言参数已被完全移除。"""
        sig = inspect.signature(func)
        assert param_name not in sig.parameters, \
            f"参数 '{param_name}' 应当从 {func.__name__} 中移除"
    
    def assert_property_removed(self, cls: type, prop_name: str) -> None:
        """断言属性已被完全移除。"""
        assert not hasattr(cls, prop_name), \
            f"{cls.__name__}.{prop_name} 属性应当被移除"
    
    def assert_class_removed(self, module: Any, class_name: str) -> None:
        """断言类已被完全移除。"""
        assert not hasattr(module, class_name), \
            f"{class_name} 类应当被移除"
```

---

## 三、P0 任务：高风险兼容层清理

### 任务 P0-1: SessionManager 完全移除 Legacy 参数

#### 目标
完全移除 `api_key`, `base_url`, `allowed_dirs` 参数及 `allowed_dirs` 属性。

#### Step 1: 编写存在性测试（红）

```python
# tests/unit/compatibility/test_session_manager_cleanup.py

"""SessionManager 兼容层清理测试。"""

import inspect
import pytest
from pathlib import Path

from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerCompatibilityRemoval:
    """验证 SessionManager 兼容层已完全移除。"""
    
    def test_api_key_param_exists(self):
        """Step 1: 验证 api_key 参数当前存在（清理前）。"""
        sig = inspect.signature(SessionManager.__init__)
        assert 'api_key' in sig.parameters, \
            "测试前置条件：api_key 参数应当存在"
    
    def test_base_url_param_exists(self):
        """Step 1: 验证 base_url 参数当前存在（清理前）。"""
        sig = inspect.signature(SessionManager.__init__)
        assert 'base_url' in sig.parameters, \
            "测试前置条件：base_url 参数应当存在"
    
    def test_allowed_dirs_param_exists(self):
        """Step 1: 验证 allowed_dirs 参数当前存在（清理前）。"""
        sig = inspect.signature(SessionManager.__init__)
        assert 'allowed_dirs' in sig.parameters, \
            "测试前置条件：allowed_dirs 参数应当存在"
    
    def test_allowed_dirs_property_exists(self):
        """Step 1: 验证 allowed_dirs 属性当前存在（清理前）。"""
        assert hasattr(SessionManager, 'allowed_dirs'), \
            "测试前置条件：allowed_dirs 属性应当存在"
```

#### Step 2-3: 识别并更新所有调用方

```bash
# 查找所有使用点
grep -rn "api_key=" autoBMAD/docuswarm tests --include="*.py"
grep -rn "base_url=" autoBMAD/docuswarm tests --include="*.py"
grep -rn "allowed_dirs=" autoBMAD/docuswarm tests --include="*.py"
grep -rn "\.allowed_dirs" autoBMAD/docuswarm tests --include="*.py"
```

**示例调用方更新**:

```python
# 更新前
def create_session_with_legacy_params():
    return SessionManager(
        work_dir=Path("/tmp"),
        api_key=os.environ["ANTHROPIC_API_KEY"],
        base_url="https://api.anthropic.com",
        allowed_dirs=["/data"]
    )

# 更新后
from autoBMAD.docuswarm.node_execution.contracts import NodeToolPermissions
from autoBMAD.docuswarm.config import Config

def create_session_with_new_api():
    config = Config(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        base_url="https://api.anthropic.com"
    )
    tool_permissions = NodeToolPermissions(
        file_dirs=["/data"],
        search_dirs=[]
    )
    return SessionManager(
        work_dir=Path("/tmp"),
        config=config,
        tool_permissions=tool_permissions
    )
```

#### Step 4: 实现清理

```python
# autoBMAD/docuswarm/llm/session_manager.py

class SessionManager:
    """Session manager - 兼容层已完全移除。"""
    
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
        self._active_clients: dict[str, ClaudeSDKClient] = {}
        self._logger = logger.bind(
            component="SessionManager",
            work_dir=str(work_dir),
            agent_file=str(agent_file) if agent_file else None,
            node_id=node_id,
        )
    
    @property
    def file_dirs(self) -> list[str]:
        """Get the file directories."""
        return self._file_dirs
    
    @property
    def search_dirs(self) -> list[str]:
        """Get the search directories."""
        return self._search_dirs
    
    # allowed_dirs property 已完全移除
```

#### Step 5: 更新测试为移除验证（绿）

```python
# tests/unit/compatibility/test_session_manager_cleanup.py

"""SessionManager 兼容层清理测试 - 移除验证。"""

import inspect
import pytest
from pathlib import Path

from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerCompatibilityRemoved:
    """验证 SessionManager 兼容层已完全移除。"""
    
    def test_api_key_param_removed(self):
        """验证 api_key 参数已移除。"""
        sig = inspect.signature(SessionManager.__init__)
        assert 'api_key' not in sig.parameters, \
            "api_key 参数应当被移除，使用 config 代替"
    
    def test_base_url_param_removed(self):
        """验证 base_url 参数已移除。"""
        sig = inspect.signature(SessionManager.__init__)
        assert 'base_url' not in sig.parameters, \
            "base_url 参数应当被移除，使用 config 代替"
    
    def test_allowed_dirs_param_removed(self):
        """验证 allowed_dirs 参数已移除。"""
        sig = inspect.signature(SessionManager.__init__)
        assert 'allowed_dirs' not in sig.parameters, \
            "allowed_dirs 参数应当被移除，使用 tool_permissions 代替"
    
    def test_allowed_dirs_property_removed(self):
        """验证 allowed_dirs 属性已移除。"""
        assert not hasattr(SessionManager, 'allowed_dirs'), \
            "allowed_dirs 属性应当被移除，使用 file_dirs 代替"
    
    def test_legacy_params_rejected(self):
        """验证 legacy 参数被拒绝。"""
        with pytest.raises(TypeError):
            SessionManager(work_dir=Path("/tmp"), api_key="test")
        
        with pytest.raises(TypeError):
            SessionManager(work_dir=Path("/tmp"), allowed_dirs=["/tmp"])
    
    def test_new_api_works(self):
        """验证新 API 正常工作。"""
        from autoBMAD.docuswarm.node_execution.contracts import NodeToolPermissions
        
        tool_permissions = NodeToolPermissions(
            file_dirs=["/data"],
            search_dirs=[]
        )
        session = SessionManager(
            work_dir=Path("/tmp"),
            tool_permissions=tool_permissions
        )
        
        assert session.file_dirs == ["/data"]
        assert session.search_dirs == []
```

#### 验收标准

- [ ] `api_key` 参数已移除
- [ ] `base_url` 参数已移除
- [ ] `allowed_dirs` 参数已移除
- [ ] `allowed_dirs` 属性已移除
- [ ] 所有调用方已更新
- [ ] 所有测试通过

---

### 任务 P0-2: DualAgentNode 完全移除 Legacy 执行链

#### 目标
完全移除 `execute()` 方法及其桥接方法，统一使用 `execute_with_context()`。

#### Step 1: 编写存在性测试（红）

```python
# tests/unit/compatibility/test_dual_agent_cleanup.py

"""DualAgentNode 兼容层清理测试。"""

import inspect
import pytest

from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode


class TestDualAgentCompatibilityRemoval:
    """验证 DualAgentNode 兼容层当前存在（清理前）。"""
    
    def test_execute_method_exists(self):
        """Step 1: 验证 execute() 方法当前存在。"""
        assert hasattr(DualAgentNode, 'execute'), \
            "测试前置条件：execute() 方法应当存在"
    
    def test_legacy_builder_exists(self):
        """Step 1: 验证 _build_execution_context_from_legacy 存在。"""
        assert hasattr(DualAgentNode, '_build_execution_context_from_legacy'), \
            "测试前置条件：_build_execution_context_from_legacy 应当存在"
    
    def test_legacy_normalizer_exists(self):
        """Step 1: 验证 _normalize_legacy_subject_context 存在。"""
        assert hasattr(DualAgentNode, '_normalize_legacy_subject_context'), \
            "测试前置条件：_normalize_legacy_subject_context 应当存在"
```

#### Step 2-3: 更新所有调用方

```bash
# 查找所有调用点
grep -rn "\.execute(" autoBMAD/docuswarm --include="*.py" | grep -v "execute_with_context"
```

**关键更新：pipeline/orchestrator.py**

```python
# autoBMAD/docuswarm/pipeline/orchestrator.py

# 更新前
result = await node.execute(
    subject_context=context_data,
    task=node_config.task,
    pipeline_id=pipeline_id
)

# 更新后
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

#### Step 4: 实现清理

```python
# autoBMAD/docuswarm/nodes/dual_agent.py

class DualAgentNode:
    """DualAgentNode - 兼容层已完全移除。"""
    
    # execute() 方法已完全移除
    # _build_execution_context_from_legacy() 已完全移除
    # _normalize_legacy_subject_context() 已完全移除
    
    async def execute_with_context(
        self,
        execution_context: NodeExecutionContext,
    ) -> NodeResult:
        """Execute the dual-agent pattern using NodeExecutionContext.
        
        This is the ONLY execution entry point.
        All calling code must construct NodeExecutionContext before calling.
        
        Args:
            execution_context: The unified NodeExecutionContext.
        
        Returns:
            NodeResult containing deliverable, evaluation, etc.
        """
        # ... 现有实现，无需修改
```

#### Step 5: 更新测试为移除验证（绿）

```python
# tests/unit/compatibility/test_dual_agent_cleanup.py

"""DualAgentNode 兼容层清理测试 - 移除验证。"""

import inspect
import pytest
import asyncio

from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode


class TestDualAgentCompatibilityRemoved:
    """验证 DualAgentNode 兼容层已完全移除。"""
    
    def test_execute_method_removed(self):
        """验证 execute() 方法已移除。"""
        assert not hasattr(DualAgentNode, 'execute'), \
            "execute() 方法应当被移除，使用 execute_with_context()"
    
    def test_legacy_builder_removed(self):
        """验证 _build_execution_context_from_legacy 已移除。"""
        assert not hasattr(DualAgentNode, '_build_execution_context_from_legacy'), \
            "_build_execution_context_from_legacy 应当被移除"
    
    def test_legacy_normalizer_removed(self):
        """验证 _normalize_legacy_subject_context 已移除。"""
        assert not hasattr(DualAgentNode, '_normalize_legacy_subject_context'), \
            "_normalize_legacy_subject_context 应当被移除"
    
    def test_execute_with_context_only_entry(self):
        """验证 execute_with_context 是唯一执行入口。"""
        methods = [m for m in dir(DualAgentNode) if not m.startswith('_')]
        execute_methods = [m for m in methods if 'execute' in m.lower()]
        
        assert execute_methods == ['execute_with_context'], \
            f"应当只有 execute_with_context，但找到: {execute_methods}"
```

#### 验收标准

- [ ] `execute()` 方法已移除
- [ ] `_build_execution_context_from_legacy()` 已移除
- [ ] `_normalize_legacy_subject_context()` 已移除
- [ ] `pipeline/orchestrator.py` 已更新
- [ ] 所有调用方已更新
- [ ] 所有测试通过

---

## 四、P1 任务：中风险兼容层清理

### 任务 P1-1: ContextValidator 移除 node_id 参数

#### TDD 流程

```python
# tests/unit/compatibility/test_validator_cleanup.py

"""ContextValidator 兼容层清理测试。"""

import inspect
from autoBMAD.docuswarm.context.validator import ContextValidator


def test_node_id_param_removed():
    """验证 node_id 参数已从 validate_execution_context 移除。"""
    validator = ContextValidator()
    sig = inspect.signature(validator.validate_execution_context)
    
    assert 'node_id' not in sig.parameters, \
        "node_id 参数应当被移除"
```

#### 实现

```python
# autoBMAD/docuswarm/context/validator.py

def validate_execution_context(
    self,
    context: dict[str, Any],
    # node_id 参数已移除
) -> ValidationResult:
    """Validate a NodeExecutionContext protocol.
    
    Args:
        context: The execution context dictionary to validate.
    
    Returns:
        ValidationResult containing validation outcome.
    """
    return cast(ValidationResult, self._node_execution_strategy.validate(context))
```

---

### 任务 P1-2: StateManager 移除 state 字段冗余

#### TDD 流程

```python
# tests/unit/compatibility/test_state_manager_cleanup.py

"""StateManager 兼容层清理测试。"""

import pytest
from autoBMAD.docuswarm.storage.state_manager import StateManager


def test_state_field_not_in_result(temp_db_path):
    """验证 get_pipeline 返回结果不包含冗余 state 字段。"""
    manager = StateManager(temp_db_path)
    
    # 创建测试 pipeline
    pipeline_id = manager.create_pipeline("test_pipeline")
    
    # 获取结果
    result = manager.get_pipeline(pipeline_id)
    
    # 不应包含冗余 state 字段
    assert 'state' not in result, \
        "state 字段应当被移除，使用扁平化字段"
    
    # 但应该包含扁平化字段
    assert 'evaluations' in result
    assert 'node_iterations' in result
```

#### 实现

```python
# autoBMAD/docuswarm/storage/state_manager.py

# 在 get_pipeline 方法中

result = {
    "evaluations": state.get("evaluations", {}),
    "node_iterations": state.get("node_iterations", {}),
    "session_ids": state.get("session_ids", {}),
    "session_metadata": state.get("session_metadata", {}),
    "current_node_session_id": state.get("current_node_session_id"),
    "error": state.get("error"),
    "shared_context": state.get("shared_context", {}),
    "subject_context": state.get("subject_context", {}),
    # "state": state,  # ← 已移除
    "node_results": node_results,
}
```

---

## 五、P2 任务：低风险兼容层清理

### 任务 P2-1: Tools Function-Style API 移除

#### 目标文件
- `tools/create_deliverable.py:182-197`
- `tools/create_document_set.py:310`
- `tools/update_context.py:177-192`

#### TDD 流程

```python
# tests/unit/compatibility/test_tools_cleanup.py

"""Tools 兼容层清理测试。"""

import inspect
from autoBMAD.docuswarm.tools import create_deliverable
from autoBMAD.docuswarm.tools import create_document_set
from autoBMAD.docuswarm.tools import update_context


def test_create_deliverable_function_removed():
    """验证 create_deliverable 函数式 API 已移除。"""
    # 应当只有 CreateDeliverableTool 类
    assert not hasattr(create_deliverable, 'create_deliverable'), \
        "函数式 API 应当被移除，使用 CreateDeliverableTool 类"


def test_create_document_set_function_removed():
    """验证 create_document_set 函数式 API 已移除。"""
    assert not hasattr(create_document_set, 'create_document_set'), \
        "函数式 API 应当被移除，使用 CreateDocumentSetTool 类"
```

#### 实现

```python
# autoBMAD/docuswarm/tools/create_deliverable.py

# 删除以下代码:
# async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
#     """Backward-compatible function API..."""
#     tool = CreateDeliverableTool()
#     return await tool._execute(params)

__all__ = ["CreateDeliverableTool", "CreateDeliverableParams"]
```

---

### 任务 P2-2: SDK Adapter 别名移除

#### TDD 流程

```python
# tests/unit/compatibility/test_sdk_adapter_cleanup.py

"""SDK Adapter 兼容层清理测试。"""

from autoBMAD.docuswarm.tools import sdk_adapter


def test_adapt_to_sdk_alias_removed():
    """验证 adapt_to_sdk 别名已移除。"""
    assert not hasattr(sdk_adapter, 'adapt_to_sdk'), \
        "adapt_to_sdk 别名应当被移除，使用 adapt_to_claude"


def test_adapt_from_sdk_alias_removed():
    """验证 adapt_from_sdk 别名已移除。"""
    assert not hasattr(sdk_adapter, 'adapt_from_sdk'), \
        "adapt_from_sdk 别名应当被移除，使用 adapt_from_claude"
```

#### 实现

```python
# autoBMAD/docuswarm/tools/sdk_adapter.py

# 删除以下代码:
# adapt_to_sdk = adapt_to_claude
# adapt_from_sdk = adapt_from_claude

__all__ = [
    "adapt_to_claude",
    "adapt_from_claude",
    # "adapt_to_sdk",  # ← 已移除
    # "adapt_from_sdk",  # ← 已移除
    "adapt_result_to_metadata",
]
```

---

### 任务 P2-3: 异常类兼容移除

#### TDD 流程

```python
# tests/unit/compatibility/test_exceptions_cleanup.py

"""Exceptions 兼容层清理测试。"""

from autoBMAD.docuswarm import exceptions


def test_agent_error_removed():
    """验证 AgentError 兼容异常已移除。"""
    assert not hasattr(exceptions, 'AgentError'), \
        "AgentError 应当被移除"


def test_validation_error_removed():
    """验证 ValidationError 兼容异常已移除。"""
    assert not hasattr(exceptions, 'ValidationError'), \
        "ValidationError 应当被移除"
```

---

### 任务 P2-4: CLI 命令别名移除

#### TDD 流程

```python
# tests/unit/compatibility/test_cli_cleanup.py

"""CLI 兼容层清理测试。"""

from click.testing import CliRunner
from autoBMAD.docuswarm.cli.main import cli


def test_list_pipelines_alias_removed():
    """验证 list-pipelines 别名已移除。"""
    runner = CliRunner()
    
    # list-pipelines 应当不存在
    result = runner.invoke(cli, ['list-pipelines'])
    assert result.exit_code != 0, \
        "list-pipelines 别名应当被移除，使用 list"
```

#### 实现

```python
# autoBMAD/docuswarm/cli/main.py

# 删除以下代码:
# cli.add_command(list_pipelines, name="list-pipelines")

cli.add_command(list_pipelines)  # 只保留默认名称
```

---

### 任务 P2-5: Node Loader Facade 移除

#### TDD 流程

```python
# tests/unit/compatibility/test_loader_facade_cleanup.py

"""Node Loader Facade 兼容层清理测试。"""

# 所有导入应当直接来自 autoBMAD.nodes.loader
# autoBMAD.docuswarm.nodes.loader 应当不存在或为空


def test_loader_facade_removed():
    """验证 loader facade 已移除。"""
    import importlib
    
    # 尝试导入 facade 应当失败或返回空模块
    with pytest.raises(ImportError):
        from autoBMAD.docuswarm.nodes import loader
```

#### 实现

```python
# autoBMAD/docuswarm/nodes/loader.py

"""Node Configuration Loader - 已迁移。

此模块已迁移到 autoBMAD.nodes.loader。
请直接从 autoBMAD.nodes.loader 导入。
"""

raise ImportError(
    "autoBMAD.docuswarm.nodes.loader has been removed. "
    "Import directly from autoBMAD.nodes.loader instead."
)
```

---

## 六、验收标准

### 6.1 代码验收

```python
# tests/integration/compatibility/test_zero_compatibility.py

"""零兼容层验收测试。"""

import subprocess
import re


def test_no_deprecated_in_codebase():
    """验证代码库中不存在 'deprecated' 标记。"""
    result = subprocess.run(
        ['grep', '-ri', 'deprecated', 'autoBMAD/docuswarm', '--include=*.py'],
        capture_output=True,
        text=True
    )
    
    # 排除文档字符串中的说明
    lines = [l for l in result.stdout.split('\n') 
             if l and '"""' not in l and "'''" not in l]
    
    assert len(lines) == 0, \
        f"发现 deprecated 标记:\n{chr(10).join(lines[:5])}"


def test_no_backward_compatibility_in_codebase():
    """验证代码库中不存在 'backward compatibility'。"""
    result = subprocess.run(
        ['grep', '-ri', 'backward compatibility', 'autoBMAD/docuswarm', '--include=*.py'],
        capture_output=True,
        text=True
    )
    
    assert result.stdout == "", \
        f"发现 backward compatibility:\n{result.stdout[:500]}"


def test_no_legacy_in_codebase():
    """验证代码库中不存在 'legacy' 标记（除历史文档外）。"""
    result = subprocess.run(
        ['grep', '-ri', 'legacy', 'autoBMAD/docuswarm', '--include=*.py'],
        capture_output=True,
        text=True
    )
    
    # 排除 _normalize_legacy_subject_context 等预期的遗留引用
    lines = [l for l in result.stdout.split('\n') 
             if l and '_legacy_' in l.lower()]
    
    assert len(lines) == 0, \
        f"发现 legacy 标记:\n{chr(10).join(lines[:5])}"
```

### 6.2 功能验收

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 端到端测试通过
- [ ] 手动验证关键路径

### 6.3 检查清单

```markdown
## 最终检查清单

### P0 验收
- [ ] SessionManager 无 legacy 参数
- [ ] SessionManager 无 allowed_dirs 属性
- [ ] DualAgentNode 无 execute() 方法
- [ ] DualAgentNode 无桥接方法

### P1 验收
- [ ] ContextValidator 无 node_id 参数
- [ ] StateManager 无冗余 state 字段

### P2 验收
- [ ] Tools 无 function-style API
- [ ] SDK Adapter 无别名
- [ ] 无兼容异常类
- [ ] CLI 无命令别名
- [ ] Node Loader facade 已移除

### 代码质量
- [ ] 代码覆盖度 > 80%
- [ ] 无 mypy 错误
- [ ] 无 ruff 警告
- [ ] 文档已更新
```

---

## 七、回滚策略

### 7.1 提交策略

```
分支: feature/remove-compatibility-layers

提交 1: P0-1 SessionManager 清理
提交 2: P0-2 DualAgentNode 清理
提交 3: P1-1 ContextValidator 清理
提交 4: P1-2 StateManager 清理
提交 5: P2 所有清理
提交 6: 文档更新
```

### 7.2 回滚计划

如果清理导致问题：

1. **立即回滚**: `git revert HEAD~n..HEAD`
2. **修复问题**
3. **重新提交**

### 7.3 特性开关（可选）

如需渐进式发布：

```python
# 在清理前添加特性开关（仅用于过渡期）
import os

USE_NEW_API_ONLY = os.environ.get("DOCUSWARM_NEW_API_ONLY", "true").lower() == "true"

if USE_NEW_API_ONLY:
    # 新 API 路径
else:
    # 旧 API 路径（清理时删除）
```

---

## 附录

### A. 批量替换脚本

```bash
#!/bin/bash
# scripts/migrate_to_new_api.sh

# 替换 SessionManager 调用
find autoBMAD/docuswarm tests -name "*.py" -exec sed -i \
    -e 's/api_key=.*,/\/\/ TODO: Move to config/g' \
    -e 's/base_url=.*,/\/\/ TODO: Move to config/g' \
    -e 's/allowed_dirs=/file_dirs=/g' \
    {} \;
```

### B. 快速检查命令

```bash
# 检查是否还有遗留代码
grep -r "api_key=" autoBMAD/docuswarm tests --include="*.py"
grep -r "_legacy_" autoBMAD/docuswarm --include="*.py"
grep -r "backward compatibility" autoBMAD/docuswarm --include="*.py"
grep -r "deprecated" autoBMAD/docuswarm --include="*.py" | grep -v "doc"
```

---

**文档版本**: 1.0  
**最后更新**: 2026-04-04  
**维护者**: DocuSwarm Team
