# 2026-03-25 DocuSwarm 深度评估报告

> 评估对象：`autoBMAD/docuswarm`
>
> 评估日期：2026-03-25
>
> 评估方法：静态代码审查、目录与构件边界检查、定向测试验证、工作树变更态势分析
>
> 核心结论：`docuswarm` 不建议重写，建议用 2 到 3 个迭代完成“入口收敛、状态语义收敛、执行主干收敛、运行时产物出包”四条主线治理

## 1. 执行摘要

`docuswarm` 已经不是“原型能不能跑”的问题，而是一个典型的“重构已进行到中段，但主入口、主语义、主边界尚未完全收口”的系统。它有明显的正向资产：模块分层方向基本正确，新的 `cli/commands + cli/services` 结构已经出现，`state_json` 单一真相源的方向已经被写进实现和测试意图中，`PipelineAdapter` 也明确表达了边界收敛的意识。

但当前技术债的利息也非常清楚：

- 安装依赖声明和真实运行依赖出现漂移，已经触及“能否稳定安装和运行”的底线。
- 真实 CLI 入口和正在被测试的新 CLI 入口仍未统一，容易出现“测试是绿的，用户入口仍旧不稳”的假象。
- `state_json` 与顶层 `current_node` 仍在并行表达状态，`status/resume/restart/cancel` 之间的业务语义尚未完全统一。
- `pipeline` 与 `node_execution` 两套执行骨架尚未完全收敛，兼容路径与 fallback 仍在主路径附近。
- 源码包内部混入数据库、缓存、输出目录、历史研究文档和嵌套目录，源码边界已经受到运行时产物污染。
- 测试与文档质量门存在明显漂移，且关键状态测试在本次验证中暴露出数据库初始化层的环境/架构问题。

按 `managing-tech-debt` 的原则判断，这不是应该重写的系统，而是应该立即停止继续扩散过渡态、优先删除和收口的系统。

## 2. 当前系统快照

### 2.1 代码规模

- `autoBMAD/docuswarm` 下共有 `94` 个 Python 源文件。
- 合计约 `16,302` 行 Python 代码。

分模块规模如下：

| 模块 | 文件数 | LOC |
|---|---:|---:|
| `pipeline` | 10 | 3120 |
| `node_execution` | 13 | 2255 |
| `agents` | 8 | 1777 |
| `storage` | 5 | 1584 |
| `nodes` | 4 | 1367 |
| `llm` | 6 | 1215 |
| `tools` | 10 | 1068 |
| `context` | 5 | 766 |
| `cli` | 14 | 722 |
| `prompts` | 6 | 628 |
| `utils` | 3 | 367 |
| `models` | 3 | 65 |

最大文件热点如下：

| 文件 | 行数 |
|---|---:|
| `autoBMAD/docuswarm/nodes/dual_agent.py` | 903 |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | 891 |
| `autoBMAD/docuswarm/storage/state_manager.py` | 840 |
| `autoBMAD/docuswarm/main.py` | 674 |
| `autoBMAD/docuswarm/agents/independent.py` | 661 |
| `autoBMAD/docuswarm/pipeline/graph.py` | 628 |

这说明复杂度高度集中在编排、状态、节点执行和旧 CLI 入口几个文件上，属于可治理但不能再继续扩散的债务形态。

### 2.2 工作树状态

本次评估时，工作树处于高变更态：

- `44` 个已修改文件
- `71` 个已删除文件
- `140` 个未跟踪文件
- 合计 `255` 条 `git status --short` 变更

这意味着当前分支明显处于大规模迁移或收敛阶段。它不改变架构判断，但会显著放大回归和文档漂移风险。

### 2.3 源码包边界

`autoBMAD/docuswarm` 顶层除了代码模块，还直接包含：

- `.pytest_cache/`
- `__pycache__/`
- `docs/`
- `output/`
- `docuswarm.db`
- `pytest.ini`
- 一个嵌套的 `autoBMAD/` 目录

按扩展名统计，当前包内存在：

- `94` 个 `.py`
- `101` 个 `.pyc`
- `14` 个 `.md`
- `9` 个 `.yaml`
- `1` 个 `.db`
- `1` 个 `.ini`

