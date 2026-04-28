# DocuSwarm 依赖漂移深度研究报告

**研究日期**: 2026-03-25  
**研究范围**: F1. 依赖声明与真实运行依赖漂移 (P0级别)  
**研究方法**: 静态代码分析、依赖追踪、架构对比  
**报告状态**: 完成

---

## 执行摘要

### 核心发现

DocuSwarm 项目存在**严重的依赖漂移问题**，已达到 P0 级别：

| 指标 | 数值 | 严重程度 |
|------|------|----------|
| 依赖漂移评分 | **85/100** | CRITICAL |
| 使用 kimi-agent-sdk 的文件数 | **7** | CRITICAL |
| 使用 kaos.path 的文件数 | **3** | HIGH |
| 使用 claude-agent-sdk 的文件数 | 6 | 参考 |

### 问题本质

项目声明的依赖 (`pyproject.toml`) 与实际代码运行的依赖之间存在**根本性不一致**：

- **声明世界**: `claude-agent-sdk>=0.1.0,<0.2.0`
- **运行世界**: `kimi-agent-sdk` + `kaos.path`

这导致：
1. 新环境按官方安装步骤无法运行
2. CI/CD 流程可能基于错误依赖声明
3. 开发者文档与实际代码严重不符

---

## 详细分析

### 1. 依赖声明现状

#### 1.1 pyproject.toml (官方声明)
```toml
dependencies = [
    "langgraph>=0.2.50,<0.3.0",
    "langgraph-checkpoint-sqlite>=2.0.4,<3.0.0",
    "langchain>=0.3.0,<0.4.0",
    "langchain-core>=0.3.0,<0.4.0",
    "claude-agent-sdk>=0.1.0,<0.2.0",  # <-- 唯一声明的SDK
    ...
]
```

#### 1.2 requirements.txt
```
# DocuSwarm Multi-Agent Orchestration System
# Project: DocuSwarm v2.0 (claude-agent-sdk architecture)
claude-agent-sdk>=0.1.0,<0.2.0
```

#### 1.3 requirements-dev.txt
```
# Project: DocuSwarm v1.0 (kimi-agent-sdk architecture)  # <-- 注释仍写kimi!
...
# ========== AI Agent SDK ==========
claude-agent-sdk>=0.1.38  # <-- 实际保留的是claude
```

**问题**: `requirements-dev.txt` 第3行仍写着 "kimi-agent-sdk architecture"

---

### 2. 实际代码依赖分析

#### 2.1 kimi-agent-sdk 使用情况 (7个文件)

| 文件路径 | 导入内容 | 行号 | 影响模块 |
|----------|----------|------|----------|
| `agents/evaluator.py` | `Message` | 21 | 评估Agent |
| `agents/independent.py` | `Message`, `MessageAggregator`, `MaxStepsReached`, `RunCancelled` | 23-24, 288-289 | 独立Agent |
| `llm/approval.py` | `ApprovalRequest` | 29 | 审批系统 |
| `llm/session_manager.py` | `ApprovalHandlerFn`, `ChatProviderError`, `Config`, `ConfigError`, `InvalidToolError`, `MaxStepsReached`, `Message`, `RunCancelled`, `Session`, `WireMessage`, `MessageAggregator` | 26-38 | 会话管理 |
| `pipeline/orchestrator.py` | `Message` | 17 | 编排器 |
| `tools/callable_tool_wrapper.py` | `CallableTool2`, `ToolReturnValue` | 11 | 工具包装器 |
| `tools/sdk_adapter.py` | `ToolError`, `ToolOk`, `ToolReturnValue` | 12 | SDK适配器 |

#### 2.2 kaos.path 使用情况 (3个文件)

| 文件路径 | 导入内容 | 行号 | 用途 |
|----------|----------|------|------|
| `agents/independent.py` | `KaosPath` | 565, 695 | 路径处理 |
| `llm/session_manager.py` | `KaosPath` | 25 | 工作目录 |
| `pipeline/orchestrator.py` | `KaosPath` | 16 | 路径处理 |

#### 2.3 claude-agent-sdk 使用情况 (6个文件)

通过对比分析，发现以下文件正确使用了 `claude-agent-sdk`：
- `autoBMAD/epic_automation/sdk_wrapper.py` (作为参考架构)
- 其他工具文件 (符合声明依赖)

