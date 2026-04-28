# 2026-03-17 DocuSwarm F1-F8 深度决策研究报告

> 范围：围绕用户锁定的 F1-F8 决策，对 autoBMAD/docuswarm 的状态、上下文、工具、测试、类型与文档进行再次研究。
> 研究方式：静态代码审查、SQLite 快照检查、文档漂移扫描、当前工作区测试可见性检查

## 1. 用户已锁定的决策边界

- F1: 用奥卡姆剃刀比较 state_json 与 LangGraph checkpoint，并产出单一业务真相源判断。
- F2: 认可 shared_context 闭环修复方向。
- F3: 认可 Evaluator 输入契约闭环修复方向。
- F4: 选择 docs-free，只保留 create_deliverable / create_document_set / update_context；工具注册 API 必须收敛成一种用法。
- F5: 比较 dataclass 风格与 METADATA: JSON 兼容风格，明确拒绝 kimi SDK ToolOk/ToolError 作为系统主契约。
- F6: 不再把历史红灯直接当作当前回归质量门；当前研究只基于现工作区快照。
- F7: 认可类型系统、导出面、惰性导入收敛方向。
- F8: 认可文档收敛与去漂移方向。

## 2. 运行时快照

- 数据库存在：`True`
- 数据库路径：`D:\GITHUB\DocuSwarm\docuswarm.db`
- pipelines 条数：`51`
- checkpoints 条数：`128`
- 最新 pipeline 的 `state_json` 键：`subject, context_file, content`
- 最新 checkpoint 的 channel 键：`pipeline_id, subject_context, current_node, completed_nodes, deliverables, questions, evaluations, node_iterations, session_ids, session_metadata, current_node_session_id, status, error, __finalize__`
- 当前工作区可见测试文件数：`0`

## 3. 核心研究结论

### F1. 状态持久化与恢复链路没有闭环

- 严重级别：`P0`
- 决策：以奥卡姆剃刀判断，state_json 应成为唯一业务真相源，LangGraph checkpoint 只保留为运行期恢复快照。
- 结论依据：
  - 固定五节点顺序流水线的业务语义，明显比 LangGraph 内部 channel 语义更简单，应该让更简单的业务模型成为真相源。
  - 如果同时把 checkpoint 和 state_json 都视为完整真相，就需要长期维护双重一致性，复杂度会持续外溢到 resume、status、restart、debug 和测试。
  - 数据库样本已证明 checkpoint 比 state_json 更完整，但这恰恰说明当前真正的问题是 state_json 没有写满，而不是应该把真相源交给 checkpoint。
- 数据库证据：最新 `state_json` 键为 `subject, context_file, content`；最新 checkpoint channel 键为 `pipeline_id, subject_context, current_node, completed_nodes, deliverables, questions, evaluations, node_iterations, session_ids, session_metadata, current_node_session_id, status, error, __finalize__`
- 决策矩阵：
  - `state_json`: 业务真相=高，字段由项目自己定义，可直接映射业务状态。；稳定性=高，只要保持 PipelineState schema 稳定即可。；可运维性=高，易查库、易审计、易做 status/resume/restart 运维界面。；耦合=低，和 LangGraph 内部实现解耦。；当前缺口=当前只落了 subject_context，不是完整 PipelineState。
  - `LangGraph checkpoint`: 业务真相=中，能反映运行时快照，但语义偏框架内部。；稳定性=中低，受 LangGraph 序列化格式和 channel 结构约束。；可运维性=低，BLOB/msgpack 难以直接作为业务审计真相。；耦合=高，直接耦合框架恢复机制。；当前缺口=当前最完整，但它完整的是“框架恢复态”，不是“业务真相源”。
- 收敛动作：
  - create_pipeline / 运行中状态更新统一写入完整 PipelineState 到 state_json。
  - resume/status/restart 的业务判断统一读取 state_json，而非默认读取 checkpoint_state。
  - checkpoint 丢失时，系统仍应能依据 state_json 从 current_node 重新执行，而不是丢失恢复能力。
