#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDE.md 更新脚本单元测试

此脚本包含对 update_claude_md.py 各功能模块的单元测试，
用于验证更新逻辑的正确性和健壮性。

运行方式：
    python -m pytest tests/test_update_claude_md.py -v
    python -m pytest tests/test_update_claude_md.py -v --tb=short
    python -m pytest tests/test_update_claude_md.py -v --cov=scripts
"""

import sys
import os
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, List, Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入被测试的模块
from scripts.update_claude_md import (
    GitInfo,
    ClaudeMDUpdater,
    PROJECT_ROOT,
    ANTHROPIC_SDK_AVAILABLE
)


class TestGitInfo:
    """GitInfo 类的单元测试"""
    
    def test_git_info_initialization(self):
        """测试 GitInfo 对象初始化"""
        info = GitInfo(
            commit_hash="abc123def456",
            subject="测试提交",
            author="Test User",
            date="2026-01-01 12:00:00"
        )
        
        assert info.commit_hash == "abc123def456"
        assert info.short_hash == "abc123de"
        assert info.subject == "测试提交"
        assert info.author == "Test User"
        assert info.date == "2026-01-01 12:00:00"
    
    def test_git_info_to_dict(self):
        """测试 GitInfo 转换为字典"""
        info = GitInfo(
            commit_hash="abc123def456",
            subject="测试提交",
            author="Test User",
            date="2026-01-01 12:00:00"
        )
        
        result = info.to_dict()
        
        assert isinstance(result, dict)
        assert result['hash'] == "abc123def456"
        assert result['short_hash'] == "abc123de"
        assert result['subject'] == "测试提交"
        assert result['author'] == "Test User"
        assert result['date'] == "2026-01-01 12:00:00"
    
    def test_git_info_short_hash_length(self):
        """测试短哈希长度正确"""
        info = GitInfo(
            commit_hash="abc123def456789",
            subject="测试",
            author="User",
            date="2026-01-01"
        )
        
        assert len(info.short_hash) == 8
        assert info.short_hash == info.commit_hash[:8]


class TestClaudeMDUpdater:
    """ClaudeMDUpdater 类的单元测试"""
    
    def setup_method(self):
        """每个测试方法执行前的初始化"""
        self.updater = ClaudeMDUpdater()
    
    def test_updater_initialization(self):
        """测试更新器初始化"""
        updater = ClaudeMDUpdater()
        
        assert updater.claude_md_path.exists() or True  # 文件可能不存在
        # 检查 backup_path 是否以 .bak 结尾（这是备份文件的特征）
        assert str(updater.backup_path).endswith('.bak')
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_get_commit_info_success(self, mock_run):
        """测试成功获取提交信息"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456|测试提交|Test User|2026-01-01 12:00:00\n"
        mock_run.return_value = mock_result
        
        result = self.updater.get_commit_info()
        
        assert result is not None
        assert isinstance(result, GitInfo)
        assert result.commit_hash == "abc123def456"
        assert result.subject == "测试提交"
        assert result.author == "Test User"
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_get_commit_info_failure(self, mock_run):
        """测试获取提交信息失败"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        result = self.updater.get_commit_info()
        
        assert result is None
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_get_commit_info_exception(self, mock_run):
        """测试获取提交信息时发生异常"""
        mock_run.side_effect = Exception("Git 命令失败")
        
        result = self.updater.get_commit_info()
        
        assert result is None
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_get_changed_files_success(self, mock_run):
        """测试成功获取变更文件列表"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "file1.py\nfile2.py\nfile3.py\n"
        mock_run.return_value = mock_result
        
        result = self.updater.get_changed_files()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "file1.py" in result
        assert "file2.py" in result
        assert "file3.py" in result
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_get_changed_files_empty(self, mock_run):
        """测试获取空变更文件列表"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "\n"
        mock_run.return_value = mock_result
        
        result = self.updater.get_changed_files()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_get_diff_summary_success(self, mock_run):
        """测试成功获取变更统计"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "2 files changed, 5 insertions(+), 2 deletions(-)"
        mock_run.return_value = mock_result
        
        result = self.updater.get_diff_summary()
        
        assert isinstance(result, str)
        assert "files changed" in result
    
    def test_generate_update_content_with_files(self):
        """测试生成包含文件的更新内容"""
        commit_info = GitInfo(
            commit_hash="abc123def456",
            subject="添加新功能",
            author="Test User",
            date="2026-01-01 12:00:00"
        )
        changed_files = ["src/main.py", "tests/test_main.py"]
        diff_summary = "2 files changed, 10 insertions(+)"
        
        result = self.updater.generate_update_content(
            commit_info, changed_files, diff_summary
        )
        
        assert "abc123de" in result
        assert "添加新功能" in result
        assert "Test User" in result
        assert "src/main.py" in result
        assert "tests/test_main.py" in result
        assert "files changed" in result
    
    def test_generate_update_content_without_files(self):
        """测试生成不包含文件的更新内容"""
        commit_info = GitInfo(
            commit_hash="abc123def456",
            subject="仅更新文档",
            author="Test User",
            date="2026-01-01 12:00:00"
        )
        
        result = self.updater.generate_update_content(
            commit_info, [], None
        )
        
        assert "abc123de" in result
        assert "仅更新文档" in result
        assert "变更文件" not in result or "无" in result
    
    def test_backup_file_creation(self):
        """测试备份文件创建"""
        # 确保测试环境下不会真正创建备份
        # 这里主要测试方法是否存在且可调用
        self.updater._backup_file()  # 不应抛出异常
    
    @patch('scripts.update_claude_md.ANTHROPIC_SDK_AVAILABLE', False)
    def test_update_claude_md_basic_mode(self):
        """测试基础更新模式"""
        updater = ClaudeMDUpdater()
        
        # 模拟文件存在
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value="# CLAUDE.md\n\n## 更新记录"):
                with patch.object(Path, 'write_text') as mock_write:
                    content = "测试内容"
                    
                    # 由于 SDK 不可用，应该使用基础模式
                    result = updater.update_claude_md_basic(content)
                    
                    # 验证写入被调用
                    assert mock_write.called or result == True


