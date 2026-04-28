# MemoryManager 彻底移除方案研究报告

**文件**: `docs/research/refactor-2026-03-26/02-memory-manager-removal.md`  
**日期**: 2026-03-26  
**作者**: Robin（后端重构专家）  
**依赖扫描工具**: `tools/memory_manager_dependency_scanner.py`  
**扫描结果**: `.tmp/memory_manager_scan.json`  
**关联评估文档**:
- `docs/evaluation/2026-03-26-docuswarm-implementation-gap-analysis.md`
- `docs/evaluation/2026-03-26-docuswarm-deep-architecture-analysis.md`

---

## 1. 执行摘要

### 1.1 MemoryManager 当前状态

`MemoryManager` 是 DocuSwarm 在 Story 4.3（EPIC-04 上下文隔离）中设计的三层内存隔离组件，位于 `autoBMAD/docuswarm/context/memory.py`。该模块定义了 `MemoryScope` 枚举（SHARED / INDEPENDENT / EVALUATOR）和 `MemoryManager` 类（write / read / get_agent_context / clear_private_memory 四个公共方法）。

**关键发现**：经过诊断工具扫描（137 个 Python 文件），`MemoryManager` **从未被任何业务代码实际调用**：

| 指标 | 数值 |
|------|------|
| 导入引用数 | 1（仅 `context/__init__.py` 的 re-export）|
| 使用点（method_call）| 0（全部来自 memory.py 自身内部逻辑）|
| 受影响文件数 | 2（memory.py 自身 + __init__.py）|
| 整体移除复杂度 | **LOW（低）** |

`DualAgentNode`、`Orchestrator`、`node_execution/` 下的所有模块均**未引用** MemoryManager。它仅被 `__init__.py` 重新导出，属于"已定义但未启用"的孤立代码。

### 1.2 移除理由

1. **零使用率**：整个代码库无任何业务调用，属于死代码（dead code）
2. **功能已被替代**：`PipelineState.shared_context` + `ContextManager` 组合已满足所有当前隔离需求
3. **奥卡姆剃刀原则**：三层内存模型增加理解和维护成本，却无即时收益
4. **无真实需求**：当前无任何 Evaluator 私有内存的业务用例
5. **测试覆盖零**：`tests/` 目录下无任何 MemoryManager 相关测试文件

### 1.3 移除复杂度评估

| 维度 | 评估 |
|------|------|
| 代码修改量 | 极小（删除 1 个文件 + 修改 `__init__.py` 2 行）|
| 破坏性风险 | 极低（无外部调用方）|
| 测试影响 | 无（无相关测试）|
| 接口兼容性 | `__all__` 需要更新，但无外部消费者 |
| 回滚成本 | 低（通过 git 即可还原）|

**总体结论**：移除 MemoryManager 是一项**低风险、高价值**的清理操作。

---

## 2. 现状分析

### 2.1 MemoryManager 完整实现分析

**文件**: `autoBMAD/docuswarm/context/memory.py`（179 行）

#### 2.1.1 类结构

```
MemoryScope(Enum)                         # 第17-22行
├── SHARED = "shared"
├── INDEPENDENT = "independent"
└── EVALUATOR = "evaluator"

MemoryManager                             # 第25-179行
├── __init__(self) -> None                # 第32-36行：初始化三个内存字典
│   ├── _shared_memory: dict[str, Any]
│   ├── _independent_memory: dict[str, Any]
│   └── _evaluator_memory: dict[str, Any]
├── write(key, value, scope) -> None      # 第38-69行：按 scope 写入对应字典
├── read(key, scope) -> Any               # 第71-111行：按 scope 读取对应字典
├── get_agent_context(agent_type) -> dict # 第113-147行：合并 shared+private 上下文
└── clear_private_memory(scope) -> None  # 第149-179行：清空私有内存（不清 shared）
```

#### 2.1.2 方法详细分析

