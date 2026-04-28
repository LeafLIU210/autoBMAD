"""CLI 入口差异分析工具 - TD-1 深度研究

用于研究 DocuSwarm 项目中旧 CLI 入口 (main.py) 与新 CLI 入口 (cli/main.py) 的差异。
这是 TD-1 技术债务的核心：生产入口与测试入口错位。

使用方法:
    python tools/cli_entry_analyzer.py [--report OUTPUT_FILE]
"""

from __future__ import annotations

import ast
import inspect
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# 确保能导入项目模块
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "autoBMAD"))


@dataclass
class CommandInfo:
    """CLI 命令信息."""
    name: str
    source_file: str
    line_count: int
    has_asyncio_run: bool
    uses_hybrid_orchestrator: bool
    uses_state_manager: bool
    imports: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)


@dataclass
class EntryPointAnalysis:
    """入口点分析结果."""
    name: str
    module_path: str
    file_path: str
    line_count: int
    cli_function: str
    commands: list[CommandInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    architecture_violations: list[str] = field(default_factory=list)


@dataclass
class AnalysisReport:
    """完整分析报告."""
    old_entry: EntryPointAnalysis | None = None
    new_entry: EntryPointAnalysis | None = None
    command_divergence: dict[str, Any] = field(default_factory=dict)
    coverage_gap: dict[str, Any] = field(default_factory=dict)
    risk_assessment: dict[str, Any] = field(default_factory=dict)


class CLIEntryAnalyzer:
    """CLI 入口分析器."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.auto_bmad_path = self.project_root / "autoBMAD" / "docuswarm"
        
    def analyze_old_entry(self) -> EntryPointAnalysis:
        """分析旧入口 (main.py)."""
        file_path = self.auto_bmad_path / "main.py"
        module_path = "autoBMAD.docuswarm.main"
        
        if not file_path.exists():
            raise FileNotFoundError(f"旧入口文件不存在: {file_path}")
        
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        line_count = len(lines)
        
        # 解析 AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return EntryPointAnalysis(
                name="old_main_py",
                module_path=module_path,
                file_path=str(file_path),
                line_count=line_count,
                cli_function="cli",
                architecture_violations=[f"语法错误: {e}"]
            )
        
        # 提取导入
        imports = self._extract_imports(tree)
        
        # 分析命令
        commands = self._analyze_commands_in_tree(tree, str(file_path))
        
        # 检查架构违规
        violations = self._check_architecture_violations(tree, content)
        
        return EntryPointAnalysis(
            name="old_main_py",
            module_path=module_path,
            file_path=str(file_path),
            line_count=line_count,
            cli_function="cli",
            commands=commands,
            imports=imports,
            architecture_violations=violations
        )
    
    def analyze_new_entry(self) -> EntryPointAnalysis:
        """分析新入口 (cli/main.py)."""
        file_path = self.auto_bmad_path / "cli" / "main.py"
        module_path = "autoBMAD.docuswarm.cli.main"
        
        if not file_path.exists():
            raise FileNotFoundError(f"新入口文件不存在: {file_path}")
        
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        line_count = len(lines)
        
        # 解析 AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return EntryPointAnalysis(
                name="new_cli_main",
                module_path=module_path,
                file_path=str(file_path),
                line_count=line_count,
                cli_function="cli",
                architecture_violations=[f"语法错误: {e}"]
            )
        
        # 提取导入
        imports = self._extract_imports(tree)
        
        # 分析命令（在新入口中命令是从 commands 模块导入的）
        commands = self._analyze_imported_commands()
        
        # 检查架构违规
        violations = self._check_architecture_violations(tree, content)
        
        return EntryPointAnalysis(
            name="new_cli_main",
            module_path=module_path,
            file_path=str(file_path),
            line_count=line_count,
            cli_function="cli",
            commands=commands,
            imports=imports,
            architecture_violations=violations
        )
    
    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """提取导入语句."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return sorted(set(imports))
    
    def _analyze_commands_in_tree(self, tree: ast.AST, file_path: str) -> list[CommandInfo]:
        """分析 AST 中的命令定义."""
        commands = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查是否有 @cli.command() 装饰器
                is_command = False
                decorators = []
                for decorator in node.decorator_list:
                    deco_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
                    decorators.append(deco_str)
                    if "cli.command" in deco_str or "@cli" in deco_str:
                        is_command = True
                
                if is_command:
                    # 检查函数体
                    body_source = ast.unparse(node) if hasattr(ast, "unparse") else ""
                    line_count = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
                    
                    commands.append(CommandInfo(
                        name=node.name,
                        source_file=file_path,
                        line_count=line_count,
                        has_asyncio_run="asyncio.run" in body_source,
                        uses_hybrid_orchestrator="HybridOrchestrator" in body_source,
                        uses_state_manager="StateManager" in body_source,
                        decorators=decorators
                    ))
        
        return commands
    
    def _analyze_imported_commands(self) -> list[CommandInfo]:
        """分析从 commands 模块导入的命令."""
        commands = []
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
            
            file_commands = self._analyze_commands_in_tree(tree, str(cmd_file))
            commands.extend(file_commands)
        
        return commands
    
    def _check_architecture_violations(self, tree: ast.AST, content: str) -> list[str]:
        """检查架构违规."""
        violations = []
        
        # 检查是否在入口层直接执行业务逻辑
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == "cli":
                    continue  # 跳过 CLI 主函数
                    
                body_source = ast.unparse(node) if hasattr(ast, "unparse") else ""
                
                # 检查是否在命令函数中直接调用 asyncio.run
                if "asyncio.run" in body_source and "cli" not in node.name:
                    # 检查是否在 __main__ 块中
                    if not self._is_in_main_block(node, content):
                        violations.append(
                            f"函数 '{node.name}' 直接在 CLI 层调用 asyncio.run()，"
                            "违反了分层架构原则"
                        )
        
        return violations
    
    def _is_in_main_block(self, node: ast.FunctionDef, content: str) -> bool:
        """检查节点是否在 if __name__ == "__main__" 块中."""
        # 简化检查：通过行号判断
        lines = content.split("\n")
        in_main_block = False
        
        for i, line in enumerate(lines[:node.lineno - 1], 1):
            if 'if __name__ == "__main__"' in line or "if __name__ == '__main__'" in line:
                in_main_block = True
            if in_main_block and line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                in_main_block = False
        
        return in_main_block
    
    def analyze_command_divergence(
        self, old_entry: EntryPointAnalysis, new_entry: EntryPointAnalysis
    ) -> dict[str, Any]:
        """分析两个入口的命令差异."""
        old_commands = {cmd.name: cmd for cmd in old_entry.commands}
        new_commands = {cmd.name: cmd for cmd in new_entry.commands}
        
        old_only = set(old_commands.keys()) - set(new_commands.keys())
        new_only = set(new_commands.keys()) - set(old_commands.keys())
        common = set(old_commands.keys()) & set(new_commands.keys())
        
        # 检查共同命令的实现差异
        implementation_diffs = []
        for cmd_name in common:
            old_cmd = old_commands[cmd_name]
            new_cmd = new_commands[cmd_name]
            
            if old_cmd.line_count != new_cmd.line_count:
                implementation_diffs.append({
                    "command": cmd_name,
                    "old_lines": old_cmd.line_count,
                    "new_lines": new_cmd.line_count,
                    "line_diff": new_cmd.line_count - old_cmd.line_count
                })
        
        return {
            "old_entry_only_commands": sorted(old_only),
            "new_entry_only_commands": sorted(new_only),
            "common_commands": sorted(common),
            "command_count": {
                "old_entry": len(old_entry.commands),
                "new_entry": len(new_entry.commands)
            },
            "implementation_differences": implementation_diffs
        }
    
    def analyze_coverage_gap(
        self, old_entry: EntryPointAnalysis, new_entry: EntryPointAnalysis
    ) -> dict[str, Any]:
        """分析测试覆盖缺口."""
        # 检查测试文件导入的是哪个入口
        test_dir = self.project_root / "tests"
        old_refs = 0
        new_refs = 0
        
        if test_dir.exists():
            for test_file in test_dir.rglob("*.py"):
                content = test_file.read_text(encoding="utf-8")
                if "from autoBMAD.docuswarm.main import" in content or \
                   "from autoBMAD.docuswarm.main import cli" in content:
                    old_refs += 1
                if "from autoBMAD.docuswarm.cli.main import" in content or \
                   "from autoBMAD.docuswarm.cli.main import cli" in content:
                    new_refs += 1
        
        # 检查 pyproject.toml 打包入口
        pyproject = self.project_root / "pyproject.toml"
        package_entry = None
        if pyproject.exists():
            content = pyproject.read_text()
            for line in content.split("\n"):
                if 'docuswarm = ' in line:
                    package_entry = line.strip()
                    break
        
        # 检查 __main__.py
        main_py = self.auto_bmad_path / "__main__.py"
        module_entry = None
        if main_py.exists():
            content = main_py.read_text()
            for line in content.split("\n"):
                if "from" in line and "import cli" in line:
                    module_entry = line.strip()
                    break
        
        return {
            "test_references": {
                "old_entry_count": old_refs,
                "new_entry_count": new_refs,
                "test_entry_mismatch": old_refs == 0 and new_refs > 0
            },
            "package_entry": package_entry,
            "module_entry": module_entry,
            "production_uses_old": old_entry.module_path in (package_entry or ""),
            "production_uses_new": new_entry.module_path in (package_entry or "")
        }
    
    def assess_risks(
        self, old_entry: EntryPointAnalysis, new_entry: EntryPointAnalysis, divergence: dict
    ) -> dict[str, Any]:
        """风险评估."""
        risks = []
        risk_level = "low"
        
        # 检查 1: 测试入口与生产入口不一致
        if divergence.get("test_references", {}).get("test_entry_mismatch"):
            risks.append({
                "type": "entry_mismatch",
                "severity": "high",
                "description": "测试使用新入口，但生产环境使用旧入口，导致测试无法保护生产代码",
                "evidence": f"生产入口: {old_entry.module_path}, 测试入口: {new_entry.module_path}"
            })
            risk_level = "high"
        
        # 检查 2: 命令缺失
        old_only = divergence.get("old_entry_only_commands", [])
        new_only = divergence.get("new_entry_only_commands", [])
        
        if old_only:
            risks.append({
                "type": "missing_commands_in_new",
                "severity": "medium",
                "description": f"旧入口有但新入口没有的命令: {old_only}",
                "evidence": f"缺失命令: {', '.join(old_only)}"
            })
            if risk_level == "low":
                risk_level = "medium"
        
        if new_only:
            risks.append({
                "type": "missing_commands_in_old",
                "severity": "low",
                "description": f"新入口有但旧入口没有的命令: {new_only}",
                "evidence": f"新增命令: {', '.join(new_only)}"
            })
        
        # 检查 3: 架构违规
        old_violations = len(old_entry.architecture_violations)
        new_violations = len(new_entry.architecture_violations)
        
        if old_violations > 0:
            risks.append({
                "type": "architecture_violation",
                "severity": "medium",
                "description": f"旧入口存在 {old_violations} 个架构违规",
                "evidence": old_entry.architecture_violations[:3]  # 前3个
            })
            if risk_level == "low":
                risk_level = "medium"
        
        # 检查 4: 代码行数差异（旧入口是否过于臃肿）
        line_diff = old_entry.line_count - new_entry.line_count
        if line_diff > 500:
            risks.append({
                "type": "code_bloat",
                "severity": "medium",
                "description": f"旧入口比新入口多 {line_diff} 行代码，维护成本高",
                "evidence": f"旧入口: {old_entry.line_count} 行, 新入口: {new_entry.line_count} 行"
            })
        
        return {
            "risk_level": risk_level,
            "risks": risks,
            "summary": {
                "high_risks": len([r for r in risks if r["severity"] == "high"]),
                "medium_risks": len([r for r in risks if r["severity"] == "medium"]),
                "low_risks": len([r for r in risks if r["severity"] == "low"])
            }
        }
    
    def run_full_analysis(self) -> AnalysisReport:
        """运行完整分析."""
        print("[开始] 分析 CLI 入口差异...")
        print("=" * 60)
        
        print("\n[分析] 旧入口 (main.py)...")
        old_entry = self.analyze_old_entry()
        print(f"   [OK] 找到 {len(old_entry.commands)} 个命令")
        print(f"   [OK] 文件大小: {old_entry.line_count} 行")
        if old_entry.architecture_violations:
            print(f"   [WARN] 发现 {len(old_entry.architecture_violations)} 个架构违规")
        
        print("\n[分析] 新入口 (cli/main.py)...")
        new_entry = self.analyze_new_entry()
        print(f"   [OK] 找到 {len(new_entry.commands)} 个命令")
        print(f"   [OK] 文件大小: {new_entry.line_count} 行")
        if new_entry.architecture_violations:
            print(f"   [WARN] 发现 {len(new_entry.architecture_violations)} 个架构违规")
        
        print("\n[分析] 命令差异...")
        divergence = self.analyze_command_divergence(old_entry, new_entry)
        print(f"   旧入口独有: {len(divergence['old_entry_only_commands'])} 个")
        print(f"   新入口独有: {len(divergence['new_entry_only_commands'])} 个")
        print(f"   共同命令: {len(divergence['common_commands'])} 个")
        
        print("\n[分析] 测试覆盖...")
        coverage_gap = self.analyze_coverage_gap(old_entry, new_entry)
        print(f"   测试引用旧入口: {coverage_gap['test_references']['old_entry_count']} 次")
        print(f"   测试引用新入口: {coverage_gap['test_references']['new_entry_count']} 次")
        print(f"   打包入口: {coverage_gap['package_entry']}")
        
        print("\n[分析] 风险评估...")
        risk_assessment = self.assess_risks(old_entry, new_entry, coverage_gap)
        print(f"   风险等级: {risk_assessment['risk_level'].upper()}")
        print(f"   高风险项: {risk_assessment['summary']['high_risks']}")
        print(f"   中风险项: {risk_assessment['summary']['medium_risks']}")
        print(f"   低风险项: {risk_assessment['summary']['low_risks']}")
        
        print("\n" + "=" * 60)
        print("[完成] 分析完成!")
        
        return AnalysisReport(
            old_entry=old_entry,
            new_entry=new_entry,
            command_divergence=divergence,
            coverage_gap=coverage_gap,
            risk_assessment=risk_assessment
        )


def generate_markdown_report(report: AnalysisReport, output_path: Path) -> None:
    """生成 Markdown 格式报告."""
    lines = []
    
    lines.append("# TD-1 CLI 真实入口与受测入口错位 - 深度研究报告")
    lines.append("")
    lines.append(f"**生成时间**: {__import__('datetime').datetime.now().isoformat()}")
    lines.append(f"**研究工具**: tools/cli_entry_analyzer.py")
    lines.append("")
    
    # 执行摘要
    lines.append("## 执行摘要")
    lines.append("")
    lines.append(f"本研究报告针对 TD-1 技术债务（CLI 真实入口与受测入口错位）进行深度分析。")
    lines.append("")
    
    risk_level = report.risk_assessment.get("risk_level", "unknown")
    risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk_level, "⚪")
    lines.append(f"**整体风险等级**: {risk_emoji} {risk_level.upper()}")
    lines.append("")
    
    # 关键发现
    lines.append("### 关键发现")
    lines.append("")
    
    coverage = report.coverage_gap
    test_refs = coverage.get("test_references", {})
    if test_refs.get("test_entry_mismatch"):
        lines.append("🔴 **严重问题**: 测试入口与生产入口不一致")
        lines.append("   - 测试代码导入的是 `autoBMAD.docuswarm.cli.main:cli`（新入口）")
        lines.append("   - 生产环境通过 `pyproject.toml` 使用的是 `autoBMAD.docuswarm.main:cli`（旧入口）")
        lines.append("   - **后果**: 测试通过 ≠ 生产入口安全")
        lines.append("")
    
    if report.old_entry and report.new_entry:
        line_diff = report.old_entry.line_count - report.new_entry.line_count
        if line_diff > 500:
            lines.append(f"🟡 **代码臃肿**: 旧入口 ({report.old_entry.line_count} 行) 比新入口 ({report.new_entry.line_count} 行) 多 {line_diff} 行")
            lines.append("   - 旧入口将业务逻辑与 CLI 层耦合")
            lines.append("   - 新入口采用分层架构，业务逻辑委托给 services/ 模块")
            lines.append("")
    
    divergence = report.command_divergence
    old_only = divergence.get("old_entry_only_commands", [])
    new_only = divergence.get("new_entry_only_commands", [])
    
    if old_only:
        lines.append(f"🟡 **命令缺失**: 旧入口有 {len(old_only)} 个命令可能未迁移到新入口")
        lines.append(f"   - 缺失命令: {', '.join(old_only)}")
        lines.append("")
    
    if new_only:
        lines.append(f"🟢 **新功能**: 新入口新增了 {len(new_only)} 个命令")
        lines.append(f"   - 新增命令: {', '.join(new_only)}")
        lines.append("")
    
    # 详细分析
    lines.append("## 详细分析")
    lines.append("")
    
    # 入口对比
    lines.append("### 入口点对比")
    lines.append("")
    lines.append("| 属性 | 旧入口 (main.py) | 新入口 (cli/main.py) |")
    lines.append("|------|------------------|---------------------|")
    
    if report.old_entry and report.new_entry:
        lines.append(f"| 模块路径 | `{report.old_entry.module_path}` | `{report.new_entry.module_path}` |")
        lines.append(f"| 文件路径 | `{report.old_entry.file_path}` | `{report.new_entry.file_path}` |")
        lines.append(f"| 代码行数 | {report.old_entry.line_count} 行 | {report.new_entry.line_count} 行 |")
        lines.append(f"| 命令数量 | {len(report.old_entry.commands)} 个 | {len(report.new_entry.commands)} 个 |")
        old_v = len(report.old_entry.architecture_violations)
        new_v = len(report.new_entry.architecture_violations)
        lines.append(f"| 架构违规 | {old_v} 个 | {new_v} 个 |")
    
    lines.append("")
    
    # 命令对比
    lines.append("### 命令对比")
    lines.append("")
    
    if old_only:
        lines.append(f"**仅在旧入口存在的命令** ({len(old_only)} 个):")
        for cmd in old_only:
            lines.append(f"- `{cmd}`")
        lines.append("")
    
    if new_only:
        lines.append(f"**仅在新入口存在的命令** ({len(new_only)} 个):")
        for cmd in new_only:
            lines.append(f"- `{cmd}`")
        lines.append("")
    
    common = divergence.get("common_commands", [])
    if common:
        lines.append(f"**两个入口都存在的命令** ({len(common)} 个):")
        lines.append(f"`{'`, `'.join(common)}`")
        lines.append("")
    
    # 测试覆盖分析
    lines.append("### 测试覆盖分析")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 测试引用旧入口次数 | {test_refs.get('old_entry_count', 0)} |")
    lines.append(f"| 测试引用新入口次数 | {test_refs.get('new_entry_count', 0)} |")
    lines.append(f"| pyproject.toml 打包入口 | `{coverage.get('package_entry', 'N/A')}` |")
    lines.append(f"| __main__.py 模块入口 | `{coverage.get('module_entry', 'N/A')}` |")
    lines.append("")
    
    # 架构违规详情
    if report.old_entry and report.old_entry.architecture_violations:
        lines.append("### 旧入口架构违规详情")
        lines.append("")
        for v in report.old_entry.architecture_violations[:10]:  # 最多显示10个
            lines.append(f"- ⚠️ {v}")
        lines.append("")
    
    # 风险评估详情
    lines.append("### 风险评估")
    lines.append("")
    
    risks = report.risk_assessment.get("risks", [])
    if risks:
        for risk in risks:
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk["severity"], "⚪")
            lines.append(f"**{severity_emoji} [{risk['severity'].upper()}] {risk['type']}**")
            lines.append(f"- 描述: {risk['description']}")
            if isinstance(risk['evidence'], list):
                lines.append(f"- 证据: {', '.join(map(str, risk['evidence']))}")
            else:
                lines.append(f"- 证据: {risk['evidence']}")
            lines.append("")
    else:
        lines.append("✅ 未发现明显风险")
        lines.append("")
    
    # 建议方案
    lines.append("## 建议方案")
    lines.append("")
    lines.append("基于以上分析，推荐以下收敛方案：")
    lines.append("")
    lines.append("### 方案 A: 切换到新入口（推荐）")
    lines.append("")
    lines.append("**步骤**:")
    lines.append("1. 修改 `pyproject.toml` 中的打包入口:")
    lines.append("   ```toml")
    lines.append("   [project.scripts]")
    lines.append('   docuswarm = "autoBMAD.docuswarm.cli.main:cli"')
    lines.append("   ```")
    lines.append("2. 修改 `autoBMAD/docuswarm/__main__.py`:")
    lines.append("   ```python")
    lines.append("   from autoBMAD.docuswarm.cli.main import cli")
    lines.append("   ```")
    lines.append("3. 确保旧入口中独有的命令已迁移到新入口")
    lines.append("4. 添加针对真实打包入口的 smoke tests")
    lines.append("")
    lines.append("**优点**:")
    lines.append("- 新入口采用分层架构，维护性更好")
    lines.append("- 测试与实际入口一致")
    lines.append("- 代码更少，职责更清晰")
    lines.append("")
    lines.append("**风险**:")
    if old_only:
        lines.append(f"- 需要迁移以下命令: {', '.join(old_only)}")
    lines.append("")
    
    lines.append("### 方案 B: 废弃新入口，回并到旧入口")
    lines.append("")
    lines.append("**步骤**:")
    lines.append("1. 将新入口中的命令实现合并回旧入口")
    lines.append("2. 删除 `cli/` 目录")
    lines.append("3. 更新测试以导入旧入口")
    lines.append("")
    lines.append("**优点**:")
    lines.append("- 改动范围小")
    lines.append("")
    lines.append("**缺点**:")
    lines.append("- 旧入口继续臃肿，技术债务累积")
    lines.append("- 丢失分层架构的成果")
    lines.append("")
    
    # 结论
    lines.append("## 结论")
    lines.append("")
    lines.append("TD-1 技术债务的核心是 **测试入口与生产入口不一致**，这导致测试无法有效保护生产代码。")
    lines.append("建议立即采取行动，选择上述方案之一进行收敛，避免债务进一步累积。")
    lines.append("")
    
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[保存] 报告已保存: {output_path}")


def main():
    """主函数."""
    import argparse
    import datetime
    
    parser = argparse.ArgumentParser(description="CLI 入口差异分析工具")
    parser.add_argument(
        "--report", "-r",
        type=str,
        default=f"docs/research/2026-03-18-TD1-cli-entry-misalignment-research-report.md",
        help="报告输出路径"
    )
    parser.add_argument(
        "--json", "-j",
        type=str,
        default=None,
        help="JSON 格式报告输出路径"
    )
    
    args = parser.parse_args()
    
    analyzer = CLIEntryAnalyzer()
    report = analyzer.run_full_analysis()
    
    # 生成 Markdown 报告
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    generate_markdown_report(report, report_path)
    
    # 可选：生成 JSON 报告
    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为可序列化的字典
        def to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: to_dict(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [to_dict(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: to_dict(v) for k, v in obj.items()}
            return obj
        
        json_path.write_text(
            json.dumps(to_dict(report), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"[保存] JSON 报告已保存: {json_path}")
    
    return report


if __name__ == "__main__":
    main()
