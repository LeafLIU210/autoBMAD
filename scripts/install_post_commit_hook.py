#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 版本的 post-commit hook 安装程序
使用 TDD 方式开发

此脚本自动安装和配置 post-commit hook，使每次 git commit 后
自动更新 CLAUDE.md 文件。

使用方式：
    python scripts/install_post_commit_hook.py
"""

import sys
import os
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional


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


class PostCommitInstaller:
    """post-commit hook 安装程序"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化安装程序

        Args:
            project_root: 项目根目录，默认为当前工作目录
        """
        self.project_root = project_root or Path.cwd()
        self.scripts_dir = self.project_root / "scripts"
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
        self.post_commit_source = self.scripts_dir / "post-commit"
        self.post_commit_target = self.git_hooks_dir / "post-commit"
        self.log_file = self.scripts_dir / "install_post_commit_hook.log"

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

        # 检查源文件
        if not self.post_commit_source.exists():
            Logger.error(f"Hook 源文件不存在: {self.post_commit_source}")
            Logger.warning(f"请确保 {self.post_commit_source} 存在")
            return False

        Logger.success("Hook 源文件存在")

        # 备份现有 hook
        if self.post_commit_target.exists():
            backup_path = str(self.post_commit_target) + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            Logger.step(4.1, f"备份现有 hook 到: {backup_path}")
            shutil.copy2(self.post_commit_target, backup_path)
            Logger.success("备份完成")

        # 复制新 hook
        Logger.step(4.2, "复制 hook 到 .git/hooks/")

        try:
            shutil.copy2(self.post_commit_source, self.post_commit_target)

            # 设置可执行权限（Unix 系统）
            if platform.system() != 'Windows':
                os.chmod(self.post_commit_target, 0o755)

            Logger.success("Hook 复制成功")
            return True
        except Exception as e:
            Logger.error(f"复制 hook 失败: {e}")
            return False

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
    try:
        installer = PostCommitInstaller()
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
