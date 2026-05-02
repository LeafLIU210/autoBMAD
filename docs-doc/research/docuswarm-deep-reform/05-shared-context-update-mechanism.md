# Shared Context 更新机制研究报告

## 1. 概述

### 研究目标

本报告深入研究 DocuSwarm 项目中 Shared Context 的更新机制，设计独立 Agent 在执行期间调用工具更新共享上下文的完整方案。

### 背景与前置结论

Task 4（工具权限方案研究）已完成，核心发现：
- 工具权限体系完备，支持 5 个工具的权限管理
- 项目已存在 `update_context.py` 工具，实现基本共享上下文更新功能
- 本报告在此基础上进行全面系统分析和优化设计

---

## 2. 当前 Shared Context 体系分析

### 2.1 PipelineState 中 shared_context 的定义

**数据结构**（state.py 第 77, 109 行）：
```python
class PipelineState(TypedDict):
    # ... 其他字段 ...
    shared_context: dict[str, Any]  # P1-1: Cross-node shared context
```

**初始化**：
```python
def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> PipelineState:
    return PipelineState(
        # ...
        shared_context={},  # P1-1: Initialize shared_context
    )
```

**特点**：
- 自由形式字典，无 schema 约束
- 完全 JSON 可序列化
- 支持任意深度嵌套
- 位置：PipelineState 顶级字段

### 2.2 shared_context 在节点间的传递路径

**传递流程**：
```
orchestrator.start_pipeline()
  ↓
5 个节点顺序执行（analyzer → pm → ux → architect → po）
  ↓
每个节点执行时：
  state["shared_context"] 
    → executor 中提取 
    → NodeExecutionContext 中传递
    → ContextManager.build_independent_input() 注入
    → IndependentAgentInput 包含 shared_context
    → Agent 可读取和修改（通过 update_context 工具）
  ↓
下一个节点继承已更新的 shared_context
```

**代码实现**（executor.py 第 129 行）：
```python
execution_context = context_builder.build(
    shared_context=state.get("shared_context", {}),  # 从 state 提取
    # ...
)
```

### 2.3 shared_context 的持久化方式

**SQLite WAL 模式**：
- 并发读取安全
- 写入原子性保证
- 支持服务器崩溃恢复

**LangGraph Checkpoint**：
- 节点完成后，整个 PipelineState（包括 shared_context）被序列化
- 存储在 SQLite 的 checkpoint 表
- Pipeline 恢复时从最后成功的 checkpoint 恢复

**StateManager.update_shared_context()**（state_manager.py 第 556-719 行）：
- 支持 set/append/remove 三种操作
- 支持嵌套路径（"facts.market_scope"）
- 深度合并字典值
- 原子事务写入

### 2.4 shared_context 的当前写入方式

**唯一写入入口**：`update_context` 工具

**工具特点**：
1. **白名单保护**：仅允许修改特定前缀
   - facts.*
   - decisions.*
   - open_questions
   - doc_summaries.*
   - notes

2. **三种操作**：
   - set：替换或深度合并
   - append：添加到列表
   - remove：删除键

3. **类型检查**：append/remove 对列表类型进行验证

---

## 3. update_shared_context 工具设计

### 3.1 现有工具的功能分析

**UpdateContextTool 类**（update_context.py）：
- 继承 ToolResultCallableTool
- 参数验证通过 Pydantic
- 返回 ToolResult
- StateManager 持久化

**操作实现**（state_manager.py）：
- Set：支持嵌套路径和深度合并
- Append：创建列表或添加元素
- Remove：删除键或从列表移除

### 3.2 工具功能评估

**优点**：
- 操作完整（set/append/remove）
- 嵌套路径支持
- 深度合并
- 白名单保护
- 类型检查
- 完整错误处理

**改进空间**：
- 无条件/乐观锁更新
- 无变更历史
- 白名单硬编码
- 并发冲突处理简单

### 3.3 推荐方案

**方案 A（推荐）：保留并增强现有工具**

改进方向：
1. 添加版本控制（时间戳或版本号）
2. 支持条件更新（乐观锁）
3. 可配置白名单
4. 变更历史记录

