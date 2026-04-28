# DocuSwarm Pipeline 超时与 MISSING_FILE_PATH 错误 - 测试驱动修复方案

**基于**: [pipeline-timeout-root-cause-analysis.md](../research/pipeline-timeout-root-cause-analysis.md)  
**创建日期**: 2026-04-06  
**状态**: 待实施

---

## 一、方案概述

本方案采用**测试驱动开发 (TDD)** 方法，针对根因分析报告中的 6 个修复建议，按优先级顺序实施。每个修复包含：

1. **失败测试** - 先编写验证修复需求的测试（预期失败）
2. **实现修复** - 使测试通过的最小代码变更
3. **回归测试** - 确保不破坏现有功能
4. **集成验证** - 端到端验证

---

## 二、修复优先级矩阵

| 修复项 | 优先级 | 严重程度 | 测试类型 | 依赖项 |
|--------|--------|----------|----------|--------|
| Fix-1: contract_builder JSON 示例 | P0 | CRITICAL | 单元测试 | 无 |
| Fix-2: markdown_fallback 分支 | P0 | CRITICAL | 单元测试 + 集成测试 | Fix-1 |
| Fix-6: system_prompt 路径对齐 | P1 | HIGH | 单元测试 | Fix-1 |
| Fix-3: 超时诊断日志 | P1 | HIGH | 单元测试 (mock) | 无 |
| Fix-4: CreateDeliverableTool output_dir | P1 | HIGH | 集成测试 | 无 |
| Fix-5: 状态保存与重试优化 | P2 | MEDIUM | 集成测试 + E2E测试 | Fix-2, Fix-3 |

---

## 三、Fix-1: contract_builder._build_instructions_section() 修复

### 3.1 问题描述

`contract_builder._build_instructions_section()` 的 JSON 示例缺少 `file_path` 和 `sha256` 字段，导致 LLM 不知道需要在响应中包含这些必填字段。

### 3.2 测试先行

```python
# tests/unit/prompts/test_contract_builder_fix1.py
"""Fix-1 测试: 验证 contract_builder JSON 示例包含 file_path 和 sha256."""

import pytest
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder


class TestFix1ContractBuilderJSONExample:
    """Test Fix-1: contract_builder._build_instructions_section() 修复."""

    def test_instructions_section_contains_file_path_example(self):
        """JSON 示例必须包含 file_path 字段示例."""
        builder = NodePromptContractBuilder()
        instructions = builder._build_instructions_section()
        
        assert '"file_path"' in instructions, (
            "FAIL: JSON 示例中缺少 'file_path' 字段\n"
            "LLM 将不知道需要在响应中包含 file_path，导致 MISSING_FILE_PATH 错误"
        )
    
    def test_instructions_section_contains_sha256_example(self):
        """JSON 示例必须包含 sha256 字段示例."""
        builder = NodePromptContractBuilder()
        instructions = builder._build_instructions_section()
        
        assert '"sha256"' in instructions, (
            "FAIL: JSON 示例中缺少 'sha256' 字段\n"
            "验证器要求 sha256，LLM 若不知需包含此字段会导致验证失败"
        )
    
    def test_instructions_section_contains_important_note(self):
        """必须包含 IMPORTANT 提示，强调 file_path 和 sha256 的来源."""
        builder = NodePromptContractBuilder()
        instructions = builder._build_instructions_section()
        
        assert "IMPORTANT" in instructions, (
            "FAIL: 缺少 IMPORTANT 提示\n"
            "需要明确告知 LLM 必须从 create_deliverable 工具输出中获取 file_path 和 sha256"
        )
    
    def test_file_path_example_shows_tool_source(self):
        """file_path 示例应表明来自工具返回."""
        builder = NodePromptContractBuilder()
        instructions = builder._build_instructions_section()
        
        # 验证示例值暗示来自工具返回
        assert any(
            hint in instructions.lower() 
            for hint in ["tool", "returned", "create_deliverable"]
        ), (
            "FAIL: file_path 示例未表明来自工具返回\n"
            "示例应类似: 'path/returned/by/create_deliverable/tool.md'"
        )
    
    def test_instructions_section_contains_execution_workflow(self):
        """必须包含执行工作流说明."""
        builder = NodePromptContractBuilder()
        instructions = builder._build_instructions_section()
        
        assert "Execution Workflow" in instructions, (
            "FAIL: 缺少 Execution Workflow 说明\n"
            "需要明确告知 LLM: 1)调用工具 2)获取返回 3)构造 JSON 响应"
        )
    
    def test_complete_json_example_is_valid_json(self):
        """JSON 示例必须是有效的 JSON 格式."""
        import json
        import re
        
        builder = NodePromptContractBuilder()
        instructions = builder._build_instructions_section()
        
        # 提取 JSON 代码块
        json_match = re.search(
            r'```json\s*(\{[\s\S]*?\})\s*```', 
            instructions
        )
        assert json_match, "FAIL: 未找到 JSON 代码块"
        
        json_str = json_match.group(1)
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"FAIL: JSON 示例格式无效: {e}")
        
        # 验证结构
        assert "deliverable" in parsed, "FAIL: JSON 缺少 deliverable 字段"
        assert "file_path" in parsed["deliverable"], "FAIL: deliverable 缺少 file_path"
        assert "sha256" in parsed["deliverable"], "FAIL: deliverable 缺少 sha256"
        assert "questions" in parsed, "FAIL: JSON 缺少 questions 字段"
        assert "action" in parsed, "FAIL: JSON 缺少 action 字段"
```

