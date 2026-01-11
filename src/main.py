#!/usr/bin/env python3
"""
PyQt Windows应用程序入口点

这是一个使用PySide6构建的现代Qt应用程序模板。
应用程序集成了BMAD开发方法论和AI辅助开发工具。

运行方式:
    python src/main.py
    或者
    python -m my_qt_app

作者: Claude Code
版本: 2.0.0
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from my_qt_app import MainWindow
from PySide6.QtWidgets import QApplication


def main():
    """主函数 - 应用程序入口点"""
    # 创建QApplication实例
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("PyQt Windows应用程序模板")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Claude Code")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 启动事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
