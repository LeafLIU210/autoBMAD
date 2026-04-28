"""
Task 契约使用点扫描器 - 分析 contracts.py 定义的契约在所有模块中的使用情况

功能：
1. 分析 node_execution/contracts.py 中定义的所有 Task 相关类/接口
2. 搜索所有导入和使用这些类的模块
3. 对比 Task 契约字段与 persona.json 字段的重叠
4. 输出：使用点清单、字段重叠分析、替换可行性评估

用法：
    python tools/task_contract_usage_scanner.py
    python tools/task_contract_usage_scanner.py --output .tmp/task_contract_report.json
    python tools/task_contract_usage_scanner.py --format text --print
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
CONTRACTS_FILE = AUTOBBMAD_ROOT / "docuswarm" / "node_execution" / "contracts.py"
NODES_DIR = AUTOBBMAD_ROOT / "nodes"
TMP_DIR = PROJECT_ROOT / ".tmp"

# contracts.py 中已知的契约类
KNOWN_CONTRACT_CLASSES = [
    "NodeExecutionContext",
    "NodeExecutionContextRequired",
    "IndependentAgentInput",
    "EvaluatorAgentInput",
    "DeliverableRequirements",
    "DeliverableArtifact",
    "IndependentOutput",
    "EvaluatorOutput",
]

# persona.json 中的标准顶层字段
PERSONA_STANDARD_FIELDS = [
    "name", "role", "identity", "expertise",
    "principles", "tools", "output_format",
]


@dataclass
class ContractClass:
    """契约类定义"""
    name: str
    file: str
    line: int
    fields: list[dict[str, str]]  # [{name, type, required}]
    base_classes: list[str]
    docstring: str
    is_typed_dict: bool = False


@dataclass
class ContractImport:
    """契约导入引用"""
    file: str
    line: int
    module: str
    imported_names: list[str]


@dataclass
class ContractUsage:
    """契约使用点"""
    file: str
    line: int
    function: str
    class_name: str | None
    usage_type: str  # "type_annotation" | "instantiation" | "dict_access" | "key_access"
    contract_name: str
    code_snippet: str
    field_accessed: str | None = None  # 访问的具体字段（如 ctx["task_name"]）


@dataclass
class PersonaFieldOverlap:
    """persona.json 与契约字段重叠分析"""
    node_name: str
    persona_fields: list[str]
    contract_fields: list[str]
    overlapping_fields: list[str]
    only_in_persona: list[str]
    only_in_contract: list[str]
    overlap_ratio: float


@dataclass
class TaskContractReport:
    """Task 契约完整报告"""
    contract_definitions: list[ContractClass] = field(default_factory=list)
    import_references: list[ContractImport] = field(default_factory=list)
    usage_points: list[ContractUsage] = field(default_factory=list)
    persona_overlaps: list[PersonaFieldOverlap] = field(default_factory=list)
    replacement_feasibility: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)


class ContractDefinitionVisitor(ast.NodeVisitor):
    """从 contracts.py 提取契约类定义"""

    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.lines = source.splitlines()
        self.classes: list[ContractClass] = []

    def _get_docstring(self, node: ast.ClassDef) -> str:
        if (node.body and
                isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant)):
            return str(node.body[0].value.value)[:300]
        return ""

    def _extract_typed_dict_fields(self, node: ast.ClassDef) -> list[dict[str, str]]:
        """提取 TypedDict 的字段"""
        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                try:
                    field_name = ast.unparse(stmt.target)
                    field_type = ast.unparse(stmt.annotation) if stmt.annotation else "Any"
                    fields.append({
                        "name": field_name,
                        "type": field_type,
                        "required": True,
                    })
                except Exception:
                    pass
        return fields

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        base_names = []
        is_typed_dict = False
        for base in node.bases:
            try:
                bn = ast.unparse(base)
                base_names.append(bn)
                if "TypedDict" in bn:
                    is_typed_dict = True
            except Exception:
                pass

        # 只关注契约相关类
        if node.name in KNOWN_CONTRACT_CLASSES or is_typed_dict or "Contract" in node.name:
            fields = self._extract_typed_dict_fields(node)
            cc = ContractClass(
                name=node.name,
                file=self.file_path,
                line=node.lineno,
                fields=fields,
                base_classes=base_names,
                docstring=self._get_docstring(node),
                is_typed_dict=is_typed_dict,
            )
            self.classes.append(cc)

        self.generic_visit(node)


class ContractUsageVisitor(ast.NodeVisitor):
    """扫描 contracts 类的使用点"""

    def __init__(self, source: str, file_path: str, contract_names: set[str]):
        self.source = source
        self.file_path = file_path
        self.lines = source.splitlines()
        self.contract_names = contract_names
        self.imports: list[ContractImport] = []
        self.usages: list[ContractUsage] = []
        self._class_stack: list[str] = []
        self._func_stack: list[str] = []

    def _get_line(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.lines):
            return self.lines[lineno - 1].strip()
        return ""

    def _func_name(self) -> str:
        return ".".join(self._func_stack) if self._func_stack else "<module>"

    def _class_name(self) -> str | None:
        return self._class_stack[-1] if self._class_stack else None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def _visit_funcdef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._func_stack.append(node.name)

        # 检查函数参数类型注解
        for arg in node.args.args:
            if arg.annotation:
                try:
                    ann = ast.unparse(arg.annotation)
                    for cname in self.contract_names:
                        if cname in ann:
                            self.usages.append(ContractUsage(
                                file=self.file_path,
                                line=node.lineno,
                                function=self._func_name(),
                                class_name=self._class_name(),
                                usage_type="type_annotation",
                                contract_name=cname,
                                code_snippet=self._get_line(node.lineno)[:120],
                            ))
                except Exception:
                    pass

        # 检查返回类型注解
        if node.returns:
            try:
                ret = ast.unparse(node.returns)
                for cname in self.contract_names:
                    if cname in ret:
                        self.usages.append(ContractUsage(
                            file=self.file_path,
                            line=node.lineno,
                            function=self._func_name(),
                            class_name=self._class_name(),
                            usage_type="type_annotation",
                            contract_name=cname,
                            code_snippet=f"-> {ret}",
                        ))
            except Exception:
                pass

        self.generic_visit(node)
        self._func_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_funcdef(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_funcdef(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not node.module:
            self.generic_visit(node)
            return

        if "contracts" in node.module or "node_execution" in node.module:
            contract_names_imported = [
                alias.name for alias in node.names
                if alias.name in self.contract_names
            ]
            if contract_names_imported:
                self.imports.append(ContractImport(
                    file=self.file_path,
                    line=node.lineno,
                    module=node.module,
                    imported_names=contract_names_imported,
                ))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """检测类型注解赋值"""
        try:
            ann = ast.unparse(node.annotation)
            for cname in self.contract_names:
                if cname in ann:
                    self.usages.append(ContractUsage(
                        file=self.file_path,
                        line=node.lineno,
                        function=self._func_name(),
                        class_name=self._class_name(),
                        usage_type="type_annotation",
                        contract_name=cname,
                        code_snippet=self._get_line(node.lineno)[:120],
                    ))
        except Exception:
            pass
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """检测字典键访问 ctx["task_name"]"""
        try:
            val = ast.unparse(node.value)
            if any(hint in val for hint in ["ctx", "context", "execution_context", "input"]):
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    self.usages.append(ContractUsage(
                        file=self.file_path,
                        line=node.lineno,
                        function=self._func_name(),
                        class_name=self._class_name(),
                        usage_type="dict_access",
                        contract_name="NodeExecutionContext",
                        code_snippet=self._get_line(node.lineno)[:120],
                        field_accessed=node.slice.value,
                    ))
        except Exception:
            pass
        self.generic_visit(node)


def parse_contracts_file() -> list[ContractClass]:
    """解析 contracts.py 提取所有契约类"""
    try:
        source = CONTRACTS_FILE.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception as e:
        print(f"[ERROR] 无法解析 contracts.py: {e}", file=sys.stderr)
        return []

    rel_path = str(CONTRACTS_FILE.relative_to(PROJECT_ROOT))
    visitor = ContractDefinitionVisitor(source, rel_path)
    visitor.visit(tree)
    return visitor.classes


def scan_usages(contract_names: set[str]) -> tuple[list[ContractImport], list[ContractUsage]]:
    """扫描所有文件中的契约使用"""
    all_imports: list[ContractImport] = []
    all_usages: list[ContractUsage] = []

    py_files = list(AUTOBBMAD_ROOT.rglob("*.py"))
    print(f"[INFO] 扫描 {len(py_files)} 个 Python 文件...")

    for py_file in sorted(py_files):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        # 快速预筛：文件中是否含有契约名
        if not any(cname in source for cname in contract_names):
            continue

        rel_path = str(py_file.relative_to(PROJECT_ROOT))
        visitor = ContractUsageVisitor(source, rel_path, contract_names)
        visitor.visit(tree)

        if visitor.imports or visitor.usages:
            print(f"  [FOUND] {rel_path}: {len(visitor.imports)} 导入, {len(visitor.usages)} 使用点")

        all_imports.extend(visitor.imports)
        all_usages.extend(visitor.usages)

    return all_imports, all_usages


def load_persona_json(node_name: str) -> dict[str, Any] | None:
    """加载 persona.json"""
    persona_path = NODES_DIR / node_name / "persona.json"
    if not persona_path.exists():
        return None
    try:
        return json.loads(persona_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _flatten_fields(d: Any, prefix: str = "") -> list[str]:
    """递归提取字典的所有字段路径"""
    if not isinstance(d, dict):
        return [prefix] if prefix else []
    result = []
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        result.append(full_key)
        if isinstance(v, dict):
            result.extend(_flatten_fields(v, full_key))
    return result


def analyze_persona_overlap(contracts: list[ContractClass]) -> list[PersonaFieldOverlap]:
    """分析 persona.json 与契约字段的重叠"""
    overlaps = []
    node_names = [d.name for d in NODES_DIR.iterdir() if d.is_dir()]

    # 合并所有契约字段
    all_contract_fields = []
    for c in contracts:
        all_contract_fields.extend(f["name"] for f in c.fields)

    for node_name in node_names:
        persona = load_persona_json(node_name)
        if not persona:
            continue

        persona_fields = _flatten_fields(persona)
        contract_fields = all_contract_fields

        overlapping = [f for f in persona_fields if f in contract_fields]
        only_persona = [f for f in persona_fields if f not in contract_fields]
        only_contract = [f for f in contract_fields if f not in persona_fields]

        overlap_ratio = len(overlapping) / max(len(persona_fields), 1)

        overlaps.append(PersonaFieldOverlap(
            node_name=node_name,
            persona_fields=persona_fields,
            contract_fields=contract_fields,
            overlapping_fields=overlapping,
            only_in_persona=only_persona,
            only_in_contract=only_contract,
            overlap_ratio=round(overlap_ratio, 3),
        ))

    return overlaps


def assess_replacement_feasibility(
    contracts: list[ContractClass],
    imports: list[ContractImport],
    usages: list[ContractUsage],
    overlaps: list[PersonaFieldOverlap],
) -> dict[str, Any]:
    """评估用 persona.json 替换 Task 契约的可行性"""

    # 统计每个契约类的使用频率
    contract_usage_count: dict[str, int] = {}
    for u in usages:
        contract_usage_count[u.contract_name] = contract_usage_count.get(u.contract_name, 0) + 1

    # 统计字典访问的字段
    accessed_fields: dict[str, int] = {}
    for u in usages:
        if u.field_accessed:
            accessed_fields[u.field_accessed] = accessed_fields.get(u.field_accessed, 0) + 1

    # 识别高频访问字段
    high_freq_fields = {k: v for k, v in accessed_fields.items() if v >= 2}

    # 评估每个类的替换可行性
    class_feasibility = {}
    for c in contracts:
        usage_count = contract_usage_count.get(c.name, 0)
        has_persona_overlap = any(
            c.name in ["IndependentAgentInput"] and o.overlap_ratio > 0.2
            for o in overlaps
        )

        if c.name == "IndependentAgentInput":
            feasibility = "HIGH"
            reason = "大量字段与 persona.json 重叠，可以合并到 NodeExecutionContext 传递"
        elif c.name in ["NodeExecutionContext", "NodeExecutionContextRequired"]:
            feasibility = "LOW"
            reason = "这是核心执行协议，不应被 persona.json 替换，但可以精简字段"
        elif c.name in ["DeliverableRequirements", "DeliverableArtifact"]:
            feasibility = "MEDIUM"
            reason = "部分字段可以从 persona.json/node.yaml 的 output_format 派生"
        elif c.name in ["EvaluatorAgentInput"]:
            feasibility = "MEDIUM"
            reason = "criteria 字段可以移至 node.yaml，减少运行时契约字段"
        else:
            feasibility = "LOW"
            reason = f"使用频率: {usage_count}，移除影响较小"

        class_feasibility[c.name] = {
            "feasibility": feasibility,
            "reason": reason,
            "usage_count": usage_count,
            "field_count": len(c.fields),
        }

    return {
        "class_feasibility": class_feasibility,
        "high_frequency_fields_accessed": high_freq_fields,
        "total_dict_access_points": sum(1 for u in usages if u.usage_type == "dict_access"),
        "total_type_annotation_points": sum(1 for u in usages if u.usage_type == "type_annotation"),
        "persona_overlap_summary": [
            {
                "node": o.node_name,
                "overlap_ratio": o.overlap_ratio,
                "overlapping": o.overlapping_fields,
            }
            for o in overlaps
        ],
        "migration_recommendation": (
            "建议保留 NodeExecutionContext 作为执行协议，"
            "将 IndependentAgentInput 中的 persona 相关字段（role_supplement, persona_context）"
            "直接从 persona.json 加载，不再通过契约传递。"
            "DeliverableRequirements 可以移入 node.yaml 配置。"
        ),
    }


def run_analysis() -> TaskContractReport:
    """运行完整分析"""
    report = TaskContractReport()

    # 1. 解析契约定义
    print("[INFO] 解析 contracts.py 中的契约定义...")
    report.contract_definitions = parse_contracts_file()
    contract_names = {c.name for c in report.contract_definitions}
    print(f"  发现 {len(report.contract_definitions)} 个契约类: {', '.join(contract_names)}")

    # 2. 扫描使用点
    imports, usages = scan_usages(contract_names)
    report.import_references = imports
    report.usage_points = usages

    # 3. persona 字段重叠分析
    print("[INFO] 分析 persona.json 字段重叠...")
    report.persona_overlaps = analyze_persona_overlap(report.contract_definitions)

    # 4. 替换可行性评估
    print("[INFO] 评估替换可行性...")
    report.replacement_feasibility = assess_replacement_feasibility(
        report.contract_definitions,
        report.import_references,
        report.usage_points,
        report.persona_overlaps,
    )

    # 汇总
    files_with_imports = list({ref.file for ref in imports})
    report.summary = {
        "contracts_defined": len(report.contract_definitions),
        "contract_names": list(contract_names),
        "files_importing_contracts": files_with_imports,
        "total_import_references": len(imports),
        "total_usage_points": len(usages),
        "usage_by_type": {
            utype: sum(1 for u in usages if u.usage_type == utype)
            for utype in {"type_annotation", "instantiation", "dict_access", "key_access"}
        },
        "contracts_field_summary": [
            {"name": c.name, "fields": [f["name"] for f in c.fields], "is_typed_dict": c.is_typed_dict}
            for c in report.contract_definitions
        ],
        "nodes_analyzed_for_persona": [o.node_name for o in report.persona_overlaps],
    }

    return report


def format_text_report(report: TaskContractReport) -> str:
    """格式化文本报告"""
    lines = [
        "=" * 70,
        "Task 契约使用点扫描报告",
        "=" * 70,
        "",
        "## 摘要统计",
        f"  - 契约类数量: {report.summary.get('contracts_defined', 0)}",
        f"  - 导入引用总数: {report.summary.get('total_import_references', 0)}",
        f"  - 使用点总数: {report.summary.get('total_usage_points', 0)}",
        f"  - 导入文件数: {len(report.summary.get('files_importing_contracts', []))}",
        "",
        "## 契约类定义",
    ]

    for c in report.contract_definitions:
        lines.append(f"\n  [{c.name}] (L{c.line}, TypedDict={c.is_typed_dict})")
        lines.append(f"    基类: {', '.join(c.base_classes)}")
        for f in c.fields:
            lines.append(f"    - {f['name']}: {f['type']}")

    lines += ["", "## 导入清单"]
    for ref in sorted(report.import_references, key=lambda x: x.file):
        lines.append(
            f"  {ref.file}:L{ref.line} — from {ref.module} import {', '.join(ref.imported_names)}"
        )

    lines += ["", "## 使用点（类型注解）"]
    for u in sorted(report.usage_points, key=lambda x: (x.file, x.line)):
        if u.usage_type == "type_annotation":
            cls = f"{u.class_name}." if u.class_name else ""
            lines.append(f"  {u.file}:L{u.line} [{cls}{u.function}] → {u.contract_name}")

    lines += ["", "## 字典键访问点（高风险，直接耦合到字段名）"]
    dict_accesses = [u for u in report.usage_points if u.usage_type == "dict_access"]
    if dict_accesses:
        field_count: dict[str, int] = {}
        for u in dict_accesses:
            if u.field_accessed:
                field_count[u.field_accessed] = field_count.get(u.field_accessed, 0) + 1
        for field_name, count in sorted(field_count.items(), key=lambda x: -x[1]):
            lines.append(f"  '{field_name}': 访问 {count} 次")
    else:
        lines.append("  (无字典键访问)")

    lines += ["", "## Persona.json 字段重叠分析"]
    for o in report.persona_overlaps:
        lines.append(f"\n  [{o.node_name}] 重叠率: {o.overlap_ratio:.1%}")
        if o.overlapping_fields:
            lines.append(f"    重叠字段: {', '.join(o.overlapping_fields)}")

    lines += ["", "## 替换可行性评估"]
    for cname, info in report.replacement_feasibility.get("class_feasibility", {}).items():
        marker = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(info["feasibility"], "⚪")
        lines.append(f"\n  {marker} {cname} [可行性: {info['feasibility']}]")
        lines.append(f"    {info['reason']}")

    rec = report.replacement_feasibility.get("migration_recommendation", "")
    if rec:
        lines += ["", "## 迁移建议", f"  {rec}"]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="扫描 Task 契约在 DocuSwarm 中的使用点和 persona 字段重叠"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径 (默认: .tmp/task_contract_report.json)",
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

    print("[INFO] 开始 Task 契约使用点扫描...")
    report = run_analysis()

    if args.output:
        output_path = Path(args.output)
    else:
        TMP_DIR.mkdir(exist_ok=True)
        suffix = ".txt" if args.format == "text" else ".json"
        output_path = TMP_DIR / f"task_contract_report{suffix}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        data = {
            "summary": report.summary,
            "contract_definitions": [asdict(c) for c in report.contract_definitions],
            "import_references": [asdict(r) for r in report.import_references],
            "usage_points": [asdict(u) for u in report.usage_points],
            "persona_overlaps": [asdict(o) for o in report.persona_overlaps],
            "replacement_feasibility": report.replacement_feasibility,
        }
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        text = format_text_report(report)
        output_path.write_text(text, encoding="utf-8")

    print(f"\n[DONE] 报告已保存到: {output_path}")
    print(f"[INFO] 发现 {len(report.contract_definitions)} 个契约类，"
          f"{len(report.import_references)} 个导入，"
          f"{len(report.usage_points)} 个使用点")

    if args.print:
        print("\n" + format_text_report(report))


if __name__ == "__main__":
    main()
