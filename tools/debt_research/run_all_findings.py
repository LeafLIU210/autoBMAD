#!/usr/bin/env python3
"""
综合调试工具运行器
运行所有 Finding 的调试工具并生成汇总报告
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def run_finding_1():
    """运行 Finding 1 调试."""
    print("\n" + "=" * 80)
    print("运行 Finding 1: Session Manager 初始化问题")
    print("=" * 80)
    result = subprocess.run(
        [sys.executable, "tools/debt_research/finding_1_session_manager_debug.py"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return {"finding": 1, "stdout": result.stdout, "stderr": result.stderr}


async def run_finding_2():
    """运行 Finding 2 调试."""
    print("\n" + "=" * 80)
    print("运行 Finding 2: Pipeline ID 功能损坏")
    print("=" * 80)
    result = subprocess.run(
        [sys.executable, "tools/debt_research/finding_2_pipeline_id_debug.py"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return {"finding": 2, "stdout": result.stdout, "stderr": result.stderr}


async def run_finding_3():
    """运行 Finding 3 调试."""
    print("\n" + "=" * 80)
    print("运行 Finding 3: 双轨节点执行器")
    print("=" * 80)
    result = subprocess.run(
        [sys.executable, "tools/debt_research/finding_3_dual_executor_debug.py"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return {"finding": 3, "stdout": result.stdout, "stderr": result.stderr}


async def run_finding_4():
    """运行 Finding 4 调试."""
    print("\n" + "=" * 80)
    print("运行 Finding 4: 状态双轨模型")
    print("=" * 80)
    result = subprocess.run(
        [sys.executable, "tools/debt_research/finding_4_state_model_debug.py"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return {"finding": 4, "stdout": result.stdout, "stderr": result.stderr}


async def run_finding_5():
    """运行 Finding 5 调试."""
    print("\n" + "=" * 80)
    print("运行 Finding 5: 依赖、命名与文档漂移")
    print("=" * 80)
    result = subprocess.run(
        [sys.executable, "tools/debt_research/finding_5_dependency_drift_debug.py"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return {"finding": 5, "stdout": result.stdout, "stderr": result.stderr}


async def run_all_findings():
    """并行运行所有调试工具."""
    tasks = [
        run_finding_1(),
        run_finding_2(),
        run_finding_3(),
        run_finding_4(),
        run_finding_5(),
    ]
    results = await asyncio.gather(*tasks)
    return results


if __name__ == "__main__":
    print("=" * 80)
    print("DocuSwarm 技术债深度研究工具")
    print(f"运行时间: {datetime.now().isoformat()}")
    print("=" * 80)

    results = asyncio.run(run_all_findings())

    # 保存原始结果
    output_dir = project_root / "tools" / "debt_research" / "output"
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "findings_raw_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"所有调试结果已保存到: {output_dir / 'findings_raw_output.json'}")
    print("=" * 80)
