# Output 目录统一与 Context_File 传递 — 测试驱动解决方案

**创建日期**: 2026-02-24  
**需求来源**: 用户需求分析  
**分析范围**: `autoBMAD\docuswarm`

---

## 执行摘要

### 需求描述

1. **统一输出路径**: 所有节点交付物保存到 `autoBMAD\output\{pipeline_id}\`
2. **Context_File 传递**: 每个独立 Agent 根据 `<context_file>` 独立创建交付物
3. **@docs 文档修改能力**: 允许每个独立 Agent 根据节点交付物修改主目录下的 `@docs` 相关文档

### 当前问题

#### 问题 1: 输出目录重复创建 (P0)

**现象**:
- ✅ `autoBMAD\output\pipeline-xxx\` — 正确位置 (IndependentAgent 创建)
- ❌ `d:\GITHUB\DocuSwarm\pipeline-xxx\` — 意外位置 (Orchestrator 默认 work_dir)

**根因**:
```python
# orchestrator.py:181
work_dir = KaosPath(self._work_dir) if self._work_dir else KaosPath.cwd()
#                                                          ↑ 当 _work_dir=None 时使用当前工作目录
```

**影响**: 
- 用户执行命令时在项目根目录 `d:\GITHUB\DocuSwarm\`
- Kimi SDK 使用 `cwd()` 创建了根目录的 `pipeline-xxx\`
- IndependentAgent 单独创建了正确的 `autoBMAD\output\pipeline-xxx\`

#### 问题 2: Context_File 未正确传递 (P1)

**现状分析**:

1. **Orchestrator 创建 context**:
```python
# orchestrator.py:395
initial_state = create_initial_state(pipeline_id, subject_context)
# subject_context = {"subject": "proposal", "context_file": "proposal.md", "content": "..."}
```

2. **Pipeline State 存储**:
```python
# state.py:263
def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> PipelineState:
    return {
        "pipeline_id": pipeline_id,
        "subject_context": subject_context,  # ← 包含 context_file
        ...
    }
```

3. **Graph 节点转换**:
```python
# graph.py:185-193
subject_context = state.get("subject_context", {})
accumulated = accumulate_context(subject_context, deliverables, node_id)
context_file = json.dumps(accumulated)  # ← 序列化为 JSON 字符串
```

4. **Executor 调用节点**:
```python
# executor.py:135-144
subject_context = state.get("context_file", "")
task = _extract_task_from_state(state)
result = await node.execute(
    subject_context=str(subject_context),
    task=task,
    pipeline_id=pipeline_id,
)
```

5. **IndependentAgent 接收**:
```python
# independent.py:431-437
task: str = cast(str, context.get("task", ""))
if not task:
    subject_ctx = context.get("subject_context", {})
    if isinstance(subject_ctx, dict):
        task = cast(str, subject_ctx.get("task", ""))
```

**问题点**:
- ✅ `subject_context` 正确传递到 `PipelineState`
- ✅ `accumulate_context` 合并了前序节点交付物
- ❌ `IndependentAgent` 只提取了 `task`，未使用完整的 `context_file`
- ❌ Agent 的 LLM Prompt 中未包含原始 context 文件内容

---

## 问题深度分析

### 根因层 1: Orchestrator 未初始化 _work_dir

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

**问题位置**: 第 100-150 行 `__init__` 方法

```python
def __init__(
    self,
    db_path: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
):
    self._db_path = db_path or "docuswarm.db"
    self._api_key = api_key
    self._base_url = base_url
    self._checkpointer = checkpointer
    self._session_manager: KimiSessionManager | None = None
    self._state_manager = StateManager(db_path=self._db_path)
    self._work_dir: str | None = None  # ← 始终为 None！
```

**调用链**:
```
main.py:start() 
  ↓
orchestrator = HybridOrchestrator(db_path=..., api_key=..., base_url=...)
  ↓
self._work_dir = None  # 未设置
  ↓
_get_or_create_session_manager()
  ↓
work_dir = KaosPath(self._work_dir) if self._work_dir else KaosPath.cwd()
  ↓
KaosPath.cwd() = d:\GITHUB\DocuSwarm  # 当前工作目录
  ↓
Kimi SDK 在根目录创建 pipeline-xxx\
```

### 根因层 2: Context_File 传递链断裂

**传递链分析**:

```
1. CLI 读取文件
   main.py:108 → content = f.read()

2. 构建 subject_context
   main.py:131-135 → subject_context = {
       "subject": subject,
       "context_file": str(context_path),
       "content": content,
   }

3. 传入 Orchestrator
   main.py:138 → orchestrator.start_pipeline(subject_context)

4. 创建初始状态
   orchestrator.py:395 → initial_state = create_initial_state(pipeline_id, subject_context)

5. Graph 转换为 NodeRunState
   graph.py:192 → context_file = json.dumps(accumulated)
   # accumulated = {
   #   "subject_context": subject_context,  # ← 包含 content
   #   "analyst_deliverable": {...},
   #   ...
   # }

6. Executor 提取 context_file
   executor.py:135 → subject_context = state.get("context_file", "")

7. DualAgentNode.execute()
   dual_agent.py:172 → await self.independent.execute({
       "task": task,
       "subject_context": subject_context,
       "pipeline_id": pipeline_id,
   })

8. IndependentAgent.execute()
   independent.py:431-437 → 
   task = context.get("task", "")
   # ❌ 未使用 subject_context 中的 content！
```

**断裂点**:
- `IndependentAgent` 接收到 `subject_context`，但只提取 `task`
- LLM Prompt 构建时未包含 `context_file` 的完整内容
- Agent 生成交付物时缺少原始需求上下文

---

## 测试驱动解决方案

### 方案 A: 修复 Orchestrator work_dir 初始化 (P0)

#### A1. 添加 work_dir 参数到 __init__

**修复文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

**位置**: 第 100-150 行

**修改**:
```python
def __init__(
    self,
    db_path: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    work_dir: str | None = None,  # ← 新增参数
):
    self._db_path = db_path or "docuswarm.db"
    self._api_key = api_key
    self._base_url = base_url
    self._checkpointer = checkpointer
    self._session_manager: KimiSessionManager | None = None
    self._state_manager = StateManager(db_path=self._db_path)
    
    # 新增: 初始化 work_dir，默认为 autoBMAD/output
    if work_dir is None:
        # 计算 autoBMAD 根目录
        autoBMAD_root = Path(__file__).parent.parent.parent.resolve()
        self._work_dir = str(autoBMAD_root / "output")
    else:
        self._work_dir = work_dir
    
    logger.info("orchestrator_initialized", work_dir=self._work_dir)
```

#### A2. 在 start_pipeline 中创建 pipeline 子目录

**位置**: 第 385-400 行

**修改**:
```python
# Step 4: Set logging context for this pipeline
set_log_context(run_id=final_pipeline_id, node_id="orchestrator")

# Step 4.5: 确保 pipeline 输出目录存在
pipeline_work_dir = Path(self._work_dir) / final_pipeline_id
pipeline_work_dir.mkdir(parents=True, exist_ok=True)
logger.info("pipeline_work_dir_created", path=str(pipeline_work_dir))

# Step 5: Create and execute the pipeline graph
```

#### A3. 更新 _get_or_create_session_manager

**位置**: 第 176-190 行

**修改**:
```python
def _get_or_create_session_manager(self, pipeline_id: str | None = None) -> KimiSessionManager:
    """Get or create session manager with pipeline-specific work_dir.
    
    Args:
        pipeline_id: Optional pipeline ID for setting work_dir.
    
    Returns:
        KimiSessionManager instance.
    """
    if self._session_manager is not None and pipeline_id is None:
        return self._session_manager

    # Create a new session manager with pipeline-specific work_dir
    try:
        if pipeline_id:
            # Pipeline-specific work_dir
            work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id))
        else:
            # Global work_dir
            work_dir = KaosPath(self._work_dir)
        
        session_manager = KimiSessionManager(
            work_dir=work_dir,
            api_key=self._api_key,
            base_url=self._base_url,
        )
        
        # 只缓存全局 session_manager
        if pipeline_id is None:
            self._session_manager = session_manager
        
        logger.info("session_manager_created", work_dir=str(work_dir))
        return session_manager
    except Exception as e:
        logger.error("failed_to_create_session_manager", error=str(e))
        raise OrchestratorError(f"Failed to create session manager: {e}") from e
```

#### A4. 更新 main.py 调用

**修复文件**: `autoBMAD/docuswarm/main.py`

**位置**: 第 123-128 行

**修改**:
```python
# Use HybridOrchestrator to start the pipeline
config = load_config()

# 计算 autoBMAD 根目录
autoBMAD_root = Path(__file__).parent.parent
work_dir = str(autoBMAD_root / "output")

