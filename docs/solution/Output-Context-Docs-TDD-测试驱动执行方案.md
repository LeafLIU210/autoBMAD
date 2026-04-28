## DocuSwarm Output/Context/Docs 测试驱动执行方案

**适用范围**:
- Output 目录统一相关逻辑（P0）
- Context_File 传递到 Agent/LLM 的完整链路（P1）
- @docs 文档读取/更新/列出工具（P2-docs）
- 多文档创建能力及模板体系（P2-multi-docs）

**目标**:
- 用最小但关键的一组单元测试与集成测试，锁定当前实现行为，防止后续重构引入回归。
- 让 `docs/solution` 中的 TDD 方案文档与实际测试文件一一对应，可追踪、可执行。

---

## 一、总体策略

### 1.1 测试分层

- **单元测试（unit）**:
  - **目标**: 在不依赖外部服务（Kimi API 等）的前提下验证核心逻辑与公共工具行为。
  - **位置**: `autoBMAD/docuswarm/tests/unit/`。
  - **手段**: 通过 `monkeypatch`、`unittest.mock` 等方式替换 `KimiSessionManager`、文件 IO 等外部依赖。
- **集成测试（integration）**:
  - **目标**: 从 pipeline 入口驱动 `HybridOrchestrator`、节点执行器与 Agent，覆盖 Output/Context/Docs 端到端行为（在必要位置对 LLM 响应做 mock）。
  - **位置**: `autoBMAD/docuswarm/tests/integration/`。
  - **手段**: 构造真实的 SQLite/文件目录结构，使用测试专用 `db_path`、`work_dir`、`docs` 目录，mock LLM 调用但保留其调用拓扑。
- **端到端手工验证（manual E2E）**:
  - **目标**: 通过 CLI 命令确认测试无法覆盖的交互体验与目录结构细节，例如控制台输出与日志内容。
  - **手段**: 使用 `python -m autoBMAD.docuswarm start -c ...` 等命令；在 TDD 文档中给出推荐命令，不在自动化测试中强制执行。

### 1.2 优先顺序

1. **第一阶段（必须）** — 锁定 P0/P1 行为：
   - 完成 `HybridOrchestrator` 与 `IndependentAgent` 的核心单元测试。
   - 补充一个最小集成测试验证 `context_file` 内容确实到达 IndependentAgent 并被用于 Prompt 构造。
2. **第二阶段（推荐）** — 固化 @docs 工具行为：
   - 为 `read_docs_file`/`update_docs_file`/`list_docs_files` 补充覆盖安全边界与备份行为的单元测试。
   - 通过集成测试验证 Agent 能成功读写测试用 `docs` 目录中的文件。
3. **第三阶段（增强）** — 引入多文档创建测试：
   - 为 `create_document_set` 与节点模板体系建立单元测试。
   - 在集成级别验证多文档创建结果与模板约束（必需章节、Mermaid 基本合法性）的关系。

### 1.3 与现有结构的约束

- **编码规范**（参考项目 Python 规范记忆与现有代码）:
  - 使用类型提示、dataclass、Google 风格 docstring，保持与现有模块一致。
  - 测试命名遵循 `test_<module>_<behavior>` 的模式，单个测试专注单一行为。
- **现有测试基础设施**:
  - 使用已有的 `conftest.py` 中共享 fixture（例如临时目录、配置加载），避免在新测试中重复造轮子。
  - 保持测试文件组织与现有 `test_message_extraction.py` 一致：以类/函数划分主题、适度使用 fixture 和 helper。

---

## 二、P0：Output 目录统一测试计划

### 2.1 单元测试：`test_orchestrator_work_dir.py`

**测试目标**: 验证 `HybridOrchestrator` 在不同构造参数下的 `work_dir` 选择策略，以及与 `KimiSessionManager` 的交互中不再依赖 `cwd()`。

**关联实现**:
- [HybridOrchestrator](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/pipeline/orchestrator.py)
- `_get_or_create_session_manager`
- `start_pipeline`

**测试用例设计**:

- **用例 P0-U1: 默认 work_dir 指向 autoBMAD/output**
  - 构造: `HybridOrchestrator(db_path=temp_db, api_key="test", base_url="https://test")`，不传 `work_dir`。
  - 断言:
    - `orchestrator._work_dir` 末尾为 `autoBMAD/output`（兼容 Windows/Posix 分隔符）。
