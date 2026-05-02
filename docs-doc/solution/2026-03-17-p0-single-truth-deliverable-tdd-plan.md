# P0 方案B 测试驱动方案: 文件层为唯一真相

## 1. 背景

根据 `docs/research/2026-03-13-p0-single-truth-deliverable-plan.md` 中的 **方案B: 文件层为唯一真相，状态层只存 metadata**，本测试驱动方案旨在验证和驱动实现以下目标：

### 设计原则
- **工具写盘是唯一真相**: 正式文档通过 `create_deliverable` 工具写入磁盘
- **状态层只存 metadata**: Pipeline state 中不再保存完整 markdown 正文
- **评审必须基于正式文档正文**: Evaluator 必须从磁盘读取正文进行评估
- **链式上下文传播摘要**: 下游节点通过 metadata + file path 获取上游交付物

### 目标数据结构
```python
class DeliverableArtifact(TypedDict):
    title: str
    summary: str           # 不再是完整内容
    file_path: str         # 指向磁盘文件
    sha256: str            # 文件哈希校验
    word_count: int
    section_index: list[str]
    content_type: str      # markdown
```

---

## 2. 测试范围

### 2.1 单元测试 (Unit Tests)

#### 2.1.1 `create_deliverable` 工具测试
**文件**: `tests/unit/tools/test_create_deliverable_metadata.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_returns_metadata_with_hash` | 验证工具返回包含 SHA256 的 metadata | 返回值包含 `file_path`, `sha256`, `word_count`, `section_index` |
| `test_sha256_matches_file_content` | 验证 SHA256 与文件内容一致 | 计算文件 SHA256 与返回值匹配 |
| `test_word_count_accurate` | 验证字数统计准确 | 返回的字数与实际 markdown 字数一致 |
| `test_section_index_extraction` | 验证章节索引提取 | 正确提取所有 `##` 章节标题 |
| `test_content_not_in_return_value` | 验证返回值不包含完整正文 | `content` 字段不在返回的 metadata 中 |

#### 2.1.2 `graph.py` 状态管理测试
**文件**: `tests/unit/pipeline/test_graph_no_content_duplication.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_state_has_no_full_content` | 验证 pipeline state 不包含完整正文 | `deliverables[node_id]` 只包含 metadata |
| `test_no_redundant_file_write` | 验证不重复写入文件 | `create_deliverable` 后 graph 不再二次保存 |
| `test_deliverable_artifact_structure` | 验证交付物数据结构 | 符合 `DeliverableArtifact` 定义 |

#### 2.1.3 `evaluator.py` 正文读取测试
**文件**: `tests/unit/agents/test_evaluator_reads_file.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_reads_deliverable_body_from_file` | 验证从文件读取正文 | Evaluator 使用 `file_path` 读取正文 |
| `test_body_matches_disk_content` | 验证正文与磁盘一致 | 读取的正文与磁盘文件完全匹配 |
| `test_uses_artifact_metadata` | 验证使用 artifact metadata | Evaluator 输入包含 `deliverable_artifact` 和 `deliverable_body` |

#### 2.1.4 `independent.py` 输出结构测试
**文件**: `tests/unit/agents/test_independent_output_structure.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_output_has_metadata_only` | 验证输出只有 metadata | `deliverable.content` 是摘要而非全文 |
| `test_output_includes_file_path` | 验证输出包含文件路径 | `deliverable.file_path` 指向工具创建的文件 |
| `test_output_includes_sha256` | 验证输出包含哈希 | `deliverable.sha256` 存在且有效 |

#### 2.1.5 `dual_agent.py` 集成测试
**文件**: `tests/unit/nodes/test_dual_agent_single_truth.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_evaluator_receives_body_from_file` | 验证 Evaluator 接收文件正文 | `execute_with_input` 传递 `deliverable_body` |
| `test_result_has_metadata_only` | 验证结果只含 metadata | `NodeResult.deliverable` 符合 `DeliverableArtifact` |
| `test_no_content_in_state_after_execution` | 验证执行后状态无正文 | Pipeline state 通过验证检查 |

