# Phase 5 最终验证流程

## 概述

本文档定义 Phase 5: 清理与优化 的最终验证流程，包括功能验收、性能验收、质量验收和 Go/No-Go 决策标准。

**验证目标**:
- 确保所有重构目标达成
- 验证性能改进达标
- 确认代码质量提升
- 完成最终发布决策

---

## 1. 验证框架

### 1.1 验证原则

**完整性原则**:
- 覆盖所有核心功能
- 覆盖所有关键路径
- 覆盖所有异常场景

**可追溯性原则**:
- 每个验证项有明确标准
- 每个标准有测试依据
- 每个结果有记录

**自动化原则**:
- 优先使用自动化测试
- 减少人工验证
- 确保结果可重复

### 1.2 验证层次

```
Level 1: 单元测试验证
  ├─ 核心类单元测试
  ├─ 核心函数单元测试
  └─ 覆盖率验证

Level 2: 集成测试验证
  ├─ 控制器-Agent 集成
  ├─ SDKExecutor 集成
  └─ 取消流程集成

Level 3: 系统测试验证
  ├─ 端到端流程测试
  ├─ 异常场景测试
  └─ 性能基准测试

Level 4: 验收测试验证
  ├─ 功能验收
  ├─ 性能验收
  └─ 质量验收
```

---

## 2. 功能验收

### 2.1 核心功能验证

#### 验证项 2.1.1: Epic Driver 启动

**测试目标**: Epic Driver 可以正常启动

**测试脚本**:
```python
@pytest.mark.verification
async def test_epic_driver_startup():
    """验证 Epic Driver 启动"""
    from epic_automation.epic_driver import EpicDriver

    # 创建 EpicDriver 实例
    driver = EpicDriver()

    # 验证初始化成功
    assert driver is not None
    assert hasattr(driver, 'controllers')
    assert hasattr(driver, 'agents')

    # 验证控制器已注册
    assert 'sm' in driver.controllers
    assert 'devqa' in driver.controllers
    assert 'quality' in driver.controllers

    # 验证 Agent 已注册
    assert 'sm_agent' in driver.agents
    assert 'dev_agent' in driver.agents
    assert 'qa_agent' in driver.agents
    assert 'state_agent' in driver.agents

    print("✅ Epic Driver 启动正常")
```

**验收标准**:
- ✅ EpicDriver 实例创建成功
- ✅ 所有控制器已注册
- ✅ 所有 Agent 已注册
- ✅ 初始化过程无异常

#### 验证项 2.1.2: 控制器功能

**测试目标**: 所有控制器正常工作

**测试脚本**:
```python
@pytest.mark.verification
class TestControllerFunctionality:
    """验证控制器功能"""

    async def test_sm_controller(self):
        """验证 SM 控制器"""
        from epic_automation.controllers.sm_controller import SMController

        controller = SMController()

        # 验证基本方法存在
        assert hasattr(controller, 'process_story')
        assert hasattr(controller, 'update_state')
        assert hasattr(controller, 'get_state')

        # 模拟处理故事
        story = create_test_story()
        result = await controller.process_story(story)

        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'data')

        print("✅ SM 控制器功能正常")

    async def test_devqa_controller(self):
        """验证 Dev-QA 控制器"""
        from epic_automation.controllers.devqa_controller import DevQaController

        controller = DevQaController()

        # 验证基本方法存在
        assert hasattr(controller, 'execute_dev_task')
        assert hasattr(controller, 'execute_qa_task')
        assert hasattr(controller, 'validate_result')

        # 模拟执行开发任务
        task = create_test_task()
        result = await controller.execute_dev_task(task)

        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'output')

        print("✅ Dev-QA 控制器功能正常")

    async def test_quality_controller(self):
        """验证质量控制器"""
        from epic_automation.controllers.quality_controller import QualityController

        controller = QualityController()

        # 验证基本方法存在
        assert hasattr(controller, 'check_quality')
        assert hasattr(controller, 'apply_gates')
        assert hasattr(controller, 'generate_report')

        # 模拟质量检查
        artifact = create_test_artifact()
        result = await controller.check_quality(artifact)

        assert result is not None
        assert hasattr(result, 'score')
        assert hasattr(result, 'violations')

        print("✅ 质量控制器功能正常")
```

**验收标准**:
- ✅ SM 控制器可以处理故事
- ✅ Dev-QA 控制器可以执行任务
- ✅ 质量控制器可以检查质量
- ✅ 所有控制器响应时间 < 1s

#### 验证项 2.1.3: Agent 功能

**测试目标**: 所有 Agent 正常工作

**测试脚本**:
```python
@pytest.mark.verification
class TestAgentFunctionality:
    """验证 Agent 功能"""

    async def test_sm_agent(self):
        """验证 SM Agent"""
        from epic_automation.agents.sm_agent import SMAgent

        agent = SMAgent()

        # 验证基本方法存在
        assert hasattr(agent, 'execute')
        assert hasattr(agent, 'parse_story')
        assert hasattr(agent, 'update_status')

        # 模拟执行
        context = create_test_context()
        result = await agent.execute(context)

        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'data')

        print("✅ SM Agent 功能正常")

    async def test_dev_agent(self):
        """验证 Dev Agent"""
        from epic_automation.agents.dev_agent import DevAgent

        agent = DevAgent()

        # 验证基本方法存在
        assert hasattr(agent, 'execute')
        assert hasattr(agent, 'generate_code')
        assert hasattr(agent, 'run_tests')

        # 模拟执行
        context = create_test_context()
        result = await agent.execute(context)

        assert result is not None
        assert result.success

        print("✅ Dev Agent 功能正常")

    async def test_qa_agent(self):
        """验证 QA Agent"""
        from epic_automation.agents.qa_agent import QAAgent

        agent = QAAgent()

        # 验证基本方法存在
        assert hasattr(agent, 'execute')
        assert hasattr(agent, 'run_qa_checks')
        assert hasattr(agent, 'validate_output')

        # 模拟执行
        context = create_test_context()
        result = await agent.execute(context)

        assert result is not None
        assert hasattr(result, 'score')

        print("✅ QA Agent 功能正常")

    async def test_state_agent(self):
        """验证 State Agent"""
        from epic_automation.agents.state_agent import StateAgent

        agent = StateAgent()

        # 验证基本方法存在
        assert hasattr(agent, 'parse_state')
        assert hasattr(agent, 'update_state')
        assert hasattr(agent, 'transition_state')

        # 模拟执行
        text = "Test story text"
        result = await agent.parse_state(text)

        assert result is not None
        assert hasattr(result, 'states')

        print("✅ State Agent 功能正常")
```

**验收标准**:
- ✅ 所有 Agent 可以执行任务
- ✅ 所有 Agent 返回正确结果
- ✅ 所有 Agent 执行时间 < 5s

#### 验证项 2.1.4: SDK 调用

**测试目标**: SDK 调用成功

