"""F3 CLI 分层入口深度研究工具

针对评估报告 F3 发现（CLI 分层已完成 80% 但真实入口仍未切换）的深度研究工具。
通过运行时检查、AST 分析和配置审查，全面分析新旧 CLI 入口的差异和切换障碍。

使用方法:
    python tools/f3_cli_entry_deep_researcher.py [--output OUTPUT_DIR]

输出:
    - 运行时命令对比分析
    - 入口点配置审查
    - 服务层完整度评估
    - 切换障碍清单
    - 迁移建议报告
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CommandSpec:
    """命令规格."""
    name: str
    help_text: str | None = None
    params: list[dict[str, Any]] = field(default_factory=list)
    is_async: bool = False
    source_file: str | None = None
    line_count: int = 0
    has_asyncio_run: bool = False


@dataclass
class EntryPointRuntime:
    """入口点运行时信息."""
    name: str
    module_path: str
    file_path: str
    line_count: int
    commands: list[CommandSpec] = field(default_factory=list)
    click_group_options: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ServiceLayerAnalysis:
    """服务层分析."""
    module_path: str
    file_path: str
    methods: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    has_orchestrator: bool = False
    has_state_manager: bool = False


@dataclass
class EntryPointConfig:
    """入口点配置."""
    pyproject_entry: str | None = None
    pyproject_module: str | None = None
    main_py_entry: str | None = None
    main_py_module: str | None = None
    is_aligned: bool = False


@dataclass
class MigrationGap:
    """迁移缺口."""
    category: str
    description: str
    severity: str  # high, medium, low
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ResearchReport:
    """完整研究报告."""
    timestamp: str
    old_entry: EntryPointRuntime | None = None
    new_entry: EntryPointRuntime | None = None
    service_layer: ServiceLayerAnalysis | None = None
    entry_config: EntryPointConfig | None = None
    migration_gaps: list[MigrationGap] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)


class CLIEntryDeepResearcher:
    """CLI 入口深度研究器."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.auto_bmad_path = self.project_root / "autoBMAD" / "docuswarm"
        self.results: dict[str, Any] = {}
        
    def run_full_research(self) -> ResearchReport:
        """运行完整研究."""
        import datetime
        
        print("=" * 70)
        print("F3 CLI 分层入口深度研究")
        print("=" * 70)
        print()
        
        # 1. 运行时分析新旧入口
        print("[阶段 1/5] 运行时分析 CLI 入口...")
        old_entry = self._analyze_old_entry_runtime()
        new_entry = self._analyze_new_entry_runtime()
        print(f"  [OK] 旧入口: {len(old_entry.commands)} 个命令")
        print(f"  [OK] 新入口: {len(new_entry.commands)} 个命令")
        print()
        
        # 2. 服务层分析
        print("[阶段 2/5] 分析服务层实现...")
        service_layer = self._analyze_service_layer()
        print(f"  [OK] 服务方法: {len(service_layer.methods)} 个")
        print(f"  [OK] 依赖 Orchestrator: {service_layer.has_orchestrator}")
        print(f"  [OK] 依赖 StateManager: {service_layer.has_state_manager}")
        print()
        
        # 3. 入口配置审查
        print("[阶段 3/5] 审查入口点配置...")
        entry_config = self._analyze_entry_config()
        print(f"  [OK] pyproject.toml: {entry_config.pyproject_entry}")
        print(f"  [OK] __main__.py: {entry_config.main_py_entry}")
        print(f"  [OK] 配置一致: {entry_config.is_aligned}")
        print()
        
        # 4. 迁移缺口分析
        print("[阶段 4/5] 分析迁移缺口...")
        gaps = self._analyze_migration_gaps(old_entry, new_entry, service_layer, entry_config)
        high_gaps = len([g for g in gaps if g.severity == "high"])
        med_gaps = len([g for g in gaps if g.severity == "medium"])
        print(f"  [OK] 发现 {len(gaps)} 个缺口 (高:{high_gaps}, 中:{med_gaps})")
        print()
        
        # 5. 生成建议
        print("[阶段 5/5] 生成迁移建议...")
        recommendations = self._generate_recommendations(gaps, old_entry, new_entry)
        print(f"  [OK] 生成 {len(recommendations)} 条建议")
        print()
        
        print("=" * 70)
        print("研究完成!")
        print("=" * 70)
        
        return ResearchReport(
            timestamp=datetime.datetime.now().isoformat(),
            old_entry=old_entry,
            new_entry=new_entry,
            service_layer=service_layer,
            entry_config=entry_config,
            migration_gaps=gaps,
            recommendations=recommendations
        )
    
    def _analyze_old_entry_runtime(self) -> EntryPointRuntime:
        """运行时分析旧入口."""
        file_path = self.auto_bmad_path / "main.py"
        module_path = "autoBMAD.docuswarm.main"
        
        content = file_path.read_text(encoding="utf-8")
        line_count = len(content.split("\n"))
        
        # 通过导入和反射获取命令信息
        commands = []
        try:
            sys.path.insert(0, str(self.project_root))
            sys.path.insert(0, str(self.project_root / "autoBMAD"))
            
            from autoBMAD.docuswarm.main import cli
            
            # 获取 click group 的命令
            if hasattr(cli, 'commands'):
                for name, cmd in cli.commands.items():
                    spec = self._extract_command_spec(cmd, name, str(file_path))
                    commands.append(spec)
                    
        except Exception as e:
            print(f"    警告: 无法导入旧入口: {e}")
        
        return EntryPointRuntime(
            name="old_main_py",
            module_path=module_path,
            file_path=str(file_path),
            line_count=line_count,
            commands=commands
        )
    
    def _analyze_new_entry_runtime(self) -> EntryPointRuntime:
        """运行时分析新入口."""
        file_path = self.auto_bmad_path / "cli" / "main.py"
        module_path = "autoBMAD.docuswarm.cli.main"
        
        if not file_path.exists():
            return EntryPointRuntime(
                name="new_cli_main",
                module_path=module_path,
                file_path=str(file_path),
                line_count=0,
                commands=[]
            )
        
        content = file_path.read_text(encoding="utf-8")
        line_count = len(content.split("\n"))
        
        commands = []
        try:
            from autoBMAD.docuswarm.cli.main import cli
            
            if hasattr(cli, 'commands'):
                for name, cmd in cli.commands.items():
                    spec = self._extract_command_spec(cmd, name, str(file_path))
                    commands.append(spec)
                    
        except Exception as e:
            print(f"    警告: 无法导入新入口: {e}")
        
        return EntryPointRuntime(
            name="new_cli_main",
            module_path=module_path,
            file_path=str(file_path),
            line_count=line_count,
            commands=commands
        )
    
    def _extract_command_spec(self, cmd: Any, name: str, source_file: str) -> CommandSpec:
        """提取命令规格."""
        help_text = cmd.help if hasattr(cmd, 'help') else None
        params = []
        
        # 提取参数
        if hasattr(cmd, 'params'):
            for p in cmd.params:
                param_info = {
                    'name': p.name,
                    'type': type(p).__name__,
                    'required': getattr(p, 'required', False),
                    'default': str(getattr(p, 'default', None)),
                    'help': getattr(p, 'help', None),
                }
                params.append(param_info)
        
        # 尝试获取回调函数的源码信息
        line_count = 0
        has_asyncio_run = False
        
        if hasattr(cmd, 'callback') and cmd.callback:
            try:
                import inspect
                source = inspect.getsource(cmd.callback)
                line_count = len(source.split("\n"))
                has_asyncio_run = "asyncio.run" in source
            except Exception:
                pass
        
        return CommandSpec(
            name=name,
            help_text=help_text,
            params=params,
            is_async=has_asyncio_run,
            source_file=source_file,
            line_count=line_count,
            has_asyncio_run=has_asyncio_run
        )
    
    def _analyze_service_layer(self) -> ServiceLayerAnalysis:
        """分析服务层."""
        service_file = self.auto_bmad_path / "cli" / "services" / "pipeline_service.py"
        module_path = "autoBMAD.docuswarm.cli.services.pipeline_service"
        
        if not service_file.exists():
            return ServiceLayerAnalysis(
                module_path=module_path,
                file_path=str(service_file),
                methods=[],
                dependencies=[],
                has_orchestrator=False,
                has_state_manager=False
            )
        
        content = service_file.read_text(encoding="utf-8")
        
        # 解析 AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            tree = None
        
        # 提取方法
        methods = []
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name != "__init__":
                        methods.append({
                            'name': node.name,
                            'is_async': isinstance(node, ast.AsyncFunctionDef) or 
                                       any(isinstance(n, ast.AsyncFunctionDef) for n in [node]),
                            'line_count': node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
                            'args': [arg.arg for arg in node.args.args if arg.arg != 'self']
                        })
        
        # 检查依赖
        has_orchestrator = "HybridOrchestrator" in content
        has_state_manager = "StateManager" in content
        
        dependencies = []
        if has_orchestrator:
            dependencies.append("autoBMAD.docuswarm.pipeline.orchestrator.HybridOrchestrator")
        if has_state_manager:
            dependencies.append("autoBMAD.docuswarm.storage.state_manager.StateManager")
        
        return ServiceLayerAnalysis(
            module_path=module_path,
            file_path=str(service_file),
            methods=methods,
            dependencies=dependencies,
            has_orchestrator=has_orchestrator,
            has_state_manager=has_state_manager
        )
    
    def _analyze_entry_config(self) -> EntryPointConfig:
        """分析入口配置."""
        pyproject_entry = None
        pyproject_module = None
        main_py_entry = None
        main_py_module = None
        
        # 检查 pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            for line in content.split("\n"):
                if line.strip().startswith("docuswarm") and "=" in line:
                    pyproject_entry = line.strip()
                    # 提取模块路径
                    if '"' in line:
                        parts = line.split('"')
                        if len(parts) >= 2:
                            pyproject_module = parts[1].split(":")[0] if ":" in parts[1] else parts[1]
                    break
        
        # 检查 __main__.py
        main_py = self.auto_bmad_path / "__main__.py"
        if main_py.exists():
            content = main_py.read_text()
            for line in content.split("\n"):
                if line.strip().startswith("from") and "import cli" in line:
                    main_py_entry = line.strip()
                    # 提取模块路径
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == "from":
                        main_py_module = parts[1]
                    break
        
        # 判断是否一致
        is_aligned = pyproject_module == main_py_module
        
        return EntryPointConfig(
            pyproject_entry=pyproject_entry,
            pyproject_module=pyproject_module,
            main_py_entry=main_py_entry,
            main_py_module=main_py_module,
            is_aligned=is_aligned
        )
    
    def _analyze_migration_gaps(
        self,
        old_entry: EntryPointRuntime,
        new_entry: EntryPointRuntime,
        service_layer: ServiceLayerAnalysis,
        entry_config: EntryPointConfig
    ) -> list[MigrationGap]:
        """分析迁移缺口."""
        gaps = []
        
        # 1. 入口配置不一致
        if not entry_config.is_aligned:
            gaps.append(MigrationGap(
                category="entry_configuration",
                description="pyproject.toml 和 __main__.py 使用不同的入口模块",
                severity="high",
                evidence=[
                    f"pyproject.toml: {entry_config.pyproject_module}",
                    f"__main__.py: {entry_config.main_py_module}"
                ],
                recommendation="统一两个入口配置，都指向新的 cli.main 模块"
            ))
        
        # 2. 生产入口使用旧模块
        if entry_config.pyproject_module and "cli.main" not in entry_config.pyproject_module:
            gaps.append(MigrationGap(
                category="production_entry",
                description="生产入口 (pyproject.toml) 仍指向旧 main 模块",
                severity="high",
                evidence=[
                    f"当前配置: {entry_config.pyproject_entry}",
                    "建议改为: docuswarm = \"autoBMAD.docuswarm.cli.main:cli\""
                ],
                recommendation="修改 pyproject.toml [project.scripts] 指向新入口"
            ))
        
        # 3. 命令数量对比
        old_commands = {c.name for c in old_entry.commands}
        new_commands = {c.name for c in new_entry.commands}
        
        missing_in_new = old_commands - new_commands
        if missing_in_new:
            gaps.append(MigrationGap(
                category="command_coverage",
                description=f"新入口缺失 {len(missing_in_new)} 个命令",
                severity="high",
                evidence=sorted(missing_in_new),
                recommendation="将缺失的命令实现迁移到 cli/commands/ 目录"
            ))
        
        # 4. 服务层方法覆盖度
        service_methods = {m['name'] for m in service_layer.methods}
        expected_methods = {'start', 'status', 'resume', 'cancel', 'list_pipelines'}
        missing_methods = expected_methods - service_methods
        
        if missing_methods:
            gaps.append(MigrationGap(
                category="service_layer",
                description=f"服务层缺失 {len(missing_methods)} 个预期方法",
                severity="medium",
                evidence=sorted(missing_methods),
                recommendation="在 PipelineService 中实现缺失的方法"
            ))
        
        # 5. 架构违规检查
        old_violations = [c for c in old_entry.commands if c.has_asyncio_run]
        if old_violations:
            gaps.append(MigrationGap(
                category="architecture",
                description=f"旧入口有 {len(old_violations)} 个命令直接调用 asyncio.run",
                severity="medium",
                evidence=[f"{c.name} ({c.line_count} 行)" for c in old_violations],
                recommendation="将业务逻辑迁移到服务层，CLI 层只负责参数解析和结果展示"
            ))
        
        # 6. 代码行数对比
        if old_entry.line_count > 600 and new_entry.line_count < 100:
            gaps.append(MigrationGap(
                category="code_bloat",
                description="旧入口代码量过大，新入口过于精简",
                severity="low",
                evidence=[
                    f"旧入口: {old_entry.line_count} 行",
                    f"新入口: {new_entry.line_count} 行",
                    f"差值: {old_entry.line_count - new_entry.line_count} 行"
                ],
                recommendation="这是正常的分层结果，新入口的代码量转移到 commands/ 和 services/ 目录"
            ))
        
        return gaps
    
    def _generate_recommendations(
        self,
        gaps: list[MigrationGap],
        old_entry: EntryPointRuntime,
        new_entry: EntryPointRuntime
    ) -> list[dict[str, Any]]:
        """生成迁移建议."""
        recommendations = []
        
        # 基于缺口生成建议
        high_gaps = [g for g in gaps if g.severity == "high"]
        
        if high_gaps:
            recommendations.append({
                "priority": "P0",
                "title": "立即切换入口配置",
                "description": "修改 pyproject.toml 和 __main__.py 指向新入口",
                "steps": [
                    "修改 pyproject.toml: docuswarm = \"autoBMAD.docuswarm.cli.main:cli\"",
                    "修改 __main__.py: from autoBMAD.docuswarm.cli.main import cli",
                    "验证 pip install -e . 后 docuswarm 命令可用"
                ],
                "risks": ["需要确保新入口的所有命令已实现"]
            })
        
        # 检查命令覆盖
        old_commands = {c.name for c in old_entry.commands}
        new_commands = {c.name for c in new_entry.commands}
        missing = old_commands - new_commands
        
        if missing:
            recommendations.append({
                "priority": "P1",
                "title": "完成命令迁移",
                "description": f"将 {len(missing)} 个命令从旧入口迁移到新入口",
                "steps": [
                    f"迁移命令: {', '.join(sorted(missing))}",
                    "在 cli/commands/ 下创建新的命令模块",
                    "使用 PipelineService 封装业务逻辑",
                    "保持命令行接口向后兼容"
                ],
                "risks": ["命令参数可能有细微差异，需要验证"]
            })
        
        recommendations.append({
            "priority": "P2",
            "title": "删除或归档旧入口",
            "description": "在验证新入口稳定后删除旧 main.py",
            "steps": [
                "运行完整回归测试",
                "确保所有旧命令在新入口可用",
                "删除 autoBMAD/docuswarm/main.py",
                "更新相关文档"
            ],
            "risks": ["如果有其他模块直接导入旧 main.py 会失败"]
        })
        
        return recommendations


