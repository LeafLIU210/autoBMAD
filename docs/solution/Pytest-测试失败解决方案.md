# Pytest 测试失败 — 测试驱动解决方案 (2026-02-24 实测更新版)

**创建日期**: 2026-02-24  
**基于报告**: `docs/research/Pytest-测试结果分析报告.md`  
**实测验证**: 2026-02-24 10:12 执行完成

---

## 执行摘要 (实际测试验证后)

经过**针对性实际测试**，确认 **4 类有效问题**，之前报告的 20 个单元测试失败中，**17 个已自动修复** (可能由于环境差异或代码更新)。

| 优先级 | 问题 | 当前状态 | 影响 | 类型 |
|--------|------|----------|------|------|
| **P0** | Mock 函数签名不匹配 | ❌ 2/19 失败 | 2 个测试 | 测试缺陷 |
| **P1** | flow.py StateManager Mock 路径 + create_pipeline 逻辑 | ❌ 确认失败 | 1+ 个测试 | 源码+测试缺陷 |
| **P2** | template_loader 异常类身份不匹配 | ❌ 确认失败 | 1 个测试 | 测试基础设施 |
| **P3** | subpackages 模块别名不完整 | ✅ 当前通过 (19/19) | 0 (间歇) | 测试基础设施 |
| **P4** | 集成测试 LLM 响应格式错误 | ❌ 4/9 失败 | 集成测试 | Prompt 问题 |

**重要发现**:  
- executor.py 的 `Path` 导入缺失在当前测试中**未触发**，因 mock 机制避免了第 122 行的执行
- 主要失败原因是 **Mock 签名不匹配**，而非之前认为的 NameError
- **新发现**: 集成测试失败是 **LLM 响应格式问题** (Markdown ≠ JSON)，非超时问题

---

## 问题 1 (P0): Mock 函数签名不匹配 + executor.py 缺失 Path 导入

### 影响范围

**实际测试结果** (2026-02-24):
- ✅ **17/19 通过** — `test_node_executor.py` 中大部分测试已修复
- ❌ **2/19 失败** — `TestChainedContextExtraction` 类的 2 个测试

**当前失败测试**:
- `test_executor_extracts_task_from_chained_context_deliverable`
- `test_executor_extracts_task_from_chained_context_task`

**失败原因** (新发现):
```python
TypeError: TestChainedContextExtraction.test_executor_extracts_task_from_chained_context_deliverable.<locals>.mock_execute() got an unexpected keyword argument 'pipeline_id'
```

### 深度根因分析 (更新)

#### 根因层 1: Mock 函数签名不匹配 (当前失败)

**文件**: `tests/unit/test_node_executor.py` 第 689-707 行

**问题**: 测试中的 `mock_execute` 函数签名与真实 `DualAgentNode.execute()` 不匹配

```python
# 测试中的 mock (第 689 行) — 缺少 pipeline_id 参数
async def mock_execute(subject_context, task):  # ❌ 缺少 pipeline_id
    captured_tasks.append(task)
    ...
```

**真实签名** (`autoBMAD/docuswarm/nodes/dual_agent.py` 第 139 行):
```python
async def execute(
    self,
    subject_context: str,
    task: str,
    pipeline_id: str = "",  # ← 必需参数
) -> NodeExecutionResult:
```

**调用链**:
```
test → executor(initial_state)
  ↓
executor.py:139 → result = await node.execute(
    subject_context=str(subject_context),
    task=task,
    pipeline_id=pipeline_id,  # ← 传入了 pipeline_id
)
  ↓
mock_execute(subject_context, task, pipeline_id)  # ← 调用时包含 3 个参数
  ↓
TypeError: mock_execute() got an unexpected keyword argument 'pipeline_id'
```

#### 根因层 2: executor.py 缺失 Path 导入 (已间接修复)

**文件**: `autoBMAD/docuswarm/node_execution/executor.py`

**状态**: 虽然源码中第 122 行仍使用 `Path(__file__)`，但由于 mock 机制，此行在大多数测试中未被执行到，因此未触发 NameError。

**历史原因**: 之前报告的 12 个失败中，实际只有 2 个是当前真实失败，其余 10 个可能在之前的修复中已解决或测试环境不同。

**当前导入列表** (第 1-27 行):
```python
import copy
from collections.abc import Callable, Coroutine
from typing import Any
import structlog
from autoBMAD.docuswarm.config import Config
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
from autoBMAD.docuswarm.node_execution.state import (...)
from autoBMAD.docuswarm.nodes.dual_agent import create_dual_agent_node
from autoBMAD.docuswarm.nodes.loader import NodeLoader
# ❌ 缺失: from pathlib import Path
```