- 关键证据：
  - `autoBMAD/docuswarm/storage/state_manager.py:116` -> `state_json = json.dumps(subject_context or {})`
  - `autoBMAD/docuswarm/storage/state_manager.py:311` -> `"state": json.loads(cast(str, row["state_json"])) if row["state_json"] else {},`
  - `autoBMAD/docuswarm/pipeline/state.py:57` -> `class PipelineState(TypedDict):`
  - `autoBMAD/docuswarm/pipeline/state.py:77` -> `shared_context: dict[str, Any]  # P1-1: Cross-node shared context`
  - `autoBMAD/docuswarm/pipeline/state.py:80` -> `def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> PipelineState:`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:550` -> `checkpoint_state = pipeline.get("state", {})`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:605` -> `initial_state["completed_nodes"] = checkpoint_state.get("completed_nodes", [])`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:606` -> `initial_state["deliverables"] = checkpoint_state.get("deliverables", {})`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:610` -> `initial_state["session_ids"] = checkpoint_state.get("session_ids", {})`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:686` -> `checkpoint_state = pipeline.get("state", {})`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:900` -> `initial_state["completed_nodes"] = checkpoint_state.get("completed_nodes", [])`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:901` -> `initial_state["deliverables"] = checkpoint_state.get("deliverables", {})`
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:905` -> `initial_state["session_ids"] = checkpoint_state.get("session_ids", {})`

### F2. shared_context 只完成了“能写”，没有完成“能持续参与执行”

- 严重级别：`P0/P1`
- 决策：同意原建议，shared_context 必须从持久化入口延续到真实执行上下文和恢复链路。
- 结论依据：
  - StateManager 已能写 shared_context，ContextManager 也会把 shared_context 放入 IndependentAgentInput。
  - 但 IndependentAgent.execute_with_input() 又重建了 shared_context={} 的 NodeExecutionContext，导致共享上下文在真正构建 prompt 之前丢失。
  - 这使 update_context 成为“表面能力”，系统无法稳定让共享知识持续参与下游节点执行。
- 收敛动作：
  - 停止在 Agent 层重新构造缺字段上下文；直接消费 ContextManager 传入的结构化输入。
  - 补一条端到端测试：update_context -> 下一节点 prompt 可见 -> resume 后仍可见。
  - 把 shared_context 纳入 state_json 完整 schema，而不是作为临时附加字段。
- 关键证据：
  - `autoBMAD/docuswarm/storage/state_manager.py:480` -> `async def update_shared_context(`
  - `autoBMAD/docuswarm/storage/state_manager.py:534` -> `if "shared_context" not in current_state:`
  - `autoBMAD/docuswarm/storage/state_manager.py:535` -> `current_state["shared_context"] = {}`
  - `autoBMAD/docuswarm/context/isolation.py:101` -> `shared_context = execution_context.get("shared_context", {})`
  - `autoBMAD/docuswarm/context/isolation.py:112` -> `shared_context=shared_context,  # P1-1: Pass shared_context`
  - `autoBMAD/docuswarm/agents/independent.py:681` -> `shared_context={},`

### F3. Evaluator 的输入契约被重新削弱，原始上下文与交付物真相并未稳定闭环

- 严重级别：`P1`
- 决策：同意原建议，Evaluator 必须直接围绕 EvaluatorAgentInput 组装 prompt，不能再重建缩水版 NodeExecutionContext。
- 结论依据：
  - ContextManager.build_evaluator_input() 已经把 file_path 设为必填，并读取磁盘上的正式正文，这个方向是正确的。
  - EvaluatorAgent.execute_with_input() 仍然把 original_context 和 shared_context 置空后再建 contract，说明输入契约在最后一步又被削弱。
  - 结果是 Evaluator 更像在评审“文档文本质量”，而不是稳定地评审“该文档是否满足原始任务与约束”。
- 收敛动作：
  - 让 Evaluator contract builder 直接吃 EvaluatorAgentInput，而不是靠临时 NodeExecutionContext 补字段。
  - 补 prompt 快照测试，断言原始上下文摘要、正式正文、评审标准三者都稳定在最终 prompt 中。
