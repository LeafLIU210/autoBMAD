"""
BasedPyrightAgent 重构单元测试

测试 BasedPyrightAgent 的新增功能：
1. parse_errors_by_file() - 按文件分组类型错误
2. build_fix_prompt() - 构造修复 Prompt
3. execute() - 执行类型检查

作者: autoBMAD Team
日期: 2026-01-13
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.epic_automation.agents.quality_agents import BasedPyrightAgent


class TestBasedPyrightAgentRefactor:
    """BasedPyrightAgent 重构测试"""

    @pytest.fixture
    def basedpyright_agent(self):
        """创建 BasedPyrightAgent 实例"""
        return BasedPyrightAgent()

    @pytest.mark.asyncio
    async def test_execute_command_format(self, basedpyright_agent):
        """测试执行命令格式"""
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": json.dumps({
                "generalDiagnostics": []
            }),
            "stderr": ""
        }

        with patch.object(basedpyright_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            await basedpyright_agent.execute("src")

            # 验证使用了正确的命令格式
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "basedpyright" in call_args
            assert "--outputjson" in call_args
            assert "src" in call_args

    @pytest.mark.asyncio
    async def test_execute_with_type_errors(self, basedpyright_agent):
        """测试执行带类型错误"""
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": json.dumps({
                "generalDiagnostics": [
                    {
                        "file": "type_error.py",
                        "severity": "error",
                        "message": "Argument of type 'str' cannot be assigned to parameter 'value' of type 'int'",
                        "rule": "reportGeneralTypeIssues",
                        "range": {
                            "start": {"line": 10, "character": 15},
                            "end": {"line": 10, "character": 20}
                        }
                    }
                ]
            }),
            "stderr": ""
        }

        with patch.object(basedpyright_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await basedpyright_agent.execute("src")

            assert result["status"] == "completed"
            assert result["errors"] == 1
            assert result["warnings"] == 0
            assert result["files_checked"] == 1
            assert len(result["issues"]) == 1

    @pytest.mark.asyncio
    async def test_execute_no_json_output(self, basedpyright_agent):
        """测试无 JSON 输出"""
        mock_result = {
            "status": "completed",
            "returncode": 0,
            "stdout": "",
            "stderr": ""
        }

        with patch.object(basedpyright_agent, "_run_subprocess", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            result = await basedpyright_agent.execute("src")

            assert result["status"] == "completed"
            assert result["errors"] == 0
            assert result["warnings"] == 0
            assert result["files_checked"] == 0
            assert result["issues"] == []

    def test_parse_errors_by_file_single_file(self, basedpyright_agent):
        """测试单文件类型错误分组"""
        issues = [
            {
                "file": "type_error.py",
                "severity": "error",
                "message": "Type mismatch",
                "rule": "reportGeneralTypeIssues",
                "range": {
                    "start": {"line": 10, "character": 5},
                    "end": {"line": 10, "character": 10}
                }
            },
            {
                "file": "type_error.py",
                "severity": "warning",
                "message": "Missing type annotation",
                "rule": "reportMissingTypeStubs",
                "range": {
                    "start": {"line": 20, "character": 0},
                    "end": {"line": 20, "character": 5}
                }
            }
        ]

        result = basedpyright_agent.parse_errors_by_file(issues)

        assert "type_error.py" in result
        assert len(result["type_error.py"]) == 2

        # 验证错误信息结构
        error1 = result["type_error.py"][0]
        assert error1["line"] == 10
        assert error1["column"] == 5
        assert error1["rule"] == "reportGeneralTypeIssues"
        assert error1["message"] == "Type mismatch"
        assert error1["severity"] == "error"

        error2 = result["type_error.py"][1]
        assert error2["line"] == 20
        assert error2["column"] == 0
        assert error2["rule"] == "reportMissingTypeStubs"
        assert error2["severity"] == "warning"

    def test_parse_errors_by_file_multiple_files(self, basedpyright_agent):
        """测试多文件类型错误分组"""
        issues = [
            {
                "file": "file1.py",
                "severity": "error",
                "message": "error 1",
                "rule": "rule1",
                "range": {"start": {"line": 1, "character": 1}}
            },
            {
                "file": "file2.py",
                "severity": "error",
                "message": "error 2",
                "rule": "rule2",
                "range": {"start": {"line": 5, "character": 10}}
            },
            {
                "file": "file1.py",
                "severity": "warning",
                "message": "warning 1",
                "rule": "rule3",
                "range": {"start": {"line": 15, "character": 5}}
            }
        ]

        result = basedpyright_agent.parse_errors_by_file(issues)

        assert len(result) == 2
        assert "file1.py" in result
        assert "file2.py" in result
        assert len(result["file1.py"]) == 2
        assert len(result["file2.py"]) == 1

    def test_parse_errors_by_file_empty(self, basedpyright_agent):
        """测试空错误列表"""
        result = basedpyright_agent.parse_errors_by_file([])

        assert result == {}

    def test_parse_errors_by_file_missing_range(self, basedpyright_agent):
        """测试缺少 range 字段"""
        issues = [
            {
                "file": "test.py",
                "severity": "error",
                "message": "error",
                "rule": "rule1",
                "range": {}
            }
        ]

        result = basedpyright_agent.parse_errors_by_file(issues)

        assert "test.py" in result
        assert result["test.py"][0]["line"] is None
        assert result["test.py"][0]["column"] is None

    def test_parse_errors_by_file_missing_file(self, basedpyright_agent):
        """测试缺少 file 字段"""
        issues = [
            {
                "severity": "error",
                "message": "error",
                "rule": "rule1",
                "range": {"start": {"line": 1, "character": 1}}
            }
        ]

        result = basedpyright_agent.parse_errors_by_file(issues)

        # 缺少 file 字段的项应该被跳过
        assert len(result) == 0

    def test_build_fix_prompt(self, basedpyright_agent):
        """测试构造修复 Prompt"""
        errors = [
            {
                "line": 10,
                "column": 15,
                "rule": "reportGeneralTypeIssues",
                "message": "Type mismatch",
                "severity": "error"
            },
            {
                "line": 20,
                "column": 0,
                "rule": "reportMissingTypeStubs",
                "message": "Missing type annotation",
                "severity": "warning"
            }
        ]

        prompt = basedpyright_agent.build_fix_prompt(
            tool="basedpyright",
            file_path="src/type_error.py",
            file_content="def func(x):\n    return x",
            errors=errors
        )

        # 验证 Prompt 包含关键信息
        assert "src/type_error.py" in prompt
        assert "def func" in prompt or "func" in prompt
        assert "Type Error 1" in prompt
        assert "Type Error 2" in prompt
        assert "reportGeneralTypeIssues" in prompt
        assert "reportMissingTypeStubs" in prompt
        assert "Line: 10" in prompt
        assert "Line: 20" in prompt
        assert "<BASEDPYRIGHT_FIX_COMPLETE>" in prompt

    def test_format_errors_summary(self, basedpyright_agent):
        """测试错误摘要格式化"""
        errors = [
            {
                "line": 10,
                "column": 15,
                "rule": "reportGeneralTypeIssues",
                "message": "Type mismatch",
                "severity": "error"
            },
            {
                "line": 20,
                "column": 0,
                "rule": "reportMissingTypeStubs",
                "message": "Missing type annotation",
                "severity": "warning"
            }
        ]

        summary = basedpyright_agent._format_errors_summary(errors)

        # 验证格式
        assert "Type Error 1" in summary
        assert "Type Error 2" in summary
        assert "Line: 10" in summary
        assert "Line: 20" in summary
        assert "Column: 15" in summary
        assert "Column: 0" in summary
        assert "Rule: `reportGeneralTypeIssues`" in summary
        assert "Rule: `reportMissingTypeStubs`" in summary
        assert "Severity: error" in summary
        assert "Severity: warning" in summary

    @pytest.mark.asyncio
    async def test_execute_exception(self, basedpyright_agent):
        """测试执行异常"""
        with patch.object(basedpyright_agent, "_run_subprocess", side_effect=Exception("Execution error")):
            result = await basedpyright_agent.execute("src")

            assert result["status"] == "failed"
            assert "error" in result["error"].lower()


class TestBasedPyrightPromptTemplates:
    """BasedPyright Prompt 模板测试"""

    def test_basedpyright_fix_prompt_format(self):
        """测试 BasedPyright 修复 Prompt 格式"""
        from autoBMAD.epic_automation.agents.quality_agents import BASEDPYRIGHT_FIX_PROMPT

        # 验证模板包含必要元素
        assert "<system>" in BASEDPYRIGHT_FIX_PROMPT
        assert "<user>" in BASEDPYRIGHT_FIX_PROMPT
        assert "BasedPyright" in BASEDPYRIGHT_FIX_PROMPT
        assert "类型注解" in BASEDPYRIGHT_FIX_PROMPT
        assert "Summary of Changes" in BASEDPYRIGHT_FIX_PROMPT
        assert "Fixed File" in BASEDPYRIGHT_FIX_PROMPT
        assert "<BASEDPYRIGHT_FIX_COMPLETE>" in BASEDPYRIGHT_FIX_PROMPT
        assert "{file_path}" in BASEDPYRIGHT_FIX_PROMPT
        assert "{file_content}" in BASEDPYRIGHT_FIX_PROMPT
        assert "{errors_summary}" in BASEDPYRIGHT_FIX_PROMPT

    def test_prompt_substitution(self):
        """测试 Prompt 替换"""
        from autoBMAD.epic_automation.agents.quality_agents import BASEDPYRIGHT_FIX_PROMPT

        prompt = BASEDPYRIGHT_FIX_PROMPT.format(
            file_path="test.py",
            file_content="def func(x): return x",
            errors_summary="Type error summary"
        )

        # 验证替换成功
        assert "{file_path}" not in prompt
        assert "{file_content}" not in prompt
        assert "{errors_summary}" not in prompt
        assert "test.py" in prompt
        assert "def func" in prompt
        assert "Type error summary" in prompt
