# BMAD Epic Automation 重构迁移策略

**文档版本**: 1.0  
**创建日期**: 2026-01-11  
**状态**: Draft

---

## 1. 迁移概览

### 1.1 迁移目标

**主要目标**：
1. 彻底消除 Cancel Scope 跨 Task 错误
2. 统一使用 AnyIO 框架
3. 实现五层架构设计
4. 保持业务功能不变

**技术目标**：
- 每个 SDK 调用在独立 TaskGroup 中
- 引入控制器层和 Agent 层
- 实现结构化并发和 RAII 资源管理
- 不向后兼容（破坏性重构）

### 1.2 迁移范围

**需要重构的模块**：
```
autoBMAD/epic_automation/
├── epic_driver.py          → 重构为 EpicDriver + Controllers
├── sm_agent.py             → 重构为 SMController + SMAgent
├── dev_agent.py            → 重构为 DevAgent (新接口)
├── qa_agent.py             → 重构为 QAAgent (新接口)
├── sdk_session_manager.py  → 废弃，功能合并到 SDKExecutor
├── sdk_wrapper.py          → 重构为 SDKExecutor + CancellationManager
├── quality_agents.py       → 重构为 QualityController + Quality Agents
└── story_parser.py         → 重构为 StateAgent
```

**新增模块**：
```
autoBMAD/epic_automation/
├── core/
│   ├── taskgroup_manager.py    # TaskGroup 管理
│   ├── sdk_executor.py          # SDK 执行层
│   └── cancellation_manager.py  # 取消管理
├── controllers/
│   ├── base_controller.py       # 控制器基类
│   ├── sm_controller.py         # SM 控制器
│   ├── devqa_controller.py      # Dev-QA 控制器
│   └── quality_controller.py    # 质量门控控制器
└── agents/
    ├── base_agent.py            # Agent 基类
    ├── sm_agent.py              # SM Agent (重构)
    ├── state_agent.py           # 状态解析 Agent (新)
    ├── dev_agent.py             # Dev Agent (重构)
    ├── qa_agent.py              # QA Agent (重构)
    └── quality_agents.py        # 质量 Agents (重构)
```

---

## 2. 迁移策略

### 2.1 迁移方式：Big Bang 重构

**选择理由**：
1. 不向后兼容，破坏性重构
2. 架构变化巨大，难以增量迁移
3. 新旧代码共存成本高
4. 重构范围有限，风险可控

**替代方案被拒绝的原因**：
- ❌ 增量迁移：新旧架构互斥，无法共存
- ❌ 并行开发：资源浪费，维护成本高
- ❌ 分支隔离：合并冲突过多

### 2.2 风险控制

**风险 1: 功能回归**

**控制措施**：
- 完整的 E2E 测试套件
- 业务流程验收测试
- 逐个 Story 验证

**风险 2: 性能退化**

**控制措施**：
- 性能基准测试
- TaskGroup 开销评估
- 关键路径优化

**风险 3: 集成问题**

**控制措施**：
- 分阶段集成
- 每阶段充分测试
- 快速回滚机制

---

## 3. 迁移阶段

### 3.1 阶段划分

```
Phase 0: 准备阶段 (1 天)
  └─ 环境准备、文档评审、测试基线

Phase 1: SDK 执行层 (3 天)
  └─ SDKExecutor + CancellationManager + SafeClaudeSDK

Phase 2: 控制器层 (3 天)
  └─ SMController + DevQaController + QualityController

Phase 3: Agent 层 (4 天)
  └─ 重构所有 Agent

Phase 4: 集成测试 (2 天)
  └─ E2E 测试 + 性能测试

Phase 5: 清理与优化 (2 天)
  └─ 删除旧代码 + 文档更新

总计: 15 天
```

### 3.2 Phase 0: 准备阶段

**时间**: 1 天

**目标**：
- 搭建测试环境
- 建立性能基线
- 创建测试数据

**任务清单**：
```
□ 安装 AnyIO (anyio>=4.0.0)
□ 创建测试 Epic 文件
□ 运行现有测试套件，建立基线
□ 记录当前性能指标
□ 评审架构文档
□ 团队培训 (AnyIO 基础)
```

**产出**：
- 测试环境就绪
- 性能基线报告
- 测试数据集

### 3.3 Phase 1: SDK 执行层

**时间**: 3 天

**目标**：
- 创建 SDK 执行层核心组件
- 实现 TaskGroup 隔离机制
- 验证 Cancel Scope 不跨 Task

**详细计划**：见 [02-phase1-sdk-executor.md](02-phase1-sdk-executor.md)

