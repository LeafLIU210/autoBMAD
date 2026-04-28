# refactor-2026-03-26 运行时消费链路专项评估报告

**评估对象**
- 基线报告：`docs/evaluation/2026-04-03-refactor-2026-03-26-implementation-review.md`
- 评估范围：
  - `mcp_servers` 是否可移除
  - 节点级 evaluator 阈值与迭代配置是否真正进入运行时
  - `allowed_builtin_tools` 是否真正进入 SessionManager 运行时权限

**评估日期**
- 2026-04-03

**评估方法**
- 静态代码审查
- 运行时定向实测
- 定向 `pytest` 验证

---

## 1. 执行摘要

本次专项评估的核心结论如下：

1. **从需求语义上，可以不把 MCP 当作必须对外承诺的能力；但从当前实现上，`mcp_servers` 还不能直接移除。**
   当前代码里，节点级文件/搜索工具并不是“有了 `allowed_tools` 就能工作”，而是必须先通过 `mcp_servers` 把工具真正挂载到 SDK 会话里。也就是说，**需求不需要 MCP，不代表当前实现不依赖 MCP**。

2. **节点级 evaluator 配置已被 `NodeLoader` 成功加载，但运行时存在���双重绕开”问题。**
   - `EvaluatorAgent` 用硬编码阈值 `0.70/0.50` 判定 `APPROVED/BLOCKED`
   - `DualAgentNode` 的最大迭代次数没有从 `node.yaml/evaluator.yaml` 注入
   - `QualityConfig` 又以代码内置阈值接管了“达到最大迭代后的最终判定”
   因此，当前 evaluator 配置更像“可解析元数据”，而不是“运行时唯一真相”。

3. **`allowed_builtin_tools` 已进入节点 schema，但没有真正进入 SessionManager 运行时权限。**
   `NodeLoader` 已读到 `["Read", "Glob"]`，但 `IndependentAgent -> SessionManager` 只传了 `file_dirs/search_dirs`，导致 `SessionManager` 在重建 `NodeToolPermissions` 时丢失 builtin 白名单，最终运行时 `allowed_tools` 里只有 MCP 工具，没有 `Read/Glob`。

4. **专项评估中还发现一个与第 1 条强相关的附加问题：节点目录权限的路径解析基准疑似错误。**
   当前 `IndependentAgent` 将 `docs/` 解析为 `autoBMAD/docs/`，而仓库真实目录是仓库根下的 `docs/`。这意味着即便修掉 `mcp_servers` key 冲突，当前文件/搜索工具接线也仍然可能指向错误目录。

综合判断：

- **需求层**：应该表达为“节点级受控工具访问能力”，而不是“必须使用 MCP”
- **实现层**：当前还**不能**删除 `mcp_servers`
- **配��消费层**：evaluator 与 builtin tools 都存在“已加载、未完整消费”的典型半落地状态

---

## 2. 结论矩阵

| 议题 | 当前状态 | 严重级别 | 结论 |
|---|---|---|---|
| `mcp_servers` 是否可移除 | 需求层可去 MCP 化，运行时实现层不可直接删除 | 高 | 不能直接移除，应先替换接线能力 |
| evaluator 阈值/迭代配置运行时消费 | 已加载，未成为运行时单一真相 | 高 | 存在实质性配置-运行时偏差 |
| `allowed_builtin_tools` 运行时接入 | schema 已支持，SessionManager 未接线 | 中 | 配置未闭环 |

---

## 3. 议题一：`mcp_servers` 是否应该移除

### 3.1 需求视角的判断

如果只从需求语义出发，真正需要的是：

- 代理能够调用工具
- 工具权限能够按节点隔离
- 文件访问和搜索能力能够被约束到指定目录

从这个角度看，**“MCP”只是实现机制，不应该被提升为需求本身**。对外需求描述更合适的表述应是：

> 节点具有受控的工具调用能力，包含 builtin tools 与节点级文件/搜索能力，并且运行时权限与节点配置一致。

因此：

- **可以从需求文档/架构目标中移除“必须使用 MCP”的表述**
- **不应把“是否用了 MCP”作为验收标准**

### 3.2 当前实现为什��还离不开 `mcp_servers`

当前运行时里，节点级文件/搜索工具的接入链路是：

1. `IndependentAgent.execute_with_input()` 读取 `NodeLoader.load(self.node_id)`，提取 `file_dirs/search_dirs`
   - `autoBMAD/docuswarm/agents/independent.py:683-704`

