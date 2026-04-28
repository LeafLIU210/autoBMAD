"""
Phase A - P1-3 测试环境权限问题调试工具
========================================
研究 pytest-qt 临时目录权限问题及其影响

使用方法:
    python tools/phase_a_research/p1_test_investigator.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


def run_pytest_dry_run() -> dict[str, Any]:
    """Run pytest collection to identify test files without executing."""
    print("\n[Phase A - P1-3] 收集测试信息...")
    
    result = subprocess.run(
        ["python", "-m", "pytest", "--collect-only", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    findings = {
        "collection_success": result.returncode == 0,
        "stdout": result.stdout[:2000] if result.stdout else "",
        "stderr": result.stderr[:2000] if result.stderr else "",
        "test_count": 0,
        "error_patterns": [],
    }
    
    # Count test files
    if result.stdout:
        lines = result.stdout.strip().split("\n")
        test_files = [l for l in lines if "::" in l]
        findings["test_count"] = len(test_files)
    
    # Check for permission errors
    if "PermissionError" in result.stderr or "WinError 5" in result.stderr:
        findings["error_patterns"].append("PermissionError/WinError 5")
    
    print(f"  收集到的测试数量: {findings['test_count']}")
    if not findings["collection_success"]:
        print(f"  收集失败: {findings['stderr'][:200]}")
    
    return findings


def run_architecture_tests() -> dict[str, Any]:
    """Run architecture tests specifically."""
    print("\n[Phase A - P1-3] 运行架构测试...")
    
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/architecture", "-v"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    
    findings = {
        "returncode": result.returncode,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "failures": [],
    }
    
    # Parse output
    if result.stdout:
        # Look for PASSED/FAILED/ERROR patterns
        for line in result.stdout.split("\n"):
            if "PASSED" in line:
                findings["passed"] += 1
            elif "FAILED" in line:
                findings["failed"] += 1
                findings["failures"].append(line.strip())
            elif "ERROR" in line:
                findings["errors"] += 1
    
    print(f"  通过: {findings['passed']}, 失败: {findings['failed']}, 错误: {findings['errors']}")
    
    # Specifically check for _run_async failure
    for failure in findings["failures"]:
        if "_run_async" in failure or "test_no_run_async_bridge_anywhere" in failure:
            print(f"  FAIL 发现 _run_async bridge 违规: {failure}")
    
    return findings


def check_temp_directory_permissions() -> dict[str, Any]:
    """Check temp directory permissions and pytest-basetemp settings."""
    print("\n[Phase A - P1-3] 检查临时目录权限...")
    
    findings = {
        "system_temp": tempfile.gettempdir(),
        "temp_writable": False,
        "pytest_basetemp": None,
        "conftest_exists": False,
    }
    
    # Check if system temp is writable
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / "docuswarm_test_write.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
        findings["temp_writable"] = True
    except PermissionError:
        findings["temp_writable"] = False
    
    print(f"  系统临时目录: {findings['system_temp']}")
    print(f"  可写性: {'OK' if findings['temp_writable'] else 'FAIL'}")
    
    # Check for conftest.py with basetemp
    conftest_paths = [
        PROJECT_ROOT / "conftest.py",
        PROJECT_ROOT / "tests" / "conftest.py",
    ]
    for path in conftest_paths:
        if path.exists():
            findings["conftest_exists"] = True
            content = path.read_text(encoding="utf-8")
            if "basetemp" in content:
                findings["pytest_basetemp"] = "configured"
                print(f"  发现 conftest.py: {path}")
            break
    
    # Check pytest.ini or pyproject.toml for basetemp
    pytest_ini = PROJECT_ROOT / "pytest.ini"
    pyproject_toml = PROJECT_ROOT / "pyproject.toml"
    
    if pytest_ini.exists():
        content = pytest_ini.read_text(encoding="utf-8")
        if "basetemp" in content:
            findings["pytest_basetemp"] = "configured in pytest.ini"
    
    if pyproject_toml.exists():
        content = pyproject_toml.read_text(encoding="utf-8")
        if "basetemp" in content:
            findings["pytest_basetemp"] = "configured in pyproject.toml"
    
    return findings


def analyze_coverage_hotspots() -> dict[str, Any]:
    """Analyze coverage for hotspot modules."""
    print("\n[Phase A - P1-3] 分析热点模块覆盖率...")
    
    hotspot_modules = [
        "autoBMAD/docuswarm/pipeline/orchestrator.py",
        "autoBMAD/docuswarm/cli/services/pipeline_service.py",
        "autoBMAD/docuswarm/nodes/dual_agent.py",
        "autoBMAD/docuswarm/storage/state_manager.py",
        "autoBMAD/docuswarm/node_execution/executor.py",
        "autoBMAD/docuswarm/context/validator.py",
        "autoBMAD/docuswarm/llm/session_manager.py",
    ]
    
    findings = {
        "hotspots": [],
        "coverage_command": "coverage report -m " + " ".join(hotspot_modules),
    }
    
    # Try to run coverage if available
    result = subprocess.run(
        ["python", "-m", "coverage", "report", "-m"] + hotspot_modules,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    if result.returncode == 0 and result.stdout:
        print("  覆盖率报告:")
        for line in result.stdout.split("\n"):
            if any(mod.split("/")[-1] in line for mod in hotspot_modules):
                print(f"    {line}")
                # Parse percentage
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        coverage_pct = int(parts[-3].replace("%", ""))
                        module_name = parts[0]
                        findings["hotspots"].append({
                            "module": module_name,
                            "coverage": coverage_pct,
                        })
                    except (ValueError, IndexError):
                        pass
    else:
        print("  无法获取覆盖率报告 (coverage 模块可能未安装或无数据)")
        # Use static line counts as proxy
        for module in hotspot_modules:
            mod_path = PROJECT_ROOT / module
            if mod_path.exists():
                line_count = len(mod_path.read_text(encoding="utf-8").split("\n"))
                findings["hotspots"].append({
                    "module": module,
                    "lines": line_count,
                    "coverage": "unknown",
                })
                print(f"    {module}: {line_count} 行")
    
    return findings


def create_test_recommendations() -> dict[str, Any]:
    """Create recommendations for fixing test issues."""
    return {
        "temp_permission_fixes": [
            {
                "option": "配置 basetemp",
                "command": "pytest --basetemp=./.pytest-temp",
                "description": "使用项目内临时目录避免权限问题",
            },
            {
                "option": "环境变量",
                "command": "set PYTEST_DEBUG_TEMPROOT=./tmp",
                "description": "设置 pytest 临时根目录 (Windows)",
            },
            {
                "option": "清理残留目录",
                "command": "rmdir /s /q %TEMP%\\pytest-of-*",
                "description": "手动清理残留临时目录",
            },
        ],
        "smoke_tests_to_add": [
            "tests/smoke/test_start_pipeline.py - 主启动路径",
            "tests/smoke/test_resume_pipeline.py - 恢复路径",
            "tests/smoke/test_cancel_pipeline.py - 取消路径",
            "tests/smoke/test_escalation.py - 升级路径",
        ],
        "coverage_thresholds": {
            "pipeline/orchestrator.py": "50%",
            "storage/state_manager.py": "40%",
            "nodes/dual_agent.py": "40%",
            "node_execution/executor.py": "30%",
        },
    }


def main() -> int:
    """Run all Phase A test investigations."""
    print("=" * 70)
    print("Phase A 测试环境权限问题深度调试")
    print("=" * 70)
    print("目标: 分析 Finding P1-3 的测试阻断原因和修复建议")
    
    report = {
        "title": "Phase A 测试环境权限问题深度研究报告",
        "description": "针对 Finding P1-3 的测试权限问题分析和修复建议",
        "timestamp": "2026-04-04",
        "findings": {},
    }
    
    # Check temp permissions
    report["findings"]["temp_permissions"] = check_temp_directory_permissions()
    
    # Run pytest dry-run
    report["findings"]["pytest_collection"] = run_pytest_dry_run()
    
    # Run architecture tests
    report["findings"]["architecture_tests"] = run_architecture_tests()
    
    # Analyze coverage
    report["findings"]["coverage_analysis"] = analyze_coverage_hotspots()
    
    # Recommendations
    report["recommendations"] = create_test_recommendations()
    
    # Write report
    output_path = PROJECT_ROOT / "docs" / "research" / "phase_a_test_issues_analysis.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[完成] 分析报告已保存: {output_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Phase A 测试问题摘要")
    print("=" * 70)
    
    temp = report["findings"]["temp_permissions"]
    print(f"\n临时目录权限:")
    print(f"  - 系统临时目录: {temp['system_temp']}")
    print(f"  - 可写性: {'OK' if temp['temp_writable'] else 'FAIL'}")
    if temp.get("pytest_basetemp"):
        print(f"  - basetemp 配置: {temp['pytest_basetemp']}")
    else:
        print(f"  - basetemp 配置: 未配置 (建议添加)")
    
    arch = report["findings"]["architecture_tests"]
    print(f"\n架构测试状态:")
    print(f"  - 通过: {arch['passed']}")
    print(f"  - 失败: {arch['failed']}")
    print(f"  - 错误: {arch['errors']}")
    if arch['failed'] > 0:
        print(f"  FAIL 存在架构违规 (如 _run_async bridge)")
    
    cov = report["findings"]["coverage_analysis"]
    print(f"\n热点模块覆盖率:")
    for hotspot in cov.get("hotspots", []):
        cov_val = hotspot.get("coverage", "unknown")
        if cov_val == "unknown":
            print(f"  - {hotspot['module']}: {hotspot.get('lines', '?')} 行 (覆盖率未知)")
        else:
            status = "OK" if isinstance(cov_val, int) and cov_val >= 40 else "FAIL"
            print(f"  {status} {hotspot['module']}: {cov_val}%")
    
    print("\n" + "=" * 70)
    print("修复建议:")
    print("  1. 临时目录权限:")
    for fix in report["recommendations"]["temp_permission_fixes"]:
        print(f"     - {fix['option']}: {fix['command']}")
    print("  2. 需要补充的冒烟测试:")
    for test in report["recommendations"]["smoke_tests_to_add"]:
        print(f"     - {test}")
    print("  3. 覆盖率目标:")
    for mod, threshold in report["recommendations"]["coverage_thresholds"].items():
        print(f"     - {mod}: {threshold}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