**关键里程碑**：
- Day 1: SDKExecutor 基础实现
- Day 2: CancellationManager 实现
- Day 3: 集成测试通过

### 3.4 Phase 2: 控制器层

**时间**: 3 天

**目标**：
- 创建控制器层框架
- 实现三个核心控制器
- 建立状态机流水线

**详细计划**：见 [03-phase2-controllers.md](03-phase2-controllers.md)

**关键里程碑**：
- Day 1: BaseController + SMController
- Day 2: DevQaController
- Day 3: QualityController

### 3.5 Phase 3: Agent 层

**时间**: 4 天

**目标**：
- 重构所有 Agent
- 统一 Agent 接口
- 集成 SDKExecutor

**详细计划**：见 [04-phase3-agents.md](04-phase3-agents.md)

**关键里程碑**：
- Day 1: BaseAgent + SMAgent
- Day 2: StateAgent + DevAgent
- Day 3: QAAgent
- Day 4: Quality Agents

### 3.6 Phase 4: 集成测试

**时间**: 2 天

**目标**：
- 完整 E2E 测试
- 性能验证
- Bug 修复

**详细计划**：见 [05-phase4-integration.md](05-phase4-integration.md)

**关键里程碑**：
- Day 1: E2E 测试套件执行
- Day 2: 性能测试 + Bug 修复

### 3.7 Phase 5: 清理与优化

**时间**: 2 天

**目标**：
- 删除旧代码
- 更新文档
- 性能优化

**详细计划**：见 [06-phase5-cleanup.md](06-phase5-cleanup.md)

**关键里程碑**：
- Day 1: 代码清理 + 文档更新
- Day 2: 性能优化 + 最终验证

---

## 4. 人员分工

### 4.1 角色定义

**架构师 (Architect)**：
- 设计审查
- 关键决策
- 风险评估

**开发工程师 (Developer)**：
- 编码实现
- 单元测试
- 代码审查

**测试工程师 (QA)**：
- 测试用例设计
- E2E 测试执行
- Bug 验证

**技术文档工程师 (Doc)**：
- 文档编写
- 示例代码
- 培训材料

### 4.2 分工方案

**Phase 1: SDK 执行层**
- 开发工程师 (2人): 实现核心组件
- 测试工程师 (1人): 单元测试
- 架构师 (1人): 设计审查

**Phase 2: 控制器层**
- 开发工程师 (2人): 实现控制器
- 测试工程师 (1人): 集成测试
- 架构师 (1人): 代码审查

**Phase 3: Agent 层**
- 开发工程师 (3人): 并行重构 Agents
- 测试工程师 (1人): Agent 测试
- 架构师 (1人): 接口审查

**Phase 4: 集成测试**
- 测试工程师 (2人): E2E 测试
- 开发工程师 (2人): Bug 修复
- 架构师 (1人): 质量把控

**Phase 5: 清理与优化**
- 开发工程师 (1人): 代码清理
- 文档工程师 (1人): 文档更新
- 架构师 (1人): 最终验收

---

## 5. 测试策略

### 5.1 测试金字塔

```
        /\
       /  \        E2E Tests (10%)
      /────\       - 完整业务流程
     /      \      - 性能测试
    /────────\     
   /          \    Integration Tests (30%)
  /────────────\   - 模块间集成
 /              \  - 控制器-Agent 集成
/────────────────\ 
     Unit Tests    Unit Tests (60%)
                   - 单个类/函数
                   - Mock 外部依赖
```

### 5.2 测试类型

**单元测试 (60%)**：
- 每个类独立测试
- Mock 所有外部依赖
- 覆盖率 > 80%

**集成测试 (30%)**：
- Controller + Agent 集成
- Agent + SDKExecutor 集成
- TaskGroup 隔离验证

**E2E 测试 (10%)**：
- 完整 Story 处理流程
- SM + Dev-QA + Quality 全流程
- 性能和稳定性测试

### 5.3 测试优先级

**P0 (必须通过)**：
- Cancel Scope 隔离测试
- 资源清理验证
- 核心业务流程

**P1 (重要)**：
- 异常处理测试
- 状态机流水线
- 并发场景

**P2 (可选)**：
- 边界条件测试
- 性能压测
- 兼容性测试

---

## 6. 回滚计划

### 6.1 回滚触发条件

**立即回滚**：
- 核心功能完全失败
- 数据损坏或丢失
- 严重性能退化 (>50%)

**计划回滚**：
- 关键 Bug 无法修复
- 测试通过率 < 70%
- 性能退化 > 30%

### 6.2 回滚步骤

**Step 1: 停止新代码部署**
```bash
# 切换到旧代码分支
git checkout old-stable-branch
```