orchestrator = HybridOrchestrator(
    db_path=str(config.db_path),
    api_key=config.api_key,
    base_url=config.base_url,
    work_dir=work_dir,  # ← 传入 work_dir
)
```

### 方案 B: 修复 Context_File 传递到 LLM Prompt (P1)

#### B1. 在 IndependentAgent 中提取完整 context

**修复文件**: `autoBMAD/docuswarm/agents/independent.py`

**位置**: 第 420-450 行

**修改**:
```python
async def execute(
    self,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Execute the independent agent.
    
    Args:
        context: Execution context containing:
            - task: The task to perform
            - subject_context: Original context (可能是 dict 或 JSON string)
            - pipeline_id: Pipeline identifier
    
    Returns:
        Dict containing:
            - deliverable: {title, content, metadata}
            - questions: List of {priority, question, context}
    """
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

    # 新增: 提取完整的 subject_context 用于 LLM Prompt
    subject_context_raw = context.get("subject_context", {})
    
    # 规范化 subject_context (可能是 dict 或 JSON string)
    if isinstance(subject_context_raw, str):
        try:
            subject_context_data = json.loads(subject_context_raw)
        except json.JSONDecodeError:
            subject_context_data = {"context": subject_context_raw}
    elif isinstance(subject_context_raw, dict):
        subject_context_data = subject_context_raw
    else:
        subject_context_data = {}
    
    # 提取原始 context 文件内容
    context_content = subject_context_data.get("subject_context", {}).get("content", "")
    if not context_content:
        context_content = subject_context_data.get("content", "")
    
    self.logger.info(
        "extracted_context",
        task_preview=task[:100],
        has_context_content=bool(context_content),
        context_length=len(context_content) if context_content else 0,
    )

    # Compute output directory
    output_dir = self.project_root / "output" / pipeline_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set instance variables
    self._agent_file = (
        self.project_root / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
    )
    self._work_dir = output_dir

    self.logger.info(
        "executing_independent_agent",
        node_id=self.node_id,
        task=task[:100],
        pipeline_id=pipeline_id,
        work_dir=str(self._work_dir),
        agent_file=str(self._agent_file),
    )

    # Create session manager
    from kaos.path import KaosPath
    from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

    pipeline_session_manager = KimiSessionManager(
        work_dir=KaosPath(str(output_dir)),
        agent_file=self._agent_file,
        config=self.session_manager.config if self.session_manager else None,
    )

    original_session_manager = self.session_manager
    self.session_manager = pipeline_session_manager

    try:
        # 构建包含 context 的完整 prompt
        if context_content:
            enriched_task = f"""## Original Context

{context_content}

## Task

{task}

Please create the deliverable based on the original context above."""
        else:
            enriched_task = task
        
        # Call LLM with enriched task
        response = await self._call_llm(user_message=enriched_task)
    finally:
        self.session_manager = original_session_manager

    # Parse and validate response
    output = self._parse_response(response)

    self.logger.info(
        "independent_agent_completed",
        deliverable_title=output.get("deliverable", {}).get("title", "unknown"),
        questions_count=len(output.get("questions", [])),
    )

    return output
```

#### B2. 更新 accumulate_context 保留原始 content

**修复文件**: `autoBMAD/docuswarm/pipeline/state.py`

**位置**: 第 184-230 行

**修改**:
```python
def accumulate_context(
    subject_context: dict[str, Any],
    deliverables: dict[str, dict[str, Any]],
    current_node: str,
) -> dict[str, Any]:
    """Accumulate context by merging subject context with previous deliverables.
    
    Args:
        subject_context: The initial subject/context of the pipeline.
                        Should contain: {"subject": "...", "content": "...", "context_file": "..."}
        deliverables: Dictionary of node deliverables (key: node_id).
        current_node: The node that will receive this context.
    
    Returns:
        A new context dictionary containing subject_context and all previous deliverables.
    """
    try:
        current_index = PIPELINE_NODES.index(current_node)
    except ValueError:
        return {"subject_context": subject_context}

    previous_nodes = PIPELINE_NODES[:current_index]

    # Build accumulated context
    accumulated: dict[str, Any] = {
        "subject_context": subject_context.copy() if subject_context else {},
    }

    # Add each previous node's deliverable to the context
    for node_id in previous_nodes:
        if node_id in deliverables and deliverables[node_id]:
            accumulated[f"{node_id}_deliverable"] = deliverables[node_id].copy()

    return accumulated
```

**说明**: 该函数已经正确保留了 `subject_context`，无需修改。问题在于下游节点未使用 `content` 字段。

---

## 单元测试设计

### Test 1: Orchestrator work_dir 初始化

**测试文件**: `tests/unit/test_orchestrator_work_dir.py`

```python
import pytest
from pathlib import Path
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class TestOrchestratorWorkDir:
    """Test HybridOrchestrator work_dir initialization."""
    
    def test_default_work_dir_in_autoBMAD_output(self, tmp_path):
        """Test that default work_dir is autoBMAD/output."""
        orchestrator = HybridOrchestrator(
            db_path=str(tmp_path / "test.db"),
            api_key="test-key",
        )
        
        # work_dir 应该指向 autoBMAD/output
        assert orchestrator._work_dir.endswith("autoBMAD/output") or \
               orchestrator._work_dir.endswith("autoBMAD\\output")
    
    def test_custom_work_dir(self, tmp_path):
        """Test custom work_dir is respected."""
        custom_dir = tmp_path / "custom_output"
        
        orchestrator = HybridOrchestrator(
            db_path=str(tmp_path / "test.db"),
            api_key="test-key",
            work_dir=str(custom_dir),
        )
        
        assert orchestrator._work_dir == str(custom_dir)
    
    def test_session_manager_uses_pipeline_work_dir(self, tmp_path, monkeypatch):
        """Test session manager is created with pipeline-specific work_dir."""
        from kaos.path import KaosPath
        from unittest.mock import MagicMock, patch
        
        orchestrator = HybridOrchestrator(
            db_path=str(tmp_path / "test.db"),
            api_key="test-key",
            work_dir=str(tmp_path / "output"),
        )
        
        with patch("autoBMAD.docuswarm.pipeline.orchestrator.KimiSessionManager") as mock_sm:
            mock_sm.return_value = MagicMock()
            
            sm = orchestrator._get_or_create_session_manager(pipeline_id="test-123")
            
            # 验证 work_dir 包含 pipeline_id
            call_kwargs = mock_sm.call_args.kwargs
            assert "test-123" in str(call_kwargs["work_dir"])
```

### Test 2: Context_File 传递到 IndependentAgent

**测试文件**: `tests/unit/test_independent_agent_context.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from autoBMAD.docuswarm.agents.independent import IndependentAgent


class TestIndependentAgentContext:
    """Test IndependentAgent context extraction and usage."""
    
    @pytest.mark.asyncio
    async def test_extract_content_from_subject_context_dict(self, tmp_path, mock_config):
        """Test extracting content from dict subject_context."""
        with patch("autoBMAD.docuswarm.agents.persona.PersonaLoader.load"):
            agent = IndependentAgent(
                config=mock_config,
                session_manager=MagicMock(),
                node_id="analyst",
                project_root=tmp_path,
            )
            
            # Mock LLM call
            with patch.object(agent, "_call_llm", new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = [
                    MagicMock(
                        role="assistant",
                        content=[MagicMock(text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}')],
                    )
                ]
                
                context = {
                    "task": "Create document",
                    "pipeline_id": "test-123",
                    "subject_context": {
                        "subject_context": {
                            "content": "Original proposal content here"
                        }
                    }
                }
                
                await agent.execute(context)
                
                # 验证 LLM 接收到包含 content 的 prompt
                call_args = mock_llm.call_args
                user_message = call_args.kwargs["user_message"]
                
                assert "Original proposal content here" in user_message
                assert "## Original Context" in user_message
    
    @pytest.mark.asyncio
    async def test_extract_content_from_json_string(self, tmp_path, mock_config):
        """Test extracting content from JSON string subject_context."""
        import json
        
        with patch("autoBMAD.docuswarm.agents.persona.PersonaLoader.load"):
            agent = IndependentAgent(
                config=mock_config,
                session_manager=MagicMock(),
                node_id="analyst",
                project_root=tmp_path,
            )
            
            with patch.object(agent, "_call_llm", new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = [
                    MagicMock(
                        role="assistant",
                        content=[MagicMock(text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}')],
                    )
                ]
                
                subject_context_json = json.dumps({
                    "subject_context": {
                        "content": "JSON content here"
                    }
                })
                
                context = {
                    "task": "Create document",
                    "pipeline_id": "test-456",
                    "subject_context": subject_context_json,
                }
                
                await agent.execute(context)
                
                call_args = mock_llm.call_args
                user_message = call_args.kwargs["user_message"]
                
                assert "JSON content here" in user_message
    
    @pytest.mark.asyncio
    async def test_fallback_when_no_content(self, tmp_path, mock_config):
        """Test agent works when no content is available."""
        with patch("autoBMAD.docuswarm.agents.persona.PersonaLoader.load"):
            agent = IndependentAgent(
                config=mock_config,
                session_manager=MagicMock(),
                node_id="analyst",
                project_root=tmp_path,
            )
            
            with patch.object(agent, "_call_llm", new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = [
                    MagicMock(
                        role="assistant",
                        content=[MagicMock(text='{"deliverable": {"title": "Test", "content": "..."}, "questions": []}')],
                    )
                ]
                
                context = {
                    "task": "Create document",
                    "pipeline_id": "test-789",
                    "subject_context": {},
                }
                
                await agent.execute(context)
                
                # 应该只传递 task，不包含 "## Original Context"
                call_args = mock_llm.call_args
                user_message = call_args.kwargs["user_message"]
                
                assert "## Original Context" not in user_message
                assert "Create document" in user_message
```

### Test 3: 集成测试 - 完整 Pipeline

**测试文件**: `tests/integration/test_context_file_transmission.py`

```python
import pytest
import asyncio
from pathlib import Path
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


@pytest.mark.integration
@pytest.mark.timeout(300)
class TestContextFileTransmission:
    """Integration test for context_file transmission through pipeline."""
    
    def test_context_file_reaches_independent_agent(self, tmp_path):
        """Test that context_file content reaches IndependentAgent."""
        # 准备测试数据
        context_file = tmp_path / "test_context.md"
        context_file.write_text("# Test Proposal\n\nBuild a web application.")
        
        db_path = tmp_path / "test.db"
        work_dir = tmp_path / "output"
        
        orchestrator = HybridOrchestrator(
            db_path=str(db_path),
            api_key="test-key",
            work_dir=str(work_dir),
        )
        
        subject_context = {
            "subject": "test_context",
            "context_file": str(context_file),
            "content": context_file.read_text(),
        }
        
        # 运行 pipeline (只运行 analyst 节点)
        pipeline_id = asyncio.run(orchestrator.start_pipeline(subject_context))
        
        # 验证输出目录
        pipeline_output = work_dir / pipeline_id
        assert pipeline_output.exists()
        
        # 验证交付物包含 context 信息
        # (需要 mock LLM 或使用真实 API)
        analyst_report = pipeline_output / "analyst-report.md"
        if analyst_report.exists():
            content = analyst_report.read_text()
            # 验证交付物反映了原始 context
            assert len(content) > 0
```

---

## 修复实施顺序

### 阶段 1: 修复 Orchestrator work_dir (P0 — 20 分钟)

1. **修改 orchestrator.py** (方案 A1-A3):
   - 添加 `work_dir` 参数到 `__init__`
   - 默认值设为 `autoBMAD/output`
   - 更新 `_get_or_create_session_manager` 支持 pipeline_id

2. **修改 main.py** (方案 A4):
   - 计算 `autoBMAD_root`
   - 传入 `work_dir` 参数

3. **运行单元测试**:
   ```bash
   pytest tests/unit/test_orchestrator_work_dir.py -v
   ```

4. **手动验证**:
   ```bash
   python -m autoBMAD.docuswarm start -c proposal.md
   # 验证只创建 autoBMAD\output\pipeline-xxx\
   # 确认根目录无 pipeline-xxx\
   ```

### 阶段 2: 修复 Context_File 传递 (P1 — 30 分钟)

1. **修改 independent.py** (方案 B1):
   - 提取 `subject_context` 中的 `content`
   - 构建 enriched_task 包含原始 context
   - 添加日志记录

2. **运行单元测试**:
   ```bash
   pytest tests/unit/test_independent_agent_context.py -v
   ```

3. **运行集成测试**:
   ```bash
   pytest tests/integration/test_context_file_transmission.py -v --timeout=300
   ```

### 阶段 3: 回归测试 (10 分钟)

```bash
# 单元测试
pytest tests/unit/ -v --tb=short

# 集成测试 (快速验证)
pytest tests/integration/test_node_executor_integration.py -k "Mock" -v

# 完整流程验证
python -m autoBMAD.docuswarm start -c proposal.md
python -m autoBMAD.docuswarm status <pipeline_id>
python -m autoBMAD.docuswarm export <pipeline_id> ./output
```

---

## 验证清单

### ✅ 修复前检查

- [ ] 确认根目录存在 `pipeline-xxx\` 文件夹
- [ ] 确认 `autoBMAD\output\pipeline-xxx\` 正确创建
- [ ] 确认 `orchestrator._work_dir` 为 `None`
- [ ] 确认 `IndependentAgent` 未使用 `context_file.content`

### ✅ 修复后验证 - 阶段 1

- [ ] `orchestrator._work_dir` 指向 `autoBMAD/output`
- [ ] 运行 pipeline 后只在 `autoBMAD\output\` 创建目录
- [ ] 根目录无 `pipeline-xxx\` 文件夹
- [ ] 单元测试 `test_orchestrator_work_dir.py` 全部通过

### ✅ 修复后验证 - 阶段 2

- [ ] LLM Prompt 包含 `## Original Context` 部分
- [ ] `context_content` 正确提取
- [ ] 日志显示 `has_context_content=True`
- [ ] 单元测试 `test_independent_agent_context.py` 全部通过

### ✅ 修复后验证 - 阶段 3

- [ ] 所有单元测试保持通过
- [ ] 集成测试无回归
- [ ] 端到端验证: context → analyst → deliverable

---

## 附加优化建议

### 1. 添加配置选项

**修改文件**: `autoBMAD/docuswarm/config.py`

```python
DEFAULT_OUTPUT_DIR = "output"  # 已存在

# 在 Config 类中添加
@dataclass(frozen=True)
class Config:
    ...
    output_dir: Path = field(default_factory=lambda: Path(DEFAULT_OUTPUT_DIR))
```

**修改 orchestrator.py**:
```python
def __init__(self, ..., config: Config | None = None):
    if work_dir is None:
        if config and config.output_dir:
            self._work_dir = str(config.output_dir)
        else:
            autoBMAD_root = Path(__file__).parent.parent.parent.resolve()
            self._work_dir = str(autoBMAD_root / "output")
```

### 2. 清理遗留的根目录文件夹

**添加到 CLI**: `main.py`

```python
@cli.command("clean-root")
@click.option("--confirm", is_flag=True, help="Skip confirmation")
def clean_root_pipelines(_ctx: click.Context, confirm: bool) -> None:
    """Clean up accidentally created pipeline folders in project root."""
    import shutil
    
    root = Path.cwd()
    pattern = "pipeline-*"
    
    matches = list(root.glob(pattern))
    if not matches:
        console.print("[green]No root pipeline folders found[/green]")
        return
    
    console.print(f"[yellow]Found {len(matches)} pipeline folder(s) in root:[/yellow]")
    for p in matches:
        console.print(f"  - {p.name}")
    
    if not confirm:
        if not click.confirm("Delete these folders?"):
            console.print("[yellow]Cancelled[/yellow]")
            return
    
    for p in matches:
        shutil.rmtree(p)
        console.print(f"[green]✓[/green] Deleted {p.name}")
```

---

## 方案 C: 增加 @docs 文档修改能力 (P2 - 新增需求)

### C1. 需求分析

**目标**: 让 Agent 能够修改 `@docs` 目录下的现有文档，而不仅仅创建新交付物

**应用场景**:
1. 更新现有架构文档
2. 补充 API 文档
3. 修订设计规范
4. 同步代码与文档

**安全考虑**:
- ⚠️ 破坏 work_dir 隔离机制
- ⚠️ 需要严格的路径访问控制
- ⚠️ 需要文件备份机制
- ⚠️ 需要明确的修改审批流程

### C2. 技术方案设计

#### 方案 C1: 扩展工具集 (推荐 - 渐进式)

**核心思想**: 参考 Kimi CLI 的内置文件工具，创建受控的文件操作工具

**Kimi CLI 内置工具**:
```yaml
# kimi_cli.tools.file 模块提供
- ReadFile        # 读取文件
- WriteFile       # 写入文件
- StrReplaceFile  # 字符串替换
- Glob            # 文件搜索
- Grep            # 内容搜索
```

**实现步骤**:

##### Step 1: 创建 ReadDocsFileTool

**新建文件**: `autoBMAD/docuswarm/tools/read_docs_file.py`

```python
"""ReadDocsFileTool - 读取 @docs 目录文件的工具"""

from __future__ import annotations

from pathlib import Path
from typing import override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class ReadDocsFileParams(BaseModel):
    """Parameters for reading docs file.
    
    Attributes:
        file_path: Relative path from docs root (e.g., 'architecture/system-design.md')
    """
    
    file_path: str = Field(
        description="Relative path from docs root, e.g., 'architecture/system-design.md'"
    )


class ReadDocsFileTool(CallableTool2[ReadDocsFileParams]):
    """Tool for reading files from @docs directory.
    
    This tool provides read-only access to project documentation.
    It only allows reading files within the docs/ directory for safety.
    """
    
    name: str = "read_docs_file"
    description: str = "Read content from a file in the @docs directory"
    params: type[ReadDocsFileParams] = ReadDocsFileParams
    
    def __init__(self, project_root: Path):
        """Initialize with project root path.
        
        Args:
            project_root: Root directory of the project (contains docs/)
        """
        super().__init__()
        self.docs_root = project_root / "docs"
    
    @override
    async def __call__(self, params: ReadDocsFileParams) -> ToolReturnValue:
        """Read file from docs directory.
        
        Args:
            params: Validated parameters with file_path
        
        Returns:
            ToolOk with file content or ToolError if failed
        """
        try:
            # Construct full path
            file_path = self.docs_root / params.file_path
            
            # Security check 1: Resolve symlinks and check it's under docs/
            resolved_path = file_path.resolve()
            docs_root_resolved = self.docs_root.resolve()
            
            if not str(resolved_path).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.file_path} is outside docs/ directory",
                    brief="Access denied - path traversal attempt"
                )
            
            # Security check 2: File must exist and be a file
            if not resolved_path.exists():
                return ToolError(
                    output="",
                    message=f"File not found: {params.file_path}",
                    brief="File not found"
                )
            
            if not resolved_path.is_file():
                return ToolError(
                    output="",
                    message=f"Not a file: {params.file_path}",
                    brief="Not a file"
                )
            
            # Read file content
            async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
                content = await f.read()
            
            return ToolOk(output=f"Content of {params.file_path}:\n\n{content}")
            
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to read file"
            )
```

##### Step 2: 创建 UpdateDocsFileTool

**新建文件**: `autoBMAD/docuswarm/tools/update_docs_file.py`

```python
"""UpdateDocsFileTool - 更新 @docs 目录文件的工具"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class UpdateDocsFileParams(BaseModel):
    """Parameters for updating docs file.
    
    Attributes:
        file_path: Relative path from docs root
        old_content: Original content (for verification)
        new_content: New content to write
        create_backup: Whether to create backup (default: True)
    """
    
    file_path: str = Field(
        description="Relative path from docs root, e.g., 'architecture/system-design.md'"
    )
    old_content: str = Field(
        description="Original content snippet (for verification, first 500 chars)"
    )
    new_content: str = Field(
        description="Complete new content to write to the file"
    )
    create_backup: bool = Field(
        default=True,
        description="Whether to create a backup before updating"
    )


class UpdateDocsFileTool(CallableTool2[UpdateDocsFileParams]):
    """Tool for updating files in @docs directory.
    
    This tool provides controlled write access to project documentation.
    It includes safety checks:
    - Content verification before update
    - Automatic backup creation
    - Path traversal prevention
    - Atomic write operation
    """
    
    name: str = "update_docs_file"
    description: str = "Update content of a file in the @docs directory"
    params: type[UpdateDocsFileParams] = UpdateDocsFileParams
    
    def __init__(self, project_root: Path, backup_dir: Path | None = None):
        """Initialize with project root and backup directory.
        
        Args:
            project_root: Root directory of the project (contains docs/)
            backup_dir: Directory for backups (default: docs/.backups/)
        """
        super().__init__()
        self.docs_root = project_root / "docs"
        self.backup_dir = backup_dir or (self.docs_root / ".backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    @override
    async def __call__(self, params: UpdateDocsFileParams) -> ToolReturnValue:
        """Update file in docs directory.
        
        Args:
            params: Validated parameters
        
        Returns:
            ToolOk if successful, ToolError if failed
        """
        try:
            # Construct full path
            file_path = self.docs_root / params.file_path
            
            # Security check 1: Path traversal prevention
            resolved_path = file_path.resolve()
            docs_root_resolved = self.docs_root.resolve()
            
            if not str(resolved_path).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.file_path} is outside docs/",
                    brief="Access denied"
                )
            
            # Check if file exists
            if not resolved_path.exists():
                return ToolError(
                    output="",
                    message=f"File not found: {params.file_path}",
                    brief="File not found"
                )
            
            # Read current content for verification
            async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
                current_content = await f.read()
            
            # Verify old_content matches (first 500 chars)
            current_preview = current_content[:500]
            if params.old_content not in current_preview:
                return ToolError(
                    output="",
                    message=(
                        f"Content verification failed. "
                        f"The file may have been modified by another process. "
                        f"Please read the file again and retry."
                    ),
                    brief="Content verification failed"
                )
            
            # Create backup if requested
            if params.create_backup:
                timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
                backup_name = f"{Path(params.file_path).stem}_{timestamp}.bak"
                backup_path = self.backup_dir / backup_name
                
                async with aiofiles.open(backup_path, "w", encoding="utf-8") as f:
                    await f.write(current_content)
            
            # Write new content (atomic write pattern)
            temp_path = resolved_path.with_suffix(resolved_path.suffix + ".tmp")
            
            try:
                async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                    await f.write(params.new_content)
                
                # Atomic rename
                temp_path.replace(resolved_path)
                
                backup_info = f" (backup created: {backup_name})" if params.create_backup else ""
                return ToolOk(
                    output=f"Successfully updated {params.file_path}{backup_info}"
                )
            
            finally:
                # Cleanup temp file if it still exists
                if temp_path.exists():
                    temp_path.unlink()
        
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to update file"
            )
