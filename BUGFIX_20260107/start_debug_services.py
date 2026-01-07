#!/usr/bin/env python3
"""
Start Debug Services

启动调试服务器和仪表板服务

Usage:
    python start_debug_services.py [--server] [--dashboard] [--port PORT]
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def start_debug_server(port: int = 5678):
    """启动 debugpy 服务器"""
    from debugpy_integration import DebugpyServer

    print(f"Starting debugpy server on port {port}...")
    server = DebugpyServer()
    await server.start(port=port)
    print(f"Debugpy server started on {server.server_info['host']}:{server.server_info['port']}")
    print("Waiting for debugger to attach...")
    print("Press Ctrl+C to stop")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down debugpy server...")
        await server.stop()
        print("Debugpy server stopped")


async def start_dashboard(port: int = 8080):
    """启动调试仪表板"""
    from enhanced_debug_suite import DebugDashboard

    print(f"Starting debug dashboard on port {port}...")
    dashboard = DebugDashboard(port=port)
    await dashboard.start()
    print(f"Debug dashboard started on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down debug dashboard...")
        await dashboard.stop()
        print("Debug dashboard stopped")


async def start_all_services(server_port: int = 5678, dashboard_port: int = 8080):
    """启动所有服务"""
    print("Starting all debug services...")
    print(f"  Debugpy server: {server_port}")
    print(f"  Debug dashboard: {dashboard_port}")
    print()

    # 创建任务
    server_task = asyncio.create_task(start_debug_server(server_port))
    dashboard_task = asyncio.create_task(start_dashboard(dashboard_port))

    try:
        await asyncio.gather(server_task, dashboard_task)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        server_task.cancel()
        dashboard_task.cancel()
        try:
            await server_task
            await dashboard_task
        except asyncio.CancelledError:
            pass
        print("All services stopped")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Start debugpy server and dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_debug_services.py                    # Start both services
  python start_debug_services.py --server           # Start only server
  python start_debug_services.py --dashboard        # Start only dashboard
  python start_debug_services.py --port 5679        # Custom port
  python start_debug_services.py --server --port 5679 --dashboard-port 8081
        """
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="Start debugpy server (default: both)"
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start debug dashboard (default: both)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5678,
        help="Debugpy server port (default: 5678)"
    )

    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=8080,
        help="Debug dashboard port (default: 8080)"
    )

    args = parser.parse_args()

    # 确定要启动的服务
    start_server = args.server or not args.dashboard
    start_dashboard_flag = args.dashboard or not args.server

    if start_server and start_dashboard_flag:
        asyncio.run(start_all_services(args.port, args.dashboard_port))
    elif start_server:
        asyncio.run(start_debug_server(args.port))
    elif start_dashboard_flag:
        asyncio.run(start_dashboard(args.dashboard_port))
    else:
        print("No services specified to start")
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServices interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
