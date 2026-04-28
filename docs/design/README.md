# DocuSwarm Design Alignment Index

## 当前入口

当前设计主文档仍是:

- `docs/plan/UX_DESIGN.md`

新增本目录是为了给后续阅读提供稳定入口，并明确哪些设计约束已被 2026-03-13 的重构研究更新。

## 重要决策更新 (2026-04-05)

### Session 执行失败修复 (P0 Critical)

**问题**: 2026-04-05 发现 Session 执行失败链 `llm_call_error` → `independent_agent_failed` → `node_execution_failed`，影响所有节点 100% 失败。

**根因**:
1. `ClaudeSessionWrapper.prompt()` 调用了 SDK 中不存在的 `send_message()` 和 `messages()` 方法
2. `independent.py` 错误地对 async generator 使用 `await session.prompt()`
3. `ANTHROPIC_MODEL_NAME` 环境变量逻辑需要移除

**修复方案**:
| Bug | 修复内容 | 文件 |
|-----|----------|------|
| BUG-1 | `send_message()` → `query()`, `messages()` → `receive_messages()` | `session_manager.py` |
| BUG-2 | 移除 `await`，改为 `async for msg in session.prompt()` | `independent.py` |
| BUG-3 | 移除 `ANTHROPIC_MODEL_NAME` 环境变量读取 | `session_manager.py` |

**相关文档**:
- [Session Execution Failure Analysis](../research/session-execution-failure-analysis.md) - 深度分析报告
- [Session Execution Failure Solution](../research/session-execution-failure-solution.md) - 修复方案
- [Session Execution Failure TDD Plan](../solution/2026-04-05-session-execution-failure-tdd-plan.md) - 测试驱动方案

---

## 重要决策更新 (2026-03-17)

### P1-2 更新: Reference Docs Preload (Step 2)

基于 [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md)，产品决定实施 **Step 2: 引用文档预加载功能**。

**核心变更**:
- ✅ 实施引用文档自动预加载 (Phase 13 / P12)
- ❌ ~~`docs/research/2026-03-13-p1-controlled-docs-context-strategy-plan.md`~~ 不再实施
- ❌ ~~`ContextResolver` 和 `@path` 注入~~ 不再实施

**新功能: Reference Docs Preload**:
- Context file 中引用的文档自动注入 Agent 提示词
- 无需 Agent 主动调用工具读取
- 递归搜索 `docs/` 目录，支持子目录
- 内容截断保护 (10K 字符限制)

