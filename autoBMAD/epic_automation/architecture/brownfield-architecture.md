# autoBMAD Epic Automation - Brownfield Architecture Document

**Version**: 3.0  
**Date**: 2026-01-14  
**Status**: Current Production Implementation

---

## Document Purpose

This document captures the **ACTUAL STATE** of the autoBMAD Epic Automation system as implemented in `autoBMAD/epic_automation/`. It documents real code patterns, technical debt, workarounds, and integration points - NOT idealized architecture.

**Use this document when**:
- Understanding how the system actually works
- Planning enhancements or refactoring
- Debugging issues
- Onboarding new developers

---

## 核心工作流程 - 实际执行顺序

### 完整流程图

```
用户执行命令
    ↓
epic_driver.py main()
    ↓
parse_epic() - 解析Epic文件，提取故事ID
    ↓
    ├─→ 匹配story files (4种fallback策略)
    ├─→ 如果文件不存在 → SMAgent.create_stories()
    └─→ parse_status_sync() 解析每个故事状态
    ↓
run_epic() - 主循环
    ↓
对每个story:
    ↓
    StateAgent.parse_status() - 从markdown解析当前状态
    ↓
    根据状态决定执行阶段:
    ├─→ "Draft" / "Ready" → execute_sm_phase()
    │       ↓
    │       SMController.execute()
    │       ↓
    │       SMAgent 通过 SafeClaudeSDK 生成/细化故事
    │       ↓
    │       StatusUpdateAgent 更新故事状态
    │
    ├─→ "Ready for Development" → execute_dev_phase()
    │       ↓
    │       DevQaController.execute()
    │       ↓
    │       循环 (最多 max_iterations):
    │       ├─→ DevAgent 实现代码
    │       ├─→ QAAgent 验证
    │       └─→ 如果QA通过 → StatusUpdateAgent 更新状态
    │
    └─→ "Ready for Done" / "Done" → 继续下一个故事
    ↓
所有故事处理完成后:
    ↓
execute_quality_gates() - 质量门控
    ↓
QualityGateOrchestrator.execute_quality_gates()
    ↓
    Phase 1: Ruff Check (max_cycles=3)
    ├─→ QualityCheckController.run()
    ├─→ RuffAgent.check()
    └─→ 如果有错误 → SDK fix → 回归检查
    ↓
    Phase 2: BasedPyright Check (max_cycles=3)
    ├─→ QualityCheckController.run()
    ├─→ BasedPyrightAgent.check()
    └─→ 如果有错误 → SDK fix → 回归检查
    ↓
    Phase 3: Ruff Format (最终格式化)
    └─→ RuffAgent.format()
    ↓
    Phase 4: Pytest (max_cycles=3)
    ├─→ PytestController.run()
    ├─→ PytestAgent.execute()
    └─→ 如果失败 → SDK fix → 重新运行
    ↓
    如果达到max_cycles但仍有错误:
    ├─→ 返回 success=True (非阻断)
    ├─→ 记录 quality_warnings
    └─→ 生成 errors/quality_errors_*.json
    ↓
Epic完成
```

---

## 关键数据流 - 状态解析机制

### 状态解析流程 (StateAgent)

```python
# 1. 从markdown文件解析核心状态
story_path = "docs/stories/004.1-story.md"
↓
StateAgent.parse_status(story_path)
↓
尝试AI解析 (使用SafeClaudeSDK):
├─→ 成功 → 返回核心状态值
└─→ 失败 → 正则表达式回退
    ↓
    搜索模式: **Status**: {status_value}
    ↓
    提取状态值

# 2. 核心状态值到处理状态映射
core_status = "Ready for Development"
↓
core_status_to_processing(core_status)
↓
返回: "pending"

# 3. EpicDriver 根据核心状态决定执行
if core_status in ["Draft", "Ready"]:
    await execute_sm_phase()
elif core_status == "Ready for Development":
    await execute_dev_phase()
elif core_status in ["Ready for Done", "Done"]:
    continue  # 跳过此故事
```

**关键点**:
- 状态值来源于**markdown文件本身**，不是仅从数据库
- AI解析失败时有正则回退 (性能vs准确性权衡)
- 核心状态值驱动整个工作流决策

---

## 技术债务与已知问题

### 1. EpicDriver 过大 (2601行)