| 方法 | 行号 | 功能 | 实际调用次数 |
|------|------|------|------------|
| `__init__` | 32-36 | 初始化三个 dict | 0（从未实例化）|
| `write` | 38-69 | 按 scope 写入 | 0 |
| `read` | 71-111 | 按 scope 读取 | 0 |
| `get_agent_context` | 113-147 | 合并上下文 | 0 |
| `clear_private_memory` | 149-179 | 清空私有内存 | 0 |

#### 2.1.3 设计模式

`MemoryManager` 采用了 **Strategy Pattern**（通过 `MemoryScope` 枚举路由写入目标）和 **Façade Pattern**（统一对外暴露 read/write 接口屏蔽三字典内部结构）。设计本身无缺陷，问题在于它从未被集成到实际运行路径中。

### 2.2 依赖图（基于诊断工具输出）

```
依赖关系图（→ 表示"被依赖"）

autoBMAD/docuswarm/context/memory.py
    ← autoBMAD/docuswarm/context/__init__.py (import_type: from_import, line 16)

其他所有模块（node_execution、pipeline、agents）→ 均无对 memory.py 的引用
```

**诊断工具扫描结果摘要**（`.tmp/memory_manager_scan.json`）：

```json
{
  "summary": {
    "total_import_references": 1,
    "total_usage_points": 11,
    "affected_files_count": 2,
    "overall_removal_complexity": "low",
    "usage_by_type": {
      "type_annotation": 3,
      "method_call": 8
    }
  }
}
```

> 注：11 个"使用点"**全部来自 memory.py 自身**（类内部的 `MemoryScope.SHARED` 等引用），并非外部调用。

### 2.3 与其他模块的耦合分析

#### 2.3.1 context 模块内耦合

| 文件 | 耦合关系 | 说明 |
|------|----------|------|
| `context/__init__.py` | **直接导入** MemoryManager, MemoryScope | 第16、28-29行 |
| `context/isolation.py` | **无耦合** | ContextManager 完全独立 |
| `context/filter.py` | **无耦合** | ContextFilter 完全独立 |
| `context/audit.py` | **无耦合** | IsolationAuditLogger 完全独立 |

#### 2.3.2 pipeline 模块耦合

经 grep 扫描 `autoBMAD/docuswarm/pipeline/` 目录下所有 `.py` 文件：

- `orchestrator.py`：**无任何 memory 引用**
- `escalation.py`：第 162 行有 `# Store in memory` 注释，但这只是注释，非代码引用
- 其余文件：**无 memory 引用**

#### 2.3.3 node_execution 模块耦合

经 grep 扫描 `autoBMAD/docuswarm/node_execution/` 目录下所有 `.py` 文件（12 个文件）：

- **完全无任何 MemoryManager 引用**
- `contracts.py` 定义的 `NodeExecutionContext` TypedDict 中无 memory_manager 字段
- `context_builder.py` 构建上下文时使用 `shared_context` 字典，不涉及 MemoryManager

#### 2.3.4 agents 模块耦合

经扫描 `autoBMAD/docuswarm/` 所有子模块：**无任何外部文件引用 MemoryManager**。

---

## 3. 影响范围分析

### 3.1 直接影响的文件清单（含行号）

| 文件路径 | 影响类型 | 影响行号 | 操作 |
|----------|----------|----------|------|
| `autoBMAD/docuswarm/context/memory.py` | **文件删除** | 全部（1-179行）| 整体删除 |
| `autoBMAD/docuswarm/context/__init__.py` | **导入移除** | 第16行（import）、第28-29行（__all__）| 删除3行 |

**直接影响文件总计：2 个文件，3 行代码修改 + 179 行删除**

#### 3.1.1 `autoBMAD/docuswarm/context/__init__.py` 变更详情

```python
# 第16行（当前）—— 需要删除
from autoBMAD.docuswarm.context.memory import MemoryManager, MemoryScope

# 第18-30行（当前）—— __all__ 中需要删除2项
__all__ = [
    "AuditEvent",
    "EVENT_TYPE_CONTEXT_BUILD",
    "EVENT_TYPE_FILTER",
    "EVENT_TYPE_VIOLATION",
    "IsolationAuditLogger",
    "ContextFilter",
    "ContextManager",
    "ContextIsolationError",
    "PRIVATE_FIELDS",
    "MemoryManager",   # ← 删除此行
    "MemoryScope",     # ← 删除此行
]
```