**相关文档**:
- [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)
- [Architecture Doc](../architecture/04_STATE_ARCHITECTURE.md#6-reference-docs-preload-architecture-step-2)

### 设计对齐重点 (更新)

- 节点输出必须重新回到"节点契约驱动"，而不是"persona 驱动"。
- 用户看到的交付物应始终对应工具写盘的正式文档，而不是 state 中的摘要副本。
- ~~docs 相关能力在 UX 上应表现为"受控参考来源"~~ (已移除，工作流不读取 docs/)

## 建议阅读顺序

1. `docs/plan/UX_DESIGN.md`
2. `docs/evaluation/docuswarm-agent-context-injection-evaluation-2026-03-13.md`
3. `docs/research/2026-03-13-docuswarm-context-refactor-overview.md`
4. `docs/research/2026-03-13-p0-node-prompt-injection-plan.md`
5. `docs/research/2026-03-13-p0-single-truth-deliverable-plan.md`
6. ~~`docs/research/2026-03-13-p1-controlled-docs-context-strategy-plan.md`~~ (已移除)

## 重构验收标准

- [ ] Independent prompt 中能稳定看到节点契约信息
- [ ] Evaluator 评审对象始终来自工具写盘后的正式文档正文
- [ ] Pipeline state 不再保存完整 markdown 正文，仅保存 metadata
- [ ] `update_context` 可真实写入并在下一节点读取
- [ ] 工作流运行过程中不读取 `docs/`，所有执行产物只进入 `output/`

## F5 Pipeline & Node Execution 设计约束 (2026-03-25)

### 单一主干原则

| 模块 | 职责 | 禁止行为 |
|------|------|---------|
| `pipeline/` | 业务编排 (Orchestration) | 直接操作 NodeRunState |
| `node_execution/` | 节点执行 (Execution) | 直接创建 synthetic pipeline_id |
| `PipelineAdapter` | 唯一合法边界 | N/A |

### 硬失败约束

**Before (Deprecated)**:
```python
# ❌ 禁止: Silent fallback
def create_pipeline_graph(..., session_manager: Any | None = None):
    if session_manager is None:
        # 静默降级到 deprecated executor
        return _create_default_node_executor(...)
```

**After (F5)**:
```python
# ✅ 必须: Hard fail on missing session_manager (P1-2: SessionManager, KimiSessionManager removed)
def create_pipeline_graph(..., session_manager: SessionManager):
    if session_manager is None:
        raise ValueError("session_manager is required")
```

### 边界使用规范

```python
# ✅ 必须: 通过 PipelineAdapter 创建 synthetic ID
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

pipeline_id = PipelineAdapter.create_pipeline_id("analyst", "run-123")
pipeline_id = PipelineAdapter.create_run_pipeline_id("run-456")

# ❌ 禁止: 直接 f-string 拼接
pipeline_id = f"node-analyst-run-123"  # 违规!
pipeline_id = f"node-run-{run_id}"      # 违规!
```

### 状态转换规范

```python
# ✅ 必须: 使用 PipelineAdapter 进行状态转换
node_state = PipelineAdapter.convert_pipeline_to_node_state(
    pipeline_state, "analyst"
)
pipeline_state = PipelineAdapter.convert_node_to_pipeline_state(
    node_state, original_pipeline_state
)

# ❌ 禁止: 直接调用内部转换函数 (已从 pipeline/graph.py 移除)
# _convert_pipeline_to_node_state(...)  # 已删除!
# _convert_node_to_pipeline_state(...)  # 已删除!
```

### 参考文档

- [F5 TDD Implementation Plan](../solution/2026-03-25-f5-test-driven-implementation-plan.md)
- [F5 Research Report](../research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md)
- [F5 Unified Design Spec](../research/2026-03-25-f5-unified-design-spec.md)

---

## F2 状态一致性设计约束 (2026-03-25)

### 单一真相源原则

Pipeline 状态管理遵循 `state_json` 单一真相源模式：

- **写入约束**: 所有状态变更必须通过 `StateManager.update_pipeline_state()` 方法
- **读取约束**: 所有状态读取必须使用 `PipelineStateView` 或 `pipeline["state"]` 路径
- **禁止直接访问**: 不允许直接访问 `pipeline["current_node"]`（顶层字段）

### 状态访问规范

```python
# ✅ 推荐: 使用 PipelineStateView
view = PipelineStateView(pipeline)
current_node = view.current_node  # 从 state_json 读取

# ✅ 允许: 直接访问 state 字段
state = pipeline.get("state", {})
current_node = state.get("current_node")

# ❌ 禁止: 访问顶层字段（可能过时）
current_node = pipeline.get("current_node")  # 不要这样做
```

### 参考文档

- [F2 Test-Driven Implementation Plan](../solution/2026-03-25-f2-test-driven-implementation-plan.md)
- [F2 State Consistency Research](../research/2026-03-25-f2-state-json-consistency-research-report.md)
- [F2 Unified Design Spec](../research/2026-03-25-f2-unified-design-spec.md)

---

## 2026-03-28 重构实施设计约束

### 概述

基于审查报告的5项关键要求，实施以下设计约束：

| 要求 | 设计约束 | 状态 |
|------|----------|------|
| **REQ-001** | system_prompt 必须使用 preset/append 结构 | 强制 |
| **REQ-002** | evaluator 配置必须内联于 node.yaml | 强制 |
| **REQ-003** | SessionManager 必须接收 node_id 和 tool_permissions | 强制 |
| **REQ-004** | tests/__init__.py 必须有效 Python 语法 | 强制 |
| **REQ-005** | deliverable 必须包含扩展字段 | 强制 |

### system_prompt 结构约束

**拒绝向后兼容**:
```python
# ❌ 禁止: 字符串直接赋值
options.system_prompt = "persona + instructions"

# ✅ 必须: preset/append 结构
options.system_prompt = {
    "type": "preset",
    "preset": "claude_code",
    "append": "Layers 2+3+4 content"
}
```

### node.yaml Schema v2.1 约束

**Deliverable 扩展字段**:
```yaml
deliverable:
  required_sections: [...]
  template_title: "..."      # 必填
  output_filename: "..."     # 必填
  format_hints:              # 可选
    max_words: 3000
    target_audience: "..."
```

**Evaluator 内联配置**:
```yaml
evaluator:
  criteria_file: evaluator.yaml
  threshold:                  # 单数，非 thresholds
    approval: 0.70
    escalation: 0.50
  max_iterations: 3
```

### 工具权限注入约束

**SessionManager 创建必须包含**:
```python
SessionManager(
    work_dir=...,
    node_id="analyst",                    # 用于 MCP 服务器命名
    file_dirs=["docs/", "docs/research/"], # 文件读取权限
    search_dirs=["docs/"],                 # 搜索权限
)
```

### 参考文档

- [Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md) - 详细实施研究
- [Test-Driven Implementation](../solution/refactor-2026-03-28-test-driven-implementation.md) - TDD 实施方案
- [Implementation Review](../evaluation/2026-03-28-refactor-2026-03-26-implementation-review.md) - 审查报告

---

## 2026-03-29 优先级问题修复设计约束

### F5: 配置检查器语义验证增强 (P1)

**问题**: `node_config_completeness_checker.py` 报告 100% 完整度，但存在跨文件语义不一致。

**新增设计约束**:

| 检查项 | 说明 | 影响 |
|--------|------|------|
| Sections 一致性 | `node.yaml:deliverable.required_sections` 必须与 `persona.json:output_format.sections` 一致 | 高 |
| 语义匹配分数 | 合规分数 = 交集大小 / 并集大小 | 中 |

**示例不一致检测** (architect 节点):
```yaml
# node.yaml - 4 sections
required_sections: [architecture, api_design, data_model, security]

# persona.json - 9 sections  
sections: [system_overview, architectural_pattern, component_diagram, data_model, api_design, security, scalability, integration_points, technology_stack]

# 检测结果:
# - 交集: 3 (data_model, api_design, security)
# - 并集: 10
# - 匹配率: 30% ⚠️
```

**修复后检查器行为**:
```python
# node_config_completeness_checker.py
issues = check_cross_file_consistency(node_dir)
# 返回: [ConsistencyIssue(severity="warning", message="Sections mismatch...")]

completeness_score *= calculate_semantic_match_score(node_dir)
# 100% -> 30% (反映真实一致性)
```

### F6: SessionManager 属性清理 (P2)

**问题**: `SessionManager.allowed_dirs` 属性访问未定义的 `_allowed_dirs`。

**设计变更**:
```python
# ❌ 已删除 (会导致 AttributeError)
@property
def allowed_dirs(self) -> list[str] | None:
    return self._file_dirs or self._allowed_dirs  # _allowed_dirs 未定义!

# ✅ 使用替代属性
@property
def file_dirs(self) -> list[str] | None:
    return self._file_dirs
```

**迁移指南**:
- 所有使用 `session_manager.allowed_dirs` 的代码改为 `session_manager.file_dirs`
- `allowed_dirs` 是一个已废弃的兼容属性，现已完全移除

### 参考文档

- [Priority Issues Test-Driven Plan](../solution/2026-03-29-docuswarm-priority-issues-test-driven-plan.md) - 完整修复方案
- [Priority Issues Research](../research/2026-03-28-docuswarm-priority-issues-deep-research.md) - 问题深度研究

---

## P0-2/P0-3 退役设计约束 (2026-04-03)

### 单执行主干原则 (P0-2)

**禁止存在第二执行主干**:

```python
# ❌ 禁止: 任何对历史实现的引用
from autoBMAD.docuswarm.nodes.dual_agent import create_node_executor  # ImportError!
import autoBMAD.docuswarm.node_execution.graph  # ImportError!
import autoBMAD.docuswarm.node_execution.flow   # ImportError!

# ✅ 唯一合法入口:
from autoBMAD.docuswarm.node_execution.executor import create_node_executor
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
```

**架构守护测试**:
- `test_p0_2_execution_trunk_retirement.py`: 验证旧符号不可访问
- `test_exactly_one_create_node_executor_implementation()`: AST 扫描确认单一实现

### 同步/异步契约原则 (P0-3)

**StateManager 同步契约**:
```python
# ✅ StateManager 方法必须是普通 def
class StateManager:
    def get_latest_successful_run(...): ...  # 同步
    def save_node_result(...): ...           # 同步

# ❌ 禁止: await 同步方法
run_result = await state_manager.get_latest_successful_run(...)  # TypeError!

# ✅ 上层 async 代码使用 asyncio.to_thread()
run_result = await asyncio.to_thread(
    state_manager.get_latest_successful_run, pred_id, context_hash
)
```

**pipeline/graph.py 约束**:
```python
# ❌ 禁止: run_until_complete 自举
checkpointer = loop.run_until_complete(create_async_checkpointer())  # RuntimeError!

# ✅ 必须: 预创建 checkpointer 传入
if checkpointer is None and db_path is not None:
    raise ValueError("session_manager is required")  # 硬失败
```

**禁止 _run_async 桥接**:
```python
# ❌ 禁止: ThreadPoolExecutor + asyncio.run 桥接
def _run_async(coro):
    with ThreadPoolExecutor() as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()
```

### 参考文档

- [Test-Driven Retirement Plan](../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md) - 完整退役方案
- [Deep Research Report](../research/2026-04-03-p0-2-p0-3-deep-research-report.md) - 问题深度研究

---

## P1-2 配置语义统一设计约束 (2026-04-03)

### 概述

P1-2 配置语义混杂技术债要求统一配置命名，消除 `KIMI_API_KEY`/`CLAUDE_API_KEY`/`ANTHROPIC_API_KEY` 混用问题。

**清理原则**:
1. **无兼容层原则**: 不再保留任何兼容性别名或兼容层
2. **主路径唯一原则**: 每个功能只有一个主路径入口
3. **命名一致性原则**: 统一使用 `ANTHROPIC_*` 和 `SessionManager`
4. **代码即文档原则**: 删除的代码比废弃标记更清晰

### 环境变量命名规范

**唯一支持的配置**:
```bash
# ✅ 使用: ANTHROPIC_* 命名
ANTHROPIC_API_KEY=your-api-key
ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
ANTHROPIC_MODEL_NAME=claude-3-opus-20240229
```

**已移除配置 (不再支持)**:
```bash
# ❌ 已移除: 不再支持，无兼容层
KIMI_API_KEY=xxx              # 使用 ANTHROPIC_API_KEY
KIMI_BASE_URL=xxx             # 使用 ANTHROPIC_BASE_URL
CLAUDE_API_KEY=xxx            # 使用 ANTHROPIC_API_KEY
CLAUDE_BASE_URL=xxx           # 使用 ANTHROPIC_BASE_URL
CLAUDE_MODEL_NAME=xxx         # 使用 ANTHROPIC_MODEL_NAME
```

### 配置读取职责规范

```python
# ✅ 正确: 配置层统一读取 ANTHROPIC_*
# config.py
class Config:
    def __post_init__(self):
        # P1-2: 仅读取 ANTHROPIC_API_KEY，无 KIMI_* 兼容
        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY is required")

# ✅ 正确: 会话层从 Config 获取凭证
# session_manager.py
class SessionManager:
    def __init__(self, config: Config, ...):
        self._config = config  # 从 Config 获取，不直接读环境变量
        # P1-2: _api_key 和 _base_url 字段已移除

# ❌ 错误: 会话层直接读取环境变量 (P1-2 已修复)
# class SessionManager:
#     def __init__(self, ...):
#         self._api_key = os.environ.get("CLAUDE_API_KEY")  # 已移除
```

### 配置链路规范

```
统一的配置流 (P1-2 最终状态):
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   .env      │────▶│  Config     │────▶│  SessionManager     │
│ (ANTHROPIC_*│     │  (唯一入口)  │     │  (消费配置创建会话)  │
└─────────────┘     └─────────────┘     └─────────────────────┘
```

### KimiSessionManager 别名移除

**P1-2 清理**: `KimiSessionManager = SessionManager` 别名已移除。

```python
# ❌ 已移除: KimiSessionManager 别名
# from autoBMAD.docuswarm.llm import KimiSessionManager  # ImportError!

# ✅ 使用: SessionManager
from autoBMAD.docuswarm.llm import SessionManager
```

### 环境变量映射（最终状态）

| 旧配置 | 新配置 | 处理方式 |
|--------|--------|----------|
| `KIMI_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `KIMI_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `CLAUDE_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_MODEL_NAME` | *(已移除)* | 模型由 API 网关统一管理，详见 Session Execution Failure Solution |

### 测试驱动验证

所有配置语义变更必须有测试守护:

| 测试文件 | 验证内容 |
|----------|----------|
| `test_config_semantics_unified.py` | 仅 ANTHROPIC_API_KEY 被读取，旧命名不再支持 |
| `test_session_manager_semantics.py` | 未消费字段已移除，无 CLAUDE_* 读取 |
| `test_dual_agent_config.py` | `_get_config()` 使用统一 Config |
| `test_config_semantics_end_to_end.py` | 端到端配置链路一致性 |

### 参考文档

- [P1-2 Deep Research](../research/2026-04-03-p1-2-config-semantics-analysis-report.md) - 配置语义深度研究报告
- [P1-2 Test-Driven Plan](../solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md) - 测试驱动实施方案

---

## P0 Runtime Consumption 设计约束 (2026-04-03)

### 配置即行为原则

运行时组件必须消费配置文件声明的值，禁止硬编码特例。

| 配置项 | 配置源 | 运行时消费点 | 禁止行为 |
|--------|--------|--------------|----------|
| **max_iterations** | `node.yaml` `evaluator.max_iterations` | `DualAgentNode` | 禁止硬编码 `DEFAULT_MAX_ITERATIONS` |
| **approval_threshold** | `evaluator.yaml` `threshold.approval` | `EvaluatorAgent` | 禁止硬编码 `APPROVAL_THRESHOLD = 0.70` |
| **blocked_threshold** | `evaluator.yaml` `threshold.escalation` | `EvaluatorAgent` | 禁止硬编码 `BLOCKED_THRESHOLD = 0.50` |
| **allowed_builtin_tools** | `node.yaml` `tools.allowed_builtin_tools` | `SessionManager` | 禁止忽略/丢失 builtin tools |
| **file_permissions** | `node.yaml` `tools.file_permissions` | `SessionManager` | 禁止解析为错误目录 |
| **MCP server keys** | `NodeToolFilter` 命名规范 | `SessionManager` | 禁止 key 冲突导致 server 覆盖 |

### 单一真相源原则

```
NodeLoader.load(node_id)  ────────┐
    ├── node.evaluator.max_iterations ───┐
    ├── node.evaluator.threshold.* ──────┼──► 运行时组件
    ├── node.tool_permissions.* ─────────┤    (必须消费，无硬编码)
    └── node.deliverable.* ──────────────┘
```

**规则**:
1. 运行时组件必须通过 `NodeLoader` 获取配置
2. 显式参数 > 节点配置 > 默认值 (仅作为 fallback)
3. 配置变更必须自动反映在运行时行为中

### 目录解析规范

**正确路径解析** (P0 Fix):
```python
# ✅ 正确: 使用仓库根目录
repo_root = project_root.parent if project_root.name == "autoBMAD" else project_root
file_dirs = [str(repo_root / d) for d in node_config.tool_permissions.file_permissions.allowed_read_dirs]
# Result: D:\GITHUB\DocuSwarm\docs (正确)

# ❌ 错误: 使用 autoBMAD 子目录
file_dirs = [str(project_root / d) for d in node_config.tool_permissions.file_permissions.allowed_read_dirs]
# Result: D:\GITHUB\DocuSwarm\autoBMAD\docs (错误)
```

### MCP Server Key 命名规范 (SDK MCP 格式)

> **2026-04-05 Update**: 已从 FastMCP 格式迁移到 SDK MCP 格式，解决 `TypeError: Object of type FastMCP is not JSON serializable` 问题。

```python
# tool_filter.py 定义的常量
FILE_SERVER_NAME_FORMAT = "docuswarm-files-{node_id}"
SEARCH_SERVER_NAME_FORMAT = "docuswarm-search-{node_id}"

# SessionManager 必须保持一致
# SDK MCP 格式: create_mcp_servers() 返回 dict[str, Any]
options.mcp_servers = {
    f"docuswarm-files-{node_id}": file_server,    # SDK MCP server dict
    f"docuswarm-search-{node_id}": search_server, # SDK MCP server dict
}

# allowed_tools 中的工具名格式 (SDK MCP 约定)
allowed_tools = [
    "Read",                                               # builtin
    "Glob",                                               # builtin
    f"mcp__docuswarm-files-{node_id}__read_document",     # MCP file (SDK format)
    f"mcp__docuswarm-search-{node_id}__grep_search",      # MCP search (SDK format)
    f"mcp__docuswarm-search-{node_id}__glob_search",      # MCP search (SDK format)
]
```

**FastMCP → SDK MCP 迁移要点**:

| 项目 | FastMCP (旧) | SDK MCP (新) |
|-----|-------------|-------------|
| **返回类型** | `list[FastMCP]` | `dict[str, Any]` |
| **序列化** | ❌ 不支持 | ✅ 支持 |
| **Server 名称** | `mcp__docuswarm-files-{node_id}` | `docuswarm-files-{node_id}` |
| **工具装饰器** | `@server.tool(name="...")` | `@tool(name, desc, schema)` |
| **返回值格式** | 直接返回字符串/对象 | `{'content': [{'type': 'text', 'text': ...}]}` |
| **Server 结构** | `FastMCP` 对象 | `{'type': 'sdk', 'name': ..., 'instance': ...}` |

**SDK MCP 工具实现示例**:

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool('read_document', 'Read a document within allowed directories', {
    'type': 'object',
    'properties': {
        'path': {'type': 'string', 'description': 'Path to the file'}
    },
    'required': ['path']
})
async def read_document_tool(args: dict) -> dict:
    result = read_document(args['path'], validator=validator)
    if result.success:
        return {'content': [{'type': 'text', 'text': str(result.result)}]}
    return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}

