# DocuSwarm `start` 命令启动失败深度研究报告

**研究日期**: 2026-04-28
**研究工具**: `tools/debug/docuswarm_launch_diagnostic.py`
**研究范围**: `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md`
**关联历史研究**:
- `2026-04-27-docuswarm-calc-one-plus-one-root-cause-report.md`
- `2026-04-06-docuswarm-root-cause-deep-research-report.md`
- `docs-doc/solution/TDD-Finding-1-2-3-4-5-Quick-Reference.md`

---

## 执行摘要

执行命令 `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 时，DocuSwarm 在**导入阶段即完全崩溃**，无法进入任何业务逻辑。本次研究识别出 **4 个阻断性根因**和 **3 个高优先级隐患**，形成清晰的"导入链瀑布失败"模式。

| 根因编号 | 优先级 | 问题 | 状态 |
|----------|--------|------|------|
| RC-A | P0 CRITICAL | `kaos` 未声明依赖导致导入链全崩 | 确认 |
| RC-B | P0 CRITICAL | `ANTHROPIC_API_KEY` 缺失导致配置验证失败 | 确认 |
| RC-C | P1 HIGH | `kimi_agent_sdk` 残留引用（遗留 SDK 未清理） | 确认 |
| RC-D | P1 HIGH | 节点配置路径解析不一致（历史回归） | 已知 |
| RC-E | P2 MEDIUM | `output/` 目录未预创建 | 确认 |
| RC-F | P2 MEDIUM | `docuswarm.yaml` 配置漂移风险 | 观察 |

> **核心结论**: `kaos.path` 是一个**幽灵依赖**——它被代码引用但不存在于依赖声明中、不存在于虚拟环境中、甚至在 PyPI 上也没有对应的公开包。这是本次启动失败的**第一块多米诺骨牌**。

---

## 问题现象重现

### 执行命令

```bash
cd /home/leafliu/autoBMAD
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

### 实际输出

```
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  ...
  File "/home/leafliu/autoBMAD/autoBMAD/docuswarm/pipeline/orchestrator.py", line 16, in <module>
    from kaos.path import KaosPath
ModuleNotFoundError: No module named 'kaos'
```

### 现象特征

1. **崩溃位置**: 导入 `pipeline/orchestrator.py` 时即失败，未进入任何 CLI 命令处理
2. **错误类型**: `ModuleNotFoundError`，非业务逻辑异常
3. **级联效应**: 由于 `orchestrator.py` 被 `cli/commands/start.py` -> `cli/services/pipeline_service.py` 依赖，整个 CLI 命令树全部无法加载
4. **环境特征**: `.venv` 已激活（Python 3.12.10），所有声明依赖均已安装

---

## 根因深度分析

### RC-A: `kaos.path` — 幽灵依赖（P0 CRITICAL）

#### 问题描述

`autoBMAD/docuswarm/pipeline/orchestrator.py` 第 16 行：

```python
from kaos.path import KaosPath
```

`KaosPath` 仅在 `_get_or_create_session_manager()` 方法中使用两次：

```python
# orchestrator.py L193
work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id))
# orchestrator.py L196
work_dir = KaosPath(self._work_dir)
```

#### 为什么这是幽灵依赖？

| 检查维度 | 结果 |
|----------|------|
| `pyproject.toml` dependencies | 未声明 |
| `requirements.txt` | 未声明 |
| `.venv` 中是否安装 | 否 |
| PyPI 是否存在 `kaos` 包 | 无公开对应包 |
| 历史文档是否标记为技术债务 | 是（TDD-Finding-5） |

#### 历史背景

根据 `docs-doc/solution/TDD-Finding-1-2-3-4-5-Quick-Reference.md` 中的 **Finding 5: 依赖清理**：

> ```python
> from kaos.path import KaosPath  # ❌ pyproject.toml 未声明
> ```
> 
> **解决方案**: `from pathlib import Path` 标准库替代

这说明 `kaos.path` 的移除工作**已被识别但尚未完成**，导致代码与依赖声明之间出现"漂移"。

