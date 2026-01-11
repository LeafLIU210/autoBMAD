# Phase 2: 控制器层实施计划

**文档版本**: 1.0
**创建日期**: 2026-01-11
**状态**: Ready for Implementation
**前序阶段**: Phase 1 (SDK执行层) 必须完成

---

## 1. 实施概览

### 1.1 阶段目标

**核心目标**：
1. 创建控制器层框架（BaseController）
2. 实现三个核心控制器（SMController、DevQaController、QualityController）
3. 建立状态机流水线
4. 与 Phase 1 的 SDK 执行层集成
5. 确保与现有代码的平滑迁移

**技术目标**：
- 控制器作为业务流程的决策层
- 基于状态的驱动机制
- 与 TaskGroup 层完美集成
- 消除跨 Task 的 Cancel Scope 问题

### 1.2 架构定位

```
Layer 1: TaskGroup (AnyIO 容器)
  ↓ 管理
Layer 2: Controller (业务流程决策) ← 本阶段
  ↓ 控制
Layer 3: Agent (业务逻辑实现)
  ↓ 委托
Layer 4: SDK Executor (SDK调用管理)
```

### 1.3 交付物清单

**核心文件**：
```
autoBMAD/epic_automation/
├── core/
│   ├── taskgroup_manager.py       # Phase 1 已完成
│   ├── sdk_executor.py            # Phase 1 已完成
│   └── cancellation_manager.py    # Phase 1 已完成
├── controllers/
│   ├── base_controller.py         # 新建
│   ├── sm_controller.py          # 新建
│   ├── devqa_controller.py       # 新建
│   └── quality_controller.py     # 新建
└── agents/
    ├── base_agent.py             # 新建（重构现有 Agent）
    ├── sm_agent.py               # 重构
    ├── state_agent.py            # 新建
    ├── dev_agent.py              # 重构
    ├── qa_agent.py               # 重构
    └── quality_agents.py         # 重构
```

**测试文件**：
```
tests/
├── unit/
│   ├── test_base_controller.py    # 新建
│   ├── test_sm_controller.py      # 新建
│   ├── test_devqa_controller.py    # 新建
│   └── test_quality_controller.py  # 新建
└── integration/
    ├── test_controller_agent_integration.py  # 新建
    └── test_state_machine_pipeline.py        # 新建
```

---

## 2. 详细实施计划

### 2.1 Day 1: BaseController + SMController

#### 2.1.1 创建控制器框架

**目标**: 建立所有控制器的基类和通用机制

**文件**: `autoBMAD/epic_automation/controllers/base_controller.py`

**实现内容**:

```python
"""
Base Controller - 所有控制器的基类
"""
from __future__ import annotations
import logging
import anyio
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """控制器基类，定义通用接口和行为"""

    def __init__(self, task_group: anyio.abc.TaskGroup):
        """
        初始化控制器

        Args:
            task_group: 控制器所属的 TaskGroup
        """
        self.task_group = task_group
        self.logger = logging.getLogger(f"{self.__class__.__module__}")

    @abstractmethod
    async def execute(self, *args, **kwargs) -> bool:
        """
        执行控制器主逻辑

        Returns:
            bool: 执行是否成功
        """
        pass

    async def _execute_within_taskgroup(self, coro):
        """
        在所属 TaskGroup 内执行协程

        Args:
            coro: 要执行的协程函数

        Returns:
            协程执行结果
        """
        return await self.task_group.start(lambda: coro)

    def _log_execution(self, message: str, level: str = "info"):
        """记录执行日志"""
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"[{self.__class__.__name__}] {message}")


class StateDrivenController(BaseController):
    """状态驱动的控制器基类"""

    def __init__(self, task_group: anyio.abc.TaskGroup):
        super().__init__(task_group)
        self.max_iterations = 3

    async def run_state_machine(self, initial_state: str, max_rounds: int = 3) -> bool:
        """
        运行状态机循环

        Args:
            initial_state: 初始状态
            max_rounds: 最大执行轮数

        Returns:
            bool: 是否达到终止状态
        """
        self.max_iterations = max_rounds
        return await self._run_state_machine_loop(initial_state)

    async def _run_state_machine_loop(self, initial_state: str) -> bool:
        """状态机循环实现"""
        current_state = initial_state
        for round_num in range(1, self.max_iterations + 1):
            self._log_execution(f"Round {round_num}: Current state = {current_state}")

            # 状态检查和决策
            next_state = await self._make_decision(current_state)

            if self._is_termination_state(next_state):
                self._log_execution(f"Reached termination state: {next_state}")
                return True

            current_state = next_state

        self._log_execution(f"Max iterations ({self.max_iterations}) reached")
        return False

    @abstractmethod
    async def _make_decision(self, current_state: str) -> str:
        """
        基于当前状态做出决策

        Args:
            current_state: 当前状态

        Returns:
            str: 下一个状态
        """
        pass

    def _is_termination_state(self, state: str) -> bool:
        """判断是否为终止状态"""
        return state in ["Done", "Ready for Done"]
```