server = create_sdk_mcp_server(
    name=f"docuswarm-files-{node_id}",
    version="1.0.0",
    tools=[read_document_tool]
)  # 返回 dict，可直接用于 ClaudeAgentOptions
```

### 测试驱动验证

所有 P0 修复必须有自动化测试守护:

| 测试文件 | 验证内容 |
|----------|----------|
| `test_session_manager_mcp_keys.py` | MCP server keys 不冲突，命名与 NodeToolFilter 一致，SDK MCP 格式正确 |
| `test_independent_agent_permissions.py` | `allowed_builtin_tools` 正确传递到运行时 |
| `test_directory_resolution.py` | 目录解析使用仓库根目录 |
| `test_evaluator_threshold_consumption.py` | Evaluator 从节点配置加载阈值 |
| `test_dual_agent_max_iterations.py` | `max_iterations` 从节点配置加载 |
| `test_runtime_config_consistency.py` | 端到端配置一致性验证 |

### 参考文档

- [P0 Runtime Consumption Research](../research/2026-04-03-p0-runtime-consumption-fix-research-report.md) - 修复研究报告
- [P0 Test-Driven Plan](../solution/2026-04-03-p0-runtime-consumption-test-driven-plan.md) - 测试驱动方案

---

## Phase A/B Technical Debt Resolution 设计约束 (2026-04-04)

### 概述

基于 [技术债务审计报告](../evaluation/2026-04-04-docuswarm-tech-debt-audit.md)，分两个阶段修复关键运行时缺陷和测试缺口。

### Phase A: 运行时缺陷修复 (Critical)

#### P0-1: Asyncio Run in Async Context

**问题**: `HybridOrchestrator.start_pipeline()` 是 `async def`，但内部使用 `asyncio.run()`。

**修复**:
```python
# ❌ 修复前 (orchestrator.py:328,391)
import asyncio
_ = asyncio.run(
    self._state_manager.update_pipeline_state(...)
)

