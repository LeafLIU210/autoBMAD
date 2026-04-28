# DocuSwarm 研究文档

本目录包含 DocuSwarm 项目的深度研究报告，涵盖架构评估、问题分析和解决方案设计。

## 研究主题

### F1: 依赖漂移问题 (P0 - CRITICAL)

依赖声明与实际运行依赖之间的严重不一致。

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [Dependency Drift Research](./dependency-drift-2026-03-25/README.md) | 完整的依赖漂移分析、影响评估 | **必读** |
| [Dependency Drift Executive Summary](./dependency-drift-2026-03-25/EXECUTIVE_SUMMARY.txt) | 一页纸执行摘要 | 快速了解 |
| [Migration Plan](./dependency-drift-2026-03-25/migration-plan.md) | 详细的迁移实施方案 | **必读** |

**TDD 迁移方案**: [TDD-SDK-Migration-2026-03-25](../solution/TDD-SDK-Migration-2026-03-25.md)

**状态**: 🔄 **In Progress** (Drift Score 85/100)

---

### Finding B: 兼容层清理 (2026-04-04)

**零容忍兼容层清理**: 完全移除所有 deprecated/legacy/compatibility 代码。

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [Finding B 深度研究报告](./2026-04-04-finding-b-compatibility-layer-deep-dive.md) | 23 处兼容层标记分析、风险评估 | **必读** |
| [Finding B TDD 方案](../solution/2026-04-04-finding-b-compatibility-cleanup-tdd-plan.md) | P0/P1/P2 完整清理方案 | **必读** |
| [文档对齐报告](../DOCUMENT_ALIGNMENT_REPORT.md) | 所有文档对齐变更汇总 | 参考 |

**核心原则**:
1. **零容忍**: 不保留 deprecation 警告，直接移除代码
2. **零容忍遗留**: 所有兼容代码必须完全删除
3. **单一入口**: 每个功能只有一个主路径

**状态**: 🔴 **Priority** (P0/P1/P2 全面清理)

---

### F2: State JSON 一致性问题

`state_json` 单一真相源方向正确，但实现仍未完全收口。

## 文档清单

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [F2 深度研究报告](./2026-03-25-f2-state-json-consistency-research-report.md) | 完整的问题分析、风险评估、代码审查 | **必读** |
| [统一设计方案技术规范](./2026-03-25-f2-unified-design-spec.md) | 详细的改造方案、API 设计、实施路线图 | **必读** |

## 调试工具

```bash
# 运行 F2 一致性分析工具
python tools/f2_state_consistency_analyzer.py --db docuswarm.db

# 生成完整报告
python tools/f2_state_consistency_analyzer.py --generate-report

# 输出 JSON 格式（用于自动化）
python tools/f2_state_consistency_analyzer.py --json > docs/research/f2_analysis_report.json
```

## 核心发现摘要

### 问题本质

系统存在**双重状态来源**：
- **顶层字段**: `pipelines.current_node`, `pipelines.status`
- **state_json 内部**: `state_json.current_node`, `state_json.status`

### 风险等级

| 操作 | 风险等级 | 原因 |
|------|----------|------|
| `get_pipeline()` | **CRITICAL** | 同时返回双重来源数据 |
| `restart_from_node()` | **HIGH** | 读取和写入使用不同来源 |
| `cancel_current_node()` | **HIGH** | 读取和写入使用不同来源 |
| `status` 命令 | **HIGH** | 混合使用双重来源 |

### 推荐方案

**方案A：state_json 作为唯一真相源**（推荐）

1. 删除 `pipelines.current_node` 列
2. 所有读写操作统一通过 `state_json`
3. 建立 `update_pipeline_state()` 作为唯一写入入口

## 快速行动指南

### 立即执行（P0）

1. **添加一致性检查**
   ```python
   # 在关键操作前添加运行时检查
   _verify_state_consistency(pipeline_id)
   ```

2. **修复高危操作**
   - 修改 `update_pipeline_status()` 同步更新 `state_json`

### 短期执行（P1）

1. 统一 CLI 状态读取逻辑
2. 创建 `PipelineStateView` 帮助类
3. 标记旧方法为 deprecated

### 长期执行（P2）

1. 执行数据库迁移
2. 删除废弃代码
3. 更新架构文档

## 实施路线图

```
Week 1-2: 基础设施（新 API + 一致性检查）
Week 3-5: 调用点迁移（Orchestrator + CLI）
Week 6:   数据迁移
Week 7:   代码清理
Week 8:   验证与发布
```

## 相关资源

- [评估报告原文](../evaluation/2026-03-25-docuswarm-deep-evaluation-report.md)
- [Pipeline State 定义](../../autoBMAD/docuswarm/pipeline/state.py)
- [StateManager 实现](../../autoBMAD/docuswarm/storage/state_manager.py)

---

## Deep Reform 深度改革研究 (2026-04-06)

**DocuSwarm 深度改革研究系列** - 涵盖技能引入、节点任务重构、文档创建约束等重大架构改进。

### 改革概览

| 领域 | 核心内容 | 状态 |
|------|----------|------|
| **技能引入** | Claude Agent SDK Skills 集成 | 🔄 In Progress |
| **任务重构** | Analyst 从数据分析改为产品简介创建 | 🔄 In Progress |
| **文档约束** | 单/多文档创建约束机制 | 🔄 In Progress |
| **多文档支持** | architect/po 支持创建多份文档 | ⏳ Pending |
| **实现缺口** | F3/F4/F5/F6/F7/F8 修复 | 🔄 In Progress |

