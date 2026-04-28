"""
DocuSwarm 优先级问题深度调试器

基于评估报告 docs/evaluation/2026-03-28-refactor-2026-03-26-deep-implementation-audit.md
对6个关键发现进行验证和诊断：
- P0: Finding 1-3 (交付物契约丢失、BMAD技能注入缺失、阈值读取问题)
- P1: Finding 4-5 (ContextValidator分裂、配置检查器语义问题)
- P2: Finding 6 (SessionManager.allowed_dirs)

用法:
    python tools/docuswarm_priority_issues_debugger.py
    python tools/docuswarm_priority_issues_debugger.py --finding 1
    python tools/docuswarm_priority_issues_debugger.py --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class FindingResult:
    """单个发现验证结果"""
    id: str
    severity: str  # P0, P1, P2
    title: str
    status: str  # CONFIRMED, PARTIAL, FIXED, UNKNOWN
    evidence: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    code_snippets: list[dict[str, str]] = field(default_factory=list)


@dataclass
class DebugReport:
    """完整调试报告"""
    timestamp: str
    findings: list[FindingResult]
    summary: dict[str, Any] = field(default_factory=dict)


class PriorityIssuesDebugger:
    """优先级问题调试器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: list[FindingResult] = []
        
    def run_all_checks(self) -> DebugReport:
        """运行所有检查"""
        from datetime import datetime
        
        # P0 级问题
        self.findings.append(self._check_finding_1())
        self.findings.append(self._check_finding_2())
        self.findings.append(self._check_finding_3())
        
        # P1 级问题
        self.findings.append(self._check_finding_4())
        self.findings.append(self._check_finding_5())
        
        # P2 级问题
        self.findings.append(self._check_finding_6())
        
        # 生成摘要
        summary = {
            "total_findings": len(self.findings),
            "p0_confirmed": sum(1 for f in self.findings if f.severity == "P0" and f.status == "CONFIRMED"),
            "p1_confirmed": sum(1 for f in self.findings if f.severity == "P1" and f.status == "CONFIRMED"),
            "p2_confirmed": sum(1 for f in self.findings if f.severity == "P2" and f.status == "CONFIRMED"),
            "overall_health": self._calculate_health_score(),
        }
        
        return DebugReport(
            timestamp=datetime.now().isoformat(),
            findings=self.findings,
            summary=summary
        )
    
    def _calculate_health_score(self) -> float:
        """计算整体健康分数"""
        if not self.findings:
            return 100.0
        
        weights = {"P0": 40, "P1": 30, "P2": 10}
        total_weight = sum(weights[f.severity] for f in self.findings)
        
        if total_weight == 0:
            return 100.0
            
        weighted_score = sum(
            weights[f.severity] * (0 if f.status == "CONFIRMED" else 1)
            for f in self.findings
        )
        
        return round((1 - weighted_score / total_weight) * 100, 2)
    
    def _check_finding_1(self) -> FindingResult:
        """
        Finding 1: Structured 执行路径会丢失交付物契约
        
        验证:
        1. ContextManager.build_independent_input() 是否构建 deliverable_requirements
        2. IndependentAgent.execute_with_input() 是否将其放入 NodeExecutionContext
        3. contract_builder._build_deliverable_section() 是否能读取到
        """
        evidence = []
        code_snippets = []
        recommendations = []
        
        # 检查 1: isolation.py 是否构建 deliverable_requirements
        isolation_path = self.project_root / "autoBMAD/docuswarm/context/isolation.py"
        if isolation_path.exists():
            content = isolation_path.read_text(encoding="utf-8")
            if "deliverable_requirements=deliverable_reqs" in content:
                evidence.append({
                    "check": "isolation.py builds deliverable_requirements",
                    "status": "PASS",
                    "detail": "build_independent_input() 正确构建 deliverable_requirements"
                })
            else:
                evidence.append({
                    "check": "isolation.py builds deliverable_requirements", 
                    "status": "FAIL",
                    "detail": "未找到 deliverable_requirements 构建代码"
                })
        
        # 检查 2: independent.py 是否将 deliverable_requirements 放入 context
        independent_path = self.project_root / "autoBMAD/docuswarm/agents/independent.py"
        if independent_path.exists():
            content = independent_path.read_text(encoding="utf-8")
            
            # 查找 NodeExecutionContext 构造
            if "NodeExecutionContext(" in content:
                # 检查是否包含 deliverable_requirements
                if "deliverable_requirements" in content:
                    evidence.append({
                        "check": "independent.py passes deliverable_requirements to context",
                        "status": "UNCLEAR",
                        "detail": "代码中包含 deliverable_requirements 但需进一步验证传递路径"
                    })
                else:
                    evidence.append({
                        "check": "independent.py passes deliverable_requirements to context",
                        "status": "FAIL",
                        "detail": "NodeExecutionContext 构造中未包含 deliverable_requirements 字段"
                    })
                    code_snippets.append({
                        "file": "autoBMAD/docuswarm/agents/independent.py",
                        "issue": "Context构建时丢失 deliverable_requirements",
                        "lines": "656-666"
                    })
                    recommendations.append(
                        "在 IndependentAgent.execute_with_input() 中将 agent_input['deliverable_requirements'] "
                        "添加到 NodeExecutionContext 构造中"
                    )
        
        # 检查 3: contract_builder 从 context 读取
        contract_builder_path = self.project_root / "autoBMAD/docuswarm/prompts/contract_builder.py"
        if contract_builder_path.exists():
            content = contract_builder_path.read_text(encoding="utf-8")
            if "context.get(\"deliverable_requirements\"" in content:
                evidence.append({
                    "check": "contract_builder reads deliverable_requirements from context",
                    "status": "PASS",
                    "detail": "_build_deliverable_section() 尝试从 context 读取"
                })
            else:
                evidence.append({
                    "check": "contract_builder reads deliverable_requirements from context",
                    "status": "FAIL",
                    "detail": "未找到从 context 读取 deliverable_requirements 的代码"
                })
        
        # 判断状态
        fail_count = sum(1 for e in evidence if e["status"] == "FAIL")
        status = "CONFIRMED" if fail_count >= 1 else "PARTIAL"
        
        return FindingResult(
            id="1",
            severity="P0",
            title="Structured 执行路径会丢失交付物契约",
            status=status,
            evidence=evidence,
            recommendations=recommendations or [
                "在 IndependentAgent.execute_with_input() 中直接使用 agent_input['deliverable_requirements']",
                "或让 NodePromptContractBuilder._build_deliverable_section() 改为从 NodeLoader.load(node_id) 读取"
            ],
            code_snippets=code_snippets or [{"file": "autoBMAD/docuswarm/agents/independent.py", "lines": "656-666", "issue": "未传递 deliverable_requirements"}]
        )
    
    def _check_finding_2(self) -> FindingResult:
        """
        Finding 2: BMAD 技能注入没有进入主执行链
        
        验证:
        1. SkillInjector 是否存在且功能正常
        2. PromptTemplateEngine 是否存在
        3. 主执行链是否使用这些组件
        """
        evidence = []
        code_snippets = []
        recommendations = []
        
        # 检查 1: SkillInjector 存在
        skill_injector_path = self.project_root / "autoBMAD/docuswarm/prompts/skill_injector.py"
        if skill_injector_path.exists():
            content = skill_injector_path.read_text(encoding="utf-8")
            if "build_skill_section" in content:
                evidence.append({
                    "check": "SkillInjector exists",
                    "status": "PASS",
                    "detail": "SkillInjector 类存在且有 build_skill_section 方法"
                })
            else:
                evidence.append({
                    "check": "SkillInjector exists",
                    "status": "FAIL",
                    "detail": "SkillInjector 存在但缺少关键方法"
                })
        
        # 检查 2: PromptTemplateEngine 存在
        template_engine_path = self.project_root / "autoBMAD/docuswarm/prompts/template_engine.py"
        if template_engine_path.exists():
            evidence.append({
                "check": "PromptTemplateEngine exists",
                "status": "PASS", 
                "detail": "PromptTemplateEngine 类存在"
            })
        
        # 检查 3: 主执行链是否使用
        independent_path = self.project_root / "autoBMAD/docuswarm/agents/independent.py"
        if independent_path.exists():
            content = independent_path.read_text(encoding="utf-8")
            
            uses_contract_builder = "contract_builder.build_independent_contract" in content
            uses_template_engine = "PromptTemplateEngine" in content or "build_system_prompt_append" in content
            uses_skill_injector = "SkillInjector" in content or "build_skill_section" in content
            
            if uses_contract_builder and not uses_template_engine:
                evidence.append({
                    "check": "Main execution chain uses PromptTemplateEngine",
                    "status": "FAIL",
                    "detail": "主执行链使用 contract_builder 而非 PromptTemplateEngine"
                })
                code_snippets.append({
                    "file": "autoBMAD/docuswarm/agents/independent.py",
                    "lines": "668-670",
                    "issue": "使用 contract_builder 而非 PromptTemplateEngine"
                })
                recommendations.append("统一 execute_with_input() 的 system prompt 生成路径，改走 PromptTemplateEngine")
            
            if not uses_skill_injector:
                evidence.append({
                    "check": "Main execution chain includes skill injection",
                    "status": "FAIL",
                    "detail": "主执行链未调用 SkillInjector"
                })
                recommendations.append("在 NodePromptContractBuilder 内显式接入 SkillInjector")
        
        # 检查 4: contract_builder 是否有技能章节
        contract_builder_path = self.project_root / "autoBMAD/docuswarm/prompts/contract_builder.py"
        if contract_builder_path.exists():
            content = contract_builder_path.read_text(encoding="utf-8")
            if "skill" in content.lower():
                evidence.append({
                    "check": "Contract builder includes skills",
                    "status": "PASS",
                    "detail": "contract_builder 包含 skill 相关代码"
                })
            else:
                evidence.append({
                    "check": "Contract builder includes skills",
                    "status": "FAIL",
                    "detail": "contract_builder 未包含技能章节"
                })
        
        fail_count = sum(1 for e in evidence if e["status"] == "FAIL")
        status = "CONFIRMED" if fail_count >= 2 else "PARTIAL"
        
        return FindingResult(
            id="2",
            severity="P0",
            title="BMAD 技能注入没有进入主执行链",
            status=status,
            evidence=evidence,
            recommendations=recommendations,
            code_snippets=code_snippets
        )
    
    def _check_finding_3(self) -> FindingResult:
        """
        Finding 3: criteria_loader.py 仍读取废弃的 thresholds
        
        验证:
        1. NodeLoader 是否读取 threshold (v2)
        2. CriteriaLoader 是否读取 thresholds (旧)
        3. 配置文件中实际使用哪个字段
        """
        evidence = []
        code_snippets = []
        recommendations = []
        
        # 检查 1: CriteriaLoader 读取的字段
        criteria_loader_path = self.project_root / "autoBMAD/docuswarm/agents/evaluator_config/criteria_loader.py"
        if criteria_loader_path.exists():
            content = criteria_loader_path.read_text(encoding="utf-8")
            
            if 'data.get("thresholds")' in content:
                evidence.append({
                    "check": "CriteriaLoader reads correct field",
                    "status": "FAIL",
                    "detail": "CriteriaLoader 仍读取废弃的 'thresholds' 而非 'threshold'"
                })
                code_snippets.append({
                    "file": "autoBMAD/docuswarm/agents/evaluator_config/criteria_loader.py",
                    "lines": "104-105",
                    "issue": "读取 thresholds 而非 threshold"
                })
                recommendations.append("将 criteria_loader.py 升级为优先读 'threshold'，兼容读 'thresholds'")
            elif 'data.get("threshold")' in content:
                evidence.append({
                    "check": "CriteriaLoader reads correct field",
                    "status": "PASS",
                    "detail": "CriteriaLoader 已更新为读取 'threshold'"
                })
            
        # 检查 2: 配置文件中使用的字段
        nodes_dir = self.project_root / "autoBMAD/nodes"
        threshold_usage = {"threshold": 0, "thresholds": 0}
        
        for node_dir in nodes_dir.iterdir():
            if node_dir.is_dir():
                evaluator_file = node_dir / "evaluator.yaml"
                if evaluator_file.exists():
                    content = evaluator_file.read_text(encoding="utf-8")
                    if "threshold:" in content and "thresholds:" not in content:
                        threshold_usage["threshold"] += 1
                    elif "thresholds:" in content:
                        threshold_usage["thresholds"] += 1
        
        evidence.append({
            "check": "Config files use v2 'threshold' field",
            "status": "PASS" if threshold_usage["threshold"] > 0 else "INFO",
            "detail": f"找到 {threshold_usage['threshold']} 个节点使用 'threshold', "
                     f"{threshold_usage['thresholds']} 个节点使用 'thresholds'"
        })
        
        # 检查 3: NodeLoader 读取的字段
        node_loader_path = self.project_root / "autoBMAD/nodes/loader.py"
        if node_loader_path.exists():
            content = node_loader_path.read_text(encoding="utf-8")
            if "threshold" in content:
                evidence.append({
                    "check": "NodeLoader reads threshold",
                    "status": "PASS",
                    "detail": "NodeLoader 包含 threshold 读取逻辑"
                })
        
        status = "CONFIRMED" if any(e["status"] == "FAIL" for e in evidence) else "FIXED"
        
        return FindingResult(
            id="3",
            severity="P0",
            title="criteria_loader.py 仍读取废弃的 thresholds",
            status=status,
            evidence=evidence,
            recommendations=recommendations or ["明确废弃整个 evaluator_config 子模块，避免形成错误备用路径"],
            code_snippets=code_snippets
        )
    
    def _check_finding_4(self) -> FindingResult:
        """
        Finding 4: ContextValidator 的"节点级规则注册"与"实际校验实例"分裂
        
        验证:
        1. NodeLoader 是否注册规则到 singleton
        2. 实际使用时是否创建新实例
        """
        evidence = []
        code_snippets = []
        recommendations = []
        
        # 检查 1: NodeLoader 注册到 singleton
        node_loader_path = self.project_root / "autoBMAD/nodes/loader.py"
        if node_loader_path.exists():
            content = node_loader_path.read_text(encoding="utf-8")
            if "ContextValidator.get_instance()" in content and "load_node_rules" in content:
                evidence.append({
                    "check": "NodeLoader registers to singleton",
                    "status": "PASS",
                    "detail": "NodeLoader 使用 get_instance() 并调用 load_node_rules"
                })
            else:
                evidence.append({
                    "check": "NodeLoader registers to singleton",
                    "status": "FAIL",
                    "detail": "NodeLoader 未正确注册规则"
                })
        
        # 检查 2: isolation.py 是否创建新实例
        isolation_path = self.project_root / "autoBMAD/docuswarm/context/isolation.py"
        if isolation_path.exists():
            content = isolation_path.read_text(encoding="utf-8")
            
            # 查找直接实例化
            if "ContextValidator()" in content:
                evidence.append({
                    "check": "isolation.py creates fresh instance",
                    "status": "FAIL",
                    "detail": "isolation.py 直接创建新实例而非使用 singleton"
                })
                code_snippets.append({
                    "file": "autoBMAD/docuswarm/context/isolation.py",
                    "lines": "90-95",
                    "issue": "直接创建 ContextValidator() 而非 get_instance()"
                })
                recommendations.append("全仓统一使用 ContextValidator.get_instance()")
            elif "get_instance()" in content:
                evidence.append({
                    "check": "isolation.py uses singleton",
                    "status": "PASS",
                    "detail": "isolation.py 使用 get_instance()"
                })
        
        # 检查 3: independent.py 是否创建新实例
        independent_path = self.project_root / "autoBMAD/docuswarm/agents/independent.py"
        if independent_path.exists():
            content = independent_path.read_text(encoding="utf-8")
            if "ContextValidator()" in content:
                evidence.append({
                    "check": "independent.py creates fresh instance",
                    "status": "FAIL",
                    "detail": "independent.py 直接创建新实例"
                })
                code_snippets.append({
                    "file": "autoBMAD/docuswarm/agents/independent.py",
                    "issue": "直接创建 ContextValidator() 实例"
                })
        
        # 检查 4: evaluator.py 是否创建新实例  
        evaluator_path = self.project_root / "autoBMAD/docuswarm/agents/evaluator.py"
        if evaluator_path.exists():
            content = evaluator_path.read_text(encoding="utf-8")
            if "ContextValidator()" in content:
                evidence.append({
                    "check": "evaluator.py creates fresh instance",
                    "status": "FAIL",
                    "detail": "evaluator.py 直接创建新实例"
                })
        
        fail_count = sum(1 for e in evidence if e["status"] == "FAIL")
        status = "CONFIRMED" if fail_count >= 2 else "PARTIAL"
        
        return FindingResult(
            id="4",
            severity="P1",
            title="ContextValidator 的节点级规则注册与实际校验实例分裂",
            status=status,
            evidence=evidence,
            recommendations=recommendations or ["通过依赖注入把 validator 从 orchestrator/context manager 传到底层"],
            code_snippets=code_snippets
        )
    
    def _check_finding_5(self) -> FindingResult:
        """
        Finding 5: 节点配置检查器对"语义不一致"过于乐观
        
        验证:
        1. 检查 architect 节点的 sections 不一致问题
        2. 检查检查器是否正确识别
        """
        evidence = []
        code_snippets = []
        recommendations = []
        
        # 检查 1: architect node.yaml sections
        architect_node = self.project_root / "autoBMAD/nodes/architect/node.yaml"
        architect_persona = self.project_root / "autoBMAD/nodes/architect/persona.json"
        
        node_sections = []
        persona_sections = []
        
        if architect_node.exists():
            import yaml
            with open(architect_node, encoding="utf-8") as f:
                node_data = yaml.safe_load(f)
                node_sections = node_data.get("deliverable", {}).get("required_sections", [])
            
            evidence.append({
                "check": "architect node.yaml sections",
                "status": "INFO",
                "detail": f"node.yaml 定义 {len(node_sections)} 个 sections: {node_sections}"
            })
        
        if architect_persona.exists():
            import json
            with open(architect_persona, encoding="utf-8") as f:
                persona_data = json.load(f)
                persona_sections = persona_data.get("output_format", {}).get("sections", [])
            
            evidence.append({
                "check": "architect persona.json sections",
                "status": "INFO", 
                "detail": f"persona.json 定义 {len(persona_sections)} 个 sections: {persona_sections}"
            })
        
        # 检查是否一致
        if node_sections and persona_sections:
            if set(node_sections) != set(persona_sections):
                evidence.append({
                    "check": "Sections consistency between node.yaml and persona.json",
                    "status": "FAIL",
                    "detail": f"不匹配: node.yaml 有 {len(node_sections)} 个, persona.json 有 {len(persona_sections)} 个"
                })
                code_snippets.append({
                    "file": "autoBMAD/nodes/architect/node.yaml",
                    "lines": "22-29",
                    "issue": f"required_sections: {node_sections}"
                })
                code_snippets.append({
                    "file": "autoBMAD/nodes/architect/persona.json",
                    "lines": "45-57",
                    "issue": f"output_format.sections: {persona_sections}"
                })
                recommendations.append("将跨文件语义一致性纳入 node_config_completeness_checker 得分")
                recommendations.append("architect 节点的 sections 不匹配应至少降低 compliance 分")
            else:
                evidence.append({
                    "check": "Sections consistency",
                    "status": "PASS",
                    "detail": "node.yaml 和 persona.json 的 sections 一致"
                })
        
        # 检查 2: 检查器是否过于乐观
        checker_path = self.project_root / "tools/node_config_completeness_checker.py"
        if checker_path.exists():
            content = checker_path.read_text(encoding="utf-8")
            if "cross_file_consistency" in content or "semantic" in content.lower():
                evidence.append({
                    "check": "Checker includes semantic validation",
                    "status": "PASS",
                    "detail": "检查器包含语义一致性检查"
                })
            else:
                evidence.append({
                    "check": "Checker includes semantic validation",
                    "status": "FAIL",
                    "detail": "检查器缺少跨文件语义一致性检查"
                })
        
        status = "CONFIRMED" if any(e["status"] == "FAIL" for e in evidence) else "PARTIAL"
        
        return FindingResult(
            id="5",
            severity="P1",
            title="节点配置检查器对语义不一致过于乐观",
            status=status,
            evidence=evidence,
            recommendations=recommendations,
            code_snippets=code_snippets
        )
    
    def _check_finding_6(self) -> FindingResult:
        """
        Finding 6: SessionManager.allowed_dirs 属性存在未定义字段访问
        
        验证:
        1. allowed_dirs 属性是否访问 _allowed_dirs
        2. __init__ 是否定义 _allowed_dirs
        """
        evidence = []
        code_snippets = []
        recommendations = []
        
        session_manager_path = self.project_root / "autoBMAD/docuswarm/llm/session_manager.py"
        if session_manager_path.exists():
            content = session_manager_path.read_text(encoding="utf-8")
            
            # 检查 allowed_dirs 属性
            if "self._file_dirs or self._allowed_dirs" in content:
                evidence.append({
                    "check": "allowed_dirs property accesses _allowed_dirs",
                    "status": "CONFIRMED",
                    "detail": "allowed_dirs 属性访问未定义的 _allowed_dirs"
                })
                code_snippets.append({
                    "file": "autoBMAD/docuswarm/llm/session_manager.py",
                    "lines": "128-131",
                    "issue": "return self._file_dirs or self._allowed_dirs"
                })
            
            # 检查 __init__ 是否定义 _allowed_dirs
            if "self._allowed_dirs" in content:
                # 需要判断是否在 __init__ 中定义
                lines = content.split("\n")
                in_init = False
                init_has_allowed_dirs = False
                
                for line in lines:
                    if "def __init__" in line:
                        in_init = True
                    elif in_init and line.strip().startswith("def "):
                        in_init = False
                    elif in_init and "self._allowed_dirs" in line:
                        init_has_allowed_dirs = True
                        break
                
                if init_has_allowed_dirs:
                    evidence.append({
                        "check": "__init__ defines _allowed_dirs",
                        "status": "PASS",
                        "detail": "__init__ 中定义了 _allowed_dirs"
                    })
                else:
                    evidence.append({
                        "check": "__init__ defines _allowed_dirs",
                        "status": "FAIL",
                        "detail": "__init__ 中未定义 _allowed_dirs，会导致 AttributeError"
                    })
                    recommendations.append("直接删除该兼容属性 allowed_dirs")
                    recommendations.append("或在 __init__ 中显式保存 allowed_dirs")
            
        status = "CONFIRMED" if any(e["status"] == "FAIL" for e in evidence) else "FIXED"
        
        return FindingResult(
            id="6",
            severity="P2",
            title="SessionManager.allowed_dirs 属性存在未定义字段访问",
            status=status,
            evidence=evidence,
            recommendations=recommendations,
            code_snippets=code_snippets
        )


