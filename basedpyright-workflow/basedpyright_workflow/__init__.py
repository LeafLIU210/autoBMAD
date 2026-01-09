"""BasedPyright - 代码质量检查、报告和修复工作流工具.

一个通用的 Python 类型检查工具，提供：
- 基于 basedpyright 的类型检查
- Markdown 和 HTML 报告生成
- 错误提取用于自动化修复
- 与 Claude Code 集成
"""

__version__ = "1.0.0"
__author__ = "BasedPyright Tool"
__description__ = "代码质量检查、报告和修复工作流工具"

# Import main workflow functions
from . import basedpyright_workflow as _basedpyright_workflow_module
from . import ruff_workflow as _ruff_workflow_module

# Export the main workflow functions
run_basedpyright_check = _basedpyright_workflow_module.run_basedpyright_check
run_ruff_check = _ruff_workflow_module.run_ruff_check

__all__ = [
    "run_basedpyright_check",
    "run_ruff_check",
]
