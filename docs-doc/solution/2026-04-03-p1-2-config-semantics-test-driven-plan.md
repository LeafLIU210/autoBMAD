# P1-1/P1-2 配置语义与 Deprecated 接口清理测试驱动方案

**方案日期**: 2026-04-03  
**依据报告**: `docs/research/2026-04-03-p1-2-config-semantics-analysis-report.md`  
**目标模块**: `autoBMAD/docuswarm`  
**技术债编号**: P1-1 (Deprecated 接口清理) + P1-2 (配置语义统一)  
**方案优先级**: P1

---

## 1. 方案概述

本方案针对 **P1-1 Deprecated 接口长期驻留** 和 **P1-2 配置语义混杂** 两大技术债，设计一套完整的测试驱动清理验证体系。与常规迁移方案不同，本方案采用**彻底清理策略**：

- **无兼容层**: 不保留任何兼容性别名或废弃接口
- **即时替换**: 所有调用点同步更新
- **零废弃标记**: 清理后代码中不存在任何 deprecation 警告

### 1.1 核心目标

| 目标 | 说明 |
|------|------|
| **命名统一** | 所有配置读取统一使用 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_BASE_URL` |
| **接口唯一** | 每个功能只有一个接口，`update_pipeline_state()` 替代 `update_pipeline_status()` |
| **别名清除** | 彻底移除 `KimiSessionManager`，统一使用 `SessionManager` |
| **兼容层删除** | 删除 `models` 目录及所有兼容层代码 |
| **无回归风险** | 所有变更必须有测试守护，确保功能零损失 |

### 1.2 清理阶段映射

| 阶段 | 目标文件 | 主要变更 | 测试重点 |
|------|----------|----------|----------|
| Phase A | `models/` 目录 | **删除整个目录** | 零引用验证 |
| Phase A | `pipeline/escalation.py` | 迁移 2 处 `update_pipeline_status()` | 功能等价性 |
| Phase B | `config.py` | 统一使用 `ANTHROPIC_*` | 配置读取验证 |
| Phase B | `session_manager.py` | 移除 `_api_key`、`_base_url` | 字段移除验证 |
| Phase B | `dual_agent.py` | 统一使用 `Config` | 配置链路验证 |
| Phase C | `pipeline/orchestrator.py` | 迁移 11 处调用 | 集成测试 |
| Phase C | `cli/services/pipeline_service.py` | 迁移 2 处调用 | 集成测试 |
| Phase C | `state_manager.py` | **删除 `update_pipeline_status()`** | 接口移除验证 |

---

## 2. 测试目标与范围

### 2.1 测试范围矩阵

| 层级 | 覆盖内容 | 测试类型 |
|------|----------|----------|
| 单元测试 | `Config` 类、环境变量读取、字段存在性 | 隔离测试、Mock 测试 |
| 集成测试 | `Config` → `SessionManager` → `dual_agent` 配置链路 | 端到端契约测试 |
| 迁移测试 | `update_pipeline_status()` → `update_pipeline_state()` 等价性 | 行为验证测试 |
| 回归测试 | 删除兼容层后现有功能不受影响 | 保护性测试 |
| 静态检查 | 确保无残留 `KimiSessionManager`、`update_pipeline_status` 引用 | AST/Grep 检查 |

### 2.2 环境变量映射表（最终状态）

| 配置 | 状态 | 测试验证点 |
|------|------|------------|
| `ANTHROPIC_API_KEY` | ✅ 唯一配置 | 读取、错误提示 |
| `ANTHROPIC_BASE_URL` | ✅ 唯一配置 | 读取、默认值 |
| `ANTHROPIC_MODEL_NAME` | ✅ 统一命名 | 模型选择 |
| `KIMI_API_KEY` | ❌ 移除支持 | 不再读取验证 |
| `KIMI_BASE_URL` | ❌ 移除支持 | 不再读取验证 |
| `CLAUDE_API_KEY` | ❌ 移除支持 | 不再读取验证 |
| `CLAUDE_BASE_URL` | ❌ 移除支持 | 不再读取验证 |

---

## 3. Phase A: 兼容层删除测试方案

### 3.1 `models` 目录删除验证

#### 测试文件
`tests/cleanup/test_models_removed.py`

#### 测试用例设计

```python
def test_models_directory_removed():
    """验证 models 目录已彻底删除"""
    from pathlib import Path
    
    models_dir = Path("autoBMAD/docuswarm/models")
    
    # Assert - 目录不应存在
    assert not models_dir.exists(), f"models 目录应当被删除: {models_dir}"


