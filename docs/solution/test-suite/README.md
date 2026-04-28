# Session 执行失败修复 - 测试套件

本目录包含针对 DocuSwarm Session 执行失败问题的测试驱动修复方案的测试文件。

## 测试文件说明

| 文件 | 说明 | 对应修复 |
|------|------|----------|
| `test_fix3_model_removal.py` | 验证 ANTHROPIC_MODEL_NAME 移除 | Fix-3 |
| `test_fix1_prompt_method.py` | 验证 prompt() 方法 API 修复 | Fix-1 |
| `test_fix2_await_removal.py` | 验证 await 移除 | Fix-2 |
| `conftest.py` | 共享夹具和配置 | - |

## 快速开始

### 运行所有测试

```bash
cd docs/solution/test-suite
python run_tests.py
```

### 运行单个测试文件

```bash
# Fix-3 测试
pytest test_fix3_model_removal.py -v

# Fix-1 测试
pytest test_fix1_prompt_method.py -v

# Fix-2 测试
pytest test_fix2_await_removal.py -v
```

### 运行特定测试用例

```bash
# 运行特定测试类
pytest test_fix3_model_removal.py::TestCreateOptionsModelRemoval -v

# 运行特定测试方法
pytest test_fix1_prompt_method.py::TestPromptMethodAPI::test_prompt_calls_query_not_send_message -v
```

## 测试覆盖范围

### Fix-3: Model 移除测试 (TEST-F3-001 ~ TEST-F3-009)

- ✅ `_create_options()` 返回 `model=None`
- ✅ 忽略 `ANTHROPIC_MODEL_NAME` 环境变量
- ✅ 忽略 `config.model` 属性
- ✅ `permission_mode` 正确设置
- ✅ `cwd` 字段正确设置
- ✅ `agent_file` 正确传递
- ✅ `thinking` 模式正确设置

### Fix-1: Prompt 方法修复测试 (TEST-F1-001 ~ TEST-F1-007)

- ✅ 使用 `query()` 而非 `send_message()`
- ✅ 使用 `receive_messages()` 而非 `messages()`
- ✅ 正确 yield 所有消息
- ✅ `prompt()` 是 async generator
- ✅ 正确处理空消息
- ✅ 正确处理大消息

### Fix-2: Await 移除测试 (TEST-F2-001 ~ TEST-F2-006)

- ✅ 源代码中无 `await session.prompt()`
- ✅ 使用 `async for session.prompt()` 模式
- ✅ 正确处理 async generator
- ✅ 不抛出 `TypeError: async_generator can't be used in 'await'`
- ✅ dict 消息正确收集
- ✅ 对象消息正确转换

## 测试执行顺序

建议按以下顺序执行测试：

1. **Fix-3 优先** (test_fix3_model_removal.py)
   - 这是基础配置变更
   
2. **Fix-1 次之** (test_fix1_prompt_method.py)
   - 核心 SDK 交互修复
   
3. **Fix-2 最后** (test_fix2_await_removal.py)
   - 调用模式修正

## 故障排查

### 导入错误

确保在项目根目录运行测试：

```bash
cd D:\GITHUB\DocuSwarm
pytest docs/solution/test-suite/test_fix3_model_removal.py -v
```

### 缺少依赖

确保已安装测试依赖：

```bash
pip install pytest pytest-asyncio
```

### Mock 相关问题

如果测试因为 mock 对象的问题失败，检查：

1. `AsyncMock` 是否正确使用
2. 异步生成器模拟是否正确
3. 路径设置是否正确

## 参考文档

- 测试方案文档: `docs/solution/2026-04-05-session-execution-failure-tdd-plan.md`
- 修复方案文档: `docs/research/session-execution-failure-solution.md`
- 原始分析报告: `docs/research/session-execution-failure-analysis.md`
