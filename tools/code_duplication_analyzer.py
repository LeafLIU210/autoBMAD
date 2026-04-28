"""
DocuSwarm 代码重复分析工具
用于检测和分析 TD-001: Checkpointer 创建代码重复问题

Usage:
    python tools/code_duplication_analyzer.py --target autoBMAD/docuswarm/pipeline/orchestrator.py
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CodeBlock:
    """Represents a block of code that may be duplicated."""
    content: str
    start_line: int
    end_line: int
    function_name: str | None = None
    context: str = ""  # e.g., "start_pipeline", "resume_pipeline"
    hash: str = field(default="")
    
    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.md5(self.content.strip().encode()).hexdigest()[:12]


@dataclass
class DuplicationFinding:
    """Represents a duplication finding."""
    severity: str  # "high", "medium", "low"
    pattern_name: str
    locations: list[tuple[str, int, int]]  # (function, start_line, end_line)
    duplicated_lines: int
    content_preview: str
    recommendation: str


class CheckpointerPatternAnalyzer(ast.NodeVisitor):
    """AST visitor to find checkpointer creation patterns."""
    
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()
        self.findings: list[CodeBlock] = []
        self.current_function: str | None = None
        self.pattern_blocks: list[tuple[int, int, str]] = []  # start, end, context
        
    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Visit function definitions to track context."""
        outer_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = outer_function
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)
        
    def find_checkpointer_patterns(self) -> list[CodeBlock]:
        """Find all checkpointer creation patterns in the source."""
        # Pattern 1: aiosqlite.connect pattern
        pattern1 = r"(import aiosqlite\s+from langgraph\.checkpoint\.sqlite\.aio import AsyncSqliteSaver.*?checkpointer = AsyncSqliteSaver\(conn=aconn\))"
        
        matches = list(re.finditer(
            r"(if checkpointer is None:\s+import aiosqlite\s+from langgraph\.checkpoint\.sqlite\.aio import AsyncSqliteSaver\s+aconn = await aiosqlite\.connect\(self\._db_path\)\s+.*?checkpointer = AsyncSqliteSaver\(conn=aconn\))",
            self.source,
            re.DOTALL
        ))
        
        for match in matches:
            start_line = self.source[:match.start()].count('\n') + 1
            end_line = self.source[:match.end()].count('\n') + 1
            content = match.group(1)
            
            # Find which function this belongs to
            context = self._find_function_for_line(start_line)
            
            self.findings.append(CodeBlock(
                content=content,
                start_line=start_line,
                end_line=end_line,
                function_name=context,
                context=context
            ))
            
        return self.findings
    
    def _find_function_for_line(self, line_num: int) -> str:
        """Find which function contains the given line number."""
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.lineno <= line_num <= node.end_lineno:
                    return node.name
        return "unknown"


def analyze_orchestrator_checkpointer_duplication(filepath: Path) -> list[DuplicationFinding]:
    """Analyze orchestrator.py for checkpointer duplication patterns."""
    source = filepath.read_text(encoding="utf-8")
    lines = source.splitlines()
    
    findings = []
    
    # Define the checkpointer creation pattern to search for
    pattern_markers = [
        "if checkpointer is None:",
        "import aiosqlite",
        "from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver",
        "aconn = await aiosqlite.connect",
        "PRAGMA journal_mode=WAL",
        "PRAGMA synchronous=NORMAL",
        "is_alive",
        "AsyncSqliteSaver(conn=aconn)"
    ]
    
    # Find all occurrences
    occurrences = []
    for i, line in enumerate(lines, 1):
        if "if checkpointer is None:" in line:
            # Find the function this belongs to
            func_name = _find_containing_function(lines, i)
            
            # Extract the block (approximately 15-20 lines)
            block_start = i
            block_end = min(i + 20, len(lines))
            block_content = '\n'.join(lines[block_start-1:block_end])
            
            occurrences.append({
                'function': func_name,
                'start_line': block_start,
                'end_line': block_end,
                'content': block_content
            })
    
    if len(occurrences) >= 2:
        # Calculate duplication metrics
        total_lines = sum(o['end_line'] - o['start_line'] + 1 for o in occurrences)
        avg_lines = total_lines / len(occurrences)
        
        # Extract common pattern
        common_pattern = _extract_common_pattern([o['content'] for o in occurrences])
        
        locations = [(o['function'], o['start_line'], o['end_line']) for o in occurrences]
        
        findings.append(DuplicationFinding(
            severity="high",
            pattern_name="Checkpointer Creation Block",
            locations=locations,
            duplicated_lines=int(avg_lines * (len(occurrences) - 1)),
            content_preview=common_pattern[:500] + "..." if len(common_pattern) > 500 else common_pattern,
            recommendation="Extract _create_checkpointer() private method to reduce ~60 lines of duplication"
        ))
    
    return findings