### 3.3 实现修复

**文件**: `autoBMAD/docuswarm/prompts/contract_builder.py`  
**方法**: `_build_instructions_section()` (第250-291行)

```python
def _build_instructions_section(self) -> str:
    """构建固定指令章节."""
    return """## Agent Instructions

You are an Independent Agent that creates deliverables and generates questions.

## Execution Workflow

1. **Create Deliverable**: Use the 'create_deliverable' tool to save your document
   - The tool accepts: title (string) and content (Markdown string)
   - This writes the deliverable to a .md file
   - The tool returns metadata including: file_path, sha256, word_count, section_index

2. **Generate Questions**: Formulate follow-up questions with priorities

3. **Return Execution Report**: After using tools, you MUST return a JSON response

## CRITICAL: Output Format

After executing tools, you MUST respond with ONLY this exact JSON structure:

```json
{
  "deliverable": {
    "title": "Brief title of what you created",
    "content": "Brief summary (1-2 sentences, NOT the full document)",
    "file_path": "path/returned/by/create_deliverable/tool.md",
    "sha256": "hash_returned_by_create_deliverable_tool"
  },
  "questions": [
    {
      "question": "Question text?",
      "priority": "blocking | clarifying | optional",
      "context": "Context or rationale for this question"
    }
  ],
  "action": "create_deliverable"
}
```

**IMPORTANT**:
- The entire response must be valid JSON parseable by json.loads()
- Do NOT include markdown formatting outside the JSON
- You MUST include "file_path" and "sha256" from the create_deliverable tool output

**Question Priorities**:
- **blocking**: Must be answered before proceeding
- **clarifying**: Help refine the deliverable
- **optional**: Nice-to-have for future consideration
"""
```

### 3.4 回归测试

```python
# tests/unit/prompts/test_contract_builder_regression.py
"""Fix-1 回归测试: 确保修复不破坏现有功能."""

import pytest
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder


class TestFix1Regression:
    """Fix-1 回归测试."""

    def test_render_independent_system_prompt_structure_preserved(self):
        """验证整体 prompt 结构未被破坏."""
        builder = NodePromptContractBuilder()
        
        # Mock 输入
        context = {
            "node_info": {"name": "test_node", "type": "analyst"},
            "context_variables": {"project": "test"},
            "artifacts": [],
        }
        
        contract = builder.build_independent_contract(context)
        prompt = builder.render_independent_system_prompt(contract)
        
        # 验证关键章节仍然存在
        assert "## Agent Instructions" in prompt
        assert "## Execution Workflow" in prompt  # 新增章节
        assert "## CRITICAL: Output Format" in prompt
    
    def test_render_independent_system_prompt_contains_variables(self):
        """验证变量替换功能正常."""
        builder = NodePromptContractBuilder()
        
        context = {
            "node_info": {"name": "analyst", "type": "analyst"},
            "context_variables": {"project": "bubble-sort"},
            "artifacts": [{"title": "context", "path": "/path/to/context.md"}],
        }
        
        contract = builder.build_independent_contract(context)
        prompt = builder.render_independent_system_prompt(contract)
        
        assert "bubble-sort" in prompt
        assert "analyst" in prompt
```

---

## 四、Fix-2: markdown_fallback 分支修复

### 4.1 问题描述

超时后 `_call_llm_with_prompts` 返回 partial messages，`_parse_response` 触发 `markdown_fallback`，但构建的 dict 缺少 `file_path` 和 `sha256`，导致验证失败。

### 4.2 测试先行