- 关键证据：
  - `autoBMAD/docuswarm/context/isolation.py:140` -> `file_path = deliverable.get("file_path")`
  - `autoBMAD/docuswarm/context/isolation.py:149` -> `deliverable_body = path.read_text(encoding="utf-8")`
  - `autoBMAD/docuswarm/context/isolation.py:155` -> `return EvaluatorAgentInput(`
  - `autoBMAD/docuswarm/context/isolation.py:158` -> `original_context_summary=original_summary,  # P0-2`
  - `autoBMAD/docuswarm/agents/evaluator.py:571` -> `original_context={},`
  - `autoBMAD/docuswarm/agents/evaluator.py:573` -> `shared_context={},`
  - `autoBMAD/docuswarm/agents/evaluator.py:582` -> `deliverable_body=deliverable_body,`

### F4. 工具层处于产品决策未收敛状态

- 严重级别：`P0/P1`
- 决策：采用方案 A：坚持 docs-free，只保留 create_deliverable / create_document_set / update_context；工具注册 API 收敛成一种用法。
- 结论依据：
  - 运行期 agent 配置和 tools 包导出都已经朝 docs-free 收敛，但仍保留 parse_deliverable_metadata 这类旧兼容思维。
  - tool_registry.py 与 models/tool_registry.py 同时存在，且一个偏全局注册器、一个偏扩展定义模型，API 语义已经分叉。
  - 继续维持双轨只会让 prompt、测试、注册、导出和文档不断互相否定。
- 收敛动作：
  - 删除 docs 工具相关残留导出、文档、旧测试假设，明确 docs-free 是唯一有效产品决策。
  - 只保留一个 ToolRegistry 入口，其他模块改为纯重定向或直接删除。
  - 不再保留两套互相矛盾的测试并存。
- 关键证据：
  - `autoBMAD/docuswarm/tools/__init__.py:11` -> `CreateDeliverableTool,`
  - `autoBMAD/docuswarm/tools/__init__.py:15` -> `CreateDocumentSetTool,`
  - `autoBMAD/docuswarm/tools/__init__.py:19` -> `UpdateContextTool,`
  - `autoBMAD/docuswarm/tools/__init__.py:23` -> `def parse_deliverable_metadata(output: str) -> dict[str, Any]:`
  - `autoBMAD/docuswarm/tools/__init__.py:34` -> `>>> metadata = parse_deliverable_metadata(output)`
  - `autoBMAD/docuswarm/tools/__init__.py:49` -> `"CreateDeliverableTool",`
  - `autoBMAD/docuswarm/tools/__init__.py:51` -> `"CreateDocumentSetTool",`
  - `autoBMAD/docuswarm/tools/__init__.py:53` -> `"UpdateContextTool",`
  - `autoBMAD/docuswarm/tools/__init__.py:54` -> `"parse_deliverable_metadata",`
  - `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:5` -> `# NOTE: This is a docs-free configuration per P1-2 decision.`
  - `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:13` -> `- "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"`
  - `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:14` -> `- "autoBMAD.docuswarm.tools.update_context:UpdateContextTool"`
  - `autoBMAD/docuswarm/agents/configs/independent_agent.yaml:15` -> `- "autoBMAD.docuswarm.tools.create_document_set:CreateDocumentSetTool"`
  - `autoBMAD/docuswarm/tools/tool_registry.py:8` -> `class ToolRegistry:`
  - `autoBMAD/docuswarm/tools/tool_registry.py:77` -> `def get_tool_registry() -> ToolRegistry:`
  - `autoBMAD/docuswarm/tools/tool_registry.py:89` -> `def register_tool(name: str) -> Callable[[Callable[..., ToolResult]], Callable[..., ToolResult]]:`
  - `autoBMAD/docuswarm/models/tool_registry.py:26` -> `class ToolRegistryExtended(ToolRegistry):`
  - `autoBMAD/docuswarm/models/tool_registry.py:78` -> `__all__ = ["ToolRegistry", "ToolDefinition", "ToolResult"]`

### F5. ToolResult / ToolResultExtractor / 工具返回格式之间已经分叉