```

##### Step 3: 创建 ListDocsFilesTool

**新建文件**: `autoBMAD/docuswarm/tools/list_docs_files.py`

```python
"""ListDocsFilesTool - 列出 @docs 目录文件的工具"""

from __future__ import annotations

from pathlib import Path
from typing import override

from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class ListDocsFilesParams(BaseModel):
    """Parameters for listing docs files.
    
    Attributes:
        directory: Relative directory path from docs root (default: '.')
        pattern: Glob pattern for filtering files (default: '*.md')
        recursive: Whether to search recursively (default: True)
    """
    
    directory: str = Field(
        default=".",
        description="Relative directory path from docs root, e.g., 'architecture'"
    )
    pattern: str = Field(
        default="*.md",
        description="Glob pattern for filtering files, e.g., '*.md' or '**/*.yaml'"
    )
    recursive: bool = Field(
        default=True,
        description="Whether to search recursively in subdirectories"
    )


class ListDocsFilesTool(CallableTool2[ListDocsFilesParams]):
    """Tool for listing files in @docs directory.
    
    This tool helps agents discover available documentation files.
    """
    
    name: str = "list_docs_files"
    description: str = "List files in the @docs directory with glob pattern support"
    params: type[ListDocsFilesParams] = ListDocsFilesParams
    
    def __init__(self, project_root: Path):
        """Initialize with project root path.
        
        Args:
            project_root: Root directory of the project (contains docs/)
        """
        super().__init__()
        self.docs_root = project_root / "docs"
    
    @override
    async def __call__(self, params: ListDocsFilesParams) -> ToolReturnValue:
        """List files in docs directory.
        
        Args:
            params: Validated parameters
        
        Returns:
            ToolOk with file list or ToolError if failed
        """
        try:
            # Construct target directory
            target_dir = self.docs_root / params.directory
            
            # Security check: Path traversal prevention
            resolved_dir = target_dir.resolve()
            docs_root_resolved = self.docs_root.resolve()
            
            if not str(resolved_dir).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.directory} is outside docs/",
                    brief="Access denied"
                )
            
            if not resolved_dir.exists():
                return ToolError(
                    output="",
                    message=f"Directory not found: {params.directory}",
                    brief="Directory not found"
                )
            
            # Collect files
            if params.recursive:
                pattern = f"**/{params.pattern}"
            else:
                pattern = params.pattern
            
            files = sorted(resolved_dir.glob(pattern))
            
            # Convert to relative paths from docs root
            relative_files = [
                str(f.relative_to(self.docs_root))
                for f in files
                if f.is_file()
            ]
            
            if not relative_files:
                return ToolOk(
                    output=f"No files found matching pattern '{params.pattern}' in {params.directory}"
                )
            
            file_list = "\n".join(f"- {f}" for f in relative_files)
            return ToolOk(
                output=f"Found {len(relative_files)} file(s) in {params.directory}:\n\n{file_list}"
            )
        
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to list files"
            )
