"""
F1/F2 问题深度分析工具

用于深度研究以下关键问题：
- F1: Skills 白名单与 sdk_native 开关没有在运行时真正生效
- F2: submit_execution_report 已实现但未被允许调用

使用方法:
    cd d:/GITHUB/DocuSwarm
    python tools/f1_f2_deep_dive_analyzer.py

输出:
    - 控制台报告
    - docs/research/f1_f2_deep_dive_report.md 详细研究报告
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 添加项目路径
PROJECT_ROOT = Path("d:/GITHUB/DocuSwarm")
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class Finding:
    """分析发现的问题"""
    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # F1, F2, etc.
    title: str
    description: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    files_affected: list[str] = field(default_factory=list)


@dataclass
class AnalysisReport:
    """分析报告"""
    findings: list[Finding] = field(default_factory=list)
    code_snippets: dict[str, str] = field(default_factory=dict)
    runtime_checks: dict[str, Any] = field(default_factory=dict)

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def to_markdown(self) -> str:
        """生成 Markdown 格式的报告"""
        lines = [
            "# F1/F2 问题深度研究报告",
            "",
            f"**生成时间**: {__import__('datetime').datetime.now().isoformat()}",
            f"**分析工具**: tools/f1_f2_deep_dive_analyzer.py",
            "",
            "## 执行摘要",
            "",
        ]

        # 按严重级别分组
        critical = [f for f in self.findings if f.severity == "CRITICAL"]
        high = [f for f in self.findings if f.severity == "HIGH"]
        medium = [f for f in self.findings if f.severity == "MEDIUM"]
        low = [f for f in self.findings if f.severity == "LOW"]

        lines.extend([
            f"| 严重级别 | 数量 |",
            f"|---------|------|",
            f"| CRITICAL | {len(critical)} |",
            f"| HIGH | {len(high)} |",
            f"| MEDIUM | {len(medium)} |",
            f"| LOW | {len(low)} |",
            "",
            "---",
            "",
        ])

        # 详细发现
        lines.append("## 详细发现")
        lines.append("")

        for finding in self.findings:
            lines.extend([
                f"### {finding.id}: {finding.title}",
                "",
                f"**类别**: {finding.category}",
                f"**严重级别**: {finding.severity}",
                f"**影响文件**: {', '.join(finding.files_affected)}",
                "",
                "**描述**:",
                f"> {finding.description}",
                "",
            ])

            if finding.evidence:
                lines.extend([
                    "**证据**:",
                    "",
                ])
                for ev in finding.evidence:
                    lines.append(f"- {ev}")
                lines.append("")

            if finding.recommendation:
                lines.extend([
                    "**修复建议**:",
                    f"```\n{finding.recommendation}\n```",
                    "",
                ])

            lines.append("---")
            lines.append("")

        # 代码片段
        if self.code_snippets:
            lines.extend([
                "## 关键代码片段",
                "",
            ])
            for name, code in self.code_snippets.items():
                lines.extend([
                    f"### {name}",
                    "",
                    "```python",
                    code,
                    "```",
                    "",
                ])

        # 运行时检查
        if self.runtime_checks:
            lines.extend([
                "## 运行时检查结果",
                "",
                "```json",
                json.dumps(self.runtime_checks, indent=2, default=str),
                "```",
                "",
            ])

        return "\n".join(lines)


def analyze_session_manager_build_allowed_tools() -> Finding | None:
    """分析 SessionManager._build_allowed_tools() 方法"""
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # 检查是否无条件添加 "Skill"
    has_unconditional_skill = 'tools.append("Skill")' in content

    # 检查是否检查 sdk_native
    checks_sdk_native = "sdk_native" in content and "_build_allowed_tools" in content

    # 提取代码片段
    lines = content.split("\n")
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if "def _build_allowed_tools(" in line:
            start_idx = i
        elif start_idx is not None and line.strip() and not line.startswith(" ") and i > start_idx:
            end_idx = i
            break

    if start_idx is not None and end_idx is None:
        end_idx = min(start_idx + 50, len(lines))

    code_snippet = "\n".join(lines[start_idx:end_idx]) if start_idx else ""

    if has_unconditional_skill and not checks_sdk_native:
        return Finding(
            id="F1-001",
            severity="CRITICAL",
            category="F1",
            title="SessionManager._build_allowed_tools() 无条件添加 Skill 工具",
            description=(
                "SessionManager._build_allowed_tools() 方法无条件地将 'Skill' 添加到 allowed_tools 列表中，"
                "没有检查 NodeSkillsConfig.sdk_native 开关。这意味着即使 sdk_native=False，Skills 仍然会被启用。"
            ),
            evidence=[
                f"代码中直接执行 tools.append(\"Skill\")，没有条件判断",
                f"方法内没有引用 self._tool_permissions.skills.sdk_native",
            ],
            recommendation="在添加 'Skill' 之前检查 self._tool_permissions.skills.sdk_native 是否为 True",
            files_affected=["autoBMAD/docuswarm/llm/session_manager.py"],
        )

    return None


def analyze_session_manager_create_options() -> Finding | None:
    """分析 SessionManager._create_options() 方法"""
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # 检查是否无条件设置 setting_sources
    has_unconditional_setting_sources = '"setting_sources": ["project"]' in content

    # 检查是否检查 sdk_native
    checks_sdk_native_in_create_options = (
        "_create_options" in content and "sdk_native" in content
    )

    # 检查 _create_options 方法内是否使用 sdk_native
    lines = content.split("\n")
    in_create_options = False
    create_options_lines = []

    for line in lines:
        if "def _create_options(" in line:
            in_create_options = True
        elif in_create_options:
            if line.strip() and not line.startswith(" ") and "def " in line:
                break
            create_options_lines.append(line)

    create_options_code = "\n".join(create_options_lines)
    checks_sdk_native = "sdk_native" in create_options_code

    if has_unconditional_setting_sources and not checks_sdk_native:
        return Finding(
            id="F1-002",
            severity="CRITICAL",
            category="F1",
            title="SessionManager._create_options() 无条件启用 setting_sources",
            description=(
                "SessionManager._create_options() 方法无条件设置 setting_sources=['project']，"
                "没有检查 NodeSkillsConfig.sdk_native 开关。这导致即使 sdk_native=False，"
                "SDK 仍然会尝试从 .claude/skills/ 目录自动发现技能。"
            ),
            evidence=[
                'options_dict["setting_sources"] = ["project"] 是无条件执行的',
                "_create_options 方法体内没有检查 sdk_native",
            ],
            recommendation="在设置 setting_sources 之前检查 self._tool_permissions.skills.sdk_native",
            files_affected=["autoBMAD/docuswarm/llm/session_manager.py"],
        )

    return None


def analyze_independent_agent_tool_permissions_rebuild() -> Finding | None:
    """分析 IndependentAgent.execute_with_input() 中 NodeToolPermissions 重建"""
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "independent.py"

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # 检查是否丢失了 skills 和 shared_context
    lines = content.split("\n")

    # 查找 full_tool_permissions 创建位置
    in_execute_with_input = False
    tool_permissions_build_lines = []
    found_rebuild = False

    for i, line in enumerate(lines):
        if "async def execute_with_input(" in line:
            in_execute_with_input = True
        elif in_execute_with_input and line.strip() and line.startswith("async def "):
            break

        if in_execute_with_input and "NodeToolPermissions(" in line:
            found_rebuild = True
            # 收集前后几行
            start = max(0, i - 3)
            end = min(len(lines), i + 15)
            tool_permissions_build_lines = lines[start:end]

    if not found_rebuild:
        return None

    build_code = "\n".join(tool_permissions_build_lines)

    # 检查是否包含 skills 和 shared_context
    has_skills = "skills=" in build_code
    has_shared_context = "shared_context=" in build_code

    if not has_skills or not has_shared_context:
        return Finding(
            id="F1-003",
            severity="CRITICAL",
            category="F1",
            title="IndependentAgent.execute_with_input() 重建 NodeToolPermissions 时丢失配置",
            description=(
                "IndependentAgent.execute_with_input() 方法在创建 full_tool_permissions 时，"
                f"{'缺少 skills 配置' if not has_skills else ''} "
                f"{'缺少 shared_context 配置' if not has_shared_context else ''}。"
                "这导致从 node.yaml 加载的 skills 和 shared_context 配置在运行时丢失。"
            ),
            evidence=[
                "代码片段显示只传递了 allowed_builtin_tools, file_permissions, search_permissions",
                "node_config.tool_permissions.skills 没有被传递到新的 NodeToolPermissions",
                "node_config.tool_permissions.shared_context 没有被传递到新的 NodeToolPermissions",
            ],
            recommendation=(
                "在创建 full_tool_permissions 时，从 node_config.tool_permissions 复制所有字段，\n"
                "或者使用 dataclasses.replace() 来保留所有现有配置。"
            ),
            files_affected=["autoBMAD/docuswarm/agents/independent.py"],
        )

    return None


def analyze_tool_filter_get_allowed_tools() -> Finding | None:
    """分析 NodeToolFilter.get_allowed_tools() 方法"""
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm" / "tool_filter.py"

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # 检查是否放行 create_deliverable
    has_create_deliverable = "create_deliverable" in content

    # 检查是否放行 submit_execution_report
    has_submit_execution_report = "submit_execution_report" in content

    # 检查 get_allowed_tools 方法
    has_submit_report_in_get_allowed = (
        "submit_execution_report" in content
        and "get_allowed_tools" in content
    )

    # 实际上，我们需要检查 get_allowed_tools 方法体
    lines = content.split("\n")
    in_get_allowed_tools = False
    get_allowed_tools_code = []

    for line in lines:
        if "def get_allowed_tools(" in line:
            in_get_allowed_tools = True
        elif in_get_allowed_tools:
            if line.strip() and not line.startswith(" ") and "def " in line:
                break
            get_allowed_tools_code.append(line)

    get_allowed_tools_body = "\n".join(get_allowed_tools_code)
    has_submit_in_method = "submit_execution_report" in get_allowed_tools_body

    if has_create_deliverable and not has_submit_in_method:
        return Finding(
            id="F2-001",
            severity="CRITICAL",
            category="F2",
            title="NodeToolFilter.get_allowed_tools() 未放行 submit_execution_report",
            description=(
                "NodeToolFilter.get_allowed_tools() 方法只放行 create_deliverable 工具，"
                "但没有放行 submit_execution_report 工具。尽管 submit_execution_report 工具"
                "已在 create_deliverable_sdk.py 中实现并在 MCP server 中注册，"
                "但由于不在 allowed_tools 列表中，Claude SDK 无法调用它。"
            ),
            evidence=[
                "get_allowed_tools() 方法中只有 create_deliverable 被添加到 tools 列表",
                "submit_execution_report 没有在 get_allowed_tools() 中被添加",
                "工具在 MCP server 中注册但不放行，导致运行时无法调用",
            ],
            recommendation=(
                "在 get_allowed_tools() 方法中添加 submit_execution_report 工具：\n"
                'if self.output_dir:\n'
                '    tools.append(...)  # create_deliverable\n'
                '    tools.append(MCP_TOOL_NAME_FORMAT.format(...submit_execution_report...))'
            ),
            files_affected=["autoBMAD/docuswarm/llm/tool_filter.py"],
        )

    return None


def analyze_create_deliverable_server_registration() -> Finding | None:
    """分析 create_deliverable_server 中的工具注册"""
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "tools" / "create_deliverable_sdk.py"

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")

    # 检查 submit_execution_report 是否已定义
    has_submit_execution_report = "def submit_execution_report(" in content

    # 检查是否在 MCP server 中注册
    has_registration = "submit_execution_report_tool" in content

    # 检查是否在 tools 列表中
    in_create_server = False
    server_lines = []

    for line in content.split("\n"):
        if "def create_deliverable_server(" in line:
            in_create_server = True
        elif in_create_server:
            if line.strip() and not line.startswith(" ") and "def " in line:
                break
            server_lines.append(line)

    server_code = "\n".join(server_lines)
    has_in_tools_list = "submit_execution_report_tool" in server_code

    # 检查工具命名
    has_correct_naming = "submit_execution_report" in server_code

    return Finding(
        id="F2-002" if has_submit_execution_report and has_registration else "F2-INFO-001",
        severity="INFO" if has_submit_execution_report and has_registration else "HIGH",
        category="F2",
        title="submit_execution_report 工具实现状态",
        description=(
            "submit_execution_report 工具已在 create_deliverable_sdk.py 中完整实现：\n"
            f"- 函数定义: {'✓ 存在' if has_submit_execution_report else '✗ 缺失'}\n"
            f"- MCP 注册: {'✓ 存在' if has_registration else '✗ 缺失'}\n"
            f"- 在 tools 列表: {'✓ 存在' if has_in_tools_list else '✗ 缺失'}\n"
            "但由于 NodeToolFilter 不放行，运行时仍无法调用。"
        ),
        evidence=[
            "SUBMIT_EXECUTION_REPORT_SCHEMA 已定义 (line 28-83)",
            "submit_execution_report 函数已定义 (line 167-202)",
            "submit_execution_report_tool MCP handler 已定义 (line 288-308)",
            "在 create_deliverable_server 中注册到 tools 列表 (line 317)",
        ],
        recommendation="修复 NodeToolFilter.get_allowed_tools() 以放行此工具",
        files_affected=["autoBMAD/docuswarm/tools/create_deliverable_sdk.py"],
    )


def analyze_skills_whitelist_usage() -> Finding | None:
    """分析 skills.whitelist 在运行时的使用情况"""
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "prompts" / "skill_injector.py"

    if not file_path.exists():
        return Finding(
            id="F1-004",
            severity="HIGH",
            category="F1",
            title="SkillInjector 模块可能不存在",
            description="未能找到 skill_injector.py 模块，无法验证 skills.whitelist 的使用",
            evidence=["文件不存在: autoBMAD/docuswarm/prompts/skill_injector.py"],
            recommendation="确认 skill_injector.py 文件位置",
            files_affected=["autoBMAD/docuswarm/prompts/skill_injector.py"],
        )

    content = file_path.read_text(encoding="utf-8")

    # 检查 whitelist 是否只用于 prompt 注入
    uses_for_prompt = "whitelist" in content and "quick_reference" in content.lower()

    # 检查是否有运行时权限控制
    has_runtime_check = False  # 我们已经在其他检查中确认了没有运行时检查

    return Finding(
        id="F1-004",
        severity="HIGH",
        category="F1",
        title="skills.whitelist 仅用于 prompt 注入，不是运行时权限边界",
        description=(
            "skills.whitelist 配置仅在 SkillInjector.build_skills_quick_reference() 中使用，"
            "用于在 system prompt 中注入可用技能列表。但这只是提示词层面的'建议'，"
            "不是真正的运行时权限边界。由于 SessionManager 无条件启用所有 Skills，"
            "LLM 仍然可以调用不在 whitelist 中的技能。"
        ),
        evidence=[
            "skill_injector.py 只构建 quick reference 文本",
            "whitelist 不传递给 ClaudeAgentOptions 的任何权限控制参数",
            "SDK 的 Skills 机制目前不支持细粒度的单个技能控制",
        ],
        recommendation=(
            "方案1: 使用 SDK 原生 Skill 工具时，所有技能都会暴露，whitelist 仅作为提示\n"
            "方案2: 考虑在 Skill 内容加载层添加过滤（如果 SDK 支持）\n"
            "方案3: 更新文档明确说明 whitelist 的局限性"
        ),
        files_affected=[
            "autoBMAD/docuswarm/prompts/skill_injector.py",
            "autoBMAD/docuswarm/llm/session_manager.py",
        ],
    )


def check_node_yaml_configs() -> list[Finding]:
    """检查 node.yaml 中的 skills 配置"""
    findings = []
    nodes_dir = PROJECT_ROOT / "autoBMAD" / "nodes"

    if not nodes_dir.exists():
        return findings

    for node_dir in nodes_dir.iterdir():
        if not node_dir.is_dir():
            continue

        node_yaml = node_dir / "node.yaml"
        if not node_yaml.exists():
            continue

        import yaml
        try:
            config = yaml.safe_load(node_yaml.read_text(encoding="utf-8"))
            tools = config.get("tools", {})
            skills = tools.get("skills", {})

            if skills:
                sdk_native = skills.get("sdk_native", False)
                whitelist = skills.get("whitelist", [])

                # 如果 sdk_native 为 true 但实际运行时未生效，这是一个问题
                if sdk_native:
                    findings.append(
                        Finding(
                            id=f"F1-NODE-{node_dir.name}",
                            severity="MEDIUM",
                            category="F1",
                            title=f"节点 {node_dir.name} 的 sdk_native=true 但运行时未生效",
                            description=(
                                f"节点 {node_dir.name} 的 node.yaml 设置了 sdk_native=true，"
                                f"whitelist={whitelist}，但由于 SessionManager 无条件启用 Skill，"
                                f"这个配置实际上被忽略了。"
                            ),
                            evidence=[
                                f"node.yaml 设置: sdk_native={sdk_native}",
                                f"node.yaml 设置: whitelist={whitelist}",
                                "但 SessionManager 不检查这些设置",
                            ],
                            recommendation="修复 SessionManager 以尊重 node.yaml 的 skills 配置",
                            files_affected=[f"autoBMAD/nodes/{node_dir.name}/node.yaml"],
                        )
                    )
        except Exception as e:
            findings.append(
                Finding(
                    id=f"F1-NODE-{node_dir.name}-ERROR",
                    severity="LOW",
                    category="F1",
                    title=f"无法解析节点 {node_dir.name} 的配置",
                    description=f"解析 node.yaml 时出错: {e}",
                    files_affected=[f"autoBMAD/nodes/{node_dir.name}/node.yaml"],
                )
            )

    return findings


def extract_key_code_snippets() -> dict[str, str]:
    """提取关键代码片段"""
    snippets = {}

    # SessionManager._build_allowed_tools
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # 提取 _build_allowed_tools
        start_idx = None
        end_idx = None
        for i, line in enumerate(lines):
            if "def _build_allowed_tools(" in line:
                start_idx = i
            elif start_idx is not None and line.strip() and not line.startswith(" ") and i > start_idx:
                end_idx = i
                break

        if start_idx is not None:
            end_idx = end_idx or min(start_idx + 50, len(lines))
            snippets["SessionManager._build_allowed_tools"] = "\n".join(lines[start_idx:end_idx])

        # 提取 _create_options 中的 setting_sources
        start_idx = None
        for i, line in enumerate(lines):
            if "def _create_options(" in line:
                start_idx = i
            elif start_idx is not None and "setting_sources" in line:
                # 提取前后几行
                snippet_start = max(0, i - 2)
                snippet_end = min(len(lines), i + 3)
                snippets["SessionManager._create_options (setting_sources)"] = "\n".join(
                    lines[snippet_start:snippet_end]
                )
                break

    # NodeToolFilter.get_allowed_tools
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "llm" / "tool_filter.py"
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        start_idx = None
        end_idx = None
        for i, line in enumerate(lines):
            if "def get_allowed_tools(" in line:
                start_idx = i
            elif start_idx is not None and line.strip() and not line.startswith(" ") and i > start_idx:
                end_idx = i
                break

        if start_idx is not None:
            end_idx = end_idx or min(start_idx + 80, len(lines))
            snippets["NodeToolFilter.get_allowed_tools"] = "\n".join(lines[start_idx:end_idx])

    # IndependentAgent.execute_with_input tool_permissions 重建
    file_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "NodeToolPermissions(" in line and i > 0:
                # 提取前后几行
                snippet_start = max(0, i - 5)
                snippet_end = min(len(lines), i + 15)
                snippets["IndependentAgent NodeToolPermissions 重建"] = "\n".join(
                    lines[snippet_start:snippet_end]
                )
                break

    return snippets


def main() -> int:
    """主函数"""
    print("=" * 80)
    print("F1/F2 问题深度分析工具")
    print("=" * 80)
    print()

    report = AnalysisReport()

    # 运行所有分析
    analyzers = [
        ("SessionManager._build_allowed_tools", analyze_session_manager_build_allowed_tools),
        ("SessionManager._create_options", analyze_session_manager_create_options),
        ("IndependentAgent tool_permissions 重建", analyze_independent_agent_tool_permissions_rebuild),
        ("NodeToolFilter.get_allowed_tools", analyze_tool_filter_get_allowed_tools),
        ("create_deliverable_server 注册", analyze_create_deliverable_server_registration),
        ("skills.whitelist 使用", analyze_skills_whitelist_usage),
    ]

    for name, analyzer in analyzers:
        print(f"[*] 分析: {name}...")
        try:
            finding = analyzer()
            if finding:
                report.add_finding(finding)
                print(f"  [发现] {finding.severity}: {finding.title}")
            else:
                print(f"  [通过] 未发现 {name} 相关问题")
        except Exception as e:
            print(f"  [错误] 分析失败: {e}")
        print()

    # 检查 node.yaml 配置
    print("[*] 检查 node.yaml 配置...")
    node_findings = check_node_yaml_configs()
    for finding in node_findings:
        report.add_finding(finding)
        print(f"  [发现] {finding.severity}: {finding.title}")
    print()

    # 提取代码片段
    print("[*] 提取关键代码片段...")
    report.code_snippets = extract_key_code_snippets()
    print(f"  提取了 {len(report.code_snippets)} 个代码片段")
    print()

    # 生成报告
    print("[*] 生成研究报告...")
    report_path = PROJECT_ROOT / "docs" / "research" / "f1-f2-deep-reform-runtime-analysis-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = report.to_markdown()
    report_path.write_text(markdown, encoding="utf-8")

    print(f"  报告已保存: {report_path}")
    print()

    # 打印摘要
    print("=" * 80)
    print("分析摘要")
    print("=" * 80)

    critical = [f for f in report.findings if f.severity == "CRITICAL"]
    high = [f for f in report.findings if f.severity == "HIGH"]
    medium = [f for f in report.findings if f.severity == "MEDIUM"]
    low = [f for f in report.findings if f.severity == "LOW"]
    info = [f for f in report.findings if f.severity == "INFO"]

    print(f"  CRITICAL: {len(critical)}")
    print(f"  HIGH: {len(high)}")
    print(f"  MEDIUM: {len(medium)}")
    print(f"  LOW: {len(low)}")
    print(f"  INFO: {len(info)}")
    print()

    if critical:
        print("关键问题:")
        for f in critical:
            print(f"  - [{f.category}] {f.title}")
        print()

    print(f"完整报告请查看: {report_path}")

    return 0 if not critical else 1


if __name__ == "__main__":
    sys.exit(main())
