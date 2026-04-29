# 测试规范详细说明

**版本**: 2.1
**最后更新**: 2026-04-05

---

## 目录

1. [测试框架与实践](#1-测试框架与实践)
2. [测试文件组织](#2-测试文件组织)
3. [测试编写规范](#3-测试编写规范)
4. [测试覆盖要求](#4-测试覆盖要求)
5. [异步测试](#5-异步测试)
6. [测试工具](#6-测试工具)

---

## 1. 测试框架与实践

### 1.1 测试框架

项目统一采用`pytest`作为测试框架。

### 1.2 常用测试命令

- `pytest -v --tb=short`: 标准执行，详细输出
- `pytest -v --tb=short -s`: 同时显示标准输出
- `pytest -v --tb=short -k "test_name"`: 运行匹配特定模式的测试
- `pytest -v --tb=short --maxfail=1`: 首次失败后停止
- `pytest -v --tb=short --cov=<module>`: 生成代码覆盖率报告

---

## 2. 测试文件组织

- 测试文件应放在`tests/`目录下
- 测试文件结构应镜像源代码结构
- 每个模块的测试应独立且可重复执行

### 2.1 目录结构示例

```
tests/
├── __init__.py
├── conftest.py            # pytest全局fixture
├── fixtures/              # 测试固件（TDD关键）
│   ├── __init__.py
│   └── mock_data.py       # 测试模拟数据
├── unit/                  # 单元测试（无UI，快速）
│   ├── test_models.py
│   └── test_services.py
├── integration/           # 集成测试（含DB、文件）
│   └── test_config.py
```

---

## 3. 测试编写规范

### 3.1 AAA模式

遵循AAA模式: Arrange（准备）→ Act（执行）→ Assert（断言）

### 3.2 测试函数命名

测试函数名应清晰描述测试意图，如`test_user_login_with_valid_credentials()`

### 3.3 使用pytest fixture

使用pytest fixture管理测试数据和资源。

### 3.4 示例测试结构

```python
import pytest
from your_module import YourClass

class TestYourClass:
    @pytest.fixture
    def setup_instance(self):
        """准备测试实例"""
        return YourClass()

    def test_basic_functionality(self, setup_instance):
        """测试基本功能"""
        # Arrange（准备）
        instance = setup_instance
        expected_result = "expected"

        # Act（执行）
        actual_result = instance.some_method()

        # Assert（断言）
        assert actual_result == expected_result
```

---

## 4. 测试覆盖要求

- 核心业务逻辑必须有单元测试覆盖
- 关键功能应包含集成测试
- 回归问题必须先编写测试用例，再修复bug

---

## 5. 异步测试

### 5.1 pytest-asyncio

DocuSwarm 使用异步架构，测试中使用 `pytest-asyncio` 进行异步测试。

### 5.2 异步测试示例

```python
import pytest
from unittest.mock import AsyncMock, patch
from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator

class TestPipelineOrchestrator:
    @pytest.fixture
    async def orchestrator(self):
        """创建测试编排器"""
        return HybridOrchestrator(config=test_config)

    @pytest.mark.asyncio
    async def test_pipeline_start(self, orchestrator):
        """测试流水线启动"""
        # Arrange
        context_file = "test-context.md"

        # Act
        result = await orchestrator.start(context_file)

        # Assert
        assert result.status == "running"
```

---

## 6. 测试工具

### 6.1 Fixtest-Workflow

使用Fixtest-Workflow进行测试的自动化扫描、运行和修复。

#### 工作流程
```bash
# 1. 扫描测试文件
cd fixtest-workflow
python scan_test_files.py

# 2. 执行测试
python run_tests.py

# 3. 自动修复
.\fix_tests.ps1

# 4. 验证修复
python run_tests.py
```

### 6.2 代码覆盖率

使用pytest-cov生成代码覆盖率报告：

```bash
pytest --cov=autoBMAD/docuswarm --cov-report=html --cov-report=term
```

---

**参考文档**:
- [质量保证流程](./quality_assurance.md)
- [开发规则与实践](./development_rules.md)

---

**版本历史**:
- v1.0 (2026-01-04): 初始版本，完整的测试规范说明
