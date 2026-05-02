# 依赖统一迁移方案

**方案版本**: 1.0  
**创建日期**: 2026-03-25  
**状态**: 待实施

---

## 1. 迁移目标

将 DocuSwarm 项目从 `kimi-agent-sdk` + `kaos.path` 完全迁移到 `claude-agent-sdk`，实现：

1. **依赖声明与实际一致**: pyproject.toml 声明的依赖 = 代码实际使用的依赖
2. **单一 SDK 事实源**: 只使用 `claude-agent-sdk`
3. **零向后兼容**: 彻底移除 `kimi-agent-sdk` 相关代码
4. **参考架构**: 以 `autoBMAD/epic_automation/sdk_wrapper.py` 为 SDK 封装标准

---

## 2. 迁移范围

### 2.1 必须迁移的文件 (7个)

```
autoBMAD/docuswarm/
├── agents/
│   ├── evaluator.py          # Message 导入
│   └── independent.py        # Message, MessageAggregator, MaxStepsReached, RunCancelled, KaosPath
├── llm/
│   ├── approval.py           # ApprovalRequest
│   └── session_manager.py    # 完整 SDK 依赖 + KaosPath
├── pipeline/
│   └── orchestrator.py       # Message, KaosPath
└── tools/
    ├── callable_tool_wrapper.py  # CallableTool2, ToolReturnValue
    └── sdk_adapter.py        # ToolError, ToolOk, ToolReturnValue
```

### 2.2 需要更新的配置文件 (3个)

```
.
├── pyproject.toml            # 确认依赖声明正确
├── requirements.txt          # 清理注释
└── requirements-dev.txt      # 移除 kimi-agent-sdk 相关注释
```

---

## 3. 详细迁移步骤

### Step 1: 重写 KimiSessionManager

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

**当前问题**:
```python
# 当前导入 (需要移除)
from kaos.path import KaosPath
from kimi_agent_sdk import (
    ApprovalHandlerFn, ChatProviderError, Config, ConfigError,
    InvalidToolError, MaxStepsReached, Message, RunCancelled,
    Session, WireMessage,
)
from kimi_agent_sdk._aggregator import MessageAggregator
```

**目标架构** (参考 `sdk_wrapper.py`):
```python
# 新导入
from pathlib import Path
from claude_agent_sdk import ResultMessage, query
from claude_agent_sdk import (
    AssistantMessage, SystemMessage, TextBlock,
    ThinkingBlock, ToolResultBlock, ToolUseBlock, UserMessage
)
import structlog

# 使用 Path 替代 KaosPath
class SessionManager:
    def __init__(self, work_dir: Path, ...):
        self._work_dir = work_dir  # 标准 Path 类型
        
    async def single_prompt(self, prompt: str, ...) -> list[dict[str, Any]]:
        # 使用 claude-agent-sdk 的 query()
        generator = query(prompt=prompt, options=self.options)
        # 返回标准 dict 消息列表
```

**关键变更点**:
1. `KaosPath` → `pathlib.Path`
2. `kimi_agent_sdk.Session` → `claude_agent_sdk.query()`
3. `Message` → `dict[str, Any]`
4. `MessageAggregator` → 自定义或移除
5. `MaxStepsReached`, `RunCancelled` → 使用 DocuSwarm 统一异常

---

### Step 2: 迁移工具系统

**文件**: `autoBMAD/docuswarm/tools/sdk_adapter.py`

**当前代码**:
```python
from kimi_agent_sdk import ToolError, ToolOk, ToolReturnValue

def adapt_to_sdk(result: ToolResult) -> ToolReturnValue:
    if result.success:
        return ToolOk(output=...)
    else:
        return ToolError(output=..., message=...)
```

**目标代码**:
```python
# 移除 kimi_agent_sdk 依赖
# claude-agent-sdk 使用不同的工具返回格式
# 直接返回结构化 dict

def adapt_to_claude(result: ToolResult) -> dict[str, Any]:
    """将 ToolResult 转换为 Claude SDK 工具返回格式."""
    if result.success:
        return {
            "type": "tool_result",
            "content": result.result,
        }
    else:
        return {
            "type": "tool_result", 
            "content": {"error": result.error},
            "is_error": True,
        }
```

**文件**: `autoBMAD/docuswarm/tools/callable_tool_wrapper.py`

**当前代码**:
```python
from kimi_agent_sdk import CallableTool2, ToolReturnValue

class ToolResultCallableTool(CallableTool2[P], Generic[P]):
    @override
    async def __call__(self, params: P) -> ToolReturnValue:
        result = await self._execute(params)
        return adapt_to_sdk(result)
```

**目标代码**:
```python
# 移除 CallableTool2 基类
# 改为纯函数式工具

class ToolResultWrapper:
    """纯函数式工具包装器."""
    
    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        result = await self._execute(params)
        return adapt_to_claude(result)
        
    async def _execute(self, params: dict[str, Any]) -> ToolResult:
        raise NotImplementedError
```

---

### Step 3: 迁移 Agent 实现

**文件**: `autoBMAD/docuswarm/agents/independent.py`

**当前导入**:
```python
from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator
...
from kimi_agent_sdk import MaxStepsReached, RunCancelled
```

**目标导入**:
```python
# 使用标准 dict 替代 Message
Message = dict[str, Any]

# 使用 DocuSwarm 统一异常
from autoBMAD.docuswarm.exceptions import StepLimitExceeded, SessionCancelled

# 移除 MessageAggregator，使用简单列表收集
```