### 3.2 间接影响的模块

**无间接影响**。

经完整扫描，`MemoryManager` 和 `MemoryScope` 仅被 `context/__init__.py` 导入，且该导入未被任何其他模块消费。移除后不存在级联失败风险。

### 3.3 配置文件中的引用

扫描 `.yaml`、`.json`、`.toml`、`.cfg` 配置文件：

- `pyproject.toml`：无 memory 相关配置
- `requirements.txt` / `requirements-dev.txt`：无 memory 相关依赖
- `node.yaml` 系列文件：无 memory_manager 引用
- `.env`：无 memory 相关配置

**结论：配置文件零影响。**

### 3.4 测试文件中的引用

扫描 `tests/` 目录全部 `.py` 文件（包含 agents、architecture、cli、e2e、integration、node_execution、pipeline、storage、tools 等子目录）：

**结论：测试文件零引用，无需修改任何现有测试。**

---

## 4. 移除方案

### 4.1 总体策略

采用**两步原子操作**：先修改 `__init__.py` 移除导出，再删除 `memory.py` 文件。顺序不可颠倒（否则中间状态 `__init__.py` 会因缺少 `memory.py` 而 ImportError）。

### 4.2 分步移除计划

#### Step 1：更新 `context/__init__.py`（移除导入和导出）

**文件**：`autoBMAD/docuswarm/context/__init__.py`

**修改前**（当前代码）：
```python
"""Context management module."""

from autoBMAD.docuswarm.context.audit import (
    EVENT_TYPE_CONTEXT_BUILD,
    EVENT_TYPE_FILTER,
    EVENT_TYPE_VIOLATION,
    AuditEvent,
    IsolationAuditLogger,
)
from autoBMAD.docuswarm.context.filter import ContextFilter
from autoBMAD.docuswarm.context.isolation import (
    PRIVATE_FIELDS,
    ContextIsolationError,
    ContextManager,
)
from autoBMAD.docuswarm.context.memory import MemoryManager, MemoryScope  # ← 第16行，删除

__all__ = [
    "AuditEvent",
    "EVENT_TYPE_CONTEXT_BUILD",
    "EVENT_TYPE_FILTER",
    "EVENT_TYPE_VIOLATION",
    "IsolationAuditLogger",
    "ContextFilter",
    "ContextManager",
    "ContextIsolationError",
    "PRIVATE_FIELDS",
    "MemoryManager",   # ← 删除
    "MemoryScope",     # ← 删除
]
```

**修改后**（目标代码）：
```python
"""Context management module."""

from autoBMAD.docuswarm.context.audit import (
    EVENT_TYPE_CONTEXT_BUILD,
    EVENT_TYPE_FILTER,
    EVENT_TYPE_VIOLATION,
    AuditEvent,
    IsolationAuditLogger,
)
from autoBMAD.docuswarm.context.filter import ContextFilter
from autoBMAD.docuswarm.context.isolation import (
    PRIVATE_FIELDS,
    ContextIsolationError,
    ContextManager,
)

__all__ = [
    "AuditEvent",
    "EVENT_TYPE_CONTEXT_BUILD",
    "EVENT_TYPE_FILTER",
    "EVENT_TYPE_VIOLATION",
    "IsolationAuditLogger",
    "ContextFilter",
    "ContextManager",
    "ContextIsolationError",
    "PRIVATE_FIELDS",
]
```

#### Step 2：删除 `memory.py` 文件

```bash
# 确认无外部引用后执行删除
rm autoBMAD/docuswarm/context/memory.py
```

**或通过 IDE 文件删除操作执行**（推荐，避免误操作）。

#### Step 3：验证构建无错误

```bash
cd d:/GITHUB/DocuSwarm
python -c "from autoBMAD.docuswarm.context import ContextManager, ContextFilter, IsolationAuditLogger; print('OK')"
```

预期输出：`OK`

#### Step 4：运行回归测试

```bash
cd d:/GITHUB/DocuSwarm
python -m pytest tests/ -x -q 2>&1 | tail -20
```