#### 影响范围

- **直接**: `orchestrator.py` 无法导入
- **级联**: `pipeline_service.py` -> `start.py` -> `cli/commands/__init__.py` -> `cli/main.py` -> `__main__.py` 全部失败
- **深层**: `NodeLoader` 因可能间接引用 orchestrator 相关模块，同样在导入链中受影响

---

### RC-B: `ANTHROPIC_API_KEY` 缺失（P0 CRITICAL）

#### 问题描述

即使通过 mock 或临时补丁绕过 `kaos` 导入，`Config.__post_init__` 会立即抛出 `ConfigurationError`：

```python
# config.py L110-116
api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ConfigurationError(
        "ANTHROPIC_API_KEY is required. Please set it in your .env file "
        + "or as an environment variable."
    )
```

#### 环境检查结果

| 配置来源 | 状态 |
|----------|------|
| `.env` 文件 | 不存在 |
| 环境变量 `ANTHROPIC_API_KEY` | 未设置 |
| `docuswarm.yaml` | 存在（但不会加载 API key） |

#### 为什么这是阻断性的？

`Config` 的初始化发生在 `cli/main.py` 的 `cli()` 函数中（每次 CLI 调用都会执行 `_ = load_config()`），这意味着**即使运行 `--help` 也会失败**（如果 kaos 被修复后）。

---

### RC-C: `kimi_agent_sdk` 残留引用（P1 HIGH）

#### 问题描述

`llm/approval.py` 中仍存在对 `kimi_agent_sdk` 的引用：

```python
# approval.py L12 (docstring 中的示例代码)
>>> from kimi_agent_sdk import ApprovalRequest

# approval.py L29 (TYPE_CHECKING 块中)
if TYPE_CHECKING:
    from kimi_agent_sdk import ApprovalRequest
```

#### 风险评估

- **运行时风险**: 低。`TYPE_CHECKING` 块在运行时不执行
- **代码质量风险**: 高。文档示例和类型提示引用了一个不存在的包，误导开发者
- **维护风险**: 高。`kimi_agent_sdk` 是已被迁移的旧 SDK，残留引用表明迁移清理不完整

#### 关联历史

TDD-Finding-5 同样标记了此问题：

> ```bash
> grep -r "kimi_agent_sdk" autoBMAD/ || echo "✅ PASS"
> ```

---

### RC-D: 节点配置路径解析不一致（P1 HIGH，历史回归）

#### 问题描述

根据 `2026-04-27-docuswarm-calc-one-plus-one-root-cause-report.md`，当启动命令最终能执行到节点层面时，会遭遇 `CriteriaLoadError`：

```
Criteria file not found: .../nodes/analyst/evaluator.yaml
```

#### 根因机制

| 加载器 | 路径计算逻辑 | 实际解析路径 |
|--------|-------------|-------------|
| `NodeLoader._get_base_path()` | `Path(__file__).parent.parent` | `autoBMAD/nodes/` ✓ |
| `CriteriaLoader.__init__()` | `project_root or Path.cwd()` | `nodes/` ✗ |
| `PersonaLoader.load()` | `project_root or Path.cwd()` | `nodes/` ✗ |

`executor.py` 错误地将 `project_root`（仓库根目录）传入 `create_dual_agent_node`，而配置文件实际在 `autoBMAD/nodes/` 下。

#### 关键代码

```python
# executor.py L125-126
auto_bmad_root = Path(__file__).parent.parent.parent.resolve()
repo_root = auto_bmad_root.parent if auto_bmad_root.name == "autoBMAD" else auto_bmad_root

# executor.py L147-151
node = create_dual_agent_node(
    config=config,
    session_manager=session_manager,
    node_id=node_id,
    project_root=repo_root,  # ← 错误：应为 auto_bmad_root
)
```

---

### RC-E: `output/` 目录未预创建（P2 MEDIUM）

#### 问题描述

`PipelineService.start()` 尝试使用 `output_dir`，但 `output/` 目录不存在：

