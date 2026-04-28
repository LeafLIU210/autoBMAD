"""
Phase B - P1-2 文档/配置口径漂移分析工具
==========================================
分析 README.md 和 CONFIGURATION.md 中的 KIMI_* 和 KimiSessionManager 残留

使用方法:
    python tools/phase_b_research/p1_doc_drift_analyzer.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Files to analyze
TARGET_FILES = [
    "autoBMAD/docuswarm/README.md",
    "autoBMAD/docuswarm/CONFIGURATION.md",
]

# Configuration keys that should be migrated
DEPRECATED_PATTERNS = [
    (r"KIMI_API_KEY", "ANTHROPIC_API_KEY"),
    (r"KIMI_BASE_URL", "ANTHROPIC_BASE_URL"),
    (r"KimiSessionManager", "SessionManager"),
]

# Correct patterns
CORRECT_PATTERNS = [
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_BASE_URL",
    "SessionManager",
]


def analyze_file(filepath: Path) -> dict[str, Any]:
    """Analyze a single file for deprecated patterns."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}
    
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    findings = {
        "file": str(filepath.relative_to(PROJECT_ROOT)),
        "total_lines": len(lines),
        "deprecated_occurrences": [],
        "correct_occurrences": [],
        "code_blocks": [],
        "migration_examples": [],
    }
    
    in_code_block = False
    code_block_start = 0
    code_block_content = []
    
    for line_num, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                # End of code block
                findings["code_blocks"].append({
                    "start": code_block_start,
                    "end": line_num,
                    "content": "\n".join(code_block_content),
                    "has_deprecated": False,  # Simplified for now
                })
                code_block_content = []
            else:
                # Start of code block
                code_block_start = line_num
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            code_block_content.append(line)
        
        # Check for deprecated patterns
        for pattern, replacement in DEPRECATED_PATTERNS:
            pattern_clean = pattern.replace("\\\\", "")  # Remove regex escape chars
            for match in re.finditer(pattern, line):
                findings["deprecated_occurrences"].append({
                    "line": line_num,
                    "column": match.start() + 1,
                    "match": match.group(),
                    "replacement": replacement,
                    "context": line.strip(),
                    "in_code_block": in_code_block,
                })
        
        # Check for correct patterns (for comparison)
        for pattern in CORRECT_PATTERNS:
            for match in re.finditer(pattern, line):
                findings["correct_occurrences"].append({
                    "line": line_num,
                    "column": match.start() + 1,
                    "match": match.group(),
                    "context": line.strip(),
                })
    
    return findings


def analyze_config_implementation() -> dict[str, Any]:
    """Analyze the actual Config implementation to verify correct patterns."""
    print("\n[Phase B - P1-2] 分析 Config 实现...")
    
    config_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "config.py"
    if not config_path.exists():
        return {"error": "Config file not found"}
    
    content = config_path.read_text(encoding="utf-8")
    
    findings = {
        "file": "autoBMAD/docuswarm/config.py",
        "env_vars_found": [],
        "uses_anthropic": False,
        "uses_kimi": False,
    }
    
    # Check for environment variable references
    if "ANTHROPIC_API_KEY" in content:
        findings["env_vars_found"].append("ANTHROPIC_API_KEY")
        findings["uses_anthropic"] = True
    if "ANTHROPIC_BASE_URL" in content:
        findings["env_vars_found"].append("ANTHROPIC_BASE_URL")
        findings["uses_anthropic"] = True
    if "KIMI_API_KEY" in content:
        findings["uses_kimi"] = True
    if "KIMI_BASE_URL" in content:
        findings["uses_kimi"] = True
    
    print(f"  发现的环境变量:")
    for var in findings["env_vars_found"]:
        print(f"    OK {var}")
    
    if findings["uses_kimi"]:
        print(f"  WARN 仍发现 KIMI_* 残留")
    else:
        print(f"  OK 代码已实现 ANTHROPIC_* 迁移")
    
    return findings


