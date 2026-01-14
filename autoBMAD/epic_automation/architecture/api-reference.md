# API 参考文档

## SDK 执行层 API

### SDKExecutor

```python
class SDKExecutor:
    """SDK 执行器 - 在独立 TaskGroup 中执行 SDK 调用"""

    def __init__(self) -> None:
        """初始化 SDK 执行器"""
        self.cancel_manager = CancellationManager()

    async def execute(
        self,
        sdk_func: Callable[[], AsyncIterator[Any]],
        target_predicate: Callable[[Any], bool],
        *,
        timeout: float | None = None,
        agent_name: str = "Unknown"
    ) -> SDKResult:
        """
        在独立 TaskGroup 中执行 SDK 调用

        Args:
            sdk_func: SDK 调用函数（返回异步迭代器）
            target_predicate: 目标检测函数
            timeout: 超时时间（秒）
            agent_name: Agent 名称

        Returns:
            SDKResult: 执行结果
        """
```

### SDKResult

```python
@dataclass
class SDKResult:
    """SDK 执行结果"""

    # 业务成功标志
    has_target_result: bool = False
    cleanup_completed: bool = False

    # 执行信息
    duration_seconds: float = 0.0
    session_id: str = ""
    agent_name: str = ""

    # 结果数据
    messages: list[Any] = field(default_factory=list)
    target_message: Any = None

    # 错误信息
    error_type: SDKErrorType = SDKErrorType.SUCCESS
    errors: list[str] = field(default_factory=list)

    def is_success(self) -> bool:
        """判断业务是否成功"""
        return self.has_target_result and self.cleanup_completed
```

### CancellationManager

```python
class CancellationManager:
    """取消管理器 - 双条件验证机制"""

    def __init__(self) -> None:
        """初始化取消管理器"""
        self._active_calls: Dict[str, CallInfo] = {}

    async def confirm_safe_to_proceed(
        self,
        call_id: str,
        timeout: float = 5.0
    ) -> bool:
        """
        确认可以安全进行下一步（双条件验证）

        条件：
        1. cancel_requested = True
        2. cleanup_completed = True

        Args:
            call_id: 调用 ID
            timeout: 等待超时（秒）

        Returns:
            bool: 是否可以安全进行
        """
```

## 控制器层 API

### BaseController

```python
class BaseController(ABC):
    """控制器基类"""

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """执行控制器逻辑"""
        pass
```

### SMController

```python
class SMController(BaseController):
    """故事管理控制器"""

    async def process_story(self, story: Any) -> Any:
        """处理故事"""

    async def update_state(self, story_id: str, state: str) -> bool:
        """更新状态"""

    async def get_state(self, story_id: str) -> Optional[str]:
        """获取状态"""
```

## Agent 层 API

### BaseAgent

```python
class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, task_group: Optional[anyio.abc.TaskGroup] = None):
        """初始化 Agent"""

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """执行 Agent 逻辑"""
        pass
```

### SMAgent

```python
class SMAgent(BaseAgent):
    """故事管理 Agent"""

    async def execute(self, context: Dict[str, Any]) -> Any:
        """执行故事管理任务"""

    async def parse_story(self, story_path: str) -> Optional[str]:
        """解析故事状态"""

    async def update_status(self, story_path: str, status: str) -> bool:
        """更新状态"""
```

### StateAgent

```python
class StateAgent(BaseAgent):
    """状态解析 Agent"""

    async def parse_status(self, story_path: str) -> Optional[str]:
        """解析故事状态"""

    async def get_processing_status(self, story_path: str) -> Optional[str]:
        """获取处理状态"""

    async def update_story_status(self, story_path: str, status: str) -> bool:
        """更新故事状态"""
```
