"""
DocuSwarm 架构分析器 - 用于深度研究 Kimi 依赖和迁移准备

功能：
1. 分析 Kimi 依赖分布
2. 识别关键迁移点
3. 生成架构依赖图
4. 对比 epic_automation 架构模式

用法：
    python tools/architecture_analyzer.py --mode deps
    python tools/architecture_analyzer.py --mode compare
    python tools/architecture_analyzer.py --mode report --output migration-analysis.md
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ImportInfo:
    """导入信息"""
    module: str
    names: list[str]
    is_kimi: bool = False
    is_claude: bool = False
    line_number: int = 0


@dataclass
class FileAnalysis:
    """文件分析结果"""
    path: Path
    kimi_imports: list[ImportInfo] = field(default_factory=list)
    claude_imports: list[ImportInfo] = field(default_factory=list)
    session_manager_usage: list[dict[str, Any]] = field(default_factory=list)
    kimi_types: list[str] = field(default_factory=list)


@dataclass
class ArchitectureReport:
    """架构分析报告"""
    files_analyzed: int = 0
    kimi_dependency_count: int = 0
    session_manager_files: list[Path] = field(default_factory=list)
    critical_migration_points: list[dict[str, Any]] = field(default_factory=list)
    file_analyses: list[FileAnalysis] = field(default_factory=list)


def is_kimi_import(module: str) -> bool:
    """检查是否为 Kimi 相关导入"""
    kimi_modules = [
        "kimi_agent_sdk",
        "kimi_cli",
        "kaos",
    ]
    return any(module.startswith(km) for km in kimi_modules)


def is_claude_import(module: str) -> bool:
    """检查是否为 Claude 相关导入"""
    return module.startswith("claude_agent_sdk")


def analyze_file(file_path: Path) -> FileAnalysis | None:
    """分析单个文件的导入和依赖"""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return None

    analysis = FileAnalysis(path=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                info = ImportInfo(
                    module=alias.name,
                    names=[alias.asname or alias.name],
                    is_kimi=is_kimi_import(alias.name),
                    is_claude=is_claude_import(alias.name),
                    line_number=node.lineno,
                )
                if info.is_kimi:
                    analysis.kimi_imports.append(info)
                elif info.is_claude:
                    analysis.claude_imports.append(info)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            info = ImportInfo(
                module=module,
                names=names,
                is_kimi=is_kimi_import(module),
                is_claude=is_claude_import(module),
                line_number=node.lineno,
            )
            if info.is_kimi:
                analysis.kimi_imports.append(info)
                analysis.kimi_types.extend(names)
            elif info.is_claude:
                analysis.claude_imports.append(info)

    # 查找 KimiSessionManager 使用
    if "KimiSessionManager" in content:
        analysis.session_manager_usage.append({
            "type": "KimiSessionManager",
            "count": content.count("KimiSessionManager"),
        })

    return analysis


def analyze_docuswarm() -> ArchitectureReport:
    """分析整个 docuswarm 项目"""
    report = ArchitectureReport()
    docuswarm_path = PROJECT_ROOT / "autoBMAD" / "docuswarm"

    python_files = list(docuswarm_path.rglob("*.py"))
    python_files = [f for f in python_files if "__pycache__" not in str(f)]

    for file_path in python_files:
        analysis = analyze_file(file_path)
        if analysis:
            report.files_analyzed += 1
            report.file_analyses.append(analysis)

            if analysis.kimi_imports:
                report.kimi_dependency_count += len(analysis.kimi_imports)

            if analysis.session_manager_usage:
                report.session_manager_files.append(file_path)

    # 识别关键迁移点
    critical_files = [
        "llm/session_manager.py",
        "agents/independent.py",
        "agents/evaluator.py",
        "agents/base.py",
        "nodes/dual_agent.py",
        "pipeline/orchestrator.py",
        "llm/approval.py",
        "config.py",
    ]

    for cf in critical_files:
        cf_path = docuswarm_path / cf
        if cf_path.exists():
            analysis = next(
                (a for a in report.file_analyses if a.path == cf_path),
                None
            )
            if analysis:
                report.critical_migration_points.append({
                    "file": cf,
                    "kimi_imports": len(analysis.kimi_imports),
                    "kimi_types": analysis.kimi_types,
                    "session_manager_usage": bool(analysis.session_manager_usage),
                })

    return report


def generate_dependency_report(report: ArchitectureReport) -> str:
    """生成依赖分析报告"""
    lines = []
    lines.append("# DocuSwarm Kimi 依赖分析报告")
    lines.append("")
    lines.append("## 统计概览")
    lines.append("")
    lines.append(f"- 分析文件数: {report.files_analyzed}")
    lines.append(f"- Kimi 依赖总数: {report.kimi_dependency_count}")
    lines.append(f"- 使用 SessionManager 的文件: {len(report.session_manager_files)}")
    lines.append("")

    lines.append("## 关键迁移点")
    lines.append("")
    lines.append("| 文件 | Kimi 导入数 | 关键类型 | SessionManager |")
    lines.append("|------|------------|----------|----------------|")
    for point in report.critical_migration_points:
        types = ", ".join(point["kimi_types"][:3])
        sm = "是" if point["session_manager_usage"] else "否"
        lines.append(
            f"| {point['file']} | {point['kimi_imports']} | {types} | {sm} |"
        )
    lines.append("")

    lines.append("## 详细依赖分布")
    lines.append("")
    for analysis in report.file_analyses:
        if analysis.kimi_imports:
            rel_path = analysis.path.relative_to(PROJECT_ROOT)
            lines.append(f"### {rel_path}")
            lines.append("")
            for imp in analysis.kimi_imports:
                names = ", ".join(imp.names)
                lines.append(f"- 行 {imp.line_number}: `{imp.module}` → {names}")
            lines.append("")

    return "\n".join(lines)


def compare_with_epic_automation() -> str:
    """对比 epic_automation 架构"""
    lines = []
    lines.append("# epic_automation 架构模式对比")
    lines.append("")

    # 检查 epic_automation 的核心组件
    epic_path = PROJECT_ROOT / "autoBMAD" / "epic_automation"
    core_components = {
        "SDKResult": epic_path / "core" / "sdk_result.py",
        "CancellationManager": epic_path / "core" / "cancellation_manager.py",
        "SDKExecutor": epic_path / "core" / "sdk_executor.py",
        "sdk_helper": epic_path / "agents" / "sdk_helper.py",
        "SDKWrapper": epic_path / "sdk_wrapper.py",
    }

    lines.append("## epic_automation 核心组件状态")
    lines.append("")
    for name, path in core_components.items():
        exists = "✓" if path.exists() else "✗"
        lines.append(f"- {exists} `{name}`: `{path.relative_to(PROJECT_ROOT)}`")
    lines.append("")

    lines.append("## 架构模式对比")
    lines.append("")
    lines.append("| 能力 | docuswarm (当前) | epic_automation (目标) |")
    lines.append("|------|-----------------|----------------------|")
    lines.append("| 结果标准化 | ✗ 无统一结果类型 | ✓ SDKResult |")
    lines.append("| 取消管理 | ✗ 无显式清理确认 | ✓ CancellationManager |")
    lines.append("| 执行隔离 | ✗ 直接调用 SDK | ✓ SDKExecutor (TaskGroup) |")
    lines.append("| Agent 入口 | ✗ 各 Agent 分别调用 | ✓ sdk_helper 统一入口 |")
    lines.append("| 错误分类 | ✗ 异常直接透传 | ✓ SDKErrorType 显式分类 |")
    lines.append("")

    lines.append("## 可复用组件清单")
    lines.append("")
    lines.append("以下组件可直接移植到 docuswarm：")
    lines.append("")
    lines.append("1. **sdk_result.py** - SDKResult 数据类（无需修改）")
    lines.append("2. **cancellation_manager.py** - CancellationManager（可能需要适配）")
    lines.append("3. **sdk_executor.py** - SDKExecutor（核心逻辑，需要测试）")
    lines.append("4. **sdk_helper.py** - execute_sdk_call 函数（需要适配 Prompt 格式）")
    lines.append("")

    return "\n".join(lines)


def generate_migration_checklist(report: ArchitectureReport) -> str:
    """生成迁移检查清单"""
    lines = []
    lines.append("# DocuSwarm 迁移检查清单")
    lines.append("")
    lines.append("基于架构分析生成的检查清单，按 Phase 组织。")
    lines.append("")

    # Phase 0
    lines.append("## Phase 0: 运行时抽象层建设")
    lines.append("")
    lines.append("### 新增文件")
    lines.append("- [ ] `llm/runtime.py` - LLMRuntime 抽象接口")
    lines.append("- [ ] `llm/sdk_result.py` - SDKResult + SDKErrorType")
    lines.append("- [ ] `llm/cancellation_manager.py` - CancellationManager")
    lines.append("- [ ] `llm/sdk_executor.py` - SDKExecutor")
    lines.append("- [ ] `llm/claude_runtime.py` - ClaudeRuntime 实现")
    lines.append("- [ ] `agents/sdk_helper.py` - execute_sdk_call 统一入口")
    lines.append("")
    lines.append("### 修改文件")
    lines.append("- [ ] `config.py` - 添加 ANTHROPIC_API_KEY 支持")
    lines.append("")

    # Phase 1
    lines.append("## Phase 1: 轻量调用路径迁移")
    lines.append("")
    lines.append("### Context Validator")
    lines.append("- [ ] 修改 `orchestrator._validate_context()`")
    lines.append("- [ ] 替换 `single_prompt()` 调用为 `execute_sdk_call()`")
    lines.append("- [ ] 测试验证逻辑正常工作")
    lines.append("")
    lines.append("### EvaluatorAgent")
    lines.append("- [ ] 修改 `_call_llm()` 方法")
    lines.append("- [ ] 适配 SDKResult 消息解析")
    lines.append("- [ ] 测试评分准确性")
    lines.append("")

    # Phase 2
    lines.append("## Phase 2: IndependentAgent 迁移")
    lines.append("")
    lines.append("### 工具调用链路")
    lines.append("- [ ] 设计 provider-neutral 工具注册")
    lines.append("- [ ] 实现 `approval_policy.py` 策略层")
    lines.append("- [ ] 修改 `_call_llm_via_session()` 方法")
    lines.append("- [ ] 适配 Claude 消息格式")
    lines.append("")
    lines.append("### 交付物生成")
    lines.append("- [ ] 验证 `create_deliverable` 工具触发")
    lines.append("- [ ] 测试交付物文件写入")
    lines.append("")

    # Phase 3
    lines.append("## Phase 3: 编排恢复链路迁移")
    lines.append("")
    lines.append("### Session 管理")
    lines.append("- [ ] 修改 `_attempt_session_resume()`")
    lines.append("- [ ] 集成 CancellationManager 清理确认")
    lines.append("- [ ] 修复状态机语义（假成功问题）")
    lines.append("")

    # Phase 4
    lines.append("## Phase 4: Kimi 代码移除")
    lines.append("")
    lines.append("### 清理工作")
    lines.append("- [ ] 移除 `llm/session_manager.py`")
    lines.append("- [ ] 移除 `llm/approval.py`")
    lines.append("- [ ] 更新 `config.py` 移除 KIMI_*")
    lines.append("- [ ] 更新文档")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DocuSwarm 架构分析器 - 用于迁移准备"
    )
    parser.add_argument(
        "--mode",
        choices=["deps", "compare", "checklist", "report"],
        default="deps",
        help="分析模式: deps=依赖分析, compare=架构对比, checklist=检查清单, report=完整报告"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径（默认输出到 stdout）"
    )
    args = parser.parse_args()

    if args.mode == "deps":
        report = analyze_docuswarm()
        content = generate_dependency_report(report)

    elif args.mode == "compare":
        content = compare_with_epic_automation()

    elif args.mode == "checklist":
        report = analyze_docuswarm()
        content = generate_migration_checklist(report)

    elif args.mode == "report":
        report = analyze_docuswarm()
        deps_report = generate_dependency_report(report)
        compare_report = compare_with_epic_automation()
        checklist = generate_migration_checklist(report)
        content = f"""{deps_report}

---

{compare_report}

---

{checklist}
"""

    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(content, encoding="utf-8")
        print(f"报告已保存到: {output_path}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