def check_prd_consistency() -> dict[str, Any]:
    """Check if PRD.md uses correct patterns."""
    print("\n[Phase B - P1-2] 检查 PRD.md 一致性...")
    
    prd_path = PROJECT_ROOT / "docs" / "PRD.md"
    if not prd_path.exists():
        return {"error": "PRD.md not found"}
    
    content = prd_path.read_text(encoding="utf-8")
    
    findings = {
        "file": "docs/PRD.md",
        "anthropic_mentions": content.count("ANTHROPIC_API_KEY"),
        "kimi_mentions": content.count("KIMI_API_KEY"),
        "consistent": False,
    }
    
    findings["consistent"] = findings["anthropic_mentions"] > 0 and findings["kimi_mentions"] == 0
    
    print(f"  ANTHROPIC_API_KEY 提及: {findings['anthropic_mentions']} 次")
    print(f"  KIMI_API_KEY 提及: {findings['kimi_mentions']} 次")
    print(f"  状态: {'OK 一致' if findings['consistent'] else 'WARN 需要检查'}")
    
    return findings


def generate_migration_patch() -> dict[str, Any]:
    """Generate specific migration instructions."""
    print("\n[Phase B - P1-2] 生成迁移补丁建议...")
    
    patches = []
    
    for target_file in TARGET_FILES:
        filepath = PROJECT_ROOT / target_file
        if not filepath.exists():
            continue
        
        content = filepath.read_text(encoding="utf-8")
        original_content = content
        
        # Track changes
        file_patches = {
            "file": target_file,
            "changes": [],
        }
        
        # Simple replacements (may need manual review)
        replacements = [
            ("KIMI_API_KEY", "ANTHROPIC_API_KEY"),
            ("KIMI_BASE_URL", "ANTHROPIC_BASE_URL"),
            ("KimiSessionManager", "SessionManager"),
        ]
        
        for old, new in replacements:
            count = content.count(old)
            if count > 0:
                file_patches["changes"].append({
                    "from": old,
                    "to": new,
                    "occurrences": count,
                })
        
        if file_patches["changes"]:
            patches.append(file_patches)
    
    for p in patches:
        print(f"\n  {p['file']}:")
        for change in p["changes"]:
            print(f"    - {change['from']} -> {change['to']} ({change['occurrences']} 处)")
    
    return {"patches": patches}


def create_doc_update_plan() -> dict[str, Any]:
    """Create a detailed plan for updating documentation."""
    return {
        "phase_b_tasks": [
            {
                "priority": "P0",
                "task": "更新 README.md",
                "changes": [
                    "将所有 KIMI_API_KEY 替换为 ANTHROPIC_API_KEY",
                    "将所有 KIMI_BASE_URL 替换为 ANTHROPIC_BASE_URL",
                    "将所有 KimiSessionManager 替换为 SessionManager",
                    "更新配置示例代码块",
                ],
                "estimated_time": "30 分钟",
            },
            {
                "priority": "P0",
                "task": "更新 CONFIGURATION.md",
                "changes": [
                    "替换所有环境变量引用",
                    "更新配置示例",
                    "更新故障排除部分",
                ],
                "estimated_time": "45 分钟",
            },
            {
                "priority": "P1",
                "task": "验证 PRD.md 一致性",
                "changes": [
                    "确认 PRD.md 使用 ANTHROPIC_* 而非 KIMI_*",
                ],
                "estimated_time": "10 分钟",
            },
            {
                "priority": "P1",
                "task": "添加迁移说明",
                "changes": [
                    "添加从 KIMI_* 到 ANTHROPIC_* 的迁移指南",
                    "说明 SessionManager 的变化",
                ],
                "estimated_time": "20 分钟",
            },
        ],
        "verification_checklist": [
            "grep -r 'KIMI_API_KEY' autoBMAD/docuswarm/*.md 应该无结果",
            "grep -r 'KIMI_BASE_URL' autoBMAD/docuswarm/*.md 应该无结果",
            "grep -r 'KimiSessionManager' autoBMAD/docuswarm/*.md 应该无结果",
            "grep -r 'ANTHROPIC_API_KEY' autoBMAD/docuswarm/README.md 应该命中",
            "grep -r 'SessionManager' autoBMAD/docuswarm/README.md 应该命中",
        ],
    }