**问题**:
- 单个文件包含太多职责
- 难以维护和测试
- 违反单一职责原则

**影响**:
- 修改任何功能都需要理解整个文件
- 单元测试覆盖率低
- 重构风险高

**建议**:
- 将 QualityGateOrchestrator 提取到独立文件
- 故事匹配逻辑 (_find_story_file_with_fallback) 移至 doc_parser.py
- 创建独立的 EpicParser 类

### 2. 超时配置废弃但未清理

**位置**: epic_driver.py lines 48-53

```python
# 超时配置常量 - DEPRECATED: External timeouts removed - using max_turns instead
STORY_TIMEOUT = None  # 4小时 = 240分钟（整个故事的所有循环）
CYCLE_TIMEOUT = None  # 90分钟（单次Dev+QA循环）
DEV_TIMEOUT = None  # 45分钟（开发阶段）
QA_TIMEOUT = None  # 30分钟（QA审查阶段）
SM_TIMEOUT = None  # 30分钟（SM阶段）
```

**问题**: 已废弃但仍保留在代码中，造成混淆

**建议**: 删除这些常量，注释说明改用 max_turns 限制

### 3. 连接池可耗尽 (StateManager)

**问题**:
- DatabaseConnectionPool 只有5个连接
- 获取超时仅5秒
- 高并发下可能耗尽

**影响**:
- `RuntimeError: Database connection pool exhausted`
- 需要重试或失败

**缓解**:
- 使用连接池时确保及时释放
- 增加池大小（需权衡内存）
- 添加连接池监控

### 4. 状态解析双路径复杂性

**问题**:
- StateAgent 同时支持 AI 解析和正则回退
- 增加代码复杂度
- 难以预测使用哪种方式

**权衡**:
- **优点**: AI失败时仍能工作
- **缺点**: 维护两套逻辑

**建议**: 添加配置选项明确选择解析策略

### 5. 日志文件无自动轮换

**问题**:
- logs/ 目录下文件持续累积
- 需要手动清理
- 可能占用大量磁盘空间

**临时方案**:
- 定期手动删除旧日志
- 或设置 create_log_file=False (仅控制台)

**长期方案**: 实现日志轮换（按大小或时间）

### 6. Windows路径硬编码

**问题**:
- 部分路径处理假设Windows环境
- `_convert_to_windows_path()` 方法针对WSL/Unix转换

**影响**: 跨平台兼容性有限

**建议**: 使用 pathlib 处理所有路径

---

## 关键约束与限制

### 必须遵守的约定

1. **故事状态更新必须通过 StatusUpdateAgent**
   - 不要直接修改markdown文件
   - 不要直接调用 StateManager.update_story_status() 来修改逻辑流程
   - StatusUpdateAgent 是单一真相源

2. **SDK调用必须在独立 TaskGroup 中**
   - 每个 `anyio.create_task_group()` 包装一次SDK调用
   - 避免 cancel scope 跨任务传播
   - 参考: execute_sm_phase, execute_dev_phase

3. **Quality Gates 达到max_cycles返回success=True**
   - 质量门控超限时不阻断流程
   - 生成警告和错误JSON
   - 不要改为返回False (会中断epic执行)

4. **数据库操作使用乐观锁**
   - 所有 update 操作必须检查 version 列
   - 版本冲突需要重试
   - 不要禁用版本检查

5. **Epic文件必须在 docs/epics/ 目录**
   - 故事文件查找逻辑依赖此结构
   - 故事文件位于 docs/stories/
   - 改变目录结构需要同时修改匹配逻辑

---

## 集成点与外部依赖

### Claude SDK 集成

**配置要求**:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Linux/Mac
export ANTHROPIC_API_KEY="your_api_key_here"

# 可选: 启用调试日志
export ANTHROPIC_LOG=debug
```

**调用模式**:
```python
# SafeClaudeSDK 封装 (sdk_wrapper.py)
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

sdk = SafeClaudeSDK(
    prompt="Generate story from epic",
    options=ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        cwd=str(Path.cwd())
    ),
    timeout=600,  # 10分钟
    log_manager=log_manager
)

async for message in sdk.stream_query(prompt, files=[epic_path]):
    # 处理流式响应
    pass
