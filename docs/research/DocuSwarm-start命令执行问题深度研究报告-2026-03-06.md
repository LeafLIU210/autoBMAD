# DocuSwarm `start` 命令执行问题深度研究报告

## 文档信息

| 字段 | 内容 |
|---|---|
| 主题 | 深度研究 `python -m autoBMAD.docuswarm start --context docs/examples/project-requirements.md` |
| 研究日期 | 2026-03-06 |
| 研究范围 | `@logs`、数据库、CLI 入口、编排层、节点执行层、工具注册链路、`@docs-copy` 既有研究 |
| 结论级别 | 可复现、可定位、具备代码级证据 |

---

## 一、执行摘要

本次研究确认：`python -m autoBMAD.docuswarm start --context docs/examples/project-requirements.md` 当前至少存在 **两层串行故障**，并且历史运行还暴露出 **一层“假成功”故障**。

### 核心结论

1. **你指定的命令在 2026-03-06 的当前环境下，首先失败在 Context Validation 阶段，而不是节点执行阶段。**
   - 首个阻塞点是 Kimi SDK 会话目录默认落到 `C:\Users\Administrator\.kimi\sessions`，当前执行环境对该目录无写权限，触发 `WinError 5`。
   - 将 `KIMI_SHARE_DIR` 重定向到仓库内可写目录后，权限问题消失，随后暴露出第二个真实问题：`Connection error.`。

2. **历史成功进入节点阶段的一次运行（`pipeline-1772787008108-cf362dbf`）表明：5 个节点全部失败，但流水线最终被错误标记为 `completed`。**
   - 根日志 `logger.log` 明确显示 analyst / pm / ux / architect / po 五个节点都报了 `no_deliverable_tool_called`。
   - 数据库却显示该流水线 `status=completed`、`current_node=po`，而且 `state_json` 仍然只有初始上下文，`node_results`/`node_runs` 为空。

3. **`create_deliverable` 工具链路存在明显断链。**
   - 运行时验证表明：`ToolRegistry` 在默认导入路径下是空的；只有显式 `import autoBMAD.docuswarm.tools` 后才出现 6 个工具。
   - 生产执行路径中几乎没有任何地方显式导入 `autoBMAD.docuswarm.tools`。
   - 因此，代码中的“工具已经通过 ToolRegistry 注册”的假设，在当前生产路径里并不成立。

4. **失败传播与状态持久化也存在系统性问题。**
   - `node_execution.executor` 吃掉节点异常，只把节点状态设成 `FAILED` 返回，而不抛出异常。
   - `pipeline.graph` 的集成执行器随后仍然无条件把该节点加入 `completed_nodes`。
   - `finalize_pipeline_state()` 又无条件把流水线总状态设为 `completed`。
   - 最终形成“节点全挂、流水线成功”的假象。

---

## 二、研究输入与证据来源

本次研究基于以下输入完成：

### 2.1 用户指定对象

- 命令：`python -m autoBMAD.docuswarm start --context docs/examples/project-requirements.md`
- 日志：`@logs`
- 调试工具：`@tools`
- 参考材料：`@docs-copy`

### 2.2 本次实际检查的关键文件

- CLI 入口：`autoBMAD/docuswarm/main.py`
- 编排器：`autoBMAD/docuswarm/pipeline/orchestrator.py`
- 上下文验证：`autoBMAD/docuswarm/pipeline/context_validator.py`
- 会话管理：`autoBMAD/docuswarm/llm/session_manager.py`
- 独立代理：`autoBMAD/docuswarm/agents/independent.py`
- 图执行层：`autoBMAD/docuswarm/pipeline/graph.py`
- 节点执行器：`autoBMAD/docuswarm/node_execution/executor.py`
- 工具注册：`autoBMAD/docuswarm/tools/__init__.py`
- 工具注册表：`autoBMAD/docuswarm/models/tool_registry.py`
- Kimi 共享目录：`venv/Lib/site-packages/kimi_cli/share.py`
- Kimi 会话目录逻辑：`venv/Lib/site-packages/kimi_cli/metadata.py`

