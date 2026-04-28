from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "docs"
    / "research"
    / "2026-03-17-docuswarm-decision-research-report.md"
)


@dataclass
class Evidence:
    path: str
    line: int
    snippet: str


class DocuSwarmDecisionResearcher:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self._cache: dict[Path, list[str]] = {}

    def _read_lines(self, path: Path) -> list[str]:
        if path not in self._cache:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="replace")
            self._cache[path] = text.splitlines()
        return self._cache[path]

    def _find(self, rel_path: str, patterns: list[str]) -> list[Evidence]:
        path = self.project_root / rel_path
        if not path.exists():
            return []

        evidences: list[Evidence] = []
        for idx, line in enumerate(self._read_lines(path), start=1):
            for pattern in patterns:
                if pattern in line:
                    evidences.append(
                        Evidence(
                            path=rel_path.replace("\\", "/"),
                            line=idx,
                            snippet=line.strip(),
                        )
                    )
                    break
        return evidences

    def _count_test_files(self) -> int:
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            return 0
        return sum(1 for path in tests_dir.rglob("*") if path.is_file())

    def _db_snapshot(self) -> dict[str, Any]:
        db_path = self.project_root / "docuswarm.db"
        snapshot: dict[str, Any] = {
            "db_path": str(db_path),
            "db_exists": db_path.exists(),
        }
        if not db_path.exists():
            return snapshot

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            tables = [
                row["name"]
                for row in cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()
            ]
            snapshot["tables"] = tables
            snapshot["pipeline_count"] = (
                cursor.execute("SELECT COUNT(*) AS cnt FROM pipelines").fetchone()["cnt"]
                if "pipelines" in tables
                else 0
            )
            snapshot["checkpoint_count"] = (
                cursor.execute("SELECT COUNT(*) AS cnt FROM checkpoints").fetchone()["cnt"]
                if "checkpoints" in tables
                else 0
            )

            if "pipelines" in tables:
                row = cursor.execute(
                    "SELECT pipeline_id, state_json FROM pipelines ORDER BY updated_at DESC, rowid DESC LIMIT 1"
                ).fetchone()
                if row is not None:
                    try:
                        state = json.loads(row["state_json"]) if row["state_json"] else {}
                    except Exception as exc:
                        state = {"__parse_error__": str(exc)}
                    snapshot["latest_pipeline"] = {
                        "pipeline_id": row["pipeline_id"],
                        "state_type": type(state).__name__,
                        "state_keys": list(state.keys()) if isinstance(state, dict) else [],
                    }

            if "checkpoints" in tables:
                row = cursor.execute(
                    "SELECT thread_id, checkpoint FROM checkpoints ORDER BY rowid DESC LIMIT 1"
                ).fetchone()
                if row is not None:
                    decoded_keys: list[str] = []
                    channel_value_keys: list[str] = []
                    try:
                        import msgpack  # type: ignore

                        decoded = msgpack.unpackb(row["checkpoint"])
                        decoded_keys = self._normalize_keys(decoded)
                        channel_values = decoded.get(b"channel_values") or decoded.get(
                            "channel_values", {}
                        )
                        channel_value_keys = self._normalize_keys(channel_values)
                    except Exception as exc:
                        decoded_keys = [f"<checkpoint decode failed: {exc}>"]

                    snapshot["latest_checkpoint"] = {
                        "thread_id": row["thread_id"],
                        "top_level_keys": decoded_keys,
                        "channel_value_keys": channel_value_keys,
                    }
        finally:
            conn.close()

        return snapshot

    @staticmethod
    def _normalize_keys(value: Any) -> list[str]:
        if not isinstance(value, dict):
            return []
        keys: list[str] = []
        for key in value.keys():
            if isinstance(key, bytes):
                keys.append(key.decode("utf-8", errors="replace"))
            else:
                keys.append(str(key))
        return keys

    def collect(self) -> dict[str, Any]:
        db_snapshot = self._db_snapshot()
        test_file_count = self._count_test_files()

        findings = {
            "F1": self._analyze_f1(db_snapshot),
            "F2": self._analyze_f2(),
            "F3": self._analyze_f3(),
            "F4": self._analyze_f4(),
            "F5": self._analyze_f5(),
            "F6": self._analyze_f6(test_file_count),
            "F7": self._analyze_f7(),
            "F8": self._analyze_f8(),
        }

        return {
            "title": "2026-03-17 DocuSwarm F1-F8 深度决策研究报告",
            "scope": "围绕用户锁定的 F1-F8 决策，对 autoBMAD/docuswarm 的状态、上下文、工具、测试、类型与文档进行再次研究。",
            "user_locked_decisions": [
                "F1: 用奥卡姆剃刀比较 state_json 与 LangGraph checkpoint，并产出单一业务真相源判断。",
                "F2: 认可 shared_context 闭环修复方向。",
                "F3: 认可 Evaluator 输入契约闭环修复方向。",
                "F4: 选择 docs-free，只保留 create_deliverable / create_document_set / update_context；工具注册 API 必须收敛成一种用法。",
                "F5: 比较 dataclass 风格与 METADATA: JSON 兼容风格，明确拒绝 kimi SDK ToolOk/ToolError 作为系统主契约。",
                "F6: 不再把历史红灯直接当作当前回归质量门；当前研究只基于现工作区快照。",
                "F7: 认可类型系统、导出面、惰性导入收敛方向。",
                "F8: 认可文档收敛与去漂移方向。",
            ],
            "runtime_snapshot": {
                "database": db_snapshot,
                "visible_test_file_count": test_file_count,
            },
            "findings": findings,
            "final_architecture_decisions": [
                "业务真相源收敛到 state_json；checkpoint 降级为运行期恢复快照。",
                "shared_context 必须贯穿写入、提示词消费、恢复继续执行三段链路。",
                "Evaluator 直接围绕 EvaluatorAgentInput 生成 prompt，不再重建丢字段的临时上下文。",
                "工具面坚持 docs-free，仅保留三个工具，并只保留一种注册 API。",
                "系统内部工具返回协议收敛到结构化 ToolResult/dataclass；METADATA: JSON 仅保留在边界兼容层。",
                "拒绝把 kimi SDK ToolOk/ToolError 继续扩散成内部事实格式。",
                "测试门禁改为服务当前架构，而不是兼容历史双轨假设。",
                "显式清理 __all__、重导出和大面积 __getattr__ 惰性导入造成的类型腐蚀。",
            ],
            "execution_order": [
                "先补齐 state_json 与 shared_context / evaluator 契约闭环，再动工具契约与注册 API。",
                "随后统一 ToolResult 协议并删除旧测试/旧注册残留。",
                "最后做类型、导出面、文档三类工程化清理，让新测试体系稳定落地。",
            ],
        }

    def _analyze_f1(self, db_snapshot: dict[str, Any]) -> dict[str, Any]:
        evidence = [
            *self._find(
                "autoBMAD/docuswarm/storage/state_manager.py",
                [
                    "state_json = json.dumps(subject_context or {})",
                    '"state": json.loads(cast(str, row["state_json"])) if row["state_json"] else {},',
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/pipeline/state.py",
                [
                    "class PipelineState(TypedDict):",
                    "shared_context: dict[str, Any]",
                    "def create_initial_state(",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/pipeline/orchestrator.py",
                [
                    'checkpoint_state = pipeline.get("state", {})',
                    'initial_state["completed_nodes"] = checkpoint_state.get("completed_nodes", [])',
                    'initial_state["deliverables"] = checkpoint_state.get("deliverables", {})',
                    'initial_state["session_ids"] = checkpoint_state.get("session_ids", {})',
                ],
            ),
        ]

        decision_matrix = [
            {
                "option": "state_json",
                "business_truth": "高，字段由项目自己定义，可直接映射业务状态。",
                "stability": "高，只要保持 PipelineState schema 稳定即可。",
                "operability": "高，易查库、易审计、易做 status/resume/restart 运维界面。",
                "coupling": "低，和 LangGraph 内部实现解耦。",
                "current_gap": "当前只落了 subject_context，不是完整 PipelineState。",
            },
            {
                "option": "LangGraph checkpoint",
                "business_truth": "中，能反映运行时快照，但语义偏框架内部。",
                "stability": "中低，受 LangGraph 序列化格式和 channel 结构约束。",
                "operability": "低，BLOB/msgpack 难以直接作为业务审计真相。",
                "coupling": "高，直接耦合框架恢复机制。",
                "current_gap": "当前最完整，但它完整的是“框架恢复态”，不是“业务真相源”。",
            },
        ]

        latest_pipeline = db_snapshot.get("latest_pipeline", {})
        latest_checkpoint = db_snapshot.get("latest_checkpoint", {})

        return {
            "title": "状态持久化与恢复链路没有闭环",
            "severity": "P0",
            "decision": "以奥卡姆剃刀判断，state_json 应成为唯一业务真相源，LangGraph checkpoint 只保留为运行期恢复快照。",
            "why": [
                "固定五节点顺序流水线的业务语义，明显比 LangGraph 内部 channel 语义更简单，应该让更简单的业务模型成为真相源。",
                "如果同时把 checkpoint 和 state_json 都视为完整真相，就需要长期维护双重一致性，复杂度会持续外溢到 resume、status、restart、debug 和测试。",
                "数据库样本已证明 checkpoint 比 state_json 更完整，但这恰恰说明当前真正的问题是 state_json 没有写满，而不是应该把真相源交给 checkpoint。",
            ],
            "database_snapshot": {
                "latest_pipeline_state_keys": latest_pipeline.get("state_keys", []),
                "latest_checkpoint_channel_keys": latest_checkpoint.get("channel_value_keys", []),
            },
            "decision_matrix": decision_matrix,
            "required_changes": [
                "create_pipeline / 运行中状态更新统一写入完整 PipelineState 到 state_json。",
                "resume/status/restart 的业务判断统一读取 state_json，而非默认读取 checkpoint_state。",
                "checkpoint 丢失时，系统仍应能依据 state_json 从 current_node 重新执行，而不是丢失恢复能力。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def _analyze_f2(self) -> dict[str, Any]:
        evidence = [
            *self._find(
                "autoBMAD/docuswarm/storage/state_manager.py",
                [
                    'if "shared_context" not in current_state:',
                    'current_state["shared_context"] = {}',
                    "async def update_shared_context(",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/context/isolation.py",
                [
                    'shared_context = execution_context.get("shared_context", {})',
                    "shared_context=shared_context,  # P1-1: Pass shared_context",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/agents/independent.py",
                [
                    "shared_context={},",
                ],
            ),
        ]

        return {
            "title": "shared_context 只完成了“能写”，没有完成“能持续参与执行”",
            "severity": "P0/P1",
            "decision": "同意原建议，shared_context 必须从持久化入口延续到真实执行上下文和恢复链路。",
            "why": [
                "StateManager 已能写 shared_context，ContextManager 也会把 shared_context 放入 IndependentAgentInput。",
                "但 IndependentAgent.execute_with_input() 又重建了 shared_context={} 的 NodeExecutionContext，导致共享上下文在真正构建 prompt 之前丢失。",
                "这使 update_context 成为“表面能力”，系统无法稳定让共享知识持续参与下游节点执行。",
            ],
            "required_changes": [
                "停止在 Agent 层重新构造缺字段上下文；直接消费 ContextManager 传入的结构化输入。",
                "补一条端到端测试：update_context -> 下一节点 prompt 可见 -> resume 后仍可见。",
                "把 shared_context 纳入 state_json 完整 schema，而不是作为临时附加字段。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def _analyze_f3(self) -> dict[str, Any]:
        evidence = [
            *self._find(
                "autoBMAD/docuswarm/context/isolation.py",
                [
                    'file_path = deliverable.get("file_path")',
                    'deliverable_body = path.read_text(encoding="utf-8")',
                    "return EvaluatorAgentInput(",
                    "original_context_summary=original_summary,  # P0-2",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/agents/evaluator.py",
                [
                    "original_context={},",
                    "shared_context={},",
                    "deliverable_body=deliverable_body,",
                ],
            ),
        ]

        return {
            "title": "Evaluator 的输入契约被重新削弱，原始上下文与交付物真相并未稳定闭环",
            "severity": "P1",
            "decision": "同意原建议，Evaluator 必须直接围绕 EvaluatorAgentInput 组装 prompt，不能再重建缩水版 NodeExecutionContext。",
            "why": [
                "ContextManager.build_evaluator_input() 已经把 file_path 设为必填，并读取磁盘上的正式正文，这个方向是正确的。",
                "EvaluatorAgent.execute_with_input() 仍然把 original_context 和 shared_context 置空后再建 contract，说明输入契约在最后一步又被削弱。",
                "结果是 Evaluator 更像在评审“文档文本质量”，而不是稳定地评审“该文档是否满足原始任务与约束”。",
            ],
            "required_changes": [
                "让 Evaluator contract builder 直接吃 EvaluatorAgentInput，而不是靠临时 NodeExecutionContext 补字段。",
                "补 prompt 快照测试，断言原始上下文摘要、正式正文、评审标准三者都稳定在最终 prompt 中。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def _analyze_f4(self) -> dict[str, Any]:
        evidence = [
            *self._find(
                "autoBMAD/docuswarm/tools/__init__.py",
                [
                    "CreateDeliverableTool",
                    "CreateDocumentSetTool",
                    "UpdateContextTool",
                    "parse_deliverable_metadata",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/agents/configs/independent_agent.yaml",
                [
                    "docs-free configuration",
                    "create_deliverable",
                    "update_context",
                    "create_document_set",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/tools/tool_registry.py",
                [
                    "class ToolRegistry:",
                    "def get_tool_registry() -> ToolRegistry:",
                    "def register_tool(name: str)",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/models/tool_registry.py",
                [
                    "class ToolRegistryExtended(ToolRegistry):",
                    '__all__ = ["ToolRegistry", "ToolDefinition", "ToolResult"]',
                ],
            ),
        ]

        return {
            "title": "工具层处于产品决策未收敛状态",
            "severity": "P0/P1",
            "decision": "采用方案 A：坚持 docs-free，只保留 create_deliverable / create_document_set / update_context；工具注册 API 收敛成一种用法。",
            "why": [
                "运行期 agent 配置和 tools 包导出都已经朝 docs-free 收敛，但仍保留 parse_deliverable_metadata 这类旧兼容思维。",
                "tool_registry.py 与 models/tool_registry.py 同时存在，且一个偏全局注册器、一个偏扩展定义模型，API 语义已经分叉。",
                "继续维持双轨只会让 prompt、测试、注册、导出和文档不断互相否定。",
            ],
            "required_changes": [
                "删除 docs 工具相关残留导出、文档、旧测试假设，明确 docs-free 是唯一有效产品决策。",
                "只保留一个 ToolRegistry 入口，其他模块改为纯重定向或直接删除。",
                "不再保留两套互相矛盾的测试并存。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def _analyze_f5(self) -> dict[str, Any]:
        evidence = [
            *self._find(
                "autoBMAD/docuswarm/tools/tool_result.py",
                [
                    "class ToolResult:",
                    "success: bool",
                    "result: Any = None",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/tools/tool_result_extractor.py",
                [
                    "if isinstance(response, ToolResult):",
                    "return ToolResult.from_dict(response)",
                    "return ToolResult(success=True, result=response)",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/tools/create_deliverable.py",
                [
                    "from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue",
                    'f"METADATA: {json.dumps(metadata, ensure_ascii=False)}"',
                    "return ToolOk(output=output_text)",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/tools/create_document_set.py",
                [
                    "from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue",
                    "return ToolOk(output=result_msg)",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/tools/update_context.py",
                [
                    "from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue",
                    "async def update_context(params: UpdateContextParams) -> ToolResult:",
                    "return ToolResult(",
                ],
            ),
        ]

        comparison = [
            {
                "style": "结构化 Python dataclass / ToolResult",
                "fit": "推荐为主协议",
                "strengths": [
                    "类型可检查、IDE 友好、便于测试和序列化。",
                    "更适合作为系统内部稳定演进契约。",
                    "能自然承载 file_path / sha256 / section_index / warnings 等结构化字段。",
                ],
                "weaknesses": [
                    "若外部 SDK 边界只接受文本，需要额外适配层。",
                ],
            },
            {
                "style": "字符串内嵌 METADATA: JSON",
                "fit": "仅适合边界兼容层",
                "strengths": [
                    "短期兼容当前以文本输出为主的调用面。",
                ],
                "weaknesses": [
                    "依赖字符串分隔符，天然脆弱，容易被文案或换行污染。",
                    "迫使 ToolResultExtractor、测试和 Agent 一起承担文本解析负担。",
                ],
            },
            {
                "style": "kimi SDK ToolOk/ToolError",
                "fit": "明确拒绝作为系统主契约",
                "strengths": [
                    "适合 SDK 边界调用。",
                ],
                "weaknesses": [
                    "把系统内部事实格式绑死到特定 SDK 类型。",
                    "已经与 ToolResult/dataclass 和 METADATA 文本兼容层形成三叉分裂。",
                ],
            },
        ]

        return {
            "title": "ToolResult / ToolResultExtractor / 工具返回格式之间已经分叉",
            "severity": "P1",
            "decision": "主协议收敛到结构化 ToolResult/dataclass；METADATA: JSON 仅保留为边界兼容；拒绝 kimi SDK ToolOk/ToolError 作为系统主契约。",
            "comparison": comparison,
            "required_changes": [
                "让工具内部先返回统一 ToolResult，再由单一适配层决定是否包装成 SDK 所需返回类型。",
                "parse_deliverable_metadata 与 ToolResultExtractor 退到边界层，不再主导系统内部协议。",
                "新工具和新测试禁止继续把 ToolOk/ToolError 当作内部事实格式。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def _analyze_f6(self, test_file_count: int) -> dict[str, Any]:
        return {
            "title": "测试体系不能再把历史红灯直接当作当前质量门",
            "severity": "治理项",
            "decision": "接受用户输入：历史测试已清理并重建；当前工作区快照中未发现可见测试文件，因此本报告不以旧红灯判断当前回归质量。",
            "why": [
                f"当前工作区可见测试文件数为 {test_file_count}。",
                "这意味着本次研究无法用仓内旧测试直接证明当前回归状态，也不应该继续复用历史双轨假设做质量门。",
            ],
            "required_changes": [
                "新测试体系只围绕当前有效决策：state_json 单真相、docs-free、统一 ToolResult 协议。",
                "把环境敏感测试与核心契约测试分层，避免再次把噪音和真实回归混在一起。",
                "最先补齐的是 F1/F2/F3/F4/F5 的契约测试，而不是历史兼容测试。",
            ],
            "evidence": [],
        }

    def _analyze_f7(self) -> dict[str, Any]:
        evidence = [
            *self._find(
                "autoBMAD/docuswarm/__init__.py",
                [
                    "def __getattr__(name: str):",
                    '"IndependentAgent",',
                    '"create_node_execution",',
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/node_execution/__init__.py",
                [
                    "def __getattr__(name):",
                    '"create_node_executor",',
                    '"ContextValidator",',
                    "__all__ = [",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/models/__init__.py",
                [
                    "from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolResult",
                    "from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolRegistry",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/models/tool_registry.py",
                [
                    "class ToolRegistryExtended(ToolRegistry):",
                    '__all__ = ["ToolRegistry", "ToolDefinition", "ToolResult"]',
                ],
            ),
        ]

        return {
            "title": "类型系统、导出面和惰性导入层已经出现腐蚀",
            "severity": "P2",
            "decision": "同意原建议，收敛导出面，减少惰性导入，清理重导出与名实不符的兼容层。",
            "why": [
                "顶层包与 node_execution 都依赖大面积 __getattr__ 做懒加载，静态可见性差，类型系统保护效果被削弱。",
                "models/__init__.py 和 models/tool_registry.py 继续重导出 tools 层实体，且 ToolRegistryExtended 并未稳定暴露到 __all__，语义已经混乱。",
                "这些问题短期不一定炸运行时，但会持续拖慢重构反馈和类型检查可靠性。",
            ],
            "required_changes": [
                "优先明确公共 API 面，显式导出真正稳定的符号。",
                "减少兼容重导出，把 models/tools 的职责边界重新拉直。",
                "把 lazy import 缩到必要最小范围，配合类型检查修复 error 级问题。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def _analyze_f8(self) -> dict[str, Any]:
        evidence = [
            *self._find(
                "docs/design.md",
                [
                    "shared_context={}",
                    "original_context={}",
                    "EvaluatorAgentInput",
                ],
            ),
            *self._find(
                "docs/architecture.md",
                [
                    "shared_context: Dict",
                    "EvaluatorAgentInput",
                    "NodeExecutionContext",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/docs/DocuSwarm-CLI-Research-Report.md",
                [
                    "checkpoint_state = pipeline.get(\"state\", {})",
                    "`state_json`",
                    "checkpoints.py",
                ],
            ),
            *self._find(
                "autoBMAD/docuswarm/docs/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md",
                [
                    "return ToolOk(",
                    "checkpointer=checkpointer",
                ],
            ),
        ]

        return {
            "title": "文档层存在漂移与质量退化信号",
            "severity": "P2",
            "decision": "同意原建议，文档要围绕当前有效决策重新分层，区分现行规范、历史方案和废弃兼容。",
            "why": [
                "docs/design.md 与 docs/architecture.md 仍把若干中间态实现细节写成设计事实，容易把读者再次带回共享上下文被清空、Evaluator 重建缩水上下文的旧路径。",
                "仓内历史研究文档仍大量描述 checkpoint 作为主恢复视角、ToolOk/ToolError 示例等旧决策，若不标注状态，会继续污染后续实现与测试。",
            ],
            "required_changes": [
                "建立“当前生效决策索引”，明确 state_json/docs-free/ToolResult 是现行规则。",
                "为历史研究文档增加 archived / superseded 标记，避免被误读为现行架构。",
                "文档评审以后应把‘是否与当前代码和决策一致’当成独立质量门。",
            ],
            "evidence": [asdict(item) for item in evidence],
        }

    def to_markdown(self, report: dict[str, Any]) -> str:
        lines: list[str] = []
        lines.append(f"# {report['title']}")
        lines.append("")
        lines.append(f"> 范围：{report['scope']}")
        lines.append("> 研究方式：静态代码审查、SQLite 快照检查、文档漂移扫描、当前工作区测试可见性检查")
        lines.append("")
        lines.append("## 1. 用户已锁定的决策边界")
        lines.append("")
        for item in report["user_locked_decisions"]:
            lines.append(f"- {item}")
        lines.append("")

        runtime_snapshot = report["runtime_snapshot"]
        database = runtime_snapshot["database"]
        lines.append("## 2. 运行时快照")
        lines.append("")
        lines.append(f"- 数据库存在：`{database.get('db_exists')}`")
        lines.append(f"- 数据库路径：`{database.get('db_path')}`")
        lines.append(f"- pipelines 条数：`{database.get('pipeline_count', 0)}`")
        lines.append(f"- checkpoints 条数：`{database.get('checkpoint_count', 0)}`")
        latest_pipeline = database.get("latest_pipeline", {})
        latest_checkpoint = database.get("latest_checkpoint", {})
        if latest_pipeline:
            lines.append(
                f"- 最新 pipeline 的 `state_json` 键：`{', '.join(latest_pipeline.get('state_keys', []))}`"
            )
        if latest_checkpoint:
            lines.append(
                f"- 最新 checkpoint 的 channel 键：`{', '.join(latest_checkpoint.get('channel_value_keys', []))}`"
            )
        lines.append(
            f"- 当前工作区可见测试文件数：`{runtime_snapshot['visible_test_file_count']}`"
        )
        lines.append("")

        lines.append("## 3. 核心研究结论")
        lines.append("")
        for finding_id, finding in report["findings"].items():
            lines.append(f"### {finding_id}. {finding['title']}")
            lines.append("")
            lines.append(f"- 严重级别：`{finding['severity']}`")
            lines.append(f"- 决策：{finding['decision']}")
            if "why" in finding:
                lines.append("- 结论依据：")
                for item in finding["why"]:
                    lines.append(f"  - {item}")
            if "database_snapshot" in finding:
                dbs = finding["database_snapshot"]
                lines.append(
                    f"- 数据库证据：最新 `state_json` 键为 `{', '.join(dbs.get('latest_pipeline_state_keys', []))}`；最新 checkpoint channel 键为 `{', '.join(dbs.get('latest_checkpoint_channel_keys', []))}`"
                )
            if "decision_matrix" in finding:
                lines.append("- 决策矩阵：")
                for item in finding["decision_matrix"]:
                    lines.append(
                        f"  - `{item['option']}`: 业务真相={item['business_truth']}；稳定性={item['stability']}；可运维性={item['operability']}；耦合={item['coupling']}；当前缺口={item['current_gap']}"
                    )
            if "comparison" in finding:
                lines.append("- 方案对比：")
                for item in finding["comparison"]:
                    strengths = "；".join(item["strengths"])
                    weaknesses = "；".join(item["weaknesses"])
                    lines.append(
                        f"  - `{item['style']}`: 适配结论={item['fit']}；优点={strengths}；缺点={weaknesses}"
                    )
            if "required_changes" in finding:
                lines.append("- 收敛动作：")
                for item in finding["required_changes"]:
                    lines.append(f"  - {item}")
            evidence = finding.get("evidence", [])
            if evidence:
                lines.append("- 关键证据：")
                for item in evidence:
                    lines.append(
                        f"  - `{item['path']}:{item['line']}` -> `{item['snippet']}`"
                    )
            lines.append("")

        lines.append("## 4. 最终架构决策")
        lines.append("")
        for item in report["final_architecture_decisions"]:
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## 5. 推荐执行顺序")
        lines.append("")
        for idx, item in enumerate(report["execution_order"], start=1):
            lines.append(f"{idx}. {item}")
        lines.append("")

        return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="围绕 F1-F8 决策对 DocuSwarm 进行深度研究，并输出 Markdown/JSON 报告。"
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="输出格式，默认 markdown。",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出文件路径；未提供时打印到 stdout。",
    )
    args = parser.parse_args(argv)

    researcher = DocuSwarmDecisionResearcher(PROJECT_ROOT)
    report = researcher.collect()

    if args.format == "json":
        output_text = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        output_text = researcher.to_markdown(report)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text, encoding="utf-8")
    else:
        encoded = output_text.encode(sys.stdout.encoding or "utf-8", errors="replace")
        sys.stdout.buffer.write(encoded)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