这已经不是单纯“目录有点乱”，而是源码包正在承载运行时产物、研究文档和缓存文件。

## 3. 本次验证动作

### 3.1 已执行

- `pytest tests/cli/test_commands_smoke.py -q`
  - 结果：`15 passed`
  - 说明：新 CLI 分层本身是可工作的，至少命令注册和薄入口方向成立。

- 同一轮测试生成的覆盖率快照显示，总体覆盖率约 `34%`。
  - 关键模块覆盖率偏低：
  - `storage/state_manager.py` 约 `25%`
  - `pipeline/orchestrator.py` 约 `34%`
  - `cli/commands/status.py` 约 `37%`
  - `main.py` 为 `0%`
  - `public_api.py` 为 `0%`
  - `tools/create_deliverable.py`、`tools/create_document_set.py`、`tools/tool_registry.py` 也为 `0%`

- `pytest tests/storage/test_state_json_single_source.py -q`
  - 结果：`5 errors`
  - 错误形态：不是断言失败，而是在 `StateManager(db_path=临时目录/test.db)` 初始化阶段触发 `sqlite3.OperationalError: unable to open database file`，随后临时目录清理又触发 `PermissionError`
  - 说明：关键状态测试当前暴露的是更底层的数据库初始化/资源生命周期问题，而不仅是业务断言问题。

### 3.2 验证噪声

两轮 pytest 都出现了 `.pytest_cache` 写入被拒绝的警告。这更像环境/权限噪声，但也侧面说明当前测试缓存和工作区权限治理不够干净。

## 4. 关键发现

### F1. 依赖声明与真实运行依赖漂移，已经接近 P0

**严重级别：P0**

**证据**

- `pyproject.toml:27-45` 和 `requirements.txt:15-17` 声明的是 `claude-agent-sdk`
- 但运行代码实际在导入：
  - `autoBMAD/docuswarm/pipeline/orchestrator.py:16-17` 使用 `kaos.path` 与 `kimi_agent_sdk`
  - `autoBMAD/docuswarm/llm/session_manager.py:25-38` 使用 `kaos.path`、`kimi_agent_sdk`、`kimi_agent_sdk._aggregator`
- `autoBMAD/docuswarm/tools/sdk_adapter.py`、`callable_tool_wrapper.py`、`agents/independent.py`、`agents/evaluator.py` 也依赖 `kimi_agent_sdk`
- `requirements-dev.txt:3` 仍写着 “kimi-agent-sdk architecture”，但 `requirements-dev.txt:31-33` 实际保留的是 `claude-agent-sdk`

**问题本质**

这里不是文案不一致，而是“依赖元数据表达的世界”和“代码实际运行的世界”已经不是同一个世界。只要 CI、打包、部署或新开发者按 `pyproject.toml` 安装，就可能得到一个声明上正确、运行时却缺包的环境。

**影响**

- 安装可靠性下降
- CI 可信度下降
- 故障定位成本上升
- 文档和环境初始化脚本会持续误导团队

**建议**

- 在一个迭代内明确唯一运行时 SDK 事实源
- 统一 `pyproject.toml`、`requirements*.txt`、README、安装脚本
- 把“依赖漂移计数”作为每周治理指标，目标是 `0`

### F2. `state_json` 单一真相源方向正确，但实现仍未完全收口

**严重级别：P0**

**证据**

- `autoBMAD/docuswarm/storage/state_manager.py:138-174`
  - `update_pipeline_status()` 仍直接更新顶层 `pipelines.current_node`
- `autoBMAD/docuswarm/storage/state_manager.py:253-315`
  - `get_pipeline()` 同时返回顶层 `current_node` 和 `state_json` 解析出的 `state`
- `autoBMAD/docuswarm/cli/commands/status.py:41-45`
  - 节点表使用 `pipeline_state = pipeline.get("state", {})`
  - 但当前节点又从顶层 `pipeline.get("current_node", "")` 读取
- `autoBMAD/docuswarm/pipeline/orchestrator.py:448-453`
  - `start_pipeline()` 启动时会写顶层 `current_node`