def generate_markdown_report(report: ResearchReport, output_path: Path) -> None:
    """生成 Markdown 格式研究报告."""
    lines = []
    
    # 标题
    lines.append("# F3 CLI 分层入口深度研究报告")
    lines.append("")
    lines.append(f"**研究时间**: {report.timestamp}")
    lines.append(f"**研究工具**: `tools/f3_cli_entry_deep_researcher.py`")
    lines.append(f"**研究对象**: DocuSwarm CLI 新旧入口分层问题")
    lines.append("")
    
    # 执行摘要
    lines.append("## 执行摘要")
    lines.append("")
    
    if report.migration_gaps:
        high_count = len([g for g in report.migration_gaps if g.severity == "high"])
        med_count = len([g for g in report.migration_gaps if g.severity == "medium"])
        lines.append(f"本研究针对 F3 技术债务（CLI 分层完成 80% 但真实入口未切换）进行深度分析。")
        lines.append(f"发现 **{len(report.migration_gaps)}** 个迁移缺口，其中高优先级 **{high_count}** 个，中优先级 **{med_count}** 个。")
    lines.append("")
    
    # 关键发现
    lines.append("### 关键发现")
    lines.append("")
    
    if report.entry_config:
        if not report.entry_config.is_aligned:
            lines.append("🔴 **入口配置不一致**: pyproject.toml 和 __main__.py 指向不同模块")
            lines.append(f"   - pyproject.toml → `{report.entry_config.pyproject_module}`")
            lines.append(f"   - __main__.py → `{report.entry_config.main_py_module}`")
            lines.append("")
        
        if report.entry_config.pyproject_module and "cli.main" not in report.entry_config.pyproject_module:
            lines.append("🔴 **生产入口未切换**: `pip install` 后的 `docuswarm` 命令仍使用旧入口")
            lines.append("")
    
    if report.old_entry and report.new_entry:
        old_cmds = {c.name for c in report.old_entry.commands}
        new_cmds = {c.name for c in report.new_entry.commands}
        missing = old_cmds - new_cmds
        
        if missing:
            lines.append(f"🟡 **命令迁移不完整**: 新入口缺失 {len(missing)} 个命令")
            lines.append(f"   - 缺失: {', '.join(sorted(missing))}")
            lines.append("")
        
        lines.append(f"📊 **代码量对比**:")
        lines.append(f"   - 旧入口: {report.old_entry.line_count} 行（包含业务逻辑）")
        lines.append(f"   - 新入口: {report.new_entry.line_count} 行（仅注册命令）")
        lines.append(f"   - 差异: 新入口采用分层架构，业务逻辑移至 services/")
        lines.append("")
    
    # 入口点详细对比
    lines.append("## 入口点详细对比")
    lines.append("")
    
    if report.old_entry and report.new_entry:
        lines.append("| 属性 | 旧入口 (main.py) | 新入口 (cli/main.py) |")
        lines.append("|------|------------------|---------------------|")
        lines.append(f"| 模块路径 | `{report.old_entry.module_path}` | `{report.new_entry.module_path}` |")
        lines.append(f"| 文件路径 | `{report.old_entry.file_path}` | `{report.new_entry.file_path}` |")
        lines.append(f"| 代码行数 | {report.old_entry.line_count} 行 | {report.new_entry.line_count} 行 |")
        lines.append(f"| 注册命令 | {len(report.old_entry.commands)} 个 | {len(report.new_entry.commands)} 个 |")
        lines.append("")
    
    # 命令详细对比
    lines.append("### 命令详细对比")
    lines.append("")
    
    if report.old_entry and report.new_entry:
        old_by_name = {c.name: c for c in report.old_entry.commands}
        new_by_name = {c.name: c for c in report.new_entry.commands}
        
        all_names = set(old_by_name.keys()) | set(new_by_name.keys())
        
        lines.append("| 命令 | 旧入口 | 新入口 | 状态 |")
        lines.append("|------|--------|--------|------|")
        
        for name in sorted(all_names):
            old_ok = "✓" if name in old_by_name else "✗"
            new_ok = "✓" if name in new_by_name else "✗"
            
            if name in old_by_name and name in new_by_name:
                status = "已迁移"
            elif name in old_by_name:
                status = "待迁移"
            else:
                status = "新增"
            
            lines.append(f"| `{name}` | {old_ok} | {new_ok} | {status} |")
        
        lines.append("")
    
    # 服务层分析
    if report.service_layer:
        lines.append("## 服务层分析")
        lines.append("")
        lines.append(f"**模块**: `{report.service_layer.module_path}`")
        lines.append(f"**文件**: `{report.service_layer.file_path}`")
        lines.append("")
        lines.append(f"**依赖关系**:")
        for dep in report.service_layer.dependencies:
            lines.append(f"- `{dep}`")
        lines.append("")
        
        if report.service_layer.methods:
            lines.append("**已实现方法**:")
            lines.append("")
            lines.append("| 方法 | 异步 | 行数 | 参数 |")
            lines.append("|------|------|------|------|")
            for m in report.service_layer.methods:
                async_flag = "✓" if m.get('is_async') else "✗"
                args = ", ".join(m.get('args', []))
                lines.append(f"| `{m['name']}` | {async_flag} | {m['line_count']} | {args} |")
            lines.append("")
    
    # 入口配置详情
    if report.entry_config:
        lines.append("## 入口配置详情")
        lines.append("")
        lines.append("### pyproject.toml 配置")
        lines.append(f"```toml")
        lines.append(f"[project.scripts]")
        lines.append(f"{report.entry_config.pyproject_entry or '# 未配置'}")
        lines.append(f"```")
        lines.append("")
        
        lines.append("### __main__.py 配置")
        lines.append(f"```python")
        lines.append(f"{report.entry_config.main_py_entry or '# 未配置'}")
        lines.append(f"```")
        lines.append("")
        
        lines.append("### 配置一致性")
        if report.entry_config.is_aligned:
            lines.append("✅ **一致**: 两个入口配置指向同一模块")
        else:
            lines.append("❌ **不一致**: 两个入口配置指向不同模块")
            lines.append(f"- pyproject.toml → `{report.entry_config.pyproject_module}`")
            lines.append(f"- __main__.py → `{report.entry_config.main_py_module}`")
        lines.append("")
    
    # 迁移缺口清单
    if report.migration_gaps:
        lines.append("## 迁移缺口清单")
        lines.append("")
        
        severity_order = {"high": 0, "medium": 1, "low": 2}
        sorted_gaps = sorted(report.migration_gaps, key=lambda g: severity_order.get(g.severity, 3))
        
        for gap in sorted_gaps:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(gap.severity, "⚪")
            lines.append(f"### {emoji} [{gap.severity.upper()}] {gap.category}")
            lines.append("")
            lines.append(f"**描述**: {gap.description}")
            lines.append("")
            
            if gap.evidence:
                lines.append("**证据**:")
                for e in gap.evidence:
                    lines.append(f"- {e}")
                lines.append("")
            
            if gap.recommendation:
                lines.append(f"**建议**: {gap.recommendation}")
                lines.append("")
    
    # 迁移建议
    if report.recommendations:
        lines.append("## 迁移建议")
        lines.append("")
        
        for i, rec in enumerate(report.recommendations, 1):
            priority_color = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(rec.get('priority', ''), "⚪")
            lines.append(f"### {priority_color} [{rec.get('priority', 'N/A')}] {rec.get('title', '')}")
            lines.append("")
            lines.append(f"{rec.get('description', '')}")
            lines.append("")
            
            if rec.get('steps'):
                lines.append("**执行步骤**:")
                for step in rec['steps']:
                    lines.append(f"1. {step}")
                lines.append("")
            
            if rec.get('risks'):
                lines.append("**风险提醒**:")
                for risk in rec['risks']:
                    lines.append(f"- ⚠️ {risk}")
                lines.append("")
    
    # 结论
    lines.append("## 结论")
    lines.append("")
    lines.append("F3 技术债务的核心问题是 **CLI 分层架构已经实现，但生产入口配置未切换**。")
    lines.append("")
    lines.append("这导致:")
    lines.append("1. 测试使用新入口，生产使用旧入口，测试无法保护生产代码")
    lines.append("2. 新旧代码并行维护，增加认知负担")
    lines.append("3. 新架构的优势无法在生产环境体现")
    lines.append("")
    lines.append("建议采取以下行动:")
    lines.append("1. **立即**: 修改入口配置指向新 CLI")
    lines.append("2. **1-2 天内**: 验证所有命令在新入口正常工作")
    lines.append("3. **1 周内**: 完成缺失命令的迁移")
    lines.append("4. **2 周内**: 删除旧入口代码")
    lines.append("")
    
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[保存] Markdown 报告: {output_path}")


