# TDD 重构方案: ContextValidator 提取

> **关联研究报告**: [DocuSwarm-重构详细研究报告.md](../research/DocuSwarm-重构详细研究报告.md) P0-1  
> **优先级**: P0 - 关键  
> **预估工期**: 1-2 天  
> **影响范围**: `pipeline/orchestrator.py`, `pipeline/context_validator.py` (新增)

---

## 1. 问题分析

### 1.1 当前代码问题

`HybridOrchestrator` 类承担了**6个不同职责**，其中 `_validate_context()` 方法混合了：
- Prompt 格式化（字符串模板操作）
- LLM 调用（外部依赖）
- JSON 解析（错误处理）
- 结果验证（业务逻辑）

**当前代码位置**: `orchestrator.py` 第 222-304 行

```python
async def _validate_context(self, subject_context: dict[str, Any]) -> dict[str, Any]:
    """Validate subject context using LLM."""
    # 1. Prompt 格式化（应该分离）
    context_str = json.dumps(subject_context, indent=2)
    prompt = CONTEXT_VALIDATION_PROMPT.format(subject_context=context_str)
    
    # 2. LLM 调用（应该分离）
    messages = await session_manager.single_prompt(prompt=prompt, mode="agent", yolo=True)
    
    # 3. 内容提取（应该复用现有工具）
    content = extract_text_from_messages(messages)
    
    # 4. JSON 解析（错误处理复杂）
    if content.startswith("```json"):
        content = content[7:]
    ...
    result = json.loads(content.strip())
    
    # 5. Fail-open 策略（风险点）
    except (json.JSONDecodeError, ValueError) as e:
        return {"valid": True, "reason": "...", "missing_info": []}  # Fail open!
```

### 1.2 关键风险点

**Fail-Open 策略风险**（P1-5）:
```python
# 当前行为：解析失败时默认允许继续
except (json.JSONDecodeError, ValueError) as e:
    return {"valid": True, "reason": "...", "missing_info": []}
```
- **风险**: 无效上下文可能导致后续所有节点产生低质量输出
- **建议**: 增加结构化重试，持续失败则返回带 warning 的结果

---

## 2. 目标设计

### 2.1 ContextValidator 职责

```
┌─────────────────────────────────────────────────────────────┐
│                    ContextValidator                          │
├─────────────────────────────────────────────────────────────┤
│  - Prompt 构建（从外部模板加载）                              │
│  - LLM 调用（使用注入的 session_manager）                    │
│  - 结构化重试（最多3次）                                     │
│  - JSON 解析与验证                                           │
│  - 错误处理（可配置的 fail-open/fail-close）                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 API 设计

```python
@dataclass
class ValidationResult:
    """Result of context validation."""
    valid: bool
    reason: str
    missing_info: list[str]
    raw_response: str | None = None  # For debugging
    attempts: int = 1  # Track retry count
    fallback_used: bool = False  # Track if fail-open was used


class ContextValidator:
    """Validate pipeline context using LLM.
    
    Extracted from HybridOrchestrator to follow Single Responsibility Principle.
    Implements structured retry logic and configurable error handling.
    """
    
    DEFAULT_MAX_RETRIES = 2  # Total 3 attempts
    DEFAULT_FAIL_OPEN = False  # Changed from True for safety
    
    def __init__(
        self,
        session_manager: SessionManager,
        prompt_template: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        fail_open: bool = DEFAULT_FAIL_OPEN,
    ) -> None:
        """Initialize context validator.
        
        Args:
            session_manager: Manager for LLM interactions
            prompt_template: Optional custom validation prompt
            max_retries: Maximum retry attempts for failed parsing
            fail_open: If True, allow pipeline on validation failure
                      If False, raise exception on failure
        """
    
    async def validate(
        self, 
        subject_context: dict[str, Any]
    ) -> ValidationResult:
        """Validate subject context.
        
        Implements structured retry:
        1. Call LLM with validation prompt
        2. Parse JSON response
        3. If parsing fails, retry up to max_retries
        4. If all retries fail, use fail_open policy
        
        Args:
            subject_context: The context to validate
            
        Returns:
            ValidationResult with validation status
            
        Raises:
            ContextValidationError: If validation fails and fail_open=False
        """
```

---