def test_models_import_fails():
    """验证 models 模块导入失败"""
    with pytest.raises(ImportError):
        from autoBMAD.docuswarm import models


def test_models_toolresult_import_fails():
    """验证 ToolResult 无法从 models 导入"""
    with pytest.raises(ImportError):
        from autoBMAD.docuswarm.models import ToolResult


def test_models_toolregistry_import_fails():
    """验证 ToolRegistry 无法从 models 导入"""
    with pytest.raises(ImportError):
        from autoBMAD.docuswarm.models import ToolRegistry
```

### 3.2 `escalation.py` 迁移测试

#### 测试文件
`tests/unit/docuswarm/pipeline/test_escalation_migration.py`

#### 测试用例设计

```python
@pytest.mark.asyncio
async def test_escalation_uses_update_pipeline_state():
    """验证 escalation.py 使用 update_pipeline_state 而非 update_pipeline_status"""
    # Arrange
    from autoBMAD.docuswarm.pipeline.escalation import EscalationHandler
    
    mock_state_manager = MagicMock()
    mock_state_manager.update_pipeline_state = AsyncMock(return_value=True)
    
    handler = EscalationHandler(state_manager=mock_state_manager)
    
    # Act - 模拟暂停 pipeline
    await handler.pause_pipeline("test-pipeline-id", "test reason")
    
    # Assert - 必须使用新的 async 接口
    mock_state_manager.update_pipeline_state.assert_called_once()
    call_args = mock_state_manager.update_pipeline_state.call_args
    assert call_args[0][0] == "test-pipeline-id"
    assert call_args[1]["state_update"]["status"] == "paused"


def test_no_update_pipeline_status_in_escalation():
    """验证 escalation.py 中不存在 update_pipeline_status 调用"""
    import ast
    from pathlib import Path
    
    escalation_file = Path("autoBMAD/docuswarm/pipeline/escalation.py")
    source = escalation_file.read_text()
    tree = ast.parse(source)
    
    # 搜索所有方法调用
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr != "update_pipeline_status", \
                    f"发现 update_pipeline_status 调用，应当已被替换: {ast.dump(node)}"
```

---

## 4. Phase B: 配置层清理测试方案

### 4.1 `config.py` 清理测试

#### 测试文件
`tests/unit/docuswarm/test_config_cleanup.py`

#### 测试用例设计

```python
def test_config_only_reads_anthropic_api_key():
    """验证 Config 仅读取 ANTHROPIC_API_KEY"""
    # Arrange
    with patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "anthropic-key-123",
        "KIMI_API_KEY": "kimi-key-456",  # 应被忽略
    }, clear=True):
        # Act
        config = Config.from_env_and_yaml()
        
        # Assert
        assert config.api_key == "anthropic-key-123"


def test_config_ignores_kimi_api_key():
    """验证 Config 忽略 KIMI_API_KEY（即使 ANTHROPIC_API_KEY 未设置）"""
    # Arrange
    with patch.dict(os.environ, {
        "KIMI_API_KEY": "kimi-key-only",
    }, clear=True):
        # Act & Assert - 应当抛出错误，而不是使用 KIMI_API_KEY
        with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY is required"):
            Config.from_env_and_yaml()


def test_config_only_reads_anthropic_base_url():
    """验证 Config 仅读取 ANTHROPIC_BASE_URL"""
    # Arrange
    with patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test-key",
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com/v1/",
        "KIMI_BASE_URL": "https://api.kimi.com/coding/",  # 应被忽略
    }, clear=True):
        # Act
        config = Config.from_env_and_yaml()
        
        # Assert
        assert config.base_url == "https://api.anthropic.com/v1/"


def test_config_error_message_only_mentions_anthropic():
    """验证错误消息仅提及 ANTHROPIC_API_KEY"""
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            Config.from_env_and_yaml()
        
        error_msg = str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in error_msg
        assert "KIMI_API_KEY" not in error_msg
        assert "CLAUDE_API_KEY" not in error_msg


