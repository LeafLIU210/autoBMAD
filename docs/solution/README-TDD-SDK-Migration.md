# TDD SDK 迁移方案文档集

**创建日期**: 2026-03-25  
**目标**: 通过测试驱动开发完成 kimi-agent-sdk 到 claude-agent-sdk 的迁移

---

## 文档清单

| 文档 | 用途 | 读者 |
|------|------|------|
| [TDD-SDK-Migration-2026-03-25.md](./TDD-SDK-Migration-2026-03-25.md) | 完整TDD方案 | 架构师、技术负责人 |
| [TDD-SDK-Migration-Implementation-Guide.md](./TDD-SDK-Migration-Implementation-Guide.md) | 详细实施步骤 | 开发人员 |
| [TDD-SDK-Migration-QuickRef.md](./TDD-SDK-Migration-QuickRef.md) | 快速参考卡片 | 日常开发 |
| [README-TDD-SDK-Migration.md](./README-TDD-SDK-Migration.md) | 本导航文档 | 所有人 |

---

## 快速导航

### 如果你是架构师/技术负责人
→ 阅读 [TDD-SDK-Migration-2026-03-25.md](./TDD-SDK-Migration-2026-03-25.md)
- 了解整体TDD策略
- 测试金字塔设计
- 迁移顺序规划
- CI/CD集成方案

### 如果你是开发人员
→ 阅读 [TDD-SDK-Migration-Implementation-Guide.md](./TDD-SDK-Migration-Implementation-Guide.md)
- Step-by-step 实施指南
- 代码示例（Before/After）
- 测试运行命令
- 常见问题解决

### 如果你正在进行迁移工作
→ 阅读 [TDD-SDK-Migration-QuickRef.md](./TDD-SDK-Migration-QuickRef.md)
- 导入替换速查表
- 类型替换速查表
- 每日命令
- 快速调试技巧

---

## TDD 流程概览

```
Red → Green → Refactor
  ↑___________|

1. RED: 编写测试，验证失败
   pytest tests/... -v  # 应该失败

2. GREEN: 实现代码，使测试通过
   # 修改代码

3. REFACTOR: 重构优化
   # 清理代码，保持测试通过

4. REGRESSION: 回归测试
   pytest tests/ -v  # 确保无回归
```

---

## 迁移范围

### 必须迁移的文件 (7个)

```
autoBMAD/docuswarm/
├── llm/
│   ├── session_manager.py      ← 最关键，618行
│   └── approval.py
├── pipeline/
│   └── orchestrator.py
├── tools/
│   ├── sdk_adapter.py
│   └── callable_tool_wrapper.py
└── agents/
    ├── independent.py
    └── evaluator.py
```

### 需要创建的测试文件 (6个)

```
tests/
├── llm/
│   └── test_session_manager_tdd.py      # Phase 2
├── tools/
│   ├── test_sdk_adapter_tdd.py          # Phase 3
│   └── test_callable_tool_wrapper_tdd.py # Phase 3
├── agents/
│   ├── test_independent_agent_tdd.py    # Phase 4
│   └── test_evaluator_agent_tdd.py      # Phase 4
└── cli/
    └── test_cli_integration_tdd.py      # Phase 5
```

---

## 时间估算

| 阶段 | 内容 | 预估时间 |
|------|------|---------|
| Phase 1 | 基础设施 | 2-4小时 |
| Phase 2 | SessionManager | 4-6小时 |
| Phase 3 | 工具系统 | 3-4小时 |
| Phase 4 | Agent层 | 3-4小时 |
| Phase 5 | 集成验证 | 2-3小时 |
| **总计** | | **14-21小时 (2-3天)** |

---

## 验收标准

- [ ] 所有TDD测试通过
- [ ] `migration_tracker.py --check` 通过
- [ ] Drift Score = 0
- [ ] 原始测试套件通过率 ≥ 95%
- [ ] E2E测试通过
- [ ] 代码审查通过

---

## 相关资源

### 研究文档
- [dependency-drift-2026-03-25](../research/dependency-drift-2026-03-25/) - 依赖漂移研究报告

### 工具
- `tools/dependency_analysis/dependency_drift_analyzer.py` - 漂移分析
- `tools/dependency_analysis/migration_tracker.py` - 进度跟踪

### 参考实现
- `autoBMAD/epic_automation/sdk_wrapper.py` - claude-agent-sdk 正确用法

---

## 更新日志

- **2026-03-25**: 初始版本，创建完整TDD方案文档集

---

**维护**: 迁移完成后更新此文档状态
