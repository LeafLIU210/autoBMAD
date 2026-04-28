#!/usr/bin/env python3
"""
配置语义混杂（Kimi/Claude 命名债）深度分析工具

用途：分析 DocuSwarm 项目中配置命名不一致问题（P1-2技术债）
重点关注：
1. KIMI_API_KEY vs ANTHROPIC_API_KEY 混用
2. 配置层与会话层的命名不一致
3. claude-agent-sdk 架构下的配置漂移
"""

from __future__ import annotations

import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ConfigUsageFinding:
    """配置使用发现记录"""
    file_path: str
    line_number: int
    config_name: str
    context: str  # 使用上下文：'config_layer', 'session_layer', 'docs', 'other'
    usage_type: str  # 'read', 'write', 'default', 'doc_reference'
    code_snippet: str
    recommendation: str = ""


@dataclass
class ConfigSemanticsReport:
    """配置语义分析报告"""
    kimi_api_key_usages: list[ConfigUsageFinding] = field(default_factory=list)
    anthropic_api_key_usages: list[ConfigUsageFinding] = field(default_factory=list)
    claude_api_key_usages: list[ConfigUsageFinding] = field(default_factory=list)
    kimi_base_url_usages: list[ConfigUsageFinding] = field(default_factory=list)
    anthropic_base_url_usages: list[ConfigUsageFinding] = field(default_factory=list)
    claude_base_url_usages: list[ConfigUsageFinding] = field(default_factory=list)
    
    # 架构层次分析
    config_layer_findings: list[ConfigUsageFinding] = field(default_factory=list)
    session_layer_findings: list[ConfigUsageFinding] = field(default_factory=list)
    docs_findings: list[ConfigUsageFinding] = field(default_factory=list)
    
    # 问题统计
    total_inconsistencies: int = 0
    critical_issues: int = 0
    warning_issues: int = 0


def find_config_in_file(file_path: Path, config_patterns: dict[str, str]) -> list[ConfigUsageFinding]:
    """在文件中查找配置使用情况"""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception:
        return findings
    
    for line_num, line in enumerate(lines, 1):
        for config_name, pattern in config_patterns.items():
            if re.search(pattern, line):
                # 确定上下文
                context = 'other'
                if 'config' in str(file_path).lower() or 'config.py' in str(file_path):
                    context = 'config_layer'
                elif 'session' in str(file_path).lower() or 'llm/' in str(file_path):
                    context = 'session_layer'
                elif file_path.suffix == '.md':
                    context = 'docs'
                
                # 确定使用类型
                usage_type = 'reference'
                if 'os.environ.get' in line or 'os.getenv' in line:
                    usage_type = 'read'
                elif '=' in line and ('default' in line.lower() or 'DEFAULT' in line):
                    usage_type = 'default'
                elif 'os.environ[' in line or 'os.environ.set' in line:
                    usage_type = 'write'
                
                finding = ConfigUsageFinding(
                    file_path=str(file_path),
                    line_number=line_num,
                    config_name=config_name,
                    context=context,
                    usage_type=usage_type,
                    code_snippet=line.strip()[:100]
                )
                findings.append(finding)
    
    return findings


def analyze_python_config_usage(file_path: Path) -> dict[str, Any]:
    """分析 Python 文件中的配置使用（AST分析）"""
    results = {
        'env_reads': [],
        'class_configs': [],
        'init_params': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except Exception:
        return results
    
    for node in ast.walk(tree):
        # 查找 os.environ.get/os.getenv 调用
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['get', 'getenv']:
                    if isinstance(node.args, list) and len(node.args) > 0:
                        if isinstance(node.args[0], ast.Constant):
                            env_var = node.args[0].value
                            if isinstance(env_var, str) and ('API_KEY' in env_var or 'BASE_URL' in env_var):
                                results['env_reads'].append({
                                    'var': env_var,
                                    'line': node.lineno
                                })
        
        # 查找类定义中的配置字段
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name):
                        if 'api_key' in item.target.id or 'base_url' in item.target.id:
                            results['class_configs'].append({
                                'class': node.name,
                                'field': item.target.id,
                                'line': item.lineno
                            })
    
    return results