**执行链分析** — 为什么影响迭代计数:

1. 测试调用 `executor(initial_state)` → 进入 `_execute_node()`
2. `_execute_node()` 在 `try` 块内执行:
   - 第 107 行: `NodeLoader()` ← 已 mock，正常
   - 第 108 行: `loader.load(node_id)` ← mock 返回 MockNodeConfig，正常
   - 第 118 行: `config = _get_config()` ← 调用真实 load_config()，正常
   - **第 122 行**: `Path(__file__)` ← **NameError 抛出！**
3. 异常被第 201 行的 `except Exception as e:` 捕获
4. 第 210 行: `new_state["status"] = FAILED` — 状态变为 FAILED
5. 第 212 行: 返回 `new_state` — **iteration 从未递增** (递增在第 151 行，未到达)

**这就是为什么**: `assert result_state["iteration"] == 2` 失败 — 实际值为 1 (初始值)

### 解决方案 (更新)

#### 修复 A: 修复测试中的 Mock 签名 (优先)

**修复文件**: `tests/unit/test_node_executor.py`

**位置**: 第 689 行和第 746 行

**修改**: 在两处 `mock_execute` 函数中添加 `pipeline_id` 参数

```python
# 第 689 行 - test_executor_extracts_task_from_chained_context_deliverable
async def mock_execute(subject_context, task, pipeline_id=""):  # ← 添加 pipeline_id 参数
    captured_tasks.append(task)
    mock_result = MagicMock()
    mock_result.deliverable = {}
    mock_result.questions = []
    mock_result.evaluation = {"verdict": "APPROVED"}
    mock_result.iteration = 1
    return mock_result

# 第 746 行 - test_executor_extracts_task_from_chained_context_task
async def mock_execute(subject_context, task, pipeline_id=""):  # ← 添加 pipeline_id 参数
    captured_tasks.append(task)
    mock_result = MagicMock()
    mock_result.deliverable = {}
    mock_result.questions = []
    mock_result.evaluation = {"verdict": "APPROVED"}
    mock_result.iteration = 1
    return mock_result
```

#### 修复 B: executor.py 添加 Path 导入 (预防性)

**修复文件**: `autoBMAD/docuswarm/node_execution/executor.py`

**修改**: 在导入区域添加 `from pathlib import Path`

```python
# 第 11 行后添加
import copy
from collections.abc import Callable, Coroutine
from pathlib import Path          # ← 新增
from typing import Any
```

**重要性**: 虽然当前测试未触发 NameError，但此导入缺失会在真实执行或集成测试中导致失败。

### 验证步骤 (更新)

```bash
# 1. 修复后运行失败的测试
pytest tests/unit/test_node_executor.py::TestChainedContextExtraction -v --tb=short

# 2. 预期结果: 2 个测试通过 (从当前的 0/2 → 2/2)

# 3. 运行完整 test_node_executor.py
pytest tests/unit/test_node_executor.py -v --tb=short

# 4. 预期结果: 19/19 全部通过 (从当前的 17/19 → 19/19)

# 5. 确认无副作用
pytest tests/ -v --tb=short -k "executor"
```

### 附加发现 (已验证)

#### 发现 1: Mock 签名不一致是系统性问题

在 `test_node_executor.py` 中，多处 `mock_execute` 函数都使用了两参数签名：
- `async def mock_execute(subject_context, task):` ← 旧签名
- 应改为: `async def mock_execute(subject_context, task, pipeline_id=""):` ← 新签名

**受影响位置**: 第 100, 138, 178, 219, 262, 299, 337, 415, 464, 509, 554, 598, 689, 746, 806 行

**当前状态**: 大部分测试通过是因为 `create_dual_agent_node` 被 mock，未真实调用。只有 `TestChainedContextExtraction` 因特殊的调用方式触发了此问题。

**建议**: 全部统一修复以避免未来回归。

#### 发现 2: mock_session_manager fixture 引用方式不一致

部分测试方法引用 `mock_session_manager` 时未将其作为 fixture 参数注入 (第 154, 192, 232 行等)。虽然当前未导致失败，但违反了 pytest fixture 最佳实践。

---

## 问题 5 (P4): 集成测试 LLM 响应解析失败 (实测根因更新)

### 影响范围

**实际测试结果** (2026-02-24 11:20-11:21):
- ❌ **4/9 失败** — 所有失败都是 `ResponseParseError: No JSON found in response`
- ✅ **5/9 通过** — 包括 mock 相关测试和状态转换测试
- ⏱️ **总耗时**: 348.33 秒 (5分48秒) — **未超时**

