# BMAD Epic Driver - 日志保存系统

## 概述

本文档介绍 BMAD Epic Driver 的完整日志保存机制，该系统能够自动捕获和保存所有运行时输出，包括终端输出、SDK消息（每10秒周期性消息）和异常信息。

## 功能特性

### ✅ 核心功能

1. **自动时间戳日志文件创建**
   - 每次运行时自动创建 `logs/epic_YYYYMMDD_HHMMSS.log` 格式文件
   - 基于实际运行时间生成唯一标识

2. **全量日志捕获**
   - 所有控制台输出
   - SDK调用的所有消息（包括每10秒周期性消息）
   - 代理(SM/Dev/QA)的执行日志
   - 错误和异常信息

3. **实时增量写入**
   - 实时写入日志文件
   - 每10秒持续更新
   - 包含时间戳和相对运行时间

4. **双写模式**
   - 同时输出到控制台和文件
   - 保持原有控制台体验
   - 持久化存储所有日志

5. **结构化日志格式**
   ```
   [2026-01-06 11:15:33] [INFO     ] [   10.5s] SM phase started
   [2026-01-06 11:15:34] [SDK TOOL_USE  ] [   11.2s] Using tool: Read
   [2026-01-06 11:15:45] [SDK THINKING  ] [   22.0s] [Thinking] Now I understand...
   ```

## 文件结构

```
autoBMAD/epic_automation/
├── logs/                              # 日志目录
│   ├── epic_20260106_111533.log       # 时间戳日志文件
│   ├── epic_20260106_112045.log
│   └── ...
├── log_manager.py                     # 日志管理器
├── epic_driver.py                     # 主驱动（已集成日志）
├── sdk_wrapper.py                     # SDK包装器（已增强）
├── dev_agent.py                       # 开发代理（已增强）
└── LOGSYSTEM_README.md                # 本文档
```

## 使用方法

### 自动日志记录

日志系统会在 `epic_driver.py` 运行时自动启动：

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md
```

系统会自动：
1. 创建日志目录 `autoBMAD/epic_automation/logs/`
2. 生成时间戳日志文件
3. 开始记录所有输出
4. 在运行结束时关闭日志文件

### 查看日志文件

#### 1. 列出所有日志文件

```python
from autoBMAD.epic_automation.log_manager import LogManager

log_manager = LogManager()
log_files = log_manager.list_log_files(limit=10)
for log_file in log_files:
    print(log_file.name)
```

#### 2. 读取日志内容

```bash
# 查看最新日志
cat autoBMAD/epic_automation/logs/epic_20260106_113636.log

# 实时跟踪日志（Linux/macOS）
tail -f autoBMAD/epic_automation/logs/epic_*.log
```

### 测试日志系统

运行测试脚本验证日志功能：

```bash
python autoBMAD/epic_automation/test_logging.py
```

测试包括：
- 基本日志记录
- SDK消息记录
- 异常日志记录
- 日志文件列表

## 技术实现

### 核心组件

#### 1. LogManager 类 (`log_manager.py`)

负责日志文件的创建、管理和写入：

```python
class LogManager:
    def create_timestamped_log(self) -> Path
    def write_log(self, message: str, level: str = "INFO")
    def write_sdk_message(self, message: str, msg_type: str = "SDK")
    def write_exception(self, exception: Exception, context: str = "")
    def close_log(self)
```

#### 2. SDKMessageTracker 增强 (`sdk_wrapper.py`)

扩展了原有的SDK消息追踪器，添加文件写入功能：

```python
class SDKMessageTracker:
    def __init__(self, log_manager=None)
    def update_message(self, message: str, msg_type: str = "INFO"):
        # 原功能 + 写入日志文件
```

#### 3. EpicDriver 集成 (`epic_driver.py`)

在主驱动中初始化和使用日志管理器：

```python
def __init__(self, ...):
    # 初始化日志管理器
    self.log_manager = LogManager()
    init_logging(self.log_manager)
    setup_dual_write(self.log_manager)
```

#### 4. DevAgent 增强 (`dev_agent.py`)

传递日志管理器给SDK调用：

```python
async def _execute_single_claude_sdk(self, ..., log_manager=None):
    sdk = SafeClaudeSDK(prompt, options, timeout=900.0, log_manager=log_manager)
```

### 日志格式说明

#### 普通日志
```
[2026-01-06 11:15:33] [INFO     ] [   10.5s] Starting Epic Driver
```

#### SDK消息
```
[2026-01-06 11:15:34] [SDK TOOL_USE  ] [   11.2s] Using tool: Read
[2026-01-06 11:15:45] [SDK THINKING  ] [   22.0s] [Thinking] Now I understand...
[2026-01-06 11:15:55] [SDK USER      ] [   32.0s] [User sent 1 content blocks]
```

#### 异常日志
```
[================================================================================]
[2026-01-06 11:16:00] [ERROR     ] [   60.0s] EXCEPTION OCCURRED
[================================================================================]
Context: Epic Driver run()
Exception Type: RuntimeError
Exception Message: SDK timeout