def _find_containing_function(lines: list[str], line_num: int) -> str:
    """Find the function that contains the given line number."""
    for i in range(line_num - 1, -1, -1):
        line = lines[i]
        if line.strip().startswith("async def ") or line.strip().startswith("def "):
            # Extract function name
            match = re.search(r"(?:async )?def\s+(\w+)", line)
            if match:
                return match.group(1)
    return "unknown"


def _extract_common_pattern(blocks: list[str]) -> str:
    """Extract the common pattern from duplicated blocks."""
    if not blocks:
        return ""
    
    # Simple approach: return the first block as representative
    # A more sophisticated approach would find the LCS
    lines = blocks[0].splitlines()
    
    # Filter to essential lines (imports, connection, pragmas, patch, saver)
    essential_lines = []
    for line in lines:
        stripped = line.strip()
        if any(marker in stripped for marker in [
            "import aiosqlite",
            "AsyncSqliteSaver",
            "aconn = await",
            "PRAGMA",
            "is_alive",
            "checkpointer ="
        ]):
            essential_lines.append(line)
    
    return '\n'.join(essential_lines)


def analyze_monkey_patch_usage(filepath: Path) -> list[DuplicationFinding]:
    """Analyze monkey-patch patterns for TD-002."""
    source = filepath.read_text(encoding="utf-8")
    lines = source.splitlines()
    
    findings = []
    
    # Find is_alive monkey patches
    patch_lines = []
    for i, line in enumerate(lines, 1):
        if "is_alive" in line and "def _is_alive" in line:
            func_name = _find_containing_function(lines, i)
            patch_lines.append((func_name, i, line.strip()))
    
    if len(patch_lines) >= 2:
        locations = [(f, l, l+5) for f, l, _ in patch_lines]
        
        # Get the patch implementation
        patch_impl = []
        for _, line_num, _ in patch_lines:
            for j in range(line_num - 1, min(line_num + 5, len(lines))):
                patch_impl.append(lines[j])
        
        findings.append(DuplicationFinding(
            severity="medium",
            pattern_name="aiosqlite is_alive Monkey-patch",
            locations=locations,
            duplicated_lines=len(patch_lines) * 5,
            content_preview="def _is_alive() -> bool:\n    return True\naconn.is_alive = _is_alive",
            recommendation="Extract _patch_aiosqlite_connection() method and track LangGraph issue for proper fix"
        ))
    
    return findings


