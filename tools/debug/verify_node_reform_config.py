#!/usr/bin/env python3
"""
节点 Deep Reform 配置合规验证脚本

用于验证 F7 和 F8 问题:
- F7: Analyst 节点任务语义是否按方案重构
- F8: 模板配置是否完整

Usage:
    python tools/debug/verify_node_reform_config.py [node_id]
    python tools/debug/verify_node_reform_config.py --all

Example:
    python tools/debug/verify_node_reform_config.py analyst
    python tools/debug/verify_node_reform_config.py --all
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.nodes.loader import NodeLoader


# Expected configurations per Deep Reform spec
EXPECTED_ANALYST_TASK = {
    "name": "create-product-brief",
    "skill_ref": "bmad-product-brief",
}

EXPECTED_ANALYST_SKILLS_WHITELIST = [
    "bmad-product-brief",
    "bmad-domain-research",
    "bmad-market-research",
    "bmad-advanced-elicitation",
]


def check_f7_analyst_task_semantics(config, node_id: str) -> list[str]:
    """Check F7: Analyst task semantics compliance."""
    issues = []
    
    if node_id != "analyst":
        return issues
    
    print("\n📋 F7 检查: Analyst 任务语义重构")
    print("-" * 40)
    
    task = config.task
    
    # Check task name
    if task.name != EXPECTED_ANALYST_TASK["name"]:
        issues.append(
            f"❌ task.name = '{task.name}' (期望: '{EXPECTED_ANALYST_TASK['name']}')"
        )
    else:
        print(f"   ✅ task.name = '{task.name}'")
    
    # Check skill_ref
    if task.skill_ref != EXPECTED_ANALYST_TASK["skill_ref"]:
        issues.append(
            f"❌ task.skill_ref = '{task.skill_ref}' (期望: '{EXPECTED_ANALYST_TASK['skill_ref']}')"
        )
    else:
        print(f"   ✅ task.skill_ref = '{task.skill_ref}'")
    
    # Check skills whitelist
    actual_whitelist = config.tool_permissions.skills.whitelist
    print(f"\n   Skills 白名单:")
    for skill in EXPECTED_ANALYST_SKILLS_WHITELIST:
        if skill in actual_whitelist:
            print(f"     ✅ {skill}")
        else:
            print(f"     ❌ {skill} (缺失)")
            issues.append(f"❌ Skill '{skill}' 不在白名单中")
    
    if not issues:
        print("\n   ✅ F7 检查通过")
    
    return issues


def check_f8_template_alignment(config, node_id: str) -> list[str]:
    """Check F8: Template alignment configuration."""
    issues = []
    
    print("\n📋 F8 检查: 模板对齐配置")
    print("-" * 40)
    
    deliverable = config.deliverable
    
    # Check template configuration fields
    print(f"   template_title: {deliverable.template_title or '(未设置)'}")
    print(f"   output_filename: {deliverable.output_filename or '(未设置)'}")
    print(f"   document_types: {deliverable.document_types or []}")
    print(f"   max_deliverables: {deliverable.max_deliverables}")
    
    # Check if template file exists
    template_file = project_root / "autoBMAD" / "docuswarm" / "templates" / f"{node_id}_templates.yaml"
    if template_file.exists():
        print(f"\n   ✅ 模板文件存在: {template_file.relative_to(project_root)}")
        
        # Try to load template
        try:
            import yaml
            with open(template_file, encoding="utf-8") as f:
                template_data = yaml.safe_load(f)
            
            templates = template_data.get("templates", [])
            standards = template_data.get("standards", {})
            
            print(f"   定义模板数: {len(templates)}")
            for t in templates:
                print(f"     - {t.get('template_id')}: {t.get('title')}")
            
            if standards:
                print(f"\n   文档标准:")
                for key, value in standards.items():
                    print(f"     - {key}: {value}")
        except Exception as e:
            issues.append(f"❌ 模板文件解析失败: {e}")
    else:
        issues.append(f"❌ 模板文件缺失: {template_file.relative_to(project_root)}")
    
    # Check TemplateLoader path
    from autoBMAD.docuswarm.prompts.template_loader import TemplateLoader
    loader_path = TemplateLoader.DEFAULT_TEMPLATES_DIR
    expected_path = project_root / "autoBMAD" / "docuswarm" / "templates"
    
    print(f"\n   TemplateLoader 默认路径:")
    print(f"     当前: {loader_path}")
    print(f"     期望: {expected_path}")
    
    if loader_path != expected_path:
        issues.append(
            f"❌ TemplateLoader 路径不匹配 - 当前指向 prompts/templates/，"
            f"但模板文件在 docuswarm/templates/"
        )
    
    if not issues:
        print("\n   ⚠️ F8 配置存在，但运行时可能未接线")
    
    return issues


def check_shared_context_config(config, node_id: str) -> list[str]:
    """Check shared context configuration (F6 related)."""
    issues = []
    
    print("\n📋 F6 检查: Shared Context 配置")
    print("-" * 40)
    
    sc = config.tool_permissions.shared_context
    
    print(f"   enabled: {sc.enabled}")
    print(f"   operations: {sc.operations}")
    print(f"   allowed_keys: {sc.allowed_keys}")
    
    if sc.enabled:
        print("\n   ✅ Shared Context 已启用")
        if not sc.operations:
            issues.append("❌ operations 列表为空")
    else:
        print("\n   ⚠️ Shared Context 未启用")
    
    return issues


def verify_node_config(node_id: str) -> dict:
    """Verify Deep Reform configuration for a node."""
    print(f"\n{'='*60}")
    print(f"🔍 验证节点配置: {node_id.upper()}")
    print(f"{'='*60}")
    
    config = NodeLoader.load(node_id)
    
    all_issues = []
    
    # F6 check
    issues = check_shared_context_config(config, node_id)
    all_issues.extend(issues)
    
    # F7 check (only for analyst)
    if node_id == "analyst":
        issues = check_f7_analyst_task_semantics(config, node_id)
        all_issues.extend(issues)
    
    # F8 check
    issues = check_f8_template_alignment(config, node_id)
    all_issues.extend(issues)
    
    # Summary
    print(f"\n📊 验证结果")
    print("-" * 40)
    if all_issues:
        print(f"   发现 {len(all_issues)} 个问题:")
        for issue in all_issues:
            print(f"     {issue}")
    else:
        print("   ✅ 配置检查通过")
    
    return {
        "node_id": node_id,
        "issues": all_issues,
        "passed": len(all_issues) == 0
    }


def print_summary(results: list[dict]):
    """Print verification summary."""
    print(f"\n{'='*60}")
    print("📋 验证汇总")
    print(f"{'='*60}")
    
    total_issues = sum(len(r["issues"]) for r in results)
    
    for r in results:
        status = "✅" if r["passed"] else "❌"
        issue_count = len(r["issues"])
        print(f"\n{status} {r['node_id'].upper()} ({issue_count} 个问题)")
        for issue in r["issues"]:
            print(f"   {issue}")
    
    print(f"\n{'='*60}")
    if total_issues == 0:
        print("✅ 所有节点配置检查通过")
    else:
        print(f"❌ 共发现 {total_issues} 个配置问题")
        print("\n问题分类:")
        print("   F6: update_context MCP 链路未接线")
        print("   F7: Analyst 任务语义未重构")
        print("   F8: 模板对齐停留在配置层")
    print(f"{'='*60}")


def main():
    """Main entry point."""
    nodes = ["analyst", "pm", "ux", "architect", "po"]
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            pass  # Use all nodes
        else:
            nodes = [sys.argv[1]]
    
    print("🔧 节点 Deep Reform 配置合规验证")
    print("=" * 60)
    print("验证目标:")
    print("  - F6: Shared Context 配置")
    print("  - F7: Analyst 任务语义重构")
    print("  - F8: 模板对齐配置")
    
    results = []
    for node_id in nodes:
        try:
            result = verify_node_config(node_id)
            results.append(result)
        except Exception as e:
            print(f"\n❌ 验证 {node_id} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print_summary(results)
    
    # Exit with error code if any check failed
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
