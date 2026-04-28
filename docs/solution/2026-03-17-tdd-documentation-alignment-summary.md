# TDD 方案文档对齐更新总结

> 日期: 2026-03-17  
> 任务: 根据 TDD 测试驱动方案对齐更新相关文档

## 更新概览

已完成以下文档的更新，添加 TDD 测试驱动方案的引用和链接：

### 1. PRD 文档 (`docs/prd.md`)

**更新内容**:
- 在"相关重构方案"部分新增"TDD 测试驱动方案 (2026-03-17 新增)"小节
- 添加了所有 TDD 方案的链接：
  - TDD 主方案
  - 实施路线图
  - Phase 1/2/3 详细计划
  - 测试模板

### 2. 架构文档索引 (`docs/architecture/README.md`)

**更新内容**:
- 新增"TDD 测试驱动实施方案 (2026-03-17)"章节
- 添加目标架构摘要下方的 TDD 方案表格
- 添加实施顺序图示

### 3. 状态架构文档 (`docs/architecture/04_STATE_ARCHITECTURE.md`)

**更新内容**:
- 在文档末尾的 Alignment Notice 中添加：
  - TDD Implementation Plan 引用
  - Phase 1 (PipelineState shared_context 字段) 链接

### 4. 上下文隔离架构文档 (`docs/architecture/06_CONTEXT_ISOLATION.md`)

**更新内容**:
- 在文档末尾的 Alignment Notice 中添加：
  - TDD Implementation Plan 引用
  - Phase 2 (Evaluator 强制文件读取) 说明
  - Phase 3 (EvaluatorAgentInput 原始上下文) 说明

### 5. 重构概览文档 (`docs/research/2026-03-13-docuswarm-context-refactor-overview.md`)

**更新内容**:
- 新增第 8 节"TDD 测试驱动实施方案 (2026-03-17)"
- 包含核心文档表格
- 包含 Phase 详细计划表格
- 包含实施顺序图示
- 包含关键测试文件清单

### 6. 深度研究报告 (`docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`)

**更新内容**:
- 在文档末尾新增"TDD 测试驱动实施方案"章节
- 添加核心文档表格
- 添加 Phase 与研究发现的对应关系
- 添加实施顺序
- 添加测试模板说明

---

## 文档引用关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TDD 方案文档引用关系                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  核心方案文档                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2026-03-17-docuswarm-context-refactor-tdd-master-plan.md            │   │
│  │ (TDD 主方案 - 完整的测试驱动实施指南)                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ▲                                        │
│           ┌────────────────────────┼────────────────────────┐               │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌─────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐ │
│  │ prd.md          │  │ architecture/       │  │ research/               │ │
│  │ (产品需求文档)   │  │ README.md           │  │ 2026-03-13-overview.md  │ │
│  │                 │  │ (架构文档索引)       │  │ (重构概览)              │ │
│  │ • 重构方案引用   │  │                     │  │                         │ │
│  │ • TDD方案链接   │  │ • 目标架构摘要      │  │ • 第8节 TDD方案         │ │
│  │                 │  │ • TDD方案表格       │  │ • 实施顺序              │ │
│  └─────────────────┘  └─────────────────────┘  └─────────────────────────┘ │
│           │                        │                        │               │
│           │                        ▼                        │               │
│           │           ┌─────────────────────┐               │               │
│           │           │ 04_STATE_ARCH.md    │               │               │
│           │           │ 06_CONTEXT_ISO.md   │               │               │
│           │           │                     │               │               │
│           │           │ • Alignment Notice  │               │               │
│           │           │ • TDD Plan 引用     │               │               │
│           │           └─────────────────────┘               │               │
│           │                                                 │               │
│           └─────────────────────────────────────────────────┘               │
│                                    ▲                                        │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2026-03-17-deep-research-report.md                                  │   │
│  │ (深度研究报告)                                                       │   │
│  │                                                                     │   │
│  │ • 研究发现 -> TDD方案映射                                           │   │
│  │ • Phase与问题对应关系                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 关键更新点汇总

### 1. PRD 对齐 (`docs/prd.md`)

| 更新位置 | 更新内容 |
|----------|----------|
| 相关重构方案 -> TDD 测试驱动方案 | 新增 6 个 TDD 方案文档链接 |

### 2. 架构对齐 (`docs/architecture/`)

| 文档 | 更新位置 | 更新内容 |
|------|----------|----------|
| `README.md` | 新增章节 | TDD 测试驱动实施方案 (2026-03-17) |
| `04_STATE_ARCHITECTURE.md` | 文档末尾 | TDD Implementation Plan 引用 |
| `06_CONTEXT_ISOLATION.md` | 文档末尾 | Phase 2/3 说明 |

### 3. 研究文档对齐 (`docs/research/`)

| 文档 | 更新位置 | 更新内容 |
|------|----------|----------|
| `2026-03-13-docuswarm-context-refactor-overview.md` | 新增第 8 节 | 完整的 TDD 方案引用 |
| `2026-03-17-docuswarm-context-refactor-deep-research-report.md` | 文档末尾 | 研究发现到 TDD 方案的映射 |

---

## 文档间引用链路

### 发现 -> 方案 -> 实施的完整链路

```
研究发现
    │
    ├──► docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md
    │       └── P1-1-002: shared_context 未进入 IndependentAgentInput
    │       └── P0-3-004: Evaluator 退回到 deliverable.content
    │       └── P0-2-003: EvaluatorAgentInput 缺少原始上下文摘要
    │
    └──► docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md
            │
            ├──► Phase 1: P1-1 update_context 持久化
            │       └── tests/unit/tools/test_update_context_binding.py
            │       └── tests/unit/node_execution/test_contracts.py
            │
            ├──► Phase 2: P0-3 单一交付物真相
            │       └── tests/unit/context/test_isolation.py
            │       └── tests/unit/llm/test_response_validation.py
            │
            └──► Phase 3: P0-2 Evaluator 上下文补完
                    └── tests/unit/prompts/test_contract_builder.py
```

---

## 下一步行动

1. **开始 Phase 1 实施**
   - 参考 `2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md`
   - 使用测试模板 `2026-03-17-tdd-test-templates.py` 中的 Template 1-3

2. **创建测试文件**
   ```bash
   cp docs/solution/2026-03-17-tdd-test-templates.py \
      tests/unit/tools/test_update_context_binding.py
   ```

3. **遵循 TDD 循环**
   - Red: 编写失败的测试
   - Green: 最小实现通过测试
   - Refactor: 重构代码

---

## 参考文档

所有相关文档现在都已相互引用，形成完整的文档网络：

1. **研究发现** -> `docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`
2. **TDD 主方案** -> `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
3. **实施路线图** -> `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-implementation-roadmap.md`
4. **测试模板** -> `docs/solution/2026-03-17-tdd-test-templates.py`
