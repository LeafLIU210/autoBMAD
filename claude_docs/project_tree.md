project/                       # 项目根目录
├── src/                        # 源代码
│   └── my_qt_app/              # 主程序包（命名用下划线）
│       ├── __init__.py
│       ├── __main__.py         # 程序入口：python -m my_qt_app
│       ├── main.py             # 启动逻辑（实例化QApplication）
│       ├── ui/                 # UI层
│       │   ├── __init__.py
│       │   ├── main_window.ui  # Qt Designer文件
│       │   ├── main_window.py  # UI逻辑（业务分离）
│       │   └── resources.qrc   # Qt资源文件（图标、图片）
│       ├── core/               # 核心业务逻辑（测试重点）
│       │   ├── __init__.py
│       │   ├── models.py       # 数据模型
│       │   ├── services.py     # 业务服务
│       │   └── config.py       # 配置管理
│       └── utils/              # 工具模块
│           ├── __init__.py
│           └── logger.py       # 日志处理
│
├── tests/                      # 测试目录（镜像src结构）
│   ├── __init__.py
│   ├── conftest.py             # pytest全局fixture
│   ├── fixtures/               # 测试固件（TDD关键）
│   │   ├── __init__.py
│   │   └── mock_qt_objects.py  # Mock的Qt组件
│   ├── unit/                   # 单元测试（无UI，快速）
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/            # 集成测试（含DB、文件）
│   │   └── test_config.py
│   └── gui/                    # GUI测试（用pytest-qt）
│       ├── __init__.py
│       └── test_main_window.py
│
├── autoBMAD/                   # autoBMAD工作流工具 ⭐
│   ├── epic_automation/        # Epic自动化系统（5阶段BMAD工作流）
│   │   ├── epic_driver.py      # 主编排器和CLI接口
│   │   ├── sm_agent.py         # Story Master代理
│   │   ├── dev_agent.py        # 开发代理
│   │   ├── qa_agent.py         # QA代理
│   │   ├── state_manager.py    # SQLite状态管理
│   │   ├── log_manager.py      # 双写日志系统
│   │   ├── controllers/        # 工作流控制器
│   │   ├── agents/             # Agent实现
│   │   ├── core/               # 基础设施（SDK执行器等）
│   │   ├── logs/               # 日志输出目录
│   │   └── README.md           # 详细文档
│   │
│   ├── docuswarm/              # 多智能体文档编排系统（LangGraph）
│   │   ├── main.py             # CLI入口
│   │   ├── pipeline/           # 流水线编排
│   │   ├── nodes/              # 节点系统
│   │   ├── agents/             # Agent实现（Independent + Evaluator）
│   │   ├── context/            # 上下文管理
│   │   ├── storage/            # 存储层
│   │   ├── llm/                # LLM集成（Kimi SDK）
│   │   ├── tools/              # 工具函数
│   │   ├── docuswarm.yaml      # 配置文件
│   │   └── README.md           # 详细文档
│   │
│   ├── nodes/                  # BMAD节点配置
│   │   ├── analyst/            # 业务分析师节点
│   │   │   ├── node.yaml
│   │   │   ├── persona.json
│   │   │   └── evaluator.yaml
│   │   ├── pm/                 # 项目经理节点
│   │   ├── ux/                 # UX设计师节点
│   │   ├── architect/          # 架构师节点
│   │   └── po/                 # 产品负责人节点
│   │
│   ├── agentdocs/              # Claude Agent SDK文档
│   └── Skill/                  # Claude Code Skill文件
│       ├── autoBMAD-epic-automation.skill
│       ├── SKILL.md
│       └── install_autoBMAD_skill.ps1
│
├── build/                      # Nuitka构建专用
│   ├── build.py                # 一键构建脚本
│   ├── build.spec              # Nuitka参数配置
│   ├── app.ico                 # Windows程序图标
│   └── version_info.py         # Windows版本信息（FILEVERSION等）
│
├── dist/                       # 打包输出（gitignore）
│   └── build.log               # 构建日志
│
├── docs/                       # 项目文档
│   └── epics/                  # Epic文档
│
├── claude_docs/                # 详细说明文档 ⭐
│   ├── core_principles.md
│   ├── bmad_methodology.md
│   ├── workflow_tools.md
│   ├── development_rules.md
│   ├── testing_guide.md
│   ├── quality_assurance.md
│   ├── technical_specs.md
│   ├── project_tree.md
│   ├── quick_reference.md
│   ├── ai_workflow.md
│   └── venv.md
│
├── .venv/                      # 虚拟环境（gitignore）
│
├── requirements.txt            # 生产依赖：PySide6, loguru
├── requirements-dev.txt        # 开发依赖：pytest, pytest-qt, nuitka, black
├── pyproject.toml              # 现代Python配置（pytest、black、mypy）
├── pytest.ini                  # pytest专用配置（Qt插件等）
├── .gitignore                  # Git忽略规则
├── .pre-commit-config.yaml     # 代码质量检查（可选但推荐）
├── README.md                   # 项目说明
└── CLAUDE.md                   # Claude Code指导文档