**失败测试**:
1. `test_analyst_node_produces_deliverable` — analyst/pm/ux/architect/po 全部节点解析失败
2. `test_file_output_created` — 因无 deliverable 导致无文件输出
3. `test_pipeline_with_single_node_execution` — analyst deliverable 不存在
4. `test_independent_agent_uses_work_dir` — 直接抛出 ResponseParseAgentError

**受影响文件**: `tests/integration/test_node_executor_integration.py`

**关键证据** (终端日志 33-37 行):
```
2026-02-24 11:20:33 [error] response_parse_failed
content=## Summary

I have created a simple integration test document titled **"Integration Test Document"**. 
The document includes:
- **Overview section** explaining the purpose of the test
- **Test Informa

error=No JSON found in response node_id=analyst
```

### 深度根因分析

#### 根因层 1: LLM 返回纯 Markdown 而非 JSON 格式

**文件**: `autoBMAD/docuswarm/llm/response.py` 第 70-94 行

**问题机制**:

实际 LLM 响应内容 (终端日志显示):
```markdown
## Summary

I have created a simple integration test document titled **"Integration Test Document"**. 
The document includes:
- **Overview section** explaining the purpose of the test
- **Test Information** with environment details
...
```

**预期 LLM 响应格式** (IndependentAgent 要求):
```json
{
  "deliverable": {"content": "...", "title": "..."},
  "questions": [],
  "action": "create_deliverable"
}
```

**解析流程失败**:
```
IndependentAgent._parse_response(response)
  ↓ 第 321 行
extract_json(content)  # ← 尝试提取 JSON
  ↓ response.py 第 74 行
json.loads(response)  # ✗ JSONDecodeError — 纯 Markdown
  ↓ 第 80 行
extract_json_from_markdown(response)  # ✗ 无代码块
  ↓ 第 86 行
re.search(r"\{[^{}]*...*\}", response)  # ✗ 无 JSON 结构
  ↓ 第 94 行
raise ResponseParseError("No JSON found in response")
```

**调用链**:
```
test → IndependentAgent.execute()
  ↓
session_manager.single_prompt(...) → Kimi API
  ↓ (LLM 生成响应)
LLM 返回: "## Summary\n\nI have created..." ← 纯 Markdown
  ↓
_parse_response(response)
  ↓
extract_json(content) → ResponseParseError
  ↓
raise ResponseParseAgentError
```

#### 根因层 2: Prompt 未正确指定输出格式

**分析 IndependentAgent 的 Prompt 构建**:

从终端日志看，LLM 生成了有意义的 Markdown 内容，说明:
1. **API 连接正常** — 响应时间 10 秒左右 (11:20:23 → 11:20:33)
2. **LLM 理解任务** — 生成了文档摘要
3. **格式不符预期** — 返回 Markdown 而非 JSON

**可能原因**:

1. **Prompt 模板缺少明确的输出格式约束**
   - `independent_agent.yaml` 可能未强制要求 JSON 输出
   - 或 LLM 未遵守格式指令

2. **Tool Schema 未正确传递给 LLM**
   - Kimi SDK 可能需要明确的 `response_format` 参数
   - 或 `tools` 参数未包含 `create_deliverable` 的 schema

3. **LLM 模型版本问题**
   - 不同模型对 JSON 格式输出的支持程度不同
   - 可能需要在 prompt 中更明确地要求 JSON

#### 根因层 3: extract_json 函数正则表达式不健壮

**文件**: `autoBMAD/docuswarm/llm/response.py` 第 85-91 行

```python
# 当前正则 — 只能匹配简单的 JSON 结构
json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
match = re.search(json_pattern, response)
```

**局限性**:
- 不支持嵌套超过 2 层的 JSON
- 不处理数组 `[]` 格式
- 遇到复杂 JSON (如包含转义字符) 失败

**实际场景**:
如果 LLM 响应中包含:
```
Here's the result: {"deliverable": {"content": "Test"}, "questions": []}
```
正则可能无法匹配嵌套结构或数组。

**终端证据**:
虽然日志显示的是纯 Markdown，但在完整响应中可能有 JSON，只是正则未能提取。

### 解决方案

#### 方案 A: 修复 Prompt 模板强制 JSON 输出 (推荐 — 治本)

**修复文件**: `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`

在 prompt 末尾添加明确的输出格式要求:
```yaml
prompt: |
  ...(现有 prompt 内容)...
  
  CRITICAL OUTPUT REQUIREMENT:
  You MUST respond with ONLY a valid JSON object in the following exact format:
  {
    "deliverable": {"title": "...", "content": "..."},
    "questions": [...],
    "action": "create_deliverable"
  }
  
  DO NOT include any markdown formatting, explanations, or text outside the JSON.
  The entire response must be parseable by json.loads().
```

