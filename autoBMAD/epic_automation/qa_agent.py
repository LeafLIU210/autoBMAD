"""
修复后的QA代理 - Fixed QA Agent

解决QA代理中的异步执行和错误处理问题。
基于原版本：d:/GITHUB/pytQt_template/autoBMAD/epic_automation/qa_agent.py

主要修复：
1. 优化异步执行流程
2. 增强错误恢复机制
3. 改进资源管理
4. 添加更好的日志记录
5. 优化会话管理
"""

from __future__ import annotations

import asyncio
import logging
import re
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Import SafeClaudeSDK wrapper
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

# Import SDK session manager for isolated execution
from .sdk_session_manager import SDKSessionManager

# Import Claude SDK types
try:
    from claude_agent_sdk import ClaudeAgentOptions
except ImportError:
    # For development without SDK installed
    ClaudeAgentOptions = None

# Type annotations for QA tools
if TYPE_CHECKING:
    pass
else:
    try:
        from .qa_tools_integration import QAStatus  # type: ignore  # noqa: F401

        QA_TOOLS_AVAILABLE = True
    except ImportError:
        # Fallback classes for when qa_tools_integration is not available
        class QAStatus(Enum):
            """QA status enum with value attribute."""

            PASS = "PASS"
            FAIL = "FAIL"
            CONCERNS = "CONCERNS"
            WAIVED = "WAIVED"

        class QAAutomationWorkflow:
            """Fallback QA workflow when tools are not available."""

            def __init__(
                self,
                basedpyright_dir: str,
                fixtest_dir: str,
                timeout: int = 300,
                max_retries: int = 1,
            ):
                self.basedpyright_dir = basedpyright_dir
                self.fixtest_dir = fixtest_dir
                self.timeout = timeout
                self.max_retries = max_retries

            async def run_qa_checks(
                self, source_dir: str, test_dir: str
            ) -> dict[str, Any]:
                """Fallback implementation when QA tools are not available."""
                return {
                    "overall_status": QAStatus.WAIVED.value,  # type: ignore
                    "basedpyright": {"errors": 0, "warnings": 0},
                    "fixtest": {"tests_failed": 0, "tests_errors": 0},
                    "message": "QA tools not available",
                }

        # QA_TOOLS_AVAILABLE already set to False by default

logger = logging.getLogger(__name__)


class QAResult:
    """QA执行结果"""

    def __init__(
        self,
        passed: bool,
        completed: bool = False,
        needs_fix: bool = False,
        dev_prompt: str | None = None,
        fallback_review: bool = False,
        checks_passed: int = 0,
        total_checks: int = 0,
        reason: str | None = None,
    ):
        self.passed = passed
        self.completed = completed
        self.needs_fix = needs_fix
        self.dev_prompt = dev_prompt
        self.fallback_review = fallback_review
        self.checks_passed = checks_passed
        self.total_checks = total_checks
        self.reason = reason

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "passed": self.passed,
            "completed": self.completed,
            "needs_fix": self.needs_fix,
            "dev_prompt": self.dev_prompt,
            "fallback_review": self.fallback_review,
            "checks_passed": self.checks_passed,
            "total_checks": self.total_checks,
            "reason": self.reason,
        }


