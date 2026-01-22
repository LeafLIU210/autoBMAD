# autoBMAD Epic自动化工作流详细说明

**版本**: 2.1
**最后更新**: 2026-01-22

---

## 目录

1. [工作流概述](#1-工作流概述)
2. [autoBMAD Epic自动化系统](#2-autobmad-epic自动化系统)
3. [安装与配置](#3-安装与配置)
4. [使用指南](#4-使用指南)
5. [质量门控系统](#5-质量门控系统)
6. [Claude Code Skills集成](#6-claude-code-skills集成)
7. [故障排除](#7-故障排除)

---

## 1. 工作流概述

本项目采用 **autoBMAD Epic Automation** 作为核心工作流系统,它是一个完整的5阶段BMAD开发自动化工具。该系统以Python实现,集成了Claude Agent SDK,提供从故事创建到质量验证的完整自动化支持。

### 1.1 核心依赖

本项目依赖以下核心技术：

- **[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)** - AI代理编排和执行框架
- **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** - AI驱动的敏捷开发方法论
- **autoBMAD Epic Automation** - 完整的自动化工作流系统

### 1.2 核心特性

| 特性 | 描述 | 核心价值 |
|------|------|----------|
| **5阶段工作流** | SM-Dev-QA循环 + 质量门控 + 测试自动化 | 完整开发周期自动化 |
| **AI驱动创建** | SM Agent使用Claude SDK生成故事 | 智能化文档生成 |
| **质量门控** | Basedpyright类型检查 + Ruff代码风格 | 代码质量保证 |
| **测试自动化** | Pytest执行 | 测试质量保证 |
| **状态管理** | SQLite持久化存储 | 断点恢复能力 |
| **便携性** | 自包含解决方案 | 快速部署使用 |

### 1.3 工作流架构

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

---

## 2. autoBMAD Epic自动化系统

### 2.1 系统概述

**autoBMAD Epic Automation** 位于 `autoBMAD/epic_automation/` 目录,是实现BMAD开发方法论完全自动化的Python工作流系统。它通过Claude Agent SDK集成提供AI驱动的故事创建,并管理完整的5阶段开发周期。

### 2.2 核心架构

#### 主要组件

```
autoBMAD/epic_automation/
├── epic_driver.py          # 主编排器和CLI接口(异步Epic解析)
├── sm_agent.py            # Story Master代理(Claude SDK集成)
├── dev_agent.py           # 开发代理
├── qa_agent.py            # 质量保证代理
├── state_manager.py       # 状态持久化和跟踪(SQLite)
├── sdk_wrapper.py         # Claude SDK封装
├── log_manager.py         # 日志管理系统
├── base_agent.py          # Agent基类
└── README.md              # 详细文档
```

#### 支持目录

```
autoBMAD/epic_automation/
├── agents/                 # Agent配置文件
├── controllers/            # 控制器模块
├── core/                   # 核心功能模块
├── monitoring/             # 监控工具
├── reports/                # 报告生成
└── logs/                   # 日志输出
```

### 2.3 五阶段工作流详解

#### Phase 1: SM-Dev-QA循环

**Story Master (SM) Agent**:
- **Epic分析**: 使用正则表达式从Epic文档提取Story ID
- **AI故事创建**: 通过Claude Agent SDK生成完整故事文档
- **SDK集成**: 直接集成 `claude_agent_sdk.query()` 和 `ClaudeAgentOptions`
- **自动提示生成**: 构建格式化提示词
- **权限处理**: 自动设置 `permission_mode="bypassPermissions"`

**Development (Dev) Agent**:
- 根据规范实现故事
- 编写代码、测试和文档
- 遵循最佳实践和编码标准
- 更新故事文件进度

**Quality Assurance (QA) Agent**:
- 审查实现质量
- 验证验收标准
- 检查代码标准和测试
- 提供反馈和通过/失败决策

#### Phase 2: 质量门控

**Basedpyright类型检查**:
- **目的**: 静态类型检查捕获类型相关错误
- **重试逻辑**: 最多3次自动重试
- **自动修复**: Ruff可以自动修复许多问题
- **配置**: 通过 `pyproject.toml` 配置

**Ruff代码风格检查**:
- **目的**: 快速Python代码检查与自动修复
- **覆盖范围**: PEP 8、复杂度、导入等
- **自动修复**: 自动修复可修复的问题
- **性能**: 非常快,主要受I/O限制

#### Phase 3: 测试自动化

**Pytest执行**:
- **目的**: 运行测试套件中的所有测试
- **覆盖范围**: 单元测试、集成测试和E2E测试
- **报告**: 详细的测试报告和失败分析

#### Phase 4: 编排管理

**Epic Driver**:
- 管理完整的工作流执行
- 阶段门控和依赖管理
- 进度跟踪和状态更新
- 错误处理和恢复

#### Phase 5: 文档与测试

- 全面的文档编写
- 集成测试执行
- 用户指导和最佳实践

### 2.4 状态管理

#### SQLite持久化

**state_manager.py** 提供:
- 基于SQLite的状态存储
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

### 2.5 日志系统

**log_manager.py** 提供:
- 双写模式(文件+控制台)
- 结构化日志输出
- 按阶段和代理分类
- 详细的执行跟踪
- 错误和警告高亮

---

## 3. 安装与配置

### 3.1 系统要求

#### 必需软件

- **Python 3.12+**: 核心运行时
- **Claude Agent SDK**: AI代理功能(SM Agent故事创建)
- **Basedpyright>=1.1.0**: 类型检查工具
- **Ruff>=0.1.0**: 代码风格检查工具
- **Pytest>=7.0.0**: 测试框架

### 3.2 安装步骤

#### 1. 复制模板

```bash
# 复制epic_automation文件夹到项目目录
cp -r /path/to/epic_automation /your/project/autoBMAD/

# Windows
xcopy /E /I epic_automation \your\project\autoBMAD\epic_automation
```

#### 2. 创建虚拟环境(推荐)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### 3. 安装依赖

```bash
# 安装Claude Agent SDK
pip install claude_agent_sdk>=0.1.0

# 安装质量门控工具
pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0

# 或一次性安装所有依赖
pip install claude_agent_sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0
```

#### 4. 配置环境变量

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Linux/macOS
export ANTHROPIC_API_KEY="your_api_key_here"
```

#### 5. 创建任务指导文件

在 `.bmad-core/tasks/` 目录下创建:

```bash
mkdir -p .bmad-core/tasks
```

创建以下文件:
- `create-next-story.md` - SM Agent指导
- `develop-story.md` - Dev Agent指导
- `review-story.md` - QA Agent指导

#### 6. 验证安装

```bash
# 查看帮助信息
python autoBMAD/epic_automation/epic_driver.py --help

# 验证依赖
basedpyright --version
ruff --version
pytest --version
python -c "import claude_agent_sdk; print('Claude Agent SDK installed')"
```

### 3.3 配置文件

#### pyproject.toml

在项目根目录创建或更新 `pyproject.toml`:

```toml
[tool.basedpyright]
pythonVersion = "3.12"
typeCheckingMode = "basic"
reportMissingImports = true
reportMissingTypeStubs = true

[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "W", "I", "N", "UP", "YTT", "ANN", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PT", "Q", "RSE", "RET", "SLF", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PGH", "PL", "TRY", "FLY", "NPY", "PERF", "FURB", "LOG", "RUF"]
ignore = ["ANN101", "ANN102"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["S101", "ANN"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### 3.4 目录结构

完整的项目结构:

```
project/
├── autoBMAD/
│   └── epic_automation/     # 主自动化包
│       ├── epic_driver.py
│       ├── sm_agent.py
│       ├── dev_agent.py
│       ├── qa_agent.py
│       ├── state_manager.py
│       └── ...
├── .bmad-core/
│   └── tasks/              # 任务指导文件
│       ├── create-next-story.md
│       ├── develop-story.md
│       └── review-story.md
├── docs/
│   └── epics/              # Epic文档
│       └── my-epic.md
├── src/                    # 源代码
├── tests/                  # 测试代码
└── pyproject.toml          # 项目配置
```

---

## 4. 使用指南

### 4.1 基本使用

#### 处理Epic文件

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 运行完整5阶段工作流
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

### 4.2 CLI选项

#### 位置参数

- `epic_path` (必需): Epic Markdown文件路径

#### 可选标志

- `--max-iterations N`: 失败故事的最多重试次数(默认: 3)
- `--retry-failed`: 启用失败故事的自动重试
- `--verbose`: 启用详细日志输出
- `--concurrent`: 并行处理故事(实验性功能)
- `--no-claude`: 禁用Claude Code CLI集成(使用模拟模式)
- `--source-dir DIR`: 源代码目录(默认: "src")
- `--test-dir DIR`: 测试目录(默认: "tests")

#### 质量门控和测试选项

- `--skip-quality`: 跳过代码质量门控(basedpyright和ruff)
- `--skip-tests`: 跳过测试自动化(pytest)

### 4.3 使用示例

#### 示例1: 完整工作流含质量门控

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

这将处理 `my-epic.md` 中的所有故事,通过完整的5阶段工作流:
- Phase 1: SM-Dev-QA循环
- Phase 2: 质量门控(basedpyright + ruff)
- Phase 3: 测试自动化(pytest)
- 质量门控最多3次重试
- 测试自动化最多5次重试

#### 示例2: 跳过质量门控(快速开发)

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality
```

通过SM-Dev-QA循环和测试自动化处理故事,但跳过质量门控以加快开发迭代。

#### 示例3: 跳过测试自动化(快速验证)

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests
```

通过SM-Dev-QA循环和质量门控处理故事,但跳过测试自动化以快速验证。

#### 示例4: 同时跳过质量门控和测试

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --skip-tests
```

仅处理SM-Dev-QA循环,跳过质量门控和测试自动化,在初始开发期间实现最大速度。

#### 示例5: 启用自动重试

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --retry-failed --verbose
```

启用失败故事的自动重试并提供详细的日志输出。

### 4.4 Epic文档格式

#### Epic结构示例

```markdown
# Epic: 核心算法基础

## 概述

本 Epic 包含核心算法实现的基础故事。

## 故事列表

- **[Story 001: 数据结构实现](docs/stories/story-001.md)**
- **[Story 002: 算法优化](docs/stories/story-002.md)**
- **[Story 003: 测试覆盖](docs/stories/story-003.md)**

## Story 001: 数据结构实现

**作为** 开发者,
**我希望** 实现核心数据结构,
**以便** 支持后续算法开发。

**验收标准**:
- [ ] 实现链表结构
- [ ] 实现树结构
- [ ] 通过所有单元测试
```

### 4.5 工作流执行过程

1. **初始化**: epic_driver.py 解析CLI参数并初始化EpicDriver
2. **Epic解析**: 读取Epic Markdown文件并提取故事引用
3. **故事处理循环**: 对每个故事:
   - **SM阶段**: Story Master代理精化和验证故事
   - **Dev阶段**: Development代理根据规范实现故事
   - **QA阶段**: Quality Assurance代理验证实现
4. **重试逻辑**: 如果故事QA失败:
   - 如果启用 `--retry-failed`,则Dev阶段最多重试 `--max-iterations` 次
   - 如果禁用 `--retry-failed`,则标记故事为失败并继续处理
5. **状态管理**: state_manager.py 跟踪每个故事的状态
6. **报告**: 系统提供汇总统计和详细日志

---

## 5. 质量门控系统

### 5.1 Basedpyright类型检查

#### 功能特性

- **静态类型分析**: 捕获类型相关错误
- **配置灵活**: 通过 `pyproject.toml` 配置
- **增量检查**: 仅检查变更的文件
- **并发优化**: 快速检查大型代码库

#### 使用方法

```bash
# 单独运行basedpyright检查
basedpyright src/

# 或通过autoBMAD工作流自动执行
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

#### 配置示例

```toml
[tool.basedpyright]
pythonVersion = "3.12"
typeCheckingMode = "basic"
reportMissingImports = true
reportMissingTypeStubs = true
include = ["src"]
exclude = ["tests", "build"]
```

### 5.2 Ruff代码风格检查

#### 功能特性

- **快速检查**: 非常快的Python代码检查器
- **自动修复**: 自动修复可修复的问题
- **全面规则**: 支持PEP 8和更多规则
- **高性能**: 主要受I/O限制

#### 使用方法

```bash
# 检查并自动修复问题
ruff check --fix src/

# 格式化代码
ruff format src/

# 或通过autoBMAD工作流自动执行
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

#### 配置示例

```toml
[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "W", "I", "N"]
ignore = ["ANN101", "ANN102"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["S101", "ANN"]
```

### 5.3 Pytest测试执行

#### 功能特性

- **全面测试**: 运行单元、集成和E2E测试
- **详细报告**: 失败分析和详细输出
- **覆盖率**: 代码覆盖率统计
- **插件系统**: 丰富的插件生态

#### 使用方法

```bash
# 运行所有测试
pytest tests/ -v

# 带覆盖率
pytest tests/ --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_my_feature.py -v

# 或通过autoBMAD工作流自动执行
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

### 5.4 质量门控决策矩阵

| 状态 | 含义 | 后续操作 | 是否可继续 |
|------|------|----------|------------|
| **PASS** | 所有关键要求满足 | 无 | ✅ 是 |
| **CONCERNS** | 发现非关键问题 | 进入修复 | ⚠️ 谨慎进行 |
| **FAIL** | 发现关键问题 | 必须修复 | ❌ 否 |
| **WAIVED** | 问题已被确认和接受 | 记录理由 | ✅ 批准后可以 |

## 6. Claude Code Skills集成

autoBMAD系统可以作为Claude Code的Skill安装，实现AI助手直接调用工作流功能。

### 6.1 Skill概述

autoBMAD Skill封装了完整的5阶段工作流，使Claude Code能够：
- 自动处理Epic文档
- 执行SM-Dev-QA循环
- 运行质量门控检查
- 执行测试自动化
- 管理状态和生成报告

### 6.2 安装Skill

#### 方法1：使用安装脚本（推荐）

**Windows PowerShell:**
```powershell
.\autoBMAD\Skill\install_autoBMAD_skill.ps1
```

**Linux/macOS:**
```bash
chmod +x ./autoBMAD/Skill/install_autoBMAD_skill.sh
./autoBMAD/Skill/install_autoBMAD_skill.sh
```

#### 方法2：手动复制

```bash
# 创建skills目录
mkdir -p ~/.claude/skills

# 复制skill文件
cp autoBMAD/Skill/autoBMAD-epic-automation.skill ~/.claude/skills/
```

### 6.3 Skill文档

完整的Skill文档位于 `autoBMAD/Skill/` 目录：

| 文档 | 描述 |
|------|------|
| **[SKILL.md](../autoBMAD/Skill/SKILL.md)** | Skill完整参考文档，包含用法、选项、示例 |
| **[SKILL_INSTALLATION_GUIDE.md](../autoBMAD/Skill/SKILL_INSTALLATION_GUIDE.md)** | 详细安装指南，包含故障排除 |

### 6.4 使用Skill

#### 在Claude Code中调用

安装Skill后，可以在Claude Code对话中直接调用：

```
请使用autoBMAD工作流处理epic文件 docs/epics/my-epic.md
```

Claude Code将自动：
1. 识别autoBMAD-epic-automation Skill
2. 执行完整的5阶段工作流
3. 返回执行结果和报告

#### Skill提供的功能

- ✅ **完整工作流**: SM-Dev-QA循环 + 质量门控 + 测试自动化
- ✅ **智能重试**: 自动重试失败的阶段（可配置次数）
- ✅ **状态管理**: SQLite持久化，支持断点恢复
- ✅ **详细日志**: 双写模式（控制台+文件）
- ✅ **灵活配置**: 支持跳过质量门控或测试
- ✅ **错误报告**: JSON格式的详细错误信息

#### 常用调用模式

**完整工作流:**
```
请使用autoBMAD处理epic: docs/epics/feature-x.md，启用详细输出
```

**跳过质量门控（快速开发）:**
```
请用autoBMAD处理 docs/epics/feature-x.md，跳过质量检查
```

**仅运行SM-Dev-QA循环:**
```
请用autoBMAD处理 docs/epics/feature-x.md，跳过质量检查和测试
```

### 6.5 Skill配置

#### 环境变量

Skill需要以下环境变量：

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Linux/macOS
export ANTHROPIC_API_KEY="your_api_key_here"
```

#### CLI选项映射

Skill支持所有CLI选项，可以通过自然语言指定：

| CLI选项 | 自然语言描述 |
|---------|-------------|
| `--verbose` | "启用详细输出"、"显示详细日志" |
| `--skip-quality` | "跳过质量检查"、"不运行质量门控" |
| `--skip-tests` | "跳过测试"、"不运行测试" |
| `--max-iterations N` | "最多重试N次"、"迭代次数N" |
| `--source-dir DIR` | "源代码目录是DIR" |
| `--test-dir DIR` | "测试目录是DIR" |

### 6.6 Skill验证

#### 检查安装

```bash
# 验证skill文件存在
ls ~/.claude/skills/autoBMAD-epic-automation.skill

# 查看skill内容
unzip -l ~/.claude/skills/autoBMAD-epic-automation.skill
```

#### 测试Skill

在Claude Code中测试：

```
请显示autoBMAD skill的帮助信息
```

Claude应该能够识别并显示Skill的功能描述。

### 6.7 故障排除

#### 问题：Claude Code无法识别Skill

**解决方案:**
1. 确认skill文件位于正确位置：`~/.claude/skills/`
2. 重启Claude Code
3. 检查skill文件权限

#### 问题：Skill执行失败

**解决方案:**
1. 验证环境变量已设置：`echo $ANTHROPIC_API_KEY`
2. 检查autoBMAD系统是否存在：`ls autoBMAD/epic_automation/epic_driver.py`
3. 确认依赖已安装：`pip list | grep claude-agent-sdk`

#### 问题：Epic文件无法找到

**解决方案:**
1. 使用绝对路径指定epic文件
2. 确认当前工作目录正确
3. 检查文件是否存在：`ls docs/epics/your-epic.md`

---

## 7. 故障排除

### 7.1 常见问题

#### 问题: "Epic文件未找到"

**错误信息**:
```
ERROR - Epic file not found: docs/epics/my-epic.md
```

**解决方案**:
- 验证文件路径是否正确
- 确保文件存在
- 尝试使用绝对路径

#### 问题: "任务目录未找到"

**错误信息**:
```
WARNING - Tasks directory not found: .bmad-core/tasks
```

**解决方案**:
- 创建目录: `mkdir -p .bmad-core/tasks`
- 添加任务指导文件
- 系统将继续但功能减少

#### 问题: "Claude Agent SDK未安装"

**错误信息**:
```
ERROR - Claude Agent SDK not installed
```

**解决方案**:
```bash
pip install claude_agent_sdk>=0.1.0
python -c "import claude_agent_sdk; print('Installed successfully')"
```

#### 问题: "质量门控工具未找到"

**错误信息**:
```
WARNING - Quality gate tools not found
```

**解决方案**:
```bash
# 安装质量门控工具
pip install basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0

# 或使用 --skip-quality 跳过
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality
```

注意: 系统具有优雅降级 - 即使没有这些工具,也能继续运行,但QA能力会减少。

#### 问题: 故事未被处理

**症状**:
- Epic中未找到故事
- 故事存在但未被执行

**解决方案**:
- 验证Epic文件包含正确格式的故事引用
- 使用模式: `[Story xxx: ...](path)`
- 检查故事文件实际存在于引用路径

### 7.2 调试模式

对于详细调试,使用最大详细级别运行:

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose --max-iterations 1
```

这将:
- 显示所有DEBUG级别的日志信息
- 限制重试为1次以快速获取反馈
- 显示每个阶段的详细进度

### 7.3 常见问答

**Q: 能否在没有互联网的情况下运行工具?**
A: 不能,工具需要互联网访问以与Claude SDK通信。

**Q: 能否暂停和恢复处理?**
A: 可以,状态管理器持久化进度。您可以再次运行相同的命令继续。

**Q: 能否跳过已完成的故事?**
A: 可以,系统自动跳过标记为"已完成"的故事。

**Q: 在同一个Epic上多次运行是否安全?**
A: 可以,工具设计为幂等,将跳过已完成的故事。

**Q: 能否自定义代理行为?**
A: 可以,修改 `.bmad-core/tasks/` 中的任务指导文件可以自定义代理行为。

---

## 最佳实践

### Epic组织
- 在单个Epic中分组相关故事
- 使用描述性Epic名称
- 保持Epic专注于单一功能或领域

### 故事结构
- 遵循BMAD故事模板
- 包含清晰的验收标准
- 将复杂任务分解为子任务

### 测试
- 从简单故事开始测试设置
- 使用 `--verbose` 标志进行调试
- 保留可工作Epic文件的备份

### 版本控制
- 提交Epic和故事文件到Git
- 不提交 `.ai/` 目录(包含临时状态)
- 跟踪任务指导文件的变更

### 状态管理
- 状态保存在 `.ai/` 目录
- 安全删除 `.ai/` 以重置状态
- Epic可以安全地重新运行

---

**参考文档**:
- [BMAD开发方法论](./bmad_methodology.md)
- [质量保证流程](./quality_assurance.md)
- [测试指南](./testing_guide.md)
- [autoBMAD README](../autoBMAD/epic_automation/README.md)
- [autoBMAD SETUP](../autoBMAD/epic_automation/SETUP.md)

---

**版本历史**:
- v2.2 (2026-01-22): 移除CI/CD集成，更新为autoBMAD工作流
- v2.1 (2026-01-14): 添加Claude Code Skills集成章节
- v2.0 (2026-01-14): 重写为autoBMAD Epic自动化工作流说明
- v1.0 (2026-01-04): 初始版本，包含BMAD-Workflow、BasedPyright-Workflow、Fixtest-Workflow