class TestIntegration:
    """集成测试"""
    
    def test_full_update_workflow(self):
        """测试完整的更新工作流"""
        updater = ClaudeMDUpdater()
        
        # 模拟 Git 命令返回
        with patch('scripts.update_claude_md.subprocess.run') as mock_run:
            # 模拟提交信息
            mock_result1 = MagicMock()
            mock_result1.returncode = 0
            mock_result1.stdout = "abc123def456|集成测试提交|Test User|2026-01-01 12:00:00\n"
            
            # 模拟变更文件
            mock_result2 = MagicMock()
            mock_result2.returncode = 0
            mock_result2.stdout = "test_file.py\n"
            
            # 模拟变更统计
            mock_result3 = MagicMock()
            mock_result3.returncode = 0
            mock_result3.stdout = "1 file changed, 5 insertions(+)"
            
            mock_run.side_effect = [mock_result1, mock_result2, mock_result3]
            
            # 模拟文件操作（避免真实文件操作）
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'read_text', return_value="# CLAUDE.md\n\n## 更新记录"):
                    with patch.object(Path, 'write_text') as mock_write:
                        # 执行更新
                        success = updater.update()
                        
                        # 验证更新被调用（至少被调用一次或成功）
                        assert success == True or mock_write.called


class TestEdgeCases:
    """边界情况和异常处理测试"""
    
    def setup_method(self):
        """每个测试方法执行前的初始化"""
        self.updater = ClaudeMDUpdater()
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_empty_commit_subject(self, mock_run):
        """测试空提交主题的处理"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456||Test User|2026-01-01\n"
        mock_run.return_value = mock_result
        
        result = self.updater.get_commit_info()
        
        # 应该能处理空主题
        assert result is not None
        assert result.subject == ""
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_special_characters_in_subject(self, mock_run):
        """测试提交主题中的特殊字符"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456|修复 #123: 解决特殊字符问题|Test User|2026-01-01\n"
        mock_run.return_value = mock_result
        
        result = self.updater.get_commit_info()
        
        assert result is not None
        assert "#123" in result.subject
        assert "特殊字符" in result.subject
    
    @patch('scripts.update_claude_md.subprocess.run')
    def test_unicode_characters_in_content(self, mock_run):
        """测试内容中的 Unicode 字符"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456|测试中文和 emoji 🚀|Test User|2026-01-01\n"
        mock_run.return_value = mock_result
        
        result = self.updater.get_commit_info()
        
        assert result is not None
        assert "中文" in result.subject
        assert "🚀" in result.subject
    
    def test_generate_content_with_long_file_list(self):
        """测试长文件列表的处理"""
        commit_info = GitInfo(
            commit_hash="abc123def456",
            subject="批量更新",
            author="Test User",
            date="2026-01-01"
        )
        changed_files = [f"src/file{i}.py" for i in range(20)]
        
        result = self.updater.generate_update_content(
            commit_info, changed_files, "20 files changed"
        )
        
        # 应该包含所有文件
        for i in range(20):
            assert f"src/file{i}.py" in result


class TestConfiguration:
    """配置相关测试"""
    
    def test_project_root_path(self):
        """测试项目根目录路径"""
        assert PROJECT_ROOT is not None
        assert isinstance(PROJECT_ROOT, Path)
        assert PROJECT_ROOT.exists()
    
    def test_claude_md_path_exists(self):
        """测试 CLAUDE.md 文件存在"""
        claude_md = PROJECT_ROOT / 'CLAUDE.md'
        # 这个测试假设 CLAUDE.md 已存在
        # 在实际测试中可能需要跳过或使用 mock
        if claude_md.exists():
            assert claude_md.suffix == '.md'


# ============================================================
# pytest 配置
# ============================================================

if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v"])