**关键特性**：
1. **TaskGroup 集成**: 控制器必须在 TaskGroup 内运行
2. **状态驱动**: 基类提供状态机循环机制
3. **通用日志**: 统一的日志记录机制
4. **迭代控制**: 防止无限循环的保护机制

#### 2.1.2 实现 SMController

**目标**: 控制 SM (Story Management) 阶段流程

**文件**: `autoBMAD/epic_automation/controllers/sm_controller.py`

**实现内容**:

```python
"""
SM Controller - Story Management Controller
控制 SM 阶段的业务流程
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Optional

import anyio

from .base_controller import StateDrivenController
from ..agents.sm_agent import SMAgent
from ..agents.state_agent import StateAgent

logger = logging.getLogger(__name__)


class SMController(StateDrivenController):
    """SM 阶段控制器"""

    def __init__(self, task_group: anyio.abc.TaskGroup, project_root: Optional[Path] = None):
        """
        初始化 SM 控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            project_root: 项目根目录
        """
        super().__init__(task_group)
        self.project_root = project_root
        self.sm_agent = SMAgent(project_root=str(project_root) if project_root else None)
        self.state_agent = StateAgent()
        self._log_execution("SMController initialized")

    async def execute(
        self,
        epic_content: str,
        story_id: str,
        tasks_path: Optional[str] = None
    ) -> bool:
        """
        执行 SM 阶段流程

        Args:
            epic_content: Epic 内容
            story_id: Story ID (如 "1.1", "1.2")
            tasks_path: 任务路径

        Returns:
            bool: 执行是否成功
        """
        self._log_execution(f"Starting SM phase for story {story_id}")

        try:
            # Step 1: 构造 SM 任务参数
            sm_config = self._build_sm_config(epic_content, story_id, tasks_path)

            # Step 2: 调用 SMAgent 生成故事
            await self._execute_within_taskgroup(
                self.sm_agent.execute(
                    story_content=epic_content,
                    story_path=f"{story_id}.md"
                )
            )

            # Step 3: 验证生成结果
            story_path = self._find_story_file(story_id)
            if not story_path:
                self._log_execution(f"Story file not found: {story_id}", "error")
                return False

            # Step 4: 验证故事内容
            if await self._validate_story_content(story_path):
                self._log_execution(f"SM phase completed successfully for story {story_id}")
                return True
            else:
                self._log_execution(f"Story validation failed for {story_id}", "error")
                return False

        except Exception as e:
            self._log_execution(f"SM phase failed: {e}", "error")
            return False

    def _build_sm_config(self, epic_content: str, story_id: str, tasks_path: Optional[str]) -> dict:
        """构造 SM 任务配置"""
        return {
            "epic_content": epic_content,
            "story_id": story_id,
            "tasks_path": tasks_path or str(Path.cwd() / "tasks")
        }

    def _find_story_file(self, story_id: str) -> Optional[Path]:
        """查找生成的故事文件"""
        if not self.project_root:
            return None

        stories_dir = self.project_root / "stories"
        pattern = f"{story_id}.md"
        matches = list(stories_dir.glob(pattern))
        return matches[0] if matches else None

    async def _validate_story_content(self, story_path: Path) -> bool:
        """验证故事文件内容"""
        try:
            content = story_path.read_text(encoding='utf-8')
            if not content or len(content) < 50:
                self._log_execution("Story content too short", "warning")
                return False

            # 解析故事状态
            status = await self.state_agent.parse_status(str(story_path))
            if not status:
                self._log_execution("Failed to parse story status", "warning")
                return False

            self._log_execution(f"Story status: {status}")
            return True

        except Exception as e:
            self._log_execution(f"Validation error: {e}", "error")
            return False

    async def _make_decision(self, current_state: str) -> str:
        """
        SM 阶段状态决策
        由于 SM 是单步流程，此方法通常不被调用
        """
        # SM 流程通常是：读取 Epic → 生成 Story → 完成
        # 不需要复杂的状态机
        return "Completed"
```

