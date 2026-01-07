#!/usr/bin/env python3
"""
Quick Verification Script for BUGFIX_20260107 debugpy Integration

快速验证 debugpy 集成是否正常工作的脚本。

Usage:
    python quick_verify.py

This script will:
1. Check if debugpy is installed
2. Verify the debugpy integration modules can be imported
3. Test basic functionality of the enhanced debug suite
4. Generate a verification report
"""

import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test results
test_results = {
    "timestamp": time.time(),
    "tests": [],
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "overall_status": "UNKNOWN"
}


def add_test_result(name: str, status: str, message: str = "", details: Dict[str, Any] = None):
    """添加测试结果"""
    test_result = {
        "name": name,
        "status": status,  # PASS, FAIL, WARNING
        "message": message,
        "details": details or {}
    }

    test_results["tests"].append(test_result)

    if status == "PASS":
        test_results["passed"] += 1
    elif status == "FAIL":
        test_results["failed"] += 1
    elif status == "WARNING":
        test_results["warnings"] += 1


def check_debugpy_installation():
    """检查 debugpy 是否安装"""
    try:
        import debugpy
        add_test_result(
            "debugpy_installation",
            "PASS",
            f"debugpy version {debugpy.__version__} is installed",
            {"version": debugpy.__version__}
        )
        return True
    except ImportError:
        add_test_result(
            "debugpy_installation",
            "FAIL",
            "debugpy is not installed. Run: pip install debugpy",
            {}
        )
        return False


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version >= (3, 8):
        add_test_result(
            "python_version",
            "PASS",
            f"Python {version.major}.{version.minor}.{version.micro} is compatible",
            {"version": f"{version.major}.{version.minor}.{version.micro}"}
        )
        return True
    else:
        add_test_result(
            "python_version",
            "FAIL",
            f"Python {version.major}.{version.minor} is not compatible. Requires 3.8+",
            {"version": f"{version.major}.{version.minor}"}
        )
        return False


def check_required_packages():
    """检查必需的包"""
    required_packages = {
        "yaml": "pyyaml",
        "rich": "rich",
        "psutil": "psutil",
        "asyncio": "asyncio (built-in)"
    }

    all_good = True
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            add_test_result(
                f"package_{package}",
                "PASS",
                f"Package {package} is available"
            )
        except ImportError:
            add_test_result(
                f"package_{package}",
                "WARNING",
                f"Package {package} not available. Install with: pip install {pip_name}"
            )
            all_good = False

    return all_good


def check_debugpy_integration_modules():
    """检查 debugpy 集成模块"""
    modules_to_test = [
        ("debugpy_integration.debugpy_server", "DebugpyServer"),
        ("debugpy_integration.debug_client", "DebugClient"),
        ("debugpy_integration.remote_debugger", "RemoteDebugger")
    ]

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            add_test_result(
                f"module_{module_name.replace('.', '_')}",
                "PASS",
                f"Module {module_name} and class {class_name} are importable"
            )
        except ImportError as e:
            add_test_result(
                f"module_{module_name.replace('.', '_')}",
                "FAIL",
                f"Failed to import {module_name}: {e}"
            )
        except AttributeError as e:
            add_test_result(
                f"module_{module_name.replace('.', '_')}",
                "FAIL",
                f"Class {class_name} not found in {module_name}: {e}"
            )


def check_enhanced_debug_suite():
    """检查增强的调试套件"""
    modules_to_test = [
        ("enhanced_debug_suite.async_debugger", "AsyncDebugger"),
        ("enhanced_debug_suite.debug_dashboard", "DebugDashboard"),
        ("enhanced_debug_suite.cancel_scope_tracker", "CancelScopeTracker"),
        ("enhanced_debug_suite.resource_monitor", "ResourceMonitor")
    ]

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            add_test_result(
                f"module_{module_name.replace('.', '_')}",
                "PASS",
                f"Enhanced debug suite module {module_name} is importable"
            )
        except ImportError as e:
            add_test_result(
                f"module_{module_name.replace('.', '_')}",
                "FAIL",
                f"Failed to import {module_name}: {e}"
            )
        except Exception as e:
            add_test_result(
                f"module_{module_name.replace('.', '_')}",
                "WARNING",
                f"Module {module_name} imported with warnings: {e}"
            )


async def test_debugpy_server():
    """测试 debugpy 服务器"""
    try:
        from debugpy_integration import DebugpyServer

        # 创建服务器实例
        server = DebugpyServer()

        # 检查服务器属性
        if hasattr(server, "start") and hasattr(server, "stop"):
            add_test_result(
                "debugpy_server_methods",
                "PASS",
                "DebugpyServer has required methods (start, stop)"
            )
        else:
            add_test_result(
                "debugpy_server_methods",
                "FAIL",
                "DebugpyServer missing required methods"
            )

    except Exception as e:
        add_test_result(
            "debugpy_server_creation",
            "FAIL",
            f"Failed to create DebugpyServer: {e}"
        )


