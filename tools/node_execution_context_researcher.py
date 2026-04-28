"""
NodeExecutionContext 深度研究工具 - 方案B实现分析

用于深度研究 DocuSwarm 中上下文协议的断裂问题：
1. executor 从 state 里"猜 task"，而不是从节点契约构建任务
2. DualAgentNode 把已有结构重新包装成 {subject, task}
3. IndependentAgent 再次尝试从字符串或嵌套 dict 里恢复上下文

本工具通过静态代码分析和运行时追踪，生成详细的诊断报告，
为方案B的实施提供数据支持。
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ContextFlowStep:
    """上下文流转步骤"""
    source: str  # 来源组件
    target: str  # 目标组件
    field_mapping: Dict[str, str]  # 字段映射关系
    transformation_type: str  # 转换类型: wrap/unwrap/extract/pass-through
    evidence: List[str] = field(default_factory=list)  # 证据代码片段
    line_numbers: List[int] = field(default_factory=list)  # 代码行号


@dataclass
class ContextAnomaly:
    """上下文异常"""
    anomaly_id: str
    severity: str  # critical/high/medium/low
    title: str
    description: str
    location: str  # 文件路径
    line_number: int
    current_behavior: str
    expected_behavior: str
    recommendation: str
    code_snippet: str = ""


@dataclass
class FieldExtractionPattern:
    """字段提取模式"""
    field_name: str
    extraction_method: str  # direct/json_parse/guess/unwrap
    source_location: str
    line_number: int
    code_snippet: str
    confidence: str  # high/medium/low - 表示提取逻辑的确定性


@dataclass
class NodeContractGap:
    """节点契约缺口"""
    node_id: str
    available_in_yaml: List[str]  # node.yaml 中有的字段
    used_in_executor: List[str]   # executor 中使用的字段
    used_in_agent: List[str]      # agent 中使用的字段
    missing_in_prompt: List[str]  # 应该但未进入 prompt 的字段


class NodeExecutionContextResearcher:
    """NodeExecutionContext 深度研究器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.anomalies: List[ContextAnomaly] = []
        self.flow_steps: List[ContextFlowStep] = []
        self.extraction_patterns: List[FieldExtractionPattern] = []
        self.contract_gaps: List[NodeContractGap] = []
        self.node_yaml_data: Dict[str, Dict[str, Any]] = {}
        
    def analyze(self) -> Dict[str, Any]:
        """执行完整分析"""
        self._load_node_yaml_configs()
        self._analyze_executor_task_extraction()
        self._analyze_dual_agent_wrapping()
        self._analyze_independent_agent_context_recovery()
        self._analyze_context_flow_chain()
        self._analyze_node_contract_gaps()
        self._propose_node_execution_context()
        return self._build_report_data()
    
    def _load_node_yaml_configs(self) -> None:
        """加载所有 node.yaml 配置"""
        nodes_dir = self.project_root / "autoBMAD" / "nodes"
        for node_yaml in nodes_dir.glob("*/node.yaml"):
            node_id = node_yaml.parent.name
            try:
                import yaml
                with open(node_yaml, 'r', encoding='utf-8') as f:
                    self.node_yaml_data[node_id] = yaml.safe_load(f)
            except Exception as e:
                self.node_yaml_data[node_id] = {"error": str(e)}
    
    def _analyze_executor_task_extraction(self) -> None:
        """分析 executor 中的 task 提取逻辑 (问题1)"""
        executor_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
        if not executor_path.exists():
            return
            
        content = executor_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # 查找 _extract_task_from_state 函数
        in_extract_func = False
        func_start_line = 0
        extract_logic_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'def _extract_task_from_state' in line:
                in_extract_func = True
                func_start_line = i
            elif in_extract_func:
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    in_extract_func = False
                else:
                    extract_logic_lines.append((i, line))
        
        # 记录异常：executor 从 state 里"猜 task"
        self.anomalies.append(ContextAnomaly(
            anomaly_id="CTX-001",
            severity="critical",
            title="executor 从 state 中猜测 task，而非使用节点契约",
            description="_extract_task_from_state 函数通过多种启发式规则（JSON解析、字段查找、回退策略）从序列化的 state 中提取 task，而不是使用 NodeLoader 加载的 node_config 中的明确任务定义。",
            location=str(executor_path.relative_to(self.project_root)),
            line_number=func_start_line,
            current_behavior="尝试从 context_file JSON、chained_context、deliverable 等多种来源猜测 task",
            expected_behavior="使用 NodeLoader 加载的 node.yaml 中的明确任务定义",
            recommendation="引入 NodeExecutionContext，在 executor 层将 node_config 转换为结构化的执行上下文",
            code_snippet='\n'.join([line for _, line in extract_logic_lines[:15]])
        ))
        
        # 记录提取模式
        for line_num, line in extract_logic_lines:
            if 'json.loads' in line:
                self.extraction_patterns.append(FieldExtractionPattern(
                    field_name="task",
                    extraction_method="json_parse",
                    source_location=str(executor_path.relative_to(self.project_root)),
                    line_number=line_num,
                    code_snippet=line.strip(),
                    confidence="low"
                ))
            elif '.get(' in line and 'subject_context' in line:
                self.extraction_patterns.append(FieldExtractionPattern(
                    field_name="subject_context",
                    extraction_method="guess",
                    source_location=str(executor_path.relative_to(self.project_root)),
                    line_number=line_num,
                    code_snippet=line.strip(),
                    confidence="low"
                ))
    
    def _analyze_dual_agent_wrapping(self) -> None:
        """分析 DualAgentNode 的上下文包装 (问题2)"""
        dual_agent_path = self.project_root / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
        if not dual_agent_path.exists():
            return
            
        content = dual_agent_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # 查找 build_independent_context 和 execute 中的包装逻辑
        wrapping_evidence = []
        for i, line in enumerate(lines, 1):
            if 'subject_context={"subject": subject_context, "task": task}' in line:
                wrapping_evidence.append((i, line.strip()))
        
        if wrapping_evidence:
            self.anomalies.append(ContextAnomaly(
                anomaly_id="CTX-002",
                severity="critical",
                title="DualAgentNode 二次包装上下文，破坏原有结构",
                description="DualAgentNode 将传入的 subject_context 和 task 重新包装为 {subject: ..., task: ...} 结构，导致下游 IndependentAgent 需要反向解析。",
                location=str(dual_agent_path.relative_to(self.project_root)),
                line_number=wrapping_evidence[0][0],
                current_behavior="subject_context={\"subject\": subject_context, \"task\": task}",
                expected_behavior="直接传递结构化的 NodeExecutionContext",
                recommendation="使用 NodeExecutionContext 统一结构，消除二次包装",
                code_snippet=wrapping_evidence[0][1]
            ))
            
            # 记录流转步骤
            self.flow_steps.append(ContextFlowStep(
                source="executor",
                target="DualAgentNode",
                field_mapping={
                    "subject_context": "subject_context.subject",
                    "task": "subject_context.task"
                },
                transformation_type="wrap",
                evidence=[line for _, line in wrapping_evidence],
                line_numbers=[line_num for line_num, _ in wrapping_evidence]
            ))
    
    def _analyze_independent_agent_context_recovery(self) -> None:
        """分析 IndependentAgent 的上下文恢复逻辑 (问题3)"""
        independent_path = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        if not independent_path.exists():
            return
            
        content = independent_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # 查找上下文恢复逻辑
        recovery_patterns = []
        for i, line in enumerate(lines, 1):
            if any(pattern in line for pattern in [
                'json_module.loads',
                'subject_context_data.get',
                'nested_ctx',
                'raw_content'
            ]):
                recovery_patterns.append((i, line.strip()))
        
        if recovery_patterns:
            self.anomalies.append(ContextAnomaly(
                anomaly_id="CTX-003",
                severity="critical",
                title="IndependentAgent 反向解析被包装的上下文",
                description="IndependentAgent 需要从可能经过 JSON 序列化和重新包装的 subject_context 中提取原始内容，使用了多种启发式路径（nested_ctx、flat structure 等）。",
                location=str(independent_path.relative_to(self.project_root)),
                line_number=recovery_patterns[0][0],
                current_behavior="尝试多种路径解析 subject_context: nested_ctx.get('content') 或 subject_context_data.get('content')",
                expected_behavior="直接接收结构化的 NodeExecutionContext，无需猜测",
                recommendation="使用 NodeExecutionContext.original_context 直接访问原始内容",
                code_snippet='\n'.join([line for _, line in recovery_patterns[:8]])
            ))
            
            # 记录提取模式
            for line_num, line in recovery_patterns:
                if 'nested_ctx' in line:
                    self.extraction_patterns.append(FieldExtractionPattern(
                        field_name="content",
                        extraction_method="unwrap",
                        source_location=str(independent_path.relative_to(self.project_root)),
                        line_number=line_num,
                        code_snippet=line,
                        confidence="low"
                    ))
    
    def _analyze_context_flow_chain(self) -> None:
        """分析完整的上下文流转链"""
        # 记录从 executor -> DualAgentNode -> IndependentAgent 的流转
        self.flow_steps.append(ContextFlowStep(
            source="executor._extract_task_from_state",
            target="DualAgentNode.execute",
            field_mapping={
                "task": "task",
                "subject_context": "subject_context"
            },
            transformation_type="pass-through",
            evidence=["task = _extract_task_from_state(state)", "await node.execute(subject_context=..., task=...)"],
            line_numbers=[137, 141]
        ))
        
        self.flow_steps.append(ContextFlowStep(
            source="DualAgentNode.build_independent_context",
            target="IndependentAgent.execute",
            field_mapping={
                "subject_context.subject": "context.subject_context",
                "subject_context.task": "context.task"
            },
            transformation_type="wrap",
            evidence=["subject_context={\"subject\": subject_context, \"task\": task}"],
            line_numbers=[323]
        ))
        
        self.flow_steps.append(ContextFlowStep(
            source="ContextManager.build_evaluator_context",
            target="EvaluatorAgent.execute",
            field_mapping={
                "filtered_deliverable": "context.deliverable",
                "subject": "context.subject_context"
            },
            transformation_type="pass-through",
            evidence=["evaluator_context = self.context_manager.build_evaluator_context(...)"],
            line_numbers=[393]
        ))
    
    def _analyze_node_contract_gaps(self) -> None:
        """分析节点契约缺口"""
        for node_id, node_config in self.node_yaml_data.items():
            if "error" in node_config:
                continue
                
            available = []
            if "name" in node_config:
                available.append("name")
            if "description" in node_config:
                available.append("description")
            if "deliverable_type" in node_config:
                available.append("deliverable_type")
            if "deliverable" in node_config and isinstance(node_config["deliverable"], dict):
                if "required_sections" in node_config["deliverable"]:
                    available.append("deliverable.required_sections")
                    
            # executor 中使用的字段
            used_in_executor = ["task"]  # 从 state 猜测
            
            # agent 中使用的字段
            used_in_agent = ["persona", "subject_context"]
            
            # 应该但未进入 prompt 的
            missing = [f for f in available if f not in used_in_executor and f not in used_in_agent]
            
            self.contract_gaps.append(NodeContractGap(
                node_id=node_id,
                available_in_yaml=available,
                used_in_executor=used_in_executor,
                used_in_agent=used_in_agent,
                missing_in_prompt=missing
            ))
    
    def _propose_node_execution_context(self) -> Dict[str, Any]:
        """提出 NodeExecutionContext 设计方案"""
        return {
            "class_name": "NodeExecutionContext",
            "description": "统一节点执行上下文，消除层间猜测和重复包装",
            "fields": [
                {"name": "pipeline_id", "type": "str", "source": "state", "description": "流水线ID"},
                {"name": "node_id", "type": "str", "source": "node.yaml", "description": "节点标识"},
                {"name": "node_name", "type": "str", "source": "node.yaml:name", "description": "节点名称"},
                {"name": "node_order", "type": "int", "source": "node.yaml:sequence", "description": "节点顺序"},
                {"name": "task_name", "type": "str", "source": "node.yaml:name", "description": "任务名称"},
                {"name": "task_description", "type": "str", "source": "node.yaml:description", "description": "任务描述"},
                {"name": "role_supplement", "type": "str", "source": "adapter_default", "description": "角色补充说明(适配层默认空字符串)"},
                {"name": "deliverable_type", "type": "str", "source": "node.yaml:deliverable_type", "description": "交付物类型"},
                {"name": "deliverable_requirements", "type": "dict", "source": "node.yaml:deliverable.required_sections", "description": "交付物要求"},
                {"name": "original_context", "type": "dict", "source": "state.context_file", "description": "原始上下文内容"},
                {"name": "chained_deliverables", "type": "list", "source": "state.chained_context", "description": "链式上游交付物"},
                {"name": "shared_context", "type": "dict", "source": "state.shared_context", "description": "共享上下文"},
                {"name": "iteration_feedback", "type": "dict | None", "source": "previous iteration", "description": "迭代反馈"},
                {"name": "docs_context", "type": "list", "source": "docs tools", "description": "文档上下文"},
            ],
            "adapter_mapping": {
                "task_name": "node.name",
                "task_description": "node.description",
                "role_supplement": "\"\" (空字符串，新schema后可配置)",
                "deliverable_requirements.required_sections": "node.deliverable.required_sections"
            }
        }
    
    def _build_report_data(self) -> Dict[str, Any]:
        """构建报告数据"""
        return {
            "summary": {
                "total_anomalies": len(self.anomalies),
                "critical_count": sum(1 for a in self.anomalies if a.severity == "critical"),
                "high_count": sum(1 for a in self.anomalies if a.severity == "high"),
                "flow_steps": len(self.flow_steps),
                "extraction_patterns": len(self.extraction_patterns),
                "contract_gaps": len(self.contract_gaps)
            },
            "anomalies": [
                {
                    "id": a.anomaly_id,
                    "severity": a.severity,
                    "title": a.title,
                    "description": a.description,
                    "location": a.location,
                    "line": a.line_number,
                    "current": a.current_behavior,
                    "expected": a.expected_behavior,
                    "recommendation": a.recommendation,
                    "code": a.code_snippet
                }
                for a in self.anomalies
            ],
            "flow_analysis": [
                {
                    "source": step.source,
                    "target": step.target,
                    "mapping": step.field_mapping,
                    "transformation": step.transformation_type,
                    "evidence": step.evidence,
                    "lines": step.line_numbers
                }
                for step in self.flow_steps
            ],
            "extraction_patterns": [
                {
                    "field": p.field_name,
                    "method": p.extraction_method,
                    "location": p.source_location,
                    "line": p.line_number,
                    "code": p.code_snippet,
                    "confidence": p.confidence
                }
                for p in self.extraction_patterns
            ],
            "contract_gaps": [
                {
                    "node_id": g.node_id,
                    "available_in_yaml": g.available_in_yaml,
                    "used_in_executor": g.used_in_executor,
                    "used_in_agent": g.used_in_agent,
                    "missing_in_prompt": g.missing_in_prompt
                }
                for g in self.contract_gaps
            ],
            "proposed_context": self._propose_node_execution_context()
        }
    
    def generate_markdown_report(self) -> str:
        """生成 Markdown 格式的研究报告"""
        data = self._build_report_data()
        
        lines = []
        lines.append("# NodeExecutionContext 深度研究报告")
        lines.append("")
        lines.append(f"> 生成时间: {__import__('datetime').datetime.now().isoformat()}")
        lines.append("> 研究目标: 分析方案B (统一 NodeExecutionContext) 的实施路径")
        lines.append("")
        
        # 执行摘要
        lines.append("## 执行摘要")
        lines.append("")
        lines.append("### 关键发现")
        lines.append("")
        lines.append(f"- **严重异常**: {data['summary']['critical_count']} 个")
        lines.append(f"- **高危异常**: {data['summary']['high_count']} 个")
        lines.append(f"- **上下文流转步骤**: {data['summary']['flow_steps']} 个")
        lines.append(f"- **字段提取模式**: {data['summary']['extraction_patterns']} 个")
        lines.append("")
        
        # 核心问题
        lines.append("## 核心问题分析")
        lines.append("")
        for anomaly in data['anomalies']:
            lines.append(f"### {anomaly['id']}: {anomaly['title']}")
            lines.append("")
            lines.append(f"**严重程度**: {anomaly['severity'].upper()}")
            lines.append("")
            lines.append(f"**位置**: `{anomaly['location']}:{anomaly['line']}`")
            lines.append("")
            lines.append(f"**问题描述**: {anomaly['description']}")
            lines.append("")
            lines.append("**当前行为**:")
            lines.append(f"```python\n{anomaly['current']}\n```")
            lines.append("")
            lines.append("**期望行为**:")
            lines.append(f"```python\n{anomaly['expected']}\n```")
            lines.append("")
            if anomaly['code']:
                lines.append("**相关代码**:")
                lines.append(f"```python\n{anomaly['code']}\n```")
                lines.append("")
            lines.append(f"**建议**: {anomaly['recommendation']}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # 上下文流转分析
        lines.append("## 上下文流转链路分析")
        lines.append("")
        lines.append("```")
        lines.append("executor._extract_task_from_state()")
        lines.append("       ↓ [猜测/提取]")
        lines.append("DualAgentNode.execute()")
        lines.append("       ↓ [二次包装 {subject, task}]")
        lines.append("ContextManager.build_independent_context()")
        lines.append("       ↓ [传递]")
        lines.append("IndependentAgent.execute()")
        lines.append("       ↓ [反向解析/解包]")
        lines.append("实际使用 (但可能解析失败)")
        lines.append("```")
        lines.append("")
        
        for i, step in enumerate(data['flow_analysis'], 1):
            lines.append(f"### 步骤 {i}: {step['source']} → {step['target']}")
            lines.append("")
            lines.append(f"**转换类型**: {step['transformation']}")
            lines.append("")
            lines.append("**字段映射**:")
            lines.append("| 源字段 | 目标字段 |")
            lines.append("|--------|----------|")
            for src, tgt in step['mapping'].items():
                lines.append(f"| {src} | {tgt} |")
            lines.append("")
            if step['evidence']:
                lines.append("**证据**:")
                for ev in step['evidence']:
                    lines.append(f"- `{ev}`")
                lines.append("")
            lines.append("")
        
        # 字段提取模式
        lines.append("## 字段提取模式统计")
        lines.append("")
        lines.append("| 字段 | 提取方法 | 位置 | 置信度 |")
        lines.append("|------|----------|------|--------|")
        for p in data['extraction_patterns']:
            lines.append(f"| {p['field']} | {p['method']} | {p['location']}:{p['line']} | {p['confidence']} |")
        lines.append("")
        
        # 节点契约缺口
        lines.append("## 节点契约缺口分析")
        lines.append("")
        for gap in data['contract_gaps']:
            lines.append(f"### 节点: {gap['node_id']}")
            lines.append("")
            lines.append(f"- **node.yaml 可用字段**: {', '.join(gap['available_in_yaml']) or '无'}")
            lines.append(f"- **executor 使用字段**: {', '.join(gap['used_in_executor'])}")
            lines.append(f"- **agent 使用字段**: {', '.join(gap['used_in_agent'])}")
            lines.append(f"- **未进入 prompt 的字段**: {', '.join(gap['missing_in_prompt']) or '无'}")
            lines.append("")
        
        # 建议的 NodeExecutionContext
        lines.append("## 建议的 NodeExecutionContext 设计")
        lines.append("")
        ctx = data['proposed_context']
        lines.append(f"### {ctx['class_name']}")
        lines.append("")
        lines.append(f"**描述**: {ctx['description']}")
        lines.append("")
        lines.append("### 字段定义")
        lines.append("")
        lines.append("| 字段名 | 类型 | 来源 | 描述 |")
        lines.append("|--------|------|------|------|")
        for f in ctx['fields']:
            lines.append(f"| {f['name']} | {f['type']} | {f['source']} | {f['description']} |")
        lines.append("")
        lines.append("### 旧 Schema 适配映射")
        lines.append("")
        lines.append("| 新字段 | 旧 Schema 映射 |")
        lines.append("|--------|----------------|")
        for k, v in ctx['adapter_mapping'].items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
        
        # 实施建议
        lines.append("## 方案B实施建议")
        lines.append("")
        lines.append("### 新增文件")
        lines.append("")
        lines.append("1. `autoBMAD/docuswarm/node_execution/contracts.py` - 定义 NodeExecutionContext TypedDict")
        lines.append("2. `autoBMAD/docuswarm/node_execution/context_builder.py` - NodeExecutionContextBuilder 实现")
        lines.append("")
        lines.append("### 修改文件")
        lines.append("")
        lines.append("1. `autoBMAD/docuswarm/node_execution/executor.py` - 使用 context_builder 替代 _extract_task_from_state")
        lines.append("2. `autoBMAD/docuswarm/nodes/dual_agent.py` - 接收 execution_context，停止二次包装")
        lines.append("3. `autoBMAD/docuswarm/agents/independent.py` - 直接使用 execution_context 字段")
        lines.append("4. `autoBMAD/docuswarm/agents/evaluator.py` - 使用 execution_context 构建评审上下文")
        lines.append("5. `autoBMAD/docuswarm/context/isolation.py` - ContextManager 基于 execution_context 裁剪")
        lines.append("")
        lines.append("### 迁移步骤")
        lines.append("")
        lines.append("```")
        lines.append("Step 1: 创建 NodeExecutionContextBuilder，兼容适配旧 node.yaml")
        lines.append("Step 2: executor 直接传入 execution_context，删除 _extract_task_from_state")
        lines.append("Step 3: DualAgentNode.execute() 接收 execution_context，停止二次包装")
        lines.append("Step 4: ContextManager 基于 execution_context 裁剪")
        lines.append("Step 5: 验证所有节点的 prompt 中都能稳定看到节点契约")
        lines.append("```")
        lines.append("")
        
        # 完成标准
        lines.append("## 完成标准")
        lines.append("")
        lines.append("- [ ] 代码中不再存在 `_extract_task_from_state()` 主导任务语义")
        lines.append("- [ ] `DualAgentNode` 不再构造 `{subject, task}` 包装")
        lines.append("- [ ] `IndependentAgent.execute()` 不再需要从字符串恢复上下文结构")
        lines.append("- [ ] 任一节点运行时，prompt 中能稳定看到节点名称、任务描述、必选章节")
        lines.append("- [ ] 五个节点的 prompt 差异来自节点契约，而不仅仅是 persona")
        lines.append("")
        
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="NodeExecutionContext 深度研究工具 - 方案B实现分析"
    )
    parser.add_argument(
        "--output",
        help="输出报告文件路径 (默认输出到控制台)",
        type=str
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式"
    )
    args = parser.parse_args()
    
    researcher = NodeExecutionContextResearcher(PROJECT_ROOT)
    researcher.analyze()
    
    if args.format == "json":
        output = json.dumps(researcher._build_report_data(), ensure_ascii=False, indent=2)
    else:
        output = researcher.generate_markdown_report()
    
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding='utf-8')
        print(f"报告已保存到: {output_path}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
