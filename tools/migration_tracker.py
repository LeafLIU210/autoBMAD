"""
DocuSwarm 迁移追踪器 - 追踪迁移进度和代码变更

功能：
1. 追踪各 Phase 完成状态
2. 检测 Kimi 代码残留
3. 验证新架构组件存在性
4. 生成迁移进度报告

用法：
    python tools/migration_tracker.py --check
    python tools/migration_tracker.py --phase 0
    python tools/migration_tracker.py --report
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUSWARM_PATH = PROJECT_ROOT / "autoBMAD" / "docuswarm"


@dataclass
class PhaseStatus:
    """Phase 完成状态"""
    phase: int
    name: str
    completed: bool = False
    files_added: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


@dataclass
class MigrationStatus:
    """迁移整体状态"""
    overall_progress: float = 0.0  # 0-100
    phases: list[PhaseStatus] = field(default_factory=list)
    kimi_code_remaining: list[str] = field(default_factory=list)
    new_components: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Phase 定义
PHASE_DEFINITIONS = [
    {
        "phase": 0,
        "name": "运行时抽象层建设",
        "files_to_add": [
            "llm/runtime.py",
            "llm/sdk_result.py",
            "llm/cancellation_manager.py",
            "llm/sdk_executor.py",
            "llm/claude_runtime.py",
            "agents/sdk_helper.py",
        ],
        "files_to_modify": [
            "config.py",
        ],
    },
    {
        "phase": 1,
        "name": "轻量调用路径迁移",
        "files_to_add": [],
        "files_to_modify": [
            "pipeline/orchestrator.py",
            "agents/evaluator.py",
        ],
    },
    {
        "phase": 2,
        "name": "IndependentAgent 迁移",
        "files_to_add": [
            "llm/approval_policy.py",
        ],
        "files_to_modify": [
            "agents/independent.py",
        ],
    },
    {
        "phase": 3,
        "name": "编排恢复链路迁移",
        "files_to_add": [],
        "files_to_modify": [
            "pipeline/orchestrator.py",
        ],
    },
    {
        "phase": 4,
        "name": "Kimi 代码移除",
        "files_to_add": [],
        "files_to_modify": [
            "config.py",
        ],
        "files_to_remove": [
            "llm/session_manager.py",
            "llm/approval.py",
        ],
    },
]


def check_file_exists(relative_path: str) -> bool:
    """检查文件是否存在"""
    return (DOCUSWARM_PATH / relative_path).exists()


def check_file_contains(relative_path: str, pattern: str) -> bool:
    """检查文件是否包含特定内容"""
    file_path = DOCUSWARM_PATH / relative_path
    if not file_path.exists():
        return False
    try:
        content = file_path.read_text(encoding="utf-8")
        return pattern in content
    except (UnicodeDecodeError, IOError):
        return False


def find_kimi_references() -> list[dict[str, Any]]:
    """查找所有 Kimi 相关引用"""
    references = []

    kimi_patterns = [
        "kimi_agent_sdk",
        "KimiSessionManager",
        "KIMI_API_KEY",
        "KIMI_BASE_URL",
        "kimi-for-coding",
        "from kaos",
    ]

    python_files = list(DOCUSWARM_PATH.rglob("*.py"))
    python_files = [f for f in python_files if "__pycache__" not in str(f)]

    for file_path in python_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = file_path.relative_to(DOCUSWARM_PATH)

            for pattern in kimi_patterns:
                if pattern in content:
                    # 计算出现次数
                    count = content.count(pattern)
                    references.append({
                        "file": str(rel_path),
                        "pattern": pattern,
                        "count": count,
                    })
        except (UnicodeDecodeError, IOError):
            continue

    return references


def check_phase_status(phase_def: dict[str, Any]) -> PhaseStatus:
    """检查单个 Phase 的完成状态"""
    phase = phase_def["phase"]
    name = phase_def["name"]

    status = PhaseStatus(phase=phase, name=name)

    # 检查新增文件
    for file_path in phase_def.get("files_to_add", []):
        if check_file_exists(file_path):
            status.files_added.append(f"✓ {file_path}")
        else:
            status.files_added.append(f"✗ {file_path}")

    # 检查修改文件
    for file_path in phase_def.get("files_to_modify", []):
        if check_file_exists(file_path):
            status.files_modified.append(f"✓ {file_path}")
        else:
            status.files_modified.append(f"✗ {file_path}")

    # 检查需要删除的文件（Phase 4 特有）
    if "files_to_remove" in phase_def:
        for file_path in phase_def["files_to_remove"]:
            if check_file_exists(file_path):
                status.blockers.append(f"应删除但存在: {file_path}")
            else:
                status.files_added.append(f"✓ 已删除: {file_path}")

    # 判断 Phase 是否完成
    added_complete = all("✓" in f for f in status.files_added)
    modified_complete = all("✓" in f for f in status.files_modified)
    status.completed = added_complete and modified_complete and not status.blockers

    return status


def analyze_migration_status() -> MigrationStatus:
    """分析整体迁移状态"""
    status = MigrationStatus()

    # 检查各 Phase 状态
    for phase_def in PHASE_DEFINITIONS:
        phase_status = check_phase_status(phase_def)
        status.phases.append(phase_status)

    # 计算总体进度
    completed_phases = sum(1 for p in status.phases if p.completed)
    status.overall_progress = (completed_phases / len(PHASE_DEFINITIONS)) * 100

    # 查找 Kimi 代码残留
    kimi_refs = find_kimi_references()
    kimi_files = set(r["file"] for r in kimi_refs)
    status.kimi_code_remaining = sorted(kimi_files)

    # 检查新组件
    new_components = [
        ("SDKResult", "llm/sdk_result.py"),
        ("CancellationManager", "llm/cancellation_manager.py"),
        ("SDKExecutor", "llm/sdk_executor.py"),
        ("ClaudeRuntime", "llm/claude_runtime.py"),
        ("sdk_helper", "agents/sdk_helper.py"),
    ]

    for name, path in new_components:
        if check_file_exists(path):
            status.new_components.append(f"✓ {name}")
        else:
            status.new_components.append(f"✗ {name}")

    # 生成警告
    if status.overall_progress > 0 and kimi_refs:
        status.warnings.append(
            f"迁移进度 {status.overall_progress:.0f}% 但仍有 {len(kimi_refs)} 处 Kimi 引用"
        )

    if not check_file_exists("llm/sdk_result.py") and check_file_exists("llm/session_manager.py"):
        status.warnings.append("尚未开始 Phase 0，请先建立运行时抽象层")

    return status


def generate_status_report(status: MigrationStatus) -> str:
    """生成状态报告"""
    lines = []
    lines.append("# DocuSwarm 迁移状态报告")
    lines.append("")
    lines.append(f"**总体进度: {status.overall_progress:.0f}%**")
    lines.append("")

    # Phase 状态
    lines.append("## Phase 状态")
    lines.append("")
    lines.append("| Phase | 名称 | 状态 |")
    lines.append("|-------|------|------|")
    for phase in status.phases:
        status_icon = "✓" if phase.completed else "○"
        lines.append(f"| {phase.phase} | {phase.name} | {status_icon} |")
    lines.append("")

    # 详细 Phase 信息
    for phase in status.phases:
        status_icon = "✓" if phase.completed else "○"
        lines.append(f"## Phase {phase.phase}: {phase.name} {status_icon}")
        lines.append("")

        if phase.files_added:
            lines.append("### 新增/删除文件")
            for f in phase.files_added:
                lines.append(f"- {f}")
            lines.append("")

        if phase.files_modified:
            lines.append("### 修改文件")
            for f in phase.files_modified:
                lines.append(f"- {f}")
            lines.append("")

        if phase.blockers:
            lines.append("### 阻塞项")
            for b in phase.blockers:
                lines.append(f"- ⚠️ {b}")
            lines.append("")

    # Kimi 代码残留
    lines.append("## Kimi 代码残留")
    lines.append("")
    if status.kimi_code_remaining:
        lines.append(f"以下文件仍包含 Kimi 引用（共 {len(status.kimi_code_remaining)} 个）：")
        lines.append("")
        for f in status.kimi_code_remaining:
            lines.append(f"- `{f}`")
    else:
        lines.append("✓ 未发现 Kimi 代码残留")
    lines.append("")

    # 新组件状态
    lines.append("## 新架构组件")
    lines.append("")
    for comp in status.new_components:
        lines.append(f"- {comp}")
    lines.append("")

    # 警告
    if status.warnings:
        lines.append("## ⚠️ 警告")
        lines.append("")
        for warning in status.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    return "\n".join(lines)


def check_specific_phase(phase_num: int) -> str:
    """检查特定 Phase 的详细状态"""
    phase_def = next(
        (p for p in PHASE_DEFINITIONS if p["phase"] == phase_num),
        None
    )
    if not phase_def:
        return f"错误: 未找到 Phase {phase_num}"

    status = check_phase_status(phase_def)

    lines = []
    lines.append(f"# Phase {phase_num}: {status.name} 详细检查")
    lines.append("")
    lines.append(f"**完成状态**: {'✓ 已完成' if status.completed else '○ 未完成'}")
    lines.append("")

    if status.files_added:
        lines.append("## 新增/删除文件检查")
        lines.append("")
        for item in status.files_added:
            lines.append(f"- {item}")
        lines.append("")

    if status.files_modified:
        lines.append("## 修改文件检查")
        lines.append("")
        for item in status.files_modified:
            lines.append(f"- {item}")
        lines.append("")

    if status.blockers:
        lines.append("## 阻塞项")
        lines.append("")
        for blocker in status.blockers:
            lines.append(f"- ⚠️ {blocker}")
        lines.append("")

    # 添加下一步建议
    lines.append("## 下一步建议")
    lines.append("")
    if status.completed:
        lines.append("✓ 本 Phase 已完成，可以进入下一阶段")
        if phase_num < 4:
            next_phase = phase_num + 1
            lines.append(f"建议运行: `python tools/migration_tracker.py --phase {next_phase}`")
    else:
        incomplete = [f for f in status.files_added + status.files_modified if "✗" in f]
        if incomplete:
            lines.append(f"需要完成以下 {len(incomplete)} 项：")
            for item in incomplete:
                # 提取文件名
                file_name = item.replace("✗ ", "").replace("(应删除但存在)", "").strip()
                lines.append(f"- 创建/修改 `{file_name}`")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DocuSwarm 迁移追踪器"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="检查整体迁移状态"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[0, 1, 2, 3, 4],
        help="检查特定 Phase 的详细状态"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成完整报告"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径"
    )
    args = parser.parse_args()

    if args.phase is not None:
        content = check_specific_phase(args.phase)

    elif args.check or args.report:
        status = analyze_migration_status()
        if args.json:
            content = json.dumps(asdict(status), indent=2, ensure_ascii=False)
        else:
            content = generate_status_report(status)

    else:
        parser.print_help()
        return 0

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(content, encoding="utf-8")
        print(f"报告已保存到: {output_path}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