---

### 3. 漂移根因分析

#### 3.1 架构迁移未完成

根据文档历史追踪，项目计划从 `kimi-agent-sdk` 迁移到 `claude-agent-sdk`：

```
迁移计划 (已完成):
- EPIC-16: SDK Wrapper 方案
- EPIC-17: Message 格式迁移
- EPIC-18: Tool Calling 迁移  
- EPIC-19: 测试依赖迁移
- EPIC-20: 异常处理迁移
```

**实际情况**: 核心运行时模块 (`session_manager.py`, `agents/*.py`) 未完成迁移

#### 3.2 迁移停滞的关键点

1. **KimiSessionManager 类** (`llm/session_manager.py:49-618`)
   - 完整依赖 `kimi_agent_sdk.Session`, `Config`, `Message`, `WireMessage`
   - 使用 `kaos.path.KaosPath` 作为工作目录类型
   - 618行代码需要重写

2. **工具系统** (`tools/`)
   - `CallableTool2` 基类依赖 `kimi_agent_sdk`
   - `ToolOk`, `ToolError`, `ToolReturnValue` 类型依赖
   - 需要迁移到纯函数式工具

3. **Agent 实现** (`agents/`)
   - `IndependentAgent` 使用 `MessageAggregator`
   - `EvaluatorAgent` 使用 `kimi_agent_sdk.Message`

#### 3.3 为什么 claude-agent-sdk 是正确的方向

参考 `autoBMAD/epic_automation/sdk_wrapper.py` 架构：

```python
# 正确的架构模式 (来自 sdk_wrapper.py)
from claude_agent_sdk import ResultMessage, query
from claude_agent_sdk import (
    AssistantMessage, SystemMessage, TextBlock,
    ThinkingBlock, ToolResultBlock, ToolUseBlock, UserMessage
)

class SafeClaudeSDK:
    """基于 claude-agent-sdk 的安全包装器"""
    async def execute(self) -> bool:
        # 使用 claude-agent-sdk 的 query() 函数
        generator = query(prompt=self.prompt, options=self.options)
        ...
```

**优势**:
- 统一的 SDK 事实源
- 与 `epic_automation` 项目一致
- 通过 Kimi Code API 工作
- 更简洁的 API 设计

---

### 4. 影响评估

#### 4.1 直接影响

| 场景 | 影响 | 概率 |
|------|------|------|
| 新开发者按 README 安装 | 运行失败 | 100% |
| CI/CD 按 pyproject.toml 安装 | 测试可能通过(mock)但实际部署失败 | 80% |
| 生产环境部署 | 需要手动安装 kimi-agent-sdk | 100% |
| 依赖审计 | 安全合规问题 | 100% |

#### 4.2 技术债务

```
当前状态:
├── 声明依赖: claude-agent-sdk (正确)
├── 实际依赖: kimi-agent-sdk (错误)
├── 混合状态: 部分文件用 claude, 核心模块用 kimi
└── 文档漂移: README/文档声称已移除 kimi

债务累积:
- 每新增一个 kimi-agent-sdk 导入 +10 债务点
- 每新增一个使用 kimi 的模块 +5 债务点
- 当前总债务评分: 85 (CRITICAL)
```

---

## 解决方案

### 方案 A: 彻底迁移 (推荐)

**目标**: 统一使用 `claude-agent-sdk`，完全移除 `kimi-agent-sdk`

**步骤**:

#### Phase 1: 核心模块迁移 (1-2天)

1. **重写 KimiSessionManager** (`llm/session_manager.py`)
   - 使用 `claude-agent-sdk` 替代 `kimi_agent_sdk.Session`
   - 使用标准 `pathlib.Path` 替代 `kaos.path.KaosPath`
   - 参考 `autoBMAD/epic_automation/sdk_wrapper.py`

2. **迁移工具系统** (`tools/`)
   - 移除 `CallableTool2` 基类
   - 移除 `ToolOk`, `ToolError`, `ToolReturnValue` 适配
   - 迁移到纯函数式工具

3. **迁移 Agent 实现** (`agents/`)
   - 移除 `Message`, `MessageAggregator` 依赖
   - 使用标准 `dict[str, Any]` 消息格式

