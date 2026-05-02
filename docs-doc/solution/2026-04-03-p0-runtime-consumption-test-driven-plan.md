# P0 Runtime Consumption 修复测试驱动方案

**方案日期**: 2026-04-03  
**依据报告**: `docs/research/2026-04-03-p0-runtime-consumption-fix-research-report.md`  
**目标模块**: `autoBMAD/docuswarm`  
**方案优先级**: P1

---

## 1. 方案概述

本方案针对 P0 Runtime Consumption 修复研究报告中的 5 个已修复问题及 P1 优先级后续工作，设计一套完整的测试驱动验证体系。通过单元测试、集成测试和端到端契约测试，确保运行时行为与配置声明（`node.yaml` / `evaluator.yaml`）完全一致，消除硬编码特例，建立配置即行为的单一真相源。

---

## 2. 测试目标与范围

### 2.1 核心目标

1. **配置即行为**: 运行时消费的阈值、权限、迭代次数必须与配置文件完全一致
2. **单一真相源**: `NodeLoader` 作为配置唯一入口，所有运行时组件必须消费其输出
3. **无回归风险**: 已修复的 5 个 P0 问题必须有自动化测试守护
4. **P1 质量门**: `QualityConfig` 中的硬编码特例必须被测试暴露并最终移除

### 2.2 测试范围

| 层级 | 覆盖内容 | 测试类型 |
|------|----------|----------|
| 单元测试 | `SessionManager`, `EvaluatorAgent`, `DualAgentNode`, `IndependentAgent` 的修复逻辑 | 隔离测试 |
| 集成测试 | `NodeLoader` → `create_dual_agent_node` → `SessionManager._create_options()` 的完整链路 | 契约测试 |
| 端到端测试 | 真实节点配置（如 `architect`）驱动下的阈值、迭代次数、权限解析 | 配置一致性测试 |

---

## 3. P0 问题测试方案

### 3.1 问题一：MCP Server Key 命名冲突

#### 问题回顾
`SessionManager._create_options()` 曾使用 `docuswarm-fastmcp-{node_id}` 作为 key，导致文件和搜索 MCP server 互相覆盖。修复后使用 `NodeToolFilter` 一致的命名规范。

#### 测试文件
`tests/unit/llm/test_session_manager_mcp_keys.py`

#### 测试用例设计

**T1.1: MCP server keys 不应冲突**
```python
# Arrange
sm = SessionManager(
    work_dir=Path("/tmp"),
    node_id="analyst",
    file_dirs=["/tmp/docs"],
    search_dirs=["/tmp/docs/research"]
)

# Act
options = sm._create_options()

# Assert
keys = list(options.mcp_servers.keys())
assert len(keys) == len(set(keys)), "MCP server keys 存在重复"
assert any("files" in k for k in keys), "缺少 file server key"
assert any("search" in k for k in keys), "缺少 search server key"
```

**T1.2: Key 命名与 NodeToolFilter 一致**
```python
# Arrange
from autoBMAD.docuswarm.llm.tool_filter import (
    FILE_SERVER_NAME_FORMAT,
    SEARCH_SERVER_NAME_FORMAT,
)
expected_file_key = FILE_SERVER_NAME_FORMAT.format(node_id="analyst")
expected_search_key = SEARCH_SERVER_NAME_FORMAT.format(node_id="analyst")

# Act
options = sm._create_options()

# Assert
assert expected_file_key in options.mcp_servers
assert expected_search_key in options.mcp_servers
```

**T1.3: allowed_tools 中的工具名前缀与 MCP keys 一致**
```python
# Arrange
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
from autoBMAD.nodes.loader import NodeLoader

node_config = NodeLoader.load("analyst")
filter_ = NodeToolFilter(node_id="analyst", tool_permissions=node_config.tool_permissions)
allowed = filter_.get_allowed_tools()

# Act
options = sm._create_options()

# Assert
for tool in allowed:
    if tool.startswith("mcp__"):
        server_part = tool.split("__")[1]
        assert server_part in options.mcp_servers, f"{server_part} 不在 MCP servers 中"
```

---

### 3.2 问题二：NodeToolPermissions 传递丢失

#### 问题回顾
`IndependentAgent.execute_with_input()` 仅传递 `file_dirs` 和 `search_dirs`，导致 `allowed_builtin_tools`（如 `["Read", "Glob"]`）丢失。

#### 测试文件
`tests/unit/agents/test_independent_agent_permissions.py`

#### 测试用例设计