```

**已知限制**:
- API调用有速率限制
- 超时设置影响长时间运行任务
- 网络问题会导致失败

### 质量工具集成

**Ruff**:
```bash
# 检查
ruff check src/ --output-format=json

# 修复
ruff check src/ --fix

# 格式化
ruff format src/
```

**BasedPyright**:
```bash
# 类型检查
basedpyright src/ --outputjson
```

**Pytest**:
```bash
# 运行测试
pytest tests/ -v --tb=short
```

**集成位置**:
- `agents/quality_agents.py` 包装所有工具调用
- 使用 `subprocess` 执行命令行工具
- 解析 JSON 输出

---

## 状态数据库 Schema

### stories 表 (实际结构)

```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    epic_path TEXT NOT NULL,           -- Epic文件路径
    story_path TEXT NOT NULL UNIQUE,   -- 故事文件路径
    status TEXT NOT NULL,              -- 处理状态 (pending/in_progress/review/completed/error)
    iteration INTEGER DEFAULT 0,        -- 迭代次数
    qa_result TEXT,                    -- QA结果 (JSON字符串)
    error_message TEXT,                -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phase TEXT,                        -- 当前阶段 (sm/dev/qa)
    version INTEGER DEFAULT 1          -- 乐观锁版本号
)
```

**关键字段**:
- `version`: 乐观锁，每次更新递增
- `story_path`: UNIQUE约束，避免重复
- `phase`: 用于标识当前执行阶段

**查询模式**:
```python
# 带版本检查的更新
cursor.execute("""
    UPDATE stories 
    SET status = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP
    WHERE story_path = ? AND version = ?
""", (new_status, story_path, current_version))

if cursor.rowcount == 0:
    raise OptimisticLockError("Version conflict")
```

---

## 性能特征 - 实测数据

### 典型执行时间

| 阶段 | 平均耗时 | 最大耗时 | 备注 |
|------|----------|----------|------|
| Epic解析 | 2-5s | 10s | 取决于故事数量 |
| SM阶段 (每故事) | 30s-2min | 5min | Claude API调用 |
| Dev阶段 (每故事) | 1-5min | 15min | 代码生成复杂度 |
| QA阶段 (每故事) | 30s-1min | 3min | 测试执行 |
| Ruff检查 | 5-10s | 30s | I/O密集型 |
| BasedPyright | 10-30s | 60s | CPU密集型 |
| Pytest (完整套件) | 30s-2min | 10min | 测试数量 |

**瓶颈分析**:
1. **Claude API调用**: 最大瓶颈，受网络和API延迟影响
2. **BasedPyright类型检查**: CPU密集，大项目较慢
3. **数据库锁竞争**: 高并发时可见

**优化建议**:
- 启用并发模式 (--concurrent) 可减少40%总时间
- 缓存API响应 (需实现)
- 增加数据库连接池大小

---

## 错误处理策略 - 实际行为

### 错误分类

1. **系统级错误** (阻断执行)
   - 数据库连接失败
   - Epic文件不存在
   - Python运行时错误

2. **质量错误** (非阻断)
   - Ruff/BasedPyright 达到 max_cycles 仍有错误
   - Pytest 达到 max_cycles 仍有失败
   - 返回 success=True 但记录警告

3. **业务逻辑错误** (可重试)
   - QA验证失败 → 重新执行Dev
   - SDK调用超时 → 重试
   - 状态转换失败 → 记录并继续

### 错误输出

**控制台日志**:
```
ERROR - Ruff quality gate reached max cycles (3) with 5 remaining error(s)
WARNING - Quality gates pipeline COMPLETED with 1 quality warning(s)
```

**错误JSON** (`errors/quality_errors_*.json`):
```json
{
  "epic_id": "docs/epics/epic-1.md",
  "timestamp": "2026-01-14T13:37:33Z",
  "source_dir": "src",
  "test_dir": "tests",
  "tools": [
    {
      "tool": "ruff",
      "phase": "phase_1_ruff",
      "status": "max_cycles_exceeded",
      "cycles": 3,
      "max_cycles": 3,
      "remaining_files": ["src/module.py", "src/utils.py"]
    }
  ]
}
```

**数据库记录**:
```sql
INSERT INTO stories (story_path, status, error_message)
VALUES ('/path/to/story.md', 'error', 'Max iterations exceeded')
```

---

## 开发者工作流程

### 添加新功能的步骤

1. **确定修改层次**:
   - Epic级流程 → epic_driver.py
   - 工作流控制 → controllers/
   - 业务逻辑 → agents/
   - 基础设施 → state_manager.py, log_manager.py

2. **遵循现有模式**:
   - SDK调用必须用SafeClaudeSDK包装
   - 控制器必须继承BaseController
   - Agent必须继承BaseAgent
   - 状态更新必须通过StatusUpdateAgent

3. **测试策略**:
   - 单元测试: `tests/unit/`
   - 集成测试: `tests/integration/`
   - E2E测试: `tests/e2e/`

4. **提交前检查**:
   ```bash
   # 代码质量
   ruff check src/ --fix
   basedpyright src/
   
   # 测试
   pytest tests/ -v
   
   # 格式化
   ruff format src/
   ```

### 调试技巧

**启用详细日志**:
```bash
# 完整调试
PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py \
    docs/epics/my-epic.md \
    --verbose \
    --create-log-file
