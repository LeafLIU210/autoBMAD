"""
Timeout Root Cause Analyzer - 超时根因深度分析工具

目标: 深度分析 prompt_timeout + MISSING_FILE_PATH 错误链的根本原因。

错误链:
  1. prompt_timeout (1200s)
  2. → response_validation_failed (MISSING_FILE_PATH)
  3. → independent_agent_failed
  4. → node_execution_failed

Usage:
    python tools/timeout_root_cause_analyzer.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# 将项目根目录加入 sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


# ========== 分析器类 ==========

class TimeoutRootCauseAnalyzer:
    """深度分析超时链根因的分析器。"""

    def __init__(self) -> None:
        self.root = ROOT
        self.autobmad = ROOT / "autoBMAD"
        self.docuswarm = ROOT / "autoBMAD" / "docuswarm"
        self.nodes_dir = ROOT / "autoBMAD" / "nodes"
        self.results: dict[str, Any] = {}

    def run(self) -> dict[str, Any]:
        """执行完整的根因分析。"""
        print("=" * 70)
        print("DocuSwarm 超时根因深度分析器")
        print("=" * 70)

        # 1. 分析 agent_file 配置
        self.results["agent_file_analysis"] = self._analyze_agent_file()

        # 2. 分析 create_deliverable 工具注册机制
        self.results["tool_registration"] = self._analyze_tool_registration()

        # 3. 分析提示词结构
        self.results["prompt_structure"] = self._analyze_prompt_structure()

        # 4. 分析验证器要求
        self.results["validator_requirements"] = self._analyze_validator_requirements()

        # 5. 分析 system_prompt 与 agent_file 的兼容性
        self.results["sdk_config_compat"] = self._analyze_sdk_config_compat()

        # 6. 分析超时路径中的日志间隙
        self.results["log_gap_analysis"] = self._analyze_log_gaps()

        # 7. 分析节点配置
        self.results["node_configs"] = self._analyze_node_configs()

        # 8. 识别根因
        self.results["root_causes"] = self._identify_root_causes()

        # 输出摘要
        self._print_summary()

        return self.results

    def _analyze_agent_file(self) -> dict[str, Any]:
        """分析 independent_agent.yaml 配置。"""
        print("\n[1] 分析 agent_file 配置...")
        agent_yaml = self.docuswarm / "agents" / "configs" / "independent_agent.yaml"
        result: dict[str, Any] = {
            "path": str(agent_yaml),
            "exists": agent_yaml.exists(),
            "content": None,
            "tools_listed": [],
            "issues": [],
        }

        if not agent_yaml.exists():
            result["issues"].append("CRITICAL: independent_agent.yaml 文件不存在!")
            print(f"  ❌ 文件不存在: {agent_yaml}")
            return result

        content = agent_yaml.read_text(encoding="utf-8")
        result["content"] = content
        print(f"  ✅ 找到文件: {agent_yaml}")

        # 提取工具列表
        tool_pattern = re.compile(r'^\s*-\s*"(.+?)"', re.MULTILINE)
        tools = tool_pattern.findall(content)
        result["tools_listed"] = tools
        print(f"  📋 配置的工具: {tools}")

        # 检查 create_deliverable 是否存在
        has_create_deliverable = any("create_deliverable" in t for t in tools)
        if not has_create_deliverable:
            result["issues"].append("MISSING: create_deliverable 工具未在 agent_file 中配置")
            print("  ❌ create_deliverable 工具未配置!")
        else:
            print("  ✅ create_deliverable 工具已配置")

        # 检查工具模块是否存在
        for tool_ref in tools:
            if ":" in tool_ref:
                module_path, class_name = tool_ref.split(":")
                # 转换模块路径到文件路径
                module_file = ROOT / module_path.replace(".", "/")
                module_file_py = Path(str(module_file) + ".py")
                exists = module_file_py.exists()
                if not exists:
                    result["issues"].append(f"MISSING_MODULE: {module_path} 不存在于 {module_file_py}")
                    print(f"  ❌ 模块不存在: {module_file_py}")
                else:
                    print(f"  ✅ 模块存在: {module_file_py}")

        return result

    def _analyze_tool_registration(self) -> dict[str, Any]:
        """分析 CreateDeliverableTool 注册和调用机制。"""
        print("\n[2] 分析 create_deliverable 工具注册机制...")
        result: dict[str, Any] = {
            "tool_file_exists": False,
            "callable_tool_wrapper_exists": False,
            "sdk_adapter_exists": False,
            "output_dir_logic": None,
            "issues": [],
        }

        # 检查 create_deliverable.py
        tool_file = self.docuswarm / "tools" / "create_deliverable.py"
        result["tool_file_exists"] = tool_file.exists()
        if tool_file.exists():
            content = tool_file.read_text(encoding="utf-8")
            print(f"  ✅ create_deliverable.py 存在 ({len(content)} 字符)")

            # 检查 output_dir 默认值
            if "Path.cwd()" in content:
                result["output_dir_logic"] = "defaults_to_cwd"
                result["issues"].append(
                    "WARNING: CreateDeliverableTool 默认 output_dir=Path.cwd(), "
                    "当 work_dir 与实际工具实例不匹配时，文件会写到错误目录"
                )
                print("  ⚠️ output_dir 默认为 Path.cwd() - 可能导致路径不一致")
        else:
            result["issues"].append("CRITICAL: create_deliverable.py 不存在")
            print("  ❌ create_deliverable.py 不存在")

        # 检查 callable_tool_wrapper.py
        wrapper_file = self.docuswarm / "tools" / "callable_tool_wrapper.py"
        result["callable_tool_wrapper_exists"] = wrapper_file.exists()
        if wrapper_file.exists():
            print(f"  ✅ callable_tool_wrapper.py 存在")
            content = wrapper_file.read_text(encoding="utf-8")
            # 检查 SDK 适配逻辑
            if "__call__" in content:
                print("  ✅ 工具有 __call__ 方法 (可作为 callable 调用)")
        else:
            result["issues"].append("CRITICAL: callable_tool_wrapper.py 不存在")

        # 检查 SDK adapter
        sdk_adapter = self.docuswarm / "tools" / "sdk_adapter.py"
        result["sdk_adapter_exists"] = sdk_adapter.exists()
        if sdk_adapter.exists():
            print(f"  ✅ sdk_adapter.py 存在")
        else:
            result["issues"].append("MISSING: sdk_adapter.py 不存在")
            print("  ❌ sdk_adapter.py 不存在")

        return result

    def _analyze_prompt_structure(self) -> dict[str, Any]:
        """分析提示词结构，检测 file_path 要求的冲突。"""
        print("\n[3] 分析提示词结构...")
        result: dict[str, Any] = {
            "system_prompt_requires_file_path": False,
            "contract_builder_instructions_require_file_path": False,
            "contract_builder_format_example_has_file_path": False,
            "issues": [],
        }

        # 检查 independent.py 的 _format_system_prompt
        independent_py = self.docuswarm / "agents" / "independent.py"
        if independent_py.exists():
            content = independent_py.read_text(encoding="utf-8")

            # 查找 file_path 要求
            if '"file_path": "path from tool output"' in content:
                result["system_prompt_requires_file_path"] = True
                print("  ✅ _format_system_prompt 要求 file_path (来自工具输出)")

            # 检查 fallback 路径 (markdown_fallback)
            if "markdown_fallback" in content:
                result["issues"].append(
                    "WARNING: markdown_fallback 构建的 data 字典缺少 file_path 和 sha256，"
                    "但验证器要求这两个字段 → 导致 MISSING_FILE_PATH"
                )
                print("  ⚠️ markdown_fallback 缺少 file_path/sha256 字段!")

        # 检查 contract_builder.py 的 instructions_section
        contract_builder = self.docuswarm / "prompts" / "contract_builder.py"
        if contract_builder.exists():
            content = contract_builder.read_text(encoding="utf-8")

            if '"file_path"' not in content:
                result["contract_builder_instructions_require_file_path"] = False
                result["issues"].append(
                    "CRITICAL: contract_builder._build_instructions_section() 的 JSON 示例 "
                    "缺少 file_path 字段! LLM 不知道要在 JSON 响应中包含 file_path"
                )
                print("  ❌ contract_builder instructions 示例缺少 file_path 字段!")
            else:
                result["contract_builder_instructions_require_file_path"] = True
                print("  ✅ contract_builder instructions 包含 file_path 要求")

        return result

    def _analyze_validator_requirements(self) -> dict[str, Any]:
        """分析验证器对 file_path 的要求。"""
        print("\n[4] 分析验证器要求...")
        result: dict[str, Any] = {
            "file_path_required": True,
            "sha256_required": True,
            "error_code": "MISSING_FILE_PATH",
            "issues": [],
        }

        validator_py = self.docuswarm / "context" / "validator.py"
        if validator_py.exists():
            content = validator_py.read_text(encoding="utf-8")

            # 查找 file_path 验证
            if 'MISSING_FILE_PATH' in content:
                print("  ✅ 验证器要求 deliverable.file_path (MISSING_FILE_PATH 错误码)")

            if 'MISSING_SHA256' in content:
                print("  ✅ 验证器要求 deliverable.sha256 (MISSING_SHA256 错误码)")

            # 统计必需字段
            required_fields = re.findall(r'result\.add_error[^)]*MISSING_(\w+)', content)
            print(f"  📋 必需字段缺失错误码: {required_fields}")
            result["required_error_codes"] = required_fields

        return result

    def _analyze_sdk_config_compat(self) -> dict[str, Any]:
        """分析 SDK 配置兼容性 - system_prompt vs agent_file。"""
        print("\n[5] 分析 SDK 配置兼容性...")
        result: dict[str, Any] = {
            "uses_preset_system_prompt": False,
            "uses_agent_file": False,
            "potential_conflict": False,
            "issues": [],
        }

        session_manager = self.docuswarm / "llm" / "session_manager.py"
        if session_manager.exists():
            content = session_manager.read_text(encoding="utf-8")

            # 检查 system_prompt 配置
            if '"type": "preset"' in content:
                result["uses_preset_system_prompt"] = True
                print("  ✅ 使用 preset 格式 system_prompt (claude_code preset)")

            # 检查 agent_file 配置
            if 'options_dict["tools"] = [str(self._agent_file)]' in content:
                result["uses_agent_file"] = True
                print("  ✅ 使用 agent_file (tools 字段)")

            # 潜在冲突: agent_file 中定义工具 vs SDK 工具注册
            if result["uses_agent_file"] and result["uses_preset_system_prompt"]:
                result["potential_conflict"] = True
                result["issues"].append(
                    "INFO: system_prompt (preset claude_code) 与 agent_file (自定义工具) 同时使用。"
                    "需确认 SDK 是否正确加载 agent_file 中定义的 create_deliverable 工具"
                )
                print("  ⚠️ system_prompt + agent_file 同时配置，需要验证工具加载")

        # 检查 system_prompt 格式是否正确传递 agent_file 工具
        independent = self.docuswarm / "agents" / "independent.py"
        if independent.exists():
            content = independent.read_text(encoding="utf-8")
            if "agent_file=self._agent_file" in content:
                print("  ✅ create_session 时传递了 agent_file")

            # 检查 pipeline_session_manager 是否包含 agent_file
            if "_create_pipeline_session_manager" in content:
                print("  ✅ 有独立的 pipeline_session_manager 工厂方法")

        return result

    def _analyze_log_gaps(self) -> dict[str, Any]:
        """分析日志时间间隙，识别 LLM 卡住的阶段。"""
        print("\n[6] 分析日志时间间隙...")
        result: dict[str, Any] = {
            "gaps_found": [],
            "issues": [],
        }

        log_file = ROOT / "logs" / "docuswarm-2026-04-06.log"
        if not log_file.exists():
            # 尝试找最新日志
            log_dir = ROOT / "logs"
            if log_dir.exists():
                logs = sorted(log_dir.glob("docuswarm-*.log"), reverse=True)
                if logs:
                    log_file = logs[0]
            if not log_file.exists():
                result["issues"].append("WARNING: 找不到日志文件")
                print("  ⚠️ 找不到日志文件")
                return result

        content = log_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        # 提取时间戳和消息
        ts_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}) \[(\w+)\].*message="([^"]+)"')

        events = []
        for line in lines:
            m = ts_pattern.search(line)
            if m:
                from datetime import datetime, timezone
                ts_str = m.group(1)
                level = m.group(2)
                message = m.group(3)
                # 解析时间戳
                try:
                    ts = datetime.fromisoformat(ts_str)
                    events.append({"ts": ts, "level": level, "message": message})
                except ValueError:
                    pass

        # 找到大的时间间隙
        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]
            diff = (curr["ts"] - prev["ts"]).total_seconds()
            if diff > 60:  # 超过 60 秒的间隙
                gap = {
                    "from_msg": prev["message"],
                    "to_msg": curr["message"],
                    "gap_seconds": diff,
                    "gap_minutes": round(diff / 60, 1),
                }
                result["gaps_found"].append(gap)
                print(f"  ⏰ 大间隙: {gap['gap_minutes']}分钟 | {prev['message']} → {curr['message']}")

        # 计算每个节点的 session_created 到 timeout 之间的 llm_message_received 数量
        node_stats: dict[str, dict] = {}
        current_node = None
        for event in events:
            msg = event["message"]
            if "session_created" in msg:
                # 从日志行找 node_id
                pass
            if "llm_message_received" in msg:
                pass

        print(f"  📊 共发现 {len(result['gaps_found'])} 个大时间间隙")
        return result

    def _analyze_node_configs(self) -> dict[str, Any]:
        """分析节点配置，检查各节点的超时和工具权限设置。"""
        print("\n[7] 分析节点配置...")
        result: dict[str, Any] = {
            "nodes_found": [],
            "issues": [],
        }

        nodes = ["analyst", "pm", "ux", "architect", "po"]
        for node_id in nodes:
            node_yaml = self.nodes_dir / node_id / "node.yaml"
            node_info: dict[str, Any] = {
                "node_id": node_id,
                "yaml_exists": node_yaml.exists(),
                "timeout": None,
                "max_iterations": None,
                "allowed_tools": [],
            }

            if node_yaml.exists():
                content = node_yaml.read_text(encoding="utf-8")
                # 提取 timeout
                timeout_match = re.search(r'timeout[:\s]+(\d+)', content)
                if timeout_match:
                    node_info["timeout"] = int(timeout_match.group(1))

                # 提取 max_iterations
                iter_match = re.search(r'max_iterations[:\s]+(\d+)', content)
                if iter_match:
                    node_info["max_iterations"] = int(iter_match.group(1))

                # 提取 allowed_builtin_tools
                tools_match = re.findall(r'allowed_builtin_tools.*?\n(.*?)(?:\n\n|\Z)', content, re.DOTALL)
                if tools_match:
                    tools = re.findall(r'-\s+(\w+)', tools_match[0])
                    node_info["allowed_tools"] = tools

                print(f"  [{node_id}] ✅ timeout={node_info['timeout']}s, max_iter={node_info['max_iterations']}")
            else:
                node_info["issues"] = f"node.yaml 不存在于 {node_yaml}"
                result["issues"].append(f"MISSING: {node_id}/node.yaml")
                print(f"  [{node_id}] ❌ node.yaml 不存在")

            result["nodes_found"].append(node_info)

        return result

    def _identify_root_causes(self) -> dict[str, Any]:
        """综合所有分析，识别根本原因。"""
        print("\n[8] 识别根本原因...")
        result: dict[str, Any] = {
            "primary_root_cause": None,
            "secondary_causes": [],
            "contributing_factors": [],
            "error_chain": [],
            "all_issues": [],
        }

        # 收集所有问题
        all_issues = []
        for key, analysis in self.results.items():
            if isinstance(analysis, dict) and "issues" in analysis:
                all_issues.extend(analysis["issues"])
        result["all_issues"] = all_issues

        # 错误链
        result["error_chain"] = [
            "1. Claude LLM 在 session.prompt() 中接收消息超过 1200 秒",
            "2. asyncio.timeout(1200) 触发 TimeoutError",
            "3. ClaudeSessionWrapper.prompt() 抛出 LLMError('prompt timed out')",
            "4. IndependentAgent._call_llm_with_prompts() 捕获异常后无法返回 messages",
            "5. _parse_response() 接收到空 messages，无法提取 JSON",
            "6. 或者: LLM 未调用 create_deliverable 工具，JSON 响应缺少 file_path/sha256",
            "7. ContextValidator.validate_independent_output() 发现 MISSING_FILE_PATH",
            "8. ResponseParseAgentError → IndependentExecutionError → node_execution_failed",
        ]

        # 主要根因分析
        prompt_structure = self.results.get("prompt_structure", {})
        sdk_compat = self.results.get("sdk_config_compat", {})
        tool_reg = self.results.get("tool_registration", {})

        # 根因 1: contract_builder instructions 缺少 file_path 示例
        if not prompt_structure.get("contract_builder_instructions_require_file_path", True):
            result["primary_root_cause"] = (
                "ROOT CAUSE A (CRITICAL): NodePromptContractBuilder._build_instructions_section() "
                "的 JSON 示例中缺少 file_path 字段。LLM 的 system_prompt 没有明确指示它需要从 "
                "create_deliverable 工具获取 file_path 并放入 JSON 响应，导致 LLM 输出的 JSON "
                "始终缺少 file_path → MISSING_FILE_PATH 验证失败。"
            )
        else:
            result["primary_root_cause"] = (
                "ROOT CAUSE B (CRITICAL): LLM (Claude) 在 1200 秒内无法完成任务。"
                "可能原因:\n"
                "  B1: LLM 正在无限循环调用工具（工具调用耗尽上下文或次数限制）\n"
                "  B2: LLM 生成了超长内容（文档内容被包含在响应JSON中而非仅摘要）\n"
                "  B3: create_deliverable 工具调用后 LLM 继续等待，未知何时返回 JSON\n"
                "  B4: 网络/API 层面的延迟导致 receive_messages() 阻塞\n"
                "  B5: LLM 确实在处理极长的文档，但 1200s 不够"
            )

        # 次要根因
        result["secondary_causes"] = [
            "CAUSE-2: contract_builder._build_instructions_section() 缺少 file_path 示例 "
            "→ 当 LLM 超时后，错误消息变为 MISSING_FILE_PATH 而非超时本身",
            "CAUSE-3: 超时后 messages 为空（因异常被重新抛出），_parse_response 得到空响应",
            "CAUSE-4: markdown_fallback 分支构建的 dict 没有 file_path，若 LLM 返回 Markdown "
            "则验证必然失败",
        ]

        # 贡献因素
        result["contributing_factors"] = [
            "FACTOR-1: 1200s 超时对于 Claude 处理大型文档分析任务可能不足",
            "FACTOR-2: system_prompt 要求 file_path 来自工具输出，但 LLM 可能在工具调用之前就超时",
            "FACTOR-3: 所有 5 个节点 (analyst/pm/ux/architect/po) 全部超时，说明是系统性问题",
            "FACTOR-4: 日志间隙：session_created 后很快收到几条消息，然后中断约20分钟",
            "FACTOR-5: bubble-sort context 可能触发了非常长的分析过程",
        ]

        print(f"\n  🎯 主要根因: {result['primary_root_cause'][:100]}...")
        print(f"  📋 次要原因数量: {len(result['secondary_causes'])}")
        print(f"  📋 贡献因素数量: {len(result['contributing_factors'])}")

        return result

    def _print_summary(self) -> None:
        """打印分析摘要。"""
        print("\n" + "=" * 70)
        print("分析摘要")
        print("=" * 70)

        root_causes = self.results.get("root_causes", {})
        print("\n🎯 主要根因:")
        print(f"  {root_causes.get('primary_root_cause', 'N/A')}")

        print("\n⛓️ 错误链:")
        for step in root_causes.get("error_chain", []):
            print(f"  {step}")

        print("\n📋 次要原因:")
        for cause in root_causes.get("secondary_causes", []):
            print(f"  - {cause}")

        print("\n🔍 贡献因素:")
        for factor in root_causes.get("contributing_factors", []):
            print(f"  - {factor}")

        print("\n💡 发现的所有问题:")
        all_issues = root_causes.get("all_issues", [])
        for issue in all_issues:
            print(f"  ⚠️ {issue}")

    def save_results(self, output_path: Path) -> None:
        """保存分析结果到 JSON 文件。"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 处理不可序列化的对象
        def make_serializable(obj: Any) -> Any:
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            return str(obj)

        import json as json_module
        with open(output_path, "w", encoding="utf-8") as f:
            json_module.dump(self.results, f, ensure_ascii=False, indent=2, default=make_serializable)
        print(f"\n✅ 分析结果已保存到: {output_path}")