### 4.3 需要保留的功能及替代实现

#### 4.3.1 共享内存（SHARED scope）→ 已由 shared_context 替代

`MemoryScope.SHARED` 的功能（跨 Agent 共享键值对）已由 `NodeExecutionContext["shared_context"]` 字段完整替代。

```python
# 替代方案：在 NodeExecutionContext 中使用 shared_context
execution_context: NodeExecutionContext = {
    ...
    "shared_context": {
        "facts.decision_made": True,      # Independent Agent 写入
        "facts.document_version": "1.0",  # Independent Agent 写入
    },
    ...
}

# ContextManager.build_independent_input() 会自动将 shared_context 传递给 IndependentAgentInput
# 见 isolation.py 第103-114行
shared_context = execution_context.get("shared_context", {})
return IndependentAgentInput(
    ...
    shared_context=shared_context,  # P1-1: Pass shared_context
)
```

#### 4.3.2 私有内存（INDEPENDENT / EVALUATOR scope）→ 无需替代

当前无任何业务场景需要 Agent 私有内存（Independent 专属或 Evaluator 专属的跨调用持久化数据）。`ContextManager` + `ContextFilter` 的三层隔离机制已满足隔离需求。

#### 4.3.3 结论

| MemoryManager 功能 | 是否需要替代 | 替代方案 |
|-------------------|------------|---------|
| SHARED 作用域写入/读取 | ✅ 已替代 | `NodeExecutionContext["shared_context"]` |
| INDEPENDENT 作用域写入/读取 | ❌ 无需替代 | 当前无业务用例 |
| EVALUATOR 作用域写入/读取 | ❌ 无需替代 | 当前无业务用例 |
| `get_agent_context()` | ❌ 无需替代 | `ContextManager.build_independent_input()` 已集成 |
| `clear_private_memory()` | ❌ 无需替代 | 无调用方 |

---

## 5. 接口变更

### 5.1 移除前后 API 对比

#### 5.1.1 `context` 模块公共 API

| 符号 | 移除前 | 移除后 |
|------|--------|--------|
| `from autoBMAD.docuswarm.context import MemoryManager` | ✅ 可用 | ❌ ImportError |
| `from autoBMAD.docuswarm.context import MemoryScope` | ✅ 可用 | ❌ ImportError |
| `from autoBMAD.docuswarm.context import ContextManager` | ✅ 可用 | ✅ 不变 |
| `from autoBMAD.docuswarm.context import ContextFilter` | ✅ 可用 | ✅ 不变 |
| `from autoBMAD.docuswarm.context import IsolationAuditLogger` | ✅ 可用 | ✅ 不变 |
| `from autoBMAD.docuswarm.context import AuditEvent` | ✅ 可用 | ✅ 不变 |
| `from autoBMAD.docuswarm.context import PRIVATE_FIELDS` | ✅ 可用 | ✅ 不变 |
| `from autoBMAD.docuswarm.context import ContextIsolationError` | ✅ 可用 | ✅ 不变 |

#### 5.1.2 被移除的接口签名

```python
# 以下接口在移除后将不再可用：

class MemoryScope(Enum):
    SHARED = "shared"
    INDEPENDENT = "independent"
    EVALUATOR = "evaluator"

class MemoryManager:
    def __init__(self) -> None: ...
    def write(self, key: str, value: Any, scope: MemoryScope) -> None: ...
    def read(self, key: str, scope: MemoryScope) -> Any: ...
    def get_agent_context(self, agent_type: str) -> dict[str, Any]: ...
    def clear_private_memory(self, scope: MemoryScope) -> None: ...
```

### 5.2 需要更新的类型注解

**无需更新**。

由于 `MemoryManager` 从未出现在任何业务模块的类型注解中（函数参数、返回值、实例变量均无引用），移除后不会产生类型检查错误。

可通过 basedpyright 验证：
```bash
basedpyright autoBMAD/docuswarm/ --outputjson 2>&1 | python -c "import json,sys; d=json.load(sys.stdin); print('errors:', d['summary']['errorCount'])"
```

### 5.3 需要更新的配置 Schema

