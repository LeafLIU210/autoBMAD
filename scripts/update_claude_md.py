#!/usr/bin/env python3
"""
CLAUDE.md Auto Update Script

This script automatically updates CLAUDE.md after git commits.
It uses Claude Agent SDK for intelligent updates when available.
"""

import sys
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Union

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_commit_info() -> Optional[Dict[str, str]]:
    """Get recent commit information"""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%s|%an|%ad'],
            capture_output=True,
            text=True,
            encoding='utf-8',
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


def get_changed_files() -> List[str]:
    """Get list of changed files in this commit"""
    try:
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]
    except Exception as e:
        print(f"Error getting changed files: {e}")
    
    return []


def get_diff_summary() -> str:
    """Get diff statistics"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD~1..HEAD'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error getting diff summary: {e}")
    
    return ""


def generate_update_content(commit_info: Dict[str, str], 
                           changed_files: List[str], 
                           diff_summary: str) -> str:
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
    
    if changed_files:
        content += f"\n**Changed Files**:\n"
        for file_path in changed_files:
            content += f"- `{file_path}`\n"
    
    if diff_summary:
        content += f"\n**Diff Summary**:\n```\n{diff_summary}\n```\n"
    
    return content


def check_anthropic_sdk() -> bool:
    """Check if anthropic SDK is available"""
    try:
        from anthropic import Anthropic
        return True
    except ImportError:
        return False


ANTHROPIC_SDK_AVAILABLE = check_anthropic_sdk()


def update_claude_md_ai(content: str) -> bool:
    """Update using Claude AI (if available)"""
    if not ANTHROPIC_SDK_AVAILABLE:
        print("anthropic SDK not available")
        return False

    try:
        from anthropic import Anthropic

        api_key = os.environ.get('ANTHROPIC_API_KEY', '')

        if not api_key:
            settings_path = PROJECT_ROOT / '.claude' / 'settings.local.json'
            if settings_path.exists():
                import json
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    api_key = settings.get('anthropic_api_key', '')

        if not api_key:
            print("API key not configured")
            return False

        client = Anthropic(api_key=api_key)

        claude_md_path = PROJECT_ROOT / 'CLAUDE.md'
        existing_content = ""
        if claude_md_path.exists():
            existing_content = claude_md_path.read_text(encoding='utf-8')

        prompt = f"""Update CLAUDE.md with this commit:

{content}

Requirements:
1. Keep document structure clean and simple
2. Update last modified date
3. Insert new content at the beginning of update records section
4. Don't remove existing content

Current CLAUDE.md:
{existing_content}