- 严重级别：`P1`
- 决策：主协议收敛到结构化 ToolResult/dataclass；METADATA: JSON 仅保留为边界兼容；拒绝 kimi SDK ToolOk/ToolError 作为系统主契约。
- 方案对比：
  - `结构化 Python dataclass / ToolResult`: 适配结论=推荐为主协议；优点=类型可检查、IDE 友好、便于测试和序列化。；更适合作为系统内部稳定演进契约。；能自然承载 file_path / sha256 / section_index / warnings 等结构化字段。；缺点=若外部 SDK 边界只接受文本，需要额外适配层。
  - `字符串内嵌 METADATA: JSON`: 适配结论=仅适合边界兼容层；优点=短期兼容当前以文本输出为主的调用面。；缺点=依赖字符串分隔符，天然脆弱，容易被文案或换行污染。；迫使 ToolResultExtractor、测试和 Agent 一起承担文本解析负担。
  - `kimi SDK ToolOk/ToolError`: 适配结论=明确拒绝作为系统主契约；优点=适合 SDK 边界调用。；缺点=把系统内部事实格式绑死到特定 SDK 类型。；已经与 ToolResult/dataclass 和 METADATA 文本兼容层形成三叉分裂。
- 收敛动作：
  - 让工具内部先返回统一 ToolResult，再由单一适配层决定是否包装成 SDK 所需返回类型。
  - parse_deliverable_metadata 与 ToolResultExtractor 退到边界层，不再主导系统内部协议。
  - 新工具和新测试禁止继续把 ToolOk/ToolError 当作内部事实格式。
- 关键证据：
  - `autoBMAD/docuswarm/tools/tool_result.py:8` -> `class ToolResult:`
  - `autoBMAD/docuswarm/tools/tool_result.py:11` -> `success: bool`
  - `autoBMAD/docuswarm/tools/tool_result.py:12` -> `result: Any = None`
  - `autoBMAD/docuswarm/tools/tool_result_extractor.py:103` -> `if isinstance(response, ToolResult):`
  - `autoBMAD/docuswarm/tools/tool_result_extractor.py:107` -> `return ToolResult.from_dict(response)`
  - `autoBMAD/docuswarm/tools/tool_result_extractor.py:109` -> `return ToolResult(success=True, result=response)`
  - `autoBMAD/docuswarm/tools/create_deliverable.py:16` -> `from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue`
  - `autoBMAD/docuswarm/tools/create_deliverable.py:169` -> `f"METADATA: {json.dumps(metadata, ensure_ascii=False)}"`
  - `autoBMAD/docuswarm/tools/create_deliverable.py:172` -> `return ToolOk(output=output_text)`
  - `autoBMAD/docuswarm/tools/create_document_set.py:15` -> `from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue`
  - `autoBMAD/docuswarm/tools/create_document_set.py:261` -> `return ToolOk(output=result_msg)`
  - `autoBMAD/docuswarm/tools/update_context.py:7` -> `from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue`
  - `autoBMAD/docuswarm/tools/update_context.py:183` -> `async def update_context(params: UpdateContextParams) -> ToolResult:`
  - `autoBMAD/docuswarm/tools/update_context.py:198` -> `return ToolResult(`

### F6. 测试体系不能再把历史红灯直接当作当前质量门

- 严重级别：`治理项`
- 决策：接受用户输入：历史测试已清理并重建；当前工作区快照中未发现可见测试文件，因此本报告不以旧红灯判断当前回归质量。
- 结论依据：
  - 当前工作区可见测试文件数为 0。
  - 这意味着本次研究无法用仓内旧测试直接证明当前回归状态，也不应该继续复用历史双轨假设做质量门。
- 收敛动作：
  - 新测试体系只围绕当前有效决策：state_json 单真相、docs-free、统一 ToolResult 协议。
  - 把环境敏感测试与核心契约测试分层，避免再次把噪音和真实回归混在一起。
  - 最先补齐的是 F1/F2/F3/F4/F5 的契约测试，而不是历史兼容测试。

### F7. 类型系统、导出面和惰性导入层已经出现腐蚀

