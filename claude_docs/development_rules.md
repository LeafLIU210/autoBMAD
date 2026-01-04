# 开发规则与实践详细说明

**版本**: 1.0
**最后更新**: 2026-01-04

---

## 目录

1. [编码规范](#1-编码规范)
2. [代码风格](#2-代码风格)
3. [代码质量检查规则](#3-代码质量检查规则)
4. [自动化测试修复](#4-自动化测试修复)

---

## 1. 编码规范

### 1.1 Python模块导入规范

#### 核心要求

1. **使用绝对导入**: 禁止使用相对导入
2. **导入路径不包含源代码目录名**: 从源代码目录的内容开始

```python
# ❌ 错误示例（包含源代码目录名或使用相对导入）
from Project_recorder.services.config_service import ConfigService
from ..services.config_service import ConfigService

# ✅ 正确示例（绝对导入）
from services.config_service import ConfigService
from ui.widgets.button import CustomButton
```

#### 导入顺序规范

```python
# 1. 标准库导入
import os
import sys
from pathlib import Path

# 2. 第三方库导入
from PySide6.QtWidgets import QWidget
import pytest

# 3. 本地应用/库导入（使用绝对导入）
from services.config_service import ConfigService
from ui.widgets.button import CustomButton
from core.recorder import Recorder
```

### 1.2 字符编码要求

1. **禁止使用Unicode编码**: 代码中不要创建或使用Unicode转义序列
2. **字符编码统一**: 所有Python源文件使用UTF-8编码
3. **可读性优先**: 字符串常量、注释、文档字符串使用人类可读的文本

```python
# ❌ 反面例子
message = "\u6b22\u8fce"  # Unicode编码的"欢迎"

# ✅ 正面例子
message = "欢迎"  # 直接使用中文字符
```

---

## 2. 代码风格

### 2.1 核心原则

- **函数/方法化**: 任何重复逻辑必须提取为函数或方法
- **清晰命名**: 变量和函数名必须清晰表达其意图
- **避免过度设计**: 不要创建深不见底的继承层次
- **减少嵌套**: 使用提前返回扁平化代码结构

### 2.2 命名规范

#### 变量命名
```python
# ✅ 好的命名
user_count = 10
is_active = True
max_retry_attempts = 3

# ❌ 差的命名
data = 10
flag = True
x = 3
```

#### 函数命名
```python
# ✅ 动词开头的清晰命名
def calculate_total_price(items):
    """计算商品总价"""
    pass

def validate_user_input(input_data):
    """验证用户输入"""
    pass

# ❌ 模糊的命名
def process(data):
    """处理数据"""
    pass
```

#### 类命名
```python
# ✅ PascalCase命名
class UserAccountManager:
    pass

class DatabaseConnection:
    pass

# ❌ 随意的命名
class manager:
    pass

class db:
    pass
```

---

## 3. 代码质量检查规则

### 3.1 基于pyright的类型检查

#### 类型检查要求

1. **类型注解**:
   - 所有公共函数和方法必须有返回类型注解
   - 函数参数建议添加类型注解
   - 类属性建议添加类型注解

```python
# ✅ 正确示例
def calculate_area(radius: float) -> float:
    """计算圆的面积"""
    return 3.14 * radius * radius

class UserService:
    def __init__(self, config: ConfigService) -> None:


    def get self.config = config_user(self, user_id: int) -> User:
        """获取用户信息"""
        return self._repository.get_by_id(user_id)
```

2. **配置文件**:
   - 项目根目录创建 `.bpr.json` 配置文件
   - 定义检查范围和规则

```json
{
    "include": ["src/**/*"],
    "exclude": ["tests/**/*", "build/**/*"],
    "report": {
        "enable": true,
        "format": "json"
    }
}
```

3. **检查执行**:
```bash
# 运行类型检查
cd basedpyright-workflow
basedpyright-workflow check

# 生成详细报告
basedpyright-workflow report

# 完整工作流
basedpyright-workflow workflow
```

### 3.2 Ruff代码风格检查

#### Ruff配置 (pyproject.toml)

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
```

#### 执行命令
```bash
# 检查代码风格
ruff check src/

# 自动修复可修复的问题
ruff check --fix src/

# 格式化代码
ruff format src/
```

### 3.3 智能冲突解决

BasedPyright-Workflow 提供智能冲突解决机制：

1. **优先级策略**:
   - 类型错误 (Type Error) > 代码风格 (Style)
   - 逻辑错误 (Logic Error) > 格式错误 (Format)
   - 安全问题 (Security) > 性能问题 (Performance)

2. **自动化决策**:
   - 优先修复类型错误
   - 然后处理代码风格问题
   - 避免重复修复

3. **手动干预**:
```powershell
# 使用PowerShell脚本进行自动修复
cd basedpyright-workflow
.\fix_unified_errors_new.ps1
```

### 3.4 集成到开发流程

#### 预提交检查
```bash
#!/bin/bash
# pre-commit.sh
echo "运行类型检查..."
basedpyright-workflow check

echo "检查代码风格..."
ruff check --fix src/

echo "运行测试..."
pytest tests/
```

#### CI/CD集成
```yaml
# .github/workflows/quality-check.yml
- name: Run BasedPyright
  run: |
    cd basedpyright-workflow
    basedpyright-workflow check

- name: Run Ruff
  run: |
    ruff check src/
    ruff format --check src/
```

---

## 4. 自动化测试修复

### 4.1 Fixtest-Workflow集成

项目使用 **Fixtest-Workflow** 工具进行测试的自动化扫描、运行和修复。

#### 测试修复流程

1. **发现测试文件**:
```bash
cd fixtest-workflow
python scan_test_files.py
# 生成 fileslist/test_files_list_20260104_143022.json
```

2. **执行测试**:
```bash
# 完整测试套件
python run_tests.py

# 快速演示 (仅3个文件)
python demo_run_tests.py
# 生成 summaries/test_results_summary_*.json
```

3. **自动修复**:
```powershell
# PowerShell脚本自动修复
.\fix_tests.ps1

# 观察Claude修复过程
# 循环直到所有错误解决
```

4. **验证修复**:
```bash
# 重新运行测试验证
python run_tests.py
```

### 4.2 测试质量要求

1. **测试文件组织**:
   - 测试文件命名: `test_*.py`
   - 测试函数命名: `test_*`
   - 避免测试文件过大 (>1500行)

2. **超时保护**:
   - 单个测试超时: 120秒
   - 避免测试挂起
   - 使用pytest-timeout插件

3. **错误处理**:
   - 区分ERROR、FAIL、TIMEOUT
   - 优先修复ERROR级别问题
   - 记录详细错误信息

### 4.3 最佳实践

**开发阶段**:
- 开发新功能时同步编写测试
- 遇到测试失败立即修复
- 使用演示模式快速验证

**调试阶段**:
- 使用Fixtest-Workflow扫描问题
- 通过Claude自动修复
- 手动审查修复结果

**CI/CD阶段**:
- 在CI流程中运行测试检查
- 仅在测试失败时触发修复
- 保留测试结果日志

---

**参考文档**:
- [核心原则](./core_principles.md)
- [测试指南](./testing_guide.md)
- [技术规范](./technical_specs.md)

---

**版本历史**:
- v1.0 (2026-01-04): 初始版本，完整的开发规则与实践说明
