#\!/usr/bin/env python3
"""
验证 Epic Driver 取消机制重构实施的脚本
"""

import re
from pathlib import Path
from typing import List, Tuple


def verify_sdk_wrapper_modifications():
    results = []
    success = True
    sdk_wrapper_path = Path("autoBMAD/epic_automation/sdk_wrapper.py")
    
    if not sdk_wrapper_path.exists():
        return False, [f"文件不存在: {sdk_wrapper_path}"]
    
    content = sdk_wrapper_path.read_text(encoding="utf-8")
    
    # 检查 CancelledError 是否返回 False
    if 'except asyncio.CancelledError:' in content:
        # 检查 _execute_with_recovery
        pattern = r'async def _execute_with_recovery.*?(?=async def|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            method_content = match.group(0)
            if 'return False' in method_content:
                results.append("✓ _execute_with_recovery: CancelledError 改为返回 False")
            else:
                results.append("✗ _execute_with_recovery: 需要检查")
                success = False
    
    return success, results


def verify_epic_driver_modifications():
    results = []
    success = True
    epic_driver_path = Path("autoBMAD/epic_automation/epic_driver.py")
    
    if not epic_driver_path.exists():
        return False, [f"文件不存在: {epic_driver_path}"]
    
    content = epic_driver_path.read_text(encoding="utf-8")
    
    # 检查 process_story 是否移除了 CancelledError
    pattern = r'async def process_story.*?async def _process_story_impl'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        method_content = match.group(0)
        if 'except asyncio.CancelledError:' not in method_content:
            results.append("✓ process_story: 移除了 CancelledError 处理")
        else:
            results.append("✗ process_story: 仍捕获 CancelledError")
            success = False
    
    return success, results


def verify_story_parser_modifications():
    results = []
    success = True
    story_parser_path = Path("autoBMAD/epic_automation/story_parser.py")
    
    if not story_parser_path.exists():
        return False, [f"文件不存在: {story_parser_path}"]
    
    content = story_parser_path.read_text(encoding="utf-8")
    
    if 'PROCESSING_TO_CORE_MAPPING' in content:
        results.append("✓ 添加了 PROCESSING_TO_CORE_MAPPING")
    else:
        results.append("✗ 未添加 PROCESSING_TO_CORE_MAPPING")
        success = False
    
    if '"cancelled": CORE_STATUS_READY_FOR_DEVELOPMENT' in content:
        results.append("✓ cancelled 映射到 Ready for Development")
    else:
        results.append("✗ cancelled 未映射")
        success = False
    
    return success, results


print("=" * 80)
print("Epic Driver 取消机制重构实施验证")
print("=" * 80)
print()

all_success = True

print("1. 验证 SDK 层封装...")
print("-" * 80)
success, results = verify_sdk_wrapper_modifications()
for result in results:
    print(result)
print()
all_success = all_success and success

print("2. 验证 EpicDriver 信号处理...")
print("-" * 80)
success, results = verify_epic_driver_modifications()
for result in results:
    print(result)
print()
all_success = all_success and success

print("3. 验证状态驱动循环...")
print("-" * 80)
success, results = verify_story_parser_modifications()
for result in results:
    print(result)
print()

print("=" * 80)
if all_success:
    print("✅ 验证完成！")
else:
    print("⚠️  请检查部分修改")
print("=" * 80)
