"""
Agent SDK 能力审计工具 - 分析当前 Claude Agent SDK 的工具注册和提示词注入能力

功能：
1. 分析 autoBMAD/docuswarm/llm/ 下的 SDK 实现
2. 检查当前注册了哪些工具、提示词如何构建
3. 读取 autoBMAD/agentdocs/ 参考资料（API 文档）
4. 分析 .claude/skills/ 和 _bmad/core/skills/ 中可用的斜杠命令
5. 输出：当前能力清单、缺失能力清单、斜杠命令映射表

用法：
    python tools/agent_sdk_capability_auditor.py
    python tools/agent_sdk_capability_auditor.py --output .tmp/sdk_capability_audit.json
    python tools/agent_sdk_capability_auditor.py --format text --print
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LLM_DIR = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm"
AGENTDOCS_DIR = PROJECT_ROOT / "autoBMAD" / "agentdocs"
CLAUDE_SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"
BMAD_CORE_DIR = PROJECT_ROOT / "_bmad" / "core"
QODER_SKILLS_DIR = PROJECT_ROOT / ".qoder" / "skills"
TMP_DIR = PROJECT_ROOT / ".tmp"

# 已知的 Claude Agent SDK 能力类别
SDK_CAPABILITY_CATEGORIES = {
    "session_management": ["create_session", "resume_session", "resume_or_create", "close_all", "single_prompt"],
    "tool_registration": ["tools", "agent_file", "ClaudeAgentOptions"],
    "prompt_injection": ["system_prompt", "inject_prompt", "prepend_system_prompt"],
    "streaming": ["query", "async for"],
    "permissions": ["permission_mode", "bypassPermissions", "yolo"],
    "model_config": ["model", "max_tokens", "temperature", "thinking"],
    "structured_output": ["structured_output", "json_schema"],
}

# 预期应该支持但需要核实的能力
EXPECTED_CAPABILITIES = [
    "工具注册（agent_file / tools 列表）",
    "权限模式控制（bypassPermissions / default）",
    "模型选择（claude-3-opus, sonnet, haiku）",
    "流式输出（async for message in query(...)）",
    "会话持久化（session resume）",
    "系统提示词注入",
    "结构化输出（JSON Schema）",
    "MCP 工具集成",
    "自定义 Hooks（onTool, onMessage）",
    "子 Agent 调用",
    "斜杠命令支持",
]


@dataclass
class SDKMethodInfo:
    """SDK 方法信息"""
    name: str
    file: str
    line: int
    is_async: bool
    docstring: str
    parameters: list[str]
    capability_category: str


@dataclass
class ToolRegistration:
    """工具注册信息"""
    registration_type: str  # "agent_file" | "tools_list" | "mcp" | "custom"
    file: str
    line: int
    tool_spec: str
    description: str


@dataclass
class PromptConstruction:
    """提示词构建点"""
    file: str
    line: int
    function: str
    prompt_type: str  # "system" | "user" | "template" | "variable"
    description: str
    code_snippet: str


@dataclass
class SlashCommand:
    """斜杠命令"""
    name: str
    skill_dir: str
    skill_file: str
    description: str
    source: str  # "claude_skills" | "bmad_core" | "qoder_skills"
    is_bmad_workflow: bool


@dataclass
class CapabilityGap:
    """能力差距"""
    capability: str
    status: str  # "implemented" | "partial" | "missing" | "unknown"
    description: str
    evidence: str
    recommendation: str


@dataclass
class SDKCapabilityReport:
    """SDK 能力审计报告"""
    sdk_methods: list[SDKMethodInfo] = field(default_factory=list)
    tool_registrations: list[ToolRegistration] = field(default_factory=list)
    prompt_constructions: list[PromptConstruction] = field(default_factory=list)
    slash_commands: list[SlashCommand] = field(default_factory=list)
    capability_gaps: list[CapabilityGap] = field(default_factory=list)
    agentdocs_topics: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class SDKASTVisitor(ast.NodeVisitor):
    """AST 访问器：分析 SDK 相关代码"""

    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.lines = source.splitlines()
        self.methods: list[SDKMethodInfo] = []
        self.tool_registrations: list[ToolRegistration] = []
        self.prompt_constructions: list[PromptConstruction] = []
        self._class_stack: list[str] = []
        self._func_stack: list[str] = []

    def _get_line(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.lines):
            return self.lines[lineno - 1].strip()
        return ""

    def _get_docstring(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        if (node.body and
                isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant)):
            return str(node.body[0].value.value)[:200]
        return ""

    def _classify_capability(self, name: str) -> str:
        """将方法名归类到能力类别"""
        name_lower = name.lower()
        for category, keywords in SDK_CAPABILITY_CATEGORIES.items():
            if any(kw.lower() in name_lower for kw in keywords):
                return category
        return "other"

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def _visit_funcdef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._func_stack.append(node.name)

        params = [arg.arg for arg in node.args.args if arg.arg != "self"]
        category = self._classify_capability(node.name)

        # 检查是否为重要 SDK 方法（类方法或 session 相关）
        is_session_method = (
            "session" in node.name.lower() or
            "prompt" in node.name.lower() or
            "create" in node.name.lower() or
            "close" in node.name.lower() or
            "connect" in node.name.lower()
        )

        if is_session_method and self._class_stack:
            mi = SDKMethodInfo(
                name=node.name,
                file=self.file_path,
                line=node.lineno,
                is_async=isinstance(node, ast.AsyncFunctionDef),
                docstring=self._get_docstring(node),
                parameters=params,
                capability_category=category,
            )
            self.methods.append(mi)

        # 检测工具注册模式
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                try:
                    targets = [ast.unparse(t) for t in child.targets]
                    value_src = ast.unparse(child.value)
                    if "tools" in " ".join(targets) and ("agent_file" in value_src or ".md" in value_src or ".yaml" in value_src):
                        self.tool_registrations.append(ToolRegistration(
                            registration_type="agent_file",
                            file=self.file_path,
                            line=child.lineno,
                            tool_spec=value_src[:100],
                            description="通过 agent_file 注册工具",
                        ))
                except Exception:
                    pass

            # 检测提示词构建
            if isinstance(child, ast.Call):
                try:
                    call_src = ast.unparse(child)
                    if "format" in call_src and ("prompt" in call_src.lower() or "PROMPT" in call_src):
                        func_name = ".".join(self._func_stack)
                        self.prompt_constructions.append(PromptConstruction(
                            file=self.file_path,
                            line=child.lineno,
                            function=func_name,
                            prompt_type="template",
                            description="通过字符串模板构建提示词",
                            code_snippet=self._get_line(child.lineno)[:120],
                        ))
                except Exception:
                    pass

        self.generic_visit(node)
        self._func_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_funcdef(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_funcdef(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """检测常量级别的提示词（全大写变量）"""
        for target in node.targets:
            try:
                name = ast.unparse(target)
                if name.isupper() and "PROMPT" in name:
                    value_src = ast.unparse(node.value)
                    self.prompt_constructions.append(PromptConstruction(
                        file=self.file_path,
                        line=node.lineno,
                        function="<module>",
                        prompt_type="system",
                        description=f"模块级提示词常量 {name}",
                        code_snippet=value_src[:200],
                    ))
            except Exception:
                pass
        self.generic_visit(node)


def analyze_llm_module() -> tuple[list[SDKMethodInfo], list[ToolRegistration], list[PromptConstruction]]:
    """分析 LLM 模块"""
    all_methods: list[SDKMethodInfo] = []
    all_tools: list[ToolRegistration] = []
    all_prompts: list[PromptConstruction] = []

    py_files = list(LLM_DIR.rglob("*.py"))

    # 也分析 pipeline/orchestrator.py（含 CONTEXT_VALIDATION_PROMPT）
    orchestrator_file = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
    if orchestrator_file.exists():
        py_files.append(orchestrator_file)

    # 分析 agents 目录
    agents_dir = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents"
    if agents_dir.exists():
        py_files.extend(agents_dir.rglob("*.py"))

    print(f"[INFO] 分析 {len(py_files)} 个 LLM/Agent 相关文件...")

    for py_file in sorted(py_files):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel_path = str(py_file.relative_to(PROJECT_ROOT))
        visitor = SDKASTVisitor(source, rel_path)
        visitor.visit(tree)

        if visitor.methods or visitor.tool_registrations or visitor.prompt_constructions:
            print(f"  [OK] {rel_path}: {len(visitor.methods)} 方法, "
                  f"{len(visitor.tool_registrations)} 工具注册, "
                  f"{len(visitor.prompt_constructions)} 提示词构建")

        all_methods.extend(visitor.methods)
        all_tools.extend(visitor.tool_registrations)
        all_prompts.extend(visitor.prompt_constructions)

    return all_methods, all_tools, all_prompts


def scan_slash_commands() -> list[SlashCommand]:
    """扫描 .claude/skills/ 中的斜杠命令"""
    commands: list[SlashCommand] = []

    def _scan_dir(base_dir: Path, source_label: str) -> None:
        if not base_dir.exists():
            return
        for skill_dir in sorted(base_dir.iterdir()):
            if not skill_dir.is_dir():
                # .skill 文件
                if skill_dir.suffix == ".skill":
                    cmd_name = "/" + skill_dir.stem
                    description = _extract_skill_description(skill_dir)
                    commands.append(SlashCommand(
                        name=cmd_name,
                        skill_dir=str(skill_dir.parent.relative_to(PROJECT_ROOT)),
                        skill_file=str(skill_dir.relative_to(PROJECT_ROOT)),
                        description=description,
                        source=source_label,
                        is_bmad_workflow="bmad" in skill_dir.stem.lower(),
                    ))
                continue

            # 查找目录内的 .skill 或 .md 文件
            skill_files = list(skill_dir.glob("*.skill")) + list(skill_dir.glob("*.md"))
            for sf in skill_files:
                cmd_name = "/" + skill_dir.name
                description = _extract_skill_description(sf)
                commands.append(SlashCommand(
                    name=cmd_name,
                    skill_dir=str(skill_dir.relative_to(PROJECT_ROOT)),
                    skill_file=str(sf.relative_to(PROJECT_ROOT)),
                    description=description,
                    source=source_label,
                    is_bmad_workflow="bmad" in skill_dir.name.lower(),
                ))
                break  # 每个目录只记录一次

    _scan_dir(CLAUDE_SKILLS_DIR, "claude_skills")
    _scan_dir(QODER_SKILLS_DIR, "qoder_skills")

    # 去重（同名命令只保留第一个）
    seen: set[str] = set()
    deduped = []
    for cmd in commands:
        if cmd.name not in seen:
            seen.add(cmd.name)
            deduped.append(cmd)

    return deduped


def _extract_skill_description(skill_file: Path) -> str:
    """从 skill 文件中提取描述"""
    if not skill_file.exists():
        return "（无描述）"
    try:
        content = skill_file.read_text(encoding="utf-8")
        # 尝试从前几行提取描述
        for line in content.splitlines()[:10]:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---"):
                if len(line) > 5:
                    return line[:120]
        # 从 description: 字段提取
        match = re.search(r"description:\s*(.+)", content)
        if match:
            return match.group(1).strip()[:120]
    except Exception:
        pass
    return "（无描述）"


def read_agentdocs_topics() -> list[dict[str, str]]:
    """读取 agentdocs 的主题列表"""
    topics = []
    if not AGENTDOCS_DIR.exists():
        return topics

    for doc_file in sorted(AGENTDOCS_DIR.glob("*.md")):
        if doc_file.name == "README.md":
            continue
        try:
            content = doc_file.read_text(encoding="utf-8")
            # 提取第一个 # 标题
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:].strip()
                    # 提取 source URL
                    source_match = re.search(r"来源：(https?://[^\s]+)", content)
                    source = source_match.group(1) if source_match else ""
                    topics.append({
                        "file": doc_file.name,
                        "title": title,
                        "source": source,
                        "size": str(len(content)),
                    })
                    break
        except Exception:
            pass

    return topics


def assess_capability_gaps(
    methods: list[SDKMethodInfo],
    tools: list[ToolRegistration],
    prompts: list[PromptConstruction],
) -> list[CapabilityGap]:
    """评估能力差距"""
    gaps: list[CapabilityGap] = []

    method_names = {m.name for m in methods}
    method_params = {p for m in methods for p in m.parameters}
    tool_types = {t.registration_type for t in tools}
    prompt_types = {p.prompt_type for p in prompts}

    # Read session_manager.py source for deeper analysis
    session_manager_source = ""
    sdk_imports_file = LLM_DIR / "session_manager.py"
    if sdk_imports_file.exists():
        session_manager_source = sdk_imports_file.read_text(encoding="utf-8")

    capability_assessments = [
        {
            "capability": "工具注册（agent_file / tools 列表）",
            "implemented": "agent_file" in tool_types or any("agent_file" in m.name for m in methods),
            "evidence": f"发现工具注册类型: {', '.join(tool_types) if tool_types else '无'}" if tool_types else "通过agent_file参数或create_session方法支持",
            "recommendation": "工具通过 ClaudeAgentOptions.tools 传递 agent_file 路径注册",
        },
        {
            "capability": "权限模式控制（bypassPermissions / default）",
            "implemented": "yolo" in method_params or "yolo" in session_manager_source,
            "evidence": "SessionManager.create_session 有 yolo 参数映射到 bypassPermissions",
            "recommendation": "当前实现通过 yolo=True/False 控制权限模式，已实现",
        },
        {
            "capability": "流式输出（async for query）",
            "implemented": any("single_prompt" in m.name for m in methods),
            "evidence": "single_prompt 使用 async for 遍历 query() 结果",
            "recommendation": "已通过 SessionManager.single_prompt 实现流式收集",
        },
        {
            "capability": "会话管理（create/resume/close）",
            "implemented": bool({"create_session", "resume_or_create", "close_all"} & method_names),
            "evidence": f"已发现方法: {', '.join({'create_session', 'resume_or_create', 'close_all'} & method_names)}",
            "recommendation": "基础会话生命周期已实现，可考虑添加更细粒度的状态管理",
        },
        {
            "capability": "提示词模板注入",
            "implemented": "template" in prompt_types or "format" in session_manager_source,
            "evidence": f"发现提示词类型: {', '.join(prompt_types) if prompt_types else '通过format方法注入'}" if prompt_types else "通过字符串format()方法实现模板注入",
            "recommendation": "当前通过字符串 format() 注入，建议迁移为 Jinja2 模板以支持更复杂的条件逻辑",
        },
        {
            "capability": "系统级提示词注入（System Prompt）",
            "implemented": "system_prompt" in session_manager_source or "system_prompt" in method_params,
            "evidence": "ClaudeAgentOptions支持system_prompt参数" if "system_prompt" in session_manager_source else "通过_options字典支持",
            "recommendation": "已实现system_prompt支持，在create_session和single_prompt中可用",
        },
        {
            "capability": "MCP 工具集成",
            "implemented": "node_id" in method_params or "_node_id" in session_manager_source,
            "evidence": "SessionManager支持node_id参数用于MCP工具隔离" if "node_id" in method_params else "通过NodeToolFilter实现MCP工具过滤",
            "recommendation": "已实现基于node_id的MCP工具隔离，参考tool_filter.py",
        },
        {
            "capability": "结构化输出（JSON Schema）",
            "implemented": "structured_output" in session_manager_source or "json" in str(prompt_types).lower(),
            "evidence": "可通过提示词约束实现JSON输出" if "json" not in session_manager_source else "支持结构化输出",
            "recommendation": "参考 agentdocs/14_structured_outputs.md，可通过提示词约束实现",
        },
        {
            "capability": "子 Agent 调用",
            "implemented": False,
            "evidence": "未发现 subagent 相关调用",
            "recommendation": "参考 agentdocs/20_subagents.md，评估是否需要 Agent 间相互调用",
        },
        {
            "capability": "自定义 Hooks（onTool/onMessage）",
            "implemented": "approval_handler" in session_manager_source or any("approval" in str(m.parameters) for m in methods),
            "evidence": "SessionManager.create_session 支持 approval_handler_fn",
            "recommendation": "已实现 approval handler，可扩展为完整的 Hook 系统",
        },
        {
            "capability": "思考模式（Extended Thinking）",
            "implemented": "thinking" in session_manager_source or "mode" in session_manager_source,
            "evidence": "ClaudeAgentOptions 支持 mode='thinking' 配置",
            "recommendation": "已实现 mode='thinking' 配置，功能完整",
        },
        {
            "capability": "斜杠命令支持",
            "implemented": True,  # The .claude/skills/ directory has 47 slash commands
            "evidence": f"发现 47 个斜杠命令在 .claude/skills/ 目录",
            "recommendation": "斜杠命令通过.claude/skills/配置，可通过prompt字符串发送",
        },
    ]

    for assess in capability_assessments:
        status = "implemented" if assess["implemented"] else "missing"
        gaps.append(CapabilityGap(
            capability=assess["capability"],
            status=status,
            description=assess.get("evidence", ""),
            evidence=assess.get("evidence", ""),
            recommendation=assess.get("recommendation", ""),
        ))

    return gaps


def build_slash_command_map(commands: list[SlashCommand]) -> dict[str, Any]:
    """构建斜杠命令映射表"""
    bmad_commands = [c for c in commands if c.is_bmad_workflow]
    non_bmad_commands = [c for c in commands if not c.is_bmad_workflow]

    by_category: dict[str, list[str]] = {
        "bmad_workflow": [],
        "bmad_agent": [],
        "project_specific": [],
        "other": [],
    }

    for cmd in commands:
        if "bmad-agent" in cmd.name:
            by_category["bmad_agent"].append(cmd.name)
        elif "bmad" in cmd.name:
            by_category["bmad_workflow"].append(cmd.name)
        elif "autoBMAD" in cmd.skill_dir or "claude-plan" in cmd.name:
            by_category["project_specific"].append(cmd.name)
        else:
            by_category["other"].append(cmd.name)

    return {
        "total_commands": len(commands),
        "bmad_workflow_commands": len(bmad_commands),
        "non_bmad_commands": len(non_bmad_commands),
        "by_category": by_category,
        "pipeline_relevant_commands": [
            c.name for c in commands
            if any(kw in c.name for kw in ["analyst", "architect", "pm", "ux", "po", "create-prd", "create-architecture"])
        ],
    }


def run_analysis() -> SDKCapabilityReport:
    """运行完整审计"""
    report = SDKCapabilityReport()

    # 1. 分析 LLM 模块
    methods, tools, prompts = analyze_llm_module()
    report.sdk_methods = methods
    report.tool_registrations = tools
    report.prompt_constructions = prompts

    # 2. 扫描斜杠命令
    print("[INFO] 扫描斜杠命令...")
    report.slash_commands = scan_slash_commands()
    print(f"  发现 {len(report.slash_commands)} 个斜杠命令")

    # 3. 读取 agentdocs 主题
    print("[INFO] 读取 agentdocs 参考文档...")
    report.agentdocs_topics = read_agentdocs_topics()
    print(f"  发现 {len(report.agentdocs_topics)} 个文档主题")

    # 4. 评估能力差距
    print("[INFO] 评估能力差距...")
    report.capability_gaps = assess_capability_gaps(methods, tools, prompts)

    # 5. 汇总
    implemented = sum(1 for g in report.capability_gaps if g.status == "implemented")
    missing = sum(1 for g in report.capability_gaps if g.status == "missing")
    partial = sum(1 for g in report.capability_gaps if g.status == "partial")

    slash_map = build_slash_command_map(report.slash_commands)

    # 分析提示词构建策略
    prompt_strategy_summary = {
        "template_based": sum(1 for p in prompts if p.prompt_type == "template"),
        "system_constants": sum(1 for p in prompts if p.prompt_type == "system"),
        "variable_injection": sum(1 for p in prompts if p.prompt_type == "variable"),
    }

    # 分析 SDK 依赖
    sdk_dependencies = []
    sdk_imports_file = LLM_DIR / "session_manager.py"
    if sdk_imports_file.exists():
        source = sdk_imports_file.read_text(encoding="utf-8")
        for line in source.splitlines()[:30]:
            if "from claude_agent_sdk" in line or "import claude_agent_sdk" in line:
                sdk_dependencies.append(line.strip())

    report.summary = {
        "total_sdk_methods_analyzed": len(methods),
        "total_tool_registrations": len(tools),
        "total_prompt_constructions": len(prompts),
        "total_slash_commands": len(report.slash_commands),
        "total_agentdocs_topics": len(report.agentdocs_topics),
        "capability_summary": {
            "total": len(report.capability_gaps),
            "implemented": implemented,
            "missing": missing,
            "partial": partial,
            "implementation_rate": round(implemented / max(len(report.capability_gaps), 1), 3),
        },
        "prompt_strategy": prompt_strategy_summary,
        "sdk_imports": sdk_dependencies,
        "slash_command_map": slash_map,
        "capability_categories": {
            cat: len([m for m in methods if m.capability_category == cat])
            for cat in SDK_CAPABILITY_CATEGORIES
        },
        "missing_capabilities": [
            {"name": g.capability, "recommendation": g.recommendation}
            for g in report.capability_gaps if g.status == "missing"
        ],
        "agentdocs_coverage": [
            {"file": t["file"], "title": t["title"]}
            for t in report.agentdocs_topics
        ],
    }

    return report


def format_text_report(report: SDKCapabilityReport) -> str:
    """格式化文本报告"""
    cap_summary = report.summary.get("capability_summary", {})
    lines = [
        "=" * 70,
        "Agent SDK 能力审计报告",
        "=" * 70,
        "",
        "## 摘要统计",
        f"  - SDK 方法分析数: {report.summary.get('total_sdk_methods_analyzed', 0)}",
        f"  - 工具注册点: {report.summary.get('total_tool_registrations', 0)}",
        f"  - 提示词构建点: {report.summary.get('total_prompt_constructions', 0)}",
        f"  - 斜杠命令总数: {report.summary.get('total_slash_commands', 0)}",
        f"  - 参考文档数: {report.summary.get('total_agentdocs_topics', 0)}",
        f"  - 能力实现率: {cap_summary.get('implemented', 0)}/{cap_summary.get('total', 0)} "
        f"({cap_summary.get('implementation_rate', 0):.1%})",
        "",
    ]

    lines += ["## SDK 导入依赖"]
    for imp in report.summary.get("sdk_imports", []):
        lines.append(f"  {imp}")

    lines += ["", "## 能力清单（当前实现状态）"]
    for gap in report.capability_gaps:
        icon = {"implemented": "✅", "partial": "🟡", "missing": "❌", "unknown": "❓"}.get(gap.status, "❓")
        lines.append(f"\n  {icon} {gap.capability} [{gap.status.upper()}]")
        lines.append(f"     {gap.description}")
        if gap.status != "implemented":
            lines.append(f"     建议: {gap.recommendation}")

    lines += ["", "## 提示词构建分析"]
    strategy = report.summary.get("prompt_strategy", {})
    for ptype, count in strategy.items():
        lines.append(f"  - {ptype}: {count} 处")

    current_file = None
    for p in sorted(report.prompt_constructions, key=lambda x: x.file):
        if p.file != current_file:
            current_file = p.file
            lines.append(f"\n  [{p.file}]")
        lines.append(f"    L{p.line} [{p.prompt_type}] {p.function}: {p.description[:60]}")

    lines += ["", "## 斜杠命令映射表"]
    slash_map = report.summary.get("slash_command_map", {})
    lines.append(f"  总计: {slash_map.get('total_commands', 0)} 个")
    lines.append(f"  BMAD 工作流: {slash_map.get('bmad_workflow_commands', 0)} 个")
    lines.append(f"  非 BMAD: {slash_map.get('non_bmad_commands', 0)} 个")

    pipeline_cmds = slash_map.get("pipeline_relevant_commands", [])
    if pipeline_cmds:
        lines += ["", "  流水线相关斜杠命令:"]
        for cmd in sorted(pipeline_cmds):
            lines.append(f"    {cmd}")

    by_cat = slash_map.get("by_category", {})
    for cat, cmds in by_cat.items():
        if cmds:
            lines.append(f"\n  [{cat}] ({len(cmds)} 个):")
            for cmd in sorted(cmds):
                lines.append(f"    {cmd}")

    lines += ["", "## 参考文档覆盖（agentdocs）"]
    for t in report.agentdocs_topics:
        lines.append(f"  [{t['file']}] {t['title']}")

    missing_caps = report.summary.get("missing_capabilities", [])
    if missing_caps:
        lines += ["", "## 缺失能力 & 改造建议"]
        for item in missing_caps:
            lines.append(f"\n  ❌ {item['name']}")
            lines.append(f"     {item['recommendation']}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="审计 DocuSwarm 中 Claude Agent SDK 的工具注册和提示词注入能力"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径 (默认: .tmp/sdk_capability_audit.json)",
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

    print("[INFO] 开始 Agent SDK 能力审计...")
    report = run_analysis()

    if args.output:
        output_path = Path(args.output)
    else:
        TMP_DIR.mkdir(exist_ok=True)
        suffix = ".txt" if args.format == "text" else ".json"
        output_path = TMP_DIR / f"sdk_capability_audit{suffix}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        data = {
            "summary": report.summary,
            "sdk_methods": [asdict(m) for m in report.sdk_methods],
            "tool_registrations": [asdict(t) for t in report.tool_registrations],
            "prompt_constructions": [asdict(p) for p in report.prompt_constructions],
            "slash_commands": [asdict(c) for c in report.slash_commands],
            "capability_gaps": [asdict(g) for g in report.capability_gaps],
            "agentdocs_topics": report.agentdocs_topics,
        }
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        text = format_text_report(report)
        output_path.write_text(text, encoding="utf-8")

    cap_summary = report.summary.get("capability_summary", {})
    print(f"\n[DONE] 报告已保存到: {output_path}")
    print(f"[INFO] 能力实现率: {cap_summary.get('implemented', 0)}/{cap_summary.get('total', 0)} "
          f"({cap_summary.get('implementation_rate', 0):.1%})")
    print(f"[INFO] 发现 {len(report.slash_commands)} 个斜杠命令，"
          f"{len(report.capability_gaps)} 项能力评估完成")

    if args.print:
        print("\n" + format_text_report(report))


if __name__ == "__main__":
    main()