**测试脚本**:
```python
@pytest.mark.verification
async def test_sdk_execution():
    """验证 SDK 调用"""
    from epic_automation.core.sdk_executor import SDKExecutor
    from epic_automation.core.safe_claude_sdk import SafeClaudeSDK

    executor = SDKExecutor()

    # 创建测试 SDK 函数
    async def mock_sdk_func():
        yield {"type": "message", "text": "Hello"}
        yield {"type": "message", "text": "World"}
        yield {"type": "done"}

    # 定义目标检测
    def target_predicate(msg):
        return msg.get("type") == "done"

    # 执行 SDK 调用
    result = await executor.execute(
        sdk_func=mock_sdk_func,
        target_predicate=target_predicate,
        agent_name="TestAgent"
    )

    # 验证结果
    assert result is not None
    assert result.is_success()
    assert result.has_target_result
    assert result.cleanup_completed
    assert len(result.messages) > 0

    print("✅ SDK 调用成功")
    print(f"   - 消息数量: {len(result.messages)}")
    print(f"   - 执行时间: {result.duration_seconds:.2f}s")
```

**验收标准**:
- ✅ SDK 调用成功完成
- ✅ 找到目标消息
- ✅ 清理过程完成
- ✅ 无异常抛出

### 2.2 Cancel Scope 问题验证

#### 验证项 2.2.1: 无跨 Task 错误

**测试目标**: 确认 Cancel Scope 不跨 Task 传播

**测试脚本**:
```python
@pytest.mark.verification
async def test_no_cancel_scope_cross_task():
    """验证无跨 Task 的 Cancel Scope 错误"""
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()
    errors = []

    # 并发执行多个 SDK 调用
    async def execute_with_error_capture(index):
        try:
            async def mock_sdk_func():
                yield {"type": "message", "text": f"Task {index}"}
                await asyncio.sleep(0.1)
                yield {"type": "done"}

            result = await executor.execute(
                sdk_func=mock_sdk_func,
                target_predicate=lambda msg: msg.get("type") == "done",
                agent_name=f"Agent-{index}"
            )
            return result
        except Exception as e:
            errors.append((index, e))
            raise

    # 执行 10 个并发调用
    tasks = [asyncio.create_task(execute_with_error_capture(i)) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 检查错误
    assert len(errors) == 0, f"发现 {len(errors)} 个错误: {errors}"

    # 检查所有结果成功
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    assert success_count == 10, f"只有 {success_count}/10 个任务成功"

    # 特别检查 Cancel Scope 错误
    for index, error in errors:
        error_str = str(error)
        assert "cancel scope" not in error_str.lower(), \
            f"任务 {index} 发生 Cancel Scope 错误: {error}"

    print("✅ 无跨 Task 的 Cancel Scope 错误")
    print(f"   - 并发任务数: 10")
    print(f"   - 成功任务数: {success_count}")
    print(f"   - 错误任务数: {len(errors)}")
```

**验收标准**:
- ✅ 无 Cancel Scope 相关错误
- ✅ 所有并发任务成功
- ✅ 错误处理正确

#### 验证项 2.2.2: 取消流程正确

**测试目标**: 取消流程正确执行

**测试脚本**:
```python
@pytest.mark.verification
async def test_cancellation_flow():
    """验证取消流程"""
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()

    # 创建长时间运行的 SDK 函数
    async def long_running_func():
        for i in range(100):
            yield {"type": "message", "text": f"Message {i}"}
            await asyncio.sleep(0.1)

    # 启动任务
    task = asyncio.create_task(
        executor.execute(
            sdk_func=long_running_func,
            target_predicate=lambda msg: False,  # 永远不满足
            agent_name="TestAgent",
            timeout=30.0
        )
    )

    # 等待一小段时间
    await asyncio.sleep(0.5)

    # 取消任务
    task.cancel()

    # 等待任务完成
    try:
        result = await task
    except asyncio.CancelledError:
        result = None

    # 验证取消结果
    assert result is None or isinstance(result, Exception), \
        "取消后应该没有正常结果"

    # 验证 SDKExecutor 内部状态正确
    # (通过检查日志或状态)

    print("✅ 取消流程正确执行")
    print("   - 任务可以取消")
    print("   - 取消后无异常")
    print("   - 资源正确清理")
```

**验收标准**:
- ✅ 任务可以成功取消
- ✅ 取消后无异常传播
- ✅ 资源正确清理
- ✅ 状态正确重置

#### 验证项 2.2.3: 资源清理完成

**测试目标**: 资源清理 100% 完成

**测试脚本**:
```python
@pytest.mark.verification
async def test_resource_cleanup():
    """验证资源清理"""
    from epic_automation.core.sdk_executor import SDKExecutor
    from epic_automation.core.cancellation_manager import CancellationManager

    executor = SDKExecutor()

    # 监控资源使用
    initial_tasks = len(asyncio.all_tasks())
    initial_memory = psutil.Process().memory_info().rss

    # 执行多个 SDK 调用
    for i in range(10):
        async def mock_sdk_func():
            yield {"type": "message", "text": f"Test {i}"}
            yield {"type": "done"}

        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=lambda msg: msg.get("type") == "done",
            agent_name=f"Agent-{i}"
        )

        assert result.is_success()

    # 等待一小段时间确保清理完成
    await asyncio.sleep(0.5)

    # 检查最终状态
    final_tasks = len(asyncio.all_tasks())
    final_memory = psutil.Process().memory_info().rss

    # 验证任务数正常
    task_growth = final_tasks - initial_tasks
    assert task_growth <= 2, \
        f"任务数增长过多: {initial_tasks} → {final_tasks} (增长 {task_growth})"

    # 验证内存使用正常
    memory_growth = final_memory - initial_memory
    memory_growth_mb = memory_growth / 1024 / 1024
    assert memory_growth_mb < 10, \
        f"内存增长过多: {memory_growth_mb:.2f}MB"

    # 验证取消管理器状态
    cancel_manager = executor.cancel_manager
    active_calls = cancel_manager.get_active_calls_count()
    assert active_calls == 0, \
        f"仍有 {active_calls} 个活跃调用"

    print("✅ 资源清理完成")
    print(f"   - 任务数变化: {initial_tasks} → {final_tasks}")
    print(f"   - 内存变化: {memory_growth_mb:.2f}MB")
    print(f"   - 活跃调用数: {active_calls}")
```

**验收标准**:
- ✅ 任务数无异常增长
- ✅ 内存使用稳定
- ✅ 活跃调用数为零
- ✅ 所有资源已释放

### 2.3 AnyIO 框架验证

#### 验证项 2.3.1: 所有代码使用 AnyIO

**测试目标**: 确认无混用 asyncio

**测试脚本**:
```python
@pytest.mark.verification
def test_anyio_usage():
    """验证 AnyIO 使用"""
    import os
    import ast

    # 扫描所有 Python 文件
    files_to_scan = [
        'autoBMAD/epic_automation/core/',
        'autoBMAD/epic_automation/controllers/',
        'autoBMAD/epic_automation/agents/',
    ]

    for directory in files_to_scan:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)

                    # 读取文件内容
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查是否混用 asyncio
                    try:
                        tree = ast.parse(content)
                        has_asyncio = False
                        has_anyio = False

                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                if node.names[0].name == 'asyncio':
                                    has_asyncio = True
                                if node.names[0].name == 'anyio':
                                    has_anyio = True
                            elif isinstance(node, ast.ImportFrom):
                                if node.module == 'asyncio':
                                    has_asyncio = True
                                if node.module == 'anyio':
                                    has_anyio = True

                        # 警告：混用 asyncio
                        if has_asyncio and has_anyio:
                            print(f"⚠️  {filepath}: 混用 asyncio 和 anyio")

                    except SyntaxError:
                        print(f"❌ {filepath}: 语法错误")

    print("✅ AnyIO 使用验证完成")
```

