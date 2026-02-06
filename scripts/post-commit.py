#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Post-Commit Hook - Python 跨平台版本

此脚本在 git commit 完成后自动执行，调用 Python 脚本更新 CLAUDE.md。
它通过 Claude Agent SDK 智能分析提交内容，生成有意义的更新记录。

跨平台兼容：Windows (PowerShell/Git Bash)、Linux、macOS

使用方式：
1. 将 scripts/post-commit.py 复制到 .git/hooks/post-commit
2. 或创建 .git/hooks/post-commit.bat 调用此脚本
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 版本信息
SCRIPT_VERSION = "1.0.0"
SCRIPT_NAME = "post-commit hook"


class GitHookInstaller:
    """Git Hook 安装器"""
    
    @staticmethod
    def get_project_root() -> Path:
        """获取项目根目录"""
        # 方法1: 使用 Git 命令获取根目录
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                root = Path(result.stdout.strip())
                if root.exists():
                    return root
        except Exception:
            pass
        
        # 方法2: 从当前目录向上查找 .git 目录
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / '.git').is_dir():
                return parent
        
        # 方法3: 备用：从 .git/hooks 向上两级
        hooks_dir = Path.cwd()
        if hooks_dir.name == 'hooks':
            return hooks_dir.parent.parent
        
        return current.parent
    
    @staticmethod
    def get_venv_python(venv_name: str = "venv") -> Optional[Path]:
        """获取虚拟环境 Python 解释器路径"""
        project_root = GitHookInstaller.get_project_root()
        logger.info(f"项目根目录: {project_root}")
        
        # 不同平台的 Python 路径
        candidates = [
            project_root / venv_name / "Scripts" / "python.exe",      # Windows
            project_root / venv_name / "bin" / "python",              # Linux/macOS
            project_root / venv_name / "python.exe",                   # Windows (备用)
        ]
        
        for candidate in candidates:
            logger.info(f"检查: {candidate} (存在: {candidate.exists()})")
            if candidate.exists():
                logger.info(f"找到 Python 解释器: {candidate}")
                return candidate
        
        return None
    
    @staticmethod
    def get_update_script() -> Optional[Path]:
        """获取更新脚本路径"""
        project_root = GitHookInstaller.get_project_root()
        update_script = project_root / "scripts" / "update_claude_md.py"
        
        if update_script.exists():
            return update_script
        
        return None


class PostCommitHook:
    """Post-Commit Hook 执行器"""
    
    def __init__(self):
        self.project_root = GitHookInstaller.get_project_root()
        self.venv_python = GitHookInstaller.get_venv_python()
        self.update_script = GitHookInstaller.get_update_script()
    
    def run(self) -> bool:
        """执行 hook 主逻辑"""
        logger.info("=" * 50)
        logger.info(f"{SCRIPT_NAME} v{SCRIPT_VERSION} 开始执行")
        logger.info(f"项目根目录: {self.project_root}")
        
        # 验证必要的文件
        if not self._validate_prerequisites():
            logger.warning("跳过 CLAUDE.md 更新：先决条件验证失败")
            return True
        
        # 执行更新脚本
        success = self._execute_update_script()
        
        if success:
            logger.info("CLAUDE.md 更新完成")
        else:
            logger.warning("CLAUDE.md 更新失败，但不影响提交")
        
        logger.info(f"{SCRIPT_NAME} 执行完成")
        logger.info("=" * 50)
        
        return True
    
    def _validate_prerequisites(self) -> bool:
        """验证先决条件"""
        logger.info("验证必要的文件...")
        
        if self.venv_python is None:
            logger.error(f"虚拟环境 Python 未找到")
            return False
        
        if self.update_script is None:
            logger.error(f"更新脚本未找到")
            return False
        
        return True
    
    def _execute_update_script(self) -> bool:
        """执行更新脚本"""
        logger.info(f"执行更新脚本: {self.update_script}")
        
        try:
            # 使用subprocess 执行 Python 脚本
            result = subprocess.run(
                [str(self.venv_python), str(self.update_script)],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=60  # 60秒超时
            )
            
            # 输出脚本的日志
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        logger.info(f"  {line}")
            
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line:
                        logger.warning(f"  {line}")
            
            if result.returncode == 0:
                logger.info("更新脚本执行成功")
                return True
            else:
                logger.error(f"更新脚本执行失败 (退出码: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("更新脚本执行超时 (60秒)")
            return False
        except Exception as e:
            logger.error(f"执行更新脚本时发生异常: {e}")
            return False


def main():
    """主入口点"""
    try:
        hook = PostCommitHook()
        success = hook.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Hook 执行时发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 0  # 不阻止提交


if __name__ == "__main__":
    sys.exit(main())
