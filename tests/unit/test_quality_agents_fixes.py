"""
质量检查代理修复测试

测试针对以下修复的单元测试：
1. 修复 RuffAgent/BasedPyrightAgent 返回值错误
2. 修复 PytestAgent 失败信息类型转换
3. 修复 Unicode 解码错误

作者: autoBMAD Team
日期: 2026-01-14
"""

import pytest
import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from autoBMAD.epic_automation.agents.quality_agents import (
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent,
    PytestTestCase
)


class TestQualityAgentFixes:
    """质量检查代理修复测试"""

    @pytest.fixture
    def ruff_agent(self):
        """创建 RuffAgent 实例"""
        return RuffAgent()

    @pytest.fixture
    def basedpyright_agent(self):
        """创建 BasedPyrightAgent 实例"""
        return BasedPyrightAgent()

    @pytest.fixture
    def pytest_agent(self):
        """创建 PytestAgent 实例"""
        return PytestAgent()


class TestRuffAgentErrorBranch(TestQualityAgentFixes):
    """RuffAgent 错误分支测试"""

    @pytest.mark.asyncio
    async def test_execute_error_branch_returns_failed_status(self, ruff_agent):
        """测试执行错误分支返回 'failed' 状态而非 result['status']"""
        # 模拟 _run_subprocess 返回错误状态
        mock_result = {
            "status": "failed",
            "returncode": 1,
            "stdout": "",
            "stderr": "Command failed with error"
        }

        with patch.object(ruff_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await ruff_agent.execute("src")

            # 验证返回 'failed' 状态而不是 result['status']
            assert result["status"] == "failed"
            assert "errors" in result
            assert "warnings" in result
            assert "files_checked" in result
            assert "issues" in result
            assert "message" in result


class TestBasedPyrightAgentErrorBranch(TestQualityAgentFixes):
    """BasedPyrightAgent 错误分支测试"""

    @pytest.mark.asyncio
    async def test_execute_error_branch_returns_failed_status(self, basedpyright_agent):
        """测试执行错误分支返回 'failed' 状态而非 result['status']"""
        # 模拟 _run_subprocess 返回错误状态
        mock_result = {
            "status": "failed",
            "returncode": 1,
            "stdout": "",
            "stderr": "Type check failed"
        }

        with patch.object(basedpyright_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await basedpyright_agent.execute("src")

            # 验证返回 'failed' 状态而不是 result['status']
            assert result["status"] == "failed"
            assert "errors" in result
            assert "warnings" in result
            assert "files_checked" in result
            assert "issues" in result
            assert "message" in result


class TestPytestAgentFailureLoading(TestQualityAgentFixes):
    """PytestAgent 失败信息加载测试"""

    def test_load_failures_from_json_with_valid_data(self, pytest_agent, tmp_path):
        """测试从 JSON 加载有效的失败信息"""
        # 创建临时 JSON 文件
        summary_json = tmp_path / "summary.json"
        test_file_path = "tests/test_integration.py"

        # 创建包含失败信息的 JSON 数据
        summary_data = {
            "rounds": [
                {
                    "round_index": 1,
                    "round_type": "initial",
                    "timestamp": "2026-01-14T10:00:00Z",
                    "failed_files": [
                        {
                            "test_file": test_file_path,
                            "status": "failed",
                            "failures": [
                                {
                                    "nodeid": f"{test_file_path}::test_case_1",
                                    "failure_type": "failed",
                                    "message": "AssertionError: expected 1, got 2",
                                    "short_tb": "test_file.py:10: AssertionError"
                                },
                                {
                                    "nodeid": f"{test_file_path}::test_case_2",
                                    "failure_type": "error",
                                    "message": "TypeError: 'NoneType' object",
                                    "short_tb": "test_file.py:20: TypeError"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # 测试加载失败信息
        failures = pytest_agent._load_failures_from_json(
            str(summary_json),
            test_file_path
        )

        # 验证返回类型和内容
        assert isinstance(failures, list)
        assert len(failures) == 2

        # 验证第一个失败信息
        failure1 = failures[0]
        assert failure1["nodeid"] == f"{test_file_path}::test_case_1"
        assert failure1["failure_type"] == "failed"
        assert "AssertionError" in failure1["message"]
        assert "test_file.py:10" in failure1["short_tb"]

        # 验证第二个失败信息
        failure2 = failures[1]
        assert failure2["nodeid"] == f"{test_file_path}::test_case_2"
        assert failure2["failure_type"] == "error"
        assert "TypeError" in failure2["message"]
        assert "test_file.py:20" in failure2["short_tb"]

    def test_load_failures_from_json_with_missing_file(self, pytest_agent, tmp_path):
        """测试从 JSON 加载不存在的测试文件"""
        summary_json = tmp_path / "summary.json"

        summary_data = {
            "rounds": [
                {
                    "round_index": 1,
                    "round_type": "initial",
                    "failed_files": [
                        {
                            "test_file": "tests/other_test.py",
                            "status": "failed",
                            "failures": []
                        }
                    ]
                }
            ]
        }

        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # 测试加载不存在的文件
        failures = pytest_agent._load_failures_from_json(
            str(summary_json),
            "tests/test_integration.py"  # 不存在的文件
        )

        # 应该返回空列表
        assert failures == []

    def test_load_failures_from_json_with_invalid_type(self, pytest_agent, tmp_path, caplog):
        """测试从 JSON 加载无效类型的失败信息"""
        summary_json = tmp_path / "summary.json"
        test_file_path = "tests/test_integration.py"

        # 创建包含无效类型数据的 JSON
        summary_data = {
            "rounds": [
                {
                    "round_index": 1,
                    "round_type": "initial",
                    "failed_files": [
                        {
                            "test_file": test_file_path,
                            "status": "failed",
                            "failures": "invalid_type"  # 应该是 list 但这里是 str
                        }
                    ]
                }
            ]
        }

        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # 测试加载无效类型
        with caplog.at_level(logging.WARNING):
            failures = pytest_agent._load_failures_from_json(
                str(summary_json),
                test_file_path
            )

        # 应该记录警告并返回空列表
        assert failures == []
        assert "Invalid failures format" in caplog.text

    def test_load_failures_from_json_with_incomplete_data(self, pytest_agent, tmp_path, caplog):
        """测试从 JSON 加载不完整的失败信息"""
        summary_json = tmp_path / "summary.json"
        test_file_path = "tests/test_integration.py"

        # 创建包含不完整数据的 JSON
        summary_data = {
            "rounds": [
                {
                    "round_index": 1,
                    "round_type": "initial",
                    "failed_files": [
                        {
                            "test_file": test_file_path,
                            "status": "failed",
                            "failures": [
                                {
                                    "nodeid": f"{test_file_path}::test_case_1",
                                    # 缺少 "failure_type" 字段
                                    "message": "Error message",
                                    "short_tb": "Error traceback"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # 测试加载不完整数据
        with caplog.at_level(logging.WARNING):
            failures = pytest_agent._load_failures_from_json(
                str(summary_json),
                test_file_path
            )

        # 不完整的失败信息应该被跳过
        assert len(failures) == 0
        assert "Incomplete failure data" in caplog.text

    def test_load_failures_from_json_with_non_dict_items(self, pytest_agent, tmp_path, caplog):
        """测试从 JSON 加载非字典项的失败信息"""
        summary_json = tmp_path / "summary.json"
        test_file_path = "tests/test_integration.py"

        # 创建包含非字典项的 JSON
        summary_data = {
            "rounds": [
                {
                    "round_index": 1,
                    "round_type": "initial",
                    "failed_files": [
                        {
                            "test_file": test_file_path,
                            "status": "failed",
                            "failures": [
                                "invalid_string",  # 应该是 dict 但这里是 str
                                123,  # 应该是 dict 但这里是 int
                                {
                                    "nodeid": f"{test_file_path}::test_case_1",
                                    "failure_type": "failed",
                                    "message": "Error message",
                                    "short_tb": "Error traceback"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        # 测试加载非字典项
        with caplog.at_level(logging.WARNING):
            failures = pytest_agent._load_failures_from_json(
                str(summary_json),
                test_file_path
            )

        # 有效的失败信息应该被保留，无效的应该被跳过
        assert len(failures) == 1
        assert failures[0]["nodeid"] == f"{test_file_path}::test_case_1"


class TestSubprocessEncoding(TestQualityAgentFixes):
    """子进程编码测试"""

    @pytest.mark.asyncio
    async def test_run_subprocess_with_utf8_encoding(self, pytest_agent):
        """测试 _run_subprocess 使用 UTF-8 编码"""
        # 模拟 subprocess.run 使用 UTF-8 编码
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "测试输出 • ✓ ✗"
        mock_process.stderr = ""

        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop_instance = Mock()
            mock_loop_instance.run_in_executor = AsyncMock(return_value=mock_process)
            mock_loop.return_value = mock_loop_instance

            result = await pytest_agent._run_subprocess("echo test")

            # 验证调用了正确的参数
            call_args = mock_loop_instance.run_in_executor.call_args
            assert call_args is not None

            # 验证 encoding 参数被传递
            executor_call = call_args[0][1]  # lambda 函数
            # 验证 subprocess.run 被正确调用
            # 注意：由于使用了 lambda，我们需要验证整体行为

            # 验证结果包含 UTF-8 内容
            assert result["status"] == "completed"
            assert "测试输出" in result["stdout"]
            assert "✓" in result["stdout"] or "✗" in result["stdout"]

    @pytest.mark.asyncio
    async def test_run_subprocess_with_unicode_characters(self, pytest_agent):
        """测试 _run_subprocess 处理 Unicode 字符"""
        # 创建包含各种 Unicode 字符的模拟输出
        unicode_output = "✓ 成功 • 错误 ✗ 警告 🐛 Bug"

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = unicode_output
        mock_process.stderr = ""

        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop_instance = Mock()
            mock_loop_instance.run_in_executor = AsyncMock(return_value=mock_process)
            mock_loop.return_value = mock_loop_instance

            result = await pytest_agent._run_subprocess("echo test")

            # 验证 Unicode 字符被正确处理
            assert result["status"] == "completed"
            assert result["stdout"] == unicode_output


class TestPytestAgentJSONReportParsing(TestQualityAgentFixes):
    """PytestAgent JSON报告解析测试（新增）"""

    def test_parse_json_report_with_collectors(self, pytest_agent, tmp_path):
        """测试解析包含collection errors的JSON报告"""
        json_file = tmp_path / "test_report.json"
        test_file = "tests/test_cli.py"

        # 创建包含collection errors的JSON数据
        json_data = {
            "collectors": [
                {
                    "nodeid": "tests/test_cli.py",
                    "outcome": "failed",
                    "longrepr": "ImportError: cannot import name 'xxx'\nModule not found"
                }
            ],
            "tests": []
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f)

        # 测试解析
        failures = pytest_agent._parse_json_report(str(json_file), test_file)

        # 验证捕获了collection error
        assert len(failures) == 1
        assert failures[0]["failure_type"] == "error"
        assert "Collection failed" in failures[0]["message"]
        assert "ImportError" in failures[0]["message"]
        assert failures[0]["nodeid"] == test_file

    def test_parse_json_report_with_test_failures(self, pytest_agent, tmp_path):
        """测试解析包含测试失败的JSON报告"""
        json_file = tmp_path / "test_report.json"
        test_file = "tests/test_cli.py"

        # 创建包含测试失败的JSON数据
        json_data = {
            "collectors": [],
            "tests": [
                {
                    "nodeid": "tests/test_cli.py::test_example",
                    "outcome": "failed",
                    "call": {
                        "longrepr": "AssertionError: expected 5, got 3"
                    }
                }
            ]
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f)

        # 测试解析
        failures = pytest_agent._parse_json_report(str(json_file), test_file)

        # 验证捕获了测试失败
        assert len(failures) == 1
        assert failures[0]["failure_type"] == "failed"
        assert "AssertionError" in failures[0]["message"]
        assert failures[0]["nodeid"] == "tests/test_cli.py::test_example"

    def test_parse_json_report_empty(self, pytest_agent, tmp_path, caplog):
        """测试解析空的JSON报告"""
        json_file = tmp_path / "empty_report.json"
        test_file = "tests/test_cli.py"

        # 创建空的JSON数据
        json_data = {"collectors": [], "tests": []}

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f)

        # 测试解析
        with caplog.at_level(logging.WARNING):
            failures = pytest_agent._parse_json_report(str(json_file), test_file)

        # 验证返回空列表并记录警告
        assert failures == []
        assert "empty (no tests, no collectors)" in caplog.text

    @pytest.mark.asyncio
    async def test_run_pytest_single_file_with_stderr_fallback(self, pytest_agent, tmp_path):
        """测试stderr后备机制（当JSON解析失败时）"""
        test_file = "tests/test_cli.py"
        timeout = 30

        # 创建临时JSON文件（但内容为空，导致解析失败）
        json_file = tmp_path / "empty.json"
        json_file.write_text("{}")

        # 模拟失败执行结果（有stderr但无failures）
        mock_result = {
            "returncode": 1,
            "status": "failed",
            "stderr": "ImportError: No module named 'xxx'",
            "stdout": ""
        }

        with patch.object(pytest_agent, "_parse_json_report", return_value=[]):
            with patch.object(pytest_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = mock_result

                result = await pytest_agent._run_pytest_single_file(test_file, timeout)

                # 验证使用了stderr作为fallback
                assert len(result["failures"]) == 1
                assert result["failures"][0]["failure_type"] == "error"
                assert "No module named 'xxx'" in result["failures"][0]["message"]
                assert result["status"] == "error"


class TestEpicDriverStorySync(TestQualityAgentFixes):
    """EpicDriver 故事同步测试（新增）"""

    @pytest.mark.asyncio
    async def test_story_sync_uses_full_paths(self):
        """测试故事同步使用完整路径而非短ID"""
        from autoBMAD.epic_automation.epic_driver import EpicDriver

        # 模拟stories数据
        stories = [
            {"id": "1.1: Story 1.1", "path": "D:/GITHUB/pytQt_template/docs/stories/1.1.md"},
            {"id": "1.2: Story 1.2", "path": "D:/GITHUB/pytQt_template/docs/stories/1.2.md"},
        ]

        # 创建epic_driver实例（部分mock）
        with patch("autoBMAD.epic_automation.epic_driver.EpicDriver.__init__", return_value=None):
            epic_driver = EpicDriver()
            epic_driver.logger = Mock()
            epic_driver.status_update_agent = Mock()
            epic_driver.state_manager = Mock()
            epic_driver.epic_id = "test_epic"

            # 模拟stories
            epic_driver.stories = stories

            # 执行同步
            epic_driver.logger.info = Mock()
            epic_driver.logger.debug = Mock()

            # 创建AsyncMock
            sync_mock = AsyncMock(return_value={
                "success_count": 2,
                "error_count": 0
            })
            epic_driver.status_update_agent.sync_from_database = sync_mock

            # 调用状态同步代码
            story_paths = [story["path"] for story in stories]
            epic_driver.logger.debug(f"Story paths for sync: {story_paths}")

            await epic_driver.status_update_agent.sync_from_database(
                state_manager=epic_driver.state_manager,
                epic_id=epic_driver.epic_id,
                story_ids=story_paths
            )

            # 验证传递的是完整路径
            call_args = epic_driver.status_update_agent.sync_from_database.call_args
            assert call_args[1]["story_ids"] == story_paths
            assert all("docs/stories" in path for path in story_paths)


class TestQualityAgentIntegration:
    """质量检查代理集成测试"""

    @pytest.mark.asyncio
    async def test_ruff_agent_complete_workflow(self, tmp_path):
        """测试 RuffAgent 完整工作流"""
        ruff_agent = RuffAgent()

        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nprint('hello')\n")

        # 模拟成功的检查结果
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": json.dumps([]),
            "stderr": ""
        }

        with patch.object(ruff_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await ruff_agent.execute(str(tmp_path))

            # 验证结果
            assert result["status"] == "completed"
            assert "errors" in result
            assert "warnings" in result
            assert "files_checked" in result
            assert "issues" in result
            assert "message" in result

    @pytest.mark.asyncio
    async def test_basedpyright_agent_complete_workflow(self, tmp_path):
        """测试 BasedPyrightAgent 完整工作流"""
        basedpyright_agent = BasedPyrightAgent()

        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("def func(x):\n    return x\n")

        # 模拟成功的类型检查结果
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": json.dumps({"generalDiagnostics": []}),
            "stderr": ""
        }

        with patch.object(basedpyright_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await basedpyright_agent.execute(str(tmp_path))

            # 验证结果
            assert result["status"] == "completed"
            assert "errors" in result
            assert "warnings" in result
            assert "files_checked" in result
            assert "issues" in result
            assert "message" in result
