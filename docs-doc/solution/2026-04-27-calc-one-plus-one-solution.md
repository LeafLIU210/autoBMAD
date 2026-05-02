# calc-one-plus-one 测试驱动解决方案

## 问题概述

DocuSwarm CLI 命令 `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 因节点配置文件路径不一致导致所有节点执行失败。

## 奥卡姆剃刀原则

> "如无必要，勿增实体。"

选择**最小侵入性**的修复方案：仅修改一行代码的路径参数，使 `create_dual_agent_node` 的 `project_root` 指向配置文件实际所在的 `autoBMAD` 目录。

## 解决方案详情

### 代码修复

**文件**: `autoBMAD/docuswarm/node_execution/executor.py`
**行号**: 第 151 行
**变更**: 将 `project_root=repo_root` 改为 `project_root=auto_bmad_root`

```python
# 修复前
        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id=node_id,
            project_root=repo_root,
        )

# 修复后
        node = create_dual_agent_node(
            config=config,
            session_manager=session_manager,
            node_id=node_id,
            project_root=auto_bmad_root,
        )
```

### 修复原理

| 组件 | 修复前路径 | 修复后路径 | 效果 |
|------|-----------|-----------|------|
| `create_dual_agent_node` | `repo_root` (项目根目录) | `auto_bmad_root` (autoBMAD 目录) | 正确指向配置 |
| `PersonaLoader` | `nodes/{node}/persona.json` (项目根目录) | `autoBMAD/nodes/{node}/persona.json` | ✓ 找到文件 |
| `CriteriaLoader` | `nodes/{node}/evaluator.yaml` (项目根目录) | `autoBMAD/nodes/{node}/evaluator.yaml` | ✓ 找到文件 |
| `PromptTemplateEngine` | `nodes/{node}/persona.json` (项目根目录) | `autoBMAD/nodes/{node}/persona.json` | ✓ 找到文件 |
| `context_builder` | `repo_root` (不变) | `repo_root` (不变) | ✓ docs/ 解析不受影响 |

### 为什么这是最简方案

1. **不移动文件**: 无需复制或移动 15 个配置文件
2. **不修改加载器**: 无需改动 `CriteriaLoader`、`PersonaLoader`、`NodeLoader` 的逻辑
3. **不影响其他功能**: `context_builder` 仍正确解析项目根目录的 `docs/`
4. **单点修改**: 仅一行代码变更

## 测试策略

### 测试目标

1. 验证修复后节点配置能正确加载
2. 验证 5 个节点的 `node.yaml`、`persona.json`、`evaluator.yaml` 均能被解析
3. 验证 `create_dual_agent_node` 使用正确的 `project_root`
4. 验证端到端命令能成功启动（无配置类错误）

### 测试类型

- **单元测试**: 验证路径解析逻辑
- **集成测试**: 验证 `create_node_executor` + `create_dual_agent_node` 的集成
- **端到端测试**: 验证 CLI 命令启动时无配置错误

## 验证步骤

1. 执行代码修复
2. 运行测试套件确认无回归
3. 执行 CLI 命令验证终端输出无 `CriteriaLoadError`
4. 检查 5 个节点是否均成功加载配置

## 成功标准

1. bash 命令终端输出无 `CriteriaLoadError` / `FileNotFoundError` 错误
2. 5 个节点配置加载成功（无警告/错误）
3. 测试全部通过
4. 流水线能继续执行（后续 LLM 调用不在本方案范围内，但配置错误已消除）
