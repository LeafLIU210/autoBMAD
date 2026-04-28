# 测试驱动迁移快速入门

**目标**: 在 5 分钟内开始 FastMCP → SDK MCP 迁移测试

---

## 1. 环境检查

```bash
# 检查 Python 版本
python --version  # >= 3.10

# 检查 pytest
pytest --version

# 检查 SDK 可用性
python -c "import claude_agent_sdk; print('✓ SDK available')"
```

---

## 2. 快速运行测试

```bash
# 进入测试目录
cd docs/solution

# 运行所有测试
python run_tests.py

# 或运行特定测试类型
python run_tests.py unit           # 单元测试
python run_tests.py integration    # 集成测试
python run_tests.py e2e            # 端到端测试
```

---

## 3. TDD 工作流程

```
第1步: 运行测试 (预期失败)
   python run_tests.py unit
   → 应该看到大量测试失败

第2步: 实现第一个功能
   编辑 implementation/file_tools_sdk.py
   → 实现 create_file_read_server 函数

第3步: 重新运行测试
   python run_tests.py unit
   → 检查哪些测试通过了

第4步: 修复失败的测试
   → 修改代码直到所有单元测试通过

第5步: 重复 2-4 直到完成
```

---

## 4. 测试文件对应关系

| 测试文件 | 实现文件 | 验证内容 |
|---------|---------|---------|
| `test_file_tools_migration.py` | `implementation/file_tools_sdk.py` | 文件读取工具 |
| `test_search_tools_migration.py` | `implementation/search_tools_sdk.py` | 搜索工具 |
| `test_session_manager_integration.py` | `implementation/tool_filter_adapter.py` | 工具过滤器 |

---

## 5. 关键测试验证点

### 必须通过的测试

- ✅ TEST-001: 返回类型是 `dict` (不是 FastMCP 对象)
- ✅ TEST-003: `server['type'] == 'sdk'`
- ✅ TEST-020: `ClaudeSDKClient.connect()` 不抛出 JSON 序列化错误

### 手动验证

```python
# 快速验证脚本
from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
import json

server = create_file_read_server(["/tmp"], "test")

# 验证 1: 是 dict
assert isinstance(server, dict), "Must be dict!"

# 验证 2: 可以 JSON 序列化
try:
    json.dumps(server)
    print("✓ JSON serializable")
except TypeError as e:
    print(f"✗ JSON error: {e}")

# 验证 3: 有正确的键
assert server['type'] == 'sdk'
assert 'name' in server
print("✓ SDK MCP format correct")
```

---

## 6. 故障排查

### 问题: `ModuleNotFoundError`

```bash
# 解决方案: 从项目根目录运行
cd D:/GITHUB/DocuSwarm
python -m pytest docs/solution/test-suite/ -v
```

### 问题: SDK 不可用

```bash
# 检查 SDK 安装
pip list | findstr claude

# 安装 SDK (如果需要)
pip install claude-agent-sdk
```

### 问题: 测试全部失败

```bash
# 检查实现文件是否存在
ls docs/solution/implementation/

# 预期: 开始时测试应该失败 (TDD 红阶段)
# 随着实现推进，测试应该逐渐通过 (TDD 绿阶段)
```

---

## 7. 下一步

1. 阅读完整方案: `test-driven-sdk-mcp-migration-plan.md`
2. 完成验证清单: `verification/migration_checklist.md`
3. 开始实现代码: `implementation/` 目录

---

**预计时间**: 
- 阅读文档: 15 分钟
- 运行测试: 2 分钟
- 完整迁移: 1-2 天
