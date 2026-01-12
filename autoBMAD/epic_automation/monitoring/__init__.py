"""监测模块

该模块提供监控和管理功能，包括：
- 取消管理器
- 资源监控
"""

from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager


def get_cancellation_manager():
    """获取取消管理器实例

    Returns:
        CancellationManager: 取消管理器实例
    """
    return CancellationManager()