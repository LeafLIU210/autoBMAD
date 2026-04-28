#!/usr/bin/env python3
"""
Finding 5 深度调试工具: 依赖、命名与文档漂移分析

问题: 依赖、命名与文档发生长期漂移，运行时真实语义不再清晰

研究目标:
1. 检查未声明的依赖（如 kaos.path）
2. 分析命名不一致（KimiSessionManager vs SessionManager）
3. 检查 deprecated/legacy/兼容代码
4. 提出收敛方案
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class DependencyDriftDebugger:
    """依赖漂移调试器."""

    # 已知的问题依赖
    DEPRECATED_MODULES = [
        "kaos.path",
        "kimi_agent_sdk",
        "kimi_agent_sdk._aggregator",
    ]

    # 命名不一致的模式
    NAMING_ISSUES = [
        ("KimiSessionManager", "SessionManager"),
        ("kimi_session_manager", "session_manager"),
    ]

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.findings: list[dict[str, Any]] = []

    def scan_imports(self) -> dict[str, Any]:
        """扫描项目中的导入."""
        print("=" * 70)
        print("FINDING 5: 依赖、命名与文档漂移分析")
        print("=" * 70)

        print("\n[1] 问题依赖扫描:")

        deprecated_imports: dict[str, list[str]] = {mod: [] for mod in self.DEPRECATED_MODULES}

        # 扫描 Python 文件
        py_files = list(self.project_root.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f) and ".venv" not in str(f)]

        for py_file in py_files:
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            for deprecated in self.DEPRECATED_MODULES:
                                if deprecated in alias.name:
                                    rel_path = py_file.relative_to(self.project_root)
                                    deprecated_imports[deprecated].append(str(rel_path))

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for deprecated in self.DEPRECATED_MODULES:
                                if deprecated in node.module:
                                    rel_path = py_file.relative_to(self.project_root)
                                    deprecated_imports[deprecated].append(str(rel_path))

            except SyntaxError:
                continue
            except Exception:
                continue

        # 打印结果
        total_issues = 0
        for mod, files in deprecated_imports.items():
            unique_files = list(set(files))
            if unique_files:
                total_issues += len(unique_files)
                print(f"\n    {mod}:")
                for f in unique_files:
                    print(f"      - {f}")

        return {
            "deprecated_imports": deprecated_imports,
            "total_issue_files": total_issues,
        }

    def check_pyproject_dependencies(self) -> dict[str, Any]:
        """检查 pyproject.toml 依赖声明."""
        print("\n[2] 依赖声明检查:")

        pyproject_path = self.project_root / "pyproject.toml"
        pyproject_content = pyproject_path.read_text(encoding="utf-8")

        findings = {
            "has_kaos_path": "kaos.path" in pyproject_content,
            "has_kimi_agent_sdk": "kimi-agent-sdk" in pyproject_content,
            "has_claude_agent_sdk": "claude-agent-sdk" in pyproject_content,
        }

        print(f"    pyproject.toml 依赖声明:")
        print(f"      kaos.path: {'声明' if findings['has_kaos_path'] else '未声明'}")
        print(f"      kimi-agent-sdk: {'声明' if findings['has_kimi_agent_sdk'] else '未声明'}")
        print(f"      claude-agent-sdk: {'声明' if findings['has_claude_agent_sdk'] else '未声明'}")

        # 检查实际导入但未声明的依赖
        undeclared = []
        if not findings["has_kaos_path"]:
            undeclared.append("kaos.path")
        if not findings["has_kimi_agent_sdk"]:
            undeclared.append("kimi-agent-sdk")

        if undeclared:
            print(f"\n    ⚠️  发现未声明的依赖: {', '.join(undeclared)}")

        findings["undeclared_dependencies"] = undeclared
        return findings

    def analyze_naming_consistency(self) -> dict[str, Any]:
        """分析命名一致性."""
        print("\n[3] 命名一致性检查:")

        findings = {}

        # 检查 KimiSessionManager 别名
        session_manager_path = self.project_root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
        if session_manager_path.exists():
            source = session_manager_path.read_text()

            # 查找别名定义
            alias_pattern = r"(\w+)\s*=\s*SessionManager"
            matches = re.findall(alias_pattern, source)

            if matches:
                print(f"    发现 SessionManager 别名:")
                for alias in matches:
                    print(f"      - {alias} = SessionManager")
                    if alias != "SessionManager":
                        findings["deprecated_alias"] = alias
                        print(f"        ⚠️  建议移除别名 {alias}")

        # 检查代码中使用 KimiSessionManager 的地方
        kim_usage = []
        py_files = list(self.project_root.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]

        for py_file in py_files:
            try:
                source = py_file.read_text(encoding="utf-8")
                if "KimiSessionManager" in source:
                    rel_path = py_file.relative_to(self.project_root)
                    kim_usage.append(str(rel_path))
            except:
                continue

        if kim_usage:
            print(f"\n    使用 KimiSessionManager 的文件:")
            for f in set(kim_usage):
                print(f"      - {f}")

        findings["kimi_session_manager_usage"] = list(set(kim_usage))
        return findings

    def scan_deprecated_patterns(self) -> dict[str, Any]:
        """扫描 deprecated/legacy/兼容代码."""
        print("\n[4] Deprecated/Legacy 代码扫描:")

        patterns = {
            "deprecated": r"deprecated",
            "legacy": r"legacy",
            "backward_compatibility": r"backward.?compatibility",
            "compatibility": r"compatibility",
            "todo_remove": r"TODO.*remove",
        }

        findings = {k: [] for k in patterns}

        py_files = list(self.project_root.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f) and "test" not in str(f).lower()]

        for py_file in py_files:
            try:
                source = py_file.read_text(encoding="utf-8")
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, source, re.IGNORECASE)
                    if matches:
                        rel_path = py_file.relative_to(self.project_root)
                        findings[pattern_name].append(str(rel_path))
            except:
                continue

        # 打印结果
        for pattern_name, files in findings.items():
            unique_files = list(set(files))
            if unique_files:
                print(f"\n    {pattern_name} ({len(unique_files)} 个文件):")
                for f in unique_files[:5]:  # 只显示前5个
                    print(f"      - {f}")
                if len(unique_files) > 5:
                    print(f"      ... 还有 {len(unique_files) - 5} 个文件")

        return findings

    def check_document_alignment(self) -> dict[str, Any]:
        """检查文档一致性."""
        print("\n[5] 文档一致性检查:")

        # 检查 PRD 文档
        prd_path = self.project_root / "docs" / "PRD.md"
        findings = {}

        if prd_path.exists():
            prd_content = prd_path.read_text()

            # 检查宣称的依赖
            if "kimi-agent-sdk" in prd_content.lower():
                findings["prd_claims_no_kimi"] = "完全移除" in prd_content
                print(f"    PRD.md 宣称完全移除 kimi-agent-sdk: {findings['prd_claims_no_kimi']}")

        # 检查 README
        readme_path = self.project_root / "autoBMAD" / "docuswarm" / "README.md"
        if readme_path.exists():
            readme_content = readme_path.read_text(encoding="utf-8")
            if "Kimi" in readme_content:
                findings["readme_mentions_kimi"] = True
                print(f"    ⚠️  README.md 仍包含 Kimi 相关命名")

        return findings

    def generate_solution(self) -> dict[str, Any]:
        """生成解决方案."""
        print("\n" + "=" * 70)
        print("解决方案建议 (基于移除 deprecated 和统一命名)")
        print("=" * 70)

        solutions = {
            "preferred": {
                "title": "方案: 依赖清理和命名统一",
                "description": "移除所有未声明依赖和 deprecated 代码，统一命名",
                "steps": [
                    "1. 移除 kaos.path 依赖:",
                    "   - 替换 from kaos.path import KaosPath 为 from pathlib import Path",
                    "   - 验证所有使用 KaosPath 的地方兼容 Path",
                    "",
                    "2. 移除 kimi-agent-sdk 残留:",
                    "   - 删除所有 kimi_agent_sdk 导入",
                    "   - 删除所有 KimiSessionManager 别名",
                    "   - 统一使用 SessionManager",
                    "",
                    "3. 清理 deprecated/legacy 代码:",
                    "   - 删除标记为 deprecated 的函数和类",
                    "   - 删除 backward compatibility 层",
                    "   - 删除 TODO remove 的代码",
                    "",
                    "4. 更新依赖声明:",
                    "   - 确保 pyproject.toml 声明所有运行时依赖",
                    "   - 移除未使用的依赖",
                    "",
                    "5. 文档同步:",
                    "   - 更新 README.md 移除 Kimi 命名",
                    "   - 确保 PRD 与实际代码一致",
                ],
            },
        }

        for key, sol in solutions.items():
            print(f"\n[{sol['title']}]")
            print(f"  描述: {sol['description']}")
            print(f"  步骤:")
            for step in sol["steps"]:
                print(f"    {step}")

        return solutions

    def run_full_analysis(self) -> dict[str, Any]:
        """运行完整分析."""
        result = {
            "finding_id": "F5",
            "title": "依赖、命名与文档漂移",
            "severity": "P1",
            "analysis": {
                "deprecated_imports": self.scan_imports(),
                "pyproject_dependencies": self.check_pyproject_dependencies(),
                "naming_consistency": self.analyze_naming_consistency(),
                "deprecated_patterns": self.scan_deprecated_patterns(),
                "document_alignment": self.check_document_alignment(),
            },
            "solutions": self.generate_solution(),
        }
        return result


async def main():
    """主函数."""
    debugger = DependencyDriftDebugger()
    result = debugger.run_full_analysis()
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
