# EpicDriver协调机制

<cite>
**本文档引用的文件**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py)
- [state_manager.py](file://autoBMAD/epic_automation/state_manager.py)
- [log_manager.py](file://autoBMAD/epic_automation/log_manager.py)
- [devqa_controller.py](file://autoBMAD/epic_automation/controllers/devqa_controller.py)
</cite>

## 更新摘要
**已更改内容**
- 更新了 `execute_dev_phase` 方法的描述，说明其创建 `DevQaController` 来执行开发和QA循环
- 移除了关于 `execute_qa_phase` 方法的过时描述，因其已被弃用
- 重写了 `process_story_impl` 方法的工作流程，强调其由核心状态值驱动
- 更新了与 `StateManager` 和 `LogManager` 集成的描述
- 添加了新的代码示例以反映重构后的协调机制

## 目录
- [EpicDriver协调机制](#epicdriver协调机制)
  - [更新摘要](#更新摘要)
  - [目录](#目录)
  - [概述](#概述)
  - [核心组件](#核心组件)
    - [parse_epic 方法](#parse_epic-方法)
    - [execute_dev_phase 方法](#execute_dev_phase-方法)
    - [process_story_impl 方法](#process_story_impl-方法)
    - [execute_quality_gates 方法](#execute_quality_gates-方法)
  - [与状态和日志管理器的集成](#与状态和日志管理器的集成)
    - [StateManager 集成](#statemanager-集成)
    - [LogManager 集成](#logmanager-集成)
  - [错误处理与重试机制](#错误处理与重试机制)
  - [代码示例](#代码示例)

## 概述
EpicDriver 是 BMAD 自动化系统的主要协调器，负责驱动 SM-Dev-QA 工作流。它通过解析史诗（epic）文件来启动整个流程，并协调各个阶段的任务执行。EpicDriver 的核心职责是作为主工作流的驱动者，确保从故事解析到开发、测试直至质量门控的整个生命周期得以顺利完成。

## 核心组件
### parse_epic 方法
`parse_epic` 方法负责解析史诗文件并提取故事信息。该方法首先读取史诗文件的内容，然后使用正则表达式从文档中提取故事ID。它支持隐式编号关联，即从史诗文档中提取故事ID后，会根据文件名模式（如 001.xxx.md）在 `docs/stories/` 目录下搜索对应的故事文件，而无需在文档中显式地添加Markdown链接。

```python
async def parse_epic(self) -> list[dict[str, Any]]:
    """
    解析史诗markdown文件并提取故事信息。

    支持隐式编号关联：
    - 从史诗文档中提取故事ID
    - 根据文件名模式搜索故事文件（如 001.xxx.md）
    - 无需显式Markdown链接

    Returns:
        包含路径和元数据的故事字典列表
    """
```

### execute_dev_phase 方法
`execute_dev_phase` 方法是开发阶段的核心执行器。与旧版本不同，该方法不再直接调用 `DevAgent` 和 `QAAgent`，而是创建一个 `DevQaController` 实例来管理整个开发-测试循环。此重构将开发和QA的协调逻辑从 `EpicDriver` 中解耦，提高了代码的模块化和可维护性。

当 `execute_dev_phase` 被调用时，它会在一个 `anyio` 任务组中创建 `DevQaController` 实例，并传入必要的参数，如 `use_claude` 和 `log_manager`。然后，它调用 `DevQaController` 的 `execute` 方法来启动循环。此方法还包含一个安全机制，通过 `iteration` 参数防止无限循环。

**Section sources**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L1196-L1262)
- [devqa_controller.py](file://autoBMAD/epic_automation/controllers/devqa_controller.py#L18-L198)

### process_story_impl 方法
`process_story_impl` 方法是故事处理的核心实现，其工作流程完全由核心状态值驱动。这是本次重构的关键变化之一。旧版本的 `EpicDriver` 依赖于 `StateManager` 中的数据库状态来决定下一步操作，而新版本则完全依赖于 `StateAgent` 从故事文档中解析出的核心状态值。

该方法实现了一个循环，每次迭代都遵循以下步骤：
1.  **读取状态**：调用 `_parse_story_status` 方法获取故事的当前核心状态。
2.  **做出决策**：根据核心状态值（如 "Draft", "Ready for Development", "In Progress", "Ready for Review"）决定下一步是执行开发还是QA。
3.  **执行动作**：调用 `execute_dev_phase` 或 `execute_qa_phase` 来执行相应任务。
4.  **循环**：循环继续，直到故事状态变为 "Done" 或 "Ready for Done"。

这种基于核心状态值的驱动方式使得工作流更加健壮，因为它直接反映了故事文档中的真实状态，而不是可能滞后的数据库记录。

**Section sources**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L1321-L1441)

### execute_quality_gates 方法
`execute_quality_gates` 方法负责在开发-测试循环完成后执行一系列质量检查。它通过 `QualityGateOrchestrator` 类来协调 Ruff 代码格式化检查、BasedPyright 类型检查和 Pytest 单元测试的执行。该方法按顺序执行这些质量门控，并在任一检查失败时记录错误，但不会中断主工作流的执行，确保了流程的非阻塞性。

## 与状态和日志管理器的集成
### StateManager 集成
`EpicDriver` 与 `StateManager` 的集成主要用于持久化记录故事的处理状态。尽管 `process_story_impl` 的决策逻辑现在由核心状态值驱动，但 `StateManager` 仍然在后台发挥作用。例如，在 `execute_dev_phase` 和 `execute_sm_phase` 成功完成后，`EpicDriver` 会调用 `StateManager` 的 `update_story_status` 方法来更新数据库中的记录。这为报告和监控提供了数据支持。

```python
await self.state_manager.update_story_status(
    story_path=story_path, status="sm_completed", phase="sm"
)
```

**Section sources**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L1171-L1173)
- [state_manager.py](file://autoBMAD/epic_automation/state_manager.py#L223-L369)

### LogManager 集成
`EpicDriver` 通过 `LogManager` 实现了统一的日志记录系统。在 `__init__` 方法中，`EpicDriver` 会初始化 `LogManager` 实例，并通过 `init_logging` 和 `setup_dual_write` 函数配置日志系统。这使得日志可以同时输出到控制台和时间戳文件中，便于调试和审计。

```python
self.log_manager = LogManager(create_log_file=create_log_file)
init_logging(self.log_manager)
setup_dual_write(self.log_manager)
```

**Section sources**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L625-L628)
- [log_manager.py](file://autoBMAD/epic_automation/log_manager.py#L18-L466)

## 错误处理与重试机制
`EpicDriver` 实现了多层次的错误处理和重试机制。对于单个故事的处理，`process_story` 方法会捕获 `RuntimeError`，特别是与取消作用域（cancel scope）相关的错误，并将其视为非致命错误，允许工作流继续处理下一个故事。同时，`execute_dev_phase` 方法内置了基于 `max_iterations` 的安全机制，防止故事因持续失败而陷入无限循环。

## 代码示例
以下代码片段展示了 `EpicDriver` 如何协调 `DevQaController` 来执行开发-测试循环：

```python
async def execute_dev_phase(self, story_path: str, iteration: int = 1) -> bool:
    # 安全检查：防止超过最大迭代次数
    if iteration > self.max_iterations:
        logger.error(f"Max iterations ({self.max_iterations}) reached for {story_path}")
        await self.state_manager.update_story_status(
            story_path=story_path, status="failed", error="Max iterations exceeded"
        )
        return False

    try:
        # 在异步上下文中创建 DevQaController
        import anyio
        async with anyio.create_task_group() as tg:
            from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
            devqa_controller = DevQaController(
                tg,
                use_claude=self.use_claude,
                log_manager=self.log_manager
            )
            self.devqa_controller = devqa_controller

            # 执行完整的 Dev-QA 流水线
            result = await devqa_controller.execute(story_path)
            return result

    except Exception as e:
        logger.error(f"Dev phase failed for {story_path}: {e}")
        await self.state_manager.update_story_status(
            story_path=story_path, status="error", error=str(e)
        )
        return False
```

此示例清晰地展示了 `EpicDriver` 如何创建 `DevQaController` 并委托其执行复杂的开发-测试任务，体现了职责分离的设计原则。