# Blocking Question Mechanism Deep Research Report

Generated from: /home/leafliu/autoBMAD/autoBMAD/docuswarm
Log file: /home/leafliu/autoBMAD/logs/docuswarm-2026-05-01.log
DB file: /home/leafliu/autoBMAD/docuswarm.db

---

## F1: QuestionHandler 没有持久化，CLI 查询/回答在真实运行后不可用
**Severity:** High

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/questions.py: QuestionHandler._questions is a plain in-memory dict, not persisted to disk or database.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/cli/commands/answer.py: Each CLI invocation creates a NEW QuestionHandler instance, so it cannot see questions collected during pipeline execution.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/cli/commands/questions.py: Same issue - new QuestionHandler per CLI call, get_unanswered_questions() always returns empty for historical pipelines.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/questions.py**
```python
self._questions: dict[str, list[Question]] = {}
```

**Recommendation:** 删除 QuestionHandler 的交互式内存管理职责。若保留问题展示，应直接从 pipeline final state 的 questions 字段读取。

---

## F2: create_dual_agent_node 默认没有注入 QuestionHandler，问题收集器不是主路径组件
**Severity:** High

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/nodes/dual_agent.py: DualAgentNode.__init__ accepts question_handler, but it is optional.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/nodes/dual_agent.py: create_dual_agent_node() does NOT pass question_handler to DualAgentNode constructor. The main execution path never enables QuestionHandler.collect_questions().

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/nodes/dual_agent.py**
```python
def create_dual_agent_node(
    config: Any,  # Actually Config, but config package uses dynamic import
    session_manager: SessionManager,
    node_id: str,
    project_root: Path | None = None,
    max_iterations: int | None = None,
) -> DualAgentNode:
    """Create a DualAgentNode with configured agents.

    P0 Fix: max_iterations now defaults to None, which triggers loading from node config.

    Args:
        config: Agent configuration.
        session_manager: SessionManager for SDK interactions.
        node_id: The node identifier for persona/criteria loading.
        project_root: 
```

**Recommendation:** 删除 DualAgentNode 的 question_handler 参数与 collect_questions() 调用。保留 NodeResult.questions 直接原样入 state。

---

## F3: README 描述的 paused/answer/resume 流程与代码不一致
**Severity:** High

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/README.md: README makes interactive Q&A promises: ["README mentions 'questions' and 'answer' commands", "README mentions 'paused' status", "README mentions 'blocking' questions"]. But as shown in F1/F2, the underlying implementation does not support cross-process question persistence or pause/resume driven by blocking questions.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/storage/state_manager.py: 'paused' is in PIPELINE_STATUSES, but no code links it to blocking question detection.

**Recommendation:** 同步更新 README: 删除'管理问题与回答'章节，删除 paused 状态说明，改为'节点诊断与后续事项'。

---

## F4: blocking 语义鼓励代理提问，但用户不回答时会污染成功输出
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/prompts/contract_builder.py: Prompt explicitly instructs agent to generate 'blocking' questions and says 'Must be answered before proceeding'.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/tools/create_deliverable_sdk.py: Tool schema enum includes 'blocking' as valid priority.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/context/validator.py: Validator VALID_PRIORITIES includes 'blocking'.
- DB pipeline state (status=completed): Found 2 blocking questions in a COMPLETED pipeline. This proves blocking questions do NOT block execution.
-   - [ux] PM 提供的 PRD 中是否已将输出格式 `1 + 1 = 2` 与退出码 0 列为验收标准？如未明确，建议 UX 与 PM 对齐以避免下游实现偏差。...
-   - [po] 上游交付物（analyst分析报告、prd产品需求文档、architect技术架构文档）在文件系统中未找到实物文件，是否应以提示中提供的「上游交付物摘要」和 calc-context.md / use...

**Recommendation:** 移除 blocking priority，改为只允许 clarifying/optional。真正阻断的场景应由 evaluator 返回 BLOCKED 或 executor 抛出错误。

---

## F5: 存在第二套 QuestionPriority 定义，priority 语义已经分叉
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/questions.py: Defines QuestionPriority as Enum with BLOCKING, CLARIFYING, OPTIONAL (uppercase).
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/response.py: Defines DIFFERENT QuestionPriority as Literal[low, medium, high, critical]. This is completely incompatible with the pipeline enum.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/context/validator.py: Uses lowercase set {blocking, clarifying, optional}.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/questions.py: Uses .upper() to bridge lowercase input to uppercase enum. This masks the design divergence.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/response.py**
```python
QuestionPriority = Literal["low", "medium", "high", "critical"]
```

