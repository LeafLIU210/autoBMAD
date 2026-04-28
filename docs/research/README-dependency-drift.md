# DocuSwarm 依赖漂移研究报告

**报告日期**: 2026-03-25  
**研究类型**: 深度技术分析  
**严重程度**: P0 - CRITICAL  
**漂移评分**: 85/100

---

## 问题概述

DocuSwarm 项目存在**严重的依赖声明与实际运行依赖漂移问题**。

### 核心矛盾

| 维度 | 声明状态 | 实际状态 |
|------|----------|----------|
| pyproject.toml | `claude-agent-sdk` | - |
| requirements.txt | `claude-agent-sdk` | - |
| 代码实际导入 | - | `kimi-agent-sdk` + `kaos.path` |

### 关键数据

- **185** 个 Python 文件被分析
- **7** 个文件使用 `kimi-agent-sdk`
- **3** 个文件使用 `kaos.path`
- **0** 个文件完成迁移

---

## 受影响的核心模块

### 必须修复的文件 (7个)

```
autoBMAD/docuswarm/
├── agents/
│   ├── evaluator.py          # Message
│   └── independent.py        # Message, MessageAggregator, KaosPath
├── llm/
│   ├── approval.py           # ApprovalRequest  
│   └── session_manager.py    # [CRITICAL] 完整SDK依赖 + KaosPath
├── pipeline/
│   └── orchestrator.py       # Message, KaosPath
└── tools/
    ├── callable_tool_wrapper.py  # CallableTool2
    └── sdk_adapter.py        # ToolOk, ToolError
```

### 需要更新的配置 (3个)

- `pyproject.toml` - 声明正确，无需修改
- `requirements.txt` - 声明正确，无需修改
- `requirements-dev.txt` - 需移除 "kimi-agent-sdk architecture" 注释

---

## 根因分析

1. **架构迁移未完成**: 从 `kimi-agent-sdk` 到 `claude-agent-sdk` 的迁移在核心模块停滞
2. **KimiSessionManager**: 618行代码深度绑定 `kimi_agent_sdk.Session`
3. **工具系统**: 基于 `CallableTool2` 类继承模型需要重写
4. **Agent实现**: 使用 `MessageAggregator` 等 SDK 特定类型

---

## 参考架构

**正确架构**: `autoBMAD/epic_automation/sdk_wrapper.py`

```python
from claude_agent_sdk import ResultMessage, query
from claude_agent_sdk import (
    AssistantMessage, SystemMessage, TextBlock,
    ThinkingBlock, ToolResultBlock, ToolUseBlock, UserMessage
)

class SafeClaudeSDK:
    """基于 claude-agent-sdk 的安全包装器"""
    async def execute(self) -> bool:
        generator = query(prompt=self.prompt, options=self.options)
        # ... 处理响应
```

---

## 解决方案

### 推荐方案: 彻底迁移 (3天)

**Phase 1: 核心模块迁移** (1-2天)
1. 重写 `llm/session_manager.py` - 使用 `claude-agent-sdk`
2. 迁移 `tools/` - 移除 `CallableTool2`，改用纯函数
3. 迁移 `agents/` - 使用 `dict[str, Any]` 替代 `Message`

**Phase 2: 依赖清理** (半天)
1. 更新 `requirements-dev.txt` 注释
2. 验证所有依赖文件一致性

**Phase 3: 验证** (1天)
1. 运行全量测试
2. 验证新环境安装
3. 添加 CI 检查

---

## 工具使用

### 1. 依赖漂移分析

```bash
python tools/dependency_analysis/dependency_drift_analyzer.py
```

**输出**:
- 控制台报告
- `docs/research/dependency_drift_analysis.json`

### 2. 迁移进度跟踪

```bash
python tools/dependency_analysis/migration_tracker.py
python tools/dependency_analysis/migration_tracker.py --check  # CI模式
```

---

## 文档清单

### 研究报告

| 文档 | 路径 | 内容 |
|------|------|------|
| 主研究报告 | [docs/research/dependency-drift-2026-03-25/README.md](./dependency-drift-2026-03-25/README.md) | 完整分析 |
| 迁移方案 | [docs/research/dependency-drift-2026-03-25/migration-plan.md](./dependency-drift-2026-03-25/migration-plan.md) | 实施计划 |
| 分析数据 | [docs/research/dependency_drift_analysis.json](./dependency_drift_analysis.json) | JSON数据 |

### 工具脚本

| 工具 | 路径 | 用途 |
|------|------|------|
| 漂移分析器 | `tools/dependency_analysis/dependency_drift_analyzer.py` | 分析依赖漂移 |
| 迁移跟踪器 | `tools/dependency_analysis/migration_tracker.py` | 跟踪迁移进度 |

---

## 成功标准

- [ ] Drift Score = 0
- [ ] 无 `kimi_agent_sdk` 导入
- [ ] 无 `kaos` 导入
- [ ] 所有测试通过
- [ ] 新环境安装验证通过
- [ ] CI 检查通过

---

## 后续行动

1. **立即**: 确认迁移优先级和资源分配
2. **第1天**: 开始 `session_manager.py` 重写
3. **第2天**: 迁移工具和 Agent 模块
4. **第3天**: 验证和清理

---

**报告维护**: 本报告将随迁移进度更新