#### Phase 2: 依赖清理 (半天)

1. 更新 `pyproject.toml` - 确认只声明 `claude-agent-sdk`
2. 更新 `requirements.txt` - 清理注释
3. 更新 `requirements-dev.txt` - 移除 "kimi-agent-sdk architecture" 注释
4. 更新 README - 确保描述与实际一致

#### Phase 3: 验证 (1天)

1. 运行全套测试
2. 验证新环境安装流程
3. 添加 CI 检查防止未来漂移

### 方案 B: 回退声明 (临时方案)

**目标**: 暂时将声明回退到 `kimi-agent-sdk` 以恢复一致性

**步骤**:
1. 修改 `pyproject.toml` 声明 `kimi-agent-sdk`
2. 更新文档说明当前实际依赖
3. 制定迁移计划并执行

**缺点**: 继续累积技术债务，推迟问题解决

### 方案 C: 双 SDK 支持 (不推荐)

**目标**: 同时支持两种 SDK

**缺点**:
- 增加维护复杂度
- 违背单一事实源原则
- 长期债务更高

---

## 推荐实施计划

### 优先级: P0

| 任务 | 负责人 | 预估工时 | 依赖 |
|------|--------|----------|------|
| 重写 llm/session_manager.py | TBD | 4h | 无 |
| 迁移 tools/sdk_adapter.py | TBD | 2h | session_manager |
| 迁移 tools/callable_tool_wrapper.py | TBD | 2h | sdk_adapter |
| 迁移 agents/independent.py | TBD | 3h | session_manager |
| 迁移 agents/evaluator.py | TBD | 2h | session_manager |
| 迁移 llm/approval.py | TBD | 1h | session_manager |
| 迁移 pipeline/orchestrator.py | TBD | 2h | session_manager |
| 清理依赖文件 | TBD | 1h | 所有迁移完成 |
| 验证测试 | TBD | 4h | 依赖清理 |
| **总计** | | **21h (~3天)** | |

### 迁移检查清单

- [ ] `llm/session_manager.py` 不再导入 `kimi_agent_sdk`
- [ ] `llm/session_manager.py` 不再导入 `kaos.path`
- [ ] `agents/independent.py` 不再导入 `kimi_agent_sdk`
- [ ] `agents/evaluator.py` 不再导入 `kimi_agent_sdk`
- [ ] `llm/approval.py` 不再导入 `kimi_agent_sdk`
- [ ] `pipeline/orchestrator.py` 不再导入 `kimi_agent_sdk`
- [ ] `tools/sdk_adapter.py` 不再导入 `kimi_agent_sdk`
- [ ] `tools/callable_tool_wrapper.py` 不再导入 `kimi_agent_sdk`
- [ ] `requirements-dev.txt` 注释更新
- [ ] 全量测试通过
- [ ] 新环境安装验证通过

---

## 监控建议

### CI/CD 检查

添加 GitHub Actions 步骤:

```yaml
- name: Check Dependency Drift
  run: |
    python tools/dependency_analysis/dependency_drift_analyzer.py
    if [ $? -ne 0 ]; then
      echo "ERROR: Dependency drift detected!"
      exit 1
    fi
```

### 代码审查检查点

- [ ] 新代码是否引入 `kimi_agent_sdk` 导入
- [ ] 新代码是否引入 `kaos.path` 导入
- [ ] 依赖文件修改是否一致

---

## 附录

### A. 工具使用说明

```bash
# 运行依赖漂移分析
python tools/dependency_analysis/dependency_drift_analyzer.py

# 输出位置
docs/research/dependency_drift_analysis.json
```

### B. 参考架构

```
autoBMAD/epic_automation/sdk_wrapper.py
├── 使用 claude-agent-sdk
├── 安全包装器模式
└── 正确的 SDK 封装架构
```

### C. 相关文档

- [评估报告](../../evaluation/2026-03-25-docuswarm-deep-evaluation-report.md)
- [迁移研究](../migration/README.md)
- [SDK Wrapper 参考](../../../autoBMAD/epic_automation/sdk_wrapper.py)

---

**报告生成时间**: 2026-03-25  
**分析工具版本**: 1.0.0  
**下次复查**: 迁移完成后
