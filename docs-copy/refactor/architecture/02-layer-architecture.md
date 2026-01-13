# BMAD Epic Automation 五层架构详解

**文档版本**: 1.0  
**创建日期**: 2026-01-11  
**状态**: Draft

---

## 1. 架构层次概览

### 1.1 五层模型

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: TaskGroup 层                                    │
│ - 职责: AnyIO 结构化并发容器，生命周期隔离               │
│ - 组件: SM TaskGroup, Story TaskGroup, SDK TaskGroup     │
└─────────────────────────────────────────────────────────┘
                          ↓ 管理
┌─────────────────────────────────────────────────────────┐
│ Layer 2: 控制器层 (Controller)                           │
│ - 职责: 业务流程决策，状态驱动                           │
│ - 组件: SMController, DevQaController, QualityController │
└─────────────────────────────────────────────────────────┘
                          ↓ 调用
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Agent 层                                        │
│ - 职责: 业务逻辑实现，Prompt 构造，结果解释              │
│ - 组件: SMAgent, StateAgent, DevAgent, QAAgent          │
└─────────────────────────────────────────────────────────┘
                          ↓ 委托
┌─────────────────────────────────────────────────────────┐
│ Layer 4: SDK 执行层                                      │
│ - 职责: SDK 调用管理，取消控制，清理保证                 │
│ - 组件: SDKExecutor, CancellationManager, SafeClaudeSDK  │
└─────────────────────────────────────────────────────────┘
                          ↓ 使用
┌─────────────────────────────────────────────────────────┐
│ Layer 5: Claude SDK 层                                   │
│ - 职责: 第三方 AI 服务，流式响应                         │
│ - 组件: Claude Agent SDK (第三方)                        │
└─────────────────────────────────────────────────────────┘
```

### 1.2 层间依赖关系

```
Layer 1 (TaskGroup)
  ↓ 包含
Layer 2 (Controller) → 状态驱动 → StateManager, Story Files
  ↓ 控制
Layer 3 (Agent) → 读写 → Story Files, Code Files
  ↓ 委托
Layer 4 (SDK Executor) → 管理 → Task, CancelScope, Resources
  ↓ 调用
Layer 5 (Claude SDK) → 网络请求 → Claude API
```

**依赖原则**：
- 上层可以依赖下层
- 下层不能依赖上层
- 同层之间不能直接依赖

---

## 2. Layer 1: TaskGroup 层

### 2.1 职责定义

**核心职责**：
1. 提供结构化并发容器
2. 管理 Cancel Scope 生命周期
3. 确保资源自动清理
4. 隔离不同业务单元

### 2.2 TaskGroup 类型

#### 2.2.1 SM TaskGroup

**生命周期**: Story 初始化阶段

**包含内容**：
```
SM TaskGroup
  ├─ SMController 执行上下文
  ├─ SMAgent 业务逻辑
  └─ SDK 调用 TaskGroup (嵌套)
```

**示例代码**：
```python
async def process_story_sm_phase(story_path: str):
    """在独立 TaskGroup 中执行 SM 阶段"""
    async with anyio.create_task_group() as sm_tg:
        sm_controller = SMController(sm_tg)
        result = await sm_controller.execute(story_path)
        return result
    # 退出时保证所有子任务完成清理
```

#### 2.2.2 Story TaskGroup (Dev-QA)

**生命周期**: Story 的完整 Dev-QA 流程

**包含内容**：
```
Story TaskGroup
  ├─ DevQaController 执行上下文
  ├─ StateAgent + DevAgent + QAAgent 业务逻辑
  └─ 多个 SDK 调用 TaskGroup (嵌套)
```

**示例代码**：
```python
async def process_story_devqa_phase(story_path: str):
    """在独立 TaskGroup 中执行 Dev-QA 阶段"""
    async with anyio.create_task_group() as story_tg:
        devqa_controller = DevQaController(story_tg)
        result = await devqa_controller.run_pipeline(story_path)
        return result
    # 退出时保证所有 Agent 的 SDK 调用都已清理
```

#### 2.2.3 SDK TaskGroup

**生命周期**: 单次 SDK 调用

**包含内容**：
```
SDK TaskGroup
  ├─ Claude SDK 流式调用
  ├─ 消息收集任务
  └─ 取消管理任务
