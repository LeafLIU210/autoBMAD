"""
端到端完整 Epic 工作流集成测试
测试真实的端到端场景
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver


@pytest.mark.e2e
@pytest.mark.anyio
async def test_complete_epic_to_deployment_pipeline():
    """测试完整的 Epic 到部署流水线"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        docs_dir = tmp_path / "docs"
        epic_dir = docs_dir / "epics"
        stories_dir = docs_dir / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建 Epic 文件
        epic_file = epic_dir / "test-epic.md"
        epic_content = """# Epic 1: 测试 Epic

## Overview
这是一个完整的端到端测试 Epic

## Stories
### Story 1.1: 功能开发
### Story 1.2: 测试实现
### Story 1.3: 集成验证

## Acceptance Criteria
- [ ] 所有功能正常工作
- [ ] 测试覆盖率达到 90%
- [ ] 集成测试通过
"""
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建 Story 文件
        for i in range(1, 4):
            story_file = stories_dir / f"1.{i}-test-story-{i}.md"
            story_content = f"""# Story 1.{i}: 功能 {i}

**Status**: Draft

## Description
这是第 {i} 个功能的实现。

## Acceptance Criteria
- [ ] 功能 {i} 正确实现
- [ ] 单元测试通过
- [ ] 代码审查完成
"""
            story_file.write_text(story_content, encoding='utf-8')

        # 创建源码和测试文件
        (src_dir / "main.py").write_text("""
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello())
""", encoding='utf-8')

        (tests_dir / "test_main.py").write_text("""
from src.main import hello

def test_hello():
    assert hello() == "Hello, World!"
""", encoding='utf-8')

        # 创建 EpicDriver
        driver = EpicDriver(
            epic_path=str(epic_file),
            max_iterations=3,
            retry_failed=True,
            verbose=True,
            concurrent=False,
            use_claude=False,
            source_dir=str(src_dir),
            test_dir=str(tests_dir),
            skip_quality=False,
            skip_tests=False
        )

        # 模拟状态解析：模拟真实的状态转换
        call_count = 0
        async def mock_parse_status(path):
            nonlocal call_count
            call_count += 1

            # 模拟状态转换：Draft -> In Progress -> Done
            if call_count % 3 == 1:
                return "Draft"
            elif call_count % 3 == 2:
                return "In Progress"
            else:
                return "Done"

        # 模拟执行阶段
        driver._parse_story_status = mock_parse_status
        driver.execute_dev_phase = AsyncMock(return_value=True)
        driver.execute_qa_phase = AsyncMock(return_value=True)

        # 模拟状态管理器
        driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
        driver.state_manager.get_story_status = AsyncMock(return_value=None)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
            "success_count": 3,
            "error_count": 0
        })

        # 执行完整流程
        result = await driver.run()

        # 验证结果
        assert result is True
        assert len(driver.stories) == 3


@pytest.mark.e2e
@pytest.mark.anyio
async def test_real_world_scenario():
    """测试真实世界场景"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        docs_dir = tmp_path / "docs"
        epic_dir = docs_dir / "epics"
        stories_dir = docs_dir / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建真实场景的 Epic
        epic_file = epic_dir / "real-world-epic.md"
        epic_content = """# Real-World Epic: 用户管理系统

## Overview
这是一个真实的用户管理系统开发 Epic，包含多个复杂的故事。

## Stories
### Story 1.1: 用户注册功能
### Story 1.2: 用户登录功能
### Story 1.3: 用户权限管理
### Story 1.4: 数据验证和安全性
### Story 1.5: 性能优化

## Acceptance Criteria
- [ ] 用户可以成功注册
- [ ] 用户可以安全登录
- [ ] 权限管理正确工作
- [ ] 所有输入都经过验证
- [ ] 系统响应时间 < 2秒
"""
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建对应的 Story 文件
        for i in range(1, 6):
            story_file = stories_dir / f"1.{i}-user-management-{i}.md"
            story_content = f"""# Story 1.{i}: 用户管理功能 {i}

