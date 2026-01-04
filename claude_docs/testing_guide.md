# 测试规范详细说明

**版本**: 1.0
**最后更新**: 2026-01-04

---

## 目录

1. [测试框架与实践](#1-测试框架与实践)
2. [测试文件组织](#2-测试文件组织)
3. [测试编写规范](#3-测试编写规范)
4. [测试覆盖要求](#4-测试覆盖要求)
5. [GUI测试](#5-gui测试)
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
│   └── mock_qt_objects.py # Mock的Qt组件
├── unit/                  # 单元测试（无UI，快速）
│   ├── test_models.py
│   └── test_services.py
├── integration/           # 集成测试（含DB、文件）
│   └── test_config.py
└── gui/                   # GUI测试（用pytest-qt）
    ├── __init__.py
    └── test_main_window.py
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

## 5. GUI测试

### 5.1 pytest-qt插件

为GUI组件测试使用`pytest-qt`插件。

### 5.2 GUI测试示例

```python
import pytest
from pytestqt.qtbot import QtBot
from my_qt_app.ui.main_window import MainWindow

class TestMainWindow:
    @pytest.fixture
    def main_window(self, qtbot):
        """创建主窗口"""
        window = MainWindow()
        qtbot.addWidget(window)
        return window

    def test_button_click(self, qtbot, main_window):
        """测试按钮点击"""
        # 点击按钮
        qtbot.mouseClick(main_window.pushButton, Qt.LeftButton)

        # 验证结果
        assert main_window.label.text() == "Button clicked"
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
pytest --cov=src --cov-report=html --cov-report=term
```

---

**参考文档**:
- [质量保证流程](./quality_assurance.md)
- [开发规则与实践](./development_rules.md)

---

**版本历史**:
- v1.0 (2026-01-04): 初始版本，完整的测试规范说明
