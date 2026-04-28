# TDD SDK 迁移快速参考

**完整文档**: [TDD-SDK-Migration-2026-03-25.md](./TDD-SDK-Migration-2026-03-25.md)  
**实施指南**: [TDD-SDK-Migration-Implementation-Guide.md](./TDD-SDK-Migration-Implementation-Guide.md)

---

## 迁移地图

```
文件状态: [PENDING] → [IN_PROGRESS] → [TEST_PASS] → [DONE]

llm/session_manager.py          [PENDING]  ← 关键阻塞
├── tests/llm/test_session_manager_tdd.py
│   ├── TestSessionManagerImports
│   ├── TestSessionManagerInitialization
│   ├── TestSessionManagerSinglePrompt
│   ├── TestSessionManagerLifecycle
│   └── TestSessionManagerErrors

llm/approval.py                  [PENDING]
├── tests/llm/test_approval_tdd.py

pipeline/orchestrator.py         [PENDING]
├── tests/pipeline/test_orchestrator_tdd.py

tools/sdk_adapter.py             [PENDING]
├── tests/tools/test_sdk_adapter_tdd.py

tools/callable_tool_wrapper.py   [PENDING]
├── tests/tools/test_callable_tool_wrapper_tdd.py

agents/independent.py            [PENDING]
├── tests/agents/test_independent_agent_tdd.py

agents/evaluator.py              [PENDING]
├── tests/agents/test_evaluator_agent_tdd.py
```

---

## 每日命令

```bash
# 开始工作 - 检查进度
python tools/dependency_analysis/migration_tracker.py

# 运行当前阶段的测试
pytest tests/llm/test_session_manager_tdd.py -v

# 提交前 - 全量测试
pytest tests/ -v --tb=short -x

# 验证漂移已修复
python tools/dependency_analysis/migration_tracker.py --check
```

---

## 导入替换表

| 旧导入 (kimi) | 新导入 (claude) | 备注 |
|--------------|----------------|------|
| `from kaos.path import KaosPath` | `from pathlib import Path` | 标准库替代 |
| `from kimi_agent_sdk import Message` | 移除 | 使用 `dict[str, Any]` |
| `from kimi_agent_sdk import Session` | `from claude_agent_sdk import query` | 函数式API |
| `from kimi_agent_sdk import Config` | 移除 | 使用 `dict[str, Any]` |
| `from kimi_agent_sdk import ResultMessage` | `from claude_agent_sdk import ResultMessage` | 直接替换 |
| `from kimi_agent_sdk import ToolOk, ToolError` | 移除 | 使用 `dict` |
| `from kimi_agent_sdk import CallableTool2` | 移除 | 使用纯函数 |
| `from kimi_agent_sdk._aggregator import MessageAggregator` | 移除 | 自行实现或简化 |

---

## 类型替换表

| 旧类型 | 新类型 | 示例 |
|--------|--------|------|
| `KaosPath` | `pathlib.Path` | `work_dir: Path` |
| `list[Message]` | `list[dict[str, Any]]` | `return [{"role": "assistant", "content": []}]` |
| `ToolReturnValue` | `dict[str, Any]` | `return {"type": "tool_result", "content": {}}` |
| `Session` | 移除 | 使用 `query()` 函数 |
| `Config` | `dict[str, Any]` | `config: dict[str, Any]` |

---

## 测试模板

```python
# 标准测试结构
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

class TestNewFeature:
    """Tests for X migration."""
    
    def test_no_kimi_imports(self) -> None:
        """RED: Verify no kimi imports."""
        import module
        source = Path(module.__file__).read_text()
        assert "kimi_agent_sdk" not in source
    
    @pytest.mark.asyncio
    async def test_new_behavior(self) -> None:
        """RED: Test new behavior."""
        # Arrange
        # Act
        # Assert
        pass
```

---

## 常见错误与解决

| 错误 | 原因 | 解决 |
|------|------|------|
| `ImportError: kimi_agent_sdk` | 未完全移除导入 | 检查文件头部导入 |
| `TypeError: 'KaosPath' object...` | 类型不匹配 | 替换为 `pathlib.Path` |
| `AttributeError: 'dict' has no...` | 仍按 Message 对象访问 | 改为 dict 访问方式 |
| `NameError: 'Message' is not...` | 类型别名未定义 | 移除或替换为 dict |

---

## 参考实现

```python
# 参考: autoBMAD/epic_automation/sdk_wrapper.py

from claude_agent_sdk import ResultMessage, query

async def execute_with_claude(prompt: str, options: dict) -> bool:
    """正确使用 claude-agent-sdk 的示例."""
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                return not message.is_error
        return True
    except Exception:
        return False
```

---

## 检查清单

### 每个文件完成后
- [ ] TDD 测试全部通过
- [ ] 运行 `migration_tracker.py` 检查进度
- [ ] 无 `kimi_agent_sdk` 字符串残留
- [ ] 提交代码

### 每日结束时
- [ ] 所有测试通过
- [ ] 推送分支
- [ ] 更新进度

---

## 支持

- **问题**: 查阅 [TDD-SDK-Migration-Implementation-Guide.md](./TDD-SDK-Migration-Implementation-Guide.md)
- **研究**: 查阅 [dependency-drift-2026-03-25](../research/dependency-drift-2026-03-25/)
- **工具**: `tools/dependency_analysis/`