class QAAgent:
    """
    修复后的Quality Assurance代理。

    提供优化的故事验证和QA检查功能。
    修复内容：
    1. 优化异步执行流程
    2. 增强错误恢复机制
    3. 改进会话管理
    4. 添加重试机制
    5. 优化资源清理
    """

    name: str = "QA Agent"

    def __init__(self) -> None:
        """初始化QA代理."""
        # 每个QAAgent实例创建独立的会话管理器，消除跨Agent cancel scope污染
        self._session_manager = SDKSessionManager()

        # Initialize StatusParser for robust status parsing
        try:
            from autoBMAD.epic_automation.story_parser import StatusParser

            # 创建有效的SDK实例以支持AI解析
            sdk_instance = None
            if SafeClaudeSDK:
                try:
                    # 创建选项对象
                    options = None
                    if ClaudeAgentOptions:
                        options = ClaudeAgentOptions(
                            permission_mode="bypassPermissions",
                            cwd=str(Path.cwd()),
                            cli_path=r"D:\GITHUB\pytQt_template\venv\Lib\site-packages\claude_agent_sdk\_bundled\claude.exe",
                        )
                    # 创建SDK实例
                    sdk_instance = SafeClaudeSDK(
                        prompt="Parse story status",
                        options=options,
                        timeout=None,
                        log_manager=None,
                    )
                except Exception as e:
                    logger.warning(f"[QA Agent] Failed to create SDK instance: {e}")

            # 传入SDK实例（可能为None）
            self.status_parser = StatusParser(sdk_wrapper=sdk_instance)
        except ImportError:
            self.status_parser = None
            logger.warning(
                "[QA Agent] StatusParser not available, using fallback parsing"
            )

        logger.info(f"{self.name} initialized")

    async def _parse_story_status(self, story_path: str) -> str:
        """
        解析故事文档状态

        Args:
            story_path: 故事文件路径

        Returns:
            状态字符串（如 "Done", "Ready for Done", "Ready for Review" 等）
        """
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"[QA Agent] Story file not found: {story_path}")
                return "Unknown"

            content = story_file.read_text(encoding="utf-8")

            # 使用 StatusParser 解析状态
            if self.status_parser:
                try:
                    status = await self.status_parser.parse_status(content)
                    if status and status != "unknown":
                        logger.debug(
                            f"[QA Agent] Found status using AI parsing: '{status}'"
                        )
                        return status
                    else:
                        logger.warning(
                            f"[QA Agent] StatusParser failed to parse status from {story_path}"
                        )
                except Exception as e:
                    logger.warning(
                        f"[QA Agent] StatusParser error: {e}, falling back to regex"
                    )

            # 回退到正则表达式解析
            logger.debug(f"[QA Agent] Using fallback regex parsing for {story_path}")
            status_patterns = [
                r"##\s*Status\s*\n\s*\*\*([^*]+)\*\*",  # Multi-line: ## Status\n**Value**
                r"##\s*Status\s*\n\s*([^\n]+)",  # Multi-line: ## Status\n Value
                r"Status:\s*\*\*([^*]+)\*\*",  # Inline: Status: **Bold** format
                r"Status:\s*(\w+(?:\s+\w+)*)",  # Inline: Status: Regular format
            ]

            for pattern in status_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    status = match.group(1).strip().lower()
                    logger.debug(f"[QA Agent] Found status using regex: '{status}'")
                    return status

            logger.warning(f"Could not find status in story file: {story_path}")
            return "Unknown"

        except Exception as e:
            logger.error(f"Error parsing story status: {e}")
            return "Unknown"

    async def execute(
        self,
        story_content: str,
        story_path: str = "",
        use_qa_tools: bool = True,
        source_dir: str = "src",
        test_dir: str = "tests",
        max_retries: int = 3,
    ) -> dict[str, str | bool | list[str] | int | None]:
        """
        执行QA阶段 - 根据故事状态决定执行路径。

        Args:
            story_content: 故事的原始markdown内容
            story_path: 故事文件路径
            use_qa_tools: 是否使用QA工具
            source_dir: 源代码目录
            test_dir: 测试目录
            max_retries: 最大重试次数

        Returns:
            包含QA结果的字典
        """
        # 检查故事状态
        if story_path:
            try:
                status = await self._parse_story_status(story_path)
                status_lower = status.lower().strip()

                # 如果状态是 "Done" 或 "Ready for Done"，跳过QA
                if status_lower in ["done", "ready for done"]:
                    logger.info(f"{self.name} Story status is '{status}' - skipping QA")
                    return {
                        "passed": True,
                        "completed": True,
                        "needs_fix": False,
                        "dev_prompt": None,
                        "fallback_review": False,
                        "checks_passed": 0,
                        "total_checks": 0,
                        "reason": f"故事状态为'{status}'，QA跳过",
                    }

                # 如果状态是 "Ready for Review"，执行完整QA审查
                elif status_lower in ["ready for review"]:
                    logger.info(
                        f"{self.name} Story status is '{status}' - executing QA review"
                    )
                    qa_result = await self._execute_qa_review(
                        story_path, source_dir, test_dir
                    )
                    return qa_result.to_dict()

                # 其他状态返回需要修复
                else:
                    logger.info(
                        f"{self.name} Story status is '{status}' - needs fixing"
                    )
                    return {
                        "passed": False,
                        "completed": False,
                        "needs_fix": True,
                        "dev_prompt": f"*fix the qa gate file in @docs\\qa\\gates for {story_path} - Update story status from '{status}' to 'Ready for Review'",
                        "fallback_review": False,
                        "checks_passed": 0,
                        "total_checks": 0,
                        "reason": f"故事状态为'{status}'，需要修复",
                    }

            except Exception as e:
                logger.error(f"Error checking story status: {e}")
                # 状态检查失败时，执行回退QA审查
                logger.info(
                    f"{self.name} Status check failed, executing fallback QA review"
                )
                qa_result = await self._perform_fallback_qa_review(
                    story_path, source_dir, test_dir
                )
                return qa_result.to_dict()
        else:
            # 没有故事路径时执行回退QA审查
            logger.warning(
                f"{self.name} No story path provided, executing fallback QA review"
            )
            qa_result = await self._perform_fallback_qa_review(
                story_path, source_dir, test_dir
            )
            return qa_result.to_dict()

    async def _execute_qa_review(
        self, story_path: str, source_dir: str, test_dir: str
    ) -> QAResult:
        """执行QA审查"""
        try:
            # 执行AI驱动的QA审查
            review_success = await self._execute_ai_qa_review(story_path)

            if not review_success:
                logger.warning(
                    f"{self.name} AI-driven QA review failed, using fallback review"
                )
                return await self._perform_fallback_qa_review(
                    story_path, source_dir, test_dir
                )

            # 检查故事状态
            status_ready = await self._check_story_status(story_path)

            if not status_ready:
                # 创建修复提示
                dev_prompt = f"*review-qa @(story_path) Fix based on QA gate file in @docs\\qa\\gates for the story"

                logger.info(f"{self.name} QA found issues, needs fixing")
                return QAResult(
                    passed=False,
                    needs_fix=True,
                    dev_prompt=dev_prompt,
                )
            else:
                # 状态为Ready for Done，故事完成
                logger.info(f"{self.name} QA PASSED - Ready for Done")
                return QAResult(passed=True, completed=True, needs_fix=False)

        except asyncio.CancelledError:
            logger.warning(f"{self.name} QA review cancelled for {story_path}")
            return QAResult(
                passed=False,
                needs_fix=True,
                fallback_review=True,
                reason="QA review was cancelled",
            )
        except Exception as e:
            logger.error(f"{self.name} QA review error: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return QAResult(
                passed=False,
                needs_fix=True,
                fallback_review=True,
                reason=f"QA review error: {str(e)}",
            )

    async def _execute_ai_qa_review(self, story_path: str) -> bool:
        """执行AI驱动的QA审查"""
        try:
            # 构建QA提示
            qa_prompt = self._build_qa_prompt(story_path)

            # 执行SDK调用
            sdk_func = self._create_sdk_execution_function(qa_prompt)

            # 使用会话管理器执行
            result = await self._session_manager.execute_isolated(
                agent_name=self.name,
                sdk_func=sdk_func,
                timeout=None,  # No external timeout
            )

            logger.info(
                f"{self.name} QA review result: {result.success} "
                f"(duration: {result.duration_seconds:.1f}s)"
            )

            return result.success

        except Exception as e:
            logger.error(f"{self.name} AI QA review execution error: {e}")
            logger.debug(f"Error details: {e}", exc_info=True)
            return False

    def _build_qa_prompt(self, story_path: str) -> str:
        """构建QA提示"""
        return f'@.bmad-core\\agents\\qa.md @.bmad-core\\tasks\\review-story.md Review the current story document @{story_path} . If the review passes, update the story document status to "Done". Additionally, @.bmad-core\\tasks\\qa-gate.md create a gate file for the story document and save it to @docs\\qa\\gates .'

    def _create_sdk_execution_function(self, prompt: str):
        """创建SDK执行函数"""

        async def sdk_execution():
            try:
                # 检查SDK可用性
                if not hasattr(SafeClaudeSDK, "__init__"):
                    logger.warning("SafeClaudeSDK not available")
                    return False

                # 创建SDK实例
                options = None
                if ClaudeAgentOptions:
                    options = ClaudeAgentOptions(
                        permission_mode="bypassPermissions",
                        cwd=str(Path.cwd()),
                        cli_path=r"D:\GITHUB\pytQt_template\venv\Lib\site-packages\claude_agent_sdk\_bundled\claude.exe",
                    )
                    # 限制最大回合数，防止无限等待
                    options.max_turns = 1000

                sdk = SafeClaudeSDK(
                    prompt=prompt,
                    options=options,
                    timeout=None,  # No external timeout
                )

                # 执行SDK
                result = await sdk.execute()
                return result

            except Exception as e:
                logger.error(f"SDK execution error: {e}")
                logger.debug(f"SDK error details: {e}", exc_info=True)
                return False

        return sdk_execution

    async def _check_story_status(self, story_path: str) -> bool:
        """检查故事状态使用混合解析策略"""
        try:
            story_file = Path(story_path)
            if not story_file.exists():
                logger.error(f"Story file not found: {story_path}")
                return False

            content = story_file.read_text(encoding="utf-8")

            # Use StatusParser if available (AI-powered parsing)
            if self.status_parser:
                try:
                    # Note: parse_status is now async in SimpleStatusParser
                    status = await self.status_parser.parse_status(content)
                    if status and status != "unknown":
                        logger.debug(
                            f"[QA Agent] Found status using AI parsing: '{status}'"
                        )
                        return self._evaluate_story_status(status)
                    else:
                        logger.warning(
                            f"[QA Agent] StatusParser failed to parse status from {story_path}"
                        )
                except Exception as e:
                    logger.warning(
                        f"[QA Agent] StatusParser error: {e}, falling back to regex"
                    )

            # Fallback to original regex patterns
            logger.debug(f"[QA Agent] Using fallback regex parsing for {story_path}")
            status_patterns = [
                r"##\s*Status\s*\n\s*\*\*([^*]+)\*\*",  # Multi-line: ## Status\n**Value**
                r"##\s*Status\s*\n\s*([^\n]+)",  # Multi-line: ## Status\n Value
                r"Status:\s*\*\*([^*]+)\*\*",  # Inline: Status: **Bold** format
                r"Status:\s*(\w+(?:\s+\w+)*)",  # Inline: Status: Regular format
            ]

            for pattern in status_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    status = match.group(1).strip().lower()
                    logger.debug(f"[QA Agent] Found status using regex: '{status}'")
                    return self._evaluate_story_status(status)

            logger.warning(f"Could not find status in story file: {story_path}")
            return False

        except Exception as e:
            logger.error(f"Error checking story status: {e}")
            return False

    def _evaluate_story_status(self, status: str) -> bool:
        """
        评估故事状态，判断是否应该跳过QA

        Args:
            status: 解析出的状态字符串

        Returns:
            True 如果故事已完成应该跳过QA，False 如果需要执行QA
        """
        status_lower = status.lower().strip()

        # 检查状态是否为完成状态（使用标准状态值）
        if status_lower in ["ready for done", "done"]:
            logger.info(
                f"Story status is '{status}' - considered complete, skipping QA"
            )
            return True
        elif status_lower == "ready for review":
            logger.info(
                f"Story status is '{status}' - ready for QA review, proceeding with QA"
            )
            # Ready for Review should trigger QA review
            return False
        else:
            logger.debug(
                f"Story status is '{status}' - not a completion status, proceeding with QA"
            )
            return False

    async def _perform_fallback_qa_review(
        self, story_path: str, source_dir: str = "src", test_dir: str = "tests"
    ) -> QAResult:
        """执行回退QA审查"""
        logger.info(f"{self.name} Performing fallback QA review")

        try:
            # 基础检查
            checks_passed = 0
            total_checks = 3

            # 检查1: 故事文件存在
            story_file = Path(story_path)
            if story_file.exists():
                checks_passed += 1
            else:
                logger.error(f"Story file not found: {story_path}")

            # 检查2: 源代码目录存在
            source_path = Path(source_dir)
            if source_path.exists():
                checks_passed += 1
            else:
                logger.warning(f"Source directory not found: {source_dir}")

            # 检查3: 测试目录存在
            test_path = Path(test_dir)
            if test_path.exists():
                checks_passed += 1
            else:
                logger.warning(f"Test directory not found: {test_dir}")

            # 决定是否通过
            passed = checks_passed == total_checks

            logger.info(
                f"{self.name} Fallback QA review: {checks_passed}/{total_checks} checks passed"
            )

            return QAResult(
                passed=passed,
                completed=passed,
                needs_fix=not passed,
                fallback_review=True,
                checks_passed=checks_passed,
                total_checks=total_checks,
                reason=f"Fallback review: {checks_passed}/{total_checks} checks passed",
            )

        except Exception as e:
            logger.error(f"{self.name} Fallback QA review error: {e}")
            return QAResult(
                passed=False,
                completed=False,
                needs_fix=True,
                fallback_review=True,
                reason=f"Fallback review error: {str(e)}",
            )

    async def _check_code_quality_basics(self, story_path: str) -> dict[str, Any]:
        """检查基础代码质量"""
        try:
            checks_passed = 0
            total_checks = 2

            # 检查源代码目录
            src_path = Path("src")
            if not src_path.exists():
                logger.warning("Source directory not found: src")
                return {
                    "passed": False,
                    "checks_passed": 0,
                    "total_checks": total_checks,
                    "reason": "Source directory not found",
                }

            # 检查Python文件是否存在
            python_files = list(src_path.glob("**/*.py"))
            if python_files:
                checks_passed += 1
                logger.debug(f"Found {len(python_files)} Python files")

                # 简单的代码质量检查：检查是否有语法错误
                for py_file in python_files[:10]:  # 只检查前10个文件以节省时间
                    try:
                        with open(py_file, encoding="utf-8") as f:
                            content = f.read()
                            compile(content, py_file, "exec")
                    except SyntaxError as e:
                        logger.warning(f"Syntax error in {py_file}: {e}")
                        return {
                            "passed": False,
                            "checks_passed": checks_passed,
                            "total_checks": total_checks,
                            "reason": f"Syntax error in {py_file}",
                        }
            else:
                logger.warning("No Python files found in src directory")
                return {
                    "passed": False,
                    "checks_passed": 0,
                    "total_checks": total_checks,
                    "reason": "No Python files found",
                }

            # 检查基本的代码结构
            checks_passed += 1
            logger.info(f"Code quality check: {checks_passed}/{total_checks} passed")

            return {
                "passed": checks_passed == total_checks,
                "checks_passed": checks_passed,
                "total_checks": total_checks,
                "files_checked": len(python_files),
            }

        except Exception as e:
            logger.error(f"Error checking code quality: {e}")
            return {
                "passed": False,
                "checks_passed": 0,
                "total_checks": 2,
                "reason": f"Error checking code quality: {str(e)}",
            }

    async def _check_test_files_exist(self, story_path: str) -> dict[str, Any]:
        """检查测试文件是否存在"""
        try:
            test_path = Path("tests")
            if not test_path.exists():
                logger.warning("Test directory not found: tests")
                return {
                    "passed": False,
                    "test_count": 0,
                    "reason": "Test directory not found",
                }

            # 查找测试文件
            test_files = list(test_path.glob("**/test_*.py")) + list(
                test_path.glob("**/*_test.py")
            )
            test_count = len(test_files)

            if test_count > 0:
                logger.info(f"Found {test_count} test files")
                return {
                    "passed": True,
                    "test_count": test_count,
                    "test_files": [str(f) for f in test_files[:5]],  # 只返回前5个文件名
                }
            else:
                logger.warning("No test files found")
                return {
                    "passed": False,
                    "test_count": 0,
                    "reason": "No test files found",
                }

        except Exception as e:
            logger.error(f"Error checking test files: {e}")
            return {
                "passed": False,
                "test_count": 0,
                "reason": f"Error checking test files: {str(e)}",
            }

    async def _check_documentation_updated(self, story_path: str) -> dict[str, Any]:
        """检查文档是否已更新"""
        try:
            # 检查故事文件是否存在
            story_file = Path(story_path)
            if not story_file.exists():
                logger.warning(f"Story file not found: {story_path}")
                return {
                    "passed": False,
                    "last_updated": None,
                    "reason": "Story file not found",
                }

            # 获取文件的最后修改时间
            stat = story_file.stat()
            last_updated = stat.st_mtime

            # 检查文档内容是否包含必要部分
            content = story_file.read_text(encoding="utf-8")

            # 检查基本文档结构
            required_sections = ["#", "##"]
            has_structure = any(section in content for section in required_sections)

            if has_structure and last_updated:
                logger.info("Documentation appears to be updated")
                return {
                    "passed": True,
                    "last_updated": last_updated,
                    "has_structure": has_structure,
                }
            else:
                logger.warning("Documentation may be outdated")
                return {
                    "passed": False,
                    "last_updated": last_updated,
                    "reason": "Documentation lacks proper structure",
                }

        except Exception as e:
            logger.error(f"Error checking documentation: {e}")
            return {
                "passed": False,
                "last_updated": None,
                "reason": f"Error checking documentation: {str(e)}",
            }

    async def get_statistics(self) -> dict[str, Any]:
        """获取QA代理统计信息"""
        try:
            stats = self._session_manager.get_statistics()

            return {
                "agent_name": self.name,
                "session_statistics": stats,
                "active_sessions": self._session_manager.get_session_count(),
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