```

##### Step 4: 注册工具到 independent_agent.yaml

**修改文件**: `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`

```yaml
# Agent file for Independent Agent
# This file configures the tools available to the Independent Agent
# Format follows kimi-agent-sdk agent_file specification

version: 1

agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.update_context:UpdateContextTool"
    # 新增: @docs 文档操作工具
    - "docuswarm.tools.read_docs_file:ReadDocsFileTool"
    - "docuswarm.tools.update_docs_file:UpdateDocsFileTool"
    - "docuswarm.tools.list_docs_files:ListDocsFilesTool"
```

##### Step 5: 在 IndependentAgent 中初始化工具

**修改文件**: `autoBMAD/docuswarm/agents/independent.py`

**位置**: `__init__` 方法

```python
def __init__(
    self,
    config: AgentConfig,
    session_manager: KimiSessionManager,
    node_id: str = "dev",
    project_root: Path | None = None,
):
    """Initialize the independent agent.
    
    Args:
        config: Agent configuration
        session_manager: Session manager for LLM interactions
        node_id: Node identifier
        project_root: Root directory of the project
    """
    super().__init__(config, session_manager=session_manager)
    self.node_id = node_id
    self.project_root = project_root or Path.cwd()
    
    # Story 11.1: Instance variables
    self._agent_file: Path | None = None
    self._work_dir: Path | None = None
    
    # 新增: 注册 @docs 工具 (需要 project_root)
    self._register_docs_tools()
    
    # Load persona
    try:
        self.persona = PersonaLoader.load(
            node_id=node_id,
            project_root=self.project_root,
            use_cache=True,
        )
    except Exception as e:
        raise IndependentAgentError(f"Failed to load persona: {e}") from e

