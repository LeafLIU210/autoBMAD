"""命令行接口模块.

提供基于pyright风格的命令行工具，支持以下命令：
- check: 运行类型检查
- report: 生成Markdown报告
- fix: 提取错误用于修复
- workflow: 执行完整工作流
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .core.checker import TypeChecker
from .core.reporter import ReportGenerator
from .core.extractor import ErrorExtractor
from .core.ruff_integration import RuffIntegrator, ResultMerger, ConflictResolver
from .utils.scanner import get_latest_file
from .config.settings import get_config_manager, get_config


def _print_header(message: str):
    """打印带边框的标题."""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80 + "\n")


def cmd_check(args) -> int:
    """check命令：运行类型检查.

    Usage:
        basedpyright check [--path SRC] [--output RESULTS]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功无错误，1=有错误）
    """
    _print_header("Step 1: 运行 BasedPyright 类型检查")

    # 设置目录
    source_dir = args.path
    output_dir = args.output

    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print()

    try:
        # 运行检查
        checker = TypeChecker(source_dir, output_dir)
        result = checker.run_check()

        # 输出结果
        print(f"TXT结果: {result['txt_file']}")
        print(f"JSON结果: {result['json_file']}")
        print()

        # 返回退出码
        error_count = result.get("error_count", 0)
        if error_count > 0:
            print(f"发现 {error_count} 个错误")
            return 1
        else:
            print("[OK] 检查完成（无错误）")
            return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_report(args) -> int:
    """report命令：生成 Markdown 报告.

    Usage:
        basedpyright report [--input RESULTS] [--output REPORTS]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("Step 2: 生成分析报告")

    # 确定输入目录
    input_dir = args.input
    txt_file = args.txt_file
    json_file = args.json_file

    # 如果没有指定文件，自动查找最新的
    if not txt_file and not json_file:
        print(f"未指定输入文件，在 {input_dir} 中查找最新的结果...")

        # 查找最新的 TXT 文件
        txt_file = get_latest_file(input_dir, "basedpyright_check_result_*.txt")
        if txt_file:
            print(f"  找到 TXT: {txt_file.name}")
        else:
            print("  警告: 未找到 TXT 结果文件")

        # 查找最新的 JSON 文件
        json_file = get_latest_file(input_dir, "basedpyright_check_result_*.json")
        if json_file:
            print(f"  找到 JSON: {json_file.name}")
        else:
            print("  警告: 未找到 JSON 结果文件")

        if not txt_file and not json_file:
            print("错误: 未找到任何检查结果文件")
            return 1

    else:
        if txt_file:
            print(f"使用 TXT 文件: {txt_file}")
        if json_file:
            print(f"使用 JSON 文件: {json_file}")

    print()

    try:
        # 创建生成器并加载结果
        generator = ReportGenerator(txt_file, json_file)
        if not generator.load_results():
            print("错误: 无法加载任何结果文件")
            return 1

        # 生成报告
        output_dir = args.output
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_file = output_dir / f"basedpyright_report_{timestamp}.md"

        generator.generate_markdown(md_file)

        print("\n[OK] 报告生成完成")
        print(f"  报告文件: {md_file}")
        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_fix(args) -> int:
    """fix命令：提取错误.

    Usage:
        basedpyright fix [--input RESULTS] [--output RESULTS] [--include-ruff]

    从检查结果中提取 ERROR 级别错误，包括basedpyright和ruff的结果，
    生成 JSON 数据用于修复。

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    include_ruff = getattr(args, 'include_ruff', False)
    if include_ruff:
        _print_header("Step 3: 提取错误数据 (basedpyright + ruff)")
    else:
        _print_header("Step 3: 提取错误数据")

    # 确定输入文件
    input_dir = args.input
    txt_file = args.txt_file
    json_file = args.json_file

    # 如果没有指定文件，自动查找最新的 TXT
    if not txt_file and not json_file:
        print(f"未指定输入文件，在 {input_dir} 中查找最新的 TXT 结果...")

        txt_file = get_latest_file(input_dir, "basedpyright_check_result_*.txt")
        if txt_file:
            print(f"  找到: {txt_file.name}")
        else:
            print("  错误: 未找到检查结果文件")
            return 1
    else:
        if txt_file:
            print(f"使用 TXT 文件: {txt_file}")
        if json_file:
            print(f"使用 JSON 文件: {json_file}")

    if include_ruff:
        print(f"启用 ruff 错误提取，搜索目录: {input_dir}")

    print()

    try:
        # 提取错误
        extractor = ErrorExtractor(
            txt_file=txt_file,
            json_file=json_file,
            include_ruff=include_ruff,
            results_dir=input_dir
        )
        if not extractor.load_file():
            print("错误: 无法加载检查结果文件")
            return 1

        errors = extractor.extract_errors()

        # 保存到文件
        output_dir = args.output
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if include_ruff:
            errors_file = output_dir / f"unified_errors_only_{timestamp}.json"
        else:
            errors_file = output_dir / f"basedpyright_errors_only_{timestamp}.json"

        extractor.save_json(errors_file, errors)

        # 显示下一步提示
        print("\n" + "=" * 80)
        print("错误提取完成！下一步操作：")
        print("=" * 80)
        print()
        print("运行以下命令开始自动修复：")
        print()
        if include_ruff:
            print("    powershell .\\basedpyright-workflow\\fix_unified_errors_new.ps1 \\")
            print(f"        -ErrorsFile \"{errors_file}\" \\")
            print("        -IncludeRuff")
        else:
            print("    powershell .\\basedpyright-workflow\\fix_project_errors.ps1 \\")
            print(f"        -ErrorsFile \"{errors_file}\"")
        print()
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_workflow(args) -> int:
    """workflow命令：执行完整工作流.

    顺序执行以下步骤：
    1. 运行检查（basedpyright + ruff，如果启用）
    2. 生成报告（report）
    3. 提取错误（fix）

    即使检查中发现错误，也会继续执行后续步骤（便于生成报告和提取错误进行修复）。
    只有当发生真正的执行错误（如命令失败）时才会终止。

    Usage:
        basedpyright workflow [--path SRC] [--include-ruff] [--format-after-fix]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=全部成功，1=任一步骤失败）
    """
    # 加载配置
    try:
        config = get_config()
    except Exception:
        config = get_config_manager().get_config()

    # 确定是否包含ruff
    include_ruff = getattr(args, 'include_ruff', False)
    format_after_fix = getattr(args, 'format_after_fix', False)

    if include_ruff:
        _print_header("执行完整工作流：basedpyright + ruff → report → fix")
    else:
        _print_header("执行完整工作流：check → report → fix")

    # 步骤 1: 运行检查
    if include_ruff:
        print("\n[1/4] 运行检查 (basedpyright + ruff)...")
        result = _run_unified_check(args, config)
    else:
        print("\n[1/3] 运行类型检查...")
        result = cmd_check(args)

    if result > 1:  # 真正的执行错误（返回值 >1）
        print("\n错误：检查步骤执行失败")
        return result
    elif result == 1:
        print("\n检查完成，发现错误，继续执行后续步骤...")

    # 步骤 2: ruff自动修复（如果启用）
    if include_ruff and config.ruff.fix_enabled:
        print("\n[2/4] 应用ruff自动修复...")
        result = _apply_ruff_fixes(args, config)
        if result != 0:
            print("警告：ruff修复步骤出现问题，但继续执行后续步骤...")

    # 步骤 3: 格式化（如果启用且需要）
    if include_ruff and format_after_fix and config.ruff.format_enabled:
        step_num = "3/4"
    elif include_ruff:
        step_num = "3/4"
    else:
        step_num = "2/3"

    if include_ruff and format_after_fix and config.ruff.format_enabled:
        print(f"\n[{step_num}] 应用代码格式化...")
        result = _apply_ruff_formatting(args, config)
        if result != 0:
            print("警告：格式化步骤出现问题，但继续执行后续步骤...")

    # 步骤 4: 生成报告
    if include_ruff:
        if config.ruff.fix_enabled or format_after_fix:
            report_step = "4/4"
        else:
            report_step = "3/4"
        print(f"\n[{report_step}] 生成分析报告...")
    else:
        print("\n[2/3] 生成分析报告...")

    # 为 report 命令准备参数
    class ReportArgs:
        def __init__(self):
            self.input = args.output
            self.output = config.reports_directory
            self.txt_file = None
            self.json_file = None

    report_args = ReportArgs()
    result = cmd_report(report_args)
    if result != 0 and not args.ignore_errors:
        print("\n工作流终止：报告生成失败")
        return result

    # 步骤 5: 提取错误（仅在需要时）
    # 总是需要提取错误，因为用户可能希望手动修复ruff无法自动修复的问题
    if include_ruff:
        if config.ruff.fix_enabled or format_after_fix:
            extract_step = "5/5"
        else:
            extract_step = "4/4"
        print(f"\n[{extract_step}] 提取错误数据...")
    else:
        print("\n[3/3] 提取错误数据...")

    # 为 fix 命令准备参数
    class FixArgs:
        def __init__(self):
            self.input = args.output
            self.output = config.results_directory
            self.txt_file = None
            self.json_file = None
            self.include_ruff = include_ruff

    fix_args = FixArgs()
    result = cmd_fix(fix_args)
    if result != 0:
        print("\n工作流终止：错误提取失败")
        return result

    # 完成提示
    print("\n" + "=" * 80)
    print("[OK] 完整工作流完成！")
    print("-" * 80)

    if include_ruff:
        print("已完成 basedpyright + ruff 检查和报告生成")
        print("下一步：运行 PowerShell 脚本开始自动修复")
        print()
        if config.ruff.fix_enabled or config.ruff.format_enabled:
            print("    powershell .\\basedpyright-workflow\\fix_unified_errors_new.ps1 -IncludeRuff")
            if config.ruff.fix_enabled:
                print("    # 或包含ruff自动修复:")
                print("    powershell .\\basedpyright-workflow\\fix_unified_errors_new.ps1 -IncludeRuff -ApplyRuffFixes")
        else:
            print("    powershell .\\basedpyright-workflow\\fix_unified_errors_new.ps1 -IncludeRuff")
        print()
    else:
        print("下一步：运行 PowerShell 脚本开始自动修复")
        print()
        print("    powershell .\\basedpyright-workflow\\fix_project_errors.ps1")
        print()

    print("=" * 80)

    return 0


def _run_unified_check(args, config) -> int:
    """运行统一的检查（basedpyright + ruff）

    Args:
        args: 命令行参数
        config: 配置对象

    Returns:
        int: 退出码
    """
    source_dir = args.path
    output_dir = args.output

    try:
        # 运行 basedpyright 检查
        print("  运行 basedpyright 检查...")
        bp_checker = TypeChecker(source_dir, output_dir)
        bp_result = bp_checker.run_check()

        # 运行 ruff 检查
        ruff_errors = 0
        if config.ruff.enabled:
            print("  运行 ruff 检查...")
            ruff_integrator = RuffIntegrator(config.ruff, source_dir, output_dir)
            ruff_result = ruff_integrator.run_check()
            ruff_integrator.cleanup()

            if not ruff_result.get("execution_failed"):
                # 保存 ruff 结果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruff_integrator.save_results(ruff_result, timestamp)
                ruff_errors = ruff_result.get("errors", 0)
            else:
                print(f"    警告: ruff 检查失败 - {ruff_result.get('error', '未知错误')}")
        else:
            print("  ruff 检查已禁用")

        # 合并结果
        merger = ResultMerger()
        merged_result = merger.merge_results(bp_result, ruff_result if config.ruff.enabled else {})

        # 解决冲突
        resolver = ConflictResolver("basedpyright_priority")  # 基于用户要求
        resolved_result = resolver.resolve_conflicts(merged_result)

        # 输出统计
        total_errors = bp_result.get("error_count", 0) + ruff_errors
        print("\n  检查完成:")
        print(f"    basedpyright: {bp_result.get('error_count', 0)} 错误")
        if config.ruff.enabled:
            print(f"    ruff: {ruff_errors} 错误")
        print(f"    总计: {total_errors} 错误")

        # 返回是否有错误
        return 1 if total_errors > 0 else 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 2  # 返回 >1 表示执行错误


def _apply_ruff_fixes(args, config) -> int:
    """应用ruff自动修复

    Args:
        args: 命令行参数
        config: 配置对象

    Returns:
        int: 退出码
    """
    source_dir = args.path

    try:
        integrator = RuffIntegrator(config.ruff, source_dir, args.output)

        # 先预览可修复的问题
        print("  预览可修复的问题...")
        preview_result = integrator.preview_fixes()

        if preview_result.get("execution_failed"):
            print(f"  警告: ruff修复预览失败 - {preview_result.get('error', '未知错误')}")
            integrator.cleanup()
            return 1

        if not preview_result.get("enabled", False):
            print("  ruff修复功能已禁用")
            integrator.cleanup()
            return 0

        total_fixable = preview_result.get("total_fixable", 0)
        files_with_fixes = preview_result.get("files_with_fixes", 0)

        if total_fixable == 0:
            print("  没有可自动修复的问题")
            integrator.cleanup()
            return 0

        print(f"  发现 {total_fixable} 个可修复的问题，涉及 {files_with_fixes} 个文件")

        # 应用修复
        print("  应用自动修复...")
        fix_result = integrator.apply_fixes()
        integrator.cleanup()

        if fix_result.get("execution_failed"):
            print(f"  警告: ruff修复失败 - {fix_result.get('error', '未知错误')}")
            return 1

        if not fix_result.get("fixed", False):
            print(f"  {fix_result.get('message', '修复未执行')}")
            return 0

        # 显示修复结果
        fixed_count = fix_result.get("fixed_count", 0)
        before_count = fix_result.get("before_count", 0)
        after_count = fix_result.get("after_count", 0)
        rules_used = fix_result.get("rules_used", [])
        unsafe_used = fix_result.get("unsafe_used", False)

        print("  修复完成:")
        print(f"    修复前: {before_count} 个问题")
        print(f"    修复后: {after_count} 个问题")
        print(f"    已修复: {fixed_count} 个问题")

        if unsafe_used:
            print("    ⚠ 使用了unsafe修复")

        if rules_used and rules_used != ["all"]:
            print(f"    使用的规则: {', '.join(rules_used)}")
        elif rules_used == ["all"]:
            print("    修复所有可修复的问题")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 2


def _apply_ruff_formatting(args, config) -> int:
    """应用ruff格式化

    Args:
        args: 命令行参数
        config: 配置对象

    Returns:
        int: 退出码
    """
    source_dir = args.path

    try:
        integrator = RuffIntegrator(config.ruff, source_dir, args.output)
        result = integrator.format_and_check()
        integrator.cleanup()

        if result.get("execution_failed"):
            print(f"  警告: ruff 格式化失败 - {result.get('error', '未知错误')}")
            return 1

        if not result.get("enabled", False):
            print("  ruff 格式化已禁用")
            return 0

        if result.get("formatted", False):
            files_count = result.get("files_count", 0)
            files = result.get("files", [])
            verification = result.get("verification", "unknown")

            print(f"  已格式化 {files_count} 个文件")

            if verification == "passed":
                print("  ✓ 格式化验证通过")
            else:
                print("  ⚠ 格式化验证失败")

            # 显示文件列表（如果有的话）
            if files:
                print("  格式化的文件:")
                for file in files[:5]:  # 显示前5个文件
                    print(f"    - {file}")
                if len(files) > 5:
                    print(f"    ... 还有 {len(files) - 5} 个文件")
        else:
            message = result.get("message", "代码格式良好，无需格式化")
            print(f"  {message}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 2


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器."""
    # 加载配置（从 .bpr.json 读取）
    try:
        config = get_config()
    except Exception:
        # 如果加载失败，使用默认配置
        config = get_config_manager().get_config()

    parser = argparse.ArgumentParser(
        prog="basedpyright-workflow",
        description="Python 代码质量检查、报告和修复工作流工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行类型检查
  basedpyright-workflow check

  # 指定源目录和输出目录
  basedpyright-workflow check --path ./lib --output ./check_results

  # 生成报告
  basedpyright-workflow report

  # 提取错误用于修复
  basedpyright-workflow fix

  # 执行完整工作流（仅basedpyright）
  basedpyright-workflow workflow

  # 执行完整工作流（包含ruff检查）
  basedpyright-workflow workflow --include-ruff

  # 执行完整工作流（包含ruff检查和格式化）
  basedpyright-workflow workflow --include-ruff --format-after-fix

  # 执行完整工作流（包含ruff检查、自动修复和格式化）
  basedpyright-workflow workflow --include-ruff --format-after-fix

  # 查看帮助
  basedpyright-workflow --help
  basedpyright-workflow check --help
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # check 命令
    check_parser = subparsers.add_parser(
        "check", help="运行基于 basedpyright 的类型检查"
    )
    check_parser.add_argument(
        "--path",
        type=Path,
        default=config.source_directory,
        help=f"源代码目录 (默认: {config.source_directory})",
    )
    check_parser.add_argument(
        "--output",
        type=Path,
        default=config.results_directory,
        help=f"结果输出目录 (默认: {config.results_directory})",
    )

    # report 命令
    report_parser = subparsers.add_parser(
        "report", help="生成 Markdown 分析报告"
    )
    report_parser.add_argument(
        "--input",
        type=Path,
        default=config.results_directory,
        help=f"检查结果目录 (默认: {config.results_directory})",
    )
    report_parser.add_argument(
        "--output",
        type=Path,
        default=config.reports_directory,
        help=f"报告输出目录 (默认: {config.reports_directory})",
    )
    report_parser.add_argument(
        "--txt-file",
        type=Path,
        help="指定 TXT 结果文件（可选）",
    )
    report_parser.add_argument(
        "--json-file",
        type=Path,
        help="指定 JSON 结果文件（可选）",
    )

    # fix 命令
    fix_parser = subparsers.add_parser(
        "fix", help="提取 ERROR 级别错误用于修复"
    )
    fix_parser.add_argument(
        "--input",
        type=Path,
        default=config.results_directory,
        help=f"检查结果目录 (默认: {config.results_directory})",
    )
    fix_parser.add_argument(
        "--output",
        type=Path,
        default=config.results_directory,
        help=f"错误数据输出目录 (默认: {config.results_directory})",
    )
    fix_parser.add_argument(
        "--txt-file",
        type=Path,
        help="指定 TXT 结果文件（可选）",
    )
    fix_parser.add_argument(
        "--json-file",
        type=Path,
        help="指定 JSON 结果文件（可选）",
    )

    # workflow 命令
    workflow_parser = subparsers.add_parser(
        "workflow", help="执行完整工作流 (check → report → fix)"
    )
    workflow_parser.add_argument(
        "--path",
        type=Path,
        default=config.source_directory,
        help=f"源代码目录 (默认: {config.source_directory})",
    )
    workflow_parser.add_argument(
        "--output",
        type=Path,
        default=config.results_directory,
        help=f"结果输出目录 (默认: {config.results_directory})",
    )
    workflow_parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="忽略检查错误，继续执行后续步骤",
    )
    workflow_parser.add_argument(
        "--include-ruff",
        action="store_true",
        help="在检查中包含ruff代码检查",
    )
    workflow_parser.add_argument(
        "--format-after-fix",
        action="store_true",
        help="在修复后应用ruff代码格式化",
    )

    return parser


def main() -> int:
    """主函数：解析命令行参数并执行对应命令."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "check":
            return cmd_check(args)
        elif args.command == "report":
            return cmd_report(args)
        elif args.command == "fix":
            return cmd_fix(args)
        elif args.command == "workflow":
            return cmd_workflow(args)
        else:
            print(f"未知命令: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
