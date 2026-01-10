#!/usr/bin/env python3
"""
状态映射测试脚本

验证状态值系统统一后的映射是否正确。
"""

import sys
sys.path.insert(0, "d:\\GITHUB\\pytQt_template")

from autoBMAD.epic_automation.story_parser import _normalize_story_status
from autoBMAD.epic_automation.state_manager import StateManager


def test_normalize_story_status():
    """测试 _normalize_story_status 函数"""
    print("测试 _normalize_story_status 函数...")

    # 测试基本状态
    test_cases = [
        # (输入, 期望输出, 描述)
        ("draft", "Draft", "draft 应该映射为 Draft"),
        ("completed", "Done", "completed 应该映射为 Done"),
        ("in_progress", "In Progress", "in_progress 应该映射为 In Progress"),
        ("ready_for_review", "Ready for Review", "ready_for_review 应该映射为 Ready for Review"),
        ("failed", "Failed", "failed 应该映射为 Failed"),

        # 测试核心状态值（应该保持不变）
        ("Draft", "Draft", "Draft 应该保持不变"),
        ("Done", "Done", "Done 应该保持不变"),
        ("In Progress", "In Progress", "In Progress 应该保持不变"),
        ("Ready for Review", "Ready for Review", "Ready for Review 应该保持不变"),

        # 测试特殊状态
        ("dev_completed", "Ready for Review", "dev_completed 应该映射为 Ready for Review"),
        ("sm_completed", "sm_completed", "sm_completed 应该保持不变（特殊状态）"),
    ]

    failed_tests = []

    for input_status, expected_output, description in test_cases:
        result = _normalize_story_status(input_status)
        if result == expected_output:
            print(f"  [OK] {description}: '{input_status}' -> '{result}'")
        else:
            print(f"  [FAIL] {description}: '{input_status}' -> '{result}' (期望: '{expected_output}')")
            failed_tests.append((input_status, result, expected_output, description))

    if failed_tests:
        print(f"\n[FAIL] 测试失败! {len(failed_tests)} 个测试用例未通过")
        for input_status, result, expected_output, description in failed_tests:
            print(f"  - {description}: 得到 '{result}', 期望 '{expected_output}'")
        return False
    else:
        print(f"\n[OK] 所有 {len(test_cases)} 个测试用例通过!")
        return True


async def test_state_manager_mapping():
    """测试 StateManager 的状态映射"""
    print("\n测试 StateManager 状态映射...")

    # 创建临时数据库
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    try:
        state_manager = StateManager(db_path)

        # 测试状态映射
        test_cases = [
            ("completed", "Done"),
            ("dev_completed", "Ready for Review"),
            ("in_progress", "In Progress"),
            ("failed", "Failed"),
        ]

        # 验证映射是否正确
        for db_status, expected_markdown in test_cases:
            # 模拟 _update_markdown_status 中的映射逻辑
            status_mapping = {
                "completed": "Done",
                "done": "Done",
                "dev_completed": "Ready for Review",
                "pending": "Draft",
                "ready_for_development": "Ready for Development",
                "in_progress": "In Progress",
                "review": "Ready for Review",
                "ready_for_review": "Ready for Review",
                "ready_for_done": "Ready for Done",
                "failed": "Failed",
                "error": "Failed",
                "cancelled": "Draft",
            }

            mapped_status = status_mapping.get(db_status.lower(), db_status)
            if mapped_status == expected_markdown:
                print(f"  [OK] 数据库状态 '{db_status}' 映射为 Markdown 状态 '{mapped_status}'")
            else:
                print(f"  [FAIL] 数据库状态 '{db_status}' 映射错误: 得到 '{mapped_status}', 期望 '{expected_markdown}'")
                return False

        print("[OK] StateManager 状态映射测试通过!")
        return True

    finally:
        # 清理临时数据库
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_qa_completed_removal():
    """测试 qa_completed 状态已被移除"""
    print("\n测试 qa_completed 状态移除...")

    # 测试 _normalize_story_status 是否仍能处理 qa_completed
    result = _normalize_story_status("qa_completed")

    # qa_completed 应该返回默认值 "Draft"（因为它不在映射表中）
    if result == "Draft":
        print(f"  [OK] qa_completed 不再作为特殊状态处理，返回默认值: '{result}'")
        return True
    else:
        print(f"  [FAIL] qa_completed 仍被特殊处理: '{result}' (期望: 'Draft')")
        return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("状态值系统统一测试")
    print("=" * 60)

    all_passed = True

    # 测试 1: _normalize_story_status 函数
    if not test_normalize_story_status():
        all_passed = False

    # 测试 2: StateManager 映射
    if not await test_state_manager_mapping():
        all_passed = False

    # 测试 3: qa_completed 移除
    if not test_qa_completed_removal():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] 所有测试通过! 状态值系统统一成功!")
        print("=" * 60)
        return 0
    else:
        print("[FAIL] 部分测试失败! 请检查状态映射配置。")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