```python
# tests/unit/agents/test_independent_agent_fix2.py
"""Fix-2 测试: 验证 markdown_fallback 能正确提取工具返回的 file_path 和 sha256."""

import json
import pytest
from unittest.mock import MagicMock, patch

from autoBMAD.docuswarm.agents.independent import IndependentAgent


class TestFix2ExtractCreateDeliverableResult:
    """Test Fix-2: _extract_create_deliverable_result 方法."""

    @pytest.fixture
    def agent(self):
        return IndependentAgent(
            name="test_agent",
            system_prompt="test prompt",
        )

    def test_extract_from_json_string_content_case_a(self, agent):
        """Case A: tool_result.content 是 JSON 字符串 (实际生产格式)."""
        tool_output = {
            "file_path": "/output/test.md",
            "sha256": "abc123",
            "word_count": 100,
        }
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool_123",
                        "content": json.dumps(tool_output),  # JSON 字符串
                        "is_error": False,
                    }
                ],
            }
        ]
        
        file_path, sha256 = agent._extract_create_deliverable_result(messages)
        
        assert file_path == "/output/test.md", f"FAIL: 期望 '/output/test.md', 得到 '{file_path}'"
        assert sha256 == "abc123", f"FAIL: 期望 'abc123', 得到 '{sha256}'"

    def test_extract_from_dict_content_case_b(self, agent):
        """Case B: tool_result.content 是 dict (假设已解析)."""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool_123",
                        "content": {  # dict 格式
                            "file_path": "/output/test.md",
                            "sha256": "abc123",
                        },
                        "is_error": False,
                    }
                ],
            }
        ]
        
        file_path, sha256 = agent._extract_create_deliverable_result(messages)
        
        assert file_path == "/output/test.md"
        assert sha256 == "abc123"

    def test_extract_skips_error_results(self, agent):
        """跳过 is_error=True 的 tool_result."""
        messages = [
            {
                "content": [
                    {
                        "type": "tool_result",
                        "content": json.dumps({"error": "failed"}),
                        "is_error": True,  # 错误结果
                    },
                    {
                        "type": "tool_result",
                        "content": json.dumps({
                            "file_path": "/output/success.md",
                            "sha256": "success123",
                        }),
                        "is_error": False,
                    },
                ],
            }
        ]
        
        file_path, sha256 = agent._extract_create_deliverable_result(messages)
        
        assert file_path == "/output/success.md"
        assert sha256 == "success123"

    def test_extract_returns_none_when_not_found(self, agent):
        """当没有 tool_result 包含 file_path 时返回 None."""
        messages = [
            {
                "content": [
                    {"type": "text", "text": "some message"},
                ],
            }
        ]
        
        file_path, sha256 = agent._extract_create_deliverable_result(messages)
        
        assert file_path is None
        assert sha256 is None

    def test_extract_handles_invalid_json(self, agent):
        """处理无效的 JSON 字符串."""
        messages = [
            {
                "content": [
                    {
                        "type": "tool_result",
                        "content": "not valid json",
                        "is_error": False,
                    },
                    {
                        "type": "tool_result",
                        "content": json.dumps({
                            "file_path": "/output/valid.md",
                            "sha256": "valid123",
                        }),
                        "is_error": False,
                    },
                ],
            }
        ]
        
        file_path, sha256 = agent._extract_create_deliverable_result(messages)
        
        # 应跳过无效 JSON，使用有效的
        assert file_path == "/output/valid.md"


class TestFix2MarkdownFallbackIntegration:
    """Test Fix-2: markdown_fallback 与 extract 方法集成."""

    @pytest.fixture
    def agent(self):
        return IndependentAgent(
            name="test_agent",
            system_prompt="test prompt",
        )

    def test_markdown_fallback_uses_extracted_tool_result(self, agent):
        """markdown_fallback 应使用从工具返回中提取的 file_path/sha256."""
        tool_output = {
            "file_path": "/output/from_tool.md",
            "sha256": "from_tool_hash",
        }
        messages = [
            {
                "role": "assistant",
                "content": "# Summary\n\nThis is a summary.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": json.dumps(tool_output),
                        "is_error": False,
                    }
                ],
            }
        ]
        
        result = agent._parse_response(messages)
        
        assert result["deliverable"]["file_path"] == "/output/from_tool.md"
        assert result["deliverable"]["sha256"] == "from_tool_hash"
        assert result["action"] == "create_deliverable"

    def test_markdown_fallback_raises_error_when_no_tool_result(self, agent):
        """当没有工具返回且内容看起来像 Markdown 时，应抛出错误."""
        messages = [
            {
                "role": "assistant",
                "content": "# Summary\n\nThis is just markdown without tool call.",
            }
        ]
        
        from autoBMAD.docuswarm.agents.independent import ResponseParseAgentError
        
        with pytest.raises(ResponseParseAgentError) as exc_info:
            agent._parse_response(messages)
        
        assert "create_deliverable" in str(exc_info.value)
        assert "file_path" in str(exc_info.value)

    def test_markdown_fallback_preserves_title_and_content(self, agent):
        """markdown_fallback 应正确提取 title 和 content."""
        messages = [
            {
                "role": "assistant",
                "content": "# Analysis Report\n\nThis is the content of the report.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": json.dumps({
                            "file_path": "/output/report.md",
                            "sha256": "report_hash",
                        }),
                        "is_error": False,
                    }
                ],
            }
        ]
        
        result = agent._parse_response(messages)
        
        assert result["deliverable"]["title"] == "Analysis Report"
        assert "This is the content" in result["deliverable"]["content"]
```

### 4.3 实现修复

**文件**: `autoBMAD/docuswarm/agents/independent.py`