### 2.3 本次检查的运行态证据

- 根日志：`logger.log`
- 本次复现日志：`logs/docuswarm-2026-03-06.log`
- 主数据库：`docuswarm.db`
- 调试快照：`docs-copy/research/_debug-snapshot-bubble-sort-cli-arch.md`

### 2.4 参考的既有研究（来自 `@docs-copy`）

- `docs-copy/evaluation/DocuSwarm-CLI-Research-Report.md`
- `docs-copy/research/BMM-NodeExecutor-重构研究报告-Part5-交付物保存流程.md`
- `docs-copy/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

说明：其中 `DocuSwarm-CLI-Research-Report.md` 有一部分结论已经过时。它假定 `start` 只建库不执行；而当前 `main.py` 已经实际调用 `HybridOrchestrator.start_pipeline()`。本报告已基于当前仓库代码重新校正。

---

## 三、当前命令的真实执行路径

### 3.1 CLI 层行为

`main.py` 中的 `start()` 现在不是旧版“只创建 pipeline 记录”的逻辑，而是：

1. 验证上下文文件存在且可读。
2. 用 `utf-8` 读取内容。
3. 调用 `ContextResolver.resolve()` 解析 `@` 引用。
4. 组装 `subject_context`。
5. `asyncio.run(orchestrator.start_pipeline(subject_context))`。

也就是说，**当前 `start` 命令确实进入了编排器，不是停留在 CLI 壳层。**

### 3.2 复现到的引用解析结果

对 `docs/examples/project-requirements.md` 的实际复现显示：

- subject = `project-requirements`
- 成功解析 1 个 `@` 引用
- 被引用文件是：`@docs/examples/bubble-sort-cli-arch.md`

这说明：**命令本身和上下文引用解析没有先天失败，真正的阻塞发生在更后面的 LLM 验证阶段。**

### 3.3 编排器中的关键时序

`HybridOrchestrator.start_pipeline()` 的顺序是：

1. 先做 `ContextValidator.validate(subject_context)`。
2. 验证通过后才调用 `StateManager.create_pipeline()`。
3. 再把状态更新为 `running`。
4. 再执行 LangGraph。

所以在当前复现中，如果 Context Validation 没过，**数据库里本来就不会生成新的 pipeline 记录**。这也解释了为什么你要求的 `project-requirements.md` 运行没有在 `docuswarm.db` 里留下新 pipeline。

---

## 四、第一层故障：Kimi 会话目录权限错误

### 4.1 复现结果

在 2026-03-06 的第一次复现中，命令输出如下关键信号：

- `Context validation failed after 4 attempts`
- `Failed to create session: [WinError 5] 拒绝访问`
- 路径指向 `C:\Users\Administrator\.kimi\sessions\...`

而 `logs/docuswarm-2026-03-06.log` 对应阶段也只出现：

- `single_prompt_start`
- `creating_session`
- `session_creation_error`
- `single_prompt_error`

循环 4 次后直接终止。

### 4.2 根因定位

Kimi CLI 的共享目录逻辑是：

- `kimi_cli.share.get_share_dir()`：优先用 `KIMI_SHARE_DIR`，否则默认 `Path.home() / ".kimi"`
- `kimi_cli.metadata.WorkDirMeta.sessions_dir`：在 `get_share_dir() / "sessions" / <workdir_md5>` 下创建会话目录

因此当前环境默认会尝试写：

`C:\Users\Administrator\.kimi\sessions\...`

而这条路径在本次执行环境下不可写，导致 **LLM 会话尚未创建就失败**，于是整个 `ContextValidator` 连第一轮有效请求都发不出去。

### 4.3 为什么这是“首个故障”

因为 `start_pipeline()` 先验证上下文再建 pipeline，权限错误发生在验证阶段，所以它会比：

- 网络错误
- 工具注册错误
- 节点执行错误

都更早暴露。

---

## 五、第二层故障：修正共享目录后，暴露真实连接失败

### 5.1 对照复现

我在同一天做了第二次复现，只改变一个条件：

```powershell
$env:KIMI_SHARE_DIR='D:\GITHUB\DocuSwarm\.kimi'
python -m autoBMAD.docuswarm --verbose --log-level DEBUG --log-file logs start --context docs/examples/project-requirements.md
```

结果：

- `WinError 5` 消失
- `session_created` 开始出现
- 随后 4 次都失败在 `single_prompt_failed`
- 终端输出是 `Connection error.`

### 5.2 结论

这说明当前命令不是单一问题，而是 **串行双故障**：

1. 默认共享目录权限问题
2. 共享目录修复后，网络/连接问题

因此如果直接盯着 “Connection error” 去修，很容易忽略更前面的环境权限阻塞；反过来，只修共享目录也不能让命令真正跑通。

---

## 六、历史运行暴露的第三层故障：节点全失败但流水线仍显示成功

### 6.1 历史样本

根日志 `logger.log` 记录了一次更早的流水线：

- pipeline_id: `pipeline-1772787008108-cf362dbf`
- subject: `bubble-sort-cli-arch`
- 时间范围：2026-03-06 08:50:08 到 2026-03-06 09:01:23

该样本不是你这次指定的 `project-requirements.md` 直接复现结果，但它非常有价值，因为它已经进入了节点执行阶段，能暴露更深层的运行时问题。

### 6.2 日志证据

五个节点全部出现同一类错误：

- `no_deliverable_tool_called`
- `independent_agent_failed`
- `node_execution_failed`

顺序覆盖：

- analyst
- pm
- ux
- architect
- po

也就是说，**这个流水线不是“部分失败”，而是 5/5 节点全部失败。**

### 6.3 但数据库给出的表象

`docuswarm.db` 中同一条 pipeline 的记录却是：

- `status = completed`
- `current_node = po`
- `state_json` 只保留了 `subject/context_file/content`
- `node_results = 0 行`
- `node_runs = 0 行`

这形成了非常危险的假象：

> 日志说全部失败，数据库说已完成，状态快照又像没跑过。

---

## 七、`create_deliverable` 工具链路断裂的根因分析

### 7.1 代码中的设计意图

`IndependentAgent` 的设计假设是：

- Agent 应使用 `create_deliverable` 工具产出交付物
- `_parse_response()` 通过 `ToolResultExtractor.extract_from_dicts()` 从响应中提取工具调用参数
- 如果没有提取到，则报 `no_deliverable_tool_called`

这和 `@docs-copy` 中既有研究是一致的：交付物保存流程被设计成“工具优先、文本次之”。

### 7.2 运行时验证结果

我直接检查了运行时注册表：

- 在默认导入路径下：`ToolRegistry.get_all()` 返回 `0`
- 显式执行 `import autoBMAD.docuswarm.tools` 后：返回 `6`

工具名分别是：

- `create_deliverable`
- `create_document_set`
- `list_docs_files`
- `read_docs_file`
- `update_context`
- `update_docs_file`

### 7.3 这意味着什么

`autoBMAD.docuswarm.tools.__init__` 的确会在导入时触发注册副作用；**但生产执行路径几乎没有地方显式导入它。**

因此当前代码存在一个非常明确的设计落差：

- 注释写的是“工具通过 ToolRegistry 显式注册”
- 真实运行却没有显式触发这一步

### 7.4 为什么这会导致 `no_deliverable_tool_called`

这里至少有两种可能，且都指向同一个修复方向：

#### 可能性 A：SDK 从未拿到工具定义

如果 SDK 侧没有接收到工具定义，那么模型根本不可能调用 `create_deliverable`。

#### 可能性 B：注册表虽然理论上存在，但生产路径根本没完成导入

这正是本次运行时验证直接证实的情况。

无论是哪种可能，结论都一致：

> 当前“工具可调用”这件事不是显式、稳定、可验证的生产能力，而是依赖导入副作用的脆弱假设。

---

## 八、“节点失败但流水线 completed”的代码级根因链

这个问题比工具缺失更严重，因为它会污染数据库状态与用户认知。

### 8.1 第一环：节点执行器吞掉异常

`node_execution/executor.py` 中，节点运行失败时：

- 记录 `node_execution_failed`
- 把 `new_state["status"] = FAILED`
- **但不重新抛出异常**

这意味着上层图执行器拿到的是“正常返回的失败状态对象”，而不是异常。

### 8.2 第二环：图执行器无条件把节点记为完成

`pipeline/graph.py` 的集成执行器在执行完节点后，无论节点是否真正成功：

- 都会递增 `node_iterations`
- 都会把当前 `node_id` 追加到 `completed_nodes`

也就是说，**“执行过”和“成功完成”在这里被错误地混为一谈。**

### 8.3 第三环：最终节点无条件把流水线设为 completed

`finalize_pipeline_state()` 只是把：

- `result["status"] = COMPLETED`

它并不会检查：

- 是否存在失败节点
- 是否缺少 deliverable
- 是否缺少 evaluation
- 是否存在阻塞问题

### 8.4 第四环：编排器把这个假状态写回数据库

`HybridOrchestrator.start_pipeline()` 在 `graph.ainvoke()` 返回后，直接把数据库状态更新成：

- `status = completed`
- `current_node = final_current_node`

因此假完成状态会被正式落库，而不是只停留在内存里。

### 8.5 最终后果

形成如下闭环：

1. 节点失败
2. 失败被吞掉
3. 图层把失败节点加入 completed_nodes
4. 流水线 finalize 设为 completed
5. DB 也被写成 completed

这会直接误导：

- `status` 命令
- 排障判断
- 后续 resume/restart 决策
- 用户对产物完整性的信任

---

## 九、状态持久化与可观测性缺口

### 9.1 `state_json` 没有同步最终 LangGraph 状态

当前 pipeline 表中的 `state_json` 在历史样本里只保留初始上下文，没有：

- `completed_nodes`
- `deliverables`
- `questions`
- `evaluations`
- `node_iterations`
- `error`

这让数据库无法承担“最终事实源”的角色。

### 9.2 集成执行路径没有落 `node_results` / `node_runs`

研究发现：

- `node_execution/flow.py` 中是有 `save_node_result()` 的
- 但 LangGraph 集成路径走的是 `pipeline.graph -> node_execution.executor`
- 该路径没有把执行结果可靠持久化到 `node_results` / `node_runs`

于是日志和数据库完全脱节。

### 9.3 日志分裂

当前至少存在两套关键日志来源：

- `logger.log`
- `logs/docuswarm-2026-03-06.log`

前者记录了历史节点失败，后者记录了本次上下文验证失败。对于同一个排障任务，调查者必须同时看两处，效率很低。

### 9.4 Windows 控制台编码噪声（次要问题）

仓库里存在中文和 `✓` 等 Unicode 输出；在 Windows/GBK 终端下容易出现乱码或编码异常。这个问题不会导致本次核心故障，但会降低排障效率。建议统一使用：

```powershell
$env:PYTHONIOENCODING='utf-8'
```

---

## 十、与 `@docs-copy` 既有研究的交叉验证

### 10.1 被当前代码证实的部分

`docs-copy/research/BMM-NodeExecutor-重构研究报告-Part5-交付物保存流程.md` 中关于“交付物必须先通过 `create_deliverable` 工具产生”的判断，与当前 `IndependentAgent._parse_response()` 的实现完全一致。

### 10.2 被当前代码修正的部分

`docs-copy/evaluation/DocuSwarm-CLI-Research-Report.md` 里“`start` 只建库不执行”的结论，对当前仓库版本已经不成立。现在 `main.py` 中 `start()` 会进入 `HybridOrchestrator.start_pipeline()`。

### 10.3 新增的研究结论

既有文档更多讨论了“理论设计”和“工具抽取模式”；本次研究新增确认了三个此前未完全闭环的问题：

1. `KIMI_SHARE_DIR` 默认目录权限问题
2. ToolRegistry 导入副作用导致的真实未注册状态
3. 节点失败仍被流水线包装成 completed 的假成功链路

---

## 十一、新增/完善的调试工具

本次按你的要求在 `@tools` 中补充了离线调试工具：

### 11.1 新增文件

- `tools/docuswarm_debugger.py`
- `tools/README.md`

### 11.2 工具能力

该工具可以自动串联：

- `docuswarm.db`
- `logger.log`
- `logs/*.log`
- 指定 `pipeline_id` 的数据库快照
- ToolRegistry 运行时注册状态

### 11.3 已生成的辅助快照

- `docs-copy/research/_debug-snapshot-bubble-sort-cli-arch.md`

### 11.4 推荐用法

```bash
python tools/docuswarm_debugger.py --pipeline-id pipeline-1772787008108-cf362dbf
python tools/docuswarm_debugger.py --pipeline-id pipeline-1772787008108-cf362dbf --format markdown
python tools/docuswarm_debugger.py --pipeline-id pipeline-1772787008108-cf362dbf --format markdown --output docs-copy/research/debug-snapshot.md
```

---

## 十二、优先级建议（按修复收益排序）

## P0：必须先做

### P0-1 修复默认共享目录权限问题

在 CLI 启动时显式设置或注入可写的 `KIMI_SHARE_DIR`，至少支持：

- `.kimi/` 位于项目根目录
- `autoBMAD/output/.kimi/`
- 或配置项统一管理

否则 `start` 连 Context Validation 都可能过不去。

### P0-2 显式初始化工具注册

不要依赖导入副作用。建议在生产启动链路显式调用：

- `import autoBMAD.docuswarm.tools`
- 或 `register_all_tools()`

并在 Session 创建前输出“已注册工具数”。

### P0-3 修复失败传播语义

应保证：

- 节点失败时抛异常或返回可阻断图执行的状态
- 图执行器不得把失败节点加入 `completed_nodes`
- `finalize_pipeline_state()` 不得无条件标 completed

否则会持续制造假成功。

## P1：尽快做

### P1-1 持久化最终状态快照

在每个节点完成后、以及流水线最终完成后，把真实状态同步回 `pipelines.state_json`。

### P1-2 集成路径写入 `node_results` / `node_runs`

让 LangGraph 集成路径与 `node_execution/flow.py` 的持久化能力对齐。

### P1-3 把日志统一到 pipeline 维度

建议：

- 全部日志统一落 `logs/`
- 文件名带 `pipeline_id`
- CLI 输出中明确打印本次日志文件路径

## P2：增强排障体验

### P2-1 新增内建 `debug` CLI 命令

把 `tools/docuswarm_debugger.py` 的能力内建进：

```bash
python -m autoBMAD.docuswarm debug <pipeline_id>
```

### P2-2 将“环境问题”和“业务问题”分层输出

例如把错误明确分成：

- Session directory permission
- Provider connection
- Tool registration
- Node execution failure

这样用户不会把后层故障误认为首因。

---

## 十三、最终结论

对你指定命令的最终判断如下：

### 结论 1：当前命令在本环境下并不会进入节点执行

因为它先失败在 Context Validation：

- 先是 `.kimi/sessions` 权限错误
- 修正后是 `Connection error.`

### 结论 2：即使后续网络通了，系统仍然存在更深层执行问题

历史日志已经证明：

- 节点可能全部失败
- `create_deliverable` 工具链路可能仍断裂
- 流水线仍可能被错误标记为 `completed`

### 结论 3：这是一个“环境问题 + 工具注册问题 + 状态机问题”叠加的复合故障

不能只修一处。

如果只修：

- 共享目录权限：会继续撞到连接问题
- 连接问题：可能继续撞到工具注册断链
- 工具注册：仍可能继续遭遇“失败被标成成功”

因此正确策略必须是：

1. 先修环境入口（`KIMI_SHARE_DIR`）
2. 再修工具注册与 SDK 桥接
3. 最后修失败传播和状态持久化

---

## 附录 A：本次实际执行的两条复现命令

### A.1 原始复现

```powershell
python -m autoBMAD.docuswarm --verbose --log-level DEBUG --log-file logs start --context docs/examples/project-requirements.md
```

结果：`WinError 5`，失败于 `C:\Users\Administrator\.kimi\sessions\...`

### A.2 共享目录修正后的对照复现

```powershell
$env:KIMI_SHARE_DIR='D:\GITHUB\DocuSwarm\.kimi'
python -m autoBMAD.docuswarm --verbose --log-level DEBUG --log-file logs start --context docs/examples/project-requirements.md
```

结果：会话创建成功，但 4 次验证请求都失败于 `Connection error.`

---

## 附录 B：建议的下一步验证顺序

1. 固定 `KIMI_SHARE_DIR` 到仓库可写目录。
2. 在 CLI 启动时打印 ToolRegistry 当前已注册数量。
3. 在创建 Session 前后打印实际可用工具列表。
4. 让节点失败时真正阻断 LangGraph，而不是继续 finalize。
5. 再做一次完整复现，确认：
   - pipeline 是否创建
   - tool 是否被调用
   - node_results 是否落库
   - state_json 是否同步
   - status 是否与真实执行一致

---

## Appendix C: 2026-03-08 Re-evaluation of Env Vars and Connection Failure

### C.1 Updated conclusion

Based on the March 8, 2026 re-evaluation, changing only `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` does **not** directly solve either of the first two failures in the `start` path.

- The session-directory permission failure is controlled by `KIMI_SHARE_DIR`, not by `ANTHROPIC_*`.
- The downstream `Connection error.` happens after session creation and is therefore a later-stage provider/connectivity failure.
- The active `start -> ContextValidator -> KimiSessionManager` path primarily reads `KIMI_API_KEY`, `KIMI_BASE_URL`, `KIMI_MODEL_NAME`, and `KIMI_SHARE_DIR`.

### C.2 Code evidence

- `autoBMAD/docuswarm/config.py` loads `.env` first and uses `override=True`.
- The same file reads `KIMI_API_KEY` and `KIMI_BASE_URL`, not `ANTHROPIC_*`, for the main DocuSwarm config.
- `autoBMAD/docuswarm/pipeline/orchestrator.py` creates `KimiSessionManager` for context validation.
- `autoBMAD/docuswarm/llm/session_manager.py` builds SDK config from `KIMI_*` values and then calls `Session.create(...)`.
- `ANTHROPIC_*` is mainly relevant to the separate `ClaudeSDKWrapper` path, which is not the first failing path for this `start` command.

### C.3 Important precedence warning

The current codebase uses `load_dotenv(..., override=True)`. In practice this means:

- project-root `.env` values override existing process/system environment variables;
- therefore, even if system-level `KIMI_*` values were changed, `.env` may still win at runtime;
- as a result, saying ?I already changed the system environment variables? is not sufficient unless `.env` is checked at the same time.

### C.4 Re-evaluating the two failures

#### First-layer failure: session directory permission

This remains a `KIMI_SHARE_DIR` / default `~/.kimi` write-permission problem. Replacing `ANTHROPIC_*` cannot directly fix it.

#### Second-layer failure: `Connection error.`

After redirecting `KIMI_SHARE_DIR` to a writable project-local directory, the logs show `session_created` followed by `single_prompt_failed`. This confirms that the local session setup step succeeded and the failure moved downstream to provider connectivity/access.

### C.5 What cannot yet be concluded safely

In the current restricted execution environment, the observed `Connection error.` is **not enough** to prove that the Kimi key is invalid. It is also compatible with:

- outbound network restrictions in the execution environment;
- base URL reachability problems;
- DNS / TLS / route failures;
- provider-side handshake rejection that the SDK surfaces as a generic connection failure.

### C.6 Practical next step

The next validation order should be:

1. set `KIMI_SHARE_DIR` to a writable in-repo directory;
2. explicitly print and verify `KIMI_API_KEY`, `KIMI_BASE_URL`, `KIMI_MODEL_NAME`, and `KIMI_SHARE_DIR`;
3. verify whether project-root `.env` is overriding system env values;
4. retry in an environment that allows real outbound access to the Kimi Code endpoint;
5. only then decide whether the remaining root cause is URL, key, or network policy.