def test_config_no_deprecation_warnings():
    """验证 Config 不产生任何 DeprecationWarning"""
    import warnings
    
    with patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test-key",
    }, clear=True):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Config.from_env_and_yaml()
            
            # Assert - 不应有 DeprecationWarning
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 0, f"发现 DeprecationWarning: {deprecation_warnings}"
```

### 4.2 `session_manager.py` 清理测试

#### 测试文件
`tests/unit/docuswarm/llm/test_session_manager_cleanup.py`

#### 测试用例设计

```python
def test_session_manager_no_api_key_field():
    """验证 SessionManager 不存在 _api_key 字段"""
    # Arrange & Act
    sm = SessionManager(work_dir=Path("/tmp"))
    
    # Assert - 字段应被移除
    assert not hasattr(sm, "_api_key"), "_api_key 字段应当被移除"


def test_session_manager_no_base_url_field():
    """验证 SessionManager 不存在 _base_url 字段"""
    # Arrange & Act
    sm = SessionManager(work_dir=Path("/tmp"))
    
    # Assert
    assert not hasattr(sm, "_base_url"), "_base_url 字段应当被移除"


def test_session_manager_no_claude_api_key_read():
    """验证 SessionManager 不读取 CLAUDE_API_KEY 环境变量"""
    # Arrange
    with patch.dict(os.environ, {
        "CLAUDE_API_KEY": "claude-key-should-be-ignored",
    }, clear=True):
        # Act
        sm = SessionManager(work_dir=Path("/tmp"))
        
        # Assert - 不应存储该值
        if hasattr(sm, "_api_key"):
            assert sm._api_key != "claude-key-should-be-ignored"


def test_session_manager_uses_config_for_credentials():
    """验证 SessionManager 从 config 获取凭证"""
    # Arrange
    mock_config = MagicMock()
    mock_config.api_key = "config-api-key"
    mock_config.base_url = "https://config-url.com/"
    
    # Act
    sm = SessionManager(
        work_dir=Path("/tmp"),
        config=mock_config,
    )
    
    # Assert
    assert sm._config == mock_config


def test_kimi_session_manager_removed():
    """验证 KimiSessionManager 别名已移除"""
    # Act & Assert - 应当无法导入
    with pytest.raises(ImportError):
        from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager


def test_session_manager_all_no_kimi_alias():
    """验证 __all__ 中不包含 KimiSessionManager"""
    from autoBMAD.docuswarm.llm import session_manager
    
    assert "KimiSessionManager" not in session_manager.__all__
```

### 4.3 `dual_agent.py` 对齐测试

#### 测试文件
`tests/unit/docuswarm/nodes/test_dual_agent_cleanup.py`

#### 测试用例设计

```python
def test_get_config_uses_from_env_and_yaml():
    """验证 _get_config 使用 Config.from_env_and_yaml()"""
    # Arrange
    from autoBMAD.docuswarm.nodes.dual_agent import _get_config
    
    with patch("autoBMAD.docuswarm.config.Config.from_env_and_yaml") as mock_from_env:
        mock_config = MagicMock()
        mock_from_env.return_value = mock_config
        
        # Act
        result = _get_config()
        
        # Assert
        mock_from_env.assert_called_once()
        assert result == mock_config


def test_dual_agent_node_receives_config():
    """验证 DualAgentNode 接收并使用 Config"""
    # Arrange
    from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
    
    mock_config = MagicMock()
    mock_config.api_key = "test-api-key"
    mock_config.base_url = "https://test.com/"
    
    # Act
    node = DualAgentNode(
        config=mock_config,
        session_manager=MagicMock(),
        node_id="test_node",
    )
    
    # Assert
    assert node.config == mock_config
```

---

## 5. Phase C: 核心接口迁移测试方案

### 5.1 `update_pipeline_status()` → `update_pipeline_state()` 迁移

#### 测试文件
`tests/unit/docuswarm/storage/test_state_manager_migration.py`

#### 测试用例设计

```python
def test_update_pipeline_status_removed():
    """验证 update_pipeline_status 方法已移除"""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    
    sm = StateManager(db_path=":memory:")
    
    # Assert - 方法不应存在
    assert not hasattr(sm, "update_pipeline_status") or not callable(getattr(sm, "update_pipeline_status", None))