- **用例 P0-U2: 自定义 work_dir 保留**
  - 构造: `HybridOrchestrator(work_dir=str(tmp_path/"custom_output"), ...)`。
  - 断言: `_work_dir == custom_output` 完全相等，不被覆盖。
- **用例 P0-U3: SessionManager 使用全局 work_dir**
  - 使用 `unittest.mock.patch` 替换 `KimiSessionManager`，捕获其 `work_dir` 参数。
  - 调用 `_get_or_create_session_manager(pipeline_id=None)`。
  - 断言: 第一次调用时 `work_dir` 为 `KaosPath(orchestrator._work_dir)`，后续调用复用缓存实例，不再重新创建。
- **用例 P0-U4: SessionManager 使用 pipeline-specific work_dir**
  - 同样 patch `KimiSessionManager`。
  - 调用 `_get_or_create_session_manager(pipeline_id="pipeline-123")`。
  - 断言: `work_dir` 路径中包含 `output/pipeline-123`，不包含项目根目录裸 `pipeline-123` 子目录。

### 2.2 集成测试：`test_pipeline_output_directory.py`

**测试目标**: 从 `start_pipeline` 入口验证只在期望位置创建输出目录。

**场景设计**:

- **用例 P0-I1: Pipeline 输出目录创建**
  - 使用临时目录作为 autoBMAD 根（通过 `monkeypatch.chdir(tmp_project_root)` 或为 `HybridOrchestrator` 显式传入 `work_dir`）。
  - 准备最小 `subject_context`（不要求真实 LLM 调用，可通过 mock `_validate_context` 与 `_get_or_create_session_manager` 避免网络）。
  - 调用 `asyncio.run(orchestrator.start_pipeline(subject_context))`。
  - 断言:
    - 在 `work_dir/pipeline_id` 下存在输出目录。
    - 在测试项目根目录下**不存在**裸 `pipeline-*` 目录。

> 注意：此处集成测试仍可通过 mock LLM 与 checkpointer，避免引入真实外部依赖，仅验证目录层面的副作用。

---

## 三、P1：Context_File 传递测试计划

### 3.1 单元测试：`test_independent_agent_context.py`

**测试目标**: 验证 `IndependentAgent.execute` 能在多种 `subject_context` 结构下正确提取 `context_file` 内容，并按约定构造 `enriched_task`。

**关联实现**:
- [IndependentAgent.execute](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/agents/independent.py)
- `_call_llm`

**测试策略**:
- 使用 fixture 构造 `IndependentAgent`，通过 `PersonaLoader.load`、`KimiSessionManager` 的 mock 避免真实外部调用。
- 通过 patch `_call_llm`，捕获传入的 `user_message`，不关心 LLM 返回真实内容。

**用例设计**:

- **P1-U1: dict 结构 subject_context（嵌套 subject_context.content）**
  - 构造 `context`:
    - `task="Create document"`
    - `pipeline_id="test-123"`
    - `subject_context={"subject_context": {"content": "Original content A"}}`
  - 执行 `agent.execute(context)`。
  - 断言:
    - `_call_llm` 被调用一次。
    - `user_message` 中包含 `## Original Context`、`Original content A`、`## Task`、`Create document`。
- **P1-U2: JSON 字符串 subject_context**
  - `subject_context` 为 JSON 字符串，内部结构同 P1-U1。
  - 断言: `user_message` 中出现 JSON 中的 `content` 文本。
- **P1-U3: 扁平结构 subject_context.content**
  - `subject_context={"content": "Flat content"}`。
  - 断言: `user_message` 中包含 `Flat content`。
- **P1-U4: 无 content 时降级为仅 task**
  - `subject_context={}` 或 `None`。
  - 断言: `user_message` 不包含 `## Original Context`，只包含 `task` 本身。
- **P1-U5: 日志字段正确**（可选）
  - 通过 `caplog` 捕获 `extracted_context_content` 日志，验证 `has_context_content` 与 `context_length` 与输入匹配。

### 3.2 集成测试：`test_context_file_transmission.py`

**测试目标**: 在不接入真实 LLM 的前提下，验证从 CLI/Orchestrator 到 IndependentAgent 的 `context_file` 传递链路完整性。

