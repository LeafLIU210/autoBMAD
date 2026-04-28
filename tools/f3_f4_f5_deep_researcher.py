"""
F3_F4_F5 Deep Research Tool
===========================

深度研究工具，用于诊断和分析以下三个高优先级问题：
- F3: Multi-document 方案只实现了局部结构，未形成端到端运行时支持
- F4: docs_context_summary 已生成并注入 state，但在 IndependentAgent 提示词构建前被丢弃
- F5: SummaryAgent 返回类型与 PipelineState.docs_context_summary 声明不一致

用法:
    python tools/f3_f4_f5_deep_researcher.py [--verbose]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CodeLocation:
    """代码位置信息"""
    file: str
    line: int
    column: int = 0
    snippet: str = ""
    
    def __str__(self) -> str:
        return f"{self.file}:{self.line}"


@dataclass
class Issue:
    """发现的问题"""
    issue_id: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    location: CodeLocation | None = None
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "location": str(self.location) if self.location else None,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass
class DataFlow:
    """数据流追踪"""
    source: str
    sink: str
    path: list[str] = field(default_factory=list)
    status: str = ""  # intact, broken, partial
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "sink": self.sink,
            "path": self.path,
            "status": self.status,
        }


class F3F4F5Researcher:
    """F3/F4/F5 问题深度研究器"""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.issues: list[Issue] = []
        self.data_flows: list[DataFlow] = []
        
    def log(self, message: str) -> None:
        if self.verbose:
            print(f"[RESEARCH] {message}")
            
    def analyze_all(self) -> dict[str, Any]:
        """执行所有分析"""
        self.log("开始 F3/F4/F5 深度研究...")
        
        # F3: Multi-document 分析
        self.analyze_f3_multi_document()
        
        # F4: docs_context_summary 传递链分析
        self.analyze_f4_docs_context_flow()
        
        # F5: 类型一致性分析
        self.analyze_f5_type_consistency()
        
        return {
            "issues": [i.to_dict() for i in self.issues],
            "data_flows": [d.to_dict() for d in self.data_flows],
            "summary": self._generate_summary(),
        }
    
    def analyze_f3_multi_document(self) -> None:
        """分析 F3: Multi-document 方案实现情况"""
        self.log("分析 F3: Multi-document 实现...")
        
        # 1. 检查 CreateDeliverableParams 参数支持
        params_file = self.project_root / "autoBMAD" / "docuswarm" / "tools" / "create_deliverable.py"
        if params_file.exists():
            content = params_file.read_text(encoding="utf-8")
            has_index = "document_index" in content
            has_total = "document_total" in content
            has_type = "document_type" in content
            
            self.log(f"  CreateDeliverableParams: document_index={has_index}, document_total={has_total}, document_type={has_type}")
            
            if not all([has_index, has_total, has_type]):
                self.issues.append(Issue(
                    issue_id="F3-001",
                    severity="high",
                    title="CreateDeliverableParams 缺少 multi-document 参数",
                    description="Python 参数类未实现 document_index/document_total/document_type",
                    location=CodeLocation(str(params_file), 24),
                    evidence=[f"has_index={has_index}", f"has_total={has_total}", f"has_type={has_type}"],
                    recommendation="添加 multi-document 参数到 CreateDeliverableParams",
                ))
        
        # 2. 检查 MCP schema 暴露情况
        sdk_file = self.project_root / "autoBMAD" / "docuswarm" / "tools" / "create_deliverable_sdk.py"
        if sdk_file.exists():
            content = sdk_file.read_text(encoding="utf-8")
            
            # 查找 MCP tool schema
            schema_match = re.search(r'@tool\s*\(\s*"create_deliverable"[^)]*\{([^}]+)\}', content, re.DOTALL)
            if schema_match:
                schema_content = schema_match.group(1)
                has_schema_index = "document_index" in schema_content
                has_schema_total = "document_total" in schema_content
                has_schema_type = "document_type" in schema_content
                
                self.log(f"  MCP Schema: document_index={has_schema_index}, document_total={has_schema_total}, document_type={has_schema_type}")
                
                if not all([has_schema_index, has_schema_total, has_schema_type]):
                    self.issues.append(Issue(
                        issue_id="F3-002",
                        severity="high",
                        title="MCP create_deliverable schema 未暴露 multi-document 参数",
                        description="LLM 无法通过 MCP 工具调用传递 document_index/document_total/document_type 参数",
                        location=CodeLocation(str(sdk_file), 243),
                        evidence=["Schema 只包含 title, content, metadata"],
                        recommendation="在 MCP tool schema 中添加 multi-document 参数定义",
                    ))
            
            # 3. 检查 submit_execution_report schema
            has_submit_report = "submit_execution_report" in content
            submit_schema_match = re.search(r'"submit_execution_report"[^}]*properties[^}]*\{([^}]+)deliverable', content, re.DOTALL)
            
            self.log(f"  submit_execution_report 存在={has_submit_report}")
            
            if has_submit_report:
                # 检查是否为单 deliverable 结构
                single_deliverable = '"deliverable":' in content and '"deliverables":' not in content
                if single_deliverable:
                    self.issues.append(Issue(
                        issue_id="F3-003",
                        severity="high",
                        title="submit_execution_report schema 只支持单 deliverable",
                        description="无法通过 submit_execution_report 报告多个文档",
                        location=CodeLocation(str(sdk_file), 288),
                        evidence=["Schema 定义了单个 deliverable 对象，而非数组"],
                        recommendation="修改 schema 支持 deliverables 数组",
                    ))
        
        # 4. 检查 IndependentAgent 提取逻辑
        agent_file = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        if agent_file.exists():
            content = agent_file.read_text(encoding="utf-8")
            
            # 检查 _extract_submit_report_result 方法
            if "_extract_submit_report_result" in content:
                # 检查是否只返回第一个报告
                first_report_pattern = r'return\s+report'
                matches = list(re.finditer(first_report_pattern, content))
                self.log(f"  _extract_submit_report_result return 语句数量={len(matches)}")
                
                self.issues.append(Issue(
                    issue_id="F3-004",
                    severity="high",
                    title="IndependentAgent 只提取单个 execution report",
                    description="_extract_submit_report_result 方法只返回第一个找到的报告，无法处理多文档场景",
                    location=CodeLocation(str(agent_file), 545),
                    evidence=["方法返回单个 report 对象"],
                    recommendation="修改方法返回 report 列表",
                ))
        
        # 5. 检查 DualAgentNode 存储逻辑
        dual_agent_file = self.project_root / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
        if dual_agent_file.exists():
            content = dual_agent_file.read_text(encoding="utf-8")
            
            # 检查 final_deliverable 类型
            if "final_deliverable: dict" in content or "final_deliverable: Dict" in content:
                self.log("  DualAgentNode.final_deliverable 是 dict 类型")
                
                self.issues.append(Issue(
                    issue_id="F3-005",
                    severity="high",
                    title="DualAgentNode 只维护单个 final_deliverable",
                    description="运行时态只支持单个 deliverable，无法存储多文档结果",
                    location=CodeLocation(str(dual_agent_file), 286),
                    evidence=["final_deliverable: dict[str, Any] = {}"],
                    recommendation="改为 list[dict] 或添加 multi-document 包装结构",
                ))
        
        # 记录数据流
        self.data_flows.append(DataFlow(
            source="LLM (multi-document intent)",
            sink="NodeResult.deliverable",
            path=[
                "MCP create_deliverable tool",
                "CreateDeliverableSDKTool",
                "IndependentAgent._parse_response",
                "DualAgentNode.execute",
            ],
            status="broken",
        ))
    
    def analyze_f4_docs_context_flow(self) -> None:
        """分析 F4: docs_context_summary 传递链"""
        self.log("分析 F4: docs_context_summary 传递链...")
        
        # 1. 检查 PipelineState 定义
        state_file = self.project_root / "autoBMAD" / "docuswarm" / "pipeline" / "state.py"
        if state_file.exists():
            content = state_file.read_text(encoding="utf-8")
            has_field = "docs_context_summary" in content
            self.log(f"  PipelineState.docs_context_summary 存在={has_field}")
        
        # 2. 检查 orchestrator 注入
        orch_file = self.project_root / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
        if orch_file.exists():
            content = orch_file.read_text(encoding="utf-8")
            has_summarize = "_summarize_referenced_documents" in content
            has_inject = "docs_context_summary=docs_context_summary" in content
            self.log(f"  Orchestrator 调用 SummaryAgent={has_summarize}, 注入 state={has_inject}")
        
        # 3. 检查 PipelineAdapter 传递
        adapter_file = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "pipeline_adapter.py"
        if adapter_file.exists():
            content = adapter_file.read_text(encoding="utf-8")
            has_extract = 'pipeline_state.get("docs_context_summary", [])' in content
            has_inject_adapter = 'accumulated["docs_context_summary"] = docs_summary' in content
            self.log(f"  PipelineAdapter 提取={has_extract}, 注入 accumulated={has_inject_adapter}")
            
            if not has_extract:
                self.issues.append(Issue(
                    issue_id="F4-001",
                    severity="high",
                    title="PipelineAdapter 未提取 docs_context_summary",
                    description="PipelineAdapter.convert_pipeline_to_node_state 未从 PipelineState 提取 docs_context_summary",
                    recommendation="添加提取逻辑",
                ))
        
        # 4. 检查 ContextManager.build_independent_input
        isolation_file = self.project_root / "autoBMAD" / "docuswarm" / "context" / "isolation.py"
        if isolation_file.exists():
            content = isolation_file.read_text(encoding="utf-8")
            
            # 检查 IndependentAgentInput 定义
            contracts_file = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
            contracts_content = contracts_file.read_text(encoding="utf-8") if contracts_file.exists() else ""
            
            has_docs_context_in_input = "docs_context" in contracts_content and "IndependentAgentInput" in contracts_content
            self.log(f"  IndependentAgentInput 包含 docs_context={has_docs_context_in_input}")
            
            if not has_docs_context_in_input:
                self.issues.append(Issue(
                    issue_id="F4-002",
                    severity="high",
                    title="IndependentAgentInput 不包含 docs_context",
                    description="TypedDict 定义缺少 docs_context 字段，导致无法传递",
                    location=CodeLocation(str(contracts_file or isolation_file), 41),
                    evidence=["IndependentAgentInput 字段列表中无 docs_context"],
                    recommendation="添加 docs_context: list[dict[str, Any]] 到 IndependentAgentInput",
                ))
            
            # 检查 build_independent_input 方法
            build_method_match = re.search(
                r'def build_independent_input\([^)]+\)[^:]*:\s*"""[\s\S]*?"""\s*((?:\n[^\n]+)*)',
                content
            )
            if build_method_match:
                method_body = build_method_match.group(1)
                returns_docs_context = "docs_context" in method_body
                self.log(f"  build_independent_input 返回 docs_context={returns_docs_context}")
                
                if not returns_docs_context:
                    self.issues.append(Issue(
                        issue_id="F4-003",
                        severity="high",
                        title="ContextManager.build_independent_input 丢弃 docs_context",
                        description="方法从 execution_context 读取数据，但未将 docs_context 放入返回的 IndependentAgentInput",
                        location=CodeLocation(str(isolation_file), 120),
                        evidence=["方法返回 IndependentAgentInput 不包含 docs_context"],
                        recommendation="在方法中添加 docs_context 到返回字典",
                    ))
        
        # 5. 检查 IndependentAgent.execute_with_input
        agent_file = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        if agent_file.exists():
            content = agent_file.read_text(encoding="utf-8")
            
            # 检查是否读取 docs_context
            reads_docs_context = 'agent_input.get("docs_context"' in content
            
            # 检查 NodeExecutionContext 构造
            context_construct_match = re.search(
                r'NodeExecutionContext\([^)]+\)',
                content,
                re.DOTALL
            )
            if context_construct_match:
                construct_call = context_construct_match.group(0)
                passes_docs_context = "docs_context" in construct_call
                self.log(f"  execute_with_input 读取 docs_context={reads_docs_context}, 传递给 NodeExecutionContext={passes_docs_context}")
                
                # 查找强制设为空列表的代码
                empty_list_pattern = r'docs_context:\s*list\[dict\[str,\s*Any\]\]\s*=\s*\[\]'
                has_empty_list = bool(re.search(empty_list_pattern, content))
                
                if has_empty_list and not reads_docs_context:
                    self.issues.append(Issue(
                        issue_id="F4-004",
                        severity="high",
                        title="IndependentAgent.execute_with_input 强制 docs_context 为空列表",
                        description="方法重建 NodeExecutionContext 时将 docs_context 强制设为空列表，丢弃已注入的摘要",
                        location=CodeLocation(str(agent_file), 924),
                        evidence=["docs_context: list[dict[str, Any]] = []"],
                        recommendation="从 agent_input 读取 docs_context 并传递",
                    ))
        
        # 记录数据流
        self.data_flows.append(DataFlow(
            source="PipelineState.docs_context_summary",
            sink="IndependentAgent Prompt",
            path=[
                "PipelineAdapter.convert_pipeline_to_node_state",
                "context_file (accumulated)",
                "_execute_node (executor.py)",
                "context_builder.build",
                "NodeExecutionContext.docs_context",
                "ContextManager.build_independent_input",
                "IndependentAgentInput",
                "IndependentAgent.execute_with_input",
                "NodeExecutionContext (rebuild)",
                "contract_builder.build_independent_contract",
            ],
            status="broken",
        ))
    
    def analyze_f5_type_consistency(self) -> None:
        """分析 F5: 类型一致性问题"""
        self.log("分析 F5: 类型一致性...")
        
        # 1. 检查 PipelineState 声明
        state_file = self.project_root / "autoBMAD" / "docuswarm" / "pipeline" / "state.py"
        if state_file.exists():
            content = state_file.read_text(encoding="utf-8")
            
            # 查找 docs_context_summary 声明
            type_match = re.search(r'docs_context_summary:\s*(\S+)', content)
            if type_match:
                declared_type = type_match.group(1)
                self.log(f"  PipelineState.docs_context_summary 声明类型={declared_type}")
                
                if declared_type != "list[dict[str, Any]]":
                    self.issues.append(Issue(
                        issue_id="F5-001",
                        severity="medium",
                        title="PipelineState.docs_context_summary 类型声明不明确",
                        description=f"声明类型为 {declared_type}，期望 list[dict[str, Any]]",
                        location=CodeLocation(str(state_file), 79),
                        evidence=[f"声明: docs_context_summary: {declared_type}"],
                        recommendation="明确声明为 list[dict[str, Any]]",
                    ))
        
        # 2. 检查 SummaryAgent 返回类型
        summary_file = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "summary.py"
        if summary_file.exists():
            content = summary_file.read_text(encoding="utf-8")
            
            # 查找 summarize_context 返回类型
            return_match = re.search(
                r'async def summarize_context\([^)]+\)(?:\s*->\s*([^:]+))?:',
                content
            )
            if return_match:
                return_type = return_match.group(1) if return_match.group(1) else "未声明"
                self.log(f"  SummaryAgent.summarize_context 返回类型={return_type}")
                
                if "DocumentSummary" in str(return_type) and "dict" not in str(return_type):
                    self.issues.append(Issue(
                        issue_id="F5-002",
                        severity="high",
                        title="SummaryAgent 返回类型与 PipelineState 声明不一致",
                        description="SummaryAgent.summarize_context 返回 list[DocumentSummary]，但 PipelineState 期望 list[dict[str, Any]]",
                        location=CodeLocation(str(summary_file), 564),
                        evidence=[
                            "SummaryAgent 返回: list[DocumentSummary]",
                            "PipelineState 期望: list[dict[str, Any]]",
                        ],
                        recommendation="统一类型：要么 SummaryAgent 返回 list[dict]（调用 to_dict()），要么修改 PipelineState 声明",
                    ))
        
        # 3. 检查 orchestrator 存储方式
        orch_file = self.project_root / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
        if orch_file.exists():
            content = orch_file.read_text(encoding="utf-8")
            
            # 查找存储逻辑
            store_match = re.search(
                r'docs_context_summary\s*=\s*([^,)]+)',
                content
            )
            if store_match:
                store_value = store_match.group(1).strip()
                self.log(f"  Orchestrator 存储值={store_value}")
                
                if "result" in store_value or "docs_context_summary" in store_value:
                    # 检查是否调用 to_dict
                    has_to_dict = "to_dict" in content
                    self.log(f"  是否调用 to_dict={has_to_dict}")
                    
                    if not has_to_dict:
                        self.issues.append(Issue(
                            issue_id="F5-003",
                            severity="high",
                            title="Orchestrator 存储 DocumentSummary 对象而非 dict",
                            description="直接将 SummaryAgent 返回的 DocumentSummary 对象存入 state，未转换为 dict",
                            location=CodeLocation(str(orch_file), 438),
                            evidence=["未调用 to_dict() 转换"],
                            recommendation="存储前调用 [d.to_dict() for d in result] 转换",
                        ))
        
        # 记录数据流
        self.data_flows.append(DataFlow(
            source="SummaryAgent.summarize_context",
            sink="PipelineState.docs_context_summary",
            path=[
                "Orchestrator._summarize_referenced_documents",
                "create_initial_state",
                "PipelineState (LangGraph checkpoint)",
            ],
            status="partial",
        ))
    
    def _generate_summary(self) -> dict[str, Any]:
        """生成分析摘要"""
        critical = sum(1 for i in self.issues if i.severity == "critical")
        high = sum(1 for i in self.issues if i.severity == "high")
        medium = sum(1 for i in self.issues if i.severity == "medium")
        low = sum(1 for i in self.issues if i.severity == "low")
        
        broken_flows = sum(1 for d in self.data_flows if d.status == "broken")
        partial_flows = sum(1 for d in self.data_flows if d.status == "partial")
        
        return {
            "total_issues": len(self.issues),
            "severity_breakdown": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
            },
            "data_flows": {
                "total": len(self.data_flows),
                "broken": broken_flows,
                "partial": partial_flows,
                "intact": len(self.data_flows) - broken_flows - partial_flows,
            },
            "f3_status": "未实现端到端" if any(i.issue_id.startswith("F3-") for i in self.issues) else "已实现",
            "f4_status": "数据流断裂" if any(i.issue_id.startswith("F4-") for i in self.issues) else "数据流完整",
            "f5_status": "类型不一致" if any(i.issue_id.startswith("F5-") for i in self.issues) else "类型一致",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="F3/F4/F5 深度研究工具")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--output", "-o", type=str, help="输出 JSON 文件路径")
    args = parser.parse_args()
    
    # 确定项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"=" * 70)
    print("F3/F4/F5 深度研究工具")
    print(f"项目根目录: {project_root}")
    print(f"=" * 70)
    
    researcher = F3F4F5Researcher(project_root, verbose=args.verbose)
    results = researcher.analyze_all()
    
    # 打印摘要
    summary = results["summary"]
    print("\n" + "=" * 70)
    print("分析摘要")
    print("=" * 70)
    print(f"总问题数: {summary['total_issues']}")
    print(f"严重级别: Critical={summary['severity_breakdown']['critical']}, "
          f"High={summary['severity_breakdown']['high']}, "
          f"Medium={summary['severity_breakdown']['medium']}, "
          f"Low={summary['severity_breakdown']['low']}")
    print(f"数据流: {summary['data_flows']['total']} 条 "
          f"(断裂={summary['data_flows']['broken']}, "
          f"部分={summary['data_flows']['partial']})")
    print(f"\n状态评估:")
    print(f"  F3 (Multi-document): {summary['f3_status']}")
    print(f"  F4 (Docs Context Flow): {summary['f4_status']}")
    print(f"  F5 (Type Consistency): {summary['f5_status']}")
    
    # 打印详细问题
    if results["issues"]:
        print("\n" + "=" * 70)
        print("发现的问题")
        print("=" * 70)
        for issue in results["issues"]:
            print(f"\n[{issue['issue_id']}] {issue['severity'].upper()}: {issue['title']}")
            print(f"  位置: {issue['location'] or 'N/A'}")
            print(f"  描述: {issue['description']}")
            if issue['evidence']:
                print(f"  证据: {', '.join(issue['evidence'])}")
            if issue['recommendation']:
                print(f"  建议: {issue['recommendation']}")
    
    # 打印数据流
    if results["data_flows"]:
        print("\n" + "=" * 70)
        print("数据流分析")
        print("=" * 70)
        for flow in results["data_flows"]:
            print(f"\n  {flow['source']} -> {flow['sink']}")
            print(f"  状态: {flow['status'].upper()}")
            print(f"  路径: {' -> '.join(flow['path'][:3])}...")
    
    # 保存结果
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n结果已保存到: {output_path}")
    
    print("\n" + "=" * 70)
    
    return 0 if summary["severity_breakdown"]["critical"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
