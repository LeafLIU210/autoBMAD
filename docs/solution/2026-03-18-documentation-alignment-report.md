# DocuSwarm 文档对齐报告

> 对齐日期: 2026-03-18
> 对齐范围: PRD、Architecture、Design、Research 文档
> 对齐依据: 
> - `docs/research/2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md`
> - `docs/solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md`

---

## 对齐摘要

本次对齐工作基于 2026-03-18 的 P0/P1 技术债务深度研究和 TDD 方案，更新了以下文档：

| 文档 | 更新内容 | 状态 |
|-----|---------|------|
| PRD.md | 新增 TD-1~TD-5 技术债务索引、TDD 方案引用 | ✅ 已更新 |
| architecture.md | 新增 Implementation Status (TD-1~TD-5)、参考文档 | ✅ 已更新 |
| design.md | 新增 TD 相关参考文档 | ✅ 已更新 |
| F1 状态持久化研究 | 新增 TD-1 关联章节 | ✅ 已更新 |
| F2 Shared Context 研究 | 新增 TD-1、TD-4 关联章节 | ✅ 已更新 |
| F4 工具层收敛研究 | 新增 TD-2、TD-3 关联章节 | ✅ 已更新 |

---

## 详细变更

### 1. docs/prd.md

**变更位置**: 文档头部、F1-F8 决策体系、重构推荐顺序、参考工具

**新增内容**:

```markdown
### TD-1~TD-5 技术债务治理体系 (2026-03-18 新增)

基于技术债务评估报告，建立了 P0/P1 技术债务治理体系：

| 技术债务 | 严重级别 | 核心问题 | 状态 | 参考文档 |
|---------|---------|---------|------|---------|
| **TD-1** | P0 | current_node 与 state_json 状态重复表示 | 🟡 治理中 | [研究报告] |
| **TD-2** | P0 | 工具层强依赖 Path.cwd() | 🟡 治理中 | [研究报告] |
| **TD-3** | P1 | models 兼容层仍在主路径 | 🟡 治理中 | [研究报告] |
| **TD-4** | P1 | 三套执行骨架并存 | 🟡 治理中 | [研究报告] |
| **TD-5** | P1 | CLI 入口过厚 | 🟡 治理中 | [研究报告] |

### TD TDD 测试驱动方案 (2026-03-18 新增)

| 技术债务 | TDD 方案 | 测试文件 |
|---------|---------|---------|
| TD-1 | [P0/P1 TDD 主方案] | `test_state_json_single_source.py` |
| ... | ... | ... |
```

---

### 2. docs/architecture.md

**变更位置**: Implementation Status 章节、References 章节

**新增内容**:

```markdown
## 7. Implementation Status (F1-F8 & TD-1~TD-5)

### TD-1: State Duplication Resolution (P0) 🟡
- **Status**: In Progress (TDD Phase 2)
- **Problem**: current_node 重复表示
- **Solution**: state_json 为唯一业务真相源
- **TDD Reference**: [P0/P1 TDD Master Plan]

### TD-2: Tool Layer CWD Decoupling (P0) 🟡
- **Status**: In Progress (TDD Phase 1)
- **Problem**: Tools depend on Path.cwd()
- **Solution**: Explicit output_dir injection
...
```

---

### 3. docs/design.md

**变更位置**: References 章节

**新增内容**:

```markdown
### TD-1~TD-5 技术债务文档 (2026-03-18)

- [技术债务评估报告] - P0/P1 问题评估
- [技术债务深度研究报告] - 深度研究
- [P0/P1 TDD 主方案] - 测试驱动实施方案
```

---

### 4. Research 文档

#### F1 状态持久化研究

**新增**: "TD-1 技术债务关联" 章节

- 说明 F1 与 TD-1 的直接对应关系
- 引用技术债务评估报告和 TDD 方案

#### F2 Shared Context 研究

**新增**: "技术债务关联" 章节

- 说明 F2 与 TD-1、TD-4 的关联
- TD-1: shared_context 持久化依赖 state_json
- TD-4: shared_context 链路跨越骨架边界

#### F4 工具层收敛研究

**新增**: "技术债务关联" 章节

- 说明 F4 与 TD-2、TD-3 的关联
- TD-2: 工具层需要显式 output_dir 注入
- TD-3: models 兼容层需要清理

---

## 文档关联图

```
                              ┌─────────────────────────┐
                              │   技术债务评估报告       │
                              │   (2026-03-18)          │
                              └───────────┬─────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
          │  技术债务深度    │   │  F1-F8 决策     │   │  TDD 主方案     │
          │  研究报告        │   │  研究           │   │                 │
          │  (2026-03-18)    │   │  (2026-03-17)   │   │ (2026-03-18)    │
          └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
                   │                     │                     │
     ┌─────────────┼─────────────┐       │                     │
     │             │             │       │                     │
     ▼             ▼             ▼       ▼                     ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      ┌─────────────┐
│ PRD.md  │  │arch.md  │  │design.md│  │F1-F8    │      │ TDD 执行    │
│(已更新)  │  │(已更新)  │  │(已更新) │  │研究     │      │ 摘要        │
└─────────┘  └─────────┘  └─────────┘  └─────────┘      └─────────────┘
```

---

## 一致性检查清单

### PRD.md 一致性

- [x] TD-1~TD-5 技术债务表格与研究报告一致
- [x] TDD 方案引用指向正确路径
- [x] 执行路线图与 TDD 主方案一致
- [x] 验收标准涵盖所有 TD

### architecture.md 一致性

- [x] TD-1~TD-5 Implementation Status 与研究报告一致
- [x] TDD Reference 链接正确
- [x] 与 F1-F8 Implementation Status 并列展示

### design.md 一致性

- [x] 参考文档包含所有 TD 相关文档
- [x] 文档路径正确

### Research 文档一致性

- [x] F1 与 TD-1 关联描述准确
- [x] F2 与 TD-1、TD-4 关联描述准确
- [x] F4 与 TD-2、TD-3 关联描述准确
- [x] 所有链接指向正确

---

## 后续维护建议

1. **定期同步**: 当 TDD 方案实施进度更新时，同步更新 PRD 和 architecture 中的状态
2. **验收标准**: 当 TD 验收标准完成时，更新对应文档中的复选框
3. **链接检查**: 定期运行文档链接检查，确保所有引用有效

---

## 参考文档

- [技术债务评估报告](../evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md)
- [技术债务深度研究报告](../research/2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md)
- [P0/P1 TDD 主方案](2026-03-18-docuswarm-p0-p1-tdd-master-plan.md)
- [P0/P1 TDD 执行摘要](2026-03-18-docuswarm-p0-p1-tdd-execution-summary.md)

---

*对齐完成时间: 2026-03-18*
