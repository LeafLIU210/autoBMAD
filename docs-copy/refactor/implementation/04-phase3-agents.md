# Phase 3: Agent 层实施计划

**文档版本**: 1.0
**创建日期**: 2026-01-11
**状态**: Ready for Implementation
**前序阶段**: Phase 2 (控制器层) 必须完成

---

## 1. 实施概览

### 1.1 阶段目标

**核心目标**：
1. 重构所有Agent以继承BaseAgent基类
2. 统一Agent接口，简化异步执行流程
3. 集成Phase 1的SDKExecutor组件
4. 确保与Phase 2控制器层的无缝对接
5. 消除Cancel Scope跨Task错误

**技术目标**：
- 所有Agent继承BaseAgent并实现标准化接口
- 集成TaskGroup管理机制
- 统一SDK调用入口
- 优化异步执行和错误处理

### 1.2 架构定位

```
Layer 1: TaskGroup (AnyIO 容器)
  ↓ 管理
Layer 2: Controller (业务流程决策)
  ↓ 控制
Layer 3: Agent (业务逻辑实现) ← 本阶段
  ↓ 委托
Layer 4: SDK Executor (SDK调用管理) - Phase 1 已完成
```

### 1.3 当前状态分析

**已完成组件**：
- ✅ `agents/base_agent.py` - 基础Agent基类已存在
- ✅ `agents/state_agent.py` - StateAgent已继承BaseAgent
- ✅ `agents/quality_agents.py` - Quality Agents已继承BaseAgent

**需要重构的组件**：
- 🔄 `sm_agent.py` (根目录) → 移动到 `agents/sm_agent.py` 并集成BaseAgent
- 🔄 `dev_agent.py` (根目录) → 移动到 `agents/dev_agent.py` 并集成BaseAgent
- 🔄 `qa_agent.py` (根目录) → 移动到 `agents/qa_agent.py` 并集成BaseAgent

### 1.4 交付物清单

**重构文件**：
```
autoBMAD/epic_automation/
├── agents/
│   ├── base_agent.py             # 现有（需增强）
│   ├── state_agent.py            # 现有（已集成）
│   ├── quality_agents.py         # 现有（已集成）
│   ├── sm_agent.py               # 新建（从根目录迁移）
│   ├── dev_agent.py              # 新建（从根目录迁移）
│   └── qa_agent.py               # 新建（从根目录迁移）
└── 移除旧文件：
    ├── sm_agent.py (根目录)       # 删除
    ├── dev_agent.py (根目录)      # 删除
    └── qa_agent.py (根目录)       # 删除
```

**测试文件**：
```
tests/unit/
├── test_base_agent.py            # 新建
├── test_sm_agent.py              # 新建
├── test_dev_agent.py             # 新建
└── test_qa_agent.py             # 新建

tests/integration/
├── test_agent_controller_integration.py  # 新建
└── test_agent_taskgroup_integration.py    # 新建
```

---

## 2. 详细实施计划

### 2.1 Day 1: BaseAgent增强 + SMAgent重构

#### 2.1.1 增强BaseAgent基类

**目标**: 扩展BaseAgent以支持TaskGroup和SDKExecutor集成

**文件**: `autoBMAD/epic_automation/agents/base_agent.py`

**实现内容**:

```python
"""
增强的Base Agent - 所有 Agent 的基类
支持TaskGroup管理和SDKExecutor集成
"""
from __future__ import annotations
import logging
import anyio
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent 基类，定义通用接口和行为"""

    def __init__(self, name: str, task_group: Optional[anyio.abc.TaskGroup] = None):
        """
        初始化 Agent

        Args:
            name: Agent 名称
            task_group: 可选的TaskGroup实例
        """
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__module__}")
        self.task_group = task_group
        self._execution_context = {}

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        执行 Agent 主逻辑

        Returns:
            Any: 执行结果
        """
        pass

    def _log_execution(self, message: str, level: str = "info"):
        """记录执行日志"""
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"[{self.name}] {message}")

    def set_task_group(self, task_group: anyio.abc.TaskGroup):
        """设置TaskGroup实例"""
        self.task_group = task_group

    async def _execute_within_taskgroup(self, coro: Callable) -> Any:
        """
        在TaskGroup内执行协程

        Args:
            coro: 要执行的协程函数

        Returns:
            协程执行结果

        Raises:
            RuntimeError: 如果没有设置TaskGroup
        """
        if not self.task_group:
            raise RuntimeError(f"{self.name}: TaskGroup not set")

        return await self.task_group.start(lambda: coro())

    async def _execute_sdk_call(
        self,
        sdk_executor,
        prompt: str,
        **kwargs
    ) -> Any:
        """
        使用SDKExecutor执行SDK调用

        Args:
            sdk_executor: SDKExecutor实例
            prompt: SDK提示词
            **kwargs: 其他参数

        Returns:
            SDK调用结果
        """
        self._log_execution(f"Executing SDK call via SDKExecutor")
        result = await sdk_executor.execute_sdk_call(
            prompt=prompt,
            **kwargs
        )
        self._log_execution(f"SDK call completed")
        return result

    def _validate_execution_context(self) -> bool:
        """验证执行上下文"""
        if not self.task_group:
            self._log_execution("Warning: No TaskGroup set", "warning")
            return False
        return True
```

**关键特性**：
1. **TaskGroup集成**: 支持在TaskGroup内执行
2. **SDKExecutor集成**: 统一的SDK调用入口
3. **上下文验证**: 确保执行前上下文完整
4. **增强日志**: 统一的日志记录机制

#### 2.1.2 重构SMAgent

**目标**: 将SMAgent从根目录迁移到agents目录，并集成BaseAgent

**源文件**: `autoBMAD/epic_automation/sm_agent.py`
**目标文件**: `autoBMAD/epic_automation/agents/sm_agent.py`

**重构策略**:

```python
"""
SM Agent - Story Master Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Any, Optional

from .base_agent import BaseAgent
from ..core.sdk_executor import SDKExecutor
from ..story_parser import SimpleStoryParser

logger = logging.getLogger(__name__)


class SMAgent(BaseAgent):
    """Story Master agent for handling story-related tasks."""

    def __init__(
        self,
        task_group: Optional[anyio.abc.TaskGroup] = None,
        project_root: Optional[Path] = None,
        tasks_path: Optional[Path] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        初始化 SM agent.

        Args:
            task_group: TaskGroup实例
            project_root: Root directory of the project
            tasks_path: Path to tasks directory
            config: Configuration dictionary
        """
        super().__init__("SMAgent", task_group)
        self.project_root = project_root
        self.tasks_path = tasks_path
        self.config = config or {}

        # 集成SDKExecutor
        self.sdk_executor = SDKExecutor(task_group) if task_group else None

        # 初始化SimpleStoryParser
        try:
            self.status_parser = SimpleStoryParser(sdk_wrapper=None)
        except ImportError:
            self.status_parser = None
            logger.warning(
                "[SM Agent] SimpleStoryParser not available, using fallback parsing"
            )

        self._log_execution("SMAgent initialized")

    async def execute(
        self,
        story_content: Optional[str] = None,
        story_path: Optional[str] = None,
        epic_path: Optional[str] = None,
    ) -> bool:
        """
        执行SM阶段任务

        Args:
            story_content: Raw markdown content of the story
            story_path: Path to the story file
            epic_path: Path to the epic file

        Returns:
            True if successful, False otherwise
        """
        self._log_execution("Starting SM phase execution")

        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "error")
            return False

        try:
            # 优先从Epic创建故事
            if epic_path:
                return await self._execute_within_taskgroup(
                    self._create_stories_from_epic(epic_path)
                )

            # 否则处理现有故事
            if story_content and story_path:
                return await self._execute_within_taskgroup(
                    self._process_story_content(story_content, story_path)
                )

            self._log_execution("No valid input provided", "error")
            return False

        except Exception as e:
            self._log_execution(f"Execution failed: {e}", "error")
            return False

    async def _create_stories_from_epic(self, epic_path: str) -> bool:
        """
        从Epic创建故事 - 重构后使用SDKExecutor
        """
        try:
            self._log_execution(f"Creating stories from Epic: {epic_path}")

            # 读取Epic内容
            with open(epic_path, encoding="utf-8") as f:
                epic_content = f.read()

            # 提取故事ID
            story_ids = self._extract_story_ids_from_epic(epic_content)
            if not story_ids:
                self._log_execution("No story IDs found", "error")
                return False

            # 使用SDKExecutor执行故事创建
            if self.sdk_executor:
                prompt = self._build_claude_prompt(epic_path, story_ids)
                result = await self._execute_sdk_call(self.sdk_executor, prompt)

                if result:
                    # 验证故事文件
                    all_passed, _ = await self._verify_story_files(story_ids, epic_path)
                    return all_passed
                else:
                    self._log_execution("SDK call failed", "error")
                    return False
            else:
                self._log_execution("SDKExecutor not available", "error")
                return False

        except Exception as e:
            self._log_execution(f"Failed to create stories: {e}", "error")
            return False

    async def _process_story_content(
        self, story_content: str, story_path: str
    ) -> bool:
        """处理故事内容"""
        try:
            self._log_execution(f"Processing story content: {story_path}")

            # 解析故事元数据
            story_data = await self._parse_story_metadata(story_content)
            if not story_data:
                self._log_execution("Failed to parse story metadata", "error")
                return False

            # 验证故事结构
            validation_result = await self._validate_story_structure(story_data)
            if not validation_result["valid"]:
                self._log_execution(
                    f"Story validation issues: {validation_result['issues']}", "warning"
                )

            self._log_execution("SM phase completed successfully")
            return True

        except Exception as e:
            self._log_execution(f"Failed to process story: {e}", "error")
            return False

    def _extract_story_ids_from_epic(self, content: str) -> list[str]:
        """提取故事ID - 保持现有逻辑"""
        # ... (保持原有实现)
        pass

    def _build_claude_prompt(self, epic_path: str, story_ids: list[str]) -> str:
        """构建Claude提示 - 保持现有逻辑"""
        # ... (保持原有实现)
        pass

    async def _verify_story_files(
        self, story_ids: list[str], epic_path: str
    ) -> tuple[bool, list[str]]:
        """验证故事文件 - 保持现有逻辑"""
        # ... (保持原有实现)
        pass

    async def _parse_story_metadata(
        self, story_content: str
    ) -> Optional[dict[str, Any]]:
        """解析故事元数据 - 保持现有逻辑"""
        # ... (保持原有实现)
        pass

    async def _validate_story_structure(
        self, story_data: dict[str, Any]
    ) -> dict[str, Any]:
        """验证故事结构 - 保持现有逻辑"""
        # ... (保持原有实现)
        pass
```

**重构重点**：
1. **继承BaseAgent**: 添加task_group参数支持
2. **SDKExecutor集成**: 使用SDKExecutor替代直接SDK调用
3. **异步执行**: 使用`_execute_within_taskgroup`方法
4. **保持逻辑**: 保持现有核心业务逻辑不变

#### 2.1.3 迁移文件

**步骤1**: 创建新文件
```bash
# 将sm_agent.py复制到agents目录
cp autoBMAD/epic_automation/sm_agent.py autoBMAD/epic_automation/agents/sm_agent.py
```

**步骤2**: 更新导入路径
```python
# 在新文件中更新导入
from .base_agent import BaseAgent
from ..core.sdk_executor import SDKExecutor
```

**步骤3**: 更新控制器导入
```python
# 在controllers/sm_controller.py中更新导入
from ..agents.sm_agent import SMAgent  # 从 ..sm_agent 改为 ..agents.sm_agent
```

**步骤4**: 删除旧文件
```bash
# 删除根目录的旧文件
rm autoBMAD/epic_automation/sm_agent.py
```

#### 2.1.4 Day 1 验收标准

**代码验收**：
- [ ] `base_agent.py` 增强完成，支持TaskGroup和SDKExecutor
- [ ] `agents/sm_agent.py` 编译无错误
- [ ] SMAgent正确继承BaseAgent
- [ ] 所有导入路径正确解析

**功能验收**：
- [ ] SMAgent可以实例化（带task_group参数）
- [ ] SMAgent.execute()可以正常调用
- [ ] SDKExecutor集成正常工作
- [ ] 状态解析功能正常

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_base_agent.py -v
pytest tests/unit/test_sm_agent.py -v

# 运行集成测试
pytest tests/integration/test_agent_controller_integration.py::test_sm_agent_integration -v
```

---

### 2.2 Day 2: StateAgent优化 + DevAgent重构

#### 2.2.1 优化StateAgent

**目标**: 增强StateAgent以支持TaskGroup管理

**文件**: `autoBMAD/epic_automation/agents/state_agent.py`

**实现内容**:

```python
"""
State Agent - 状态解析和管理 Agent
增强后支持TaskGroup管理
"""
from __future__ import annotations
import logging
import anyio
from pathlib import Path
from typing import Optional