Traceback:
  ...
[================================================================================]
```

### 时间戳说明

- **绝对时间**: `[2026-01-06 11:15:33]` - 系统时间
- **相对时间**: `[   10.5s]` - 从日志开始经过的秒数

### 消息类型

| 类型 | 说明 | 示例 |
|------|------|------|
| INFO | 一般信息 | "Starting Dev phase" |
| DEBUG | 调试信息 | "Prompt preview..." |
| WARNING | 警告 | "SDK call failed, retrying" |
| ERROR | 错误 | "Failed to execute SDK call" |
| SDK TOOL_USE | SDK工具调用 | "Using tool: Read" |
| SDK THINKING | SDK思考过程 | "[Thinking] Now I understand..." |
| SDK USER | SDK用户输入 | "[User sent 1 content blocks]" |
| SDK TOOL_RESULT | SDK工具结果 | "[Tool result] File read successfully" |
| SDK SYSTEM | SDK系统消息 | "[System initialized]" |
| STDOUT | 标准输出 | 捕获的print()输出 |
| STDERR | 标准错误 | 捕获的错误输出 |

## 配置选项

### 修改日志目录

```python
# 在 epic_driver.py 的 __init__ 方法中
self.log_manager = LogManager(base_dir="custom/log/path")
```

### 修改日志级别

```python
# 修改 logging 级别
logging.getLogger().setLevel(logging.DEBUG)  # 显示所有日志
```

### 禁用文件日志（仅控制台）

如果需要禁用文件日志，可以注释掉 `epic_driver.py` 中的相关行：

```python
# 注释掉这些行
# self.log_manager = LogManager()
# init_logging(self.log_manager)
# setup_dual_write(self.log_manager)
```

## 最佳实践

### 1. 日志轮转

日志系统按运行次数创建新文件，不自动删除旧文件。建议定期清理：

```bash
# 保留最近30天的日志
find autoBMAD/epic_automation/logs/ -name "epic_*.log" -mtime +30 -delete
```

### 2. 日志监控

可以设置监控脚本来检查错误日志：

```bash
# 查找错误日志
grep "ERROR" autoBMAD/epic_automation/logs/epic_*.log

# 统计错误数量
grep -c "ERROR" autoBMAD/epic_automation/logs/epic_*.log
```

### 3. 调试模式

启用详细日志记录：

```bash
python autoBMAD/epic_automation/epic_driver.py docs/epics/my-epic.md --verbose
```

### 4. 异常分析

日志文件包含完整的异常堆栈，便于调试：

```
[ERROR] Epic driver execution failed: SDK timeout
Traceback (most recent call last):
  File "epic_driver.py", line 940, in run
    dev_qa_success = await self.execute_dev_qa_cycle(stories)
  ...
```

## 故障排除

### 问题1: 编码错误

**现象**: `UnicodeEncodeError: 'gbk' codec can't encode character`

**解决**: 确保使用UTF-8编码：
```python
open(log_file, 'w', encoding='utf-8')
```

### 问题2: 权限错误

**现象**: `PermissionError: [Errno 13] Permission denied`

**解决**: 检查日志目录权限：
```bash
chmod 755 autoBMAD/epic_automation/logs/
```

### 问题3: 磁盘空间

**现象**: 日志文件占用大量磁盘空间

**解决**: 实施日志轮转和清理策略（见最佳实践）

## 性能影响

- **CPU**: 最小影响（异步写入）
- **内存**: 忽略不计（行缓冲）
- **磁盘**: 取决于日志级别和运行时间
- **I/O**: 实时写入，可能略有影响

## 兼容性

- **Python**: 3.8+
- **操作系统**: Windows, Linux, macOS
- **编码**: UTF-8

## 更新日志

### v1.0 (2026-01-06)
- ✅ 初始版本发布
- ✅ 自动时间戳日志文件创建
- ✅ SDK消息实时记录
- ✅ 异常日志完整记录
- ✅ 双写模式支持
- ✅ 测试脚本提供

## 联系信息

如有疑问或问题，请查看：
1. 测试脚本: `test_logging.py`
2. 示例日志: `logs/epic_*.log`
3. 源代码: `log_manager.py`

---

**注意**: 本日志系统是 BMAD Epic Driver 的内置功能，无需额外配置即可使用。首次运行时会自动创建日志目录和文件。