**路径覆盖**:
- CLI / main → `HybridOrchestrator.start_pipeline` → 状态管理 (`create_initial_state`) → graph/state → `create_dual_agent_node` → `IndependentAgent.execute`。

**关键技术点**:
- 使用临时目录模拟项目根、autoBMAD 根与 `docs` 目录。
- 通过 monkeypatch 替换：
  - `HybridOrchestrator._validate_context`（直接返回 `{"valid": True}`）。
  - `KimiSessionManager` 或 `IndependentAgent._call_llm`，避免真实 HTTP 调用并捕获最终 Prompt。

**用例设计**:

- **P1-I1: context_file 内容贯通到 IndependentAgent**
  - 在临时目录创建 `proposal.md`，写入带有可识别短语的 Markdown（如 `"Build a web application with authentication"`）。
  - 使用 `HybridOrchestrator`（或通过模拟 CLI）启动 pipeline，传入 `subject_context`，确保 `context_file` 与 `content` 字段正确填写。
  - 在 `IndependentAgent._call_llm` 的 mock 中捕获 `user_message`。
  - 断言:
    - `user_message` 中包含 `## Original Context` 段落，并出现 `proposal.md` 中的关键短语。
    - `task` 部分与从 state 中提取的任务描述一致。

---

## 四、P2-docs：@docs 文档修改能力测试计划

### 4.1 单元测试：`test_docs_tools.py`

**测试目标**: 验证 `read_docs_file`/`update_docs_file`/`list_docs_files` 的核心行为与安全边界。

**关联实现**:
- [ReadDocsFileTool](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/tools/read_docs_file.py)
- [UpdateDocsFileTool](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/tools/update_docs_file.py)
- [ListDocsFilesTool](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/tools/list_docs_files.py)

**用例设计（按工具分组）**:

- **ReadDocsFileTool**:
  - 成功读取:
    - 在临时 `docs` 目录下创建 `test.md`，写入简单内容。
    - 调用工具，断言 `ToolOk.output` 中包含文件内容。
  - 路径穿越防护:
    - `file_path="../secret.md"` 时返回 `ToolError`，`message` 中包含 `Access denied`。
  - 不存在文件/目录:
    - 对不存在文件返回 `ToolError`，`brief="File not found"`。
- **UpdateDocsFileTool**:
  - 正常更新并备份:
    - 写入初始内容 `# Title\n\nBody`。
    - `old_content` 传入 `# Title`，`new_content` 为更新后的完整文档，`create_backup=True`。
    - 断言:
      - 返回 `ToolOk`，`output` 中包含 `Successfully updated`。
      - 原文件内容更新为新内容。
      - 在 `.backups` 目录中存在备份文件。
  - 内容验证失败:
    - 提供不匹配的 `old_content`，断言返回 `ToolError`，`message` 中包含 `verification failed`。
  - 路径穿越/不存在文件场景同 Read 工具。
- **ListDocsFilesTool**:
  - 递归列出 Markdown 文件:
    - 构造 `docs/architecture/design.md`、`docs/api.md` 两个文件。
    - 调用 `directory="."`, `pattern="*.md"`, `recursive=True`。
    - 断言 `ToolOk.output` 中列出了两个相对路径。
  - 非递归模式:
    - `recursive=False` 时在子目录下的文件不应出现。
  - 路径穿越/不存在目录同前。

### 4.2 集成测试：`test_docs_modification.py`

**测试目标**: 验证在启用 docs 工具并通过 pipeline/Agent 调用时，能够安全地更新 `docs` 目录中的文档并创建备份。

> 注意：在当前代码基线中，docs 工具尚未在 `independent_agent.yaml` 中注册，集成测试可分为“规划阶段”与“落地后补充”两步实施：
> - 规划阶段：仅给出期望的测试结构与断言，但先不提交执行失败的测试。
> - 落地后：在完成 Agent 配置更新后，再补充并启用此测试模块。

**预期测试结构**（落地时使用）:

- 在临时项目根下构造 `docs/architecture/test-design.md` 以及 `autoBMAD` 目录，使得工具的路径推断逻辑仍然有效。
- 构造一个 context 文件，描述“读取→插入新章节→更新→创建总结交付物”的任务，驱动 IndependentAgent 调用 docs 工具。
- 通过对 `docs/architecture/test-design.md` 的内容与 `.backups` 目录的检查，验证修改与备份逻辑。