**Status**: Draft

## Description
这是用户管理系统中第 {i} 个功能的实现。

## Tasks
- [ ] 设计功能架构
- [ ] 实现核心功能
- [ ] 编写单元测试
- [ ] 进行代码审查
- [ ] 集成测试

## Acceptance Criteria
- [ ] 功能 {i} 正确实现
- [ ] 测试覆盖率达到 85%
- [ ] 性能符合要求
- [ ] 安全检查通过
"""
            story_file.write_text(story_content, encoding='utf-8')

        # 创建更复杂的源码和测试
        (src_dir / "user_manager.py").write_text("""
class UserManager:
    def __init__(self):
        self.users = {}
        self.permissions = {}

    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = password
        return True

    def login(self, username, password):
        if username in self.users and self.users[username] == password:
            return True
        return False

    def has_permission(self, username, permission):
        return self.permissions.get(username, []).count(permission) > 0
""", encoding='utf-8')

        (tests_dir / "test_user_manager.py").write_text("""
from src.user_manager import UserManager

def test_register_user():
    manager = UserManager()
    assert manager.register_user("testuser", "password123") is True
    assert manager.register_user("testuser", "password123") is False

def test_login():
    manager = UserManager()
    manager.register_user("testuser", "password123")
    assert manager.login("testuser", "password123") is True
    assert manager.login("testuser", "wrongpassword") is False
""", encoding='utf-8')

        # 创建 EpicDriver
        driver = EpicDriver(
            epic_path=str(epic_file),
            max_iterations=5,
            retry_failed=True,
            verbose=True,
            concurrent=False,
            use_claude=False,
            source_dir=str(src_dir),
            test_dir=str(tests_dir),
            skip_quality=False,
            skip_tests=False
        )

        # 模拟复杂的状态转换
        async def mock_parse_status(path):
            # 根据文件名模拟不同的状态
            if "1.1" in path:
                return "Done"  # 用户注册已完成
            elif "1.2" in path:
                return "Ready for Review"  # 用户登录待审查
            elif "1.3" in path:
                return "In Progress"  # 权限管理进行中
            elif "1.4" in path:
                return "Draft"  # 数据验证刚开始
            else:
                return "Done"

        # 模拟执行阶段
        driver._parse_story_status = mock_parse_status
        driver.execute_dev_phase = AsyncMock(return_value=True)
        driver.execute_qa_phase = AsyncMock(return_value=True)

        # 模拟状态管理器
        driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
        driver.state_manager.get_story_status = AsyncMock(return_value=None)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
            "success_count": 5,
            "error_count": 0
        })

        # 执行完整流程
        result = await driver.run()

        # 验证结果
        assert result is True
        assert len(driver.stories) == 5


@pytest.mark.e2e
@pytest.mark.performance
@pytest.mark.anyio
async def test_performance_under_load():
    """测试负载下的性能"""
    import time

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        docs_dir = tmp_path / "docs"
        epic_dir = docs_dir / "epics"
        stories_dir = docs_dir / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建有多个故事的 Epic
        epic_file = epic_dir / "performance-epic.md"
        epic_content = "# Performance Test Epic\n\n"
        for i in range(1, 11):  # 10个故事
            epic_content += f"### Story {i}: 测试故事 {i}\n"
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建对应的 Story 文件
        for i in range(1, 11):
            story_file = stories_dir / f"{i}-performance-test-{i}.md"
            story_content = f"""# Story {i}: 性能测试故事 {i}

**Status**: Draft

## Description
这是性能测试的第 {i} 个故事。
"""
            story_file.write_text(story_content, encoding='utf-8')

        # 创建源码和测试
        for i in range(1, 11):
            (src_dir / f"module_{i}.py").write_text(f"""
def function_{i}():
    return {i} * 2
""", encoding='utf-8')

            (tests_dir / f"test_module_{i}.py").write_text(f"""
from src.module_{i} import function_{i}

def test_function_{i}():
    assert function_{i}() == {i * 2}