def analyze_config_py(file_path: Path = Path("autoBMAD/docuswarm/config.py")) -> dict[str, Any]:
    """深度分析 config.py 文件"""
    analysis = {
        'env_vars_used': [],
        'default_values': {},
        'validation_logic': [],
        'issues': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        analysis['issues'].append(f"File not found: {file_path}")
        return analysis
    
    # 查找环境变量引用
    env_patterns = [
        (r'os\.environ\.get\(["\']([^"\']*?)["\']', 'os.environ.get'),
        (r'os\.getenv\(["\']([^"\']*?)["\']', 'os.getenv'),
    ]
    
    for pattern, method in env_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            env_var = match.group(1)
            analysis['env_vars_used'].append({
                'var': env_var,
                'method': method
            })
    
    # 查找默认值
    default_patterns = [
        (r'DEFAULT_(\w+)\s*=\s*["\']([^"\']+)["\']', 'string'),
        (r'DEFAULT_(\w+)\s*=\s*(\d+)', 'int'),
    ]
    
    for pattern, ptype in default_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            key = match.group(1)
            value = match.group(2)
            analysis['default_values'][key] = {'value': value, 'type': ptype}
    
    # 检查关键问题
    if 'KIMI_API_KEY' in content and 'ANTHROPIC_API_KEY' not in content:
        analysis['issues'].append({
            'severity': 'HIGH',
            'message': 'config.py 只使用 KIMI_API_KEY，未支持 ANTHROPIC_API_KEY',
            'recommendation': '添加对 ANTHROPIC_API_KEY 的支持，作为 claude-agent-sdk 的标准配置'
        })
    
    if 'KIMI_BASE_URL' in content and 'ANTHROPIC_BASE_URL' not in content:
        analysis['issues'].append({
            'severity': 'HIGH', 
            'message': 'config.py 只使用 KIMI_BASE_URL，未支持 ANTHROPIC_BASE_URL',
            'recommendation': '添加对 ANTHROPIC_BASE_URL 的支持'
        })
    
    return analysis


def analyze_session_manager(file_path: Path = Path("autoBMAD/docuswarm/llm/session_manager.py")) -> dict[str, Any]:
    """深度分析 session_manager.py 文件"""
    analysis = {
        'env_vars_used': [],
        'unused_fields': [],
        'issues': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        analysis['issues'].append(f"File not found: {file_path}")
        return analysis
    
    # 检查环境变量使用
    if 'CLAUDE_API_KEY' in content:
        analysis['env_vars_used'].append('CLAUDE_API_KEY')
    if 'ANTHROPIC_API_KEY' in content:
        analysis['env_vars_used'].append('ANTHROPIC_API_KEY')
    if 'KIMI_API_KEY' in content:
        analysis['env_vars_used'].append('KIMI_API_KEY')
    
    # 检查 _api_key/_base_url 是否被消费
    init_pattern = r'self\._api_key\s*=.*?(?:CLAUDE_API_KEY|ANTHROPIC_API_KEY)'
    usage_pattern = r'self\._api_key(?!\s*=)'
    
    init_matches = list(re.finditer(init_pattern, content))
    usage_matches = list(re.finditer(usage_pattern, content))
    
    if init_matches and len(usage_matches) <= 1:  # 只有初始化，没有其他使用
        analysis['unused_fields'].append('_api_key')
        analysis['issues'].append({
            'severity': 'MEDIUM',
            'message': '_api_key 字段在 SessionManager 中被初始化但未被消费',
            'recommendation': '确认 claude-agent-sdk 是否需要显式传入 api_key，或移除未使用的字段'
        })
    
    # 检查 _base_url 使用
    base_url_init = r'self\._base_url\s*=' in content
    base_url_usage = len(re.findall(r'self\._base_url(?!\s*=)', content)) > 0
    
    if base_url_init and not base_url_usage:
        analysis['unused_fields'].append('_base_url')
        analysis['issues'].append({
            'severity': 'MEDIUM',
            'message': '_base_url 字段在 SessionManager 中被初始化但可能未被消费',
            'recommendation': '检查 ClaudeAgentOptions 是否使用 _base_url'
        })
    
    return analysis


def generate_report(project_root: Path = Path(".")) -> ConfigSemanticsReport:
    """生成完整的配置语义分析报告"""
    report = ConfigSemanticsReport()
    
    # 定义要搜索的配置模式
    config_patterns = {
        'KIMI_API_KEY': r'KIMI_API_KEY',
        'ANTHROPIC_API_KEY': r'ANTHROPIC_API_KEY',
        'CLAUDE_API_KEY': r'CLAUDE_API_KEY',
        'KIMI_BASE_URL': r'KIMI_BASE_URL',
        'ANTHROPIC_BASE_URL': r'ANTHROPIC_BASE_URL',
        'CLAUDE_BASE_URL': r'CLAUDE_BASE_URL',
    }
    
    # 搜索文件
    search_paths = [
        Path("autoBMAD/docuswarm"),
        Path("autoBMAD/epic_automation"),
        Path("docs"),
        Path("."),
    ]
    
    for search_path in search_paths:
        if not (project_root / search_path).exists():
            continue
            
        for ext in ['*.py', '*.md', '*.yaml', '*.yml', '*.json', '*.sh']:
            for file_path in (project_root / search_path).rglob(ext):
                if 'venv' in str(file_path) or '.git' in str(file_path):
                    continue
                    
                findings = find_config_in_file(file_path, config_patterns)
                
                for finding in findings:
                    if finding.config_name == 'KIMI_API_KEY':
                        report.kimi_api_key_usages.append(finding)
                    elif finding.config_name == 'ANTHROPIC_API_KEY':
                        report.anthropic_api_key_usages.append(finding)
                    elif finding.config_name == 'CLAUDE_API_KEY':
                        report.claude_api_key_usages.append(finding)
                    elif finding.config_name == 'KIMI_BASE_URL':
                        report.kimi_base_url_usages.append(finding)
                    elif finding.config_name == 'ANTHROPIC_BASE_URL':
                        report.anthropic_base_url_usages.append(finding)
                    elif finding.config_name == 'CLAUDE_BASE_URL':
                        report.claude_base_url_usages.append(finding)
                    
                    # 按上下文分类
                    if finding.context == 'config_layer':
                        report.config_layer_findings.append(finding)
                    elif finding.context == 'session_layer':
                        report.session_layer_findings.append(finding)
                    elif finding.context == 'docs':
                        report.docs_findings.append(finding)
    
    # 统计问题
    report.total_inconsistencies = (
        len(report.kimi_api_key_usages) + 
        len(report.anthropic_api_key_usages) +
        len(report.claude_api_key_usages)
    )
    
    return report


def print_report(report: ConfigSemanticsReport, detailed: bool = False) -> None:
    """打印分析报告"""
    print("=" * 80)
    print("DocuSwarm 配置语义混杂（Kimi/Claude 命名债）深度分析报告")
    print("=" * 80)
    print()
    
    # 汇总统计
    print("【汇总统计】")
    print(f"  KIMI_API_KEY 使用次数: {len(report.kimi_api_key_usages)}")
    print(f"  ANTHROPIC_API_KEY 使用次数: {len(report.anthropic_api_key_usages)}")
    print(f"  CLAUDE_API_KEY 使用次数: {len(report.claude_api_key_usages)}")
    print(f"  KIMI_BASE_URL 使用次数: {len(report.kimi_base_url_usages)}")
    print(f"  ANTHROPIC_BASE_URL 使用次数: {len(report.anthropic_base_url_usages)}")
    print(f"  CLAUDE_BASE_URL 使用次数: {len(report.claude_base_url_usages)}")
    print(f"  总计不一致项: {report.total_inconsistencies}")
    print()
    
    # 架构层次分析
    print("【架构层次分布】")
    print(f"  配置层 (config_layer): {len(report.config_layer_findings)} 处")
    print(f"  会话层 (session_layer): {len(report.session_layer_findings)} 处")
    print(f"  文档层 (docs): {len(report.docs_findings)} 处")
    print()
    
    if detailed:
        # 详细列出配置层发现
        if report.config_layer_findings:
            print("【配置层详细发现】")
            for finding in report.config_layer_findings[:20]:  # 限制显示数量
                print(f"  {finding.file_path}:{finding.line_number}")
                print(f"    配置: {finding.config_name} | 类型: {finding.usage_type}")
                print(f"    代码: {finding.code_snippet}")
                print()
        
        # 详细列出会话层发现
        if report.session_layer_findings:
            print("【会话层详细发现】")
            for finding in report.session_layer_findings[:20]:
                print(f"  {finding.file_path}:{finding.line_number}")
                print(f"    配置: {finding.config_name} | 类型: {finding.usage_type}")
                print(f"    代码: {finding.code_snippet}")
                print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='分析 DocuSwarm 配置语义混杂问题'
    )
    parser.add_argument(
        '--detailed', '-d',
        action='store_true',
        help='显示详细报告'
    )
    parser.add_argument(
        '--config-analysis', '-c',
        action='store_true',
        help='深度分析 config.py'
    )
    parser.add_argument(
        '--session-analysis', '-s',
        action='store_true',
        help='深度分析 session_manager.py'
    )
    
    args = parser.parse_args()
    
    project_root = Path(".")
    
    # 深度分析特定文件
    if args.config_analysis:
        print("=" * 80)
        print("深度分析: autoBMAD/docuswarm/config.py")
        print("=" * 80)
        analysis = analyze_config_py()
        print(f"\n环境变量使用: {analysis['env_vars_used']}")
        print(f"\n默认值定义: {analysis['default_values']}")
        print(f"\n发现的问题:")
        for issue in analysis['issues']:
            print(f"  [{issue['severity']}] {issue['message']}")
            print(f"    建议: {issue['recommendation']}")
        print()
    
    if args.session_analysis:
        print("=" * 80)
        print("深度分析: autoBMAD/docuswarm/llm/session_manager.py")
        print("=" * 80)
        analysis = analyze_session_manager()
        print(f"\n环境变量使用: {analysis['env_vars_used']}")
        print(f"\n未使用字段: {analysis['unused_fields']}")
        print(f"\n发现的问题:")
        for issue in analysis['issues']:
            print(f"  [{issue['severity']}] {issue['message']}")
            print(f"    建议: {issue['recommendation']}")
        print()
    
    # 生成完整报告
    report = generate_report(project_root)
    print_report(report, detailed=args.detailed)
    
    return report


if __name__ == "__main__":
    main()