---

## 五、P2-multi-docs：多文档创建能力测试计划

### 5.1 单元测试：`test_create_document_set.py`

**测试目标**: 验证 `create_document_set` 在不同模板与内容组合下的行为，以及对模板/图表的基本校验。

**关联实现**:
- [CreateDocumentSetTool](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/tools/create_document_set.py)
- 模板文件 `templates/*.yaml`

**测试策略**:
- 使用 `monkeypatch.chdir(tmp_path)` 将当前工作目录设置到临时输出目录。
- 保证临时目录下存在简化版 `templates/*.yaml`（可通过复制项目中的真实文件或写入测试专用模板）。

**用例设计**:

- **P2M-U1: 基于模板 ID 创建多个文档**
  - 准备两个 `DocumentSpec`，模板 ID 分别为 `market_research` 和 `user_personas`。
  - 内容中包含各自模板的必需章节标题。
  - 执行工具，断言:
    - 返回的 `ToolOk.output` 中包含 `Created 2 document(s)`。
    - 输出目录中存在 `market-research-report.md` 与 `user-personas.md`（基于模板 `filename_pattern`）。
- **P2M-U2: 缺失必需章节产生警告但仍写文件**
  - 构造缺少某个必要章节的内容。
  - 断言:
    - 文件仍然被创建。
    - `output` 中包含 `Validation Warnings` 与缺失章节名称。
- **P2M-U3: Mermaid diagram 基本合法性检查**
  - 构造包含 ` ```mermaid` 代码块、但第一行缺乏合法 diagram 类型的内容。
  - 断言: `Validation Warnings` 中包含有关 `Missing diagram type` 的信息。

### 5.2 集成场景（规划）

**目标**: 在 `IndependentAgent` 中注册 `create_document_set` 工具后，设计高价值场景，例如 Analyst 节点一次创建市场分析、人物角色与风险评估三份文档。

**测试思路**:
- 构造 context，使 LLM（通过 mock）返回对 `create_document_set` 的调用。
- 在集成测试中不验证 LLM 的智能程度，而是验证:
  - 工具被调用且产生多个文档。
  - 生成的文件名与模板期望匹配。
  - 必需章节缺失时，仅产生警告，不阻断文件生成。

---

## 六、测试执行与维护

### 6.1 推荐执行序列

- **本地开发循环**:
  - 聚焦某一方案（例如 P0），按以下顺序执行:
    - `pytest autoBMAD/docuswarm/tests/unit/test_orchestrator_work_dir.py -v`
    - `pytest autoBMAD/docuswarm/tests/integration/test_pipeline_output_directory.py -v`（完成后再启用）
  - 完成 P1/P2 后，扩展到:
    - `pytest autoBMAD/docuswarm/tests/unit -v`
    - `pytest autoBMAD/docuswarm/tests/integration -v`

### 6.2 与现有 TDD 文档的对齐关系

- **P0-Output目录统一-TDD方案.md** / **P1-Context_File传递-TDD方案.md**:
  - 本执行方案将其中给出的测试用例骨架具体化为文件名与断言细节，可直接作为实现蓝本。
- **P2-docs文档修改能力-TDD方案.md** / **P2-多文档创建能力-TDD方案.md**:
  - 原有方案多集中在工具/模板设计，本方案补充了测试分层、mock 策略与最小可行的断言集合。
- **Output目录统一与Context_File传递-概览.md**:
  - 本执行方案将概览文档中的“文件修改清单”和“实施顺序”映射为实际测试文件与运行命令，形成完整闭环。

---

## 七、实施顺序建议（总结版）

- **步骤 1**：实现 P0/P1 的单元测试与最小集成测试，确保 Output/Context 行为可回归。
- **步骤 2**：补齐 docs 工具的单元测试，在不修改 Agent 配置的前提下先锁定工具行为。
- **步骤 3**：实现 `create_document_set` 的单元测试，覆盖模板加载与验证逻辑。
- **步骤 4**：在 Agent 配置中逐步接入 docs 与多文档工具，并在此基础上补充对应的集成测试。
- **步骤 5**：将所有新测试纳入 CI 流程，结合基于 `pytest_summary.json` 的测试报告分析，持续更新 `docs/solution` 中的 TDD 方案与执行文档。