@pytest.mark.asyncio
async def test_update_pipeline_state_exists_and_works():
    """验证 update_pipeline_state 存在且正常工作"""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    
    sm = StateManager(db_path=":memory:")
    
    # 先创建一个 pipeline
    sm.create_pipeline("test-pipeline", "Test Pipeline")
    
    # Act
    result = await sm.update_pipeline_state("test-pipeline", {
        "status": "running",
        "current_node": "analyst",
    })
    
    # Assert
    assert result is True
    
    # 验证状态已更新
    pipeline = sm.get_pipeline("test-pipeline")
    assert pipeline["status"] == "running"


@pytest.mark.asyncio
async def test_update_pipeline_state_equivalent_to_old_status_update():
    """验证 update_pipeline_state 与原 update_pipeline_status 行为等价"""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    
    sm = StateManager(db_path=":memory:")
    sm.create_pipeline("test-pipeline", "Test Pipeline")
    
    # Act - 使用新接口模拟原接口的行为
    await sm.update_pipeline_state("test-pipeline", {
        "status": "running",
        "current_node": "analyst",
    })
    
    # Assert - 验证结果与预期一致
    pipeline = sm.get_pipeline("test-pipeline")
    assert pipeline["status"] == "running"
    # state_json 应同步更新
    import json
    state = json.loads(pipeline["state_json"])
    assert state["status"] == "running"
    assert state["current_node"] == "analyst"
```

### 5.2 `orchestrator.py` 迁移测试

#### 测试文件
`tests/integration/test_orchestrator_migration.py`

#### 测试用例设计

```python
def test_orchestrator_no_update_pipeline_status_calls():
    """验证 orchestrator.py 中不存在 update_pipeline_status 调用"""
    import ast
    from pathlib import Path
    
    orchestrator_file = Path("autoBMAD/docuswarm/pipeline/orchestrator.py")
    source = orchestrator_file.read_text()
    tree = ast.parse(source)
    
    # 搜索所有方法调用
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr != "update_pipeline_status", \
                    f"发现 update_pipeline_status 调用: {ast.dump(node)}"


def test_orchestrator_imports_session_manager_not_kimi():
    """验证 orchestrator.py 导入 SessionManager 而非 KimiSessionManager"""
    import ast
    from pathlib import Path
    
    orchestrator_file = Path("autoBMAD/docuswarm/pipeline/orchestrator.py")
    source = orchestrator_file.read_text()
    
    # 验证不包含 KimiSessionManager
    assert "KimiSessionManager" not in source, "orchestrator.py 应移除 KimiSessionManager 引用"


@pytest.mark.asyncio
async def test_orchestrator_uses_update_pipeline_state():
    """验证 orchestrator 使用 update_pipeline_state 更新状态"""
    from autoBMAD.docuswarm.pipeline.orchestrator import PipelineOrchestrator
    
    mock_state_manager = MagicMock()
    mock_state_manager.update_pipeline_state = AsyncMock(return_value=True)
    
    orchestrator = PipelineOrchestrator(
        state_manager=mock_state_manager,
        # ... 其他 mock 依赖
    )
    
    # Act - 执行某个会更新状态的操作
    await orchestrator.start_pipeline("test-pipeline")
    
    # Assert - 验证使用了新接口
    mock_state_manager.update_pipeline_state.assert_called()
```

---

## 6. 静态代码检查方案

### 6.1 残留引用检查脚本

**工具文件**: `tools/cleanup_verification.py`

```python
#!/usr/bin/env python3
"""验证清理是否彻底的脚本"""

import ast
import subprocess
import sys
from pathlib import Path