**文件**: `autoBMAD/docuswarm/agents/evaluator.py`

**当前导入**:
```python
from kimi_agent_sdk import Message
```

**目标导入**:
```python
# 使用标准 dict
Message = dict[str, Any]
```

---

### Step 4: 迁移其他模块

**文件**: `autoBMAD/docuswarm/llm/approval.py`

**当前**:
```python
from kimi_agent_sdk import ApprovalRequest
```

**目标**:
```python
# 定义本地 ApprovalRequest 类型或使用 dict
ApprovalRequest = dict[str, Any]
```

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

**当前**:
```python
from kaos.path import KaosPath
from kimi_agent_sdk import Message
```

**目标**:
```python
from pathlib import Path
Message = dict[str, Any]
```

---

### Step 5: 更新依赖声明文件

**pyproject.toml** (确认正确):
```toml
dependencies = [
    "langgraph>=0.2.50,<0.3.0",
    "langgraph-checkpoint-sqlite>=2.0.4,<3.0.0",
    "langchain>=0.3.0,<0.4.0",
    "langchain-core>=0.3.0,<0.4.0",
    "claude-agent-sdk>=0.1.0,<0.2.0",
    # 移除 kimi-agent-sdk 如果存在
    ...
]
```

**requirements.txt**:
```
# DocuSwarm Multi-Agent Orchestration System
# Production Dependencies
# Updated: 2026-03-25
# Project: DocuSwarm v2.0 (claude-agent-sdk architecture)
# Python: >=3.12.10

# === Core Framework ===
langgraph>=0.2.50,<0.3.0
langgraph-checkpoint-sqlite>=2.0.4,<3.0.0
langchain>=0.3.0,<0.4.0

# claude-agent-sdk - Claude SDK via Kimi Code API
claude-agent-sdk>=0.1.0,<0.2.0

# ... rest of dependencies
```

**requirements-dev.txt**:
```
# DocuSwarm Development Dependencies
# Updated: 2026-03-25
# Project: DocuSwarm v2.0 (claude-agent-sdk architecture)
# Python: >=3.12.10

# ========== Production Dependencies ==========
-r requirements.txt

# ... test dependencies

# ========== AI Agent SDK ==========
claude-agent-sdk>=0.1.38
```

---

## 4. 迁移后架构

```
DocuSwarm Architecture (Post-Migration)

┌─────────────────────────────────────────────────────────────┐
│                    CLI Layer (cli/)                         │
├─────────────────────────────────────────────────────────────┤
│                 Service Layer (cli/services)                │
├─────────────────────────────────────────────────────────────┤
│                   Agent Layer (agents/)                     │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ IndependentAgent│  │ EvaluatorAgent  │                   │
│  │  (uses dict)    │  │  (uses dict)    │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                            │
│           └────────┬───────────┘                            │
│                    │                                        │
├────────────────────┼────────────────────────────────────────┤
│                    ▼                                        │
│           SessionManager (llm/)                             │
│              (claude-agent-sdk)                             │
│         ┌─────────────────────┐                             │
│         │   SafeClaudeSDK     │                             │
│         │  (from sdk_wrapper) │                             │
│         └─────────────────────┘                             │
├─────────────────────────────────────────────────────────────┤
│                  Tools Layer (tools/)                       │
│              (Pure Functions + dict)                        │
├─────────────────────────────────────────────────────────────┤
│              Pipeline Layer (pipeline/)                     │
│                  (Path instead of KaosPath)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ claude-agent-sdk│
                    │  via Kimi Code  │
                    │     API         │
                    └─────────────────┘
```

---

## 5. 验证计划

### 5.1 静态检查

```bash
# 1. 运行依赖漂移分析器
python tools/dependency_analysis/dependency_drift_analyzer.py
# Expected: Drift Score = 0

# 2. 检查无 kimi-agent-sdk 导入
grep -r "from kimi_agent_sdk" autoBMAD/docuswarm || echo "PASS: No kimi imports"
grep -r "import kimi_agent_sdk" autoBMAD/docuswarm || echo "PASS: No kimi imports"

# 3. 检查无 kaos 导入
grep -r "from kaos" autoBMAD/docuswarm || echo "PASS: No kaos imports"
grep -r "import kaos" autoBMAD/docuswarm || echo "PASS: No kaos imports"
```

### 5.2 单元测试

```bash
# 运行所有测试
pytest tests/ -v --tb=short

# 关键测试
pytest tests/cli/test_commands_smoke.py -v
pytest tests/llm/ -v
pytest tests/agents/ -v
```

### 5.3 集成测试

```bash
# 新环境安装测试
python -m venv test_env
test_env\Scripts\activate
pip install -e .
python -c "from autoBMAD.docuswarm.llm.session_manager import SessionManager; print('OK')"
```

---

## 6. 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| SessionManager 重写引入 bug | 中 | 高 | 保留旧版本备份，全面测试 |
| Tool 格式不兼容 | 中 | 中 | 渐进式迁移，逐个验证 |
| 性能回归 | 低 | 中 | 基准测试对比 |
| 文档未更新 | 高 | 低 | 强制文档更新检查清单 |

---

## 7. 成功标准

- [ ] `dependency_drift_analyzer.py` 返回 Drift Score = 0
- [ ] 无 `kimi_agent_sdk` 导入
- [ ] 无 `kaos` 导入
- [ ] `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` 一致
- [ ] 所有测试通过
- [ ] 新环境安装验证通过
- [ ] CI/CD 检查通过

---

**方案维护**: 迁移完成后更新此文档状态为 "已完成"
