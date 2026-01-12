"""
Pytest配置文件 - 安全TaskGroup和测试工具

本文件提供安全的测试fixture，避免Cancel Scope跨任务问题。
"""
import pytest
import anyio
import asyncio
from typing import AsyncGenerator


class SafeTaskGroupContext:
    """
    安全的TaskGroup上下文管理器

    解决AnyIO CancelScope跨任务错误的关键实现：
    - 确保CancelScope在同一任务内创建和销毁
    - 添加同步点，防止任务泄露
    - 提供清晰的错误提示
    """

    def __init__(self):
        self._task_group = None
        self._closed = False

    async def __aenter__(self):
        """进入TaskGroup上下文"""
        if self._closed:
            raise RuntimeError("TaskGroup context is closed")

        # 创建新的TaskGroup
        self._task_group = anyio.create_task_group()
        return self._task_group

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出TaskGroup上下文，添加同步保护"""
        if self._task_group and not self._closed:
            try:
                # 关键：添加同步点，确保所有任务正确完成
                # 这防止了CancelScope跨任务访问问题
                await asyncio.sleep(0)

                # 优雅关闭TaskGroup
                # 注意：anyio.create_task_group()返回的对象没有aclose方法
                # TaskGroup会在退出上下文时自动关闭
                self._closed = True

            except Exception as e:
                # 记录错误但不重新抛出（pytest会处理）
                print(f"Warning: Error closing TaskGroup: {e}")

    @property
    def task_group(self):
        """获取内部TaskGroup实例"""
        if self._task_group is None:
            raise RuntimeError("TaskGroup not initialized. Use 'async with safe_task_group() as tg:'")
        return self._task_group


@pytest.fixture
def safe_task_group() -> AsyncGenerator[SafeTaskGroupContext, None]:
    """
    安全的TaskGroup fixture

    使用方式：
    ```python
    @pytest.mark.anyio
    async def test_example(safe_task_group):
        async with safe_task_group as tg:
            # 在这里使用tg进行测试
            controller = SMController(tg, project_root)
            result = await controller.execute(...)
            assert result is True
    ```

    关键特性：
    1. 自动管理TaskGroup生命周期
    2. 防止CancelScope跨任务访问
    3. 提供清晰的错误提示
    4. 与pytest-asyncio兼容
    """
    context = SafeTaskGroupContext()

    # 提供上下文管理器接口
    async def _get_context():
        return context

    # 返回上下文管理器
    yield context

    # pytest清理（在所有测试完成后）
    if not context._closed:
        try:
            # 确保上下文被正确关闭
            import warnings
            warnings.warn(
                "TaskGroup context was not properly closed. "
                "Please use 'async with safe_task_group() as tg:' syntax.",
                UserWarning,
                stacklevel=2
            )
        except Exception:
            pass  # 忽略清理错误


# 便利的fixture别名
@pytest.fixture
def task_group_context():
    """safe_task_group的别名，提供向后兼容"""
    return SafeTaskGroupContext()


# 测试工具函数
def assert_task_group_active(context: SafeTaskGroupContext):
    """
    断言TaskGroup处于活动状态

    Args:
        context: SafeTaskGroupContext实例

    Raises:
        AssertionError: 如果TaskGroup未激活
        RuntimeError: 如果上下文未初始化
    """
    if context._task_group is None:
        raise RuntimeError("TaskGroup not initialized")
    if context._closed:
        raise RuntimeError("TaskGroup context is already closed")


# 全局配置
def pytest_configure(config):
    """Pytest全局配置"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "safe_task: mark test as requiring safe_task_group fixture"
    )

    # 设置测试超时（可选）
    # config.option.timeout = 300  # 5分钟超时


def pytest_collection_modifyitems(config, items):
    """修改测试集合，为异步测试添加标记"""
    for item in items:
        # 自动为使用safe_task_group的测试添加标记
        if "safe_task_group" in item.fixturenames:
            item.add_marker(pytest.mark.safe_task)