- `autoBMAD/docuswarm/pipeline/orchestrator.py:685-694`
  - `restart_from_node()` 从 `pipeline["state"]` 读取恢复语义
- `autoBMAD/docuswarm/pipeline/orchestrator.py:987-1045`
  - `cancel_current_node()` 又从 `state` 内读取 `current_node` 和 `current_node_session_id`

**问题本质**

团队其实已经在朝“`state_json` 是业务真相源”演进，但顶层列 `current_node` 仍在承担展示或控制责任。只要这些责任没有彻底分离，就会持续出现：

- 展示读一个来源
- 恢复读另一个来源
- 状态写回第三种时机

这类问题最伤团队信任，因为它往往表现为“状态看起来对，但恢复路径不对”。

**验证结果**

本次本来尝试用 `tests/storage/test_state_json_single_source.py` 验证这一方向，但测试没有走到业务断言阶段，而是在临时数据库初始化时失败。这进一步说明状态层不只是语义债，也存在可测试性/资源生命周期债。

**建议**

- 明确 `state_json` 为唯一业务真相源
- 顶层 `current_node` 若保留，只允许作为查询优化或冗余展示字段
- 为 `status/resume/restart/cancel` 增加统一的一致性测试集
- 修复数据库初始化与测试隔离问题，确保状态债可被自动化守住

### F3. CLI 分层已经完成 80%，但真实入口仍未切换

**严重级别：P1**

**证据**

- `pyproject.toml:43-44`
  - 打包脚本仍指向 `autoBMAD.docuswarm.main:cli`
- `autoBMAD/docuswarm/__main__.py:6`
  - `python -m autoBMAD.docuswarm` 仍导向旧 `main.py`
- 新 CLI 已存在且较薄：
  - `autoBMAD/docuswarm/cli/main.py:1-86`
  - 只负责注册命令、加载配置、初始化日志
- 新 CLI 的 smoke tests 也存在：
  - `tests/cli/test_commands_smoke.py:9` 从 `autoBMAD.docuswarm.cli.main import cli`
  - `tests/cli/test_commands_smoke.py:99-105` 明确要求薄入口 `< 150` 行
  - `tests/cli/test_commands_smoke.py:134-157` 明确要求 `cli/main.py` 不直接承载业务 `asyncio.run()`
- 旧入口体量仍偏大：
  - `autoBMAD/docuswarm/main.py` 约 `674` 行
  - 包含 `7` 个 `@cli.command()` 和 `4` 处 `asyncio.run()`

**问题本质**

这是一种非常典型的“重构成果已经存在，但生产入口还没切换”的过渡态。结果就是：

- 新结构有测试
- 旧入口是真实入口
- 真实入口反而没有得到新测试策略的保护

**影响**

- 测试绿灯不等于用户入口稳定
- 新旧入口共存会放大维护成本
- 所有人都会下意识继续补旧入口，或者误以为旧入口还能长期保留

**建议**

- 下一迭代优先把 `project.scripts` 和 `__main__.py` 切到 `autoBMAD.docuswarm.cli.main:cli`
- 如果暂时不能切换，也至少让旧入口退化成薄代理
- 切换后补一组真正命中打包入口的 smoke tests

### F4. 源码包内部混入运行时产物与历史文档，边界已被污染

**严重级别：P1**

**证据**

- `autoBMAD/docuswarm` 顶层直接包含：
  - `.pytest_cache/`
  - `__pycache__/`
  - `docs/`
  - `output/`
  - `docuswarm.db`
  - `pytest.ini`
  - `autoBMAD/`
- 包内扩展名统计显示：
  - `.py` 94 个
  - `.pyc` 101 个
  - `.md` 14 个
  - `.db` 1 个

**问题本质**

当源码包开始承载缓存、数据库、输出目录和历史研究文档时，会同时损伤：

- 打包边界
- 代码导航体验
- 构建可重复性
- 测试隔离
- “什么是源码，什么是产物”的团队共识

这类债务常常不会立刻炸掉功能，但会持续拉高所有工程动作的摩擦成本。

**建议**

