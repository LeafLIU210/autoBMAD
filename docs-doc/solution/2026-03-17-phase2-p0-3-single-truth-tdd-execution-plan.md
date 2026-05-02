# Phase 2: P0-3 - 单一交付物真相收口 - TDD 执行计划

> 基于: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`  
> 优先级: 🔴 最高  
> 目标: 消除摘要/正文双轨，确保 Evaluator 始终评审正式文档

## 研究问题回顾

来自研究报告:
- **P0-3-002**: file_path 和 sha256 不是强制验证字段
- **P0-3-003**: DeliverableArtifact 目标结构与运行时验证不一致 (summary vs content)
- **P0-3-004**: Evaluator 在 file_path 缺失时会退回到 deliverable.content
- **P0-3-001**: create_deliverable 已实现 metadata-first 返回 (✅ 已完成)

## 实施步骤

### Step 1: 强制验证 file_path 和 sha256

#### TDD Cycle 1.1

**Red - 编写失败测试:**
```python
# tests/unit/llm/test_response_validation.py

import pytest
from autoBMAD.docuswarm.llm.response import (
    validate_independent_output,
    ValidationError
)


class TestDeliverableValidationSingleTruth:
    """Test deliverable validation enforces single truth"""
    
    def test_file_path_is_required(self):
        """deliverable.file_path should be required"""
        data = {
            "deliverable": {
                "title": "Test",
                "summary": "Brief summary",
                # file_path missing!
                "sha256": "abc123..."
            },
            "questions": []
        }
        
        with pytest.raises(ValidationError, match="file_path is required"):
            validate_independent_output(data)
    
    def test_sha256_is_required(self):
        """deliverable.sha256 should be required"""
        data = {
            "deliverable": {
                "title": "Test",
                "summary": "Brief summary",
                "file_path": "/path/to/file.md",
                # sha256 missing!
            },
            "questions": []
        }
        
        with pytest.raises(ValidationError, match="sha256 is required"):
            validate_independent_output(data)
```

运行测试:
```bash
pytest tests/unit/llm/test_response_validation.py -v
# Expected: FAIL (currently allows optional fields)
```

**Green - 最小实现:**
```python
# autoBMAD/docuswarm/llm/response.py

def validate_independent_output(data: dict[str, Any]) -> None:
    """Validate Independent Agent output against schema."""
    
    # Validate deliverable (required)
    if "deliverable" not in data:
        raise ValidationError("deliverable: required field missing")
    
    deliverable: dict[str, Any] = data["deliverable"]
    
    # Validate deliverable.title (required)
    if "title" not in deliverable:
        raise ValidationError("deliverable.title: required field missing")
    if not isinstance(deliverable["title"], str):
        raise ValidationError("deliverable.title: must be a string")
    
    # P0-3: file_path is now REQUIRED (not optional)
    if "file_path" not in deliverable:
        raise ValidationError("deliverable.file_path: required field missing")
    if not isinstance(deliverable["file_path"], str):
        raise ValidationError("deliverable.file_path: must be a string")
    
    # P0-3: sha256 is now REQUIRED (not optional)
    if "sha256" not in deliverable:
        raise ValidationError("deliverable.sha256: required field missing")
    if not isinstance(deliverable["sha256"], str):
        raise ValidationError("deliverable.sha256: must be a string")
    
    # P0-3: Prefer summary over content
    if "summary" not in deliverable and "content" not in deliverable:
        raise ValidationError("deliverable.summary: required field missing")
    if "summary" in deliverable and not isinstance(deliverable["summary"], str):
        raise ValidationError("deliverable.summary: must be a string")
```

运行测试:
```bash
pytest tests/unit/llm/test_response_validation.py -v
# Expected: PASS
```

---

#### TDD Cycle 1.2

**Red - 编写失败测试:**
```python
# Test: accepts_valid_metadata_only_deliverable

def test_accepts_valid_metadata_only_deliverable(self):
    """Should accept deliverable with metadata only (no full content)"""
    data = {
        "deliverable": {
            "title": "Test Deliverable",
            "summary": "Brief summary of the document",
            "file_path": "output/pipeline-001/test.md",
            "sha256": "a3f5c8e9d2b1...",
            "word_count": 1500,
            "section_index": ["Overview", "Details"]
        },
        "questions": []
    }
    
    # Should not raise
    validate_independent_output(data)
```

运行测试:
```bash
pytest tests/unit/llm/test_response_validation.py::TestDeliverableValidationSingleTruth::test_accepts_valid_metadata_only_deliverable -v
# Expected: PASS
```

---

### Step 2: 统一 DeliverableArtifact 字段

#### TDD Cycle 2.1

**Red - 编写失败测试:**
```python
# tests/unit/node_execution/test_contracts.py

from autoBMAD.docuswarm.node_execution.contracts import DeliverableArtifact


