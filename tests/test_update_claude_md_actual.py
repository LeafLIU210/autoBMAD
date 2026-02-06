#!/usr/bin/env python3
"""
CLAUDE.md 自动更新脚本的单元测试 - 实际实现版本
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_claude_md import (
    get_commit_info,
    get_changed_files,
    get_diff_summary,
    generate_update_content,
    check_anthropic_sdk,
    ANTHROPIC_SDK_AVAILABLE,
    update_claude_md_ai,
    update_claude_md_basic,
    main
)

class TestCommitInfo:
    """测试提交信息获取功能"""

    def test_get_commit_info_success(self):
        """测试成功获取提交信息"""
        result = get_commit_info()
        if result is not None:
            assert isinstance(result, dict)
            assert 'hash' in result
            assert 'short_hash' in result
            assert 'subject' in result
            assert 'author' in result
            assert 'date' in result
            assert len(result['short_hash']) == 8

    def test_commit_info_structure(self):
        """测试提交信息结构完整性"""
        result = get_commit_info()
        if result is not None:
            # 验证哈希长度
            assert len(result['hash']) >= 7
            assert len(result['short_hash']) == 8
            # 验证必要字段不为空
            assert result['subject'].strip() != ""
            assert result['author'].strip() != ""


class TestChangedFiles:
    """测试变更文件获取功能"""

    def test_get_changed_files_returns_list(self):
        """测试返回列表类型"""
        result = get_changed_files()
        assert isinstance(result, list)

    def test_get_changed_files_content(self):
        """测试变更文件内容"""
        result = get_changed_files()
        # 应该是文件路径列表
        for file_path in result:
            assert isinstance(file_path, str)
            assert file_path.strip() != ""


class TestDiffSummary:
    """测试差异摘要获取功能"""

    def test_get_diff_summary_returns_string(self):
        """测试返回字符串类型"""
        result = get_diff_summary()
        assert isinstance(result, str)


class TestUpdateContent:
    """测试更新内容生成功能"""

    def test_generate_content_with_valid_info(self):
        """测试生成有效内容"""
        mock_info = {
            'hash': 'abc123def456',
            'short_hash': 'abc123de',
            'subject': '测试提交消息',
            'author': 'Test User',
            'date': '2026-02-06'
        }
        result = generate_update_content(mock_info, ['file1.py', 'file2.py'], 'test diff')

        assert result is not None
        assert 'abc123de' in result
        assert '测试提交消息' in result
        assert 'Test User' in result
        assert 'file1.py' in result
        assert 'file2.py' in result

    def test_generate_content_with_minimal_info(self):
        """测试最小信息生成内容"""
        mock_info = {
            'hash': 'xyz789',
            'short_hash': 'xyz78901',
            'subject': '简单提交',
            'author': 'User',
            'date': '2026-02-06'
        }
        result = generate_update_content(mock_info, [], "")

        assert result is not None
        assert 'xyz78901' in result
        assert '简单提交' in result

    def test_generate_content_without_info(self):
        """测试无信息时返回None"""
        result = generate_update_content(None, [], "")
        assert result is None


class TestAnthropicSDK:
    """测试 Anthropic SDK 相关功能"""

    def test_check_anthropic_sdk(self):
        """测试 SDK 检查功能"""
        available = check_anthropic_sdk()
        assert isinstance(available, bool)
        # 如果可用，ANTHROPIC_SDK_AVAILABLE 应该为 True
        if available:
            assert ANTHROPIC_SDK_AVAILABLE is True

    def test_ai_update_mock(self):
        """测试 AI 更新模式（模拟）"""
        # 测试当 SDK 不可用时的情况
        with patch('scripts.update_claude_md.ANTHROPIC_SDK_AVAILABLE', False):
            result = update_claude_md_ai("test content")
            assert result is False

        # 测试当环境变量未设置时的情况
        with patch('scripts.update_claude_md.ANTHROPIC_SDK_AVAILABLE', True):
            with patch('os.environ.get', return_value=''):
                result = update_claude_md_ai("test content")
                assert result is False


class TestBasicUpdate:
    """测试基础更新功能"""

    def test_basic_update_success(self):
        """测试成功的基础更新"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / 'CLAUDE.md'
            original_content = """# CLAUDE.md

**最后更新**: 2026-01-01

## 更新记录

### 2026-01-01
- 初始版本
"""
            temp_path.write_text(original_content, encoding='utf-8')

            # 模拟 PROJECT_ROOT
            with patch('scripts.update_claude_md.PROJECT_ROOT', temp_path.parent):
                content = """
### 2026-02-06
- **Commit**: abc123de - 测试更新
- **Author**: Test User
"""
                result = update_claude_md_basic(content)

                assert result is True
                updated_content = temp_path.read_text(encoding='utf-8')
                assert 'abc123de' in updated_content
                assert '测试更新' in updated_content

    def test_basic_update_no_file(self):
        """测试文件不存在的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('scripts.update_claude_md.PROJECT_ROOT', Path(temp_dir)):
                result = update_claude_md_basic("test content")
                assert result is False

    def test_basic_update_create_new_section(self):
        """测试创建新的更新记录部分"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / 'CLAUDE.md'
            original_content = """# CLAUDE.md

**最后更新**: 2026-01-01
"""
            temp_path.write_text(original_content, encoding='utf-8')

            with patch('scripts.update_claude_md.PROJECT_ROOT', temp_path.parent):
                content = """
### 2026-02-06
- **Commit**: abc123de - 新建更新
- **Author**: Test User
"""
                result = update_claude_md_basic(content)

                assert result is True
                updated_content = temp_path.read_text(encoding='utf-8')
                assert 'abc123de' in updated_content
                assert '新建更新' in updated_content


