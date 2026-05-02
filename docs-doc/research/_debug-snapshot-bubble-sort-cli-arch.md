# DocuSwarm 离线诊断报告

## 范围

- 项目根目录: `D:\GITHUB\DocuSwarm`
- 目标流水线: `pipeline-1772787008108-cf362dbf`

## 数据库快照

- pipeline_id: `pipeline-1772787008108-cf362dbf`
- subject: `bubble-sort-cli-arch`
- status: `completed`
- current_node: `po`
- created_at: `2026-03-06 08:50:08`
- updated_at: `2026-03-06 09:01:23`
- state keys: `['content', 'context_file', 'subject']`
- node_results rows: `0`
- node_runs rows: `0`

## 工具注册快照

- ToolRegistry before importing tools package: `0`
- ToolRegistry after importing tools package: `6`
- Registered tool names: `['create_deliverable', 'create_document_set', 'list_docs_files', 'read_docs_file', 'update_context', 'update_docs_file']`

## 发现

- [HIGH] 流水线被标记为 completed，但状态快照几乎为空: `pipelines.state_json` 只保留了初始上下文，没有同步 LangGraph 最终状态；这会让 CLI/排障无法从数据库还原真实执行结果。
- [HIGH] 节点执行失败已写入日志，但数据库没有对应节点运行记录: 集成执行路径没有把失败节点写入 `node_results`/`node_runs`，导致日志、数据库、CLI 状态三者失真。
- [HIGH] IndependentAgent 未触发 `create_deliverable` 工具: 日志显示各节点返回了文本/消息，但 `ToolResultExtractor` 未提取到任何 `create_deliverable` 调用；这意味着代理提示词、工具注册、SDK 工具桥接三者至少有一处断链。
- [HIGH] 节点失败后流水线仍可能被最终标记为 completed: 当前图执行层把失败节点包装成普通状态返回，且集成执行器无条件追加 `completed_nodes`，最终 `finalize_pipeline_state()` 直接把整体状态置为 `completed`。
- [HIGH] 工具注册依赖导入副作用，但生产执行路径没有显式导入工具包: 运行时验证表明 `ToolRegistry` 在默认导入路径下为空，只有显式 `import autoBMAD.docuswarm.tools` 后才出现工具；这与 `IndependentAgent` 中“工具已通过 ToolRegistry 注册”的假设不一致。

## 日志样本

```text
2026-03-06T08:50:41.654504Z [error    ] no_deliverable_tool_called     agent=IndependentAgent node_id=analyst response_count=3 run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:50:41.654504Z [error    ] independent_agent_failed       error=No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. iteration=1 node=DualAgentNode node_id=analyst run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:50:41.654504Z [error    ] node_execution_failed          error=Independent Agent failed on iteration 1: No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. error_type=IndependentExecutionError node_id=analyst run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:53:13.357556Z [error    ] no_deliverable_tool_called     agent=IndependentAgent node_id=pm response_count=7 run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:53:13.358563Z [error    ] independent_agent_failed       error=No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. iteration=1 node=DualAgentNode node_id=pm run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:53:13.358563Z [error    ] node_execution_failed          error=Independent Agent failed on iteration 1: No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. error_type=IndependentExecutionError node_id=pm run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:55:47.287810Z [error    ] no_deliverable_tool_called     agent=IndependentAgent node_id=ux response_count=8 run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:55:47.287810Z [error    ] independent_agent_failed       error=No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. iteration=1 node=DualAgentNode node_id=ux run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:55:47.288330Z [error    ] node_execution_failed          error=Independent Agent failed on iteration 1: No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. error_type=IndependentExecutionError node_id=ux run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:59:41.739342Z [error    ] no_deliverable_tool_called     agent=IndependentAgent node_id=architect response_count=9 run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:59:41.740342Z [error    ] independent_agent_failed       error=No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. iteration=1 node=DualAgentNode node_id=architect run_id=pipeline-1772787008108-cf362dbf
2026-03-06T08:59:41.740342Z [error    ] node_execution_failed          error=Independent Agent failed on iteration 1: No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. error_type=IndependentExecutionError node_id=architect run_id=pipeline-1772787008108-cf362dbf
2026-03-06T09:01:23.187524Z [error    ] no_deliverable_tool_called     agent=IndependentAgent node_id=po response_count=9 run_id=pipeline-1772787008108-cf362dbf
2026-03-06T09:01:23.187524Z [error    ] independent_agent_failed       error=No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. iteration=1 node=DualAgentNode node_id=po run_id=pipeline-1772787008108-cf362dbf
2026-03-06T09:01:23.187524Z [error    ] node_execution_failed          error=Independent Agent failed on iteration 1: No create_deliverable tool was called by the agent. The agent must use the create_deliverable tool to produce output. error_type=IndependentExecutionError node_id=po run_id=pipeline-1772787008108-cf362dbf
+ Pipeline started: pipeline-1772787008108-cf362dbf
```