2. `SessionManager._create_options()` 用这些目录重建 `NodeToolPermissions`
   - `autoBMAD/docuswarm/llm/session_manager.py:183-200`

3. `NodeToolFilter.create_mcp_servers()` 创建文件/搜索 FastMCP server
   - `autoBMAD/docuswarm/llm/tool_filter.py:150-204`

4. `SessionManager._create_options()` 再把这些 server 写入 `ClaudeAgentOptions.mcp_servers`
   - `autoBMAD/docuswarm/llm/session_manager.py:203-210`

5. `NodeToolFilter.get_allowed_tools()` 生成 `mcp__...` 风格工具名白名单
   - `autoBMAD/docuswarm/llm/tool_filter.py:95-148`

这意味着：

- `allowed_tools` 只是**白名单**
- 真正把文件/搜索工具挂进 SDK 会话的是 `mcp_servers`

换句话说，当前实现中：

> **没有 `mcp_servers`，就只有权限声明，没有工具实体。**

### 3.3 当前实现中 `mcp_servers` 本身还存在关键缺陷

#### 证据 1：server 命名发生覆盖

`SessionManager` 当前把 MCP server 列表转成字典时，使用的是：

```python
f"docuswarm-{server.__class__.__name__.lower()}-{self._node_id}"
```

对应代码：
- `autoBMAD/docuswarm/llm/session_manager.py:207-209`

而文件工具与搜索工具返回的对象都是 `FastMCP`：
- `autoBMAD/docuswarm/tools/file_tools.py:454-465`
- `autoBMAD/docuswarm/tools/search_tools.py:434-445`

因此两个 server 最终都会映射成同一个 key：

- `docuswarm-fastmcp-analyst`

#### 证据 2：运行时实测确认“创建了两个 server，但最后只剩一个 key”

本次定向实测：

- `NodeLoader.load("analyst")` 读取到：
  - `allowed_builtin_tools = ['Read', 'Glob']`
  - `file_dirs = ['docs/', 'docs/research/']`
  - `search_dirs = ['docs/']`

- 以真实 analyst 配置构造 `SessionManager._create_options()` 后得到：
  - `allowed_tools = ['mcp__docuswarm-files-analyst__read_document', 'mcp__docuswarm-files-analyst__list_documents', 'mcp__docuswarm-search-analyst__grep_search', 'mcp__docuswarm-search-analyst__glob_search']`
  - `mcp_servers_keys = ['docuswarm-fastmcp-analyst']`
  - `mcp_server_count = 1`

同时日志明确显示：

- `server_count=2`

这说明：

- `NodeToolFilter` 确实创建了两个 server
- `SessionManager` 在字典化阶段把它们覆盖成了一个

### 3.4 当前实现还存在 server key 与 allowed tool 命名源不一致

`NodeToolFilter.get_allowed_tools()` 的命名源是：

- `mcp__docuswarm-files-{node_id}__...`
- `mcp__docuswarm-search-{node_id}__...`

对应：
- `autoBMAD/docuswarm/llm/tool_filter.py:124-143`

而 `SessionManager` 写入 `mcp_servers` 的 key 却是：

- `docuswarm-fastmcp-{node_id}`

对应：
- `autoBMAD/docuswarm/llm/session_manager.py:207-209`

如果 SDK 将 `mcp_servers` 的 key 作为 server name 参与工具命名或匹配，那么：

- `allowed_tools`
- `mcp_servers`
- 实际工具名

三者就不是同源命名体系。

即便不依赖这层推断，单看“两个 server 只剩一个 key”已经足够判定现实现存在接线缺陷。

### 3.5 附加发现：当前节点工具目录解析基准也存在偏差

`IndependentAgent.execute_with_input()` 使用：

```python
str(self.project_root / d)
```

把节点配置里的 `docs/` 拼接为绝对路径：
- `autoBMAD/docuswarm/agents/independent.py:688-695`

而 `node_execution.executor` 传给 `create_dual_agent_node()` 的 `project_root` 是：

- `Path(__file__).parent.parent.parent.resolve()`
- 即 `autoBMAD`
- `autoBMAD/docuswarm/node_execution/executor.py:134-144`

所以运行时会把 `docs/` 解析为：

- `autoBMAD/docs/`

而仓库真实目录位于：

- 仓库根下 `docs/`

本次实测日志也出现了：

- `Allowed directory does not exist: autoBMAD\\docs`
- `Allowed directory does not exist: autoBMAD\\docs\\research`