**集成点**：
1. **与 SMAgent 集成**: 调用现有的 SMAgent.execute()
2. **与 StateAgent 集成**: 验证生成的故事状态
3. **TaskGroup 生命周期**: 在 TaskGroup 内执行所有操作

#### 2.1.3 创建 StateAgent

**目标**: 提供统一的状态解析和状态管理

**文件**: `autoBMAD/epic_automation/agents/state_agent.py`

**实现内容**:

```python
"""
State Agent - 状态解析和管理 Agent
负责解析故事文件中的状态，转换为标准状态值
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from ..story_parser import SimpleStoryParser, core_status_to_processing

logger = logging.getLogger(__name__)


class StateAgent:
    """状态解析和管理 Agent"""

    def __init__(self):
        """初始化状态 Agent"""
        self.status_parser = SimpleStoryParser()
        self.logger = logging.getLogger(__name__)

    async def parse_status(self, story_path: str) -> Optional[str]:
        """
        解析故事文件的状态

        Args:
            story_path: 故事文件路径

        Returns:
            Optional[str]: 解析出的核心状态值，失败返回 None
        """
        try:
            if isinstance(story_path, (str, Path)):
                content = Path(story_path).read_text(encoding='utf-8')
            else:
                content = str(story_path)

            status = await self.status_parser.parse_status(content)
            if status:
                self.logger.debug(f"Parsed status: {status}")
                return status
            else:
                self.logger.warning("Status parser returned None")
                return None

        except Exception as e:
            self.logger.error(f"Failed to parse status: {e}")
            return None

    async def get_processing_status(self, story_path: str) -> Optional[str]:
        """
        获取处理状态值（数据库存储格式）

        Args:
            story_path: 故事文件路径

        Returns:
            Optional[str]: 处理状态值，失败返回 None
        """
        core_status = await self.parse_status(story_path)
        if core_status:
            return core_status_to_processing(core_status)
        return None

    async def update_story_status(self, story_path: str, status: str) -> bool:
        """
        更新故事状态（如果需要）

        Args:
            story_path: 故事文件路径
            status: 新的状态值

        Returns:
            bool: 更新是否成功
        """
        # StateAgent 主要用于解析，实际的状态更新由其他组件处理
        # 这里保留接口，便于扩展
        self.logger.info(f"Status update requested: {story_path} -> {status}")
        return True
```

#### 2.1.4 Day 1 验收标准

**代码验收**：
- [ ] `base_controller.py` 编译无错误
- [ ] `sm_controller.py` 编译无错误
- [ ] `state_agent.py` 编译无错误
- [ ] 所有导入正确解析

**功能验收**：
- [ ] SMController 可以实例化
- [ ] SMController.execute() 可以调用
- [ ] StateAgent.parse_status() 可以解析状态
- [ ] 集成测试通过

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_base_controller.py -v
pytest tests/unit/test_sm_controller.py -v

# 运行集成测试
pytest tests/integration/test_controller_agent_integration.py::test_sm_controller_flow -v
```

---

### 2.2 Day 2: DevQaController

#### 2.2.1 实现 DevQaController

**目标**: 控制 Dev-QA 状态机流水线

**文件**: `autoBMAD/epic_automation/controllers/devqa_controller.py`

**实现内容**:

```python
"""
DevQa Controller - Dev-QA 流水线控制器
控制开发-测试-审查的循环流程
"""
from __future__ import annotations
import logging
from typing import Optional

import anyio

from .base_controller import StateDrivenController
from ..agents.state_agent import StateAgent
from ..agents.dev_agent import DevAgent
from ..agents.qa_agent import QAAgent
from ..story_parser import ProcessingStatus

logger = logging.getLogger(__name__)


