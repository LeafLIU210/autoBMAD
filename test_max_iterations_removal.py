#!/usr/bin/env python3
"""
验证 max_iterations 移除的测试脚本
"""

import sys
import time
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入是否正常"""
    try:
        from autoBMAD.epic_automation.epic_driver import EpicDriver, StoryProgressTracker, STORY_TIME_BUDGET, CYCLE_TIME_BUDGET
        print("PASS: Import test successful")
        return True
    except ImportError as e:
        print(f"❌ 导入测试失败: {e}")
        return False

def test_progress_tracker():
    """测试进度跟踪器功能"""
    try:
        from autoBMAD.epic_automation.epic_driver import StoryProgressTracker
        import logging

        # 创建测试logger
        logger = logging.getLogger(__name__)

        # 创建进度跟踪器
        tracker = StoryProgressTracker("test_story.md", logger)

        # 测试记录循环开始
        tracker.record_cycle_start()
        print(f"✅ 循环计数: {tracker.cycle_count}")

        # 测试记录Dev阶段
        tracker.record_dev_phase(10.5, True)
        print(f"✅ Dev阶段时间: {tracker.dev_phase_times}")

        # 测试记录QA阶段
        tracker.record_qa_phase(5.2, True, "In Progress")
        print(f"✅ QA阶段时间: {tracker.qa_phase_times}")
        print(f"✅ 状态历史: {tracker.status_history}")

        # 测试获取摘要
        summary = tracker.get_summary()
        print(f"✅ 进度摘要: {summary}")

        print("✅ 进度跟踪器测试通过")
        return True
    except Exception as e:
        print(f"❌ 进度跟踪器测试失败: {e}")
        return False

def test_epic_driver_init():
    """测试 EpicDriver 初始化"""
    try:
        from autoBMAD.epic_automation.epic_driver import EpicDriver

        # 尝试创建 EpicDriver 实例（不传递 max_iterations）
        driver = EpicDriver(
            epic_path="test.md",
            retry_failed=False,
            verbose=True
        )

        # 检查 max_iterations 属性是否存在
        if hasattr(driver, 'max_iterations'):
            print("❌ max_iterations 属性仍然存在")
            return False
        else:
            print("✅ max_iterations 属性已移除")

        print("✅ EpicDriver 初始化测试通过")
        return True
    except Exception as e:
        print(f"❌ EpicDriver 初始化测试失败: {e}")
        return False

def test_constants():
    """测试时间预算常量"""
    try:
        from autoBMAD.epic_automation.epic_driver import STORY_TIME_BUDGET, CYCLE_TIME_BUDGET

        print(f"✅ STORY_TIME_BUDGET: {STORY_TIME_BUDGET} 秒 ({STORY_TIME_BUDGET/60} 分钟)")
        print(f"✅ CYCLE_TIME_BUDGET: {CYCLE_TIME_BUDGET} 秒 ({CYCLE_TIME_BUDGET/60} 分钟)")

        return True
    except Exception as e:
        print(f"❌ 常量测试失败: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting max_iterations removal verification...")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Progress Tracker Test", test_progress_tracker),
        ("EpicDriver Init Test", test_epic_driver_init),
        ("Time Budget Constants Test", test_constants)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("All tests passed! max_iterations removal successful!")
        return 0
    else:
        print("Some tests failed, please check the code")
        return 1

if __name__ == "__main__":
    sys.exit(main())
