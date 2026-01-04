#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本4：生成Claude提示词并调用修复
根据汇总JSON生成结构化提示词，调用claude --dangerously-skip-permissions
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


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


def generate_fix_prompt(summary_data, output_file):
    """
    生成修复提示词

    Args:
        summary_data: 汇总数据
        output_file: 输出文件路径

    Returns:
        str: 生成的提示词
    """
    prompt_parts = []
    prompt_parts.append("# 测试修复任务")
    prompt_parts.append("")
    prompt_parts.append(f"**扫描时间**: {summary_data.get('scan_timestamp', 'N/A')}")
    prompt_parts.append(f"**测试时间**: {summary_data.get('test_start_time', 'N/A')}")
    prompt_parts.append(f"**总文件数**: {summary_data.get('total_files', 0)}")

    summary = summary_data.get('summary', {})
    prompt_parts.append("")
    prompt_parts.append("## 测试汇总")
    prompt_parts.append(f"- 通过: {summary.get('passed', 0)} 个")
    prompt_parts.append(f"- 失败: {summary.get('failed', 0)} 个")
    prompt_parts.append(f"- 错误: {summary.get('errors', 0)} 个")
    prompt_parts.append(f"- 超时: {summary.get('timeouts', 0)} 个")

    error_files = summary_data.get("files_with_errors", [])
    prompt_parts.append("")
    prompt_parts.append(f"## 需要修复的文件 ({len(error_files)} 个)")
    prompt_parts.append("")

    for i, file_info in enumerate(error_files, 1):
        rel_path = file_info["relative_path"]
        result = file_info.get("result", "unknown")
        execution_time = file_info.get("execution_time", 0)

        prompt_parts.append(f"### 文件 {i}: {rel_path}")
        prompt_parts.append("")
        prompt_parts.append(f"**状态**: {result}")
        prompt_parts.append(f"**执行时间**: {execution_time:.2f}s")
        prompt_parts.append("")

        # 添加错误信息
        if file_info.get("errors"):
            prompt_parts.append("**错误信息**:")
            for error in file_info["errors"]:
                prompt_parts.append(f"- 类型: {error.get('type', 'N/A')}")
                prompt_parts.append(f"  消息: {error.get('message', 'N/A')}")
                if error.get("details"):
                    for detail in error["details"]:
                        prompt_parts.append(f"  - {detail}")
            prompt_parts.append("")

        # 添加失败信息
        if file_info.get("failures"):
            prompt_parts.append("**失败信息**:")
            for failure in file_info["failures"]:
                prompt_parts.append(f"- 测试: {failure.get('test_name', 'N/A')}")
                prompt_parts.append(f"  消息: {failure.get('message', 'N/A')}")
                if failure.get("details"):
                    for detail in failure["details"]:
                        prompt_parts.append(f"  - {detail}")
            prompt_parts.append("")

        # 如果有调试信息，添加到提示词
        if file_info.get("debug_info"):
            debug = file_info["debug_info"]
            prompt_parts.append("**调试信息**:")
            prompt_parts.append(f"- 调试会话ID: {debug.get('debug_session_id', 'N/A')}")
            prompt_parts.append(f"- 调试端口: {debug.get('debug_port', 'N/A')}")

            debug_log = debug.get('debug_log', '')
            if debug_log:
                # 只显示前500个字符避免过长
                if len(debug_log) > 500:
                    prompt_parts.append(f"- 调试日志（前500字符）:\n```\n{debug_log[:500]}...\n```")
                else:
                    prompt_parts.append(f"- 调试日志:\n```\n{debug_log}\n```")

            prompt_parts.append("")

        prompt_parts.append("---")
        prompt_parts.append("")

    # 添加修复指导
    prompt_parts.append("## 修复指导")
    prompt_parts.append("")
    prompt_parts.append("请对每个失败的文件执行以下步骤：")
    prompt_parts.append("")
    prompt_parts.append("1. **分析错误原因**: 仔细阅读ERROR和FAIL的具体信息")
    prompt_parts.append("2. **查看调试信息**: 如果有debug_info字段，请仔细分析调试日志")
    prompt_parts.append("3. **修复代码**: 根据错误信息修复对应的代码")
    prompt_parts.append("4. **验证修复**: 运行pytest验证修复结果")
    prompt_parts.append("5. **循环验证**: 如果仍有ERROR或FAIL，继续修复直到测试完全通过")
    prompt_parts.append("")
    prompt_parts.append("**重要要求**:")
    prompt_parts.append("- 必须修复所有ERROR和FAIL")
    prompt_parts.append("- 每轮修复后必须立即执行测试验证")
    prompt_parts.append("- 重复验证直到测试完全通过")
    prompt_parts.append("- 显示最终的测试结果（应该显示PASSED且没有任何ERROR或FAIL）")

    prompt = "\n".join(prompt_parts)

    # 保存提示词到文件
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prompt)

    return prompt