```python
class IndependentAgent:
    # ... 现有代码 ...

    def _extract_create_deliverable_result(
        self, messages: list[dict[str, Any]]
    ) -> tuple[str | None, str | None]:
        """从 messages 中提取 create_deliverable 工具的返回结果.

        数据链路验证 (来自 tools/timeout_root_cause_analyzer.py):
          sdk_adapter.adapt_to_claude() 将 metadata dict 序列化为 JSON字符串存入 content。
          因此 tool_result["content"] 是字符串，必须先 json.loads() 再检查 dict。

        Returns:
            (file_path, sha256) 元组，未找到时返回 (None, None)
        """
        import json as json_module
        
        for msg in messages:
            content_blocks = msg.get("content", [])
            if not isinstance(content_blocks, list):
                continue
                
            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_result":
                    continue
                if block.get("is_error", False):
                    continue  # 跳过错误结果

                tool_output = block.get("content", {})

                # 关键修复: content 是 JSON字符串 (sdk_adapter 序列化结果)
                # 必须先 json.loads() 才能得到 dict
                if isinstance(tool_output, str):
                    try:
                        tool_output = json_module.loads(tool_output)
                    except json_module.JSONDecodeError:
                        continue

                if isinstance(tool_output, dict) and "file_path" in tool_output:
                    return (
                        str(tool_output["file_path"]),
                        str(tool_output.get("sha256", "")),
                    )
        return None, None

    def _parse_response(self, response: list[dict[str, Any]]) -> dict[str, Any]:
        """解析 LLM 响应，支持 JSON 和 Markdown fallback."""
        # ... 现有代码 ...
        
        # 提取文本内容
        content = self._extract_content_from_messages(response)
        
        # 尝试解析 JSON
        data = extract_json(content)
        if data is not None:
            return data
        
        # Markdown fallback
        if content.strip().startswith(("#", "##", "###")) or "Summary" in content[:100]:
            self.logger.warning(
                "llm_returned_markdown_fallback",
                attempting_fallback=True,
                content_preview=content[:200],
            )

            # Fix-2: 先从工具调用历史中提取 file_path/sha256
            file_path, sha256 = self._extract_create_deliverable_result(response)

            if file_path:
                # 工具已成功执行，补全 LLM 遗漏的字段
                import re as re_module
                title_match = re_module.search(r"^#+\s*(.+)$", content, re_module.MULTILINE)
                title = title_match.group(1) if title_match else "LLM Generated Document"
                data = {
                    "deliverable": {
                        "title": title,
                        "content": content[:500] + "..." if len(content) > 500 else content,
                        "file_path": file_path,   # ✅ 来自工具真实返回
                        "sha256": sha256 or "",   # ✅ 来自工具真实返回
                    },
                    "questions": [],
                    "action": "create_deliverable",
                }
                return data
            else:
                # 工具未执行或结果丢失，拒绝处理，触发重试
                raise ResponseParseAgentError(
                    "LLM returned Markdown instead of JSON, and no create_deliverable "
                    "tool result found in messages. LLM must call create_deliverable "
                    f"tool and include file_path in JSON response. Preview: {content[:200]}"
                )
        
        # ... 剩余代码 ...
```

### 4.4 集成测试

```python
# tests/integration/agents/test_independent_agent_timeout_scenario.py
"""Fix-2 集成测试: 模拟超时场景验证修复效果."""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from autoBMAD.docuswarm.agents.independent import IndependentAgent, LLMCallError


class TestTimeoutScenarioWithPartialMessages:
    """模拟超时后返回 partial messages 的场景."""

    @pytest.fixture
    def agent(self):
        return IndependentAgent(
            name="test_agent",
            system_prompt="test",
        )

    @pytest.fixture
    def partial_messages_with_tool_result(self):
        """模拟超时前已收到的 partial messages（含工具返回）."""
        return [
            {"role": "assistant", "content": "I'll create the deliverable."},
            {"role": "user", "content": [{"type": "text", "text": "OK"}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool_001",
                        "content": json.dumps({
                            "file_path": "/output/pipeline-xxx/analyst-report.md",
                            "sha256": "a1b2c3d4e5f6",
                            "word_count": 1500,
                        }),
                        "is_error": False,
                    }
                ],
            },
            {"role": "assistant", "content": "# Analysis Report\n\nSummary of findings..."},
        ]

    async def mock_llm_with_timeout(self, *args, **kwargs):
        """模拟 LLM 调用超时."""
        raise asyncio.TimeoutError("Simulated timeout")

    @pytest.mark.asyncio
    async def test_timeout_with_tool_result_extracts_file_path(
        self, agent, partial_messages_with_tool_result
    ):
        """超时但有工具返回时，应正确提取 file_path 和 sha256."""
        
        # Mock _call_llm 超时后返回 partial messages
        with patch.object(agent, '_call_llm', side_effect=partial_messages_with_tool_result):
            # 模拟 _call_llm_with_prompts 的行为
            result = await agent._call_llm_with_prompts(
                system_prompt_append="test",
                user_prompt="test",
            )
        
        # 解析结果
        parsed = agent._parse_response(result)
        
        # 验证从工具返回中提取了正确的路径
        assert parsed["deliverable"]["file_path"] == "/output/pipeline-xxx/analyst-report.md"
        assert parsed["deliverable"]["sha256"] == "a1b2c3d4e5f6"

    @pytest.mark.asyncio
    async def test_timeout_without_tool_result_raises_error(self, agent):
        """超时且无工具返回时，应抛出错误触发重试."""
        messages_without_tool = [
            {"role": "assistant", "content": "# Just a heading\n\nSome content."},
        ]
        
        with patch.object(agent, '_call_llm', return_value=messages_without_tool):
            result = await agent._call_llm_with_prompts(
                system_prompt_append="test",
                user_prompt="test",
            )
        
        from autoBMAD.docuswarm.agents.independent import ResponseParseAgentError
        
        with pytest.raises(ResponseParseAgentError) as exc_info:
            agent._parse_response(result)
        
        assert "create_deliverable" in str(exc_info.value)
```