**无需更新**。

`MemoryManager` 不在任何 NodeConfig、PipelineConfig 或环境配置中有对应字段。

---

## 6. 回归测试策略

### 6.1 需要新增的测试用例

虽然移除操作本身的风险极低，但建议新增以下**保护性测试**以确保 context 模块导出的完整性：

#### 6.1.1 context 模块导出验证测试

**建议文件**：`tests/architecture/test_context_exports.py`

```python
"""验证 context 模块在移除 MemoryManager 后的导出完整性。"""

import pytest


def test_context_module_exports_required_symbols():
    """验证 context 模块仍导出所有必要符号。"""
    from autoBMAD.docuswarm.context import (
        AuditEvent,
        ContextFilter,
        ContextIsolationError,
        ContextManager,
        EVENT_TYPE_CONTEXT_BUILD,
        EVENT_TYPE_FILTER,
        EVENT_TYPE_VIOLATION,
        IsolationAuditLogger,
        PRIVATE_FIELDS,
    )
    assert ContextManager is not None
    assert ContextFilter is not None
    assert IsolationAuditLogger is not None


def test_memory_manager_not_in_context_exports():
    """验证 MemoryManager 已从公共导出中移除。"""
    import autoBMAD.docuswarm.context as ctx_module
    assert not hasattr(ctx_module, "MemoryManager"), (
        "MemoryManager 应已从 context 模块移除"
    )
    assert not hasattr(ctx_module, "MemoryScope"), (
        "MemoryScope 应已从 context 模块移除"
    )


def test_memory_py_file_deleted():
    """验证 memory.py 文件已被物理删除。"""
    from pathlib import Path
    memory_file = Path("autoBMAD/docuswarm/context/memory.py")
    assert not memory_file.exists(), (
        f"memory.py 应已被删除，但仍存在于 {memory_file.absolute()}"
    )
```

#### 6.1.2 context 模块功能回归测试

**建议补充至**：`tests/architecture/test_context_isolation.py`（如已存在）

```python
def test_context_manager_builds_independent_input_without_memory_manager():
    """验证 ContextManager 在没有 MemoryManager 的情况下仍能正常构建 IndependentAgentInput。"""
    from autoBMAD.docuswarm.context import ContextManager
    from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext

    ctx = ContextManager()
    execution_context: NodeExecutionContext = {
        "node_id": "test-node",
        "node_name": "Test Node",
        "task_name": "test-task",
        "task_description": "Test task description",
        "role_supplement": "",
        "deliverable_requirements": [],
        "original_context": "Test context",
        "chained_deliverables": [],
        "shared_context": {"key": "value"},
        "iteration_feedback": None,
        "evaluator_criteria": [],
    }
    result = ctx.build_independent_input(execution_context)
    assert result["shared_context"] == {"key": "value"}
    assert result["task_name"] == "test-task"
```

### 6.2 需要修改的现有测试

**无需修改任何现有测试。**

扫描结果确认：`tests/` 目录下无任何与 MemoryManager 相关的测试文件或测试用例。

### 6.3 验证移除完整性的检查方法

#### 6.3.1 自动化验证脚本

```bash
#!/bin/bash
# verify_memory_removal.sh

echo "=== MemoryManager 移除完整性验证 ==="

echo "[1] 验证 memory.py 已删除..."
if [ -f "autoBMAD/docuswarm/context/memory.py" ]; then
    echo "  FAIL: memory.py 仍然存在"
    exit 1
else
    echo "  PASS: memory.py 已删除"
fi

echo "[2] 验证 __init__.py 中无 MemoryManager 引用..."
if grep -q "MemoryManager" autoBMAD/docuswarm/context/__init__.py; then
    echo "  FAIL: __init__.py 仍包含 MemoryManager 引用"
    exit 1
else
    echo "  PASS: __init__.py 已清理"
fi

echo "[3] 验证全局无 MemoryManager 引用..."
REFS=$(grep -r "MemoryManager\|MemoryScope" autoBMAD/ --include="*.py" | grep -v "memory_manager_dependency_scanner" | wc -l)
if [ "$REFS" -gt 0 ]; then
    echo "  WARN: 仍有 $REFS 处引用"
    grep -rn "MemoryManager\|MemoryScope" autoBMAD/ --include="*.py"
else
    echo "  PASS: 全局零引用"
fi

echo "[4] 运行 Python 导入测试..."
python -c "
from autoBMAD.docuswarm.context import ContextManager, ContextFilter, IsolationAuditLogger
print('  PASS: 核心模块导入正常')
try:
    from autoBMAD.docuswarm.context import MemoryManager
    print('  FAIL: MemoryManager 仍可导入')
    exit(1)
except ImportError:
    print('  PASS: MemoryManager 已不可导入')
"

echo "[5] 运行单元测试..."
python -m pytest tests/ -x -q --tb=short 2>&1 | tail -5

echo "=== 验证完成 ==="
```