def main() -> int:
    """Run all Phase B documentation drift analysis."""
    print("=" * 70)
    print("Phase B 文档/配置口径漂移分析")
    print("=" * 70)
    print("目标: 分析 Finding P1-2 的文档与代码不一致问题")
    
    report = {
        "title": "Phase B 文档/配置口径漂移深度研究报告",
        "description": "针对 Finding P1-2 的文档一致性分析和修复计划",
        "timestamp": "2026-04-04",
        "findings": {},
    }
    
    # Analyze target files
    report["findings"]["file_analysis"] = {}
    for target_file in TARGET_FILES:
        filepath = PROJECT_ROOT / target_file
        print(f"\n[Phase B - P1-2] 分析 {target_file}...")
        analysis = analyze_file(filepath)
        report["findings"]["file_analysis"][target_file] = analysis
        
        deprecated = analysis.get("deprecated_occurrences", [])
        print(f"  总长度: {analysis.get('total_lines', 0)} 行")
        print(f"  发现 {len(deprecated)} 处过时引用:")
        
        # Group by pattern
        by_pattern = {}
        for occ in deprecated:
            pattern = occ["match"]
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(occ)
        
        for pattern, occurrences in by_pattern.items():
            print(f"    - {pattern}: {len(occurrences)} 处")
            # Show first 3
            for occ in occurrences[:3]:
                # Skip printing context to avoid Unicode issues with file content
                print(f"      Line {occ['line']}")
            if len(occurrences) > 3:
                print(f"      ... 还有 {len(occurrences) - 3} 处")
    
    # Check implementation
    report["findings"]["config_implementation"] = analyze_config_implementation()
    
    # Check PRD consistency
    report["findings"]["prd_consistency"] = check_prd_consistency()
    
    # Generate patches
    report["migration_patches"] = generate_migration_patch()
    
    # Update plan
    report["update_plan"] = create_doc_update_plan()
    
    # Write report
    output_path = PROJECT_ROOT / "docs" / "research" / "phase_b_doc_drift_analysis.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[完成] 分析报告已保存: {output_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Phase B 文档漂移问题摘要")
    print("=" * 70)
    
    total_deprecated = 0
    for filename, analysis in report["findings"]["file_analysis"].items():
        deprecated = len(analysis.get("deprecated_occurrences", []))
        total_deprecated += deprecated
        print(f"\n{filename}:")
        print(f"  - 过时引用: {deprecated} 处")
    
    config_impl = report["findings"]["config_implementation"]
    print(f"\n代码实现状态:")
    print(f"  - 使用 ANTHROPIC_*: {'OK' if config_impl.get('uses_anthropic') else 'FAIL'}")
    print(f"  - 残留 KIMI_*: {'WARN 是' if config_impl.get('uses_kimi') else 'OK 否'}")
    
    prd = report["findings"]["prd_consistency"]
    print(f"\nPRD 一致性:")
    print(f"  - ANTHROPIC_API_KEY: {prd.get('anthropic_mentions', 0)} 次")
    print(f"  - KIMI_API_KEY: {prd.get('kimi_mentions', 0)} 次")
    print(f"  - 状态: {'OK 一致' if prd.get('consistent') else 'WARN 需要更新'}")
    
    print("\n" + "=" * 70)
    print(f"总计发现 {total_deprecated} 处需要更新的引用")
    print("=" * 70)
    print("\n建议的修复顺序:")
    for task in report["update_plan"]["phase_b_tasks"]:
        print(f"  [{task['priority']}] {task['task']} (预计 {task['estimated_time']})")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
