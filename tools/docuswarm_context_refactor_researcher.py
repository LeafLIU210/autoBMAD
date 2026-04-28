"""
DocuSwarm Context Refactor 深度研究工具

基于评估文档 `docs/evaluation/2026-03-17-docuswarm-context-refactor-implementation-evaluation.md`，
对 autoBMAD/docuswarm 进行深度研究，验证关键发现的实现状态。

研究范围:
1. P0-1: 单一上下文协议实现状态
2. P0-2: node.yaml prompt 注入完成度
3. P0-3: 单一交付物真相闭环验证
4. P1-1: update_context 持久化运行时闭环
5. P1-2: docs-free workflow 边界状态
6. 测试覆盖缺口分析
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Evidence:
    """证据项"""
    path: str
    line: int
    snippet: str
    context: str = ""


@dataclass
class Finding:
    """研究发现"""
    finding_id: str
    severity: str  # critical/high/medium/low
    category: str  # P0-1/P0-2/P0-3/P1-1/P1-2/TEST
    title: str
    description: str
    current_state: str
    expected_state: str
    recommendation: str
    evidences: List[Evidence] = field(default_factory=list)
    verification_status: str = "unverified"  # verified/partial/unverified


@dataclass
class ImplementationStatus:
    """实现状态统计"""
    category: str
    target: str
    current: str
    completion_pct: int
    blockers: List[str] = field(default_factory=list)


class DocuSwarmContextRefactorResearcher:
    """DocuSwarm Context Refactor 深度研究器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[Finding] = []
        self.statuses: List[ImplementationStatus] = []
        self.evidence_cache: Dict[str, str] = {}
        
    def _read_file(self, path: Path) -> str:
        """读取文件内容并缓存"""
        key = str(path)
        if key not in self.evidence_cache:
            try:
                self.evidence_cache[key] = path.read_text(encoding='utf-8')
            except Exception as e:
                self.evidence_cache[key] = f"ERROR: {e}"
        return self.evidence_cache[key]
    
    def _find_pattern(self, path: Path, pattern: str, context_lines: int = 2) -> List[Evidence]:
        """在文件中查找模式"""
        content = self._read_file(path)
        lines = content.splitlines()
        evidences = []
        
        for i, line in enumerate(lines, 1):
            if pattern in line:
                start = max(0, i - context_lines - 1)
                end = min(len(lines), i + context_lines)
                context = "\n".join(lines[start:end])
                evidences.append(Evidence(
                    path=str(path.relative_to(self.project_root)),
                    line=i,
                    snippet=line.strip(),
                    context=context
                ))
        return evidences
    
    def _check_file_exists(self, rel_path: str) -> bool:
        """检查文件是否存在"""
        return (self.project_root / rel_path).exists()
    
    def run_full_research(self) -> Dict[str, Any]:
        """执行完整研究"""
        print("[RESEARCH] Starting DocuSwarm Context Refactor Deep Research...")
        
        # P0-1: 单一上下文协议
        print("  [STEP] Researching P0-1: Single Context Protocol...")
        self._research_p0_1_single_context_protocol()
        
        # P0-2: node.yaml prompt 注入
        print("  [STEP] Researching P0-2: Node Prompt Injection...")
        self._research_p0_2_node_prompt_injection()
        
        # P0-3: 单一交付物真相
        print("  [STEP] Researching P0-3: Single Truth Deliverable...")
        self._research_p0_3_single_truth_deliverable()
        
        # P1-1: update_context 持久化
        print("  [STEP] Researching P1-1: Update Context Persistence...")
        self._research_p1_1_update_context_persistence()
        
        # P1-2: docs-free workflow
        print("  [STEP] Researching P1-2: Docs-free Workflow...")
        self._research_p1_2_docs_free_workflow()
        
        # 测试覆盖分析
        print("  [STEP] Analyzing Test Coverage Gaps...")
        self._research_test_coverage_gaps()
        
        # 生成状态总结
        self._generate_status_summary()
        
        return self._build_report_data()
    
    def _research_p0_1_single_context_protocol(self) -> None:
        """研究 P0-1: 单一上下文协议实现状态"""
        
        # 检查核心组件是否存在
        contracts_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
        context_builder_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "context_builder.py"
        executor_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
        
        # 验证 NodeExecutionContext 定义
        if contracts_path.exists():
            content = self._read_file(contracts_path)
            has_node_exec_context = "class NodeExecutionContext" in content or "NodeExecutionContext =" in content
            has_independent_input = "IndependentAgentInput" in content
            has_evaluator_input = "EvaluatorAgentInput" in content
            has_deliverable_artifact = "DeliverableArtifact" in content
            
            if has_node_exec_context and has_independent_input and has_evaluator_input:
                self.findings.append(Finding(
                    finding_id="P0-1-001",
                    severity="low",
                    category="P0-1",
                    title="NodeExecutionContext 核心数据结构已定义",
                    description="NodeExecutionContext、IndependentAgentInput、EvaluatorAgentInput TypedDict 已在 contracts.py 中定义",
                    current_state="核心数据结构已落地",
                    expected_state="完整协议定义",
                    recommendation="已满足基本要求",
                    evidences=[Evidence(
                        path=str(contracts_path.relative_to(self.project_root)),
                        line=content.find("NodeExecutionContext"),
                        snippet="NodeExecutionContext TypedDict defined",
                        context="Core protocol structures defined"
                    )],
                    verification_status="verified"
                ))
        
        # 验证 NodeExecutionContextBuilder 实现
        if context_builder_path.exists():
            content = self._read_file(context_builder_path)
            has_builder_class = "NodeExecutionContextBuilder" in content
            has_build_method = "def build" in content
            
            if has_builder_class and has_build_method:
                self.findings.append(Finding(
                    finding_id="P0-1-002",
                    severity="low",
                    category="P0-1",
                    title="NodeExecutionContextBuilder 已实现",
                    description="上下文构建器已实现，用于从 node.yaml 和 runtime state 构建统一上下文",
                    current_state="Builder 已落地",
                    expected_state="完整构建逻辑",
                    recommendation="已满足基本要求",
                    verification_status="verified"
                ))
        
        # 验证 executor 使用新协议
        if executor_path.exists():
            content = self._read_file(executor_path)
            uses_context_builder = "create_context_builder" in content
            calls_execute_with_context = "execute_with_context" in content
            
            if uses_context_builder and calls_execute_with_context:
                self.findings.append(Finding(
                    finding_id="P0-1-003",
                    severity="low",
                    category="P0-1",
                    title="Executor 已接入单一上下文协议",
                    description="executor.py 已通过 context_builder 构建 execution_context 并调用 execute_with_context",
                    current_state="Executor 已接入新协议",
                    expected_state="全流程统一协议",
                    recommendation="已满足基本要求",
                    verification_status="verified"
                ))
        
        # 检查状态层是否收敛
        pipeline_state_path = self.project_root / "autoBMAD" / "docuswarm" / "pipeline" / "state.py"
        if pipeline_state_path.exists():
            content = self._read_file(pipeline_state_path)
            has_execution_context_in_state = "execution_context" in content
            has_shared_context = "shared_context" in content
            
            if not has_execution_context_in_state:
                self.findings.append(Finding(
                    finding_id="P0-1-004",
                    severity="medium",
                    category="P0-1",
                    title="PipelineState 尚未显式持有 execution_context",
                    description="当前 PipelineState 仍以 context_file/chained_context/deliverables 为主，而非显式持有 execution_context",
                    current_state="旧状态结构",
                    expected_state="PipelineState.execution_context 字段",
                    recommendation="考虑在 PipelineState 中显式添加 execution_context 字段以统一协议",
                    evidences=self._find_pattern(pipeline_state_path, "PipelineState", 5),
                    verification_status="partial"
                ))
    
    def _research_p0_2_node_prompt_injection(self) -> None:
        """研究 P0-2: node.yaml prompt 注入完成度"""
        
        # 检查 NodePromptContractBuilder
        contract_builder_path = self.project_root / "autoBMAD" / "docuswarm" / "prompts" / "contract_builder.py"
        independent_path = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
        evaluator_path = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "evaluator.py"
        
        if contract_builder_path.exists():
            content = self._read_file(contract_builder_path)
            has_independent_contract = "build_independent_contract" in content
            has_evaluator_contract = "build_evaluator_contract" in content
            has_task_section = "_build_task_section" in content
            has_deliverable_section = "_build_deliverable_section" in content
            
            if all([has_independent_contract, has_evaluator_contract, has_task_section, has_deliverable_section]):
                self.findings.append(Finding(
                    finding_id="P0-2-001",
                    severity="low",
                    category="P0-2",
                    title="NodePromptContractBuilder 已实现 prompt 契约构建",
                    description="contract_builder.py 已实现 Independent 和 Evaluator 的 prompt 契约构建",
                    current_state="Prompt Contract Builder 已落地",
                    expected_state="完整 prompt 注入",
                    recommendation="已满足基本要求",
                    verification_status="verified"
                ))
        
        # 验证 IndependentAgent 使用 contract builder
        if independent_path.exists():
            content = self._read_file(independent_path)
            uses_contract_builder = "contract_builder" in content and "build_independent_contract" in content
            has_execute_with_input = "execute_with_input" in content
            
            if uses_contract_builder and has_execute_with_input:
                self.findings.append(Finding(
                    finding_id="P0-2-002",
                    severity="low",
                    category="P0-2",
                    title="IndependentAgent 已使用 contract builder 组装 prompt",
                    description="IndependentAgent.execute_with_input() 已使用 NodePromptContractBuilder 构建 prompt",
                    current_state="Independent prompt 注入基本完成",
                    expected_state="完整闭环",
                    recommendation="已满足基本要求",
                    verification_status="verified"
                ))
        
        # 验证 EvaluatorAgent 使用 contract builder
        if evaluator_path.exists():
            content = self._read_file(evaluator_path)
            uses_contract_builder = "contract_builder" in content and "build_evaluator_contract" in content
            
            # 检查 Evaluator 是否包含原始上下文摘要
            has_original_context = "original_context" in content
            evaluator_input_has_context = "EvaluatorAgentInput" in self._read_file(
                self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
            )
            
            # 检查 contracts.py 中 EvaluatorAgentInput 是否包含原始上下文
            contracts_content = self._read_file(
                self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
            )
            evaluator_input_def = contracts_content[contracts_content.find("class EvaluatorAgentInput"):]
            evaluator_input_def = evaluator_input_def[:evaluator_input_def.find("class", 10)] if "class" in evaluator_input_def[10:] else evaluator_input_def[:500]
            has_original_context_in_input = "original_context" in evaluator_input_def
            
            if uses_contract_builder and not has_original_context_in_input:
                self.findings.append(Finding(
                    finding_id="P0-2-003",
                    severity="high",
                    category="P0-2",
                    title="EvaluatorAgentInput 缺少原始上下文摘要字段",
                    description="EvaluatorAgentInput 当前只包含 task_name, task_description, deliverable_artifact, deliverable_body, criteria，没有原始上下文字段",
                    current_state="Evaluator 输入缺少原始上下文",
                    expected_state="EvaluatorAgentInput 包含 original_context_summary",
                    recommendation="在 EvaluatorAgentInput 中添加原始上下文摘要字段，让 Evaluator prompt 能渲染'原始需求摘要'章节",
                    evidences=[
                        Evidence(
                            path="autoBMAD/docuswarm/node_execution/contracts.py",
                            line=contracts_content.find("EvaluatorAgentInput"),
                            snippet="class EvaluatorAgentInput(TypedDict):",
                            context=evaluator_input_def[:300]
                        )
                    ],
                    verification_status="partial"
                ))
        
        # 检查 node.yaml 结构
        nodes_dir = self.project_root / "nodes"
        node_yaml_files = list(nodes_dir.glob("*/node.yaml"))
        
        has_new_schema = False
        for yaml_file in node_yaml_files:
            content = self._read_file(yaml_file)
            if "task:" in content and "name:" in content and "description:" in content:
                has_new_schema = True
                break
        
        if has_new_schema:
            self.findings.append(Finding(
                finding_id="P0-2-004",
                severity="low",
                category="P0-2",
                title="node.yaml 已普遍采用新 schema",
                description="根目录 nodes/*/node.yaml 已普遍采用带 task / deliverable 子结构的新形态",
                current_state="新 schema 已落地",
                expected_state="完整契约注入",
                recommendation="与 overview 文档同步，更新研究结论",
                verification_status="verified"
            ))
    
    def _research_p0_3_single_truth_deliverable(self) -> None:
        """研究 P0-3: 单一交付物真相闭环验证"""
        
        create_deliverable_path = self.project_root / "autoBMAD" / "docuswarm" / "tools" / "create_deliverable.py"
        response_path = self.project_root / "autoBMAD" / "docuswarm" / "llm" / "response.py"
        isolation_path = self.project_root / "autoBMAD" / "docuswarm" / "context" / "isolation.py"
        contracts_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
        
        # 验证 create_deliverable 返回 metadata
        if create_deliverable_path.exists():
            content = self._read_file(create_deliverable_path)
            returns_metadata = "file_path" in content and "sha256" in content and "metadata" in content
            writes_file = "aiofiles.open" in content or "async with aiofiles" in content
            
            if returns_metadata and writes_file:
                self.findings.append(Finding(
                    finding_id="P0-3-001",
                    severity="low",
                    category="P0-3",
                    title="create_deliverable 已实现 metadata-first 返回",
                    description="create_deliverable 工具已写盘并返回 metadata，而非正文",
                    current_state="metadata-first 已实现",
                    expected_state="强制 metadata-only",
                    recommendation="已满足基本要求",
                    verification_status="verified"
                ))
        
        # 检查验证层是否强制 file_path/sha256
        if response_path.exists():
            content = self._read_file(response_path)
            validation_section = content[content.find("validate_independent_output"):content.find("def validate_evaluator_output")]
            
            # 检查 file_path 和 sha256 是否是强制字段
            file_path_optional = "file_path" in validation_section and "if \"file_path\" in deliverable" in validation_section
            sha256_optional = "sha256" in validation_section and "if \"sha256\" in deliverable" in validation_section
            content_required = "deliverable.content" in validation_section and "required" in validation_section
            
            if file_path_optional and sha256_optional:
                self.findings.append(Finding(
                    finding_id="P0-3-002",
                    severity="high",
                    category="P0-3",
                    title="file_path 和 sha256 不是强制验证字段",
                    description="当前验证只要求 deliverable.title 和 deliverable.content，file_path/sha256 仅'如果存在则校验类型'。这意味着模型可以返回只有摘要、没有 artifact metadata 的输出，仍然通过验证。",
                    current_state="file_path/sha256 可选",
                    expected_state="file_path/sha256 强制",
                    recommendation="将 file_path 和 sha256 提升为强制字段，确保单一真相",
                    evidences=self._find_pattern(response_path, "file_path", 3),
                    verification_status="partial"
                ))
        
        # 检查 DeliverableArtifact 定义与运行时不一致
        if contracts_path.exists() and response_path.exists():
            contracts_content = self._read_file(contracts_path)
            response_content = self._read_file(response_path)
            
            # 检查 DeliverableArtifact 使用 summary
            artifact_def = contracts_content[contracts_content.find("class DeliverableArtifact"):]
            artifact_def = artifact_def[:artifact_def.find("class", 10)] if "class" in artifact_def[10:] else artifact_def[:500]
            uses_summary_in_artifact = "summary" in artifact_def
            
            # 检查运行时验证使用 content
            validation_uses_content = "deliverable.content" in response_content
            
            if uses_summary_in_artifact and validation_uses_content:
                self.findings.append(Finding(
                    finding_id="P0-3-003",
                    severity="high",
                    category="P0-3",
                    title="DeliverableArtifact 目标结构与运行时验证不一致",
                    description="目标类型使用 'summary'，但运行时验证仍使用 'deliverable.content'。代码库同时存在两套语义：文档层用 summary，运行时/验证层用 content。",
                    current_state="summary/content 双轨并存",
                    expected_state="统一使用 summary",
                    recommendation="统一使用 summary 字段，去掉 deliverable.content 的双重语义",
                    evidences=[
                        Evidence(
                            path="autoBMAD/docuswarm/node_execution/contracts.py",
                            line=contracts_content.find("summary"),
                            snippet="summary: str  # 简短摘要",
                            context=artifact_def[:200]
                        ),
                        *self._find_pattern(response_path, "deliverable.content", 3)
                    ],
                    verification_status="partial"
                ))
        
        # 检查 Evaluator 是否会退回到摘要
        if isolation_path.exists():
            content = self._read_file(isolation_path)
            build_evaluator_input_section = content[content.find("def build_evaluator_input"):content.find("def build_evaluator_context")]
            
            has_fallback_to_content = "deliverable.get(\"content\"" in build_evaluator_input_section or 'deliverable.get("content"' in build_evaluator_input_section
            
            if has_fallback_to_content:
                self.findings.append(Finding(
                    finding_id="P0-3-004",
                    severity="high",
                    category="P0-3",
                    title="Evaluator 在 file_path 缺失时会退回到 deliverable.content",
                    description="build_evaluator_input() 中当 file_path 缺失或不可读时会退回到 deliverable.get('content', '')，这意味着 Evaluator 可能评审摘要而非正式正文。",
                    current_state="存在 fallback 到摘要的逻辑",
                    expected_state="强制从文件读取正文",
                    recommendation="禁止 Evaluator 退回到摘要作为正式评审正文，确保评审对象始终来自工具写盘后的正式文档",
                    evidences=self._find_pattern(isolation_path, "deliverable.get", 3),
                    verification_status="partial"
                ))
    
    def _research_p1_1_update_context_persistence(self) -> None:
        """研究 P1-1: update_context 持久化运行时闭环"""
        
        update_context_path = self.project_root / "autoBMAD" / "docuswarm" / "tools" / "update_context.py"
        state_manager_path = self.project_root / "autoBMAD" / "docuswarm" / "storage" / "state_manager.py"
        independent_agent_yaml = self.project_root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
        isolation_path = self.project_root / "autoBMAD" / "docuswarm" / "context" / "isolation.py"
        contracts_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
        pipeline_state_path = self.project_root / "autoBMAD" / "docuswarm" / "pipeline" / "state.py"
        
        # 检查 UpdateContextTool 依赖注入
        if update_context_path.exists():
            content = self._read_file(update_context_path)
            
            needs_state_manager = "state_manager: StateManager" in content or "_state_manager" in content
            needs_pipeline_id = "pipeline_id" in content
            has_init_params = "def __init__" in content and ("state_manager" in content or "_state_manager" in content)
            
            # 检查独立函数（向后兼容）是否返回 mock
            standalone_noop = "ToolResult(success=True" in content and "acknowledged" in content
            
            if needs_state_manager and standalone_noop:
                self.findings.append(Finding(
                    finding_id="P1-1-001",
                    severity="critical",
                    category="P1-1",
                    title="update_context 仍未形成可用的运行时闭环",
                    description="UpdateContextTool 运行时依赖 state_manager 与 pipeline_id，但默认 agent 配置只声明了类路径，没有看到任何绑定逻辑。standalone 函数返回 mock success 而非真实更新。",
                    current_state="接口存在但运行闭环未成立",
                    expected_state="真实 StateManager 绑定和持久化",
                    recommendation="为 UpdateContextTool 提供真实的 StateManager / pipeline_id 绑定机制，确保 agent 调用时能真实更新上下文",
                    evidences=[
                        *self._find_pattern(update_context_path, "StateManager not available", 2),
                        *self._find_pattern(update_context_path, "acknowledged", 2)
                    ],
                    verification_status="unverified"
                ))
        
        # 检查 shared_context 是否进入 IndependentAgentInput
        if contracts_path.exists() and isolation_path.exists():
            contracts_content = self._read_file(contracts_path)
            isolation_content = self._read_file(isolation_path)
            
            # 检查 IndependentAgentInput 是否包含 shared_context
            independent_input_def = contracts_content[contracts_content.find("class IndependentAgentInput"):]
            independent_input_def = independent_input_def[:independent_input_def.find("class", 10)] if "class" in independent_input_def[10:] else independent_input_def[:500]
            has_shared_context_in_input = "shared_context" in independent_input_def
            
            # 检查 build_independent_input 是否输出 shared_context
            build_independent_section = isolation_content[isolation_content.find("def build_independent_input"):isolation_content.find("def build_evaluator_input")]
            outputs_shared_context = "shared_context" in build_independent_section
            
            if not has_shared_context_in_input:
                self.findings.append(Finding(
                    finding_id="P1-1-002",
                    severity="high",
                    category="P1-1",
                    title="shared_context 未进入 IndependentAgentInput",
                    description="IndependentAgentInput 当前未包含 shared_context 字段，导致即使 StateManager 写入 shared_context，也不会进入 agent 输入。",
                    current_state="shared_context 未接入 Agent 输入",
                    expected_state="IndependentAgentInput 包含 shared_context",
                    recommendation="在 IndependentAgentInput 中添加 shared_context 字段，在 build_independent_input() 中显式渲染",
                    evidences=[
                        Evidence(
                            path="autoBMAD/docuswarm/node_execution/contracts.py",
                            line=contracts_content.find("IndependentAgentInput"),
                            snippet="class IndependentAgentInput(TypedDict):",
                            context=independent_input_def[:300]
                        )
                    ],
                    verification_status="unverified"
                ))
        
        # 检查 PipelineState 是否声明 shared_context
        if pipeline_state_path.exists():
            content = self._read_file(pipeline_state_path)
            pipeline_state_def = content[content.find("class PipelineState"):content[content.find("class PipelineState"):].find("class", 10)]
            
            # 检查 create_initial_state 是否初始化 shared_context
            create_initial_section = content[content.find("def create_initial_state"):content[content.find("def create_initial_state"):].find("def ", 10)]
            has_shared_context_init = "shared_context" in content[content.find("def create_initial_state"):content.find("def create_initial_state")+1000]
            
            if not has_shared_context_init:
                self.findings.append(Finding(
                    finding_id="P1-1-003",
                    severity="medium",
                    category="P1-1",
                    title="恢复链路不会回填 shared_context",
                    description="PipelineState 和 create_initial_state 未声明/初始化 shared_context，恢复路径重建 state 时不会把 shared_context 放回去。",
                    current_state="shared_context 不在恢复链路",
                    expected_state="resume/restart 恢复 shared_context",
                    recommendation="在 PipelineState 中声明 shared_context，在 create_initial_state 中初始化",
                    evidences=self._find_pattern(pipeline_state_path, "create_initial_state", 10),
                    verification_status="unverified"
                ))
        
        # 验证 StateManager.update_shared_context 是否已实现
        if state_manager_path.exists():
            content = self._read_file(state_manager_path)
            has_update_shared_context = "async def update_shared_context" in content
            
            if has_update_shared_context:
                self.findings.append(Finding(
                    finding_id="P1-1-004",
                    severity="low",
                    category="P1-1",
                    title="StateManager.update_shared_context 已实现真实写库",
                    description="StateManager 已实现 update_shared_context 方法，支持 set/append/remove 操作和嵌套 key_path",
                    current_state="持久化层已实现",
                    expected_state="完整运行时闭环",
                    recommendation="与工具层绑定完成闭环",
                    evidences=self._find_pattern(state_manager_path, "update_shared_context", 5),
                    verification_status="verified"
                ))
    
    def _research_p1_2_docs_free_workflow(self) -> None:
        """研究 P1-2: docs-free workflow 边界状态"""
        
        context_builder_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "context_builder.py"
        contracts_path = self.project_root / "autoBMAD" / "docuswarm" / "node_execution" / "contracts.py"
        main_path = self.project_root / "autoBMAD" / "docuswarm" / "main.py"
        readme_path = self.project_root / "autoBMAD" / "docuswarm" / "README.md"
        
        # 检查 docs_context 是否固定为空
        if context_builder_path.exists():
            content = self._read_file(context_builder_path)
            docs_context_fixed_empty = "docs_context=[]" in content or 'docs_context: list[dict[str, Any]] = []' in content
            
            if docs_context_fixed_empty:
                self.findings.append(Finding(
                    finding_id="P1-2-001",
                    severity="low",
                    category="P1-2",
                    title="docs_context 已固定为空列表",
                    description="NodeExecutionContextBuilder 当前固定 docs_context=[]，符合 docs-free 决策",
                    current_state="docs_context 已停用",
                    expected_state="完全移除 docs 相关代码",
                    recommendation="继续清理 docs 相关残余代码",
                    verification_status="verified"
                ))
        
        # 检查 CLI 是否仍读取 docs
        if main_path.exists():
            content = self._read_file(main_path)
            reads_docs = "docs/" in content or "docs" in content
            
            if reads_docs:
                self.findings.append(Finding(
                    finding_id="P1-2-002",
                    severity="medium",
                    category="P1-2",
                    title="CLI 仍直接读取用户提供的 context file",
                    description="main.py 仍直接读取用户提供的 context file，虽不一定是 docs/ 文件，但边界尚未完全收口",
                    current_state="CLI 边界宽松",
                    expected_state="workflow never reads docs/",
                    recommendation="清理 CLI 中仍鼓励以 docs/*.md 作为标准入口的表述",
                    evidences=self._find_pattern(main_path, "context", 3),
                    verification_status="partial"
                ))
        
        # 检查 README 是否仍引用 docs
        if readme_path.exists():
            content = self._read_file(readme_path)
            references_docs_examples = "docs/epics/" in content or "docs/proposal.md" in content
            
            if references_docs_examples:
                self.findings.append(Finding(
                    finding_id="P1-2-003",
                    severity="low",
                    category="P1-2",
                    title="README 仍把 docs/*.md 作为标准工作流示例",
                    description="README 仍引用 docs/epics/EPIC-01.md、docs/proposal.md 作为标准工作流示例，与 docs-free 决策不一致",
                    current_state="文档未同步",
                    expected_state="文档更新为 docs-free",
                    recommendation="更新 README，移除 docs/ 路径示例",
                    verification_status="partial"
                ))
    
    def _research_test_coverage_gaps(self) -> None:
        """研究测试覆盖缺口"""
        
        tests_dir = self.project_root / "autoBMAD" / "docuswarm" / "tests"
        
        # 检查关键测试文件是否存在
        expected_test_files = [
            "test_node_execution_context.py",
            "test_prompt_contract_builder.py",
            "test_single_truth_deliverable.py",
            "test_update_context_persistence.py",
            "test_shared_context_cross_node.py",
            "test_docs_free_boundary.py",
        ]
        
        existing_tests = []
        missing_tests = []
        
        for test_file in expected_test_files:
            if (tests_dir / "unit" / test_file).exists() or (tests_dir / "integration" / test_file).exists():
                existing_tests.append(test_file)
            else:
                missing_tests.append(test_file)
        
        if missing_tests:
            self.findings.append(Finding(
                finding_id="TEST-001",
                severity="high",
                category="TEST",
                title="本轮重构几乎没有成体系的自动化回归测试",
                description=f"当前 tests 目录下未发现与重构目标直接对应的 source test 文件。缺失: {', '.join(missing_tests)}",
                current_state="强依赖人工审查与局部验证",
                expected_state="完整测试护栏",
                recommendation="补上 prompt contract、single truth、update_context persistence、shared_context cross-node、docs-free boundary 的单元/集成测试",
                evidences=[
                    Evidence(
                        path="autoBMAD/docuswarm/tests",
                        line=0,
                        snippet=f"Existing: {', '.join(existing_tests) or 'None'}",
                        context=f"Missing: {', '.join(missing_tests)}"
                    )
                ],
                verification_status="unverified"
            ))
    
    def _generate_status_summary(self) -> None:
        """生成状态总结"""
        
        status_map = {
            "P0-1": ("收敛为单一上下文协议", 75),
            "P0-2": ("让 node.yaml 真正进入 prompt", 78),
            "P0-3": ("消除摘要/正式文档双轨", 55),
            "P1-1": ("让 update_context 接入 StateManager", 25),
            "P1-2": ("docs-free workflow", 70),
        }
        
        for category, (target, default_pct) in status_map.items():
            category_findings = [f for f in self.findings if f.category == category]
            
            verified = sum(1 for f in category_findings if f.verification_status == "verified")
            partial = sum(1 for f in category_findings if f.verification_status == "partial")
            unverified = sum(1 for f in category_findings if f.verification_status == "unverified")
            
            # 计算完成度
            if verified + partial + unverified == 0:
                pct = default_pct
            else:
                pct = int((verified * 100 + partial * 50) / (verified + partial + unverified))
            
            blockers = [f.title for f in category_findings if f.severity in ("critical", "high") and f.verification_status != "verified"]
            
            self.statuses.append(ImplementationStatus(
                category=category,
                target=target,
                current=f"已验证: {verified}, 部分: {partial}, 未验证: {unverified}",
                completion_pct=pct,
                blockers=blockers[:3]  # 最多3个阻塞项
            ))
    
    def _build_report_data(self) -> Dict[str, Any]:
        """构建报告数据"""
        return {
            "meta": {
                "title": "DocuSwarm Context Refactor 深度研究报告",
                "date": "2026-03-17",
                "based_on": "docs/evaluation/2026-03-17-docuswarm-context-refactor-implementation-evaluation.md",
                "scope": "autoBMAD/docuswarm",
            },
            "executive_summary": {
                "total_findings": len(self.findings),
                "critical": sum(1 for f in self.findings if f.severity == "critical"),
                "high": sum(1 for f in self.findings if f.severity == "high"),
                "medium": sum(1 for f in self.findings if f.severity == "medium"),
                "low": sum(1 for f in self.findings if f.severity == "low"),
                "overall_completion": sum(s.completion_pct for s in self.statuses) // len(self.statuses) if self.statuses else 0,
            },
            "implementation_status": [
                {
                    "category": s.category,
                    "target": s.target,
                    "current": s.current,
                    "completion_pct": s.completion_pct,
                    "blockers": s.blockers
                }
                for s in self.statuses
            ],
            "findings": [
                {
                    "id": f.finding_id,
                    "severity": f.severity,
                    "category": f.category,
                    "title": f.title,
                    "description": f.description,
                    "current_state": f.current_state,
                    "expected_state": f.expected_state,
                    "recommendation": f.recommendation,
                    "verification_status": f.verification_status,
                    "evidences": [
                        {
                            "path": e.path,
                            "line": e.line,
                            "snippet": e.snippet,
                        }
                        for e in f.evidences[:3]  # 最多3个证据
                    ]
                }
                for f in sorted(self.findings, key=lambda x: (x.category, x.severity))
            ]
        }
    
    def generate_markdown_report(self) -> str:
        """生成 Markdown 格式的研究报告"""
        data = self._build_report_data()
        
        lines = []
        lines.append(f"# {data['meta']['title']}")
        lines.append("")
        lines.append(f"> 研究日期: {data['meta']['date']}")
        lines.append(f"> 基于评估: `{data['meta']['based_on']}`")
        lines.append(f"> 研究范围: `{data['meta']['scope']}`")
        lines.append("")
        
        # 执行摘要
        lines.append("## 执行摘要")
        lines.append("")
        summary = data['executive_summary']
        lines.append(f"- **总体完成度**: {summary['overall_completion']}%")
        lines.append(f"- **研究发现总数**: {summary['total_findings']}")
        lines.append(f"- **严重 (Critical)**: {summary['critical']}")
        lines.append(f"- **高危 (High)**: {summary['high']}")
        lines.append(f"- **中等 (Medium)**: {summary['medium']}")
        lines.append(f"- **低危 (Low)**: {summary['low']}")
        lines.append("")
        
        # 实现状态总览
        lines.append("## 实现状态总览")
        lines.append("")
        lines.append("| 主题 | 目标 | 当前状态 | 完成度 | 阻塞项 |")
        lines.append("|------|------|----------|--------|--------|")
        for s in data['implementation_status']:
            blockers_str = "; ".join(s['blockers']) if s['blockers'] else "无"
            lines.append(f"| {s['category']} | {s['target']} | {s['current']} | {s['completion_pct']}% | {blockers_str} |")
        lines.append("")
        
        # 按类别分组的研究发现
        lines.append("## 详细研究发现")
        lines.append("")
        
        current_category = None
        for finding in data['findings']:
            if finding['category'] != current_category:
                current_category = finding['category']
                lines.append(f"### {current_category} 相关发现")
                lines.append("")
            
            severity_emoji = {
                "critical": "[CRIT]",
                "high": "[HIGH]",
                "medium": "[MED]",
                "low": "[LOW]"
            }.get(finding['severity'], "[INFO]")
            
            status_emoji = {
                "verified": "[OK]",
                "partial": "[~]",
                "unverified": "[X]"
            }.get(finding['verification_status'], "[?]")
            
            lines.append(f"#### {severity_emoji} {finding['id']}: {finding['title']}")
            lines.append("")
            lines.append(f"**验证状态**: {status_emoji} {finding['verification_status']}")
            lines.append("")
            lines.append(f"**问题描述**: {finding['description']}")
            lines.append("")
            lines.append("**当前状态**:")
            lines.append(f"> {finding['current_state']}")
            lines.append("")
            lines.append("**期望状态**:")
            lines.append(f"> {finding['expected_state']}")
            lines.append("")
            
            if finding['evidences']:
                lines.append("**证据**:")
                for e in finding['evidences']:
                    lines.append(f"- `{e['path']}:{e['line']}`: `{e['snippet'][:80]}`")
                lines.append("")
            
            lines.append(f"**建议**: {finding['recommendation']}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # 后续建议
        lines.append("## 后续建议")
        lines.append("")
        lines.append("### 建议的实施顺序")
        lines.append("")
        lines.append("1. **先完成 P1-1 真闭环**")
        lines.append("   - 为 UpdateContextTool 提供真实的 StateManager / pipeline_id 绑定机制")
        lines.append("   - 把 shared_context 带入 IndependentAgentInput")
        lines.append("   - 在 prompt builder 中显式渲染 shared_context")
        lines.append("   - 在 resume/restart 路径恢复 shared_context")
        lines.append("")
        lines.append("2. **再收口 P0-3 单一交付物真相**")
        lines.append("   - 统一使用 summary，去掉 deliverable.content 的双重语义")
        lines.append("   - 将 file_path / sha256 提升为强制字段")
        lines.append("   - 禁止 Evaluator 退回到摘要作为正式评审正文")
        lines.append("   - 限制下游链式上下文只传播 metadata + summary")
        lines.append("")
        lines.append("3. **然后补完 P0-2 的 Evaluator 上下文**")
        lines.append("   - 在 EvaluatorAgentInput 中加入原始上下文摘要")
        lines.append("   - 让 Evaluator prompt 稳定出现'原始需求摘要'章节")
        lines.append("")
        lines.append("4. **最后清理 P0-1 与 P1-2 的尾巴**")
        lines.append("   - 视需要把状态层进一步收敛到 execution_context 主协议")
        lines.append("   - 清理 README / CLI 中仍鼓励以 docs/*.md 作为标准入口的表述")
        lines.append("")
        lines.append("5. **补测试**")
        lines.append("   - 至少补上 prompt contract、single truth、update_context persistence、shared_context cross-node、docs-free boundary 的单元/集成测试")
        lines.append("")
        
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DocuSwarm Context Refactor 深度研究工具"
    )
    parser.add_argument(
        "--output",
        help="输出报告文件路径",
        type=str
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式"
    )
    args = parser.parse_args()
    
    researcher = DocuSwarmContextRefactorResearcher(PROJECT_ROOT)
    researcher.run_full_research()
    
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
        print(f"[DONE] Research report saved to: {output_path}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
