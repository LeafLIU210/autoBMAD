# Epic 16: Claude SDK Wrapper（SDK 替换）

**Epic ID**: EPIC-16  
**关联方案**: [TDD-05-SDKWrapper-Refactor.md](../solution/TDD-05-SDKWrapper-Refactor.md)  
**Version**: 1.0  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Estimated Effort**: 2-3 Days  
**Priority**: P1 - 重要

---

> **注意**: 本文档描述的 `claude-agent-sdk` + **Kimi Code API** 方案是项目的**唯一 SDK 方案**，已完全替代之前的 `kimi-agent-sdk` 方案。本文档同时作为 EPIC-06 至 EPIC-11（原 SDK 相关 Epic）的统一替代方案。

---

## 1. Epic Overview

### 1.1 Summary

采用 `claude-agent-sdk` + **Kimi Code API** 的 OpenAI 兼容接口作为**唯一** SDK 方案。创建 `ClaudeSDKWrapper` 和兼容层 `SessionManager`，实现从旧架构的平滑迁移。

**关键配置**:
- `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`
- `ANTHROPIC_API_KEY=<your-kimi-api-key>`

> 此方案与 `epic_automation` 使用的 SDK 保持一致，通过 Kimi Code API 的 OpenAI 兼容接口工作。`kimi-agent-sdk` 已被完全弃用。

### 1.2 Business Value

- **架构统一**: 与 `epic_automation` 使用相同 SDK
- **标准化**: 使用通用的 Tool Use Block 模式
- **可维护性**: 简化 MessageAggregator 等复杂逻辑
- **向前兼容**: 为未来功能扩展奠定基础

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| 向后兼容 | 原调用点无需修改 |
| 测试覆盖率 | ClaudeSDKWrapper >= 85%, SessionManager >= 85% |
| 功能等价 | 所有现有功能正常工作 |
| 环境配置 | 支持 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_API_KEY` |

### 1.4 Dependencies

- **Requires**: 无（但必须先于 EPIC-14 和 EPIC-15 完成）
- **Blocks**: EPIC-14 (Tool Result Extractor), EPIC-15 (Context Resolver)

---

## 2. Architecture Context

### 2.1 SDK 架构

```
统一架构: claude-agent-sdk + Kimi Code API
──────────────────────────────────────────
query() 函数式 API
返回 AsyncGenerator
ResultMessage (终结)
标准 Tool Use Block
标准 Path
环境变量: ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY
```

### 2.2 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Claude SDK Wrapper 架构                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SessionManager (~150行)                                                    │
│  ├─→ single_prompt(prompt, agent_name, ...) → SDKResult                     │
│  ├─→ execute_with_tools(prompt, tools, ...) → SDKResult                     │
│  ├─→ work_dir, config 属性                                                  │
│  │                                                                          │
│  └─→ ClaudeSDKWrapper (内部使用)                                            │
│      ├─→ execute(prompt, agent_name, timeout, cwd) → SDKResult            │
│      ├─→ 设置 ANTHROPIC_* 环境变量                                         │
│      ├─→ query() AsyncGenerator 处理                                       │
│      └─→ ResultMessage 提取                                                │
│                                                                             │
│  ★ 使用 Kimi Code API 的 OpenAI 兼容接口 ★                                │
│  ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"                         │
│  ANTHROPIC_API_KEY="your-kimi-api-key"                                     │
│                                                                             │
│  ★ 唯一方案：claude-agent-sdk + Kimi Code API ★                           │
└─────────────────────────────────────────────────────────────────────────────┘
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Key Files

| File | Purpose |
|------|---------|
| `llm/claude_sdk_wrapper.py` | 新增：ClaudeSDKWrapper 实现 |
| `llm/session_manager.py` | 重写：SessionManager 统一接口层 |
| `llm/__init__.py` | 修改：更新导出 |
| `tests/unit/test_claude_sdk_wrapper.py` | 新增：SDK Wrapper 测试 |
| `tests/unit/test_session_manager.py` | 新增/修改：SessionManager 测试 |

---

## 3. User Stories

### Story 16.1: SDKResult 数据类

**ID**: US-16.1  
**As a** developer  
**I want to** 定义 SDKResult 数据类  
**So that** SDK 执行结果标准化

**Acceptance Criteria**:
- [ ] `SDKResult` dataclass 定义完成
- [ ] 包含 `success`, `content`, `error`, `duration`
- [ ] 包含 `messages`, `tool_calls` 字段
- [ ] 实现 `is_success()` 方法
- [ ] 定义 `SDKError`, `SDKNotAvailableError` 异常

**Technical Tasks**:
1. 创建 `llm/claude_sdk_wrapper.py`
2. 定义 `SDKResult` 数据类
3. 定义异常类

**Implementation**:
```python
@dataclass
class SDKResult:
    success: bool
    content: str | None
    error: str | None
    duration: float
    messages: list[Any] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    
    def is_success(self) -> bool:
        return self.success and self.content is not None

