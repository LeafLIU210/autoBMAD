"""
RuffAgent 重构单元测试

测试 RuffAgent 的新增功能：
1. parse_errors_by_file() - 按文件分组错误
2. build_fix_prompt() - 构造修复 Prompt
3. format() - 代码格式化
4. execute() - 使用 --fix 自动修复

作者: autoBMAD Team
日期: 2026-01-13
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from autoBMAD.epic_automation.agents.quality_agents import RuffAgent


class TestRuffAgentRefactor:
    """RuffAgent 重构测试"""

    @pytest.fixture
    def ruff_agent(self):
        """创建 RuffAgent 实例"""
        return RuffAgent()

    @pytest.mark.asyncio
    async def test_execute_with_fix_flag(self, ruff_agent):
        """测试执行使用 --fix 标志"""
        # 模拟 _run_subprocess 返回
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": json.dumps([
                {
                    "filename": "test.py",
                    "code": "F401",
                    "message": "'os' imported but unused",
                    "severity": "error",
                    "location": {"row": 1, "column": 1}
                }
            ]),
            "stderr": ""
        }

        with patch.object(ruff_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await ruff_agent.execute("src")

            # 验证使用了 --fix
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "--fix" in call_args
            assert "ruff check" in call_args

            # 验证结果解析
            assert result["status"] == "completed"
            assert result["errors"] == 1
            assert result["warnings"] == 0
            assert result["files_checked"] == 1
            assert len(result["issues"]) == 1

    @pytest.mark.asyncio
    async def test_execute_no_json_output(self, ruff_agent):
        """测试无 JSON 输出"""
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": "",
            "stderr": ""
        }

        with patch.object(ruff_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await ruff_agent.execute("src")

            assert result["status"] == "completed"
            assert result["errors"] == 0
            assert result["warnings"] == 0
            assert result["files_checked"] == 0
            assert result["issues"] == []

    def test_parse_errors_by_file_single_file(self, ruff_agent):
        """测试单文件错误分组"""
        issues = [
            {
                "filename": "test.py",
                "code": "F401",
                "message": "'os' imported but unused",
                "severity": "error",
                "location": {"row": 1, "column": 1}
            },
            {
                "filename": "test.py",
                "code": "E501",
                "message": "Line too long",
                "severity": "error",
                "location": {"row": 10, "column": 80}
            }
        ]

        result = ruff_agent.parse_errors_by_file(issues)

        assert "test.py" in result
        assert len(result["test.py"]) == 2

        # 验证错误信息结构
        error1 = result["test.py"][0]
        assert error1["line"] == 1
        assert error1["column"] == 1
        assert error1["code"] == "F401"
        assert error1["message"] == "'os' imported but unused"
        assert error1["severity"] == "error"

        error2 = result["test.py"][1]
        assert error2["line"] == 10
        assert error2["column"] == 80
        assert error2["code"] == "E501"

    def test_parse_errors_by_file_multiple_files(self, ruff_agent):
        """测试多文件错误分组"""
        issues = [
            {
                "filename": "file1.py",
                "code": "F401",
                "message": "error 1",
                "severity": "error",
                "location": {"row": 1, "column": 1}
            },
            {
                "filename": "file2.py",
                "code": "E501",
                "message": "error 2",
                "severity": "error",
                "location": {"row": 5, "column": 10}
            },
            {
                "filename": "file1.py",
                "code": "E502",
                "message": "error 3",
                "severity": "warning",
                "location": {"row": 15, "column": 5}
            }
        ]

        result = ruff_agent.parse_errors_by_file(issues)

        assert len(result) == 2
        assert "file1.py" in result
        assert "file2.py" in result
        assert len(result["file1.py"]) == 2
        assert len(result["file2.py"]) == 1

    def test_parse_errors_by_file_empty(self, ruff_agent):
        """测试空错误列表"""
        result = ruff_agent.parse_errors_by_file([])

        assert result == {}

    def test_parse_errors_by_file_missing_fields(self, ruff_agent):
        """测试缺少字段的错误"""
        issues = [
            {
                "filename": "test.py",
                "code": "F401",
                "message": "error",
                "severity": "error",
                "location": {}
            }
        ]

        result = ruff_agent.parse_errors_by_file(issues)

        assert "test.py" in result
        assert result["test.py"][0]["line"] is None
        assert result["test.py"][0]["column"] is None

    def test_build_fix_prompt(self, ruff_agent):
        """测试构造修复 Prompt"""
        errors = [
            {
                "line": 1,
                "column": 1,
                "code": "F401",
                "message": "'os' imported but unused",
                "severity": "error"
            },
            {
                "line": 10,
                "column": 80,
                "code": "E501",
                "message": "Line too long",
                "severity": "error"
            }
        ]

        prompt = ruff_agent.build_fix_prompt(
            tool="ruff",
            file_path="src/test.py",
            file_content="import os\n# code here",
            errors=errors
        )

        # 验证 Prompt 包含关键信息
        assert "src/test.py" in prompt
        assert "import os" in prompt or "os" in prompt
        assert "Error 1" in prompt
        assert "Error 2" in prompt
        assert "F401" in prompt
        assert "E501" in prompt
        assert "Line: 1" in prompt
        assert "Line: 10" in prompt
        assert "<RUFF_FIX_COMPLETE>" in prompt

    def test_format_errors_summary(self, ruff_agent):
        """测试错误摘要格式化"""
        errors = [
            {
                "line": 1,
                "column": 5,
                "code": "F401",
                "message": "'os' imported but unused",
                "severity": "error"
            },
            {
                "line": 10,
                "column": 80,
                "code": "E501",
                "message": "Line too long",
                "severity": "warning"
            }
        ]

        summary = ruff_agent._format_errors_summary(errors)

        # 验证格式
        assert "Error 1" in summary
        assert "Error 2" in summary
        assert "Line: 1" in summary
        assert "Line: 10" in summary
        assert "Code: `F401`" in summary
        assert "Code: `E501`" in summary
        assert "Severity: error" in summary
        assert "Severity: warning" in summary

    @pytest.mark.asyncio
    async def test_format_success(self, ruff_agent):
        """测试格式化成功"""
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": "",
            "stderr": ""
        }

        with patch.object(ruff_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await ruff_agent.format("src")

            # 验证调用
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "ruff format" in call_args

            # 验证结果
            assert result["status"] == "completed"
            assert result["formatted"] == True
            assert result["message"] == "Code formatted successfully"

    @pytest.mark.asyncio
    async def test_format_failure(self, ruff_agent):
        """测试格式化失败"""
        mock_result = {
            "status": "completed",
            "returncode": 1,
            "stdout": "error",
            "stderr": "error"
        }

        with patch.object(ruff_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await ruff_agent.format("src")

            assert result["status"] == "completed"
            assert result["formatted"] == False
            assert result["message"] == "Format failed"

    @pytest.mark.asyncio
    async def test_format_exception(self, ruff_agent):
        """测试格式化异常"""
        with patch.object(ruff_agent, "_run_subprocess", side_effect=Exception("Format error")):
            result = await ruff_agent.format("src")

            assert result["status"] == "failed"
            assert result["formatted"] == False
            assert "error" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_exception(self, ruff_agent):
        """测试执行异常"""
        with patch.object(ruff_agent, "_run_subprocess", side_effect=Exception("Execution error")):
            result = await ruff_agent.execute("src")

            assert result["status"] == "failed"
            assert "error" in result["error"].lower()


class TestRuffPromptTemplates:
    """Ruff Prompt 模板测试"""

    def test_ruff_fix_prompt_format(self):
        """测试 Ruff 修复 Prompt 格式"""
        from autoBMAD.epic_automation.agents.quality_agents import RUFF_FIX_PROMPT

        # 验证模板包含必要元素
        assert "<system>" in RUFF_FIX_PROMPT
        assert "<user>" in RUFF_FIX_PROMPT
        assert "Ruff" in RUFF_FIX_PROMPT
        assert "Summary of Changes" in RUFF_FIX_PROMPT
        assert "Fixed File" in RUFF_FIX_PROMPT
        assert "<RUFF_FIX_COMPLETE>" in RUFF_FIX_PROMPT
        assert "{file_path}" in RUFF_FIX_PROMPT
        assert "{file_content}" in RUFF_FIX_PROMPT
        assert "{errors_summary}" in RUFF_FIX_PROMPT

    def test_prompt_substitution(self):
        """测试 Prompt 替换"""
        from autoBMAD.epic_automation.agents.quality_agents import RUFF_FIX_PROMPT

        prompt = RUFF_FIX_PROMPT.format(
            file_path="test.py",
            file_content="print('hello')",
            errors_summary="Error summary"
        )

        # 验证替换成功
        assert "{file_path}" not in prompt
        assert "{file_content}" not in prompt
        assert "{errors_summary}" not in prompt
        assert "test.py" in prompt
        assert "print('hello')" in prompt
        assert "Error summary" in prompt