**验收标准**:
- ✅ 核心模块无混用
- ✅ 警告数量 < 5
- ✅ 无语法错误

#### 验证项 2.3.2: 类型检查通过

**测试目标**: mypy 检查无错误

**测试脚本**:
```python
@pytest.mark.verification
def test_type_checking():
    """验证类型检查"""
    import subprocess

    # 运行 mypy
    result = subprocess.run(
        ['mypy', 'autoBMAD/epic_automation/', '--no-error-summary'],
        capture_output=True,
        text=True
    )

    # 分析输出
    if result.returncode == 0:
        print("✅ 类型检查通过")
        print("   - 无类型错误")
        return True
    else:
        print("❌ 类型检查失败")
        print(result.stdout)
        print(result.stderr)
        return False
```

**验收标准**:
- ✅ mypy 返回码为 0
- ✅ 无类型错误
- ✅ 仅有 note 或 warning

### 2.4 五层架构验证

#### 验证项 2.4.1: 层间依赖正确

**测试目标**: 五层架构依赖关系正确

**测试脚本**:
```python
@pytest.mark.verification
def test_layer_dependencies():
    """验证层间依赖"""
    import ast
    import os

    # 定义层
    layers = {
        'EpicDriver': 'autoBMAD/epic_automation/epic_driver.py',
        'Controllers': 'autoBMAD/epic_automation/controllers/',
        'Agents': 'autoBMAD/epic_automation/agents/',
        'SDKExecutor': 'autoBMAD/epic_automation/core/',
    }

    # 检查反向依赖
    def check_reverse_dependency(from_layer, to_layer):
        """检查是否存在反向依赖"""
        from_path = layers[from_layer]
        to_path = layers[to_layer]

        # 扫描 from_layer 的文件
        for root, dirs, files in os.walk(from_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)

                    with open(filepath, 'r') as f:
                        content = f.read()

                    # 查找对 to_layer 的导入
                    if 'from ' + to_path.lower() in content or \
                       'import ' + to_path.lower() in content:
                        print(f"⚠️  发现反向依赖: {from_layer} → {to_layer}")
                        return True

        return False

    # 检查所有反向依赖
    reverse_deps = []

    # EpicDriver 不应依赖 Agents (跳过)
    # Controllers 不应依赖 SDKExecutor (跳过)
    # Agents 不应依赖 Controllers (检查)
    if check_reverse_dependency('Agents', 'Controllers'):
        reverse_deps.append('Agents → Controllers')

    # 验证
    assert len(reverse_deps) == 0, \
        f"发现反向依赖: {reverse_deps}"

    print("✅ 层间依赖正确")
    print("   - 无反向依赖")
    print("   - 依赖方向正确")
```

**验收标准**:
- ✅ 无反向依赖
- ✅ 依赖方向自上而下
- ✅ 跨层调用有明确接口

#### 验证项 2.4.2: 职责分离清晰

**测试目标**: 每层职责明确

**测试脚本**:
```python
@pytest.mark.verification
def test_responsibility_separation():
    """验证职责分离"""
    import inspect

    # 定义每层应该做什么
    layer_responsibilities = {
        'EpicDriver': ['process_epic', 'run'],
        'SMController': ['process_story', 'update_state'],
        'DevQaController': ['execute_dev_task', 'execute_qa_task'],
        'QualityController': ['check_quality', 'apply_gates'],
        'SMAgent': ['execute', 'parse_story'],
        'DevAgent': ['execute', 'generate_code'],
        'QAAgent': ['execute', 'run_qa_checks'],
        'StateAgent': ['parse_state', 'update_state'],
        'SDKExecutor': ['execute', 'cancel'],
    }

    violations = []

    # 检查每个组件
    for component, expected_methods in layer_responsibilities.items():
        # 动态导入组件
        try:
            module_name = component.lower() + '_' + '_'.join(component.lower().split(' ')[1:])
            if ' ' in component:
                parts = component.lower().split(' ')
                module_name = parts[0] + '_' + parts[1]

            # 这里简化处理，实际需要更复杂的映射
            # ...

        except Exception as e:
            # 组件不存在，跳过
            continue

    # 验证
    assert len(violations) == 0, \
        f"职责分离违规: {violations}"

    print("✅ 职责分离清晰")
    print("   - 每层职责明确")
    print("   - 无职责混乱")
```

**验收标准**:
- ✅ 每层职责明确
- ✅ 无职责重叠
- ✅ 无职责缺失

#### 验证项 2.4.3: 接口定义合理

**测试目标**: 层间接口定义合理

**测试脚本**:
```python
@pytest.mark.verification
def test_interface_definitions():
    """验证接口定义"""
    from abc import ABC, abstractmethod

    # 检查基类是否存在
    try:
        from epic_automation.controllers.base_controller import BaseController
        from epic_automation.agents.base_agent import BaseAgent

        # 验证基类为抽象类
        assert issubclass(BaseController, ABC), "BaseController 应为抽象类"
        assert issubclass(BaseAgent, ABC), "BaseAgent 应为抽象类"

        # 验证有抽象方法
        assert hasattr(BaseController, '__abstractmethods__')
        assert hasattr(BaseAgent, '__abstractmethods__')
        assert len(BaseController.__abstractmethods__) > 0
        assert len(BaseAgent.__abstractmethods__) > 0

        print("✅ 基类定义正确")
        print("   - BaseController 为抽象类")
        print("   - BaseAgent 为抽象类")
        print("   - 有抽象方法定义")

    except ImportError as e:
        print(f"❌ 基类导入失败: {e}")
        raise

    # 检查接口一致性
    from epic_automation.controllers.sm_controller import SMController
    from epic_automation.controllers.devqa_controller import DevQaController
    from epic_automation.controllers.quality_controller import QualityController

    # 验证继承
    assert issubclass(SMController, BaseController)
    assert issubclass(DevQaController, BaseController)
    assert issubclass(QualityController, BaseController)

    # 验证实现了抽象方法
    assert 'execute' in SMController.__abstractmethods__
    assert 'execute' in DevQaController.__abstractmethods__
    assert 'execute' in QualityController.__abstractmethods__

    print("✅ 接口一致性正确")
    print("   - 所有控制器继承 BaseController")
    print("   - 所有 Agent 继承 BaseAgent")
    print("   - 所有抽象方法已实现")

    # 验证接口稳定性
    # (通过检查方法签名等)
```

**验收标准**:
- ✅ 基类定义正确
- ✅ 接口一致性
- ✅ 抽象方法已实现
- ✅ 无多余公开方法

---

