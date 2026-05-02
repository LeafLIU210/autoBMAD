# Pipeline State Consistency Deep Research Report

Generated from: /home/leafliu/autoBMAD/autoBMAD/docuswarm
Log file: /home/leafliu/autoBMAD/logs/docuswarm-2026-05-01.log
DB file: /home/leafliu/autoBMAD/docuswarm.db

---

## STATE-1: 完成状态仍保留 current_node='po'，会误导 status/resume/cancel 语义
**Severity:** High

### Evidence
- DB state_json: status='completed', current_node='po', completed_nodes=['analyst', 'pm', 'ux', 'architect', 'po']
- BUG CONFIRMED: completed pipeline still has current_node set. This makes it appear as if the pipeline is still running on 'po'.
- DB top-level columns: status='completed', current_node='po'
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/graph.py: executor sets current_node to node_id at start of each node.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py: HybridOrchestrator.start_pipeline() writes final_current_node = result.get('current_node', 'po') back to DB.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py:687: Found potential current_node clearing: initial_state["current_node_session_id"] = session_id if session_resumed else None
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py:984: Found potential current_node clearing: initial_state["current_node_session_id"] = None  # Clear session_id for restart

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/graph.py**
```python
new_state["current_node"] = node_id
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py**
```python
final_current_node = result.get("current_node", "po")
```

**Recommendation:** finalize_pipeline_state() 或 graph finalize executor 应显式写: state["current_node"] = None; state["last_node"] = previous_current_node。

---

## STATE-2: node_iterations 统计与实际 DualAgent iteration 不一致
**Severity:** High

### Evidence
- DB state_json node_iterations: {'analyst': 2, 'pm': 2, 'ux': 2, 'architect': 2, 'po': 2}
- ANOMALY: analyst shows 2 iterations, but logs show dual_agent_approved iteration=1 for all nodes.
- ANOMALY: pm shows 2 iterations, but logs show dual_agent_approved iteration=1 for all nodes.
- ANOMALY: ux shows 2 iterations, but logs show dual_agent_approved iteration=1 for all nodes.
- ANOMALY: architect shows 2 iterations, but logs show dual_agent_approved iteration=1 for all nodes.
- ANOMALY: po shows 2 iterations, but logs show dual_agent_approved iteration=1 for all nodes.
- Log analysis: Found 5 'dual_agent_approved' events with iterations: ['1', '1', '1', '1', '1']
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/graph.py: Uses executed_node_state.get('iteration', 1) for node_iterations. But NodeResult.iteration may have off-by-one or adapter drift.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/graph.py**
```python
        # P1-1 Fix: Use the iteration value reported by the node executor directly,
        # rather than incrementing unconditionally. This ensures node_iterations
        # reflects actual rounds executed by DualAgentNode.
        node_status = executed_node_state.get("status", "")
        if node_status != "failed":
            actual_iteration = executed_node_state.get("iteration", 1)
            result_state["node_iterations"][node_id] = actual_iteration
        else:
            if "failed_nodes" not in result_state:
                result_state["failed_nodes"] = []
            if node_id not in result_state["failed_nodes"]:
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/nodes/dual_agent.py**
```python
                node configuration and runtime state.

        Returns:
            NodeResult containing deliverable, questions, evaluation, iteration, and timestamp.

        Raises:
            DualAgentNodeError: If execution fails.
```

**Recommendation:** 统一 iteration 语义: attempt_index(即将执行第几次), iterations_executed(已完成), dual_agent_iterations(evaluator 修订循环次数)。最小修复: 让 NodeResult.iteration 表示实际执行轮数，禁止二次递增。

---

## STATE-3: emergency finalize 写入非法状态 'interrupted' 并绕开 state_json
**Severity:** High

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/cli/services/pipeline_service.py: _emergency_finalize() executes raw SQL setting status='interrupted'.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/storage/state_manager.py: PIPELINE_STATUSES = ("pending", "running", "completed", "failed", "paused", "cancelled"). 'interrupted' is NOT in this list.
- CONFIRMED: 'interrupted' is an ILLEGAL status value.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/cli/services/pipeline_service.py: _emergency_finalize() does NOT update state_json. It only updates the top-level pipelines.status column. This breaks the single-source-of-truth principle.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/cli/services/pipeline_service.py**
```python
        if pipeline_id is None:
            return
        try:
            conn = sqlite3.connect(self._db_path)
            conn.execute(
                "UPDATE pipelines SET status = 'interrupted', updated_at = CURRENT_TIMESTAMP "
                "WHERE pipeline_id = ? AND status = 'running'",
                (pipeline_id,)
            )
            conn.commit()
            conn.close()
```

**Recommendation:** 方案A: 将 'interrupted' 纳入合法状态，并通过 StateManager.update_pipeline_state() 写完整 state。方案B: 将中断统一映射为 'cancelled' 或 'failed'。

---

## STATE-4: StateManager.update_pipeline_state() 对完整 result 使用 deep merge，可能保留旧字段
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/storage/state_manager.py: update_pipeline_state() calls _deep_merge() instead of full replacement.
- Impact: resume/restart 后可能残留旧 questions、evaluations、session_metadata。节点重跑时删除字段不容易生效，因为 merge 不支持删除语义。

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/storage/state_manager.py**
```python
    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """Deep merge source dict into target dict.

        Args:
            target: The dictionary to merge into (modified in place).
            source: The dictionary to merge from.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                value_dict: dict[str, Any] = value
                self._deep_merge(target[key], value_dict)
            else:
                target[key] = value

    def get_latest_successful_run(
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/storage/state_manager.py**
```python
                    )

                # Parse current state
                current_state: dict[str, Any] = {}
                if row["state_json"]:
                    current_state = json.loads(cast(str, row["state_json"]))

                # Deep merge the update
                self._deep_merge(current_state, state_update)

                # Write back to database
```

**Recommendation:** 拆分 API: patch_pipeline_state() 用 deep merge，replace_pipeline_state() 做完整替换。HybridOrchestrator final write 应使用 replace 语义。

---

## STATE-5: pipeline_started 日志事件在执行完成后才输出
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py: 'pipeline_started' log event is emitted AFTER graph.ainvoke() completes.
- Log analysis: 'pipeline_started' appears at 89.9% of log file (near the END), confirming it is emitted after completion.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py**
```python
            result["status"] = final_status
            result["current_node"] = final_current_node
            await self._state_manager.update_pipeline_state(
                final_pipeline_id,
                result,
            )

            logger.info(
                "pipeline_started",
                pipeline_id=final_pipeline_id,
                result=result,
            )

            # P1 Fix: Return full status dict instead of just pipeline_id
```

**Recommendation:** 把当前事件改名为 'pipeline_completed' 或 'pipeline_finished'。真正的 'pipeline_started' 应在 update status=running 后、graph 执行前记录。

---

## STATE-EXTRA: Top-level DB columns 与 state_json 之间的一致性检查
**Severity:** Info

### Evidence
- Top-level status: 'completed' | state_json status: 'completed'
- Top-level current_node: 'po' | state_json current_node: 'po'
- status is CONSISTENT between top-level and state_json.
- current_node is CONSISTENT between top-level and state_json.

**Recommendation:** 

---
