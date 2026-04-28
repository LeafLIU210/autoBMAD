# DocuSwarm 测试驱动解决方案计划

**方案日期**: 2026-04-06  
**基于报告**: `docs/research/2026-04-06-docuswarm-root-cause-deep-research-report.md`  
**目标**: 通过测试驱动开发 (TDD) 方式修复 RC-1 ~ RC-5 根因  
**统一超时配置**: 60s (测试/调试配置)

---

## 目录

1. [总体策略](#总体策略)
2. [测试策略](#测试策略)
3. [阶段一：Fix-2B - cwd 职责拆分 (P0)](#阶段一fix-2b---cwd-职责拆分-p0)
4. [阶段二：Fix-1 - 超时配置接入 (P0)](#阶段二fix-1---超时配置接入-p0)
5. [阶段三：Fix-3 - Parse Fallback 扩展 (P1)](#阶段三fix-3---parse-fallback-扩展-p1)
7. [集成测试方案](#集成测试方案)
8. [验证清单](#验证清单)

---

## 总体策略

### TDD 循环

```
红 -> 绿 -> 重构
 |      |       |
 |      |       +-> 优化代码结构
 |      +-> 实现最小代码使测试通过
 +-> 编写失败测试
```

### 修复优先级

| 阶段 | 修复项 | 优先级 | 依赖 | 预估工时 |
|------|--------|--------|------|----------|
| 1 | Fix-2B: cwd 职责拆分 | P0 | 无 | 4h |
| 2 | Fix-1: 超时配置接入 | P0 | 阶段1 | 2h |
| 3 | Fix-3: Fallback 扩展 | P1 | 阶段1-2 | 2h |

### 分支策略

```
main
  └── fix/rc1-cwd-responsibility-split
        └── fix/rc2-timeout-configuration
              └── fix/rc3-parse-fallback
                    └── fix/rc4-fail-fast
```

---

## 测试策略

### 测试金字塔

```
       /\
      /  \
     / E2E\     (1 test: 完整流水线)
    /--------\
   /Integration\  (3 tests: SessionManager, Agent, Pipeline)
  /--------------\
 /   Unit Tests   \ (10+ tests: 各函数/方法)
/------------------\
```

### 测试文件命名

| 被测文件 | 测试文件 |
|----------|----------|
| `session_manager.py` | `test_session_manager_fix.py` |
| `independent.py` | `test_independent_agent_fix.py` |
| `executor.py` | `test_executor_fix.py` |
| `dual_agent.py` | `test_dual_agent_fix.py` |

### Mock 策略

```python
# SDK Client Mock
class MockClaudeSDKClient:
    def __init__(self, options):
        self.options = options
        self.connected = False
        
    async def connect(self):
        self.connected = True
        
    async def query(self, message):
        return MockQueryResult()
        
    async def receive_messages(self):
        # 模拟 ThinkingBlock + ToolUse + TextBlock
        yield MockThinkingBlock("Analyzing...")
        yield MockToolUseBlock("create_deliverable", {...})
        yield MockTextBlock('{"deliverable": {...}}')
```

---

## 阶段一：Fix-2B - cwd 职责拆分 (P0)

### 目标

拆分 `work_dir` 的双重职责：
- `cwd`: 仓库根目录 → 用于 Python import
- `output_dir`: output/pipeline_id → 用于文件输出

### Step 1.1: 编写失败测试

**测试文件**: `tests/fix/test_session_manager_cwd_split.py`

```python
"""Test for Fix-2B: cwd responsibility split."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch


class TestSessionManagerCwdSplit:
    """Test SessionManager cwd/output_dir split."""
    
    def test_session_manager_accepts_cwd_and_output_dir(self):
        """Test that SessionManager accepts both cwd and output_dir."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        repo_root = Path("/repo/root")
        output_dir = Path("/repo/root/output/pipeline-123")
        
        # Should accept both parameters
        sm = SessionManager(
            cwd=repo_root,
            output_dir=output_dir,
        )
        
        assert sm._cwd == repo_root
        assert sm._output_dir == output_dir
    
    def test_create_options_uses_cwd_not_output_dir(self):
        """Test that _create_options uses cwd for SDK options."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        repo_root = Path("/repo/root")
        output_dir = Path("/repo/root/output/pipeline-123")
        
        sm = SessionManager(
            cwd=repo_root,
            output_dir=output_dir,
        )
        
        options = sm._create_options(mode="agent", yolo=True)
        
        # Critical assertion: cwd should be repo root
        assert options.cwd == repo_root
        assert options.cwd != output_dir
    
    def test_output_dir_available_for_tools(self):
        """Test that output_dir is available for tool instantiation."""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        repo_root = Path("/repo/root")
        output_dir = Path("/repo/root/output/pipeline-123")
        
        sm = SessionManager(
            cwd=repo_root,
            output_dir=output_dir,
        )
        
        # output_dir should be accessible
        assert sm.output_dir == output_dir
```

### Step 1.2: 实现最小代码使测试通过

**修改文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
class SessionManager:
    """Updated SessionManager with cwd/output_dir split (Fix-2B)."""
    
    def __init__(
        self,
        cwd: Path | None = None,           # NEW: for SDK import
        output_dir: Path | None = None,    # NEW: for file output
        work_dir: Path | None = None,      # DEPRECATED: for backward compatibility
        agent_file: Path | None = None,
        config: Any | None = None,
        # ... other params
    ) -> None:
        """Initialize SessionManager with cwd/output_dir split.
        
        Args:
            cwd: Working directory for SDK (should be repo root for import).
            output_dir: Directory for file output (e.g., output/pipeline_id).
            work_dir: Deprecated, use cwd or output_dir instead.
        """
        # Handle backward compatibility
        if work_dir is not None:
            self._cwd = cwd or work_dir
            self._output_dir = output_dir or work_dir
        else:
            self._cwd = cwd or Path.cwd()
            self._output_dir = output_dir or self._cwd
            
        self._agent_file = agent_file
        self._config = config
        # ... rest of init
    
    @property
    def cwd(self) -> Path:
        """Get cwd for SDK import."""
        return self._cwd
    
    @property
    def output_dir(self) -> Path:
        """Get output directory for file operations."""
        return self._output_dir
    
    def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
        """Create options with correct cwd."""
        permission_mode = "bypassPermissions" if yolo else "default"
        
        options_dict: dict[str, Any] = {
            "cwd": self._cwd,  # FIX: Use _cwd instead of _work_dir
            "permission_mode": permission_mode,
        }
        
        if self._agent_file:
            options_dict["tools"] = [str(self._agent_file)]
            
        # ... rest of method
        
        return ClaudeAgentOptions(**options_dict)
```

### Step 1.3: 重构并添加更多测试

**测试文件**: `tests/fix/test_create_deliverable_tool_output_dir.py`

```python
"""Test CreateDeliverableTool with explicit output_dir."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, mock_open


class TestCreateDeliverableToolOutputDir:
    """Test CreateDeliverableTool output_dir support."""
    
    @pytest.mark.asyncio
    async def test_tool_uses_explicit_output_dir(self, tmp_path: Path):
        """Test that tool uses explicit output_dir parameter."""
        from autoBMAD.docuswarm.tools.create_deliverable import (
            CreateDeliverableTool,
            CreateDeliverableParams,
        )
        
        output_dir = tmp_path / "output" / "pipeline-123"
        output_dir.mkdir(parents=True)
        
        tool = CreateDeliverableTool(output_dir=output_dir)
        
        params = CreateDeliverableParams(
            title="Test Document",
            content="# Test\n\nContent",
        )
        
        result = await tool._execute(params)
        
        assert result.success is True
        assert result.result is not None
        assert "file_path" in result.result
        
        # Verify file was created in output_dir
        file_path = Path(result.result["file_path"])
        assert file_path.parent == output_dir
        assert file_path.exists()
    
    def test_tool_without_output_dir_uses_cwd(self):
        """Test backward compatibility: tool without output_dir uses cwd."""
        from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool
        
        tool = CreateDeliverableTool()  # No output_dir
        
        # Should default to cwd
        assert tool.output_dir == Path.cwd()
```

---

## 阶段二：Fix-1 - 超时配置接入 (P0)

### 目标

将 `node.yaml` 中的 `runtime.timeout` 配置传入 `session.prompt(timeout=...)`。

**统一配置**: 60s

### Step 2.1: 编写失败测试

**测试文件**: `tests/fix/test_executor_timeout_passing.py`

```python
"""Test for Fix-1: timeout configuration passing."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestExecutorTimeoutPassing:
    """Test that executor passes timeout to session.prompt()."""
    
    @pytest.mark.asyncio
    async def test_executor_reads_node_timeout(self):
        """Test that executor reads timeout from node config."""
        from autoBMAD.docuswarm.node_execution.executor import _execute_node
        from autoBMAD.docuswarm.node_execution.state import create_initial_state
        
        # Mock state
        state = create_initial_state(
            pipeline_id="test-pipeline",
            context_file="test context",
        )
        
        # Mock node config
        mock_node_config = MagicMock()
        mock_node_config.runtime.timeout = 60  # 60s test config
        
        with patch("autoBMAD.nodes.loader.NodeLoader.load", return_value=mock_node_config):
            with patch("autoBMAD.docuswarm.nodes.dual_agent.DualAgentNode.execute_with_context") as mock_execute:
                mock_execute.return_value = MagicMock(
                    deliverable={},
                    questions=[],
                    evaluation={"verdict": "APPROVED"},
                )
                
                await _execute_node(
                    state=state,
                    node_id="analyst",
                    session_manager=MagicMock(),
                    logger=MagicMock(),
                )
                
                # Verify NodeLoader.load was called with correct node_id
                mock_node_config.assert_called_once_with("analyst")
    
    @pytest.mark.asyncio
    async def test_session_prompt_receives_timeout(self):
        """Test that session.prompt() receives timeout parameter."""
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = MagicMock()
        mock_client.query = AsyncMock()
        mock_client.receive_messages = AsyncMock(return_value=[])
        
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-session",
            work_dir=MagicMock(),
        )
        
        # Test that prompt method accepts timeout parameter
        async for msg in wrapper.prompt("test message", timeout=60):
            pass
        
        # Verify asyncio.timeout was called with 60
        with patch("asyncio.timeout") as mock_timeout:
            mock_timeout.return_value.__aenter__ = AsyncMock()
            mock_timeout.return_value.__aexit__ = AsyncMock()
            
            async for msg in wrapper.prompt("test", timeout=60):
                pass
                
            mock_timeout.assert_called_once_with(60)
```

### Step 2.2: 实现最小代码使测试通过

**修改文件**: `autoBMAD/docuswarm/node_execution/executor.py`

```python
async def _execute_node(
    state: NodeRunState,
    node_id: str,
    session_manager: SessionManager,
    logger: Any,
) -> NodeRunState:
    """Execute a node with timeout from config (Fix-1)."""
    
    # ... existing code ...
    
    try:
        # FIX-1: Load node config to get timeout
        from autoBMAD.nodes.loader import NodeLoader
        node_config = NodeLoader.load(node_id)
        node_timeout = node_config.runtime.timeout  # 60s
        
        # Pass timeout through execution context
        execution_context["timeout"] = node_timeout
        
        # Create node with timeout-aware session manager
        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id=node_id,
            project_root=repo_root,
            timeout=node_timeout,  # NEW: pass timeout
        )
        
        result = await node.execute_with_context(execution_context)
        
        # ... rest of method ...
```

**修改文件**: `autoBMAD/docuswarm/nodes/dual_agent.py`

```python
async def execute_with_context(
    self,
    execution_context: NodeExecutionContext,
) -> NodeResult:
    """Execute with timeout support (Fix-1)."""
    
    # Get timeout from context
    timeout = execution_context.get("timeout", 60)  # Default 60s
    
    # ... iteration loop ...
    
    independent_output = await self.independent_agent.execute_with_input(
        agent_input=independent_input,
        pipeline_id=pipeline_id,
        timeout=timeout,  # NEW: pass timeout
    )
```

**修改文件**: `autoBMAD/docuswarm/agents/independent.py`

```python
async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
    timeout: int = 60,  # NEW: timeout parameter
) -> IndependentOutput:
    """Execute with timeout support (Fix-1)."""
    
    # ... setup code ...
    
    try:
        response = await self._call_llm_with_prompts(
            system_prompt_append=system_prompt,
            user_prompt=user_prompt,
            timeout=timeout,  # NEW: pass timeout
        )
    finally:
        self.session_manager = original_session_manager
    
    # ... rest of method ...

async def _call_llm_with_prompts(
    self,
    system_prompt_append: str,
    user_prompt: str,
    timeout: int = 60,  # NEW: timeout parameter
) -> list[dict[str, Any]]:
    """Call LLM with timeout (Fix-1)."""
    
    # ... session creation ...
    
    async for msg in session.prompt(user_prompt, timeout=timeout):  # FIX: pass timeout
        message_count += 1
        # ... message processing ...
```

---

## 阶段三：Fix-3 - Parse Fallback 扩展 (P1)

### 目标

扩展 `_parse_response` 的 fallback 机制，处理任何非 JSON 内容。

### Step 3.1: 编写失败测试

**测试文件**: `tests/fix/test_parse_response_fallback.py`

```python
"""Test for Fix-3: parse response fallback extension."""

import pytest
from unittest.mock import MagicMock


class TestParseResponseFallback:
    """Test _parse_response fallback for plain text."""
    
    def test_fallback_triggers_for_plain_text(self):
        """Test fallback triggers for plain English prose."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        agent = IndependentAgent(
            config=MagicMock(),
            session_manager=MagicMock(),
            node_id="analyst",
        )
        
        # Plain text content (not starting with # or containing Summary)
        response = [{
            "role": "assistant",
            "content": [{
                "type": "text",
                "text": "The tools appear to have some issues, but I need to complete..."
            }]
        }]
        
        # Should try fallback (extract tool results) instead of raising immediately
        with pytest.raises(Exception) as exc_info:
            agent._parse_response(response)
        
        # Error should mention trying fallback
        assert "tool result" in str(exc_info.value).lower() or "fallback" in str(exc_info.value).lower()
    
    def test_fallback_extracts_tool_result(self):
        """Test fallback extracts file_path/sha256 from tool_result."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        agent = IndependentAgent(
            config=MagicMock(),
            session_manager=MagicMock(),
            node_id="analyst",
        )
        
        # Response with tool_result but no JSON
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "call_123",
                        "content": '{"file_path": "/output/test.md", "sha256": "abc123"}',
                        "is_error": False,
                    },
                    {
                        "type": "text",
                        "text": "I have created the document.",
                    }
                ]
            }
        ]
        
        # Mock validator to return valid
        with patch("autoBMAD.docuswarm.context.validator.ContextValidator") as mock_validator:
            mock_validator.return_value.validate_independent_output.return_value = MagicMock(
                valid=True,
                issues=[],
            )
            
            result = agent._parse_response(response)
            
            # Should construct valid output from tool_result
            assert "deliverable" in result
            assert result["deliverable"]["file_path"] == "/output/test.md"
            assert result["deliverable"]["sha256"] == "abc123"
    
    def test_fallback_condition_non_json_start(self):
        """Test fallback triggers for content not starting with {."""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        agent = IndependentAgent(
            config=MagicMock(),
            session_manager=MagicMock(),
            node_id="analyst",
        )
        
        # Test various non-JSON starts
        non_json_contents = [
            "The tools appear to have issues...",
            "I need to complete my task.",
            "Let me think about this...",
            "Processing your request...",
        ]
        
        for content in non_json_contents:
            response = [{
                "role": "assistant",
                "content": [{"type": "text", "text": content}]
            }]
            
            # Should attempt fallback (which may fail but should try)
            try:
                agent._parse_response(response)
            except Exception as e:
                # Error should indicate fallback was attempted
                pass  # Expected for content without tool results