- 立即把缓存、数据库、输出目录、研究文档移出运行时代码包
- 给打包规则和 `.gitignore` 加强约束
- 把“源码包中的非源码文件数”作为删除型治理指标

### F5. `pipeline` 与 `node_execution` 仍在并行承载主语义

**严重级别：P1**

**证据**

- 模块规模显示：
  - `pipeline` 3120 LOC
  - `node_execution` 2255 LOC
- 两侧同时存在同名或近同名概念：
  - `graph`
  - `state`
  - `metrics`
  - `escalation`
- `autoBMAD/docuswarm/pipeline/graph.py:55-93`
  - 仍保留 deprecated 的默认 executor，并明确说明会生成空 deliverable
- `autoBMAD/docuswarm/pipeline/graph.py:471-490`
  - 没有 `session_manager` 时仍会 fallback 到默认 executor
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py:35-60`
  - 通过合成 `node-{node_id}-{run_id}` 和 `node-run-{run_id}` 维护 synthetic pipeline id 语义

**问题本质**

系统已经意识到需要一个边界适配层，这是好事；但当前问题是“边界层存在”不等于“主干已收敛”。只要 fallback 仍留在主路径，主语义就还没有真正定下来。

**影响**

- 新人认知成本高
- 改动扩散面大
- 一旦出现生产问题，很难快速判断问题是在 orchestrator、graph、adapter 还是 node executor

**建议**

- 明确唯一主干：推荐 `pipeline` 负责业务编排，`node_execution` 负责节点执行
- 让 `PipelineAdapter` 成为唯一合法边界
- 尽快移除或硬失败 deprecated fallback，不再允许静默兜底

### F6. 兼容层过宽，删除节奏不清晰

**严重级别：P2**

**证据**

- `autoBMAD/docuswarm/models/__init__.py:13-32`
  - 通过 `__getattr__` 做懒加载兼容
- `autoBMAD/docuswarm/models/tool_registry.py:1-25`
  - 导入即告警的兼容 re-export
- `autoBMAD/docuswarm/public_api.py:1-48`
  - 又提供了一层稳定 facade
- `autoBMAD/docuswarm/tools/create_deliverable.py:183-198`
  - 保留函数式 backward-compatible API
- `autoBMAD/docuswarm/tools/create_document_set.py:311-322`
  - 同样保留函数式兼容 API
- `rg -n "tool_result_extractor|ToolResultExtractor" autoBMAD tests`
  - 除定义文件本身外，没有发现实际引用

**问题本质**

兼容层不是坏事，坏的是没有退场时间表。当前项目至少同时维护了：

- `models` 兼容入口
- `public_api` facade
- 函数式旧 API
- 新工具类 API
- 似乎已闲置的 `tool_result_extractor.py`

如果不主动删，这些入口会从“过渡层”自然演变成“永久支持面”。

**建议**

- 维护一份兼容层退场清单：入口、替代路径、目标删除版本
- 优先删除零引用模块和零收益兼容层
- 用删除代码替代继续增加“临时兼容”

### F7. 测试、配置和文档已经出现多处漂移

**严重级别：P2**

**证据**

- 测试配置双轨：
  - `pyproject.toml:60-76` 定义主 pytest 配置
  - `autoBMAD/docuswarm/pytest.ini:1-10` 又定义一份子配置
- README 编码漂移明显：
  - 根 `README.md:9-18` 已出现大面积 mojibake
  - `autoBMAD/docuswarm/README.md:1-44` 同样存在编码问题
- 用户可见输出也有编码问题：
  - `autoBMAD/docuswarm/cli/commands/status.py:53-61` 中状态文本为乱码字符
- 从定向测试看：
  - 新 CLI smoke 通过
  - 但关键状态测试在更底层失败
  - 覆盖率对关键模块保护不足

**问题本质**

这类债务不会立刻阻止系统运行，但会不断制造“局部看起来都正常，整体却不可信”的感觉。对使用者来说，这是产品债；对团队来说，这是认知税。

**建议**

- 统一 pytest 配置来源，只保留一份
- 统一 README 和 CLI 输出编码
- 将关键路径测试与展示层快照测试分层治理

## 5. 正向资产

为了避免把所有重构痕迹都误判为纯负债，这里也明确记录当前系统的正向基础：

- 新 CLI 分层方向是对的，而且 smoke tests 已经能证明注册与薄入口模型成立。
- `PipelineAdapter` 的存在表明团队已经开始有意识地把合成 ID 和转换逻辑收口，而不是继续散落在业务代码里。
- `StateManager.create_pipeline()` 已尝试写入完整 `PipelineState` 到 `state_json`，说明“单一真相源”的战略方向是清楚的。
- `pipeline_service.py` 体现了 CLI 与业务逻辑分层的健康演进。
- `create_deliverable` / `create_document_set` 已在接口上向结构化 `ToolResult` 方向收敛，这比纯字符串协议要健康。

这些资产说明：项目最需要的是收口和删减，而不是推倒重来。

## 6. 治理建议

### Phase 1：止血，1 个迭代

目标：先恢复“真实入口可信、安装可信、边界可信”。

建议动作：

1. 统一 SDK 依赖事实源
2. 切换真实 CLI 入口到 `autoBMAD.docuswarm.cli.main:cli`
3. 将缓存、数据库、输出目录、历史文档从 `autoBMAD/docuswarm` 包内移出
4. 为 `DatabaseManager` 的单例和路径生命周期补测试隔离方案

完成标准：

- 生产入口和测试入口完全一致
- 新环境按官方安装步骤可直接运行
- 包内不再出现 `.db`、`.pytest_cache`、`__pycache__`、`output/`

### Phase 2：收敛主语义，1 到 2 个迭代

目标：把状态和执行真正收敛成一条主线。

建议动作：

1. 明确 `state_json` 为唯一业务真相源
2. 为 `status/resume/restart/cancel` 建立统一一致性测试
3. 明确 `pipeline` 和 `node_execution` 的主从关系
4. 移除或禁止 deprecated default executor fallback

完成标准：

- 不再有任何业务逻辑依赖顶层 `current_node` 决策
- 没有 `session_manager` 时系统显式失败，而不是静默降级
- synthetic id 逻辑只保留在 `PipelineAdapter`

### Phase 3：删除代码，1 个迭代

目标：把过渡态真正结束掉。

建议动作：

1. 删除旧 `main.py` 或将其缩成纯代理
2. 为 `models`、`public_api`、函数式兼容 API 制定退场计划
3. 删除零引用模块，如 `tool_result_extractor.py`
4. 统一 README、pytest 配置和 CLI 编码输出

完成标准：

- 兼容层数量持续下降
- 零引用模块清零
- 文档和 CLI 输出不再出现编码错误

## 7. 建议跟踪指标

为了把技术债转化成可管理的产品债，建议每周跟踪以下指标：

- 真实 CLI 入口数量，目标 `1`
- 运行时代码包中的非源码文件数，目标持续下降至 `0`
- 依赖声明与实际导入不一致项数量，目标 `0`
- 关键状态用例通过率，目标 `100%`
- `pipeline/orchestrator.py`、`storage/state_manager.py`、`cli/commands/status.py` 覆盖率
- deprecated/compatibility 入口数量
- 零引用模块数量

## 8. 不建议做的事

- 不建议整体重写
- 不建议在真实 CLI 入口未切换前继续扩展新命令
- 不建议继续把运行时产物放进源码包
- 不建议继续维持“旧入口 + 新入口”“旧状态语义 + 新状态语义”双轨并行
- 不建议继续增加新的兼容层，而不先删除旧兼容层

## 9. 最终判断

`docuswarm` 当前最核心的债务，不是代码风格，也不是单点 bug，而是“重构方向对了，但系统还处在多条主线并行的过渡态”。这类债务最大的风险不是功能立即失效，而是交付可信度、安装可靠性、测试可信度和团队认知逐步下降。

好消息是，问题高度集中：

- 入口
- 状态
- 执行主干
- 包边界
- 兼容层

这意味着它非常适合做增量治理，不适合做重写。接下来最有价值的动作不是“再设计一套更漂亮的新架构”，而是果断收口、删除、统一事实源。只要优先级排对，连续 2 到 3 个迭代就能显著降低这套系统的维护利息。