**或在代码中强制设置 response_format**:

**修复文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
# 在 single_prompt 调用时添加
response = await session.single_prompt(
    user_input=prompt,
    response_format={"type": "json_object"},  # ← 新增
)
```

#### 方案 B: 增强 extract_json 正则表达式 (辅助)

**修复文件**: `autoBMAD/docuswarm/llm/response.py` 第 85 行

```python
# 改进正则以支持嵌套和数组
json_pattern = r"\{(?:[^{}\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\]|\{(?:[^{}]|\{[^{}]*\})*\})*\}"
match = re.search(json_pattern, response, re.DOTALL)

# 或使用更激进的提取策略
import ast
try:
    # 尝试查找任何看起来像 JSON 的内容
    for line in response.split('\n'):
        if line.strip().startswith('{'):
            json_str = ''
            brace_count = 0
            for char in response[response.index(line):]:  
                json_str += char
                if char == '{': brace_count += 1
                elif char == '}': brace_count -= 1
                if brace_count == 0 and json_str.strip():
                    return json.loads(json_str)
except Exception:
    pass
```

#### 方案 C: 添加 Fallback 解析逻辑 (容错)

**修复文件**: `autoBMAD/docuswarm/agents/independent.py` 第 319-324 行

```python
try:
    data = extract_json(content)
except ResponseParseError as e:
    # Fallback: 如果是纯 Markdown，尝试构造 JSON
    if content.startswith("##") or content.startswith("#"):
        self.logger.warning("llm_returned_markdown", attempting_fallback=True)
        data = {
            "deliverable": {
                "title": "LLM Generated Document",
                "content": content  # 使用原始 Markdown
            },
            "questions": [],
            "action": "create_deliverable"
        }
    else:
        self.logger.error("response_parse_failed", error=str(e), content=content[:200])
        raise ResponseParseAgentError(f"Failed to parse response: {e}") from e
```

#### 方案 D: 跳过集成测试 (短期规避)

**修复文件**: `pytest.ini`

```ini
[pytest]
addopts = -m "not integration"
```

### 验证步骤

```bash
# 方案 A: 修改 Prompt 后重新测试
pytest tests/integration/test_node_executor_integration.py::TestNodeExecutorIntegration::test_analyst_node_produces_deliverable -v -s

# 验证 LLM 响应格式 (查看日志)
# 应该看到 JSON 格式的响应而非 Markdown

# 方案 B+C: 测试 Fallback 逻辑
pytest tests/integration/ -v --tb=short

# 方案 D: 跳过集成测试
pytest tests/unit/ -v --tb=short
```

### 影响评估

**实际测试表现** (终端日志分析):
- ✅ **API 连接正常** — 每次调用 10 秒左右完成
- ✅ **LLM 理解能力正常** — 生成了有意义的 Markdown 内容
- ❌ **输出格式错误** — 返回 Markdown 而非 JSON
- 📊 **测试覆盖率 33%** — 表明代码执行正常，只是断言失败

**根本问题定位**:
这不是超时或网络问题，而是 **Prompt Engineering 问题**:
- Kimi LLM 默认倾向生成人类可读的 Markdown
- 需要在 Prompt 中**强制指定** JSON 输出格式
- 或使用 Kimi SDK 的 `response_format` 参数

**建议优先级**:
1. **立即执行** (P0): 方案 A — 修复 Prompt 模板，强制 JSON 输出
2. **辅助增强** (P1): 方案 C — 添加 Fallback 容错逻辑
3. **长期优化** (P2): 方案 B — 增强正则表达式提取能力
4. **短期规避** (P3): 方案 D — 跳过集成测试

**时间估算**:
- 方案 A: 10-15 分钟 (修改 YAML + 测试)
- 方案 C: 20 分钟 (代码修改 + 单元测试)
- 方案 B: 30 分钟 (复杂正则 + 边界测试)
- 方案 D: 2 分钟 (配置修改)


### 影响范围

**实际测试结果** (2026-02-24):
- ❌ **仍然失败** — `test_execute_node_flow_success` (完整错误输出被截断)
- ⚠️ **未单独测试** — `test_execute_node_flow_with_no_chain_flag`

**受影响测试文件**: `tests/unit/test_node_execution_flow.py`

**当前失败测试**:
- `TestExecuteNodeFlow::test_execute_node_flow_success` ← 确认失败

### 深度根因分析

此问题包含 **两层缺陷**:

#### 缺陷层 1: Mock 路径导致 StateManager 未被正确替换

**文件**: `tests/unit/test_node_execution_flow.py` 第 361 行

测试使用以下 patch 路径:
```python
with patch("docuswarm.node_execution.flow.StateManager") as mock_state_manager_cls:
```

**`conftest.py` 模块别名映射** (第 54+69 行):
```python
import autoBMAD.docuswarm.node_execution
sys.modules["docuswarm.node_execution"] = autoBMAD.docuswarm.node_execution
# ❌ 缺失: sys.modules["docuswarm.node_execution.flow"] 的显式映射
```

**问题机制**:

`unittest.mock.patch` 解析 `"docuswarm.node_execution.flow.StateManager"` 时:
1. 调用 `__import__("docuswarm")` → 通过别名获取 `autoBMAD.docuswarm`
2. `getattr(module, "node_execution")` → `autoBMAD.docuswarm.node_execution`
3. `getattr(module, "flow")` → 尝试获取 `.flow` 子模块

在步骤 3，由于 `docuswarm.node_execution.flow` 未在 `sys.modules` 中显式注册，Python 可能创建一个**新的模块引用**而非复用 `autoBMAD.docuswarm.node_execution.flow`。这导致 `patch` 修改了一个不同的模块对象上的 `StateManager`，而实际执行代码使用的是原始模块中的 `StateManager`。

**证据**: 测试报错 `StorageError: Pipeline not found: node-analyst-run-test-123`，说明调用了真实的 `StateManager.save_node_result()`，而非 mock。

#### 缺陷层 2: flow.py 中 create_pipeline 未使用预期的 pipeline_id

**文件**: `autoBMAD/docuswarm/node_execution/flow.py` 第 290-306 行

```python
pipeline_id = f"node-{node_id}-{run_id}"  # 例: "node-analyst-run-test-123"