# ✅ 修复后
_ = await self._state_manager.update_pipeline_state(...)
```

**验证**:
- `test_p0_1_asyncio_run_regression.py`: AST 扫描确认无 `asyncio.run()` 在 `async def` 中

#### P0-2: _run_async Bridge Removal

**问题**: `PipelineService` 使用 `ThreadPoolExecutor + asyncio.run` 桥接，违反架构契约。

**修复**:
```python
# ❌ 修复前 - 已删除
# def _run_async(coro): ...

# ✅ 修复后 - 方法改为 async def
async def cancel(self, pipeline_id: str) -> bool:
    ...
    return await self._state_manager.update_pipeline_state(...)

async def cancel_all(self, status: str | None = None) -> tuple[...]:
    ...
    for p in cancellable:
        await self._state_manager.update_pipeline_state(...)
```

**验证**:
- `test_no_run_async_bridge_anywhere.py`: 全代码库扫描确认无 `_run_async`
- `test_cancel_is_async.py`: 验证 `cancel()` 是 `async def`

#### P1-1: Escalate Await

**问题**: `DualAgentNode` 调用异步 `escalate()` 但未 `await`。

**修复**:
```python
# ❌ 修复前 (dual_agent.py:807,845)
if self.escalation_handler:
    self.escalation_handler.escalate(...)  # 未执行!

# ✅ 修复后
if self.escalation_handler:
    await self.escalation_handler.escalate(...)
```

**验证**:
- `test_p1_1_escalation_await_regression.py`: AST 扫描确认 `escalate()` 被 `await`

### Phase B: 测试与文档修复 (High)

#### P1-2: 文档一致性

**问题**: `README.md` 和 `CONFIGURATION.md` 仍使用 `KIMI_*` 和 `KimiSessionManager`。

**修复**:
```markdown
# README.md / CONFIGURATION.md
# ❌ 修复前
KIMI_API_KEY=xxx
KimiSessionManager

# ✅ 修复后
ANTHROPIC_API_KEY=xxx
SessionManager
```

**验证**:
- `test_documentation_consistency.py`: 扫描确认无 `KIMI_*` 和 `KimiSessionManager`

#### P1-3: 冒烟测试补充

**新增测试**:
| 测试文件 | 覆盖路径 |
|----------|----------|
| `test_start_pipeline.py` | Pipeline 启动主路径 |
| `test_resume_pipeline.py` | Pipeline 恢复主路径 |
| `test_cancel_pipeline.py` | Pipeline 取消主路径 |
| `test_escalation.py` | Pipeline 升级主路径 |

**验证**:
```bash
pytest tests/smoke/ -v
```

### 验收标准

| 检查项 | 目标 | 验证 |
|--------|------|------|
| P0-1 | `asyncio.run()` 在 async def 中 = 0 | AST 扫描 |
| P0-2 | `_run_async` 不存在 | AST 扫描 |
| P1-1 | `escalate()` 全部 `await` | AST 扫描 + 运行时测试 |
| P1-2 | `KIMI_*` 文档引用 = 0 | 文本扫描 |
| P1-3 | 冒烟测试 4/4 通过 | pytest |
| 架构测试 | 100% 通过 | pytest |
| 覆盖率 | Orchestrator >= 40%, Dual Agent >= 40% | coverage |

### 参考文档

- [Phase A/B Research Report](../research/phase_a_b_technical_debt_research_report.md) - 深度研究报告
- [Phase A/B TDD Solution](../solution/phase_a_b_test_driven_solution_plan.md) - 测试驱动方案
- [Phase A/B TDD Execution Guide](../solution/TDD_EXECUTION_GUIDE.md) - 快速执行参考
- [Tech Debt Audit](../evaluation/2026-04-04-docuswarm-tech-debt-audit.md) - 技术债务审计

---

## Finding B: 兼容层清理设计约束 (2026-04-04)

### 概述

基于 [Finding B 深度研究报告](../research/2026-04-04-finding-b-compatibility-layer-deep-dive.md)，**完全移除所有兼容层代码**，实现零容忍遗留。

> **核心原则**: 零容忍兼容层。所有标记为 deprecated/legacy/compatibility 的代码必须完全移除，不保留警告、不保留别名、不保留桥接。

### P0: 主路径兼容层清理 (Critical)

#### SessionManager Legacy 参数移除

**问题**: SessionManager 仍接受 `api_key`, `base_url`, `allowed_dirs` 等 legacy 参数，导致配置源混乱。

**设计约束**:
```python
# ❌ 禁止: Legacy 参数（已移除）
SessionManager(
    work_dir=path,
    api_key="xxx",        # 已移除！
    base_url="xxx",       # 已移除！
    allowed_dirs=["/tmp"] # 已移除！使用 file_dirs
)

# ✅ 正确: 统一使用 config + tool_permissions
from autoBMAD.docuswarm.node_execution.contracts import NodeToolPermissions

tool_permissions = NodeToolPermissions(
    file_dirs=["/data"],
    search_dirs=[]
)
SessionManager(
    work_dir=path,
    config=config,           # 包含 API 凭证
    tool_permissions=tool_permissions  # 完整权限配置
)
```

**属性移除**:
```python
# ❌ 已移除: allowed_dirs 属性
# session_manager.allowed_dirs  # AttributeError!

# ✅ 使用: file_dirs 属性
session_manager.file_dirs  # 正确
```

#### DualAgentNode Legacy 执行链移除

**问题**: DualAgentNode 同时存在 `execute()` 和 `execute_with_context()`，导致执行路径分叉。

**设计约束**:
```python
# ❌ 禁止: execute() 方法（已完全移除）
# result = await node.execute(subject_context, task, pipeline_id)  # 不存在！

