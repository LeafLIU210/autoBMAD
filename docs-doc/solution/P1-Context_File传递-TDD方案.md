# P1: Context_File 传递 — 测试驱动开发方案

**优先级**: P1 (High)  
**预估工时**: 30 分钟  
**依赖**: [P0-Output目录统一-TDD方案.md](./P0-Output目录统一-TDD方案.md)  
**影响范围**: Agent 交付物质量

---

## 目录

1. [问题描述](#1-问题描述)
2. [根因分析](#2-根因分析)
3. [解决方案设计](#3-解决方案设计)
4. [TDD 测试用例](#4-tdd-测试用例)
5. [实施步骤](#5-实施步骤)
6. [验证清单](#6-验证清单)

---

## 1. 问题描述

### 1.1 现象

用户提供的 `context_file` (如 `proposal.md`) 的完整内容未能传递到 IndependentAgent 的 LLM Prompt 中。

**预期行为**:
```
用户 → CLI → context_file.content → PipelineState → IndependentAgent → LLM Prompt
                ↑                                                          ↑
        "Build a web app..."                                      "Build a web app..."
```

**实际行为**:
```
用户 → CLI → context_file.content → PipelineState → IndependentAgent → LLM Prompt
                ↑                                                          ↑
        "Build a web app..."                                      (只有 task 字段)
```

### 1.2 影响

1. **交付物质量下降**: Agent 生成的文档缺乏对原始需求的理解
2. **上下文丢失**: 后续节点无法获取完整的需求背景
3. **迭代效率低**: 需要用户反复补充信息

### 1.3 复现步骤

```bash
# 创建 context 文件
echo "# Project Proposal\n\nBuild a web application with user authentication." > proposal.md

# 运行 Pipeline
python -m autoBMAD.docuswarm start -c proposal.md

# 检查 analyst 节点的交付物
# 发现交付物中没有引用 "web application" 或 "user authentication" 等原始内容
```

---

## 2. 根因分析

### 2.1 数据传递链

```
1. CLI 读取文件
   main.py:108 → content = f.read()

2. 构建 subject_context
   main.py:131-135 → subject_context = {
       "subject": subject,
       "context_file": str(context_path),
       "content": content,  ← 完整内容在这里
   }

3. 传入 Orchestrator
   main.py:138 → orchestrator.start_pipeline(subject_context)

4. 创建初始状态
   orchestrator.py:395 → initial_state = create_initial_state(pipeline_id, subject_context)
   # initial_state["subject_context"] = subject_context ← 正确保存

5. Graph 转换为 NodeRunState
   graph.py:192 → context_file = json.dumps(accumulated)
   # accumulated = {
   #   "subject_context": subject_context,  ← 包含 content
   #   "analyst_deliverable": {...},
   #   ...
   # }

6. Executor 提取 context_file
   executor.py:135 → subject_context = state.get("context_file", "")
   # subject_context 现在是 JSON 字符串

7. DualAgentNode.execute()
   dual_agent.py:172 → await self.independent.execute({
       "task": task,
       "subject_context": subject_context,  ← 传递了
       "pipeline_id": pipeline_id,
   })

8. IndependentAgent.execute() ❌ 问题点
   independent.py:431-437 → 
   task = context.get("task", "")
   # 只提取了 task，未使用 subject_context 中的 content！
```

### 2.2 问题代码位置

**文件**: `autoBMAD/docuswarm/agents/independent.py`

**位置**: `execute` 方法 (约 420-450 行)

```python
async def execute(
    self,
    context: dict[str, Any],
) -> dict[str, Any]:
    # Extract task
    task: str = cast(str, context.get("task", ""))
    if not task:
        subject_ctx = context.get("subject_context", {})
        if isinstance(subject_ctx, dict):
            task = cast(str, subject_ctx.get("task", ""))
    if not task:
        raise IndependentAgentError("No task provided in context")

    # Story 11.1: Extract pipeline_id
    pipeline_id: str = context.get("pipeline_id", "")
    if not pipeline_id:
        raise IndependentAgentError("pipeline_id is required in context")

    # ❌ 缺少: 提取 subject_context 中的 content
    # ❌ 缺少: 将 content 注入 LLM Prompt

    # ... 后续代码调用 _call_llm(user_message=task) 
    # 只传递了 task，没有原始 context
```

### 2.3 根因总结

| 组件 | 状态 | 说明 |
|------|------|------|
| CLI → subject_context | ✅ 正确 | content 被正确读取并封装 |
| Orchestrator → PipelineState | ✅ 正确 | subject_context 被保存到状态 |
| Graph → accumulate_context | ✅ 正确 | 合并了前序节点交付物 |
| Executor → DualAgentNode | ✅ 正确 | subject_context 被传递 |
| **IndependentAgent → LLM** | ❌ 断裂 | 只提取 task，忽略 content |

---

## 3. 解决方案设计

### 3.1 方案概述

```
修改策略:
1. IndependentAgent.execute(): 提取 subject_context 中的 content
2. 构建 enriched_task: 将原始 content 注入 LLM Prompt
3. 添加日志: 记录 content 是否成功提取
```

### 3.2 代码修改设计

#### 修改: `independent.py` - `execute` 方法

**修改位置**: 约 420-480 行

**修改前** (简化展示):
```python
async def execute(
    self,
    context: dict[str, Any],
) -> dict[str, Any]:
    # Extract task
    task: str = cast(str, context.get("task", ""))
    if not task:
        subject_ctx = context.get("subject_context", {})
        if isinstance(subject_ctx, dict):
            task = cast(str, subject_ctx.get("task", ""))
    if not task:
        raise IndependentAgentError("No task provided in context")

    # Extract pipeline_id
    pipeline_id: str = context.get("pipeline_id", "")
    if not pipeline_id:
        raise IndependentAgentError("pipeline_id is required in context")

    # ... 省略中间代码 ...

    # Call LLM
    response = await self._call_llm(user_message=task)  # ← 只传 task
```

**修改后**:
```python
async def execute(
    self,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Execute the independent agent.
    
    Args:
        context: Execution context containing:
            - task: The task to perform
            - subject_context: Original context (may be dict or JSON string)
            - pipeline_id: Pipeline identifier
    
    Returns:
        Dict containing:
            - deliverable: {title, content, metadata}
            - questions: List of {priority, question, context}
    """
    import json
    
    # Extract task
    task: str = cast(str, context.get("task", ""))
    if not task:
        subject_ctx = context.get("subject_context", {})
        if isinstance(subject_ctx, dict):
            task = cast(str, subject_ctx.get("task", ""))
    if not task:
        raise IndependentAgentError("No task provided in context")

    # Extract pipeline_id
    pipeline_id: str = context.get("pipeline_id", "")
    if not pipeline_id:
        raise IndependentAgentError("pipeline_id is required in context")

    # ===== 新增: 提取原始 context 内容 =====
    subject_context_raw = context.get("subject_context", {})
    
    # 规范化 subject_context (可能是 dict 或 JSON string)
    if isinstance(subject_context_raw, str):
        try:
            subject_context_data = json.loads(subject_context_raw)
        except json.JSONDecodeError:
            # 如果不是有效 JSON，包装为简单 dict
            subject_context_data = {"context": subject_context_raw}
    elif isinstance(subject_context_raw, dict):
        subject_context_data = subject_context_raw
    else:
        subject_context_data = {}
    
    # 提取原始 context 文件内容 (支持多层嵌套)
    context_content = ""
    
    # 尝试路径 1: subject_context.subject_context.content
    nested_ctx = subject_context_data.get("subject_context", {})
    if isinstance(nested_ctx, dict):
        context_content = nested_ctx.get("content", "")
    
    # 尝试路径 2: subject_context.content
    if not context_content:
        context_content = subject_context_data.get("content", "")
    
    self.logger.info(
        "extracted_context_content",
        task_preview=task[:100] if task else "",
        has_context_content=bool(context_content),
        context_length=len(context_content) if context_content else 0,
    )
    # ===== 新增结束 =====

    # ... 省略 output_dir 设置等代码 ...

    # ===== 修改: 构建包含 context 的 enriched_task =====
    if context_content:
        enriched_task = f"""## Original Context

{context_content}

## Task

{task}

Please create the deliverable based on the original context above. Reference specific details from the context in your analysis."""
    else:
        enriched_task = task
    # ===== 修改结束 =====

    try:
        # Call LLM with enriched task (包含原始 context)
        response = await self._call_llm(user_message=enriched_task)
    finally:
        # ... cleanup code ...
        pass

    # ... 后续解析代码 ...
```

### 3.3 enriched_task 格式说明

```markdown
## Original Context

[用户提供的 context_file 完整内容]

## Task

[从 state 提取的 task 描述]

Please create the deliverable based on the original context above. Reference specific details from the context in your analysis.
```

**设计理由**:
1. **清晰分隔**: `## Original Context` 和 `## Task` 明确区分原始需求和任务指令
2. **完整保留**: 原始内容不做任何截断或摘要
3. **引导 LLM**: 最后一句提示 LLM 引用原始 context 中的具体细节

---

## 4. TDD 测试用例

### 4.1 测试文件

**文件**: `tests/unit/test_independent_agent_context.py`

### 4.2 测试代码

```python
"""Unit tests for IndependentAgent context extraction and usage.

This module tests:
1. Extracting content from dict subject_context
2. Extracting content from JSON string subject_context
3. Handling nested subject_context structures
4. Fallback when no content is available
5. enriched_task format validation
"""

import json
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from autoBMAD.docuswarm.agents.independent import IndependentAgent
from autoBMAD.docuswarm.config import Config as AgentConfig


@pytest.fixture
def mock_config(tmp_path: Path) -> AgentConfig:
    """Create a mock AgentConfig for testing."""
    return AgentConfig(
        db_path=tmp_path / "test.db",
        api_key="test-api-key",
        base_url="https://api.test.com",
    )


@pytest.fixture
def mock_session_manager() -> MagicMock:
    """Create a mock KimiSessionManager."""
    return MagicMock()


class TestContextExtraction:
    """Test context extraction from various input formats."""

    @pytest.mark.asyncio
    async def test_extract_content_from_dict_subject_context(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test extracting content from dict subject_context."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            # Mock LLM call to capture the user_message
            captured_messages: list[str] = []
            
            async def capture_llm_call(user_message: str) -> list[Any]:
                captured_messages.append(user_message)
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=capture_llm_call):
                context = {
                    "task": "Create analysis document",
                    "pipeline_id": "test-pipeline-123",
                    "subject_context": {
                        "subject_context": {
                            "content": "Original proposal: Build a web application with user authentication."
                        }
                    },
                }
                
                await agent.execute(context)
                
                # Verify LLM received enriched_task with original content
                assert len(captured_messages) == 1
                enriched_task = captured_messages[0]
                
                assert "## Original Context" in enriched_task
                assert "Original proposal: Build a web application" in enriched_task
                assert "## Task" in enriched_task
                assert "Create analysis document" in enriched_task

    @pytest.mark.asyncio
    async def test_extract_content_from_json_string(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test extracting content from JSON string subject_context."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            captured_messages: list[str] = []
            
            async def capture_llm_call(user_message: str) -> list[Any]:
                captured_messages.append(user_message)
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=capture_llm_call):
                # subject_context 是 JSON 字符串
                subject_context_json = json.dumps({
                    "subject_context": {
                        "content": "JSON content: Design a REST API."
                    }
                })
                
                context = {
                    "task": "Create API specification",
                    "pipeline_id": "test-pipeline-456",
                    "subject_context": subject_context_json,
                }
                
                await agent.execute(context)
                
                # Verify content was extracted from JSON string
                assert len(captured_messages) == 1
                enriched_task = captured_messages[0]
                
                assert "JSON content: Design a REST API" in enriched_task

    @pytest.mark.asyncio
    async def test_extract_content_from_flat_structure(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test extracting content from flat subject_context structure."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            captured_messages: list[str] = []
            
            async def capture_llm_call(user_message: str) -> list[Any]:
                captured_messages.append(user_message)
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=capture_llm_call):
                # 扁平结构: content 直接在 subject_context 下
                context = {
                    "task": "Analyze requirements",
                    "pipeline_id": "test-pipeline-789",
                    "subject_context": {
                        "content": "Flat structure content: Mobile app requirements."
                    },
                }
                
                await agent.execute(context)
                
                # Verify content was extracted from flat structure
                assert len(captured_messages) == 1
                enriched_task = captured_messages[0]
                
                assert "Flat structure content: Mobile app" in enriched_task


class TestFallbackBehavior:
    """Test fallback behavior when content is not available."""

    @pytest.mark.asyncio
    async def test_no_original_context_header_when_empty(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test that '## Original Context' is not added when content is empty."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            captured_messages: list[str] = []
            
            async def capture_llm_call(user_message: str) -> list[Any]:
                captured_messages.append(user_message)
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=capture_llm_call):
                # 空的 subject_context
                context = {
                    "task": "Create document without context",
                    "pipeline_id": "test-pipeline-empty",
                    "subject_context": {},
                }
                
                await agent.execute(context)
                
                # Verify no "## Original Context" header
                assert len(captured_messages) == 1
                enriched_task = captured_messages[0]
                
                assert "## Original Context" not in enriched_task
                assert "Create document without context" in enriched_task

    @pytest.mark.asyncio
    async def test_task_only_when_content_missing(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test that only task is sent when content is missing."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            captured_messages: list[str] = []
            
            async def capture_llm_call(user_message: str) -> list[Any]:
                captured_messages.append(user_message)
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=capture_llm_call):
                context = {
                    "task": "Simple task",
                    "pipeline_id": "test-simple",
                    "subject_context": {
                        "subject_context": {
                            # 没有 content 字段
                            "subject": "test"
                        }
                    },
                }
                
                await agent.execute(context)
                
                # Verify only task was sent
                assert len(captured_messages) == 1
                enriched_task = captured_messages[0]
                
                # 应该直接是 task，没有额外格式
                assert enriched_task == "Simple task"


class TestEnrichedTaskFormat:
    """Test the format of enriched_task."""

    @pytest.mark.asyncio
    async def test_enriched_task_structure(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test that enriched_task has correct structure."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            captured_messages: list[str] = []
            
            async def capture_llm_call(user_message: str) -> list[Any]:
                captured_messages.append(user_message)
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=capture_llm_call):
                context = {
                    "task": "Analyze the project requirements",
                    "pipeline_id": "test-format",
                    "subject_context": {
                        "subject_context": {
                            "content": "# Project Requirements\n\n1. User authentication\n2. Dashboard"
                        }
                    },
                }
                
                await agent.execute(context)
                
                enriched_task = captured_messages[0]
                
                # Verify structure
                lines = enriched_task.split("\n")
                
                # 检查头部: ## Original Context
                assert lines[0] == "## Original Context"
                
                # 检查 content 出现在 Original Context 之后
                context_start = enriched_task.index("## Original Context")
                task_start = enriched_task.index("## Task")
                content_start = enriched_task.index("# Project Requirements")
                
                assert context_start < content_start < task_start
                
                # 检查 task 出现在 ## Task 之后
                assert "Analyze the project requirements" in enriched_task[task_start:]


class TestLogging:
    """Test logging of context extraction."""

    @pytest.mark.asyncio
    async def test_logs_context_extraction_success(
        self,
        tmp_path: Path,
        mock_config: AgentConfig,
        mock_session_manager: MagicMock,
    ) -> None:
        """Test that successful context extraction is logged."""
        with patch(
            "autoBMAD.docuswarm.agents.independent.PersonaLoader.load"
        ) as mock_persona:
            mock_persona.return_value = MagicMock()
            
            agent = IndependentAgent(
                config=mock_config,
                session_manager=mock_session_manager,
                node_id="analyst",
                project_root=tmp_path,
            )
            
            # Capture log calls
            log_calls: list[tuple[str, dict]] = []
            original_info = agent.logger.info
            
            def capture_log(event: str, **kwargs: Any) -> None:
                log_calls.append((event, kwargs))
                original_info(event, **kwargs)
            
            agent.logger.info = capture_log
            
            async def mock_llm(user_message: str) -> list[Any]:
                return [
                    MagicMock(
                        role="assistant",
                        content=[
                            MagicMock(
                                text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}'
                            )
                        ],
                    )
                ]
            
            with patch.object(agent, "_call_llm", side_effect=mock_llm):
                context = {
                    "task": "Test task",
                    "pipeline_id": "test-log",
                    "subject_context": {
                        "subject_context": {
                            "content": "Test content for logging"
                        }
                    },
                }
                
                await agent.execute(context)
                
                # Find the context extraction log entry
                extraction_logs = [
                    (event, kwargs)
                    for event, kwargs in log_calls
                    if event == "extracted_context_content"
                ]
                
                assert len(extraction_logs) == 1
                event, kwargs = extraction_logs[0]
                
                assert kwargs["has_context_content"] is True
                assert kwargs["context_length"] == len("Test content for logging")
```

### 4.3 测试运行命令

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行单元测试
pytest tests/unit/test_independent_agent_context.py -v --tb=short

# 运行带覆盖率
pytest tests/unit/test_independent_agent_context.py -v --cov=autoBMAD.docuswarm.agents.independent
```

---

## 5. 实施步骤

### 5.1 Step 1: 创建测试文件

```bash
# 确保测试目录存在
mkdir -p tests/unit

# 创建测试文件 (复制上述测试代码)
# tests/unit/test_independent_agent_context.py
```

### 5.2 Step 2: 运行测试 (确认当前失败)

```bash
pytest tests/unit/test_independent_agent_context.py -v
# 预期: 大部分测试失败 (test_extract_content_* 系列)
```

### 5.3 Step 3: 修改 `independent.py`

在 `execute` 方法中添加:
1. `import json` (如果尚未导入)
2. 提取 `subject_context_raw`
3. 规范化为 dict
4. 提取 `context_content`
5. 构建 `enriched_task`
6. 添加日志记录

### 5.4 Step 4: 重新运行测试 (确认通过)

```bash
pytest tests/unit/test_independent_agent_context.py -v
# 预期: 所有测试通过
```

### 5.5 Step 5: 手动验证

```bash
# 创建 context 文件
cat > test_proposal.md << 'EOF'
# Web Application Proposal

## Requirements
1. User authentication with OAuth2
2. Real-time notifications
3. Dashboard with analytics

## Technical Stack
- Frontend: React with TypeScript
- Backend: Python FastAPI
- Database: PostgreSQL
EOF

# 运行 Pipeline
python -m autoBMAD.docuswarm start -c test_proposal.md

# 检查日志输出
# 应该看到: has_context_content=True, context_length=xxx

# 检查 analyst 节点交付物
cat autoBMAD/output/pipeline-*/analyst-*.md
# 应该包含对 "OAuth2", "React", "PostgreSQL" 等原始内容的引用
```

### 5.6 Step 6: 运行回归测试

```bash
# 类型检查
basedpyright autoBMAD/docuswarm/agents/independent.py

# 代码风格
ruff check autoBMAD/docuswarm/agents/independent.py

# 相关单元测试
pytest tests/unit/ -k "independent" -v --tb=short
```

---

## 6. 验证清单

### 6.1 修复前状态 (预期失败)

- [ ] 运行 `pytest tests/unit/test_independent_agent_context.py -v`
- [ ] 确认 `test_extract_content_from_dict_subject_context` 失败
- [ ] 确认 LLM 只接收 `task`，不包含原始 context

### 6.2 修复后状态 (预期通过)

- [ ] 所有 `test_independent_agent_context.py` 测试通过
- [ ] 日志显示 `has_context_content=True`
- [ ] 日志显示正确的 `context_length`
- [ ] LLM Prompt 包含 `## Original Context` 部分
- [ ] LLM Prompt 包含 `## Task` 部分
- [ ] 原始 context 内容完整保留在 Prompt 中

### 6.3 交付物验证

- [ ] Analyst 节点交付物引用了原始 context 中的具体内容
- [ ] 后续节点可以访问前序节点的交付物 (accumulate_context 正常工作)

### 6.4 回归测试

- [ ] `basedpyright` 类型检查通过
- [ ] `ruff check` 代码风格通过
- [ ] 现有单元测试无回归

---

## 附录

### A. enriched_task 完整示例

**输入**:
- task: "Create requirements analysis document"
- content: "# Proposal\n\nBuild a mobile app for food ordering."

**输出 (enriched_task)**:
```markdown
## Original Context

# Proposal

Build a mobile app for food ordering.

## Task

Create requirements analysis document

Please create the deliverable based on the original context above. Reference specific details from the context in your analysis.
```

### B. 数据流图

```
subject_context (from CLI)
    │
    ▼
┌───────────────────────────────────────┐
│ PipelineState["subject_context"]      │
│ {                                     │
│   "subject": "proposal",              │
│   "context_file": "proposal.md",      │
│   "content": "..."                    │◄── 完整内容
│ }                                     │
└───────────────────────────────────────┘
    │
    ▼ accumulate_context()
┌───────────────────────────────────────┐
│ accumulated (JSON string)             │
│ {                                     │
│   "subject_context": {...},           │◄── 包含 content
│   "analyst_deliverable": {...}        │
│ }                                     │
└───────────────────────────────────────┘
    │
    ▼ IndependentAgent.execute()
┌───────────────────────────────────────┐
│ context_content = extracted content   │
│                                       │
│ enriched_task =                       │
│   ## Original Context                 │
│   {content}                           │◄── 注入原始内容
│                                       │
│   ## Task                             │
│   {task}                              │
└───────────────────────────────────────┘
    │
    ▼ _call_llm(user_message=enriched_task)
┌───────────────────────────────────────┐
│ LLM receives full context + task      │
│ → Generates informed deliverable      │
└───────────────────────────────────────┘
```

### C. 参考链接

- [概览文档](./Output目录统一与Context_File传递-概览.md)
- [前一阶段: P0-Output目录统一-TDD方案.md](./P0-Output目录统一-TDD方案.md)
- [下一阶段: P2-docs文档修改能力-TDD方案.md](./P2-docs文档修改能力-TDD方案.md)