class TestDeliverableArtifactSchema:
    """Test DeliverableArtifact uses summary not content"""
    
    def test_uses_summary_field(self):
        """DeliverableArtifact should use 'summary' field, not 'content'"""
        # This test verifies type definition at runtime
        artifact: DeliverableArtifact = {
            "title": "Test",
            "summary": "Brief summary",  # Not 'content'
            "file_path": "/path/to/file.md",
            "sha256": "abc123",
            "word_count": 100,
            "section_index": ["Section 1"],
            "content_type": "markdown"
        }
        
        assert "summary" in artifact
        assert artifact["summary"] == "Brief summary"
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/node_execution/contracts.py

class DeliverableArtifact(TypedDict):
    """
    交付物元数据 - 文件层为唯一真相。
    
    状态层只保存 metadata，完整内容通过 file_path 从磁盘读取。
    """
    
    title: str
    summary: str  # P0-3: Use 'summary', not 'content'
    file_path: str
    sha256: str
    word_count: int
    section_index: list[str]
    content_type: str
```

---

#### TDD Cycle 2.2: 迁移现有代码

**Red - 编写失败测试 (发现代码中使用 content 的地方):**
```python
# tests/regression/test_no_content_field.py

class TestNoContentField:
    """Regression: Ensure no code uses 'content' instead of 'summary'"""
    
    def test_context_isolation_uses_summary(self):
        """ContextManager should use 'summary' not 'content' for deliverables"""
        manager = ContextManager()
        
        # Mock execution context with summary
        execution_context = create_execution_context(
            chained_deliverables=[{
                "node_id": "analyst",
                "deliverable": {
                    "title": "Analysis",
                    "summary": "Brief analysis"  # Using summary
                }
            }]
        )
        
        result = manager.build_independent_input(execution_context)
        
        # Should use summary
        assert result["chained_deliverables_summary"][0]["summary"] == "Brief analysis"
```

**Green - 修复代码:**
```python
# autoBMAD/docuswarm/context/isolation.py

def build_independent_input(...):
    # ... existing code ...
    
    chained_summary = []
    for item in execution_context["chained_deliverables"]:
        deliverable = item.get("deliverable", {})
        chained_summary.append({
            "node_id": item.get("node_id"),
            "title": deliverable.get("title", "Untitled"),
            # P0-3: Use 'summary' instead of 'content'
            "summary": deliverable.get("summary", "")[:200],
        })
    
    # ...
```

---

### Step 3: 禁止 Evaluator fallback 到摘要

#### TDD Cycle 3.1

**Red - 编写失败测试:**
```python
# tests/unit/context/test_isolation.py

class TestEvaluatorInputSingleTruth:
    """Test Evaluator input enforces single truth"""
    
    def test_build_evaluator_input_reads_file_content(self, tmp_path):
        """build_evaluator_input should read full content from file"""
        manager = ContextManager()
        
        # Create actual file with full content
        file_path = tmp_path / "deliverable.md"
        full_content = "# Full Document\n\nThis is the complete content with details."
        file_path.write_text(full_content)
        
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "summary": "Short summary only",  # Should NOT use this
            "file_path": str(file_path),
            "sha256": "abc123"
        }
        
        result = manager.build_evaluator_input(execution_context, deliverable)
        
        # Must read full content from file
        assert result["deliverable_body"] == full_content
        assert result["deliverable_body"] != "Short summary only"
    
    def test_raises_if_file_missing(self):
        """build_evaluator_input should raise if file_path doesn't exist"""
        manager = ContextManager()
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "file_path": "/nonexistent/file.md",
            "sha256": "abc123"
        }
        
        with pytest.raises(FileNotFoundError, match="Deliverable file not found"):
            manager.build_evaluator_input(execution_context, deliverable)
    
    def test_raises_if_file_path_missing(self):
        """build_evaluator_input should raise if file_path is None"""
        manager = ContextManager()
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "summary": "Only summary, no file",
            # file_path missing!
        }
        
        with pytest.raises(ValueError, match="file_path is required"):
            manager.build_evaluator_input(execution_context, deliverable)
```

运行测试:
```bash
pytest tests/unit/context/test_isolation.py::TestEvaluatorInputSingleTruth -v
# Expected: FAIL (currently has fallback logic)
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/context/isolation.py

def build_evaluator_input(
    self,
    execution_context: NodeExecutionContext,
    deliverable: dict[str, Any] | None,
) -> EvaluatorAgentInput:
    """构建 EvaluatorAgent 的输入。
    
    P0-3: Evaluator 必须评审工具写盘后的正式文档正文，
    不允许退回到 deliverable.summary。
    """
    if not deliverable:
        raise ValueError("deliverable is required for evaluation")
    
    # P0-3: file_path is REQUIRED, no fallback
    file_path = deliverable.get("file_path")
    if not file_path:
        raise ValueError("file_path is required for evaluation")
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Deliverable file not found: {file_path}")
    
    # P0-3: Always read full content from file
    deliverable_body = path.read_text(encoding="utf-8")
    
    return EvaluatorAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        deliverable_artifact=deliverable,
        deliverable_body=deliverable_body,  # Full content from file
        criteria=execution_context.get("evaluator_criteria", []),
    )
