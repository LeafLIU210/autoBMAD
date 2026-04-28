# Epic 13: ContextValidator 提取重构

**Epic ID**: EPIC-13  
**关联方案**: [TDD-02-ContextValidator-Refactor.md](../solution/TDD-02-ContextValidator-Refactor.md)  
**Version**: 1.0  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 1-2 Days  
**Priority**: P0 - 关键

---

## 1. Epic Overview

### 1.1 Summary

从 `HybridOrchestrator` 中提取 `_validate_context` 方法，创建独立的 `ContextValidator` 组件。实现结构化重试逻辑，替换原有的 fail-open 策略，提升验证可靠性。

### 1.2 Business Value

- **单一职责**: 分离验证逻辑，Orchestrator 专注于流程控制
- **可靠性提升**: 结构化重试替代 fail-open，减少无效上下文导致的低质量输出
- **可配置性**: 支持 `fail_open` 和 `fail_close` 两种模式
- **可观测性**: 记录重试次数和 fallback 使用情况

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 职责分离 | Orchestrator 不再包含验证逻辑 |
| 重试成功率 | 第2/3次尝试成功率 >= 80% |
| 测试覆盖率 | ContextValidator >= 90% |
| 行数减少 | orchestrator.py 减少 ~80 行 |

### 1.4 Dependencies

- **Requires**: 无（独立重构）
- **Blocks**: 无

---

## 2. Architecture Context

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContextValidator 组件架构                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HybridOrchestrator                                                         │
│  ├─→ ContextValidator (新增，~200行)                                        │
│  │   ├─→ ValidationResult (dataclass)                                      │
│  │   ├─→ validate(context) → ValidationResult                              │
│  │   ├─→ _parse_validation_response()                                      │
│  │   └─→ _handle_validation_failure()                                      │
│  │                                                                          │
│  │  流程:                                                                    │
│  │  1. Build prompt → 2. Call LLM → 3. Parse JSON                         │
│  │  4. Validate structure → 5. Retry if needed                             │
│  │  6. Fail-open/close policy                                              │
│  │                                                                          │
│  └─→ 简化后的 start_pipeline():                                             │
│      result = await validator.validate(context)                            │
│      if not result.valid: raise ValidationError                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Files

| File | Purpose |
|------|---------|
| `pipeline/context_validator.py` | 新增：ContextValidator 实现 |
| `pipeline/orchestrator.py` | 修改：移除 `_validate_context` 方法 |
| `tests/unit/test_context_validator.py` | 新增：单元测试 |

---

## 3. User Stories

### Story 13.1: ValidationResult 数据类

**ID**: US-13.1  
**As a** developer  
**I want to** 定义 ValidationResult 数据类  
**So that** 验证结果结构清晰

**Acceptance Criteria**:
- [ ] `ValidationResult` dataclass 定义完成
- [ ] 包含 `valid`, `reason`, `missing_info` 字段
- [ ] 包含 `raw_response`, `attempts`, `fallback_used` 字段
- [ ] 定义 `ContextValidationError` 异常类

**Technical Tasks**:
1. 创建 `pipeline/context_validator.py`
2. 定义 `ValidationResult` 数据类
3. 定义 `ContextValidationError` 异常

**Implementation**:
```python
@dataclass
class ValidationResult:
    valid: bool
    reason: str
    missing_info: list[str]
    raw_response: str | None = None
    attempts: int = 1
    fallback_used: bool = False

class ContextValidationError(Exception):
    pass
```

**Definition of Done**:
- [ ] 数据类定义完整
- [ ] 类型注解正确
- [ ] 文档字符串清晰

---

### Story 13.2: 基础验证逻辑

**ID**: US-13.2  
**As a** developer  
**I want to** 实现基础验证逻辑  
**So that** 可以验证上下文完整性

**Acceptance Criteria**:
- [ ] `ContextValidator` 类初始化支持配置参数
- [ ] `validate` 方法调用 LLM 并解析响应
- [ ] 成功时返回 `ValidationResult`
- [ ] 支持自定义 prompt 模板

**Technical Tasks**:
1. 实现 `ContextValidator.__init__`
2. 实现 `validate` 核心方法
3. 实现 `_parse_validation_response`