---

## 五、Fix-3: 超时诊断日志修复

### 5.1 问题描述

`ClaudeSessionWrapper.prompt()` 的超时日志缺少 `messages_received_before_timeout` 计数，导致诊断困难。

### 5.2 测试先行

```python
# tests/unit/llm/test_session_manager_fix3.py
"""Fix-3 测试: 验证超时日志包含 messages_received 计数."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper, LLMError


class TestFix3TimeoutLogging:
    """Test Fix-3: 超时诊断日志增强."""

    @pytest.fixture
    def mock_client(self):
        """创建模拟的 LLM 客户端."""
        client = MagicMock()
        client.query = AsyncMock()
        client.receive_messages = AsyncMock()
        return client

    @pytest.fixture
    def session(self, mock_client):
        return ClaudeSessionWrapper(
            client=mock_client,
            session_id="test-session",
            logger=MagicMock(),
        )

    @pytest.mark.asyncio
    async def test_timeout_log_contains_messages_received_count(self, session, mock_client):
        """超时日志必须包含 messages_received_before_timeout 字段."""
        
        # 模拟 receive_messages 产生 5 条消息后超时
        async def generate_messages():
            for i in range(5):
                yield {"type": "content_block_delta", "index": i}
            # 第6条消息前超时
            raise asyncio.TimeoutError("Simulated timeout")
        
        mock_client.receive_messages = generate_messages
        
        with pytest.raises(LLMError) as exc_info:
            async for msg in session.prompt("test message", timeout=1):
                pass
        
        # 验证日志调用
        error_calls = [
            call for call in session._logger.error.call_args_list
            if call.kwargs.get("event") == "prompt_timeout" or 
               (call.args and call.args[0] == "prompt_timeout")
        ]
        
        assert len(error_calls) > 0, "未找到 prompt_timeout 日志"
        
        # 检查日志参数
        log_kwargs = error_calls[0].kwargs if error_calls[0].kwargs else error_calls[0].args[1]
        assert "messages_received_before_timeout" in log_kwargs, (
            "FAIL: 超时日志缺少 messages_received_before_timeout 字段"
        )
        assert log_kwargs["messages_received_before_timeout"] == 5, (
            f"FAIL: 期望收到 5 条消息，日志显示 {log_kwargs['messages_received_before_timeout']}"
        )

    @pytest.mark.asyncio
    async def test_timeout_log_contains_message_length(self, session, mock_client):
        """超时日志必须包含 message_length 字段."""
        
        async def generate_messages():
            yield {"type": "test"}
            raise asyncio.TimeoutError()
        
        mock_client.receive_messages = generate_messages
        
        test_message = "x" * 1000  # 1000 字符的消息
        
        with pytest.raises(LLMError):
            async for msg in session.prompt(test_message, timeout=1):
                pass
        
        error_calls = [
            call for call in session._logger.error.call_args_list
            if call.args and call.args[0] == "prompt_timeout"
        ]
        
        assert len(error_calls) > 0
        log_kwargs = error_calls[0].kwargs
        assert "message_length" in log_kwargs
        assert log_kwargs["message_length"] == 1000

    @pytest.mark.asyncio
    async def test_normal_completion_logs_no_error(self, session, mock_client):
        """正常完成时不应记录超时错误."""
        
        async def generate_messages():
            yield {"type": "content_block_delta", "delta": {"text": "Hello"}}
            yield {"type": "message_stop"}
        
        mock_client.receive_messages = generate_messages
        
        messages = []
        async for msg in session.prompt("test", timeout=10):
            messages.append(msg)
        
        # 验证没有超时错误日志
        timeout_error_calls = [
            call for call in session._logger.error.call_args_list
            if call.args and call.args[0] == "prompt_timeout"
        ]
        
        assert len(timeout_error_calls) == 0, "正常完成不应记录超时错误"
```