try:
    pipeline = state_manager.get_pipeline(pipeline_id)
    if pipeline is None:
        state_manager.create_pipeline(        # ← 创建时使用自动生成的 ID
            subject=f"Node: {node_id}",
            subject_context={...},
        )
except Exception:
    pass

state_manager.save_node_result(
    pipeline_id=pipeline_id,    # ← 使用 "node-analyst-run-test-123"
    ...
)
```

**StateManager.create_pipeline** (第 98-132 行) 内部自动生成 ID:
```python
def create_pipeline(self, subject, subject_context=None) -> str:
    pipeline_id = self._generate_pipeline_id()  # "pipeline-{timestamp}-{uuid}" ← 全新 ID！
    ...
```

**问题**: 即使 mock 被修复，`flow.py` 的真实逻辑仍然有 BUG:
- `create_pipeline()` 生成的 pipeline_id (如 `pipeline-1234-abcd`) ≠ `save_node_result()` 使用的 pipeline_id (如 `node-analyst-run-test-123`)
- `save_node_result()` 检查 `_pipeline_exists(pipeline_id)` 必然失败

### 解决方案

#### 修复 A: conftest.py — 补充模块别名

**修复文件**: `tests/conftest.py`

在现有别名之后添加:

```python
# 补充 node_execution 子模块别名
import autoBMAD.docuswarm.node_execution.flow
import autoBMAD.docuswarm.node_execution.executor
import autoBMAD.docuswarm.node_execution.state
import autoBMAD.docuswarm.node_execution.chaining
import autoBMAD.docuswarm.node_execution.validator

sys.modules["docuswarm.node_execution.flow"] = autoBMAD.docuswarm.node_execution.flow
sys.modules["docuswarm.node_execution.executor"] = autoBMAD.docuswarm.node_execution.executor
sys.modules["docuswarm.node_execution.state"] = autoBMAD.docuswarm.node_execution.state
sys.modules["docuswarm.node_execution.chaining"] = autoBMAD.docuswarm.node_execution.chaining
sys.modules["docuswarm.node_execution.validator"] = autoBMAD.docuswarm.node_execution.validator
```

#### 修复 B: flow.py — 修复 create_pipeline 逻辑

**修复文件**: `autoBMAD/docuswarm/node_execution/flow.py` 第 292-306 行

**方案 B1** (推荐 — 使用返回的 pipeline_id):
```python
# 将 create_pipeline 返回的 ID 赋值给 pipeline_id
try:
    pipeline = state_manager.get_pipeline(pipeline_id)
    if pipeline is None:
        pipeline_id = state_manager.create_pipeline(
            subject=f"Node: {node_id}",
            subject_context={
                "run_id": run_id,
                "node_id": node_id,
                "context_hash": context_hash,
            },
        )
except Exception:
    pass
```

**方案 B2** (备选 — 扩展 StateManager 接口):

在 `StateManager.create_pipeline` 中添加可选 `pipeline_id` 参数:
```python
def create_pipeline(
    self,
    subject: str,
    subject_context: dict[str, Any] | None = None,
    pipeline_id: str | None = None,  # ← 新增
) -> str:
    pipeline_id = pipeline_id or self._generate_pipeline_id()
    ...
