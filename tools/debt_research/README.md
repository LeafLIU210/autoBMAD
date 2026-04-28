# DocuSwarm 技术债研究工具套件

本目录包含用于深度研究 DocuSwarm 技术债的调试工具。

## 工具清单

| 工具 | 用途 | 输出 |
|------|------|------|
| `finding_1_session_manager_debug.py` | 分析 Session Manager 初始化链路问题 | 控制台报告 |
| `finding_2_pipeline_id_debug.py` | 分析 Pipeline ID 双轨问题 | 控制台报告 + 模拟测试 |
| `finding_3_dual_executor_debug.py` | 分析双轨节点执行器问题 | 函数对比分析 |
| `finding_4_state_model_debug.py` | 分析状态双轨模型问题 | 数据库结构分析 |
| `finding_5_dependency_drift_debug.py` | 分析依赖和命名漂移问题 | 依赖扫描报告 |
| `run_all_findings.py` | 批量运行所有调试工具 | JSON 汇总报告 |

## 使用方法

### 运行单个调试工具

```bash
cd d:\GITHUB\DocuSwarm
python tools/debt_research/finding_1_session_manager_debug.py
```

### 运行所有调试工具

```bash
cd d:\GITHUB\DocuSwarm
python tools/debt_research/run_all_findings.py
```

输出将保存在 `tools/debt_research/output/findings_raw_output.json`

## 研究报告

详细的研究报告位于 `docs/research/`:

- `2026-03-29-finding-1-2-3-4-5-deep-research-report.md` - 深度研究报告
- `2026-03-29-finding-1-2-3-4-5-implementation-guide.md` - 实施指南

## Finding 概要

### Finding 1: Session Manager 初始化故障 [P0]

**问题**: `start_pipeline()` 在未显式注入 `session_manager` 时会触发 LLM 校验后报错

**根因**: 
- `ContextValidator.__init__` 允许 `session_manager=None`
- `validate_context_with_llm()` 在 `session_manager` 创建前被调用

**解决**: 延迟注入模式 - 将 `session_manager` 从构造函数移到方法参数

### Finding 2: Pipeline ID 功能损坏 [P0]

**问题**: 数据库创建的 ID 与后续更新使用的 ID 不一致

**根因**: 
- `create_pipeline()` 总是自动生成 ID
- `final_pipeline_id = pipeline_id or db_pipeline_id` 可能使用不存在的 ID

**解决**: 移除自定义 `pipeline_id` 参数，强制使用数据库生成 ID

### Finding 3: 双轨节点执行器 [P1]

**问题**: `node_execution/executor.py` 和 `nodes/dual_agent.py` 各有一套执行器

**根因**: 职责边界不清，历史遗留代码

**解决**: 删除 `nodes/dual_agent.py` 中的重复执行器代码

### Finding 4: 状态双轨模型 [P1]

**问题**: `state_json` 与顶层列并存，读写来源不一致

**根因**: 
- `StateManager` 复制了 `_create_initial_state`
- 读写路径不统一

**解决**: `state_json` 作为唯一事实源

### Finding 5: 依赖、命名与文档漂移 [P1]

**问题**: 未声明依赖（`kaos.path`），命名不一致（`KimiSessionManager` vs `SessionManager`）

**根因**: SDK 迁移未完全清理

**解决**: 移除未声明依赖，统一命名，删除 deprecated 代码

## 修复优先级

```
Phase 0 (P0) - 紧急修复:
├── Finding 1: Session Manager 初始化
└── Finding 2: Pipeline ID 一致性

Phase 1 (P1) - 主干收敛:
├── Finding 3: 统一节点执行器
└── Finding 4: 统一状态模型

Phase 2 (P1) - 清理漂移:
└── Finding 5: 依赖和命名清理
```

## 验收标准

详见实施指南中的验收检查清单。