class DevQaController(StateDrivenController):
    """Dev-QA 流水线控制器"""

    def __init__(
        self,
        task_group: anyio.abc.TaskGroup,
        use_claude: bool = True,
        log_manager=None
    ):
        """
        初始化 DevQa 控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            use_claude: 是否使用 Claude 进行真实开发
            log_manager: 日志管理器
        """
        super().__init__(task_group)
        self.state_agent = StateAgent()
        self.dev_agent = DevAgent(use_claude=use_claude, log_manager=log_manager)
        self.qa_agent = QAAgent(use_claude=use_claude, log_manager=log_manager)
        self.max_rounds = 3
        self._log_execution("DevQaController initialized")

    async def execute(self, story_path: str) -> bool:
        """
        执行 Dev-QA 流水线

        Args:
            story_path: 故事文件路径

        Returns:
            bool: 执行是否成功
        """
        self._log_execution(f"Starting Dev-QA pipeline for {story_path}")

        try:
            # 启动状态机循环
            result = await self.run_state_machine(
                initial_state="Start",
                max_rounds=self.max_rounds
            )

            if result:
                self._log_execution("Dev-QA pipeline completed successfully")
            else:
                self._log_execution("Dev-QA pipeline did not complete within max rounds", "warning")

            return result

        except Exception as e:
            self._log_execution(f"Dev-QA pipeline failed: {e}", "error")
            return False

    async def run_pipeline(self, story_path: str, max_rounds: int = 3) -> bool:
        """
        运行 Dev-QA 流水线（别名方法）

        Args:
            story_path: 故事文件路径
            max_rounds: 最大轮数

        Returns:
            bool: 执行是否成功
        """
        return await self.execute(story_path)

    async def _make_decision(self, current_state: str) -> str:
        """
        基于当前状态做出 Dev-QA 决策

        Args:
            current_state: 当前状态

        Returns:
            str: 下一个状态
        """
        try:
            # 重新读取当前状态
            story_path = self._get_story_path()
            current_status = await self.state_agent.parse_status(story_path)

            if not current_status:
                self._log_execution("Failed to parse current status", "error")
                return "Failed"

            self._log_execution(f"Current status: {current_status}")

            # 状态决策逻辑
            if current_status in ["Done", "Ready for Done"]:
                self._log_execution("Story already completed")
                return current_status

            elif current_status in ["Draft", "Ready for Development", "Failed"]:
                # 需要开发
                self._log_execution("Development required")
                await self._execute_within_taskgroup(
                    self.dev_agent.execute(story_path)
                )
                return "AfterDev"

            elif current_status == "In Progress":
                # 继续开发或进入 QA
                self._log_execution("Development in progress")
                await self._execute_within_taskgroup(
                    self.dev_agent.execute(story_path)
                )
                return "AfterDev"

            elif current_status == "Ready for Review":
                # 需要 QA
                self._log_execution("QA required")
                await self._execute_within_taskgroup(
                    self.qa_agent.execute(story_path)
                )
                return "AfterQA"

            else:
                self._log_execution(f"Unknown status: {current_status}", "warning")
                return current_status

        except Exception as e:
            self._log_execution(f"Decision error: {e}", "error")
            return "Error"

    def _get_story_path(self) -> str:
        """获取故事文件路径"""
        # 这里需要根据实际调用时的参数确定
        # 暂时返回占位符，实际实现时需要调整
        return "current_story.md"

    def _is_termination_state(self, state: str) -> bool:
        """判断是否为 Dev-QA 的终止状态"""
        return state in ["Done", "Ready for Done", "Failed", "Error"]
```

**关键特性**：
1. **状态机循环**: 自动循环直到达到终止状态
2. **Dev/QA 决策**: 根据状态智能调用 Dev 或 QA Agent
3. **TaskGroup 隔离**: 所有 Agent 调用都在 TaskGroup 内执行
4. **迭代控制**: 防止无限循环

#### 2.2.2 集成 DevAgent 和 QAAgent

**目标**: 确保 DevAgent 和 QAAgent 与控制器的集成

**现有代码分析**：
- `dev_agent.py` 已经存在，需要重构以适应新架构
- `qa_agent.py` 已经存在，需要重构以适应新架构
- 两个 Agent 都使用 `SafeClaudeSDK`，需要集成

**重构策略**：
1. 保持现有 Agent 的核心逻辑不变
2. 添加 TaskGroup 支持
3. 优化异步执行流程
4. 增强错误处理

#### 2.2.3 Day 2 验收标准

**代码验收**：
- [ ] `devqa_controller.py` 编译无错误
- [ ] DevAgent 集成测试通过
- [ ] QAAgent 集成测试通过
- [ ] 状态机循环正常工作

**功能验收**：
- [ ] DevQaController 可以实例化
- [ ] 状态机循环最多运行 3 轮
- [ ] 根据状态正确调用 Dev/QA Agent
- [ ] 达到 "Done" 状态时正确终止

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_devqa_controller.py -v

# 运行集成测试
pytest tests/integration/test_state_machine_pipeline.py -v
```