#### 6.3.2 basedpyright 静态分析验证

```bash
basedpyright autoBMAD/docuswarm/context/ 2>&1 | grep -E "error|warning" | head -20
```

预期：零错误，或仅有与 MemoryManager 无关的既有警告。

---

## 7. 风险评估与缓解

### 7.1 运行时错误风险

#### 7.1.1 风险：外部代码直接 import MemoryManager

| 项目 | 说明 |
|------|------|
| 风险级别 | **极低** |
| 风险描述 | 若有外部脚本（非 autoBMAD/ 目录）直接 `from autoBMAD.docuswarm.context import MemoryManager`，移除后会触发 ImportError |
| 缓解措施 | 已通过 grep 扫描整个工程目录（137 个 Python 文件），**确认无任何外部引用** |
| 残留风险 | `tools/` 目录下的独立脚本、`scripts/` 目录下的工具——已确认仅有扫描工具提及 MemoryManager 关键词（字符串形式），非导入引用 |

#### 7.1.2 风险：运行时动态导入

| 项目 | 说明 |
|------|------|
| 风险级别 | **极低** |
| 风险描述 | 若代码中使用 `importlib.import_module("autoBMAD.docuswarm.context.memory")` 动态导入 |
| 缓解措施 | 扫描全局 `importlib` 和 `__import__` 调用，未发现相关用例 |

### 7.2 配置兼容性风险

#### 7.2.1 风险：未来扩展中误用 MemoryScope 概念

| 项目 | 说明 |
|------|------|
| 风险级别 | **低** |
| 风险描述 | 未来开发者可能期望通过 `MemoryScope` 控制内存隔离，但该 API 已不存在 |
| 缓解措施 | 在 `context/isolation.py` 顶部注释中说明当前隔离策略使用 `shared_context`，不使用 MemoryManager |
| 建议注释内容 | `# 注意：内存隔离通过 NodeExecutionContext["shared_context"] + ContextManager 实现。MemoryManager 已于 2026-03-26 重构中移除，原因：零使用率且功能已被 shared_context 覆盖。` |

### 7.3 未来扩展性影响

#### 7.3.1 场景：需要更严格的 Agent 内存隔离

**问题**：若未来出现需要 Evaluator Agent 拥有私有内存的业务场景（如多轮评审积累评分历史），MemoryManager 的三层隔离模型将是自然实现。

**影响评估**：

| 扩展需求 | 移除 MemoryManager 后的实现成本 |
|---------|-------------------------------|
| 跨节点共享数据 | 无影响，`shared_context` 已满足 |
| Evaluator 私有内存 | 需重新实现，但可从 git 历史恢复 memory.py |
| 内存级别的审计追踪 | 需要，但当前 `IsolationAuditLogger` 已提供基础审计 |

**缓解措施**：移除前通过 `git commit` 保存历史记录，未来若需要可通过 `git show` 或 `git revert` 恢复。

#### 7.3.2 场景：分布式/持久化内存扩展

MemoryManager 原设计保留了"持久化、分布式内存等高级特性"的扩展接口（见 `2026-03-26-docuswarm-deep-architecture-analysis.md` 第 213 行注释）。移除后，若需要此类特性，需从零开始设计，无法基于现有代码扩展。

