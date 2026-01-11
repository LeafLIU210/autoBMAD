"""模板命令模块

提供基于模板的工作流配置生成和管理功能。
"""

import sys
from pathlib import Path

from ..templates import get_template_manager, TemplateMetadata


def _print_header(message: str):
    """打印带边框的标题."""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80 + "\n")


def _print_template_info(metadata: TemplateMetadata, index: int = None) -> None:
    """打印模板信息

    Args:
        metadata: 模板元数据
        index: 模板索引（可选）
    """
    prefix = f"{index}. " if index else ""
    print(f"{prefix}📋 {metadata.name}")
    print(f"   📝 描述: {metadata.description}")
    print(f"   🏷️  类型: {metadata.project_type.value} / {metadata.workflow_type.value}")
    print(f"   🏷️  标签: {', '.join(metadata.tags)}")
    print(f"   📋 版本: {metadata.version} by {metadata.author}")
    print(f"   🔧 要求: {', '.join(metadata.requirements) if metadata.requirements else '无特殊要求'}")
    print()


def cmd_template_list(args) -> int:
    """列出可用模板命令

    Usage:
        basedpyright template list [--type TYPE] [--workflow WORKFLOW]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("可用的BMAD工作流模板")

    try:
        template_manager = get_template_manager()
        templates = template_manager.list_templates()

        # 过滤模板
        if args.type:
            templates = [t for t in templates if t.project_type.value == args.type]
        if args.workflow:
            templates = [t for t in templates if t.workflow_type.value == args.workflow]

        if not templates:
            print("未找到匹配的模板。")
            return 1

        print(f"共找到 {len(templates)} 个模板:\n")

        for i, metadata in enumerate(templates, 1):
            _print_template_info(metadata, i)

        print("使用方法:")
        print("  basedpyright template create <模板名>")
        print("  basedpyright template auto-detect")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_template_create(args) -> int:
    """从模板创建配置命令

    Usage:
        basedpyright template create TEMPLATE_NAME [--output CONFIG_FILE]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    if not args.template_name:
        print("错误: 必须指定模板名称")
        return 1

    _print_header(f"从模板创建配置: {args.template_name}")

    try:
        template_manager = get_template_manager()
        template = template_manager.get_template(args.template_name)

        if not template:
            print(f"错误: 未找到模板 '{args.template_name}'")
            print("可用模板:")
            for name in template_manager.templates.keys():
                print(f"  - {name}")
            return 1

        # 显示模板信息
        print("模板信息:")
        _print_template_info(template.metadata)

        # 验证环境
        print("验证项目环境...")
        errors = template.validate_environment()
        if errors:
            print("⚠️  环境警告:")
            for error in errors:
                print(f"   - {error}")
            print()

        # 确定输出文件
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = Path.cwd() / ".bmadrc.json"

        # 检查文件是否已存在
        if output_file.exists():
            if not args.force:
                response = input(f"配置文件 {output_file} 已存在，是否覆盖? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("操作已取消")
                    return 0

        # 生成配置
        success = template_manager.save_template_config(
            args.template_name,
            output_file,
            Path.cwd()
        )

        if success:
            print("\n[OK] 配置文件已生成!")
            print(f"  输出文件: {output_file}")
            print("\n下一步操作:")
            print("  1. 根据需要调整配置文件")
            print("  2. 运行 'basedpyright config validate' 验证配置")
            print("  3. 运行 'basedpyright workflow' 开始使用")
        else:
            print("生成配置失败")
            return 1

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_template_detect(args) -> int:
    """自动检测模板命令

    Usage:
        basedpyright template auto-detect [--project-path PATH]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    _print_header("自动检测适合的模板")

    try:
        project_path = Path(args.project_path) if args.project_path else Path.cwd()
        template_manager = get_template_manager()

        print(f"扫描项目路径: {project_path.absolute()}\n")

        # 自动检测
        recommended_template = template_manager.auto_detect_template(project_path)

        if recommended_template:
            template = template_manager.get_template(recommended_template)
            if template:
                print("🎯 推荐模板:")
                _print_template_info(template.metadata)

                # 询问是否创建配置
                try:
                    response = input("\n是否使用此模板创建配置文件? (Y/n): ")
                    if response.lower() in ['', 'y', 'yes']:
                        output_file = Path.cwd() / ".bmadrc.json"
                        success = template_manager.save_template_config(
                            recommended_template,
                            output_file,
                            project_path
                        )

                        if success:
                            print(f"\n[OK] 配置文件已生成: {output_file}")
                        else:
                            print("生成配置失败")
                            return 1
                    else:
                        print("操作已取消")
                except (EOFError, KeyboardInterrupt):
                    print("\n操作已取消")
            else:
                print(f"错误: 推荐的模板 '{recommended_template}' 不可用")
                return 1
        else:
            print("无法自动检测适合的模板")
            print("请手动选择模板:")
            for name in template_manager.templates.keys():
                print(f"  - {name}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_template_info(args) -> int:
    """显示模板详细信息命令

    Usage:
        basedpyright template info TEMPLATE_NAME

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    if not args.template_name:
        print("错误: 必须指定模板名称")
        return 1

    _print_header(f"模板详情: {args.template_name}")

    try:
        template_manager = get_template_manager()
        template = template_manager.get_template(args.template_name)

        if not template:
            print(f"错误: 未找到模板 '{args.template_name}'")
            return 1

        metadata = template.metadata

        # 详细信息
        print(f"📋 模板名称: {metadata.name}")
        print(f"📝 详细描述: {metadata.description}")
        print(f"🏷️  项目类型: {metadata.project_type.value}")
        print(f"🔄 工作流类型: {metadata.workflow_type.value}")
        print(f"📋 版本: {metadata.version}")
        print(f"👤 作者: {metadata.author}")
        print(f"🏷️  标签: {', '.join(metadata.tags)}")
        print(f"🔧 系统要求: {', '.join(metadata.requirements) if metadata.requirements else '无特殊要求'}")
        print(f"📅 创建时间: {metadata.created_at}")
        print(f"📅 更新时间: {metadata.updated_at}")

        # 显示生成的配置预览
        print("\n🔧 生成的配置预览:")
        config = template.generate_config()
        print(f"  项目名称: {config.project_name}")
        print(f"  自动修复: {'启用' if config.auto_fix_enabled else '禁用'}")
        print(f"  Git集成: {'启用' if config.git_integration else '禁用'}")
        print(f"  严格模式: {'启用' if config.checker.strict_mode else '禁用'}")
        print(f"  置信度阈值: {config.analyzer.confidence_threshold}")

        print("\n💡 使用此模板:")
        print(f"  basedpyright template create {args.template_name}")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_template_validate(args) -> int:
    """验证模板命令

    Usage:
        basedpyright template validate TEMPLATE_NAME [--project-path PATH]

    Args:
        args: 命令行参数对象

    Returns:
        退出码（0=成功，1=失败）
    """
    if not args.template_name:
        print("错误: 必须指定模板名称")
        return 1

    _print_header(f"验证模板: {args.template_name}")

    try:
        template_manager = get_template_manager()
        template = template_manager.get_template(args.template_name)

        if not template:
            print(f"错误: 未找到模板 '{args.template_name}'")
            return 1

        project_path = Path(args.project_path) if args.project_path else Path.cwd()

        print(f"项目路径: {project_path.absolute()}\n")

        # 环境验证
        errors = template.validate_environment()
        if not errors:
            print("✅ 环境验证通过！此模板适合当前项目。")
        else:
            print("⚠️  环境兼容性问题:")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")

            print("\n💡 建议:")
            print("  - 可以选择更适合的模板")
            print("  - 或手动调整项目结构")
            print("  - 或强制使用此模板并忽略警告")

        # 配置生成测试
        print("\n🔧 测试配置生成...")
        try:
            config = template.generate_config()
            print("✅ 配置生成成功")
        except Exception as e:
            print(f"❌ 配置生成失败: {e}")
            return 1

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1