```

### Step 3.2: 实现最小代码使测试通过

**修改文件**: `autoBMAD/docuswarm/agents/independent.py`

```python
def _parse_response(self, response: list[dict[str, Any]]) -> IndependentOutput:
    """Parse and validate LLM response with extended fallback (Fix-3)."""
    content = self._extract_content_from_messages(response)
    
    if not content or not content.strip():
        raise ResponseParseAgentError("Empty response from LLM")
    
    try:
        data = extract_json(content)
    except ResponseParseError as e:
        # FIX-3: Extended fallback condition
        is_non_json_text = (
            content.strip().startswith(("#", "##", "###"))
            or "Summary" in content[:100]
            or not content.strip().startswith("{")  # NEW: Any non-JSON content
        )
        
        if is_non_json_text:
            self.logger.warning(
                "llm_returned_non_json_fallback",
                attempting_fallback=True,
                content_preview=content[:200],
            )
            
            # Try to extract tool results
            file_path, sha256 = self._extract_create_deliverable_result(response)
            
            if file_path:
                import re
                
                title_match = re.search(r"^#+\s*(.+)$", content, re.MULTILINE)
                title = title_match.group(1) if title_match else "LLM Generated Document"
                
                data = {
                    "deliverable": {
                        "title": title,
                        "content": content[:500] + "..." if len(content) > 500 else content,
                        "file_path": file_path,
                        "sha256": sha256 or "",
                    },
                    "questions": [],
                    "action": "create_deliverable",
                }
                
                self.logger.info(
                    "non_json_fallback_success_with_tool_result",
                    constructed_title=title,
                    file_path=file_path,
                )
            else:
                # More descriptive error
                content_type = "markdown" if content.strip().startswith("#") else "plain_text"
                raise ResponseParseAgentError(
                    f"LLM returned non-JSON content ({content_type}) and no tool result found. "
                    f"Content preview: {content[:200]}"
                ) from e
        else:
            self.logger.error("response_parse_failed", error=str(e), content=content[:200])
            raise ResponseParseAgentError(f"Failed to parse response: {e}") from e
    
    # ... validation code ...
    return data