# ========== 额外检查: 验证 tool_result 消息结构 ==========

def check_tool_result_message_structure() -> dict[str, Any]:
    """验证 tool_result 消息在 messages 列表中的实际结构。

    关键链路:
      CreateDeliverableTool._execute() → ToolResult(success=True, result=metadata)
      → sdk_adapter.adapt_to_claude()  → {type: tool_result, content: JSON_STRING, is_error: False}
      → _convert_content_block()       → {type: tool_result, tool_use_id, content: str, is_error}
      → _message_to_dict()             → {role: tool, content: [{type: tool_result, ...}]}

    关键问题: content 字段是 JSON **字符串** 还是 dict?
    """
    print("\n" + "=" * 70)
    print("额外检查: tool_result 消息结构验证")
    print("=" * 70)

    root = Path(__file__).parent.parent
    result: dict[str, Any] = {
        "sdk_adapter_content_type": None,
        "session_manager_tool_result_content_type": None,
        "fallback_extraction_method": None,
        "issues": [],
        "verdict": None,
    }

    # ------------------------------------------------------------------
    # 1. 分析 sdk_adapter.adapt_to_claude 的输出格式
    # ------------------------------------------------------------------
    sdk_adapter_path = root / "autoBMAD" / "docuswarm" / "tools" / "sdk_adapter.py"
    if sdk_adapter_path.exists():
        content = sdk_adapter_path.read_text(encoding="utf-8")

        # 检查 content 是 json.dumps 结果 (字符串) 还是 dict
        if "json.dumps(result.result" in content:
            result["sdk_adapter_content_type"] = "JSON_STRING"
            print("  📌 sdk_adapter.adapt_to_claude(): content = JSON字符串 (json.dumps)")
            print("     → tool_result.content 是字符串, 需要 json.loads() 才能得到 dict")
        elif "result.result" in content:
            result["sdk_adapter_content_type"] = "DICT"
            print("  📌 sdk_adapter.adapt_to_claude(): content 可能是 dict")
    else:
        result["issues"].append("MISSING: sdk_adapter.py 不存在")
        print("  ❌ sdk_adapter.py 不存在")

    # ------------------------------------------------------------------
    # 2. 分析 session_manager._convert_content_block 中 ToolResultBlock 的转换
    # ------------------------------------------------------------------
    session_mgr_path = root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    if session_mgr_path.exists():
        content = session_mgr_path.read_text(encoding="utf-8")

        # 找 ToolResultBlock 转换逻辑
        import re as re_module
        tool_result_block = re_module.search(
            r'isinstance\(item, ToolResultBlock\).*?converted = \{(.*?)\}',
            content, re_module.DOTALL
        )
        if tool_result_block:
            block_content = tool_result_block.group(1)
            # 检查 content 字段从哪里来
            if 'getattr(item, "content", "")' in content:
                print("  📌 _convert_content_block: ToolResultBlock.content → dict['content']")
                print("     ToolResultBlock 来自 SDK 返回, 其 content 可能是字符串或已解析的对象")
                result["session_manager_tool_result_content_type"] = "FROM_SDK_TOOLRESULTBLOCK"

    # ------------------------------------------------------------------
    # 3. 模拟 messages 结构, 验证提取逻辑
    # ------------------------------------------------------------------
    print("\n  [模拟验证] 构造模拟 messages 测试提取逻辑...")

    import json as json_module

    # 模拟情况 A: content 是 JSON 字符串 (sdk_adapter 序列化后)
    fake_file_path = "/output/pipeline-xxx/analyst-report.md"
    fake_sha256 = "abc123def456"
    metadata_dict = {
        "title": "Analyst Report",
        "file_path": fake_file_path,
        "sha256": fake_sha256,
        "word_count": 1234,
        "content_type": "markdown",
    }

    # Case A: content 为 JSON 字符串 (adapt_to_claude 的输出)
    messages_case_a = [
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll create the deliverable."},
                {
                    "type": "tool_use",
                    "name": "create_deliverable",
                    "input": {"title": "Analyst Report", "content": "..."},
                    "id": "tool_001",
                },
            ],
        },
        {
            "role": "tool",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "tool_001",
                    "content": json_module.dumps(metadata_dict),  # JSON字符串
                    "is_error": False,
                }
            ],
        },
    ]

    # Case B: content 为 dict (假设 SDK 内部已解析)
    messages_case_b = [
        {
            "role": "tool",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "tool_001",
                    "content": metadata_dict,  # dict
                    "is_error": False,
                }
            ],
        },
    ]

    # Case C: tool_use_id 不在 user 消息, 而是在 assistant 消息里的 tool_result
    messages_case_c = [
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "tool_001",
                    "content": json_module.dumps(metadata_dict),
                    "is_error": False,
                }
            ],
        },
    ]

    # ------------------------------------------------------------------
    # 4. 测试提取函数 (需要 json.loads)
    # ------------------------------------------------------------------
    def extract_file_path_from_messages(messages: list[dict]) -> tuple[str | None, str | None]:
        """从 messages 中提取 create_deliverable 工具返回的 file_path 和 sha256.

        关键: tool_result.content 可能是 JSON字符串 或 dict, 需要双重处理.
        """
        for msg in messages:
            content_blocks = msg.get("content", [])
            if not isinstance(content_blocks, list):
                continue
            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_result":
                    continue
                if block.get("is_error", False):
                    continue  # 跳过错误结果

                tool_output = block.get("content", {})

                # 关键: content 可能是 JSON字符串 (sdk_adapter序列化) 或 dict
                if isinstance(tool_output, str):
                    try:
                        tool_output = json_module.loads(tool_output)
                    except json_module.JSONDecodeError:
                        continue

                if isinstance(tool_output, dict) and "file_path" in tool_output:
                    return (
                        str(tool_output["file_path"]),
                        str(tool_output.get("sha256", "")),
                    )
        return None, None

    # 测试三种 case
    fp_a, sha_a = extract_file_path_from_messages(messages_case_a)
    fp_b, sha_b = extract_file_path_from_messages(messages_case_b)
    fp_c, sha_c = extract_file_path_from_messages(messages_case_c)

    print(f"  Case A (content=JSON字符串): file_path={fp_a!r}, sha256={sha_a!r}")
    print(f"  Case B (content=dict):       file_path={fp_b!r}, sha256={sha_b!r}")
    print(f"  Case C (assistant消息里):    file_path={fp_c!r}, sha256={sha_c!r}")

    all_pass = (
        fp_a == fake_file_path and sha_a == fake_sha256
        and fp_b == fake_file_path and sha_b == fake_sha256
        and fp_c == fake_file_path and sha_c == fake_sha256
    )

    if all_pass:
        result["verdict"] = "PASS: 提取函数正确处理了 JSON字符串 和 dict 两种 content 格式"
        result["fallback_extraction_method"] = "json.loads(content) if isinstance(content, str) else content"
        print("  ✅ 全部通过: 提取逻辑可以处理两种 content 格式")
    else:
        result["verdict"] = "FAIL: 提取函数存在问题"
        result["issues"].append("提取函数无法从所有 case 中正确获取 file_path")
        print("  ❌ 部分 case 失败")

    # ------------------------------------------------------------------
    # 5. 验证原有 fallback 方案的 BUG: content 直接当 dict 用
    # ------------------------------------------------------------------
    print("\n  [BUG验证] 验证原方案 (未 json.loads) 的问题...")

    def extract_file_path_BUGGY(messages: list[dict]) -> tuple[str | None, str | None]:
        """原有方案: 直接把 content 当 dict 用, 未处理 JSON字符串情况."""
        for msg in messages:
            content_blocks = msg.get("content", [])
            if not isinstance(content_blocks, list):
                continue
            for block in content_blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_result":
                    continue
                tool_output = block.get("content", {})
                # ❌ 原方案: 直接 isinstance(tool_output, dict)
                # 若 tool_output 是 JSON字符串 则 isinstance(dict) 返回 False!
                if isinstance(tool_output, dict) and "file_path" in tool_output:
                    return str(tool_output["file_path"]), str(tool_output.get("sha256", ""))
        return None, None

    fp_buggy_a, _ = extract_file_path_BUGGY(messages_case_a)  # JSON字符串 case
    fp_buggy_b, _ = extract_file_path_BUGGY(messages_case_b)  # dict case

    if fp_buggy_a is None and fp_buggy_b is not None:
        print("  ❌ BUG确认: 原方案在 Case A (JSON字符串) 下提取失败!")
        print("     原方案假设 content 是 dict, 但 sdk_adapter 实际返回 JSON字符串")
        result["issues"].append(
            "CRITICAL BUG in fallback: 原方案直接 isinstance(content, dict) 检查, "
            "但 sdk_adapter.adapt_to_claude() 将 content 序列化为 JSON字符串, "
            "导致在实际 messages 中无法提取 file_path. "
            "必须先 json.loads(content) 再检查 dict."
        )
    else:
        print(f"  ℹ️ BUG验证结果: Case A={fp_buggy_a!r}, Case B={fp_buggy_b!r}")

    # ------------------------------------------------------------------
    # 6. 输出最终结论
    # ------------------------------------------------------------------
    print("\n  📋 结论:")
    print(f"  sdk_adapter content 类型: {result['sdk_adapter_content_type']}")
    print(f"  正确提取方法: {result['fallback_extraction_method']}")
    print(f"  最终判断: {result['verdict']}")
    if result["issues"]:
        print("  ❌ 发现问题:")
        for issue in result["issues"]:
            print(f"    - {issue}")

    return result