### 2.2 集成测试 (Integration Tests)

#### 2.2.1 完整流程测试
**文件**: `tests/integration/test_single_truth_workflow.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_full_pipeline_single_truth` | 验证完整 pipeline 符合单真相原则 | 所有节点交付物仅存 metadata |
| `test_evaluator_sees_actual_content` | 验证 Evaluator 评审实际内容 | 评分基于磁盘文件而非摘要 |
| `test_chain_context_metadata_only` | 验证链式上下文只传 metadata | 下游节点收到 `DeliverableArtifact` 列表 |

#### 2.2.2 文件读取器测试
**文件**: `tests/integration/test_deliverable_body_reader.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_body_reader_returns_file_content` | 验证正文读取器功能 | 根据 `file_path` 读取并返回正文 |
| `test_body_reader_handles_missing_file` | 验证缺失文件处理 | 文件不存在时抛出明确异常 |
| `test_body_reader_verifies_hash` | 验证哈希校验 | 可选: 验证文件哈希与 `sha256` 匹配 |

### 2.3 回归测试 (Regression Tests)

#### 2.3.1 下游节点兼容性测试
**文件**: `tests/regression/test_downstream_compatibility.py`

| 测试用例 | 描述 | 验收标准 |
|---------|------|---------|
| `test_downstream_can_read_summary` | 验证下游节点可读取摘要 | 通过 `deliverable.summary` 获取 |
| `test_downstream_can_read_full_body` | 验证下游节点可读取正文 | 通过 `file_path` 按需读取全文 |
| `test_legacy_context_format_still_works` | 验证旧格式兼容 | 支持未更新的节点配置 |

---

## 3. 代码改动边界验证

### 3.1 文件清单

```
autoBMAD/docuswarm/tools/create_deliverable.py    # Step 1: 扩展返回值
autoBMAD/docuswarm/agents/independent.py          # Step 2: 修改输出结构
autoBMAD/docuswarm/agents/evaluator.py            # Step 4: 接收 deliverable_body
autoBMAD/docuswarm/nodes/dual_agent.py            # Step 4: 在 Evaluator 前读取正文
autoBMAD/docuswarm/pipeline/graph.py              # Step 3: 删除二次保存逻辑
autoBMAD/docuswarm/storage/files.py               # 新增: 轻量正文读取器
```

### 3.2 每个文件的测试验证点

#### `create_deliverable.py`
- [x] 返回值包含 `file_path`, `sha256`, `word_count`, `section_index`
- [x] 文件确实写入磁盘
- [x] 返回值不包含完整 `content`

#### `independent.py`
- [x] `deliverable.content` 是摘要 (1-2 句)
- [x] 输出 JSON 包含 `file_path` 和 `sha256`
- [x] Prompt 明确说明 "deliverable.content 只是摘要"

#### `evaluator.py`
- [x] `execute_with_input` 接收 `deliverable_body` 参数
- [x] 评估基于 `deliverable_body` 而非摘要
- [x] `execute` 方法通过 `file_path` 读取正文 (向后兼容)

#### `dual_agent.py`
- [x] `execute_with_context` 在调用 Evaluator 前读取文件正文
- [x] 构建 `EvaluatorAgentInput` 包含 `deliverable_body`
- [x] `NodeResult.deliverable` 符合 `DeliverableArtifact`

#### `graph.py`
- [x] 不再调用 `_save_deliverable_async` 二次保存
- [x] `deliverables[node_id]` 存储 metadata 而非正文
- [x] Pipeline state 可序列化且大小合理

---

## 4. 测试执行计划

### 4.1 执行顺序

