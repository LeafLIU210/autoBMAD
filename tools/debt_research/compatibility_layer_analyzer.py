#!/usr/bin/env python3
"""
兼容层深度分析工具 - Finding B 研究

此工具用于分析 DocuSwarm 中兼容层的分布、影响和清理优先级。
根据技术债审查报告 Finding B: "兼容层仍然停留在主路径，增加理解成本和行为分叉"

使用方法:
    python tools/debt_research/compatibility_layer_analyzer.py
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CompatibilityPattern:
    """兼容层模式定义"""
    name: str
    pattern: str
    category: str  # 'parameter', 'property', 'method', 'alias', 'module', 'exception', 'data'
    severity: str  # 'high', 'medium', 'low'
    description: str


@dataclass
class CompatibilityFinding:
    """兼容层发现记录"""
    file_path: Path
    line_number: int
    pattern_name: str
    category: str
    severity: str
    code_snippet: str
    context: str
    recommendation: str


# 定义需要检测的兼容层模式
COMPATIBILITY_PATTERNS = [
    # 参数级兼容
    CompatibilityPattern(
        name="deprecated_parameter",
        pattern=r"deprecated.*use\s+(\w+)",
        category="parameter",
        severity="high",
        description="Deprecated 参数仍被接受，建议直接移除并强制使用新参数"
    ),
    CompatibilityPattern(
        name="allowed_dirs_fallback",
        pattern=r"allowed_dirs.*backward compatibility",
        category="parameter",
        severity="high",
        description="allowed_dirs 回退到 file_dirs，应直接移除兼容逻辑"
    ),
    
    # 属性级兼容
    CompatibilityPattern(
        name="deprecated_property",
        pattern=r"def allowed_dirs.*deprecated",
        category="property",
        severity="medium",
        description="Deprecated 属性仍被暴露"
    ),
    
    # 方法级兼容
    CompatibilityPattern(
        name="legacy_normalizer",
        pattern=r"_normalize_legacy",
        category="method",
        severity="high",
        description="Legacy 数据规范化方法，说明新旧格式转换仍在主路径"
    ),
    CompatibilityPattern(
        name="legacy_builder",
        pattern=r"_build.*_from_legacy",
        category="method",
        severity="high",
        description="从 legacy 参数构建新对象的桥接方法"
    ),
    
    # 模块级兼容
    CompatibilityPattern(
        name="reexport_facade",
        pattern=r"backward compatibility.*autoBMAD",
        category="module",
        severity="medium",
        description="重导出 facade 模式，用于兼容旧导入路径"
    ),
    
    # 别名兼容
    CompatibilityPattern(
        name="function_alias",
        pattern=r"adapt_to_sdk|adapt_from_sdk",
        category="alias",
        severity="low",
        description="函数别名用于兼容旧 API"
    ),
    
    # 数据级兼容
    CompatibilityPattern(
        name="state_field_keep",
        pattern=r"Keep state field for backward compatibility",
        category="data",
        severity="medium",
        description="保留冗余 state 字段用于兼容"
    ),
    
    # 异常兼容
    CompatibilityPattern(
        name="exception_alias",
        pattern=r"backward compatibility.*exception|exception.*backward compatibility",
        category="exception",
        severity="low",
        description="异常类保留用于兼容"
    ),
    
    # 调用级兼容
    CompatibilityPattern(
        name="legacy_execute_bridge",
        pattern=r"execute.*_build_execution_context_from_legacy",
        category="method",
        severity="high",
        description="execute() 方法仍通过 legacy bridge 调用"
    ),
    
    # CLI 兼容
    CompatibilityPattern(
        name="cli_alias",
        pattern=r"Backward compatibility alias",
        category="alias",
        severity="low",
        description="CLI 命令别名"
    ),
]


class CompatibilityLayerAnalyzer:
    """兼容层分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.source_dir = project_root / "autoBMAD" / "docuswarm"
        self.findings: list[CompatibilityFinding] = []
        self.category_stats: dict[str, dict] = {}
        
    def analyze(self) -> None:
        """执行完整分析"""
        print("=" * 80)
        print("Finding B: 兼容层深度分析")
        print("=" * 80)
        print()
        
        # 1. 扫描所有 Python 文件
        python_files = list(self.source_dir.rglob("*.py"))
        print(f"扫描文件数: {len(python_files)}")
        print()
        
        # 2. 分析每个文件
        for py_file in sorted(python_files):
            self._analyze_file(py_file)
        
        # 3. 生成报告
        self._generate_report()
        
    def _analyze_file(self, file_path: Path) -> None:
        """分析单个文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for line_num, line in enumerate(lines, 1):
                for pattern in COMPATIBILITY_PATTERNS:
                    if re.search(pattern.pattern, line, re.IGNORECASE):
                        finding = CompatibilityFinding(
                            file_path=file_path.relative_to(self.project_root),
                            line_number=line_num,
                            pattern_name=pattern.name,
                            category=pattern.category,
                            severity=pattern.severity,
                            code_snippet=line.strip(),
                            context=self._get_context(lines, line_num),
                            recommendation=self._get_recommendation(pattern, line)
                        )
                        self.findings.append(finding)
                        
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
    
    def _get_context(self, lines: list[str], line_num: int, context_lines: int = 3) -> str:
        """获取代码上下文"""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        context = []
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            context.append(f"{marker}{i+1:4d}: {lines[i]}")
        return "\n".join(context)
    
    def _get_recommendation(self, pattern: CompatibilityPattern, code_line: str) -> str:
        """根据模式生成具体建议"""
        recommendations = {
            "deprecated_parameter": (
                "1. 移除 deprecated 参数\n"
                "2. 更新所有调用方使用新参数\n"
                "3. 添加静态检查防止回退"
            ),
            "allowed_dirs_fallback": (
                "1. 移除 allowed_dirs 参数\n"
                "2. 强制使用 file_dirs\n"
                "3. 更新文档和示例"
            ),
            "deprecated_property": (
                "1. 移除 allowed_dirs 属性\n"
                "2. 更新依赖该属性的代码\n"
                "3. 使用 deprecation 警告"
            ),
            "legacy_normalizer": (
                "1. 统一数据输入格式\n"
                "2. 在边界处转换，不在核心逻辑\n"
                "3. 逐步移除对旧格式的支持"
            ),
            "legacy_builder": (
                "1. 统一使用 NodeExecutionContext\n"
                "2. 移除 execute() 的 legacy 参数支持\n"
                "3. 所有调用方迁移到 execute_with_context()"
            ),
            "reexport_facade": (
                "1. 更新所有导入语句\n"
                "2. 添加 deprecation 警告到 facade\n"
                "3. 计划移除 facade 模块"
            ),
            "function_alias": (
                "1. 更新所有调用使用新函数名\n"
                "2. 添加 deprecation 警告\n"
                "3. 计划移除别名"
            ),
            "state_field_keep": (
                "1. 识别依赖 state 字段的代码\n"
                "2. 更新使用新结构\n"
                "3. 移除冗余字段"
            ),
            "exception_alias": (
                "1. 统一使用新异常类型\n"
                "2. 更新 except 子句\n"
                "3. 计划移除旧异常"
            ),
            "legacy_execute_bridge": (
                "1. 直接调用 execute_with_context()\n"
                "2. 移除 execute() 的 legacy 桥接\n"
                "3. 在调用方构建 NodeExecutionContext"
            ),
            "cli_alias": (
                "1. 更新脚本和文档\n"
                "2. 添加 deprecation 警告\n"
                "3. 计划移除别名"
            ),
        }
        return recommendations.get(pattern.name, "需要具体分析")
    
    def _generate_report(self) -> None:
        """生成分析报告"""
        # 按类别分组
        findings_by_category: dict[str, list[CompatibilityFinding]] = {}
        for finding in self.findings:
            if finding.category not in findings_by_category:
                findings_by_category[finding.category] = []
            findings_by_category[finding.category].append(finding)
        
        # 按严重性分组
        findings_by_severity: dict[str, list[CompatibilityFinding]] = {
            "high": [], "medium": [], "low": []
        }
        for finding in self.findings:
            findings_by_severity[finding.severity].append(finding)
        
        # 按文件分组
        findings_by_file: dict[Path, list[CompatibilityFinding]] = {}
        for finding in self.findings:
            if finding.file_path not in findings_by_file:
                findings_by_file[finding.file_path] = []
            findings_by_file[finding.file_path].append(finding)
        
        print("=" * 80)
        print("一、兼容层统计概览")
        print("=" * 80)
        print(f"\n总计发现兼容层标记: {len(self.findings)} 处")
        print(f"\n按严重性分布:")
        print(f"  - 高风险 (high): {len(findings_by_severity['high'])} 处")
        print(f"  - 中风险 (medium): {len(findings_by_severity['medium'])} 处")
        print(f"  - 低风险 (low): {len(findings_by_severity['low'])} 处")
        print(f"\n按类别分布:")
        for category, items in sorted(findings_by_category.items()):
            print(f"  - {category}: {len(items)} 处")
        print(f"\n涉及文件数: {len(findings_by_file)} 个")
        
        print()
        print("=" * 80)
        print("二、主路径兼容层分析 (高风险)")
        print("=" * 80)
        
        # 重点关注主路径上的兼容层
        main_path_files = [
            "llm/session_manager.py",
            "nodes/dual_agent.py",
            "context/validator.py",
            "pipeline/orchestrator.py",
            "storage/state_manager.py",
        ]
        
        for file_pattern in main_path_files:
            print(f"\n>>> {file_pattern}")
            print("-" * 60)
            file_findings = [
                f for f in self.findings 
                if file_pattern in str(f.file_path) and f.severity == "high"
            ]
            if file_findings:
                for finding in file_findings:
                    print(f"\n  [{finding.pattern_name}] 第 {finding.line_number} 行")
                    print(f"  代码: {finding.code_snippet[:80]}")
                    print(f"  建议:")
                    for line in finding.recommendation.split("\n"):
                        print(f"    {line}")
            else:
                print("  (无高风险兼容层标记)")
        
        print()
        print("=" * 80)
        print("三、关键文件详细分析")
        print("=" * 80)
        
        # 对最关键的 3 个文件进行深度分析
        critical_files = [
            Path("autoBMAD/docuswarm/llm/session_manager.py"),
            Path("autoBMAD/docuswarm/nodes/dual_agent.py"),
            Path("autoBMAD/docuswarm/context/validator.py"),
        ]
        
        for critical_file in critical_files:
            self._deep_analyze_file(critical_file)
        
        print()
        print("=" * 80)
        print("四、清理优先级建议")
        print("=" * 80)
        
        print("""