```

运行测试:
```bash
pytest tests/unit/context/test_isolation.py::TestEvaluatorInputSingleTruth -v
# Expected: PASS
```

---

### Step 4: 限制下游传播为 metadata + summary

#### TDD Cycle 4.1

**Red - 编写失败测试:**
```python
# tests/unit/pipeline/test_state_accumulation.py

class TestChainedContextPropagation:
    """Test that chained context only propagates metadata + summary"""
    
    def test_accumulate_context_excludes_full_content(self):
        """accumulate_context should exclude full deliverable content"""
        subject_context = {"task": "Build app"}
        deliverables = {
            "analyst": {
                "title": "Analysis",
                "summary": "Brief analysis summary",
                "file_path": "output/analysis.md",
                "sha256": "abc123",
                # Note: full content is in the file, not here
            }
        }
        
        result = accumulate_context(subject_context, deliverables, "pm")
        
        assert "analyst_deliverable" in result
        analyst_output = result["analyst_deliverable"]
        
        # Should only have metadata + summary
        assert "summary" in analyst_output
        assert "file_path" in analyst_output
        assert "sha256" in analyst_output
        assert analyst_output["summary"] == "Brief analysis summary"
        
        # Should NOT have full content
        assert "content" not in analyst_output
```

**Green - 实现 (验证现有代码):**
```python
# Verify autoBMAD/docuswarm/pipeline/state.py

# The accumulate_context function should already work correctly
# if deliverables only contain metadata.
# 
# If there's code that copies full deliverable including content,
# fix it to only copy metadata fields.
```

---

### Step 5: 集成测试

#### TDD Cycle 5.1

**Red - 编写失败测试:**
```python
# tests/integration/test_single_truth_deliverable.py

class TestSingleTruthDeliverable:
    """Integration test: Single truth deliverable flow"""
    
    @pytest.mark.asyncio
    async def test_evaluator_reads_full_content_from_file(self, tmp_path):
        """End-to-end: Evaluator should read full content from file"""
        # Arrange
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create deliverable file
        deliverable_file = output_dir / "analysis.md"
        full_content = "# Analysis\n\nDetailed analysis content here."
        deliverable_file.write_text(full_content)
        
        # Create execution context
        execution_context = create_execution_context(
            pipeline_id="test-pipeline",
            node_id="pm"
        )
        
        # Create deliverable metadata (as would be returned by IndependentAgent)
        deliverable = {
            "title": "Analysis",
            "summary": "Brief summary",
            "file_path": str(deliverable_file),
            "sha256": hashlib.sha256(full_content.encode()).hexdigest(),
            "word_count": 10,
            "section_index": ["Analysis"]
        }
        
        # Act
        manager = ContextManager()
        evaluator_input = manager.build_evaluator_input(
            execution_context,
            deliverable
        )
        
        # Assert
        assert evaluator_input["deliverable_body"] == full_content
        assert evaluator_input["deliverable_body"] != deliverable["summary"]
```

---

## 验收清单

- [ ] `validate_independent_output()` 强制要求 `file_path`
- [ ] `validate_independent_output()` 强制要求 `sha256`
- [ ] `DeliverableArtifact` 使用 `summary` 字段
- [ ] 所有代码从 `content` 迁移到 `summary`
- [ ] `build_evaluator_input()` 总是从文件读取正文
- [ ] `build_evaluator_input()` 在 file_path 缺失时抛出异常
- [ ] `build_evaluator_input()` 在文件不存在时抛出异常
- [ ] `build_evaluator_input()` 不使用 `deliverable.get("content")` fallback
- [ ] 链式上下文只传播 metadata + summary
- [ ] 集成测试验证端到端单一真相
- [ ] 所有测试通过率 100%
- [ ] 代码覆盖率 > 80%

## 潜在风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 向后兼容性 | 高 | 同步更新所有 agent prompt 示例 |
| 文件读取失败 | 中 | 添加明确的错误信息和重试机制 |
| 性能影响 | 低 | 文件读取使用 async/await |
| 存储空间 | 低 | State 只存 metadata，文件存正文 |

## 与 Phase 1 (P1-1) 的依赖关系

Phase 2 依赖 Phase 1 完成:
- `shared_context` 持久化机制 (P1-1)
- StateManager 绑定模式 (P1-1)

建议: **先完成 Phase 1，再开始 Phase 2**

## 参考文档

- 研究报告: `docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`
- 主 TDD 方案: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
- Phase 1 计划: `docs/solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md`
