"""配置管理命令模块

提供配置文件的创建、查看、验证和管理功能。
"""

import sys
from pathlib import Path

from ..config import ConfigManager, BMADWorkflowConfig


def _print_header(message: str):
    """打印带边框的标题."""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80 + "\n")


def cmd_config_init(args) -> int:
    """初始化配置文件命令

    Usage:
        basedpyright config init [--path CONFIG_FILE] [--template TEMPLATE]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("初始化BMAD工作流配置")

    # 确定配置文件路径
    if args.path:
        config_file = Path(args.path)
    else:
        config_file = Path.cwd() / ".bmadrc.json"

    if config_file.exists():
        if not args.force:
            response = input(f"配置文件 {config_file} 已存在，是否覆盖? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("操作已取消")
                return 0

    try:
        # 创建配置管理器
        config_manager = ConfigManager()

        if args.template:
            # 使用指定的模板
            if args.template == "minimal":
                config = BMADWorkflowConfig()
                config.reporter.include_trends = False
                config.reporter.include_file_comparison = False
                config.notifications.enabled = False
            elif args.template == "comprehensive":
                config = BMADWorkflowConfig()
                config.reporter.include_trends = True
                config.reporter.include_file_comparison = True
                config.notifications.enabled = True
                config.batch.parallel_processing = True
            else:
                config = BMADWorkflowConfig()
        else:
            config = config_manager.get_config()

        # 保存配置
        config_manager.config = config
        config_manager.save_config(config_file)

        print("\n[OK] 配置文件初始化完成！")
        print(f"  配置文件: {config_file}")
        print("\n下一步操作:")
        print("  1. 编辑配置文件以自定义设置")
        print("  2. 运行 'basedpyright config show' 查看当前配置")
        print("  3. 运行 'basedpyright config validate' 验证配置")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_config_show(args) -> int:
    """显示当前配置命令

    Usage:
        basedpyright config show [--section SECTION]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("当前BMAD工作流配置")

    try:
        config_manager = ConfigManager(args.config)
        config = config_manager.get_config()

        if args.section:
            # 显示特定配置节
            if hasattr(config, args.section):
                section = getattr(config, args.section)
                print(f"## {args.section.upper()} 配置\n")
                if hasattr(section, '__dataclass_fields__'):
                    from dataclasses import fields
                    for field_info in fields(section):
                        value = getattr(section, field_info.name)
                        print(f"  {field_info.name}: {value}")
                else:
                    print(f"  {args.section}: {section}")
                print()
            else:
                print(f"错误: 未知的配置节 '{args.section}'")
                return 1
        else:
            # 显示完整配置
            print("### 基础配置")
            print(f"  项目名称: {config.project_name}")
            print(f"  源目录: {config.source_directory}")
            print(f"  输出目录: {config.output_directory}")
            print(f"  自动修复: {'启用' if config.auto_fix_enabled else '禁用'}")
            print(f"  备份模式: {'启用' if config.backup_before_fix else '禁用'}")
            print(f"  Git集成: {'启用' if config.git_integration else '禁用'}")

            print("\n### 检查器配置")
            print(f"  Python版本: {config.checker.python_version}")
            print(f"  严格模式: {'启用' if config.checker.strict_mode else '禁用'}")
            print(f"  超时时间: {config.checker.timeout_seconds}秒")
            print(f"  包含文件: {', '.join(config.checker.include_files[:3])}{'...' if len(config.checker.include_files) > 3 else ''}")

            print("\n### 分析器配置")
            print(f"  自动分类: {'启用' if config.analyzer.auto_classify else '禁用'}")
            print(f"  置信度阈值: {config.analyzer.confidence_threshold}")
            print(f"  启用分组: {'启用' if config.analyzer.enable_grouping else '禁用'}")
            print(f"  修复建议: {'启用' if config.analyzer.fix_suggestions else '禁用'}")

            print("\n### 报告器配置")
            print(f"  输出格式: {[f.value for f in config.reporter.output_formats]}")
            print(f"  趋势分析: {'启用' if config.reporter.include_trends else '禁用'}")
            print(f"  文件比较: {'启用' if config.reporter.include_file_comparison else '禁用'}")
            print(f"  最大错误详情: {config.reporter.max_error_details}")

            print("\n### 批量处理配置")
            print(f"  并行处理: {'启用' if config.batch.parallel_processing else '禁用'}")
            print(f"  最大工作线程: {config.batch.max_workers}")
            print(f"  批量大小: {config.batch.batch_size}")

            print("\n### 日志配置")
            print(f"  日志级别: {config.logging.level.value}")
            print(f"  日志目录: {config.logging.log_dir}")
            print(f"  文件日志: {'启用' if config.logging.log_to_file else '禁用'}")

            if config.notifications.enabled:
                print("\n### 通知配置")
                print(f"  邮件通知: {'启用' if config.notifications.email_enabled else '禁用'}")
                print(f"  错误通知: {'启用' if config.notifications.notify_on_error else '禁用'}")
                print(f"  完成通知: {'启用' if config.notifications.notify_on_completion else '禁用'}")

        print(f"\n配置文件: {config_manager.config_file or '使用默认配置'}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_config_validate(args) -> int:
    """验证配置命令

    Usage:
        basedpyright config validate [--config CONFIG_FILE]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("验证BMAD工作流配置")

    try:
        config_manager = ConfigManager(args.config)
        errors = config_manager.validate_config()

        if not errors:
            print("[OK] 配置验证通过！")
            print("所有配置项都有效。")
            return 0
        else:
            print("❌ 发现配置问题：")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")

            print(f"\n配置文件: {config_manager.config_file or '使用默认配置'}")
            return 1

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_config_set(args) -> int:
    """设置配置项命令

    Usage:
        basedpyright config set KEY VALUE [--config CONFIG_FILE]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    if not args.key or not args.value:
        print("错误: 必须指定键和值")
        return 1

    try:
        config_manager = ConfigManager(args.config)

        # 解析值类型
        value = args.value
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)

        # 设置配置值
        config_manager._set_nested_value(args.key, value)

        # 保存配置
        config_manager.save_config()

        print(f"[OK] 配置已更新: {args.key} = {value}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_config_template(args) -> int:
    """生成配置模板命令

    Usage:
        basedpyright config template [--type TYPE] [--output FILE]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("生成配置模板")

    try:
        # 确定输出文件
        if args.output:
            output_file = Path(args.output)
        else:
            template_name = f"{args.type}_template" if args.type else "bmad_template"
            output_file = Path.cwd() / f"{template_name}.json"

        # 创建配置管理器
        config_manager = ConfigManager()

        # 根据类型调整配置
        config = config_manager.get_config()

        if args.type == "minimal":
            config.reporter.include_trends = False
            config.reporter.include_file_comparison = False
            config.notifications.enabled = False
            config.batch.parallel_processing = False
        elif args.type == "comprehensive":
            config.reporter.include_trends = True
            config.reporter.include_file_comparison = True
            config.notifications.enabled = True
            config.batch.parallel_processing = True
            config.batch.max_workers = 8
        elif args.type == "strict":
            config.checker.strict_mode = True
            config.analyzer.confidence_threshold = 0.9
            config.auto_fix_enabled = False  # 严格模式下不自动修复
        elif args.type == "auto":
            config.auto_fix_enabled = True
            config.analyzer.confidence_threshold = 0.6  # 更宽松的阈值
            config.analyzer.fix_suggestions = True

        # 保存模板
        config_manager.config = config
        config_manager.save_config(output_file)

        print(f"[OK] 配置模板已生成: {output_file}")
        print(f"\n模板类型: {args.type or 'default'}")
        print("下一步操作:")
        print("  1. 编辑模板文件以适应项目需求")
        print("  2. 复制到项目根目录作为 .bmadrc.json")
        print("  3. 运行 'basedpyright config validate' 验证配置")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_config_path(args) -> int:
    """显示配置文件路径命令

    Usage:
        basedpyright config path [--config CONFIG_FILE]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    try:
        config_manager = ConfigManager(args.config)

        if config_manager.config_file:
            print(f"配置文件: {config_manager.config_file.absolute()}")
            print(f"存在: {'是' if config_manager.config_file.exists() else '否'}")
        else:
            print("未找到配置文件，使用默认配置")

        print("\n搜索路径:")
        search_paths = [
            Path.cwd() / ".bmadrc.json",
            Path.cwd() / "bmad.config.json",
            Path.cwd() / "basedpyright-workflow.config.json",
            Path.home() / ".bmadrc.json",
        ]

        for path in search_paths:
            exists = "✓" if path.exists() else "✗"
            print(f"  {exists} {path}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1