【P0 - 立即清理】主路径上的高危兼容层

1. SessionManager 的 legacy 参数 (api_key, base_url, allowed_dirs)
   - 影响: 所有会话创建
   - 行动: 移除参数，强制使用 config 对象
   - 预估工作量: 2-3 天

2. DualAgentNode.execute() 的 legacy 桥接
   - 影响: 节点执行主路径
   - 行动: 移除 execute() 的 legacy 支持，统一使用 execute_with_context()
   - 预估工作量: 3-5 天

【P1 - 近期清理】影响理解成本的兼容层

3. context/validator.py 的 node_id 参数
   - 行动: 移除兼容参数
   - 预估工作量: 1 天

4. storage/state_manager.py 的 state 字段保留
   - 行动: 识别依赖后移除
   - 预估工作量: 2 天

【P2 - 计划清理】边缘兼容层

5. nodes/loader.py re-export facade
6. tools/ 中的 function-style API
7. 异常类兼容保留
8. CLI 命令别名
        """)
        
        print()
        print("=" * 80)
        print("五、行为分叉风险分析")
        print("=" * 80)
        
        print("""
当前兼容层导致的行为分叉:

1. 【参数处理分叉】
   SessionManager 同时接受:
   - 新方式: config 对象 + tool_permissions
   - 旧方式: api_key + base_url + allowed_dirs
   → 两种路径的参数合并逻辑可能产生不同结果