# ✅ 正确: 统一使用 execute_with_context()
from autoBMAD.docuswarm.node_execution.context_builder import create_context_builder

execution_context = create_context_builder().build(
    pipeline_id=pipeline_id,
    node_id=node.node_id,
    original_context={"content": task, "task": task, **context_data}
)
result = await node.execute_with_context(execution_context)
```

**桥接方法移除**:
```python
# ❌ 已移除: 所有 legacy 桥接方法
# node._build_execution_context_from_legacy(...)  # 不存在！
# node._normalize_legacy_subject_context(...)     # 不存在！
```

### P1: 验证/存储层兼容层清理 (High)

#### ContextValidator node_id 参数移除

**设计约束**:
```python
# ❌ 禁止: node_id 参数（已移除）
# validator.validate_execution_context(context, node_id="xxx")  # TypeError!

# ✅ 正确: 仅接受 context 参数
validator.validate_execution_context(context)
```

#### StateManager state 字段冗余移除

**设计约束**:
```python
# ❌ 禁止: 访问冗余 state 字段
# pipeline["state"]["evaluations"]  # 不存在！

# ✅ 正确: 使用扁平化字段
pipeline["evaluations"]
pipeline["node_iterations"]
```

### P2: 边缘模块兼容层清理 (Medium)

#### Tools Function-Style API 移除

**设计约束**:
```python
# ❌ 禁止: 函数式 API（已移除）
# from autoBMAD.docuswarm.tools.create_deliverable import create_deliverable
# result = await create_deliverable(params)  # 不存在！

# ✅ 正确: 使用类式 API
from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool

tool = CreateDeliverableTool()
result = await tool.execute(params)
```

#### SDK Adapter 别名移除

**设计约束**:
```python
# ❌ 禁止: 旧别名（已移除）
# from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_sdk  # ImportError!

# ✅ 正确: 使用新名称
from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_claude
```

#### 兼容异常类移除

**设计约束**:
```python
# ❌ 禁止: 兼容异常类（已移除）
# from autoBMAD.docuswarm.exceptions import AgentError       # ImportError!
# from autoBMAD.docuswarm.exceptions import ValidationError  # ImportError!

# ✅ 正确: 使用标准异常
from autoBMAD.docuswarm.exceptions import DocuSwarmError
```

#### CLI 命令别名移除

**设计约束**:
```bash
# ❌ 禁止: 命令别名（已移除）
# $ docuswarm list-pipelines  # 不存在！

# ✅ 正确: 使用标准命令
$ docuswarm list
```

#### Node Loader Facade 移除

**设计约束**:
```python
# ❌ 禁止: Facade 导入（已移除）
# from autoBMAD.docuswarm.nodes.loader import NodeConfig  # ImportError!

# ✅ 正确: 直接导入
from autoBMAD.nodes.loader import NodeConfig
```

### 零容忍验证

**代码扫描验证**:
```bash
# 验证无 deprecated 标记
grep -r "deprecated" autoBMAD/docuswarm --include="*.py" | wc -l
# 期望: 0

# 验证无 backward compatibility
grep -r "backward compatibility" autoBMAD/docuswarm --include="*.py" | wc -l
# 期望: 0

# 验证无 legacy 标记
grep -r "_legacy_" autoBMAD/docuswarm --include="*.py" | wc -l
# 期望: 0
```

**架构守护测试**:
| 测试文件 | 验证内容 |
|----------|----------|
| `test_session_manager_cleanup.py` | SessionManager 无 legacy 参数 |
| `test_dual_agent_cleanup.py` | DualAgentNode 无 execute() 方法 |
| `test_validator_cleanup.py` | Validator 无 node_id 参数 |
| `test_state_manager_cleanup.py` | StateManager 无冗余 state 字段 |
| `test_tools_cleanup.py` | Tools 无 function-style API |
| `test_sdk_adapter_cleanup.py` | SDK Adapter 无别名 |
| `test_exceptions_cleanup.py` | 无兼容异常类 |
| `test_cli_cleanup.py` | CLI 无命令别名 |
| `test_loader_facade_cleanup.py` | Node Loader facade 已移除 |
| `test_zero_compatibility.py` | 全代码库无兼容层标记 |

### 验收标准

| 检查项 | 目标 | 验证方式 |
|--------|------|----------|
| `deprecated` 标记 | 0 | grep + AST 扫描 |
| `backward compatibility` | 0 | grep + AST 扫描 |
| `_legacy_` 标记 | 0 | grep + AST 扫描 |
| SessionManager 参数 | 仅 `config`, `tool_permissions` | 签名检查 |
| DualAgentNode 方法 | 仅 `execute_with_context` | hasattr 检查 |
| 架构测试 | 100% 通过 | pytest |

### 参考文档

- [Finding B Deep Research](../research/2026-04-04-finding-b-compatibility-layer-deep-dive.md) - 深度研究报告
- [Finding B TDD Plan](../solution/2026-04-04-finding-b-compatibility-cleanup-tdd-plan.md) - 测试驱动清理方案
- [Tech Debt Audit](../evaluation/2026-04-04-docuswarm-tech-debt-audit.md) - 技术债务审计报告


---

## Step 2: Reference Docs Preload 设计约束 (2026-04-05)

### 概述

基于 [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md) 和 [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)，实施引用文档自动预加载功能。

### 核心设计原则

| 原则 | 说明 |
|------|------|
| **预加载优于工具调用** | 引用文档内容在构建阶段注入，无需 Agent 主动调用工具 |
| **递归搜索** | 支持 `docs/` 目录及其所有子目录 |
| **最浅路径优先** | 同名文件取路径最浅的版本 |
| **内容保护** | 单文件 10K 字符截断，防止 prompt 溢出 |

### 实现规范

#### Filename Extraction

```python
# ✅ 支持的格式
- `algorithm-spec.md`      # 反引号格式
- requirements.md          # 裸文件名格式
- `config.yaml`            # YAML 扩展名
- data.json                # JSON 扩展名

# ❌ 不支持的格式
- 'algorithm-spec.md'      # 单引号
- "requirements.md"        # 双引号
- /docs/algorithm-spec.md  # 路径前缀
```

#### Directory Search Order

```
docs/
├── algorithm-spec.md      ← 最浅路径 (优先选择)
├── bubble-sort/
│   └── algorithm-spec.md  ← 较深路径 (忽略)
└── research/
    └── algorithm-spec.md  ← 最深路径 (忽略)
```

#### Content Truncation

```python
MAX_DOC_CONTENT_LENGTH = 10000  # 字符

# 原始内容 > 10K 字符
truncated = content[:10000] + "\n\n[内容已截断]"
```

### 组件职责

| 组件 | 职责 | 文件 |
|------|------|------|
| `NodeExecutionContextBuilder` | 构建上下文，调用 `_resolve_reference_docs()` | `context_builder.py` |
| `_resolve_reference_docs()` | 提取文件名、搜索文件、读取内容 | `context_builder.py` |
| `NodePromptContractBuilder` | 渲染 `docs_context` 到提示词 | `contract_builder.py` |
| `executor.py` | 传递 `repo_root` 参数 | `executor.py` |

### 安全约束

```python
# ✅ 正确: 使用 PathValidator
from autoBMAD.docuswarm.tools.file_tools import PathValidator

validator = PathValidator([str(repo_root / "docs")])
abs_path = validator.validate(str(candidate))

