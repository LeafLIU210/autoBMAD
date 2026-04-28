#!/usr/bin/env python3
"""测试运行脚本

用法:
    python run_tests.py           # 运行所有测试
    python run_tests.py unit      # 只运行单元测试
    python run_tests.py integration  # 只运行集成测试
    python run_tests.py e2e       # 只运行端到端测试
"""
import sys
import subprocess
from pathlib import Path

TEST_DIR = Path(__file__).parent / "test-suite"

TEST_FILES = {
    "unit": [
        "test_file_tools_migration.py",
        "test_search_tools_migration.py",
    ],
    "integration": [
        "test_session_manager_integration.py",
    ],
    "e2e": [
        "test_end_to_end_pipeline.py",
    ],
}


def run_tests(test_type: str | None = None):
    """运行测试"""
    if test_type is None or test_type == "all":
        files = []
        for f_list in TEST_FILES.values():
            files.extend(f_list)
    elif test_type in TEST_FILES:
        files = TEST_FILES[test_type]
    else:
        print(f"Unknown test type: {test_type}")
        print(f"Available: all, {', '.join(TEST_FILES.keys())}")
        sys.exit(1)
    
    cmd = ["pytest", "-v", "--tb=short"]
    for f in files:
        cmd.append(str(TEST_DIR / f))
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_tests(test_type)