def call_claude(prompt_file):
    """
    调用claude --dangerously-skip-permissions，显示窗口

    Args:
        prompt_file: 提示词文件路径

    Returns:
        bool: 是否成功
    """
    try:
        print("\n" + "=" * 60)
        print("正在调用 Claude 进行修复...")
        print("=" * 60 + "\n")

        # 构建claude命令，读取提示词文件
        # 使用 @prompt_file 语法将提示词注入claude
        cmd = f'claude --dangerously-skip-permissions @"{prompt_file}"'

        print(f"执行命令: {cmd}")
        print("\n" + "=" * 60)
        print("Claude 窗口应该已经打开...")
        print("=" * 60 + "\n")

        # 使用subprocess.run执行命令
        # 这样会等待命令完成
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,  # 不捕获输出，让claude显示窗口
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("Claude 调用完成")
            print("=" * 60 + "\n")
            return True
        else:
            print("\n" + "=" * 60)
            print(f"Claude 调用退出，代码: {result.returncode}")
            print("=" * 60 + "\n")
            return False

    except Exception as e:
        error_msg = f"调用Claude失败: {str(e)}"
        print(f"\n[ERROR] {error_msg}\n")
        return False


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    summaries_dir = script_dir / "summaries"
    prompts_dir = script_dir / "prompts"

    try:
        # 查找最新汇总JSON
        latest_summary = find_latest_summary_json(summaries_dir)
        print(f"\n=== 生成Claude修复提示词 ===\n")

        # 加载数据
        summary_data = load_summary_json(latest_summary)

        # 检查是否有错误文件
        error_files = summary_data.get("files_with_errors", [])
        if not error_files:
            print("[OK] 所有测试都已通过，没有需要修复的文件！")
            return

        print(f"发现 {len(error_files)} 个失败文件需要修复\n")

        # 生成提示词
        timestamp = get_timestamp()
        prompt_file = prompts_dir / f"fix_prompt_{timestamp}.md"
        print(f"生成提示词文件: {prompt_file}")

        prompt = generate_fix_prompt(summary_data, prompt_file)
        print(f"提示词长度: {len(prompt)} 字符")
        print(f"提示词已保存到: {prompt_file}\n")

        # 更新汇总JSON标记已生成提示词
        summary_data["prompt_generated"] = True
        summary_data["prompt_file"] = str(prompt_file)
        summary_data["prompt_timestamp"] = datetime.now().isoformat()

        output_path = summaries_dir / f"test_results_summary_prompt_{timestamp}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        print(f"已更新汇总JSON: {output_path}\n")

        # 调用Claude
        success = call_claude(prompt_file)

        if success:
            print("\n[SUCCESS] Claude修复调用成功完成！")
            print(f"提示词文件: {prompt_file}")
            print(f"更新后的汇总JSON: {output_path}")
        else:
            print("\n[WARNING] Claude调用可能有问题，请检查输出")
            print(f"提示词文件: {prompt_file}")

    except Exception as e:
        print(f"\n[ERROR] 生成提示词或调用Claude时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
