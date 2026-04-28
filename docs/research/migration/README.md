# DocuSwarm kimi-agent-sdk 完全移除报告

> **奥卡姆剃刀原则**: 如无必要，勿增实体  
> **决策**: 完全移除 kimi-agent-sdk，零向后兼容  
> **研究日期**: 2026-03-02

---

## 文档索引

| # | 文档 | 主题 | 说明 |
|---|------|------|------|
| 1 | [01-message-format-migration-report.md](01-message-format-migration-report.md) | Message 格式迁移 | 完全移除 Kimi Message，使用 Claude SDK 格式 |
| 2 | [02-tool-calling-mechanism-migration-report.md](02-tool-calling-mechanism-migration-report.md) | Tool 调用机制迁移 | 完全移除 CallableTool2，使用函数式工具 |
| 3 | [03-test-dependency-migration-report.md](03-test-dependency-migration-report.md) | 测试依赖迁移 | 完全移除 Kimi SDK mock，使用统一测试框架 |
| 4 | [04-exception-handling-migration-report.md](04-exception-handling-migration-report.md) | 异常处理迁移 | 完全移除 Kimi SDK 异常，使用统一异常体系 |

---

## 执行摘要

### 总体评估

| 维度 | 评估 |
|-----|------|
| **总工作量** | 4-6 周 |
| **影响文件数** | 47+ 个文件 |
| **技术可行性** | ✅ 可行 |
| **实施风险** | 🟡 中（需要全面测试） |
| **策略** | **完全移除，零兼容** |

### 核心决策

```
迁移架构
═══════════════════════════════════════════════════════════════════

迁移前                          迁移后
─────────────────────────────────────────────────────────────────
┌─────────────────┐             ┌─────────────────┐
│  Kimi SDK       │      →      │  Claude SDK     │
│  (完全移除)      │             │  (唯一SDK)       │
└────────┬────────┘             └────────┬────────┘
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│  Message        │             │  ResultMessage  │
│  CallableTool2  │      →      │  FunctionTool   │
│  MaxStepsReached│             │  SDKResult      │
└─────────────────┘             └─────────────────┘
```

**不兼容内容（已移除）**:
- ❌ UnifiedMessage 适配器层
- ❌ CallableTool2 兼容包装器
- ❌ Kimi SDK 异常别名
- ❌ 废弃警告机制
- ❌ 双轨制支持

---

## 各迁移报告摘要

### 1. Message 格式迁移

**核心变更**: 完全移除 Kimi SDK `Message` 类

**迁移前**:
```python
from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator

async def _call_llm(...) -> list[Message]:
    aggregator = MessageAggregator()
    async for wire_msg in session.prompt(prompt):
        for msg in aggregator.feed(wire_msg):
            yield msg
```

**迁移后**:
```python
from autoBMAD.docuswarm.llm.response import ResponseMessage

async def _call_llm(...) -> list[ResponseMessage]:
    result = await sdk_wrapper.execute(prompt)
    return result.messages
```

**移除内容**:
- `kimi_agent_sdk.Message` 导入
- `MessageAggregator` 使用
- `WireMessage` 处理

---

### 2. Tool 调用机制迁移

**核心变更**: 完全移除 `CallableTool2` 类继承模型

**迁移前**:
```python
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError

class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    name = "create_deliverable"
    params = CreateDeliverableParams
    
    async def __call__(self, params) -> ToolReturnValue:
        return ToolOk(output="...")
```

**迁移后**:
```python
from autoBMAD.docuswarm.models.tool import ToolResult

async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    return ToolResult(success=True, output="...")
```

**移除内容**:
- `CallableTool2` 基类
- `ToolOk` / `ToolError` 返回类型
- 类继承模型
- YAML 工具配置

---

### 3. 测试依赖迁移

**核心变更**: 完全移除 `kimi-agent-sdk` mock

**迁移前**:
```python
# conftest.py
@pytest.fixture(autouse=True)
def mock_kimi_sdk():
    with patch.dict("sys.modules", {"kimi_agent_sdk": MagicMock()}):
        yield
```

**迁移后**:
```python
# conftest.py
@pytest.fixture
def mock_sdk_result():
    return MockSDKResult(
        success=True,
        content="Mock response",
        messages=[]
    )
```

**移除内容**:
- 全局 `autouse` kimi_sdk mock
- `Message` mock 对象
- `Session` mock 类
- `MessageAggregator` mock

---

### 4. 异常处理迁移

**核心变更**: 完全移除 Kimi SDK 异常类

**迁移前**:
```python
from kimi_agent_sdk import (
    MaxStepsReached,
    RunCancelled,
    ChatProviderError,
    ConfigError,
)

try:
    await session.prompt(prompt)
except MaxStepsReached:
    handle_max_steps()
except RunCancelled:
    handle_cancelled()
```