### 5.3 实现修复

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`  
**方法**: `ClaudeSessionWrapper.prompt()` (第794-800行附近)

```python
async def prompt(
    self,
    message: str,
    timeout: int | None = None,
) -> AsyncIterator[Any]:
    effective_timeout = timeout if timeout is not None else self.DEFAULT_PROMPT_TIMEOUT

    try:
        await self._client.query(message)
    except Exception as e:
        self._logger.error("query_failed", error=str(e))
        raise LLMError(f"Failed to send query: {e}") from e

    messages_received = 0  # ← Fix-3: 新增计数器
    try:
        async with asyncio.timeout(effective_timeout):
            async for msg in self._client.receive_messages():
                messages_received += 1  # ← Fix-3: 计数
                yield msg
    except TimeoutError as e:
        self._logger.error(
            "prompt_timeout",
            timeout_seconds=effective_timeout,
            message_length=len(message),
            messages_received_before_timeout=messages_received,  # ← Fix-3: 新增
        )
        raise LLMError(f"Session prompt timed out after {effective_timeout} seconds") from e
```

---

## 六、Fix-4: CreateDeliverableTool output_dir 修复

### 6.1 问题描述

`CreateDeliverableTool` 在 `agent_yaml` 中无参数实例化，导致 `output_dir = Path.cwd()`，文件写入当前工作目录而非 pipeline output 目录。

### 6.2 测试先行

```python
# tests/unit/tools/test_create_deliverable_fix4.py
"""Fix-4 测试: 验证 CreateDeliverableTool 使用正确的 output_dir."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool


class TestFix4CreateDeliverableToolOutputDir:
    """Test Fix-4: CreateDeliverableTool output_dir 修复."""

    def test_tool_accepts_output_dir_parameter(self):
        """工具构造函数必须接受 output_dir 参数."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = CreateDeliverableTool(output_dir=Path(tmpdir))
            assert tool.output_dir == Path(tmpdir)

    def test_tool_uses_cwd_as_default(self):
        """无参数时默认使用 cwd（现有行为，需修改）."""
        tool = CreateDeliverableTool()
        assert tool.output_dir == Path.cwd()

    def test_execute_writes_to_correct_output_dir(self):
        """工具执行时应写入指定的 output_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = CreateDeliverableTool(output_dir=Path(tmpdir))
            
            result = tool._execute(
                title="Test Document",
                content="# Test Content",
            )
            
            assert result.success is True
            assert "file_path" in result.result
            
            # 验证文件写入正确目录
            file_path = Path(result.result["file_path"])
            assert file_path.parent == Path(tmpdir), (
                f"FAIL: 文件写入 {file_path.parent}，期望 {tmpdir}"
            )
            assert file_path.exists()

    def test_execute_preserves_relative_paths(self):
        """工具应正确处理相对路径."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = CreateDeliverableTool(output_dir=Path(tmpdir))
            
            result = tool._execute(
                title="Test",
                content="Content",
                filename="subdir/test.md",  # 相对路径
            )
            
            file_path = Path(result.result["file_path"])
            assert file_path.parent.name == "subdir"
            assert file_path.exists()


class TestFix4ToolWrapperIntegration:
    """Fix-4 与 callable_tool_wrapper 集成测试."""

    def test_wrapper_passes_output_dir_to_tool(self):
        """wrapper 应将 work_dir 传递给工具实例."""
        # 这是一个集成测试占位符
        # 实际实现取决于 callable_tool_wrapper.py 的修改
        pytest.skip("需要 callable_tool_wrapper.py 修改后实现")
```

### 6.3 实现方案

由于 `CreateDeliverableTool` 是通过 `agent_yaml` 配置由 SDK 加载的，推荐采用**运行时注入**方案：

**方案 A: 在 `execute_with_input()` 中显式实例化**

```python
# autoBMAD/docuswarm/agents/independent.py

async def execute_with_input(
    self,
    system_prompt_append: str,
    user_prompt: str,
    output_dir: Path,  # ← 新增参数
) -> IndependentAgentOutput:
    """Execute agent with pre-built input (生产路径)."""
    
    # 显式创建工具实例，传入正确的 output_dir
    from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool
    
    tools = [
        CreateDeliverableTool(output_dir=output_dir),  # ← Fix-4: 传入正确的 output_dir
        UpdateContextTool(),
        CreateDocumentSetTool(),
    ]
    
    # 使用这些工具创建 session，而不是依赖 agent_yaml 加载
    session = await self._session_manager.create_session(
        system_prompt=system_prompt,
        tools=tools,  # ← 传递显式工具实例
        # ... 其他参数
    )
    
    # ... 剩余代码
```

**方案 B: 修改 callable_tool_wrapper.py 传递 work_dir**

```python
# autoBMAD/docuswarm/tools/callable_tool_wrapper.py

class CallableToolWrapper(Tool):
    """包装器，将 work_dir 传递给支持 output_dir 参数的工具."""
    
    def __init__(self, tool_class, work_dir: Path | None = None):
        self._tool_class = tool_class
        self._work_dir = work_dir
        
        # 实例化工具，传入 work_dir 如果工具支持
        import inspect
        sig = inspect.signature(tool_class.__init__)
        if 'output_dir' in sig.parameters and work_dir:
            self._tool = tool_class(output_dir=work_dir)
        else:
            self._tool = tool_class()
    
    # ... 代理方法到 self._tool