def _register_docs_tools(self) -> None:
    """Register tools for @docs directory access.
    
    This method dynamically instantiates tools that require project_root.
    """
    from autoBMAD.docuswarm.tools.read_docs_file import ReadDocsFileTool
    from autoBMAD.docuswarm.tools.update_docs_file import UpdateDocsFileTool
    from autoBMAD.docuswarm.tools.list_docs_files import ListDocsFilesTool
    
    # Get project root (should be d:\GITHUB\DocuSwarm)
    # project_root points to autoBMAD, so parent is DocuSwarm root
    docs_project_root = self.project_root.parent
    
    # Instantiate tools with project_root
    self.read_docs_tool = ReadDocsFileTool(project_root=docs_project_root)
    self.update_docs_tool = UpdateDocsFileTool(project_root=docs_project_root)
    self.list_docs_tool = ListDocsFilesTool(project_root=docs_project_root)
    
    # Register tools to session_manager (if supported by Kimi SDK)
    # Note: Kimi SDK loads tools from agent_file, so we need to ensure
    # these tool instances are passed to the session when created
    
    self.logger.info(
        "registered_docs_tools",
        docs_root=str(docs_project_root / "docs"),
        tools=["read_docs_file", "update_docs_file", "list_docs_files"]
    )
```

**注意**: Kimi SDK 通过 `agent_file` 加载工具，工具需要无参构造函数。因此需要调整工具设计：

**调整后的工具设计** (无参构造函数版本):

```python
# tools/read_docs_file.py - 最终版本
class ReadDocsFileTool(CallableTool2[ReadDocsFileParams]):
    name: str = "read_docs_file"
    description: str = "Read content from a file in the @docs directory"
    params: type[ReadDocsFileParams] = ReadDocsFileParams
    
    def __init__(self):
        """Initialize without parameters (required by Kimi SDK)."""
        super().__init__()
        # Dynamically compute project_root
        # This assumes the tool is imported from autoBMAD/docuswarm/tools/
        self.docs_root = self._compute_docs_root()
    
    def _compute_docs_root(self) -> Path:
        """Compute docs root directory.
        
        Returns:
            Path to docs/ directory
        """
        # Get autoBMAD/docuswarm/tools/read_docs_file.py location
        current_file = Path(__file__)
        # Navigate: tools/ -> docuswarm/ -> autoBMAD/ -> DocuSwarm/ -> docs/
        project_root = current_file.parent.parent.parent.parent
        return project_root / "docs"
```

同样地，`UpdateDocsFileTool` 和 `ListDocsFilesTool` 也需要调整为无参构造函数。

---

## 方案 D: 节点Agent创建多文档能力 (P2 - 参考 _bmad)

### D1. 需求分析

**参考 BMAD 模式**:

从 `_bmad` 的实践中学习：
1. **Tech Writer Agent**: 专职文档创建角色
2. **Document Project Workflow**: 系统化文档生成流程
3. **Template 机制**: 预定义文档模板 (index-template.md, deep-dive-template.md 等)
4. **Documentation Standards**: 统一的文档质量标准 (CommonMark, Mermaid, 无时间估算)

**DocuSwarm 的应用场景**:

1. **Analyst 节点**: 创建多个分析报告
   - Market Research Report
   - Competitor Analysis
   - User Persona Documents
   - Risk Assessment

2. **Architect 节点**: 创建架构文档集
   - System Architecture Overview
   - Component Design Documents
   - API Specifications
   - Database Schema Design

3. **Dev 节点**: 创建实现文档
   - Implementation Plan
   - Code Review Checklist
   - Testing Strategy
   - Deployment Guide

**当前限制**:
- ❌ Agent 只能调用一次 `create_deliverable`，创建单一文档
- ❌ 无文档模板机制
- ❌ 无文档质量标准引用
- ❌ 无多文档协调机制

### D2. 技术方案设计

#### 方案 D1: 扩展 CreateDeliverableTool 支持多文档创建

**核心思想**: 允许 Agent 在一次执行中创建多个结构化的文档

##### Step 1: 创建文档模板系统

**新建目录**: `autoBMAD/docuswarm/templates/`

**新建文件**: `autoBMAD/docuswarm/templates/analyst_templates.yaml`

```yaml
# Analyst 节点文档模板配置
version: 1.0
node_id: analyst

templates:
  - template_id: market_research
    title: Market Research Report
    filename_pattern: "market-research-report.md"
    description: "Comprehensive market analysis and trends"
    sections:
      - heading: Executive Summary
        required: true
      - heading: Market Overview
        required: true
      - heading: Target Segments
        required: true
      - heading: Competitive Landscape
        required: true
      - heading: Market Opportunities
        required: true
      - heading: Recommendations
        required: true

  - template_id: user_personas
    title: User Persona Analysis
    filename_pattern: "user-personas.md"
    description: "Detailed user persona definitions"
    sections:
      - heading: Overview
        required: true
      - heading: Primary Personas
        required: true
      - heading: Secondary Personas
        required: false
      - heading: User Journey Maps
        required: true

  - template_id: risk_assessment
    title: Risk Assessment Report
    filename_pattern: "risk-assessment.md"
    description: "Project risk identification and mitigation"
    sections:
      - heading: Risk Overview
        required: true
      - heading: Technical Risks
        required: true
      - heading: Business Risks
        required: true
      - heading: Mitigation Strategies
        required: true

# Documentation standards reference
standards:
  style_guide: "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"
  diagram_format: "mermaid"
  no_time_estimates: true
  commonmark_strict: true
```

**新建文件**: `autoBMAD/docuswarm/templates/architect_templates.yaml`

```yaml
# Architect 节点文档模板配置
version: 1.0
node_id: architect

templates:
  - template_id: system_architecture
    title: System Architecture Overview
    filename_pattern: "system-architecture.md"
    description: "High-level system architecture"
    sections:
      - heading: Architecture Vision
        required: true
      - heading: System Components
        required: true
      - heading: Data Flow
        required: true
      - heading: Technology Stack
        required: true
      - heading: Architecture Diagrams
        required: true
        note: "Use Mermaid flowchart or C4 model"

  - template_id: api_specification
    title: API Specification
    filename_pattern: "api-specification.md"
    description: "RESTful API design and contracts"
    sections:
      - heading: API Overview
        required: true
      - heading: Authentication
        required: true
      - heading: Endpoints
        required: true
      - heading: Data Models
        required: true
      - heading: Error Handling
        required: true

  - template_id: database_schema
    title: Database Schema Design
    filename_pattern: "database-schema.md"
    description: "Database structure and relationships"
    sections:
      - heading: Schema Overview
        required: true
      - heading: Entity Definitions
        required: true
      - heading: Relationships
        required: true
      - heading: Indexes and Constraints
        required: true
      - heading: Migration Strategy
        required: true

standards:
  style_guide: "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"
  diagram_format: "mermaid"
  no_time_estimates: true
  commonmark_strict: true
