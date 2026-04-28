"""
MemoryManager 依赖扫描器 - 分析 MemoryManager 的全部引用和依赖链

功能：
1. 搜索所有引用 MemoryManager、memory_manager、MemoryScope 的导入和使用
2. 分析依赖方向（谁依赖 MemoryManager，MemoryManager 依赖谁）
3. 生成完整的依赖图、引用点清单、安全移除的影响范围评估

用法：
    python tools/memory_manager_dependency_scanner.py
    python tools/memory_manager_dependency_scanner.py --output .tmp/memory_manager_deps.json
    python tools/memory_manager_dependency_scanner.py --format text --print
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTOBBMAD_ROOT = PROJECT_ROOT / "autoBMAD"
TMP_DIR = PROJECT_ROOT / ".tmp"

# MemoryManager 相关的关键词
MEMORY_MANAGER_SYMBOLS = [
    "MemoryManager",
    "MemoryScope",
    "memory_manager",
    "memory.py",
]

MEMORY_MODULE_PATH = "autoBMAD.docuswarm.context.memory"

# 依赖权重：用于评估移除复杂度
REMOVAL_COMPLEXITY = {
    "direct_import": 3,   # 直接导入
    "type_annotation": 1,  # 仅类型注解
    "instantiation": 4,    # 实例化
    "method_call": 2,      # 方法调用
    "passed_as_arg": 2,    # 作为参数传递
}


@dataclass
class ImportReference:
    """导入引用"""
    file: str
    line: int
    import_type: str  # "from_import" | "direct_import"
    module: str
    imported_names: list[str]
    alias: str | None = None


@dataclass
class UsagePoint:
    """使用点"""
    file: str
    line: int
    function: str
    class_name: str | None
    usage_type: str  # "instantiation" | "method_call" | "type_annotation" | "passed_as_arg"
    symbol: str
    code_snippet: str
    complexity_score: int = 0


@dataclass
class DependencyNode:
    """依赖图节点"""
    module_path: str
    file: str
    imports_memory: bool = False
    is_memory_module: bool = False
    imported_by: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    usage_count: int = 0
    removal_complexity: int = 0


@dataclass
class MemoryManagerReport:
    """MemoryManager 依赖报告"""
    import_references: list[ImportReference] = field(default_factory=list)
    usage_points: list[UsagePoint] = field(default_factory=list)
    dependency_graph: dict[str, DependencyNode] = field(default_factory=dict)
    removal_impact: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)


class MemoryManagerASTVisitor(ast.NodeVisitor):
    """AST 访问器：扫描 MemoryManager 的导入和使用"""

    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.lines = source.splitlines()
        self.import_references: list[ImportReference] = []
        self.usage_points: list[UsagePoint] = []
        self._class_stack: list[str] = []
        self._func_stack: list[str] = []

    def _get_line(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.lines):
            return self.lines[lineno - 1].strip()
        return ""

    def _is_memory_symbol(self, name: str) -> bool:
        return any(sym in name for sym in ["MemoryManager", "MemoryScope", "memory_manager"])

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._func_stack.append(node.name)

        # 检查参数类型注解
        for arg in node.args.args:
            if arg.annotation:
                try:
                    ann_src = ast.unparse(arg.annotation)
                    if self._is_memory_symbol(ann_src):
                        self.usage_points.append(UsagePoint(
                            file=self.file_path,
                            line=node.lineno,
                            function=".".join(self._func_stack),
                            class_name=self._class_stack[-1] if self._class_stack else None,
                            usage_type="type_annotation",
                            symbol=ann_src,
                            code_snippet=self._get_line(node.lineno)[:120],
                            complexity_score=REMOVAL_COMPLEXITY["type_annotation"],
                        ))
                except Exception:
                    pass

        self.generic_visit(node)
        self._func_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if self._is_memory_symbol(alias.name):
                self.import_references.append(ImportReference(
                    file=self.file_path,
                    line=node.lineno,
                    import_type="direct_import",
                    module=alias.name,
                    imported_names=[alias.name],
                    alias=alias.asname,
                ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not node.module:
            self.generic_visit(node)
            return

        memory_names = [
            alias.name for alias in node.names
            if self._is_memory_symbol(alias.name)
        ]
        if memory_names or "memory" in (node.module or ""):
            # 过滤：只关注 docuswarm.context.memory
            if "context" in node.module or "memory" in node.module:
                self.import_references.append(ImportReference(
                    file=self.file_path,
                    line=node.lineno,
                    import_type="from_import",
                    module=node.module,
                    imported_names=memory_names,
                ))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """检测实例化和方法调用"""
        func_src = ""
        try:
            func_src = ast.unparse(node.func)
        except Exception:
            pass

        if self._is_memory_symbol(func_src):
            # 判断是实例化还是方法调用
            if isinstance(node.func, ast.Name) and node.func.id[0].isupper():
                usage_type = "instantiation"
            elif isinstance(node.func, ast.Attribute):
                usage_type = "method_call"
            else:
                usage_type = "method_call"

            func_name = ".".join(self._func_stack) if self._func_stack else "<module>"
            self.usage_points.append(UsagePoint(
                file=self.file_path,
                line=node.lineno,
                function=func_name,
                class_name=self._class_stack[-1] if self._class_stack else None,
                usage_type=usage_type,
                symbol=func_src,
                code_snippet=self._get_line(node.lineno)[:120],
                complexity_score=REMOVAL_COMPLEXITY.get(usage_type, 2),
            ))

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """检测类型注解赋值"""
        try:
            ann_src = ast.unparse(node.annotation)
            if self._is_memory_symbol(ann_src):
                func_name = ".".join(self._func_stack) if self._func_stack else "<module>"
                self.usage_points.append(UsagePoint(
                    file=self.file_path,
                    line=node.lineno,
                    function=func_name,
                    class_name=self._class_stack[-1] if self._class_stack else None,
                    usage_type="type_annotation",
                    symbol=ann_src,
                    code_snippet=self._get_line(node.lineno)[:120],
                    complexity_score=REMOVAL_COMPLEXITY["type_annotation"],
                ))
        except Exception:
            pass
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """检测 MemoryScope.XXX 枚举使用"""
        try:
            full = ast.unparse(node)
            if "MemoryScope." in full or "memory_manager." in full:
                func_name = ".".join(self._func_stack) if self._func_stack else "<module>"
                self.usage_points.append(UsagePoint(
                    file=self.file_path,
                    line=node.lineno,
                    function=func_name,
                    class_name=self._class_stack[-1] if self._class_stack else None,
                    usage_type="method_call",
                    symbol=full[:80],
                    code_snippet=self._get_line(node.lineno)[:120],
                    complexity_score=REMOVAL_COMPLEXITY["method_call"],
                ))
        except Exception:
            pass
        self.generic_visit(node)


def analyze_file(file_path: Path) -> tuple[list[ImportReference], list[UsagePoint]]:
    """分析单个文件"""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  [WARN] 跳过文件 {file_path}: {e}", file=sys.stderr)
        return [], []

    rel_path = str(file_path.relative_to(PROJECT_ROOT))
    visitor = MemoryManagerASTVisitor(source, rel_path)
    visitor.visit(tree)

    # 去重 usage_points（同文件同行同类型）
    seen = set()
    deduped_usage = []
    for u in visitor.usage_points:
        key = (u.file, u.line, u.usage_type, u.symbol)
        if key not in seen:
            seen.add(key)
            deduped_usage.append(u)

    return visitor.import_references, deduped_usage


def build_dependency_graph(
    all_refs: list[ImportReference],
    all_usage: list[UsagePoint],
) -> dict[str, DependencyNode]:
    """构建依赖图"""
    graph: dict[str, DependencyNode] = {}

    # 添加 MemoryManager 自身节点
    memory_key = "autoBMAD/docuswarm/context/memory.py"
    graph[memory_key] = DependencyNode(
        module_path=MEMORY_MODULE_PATH,
        file=memory_key,
        is_memory_module=True,
    )

    # 从导入引用中构建图
    files_importing: dict[str, list[str]] = {}
    for ref in all_refs:
        if ref.file not in files_importing:
            files_importing[ref.file] = []
        files_importing[ref.file].extend(ref.imported_names)

    for file, names in files_importing.items():
        if file not in graph:
            graph[file] = DependencyNode(
                module_path=file.replace("/", ".").replace(".py", ""),
                file=file,
                imports_memory=True,
            )
        graph[file].imports.append(memory_key)
        graph[memory_key].imported_by.append(file)

    # 计算使用复杂度
    for u in all_usage:
        if u.file in graph:
            graph[u.file].usage_count += 1
            graph[u.file].removal_complexity += u.complexity_score

    return graph


def assess_removal_impact(
    all_refs: list[ImportReference],
    all_usage: list[UsagePoint],
    graph: dict[str, DependencyNode],
) -> dict[str, Any]:
    """评估安全移除 MemoryManager 的影响范围"""
    affected_files = list({ref.file for ref in all_refs} | {u.file for u in all_usage})

    # 按复杂度分级
    high_impact = []
    medium_impact = []
    low_impact = []

    for f in affected_files:
        node = graph.get(f)
        if node:
            score = node.removal_complexity
            if score >= 8:
                high_impact.append({"file": f, "score": score, "usage_count": node.usage_count})
            elif score >= 4:
                medium_impact.append({"file": f, "score": score, "usage_count": node.usage_count})
            else:
                low_impact.append({"file": f, "score": score, "usage_count": node.usage_count})

    # 统计使用类型分布
    usage_type_dist: dict[str, int] = {}
    for u in all_usage:
        usage_type_dist[u.usage_type] = usage_type_dist.get(u.usage_type, 0) + 1

    # 是否有测试文件引用
    test_refs = [f for f in affected_files if "test" in f.lower()]

    return {
        "total_affected_files": len(affected_files),
        "affected_files": sorted(affected_files),
        "high_impact_files": sorted(high_impact, key=lambda x: x["score"], reverse=True),
        "medium_impact_files": sorted(medium_impact, key=lambda x: x["score"], reverse=True),
        "low_impact_files": sorted(low_impact, key=lambda x: x["score"], reverse=True),
        "usage_type_distribution": usage_type_dist,
        "test_files_affected": test_refs,
        "removal_steps": _generate_removal_steps(all_refs, all_usage, affected_files),
        "overall_complexity": "high" if high_impact else ("medium" if medium_impact else "low"),
    }


def _generate_removal_steps(
    refs: list[ImportReference],
    usages: list[UsagePoint],
    affected_files: list[str],
) -> list[str]:
    """生成移除建议步骤"""
    steps = [
        "1. 确认 MemoryManager 当前实际使用量（运行此工具后查看 usage_points）",
        "2. 检查所有 test_files_affected 中的测试用例，标记需要更新的测试",
        "3. 对 high_impact_files 中的文件，逐一分析是否可用 NodeExecutionContext.shared_context 替代",
        "4. 移除 context/memory.py 中的 MemoryManager 和 MemoryScope 类",
        "5. 更新 context/__init__.py 移除相关导出",
        "6. 批量替换所有 import 引用（优先处理 medium/low impact 文件）",
        "7. 运行测试套件验证无功能回归",
    ]
    return steps


def run_analysis() -> MemoryManagerReport:
    """运行完整扫描"""
    report = MemoryManagerReport()

    py_files = list(AUTOBBMAD_ROOT.rglob("*.py"))
    print(f"[INFO] 扫描 {len(py_files)} 个 Python 文件...")

    all_refs: list[ImportReference] = []
    all_usage: list[UsagePoint] = []

    for py_file in sorted(py_files):
        refs, usages = analyze_file(py_file)
        if refs or usages:
            rel = str(py_file.relative_to(PROJECT_ROOT))
            print(f"  [FOUND] {rel}: {len(refs)} 个导入, {len(usages)} 个使用点")
        all_refs.extend(refs)
        all_usage.extend(usages)

    report.import_references = all_refs
    report.usage_points = all_usage
    report.dependency_graph = build_dependency_graph(all_refs, all_usage)
    report.removal_impact = assess_removal_impact(all_refs, all_usage, report.dependency_graph)

    # 汇总
    report.summary = {
        "total_import_references": len(all_refs),
        "total_usage_points": len(all_usage),
        "affected_files_count": report.removal_impact.get("total_affected_files", 0),
        "overall_removal_complexity": report.removal_impact.get("overall_complexity", "unknown"),
        "usage_by_type": report.removal_impact.get("usage_type_distribution", {}),
        "dependency_graph_nodes": len(report.dependency_graph),
        "files_importing_memory_manager": [
            ref.file for ref in all_refs
        ],
        "memory_manager_definition": "autoBMAD/docuswarm/context/memory.py",
        "memory_manager_class_api": [
            "MemoryManager.__init__()",
            "MemoryManager.write(key, value, scope: MemoryScope)",
            "MemoryManager.read(key, scope: MemoryScope)",
            "MemoryManager.get_agent_context(agent_type: str)",
            "MemoryManager.clear_private_memory(scope: MemoryScope)",
        ],
    }

    return report


def format_text_report(report: MemoryManagerReport) -> str:
    """格式化文本报告"""
    lines = [
        "=" * 70,
        "MemoryManager 依赖扫描报告",
        "=" * 70,
        "",
        "## 摘要统计",
        f"  - 导入引用总数: {report.summary.get('total_import_references', 0)}",
        f"  - 使用点总数: {report.summary.get('total_usage_points', 0)}",
        f"  - 受影响文件数: {report.summary.get('affected_files_count', 0)}",
        f"  - 移除复杂度评估: {report.summary.get('overall_removal_complexity', 'unknown').upper()}",
        "",
        "## 使用类型分布",
    ]

    for utype, count in report.summary.get("usage_by_type", {}).items():
        lines.append(f"  - {utype}: {count} 处")

    lines += ["", "## 导入引用清单"]
    for ref in report.import_references:
        names_str = ", ".join(ref.imported_names) if ref.imported_names else ref.module
        lines.append(f"  {ref.file}:L{ref.line} — from {ref.module} import {names_str}")

    lines += ["", "## 详细使用点"]
    current_file = None
    for u in sorted(report.usage_points, key=lambda x: (x.file, x.line)):
        if u.file != current_file:
            current_file = u.file
            lines.append(f"\n  [{current_file}]")
        cls = f"{u.class_name}." if u.class_name else ""
        lines.append(
            f"    L{u.line} [{u.usage_type}] {cls}{u.function}: {u.code_snippet}"
        )

    lines += ["", "## 移除影响评估"]
    impact = report.removal_impact
    lines.append(f"  整体复杂度: {impact.get('overall_complexity', 'unknown').upper()}")

    if impact.get("high_impact_files"):
        lines.append("\n  高影响文件 (需要重点处理):")
        for f in impact["high_impact_files"]:
            lines.append(f"    🔴 {f['file']} (分数: {f['score']}, 使用点: {f['usage_count']})")

    if impact.get("medium_impact_files"):
        lines.append("\n  中等影响文件:")
        for f in impact["medium_impact_files"]:
            lines.append(f"    🟡 {f['file']} (分数: {f['score']}, 使用点: {f['usage_count']})")

    if impact.get("low_impact_files"):
        lines.append("\n  低影响文件:")
        for f in impact["low_impact_files"]:
            lines.append(f"    🟢 {f['file']} (分数: {f['score']}, 使用点: {f['usage_count']})")

    lines += ["", "## 建议移除步骤"]
    for step in impact.get("removal_steps", []):
        lines.append(f"  {step}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="扫描 MemoryManager 在 DocuSwarm 中的所有引用和依赖链"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径 (默认: .tmp/memory_manager_deps.json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="json",
        help="输出格式 (默认: json)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="同时打印报告到终端",
    )
    args = parser.parse_args()

    print("[INFO] 开始 MemoryManager 依赖扫描...")
    report = run_analysis()

    if args.output:
        output_path = Path(args.output)
    else:
        TMP_DIR.mkdir(exist_ok=True)
        suffix = ".txt" if args.format == "text" else ".json"
        output_path = TMP_DIR / f"memory_manager_deps{suffix}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        data = {
            "summary": report.summary,
            "import_references": [asdict(r) for r in report.import_references],
            "usage_points": [asdict(u) for u in report.usage_points],
            "dependency_graph": {
                k: asdict(v) for k, v in report.dependency_graph.items()
            },
            "removal_impact": report.removal_impact,
        }
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        text = format_text_report(report)
        output_path.write_text(text, encoding="utf-8")

    print(f"\n[DONE] 报告已保存到: {output_path}")
    print(f"[INFO] 发现 {len(report.import_references)} 个导入引用，"
          f"{len(report.usage_points)} 个使用点，"
          f"影响 {report.removal_impact.get('total_affected_files', 0)} 个文件")
    print(f"[INFO] 整体移除复杂度: {report.removal_impact.get('overall_complexity', 'unknown').upper()}")

    if args.print:
        print("\n" + format_text_report(report))


if __name__ == "__main__":
    main()
