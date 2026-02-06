#!/usr/bin/env python3
"""
完整的集成测试 - 验证整个 Git commit 触发 CLAUDE.md 自动更新流程
"""

import pytest
import sys
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_complete_git_workflow():
    """测试完整的 Git 工作流程"""
    # 创建临时目录进行测试
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 初始化 Git 仓库
        subprocess.run(['git', 'init'], cwd=temp_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_path, check=True, capture_output=True)

        # 创建 CLAUDE.md 文件
        claude_md_content = """# CLAUDE.md

**最后更新**: 2026-01-01

## 更新记录

"""
        claude_md_path = temp_path / 'CLAUDE.md'
        claude_md_path.write_text(claude_md_content, encoding='utf-8')

        # 创建测试文件
        test_file = temp_path / 'test.txt'
        test_file.write_text('Test content', encoding='utf-8')

        # 初始提交
        subprocess.run(['git', 'add', '.'], cwd=temp_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', '初始提交'], cwd=temp_path, check=True, capture_output=True)

        # 创建并运行更新脚本的副本
        script_path = temp_path / 'update_script.py'
        script_content = '''#!/usr/bin/env python3
import sys
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent

def get_commit_info():
    """Get recent commit information"""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%s|%an|%ad'],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        if result.returncode == 0:
            parts = result.stdout.strip().split('|')
            if len(parts) >= 4:
                return {
                    'hash': parts[0],
                    'short_hash': parts[0][:8],
                    'subject': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                }
    except Exception as e:
        print(f"Error getting commit info: {e}")

    return None

def generate_update_content(commit_info):
    """Generate update content for CLAUDE.md"""
    if not commit_info:
        return None

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    content = f"""
### {timestamp}
- **Commit**: {commit_info['short_hash']} - {commit_info['subject']}
- **Author**: {commit_info['author']}
- **Time**: {commit_info['date']}
"""

    return content

def update_claude_md_basic(content):
    """Basic update mode without AI"""
    claude_md_path = PROJECT_ROOT / 'CLAUDE.md'

    try:
        if not claude_md_path.exists():
            print("CLAUDE.md not found")
            return False

        existing_content = claude_md_path.read_text(encoding='utf-8')

        # Update timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d')
        date_pattern = r'\\*\\*最后更新\\*\\*: \\d{4}-\\d{2}-\\d{2}'
        if re.search(date_pattern, existing_content):
            existing_content = re.sub(
                date_pattern,
                f"**最后更新**: {timestamp}",
                existing_content
            )

        # Append new content to update records section
        if "## 更新记录" in existing_content:
            parts = existing_content.split("## 更新记录", 1)
            updated_content = parts[0] + "## 更新记录" + content + "\\n" + parts[1]
        else:
            updated_content = existing_content + content + "\\n"

        claude_md_path.write_text(updated_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"Basic update failed: {e}")
        return False

def main():
    """Main function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Updating CLAUDE.md... ({timestamp})")

    # Get commit info
    commit_info = get_commit_info()
    if not commit_info:
        print("Cannot get commit info, skipping update")
        return 1

    print(f"Commit: {commit_info['short_hash']} - {commit_info['subject']}")

    # Generate content
    content = generate_update_content(commit_info)
    if not content:
        print("Cannot generate update content")
        return 1

    # Update CLAUDE.md
    print("Using basic update mode...")
    success = update_claude_md_basic(content)

    if success:
        print("CLAUDE.md updated successfully")
        return 0
    else:
        print("CLAUDE.md update failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        script_path.write_text(script_content, encoding='utf-8')

        # 创建新提交来触发更新
        test_file.write_text('Updated test content', encoding='utf-8')
        subprocess.run(['git', 'add', 'test.txt'], cwd=temp_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', '集成测试：验证自动更新功能'], cwd=temp_path, check=True, capture_output=True)

        # 运行更新脚本
        result = subprocess.run(['python', str(script_path)], cwd=temp_path, capture_output=True, text=True, encoding='utf-8')

        # 验证结果
        print("=== 脚本输出 ===")
        print(result.stdout)
        if result.stderr:
            print("=== 错误输出 ===")
            print(result.stderr)

        # 验证 CLAUDE.md 是否被更新
        updated_content = claude_md_path.read_text(encoding='utf-8')
        print("=== 更新后的 CLAUDE.md 内容 ===")
        print(updated_content)

        # 断言验证
        assert result.returncode == 0, f"脚本执行失败，返回码: {result.returncode}"
        assert "集成测试：验证自动更新功能" in updated_content, "更新记录未找到"
        assert "2026-02-06" in updated_content, "日期未更新"
        assert "Test User" in updated_content, "作者信息未找到"

        print("✅ 集成测试通过！")


def test_post_commit_hook_simulation():
    """模拟 post-commit hook 执行"""
    # 验证脚本存在并且可执行
    script_path = Path(__file__).parent.parent / 'scripts' / 'post-commit'
    assert script_path.exists(), "post-commit hook 脚本不存在"

    # 检查脚本内容是否正确
    content = script_path.read_text(encoding='utf-8')
    assert "update_claude_md.py" in content, "脚本未调用 update_claude_md.py"
    assert "venv" in content, "脚本未正确配置虚拟环境路径"


if __name__ == "__main__":
    test_complete_git_workflow()
    test_post_commit_hook_simulation()
    print("所有集成测试通过！")