def generate_td001_report(findings: list[DuplicationFinding], output_path: Path | None = None) -> str:
    """Generate TD-001 analysis report."""
    lines = [
        "# TD-001 深度分析报告: Checkpointer 代码重复",
        "",
        "## 问题概述",
        "",
        "**问题**: aiosqlite 连接 + PRAGMA + monkey-patch 代码在 orchestrator.py 中重复 4 次",
        "**影响**: ~60 行冗余代码，维护困难，容易遗漏修改",
        "**位置**: ",
        "- `start_pipeline()` (行 437-457)",
        "- `resume_pipeline()` (行 561-581)",
        "- `restart_from_node()` (行 726-746)",
        "- `_restart_node()` (行 893-912)",
        "",
        "## 重复代码分析",
        "",
    ]
    
    for finding in findings:
        lines.extend([
            f"### {finding.pattern_name}",
            "",
            f"**严重级别**: {finding.severity.upper()}",
            f"**重复行数**: ~{finding.duplicated_lines} 行",
            "",
            "**出现位置**:",
        ])
        for func, start, end in finding.locations:
            lines.append(f"- `{func}()` (行 {start}-{end})")
        
        lines.extend([
            "",
            "**代码样例**:",
            "```python",
            finding.content_preview,
            "```",
            "",
            "**修复建议**:",
            f"> {finding.recommendation}",
            "",
        ])
    
    lines.extend([
        "## 修复方案",
        "",
        "### 推荐实现",
        "",
        "```python",
        "async def _create_checkpointer(self) -> AsyncSqliteSaver:",
        '    """Create an AsyncSqliteSaver checkpointer with proper async support."""',
        "    import aiosqlite",
        "    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver",
        "",
        "    aconn = await aiosqlite.connect(self._db_path)",
        "    await aconn.execute('PRAGMA journal_mode=WAL')",
        "    await aconn.execute('PRAGMA synchronous=NORMAL')",
        "",
        "    # Patch for langgraph compatibility (TD-002)",
        "    self._patch_aiosqlite_connection(aconn)",
        "",
        "    return AsyncSqliteSaver(conn=aconn)",
        "",
        "def _patch_aiosqlite_connection(self, conn) -> None:",
        '    """Add is_alive method for langgraph compatibility (TD-002)."""',
        "    if not hasattr(conn, 'is_alive'):",
        "        conn.is_alive = lambda: True  # noqa: E731",
        "```",
        "",
        "### 使用方式",
        "",
        "将 4 处重复代码替换为:",
        "",
        "```python",
        "checkpointer = self._checkpointer",
        "if checkpointer is None:",
        "    checkpointer = await self._create_checkpointer()",
        "```",
        "",
        "## 预期收益",
        "",
        "- **代码行数减少**: ~60 行 → ~15 行",
        "- **维护成本降低**: 修改只需一处",
        "- **可读性提升**: 意图更清晰",
        "- **测试简化**: 只需测试一个方法",
        "",
    ])
    
    report = '\n'.join(lines)
    
    if output_path:
        output_path.write_text(report, encoding="utf-8")
    
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze code duplication in DocuSwarm")
    parser.add_argument("--target", default="autoBMAD/docuswarm/pipeline/orchestrator.py",
                        help="Target file to analyze")
    parser.add_argument("--output", help="Output report file path")
    args = parser.parse_args()
    
    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: File not found: {target_path}")
        return 1
    
    print(f"Analyzing: {target_path}")
    print("=" * 60)
    
    # Analyze TD-001
    td001_findings = analyze_orchestrator_checkpointer_duplication(target_path)
    
    # Analyze TD-002
    td002_findings = analyze_monkey_patch_usage(target_path)
    
    all_findings = td001_findings + td002_findings
    
    if not all_findings:
        print("No significant duplication patterns found.")
        return 0
    
    for finding in all_findings:
        print(f"\n[{finding.severity.upper()}] {finding.pattern_name}")
        print(f"  重复次数: {len(finding.locations)}")
        print(f"  重复行数: ~{finding.duplicated_lines}")
        print("  出现位置:")
        for func, start, end in finding.locations:
            print(f"    - {func}() @ line {start}-{end}")
    
    # Generate report
    output_path = Path(args.output) if args.output else None
    report = generate_td001_report(td001_findings, output_path)
    
    if output_path:
        print(f"\nReport saved to: {output_path}")
    else:
        print("\n" + "=" * 60)
        print(report)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