""", encoding='utf-8')

        # 创建 EpicDriver
        driver = EpicDriver(
            epic_path=str(epic_file),
            max_iterations=3,
            retry_failed=False,
            verbose=False,
            concurrent=False,
            use_claude=False,
            source_dir=str(src_dir),
            test_dir=str(tests_dir),
            skip_quality=True,
            skip_tests=True
        )

        # 模拟快速状态解析
        async def mock_parse_status(path):
            return "Done"

        # 模拟执行阶段
        driver._parse_story_status = mock_parse_status
        driver.execute_dev_phase = AsyncMock(return_value=True)
        driver.execute_qa_phase = AsyncMock(return_value=True)

        # 模拟状态管理器
        driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
        driver.state_manager.get_story_status = AsyncMock(return_value=None)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
            "success_count": 10,
            "error_count": 0
        })

        # 测量执行时间
        start_time = time.time()
        result = await driver.run()
        end_time = time.time()

        # 验证结果
        assert result is True
        assert len(driver.stories) == 10

        # 验证性能 - 应该在合理时间内完成
        execution_time = end_time - start_time
        assert execution_time < 30.0  # 30秒内完成
        print(f"Performance test completed in {execution_time:.2f} seconds")


@pytest.mark.e2e
@pytest.mark.anyio
async def test_error_recovery_scenario():
    """测试错误恢复场景"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 创建项目结构
        docs_dir = tmp_path / "docs"
        epic_dir = docs_dir / "epics"
        stories_dir = docs_dir / "stories"
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"

        for dir_path in [epic_dir, stories_dir, src_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建可能出错的 Epic
        epic_file = epic_dir / "error-recovery-epic.md"
        epic_content = """# Error Recovery Epic

## Stories
### Story 1.1: 正常功能
### Story 1.2: 可能失败的功能
### Story 1.3: 恢复后的功能

## Acceptance Criteria
- [ ] 错误被正确处理
- [ ] 系统能够恢复
- [ ] 数据一致性保持
"""
        epic_file.write_text(epic_content, encoding='utf-8')

        # 创建对应的 Story 文件
        for i in range(1, 4):
            story_file = stories_dir / f"1.{i}-error-recovery-{i}.md"
            story_content = f"""# Story 1.{i}: 错误恢复测试 {i}

**Status**: Draft

## Description
这是错误恢复测试的第 {i} 个故事。
"""
            story_file.write_text(story_content, encoding='utf-8')

        # 创建 EpicDriver，启用重试
        driver = EpicDriver(
            epic_path=str(epic_file),
            max_iterations=3,
            retry_failed=True,  # 启用重试
            verbose=True,
            concurrent=False,
            use_claude=False,
            source_dir=str(src_dir),
            test_dir=str(tests_dir),
            skip_quality=True,
            skip_tests=True
        )

        # 模拟可能出错的状态解析
        call_count = 0
        async def mock_parse_status(path):
            nonlocal call_count
            call_count += 1

            # 模拟第一次失败，第二次成功的场景
            if "1.2" in path and call_count == 2:
                raise Exception("Simulated error")
            return "Done"

        # 模拟执行阶段，其中一个会失败
        async def mock_execute_dev_phase(story_path, iteration=1):
            if "1.2" in story_path and iteration == 1:
                raise Exception("Development failed")
            return True

        # 设置模拟
        driver._parse_story_status = mock_parse_status
        driver.execute_dev_phase = mock_execute_dev_phase
        driver.execute_qa_phase = AsyncMock(return_value=True)

        # 模拟状态管理器
        driver.state_manager.update_story_status = AsyncMock(return_value=(True, 1))
        driver.state_manager.get_story_status = AsyncMock(return_value=None)
        driver.state_manager.sync_story_statuses_to_markdown = AsyncMock(return_value={
            "success_count": 3,
            "error_count": 0
        })

        # 执行流程
        result = await driver.run()

        # 验证结果 - 重试机制应该使其成功
        assert result is True
        assert len(driver.stories) == 3


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-m", "e2e"])
