#!/usr/bin/env python3
"""
兼容层调用链追踪工具

分析兼容层代码如何影响主执行路径，追踪从旧 API 到新 API 的转换链路。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CallChainNode:
    """调用链节点"""
    file: str
    function: str
    line: int
    description: str
    code_snippet: str = ""


@dataclass
class CompatibilityCallChain:
    """兼容层调用链"""
    name: str
    entry_point: CallChainNode
    bridge_points: list[CallChainNode] = field(default_factory=list)
    exit_point: CallChainNode | None = None
    risk_level: str = "medium"  # low, medium, high
    impact_description: str = ""


class CompatibilityCallChainTracer:
    """兼容层调用链追踪器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.source_dir = project_root / "autoBMAD" / "docuswarm"
        self.chains: list[CompatibilityCallChain] = []
        
    def trace_all(self) -> None:
        """追踪所有兼容层调用链"""
        print("=" * 80)
        print("兼容层调用链追踪分析")
        print("=" * 80)
        print()
        
        # 追踪 SessionManager 的 legacy 参数链
        self._trace_session_manager_legacy()
        
        # 追踪 DualAgentNode 的 legacy 执行链
        self._trace_dual_agent_legacy()
        
        # 追踪 StateManager 的兼容字段链
        self._trace_state_manager_compatibility()
        
        # 追踪 Tools 的 function-style API 链
        self._trace_tools_function_style()
        
        # 生成报告
        self._generate_chain_report()
    
    def _trace_session_manager_legacy(self) -> None:
        """追踪 SessionManager legacy 参数调用链"""
        chain = CompatibilityCallChain(
            name="SessionManager Legacy Parameters",
            entry_point=CallChainNode(
                file="llm/session_manager.py",
                function="__init__",
                line=70,
                description="Entry: 接受 legacy 参数 (api_key, base_url, allowed_dirs)",
                code_snippet="def __init__(..., api_key=None, base_url=None, allowed_dirs=None, ...):"
            ),
            bridge_points=[
                CallChainNode(
                    file="llm/session_manager.py",
                    function="__init__",
                    line=99,
                    description="Bridge: 参数回退逻辑",
                    code_snippet="self._file_dirs = file_dirs or allowed_dirs or []"
                ),
                CallChainNode(
                    file="llm/session_manager.py",
                    function="allowed_dirs",
                    line=131,
                    description="Bridge: Deprecated 属性暴露",
                    code_snippet="@property\ndef allowed_dirs(self): # deprecated"
                ),
            ],
            exit_point=CallChainNode(
                file="llm/session_manager.py",
                function="_create_options",
                line=181,
                description="Exit: 参数被用于创建客户端配置",
                code_snippet="has_legacy_dirs = self._file_dirs or self._search_dirs"
            ),
            risk_level="high",
            impact_description="""
影响范围:
- 所有使用 SessionManager 的代码
- 如果同时传入新参数和 legacy 参数，回退逻辑可能导致意外行为
- 增加了配置理解成本（需要知道哪些参数是新/旧）
"""
        )
        self.chains.append(chain)
    
    def _trace_dual_agent_legacy(self) -> None:
        """追踪 DualAgentNode legacy 执行链"""
        chain = CompatibilityCallChain(
            name="DualAgentNode Legacy Execution",
            entry_point=CallChainNode(
                file="nodes/dual_agent.py",
                function="execute",
                line=300,
                description="Entry: execute() 接受 legacy 参数 (subject_context, task, pipeline_id)",
                code_snippet="async def execute(self, subject_context, task=\"\", pipeline_id=\"\", ...):"
            ),
            bridge_points=[
                CallChainNode(
                    file="nodes/dual_agent.py",
                    function="_build_execution_context_from_legacy",
                    line=227,
                    description="Bridge: 从 legacy 参数构建 execution context",
                    code_snippet="def _build_execution_context_from_legacy(self, ...):"
                ),
                CallChainNode(
                    file="nodes/dual_agent.py",
                    function="_normalize_legacy_subject_context",
                    line=203,
                    description="Bridge: 规范化 legacy subject_context",
                    code_snippet="def _normalize_legacy_subject_context(self, subject_context):"
                ),
            ],
            exit_point=CallChainNode(
                file="nodes/dual_agent.py",
                function="execute_with_context",
                line=336,
                description="Exit: 转换为新 API 执行",
                code_snippet="async def execute_with_context(self, execution_context: NodeExecutionContext):"
            ),
            risk_level="high",
            impact_description="""
影响范围:
- 所有节点执行路径
- 数据转换过程可能丢失信息或改变语义
- 增加调试难度（需要跟踪转换逻辑）
- 新旧两种调用方式并存，增加维护负担
"""
        )
        self.chains.append(chain)
    
    def _trace_state_manager_compatibility(self) -> None:
        """追踪 StateManager 兼容字段链"""
        chain = CompatibilityCallChain(
            name="StateManager State Field Compatibility",
            entry_point=CallChainNode(
                file="storage/state_manager.py",
                function="get_pipeline",
                line=380,
                description="Entry: 构建结果时保留 state 字段",
                code_snippet='"state": state,  # Keep state field for backward compatibility'
            ),
            bridge_points=[],
            exit_point=None,
            risk_level="medium",
            impact_description="""
影响范围:
- 所有读取 pipeline 状态的代码
- 数据冗余，可能导致不一致
- 增加序列化/反序列化开销
"""
        )
        self.chains.append(chain)
    
    def _trace_tools_function_style(self) -> None:
        """追踪 Tools function-style API 链"""
        chain = CompatibilityCallChain(
            name="Tools Function-Style API",
            entry_point=CallChainNode(
                file="tools/create_deliverable.py",
                function="create_deliverable",
                line=184,
                description="Entry: Function-style API 用于测试兼容",
                code_snippet="async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:"
            ),
            bridge_points=[
                CallChainNode(
                    file="tools/create_deliverable.py",
                    function="create_deliverable",
                    line=196,
                    description="Bridge: 创建工具实例并调用",
                    code_snippet="tool = CreateDeliverableTool()\nreturn await tool._execute(params)"
                ),
            ],
            exit_point=CallChainNode(
                file="tools/create_deliverable.py",
                function="CreateDeliverableTool._execute",
                line=135,
                description="Exit: 实际执行工具方法",
                code_snippet="async def _execute(self, params: CreateDeliverableParams) -> ToolResult:"
            ),
            risk_level="low",
            impact_description="""
影响范围:
- 仅测试代码和一些旧调用
- 低风险，但增加了工具理解成本
"""
        )
        self.chains.append(chain)
        
        # 另一个类似的链
        chain2 = CompatibilityCallChain(
            name="SDK Adapter Aliases",
            entry_point=CallChainNode(
                file="tools/sdk_adapter.py",
                function="adapt_to_sdk",
                line=132,
                description="Entry: 函数别名",
                code_snippet="adapt_to_sdk = adapt_to_claude  # Backward compatibility"
            ),
            bridge_points=[],
            exit_point=CallChainNode(
                file="tools/sdk_adapter.py",
                function="adapt_to_claude",
                line=15,
                description="Exit: 实际函数",
                code_snippet="def adapt_to_claude(context: dict[str, Any]) -> dict[str, Any]:"
            ),
            risk_level="low",
            impact_description="""
影响范围:
- SDK 适配层
- 增加 API 理解成本
"""
        )
        self.chains.append(chain2)
    
    def _generate_chain_report(self) -> None:
        """生成调用链报告"""
        print()
        print("=" * 80)
        print("兼容层调用链详细分析")
        print("=" * 80)
        
        for i, chain in enumerate(self.chains, 1):
            print(f"\n[{i}] {chain.name}")
            print(f"    风险级别: {chain.risk_level.upper()}")
            print()
            
            # Entry
            print(f"  ┌─ ENTRY: {chain.entry_point.file}:{chain.entry_point.line}")
            print(f"  │   Function: {chain.entry_point.function}")
            print(f"  │   {chain.entry_point.description}")
            print(f"  │   Code: {chain.entry_point.code_snippet[:60]}...")
            print()
            
            # Bridge points
            for j, bridge in enumerate(chain.bridge_points, 1):
                print(f"  ├─ BRIDGE {j}: {bridge.file}:{bridge.line}")
                print(f"  │   Function: {bridge.function}")
                print(f"  │   {bridge.description}")
                print(f"  │   Code: {bridge.code_snippet[:60]}...")
                print()
            
            # Exit
            if chain.exit_point:
                print(f"  └─ EXIT: {chain.exit_point.file}:{chain.exit_point.line}")
                print(f"      Function: {chain.exit_point.function}")
                print(f"      {chain.exit_point.description}")
                print(f"      Code: {chain.exit_point.code_snippet[:60]}...")
            
            print()
            print(f"  影响描述:")
            for line in chain.impact_description.strip().split("\n"):
                print(f"    {line}")
            print()
            print("-" * 80)
        
        # 汇总
        print()
        print("=" * 80)
        print("调用链风险汇总")
        print("=" * 80)
        
        high_risk = [c for c in self.chains if c.risk_level == "high"]
        medium_risk = [c for c in self.chains if c.risk_level == "medium"]
        low_risk = [c for c in self.chains if c.risk_level == "low"]
        
        print(f"\n高风险调用链: {len(high_risk)} 条")
        for c in high_risk:
            print(f"  - {c.name}")
        
        print(f"\n中风险调用链: {len(medium_risk)} 条")
        for c in medium_risk:
            print(f"  - {c.name}")
        
        print(f"\n低风险调用链: {len(low_risk)} 条")
        for c in low_risk:
            print(f"  - {c.name}")
        
        print()
        print("=" * 80)
        print("关键发现")
        print("=" * 80)
        print("""
1. 【执行路径分叉】
   DualAgentNode.execute() 和 execute_with_context() 同时存在，
   导致所有节点调用都有两条可能的路径，增加了理解成本和测试负担。

2. 【数据转换风险】
   _build_execution_context_from_legacy() 在运行时进行数据格式转换，
   可能引入难以发现的 bug（如字段丢失、类型转换错误）。

3. 【配置源混乱】
   SessionManager 同时接受多种配置方式（config 对象、独立参数、legacy 参数），
   优先级和回退逻辑增加了配置系统的复杂度。

4. 【隐式依赖】
   某些兼容层（如 state 字段保留）存在隐式依赖，
   难以确定哪些代码依赖了这些兼容特性。
        """)


def main():
    project_root = Path(__file__).parent.parent.parent
    tracer = CompatibilityCallChainTracer(project_root)
    tracer.trace_all()


if __name__ == "__main__":
    main()