def print_report(report: DebugReport, format_type: str = "text"):
    """打印报告"""
    import io
    import sys
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    
    if format_type == "json":
        # 转换为可序列化的字典
        report_dict = {
            "timestamp": report.timestamp,
            "summary": report.summary,
            "findings": [
                {
                    "id": f.id,
                    "severity": f.severity,
                    "title": f.title,
                    "status": f.status,
                    "evidence": f.evidence,
                    "recommendations": f.recommendations,
                    "code_snippets": f.code_snippets,
                }
                for f in report.findings
            ]
        }
        print(json.dumps(report_dict, indent=2, ensure_ascii=False))
    else:
        print("=" * 80)
        print("DocuSwarm 优先级问题深度调试报告")
        print("=" * 80)
        print(f"生成时间: {report.timestamp}")
        print()
        
        print("📊 摘要")
        print("-" * 40)
        for key, value in report.summary.items():
            print(f"  {key}: {value}")
        print()
        
        # 按严重级别分组
        for severity in ["P0", "P1", "P2"]:
            findings = [f for f in report.findings if f.severity == severity]
            if not findings:
                continue
                
            emoji = "🔴" if severity == "P0" else "🟡" if severity == "P1" else "🟢"
            print(f"{emoji} {severity} 级发现")
            print("-" * 40)
            
            for f in findings:
                status_emoji = "✅" if f.status == "FIXED" else "❌" if f.status == "CONFIRMED" else "⚠️"
                print(f"\n  Finding {f.id}: {f.title}")
                print(f"  状态: {status_emoji} {f.status}")
                
                if f.evidence:
                    print(f"\n  证据:")
                    for e in f.evidence:
                        e_emoji = "✅" if e["status"] == "PASS" else "❌" if e["status"] == "FAIL" else "ℹ️"
                        print(f"    {e_emoji} {e['check']}: {e['detail']}")
                
                if f.code_snippets:
                    print(f"\n  相关代码:")
                    for cs in f.code_snippets:
                        print(f"    - {cs['file']}:{cs.get('lines', 'N/A')}")
                        if 'issue' in cs:
                            print(f"      问题: {cs['issue']}")
                
                if f.recommendations:
                    print(f"\n  建议:")
                    for r in f.recommendations:
                        print(f"    • {r}")
            
            print()
        
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="DocuSwarm 优先级问题调试器")
    parser.add_argument("--finding", type=int, choices=[1, 2, 3, 4, 5, 6],
                        help="仅检查特定 finding")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="输出格式")
    parser.add_argument("--output", type=str,
                        help="输出文件路径")
    
    args = parser.parse_args()
    
    debugger = PriorityIssuesDebugger(PROJECT_ROOT)
    
    if args.finding:
        # 仅运行特定检查
        method = getattr(debugger, f"_check_finding_{args.finding}")
        finding = method()
        report = DebugReport(
            timestamp="__NA__",
            findings=[finding],
            summary={}
        )
    else:
        report = debugger.run_all_checks()
    
    print_report(report, args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if args.format == "json":
            report_dict = {
                "timestamp": report.timestamp,
                "summary": report.summary,
                "findings": [
                    {
                        "id": f.id,
                        "severity": f.severity,
                        "title": f.title,
                        "status": f.status,
                        "evidence": f.evidence,
                        "recommendations": f.recommendations,
                        "code_snippets": f.code_snippets,
                    }
                    for f in report.findings
                ]
            }
            output_path.write_text(json.dumps(report_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            # 文本格式需要重新生成
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            print_report(report, "text")
            text_output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            output_path.write_text(text_output, encoding="utf-8")
        
        print(f"\n报告已保存到: {args.output}")


if __name__ == "__main__":
    main()
