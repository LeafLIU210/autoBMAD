#!/usr/bin/env python3
"""TD-4: 输出目录与工作目录隐式绑定 Path.cwd() 深度分析工具.

该工具用于深度分析 DocuSwarm 中 TD-4 技术债问题：
- 识别所有使用 Path.cwd() 作为默认值的代码点
- 追踪 work_dir/output_dir 的传递链路
- 检测 os.chdir() 在测试中的使用
- 分析工具、Agent、SessionManager 之间的目录依赖关系

用法:
    python tools/td4_path_cwd_analyzer.py --scan-codebase
    python tools/td4_path_cwd_analyzer.py --analyze-chain
    python tools/td4_path_cwd_analyzer.py --check-tests
    python tools/td4_path_cwd_analyzer.py --full-analysis
    python tools/td4_path_cwd_analyzer.py --generate-report --output docs/research/TD-4-detailed-research-report.md
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUSWARM_ROOT = PROJECT_ROOT / "autoBMAD" / "docuswarm"
TESTS_ROOT = PROJECT_ROOT / "tests"


@dataclass
class PathCwdUsage:
    """Path.cwd() 使用点记录."""
    file: str
    line: int
    column: int
    context: str  # 函数/类上下文
    code_snippet: str
    severity: str  # high, medium, low
    category: str  # tool, agent, session, test, other
    notes: str = ""


@dataclass
class ChdirUsage:
    """os.chdir() 使用点记录."""
    file: str
    line: int
    code_snippet: str
    context: str  # test function or setup
    has_proper_cleanup: bool


@dataclass
class DirectoryChainLink:
    """目录传递链中的一个环节."""
    component: str  # Tool, Agent, SessionManager, etc.
    file: str
    param_name: str  # output_dir, work_dir, etc.
    default_value: str  # Path.cwd(), None, etc.
    receives_from: str | None = None  # 从哪个组件接收
    passes_to: list[str] = field(default_factory=list)  # 传递给哪些组件


@dataclass
class TD4AnalysisResult:
    """TD-4 分析结果."""
    path_cwd_usages: list[PathCwdUsage] = field(default_factory=list)
    chdir_usages: list[ChdirUsage] = field(default_factory=list)
    directory_chains: list[DirectoryChainLink] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, int] = field(default_factory=dict)


def _find_files(root: Path, pattern: str = "*.py") -> list[Path]:
    """递归查找文件."""
    if not root.exists():
        return []
    return list(root.rglob(pattern))


def _read_file(filepath: Path) -> str:
    """读取文件内容."""
    try:
        return filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return filepath.read_text(encoding="utf-8", errors="replace")


def _parse_ast(filepath: Path) -> ast.AST | None:
    """解析 Python 文件为 AST."""
    try:
        content = _read_file(filepath)
        return ast.parse(content)
    except SyntaxError:
        return None


def _get_context(node: ast.AST, tree: ast.AST) -> str:
    """获取 AST 节点的上下文（类/函数名）."""
    for parent in ast.walk(tree):
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.iter_child_nodes(parent):
                if child is node or (hasattr(child, "lineno") and hasattr(node, "lineno") 
                                     and child.lineno == node.lineno):
                    if isinstance(parent, ast.ClassDef):
                        return f"class:{parent.name}"
                    else:
                        return f"func:{parent.name}"
    return "module"


def scan_path_cwd_usages() -> list[PathCwdUsage]:
    """扫描所有 Path.cwd() 的使用点."""
    usages: list[PathCwdUsage] = []
    
    files = _find_files(DOCUSWARM_ROOT) + _find_files(TESTS_ROOT)
    
    for filepath in files:
        content = _read_file(filepath)
        tree = _parse_ast(filepath)
        
        if tree is None:
            continue
        
        # 查找 Path.cwd() 调用
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查是否是 Path.cwd()
                if (isinstance(node.func, ast.Attribute) 
                    and node.func.attr == "cwd"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in ("Path", "PosixPath", "WindowsPath", "PurePath")):
                    
                    context = _get_context(node, tree)
                    lines = content.split("\n")
                    line_idx = node.lineno - 1
                    code_snippet = lines[line_idx].strip() if 0 <= line_idx < len(lines) else ""
                    
                    # 确定类别和严重性
                    rel_path = str(filepath.relative_to(PROJECT_ROOT))
                    if "test" in rel_path.lower():
                        category = "test"
                        severity = "medium"
                    elif "tool" in rel_path.lower():
                        category = "tool"
                        severity = "high"
                    elif "agent" in rel_path.lower():
                        category = "agent"
                        severity = "high"
                    elif "session" in rel_path.lower() or "llm" in rel_path.lower():
                        category = "session"
                        severity = "high"
                    else:
                        category = "other"
                        severity = "low"
                    
                    usages.append(PathCwdUsage(
                        file=rel_path,
                        line=node.lineno,
                        column=node.col_offset,
                        context=context,
                        code_snippet=code_snippet,
                        severity=severity,
                        category=category,
                    ))
        
        # 文本搜索检测 output_dir or Path.cwd() 模式
        for i, line in enumerate(content.split("\n"), 1):
            if "or Path.cwd()" in line or "or Path.cwd" in line:
                # 检查是否已记录
                if not any(u.file == str(filepath.relative_to(PROJECT_ROOT)) and u.line == i for u in usages):
                    context = "module"
                    rel_path = str(filepath.relative_to(PROJECT_ROOT))
                    
                    if "test" in rel_path.lower():
                        category = "test"
                        severity = "medium"
                    elif "tool" in rel_path.lower():
                        category = "tool"
                        severity = "high"
                    else:
                        category = "other"
                        severity = "medium"
                    
                    usages.append(PathCwdUsage(
                        file=rel_path,
                        line=i,
                        column=line.find("or Path.cwd()"),
                        context=context,
                        code_snippet=line.strip(),
                        severity=severity,
                        category=category,
                        notes="or Path.cwd() fallback pattern",
                    ))
    
    return sorted(usages, key=lambda x: (x.category, x.severity, x.file))


def scan_chdir_usages() -> list[ChdirUsage]:
    """扫描所有 os.chdir() 的使用点."""
    usages: list[ChdirUsage] = []
    
    files = _find_files(TESTS_ROOT)
    
    for filepath in files:
        content = _read_file(filepath)
        tree = _parse_ast(filepath)
        
        if tree is None:
            continue
        
        lines = content.split("\n")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查 os.chdir 调用
                if (isinstance(node.func, ast.Attribute) 
                    and node.func.attr == "chdir"):
                    
                    context = _get_context(node, tree)
                    line_idx = node.lineno - 1
                    code_snippet = lines[line_idx].strip() if 0 <= line_idx < len(lines) else ""
                    
                    # 检查是否有清理（在同一上下文中查找 os.chdir 恢复）
                    has_cleanup = False
                    func_node = None
                    for parent in ast.walk(tree):
                        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            for child in ast.iter_child_nodes(parent):
                                if child is node:
                                    func_node = parent
                                    break
                    
                    if func_node:
                        # 检查函数中是否有恢复 cwd 的逻辑
                        func_content = content.split("\n")[func_node.lineno-1:func_node.end_lineno]
                        func_text = "\n".join(func_content)
                        has_cleanup = "os.chdir(original" in func_text or "os.chdir(cwd" in func_text
                    
                    rel_path = str(filepath.relative_to(PROJECT_ROOT))
                    usages.append(ChdirUsage(
                        file=rel_path,
                        line=node.lineno,
                        code_snippet=code_snippet,
                        context=context,
                        has_proper_cleanup=has_cleanup,
                    ))
    
    return sorted(usages, key=lambda x: x.file)


def analyze_directory_chain() -> list[DirectoryChainLink]:
    """分析 output_dir/work_dir 的传递链."""
    chain: list[DirectoryChainLink] = []
    
    # 1. CreateDeliverableTool
    tool_file = DOCUSWARM_ROOT / "tools" / "create_deliverable.py"
    if tool_file.exists():
        content = _read_file(tool_file)
        if "output_dir: Path | None = None" in content:
            chain.append(DirectoryChainLink(
                component="CreateDeliverableTool",
                file="autoBMAD/docuswarm/tools/create_deliverable.py",
                param_name="output_dir",
                default_value="Path.cwd()",
                receives_from=None,
                passes_to=["FileSystem"],
            ))
    
    # 2. CreateDocumentSetTool
    docset_file = DOCUSWARM_ROOT / "tools" / "create_document_set.py"
    if docset_file.exists():
        content = _read_file(docset_file)
        if "output_dir: Path | None = None" in content:
            chain.append(DirectoryChainLink(
                component="CreateDocumentSetTool",
                file="autoBMAD/docuswarm/tools/create_document_set.py",
                param_name="output_dir",
                default_value="Path.cwd()",
                receives_from=None,
                passes_to=["FileSystem"],
            ))
    
    # 3. KimiSessionManager
    session_file = DOCUSWARM_ROOT / "llm" / "session_manager.py"
    if session_file.exists():
        content = _read_file(session_file)
        if "work_dir: KaosPath" in content:
            chain.append(DirectoryChainLink(
                component="KimiSessionManager",
                file="autoBMAD/docuswarm/llm/session_manager.py",
                param_name="work_dir",
                default_value="Required (no default)",
                receives_from="Orchestrator/Flow",
                passes_to=["SDK Session"],
            ))
    
    # 4. IndependentAgent
    agent_file = DOCUSWARM_ROOT / "agents" / "independent.py"
    if agent_file.exists():
        content = _read_file(agent_file)
        if "output_dir" in content or "work_dir" in content:
            chain.append(DirectoryChainLink(
                component="IndependentAgent",
                file="autoBMAD/docuswarm/agents/independent.py",
                param_name="output_dir/work_dir",
                default_value="project_root / 'output' / pipeline_id",
                receives_from="NodeExecutor",
                passes_to=["KimiSessionManager", "CreateDeliverableTool"],
            ))
    
    # 5. HybridOrchestrator
    orch_file = DOCUSWARM_ROOT / "pipeline" / "orchestrator.py"
    if orch_file.exists():
        content = _read_file(orch_file)
        if "work_dir" in content:
            chain.append(DirectoryChainLink(
                component="HybridOrchestrator",
                file="autoBMAD/docuswarm/pipeline/orchestrator.py",
                param_name="work_dir",
                default_value="autoBMAD/output (not cwd)",
                receives_from=None,
                passes_to=["KimiSessionManager"],
            ))
    
    # 6. FileStorage
    storage_file = DOCUSWARM_ROOT / "storage" / "files.py"
    if storage_file.exists():
        content = _read_file(storage_file)
        if "output_root" in content:
            chain.append(DirectoryChainLink(
                component="FileStorage",
                file="autoBMAD/docuswarm/storage/files.py",
                param_name="output_root",
                default_value="output (constant)",
                receives_from=None,
                passes_to=["FileSystem"],
            ))
    
    return chain


def generate_findings(result: TD4AnalysisResult) -> list[dict[str, Any]]:
    """生成分析发现."""
    findings = []
    
    # 发现 1: Path.cwd() 在生产代码中的使用
    prod_cwd = [u for u in result.path_cwd_usages if u.category != "test"]
    if prod_cwd:
        high_sev = [u for u in prod_cwd if u.severity == "high"]
        findings.append({
            "id": "TD-4.1",
            "severity": "high",
            "title": f"生产代码中存在 {len(prod_cwd)} 处 Path.cwd() 隐式依赖",
            "detail": f"其中 {len(high_sev)} 处为高严重性（工具层和Agent层）",
            "locations": [f"{u.file}:{u.line}" for u in high_sev[:5]],
            "recommendation": "统一通过构造函数参数注入 output_dir/work_dir，移除 Path.cwd() 默认值",
        })
    
    # 发现 2: 测试中的 os.chdir()
    if result.chdir_usages:
        without_cleanup = [u for u in result.chdir_usages if not u.has_proper_cleanup]
        findings.append({
            "id": "TD-4.2",
            "severity": "medium",
            "title": f"测试代码中存在 {len(result.chdir_usages)} 处 os.chdir()",
            "detail": f"其中 {len(without_cleanup)} 处可能没有适当的清理",
            "locations": [f"{u.file}:{u.line}" for u in result.chdir_usages[:5]],
            "recommendation": "使用显式 output_dir 参数替代 os.chdir()，提高测试隔离性",
        })
    
    # 发现 3: 目录传递链断裂
    chain = result.directory_chains
    tools_with_cwd = [c for c in chain if c.component.endswith("Tool") and c.default_value == "Path.cwd()"]
    if tools_with_cwd:
        findings.append({
            "id": "TD-4.3",
            "severity": "high",
            "title": "工具层目录传递链存在断裂风险",
            "detail": "CreateDeliverableTool 和 CreateDocumentSetTool 默认使用 Path.cwd()，但上层调用者可能未显式传递 output_dir",
            "locations": [c.file for c in tools_with_cwd],
            "recommendation": "确保所有调用点都显式传递 output_dir，或将默认值改为更具确定性的路径",
        })
    
    # 发现 4: work_dir 与 output_dir 语义混淆
    work_dir_links = [c for c in chain if "work_dir" in c.param_name]
    output_dir_links = [c for c in chain if "output_dir" in c.param_name]
    if work_dir_links and output_dir_links:
        findings.append({
            "id": "TD-4.4",
            "severity": "medium",
            "title": "work_dir 与 output_dir 语义可能存在混淆",
            "detail": f"发现 {len(work_dir_links)} 处 work_dir 和 {len(output_dir_links)} 处 output_dir 使用点，需要明确区分两者的职责边界",
            "locations": [c.file for c in work_dir_links + output_dir_links],
            "recommendation": "明确 work_dir 作为 SDK 执行环境，output_dir 作为交付物存储位置，避免混用",
        })
    
    return findings


def print_analysis(result: TD4AnalysisResult) -> None:
    """打印分析结果."""
    print("=" * 80)
    print("TD-4: 输出目录与工作目录隐式绑定 Path.cwd() 深度分析报告")
    print("=" * 80)
    print()
    
    # 1. Path.cwd() 使用统计
    print("[STATS] Path.cwd() 使用统计")
    print("-" * 80)
    by_category = {}
    for u in result.path_cwd_usages:
        by_category[u.category] = by_category.get(u.category, 0) + 1
    
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat:12s}: {count:3d} 处")
    print(f"  {'总计':12s}: {len(result.path_cwd_usages):3d} 处")
    print()
    
    # 2. 高严重性使用点
    print("[HIGH] 高严重性 Path.cwd() 使用点 (生产代码)")
    print("-" * 80)
    high_prod = [u for u in result.path_cwd_usages if u.severity == "high" and u.category != "test"]
    for u in high_prod[:10]:
        print(f"  {u.file}:{u.line}")
        print(f"    代码: {u.code_snippet[:60]}")
        print(f"    上下文: {u.context}")
        print()
    if len(high_prod) > 10:
        print(f"  ... 还有 {len(high_prod) - 10} 处")
    print()
    
    # 3. os.chdir() 使用
    print("[MED] 测试中的 os.chdir() 使用")
    print("-" * 80)
    print(f"  总计: {len(result.chdir_usages)} 处")
    for u in result.chdir_usages[:8]:
        cleanup_status = "[OK] 有清理" if u.has_proper_cleanup else "[WARN] 可能无清理"
        print(f"  {u.file}:{u.line} ({cleanup_status})")
        print(f"    代码: {u.code_snippet[:50]}")
    if len(result.chdir_usages) > 8:
        print(f"  ... 还有 {len(result.chdir_usages) - 8} 处")
    print()
    
    # 4. 目录传递链
    print("[CHAIN] 目录传递链分析")
    print("-" * 80)
    for link in result.directory_chains:
        print(f"  [COMP] {link.component}")
        print(f"     文件: {link.file}")
        print(f"     参数: {link.param_name}")
        print(f"     默认值: {link.default_value}")
        if link.receives_from:
            print(f"     ← 接收自: {link.receives_from}")
        if link.passes_to:
            print(f"     → 传递给: {', '.join(link.passes_to)}")
        print()
    
    # 5. 关键发现
    print("[FINDINGS] 关键发现")
    print("-" * 80)
    for f in result.findings:
        severity_symbol = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(f["severity"], "[INFO]")
        print(f"  {severity_symbol} [{f['id']}] {f['title']}")
        print(f"     严重性: {f['severity']}")
        print(f"     详情: {f['detail']}")
        print(f"     位置: {', '.join(f['locations'][:3])}")
        print(f"     建议: {f['recommendation']}")
        print()


def generate_markdown_report(result: TD4AnalysisResult) -> str:
    """生成 Markdown 格式的研究报告."""
    lines = []
    
    lines.append("# TD-4 深度研究报告：输出目录与工作目录隐式绑定 Path.cwd()")
    lines.append("")
    lines.append("> 研究日期: 2026-03-25")
    lines.append("> ")
    lines.append("> 研究范围: `autoBMAD/docuswarm` 工具层、Agent 层、测试层")
    lines.append("> ")
    lines.append("> 研究方法: 静态代码分析、AST 解析、依赖链路追踪")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 执行摘要
    lines.append("## 1. 执行摘要")
    lines.append("")
    lines.append("### 1.1 问题定义 (TD-4)")
    lines.append("")
    lines.append("根据技术债评估报告，TD-4 描述的是：")
    lines.append("")
    lines.append("> **输出目录/工作目录隐式耦合**: 业务行为依赖进程级全局状态 `Path.cwd()`，")
    lines.append("> 测试、CLI、Agent、脚本必须共享同一套隐式工作目录假设。")
    lines.append("")
    
    total_cwd = len(result.path_cwd_usages)
    prod_cwd = len([u for u in result.path_cwd_usages if u.category != "test"])
    test_cwd = len([u for u in result.path_cwd_usages if u.category == "test"])
    chdir_count = len(result.chdir_usages)
    
    lines.append("### 1.2 关键数据")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| Path.cwd() 使用点 (总计) | {total_cwd} |")
    lines.append(f"| Path.cwd() 使用点 (生产代码) | {prod_cwd} |")
    lines.append(f"| Path.cwd() 使用点 (测试代码) | {test_cwd} |")
    lines.append(f"| os.chdir() 使用点 (测试) | {chdir_count} |")
    lines.append(f"| 目录传递链环节 | {len(result.directory_chains)} |")
    lines.append("")
    
    # 问题分析
    lines.append("## 2. 问题深度分析")
    lines.append("")
    
    lines.append("### 2.1 Path.cwd() 在生产代码中的分布")
    lines.append("")
    lines.append("```")
    by_cat = {}
    for u in result.path_cwd_usages:
        if u.category != "test":
            by_cat[u.category] = by_cat.get(u.category, 0) + 1
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        lines.append(f"{cat:15s}: {'█' * count} {count}")
    lines.append("```")
    lines.append("")
    
    lines.append("### 2.2 关键问题代码")
    lines.append("")
    high_prod = [u for u in result.path_cwd_usages if u.severity == "high" and u.category != "test"]
    for u in high_prod:
        lines.append(f"#### {u.file}:{u.line}")
        lines.append("")
        lines.append(f"```python")
        lines.append(f"# 上下文: {u.context}")
        lines.append(f"{u.code_snippet}")
        lines.append("```")
        lines.append("")
        lines.append(f"**问题**: {u.notes or '使用 Path.cwd() 作为默认值，依赖全局进程状态'}")
        lines.append("")
    
    lines.append("### 2.3 测试中的 os.chdir() 模式")
    lines.append("")
    lines.append("测试代码为了绕过 `Path.cwd()` 依赖，不得不使用 `os.chdir()` 来操纵全局状态：")
    lines.append("")
    lines.append("```python")
    lines.append("# 典型模式 (来自 test_create_deliverable_unit.py)")
    lines.append("@pytest.fixture")
    lines.append("def temp_dir(self):")
    lines.append("    temp_path = tempfile.mkdtemp()")
    lines.append("    original_cwd = os.getcwd()  # 保存原目录")
    lines.append("    os.chdir(temp_path)         # 切换到临时目录")
    lines.append("    yield temp_path")
    lines.append("    os.chdir(original_cwd)      # 恢复目录")
    lines.append("    shutil.rmtree(temp_path, ignore_errors=True)")
    lines.append("```")
    lines.append("")
    lines.append(f"这种模式的弊端：")
    lines.append(f"- 测试间共享全局状态，可能导致交叉污染")
    lines.append(f"- 需要显式清理，遗漏会导致后续测试失败")
    lines.append(f"- 无法并行执行测试（改变全局 cwd）")
    lines.append("")
    
    # 目录传递链
    lines.append("## 3. 目录传递链分析")
    lines.append("")
    lines.append("### 3.1 当前架构")
    lines.append("")
    lines.append("```")
    lines.append("CLI Entry (docuswarm start)")
    lines.append("    │")
    lines.append("    ▼")
    lines.append("HybridOrchestrator")
    lines.append("    │  work_dir = autoBMAD/output (显式)")
    lines.append("    ▼")
    lines.append("KimiSessionManager")
    lines.append("    │  work_dir (required)")
    lines.append("    ▼")
    lines.append("SDK Session")
    lines.append("    │  work_dir 作为执行环境")
    lines.append("    ▼")
    lines.append("IndependentAgent ──► CreateDeliverableTool")
    lines.append("                         │  output_dir (可选, 默认 Path.cwd())")
    lines.append("                         ▼")
    lines.append("                    FileSystem")
    lines.append("```")
    lines.append("")
    
    lines.append("### 3.2 链断裂点")
    lines.append("")
    lines.append("| 环节 | 参数 | 默认值 | 风险等级 |")
    lines.append("|------|------|--------|----------|")
    for link in result.directory_chains:
        if "Path.cwd()" in link.default_value:
            risk = "🔴 高"
        elif "Required" in link.default_value:
            risk = "🟢 低"
        else:
            risk = "🟡 中"
        lines.append(f"| {link.component} | {link.param_name} | {link.default_value} | {risk} |")
    lines.append("")
    
    # 影响分析
    lines.append("## 4. 业务影响分析")
    lines.append("")
    lines.append("### 4.1 当前影响")
    lines.append("")
    for f in result.findings:
        lines.append(f"#### {f['id']}: {f['title']}")
        lines.append("")
        lines.append(f"**严重性**: {f['severity']}")
        lines.append("")
        lines.append(f"**详情**: {f['detail']}")
        lines.append("")
        lines.append("**相关位置**:")
        for loc in f['locations']:
            lines.append(f"- `{loc}`")
        lines.append("")
        lines.append(f"**修复建议**: {f['recommendation']}")
        lines.append("")
    
    lines.append("### 4.2 潜在风险")
    lines.append("")
    lines.append("1. **并发执行风险**: 如果未来需要并行执行多个 pipeline，全局 `Path.cwd()` 会导致文件写入冲突")
    lines.append("2. **远程执行风险**: 分布式或容器化环境下，`Path.cwd()` 的行为难以预测")
    lines.append("3. **测试维护成本**: 每个新测试都需要处理 `os.chdir()` 模式，增加开发负担")
    lines.append("4. **调试困难**: 用户报告文件位置问题时，难以确定实际写入路径")
    lines.append("")
    
    # 修复方案
    lines.append("## 5. 修复方案")
    lines.append("")
    lines.append("### 5.1 短期方案 (Phase 1: 止血)")
    lines.append("")
    lines.append("1. **工具层显式注入**: 确保所有 `CreateDeliverableTool` 和 `CreateDocumentSetTool` 的调用都显式传递 `output_dir`")
    lines.append("2. **Agent 层统一**: `IndependentAgent` 创建工具时，使用已确定的 `output_dir` 而非依赖默认值")
    lines.append("3. **测试清理**: 将依赖 `os.chdir()` 的测试逐步替换为显式 `output_dir` 注入")
    lines.append("")
    
    lines.append("### 5.2 中期方案 (Phase 2: 收敛)")
    lines.append("")
    lines.append("1. **移除 Path.cwd() 默认值**: 将工具的 `output_dir` 参数改为必需参数，强制调用方显式指定")
    lines.append("2. **统一目录语义**: 明确区分 `work_dir` (SDK 执行环境) 和 `output_dir` (交付物存储)")
    lines.append("3. **配置中心化**: 在 `Config` 类中统一定义输出目录策略")
    lines.append("")
    
    lines.append("### 5.3 长期方案 (Phase 3: 清理)")
    lines.append("")
    lines.append("1. **完全移除 os.chdir()**: 所有测试使用依赖注入模式")
    lines.append("2. **路径抽象层**: 引入 `PathResolver` 统一处理相对/绝对路径")
    lines.append("3. **审计机制**: 添加运行时路径使用审计，防止隐式依赖")
    lines.append("")
    
    # 跟踪指标
    lines.append("## 6. 建议跟踪指标")
    lines.append("")
    lines.append("| 指标 | 当前值 | 目标值 |")
    lines.append("|------|--------|--------|")
    lines.append(f"| 生产代码 Path.cwd() 使用 | {prod_cwd} | 0 |")
    lines.append(f"| 测试代码 os.chdir() 使用 | {chdir_count} | 0 |")
    lines.append(f"| 显式 output_dir 注入率 | ~50% | 100% |")
    lines.append("| 路径相关测试失败率 | 未知 | <1% |")
    lines.append("")
    
    # 参考
    lines.append("## 7. 参考")
    lines.append("")
    lines.append("- 原始技术债评估: `docs/evaluation/2026-03-18-docuswarm-technical-debt-detailed-assessment.md`")
    lines.append("- TD-4 描述: 输出目录/工作目录隐式耦合，需要去除全局状态化")
    lines.append("- 相关测试: `tests/tools/test_output_dir_injection.py` (已部分修复)")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("**报告生成时间**: 2026-03-25")
    lines.append("**分析工具**: `tools/td4_path_cwd_analyzer.py`")
    lines.append("")
    
    return "\n".join(lines)


def main() -> int:
    """主函数."""
    parser = argparse.ArgumentParser(
        description="TD-4: Path.cwd() 隐式依赖深度分析工具"
    )
    parser.add_argument(
        "--scan-codebase",
        action="store_true",
        help="扫描所有 Path.cwd() 使用点",
    )
    parser.add_argument(
        "--analyze-chain",
        action="store_true",
        help="分析目录传递链",
    )
    parser.add_argument(
        "--check-tests",
        action="store_true",
        help="检查测试中的 os.chdir()",
    )
    parser.add_argument(
        "--full-analysis",
        action="store_true",
        help="执行完整分析",
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="生成研究报告",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="报告输出路径",
    )
    
    args = parser.parse_args()
    
    # 如果没有指定任何操作，默认执行完整分析
    if not any([args.scan_codebase, args.analyze_chain, args.check_tests, 
                args.full_analysis, args.generate_report]):
        args.full_analysis = True
    
    result = TD4AnalysisResult()
    
    if args.scan_codebase or args.full_analysis:
        print("[SCAN] 扫描 Path.cwd() 使用点...")
        result.path_cwd_usages = scan_path_cwd_usages()
        print(f"   发现 {len(result.path_cwd_usages)} 处")
    
    if args.check_tests or args.full_analysis:
        print("[SCAN] 检查测试中的 os.chdir()...")
        result.chdir_usages = scan_chdir_usages()
        print(f"   发现 {len(result.chdir_usages)} 处")
    
    if args.analyze_chain or args.full_analysis:
        print("[SCAN] 分析目录传递链...")
        result.directory_chains = analyze_directory_chain()
        print(f"   发现 {len(result.directory_chains)} 个环节")
    
    if args.full_analysis:
        result.findings = generate_findings(result)
        print_analysis(result)
    
    if args.generate_report or args.output:
        if not result.path_cwd_usages:
            result.path_cwd_usages = scan_path_cwd_usages()
        if not result.chdir_usages:
            result.chdir_usages = scan_chdir_usages()
        if not result.directory_chains:
            result.directory_chains = analyze_directory_chain()
        if not result.findings:
            result.findings = generate_findings(result)
        
        report = generate_markdown_report(result)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding="utf-8")
            print(f"\n[REPORT] 报告已保存到: {output_path}")
        else:
            print(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
