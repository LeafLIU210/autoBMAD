"""
质量门控SDK调用重构专项测试

验证重构后的SDK调用符合统一接口规范：
1. 使用 sdk_helper.execute_sdk_call() 统一接口
2. 使用 ClaudeAgentOptions 对象而非字典
3. 使用 SDKResult 统一结果处理
4. 错误处理正确

作者: autoBMAD Team
日期: 2026-01-14
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from autoBMAD.epic_automation.controllers.quality_check_controller import QualityCheckController
from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType


class TestQualityCheckControllerSDKRefactor:
    """质量门控SDK调用重构验证测试"""

    @pytest.fixture
    def mock_agent(self):
        """创建模拟的 Agent"""
        agent = Mock()
        agent.execute = AsyncMock()
        agent.parse_errors_by_file = Mock()
        agent.build_fix_prompt = Mock(return_value="Mock prompt")
        return agent

    @pytest.fixture
    def controller(self, mock_agent):
        """创建 QualityCheckController 实例"""
        return QualityCheckController(
            tool="basedpyright",
            agent=mock_agent,
            source_dir="src",
            max_cycles=3,
            sdk_call_delay=60,
            sdk_timeout=600,
        )

    @pytest.mark.asyncio
    async def test_sdk_refactor_unified_interface(self, controller):
        """
        验证SDK调用使用统一接口（execute_sdk_call）

        重构前：直接实例化 SafeClaudeSDK
        重构后：使用 sdk_helper.execute_sdk_call()
        """
        # 模拟 SDKResult 成功
        mock_result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=10.0,
            session_id="test-session",
            agent_name="BasedpyrightAgent",
            error_type=SDKErrorType.SUCCESS,
            errors=[]
        )

        # 验证调用了正确的统一接口
        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_result

            result = await controller._execute_sdk_fix(
                prompt="Fix basedpyright errors",
                file_path="src/test.py"
            )

            # 验证调用了execute_sdk_call
            mock_execute.assert_called_once()

            # 验证传递的参数
            args, kwargs = mock_execute.call_args
            assert kwargs["prompt"] == "Fix basedpyright errors"
            assert kwargs["agent_name"] == "BasedpyrightAgent"
            assert kwargs["timeout"] == 600.0
            assert kwargs["permission_mode"] == "bypassPermissions"

            # 验证结果处理
            assert result["success"] is True
            assert result["result"] == mock_result
            assert result["duration"] == 10.0

    @pytest.mark.asyncio
    async def test_sdk_refactor_error_handling(self, controller):
        """
        验证SDK调用错误处理

        重构前：直接传播异常
        重构后：使用SDKResult统一错误处理
        """
        # 模拟 SDKResult 失败（SDK内部错误）
        mock_result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            duration_seconds=5.0,
            session_id="test-session",
            agent_name="BasedpyrightAgent",
            error_type=SDKErrorType.SDK_ERROR,
            errors=["SDK internal error", "Connection timeout"]
        )

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_result

            result = await controller._execute_sdk_fix(
                prompt="Fix basedpyright errors",
                file_path="src/test.py"
            )

            # 验证错误被正确处理
            assert result["success"] is False
            assert "sdk_error" in result["error"]
            assert "SDK internal error" in result["error"]
            assert "Connection timeout" in result["error"]

    @pytest.mark.asyncio
    async def test_sdk_refactor_timeout_error(self, controller):
        """验证SDK调用超时错误处理"""
        # 模拟 SDKResult 超时
        mock_result = SDKResult(
            has_target_result=False,
            cleanup_completed=False,
            duration_seconds=600.0,
            session_id="test-session",
            agent_name="BasedpyrightAgent",
            error_type=SDKErrorType.TIMEOUT,
            errors=["Operation timed out after 600 seconds"]
        )

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_result

            result = await controller._execute_sdk_fix(
                prompt="Fix basedpyright errors",
                file_path="src/test.py"
            )

            # 验证超时错误被正确处理
            assert result["success"] is False
            assert "timeout" in result["error"]
            assert "Operation timed out" in result["error"]

    @pytest.mark.asyncio
    async def test_sdk_refactor_no_sdk_error(self, controller):
        """验证SDK不可用错误处理"""
        # 模拟 SDKResult SDK不可用
        mock_result = SDKResult(
            has_target_result=False,
            cleanup_completed=True,
            duration_seconds=0.0,
            session_id="no-sdk",
            agent_name="BasedpyrightAgent",
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Claude Agent SDK not installed"]
        )

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_result

            result = await controller._execute_sdk_fix(
                prompt="Fix basedpyright errors",
                file_path="src/test.py"
            )

            # 验证SDK不可用错误被正确处理
            assert result["success"] is False
            assert "sdk_error" in result["error"]
            assert "SDK not installed" in result["error"]

    @pytest.mark.asyncio
    async def test_sdk_refactor_exception_handling(self, controller):
        """验证SDK调用异常处理"""
        # 模拟 execute_sdk_call 抛出异常
        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.side_effect = Exception("Unexpected error")

            result = await controller._execute_sdk_fix(
                prompt="Fix basedpyright errors",
                file_path="src/test.py"
            )

            # 验证异常被正确捕获
            assert result["success"] is False
            assert "Unexpected error" in result["error"]

    @pytest.mark.asyncio
    async def test_sdk_refactor_different_tools(self):
        """验证不同工具都能正确使用统一SDK接口"""
        from autoBMAD.epic_automation.agents.quality_agents import RuffAgent

        mock_agent = Mock()
        mock_agent.execute = AsyncMock()
        mock_agent.parse_errors_by_file = Mock()
        mock_agent.build_fix_prompt = Mock(return_value="Mock prompt")

        # 测试 ruff 工具
        controller = QualityCheckController(
            tool="ruff",
            agent=mock_agent,
            source_dir="src",
            max_cycles=3,
            sdk_call_delay=60,
            sdk_timeout=600,
        )

        mock_result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=8.0,
            session_id="test-session",
            agent_name="RuffAgent",
            error_type=SDKErrorType.SUCCESS,
            errors=[]
        )

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_result

            result = await controller._execute_sdk_fix(
                prompt="Fix ruff errors",
                file_path="src/test.py"
            )

            # 验证工具名称正确传递
            _, kwargs = mock_execute.call_args
            assert kwargs["agent_name"] == "RuffAgent"
            assert result["success"] is True

    def test_sdk_refactor_parameters(self, mock_agent):
        """验证SDK调用参数符合规范"""
        controller = QualityCheckController(
            tool="basedpyright",
            agent=mock_agent,
            source_dir="src",
            max_cycles=3,
            sdk_call_delay=60,
            sdk_timeout=600,
        )

        # 验证初始化参数
        assert controller.sdk_timeout == 600
        assert controller.tool == "basedpyright"

    @pytest.mark.asyncio
    async def test_sdk_refactor_integration_with_run(self, mock_agent):
        """验证重构后的SDK调用与run()方法的集成"""
        controller = QualityCheckController(
            tool="basedpyright",
            agent=mock_agent,
            source_dir="src",
            max_cycles=2,
            sdk_call_delay=60,
            sdk_timeout=600,
        )

        # 模拟检查阶段有错误，然后第二次检查没有错误
        mock_agent.execute.side_effect = [
            {
                "status": "completed",
                "issues": [{"filename": "src/test.py", "code": "E501", "message": "Line too long"}]
            },
            {
                "status": "completed",
                "issues": []  # 第二次检查无错误
            }
        ]

        # 模拟解析错误
        mock_agent.parse_errors_by_file.return_value = {
            "src/test.py": [{"line": 10, "message": "Line too long"}]
        }

        # 模拟SDK修复成功
        mock_result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=10.0,
            session_id="test-session",
            agent_name="BasedpyrightAgent",
            error_type=SDKErrorType.SUCCESS,
            errors=[]
        )

        with patch(
            "autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call",
            new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = mock_result

            # 模拟文件读取
            with patch("builtins.open", create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = "file content"
                mock_file.__enter__ = Mock(return_value=mock_file)
                mock_file.__exit__ = Mock(return_value=False)
                mock_open.return_value = mock_file

                # 模拟延时
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    # 运行完整的检查流程
                    result = await controller.run()

            # 验证使用统一SDK接口
            assert mock_execute.called

            # 验证结果正确（修复成功）
            assert result["status"] == "completed"
            assert result["tool"] == "basedpyright"