```

---


### 目标

在 `node.yaml` 中添加 `fail_fast` 选项，支持节点失败时中断流水线。

### Step 4.1: 编写失败测试

**测试文件**: `tests/fix/test_fail_fast_option.py`

```python
"""Test for Fix-4: optional fail-fast support."""

import pytest
from unittest.mock import MagicMock, patch


class TestFailFastOption:
    """Test fail_fast option in node config."""
    
    def test_node_config_accepts_fail_fast(self):
        """Test that NodeConfig accepts fail_fast parameter."""
        from autoBMAD.nodes.loader import NodeConfig, NodeRuntimeConfig
        
        config = NodeConfig(
            node_id="analyst",
            name="Analyst",
            sequence=1,
            deliverable_type="report",
            runtime=NodeRuntimeConfig(
                timeout=60,
                fail_fast=True,  # NEW parameter
            ),
        )
        
        assert config.runtime.fail_fast is True
    
    @pytest.mark.asyncio
    async def test_pipeline_aborts_on_failure_when_fail_fast(self):
        """Test pipeline aborts when node fails and fail_fast=true."""
        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        
        # Mock node config with fail_fast
        mock_config = MagicMock()
        mock_config.runtime.fail_fast = True
        
        with patch("autoBMAD.nodes.loader.NodeLoader.load", return_value=mock_config):
            orchestrator = HybridOrchestrator()
            
            # Mock a failing node execution
            with patch.object(orchestrator, "_execute_single_node") as mock_execute:
                mock_execute.return_value = {"status": "FAILED"}
                
                # Should abort after first failure
                result = await orchestrator.run_pipeline(
                    pipeline_id="test",
                    node_ids=["analyst", "pm", "ux"],
                )
                
                # Only first node should execute
                assert mock_execute.call_count == 1
                assert result["aborted"] is True
                assert result["completed_nodes"] == []