---

### 2.3 Day 3: QualityController

#### 2.3.1 实现 QualityController

**目标**: 控制质量门控流程

**文件**: `autoBMAD/epic_automation/controllers/quality_controller.py`

**实现内容**:

```python
"""
Quality Controller - 质量门控控制器
控制代码质量检查流程（Ruff、BasedPyright、Pytest）
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import anyio

from .base_controller import BaseController
from ..agents.quality_agents import (
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent
)

logger = logging.getLogger(__name__)


class QualityController(BaseController):
    """质量门控控制器"""

    def __init__(
        self,
        task_group: anyio.abc.TaskGroup,
        project_root: Optional[Path] = None
    ):
        """
        初始化质量控制器

        Args:
            task_group: 控制器所属的 TaskGroup
            project_root: 项目根目录
        """
        super().__init__(task_group)
        self.project_root = project_root
        self.ruff_agent = RuffAgent()
        self.pyright_agent = BasedPyrightAgent()
        self.pytest_agent = PytestAgent()
        self._log_execution("QualityController initialized")

    async def execute(self, source_dir: Optional[str] = None, test_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        执行质量门控

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录

        Returns:
            Dict[str, Any]: 质量检查结果
        """
        self._log_execution("Starting quality gate process")

        results = {
            "overall_status": "pending",
            "checks": {}
        }

        try:
            # Step 1: Ruff 代码风格检查
            self._log_execution("Running Ruff checks")
            ruff_result = await self._execute_within_taskgroup(
                self.ruff_agent.execute(
                    source_dir=source_dir or str(self.project_root / "src"),
                    project_root=str(self.project_root) if self.project_root else None
                )
            )
            results["checks"]["ruff"] = ruff_result

            # Step 2: BasedPyright 类型检查
            self._log_execution("Running BasedPyright checks")
            pyright_result = await self._execute_within_taskgroup(
                self.pyright_agent.execute(
                    source_dir=source_dir or str(self.project_root / "src")
                )
            )
            results["checks"]["pyright"] = pyright_result

            # Step 3: Pytest 测试执行
            self._log_execution("Running Pytest")
            pytest_result = await self._execute_within_taskgroup(
                self.pytest_agent.execute(
                    source_dir=source_dir or str(self.project_root / "src"),
                    test_dir=test_dir or str(self.project_root / "tests")
                )
            )
            results["checks"]["pytest"] = pytest_result

            # Step 4: 汇总结果
            results["overall_status"] = self._evaluate_overall_status(results["checks"])

            self._log_execution(f"Quality gate completed: {results['overall_status']}")
            return results

        except Exception as e:
            self._log_execution(f"Quality gate failed: {e}", "error")
            results["overall_status"] = "error"
            results["error"] = str(e)
            return results

    def _evaluate_overall_status(self, checks: Dict[str, Any]) -> str:
        """
        评估整体质量状态

        Args:
            checks: 各检查项结果

        Returns:
            str: 整体状态
        """
        # 评估逻辑
        # 如果所有检查都通过，返回 pass
        # 如果有警告但无错误，返回 pass
        # 如果有错误，返回 fail

        has_error = False
        has_warning = False

        for check_name, result in checks.items():
            if isinstance(result, dict):
                if result.get("errors", 0) > 0:
                    has_error = True
                elif result.get("warnings", 0) > 0:
                    has_warning = True

        if has_error:
            return "fail"
        elif has_warning:
            return "pass_with_warnings"
        else:
            return "pass"
```

#### 2.3.2 重构 Quality Agents

**目标**: 重构 `quality_agents.py` 以适应新架构

**现有代码分析**：
- `quality_agents.py` 包含多个质量检查 Agent
- 需要提取为独立的 Agent 类
- 需要集成 TaskGroup 支持

