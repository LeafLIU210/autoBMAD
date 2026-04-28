"""CLI 行为验证工具 - TD-1 深度研究

验证新旧 CLI 入口的实际行为差异。

使用方法:
    python tools/cli_behavior_verifier.py [--verbose]
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

# 确保能导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "autoBMAD"))


class CLIBehaviorVerifier:
    """CLI 行为验证器."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.auto_bmad_path = self.project_root / "autoBMAD" / "docuswarm"
        self.results: dict[str, Any] = {}

    def verify_command_equivalence(self) -> dict[str, Any]:
        """验证新旧入口的命令等价性."""
        print("[验证] 命令等价性分析...")
        
        # 获取旧入口的命令
        old_commands = self._extract_old_commands()
        
        # 获取新入口的命令
        new_commands = self._extract_new_commands()
        
        # 比较命令
        comparison = {
            "old_commands": old_commands,
            "new_commands": new_commands,
            "missing_in_new": sorted(set(old_commands.keys()) - set(new_commands.keys())),
            "missing_in_old": sorted(set(new_commands.keys()) - set(old_commands.keys())),
            "common": sorted(set(old_commands.keys()) & set(new_commands.keys()))
        }
        
        # 检查共同命令的参数一致性
        parameter_diffs = []
        for cmd_name in comparison["common"]:
            old_params = old_commands[cmd_name].get("parameters", [])
            new_params = new_commands[cmd_name].get("parameters", [])
            
            if old_params != new_params:
                parameter_diffs.append({
                    "command": cmd_name,
                    "old_params": old_params,
                    "new_params": new_params
                })
        
        comparison["parameter_differences"] = parameter_diffs
        comparison["equivalent"] = (
            len(comparison["missing_in_new"]) == 0 and
            len(comparison["missing_in_old"]) == 0 and
            len(parameter_diffs) == 0
        )
        
        self.results["command_equivalence"] = comparison
        return comparison

    def verify_import_paths(self) -> dict[str, Any]:
        """验证导入路径差异."""
        print("[验证] 导入路径分析...")
        
        old_imports = self._extract_imports(self.auto_bmad_path / "main.py")
        new_imports = self._extract_imports(self.auto_bmad_path / "cli" / "main.py")
        
        # 分析关键依赖
        key_dependencies = [
            "HybridOrchestrator",
            "StateManager",
            "QuestionHandler",
            "FileStorage",
            "load_config",
            "configure_logging"
        ]
        
        old_deps = {dep: dep in " ".join(old_imports) for dep in key_dependencies}
        new_deps = {dep: dep in " ".join(new_imports) for dep in key_dependencies}
        
        analysis = {
            "old_imports_count": len(old_imports),
            "new_imports_count": len(new_imports),
            "old_has_direct_dependencies": old_deps,
            "new_has_direct_dependencies": new_deps,
            "old_imports_sample": old_imports[:10],
            "new_imports_sample": new_imports[:10]
        }
        
        self.results["import_paths"] = analysis
        return analysis

    def verify_architecture_layers(self) -> dict[str, Any]:
        """验证架构分层."""
        print("[验证] 架构分层分析...")
        
        # 旧入口直接调用的分析
        old_file = self.auto_bmad_path / "main.py"
        old_content = old_file.read_text(encoding="utf-8")
        
        # 检查是否在 CLI 层直接调用业务逻辑
        violations = []
        
        # 检查是否直接实例化 orchestrator
        if "HybridOrchestrator(" in old_content:
            violations.append("旧入口直接实例化 HybridOrchestrator")
        
        # 检查是否直接实例化 StateManager
        if "StateManager(" in old_content:
            violations.append("旧入口直接实例化 StateManager")
        
        # 检查是否在命令函数外调用 asyncio.run
        if "asyncio.run(orchestrator" in old_content or "asyncio.run(self." in old_content:
            violations.append("旧入口在 CLI 层直接调用异步业务逻辑")
        
        # 新入口分析
        new_file = self.auto_bmad_path / "cli" / "main.py"
        new_content = new_file.read_text(encoding="utf-8")
        
        new_violations = []
        if "HybridOrchestrator(" in new_content:
            new_violations.append("新入口直接实例化 HybridOrchestrator")
        if "StateManager(" in new_content:
            new_violations.append("新入口直接实例化 StateManager")
        
        analysis = {
            "old_violations": violations,
            "new_violations": new_violations,
            "old_architecture_score": max(0, 10 - len(violations)),
            "new_architecture_score": max(0, 10 - len(new_violations)),
            "layer_separation": "新入口采用了命令层->服务层->业务层的分层架构" if not new_violations else "新入口存在架构违规"
        }
        
        self.results["architecture_layers"] = analysis
        return analysis

    def verify_test_alignment(self) -> dict[str, Any]:
        """验证测试对齐情况."""
        print("[验证] 测试对齐分析...")
        
        test_dir = self.project_root / "tests"
        
        # 统计测试引用
        old_entry_refs = 0
        new_entry_refs = 0
        test_files_checked = []
        
        if test_dir.exists():
            for test_file in test_dir.rglob("*.py"):
                content = test_file.read_text(encoding="utf-8")
                relative_path = test_file.relative_to(self.project_root)
                test_files_checked.append(str(relative_path))
                
                # 检查旧入口引用
                if "from autoBMAD.docuswarm.main import" in content:
                    old_entry_refs += 1
                if "from autoBMAD.docuswarm import main" in content:
                    old_entry_refs += 1
                
                # 检查新入口引用
                if "from autoBMAD.docuswarm.cli.main import" in content:
                    new_entry_refs += 1
                if "from autoBMAD.docuswarm.cli import main" in content:
                    new_entry_refs += 1
        
        # 检查打包入口
        pyproject = self.project_root / "pyproject.toml"
        package_entry = None
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if 'docuswarm = ' in line:
                    package_entry = line.strip()
                    break
        
        # 检查模块入口
        main_py = self.auto_bmad_path / "__main__.py"
        module_entry = None
        if main_py.exists():
            content = main_py.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.strip().startswith("from ") and " import cli" in line:
                    module_entry = line.strip()
                    break
        
        analysis = {
            "test_files_checked": len(test_files_checked),
            "old_entry_test_refs": old_entry_refs,
            "new_entry_test_refs": new_entry_refs,
            "package_entry": package_entry,
            "module_entry": module_entry,
            "production_uses_old": "autoBMAD.docuswarm.main" in (package_entry or ""),
            "production_uses_new": "autoBMAD.docuswarm.cli.main" in (package_entry or ""),
            "test_uses_old": old_entry_refs > 0,
            "test_uses_new": new_entry_refs > 0,
            "alignment_status": "对齐" if (
                ("autoBMAD.docuswarm.cli.main" in (package_entry or "")) == (new_entry_refs > 0)
            ) else "错位"
        }
        
        self.results["test_alignment"] = analysis
        return analysis

    def verify_functional_parity(self) -> dict[str, Any]:
        """验证功能对等性."""
        print("[验证] 功能对等性分析...")
        
        # 检查旧入口的功能
        old_file = self.auto_bmad_path / "main.py"
        old_content = old_file.read_text(encoding="utf-8")
        
        old_features = {
            "start_command": "@cli.command()" in old_content and "def start(" in old_content,
            "status_command": "@cli.command()" in old_content and "def status(" in old_content,
            "resume_command": "@cli.command()" in old_content and "def resume(" in old_content,
            "cancel_command": "@cli.command()" in old_content and "def cancel" in old_content,
            "cancel_all_command": "def cancel_all_pipelines(" in old_content,
            "clean_command": "def clean_pipelines(" in old_content,
            "list_command": "def list_pipelines(" in old_content,
            "export_command": "def export(" in old_content,
            "questions_command": "def questions(" in old_content,
            "answer_command": "def answer(" in old_content,
            "rich_tables": "from rich.table import Table" in old_content,
            "async_support": "import asyncio" in old_content,
            "logging_config": "configure_logging" in old_content
        }
        
        # 检查新入口的命令层
        new_commands_dir = self.auto_bmad_path / "cli" / "commands"
        new_features = {
            "start_command": (new_commands_dir / "start.py").exists(),
            "status_command": (new_commands_dir / "status.py").exists(),
            "resume_command": (new_commands_dir / "resume.py").exists(),
            "cancel_command": (new_commands_dir / "cancel.py").exists(),
            "clean_command": (new_commands_dir / "clean.py").exists(),
            "list_command": (new_commands_dir / "list.py").exists(),
            "export_command": (new_commands_dir / "export.py").exists(),
            "questions_command": (new_commands_dir / "questions.py").exists(),
            "answer_command": (new_commands_dir / "answer.py").exists()
        }
        
        # 检查新入口的服务层
        service_file = self.auto_bmad_path / "cli" / "services" / "pipeline_service.py"
        if service_file.exists():
            service_content = service_file.read_text(encoding="utf-8")
            new_features["rich_tables"] = "from rich" in service_content
            new_features["async_support"] = "import asyncio" in service_content
            new_features["logging_config"] = "logging" in service_content
        
        # 检查新入口是否缺少 cancel_all 命令
        new_features["cancel_all_command"] = False  # 需要检查 list.py 或其他文件
        for cmd_file in new_commands_dir.glob("*.py"):
            content = cmd_file.read_text(encoding="utf-8")
            if "cancel_all" in content or "cancel-all" in content:
                new_features["cancel_all_command"] = True
                break
        
        # 计算功能覆盖
        old_feature_set = set(old_features.keys())
        new_feature_set = set(new_features.keys())
        
        analysis = {
            "old_features": old_features,
            "new_features": new_features,
            "feature_parity": {
                "old_only": sorted(old_feature_set - new_feature_set),
                "new_only": sorted(new_feature_set - old_feature_set),
                "common": sorted(old_feature_set & new_feature_set)
            },
            "parity_score": f"{len(old_feature_set & new_feature_set)}/{len(old_feature_set)}"
        }
        
        self.results["functional_parity"] = analysis
        return analysis

    def _extract_old_commands(self) -> dict[str, dict]:
        """提取旧入口的命令定义."""
        file_path = self.auto_bmad_path / "main.py"
        content = file_path.read_text(encoding="utf-8")
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {}
        
        commands = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查是否有 @cli.command() 装饰器
                is_command = False
                for decorator in node.decorator_list:
                    deco_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
                    if "cli.command" in deco_str:
                        is_command = True
                        break
                
                if is_command:
                    # 提取参数
                    params = []
                    for decorator in node.decorator_list:
                        deco_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
                        if "click.option" in deco_str or "click.argument" in deco_str:
                            params.append(deco_str)
                    
                    commands[node.name] = {
                        "parameters": params,
                        "line_count": node.end_lineno - node.lineno + 1 if node.end_lineno else 0
                    }
        
        return commands

    def _extract_new_commands(self) -> dict[str, dict]:
        """提取新入口的命令定义."""
        commands = {}
        commands_dir = self.auto_bmad_path / "cli" / "commands"
        
        if not commands_dir.exists():
            return commands
        
        for cmd_file in commands_dir.glob("*.py"):
            if cmd_file.name.startswith("_"):
                continue
            
            content = cmd_file.read_text(encoding="utf-8")
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否有 @click.command() 装饰器
                    is_command = False
                    for decorator in node.decorator_list:
                        deco_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
                        if "click.command" in deco_str:
                            is_command = True
                            break
                    
                    if is_command:
                        # 提取参数
                        params = []
                        for decorator in node.decorator_list:
                            deco_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
                            if "click.option" in deco_str or "click.argument" in deco_str:
                                params.append(deco_str)
                        
                        commands[node.name] = {
                            "parameters": params,
                            "file": cmd_file.name,
                            "line_count": node.end_lineno - node.lineno + 1 if node.end_lineno else 0
                        }
        
        return commands

    def _extract_imports(self, file_path: Path) -> list[str]:
        """提取文件的导入语句."""
        if not file_path.exists():
            return []
        
        content = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports

    def run_full_verification(self) -> dict[str, Any]:
        """运行完整验证."""
        print("=" * 60)
        print("CLI 行为验证工具")
        print("=" * 60)
        print()
        
        self.verify_command_equivalence()
        self.verify_import_paths()
        self.verify_architecture_layers()
        self.verify_test_alignment()
        self.verify_functional_parity()
        
        print()
        print("=" * 60)
        print("[完成] 验证完成")
        print("=" * 60)
        
        return self.results

    def generate_report(self, output_path: Path | None = None) -> str:
        """生成验证报告."""
        if not self.results:
            self.run_full_verification()
        
        lines = []
        lines.append("# TD-1 CLI 行为验证报告")
        lines.append("")
        lines.append("## 概述")
        lines.append("")
        lines.append("本报告通过静态代码分析验证新旧 CLI 入口的行为差异。")
        lines.append("")
        
        # 命令等价性
        cmd_eq = self.results.get("command_equivalence", {})
        lines.append("## 命令等价性分析")
        lines.append("")
        lines.append(f"- 旧入口命令数: {len(cmd_eq.get('old_commands', {}))}")
        lines.append(f"- 新入口命令数: {len(cmd_eq.get('new_commands', {}))}")
        lines.append(f"- 命令等价: {'是' if cmd_eq.get('equivalent') else '否'}")
        
        if cmd_eq.get('missing_in_new'):
            lines.append(f"- 新入口缺失命令: {', '.join(cmd_eq['missing_in_new'])}")
        if cmd_eq.get('missing_in_old'):
            lines.append(f"- 旧入口缺失命令: {', '.join(cmd_eq['missing_in_old'])}")
        lines.append("")
        
        # 架构分层
        arch = self.results.get("architecture_layers", {})
        lines.append("## 架构分层分析")
        lines.append("")
        lines.append(f"- 旧入口架构评分: {arch.get('old_architecture_score', 'N/A')}/10")
        lines.append(f"- 新入口架构评分: {arch.get('new_architecture_score', 'N/A')}/10")
        lines.append(f"- 分层说明: {arch.get('layer_separation', 'N/A')}")
        
        if arch.get('old_violations'):
            lines.append("")
            lines.append("旧入口架构违规:")
            for v in arch['old_violations']:
                lines.append(f"- {v}")
        lines.append("")
        
        # 测试对齐
        test = self.results.get("test_alignment", {})
        lines.append("## 测试对齐分析")
        lines.append("")
        lines.append(f"- 生产使用旧入口: {'是' if test.get('production_uses_old') else '否'}")
        lines.append(f"- 生产使用新入口: {'是' if test.get('production_uses_new') else '否'}")
        lines.append(f"- 测试使用旧入口: {'是' if test.get('test_uses_old') else '否'}")
        lines.append(f"- 测试使用新入口: {'是' if test.get('test_uses_new') else '否'}")
        lines.append(f"- 对齐状态: {test.get('alignment_status', '未知')}")
        lines.append("")
        
        # 功能对等
        func = self.results.get("functional_parity", {})
        lines.append("## 功能对等性")
        lines.append("")
        lines.append(f"- 功能对等评分: {func.get('parity_score', 'N/A')}")
        
        parity = func.get('feature_parity', {})
        if parity.get('old_only'):
            lines.append(f"- 旧入口独有功能: {', '.join(parity['old_only'])}")
        if parity.get('new_only'):
            lines.append(f"- 新入口独有功能: {', '.join(parity['new_only'])}")
        lines.append("")
        
        # 结论
        lines.append("## 结论")
        lines.append("")
        
        alignment = test.get('alignment_status', '')
        if alignment == "错位":
            lines.append("**发现严重问题**: 测试入口与生产入口不一致！")
            lines.append("")
            lines.append("- 生产环境通过 `pyproject.toml` 使用旧入口")
            lines.append("- 测试代码导入的是新入口")
            lines.append("- 这意味着测试通过不等于生产入口安全")
        else:
            lines.append("**状态**: 入口已对齐")
        
        lines.append("")
        
        report = "\n".join(lines)
        
        if output_path:
            output_path.write_text(report, encoding="utf-8")
            print(f"[保存] 报告已保存: {output_path}")
        
        return report


def main():
    """主函数."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CLI 行为验证工具")
    parser.add_argument(
        "--report", "-r",
        type=str,
        default="docs/research/2026-03-18-TD1-cli-behavior-verification.md",
        help="报告输出路径"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    verifier = CLIBehaviorVerifier()
    verifier.run_full_verification()
    
    # 生成报告
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    verifier.generate_report(report_path)
    
    # 打印关键发现
    print("\n" + "=" * 60)
    print("关键发现摘要:")
    print("=" * 60)
    
    test = verifier.results.get("test_alignment", {})
    print(f"测试对齐状态: {test.get('alignment_status', '未知')}")
    
    cmd_eq = verifier.results.get("command_equivalence", {})
    print(f"命令等价性: {'是' if cmd_eq.get('equivalent') else '否'}")
    
    arch = verifier.results.get("architecture_layers", {})
    print(f"架构评分: 旧={arch.get('old_architecture_score', 'N/A')}/10, 新={arch.get('new_architecture_score', 'N/A')}/10")


if __name__ == "__main__":
    main()