这意味着第 1 条问题不只是 `mcp_servers` 是否保留，还包括：

- 即便继续保留 `mcp_servers`
- 当前目录权限解析也未必指向正确目标

### 3.6 是否建议现在移除 `mcp_servers`

**结论：不建议现在移除。**

应把问题拆成两层：

#### 可以移除的

- 需求表述里对 MCP 的显式绑定
- 架构说明里“用 MCP 才算完成”的表述

#### 现在不能移除的

- 当前 `SessionManager` 里的 `mcp_servers` 运行时接线

因为当前代码没有替代方案来同时满足：

- 节点级文件/搜索工具注入
- 目录级访问约束
- 工具名白名单控制

### 3.7 可行替代路径评估

#### 路径 A：继续保留 MCP，但把 MCP 降为实现细节

适用性：**最现实、最小改动**

做法：
- 保留 `mcp_servers`
- 修复 server key 命名与冲突
- 让 `NodeToolFilter` 成为唯一命名源
- 对上层只暴露“节点受控工具权限”，不暴露 MCP 术语

结论：
- **短期推荐**

#### 路径 B：改用 builtin tools + `can_use_tool/hooks` 做路径级控制

依据：
- SDK 文档快照已显示 `ClaudeAgentOptions` 支持 `can_use_tool` 与 `hooks`
  - `autoBMAD/agentdocs/05_python.md:107-110,367-369`
  - `autoBMAD/agentdocs/10_user_input.md:14-20`
  - `autoBMAD/agentdocs/11_hooks.md:117-129`

潜在优势：
- 需求表达更自然
- 可减少自建 MCP 工具层

现实问题：
- 当前代码完全没有接入 `can_use_tool/hooks`
- builtin `Read/Glob/Grep` 的权限模型与当前“按 node.yaml 指定目录白名单”并不等价
- 当前 `cwd` 是 `output/<pipeline_id>`，即便直接放开 `Read/Glob`，也未必能访问节点想读的 `docs/`

结论：
- **中期可研究**
- **不是可直接删除 `mcp_servers` 的即刻替代**

#### 路径 C：改为 SDK custom tools

依据：
- SDK 文档快照中的 custom tools 最终仍通过 `create_sdk_mcp_server()` + `mcp_servers` 暴露
  - `autoBMAD/agentdocs/05_python.md:54-63,242-246`
  - `autoBMAD/agentdocs/19_custom_tools.md`

结论：
- 这条路径可以优化实现方式
- 但**不能实现“移除 `mcp_servers`”这个目标**

### 3.8 本议题最终结论

> **需求上不需要 MCP，当前实现上仍依赖 MCP。**

推荐决策是：

- **需求层去 MCP 化**
- **实现层短期保留 `mcp_servers`，先修好命名、注入和目录解析**

---

## 4. 议题二：节点级 evaluator 阈值与迭代配置已加载，但运行时没有真正消费

### 4.1 `NodeLoader` 已经成功加载 evaluator 配置

`NodeLoader` 的 evaluator 配置结构已包含：

- `criteria`
- `threshold`
- `max_iterations`
- `model`
- `criteria_file`

对应：
- `autoBMAD/nodes/loader.py:90-98`
- `autoBMAD/nodes/loader.py:422-428`

真实节点配置也确实声明了这些字段，例如：

- `autoBMAD/nodes/architect/evaluator.yaml:23-27`
- `autoBMAD/nodes/analyst/evaluator.yaml:24-26`

### 4.2 运行时第一个断点：`EvaluatorAgent` 没有消费节点阈值

`EvaluatorAgent` 当前有硬编码阈值：

- `APPROVAL_THRESHOLD = 0.70`
- `BLOCKED_THRESHOLD = 0.50`

对应：
- `autoBMAD/docuswarm/agents/evaluator.py:67-69`

判定逻辑：
- `alignment_score >= 0.70 -> APPROVED`
- `alignment_score <= 0.50 -> BLOCKED`
- 其他 -> `NEEDS_REVISION`

对应：
- `autoBMAD/docuswarm/agents/evaluator.py:269-283`

而 `EvaluatorAgent._load_criteria()` 只读取 `criteria`，并不读取 `threshold/max_iterations/model`
- `autoBMAD/docuswarm/agents/evaluator.py:105-155`

因此当前 evaluator 运行时的真实语义是：

- **标准项来自节点配置**
- **阈值不来自节点配置**

### 4.3 运行时第二个断点：`DualAgentNode` 的 `max_iterations` 没有从节点配置注入