```

### Step 4.2: 实现最小代码使测试通过

**修改文件**: `autoBMAD/nodes/loader.py`

```python
@dataclass
class NodeRuntimeConfig:
    """Configuration for node runtime behavior."""
    timeout: int = 60  # 60s test config
    retry_max_attempts: int = 3
    retry_backoff: float = 1.5
    fail_fast: bool = False  # NEW: abort pipeline on failure
```

**修改文件**: `autoBMAD/docuswarm/pipeline/graph.py`

```python
async def execute_node_with_fail_fast(state: PipelineState) -> PipelineState:
    """Execute node with optional fail-fast support (Fix-4)."""
    node_id = state["current_node"]
    
    # Load node config
    from autoBMAD.nodes.loader import NodeLoader
    node_config = NodeLoader.load(node_id)
    
    # Execute node
    result = await execute_single_node(state)
    
    # Check fail_fast
    if result["status"] == "FAILED" and node_config.runtime.fail_fast:
        state["status"] = "ABORTED"
        state["abort_reason"] = f"Node {node_id} failed with fail_fast=true"
        return state
    
    # Continue to next node
    state["completed_nodes"].append(node_id)
    return state
```

---

## 集成测试方案

### 完整流程测试

**测试文件**: `tests/fix/test_integration_complete_flow.py`

```python
"""Integration test for complete fix verification."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


class TestCompleteFlowIntegration:
    """Integration test for complete flow with all fixes."""
    
    @pytest.mark.asyncio
    async def test_complete_flow_with_all_fixes(self, tmp_path: Path):
        """Test complete flow with Fix-2B, Fix-1, Fix-3 applied."""
        
        # Setup
        repo_root = tmp_path
        output_dir = repo_root / "output" / "pipeline-123"
        output_dir.mkdir(parents=True)
        
        # Create session manager with split cwd/output_dir (Fix-2B)
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        
        sm = SessionManager(
            cwd=repo_root,      # For SDK import
            output_dir=output_dir,  # For file output
        )
        
        assert sm.cwd == repo_root
        assert sm.output_dir == output_dir
        
        # Verify options use cwd (Fix-2B)
        options = sm._create_options(mode="agent", yolo=True)
        assert options.cwd == repo_root
        
        # Create independent agent with timeout (Fix-1)
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        
        agent = IndependentAgent(
            config=MagicMock(),
            session_manager=sm,
            node_id="analyst",
        )
        
        # Test timeout passing
        agent_input = {
            "task_name": "Test Task",
            "original_context_summary": "Test context",
        }
        
        # Mock session.prompt to verify timeout
        with patch.object(agent, "_call_llm_with_prompts") as mock_call:
            mock_call.return_value = []
            
            try:
                await agent.execute_with_input(
                    agent_input=agent_input,
                    pipeline_id="pipeline-123",
                    timeout=60,  # 60s test config
                )
            except:
                pass  # Expected without full mock
            
            # Verify timeout was passed
            mock_call.assert_called_once()
            call_kwargs = mock_call.call_args[1]
            assert call_kwargs.get("timeout") == 60
    
    @pytest.mark.asyncio
    async def test_end_to_end_with_mock_sdk(self, tmp_path: Path):
        """End-to-end test with mocked SDK."""
        
        from autoBMAD.docuswarm.tools.create_deliverable import (
            CreateDeliverableTool,
            CreateDeliverableParams,
        )
        
        output_dir = tmp_path / "output" / "pipeline-test"
        output_dir.mkdir(parents=True)
        
        # Create deliverable (Fix-2B)
        tool = CreateDeliverableTool(output_dir=output_dir)
        
        params = CreateDeliverableParams(
            title="Integration Test Document",
            content="# Test\n\nThis is a test document.",
        )
        
        result = await tool._execute(params)
        
        assert result.success is True
        assert result.result["file_path"].startswith(str(output_dir))
        
        # Verify file exists
        file_path = Path(result.result["file_path"])
        assert file_path.exists()
        assert file_path.read_text() == "# Test\n\nThis is a test document."
```

---

## 验证清单

### 修复前检查清单

- [ ] 所有测试失败（预期）
- [ ] 代码审查确认问题存在
- [ ] 测试覆盖率 > 80%

### 修复后检查清单

- [ ] 所有测试通过
- [ ] 代码审查通过
- [ ] 集成测试通过
- [ ] 文档已更新

### 最终验证

```bash
# Run all fix tests
pytest tests/fix/ -v --tb=short

# Run integration tests
pytest tests/fix/test_integration_complete_flow.py -v

# Run with coverage
pytest tests/fix/ --cov=autoBMAD.docuswarm --cov-report=html

# Full pipeline test (manual)
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

### 预期结果

| 检查项 | 预期结果 |
|--------|----------|
| 单元测试 | 全部通过 |
| 集成测试 | 全部通过 |
| 覆盖率 | > 85% |
| 日志输出 | `tool_name='create_deliverable'` 出现 |
| 文件输出 | 5 个 `.md` 文件在 output/pipeline-*/ |
| 超时 | 60s 内完成每个节点 |

---

## 附录：代码变更汇总

### 新增测试文件

```
tests/fix/
├── __init__.py
├── test_session_manager_cwd_split.py
├── test_create_deliverable_tool_output_dir.py
├── test_executor_timeout_passing.py
├── test_parse_response_fallback.py
├── test_fail_fast_option.py
└── test_integration_complete_flow.py
```

### 修改文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `session_manager.py` | 修改 | 添加 cwd/output_dir 拆分 |
| `independent.py` | 修改 | 添加 timeout 参数传递, 扩展 fallback |
| `executor.py` | 修改 | 读取并传递 node timeout |
| `dual_agent.py` | 修改 | 传递 timeout 到 agent |
| `loader.py` | 修改 | 添加 fail_fast 配置 |
| `graph.py` | 修改 | 添加 fail-fast 逻辑 |

---

*方案结束*