class SDKError(Exception):
    pass

class SDKNotAvailableError(SDKError):
    pass
```

**Definition of Done**:
- [ ] 数据类定义完整
- [ ] 方法实现正确
- [ ] 异常类层次清晰

---

### Story 16.2: ClaudeSDKWrapper 初始化

**ID**: US-16.2  
**As a** developer  
**I want to** 实现 ClaudeSDKWrapper 初始化  
**So that** 支持环境变量和显式参数

**Acceptance Criteria**:
- [ ] 支持 `base_url`, `api_key`, `permission_mode` 参数
- [ ] 从环境变量读取默认值
- [ ] 设置合理的默认 base_url
- [ ] 集成 structlog 日志

**Technical Tasks**:
1. 实现 `__init__` 方法
2. 处理环境变量读取
3. 设置默认值

**Implementation**:
```python
class ClaudeSDKWrapper:
    DEFAULT_BASE_URL = "https://api.kimi.com/coding/"
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        permission_mode: str = "bypassPermissions",
    ) -> None:
        self.base_url = base_url or os.getenv(
            "ANTHROPIC_BASE_URL",
            self.DEFAULT_BASE_URL  # https://api.kimi.com/coding/
        )
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.permission_mode = permission_mode
        self._logger = logger.bind(component="ClaudeSDKWrapper")
```

**Definition of Done**:
- [ ] 显式参数测试通过
- [ ] 环境变量测试通过
- [ ] 默认值测试通过

---

### Story 16.3: query() 执行与结果提取

**ID**: US-16.3  
**As a** developer  
**I want to** 实现 query() 执行  
**So that** 可以调用 Claude SDK

**Acceptance Criteria**:
- [ ] 设置 `ANTHROPIC_*` 环境变量
- [ ] 创建 `ClaudeAgentOptions`
- [ ] 调用 `query()` 获取 AsyncGenerator
- [ ] 提取 `ResultMessage`
- [ ] 处理成功、失败、无结果情况

**Technical Tasks**:
1. 实现 `execute` 方法
2. 处理环境变量设置
3. 实现消息迭代和结果提取
4. 处理各种结果状态

**Implementation**:
```python
async def execute(
    self,
    prompt: str,
    agent_name: str = "docuswarm",
    timeout: float | None = None,
    cwd: str | Path | None = None,
) -> SDKResult:
    if not SDK_AVAILABLE or query is None:
        return SDKResult(
            success=False,
            content=None,
            error="Claude Agent SDK not available",
            duration=0.0,
        )
    
    timeout = timeout or self.DEFAULT_TIMEOUT
    start_time = time.time()
    
    os.environ["ANTHROPIC_BASE_URL"] = self.base_url
    os.environ["ANTHROPIC_API_KEY"] = self.api_key
    
    options = ClaudeAgentOptions(
        permission_mode=self.permission_mode,
        cwd=str(cwd or Path.cwd()),
    )
    
    messages: list[Any] = []
    result_content: str | None = None
    
    async for message in query(prompt=prompt, options=options):
        messages.append(message)
        if isinstance(message, ResultMessage):
            if message.is_error:
                return SDKResult(
                    success=False,
                    content=None,
                    error=str(message.result),
                    duration=time.time() - start_time,
                    messages=messages,
                )
            else:
                result_content = str(message.result)
                break
    
    duration = time.time() - start_time
    
    if result_content is not None:
        return SDKResult(
            success=True,
            content=result_content,
            error=None,
            duration=duration,
            messages=messages,
        )
    else:
        return SDKResult(
            success=False,
            content=None,
            error="No ResultMessage received",
            duration=duration,
            messages=messages,
        )