```

**示例代码**：
```python
async def execute_sdk_call(sdk_func: Callable):
    """在独立 TaskGroup 中执行 SDK 调用"""
    async with anyio.create_task_group() as sdk_tg:
        result = await sdk_tg.start(sdk_func)
        return result
    # 退出时保证 Claude SDK 内部任务已清理
```

#### 2.2.4 Quality TaskGroup

**生命周期**: 质量门控阶段

**包含内容**：
```
Quality TaskGroup
  ├─ Ruff TaskGroup
  │   └─ RuffController + RuffAgent
  ├─ BasedPyright TaskGroup
  │   └─ PyrightController + PyrightAgent
  └─ Pytest TaskGroup
      └─ PytestController + PytestAgent
```

### 2.3 TaskGroup 嵌套规则

**规则 1: 最多三层嵌套**
```
Level 1: Story TaskGroup (Story 隔离)
  ↓
Level 2: Agent TaskGroup (Agent 隔离，可选)
  ↓
Level 3: SDK TaskGroup (SDK 调用隔离)
```

**规则 2: 同级 TaskGroup 顺序执行**
```python
# 顺序执行多个 Story
for story in stories:
    async with create_task_group() as story_tg:
        await process_story(story_tg, story)
    # 下一个 Story 开始前，前一个 Story 完全清理
```

**规则 3: 父 TaskGroup 等待所有子 TaskGroup**
```python
async with create_task_group() as parent_tg:
    await parent_tg.start(child_task_1)
    await parent_tg.start(child_task_2)
# 退出时保证 child_task_1 和 child_task_2 都完成
```

### 2.4 Cancel Scope 管理

**RAII 保证**：
```python
async with create_task_group() as tg:
    # 进入：
    # 1. 创建 cancel scope
    # 2. push 到当前 Task 的 scope 栈
    
    await tg.start(some_task)
    
    # 退出：
    # 1. 取消所有子任务
    # 2. 等待子任务完成 (包括清理)
    # 3. pop cancel scope
    # 4. 如果有异常，在此处理
# 保证：enter 和 exit 在同一 Task 中
```

---

## 3. Layer 2: 控制器层

### 3.1 职责定义

**核心职责**：
1. 业务流程决策（基于核心状态值）
2. 调用 Agent 执行具体任务
3. 管理业务流程状态机
4. 不直接调用 SDK

**禁止事项**：
- ❌ 不能直接调用 SDK
- ❌ 不能处理 SDK 底层异常
- ❌ 不能管理 Cancel Scope
- ❌ 不能读写文件（通过 Agent）

### 3.2 控制器类型

#### 3.2.1 SMController

**职责**：控制 SM 阶段流程

**状态机**：
```
初始化 → 读取 Epic → 调用 SMAgent → 生成 Story → 完成
```

**接口**：
```python
class SMController:
    def __init__(self, task_group: anyio.abc.TaskGroup):
        self.task_group = task_group
        self.sm_agent = SMAgent()
    
    async def execute(self, epic_content: str, story_id: str) -> bool:
        """执行 SM 阶段"""
        # 1. 构造 SM 任务参数
        # 2. 调用 SMAgent
        # 3. 验证生成结果
        # 4. 返回成功/失败
```

#### 3.2.2 DevQaController

**职责**：控制 Dev-QA 状态机流水线

**状态机（扩展版）**：
```
Step 1:  StateAgent 解析状态 S0
Step 2:  决策 → Dev Agent (如需要)
Step 3:  StateAgent 解析状态 S1
Step 4:  决策 → QA Agent (如需要)
Step 5:  StateAgent 解析状态 S2
Step 6:  决策 → Dev Agent (如需要)
Step 7:  StateAgent 解析状态 S3
Step 8:  决策 → QA Agent (如需要)
Step 9:  StateAgent 解析状态 S4
...
最多重复 3 轮 Dev-QA
```

**接口**：
```python
class DevQaController:
    def __init__(self, task_group: anyio.abc.TaskGroup):
        self.task_group = task_group
        self.state_agent = StateAgent()
        self.dev_agent = DevAgent()
        self.qa_agent = QAAgent()
    
    async def run_pipeline(self, story_path: str) -> bool:
        """运行 Dev-QA 流水线"""
        max_rounds = 3
        
        for round_num in range(1, max_rounds + 1):
            # Step 1: 状态解析
            status = await self.state_agent.parse_status(story_path)
            
            # 终止条件
            if status in ["Done", "Ready for Done"]:
                return True
            
            # Step 2: Dev (如需要)
            if status in ["Draft", "Ready for Development", "Failed"]:
                await self.dev_agent.execute(story_path)
            
            # Step 3: 状态解析
            status = await self.state_agent.parse_status(story_path)
            
            # Step 4: QA (如需要)
            if status == "Ready for Review":
                await self.qa_agent.execute(story_path)
            
            # Step 5: 状态解析
            status = await self.state_agent.parse_status(story_path)
        
        return False  # 超过最大轮次