```

---

## 七、Fix-6: system_prompt 路径对齐

### 7.1 问题描述

`execute()` 内部路径和 `execute_with_input()` 生产路径使用不同的 system prompt 构建方式。

### 7.2 测试先行

```python
# tests/unit/agents/test_prompt_path_alignment_fix6.py
"""Fix-6 测试: 验证两条 system_prompt 路径对齐."""

import pytest
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder
from autoBMAD.docuswarm.agents.independent import IndependentAgent


class TestFix6PromptPathAlignment:
    """Test Fix-6: 两条 system_prompt 路径对齐."""

    def test_contract_builder_matches_format_system_prompt(self):
        """contract_builder 的输出应与 _format_system_prompt 包含相同关键字段."""
        
        # 构建 contract_builder 的输出
        builder = NodePromptContractBuilder()
        context = {
            "node_info": {"name": "test", "type": "analyst"},
            "context_variables": {},
            "artifacts": [],
        }
        contract = builder.build_independent_contract(context)
        contract_prompt = builder.render_independent_system_prompt(contract)
        
        # 关键字段必须都存在
        required_fields = [
            '"file_path"',
            '"sha256"',
            "IMPORTANT",
            "Execution Workflow",
            "create_deliverable",
        ]
        
        for field in required_fields:
            assert field in contract_prompt, (
                f"FAIL: contract_builder 输出缺少 '{field}'\n"
                "两条路径未对齐"
            )

    def test_both_paths_contain_file_path_example(self):
        """两条路径的输出都必须包含 file_path 示例."""
        agent = IndependentAgent(
            name="test",
            system_prompt="test",
        )
        
        # 获取 _format_system_prompt 的输出（通过间接方式）
        format_prompt = agent._format_system_prompt(
            node_type="analyst",
            input_text="test",
            artifacts=[],
        )
        
        # 获取 contract_builder 的输出
        builder = NodePromptContractBuilder()
        contract = builder.build_independent_contract({
            "node_info": {"name": "test", "type": "analyst"},
            "context_variables": {},
            "artifacts": [],
        })
        contract_prompt = builder.render_independent_system_prompt(contract)
        
        # 两者都必须包含 file_path 示例
        assert '"file_path"' in format_prompt, "_format_system_prompt 缺少 file_path"
        assert '"file_path"' in contract_prompt, "contract_builder 缺少 file_path"
        
        # 两者都必须包含 sha256 示例
        assert '"sha256"' in format_prompt, "_format_system_prompt 缺少 sha256"
        assert '"sha256"' in contract_prompt, "contract_builder 缺少 sha256"
```

### 7.3 验证 Fix-1 已覆盖

Fix-6 由 Fix-1 自动覆盖，无需额外代码修改。运行上述测试验证对齐即可。

---

## 八、Fix-5: 状态保存与重试优化（P2）

### 8.1 测试先行

```python
# tests/integration/agents/test_state_persistence_fix5.py
"""Fix-5 测试: 验证超时后的状态保存与重试."""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from autoBMAD.docuswarm.agents.independent import IndependentAgent


class TestFix5StatePersistence:
    """Test Fix-5: 超时后状态保存与重试."""

    @pytest.fixture
    def checkpoint_dir(self, tmp_path):
        return tmp_path / "checkpoints"

    @pytest.fixture
    def agent(self, checkpoint_dir):
        return IndependentAgent(
            name="test_agent",
            system_prompt="test",
            checkpoint_dir=checkpoint_dir,
        )

    @pytest.mark.asyncio
    async def test_timeout_saves_partial_messages(self, agent, checkpoint_dir):
        """超时后应保存 partial messages 到检查点."""
        partial_messages = [
            {"role": "assistant", "content": "partial content"},
        ]
        
        with patch.object(agent, '_call_llm', return_value=partial_messages):
            with patch.object(agent._session_manager, 'save_checkpoint') as mock_save:
                try:
                    await agent.execute_with_input(
                        system_prompt_append="test",
                        user_prompt="test",
                    )
                except Exception:
                    pass  # 期望可能抛出异常
        
        # 验证保存检查点被调用
        mock_save.assert_called_once()
        args = mock_save.call_args
        assert "messages" in args.kwargs or any("messages" in str(arg) for arg in args.args)

    @pytest.mark.asyncio
    async def test_retry_uses_saved_tool_result(self, agent):
        """重试时应使用已保存的工具返回，避免重复执行."""
        saved_state = {
            "messages": [
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "content": json.dumps({
                                "file_path": "/output/already_created.md",
                                "sha256": "already_hash",
                            }),
                            "is_error": False,
                        }
                    ],
                }
            ],
            "tool_executed": True,
        }
        
        with patch.object(agent._session_manager, 'load_checkpoint', return_value=saved_state):
            with patch.object(agent, '_call_llm') as mock_call:
                # 如果有检查点，不应重新调用 LLM
                result = await agent.execute_with_input(
                    system_prompt_append="test",
                    user_prompt="test",
                    resume_from_checkpoint=True,
                )
                
                # 验证使用了已保存的工具结果
                assert result.deliverable.file_path == "/output/already_created.md"
                mock_call.assert_not_called()  # 不应重新调用