## 3. 测试驱动开发计划

### Phase 1: 编写测试（红阶段）

#### Test 1: 基础验证测试
```python
# tests/unit/test_context_validator.py

import pytest
from unittest.mock import AsyncMock, Mock
from autoBMAD.docuswarm.pipeline.context_validator import (
    ContextValidator, 
    ValidationResult,
    ContextValidationError,
)


class TestContextValidatorBasic:
    """Test basic validation functionality."""
    
    @pytest.mark.asyncio
    async def test_validate_returns_result_on_valid_response(self):
        """Test successful validation with valid LLM response."""
        # Arrange
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content='{"valid": true, "reason": "Context is complete", "missing_info": []}',
            is_success=lambda: True
        ))
        
        validator = ContextValidator(session_manager=mock_session)
        context = {"subject": "Test Project", "task": "Create PRD"}
        
        # Act
        result = await validator.validate(context)
        
        # Assert
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.reason == "Context is complete"
        assert result.missing_info == []
        assert result.attempts == 1
        assert result.fallback_used is False
    
    @pytest.mark.asyncio
    async def test_validate_detects_invalid_context(self):
        """Test detection of invalid context."""
        # Arrange
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content='{"valid": false, "reason": "Missing requirements", "missing_info": ["target_audience"]}',
            is_success=lambda: True
        ))
        
        validator = ContextValidator(session_manager=mock_session)
        
        # Act
        result = await validator.validate({"subject": "Test"})
        
        # Assert
        assert result.valid is False
        assert "Missing requirements" in result.reason
        assert "target_audience" in result.missing_info
```

#### Test 2: 重试逻辑测试（关键测试）
```python
class TestContextValidatorRetry:
    """Test structured retry logic."""
    
    @pytest.mark.asyncio
    async def test_retry_on_json_parse_error(self):
        """CRITICAL: Should retry when JSON parsing fails.
        
        This addresses P1-5: Replace fail-open with structured retry.
        """
        # Arrange - First call returns invalid JSON, second succeeds
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(side_effect=[
            Mock(success=True, content='Not valid JSON', is_success=lambda: True),
            Mock(success=True, content='{"valid": true, "reason": "OK", "missing_info": []}', is_success=lambda: True),
        ])
        
        validator = ContextValidator(
            session_manager=mock_session,
            max_retries=2,
        )
        
        # Act
        result = await validator.validate({"subject": "Test"})
        
        # Assert
        assert result.valid is True
        assert result.attempts == 2  # Retried once
        assert mock_session.single_prompt.call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_exhaustion_with_fail_open(self):
        """When all retries exhausted with fail_open=True, return valid=True with warning."""
        # Arrange - All calls return invalid JSON
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True, content='Invalid JSON', is_success=lambda: True
        ))
        
        validator = ContextValidator(
            session_manager=mock_session,
            max_retries=2,
            fail_open=True,  # Allow pipeline to continue
        )
        
        # Act
        result = await validator.validate({"subject": "Test"})
        
        # Assert
        assert result.valid is True  # Fail open
        assert result.fallback_used is True  # But mark as fallback
        assert "validation failed" in result.reason.lower()
        assert mock_session.single_prompt.call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_retry_exhaustion_with_fail_close(self):
        """When all retries exhausted with fail_open=False, raise exception."""
        # Arrange
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True, content='Invalid JSON', is_success=lambda: True
        ))
        
        validator = ContextValidator(
            session_manager=mock_session,
            max_retries=1,
            fail_open=False,  # Strict mode
        )
        
        # Act & Assert
        with pytest.raises(ContextValidationError) as exc_info:
            await validator.validate({"subject": "Test"})
        
        assert "validation failed after 2 attempts" in str(exc_info.value)
```

#### Test 3: Markdown 代码块处理测试
```python
class TestContextValidatorMarkdown:
    """Test handling of markdown code blocks in LLM response."""
    
    @pytest.mark.asyncio
    async def test_strip_markdown_json_block(self):
        """Test stripping ```json and ``` from response."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content='''```json
{
  "valid": true,
  "reason": "Context is complete",
  "missing_info": []
}
```''',
            is_success=lambda: True
        ))
        
        validator = ContextValidator(session_manager=mock_session)
        
        # Act
        result = await validator.validate({"subject": "Test"})
        
        # Assert
        assert result.valid is True
    
    @pytest.mark.asyncio
    async def test_strip_generic_code_block(self):
        """Test stripping generic ``` from response."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content='''```
{"valid": true, "reason": "OK", "missing_info": []}
```''',
            is_success=lambda: True
        ))
        
        validator = ContextValidator(session_manager=mock_session)
        result = await validator.validate({"subject": "Test"})
        
        assert result.valid is True
```

