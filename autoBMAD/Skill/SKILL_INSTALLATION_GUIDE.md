# autoBMAD-epic-automation Skill 安装指南

## 概述

本指南说明如何将 `autoBMAD-epic-automation` Skill 安装到新项目中。

## 📦 所需文件

### 核心文件
- **autoBMAD-epic-automation.skill** - Skill 包文件（2.9 KB）

### 完整系统文件
- **autoBMAD/** - Epic Automation 系统完整代码
- **autoBMAD/epic_automation/** - 主要自动化模块

## 🚀 快速安装

### 方法 1: 复制 Skill 文件（最简单）

```bash
# 1. 创建目录
mkdir -p your-project/.claude/skills

# 2. 复制 skill 文件
cp source-project/.claude/skills/autoBMAD-epic-automation.skill your-project/.claude/skills/

# 3. 复制 autoBMAD 系统（如果新项目没有）
cp -r source-project/autoBMAD your-project/
```

### 方法 2: 从 ZIP 文件安装

```bash
# 1. 解压 skill 文件
unzip autoBMAD-epic-automation.skill -d your-project/.claude/skills/

# 2. 重命名目录
mv your-project/.claude/skills/SKILL your-project/.claude/skills/autoBMAD-epic-automation
```

### 方法 3: 使用安装脚本

**Linux/macOS:**
```bash
chmod +x install_autoBMAD_skill.sh
./install_autoBMAD_skill.sh
```

**Windows PowerShell:**
```powershell
.\install_autoBMAD_skill.ps1
```

## 📋 验证安装

### 检查 Skill 文件
```bash
# 验证文件存在
ls -la .claude/skills/autoBMAD-epic-automation.skill

# 查看内容
unzip -l .claude/skills/autoBMAD-epic-automation.skill
```

### 测试运行
```bash
# 检查 autoBMAD 系统是否存在
ls autoBMAD/epic_automation/epic_driver.py

# 测试运行
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py --help
```

## ⚙️ 环境配置

### 1. 安装依赖
```bash
pip install claude-agent-sdk>=0.1.0 basedpyright>=1.1.0 ruff>=0.1.0 pytest>=7.0.0 debugpy>=1.6.0 loguru anyio
```

### 2. 设置环境变量
```bash
# Linux/macOS
export ANTHROPIC_API_KEY="your_api_key_here"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"
```

## 📁 项目结构

安装后，您的项目应包含：

```
your-project/
├── .claude/
│   └── skills/
│       └── autoBMAD-epic-automation.skill  ← Skill 文件
├── autoBMAD/
│   └── epic_automation/
│       ├── epic_driver.py                 ← 主程序
│       ├── agents/                        ← AI 代理
│       ├── controllers/                   ← 控制器
│       └── ...
├── docs/epics/                            ← Epic 文档（推荐）
├── .bmad-core/tasks/                      ← 任务指导（推荐）
└── src/                                   ← 源代码
```

## 🎯 使用方法

### 完整工作流
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

### 跳过质量门控（快速开发）
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-quality --verbose
```

### 跳过测试（快速验证）
```bash
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --skip-tests --verbose
```

## 🔧 故障排除

### 问题: "Skill 文件未找到"
**解决方案**: 确保 `.claude/skills/autoBMAD-epic-automation.skill` 存在

### 问题: "无法导入 autoBMAD 模块"
**解决方案**: 确保 `autoBMAD/` 目录存在，或设置 `PYTHONPATH=.`

### 问题: "找不到 epic_driver.py"
**解决方案**: 确保路径正确 `autoBMAD/epic_automation/epic_driver.py`

## 📊 文件大小参考

| 文件 | 大小 | 描述 |
|------|------|------|
| autoBMAD-epic-automation.skill | 2.9 KB | Skill 包文件 |
| autoBMAD/ | ~200 KB | 完整系统 |
| autoBMAD/epic_automation/ | ~150 KB | 核心模块 |

## 🎓 示例 Epic 文件

创建示例 epic 文件：`docs/epics/example.md`

```markdown
# Epic: 示例功能

## Stories
- [Story 001: 功能实现](docs/stories/story-001.md)
- [Story 002: 测试编写](docs/stories/story-002.md)
```

## ✅ 安装验证清单

- [ ] Skill 文件存在于 `.claude/skills/`
- [ ] autoBMAD 系统已复制
- [ ] 依赖包已安装
- [ ] API 密钥已设置
- [ ] 测试命令运行成功
- [ ] Epic 文档已创建

## 📞 支持

如有问题，请检查：
1. Skill 文件完整性
2. 依赖版本兼容性
3. 环境变量设置
4. Python 版本（需要 3.12+）

---

**Skill 名称**: autoBMAD-epic-automation
**版本**: 1.0
**兼容性**: Python 3.12+ | Claude Agent SDK