```

#### 3.2.3 QualityController

**职责**：控制质量门控流程

**状态机**：
```
初始化 → Ruff → BasedPyright → Pytest → 生成报告 → 完成
```

**接口**：
```python
class QualityController:
    def __init__(self, task_group: anyio.abc.TaskGroup):
        self.task_group = task_group
        self.ruff_agent = RuffAgent()
        self.pyright_agent = BasedPyrightAgent()
        self.pytest_agent = PytestAgent()
    
    async def execute(self) -> dict:
        """执行质量门控"""
        results = {}
        
        # Ruff
        results['ruff'] = await self.ruff_agent.execute()
        
        # BasedPyright
        results['pyright'] = await self.pyright_agent.execute()
        
        # Pytest
        results['pytest'] = await self.pytest_agent.execute()
        
        return results
```

### 3.3 控制器决策规则

**规则 1: 基于核心状态值决策**
```python
# ✅ 正确：基于状态值
if status == "Ready for Development":
    await self.dev_agent.execute(story_path)

# ❌ 错误：基于 Agent 返回值
if dev_result.success:
    await self.qa_agent.execute(story_path)
```

**规则 2: 不处理 SDK 异常**
```python
# ✅ 正确：只处理业务异常
try:
    result = await agent.execute()
except BusinessLogicError as e:
    logger.error(f"Business error: {e}")

# ❌ 错误：处理 SDK 异常
try:
    result = await agent.execute()
except asyncio.CancelledError:
    # Controller 不应处理这种异常
```

**规则 3: 状态是唯一真相源**
```python
# ✅ 正确：每次决策前重新读取状态
for iteration in range(max_iterations):
    status = await self.state_agent.parse_status(story_path)
    
    if status == "Done":
        break
    
    # 基于最新状态决策
    if status == "Ready for Development":
        await self.dev_agent.execute(story_path)
```

---

## 4. Layer 3: Agent 层

### 4.1 职责定义

**核心职责**：
1. 构造 SDK Prompt
2. 定义目标 ResultMessage（成功条件）
3. 解释 SDK 返回结果
4. 更新 Story 状态
5. 读写文件（代码、文档）

**禁止事项**：
- ❌ 不能做流程决策（由 Controller 负责）
- ❌ 不能管理 TaskGroup
- ❌ 不能处理 CancelledError（由 SDK 执行层负责）

### 4.2 Agent 类型

#### 4.2.1 SMAgent

**职责**：生成 Story 模板

**输入**：Epic 内容、Story ID

**输出**：Story Markdown 文件

**接口**：
```python
class SMAgent:
    def __init__(self, sdk_executor: SDKExecutor):
        self.sdk_executor = sdk_executor
    
    async def execute(self, epic_content: str, story_id: str) -> bool:
        """执行 SM 任务"""
        # 1. 构造 SM Prompt
        prompt = self._build_sm_prompt(epic_content, story_id)
        
        # 2. 定义目标条件
        def target_predicate(msg: ResultMessage) -> bool:
            return "Story Template Generated" in msg.text
        
        # 3. 调用 SDK 执行层
        result = await self.sdk_executor.execute(
            sdk_func=lambda: self._call_claude(prompt),
            target_predicate=target_predicate,
            agent_name="SMAgent"
        )
        
        # 4. 解释结果并写文件
        if result.has_target_result:
            story_content = self._extract_story_content(result.messages)
            self._write_story_file(story_id, story_content)
            return True
        
        return False