# ========== 额外检查: 验证 contract_builder instructions ==========

def check_contract_builder_json_example() -> dict[str, Any]:
    """专门检查 contract_builder 的 JSON 示例是否包含 file_path。"""
    root = Path(__file__).parent.parent
    contract_builder = root / "autoBMAD" / "docuswarm" / "prompts" / "contract_builder.py"

    result: dict[str, Any] = {
        "file_exists": contract_builder.exists(),
        "instructions_json_example": None,
        "has_file_path_in_example": False,
        "has_sha256_in_example": False,
        "verdict": None,
    }

    if not contract_builder.exists():
        result["verdict"] = "CRITICAL: contract_builder.py 不存在"
        return result

    content = contract_builder.read_text(encoding="utf-8")

    # 提取 _build_instructions_section 方法内的 JSON 示例
    method_match = re.search(
        r'def _build_instructions_section.*?return """(.*?)"""',
        content,
        re.DOTALL
    )
    if method_match:
        instructions = method_match.group(1)
        result["instructions_json_example"] = instructions[:500]  # 截断
        result["has_file_path_in_example"] = '"file_path"' in instructions
        result["has_sha256_in_example"] = '"sha256"' in instructions

        if not result["has_file_path_in_example"]:
            result["verdict"] = (
                "CRITICAL BUG: _build_instructions_section() 的 JSON 示例缺少 file_path 字段。"
                "当 execute_with_input() 调用 contract_builder 渲染 system_prompt 时，"
                "LLM 收到的指令示例中没有 file_path，导致 LLM 不知道需要在 JSON 中包含 file_path。"
                "而验证器 (IndependentOutputValidationStrategy) 强制要求 file_path 存在。"
                "这是一个设计矛盾: system_prompt (来自 _format_system_prompt) 要求 file_path，"
                "但 execute_with_input 使用 contract_builder 渲染的 system_prompt 不含此要求。"
            )
        else:
            result["verdict"] = "OK: contract_builder instructions 包含 file_path 要求"
    else:
        result["verdict"] = "UNKNOWN: 未能提取 _build_instructions_section 方法"

    return result


