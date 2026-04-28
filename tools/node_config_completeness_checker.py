"""
节点配置完整性检查器 - 对比 _bmad 核心配置与 autoBMAD/nodes 节点配置的完整性

功能：
1. 读取 autoBMAD/nodes/{analyst,pm,ux,architect,po}/ 中的 node.yaml、persona.json、evaluator.yaml
2. 读取 _bmad/_config/ 中的 agent 角色定义 (customize.yaml)
3. 对比每个节点的配置完整度（缺少哪些字段、多余哪些字段）
4. 生成每个节点的配置差距报告

用法：
    python tools/node_config_completeness_checker.py
    python tools/node_config_completeness_checker.py --output .tmp/node_config_report.json
    python tools/node_config_completeness_checker.py --node analyst
    python tools/node_config_completeness_checker.py --format text --print
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Fix Windows console encoding (only when not running under pytest)
if sys.platform == "win32" and "pytest" not in sys.modules:
    try:
        if hasattr(sys.stdout, "buffer") and sys.stdout.isatty():
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer") and sys.stderr.isatty():
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass  # Fallback if stream manipulation fails

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("[WARN] PyYAML 未安装，将使用简单解析器解析 YAML 文件", file=sys.stderr)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NODES_DIR = PROJECT_ROOT / "autoBMAD" / "nodes"
BMAD_CONFIG_DIR = PROJECT_ROOT / "_bmad" / "_config"
BMAD_AGENTS_DIR = BMAD_CONFIG_DIR / "agents"
TMP_DIR = PROJECT_ROOT / ".tmp"

# node.yaml v2 标准字段规范 (Story 26.7)
NODE_YAML_REQUIRED_FIELDS = {
    "node_id": "节点唯一标识符",
    "name": "节点显示名称",
    "description": "节点描述",
    "sequence": "执行顺序",
    "deliverable_type": "交付物类型",
    "deliverable": "交付物配置",
    "agent": "Agent 配置",
    "dependencies": "依赖节点列表",
    "task": "任务配置（v2 必填）",
}

# v2 schema 必填嵌套字段 - Story 26.7
NODE_YAML_V2_REQUIRED_NESTED = {
    "task.name": "task 配置中的 name 字段（v2 必填）",
    "task.description": "task 配置中的 description 字段（v2 必填）",
}

NODE_YAML_OPTIONAL_FIELDS = {
    "questions": "CLI 交互问题",
    "evaluator": "评估器配置（可来自 evaluator.yaml）",
    "runtime": "运行时配置（v2）",
    "schema_version": "配置模式版本（v2 默认 2.0）",
    "timeout": "执行超时（已废弃，使用 runtime.timeout）",
    "retry": "重试配置（已废弃，使用 runtime.retry_*）",
}

# persona.json v2 标准字段规范 (Story 26.7)
PERSONA_REQUIRED_FIELDS = {
    "name": "角色名称",
    "role": "角色职位",
    "identity": "身份描述（系统提示词核心）",
    "expertise": "专业能力列表",
    "principles": "工作原则列表",
}

# v2 schema 必填字段 - Story 26.7
PERSONA_V2_REQUIRED_FIELDS = {
    "communication_style": "沟通风格对象（v2 必填）",
}

PERSONA_OPTIONAL_FIELDS = {
    "tools": "可用工具列表",
    "output_format": "输出格式定义",
    "critical_actions": "关键行动",
    "memories": "持久记忆",
}

# evaluator.yaml 标准字段规范 (Story 26.7)
EVALUATOR_YAML_REQUIRED_FIELDS = {
    "criteria": "评估标准列表",
}

EVALUATOR_YAML_OPTIONAL_FIELDS = {
    "threshold": "通过阈值（v2 单数形式）",
    "max_iterations": "最大迭代次数",
    "model": "评估模型",
}

# 已废弃字段检测 - Story 26.7
EVALUATOR_DEPRECATED_FIELDS = {
    "thresholds": "thresholds 已废弃，请使用单数形式 threshold",
}

# _bmad customize.yaml 标准字段规范
BMAD_CUSTOMIZE_REQUIRED_FIELDS = {
    "agent": "Agent 元数据",
    "persona": "Persona 配置",
}

BMAD_CUSTOMIZE_OPTIONAL_FIELDS = {
    "critical_actions": "关键行动",
    "memories": "持久记忆",
    "menu": "菜单项",
    "prompts": "自定义提示词",
}

# 节点到 _bmad agent 名称的映射
NODE_TO_BMAD_AGENT_MAP = {
    "analyst": "bmm-analyst",
    "pm": "bmm-pm",
    "ux": "bmm-ux-designer",
    "architect": "bmm-architect",
    "po": "bmm-po",
}


def load_yaml_safe(file_path: Path) -> dict[str, Any]:
    """安全加载 YAML 文件"""
    if not file_path.exists():
        return {}
    try:
        content = file_path.read_text(encoding="utf-8")
        if HAS_YAML:
            result = yaml.safe_load(content)
            return result if isinstance(result, dict) else {}
        else:
            # 简单 YAML 解析（仅支持顶层键）
            result: dict[str, Any] = {}
            for line in content.splitlines():
                line = line.rstrip()
                if line and not line.startswith("#") and ":" in line and not line.startswith(" "):
                    key = line.split(":")[0].strip()
                    result[key] = "__parsed__"
            return result
    except Exception as e:
        print(f"  [WARN] 无法解析 {file_path}: {e}", file=sys.stderr)
        return {}


def load_json_safe(file_path: Path) -> dict[str, Any]:
    """安全加载 JSON 文件"""
    if not file_path.exists():
        return {}
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [WARN] 无法解析 {file_path}: {e}", file=sys.stderr)
        return {}


def get_relative_path(file_path: Path) -> str:
    """Get path relative to PROJECT_ROOT, or just filename if not under PROJECT_ROOT"""
    try:
        return str(file_path.relative_to(PROJECT_ROOT))
    except ValueError:
        # File is not under PROJECT_ROOT (e.g., temp files in tests)
        return file_path.name


def get_nested_value(data: dict[str, Any], path: str) -> tuple[bool, Any]:
    """
    获取嵌套字典中的值
    返回: (是否存在, 值)
    """
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False, None
    return True, current


def is_non_empty(value: Any) -> bool:
    """检查值是否非空"""
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


@dataclass
class FieldGap:
    """字段差距"""
    field_name: str
    gap_type: str  # "missing_required" | "missing_optional" | "extra_field" | "value_mismatch" | "deprecated_field"
    description: str
    severity: str  # "critical" | "warning" | "info"
    suggestion: str


@dataclass
class FileReport:
    """单个配置文件报告"""
    file_path: str
    exists: bool
    fields_present: list[str]
    required_missing: list[str]
    optional_missing: list[str]
    extra_fields: list[str]
    gaps: list[FieldGap]
    completeness_score: float  # 0.0 - 1.0
    v2_compliance_score: float  # Story 26.7: v2 schema compliance
    deprecated_fields_found: list[str]  # Story 26.7: deprecated fields
    parse_error: str | None = None


@dataclass
class CrossFileConsistency:
    """跨文件一致性检查"""
    check_name: str
    status: str  # "ok" | "warning" | "error"
    details: str
    files_involved: list[str]


@dataclass
class NodeConfigReport:
    """单个节点的配置报告"""
    node_name: str
    node_dir: str
    node_yaml: FileReport
    persona_json: FileReport
    evaluator_yaml: FileReport
    bmad_customize: FileReport
    cross_file_checks: list[CrossFileConsistency]
    overall_score: float
    v2_compliance_score: float  # Story 26.7
    critical_issues: list[str]
    recommendations: list[str]


@dataclass
class NodeConfigCompletenessReport:
    """完整的节点配置完整性报告"""
    nodes: list[NodeConfigReport] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


def check_file_completeness_v2(
    actual: dict[str, Any],
    required_fields: dict[str, str],
    optional_fields: dict[str, str],
    v2_nested_required: dict[str, str] | None,
    deprecated_fields: dict[str, str] | None,
    file_path: Path,
) -> FileReport:
    """
    检查单个配置文件的完整性 (v2 schema - Story 26.7)

    Args:
        actual: 实际解析的数据
        required_fields: 顶层必填字段
        optional_fields: 顶层可选字段
        v2_nested_required: v2 必填嵌套字段 (如 task.name)
        deprecated_fields: 已废弃字段检测
        file_path: 文件路径
    """
    exists = file_path.exists()
    parse_error = None
    deprecated_found: list[str] = []

    if not exists:
        all_required = list(required_fields.keys())
        if v2_nested_required:
            all_required.extend(v2_nested_required.keys())
        gaps = [
            FieldGap(
                field_name=k,
                gap_type="missing_required",
                description=v,
                severity="critical",
                suggestion=f"文件 {file_path.name} 不存在，需要创建",
            )
            for k, v in {**required_fields, **(v2_nested_required or {})}.items()
        ]
        return FileReport(
            file_path=get_relative_path(file_path),
            exists=False,
            fields_present=[],
            required_missing=all_required,
            optional_missing=list(optional_fields.keys()),
            extra_fields=[],
            gaps=gaps,
            completeness_score=0.0,
            v2_compliance_score=0.0,
            deprecated_fields_found=[],
            parse_error="文件不存在",
        )

    present = list(actual.keys())
    required_missing = [k for k in required_fields if k not in actual]
    optional_missing = [k for k in optional_fields if k not in actual]
    all_known = set(required_fields) | set(optional_fields)
    extra_fields = [k for k in present if k not in all_known]

    gaps: list[FieldGap] = []
    v2_gaps: list[FieldGap] = []

    # 检查顶层必填字段
    for k in required_missing:
        gaps.append(FieldGap(
            field_name=k,
            gap_type="missing_required",
            description=required_fields[k],
            severity="critical",
            suggestion=f"添加必填字段 '{k}': {required_fields[k]}",
        ))

    # 检查可选字段
    for k in optional_missing:
        gaps.append(FieldGap(
            field_name=k,
            gap_type="missing_optional",
            description=optional_fields[k],
            severity="warning",
            suggestion=f"考虑添加可选字段 '{k}': {optional_fields[k]}",
        ))

    # 检查扩展字段
    for k in extra_fields:
        # 检查是否是已废弃字段 - Story 26.7
        if deprecated_fields and k in deprecated_fields:
            gaps.append(FieldGap(
                field_name=k,
                gap_type="deprecated_field",
                description=deprecated_fields[k],
                severity="critical",
                suggestion=f"移除已废弃字段 '{k}': {deprecated_fields[k]}",
            ))
            deprecated_found.append(k)
        else:
            gaps.append(FieldGap(
                field_name=k,
                gap_type="extra_field",
                description=f"非标准字段 '{k}'",
                severity="info",
                suggestion=f"确认字段 '{k}' 是否为自定义扩展或拼写错误",
            ))

    # 检查 v2 必填嵌套字段 - Story 26.7
    v2_nested_missing: list[str] = []
    if v2_nested_required:
        for field_path, description in v2_nested_required.items():
            exists_in_data, value = get_nested_value(actual, field_path)
            if not exists_in_data or not is_non_empty(value):
                v2_nested_missing.append(field_path)
                v2_gaps.append(FieldGap(
                    field_name=field_path,
                    gap_type="missing_required",
                    description=description,
                    severity="critical",
                    suggestion=f"添加 v2 必填嵌套字段 '{field_path}': {description}",
                ))

    # 检查已废弃字段（即使不在 extra_fields 中，也要检查所有实际数据）- Story 26.7
    if deprecated_fields:
        for key in actual.keys():
            if key in deprecated_fields and key not in deprecated_found:
                gaps.append(FieldGap(
                    field_name=key,
                    gap_type="deprecated_field",
                    description=deprecated_fields[key],
                    severity="critical",
                    suggestion=f"移除已废弃字段 '{key}': {deprecated_fields[key]}",
                ))
                deprecated_found.append(key)

    # 计算完整度分数（基于顶层必填字段）
    total_required = len(required_fields)
    present_required = total_required - len(required_missing)
    score = present_required / max(total_required, 1)

    # 计算 v2 compliance 分数 - Story 26.7
    # 包含顶层必填和 v2 嵌套必填
    total_v2_required = len(required_fields) + len(v2_nested_required or {})
    present_v2_required = present_required + (len(v2_nested_required or {}) - len(v2_nested_missing))
    v2_score = present_v2_required / max(total_v2_required, 1)

    # 合并所有 gaps
    all_gaps = gaps + v2_gaps

    return FileReport(
        file_path=get_relative_path(file_path),
        exists=True,
        fields_present=present,
        required_missing=required_missing + v2_nested_missing,
        optional_missing=optional_missing,
        extra_fields=extra_fields,
        gaps=all_gaps,
        completeness_score=round(score, 3),
        v2_compliance_score=round(v2_score, 3),
        deprecated_fields_found=deprecated_found,
    )


def check_cross_file_consistency(
    node_name: str,
    node_yaml: dict[str, Any],
    persona_json: dict[str, Any],
    evaluator_yaml: dict[str, Any],
) -> list[CrossFileConsistency]:
    """检查跨文件一致性"""
    checks: list[CrossFileConsistency] = []

    # 检查1: node.yaml 的 deliverable.required_sections 与 persona.json 的 output_format.sections 一致性
    node_sections = []
    if isinstance(node_yaml.get("deliverable"), dict):
        node_sections = node_yaml["deliverable"].get("required_sections", [])

    persona_sections = []
    if isinstance(persona_json.get("output_format"), dict):
        persona_sections = persona_json["output_format"].get("sections", [])

    if node_sections and persona_sections:
        node_set = set(node_sections)
        persona_set = set(persona_sections)
        if node_set == persona_set:
            checks.append(CrossFileConsistency(
                check_name="deliverable_sections_consistency",
                status="ok",
                details=f"node.yaml 和 persona.json 的 sections 字段一致 ({len(node_sections)} 个)",
                files_involved=["node.yaml", "persona.json"],
            ))
        else:
            only_node = node_set - persona_set
            only_persona = persona_set - node_set
            details = []
            if only_node:
                details.append(f"只在 node.yaml: {sorted(only_node)}")
            if only_persona:
                details.append(f"只在 persona.json: {sorted(only_persona)}")
            checks.append(CrossFileConsistency(
                check_name="deliverable_sections_consistency",
                status="warning",
                details="sections 字段不一致: " + "; ".join(details),
                files_involved=["node.yaml", "persona.json"],
            ))
    elif node_sections or persona_sections:
        checks.append(CrossFileConsistency(
            check_name="deliverable_sections_consistency",
            status="warning",
            details=f"只有一个文件定义了 sections (node.yaml: {bool(node_sections)}, persona.json: {bool(persona_sections)})",
            files_involved=["node.yaml", "persona.json"],
        ))

    # 检查2: node.yaml 的 deliverable_type 与 persona.json 的 output_format.type 一致性
    node_deliverable_type = node_yaml.get("deliverable_type", "")
    persona_output_type = ""
    if isinstance(persona_json.get("output_format"), dict):
        persona_output_type = persona_json["output_format"].get("type", "")

    if node_deliverable_type and persona_output_type:
        if node_deliverable_type == persona_output_type:
            checks.append(CrossFileConsistency(
                check_name="deliverable_type_consistency",
                status="ok",
                details=f"deliverable_type '{node_deliverable_type}' 一致",
                files_involved=["node.yaml", "persona.json"],
            ))
        else:
            checks.append(CrossFileConsistency(
                check_name="deliverable_type_consistency",
                status="error",
                details=f"类型不一致: node.yaml='{node_deliverable_type}', persona.json='{persona_output_type}'",
                files_involved=["node.yaml", "persona.json"],
            ))

    # 检查3: node.yaml 的 agent.type 字段
    agent_config = node_yaml.get("agent", {})
    if isinstance(agent_config, dict):
        agent_type = agent_config.get("type", "")
        if agent_type in ("independent", "dual"):
            checks.append(CrossFileConsistency(
                check_name="agent_type_valid",
                status="ok",
                details=f"agent.type='{agent_type}' 是有效值",
                files_involved=["node.yaml"],
            ))
        elif agent_type:
            checks.append(CrossFileConsistency(
                check_name="agent_type_valid",
                status="warning",
                details=f"agent.type='{agent_type}' 不是已知有效值 (expected: 'independent' | 'dual')",
                files_involved=["node.yaml"],
            ))

    # 检查4: evaluator.yaml 是否存在（有 evaluator 时）
    if not evaluator_yaml:
        checks.append(CrossFileConsistency(
            check_name="evaluator_config_exists",
            status="warning",
            details="evaluator.yaml 不存在或为空，将无法进行质量评估",
            files_involved=["evaluator.yaml"],
        ))
    else:
        checks.append(CrossFileConsistency(
            check_name="evaluator_config_exists",
            status="ok",
            details=f"evaluator.yaml 存在，包含字段: {', '.join(evaluator_yaml.keys())}",
            files_involved=["evaluator.yaml"],
        ))

    # 检查5: evaluator.yaml 是否使用已废弃的 thresholds 字段 - Story 26.7
    if evaluator_yaml and "thresholds" in evaluator_yaml:
        checks.append(CrossFileConsistency(
            check_name="evaluator_deprecated_field",
            status="error",
            details="evaluator.yaml 使用了已废弃的 'thresholds' (复数)，请使用 'threshold' (单数)",
            files_involved=["evaluator.yaml"],
        ))
    elif evaluator_yaml:
        checks.append(CrossFileConsistency(
            check_name="evaluator_deprecated_field",
            status="ok",
            details="evaluator.yaml 未使用已废弃的字段",
            files_involved=["evaluator.yaml"],
        ))

    # 检查6: persona.json 是否包含 communication_style - Story 26.7
    has_comm_style, comm_style_value = get_nested_value(persona_json, "communication_style")
    if has_comm_style and is_non_empty(comm_style_value):
        checks.append(CrossFileConsistency(
            check_name="persona_communication_style",
            status="ok",
            details=f"persona.json 包含 communication_style ({len(comm_style_value)} 个风格属性)" if isinstance(comm_style_value, list) else "persona.json 包含 communication_style",
            files_involved=["persona.json"],
        ))
    elif has_comm_style:
        checks.append(CrossFileConsistency(
            check_name="persona_communication_style",
            status="error",
            details="persona.json 的 communication_style 存在但为空",
            files_involved=["persona.json"],
        ))
    else:
        checks.append(CrossFileConsistency(
            check_name="persona_communication_style",
            status="error",
            details="persona.json 缺少 communication_style 字段（v2 必填）",
            files_involved=["persona.json"],
        ))

    return checks


def analyze_node(node_name: str) -> NodeConfigReport:
    """分析单个节点的配置完整性 (Story 26.7 v2 schema)"""
    node_dir = NODES_DIR / node_name

    print(f"  [ANALYZING] {node_name}/")

    # 加载各配置文件
    node_yaml_data = load_yaml_safe(node_dir / "node.yaml")
    persona_json_data = load_json_safe(node_dir / "persona.json")
    evaluator_yaml_data = load_yaml_safe(node_dir / "evaluator.yaml")

    # 加载对应的 _bmad customize.yaml
    bmad_agent_name = NODE_TO_BMAD_AGENT_MAP.get(node_name, f"bmm-{node_name}")
    bmad_customize_path = BMAD_AGENTS_DIR / f"{bmad_agent_name}.customize.yaml"
    bmad_customize_data = load_yaml_safe(bmad_customize_path)

    # 检查各文件完整性 (使用 v2 schema)
    node_yaml_report = check_file_completeness_v2(
        node_yaml_data,
        NODE_YAML_REQUIRED_FIELDS,
        NODE_YAML_OPTIONAL_FIELDS,
        NODE_YAML_V2_REQUIRED_NESTED,  # v2 嵌套必填
        None,
        node_dir / "node.yaml",
    )
    persona_json_report = check_file_completeness_v2(
        persona_json_data,
        PERSONA_REQUIRED_FIELDS,
        PERSONA_OPTIONAL_FIELDS,
        PERSONA_V2_REQUIRED_FIELDS,  # v2 必填
        None,
        node_dir / "persona.json",
    )
    evaluator_yaml_report = check_file_completeness_v2(
        evaluator_yaml_data,
        EVALUATOR_YAML_REQUIRED_FIELDS,
        EVALUATOR_YAML_OPTIONAL_FIELDS,
        None,
        EVALUATOR_DEPRECATED_FIELDS,  # 检测已废弃字段
        node_dir / "evaluator.yaml",
    )
    bmad_customize_report = check_file_completeness_v2(
        bmad_customize_data,
        BMAD_CUSTOMIZE_REQUIRED_FIELDS,
        BMAD_CUSTOMIZE_OPTIONAL_FIELDS,
        None,
        None,
        bmad_customize_path,
    )

    # 跨文件一致性检查
    cross_checks = check_cross_file_consistency(
        node_name, node_yaml_data, persona_json_data, evaluator_yaml_data
    )

    # 计算整体分数 - Story 26.7: 使用 v2 compliance scores
    # 权重: node.yaml (40%), persona.json (40%), evaluator.yaml (20%)
    v2_scores = [
        node_yaml_report.v2_compliance_score * 0.4,
        persona_json_report.v2_compliance_score * 0.4,
    ]
    if evaluator_yaml_report.exists:
        v2_scores.append(evaluator_yaml_report.completeness_score * 0.2)
        v2_overall_score = round(sum(v2_scores), 3)
    else:
        # 如果没有 evaluator.yaml，重新归一化权重
        v2_overall_score = round(sum(v2_scores) / 0.8, 3) if sum(v2_scores) > 0 else 0.0

    # 兼容旧版分数计算
    scores = [
        node_yaml_report.completeness_score,
        persona_json_report.completeness_score,
    ]
    if evaluator_yaml_report.exists:
        scores.append(evaluator_yaml_report.completeness_score)
    overall_score = round(sum(scores) / len(scores), 3)

    # 收集关键问题
    critical_issues = []
    for report in [node_yaml_report, persona_json_report, evaluator_yaml_report]:
        for gap in report.gaps:
            if gap.severity == "critical":
                critical_issues.append(f"[{report.file_path}] {gap.suggestion}")
    for check in cross_checks:
        if check.status == "error":
            critical_issues.append(f"[一致性] {check.details}")

    # 生成建议
    recommendations = []
    if node_yaml_report.optional_missing:
        recommendations.append(
            f"node.yaml: 建议添加可选字段 {node_yaml_report.optional_missing}"
        )
    if persona_json_report.optional_missing:
        recommendations.append(
            f"persona.json: 建议添加可选字段 {persona_json_report.optional_missing}"
        )
    if not evaluator_yaml_report.exists:
        recommendations.append(
            "建议创建 evaluator.yaml 以启用质量评估功能"
        )

    # 检查是否有对应的 _bmad 配置
    if not bmad_customize_path.exists():
        recommendations.append(
            f"_bmad 中缺少对应的 {bmad_agent_name}.customize.yaml 配置"
        )

    return NodeConfigReport(
        node_name=node_name,
        node_dir=get_relative_path(node_dir),
        node_yaml=node_yaml_report,
        persona_json=persona_json_report,
        evaluator_yaml=evaluator_yaml_report,
        bmad_customize=bmad_customize_report,
        cross_file_checks=cross_checks,
        overall_score=overall_score,
        v2_compliance_score=v2_overall_score,  # Story 26.7
        critical_issues=critical_issues,
        recommendations=recommendations,
    )


def run_analysis(node_filter: str | None = None) -> NodeConfigCompletenessReport:
    """运行完整分析"""
    report = NodeConfigCompletenessReport()

    # 发现所有节点目录
    if NODES_DIR.exists():
        node_dirs = [d for d in NODES_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")]
    else:
        print(f"[ERROR] 节点目录不存在: {NODES_DIR}", file=sys.stderr)
        node_dirs = []

    if node_filter:
        node_dirs = [d for d in node_dirs if node_filter.lower() in d.name.lower()]

    print(f"[INFO] 分析 {len(node_dirs)} 个节点...")
    for node_dir in sorted(node_dirs):
        node_report = analyze_node(node_dir.name)
        report.nodes.append(node_report)

    # 汇总统计
    all_critical = sum(len(n.critical_issues) for n in report.nodes)
    avg_score = sum(n.overall_score for n in report.nodes) / max(len(report.nodes), 1)
    avg_v2_score = sum(n.v2_compliance_score for n in report.nodes) / max(len(report.nodes), 1)

    nodes_scores = {n.node_name: n.overall_score for n in report.nodes}
    v2_nodes_scores = {n.node_name: n.v2_compliance_score for n in report.nodes}
    worst_nodes = sorted(v2_nodes_scores.items(), key=lambda x: x[1])[:3]
    best_nodes = sorted(v2_nodes_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    # 统计每种文件的缺失情况
    missing_files = {
        "node.yaml": sum(1 for n in report.nodes if not n.node_yaml.exists),
        "persona.json": sum(1 for n in report.nodes if not n.persona_json.exists),
        "evaluator.yaml": sum(1 for n in report.nodes if not n.evaluator_yaml.exists),
    }

    # Story 26.7: 统计 v2 合规情况
    v2_compliance_issues = {
        "missing_task_name": sum(1 for n in report.nodes if "task.name" in n.node_yaml.required_missing),
        "missing_task_description": sum(1 for n in report.nodes if "task.description" in n.node_yaml.required_missing),
        "missing_communication_style": sum(1 for n in report.nodes if "communication_style" in n.persona_json.required_missing),
        "deprecated_thresholds": sum(1 for n in report.nodes if "thresholds" in n.evaluator_yaml.deprecated_fields_found),
    }

    report.summary = {
        "total_nodes": len(report.nodes),
        "average_completeness_score": round(avg_score, 3),
        "average_v2_compliance_score": round(avg_v2_score, 3),  # Story 26.7
        "total_critical_issues": all_critical,
        "nodes_with_critical_issues": [
            {"node": n.node_name, "count": len(n.critical_issues), "v2_score": n.v2_compliance_score}
            for n in report.nodes if n.critical_issues
        ],
        "missing_files": missing_files,
        "v2_compliance_issues": v2_compliance_issues,  # Story 26.7
        "worst_nodes": [{"node": k, "score": v} for k, v in worst_nodes],
        "best_nodes": [{"node": k, "score": v} for k, v in best_nodes],
        "node_scores": nodes_scores,
        "v2_node_scores": v2_nodes_scores,  # Story 26.7
        "bmad_vs_node_alignment": [
            {
                "node": n.node_name,
                "bmad_agent": NODE_TO_BMAD_AGENT_MAP.get(n.node_name, "unknown"),
                "bmad_config_exists": n.bmad_customize.exists,
            }
            for n in report.nodes
        ],
    }

    return report


def format_text_report(report: NodeConfigCompletenessReport) -> str:
    """格式化文本报告 (Story 26.7)"""
    lines = [
        "=" * 70,
        "节点配置完整性检查报告 (v2 Schema)",
        "=" * 70,
        "",
        "## 摘要统计",
        f"  - 节点总数: {report.summary.get('total_nodes', 0)}",
        f"  - 平均完整度 (v1): {report.summary.get('average_completeness_score', 0):.1%}",
        f"  - 平均完整度 (v2): {report.summary.get('average_v2_compliance_score', 0):.1%}",
        f"  - 关键问题总数: {report.summary.get('total_critical_issues', 0)}",
        "",
        "## v2 Schema 合规性统计",
    ]

    v2_issues = report.summary.get("v2_compliance_issues", {})
    lines.append(f"  - 缺少 task.name: {v2_issues.get('missing_task_name', 0)} 个节点")
    lines.append(f"  - 缺少 task.description: {v2_issues.get('missing_task_description', 0)} 个节点")
    lines.append(f"  - 缺少 communication_style: {v2_issues.get('missing_communication_style', 0)} 个节点")
    lines.append(f"  - 使用废弃 thresholds: {v2_issues.get('deprecated_thresholds', 0)} 个节点")

    lines += ["", "## 文件缺失情况"]
    for fname, count in report.summary.get("missing_files", {}).items():
        if count > 0:
            lines.append(f"  [WARN] {fname}: {count} 个节点缺失")
        else:
            lines.append(f"  [OK] {fname}: 全部存在")

    lines += ["", "## 各节点 v2 完整度评分"]
    for item in sorted(report.summary.get("v2_node_scores", {}).items(), key=lambda x: x[1], reverse=True):
        score_bar = "#" * int(item[1] * 10) + "-" * (10 - int(item[1] * 10))
        status = "[PASS]" if item[1] >= 0.95 else "[FAIL]"
        lines.append(f"  {status} {item[0]:12} [{score_bar}] {item[1]:.1%}")

    lines += ["", ""]

    for node_report in report.nodes:
        v2_status = "[PASS]" if node_report.v2_compliance_score >= 0.95 else "[FAIL]"
        lines += [
            f"{'-' * 60}",
            f"节点: {node_report.node_name} {v2_status} (v2: {node_report.v2_compliance_score:.1%}, v1: {node_report.overall_score:.1%})",
            f"{'-' * 60}",
        ]

        for file_report in [node_report.node_yaml, node_report.persona_json, node_report.evaluator_yaml]:
            file_name = Path(file_report.file_path).name if file_report.file_path else "unknown"
            if not file_report.exists:
                lines.append(f"\n  [MISSING] {file_name} (不存在)")
                continue

            if file_report.v2_compliance_score >= 1.0:
                status = "[OK]"
            elif file_report.v2_compliance_score >= 0.8:
                status = "[WARN]"
            else:
                status = "[FAIL]"
            lines.append(f"\n  {status} {file_name} (v2: {file_report.v2_compliance_score:.1%})")

            if file_report.required_missing:
                lines.append(f"    缺少必填字段: {', '.join(file_report.required_missing)}")
            if file_report.optional_missing:
                lines.append(f"    缺少可选字段: {', '.join(file_report.optional_missing)}")
            if file_report.deprecated_fields_found:
                lines.append(f"    [CRITICAL] 已废弃字段: {', '.join(file_report.deprecated_fields_found)}")
            if file_report.extra_fields:
                lines.append(f"    扩展字段: {', '.join(file_report.extra_fields)}")

        if node_report.cross_file_checks:
            lines.append("\n  跨文件一致性:")
            for check in node_report.cross_file_checks:
                if check.status == "ok":
                    icon = "[OK]"
                elif check.status == "warning":
                    icon = "[WARN]"
                else:
                    icon = "[FAIL]"
                lines.append(f"    {icon} {check.check_name}: {check.details}")

        if node_report.critical_issues:
            lines.append("\n  关键问题:")
            for issue in node_report.critical_issues:
                lines.append(f"    [CRITICAL] {issue}")

        if node_report.recommendations:
            lines.append("\n  建议:")
            for rec in node_report.recommendations:
                lines.append(f"    [INFO] {rec}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="检查 autoBMAD/nodes 各节点的配置完整性并与 _bmad 配置对比"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径 (默认: .tmp/node_config_report.json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="json",
        help="输出格式 (默认: json)",
    )
    parser.add_argument(
        "--node", "-n",
        type=str,
        default=None,
        help="只分析特定节点 (例如: analyst)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="同时打印报告到终端",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="v2 compliance 阈值 (默认: 0.95, Story 26.7)",
    )
    args = parser.parse_args()

    print("[INFO] 开始节点配置完整性检查...")
    report = run_analysis(node_filter=args.node)

    if args.output:
        output_path = Path(args.output)
    else:
        TMP_DIR.mkdir(exist_ok=True)
        suffix = ".txt" if args.format == "text" else ".json"
        output_path = TMP_DIR / f"node_config_report{suffix}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        data = {
            "summary": report.summary,
            "nodes": [asdict(n) for n in report.nodes],
        }
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        text = format_text_report(report)
        output_path.write_text(text, encoding="utf-8")

    print(f"\n[DONE] 报告已保存到: {output_path}")
    print(f"[INFO] 分析了 {len(report.nodes)} 个节点，"
          f"平均 v2 完整度 {report.summary.get('average_v2_compliance_score', 0):.1%}，"
          f"发现 {report.summary.get('total_critical_issues', 0)} 个关键问题")

    # Story 26.7: 检查是否所有节点都达到阈值
    threshold = args.threshold
    all_passed = all(n.v2_compliance_score >= threshold for n in report.nodes)
    if all_passed:
        print(f"[SUCCESS] 所有节点 v2 compliance >= {threshold:.0%}")
    else:
        failed_nodes = [n.node_name for n in report.nodes if n.v2_compliance_score < threshold]
        print(f"[WARNING] 以下节点未达到 v2 compliance 阈值 ({threshold:.0%}): {failed_nodes}")

    if args.print:
        print("\n" + format_text_report(report))

    # Story 26.7: 返回非零退出码如果未达标
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
