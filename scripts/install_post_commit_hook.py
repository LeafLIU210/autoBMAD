#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 版本的 post-commit hook 安装程序 (v2.0.0)
使用 TDD 方式开发

此脚本自动安装和配置 post-commit hook，使每次 git commit 后
自动更新 CLAUDE.md 文件。

特性：
- 命令行参数支持
- 跨平台路径检测
- 详细输出模式

使用方式：
    python scripts/install_post_commit_hook.py
    python scripts/install_post_commit_hook.py --verbose
    python scripts/install_post_commit_hook.py -p /path/to/project
"""

import sys
import os
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any


# 简单的日志记录器（无 Unicode）
class Logger:
    """日志记录器"""

    @staticmethod
    def section(title: str):
        """输出章节标题"""
        separator = '=' * 60
        print(f"\n{separator}")
        print(f"  {title}")
        print(f"{separator}\n")

    @staticmethod
    def step(step_num: int, message: str):
        """输出步骤信息"""
        print(f"[{step_num}] {message}")

    @staticmethod
    def success(message: str):
        """输出成功消息"""
        print(f"[OK] {message}")

    @staticmethod
    def warning(message: str):
        """输出警告消息"""
        print(f"[!] {message}")

    @staticmethod
    def error(message: str):
        """输出错误消息"""
        print(f"[ERROR] {message}")


class PathResolver:
    """Smart path resolver for cross-platform Python detection"""

    def __init__(self, project_root: Path, venv_name: str = "venv"):
        self.project_root: Path = Path(project_root).resolve()
        self.venv_name: str = venv_name

    def get_venv_python(self) -> Path | None:
        """Cross-platform Python path detection"""
        system = platform.system().lower()

        if system == "windows":
            candidates = [
                self.project_root / self.venv_name / "Scripts" / "python.exe",
                self.project_root / self.venv_name / "python.exe",
            ]
        else:  # Linux/macOS
            candidates = [
                self.project_root / self.venv_name / "bin" / "python",
                self.project_root / self.venv_name / "python",
            ]

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def get_venv_pip(self) -> Path | None:
        """Cross-platform pip path detection"""
        system = platform.system().lower()

        if system == "windows":
            candidates = [
                self.project_root / self.venv_name / "Scripts" / "pip.exe",
                self.project_root / self.venv_name / "pip.exe",
            ]
        else:  # Linux/macOS
            candidates = [
                self.project_root / self.venv_name / "bin" / "pip",
                self.project_root / self.venv_name / "pip",
            ]

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Post-Commit Hook 安装程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/install_post_commit_hook.py
  python scripts/install_post_commit_hook.py --verbose
  python scripts/install_post_commit_hook.py -p /path/to/project
  python scripts/install_post_commit_hook.py -v myenv -s scripts --force
        """
    )
    parser.add_argument(
        '--project-root', '-p',
        type=Path,
        default=Path.cwd(),
        help='项目根目录路径 (默认: 当前目录)'
    )
    parser.add_argument(
        '--venv-name', '-v',
        type=str,
        default='venv',
        help='虚拟环境名称 (默认: venv)'
    )
    parser.add_argument(
        '--scripts-dir', '-s',
        type=str,
        default='scripts',
        help='脚本目录名称 (默认: scripts)'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='强制安装，忽略现有备份'
    )
    parser.add_argument(
        '--verify-only', '-x',
        action='store_true',
        help='仅验证现有安装，不执行安装'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    return parser.parse_args()


class PostCommitInstaller:
    """post-commit hook 安装程序 (v2.0.0)"""

    def __init__(self, project_root: Path | None = None,
                 venv_name: str = "venv",
                 scripts_dir: str = "scripts",
                 verbose: bool = False):
        """
        初始化安装程序

        Args:
            project_root: 项目根目录，默认为当前工作目录
            venv_name: 虚拟环境名称
            scripts_dir: 脚本目录名称
            verbose: 是否显示详细输出
        """
        self.project_root: Path = project_root or Path.cwd()
        self.scripts_dir: Path = self.project_root / scripts_dir
        self.git_hooks_dir: Path = self.project_root / ".git" / "hooks"
        self.verbose: bool = verbose

        # Use PathResolver for cross-platform path detection
        self.path_resolver: PathResolver = PathResolver(self.project_root, venv_name)
        self.venv_python: Path | None = self.path_resolver.get_venv_python()

        # Determine post-commit source (Python version)
        self.post_commit_source: Path = self.scripts_dir / "post-commit.py"
        self.post_commit_target: Path = self.git_hooks_dir / "post-commit"
        self.log_file: Path = self.scripts_dir / "install_post_commit_hook.log"

    def check_python_version(self) -> bool:
        """检查 Python 版本"""
        Logger.step(1, "检查 Python 版本")

        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            Logger.error("需要 Python 3.8 或更高版本")
            return False

        Logger.success("Python 版本满足要求")
        return True

    def check_git_installation(self) -> bool:
        """检查 Git 是否安装"""
        Logger.step(2, "检查 Git 安装")

        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            if result.returncode == 0:
                print(result.stdout.strip())
                Logger.success("Git 已安装")
                return True
            else:
                Logger.error("Git 未正确安装")
                return False
        except FileNotFoundError:
            Logger.error("Git 未安装或未配置")
            Logger.warning("请先安装 Git: https://git-scm.com/")
            return False

    def check_project_structure(self) -> bool:
        """检查项目结构"""
        Logger.step(3, "检查项目结构")

        # 检查必要目录
        if not self.project_root.exists():
            Logger.error(f"项目根目录不存在: {self.project_root}")
            return False

        if not self.git_hooks_dir.exists():
            Logger.error(f"Git hooks 目录不存在: {self.git_hooks_dir}")
            return False

        Logger.success("项目结构检查通过")
        return True

    def copy_hook(self) -> bool:
        """复制 post-commit hook"""
        Logger.step(4, "复制 post-commit hook")

        # 检查源文件 (Python version)
        if not self.post_commit_source.exists():
            Logger.error(f"Hook 源文件不存在: {self.post_commit_source}")
            Logger.warning(f"请确保 {self.post_commit_source} 存在")
            return False

        Logger.success(f"Hook 源文件存在: {self.post_commit_source}")

        # 备份现有 hook
        if self.post_commit_target.exists():
            backup_path = str(self.post_commit_target) + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            Logger.step(4.1, f"备份现有 hook 到: {backup_path}")
            shutil.copy2(self.post_commit_target, backup_path)
            Logger.success("备份完成")

        # 创建 hook 文件内容 (calls Python script)
        Logger.step(4.2, "创建 hook 到 .git/hooks/")

        try:
            hook_content = self._generate_hook_content()
            self.post_commit_target.write_text(hook_content, encoding='utf-8')

            # 设置可执行权限（Unix 系统）
            if platform.system() != 'Windows':
                os.chmod(self.post_commit_target, 0o755)

            Logger.success("Hook 创建成功")
            return True
        except Exception as e:
            Logger.error(f"创建 hook 失败: {e}")
            return False

    def _generate_hook_content(self) -> str:
        """Generate hook script content"""
        python_path = self.venv_python
        script_path = self.post_commit_source

        if platform.system().lower() == "windows":
            return f"""@echo off
"{python_path}" "{script_path}"
"""
        else:
            return f"""#!/bin/bash
"{python_path}" "{script_path}"
"""

    def validate_hook(self) -> bool:
        """验证 hook 安装"""
        Logger.step(5, "验证 hook 安装")

        if self.post_commit_target.exists():
            Logger.success("Hook 文件存在")
            # 检查文件大小
            size = self.post_commit_target.stat().st_size
            print(f"Hook 文件大小: {size} 字节")
            return True
        else:
            Logger.error("Hook 文件不存在")
            return False

    def run(self) -> bool:
        """运行安装流程"""
        Logger.section("Python post-commit Hook 安装程序 v1.0.0")

        print(f"项目根目录: {self.project_root}")
        print(f"Python 版本: {sys.version}\n")

        # 执行安装步骤
        steps = [
            ("检查 Python 版本", self.check_python_version),
            ("检查 Git 安装", self.check_git_installation),
            ("检查项目结构", self.check_project_structure),
            ("复制 hook", self.copy_hook),
            ("验证安装", self.validate_hook),
        ]

        for step_name, step_func in steps:
            print()  # 空行分隔
            if not step_func():
                Logger.error(f"安装失败: {step_name}")
                return False

        Logger.section("安装完成")

        print("[SUCCESS] post-commit hook 安装成功！\n")
        print("后续操作：")
        print("  1. 每次执行 git commit 后会自动更新 CLAUDE.md")
        print("  2. 更新记录会保存在 '## 更新记录' 部分")
        print("  3. 可以通过查看日志了解更新详情")
        print()
        print("常用命令：")
        print(f"  手动触发更新: {self.venv_python} {self.scripts_dir / 'update_claude_md.py'}")
        print(f"  查看日志: {self.log_file}")
        print()

        return True


def main():
    """主函数"""
    args = parse_arguments()

    try:
        installer = PostCommitInstaller(
            project_root=args.project_root,
            venv_name=args.venv_name,
            scripts_dir=args.scripts_dir,
            verbose=args.verbose
        )

        if args.verify_only:
            Logger.section("验证 post-commit hook 安装")
            success = installer.validate_hook()
            if success:
                Logger.success("Hook 已正确安装")
            else:
                Logger.error("Hook 未安装或安装不正确")
            sys.exit(0 if success else 1)

        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        Logger.error("\n安装被用户中断")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"安装过程中发生未预期的错误: {e}")
        try:
            import traceback
            traceback.print_exc()
        except:
            # 如果打印堆栈失败，至少退出
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()