from .base_agent import BaseAgent
from ..story_parser import SimpleStoryParser, core_status_to_processing

logger = logging.getLogger(__name__)


class StateAgent(BaseAgent):
    """状态解析和管理 Agent"""

    def __init__(self, task_group: Optional[anyio.abc.TaskGroup] = None):
        """
        初始化状态 Agent

        Args:
            task_group: TaskGroup实例
        """
        super().__init__("StateAgent", task_group)
        self.status_parser = SimpleStoryParser()
        self._log_execution("StateAgent initialized")

    async def execute(self, story_path: str) -> Optional[str]:
        """
        执行状态解析

        Args:
            story_path: 故事文件路径

        Returns:
            Optional[str]: 解析出的状态值
        """
        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            return await self.parse_status(story_path)

        return await self._execute_within_taskgroup(
            self._parse_status_with_taskgroup(story_path)
        )

    async def _parse_status_with_taskgroup(self, story_path: str) -> Optional[str]:
        """在TaskGroup内解析状态"""
        return await self.parse_status(story_path)

    async def parse_status(self, story_path: str) -> Optional[str]:
        """解析故事文件的状态 - 保持现有实现"""
        # ... (保持现有实现)
        pass

    async def get_processing_status(self, story_path: str) -> Optional[str]:
        """获取处理状态值 - 保持现有实现"""
        # ... (保持现有实现)
        pass

    async def update_story_status(self, story_path: str, status: str) -> bool:
        """更新故事状态 - 保持现有实现"""
        # ... (保持现有实现)
        pass
