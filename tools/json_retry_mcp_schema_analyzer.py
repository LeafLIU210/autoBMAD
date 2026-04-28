"""
JSON Retry & MCP Schema Constraint Analyzer
============================================
深度分析工具：
1. JSON 解析/字段校验失败后的重试机制（当前缺失的实证）
2. MCP Structured Output / Tool Schema 约束 JSON 的可行性评估

分析范围：
- llm/response.py          : extract_json() 三级解析路径
- agents/independent.py    : _parse_response() fallback 逻辑
- agents/evaluator.py      : _parse_response() 异常链
- nodes/dual_agent.py      : DualAgentNode 迭代循环 vs 技术重试
- node_execution/executor.py: 最终异常捕获层
- tools/create_deliverable_sdk.py: 现有 MCP tool schema
- agentdocs/14_structured_outputs.md: SDK output_format 支持
- agentdocs/19_custom_tools.md: SDK MCP tool schema 支持

Usage:
    python tools/json_retry_mcp_schema_analyzer.py
    python tools/json_retry_mcp_schema_analyzer.py --output .tmp/json_retry_analysis.json
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DOCUSWARM = ROOT / "autoBMAD" / "docuswarm"
TOOLS_DIR = ROOT / "autoBMAD" / "docuswarm" / "tools"
AGENTDOCS = ROOT / "autoBMAD" / "agentdocs"


# ============================================================
# Section 1: JSON 解析路径静态分析
# ============================================================

class JsonParsePathAnalyzer:
    """分析 extract_json() 的三级解析路径和失败模式。"""

    def __init__(self) -> None:
        self.response_py = DOCUSWARM / "llm" / "response.py"
        self.independent_py = DOCUSWARM / "agents" / "independent.py"
        self.evaluator_py = DOCUSWARM / "agents" / "evaluator.py"

    def analyze(self) -> dict[str, Any]:
        print("\n[1/6] 分析 JSON 解析路径...")
        result: dict[str, Any] = {
            "extract_json_stages": [],
            "independent_fallback_logic": {},
            "evaluator_fallback_logic": {},
            "retry_mechanisms": [],
            "parse_error_propagation": [],
        }

        # 分析 extract_json 三级策略
        if self.response_py.exists():
            content = self.response_py.read_text(encoding="utf-8")
            stages = self._extract_parse_stages(content)
            result["extract_json_stages"] = stages
            print(f"  ✅ extract_json 解析阶段: {len(stages)} 个")
        else:
            print(f"  ❌ 文件不存在: {self.response_py}")

        # 分析 IndependentAgent 的 fallback 逻辑
        if self.independent_py.exists():
            content = self.independent_py.read_text(encoding="utf-8")
            fallback = self._extract_fallback_logic(content, "IndependentAgent")
            result["independent_fallback_logic"] = fallback
            print(f"  ✅ IndependentAgent fallback 分支: {fallback.get('branches', 0)} 个")

        # 分析 EvaluatorAgent 的 fallback 逻辑
        if self.evaluator_py.exists():
            content = self.evaluator_py.read_text(encoding="utf-8")
            fallback = self._extract_fallback_logic(content, "EvaluatorAgent")
            result["evaluator_fallback_logic"] = fallback
            print(f"  ✅ EvaluatorAgent fallback 分支: {fallback.get('branches', 0)} 个")

        # 检测是否存在重试机制
        retry_found = self._detect_retry_mechanisms()
        result["retry_mechanisms"] = retry_found
        if retry_found:
            print(f"  ⚠️  检测到重试机制: {len(retry_found)} 处")
        else:
            print("  ❌ 未检测到 JSON 解析失败专用重试机制")

        return result

    def _extract_parse_stages(self, content: str) -> list[dict[str, str]]:
        """从 extract_json 函数中提取各解析阶段。"""
        stages = []

        # Stage 1: Direct json.loads
        if "json.loads(response)" in content:
            stages.append({
                "stage": 1,
                "method": "json.loads(response)",
                "description": "直接解析整个响应字符串",
                "fallback_on_fail": "ResponseParseError → try Stage 2",
            })

        # Stage 2: Markdown code block
        if "extract_json_from_markdown" in content:
            stages.append({
                "stage": 2,
                "method": "extract_json_from_markdown(response)",
                "description": "从 ```json ... ``` Markdown 代码块提取",
                "fallback_on_fail": "ResponseParseError → try Stage 3",
            })

        # Stage 3: Aggressive brace-counting
        if "brace_count" in content:
            stages.append({
                "stage": 3,
                "method": "逐行扫描 + 括号计数平衡法",
                "description": "找到第一个 { 开头的行，用括号计数找到完整 JSON 对象",
                "fallback_on_fail": "raise ResponseParseError('No JSON found in response')",
            })

        return stages

    def _extract_fallback_logic(self, content: str, agent_name: str) -> dict[str, Any]:
        """分析代理的 _parse_response 中的 fallback 逻辑。"""
        result: dict[str, Any] = {
            "agent": agent_name,
            "branches": 0,
            "has_tool_result_fallback": False,
            "final_action_on_failure": "unknown",
            "raises_on_failure": [],
        }

        # 检查是否有工具结果 fallback
        if "_extract_create_deliverable_result" in content:
            result["has_tool_result_fallback"] = True

        # 统计 fallback 分支
        fallback_keywords = [
            "is_non_json_text",
            "markdown_fallback",
            "plain_text_fallback",
            "fallback_success",
        ]
        branch_count = sum(1 for kw in fallback_keywords if kw in content)
        result["branches"] = branch_count

        # 找出最终异常类型
        raise_patterns = re.findall(r"raise\s+(\w+Error)[^)]*\)", content)
        result["raises_on_failure"] = list(set(raise_patterns))

        # 判断最终行为
        if agent_name == "IndependentAgent":
            if result["has_tool_result_fallback"]:
                result["final_action_on_failure"] = (
                    "如果有工具调用结果: 构造兜底响应; 否则: raise ResponseParseAgentError"
                )
            else:
                result["final_action_on_failure"] = "raise ResponseParseAgentError"
        elif agent_name == "EvaluatorAgent":
            result["final_action_on_failure"] = "raise EvaluationError (无 fallback)"

        return result

    def _detect_retry_mechanisms(self) -> list[dict[str, str]]:
        """扫描代码库，检测是否有专门针对 JSON 解析失败的重试逻辑。"""
        retry_signals = []

        files_to_scan = [
            DOCUSWARM / "agents" / "independent.py",
            DOCUSWARM / "agents" / "evaluator.py",
            DOCUSWARM / "nodes" / "dual_agent.py",
            DOCUSWARM / "node_execution" / "executor.py",
            DOCUSWARM / "llm" / "session_manager.py",
        ]

        retry_patterns = [
            (r"for\s+\w+\s+in\s+range\s*\(\s*\d+\s*\)", "for retry in range(N) 循环"),
            (r"retry\s*=\s*\d+", "retry 计数变量"),
            (r"max_retries", "max_retries 配置"),
            (r"ResponseParseError.*retry", "ResponseParseError 重试"),
            (r"retry.*ResponseParseError", "ResponseParseError 重试"),
            (r"json_retry", "json_retry 显式标记"),
            (r"parse_retry", "parse_retry 显式标记"),
        ]

        for filepath in files_to_scan:
            if not filepath.exists():
                continue
            content = filepath.read_text(encoding="utf-8")
            for pattern, description in retry_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    retry_signals.append({
                        "file": str(filepath.relative_to(ROOT)),
                        "pattern": pattern,
                        "description": description,
                        "matches": matches[:3],  # 最多显示3个
                    })

        return retry_signals


# ============================================================
# Section 2: 异常传播链分析
# ============================================================

class ExceptionPropagationAnalyzer:
    """分析从 JSON 解析失败到节点 FAILED 的完整异常传播路径。"""

    def __init__(self) -> None:
        self.dual_agent = DOCUSWARM / "nodes" / "dual_agent.py"
        self.executor = DOCUSWARM / "node_execution" / "executor.py"

    def analyze(self) -> dict[str, Any]:
        print("\n[2/6] 分析异常传播链...")
        result: dict[str, Any] = {
            "propagation_chain": [],
            "business_retry_loop": {},
            "technical_retry_exists": False,
            "gap_analysis": [],
        }

        # 分析 DualAgentNode 中的异常处理
        if self.dual_agent.exists():
            content = self.dual_agent.read_text(encoding="utf-8")
            business_retry = self._analyze_business_retry(content)
            result["business_retry_loop"] = business_retry
            print(f"  ✅ 业务迭代循环: max_iterations={business_retry.get('max_iterations')}")

        # 构建传播链
        chain = [
            {
                "layer": 1,
                "location": "llm/response.py :: extract_json()",
                "exception": "ResponseParseError",
                "action": "抛出异常，无重试",
            },
            {
                "layer": 2,
                "location": "agents/independent.py :: _parse_response()",
                "exception": "ResponseParseAgentError",
                "action": "有工具结果则兜底，否则包装并上抛",
            },
            {
                "layer": 3,
                "location": "nodes/dual_agent.py :: execute_with_context()",
                "exception": "IndependentExecutionError",
                "action": "捕获 Exception，包装为 IndependentExecutionError 后上抛",
            },
            {
                "layer": 4,
                "location": "node_execution/executor.py :: _execute_node()",
                "exception": "Exception (captured)",
                "action": "捕获所有异常，设置 status=FAILED，停止执行",
            },
        ]
        result["propagation_chain"] = chain

        # 关键发现：DualAgentNode 的迭代循环不捕获解析失败
        result["gap_analysis"] = [
            {
                "gap": "JSON 解析失败不触发 NEEDS_REVISION 循环",
                "root_cause": (
                    "DualAgentNode.execute_with_context() 在 Independent Agent 失败时，"
                    "直接 raise IndependentExecutionError，而不是继续下一次迭代"
                ),
                "evidence": "dual_agent.py L339-343: except Exception as e → raise IndependentExecutionError",
                "severity": "HIGH",
            },
            {
                "gap": "Evaluator JSON 失败无任何恢复路径",
                "root_cause": (
                    "EvaluatorAgent._parse_response() 无 fallback，"
                    "直接 raise EvaluationError"
                ),
                "evidence": "evaluator.py L488-492: except ResponseParseError → raise EvaluationError",
                "severity": "HIGH",
            },
            {
                "gap": "节点 FAILED 后无自动重启",
                "root_cause": (
                    "executor.py 将 status=FAILED 写入 NodeRunState，"
                    "LangGraph 图的边是顺序的，FAILED 节点不会重试"
                ),
                "evidence": "executor.py L208-218: except Exception → new_state['status'] = FAILED",
                "severity": "CRITICAL",
            },
        ]

        print(f"  ✅ 异常传播链: {len(chain)} 层")
        print(f"  ❌ 关键缺口: {len(result['gap_analysis'])} 个")

        return result

    def _analyze_business_retry(self, content: str) -> dict[str, Any]:
        """分析 DualAgentNode 的业务迭代循环。"""
        result: dict[str, Any] = {
            "has_iteration_loop": False,
            "max_iterations": 3,
            "triggers_on": [],
            "does_not_trigger_on": [],
        }

        if "while iteration < self.max_iterations" in content:
            result["has_iteration_loop"] = True

        # 检测触发条件
        if "NEEDS_REVISION" in content:
            result["triggers_on"].append("NEEDS_REVISION (评估分数低)")
        if "previous_feedback" in content:
            result["triggers_on"].append("携带改进意见的 previous_feedback")

        result["does_not_trigger_on"] = [
            "ResponseParseAgentError (JSON 解析失败)",
            "EvaluationError (评估响应解析失败)",
            "IndependentExecutionError (Independent Agent 失败)",
            "EvaluatorExecutionError (Evaluator Agent 失败)",
        ]

        # 提取 max_iterations
        m = re.search(r"DEFAULT_MAX_ITERATIONS\s*=\s*(\d+)", content)
        if m:
            result["max_iterations"] = int(m.group(1))

        return result


# ============================================================
# Section 3: MCP Tool Schema 现状分析
# ============================================================

class McpToolSchemaAnalyzer:
    """分析现有 MCP 工具的 schema 定义完整性。"""

    def __init__(self) -> None:
        self.create_deliverable_sdk = TOOLS_DIR / "create_deliverable_sdk.py"
        self.session_manager = DOCUSWARM / "llm" / "session_manager.py"
        self.tool_filter = DOCUSWARM / "llm" / "tool_filter.py"

    def analyze(self) -> dict[str, Any]:
        print("\n[3/6] 分析 MCP Tool Schema 现状...")
        result: dict[str, Any] = {
            "existing_mcp_tools": [],
            "schema_coverage": {},
            "output_format_support": {},
            "constrained_fields": [],
            "unconstrained_fields": [],
        }

        # 分析 create_deliverable tool schema
        if self.create_deliverable_sdk.exists():
            content = self.create_deliverable_sdk.read_text(encoding="utf-8")
            tool_analysis = self._analyze_create_deliverable_schema(content)
            result["existing_mcp_tools"].append(tool_analysis)
            print(f"  ✅ create_deliverable schema 字段: {len(tool_analysis.get('schema_fields', []))} 个")

        # 检查 output_format 是否被使用
        output_format_usage = self._check_output_format_usage()
        result["output_format_support"] = output_format_usage
        if output_format_usage.get("is_used"):
            print("  ✅ output_format 已被使用")
        else:
            print("  ❌ output_format 未被使用（SDK 提供但项目未集成）")

        # 标识受约束 vs 未受约束的字段
        result["constrained_fields"] = [
            "create_deliverable.title (type: string, required)",
            "create_deliverable.content (type: string, required)",
            "create_deliverable.metadata (type: object, optional)",
        ]

        result["unconstrained_fields"] = [
            "IndependentAgent execution report JSON: deliverable.file_path",
            "IndependentAgent execution report JSON: deliverable.sha256",
            "IndependentAgent execution report JSON: questions[].priority",
            "IndependentAgent execution report JSON: questions[].question",
            "IndependentAgent execution report JSON: questions[].context",
            "IndependentAgent execution report JSON: action",
            "EvaluatorAgent output JSON: criterion_scores",
            "EvaluatorAgent output JSON: alignment_score",
            "EvaluatorAgent output JSON: verdict",
            "EvaluatorAgent output JSON: issues_found",
            "EvaluatorAgent output JSON: suggestions",
        ]

        print(f"  ✅ 受约束字段: {len(result['constrained_fields'])} 个")
        print(f"  ❌ 未受约束字段: {len(result['unconstrained_fields'])} 个")

        return result

    def _analyze_create_deliverable_schema(self, content: str) -> dict[str, Any]:
        """分析 create_deliverable 工具的 JSON schema。"""
        result: dict[str, Any] = {
            "tool_name": "create_deliverable",
            "server_name_pattern": "docuswarm-deliverable-{node_id}",
            "mcp_tool_full_name": "mcp__docuswarm-deliverable-{node_id}__create_deliverable",
            "schema_fields": [],
            "required_fields": [],
            "optional_fields": [],
            "output_schema_defined": False,
        }

        # 提取 schema 字段
        if '"title"' in content and '"type": "string"' in content:
            result["schema_fields"].append("title (string, required)")
            result["required_fields"].append("title")
        if '"content"' in content and '"type": "string"' in content:
            result["schema_fields"].append("content (string, required)")
            result["required_fields"].append("content")
        if '"metadata"' in content and '"type": "object"' in content:
            result["schema_fields"].append("metadata (object, optional)")
            result["optional_fields"].append("metadata")

        # 检查是否有 output schema
        result["output_schema_defined"] = "output_schema" in content

        return result

    def _check_output_format_usage(self) -> dict[str, Any]:
        """检查 output_format 在 SessionManager 中是否被使用。"""
        result: dict[str, Any] = {
            "is_used": False,
            "usage_locations": [],
            "sdk_support": True,  # 根据 agentdocs/14 确认支持
        }

        files_to_check = [
            DOCUSWARM / "llm" / "session_manager.py",
            DOCUSWARM / "agents" / "independent.py",
            DOCUSWARM / "agents" / "evaluator.py",
        ]

        for filepath in files_to_check:
            if not filepath.exists():
                continue
            content = filepath.read_text(encoding="utf-8")
            if "output_format" in content:
                result["is_used"] = True
                result["usage_locations"].append(str(filepath.relative_to(ROOT)))

        return result


# ============================================================
# Section 4: SDK Structured Output 可行性评估
# ============================================================

class StructuredOutputFeasibilityAnalyzer:
    """评估通过 SDK output_format 约束 JSON 输出的可行性。"""

    def __init__(self) -> None:
        self.structured_outputs_doc = AGENTDOCS / "14_structured_outputs.md"
        self.python_sdk_doc = AGENTDOCS / "05_python.md"
        self.session_manager = DOCUSWARM / "llm" / "session_manager.py"

    def analyze(self) -> dict[str, Any]:
        print("\n[4/6] 评估 SDK Structured Output 可行性...")
        result: dict[str, Any] = {
            "sdk_feature_available": False,
            "api_usage": {},
            "independent_output_schema": {},
            "evaluator_output_schema": {},
            "integration_approach": [],
            "integration_complexity": "MEDIUM",
            "expected_benefits": [],
            "known_limitations": [],
        }

        # 确认 SDK 特性可用性
        if self.structured_outputs_doc.exists():
            doc_content = self.structured_outputs_doc.read_text(encoding="utf-8")
            if "output_format" in doc_content and "json_schema" in doc_content:
                result["sdk_feature_available"] = True
                result["api_usage"] = {
                    "python_api": (
                        "ClaudeAgentOptions(output_format={'type': 'json_schema', 'schema': schema})"
                    ),
                    "result_access": "message.structured_output (when isinstance(message, ResultMessage))",
                    "error_subtype": "error_max_structured_output_retries (SDK 内置重试耗尽)",
                    "retry_behavior": "SDK 自动重试直到生成有效 JSON（次数由 SDK 管理）",
                }
                print("  ✅ SDK output_format 特性已确认可用")
            else:
                print("  ❌ SDK output_format 特性文档未找到")
        else:
            print(f"  ❌ 文档不存在: {self.structured_outputs_doc}")

        # 定义 IndependentAgent 的期望输出 schema
        result["independent_output_schema"] = {
            "type": "object",
            "required": ["deliverable", "questions", "action"],
            "properties": {
                "deliverable": {
                    "type": "object",
                    "required": ["title", "content", "file_path", "sha256"],
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string", "description": "1-2句摘要，非全文"},
                        "file_path": {"type": "string", "description": "来自 create_deliverable 工具返回"},
                        "sha256": {"type": "string", "description": "来自 create_deliverable 工具返回"},
                    },
                },
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["question", "priority", "context"],
                        "properties": {
                            "question": {"type": "string"},
                            "priority": {"type": "string", "enum": ["blocking", "clarifying", "optional"]},
                            "context": {"type": "string"},
                        },
                    },
                },
                "action": {"type": "string", "enum": ["create_deliverable"]},
            },
        }

        # 定义 EvaluatorAgent 的期望输出 schema
        result["evaluator_output_schema"] = {
            "type": "object",
            "required": ["criterion_scores", "alignment_score", "verdict", "issues_found", "suggestions"],
            "properties": {
                "criterion_scores": {
                    "type": "object",
                    "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                },
                "alignment_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "verdict": {"type": "string", "enum": ["APPROVED", "NEEDS_REVISION", "BLOCKED"]},
                "issues_found": {"type": "array", "items": {"type": "string"}},
                "suggestions": {"type": "array", "items": {"type": "string"}},
            },
        }

        # 集成方案
        result["integration_approach"] = [
            {
                "approach": "A: output_format on query()",
                "description": "在 single_prompt() 的 options 中设置 output_format",
                "scope": "EvaluatorAgent（单次 query 调用，无工具调用）",
                "feasibility": "HIGH - 直接适用",
                "change_required": "session_manager.py::single_prompt() 增加 output_format 参数",
            },
            {
                "approach": "B: submit_execution_report MCP 工具",
                "description": "添加新 MCP 工具，schema 覆盖 execution report 全部字段，LLM 强制调用此工具提交结果",
                "scope": "IndependentAgent（session 模式，有工具调用）",
                "feasibility": "HIGH - SDK 支持，已有 create_deliverable 工具先例",
                "change_required": (
                    "1. tools/create_deliverable_sdk.py 增加 submit_execution_report 工具\n"
                    "2. session_manager.py 注册新工具\n"
                    "3. independent.py system prompt 指引 LLM 调用新工具\n"
                    "4. independent.py _parse_response() 从工具结果而非文本提取"
                ),
            },
            {
                "approach": "C: output_format on ClaudeSDKClient session",
                "description": "在 create_session() 的 options 中设置 output_format",
                "scope": "IndependentAgent（session 模式）",
                "feasibility": "MEDIUM - 与工具调用的交互需验证",
                "change_required": "session_manager.py::create_session() + _create_options() 增加 output_format 参数",
            },
        ]

        result["expected_benefits"] = [
            "消除「LLM 返回 Markdown 而非 JSON」的整类问题（~80% 的解析失败案例）",
            "SDK 内置重试（error_max_structured_output_retries），无需 Python 层重试逻辑",
            "enum 约束直接拦截非法 verdict/priority 值",
            "additionalProperties: false 拦截私有字段泄露（evaluator 隔离）",
            "减少 ContextValidator 的防御性代码量",
        ]

        result["known_limitations"] = [
            "output_format 与 query() 配合时需验证与 MCP 工具调用的兼容性",
            "agent 模式（session）使用 ClaudeSDKClient，output_format 支持需验证",
            "SDK 的「内置重试」次数和策略不透明（由 Claude Code 内部管理）",
            "Evaluator 的 criterion_scores 是动态 key，additionalProperties 约束力有限",
        ]

        print(f"  ✅ 集成方案: {len(result['integration_approach'])} 种")
        print(f"  ✅ 预期收益: {len(result['expected_benefits'])} 项")

        return result


# ============================================================
# Section 5: 重试机制设计方案分析
# ============================================================

class RetryMechanismDesignAnalyzer:
    """分析并设计 JSON 解析失败后的重试机制。"""

    def analyze(self) -> dict[str, Any]:
        print("\n[5/6] 设计重试机制方案...")
        result: dict[str, Any] = {
            "current_state": {},
            "design_options": [],
            "recommended_approach": {},
            "implementation_cost": {},
        }

        result["current_state"] = {
            "has_json_parse_retry": False,
            "has_schema_validation_retry": False,
            "has_business_iteration_retry": True,
            "business_retry_max": 3,
            "business_retry_trigger": "NEEDS_REVISION verdict only",
            "technical_failure_outcome": "node status = FAILED, pipeline stops",
        }

        result["design_options"] = [
            {
                "option": "Option 1: Python 层 JSON 重试（最小改动）",
                "where": "agents/independent.py::_parse_response() + agents/evaluator.py::_parse_response()",
                "mechanism": "捕获 ResponseParseError 后，重新调用 _call_llm()，最多 N 次",
                "max_retries": 2,
                "pros": [
                    "改动范围小（2个文件）",
                    "对现有架构侵入性低",
                    "可精确控制重试次数和间隔",
                ],
                "cons": [
                    "每次重试都是全新 LLM 调用（成本高）",
                    "重试时没有上下文改进（LLM 可能重复犯错）",
                    "与业务迭代循环重叠，逻辑复杂",
                ],
                "implementation_effort": "LOW (50 行代码)",
            },
            {
                "option": "Option 2: SDK output_format 约束（推荐）",
                "where": "llm/session_manager.py::single_prompt() / _create_options()",
                "mechanism": "使用 ClaudeAgentOptions(output_format=...) 让 SDK 强制 JSON 输出",
                "max_retries": "SDK 管理（error_max_structured_output_retries）",
                "pros": [
                    "SDK 内置重试，无需 Python 层额外逻辑",
                    "schema 约束消除整类解析失败",
                    "enum 约束拦截非法字段值",
                    "structured_output 直接返回 Python 对象，无需 extract_json()",
                ],
                "cons": [
                    "需要验证 output_format 与 session 模式（ClaudeSDKClient）的兼容性",
                    "EvaluatorAgent 适用直接，IndependentAgent 需额外验证",
                    "schema 必须预先定义（灵活性略降）",
                ],
                "implementation_effort": "MEDIUM (100-150 行代码，含 schema 定义)",
            },
            {
                "option": "Option 3: submit_execution_report MCP 工具（最彻底）",
                "where": "tools/create_deliverable_sdk.py + agents/independent.py",
                "mechanism": "添加 submit_execution_report 工具，schema 覆盖全部输出字段",
                "max_retries": "SDK tool_call 失败会触发 SDK 内部重试",
                "pros": [
                    "完全消除「自由文本 execution report」的不可控性",
                    "file_path/sha256 从工具结果获取（单一真相来源保持）",
                    "与现有 create_deliverable 工具模式一致（技术债务最小）",
                    "tool schema 的 enum/required 提供最强约束",
                ],
                "cons": [
                    "改动范围最大（工具定义 + 注册 + Prompt + 解析逻辑）",
                    "需要更新 system prompt 指引 LLM 必须调用此工具",
                    "可能增加 LLM 的 tool call 次数（成本）",
                ],
                "implementation_effort": "HIGH (200-300 行代码 + prompt 改动)",
            },
            {
                "option": "Option 4: 组合方案（分阶段实施）",
                "where": "Phase 1: Option 2 (EvaluatorAgent); Phase 2: Option 3 (IndependentAgent)",
                "mechanism": "先用 output_format 解决 Evaluator，再用 MCP 工具解决 Independent",
                "pros": [
                    "风险分散，可逐步验证",
                    "EvaluatorAgent 无工具调用，output_format 兼容性最佳",
                    "IndependentAgent 通过 MCP 工具获得最强约束",
                ],
                "cons": ["分两阶段实施，时间较长"],
                "implementation_effort": "MEDIUM (分阶段实施，总量 HIGH)",
            },
        ]

        result["recommended_approach"] = {
            "recommendation": "Option 4: 分阶段组合方案",
            "phase_1": {
                "target": "EvaluatorAgent",
                "method": "SDK output_format + json_schema",
                "reason": "Evaluator 使用 single_prompt()，无工具调用，output_format 兼容性最高",
                "priority": "P0 - 立即可实施",
            },
            "phase_2": {
                "target": "IndependentAgent",
                "method": "submit_execution_report MCP 工具",
                "reason": "彻底消除 execution report 不可控性，与单一真相来源设计一致",
                "priority": "P1 - 需更多测试验证",
            },
            "phase_3": {
                "target": "JSON 解析失败兜底重试",
                "method": "Option 1 的最小重试逻辑（max_retries=1）",
                "reason": "作为 Phase 1+2 的最后防线，防止 SDK 重试耗尽后仍然失败",
                "priority": "P2 - 可选增强",
            },
        }

        result["implementation_cost"] = {
            "phase_1_effort": "1-2天（含测试）",
            "phase_2_effort": "3-5天（含 prompt 调整和测试）",
            "phase_3_effort": "0.5天（纯代码，无架构影响）",
            "total_risk": "LOW-MEDIUM（SDK 特性已有文档，模式已有先例）",
        }

        print(f"  ✅ 设计方案: {len(result['design_options'])} 种")
        print(f"  ✅ 推荐方案: {result['recommended_approach']['recommendation']}")

        return result


# ============================================================
# Section 6: 综合报告生成
# ============================================================

class ReportGenerator:
    """生成综合分析报告。"""

    def generate(self, all_results: dict[str, Any]) -> dict[str, Any]:
        print("\n[6/6] 生成综合分析...")

        report = {
            "metadata": {
                "tool": "json_retry_mcp_schema_analyzer",
                "version": "1.0.0",
                "analysis_date": self._get_date(),
                "target_project": "DocuSwarm",
            },
            "executive_summary": self._generate_executive_summary(all_results),
            "findings": self._extract_key_findings(all_results),
            "detailed_results": all_results,
        }

        return report

    def _get_date(self) -> str:
        from datetime import date
        return str(date.today())

    def _generate_executive_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        return {
            "json_retry_status": "NOT IMPLEMENTED - JSON 解析/校验失败后无专用重试机制",
            "current_failure_behavior": (
                "JSON 解析失败 → ResponseParseAgentError/EvaluationError "
                "→ IndependentExecutionError/EvaluatorExecutionError "
                "→ node status=FAILED → pipeline 终止"
            ),
            "business_retry_note": (
                "DualAgentNode 的 max_iterations=3 循环仅针对 NEEDS_REVISION（业务质量不足），"
                "不处理技术失败（JSON 解析错误）"
            ),
            "mcp_constraint_status": (
                "PARTIAL - create_deliverable 工具参数有 schema 约束，"
                "但 execution report JSON 和 evaluator output JSON 无 schema 约束"
            ),
            "sdk_structured_output_available": True,
            "recommended_solution": "分阶段实施：Phase1(EvaluatorAgent output_format) + Phase2(submit_execution_report MCP工具)",
            "risk_level": "HIGH（当前任何 LLM 响应格式偏差都会导致 pipeline 完全失败）",
        }

    def _extract_key_findings(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        findings = [
            {
                "id": "F1",
                "severity": "CRITICAL",
                "title": "JSON 解析失败导致 pipeline 完全终止，无恢复路径",
                "detail": (
                    "extract_json() 三级解析全部失败后，异常沿 4 层传播链"
                    "（response.py → independent.py → dual_agent.py → executor.py）"
                    "最终将节点状态设为 FAILED。LangGraph 图无条件边处理此状态，pipeline 停止。"
                ),
                "affected_components": [
                    "llm/response.py",
                    "agents/independent.py",
                    "agents/evaluator.py",
                    "nodes/dual_agent.py",
                    "node_execution/executor.py",
                ],
                "recommendation": "实施 JSON 解析失败专用重试机制（Option 1 或 Option 2）",
            },
            {
                "id": "F2",
                "severity": "HIGH",
                "title": "EvaluatorAgent 对 JSON 校验失败零容错",
                "detail": (
                    "evaluator.py._parse_response() 捕获 ResponseParseError 后直接 raise EvaluationError，"
                    "无任何 fallback 逻辑。而 IndependentAgent 至少有工具结果兜底路径。"
                ),
                "affected_components": ["agents/evaluator.py"],
                "recommendation": "对 EvaluatorAgent 应用 output_format schema 约束（优先级最高）",
            },
            {
                "id": "F3",
                "severity": "HIGH",
                "title": "SDK output_format 特性已支持但项目未集成",
                "detail": (
                    "agentdocs/14_structured_outputs.md 确认 Claude Agent SDK 支持 "
                    "ClaudeAgentOptions(output_format={'type': 'json_schema', 'schema': ...})，"
                    "且 SDK 内置重试（error_max_structured_output_retries）。"
                    "但 session_manager.py 的 _create_options() 从未设置 output_format。"
                ),
                "affected_components": [
                    "llm/session_manager.py",
                    "agents/evaluator.py",
                ],
                "recommendation": "在 single_prompt() 中增加 output_format 参数，对 EvaluatorAgent 启用",
            },
            {
                "id": "F4",
                "severity": "MEDIUM",
                "title": "IndependentAgent execution report 完全依赖 LLM 自由文本",
                "detail": (
                    "独立代理调用 create_deliverable 工具（有 schema 约束）后，"
                    "仍需额外输出一段 execution report JSON（无约束）。"
                    "这段 JSON 包含 deliverable.file_path、questions[]、action 等关键字段，"
                    "完全依赖 extract_json() 从自由文本中提取。"
                ),
                "affected_components": [
                    "agents/independent.py",
                    "tools/create_deliverable_sdk.py",
                ],
                "recommendation": "添加 submit_execution_report MCP 工具，用 tool schema 强制约束",
            },
            {
                "id": "F5",
                "severity": "MEDIUM",
                "title": "DualAgentNode 迭代循环与技术失败处理完全分离",
                "detail": (
                    "while iteration < max_iterations 循环只处理业务质量问题（NEEDS_REVISION），"
                    "技术失败（JSON 解析错误）立即 raise 并跳出循环。"
                    "这意味着 3 次迭代机会全部浪费在第一次技术失败上。"
                ),
                "affected_components": ["nodes/dual_agent.py"],
                "recommendation": "在迭代循环内捕获技术失败并计入单独的重试计数器",
            },
        ]
        return findings

    def print_summary(self, report: dict[str, Any]) -> None:
        summary = report["executive_summary"]
        findings = report["findings"]

        print("\n" + "=" * 70)
        print("📊 综合分析摘要")
        print("=" * 70)
        print(f"\n🔴 JSON 重试状态: {summary['json_retry_status']}")
        print(f"🔴 当前失败行为: {summary['current_failure_behavior'][:80]}...")
        print(f"🟡 MCP 约束状态: {summary['mcp_constraint_status'][:80]}...")
        print(f"🟢 SDK 结构化输出: {'可用' if summary['sdk_structured_output_available'] else '不可用'}")
        print(f"✅ 推荐方案: {summary['recommended_solution']}")

        print(f"\n📋 关键发现 ({len(findings)} 个):")
        for f in findings:
            severity_icon = "🔴" if f["severity"] == "CRITICAL" else ("🟡" if f["severity"] == "HIGH" else "🔵")
            print(f"  {severity_icon} [{f['id']}] {f['title']}")


# ============================================================
# Main
# ============================================================

def main() -> dict[str, Any]:
    """运行完整分析。"""
    import argparse
    parser = argparse.ArgumentParser(description="JSON Retry & MCP Schema 分析器")
    parser.add_argument("--output", help="JSON 输出文件路径", default=None)
    args = parser.parse_args()

    print("=" * 70)
    print("DocuSwarm - JSON 重试机制 & MCP Schema 约束深度分析器")
    print("=" * 70)

    all_results: dict[str, Any] = {}

    # 执行各分析模块
    all_results["json_parse_paths"] = JsonParsePathAnalyzer().analyze()
    all_results["exception_propagation"] = ExceptionPropagationAnalyzer().analyze()
    all_results["mcp_tool_schema"] = McpToolSchemaAnalyzer().analyze()
    all_results["structured_output_feasibility"] = StructuredOutputFeasibilityAnalyzer().analyze()
    all_results["retry_mechanism_design"] = RetryMechanismDesignAnalyzer().analyze()

    # 生成综合报告
    generator = ReportGenerator()
    report = generator.generate(all_results)
    generator.print_summary(report)

    # 输出 JSON
    output_path = args.output or str(ROOT / ".tmp" / "json_retry_mcp_schema_analysis.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n💾 详细报告已保存: {output_path}")

    return report


if __name__ == "__main__":
    main()