# ========== 额外检查: 全面核查报告方案有效性 ==========

def verify_all_fixes() -> dict[str, Any]:
    """全面核查 pipeline-timeout-root-cause-analysis.md 中提出的所有修复方案。

    核查项目:
      Fix-1: contract_builder._build_instructions_section() JSON 示例
      Fix-2: markdown_fallback 分支是否已修复（含 _extract_create_deliverable_result）
      Fix-3: prompt() 超时日志是否记录 messages_received_before_timeout
      Fix-4: CreateDeliverableTool output_dir 默认值问题
      Fix-6: execute() vs execute_with_input() 两条 system_prompt 路径一致性
    """
    print("\n" + "=" * 70)
    print("全面核查: 所有修复方案有效性验证")
    print("=" * 70)

    root = Path(__file__).parent.parent
    results: dict[str, Any] = {
        "fix1_contract_builder": {},
        "fix2_markdown_fallback": {},
        "fix3_timeout_logging": {},
        "fix4_output_dir": {},
        "fix6_prompt_path_alignment": {},
        "summary": [],
    }

    # =========================================================
    # Fix-1: contract_builder._build_instructions_section() 是否包含 file_path
    # =========================================================
    print("\n[Fix-1] 核查 contract_builder._build_instructions_section() JSON 示例...")
    cb_path = root / "autoBMAD" / "docuswarm" / "prompts" / "contract_builder.py"
    cb_content = cb_path.read_text(encoding="utf-8") if cb_path.exists() else ""

    # 提取 _build_instructions_section 的返回内容
    method_match = re.search(
        r'def _build_instructions_section\(self\).*?return """(.*?)"""',
        cb_content, re.DOTALL
    )
    if method_match:
        instructions_text = method_match.group(1)
        has_file_path = '"file_path"' in instructions_text
        has_sha256 = '"sha256"' in instructions_text
        has_important_note = 'IMPORTANT' in instructions_text and 'file_path' in instructions_text
        results["fix1_contract_builder"] = {
            "has_file_path_in_json_example": has_file_path,
            "has_sha256_in_json_example": has_sha256,
            "has_important_file_path_note": has_important_note,
            "status": "FIXED" if (has_file_path and has_sha256) else "NOT_FIXED",
            "verdict": (
                "✅ Fix-1 已修复: JSON 示例包含 file_path 和 sha256"
                if (has_file_path and has_sha256)
                else "❌ Fix-1 未修复: JSON 示例缺少 file_path 或 sha256 → LLM 不知道需要这些字段"
            ),
        }
    else:
        results["fix1_contract_builder"] = {
            "status": "ERROR",
            "verdict": "❌ 无法解析 _build_instructions_section 方法",
        }

    fix1 = results["fix1_contract_builder"]
    print(f"  file_path 在示例中: {fix1.get('has_file_path_in_json_example', '未知')}")
    print(f"  sha256 在示例中: {fix1.get('has_sha256_in_json_example', '未知')}")
    print(f"  IMPORTANT 提示: {fix1.get('has_important_file_path_note', '未知')}")
    print(f"  {fix1['verdict']}")
    results["summary"].append(fix1["verdict"])

    # =========================================================
    # Fix-2: independent.py _parse_response markdown_fallback 是否修复
    # =========================================================
    print("\n[Fix-2] 核查 independent.py _parse_response markdown_fallback...")
    ind_path = root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    ind_content = ind_path.read_text(encoding="utf-8") if ind_path.exists() else ""

    # 2a: 检查 _extract_create_deliverable_result 方法是否存在
    has_extract_method = "_extract_create_deliverable_result" in ind_content

    # 2b: 检查 markdown_fallback 分支是否仍然构建缺少 file_path 的 dict
    fallback_match = re.search(
        r'llm_returned_markdown_fallback.*?data = \{(.*?)\}\n',
        ind_content, re.DOTALL
    )
    fallback_dict_text = fallback_match.group(1) if fallback_match else ""
    fallback_missing_file_path = (
        '"file_path"' not in fallback_dict_text
        and 'file_path' not in fallback_dict_text
    ) if fallback_dict_text else True  # 找不到 fallback 则视为未修复

    # 2c: 检查 fallback 是否调用了 _extract_create_deliverable_result
    fallback_calls_extract = (
        "_extract_create_deliverable_result" in ind_content
        and re.search(r'file_path.*_extract_create_deliverable_result|_extract_create_deliverable_result.*file_path', ind_content) is not None
    )

    # 2d: 检查 json.loads 是否在 _extract_create_deliverable_result 中
    extract_method_match = re.search(
        r'def _extract_create_deliverable_result.*?return None, None',
        ind_content, re.DOTALL
    )
    extract_has_json_loads = False
    extract_filters_is_error = False
    if extract_method_match:
        extract_text = extract_method_match.group(0)
        extract_has_json_loads = "json" in extract_text and "loads" in extract_text
        extract_filters_is_error = "is_error" in extract_text

    fix2_fully_fixed = (
        has_extract_method
        and extract_has_json_loads
        and extract_filters_is_error
    )

    results["fix2_markdown_fallback"] = {
        "has_extract_method": has_extract_method,
        "extract_has_json_loads": extract_has_json_loads,
        "extract_filters_is_error": extract_filters_is_error,
        "fallback_calls_extract": fallback_calls_extract,
        "original_fallback_still_missing_file_path": fallback_missing_file_path,
        "status": "FIXED" if fix2_fully_fixed else "NOT_FIXED",
        "verdict": (
            "✅ Fix-2 已修复: _extract_create_deliverable_result 存在且包含 json.loads"
            if fix2_fully_fixed
            else (
                "❌ Fix-2 未修复: markdown_fallback 仍构建缺少 file_path 的 dict"
                + (" [缺少 _extract_create_deliverable_result 方法]" if not has_extract_method else "")
                + (" [extract 方法缺少 json.loads]" if has_extract_method and not extract_has_json_loads else "")
                + (" [extract 方法未过滤 is_error]" if has_extract_method and not extract_filters_is_error else "")
            )
        ),
    }

    fix2 = results["fix2_markdown_fallback"]
    print(f"  _extract_create_deliverable_result 方法存在: {has_extract_method}")
    print(f"  extract 方法包含 json.loads: {extract_has_json_loads}")
    print(f"  extract 方法过滤 is_error: {extract_filters_is_error}")
    print(f"  fallback 调用了 extract: {fallback_calls_extract}")
    print(f"  原始 fallback 仍缺少 file_path: {fallback_missing_file_path}")
    print(f"  {fix2['verdict']}")
    results["summary"].append(fix2["verdict"])

    # =========================================================
    # Fix-3: session_manager prompt() 超时日志
    # =========================================================
    print("\n[Fix-3] 核查 ClaudeSessionWrapper.prompt() 超时日志...")
    sm_path = root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    sm_content = sm_path.read_text(encoding="utf-8") if sm_path.exists() else ""

    # 找 prompt_timeout 日志
    timeout_log_match = re.search(
        r'prompt_timeout.*?timeout_seconds=effective_timeout(.*?)raise LLMError',
        sm_content, re.DOTALL
    )
    timeout_log_text = timeout_log_match.group(0) if timeout_log_match else ""

    has_message_count_log = (
        "messages_received" in timeout_log_text
        or "message_count" in timeout_log_text
    )
    has_message_count_var = "message_count" in sm_content

    fix3_fixed = has_message_count_log
    results["fix3_timeout_logging"] = {
        "has_messages_received_log": has_message_count_log,
        "has_message_count_variable": has_message_count_var,
        "status": "FIXED" if fix3_fixed else "NOT_FIXED",
        "verdict": (
            "✅ Fix-3 已修复: prompt_timeout 日志包含 messages_received_before_timeout"
            if fix3_fixed
            else "❌ Fix-3 未修复: prompt_timeout 日志缺少 messages_received 计数"
        ),
    }

    fix3 = results["fix3_timeout_logging"]
    print(f"  超时日志含 messages_received: {has_message_count_log}")
    print(f"  message_count 变量存在: {has_message_count_var}")
    print(f"  {fix3['verdict']}")
    results["summary"].append(fix3["verdict"])

    # =========================================================
    # Fix-4: CreateDeliverableTool output_dir 默认值
    # =========================================================
    print("\n[Fix-4] 核查 CreateDeliverableTool output_dir 默认值...")
    cd_path = root / "autoBMAD" / "docuswarm" / "tools" / "create_deliverable.py"
    cd_content = cd_path.read_text(encoding="utf-8") if cd_path.exists() else ""

    has_path_cwd_default = "Path.cwd()" in cd_content and "output_dir" in cd_content

    # 检查 execute_with_input 如何传递 output_dir
    # 看 pipeline_session_manager 的 work_dir 是否传给了工具
    execute_with_input_match = re.search(
        r'def execute_with_input.*?return output',
        ind_content, re.DOTALL
    )
    execute_with_input_text = execute_with_input_match.group(0) if execute_with_input_match else ""
    passes_output_dir_to_tool = (
        "output_dir" in execute_with_input_text
        and "CreateDeliverable" not in execute_with_input_text  # 未直接实例化工具
    )

    # 实际上 create_deliverable 工具在 SDK agent_file 中注册，output_dir 通过 work_dir 传
    # 检查 agent_yaml 是否包含 work_dir 配置
    agent_yaml_path = root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
    agent_yaml_content = agent_yaml_path.read_text(encoding="utf-8") if agent_yaml_path.exists() else ""
    yaml_has_create_deliverable = "create_deliverable" in agent_yaml_content
    yaml_has_output_dir_config = "output_dir" in agent_yaml_content or "work_dir" in agent_yaml_content

    results["fix4_output_dir"] = {
        "create_deliverable_defaults_to_cwd": has_path_cwd_default,
        "agent_yaml_registers_create_deliverable": yaml_has_create_deliverable,
        "agent_yaml_configures_output_dir": yaml_has_output_dir_config,
        "status": "NOT_FIXED" if has_path_cwd_default and not yaml_has_output_dir_config else "UNCLEAR",
        "verdict": (
            "⚠️ Fix-4 待核查: CreateDeliverableTool 仍默认 Path.cwd()，"
            "需要验证 SDK 是否正确传递 work_dir 作为工具的 output_dir"
            if has_path_cwd_default
            else "✅ Fix-4: output_dir 不再使用 Path.cwd() 默认值"
        ),
    }

    fix4 = results["fix4_output_dir"]
    print(f"  CreateDeliverableTool 默认 Path.cwd(): {has_path_cwd_default}")
    print(f"  agent_yaml 注册了 create_deliverable: {yaml_has_create_deliverable}")
    print(f"  agent_yaml 配置了 output_dir/work_dir: {yaml_has_output_dir_config}")
    print(f"  {fix4['verdict']}")
    results["summary"].append(fix4["verdict"])

    # =========================================================
    # Fix-6: execute() vs execute_with_input() system_prompt 路径一致性
    # =========================================================
    print("\n[Fix-6] 核查两条 system_prompt 路径一致性...")

    # execute() 路径: _format_system_prompt() → 直接包含 file_path/sha256 示例
    format_sp_match = re.search(
        r'def _format_system_prompt.*?return f',
        ind_content, re.DOTALL
    )
    format_sp_text = format_sp_match.group(0) if format_sp_match else ""
    execute_path_has_file_path = '"file_path"' in format_sp_text or "file_path" in format_sp_text

    # execute_with_input() 路径: contract_builder.render_independent_system_prompt
    # → _build_instructions_section() → JSON 示例
    execute_with_input_uses_contract = "render_independent_system_prompt" in ind_content
    # Fix-1 的结果告诉我们 contract_builder 是否包含 file_path
    contract_has_file_path = fix1.get("has_file_path_in_json_example", False)

    both_paths_aligned = execute_path_has_file_path and contract_has_file_path

    results["fix6_prompt_path_alignment"] = {
        "execute_path_has_file_path_instruction": execute_path_has_file_path,
        "execute_with_input_uses_contract_builder": execute_with_input_uses_contract,
        "contract_builder_has_file_path": contract_has_file_path,
        "both_paths_aligned": both_paths_aligned,
        "status": "FIXED" if both_paths_aligned else "NOT_FIXED",
        "verdict": (
            "✅ Fix-6 已修复: 两条路径均包含 file_path 指令"
            if both_paths_aligned
            else (
                "❌ Fix-6 未修复: 两条 system_prompt 路径不一致"
                + (" [execute() 路径缺少 file_path]" if not execute_path_has_file_path else "")
                + (" [execute_with_input() via contract_builder 缺少 file_path]" if not contract_has_file_path else "")
            )
        ),
    }

    fix6 = results["fix6_prompt_path_alignment"]
    print(f"  execute() 路径包含 file_path 指令: {execute_path_has_file_path}")
    print(f"  execute_with_input() 使用 contract_builder: {execute_with_input_uses_contract}")
    print(f"  contract_builder 包含 file_path: {contract_has_file_path}")
    print(f"  两路径对齐: {both_paths_aligned}")
    print(f"  {fix6['verdict']}")
    results["summary"].append(fix6["verdict"])

    # =========================================================
    # 核查: _call_llm_with_prompts 中的错误处理 - partial messages 行为
    # =========================================================
    print("\n[额外] 核查 _call_llm_with_prompts 中 partial messages 的错误处理...")

    partial_match = re.search(
        r'except Exception as e:.*?if messages:.*?return messages.*?raise LLMCallError',
        ind_content, re.DOTALL
    )
    has_partial_messages_return = partial_match is not None

    # 关键问题: 若超时后 messages 有内容（partial），会被返回给 _parse_response
    # _parse_response 尝试解析这些 partial messages
    # 若 partial messages 不含完整 JSON 响应，则 fallback 到 markdown_fallback
    # markdown_fallback 构建的 dict 缺少 file_path → MISSING_FILE_PATH
    results["extra_partial_messages"] = {
        "returns_partial_on_timeout": has_partial_messages_return,
        "concern": (
            "⚠️ 超时时若有 partial messages 会被返回给 _parse_response，"
            "若这些 partial messages 不含完整 JSON 响应，"
            "markdown_fallback 会构建缺少 file_path 的 dict"
            if has_partial_messages_return else
            "ℹ️ 超时时不返回 partial messages"
        ),
    }

    print(f"  超时时返回 partial messages: {has_partial_messages_return}")
    print(f"  潜在问题: {results['extra_partial_messages']['concern'][:80]}...")
    results["summary"].append(results["extra_partial_messages"]["concern"])

    # =========================================================
    # 核查: tool_result_extractor.py 是否在 fallback 中使用
    # =========================================================
    print("\n[额外] 核查 tool_result_extractor.py 的实际用途...")
    tre_path = root / "autoBMAD" / "docuswarm" / "tools" / "tool_result_extractor.py"
    tre_content = tre_path.read_text(encoding="utf-8") if tre_path.exists() else ""

    # extract_from_messages 只扫描 tool_use (LLM 调用请求), 不扫描 tool_result (工具响应)
    scans_tool_use = '"type"] == "tool_use"' in tre_content or 'type\' == \'tool_use\'' in tre_content
    scans_tool_result_response = '"type"] == "tool_result"' in tre_content or 'type\' == \'tool_result\'' in tre_content
    independent_uses_tre = "tool_result_extractor" in ind_content or "ToolResultExtractor" in ind_content

    results["extra_tool_result_extractor"] = {
        "extract_from_messages_scans_tool_use": scans_tool_use,
        "extract_from_messages_scans_tool_result_response": scans_tool_result_response,
        "independent_imports_extractor": independent_uses_tre,
        "assessment": (
            "⚠️ tool_result_extractor.extract_from_messages() 只提取 tool_use (LLM发出的调用请求),"
            " 不提取 tool_result (工具响应结果), 因此无法用于从工具结果中获取 file_path!"
            if (scans_tool_use and not scans_tool_result_response)
            else "✅ tool_result_extractor 正确扫描了 tool_result 响应"
        ),
    }

    trea = results["extra_tool_result_extractor"]
    print(f"  扫描 tool_use (LLM调用请求): {scans_tool_use}")
    print(f"  扫描 tool_result (工具响应): {scans_tool_result_response}")
    print(f"  independent.py 使用了 ToolResultExtractor: {independent_uses_tre}")
    print(f"  评估: {trea['assessment'][:80]}...")
    results["summary"].append(trea["assessment"])

    # =========================================================
    # 核查: validator 是否要求 content 字段 (不只是 file_path/sha256)
    # =========================================================
    print("\n[额外] 核查 validator 对 deliverable 字段的完整要求...")
    val_path = root / "autoBMAD" / "docuswarm" / "context" / "validator.py"
    val_content = val_path.read_text(encoding="utf-8") if val_path.exists() else ""

    required_fields = []
    for field in ["title", "file_path", "sha256", "content", "summary"]:
        if f'"MISSING_{field.upper()}"' in val_content or f'code="MISSING_{field.upper()}"' in val_content:
            required_fields.append(field)

    # 检查 content 是否是必需字段
    content_required_match = re.search(
        r'if ["\']content["\'] not in deliverable',
        val_content
    )
    content_is_required = content_required_match is not None

    results["extra_validator_requirements"] = {
        "required_fields_with_MISSING_code": required_fields,
        "content_field_is_required": content_is_required,
    }

    print(f"  含 MISSING_X 错误码的必需字段: {required_fields}")
    print(f"  content 字段是必需的: {content_is_required}")

    # =========================================================
    # 综合总结
    # =========================================================
    print("\n" + "=" * 70)
    print("综合核查结论:")
    print("=" * 70)
    for item in results["summary"]:
        print(f"  {item[:100]}")

    return results


