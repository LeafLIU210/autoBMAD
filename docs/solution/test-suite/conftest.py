"""Session 执行失败修复测试的配置和共享夹具"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """创建临时测试目录"""
    temp_dir = Path(tempfile.mkdtemp(prefix="session_fix_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_env_clean(monkeypatch):
    """清理与 model 相关的环境变量"""
    # 保存原始值
    orig_env = os.environ.get("ANTHROPIC_MODEL_NAME")
    
    # 删除环境变量
    monkeypatch.delenv("ANTHROPIC_MODEL_NAME", raising=False)
    
    yield
    
    # 恢复原始值
    if orig_env is not None:
        os.environ["ANTHROPIC_MODEL_NAME"] = orig_env


@pytest.fixture
def sample_persona_json():
    """示例 persona JSON 内容"""
    return '''
    {
        "name": "Test Analyst",
        "role": "analyst",
        "identity": {
            "expertise": ["analysis", "testing"],
            "principles": ["accuracy", "clarity"]
        },
        "skills": {
            "technical": ["data-analysis"],
            "soft": ["communication"]
        },
        "communication": {
            "style": "professional",
            "tone": "neutral"
        }
    }
    '''


@pytest.fixture
def create_test_node(temp_test_dir: Path, sample_persona_json: str):
    """创建测试节点目录结构"""
    def _create(node_id: str = "test-node") -> Path:
        node_dir = temp_test_dir / "nodes" / node_id
        node_dir.mkdir(parents=True)
        persona_file = node_dir / "persona.json"
        persona_file.write_text(sample_persona_json)
        return node_dir
    return _create
