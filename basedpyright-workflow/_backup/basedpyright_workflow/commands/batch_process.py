"""批量处理命令模块

提供基于批量处理器的命令行接口，支持：
- 批量分析错误
- 生成分组报告
- 交互式修复操作
- 综合批量报告生成
"""

import sys
from datetime import datetime

from ..core.batch_processor import BatchErrorProcessor, ErrorCategory
from ..core.batch_reporter import BatchReportGenerator, BatchReportConfig
from ..utils.scanner import get_latest_file


def _print_header(message: str):
    """打印带边框的标题."""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80 + "\n")


def _print_section(title: str):
    """打印章节标题."""
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print(f"{'-' * 60}")


def cmd_batch_analyze(args) -> int:
    """批量分析命令：分析错误文件并生成详细报告

    Usage:
        basedpyright batch-analyze [--input ERRORS_FILE] [--output OUTPUT_DIR]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("Step 4: 批量分析错误数据")

    # 确定输入文件
    input_dir = args.input
    errors_file = args.errors_file

    if not errors_file:
        print(f"未指定错误文件，在 {input_dir} 中查找最新的错误文件...")
        errors_file = get_latest_file(input_dir, "basedpyright_errors_only_*.json")
        if errors_file:
            print(f"  找到: {errors_file.name}")
        else:
            print("  错误: 未找到错误文件")
            return 1
    else:
        print(f"使用错误文件: {errors_file}")

    if not errors_file.exists():
        print(f"错误: 文件不存在 {errors_file}")
        return 1

    print()

    try:
        # 创建批量处理器
        processor = BatchErrorProcessor(errors_file)

        # 加载错误数据
        if not processor.load_errors():
            print("错误: 无法加载错误文件")
            return 1

        print(f"已加载 {len(processor.raw_errors)} 个原始错误")

        # 执行分析
        stats = processor.analyze()

        # 显示统计信息
        _print_section("分析统计")
        print(f"原始错误数量: {stats.total_errors}")
        print(f"去重后错误数量: {stats.unique_errors}")
        print(f"处理耗时: {stats.processing_time:.2f}秒")
        print(f"错误分组数量: {stats.groups_count}")
        print(f"可自动修复错误: {stats.auto_fixable_count}")

        _print_section("错误分类统计")
        for category, count in stats.by_category.items():
            percentage = (count / stats.unique_errors * 100) if stats.unique_errors > 0 else 0
            print(f"  {category}: {count} ({percentage:.1f}%)")

        _print_section("严重程度统计")
        for severity, count in stats.by_severity.items():
            percentage = (count / stats.unique_errors * 100) if stats.unique_errors > 0 else 0
            print(f"  {severity}: {count} ({percentage:.1f}%)")

        _print_section("Top 10 错误文件")
        for file_path, count in list(stats.by_file.items())[:10]:
            print(f"  {file_path}: {count} 个错误")

        # 显示错误分组
        if processor.error_groups:
            _print_section("错误分组")
            for i, group in enumerate(processor.error_groups[:5], 1):
                print(f"\n  分组 {i}: {group.pattern}")
                print(f"    错误数量: {len(group.errors)}")
                print(f"    可自动修复: {'是' if group.auto_fixable else '否'}")
                if group.common_fix:
                    print(f"    通用建议: {group.common_fix}")

                # 显示前几个错误示例
                for j, error in enumerate(group.errors[:3], 1):
                    print(f"      {j}. {error.file}:{error.line} - {error.message[:80]}...")
                if len(group.errors) > 3:
                    print(f"      ... 还有 {len(group.errors) - 3} 个类似错误")

        # 导出详细报告
        output_dir = args.output
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"batch_analysis_report_{timestamp}.json"

        if processor.export_analysis_report(report_file):
            print("\n[OK] 分析完成！")
            print(f"  详细报告: {report_file}")
        else:
            print("\n警告: 详细报告导出失败")
            return 1

        # 显示可自动修复的错误数量
        auto_fixable = processor.get_auto_fixable_errors()
        if auto_fixable:
            print(f"\n可立即自动修复的错误: {len(auto_fixable)} 个")
            print("运行 'basedpyright batch-fix' 开始自动修复")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_batch_fix(args) -> int:
    """批量修复命令：交互式修复简单错误

    Usage:
        basedpyright batch-fix [--input ERRORS_FILE] [--auto] [--dry-run]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("Step 5: 批量修复错误")

    # 确定输入文件
    input_dir = args.input
    errors_file = args.errors_file

    if not errors_file:
        print(f"未指定错误文件，在 {input_dir} 中查找最新的错误文件...")
        errors_file = get_latest_file(input_dir, "basedpyright_errors_only_*.json")
        if errors_file:
            print(f"  找到: {errors_file.name}")
        else:
            print("  错误: 未找到错误文件")
            return 1

    print(f"使用错误文件: {errors_file}")

    try:
        # 创建批量处理器并分析
        processor = BatchErrorProcessor(errors_file)
        if not processor.load_errors():
            print("错误: 无法加载错误文件")
            return 1

        stats = processor.analyze()
        auto_fixable = processor.get_auto_fixable_errors()

        if not auto_fixable:
            print("\n没有找到可自动修复的错误")
            return 0

        print(f"\n找到 {len(auto_fixable)} 个可自动修复的错误")

        if not args.auto:
            # 交互式确认
            print("\n将要修复以下错误类型:")
            for category in ErrorCategory:
                errors = processor.get_errors_by_category(category)
                if errors and category == ErrorCategory.SIMPLE:
                    print(f"  {category.value}: {len(errors)} 个错误")

            try:
                response = input("\n是否继续修复? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("修复已取消")
                    return 0
            except (EOFError, KeyboardInterrupt):
                print("\n修复已取消（无交互环境或用户中断）")
                return 0

        if args.dry_run:
            print("\n[DRY RUN] 将要修复的错误:")
            for i, error in enumerate(auto_fixable[:10], 1):
                print(f"  {i}. {error.file}:{error.line}")
                print(f"     错误: {error.message}")
                print(f"     建议: {error.fix_suggestion}")
                print(f"     置信度: {error.confidence:.1%}")
                print()

            if len(auto_fixable) > 10:
                print(f"  ... 还有 {len(auto_fixable) - 10} 个错误")
        else:
            # 这里应该集成实际的修复逻辑
            # 目前只是演示，实际的修复需要结合具体的代码修改
            print("\n[注意] 自动修复功能需要进一步实现")
            print("当前仅支持错误分析和建议生成")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_batch_report(args) -> int:
    """批量报告命令：生成Markdown格式的批量处理报告

    Usage:
        basedpyright batch-report [--input ERRORS_FILE] [--output OUTPUT_DIR]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("Step 6: 生成批量处理报告")

    # 确定输入文件
    input_dir = args.input
    errors_file = args.errors_file

    if not errors_file:
        errors_file = get_latest_file(input_dir, "basedpyright_errors_only_*.json")
        if errors_file:
            print(f"使用错误文件: {errors_file.name}")
        else:
            print("错误: 未找到错误文件")
            return 1

    try:
        # 创建批量处理器并分析
        processor = BatchErrorProcessor(errors_file)
        if not processor.load_errors():
            print("错误: 无法加载错误文件")
            return 1

        stats = processor.analyze()

        # 生成Markdown报告
        output_dir = args.output
        output_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"batch_processing_report_{timestamp}.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            # 报告头部
            f.write("# BasedPyright 批量处理报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**源文件**: `{errors_file.name}`\n\n")

            # 执行摘要
            f.write("## 执行摘要\n\n")
            f.write(f"- **原始错误数量**: {stats.total_errors}\n")
            f.write(f"- **去重后错误数量**: {stats.unique_errors}\n")
            f.write(f"- **处理耗时**: {stats.processing_time:.2f}秒\n")
            f.write(f"- **错误分组数量**: {stats.groups_count}\n")
            f.write(f"- **可自动修复错误**: {stats.auto_fixable_count}\n\n")

            # 错误分类统计
            f.write("## 错误分类统计\n\n")
            f.write("| 分类 | 数量 | 占比 |\n")
            f.write("|------|------|------|\n")
            for category, count in stats.by_category.items():
                percentage = (count / stats.unique_errors * 100) if stats.unique_errors > 0 else 0
                f.write(f"| {category} | {count} | {percentage:.1f}% |\n")
            f.write("\n")

            # 严重程度统计
            f.write("## 严重程度统计\n\n")
            f.write("| 严重程度 | 数量 | 占比 |\n")
            f.write("|----------|------|------|\n")
            for severity, count in stats.by_severity.items():
                percentage = (count / stats.unique_errors * 100) if stats.unique_errors > 0 else 0
                f.write(f"| {severity} | {count} | {percentage:.1f}% |\n")
            f.write("\n")

            # Top错误文件
            f.write("## Top 10 错误文件\n\n")
            f.write("| 文件路径 | 错误数量 |\n")
            f.write("|----------|----------|\n")
            for file_path, count in list(stats.by_file.items())[:10]:
                f.write(f"| `{file_path}` | {count} |\n")
            f.write("\n")

            # 错误分组详情
            if processor.error_groups:
                f.write("## 错误分组分析\n\n")
                for i, group in enumerate(processor.error_groups, 1):
                    f.write(f"### 分组 {i}: {group.pattern}\n\n")
                    f.write(f"- **错误数量**: {len(group.errors)}\n")
                    f.write(f"- **可自动修复**: {'是' if group.auto_fixable else '否'}\n")
                    if group.common_fix:
                        f.write(f"- **通用建议**: {group.common_fix}\n")
                    f.write("\n")

                    f.write("#### 错误详情\n\n")
                    for j, error in enumerate(group.errors, 1):
                        f.write(f"{j}. **{error.file}:{error.line}**\n")
                        f.write(f"   - **错误**: {error.message}\n")
                        f.write(f"   - **规则**: {error.rule}\n")
                        f.write(f"   - **严重程度**: {error.severity_level.value}\n")
                        if error.fix_suggestion:
                            f.write(f"   - **修复建议**: {error.fix_suggestion}\n")
                        f.write(f"   - **置信度**: {error.confidence:.1%}\n\n")
                    f.write("---\n\n")

            # 可自动修复的错误
            auto_fixable = processor.get_auto_fixable_errors()
            if auto_fixable:
                f.write("## 可自动修复的错误\n\n")
                f.write(f"共找到 {len(auto_fixable)} 个可自动修复的错误:\n\n")
                for i, error in enumerate(auto_fixable, 1):
                    f.write(f"{i}. **{error.file}:{error.line}**\n")
                    f.write(f"   - **错误**: {error.message}\n")
                    f.write(f"   - **修复建议**: {error.fix_suggestion}\n")
                    f.write(f"   - **置信度**: {error.confidence:.1%}\n\n")

            # 建议和后续步骤
            f.write("## 建议和后续步骤\n\n")
            if stats.auto_fixable_count > 0:
                f.write("1. **立即自动修复**: 运行 `basedpyright batch-fix` 修复简单错误\n")
            if stats.groups_count > 0:
                f.write("2. **批量处理**: 优先处理错误分组中的类似问题\n")
            if stats.by_severity.get('critical', 0) > 0 or stats.by_severity.get('high', 0) > 0:
                f.write("3. **优先处理**: 首先解决高严重程度和关键错误\n")
            f.write("4. **持续监控**: 定期运行检查以保持代码质量\n")

        print("\n[OK] 批量处理报告生成完成！")
        print(f"  报告文件: {report_file}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_batch_report_enhanced(args) -> int:
    """增强批量报告命令：使用新的批量报告生成器创建综合报告

    Usage:
        basedpyright batch-report-enhanced [--input ERRORS_FILE] [--output OUTPUT_DIR] [--config CONFIG]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("Step 6+: 生成增强批量处理报告")

    # 确定输入文件
    input_dir = args.input
    errors_file = args.errors_file

    # 配置批量报告生成器
    config = BatchReportConfig()
    if hasattr(args, 'include_trends') and not args.include_trends:
        config.include_trends = False
    if hasattr(args, 'include_file_comparison') and not args.include_file_comparison:
        config.include_file_comparison = False
    if hasattr(args, 'max_error_details'):
        config.max_error_details = args.max_error_details

    try:
        # 创建批量报告生成器
        report_generator = BatchReportGenerator(config)

        if errors_file:
            # 单文件模式
            print(f"使用错误文件: {errors_file}")
            if not errors_file.exists():
                print(f"错误: 文件不存在 {errors_file}")
                return 1

            processor = BatchErrorProcessor(errors_file)
            if processor.load_errors():
                processor.analyze()
                report_generator.add_processor(processor)
                print(f"已加载 {len(processor.processed_errors)} 个处理后的错误")
            else:
                print("错误: 无法加载错误文件")
                return 1
        else:
            # 多文件模式 - 自动发现并加载所有错误文件
            print(f"在 {input_dir} 中查找所有错误文件...")
            error_files = list(input_dir.glob("basedpyright_errors_only_*.json"))

            if not error_files:
                print("错误: 未找到任何错误文件")
                return 1

            print(f"找到 {len(error_files)} 个错误文件")
            if not report_generator.load_from_files(error_files):
                print("警告: 部分文件加载失败")

        # 加载历史数据用于趋势分析
        if config.include_trends:
            print("加载历史数据用于趋势分析...")
            report_generator.load_historical_data(input_dir, days=30)

        # 生成报告
        output_dir = args.output
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 生成综合报告
        comprehensive_report = output_dir / f"batch_comprehensive_report_{timestamp}.md"
        report_generator.generate_comprehensive_markdown(comprehensive_report)

        # 生成摘要报告
        summary_report = output_dir / f"batch_summary_report_{timestamp}.md"
        report_generator.generate_summary_report(summary_report)

        print("\n[OK] 增强批量报告生成完成！")
        print(f"  综合报告: {comprehensive_report}")
        print(f"  摘要报告: {summary_report}")

        # 显示统计信息
        if report_generator.processors:
            total_errors = sum(p.stats.total_errors for p in report_generator.processors if p.stats)
            total_unique = sum(p.stats.unique_errors for p in report_generator.processors if p.stats)
            total_auto_fixable = sum(p.stats.auto_fixable_count for p in report_generator.processors if p.stats)

            print("\n📊 处理统计:")
            print(f"  总错误数: {total_errors}")
            print(f"  去重错误: {total_unique}")
            print(f"  可自动修复: {total_auto_fixable} ({total_auto_fixable/total_unique*100:.1f}%)")

            if report_generator.trend_data:
                print(f"  趋势数据点: {len(report_generator.trend_data)}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1