`DualAgentNode` 构造函数虽支持 `max_iterations`
- `autoBMAD/docuswarm/nodes/dual_agent.py:121-155`

但 `create_dual_agent_node()` 默认直接使用：

- `DualAgentNode.DEFAULT_MAX_ITERATIONS`
- `autoBMAD/docuswarm/nodes/dual_agent.py:868-910`

而 `node_execution.executor` 创建节点时并没有从 `NodeLoader` 读取 `config.evaluator.max_iterations`
- `autoBMAD/docuswarm/node_execution/executor.py:131-144`

结果是：

- 节点 evaluator 配置里的 `max_iterations`
- 运行时真正使用的最大迭代次数

两者当前没有连接。

### 4.4 运行时第三个断点：达到最大迭代后的最终判定被 `QualityConfig` 接管

`DualAgentNode` 在运行时用 `VerdictDeterminer(self.quality_config)` 决定 verdict：
- `autoBMAD/docuswarm/nodes/dual_agent.py:630-738`

`QualityConfig` 当前内置：

- 默认阈值：`0.70/0.50`
- architect 特殊阈值：`0.75/0.55`

对应：
- `autoBMAD/docuswarm/pipeline/quality.py:56-63`

而达到最大迭代后，`DualAgentNode` 又用：

- `self.quality_config.get_thresholds(self.node_id)`

决定 `FORCE_APPROVED/BLOCKED`
- `autoBMAD/docuswarm/nodes/dual_agent.py:771-779`
- `autoBMAD/docuswarm/nodes/dual_agent.py:819-845`

这使得最大迭代场景下的最终裁决来源于：

- `QualityConfig`

而不是：

- `NodeLoader.load(node_id).evaluator.threshold`

### 4.5 已确认的实质性偏差

本次定向实测：

- `NodeLoader.load("architect").evaluator.threshold`
  - `{'approval': 0.75, 'escalation': 0.5}`

- `QualityConfig().get_thresholds("architect")`
  - `{'approval': 0.75, 'escalation': 0.55}`

- `EvaluatorAgent` 类常量
  - `{'approval': 0.7, 'blocked': 0.5}`

这意味着 architect 节点当前存在至少两层不一致：

1. evaluator agent 前置判定仍按 `0.70/0.50`
2. 达到最大迭代后的最终处理又按 `0.75/0.55`

而配置文件真正声明的是：

- `approval: 0.75`
- `escalation: 0.50`

### 4.6 更深一层的问题：原始 evaluator verdict 可能直接绕过 `VerdictDeterminer`

`DualAgentNode` 在使用 `VerdictDeterminer` 前，先看 evaluator 输出的原始 verdict：

- 若已是 `APPROVED/FORCE_APPROVED/BLOCKED`，则直接采用
- 否则才调用 `VerdictDeterminer`

对应：
- `autoBMAD/docuswarm/nodes/dual_agent.py:723-738`

因为 `EvaluatorAgent` 自己就用硬编码阈值生成 terminal verdict，所以节点配置的阈值不仅“没有完整驱动运行时”，而且在一部分分支中会被**更早地绕过**。

### 4.7 本议题判断

**结论：这是高优先级运行时配置失真问题。**

当前 evaluator 配置的实际状态不是“配置即行为”，而是：

- `criteria` 驱动行为
- `threshold/max_iterations/model` 大部分仍停留在配置层

因此“节点级 evaluator 配置已落地”的表述需要修正为：

> 节点级 evaluator 配置已完成加载，但阈值、迭代控制与最终裁决尚未完全以配置为准。

### 4.8 建议整改

#### P0

- 以 `NodeLoader` 为 evaluator 配置唯一入口
- 创建 `EvaluatorRuntimeConfig`，统一承载：
  - `criteria`
  - `approval_threshold`
  - `escalation_threshold`
  - `max_iterations`
  - `model`

- 在 `create_dual_agent_node()` 阶段显式注入：
  - `EvaluatorAgent`
  - `DualAgentNode`

#### P0

- 删除或降级 `EvaluatorAgent.APPROVAL_THRESHOLD/BLOCKED_THRESHOLD` 为明确 fallback
- 删除或降级 `QualityConfig` 中对 architect 的硬编码覆盖

#### P1

- 增加运行时集成测试，至少覆盖：
  - architect 的 `approval=0.75`
  - architect 的 `escalation=0.50`
  - 节点 `max_iterations` 覆盖默认值

---

## 5. 议题三：`allowed_builtin_tools` 已写入 `node.yaml`，但未接入 SessionManager 运行时权限