```

#### 4.2.2 StateAgent

**职责**：解析 Story 状态

**输入**：Story 文件路径

**输出**：核心状态值（7 个标准状态之一）

**接口**：
```python
class StateAgent:
    def __init__(self, sdk_executor: SDKExecutor):
        self.sdk_executor = sdk_executor
    
    async def parse_status(self, story_path: str) -> str:
        """解析 Story 状态"""
        # 1. 读取 Story 内容
        content = self._read_story_file(story_path)
        
        # 2. 构造状态解析 Prompt
        prompt = self._build_status_prompt(content)
        
        # 3. 定义目标条件
        def target_predicate(msg: ResultMessage) -> bool:
            return self._is_valid_status(msg.text)
        
        # 4. 调用 SDK 执行层
        result = await self.sdk_executor.execute(
            sdk_func=lambda: self._call_claude(prompt),
            target_predicate=target_predicate,
            agent_name="StateAgent"
        )
        
        # 5. 提取状态值
        if result.has_target_result:
            status = self._extract_status(result.messages)
            return status
        
        # Fallback: 使用正则解析
        return self._fallback_parse_status(content)
```

#### 4.2.3 DevAgent

**职责**：实现 Story 需求

**输入**：Story 文件路径

**输出**：代码文件、更新状态

**接口**：
```python
class DevAgent:
    def __init__(self, sdk_executor: SDKExecutor):
        self.sdk_executor = sdk_executor
    
    async def execute(self, story_path: str) -> bool:
        """执行开发任务"""
        # 1. 读取需求
        requirements = self._read_requirements(story_path)
        
        # 2. 构造开发 Prompt
        prompt = self._build_dev_prompt(requirements)
        
        # 3. 定义目标条件
        def target_predicate(msg: ResultMessage) -> bool:
            return "Implementation Complete" in msg.text
        
        # 4. 调用 SDK 执行层
        result = await self.sdk_executor.execute(
            sdk_func=lambda: self._call_claude(prompt),
            target_predicate=target_predicate,
            agent_name="DevAgent",
            timeout=1800.0  # 30 分钟
        )
        
        # 5. 解释结果并更新
        if result.has_target_result:
            # 代码已由 Claude SDK 写入文件
            self._update_story_status(story_path, "Ready for Review")
            return True
        
        return False
```

#### 4.2.4 QAAgent

**职责**：审查代码质量

**输入**：Story 文件路径

**输出**：审查报告、更新状态

**接口**：
```python
class QAAgent:
    def __init__(self, sdk_executor: SDKExecutor):
        self.sdk_executor = sdk_executor
    
    async def execute(self, story_path: str) -> bool:
        """执行 QA 任务"""
        # 1. 读取需求和代码
        requirements = self._read_requirements(story_path)
        code_files = self._find_code_files(story_path)
        
        # 2. 构造 QA Prompt
        prompt = self._build_qa_prompt(requirements, code_files)
        
        # 3. 定义目标条件
        def target_predicate(msg: ResultMessage) -> bool:
            return "QA Review Complete" in msg.text
        
        # 4. 调用 SDK 执行层
        result = await self.sdk_executor.execute(
            sdk_func=lambda: self._call_claude(prompt),
            target_predicate=target_predicate,
            agent_name="QAAgent",
            timeout=900.0  # 15 分钟
        )
        
        # 5. 解释结果并更新
        if result.has_target_result:
            passed = self._extract_qa_result(result.messages)
            if passed:
                self._update_story_status(story_path, "Ready for Done")
            else:
                self._update_story_status(story_path, "Ready for Development")
            return True
        
        return False
```

### 4.3 Agent 设计原则

**原则 1: Agent 只判断业务成功**
```python
# ✅ 正确：只看是否拿到目标 ResultMessage
if result.has_target_result and result.cleanup_completed:
    return True  # 业务成功

# ❌ 错误：检查 SDK 错误
if not result.errors:
    return True  # 不应基于错误判断
```

**原则 2: Agent 不处理取消**
```python
# ✅ 正确：让 SDK 执行层处理
result = await self.sdk_executor.execute(...)

