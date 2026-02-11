#!/usr/bin/env python3
"""
Multi-Document Auto Update Script with Claude SDK Integration

This script automatically updates CLAUDE.md and related documents in claude_docs/
directory after git commits. It uses Claude Agent SDK for intelligent updates.

Features:
- Claude SDK intelligent analysis
- Multi-document updates
- Anti-loop protection mechanisms
- Smart document mapping based on file changes
- Batch processing for improved performance
- Real-time file logging
"""

import sys
import os
import subprocess
import re
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from dataclasses import dataclass

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Required packages check
REQUIRED_PACKAGES = ["anthropic"]

# 日志文件配置
LOG_FILE = PROJECT_ROOT / 'scripts' / 'post-commit.log'


def log_to_file(message: str, level: str = "INFO"):
    """同时输出到控制台和日志文件（实时写入）"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] [{level}] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted + '\n')
            f.flush()
    except Exception:
        pass  # 日志写入失败不影响主流程


def check_dependencies():
    """Check for required dependencies"""
    missing = []
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)

    if missing:
        log_to_file(f"Error: Missing required packages: {', '.join(missing)}", "ERROR")
        log_to_file(f"Please run: pip install {' '.join(missing)}", "ERROR")
        sys.exit(1)


check_dependencies()

# Import Anthropic SDK after verification
from anthropic import Anthropic


@dataclass
class UpdateConfig:
    """Configuration class"""
    lock_file: Path = PROJECT_ROOT / '.multi_doc_update.lock'
    timestamp_file: Path = PROJECT_ROOT / '.last_update.timestamp'
    env_var: str = 'MULTI_DOC_UPDATING'
    max_frequency: int = 300  # 5 minutes max frequency
    log_file: Path = PROJECT_ROOT / 'scripts' / 'multi_doc_update.log'


@dataclass
class CommitInfo:
    """Git commit information data class"""
    full_hash: str
    short_hash: str
    subject: str
    author: str
    date: str
    files: List[str]
    diff_summary: str


class ClaudeSDKManager:
    """Claude SDK async manager for intelligent document updates"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=self.api_key)

    async def analyze_commit_async(self, commit_info: CommitInfo) -> Dict[str, Any]:
        """Async analysis of commit content using Claude SDK"""
        prompt = self._build_analysis_prompt(commit_info)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_ai_response(response)
        except Exception as e:
            print(f"Claude SDK error: {e}")
            return {"success": False, "analysis": "", "error": str(e)}

    def _build_analysis_prompt(self, commit_info: CommitInfo) -> str:
        """Build analysis prompt from commit info"""
        files_str = "\n".join([f"- {f}" for f in commit_info.files[:10]])
        if len(commit_info.files) > 10:
            files_str += f"\n... and {len(commit_info.files) - 10} more files"

        return f"""Analyze this git commit and provide a concise summary suitable for documentation:

**Commit Hash**: {commit_info.short_hash}
**Subject**: {commit_info.subject}
**Author**: {commit_info.author}
**Date**: {commit_info.date}

**Changed Files**:
{files_str}

**Diff Summary**:
{commit_info.diff_summary}

Provide a brief (2-3 sentence) summary of what changed and why it matters for documentation purposes."""

    def _parse_ai_response(self, response: Any) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            return {"success": True, "analysis": text.strip()}
        except Exception as e:
            return {"success": False, "analysis": "", "error": str(e)}

    def sync_analyze(self, commit_info: CommitInfo) -> Dict[str, Any]:
        """Synchronous wrapper for analyze_commit_async"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.analyze_commit_async(commit_info))
                    return future.result()
            else:
                return asyncio.run(self.analyze_commit_async(commit_info))
        except RuntimeError:
            return asyncio.run(self.analyze_commit_async(commit_info))


class AntiLoopProtection:
    """Anti-loop protection mechanism"""

    def __init__(self, config: UpdateConfig | None = None):
        self.config = config or UpdateConfig()
        self._acquired_lock: bool = False

    def can_proceed(self) -> bool:
        """Check if update can proceed"""
        log_to_file("Checking anti-loop protection...")

        # Check lock file
        if self.config.lock_file.exists():
            log_to_file(f"Update skipped: Lock file exists {self.config.lock_file}", "WARNING")
            return False

        # Check environment variable
        if os.environ.get(self.config.env_var) == '1':
            log_to_file(f"Update skipped: Environment variable {self.config.env_var} is set", "WARNING")
            return False

        # Check time window
        if self._is_too_frequent():
            log_to_file(f"Update skipped: Update frequency too high (executed within 5 minutes)", "WARNING")
            return False

        log_to_file("Anti-loop protection check passed")
        return True

    def _is_too_frequent(self) -> bool:
        """Check if update frequency is too high"""
        if not self.config.timestamp_file.exists():
            return False

        try:
            last_update = float(self.config.timestamp_file.read_text().strip())
            time_since_last = time.time() - last_update
            if time_since_last < self.config.max_frequency:
                log_to_file(f"Time since last update: {time_since_last:.1f}s, threshold: {self.config.max_frequency}s", "WARNING")
                return True
        except Exception as e:
            log_to_file(f"Failed to read timestamp file: {e}", "ERROR")

        return False

    def acquire_lock(self):
        """Acquire lock"""
        if self.config.lock_file.exists():
            return False

        try:
            with open(self.config.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            self._acquired_lock = True
            return True
        except Exception as e:
            log_to_file(f"Failed to acquire lock: {e}", "ERROR")
            return False

    def release_lock(self):
        """Release lock"""
        if self._acquired_lock and self.config.lock_file.exists():
            try:
                self.config.lock_file.unlink()
            except Exception as e:
                log_to_file(f"Failed to release lock: {e}", "ERROR")
        self._acquired_lock = False

    def update_timestamp(self):
        """Update timestamp"""
        try:
            self.config.timestamp_file.write_text(str(time.time()))
        except Exception as e:
            log_to_file(f"Failed to update timestamp: {e}", "ERROR")


class MultiDocUpdater:
    """Multi-document update controller"""

    def __init__(self):
        # Target documents list
        self.target_docs: List[str] = [
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

        # Build mapping from file changes to document updates
        self.update_mapping: Dict[str, List[str]] = {
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
            'CLAUDE.md': ['CLAUDE.md', 'claude_docs/quick_reference.md'],  # Update quick reference when CLAUDE.md changes
        }

    def get_docs_to_update(self, changed_files: List[str]) -> List[str]:
        """Determine which documents need to be updated based on changed files"""
        docs_to_update: Set[str] = set()

        # Always update CLAUDE.md
        docs_to_update.add('CLAUDE.md')

        for file_path in changed_files:
            file_path = file_path.strip()
            if not file_path:
                continue

            log_to_file(f"Analyzing changed file: {file_path}")

            # Check exact match
            if file_path in self.update_mapping:
                docs_to_update.update(self.update_mapping[file_path])
                log_to_file(f"  -> Exact match, update: {self.update_mapping[file_path]}")
                continue

            # Check prefix match
            for pattern, docs in self.update_mapping.items():
                if pattern.endswith('/') and file_path.startswith(pattern):
                    docs_to_update.update(docs)
                    log_to_file(f"  -> Prefix match '{pattern}', update: {docs}")
                    break
                elif not pattern.endswith('/') and pattern in file_path:
                    docs_to_update.update(docs)
                    log_to_file(f"  -> Content match '{pattern}', update: {docs}")
                    break

        # Filter out non-existent documents
        existing_docs: List[str] = []
        for doc in docs_to_update:
            doc_full_path = PROJECT_ROOT / doc
            if doc_full_path.exists():
                existing_docs.append(doc)
            else:
                log_to_file(f"Warning: Document does not exist {doc}", "WARNING")

        return sorted(existing_docs)

    def update_single_doc(self, doc_path: str, commit_info: Dict[str, str],
                         changed_files: List[str]) -> bool:
        """Update a single document"""
        try:
            doc_full_path = PROJECT_ROOT / doc_path
            log_to_file(f"Updating document: {doc_path}")

            if not doc_full_path.exists():
                log_to_file(f"Document does not exist: {doc_path}", "WARNING")
                return False

            if doc_path == 'CLAUDE.md':
                return self._update_claude_md(commit_info, changed_files)
            else:
                return self._update_doc_md(doc_path, commit_info, changed_files)

        except Exception as e:
            log_to_file(f"Failed to update document {doc_path}: {e}", "ERROR")
            return False

    def _update_claude_md(self, commit_info: Dict[str, str],
                         changed_files: List[str]) -> bool:
        """Update CLAUDE.md (reuse existing logic)"""
        try:
            # Generate update content
            content = self._generate_update_content(commit_info, changed_files, "")

            claude_md_path = PROJECT_ROOT / 'CLAUDE.md'
            if not claude_md_path.exists():
                return False

            existing_content = claude_md_path.read_text(encoding='utf-8')

            # Update timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d')
            date_pattern = r'\*\*最后更新\*\*: \d{4}-\d{2}-\d{2}'
            if re.search(date_pattern, existing_content):
                existing_content = re.sub(
                    date_pattern,
                    f"**最后更新**: {timestamp}",
                    existing_content
                )

            # Parse and insert new table row
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
                content_value = content if content is not None else ""
                updated_content = existing_content + "\n" + content_value

            claude_md_path.write_text(updated_content, encoding='utf-8')
            log_to_file(f"CLAUDE.md updated successfully")
            return True

        except Exception as e:
            log_to_file(f"Failed to update CLAUDE.md: {e}", "ERROR")
            return False

    def _update_doc_md(self, doc_path: str, commit_info: Dict[str, str],
                      changed_files: List[str]) -> bool:
        """Update other documents"""
        try:
            doc_full_path = PROJECT_ROOT / doc_path
            existing_content = doc_full_path.read_text(encoding='utf-8')

            # Add update record at the end of the document
            update_entry = f"\n\n## Update Records\n\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            update_entry += f"- **Commit**: {commit_info['short_hash']} - {commit_info['subject']}\n"
            update_entry += f"- **Author**: {commit_info['author']}\n"
            update_entry += f"- **Changed Files**: {', '.join(changed_files[:5])}{'...' if len(changed_files) > 5 else ''}\n"

            updated_content = existing_content + update_entry
            doc_full_path.write_text(updated_content, encoding='utf-8')
            log_to_file(f"{doc_path} updated successfully")
            return True

        except Exception as e:
            log_to_file(f"Failed to update {doc_path}: {e}", "ERROR")
            return False

    def _generate_update_content(self, commit_info: Dict[str, str],
                                changed_files: List[str], diff_summary: str) -> str | None:
        """Generate update content"""
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

    def _parse_commit_content(self, content: str | None) -> Dict[str, str] | None:
        """Parse commit information"""
        try:
            if content is None or content.strip() == "":
                return {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'files': 'Code changes'
                }

            lines = content.strip().split('\n')
            commit_info: Dict[str, str] = {}

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

            # Extract date part
            if 'date' in commit_info:
                date_str: str = commit_info['date']
                try:
                    parsed_date = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y %z')
                    commit_info['date'] = parsed_date.strftime('%Y-%m-%d')
                except Exception:
                    commit_info['date'] = datetime.now().strftime('%Y-%m-%d')

            if 'files' not in commit_info:
                commit_info['files'] = 'Code changes'

            return commit_info if commit_info else None
        except Exception as e:
            log_to_file(f"Failed to parse commit content: {e}", "ERROR")
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'files': 'Code changes'
            }


def get_commit_info() -> Dict[str, str] | None:
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
        log_to_file(f"Error getting commit info: {e}", "ERROR")

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
        log_to_file(f"Error getting changed files: {e}", "ERROR")

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
        log_to_file(f"Error getting diff summary: {e}", "ERROR")

    return ""


def main() -> int:
    """Main function - Multi-document update system entry"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_to_file("=" * 60)
    log_to_file(f"Multi-document auto-update system started... ({timestamp})")
    log_to_file("=" * 60)

    # Initialize components
    updater = MultiDocUpdater()
    protection = AntiLoopProtection()

    # Anti-loop check
    if not protection.can_proceed():
        log_to_file("Update skipped: Anti-loop protection triggered")
        return 0

    # Acquire lock
    if not protection.acquire_lock():
        log_to_file("Failed to acquire lock, skipping update", "ERROR")
        return 0

    try:
        # Get commit info
        commit_info_dict = get_commit_info()
        if not commit_info_dict:
            log_to_file("Cannot get commit info, skipping update", "ERROR")
            return 1

        log_to_file(f"Commit: {commit_info_dict['short_hash']} - {commit_info_dict['subject']}")

        # Get changed files list
        changed_files = get_changed_files()
        if changed_files:
            log_to_file(f"Changed files ({len(changed_files)}): {', '.join(changed_files[:3])}{'...' if len(changed_files) > 3 else ''}")
        else:
            log_to_file("No changed files")

        # Get diff summary
        diff_summary = get_diff_summary()

        # Initialize Claude SDK manager if API key is available
        sdk_manager: ClaudeSDKManager | None = None
        ai_analysis: Dict[str, Any] | None = None
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                sdk_manager = ClaudeSDKManager()
                log_to_file("Claude SDK initialized successfully")
            except ValueError as e:
                log_to_file(f"Claude SDK initialization skipped: {e}", "WARNING")
        else:
            log_to_file("ANTHROPIC_API_KEY not set, using template-based updates")

        # Perform AI analysis if SDK is available
        if sdk_manager:
            commit_info_obj = CommitInfo(
                full_hash=commit_info_dict['hash'],
                short_hash=commit_info_dict['short_hash'],
                subject=commit_info_dict['subject'],
                author=commit_info_dict['author'],
                date=commit_info_dict['date'],
                files=changed_files,
                diff_summary=diff_summary
            )
            log_to_file("Analyzing commit with Claude SDK...")
            ai_analysis = sdk_manager.sync_analyze(commit_info_obj)
            if ai_analysis.get("success"):
                analysis_text = ai_analysis.get('analysis', '')
                if analysis_text:
                    log_to_file(f"AI Analysis: {analysis_text[:200]}...")
            else:
                log_to_file(f"AI Analysis failed: {ai_analysis.get('error', 'Unknown error')}", "WARNING")

        # Determine which documents to update
        docs_to_update = updater.get_docs_to_update(changed_files)
        log_to_file(f"Determined to update {len(docs_to_update)} documents: {docs_to_update}")

        if not docs_to_update:
            log_to_file("No documents need updating")
            protection.update_timestamp()
            return 0

        # Execute batch update
        success_count = 0
        total_docs = len(docs_to_update)

        for i, doc_path in enumerate(docs_to_update, 1):
            log_to_file(f"\n[{i}/{total_docs}] Updating document: {doc_path}")
            if updater.update_single_doc(doc_path, commit_info_dict, changed_files):
                success_count += 1
                log_to_file(f"  SUCCESS")
            else:
                log_to_file(f"  FAILED", "ERROR")

        # Update completion
        protection.update_timestamp()
        log_to_file("\n" + "=" * 60)
        log_to_file(f"Multi-document update completed: {success_count}/{total_docs} successful")
        log_to_file("=" * 60)

        if success_count == total_docs:
            log_to_file("All documents updated successfully")
            return 0
        elif success_count > 0:
            log_to_file("Partial documents updated successfully")
            return 0
        else:
            log_to_file("All documents update failed", "ERROR")
            return 1

    except Exception as e:
        log_to_file(f"Error during update process: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Release lock
        protection.release_lock()


if __name__ == "__main__":
    sys.exit(main())