```bash
# Phase 1: 单元测试 - 工具层
pytest tests/unit/tools/test_create_deliverable_metadata.py -v

# Phase 2: 单元测试 - Agent 层
pytest tests/unit/agents/test_independent_output_structure.py -v
pytest tests/unit/agents/test_evaluator_reads_file.py -v

# Phase 3: 单元测试 - Node 层
pytest tests/unit/nodes/test_dual_agent_single_truth.py -v

# Phase 4: 单元测试 - Pipeline 层
pytest tests/unit/pipeline/test_graph_no_content_duplication.py -v

# Phase 5: 集成测试
pytest tests/integration/test_single_truth_workflow.py -v
pytest tests/integration/test_deliverable_body_reader.py -v

# Phase 6: 回归测试
pytest tests/regression/test_downstream_compatibility.py -v

# Phase 7: 全量测试
pytest tests/ -v --tb=short
```

### 4.2 验收标准检查清单

- [ ] **AC1**: Pipeline state 中不再存在完整正文副本
- [ ] **AC2**: Evaluator 评分对象始终为工具写盘后的正式正文
- [ ] **AC3**: 链式上下文默认传 metadata + summary，不传全文
- [ ] **AC4**: 所有新测试通过
- [ ] **AC5**: 现有测试不破坏 (向后兼容)

---

## 5. 测试数据与 Fixtures

### 5.1 示例 DeliverableArtifact

```python
SAMPLE_DELIVERABLE_ARTIFACT = {
    "title": "Requirements Analysis Report",
    "summary": "Created comprehensive analysis covering architecture and requirements.",
    "file_path": "output/pipeline-123/requirements-analysis-report.md",
    "sha256": "a3f5c8e9d2b1...",
    "word_count": 1250,
    "section_index": ["Introduction", "Requirements", "Analysis", "Conclusion"],
    "content_type": "markdown"
}
```

### 5.2 Mock 文件内容

```python
SAMPLE_MARKDOWN_CONTENT = """# Requirements Analysis Report

## Introduction
This is the introduction section.

## Requirements
- Requirement 1: User authentication
- Requirement 2: Data persistence

## Analysis
Detailed analysis content here.

## Conclusion
Summary and next steps.
"""
```

---

## 6. 失败场景测试

### 6.1 异常情况

| 场景 | 预期行为 | 测试用例 |
|------|---------|---------|
| 文件被删除后 Evaluator 读取 | 抛出 `FileNotFoundError` | `test_evaluator_handles_missing_file` |
| SHA256 不匹配 | 记录警告但继续 (或可选抛错) | `test_hash_mismatch_warning` |
| 文件路径为空 | 抛出 `ValueError` | `test_empty_file_path_rejected` |
| 状态层意外包含正文 | 校验失败，记录错误 | `test_state_validation_rejects_full_content` |

---

## 7. 性能测试 (可选)

### 7.1 状态大小测试

```python
def test_state_size_with_metadata_only():
    """验证 metadata-only 状态大小合理。"""
    state = create_sample_pipeline_state()
    serialized = json.dumps(state)
    # 5个节点的 metadata 不应超过 10KB
    assert len(serialized) < 10 * 1024
```

---

## 8. 文档与交付物

### 8.1 生成的文档

1. 本测试驱动方案: `docs/solution/2026-03-17-p0-single-truth-deliverable-tdd-plan.md`
2. 测试报告: `docs/solution/2026-03-17-p0-single-truth-test-report.md`
3. 代码覆盖报告: `htmlcov/index.html`

### 8.2 完成标准

- [ ] 所有新测试用例实现并提交到 `tests/` 目录
- [ ] 测试报告生成，显示通过率 > 95%
- [ ] 代码覆盖率 > 80%
- [ ] 方案 B 所有代码改动完成并通过测试

---

*文档版本: 1.0*
*创建日期: 2026-03-17*
*对应研究文档: docs/research/2026-03-13-p0-single-truth-deliverable-plan.md*
