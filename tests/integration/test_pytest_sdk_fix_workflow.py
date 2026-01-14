"""
Pytest SDK修复工作流集成测试

测试完整的pytest ↔ SDK修复循环流程
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoBMAD.epic_automation.controllers.pytest_controller import PytestController
from autoBMAD.epic_automation.agents.quality_agents import PytestAgent


class TestPytestSDKFixWorkflow:
    """Pytest SDK修复工作流集成测试"""

    @pytest.fixture
    def temp_test_dir(self):
        """创建临时测试目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # 创建失败的测试文件
            (test_dir / "test_broken.py").write_text("""
def test_broken():
    '''A test that intentionally fails'''
    assert 1 == 2, "Expected 1 to equal 2"

def test_also_broken():
    '''Another failing test'''
    x = 1
    y = 2
    assert x == y, f"Expected {x} to equal {y}"
""")

            # 创建通过的测试文件
            (test_dir / "test_passing.py").write_text("""
def test_pass():
    '''A test that passes'''
    assert 1 == 1

def test_another_pass():
    '''Another passing test'''
    assert True
""")

            yield str(test_dir)

    @pytest.fixture
    def temp_source_dir(self):
        """创建临时源码目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "src"
            source_dir.mkdir()
            yield str(source_dir)

    @pytest.fixture
    def mock_pytest_agent(self):
        """Mock PytestAgent"""
        with patch.object(PytestAgent, '__init__', lambda x: None):
            agent = PytestAgent()
            agent.run_tests_sequential = AsyncMock()
            agent.run_sdk_fix_for_file = AsyncMock()
            yield agent

    @pytest.mark.asyncio
    async def test_successful_fix_workflow(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试成功的修复工作流：失败 → SDK修复 → 通过"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )
        controller.pytest_agent = mock_pytest_agent

        # 模拟初始测试失败
        mock_pytest_agent.run_tests_sequential.side_effect = [
            # 初始轮次：测试失败
            {
                "files": [
                    {
                        "test_file": "test_broken.py",
                        "status": "failed",
                        "failures": [
                            {
                                "nodeid": "test_broken.py::test_broken",
                                "failure_type": "failed",
                                "message": "AssertionError: Expected 1 to equal 2",
                                "short_tb": "test_broken.py:2: AssertionError",
                            }
                        ],
                    }
                ]
            },
            # 重试轮次：测试通过
            {
                "files": [
                    {
                        "test_file": "test_broken.py",
                        "status": "passed",
                        "failures": [],
                    }
                ]
            }
        ]

        # 模拟SDK修复成功
        mock_pytest_agent.run_sdk_fix_for_file.return_value = {
            "success": True
        }

        result = await controller.run()

        # 验证结果
        assert result["status"] == "completed"
        assert result["cycles"] == 2
        assert result["initial_failed_files"] == ["test_broken.py"]
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is True
        assert len(result["sdk_fix_errors"]) == 0

        # 验证调用次数
        assert mock_pytest_agent.run_tests_sequential.call_count == 2
        assert mock_pytest_agent.run_sdk_fix_for_file.call_count == 1

    @pytest.mark.asyncio
    async def test_multiple_failures_multiple_files(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试多个文件的多个失败"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )
        controller.pytest_agent = mock_pytest_agent

        # 模拟多个文件失败
        mock_pytest_agent.run_tests_sequential.side_effect = [
            # 初始轮次：多个文件失败
            {
                "files": [
                    {
                        "test_file": "test_broken.py",
                        "status": "failed",
                        "failures": [
                            {
                                "nodeid": "test_broken.py::test_broken",
                                "failure_type": "failed",
                                "message": "AssertionError",
                                "short_tb": "test_broken.py:2",
                            }
                        ],
                    },
                    {
                        "test_file": "test_passing.py",
                        "status": "passed",
                        "failures": [],
                    }
                ]
            },
            # 重试轮次：只有一个文件仍失败
            {
                "files": [
                    {
                        "test_file": "test_broken.py",
                        "status": "failed",
                        "failures": [
                            {
                                "nodeid": "test_broken.py::test_also_broken",
                                "failure_type": "failed",
                                "message": "AssertionError",
                                "short_tb": "test_broken.py:6",
                            }
                        ],
                    }
                ]
            },
            # 第二轮修复后
            {
                "files": [
                    {
                        "test_file": "test_broken.py",
                        "status": "passed",
                        "failures": [],
                    }
                ]
            }
        ]

        mock_pytest_agent.run_sdk_fix_for_file.return_value = {
            "success": True
        }

        result = await controller.run()

        # 验证结果
        assert result["status"] == "completed"
        assert result["cycles"] == 3
        assert result["initial_failed_files"] == ["test_broken.py"]
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is True

        # 验证调用次数
        assert mock_pytest_agent.run_tests_sequential.call_count == 3
        assert mock_pytest_agent.run_sdk_fix_for_file.call_count == 2

    @pytest.mark.asyncio
    async def test_sdk_fix_fails(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试SDK修复失败的情况"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )
        controller.pytest_agent = mock_pytest_agent

        # 模拟测试一直失败
        mock_pytest_agent.run_tests_sequential.return_value = {
            "files": [
                {
                    "test_file": "test_broken.py",
                    "status": "failed",
                    "failures": [
                        {
                            "nodeid": "test_broken.py::test_broken",
                            "failure_type": "failed",
                            "message": "AssertionError",
                            "short_tb": "test_broken.py:2",
                        }
                    ],
                }
            ]
        }

        # 模拟SDK修复失败
        mock_pytest_agent.run_sdk_fix_for_file.return_value = {
            "success": False,
            "error": "SDK修复失败：无法修复代码"
        }

        result = await controller.run()

        # 验证结果
        assert result["status"] == "failed"
        assert result["cycles"] == 3  # current_cycle will be 3 after max_cycles exceeded
        assert result["initial_failed_files"] == ["test_broken.py"]
        assert result["final_failed_files"] == ["test_broken.py"]
        assert result["sdk_fix_attempted"] is True
        assert len(result["sdk_fix_errors"]) == 2  # 每次轮次都失败

    @pytest.mark.asyncio
    async def test_max_cycles_reached(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试达到最大循环次数"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=3,
        )
        controller.pytest_agent = mock_pytest_agent

        # 模拟测试一直失败
        mock_pytest_agent.run_tests_sequential.return_value = {
            "files": [
                {
                    "test_file": "test_broken.py",
                    "status": "failed",
                    "failures": [
                        {
                            "nodeid": "test_broken.py::test_broken",
                            "failure_type": "failed",
                            "message": "AssertionError",
                            "short_tb": "test_broken.py:2",
                        }
                    ],
                }
            ]
        }

        mock_pytest_agent.run_sdk_fix_for_file.return_value = {
            "success": False,
            "error": "SDK error"
        }

        result = await controller.run()

        # 验证结果
        assert result["status"] == "failed"
        assert result["cycles"] == 4  # current_cycle will be 4 after max_cycles exceeded
        assert result["initial_failed_files"] == ["test_broken.py"]
        assert result["final_failed_files"] == ["test_broken.py"]
        assert result["sdk_fix_attempted"] is True

        # 验证调用次数：4轮测试 + 3轮SDK修复
        assert mock_pytest_agent.run_tests_sequential.call_count == 4
        assert mock_pytest_agent.run_sdk_fix_for_file.call_count == 3

    @pytest.mark.asyncio
    async def test_all_tests_pass_initial(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试初始轮次所有测试都通过"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=3,
        )
        controller.pytest_agent = mock_pytest_agent

        # 模拟初始轮次所有测试通过
        mock_pytest_agent.run_tests_sequential.return_value = {
            "files": [
                {
                    "test_file": "test_passing.py",
                    "status": "passed",
                    "failures": [],
                }
            ]
        }

        result = await controller.run()

        # 验证结果
        assert result["status"] == "completed"
        assert result["cycles"] == 1
        assert result["initial_failed_files"] == []
        assert result["final_failed_files"] == []
        assert result["sdk_fix_attempted"] is False

        # 验证没有进行SDK修复
        assert mock_pytest_agent.run_sdk_fix_for_file.call_count == 0

    def test_summary_json_structure(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试汇总JSON结构"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json_path = f.name

        try:
            controller = PytestController(
                source_dir=temp_source_dir,
                test_dir=temp_test_dir,
                summary_json_path=json_path,
            )
            controller.pytest_agent = mock_pytest_agent

            # 模拟测试结果
            asyncio.run(controller._run_test_phase_all_files(round_index=1))

            # 验证JSON文件结构
            with open(json_path, "r") as f:
                data = json.load(f)

            assert "summary" in data
            assert "rounds" in data
            assert "total_files" in data["summary"]
            assert "failed_files_initial" in data["summary"]
            assert "failed_files_final" in data["summary"]
            assert "cycles" in data["summary"]

            assert len(data["rounds"]) == 1
            assert data["rounds"][0]["round_index"] == 1
            assert data["rounds"][0]["round_type"] == "initial"
            assert "timestamp" in data["rounds"][0]
            assert "failed_files" in data["rounds"][0]

        finally:
            Path(json_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_sdk_phase_error_handling(
        self,
        temp_source_dir,
        temp_test_dir,
        mock_pytest_agent
    ):
        """测试SDK阶段错误处理"""
        controller = PytestController(
            source_dir=temp_source_dir,
            test_dir=temp_test_dir,
            max_cycles=2,
        )
        controller.pytest_agent = mock_pytest_agent

        # 模拟测试失败
        mock_pytest_agent.run_tests_sequential.return_value = {
            "files": [
                {
                    "test_file": "test_broken.py",
                    "status": "failed",
                    "failures": [
                        {
                            "nodeid": "test_broken.py::test_broken",
                            "failure_type": "failed",
                            "message": "AssertionError",
                            "short_tb": "test_broken.py:2",
                        }
                    ],
                }
            ]
        }

        # 模拟SDK修复抛出异常
        mock_pytest_agent.run_sdk_fix_for_file.side_effect = Exception("SDK connection error")

        # 应该继续执行而不是崩溃
        await controller._run_sdk_phase(
            failed_files=["test_broken.py"],
            round_index=1
        )

        # 验证错误被记录
        assert len(controller.sdk_fix_errors) == 1
        assert "SDK phase exception" in controller.sdk_fix_errors[0]["error"]

        # 验证下一轮测试仍会执行
        # （这里只是测试SDK阶段不会崩溃，实际执行需要更多mock）

    @pytest.mark.asyncio
    async def test_integration_with_pytest_agent_sequential(
        self,
        temp_source_dir,
        temp_test_dir
    ):
        """测试与PytestAgent顺序执行的集成"""
        agent = PytestAgent()

        # Mock _run_subprocess to simulate pytest execution
        agent._run_subprocess = AsyncMock(return_value={
            "status": "completed",
            "returncode": 0,
            "stdout": "2 passed",
            "stderr": ""
        })

        # Mock _parse_json_report - return empty list for passing tests
        agent._parse_json_report = MagicMock(return_value=[])

        result = await agent.run_tests_sequential(
            test_files=["test_file.py"],
            timeout_per_file=60,
            round_index=1,
            round_type="initial"
        )

        # 验证结果结构
        assert "files" in result
        assert len(result["files"]) == 1
        assert result["files"][0]["test_file"] == "test_file.py"
        assert result["files"][0]["status"] == "passed"
        assert result["files"][0]["failures"] == []

    @pytest.mark.asyncio
    async def test_integration_with_pytest_agent_sdk_fix(
        self,
        temp_source_dir,
        temp_test_dir
    ):
        """测试与PytestAgent SDK修复的集成"""
        agent = PytestAgent()

        # 创建临时测试文件
        test_file = Path(temp_test_dir) / "test_sample.py"
        test_file.write_text("""
def test_sample():
    assert 1 == 1
""")

        # 创建临时JSON文件
        summary_data = {
            "rounds": [
                {
                    "round_index": 1,
                    "failed_files": [
                        {
                            "test_file": str(test_file),
                            "status": "failed",
                            "failures": [
                                {
                                    "nodeid": "test_sample.py::test_sample",
                                    "failure_type": "failed",
                                    "message": "Error",
                                    "short_tb": "Error",
                                }
                            ],
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(summary_data, f)
            json_path = f.name

        try:
            # Mock _execute_sdk_call_with_cancel
            agent._execute_sdk_call_with_cancel = AsyncMock(return_value={
                "success": True
            })

            result = await agent.run_sdk_fix_for_file(
                test_file=str(test_file),
                source_dir=temp_source_dir,
                summary_json_path=json_path,
                round_index=1,
            )

            # 验证结果
            assert "success" in result
            assert result["success"] is True

        finally:
            Path(json_path).unlink(missing_ok=True)
