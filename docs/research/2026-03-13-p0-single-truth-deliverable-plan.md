---
**文档状态**: 🗄️ 已归档 (Archived)  
**归档日期**: 2026-03-17  
**替代文档**: F3 深度研究报告 (2026-03-17-F3-evaluator-input-contract-research-report.md)  
**说明**: 本文档是 2026-03-13 的历史研究文档，相关决策已整合到 F1-F8 体系中。当前决策以 `docs/DECISIONS.md` 为准。
---

# P0 Refactor Plan: Single Truth for Deliverables

## 1. Problem Statement

当前交付物流存在双轨:

1. `create_deliverable` 工具把完整 markdown 写入磁盘
2. `pipeline/graph.py` 又把 `deliverable.content` 重新写入存储

而 `IndependentAgent` 的 prompt 又明确说:

- `deliverable.content` 只是摘要
- 正式文档已经通过工具写盘

这意味着:

- Evaluator 可能评审摘要而不是正式文档
- 后续节点也可能拿到摘要而不是正式交付物
- 状态层和文件层可能彼此不一致

## 2. 设计原则

- 工具写盘是唯一真相
- 状态层只存 metadata
- 评审必须基于正式文档正文
- 链式上下文默认传播摘要和 metadata，需要正文时按文件路径读取

## 3. 备选方案

### 方案 A: 状态层保存完整正文，工具只是副本

缺点:
- 状态膨胀
- 更难避免双写不一致

### 方案 B: 文件层为唯一真相，状态层只存 metadata

优点:
- 最符合当前工具语义
- 改动最小
- 最容易做校验

### 方案 C: 引入对象存储和 artifact registry

缺点:
- 明显超出当前系统复杂度

推荐: 方案 B

## 4. 目标数据结构

```python
class DeliverableArtifact(TypedDict):
    title: str
    summary: str
    file_path: str
    sha256: str
    word_count: int
    section_index: list[str]
    content_type: str  # markdown
```

### 状态层持久化内容

- `title`
- `summary`
- `file_path`
- `sha256`
- `word_count`
- `section_index`
- `created_at`

### 状态层不再持久化

- 完整 markdown 正文
- 为了省事而塞进 `deliverable.content` 的长文

## 5. Evaluator 输入重构

Evaluator 在同一节点执行期间，需要看到正式文档正文，但不要求 pipeline state 持久化正文。

推荐做法:

1. `create_deliverable` 返回文件 metadata
2. `DualAgentNode` 在进入 Evaluator 前，根据 `file_path` 读取正文
3. Evaluator 使用:
   - `deliverable_artifact` metadata
   - `deliverable_body` 正式正文

这样可以实现:

- 执行期可评审正式内容
- 持久化期只保存 metadata

## 6. 代码改动边界

- `autoBMAD/docuswarm/tools/create_deliverable.py`
- `autoBMAD/docuswarm/agents/independent.py`
- `autoBMAD/docuswarm/nodes/dual_agent.py`
- `autoBMAD/docuswarm/agents/evaluator.py`
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/storage/files.py`

## 7. 迁移步骤

### Step 1

扩展 `create_deliverable` 的返回值，增加:

- `file_path`
- `sha256`
- `word_count`
- `section_index`

### Step 2

将 `IndependentAgent` 的输出结构改为:

```json
{
  "deliverable": {
    "title": "...",
    "summary": "...",
    "file_path": "...",
    "sha256": "..."
  }
}
```

### Step 3

删除 `graph.py` 中对 `deliverable.content` 的再次保存逻辑。

### Step 4

新增一个轻量读取器，在 Evaluator 前读取正式正文。

## 8. 验收标准

- pipeline state 中不再存在完整正文副本
- Evaluator 评分对象始终为工具写盘后的正式正文
- 链式上下文默认传 metadata + summary，不传全文

## 9. 相关文档

- [NodeExecutionContext 深度研究报告](2026-03-13-p0-single-context-protocol-deep-research-report.md) - 上下文流转分析
- [方案B实施设计](2026-03-13-p0-single-context-protocol-implementation-design.md) - `EvaluatorAgentInput` 中包含 `deliverable_body` 的设计
- [Architecture Document](../architecture.md) - 状态持久化层设计
- [Design Document](../design.md) - `DeliverableArtifact` 数据结构设计

## 10. 测试建议

- 单元测试: `create_deliverable` 返回 metadata 且 hash 正确
- 单元测试: `graph.py` 不再二次写正文
- 集成测试: Evaluator 看到的正文与磁盘文件一致
- 回归测试: 下游节点能通过 metadata + file path 读取上游交付物摘要或正文
