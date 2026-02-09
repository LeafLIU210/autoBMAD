#!/usr/bin/env python3
"""
Multi-Document Auto Update Script

This script automatically updates CLAUDE.md and related documents in claude_docs/
directory after git commits. It uses Claude Agent SDK for intelligent updates when available.

Features:
- Multi-document intelligent updates
- Anti-loop protection mechanisms
- Smart document mapping based on file changes
- Batch processing for improved performance
"""

import sys
import os
import subprocess
import re
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Union, Set
from dataclasses import dataclass

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class UpdateConfig:
    """配置信息类"""
    lock_file: Path = PROJECT_ROOT / '.multi_doc_update.lock'
    timestamp_file: Path = PROJECT_ROOT / '.last_update.timestamp'
    env_var: str = 'MULTI_DOC_UPDATING'
    max_frequency: int = 300  # 5分钟内最多执行一次
    log_file: Path = PROJECT_ROOT / 'scripts' / 'multi_doc_update.log'


class AntiLoopProtection:
    """防循环保护机制"""

    def __init__(self, config: UpdateConfig = None):
        self.config = config or UpdateConfig()
        self._acquired_lock = False

    def can_proceed(self) -> bool:
        """检查是否可以继续执行更新"""
        print(f"检查防循环保护机制...")

        # 检查标志文件
        if self.config.lock_file.exists():
            print(f"跳过更新：标志文件存在 {self.config.lock_file}")
            return False

        # 检查环境变量
        if os.environ.get(self.config.env_var) == '1':
            print(f"跳过更新：环境变量 {self.config.env_var} 已设置")
            return False

        # 检查时间窗口
        if self._is_too_frequent():
            print(f"跳过更新：更新频率过高（5分钟内已执行过）")
            return False

        print("防循环保护检查通过")
        return True

    def _is_too_frequent(self) -> bool:
        """检查更新频率是否过高"""
        if not self.config.timestamp_file.exists():
            return False

        try:
            last_update = float(self.config.timestamp_file.read_text().strip())
            time_since_last = time.time() - last_update
            if time_since_last < self.config.max_frequency:
                print(f"距离上次更新仅 {time_since_last:.1f} 秒，少于阈值 {self.config.max_frequency} 秒")
                return True
        except Exception as e:
            print(f"读取时间戳文件失败: {e}")

        return False

    def acquire_lock(self):
        """获取锁"""
        if self.config.lock_file.exists():
            return False

        try:
            with open(self.config.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            self._acquired_lock = True
            return True
        except Exception as e:
            print(f"获取锁失败: {e}")
            return False

    def release_lock(self):
        """释放锁"""
        if self._acquired_lock and self.config.lock_file.exists():
            try:
                self.config.lock_file.unlink()
            except Exception as e:
                print(f"释放锁失败: {e}")
        self._acquired_lock = False

    def update_timestamp(self):
        """更新时间戳"""
        try:
            self.config.timestamp_file.write_text(str(time.time()))
        except Exception as e:
            print(f"更新时间戳失败: {e}")


class MultiDocUpdater:
    """多文档更新控制器"""

    def __init__(self):
        # 目标文档列表
        self.target_docs = [
            'CLAUDE.md',
            'claude_docs/ai_workflow.md',
            'claude_docs/bmad_methodology.md',
            'claude_docs/core_principles.md',
            'claude_docs/development_rules.md',
            'claude_docs/git-commit-trigger-update.md',
            'claude_docs/project_tree.md',
            'claude_docs/quality_assurance.md',
            'claude_docs/quick_reference.md',
            'claude_docs/technical_specs.md',
            'claude_docs/testing_guide.md',
            'claude_docs/venv.md',
            'claude_docs/workflow_tools.md',
        ]

        # 建立文件变更到文档更新的映射关系
        self.update_mapping = {
            'scripts/': ['claude_docs/git-commit-trigger-update.md'],
            'autoBMAD/': ['claude_docs/workflow_tools.md'],
            'claude_docs/core_principles.md': ['claude_docs/core_principles.md'],
            'claude_docs/ai_workflow.md': ['claude_docs/ai_workflow.md'],
            'claude_docs/bmad_methodology.md': ['claude_docs/bmad_methodology.md'],
            'claude_docs/development_rules.md': ['claude_docs/development_rules.md'],
            'claude_docs/project_tree.md': ['claude_docs/project_tree.md'],
            'claude_docs/quality_assurance.md': ['claude_docs/quality_assurance.md'],
            'claude_docs/quick_reference.md': ['claude_docs/quick_reference.md'],
            'claude_docs/technical_specs.md': ['claude_docs/technical_specs.md'],
            'claude_docs/testing_guide.md': ['claude_docs/testing_guide.md'],
            'claude_docs/venv.md': ['claude_docs/venv.md'],
            'CLAUDE.md': ['CLAUDE.md', 'claude_docs/quick_reference.md'],  # CLAUDE.md更新时也更新快速参考
        }

    def get_docs_to_update(self, changed_files: List[str]) -> List[str]:
        """根据变更文件确定需要更新的文档"""
        docs_to_update = set()

        # 总是更新CLAUDE.md
        docs_to_update.add('CLAUDE.md')

        for file_path in changed_files:
            file_path = file_path.strip()
            if not file_path:
                continue

            print(f"分析变更文件: {file_path}")

            # 检查精确匹配
            if file_path in self.update_mapping:
                docs_to_update.update(self.update_mapping[file_path])
                print(f"  -> 精确匹配，更新: {self.update_mapping[file_path]}")
                continue

            # 检查前缀匹配
            for pattern, docs in self.update_mapping.items():
                if pattern.endswith('/') and file_path.startswith(pattern):
                    docs_to_update.update(docs)
                    print(f"  -> 前缀匹配 '{pattern}'，更新: {docs}")
                    break
                elif not pattern.endswith('/') and pattern in file_path:
                    docs_to_update.update(docs)
                    print(f"  -> 内容匹配 '{pattern}'，更新: {docs}")
                    break

        # 过滤掉不存在的文档
        existing_docs = []
        for doc in docs_to_update:
            doc_path = PROJECT_ROOT / doc
            if doc_path.exists():
                existing_docs.append(doc)
            else:
                print(f"警告：文档不存在 {doc}")

        return sorted(existing_docs)

    def update_single_doc(self, doc_path: str, commit_info: Dict[str, str],
                         changed_files: List[str]) -> bool:
        """更新单个文档"""
        try:
            doc_full_path = PROJECT_ROOT / doc_path
            print(f"更新文档: {doc_path}")

            if not doc_full_path.exists():
                print(f"文档不存在: {doc_path}")
                return False

            if doc_path == 'CLAUDE.md':
                return self._update_claude_md(commit_info, changed_files)
            else:
                return self._update_doc_md(doc_path, commit_info, changed_files)

        except Exception as e:
            print(f"更新文档 {doc_path} 失败: {e}")
            return False

    def _update_claude_md(self, commit_info: Dict[str, str],
                         changed_files: List[str]) -> bool:
        """更新CLAUDE.md（复用原有逻辑）"""
        try:
            # 导入原有的更新逻辑
            content = self._generate_update_content(commit_info, changed_files, "")

            claude_md_path = PROJECT_ROOT / 'CLAUDE.md'
            if not claude_md_path.exists():
                return False

            existing_content = claude_md_path.read_text(encoding='utf-8')

            # 更新timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d')
            date_pattern = r'\*\*最后更新\*\*: \d{4}-\d{2}-\d{2}'
            if re.search(date_pattern, existing_content):
                existing_content = re.sub(
                    date_pattern,
                    f"**最后更新**: {timestamp}",
                    existing_content
                )

            # 解析并插入新的表格行
            commit_info_parsed = self._parse_commit_content(content)
            if commit_info_parsed:
                table_row = f"| {commit_info_parsed['date']} | 2.0 | {commit_info_parsed['hash']} - {commit_info_parsed['subject']} | {commit_info_parsed['files']} |\n"

                if "| 日期 | 版本 | 提交信息 | 变更内容 |" in existing_content:
                    table_start = existing_content.find("| 日期 | 版本 | 提交信息 | 变更内容 |")
                    if table_start != -1:
                        header_end = existing_content.find('\n', table_start)
                        if header_end != -1:
                            separator_start = existing_content.find('\n|------', header_end)
                            if separator_start != -1:
                                separator_end = existing_content.find('\n', separator_start)
                                updated_content = (
                                    existing_content[:separator_end] +
                                    '\n' + table_row +
                                    existing_content[separator_end:]
                                )
                            else:
                                updated_content = (
                                    existing_content[:header_end] +
                                    '\n|------|------|----------|----------|\n' +
                                    table_row +
                                    existing_content[header_end:]
                                )
                        else:
                            updated_content = existing_content + "\n" + table_row
                    else:
                        updated_content = existing_content + "\n" + table_row
                else:
                    updated_content = existing_content + "\n" + table_row
            else:
                updated_content = existing_content + "\n" + content

            claude_md_path.write_text(updated_content, encoding='utf-8')
            print(f"CLAUDE.md 更新成功")
            return True

        except Exception as e:
            print(f"更新CLAUDE.md失败: {e}")
            return False

    def _update_doc_md(self, doc_path: str, commit_info: Dict[str, str],
                      changed_files: List[str]) -> bool:
        """更新其他文档"""
        try:
            doc_full_path = PROJECT_ROOT / doc_path
            existing_content = doc_full_path.read_text(encoding='utf-8')

            # 在文档末尾添加更新记录
            update_entry = f"\n\n## 更新记录\n\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            update_entry += f"- **提交**: {commit_info['short_hash']} - {commit_info['subject']}\n"
            update_entry += f"- **作者**: {commit_info['author']}\n"
            update_entry += f"- **变更文件**: {', '.join(changed_files[:5])}{'...' if len(changed_files) > 5 else ''}\n"

            updated_content = existing_content + update_entry
            doc_full_path.write_text(updated_content, encoding='utf-8')
            print(f"{doc_path} 更新成功")
            return True

        except Exception as e:
            print(f"更新 {doc_path} 失败: {e}")
            return False

    def _generate_update_content(self, commit_info: Dict[str, str],
                                changed_files: List[str], diff_summary: str) -> str:
        """生成更新内容"""
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

    def _parse_commit_content(self, content: str) -> Optional[Dict[str, str]]:
        """解析提交信息"""
        try:
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

            # 提取日期部分
            if 'date' in commit_info:
                date_str = commit_info['date']
                try:
                    parsed_date = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y %z')
                    commit_info['date'] = parsed_date.strftime('%Y-%m-%d')
                except:
                    commit_info['date'] = datetime.now().strftime('%Y-%m-%d')

            if 'files' not in commit_info:
                commit_info['files'] = '代码变更'

            return commit_info if commit_info else None
        except Exception as e:
            print(f"解析提交内容失败: {e}")
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'files': '代码变更'
            }


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
    """Main function - 多文档更新系统入口"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("=" * 60)
    print(f"多文档自动更新系统启动... ({timestamp})")
    print("=" * 60)

    # 初始化组件
    updater = MultiDocUpdater()
    protection = AntiLoopProtection()

    # 防循环检查
    if not protection.can_proceed():
        print("更新被跳过：防循环保护机制触发")
        return 0

    # 获取锁
    if not protection.acquire_lock():
        print("获取锁失败，跳过更新")
        return 0

    try:
        # 获取提交信息
        commit_info = get_commit_info()
        if not commit_info:
            print("无法获取提交信息，跳过更新")
            return 1

        print(f"提交: {commit_info['short_hash']} - {commit_info['subject']}")

        # 获取变更文件列表
        changed_files = get_changed_files()
        if changed_files:
            print(f"变更文件 ({len(changed_files)} 个): {', '.join(changed_files[:3])}{'...' if len(changed_files) > 3 else ''}")
        else:
            print("没有变更文件")

        # 获取diff摘要
        diff_summary = get_diff_summary()

        # 确定需要更新的文档
        docs_to_update = updater.get_docs_to_update(changed_files)
        print(f"确定更新 {len(docs_to_update)} 个文档: {docs_to_update}")

        if not docs_to_update:
            print("没有文档需要更新")
            protection.update_timestamp()
            return 0

        # 执行批量更新
        success_count = 0
        total_docs = len(docs_to_update)

        for i, doc_path in enumerate(docs_to_update, 1):
            print(f"\n[{i}/{total_docs}] 更新文档: {doc_path}")
            if updater.update_single_doc(doc_path, commit_info, changed_files):
                success_count += 1
                print(f"  ✅ 成功")
            else:
                print(f"  ❌ 失败")

        # 更新完成
        protection.update_timestamp()
        print("\n" + "=" * 60)
        print(f"多文档更新完成: {success_count}/{total_docs} 成功")
        print("=" * 60)

        if success_count == total_docs:
            print("✅ 所有文档更新成功")
            return 0
        elif success_count > 0:
            print("⚠️ 部分文档更新成功")
            return 0
        else:
            print("❌ 所有文档更新失败")
            return 1

    except Exception as e:
        print(f"更新过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # 释放锁
        protection.release_lock()


# 保留原有的辅助函数以确保兼容性
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


def check_anthropic_sdk() -> bool:
    """Check if anthropic SDK is available"""
    try:
        from anthropic import Anthropic
        return True
    except ImportError:
        return False


ANTHROPIC_SDK_AVAILABLE = check_anthropic_sdk()


if __name__ == "__main__":
    sys.exit(main())