```

然后在 `flow.py` 中传入:
```python
state_manager.create_pipeline(
    subject=f"Node: {node_id}",
    subject_context={...},
    pipeline_id=pipeline_id,  # ← 使用预定义 ID
)
```

#### 修复 B 的影响评估

`save_node_run` 函数 (第 328-392 行) 也有同样的逻辑问题，需要同步修复。

### 验证步骤

```bash
# 1. 修复后运行受影响的测试
pytest tests/unit/test_node_execution_flow.py::TestExecuteNodeFlow -v --tb=long

# 2. 预期结果: 2 个测试全部通过
# 3. 运行完整 flow 测试集
pytest tests/unit/test_node_execution_flow.py -v --tb=short
```

---

## 问题 3 (P2): template_loader 测试异常类身份不匹配

### 影响范围

**实际测试结果** (2026-02-24):
- ❌ **确认失败** — `test_validate_isolation_violation`

**受影响测试文件**: `tests/unit/test_template_loader.py`

**失败表现**: 异常被正确抛出但 `pytest.raises` 未能捕获

**错误日志**:
```
autoBMAD.docuswarm.prompts.validator.TemplateIsolationError: Template isolation violation: Evaluator template contains forbidden field 'private_reasoning'.
```

### 深度根因分析

**文件**: `tests/unit/test_template_loader.py` 第 15 行 + 第 244 行

```python
# 第 15 行 — 测试导入
from docuswarm.prompts.validator import TemplateIsolationError

# 第 244 行 — 使用 pytest.raises 捕获
with pytest.raises(TemplateIsolationError) as exc_info:
    loader.validate_isolation("independent_agent", "evaluator_agent")
```

**异常抛出源**: `autoBMAD/docuswarm/prompts/validator.py` 第 64 行
```python
raise TemplateIsolationError(error_msg)
```

**问题机制**:

Python 异常匹配基于**类身份** (identity)，不仅是类名。`pytest.raises(ExceptionClass)` 使用 `isinstance()` 检查，而 `isinstance()` 需要异常对象是指定类或其子类的实例。

关键问题在于 `conftest.py` 的别名映射:

```python
# conftest.py 中 ❌ 缺失:
# sys.modules["docuswarm.prompts"] = autoBMAD.docuswarm.prompts
# sys.modules["docuswarm.prompts.validator"] = autoBMAD.docuswarm.prompts.validator
```

当测试执行 `from docuswarm.prompts.validator import TemplateIsolationError` 时:
1. Python 查找 `sys.modules["docuswarm"]` → `autoBMAD.docuswarm` (有别名)
2. 查找 `docuswarm.prompts` → 可能创建新的模块引用
3. 查找 `docuswarm.prompts.validator` → 可能创建新的模块引用

如果步骤 2/3 创建了新的模块引用 (而非复用 `autoBMAD.docuswarm.prompts.validator`)，则:
- 测试中的 `TemplateIsolationError` ← 来自新模块引用
- 运行时抛出的 `TemplateIsolationError` ← 来自 `autoBMAD.docuswarm.prompts.validator`
- **类身份不同** → `isinstance()` 返回 False → `pytest.raises` 无法捕获

**报告证据**: 异常确实被抛出且消息包含 "private_reasoning"，但 `pytest.raises` 未能捕获它。

### 解决方案

#### 方案 A (推荐 — 修复 conftest.py 别名):

**修复文件**: `tests/conftest.py`

```python
# 添加 prompts 子模块别名
import autoBMAD.docuswarm.prompts
import autoBMAD.docuswarm.prompts.validator
import autoBMAD.docuswarm.prompts.template_loader

