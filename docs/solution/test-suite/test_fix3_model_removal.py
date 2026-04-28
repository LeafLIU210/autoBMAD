"""Fix-3: 移除 ANTHROPIC_MODEL_NAME 相关逻辑的测试

测试目标:
1. 验证 _create_options() 不再读取 ANTHROPIC_MODEL_NAME 环境变量
2. 验证 _create_options() 不再检查 config.model 属性
3. 验证返回的 ClaudeAgentOptions 中 model 字段为 None
"""

import ast
import inspect
import os
import pytest
from pathlib import Path
from unittest.mock import Mock


class TestCreateOptionsModelRemoval:
    """测试 _create_options 方法移除 model 相关逻辑"""
    
    def test_create_options_returns_none_model(self, temp_test_dir: Path):
        """TEST-F3-001: _create_options 返回 model=None"""
        # Arrange
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        # Act
        options = sm._create_options(mode="agent", yolo=True)
        
        # Assert
        assert options.model is None, f"Expected model=None, got {options.model}"
    
    @pytest.mark.parametrize("env_value", [
        "claude-3-opus-20240229",
        "claude-3-5-sonnet",
        "",
    ])
    def test_create_options_ignores_env_with_value(
        self, 
        monkeypatch, 
        temp_test_dir: Path,
        env_value: str
    ):
        """TEST-F3-002: 即使设置环境变量也忽略"""
        # Arrange
        monkeypatch.setenv("ANTHROPIC_MODEL_NAME", env_value)
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        # Act
        options = sm._create_options(mode="agent", yolo=True)
        
        # Assert
        assert options.model is None, f"Expected model=None even with env={env_value}"
    
    def test_create_options_ignores_config_with_model(self, temp_test_dir: Path):
        """TEST-F3-003: 即使 config 有 model 属性也忽略"""
        # Arrange
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        mock_config = Mock(spec=["model"])
        mock_config.model = "claude-3-haiku"
        
        sm = SessionManager(work_dir=temp_test_dir, config=mock_config)
        
        # Act
        options = sm._create_options(mode="agent", yolo=True)
        
        # Assert
        assert options.model is None, f"Expected model=None even if config has model attr"
    
    def test_create_options_permission_mode_bypass(self, temp_test_dir: Path):
        """TEST-F3-004: yolo=True 时 permission_mode 为 bypassPermissions"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="agent", yolo=True)
        
        assert options.permission_mode == "bypassPermissions"
    
    def test_create_options_permission_mode_default(self, temp_test_dir: Path):
        """TEST-F3-005: yolo=False 时 permission_mode 为 default"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="agent", yolo=False)
        
        assert options.permission_mode == "default"


class TestCreateOptionsBackwardCompatibility:
    """测试 _create_options 保持向后兼容的其他字段"""
    
    def test_create_options_cwd_is_set(self, temp_test_dir: Path):
        """TEST-F3-006: cwd 字段正确设置"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="agent", yolo=True)
        
        assert options.cwd == temp_test_dir
    
    def test_create_options_with_agent_file(self, temp_test_dir: Path):
        """TEST-F3-007: agent_file 正确传递给 options"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        agent_file = temp_test_dir / "agent.yaml"
        agent_file.write_text("test: true")
        
        sm = SessionManager(work_dir=temp_test_dir, agent_file=agent_file)
        options = sm._create_options(mode="agent", yolo=True)
        
        assert options.tools == [str(agent_file)]
    
    def test_create_options_thinking_mode(self, temp_test_dir: Path):
        """TEST-F3-008: thinking 模式正确设置"""
        from autoBMAD.docuswarm.llm.session_manager import SessionManager
        sm = SessionManager(work_dir=temp_test_dir)
        
        options = sm._create_options(mode="thinking", yolo=True)
        
        assert options.thinking is True


class TestOSImportUsage:
    """测试 os 模块的使用情况"""
    
    def test_no_os_environ_for_model(self):
        """TEST-F3-009: 代码中不通过 os.environ 获取 ANTHROPIC_MODEL_NAME"""
        from autoBMAD.docuswarm.llm import session_manager
        
        source_file = Path(inspect.getfile(session_manager))
        source = source_file.read_text()
        
        # 检查是否还有 ANTHROPIC_MODEL_NAME 的使用
        assert "ANTHROPIC_MODEL_NAME" not in source, \
            "ANTHROPIC_MODEL_NAME should be removed from session_manager.py"
