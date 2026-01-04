#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本3：使用debugpy调试失败测试文件
根据汇总JSON，使用debugpy附加到pytest进程，收集调试信息
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import os


def get_timestamp():
    """生成时间戳（格式：YYYYMMDD_HHMMSS）"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def find_latest_summary_json(summaries_dir):
    """
    查找最新的汇总JSON

    Args:
        summaries_dir: summaries目录路径

    Returns:
        Path: 最新的汇总JSON文件路径
    """
    summaries_path = Path(summaries_dir)
    json_files = list(summaries_path.glob("test_results_summary_*.json"))

    if not json_files:
        raise FileNotFoundError(f"在 {summaries_dir} 中未找到测试结果汇总文件")

    # 按修改时间排序，取最新的
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    print(f"使用汇总文件: {latest_file.name}")

    return latest_file


def load_summary_json(file_path):
    """
    加载汇总JSON

    Args:
        file_path: JSON文件路径

    Returns:
        dict: 汇总数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def debug_test_file(test_file_path, debug_port=5678, timeout=120):
    """
    使用debugpy调试测试文件

    Args:
        test_file_path: 测试文件路径
        debug_port: debugpy端口
        timeout: 超时时间（秒）

    Returns:
        dict: 调试信息
    """
    debug_info = {
        "debug_session_id": f"ds_{int(time.time())}",
        "debug_port": debug_port,
        "breakpoints": [],
        "debug_log": "",
        "start_time": datetime.now().isoformat(),
        "success": False
    }

    try:
        print(f"  启动debugpy调试会话（端口 {debug_port}）...")

        # 启动debugpy调试会话
        # debugpy会监听指定端口，等待客户端连接
        process = subprocess.Popen(
            [
                "python", "-m", "debugpy",
                "--listen", f"localhost:{debug_port}",
                "--wait-for-client",
                "pytest", "-v", "--tb=short", test_file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 等待进程完成或超时
        try:
            stdout, _ = process.communicate(timeout=timeout)
            debug_info["debug_log"] = stdout
            debug_info["end_time"] = datetime.now().isoformat()
            debug_info["success"] = True
            print(f"  调试完成 ({timeout}s)")

        except subprocess.TimeoutExpired:
            # 超时处理
            process.kill()
            stdout, _ = process.communicate()
            debug_info["debug_log"] = stdout + f"\n[DEBUG] 测试执行超时（{timeout}秒）"
            debug_info["end_time"] = datetime.now().isoformat()
            debug_info["timeout"] = True
            print(f"  调试超时（{timeout}秒）")

    except Exception as e:
        debug_info["debug_log"] = f"[DEBUG ERROR] 调试错误: {str(e)}"
        debug_info["end_time"] = datetime.now().isoformat()
        debug_info["success"] = False
        print(f"  调试错误: {str(e)}")

    return debug_info


def update_summary_json(summary_data, output_path):
    """
    更新汇总JSON，添加debug_info

    Args:
        summary_data: 汇总数据
        output_path: 输出文件路径
    """
    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    summaries_dir = script_dir / "summaries"

    try:
        # 查找最新汇总JSON
        latest_summary = find_latest_summary_json(summaries_dir)
        print(f"\n=== 调试失败测试文件 ===\n")

        # 加载数据
        summary_data = load_summary_json(latest_summary)

        # 检查是否有错误文件
        error_files = summary_data.get("files_with_errors", [])
        if not error_files:
            print("[OK] 没有需要调试的失败文件！")
            return

        print(f"发现 {len(error_files)} 个失败文件，开始调试...\n")

        # 调试失败的测试文件
        for i, file_info in enumerate(error_files, 1):
            rel_path = file_info["relative_path"]
            result = file_info.get("result", "unknown")

            print(f"[{i}/{len(error_files)}] 调试文件: {rel_path}")
            print(f"  状态: {result}")

            # 获取文件路径
            test_path = file_info.get("absolute_path") or file_info.get("relative_path")

            # 执行调试
            debug_info = debug_test_file(test_path)

            # 添加调试信息到文件记录中
            file_info["debug_info"] = debug_info

            print(f"  调试结果: {'成功' if debug_info['success'] else '失败'}")
            print("")

        # 保存更新的汇总JSON
        timestamp = get_timestamp()
        output_path = summaries_dir / f"test_results_summary_debug_{timestamp}.json"
        update_summary_json(summary_data, output_path)

        print(f"\n=== 调试完成 ===")
        print(f"已更新汇总JSON: {output_path}")
        print(f"调试了 {len(error_files)} 个失败文件")

        # 显示调试摘要
        success_count = sum(1 for f in error_files if f.get("debug_info", {}).get("success", False))
        print(f"调试成功: {success_count} 个")
        print(f"调试失败: {len(error_files) - success_count} 个")

        print(f"\n[INFO] 现在可以运行 generate_prompt_and_fix.py 进行修复")

    except Exception as e:
        print(f"\n[ERROR] 调试过程出错: {str(e)}")
        raise


if __name__ == "__main__":
    main()