class TestMainFunction:
    """测试主函数"""

    @patch('scripts.update_claude_md.get_commit_info')
    @patch('scripts.update_claude_md.get_changed_files')
    @patch('scripts.update_claude_md.generate_update_content')
    @patch('scripts.update_claude_md.update_claude_md_basic')
    def test_main_success_basic_mode(self, mock_update, mock_generate, mock_changed, mock_commit):
        """测试主函数成功执行（基础模式）"""
        # 设置模拟返回值
        mock_commit.return_value = {
            'hash': 'abc123',
            'short_hash': 'abc12345',
            'subject': '测试提交',
            'author': 'Test User',
            'date': '2026-02-06'
        }
        mock_changed.return_value = ['test.py']
        mock_generate.return_value = "Test update content"
        mock_update.return_value = True

        # 设置 SDK 不可用
        with patch('scripts.update_claude_md.ANTHROPIC_SDK_AVAILABLE', False):
            result = main()

            assert result == 0
            mock_commit.assert_called_once()
            mock_changed.assert_called_once()
            mock_generate.assert_called_once()
            mock_update.assert_called_once()

    @patch('scripts.update_claude_md.get_commit_info')
    def test_main_no_commit_info(self, mock_commit):
        """测试无法获取提交信息的情况"""
        mock_commit.return_value = None

        result = main()
        assert result == 1

    @patch('scripts.update_claude_md.get_commit_info')
    @patch('scripts.update_claude_md.generate_update_content')
    @patch('scripts.update_claude_md.update_claude_md_basic')
    def test_main_no_content_generated(self, mock_update, mock_generate, mock_commit):
        """测试无法生成内容的情况"""
        mock_commit.return_value = {
            'hash': 'abc123',
            'short_hash': 'abc12345',
            'subject': '测试提交',
            'author': 'Test User',
            'date': '2026-02-06'
        }
        mock_generate.return_value = None

        with patch('scripts.update_claude_md.ANTHROPIC_SDK_AVAILABLE', False):
            result = main()
            assert result == 1


class TestIntegration:
    """集成测试"""

    def test_full_update_workflow(self):
        """测试完整更新工作流"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / 'CLAUDE.md'
            original_content = """# CLAUDE.md

**最后更新**: 2026-01-01

## 更新记录

"""
            temp_path.write_text(original_content, encoding='utf-8')

            # 模拟完整的 Git 环境
            with patch('scripts.update_claude_md.PROJECT_ROOT', temp_path.parent):
                # 模拟 Git 命令
                with patch('scripts.update_claude_md.subprocess.run') as mock_run:
                    # 模拟提交信息
                    mock_run.side_effect = [
                        # 提交信息
                        MagicMock(returncode=0, stdout='abc123def456|测试提交|Test User|2026-02-06'),
                        # 变更文件
                        MagicMock(returncode=0, stdout='file1.py\nfile2.py'),
                        # 差异统计
                        MagicMock(returncode=0, stdout='2 files changed, 10 insertions(+), 5 deletions(-)'),
                    ]

                    # 模拟 SDK 不可用，强制使用基础模式
                    with patch('scripts.update_claude_md.ANTHROPIC_SDK_AVAILABLE', False):
                        # 模拟文件操作
                        with patch('pathlib.Path.exists', return_value=True):
                            with patch('pathlib.Path.read_text', return_value=original_content):
                                with patch('pathlib.Path.write_text') as mock_write:
                                    # 执行更新
                                    result = main()

                                    # 验证结果
                                    assert result == 0
                                    assert mock_write.called


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_commit_info(self):
        """测试空提交信息的处理"""
        result = generate_update_content({}, [], "")
        assert result is None

    def test_special_characters_in_content(self):
        """测试特殊字符处理"""
        mock_info = {
            'hash': 'abc123def456',
            'short_hash': 'abc123de',
            'subject': '修复 #123: 解决特殊字符问题 & 优化',
            'author': 'Test User',
            'date': '2026-02-06'
        }
        result = generate_update_content(mock_info, ['src/file.py'], 'special chars test')

        assert result is not None
        assert '#123' in result
        assert '&' in result

    def test_unicode_characters(self):
        """测试Unicode字符处理"""
        mock_info = {
            'hash': 'abc123def456',
            'short_hash': 'abc123de',
            'subject': '测试中文和emoji 🚀',
            'author': '测试用户',
            'date': '2026-02-06'
        }
        result = generate_update_content(mock_info, ['中文文件名.py'], '')

        assert result is not None
        assert '中文' in result
        assert '🚀' in result
        assert '中文文件名.py' in result


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])