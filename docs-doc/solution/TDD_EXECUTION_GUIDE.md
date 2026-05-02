# TDD 执行指南 (Quick Reference)

测试驱动开发的快速执行参考。

## 红/绿/重构循环

```
红: 编写测试 -> 运行失败
绿: 编写代码 -> 测试通过
重构: 优化代码 -> 保持通过
```

## Phase A 执行流程

### P0-1: start_pipeline() asyncio.run 修复

```bash
# 1. 红: 运行新测试 (失败)
pytest tests/architecture/test_p0_1_asyncio_run_regression.py -v

# 2. 绿: 修复代码
# 编辑 autoBMAD/docuswarm/pipeline/orchestrator.py
# Line 328: asyncio.run(...) -> await ...
# Line 391: asyncio.run(...) -> await ...

# 3. 验证通过
pytest tests/architecture/test_p0_1_asyncio_run_regression.py -v

# 4. 回归测试
pytest tests/architecture/ -v
```

### P0-2: _run_async Bridge 移除

```bash
# 1. 红: 运行架构测试 (失败)
pytest tests/architecture/test_p0_3_async_sync_contract.py::test_no_run_async_bridge_anywhere -v

# 2. 绿: 修复代码
# 编辑 autoBMAD/docuswarm/cli/services/pipeline_service.py
# - 删除 _run_async() 函数 (Line 20-39)
# - cancel() 改为 async def
# - cancel_all() 改为 async def
# - 内部调用改为 await

# 3. 更新调用点
# 编辑 CLI 命令文件
# asyncio.run(service.cancel(pipeline_id))

# 4. 验证通过
pytest tests/architecture/test_p0_3_async_sync_contract.py::test_no_run_async_bridge_anywhere -v
pytest tests/smoke/test_cancel_pipeline.py::TestCancelAsyncContract -v
```

### P1-1: escalate() await 修复

```bash
# 1. 红: 运行测试 (失败)
pytest tests/architecture/test_p1_1_escalation_await_regression.py -v

# 2. 绿: 修复代码
# 编辑 autoBMAD/docuswarm/nodes/dual_agent.py
# Line 807: escalate(...) -> await escalate(...)
# Line 845: escalate(...) -> await escalate(...)

# 3. 验证通过
pytest tests/architecture/test_p1_1_escalation_await_regression.py -v
pytest tests/smoke/test_escalation.py -v
```

### P1-3: 测试环境修复

```bash
# 1. 配置已更新 (pyproject.toml)
# addopts 中已添加 --basetemp=.pytest-temp

# 2. 运行环境测试
pytest tests/architecture/test_environment_setup.py -v

# 3. 清理残留临时目录 (Windows)
rmdir /s /q %TEMP%\pytest-of-*

# 4. 全量测试
pytest tests/ -v --ignore=tests/e2e/
```

## Phase B 执行流程

### P1-2: 文档一致性

```bash
# 1. 红: 运行文档测试 (失败)
pytest tests/architecture/test_documentation_consistency.py -v

# 2. 绿: 更新文档
# 编辑 autoBMAD/docuswarm/README.md
# 编辑 autoBMAD/docuswarm/CONFIGURATION.md
# - KIMI_API_KEY -> ANTHROPIC_API_KEY
# - KIMI_BASE_URL -> ANTHROPIC_BASE_URL
# - KimiSessionManager -> SessionManager

# 3. 验证通过
pytest tests/architecture/test_documentation_consistency.py -v
```

### P1-3: 冒烟测试补充

```bash
# 1. 测试文件已创建在 tests/smoke/
# - test_start_pipeline.py
# - test_resume_pipeline.py
# - test_cancel_pipeline.py
# - test_escalation.py

# 2. 运行冒烟测试
pytest tests/smoke/ -v

# 3. 覆盖率检查
pytest --cov=autoBMAD.docuswarm tests/smoke/ --cov-report=term-missing
```

## 每日验证命令

```bash
# 快速验证 (1分钟)
python scripts/verify_phase_a_fixes.py

# 完整验证 (5分钟)
pytest tests/architecture/ tests/smoke/ -v --tb=short

# 覆盖率报告
pytest --cov=autoBMAD.docuswarm tests/ --cov-report=term-missing
```

## 修复代码片段

### P0-1 修复

```python
# orchestrator.py Line 326-333
# 修复前:
import asyncio
_ = asyncio.run(
    self._state_manager.update_pipeline_state(...)
)

# 修复后:
_ = await self._state_manager.update_pipeline_state(...)
```

### P0-2 修复

```python
# pipeline_service.py
# 删除:
def _run_async(coro): ...

# 修改签名:
async def cancel(self, pipeline_id: str) -> bool:
    ...
    return await self._state_manager.update_pipeline_state(...)

async def cancel_all(self, status: str | None = None) -> tuple[...]:
    ...
    await self._state_manager.update_pipeline_state(...)
```

### P1-1 修复

```python
# dual_agent.py Line 807
# 修复前:
if self.escalation_handler:
    self.escalation_handler.escalate(...)

# 修复后:
if self.escalation_handler:
    await self.escalation_handler.escalate(...)
```

## 故障排除

### 测试失败排查

```bash
# 查看详细输出
pytest <test_file> -v --tb=long

# 只运行特定测试
pytest <test_file>::<test_class>::<test_method> -v

# 使用 pdb 调试
pytest <test_file> --pdb
```

### 覆盖率不足

```bash
# 查看未覆盖行
pytest --cov=autoBMAD.docuswarm <test_file> --cov-report=term-missing

# 生成 HTML 报告
pytest --cov=autoBMAD.docuswarm <test_file> --cov-report=html
# 打开 htmlcov/index.html
```

## 时间预算

| 任务 | 预计时间 | 实际时间 |
|------|----------|----------|
| P0-1 修复 | 4 小时 | ___ |
| P0-2 修复 | 4 小时 | ___ |
| P1-1 修复 | 2 小时 | ___ |
| P1-3 修复 | 2 小时 | ___ |
| P1-2 修复 | 2 小时 | ___ |
| P1-3 冒烟测试 | 12 小时 | ___ |
| **总计** | **26 小时** | ___ |