```

**优化重点**：
1. **TaskGroup支持**: 添加task_group参数
2. **异步执行**: 支持在TaskGroup内执行
3. **向下兼容**: 保持现有接口不变
4. **增强日志**: 使用BaseAgent的日志机制

#### 2.2.2 重构DevAgent

**目标**: 将DevAgent从根目录迁移到agents目录，并集成BaseAgent

**源文件**: `autoBMAD/epic_automation/dev_agent.py`
**目标文件**: `autoBMAD/epic_automation/agents/dev_agent.py`

**重构策略**:

```python
"""
Dev Agent - Development Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

import asyncio
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from .base_agent import BaseAgent
from ..core.sdk_executor import SDKExecutor
from ..log_manager import LogManager

if TYPE_CHECKING:
    from claude_agent_sdk import ClaudeAgentOptions, query

logger = logging.getLogger(__name__)


class DevAgent(BaseAgent):
    """Development agent for handling implementation tasks."""

    def __init__(
        self,
        task_group: Optional[anyio.abc.TaskGroup] = None,
        use_claude: bool = True,
        log_manager: Optional[LogManager] = None,
    ):
        """
        Initialize Dev agent.

        Args:
            task_group: TaskGroup实例
            use_claude: If True, use Claude Code CLI for real implementation
            log_manager: Optional LogManager instance for logging
        """
        super().__init__("DevAgent", task_group)
        self.use_claude = use_claude
        self._claude_available = (
            self._check_claude_available() if use_claude else False
        )
        self._log_manager = log_manager
        self._current_story_path = None

        # 集成SDKExecutor
        self.sdk_executor = SDKExecutor(task_group) if task_group else None

        # 初始化SimpleStoryParser
        try:
            # 创建SafeClaudeSDK实例（如果可用）
            from ..sdk_wrapper import SafeClaudeSDK

            if SafeClaudeSDK:
                from claude_agent_sdk import ClaudeAgentOptions

                options = ClaudeAgentOptions(
                    permission_mode="bypassPermissions", cwd=str(Path.cwd())
                )
                sdk_instance = SafeClaudeSDK(
                    prompt="Parse story status",
                    options=options,
                    timeout=None,
                    log_manager=log_manager,
                )
                self.status_parser = SimpleStoryParser(sdk_wrapper=sdk_instance)
            else:
                self.status_parser = None
        except ImportError:
            self.status_parser = None
            logger.warning(
                "[Dev Agent] SimpleStoryParser not available, using fallback parsing"
            )

        self._log_execution(
            f"DevAgent initialized (claude_mode={use_claude}, "
            f"claude_available={self._claude_available})"
        )

    async def execute(self, story_path: str) -> bool:
        """
        执行开发任务

        Args:
            story_path: 故事文件路径

        Returns:
            固定返回 True
        """
        self._log_execution(f"Executing development for {story_path}")

        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            # 即使没有TaskGroup也继续执行
            return await self._execute_development(story_path)

        return await self._execute_within_taskgroup(
            self._execute_development(story_path)
        )

    async def _execute_development(self, story_path: str) -> bool:
        """执行开发任务的核心逻辑"""
        try:
            self._log_execution(
                f"Epic Driver has determined this story needs development"
            )

            # 读取故事内容
            story_file = Path(story_path)
            if story_file.exists():
                story_content = story_file.read_text(encoding="utf-8")
                requirements = await self._extract_requirements(story_content)

                # 执行开发任务
                development_success = await self._execute_development_tasks(
                    requirements, story_path
                )
                self._log_execution(
                    f"Development tasks executed (result={development_success})"
                )
            else:
                self._log_execution(f"Story file not found: {story_path}", "warning")

            self._log_execution(
                "Development execution completed, "
                "Epic Driver will re-parse status to determine next step"
            )
            return True

        except Exception as e:
            self._log_execution(
                f"Exception during development: {e}, continuing workflow",
                "warning",
            )
            return True

    async def _execute_development_tasks(
        self, requirements: dict[str, Any], story_path: str
    ) -> bool:
        """执行开发任务 - 使用SDKExecutor"""
        try:
            # 检查QA反馈模式
            if "qa_prompt" in requirements:
                self._log_execution("Handling QA feedback with single SDK call")
                prompt = f"@.bmad-core/agents/dev.md {requirements['qa_prompt']}"
                result = await self._execute_sdk_call(
                    self.sdk_executor, prompt, story_path=story_path
                )
                return True

            # 正常开发模式
            self._log_execution(f"Executing normal development mode for '{story_path}'")
            base_prompt = (
                f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\agents\\dev.md '
                f'@D:\\GITHUB\\pytQt_template\\.bmad-core\\tasks\\develop-story.md '
                f'According to Story @{story_path}, '
                f'Create or improve comprehensive test suites '
                f'@D:\\GITHUB\\pytQt_template\\autoBMAD\\spec_automation\\tests. '
                f'Perform Test-Driven Development (TDD) iteratively until achieving '
                f'100% tests pass with comprehensive coverage. '
                f'Run "pytest -v --tb=short --cov" to verify tests and coverage. '
                f'Change story Status to "Ready for Review" when complete.'
            )

            result = await self._execute_sdk_call(
                self.sdk_executor, base_prompt, story_path=story_path
            )

            self._log_execution(
                f"Development execution completed (result={result}), "
                f"Epic Driver will re-parse status to determine next step"
            )
            return True

        except Exception as e:
            self._log_execution(
                f"Exception during development tasks: {e}, continuing workflow",
                "warning",
            )
            return True

    async def _extract_requirements(self, story_content: str) -> dict[str, Any]:
        """提取需求 - 保持现有实现"""
        # ... (保持现有实现)
        pass

    def _validate_prompt_format(self, prompt: str) -> bool:
        """验证提示格式 - 保持现有实现"""
        # ... (保持现有实现)
        pass

    def _check_claude_available(self) -> bool:
        """检查Claude可用性 - 保持现有实现"""
        # ... (保持现有实现)
        pass
```

**重构重点**：
1. **继承BaseAgent**: 添加task_group参数支持
2. **SDKExecutor集成**: 使用SDKExecutor替代直接SDK调用
3. **简化执行**: 移除复杂的状态检查逻辑
4. **保持兼容**: 维持返回True的设计

#### 2.2.3 Day 2 验收标准

**代码验收**：
- [ ] StateAgent优化完成，支持TaskGroup
- [ ] `agents/dev_agent.py` 编译无错误
- [ ] DevAgent正确继承BaseAgent
- [ ] 所有导入路径正确解析

**功能验收**：
- [ ] StateAgent可以在TaskGroup内执行
- [ ] DevAgent可以实例化（带task_group参数）
- [ ] DevAgent.execute()正常调用
- [ ] SDKExecutor集成正常工作

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_state_agent.py -v
pytest tests/unit/test_dev_agent.py -v

# 运行集成测试
pytest tests/integration/test_agent_controller_integration.py::test_dev_agent_integration -v
```

---

### 2.3 Day 3: QAAgent重构

#### 2.3.1 重构QAAgent

**目标**: 将QAAgent从根目录迁移到agents目录，并集成BaseAgent

**源文件**: `autoBMAD/epic_automation/qa_agent.py`
**目标文件**: `autoBMAD/epic_automation/agents/qa_agent.py`

**重构策略**:

```python
"""
QA Agent - Quality Assurance Agent
重构后集成BaseAgent，支持TaskGroup和SDKExecutor
"""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from .base_agent import BaseAgent
from ..core.sdk_executor import SDKExecutor
from ..story_parser import SimpleStoryParser

if TYPE_CHECKING:
    from claude_agent_sdk import ClaudeAgentOptions

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    Quality Assurance agent for handling QA review tasks.
    """

    name: str = "QA Agent"

    def __init__(self, task_group: Optional[anyio.abc.TaskGroup] = None):
        """
        初始化QA代理

        Args:
            task_group: TaskGroup实例
        """
        super().__init__("QAAgent", task_group)

        # 集成SDKExecutor
        self.sdk_executor = SDKExecutor(task_group) if task_group else None

        # 初始化SimpleStoryParser
        try:
            from ..sdk_wrapper import SafeClaudeSDK

            if SafeClaudeSDK:
                from claude_agent_sdk import ClaudeAgentOptions

                options = ClaudeAgentOptions(
                    permission_mode="bypassPermissions",
                    cwd=str(Path.cwd()),
                    cli_path=r"D:\GITHUB\pytQt_template\venv\Lib\site-packages\claude_agent_sdk\_bundled\claude.exe",
                )
                sdk_instance = SafeClaudeSDK(
                    prompt="Parse story status",
                    options=options,
                    timeout=None,
                    log_manager=None,
                )
                self.status_parser = SimpleStoryParser(sdk_wrapper=sdk_instance)
            else:
                self.status_parser = None
        except ImportError:
            self.status_parser = None
            logger.warning(
                "[QA Agent] SimpleStoryParser not available, using fallback parsing"
            )

        self._log_execution("QAAgent initialized")

    async def execute(
        self,
        story_path: str,
        cached_status: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        执行QA审查

        Args:
            story_path: 故事文件路径
            cached_status: 缓存的状态值（不再使用）

        Returns:
            固定返回 passed=True 的字典
        """
        self._log_execution(f"Executing QA review for {story_path}")

        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            # 即使没有TaskGroup也继续执行
            return await self._execute_qa_review(story_path)

        return await self._execute_within_taskgroup(
            self._execute_qa_review(story_path)
        )

    async def _execute_qa_review(self, story_path: str) -> dict[str, Any]:
        """执行QA审查的核心逻辑"""
        try:
            self._log_execution(
                "Epic Driver has determined this story needs QA review"
            )

            # 尝试执行QA工具检查
            try:
                from ..qa_tools_integration import QAAutomationWorkflow

                qa_workflow = QAAutomationWorkflow()
                qa_result = await qa_workflow.run_qa_checks()
                self._log_execution(
                    f"QA checks completed: {qa_result.get('overall_status', 'unknown')}"
                )
            except (ImportError, Exception) as e:
                self._log_execution(
                    f"QA checks failed or unavailable: {e}, continuing workflow",
                    "warning",
                )

            self._log_execution(
                "QA execution completed, "
                "Epic Driver will re-parse status to determine next step"
            )

            # 🎯 关键：始终返回 passed=True
            return {
                "passed": True,
                "completed": True,
                "needs_fix": False,
                "message": "QA execution completed",
            }

        except Exception as e:
            self._log_execution(
                f"Exception during QA: {e}, continuing workflow", "warning"
            )
            return {
                "passed": True,
                "completed": True,
                "needs_fix": False,
                "message": f"QA execution completed with exception: {str(e)}",
            }

    async def execute_qa_phase(
        self,
        story_path: str,
        source_dir: str = "src",
        test_dir: str = "tests",
        cached_status: Optional[str] = None,
    ) -> bool:
        """
        简化的QA阶段执行方法，用于Dev Agent调用

        Args:
            story_path: 故事文件路径
            source_dir: 源代码目录
            test_dir: 测试目录
            cached_status: 缓存的状态值

        Returns:
            始终返回 True
        """
        self._log_execution(f"Executing QA phase for {story_path}")

        result = await self.execute(story_path=story_path, cached_status=cached_status)

        self._log_execution(
            f"QA phase completed (result={result.get('passed', False)}), "
            f"Epic Driver will re-parse status to determine next step"
        )
        return True

    async def _parse_story_status(self, story_path: str) -> str:
        """解析故事状态 - 保持现有实现"""
        # ... (保持现有实现，简化)
        pass

    async def get_statistics(self) -> dict[str, Any]:
        """获取QA代理统计信息"""
        try:
            # 如果有会话管理器，获取统计信息
            if hasattr(self, '_session_manager'):
                stats = self._session_manager.get_statistics()
                return {
                    "agent_name": self.name,
                    "session_statistics": stats,
                    "active_sessions": self._session_manager.get_session_count(),
                }
            else:
                return {"agent_name": self.name, "message": "No session manager"}
        except Exception as e:
            self._log_execution(f"Failed to get statistics: {e}", "error")
            return {"error": str(e)}
```

**重构重点**：
1. **继承BaseAgent**: 添加task_group参数支持
2. **SDKExecutor集成**: 使用SDKExecutor替代直接SDK调用
3. **简化执行**: 移除复杂的状态检查逻辑
4. **保持兼容**: 维持返回passed=True的设计

#### 2.3.2 Day 3 验收标准

**代码验收**：
- [ ] `agents/qa_agent.py` 编译无错误
- [ ] QAAgent正确继承BaseAgent
- [ ] 所有导入路径正确解析
- [ ] 移除旧文件 `autoBMAD/epic_automation/qa_agent.py`

**功能验收**：
- [ ] QAAgent可以实例化（带task_group参数）
- [ ] QAAgent.execute()正常调用
- [ ] SDKExecutor集成正常工作
- [ ] 返回结果格式正确

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_qa_agent.py -v

# 运行集成测试
pytest tests/integration/test_agent_controller_integration.py::test_qa_agent_integration -v
```

---

### 2.4 Day 4: Quality Agents优化

#### 2.4.1 优化Quality Agents

**目标**: 增强Quality Agents以支持TaskGroup管理

**文件**: `autoBMAD/epic_automation/agents/quality_agents.py`

**实现内容**:

```python
"""
Quality Agents - 重构后的质量检查 Agents
增强后支持TaskGroup管理
"""
from __future__ import annotations
import logging
import anyio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio
import subprocess
from pathlib import Path

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BaseQualityAgent(BaseAgent, ABC):
    """质量检查 Agent 基类"""

    def __init__(
        self,
        name: str,
        task_group: Optional[anyio.abc.TaskGroup] = None,
    ):
        """
        初始化质量检查 Agent

        Args:
            name: Agent名称
            task_group: TaskGroup实例
        """
        super().__init__(name, task_group)

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行质量检查

        Args:
            **kwargs: 检查参数

        Returns:
            Dict[str, Any]: 检查结果
        """
        if not self._validate_execution_context():
            self._log_execution("Execution context invalid", "warning")
            return await self._execute_check(**kwargs)

        return await self._execute_within_taskgroup(
            self._execute_check(**kwargs)
        )

    @abstractmethod
    async def _execute_check(self, **kwargs) -> Dict[str, Any]:
        """具体的检查实现"""
        pass

    async def _run_subprocess(
        self, command: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """
        运行子进程命令

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）

        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 在线程池中运行子进程，避免 cancel scope 传播
            loop = asyncio.get_event_loop()
            process = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                    ),
                ),
                timeout=timeout + 10,
            )

            return {
                "status": "completed",
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "success": process.returncode == 0,
            }
        except asyncio.TimeoutError:
            self._log_execution(
                f"Command timed out after {timeout} seconds: {command}", "error"
            )
            return {
                "status": "failed",
                "error": f"Timeout after {timeout} seconds",
                "command": command,
            }
        except Exception as e:
            self._log_execution(f"Command failed: {e}", "error")
            return {
                "status": "failed",
                "error": str(e),
                "command": command,
            }


class RuffAgent(BaseQualityAgent):
    """Ruff 代码风格检查 Agent"""

    def __init__(self, task_group: Optional[anyio.abc.TaskGroup] = None):
        super().__init__("Ruff", task_group)

    async def _execute_check(
        self, source_dir: str, project_root: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行Ruff检查"""
        self._log_execution("Running Ruff checks")

        try:
            command = f"ruff check {source_dir} --output-format=json"
            result = await self._run_subprocess(command)

            if result["status"] == "completed":
                import json

                try:
                    issues = json.loads(result["stdout"]) if result["stdout"] else []
                    return {
                        "status": "completed",
                        "errors": len([i for i in issues if i.get("severity") == "error"]),
                        "warnings": len([i for i in issues if i.get("severity") == "warning"]),
                        "files_checked": len(set(i.get("filename", "") for i in issues)),
                        "issues": issues,
                        "message": f"Found {len(issues)} issues",
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "completed",
                        "errors": 0,
                        "warnings": 0,
                        "files_checked": 0,
                        "message": "Check completed (no JSON output)",
                    }
            else:
                return result

        except Exception as e:
            self._log_execution(f"Ruff check failed: {e}", "error")
            return {"status": "failed", "error": str(e)}


class BasedPyrightAgent(BaseQualityAgent):
    """BasedPyright 类型检查 Agent"""

    def __init__(self, task_group: Optional[anyio.abc.TaskGroup] = None):
        super().__init__("BasedPyright", task_group)

    async def _execute_check(self, source_dir: str) -> Dict[str, Any]:
        """执行BasedPyright检查"""
        self._log_execution("Running BasedPyright checks")

        try:
            command = f"basedpyright {source_dir} --outputformat=json"
            result = await self._run_subprocess(command)

            if result["status"] == "completed":
                import json

                try:
                    output = json.loads(result["stdout"]) if result["stdout"] else {}
                    issues = output.get("generalDiagnostics", [])

                    return {
                        "status": "completed",
                        "errors": len([i for i in issues if i.get("severity") == "error"]),
                        "warnings": len([i for i in issues if i.get("severity") == "warning"]),
                        "files_checked": len(set(i.get("file", "") for i in issues)),
                        "issues": issues,
                        "message": f"Found {len(issues)} type issues",
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "completed",
                        "errors": 0,
                        "warnings": 0,
                        "files_checked": 0,
                        "message": "Check completed (no JSON output)",
                    }
            else:
                return result

        except Exception as e:
            self._log_execution(f"BasedPyright check failed: {e}", "error")
            return {"status": "failed", "error": str(e)}


class PytestAgent(BaseQualityAgent):
    """Pytest 测试执行 Agent"""

    def __init__(self, task_group: Optional[anyio.abc.TaskGroup] = None):
        super().__init__("Pytest", task_group)

    async def _execute_check(
        self, source_dir: str, test_dir: str
    ) -> Dict[str, Any]:
        """执行Pytest测试"""
        self._log_execution("Running Pytest")

        try:
            command = (
                f"pytest {test_dir} -v --tb=short "
                f"--cov={source_dir} --cov-report=json"
            )
            result = await self._run_subprocess(command, timeout=600)

            if result["status"] == "completed":
                import re
                import json
                from json import JSONDecodeError

                # 尝试获取覆盖率信息
                try:
                    coverage_match = re.search(r"\{.*\}", result["stdout"], re.DOTALL)
                    if coverage_match:
                        coverage_data = json.loads(coverage_match.group())
                        coverage_percent = coverage_data.get("totals", {}).get(
                            "percent_covered", 0
                        )
                    else:
                        coverage_percent = 0
                except (JSONDecodeError, json.JSONDecodeError):
                    coverage_percent = 0

                # 解析测试统计
                output_lines = result["stdout"].split("\n")
                tests_passed = 0
                tests_failed = 0
                tests_errors = 0

                for line in output_lines:
                    if "passed" in line:
                        match = re.search(r"(\d+) passed", line)
                        if match:
                            tests_passed = int(match.group(1))
                    elif "failed" in line:
                        match = re.search(r"(\d+) failed", line)
                        if match:
                            tests_failed = int(match.group(1))
                    elif "error" in line:
                        match = re.search(r"(\d+) error", line)
                        if match:
                            tests_errors = int(match.group(1))

                return {
                    "status": "completed",
                    "tests_passed": tests_passed,
                    "tests_failed": tests_failed,
                    "tests_errors": tests_errors,
                    "coverage": coverage_percent,
                    "total_tests": tests_passed + tests_failed + tests_errors,
                    "message": f"{tests_passed} tests passed, {tests_failed} failed, {tests_errors} errors",
                }
            else:
                return result

        except Exception as e:
            self._log_execution(f"Pytest execution failed: {e}", "error")
            return {"status": "failed", "error": str(e)}
```

**优化重点**：
1. **TaskGroup支持**: 所有Quality Agents支持task_group参数
2. **统一接口**: 所有agent继承BaseQualityAgent
3. **异步执行**: 使用`_execute_within_taskgroup`方法
4. **保持功能**: 保持现有检查逻辑不变

#### 2.4.2 Day 4 验收标准

**代码验收**：
- [ ] Quality Agents增强完成，支持TaskGroup
- [ ] BaseQualityAgent正确继承BaseAgent
- [ ] 所有Quality Agents编译无错误
- [ ] 所有导入路径正确解析

**功能验收**：
- [ ] RuffAgent可以实例化（带task_group参数）
- [ ] BasedPyrightAgent可以实例化（带task_group参数）
- [ ] PytestAgent可以实例化（带task_group参数）
- [ ] 所有agents可以在TaskGroup内执行

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_quality_agents.py -v

# 运行集成测试
pytest tests/integration/test_agent_controller_integration.py::test_quality_agents_integration -v
```

---

## 3. 集成策略

### 3.1 控制器与Agent集成

**集成模式**：
```
Controller (Layer 2)
  ↓ 控制
Agent (Layer 3) - Phase 3
  ↓ 委托
SDKExecutor (Layer 4) - Phase 1
```

**关键集成点**：
1. **TaskGroup传递**: 控制器将TaskGroup传递给Agent
2. **异步执行**: 所有Agent调用都在TaskGroup内执行
3. **SDKExecutor使用**: Agent使用SDKExecutor而非直接调用SDK
4. **错误传播**: 错误从Agent传播到Controller

### 3.2 与Phase 2的集成

**更新控制器**：
```python
# controllers/sm_controller.py
from ..agents.sm_agent import SMAgent
from ..agents.state_agent import StateAgent

class SMController(StateDrivenController):
    async def execute(self, epic_content: str, story_id: str) -> bool:
        # 使用增强的SMAgent
        self.sm_agent = SMAgent(task_group=self.task_group)
        self.state_agent = StateAgent(task_group=self.task_group)

        # 执行
        return await self.sm_agent.execute(epic_content=epic_content)
```

**更新控制器导入**：
```python
# controllers/devqa_controller.py
from ..agents.dev_agent import DevAgent
from ..agents.qa_agent import QAAgent

class DevQaController(StateDrivenController):
    def __init__(self, task_group: anyio.abc.TaskGroup):
        super().__init__(task_group)
        # 使用增强的DevAgent和QAAgent
        self.dev_agent = DevAgent(task_group=task_group)
        self.qa_agent = QAAgent(task_group=task_group)
```

### 3.3 与Phase 1的集成

**集成点**：
1. **SDKExecutor**: 所有Agent使用SDKExecutor执行SDK调用
2. **CancellationManager**: 使用统一的取消管理机制
3. **TaskGroupManager**: 使用TaskGroup管理器

**示例代码**：
```python
# agents/sm_agent.py
from ..core.sdk_executor import SDKExecutor

class SMAgent(BaseAgent):
    def __init__(self, task_group: Optional[anyio.abc.TaskGroup] = None):
        super().__init__("SMAgent", task_group)
        # 使用Phase 1的SDKExecutor
        self.sdk_executor = SDKExecutor(task_group) if task_group else None

    async def _create_stories_from_epic(self, epic_path: str) -> bool:
        # 使用SDKExecutor执行SDK调用
        prompt = self._build_claude_prompt(epic_path, story_ids)
        result = await self._execute_sdk_call(self.sdk_executor, prompt)
        return result
```

---

## 4. 测试策略

### 4.1 单元测试

**BaseAgent测试**：
```python
# tests/unit/test_base_agent.py
import pytest
import anyio
from autoBMAD.epic_automation.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    async def execute(self):
        return "test"

@pytest.mark.anyio
async def test_base_agent_init():
    """测试BaseAgent初始化"""
    agent = TestAgent("TestAgent")
    assert agent.name == "TestAgent"
    assert agent.task_group is None

@pytest.mark.anyio
async def test_base_agent_set_task_group():
    """测试TaskGroup设置"""
    agent = TestAgent("TestAgent")

    async with anyio.create_task_group() as tg:
        agent.set_task_group(tg)
        assert agent.task_group is not None

@pytest.mark.anyio
async def test_base_agent_validate_context():
    """测试执行上下文验证"""
    agent = TestAgent("TestAgent")
    assert not agent._validate_execution_context()

    async with anyio.create_task_group() as tg:
        agent.set_task_group(tg)
        assert agent._validate_execution_context()
```

**SMAgent测试**：
```python
# tests/unit/test_sm_agent.py
import pytest
import anyio
from pathlib import Path
from autoBMAD.epic_automation.agents.sm_agent import SMAgent

@pytest.mark.anyio
async def test_sm_agent_init():
    """测试SMAgent初始化"""
    async with anyio.create_task_group() as tg:
        agent = SMAgent(task_group=tg)
        assert agent.name == "SMAgent"
        assert agent.task_group is tg
        assert agent.sdk_executor is not None

@pytest.mark.anyio
async def test_sm_agent_execute():
    """测试SMAgent执行"""
    async with anyio.create_task_group() as tg:
        agent = SMAgent(task_group=tg)
        # 测试执行
        result = await agent.execute(
            story_content="# Test Story\n\n**Status**: Draft",
            story_path="test_story.md"
        )
        assert isinstance(result, bool)
```

**DevAgent测试**：
```python
# tests/unit/test_dev_agent.py
import pytest
import anyio
from autoBMAD.epic_automation.agents.dev_agent import DevAgent

@pytest.mark.anyio
async def test_dev_agent_init():
    """测试DevAgent初始化"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)
        assert agent.name == "DevAgent"
        assert agent.task_group is tg
        assert agent.sdk_executor is not None

@pytest.mark.anyio
async def test_dev_agent_execute():
    """测试DevAgent执行"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(task_group=tg)
        # 创建测试故事文件
        test_story = Path("test_story.md")
        test_story.write_text("# Test Story\n\n**Status**: Draft")

        # 执行
        result = await agent.execute(str(test_story))
        assert result is True  # DevAgent始终返回True

        # 清理
        test_story.unlink()
```

**QAAgent测试**：
```python
# tests/unit/test_qa_agent.py
import pytest
import anyio
from autoBMAD.epic_automation.agents.qa_agent import QAAgent

@pytest.mark.anyio
async def test_qa_agent_init():
    """测试QAAgent初始化"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)
        assert agent.name == "QA Agent"
        assert agent.task_group is tg
        assert agent.sdk_executor is not None

@pytest.mark.anyio
async def test_qa_agent_execute():
    """测试QAAgent执行"""
    async with anyio.create_task_group() as tg:
        agent = QAAgent(task_group=tg)
        # 创建测试故事文件
        test_story = Path("test_story.md")
        test_story.write_text("# Test Story\n\n**Status**: Ready for Review")

        # 执行
        result = await agent.execute(str(test_story))
        assert result["passed"] is True
        assert result["completed"] is True
        assert result["needs_fix"] is False

        # 清理
        test_story.unlink()
```

### 4.2 集成测试

**控制器-Agent集成测试**：
```python
# tests/integration/test_agent_controller_integration.py
import pytest
import anyio
from pathlib import Path
from autoBMAD.epic_automation.controllers.sm_controller import SMController
from autoBMAD.epic_automation.agents.sm_agent import SMAgent

@pytest.mark.anyio
async def test_sm_agent_integration():
    """测试SMAgent与控制器的集成"""
    async with anyio.create_task_group() as tg:
        # 创建控制器
        controller = SMController(tg, project_root=Path.cwd())

        # 测试SMAgent
        agent = SMAgent(tg)
        result = await agent.execute(
            story_content="# Test Story\n\n**Status**: Draft",
            story_path="test_story.md"
        )
        assert isinstance(result, bool)

@pytest.mark.anyio
async def test_dev_agent_integration():
    """测试DevAgent与控制器的集成"""
    async with anyio.create_task_group() as tg:
        # 创建控制器
        controller = DevQaController(tg)

        # 创建测试故事
        test_story = Path("test_story.md")
        test_story.write_text("# Test Story\n\n**Status**: Ready for Development")

        # 测试DevAgent
        agent = DevAgent(tg)
        result = await agent.execute(str(test_story))
        assert result is True

        # 清理
        test_story.unlink()
```

**TaskGroup集成测试**：
```python
# tests/integration/test_agent_taskgroup_integration.py
import pytest
import anyio
from autoBMAD.epic_automation.agents.sm_agent import SMAgent
from autoBMAD.epic_automation.agents.dev_agent import DevAgent
from autoBMAD.epic_automation.agents.qa_agent import QAAgent

@pytest.mark.anyio
async def test_all_agents_in_taskgroup():
    """测试所有Agent在TaskGroup内的集成"""
    async with anyio.create_task_group() as tg:
        # 创建所有Agent
        sm_agent = SMAgent(tg)
        dev_agent = DevAgent(tg)
        qa_agent = QAAgent(tg)

        # 创建测试故事文件
        test_story = Path("test_story.md")
        test_story.write_text("# Test Story\n\n**Status**: Ready for Development")

        # 并行执行所有Agent
        async with anyio.create_task_group() as nested_tg:
            nested_tg.start_soon(sm_agent.execute, None, str(test_story))
            nested_tg.start_soon(dev_agent.execute, str(test_story))
            nested_tg.start_soon(qa_agent.execute, str(test_story))

        # 清理
        test_story.unlink()
```

### 4.3 性能测试

**基准测试**：
```python
# tests/performance/test_agent_performance.py
import time
import pytest
import anyio
from autoBMAD.epic_automation.agents.sm_agent import SMAgent

@pytest.mark.performance
@pytest.mark.anyio
async def test_sm_agent_execution_time():
    """测试SMAgent执行时间"""
    async with anyio.create_task_group() as tg:
        agent = SMAgent(tg)

        start = time.time()
        result = await agent.execute(
            story_content="# Test Story\n\n**Status**: Draft",
            story_path="test_story.md"
        )
        end = time.time()

        assert result is True
        assert (end - start) < 5.0  # 5秒内完成

@pytest.mark.performance
@pytest.mark.anyio
async def test_dev_agent_execution_time():
    """测试DevAgent执行时间"""
    async with anyio.create_task_group() as tg:
        agent = DevAgent(tg)

        test_story = Path("test_story.md")
        test_story.write_text("# Test Story\n\n**Status**: Ready for Development")

        start = time.time()
        result = await agent.execute(str(test_story))
        end = time.time()

        assert result is True
        assert (end - start) < 10.0  # 10秒内完成

        # 清理
        test_story.unlink()
```

---

## 5. 风险评估与缓解

### 5.1 技术风险

**风险1: TaskGroup生命周期管理**
- **描述**: Cancel Scope可能跨越TaskGroup边界
- **概率**: 中
- **影响**: 高
- **缓解**: 严格遵循`_execute_within_taskgroup`使用规范

**风险2: SDKExecutor集成问题**
- **描述**: 新Agent可能与SDKExecutor不兼容
- **概率**: 中
- **影响**: 中
- **缓解**: 充分测试SDKExecutor集成

**风险3: 状态解析冲突**
- **描述**: 多个Agent同时解析状态可能冲突
- **概率**: 低
- **影响**: 中
- **缓解**: 使用StateAgent统一状态解析

### 5.2 质量风险

**风险4: 功能回归**
- **描述**: 重构可能破坏现有功能
- **概率**: 中
- **影响**: 高
- **缓解**: 全面的E2E测试，双轨运行验证

**风险5: 性能退化**
- **描述**: 新架构可能引入性能开销
- **概率**: 低
- **影响**: 中
- **缓解**: 性能基准测试，优化关键路径

### 5.3 缓解措施

**措施1: 持续集成测试**
- 每次代码提交后自动运行测试套件
- 监控测试通过率和性能指标

**措施2: 代码审查**
- 所有代码变更必须经过审查
- 重点审查TaskGroup使用和SDKExecutor集成

**措施3: 渐进式部署**
- 先在开发环境验证
- 然后在测试环境验证
- 最后在生产环境部署

---

## 6. 验收标准

### 6.1 功能验收

**必须满足**：
- [ ] 所有Agent正确继承BaseAgent
- [ ] 所有Agent支持TaskGroup参数
- [ ] 所有Agent可以在TaskGroup内执行
- [ ] SDKExecutor集成正常工作
- [ ] 控制器可以正确管理Agent生命周期

**期望达到**：
- [ ] Agent响应时间 < 2秒
- [ ] SDK调用成功率 > 95%
- [ ] 错误处理覆盖率 > 90%

### 6.2 质量验收

**代码质量**：
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试覆盖率 > 90%
- [ ] 代码静态分析无Critical问题
- [ ] 代码审查通过率 = 100%

**文档质量**：
- [ ] API文档完整（所有公共方法）
- [ ] 架构文档清晰（Agent设计）
- [ ] 示例代码可运行

### 6.3 性能验收

**性能指标**：
- [ ] SMAgent.execute() < 2秒
- [ ] DevAgent.execute() < 10秒
- [ ] QAAgent.execute() < 5秒
- [ ] Quality Agents.execute() < 30秒
- [ ] 内存占用 < 50MB（单Agent实例）

### 6.4 验收测试套件

**运行命令**：
```bash
# 1. 单元测试
pytest tests/unit/test_base_agent.py -v
pytest tests/unit/test_sm_agent.py -v
pytest tests/unit/test_dev_agent.py -v
pytest tests/unit/test_qa_agent.py -v
pytest tests/unit/test_quality_agents.py -v

# 2. 集成测试
pytest tests/integration/test_agent_controller_integration.py -v
pytest tests/integration/test_agent_taskgroup_integration.py -v

# 3. 性能测试
pytest tests/performance/test_agent_performance.py -v

# 4. E2E测试
pytest tests/e2e/test_full_pipeline.py -v
```

**验收标准**：
- 所有测试通过率 = 100%
- 性能测试全部达标
- 代码覆盖率达标

---

## 7. 后续工作

### 7.1 Phase 4准备

**集成测试**：
- 基于重构后的Agent进行完整E2E测试
- 验证整个流水线（SM → Dev-QA → Quality）
- 性能基准对比

### 7.2 EpicDriver集成

**更新EpicDriver**：
```python
# 在epic_driver.py中集成新Agent
class EpicDriver:
    async def run_story(self, story_path: str):
        async with create_task_group() as story_tg:
            # 使用新Agent
            sm_agent = SMAgent(story_tg)
            await sm_agent.execute(story_path=story_path)

            dev_agent = DevAgent(story_tg)
            await dev_agent.execute(story_path)

            qa_agent = QAAgent(story_tg)
            await qa_agent.execute(story_path)

            # 质量检查
            quality_agents = QualityController(story_tg)
            await quality_agents.execute()
```

### 7.3 文档更新

**需要更新的文档**：
1. `ARCHITECTURE.md` - 更新Agent层说明
2. `API_REFERENCE.md` - 添加Agent API文档
3. `MIGRATION_GUIDE.md` - 添加从旧架构迁移的指南

---

## 8. 总结

### 8.1 实施价值

**架构价值**：
1. **统一接口**: 所有Agent继承BaseAgent，提供一致的接口
2. **TaskGroup集成**: 完整的TaskGroup生命周期管理
3. **SDKExecutor集成**: 统一的SDK调用入口

**技术价值**：
1. **可维护性**: 清晰的层次结构和职责分离
2. **可测试性**: 每个Agent可以独立测试
3. **可扩展性**: 易于添加新的Agent

### 8.2 关键成功因素

1. **严格遵循架构原则**: 不跨越层间依赖
2. **充分的测试覆盖**: 确保重构不破坏现有功能
3. **渐进式迁移**: 平滑过渡，避免激进变更
4. **持续验证**: 每个阶段完成后立即验证

### 8.3 里程碑检查点

**Day 1 结束检查**：
- [ ] BaseAgent增强完成
- [ ] SMAgent重构完成
- [ ] 相关测试通过

**Day 2 结束检查**：
- [ ] StateAgent优化完成
- [ ] DevAgent重构完成
- [ ] 相关测试通过

**Day 3 结束检查**：
- [ ] QAAgent重构完成
- [ ] 相关测试通过

**Day 4 结束检查**：
- [ ] Quality Agents优化完成
- [ ] 所有Agent集成测试通过
- [ ] Phase 3验收完成

**Phase 3 验收**：
- [ ] 所有Agent正常工作
- [ ] 与Phase 2控制器层无缝集成
- [ ] 与Phase 1 SDK执行层无缝集成
- [ ] 为Phase 4集成测试做好准备

---

**下一步**: Phase 4: 集成测试 - [05-phase4-integration.md](05-phase4-integration.md)