### 5.1 配置层已经支持 builtin tool 白名单

`NodeToolPermissions` 已定义：

- `allowed_builtin_tools: list[str]`

对应：
- `autoBMAD/nodes/loader.py:121-134`

`NodeLoader` 也已从 `node.yaml` 读取该字段：
- `autoBMAD/nodes/loader.py:431-445`

真实节点配置均已声明：
- `autoBMAD/nodes/analyst/node.yaml:49-58`
- `autoBMAD/nodes/architect/node.yaml:55-63`
- 其他节点同样写入 `["Read", "Glob"]`

### 5.2 运行时丢失发生在 `IndependentAgent -> SessionManager` 之间

`IndependentAgent.execute_with_input()` 虽然会加载 `NodeLoader.load(self.node_id)`，但实际只提取了：

- `file_dirs`
- `search_dirs`

对应：
- `autoBMAD/docuswarm/agents/independent.py:683-704`

它没有把完整 `NodeToolPermissions` 对象传下去。

### 5.3 `SessionManager` 又重建了一次不完整的 `NodeToolPermissions`

`SessionManager._create_options()` 当前重新构建：

```python
tool_permissions = NodeToolPermissions(
    file_permissions=NodeFilePermissions(...),
    search_permissions=NodeSearchPermissions(...),
)
```

对应：
- `autoBMAD/docuswarm/llm/session_manager.py:190-194`

这里没有填充：

- `allowed_builtin_tools`

因此 `NodeToolFilter` 实际拿到的是：

- builtin 白名单为空
- file/search 目录存在

### 5.4 运行时实测确认 builtin tools 没有进入最终白名单

本次定向实测结果：

- `NodeLoader.load("analyst").tool_permissions.allowed_builtin_tools`
  - `['Read', 'Glob']`

- `SessionManager._create_options().allowed_tools`
  - `['mcp__docuswarm-files-analyst__read_document', 'mcp__docuswarm-files-analyst__list_documents', 'mcp__docuswarm-search-analyst__grep_search', 'mcp__docuswarm-search-analyst__glob_search']`

没有出现：

- `Read`
- `Glob`

这与 `NodeToolFilter.get_allowed_tools()` 的预期行为形成鲜明对比，因为其第一步本来就是：

```python
tools.extend(self.tool_permissions.allowed_builtin_tools)
```

对应：
- `autoBMAD/docuswarm/llm/tool_filter.py:114-118`

问题不在 `NodeToolFilter`，而在进入 `NodeToolFilter` 之前，builtin 白名单已经丢了。

### 5.5 为什么这不是“小问题”

它不是单纯的“少传两个字符串”，而是暴露出当前运行时权限模型有两份真相：

#### 配置层真相

- `node.yaml` 声明节点能用 `Read/Glob`

#### 运行时真相

- `SessionManager` 只给了 MCP 工具

这会造成：

- 配置文档与真实行为不一致
- 上层以为节点有 builtin 能力，实际没有
- 后续测试容易只验证“配置读到了”，却没有验证“运行时真的可用”

### 5.6 接回 builtin tools 时还要注意一个隐藏风险

**不能简单把 `["Read", "Glob"]` 追加回 `allowed_tools` 就算完成。**

原因有两点：

1. 当前 `SessionManager` 的 `cwd` 是 pipeline 输出目录
   - `autoBMAD/docuswarm/llm/session_manager.py:160`
   - `autoBMAD/docuswarm/agents/independent.py:639-700`

2. 节点配置里的目标目录却是仓库级 `docs/`

这意味着即便把 `Read/Glob` 接回去，也仍需要回答：

- builtin tools 的访问范围是否与节点目录白名单一致
- builtin tools 是否会越过当前节点级目录限制
- builtin tools 在 `output/<pipeline_id>` 这个 `cwd` 下能否正确访问 `docs/`

因此，这个问题和第 1 条问题其实是耦合的：

- **builtin tools 的运行时接线**
- **节点目录权限模型**

必须一起设计，不能分开硬补。

### 5.7 本议题结论

**结论：`allowed_builtin_tools` 当前属于“schema 已落地、运行时未落地”。**

建议不要把它表述为“已完成支持”，更准确的说法应是：

> `allowed_builtin_tools` 已完成配置建模，但 SessionManager 尚未消费该白名单，运行时权限模型仍不完整。

### 5.8 建议整改

#### P0