**重构策略**：
```python
"""
重构后的 Quality Agents
"""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseQualityAgent(ABC):
    """质量检查 Agent 基类"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__module__}")

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行质量检查"""
        pass


class RuffAgent(BaseQualityAgent):
    """Ruff 代码风格检查 Agent"""

    def __init__(self):
        super().__init__("Ruff")

    async def execute(
        self,
        source_dir: str,
        project_root: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行 Ruff 检查

        Args:
            source_dir: 源代码目录
            project_root: 项目根目录

        Returns:
            Dict[str, Any]: 检查结果
        """
        self.logger.info("Running Ruff checks")

        try:
            # 这里会调用实际的 Ruff 工具
            # 现在返回模拟结果
            return {
                "status": "completed",
                "errors": 0,
                "warnings": 0,
                "files_checked": 10,
                "message": "No issues found"
            }
        except Exception as e:
            self.logger.error(f"Ruff check failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


class BasedPyrightAgent(BaseQualityAgent):
    """BasedPyright 类型检查 Agent"""

    def __init__(self):
        super().__init__("BasedPyright")

    async def execute(self, source_dir: str) -> Dict[str, Any]:
        """
        执行 BasedPyright 检查

        Args:
            source_dir: 源代码目录

        Returns:
            Dict[str, Any]: 检查结果
        """
        self.logger.info("Running BasedPyright checks")

        try:
            return {
                "status": "completed",
                "errors": 0,
                "warnings": 0,
                "files_checked": 10,
                "message": "No type issues found"
            }
        except Exception as e:
            self.logger.error(f"BasedPyright check failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


class PytestAgent(BaseQualityAgent):
    """Pytest 测试执行 Agent"""

    def __init__(self):
        super().__init__("Pytest")

    async def execute(
        self,
        source_dir: str,
        test_dir: str
    ) -> Dict[str, Any]:
        """
        执行 Pytest 测试

        Args:
            source_dir: 源代码目录
            test_dir: 测试目录

        Returns:
            Dict[str, Any]: 测试结果
        """
        self.logger.info("Running Pytest")

        try:
            return {
                "status": "completed",
                "tests_passed": 50,
                "tests_failed": 0,
                "tests_errors": 0,
                "coverage": 85.5,
                "message": "All tests passed"
            }
        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
```

#### 2.3.3 Day 3 验收标准

**代码验收**：
- [ ] `quality_controller.py` 编译无错误
- [ ] 所有 Quality Agent 编译无错误
- [ ] Ruff、BasedPyright、Pytest 集成测试通过
- [ ] 质量评估逻辑正确

**功能验收**：
- [ ] QualityController 可以实例化
- [ ] 三个质量检查顺序执行
- [ ] 结果汇总逻辑正确
- [ ] 错误处理机制有效

**测试验收**：
```bash
# 运行单元测试
pytest tests/unit/test_quality_controller.py -v

# 运行集成测试
pytest tests/integration/test_controller_agent_integration.py::test_quality_controller_flow -v
```

---

## 3. 集成策略

### 3.1 控制器与 Agent 集成

**集成模式**：
```
Controller (Layer 2)
  ↓ 控制
Agent (Layer 3)
  ↓ 委托
SDKExecutor (Layer 4)
```

**关键集成点**：
1. **TaskGroup 传递**: 控制器接收 TaskGroup 并传递给 Agent
2. **异步执行**: 所有 Agent 调用都在 TaskGroup 内执行
3. **状态共享**: 通过状态文件共享状态信息
4. **错误传播**: 错误从 Agent 传播到 Controller

### 3.2 与 Phase 1 的集成

**集成点**：
1. **TaskGroupManager**: 使用 Phase 1 创建的 TaskGroup 管理器
2. **SDKExecutor**: 控制器调用 SDKExecutor 而非直接调用 SDK
3. **CancellationManager**: 使用统一的取消管理机制

**示例代码**：
```python
# 在 Controller 中使用 Phase 1 的组件
from ..core.sdk_executor import SDKExecutor
from ..core.cancellation_manager import CancellationManager

class MyController(BaseController):
    async def execute(self):
        # 使用 SDKExecutor
        sdk_executor = SDKExecutor(self.task_group)
        result = await sdk_executor.execute_sdk_call(
            safe_sdk,
            "some_method",
            **kwargs
        )
        return result
```

### 3.3 与现有代码的迁移