**实现难度**：中等
**优点**：向后兼容，平滑迁移

### 3.4 工具 Schema 设计

```json
{
  "name": "update_shared_context",
  "properties": {
    "key": {
      "type": "string",
      "description": "Context key (e.g., 'facts.market_scope')",
      "examples": ["facts.market_scope", "open_questions", "decisions.architecture"]
    },
    "value": {
      "type": ["string", "number", "boolean", "object", "array", "null"],
      "description": "JSON-serializable value"
    },
    "operation": {
      "type": "string",
      "enum": ["set", "append", "remove"],
      "default": "set"
    }
  },
  "required": ["key", "value"]
}
```

**返回值设计**：
```python
{
  "success": True,
  "operation": "set",
  "key": "facts.market_scope",
  "previous_value": {...},
  "new_value": {...},
  "message": "Context updated",
  "timestamp": "2026-04-06T10:30:45Z",
  "version": "v1_1712404245123"
}
```

---

## 4. 并发安全分析

### 4.1 当前执行模型

**特点**：
1. 五个节点严格顺序执行（无并行）
2. 同一时刻仅一个节点运行
3. 不同 pipeline 隔离（不同数据库行）
4. 重试循环在同一事务上下文

**并发场景分析**：

| 场景 | 并发性 | 风险 | 说明 |
|------|--------|------|------|
| 单 pipeline 重试 | 否 | 低 | 同线程顺序执行 |
| 多 pipeline | 是 | 低 | 不同行，无冲突 |
| Pipeline 暂停/恢复 | 否 | 中 | 需考虑 checkpoint 一致性 |

### 4.2 SQLite WAL 模式的并发特性

**读-读**：✅ 可并行
**读-写**：✅ 互不阻塞
**写-写**：❌ 串行（行锁）

**关键保证**：
- 原子性：每个 UPDATE 是原子的
- 一致性：每个读取看到一致状态
- 持久性：已提交数据不会丢失

**风险**：Lost Update - 并发写入时最后一个覆盖前面的

### 4.3 乐观锁方案评估

**方案 1：基于时间戳的版本控制**
```python
{
  "shared_context": {
    "_metadata": {
      "version": 1,
      "updated_at": "2026-04-06T10:30:45Z"
    },
    "facts": {...}
  }
}
```

**方案 2：状态快照比较**
- 工具调用时传递 checksum
- 更新时验证 checksum

**推荐**：短期保持现状，中期实施版本控制

---

## 5. LangGraph 状态集成方案

### 5.1 工具执行结果的回写流程

```
IndependentAgent._call_llm()
  ├→ SDK 自动工具分发（yolo=True）
  ├→ update_context 工具调用
  │   └→ StateManager.update_shared_context()
  │       └→ SQLite UPDATE state_json
  ├→ 工具调用继续
  └→ 返回最终 JSON 输出
```

**关键点**：
- 工具直接修改 SQLite（非内存）
- 返回的 state 可能不含工具修改
- 下一个节点需从 DB 刷新

### 5.2 DualAgentNode 中的状态更新

在 `execute_with_context()` 中（dual_agent.py 第 251-300 行）：
1. Independent Agent 执行（工具调用已完成）
2. 私有字段过滤
3. Evaluator Agent 执行
4. 返回 NodeResult

### 5.3 graph.py 中的状态合并策略

```python
def executor(state: dict[str, Any]) -> dict[str, Any]:
    new_state = copy.deepcopy(state)  # 深拷贝避免污染
    new_state["current_node"] = node_id
    
    # 执行节点
    executed_node_state = await async_node_executor(node_run_state)
    converted_state = PipelineAdapter.convert_node_to_pipeline_state(...)
    
    return dict(converted_state)
```

**需要改进**：从 DB 刷新 shared_context

---

## 6. 评估 Agent 权限设计

### 6.1 独立 Agent 的访问权限

**读取权限**：✅ 完全开放
- 在 IndependentAgentInput 中接收 shared_context
- 可自由引用历史决策

**写入权限**：✅ 白名单控制
- 仅允许特定前缀
- 白名单：facts.*, decisions.*, open_questions, doc_summaries.*, notes

### 6.2 权限设计的利弊

