"""
状态解析器重构 - 单元测试
针对 STATE-PARSE-001 问题的专项测试
"""
import pytest
from autoBMAD.epic_automation.agents.state_agent import SimpleStoryParser
from autoBMAD.epic_automation.agents.state_agent import (
    CORE_STATUS_READY_FOR_DONE,
    CORE_STATUS_READY_FOR_REVIEW,
    CORE_STATUS_READY_FOR_DEVELOPMENT,
    CORE_STATUS_DRAFT,
    CORE_STATUS_IN_PROGRESS,
    CORE_STATUS_DONE,
    CORE_STATUS_FAILED,
)


@pytest.fixture
def parser():
    """创建 SimpleStoryParser 实例"""
    return SimpleStoryParser()


def test_parse_ready_for_done_basic(parser):
    """测试基本的 Ready for Done 状态"""
    content = """# Story 1.3
## Status
**Status**: Ready for Done

## Story
**As a** developer, I want to implement a comprehensive testing suite.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_parse_ready_for_done_with_decoration(parser):
    """测试带装饰的 Ready for Done 状态（括号内容）"""
    content = """# Story 1.3
## Status
**Status**: Ready for Done (approved by QA)

## Story
**As a** developer, I want to implement a comprehensive testing suite.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_parse_ready_for_done_with_emoji(parser):
    """测试带 emoji 的 Ready for Done 状态"""
    content = """# Story 1.3
## Status
**Status**: Ready for Done ✅

## Story
**As a** developer, I want to implement a comprehensive testing suite.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_ignore_qa_results_review_status(parser):
    """测试忽略 QA Results 中的历史 Review 状态"""
    content = """# Story 1.3
## Status
**Status**: Ready for Done

## Story
**As a** developer, I want to implement a comprehensive testing suite.

## QA Results
**QA Review #5**:
Status "Ready for Review" is now transitioned to "Ready for Done"
Previously in Ready for Review state, now approved.
"""
    result = parser._parse_status_with_regex(content)
    # 不应该被后面的 Review 覆盖
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_parse_review_without_done_interference(parser):
    """测试 Ready for Review 状态不被干扰"""
    content = """# Story 1.2
## Status
**Status**: Ready for Review

## Story
**As a** developer, I want to implement bubble sort algorithm.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_REVIEW, f"Expected {CORE_STATUS_READY_FOR_REVIEW}, got {result}"


def test_priority_done_over_review(parser):
    """测试 Done 优先级高于 Review（前 20 行内同时出现）"""
    content = """# Story 1.3
## Status
**Status**: Ready for Done

## Previous Status
Was: Ready for Review
Now: Ready for Done
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_parse_beyond_line_20_ignored(parser):
    """测试第 20 行后的状态被忽略"""
    lines = ["# Story 1.3", "## Status", "**Status**: Ready for Development"]
    lines.extend([""] * 20)  # 填充空行到第 23 行
    lines.append("Ready for Review")  # 第 24 行
    lines.append("Ready for Done")    # 第 25 行
    content = '\n'.join(lines)

    result = parser._parse_status_with_regex(content)
    # 只看前 20 行，应该是 Development
    assert result == CORE_STATUS_READY_FOR_DEVELOPMENT, f"Expected {CORE_STATUS_READY_FOR_DEVELOPMENT}, got {result}"


def test_parse_in_progress_status(parser):
    """测试 In Progress 状态"""
    content = """# Story 1.1
## Status
**Status**: In Progress

## Story
**As a** developer, I want to set up the project.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_IN_PROGRESS, f"Expected {CORE_STATUS_IN_PROGRESS}, got {result}"


def test_parse_draft_status(parser):
    """测试 Draft 状态"""
    content = """# Story 1.1
## Status
**Status**: Draft

## Story
**As a** developer, I want to set up the project.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_DRAFT, f"Expected {CORE_STATUS_DRAFT}, got {result}"


def test_parse_done_status(parser):
    """测试 Done 状态"""
    content = """# Story 1.1
## Status
**Status**: Done

## Story
**As a** developer, I want to set up the project.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_DONE, f"Expected {CORE_STATUS_DONE}, got {result}"


def test_parse_failed_status(parser):
    """测试 Failed 状态"""
    content = """# Story 1.1
## Status
**Status**: Failed

## Story
**As a** developer, I want to set up the project.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_FAILED, f"Expected {CORE_STATUS_FAILED}, got {result}"


def test_empty_content_returns_draft(parser):
    """测试空内容返回 Draft"""
    content = ""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_DRAFT, f"Expected {CORE_STATUS_DRAFT}, got {result}"


def test_no_status_line_returns_draft(parser):
    """测试没有 Status 行返回 Draft"""
    content = """# Story 1.1
## Story
This is a story without a status line.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_DRAFT, f"Expected {CORE_STATUS_DRAFT}, got {result}"


def test_case_insensitive_matching(parser):
    """测试大小写不敏感匹配"""
    content = """# Story 1.1
## Status
**Status**: ready for done

## Story
**As a** developer, I want to set up the project.
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_complex_story_with_long_content(parser):
    """测试包含大量内容的故事文档（前 20 行内）"""
    lines = [
        "# Story 1.3: Comprehensive Testing Suite",
        "",
        "## Status",
        "**Status**: Ready for Done",
        "",
        "## Story",
        "**As a** developer, I want to implement a comprehensive testing suite",
        "so that the project can be properly validated.",
        "",
        "## Acceptance Criteria",
        "- [ ] Unit tests for all core modules",
        "- [ ] Integration tests for the workflow",
        "- [ ] End-to-end tests for the complete process",
        "",
        "## Tasks",
        "- [ ] Set up pytest framework",
        "- [ ] Write unit tests",
        "- [ ] Set up CI/CD pipeline",
        "- [ ] Write integration tests",
        "",
        "## Dev Notes",
        "The testing strategy should cover all critical paths.",
        "",
        "## QA Results",
        "QA Review #5: Status 'Ready for Review' is now transitioned to 'Ready for Done'",
    ]
    content = '\n'.join(lines)

    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_status_line_on_exactly_line_20(parser):
    """测试 Status 行恰好在第 20 行"""
    lines = [""] * 19  # 前 19 行是空行
    lines.append("**Status**: Ready for Development")  # 第 20 行
    content = '\n'.join(lines)

    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DEVELOPMENT, f"Expected {CORE_STATUS_READY_FOR_DEVELOPMENT}, got {result}"


def test_status_line_on_line_21(parser):
    """测试 Status 行在第 21 行（被忽略）"""
    lines = [""] * 20  # 前 20 行是空行
    lines.append("**Status**: Ready for Development")  # 第 21 行
    content = '\n'.join(lines)

    result = parser._parse_status_with_regex(content)
    # 第 21 行被忽略，返回默认值 Draft
    assert result == CORE_STATUS_DRAFT, f"Expected {CORE_STATUS_DRAFT}, got {result}"


def test_multiple_status_in_first_20_lines(parser):
    """测试前 20 行内有多个状态（按优先级）"""
    content = """# Story
## Status
**Status**: Draft
## Previous Status
**Status**: Ready for Review
## Current Status
**Status**: Ready for Done
"""
    result = parser._parse_status_with_regex(content)
    # 按优先级，Ready for Done 应该被匹配
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


def test_status_with_multiple_spaces(parser):
    """测试状态行有多个空格的情况"""
    content = """# Story
## Status
**Status**:    Ready    for    Done

## Story
Test
"""
    result = parser._parse_status_with_regex(content)
    assert result == CORE_STATUS_READY_FOR_DONE, f"Expected {CORE_STATUS_READY_FOR_DONE}, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