def generate_json_report(report: ResearchReport, output_path: Path) -> None:
    """生成 JSON 格式报告."""
    
    def to_dict(obj):
        if hasattr(obj, '__dataclass_fields__'):
            return {k: to_dict(v) for k, v in asdict(obj).items()}
        elif isinstance(obj, list):
            return [to_dict(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: to_dict(v) for k, v in obj.items()}
        return obj
    
    output_path.write_text(
        json.dumps(to_dict(report), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"[保存] JSON 报告: {output_path}")


def main():
    """主函数."""
    import argparse
    
    parser = argparse.ArgumentParser(description="F3 CLI 分层入口深度研究工具")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="docs/research",
        help="报告输出目录"
    )
    
    args = parser.parse_args()
    
    # 运行研究
    researcher = CLIEntryDeepResearcher()
    report = researcher.run_full_research()
    
    # 保存报告
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = report.timestamp[:10]  # YYYY-MM-DD
    
    md_path = output_dir / f"{timestamp}-f3-cli-layered-entry-deep-research-report.md"
    generate_markdown_report(report, md_path)
    
    json_path = output_dir / f"{timestamp}-f3-cli-layered-entry-deep-research-report.json"
    generate_json_report(report, json_path)
    
    print(f"\n{'=' * 70}")
    print("所有报告已生成完毕!")
    print(f"输出目录: {output_dir.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
