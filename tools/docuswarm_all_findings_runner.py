"""
DocuSwarm 全量发现问题综合运行器

运行所有 F1-F6 调试工具并生成综合报告

用法:
    python tools/docuswarm_all_findings_runner.py
    python tools/docuswarm_all_findings_runner.py --json  # JSON 格式输出
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"


# 所有发现调试工具
FINDING_TOOLS = [
    ("F1", "docuswarm_f1_multidoc_validator_debugger.py", "多文档验证问题"),
    ("F2", "docuswarm_f2_update_context_debugger.py", "update_context MCP Server 问题"),
    ("F3", "docuswarm_f3_sdk_skills_debugger.py", "SDK Skills 发现机制问题"),
    ("F4", "docuswarm_f4_template_mapping_debugger.py", "模板运行时映射问题"),
    ("F5", "docuswarm_f5_allowed_keys_debugger.py", "shared_context.allowed_keys 传递问题"),
    ("F6", "docuswarm_f6_config_drift_debugger.py", "Analyst 节点配置漂移"),
]


def run_tool(tool_name: str) -> dict[str, Any]:
    """运行单个调试工具."""
    tool_path = TOOLS_DIR / tool_name
    
    if not tool_path.exists():
        return {
            "status": "error",
            "returncode": -1,
            "stdout": "",
            "stderr": f"Tool not found: {tool_path}",
        }
    
    try:
        result = subprocess.run(
            [sys.executable, str(tool_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=PROJECT_ROOT,
        )
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "returncode": -1,
            "stdout": "",
            "stderr": "Tool execution timed out",
        }
    except Exception as e:
        return {
            "status": "error",
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def run_all_findings():
    """运行所有发现调试工具."""
    print("=" * 80)
    print("DocuSwarm 全量发现问题综合运行器")
    print("=" * 80)
    print(f"\n项目根目录: {PROJECT_ROOT}")
    print(f"工具目录: {TOOLS_DIR}")
    print(f"发现项数量: {len(FINDING_TOOLS)}")
    
    results = {}
    passed = 0
    failed = 0
    errors = 0
    
    for finding_id, tool_name, description in FINDING_TOOLS:
        print(f"\n{'=' * 80}")
        print(f"运行 {finding_id}: {description}")
        print(f"工具: {tool_name}")
        print("=" * 80)
        
        result = run_tool(tool_name)
        results[finding_id] = {
            "description": description,
            "tool": tool_name,
            **result,
        }
        
        # 打印输出
        if result["stdout"]:
            print(result["stdout"])
        if result["stderr"]:
            print(f"\n[STDERR]\n{result['stderr']}", file=sys.stderr)
        
        # 统计
        if result["status"] == "success":
            passed += 1
            print(f"\n✓ {finding_id} 通过")
        elif result["status"] == "failed":
            failed += 1
            print(f"\n✗ {finding_id} 发现问题")
        else:
            errors += 1
            print(f"\n⚠ {finding_id} 执行出错")
    
    # 综合报告
    print("\n" + "=" * 80)
    print("综合报告")
    print("=" * 80)
    print(f"""
执行统计:
- 总发现项: {len(FINDING_TOOLS)}
- 通过 (无问题): {passed}
- 失败 (发现问题): {failed}
- 错误: {errors}

各发现项状态:
""")
    
    for finding_id, description, _ in [(f[0], f[2], f[1]) for f in FINDING_TOOLS]:
        result = results[finding_id]
        status_icon = {
            "success": "✓",
            "failed": "✗",
            "timeout": "⏱",
            "error": "⚠",
        }.get(result["status"], "?")
        print(f"  {status_icon} {finding_id}: {description}")
    
    return results, passed, failed, errors


def generate_json_report(results: dict[str, Any]) -> str:
    """生成 JSON 格式报告."""
    report = {
        "summary": {
            "total_findings": len(FINDING_TOOLS),
            "passed": sum(1 for r in results.values() if r["status"] == "success"),
            "failed": sum(1 for r in results.values() if r["status"] == "failed"),
            "errors": sum(1 for r in results.values() if r["status"] not in ("success", "failed")),
        },
        "findings": {
            finding_id: {
                "description": result["description"],
                "status": result["status"],
                "returncode": result["returncode"],
            }
            for finding_id, result in results.items()
        },
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def generate_markdown_report(results: dict[str, Any]) -> str:
    """生成 Markdown 格式报告."""
    lines = [
        "# DocuSwarm 全量发现问题综合报告",
        "",
        f"**生成时间**: 自动运行",
        f"**项目路径**: {PROJECT_ROOT}",
        "",
        "## 执行摘要",
        "",
        f"- 总发现项: {len(FINDING_TOOLS)}",
        f"- 通过 (无问题): {sum(1 for r in results.values() if r['status'] == 'success')}",
        f"- 失败 (发现问题): {sum(1 for r in results.values() if r['status'] == 'failed')}",
        f"- 错误: {sum(1 for r in results.values() if r['status'] not in ('success', 'failed'))}",
        "",
        "## 各发现项状态",
        "",
        "| 发现项 | 描述 | 状态 |",
        "|--------|------|------|",
    ]
    
    for finding_id, description, _ in [(f[0], f[2], f[1]) for f in FINDING_TOOLS]:
        result = results[finding_id]
        status = result["status"]
        status_badge = {
            "success": "✅ 通过",
            "failed": "❌ 发现问题",
            "timeout": "⏱️ 超时",
            "error": "⚠️ 错误",
        }.get(status, "❓ 未知")
        lines.append(f"| {finding_id} | {description} | {status_badge} |")
    
    lines.extend([
        "",
        "## 详细结果",
        "",
    ])
    
    for finding_id, result in results.items():
        lines.extend([
            f"### {finding_id}: {result['description']}",
            "",
            f"- **工具**: `{result['tool']}`",
            f"- **状态**: {result['status']}",
            f"- **返回码**: {result['returncode']}",
            "",
        ])
    
    lines.extend([
        "",
        "## 建议修复优先级",
        "",
        "1. **HIGH**: F1 (多文档验证), F2 (update_context), F3 (SDK Skills)",
        "2. **MEDIUM**: F4 (模板映射), F5 (allowed_keys)",
        "3. **LOW**: F6 (配置漂移)",
        "",
        "---",
        "",
        "*本报告由 docuswarm_all_findings_runner.py 自动生成*",
    ])
    
    return "\n".join(lines)


def main():
    """主函数."""
    parser = argparse.ArgumentParser(
        description="DocuSwarm 全量发现问题综合运行器"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式报告",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="输出 Markdown 格式报告",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="输出文件路径",
    )
    args = parser.parse_args()
    
    results, passed, failed, errors = run_all_findings()
    
    # 生成报告
    if args.json:
        report = generate_json_report(results)
    elif args.markdown:
        report = generate_markdown_report(results)
    else:
        # 默认只打印统计信息
        print(f"\n\n执行完成: {passed} 通过, {failed} 发现问题, {errors} 错误")
        return 0 if failed == 0 and errors == 0 else 1
    
    # 输出报告
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"\n报告已保存: {output_path}")
    else:
        print("\n" + "=" * 80)
        print("报告")
        print("=" * 80)
        print(report)
    
    return 0 if failed == 0 and errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