```

---

## 九、端到端 (E2E) 测试

### 9.1 Pipeline 完整运行测试

```python
# tests/e2e/test_pipeline_timeout_fixes.py
"""端到端测试: 验证所有修复后 Pipeline 能正常完成."""

import pytest
import asyncio
from pathlib import Path


class TestPipelineWithAllFixes:
    """所有修复后的完整 Pipeline 测试."""

    @pytest.mark.e2e
    @pytest.mark.timeout(300)  # 5 分钟超时
    async def test_bubble_sort_pipeline_completes(self):
        """bubble-sort 上下文 Pipeline 应在合理时间内完成."""
        from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
        
        orchestrator = PipelineOrchestrator()
        
        result = await orchestrator.start(
            context_file="docs/bubble-sort/bubble-sort-context.md",
            timeout_per_node=1200,  # 20 分钟每节点
        )
        
        # 验证 Pipeline 成功完成
        assert result.status == "COMPLETED", f"Pipeline 失败: {result.error}"
        
        # 验证所有节点都有输出文件
        for node_result in result.node_results:
            assert node_result.output_file is not None, (
                f"节点 {node_result.node_name} 缺少输出文件"
            )
            assert Path(node_result.output_file).exists(), (
                f"节点 {node_result.node_name} 的输出文件不存在"
            )
            
            # 验证文件在正确的 output 目录下
            assert "output/pipeline-" in str(node_result.output_file), (
                f"文件不在正确的 pipeline output 目录: {node_result.output_file}"
            )

    @pytest.mark.e2e
    async def test_no_missing_file_path_errors(self):
        """运行 Pipeline 不应出现 MISSING_FILE_PATH 错误."""
        import logging
        from unittest.mock import patch
        
        error_logs = []
        
        def capture_error(logger, event, **kwargs):
            if "MISSING_FILE_PATH" in str(event) or "MISSING_FILE_PATH" in str(kwargs):
                error_logs.append((event, kwargs))
        
        with patch('structlog.stdlib.BoundLogger.error', capture_error):
            # 运行 Pipeline
            pass  # ...
        
        assert len(error_logs) == 0, f"发现 MISSING_FILE_PATH 错误: {error_logs}"
```

---

## 十、测试执行计划

### 10.1 执行顺序

```bash
# 阶段 1: Fix-1 (P0)
pytest tests/unit/prompts/test_contract_builder_fix1.py -v
pytest tests/unit/prompts/test_contract_builder_regression.py -v

# 阶段 2: Fix-2 (P0) 
pytest tests/unit/agents/test_independent_agent_fix2.py -v
pytest tests/integration/agents/test_independent_agent_timeout_scenario.py -v

# 阶段 3: Fix-3 (P1)
pytest tests/unit/llm/test_session_manager_fix3.py -v

# 阶段 4: Fix-4 (P1)
pytest tests/unit/tools/test_create_deliverable_fix4.py -v

# 阶段 5: Fix-6 (P1)
pytest tests/unit/agents/test_prompt_path_alignment_fix6.py -v

# 阶段 6: Fix-5 (P2)
pytest tests/integration/agents/test_state_persistence_fix5.py -v

# 阶段 7: 端到端
pytest tests/e2e/test_pipeline_timeout_fixes.py -v --e2e
```

### 10.2 使用调试工具验证

```bash
# 运行调试工具验证所有修复
cd /d/GITHUB/DocuSwarm
PYTHONIOENCODING=utf-8 python tools/timeout_root_cause_analyzer.py

# 验证结果应显示所有 Fix 为 FIXED
```

---

## 十一、修复检查清单

| Fix | 测试文件 | 实现文件 | 验证命令 |
|-----|----------|----------|----------|
| Fix-1 | `test_contract_builder_fix1.py` | `contract_builder.py` | `pytest tests/unit/prompts/test_contract_builder_fix1.py` |
| Fix-2 | `test_independent_agent_fix2.py` | `independent.py` | `pytest tests/unit/agents/test_independent_agent_fix2.py` |
| Fix-3 | `test_session_manager_fix3.py` | `session_manager.py` | `pytest tests/unit/llm/test_session_manager_fix3.py` |
| Fix-4 | `test_create_deliverable_fix4.py` | `independent.py` 或 `callable_tool_wrapper.py` | `pytest tests/unit/tools/test_create_deliverable_fix4.py` |
| Fix-5 | `test_state_persistence_fix5.py` | TBD | `pytest tests/integration/agents/test_state_persistence_fix5.py` |
| Fix-6 | `test_prompt_path_alignment_fix6.py` | Fix-1 覆盖 | `pytest tests/unit/agents/test_prompt_path_alignment_fix6.py` |

---

*方案基于: [pipeline-timeout-root-cause-analysis.md](../research/pipeline-timeout-root-cause-analysis.md)*  
*创建: 2026-04-06*