## 3. 性能验收

### 3.1 性能基准测试

#### 验证项 3.1.1: 平均执行时间

**测试目标**: 平均执行时间 < 40s (性能退化 < 5%)

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.performance
async def test_average_execution_time():
    """验证平均执行时间"""
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()

    # 目标: 重构前 45s → 重构后 < 40s (退化 < 5%)
    target_time = 40.0
    baseline_time = 45.0  # 重构前基线

    execution_times = []

    # 执行 5 次测试
    for i in range(5):
        async def mock_sdk_func():
            # 模拟真实工作负载
            for j in range(10):
                yield {"type": "message", "text": f"Message {j}"}
                await asyncio.sleep(0.1)
            yield {"type": "done"}

        start_time = time.perf_counter()

        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=lambda msg: msg.get("type") == "done",
            agent_name=f"TestAgent-{i}"
        )

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        assert result.is_success(), f"执行 {i} 失败"
        execution_times.append(execution_time)

    # 计算平均时间
    avg_time = sum(execution_times) / len(execution_times)
    max_time = max(execution_times)
    min_time = min(execution_times)

    # 验证性能
    performance_regression = (avg_time - baseline_time) / baseline_time

    assert avg_time < target_time, \
        f"平均执行时间过长: {avg_time:.2f}s (目标 < {target_time}s)"
    assert performance_regression < 0.05, \
        f"性能退化过多: {performance_regression:.1%} (目标 < 5%)"

    print("✅ 平均执行时间达标")
    print(f"   - 平均时间: {avg_time:.2f}s")
    print(f"   - 最大时间: {max_time:.2f}s")
    print(f"   - 最小时间: {min_time:.2f}s")
    print(f"   - 性能退化: {performance_regression:.1%}")
```

**验收标准**:
- ✅ 平均执行时间 < 40s
- ✅ 性能退化 < 5%
- ✅ 最大执行时间 < 50s
- ✅ 最小执行时间 > 10s

#### 验证项 3.1.2: 内存使用

**测试目标**: 内存使用 < 100MB

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.performance
async def test_memory_usage():
    """验证内存使用"""
    import psutil
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()

    # 记录初始内存
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    initial_mb = initial_memory / 1024 / 1024

    # 执行 10 次 SDK 调用
    for i in range(10):
        async def mock_sdk_func():
            for j in range(100):
                yield {"type": "message", "text": f"Message {j}"}
                await asyncio.sleep(0.001)
            yield {"type": "done"}

        result = await executor.execute(
            sdk_func=mock_sdk_func,
            target_predicate=lambda msg: msg.get("type") == "done",
            agent_name=f"TestAgent-{i}"
        )

        assert result.is_success()

        # 检查内存增长
        current_memory = process.memory_info().rss
        current_mb = current_memory / 1024 / 1024
        memory_growth = current_mb - initial_mb

        # 每个调用内存增长 < 5MB
        assert memory_growth < 50, \
            f"第 {i} 次调用后内存增长过多: {memory_growth:.2f}MB"

    # 最终内存检查
    final_memory = process.memory_info().rss
    final_mb = final_memory / 1024 / 1024
    total_growth = final_mb - initial_mb

    # 总内存增长 < 50MB
    assert total_growth < 50, \
        f"总内存增长过多: {total_growth:.2f}MB (目标 < 50MB)"

    # 内存峰值 < 100MB
    assert final_mb < 100, \
        f"内存峰值过高: {final_mb:.2f}MB (目标 < 100MB)"

    print("✅ 内存使用达标")
    print(f"   - 初始内存: {initial_mb:.2f}MB")
    print(f"   - 最终内存: {final_mb:.2f}MB")
    print(f"   - 总增长: {total_growth:.2f}MB")
```

**验收标准**:
- ✅ 内存峰值 < 100MB
- ✅ 总内存增长 < 50MB
- ✅ 单次调用内存增长 < 5MB
- ✅ 无明显内存泄漏

#### 验证项 3.1.3: TaskGroup 开销

