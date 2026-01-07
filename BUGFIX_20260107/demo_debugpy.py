#!/usr/bin/env python3
"""
Demo script for BUGFIX_20260107 debugpy integration

演示 debugpy 集成的示例脚本

Usage:
    python demo_debugpy.py
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def demo_async_operation():
    """演示异步操作"""
    print("Starting async operation...")

    # 模拟一些工作
    for i in range(5):
        print(f"  Working on task {i+1}/5")
        await asyncio.sleep(0.5)

    print("Async operation completed!")
    return "demo_result"


async def main():
    """主演示函数"""
    print("=" * 80)
    print("BUGFIX_20260107 DEBUGPY INTEGRATION DEMO")
    print("=" * 80)
    print()

    # 1. 演示 AsyncDebugger
    print("1. Creating AsyncDebugger...")
    from enhanced_debug_suite import AsyncDebugger

    debugger = AsyncDebugger(
        log_file=Path("demo_async.log"),
        enable_remote_debug=True
    )
    print("   AsyncDebugger created successfully")
    print(f"   Remote debugging enabled: {debugger.enable_remote_debug}")
    print()

    # 2. 演示调试仪表板
    print("2. Creating DebugDashboard...")
    from enhanced_debug_suite import DebugDashboard

    dashboard = DebugDashboard(port=8080)
    print("   DebugDashboard created successfully")
    print()

    # 3. 演示 debugpy 服务器
    print("3. Creating DebugpyServer...")
    from debugpy_integration import DebugpyServer

    server = DebugpyServer()
    print(f"   DebugpyServer created: {server}")
    print()

    # 4. 演示远程调试器
    print("4. Creating RemoteDebugger...")
    from debugpy_integration import RemoteDebugger

    remote_debugger = RemoteDebugger()
    print(f"   RemoteDebugger created: {remote_debugger}")
    print()

    # 5. 演示调试异步操作
    print("5. Running debugged async operation...")
    try:
        # 注意：这个演示不会实际启动远程调试服务器
        # 在真实场景中，你需要在 IDE 中连接调试器
        result = await debugger.debug_async_operation(
            "demo_operation",
            demo_async_operation(),
            breakpoints=[("demo_debugpy.py", 42)]
        )
        print(f"   Operation result: {result}")
    except Exception as e:
        print(f"   Note: {e}")
        print("   (This is expected without a running debugger)")

    print()

    # 6. 演示指标收集
    print("6. Collecting metrics...")
    dashboard.update_metrics("demo_op", 1.0, True)
    dashboard.update_metrics("demo_op", 2.0, True)
    dashboard.update_metrics("demo_op", 0.5, False)
    dashboard.record_error("DEMO_ERROR", "This is a demo error", "demo_op")

    # 显示仪表板数据
    data = dashboard.get_dashboard_data()
    print(f"   Metrics collected: {len(data['operations']['recent'])} operations")
    print(f"   Errors recorded: {len(data['errors']['recent'])} errors")
    print()

    # 7. 显示统计信息
    print("7. Debug statistics:")
    stats = debugger.get_debug_statistics()
    print(f"   Debug operations: {stats.get('debug_operations', 0)}")
    print(f"   Remote debugging enabled: {stats.get('remote_debugging', {}).get('enabled', False)}")
    print()

    # 8. 显示摘要
    print("=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Install debugpy: pip install debugpy")
    print("2. Start the debug server: python -c \"from debugpy_integration import DebugpyServer; import asyncio; asyncio.run(DebugpyServer().start())\"")
    print("3. Connect your IDE to localhost:5678")
    print("4. Set breakpoints and debug your async code!")
    print()
    print("For more information, see:")
    print("  - DEBUGPY_INTEGRATION_FINAL_REPORT.md")
    print("  - BUGFIX_20260107_DEBUGPY_INTEGRATION_PLAN.md")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