**迁移策略**：
1. **保持现有接口**: 确保重构后的控制器保持原有 API 兼容
2. **渐进式替换**: 逐步替换现有代码，不破坏现有功能
3. **双轨测试**: 新旧代码并行测试，确保一致性

**迁移步骤**：
1. 创建新控制器（不影响现有代码）
2. 运行并行测试，验证结果一致
3. 更新 EpicDriver 使用新控制器
4. 移除旧代码

---

## 4. 测试策略

### 4.1 单元测试

**BaseController 测试**：
```python
# tests/unit/test_base_controller.py
import pytest
from autoBMAD.epic_automation.controllers.base_controller import BaseController

class TestController(BaseController):
    async def execute(self):
        return True

def test_base_controller_init():
    # 测试初始化
    pass

def test_execute_within_taskgroup():
    # 测试 TaskGroup 执行
    pass
```

**SMController 测试**：
```python
# tests/unit/test_sm_controller.py
import pytest
from pathlib import Path
from autoBMAD.epic_automation.controllers.sm_controller import SMController

@pytest.mark.anyio
async def test_sm_controller_execute():
    # 测试 SM 阶段执行
    pass

@pytest.mark.anyio
async def test_sm_controller_story_validation():
    # 测试故事验证
    pass
```

### 4.2 集成测试

**控制器-Agent 集成测试**：
```python
# tests/integration/test_controller_agent_integration.py
import pytest
from autoBMAD.epic_automation.controllers.sm_controller import SMController

@pytest.mark.anyio
async def test_sm_controller_with_sm_agent():
    """测试 SMController 与 SMAgent 的集成"""
    # 1. 创建测试故事文件
    # 2. 初始化 SMController
    # 3. 执行 SM 阶段
    # 4. 验证结果
    pass
```

**状态机流水线测试**：
```python
# tests/integration/test_state_machine_pipeline.py
import pytest
from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController

@pytest.mark.anyio
async def test_devqa_state_machine():
    """测试 Dev-QA 状态机流水线"""
    # 1. 创建测试故事（Draft 状态）
    # 2. 运行 Dev-QA 流水线
    # 3. 验证状态流转：Draft → In Progress → Ready for Review → Done
    pass
```

### 4.3 性能测试

**基准测试**：
```python
# tests/performance/test_controller_performance.py
import time
import pytest

@pytest.mark.performance
def test_controller_execution_time():
    """测试控制器执行时间"""
    start = time.time()
    # 执行控制器
    end = time.time()
    assert (end - start) < 5.0  # 5秒内完成
```

---

## 5. 风险评估与缓解

### 5.1 技术风险

**风险 1: TaskGroup 生命周期管理**
- **描述**: Cancel Scope 可能跨越 TaskGroup 边界
- **概率**: 中
- **影响**: 高
- **缓解**: 严格遵循 TaskGroup 嵌套规则，确保 RAII 清理

**风险 2: 状态机死循环**
- **描述**: 状态机可能进入无限循环
- **概率**: 低
- **影响**: 中
- **缓解**: 实施最大迭代次数限制

**风险 3: Agent 集成问题**
- **描述**: 现有 Agent 可能不兼容新架构
- **概率**: 中
- **影响**: 中
- **缓解**: 渐进式重构，保持向后兼容

### 5.2 质量风险

**风险 4: 功能回归**
- **描述**: 重构可能破坏现有功能
- **概率**: 中
- **影响**: 高
- **缓解**: 全面的 E2E 测试，双轨运行验证

**风险 5: 性能退化**
- **描述**: 新的架构可能引入性能开销
- **概率**: 低
- **影响**: 中
- **缓解**: 性能基准测试，优化关键路径

### 5.3 缓解措施

**措施 1: 持续集成测试**
- 每次代码提交后自动运行测试套件
- 监控测试通过率和性能指标

**措施 2: 代码审查**
- 所有代码变更必须经过审查
- 重点审查 TaskGroup 使用和状态管理逻辑

**措施 3: 渐进式部署**
- 先在开发环境验证
- 然后在测试环境验证
- 最后在生产环境部署

---

## 6. 验收标准

### 6.1 功能验收

**必须满足**：
- [ ] 三个控制器（SMController、DevQaController、QualityController）全部实现
- [ ] 控制器可以正确管理 Agent 生命周期
- [ ] 状态机循环正常工作，最多 3 轮迭代
- [ ] TaskGroup 隔离机制有效，Cancel Scope 不跨 Task