**优点**：
- 完整隔离（Evaluator 无访问权）
- 明确规范
- 易于审计

**劣势**：
- 灵活性受限
- 无读取控制
- 无版本控制

### 6.3 推荐策略

**短期**：保持现状
**中期**：可配置白名单
**长期**：细粒度权限（工具级、数据级、操作级）

---

## 7. 代码改动清单

### 7.1 必需改动

| 文件 | 改动 | 优先级 |
|------|------|--------|
| executor.py | 从 DB 刷新 shared_context | P0 |
| update_context.py | 添加版本控制支持 | P1 |
| state_manager.py | 添加变更历史表 | P2 |
| node.yaml（所有节点） | 添加 shared_context 配置 | P1 |

### 7.2 关键代码片段

**改动 1：executor.py 中的刷新**
```python
# 从 DB 读取最新的 shared_context
try:
    latest_state = state_manager.get_pipeline(pipeline_id)
    if latest_state and "state_json" in latest_state:
        persisted = json.loads(latest_state["state_json"])
        new_state["shared_context"] = persisted.get("shared_context", {})
except Exception:
    pass  # 使用内存版本
```

**改动 2：UpdateContextTool 中的版本支持**
```python
# 在 shared_context 中添加元数据
if "_metadata" not in shared_context:
    shared_context["_metadata"] = {
        "version": 0,
        "updated_at": datetime.now(UTC).isoformat(),
    }

metadata = shared_context["_metadata"]
# 更新后递增版本
metadata["version"] += 1
```

**改动 3：node.yaml 配置**
```yaml
tools:
  shared_context:
    enabled: true
    operations: ["set", "append", "remove"]
```

---

## 8. 风险评估

### 8.1 实施风险

**低风险**：
- 配置变更（不涉及逻辑）
- 现有功能增强（向后兼容）
- 回滚简单

**中风险**：
- DB 刷新增加延迟
- 版本控制引入新逻辑

### 8.2 安全风险

**已识别**：
1. Lost Update 问题（并发写入）
   - 缓解：版本控制
   - 影响：低（顺序执行）

2. 隐私泄露（所有 Agent 可读）
   - 缓解：白名单
   - 影响：中等

### 8.3 性能风险

**延迟增加**：
- 每个节点执行时多一次 DB 查询
- 预计 <10ms

**改进**：缓存最新状态

---

## 9. 实施路线图

### Phase 1：准备（1-2 天）

- [ ] 审查报告
- [ ] 准备测试环境
- [ ] 编写单元测试

### Phase 2：核心改动（1-2 天）

- [ ] executor.py：添加 DB 刷新
- [ ] UpdateContextTool：添加版本控制
- [ ] node.yaml：添加配置

### Phase 3：增强功能（2-3 天）

- [ ] 实施变更历史表
- [ ] 可配置白名单
- [ ] 性能优化

### Phase 4：测试（2-3 天）

- [ ] 单元测试
- [ ] 集成测试
- [ ] 并发测试

### Phase 5：部署（1 天）

- [ ] 代码审查
- [ ] 部署到生产
- [ ] 监控

---

## 10. 总结与建议

### 核心发现

1. **shared_context 体系完整**：已有工具和持久化机制
2. **写入方案成熟**：update_context 工具功能完整
3. **并发风险低**：顺序执行模型
4. **隔离设计稳健**：Evaluator 无访问权

### 建议

**立即实施**（P0）：
- executor.py 中添加 DB 刷新
- 所有节点 yaml 添加 shared_context 配置
- 编写集成测试

**短期实施**（P1，1 周内）：
- UpdateContextTool 版本控制
- 可配置白名单
- 变更历史记录

**中期规划**（P2，1 月内）：
- 细粒度权限控制
- 性能优化（缓存）
- 完整的权限审计

### 后续研究方向

1. **条件更新**：支持 "only if" 表达式
2. **事务性操作**：支持原子的多 key 更新
3. **变更通知**：支持 Agent 订阅 shared_context 变化
4. **版本历史**：完整的版本回滚机制

---

**报告完成**：2026-04-06
**研究员**：研究分析 Agent
**版本**：1.0

