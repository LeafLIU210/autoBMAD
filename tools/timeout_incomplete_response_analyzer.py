"""
Timeout & Incomplete Response Root Cause Analyzer
==================================================

目标: 深度分析以下错误链：
  1. prompt_timeout (60s)  — ClaudeSessionWrapper 在流式接收过程中超时
  2. → llm_call_error      — IndependentAgent 捕获异常
  3. → response_parse_failed (No JSON found) — 部分 Markdown 响应无法解析
  4. → independent_agent_failed
  5. → node_execution_failed

关键观察 (来自 2026-04-06 日志):
  - analyst 节点: 16:05:07 开始, 13 条消息已接收, 16:06:07 超时 (60s)
  - LLM 在超时时仍处于生成状态 (ThinkingBlock 存在)
  - partial response content: "The tools appear to have some issues..."
  - response_parse_failed: "No JSON found in response"

Usage:
    python tools/timeout_incomplete_response_analyzer.py
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


# ============================================================
# 分析器
# ============================================================

class TimeoutIncompleteResponseAnalyzer:
    """分析 60s 超时 + 部分响应无法解析的根因。"""

    def __init__(self) -> None:
        self.root = ROOT
        self.docuswarm = ROOT / "autoBMAD" / "docuswarm"
        self.nodes_dir = ROOT / "autoBMAD" / "nodes"
        self.results: dict[str, Any] = {}

    def run(self) -> dict[str, Any]:
        print("=" * 70)
        print("DocuSwarm Timeout & Incomplete Response 根因分析器")
        print("错误链: prompt_timeout(60s) → response_parse_failed(No JSON)")
        print("=" * 70)

        self.results["A_timeout_chain"] = self._analyze_timeout_chain()
        self.results["B_partial_response"] = self._analyze_partial_response()
        self.results["C_session_wrapper"] = self._analyze_session_wrapper()
        self.results["D_parse_fallback"] = self._analyze_parse_fallback()
        self.results["E_tool_completion"] = self._analyze_tool_completion_timing()
        self.results["F_node_config"] = self._analyze_node_config()
        self.results["G_system_prompt"] = self._analyze_system_prompt_size()
        self.results["root_causes"] = self._identify_root_causes()

        self._print_summary()

        return self.results

    # ----------------------------------------------------------
    # A. 超时链分析
    # ----------------------------------------------------------
    def _analyze_timeout_chain(self) -> dict[str, Any]:
        """分析超时触发的完整调用链。"""
        print("\n[A] 分析超时调用链...")
        result: dict[str, Any] = {
            "timeout_value_seconds": None,
            "timeout_location": None,
            "error_propagation": [],
            "issues": [],
        }

        # 1. 读取 ClaudeSessionWrapper.DEFAULT_PROMPT_TIMEOUT
        sm_file = self.docuswarm / "llm" / "session_manager.py"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8")
            m = re.search(r"DEFAULT_PROMPT_TIMEOUT\s*:\s*int\s*=\s*(\d+)", content)
            if m:
                timeout_val = int(m.group(1))
                result["timeout_value_seconds"] = timeout_val
                print(f"  DEFAULT_PROMPT_TIMEOUT = {timeout_val}s")

                if timeout_val == 60:
                    result["issues"].append(
                        "P0-TIMEOUT: DEFAULT_PROMPT_TIMEOUT=60s 对于复杂文档生成任务远远不够。"
                        "analyst 节点需要生成完整分析报告，LLM 生成时间通常超过 60s。"
                    )
                    print("  ❌ 60s 超时对于文档生成任务过短！")
                elif timeout_val == 1200:
                    print("  ℹ️  1200s (20分钟) — 原始默认值")

            # 2. 找到超时触发位置
            m2 = re.search(r"async with asyncio\.timeout\((\w+)\)", content)
            if m2:
                result["timeout_location"] = f"session_manager.py: asyncio.timeout({m2.group(1)})"
                print(f"  超时触发位置: asyncio.timeout({m2.group(1)})")

            # 3. 分析错误传播
            propagation_steps = [
                ("session_manager.py", "asyncio.TimeoutError → LLMError('Session prompt timed out')"),
                ("independent.py:367-373", "except Exception → llm_call_error warning → LLMCallError"),
                ("independent.py:674", "_parse_response(response) — response 是 partial messages"),
                ("independent.py:464", "extract_json(content) → ResponseParseError('No JSON found')"),
                ("independent.py:509", "response_parse_failed → ResponseParseAgentError"),
                ("dual_agent.py", "independent_agent_failed → node_execution_failed"),
            ]
            result["error_propagation"] = propagation_steps
            for step, desc in propagation_steps:
                print(f"  → {step}: {desc}")
        else:
            result["issues"].append("CRITICAL: session_manager.py 未找到")

        return result

    # ----------------------------------------------------------
    # B. 部分响应内容分析
    # ----------------------------------------------------------
    def _analyze_partial_response(self) -> dict[str, Any]:
        """分析超时时 LLM 的部分响应内容。"""
        print("\n[B] 分析超时时的部分响应内容...")
        result: dict[str, Any] = {
            "partial_content_observed": None,
            "content_type": None,
            "has_json": False,
            "has_markdown": False,
            "has_thinking_block": False,
            "tool_called_before_timeout": None,
            "issues": [],
        }

        # 来自终端日志的关键信息
        partial_content = (
            "The tools appear to have some issues, but I need to complete my task. "
            "The instructions say I should use the 'create_deliverable' tool to save my document, "
            "but I don't see that"
        )
        result["partial_content_observed"] = partial_content

        # 分析内容特征
        result["has_json"] = False
        result["has_markdown"] = partial_content.startswith(("#", "##")) or "Summary" in partial_content[:100]
        result["has_thinking_block"] = "ThinkingBlock" in partial_content or "thinking" in partial_content.lower()

        # 关键发现：LLM 在说"工具有问题"
        if "tools appear to have some issues" in partial_content:
            result["issues"].append(
                "P0-TOOL-VISIBILITY: LLM 报告说'工具有问题'，"
                "表明 create_deliverable 工具对 LLM 不可见或加载失败。"
                "LLM 无法调用工具，无法完成任务，陷入等待/思考循环直到超时。"
            )
            print("  ❌ 关键发现: LLM 明确表示'工具有问题'")
            print("  ❌ LLM 无法调用 create_deliverable 工具!")

        if "but I don't see that" in partial_content:
            result["issues"].append(
                "P0-TOOL-NOT-FOUND: LLM 找不到 create_deliverable 工具。"
                "这导致 LLM 无法完成分配的任务，生成不完整的纯文本响应。"
            )
            print("  ❌ LLM 明确说它'看不到'该工具")

        # 分析消息接收数量 (来自日志)
        result["messages_received_before_timeout"] = 13
        result["tool_called_before_timeout"] = False  # 日志无 tool_use 记录
        print(f"  超时前接收消息数: 13")
        print(f"  超时前是否调用工具: 否 (无 tool_use 日志)")

        return result

    # ----------------------------------------------------------
    # C. ClaudeSessionWrapper 超时机制分析
    # ----------------------------------------------------------
    def _analyze_session_wrapper(self) -> dict[str, Any]:
        """分析 ClaudeSessionWrapper.prompt() 的超时处理机制。"""
        print("\n[C] 分析 ClaudeSessionWrapper 超时处理...")
        result: dict[str, Any] = {
            "timeout_mechanism": None,
            "partial_messages_handling": None,
            "issues": [],
        }

        sm_file = self.docuswarm / "llm" / "session_manager.py"
        if not sm_file.exists():
            result["issues"].append("CRITICAL: session_manager.py 未找到")
            return result

        content = sm_file.read_text(encoding="utf-8")

        # 检查超时后的 messages 状态
        prompt_section = ""
        in_prompt = False
        for line in content.split("\n"):
            if "async def prompt(" in line:
                in_prompt = True
            if in_prompt:
                prompt_section += line + "\n"
            if in_prompt and "async def close" in line:
                break

        result["timeout_mechanism"] = "asyncio.timeout() context manager 在接收流式消息时触发 TimeoutError"

        # 分析: 超时触发后 messages 变量状态
        # 从代码看: messages_received 计数 但 messages (list[dict]) 没有被填充
        # 因为 _message_to_dict 可能对 partial 消息返回 None
        result["partial_messages_handling"] = (
            "超时触发 TimeoutError → 直接 raise LLMError → "
            "上层 except Exception 捕获 → 检查 if messages: 返回部分消息 → "
            "partial messages 传入 _parse_response() → 尝试提取 JSON → 失败"
        )

        # 检查当 messages 为空时的行为
        if "if messages:" in content:
            result["issues"].append(
                "INFO: 超时后若有 partial messages，会传入 _parse_response()。"
                "但 partial messages 包含的是 ThinkingBlock/部分文本，无 JSON → parse 失败。"
            )

        # 关键问题: asyncio.timeout 触发时，messages 列表中有什么?
        result["issues"].append(
            "P1-PARTIAL-MSG: 超时触发时 messages_received=13 但 messages(list[dict]) 可能为空，"
            "因为 ThinkingBlock 被 _convert_content_block() 过滤为 None，"
            "导致所有 ThinkingBlock 消息被丢弃，只有最终 TextBlock 才会进入 messages。"
            "如果 LLM 在 60s 内只输出了 ThinkingBlock，则 messages=[]，parse 失败。"
        )
        print("  ℹ️ 超时后 messages 列表状态取决于 LLM 消息类型")
        print("  ❌ ThinkingBlock 被过滤 → messages 可能为空")

        return result

    # ----------------------------------------------------------
    # D. 解析 fallback 路径分析
    # ----------------------------------------------------------
    def _analyze_parse_fallback(self) -> dict[str, Any]:
        """分析 _parse_response 的 fallback 机制。"""
        print("\n[D] 分析 _parse_response fallback 机制...")
        result: dict[str, Any] = {
            "fallback_trigger_condition": None,
            "fallback_logic": None,
            "issues": [],
        }

        ind_file = self.docuswarm / "agents" / "independent.py"
        if not ind_file.exists():
            result["issues"].append("CRITICAL: independent.py 未找到")
            return result

        content = ind_file.read_text(encoding="utf-8")

        # 提取 _parse_response 方法
        method_match = re.search(
            r"def _parse_response\(.*?\n(.*?)(?=\n    def |\Z)",
            content,
            re.DOTALL,
        )

        result["fallback_trigger_condition"] = (
            "content.startswith(('#','##','###')) OR 'Summary' in content[:100]"
        )
        result["fallback_logic"] = (
            "从 messages 中提取 create_deliverable 工具返回的 file_path/sha256，"
            "若有则构造 JSON；若无则抛出 ResponseParseAgentError"
        )

        # 关键: 当前错误是 "No JSON found in response" 不是 markdown fallback
        # 说明 content 不以 # 开头，也没有 "Summary"
        # 实际 content 来自 partial_content: "The tools appear to have..."
        result["issues"].append(
            "P1-FALLBACK-MISS: LLM 返回的部分内容 ('The tools appear to have some issues...') "
            "不以 '#' 开头也不含 'Summary'，因此不触发 markdown_fallback。"
            "代码直接走 else 分支，抛出 'response_parse_failed' (No JSON found)。"
        )
        result["issues"].append(
            "P2-FALLBACK-GAP: fallback 条件仅检查 Markdown 标题，"
            "未处理'纯英文散文'这种 LLM 不完整响应格式。"
            "需要扩展 fallback 以处理任意非 JSON 内容格式。"
        )
        print("  ❌ partial content ('The tools appear...') 不触发 markdown_fallback")
        print("  ❌ fallback 条件仅限 Markdown 开头，覆盖不完整")

        return result

    # ----------------------------------------------------------
    # E. 工具可见性与完成时机分析
    # ----------------------------------------------------------
    def _analyze_tool_completion_timing(self) -> dict[str, Any]:
        """分析工具注册和 LLM 工具可见性问题。"""
        print("\n[E] 分析工具可见性与注册问题...")
        result: dict[str, Any] = {
            "agent_file_path": None,
            "agent_file_exists": None,
            "tools_registered": [],
            "tool_modules_exist": {},
            "sdk_tool_load_mechanism": None,
            "issues": [],
        }

        # 检查 independent_agent.yaml
        yaml_path = self.docuswarm / "agents" / "configs" / "independent_agent.yaml"
        result["agent_file_path"] = str(yaml_path)
        result["agent_file_exists"] = yaml_path.exists()

        if yaml_path.exists():
            content = yaml_path.read_text(encoding="utf-8")
            print(f"  ✅ independent_agent.yaml 存在")

            # 提取工具列表
            tools = re.findall(r'^\s*-\s*"(.+?)"', content, re.MULTILINE)
            result["tools_registered"] = tools

            for tool_ref in tools:
                if ":" in tool_ref:
                    module_path, class_name = tool_ref.split(":")
                    module_file = ROOT / module_path.replace(".", "/")
                    py_file = Path(str(module_file) + ".py")
                    exists = py_file.exists()
                    result["tool_modules_exist"][tool_ref] = {
                        "file": str(py_file),
                        "exists": exists,
                    }
                    status = "✅" if exists else "❌"
                    print(f"  {status} {class_name}: {py_file} ({'存在' if exists else '缺失'})")

            # 分析工具加载机制
            result["sdk_tool_load_mechanism"] = (
                "agent_file.yaml 中的工具引用通过 'extend: default' + tools 列表注册到 SDK。"
                "SDK 在 session 创建时加载这些工具。"
            )

            # 关键: LLM 说'看不到工具' — 可能是路径问题
            # 工具路径是 autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool
            # 但 work_dir 是 output/pipeline_id
            result["issues"].append(
                "HYPOTHESIS-E1: SDK 加载 agent_file 时使用的 CWD 是 work_dir (output/pipeline_id)。"
                "但 independent_agent.yaml 路径是相对于 autoBMAD/ 的绝对路径。"
                "若 SDK 无法正确解析相对模块路径，工具加载可能静默失败。"
            )

            # 检查 session_manager 中如何设置 options.tools
            sm_file = self.docuswarm / "llm" / "session_manager.py"
            if sm_file.exists():
                sm_content = sm_file.read_text(encoding="utf-8")
                if 'options.tools = [str(effective_agent_file)]' in sm_content:
                    result["issues"].append(
                        "HYPOTHESIS-E2: options.tools = [str(effective_agent_file)] "
                        "将 agent_file 路径转为字符串，可能是绝对路径。"
                        "但 agent_file 在 execute_with_input 中被设为: "
                        "project_root/docuswarm/agents/configs/independent_agent.yaml。"
                        "如果 project_root 解析错误，工具文件无法找到。"
                    )
                    print("  ⚠️  options.tools 使用字符串路径设置 agent_file")

            # 检查 project_root 解析逻辑
            if "repo_root = " in sm_file.read_text(encoding="utf-8") if sm_file.exists() else "":
                pass  # 已在 independent.py 处理

            ind_file = self.docuswarm / "agents" / "independent.py"
            if ind_file.exists():
                ind_content = ind_file.read_text(encoding="utf-8")
                # 查找 agent_file 设置
                m = re.search(
                    r'self\._agent_file\s*=\s*\([^)]+\)',
                    ind_content,
                    re.DOTALL,
                )
                if m:
                    result["agent_file_construction"] = m.group(0).strip()
                    print(f"  agent_file 构造: {m.group(0).strip()[:80]}...")

                # 检查 project_root 是否正确
                if 'self.project_root / "docuswarm"' in ind_content:
                    result["issues"].append(
                        "HYPOTHESIS-E3: self.project_root / 'docuswarm' / 'agents' / 'configs' / yaml。"
                        "project_root 应为 autoBMAD/ 目录，则完整路径为 autoBMAD/docuswarm/agents/configs/yaml。"
                        "若 project_root 被设为项目根目录 (DocuSwarm/)，路径变为 "
                        "DocuSwarm/docuswarm/agents/... → 路径错误！"
                    )
                    print("  ⚠️  project_root 解析依赖调用方是否正确传递 autoBMAD 目录")

        else:
            result["issues"].append("CRITICAL: independent_agent.yaml 不存在!")
            print("  ❌ independent_agent.yaml 不存在!")

        return result

    # ----------------------------------------------------------
    # F. 节点配置分析
    # ----------------------------------------------------------
    def _analyze_node_config(self) -> dict[str, Any]:
        """分析 analyst 节点配置。"""
        print("\n[F] 分析 analyst 节点配置...")
        result: dict[str, Any] = {
            "analyst_node_path": None,
            "config_exists": False,
            "task_config": None,
            "tool_permissions": None,
            "issues": [],
        }

        # 查找 analyst 节点配置
        analyst_dirs = [
            self.nodes_dir / "analyst",
            ROOT / "nodes" / "analyst",
        ]

        for node_dir in analyst_dirs:
            if node_dir.exists():
                result["analyst_node_path"] = str(node_dir)
                result["config_exists"] = True
                print(f"  ✅ analyst 节点目录: {node_dir}")

                # 读取 node.yaml
                yaml_files = list(node_dir.glob("*.yaml")) + list(node_dir.glob("*.yml"))
                for yf in yaml_files:
                    content = yf.read_text(encoding="utf-8")
                    print(f"  📄 {yf.name}:")
                    # 提取关键配置
                    lines = content.split("\n")
                    for line in lines[:50]:
                        print(f"     {line}")
                    result["task_config"] = content[:500]
                break

        if not result["config_exists"]:
            result["issues"].append("WARNING: analyst 节点配置目录未找到")
            print(f"  ⚠️ analyst 节点配置未找到，搜索路径: {[str(d) for d in analyst_dirs]}")

        return result

    # ----------------------------------------------------------
    # G. System Prompt 大小分析
    # ----------------------------------------------------------
    def _analyze_system_prompt_size(self) -> dict[str, Any]:
        """分析 system prompt 大小对 LLM 处理时间的影响。"""
        print("\n[G] 分析 system prompt 大小...")
        result: dict[str, Any] = {
            "contract_builder_instructions": None,
            "format_system_prompt_length": None,
            "total_prompt_estimate": None,
            "issues": [],
        }

        # 读取 contract_builder.py 的 _build_instructions_section
        cb_file = self.docuswarm / "prompts" / "contract_builder.py"
        if cb_file.exists():
            content = cb_file.read_text(encoding="utf-8")
            m = re.search(
                r'def _build_instructions_section\(.*?\n(.*?)(?=\n    def |\Z)',
                content,
                re.DOTALL,
            )
            if m:
                instructions_body = m.group(1)
                # 提取 return 的字符串
                return_match = re.search(r'return\s+"""(.*?)"""', instructions_body, re.DOTALL)
                if return_match:
                    instruction_text = return_match.group(1)
                    result["contract_builder_instructions"] = len(instruction_text)
                    print(f"  contract_builder instructions: {len(instruction_text)} chars")

        # 读取 independent.py 的 _format_system_prompt
        ind_file = self.docuswarm / "agents" / "independent.py"
        if ind_file.exists():
            content = ind_file.read_text(encoding="utf-8")
            m = re.search(
                r'instructions\s*=\s*"""(.*?)"""',
                content,
                re.DOTALL,
            )
            if m:
                instr_len = len(m.group(1))
                print(f"  independent.py instructions: {instr_len} chars")

        # 估算 user prompt 大小 (context file + task)
        context_file = ROOT / "docs" / "calc-one-plus-one" / "calc-context.md"
        if context_file.exists():
            ctx_content = context_file.read_text(encoding="utf-8")
            print(f"  calc-context.md: {len(ctx_content)} chars")
            result["total_prompt_estimate"] = (
                f"System: ~3000 chars + User: {len(ctx_content)} chars context + task"
            )
            result["issues"].append(
                f"INFO: 总输入大小约 3000+{len(ctx_content)} chars，"
                "对于简单任务 60s 应当足够，问题不在提示词大小。"
            )

        return result

    # ----------------------------------------------------------
    # 根因识别
    # ----------------------------------------------------------
    def _identify_root_causes(self) -> dict[str, Any]:
        """综合所有分析，识别根因。"""
        print("\n" + "=" * 70)
        print("根因识别")
        print("=" * 70)

        root_causes = {
            "P0_CRITICAL": [],
            "P1_HIGH": [],
            "P2_MEDIUM": [],
            "summary": "",
        }

        # P0: 工具不可见 (最根本原因)
        root_causes["P0_CRITICAL"].append({
            "id": "RC-1",
            "title": "create_deliverable 工具对 LLM 不可见",
            "evidence": [
                "LLM 输出: 'The tools appear to have some issues, but I don't see that [tool]'",
                "超时前 messages_received=13，但无任何 tool_use 调用记录",
                "LLM 知道应该调用工具但无法找到它",
            ],
            "root_cause": (
                "SDK 在 work_dir=output/pipeline_id 环境下无法正确加载 "
                "independent_agent.yaml 中注册的 Python 模块工具。"
                "可能原因: (a) work_dir CWD 变更导致 Python 模块路径解析失败; "
                "(b) agent_file 路径解析错误; "
                "(c) SDK 工具加载机制与 Python 包路径不兼容。"
            ),
            "impact": "LLM 无法调用 create_deliverable 工具 → 无法保存文档 → 无法生成 JSON → parse 失败",
        })

        # P0: 60s 超时值过小
        root_causes["P0_CRITICAL"].append({
            "id": "RC-2",
            "title": "DEFAULT_PROMPT_TIMEOUT=60s 对文档生成任务过短",
            "evidence": [
                "日志: 16:05:07 → 16:06:07，精确 60s 触发超时",
                "LLM 在 60s 内仍在 ThinkingBlock 阶段 (正在推理)",
                "即使工具可用，LLM 也需要 >60s 来生成完整分析报告",
            ],
            "root_cause": (
                "DEFAULT_PROMPT_TIMEOUT 从 1200s 改为 60s 对于 IndependentAgent 场景不合适。"
                "60s 仅适用于简单问答，文档生成需要 LLM 进行深度推理 + 工具调用 + JSON 格式化，"
                "通常需要 120-600s。"
            ),
            "impact": "即使 RC-1 被修复，60s 超时仍会导致大多数节点失败",
        })

        # P1: fallback 机制覆盖不完整
        root_causes["P1_HIGH"].append({
            "id": "RC-3",
            "title": "_parse_response fallback 未处理纯文本/英文散文格式",
            "evidence": [
                "partial content: 'The tools appear to have some issues...' (英文散文，非 Markdown 标题)",
                "fallback 条件: content.startswith(('#','##','###')) OR 'Summary' in content[:100]",
                "条件不匹配 → 直接抛出 response_parse_failed",
            ],
            "root_cause": (
                "fallback 机制设计假设 LLM 返回 Markdown 格式，"
                "但当 LLM 返回纯英文解释性文本时 fallback 不触发。"
                "需要更通用的 fallback: 任何非 JSON 内容都尝试工具结果提取。"
            ),
            "impact": "即使工具已成功调用，部分响应格式也会导致 parse 失败",
        })

        # P1: ThinkingBlock 过滤导致 messages 可能为空
        root_causes["P1_HIGH"].append({
            "id": "RC-4",
            "title": "ThinkingBlock 被过滤 → 超时时 messages 为空列表",
            "evidence": [
                "session_manager._convert_content_block: ThinkingBlock → return None (被丢弃)",
                "messages_received=13 但实际 messages(list[dict]) 可能为空",
                "_parse_response([]) → Empty response from LLM",
            ],
            "root_cause": (
                "SDK 流式响应中 ThinkingBlock 被显式过滤掉 (设计决策)，"
                "但当 LLM 在 60s 内只输出 ThinkingBlock 时，"
                "messages 列表为空，导致 ResponseParseAgentError('Empty response from LLM')。"
                "日志显示 response_parse_failed: 'No JSON found in response' 而非 'Empty response'，"
                "说明至少有部分文本内容，但仍是 partial content。"
            ),
            "impact": "进一步降低 parse 成功率",
        })

        # P2: 错误后继续下一节点
        root_causes["P2_MEDIUM"].append({
            "id": "RC-5",
            "title": "analyst 失败后 pm 节点立即启动 (无中断)",
            "evidence": [
                "日志: 16:06:07 analyst node_execution_failed",
                "日志: 16:06:07 pm node_execution_started (立即)",
                "pipeline 在 analyst 失败后继续运行所有后续节点",
            ],
            "root_cause": (
                "pipeline 的 error handling 策略是继续执行后续节点而非中断。"
                "这在快速失败场景下浪费资源，且后续节点依赖 analyst 输出时会产生连锁失败。"
            ),
            "impact": "所有节点失败，浪费 API 配额",
        })

        root_causes["summary"] = (
            "根本原因是双重的: "
            "(1) create_deliverable 工具对 LLM 不可见 (工具注册/路径问题), "
            "(2) 60s 超时对文档生成任务过短。"
            "这两个 P0 根因协同作用，导致 LLM 既无法调用工具又没有足够时间完成任务。"
            "即使只修复超时问题，工具不可见问题仍会导致失败。"
            "必须同时修复两个 P0 根因。"
        )

        print("\nP0 CRITICAL:")
        for rc in root_causes["P0_CRITICAL"]:
            print(f"  [{rc['id']}] {rc['title']}")

        print("\nP1 HIGH:")
        for rc in root_causes["P1_HIGH"]:
            print(f"  [{rc['id']}] {rc['title']}")

        print("\nP2 MEDIUM:")
        for rc in root_causes["P2_MEDIUM"]:
            print(f"  [{rc['id']}] {rc['title']}")

        return root_causes

    # ----------------------------------------------------------
    # 打印摘要
    # ----------------------------------------------------------
    def _print_summary(self) -> None:
        """打印分析摘要。"""
        print("\n" + "=" * 70)
        print("分析完成")
        print("=" * 70)
        all_issues: list[str] = []
        for key, section in self.results.items():
            if isinstance(section, dict) and "issues" in section:
                all_issues.extend(section["issues"])

        print(f"\n发现问题总数: {len(all_issues)}")
        p0 = [i for i in all_issues if i.startswith("P0")]
        p1 = [i for i in all_issues if i.startswith("P1")]
        p2 = [i for i in all_issues if i.startswith("P2")]
        print(f"  P0 CRITICAL: {len(p0)}")
        print(f"  P1 HIGH: {len(p1)}")
        print(f"  P2 MEDIUM: {len(p2)}")


def main() -> None:
    analyzer = TimeoutIncompleteResponseAnalyzer()
    results = analyzer.run()

    # 保存 JSON 报告
    output_path = ROOT / ".tmp" / "timeout_incomplete_response_analysis.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n分析结果已保存: {output_path}")


if __name__ == "__main__":
    main()