#### Test 4: Prompt 模板测试
```python
class TestContextValidatorPrompt:
    """Test prompt template handling."""
    
    @pytest.mark.asyncio
    async def test_custom_prompt_template(self):
        """Test using custom prompt template."""
        custom_template = """Validate this: {subject_context}
        Output JSON with valid, reason, missing_info."""
        
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content='{"valid": true, "reason": "OK", "missing_info": []}',
            is_success=lambda: True
        ))
        
        validator = ContextValidator(
            session_manager=mock_session,
            prompt_template=custom_template,
        )
        
        await validator.validate({"subject": "Test"})
        
        # Verify custom template was used
        call_args = mock_session.single_prompt.call_args
        prompt = call_args.kwargs.get('prompt') or call_args[1].get('prompt')
        assert "Validate this:" in prompt
    
    @pytest.mark.asyncio
    async def test_default_prompt_includes_context(self):
        """Test that default prompt includes formatted context."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(return_value=Mock(
            success=True,
            content='{"valid": true, "reason": "OK", "missing_info": []}',
            is_success=lambda: True
        ))
        
        validator = ContextValidator(session_manager=mock_session)
        context = {"subject": "Test Project", "complex": {"nested": "data"}}
        
        await validator.validate(context)
        
        # Verify context is JSON-formatted in prompt
        call_args = mock_session.single_prompt.call_args
        prompt = call_args.kwargs.get('prompt') or call_args[1].get('prompt')
        assert '"subject": "Test Project"' in prompt
        assert '"complex"' in prompt
```

#### Test 5: 结果验证测试
```python
class TestContextValidatorResultValidation:
    """Test validation of LLM response structure."""
    
    @pytest.mark.asyncio
    async def test_missing_valid_field_triggers_retry(self):
        """Response without 'valid' field should trigger retry."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(side_effect=[
            Mock(success=True, content='{"reason": "Missing valid field", "missing_info": []}', is_success=lambda: True),
            Mock(success=True, content='{"valid": true, "reason": "OK", "missing_info": []}', is_success=lambda: True),
        ])
        
        validator = ContextValidator(session_manager=mock_session, max_retries=1)
        result = await validator.validate({"subject": "Test"})
        
        assert result.valid is True
        assert mock_session.single_prompt.call_count == 2
    
    @pytest.mark.asyncio
    async def test_invalid_valid_type_triggers_retry(self):
        """Response with non-boolean 'valid' should trigger retry."""
        mock_session = Mock()
        mock_session.single_prompt = AsyncMock(side_effect=[
            Mock(success=True, content='{"valid": "yes", "reason": "Invalid type", "missing_info": []}', is_success=lambda: True),
            Mock(success=True, content='{"valid": true, "reason": "OK", "missing_info": []}', is_success=lambda: True),
        ])
        
        validator = ContextValidator(session_manager=mock_session, max_retries=1)
        result = await validator.validate({"subject": "Test"})
        
        assert result.valid is True
```

### Phase 2: 实现代码（绿阶段）

