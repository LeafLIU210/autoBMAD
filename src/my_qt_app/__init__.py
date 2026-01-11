"""
My Qt App - PyQt应用程序包

这是一个使用PySide6构建的现代Qt应用程序模板。
集成了BMAD开发方法论和AI辅助开发工具。

主要组件:
- MainWindow: 主窗口界面
- 现代化的UI设计
- 响应式布局
"""

from .widgets.main_window import MainWindow

__version__ = "2.0.0"
__author__ = "Claude Code"
__description__ = "PyQt Windows应用程序开发模板"

__all__ = ["MainWindow"]
