#!/usr/bin/env python3
"""验证 Session 执行失败修复文档对齐情况

用法:
    python verify-documentation-alignment.py

检查项:
    1. ANTHROPIC_MODEL_NAME 是否已从环境变量文档中移除
    2. 是否正确引用了 session-execution-failure-solution.md
    3. 是否正确引用了测试驱动方案
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple


class CheckResult(NamedTuple):
    file: Path
    check: str
    passed: bool
    message: str


def check_file_contains(file_path: Path, pattern: str, should_exist: bool = True) -> CheckResult:
    """检查文件是否包含特定模式"""
    content = file_path.read_text(encoding="utf-8")
    exists = bool(re.search(pattern, content, re.IGNORECASE))
    
    if should_exist:
        passed = exists
        message = f"找到 '{pattern[:50]}...'" if exists else f"未找到 '{pattern[:50]}...'"
    else:
        passed = not exists
        message = f"未找到 '{pattern[:50]}...' (符合预期)" if not exists else f"找到 '{pattern[:50]}...' (应移除)"
    
    return CheckResult(file_path, f"包含检查: {pattern[:30]}", passed, message)


def check_documentation_alignment() -> list[CheckResult]:
    """执行所有文档对齐检查"""
    results = []
    docs_dir = Path(__file__).parent.parent
    
    # 1. 检查 PRD.md
    prd_file = docs_dir / "PRD.md"
    if prd_file.exists():
        results.append(check_file_contains(
            prd_file, 
            r"ANTHROPIC_MODEL_NAME.*已移除",
            should_exist=True
        ))
    
    # 2. 检查 LLM_INTEGRATION.md
    llm_integration = docs_dir / "architecture" / "05_LLM_INTEGRATION.md"
    if llm_integration.exists():
        results.append(check_file_contains(
            llm_integration,
            r"ANTHROPIC_MODEL_NAME.*已移除",
            should_exist=True
        ))
        results.append(check_file_contains(
            llm_integration,
            r"session-execution-failure-solution",
            should_exist=True
        ))
    
    # 3. 检查 tech-stack.md
    tech_stack = docs_dir / "architecture" / "tech-stack.md"
    if tech_stack.exists():
        results.append(check_file_contains(
            tech_stack,
            r"ANTHROPIC_MODEL_NAME.*已移除",
            should_exist=True
        ))
    
    # 4. 检查 02_AGENT_ARCHITECTURE.md
    agent_arch = docs_dir / "architecture" / "02_AGENT_ARCHITECTURE.md"
    if agent_arch.exists():
        results.append(check_file_contains(
            agent_arch,
            r"Session 执行失败修复",
            should_exist=True
        ))
        results.append(check_file_contains(
            agent_arch,
            r"query\(\) \+ receive_messages",
            should_exist=True
        ))
    
    # 5. 检查 design/README.md
    design_readme = docs_dir / "design" / "README.md"
    if design_readme.exists():
        results.append(check_file_contains(
            design_readme,
            r"Session 执行失败修复",
            should_exist=True
        ))
    
    # 6. 检查 EPIC-09
    epic09 = docs_dir / "epics" / "EPIC-09-SESSION-AND-CANCELLATION.md"
    if epic09.exists():
        results.append(check_file_contains(
            epic09,
            r"Session 执行失败修复",
            should_exist=True
        ))
    
    # 7. 检查测试文件是否存在
    test_suite_dir = docs_dir / "solution" / "test-suite"
    test_files = [
        "test_fix1_prompt_method.py",
        "test_fix2_await_removal.py",
        "test_fix3_model_removal.py",
    ]
    for test_file in test_files:
        test_path = test_suite_dir / test_file
        results.append(CheckResult(
            test_path,
            f"测试文件存在: {test_file}",
            test_path.exists(),
            "存在" if test_path.exists() else "不存在"
        ))
    
    return results


def print_results(results: list[CheckResult]) -> None:
    """打印检查结果"""
    print("=" * 70)
    print("Session 执行失败修复 - 文档对齐验证报告")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for result in results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"\n{status} | {result.check}")
        print(f"   文件: {result.file}")
        print(f"   详情: {result.message}")
        
        if result.passed:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("=" * 70)
    
    if failed > 0:
        print("\n⚠️  部分检查失败，请检查文档是否已正确更新")
        return 1
    else:
        print("\n✅ 所有检查通过！文档已与修复方案对齐")
        return 0


def main() -> int:
    """主函数"""
    try:
        results = check_documentation_alignment()
        return print_results(results)
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