# ❌ 错误: 直接读取任意路径
content = Path(filename).read_text()  # 安全风险!
```

### 测试约束

| 测试类型 | 数量 | 覆盖内容 |
|----------|------|----------|
| 单元测试 | 8+ | 文件名提取、搜索逻辑、截断、边界情况 |
| 集成测试 | 2+ | 完整链路、Bubble Sort 场景 |
| 架构测试 | 1+ | 安全边界验证 |

### 与旧设计的区别

| 方面 | 旧设计 (P1-2) | 新设计 (Step 2) |
|------|---------------|-----------------|
| **触发方式** | ~~Agent 调用 `read_document` 工具~~ | 预加载注入 |
| **实现位置** | ~~`ContextResolver`~~ | `NodeExecutionContextBuilder` |
| **搜索范围** | ~~受控白名单~~ | `docs/` 递归搜索 |
| **工具依赖** | ~~需要 MCP 工具~~ | 无需工具调用 |

### 参考文档

- [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)
- [方案B可行性研究](../research/2026-04-05-plan-b-read-docs-file-feasibility-research.md)
- [Architecture Doc](../architecture/04_STATE_ARCHITECTURE.md#6-reference-docs-preload-architecture-step-2)

---

## F9: SDK Message Type Handling 设计约束 (2026-04-06)

### 概述

基于 [根因分析报告](../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md)，代码错误地假设 SDK 消息对象有 `role` 属性，而 `claude_agent_sdk v0.1.68` 的 `AssistantMessage`/`TextBlock` 等类型根本没有这些字段，导致所有消息被过滤。

**核心问题**:
- `AssistantMessage` 无 `role` 属性 → `getattr(msg, "role", "")` 返回空字符串
- `TextBlock` 无 `type` 属性 → `getattr(item, "type", "")` 无法匹配
- `_message_to_dict()` 过滤所有消息 → `single_prompt()` 返回空列表

### 设计约束

#### 约束 1: 禁止使用 `getattr()` 检查消息类型

```python
# ❌ 禁止: 使用 getattr 获取 role
msg_role = getattr(msg, "role", "")
if msg_role == "assistant":  # 对 AssistantMessage 永远为 False
    ...

# ✅ 正确: 使用 isinstance() 类型检查
from claude_agent_sdk.types import AssistantMessage, UserMessage

if isinstance(msg, AssistantMessage):
    role = "assistant"
elif isinstance(msg, UserMessage):
    role = "user"
```

#### 约束 2: 禁止使用 `getattr()` 检查 ContentBlock 类型

```python
# ❌ 禁止: 使用 getattr 获取 type
item_type = getattr(item, "type", "")
if item_type == "text":  # 对 TextBlock 永远不匹配
    ...

# ✅ 正确: 使用 isinstance() 类型检查
from claude_agent_sdk.types import TextBlock, ThinkingBlock

if isinstance(item, TextBlock):
    text = item.text
elif isinstance(item, ThinkingBlock):
    # ThinkingBlock 有 thinking/signature，无 text
    pass
```

#### 约束 3: 统一消息转换入口

```python
# ❌ 禁止: Agent 层自行转换消息
async for msg in session.prompt(user_message):
    msg_dict = {
        "role": getattr(msg, "role", "unknown"),  # 错误!
        "content": getattr(msg, "content", []),
    }

# ✅ 正确: 使用 SessionManager._message_to_dict()
from autoBMAD.docuswarm.llm.session_manager import SessionManager

async for msg in session.prompt(user_message):
    msg_dict = session_manager._message_to_dict(msg)  # 正确处理 SDK 类型
    if msg_dict:
        messages.append(msg_dict)
```

#### 约束 4: 向后兼容处理

```python
# ✅ 正确: 同时处理 SDK 类型和旧格式 dict
if isinstance(msg, dict):
    # 旧格式 dict，直接使用
    return msg

if isinstance(msg, AssistantMessage):
    role = "assistant"
elif isinstance(msg, UserMessage):
    role = "user"
else:
    # Fallback: 尝试获取 role 属性
    role = getattr(msg, "role", None)
```

### SDK 类型速查表

| 类型 | 关键字段 | 无此属性 |
|------|----------|----------|
| `AssistantMessage` | `content`, `model` | `role` |
| `UserMessage` | `content` | `role` |
| `SystemMessage` | `subtype`, `data` | `role` |
| `ResultMessage` | `result`, `is_error` | `role` |
| `TextBlock` | `text` | `type` |
| `ThinkingBlock` | `thinking`, `signature` | `type` |
| `ToolUseBlock` | `name`, `input`, `id` | `type` |
| `ToolResultBlock` | `tool_use_id`, `content` | `type` |

### 影响文件

| 文件 | 方法 | 修复方式 |
|------|------|----------|
| `llm/response.py` | `extract_text_from_messages()` | 使用 `isinstance(msg, AssistantMessage)` |
| `llm/session_manager.py` | `_message_to_dict()` | 使用 `isinstance()` 判断类型，手动设置 role |
| `agents/independent.py` | `_call_llm_with_prompts()` | 使用 `SessionManager._message_to_dict()` |
| `agents/independent.py` | `_extract_content_from_messages()` | 适配转换后的 dict 格式 |

### 测试约束

所有消息处理代码必须测试以下场景：

| 测试场景 | 说明 |
|----------|------|
| `AssistantMessage` 无 role | 模拟 SDK 实际消息结构 |
| `TextBlock` 无 type | 模拟 SDK 实际 content block |
| 混合消息列表 | `SystemMessage` + `AssistantMessage` + `ResultMessage` |
| 旧格式兼容 | 带 `role` 属性的 dict 消息 |
| 空 content | `AssistantMessage(content=[])` |
| 仅 ThinkingBlock | `AssistantMessage(content=[ThinkingBlock])` |

### 验收标准

- [ ] `grep -r 'getattr.*role' autoBMAD/docuswarm/llm --include="*.py"` 返回空结果
- [ ] `grep -r 'getattr.*type' autoBMAD/docuswarm/llm --include="*.py"` 仅允许非消息处理代码
- [ ] 单元测试覆盖所有 SDK 消息类型
- [ ] Pipeline 完整执行后生成预期的 `.md` 交付物
- [ ] 无 `no_text_extracted` warning（正常响应时）

### 参考文档

- [Root Cause Analysis](../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md) - 根因分析报告
- [Test-Driven Fix Plan](../solution/2026-04-06-kimi-message-extraction-tdd-plan.md) - 测试驱动修复方案
- [LLM Integration Arch](../architecture/05_LLM_INTEGRATION.md#10-sdk-message-type-handling-best-practices) - SDK 消息处理最佳实践

---

## SDK MCP 迁移设计约束 (2026-04-05)

### 概述

基于 [FastMCP SDK 兼容性研究报告](../research/fastmcp-sdk-compatibility-issue.md) 和 [SDK MCP 迁移方案 A](../research/sdk-mcp-migration-plan-a.md)，已完成从 FastMCP 到 SDK MCP 格式的迁移。

**问题**: `TypeError: Object of type FastMCP is not JSON serializable` 导致 ClaudeSDKClient 无法创建会话。

**解决方案**: 将 `create_file_read_server()` 和 `create_search_server()` 从 FastMCP 格式改为 SDK MCP 格式。

### 核心变更

| 文件 | 变更 | 影响 |
|-----|-----|------|
| `tools/file_tools.py` | `create_file_read_server()` 返回 SDK MCP dict | 服务器创建方式 |
| `tools/search_tools.py` | `create_search_server()` 返回 SDK MCP dict | 服务器创建方式 |
| `llm/tool_filter.py` | `create_mcp_servers()` 返回 `dict[str, Any]` | 调用方需适配 |
| `llm/session_manager.py` | `_create_options()` 直接使用 dict | 简化逻辑 |

### 设计约束

**1. 返回类型约束**:
```python
# ✅ 正确: 返回 SDK MCP dict
def create_file_read_server(...) -> dict[str, Any]:
    return create_sdk_mcp_server(...)

