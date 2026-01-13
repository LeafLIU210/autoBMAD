"""
Quality Agents 单元测试
测试各种质量检查 Agent 的功能
"""

import pytest
import anyio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD"))

from autoBMAD.epic_automation.agents.quality_agents import (
    BaseQualityAgent,
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent
)


class TestQualityAgent(BaseQualityAgent):
    """测试用的质量检查 Agent"""

    async def _execute_check(self, **kwargs):
        return {"status": "completed", "success": True}


@pytest.mark.anyio
async def test_base_quality_agent_init():
    """测试 BaseQualityAgent 初始化"""
    # 不带 TaskGroup 初始化
    agent = TestQualityAgent("TestAgent")
    assert agent.name == "TestAgent"
    assert agent.task_group is None

    # 带 TaskGroup 初始化
    async with anyio.create_task_group() as tg:
        agent_with_tg = TestQualityAgent("TestAgent", tg)
        assert agent_with_tg.name == "TestAgent"
        assert agent_with_tg.task_group == tg


@pytest.mark.anyio
async def test_base_quality_agent_execute():
    """测试 BaseQualityAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = TestQualityAgent("TestAgent", tg)

        result = await agent.execute(param1="value1")

        assert result["status"] == "completed"
        assert result["success"] is True


@pytest.mark.anyio
async def test_base_quality_agent_run_subprocess():
    """测试 BaseQualityAgent 子进程执行"""
    async with anyio.create_task_group() as tg:
        agent = TestQualityAgent("TestAgent", tg)

        # 模拟成功的子进程执行
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.stdout = "Success output"
            mock_process.stderr = ""
            mock_loop.return_value.run_in_executor.return_value = mock_process

            result = await agent._run_subprocess("echo 'test'")

            assert result["status"] == "completed"
            assert result["returncode"] == 0
            assert result["success"] is True


@pytest.mark.anyio
async def test_base_quality_agent_run_subprocess_timeout():
    """测试 BaseQualityAgent 子进程超时"""
    async with anyio.create_task_group() as tg:
        agent = TestQualityAgent("TestAgent", tg)

        # 模拟超时
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.run_in_executor.side_effect = anyio.get_cancelled_exc_class()()

            result = await agent._run_subprocess("sleep 100", timeout=1)

            assert result["status"] == "failed"
            assert "Timeout" in result["error"]


@pytest.mark.anyio
async def test_ruff_agent_init():
    """测试 RuffAgent 初始化"""
    async with anyio.create_task_group() as tg:
        agent = RuffAgent(tg)
        assert agent.name == "Ruff"
        assert agent.task_group == tg


@pytest.mark.anyio
async def test_ruff_agent_execute():
    """测试 RuffAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = RuffAgent(tg)

        # 模拟子进程执行
        with patch.object(agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "returncode": 0,
                "stdout": '[]',  # 空结果
                "stderr": "",
                "success": True
            }

            result = await agent._execute_check(source_dir="src")

            assert result["status"] == "completed"
            assert result["errors"] == 0
            assert result["warnings"] == 0


@pytest.mark.anyio
async def test_based_pyright_agent_init():
    """测试 BasedPyrightAgent 初始化"""
    async with anyio.create_task_group() as tg:
        agent = BasedPyrightAgent(tg)
        assert agent.name == "BasedPyright"
        assert agent.task_group == tg


@pytest.mark.anyio
async def test_based_pyright_agent_execute():
    """测试 BasedPyrightAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = BasedPyrightAgent(tg)

        # 模拟子进程执行
        with patch.object(agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "returncode": 0,
                "stdout": '{"generalDiagnostics": []}',
                "stderr": "",
                "success": True
            }

            result = await agent._execute_check(source_dir="src")

            assert result["status"] == "completed"
            assert result["errors"] == 0
            assert result["warnings"] == 0


@pytest.mark.anyio
async def test_pytest_agent_init():
    """测试 PytestAgent 初始化"""
    async with anyio.create_task_group() as tg:
        agent = PytestAgent(tg)
        assert agent.name == "Pytest"
        assert agent.task_group == tg


@pytest.mark.anyio
async def test_pytest_agent_execute():
    """测试 PytestAgent 执行"""
    async with anyio.create_task_group() as tg:
        agent = PytestAgent(tg)

        # 模拟子进程执行
        with patch.object(agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "returncode": 0,
                "stdout": "10 passed, 0 failed in 5.0s",
                "stderr": "",
                "success": True
            }

            result = await agent._execute_check(
                source_dir="src",
                test_dir="tests"
            )

            assert result["status"] == "completed"
            assert result["tests_passed"] == 10
            assert result["tests_failed"] == 0
            assert result["total_tests"] == 10


@pytest.mark.anyio
async def test_pytest_agent_with_coverage():
    """测试 PytestAgent 带覆盖率执行"""
    async with anyio.create_task_group() as tg:
        agent = PytestAgent(tg)

        # 模拟子进程执行
        with patch.object(agent, '_run_subprocess', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                "status": "completed",
                "returncode": 0,
                "stdout": "10 passed, 0 failed in 5.0s\n{'totals': {'percent_covered': 85.5}}",
                "stderr": "",
                "success": True
            }

            result = await agent._execute_check(
                source_dir="src",
                test_dir="tests"
            )

            assert result["status"] == "completed"
            assert result["coverage"] == 85.5


@pytest.mark.anyio
async def test_quality_agents_log_execution():
    """测试质量检查 Agent 日志记录"""
    async with anyio.create_task_group() as tg:
        agent = TestQualityAgent("TestAgent", tg)

        with pytest.MonkeyPatch().context() as ctx:
            mock_log = MagicMock()
            ctx.setattr(agent.logger, 'info', mock_log)
            agent._log_execution("Test message")
            mock_log.assert_called_once()
            assert "[TestAgent] Test message" in mock_log.call_args[0][0]


@pytest.mark.anyio
async def test_all_quality_agents_with_taskgroup():
    """测试所有质量检查 Agent 在 TaskGroup 内工作"""
    async with anyio.create_task_group() as tg:
        ruff_agent = RuffAgent(tg)
        pyright_agent = BasedPyrightAgent(tg)
        pytest_agent = PytestAgent(tg)

        assert ruff_agent.task_group == tg
        assert pyright_agent.task_group == tg
        assert pytest_agent.task_group == tg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
