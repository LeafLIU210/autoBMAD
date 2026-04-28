# DocuSwarm calc-one-plus-one 根因研究报告

## 执行摘要

执行命令 `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 时，所有 5 个流水线节点（analyst, pm, ux, architect, po）均因 `CriteriaLoadError` 执行失败。根本原因是**节点配置文件路径解析不一致**。

## 问题现象

### 终端输出错误
```
[error] node_execution_failed error=Criteria file not found: D:\GITHUB\DocuSwarm\nodes\analyst\evaluator.yaml error_type=CriteriaLoadError node_id=analyst
[error] node_execution_failed error=Criteria file not found: D:\GITHUB\DocuSwarm\nodes\pm\evaluator.yaml error_type=CriteriaLoadError node_id=pm
[error] node_execution_failed error=Criteria file not found: D:\GITHUB\DocuSwarm\nodes\ux\evaluator.yaml error_type=CriteriaLoadError node_id=ux
[error] node_execution_failed error=Criteria file not found: D:\GITHUB\DocuSwarm\nodes\architect\evaluator.yaml error_type=CriteriaLoadError node_id=architect
[error] node_execution_failed error=Criteria file not found: D:\GITHUB\DocuSwarm\nodes\po\evaluator.yaml error_type=CriteriaLoadError node_id=po
```

同时伴随警告：
```
[warning] Persona file not found, using default node_id=analyst path=D:\GITHUB\DocuSwarm\nodes\analyst\persona.json
```

## 根因分析

### 1. 配置文件实际存放位置

节点配置文件实际存放在 `autoBMAD/nodes/` 目录下：
- `autoBMAD/nodes/analyst/node.yaml` ✓
- `autoBMAD/nodes/analyst/persona.json` ✓
- `autoBMAD/nodes/analyst/evaluator.yaml` ✓
- （pm, ux, architect, po 同理）

### 2. 不同加载器的路径解析逻辑

| 加载器 | 路径计算逻辑 | 实际解析路径 | 结果 |
|--------|-------------|-------------|------|
| `NodeLoader._get_base_path()` | `Path(__file__).parent.parent` (loader.py → nodes → autoBMAD) | `D:\GITHUB\DocuSwarm\autoBMAD\nodes\` | ✓ 成功 |
| `CriteriaLoader.__init__()` | `project_root or Path.cwd()` | `D:\GITHUB\DocuSwarm\nodes\` | ✗ 失败 |
| `PersonaLoader.load()` | `project_root or Path.cwd()` | `D:\GITHUB\DocuSwarm\nodes\` | ⚠ 回退默认 |

### 3. 调用链分析

`executor.py` 第 125-126 行：
```python
auto_bmad_root = Path(__file__).parent.parent.parent.resolve()
repo_root = auto_bmad_root.parent if auto_bmad_root.name == "autoBMAD" else auto_bmad_root
```

- `auto_bmad_root` = `D:\GITHUB\DocuSwarm\autoBMAD`
- `repo_root` = `D:\GITHUB\DocuSwarm` (项目根目录)

`executor.py` 第 147-151 行调用 `create_dual_agent_node`：
```python
node = create_dual_agent_node(
    config=config,
    session_manager=session_manager,
    node_id=node_id,
    project_root=repo_root,  # ← 传入项目根目录
)
```

`create_dual_agent_node` 将 `project_root=repo_root` 传递给：
- `create_independent_agent(project_root=repo_root)` → `PersonaLoader.load(project_root=repo_root)`
- `create_evaluator_agent(project_root=repo_root)` → `CriteriaLoader(project_root=repo_root)`

这导致 persona 和 evaluator 配置从项目根目录的 `nodes/` 查找，但配置文件实际在 `autoBMAD/nodes/`。

### 4. 为什么 NodeLoader 能成功而 CriteriaLoader 失败？

- `NodeLoader` 独立计算 base path，不依赖外部传入的 `project_root`
- `CriteriaLoader` 和 `PersonaLoader` 依赖 `create_dual_agent_node` 传入的 `project_root`
- `PersonaLoader` 有回退机制（使用默认 persona），只产生警告
- `CriteriaLoader` 没有回退机制，直接抛出 `FileNotFoundError`

## 影响范围

- 所有使用 `python -m autoBMAD.docuswarm start` 启动的流水线都会失败
- 5 个节点全部无法执行
- 无法生成任何交付物
- calc-one-plus-one 端到端验证任务完全阻塞

## 根因定位

**根本原因**: `executor.py` 在调用 `create_dual_agent_node` 时，错误地将 `project_root` 设为项目根目录（`repo_root`），而节点配置文件存放在 `autoBMAD/nodes/` 目录下。`NodeLoader` 能正确找到配置（因为它使用 `autoBMAD` 作为 base path），但 `CriteriaLoader` 和 `PersonaLoader` 被传入错误的路径。

**触发条件**: 当 `nodes/` 目录在项目根目录下不存在或为空时触发。

## 修复建议

依据奥卡姆剃刀原则，最简单的修复是：

修改 `autoBMAD/docuswarm/node_execution/executor.py` 第 151 行：
```python
# 修改前
node = create_dual_agent_node(
    ...
    project_root=repo_root,
)

# 修改后
node = create_dual_agent_node(
    ...
    project_root=auto_bmad_root,
)
```

这样：
- `CriteriaLoader` 和 `PersonaLoader` 将从 `autoBMAD/nodes/` 加载配置
- `context_builder` 仍使用 `repo_root` 解析 `docs/` 目录，不受影响
- 仅需修改一行代码