**T2.1: _create_pipeline_session_manager 接收完整的 tool_permissions**
```python
# Arrange
agent = IndependentAgent(config=mock_config, session_manager=mock_sm, node_id="analyst")
full_permissions = NodeToolPermissions(
    allowed_builtin_tools=["Read", "Glob"],
    file_permissions=NodeFilePermissions(allowed_read_dirs=["/tmp/docs"]),
    search_permissions=NodeSearchPermissions(search_dirs=["/tmp/docs"]),
)

# Act (mock SessionManager)
with patch("autoBMAD.docuswarm.llm.session_manager.SessionManager") as mock_cls:
    agent._create_pipeline_session_manager(
        work_dir=Path("/tmp"),
        node_id="analyst",
        file_dirs=["/tmp/docs"],
        search_dirs=["/tmp/docs"],
        tool_permissions=full_permissions,
    )

    # Assert
    call_kwargs = mock_cls.call_args.kwargs
    assert call_kwargs["tool_permissions"] == full_permissions
    assert call_kwargs["tool_permissions"].allowed_builtin_tools == ["Read", "Glob"]
```

**T2.2: execute_with_input 构建的 SessionManager 保留 allowed_builtin_tools**
```python
# Arrange (使用真实 NodeLoader 加载 analyst 配置)
from autoBMAD.nodes.loader import NodeLoader
node_config = NodeLoader.load("analyst")

# Act
# 通过 execute_with_input 的调用链路，最终验证 _create_options() 中的 allowed_tools
# 包含 Read, Glob
```

**T2.3: allowed_tools 包含 builtin tools 和 MCP 工具**
```python
# Arrange
sm = SessionManager(
    work_dir=Path("/tmp"),
    node_id="analyst",
    tool_permissions=NodeLoader.load("analyst").tool_permissions,
)

# Act
options = sm._create_options()

# Assert
# 通过 NodeToolFilter 反推 allowed_tools
filter_ = NodeToolFilter(node_id="analyst", tool_permissions=NodeLoader.load("analyst").tool_permissions)
allowed = filter_.get_allowed_tools()

builtin_tools = [t for t in allowed if not t.startswith("mcp__")]
assert "Read" in builtin_tools or "Glob" in builtin_tools, "builtin tools 丢失"
```

---

### 3.3 问题三：目录解析基准错误

#### 问题回顾
节点配置中的 `docs/` 被错误解析为 `autoBMAD/docs/`，正确路径应为仓库根目录下的 `docs/`。

#### 测试文件
`tests/unit/agents/test_directory_resolution.py`  
`tests/unit/node_execution/test_executor_project_root.py`

#### 测试用例设计

**T3.1: IndependentAgent 使用仓库根目录解析路径**
```python
# Arrange
from autoBMAD.docuswarm.agents.independent import IndependentAgent

# 模拟 project_root 指向 autoBMAD/ 子目录
agent = IndependentAgent(
    config=mock_config,
    session_manager=mock_sm,
    node_id="analyst",
    project_root=Path("/repo/autoBMAD"),
)

# Act
repo_root = agent.project_root.parent if agent.project_root.name == "autoBMAD" else agent.project_root
file_dirs = [str(repo_root / "docs")]

# Assert
assert "/repo/docs" in file_dirs
assert "autoBMAD/docs" not in file_dirs
```

**T3.2: executor.py 传递 repo_root 而非 autoBMAD 子目录**
```python
# Arrange
from autoBMAD.docuswarm.node_execution.executor import create_dual_agent_node
from unittest.mock import patch

auto_bmad_root = Path(__file__).resolve().parent.parent.parent.parent / "autoBMAD"
repo_root = auto_bmad_root.parent

# Act
with patch("autoBMAD.docuswarm.agents.independent.create_independent_agent") as mock_ia:
    with patch("autoBMAD.docuswarm.agents.evaluator.create_evaluator_agent") as mock_ea:
        create_dual_agent_node(
            config=mock_config,
            session_manager=mock_sm,
            node_id="analyst",
        )
        
        # Assert: project_root 应指向仓库根目录
        ia_call = mock_ia.call_args
        assert ia_call.kwargs["project_root"] == repo_root or str(ia_call.kwargs["project_root"]).endswith("DocuSwarm")
```

**T3.3: 解析后的目录真实存在（集成测试）**
```python
# Arrange
import os
repo_root = Path.cwd()
if repo_root.name == "autoBMAD":
    repo_root = repo_root.parent

# Act & Assert
assert (repo_root / "docs").exists(), "docs/ 目录应在仓库根下"
assert (repo_root / "docs" / "research").exists(), "docs/research/ 目录应存在"
```

---

### 3.4 问题四：Evaluator 阈值配置未消费