# ❌ 错误: 返回 FastMCP 对象 (会导致 JSON 序列化错误)
def create_file_read_server(...) -> FastMCP:
    return FastMCP(...)
```

**2. 工具命名约束**:
```python
# ✅ 正确: 工具名不含 server 前缀 (SDK 自动添加)
@tool('read_document', '...', {...})

# ❌ 错误: 工具名包含完整路径 (导致重复前缀)
@tool(f"mcp__docuswarm-files-{node_id}__read_document", '...', {...})
```

**3. 返回值格式约束**:
```python
# ✅ 正确: SDK MCP 返回值格式
return {'content': [{'type': 'text', 'text': result}]}

# ❌ 错误: 直接返回字符串
return result
```

### 验证清单

- [ ] `create_file_read_server()` 返回 `dict` 类型
- [ ] `create_search_server()` 返回 `dict` 类型
- [ ] `ClaudeSDKClient.connect()` 调用成功
- [ ] 工具命名符合 SDK 约定
- [ ] 所有 26 项测试通过

### 参考文档

- [FastMCP SDK Compatibility Issue](../research/fastmcp-sdk-compatibility-issue.md)
- [SDK MCP Migration Plan A](../research/sdk-mcp-migration-plan-a.md)
- [Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md)

---

**Document End**
---

## Pipeline Timeout Fix 设计约束 (2026-04-06)

### 概述

基于 [根因分析报告](../research/pipeline-timeout-root-cause-analysis.md) 和 [测试驱动方案](../solution/pipeline-timeout-test-driven-solution.md)，修复 Pipeline 超时与 MISSING_FILE_PATH 错误。

**问题摘要**:
- 所有节点超时（1200s）
- 错误码 `MISSING_FILE_PATH`
- 三重失败: 超时 + Partial Messages 错误处理 + 验证失败

### Fix-1: JSON 示例完整性 (P0)

**设计约束**:
```python
# contract_builder.py _build_instructions_section()
# ✅ 必须包含 file_path 和 sha256 示例
{
  "deliverable": {
    "title": "...",
    "content": "...",
    "file_path": "path/returned/by/create_deliverable/tool.md",  # 必须
    "sha256": "hash_returned_by_create_deliverable_tool"          # 必须
  }
}

# ✅ 必须包含 IMPORTANT 提示
"""
**IMPORTANT**:
- You MUST include "file_path" and "sha256" from the create_deliverable tool output
"""
```

**验证**:
- `test_instructions_section_contains_file_path_example`
- `test_instructions_section_contains_sha256_example`

### Fix-2: Tool Result Extraction (P0)

**设计约束**:
```python
# independent.py
# ✅ 必须实现 _extract_create_deliverable_result()
def _extract_create_deliverable_result(
    self, messages: list[dict[str, Any]]
) -> tuple[str | None, str | None]:
    """从 messages 中提取 tool_result.
    
    关键: content 是 JSON字符串，必须先 json.loads()
    """
    for msg in messages:
        for block in msg.get("content", []):
            if block.get("type") != "tool_result" or block.get("is_error"):
                continue
            
            tool_output = block.get("content", {})
            
            # ✅ 必须处理 JSON 字符串格式
            if isinstance(tool_output, str):
                tool_output = json.loads(tool_output)
            
            if isinstance(tool_output, dict) and "file_path" in tool_output:
                return tool_output["file_path"], tool_output.get("sha256", "")
    
    return None, None
```

**验证**:
- `test_extract_from_json_string_content_case_a`
- `test_extract_from_dict_content_case_b`
- `test_extract_skips_error_results`

### Fix-3: Timeout Diagnostics (P1)

**设计约束**:
```python
# session_manager.py ClaudeSessionWrapper.prompt()
# ✅ 必须维护 messages_received 计数器
messages_received = 0
try:
    async with asyncio.timeout(effective_timeout):
        async for msg in self._client.receive_messages():
            messages_received += 1  # 计数
            yield msg
except TimeoutError:
    self._logger.error(
        "prompt_timeout",
        timeout_seconds=effective_timeout,
        message_length=len(message),
        messages_received_before_timeout=messages_received,  # 必须
    )
```

**验证**:
- `test_timeout_log_contains_messages_received_count`
- `test_timeout_log_contains_message_length`

### Fix-4 & Fix-6: 验证项

| 修复 | 验证内容 | 测试文件 |
|------|----------|----------|
| Fix-4 | CreateDeliverableTool 支持 output_dir | `test_create_deliverable_fix4.py` |
| Fix-6 | 两条 system_prompt 路径对齐 | `test_prompt_path_alignment_fix6.py` |

### 修复后架构

```
┌─────────────────────────────────────────────────────────────┐
│                Pipeline Timeout Fix Architecture             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  contract_builder.py                                        │
│  └── _build_instructions_section()                          │
│      └── JSON 示例包含 file_path/sha256 (Fix-1)            │
│                                                             │
│  independent.py                                             │
│  ├── _extract_create_deliverable_result()                   │
│  │   └── 从 tool_result 提取 file_path/sha256 (Fix-2)      │
│  └── _parse_response()                                      │
│      └── markdown_fallback 使用提取结果                     │
│                                                             │
│  session_manager.py                                         │
│  └── ClaudeSessionWrapper.prompt()                          │
│      └── 超时日志包含 messages_received (Fix-3)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 验收标准

| 检查项 | 测试文件 | 通过标准 |
|--------|----------|----------|
| Fix-1 | `test_contract_builder_fix1.py` | 6/6 通过 |
| Fix-2 | `test_independent_agent_fix2.py` | 7/7 通过 |
| Fix-3 | `test_session_manager_fix3.py` | 3/3 通过 |
| Fix-4 | `test_create_deliverable_fix4.py` | 4/4 通过 |
| Fix-6 | `test_prompt_path_alignment_fix6.py` | 2/2 通过 |
| **总计** | **25 个测试** | **25/25 通过** |

### 参考文档