**Implementation**:
```python
class ContextValidator:
    DEFAULT_MAX_RETRIES = 2
    DEFAULT_FAIL_OPEN = False
    
    def __init__(
        self,
        session_manager: SessionManager,
        prompt_template: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        fail_open: bool = DEFAULT_FAIL_OPEN,
    ) -> None:
        self._session_manager = session_manager
        self._prompt_template = prompt_template or DEFAULT_VALIDATION_PROMPT
        self._max_retries = max_retries
        self._fail_open = fail_open
```

**Definition of Done**:
- [ ] 初始化参数完整
- [ ] 默认 prompt 模板定义
- [ ] LLM 调用集成正确

---

### Story 13.3: Markdown 代码块处理

**ID**: US-13.3  
**As a** developer  
**I want to** 处理 Markdown 代码块  
**So that** LLM 返回的 JSON 可以被正确解析

**Acceptance Criteria**:
- [ ] 去除 ````json` 前缀
- [ ] 去除 ` ``` ` 标记
- [ ] 处理嵌套代码块

**Technical Tasks**:
1. 在 `_parse_validation_response` 中实现清理逻辑
2. 测试各种 Markdown 格式

**Implementation**:
```python
def _parse_validation_response(self, content: str) -> ValidationResult:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    data = json.loads(content.strip())
    # ... validate and return
```

**Definition of Done**:
- [ ] Markdown 格式测试通过
- [ ] 非 Markdown 格式也支持

---

### Story 13.4: 结构化重试逻辑

**ID**: US-13.4  
**As a** developer  
**I want to** 实现结构化重试  
**So that** JSON 解析失败时可以自动重试

**Acceptance Criteria**:
- [ ] 最多重试 `max_retries` 次
- [ ] 记录每次尝试的错误
- [ ] 重试成功返回结果并标记 `attempts`
- [ ] 所有重试失败进入 failure handler

**Technical Tasks**:
1. 在 `validate` 中实现循环重试
2. 记录每次尝试的错误
3. 跟踪尝试次数

**Implementation**:
```python
async def validate(self, subject_context: dict[str, Any]) -> ValidationResult:
    context_str = json.dumps(subject_context, indent=2)
    prompt = self._prompt_template.format(subject_context=context_str)
    
    last_error = None
    last_raw_response = None
    
    for attempt in range(self._max_retries + 1):
        try:
            messages = await self._session_manager.single_prompt(...)
            content = extract_text_from_messages(messages)
            result = self._parse_validation_response(content)
            result.attempts = attempt + 1
            return result
        except Exception as e:
            last_error = e
            if attempt < self._max_retries:
                continue
            break
    
    return await self._handle_validation_failure(...)
```

**Definition of Done**:
- [ ] 重试逻辑测试通过
- [ ] 尝试次数正确记录
- [ ] 日志记录完整

---

### Story 13.5: Fail-Open/Close 策略

**ID**: US-13.5  
**As a** developer  
**I want to** 实现可配置的错误处理策略  
**So that** 可以根据环境选择严格或宽松模式

**Acceptance Criteria**:
- [ ] `fail_open=True`: 返回 `valid=True` 但标记 `fallback_used`
- [ ] `fail_open=False`: 抛出 `ContextValidationError`
- [ ] 原因中包含失败详情
- [ ] 日志记录策略选择

**Technical Tasks**:
1. 实现 `_handle_validation_failure` 方法
2. 根据 `self._fail_open` 决定行为
3. 记录 fallback 使用情况

**Implementation**:
```python
async def _handle_validation_failure(
    self, error, raw_response, attempts
) -> ValidationResult:
    self._logger.error("validation_failed_all_attempts", attempts=attempts)
    
    if self._fail_open:
        return ValidationResult(
            valid=True,
            reason=f"Validation failed after {attempts} attempts",
            missing_info=[],
            raw_response=raw_response,
            attempts=attempts,
            fallback_used=True,
        )
    else:
        raise ContextValidationError(
            f"Context validation failed after {attempts} attempts"
        )
```

**Definition of Done**:
- [ ] fail_open 测试通过
- [ ] fail_close 测试通过
- [ ] 异常消息清晰

---

### Story 13.6: Orchestrator 集成

**ID**: US-13.6  
**As a** developer  
**I want to** 集成到 Orchestrator  
**So that** 验证流程使用新组件