```

**Definition of Done**:
- [ ] 成功执行测试通过
- [ ] 错误处理测试通过
- [ ] 无结果处理测试通过

---

### Story 16.4: 取消与异常处理

**ID**: US-16.4  
**As a** developer  
**I want to** 处理取消和异常  
**So that** 系统健壮性提升

**Acceptance Criteria**:
- [ ] `asyncio.CancelledError` 正确处理
- [ ] 其他异常捕获并返回错误
- [ ] 记录取消和错误日志
- [ ] 确保资源清理

**Technical Tasks**:
1. 添加异常处理逻辑
2. 记录错误信息
3. 确保取消时返回正确状态

**Implementation**:
```python
try:
    # ... execution logic
except asyncio.CancelledError:
    self._logger.warning("sdk_execute_cancelled", agent_name=agent_name)
    return SDKResult(
        success=False,
        content=None,
        error="Execution cancelled",
        duration=time.time() - start_time,
    )
except Exception as e:
    self._logger.error(
        "sdk_execute_error",
        agent_name=agent_name,
        error=str(e),
    )
    return SDKResult(
        success=False,
        content=None,
        error=str(e),
        duration=time.time() - start_time,
    )
```

**Definition of Done**:
- [ ] 取消处理测试通过
- [ ] 异常处理测试通过
- [ ] 日志记录验证

---

### Story 16.5: SessionManager 兼容层

**ID**: US-16.5  
**As a** developer  
**I want to** 实现 SessionManager 兼容层  
**So that** 现有代码无需修改即可使用

**Acceptance Criteria**:
- [ ] `SessionManager` 类实现
- [ ] `single_prompt` 方法兼容原接口
- [ ] `execute_with_tools` 方法实现
- [ ] `work_dir`, `config` 属性
- [ ] 异步上下文管理器支持

**Technical Tasks**:
1. 重写 `llm/session_manager.py`
2. 使用 `ClaudeSDKWrapper` 内部实现
3. 保持与原接口兼容

**Implementation**:
```python
class SessionManager:
    def __init__(
        self,
        work_dir: Path | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._work_dir = work_dir or Path.cwd()
        self._sdk = ClaudeSDKWrapper(
            base_url=base_url,
            api_key=api_key,
        )
        self._logger = logger.bind(component="SessionManager")
    
    @property
    def work_dir(self) -> Path:
        return self._work_dir
    
    @property
    def config(self) -> dict[str, Any]:
        return {
            "base_url": self._sdk.base_url,
            "work_dir": str(self._work_dir),
        }
    
    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        result = await self._sdk.execute(
            prompt=prompt,
            agent_name=agent_name,
            timeout=timeout,
            cwd=self._work_dir,
        )
        return result
    
    async def execute_with_tools(
        self,
        prompt: str,
        tools: list[Any] | None = None,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        if tools:
            tool_desc = "\n".join(
                f"- {t.name}: {t.description}"
                for t in tools
                if hasattr(t, "name") and hasattr(t, "description")
            )
            full_prompt = f"""Available tools:
{tool_desc}

{prompt}"""
        else:
            full_prompt = prompt
        
        return await self.single_prompt(
            prompt=full_prompt,
            agent_name=agent_name,
            timeout=timeout,
        )
    
    async def close(self) -> None:
        self._logger.debug("session_manager_closed")
    
    async def __aenter__(self) -> SessionManager:
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
```

**Definition of Done**:
- [ ] 接口兼容测试通过
- [ ] single_prompt 测试通过
- [ ] execute_with_tools 测试通过
- [ ] 属性访问测试通过

---

### Story 16.6: SafeAsyncGenerator

**ID**: US-16.6  
**As a** developer  
**I want to** 实现 SafeAsyncGenerator  
**So that** 防止 cancel scope 问题

**Acceptance Criteria**:
- [ ] `SafeAsyncGenerator` 包装类实现
- [ ] 包装 `AsyncIterator`
- [ ] 防止重复迭代问题
- [ ] 支持 `aclose()` 清理

**Technical Tasks**:
1. 实现 `SafeAsyncGenerator` 类
2. 实现 `__aiter__` 和 `__anext__`
3. 实现 `aclose` 方法

**Implementation**:
```python
class SafeAsyncGenerator:
    def __init__(self, generator: AsyncIterator[Any]) -> None:
        self.generator = generator
        self._closed = False
    
    def __aiter__(self) -> SafeAsyncGenerator:
        return self
    
    async def __anext__(self) -> Any:
        if self._closed:
            raise StopAsyncIteration
        try:
            return await self.generator.__anext__()
        except StopAsyncIteration:
            self._closed = True
            raise
    
    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
```

**Definition of Done**:
- [ ] 迭代测试通过
- [ ] 关闭测试通过
- [ ] 重复迭代测试正确抛出异常

---

## 4. Technical Specifications

### 4.1 API Reference

#### ClaudeSDKWrapper

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(base_url=None, api_key=None, permission_mode="bypassPermissions")` | 初始化 |
| `execute` | `(prompt, agent_name="docuswarm", timeout=None, cwd=None) -> SDKResult` | 执行 |

#### SessionManager

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(work_dir=None, base_url=None, api_key=None)` | 初始化 |
| `single_prompt` | `(prompt, mode="agent", yolo=True, agent_name="docuswarm", timeout=1800) -> SDKResult` | 单次提示 |
| `execute_with_tools` | `(prompt, tools=None, agent_name="docuswarm", timeout=1800) -> SDKResult` | 带工具执行 |

### 4.2 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_BASE_URL` | `https://api.kimi.com/coding/` | API 基础 URL |
| `ANTHROPIC_API_KEY` | `""` | API 密钥 |

### 4.3 SessionManager 接口

`SessionManager` 提供统一的 LLM 调用接口：

| 方法/属性 | 说明 |
|-----------|------|
| `session_manager.single_prompt(prompt, agent_name, timeout)` | 执行单次提示，返回 SDKResult |
| `session_manager.work_dir` | 工作目录路径 |
| `session_manager.config` | 配置字典 |
| `session_manager.execute_with_tools(prompt, tools, agent_name, timeout)` | 带工具描述执行 |

> **注意**: `mode` 和 `yolo` 参数为向后兼容保留，但会被忽略（SDK 使用默认行为）。

---

## 5. Testing Strategy

### 5.1 Unit Tests - ClaudeSDKWrapper

| Test Class | Description |
|------------|-------------|
| `TestClaudeSDKWrapperInit` | 初始化测试 |
| `TestClaudeSDKWrapperExecute` | 执行测试 |
| `TestClaudeSDKWrapperEnvironment` | 环境变量测试 |

### 5.2 Unit Tests - SessionManager

| Test Class | Description |
|------------|-------------|
| `TestSessionManagerInit` | 初始化测试 |
| `TestSessionManagerSinglePrompt` | single_prompt 测试 |
| `TestSessionManagerExecuteWithTools` | execute_with_tools 测试 |

### 5.3 Key Test Cases

```python
# 初始化测试
def test_init_reads_from_env(self, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://custom.api.com/")
    wrapper = ClaudeSDKWrapper()
    assert wrapper.base_url == "https://custom.api.com/"

# 执行成功测试
@pytest.mark.asyncio
@patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
async def test_execute_success(self, mock_query):
    mock_query.return_value = AsyncMock()
    mock_query.return_value.__aiter__ = AsyncMock(
        return_value=iter([ResultMessage(result="Success", is_error=False)])
    )
    result = await wrapper.execute("Test prompt")
    assert result.success is True
    assert result.content == "Success"
```

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK 替换不兼容 | 中 | 高 | 提供 SessionManager 兼容层，内部使用 ClaudeSDKWrapper |
| 环境变量配置错误 | 中 | 高 | 清晰的错误消息和文档 |
| CancelledError 处理不当 | 中 | 高 | SafeAsyncGenerator 包装 |
| API 响应格式变化 | 低 | 高 | 测试覆盖不同响应类型 |

---

## 7. Definition of Done (Epic Level)

- [ ] US-16.1 完成：SDKResult 数据类
- [ ] US-16.2 完成：ClaudeSDKWrapper 初始化
- [ ] US-16.3 完成：query() 执行与结果提取
- [ ] US-16.4 完成：取消与异常处理
- [ ] US-16.5 完成：SessionManager 兼容层
- [ ] US-16.6 完成：SafeAsyncGenerator
- [ ] ClaudeSDKWrapper 覆盖率 >= 85%
- [ ] SessionManager 覆盖率 >= 85%
- [ ] 集成测试 100% 通过
- [ ] 向后兼容性验证
- [ ] basedpyright 0 错误
- [ ] ruff 0 违反

---

## 8. References

| Document | Location |
|----------|----------|
| TDD 方案 | `docs/solution/TDD-05-SDKWrapper-Refactor.md` |
| Epic 14 | `docs/epics/EPIC-14-TOOL-RESULT-EXTRACTOR.md` |
| Epic 15 | `docs/epics/EPIC-15-CONTEXT-RESOLVER.md` |

---

**Epic End**