- [根因分析报告](../research/pipeline-timeout-root-cause-analysis.md)
- [测试驱动方案](../solution/pipeline-timeout-test-driven-solution.md)
- [修复设计文档](./pipeline-timeout-fix-design.md)
- [架构更新](../architecture/02_AGENT_ARCHITECTURE.md#10-response-format-and-tool-integration-fixed-2026-04-06)


---

## Deep Reform 设计约束 (2026-04-06)

### 概述

基于 `docs/research/docuswarm-deep-reform` 系列研究，实施 DocuSwarm 深度架构改革。本文档汇总改革相关的设计约束。

### 改革领域

| 领域 | 核心变更 | 状态 | 参考文档 |
|------|----------|------|----------|
| **技能引入** | SDK Skills 机制集成 | 🔄 In Progress | `01-skills-introduction-mechanism.md` |
| **任务重构** | Analyst 职责转变 | 🔄 In Progress | `02-node-task-skill-mapping.md` |
| **文档约束** | 单/多文档约束 | 🔄 In Progress | `03-document-creation-constraints.md` |
| **摘要 Agent** | 引用文档摘要预生成 | ⏳ Pending | `06-summary-agent-design.md` |
| **F3-F8 修复** | 实现缺口修复 | 🔄 In Progress | `F3-F4-F5-*.md`, `F6-F7-F8-*.md` |

### 技能引入设计约束

#### 混合方案实施

采用**方案C（混合方案）**：SDK原生discovery + system prompt快速参考 + node.yaml whitelist控制。

```yaml
# node.yaml - skills 配置
tools:
  skills:
    sdk_native: true              # 启用 SDK 原生机制
    whitelist:                    # 技能白名单
      - bmad-product-brief
      - bmad-domain-research
      - bmad-market-research
    quick_reference_enabled: true # 在 system prompt 中显示技能列表
```

```python
# session_manager.py - 启用 SDK Skills
options_dict = {
    "cwd": self._cwd,
    "setting_sources": ["project"],  # 启用 .claude/skills/ 自动发现
    "allowed_tools": ["Skill", ...],  # 必须包含 "Skill"
}
```

```python
# independent.py - 技能快速参考注入
from autoBMAD.docuswarm.prompts.skill_injector import SkillInjector

skills_quick_ref = SkillInjector.build_skills_quick_reference(
    node_id=self.node_id,
    node_skill_config=node_config.tool_permissions.skills,
)
if skills_quick_ref:
    system_prompt_append += "\n\n" + skills_quick_ref
```

#### 约束清单

| 约束 | 说明 | 验证 |
|------|------|------|
| `setting_sources` | 必须包含 `"project"` | 配置检查 |
| `allowed_tools` | 必须包含 `"Skill"` | 工具列表检查 |
| `skill_ref` | 每个节点必须指定 skill_ref | node.yaml 校验 |
| `whitelist` | 技能必须在白名单中 | 运行时检查 |

### Analyst 任务重构设计约束

#### 任务语义转变

| 属性 | 旧值 | 新值 |
|------|------|------|
| **task.name** | `create-business-analysis-report` | `create-product-brief` |
| **persona.name** | `Analyst` | `Mary` |
| **persona.role** | `Data Analyst` | `Strategic Business Analyst & Product Discovery Expert` |
| **task.skill_ref** | - | `bmad-product-brief` |

#### node.yaml 更新

```yaml
# analyst/node.yaml
node_id: analyst
name: Analyst

task:
  name: create-product-brief
  description: |
    通过协作发现创建产品简介。作为产品发现促进者，
    引导用户理解产品意图，理解产品愿景后再分析工件。
  role_supplement: |
    你是产品发现促进者，不是数据扫描器。
    先与用户协作澄清产品意图，再基于澄清后的理解分析工件。
  skill_ref: bmad-product-brief

tools:
  skills:
    sdk_native: true
    whitelist:
      - bmad-product-brief
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
```

#### persona.json 更新

```json
{
  "name": "Mary",
  "role": "Strategic Business Analyst & Product Discovery Expert",
  "identity": "Product discovery facilitator who guides teams to understand product intent",
  "communication_style": "treasure_hunter_energy",
  "expertise": [
    "Product discovery and market research",
    "Porter's Five Forces framework",
    "SWOT analysis",
    "Requirements elicitation"
  ]
}
```

### 文档创建约束设计约束

#### 三层约束实施

```
配置层 (node.yaml)
    ↓
验证层 (Validator)
    ↓
执行层 (Orchestrator)
```

#### node.yaml 配置

```yaml
# analyst/pm/ux - 单文档约束
deliverable:
  max_deliverables: 1
  required_sections: [...]

# architect/po - 多文档支持（无限制）
deliverable:
  # max_deliverables 省略或设为 null
  required_sections: [...]
```

#### CreateDeliverableParams 扩展

```python
class CreateDeliverableParams(BaseModel):
    title: str
    content: str
    metadata: dict[str, Any]
    
    # 新增：多文档支持
    document_index: int | None = Field(
        default=None,
        description="If set, this is document N in a multi-document set (1-indexed)"
    )
    document_total: int | None = Field(
        default=None,
        description="Total number of documents in the set"
    )
    document_type: str | None = Field(
        default=None,
        description="Document type/category (e.g., 'epic-list')"
    )
```

#### MCP Schema 暴露

```python
# create_deliverable_sdk.py
@tool(
    "create_deliverable",
    "...",
    {
        "type": "object",
        "properties": {
            "title": {...},
            "content": {...},
            "document_index": {"type": "integer", "minimum": 1},
            "document_total": {"type": "integer", "minimum": 1},
            "document_type": {"type": "string"},
        },
    },
)
```

### F3-F8 实现缺口修复设计约束

#### F3: 多文档支持修复

| 缺口 | 修复方式 | 验证 |
|------|----------|------|
| MCP Schema 未暴露参数 | 添加 `document_index/total/type` 到 schema | Schema 检查 |
| `submit_execution_report` 单文档 | Schema 改为 `deliverables` 数组 | 契约测试 |
| `DualAgentNode` 单文档存储 | 新增 `documents` 列表属性 | 单元测试 |

#### F4: docs_context 传递链修复

| 断点 | 位置 | 修复方式 |
|------|------|----------|
| 断点1 | `contracts.py` | `IndependentAgentInput` 添加 `docs_context` 字段 |
| 断点2 | `isolation.py` | `build_independent_input()` 传递 `docs_context` |
| 断点3 | `independent.py` | `execute_with_input()` 读取 `docs_context` |

#### F5: 类型一致性修复

```python
# orchestrator.py
# ✅ 正确: 转换为 dict 列表
docs_context_summary = [d.to_dict() for d in result]

# ❌ 错误: 直接存储对象
docs_context_summary = result  # list[DocumentSummary]
```

#### F6: update_context MCP 暴露修复

```python
# tool_filter.py
# 新增: 创建 update_context server
if self.tool_permissions.shared_context.enabled and pipeline_id:
    from autoBMAD.docuswarm.tools.update_context_sdk import create_update_context_server
    
    update_server = create_update_context_server(
        pipeline_id=pipeline_id,
        node_id=self.node_id,
        allowed_operations=self.tool_permissions.shared_context.operations,
    )
    servers[update_server["name"]] = update_server
```

#### F7: Analyst 任务语义重构

参见上述"Analyst 任务重构设计约束"。

#### F8: 模板对齐修复

```python
# template_loader.py
# ✅ 正确: 指向 docuswarm/templates/
DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# ❌ 错误: 指向 prompts/templates/
# DEFAULT_TEMPLATES_DIR = Path(__file__).parent / "templates"
```

### 验收标准

| 检查项 | 验收标准 | 验证方式 |
|--------|----------|----------|
| Skills 集成 | Agent 提示词包含技能快速参考 | 日志检查 |
| Analyst 重构 | task.name == "create-product-brief" | 配置检查 |
| 单文档约束 | analyst/pm/ux max_deliverables=1 | 配置检查 |
| 多文档参数 | MCP Schema 暴露 document_index | Schema 检查 |
| F4 传递链 | `docs_context` 到达 Agent Prompt | 集成测试 |
| F5 类型 | `docs_context_summary` 为 list[dict] | 类型检查 |
| F6 MCP | `update_context` 工具可见 | 工具列表检查 |
| F8 模板 | TemplateLoader 路径正确 | 单元测试 |

### 参考文档

- [Deep Reform 研究目录](../research/docuswarm-deep-reform/README.md)
- [执行摘要](../research/docuswarm-deep-reform/REPORT_SUMMARY.md)
- [技能引入机制](../research/docuswarm-deep-reform/01-skills-introduction-mechanism.md)
- [节点任务重构](../research/docuswarm-deep-reform/02-node-task-skill-mapping.md)
- [文档创建约束](../research/docuswarm-deep-reform/03-document-creation-constraints.md)
- [F3/F4/F5 实现缺口](../research/docuswarm-deep-reform/F3-F4-F5-implementation-gap-research-report.md)
- [F6/F7/F8 深度研究](../research/docuswarm-deep-reform/F6-F7-F8-deep-research-report.md)

---

**Document End**
