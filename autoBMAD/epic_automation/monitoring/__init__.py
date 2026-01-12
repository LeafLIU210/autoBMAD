"""监测模块

该模块提供监控和管理功能，包括：
- 取消管理器（全局单例）
- 资源监控

重要：get_cancellation_manager() 返回全局单例实例，确保所有Agent共享同一个管理器
"""

from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager

# 全局单例
_global_cancellation_manager: CancellationManager | None = None


def get_cancellation_manager() -> CancellationManager:
    """
    获取全局取消管理器单例

    Returns:
        CancellationManager: 全局取消管理器实例
    """
    global _global_cancellation_manager

    if _global_cancellation_manager is None:
        _global_cancellation_manager = CancellationManager()

    return _global_cancellation_manager


def reset_cancellation_manager() -> None:
    """
    重置全局取消管理器（仅用于测试）

    Warning:
        此函数会清空所有活跃调用记录，仅在测试中使用
    """
    global _global_cancellation_manager
    _global_cancellation_manager = None