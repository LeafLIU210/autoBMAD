#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行pytest测试并收集ERROR和FAIL

遍历测试文件列表，执行pytest -v --tb=short，收集ERROR和FAIL信息
仅记录有ERROR、FAIL或TIMEOUT的文件到汇总JSON
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import time


def get_timestamp():
    """生成时间戳（格式：YYYYMMDD_HHMMSS）"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def find_latest_test_files_list(fileslist_dir):
    """
    查找最新的测试文件列表

    Args:
        fileslist_dir: fileslist目录路径

    Returns:
        str: 最新的测试文件列表路径
    """
    fileslist_path = Path(fileslist_dir)
    json_files = list(fileslist_path.glob("test_files_list_*.json"))

    if not json_files:
        raise FileNotFoundError(f"在 {fileslist_dir} 中未找到测试文件列表")

    # 按修改时间排序，取最新的
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    print(f"使用测试文件列表: {latest_file.name}")

    return str(latest_file)


def load_test_files_list(file_path):
    """
    加载测试文件列表

    Args:
        file_path: JSON文件路径

    Returns:
        dict: 测试文件数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_pytest_output(output):
    """
    解析pytest输出，提取ERROR和FAIL信息

    Args:
        output: pytest输出字符串

    Returns:
        dict: 包含errors和failures的字典
    """
    result = {
        "errors": [],
        "failures": [],
        "passed": True
    }

    lines = output.split('\n')
    current_error = None
    current_failure = None

    for i, line in enumerate(lines):
        # 检测ERROR行
        if 'ERROR:' in line:
            current_error = {
                "type": "ERROR",
                "message": line.strip(),
                "line": i + 1,
                "details": []
            }
            result["errors"].append(current_error)
            result["passed"] = False

        # 检测FAILED行
        elif 'FAILED' in line and '::' in line:
            test_name = line.split(' - ')[0] if ' - ' in line else line
            current_failure = {
                "type": "FAILED",
                "message": line.strip(),
                "test_name": test_name,
                "line": i + 1,
                "details": []
            }
            result["failures"].append(current_failure)
            result["passed"] = False

        # 收集错误详情
        elif current_error is not None and line.strip():
            if not line.startswith('=') and not line.startswith('-'):
                current_error["details"].append(line.strip())

        # 收集失败详情
        elif current_failure is not None and line.strip():
            if not line.startswith('=') and not line.startswith('-'):
                current_failure["details"].append(line.strip())

    return result


def parse_unittest_output(output):
    """
    解析unittest输出，提取ERROR和FAIL信息

    Args:
        output: unittest输出字符串

    Returns:
        dict: 包含errors和failures的字典
    """
    result = {
        "errors": [],
        "failures": [],
        "passed": True
    }

    lines = output.split('\n')
    current_error = None
    current_failure = None

    for i, line in enumerate(lines):
        # 检测ERROR行
        if line.startswith('E') and ('ERROR:' in line or 'Error: ' in line):
            current_error = {
                "type": "ERROR",
                "message": line.strip(),
                "line": i + 1,
                "details": []
            }
            result["errors"].append(current_error)
            result["passed"] = False

        # 检测FAILED行
        elif line.startswith('F') and ('FAILED' in line or 'Fail: ' in line):
            test_name = line.split(' - ')[0] if ' - ' in line else line
            current_failure = {
                "type": "FAILED",
                "message": line.strip(),
                "test_name": test_name,
                "line": i + 1,
                "details": []
            }
            result["failures"].append(current_failure)
            result["passed"] = False

        # 收集错误和失败详情
        elif (current_error is not None or current_failure is not None) and line.strip():
            if not line.startswith('=') and not line.startswith('-'):
                if current_error is not None:
                    current_error["details"].append(line.strip())
                elif current_failure is not None:
                    current_failure["details"].append(line.strip())

    return result


