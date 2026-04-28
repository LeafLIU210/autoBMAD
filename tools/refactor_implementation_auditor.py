#!/usr/bin/env python3
"""
DocuSwarm 重构实现审计工具

用于验证以下要求的实现状态：
1. Claude Agent SDK system_prompt preset/append 高级结构
2. node.yaml evaluator 内联引用段
3. 主执行链 SessionManager 的 node_id 和 tool_permissions 接入
4. tests/__init__.py 语法错误
5. NodeDeliverableConfig 的 template_title、output_filename、format_hints 支持

用法:
    python tools/refactor_implementation_auditor.py
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class Status(Enum):
    """审计状态"""
    PASS = "[PASS]"
    FAIL = "[FAIL]"
    WARNING = "[WARN]"
    NOT_FOUND = "[N/A]"


@dataclass
class AuditResult:
    """审计结果"""
    requirement: str
    status: Status
    detail: str
    file_path: str | None = None
    line_number: int | None = None
    suggestion: str | None = None


class RefactorImplementationAuditor:
    """重构实现审计器"""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).parent.parent
        self.results: list[AuditResult] = []

    def audit_all(self) -> list[AuditResult]:
        """执行所有审计检查"""
        self.audit_system_prompt_structure()
        self.audit_evaluator_inline_config()
        self.audit_session_manager_injection()
        self.audit_tests_init_syntax()
        self.audit_deliverable_config_fields()
        return self.results

    def audit_system_prompt_structure(self) -> None:
        """审计 1: system_prompt preset/append 高级结构"""
        req = "1. Claude Agent SDK system_prompt preset/append 结构"
        
        # 检查 SessionManager._create_options 返回值
        session_manager_path = self.project_root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
        
        if not session_manager_path.exists():
            self.results.append(AuditResult(
                requirement=req,
                status=Status.NOT_FOUND,
                detail=f"SessionManager 文件不存在: {session_manager_path}",
                suggestion="检查文件路径"
            ))
            return

        content = session_manager_path.read_text(encoding="utf-8")
        
        # 检查是否使用 dict 格式的 system_prompt
        if '"type": "preset"' in content or "'type': 'preset'" in content:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.PASS,
                detail="SessionManager 已使用 preset/append 结构",
                file_path=str(session_manager_path)
            ))
        else:
            # 检查当前实现方式
            if "ClaudeAgentOptions" in content:
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.FAIL,
                    detail="SessionManager 使用字符串形式的 system_prompt，未使用 preset/append 高级结构",
                    file_path=str(session_manager_path),
                    suggestion="修改 _create_options 方法，返回 dict 格式的 system_prompt: {'type': 'preset', 'preset': 'claude_code', 'append': ...}"
                ))
            else:
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.NOT_FOUND,
                    detail="未找到 ClaudeAgentOptions 使用",
                    file_path=str(session_manager_path)
                ))

    def audit_evaluator_inline_config(self) -> None:
        """审计 2: node.yaml evaluator 内联引用段"""
        req = "2. node.yaml evaluator 内联引用段"
        
        nodes_dir = self.project_root / "nodes"
        node_yamls = list(nodes_dir.glob("*/node.yaml"))
        
        if not node_yamls:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.NOT_FOUND,
                detail=f"未找到任何 node.yaml 文件: {nodes_dir}"
            ))
            return

        # 检查 node.yaml 是否有 evaluator 字段
        nodes_with_evaluator = []
        nodes_without_evaluator = []
        
        import yaml
        
        for yaml_path in node_yamls:
            try:
                data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                if data and "evaluator" in data:
                    nodes_with_evaluator.append(yaml_path.parent.name)
                else:
                    nodes_without_evaluator.append(yaml_path.parent.name)
            except Exception as e:
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.WARNING,
                    detail=f"解析 {yaml_path} 失败: {e}",
                    file_path=str(yaml_path)
                ))

        if nodes_with_evaluator:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.PASS,
                detail=f"以下节点已配置 evaluator 字段: {', '.join(nodes_with_evaluator)}"
            ))
        
        if nodes_without_evaluator:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.FAIL,
                detail=f"以下节点缺少 evaluator 字段: {', '.join(nodes_without_evaluator)}",
                suggestion="在 node.yaml 中添加 evaluator 配置段，包含 criteria_file、threshold、max_iterations 等字段"
            ))

        # 检查 NodeLoader 是否解析 evaluator 字段
        loader_path = self.project_root / "autoBMAD" / "nodes" / "loader.py"
        if loader_path.exists():
            loader_content = loader_path.read_text(encoding="utf-8")
            if ('config.get("evaluator")' in loader_content or 
                'config["evaluator"]' in loader_content or
                'node_config.get("evaluator")' in loader_content or
                'node_config["evaluator"]' in loader_content or
                'node_config.get("evaluator", {})' in loader_content):
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.PASS,
                    detail="NodeLoader 已支持从 node.yaml 解析 evaluator 字段",
                    file_path=str(loader_path)
                ))
            else:
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.FAIL,
                    detail="NodeLoader 未从 node.yaml 解析 evaluator 字段，仍从独立 evaluator.yaml 加载",
                    file_path=str(loader_path),
                    suggestion="修改 _build_node_config 方法，从 config 中解析 evaluator 字段"
                ))

    def audit_session_manager_injection(self) -> None:
        """审计 3: 主执行链 SessionManager 的 node_id 和 tool_permissions 接入"""
        req = "3. 主执行链 SessionManager node_id/tool_permissions 接入"
        
        # 检查 IndependentAgent.execute_with_input
        independent_path = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        
        if not independent_path.exists():
            self.results.append(AuditResult(
                requirement=req,
                status=Status.NOT_FOUND,
                detail=f"IndependentAgent 文件不存在: {independent_path}"
            ))
            return

        content = independent_path.read_text(encoding="utf-8")
        
        # 检查 execute_with_input 中 SessionManager 的创建
        # 支持两种模式: 1. 直接创建 SessionManager, 2. 通过 _create_pipeline_session_manager 工厂方法
        if "_create_pipeline_session_manager" in content:
            # 新实现: 使用工厂方法
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # 检查工厂方法调用
                        if isinstance(node.func, ast.Attribute) and node.func.attr == "_create_pipeline_session_manager":
                            keywords = {kw.arg for kw in node.keywords}
                            
                            has_node_id = "node_id" in keywords
                            has_file_dirs = "file_dirs" in keywords
                            has_search_dirs = "search_dirs" in keywords
                            
                            if has_node_id and (has_file_dirs or has_search_dirs):
                                self.results.append(AuditResult(
                                    requirement=req,
                                    status=Status.PASS,
                                    detail="execute_with_input 使用工厂方法创建 SessionManager，传递了 node_id 和 file_dirs/search_dirs",
                                    file_path=str(independent_path)
                                ))
                            else:
                                missing = []
                                if not has_node_id:
                                    missing.append("node_id")
                                if not has_file_dirs and not has_search_dirs:
                                    missing.append("file_dirs/search_dirs")
                                self.results.append(AuditResult(
                                    requirement=req,
                                    status=Status.FAIL,
                                    detail=f"工厂方法缺少参数: {', '.join(missing)}",
                                    file_path=str(independent_path),
                                    suggestion=f"修改工厂方法调用，添加 {', '.join(missing)} 参数"
                                ))
                        # 检查工厂方法定义中 SessionManager 的创建
                        elif isinstance(node.func, ast.Name) and node.func.id == "SessionManager":
                            keywords = {kw.arg for kw in node.keywords}
                            
                            has_node_id = "node_id" in keywords
                            has_file_dirs = "file_dirs" in keywords
                            has_search_dirs = "search_dirs" in keywords
                            
                            if has_node_id and (has_file_dirs or has_search_dirs):
                                self.results.append(AuditResult(
                                    requirement=req,
                                    status=Status.PASS,
                                    detail="_create_pipeline_session_manager 工厂方法正确创建 SessionManager 并传递 node_id 和 file_dirs/search_dirs",
                                    file_path=str(independent_path)
                                ))
            except SyntaxError as e:
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.WARNING,
                    detail=f"AST 解析失败: {e}",
                    file_path=str(independent_path)
                ))
        elif "SessionManager(" in content:
            # 旧实现: 直接创建 SessionManager
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id == "SessionManager":
                            keywords = {kw.arg for kw in node.keywords}
                            
                            has_node_id = "node_id" in keywords
                            has_allowed_dirs = "allowed_dirs" in keywords
                            
                            if has_node_id and has_allowed_dirs:
                                self.results.append(AuditResult(
                                    requirement=req,
                                    status=Status.PASS,
                                    detail="execute_with_input 创建 SessionManager 时传递了 node_id 和 allowed_dirs",
                                    file_path=str(independent_path)
                                ))
                            else:
                                missing = []
                                if not has_node_id:
                                    missing.append("node_id")
                                if not has_allowed_dirs:
                                    missing.append("allowed_dirs")
                                self.results.append(AuditResult(
                                    requirement=req,
                                    status=Status.FAIL,
                                    detail=f"execute_with_input 创建 SessionManager 时缺少参数: {', '.join(missing)}",
                                    file_path=str(independent_path),
                                    suggestion=f"修改 SessionManager 创建代码，添加 {', '.join(missing)} 参数"
                                ))
            except SyntaxError as e:
                self.results.append(AuditResult(
                    requirement=req,
                    status=Status.WARNING,
                    detail=f"AST 解析失败: {e}",
                    file_path=str(independent_path)
                ))
        else:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.NOT_FOUND,
                detail="未在 independent.py 中找到 SessionManager 创建",
                file_path=str(independent_path)
            ))

    def audit_tests_init_syntax(self) -> None:
        """审计 4: tests/__init__.py 语法错误"""
        req = "4. tests/__init__.py 语法错误"
        
        tests_init_path = self.project_root / "tests" / "__init__.py"
        
        if not tests_init_path.exists():
            self.results.append(AuditResult(
                requirement=req,
                status=Status.NOT_FOUND,
                detail=f"tests/__init__.py 不存在: {tests_init_path}"
            ))
            return

        content = tests_init_path.read_text(encoding="utf-8")
        
        # 尝试 AST 解析
        try:
            ast.parse(content)
            self.results.append(AuditResult(
                requirement=req,
                status=Status.PASS,
                detail="tests/__init__.py 语法正确",
                file_path=str(tests_init_path)
            ))
        except SyntaxError as e:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.FAIL,
                detail=f"tests/__init__.py 存在语法错误: {e}",
                file_path=str(tests_init_path),
                line_number=e.lineno,
                suggestion=f"将第 {e.lineno} 行改为注释格式，例如: # DocuSwarm test suite."
            ))

    def audit_deliverable_config_fields(self) -> None:
        """审计 5: NodeDeliverableConfig 扩展字段"""
        req = "5. NodeDeliverableConfig template_title/output_filename/format_hints"
        
        loader_path = self.project_root / "autoBMAD" / "nodes" / "loader.py"
        
        if not loader_path.exists():
            self.results.append(AuditResult(
                requirement=req,
                status=Status.NOT_FOUND,
                detail=f"NodeLoader 文件不存在: {loader_path}"
            ))
            return

        content = loader_path.read_text(encoding="utf-8")
        
        # 检查 NodeDeliverableConfig 定义
        required_fields = ["template_title", "output_filename", "format_hints"]
        found_fields = []
        missing_fields = []
        
        for field in required_fields:
            if field in content:
                found_fields.append(field)
            else:
                missing_fields.append(field)
        
        if not found_fields:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.FAIL,
                detail="NodeDeliverableConfig 未定义任何扩展字段 (template_title, output_filename, format_hints)",
                file_path=str(loader_path),
                suggestion="在 NodeDeliverableConfig 数据类中添加 template_title、output_filename、format_hints 字段"
            ))
        elif missing_fields:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.WARNING,
                detail=f"NodeDeliverableConfig 缺少以下字段: {', '.join(missing_fields)}",
                file_path=str(loader_path),
                suggestion=f"添加缺少的字段: {', '.join(missing_fields)}"
            ))
        else:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.PASS,
                detail="NodeDeliverableConfig 已定义所有扩展字段",
                file_path=str(loader_path)
            ))

        # 检查 _build_node_config 是否解析这些字段
        if "template_title" in content and "deliverable_data.get" in content:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.PASS,
                detail="_build_node_config 已解析 deliverable 扩展字段",
                file_path=str(loader_path)
            ))
        else:
            self.results.append(AuditResult(
                requirement=req,
                status=Status.FAIL,
                detail="_build_node_config 未解析 deliverable 扩展字段",
                file_path=str(loader_path),
                suggestion="在 _build_node_config 中解析 template_title、output_filename、format_hints 并传入 NodeDeliverableConfig"
            ))

    def print_report(self) -> None:
        """打印审计报告"""
        print("=" * 80)
        print("DocuSwarm 重构实现审计报告")
        print("=" * 80)
        print()
        
        # 按要求分组
        current_req = None
        for result in self.results:
            if result.requirement != current_req:
                current_req = result.requirement
                print(f"\n{result.requirement}")
                print("-" * 40)
            
            print(f"  状态: {result.status.value}")
            print(f"  详情: {result.detail}")
            if result.file_path:
                print(f"  文件: {result.file_path}")
            if result.line_number:
                print(f"  行号: {result.line_number}")
            if result.suggestion:
                print(f"  建议: {result.suggestion}")
            print()
        
        # 统计
        pass_count = sum(1 for r in self.results if r.status == Status.PASS)
        fail_count = sum(1 for r in self.results if r.status == Status.FAIL)
        warning_count = sum(1 for r in self.results if r.status == Status.WARNING)
        not_found_count = sum(1 for r in self.results if r.status == Status.NOT_FOUND)
        
        print("=" * 80)
        print("统计")
        print("=" * 80)
        print(f"  通过: {pass_count}")
        print(f"  失败: {fail_count}")
        print(f"  警告: {warning_count}")
        print(f"  未找到: {not_found_count}")
        print()
        
        if fail_count == 0:
            print("[OK] 所有关键检查通过！")
        else:
            print(f"[ATTENTION] 有 {fail_count} 项检查失败，需要修复")


def main() -> int:
    """主入口"""
    auditor = RefactorImplementationAuditor()
    auditor.audit_all()
    auditor.print_report()
    
    # 如果有失败项，返回非零退出码
    has_failures = any(r.status == Status.FAIL for r in auditor.results)
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