#### 问题回顾
`EvaluatorAgent` 曾使用硬编码阈值 `APPROVAL_THRESHOLD = 0.70`，而 `architect` 节点配置声明 `approval: 0.75`。

#### 测试文件
`tests/unit/agents/test_evaluator_threshold_consumption.py`

#### 测试用例设计

**T4.1: EvaluatorAgent 从节点配置加载阈值**
```python
# Arrange
from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
from unittest.mock import MagicMock

mock_sm = MagicMock()

# Act
agent = EvaluatorAgent(
    config=MagicMock(),
    session_manager=mock_sm,
    node_id="architect",
)

# Assert
assert agent.approval_threshold == 0.75, f"期望 0.75, 实际 {agent.approval_threshold}"
assert agent.blocked_threshold == 0.50, f"期望 0.50, 实际 {agent.blocked_threshold}"
```

**T4.2: 显式参数优先级高于节点配置**
```python
# Act
agent = EvaluatorAgent(
    config=MagicMock(),
    session_manager=mock_sm,
    node_id="architect",
    approval_threshold=0.90,
    blocked_threshold=0.30,
)

# Assert
assert agent.approval_threshold == 0.90
assert agent.blocked_threshold == 0.30
```

**T4.3: _determine_verdict 使用实例属性而非类常量**
```python
# Arrange
agent = EvaluatorAgent(
    config=MagicMock(),
    session_manager=mock_sm,
    node_id="architect",
)

# Act & Assert
assert agent._determine_verdict(0.76) == "APPROVED"      # >= 0.75
assert agent._determine_verdict(0.74) == "NEEDS_REVISION" # > 0.50 且 < 0.75
assert agent._determine_verdict(0.50) == "BLOCKED"       # <= 0.50
```

**T4.4: 节点配置缺失时回退到默认值**
```python
# Arrange
# 使用一个不存在的 node_id 或没有 threshold 的节点
agent = EvaluatorAgent(
    config=MagicMock(),
    session_manager=mock_sm,
    node_id="nonexistent_node_for_test",
)

# Assert
assert agent.approval_threshold == EvaluatorAgent.DEFAULT_APPROVAL_THRESHOLD
assert agent.blocked_threshold == EvaluatorAgent.DEFAULT_BLOCKED_THRESHOLD
```

---

### 3.5 问题五：max_iterations 未从配置注入

#### 问题回顾
`create_dual_agent_node()` 默认使用硬编码 `DualAgentNode.DEFAULT_MAX_ITERATIONS = 3`，未从节点 `evaluator.yaml` 加载 `max_iterations`。

#### 测试文件
`tests/unit/nodes/test_dual_agent_max_iterations.py`

#### 测试用例设计

**T5.1: 未显式传递时从节点配置加载 max_iterations**
```python
# Arrange
from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
from autoBMAD.nodes.loader import NodeLoader
from unittest.mock import MagicMock, patch

node_config = NodeLoader.load("architect")
expected = node_config.evaluator.max_iterations

# Act
with patch("autoBMAD.docuswarm.agents.independent.create_independent_agent"):
    with patch("autoBMAD.docuswarm.agents.evaluator.create_evaluator_agent"):
        node = create_dual_agent_node(
            config=MagicMock(),
            session_manager=MagicMock(),
            node_id="architect",
            # max_iterations 不传递
        )

# Assert
assert node.max_iterations == expected, f"期望 {expected}, 实际 {node.max_iterations}"
```

**T5.2: 显式传递时覆盖节点配置**
```python
# Act
with patch("autoBMAD.docuswarm.agents.independent.create_independent_agent"):
    with patch("autoBMAD.docuswarm.agents.evaluator.create_evaluator_agent"):
        node = create_dual_agent_node(
            config=MagicMock(),
            session_manager=MagicMock(),
            node_id="architect",
            max_iterations=10,
        )

# Assert
assert node.max_iterations == 10
```

**T5.3: 节点配置加载失败时回退到默认值**
```python
# Act
with patch("autoBMAD.docuswarm.agents.independent.create_independent_agent"):
    with patch("autoBMAD.docuswarm.agents.evaluator.create_evaluator_agent"):
        node = create_dual_agent_node(
            config=MagicMock(),
            session_manager=MagicMock(),
            node_id="nonexistent_node_for_test_12345",
        )

# Assert
assert node.max_iterations == DualAgentNode.DEFAULT_MAX_ITERATIONS
```

---

## 4. P1 优先级集成测试方案

### 4.1 运行时配置一致性端到端测试

#### 测试文件
`tests/integration/test_runtime_config_consistency.py`

#### 测试目标
验证从 `NodeLoader.load()` 到最终运行时对象的完整链路中，配置值不发生漂移。