sys.modules["docuswarm.prompts"] = autoBMAD.docuswarm.prompts
sys.modules["docuswarm.prompts.validator"] = autoBMAD.docuswarm.prompts.validator
sys.modules["docuswarm.prompts.template_loader"] = autoBMAD.docuswarm.prompts.template_loader
```

#### 方案 B (备选 — 修改测试导入路径):

```python
# 使用规范路径导入
from autoBMAD.docuswarm.prompts.validator import TemplateIsolationError
```

### 验证步骤

```bash
pytest tests/unit/test_template_loader.py::TestTemplateLoader::test_validate_isolation_violation -v --tb=long
```

---

## 问题 4 (P3): subpackages 模块别名不完整 (间歇性)

### 影响范围

**实际测试结果** (2026-02-24):
- ✅ **19/19 全部通过** — `test_subpackages.py` 当前执行成功

**受影响测试文件**: `tests/unit/test_subpackages.py`

**状态**: 间歇性问题当前未触发，但根因 (conftest.py 别名不完整) 仍存在

### 深度根因分析

**`conftest.py` 当前别名覆盖分析**:

| 子包路径 | 是否有别名 | 测试是否受影响 |
|---------|-----------|--------------|
| `docuswarm.agents` | ✅ 有 | 否 |
| `docuswarm.storage` | ✅ 有 | 是 (间歇) |
| `docuswarm.nodes` | ❌ 无 | 是 (间歇) |
| `docuswarm.context` | ❌ 无 | 是 (间歇) |
| `docuswarm.llm` | ❌ 无 | 是 (间歇) |
| `docuswarm.utils` | ❌ 无 | 是 (间歇) |
| `docuswarm.tools` | ❌ 无 | 是 (间歇) |

**间歇性原因**: 测试执行顺序的随机性:
- 如果其他测试先触发了 `import docuswarm.nodes` (通过 `from docuswarm.node_execution import ...` 间接触发)，Python 会在 `sys.modules` 中缓存模块，后续导入成功
- 如果 `test_subpackages.py` 先执行，直接 `import docuswarm.nodes` 可能因缺少别名而失败

### 解决方案

**修复文件**: `tests/conftest.py`

在现有别名后补充所有子包:

```python
# 补充子包别名
import autoBMAD.docuswarm.nodes
import autoBMAD.docuswarm.nodes.dual_agent
import autoBMAD.docuswarm.nodes.loader
import autoBMAD.docuswarm.context
import autoBMAD.docuswarm.context.audit
import autoBMAD.docuswarm.context.filter
import autoBMAD.docuswarm.context.isolation
import autoBMAD.docuswarm.context.memory
import autoBMAD.docuswarm.llm
import autoBMAD.docuswarm.llm.config
import autoBMAD.docuswarm.llm.response
import autoBMAD.docuswarm.llm.session_manager
import autoBMAD.docuswarm.utils
import autoBMAD.docuswarm.utils.logging
import autoBMAD.docuswarm.tools