2. 【执行入口分叉】
   DualAgentNode 提供:
   - 新方式: execute_with_context(NodeExecutionContext)
   - 旧方式: execute(subject_context, task, pipeline_id)
   → execute() 内部通过 _build_execution_context_from_legacy 转换
   → 转换过程可能丢失或改变数据

3. 【数据模型分叉】
   PipelineState 同时包含:
   - 扁平化字段 (new)
   - state 字段保留完整 dict (legacy)
   → 两处数据可能不一致

4. 【工具权限分叉】
   工具权限配置:
   - 新方式: NodeToolPermissions 对象
   - 旧方式: allowed_dirs 列表
   → 两种方式的权限范围计算可能不同
        """)
        
    def _deep_analyze_file(self, file_path: Path) -> None:
        """深度分析单个文件"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            return
            
        print(f"\n>>> {file_path}")
        print("-" * 60)
        
        try:
            content = full_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            # 分析函数参数
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._analyze_function_args(node, file_path)
                    
        except Exception as e:
            print(f"  解析错误: {e}")
    
    def _analyze_function_args(self, func: ast.FunctionDef, file_path: Path) -> None:
        """分析函数参数中的兼容层"""
        # 检查是否有 deprecated 相关的参数默认值或注解
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if "deprecated" in decorator.func.id.lower():
                        print(f"  [装饰器] {func.name} - 使用 deprecated 装饰器")


def main():
    """主入口"""
    project_root = Path(__file__).parent.parent.parent
    analyzer = CompatibilityLayerAnalyzer(project_root)
    analyzer.analyze()


if __name__ == "__main__":
    main()