```

##### Step 2: 创建多文档创建工具

**新建文件**: `autoBMAD/docuswarm/tools/create_document_set.py`

```python
"""CreateDocumentSetTool - 创建多个结构化文档的工具"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, override

import aiofiles
import yaml
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class DocumentSpec(BaseModel):
    """Single document specification.
    
    Attributes:
        template_id: Template identifier from templates YAML
        title: Document title (overrides template default)
        content: Document content in Markdown
        metadata: Additional metadata
    """
    
    template_id: str = Field(description="Template ID from node templates")
    title: str | None = Field(default=None, description="Custom title (optional)")
    content: str = Field(description="Document content in Markdown")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CreateDocumentSetParams(BaseModel):
    """Parameters for creating a document set.
    
    Attributes:
        documents: List of documents to create
        node_id: Node identifier (analyst, architect, etc.)
    """
    
    documents: list[DocumentSpec] = Field(
        description="List of documents to create",
        min_items=1,
        max_items=10
    )
    node_id: str = Field(
        default="unknown",
        description="Node identifier for template loading"
    )


def _slugify_filename(title: str) -> str:
    """Convert title to a valid filename slug.
    
    Args:
        title: The document title.
    
    Returns:
        A slugified filename with .md extension.
    """
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.md"


class CreateDocumentSetTool(CallableTool2[CreateDocumentSetParams]):
    """Tool for creating multiple structured documents based on templates.
    
    This tool extends create_deliverable to support:
    - Multiple document creation in one call
    - Template-based validation
    - Documentation standards enforcement
    - Mermaid diagram validation
    """
    
    name: str = "create_document_set"
    description: str = "Create multiple structured documents based on node templates"
    params: type[CreateDocumentSetParams] = CreateDocumentSetParams
    
    def __init__(self):
        """Initialize the tool with template loading."""
        super().__init__()
        self.templates_cache: dict[str, Any] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all node template configurations."""
        # Compute templates directory
        current_file = Path(__file__)
        templates_dir = current_file.parent.parent / "templates"
        
        if not templates_dir.exists():
            return
        
        # Load all YAML template files
        for template_file in templates_dir.glob("*_templates.yaml"):
            try:
                with open(template_file, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    node_id = config.get("node_id")
                    if node_id:
                        self.templates_cache[node_id] = config
            except Exception:
                pass  # Skip invalid template files
    
    def _get_template(self, node_id: str, template_id: str) -> dict[str, Any] | None:
        """Get template configuration.
        
        Args:
            node_id: Node identifier
            template_id: Template identifier
        
        Returns:
            Template config or None if not found
        """
        node_templates = self.templates_cache.get(node_id)
        if not node_templates:
            return None
        
        for template in node_templates.get("templates", []):
            if template.get("template_id") == template_id:
                return template
        
        return None
    
    def _validate_content_structure(
        self,
        content: str,
        template: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate document content against template structure.
        
        Args:
            content: Document content
            template: Template configuration
        
        Returns:
            (is_valid, error_message)
        """
        required_sections = [
            s["heading"] 
            for s in template.get("sections", []) 
            if s.get("required", False)
        ]
        
        for section in required_sections:
            # Check for heading (both ## and # formats)
            if f"## {section}" not in content and f"# {section}" not in content:
                return False, f"Missing required section: '{section}'"
        
        return True, ""
    
    def _validate_mermaid_diagrams(self, content: str) -> tuple[bool, str]:
        """Validate Mermaid diagram syntax.
        
        Args:
            content: Document content
        
        Returns:
            (is_valid, error_message)
        """
        # Extract mermaid code blocks
        mermaid_pattern = r"```mermaid\n(.*?)\n```"
        import re
        diagrams = re.findall(mermaid_pattern, content, re.DOTALL)
        
        for diagram in diagrams:
            # Basic validation: must start with diagram type
            first_line = diagram.strip().split("\n")[0]
            valid_types = [
                "flowchart", "sequenceDiagram", "classDiagram",
                "erDiagram", "stateDiagram-v2", "gitGraph", "graph"
            ]
            
            if not any(first_line.startswith(t) for t in valid_types):
                return False, f"Invalid Mermaid diagram: missing diagram type. Found: '{first_line}'"
        
        return True, ""
    
    @override
    async def __call__(self, params: CreateDocumentSetParams) -> ToolReturnValue:
        """Create multiple documents with validation.
        
        Args:
            params: The validated parameters
        
        Returns:
            ToolOk on success, ToolError on failure
        """
        try:
            created_files: list[str] = []
            validation_warnings: list[str] = []
            
            for doc_spec in params.documents:
                # Get template
                template = self._get_template(params.node_id, doc_spec.template_id)
                
                # Determine filename
                if template and "filename_pattern" in template:
                    filename = template["filename_pattern"]
                elif doc_spec.title:
                    filename = _slugify_filename(doc_spec.title)
                else:
                    filename = _slugify_filename(doc_spec.template_id)
                
                # Validate content structure
                if template:
                    is_valid, error_msg = self._validate_content_structure(
                        doc_spec.content,
                        template
                    )
                    if not is_valid:
                        validation_warnings.append(f"{filename}: {error_msg}")
                
                # Validate Mermaid diagrams
                is_valid, error_msg = self._validate_mermaid_diagrams(doc_spec.content)
                if not is_valid:
                    validation_warnings.append(f"{filename}: {error_msg}")
                
                # Write file
                file_path = Path.cwd() / filename
                async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                    await f.write(doc_spec.content)
                
                created_files.append(filename)
            
            # Build result message
            result_msg = f"Created {len(created_files)} document(s):\n"
            result_msg += "\n".join(f"  - {f}" for f in created_files)
            
            if validation_warnings:
                result_msg += "\n\n⚠️ Validation Warnings:\n"
                result_msg += "\n".join(f"  - {w}" for w in validation_warnings)
            
            return ToolOk(output=result_msg)
        
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to create document set"
            )
```

##### Step 3: 更新 independent_agent.yaml

**修改文件**: `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`

```yaml
version: 1

agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.create_document_set:CreateDocumentSetTool"  # 新增
    - "docuswarm.tools.update_context:UpdateContextTool"
    # @docs 文档操作工具
    - "docuswarm.tools.read_docs_file:ReadDocsFileTool"
    - "docuswarm.tools.update_docs_file:UpdateDocsFileTool"
    - "docuswarm.tools.list_docs_files:ListDocsFilesTool"
```

##### Step 4: 在 Persona 中引用文档标准

**修改文件**: `autoBMAD/docuswarm/agents/persona.py`

在 Persona 加载时，自动注入文档标准引用：

```python
@staticmethod
def load(node_id: str, project_root: Path, use_cache: bool = True) -> Persona:
    """Load persona for a given node.
    
    Args:
        node_id: Node identifier (e.g., 'analyst', 'architect')
        project_root: Project root directory
        use_cache: Whether to use cached persona
    
    Returns:
        Loaded Persona instance
    """
    # ... existing code ...
    
    # 新增: 注入文档标准引用
    doc_standards_path = project_root.parent / "_bmad" / "_memory" / "tech-writer-sidecar" / "documentation-standards.md"
    
    if doc_standards_path.exists():
        persona_content += f"\n\n## Documentation Standards\n\n"
        persona_content += f"When creating deliverables, follow: `{doc_standards_path}`\n\n"
        persona_content += "Key requirements:\n"
        persona_content += "- CommonMark strict compliance\n"
        persona_content += "- NO time estimates\n"
        persona_content += "- Mermaid diagrams for visualizations\n"
        persona_content += "- Task-oriented structure\n"
    
    # ... rest of existing code ...
```

### D3. 使用示例

**Context File 示例**:

```markdown
# Analyst Task

Analyze the market for a new SaaS project management tool.

Create the following deliverables using `create_document_set`:

1. **Market Research Report** (template: market_research)
   - Include competitive landscape with at least 3 competitors
   - Use Mermaid diagram for market segmentation
   - Identify 2-3 key opportunities

2. **User Persona Analysis** (template: user_personas)
   - Define 3 primary personas
   - Include user journey maps
   - Use Mermaid sequence diagrams for journeys

3. **Risk Assessment Report** (template: risk_assessment)
   - Identify technical and business risks
   - Provide mitigation strategies
   - Use risk matrix visualization

All documents must follow CommonMark standards and include no time estimates.
```

**Agent 执行流程**:

```
1. IndependentAgent.execute() 接收 task

2. LLM 理解需求，生成文档内容

3. 调用 create_document_set({
     documents: [
       {
         template_id: "market_research",
         content: "# Market Research Report\n\n## Executive Summary\n..."
       },
       {
         template_id: "user_personas",
         content: "# User Persona Analysis\n\n## Overview\n..."
       },
       {
         template_id: "risk_assessment",
         content: "# Risk Assessment Report\n\n## Risk Overview\n..."
       }
     ],
     node_id: "analyst"
   })

4. CreateDocumentSetTool 验证:
   - 检查必需章节是否存在
   - 验证 Mermaid 图表语法
   - 确保无时间估算

5. 创建文件到 autoBMAD/output/{pipeline_id}/:
   - market-research-report.md
   - user-personas.md
   - risk-assessment.md

6. 返回成功消息 + 验证警告（如有）
```

### D4. 模板管理

**模板查看命令** (CLI 扩展):

```python
# main.py - 新增命令
@cli.command("list-templates")
@click.option("--node", help="Filter by node ID")
def list_templates(_ctx: click.Context, node: str | None) -> None:
    """List available document templates."""
    from autoBMAD.docuswarm.tools.create_document_set import CreateDocumentSetTool
    
    tool = CreateDocumentSetTool()
    
    if node:
        templates = tool.templates_cache.get(node, {}).get("templates", [])
        console.print(f"\n[bold]Templates for {node}:[/bold]\n")
    else:
        console.print("\n[bold]All Templates:[/bold]\n")
        templates = []
        for node_id, config in tool.templates_cache.items():
            console.print(f"\n[cyan]{node_id}[/cyan]:")
            for t in config.get("templates", []):
                console.print(f"  • {t['template_id']}: {t['title']}")
        return
    
    for template in templates:
        console.print(f"\n[green]{template['template_id']}[/green]")
        console.print(f"  Title: {template['title']}")
        console.print(f"  Description: {template['description']}")
        console.print(f"  Required Sections:")
        for section in template.get("sections", []):
            req = "✓" if section.get("required") else " "
            console.print(f"    [{req}] {section['heading']}")
```

### D5. 单元测试

**测试文件**: `tests/unit/test_create_document_set.py`

```python
import pytest
from pathlib import Path
from autoBMAD.docuswarm.tools.create_document_set import (
    CreateDocumentSetTool,
    CreateDocumentSetParams,
    DocumentSpec
)


class TestCreateDocumentSetTool:
    """Test CreateDocumentSetTool functionality."""
    
    @pytest.mark.asyncio
    async def test_create_multiple_documents(self, tmp_path, monkeypatch):
        """Test creating multiple documents successfully."""
        # Change to tmp directory
        monkeypatch.chdir(tmp_path)
        
        tool = CreateDocumentSetTool()
        
        params = CreateDocumentSetParams(
            documents=[
                DocumentSpec(
                    template_id="market_research",
                    content="# Market Research Report\n\n## Executive Summary\n\nContent here."
                ),
                DocumentSpec(
                    template_id="user_personas",
                    content="# User Personas\n\n## Overview\n\nPersona content."
                )
            ],
            node_id="analyst"
        )
        
        result = await tool(params)
        
        # Verify success
        assert result.output is not None
        assert "Created 2 document(s)" in result.output
        
        # Verify files created
        assert (tmp_path / "market-research-report.md").exists()
        assert (tmp_path / "user-personas.md").exists()
    
    @pytest.mark.asyncio
    async def test_validation_warnings_for_missing_sections(self, tmp_path, monkeypatch):
        """Test that missing required sections generate warnings."""
        monkeypatch.chdir(tmp_path)
        
        tool = CreateDocumentSetTool()
        
        # Create document missing required section
        params = CreateDocumentSetParams(
            documents=[
                DocumentSpec(
                    template_id="market_research",
                    content="# Market Research Report\n\n## Only One Section"
                )
            ],
            node_id="analyst"
        )
        
        result = await tool(params)
        
        # Should succeed but with warnings
        assert result.output is not None
        assert "⚠️ Validation Warnings" in result.output
    
    @pytest.mark.asyncio
    async def test_mermaid_diagram_validation(self, tmp_path, monkeypatch):
        """Test Mermaid diagram syntax validation."""
        monkeypatch.chdir(tmp_path)
        
        tool = CreateDocumentSetTool()
        
        # Invalid Mermaid (missing diagram type)
        params = CreateDocumentSetParams(
            documents=[
                DocumentSpec(
                    template_id="market_research",
                    content="""# Report

```mermaid
A --> B
```
"""
                )
            ],
            node_id="analyst"
        )
        
        result = await tool(params)
        
        # Should warn about invalid Mermaid
        assert "⚠️ Validation Warnings" in result.output
        assert "Invalid Mermaid diagram" in result.output
```

### D6. 与 BMAD 对齐

**借鉴 BMAD 的最佳实践**:

1. **Documentation Standards 集成**
   ```python
   # 在 Persona 加载时自动引用
   standards_ref = "_bmad/_memory/tech-writer-sidecar/documentation-standards.md"
   ```

2. **Template-driven Creation**
   ```yaml
   # 每个节点都有模板配置
   analyst_templates.yaml
   architect_templates.yaml
   dev_templates.yaml
   ```

3. **Quality Validation**
   ```python
   # 自动验证:
   - CommonMark compliance
   - Required sections present
   - Mermaid diagram syntax
   - No time estimates
   ```

4. **Multi-document Support**
   ```python
   # 单次调用创建多个文档
   create_document_set(documents=[...])
   ```

### C3. 使用示例

**Prompt 示例**:

```markdown
# context_file.md

请更新架构文档 @docs/architecture/system-design.md:

1. 先使用 list_docs_files 列出 architecture 目录的文件
2. 使用 read_docs_file 读取 architecture/system-design.md
3. 在 "## 数据库设计" 章节后添加新的缓存层设计
4. 使用 update_docs_file 保存更新

同时创建一个新的交付物 architecture-update-summary.md 总结本次更新。
```

**Agent 执行流程**:

```
1. list_docs_files(directory="architecture", pattern="*.md")
   → 返回文件列表

2. read_docs_file(file_path="architecture/system-design.md")
   → 读取当前内容

3. LLM 生成新内容 (基于读取的内容 + 需求)

4. update_docs_file(
     file_path="architecture/system-design.md",
     old_content="## 数据库设计...",  # 前500字符
     new_content="<完整的新内容>",
     create_backup=True
   )
   → 更新文件，自动备份到 docs/.backups/

5. create_deliverable(
     title="Architecture Update Summary",
     content="..."
   )
   → 创建交付物到 autoBMAD/output/{pipeline_id}/
```

### C4. 安全机制

#### 1. 路径访问控制

```python
# 所有工具都包含路径验证
resolved_path = file_path.resolve()
if not str(resolved_path).startswith(str(docs_root_resolved)):
    return ToolError(message="Access denied")
```

#### 2. 自动备份

```python
# 每次更新前自动备份
backup_path = docs/.backups/{filename}_{timestamp}.bak
```

#### 3. 内容验证

```python
# 更新前验证原内容匹配
if params.old_content not in current_preview:
    return ToolError(message="Content verification failed")
```

#### 4. 原子写入

```python
# 使用临时文件 + 原子重命名
temp_path.write(new_content)
temp_path.replace(target_path)
```

### C5. 配置选项

**新增配置**: `autoBMAD/docuswarm/config.py`

```python
@dataclass(frozen=True)
class Config:
    ...
    # 新增: @docs 修改权限控制
    enable_docs_modification: bool = field(default=False)
    docs_backup_enabled: bool = field(default=True)
    docs_backup_dir: Path = field(default_factory=lambda: Path("docs/.backups"))
```

**环境变量控制**:

```bash
# .env
DOCUSWARM_ENABLE_DOCS_MODIFICATION=true
DOCUSWARM_DOCS_BACKUP_ENABLED=true
```

### C6. 单元测试

**测试文件**: `tests/unit/test_docs_tools.py`

```python
import pytest
from pathlib import Path
from autoBMAD.docuswarm.tools.read_docs_file import ReadDocsFileTool
from autoBMAD.docuswarm.tools.update_docs_file import UpdateDocsFileTool
from autoBMAD.docuswarm.tools.list_docs_files import ListDocsFilesTool


class TestReadDocsFileTool:
    """Test ReadDocsFileTool functionality."""
    
    @pytest.mark.asyncio
    async def test_read_existing_file(self, tmp_path):
        """Test reading an existing file."""
        # Setup
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        test_file = docs_root / "test.md"
        test_file.write_text("# Test Content")
        
        tool = ReadDocsFileTool(project_root=tmp_path)
        
        # Execute
        from autoBMAD.docuswarm.tools.read_docs_file import ReadDocsFileParams
        result = await tool(ReadDocsFileParams(file_path="test.md"))
        
        # Verify
        assert result.output is not None
        assert "# Test Content" in result.output
    
    @pytest.mark.asyncio
    async def test_reject_path_traversal(self, tmp_path):
        """Test that path traversal is rejected."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        tool = ReadDocsFileTool(project_root=tmp_path)
        
        # Try to access parent directory
        from autoBMAD.docuswarm.tools.read_docs_file import ReadDocsFileParams
        result = await tool(ReadDocsFileParams(file_path="../secret.md"))
        
        # Verify rejection
        assert result.message is not None
        assert "Access denied" in result.message


class TestUpdateDocsFileTool:
    """Test UpdateDocsFileTool functionality."""
    
    @pytest.mark.asyncio
    async def test_update_file_with_backup(self, tmp_path):
        """Test updating a file with backup creation."""
        # Setup
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        test_file = docs_root / "test.md"
        original_content = "# Original Content\n\nSome text."
        test_file.write_text(original_content)
        
        tool = UpdateDocsFileTool(project_root=tmp_path)
        
        # Execute
        from autoBMAD.docuswarm.tools.update_docs_file import UpdateDocsFileParams
        result = await tool(UpdateDocsFileParams(
            file_path="test.md",
            old_content="# Original Content",
            new_content="# Updated Content\n\nNew text.",
            create_backup=True
        ))
        
        # Verify
        assert result.output is not None
        assert "Successfully updated" in result.output
        assert test_file.read_text() == "# Updated Content\n\nNew text."
        
        # Verify backup created
        backup_files = list((docs_root / ".backups").glob("test_*.bak"))
        assert len(backup_files) == 1
    
    @pytest.mark.asyncio
    async def test_content_verification_failure(self, tmp_path):
        """Test that content verification prevents incorrect updates."""
        # Setup
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        test_file = docs_root / "test.md"
        test_file.write_text("# Current Content")
        
        tool = UpdateDocsFileTool(project_root=tmp_path)
        
        # Execute with wrong old_content
        from autoBMAD.docuswarm.tools.update_docs_file import UpdateDocsFileParams
        result = await tool(UpdateDocsFileParams(
            file_path="test.md",
            old_content="# Wrong Content",  # Doesn't match
            new_content="# New Content"
        ))
        
        # Verify rejection
        assert result.message is not None
        assert "verification failed" in result.message.lower()


class TestListDocsFilesTool:
    """Test ListDocsFilesTool functionality."""
    
    @pytest.mark.asyncio
    async def test_list_files_recursive(self, tmp_path):
        """Test listing files recursively."""
        # Setup
        docs_root = tmp_path / "docs"
        (docs_root / "architecture").mkdir(parents=True)
        (docs_root / "architecture" / "design.md").write_text("content")
        (docs_root / "api.md").write_text("content")
        
        tool = ListDocsFilesTool(project_root=tmp_path)
        
        # Execute
        from autoBMAD.docuswarm.tools.list_docs_files import ListDocsFilesParams
        result = await tool(ListDocsFilesParams(
            directory=".",
            pattern="*.md",
            recursive=True
        ))
        
        # Verify
        assert result.output is not None
        assert "architecture/design.md" in result.output
        assert "api.md" in result.output
```

### C7. 集成测试

**测试文件**: `tests/integration/test_docs_modification.py`

```python
import pytest
import asyncio
from pathlib import Path
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


@pytest.mark.integration
@pytest.mark.timeout(600)
class TestDocsModification:
    """Integration test for @docs modification capability."""
    
    def test_agent_can_modify_docs(self, tmp_path):
        """Test that agent can read and update @docs files."""
        # Setup project structure
        project_root = tmp_path
        docs_dir = project_root / "docs" / "architecture"
        docs_dir.mkdir(parents=True)
        
        test_doc = docs_dir / "test-design.md"
        test_doc.write_text("# Original Design\n\n## Overview\n\nInitial content.")
        
        autoBMAD_root = project_root / "autoBMAD"
        autoBMAD_root.mkdir()
        
        # Prepare context file
        context_file = project_root / "update_request.md"
        context_file.write_text("""
# Task

Please update @docs/architecture/test-design.md:

1. Read the current content using read_docs_file
2. Add a new section "## Implementation" after Overview
3. Update the file using update_docs_file
4. Create a summary deliverable
        """)
        
        # Initialize orchestrator
        db_path = tmp_path / "test.db"
        work_dir = autoBMAD_root / "output"
        
        orchestrator = HybridOrchestrator(
            db_path=str(db_path),
            api_key="test-key",
            work_dir=str(work_dir),
        )
        
        subject_context = {
            "subject": "update_docs",
            "context_file": str(context_file),
            "content": context_file.read_text(),
        }
        
        # Run pipeline
        pipeline_id = asyncio.run(orchestrator.start_pipeline(subject_context))
        
        # Verify: docs file was updated
        updated_content = test_doc.read_text()
        assert "## Implementation" in updated_content
        
        # Verify: backup was created
        backup_files = list((docs_dir.parent / ".backups").glob("test-design_*.bak"))
        assert len(backup_files) > 0
        
        # Verify: deliverable was created
        deliverables = list((work_dir / pipeline_id).glob("*.md"))
        assert len(deliverables) > 0
```

## 总结

### 问题根因

1. **输出目录重复**: `Orchestrator._work_dir` 未初始化 → 使用 `cwd()` → 根目录创建
2. **Context 未传递**: `IndependentAgent` 只提取 `task`，未使用 `context.content`
3. **@docs 修改受限**: Agent 无文件读写工具 → 无法修改现有文档
4. **单文档限制**: Agent 只能创建单一交付物 → 缺乏多文档能力和模板机制

### 解决方案

1. **方案 A**: 在 `Orchestrator.__init__` 初始化 `_work_dir` 为 `autoBMAD/output`
2. **方案 B**: 在 `IndependentAgent.execute()` 提取并使用 `subject_context.content`
3. **方案 C**: 创建 @docs 文档操作工具集 (ReadDocsFile/UpdateDocsFile/ListDocsFiles)
4. **方案 D**: 创建多文档创建能力 (CreateDocumentSet + 模板系统)

### 预期效果

- ✅ 所有交付物统一保存到 `autoBMAD\output\{pipeline_id}\`
- ✅ 每个节点 Agent 接收完整的 `<context_file>` 内容
- ✅ Agent 可以读取、更新、列出 @docs 目录的文档
- ✅ Agent 可以基于模板创建多个结构化文档
- ✅ 文档自动验证 (CommonMark, Mermaid, 章节结构)
- ✅ 引用 BMAD 文档标准 (无时间估算, 任务导向)
- ✅ 自动备份机制防止误操作
- ✅ 路径访问控制保证安全隔离
- ✅ 根目录不再创建意外的 `pipeline-xxx\` 文件夹
- ✅ 单元测试和集成测试全部通过

### 时间估算

- 阶段 1 (work_dir 修复): 20 分钟
- 阶段 2 (context 传递): 30 分钟
- 阶段 3 (@docs 工具开发): 90 分钟
  - ReadDocsFileTool: 20 分钟
  - UpdateDocsFileTool: 30 分钟
  - ListDocsFilesTool: 15 分钟
  - 工具注册与测试: 25 分钟
- 阶段 4 (多文档创建能力): 120 分钟
  - 模板系统设计: 30 分钟
  - CreateDocumentSetTool 开发: 45 分钟
  - Persona 集成: 20 分钟
  - 单元测试: 25 分钟
- 阶段 5 (回归测试): 20 分钟
- **总计**: ~280 分钟 (~4.7 小时)

---

## 文件修改清单

| 文件 | 修改类型 | 描述 | 优先级 |
|------|---------|------|--------|
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | **源码修复** | 添加 work_dir 初始化逻辑 | **P0** |
| `autoBMAD/docuswarm/main.py` | 源码修复 | 传入 work_dir 参数 | P0 |
| `autoBMAD/docuswarm/agents/independent.py` | **源码修复** | 提取并使用 context.content | **P1** |
| `autoBMAD/docuswarm/tools/read_docs_file.py` | **新增工具** | @docs 文件读取工具 | **P2** |
| `autoBMAD/docuswarm/tools/update_docs_file.py` | **新增工具** | @docs 文件更新工具 | **P2** |
| `autoBMAD/docuswarm/tools/list_docs_files.py` | **新增工具** | @docs 文件列表工具 | **P2** |
| `autoBMAD/docuswarm/tools/create_document_set.py` | **新增工具** | 多文档创建工具 | **P2** |
| `autoBMAD/docuswarm/templates/analyst_templates.yaml` | **新增模板** | Analyst 节点文档模板 | P2 |
| `autoBMAD/docuswarm/templates/architect_templates.yaml` | **新增模板** | Architect 节点文档模板 | P2 |
| `autoBMAD/docuswarm/templates/dev_templates.yaml` | **新增模板** | Dev 节点文档模板 | P2 |
| `autoBMAD/docuswarm/agents/configs/independent_agent.yaml` | 配置更新 | 注册所有新工具 | P2 |
| `autoBMAD/docuswarm/agents/persona.py` | 源码扩展 | 注入文档标准引用 | P2 |
| `tests/unit/test_orchestrator_work_dir.py` | **新增测试** | Orchestrator work_dir 单元测试 | P0 |
| `tests/unit/test_independent_agent_context.py` | **新增测试** | IndependentAgent context 单元测试 | P1 |
| `tests/unit/test_docs_tools.py` | **新增测试** | @docs 工具单元测试 | P2 |
| `tests/unit/test_create_document_set.py` | **新增测试** | 多文档创建工具测试 | P2 |
| `tests/integration/test_context_file_transmission.py` | 新增测试 | 端到端集成测试 | P2 |
| `tests/integration/test_docs_modification.py` | **新增测试** | @docs 修改集成测试 | P2 |
| `autoBMAD/docuswarm/config.py` | 配置扩展 | 添加 @docs 修改权限配置 | P2 |
| `autoBMAD/docuswarm/main.py` | 可选功能 | 添加 clean-root 命令 | P3 |