# ❌ 错误：Agent 捕获 CancelledError
try:
    result = await self.sdk_executor.execute(...)
except asyncio.CancelledError:
    # Agent 不应处理此异常
```

**原则 3: Agent 通过状态间接协作**
```python
# ✅ 正确：DevAgent 更新状态
self._update_story_status(story_path, "Ready for Review")

# QAAgent 通过状态知道该做什么
status = self._read_story_status(story_path)
if status == "Ready for Review":
    # 执行审查

# ❌ 错误：DevAgent 直接调用 QAAgent
await self.qa_agent.execute(story_path)
```

---

## 5. Layer 4: SDK 执行层

### 5.1 职责定义

**核心职责**：
1. 在独立 TaskGroup 中执行 SDK 调用
2. 管理流式消息收集
3. 检测目标 ResultMessage
4. 请求取消并等待清理完成
5. 封装所有 SDK 异常

**禁止事项**：
- ❌ 不能做业务决策
- ❌ 不能直接读写业务文件
- ❌ 不能向上抛出 CancelledError

### 5.2 核心组件

#### 5.2.1 SDKExecutor

详见 [06-sdk-execution-layer.md](06-sdk-execution-layer.md)

#### 5.2.2 CancellationManager

详见 [06-sdk-execution-layer.md](06-sdk-execution-layer.md)

#### 5.2.3 SafeClaudeSDK

详见 [06-sdk-execution-layer.md](06-sdk-execution-layer.md)

---

## 6. Layer 5: Claude SDK 层

### 6.1 职责定义

**核心职责**：
1. 与 Claude API 通信
2. 提供流式响应
3. 管理内部 TaskGroup

**特点**：
- 第三方 SDK，不可修改
- 内部使用 AnyIO TaskGroup
- 重构后与我们的架构统一

---

## 7. 层间交互示例

### 7.1 完整调用链

```python
# EpicDriver (主入口)
async def main():
    stories = parse_epic("my-epic.md")
    
    for story in stories:
        # Layer 1: 创建 Story TaskGroup
        async with anyio.create_task_group() as story_tg:
            # Layer 2: 创建 Controller
            controller = DevQaController(story_tg)
            
            # Controller 驱动流水线
            success = await controller.run_pipeline(story.path)
```

```python
# DevQaController (Layer 2)
async def run_pipeline(self, story_path: str) -> bool:
    # 调用 Layer 3: StateAgent
    status = await self.state_agent.parse_status(story_path)
    
    if status == "Ready for Development":
        # 调用 Layer 3: DevAgent
        await self.dev_agent.execute(story_path)
```

```python
# DevAgent (Layer 3)
async def execute(self, story_path: str) -> bool:
    prompt = self._build_prompt(story_path)
    
    # 调用 Layer 4: SDKExecutor
    result = await self.sdk_executor.execute(
        sdk_func=lambda: self._call_claude(prompt),
        target_predicate=self._is_complete,
        agent_name="DevAgent"
    )
    
    return result.has_target_result
```

```python
# SDKExecutor (Layer 4)
async def execute(self, sdk_func, target_predicate, agent_name) -> SDKResult:
    # 创建独立 TaskGroup
    async with anyio.create_task_group() as sdk_tg:
        # 调用 Layer 5: Claude SDK
        messages = []
        async for msg in sdk_func():
            messages.append(msg)
            
            # 检测目标
            if target_predicate(msg):
                # 请求取消
                self.cancel_manager.request_cancel(call_id)
                break
        
        # 等待清理完成
        await self.cancel_manager.confirm_safe_to_proceed(call_id)
        
        return SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            messages=messages
        )
```

---

## 8. 架构优势

### 8.1 技术优势

1. **隔离性**：每层职责清晰，故障不传播
2. **可测试性**：每层可独立测试
3. **可维护性**：修改一层不影响其他层
4. **可扩展性**：添加新 Agent 无需修改框架

### 8.2 业务优势

1. **可靠性**：TaskGroup 保证资源清理
2. **可观测性**：每层有独立日志
3. **可调试性**：问题定位精确到层
4. **可配置性**：每层可独立配置

---

**下一步**：阅读 [03-taskgroup-isolation.md](03-taskgroup-isolation.md) 了解 TaskGroup 隔离机制细节