async def test_async_debugger():
    """测试异步调试器"""
    try:
        from enhanced_debug_suite import AsyncDebugger

        # 创建调试器实例
        debugger = AsyncDebugger()

        # 检查调试器属性
        required_attrs = ["task_tracker", "scope_monitor", "resource_monitor"]
        missing_attrs = [attr for attr in required_attrs if not hasattr(debugger, attr)]

        if not missing_attrs:
            add_test_result(
                "async_debugger_creation",
                "PASS",
                "AsyncDebugger created successfully with all required attributes"
            )
        else:
            add_test_result(
                "async_debugger_creation",
                "FAIL",
                f"AsyncDebugger missing attributes: {missing_attrs}"
            )

        # 检查是否支持远程调试
        if hasattr(debugger, "enable_remote_debug"):
            if debugger.enable_remote_debug:
                add_test_result(
                    "async_debugger_remote_debug",
                    "PASS",
                    "Remote debugging is enabled"
                )
            else:
                add_test_result(
                    "async_debugger_remote_debug",
                    "WARNING",
                    "Remote debugging is disabled (may be due to missing debugpy)"
                )
        else:
            add_test_result(
                "async_debugger_remote_debug",
                "WARNING",
                "Remote debugging attribute not found"
            )

    except Exception as e:
        add_test_result(
            "async_debugger_creation",
            "FAIL",
            f"Failed to create AsyncDebugger: {e}"
        )


async def test_debug_dashboard():
    """测试调试仪表板"""
    try:
        from enhanced_debug_suite import DebugDashboard

        # 创建仪表板实例
        dashboard = DebugDashboard()

        # 检查仪表板属性
        required_attrs = ["metrics", "system_monitor"]
        missing_attrs = [attr for attr in required_attrs if not hasattr(dashboard, attr)]

        if not missing_attrs:
            add_test_result(
                "debug_dashboard_creation",
                "PASS",
                "DebugDashboard created successfully with all required attributes"
            )
        else:
            add_test_result(
                "debug_dashboard_creation",
                "FAIL",
                f"DebugDashboard missing attributes: {missing_attrs}"
            )

        # 测试指标收集
        dashboard.update_metrics("test_operation", 1.0, True)
        dashboard.record_error("TEST_ERROR", "This is a test error", "test_operation")

        add_test_result(
            "debug_dashboard_metrics",
            "PASS",
            "DebugDashboard metrics collection working"
        )

    except Exception as e:
        add_test_result(
            "debug_dashboard_creation",
            "FAIL",
            f"Failed to create DebugDashboard: {e}"
        )


async def test_config_files():
    """测试配置文件"""
    config_dir = Path("configs")
    config_files = [
        "debugpy_config.json",
        "debug_config.yaml"
    ]

    for config_file in config_files:
        config_path = config_dir / config_file
        if config_path.exists():
            try:
                if config_file.endswith(".json"):
                    with open(config_path, "r") as f:
                        json.load(f)
                elif config_file.endswith(".yaml"):
                    import yaml
                    with open(config_path, "r") as f:
                        yaml.safe_load(f)

                add_test_result(
                    f"config_{config_file.replace('.', '_')}",
                    "PASS",
                    f"Configuration file {config_file} is valid"
                )
            except Exception as e:
                add_test_result(
                    f"config_{config_file.replace('.', '_')}",
                    "FAIL",
                    f"Configuration file {config_file} is invalid: {e}"
                )
        else:
            add_test_result(
                f"config_{config_file.replace('.', '_')}",
                "WARNING",
                f"Configuration file {config_file} not found"
            )


async def run_async_tests():
    """运行异步测试"""
    await test_debugpy_server()
    await test_async_debugger()
    await test_debug_dashboard()
    await test_config_files()


def calculate_overall_status():
    """计算总体状态"""
    if test_results["failed"] > 0:
        test_results["overall_status"] = "FAIL"
    elif test_results["warnings"] > 0:
        test_results["overall_status"] = "WARNING"
    else:
        test_results["overall_status"] = "PASS"


def print_summary():
    """打印摘要"""
    print("\n" + "=" * 80)
    print("BUGFIX_20260107 DEBUGPY INTEGRATION VERIFICATION")
    print("=" * 80)

    print(f"\nTest Results:")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")
    print(f"  Warnings: {test_results['warnings']}")
    print(f"  Total: {len(test_results['tests'])}")

    print(f"\nOverall Status: {test_results['overall_status']}")

    if test_results["failed"] > 0:
        print(f"\nFailed Tests:")
        for test in test_results["tests"]:
            if test["status"] == "FAIL":
                print(f"  [X] {test['name']}: {test['message']}")

    if test_results["warnings"] > 0:
        print(f"\nWarnings:")
        for test in test_results["tests"]:
            if test["status"] == "WARNING":
                print(f"  [!] {test['name']}: {test['message']}")

    print("\n" + "=" * 80 + "\n")


def save_report():
    """保存报告"""
    report_file = Path("debugpy_integration_verification_report.json")

    try:
        with open(report_file, "w") as f:
            json.dump(test_results, f, indent=2)
        print(f"Verification report saved to: {report_file}")
    except Exception as e:
        print(f"Failed to save report: {e}")


async def main():
    """主函数"""
    print("Starting BUGFIX_20260107 debugpy integration verification...")

    # 运行检查
    print("\n1. Checking Python version...")
    check_python_version()

    print("\n2. Checking debugpy installation...")
    debugpy_available = check_debugpy_installation()

    print("\n3. Checking required packages...")
    check_required_packages()

    print("\n4. Checking debugpy integration modules...")
    check_debugpy_integration_modules()

    print("\n5. Checking enhanced debug suite...")
    check_enhanced_debug_suite()

    print("\n6. Running async tests...")
    await run_async_tests()

    # 计算总体状态
    calculate_overall_status()

    # 打印摘要
    print_summary()

    # 保存报告
    save_report()

    # 返回退出码
    if test_results["overall_status"] == "FAIL":
        print("Verification FAILED. Please fix the issues above.")
        sys.exit(1)
    elif test_results["overall_status"] == "WARNING":
        print("Verification completed with warnings. Please review the issues above.")
        sys.exit(0)
    else:
        print("Verification PASSED. All checks successful!")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nVerification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