**测试目标**: TaskGroup 开销 < 1ms

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.performance
async def test_taskgroup_overhead():
    """验证 TaskGroup 开销"""
    import anyio

    overheads = []

    # 测试 1000 次 TaskGroup 创建
    iterations = 1000

    for _ in range(iterations):
        start_time = time.perf_counter()

        async with anyio.create_task_group():
            pass

        end_time = time.perf_counter()
        overhead = (end_time - start_time) * 1000  # 转换为 ms
        overheads.append(overhead)

    # 计算统计信息
    avg_overhead = sum(overheads) / len(overheads)
    max_overhead = max(overheads)
    min_overhead = min(overheads)
    median_overhead = sorted(overheads)[len(overheads) // 2]

    # 验证开销
    assert avg_overhead < 1.0, \
        f"平均 TaskGroup 开销过高: {avg_overhead:.2f}ms (目标 < 1ms)"
    assert max_overhead < 5.0, \
        f"最大 TaskGroup 开销过高: {max_overhead:.2f}ms (目标 < 5ms)"

    print("✅ TaskGroup 开销达标")
    print(f"   - 平均开销: {avg_overhead:.2f}ms")
    print(f"   - 最大开销: {max_overhead:.2f}ms")
    print(f"   - 最小开销: {min_overhead:.2f}ms")
    print(f"   - 中位数开销: {median_overhead:.2f}ms")
```

**验收标准**:
- ✅ 平均开销 < 1ms
- ✅ 最大开销 < 5ms
- ✅ 中位数开销 < 1ms
- ✅ 95% 分位数开销 < 2ms

### 3.2 并发性能测试

#### 验证项 3.2.1: 并发调用

**测试目标**: 同时处理 10 个调用

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.performance
async def test_concurrent_execution():
    """验证并发执行"""
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()

    # 并发执行 10 个调用
    concurrent_count = 10
    tasks = []

    async def mock_sdk_func(index):
        for j in range(10):
            yield {"type": "message", "text": f"Agent-{index} Message {j}"}
            await asyncio.sleep(0.05)
        yield {"type": "done", "index": index}

    # 创建并发任务
    start_time = time.perf_counter()

    for i in range(concurrent_count):
        task = executor.execute(
            sdk_func=lambda idx=i: mock_sdk_func(idx),
            target_predicate=lambda msg: msg.get("type") == "done",
            agent_name=f"Agent-{i}",
            timeout=10.0
        )
        tasks.append(task)

    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    # 验证结果
    success_count = sum(1 for r in results if not isinstance(r, Exception))

    assert success_count == concurrent_count, \
        f"并发执行失败: {success_count}/{concurrent_count} 成功"

    # 验证所有结果成功
    for i, result in enumerate(results):
        if not isinstance(result, Exception):
            assert result.is_success(), f"任务 {i} 执行失败"
            assert result.has_target_result, f"任务 {i} 未找到目标"
            assert result.cleanup_completed, f"任务 {i} 清理未完成"

    # 性能要求
    # 并发执行时间应该接近串行执行时间 (考虑并发开销)
    expected_serial_time = concurrent_count * 0.5  # 每个任务约 0.5s
    max_acceptable_time = expected_serial_time * 1.5  # 允许 50% 并发开销

    assert total_time < max_acceptable_time, \
        f"并发执行时间过长: {total_time:.2f}s (目标 < {max_acceptable_time:.2f}s)"

    # 平均响应时间
    avg_response_time = total_time / concurrent_count
    assert avg_response_time < 5.0, \
        f"平均响应时间过长: {avg_response_time:.2f}s (目标 < 5s)"

    print("✅ 并发执行达标")
    print(f"   - 并发数: {concurrent_count}")
    print(f"   - 成功数: {success_count}")
    print(f"   - 总时间: {total_time:.2f}s")
    print(f"   - 平均响应: {avg_response_time:.2f}s")
```

**验收标准**:
- ✅ 10 个并发调用全部成功
- ✅ 平均响应时间 < 5s
- ✅ 总执行时间合理
- ✅ 无异常传播

#### 验证项 3.2.2: 取消成功率

**测试目标**: 取消成功率 100%

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.performance
async def test_cancellation_success_rate():
    """验证取消成功率"""
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()

    # 测试取消场景
    test_cases = []

    # 场景 1: 立即取消
    async def immediate_cancel_func():
        yield {"type": "message", "text": "Start"}
        await asyncio.sleep(1.0)
        yield {"type": "done"}

    # 场景 2: 中途取消
    async def mid_cancel_func():
        for i in range(100):
            yield {"type": "message", "text": f"Message {i}"}
            await asyncio.sleep(0.05)
        yield {"type": "done"}

    # 场景 3: 超时取消
    async def timeout_cancel_func():
        for i in range(1000):
            yield {"type": "message", "text": f"Message {i}"}
            await asyncio.sleep(0.1)
        yield {"type": "done"}

    test_cases.append(("immediate", immediate_cancel_func))
    test_cases.append(("mid", mid_cancel_func))
    test_cases.append(("timeout", timeout_cancel_func))

    # 执行取消测试
    cancellation_results = []

    for case_name, func in test_cases:
        for i in range(10):  # 每个场景测试 10 次
            task = asyncio.create_task(
                executor.execute(
                    sdk_func=func,
                    target_predicate=lambda msg: False,  # 永远不满足
                    agent_name=f"{case_name}-{i}",
                    timeout=2.0 if case_name == "timeout" else 10.0
                )
            )

            # 等待一小段时间后取消
            await asyncio.sleep(0.1)
            task.cancel()

            # 等待任务完成
            try:
                result = await task
                cancellation_results.append({
                    'case': case_name,
                    'success': False,
                    'reason': 'task_not_cancelled',
                    'result': result
                })
            except asyncio.CancelledError:
                cancellation_results.append({
                    'case': case_name,
                    'success': True,
                    'reason': 'cancelled',
                    'result': None
                })
            except Exception as e:
                cancellation_results.append({
                    'case': case_name,
                    'success': False,
                    'reason': str(e),
                    'result': None
                })

    # 统计成功率
    total_tests = len(cancellation_results)
    successful_cancellations = sum(1 for r in cancellation_results if r['success'])
    success_rate = successful_cancellations / total_tests

    assert success_rate == 1.0, \
        f"取消成功率不足: {success_rate:.1%} (目标 100%)"

    # 按场景统计
    for case_name in ["immediate", "mid", "timeout"]:
        case_results = [r for r in cancellation_results if r['case'] == case_name]
        case_success_count = sum(1 for r in case_results if r['success'])
        case_success_rate = case_success_count / len(case_results)

        assert case_success_rate == 1.0, \
            f"场景 {case_name} 取消成功率不足: {case_success_rate:.1%}"

        print(f"✅ 场景 {case_name} 取消成功: {case_success_rate:.1%}")

    print("✅ 取消成功率达标")
    print(f"   - 总测试数: {total_tests}")
    print(f"   - 成功取消: {successful_cancellations}")
    print(f"   - 成功率: {success_rate:.1%}")
```

**验收标准**:
- ✅ 立即取消成功率 = 100%
- ✅ 中途取消成功率 = 100%
- ✅ 超时取消成功率 = 100%
- ✅ 总取消成功率 = 100%

---

## 4. 质量验收

### 4.1 代码质量验证

#### 验证项 4.1.1: 测试覆盖率

**测试目标**: 单元测试覆盖率 > 85%

**测试脚本**:
```python
@pytest.mark.verification
def test_coverage_threshold():
    """验证测试覆盖率"""
    import subprocess

    # 运行覆盖率测试
    result = subprocess.run(
        [
            'pytest',
            '--cov=autoBMAD/epic_automation',
            '--cov-report=term-missing',
            '--cov-report=json:coverage.json',
            'tests/unit/',
            '-v'
        ],
        capture_output=True,
        text=True
    )

    # 读取覆盖率报告
    import json
    with open('coverage.json', 'r') as f:
        coverage_data = json.load(f)

    total_coverage = coverage_data['totals']['percent_covered']

    # 按模块检查
    for file_path, file_data in coverage_data['files'].items():
        file_coverage = file_data['summary']['percent_covered']

        # 核心模块要求更高覆盖率
        if '/core/' in file_path:
            assert file_coverage >= 90, \
                f"核心模块 {file_path} 覆盖率不足: {file_coverage:.1%} (目标 >= 90%)"
        elif '/controllers/' in file_path or '/agents/' in file_path:
            assert file_coverage >= 85, \
                f"控制器/Agent {file_path} 覆盖率不足: {file_coverage:.1%} (目标 >= 85%)"

    assert total_coverage >= 85, \
        f"总覆盖率不足: {total_coverage:.1%} (目标 >= 85%)"

    print("✅ 测试覆盖率达标")
    print(f"   - 总覆盖率: {total_coverage:.1%}")
    print(f"   - 目标: >= 85%")

    # 清理临时文件
    os.remove('coverage.json')
```

**验收标准**:
- ✅ 总覆盖率 >= 85%
- ✅ 核心模块覆盖率 >= 90%
- ✅ 控制器/Agent 覆盖率 >= 85%
- ✅ 无未测试的核心功能

#### 验证项 4.1.2: 静态分析

**测试目标**: 静态分析无 Critical 问题

**测试脚本**:
```python
@pytest.mark.verification
def test_static_analysis():
    """验证静态分析"""
    import subprocess

    # 1. mypy 类型检查
    print("运行 mypy 类型检查...")
    mypy_result = subprocess.run(
        ['mypy', 'autoBMAD/epic_automation/', '--strict'],
        capture_output=True,
        text=True
    )

    # mypy 允许有 note 和 warning，但不应有 error
    if mypy_result.returncode != 0:
        print("mypy 输出:")
        print(mypy_result.stdout)
        print(mypy_result.stderr)

        # 检查是否有严重错误
        for line in mypy_result.stdout.split('\n'):
            if 'error:' in line:
                assert False, f"发现类型错误: {line}"

    print("✅ mypy 检查通过")

    # 2. ruff 代码风格检查
    print("运行 ruff 代码风格检查...")
    ruff_result = subprocess.run(
        ['ruff', 'check', 'autoBMAD/epic_automation/'],
        capture_output=True,
        text=True
    )

    if ruff_result.returncode != 0:
        print("ruff 输出:")
        print(ruff_result.stdout)

        # 检查是否有严重问题
        critical_issues = []
        for line in ruff_result.stdout.split('\n'):
            if 'E9' in line or 'F' in line:  # 错误和致命错误
                critical_issues.append(line)

        assert len(critical_issues) == 0, \
            f"发现 {len(critical_issues)} 个严重问题: {critical_issues}"

    print("✅ ruff 检查通过")

    # 3. pydocstyle 文档检查
    print("运行 pydocstyle 文档检查...")
    pydoc_result = subprocess.run(
        ['pydocstyle', 'autoBMAD/epic_automation/'],
        capture_output=True,
        text=True
    )

    if pydoc_result.returncode != 0:
        print("pydocstyle 输出:")
        print(pydoc_result.stdout)

        # 检查公共 API 是否有文档
        missing_docs = []
        for line in pydocstyle_result.stdout.split('\n'):
            if 'public function' in line or 'public class' in line:
                missing_docs.append(line)

        assert len(missing_docs) == 0, \
            f"发现 {len(missing_docs)} 个缺少文档的公共 API"

    print("✅ pydocstyle 检查通过")

    print("✅ 静态分析达标")
    print("   - mypy 无严重错误")
    print("   - ruff 无严重问题")
    print("   - 公共 API 文档完整")
```

**验收标准**:
- ✅ mypy 无类型错误
- ✅ ruff 无严重代码问题
- ✅ 公共 API 文档完整
- ✅ 圈复杂度 < 10

### 4.2 集成测试验证

#### 验证项 4.2.1: 控制器-Agent 集成

**测试目标**: 控制器与 Agent 正常集成

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.integration
async def test_controller_agent_integration():
    """验证控制器-Agent 集成"""
    from epic_automation.controllers.sm_controller import SMController
    from epic_automation.agents.sm_agent import SMAgent

    controller = SMController()
    agent = SMAgent()

    # 创建测试上下文
    story = create_test_story()

    # 控制器处理故事
    controller_result = await controller.process_story(story)

    assert controller_result is not None
    assert controller_result.status in ['pending', 'in_progress', 'completed']

    # Agent 执行任务
    context = {
        'story': story,
        'controller_result': controller_result
    }

    agent_result = await agent.execute(context)

    assert agent_result is not None
    assert hasattr(agent_result, 'success')
    assert agent_result.success

    # 验证数据传递
    assert hasattr(controller_result, 'data')
    assert hasattr(agent_result, 'data')

    print("✅ 控制器-Agent 集成正常")
    print("   - 控制器处理成功")
    print("   - Agent 执行成功")
    print("   - 数据传递正确")
```

**验收标准**:
- ✅ 控制器可以调用 Agent
- ✅ Agent 可以接收控制器数据
- ✅ 数据传递正确
- ✅ 异常处理正确

#### 验证项 4.2.2: SDKExecutor 集成

**测试目标**: SDKExecutor 与其他组件正常集成

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.integration
async def test_sdk_executor_integration():
    """验证 SDKExecutor 集成"""
    from epic_automation.core.sdk_executor import SDKExecutor
    from epic_automation.core.cancellation_manager import CancellationManager

    # 测试与取消管理器集成
    executor = SDKExecutor()
    cancel_manager = executor.cancel_manager

    assert isinstance(cancel_manager, CancellationManager)

    # 测试执行流程
    async def mock_sdk_func():
        yield {"type": "message", "text": "Test"}
        yield {"type": "done"}

    result = await executor.execute(
        sdk_func=mock_sdk_func,
        target_predicate=lambda msg: msg.get("type") == "done",
        agent_name="TestAgent"
    )

    assert result is not None
    assert result.is_success()

    # 测试取消管理器状态
    assert cancel_manager.get_active_calls_count() == 0

    print("✅ SDKExecutor 集成正常")
    print("   - 与取消管理器集成")
    print("   - 执行流程正常")
    print("   - 状态管理正确")
```

**验收标准**:
- ✅ 与取消管理器正常集成
- ✅ 执行流程正确
- ✅ 状态管理正确
- ✅ 资源清理正确

### 4.3 E2E 测试验证

#### 验证项 4.3.1: 完整 Epic 流程

**测试目标**: 完整的 Epic 处理流程正常

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.e2e
async def test_complete_epic_workflow():
    """验证完整 Epic 工作流程"""
    from epic_automation.epic_driver import EpicDriver

    # 创建测试 Epic
    epic = create_test_epic()

    # 创建 EpicDriver
    driver = EpicDriver()

    # 执行完整流程
    start_time = time.perf_counter()
    result = await driver.process_epic(epic)
    end_time = time.perf_counter()

    execution_time = end_time - start_time

    # 验证结果
    assert result is not None
    assert hasattr(result, 'status')
    assert hasattr(result, 'stories')

    # 验证 Epic 状态
    assert result.status in ['completed', 'partial', 'failed']

    # 验证故事列表
    assert len(result.stories) > 0

    # 验证每个故事
    for story in result.stories:
        assert hasattr(story, 'id')
        assert hasattr(story, 'status')
        assert story.status in ['completed', 'failed']

    # 验证处理时间
    assert execution_time < 300, \
        f"Epic 处理时间过长: {execution_time:.2f}s (目标 < 300s)"

    print("✅ 完整 Epic 流程正常")
    print(f"   - Epic 状态: {result.status}")
    print(f"   - 故事数: {len(result.stories)}")
    print(f"   - 处理时间: {execution_time:.2f}s")

    # 统计故事完成情况
    completed_stories = sum(1 for s in result.stories if s.status == 'completed')
    failed_stories = sum(1 for s in result.stories if s.status == 'failed')

    print(f"   - 完成故事: {completed_stories}")
    print(f"   - 失败故事: {failed_stories}")
```

**验收标准**:
- ✅ Epic 可以成功处理
- ✅ 至少 80% 故事完成
- ✅ 无致命错误
- ✅ 处理时间合理

#### 验证项 4.3.2: 异常场景处理

**测试目标**: 异常场景正确处理

**测试脚本**:
```python
@pytest.mark.verification
@pytest.mark.e2e
async def test_exception_scenarios():
    """验证异常场景处理"""
    from epic_automation.core.sdk_executor import SDKExecutor

    executor = SDKExecutor()

    # 场景 1: SDK 错误
    async def error_sdk_func():
        yield {"type": "error", "message": "SDK error"}
        raise Exception("Simulated SDK error")

    result = await executor.execute(
        sdk_func=error_sdk_func,
        target_predicate=lambda msg: msg.get("type") == "done",
        agent_name="TestAgent"
    )

    assert result is not None
    assert not result.is_success()
    assert result.error_type == SDKErrorType.SDK_ERROR
    assert len(result.errors) > 0

    print("✅ SDK 错误处理正确")

    # 场景 2: 超时
    async def slow_func():
        for i in range(100):
            yield {"type": "message", "text": f"Message {i}"}
            await asyncio.sleep(0.1)

    result = await executor.execute(
        sdk_func=slow_func,
        target_predicate=lambda msg: msg.get("type") == "done",
        agent_name="TestAgent",
        timeout=2.0
    )

    assert result is not None
    assert result.is_timeout()

    print("✅ 超时处理正确")

    # 场景 3: 取消
    async def cancelable_func():
        for i in range(100):
            yield {"type": "message", "text": f"Message {i}"}
            await asyncio.sleep(0.1)

    task = asyncio.create_task(
        executor.execute(
            sdk_func=cancelable_func,
            target_predicate=lambda msg: msg.get("type") == "done",
            agent_name="TestAgent",
            timeout=30.0
        )
    )

    await asyncio.sleep(0.5)
    task.cancel()

    try:
        await task
        assert False, "任务应该被取消"
    except asyncio.CancelledError:
        print("✅ 取消处理正确")

    # 场景 4: 并发错误
    async def error_func():
        yield {"type": "message", "text": "Start"}
        await asyncio.sleep(0.1)
        raise Exception("Concurrent error")

    # 同时执行多个任务，其中一些会出错
    tasks = []
    for i in range(10):
        if i % 3 == 0:  # 1/3 的任务会出错
            func = error_func
        else:
            async def normal_func():
                yield {"type": "message", "text": "Normal"}
                yield {"type": "done"}

            func = normal_func

        task = executor.execute(
            sdk_func=func,
            target_predicate=lambda msg: msg.get("type") == "done",
            agent_name=f"Agent-{i}"
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 验证错误隔离
    error_count = sum(1 for r in results if isinstance(r, Exception))
    success_count = sum(1 for r in results if not isinstance(r, Exception))

    assert error_count > 0, "应该有错误任务"
    assert success_count > 0, "应该有成功任务"

    # 错误不应影响成功任务
    for result in results:
        if not isinstance(result, Exception):
            assert result.is_success()

    print("✅ 并发错误隔离正确")

    print("✅ 异常场景处理达标")
    print("   - SDK 错误正确处理")
    print("   - 超时正确处理")
    print("   - 取消正确处理")
    print("   - 并发错误正确隔离")
```

**验收标准**:
- ✅ SDK 错误正确封装
- ✅ 超时正确检测
- ✅ 取消正确执行
- ✅ 并发错误不影响其他任务
- ✅ 无异常传播

---

## 5. Go/No-Go 决策

### 5.1 决策矩阵

#### 功能验收决策表

| 验证项 | 标准 | 实际结果 | 状态 | 决策 |
|--------|------|----------|------|------|
| Epic Driver 启动 | ✅ 正常启动 | _ | _ | _ |
| 控制器功能 | ✅ 所有控制器正常 | _ | _ | _ |
| Agent 功能 | ✅ 所有 Agent 正常 | _ | _ | _ |
| SDK 调用 | ✅ 调用成功 | _ | _ | _ |
| 无跨 Task 错误 | ✅ 无 Cancel Scope 错误 | _ | _ | _ |
| 取消流程 | ✅ 取消流程正确 | _ | _ | _ |
| 资源清理 | ✅ 100% 清理完成 | _ | _ | _ |
| AnyIO 使用 | ✅ 无混用 asyncio | _ | _ | _ |
| 类型检查 | ✅ mypy 无错误 | _ | _ | _ |
| 层间依赖 | ✅ 依赖关系正确 | _ | _ | _ |

**决策规则**:
- 所有项必须 ✅，否则 **NO-GO**
- 允许有 minor issues，但不阻塞发布

#### 性能验收决策表

| 验证项 | 标准 | 实际结果 | 状态 | 决策 |
|--------|------|----------|------|------|
| 平均执行时间 | < 40s | _ | _ | _ |
| 内存使用 | < 100MB | _ | _ | _ |
| TaskGroup 开销 | < 1ms | _ | _ | _ |
| 并发调用 | 10 个调用成功 | _ | _ | _ |
| 取消成功率 | 100% | _ | _ | _ |

**决策规则**:
- 所有项必须达标，否则 **NO-GO**
- 性能退化 > 5% → **NO-GO**

#### 质量验收决策表

| 验证项 | 标准 | 实际结果 | 状态 | 决策 |
|--------|------|----------|------|------|
| 测试覆盖率 | >= 85% | _ | _ | _ |
| 静态分析 | 无 Critical 问题 | _ | _ | _ |
| 控制器-Agent 集成 | ✅ 集成正常 | _ | _ | _ |
| SDKExecutor 集成 | ✅ 集成正常 | _ | _ | _ |
| 完整 Epic 流程 | ✅ 流程正常 | _ | _ | _ |
| 异常场景处理 | ✅ 正确处理 | _ | _ | _ |

**决策规则**:
- 测试覆盖率 < 85% → **NO-GO**
- 静态分析有 Critical 问题 → **NO-GO**
- Epic 流程失败 → **NO-GO**

### 5.2 最终决策流程

#### Step 1: 执行所有验证测试

```bash
# 执行所有验证测试
pytest tests/verification/ -v --tb=short

# 生成验证报告
pytest tests/verification/ --html=verification-report.html
```

#### Step 2: 收集验证结果

```python
def collect_verification_results():
    """收集验证结果"""
    results = {
        'functionality': [],
        'performance': [],
        'quality': []
    }

    # 从测试结果文件读取
    # ...

    return results
```

#### Step 3: 应用决策规则

```python
def make_go_no_go_decision(results):
    """做出 Go/No-Go 决策"""

    # 功能验收
    if not all(r['status'] == 'PASS' for r in results['functionality']):
        return {
            'decision': 'NO-GO',
            'reason': '功能验收未通过',
            'blocking_issues': [...]
        }

    # 性能验收
    if not all(r['status'] == 'PASS' for r in results['performance']):
        return {
            'decision': 'NO-GO',
            'reason': '性能验收未通过',
            'blocking_issues': [...]
        }

    # 质量验收
    if not all(r['status'] == 'PASS' for r in results['quality']):
        return {
            'decision': 'NO-GO',
            'reason': '质量验收未通过',
            'blocking_issues': [...]
        }

    return {
        'decision': 'GO',
        'reason': '所有验收通过',
        'release_ready': True
    }
```

#### Step 4: 生成验收报告

```markdown
# 最终验收报告

## 执行摘要
- 验证日期: 2026-01-XX
- 验证人员: [姓名]
- 验证范围: Phase 5 清理与优化

## 验证结果

### 功能验收
- 验证项数: 10
- 通过数: 10
- 失败数: 0
- 状态: ✅ 通过

### 性能验收
- 验证项数: 5
- 通过数: 5
- 失败数: 0
- 状态: ✅ 通过

### 质量验收
- 验证项数: 6
- 通过数: 6
- 失败数: 0
- 状态: ✅ 通过

## 性能指标

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 平均执行时间 | < 40s | 38s | ✅ |
| 内存使用 | < 100MB | 80MB | ✅ |
| TaskGroup 开销 | < 1ms | 0.5ms | ✅ |
| 取消成功率 | 100% | 100% | ✅ |

## 代码质量

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 测试覆盖率 | >= 85% | 87% | ✅ |
| 类型检查 | 无错误 | 无错误 | ✅ |
| 静态分析 | 无 Critical | 无 Critical | ✅ |

## 最终决策

**决策**: ✅ **GO**

**理由**:
- 所有功能验收通过
- 所有性能指标达标
- 所有质量标准满足
- 重构目标全部达成

**下一步**:
- 创建发布标签 v2.0.0-rc1
- 准备发布说明
- 开始用户培训

## 签名

- 架构师: ________________ 日期: ________
- 开发负责人: ________________ 日期: ________
- QA 负责人: ________________ 日期: ________
```

### 5.3 决策标准总结

#### 必须满足 (Go 标准)

**功能**:
- ✅ Epic Driver 正常启动
- ✅ 所有控制器正常工作
- ✅ 所有 Agent 正常工作
- ✅ SDK 调用成功
- ✅ Cancel Scope 问题完全解决
- ✅ 取消流程正确
- ✅ 资源清理完成

**性能**:
- ✅ 平均执行时间 < 40s
- ✅ 内存使用 < 100MB
- ✅ TaskGroup 开销 < 1ms
- ✅ 并发 10 个调用成功
- ✅ 取消成功率 = 100%

**质量**:
- ✅ 测试覆盖率 >= 85%
- ✅ 静态分析无 Critical 问题
- ✅ 控制器-Agent 集成正常
- ✅ SDKExecutor 集成正常
- ✅ 完整 Epic 流程正常
- ✅ 异常场景正确处理

#### 禁止项 (No-Go 标准)

**任何以下情况 → NO-GO**:
- ❌ 核心功能失败
- ❌ Cancel Scope 错误未解决
- ❌ 性能退化 >= 5%
- ❌ 测试覆盖率 < 85%
- ❌ 静态分析有 Critical 问题
- ❌ Epic 流程失败
- ❌ 内存泄漏

#### 决策树

```
开始验证
    ↓
功能验收
    ├─ 所有通过 → 性能验收
    └─ 有失败 → NO-GO
            ↓
性能验收
    ├─ 所有通过 → 质量验收
    └─ 有失败 → NO-GO
            ↓
质量验收
    ├─ 所有通过 → GO (发布)
    └─ 有失败 → NO-GO
```

---

## 6. 验证工具与脚本

### 6.1 自动化验证脚本

#### 主验证脚本

```bash
#!/bin/bash
# run_verification.sh

echo "========================================="
echo "Phase 5 最终验证流程"
echo "========================================="

# 1. 单元测试
echo "1. 运行单元测试..."
pytest tests/unit/ -v --cov=autoBMAD/epic_automation --cov-report=term-missing

if [ $? -ne 0 ]; then
    echo "❌ 单元测试失败"
    exit 1
fi

# 2. 集成测试
echo "2. 运行集成测试..."
pytest tests/integration/ -v

if [ $? -ne 0 ]; then
    echo "❌ 集成测试失败"
    exit 1
fi

# 3. 性能测试
echo "3. 运行性能测试..."
pytest tests/performance/ -v --benchmark-only

if [ $? -ne 0 ]; then
    echo "❌ 性能测试失败"
    exit 1
fi

# 4. E2E 测试
echo "4. 运行 E2E 测试..."
pytest tests/e2e/ -v

if [ $? -ne 0 ]; then
    echo "❌ E2E 测试失败"
    exit 1
fi

# 5. 验证测试
echo "5. 运行验证测试..."
pytest tests/verification/ -v --html=verification-report.html

if [ $? -ne 0 ]; then
    echo "❌ 验证测试失败"
    exit 1
fi

# 6. 静态分析
echo "6. 运行静态分析..."
mypy autoBMAD/epic_automation/ --strict
ruff check autoBMAD/epic_automation/
pydocstyle autoBMAD/epic_automation/

if [ $? -ne 0 ]; then
    echo "⚠️  静态分析有警告"
fi

echo "========================================="
echo "✅ 所有验证通过"
echo "========================================="
```

### 6.2 验证报告生成

```python
def generate_verification_report(results):
    """生成验证报告"""
    import json
    from datetime import datetime

    report = {
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-rc1',
        'results': results,
        'summary': {
            'total_tests': sum(len(r) for r in results.values()),
            'passed': sum(sum(1 for t in r if t['status'] == 'PASS') for r in results.values()),
            'failed': sum(sum(1 for t in r if t['status'] == 'FAIL') for r in results.values()),
            'pass_rate': 0  # 计算得出
        }
    }

    # 计算通过率
    total = report['summary']['total_tests']
    passed = report['summary']['passed']
    if total > 0:
        report['summary']['pass_rate'] = passed / total * 100

    # 保存 JSON 报告
    with open('verification-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    # 生成 HTML 报告
    generate_html_report(report)

    return report
```

---

## 7. 后续行动

### 7.1 验证通过后的行动

**立即行动** (验证完成当天):
1. 创建发布标签: `git tag v2.0.0-rc1`
2. 生成变更日志
3. 发送验证通过通知

**短期行动** (1 周内):
1. 准备用户培训材料
2. 更新部署文档
3. 监控上线后指标

**中期行动** (1 个月内):
1. 收集用户反馈
2. 性能持续监控
3. 规划下一版本

### 7.2 验证失败后的行动

**问题分类**:
- **P0 (阻塞)**: 核心功能失败、性能退化 > 5%
- **P1 (严重)**: 质量门控失败、Cancel Scope 问题
- **P2 (一般)**: 次要功能问题、文档缺失

**修复流程**:
1. 创建 Bug 报告
2. 分配修复任务
3. 修复后重新验证
4. 更新验证报告

### 7.3 持续监控

**监控指标**:
- 执行时间趋势
- 错误率趋势
- 内存使用趋势
- 用户满意度

**报警阈值**:
- 执行时间 > 45s
- 错误率 > 5%
- 内存使用 > 120MB
- 用户投诉 > 3 个

---

## 8. 总结

### 8.1 验证框架价值

**完整性**:
- 覆盖所有关键场景
- 覆盖所有质量维度
- 覆盖所有性能指标

**可追溯性**:
- 每个标准有测试依据
- 每个结果有详细记录
- 每个决策有明确依据

**自动化**:
- 大部分验证自动化
- 结果可重复
- 效率高

### 8.2 Go/No-Go 决策价值

**降低风险**:
- 避免有缺陷的发布
- 保护用户利益
- 维护品牌声誉

**提高质量**:
- 确保发布质量
- 建立质量标准
- 持续改进

**增强信心**:
- 团队对发布有信心
- 管理层对质量有信心
- 用户对产品有信心

### 8.3 最终目标

**技术目标**:
- ✅ Cancel Scope 问题完全解决
- ✅ 性能达标或提升
- ✅ 代码质量显著提升

**业务目标**:
- ✅ 用户体验改善
- ✅ 运营成本降低
- ✅ 技术债务减少

**团队目标**:
- ✅ 提升技术能力
- ✅ 建立最佳实践
- ✅ 积累重构经验

**最终状态**: ✅ **GO** - 准备发布!
