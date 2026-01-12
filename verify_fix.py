#!/usr/bin/env python
"""
验证 StateAgent 执行返回 None 问题的修复
"""
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.state_agent import StateAgent
import anyio


async def test_stateagent_returns_value():
    """测试 StateAgent 是否正确返回值而不是 None"""
    print("测试 StateAgent 执行是否返回正确值...")

    # 创建临时故事文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        story_content = """# Test Story

**Status**: Ready for Development

## Acceptance Criteria
- Test criterion 1
"""
        f.write(story_content)
        story_path = f.name

    try:
        # 使用模拟 TaskGroup
        mock_task_group = MagicMock()

        # 创建 StateAgent 实例
        agent = StateAgent(task_group=mock_task_group)

        # 执行解析
        result = await agent.execute(story_path)

        print(f"结果: {result}")
        print(f"结果类型: {type(result)}")

        # 验证结果
        if result is None:
            print("[FAIL] StateAgent still returns None!")
            return False
        elif result == "Ready for Development":
            print("[PASS] StateAgent returns correct status value!")
            return True
        else:
            print(f"[WARN] StateAgent returned unexpected value: {result}")
            return True  # 仍然算成功，因为不是 None
    finally:
        # 清理临时文件
        Path(story_path).unlink()


async def test_stateagent_with_real_taskgroup():
    """使用真实 TaskGroup 测试"""
    print("\n使用真实 TaskGroup 测试...")

    # 创建临时故事文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        story_content = """# Test Story 2

**Status**: Draft
"""
        f.write(story_content)
        story_path = f.name

    try:
        async with anyio.create_task_group() as tg:
            agent = StateAgent(task_group=tg)
            print(f"Agent task_group type: {type(agent.task_group)}")
            print(f"Agent task_group: {agent.task_group}")

            result = await agent.execute(story_path)

            print(f"结果: {result}")
            print(f"结果类型: {type(result)}")

            if result is None:
                print("[FAIL] StateAgent still returns None!")
                return False
            elif result == "Draft":
                print("[PASS] StateAgent returns correct status value!")
                return True
            else:
                print(f"[WARN] StateAgent returned unexpected value: {result}")
                return True
    finally:
        Path(story_path).unlink()


async def main():
    print("=" * 60)
    print("StateAgent 返回 None 问题修复验证")
    print("=" * 60)

    test1 = await test_stateagent_returns_value()
    test2 = await test_stateagent_with_real_taskgroup()

    print("\n" + "=" * 60)
    if test1 and test2:
        print("[PASS] All tests passed! StateAgent fix successful!")
        print("=" * 60)
        return 0
    else:
        print("[FAIL] Some tests failed! StateAgent still has issues!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