def check_no_kimi_session_manager():
    """检查是否还有 KimiSessionManager 引用"""
    result = subprocess.run(
        ["grep", "-rn", "KimiSessionManager", "--include=*.py", "autoBMAD/"],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print("ERROR: 发现 KimiSessionManager 残留引用:")
        print(result.stdout)
        return False
    print("✓ KimiSessionManager 无残留")
    return True


def check_no_update_pipeline_status():
    """检查是否还有 update_pipeline_status 调用"""
    result = subprocess.run(
        ["grep", "-rn", "update_pipeline_status", "--include=*.py", "autoBMAD/"],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print("ERROR: 发现 update_pipeline_status 残留调用:")
        print(result.stdout)
        return False
    print("✓ update_pipeline_status 无残留")
    return True


def check_no_kimi_env_vars_in_config():
    """检查 config.py 是否还读取 KIMI_*"""
    config_file = Path("autoBMAD/docuswarm/config.py")
    source = config_file.read_text()
    
    if "KIMI_API_KEY" in source or "KIMI_BASE_URL" in source:
        print("ERROR: config.py 仍包含 KIMI_* 引用")
        return False
    print("✓ config.py 无 KIMI_* 引用")
    return True


def check_no_claude_env_vars_in_session_manager():
    """检查 session_manager.py 是否还读取 CLAUDE_*"""
    sm_file = Path("autoBMAD/docuswarm/llm/session_manager.py")
    source = sm_file.read_text()
    
    if "CLAUDE_API_KEY" in source or "CLAUDE_BASE_URL" in source:
        print("ERROR: session_manager.py 仍包含 CLAUDE_* 引用")
        return False
    print("✓ session_manager.py 无 CLAUDE_* 引用")
    return True


def check_models_directory_removed():
    """检查 models 目录是否已删除"""
    models_dir = Path("autoBMAD/docuswarm/models")
    if models_dir.exists():
        print(f"ERROR: models 目录仍存在: {models_dir}")
        return False
    print("✓ models 目录已删除")
    return True


def main():
    """运行所有检查"""
    checks = [
        check_no_kimi_session_manager,
        check_no_update_pipeline_status,
        check_no_kimi_env_vars_in_config,
        check_no_claude_env_vars_in_session_manager,
        check_models_directory_removed,
    ]
    
    all_passed = all(check() for check in checks)
    
    if all_passed:
        print("\n✅ 所有清理检查通过！")
        return 0
    else:
        print("\n❌ 部分检查未通过，请继续清理")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### 6.2 CI 集成

```yaml
# .github/workflows/cleanup-check.yml
name: Cleanup Verification

on: [push, pull_request]

jobs:
  verify-cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run cleanup verification
        run: python tools/cleanup_verification.py
      
      - name: Run P1-1/P1-2 cleanup tests
        run: |
          pytest tests/cleanup/ -v
          pytest tests/unit/docuswarm/test_config_cleanup.py -v
          pytest tests/unit/docuswarm/llm/test_session_manager_cleanup.py -v
          pytest tests/unit/docuswarm/storage/test_state_manager_migration.py -v
```

---

## 7. 测试文件组织建议

```
tests/
├── cleanup/                          # 清理验证测试
│   ├── test_models_removed.py        # models 目录删除验证
│   └── test_static_checks.py         # 静态代码检查
├── unit/
│   └── docuswarm/
│       ├── test_config_cleanup.py    # P1-2 配置清理
│       ├── storage/
│       │   └── test_state_manager_migration.py  # P1-1 接口迁移
│       ├── llm/
│       │   └── test_session_manager_cleanup.py  # P1-2 会话层清理
│       ├── pipeline/
│       │   └── test_escalation_migration.py     # Phase A 迁移
│       └── nodes/
│           └── test_dual_agent_cleanup.py       # dual_agent 对齐
├── integration/
│   ├── test_config_semantics_end_to_end.py      # 配置链路测试
│   └── test_orchestrator_migration.py           # orchestrator 迁移
└── conftest.py
```

---

## 8. 测试实现计划

### Phase A 测试（立即执行）

1. **T-A1** - models 目录删除验证
2. **T-A2** - escalation.py 迁移验证
3. **T-A3** - 静态检查脚本

### Phase B 测试（Phase A 完成后）

1. **T-B1** - config.py 仅读取 ANTHROPIC_* 验证
2. **T-B2** - session_manager.py 字段移除验证
3. **T-B3** - KimiSessionManager 移除验证
4. **T-B4** - dual_agent.py 对齐验证

### Phase C 测试（Phase B 完成后）

1. **T-C1** - update_pipeline_status 移除验证
2. **T-C2** - update_pipeline_state 功能验证
3. **T-C3** - orchestrator.py 迁移验证
4. **T-C4** - pipeline_service.py 迁移验证

---

## 9. 验收标准

| # | 验收项 | 验收标准 |
|---|--------|----------|
| **P1-1 清理** |||
| A1 | `models` 目录 | 目录已删除，导入抛出 ImportError |
| A2 | `update_pipeline_status()` | 方法已删除，不存在任何调用 |
| A3 | `update_pipeline_state()` | 成为唯一状态更新接口，所有调用已迁移 |
| A4 | `KimiSessionManager` | 别名已移除，所有导入已替换为 `SessionManager` |
| **P1-2 清理** |||
| B1 | `ANTHROPIC_API_KEY` | 唯一配置来源，`KIMI_API_KEY` 不被读取 |
| B2 | `ANTHROPIC_BASE_URL` | 唯一配置来源，`KIMI_BASE_URL` 不被读取 |
| B3 | `_api_key` 字段 | 已从 SessionManager 移除 |
| B4 | `_base_url` 字段 | 已从 SessionManager 移除 |
| B5 | 配置错误提示 | 仅提及 `ANTHROPIC_API_KEY`，不含其他命名 |
| **通用** |||
| C1 | 无 DeprecationWarning | 代码中不存在任何 deprecation 警告 |
| C2 | 测试覆盖率 | 新增测试覆盖率 > 90%，所有清理路径被覆盖 |
| C3 | CI 绿灯 | 清理验证脚本通过，现有测试零回归 |

---

## 10. 测试 Fixtures 与工具

### 10.1 共享 Fixtures

```python
# tests/conftest.py

import pytest
from pathlib import Path
from unittest.mock import MagicMock


@pytest.fixture
def mock_anthropic_env():
    """提供标准的 ANTHROPIC_* 环境变量"""
    return {
        "ANTHROPIC_API_KEY": "test-anthropic-api-key",
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com/v1/",
    }


@pytest.fixture
def temp_work_dir(tmp_path):
    """提供临时工作目录"""
    return tmp_path / "work"


@pytest.fixture
def sample_config():
    """提供标准 Config 实例"""
    from autoBMAD.docuswarm.config import Config
    return Config(
        api_key="test-api-key",
        base_url="https://test.example.com/",
    )


@pytest.fixture
def mock_state_manager():
    """提供已配置 mock 的 StateManager"""
    from unittest.mock import AsyncMock, MagicMock
    
    sm = MagicMock()
    sm.update_pipeline_state = AsyncMock(return_value=True)
    return sm
```

### 10.2 测试工具函数

```python
# tests/utils/cleanup_helpers.py

import ast
import os
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch


@contextmanager
def anthropic_env_only():
    """仅设置 ANTHROPIC_* 环境变量的上下文"""
    env_vars = {
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com/v1/",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        yield


def assert_no_deprecated_calls(file_path: Path, deprecated_names: list[str]):
    """验证文件中不存在废弃接口调用"""
    source = file_path.read_text()
    tree = ast.parse(source)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in deprecated_names, \
                    f"{file_path} 中发现废弃调用: {node.func.attr}"


def count_method_calls(file_path: Path, method_name: str) -> int:
    """统计文件中某方法的调用次数"""
    source = file_path.read_text()
    tree = ast.parse(source)
    
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == method_name:
                    count += 1
    return count
```

---

## 11. 风险与注意事项

### 11.1 实施风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 调用点遗漏 | 中 | 高 | 使用 grep + AST 分析全面扫描 |
| 环境变量未更新 | 高 | 高 | 提供迁移脚本，运行时检查报错 |
| async/sync 不匹配 | 中 | 高 | 仔细处理 `update_pipeline_state` 的 async 语义 |
| 循环导入 | 低 | 中 | 清理后检查导入图 |

### 11.2 测试执行注意事项

1. **环境隔离**: 测试必须使用 `patch.dict(os.environ, ..., clear=True)`
2. **顺序无关**: 各 Phase 测试应独立，不依赖执行顺序
3. **真实文件检查**: 静态检查测试直接读取源文件，不依赖 mock
4. **CI 集成**: 清理验证脚本应作为 CI 门禁

### 11.3 回滚策略

由于采用彻底清理策略（非渐进废弃），回滚需要：
1. 保留 Git 历史
2. 每个 Phase 完成后打 tag
3. 关键变更分小批次提交

---

## 12. 关联文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 深度研究报告 | `docs/research/2026-04-03-p1-2-config-semantics-analysis-report.md` | P1-1/P1-2 深度分析 |
| 技术债审查 | `docs/evaluation/2026-04-03-docuswarm-tech-debt-strategic-review.md` | 原始技术债定义 |
| 清理验证脚本 | `tools/cleanup_verification.py` | 静态检查工具 |

---

**方案作者**: AI Assistant  
**创建日期**: 2026-04-03  
**最后更新**: 2026-04-03  
**版本**: 2.0（含 P1-1 清理方案）