**Step 2: 恢复依赖**
```bash
# 恢复旧的依赖版本
pip install -r requirements.old.txt
```

**Step 3: 验证回滚**
```bash
# 运行测试套件
pytest tests/
```

**Step 4: 通知团队**
- 发送回滚通知
- 说明回滚原因
- 制定修复计划

### 6.3 最小化回滚影响

**策略 1: 分支隔离**
```bash
# 开发分支
git checkout -b refactor/anyio-architecture

# 保持 main 分支稳定
# 只有通过所有测试才合并
```

**策略 2: Feature Flag**
```python
# 使用配置控制新旧代码
if USE_NEW_ARCHITECTURE:
    from epic_automation.new import EpicDriver
else:
    from epic_automation.old import EpicDriver
```

**策略 3: 快照备份**
```bash
# 重构前创建完整备份
git tag -a v1.0-backup -m "Pre-refactor backup"
```

---

## 7. 成功标准

### 7.1 功能标准

**必须满足**：
- ✅ 所有现有功能正常工作
- ✅ 核心业务流程无回归
- ✅ Cancel Scope 错误完全消除

**期望达到**：
- ✅ 代码可读性提升
- ✅ 错误处理简化
- ✅ 可维护性改善

### 7.2 性能标准

**必须满足**：
- ✅ 性能退化 < 10%
- ✅ 内存占用无明显增加
- ✅ SDK 调用成功率 > 95%

**期望达到**：
- ✅ 确定性同步点，无需时间等待
- ✅ 并行处理能力提升
- ✅ 资源利用率优化

### 7.3 质量标准

**代码质量**：
- ✅ 单元测试覆盖率 > 80%
- ✅ 集成测试通过率 = 100%
- ✅ E2E 测试通过率 = 100%
- ✅ 代码审查通过
- ✅ 静态分析无 Critical 问题

**文档质量**：
- ✅ 架构文档完整
- ✅ API 文档齐全
- ✅ 示例代码可运行
- ✅ 故障排查指南

---

## 8. 时间表

### 8.1 甘特图

```
Week 1:
Mon  Tue  Wed  Thu  Fri
[P0] [P1────────────]

Week 2:
Mon  Tue  Wed  Thu  Fri
[────P1] [P2────────]

Week 3:
Mon  Tue  Wed  Thu  Fri
[P3──────────────]

Week 4:
Mon  Tue  Wed  Thu  Fri
[P4─────] [P5─────]

P0: 准备阶段 (1天)
P1: SDK 执行层 (3天)
P2: 控制器层 (3天)
P3: Agent 层 (4天)
P4: 集成测试 (2天)
P5: 清理优化 (2天)
```

### 8.2 里程碑

**M1 (Week 1 结束)**：SDK 执行层完成
- SDKExecutor 可用
- 单元测试通过
- TaskGroup 隔离验证

**M2 (Week 2 结束)**：控制器层完成
- 三个控制器可用
- 集成测试通过
- 状态机流水线验证

**M3 (Week 3 结束)**：Agent 层完成
- 所有 Agent 重构完成
- Agent 测试通过
- 完整链路可用

**M4 (Week 4 中)**：集成测试通过
- E2E 测试通过
- 性能测试达标
- Bug 清零

**M5 (Week 4 末)**：重构完成
- 旧代码清理
- 文档更新
- 正式发布

---

## 9. 沟通计划

### 9.1 每日站会

**时间**: 每天 10:00 AM

**内容**：
- 昨日完成情况
- 今日计划任务
- 遇到的问题
- 需要的协助

### 9.2 周报

**时间**: 每周五 17:00

**内容**：
- 本周完成情况
- 关键里程碑达成
- 风险和问题
- 下周计划

### 9.3 审查会议

**Phase 审查**：每个 Phase 结束后

**内容**：
- Phase 目标达成情况
- 测试结果评审
- 代码审查
- Go/No-Go 决策

---

## 10. 后续工作

### 10.1 重构后优化

**性能优化**：
- 识别性能热点
- 优化 TaskGroup 使用
- 缓存和预加载

**可观测性**：
- 添加详细日志
- 指标采集
- 监控仪表盘

**可扩展性**：
- 插件机制
- 配置热更新
- 动态 Agent 注册

### 10.2 长期改进

**架构演进**：
- 支持分布式执行
- 引入消息队列
- 微服务化

**功能增强**：
- 更多 Agent 类型
- 自定义 Prompt 模板
- 工作流可视化

---

**下一步**：阅读 [02-phase1-sdk-executor.md](02-phase1-sdk-executor.md) 了解 Phase 1 详细计划
