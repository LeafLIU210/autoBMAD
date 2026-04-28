#!/usr/bin/env python3
"""Pipeline 与 Node Execution 双主干语义分析工具 (F5 Research Tool).

该工具用于深度分析 `pipeline` 与 `node_execution` 两个模块的语义重叠问题，
帮助诊断执行路径分叉、fallback 兜底路径、以及边界适配层的健康状况。

用法:
    python tools/pipeline_node_execution_analyzer.py --mode all
    python tools/pipeline_node_execution_analyzer.py --mode boundary
    python tools/pipeline_node_execution_analyzer.py --mode fallback
    python tools/pipeline_node_execution_analyzer.py --mode state-comparison
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class SemanticOverlap:
    """语义重叠检测结果"""
    concept: str  # 概念名称 (e.g., "graph", "state", "metrics")
    pipeline_files: list[str] = field(default_factory=list)
    node_execution_files: list[str] = field(default_factory=list)
    overlap_type: str = ""  # "identical", "similar", "ambiguous"


@dataclass
class FallbackPath:
    """Fallback 路径检测"""
    location: str  # 文件位置
    line_number: int
    fallback_type: str  # "deprecated", "silent", "backward_compat"
    description: str
    has_warning: bool = False


@dataclass
class BoundaryViolation:
    """边界违规检测"""
    location: str
    violation_type: str  # "direct_access", "synthetic_id_creation", "state_bypass"
    description: str
    recommendation: str


@dataclass
class AnalysisResult:
    """分析结果"""
    semantic_overlaps: list[SemanticOverlap] = field(default_factory=list)
    fallback_paths: list[FallbackPath] = field(default_factory=list)
    boundary_violations: list[BoundaryViolation] = field(default_factory=list)
    pipeline_adapter_usage: dict[str, Any] = field(default_factory=dict)
    state_conversion_paths: list[dict[str, Any]] = field(default_factory=list)


def find_pipeline_files() -> list[Path]:
    """查找 pipeline 模块下的所有 Python 文件"""
    pipeline_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline"
    return list(pipeline_path.glob("*.py")) if pipeline_path.exists() else []


def find_node_execution_files() -> list[Path]:
    """查找 node_execution 模块下的所有 Python 文件"""
    ne_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution"
    return list(ne_path.glob("*.py")) if ne_path.exists() else []


def analyze_semantic_overlaps() -> list[SemanticOverlap]:
    """分析两个模块之间的语义重叠"""
    overlaps = []
    
    # 定义需要检测的核心概念
    core_concepts = {
        "graph": ["StateGraph", "create_graph", "add_node", "add_edge"],
        "state": ["PipelineState", "NodeRunState", "create_initial_state", "validate_state"],
        "metrics": ["MetricsCollector", "record_metric", "get_metrics"],
        "escalation": ["EscalationManager", "escalate", "should_escalate"],
        "executor": ["node_executor", "create_node_executor", "execute_node"],
        "checkpoint": ["checkpointer", "SqliteSaver", "checkpoint"],
    }
    
    pipeline_files = find_pipeline_files()
    node_execution_files = find_node_execution_files()
    
    for concept, keywords in core_concepts.items():
        overlap = SemanticOverlap(concept=concept)
        
        # 检查 pipeline 模块
        for f in pipeline_files:
            try:
                content = f.read_text(encoding="utf-8")
                if any(kw in content for kw in keywords):
                    overlap.pipeline_files.append(f.name)
            except Exception:
                pass
        
        # 检查 node_execution 模块
        for f in node_execution_files:
            try:
                content = f.read_text(encoding="utf-8")
                if any(kw in content for kw in keywords):
                    overlap.node_execution_files.append(f.name)
            except Exception:
                pass
        
        # 如果两边都有这个概念，标记为重叠
        if overlap.pipeline_files and overlap.node_execution_files:
            if overlap.pipeline_files == overlap.node_execution_files:
                overlap.overlap_type = "identical"
            elif set(overlap.pipeline_files) & set(overlap.node_execution_files):
                overlap.overlap_type = "similar"
            else:
                overlap.overlap_type = "ambiguous"
            overlaps.append(overlap)
    
    return overlaps


def analyze_fallback_paths() -> list[FallbackPath]:
    """分析 fallback/deprecated 路径"""
    fallbacks = []
    
    # 重点检查 pipeline/graph.py
    graph_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
    if graph_path.exists():
        try:
            content = graph_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for i, line in enumerate(lines, 1):
                # 检测 deprecated 函数
                if "deprecated" in line.lower() or "_create_default_node_executor" in line:
                    if "warnings.warn" in line or "DeprecationWarning" in line:
                        fallbacks.append(FallbackPath(
                            location=f"pipeline/graph.py:{i}",
                            line_number=i,
                            fallback_type="deprecated",
                            description="Deprecated default executor with warning",
                            has_warning=True
                        ))
                
                # 检测静默兜底
                if "fallback" in line.lower() or "falling_back" in line.lower():
                    fallbacks.append(FallbackPath(
                        location=f"pipeline/graph.py:{i}",
                        line_number=i,
                        fallback_type="silent",
                        description=f"Fallback path: {line.strip()}",
                        has_warning="warning" in line.lower()
                    ))
                
                # 检测 backward compatibility
                if "backward" in line.lower() and "compat" in line.lower():
                    fallbacks.append(FallbackPath(
                        location=f"pipeline/graph.py:{i}",
                        line_number=i,
                        fallback_type="backward_compat",
                        description=f"Backward compatibility: {line.strip()}",
                        has_warning=False
                    ))
        except Exception as e:
            fallbacks.append(FallbackPath(
                location="pipeline/graph.py",
                line_number=0,
                fallback_type="error",
                description=f"Error analyzing file: {e}",
                has_warning=False
            ))
    
    # 检查 create_pipeline_graph 的 session_manager 参数处理
    if graph_path.exists():
        try:
            content = graph_path.read_text(encoding="utf-8")
            if "session_manager is not None" in content:
                # 找到条件判断的位置
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "use_integrated = session_manager is not None" in line:
                        fallbacks.append(FallbackPath(
                            location=f"pipeline/graph.py:{i}",
                            line_number=i,
                            fallback_type="conditional",
                            description="Runtime selection between integrated vs default executor",
                            has_warning=True
                        ))
        except Exception:
            pass
    
    return fallbacks


def analyze_boundary_violations() -> list[BoundaryViolation]:
    """分析边界违规 - 应该通过 PipelineAdapter 但却直接访问的情况"""
    violations = []
    
    # 检查 node_execution 模块是否直接创建 synthetic pipeline_id
    ne_files = find_node_execution_files()
    for f in ne_files:
        if f.name == "pipeline_adapter.py":
            continue  # Adapter 本身是被允许的
        
        try:
            content = f.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for i, line in enumerate(lines, 1):
                # 检测直接拼接 synthetic pipeline_id
                if 'f"node-' in line or "f'node-" in line:
                    if "PipelineAdapter" not in content[:500]:  # 没有导入 Adapter
                        violations.append(BoundaryViolation(
                            location=f"node_execution/{f.name}:{i}",
                            violation_type="synthetic_id_creation",
                            description=f"Direct synthetic ID creation: {line.strip()}",
                            recommendation="Use PipelineAdapter.create_pipeline_id() instead"
                        ))
        except Exception:
            pass
    
    # 检查 flow.py 中的 synthetic pipeline_id 创建
    flow_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "flow.py"
    if flow_path.exists():
        try:
            content = flow_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for i, line in enumerate(lines, 1):
                if 'f"node-' in line or "f'node-" in line or 'f"node-run-' in line:
                    violations.append(BoundaryViolation(
                        location=f"node_execution/flow.py:{i}",
                        violation_type="synthetic_id_creation",
                        description=f"Synthetic pipeline_id in flow.py: {line.strip()}",
                        recommendation="Use PipelineAdapter.create_pipeline_id() or create_run_pipeline_id()"
                    ))
        except Exception:
            pass
    
    return violations


def analyze_pipeline_adapter() -> dict[str, Any]:
    """分析 PipelineAdapter 的使用情况"""
    result = {
        "adapter_exists": False,
        "methods": [],
        "usage_locations": [],
        "unused_methods": [],
    }
    
    adapter_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "pipeline_adapter.py"
    if not adapter_path.exists():
        return result
    
    result["adapter_exists"] = True
    
    try:
        content = adapter_path.read_text(encoding="utf-8")
        
        # 提取方法定义
        import ast
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_"):
                    continue
                result["methods"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "is_staticmethod": any(
                        isinstance(d, ast.Name) and d.id == "staticmethod"
                        for d in node.decorator_list
                    )
                })
        
        # 检查谁在使用 PipelineAdapter
        docuswarm_path = PROJECT_ROOT / "autoBMAD" / "docuswarm"
        for py_file in docuswarm_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                file_content = py_file.read_text(encoding="utf-8")
                if "PipelineAdapter" in file_content and py_file != adapter_path:
                    rel_path = py_file.relative_to(PROJECT_ROOT)
                    result["usage_locations"].append(str(rel_path))
            except Exception:
                pass
        
        # 检查哪些方法可能没有被使用
        all_methods = {m["name"] for m in result["methods"]}
        used_methods = set()
        
        for py_file in docuswarm_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file == adapter_path:
                continue
            try:
                file_content = py_file.read_text(encoding="utf-8")
                for method in all_methods:
                    if f"PipelineAdapter.{method}" in file_content:
                        used_methods.add(method)
            except Exception:
                pass
        
        result["unused_methods"] = list(all_methods - used_methods)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def analyze_state_conversion() -> list[dict[str, Any]]:
    """分析 PipelineState <-> NodeRunState 转换路径"""
    conversions = []
    
    # 检查 pipeline/graph.py 中的转换函数
    graph_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
    if graph_path.exists():
        try:
            content = graph_path.read_text(encoding="utf-8")
            
            # 检测转换函数
            if "_convert_pipeline_to_node_state" in content:
                conversions.append({
                    "direction": "pipeline -> node_execution",
                    "location": "pipeline/graph.py:_convert_pipeline_to_node_state",
                    "responsible": "pipeline module"
                })
            
            if "_convert_node_to_pipeline_state" in content:
                conversions.append({
                    "direction": "node_execution -> pipeline",
                    "location": "pipeline/graph.py:_convert_node_to_pipeline_state",
                    "responsible": "pipeline module"
                })
            
            if "adapt_state" in content:
                conversions.append({
                    "direction": "node_execution -> pipeline",
                    "location": "pipeline/graph.py:adapt_state (if exists)",
                    "responsible": "ambiguous"
                })
        except Exception:
            pass
    
    # 检查 adapter 中的转换
    adapter_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "node_execution" / "pipeline_adapter.py"
    if adapter_path.exists():
        try:
            content = adapter_path.read_text(encoding="utf-8")
            
            if "adapt_state" in content:
                conversions.append({
                    "direction": "node_execution -> pipeline",
                    "location": "node_execution/pipeline_adapter.py:adapt_state",
                    "responsible": "PipelineAdapter (correct boundary)"
                })
        except Exception:
            pass
    
    return conversions


def analyze_create_pipeline_graph() -> dict[str, Any]:
    """深度分析 create_pipeline_graph 函数的执行路径"""
    result = {
        "function_exists": False,
        "parameters": [],
        "execution_paths": [],
        "issues": []
    }
    
    graph_path = PROJECT_ROOT / "autoBMAD" / "docuswarm" / "pipeline" / "graph.py"
    if not graph_path.exists():
        return result
    
    try:
        content = graph_path.read_text(encoding="utf-8")
        result["function_exists"] = "def create_pipeline_graph(" in content
        
        # 检查参数
        if "session_manager: Any | None = None" in content:
            result["parameters"].append({
                "name": "session_manager",
                "type": "Any | None",
                "default": "None",
                "nullable": True
            })
        
        # 检查执行路径
        if "use_integrated = session_manager is not None" in content:
            result["execution_paths"].append({
                "condition": "session_manager is not None",
                "path": "integrated executor (node_execution.executor)",
                "health": "recommended"
            })
            result["execution_paths"].append({
                "condition": "session_manager is None",
                "path": "default executor (deprecated)",
                "health": "deprecated"
            })
        
        # 检查 issue
        if "use_integrated" not in content or "session_manager is not None" not in content:
            result["issues"].append("Missing explicit integrated vs default selection")
        
        # 检查 silent fallback
        if "falling_back_to_default_executor" in content or "backward compatibility" in content.lower():
            result["issues"].append("Silent fallback to deprecated executor exists")
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def print_analysis(result: AnalysisResult) -> None:
    """打印分析结果"""
    print("=" * 80)
    print("Pipeline vs Node Execution 双主干语义分析报告 (F5 Research Tool)")
    print("=" * 80)
    print()
    
    # 1. 语义重叠分析
    print("## 1. 语义重叠分析")
    print("-" * 80)
    if result.semantic_overlaps:
        for overlap in result.semantic_overlaps:
            print(f"\n概念: {overlap.concept} (类型: {overlap.overlap_type})")
            print(f"  Pipeline 模块: {', '.join(overlap.pipeline_files)}")
            print(f"  Node Execution 模块: {', '.join(overlap.node_execution_files)}")
            if overlap.overlap_type == "identical":
                print("  ⚠️  两边使用完全相同的文件名，极易混淆")
            elif overlap.overlap_type == "similar":
                print("  ⚠️  概念在两边都有实现，存在重复责任")
            elif overlap.overlap_type == "ambiguous":
                print("  ⚠️  语义分散在不同文件中，责任边界模糊")
    else:
        print("未检测到明显的语义重叠")
    print()
    
    # 2. Fallback 路径分析
    print("## 2. Fallback / Deprecated 路径分析")
    print("-" * 80)
    if result.fallback_paths:
        for fb in result.fallback_paths:
            warning_icon = "⚠️" if fb.has_warning else "❌"
            print(f"\n{warning_icon} [{fb.fallback_type.upper()}] {fb.location}")
            print(f"   描述: {fb.description}")
            if not fb.has_warning and fb.fallback_type == "deprecated":
                print("   🔴 严重: Deprecated 路径没有告警或硬失败")
    else:
        print("未检测到 fallback 路径")
    print()
    
    # 3. 边界违规分析
    print("## 3. 边界违规分析 (PipelineAdapter 应该是唯一边界)")
    print("-" * 80)
    if result.boundary_violations:
        for v in result.boundary_violations:
            print(f"\n❌ [{v.violation_type}] {v.location}")
            print(f"   问题: {v.description}")
            print(f"   建议: {v.recommendation}")
    else:
        print("✅ 未发现明显的边界违规")
    print()
    
    # 4. PipelineAdapter 使用情况
    print("## 4. PipelineAdapter 使用情况")
    print("-" * 80)
    adapter = result.pipeline_adapter_usage
    if adapter.get("adapter_exists"):
        print(f"\nAdapter 存在: ✅")
        print(f"方法数量: {len(adapter.get('methods', []))}")
        for method in adapter.get('methods', []):
            static_mark = "[静态]" if method.get("is_staticmethod") else "[实例]"
            print(f"  - {static_mark} {method['name']} (行 {method['line']})")
        
        print(f"\n使用位置 ({len(adapter.get('usage_locations', []))} 处):")
        for loc in adapter.get('usage_locations', []):
            print(f"  - {loc}")
        
        if adapter.get('unused_methods'):
            print(f"\n⚠️  可能未使用的方法: {', '.join(adapter['unused_methods'])}")
    else:
        print("❌ PipelineAdapter 不存在")
    print()
    
    # 5. 状态转换路径
    print("## 5. PipelineState <-> NodeRunState 转换路径")
    print("-" * 80)
    for conv in result.state_conversion_paths:
        direction_icon = "→" if "->" in conv["direction"] else "↔"
        print(f"\n{direction_icon} {conv['direction']}")
        print(f"   位置: {conv['location']}")
        print(f"   责任方: {conv['responsible']}")
    print()


def print_recommendations(result: AnalysisResult) -> None:
    """打印建议"""
    print("=" * 80)
    print("治理建议")
    print("=" * 80)
    print()
    
    recommendations = []
    
    # 基于 fallback 路径的建议
    silent_deprecations = [fb for fb in result.fallback_paths 
                          if fb.fallback_type == "deprecated" and not fb.has_warning]
    if silent_deprecations:
        recommendations.append({
            "priority": "P0",
            "category": "Hard Failure",
            "description": "立即为所有 deprecated fallback 添加硬失败或告警",
            "locations": [fb.location for fb in silent_deprecations]
        })
    
    # 基于边界违规的建议
    if result.boundary_violations:
        recommendations.append({
            "priority": "P0",
            "category": "Boundary Enforcement",
            "description": "所有 synthetic pipeline_id 创建必须通过 PipelineAdapter",
            "count": len(result.boundary_violations)
        })
    
    # 基于语义重叠的建议
    ambiguous_overlaps = [o for o in result.semantic_overlaps if o.overlap_type == "ambiguous"]
    if ambiguous_overlaps:
        recommendations.append({
            "priority": "P1",
            "category": "Responsibility Clarification",
            "description": "明确 pipeline 负责编排、node_execution 负责节点执行的职责边界",
            "overlaps": [o.concept for o in ambiguous_overlaps]
        })
    
    # 基于 Adapter 的建议
    adapter = result.pipeline_adapter_usage
    if adapter.get("unused_methods"):
        recommendations.append({
            "priority": "P1",
            "category": "Adapter Utilization",
            "description": "推广使用 PipelineAdapter 中未充分利用的方法",
            "methods": adapter.get("unused_methods")
        })
    
    for rec in recommendations:
        print(f"[{rec['priority']}] {rec['category']}")
        print(f"  描述: {rec['description']}")
        if 'locations' in rec:
            print(f"  位置: {', '.join(rec['locations'][:3])}")
        if 'count' in rec:
            print(f"  数量: {rec['count']}")
        if 'overlaps' in rec:
            print(f"  概念: {', '.join(rec['overlaps'])}")
        if 'methods' in rec:
            print(f"  方法: {', '.join(rec['methods'])}")
        print()


def generate_json_report(result: AnalysisResult) -> str:
    """生成 JSON 格式的报告"""
    return json.dumps({
        "semantic_overlaps": [
            {
                "concept": o.concept,
                "pipeline_files": o.pipeline_files,
                "node_execution_files": o.node_execution_files,
                "overlap_type": o.overlap_type
            }
            for o in result.semantic_overlaps
        ],
        "fallback_paths": [
            {
                "location": f.location,
                "line_number": f.line_number,
                "fallback_type": f.fallback_type,
                "description": f.description,
                "has_warning": f.has_warning
            }
            for f in result.fallback_paths
        ],
        "boundary_violations": [
            {
                "location": v.location,
                "violation_type": v.violation_type,
                "description": v.description,
                "recommendation": v.recommendation
            }
            for v in result.boundary_violations
        ],
        "pipeline_adapter_usage": result.pipeline_adapter_usage,
        "state_conversion_paths": result.state_conversion_paths
    }, indent=2, ensure_ascii=False)


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Pipeline 与 Node Execution 双主干语义分析工具"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "boundary", "fallback", "state-comparison", "adapter"],
        default="all",
        help="分析模式"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式"
    )
    parser.add_argument(
        "--output",
        help="输出文件路径"
    )
    
    args = parser.parse_args()
    
    result = AnalysisResult()
    
    if args.mode in ["all", "boundary"]:
        result.semantic_overlaps = analyze_semantic_overlaps()
        result.boundary_violations = analyze_boundary_violations()
    
    if args.mode in ["all", "fallback"]:
        result.fallback_paths = analyze_fallback_paths()
    
    if args.mode in ["all", "state-comparison"]:
        result.state_conversion_paths = analyze_state_conversion()
    
    if args.mode in ["all", "adapter"]:
        result.pipeline_adapter_usage = analyze_pipeline_adapter()
    
    # 额外的深度分析
    if args.mode == "all":
        graph_analysis = analyze_create_pipeline_graph()
        result.pipeline_adapter_usage["create_pipeline_graph_analysis"] = graph_analysis
    
    if args.json:
        content = generate_json_report(result)
    else:
        import io
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        print_analysis(result)
        print_recommendations(result)
        sys.stdout = old_stdout
        content = buf.getvalue()
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(content, encoding="utf-8")
        print(f"报告已保存到: {output_path}")
    else:
        print(content)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