**Recommendation:** 同步删除 llm/response.py 中未被真正使用的 QuestionPriority 类型别名，或标记为 deprecated。统一对外口径为小写 clarifying/optional。

---

## F6: 完全删除 questions 字段会损失有用的审计信号
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/node_execution/executor.py: Node executor writes questions into result, showing they are intended as delivery metadata.
- DB pipeline state contains 15 questions across 5 nodes. These expose upstream context gaps, assumptions, and follow-up items.
-   analyst: 3 total (blocking=0, clarifying=2, optional=1)
-   pm: 3 total (blocking=0, clarifying=1, optional=2)
-   ux: 3 total (blocking=1, clarifying=1, optional=1)
-   architect: 3 total (blocking=0, clarifying=2, optional=1)
-   po: 3 total (blocking=1, clarifying=1, optional=1)

**Recommendation:** 不要一刀切删除所有 questions 数据流。建议改为 diagnostics/follow_ups，去掉'必须回答'语义，作为 report metadata 保存和导出。

---

## CROSS: Cross-cutting: 所有源代码中 blocking 相关引用汇总
**Severity:** Info

### Evidence
- Found 24 lines referencing 'blocking' in docuswarm Python source:
-   autoBMAD/docuswarm/context/validator.py:586: VALID_PRIORITIES: set[str] = {"blocking", "clarifying", "optional"}
-   autoBMAD/docuswarm/prompts/contract_builder.py:707: "priority": "blocking | clarifying | optional",
-   autoBMAD/docuswarm/prompts/contract_builder.py:721: - **blocking**: Must be answered before proceeding
-   autoBMAD/docuswarm/storage/state_manager.py:6: executor if they need non-blocking I/O.
-   autoBMAD/docuswarm/pipeline/questions.py:7: - Question prioritization (BLOCKING, CLARIFYING, OPTIONAL)
-   autoBMAD/docuswarm/pipeline/questions.py:34: BLOCKING: Questions that prevent pipeline progression until answered.
-   autoBMAD/docuswarm/pipeline/questions.py:39: BLOCKING = "BLOCKING"
-   autoBMAD/docuswarm/pipeline/questions.py:84: >>> handler.has_blocking_questions("pipeline-123")
-   autoBMAD/docuswarm/pipeline/questions.py:113: - priority: Priority level ("BLOCKING", "CLARIFYING", "OPTIONAL")
-   autoBMAD/docuswarm/pipeline/questions.py:124: ...         "priority": "BLOCKING",
-   autoBMAD/docuswarm/pipeline/questions.py:196: def has_blocking_questions(self, pipeline_id: str) -> bool:
-   autoBMAD/docuswarm/pipeline/questions.py:197: """Check if pipeline has any unanswered blocking questions.
-   autoBMAD/docuswarm/pipeline/questions.py:203: True if there are unanswered blocking questions, False otherwise.
-   autoBMAD/docuswarm/pipeline/questions.py:206: return any(q.priority == QuestionPriority.BLOCKING for q in unanswered)
-   autoBMAD/docuswarm/tools/create_deliverable_sdk.py:107: "enum": ["blocking", "clarifying", "optional"],
-   autoBMAD/docuswarm/tools/create_deliverable_sdk.py:108: "description": "Priority level: blocking (must answer), clarifying (help refine), optional (nice-to-have)",
-   autoBMAD/docuswarm/cli/commands/questions.py:26: Displays questions sorted by priority: blocking (red), clarifying (yellow), optional (dimmed).
-   autoBMAD/docuswarm/cli/commands/questions.py:43: QuestionPriority.BLOCKING: 0,
-   autoBMAD/docuswarm/cli/commands/questions.py:54: if question.priority == QuestionPriority.BLOCKING:
-   autoBMAD/docuswarm/cli/commands/questions.py:57: priority_label = "BLOCKING"
-   autoBMAD/docuswarm/agents/independent.py:7: - Generates questions with priorities: blocking, clarifying, optional
-   autoBMAD/docuswarm/agents/independent.py:228: "priority": "blocking | clarifying | optional",
-   autoBMAD/docuswarm/agents/independent.py:242: | **blocking** | Must be answered before proceeding | Use when missing critical information that prevents task completion. You MUST have an answer to proceed. |
-   autoBMAD/docuswarm/agents/independent.py:283: 3. **Use ONLY valid priority values**: "blocking", "clarifying", "optional"

**Recommendation:** 

---
