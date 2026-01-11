#!/usr/bin/env python3
"""
PyQt应用程序快速启动脚本

使用方法:
    python run_app.py
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    """启动PyQt应用程序"""
    try:
        from PySide6.QtWidgets import QApplication
        from my_qt_app import MainWindow

        print("正在启动PyQt应用程序...")
        print("-" * 50)

        # 创建QApplication
        app = QApplication(sys.argv)

        # 创建主窗口
        window = MainWindow()
        window.show()

        print("应用程序已启动!")
        print("提示: 点击'测试'按钮验证功能")
        print("-" * 50)

        # 启动事件循环
        sys.exit(app.exec())

    except ImportError as e:
        print(f"错误: 导入模块失败: {e}")
        print("\n请确保已安装依赖:")
        print("  pip install -r requirements.txt")
        return 1

    except Exception as e:
        print(f"错误: 启动应用程序失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