#### 测试用例设计

**I1.1: architect 节点完整链路一致性**
```python
def test_architect_runtime_matches_config():
    """验证 architect 节点的运行时行为与配置完全一致"""
    # Arrange
    from autoBMAD.nodes.loader import NodeLoader
    from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
    
    node_config = NodeLoader.load("architect")
    
    # Act
    node = create_dual_agent_node(
        config=MagicMock(),
        session_manager=MagicMock(),
        node_id="architect",
    )
    
    # Assert
    assert node.max_iterations == node_config.evaluator.max_iterations
    assert node.evaluator_agent.approval_threshold == node_config.evaluator.threshold["approval"]
    assert node.evaluator_agent.blocked_threshold == node_config.evaluator.threshold["escalation"]
```

**I1.2: allowed_tools 与 tool_permissions 一致性**
```python
def test_allowed_tools_matches_node_config():
    """验证 allowed_tools 包含配置声明的所有 builtin tools"""
    from autoBMAD.nodes.loader import NodeLoader
    from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter
    
    node_config = NodeLoader.load("analyst")
    filter_ = NodeToolFilter(node_id="analyst", tool_permissions=node_config.tool_permissions)
    allowed = filter_.get_allowed_tools()
    
    for tool in node_config.tool_permissions.allowed_builtin_tools:
        assert tool in allowed, f"builtin tool {tool} 不在 allowed_tools 中"
```

**I1.3: 目录解析一致性**
```python
def test_directory_resolution_matches_repo_structure():
    """验证配置中的相对目录解析为仓库根目录下的真实路径"""
    from autoBMAD.docuswarm.agents.independent import IndependentAgent
    
    repo_root = Path.cwd()
    if repo_root.name == "autoBMAD":
        repo_root = repo_root.parent
    
    agent = IndependentAgent(
        config=MagicMock(),
        session_manager=MagicMock(),
        node_id="analyst",
        project_root=repo_root / "autoBMAD",  # 模拟错误的子目录
    )
    
    # project_root 被修正为 repo_root
    effective_root = agent.project_root.parent if agent.project_root.name == "autoBMAD" else agent.project_root
    assert effective_root == repo_root
```

---

## 5. QualityConfig 硬编码统一测试方案（P1）

### 5.1 问题回顾

`QualityConfig` 中存在针对 `architect` 节点的硬编码特例：

```python
ARCHITECT_APPROVAL = 0.75
ARCHITECT_ESCALATION = 0.55
```

而 `architect` 的 `evaluator.yaml` 配置为 `approval: 0.75, escalation: 0.50`。两者在 `escalation` 上不一致（0.55 vs 0.50），构成潜在风险。

### 5.2 测试策略

**第一阶段：暴露问题**（本方案重点）
- 编写测试强制验证 `QualityConfig.get_thresholds("architect")` 必须与 `NodeLoader.load("architect").evaluator.threshold` 一致
- 当前测试应当失败，从而驱动重构

**第二阶段：移除硬编码**（后续迭代）
- 修改 `QualityConfig` 使其默认从 `NodeLoader` / `evaluator.yaml` 加载节点特定阈值
- 测试通过后，硬编码特例即可安全移除

### 5.3 测试文件
`tests/unit/pipeline/test_quality_config_node_consistency.py`

### 5.4 测试用例设计

**Q1.1: QualityConfig 的 architect 阈值必须与节点配置一致**
```python
def test_quality_config_architect_matches_node_config():
    """
    ❌ 预期失败（Red）: 暴露 QualityConfig 硬编码与节点配置的不一致。
    该测试驱动 QualityConfig 重构，使其从 evaluator.yaml 加载阈值。
    """
    from autoBMAD.docuswarm.pipeline.quality import QualityConfig
    from autoBMAD.nodes.loader import NodeLoader
    
    node_config = NodeLoader.load("architect")
    qc = QualityConfig()
    thresholds = qc.get_thresholds("architect")
    
    assert thresholds.approval == node_config.evaluator.threshold["approval"]
    assert thresholds.escalation == node_config.evaluator.threshold["escalation"]
```