```python
# pipeline_service.py L64-65
work_dir = Path(config.output_dir)
work_dir.mkdir(parents=True, exist_ok=True)  # 会创建，但属于运行时行为
```

虽然 `exist_ok=True` 避免了崩溃，但在全新环境中首次运行时，目录的延迟创建可能导致竞态条件或权限问题。

---

### RC-F: `docuswarm.yaml` 配置漂移风险（P2 MEDIUM）

#### 问题描述

`docuswarm.yaml` 存在于 `autoBMAD/docuswarm/docuswarm.yaml`，但 `config.py` 的加载逻辑为：

```python
# config.py L202-203
if yaml_path is None:
    yaml_path = Path(__file__).parent / "docuswarm.yaml"
```

这意味着 YAML 配置与 `config.py` 同目录，这在包安装后可能指向 `site-packages/autoBMAD/docuswarm/` 而非项目根目录。如果用户在项目根目录放置 `docuswarm.yaml`，它**不会被加载**。

---

## 失败链分析

```
用户执行: python -m autoBMAD.docuswarm start --context ...
    │
    ▼
[Step 1] 导入 autoBMAD.docuswarm.__main__
    │
    ▼
[Step 2] 导入 cli.main -> cli.commands -> cli.commands.start
    │
    ▼
[Step 3] 导入 cli.services.pipeline_service
    │
    ▼
[Step 4] 导入 pipeline.orchestrator
    │
    ├──► from kaos.path import KaosPath  ◄── 第一失败点 (RC-A)
    │         ModuleNotFoundError: No module named 'kaos'
    │
    ▼ (假设通过 mock 修复 kaos)
[Step 5] cli() 调用 load_config()
    │
    ├──► Config.__post_init__ 检查 ANTHROPIC_API_KEY
    │         ConfigurationError: ANTHROPIC_API_KEY is required  ◄── 第二失败点 (RC-B)
    │
    ▼ (假设设置 API key)
[Step 6] PipelineService.start() 创建 HybridOrchestrator
    │
    ▼
[Step 7] orchestrator.start_pipeline() 执行 LangGraph
    │
    ▼
[Step 8] 节点执行器尝试加载 analyst 配置
    │
    ├──► CriteriaLoader 查找 evaluator.yaml
    │         FileNotFoundError: nodes/analyst/evaluator.yaml  ◄── 第三失败点 (RC-D)
    │
    ▼ (假设修复路径)
[Step 9] IndependentAgent 调用 LLM 工具
    │
    ├──► create_deliverable 工具不可见 (历史 RC-1)
    │
    ▼ (假设修复 cwd)
[Step 10] 流水线完成，output/pipeline-*/ 下应有 5 个 .md 文件
```

---

## 修复路线图

### 第一优先级：解除启动阻断（必须修复）

#### Fix-A1: 移除 `kaos.path` 依赖

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

```python
# 修改前 (L16)
from kaos.path import KaosPath

# 修改后
from pathlib import Path
```

```python
# 修改前 (L193, L196)
work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id))
work_dir = KaosPath(self._work_dir)

# 修改后
work_dir = Path(self._work_dir) / pipeline_id
work_dir = Path(self._work_dir)
```

**验证**:
```bash
grep -r "from kaos.path" autoBMAD/ || echo "✅ PASS"
```

#### Fix-B1: 创建 `.env` 文件模板

**文件**: 新建 `/home/leafliu/autoBMAD/.env.example`

```
# DocuSwarm Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
```

**操作**: 用户需复制为 `.env` 并填入真实 API key。

#### Fix-C1: 清理 `kimi_agent_sdk` 残留

**文件**: `autoBMAD/docuswarm/llm/approval.py`

```python
# 修改前
if TYPE_CHECKING:
    from kimi_agent_sdk import ApprovalRequest

# 修改后
if TYPE_CHECKING:
    from claude_agent_sdk.types import ApprovalRequest
```

> 注：需确认 `claude_agent_sdk` 中是否存在 `ApprovalRequest` 类型。如不存在，使用 `Any` 替代。

---

### 第二优先级：修复节点执行路径（历史回归）