- 严重级别：`P2`
- 决策：同意原建议，收敛导出面，减少惰性导入，清理重导出与名实不符的兼容层。
- 结论依据：
  - 顶层包与 node_execution 都依赖大面积 __getattr__ 做懒加载，静态可见性差，类型系统保护效果被削弱。
  - models/__init__.py 和 models/tool_registry.py 继续重导出 tools 层实体，且 ToolRegistryExtended 并未稳定暴露到 __all__，语义已经混乱。
  - 这些问题短期不一定炸运行时，但会持续拖慢重构反馈和类型检查可靠性。
- 收敛动作：
  - 优先明确公共 API 面，显式导出真正稳定的符号。
  - 减少兼容重导出，把 models/tools 的职责边界重新拉直。
  - 把 lazy import 缩到必要最小范围，配合类型检查修复 error 级问题。
- 关键证据：
  - `autoBMAD/docuswarm/__init__.py:26` -> `def __getattr__(name: str):`
  - `autoBMAD/docuswarm/__init__.py:58` -> `"IndependentAgent",`
  - `autoBMAD/docuswarm/__init__.py:60` -> `"create_node_execution",`
  - `autoBMAD/docuswarm/node_execution/__init__.py:14` -> `def __getattr__(name):`
  - `autoBMAD/docuswarm/node_execution/__init__.py:91` -> `__all__ = [`
  - `autoBMAD/docuswarm/node_execution/__init__.py:107` -> `"create_node_executor",`
  - `autoBMAD/docuswarm/node_execution/__init__.py:133` -> `"ContextValidator",`
  - `autoBMAD/docuswarm/models/__init__.py:6` -> `from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolResult`
  - `autoBMAD/docuswarm/models/__init__.py:7` -> `from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolRegistry`
  - `autoBMAD/docuswarm/models/tool_registry.py:26` -> `class ToolRegistryExtended(ToolRegistry):`
  - `autoBMAD/docuswarm/models/tool_registry.py:78` -> `__all__ = ["ToolRegistry", "ToolDefinition", "ToolResult"]`

### F8. 文档层存在漂移与质量退化信号

- 严重级别：`P2`
- 决策：同意原建议，文档要围绕当前有效决策重新分层，区分现行规范、历史方案和废弃兼容。
- 结论依据：
  - docs/design.md 与 docs/architecture.md 仍把若干中间态实现细节写成设计事实，容易把读者再次带回共享上下文被清空、Evaluator 重建缩水上下文的旧路径。
  - 仓内历史研究文档仍大量描述 checkpoint 作为主恢复视角、ToolOk/ToolError 示例等旧决策，若不标注状态，会继续污染后续实现与测试。
- 收敛动作：
  - 建立“当前生效决策索引”，明确 state_json/docs-free/ToolResult 是现行规则。
  - 为历史研究文档增加 archived / superseded 标记，避免被误读为现行架构。
  - 文档评审以后应把‘是否与当前代码和决策一致’当成独立质量门。