**Q1.2: 所有已知节点的 QualityConfig 阈值应与配置一致**
```python
import pytest

KNOWN_NODES = ["architect", "analyst", "pm", "ux", "po", "reviewer"]

@pytest.mark.parametrize("node_id", KNOWN_NODES)
def test_quality_config_matches_node_config_for_all_nodes(node_id):
    """对所有已知节点验证阈值一致性"""
    from autoBMAD.docuswarm.pipeline.quality import QualityConfig
    from autoBMAD.nodes.loader import NodeLoader
    
    try:
        node_config = NodeLoader.load(node_id)
    except FileNotFoundError:
        pytest.skip(f"Node {node_id} 无配置")
    
    if not node_config.evaluator or not node_config.evaluator.threshold:
        pytest.skip(f"Node {node_id} 无 threshold 配置")
    
    qc = QualityConfig()
    thresholds = qc.get_thresholds(node_id)
    
    assert thresholds.approval == node_config.evaluator.threshold["approval"]
    assert thresholds.escalation == node_config.evaluator.threshold["escalation"]
```

**Q1.3: QualityConfig 应支持显式 node_overrides 覆盖配置值**
```python
def test_quality_config_explicit_override_works():
    """验证显式覆盖机制仍然有效"""
    from autoBMAD.docuswarm.pipeline.quality import QualityConfig, QualityThresholds
    
    qc = QualityConfig(
        node_overrides={
            "architect": QualityThresholds(approval=0.99, escalation=0.99)
        }
    )
    thresholds = qc.get_thresholds("architect")
    
    assert thresholds.approval == 0.99
    assert thresholds.escalation == 0.99
```

---

## 6. 测试文件组织建议

```
tests/
├── unit/
│   ├── llm/
│   │   ├── test_session_manager_mcp_keys.py          # T1.1 - T1.3
│   │   └── ...
│   ├── agents/
│   │   ├── test_independent_agent_permissions.py     # T2.1 - T2.3
│   │   ├── test_directory_resolution.py              # T3.1
│   │   └── test_evaluator_threshold_consumption.py   # T4.1 - T4.4
│   ├── nodes/
│   │   └── test_dual_agent_max_iterations.py         # T5.1 - T5.3
│   ├── node_execution/
│   │   └── test_executor_project_root.py             # T3.2
│   └── pipeline/
│       └── test_quality_config_node_consistency.py   # Q1.1 - Q1.3
├── integration/
│   └── test_runtime_config_consistency.py            # I1.1 - I1.3
└── conftest.py
```

---

## 7. 测试实现计划

### Phase 1: P0 守护测试（立即执行）

按以下优先级依次实现，确保每个 P0 修复都有自动化测试覆盖：

1. **T4 系列**（Evaluator 阈值）→ 最简单，影响最大
2. **T5 系列**（max_iterations）→ 依赖 T4 的 mock 模式
3. **T1 系列**（MCP Key）→ 需要理解 `NodeToolFilter`
4. **T2 系列**（ToolPermissions）→ 需要 mock 多层调用
5. **T3 系列**（目录解析）→ 需要处理路径和文件系统

### Phase 2: 集成测试（本周内）

实现 `tests/integration/test_runtime_config_consistency.py`，使用真实的 `NodeLoader` 和最小化的 mock，验证端到端一致性。

### Phase 3: QualityConfig 驱动测试（P1，下周）

1. 先实现 Q1.1（预期失败）
2. 重构 `QualityConfig`，使其优先从 `NodeLoader` 加载节点阈值
3. 实现 Q1.2、Q1.3
4. 移除 `ARCHITECT_APPROVAL` / `ARCHITECT_ESCALATION` 硬编码

---

## 8. 验收标准

| # | 验收项 | 验收标准 |
|---|--------|----------|
| A1 | P0 测试覆盖率 | 5 个 P0 问题每个至少有 3 个单元测试守护 |
| A2 | 集成测试通过 | `test_runtime_config_consistency.py` 对 `architect` 和 `analyst` 节点全部通过 |
| A3 | QualityConfig 一致性 | `QualityConfig.get_thresholds("architect")` 与 `evaluator.yaml` 完全一致 |
| A4 | 无硬编码特例 | `QualityConfig` 中不存在任何节点 ID 的硬编码阈值分支 |
| A5 | CI 绿灯 | 新增测试全部通过，现有测试零回归 |

---

## 9. 风险与注意事项

1. **NodeLoader 路径依赖**: 集成测试依赖真实的 `nodes/` 目录结构，确保测试在仓库根目录执行
2. **pytest-qt 临时目录**: 如出现 `PermissionError`，参考研究报告第 6.1 节清理临时目录
3. **QualityConfig 重构影响面**: `VerdictDeterminer` 和 `DualAgentNode.execute_with_iteration()` 均使用 `QualityConfig`，重构时需同步检查
4. **MCP 服务器创建**: `NodeToolFilter.create_mcp_servers()` 可能依赖外部文件系统权限，单元测试建议 mock 该方法

---

**方案作者**: AI Assistant  
**最后更新**: 2026-04-03
