"""
DocuSwarm Type Fixes Script
===========================

Automatically applies fixes for critical type errors identified by basedpyright.

Usage:
    python tools/apply_type_fixes.py --dry-run    # Preview changes
    python tools/apply_type_fixes.py --apply      # Apply changes
    python tools/apply_type_fixes.py --check      # Check current state

WARNING: Make sure to backup your code or have git history before applying!
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class Fix:
    """Represents a single fix operation."""
    name: str
    description: str
    file_pattern: str
    apply: Callable[[str], str]
    check: Callable[[str], bool]


class TypeFixApplicator:
    """Applies type fixes to DocuSwarm codebase."""
    
    def __init__(self, base_path: str = "autoBMAD/docuswarm"):
        self.base_path = Path(base_path)
        self.changes_made: list[tuple[str, str]] = []
        
    def fix_evaluator_typeddict(self, content: str) -> str:
        """Fix TypedDict access in evaluator.py."""
        # Replace direct access with .get()
        replacements = [
            (
                'task_name = agent_input["task_name"]',
                'task_name = agent_input.get("task_name", "")'
            ),
            (
                'task_description = agent_input["task_description"]',
                'task_description = agent_input.get("task_description", "")'
            ),
            (
                '_ = agent_input["deliverable_artifact"]',
                '_ = agent_input.get("deliverable_artifact", {})'
            ),
            (
                'deliverable_body = agent_input["deliverable_body"]',
                'deliverable_body = agent_input.get("deliverable_body", "")'
            ),
            (
                'criteria = agent_input["criteria"] or self.criteria',
                'criteria = agent_input.get("criteria") or self.criteria'
            ),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        return content
    
    def check_evaluator_typeddict(self, content: str) -> bool:
        """Check if evaluator.py has TypedDict issues."""
        return 'agent_input["task_name"]' in content
    
    def fix_independent_typeddict(self, content: str) -> str:
        """Fix TypedDict access in independent.py."""
        replacements = [
            (
                'task_name = agent_input["task_name"]',
                'task_name = agent_input.get("task_name", "")'
            ),
            (
                'task_description = agent_input["task_description"]',
                'task_description = agent_input.get("task_description", "")'
            ),
            (
                'role_supplement = agent_input["role_supplement"]',
                'role_supplement = agent_input.get("role_supplement", "")'
            ),
            (
                'deliverable_reqs = agent_input["deliverable_requirements"]',
                'deliverable_reqs = agent_input.get("deliverable_requirements", {})'
            ),
            (
                'original_context = agent_input["original_context_summary"]',
                'original_context = agent_input.get("original_context_summary", "")'
            ),
            (
                'chained_deliverables = agent_input["chained_deliverables_summary"]',
                'chained_deliverables = agent_input.get("chained_deliverables_summary", [])'
            ),
            (
                'iteration_feedback = agent_input["iteration_feedback"]',
                'iteration_feedback = agent_input.get("iteration_feedback")'
            ),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        return content
    
    def check_independent_typeddict(self, content: str) -> bool:
        """Check if independent.py has TypedDict issues."""
        return 'agent_input["task_name"]' in content
    
    def fix_dual_agent_import(self, content: str) -> str:
        """Fix NodeExecutionContext import in dual_agent.py."""
        # Add import to TYPE_CHECKING block
        if 'from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext' not in content:
            content = content.replace(
                'from autoBMAD.docuswarm.pipeline.state import PipelineState',
                'from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext\n    from autoBMAD.docuswarm.pipeline.state import PipelineState'
            )
        
        # Fix execution_context parameter to use string literal
        content = content.replace(
            'execution_context: NodeExecutionContext,',
            'execution_context: "NodeExecutionContext",'
        )
        return content
    
    def check_dual_agent_import(self, content: str) -> bool:
        """Check if dual_agent.py has import issues."""
        return 'from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext' not in content
    
    def fix_models_dunder_all(self, content: str) -> str:
        """Fix __all__ in models/__init__.py with explicit re-exports."""
        # Check if already fixed
        if 'from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolResult' in content:
            return content
        
        new_content = '''"""Models module for DocuSwarm."""

from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolResult
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolRegistry

__all__ = [
    "ToolResult",
    "ToolRegistry",
]
'''
        return new_content
    
    def check_models_dunder_all(self, content: str) -> bool:
        """Check if models/__init__.py has dunder all issues."""
        return '__getattr__' in content and 'ToolResult' in content
    
    def fix_getattr_annotations(self, content: str) -> str:
        """Add type annotations to __getattr__ functions."""
        # Add Any import if not present
        if 'from typing import Any' not in content and 'from typing' not in content:
            content = 'from typing import Any\n\n' + content
        elif 'from typing import' in content and 'Any' not in content:
            content = content.replace(
                'from typing import',
                'from typing import Any,'
            )
        
        # Fix __getattr__ signature
        content = re.sub(
            r'def __getattr__\(name\)(?!\s*->)',
            'def __getattr__(name: str) -> Any',
            content
        )
        return content
    
    def check_getattr_annotations(self, content: str) -> bool:
        """Check if __getattr__ needs type annotations."""
        match = re.search(r'def __getattr__\(([^)]+)\)', content)
        if match:
            params = match.group(1)
            return ': str' not in params and '-> Any' not in content[match.end():match.end()+20]
        return False
    
    def fix_tool_registry_override(self, content: str) -> str:
        """Add @override decorator to tool_registry.py."""
        # Check if already has override
        if '@override' in content or 'from typing import override' in content:
            return content
        
        # Add import
        if 'from typing import' in content:
            content = content.replace(
                'from typing import',
                'from typing import override,'
            )
        else:
            content = 'from typing import override\n\n' + content
        
        # Add decorator
        content = content.replace(
            '    def clear(self)',
            '    @override\n    def clear(self)'
        )
        return content
    
    def check_tool_registry_override(self, content: str) -> bool:
        """Check if tool_registry.py needs @override."""
        return 'def clear(self)' in content and '@override' not in content
    
    def get_fixes(self) -> list[Fix]:
        """Get list of all available fixes."""
        return [
            Fix(
                name="evaluator_typeddict",
                description="Fix TypedDict access in evaluator.py",
                file_pattern="agents/evaluator.py",
                apply=self.fix_evaluator_typeddict,
                check=self.check_evaluator_typeddict,
            ),
            Fix(
                name="independent_typeddict",
                description="Fix TypedDict access in independent.py",
                file_pattern="agents/independent.py",
                apply=self.fix_independent_typeddict,
                check=self.check_independent_typeddict,
            ),
            Fix(
                name="dual_agent_import",
                description="Fix NodeExecutionContext import in dual_agent.py",
                file_pattern="nodes/dual_agent.py",
                apply=self.fix_dual_agent_import,
                check=self.check_dual_agent_import,
            ),
            Fix(
                name="models_dunder_all",
                description="Fix __all__ in models/__init__.py",
                file_pattern="models/__init__.py",
                apply=self.fix_models_dunder_all,
                check=self.check_models_dunder_all,
            ),
            Fix(
                name="getattr_annotations",
                description="Add type annotations to __getattr__ functions",
                file_pattern="*/__init__.py",
                apply=self.fix_getattr_annotations,
                check=self.check_getattr_annotations,
            ),
            Fix(
                name="tool_registry_override",
                description="Add @override to tool_registry.py",
                file_pattern="models/tool_registry.py",
                apply=self.fix_tool_registry_override,
                check=self.check_tool_registry_override,
            ),
        ]
    
    def check_all(self) -> list[tuple[str, str, bool]]:
        """Check all files for issues."""
        results = []
        for fix in self.get_fixes():
            file_path = self.base_path / fix.file_pattern.replace('*/', '')
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                needs_fix = fix.check(content)
                results.append((fix.name, str(file_path), needs_fix))
            else:
                # Try glob pattern
                import glob
                pattern = str(self.base_path / fix.file_pattern)
                for fp in glob.glob(pattern, recursive=True):
                    content = Path(fp).read_text(encoding='utf-8')
                    needs_fix = fix.check(content)
                    results.append((fix.name, fp, needs_fix))
        return results
    
    def apply_fix(self, fix_name: str, dry_run: bool = False) -> bool:
        """Apply a specific fix."""
        for fix in self.get_fixes():
            if fix.name == fix_name:
                file_path = self.base_path / fix.file_pattern.replace('*/', '')
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8')
                    if not fix.check(content):
                        print(f"  Skipping {fix.name}: already fixed")
                        return True
                    
                    new_content = fix.apply(content)
                    if dry_run:
                        print(f"  Would apply {fix.name} to {file_path}")
                    else:
                        file_path.write_text(new_content, encoding='utf-8')
                        self.changes_made.append((str(file_path), fix.name))
                        print(f"  Applied {fix.name} to {file_path}")
                    return True
        print(f"  Fix {fix_name} not found!")
        return False
    
    def apply_all(self, dry_run: bool = False) -> None:
        """Apply all fixes."""
        print(f"\n{'DRY RUN - ' if dry_run else ''}Applying fixes...")
        print("=" * 60)
        
        for fix in self.get_fixes():
            self.apply_fix(fix.name, dry_run)
        
        print("=" * 60)
        if dry_run:
            print("Dry run complete. Use --apply to make changes.")
        else:
            print(f"Applied {len(self.changes_made)} fixes.")


def main():
    parser = argparse.ArgumentParser(description="Apply type fixes to DocuSwarm")
    parser.add_argument("--check", action="store_true", help="Check which fixes are needed")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply all fixes")
    parser.add_argument("--fix", help="Apply specific fix by name")
    parser.add_argument("--list", action="store_true", help="List available fixes")
    args = parser.parse_args()
    
    applicator = TypeFixApplicator()
    
    if args.list:
        print("\nAvailable fixes:")
        for fix in applicator.get_fixes():
            print(f"  {fix.name}: {fix.description}")
            print(f"    File: {fix.file_pattern}")
        return
    
    if args.check:
        print("\nChecking for issues...")
        print("=" * 60)
        results = applicator.check_all()
        for name, path, needs_fix in results:
            status = "NEEDS FIX" if needs_fix else "OK"
            print(f"  [{status}] {name}: {path}")
        return
    
    if args.fix:
        applicator.apply_fix(args.fix, dry_run=args.dry_run)
        return
    
    if args.apply or args.dry_run:
        applicator.apply_all(dry_run=args.dry_run)
        return
    
    # Default: show help
    parser.print_help()
    print("\nExamples:")
    print("  python tools/apply_type_fixes.py --check")
    print("  python tools/apply_type_fixes.py --dry-run")
    print("  python tools/apply_type_fixes.py --apply")
    print("  python tools/apply_type_fixes.py --fix evaluator_typeddict")


if __name__ == "__main__":
    main()