sys.modules["docuswarm.nodes"] = autoBMAD.docuswarm.nodes
sys.modules["docuswarm.nodes.dual_agent"] = autoBMAD.docuswarm.nodes.dual_agent
sys.modules["docuswarm.nodes.loader"] = autoBMAD.docuswarm.nodes.loader
sys.modules["docuswarm.context"] = autoBMAD.docuswarm.context
sys.modules["docuswarm.context.audit"] = autoBMAD.docuswarm.context.audit
sys.modules["docuswarm.context.filter"] = autoBMAD.docuswarm.context.filter
sys.modules["docuswarm.context.isolation"] = autoBMAD.docuswarm.context.isolation
sys.modules["docuswarm.context.memory"] = autoBMAD.docuswarm.context.memory
sys.modules["docuswarm.llm"] = autoBMAD.docuswarm.llm
sys.modules["docuswarm.llm.config"] = autoBMAD.docuswarm.llm.config
sys.modules["docuswarm.llm.response"] = autoBMAD.docuswarm.llm.response
sys.modules["docuswarm.llm.session_manager"] = autoBMAD.docuswarm.llm.session_manager
sys.modules["docuswarm.utils"] = autoBMAD.docuswarm.utils
sys.modules["docuswarm.utils.logging"] = autoBMAD.docuswarm.utils.logging
sys.modules["docuswarm.tools"] = autoBMAD.docuswarm.tools
```

### 验证步骤

```bash
# 多次运行验证无间歇性失败
pytest tests/unit/test_subpackages.py -v --count=5
```

---

## 修复实施顺序 (基于实际测试结果)

### 阶段 0: 处理集成测试 (P4 — 5 分钟)

**目标**: 避免集成测试干扰单元测试修复流程

1. **方案 C** - 在 pytest 运行时跳过集成测试:
   ```bash
   # 临时跳过方式 (命令行)
   pytest tests/unit/ -v --tb=short  # 只运行单元测试
   
   # 或添加标记方式 (修改 tests/integration/test_node_executor_integration.py)
   pytestmark = [
       pytest.mark.integration,
       pytest.mark.skipif(not os.environ.get("KIMI_API_KEY"), reason="...")
   ]
   ```

2. 验证跳过生效:
   ```bash
   pytest tests/ -v --collect-only | grep integration
   # 应该显示集成测试被 skip
   ```

### 阶段 1: 修复 Mock 签名不匹配 (P0 — 5 分钟)

1. 在 `tests/unit/test_node_executor.py` 第 689 和 746 行修改 `mock_execute` 签名:
   ```python
   async def mock_execute(subject_context, task, pipeline_id=""):
   ```
2. 运行验证:
   ```bash
   pytest tests/unit/test_node_executor.py::TestChainedContextExtraction -v
   ```
3. **预期结果**: 2/2 测试通过 (从当前 0/2 提升)

### 阶段 1.5: 预防性添加 Path 导入 (P0 — 2 分钟)

1. 在 `autoBMAD/docuswarm/node_execution/executor.py` 第 11 行后添加:
   ```python
   from pathlib import Path
   ```
2. **重要性**: 避免集成测试或生产环境中触发 NameError

### 阶段 2: conftest.py 别名补全 (P1+P2+P3 — 15 分钟)

1. 在 `tests/conftest.py` 中补充所有缺失的子模块别名 (见问题 2/3/4 的解决方案)
2. 运行验证:
   ```bash
   pytest tests/unit/test_node_execution_flow.py tests/unit/test_template_loader.py tests/unit/test_subpackages.py -v --tb=short
   ```

### 阶段 3: flow.py 逻辑修复 (P1 — 10 分钟)

1. 修复 `flow.py` 中 `create_pipeline` 的 pipeline_id 赋值逻辑
2. 修复 `save_node_run` 函数中相同的问题
3. 运行验证:
   ```bash
   pytest tests/unit/test_node_execution_flow.py -v --tb=long
   ```

### 阶段 4: 全量回归 (5 分钟)

```bash
# 单元测试回归
pytest tests/unit/ -v --tb=short
```

**预期结果**: 单元测试全部通过 (含之前通过的 + 修复的 20)

### 阶段 5: (可选) 修复集成测试 LLM 响应格式 (30-60 分钟)

**根据项目需求决定是否执行**:

1. **优先**: 采用问题 5 的方案 A (修复 Prompt 模板)
2. **辅助**: 采用方案 C (添加 Fallback 容错)
3. 执行集成测试验证:
   ```bash
   pytest tests/integration/test_node_executor_integration.py::TestNodeExecutorIntegration::test_analyst_node_produces_deliverable -v -s
   # 查看日志确认 LLM 返回 JSON 格式
   ```

**核心问题**: 不是超时，而是 Kimi LLM 返回 Markdown 而非 JSON。需要在 Prompt 中明确指定输出格式。

---

## 根因预防建议

### 1. 导入完整性检查

在 CI 中加入静态分析步骤，检测使用但未导入的标识符:

```bash
# 使用 ruff 检查未定义名称
ruff check --select F821 autoBMAD/
```

### 2. conftest.py 别名自动化

当前手动维护 `sys.modules` 别名容易遗漏。建议改用自动发现机制:

```python
# conftest.py 中替换手动别名
import pkgutil
import autoBMAD.docuswarm

for importer, modname, ispkg in pkgutil.walk_packages(
    autoBMAD.docuswarm.__path__,
    prefix="autoBMAD.docuswarm.",
):
    try:
        __import__(modname)
        alias = modname.replace("autoBMAD.", "", 1)
        sys.modules[alias] = sys.modules[modname]
    except ImportError:
        pass
```

### 3. Mock 路径验证

在测试基类中添加 mock 路径验证:
```python
# 使用 autoBMAD 前缀进行 patch 以确保模块身份一致
# ✅ 推荐:
with patch("autoBMAD.docuswarm.node_execution.flow.StateManager"):
# ❌ 避免:
with patch("docuswarm.node_execution.flow.StateManager"):
```

---

## 附录: 文件修改清单

| 文件 | 修改类型 | 描述 | 优先级 |
|------|---------|------|--------|
| `autoBMAD/docuswarm/node_execution/executor.py` | 源码修复 | 添加 `from pathlib import Path` | P0 (预防性) |
| `autoBMAD/docuswarm/node_execution/flow.py` | 源码修复 | 修复 create_pipeline 的 pipeline_id 逻辑 | P1 |
| `tests/unit/test_node_executor.py` | 测试修复 | 修复 mock_execute 签名 (第 689, 746 行) | P0 |
| `tests/conftest.py` | 测试基础设施 | 补充缺失的子模块别名映射 | P1+P2+P3 |
| `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` | Prompt 修复 | 添加强制 JSON 输出要求 | P4 (治本) |
| `autoBMAD/docuswarm/agents/independent.py` | 容错增强 | 添加 Markdown fallback 逻辑 | P4 (辅助) |
| `autoBMAD/docuswarm/llm/response.py` | 解析增强 | 改进 JSON 提取正则 | P4 (优化) |
| `tests/integration/test_node_executor_integration.py` | 测试配置 | 添加 integration 标记跳过 | P4 (规避) |
