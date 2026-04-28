---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F1-F8 深度决策研究报告 (2026-03-17-docuswarm-decision-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史研究文档，已被 F1-F8 决策体系取代。当前决策以 `docs/DECISIONS.md` 为准。

**2026-04-05 更新**: `docs_context` 字段实现细节已更新，详见 [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md)。
---

# P0 方案B 实施设计文档

> **文档类型**: 实施设计文档 (已归档)  
> **版本**: 1.0 (历史版本)  
> **日期**: 2026-03-13  
> **归档日期**: 2026-03-17  
> **状态**: 已归档  
>  
> 本文档基于《NodeExecutionContext 深度研究报告》的深入分析，提供方案B的详细实施设计。

## 1. 设计目标

消除上下文链路的三个根问题:
1. ❌ `executor` 从 state 里"猜 task"
2. ❌ `DualAgentNode` 把已有结构重新包装成 `{subject, task}`
3. ❌ `IndependentAgent` 再次尝试从字符串或嵌套 dict 里恢复上下文

替换为:
1. ✅ 单一 `NodeExecutionContext` 协议
2. ✅ 显式构建，无猜测逻辑
3. ✅ 层间只传递，不重新包装

## 2. 核心数据结构

### 2.1 NodeExecutionContext

```python
# autoBMAD/docuswarm/node_execution/contracts.py

from typing import Any, TypedDict


class DeliverableRequirements(TypedDict, total=False):
    """交付物要求"""
    required_sections: list[str]
    template_title: str
    output_filename: str
    format_hints: dict[str, Any]


class NodeExecutionContext(TypedDict):
    """
    统一节点执行上下文。
    
    这是跨越 executor -> DualAgentNode -> IndependentAgent/EvaluatorAgent 的单一协议。
    不允许在层间传 str(context_json) 作为主协议。
    不允许 agent 端再去"猜字段"。
    不允许 task 与 subject_context 重复承载同一含义。
    """
    # === 身份标识 ===
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    
    # === 任务契约 ===
    task_name: str
    task_description: str
    role_supplement: str
    
    # === 交付物契约 ===
    deliverable_type: str
    deliverable_requirements: DeliverableRequirements
    
    # === 上下文数据 ===
    original_context: dict[str, Any]  # 用户输入的原始上下文
    chained_deliverables: list[dict[str, Any]]  # 上游节点交付物
    shared_context: dict[str, Any]  # 跨节点共享上下文
    
    # === 迭代状态 ===
    iteration_feedback: dict[str, Any] | None
    
    # === 扩展上下文 ===
    docs_context: list[dict[str, Any]]


class IndependentAgentInput(TypedDict):
    """
    IndependentAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。
    """
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: DeliverableRequirements
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    persona_context: dict[str, Any]  # persona 加载的额外上下文


class EvaluatorAgentInput(TypedDict):
    """
    EvaluatorAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。
    """
    task_name: str
    task_description: str
    deliverable_artifact: dict[str, Any]  # 交付物元数据
    deliverable_body: str  # 交付物正文（从文件读取）
    criteria: list[dict[str, Any]]
```

## 3. NodeExecutionContextBuilder 实现

```python
# autoBMAD/docuswarm/node_execution/context_builder.py

from typing import Any

from autoBMAD.docuswarm.nodes.loader import NodeConfig, NodeLoader

from .contracts import DeliverableRequirements, NodeExecutionContext


class NodeExecutionContextBuilder:
    """
    构建统一的 NodeExecutionContext。
    
    兼容旧 node.yaml schema，同时支持未来新 schema。
    """
    
    def __init__(self, loader: NodeLoader | None = None) -> None:
        self.loader = loader or NodeLoader()
    
    def build(
        self,
        pipeline_id: str,
        node_id: str,
        original_context: dict[str, Any],
        chained_deliverables: list[dict[str, Any]] | None = None,
        shared_context: dict[str, Any] | None = None,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> NodeExecutionContext:
        """
        构建 NodeExecutionContext。
        
        Args:
            pipeline_id: 流水线ID
            node_id: 节点ID
            original_context: 原始上下文（用户输入）
            chained_deliverables: 链式上游交付物
            shared_context: 共享上下文
            iteration_feedback: 迭代反馈
            
        Returns:
            完整的 NodeExecutionContext
        """
        # 1. 加载节点配置
        node_config = self.loader.load(node_id)
        
        # 2. 构建 DeliverableRequirements
        deliverable_reqs = self._build_deliverable_requirements(node_config)
        
        # 3. 组装上下文
        return NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id=node_id,
            node_name=node_config.name,
            node_order=node_config.sequence,
            
            # 任务契约 - 兼容适配
            task_name=node_config.name,  # 旧 schema: name -> task_name
            task_description=node_config.description,  # 旧 schema: description -> task_description
            role_supplement="",  # 旧 schema 默认值，新 schema 后可配置
            
            # 交付物契约
            deliverable_type=node_config.deliverable_type,
            deliverable_requirements=deliverable_reqs,
            
            # 上下文数据
            original_context=original_context,
            chained_deliverables=chained_deliverables or [],
            shared_context=shared_context or {},
            
            # 迭代状态
            iteration_feedback=iteration_feedback,
            
            # 扩展上下文（Step 2: 引用文档预加载）
            # 由 _resolve_reference_docs() 自动填充
            docs_context=docs_context if repo_root else [],
        )
    
    def _build_deliverable_requirements(
        self, 
        node_config: NodeConfig
    ) -> DeliverableRequirements:
        """
        从 NodeConfig 构建 DeliverableRequirements。
        
        兼容旧 schema 的映射:
        - required_sections <- deliverable.required_sections
        - template_title <- deliverable_type (默认)
        """
        reqs: DeliverableRequirements = {}
        
        # 从 node_config 的 deliverable 字段提取
        if hasattr(node_config, 'deliverable') and node_config.deliverable:
            if 'required_sections' in node_config.deliverable:
                reqs['required_sections'] = node_config.deliverable['required_sections']
        
        # 默认 template_title
        reqs['template_title'] = node_config.deliverable_type
        
        return reqs


def create_context_builder(loader: NodeLoader | None = None) -> NodeExecutionContextBuilder:
    """工厂函数，创建 NodeExecutionContextBuilder 实例。"""
    return NodeExecutionContextBuilder(loader=loader)
```

## 4. 修改 executor.py

```python
# autoBMAD/docuswarm/node_execution/executor.py (修改后)

async def _execute_node(
    state: NodeRunState,
    node_id: str,
    session_manager: KimiSessionManager,
    logger: Any,
) -> NodeRunState:
    """Execute a node and update NodeRunState."""
    run_id = state.get("run_id", "unknown")
    pipeline_id = state.get("pipeline_id", "")
    
    logger.info("node_execution_started", node_id=node_id, run_id=run_id)
    
    new_state = copy.deepcopy(state)
    new_state["status"] = RUNNING
    
    try:
        # ==== 修改开始 ====
        # Step 1: 构建 NodeExecutionContext (替代 _extract_task_from_state)
        from .context_builder import create_context_builder
        
        context_builder = create_context_builder()
        
        # 解析原始上下文
        original_context = _parse_original_context(state.get("context_file", ""))
        
        # 构建统一的执行上下文
        execution_context = context_builder.build(
            pipeline_id=pipeline_id,
            node_id=node_id,
            original_context=original_context,
            chained_deliverables=_extract_chained_deliverables(state),
            shared_context=state.get("shared_context", {}),
        )
        
        logger.debug(
            "execution_context_built",
            node_id=node_id,
            task_name=execution_context["task_name"],
        )
        
        # Step 2: 创建 DualAgentNode
        config = _get_config()
        project_root = Path(__file__).parent.parent.parent.resolve()
        
        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id=node_id,
            project_root=project_root,
        )
        
        # Step 3: 执行节点 - 直接传入 execution_context
        result = await node.execute_with_context(execution_context)
        # ==== 修改结束 ====
        
        # ... 后续状态更新逻辑不变
        new_state["deliverable"] = result.deliverable
        new_state["questions"] = result.questions
        new_state["evaluation"] = result.evaluation
        new_state["iteration"] = state.get("iteration", 1) + 1
        
        # 处理 verdict...
        verdict = result.evaluation.get("verdict") if result.evaluation else None
        # ...
        
    except Exception as e:
        logger.error("node_execution_failed", node_id=node_id, run_id=run_id, error=str(e))
        new_state["status"] = FAILED
    
    return new_state


def _parse_original_context(context_file: str) -> dict[str, Any]:
    """解析原始上下文文件内容。"""
    import json
    
    if not context_file:
        return {}
    
    try:
        data = json.loads(context_file)
        if isinstance(data, dict):
            return data
        return {"content": str(data)}
    except json.JSONDecodeError:
        return {"content": context_file}


def _extract_chained_deliverables(state: NodeRunState) -> list[dict[str, Any]]:
    """提取链式上游交付物。"""
    chained = state.get("chained_context", {})
    deliverables = []
    
    for node_id, context in chained.items():
        if "deliverable" in context:
            deliverables.append({
                "node_id": node_id,
                "deliverable": context["deliverable"],
            })
    
    return deliverables
```

## 5. 修改 DualAgentNode

```python
# autoBMAD/docuswarm/nodes/dual_agent.py (修改后)

class DualAgentNode:
    """
    Dual-Agent Node - 修改后版本。
    接收 NodeExecutionContext，不再二次包装。
    """
    
    async def execute_with_context(
        self,
        execution_context: NodeExecutionContext,
    ) -> NodeResult:
        """
        使用 NodeExecutionContext 执行双代理流程。
        
        Args:
            execution_context: 统一的节点执行上下文
            
        Returns:
            NodeResult 包含 deliverable, questions, evaluation
        """
        pipeline_id = execution_context["pipeline_id"]
        
        self.logger.info(
            "starting_dual_agent_execution",
            node_id=self.node_id,
            task_name=execution_context["task_name"],
        )
        
        iteration = 0
        previous_feedback: dict[str, Any] | None = None
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # ==== 修改开始 ====
            # Step 1: 使用 ContextManager 从 execution_context 构建 Independent 输入
            independent_input = self.context_manager.build_independent_input(
                execution_context=execution_context,
                iteration_feedback=previous_feedback,
            )
            
            # 直接传递，不再包装
            independent_output = await self.independent_agent.execute(independent_input)
            # ==== 修改结束 ====
            
            # Step 2: 过滤并构建 Evaluator 输入
            filtered_output = self.context_filter.filter_for_evaluator(independent_output)
            
            # ==== 修改开始 ====
            evaluator_input = self.context_manager.build_evaluator_input(
                execution_context=execution_context,
                deliverable=filtered_output.get("deliverable"),
            )
            
            evaluation = await self.evaluator_agent.execute(evaluator_input)
            # ==== 修改结束 ====
            
            # 处理 verdict...
            verdict = evaluation.get("verdict", "NEEDS_REVISION")
            
            if verdict == "APPROVED":
                break
            elif verdict == "BLOCKED":
                break
            else:
                # 准备下一轮反馈
                previous_feedback = {
                    "alignment_score": evaluation.get("alignment_score", 0.0),
                    "verdict": verdict,
                    "issues_found": evaluation.get("issues_found", []),
                    "suggestions": evaluation.get("suggestions", []),
                }
        
        return NodeResult(
            deliverable=independent_output.get("deliverable", {}),
            questions=independent_output.get("questions", []),
            evaluation=evaluation,
            iteration=iteration,
            timestamp=datetime.now(),
        )
```

## 6. 修改 ContextManager

```python
# autoBMAD/docuswarm/context/isolation.py (修改后)

from autoBMAD.docuswarm.node_execution.contracts import (
    EvaluatorAgentInput,
    IndependentAgentInput,
    NodeExecutionContext,
)


class ContextManager:
    """
    ContextManager - 修改后版本。
    基于 NodeExecutionContext 裁剪不同的 Agent 输入。
    """
    
    def build_independent_input(
        self,
        execution_context: NodeExecutionContext,
        iteration_feedback: dict[str, Any] | None = None,
    ) -> IndependentAgentInput:
        """
        构建 IndependentAgent 的输入。
        
        从 NodeExecutionContext 中提取必要字段，组装为 AgentInput。
        """
        # 构建原始上下文摘要
        original = execution_context["original_context"]
        summary = original.get("content", "") if isinstance(original, dict) else str(original)
        
        # 构建上游交付物摘要
        chained_summary = []
        for item in execution_context["chained_deliverables"]:
            deliverable = item.get("deliverable", {})
            chained_summary.append({
                "node_id": item.get("node_id"),
                "title": deliverable.get("title", "Untitled"),
                "summary": deliverable.get("content", "")[:200],  # 只取摘要
            })
        
        return IndependentAgentInput(
            task_name=execution_context["task_name"],
            task_description=execution_context["task_description"],
            role_supplement=execution_context["role_supplement"],
            deliverable_requirements=execution_context["deliverable_requirements"],
            original_context_summary=summary,
            chained_deliverables_summary=chained_summary,
            iteration_feedback=iteration_feedback,
            persona_context={},  # 由 IndependentAgent 自行加载
        )
    
    def build_evaluator_input(
        self,
        execution_context: NodeExecutionContext,
        deliverable: dict[str, Any] | None,
    ) -> EvaluatorAgentInput:
        """
        构建 EvaluatorAgent 的输入。
        
        Evaluator 需要看到完整的交付物正文，而不仅仅是摘要。
        """
        # 如果 deliverable 包含 file_path，读取完整内容
        deliverable_body = ""
        if deliverable:
            file_path = deliverable.get("file_path")
            if file_path:
                # 从文件读取完整内容
                try:
                    from pathlib import Path
                    content = Path(file_path).read_text(encoding='utf-8')
                    deliverable_body = content
                except Exception:
                    deliverable_body = deliverable.get("content", "")
            else:
                deliverable_body = deliverable.get("content", "")
        
        return EvaluatorAgentInput(
            task_name=execution_context["task_name"],
            task_description=execution_context["task_description"],
            deliverable_artifact=deliverable or {},
            deliverable_body=deliverable_body,
            criteria=[],  # 由 EvaluatorAgent 自行加载
        )
```

## 7. 新增 NodePromptContractBuilder (P0-2)

```python
# autoBMAD/docuswarm/prompts/contract_builder.py

from typing import TypedDict
from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext


class IndependentPromptContract(TypedDict):
    """Independent Agent 的 Prompt 契约"""
    persona_section: str
    task_section: str
    deliverable_section: str
    context_section: str
    instructions_section: str


class EvaluatorPromptContract(TypedDict):
    """Evaluator Agent 的 Prompt 契约"""
    task_section: str
    criteria_section: str
    deliverable_section: str
    context_section: str


class NodePromptContractBuilder:
    """Builds prompt contracts for Independent and Evaluator Agents.
    
    Design Principle:
    - System prompt: stable persona + fixed instructions
    - User prompt: dynamic task contract + context
    """
    
    def build_independent_contract(
        self,
        context: NodeExecutionContext,
    ) -> IndependentPromptContract:
        """Build IndependentPromptContract from NodeExecutionContext."""
        return {
            "persona_section": self._build_persona_section(context),
            "task_section": self._build_task_section(context),
            "deliverable_section": self._build_deliverable_section(context),
            "context_section": self._build_context_section(context),
            "instructions_section": self._build_instructions_section(),
        }
    
    def build_evaluator_contract(
        self,
        context: NodeExecutionContext,
        deliverable_body: str,
    ) -> EvaluatorPromptContract:
        """Build EvaluatorPromptContract from NodeExecutionContext."""
        return {
            "task_section": self._build_evaluator_task_section(context),
            "criteria_section": self._build_criteria_section(context),
            "deliverable_section": deliverable_body,
            "context_section": self._build_evaluator_context_section(context),
        }
    
    def render_independent_system_prompt(
        self, 
        contract: IndependentPromptContract
    ) -> str:
        """Render system prompt (stable: persona + instructions)."""
        sections = [
            contract["persona_section"],
            contract["instructions_section"],
        ]
        return "\n\n".join(filter(None, sections))
    
    def render_independent_user_prompt(
        self, 
        contract: IndependentPromptContract
    ) -> str:
        """Render user prompt (dynamic: task + deliverable + context)."""
        sections = [
            contract["task_section"],
            contract["deliverable_section"],
            contract["context_section"],
        ]
        return "\n\n".join(filter(None, sections))


def create_contract_builder() -> NodePromptContractBuilder:
    """Factory function for NodePromptContractBuilder."""
    return NodePromptContractBuilder()
```

**设计原则**:
- System prompt 包含稳定的 persona 和固定指令
- User prompt 包含动态的任务契约和上下文
- 旧 schema 兼容: `task_name` ← `node.name`, `task_description` ← `node.description`

详细 TDD 方案: [TDD-P0-NodePromptContractBuilder.md](../solution/TDD-P0-NodePromptContractBuilder.md)

## 8. 修改 IndependentAgent (使用 ContractBuilder)

```python
# autoBMAD/docuswarm/agents/independent.py (修改后)

from autoBMAD.docuswarm.node_execution.contracts import IndependentAgentInput


class IndependentAgent(BaseAgent):
    """
    IndependentAgent - 修改后版本。
    接收结构化的 IndependentAgentInput，不再反向解析。
    """
    
    async def execute(self, agent_input: IndependentAgentInput) -> IndependentOutput:
        """
        执行 Independent Agent。
        
        Args:
            agent_input: 结构化的 Agent 输入，直接从字段读取，无需解析
            
        Returns:
            包含 deliverable 和 questions 的输出
        """
        # ==== 修改开始 ====
        # 直接从 agent_input 字段读取，无需猜测或解析
        task_name = agent_input["task_name"]
        task_description = agent_input["task_description"]
        role_supplement = agent_input["role_supplement"]
        deliverable_reqs = agent_input["deliverable_requirements"]
        original_context = agent_input["original_context_summary"]
        chained_deliverables = agent_input["chained_deliverables_summary"]
        iteration_feedback = agent_input["iteration_feedback"]
        # ==== 修改结束 ====
        
        # 构建 user_message
        user_message = self._build_user_message(
            task_name=task_name,
            task_description=task_description,
            role_supplement=role_supplement,
            deliverable_reqs=deliverable_reqs,
            original_context=original_context,
            chained_deliverables=chained_deliverables,
            iteration_feedback=iteration_feedback,
        )
        
        # 调用 LLM...
        response = await self._call_llm(user_message)
        output = self._parse_response(response)
        
        return output
    
    def _build_user_message(
        self,
        task_name: str,
        task_description: str,
        role_supplement: str,
        deliverable_reqs: dict[str, Any],
        original_context: str,
        chained_deliverables: list[dict[str, Any]],
        iteration_feedback: dict[str, Any] | None,
    ) -> str:
        """构建 user message。"""
        sections = []
        
        # 任务契约
        sections.append(f"## 任务: {task_name}")
        sections.append(f"{task_description}")
        if role_supplement:
            sections.append(f"\n**角色补充**: {role_supplement}")
        
        # 交付物要求
        sections.append("\n## 交付物要求")
        if "required_sections" in deliverable_reqs:
            sections.append("必须包含以下章节:")
            for section in deliverable_reqs["required_sections"]:
                sections.append(f"- {section}")
        
        # 原始上下文
        if original_context:
            sections.append(f"\n## 原始上下文\n{original_context}")
        
        # 上游交付物
        if chained_deliverables:
            sections.append("\n## 上游交付物摘要")
            for item in chained_deliverables:
                sections.append(f"- **{item['node_id']}**: {item['title']}")
        
        # 迭代反馈
        if iteration_feedback:
            sections.append("\n## 迭代反馈")
            sections.append(f"上一轮评分: {iteration_feedback.get('alignment_score', 0)}")
            sections.append("需要改进的问题:")
            for issue in iteration_feedback.get("issues_found", []):
                sections.append(f"- {issue}")
        
        return "\n".join(sections)
```

## 9. 迁移检查清单

### Phase 1: 基础设施
- [ ] 创建 `contracts.py` 定义数据结构
- [ ] 创建 `context_builder.py` 实现构建逻辑
- [ ] 添加单元测试验证数据结构

### Phase 2: 替换 executor
- [ ] 修改 `executor.py` 使用 context_builder
- [ ] 删除 `_extract_task_from_state()`
- [ ] 验证 executor 输出正确的 execution_context

### Phase 3: 重构 DualAgentNode
- [ ] 添加 `execute_with_context()` 方法
- [ ] 修改 `ContextManager` 的方法签名
- [ ] 验证不再进行二次包装

### Phase 4: 新增 NodePromptContractBuilder
- [ ] 创建 `prompts/contract_builder.py` (TDD 驱动)
- [ ] 实现 IndependentPromptContract 构建
- [ ] 实现 EvaluatorPromptContract 构建
- [ ] 实现 prompt 渲染方法

### Phase 5: 重构 Agents (使用 ContractBuilder)
- [ ] 修改 `IndependentAgent.execute()` 接收 AgentInput
- [ ] 修改 `IndependentAgent` 使用 `NodePromptContractBuilder`
- [ ] 删除反向解析逻辑
- [ ] 修改 `EvaluatorAgent.execute()` 接收 AgentInput
- [ ] 修改 `EvaluatorAgent` 使用 `NodePromptContractBuilder`

### Phase 6: 集成测试
- [ ] 验证完整链路: executor -> DualAgentNode -> Agents
- [ ] 验证 prompt 中包含节点契约信息
- [ ] 验证五个节点的 prompt 差异正确
- [ ] 验证 contract builder 生成的 prompt 结构正确

## 9. 风险评估与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 旧测试依赖旧字段 | 高 | 中 | 保留旧字段只读兼容层，逐步迁移测试 |
| 状态序列化变化 | 中 | 高 | NodeExecutionContext 保持可序列化 |
| 性能下降 | 低 | 低 | 构建上下文是一次性开销，影响可忽略 |

## 10. Step 2 更新: docs_context 实现 (2026-04-05)

> **注意**: `docs_context` 字段的实现已更新。原计划由"上层填充"改为"自动预加载"。

### Step 2 实现细节

```python
# autoBMAD/docuswarm/node_execution/context_builder.py

def _resolve_reference_docs(
    self,
    original_context: dict[str, Any],
    node_id: str,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """从 original_context 中提取并读取引用文档。
    
    搜索策略:
    1. 从 content 字段提取文件名（反引号格式和裸文件名）
    2. 在 docs/ 目录下递归查找文件
    3. 同名文件取路径最浅的版本
    4. 内容超过 10000 字符自动截断
    """
    content = original_context.get("content", "")
    if not content:
        return []
    
    # 提取文件名
    patterns = [
        r'`([^`]+\.(?:md|txt|yaml|yml|json))`',
        r'\b([\w-]+\.(?:md|txt|yaml|yml|json))\b',
    ]
    
    referenced_files: set[str] = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        referenced_files.update(matches)
    
    # 在 docs/ 目录下递归查找
    docs_dir = repo_root / "docs"
    docs_context: list[dict[str, Any]] = []
    
    for filename in referenced_files:
        candidates = sorted(docs_dir.rglob(filename), key=lambda p: len(p.parts))
        for candidate in candidates:
            if candidate.is_file():
                try:
                    file_content = candidate.read_text(encoding="utf-8")
                    if len(file_content) > 10000:
                        file_content = file_content[:10000] + "\n\n[内容已截断]"
                    docs_context.append({
                        "filename": filename,
                        "path": str(candidate.relative_to(repo_root)),
                        "content": file_content,
                    })
                except (OSError, UnicodeDecodeError):
                    continue
                break
    
    return docs_context
```

### ContractBuilder 渲染更新

```python
# autoBMAD/docuswarm/prompts/contract_builder.py

def _build_context_section(self, context: NodeExecutionContext) -> str:
    """构建上下文章节."""
    sections: list[str] = []

    # 原始上下文
    original_context = context.get("original_context", {})
    if original_context:
        content = original_context.get("content", "")
        if content:
            sections.append(f"## 原始上下文\n{content}")

    # 引用文档（Step 2 新增）
    docs = context.get("docs_context", [])
    if docs:
        sections.append("\n## 引用文档")
        for doc in docs:
            sections.append(f"\n### {doc['filename']}\n")
            sections.append(doc['content'])

    # ... 其他章节
    
    return "\n".join(sections)
```

### 参考文档

| 文档 | 说明 |
|------|------|
| [Step 2 TDD Plan](../solution/2026-04-05-step2-reference-docs-preload-tdd-plan.md) | Step 2 测试驱动方案 |
| [方案B可行性研究](2026-04-05-plan-b-read-docs-file-feasibility-research.md) | 可行性深度分析 |
| [NodeExecutionContext 深度研究报告](2026-03-13-p0-single-context-protocol-deep-research-report.md) | 问题分析与流转链路 |
| [原始方案B计划](2026-03-13-p0-single-context-protocol-plan.md) | 原始方案设计 |
| [P0 重构总览](2026-03-13-docuswarm-context-refactor-overview.md) | 重构顺序与依赖关系 |
| [上下文注入审计](2026-03-13-context-injection-audit.md) | 审计发现 (F001-F007) |
| [节点Prompt注入计划](2026-03-13-p0-node-prompt-injection-plan.md) | Prompt 注入方案 |
| [TDD-P0-NodePromptContractBuilder.md](../solution/TDD-P0-NodePromptContractBuilder.md) | 测试驱动开发方案 |
| [单一交付物真相计划](2026-03-13-p0-single-truth-deliverable-plan.md) | 交付物存储方案 |
| [Architecture Document](../architecture.md) | 架构文档 |
| [Design Document](../design.md) | 详细设计文档 |
| [PRD](../plan/PRD.md) | 产品需求文档 |
| [tools/node_execution_context_researcher.py](../../tools/node_execution_context_researcher.py) | 研究工具 |
| [tools/node_execution_context_example.py](../../tools/node_execution_context_example.py) | 示例演示工具 |
