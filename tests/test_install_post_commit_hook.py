#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Python 版本 post-commit hook 安装程序
使用 TDD 方式开发
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入安装程序
try:
    from scripts.install_post_commit_hook import PostCommitInstaller, Logger
except ImportError as e:
    print(f"无法导入安装程序: {e}")
    print("请先实现 install_post_commit_hook.py")
    sys.exit(1)


class TestPostCommitInstaller(unittest.TestCase):
    """测试 post-commit hook 安装程序"""

    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir) / "project"
        self.project_root.mkdir()

        # 创建测试用的 .git/hooks 目录
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.git_hooks_dir.mkdir(parents=True)

        # 创建测试用的 scripts 目录
        self.scripts_dir = self.project_root / "scripts"
        self.scripts_dir.mkdir()

        # 创建虚拟环境目录
        self.venv_dir = self.project_root / "venv"
        self.venv_python = self.venv_dir / "Scripts" / "python.exe"
        self.venv_python.parent.mkdir(parents=True)

    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_check_python_version_passes(self):
        """测试：检查 Python 版本（应该通过）"""
        installer = PostCommitInstaller(self.project_root)
        result = installer.check_python_version()
        self.assertTrue(result, "Python 版本检查应该通过")

    def test_check_git_installation_with_git(self):
        """测试：检查 Git 安装（有 Git）"""
        installer = PostCommitInstaller(self.project_root)

        # 使用 patch 模拟 subprocess.run 返回成功
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='git version 2.40.0')
            result = installer.check_git_installation()
            self.assertTrue(result, "当 Git 安装时检查应该通过")

    def test_check_git_installation_without_git(self):
        """测试：检查 Git 安装（无 Git）"""
        installer = PostCommitInstaller(self.project_root)

        # 使用 patch 模拟 FileNotFoundError
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = installer.check_git_installation()
            self.assertFalse(result, "当 Git 未安装时检查应该失败")

    def test_check_project_structure_valid(self):
        """测试：检查项目结构（有效）"""
        installer = PostCommitInstaller(self.project_root)
        result = installer.check_project_structure()
        self.assertTrue(result, "有效项目结构检查应该通过")

    def test_check_project_structure_missing_git_hooks(self):
        """测试：检查项目结构（缺少 .git/hooks）"""
        # 删除 hooks 目录
        shutil.rmtree(self.git_hooks_dir)

        installer = PostCommitInstaller(self.project_root)
        result = installer.check_project_structure()
        self.assertFalse(result, "缺少 hooks 目录时检查应该失败")

    def test_copy_hook_success(self):
        """测试：复制 hook（成功）"""
        # 创建 post-commit 源文件
        source_file = self.scripts_dir / "post-commit"
        source_file.write_text("#!/usr/bin/env python3\nprint('test')\n")

        installer = PostCommitInstaller(self.project_root)
        result = installer.copy_hook()
        self.assertTrue(result, "复制 hook 应该成功")

        # 验证文件已复制
        self.assertTrue(installer.post_commit_target.exists(), "Hook 文件应该存在")
        self.assertEqual(
            installer.post_commit_target.read_text(),
            "#!/usr/bin/env python3\nprint('test')\n",
            "Hook 内容应该正确复制"
        )

    def test_copy_hook_missing_source(self):
        """测试：复制 hook（源文件不存在）"""
        installer = PostCommitInstaller(self.project_root)
        result = installer.copy_hook()
        self.assertFalse(result, "源文件不存在时复制应该失败")

    def test_copy_hook_backs_up_existing(self):
        """测试：复制 hook（备份现有 hook）"""
        # 创建现有的 hook 文件
        existing_hook = self.git_hooks_dir / "post-commit"
        existing_hook.write_text("# existing hook")

        # 创建源文件
        source_file = self.scripts_dir / "post-commit"
        source_file.write_text("# new hook")

        installer = PostCommitInstaller(self.project_root)
        result = installer.copy_hook()
        self.assertTrue(result, "复制 hook 应该成功")

        # 验证新 hook 已复制
        self.assertEqual(
            installer.post_commit_target.read_text(),
            "# new hook",
            "新 hook 内容应该正确"
        )

        # 验证备份文件存在
        backup_files = list(self.git_hooks_dir.glob("post-commit.backup.*"))
        self.assertTrue(len(backup_files) > 0, "应该创建备份文件")
        self.assertEqual(
            backup_files[0].read_text(),
            "# existing hook",
            "备份文件内容应该正确"
        )

    def test_validate_hook_exists(self):
        """测试：验证 hook（文件存在）"""
        # 创建 hook 文件
        installer = PostCommitInstaller(self.project_root)
        installer.post_commit_target.write_text("# hook")

        result = installer.validate_hook()
        self.assertTrue(result, "Hook 存在时验证应该通过")

    def test_validate_hook_missing(self):
        """测试：验证 hook（文件不存在）"""
        installer = PostCommitInstaller(self.project_root)

        # 确保文件不存在
        if installer.post_commit_target.exists():
            installer.post_commit_target.unlink()

        result = installer.validate_hook()
        self.assertFalse(result, "Hook 不存在时验证应该失败")

    def test_initialization_with_custom_project_root(self):
        """测试：初始化（自定义项目根目录）"""
        custom_root = Path(self.temp_dir) / "custom"
        custom_root.mkdir()

        installer = PostCommitInstaller(custom_root)
        self.assertEqual(installer.project_root, custom_root, "项目根目录应该正确设置")

    def test_initialization_default_project_root(self):
        """测试：初始化（默认项目根目录）"""
        installer = PostCommitInstaller()
        self.assertEqual(installer.project_root, Path.cwd(), "默认项目根目录应该是当前目录")


class TestLogger(unittest.TestCase):
    """测试日志记录器"""

    def test_logger_methods_exist(self):
        """测试：Logger 方法存在"""
        self.assertTrue(hasattr(Logger, 'section'), "Logger 应该有 section 方法")
        self.assertTrue(hasattr(Logger, 'step'), "Logger 应该有 step 方法")
        self.assertTrue(hasattr(Logger, 'success'), "Logger 应该有 success 方法")
        self.assertTrue(hasattr(Logger, 'warning'), "Logger 应该有 warning 方法")
        self.assertTrue(hasattr(Logger, 'error'), "Logger 应该有 error 方法")


if __name__ == '__main__':
    # 运行测试
    print("=" * 60)
    print("TDD 方式开发：Python post-commit hook 安装程序")
    print("=" * 60)
    print("\n测试结果:")
    print()

    unittest.main(verbosity=2)