```python
"""Context Validator - Extracted from HybridOrchestrator.

Provides structured context validation with retry logic and configurable
error handling to replace the fail-open behavior.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import structlog



if TYPE_CHECKING:
    from autoBMAD.docuswarm.llm.session_manager import SessionManager

logger = structlog.get_logger(__name__)


# Default validation prompt template
DEFAULT_VALIDATION_PROMPT = """You are a technical context validator. Analyze the context and output ONLY a JSON object.

**Context to validate:**
{subject_context}

**Validation rules:**
1. Check if there's a clear objective (what to create)
2. Check if scope is defined (requirements stated)
3. Check if there's sufficient detail to start

**Output format (respond with ONLY this JSON, no markdown blocks, no other text):**

{{
  "valid": true,
  "reason": "Brief validation reason",
  "missing_info": []
}}

**Important:**
- Do NOT call any tools
- Do NOT use markdown code blocks
- Output ONLY the JSON object
- Use lowercase true/false for booleans
"""


@dataclass
class ValidationResult:
    """Result of context validation.
    
    Attributes:
        valid: Whether context passed validation
        reason: Human-readable explanation
        missing_info: List of missing required information
        raw_response: Original LLM response for debugging
        attempts: Number of attempts made (including retries)
        fallback_used: Whether fail-open fallback was used
    """
    valid: bool
    reason: str
    missing_info: list[str]
    raw_response: str | None = None
    attempts: int = 1
    fallback_used: bool = False


class ContextValidationError(Exception):
    """Raised when context validation fails in strict mode."""
    pass


class ContextValidator:
    """Validate pipeline context using LLM with structured retry.
    
    Extracted from HybridOrchestrator to follow Single Responsibility Principle.
    Implements configurable retry logic and fail-open/fail-close policies.
    
    Example:
        >>> validator = ContextValidator(session_manager)
        >>> result = await validator.validate({"subject": "My Project", ...})
        >>> if result.valid:
        ...     print("Context is valid")
        ... else:
        ...     print(f"Missing: {result.missing_info}")
    """
    
    DEFAULT_MAX_RETRIES = 2  # Total 3 attempts
    DEFAULT_FAIL_OPEN = False  # Safer default
    
    def __init__(
        self,
        session_manager: SessionManager,
        prompt_template: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        fail_open: bool = DEFAULT_FAIL_OPEN,
    ) -> None:
        """Initialize context validator.
        
        Args:
            session_manager: SessionManager for LLM interactions (Claude SDK based)
            prompt_template: Optional custom validation prompt template
            max_retries: Maximum retry attempts for failed parsing
            fail_open: If True, allow pipeline on validation failure
        """
        self._session_manager = session_manager
        self._prompt_template = prompt_template or DEFAULT_VALIDATION_PROMPT
        self._max_retries = max_retries
        self._fail_open = fail_open
        self._logger = logger.bind(component="ContextValidator")
    
    async def validate(
        self,
        subject_context: dict[str, Any],
    ) -> ValidationResult:
        """Validate subject context with structured retry.
        
        Implements retry logic:
        1. Call LLM with validation prompt
        2. Parse JSON response
        3. Validate response structure
        4. If any step fails, retry up to max_retries
        5. If all retries fail, apply fail_open policy
        
        Args:
            subject_context: The context dictionary to validate
            
        Returns:
            ValidationResult with validation status
            
        Raises:
            ContextValidationError: If validation fails and fail_open=False
        """
        context_str = json.dumps(subject_context, indent=2)
        prompt = self._prompt_template.format(subject_context=context_str)
        
        last_error: Exception | None = None
        last_raw_response: str | None = None
        
        for attempt in range(self._max_retries + 1):
            try:
                self._logger.info("validation_attempt", attempt=attempt + 1)
                
                # Call LLM
                result = await self._session_manager.single_prompt(
                    prompt=prompt,
                    agent_name="context_validator",
                )
                content = result.content if result.is_success() else ""
                
                # Extract content
                content = extract_text_from_messages(messages)
                last_raw_response = content
                
                if not content:
                    raise ValueError("Empty response from LLM")
                
                # Parse and validate
                result = self._parse_validation_response(content)
                
                # Success - return result
                self._logger.info(
                    "validation_success",
                    valid=result.valid,
                    reason=result.reason,
                    attempts=attempt + 1,
                )
                return result
                
            except Exception as e:
                last_error = e
                self._logger.warning(
                    "validation_attempt_failed",
                    attempt=attempt + 1,
                    error=str(e),
                )
                
                if attempt < self._max_retries:
                    # Will retry
                    continue
                else:
                    # Exhausted retries
                    break
        
        # All retries exhausted - apply policy
        return await self._handle_validation_failure(
            last_error, last_raw_response, self._max_retries + 1
        )
    
    def _parse_validation_response(self, content: str) -> ValidationResult:
        """Parse and validate LLM response.
        
        Args:
            content: Raw LLM response content
            
        Returns:
            ValidationResult
            
        Raises:
            ValueError: If response is invalid
        """
        # Strip markdown
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        # Parse JSON
        data = json.loads(content.strip())
        
        # Validate structure
        if "valid" not in data:
            raise ValueError("Response missing 'valid' field")
        if not isinstance(data["valid"], bool):
            raise ValueError(f"'valid' must be boolean, got {type(data['valid'])}")
        
        return ValidationResult(
            valid=data["valid"],
            reason=data.get("reason", "No reason provided"),
            missing_info=data.get("missing_info", []),
            raw_response=content,
            attempts=1,
            fallback_used=False,
        )
    
    async def _handle_validation_failure(
        self,
        error: Exception | None,
        raw_response: str | None,
        attempts: int,
    ) -> ValidationResult:
        """Handle validation failure after retries exhausted.
        
        Args:
            error: Last error that occurred
            raw_response: Last raw response from LLM
            attempts: Number of attempts made
            
        Returns:
            ValidationResult (if fail_open=True)
            
        Raises:
            ContextValidationError: If fail_open=False
        """
        self._logger.error(
            "validation_failed_all_attempts",
            attempts=attempts,
            error=str(error) if error else "Unknown",
        )
        
        if self._fail_open:
            # Return fallback result with warning
            return ValidationResult(
                valid=True,  # Allow to proceed
                reason=f"Validation failed after {attempts} attempts: {error}. Proceeding with caution.",
                missing_info=[],
                raw_response=raw_response,
                attempts=attempts,
                fallback_used=True,  # Mark as fallback
            )
        else:
            # Raise exception
            raise ContextValidationError(
                f"Context validation failed after {attempts} attempts: {error}"
            )
```

