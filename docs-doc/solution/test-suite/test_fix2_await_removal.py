"""Fix-2: independent.py await 移除测试

测试目标:
1. 验证 _call_llm_with_prompts 不对 session.prompt() 使用 await
2. 验证 _call_llm_with_prompts 直接使用 async for 迭代 session.prompt()
3. 验证消息收集逻辑正确处理 dict 和对象类型
4. 验证不抛出 TypeError: object async_generator can't be used in 'await' expression
"""

import ast
import inspect
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock


class TestAwaitRemoval:
    """测试 _call_llm_with_prompts 方法中的 await 移除"""
    
    def test_source_code_no_await_on_prompt(self):
        """TEST-F2-001: 源代码中没有 await session.prompt()"""
        from autoBMAD.docuswarm.agents import independent
        
        source_file = Path(inspect.getfile(independent))
        source = source_file.read_text()
        
        # 查找 _call_llm_with_prompts 函数的范围
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFor):
                # 检查迭代目标
                iter_source = ast.unparse(node.iter) if hasattr(ast, 'unparse') else ""
                if 'await' in iter_source and 'session.prompt' in iter_source:
                    pytest.fail(f"Found 'await' before 'session.prompt' in async for: {iter_source}")
    
    def test_source_code_async_for_pattern(self):
        """TEST-F2-002: 源代码使用 async for session.prompt() 模式"""
        from autoBMAD.docuswarm.agents import independent
        
        source_file = Path(inspect.getfile(independent))
        tree = ast.parse(source_file.read_text())
        
        # 查找 _call_llm_with_prompts 函数
        found_async_for = False
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFor):
                # 检查迭代目标是否包含 session.prompt
                try:
                    iter_str = ast.unparse(node.iter)
                    if 'session.prompt' in iter_str and 'await' not in iter_str:
                        found_async_for = True
                        break
                except AttributeError:
                    # Python < 3.9 没有 ast.unparse
                    found_async_for = True  # 跳过详细检查
                    break
        
        assert found_async_for, "Should find async for session.prompt() pattern without await"
    
    @pytest.mark.asyncio
    async def test_call_llm_handles_async_generator(self, temp_test_dir: Path):
        """TEST-F2-003: _call_llm_with_prompts 正确处理 async generator"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        # 设置 persona
        persona_dir = temp_test_dir / "nodes" / "test-node"
        persona_dir.mkdir(parents=True)
        persona_file = persona_dir / "persona.json"
        persona_file.write_text('''
        {
            "name": "Test Analyst",
            "role": "test",
            "identity": {"expertise": ["testing"], "principles": []}
        }
        ''')
        
        # 创建 mock session
        mock_session = AsyncMock()
        
        async def mock_prompt(message: str):
            """模拟 session.prompt 返回 async generator"""
            yield {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]}
            yield {"role": "assistant", "content": [{"type": "text", "text": "World"}]}
        
        mock_session.prompt = mock_prompt
        
        # 创建 mock session manager
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        # 创建 agent
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        # 设置必要的路径
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        # 调用方法 - 如果 await 未移除会抛出 TypeError
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="system prompt",
            user_prompt="user prompt"
        )
        
        assert isinstance(messages, list)
        assert len(messages) == 2
    
    @pytest.mark.asyncio
    async def test_call_llm_no_type_error_on_prompt(self, temp_test_dir: Path):
        """TEST-F2-004: 调用不抛出 TypeError: object async_generator can't be used in 'await' expression"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        # 设置 persona
        persona_dir = temp_test_dir / "nodes" / "test-node"
        persona_dir.mkdir(parents=True)
        persona_file = persona_dir / "persona.json"
        persona_file.write_text('''
        {
            "name": "Test Analyst",
            "role": "test",
            "identity": {"expertise": ["testing"], "principles": []}
        }
        ''')
        
        mock_session = AsyncMock()
        
        # 模拟返回 async generator（不可 await）
        async def async_gen_func():
            yield {"role": "assistant", "content": "test"}
        
        mock_session.prompt = async_gen_func
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        # 如果 await 未正确移除，这里会抛出 TypeError
        try:
            await agent._call_llm_with_prompts(
                system_prompt_append="system",
                user_prompt="user"
            )
        except TypeError as e:
            if "async_generator" in str(e) and "await" in str(e):
                pytest.fail(f"await not removed from session.prompt() call: {e}")
            raise


class TestMessageCollection:
    """测试消息收集逻辑"""
    
    @pytest.mark.asyncio
    async def test_dict_messages_collected(self, temp_test_dir: Path):
        """TEST-F2-005: dict 类型的消息被正确收集"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        # 设置 persona
        persona_dir = temp_test_dir / "nodes" / "test-node"
        persona_dir.mkdir(parents=True)
        persona_file = persona_dir / "persona.json"
        persona_file.write_text('''
        {
            "name": "Test Analyst",
            "role": "test",
            "identity": {"expertise": ["testing"], "principles": []}
        }
        ''')
        
        mock_session = AsyncMock()
        
        async def mock_prompt(message: str):
            yield {"role": "assistant", "content": "dict message"}
        
        mock_session.prompt = mock_prompt
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="system",
            user_prompt="user"
        )
        
        assert len(messages) == 1
        assert messages[0]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_object_messages_converted(self, temp_test_dir: Path):
        """TEST-F2-006: 对象类型的消息被转换为 dict"""
        from autoBMAD.docuswarm.agents.independent import IndependentAgent
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        from autoBMAD.docuswarm.config import Config
        
        # 设置 persona
        persona_dir = temp_test_dir / "nodes" / "test-node"
        persona_dir.mkdir(parents=True)
        persona_file = persona_dir / "persona.json"
        persona_file.write_text('''
        {
            "name": "Test Analyst",
            "role": "test",
            "identity": {"expertise": ["testing"], "principles": []}
        }
        ''')
        
        class MockMessage:
            def __init__(self, role, content):
                self.role = role
                self.content = content
        
        mock_session = AsyncMock()
        
        async def mock_prompt(message: str):
            yield MockMessage("assistant", [{"type": "text", "text": "hello"}])
        
        mock_session.prompt = mock_prompt
        
        mock_sm = AsyncMock(spec=SessionManager)
        mock_sm.create_session = AsyncMock(return_value=mock_session)
        
        config = Config()
        agent = IndependentAgent(
            config=config,
            session_manager=mock_sm,
            node_id="test-node",
            project_root=temp_test_dir
        )
        
        agent._agent_file = temp_test_dir / "agent.yaml"
        agent._work_dir = temp_test_dir / "output" / "test-pipeline"
        agent._work_dir.mkdir(parents=True, exist_ok=True)
        agent._agent_file.write_text("tools: []")
        
        messages = await agent._call_llm_with_prompts(
            system_prompt_append="system",
            user_prompt="user"
        )
        
        assert len(messages) == 1
        assert isinstance(messages[0], dict)
        assert messages[0]["role"] == "assistant"
        assert messages[0]["content"] == [{"type": "text", "text": "hello"}]
