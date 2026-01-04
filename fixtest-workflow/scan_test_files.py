#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描测试文件生成JSON列表

专门扫描tests目录，生成JSON格式的测试文件路径列表
并提供详细的测试文件分析报告
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path


def get_timestamp():
    """生成时间戳（格式：YYYYMMDD_HHMMSS）"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def detect_test_framework(file_path):
    """
    检测测试文件使用的框架

    Args:
        file_path: 测试文件路径

    Returns:
        str: 'pytest' 或 'unittest'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)

        if 'import unittest' in content or 'from unittest' in content:
            return 'unittest'
        elif 'import pytest' in content:
            return 'pytest'
        else:
            return 'pytest'
    except Exception:
        return 'pytest' 


def scan_test_files(root_dir):
    """
    递归扫描tests目录中的测试文件

    Args:
        root_dir: 项目根目录

    Returns:
        dict: 包含测试文件列表和分类信息的字典
    """
    test_files = []
    categories = {}
    total_size = 0

    # 确保路径是Path对象
    root_path = Path(root_dir)
    tests_dir = root_path / 'tests'

    # 检查tests目录是否存在
    if not tests_dir.exists():
        print(f"[ERROR] tests目录不存在: {tests_dir}")
        return None

    print(f"正在扫描tests目录: {tests_dir}")

    # 递归遍历tests目录
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            # 只匹配test_*.py文件
            if file.startswith('test_') and file.endswith('.py'):
                # 计算相对路径（使用正斜杠）
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, root_dir)
                rel_path_normalized = rel_path.replace('\\', '/')

                # 获取文件大小
                file_size = os.path.getsize(abs_path)
                total_size += file_size

                # 分类统计
                category = os.path.dirname(rel_path_normalized)
                if category not in categories:
                    categories[category] = {
                        'count': 0,
                        'files': [],
                        'total_size': 0
                    }

                # 计算行数
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                except Exception:
                    line_count = 0

                file_info = {
                    "relative_path": rel_path_normalized,
                    "absolute_path": abs_path,
                    "file_size": file_size,
                    "file_name": file,
                    "line_count": line_count,
                    "category": category,
                    "framework": detect_test_framework(abs_path)
                }

                test_files.append(file_info)
                categories[category]['count'] += 1
                categories[category]['files'].append(file_info)
                categories[category]['total_size'] += file_size

    # 按文件大小排序
    test_files.sort(key=lambda x: x['file_size'], reverse=True)

    # 统计大文件（>1500行）
    large_files = [f for f in test_files if f['line_count'] > 1500]

    # 统计小文件（<100行）
    small_files = [f for f in test_files if f['line_count'] < 100]

    return {
        'files': test_files,
        'categories': categories,
        'total_count': len(test_files),
        'total_size': total_size,
        'large_files': large_files,
        'small_files': small_files
    }


def save_to_json(data, output_path):
    """
    保存数据到JSON文件

    Args:
        data: 要保存的数据
        output_path: 输出文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    # 获取项目根目录（脚本所在目录的父目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # 扫描测试文件
    print(f"正在扫描测试文件...")
    print(f"项目根目录: {project_root}")

    scan_result = scan_test_files(project_root)

    if not scan_result:
        print("未找到任何测试文件！")
        return

    test_files = scan_result["files"]
    print(f"找到 {len(test_files)} 个测试文件")

    # 生成时间戳
    timestamp = get_timestamp()

    # 准备输出数据
    output_data = {
        "scan_timestamp": datetime.now().isoformat(),
        "timestamp": timestamp,
        "project_root": project_root,
        "total_files": len(test_files),
        "test_files": test_files
    }

    # 保存到fileslist文件夹
    output_path = os.path.join(script_dir, "fileslist", f"test_files_list_{timestamp}.json")

    try:
        save_to_json(output_data, output_path)
        print(f"[OK] 测试文件列表已保存到: {output_path}")
        print(f"  - 总计: {len(test_files)} 个文件")
        print(f"  - 时间戳: {timestamp}")
    except Exception as e:
        print(f"[ERROR] 保存文件时出错: {e}")
        raise


if __name__ == "__main__":
    main()