### 文档导航

#### 核心研究文档

| 文档 | 说明 | 适用读者 |
|------|------|----------|
| [Deep Reform README](./docuswarm-deep-reform/README.md) | 研究系列导航和使用指南 | 所有人 |
| [执行摘要](./docuswarm-deep-reform/REPORT_SUMMARY.md) | 核心问题和实施路线图摘要 | 快速了解 |

#### 改革专题研究

| 文档 | 主题 | 行数 | 说明 |
|------|------|------|------|
| [01-skills-introduction-mechanism.md](./docuswarm-deep-reform/01-skills-introduction-mechanism.md) | 技能引入机制 | ~1200 | Skills 集成方案设计 |
| [02-node-task-skill-mapping.md](./docuswarm-deep-reform/02-node-task-skill-mapping.md) | 节点任务重构 | ~255 | 5节点 Skill 映射 |
| [03-document-creation-constraints.md](./docuswarm-deep-reform/03-document-creation-constraints.md) | 文档创建约束 | ~1566 | 单/多文档约束完整方案 |
| [04-tool-permissions-configuration.md](./docuswarm-deep-reform/04-tool-permissions-configuration.md) | 工具权限配置 | ~240 | Shared Context 权限 |
| [05-shared-context-update-mechanism.md](./docuswarm-deep-reform/05-shared-context-update-mechanism.md) | Shared Context 机制 | ~450 | update_context 工具设计 |
| [06-summary-agent-design.md](./docuswarm-deep-reform/06-summary-agent-design.md) | 摘要 Agent 设计 | ~1000 | 引用文档摘要预生成 |
| [07-docs-context-persistence.md](./docuswarm-deep-reform/07-docs-context-persistence.md) | 文档上下文持久化 | ~400 | docs_context 持久化 |

#### 实现缺口研究 (F3-F8)

| 文档 | 主题 | 说明 |
|------|------|------|
| [F3-F4-F5-README.md](./docuswarm-deep-reform/F3-F4-F5-README.md) | F3/F4/F5 文档索引 | 快速导航 |
| [F3-F4-F5-implementation-gap-research-report.md](./docuswarm-deep-reform/F3-F4-F5-implementation-gap-research-report.md) | F3/F4/F5 实现缺口 | 主研究报告 |
| [F3-F4-F5-code-path-trace.md](./docuswarm-deep-reform/F3-F4-F5-code-path-trace.md) | 代码路径追踪 | 逐行分析 |
| [F3-F4-F5-solution-proposals.md](./docuswarm-deep-reform/F3-F4-F5-solution-proposals.md) | 解决方案建议 | 实施步骤 |
| [F6-F7-F8-executive-summary.md](./docuswarm-deep-reform/F6-F7-F8-executive-summary.md) | F6/F7/F8 执行摘要 | 快速了解 |
| [F6-F7-F8-deep-research-report.md](./docuswarm-deep-reform/F6-F7-F8-deep-research-report.md) | F6/F7/F8 深度研究 | 运行时链路断裂 |

### 关键改革点

#### 1. 技能引入机制 (F1/F6/F7)

**混合方案**: SDK原生discovery + system prompt快速参考 + node.yaml whitelist控制

```yaml
# node.yaml
tools:
  skills:
    sdk_native: true
    whitelist:
      - bmad-product-brief
      - bmad-domain-research
```

#### 2. Analyst 任务重构 (F7)

| 属性 | 旧值 | 新值 |
|------|------|------|
| task.name | `create-business-analysis-report` | `create-product-brief` |
| persona.name | `Analyst` | `Mary` |
| skill_ref | - | `bmad-product-brief` |

#### 3. 文档创建约束 (F3)

- **单文档**: analyst/pm/ux `max_deliverables: 1`
- **多文档**: architect/po 支持2-5份文档
- **参数扩展**: `document_index`, `document_total`, `document_type`

#### 4. 实现缺口修复

| 问题 | 状态 | 关键修复 |
|------|------|----------|
| F3 | 🔄 | MCP Schema 暴露 multi-document 参数 |
| F4 | 🔄 | `docs_context_summary` 传递链3处断点 |
| F5 | 🔄 | `SummaryAgent` 返回类型统一 |
| F6 | 🔄 | `update_context` MCP 暴露链路 |
| F7 | 🔄 | Analyst 任务语义重构 |
| F8 | ⏳ | 模板对齐运行时接线 |

### 实施路线图

```
Phase 1 (2天)    → Phase 2 (1天)    → Phase 3 (1周)   → Phase 4 (2周)   → Phase 5 (1周)
技能引入基础设施   Analyst 任务重构    单文档约束实施     多文档支持        F3-F8修复
```

### 验收标准

- ✅ Skills 机制正常工作
- ✅ Analyst 正确执行 `create-product-brief`
- ✅ 单文档约束有效
- ✅ F3-F8 实现缺口全部修复
- ✅ 所有节点端到端测试通过

### 相关文档更新

- [PRD Phase 16](../prd.md#phase-16-p15---docuswarm-deep-reform)
- [架构文档更新](../architecture/README.md#deep-reform-2026-04-06---重大架构改革)
- [设计约束更新](../design/README.md#deep-reform-设计约束-2026-04-06)
