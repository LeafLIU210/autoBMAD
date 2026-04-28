#!/usr/bin/env python3
"""Session 执行失败修复测试的快速运行脚本"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """运行所有修复测试"""
    test_dir = Path(__file__).parent
    
    test_files = [
        "test_fix3_model_removal.py",
        "test_fix1_prompt_method.py", 
        "test_fix2_await_removal.py",
    ]
    
    all_passed = True
    
    print("=" * 60)
    print("Session 执行失败修复 - 测试套件")
    print("=" * 60)
    
    for test_file in test_files:
        test_path = test_dir / test_file
        if not test_path.exists():
            print(f"\n⚠️  跳过 {test_file} (文件不存在)")
            continue
        
        print(f"\n📝 运行 {test_file}...")
        print("-" * 40)
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
            cwd=test_dir.parent.parent.parent,  # 项目根目录
            capture_output=False
        )
        
        if result.returncode != 0:
            all_passed = False
            print(f"❌ {test_file} 失败")
        else:
            print(f"✅ {test_file} 通过")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_tests())