Return complete updated content:"""

        # 使用较短的max_tokens来减少响应时间
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,  # 减少token数量
            messages=[{"role": "user", "content": prompt}]
        )

        # Handle both text blocks and thinking blocks
        if hasattr(message.content[0], 'text'):
            updated_content = message.content[0].text
        elif hasattr(message.content[0], 'type'):
            # Handle different content types
            for block in message.content:
                if hasattr(block, 'text'):
                    updated_content = block.text
                    break
        else:
            print("Unexpected response format")
            return False

        claude_md_path.write_text(updated_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"AI update failed: {e}")
        # 如果AI更新失败，降级到基础模式
        print("Falling back to basic update mode...")
        return update_claude_md_basic(content)


def update_claude_md_basic(content: str) -> bool:
    """Basic update mode without AI"""
    claude_md_path = PROJECT_ROOT / 'CLAUDE.md'

    try:
        if not claude_md_path.exists():
            print("CLAUDE.md not found")
            return False

        existing_content = claude_md_path.read_text(encoding='utf-8')

        # Update timestamp in the header
        timestamp = datetime.now().strftime('%Y-%m-%d')
        date_pattern = r'\*\*最后更新\*\*: \d{4}-\d{2}-\d{2}'
        if re.search(date_pattern, existing_content):
            existing_content = re.sub(
                date_pattern,
                f"**最后更新**: {timestamp}",
                existing_content
            )

        # Parse the content to extract commit info
        commit_info = _parse_commit_content(content)
        if commit_info:
            # Insert new row into the update records table
            table_row = f"| {commit_info['date']} | 2.0 | {commit_info['hash']} - {commit_info['subject']} | {commit_info['files']} |\n"

            # Find the table section and insert after the separator row
            if "| 日期 | 版本 | 提交信息 | 变更内容 |" in existing_content:
                # Find the separator row (|------|------|----------|----------|)
                table_start = existing_content.find("| 日期 | 版本 | 提交信息 | 变更内容 |")
                if table_start != -1:
                    # Find the end of the header line
                    header_end = existing_content.find('\n', table_start)
                    if header_end != -1:
                        # Find the separator line
                        separator_start = existing_content.find('\n|------', header_end)
                        if separator_start != -1:
                            # Find the end of the separator line
                            separator_end = existing_content.find('\n', separator_start)
                            # Insert the new row after the separator
                            updated_content = (
                                existing_content[:separator_end] +
                                '\n' + table_row +
                                existing_content[separator_end:]
                            )
                        else:
                            # No separator found, just insert after header
                            updated_content = (
                                existing_content[:header_end] +
                                '\n|------|------|----------|----------|\n' +
                                table_row +
                                existing_content[header_end:]
                            )
                    else:
                        # Fallback: just append
                        updated_content = existing_content + "\n" + table_row
                else:
                    # Fallback: just append
                    updated_content = existing_content + "\n" + table_row
            else:
                # If no table found, just append
                updated_content = existing_content + "\n" + table_row
        else:
            # Fallback: just append the content
            updated_content = existing_content + "\n" + content

        claude_md_path.write_text(updated_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"Basic update failed: {e}")
        return False


def _parse_commit_content(content: str) -> Optional[Dict[str, str]]:
    """Parse commit information from generated content"""
    try:
        # 处理 None 或空内容
        if content is None or content.strip() == "":
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'files': '代码变更'
            }

        lines = content.strip().split('\n')
        commit_info = {}

        for line in lines:
            if line.startswith('- **Commit**:'):
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    commit_info['hash'] = parts[0].replace('- **Commit**: ', '').strip()
                    commit_info['subject'] = parts[1].strip()
                else:
                    commit_info['hash'] = parts[0].replace('- **Commit**: ', '').strip()
                    commit_info['subject'] = ''
            elif line.startswith('- **Author**:'):
                commit_info['author'] = line.replace('- **Author**: ', '').strip()
            elif line.startswith('- **Time**:'):
                commit_info['date'] = line.replace('- **Time**: ', '').strip()
            elif '**Changed Files**' in content:
                if line.startswith('- `'):
                    files_info = line.replace('- `', '').replace('`', '').strip()
                    if 'files' not in commit_info:
                        commit_info['files'] = files_info
                    else:
                        commit_info['files'] += ', ' + files_info

        # Extract just the date part
        if 'date' in commit_info:
            # Parse the date string and format it properly
            date_str = commit_info['date']
            try:
                # Try to parse the date and format it as YYYY-MM-DD
                parsed_date = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y %z')
                commit_info['date'] = parsed_date.strftime('%Y-%m-%d')
            except:
                # If parsing fails, just use today's date
                commit_info['date'] = datetime.now().strftime('%Y-%m-%d')

        # Default files info if not found
        if 'files' not in commit_info:
            commit_info['files'] = '代码变更'

        return commit_info if commit_info else None
    except Exception as e:
        print(f"Error parsing commit content: {e}")
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'files': '代码变更'
        }


def main() -> int:
    """Main function"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Updating CLAUDE.md... ({timestamp})")
    
    # Get commit info
    commit_info = get_commit_info()
    if not commit_info:
        print("Cannot get commit info, skipping update")
        return 1
    
    print(f"Commit: {commit_info['short_hash']} - {commit_info['subject']}")
    
    # Get changed files
    changed_files = get_changed_files()
    if changed_files:
        print(f"Changed files: {', '.join(changed_files)}")
    else:
        print("Changed files: None")
    
    # Get diff summary
    diff_summary = get_diff_summary()
    
    # Generate content
    content = generate_update_content(commit_info, changed_files, diff_summary)
    if not content:
        print("Cannot generate update content")
        return 1

    # Update CLAUDE.md
    # 默认使用基础模式，更可靠
    force_basic = os.environ.get('CLAUDE_MD_FORCE_BASIC', 'true').lower() == 'true'

    if ANTHROPIC_SDK_AVAILABLE and not force_basic:
        print("Using AI update mode...")
        success = update_claude_md_ai(content)
    else:
        if force_basic:
            print("Using basic update mode (reliable)...")
        else:
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