**期望达到**：
- [ ] 控制器响应时间 < 5 秒
- [ ] 状态机决策准确率 = 100%
- [ ] 错误处理覆盖率 > 90%

### 6.2 质量验收

**代码质量**：
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试覆盖率 > 90%
- [ ] 代码静态分析无 Critical 问题
- [ ] 代码审查通过率 = 100%

**文档质量**：
- [ ] API 文档完整（所有公共方法）
- [ ] 架构文档清晰（控制器设计）
- [ ] 示例代码可运行

### 6.3 性能验收

**性能指标**：
- [ ] SMController.execute() < 2 秒
- [ ] DevQaController.execute() < 10 秒（完整流水线）
- [ ] QualityController.execute() < 5 秒
- [ ] 内存占用 < 100 MB（单控制器实例）

### 6.4 验收测试套件

**运行命令**：
```bash
# 1. 单元测试
pytest tests/unit/test_base_controller.py -v
pytest tests/unit/test_sm_controller.py -v
pytest tests/unit/test_devqa_controller.py -v
pytest tests/unit/test_quality_controller.py -v

# 2. 集成测试
pytest tests/integration/test_controller_agent_integration.py -v
pytest tests/integration/test_state_machine_pipeline.py -v

# 3. 性能测试
pytest tests/performance/test_controller_performance.py -v

# 4. E2E 测试
pytest tests/e2e/test_full_pipeline.py -v
```

**验收标准**：
- 所有测试通过率 = 100%
- 性能测试全部达标
- 代码覆盖率达标

---

## 7. 后续工作

### 7.1 Phase 3 准备

**Agent 层重构**：
- 基于控制器需求，调整 Agent 接口
- 确保 Agent 与控制器的无缝集成
- 优化 Agent 的异步执行机制

### 7.2 EpicDriver 集成

**更新 EpicDriver**：
```python
# 在 epic_driver.py 中集成新控制器
class EpicDriver:
    async def run_story(self, story_path: str):
        async with create_task_group() as story_tg:
            # 使用新控制器
            sm_controller = SMController(story_tg)
            await sm_controller.execute(...)

            devqa_controller = DevQaController(story_tg)
            await devqa_controller.execute(story_path)

            quality_controller = QualityController(story_tg)
            await quality_controller.execute()
```

### 7.3 文档更新

**需要更新的文档**：
1. `ARCHITECTURE.md` - 更新控制器层说明
2. `API_REFERENCE.md` - 添加控制器 API 文档
3. `MIGRATION_GUIDE.md` - 添加从旧架构迁移的指南

---

## 8. 总结

### 8.1 实施价值

**架构价值**：
1. **清晰职责分离**: Controller 负责决策，Agent 负责实现
2. **状态驱动**: 基于统一的状态系统进行流程控制
3. **结构化并发**: AnyIO TaskGroup 提供生命周期隔离

**技术价值**：
1. **可维护性**: 控制器提供清晰的业务流程视图
2. **可测试性**: 每个控制器可以独立测试
3. **可扩展性**: 易于添加新的控制器和 Agent

### 8.2 关键成功因素

1. **严格遵循架构原则**: 不跨越层间依赖
2. **充分的测试覆盖**: 确保重构不破坏现有功能
3. **渐进式迁移**: 平滑过渡，避免激进变更
4. **持续验证**: 每个阶段完成后立即验证

### 8.3 里程碑检查点

**Day 1 结束检查**：
- [ ] BaseController 和 SMController 完成
- [ ] StateAgent 完成
- [ ] 相关测试通过

**Day 2 结束检查**：
- [ ] DevQaController 完成
- [ ] 状态机循环测试通过
- [ ] Dev/QA Agent 集成测试通过

**Day 3 结束检查**：
- [ ] QualityController 完成
- [ ] 三个质量检查工具集成测试通过
- [ ] 整体集成测试通过

**Phase 2 验收**：
- [ ] 所有控制器正常运行
- [ ] 与 Phase 1 SDK 执行层无缝集成
- [ ] 为 Phase 3 Agent 层重构做好准备

---

**下一步**: Phase 3: Agent 层重构 - [04-phase3-agents.md](04-phase3-agents.md)