---

## 4. 重构 Orchestrator

### 重构前
```python
class HybridOrchestrator:
    async def _validate_context(self, subject_context):
        # 80+ lines of validation logic
        ...
    
    async def start_pipeline(self, subject_context, pipeline_id=None):
        validation_result = await self._validate_context(subject_context)
        if not validation_result.get("valid", False):
            raise ContextValidationError(...)
```

### 重构后
```python
from autoBMAD.docuswarm.pipeline.context_validator import (
    ContextValidator, ContextValidationError
)

class HybridOrchestrator:
    def __init__(self, ...):
        ...
        self._context_validator: ContextValidator | None = None
    
    def _get_context_validator(self) -> ContextValidator:
        """Get or create context validator."""
        if self._context_validator is None:
            session_manager = self._get_or_create_session_manager()
            self._context_validator = ContextValidator(
                session_manager=session_manager,
                fail_open=False,  # Safer default
                max_retries=2,
            )
        return self._context_validator
    
    async def start_pipeline(self, subject_context, pipeline_id=None):
        # Replace complex validation logic with simple call
        validator = self._get_context_validator()
        result = await validator.validate(subject_context)
        
        if not result.valid:
            raise ContextValidationError(
                f"Validation failed: {result.reason}. "
                f"Missing: {result.missing_info}"
            )
        
        # Log if fallback was used
        if result.fallback_used:
            logger.warning("validation_used_fallback", reason=result.reason)
```

---

## 5. 验收标准

| 检查项 | 工具 | 标准 |
|--------|------|------|
| 单元测试通过 | `pytest tests/unit/test_context_validator.py -v` | 100% 通过 |
| 代码覆盖率 | `--cov=autoBMAD.docuswarm.pipeline.context_validator` | >= 90% |
| 类型检查 | `basedpyright autoBMAD/docuswarm/pipeline/context_validator.py` | 0 错误 |
| 代码风格 | `ruff check autoBMAD/docuswarm/pipeline/context_validator.py` | 0 违反 |
| 集成测试 | `pytest tests/integration/ -k validation` | 100% 通过 |
| 行数减少 | `wc -l orchestrator.py` | 减少 ~80 行 |

---

## 6. 风险与缓解

| 风险 | 可能性 | 影响 | 缓解 |
|------|--------|------|------|
| fail_open=False 破坏现有流程 | 高 | 高 | 先使用 fail_open=True 部署，监控后切换 |
| 重试增加延迟 | 中 | 中 | 添加重试延迟退避，max_retries 可配置 |
| Prompt 格式不兼容 | 低 | 高 | 保持默认 prompt 与原版本一致 |
