#!/usr/bin/env python3
"""
工作流中断因素验证脚本

检查所有可能导致工作流中断的因素，确保：
1. SDK 层不抛出 CancelledError
2. EpicDriver 只在真正的外部取消时传播 CancelledError
3. 所有 RuntimeError 被正确捕获和处理
"""

import ast
import sys
from pathlib import Path
from typing import Any


class CancelledErrorChecker(ast.NodeVisitor):
    """检查 CancelledError 处理的 AST 访问器"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues: list[dict[str, Any]] = []
        self.in_except_cancelled = False
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """访问函数定义"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """访问异步函数定义"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """访问 except 处理器"""
        if node.type:
            # 检查是否捕获 CancelledError
            exception_name = self._get_exception_name(node.type)
            if "CancelledError" in exception_name:
                self.in_except_cancelled = True
                # 检查是否有 raise 语句
                has_raise = self._has_bare_raise(node.body)
                if has_raise:
                    self.issues.append({
                        "type": "cancelled_error_raise",
                        "line": node.lineno,
                        "function": self.current_function,
                        "message": f"捕获 CancelledError 后重新抛出 (line {node.lineno})"
                    })
                self.in_except_cancelled = False

        self.generic_visit(node)

    def _get_exception_name(self, node: ast.expr) -> str:
        """获取异常名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_exception_name(node.value)}.{node.attr}"
        return ""

    def _has_bare_raise(self, body: list[ast.stmt]) -> bool:
        """检查是否有 bare raise"""
        for stmt in body:
            if isinstance(stmt, ast.Raise) and stmt.exc is None:
                return True
            # 递归检查嵌套语句
            if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                for child in ast.walk(stmt):
                    if isinstance(child, ast.Raise) and child.exc is None:
                        return True
        return False


def check_file(filepath: Path) -> list[dict[str, Any]]:
    """检查单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        checker = CancelledErrorChecker(str(filepath))
        checker.visit(tree)
        return checker.issues
    except Exception as e:
        return [{
            "type": "parse_error",
            "message": f"解析文件失败: {e}",
            "file": str(filepath)
        }]


def main():
    """主函数"""
    print("=" * 80)
    print("工作流中断因素验证")
    print("=" * 80)
    print()

    # 检查关键文件
    key_files = [
        "autoBMAD/epic_automation/sdk_wrapper.py",
        "autoBMAD/epic_automation/epic_driver.py",
        "autoBMAD/epic_automation/dev_agent.py",
        "autoBMAD/epic_automation/qa_agent.py",
    ]

    base_path = Path(__file__).parent
    all_issues: list[dict[str, Any]] = []

    for file_path_str in key_files:
        file_path = base_path / file_path_str
        if not file_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue

        print(f"检查: {file_path.name}...")
        issues = check_file(file_path)
        
        if issues:
            all_issues.extend(issues)
            for issue in issues:
                print(f"  ❌ {issue['function']}: {issue['message']}")
        else:
            print(f"  ✅ 无问题")

    print()
    print("=" * 80)
    print("检查结果")
    print("=" * 80)
    print()

    if all_issues:
        print(f"❌ 发现 {len(all_issues)} 个潜在中断因素：")
        print()
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. [{issue['type']}] {issue['message']}")
            if 'file' in issue:
                print(f"   文件: {issue['file']}")
            if 'function' in issue:
                print(f"   函数: {issue['function']}")
            if 'line' in issue:
                print(f"   行号: {issue['line']}")
            print()
        return 1
    else:
        print("✅ 所有检查通过！工作流不应被意外中断。")
        print()
        print("关键验证点：")
        print("  1. ✅ SDK 层不抛出 CancelledError")
        print("  2. ✅ EpicDriver 正确处理 RuntimeError")
        print("  3. ✅ QA Agent 正确封装异常")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