**迁移后**:
```python
from autoBMAD.docuswarm.exceptions import (
    StepLimitExceeded,
    SessionCancelled,
    ConnectionError,
    ConfigurationError,
)

try:
    await sdk_wrapper.execute(prompt)
except StepLimitExceeded:
    handle_max_steps()
except SessionCancelled:
    handle_cancelled()
```

**移除内容**:
- `MaxStepsReached` → 使用 `StepLimitExceeded`
- `RunCancelled` → 使用 `SessionCancelled`
- `ChatProviderError` → 使用 `ConnectionError`
- `ConfigError` → 使用 `ConfigurationError`
- `InvalidToolError` → 使用 `ToolExecutionError`

---

## 文件删除清单

以下文件/目录将**完全删除**:

| 路径 | 说明 |
|-----|------|
| `llm/kimi_session_manager.py` | Kimi SDK SessionManager |
| `agents/independent.py` 中的 Kimi 相关代码 | Message/MessageAggregator 导入 |
| `tools/*` 中的 CallableTool2 类 | 工具类继承实现 |
| `tests/conftest.py` 中的 Kimi mock | 全局 mock 配置 |
| `exceptions.py` 中的兼容代码 | Kimi 异常别名 |

---

## 实施路线图

### 阶段 1: 基础设施 (Week 1)

```
Week 1: 核心替换
─────────────────────────────────────────────────────────────────
□ 移除 llm/session_manager.py 中的 Kimi SDK 导入
□ 移除 agents/independent.py 中的 Message/MessageAggregator
□ 移除 agents/evaluator.py 中的 Message 导入
□ 创建纯函数式工具替代 CallableTool2
□ 更新异常导入
```

### 阶段 2: 工具迁移 (Week 2)

```
Week 2: 工具重构
─────────────────────────────────────────────────────────────────
□ 重写 tools/create_deliverable.py - 函数式
□ 重写 tools/create_document_set.py - 函数式
□ 重写 tools/read_docs_file.py - 函数式
□ 重写 tools/list_docs_files.py - 函数式
□ 重写 tools/update_docs_file.py - 函数式
□ 重写 tools/update_context.py - 函数式
□ 删除 YAML 工具配置
```

### 阶段 3: 测试更新 (Week 3)

```
Week 3: 测试重构
─────────────────────────────────────────────────────────────────
□ 重写 conftest.py - 移除 Kimi mock
□ 更新 test_session_manager.py
□ 更新 test_independent_agent.py
□ 更新 test_evaluator.py
□ 更新 test_tool_result_extractor.py
□ 更新所有集成测试
```

### 阶段 4: 清理验证 (Week 4)

```
Week 4: 验证与清理
─────────────────────────────────────────────────────────────────
□ 删除所有 Kimi SDK 相关文件
□ 运行完整测试套件
□ 端到端测试
□ 性能基准测试
□ 文档最终更新
```

---

## 风险汇总

| 风险项 | 影响 | 缓解措施 |
|-------|------|---------|
| Message 格式不兼容 | 🔴 高 | 全面代码审查 |
| Tool 机制差异 | 🔴 高 | 完整功能测试 |
| 测试覆盖不足 | 🔴 高 | 增加集成测试 |
| 异常映射错误 | 🟡 中 | 异常处理测试 |

**无向后兼容风险** - 由于是完整移除，不存在兼容性问题。

---

## 代码变更统计

| 类型 | 数量 |
|-----|------|
| 删除文件 | 8+ |
| 修改文件 | 25+ |
| 删除代码行 | ~2000 |
| 新增代码行 | ~1500 |
| 测试用例更新 | 100+ |

---

## 验证检查清单

迁移完成后，验证以下检查点:

- [ ] 项目中无 `kimi_agent_sdk` 导入
- [ ] 项目中无 `MessageAggregator` 使用
- [ ] 项目中无 `CallableTool2` 继承
- [ ] 项目中无 `ToolOk` / `ToolError` 使用
- [ ] 项目中无 `MaxStepsReached` 等 Kimi 异常
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 端到端场景测试通过
- [ ] 性能无显著下降

---

## 下一步行动

1. **创建分支**: `feature/remove-kimi-sdk`
2. **分配任务**: 根据 4 份报告分配实施团队
3. **设置里程碑**: 
   - Week 1: 基础设施完成
   - Week 2: 工具迁移完成
   - Week 3: 测试更新完成
   - Week 4: 全部完成

---

*报告完成日期: 2026-03-02*  
*文档版本: 2.0 (完全移除版)*
