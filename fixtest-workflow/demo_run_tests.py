#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示版run_tests.py - 只测试前3个文件用于演示
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加父目录到路径以便导入run_tests模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_tests import (
    get_timestamp,
    find_latest_test_files_list,
    load_test_files_list,
    run_pytest_with_timeout,
    save_summary_json
)


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 查找最新的测试文件列表
    fileslist_dir = os.path.join(script_dir, "fileslist")
    test_files_list_path = find_latest_test_files_list(fileslist_dir)

    print(f"正在加载测试文件列表...")
    test_data = load_test_files_list(test_files_list_path)
    test_files = test_data["test_files"]

    # 只测试前3个文件用于演示
    demo_files = test_files[:3]
    print(f"\n[DEMO模式] 只测试前 {len(demo_files)} 个文件进行演示")
    print(f"实际使用时请运行完整的 run_tests.py")
    print(f"超时设置: 120秒\n")

    # 初始化汇总数据
    summary_data = {
        "scan_timestamp": test_data.get("scan_timestamp", ""),
        "test_start_time": datetime.now().isoformat(),
        "timestamp": get_timestamp(),
        "total_files": len(test_files),  # 显示总数
        "demo_files_tested": len(demo_files),  # 显示演示测试的文件数
        "files_with_errors": [],
        "summary": {
            "total": len(demo_files),  # 演示模式下只统计演示的文件
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "timeouts": 0
        }
    }

    # 执行测试
    for i, test_file_info in enumerate(demo_files, 1):
        rel_path = test_file_info["relative_path"]

        # 显示进度
        progress = (i / len(demo_files)) * 100
        print(f"\n[{i}/{len(demo_files)}] ({progress:.1f}%) 正在测试: {rel_path}")

        # 运行测试
        test_result = run_pytest_with_timeout(rel_path)

        # 更新统计
        if test_result["result"] == "passed":
            summary_data["summary"]["passed"] += 1
            # 通过的文件不记录到files_with_errors
        elif test_result["result"] == "failed":
            summary_data["summary"]["failed"] += 1
            summary_data["files_with_errors"].append(test_result)
        elif test_result["result"] == "error":
            summary_data["summary"]["errors"] += 1
            summary_data["files_with_errors"].append(test_result)
        elif test_result["result"] == "timeout":
            summary_data["summary"]["timeouts"] += 1
            summary_data["files_with_errors"].append(test_result)

        # 显示结果
        if test_result["result"] == "passed":
            print(f"  [PASS] 通过 ({test_result['execution_time']:.2f}s)")
        elif test_result["result"] == "failed":
            print(f"  [FAIL] 失败 - {len(test_result['failures'])} 个失败")
        elif test_result["result"] == "error":
            print(f"  [ERROR] 错误 - {len(test_result['errors'])} 个错误")
        elif test_result["result"] == "timeout":
            print(f"  [TIMEOUT] 超时")

        # 实时保存汇总JSON
        timestamp = get_timestamp()
        output_path = os.path.join(script_dir, "summaries", f"test_results_summary_demo_{timestamp}.json")

        try:
            save_summary_json(summary_data, output_path)
        except Exception as e:
            print(f"  [WARNING] 保存汇总JSON失败: {e}")

    # 最终保存
    final_timestamp = get_timestamp()
    final_output_path = os.path.join(script_dir, "summaries", f"test_results_summary_demo_{final_timestamp}.json")

    try:
        save_summary_json(summary_data, final_output_path)
        print(f"\n[OK] 演示测试结果汇总已保存到: {final_output_path}")
        print(f"\n=== 演示测试汇总 ===")
        print(f"总计测试文件: {summary_data['summary']['total']} 个")
        print(f"通过: {summary_data['summary']['passed']} 个")
        print(f"失败: {summary_data['summary']['failed']} 个")
        print(f"错误: {summary_data['summary']['errors']} 个")
        print(f"超时: {summary_data['summary']['timeouts']} 个")
        print(f"有问题文件: {len(summary_data['files_with_errors'])} 个")

        if summary_data['files_with_errors']:
            print(f"\n[INFO] 有问题的文件已保存到汇总JSON中")
            print(f"请运行 fix_tests.ps1 进行自动修复")
        else:
            print(f"\n[OK] 所有演示测试都通过了！")

    except Exception as e:
        print(f"\n[ERROR] 保存最终汇总文件时出错: {e}")
        raise


if __name__ == "__main__":
    main()