def run_unittest_with_timeout(test_file, timeout=120):
    """
    运行unittest测试，设置超时

    Args:
        test_file: 测试文件路径
        timeout: 超时时间（秒）

    Returns:
        dict: 测试结果
    """
    result = {
        "relative_path": test_file,
        "status": "completed",
        "result": "passed",
        "errors": [],
        "failures": [],
        "execution_time": 0,
        "timestamp": datetime.now().isoformat(),
        "timeout": False,
        "framework": "unittest"
    }

    # 检查文件是否存在
    if not os.path.exists(test_file):
        result["status"] = "error"
        result["result"] = "error"
        result["execution_time"] = 0
        result["errors"].append({
            "type": "FILE_NOT_FOUND",
            "message": f"测试文件不存在: {test_file}",
            "line": 0,
            "details": [f"文件路径: {test_file}", "请检查文件路径是否正确"]
        })
        return result

    start_time = time.time()

    try:
        # 运行unittest
        process = subprocess.Popen(
            ['python', '-m', 'unittest', test_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 等待进程完成或超时
        try:
            stdout, _ = process.communicate(timeout=timeout)
            result["execution_time"] = time.time() - start_time

            # 解析输出
            parsed = parse_unittest_output(stdout)

            result["errors"] = parsed["errors"]
            result["failures"] = parsed["failures"]

            if not parsed["passed"]:
                result["result"] = "failed" if result["failures"] else "error"

        except subprocess.TimeoutExpired:
            # 超时处理
            process.kill()
            stdout, _ = process.communicate()
            result["execution_time"] = timeout
            result["status"] = "timeout"
            result["result"] = "timeout"
            result["timeout"] = True
            result["errors"].append({
                "type": "TIMEOUT",
                "message": f"测试执行超时（{timeout}秒）",
                "line": 0,
                "details": ["测试文件执行时间超过预设阈值，可能存在死循环或性能问题"]
            })

    except Exception as e:
        result["execution_time"] = time.time() - start_time
        result["status"] = "error"
        result["result"] = "error"
        result["errors"].append({
            "type": "EXECUTION_ERROR",
            "message": f"执行测试时出错: {str(e)}",
            "line": 0,
            "details": []
        })

    return result


def run_test_with_timeout(test_file, framework='pytest', timeout=120):
    """
    运行测试，支持pytest和unittest

    Args:
        test_file: 测试文件路径
        framework: 测试框架 ('pytest' 或 'unittest')
        timeout: 超时时间（秒）

    Returns:
        dict: 测试结果
    """
    if framework == 'unittest':
        return run_unittest_with_timeout(test_file, timeout)
    else:
        result = run_pytest_with_timeout(test_file, timeout)
        result["framework"] = "pytest"
        return result


def run_pytest_with_timeout(test_file, timeout=120):
    """
    运行pytest测试，设置超时

    Args:
        test_file: 测试文件路径
        timeout: 超时时间（秒）

    Returns:
        dict: 测试结果
    """
    result = {
        "relative_path": test_file,
        "status": "completed",
        "result": "passed",
        "errors": [],
        "failures": [],
        "execution_time": 0,
        "timestamp": datetime.now().isoformat(),
        "timeout": False
    }

    # 检查文件是否存在
    if not os.path.exists(test_file):
        result["status"] = "error"
        result["result"] = "error"
        result["execution_time"] = 0
        result["errors"].append({
            "type": "FILE_NOT_FOUND",
            "message": f"测试文件不存在: {test_file}",
            "line": 0,
            "details": [f"文件路径: {test_file}", "请检查文件路径是否正确"]
        })
        return result

    start_time = time.time()

    try:
        # 运行pytest
        process = subprocess.Popen(
            ['pytest', '-v', '--tb=short', test_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 等待进程完成或超时
        try:
            stdout, _ = process.communicate(timeout=timeout)
            result["execution_time"] = time.time() - start_time

            # 解析输出
            parsed = parse_pytest_output(stdout)

            result["errors"] = parsed["errors"]
            result["failures"] = parsed["failures"]

            if not parsed["passed"]:
                result["result"] = "failed" if result["failures"] else "error"

        except subprocess.TimeoutExpired:
            # 超时处理
            process.kill()
            stdout, _ = process.communicate()
            result["execution_time"] = timeout
            result["status"] = "timeout"
            result["result"] = "timeout"
            result["timeout"] = True
            result["errors"].append({
                "type": "TIMEOUT",
                "message": f"测试执行超时（{timeout}秒）",
                "line": 0,
                "details": ["测试文件执行时间超过预设阈值，可能存在死循环或性能问题"]
            })

    except Exception as e:
        result["execution_time"] = time.time() - start_time
        result["status"] = "error"
        result["result"] = "error"
        result["errors"].append({
            "type": "EXECUTION_ERROR",
            "message": f"执行测试时出错: {str(e)}",
            "line": 0,
            "details": []
        })

    return result


def save_summary_json(data, output_path):
    """
    保存汇总JSON文件

    Args:
        data: 汇总数据
        output_path: 输出文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 查找最新的测试文件列表
    fileslist_dir = os.path.join(script_dir, "fileslist")
    test_files_list_path = find_latest_test_files_list(fileslist_dir)

    print("正在加载测试文件列表...")
    test_data = load_test_files_list(test_files_list_path)
    test_files = test_data["test_files"]

    # 获取项目根目录
    project_root = test_data.get("project_root", os.path.dirname(script_dir))

    print(f"项目根目录: {project_root}")
    print(f"开始执行 {len(test_files)} 个测试文件...")
    print("超时设置: 120秒")

    # 初始化汇总数据
    summary_data = {
        "scan_timestamp": test_data.get("scan_timestamp", ""),
        "test_start_time": datetime.now().isoformat(),
        "timestamp": get_timestamp(),
        "total_files": len(test_files),
        "files_with_errors": [],
        "summary": {
            "total": len(test_files),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "timeouts": 0
        }
    }

    # 执行测试
    for i, test_file_info in enumerate(test_files, 1):
        # 优先使用 absolute_path，如果不存在则使用 relative_path
        test_file_path = test_file_info.get("absolute_path") or test_file_info.get("relative_path")
        rel_path = test_file_info.get("relative_path", test_file_path)

        # 显示进度
        progress = (i / len(test_files)) * 100
        print(f"\n[{i}/{len(test_files)}] ({progress:.1f}%) 正在测试: {rel_path}")

        # 运行测试
        test_result = run_pytest_with_timeout(test_file_path)

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
            print("  [TIMEOUT] 超时")

    # 保存最终汇总JSON
    final_timestamp = get_timestamp()
    final_output_path = os.path.join(script_dir, "summaries", f"test_results_summary_{final_timestamp}.json")

    try:
        save_summary_json(summary_data, final_output_path)
        print(f"\n[OK] 测试结果汇总已保存到: {final_output_path}")
        print("\n=== 测试汇总 ===")
        print(f"总计: {summary_data['summary']['total']} 个文件")
        print(f"通过: {summary_data['summary']['passed']} 个")
        print(f"失败: {summary_data['summary']['failed']} 个")
        print(f"错误: {summary_data['summary']['errors']} 个")
        print(f"超时: {summary_data['summary']['timeouts']} 个")
        print(f"有问题文件: {len(summary_data['files_with_errors'])} 个")

        if summary_data['files_with_errors']:
            print("\n[INFO] 有问题的文件已保存到汇总JSON中")
            print("请运行 debug_test_with_pytest.py (可选调试)")
            print("然后运行 generate_prompt_and_fix.py 进行自动修复")

    except Exception as e:
        print(f"\n[ERROR] 保存最终汇总文件时出错: {e}")
        raise


if __name__ == "__main__":
    main()