- 关键证据：
  - `docs/design.md:84` -> `class EvaluatorAgentInput(TypedDict):`
  - `docs/design.md:352` -> `) -> EvaluatorAgentInput:`
  - `docs/design.md:377` -> `return EvaluatorAgentInput(`
  - `docs/design.md:448` -> `shared_context={},`
  - `docs/design.md:520` -> `- Receives EvaluatorAgentInput with full deliverable_body`
  - `docs/design.md:531` -> `agent_input: EvaluatorAgentInput  # Changed from Dict to TypedDict`
  - `docs/design.md:557` -> `original_context={},`
  - `docs/design.md:559` -> `shared_context={},`
  - `docs/architecture.md:3` -> `> **Version**: 2.0 (Aligned with NodeExecutionContext Protocol)`
  - `docs/architecture.md:13` -> `1. **Single Context Protocol**: `NodeExecutionContext` is the unified contract across executor → DualAgentNode → Agents`
  - `docs/architecture.md:45` -> `│  │  │      NodeExecutionContextBuilder                 │    │   │`
  - `docs/architecture.md:49` -> `│  │  │  • Build unified NodeExecutionContext            │    │   │`
  - `docs/architecture.md:99` -> `New component for P0-2 that builds structured prompt contracts from NodeExecutionContext:`
  - `docs/architecture.md:107` -> `context: NodeExecutionContext`
  - `docs/architecture.md:113` -> `context: NodeExecutionContext,`
  - `docs/architecture.md:121` -> `### 2.2 NodeExecutionContext (Unified Protocol)`
  - `docs/architecture.md:126` -> `class NodeExecutionContext(TypedDict):`
  - `docs/architecture.md:145` -> `shared_context: Dict`
  - `docs/architecture.md:157` -> `### 2.3 NodeExecutionContextBuilder`
  - `docs/architecture.md:162` -> `class NodeExecutionContextBuilder:`
  - `docs/architecture.md:170` -> `) -> NodeExecutionContext:`
  - `docs/architecture.md:184` -> `Transforms `NodeExecutionContext` into agent-specific inputs:`
  - `docs/architecture.md:190` -> `execution_context: NodeExecutionContext,`
  - `docs/architecture.md:197` -> `execution_context: NodeExecutionContext,`
  - `docs/architecture.md:199` -> `) -> EvaluatorAgentInput:`
  - `docs/architecture.md:214` -> `│     └─▶ NodeExecutionContext ──▶ IndependentAgentInput      │`
  - `docs/architecture.md:226` -> `│     └─▶ NodeExecutionContext ──▶ EvaluatorAgentInput        │`
  - `docs/architecture.md:259` -> `NodeExecutionContextBuilder.build()`
  - `docs/architecture.md:260` -> `↓ [unified NodeExecutionContext]`
  - `docs/architecture.md:319` -> `|              |              |              │──NodeExecutionContext──▶|              |`
  - `docs/architecture.md:321` -> `|              |              │──────────NodeExecutionContext──────────▶|              |`
  - `docs/architecture.md:349` -> `2. **Step 2**: Update `executor.py` to use `NodeExecutionContextBuilder``
  - `docs/architecture.md:375` -> `- [NodeExecutionContext 深度研究报告](research/2026-03-13-p0-single-context-protocol-deep-research-report.md)`
  - `autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md:50` -> `└── Storage Layer (state_manager.py, checkpoints.py)`
  - `autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md:269` -> `checkpoint_state = pipeline.get("state", {})`
  - `autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md:403` -> `checkpoint_state = pipeline.get("state", {})`
  - `autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md:685` -> `3. 从 `state_json` 解析 `completed_nodes``
  - `autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md:756` -> `| `checkpoints.py` | 检查点管理 |`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:158` -> `checkpointer=checkpointer,`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:201` -> `return graph.compile(checkpointer=checkpointer)`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:347` -> `return ToolOk(output=f"Deliverable '{params.title}' created successfully")`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:874` -> `return ToolOk(output=f"Deliverable saved to {file_path}")`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:1080` -> `checkpointer=checkpointer,`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:1086` -> `checkpointer=checkpointer,`
  - `autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md:1146` -> `return ToolOk(output=f"Deliverable saved to {file_path}")`

## 4. 最终架构决策

- 业务真相源收敛到 state_json；checkpoint 降级为运行期恢复快照。
- shared_context 必须贯穿写入、提示词消费、恢复继续执行三段链路。
- Evaluator 直接围绕 EvaluatorAgentInput 生成 prompt，不再重建丢字段的临时上下文。
- 工具面坚持 docs-free，仅保留三个工具，并只保留一种注册 API。
- 系统内部工具返回协议收敛到结构化 ToolResult/dataclass；METADATA: JSON 仅保留在边界兼容层。
- 拒绝把 kimi SDK ToolOk/ToolError 继续扩散成内部事实格式。
- 测试门禁改为服务当前架构，而不是兼容历史双轨假设。
- 显式清理 __all__、重导出和大面积 __getattr__ 惰性导入造成的类型腐蚀。

## 5. 推荐执行顺序

1. 先补齐 state_json 与 shared_context / evaluator 契约闭环，再动工具契约与注册 API。
2. 随后统一 ToolResult 协议并删除旧测试/旧注册残留。
3. 最后做类型、导出面、文档三类工程化清理，让新测试体系稳定落地。

---

