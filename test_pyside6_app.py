#!/usr/bin/env python3
"""
PySide6应用程序测试脚本

此脚本用于验证PyQt应用程序是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """测试模块导入"""
    print("[TEST] Testing module imports...")

    try:
        from PySide6.QtWidgets import QApplication
        print("  [OK] PySide6.QtWidgets imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Failed to import PySide6.QtWidgets: {e}")
        return False

    try:
        from my_qt_app import MainWindow
        print("  [OK] MainWindow imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Failed to import MainWindow: {e}")
        return False

    return True


def test_application():
    """测试应用程序核心功能"""
    print("\n[TEST] Testing application core functionality...")

    try:
        from PySide6.QtWidgets import QApplication
        from my_qt_app import MainWindow

        # 创建QApplication实例（不启动事件循环）
        app = QApplication([])
        print("  [OK] QApplication created successfully")

        # 创建主窗口（不显示）
        window = MainWindow()
        print("  [OK] MainWindow created successfully")

        # 验证窗口属性
        title = window.windowTitle()
        print(f"  [OK] Window title: {title}")

        # 验证窗口大小
        size = window.size()
        print(f"  [OK] Window size: {size.width()}x{size.height()}")

        # 验证中央部件
        central_widget = window.centralWidget()
        if central_widget:
            print("  [OK] Central widget exists")
        else:
            print("  [WARNING] Central widget not found")

        return True

    except Exception as e:
        print(f"  [ERROR] Application test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("PySide6应用程序测试")
    print("=" * 60)

    # 测试导入
    if not test_imports():
        print("\n[FAILED] Import test failed")
        return 1

    # 测试应用程序
    if not test_application():
        print("\n[FAILED] Application test failed")
        return 1

    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