#### Fix-D1: 修正 `project_root` 传入值

**文件**: `autoBMAD/docuswarm/node_execution/executor.py`

```python
# 修改前 (L151)
node = create_dual_agent_node(
    ...,
    project_root=repo_root,
)

# 修改后
node = create_dual_agent_node(
    ...,
    project_root=auto_bmad_root,  # 使用 autoBMAD 根目录而非仓库根目录
)
```

---

### 第三优先级：配置与目录优化

#### Fix-E1: 预创建 `output/` 目录

```bash
mkdir -p /home/leafliu/autoBMAD/output
```

或在 `config.py` 的 `load_config()` 中增加目录初始化逻辑。

#### Fix-F1: 统一 `docuswarm.yaml` 搜索路径

**文件**: `autoBMAD/docuswarm/config.py`

```python
# 修改前
if yaml_path is None:
    yaml_path = Path(__file__).parent / "docuswarm.yaml"

# 修改后：优先查找项目根目录
if yaml_path is None:
    project_root = Path(__file__).parent.parent.parent.resolve()
    yaml_path = project_root / "docuswarm.yaml"
    if not yaml_path.exists():
        yaml_path = Path(__file__).parent / "docuswarm.yaml"
```

---

## 验证方法

### 阶段 1: 导入验证

```bash
cd /home/leafliu/autoBMAD
python -c "from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator; print('OK')"
```

### 阶段 2: CLI 加载验证

```bash
cd /home/leafliu/autoBMAD
python -m autoBMAD.docuswarm --help
```

### 阶段 3: 配置验证

```bash
python -c "from autoBMAD.docuswarm.config import load_config; c = load_config(); print('Config OK')"
```

### 阶段 4: 端到端启动验证

```bash
python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md
```

**期望结果**: 命令能正常启动，最终 `output/pipeline-*/` 下出现 5 个 `.md` 交付物文件。

---

## 关联技术债务索引

| 技术债务项 | 关联文件 | 优先级 | 参考文档 |
|-----------|---------|--------|----------|
| kaos.path 未清理 | `pipeline/orchestrator.py` | P0 | TDD-Finding-5 |
| kimi_agent_sdk 残留 | `llm/approval.py` | P1 | TDD-Finding-5 |
| cwd 职责未拆分 | `llm/session_manager.py` | P0 | RC-1 (2026-04-06) |
| 超时配置未接入 | `llm/session_manager.py` | P0 | RC-2 (2026-04-06) |
| 节点配置路径错误 | `node_execution/executor.py` | P1 | 2026-04-27 calc 报告 |
| 状态模型双轨制 | `storage/state_manager.py` | P1 | TDD-Finding-4 |
| 重复执行器 | `nodes/dual_agent.py` | P1 | TDD-Finding-3 |

---

## 附录 A: 诊断工具输出摘要

运行 `tools/debug/docuswarm_launch_diagnostic.py` 的完整输出已保存至：
`docs-doc/research/docuswarm-launch-diagnostic-report.md`

关键发现摘要：
- 导入链 6/6 全部失败，根因均为 `kaos`
- 15 个第三方依赖中 2 个缺失：`kaos`, `kimi_agent_sdk`
- 配置检查：`.env` 不存在，`ANTHROPIC_API_KEY` 未设置
- 静态分析：1 处 `kaos` 引用，2 处 `kimi_agent_sdk` 引用
- 执行模拟：即使绕过 kaos，配置验证仍失败

---

## 附录 B: 环境信息

| 项目 | 值 |
|------|-----|
| 操作系统 | Linux 24.04 |
| Python 版本 | 3.12.10 |
| 虚拟环境 | `.venv` (已激活) |
| 项目根目录 | `/home/leafliu/autoBMAD` |
| DocuSwarm 版本 | 1.0.0 |
| LangGraph | 已安装 |
| Claude Agent SDK | 0.1.69 |

---

*本报告由 `tools/debug/docuswarm_launch_diagnostic.py` 辅助生成，并结合历史研究资料进行人工分析与综合。*