**影响评估**：**低**。DocuSwarm 当前定位为单机批处理管道，分布式内存场景属于远期需求，不应以预留死代码的方式应对。

#### 7.3.3 总体评估

```
风险矩阵：

                  低概率    高概率
高影响    │ 分布式内存  │          │
          │  (低概率)  │          │
          ├────────────┼──────────┤
低影响    │            │ 配置兼容 │
          │            │ (高概率) │
          └────────────┴──────────┘

结论：所有风险均为低～中等，可接受。
```

---

## 附录 A：诊断工具输出完整摘要

**工具**：`tools/memory_manager_dependency_scanner.py`  
**执行命令**：`python tools/memory_manager_dependency_scanner.py --format json --output .tmp/memory_manager_scan.json`  
**扫描时间**：2026-03-26  
**扫描文件数**：137 个 Python 文件  

```
发现统计：
  - 导入引用：1 个（context/__init__.py 第16行）
  - 使用点：11 个（全部在 memory.py 内部）
  - 受影响文件：2 个
  - 整体移除复杂度：LOW

移除步骤建议（工具生成）：
  1. 确认 MemoryManager 当前实际使用量（运行此工具后查看 usage_points）
  2. 检查所有 test_files_affected 中的测试用例，标记需要更新的测试
  3. 对 high_impact_files 中的文件，逐一分析是否可用 NodeExecutionContext.shared_context 替代
  4. 移除 context/memory.py 中的 MemoryManager 和 MemoryScope 类
  5. 更新 context/__init__.py 移除相关导出
  6. 批量替换所有 import 引用（优先处理 medium/low impact 文件）
  7. 运行测试套件验证无功能回归
```

---

## 附录 B：关联评估文档关键结论引用

### 来源：`docs/evaluation/2026-03-26-docuswarm-implementation-gap-analysis.md`

> **第1.3节（EPIC-04 上下文隔离）**：
> "MemoryManager：⚠️ 未启用 — 代码存在但未在 DualAgentNode 中集成"
> 
> "建议：基于奥卡姆剃刀原则，建议**延迟启用** MemoryManager。当前 `PipelineState.shared_context` 已能满足跨节点共享需求，增加三层内存模型会增加复杂度却无即时收益。"

### 来源：`docs/evaluation/2026-03-26-docuswarm-deep-architecture-analysis.md`

> **第2.5节（建议：延迟启用 MemoryManager）**：
> "决策：暂不集成 MemoryManager，但保留代码
> 理由：
> 1. 当前 shared_context + ContextManager 已满足 P0-1 单一上下文协议
> 2. 没有明确的 Evaluator 私有内存需求
> 3. 增加复杂度却无即时收益，违反奥卡姆剃刀原则
> 4. 未来如需更严格的内存隔离，可随时启用"

**本报告将"延迟启用"升级为"彻底移除"的依据**：
- 评估文档发布后进一步确认了零使用率（诊断工具扫描 137 个文件，外部调用为 0）
- 死代码持续存在于代码库会误导未来开发者认为此功能"即将接入"
- 移除后可随时通过 git history 恢复，成本极低

---

## 附录 C：`context` 模块移除后的完整 `__init__.py`

```python
"""Context management module."""

from autoBMAD.docuswarm.context.audit import (
    EVENT_TYPE_CONTEXT_BUILD,
    EVENT_TYPE_FILTER,
    EVENT_TYPE_VIOLATION,
    AuditEvent,
    IsolationAuditLogger,
)
from autoBMAD.docuswarm.context.filter import ContextFilter
from autoBMAD.docuswarm.context.isolation import (
    PRIVATE_FIELDS,
    ContextIsolationError,
    ContextManager,
)

__all__ = [
    "AuditEvent",
    "EVENT_TYPE_CONTEXT_BUILD",
    "EVENT_TYPE_FILTER",
    "EVENT_TYPE_VIOLATION",
    "IsolationAuditLogger",
    "ContextFilter",
    "ContextManager",
    "ContextIsolationError",
    "PRIVATE_FIELDS",
]
```

---

*报告生成时间：2026-03-26*  
*执行者：Robin（后端重构专家）*  
*任务 ID：#3*