```

**Claude SDK调试**:
```bash
export ANTHROPIC_LOG=debug
```

**数据库查询**:
```bash
sqlite3 progress.db "SELECT * FROM stories WHERE epic_path LIKE '%my-epic%'"
```

**检查质量错误**:
```bash
cat autoBMAD/epic_automation/errors/quality_errors_*.json | jq .
```

---

## 未来改进建议

### 短期 (1-2周)

1. **重构EpicDriver**
   - 提取QualityGateOrchestrator到独立文件
   - 分离Epic解析逻辑
   - 减少文件大小到<1000行

2. **改进日志管理**
   - 实现日志轮换
   - 添加日志级别配置
   - 结构化日志输出 (JSON)

3. **增强错误报告**
   - 统一错误格式
   - 添加错误码
   - 改进错误消息

### 中期 (1-2月)

1. **性能优化**
   - 实现API响应缓存
   - 优化数据库查询
   - 增加连接池大小

2. **测试覆盖率**
   - 单元测试 → 90%+
   - 集成测试覆盖所有工作流
   - E2E测试自动化

3. **监控与可观测性**
   - 添加性能指标收集
   - 实现健康检查
   - 集成APM工具

### 长期 (3-6月)

1. **架构重构**
   - 模块化设计
   - 插件化架构
   - 微服务化 (可选)

2. **功能增强**
   - 支持并行Epic处理
   - Web UI仪表板
   - 实时进度监控

3. **平台扩展**
   - 跨平台支持 (Linux/Mac)
   - 容器化部署
   - CI/CD集成

---

## 附录

### CLI 参数完整列表

```bash
python autoBMAD/epic_automation/epic_driver.py <epic_path> [options]

位置参数:
  epic_path              Epic markdown文件路径

可选参数:
  --max-iterations N     最大重试次数 (默认: 3)
  --retry-failed         启用失败自动重试
  --verbose              启用详细日志
  --concurrent           并发处理故事 (实验性)
  --use-claude           使用Claude实现 (默认: True)
  --source-dir DIR       源代码目录 (默认: "src")
  --test-dir DIR         测试目录 (默认: "tests")
  --skip-quality         跳过质量门控
  --skip-tests           跳过测试执行
  --create-log-file      创建时间戳日志文件
```

### 环境变量

```bash
# 必需
ANTHROPIC_API_KEY=sk-...

# 可选
ANTHROPIC_LOG=debug                    # Claude SDK调试
PYTHONPATH=/path/to/project            # Python模块路径
```

### 常见问题排查

**问题1: "Database connection pool exhausted"**
- 原因: 连接池耗尽 (5个连接)
- 解决: 重启程序，或增加连接池大小

**问题2: "Cancel scope error"**
- 原因: SDK调用未在TaskGroup中隔离
- 解决: 确保使用 `async with anyio.create_task_group()`

**问题3: "Story status not found"**
- 原因: Markdown文件缺少状态字段
- 解决: 确保文件包含 `**Status**: <value>` 行

**问题4: "Max iterations exceeded"**
- 原因: Dev-QA循环达到上限
- 解决: 检查QA失败原因，手动修复或增加max_iterations

---

**文档版本**: 3.0  
**最后更新**: 2026-01-14  
**维护者**: AI Architect Team  
**反馈**: 如发现文档与代码不一致，请立即更新此文档