**Acceptance Criteria**:
- [ ] Orchestrator 中移除 `_validate_context` 方法
- [ ] 添加 `_get_context_validator` 辅助方法
- [ ] `start_pipeline` 使用新的验证流程
- [ ] 支持配置 `fail_open` 模式

**Technical Tasks**:
1. 删除原有 `_validate_context` 方法
2. 添加 `_context_validator` 实例变量
3. 实现 `_get_context_validator`
4. 修改 `start_pipeline` 调用方式

**Implementation**:
```python
class HybridOrchestrator:
    def __init__(self, ...):
        ...
        self._context_validator: ContextValidator | None = None
    
    def _get_context_validator(self) -> ContextValidator:
        if self._context_validator is None:
            self._context_validator = ContextValidator(
                session_manager=self._get_or_create_session_manager(),
                fail_open=False,
                max_retries=2,
            )
        return self._context_validator
    
    async def start_pipeline(self, subject_context, pipeline_id=None):
        validator = self._get_context_validator()
        result = await validator.validate(subject_context)
        
        if not result.valid:
            raise ContextValidationError(...)
        
        if result.fallback_used:
            logger.warning("validation_used_fallback")
```

**Definition of Done**:
- [ ] 原有方法已删除
- [ ] 新流程集成完成
- [ ] 错误处理正确

---

## 4. Technical Specifications

### 4.1 API Reference

| Class/Method | Signature | Description |
|--------------|-----------|-------------|
| `ValidationResult` | `dataclass` | 验证结果数据类 |
| `ContextValidationError` | `Exception` | 验证失败异常 |
| `ContextValidator.__init__` | `(session_manager: SessionManager, prompt_template=None, max_retries=2, fail_open=False)` | 初始化 |
| `ContextValidator.validate` | `(subject_context: dict) -> ValidationResult` | 执行验证 |

### 4.2 Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | 2 | 最大重试次数（总共尝试 max_retries+1 次） |
| `fail_open` | False | 失败后是否允许继续 |

---

## 5. Testing Strategy

### 5.1 Unit Tests

| Test Class | Description |
|------------|-------------|
| `TestContextValidatorBasic` | 基础验证功能测试 |
| `TestContextValidatorRetry` | 结构化重试逻辑测试 |
| `TestContextValidatorMarkdown` | Markdown 代码块处理测试 |
| `TestContextValidatorPrompt` | Prompt 模板测试 |
| `TestContextValidatorResultValidation` | 结果结构验证测试 |

### 5.2 Key Test Cases

```python
# 关键测试：重试成功
async def test_retry_on_json_parse_error(self):
    mock_session.single_prompt = AsyncMock(side_effect=[
        [Mock(content='Not valid JSON')],
        [Mock(content='{"valid": true, "reason": "OK", "missing_info": []}')],
    ])
    result = await validator.validate({"subject": "Test"})
    assert result.valid is True
    assert result.attempts == 2

# 关键测试：fail_open 策略
async def test_retry_exhaustion_with_fail_open(self):
    validator = ContextValidator(..., fail_open=True)
    result = await validator.validate({"subject": "Test"})
    assert result.valid is True
    assert result.fallback_used is True
```

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| fail_open=False 破坏现有流程 | 高 | 高 | 先使用 fail_open=True 部署，监控后切换 |
| 重试增加延迟 | 中 | 中 | max_retries 可配置，生产环境根据需要调整 |
| Prompt 格式不兼容 | 低 | 高 | 保持默认 prompt 与原版本一致 |

---

## 7. Definition of Done (Epic Level)

- [ ] US-13.1 完成：ValidationResult 数据类
- [ ] US-13.2 完成：基础验证逻辑
- [ ] US-13.3 完成：Markdown 代码块处理
- [ ] US-13.4 完成：结构化重试逻辑
- [ ] US-13.5 完成：Fail-Open/Close 策略
- [ ] US-13.6 完成：Orchestrator 集成
- [ ] 单元测试覆盖率 >= 90%
- [ ] 集成测试 100% 通过
- [ ] orchestrator.py 行数减少 ~80 行
- [ ] basedpyright 0 错误
- [ ] ruff 0 违反

---

## 8. References

| Document | Location |
|----------|----------|
| TDD 方案 | `docs/solution/TDD-02-ContextValidator-Refactor.md` |
| Pipeline Architecture | `docs/architecture/03_PIPELINE_ARCHITECTURE.md` |

---

**Epic End**
