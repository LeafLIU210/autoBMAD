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
from typing import Optional, Dict, List

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

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
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
        return False


def update_claude_md_basic(content: str) -> bool:
    """Basic update mode without AI"""
    claude_md_path = PROJECT_ROOT / 'CLAUDE.md'
    
    try:
        if not claude_md_path.exists():
            print("CLAUDE.md not found")
            return False
        
        existing_content = claude_md_path.read_text(encoding='utf-8')
        
        # Update timestamp
        timestamp= datetime.now().strftime('%Y-%m-%d')
        date_pattern = r'\*\*最后更新\*\*: \d{4}-\d{2}-\d{2}'
        if re.search(date_pattern, existing_content):
            existing_content = re.sub(
                date_pattern,
                f"**最后更新**: {timestamp}",
                existing_content
            )
        
        # Append new content to update records section
        if "## Update Records" in existing_content:
            parts = existing_content.split("## Update Records", 1)
            updated_content = parts[0] + "## Update Records" + content + "\n" + parts[1]
        elif "## 更新记录" in existing_content:
            parts = existing_content.split("## 更新记录", 1)
            updated_content = parts[0] + "## 更新记录" + content + "\n" + parts[1]
        else:
            updated_content = existing_content + content + "\n"
        
        claude_md_path.write_text(updated_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"Basic update failed: {e}")
        return False


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
    if ANTHROPIC_SDK_AVAILABLE:
        print("Using AI update mode...")
        success = update_claude_md_ai(content)
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