- 不要再让 `SessionManager` 自己拼装简化版权限对象
- 让 `IndependentAgent` 直接把完整 `NodeToolPermissions` 传给 `SessionManager`

#### P0

- `SessionManager` 构造器新增显式参数，例如：
  - `tool_permissions: NodeToolPermissions | None = None`

#### P1

- 如果接入 builtin tools，需要同步确定目录限制策略：
  - 继续使用 MCP 实现目录约束
  - 或改用 `can_use_tool/hooks` 对 builtin `Read/Glob/Grep` 做路径校验与拒绝

#### P1

- 增加运行时断言测试：
  - `allowed_tools` 必须包含 `Read/Glob`
  - builtin tools 与节点目录权限策略必须一致

---

## 6. 测试与验证情况

### 6.1 已成功运行的定向测试

执行：

```bash
python -m pytest tests/unit/llm/test_session_manager_mcp_config.py tests/unit/agents/test_independent_agent_execution.py -q
```

结果：

- `4 passed`

说明当前测试只能证明：

- `SessionManager` 会接受 `file_dirs/search_dirs`
- `IndependentAgent` 会把 `file_dirs/search_dirs` 传给 `SessionManager`

它们**不能证明**：

- `mcp_servers` key 不冲突
- builtin tools 已进入运行时
- evaluator 阈值/迭代配置真的驱动运行时

### 6.2 被环境阻断的测试

执行以下测试时，均被 `pytestqt` 临时目录权限阻断：

```bash
python -m pytest tests/unit/nodes/test_node_loader_evaluator.py -q
python -m pytest tests/unit/docuswarm/test_f3_threshold_loading.py -q
```

报错核心信息：

- `PermissionError: [WinError 5] 拒绝访问: C:\\Users\\Administrator\\AppData\\Local\\Temp\\pytest-of-Administrator`

因此本次会话中无法依赖这些用例完成“闭环通过”声明。

### 6.3 现有测试覆盖缺口

当前缺少能真正守住本次三项问题的集成断言：

- `mcp_servers` 同时存在 file/search 两个不同 key
- `mcp_servers` key 与 `allowed_tools` server name 同源
- `allowed_builtin_tools` 最终进入 `SessionManager._create_options().allowed_tools`
- `EvaluatorAgent` 与 `DualAgentNode` 使用的是节点配置阈值
- `max_iterations` 由节点 evaluator 配置驱动

---

## 7. 建议的整改优先级

### P0

1. 修复 `SessionManager._create_options()` 的 `mcp_servers` key 生成逻辑，禁止用类名当 key。
2. 统一 `mcp_servers` key 与 `allowed_tools` 的命名源，建议直接复用 `NodeToolFilter` 的 server naming convention。
3. 让 `IndependentAgent` / `SessionManager` 传递完整 `NodeToolPermissions`，不要只拆成 `file_dirs/search_dirs`。
4. 让 `EvaluatorAgent`、`DualAgentNode`、`VerdictDeterminer` 共用同一份从 `NodeLoader` 注入的 evaluator runtime config。
5. 修复节点权限目录的解析基准，确认 `docs/` 是相对仓库根还是相对 `autoBMAD/`。

### P1

1. 决定是否保留 MCP 作为内部实现细节。
2. 如果要逐步去 MCP 化，先设计 builtin tool 的路径级权限模型，再谈删除 `mcp_servers`。
3. 为 architect 节点补充配置驱动型集成测试，覆盖 `0.75/0.50/max_iterations`。

### P2

1. 清理当前测试环境里的 `pytestqt` 临时目录权限问题。
2. 把本次专项评估中的运行时实测沉淀为自动化回归测试。

---

## 8. 最终判断

本次专项评估给出的最重要结论不是“该不该用 MCP”，而是：

> **当前系统把“需求抽象”“配置建模”“运行时接线”混在了一起，导致上层看起来已经支持节点级工具权限与 evaluator 配置，实际运行时却仍由 MCP 接线细节、硬编码阈值和丢失的 builtin 白名单共同决定行为。**

因此更准确的状态描述应为：

- **需求层可以去 MCP 化**
- **实现层短期仍需保留 MCP 接线**
- **evaluator 与 builtin tools 目前都处在“已加载但未完整消费”的半闭环状态**

若要对外宣称 `refactor-2026-03-26` 的节点配置改革已经真正完成，至少还需要补齐以下三件事：

1. 运行时工具权限模型只有一份真相
2. evaluator 阈值/迭代控制只有一份真相
3. 测试能证明这两份“真相”确实进入了真实执行链