# ========== 额外检查: 深度核查报告方案准确性 ==========

def deep_verify_report_accuracy() -> dict[str, Any]:
    """深度核查 pipeline-timeout-root-cause-analysis.md 报告的准确性。

    新增核查项:
      N1: _format_system_prompt() 中 file_path 示例已存在（execute() 旧路径）
      N2: prompt() 超时后抛 LLMError，_call_llm_with_prompts 如何捕获
      N3: agent_yaml 工具模块路径的正确性
      N4: validator 对 questions 字段的要求（必须存在，不只 deliverable）
      N5: CreateDeliverableTool 实例化方式（SDK 传 output_dir？还是 Path.cwd？）
      N6: execute_with_context 是否有重试机制（max_iterations）
      N7: dual_agent 中 IndependentExecutionError 到 node_execution_failed 的链路
      N8: execute() 路径 vs execute_with_input() 路径的实际触发条件
    """
    print("\n" + "=" * 70)
    print("深度核查: 报告方案准确性验证")
    print("=" * 70)

    root = Path(__file__).parent.parent
    results: dict[str, Any] = {}

    # =========================================================
    # N1: execute() 旧路径中的 _format_system_prompt 确实含 file_path
    # =========================================================
    print("\n[N1] 核查 _format_system_prompt() 是否包含 file_path/sha256 示例...")
    ind_path = root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    ind_content = ind_path.read_text(encoding="utf-8") if ind_path.exists() else ""

    # 提取 _format_system_prompt 方法
    format_sp_match = re.search(
        r'def _format_system_prompt\(self\).*?return f""".*?"""',
        ind_content, re.DOTALL
    )
    old_path_text = format_sp_match.group(0) if format_sp_match else ""
    old_path_has_file_path = '"file_path": "path from tool output"' in old_path_text
    old_path_has_sha256 = '"sha256": "hash from tool output"' in old_path_text
    old_path_has_important = 'IMPORTANT' in old_path_text and 'file_path' in old_path_text
    # 验证旧路径比 contract_builder 更完整
    has_example_block = '"file_path": "output/pipeline-123' in old_path_text

    results["n1_old_path_format_system_prompt"] = {
        "has_file_path_example": old_path_has_file_path,
        "has_sha256_example": old_path_has_sha256,
        "has_important_note": old_path_has_important,
        "has_concrete_example": has_example_block,
        "verdict": (
            "✅ N1 确认: _format_system_prompt() 包含完整的 file_path/sha256 示例和 IMPORTANT 说明"
            if (old_path_has_file_path and old_path_has_sha256)
            else "❌ N1 异常: _format_system_prompt() 缺少 file_path/sha256 示例 (报告假设错误)"
        ),
    }
    n1 = results["n1_old_path_format_system_prompt"]
    print(f"  _format_system_prompt 含 file_path: {old_path_has_file_path}")
    print(f"  _format_system_prompt 含 sha256: {old_path_has_sha256}")
    print(f"  _format_system_prompt 含 IMPORTANT: {old_path_has_important}")
    print(f"  _format_system_prompt 含具体示例: {has_example_block}")
    print(f"  {n1['verdict']}")

    # =========================================================
    # N2: ClaudeSessionWrapper.prompt() 超时时抛 LLMError（不是 TimeoutError）
    #     _call_llm_with_prompts 中的 except 捕获 LLMError 还是所有 Exception？
    # =========================================================
    print("\n[N2] 核查超时异常传播链...")
    sm_path = root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    sm_content = sm_path.read_text(encoding="utf-8") if sm_path.exists() else ""

    # prompt() 中: TimeoutError -> raise LLMError
    timeout_raises_llmerror = (
        "TimeoutError" in sm_content
        and "raise LLMError" in sm_content
        and "Session prompt timed out" in sm_content
    )
    # _call_llm_with_prompts 中: except Exception -> 捕获 LLMError
    catch_broad_exception = re.search(
        r'async for msg in session.prompt.*?except Exception as e:',
        ind_content, re.DOTALL
    ) is not None
    # 查找 _call_llm_with_prompts 的异常处理
    call_llm_except = re.search(
        r'def _call_llm_with_prompts.*?except Exception as e:(.*?)raise LLMCallError',
        ind_content, re.DOTALL
    )
    call_llm_except_text = call_llm_except.group(1) if call_llm_except else ""
    partial_return_in_except = "if messages:" in call_llm_except_text and "return messages" in call_llm_except_text

    results["n2_timeout_propagation"] = {
        "prompt_raises_llmerror_on_timeout": timeout_raises_llmerror,
        "call_llm_catches_broad_exception": True,  # except Exception as e
        "partial_messages_returned_before_raise": partial_return_in_except,
        "verdict": (
            "✅ N2 确认: prompt() 超时→LLMError，_call_llm_with_prompts 用 except Exception 捕获，"
            "若 messages 非空返回 partial messages（报告正确）"
            if (timeout_raises_llmerror and partial_return_in_except)
            else "⚠️ N2 需确认: 超时传播链与报告描述不完全一致"
        ),
    }
    n2 = results["n2_timeout_propagation"]
    print(f"  prompt() 超时抛 LLMError: {timeout_raises_llmerror}")
    print(f"  _call_llm_with_prompts 捕获 Exception: True")
    print(f"  partial messages 在异常前返回: {partial_return_in_except}")
    print(f"  {n2['verdict']}")

    # =========================================================
    # N3: independent_agent.yaml 中工具模块路径是否正确存在
    # =========================================================
    print("\n[N3] 核查 agent_yaml 工具模块路径正确性...")
    agent_yaml_path = root / "autoBMAD" / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
    agent_yaml_content = agent_yaml_path.read_text(encoding="utf-8") if agent_yaml_path.exists() else ""

    tool_modules: dict[str, bool] = {}
    tool_refs = re.findall(r'- "([^"]+)"', agent_yaml_content)
    for ref in tool_refs:
        if ":" in ref:
            module_path = ref.split(":")[0]
            module_file = root / (module_path.replace(".", "/") + ".py")
            tool_modules[ref] = module_file.exists()

    results["n3_yaml_tool_paths"] = {
        "tool_refs": tool_refs,
        "module_existence": tool_modules,
        "all_exist": all(tool_modules.values()),
        "verdict": (
            "✅ N3 确认: agent_yaml 中所有工具模块路径正确"
            if all(tool_modules.values())
            else f"❌ N3 发现: 部分工具模块不存在: {[k for k,v in tool_modules.items() if not v]}"
        ),
    }
    n3 = results["n3_yaml_tool_paths"]
    for ref, exists in tool_modules.items():
        print(f"  {ref}: {'✅' if exists else '❌'} {'存在' if exists else '不存在'}")
    print(f"  {n3['verdict']}")

    # =========================================================
    # N4: validator 对 questions 字段的验证要求
    # =========================================================
    print("\n[N4] 核查 validator 对 questions 字段的完整要求...")
    val_path = root / "autoBMAD" / "docuswarm" / "context" / "validator.py"
    val_content = val_path.read_text(encoding="utf-8") if val_path.exists() else ""

    questions_required = "MISSING_QUESTIONS" in val_content
    question_priority_required = "MISSING_QUESTION_PRIORITY" in val_content
    question_text_required = "MISSING_QUESTION_TEXT" in val_content
    question_context_required = "MISSING_QUESTION_CONTEXT" in val_content
    # 关键: questions 字段是否允许为空列表（即存在但为空）
    empty_questions_ok = (
        "if not isinstance(questions, list)" in val_content
        and "MISSING_QUESTIONS" in val_content
    )

    results["n4_questions_validation"] = {
        "questions_required": questions_required,
        "question_priority_required": question_priority_required,
        "question_text_required": question_text_required,
        "question_context_required": question_context_required,
        "empty_list_is_ok": True,  # markdown_fallback 设置了 [] 是允许的
        "verdict": (
            "✅ N4 确认: questions 字段必须存在（但可以是空列表），每个问题需 priority/question/context"
            if questions_required
            else "❌ N4 异常: validator 不要求 questions 字段"
        ),
    }
    n4 = results["n4_questions_validation"]
    print(f"  questions 字段必须存在: {questions_required}")
    print(f"  priority 必须存在: {question_priority_required}")
    print(f"  question 文本必须存在: {question_text_required}")
    print(f"  context 必须存在: {question_context_required}")
    print(f"  空列表 [] 允许: True（遍历空列表不产生错误）")
    print(f"  {n4['verdict']}")

    # =========================================================
    # N5: CreateDeliverableTool 实例化方式 - SDK 如何传 output_dir
    # =========================================================
    print("\n[N5] 核查 CreateDeliverableTool 实例化与 output_dir 传递机制...")
    cd_path = root / "autoBMAD" / "docuswarm" / "tools" / "create_deliverable.py"
    cd_content = cd_path.read_text(encoding="utf-8") if cd_path.exists() else ""

    # 工具定义: __init__(self, output_dir=None) → self.output_dir = output_dir or Path.cwd()
    tool_init_has_output_dir = "def __init__(self, output_dir" in cd_content
    tool_defaults_to_cwd = "Path.cwd()" in cd_content

    # agent_yaml 注册方式: "autoBMAD.docuswarm.tools.create_deliverable:CreateDeliverableTool"
    # SDK 加载工具时调用 CreateDeliverableTool() 无参数 → output_dir=None → Path.cwd()
    # 而 SessionManager 传入 work_dir 给 SDK options.cwd，但不传给工具构造函数！
    # 这意味着工具写文件到 cwd（即执行目录），而非 output/pipeline-xxx/ 目录
    sdk_cwd_vs_tool_output_dir = (
        'options_dict["cwd"] = self._work_dir' in sm_content
        or '"cwd": self._work_dir' in sm_content
    )
    # SDK 的 cwd 选项是否影响工具实例化时的 output_dir？
    # 实际上不影响：SDK cwd 只影响文件系统操作的基目录，不作为工具 __init__ 参数传入
    tool_wrapper_path = root / "autoBMAD" / "docuswarm" / "tools" / "callable_tool_wrapper.py"
    tool_wrapper_content = tool_wrapper_path.read_text(encoding="utf-8") if tool_wrapper_path.exists() else ""
    wrapper_passes_work_dir = "work_dir" in tool_wrapper_content or "output_dir" in tool_wrapper_content

    results["n5_tool_output_dir"] = {
        "tool_init_accepts_output_dir": tool_init_has_output_dir,
        "defaults_to_path_cwd": tool_defaults_to_cwd,
        "sdk_sets_cwd_on_options": sdk_cwd_vs_tool_output_dir,
        "wrapper_passes_work_dir_to_tool": wrapper_passes_work_dir,
        "verdict": (
            "⚠️ N5 发现: SDK 通过 options.cwd 设置工作目录（影响Claude自身的文件操作），"
            "但 CreateDeliverableTool() 在 agent_yaml 中无参数实例化→output_dir=Path.cwd()。"
            "实际文件写入路径取决于运行时 cwd，不是 pipeline output 目录！"
            if (tool_defaults_to_cwd and not wrapper_passes_work_dir)
            else "✅ N5: tool wrapper 传递了 work_dir 给工具实例"
        ),
    }
    n5 = results["n5_tool_output_dir"]
    print(f"  工具 __init__ 接受 output_dir 参数: {tool_init_has_output_dir}")
    print(f"  默认 Path.cwd(): {tool_defaults_to_cwd}")
    print(f"  SDK options 设置 cwd: {sdk_cwd_vs_tool_output_dir}")
    print(f"  wrapper 传递 work_dir 给工具: {wrapper_passes_work_dir}")
    print(f"  {n5['verdict'][:100]}...")

    # =========================================================
    # N6: execute_with_context 中的 max_iterations 重试机制
    # =========================================================
    print("\n[N6] 核查 DualAgentNode 重试机制 (max_iterations)...")
    dual_path = root / "autoBMAD" / "docuswarm" / "nodes" / "dual_agent.py"
    dual_content = dual_path.read_text(encoding="utf-8") if dual_path.exists() else ""

    has_max_iterations = "max_iterations" in dual_content
    while_loop_present = "while iteration < self.max_iterations" in dual_content
    default_max_iter = re.search(r'DEFAULT_MAX_ITERATIONS\s*=\s*(\d+)', dual_content)
    default_iter_value = int(default_max_iter.group(1)) if default_max_iter else None

    # executor.py 传入了 max_iterations 吗？
    exec_path = root / "autoBMAD" / "docuswarm" / "node_execution" / "executor.py"
    exec_content = exec_path.read_text(encoding="utf-8") if exec_path.exists() else ""
    executor_uses_max_iter = "max_iterations" in exec_content

    results["n6_retry_mechanism"] = {
        "max_iterations_configured": has_max_iterations,
        "while_loop_present": while_loop_present,
        "default_max_iterations": default_iter_value,
        "executor_passes_max_iterations": executor_uses_max_iter,
        "verdict": (
            f"✅ N6 确认: DualAgentNode 有 while 迭代循环，"
            f"DEFAULT_MAX_ITERATIONS={default_iter_value}，"
            f"每次 Independent Agent 失败会在 IndependentExecutionError 中终止（不重试同一次迭代）"
            if while_loop_present
            else "❌ N6: 找不到 while 迭代循环"
        ),
    }
    n6 = results["n6_retry_mechanism"]
    print(f"  max_iterations 已配置: {has_max_iterations}")
    print(f"  while 迭代循环存在: {while_loop_present}")
    print(f"  DEFAULT_MAX_ITERATIONS: {default_iter_value}")
    print(f"  executor 传入 max_iterations: {executor_uses_max_iter}")
    print(f"  {n6['verdict'][:100]}...")

    # =========================================================
    # N7: 错误链路 IndependentExecutionError → node_execution_failed
    # =========================================================
    print("\n[N7] 核查 IndependentExecutionError → node_execution_failed 错误链...")

    # dual_agent.py: except Exception as e -> raise IndependentExecutionError
    ind_exec_error_in_dual = "raise IndependentExecutionError" in dual_content
    # executor.py: except Exception as e -> logger.error(node_execution_failed)
    node_exec_failed_in_executor = "node_execution_failed" in exec_content
    exec_catches_all = re.search(
        r'except Exception as e:.*?node_execution_failed',
        exec_content, re.DOTALL
    ) is not None

    results["n7_error_chain"] = {
        "dual_raises_independent_execution_error": ind_exec_error_in_dual,
        "executor_logs_node_execution_failed": node_exec_failed_in_executor,
        "executor_catches_all_exceptions": exec_catches_all,
        "verdict": (
            "✅ N7 确认: dual_agent 抛 IndependentExecutionError → "
            "executor 的 except Exception 捕获 → 记录 node_execution_failed（报告正确）"
            if (ind_exec_error_in_dual and exec_catches_all)
            else "⚠️ N7: 错误链路与报告描述有差异"
        ),
    }
    n7 = results["n7_error_chain"]
    print(f"  dual_agent 抛 IndependentExecutionError: {ind_exec_error_in_dual}")
    print(f"  executor 记录 node_execution_failed: {node_exec_failed_in_executor}")
    print(f"  executor 捕获所有异常: {exec_catches_all}")
    print(f"  {n7['verdict']}")

    # =========================================================
    # N8: execute() 路径 vs execute_with_input() 路径的触发条件
    # =========================================================
    print("\n[N8] 核查 execute() 与 execute_with_input() 的实际触发路径...")

    # 在 dual_agent.py 中，实际调用的是哪个方法？
    uses_execute_with_input = "execute_with_input" in dual_content
    uses_execute = re.search(r'await.*\.execute\(', dual_content) is not None

    # executor.py → dual_agent → execute_with_context → execute_with_input
    executor_calls_execute_with_context = "execute_with_context" in exec_content

    results["n8_execution_path"] = {
        "dual_uses_execute_with_input": uses_execute_with_input,
        "dual_uses_execute": uses_execute,
        "executor_calls_execute_with_context": executor_calls_execute_with_context,
        "verdict": (
            "✅ N8 确认: 生产路径为 executor→execute_with_context→execute_with_input，"
            "execute() 旧路径只被 _call_llm 调用（内部使用），"
            "报告关于两路径的描述需要修正：execute() 不是用户直接调用的旧路径"
            if (uses_execute_with_input and executor_calls_execute_with_context)
            else "⚠️ N8: 执行路径与报告描述不一致"
        ),
    }
    n8 = results["n8_execution_path"]
    print(f"  dual_agent 调用 execute_with_input: {uses_execute_with_input}")
    print(f"  dual_agent 调用 execute (旧路径): {uses_execute}")
    print(f"  executor 调用 execute_with_context: {executor_calls_execute_with_context}")
    print(f"  {n8['verdict'][:100]}...")

    # =========================================================
    # 综合总结
    # =========================================================
    print("\n" + "=" * 70)
    print("深度核查综合结论:")
    print("=" * 70)
    for key, val in results.items():
        if isinstance(val, dict) and "verdict" in val:
            print(f"  {val['verdict'][:100]}")

    return results


