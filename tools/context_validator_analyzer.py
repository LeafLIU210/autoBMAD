"""
ContextValidator 分析器 - 诊断验证逻辑的内联分布与耦合关系

功能：
1. 扫描 autoBMAD/docuswarm/ 下所有 .py 文件
2. 使用 AST 解析查找所有 validation/verify/check 相关的方法和函数
3. 特别关注 pipeline/orchestrator.py 和 context/isolation.py 中的验证逻辑
4. 输出：验证逻辑的位置清单、耦合关系、建议提取的方法列表

用法：
    python tools/context_validator_analyzer.py
    python tools/context_validator_analyzer.py --output .tmp/context_validator_report.json
    python tools/context_validator_analyzer.py --focus orchestrator
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
DOCUSWARM_SRC = PROJECT_ROOT / "autoBMAD" / "docuswarm"
TMP_DIR = PROJECT_ROOT / ".tmp"

# 验证相关的关键词模式
VALIDATION_KEYWORDS = [
    "valid", "validate", "validation",
    "verify", "verification",
    "check", "checker",
    "assert",
    "ensure",
    "inspect",
]

# 重点关注的文件
FOCUS_FILES = [
    "pipeline/orchestrator.py",
    "context/isolation.py",
    "node_execution/validator.py",
    "node_execution/contracts.py",
]


@dataclass
class ValidationMethod:
    """验证方法信息"""
    name: str
    file: str
    line_start: int
    line_end: int
    is_async: bool
    decorators: list[str]
    args: list[str]
    raises: list[str]
    calls_methods: list[str]
    docstring: str
    category: str  # "standalone", "class_method", "static_method"
    class_name: str | None = None


@dataclass
class ValidationCallSite:
    """验证方法调用点"""
    caller_file: str
    caller_function: str
    called_name: str
    line: int
    call_args_count: int
    is_inline: bool  # 是否是内联验证逻辑（不复用方法）


@dataclass
class CouplingRelation:
    """耦合关系"""
    source_file: str
    source_function: str
    target_file: str
    target_function: str
    coupling_type: str  # "import", "call", "inheritance"


@dataclass
class ValidationReport:
    """完整验证分析报告"""
    files_analyzed: int = 0
    validation_methods: list[ValidationMethod] = field(default_factory=list)
    call_sites: list[ValidationCallSite] = field(default_factory=list)
    coupling_relations: list[CouplingRelation] = field(default_factory=list)
    inline_validation_patterns: list[dict[str, Any]] = field(default_factory=list)
    extraction_candidates: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class ValidationASTVisitor(ast.NodeVisitor):
    """AST 访问器：提取验证相关信息"""

    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.lines = source.splitlines()
        self.validation_methods: list[ValidationMethod] = []
        self.call_sites: list[ValidationCallSite] = []
        self.inline_patterns: list[dict[str, Any]] = []
        self._class_stack: list[str] = []
        self._func_stack: list[str] = []

    def _is_validation_name(self, name: str) -> bool:
        """检查名称是否与验证相关"""
        name_lower = name.lower()
        return any(kw in name_lower for kw in VALIDATION_KEYWORDS)

    def _extract_raises(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        """提取函数中抛出的异常类型"""
        raises = []
        for child in ast.walk(node):
            if isinstance(child, ast.Raise) and child.exc is not None:
                exc = child.exc
                if isinstance(exc, ast.Call):
                    if isinstance(exc.func, ast.Name):
                        raises.append(exc.func.id)
                    elif isinstance(exc.func, ast.Attribute):
                        raises.append(exc.func.attr)
                elif isinstance(exc, ast.Name):
                    raises.append(exc.id)
        return list(set(raises))

    def _extract_calls(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        """提取函数中调用的方法名称"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
                elif isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
        # 过滤出验证相关的调用
        return [c for c in calls if self._is_validation_name(c)]

    def _get_docstring(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """获取函数 docstring"""
        if (node.body and
                isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant)):
            return str(node.body[0].value.value)[:200]
        return ""

    def _detect_inline_validation(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[dict[str, Any]]:
        """检测函数内部的内联验证模式（if/raise 组合）"""
        patterns = []
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # 检查 if ... raise 模式
                raises_in_if = [n for n in ast.walk(child) if isinstance(n, ast.Raise)]
                if raises_in_if:
                    # 检查条件是否含验证语义
                    condition_src = ""
                    try:
                        condition_src = ast.unparse(child.test)
                    except Exception:
                        pass
                    if any(kw in condition_src.lower() for kw in ["not", "none", "invalid", "missing", "empty"]):
                        patterns.append({
                            "type": "inline_guard",
                            "file": self.file_path,
                            "function": ".".join(self._func_stack),
                            "line": child.lineno,
                            "condition": condition_src[:100],
                            "raises": [
                                ast.unparse(r.exc)[:60] if r.exc else "unknown"
                                for r in raises_in_if
                            ],
                        })
        return patterns

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def _visit_funcdef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        func_name = node.name
        self._func_stack.append(func_name)

        # 检查是否为验证方法
        if self._is_validation_name(func_name):
            args = [arg.arg for arg in node.args.args if arg.arg != "self"]
            decorators = []
            for d in node.decorator_list:
                try:
                    decorators.append(ast.unparse(d))
                except Exception:
                    pass

            category = "standalone"
            if self._class_stack:
                if any("staticmethod" in d for d in decorators):
                    category = "static_method"
                else:
                    category = "class_method"

            vm = ValidationMethod(
                name=func_name,
                file=self.file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                is_async=isinstance(node, ast.AsyncFunctionDef),
                decorators=decorators,
                args=args,
                raises=self._extract_raises(node),
                calls_methods=self._extract_calls(node),
                docstring=self._get_docstring(node),
                category=category,
                class_name=self._class_stack[-1] if self._class_stack else None,
            )
            self.validation_methods.append(vm)

        # 检测内联验证
        inline = self._detect_inline_validation(node)
        self.inline_patterns.extend(inline)

        self.generic_visit(node)
        self._func_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_funcdef(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_funcdef(node)

    def visit_Call(self, node: ast.Call) -> None:
        """捕捉验证相关的调用点"""
        called_name = ""
        if isinstance(node.func, ast.Attribute):
            called_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            called_name = node.func.id

        if called_name and self._is_validation_name(called_name):
            caller_func = ".".join(self._func_stack) if self._func_stack else "<module>"
            cs = ValidationCallSite(
                caller_file=self.file_path,
                caller_function=caller_func,
                called_name=called_name,
                line=node.lineno,
                call_args_count=len(node.args) + len(node.keywords),
                is_inline=False,  # 有命名方法
            )
            self.call_sites.append(cs)

        self.generic_visit(node)


def analyze_file(file_path: Path, base_dir: Path) -> tuple[
    list[ValidationMethod],
    list[ValidationCallSite],
    list[dict[str, Any]]
]:
    """分析单个 Python 文件"""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  [WARN] 跳过文件 {file_path}: {e}", file=sys.stderr)
        return [], [], []

    rel_path = str(file_path.relative_to(base_dir))
    visitor = ValidationASTVisitor(source, rel_path)
    visitor.visit(tree)
    return visitor.validation_methods, visitor.call_sites, visitor.inline_patterns


def analyze_imports_coupling(file_path: Path, base_dir: Path) -> list[CouplingRelation]:
    """分析文件中与验证相关的导入耦合"""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    rel_path = str(file_path.relative_to(base_dir))
    relations = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = ""
            names = []
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]

            # 检查是否导入验证相关符号
            for name in names:
                if any(kw in (module + "." + name).lower() for kw in VALIDATION_KEYWORDS):
                    relations.append(CouplingRelation(
                        source_file=rel_path,
                        source_function="<import>",
                        target_file=module.replace(".", "/") + ".py",
                        target_function=name,
                        coupling_type="import",
                    ))

    return relations


def identify_extraction_candidates(
    methods: list[ValidationMethod],
    inline_patterns: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """识别可提取为独立验证器的候选方法"""
    candidates = []

    # 候选1：在多个文件中重复出现的验证逻辑
    name_count: dict[str, int] = {}
    for m in methods:
        name_count[m.name] = name_count.get(m.name, 0) + 1

    for name, count in name_count.items():
        if count > 1:
            files = [m.file for m in methods if m.name == name]
            candidates.append({
                "type": "duplicated_method",
                "name": name,
                "occurrence_count": count,
                "files": files,
                "recommendation": f"方法 '{name}' 在 {count} 个文件中重复定义，建议提取到 context/validators.py",
                "priority": "high",
            })

    # 候选2：内联验证密度高的文件
    file_inline_count: dict[str, int] = {}
    for p in inline_patterns:
        f = p["file"]
        file_inline_count[f] = file_inline_count.get(f, 0) + 1

    for f, count in file_inline_count.items():
        if count >= 3:
            candidates.append({
                "type": "inline_validation_cluster",
                "file": f,
                "inline_count": count,
                "recommendation": f"文件 '{f}' 有 {count} 处内联验证逻辑，建议抽取为独立方法",
                "priority": "medium" if count < 6 else "high",
            })

    # 候选3：在 orchestrator 中的验证逻辑（属于 context 层职责）
    orch_methods = [m for m in methods if "orchestrator" in m.file]
    if orch_methods:
        candidates.append({
            "type": "misplaced_validation",
            "file": "pipeline/orchestrator.py",
            "methods": [m.name for m in orch_methods],
            "recommendation": "Orchestrator 不应包含验证逻辑，建议迁移到 context/validators.py",
            "priority": "high",
        })

    return candidates


def run_analysis(focus_filter: str | None = None) -> ValidationReport:
    """运行完整分析"""
    report = ValidationReport()

    py_files = list(DOCUSWARM_SRC.rglob("*.py"))
    if focus_filter:
        py_files = [f for f in py_files if focus_filter in str(f)]

    print(f"[INFO] 扫描 {len(py_files)} 个 Python 文件...")

    all_methods: list[ValidationMethod] = []
    all_call_sites: list[ValidationCallSite] = []
    all_inline: list[dict[str, Any]] = []
    all_coupling: list[CouplingRelation] = []

    for py_file in sorted(py_files):
        methods, calls, inline = analyze_file(py_file, PROJECT_ROOT)
        coupling = analyze_imports_coupling(py_file, PROJECT_ROOT)
        all_methods.extend(methods)
        all_call_sites.extend(calls)
        all_inline.extend(inline)
        all_coupling.extend(coupling)

        if methods or inline:
            rel = str(py_file.relative_to(PROJECT_ROOT))
            print(f"  [OK] {rel}: {len(methods)} 验证方法, {len(inline)} 内联模式")

    report.files_analyzed = len(py_files)
    report.validation_methods = all_methods
    report.call_sites = all_call_sites
    report.inline_validation_patterns = all_inline
    report.coupling_relations = all_coupling
    report.extraction_candidates = identify_extraction_candidates(all_methods, all_inline)

    # 汇总统计
    focus_files_stats = {}
    for ff in FOCUS_FILES:
        ff_methods = [m for m in all_methods if ff in m.file]
        ff_inline = [p for p in all_inline if ff in p["file"]]
        focus_files_stats[ff] = {
            "validation_methods": len(ff_methods),
            "inline_patterns": len(ff_inline),
            "method_names": [m.name for m in ff_methods],
        }

    report.summary = {
        "total_files_analyzed": len(py_files),
        "total_validation_methods": len(all_methods),
        "total_call_sites": len(all_call_sites),
        "total_inline_patterns": len(all_inline),
        "total_coupling_relations": len(all_coupling),
        "high_priority_extractions": sum(
            1 for c in report.extraction_candidates if c.get("priority") == "high"
        ),
        "focus_files_stats": focus_files_stats,
        "files_with_most_validation": sorted(
            [{"file": f, "count": c}
             for f, c in {
                 m.file: sum(1 for x in all_methods if x.file == m.file)
                 for m in all_methods
             }.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10],
    }

    return report


def format_text_report(report: ValidationReport) -> str:
    """格式化文本报告"""
    lines = [
        "=" * 70,
        "ContextValidator 分析报告",
        "=" * 70,
        "",
        "## 摘要统计",
        f"  - 分析文件数: {report.summary.get('total_files_analyzed', 0)}",
        f"  - 验证方法总数: {report.summary.get('total_validation_methods', 0)}",
        f"  - 调用点总数: {report.summary.get('total_call_sites', 0)}",
        f"  - 内联验证模式: {report.summary.get('total_inline_patterns', 0)}",
        f"  - 耦合关系数: {report.summary.get('total_coupling_relations', 0)}",
        f"  - 高优先级提取候选: {report.summary.get('high_priority_extractions', 0)}",
        "",
        "## 重点文件分析",
    ]

    for ff, stats in report.summary.get("focus_files_stats", {}).items():
        lines.append(f"\n  [{ff}]")
        lines.append(f"    验证方法: {stats['validation_methods']}")
        lines.append(f"    内联模式: {stats['inline_patterns']}")
        if stats["method_names"]:
            lines.append(f"    方法名: {', '.join(stats['method_names'])}")

    lines += ["", "## 验证方法清单 (按文件)"]
    current_file = None
    for m in sorted(report.validation_methods, key=lambda x: x.file):
        if m.file != current_file:
            current_file = m.file
            lines.append(f"\n  [{current_file}]")
        prefix = "async " if m.is_async else ""
        class_prefix = f"{m.class_name}." if m.class_name else ""
        lines.append(f"    L{m.line_start}: {prefix}{class_prefix}{m.name}({', '.join(m.args)})")
        if m.raises:
            lines.append(f"      → 抛出: {', '.join(m.raises)}")

    lines += ["", "## 内联验证模式 (需要提取)"]
    for p in report.inline_validation_patterns:
        lines.append(
            f"  {p['file']}:{p['line']} [{p['function']}]"
            f"\n    条件: {p['condition']}"
            f"\n    抛出: {', '.join(p['raises'])}"
        )

    lines += ["", "## 提取候选建议"]
    for c in report.extraction_candidates:
        priority_marker = "🔴" if c.get("priority") == "high" else "🟡"
        lines.append(f"\n  {priority_marker} [{c['type']}]")
        lines.append(f"    {c['recommendation']}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="分析 ContextValidator 在 DocuSwarm 中的内联使用情况和耦合关系"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径 (支持 .json 或 .txt，默认输出到 .tmp/context_validator_report.json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="json",
        help="输出格式 (默认: json)",
    )
    parser.add_argument(
        "--focus",
        type=str,
        default=None,
        help="过滤只分析包含此字符串的文件路径 (例如: orchestrator)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="同时打印报告到终端",
    )
    args = parser.parse_args()

    print("[INFO] 开始 ContextValidator 分析...")
    report = run_analysis(focus_filter=args.focus)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        TMP_DIR.mkdir(exist_ok=True)
        suffix = ".txt" if args.format == "text" else ".json"
        output_path = TMP_DIR / f"context_validator_report{suffix}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        def _convert(obj: Any) -> Any:
            if hasattr(obj, "__dict__"):
                return asdict(obj) if hasattr(obj, "__dataclass_fields__") else obj.__dict__
            return str(obj)

        data = {
            "summary": report.summary,
            "validation_methods": [asdict(m) for m in report.validation_methods],
            "call_sites": [asdict(c) for c in report.call_sites],
            "inline_validation_patterns": report.inline_validation_patterns,
            "coupling_relations": [asdict(r) for r in report.coupling_relations],
            "extraction_candidates": report.extraction_candidates,
        }
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        text = format_text_report(report)
        output_path.write_text(text, encoding="utf-8")

    print(f"\n[DONE] 报告已保存到: {output_path}")
    print(f"[INFO] 共发现 {len(report.validation_methods)} 个验证方法，"
          f"{len(report.inline_validation_patterns)} 处内联验证，"
          f"{len(report.extraction_candidates)} 个提取候选")

    if args.print:
        print("\n" + format_text_report(report))


if __name__ == "__main__":
    main()
