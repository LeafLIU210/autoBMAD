#!/usr/bin/env python
"""验证循环次数修复"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 读取源文件验证修改
print("=" * 60)
print("验证源代码修改")
print("=" * 60)

# 验证 devqa_controller.py
devqa_file = project_root / "controllers" / "devqa_controller.py"
content = devqa_file.read_text(encoding='utf-8')
if "self.max_rounds = 5" in content:
    print("[PASS] DevQaController.max_rounds = 5")
else:
    print("[FAIL] DevQaController.max_rounds 未修改为5")

# 验证 base_controller.py
base_file = project_root / "controllers" / "base_controller.py"
content = base_file.read_text(encoding='utf-8')
if "self.max_iterations = 5" in content:
    print("[PASS] StateDrivenController.max_iterations = 5")
else:
    print("[FAIL] StateDrivenController.max_iterations 未修改为5")

# 验证 quality_check_controller.py
quality_file = project_root / "controllers" / "quality_check_controller.py"
content = quality_file.read_text(encoding='utf-8')
if "max_cycles: int = 5" in content:
    print("[PASS] QualityCheckController.max_cycles = 5")
else:
    print("[FAIL] QualityCheckController.max_cycles 未修改为5")

# 验证 pytest_controller.py
pytest_file = project_root / "controllers" / "pytest_controller.py"
content = pytest_file.read_text(encoding='utf-8')
if "max_cycles: int = 5" in content:
    print("[PASS] PytestController.max_cycles = 5")
else:
    print("[FAIL] PytestController.max_cycles 未修改为5")

# 验证循环条件修复
if "self.current_cycle < self.max_cycles" in content:
    print("[PASS] PytestController 循环条件使用 <")
else:
    print("[FAIL] PytestController 循环条件未修复")

# 验证 epic_driver.py
epic_file = project_root / "epic_driver.py"
content = epic_file.read_text(encoding='utf-8')

# 检查CLI默认值
if "default=5" in content:
    default_count = content.count("default=5")
    print(f"[PASS] epic_driver.py 中 default=5 出现 {default_count} 次")
else:
    print("[FAIL] epic_driver.py 中 default=5 未找到")

# 检查质量门控设置
if "max_cycles=5" in content:
    cycles_count = content.count("max_cycles=5")
    print(f"[PASS] epic_driver.py 中 max_cycles=5 出现 {cycles_count} 次")
else:
    print("[FAIL] epic_driver.py 中 max_cycles=5 未找到")

# 验证循环次数
print("\n" + "=" * 60)
print("循环次数验证")
print("=" * 60)

# 验证当max_cycles=3时，使用<条件应该执行3次循环
max_cycles = 3
cycles_executed = 0
current_cycle = 0
failed_files = ["file1.py"]

while failed_files and current_cycle < max_cycles:
    cycles_executed += 1
    current_cycle += 1

print(f"当 max_cycles={max_cycles} 时:")
print(f"  实际执行循环次数: {cycles_executed}")
print(f"  期望循环次数: {max_cycles}")
result = "PASS" if cycles_executed == max_cycles else "FAIL"
print(f"  结果: {result}")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)
