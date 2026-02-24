# BMAD 开发方法论详细说明

**版本**: 1.1
**最后更新**: 2026-02-24

---

## 目录

1. [BMAD核心概念](#1-bmad核心概念)
2. [开发轨道](#2-开发轨道)
3. [四阶段开发周期](#3-四阶段开发周期)
4. [核心代理团队](#4-核心代理团队)
5. [完整开发流程](#5-完整开发流程)
6. [BMAD-Workflow自动化系统](#6-bmad-workflow自动化系统)
7. [状态跟踪工作流](#7-状态跟踪工作流)

---

## 1. BMAD核心概念

### 1.1 Agents (智能代理)

BMAD的基石，包含两种类型：

#### Simple Agents (简单代理)
- **特点**: 自包含，单文件设计
- **功能**: 专注单一任务，无需配置
- **适用场景**: 代码审查、文档生成、提交信息等

#### Expert Agents (专家代理)
- **特点**: 配备侧车文件夹(sidecar)
- **功能**: 持久化记忆，跨会话保持上下文
- **优势**: 领域专家，支持复杂多阶段任务
- **适用场景**: 架构师、产品经理、游戏设计师等

### 1.2 Workflows (工作流)

结构化的渐进式流程，具有以下特征：

- **逐步披露**: 每步仅知道下一步骤
- **交互式菜单驱动**: 支持[A]高级、[P]聚会、[C]继续等选项
- **可组合**: 工作流步骤可调用其他工作流
- **LLM强化**: 关键规则在各步骤中重复强化

---

## 2. 开发轨道

### 2.1 三轨并行开发模式

```
Quick Flow ──────→ 快速实施（技术规范）
     ↓
BMad Method ─────→ 完整规划（PRD + 架构 + UX）
     ↓
Enterprise Method → 扩展规划（安全 + DevOps + 测试）
```

#### Quick Flow (快速流)
- **适用**: 简单功能、技术验证
- **产出**: Tech-Spec（技术规范）
- **周期**: 1-2天

#### BMM (Breakthrough Method of Agile AI-driven Method)
- **适用**: 中等复杂度功能
- **产出**: PRD + 架构设计 + UX文档
- **周期**: 3-5天

#### Enterprise Method (企业方法)
- **适用**: 复杂系统、企业级功能
- **产出**: 完整规划 + 安全设计 + DevOps + 测试策略
- **周期**: 1-2周

---

## 3. 四阶段开发周期 (BMM)

### Phase 1: Analysis (分析) - 可选
- **目标**: 头脑风暴、产品简报、研究
- **工具**: 创意和策略工具
- **产出**: 需求收集、市场分析、竞品研究
- **持续时间**: 1-2天

### Phase 2: Planning (规划) - 必需
- **目标**: 制定详细计划
- **产出**:
  - **Quick Flow**: Tech-Spec (技术规范)
  - **BMM/企业**: PRD (产品需求文档)
  - **UX设计文档**（可选）
- **持续时间**: 1天

### Phase 3: Solutioning (解决方案) - 依赖轨道
- **目标**: 架构设计和实现方案
- **产出**:
  - **架构设计**（BMM/企业轨道必需）
  - 史诗创建
  - 故事拆解
- **持续时间**: 1-2天

### Phase 4: Implementation (实施) - 必需
- **目标**: 开发和交付
- **产出**:
  - 冲刺规划
  - 故事级开发
  - 代码审查
- **持续时间**: 2-5天

---

## 4. 核心代理团队

| 代理 | 角色 | 主要功能 | 使用时机 | 关键命令 |
|------|------|----------|----------|----------|
| `analyst` | 业务分析师 | 市场研究、需求收集 | 项目规划、竞品分析 | `/analyst` |
| `pm` | 产品经理 | PRD创建、功能优先级 | 战略规划、路线图 | `/pm create-doc prd` |
| `architect` | 解决方案架构师 | 系统设计、技术架构 | 复杂系统、可扩展性规划 | `/architect create-doc architecture` |
| `dev` | 开发者 | 代码实现、调试 | 所有开发任务 | `@dev` |
| `qa` | QA专家 | 测试规划、质量保证 | 测试策略、bug验证 | `@qa *review` |
| `ux-expert` | UX设计师 | UI/UX设计、原型 | 用户体验、界面设计 | `@ux-expert` |
| `po` | 产品负责人 | 积压管理、故事验证 | 故事完善、验收标准 | `@po` |
| `sm` | 敏捷大师 | 冲刺规划、故事创建 | 项目管理、工作流 | `@sm *create` |

---

## 5. 完整开发流程

### 5.1 规划阶段 (Web UI推荐 - 尤其推荐Gemini!)

#### 标准流程
1. **业务分析** (可选): `/analyst` - 市场研究、竞品分析
2. **项目简报**: 创建基础文档
3. **PRD创建**: `/pm create-doc prd` - 全面的产品需求
4. **架构设计**: `/architect create-doc architecture` - 技术基础
5. **验证与对齐**: `/po` 运行主检查清单
6. **文档准备**: 将最终文档复制到项目

#### 输出要求
- PRD文档：`docs/prd.md`
- 架构文档：`docs/architecture.md`
- 故事列表：`docs/stories/`

### 5.2 IDE开发工作流

#### 前置条件
规划文档必须存在于`docs/`文件夹中。

#### 关键步骤：文档分片
文档必须被分片以便开发：
- `docs/prd.md` → `docs/prd/` 文件夹
- `docs/architecture.md` → `docs/architecture/` 文件夹

#### 开发周期（顺序进行，一次一个故事）

**步骤1 - 故事创建**:
```
新聊天 → 选择强大模型 → @sm → *create
```
- SM执行创建下一个故事任务
- 在`docs/stories/`中审查生成的故事
- 状态从"Draft"更新为"Approved"

**步骤2 - 故事实现**:
```
新聊天 → @dev
```
- 代理询问要实现哪个故事
- 开发者遵循任务/子任务，完成后标记
- 开发者维护所有更改的文件列表
- 所有测试通过后，开发者标记故事为"Review"

**步骤3 - 高级QA审查**:
```
新聊天 → @qa → 执行审查故事任务
```
- QA执行高级开发者代码审查
- QA可以直接重构和改进代码
- QA将结果追加到故事的QA Results部分
- 如果批准: 状态 → "Done"
- 如果需要更改: 状态保持"Review"，为开发者标记未完成项目

**步骤4 - 重复**: 继续SM → Dev → QA循环，直到所有史诗故事完成

#### 重要规则
一次只有一个故事在进行，按顺序工作直到所有史诗故事完成。

---

## 6. autoBMAD Epic Automation系统

### 6.1 系统概述

autoBMAD Epic Automation位于`autoBMAD/epic_automation/`目录，是实现BMAD方法论完全自动化的Python工作流系统。它通过Claude Agent SDK集成提供AI驱动的故事创建，并管理完整的5阶段开发周期。

### 6.2 核心架构

#### 五层架构

```
┌─────────────────────────────────────┐
│   Epic Driver (编排层)              │  ← 入口点 + 工作流协调
├─────────────────────────────────────┤
│   Controllers (控制层)              │  ← 业务工作流编排
├─────────────────────────────────────┤
│   Agents (业务逻辑层)               │  ← 核心业务操作
├─────────────────────────────────────┤
│   Core (基础设施层)                 │  ← SDK执行器、取消管理器
├─────────────────────────────────────┤
│   State & Logging (状态与日志层)     │  ← StateManager、LogManager
└─────────────────────────────────────┘
```

#### 核心组件

| 组件 | 文件 | 主要职责 |
|------|------|----------|
| `EpicDriver` | `epic_driver.py` | 主编排器和CLI接口 |
| `SMController` | `controllers/sm_controller.py` | Story管理协调 |
| `DevQaController` | `controllers/devqa_controller.py` | Dev-QA循环协调 |
| `QualityCheckController` | `controllers/quality_check_controller.py` | 质量门控控制器 |
| `PytestController` | `controllers/pytest_controller.py` | 测试自动化控制器 |
| `SMAgent` | `agents/sm_agent.py` | Story创建（Claude SDK集成） |
| `DevAgent` | `agents/dev_agent.py` | 开发实现 |
| `QAAgent` | `agents/qa_agent.py` | 质量保证验证 |
| `StateManager` | `state_manager.py` | SQLite状态持久化 |
| `LogManager` | `log_manager.py` | 双写日志系统 |

### 6.3 五阶段自动化周期

#### 执行流程
```
┌─────────────────────────────────────────────────────────────┐
│                    EPIC处理流程                              │
└─────────────────────────────────────────────────────────────┘

Phase 1: SM-Dev-QA循环
├── Story创建 (SM Agent + Claude SDK)
├── 实现开发 (Dev Agent)
└── 验证审查 (QA Agent)
         ↓
Phase 2: 质量门控
├── Basedpyright类型检查
├── Ruff代码风格检查与自动修复
└── 最多3次重试机会
         ↓
Phase 3: 测试自动化
├── Pytest测试执行
└── 最多5次重试机会
         ↓
Phase 4: 编排管理
├── Epic Driver管理完整工作流
├── 阶段门控执行
└── 进度跟踪
         ↓
Phase 5: 文档与测试
├── 全面文档编写
├── 集成测试
└── 用户指导
```

#### 阶段详情

##### Phase 1: SM-Dev-QA循环
- **Story Master (SM) Agent**: 使用Claude SDK生成故事
- **Development (Dev) Agent**: 根据规范实现故事
- **Quality Assurance (QA) Agent**: 验证实现质量
- **状态驱动**: Story状态从markdown驱动执行决策

##### Phase 2: 质量门控
- **Basedpyright类型检查**: 静态类型分析
- **Ruff代码风格检查**: 快速linting与自动修复
- **重试逻辑**: 最多3次自动重试
- **状态**: PASS/CONCERNS/FAIL/WAIVED

##### Phase 3: 测试自动化
- **Pytest执行**: 运行测试套件中的所有测试
- **批量处理**: 高效的并行测试执行
- **重试逻辑**: 最多5次重试
- **Debugpy集成**: 持久失败的调试支持

##### Phase 4 & 5: 编排与文档
- **Epic Driver**: 管理工作流执行
- **状态持久化**: SQLite WAL模式
- **报告生成**: 详细执行报告

### 6.4 质量门控系统

#### 门控状态

| 状态 | 含义 | 后续操作 | 是否可继续 |
|------|------|----------|------------|
| **PASS** | 所有关键要求满足 | 无 | ✅ 是 |
| **CONCERNS** | 发现非关键问题 | 建议修复 | ⚠️ 谨慎进行 |
| **FAIL** | 发现关键问题 | 必须修复 | ❌ 否 |
| **WAIVED** | 问题已被确认和接受 | 记录理由 | ✅ 批准后可以 |

#### 门控决策因素
1. **测试覆盖率**: P0测试必须100%通过
2. **代码质量**: Basedpyright类型检查无ERROR
3. **代码风格**: Ruff检查无严重违规
4. **安全性**: 无安全漏洞或已处理
5. **性能**: NFR评估满足要求

### 6.5 配置管理

#### pyproject.toml配置
```toml
[tool.basedpyright]
pythonVersion = "3.12"
typeCheckingMode = "basic"

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
```

#### 环境变量
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Linux/macOS
export ANTHROPIC_API_KEY="your_api_key_here"
```

### 6.6 状态管理

#### SQLite持久化

**state_manager.py** 提供:
- 基于SQLite的状态存储（WAL模式）
- 故事状态跟踪
- 迭代计数
- QA结果记录
- 错误消息存储
- 断点恢复能力

#### 状态转换

```
PENDING → IN_PROGRESS → QA_REVIEW → 
├─ PASS → COMPLETED
└─ FAIL → IN_PROGRESS (重试) → ...
```

### 6.7 使用指南

#### 基本执行
```bash
# 完整5阶段工作流
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose

# 跳过质量门控（快速开发）
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality

# 跳过测试自动化（快速验证）
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests

# 独立质量门控
python -m autoBMAD.epic_automation.epic_driver run-quality --verbose
```

#### 高级选项
```bash
# 使用venv包装脚本（推荐）
autoBMAD/epic_automation/run_epic_with_venv.sh docs/epics/my-epic.md --verbose

# 自定义目录和选项
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md \
  --source-dir src \
  --test-dir tests \
  --max-iterations 5 \
  --verbose
```

### 6.8 日志系统

#### 日志结构
```
autoBMAD/epic_automation/logs/
├── epic_run_*.log (Epic执行日志)
├── quality_run.log (质量门控日志)
└── monitoring/ (监控日志)
```

#### 日志特性
- 双写模式（文件+控制台）
- 结构化日志输出
- 按阶段和代理分类
- 详细的执行跟踪
- 错误和警告高亮

### 6.9 测试框架

系统包含全面的测试套件：
- **单元测试**: 核心功能测试
- **集成测试**: 端到端工作流测试
- **CLI测试**: 命令行接口测试
- **Pytest兼容性**: 完整支持pytest特性

### 6.10 当前状态

**版本**: 3.0 (截至2026-01-14)

**实现状态**:
- ✅ Epic Driver编排层（100%完成）
- ✅ Controllers控制层（100%完成）
- ✅ Agents业务逻辑层（100%完成）
- ✅ Core基础设施层（100%完成）
- ✅ State & Logging层（100%完成）
- ✅ Claude Agent SDK集成（100%完成）
- ✅ 质量门控系统（100%完成）
- ✅ 测试自动化（100%完成）
- ✅ SQLite状态管理（100%完成）

**生产就绪性**: ✅ 已准备好投入生产使用

### 6.11 与旧BMAD-Workflow的关系

> **注意**: 旧的PowerShell-based BMAD-Workflow (位于`bmad-workflow/`目录)已被弃用，由Python实现的autoBMAD Epic Automation取代。
>
> 主要改进:
> - 从PowerShell迁移到Python，更好的跨平台支持
> - 集成Claude Agent SDK进行AI驱动的故事创建
> - 使用SQLite替代JSON文件进行状态持久化
> - 添加独立的Quality Gates命令 (`run-quality`)
> - 更灵活的CLI接口和配置选项

---

## 7. 状态跟踪工作流

### 7.1 故事状态

故事进度通过定义的状态流转：

```
Draft → Approved → InProgress → Review → Done
```

#### 状态说明

**Draft (草稿)**
- **创建者**: SM (Scrum Master)
- **说明**: 初始创建的故事，需要评审
- **下一步**: 需要PO或团队批准

**Approved (已批准)**
- **创建者**: PO或团队
- **说明**: 故事已通过评审，可以开始开发
- **下一步**: 开发人员开始实现

**InProgress (进行中)**
- **创建者**: Dev
- **说明**: 故事正在开发中
- **下一步**: 开发完成，标记为Review

**Review (审查中)**
- **创建者**: Dev
- **说明**: 开发完成，等待QA审查
- **下一步**: QA审查，可能返回InProgress或标记为Done

**Done (已完成)**
- **创建者**: QA
- **说明**: 所有要求满足，测试通过
- **下一步**: 关闭故事

### 7.2 状态转换规则

#### 转换触发器

| 从状态 | 到状态 | 触发者 | 条件 |
|--------|--------|--------|------|
| Draft | Approved | PO/团队 | 需求明确、验收标准确定 |
| Approved | InProgress | Dev | 开始开发 |
| InProgress | Review | Dev | 开发完成，测试通过 |
| Review | InProgress | QA | 发现问题需要修复 |
| Review | Done | QA | 所有要求满足 |

#### 转换要求

每次状态更改都需要：
1. **验证**: 当前状态的先决条件已满足
2. **记录**: 状态变更日志
3. **通知**: 相关团队成员
4. **批准**: 需要时由负责人批准

### 7.3 质量门控状态

与故事状态并行，系统还维护质量门控状态：

```
NotStarted → RunningDevFlows → QA_Pass → QA_Concerns → QA_Fail → WAIVED
```

#### 门控状态说明

**NotStarted (未开始)**
- 质量检查尚未开始

**RunningDevFlows (开发流程运行中)**
- Phase A或C正在执行

**QA_Pass (QA通过)**
- 所有质量要求满足，可以继续

**QA_Concerns (QA关注)**
- 发现非关键问题，建议修复

**QA_Fail (QA失败)**
- 发现关键问题，必须修复

**WAIVED (已豁免)**
- 问题已被确认和接受，记录理由

---

## 最佳实践

### 1. 故事管理
- 保持故事小而专注（1-2天工作量）
- 明确验收标准
- 及时更新状态

### 2. 团队协作
- 一次只处理一个故事
- 及时沟通问题
- 遵守状态转换规则

### 3. 质量保证
- 测试驱动开发
- 代码审查必须
- 持续集成

### 4. 工具使用
- 使用BMAD-Workflow自动化
- 定期审查质量门控
- 保持日志和状态文件

---

**参考文档**:
- [AI助手工作流程](./ai_workflow.md)
- [质量保证流程](./quality_assurance.md)
- [工作流工具集](./workflow_tools.md)

---

**版本历史**:
- v1.1 (2026-02-24): 更新第6章为autoBMAD Epic Automation Python系统（取代旧PowerShell BMAD-Workflow）
- v1.0 (2026-01-04): 初始版本，完整的BMAD方法论说明