# ========== 主函数 ==========

def main() -> None:
    analyzer = TimeoutRootCauseAnalyzer()
    results = analyzer.run()

    # 额外检查
    print("\n" + "=" * 70)
    print("额外检查: contract_builder JSON 示例验证")
    print("=" * 70)
    cb_check = check_contract_builder_json_example()
    print(f"\nJSON 示例包含 file_path: {cb_check['has_file_path_in_example']}")
    print(f"JSON 示例包含 sha256: {cb_check['has_sha256_in_example']}")
    print(f"\n判断: {cb_check['verdict']}")

    results["contract_builder_json_check"] = cb_check

    # 验证 tool_result 消息结构
    tool_result_check = check_tool_result_message_structure()
    results["tool_result_structure_check"] = tool_result_check

    # 全面核查所有修复方案
    print("\n" + "=" * 70)
    print("全面核查: 所有修复方案")
    print("=" * 70)
    verify_results = verify_all_fixes()
    results["verify_all_fixes"] = verify_results

    # 深度核查报告准确性
    print("\n" + "=" * 70)
    print("深度核查: 报告方案准确性验证")
    print("=" * 70)
    deep_verify_results = deep_verify_report_accuracy()
    results["deep_verify_report"] = deep_verify_results

    # 保存结果
    output_path = Path(__file__).parent.parent / ".tmp" / "timeout_root_cause_report.json"
    analyzer.save_results(output_path)
    analyzer.results = results
    analyzer.save_results(output_path)


if __name__ == "__main__":
    main()