## 6. 详细研究报告索引

以下研究报告针对 F1-F8 每个核心结论进行了深度分析，包含问题诊断、收敛方案和测试建议。

### 6.1 核心研究报告

| 决策 | 研究报告 | 核心问题 | 状态 |
|------|----------|----------|------|
| **F1** | [状态持久化与恢复链路深度研究报告](./2026-03-17-F1-state-persistence-research-report.md) | state_json 与 checkpoint 双重真相源 | P0 |
| **F2** | [shared_context 持续参与执行深度研究报告](./2026-03-17-F2-shared-context-research-report.md) | shared_context 只完成"能写"未完成"能消费" | P0/P1 |
| **F3** | [Evaluator 输入契约闭环深度研究报告](./2026-03-17-F3-evaluator-input-contract-research-report.md) | Evaluator 输入契约被重新削弱 | P1 |
| **F4** | [工具层决策收敛深度研究报告](./2026-03-17-F4-tools-convergence-research-report.md) | 工具层决策未收敛，API 分裂 | P0/P1 |
| **F5** | [ToolResult 协议统一深度研究报告](./2026-03-17-F5-toolresult-protocol-research-report.md) | 工具返回格式三叉分裂 | P1 |
| **F6** | [测试体系质量门深度研究报告](./2026-03-17-F6-test-quality-gate-research-report.md) | 测试真空，需重建体系 | 治理项 |
| **F7** | [类型系统与导出面收敛深度研究报告](./2026-03-17-F7-type-system-research-report.md) | 惰性导入和重导出腐蚀 | P2 |
| **F8** | [文档层漂移与收敛深度研究报告](./2026-03-17-F8-documentation-drift-research-report.md) | 文档与当前决策不一致 | P2 |

### 6.2 调试工具

为支持深度研究，创建了以下调试工具：

| 工具 | 路径 | 用途 | 对应决策 |
|------|------|------|----------|
| **State Analyzer** | [tools/docuswarm_state_analyzer.py](../../tools/docuswarm_state_analyzer.py) | 分析 state_json 与 checkpoint 状态 | F1 |
| **Context Tracer** | [tools/docuswarm_context_tracer.py](../../tools/docuswarm_context_tracer.py) | 追踪 shared_context 和 Evaluator 输入链路 | F2, F3 |

#### 使用示例

```bash
# 分析数据库状态 (F1)
python tools/docuswarm_state_analyzer.py --db docuswarm.db

# 分析特定 pipeline
python tools/docuswarm_state_analyzer.py --pipeline pipeline-xxx

# 检查 shared_context 链路 (F2)
python tools/docuswarm_context_tracer.py --check-shared-context

# 检查 Evaluator 输入契约 (F3)
python tools/docuswarm_context_tracer.py --check-evaluator-input

# 检查所有 Context 链路
python tools/docuswarm_context_tracer.py --trace-all
```

### 6.3 文档导航

```
docs/research/
├── 2026-03-17-docuswarm-decision-research-report.md (本文档 - 总览)
├── 2026-03-17-F1-state-persistence-research-report.md
├── 2026-03-17-F2-shared-context-research-report.md
├── 2026-03-17-F3-evaluator-input-contract-research-report.md
├── 2026-03-17-F4-tools-convergence-research-report.md
├── 2026-03-17-F5-toolresult-protocol-research-report.md
├── 2026-03-17-F6-test-quality-gate-research-report.md
├── 2026-03-17-F7-type-system-research-report.md
└── 2026-03-17-F8-documentation-drift-research-report.md

tools/
├── docuswarm_state_analyzer.py    (F1 调试工具)
└── docuswarm_context_tracer.py    (F2, F3 调试工具)
```

---

## 7. 后续行动

1. **阅读详细报告**: 根据优先级（P0 > P1 > P2）阅读对应的研究报告
2. **运行调试工具**: 使用调试工具验证当前系统状态
3. **制定实施计划**: 基于"推荐执行顺序"制定具体的开发计划
4. **建立质量门**: 参考 F6 报告建立新的测试体系
5. **更新文档**: 参考 F8 报告建立决策索引和文档标记规范
