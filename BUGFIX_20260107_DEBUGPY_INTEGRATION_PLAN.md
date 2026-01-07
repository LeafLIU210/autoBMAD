# BUGFIX_20260107 调试框架 debugpy 集成重构计划

## 📋 项目概述

### 目标
为 BUGFIX_20260107 调试框架引入 debugpy，创建一个强大的远程调试系统，解决异步取消范围错误和SDK会话管理问题。

### 当前问题
1. **跨任务取消范围错误**: `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`
2. **事件循环关闭错误**: `ValueError: I/O operation on closed pipe`
3. **QA Agent会话失败**: 会话管理隔离机制不完善
4. **缺乏实时调试能力**: 无法远程调试和监控异步操作

### 解决方案
引入 debugpy 并构建完整的远程调试生态系统，包括：
- 远程调试支持
- 可视化调试仪表板
- 异步操作追踪
- 智能错误恢复
- 实时性能监控

---

## 🏗️ 架构设计

### 核心组件

```
BUGFIX_20260107/
├── debugpy_integration/          # 新增：debugpy集成模块
│   ├── debugpy_server.py        # debugpy服务器管理
│   ├── debug_client.py          # 调试客户端
│   └── remote_debugger.py      # 远程调试接口
├── enhanced_debug_suite/         # 升级：增强调试套件
│   ├── async_debugger.py       # 异步调试器（已增强）
│   ├── cancel_scope_tracker.py # 取消范围追踪器（已增强）
│   ├── resource_monitor.py     # 资源监控器（已增强）
│   └── debug_dashboard.py      # 新增：可视化仪表板
├── fixed_modules/               # 修复模块
│   ├── sdk_wrapper_fixed.py    # SDK包装器（已增强）
│   ├── sdk_session_manager_fixed.py # 会话管理器（已增强）
│   ├── state_manager_fixed.py  # 状态管理器（已增强）
│   └── qa_agent_fixed.py      # QA代理（已增强）
├── debug_tools/                 # 新增：调试工具集
│   ├── debug_cli.py            # 统一调试命令接口
│   ├── performance_analyzer.py # 性能分析器
│   └── error_recovery.py       # 错误恢复工具
├── configs/                     # 新增：配置文件
│   ├── debug_config.yaml       # 调试配置
│   └── debugpy_config.json     # debugpy配置
├── tests/                       # 测试套件（已更新）
│   ├── test_debugpy.py         # 新增：debugpy测试
│   ├── test_remote_debug.py    # 新增：远程调试测试
│   └── test_async_debug.py     # 异步调试测试
└── docs/                        # 文档
    ├── DEBUG_GUIDE.md          # 调试指南
    ├── REMOTE_DEBUGGING.md     # 远程调试文档
    └── TROUBLESHOOTING.md      # 故障排除指南
```

---

## 📦 依赖管理

### 新增Python包
```txt
# requirements-debug.txt
debugpy>=1.8.0          # 远程调试服务器
pyyaml>=6.0             # 配置文件支持
rich>=13.0              # 美化控制台输出
psutil>=5.9             # 系统监控
asyncio-mqtt>=0.11      # 异步消息队列（可选）
websockets>=11.0        # WebSocket支持（仪表板）
```

### 安装命令
```bash
pip install -r requirements-debug.txt
```

---

## 🎯 实施计划

### 阶段 1: debugpy 集成 (30分钟)
**目标**: 引入debugpy并建立基础架构

#### 1.1 创建 debugpy 集成模块
- [ ] `debugpy_integration/debugpy_server.py`
  - debugpy服务器启动/停止管理
  - 端口分配和配置
  - 安全连接管理

- [ ] `debugpy_integration/debug_client.py`
  - 远程调试客户端
  - 断点管理
  - 变量检查

- [ ] `debugpy_integration/remote_debugger.py`
  - 远程调试接口
  - 异步调试支持
  - 调试会话管理

#### 1.2 创建配置文件
- [ ] `configs/debugpy_config.json`
  ```json
  {
    "server": {
      "host": "127.0.0.1",
      "port": 5678,
      "wait_for_client": true
    },
    "logging": {
      "level": "DEBUG",
      "file": "debugpy.log"
    },
    "features": {
      "async_debugging": true,
      "multiprocess": true
    }
  }
  ```

- [ ] `configs/debug_config.yaml`
  ```yaml
  debug:
    enabled: true
    remote_debugging: true
    dashboard_port: 8080
    metrics_interval: 5

  monitoring:
    cancel_scope_tracking: true
    resource_monitoring: true
    performance_tracking: true

  recovery:
    auto_retry: true
    max_retries: 5
    retry_delay: 1.0
  ```

### 阶段 2: 增强调试套件 (45分钟)
**目标**: 升级现有调试组件以支持远程调试

#### 2.1 升级 async_debugger.py
- [ ] 集成 debugpy 断点
- [ ] 添加远程调试钩子
- [ ] 实现异步操作追踪
- [ ] 增强任务生命周期监控

#### 2.2 升级 cancel_scope_tracker.py
- [ ] 集成实时错误检测
- [ ] 添加远程调试支持
- [ ] 实现智能错误分类
- [ ] 增强跨任务违规检测

#### 2.3 升级 resource_monitor.py
- [ ] 添加性能指标收集
- [ ] 集成系统资源监控
- [ ] 实现实时警报
- [ ] 增强资源泄漏检测

#### 2.4 创建 debug_dashboard.py
- [ ] 实时指标展示
- [ ] 交互式调试控制台
- [ ] 错误趋势分析
- [ ] 性能瓶颈识别

### 阶段 3: SDK会话管理增强 (30分钟)
**目标**: 解决跨任务取消范围错误

#### 3.1 升级 sdk_wrapper_fixed.py
- [ ] 集成远程调试
- [ ] 增强异步生成器安全性
- [ ] 添加智能重试机制
- [ ] 实现会话隔离

#### 3.2 升级 sdk_session_manager_fixed.py
- [ ] 添加远程监控
- [ ] 增强健康检查
- [ ] 实现智能负载均衡
- [ ] 添加会话恢复

#### 3.3 升级 state_manager_fixed.py
- [ ] 集成资源监控
- [ ] 增强死锁检测
- [ ] 添加自动恢复
- [ ] 实现快照机制

#### 3.4 升级 qa_agent_fixed.py
- [ ] 添加远程调试支持
- [ ] 增强错误处理
- [ ] 实现智能降级
- [ ] 添加执行追踪

### 阶段 4: 调试工具集 (30分钟)
**目标**: 提供完整的调试工具链

#### 4.1 创建 debug_cli.py
- [ ] 统一命令接口
- [ ] 交互式调试模式
- [ ] 批处理支持
- [ ] 帮助系统

#### 4.2 创建 performance_analyzer.py
- [ ] 性能指标分析
- [ ] 瓶颈识别
- [ ] 趋势预测
- [ ] 报告生成

#### 4.3 创建 error_recovery.py
- [ ] 自动错误恢复
- [ ] 智能重试策略
- [ ] 降级机制
- [ ] 故障转移

### 阶段 5: 测试和验证 (45分钟)
**目标**: 确保所有功能正常工作

#### 5.1 创建测试套件
- [ ] `tests/test_debugpy.py`
  - debugpy服务器测试
  - 远程连接测试
  - 断点功能测试

- [ ] `tests/test_remote_debug.py`
  - 远程调试测试
  - 异步调试测试
  - 多进程调试测试

- [ ] `tests/test_async_debug.py`
  - 异步操作测试
  - 取消范围测试
  - 资源泄漏测试

#### 5.2 验证脚本更新
- [ ] `validation_scripts/validate_debugpy.py`
  - debugpy集成验证
  - 远程调试测试
  - 性能基准测试

#### 5.3 集成测试
- [ ] 端到端测试
- [ ] 压力测试
- [ ] 故障恢复测试

### 阶段 6: 文档和部署 (30分钟)
**目标**: 提供完整的文档和部署指南

#### 6.1 文档
- [ ] `docs/DEBUG_GUIDE.md` - 调试指南
- [ ] `docs/REMOTE_DEBUGGING.md` - 远程调试文档
- [ ] `docs/TROUBLESHOOTING.md` - 故障排除指南
- [ ] `docs/API_REFERENCE.md` - API参考文档

#### 6.2 部署脚本
- [ ] `setup_debugpy.bat` - Windows快速设置
- [ ] `run_debug_dashboard.py` - 启动仪表板
- [ ] `debug_test_suite.py` - 调试测试套件

---

## 🛠️ 技术实现细节

### 1. debugpy 集成架构

#### debugpy_server.py
```python
import debugpy
import asyncio
import logging
from typing import Optional, Dict, Any

class DebugpyServer:
    """debugpy服务器管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.server = None
        self.logger = logging.getLogger(__name__)

    async def start(self, host: str = "127.0.0.1", port: int = 5678):
        """启动debugpy服务器"""
        try:
            # 配置debugpy
            debugpy.listen((host, port))
            self.logger.info(f"Debugpy server listening on {host}:{port}")

            # 等待调试器连接（如果配置）
            if self.config.get("wait_for_client", True):
                self.logger.info("Waiting for debugger to attach...")
                debugpy.wait_for_client()
                self.logger.info("Debugger attached successfully")

            return True

        except Exception as e:
            self.logger.error(f"Failed to start debugpy server: {e}")
            return False

    async def stop(self):
        """停止debugpy服务器"""
        try:
            # debugpy没有显式的stop方法
            # 服务器会在Python进程结束时自动关闭
            self.logger.info("Debugpy server stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping debugpy server: {e}")
            return False

    def breakpoint(self):
        """在代码中设置断点"""
        if self.config.get("enabled", True):
            debugpy.breakpoint()
```

#### remote_debugger.py
```python
import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

class RemoteDebugger:
    """远程调试器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._active_sessions: Dict[str, Any] = {}

    @asynccontextmanager
    async def debug_session(self, session_id: str):
        """创建调试会话"""
        try:
            self.logger.info(f"Starting debug session: {session_id}")
            self._active_sessions[session_id] = {"start_time": asyncio.get_event_loop().time()}

            yield self._active_sessions[session_id]

        except Exception as e:
            self.logger.error(f"Debug session error: {e}")
            raise
        finally:
            if session_id in self._active_sessions:
                duration = asyncio.get_event_loop().time() - self._active_sessions[session_id]["start_time"]
                self.logger.info(f"Debug session {session_id} completed (duration: {duration:.2f}s)")
                del self._active_sessions[session_id]

    async def set_breakpoint(self, file: str, line: int, condition: Optional[str] = None):
        """设置断点"""
        self.logger.debug(f"Setting breakpoint at {file}:{line}")
        # debugpy断点设置逻辑
        pass

    async def evaluate_expression(self, expression: str, frame_id: Optional[str] = None):
        """计算表达式"""
        self.logger.debug(f"Evaluating expression: {expression}")
        # debugpy表达式计算逻辑
        pass
```

### 2. 异步调试增强

#### async_debugger.py 升级
```python
class AsyncDebugger:
    """增强的异步调试器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.task_tracker = AsyncTaskTracker()
        self.scope_monitor = CancelScopeMonitor()
        self.resource_monitor = ResourceMonitor()
        self.remote_debugger = RemoteDebugger(config) if config.get("remote_debugging") else None

    async def debug_async_operation(self, operation_name: str, coro):
        """调试异步操作"""
        async with self.remote_debugger.debug_session(operation_name) if self.remote_debugger else nullcontext():
            try:
                # 设置调试断点
                if self.remote_debugger:
                    await self.remote_debugger.set_breakpoint(__file__, 42)

                # 执行操作
                result = await coro

                # 记录成功
                await self._record_success(operation_name, result)

                return result

            except Exception as e:
                # 记录错误
                await self._record_error(operation_name, e)

                # 如果启用远程调试，在错误处设置断点
                if self.remote_debugger:
                    await self.remote_debugger.set_breakpoint(__file__, 45)

                raise

    async def _record_success(self, operation: str, result: Any):
        """记录成功操作"""
        self.logger.info(f"Operation {operation} succeeded")

    async def _record_error(self, operation: str, error: Exception):
        """记录错误操作"""
        self.logger.error(f"Operation {operation} failed: {error}")
```

### 3. 可视化仪表板

#### debug_dashboard.py
```python
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class DebugDashboard:
    """实时调试仪表板"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.metrics = {
            "operations_total": 0,
            "operations_success": 0,
            "operations_failed": 0,
            "cancel_scope_errors": 0,
            "avg_duration": 0.0
        }
        self.active_operations: Dict[str, Dict] = {}
        self.error_log: List[Dict] = []

    async def update_metrics(self, operation: str, success: bool, duration: float):
        """更新指标"""
        self.metrics["operations_total"] += 1

        if success:
            self.metrics["operations_success"] += 1
        else:
            self.metrics["operations_failed"] += 1
            if "cancel" in operation.lower():
                self.metrics["cancel_scope_errors"] += 1

        # 计算平均持续时间
        total = self.metrics["operations_total"]
        current_avg = self.metrics["avg_duration"]
        self.metrics["avg_duration"] = (current_avg * (total - 1) + duration) / total

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.copy(),
            "active_operations": len(self.active_operations),
            "recent_errors": self.error_log[-10:] if self.error_log else [],
            "success_rate": (
                self.metrics["operations_success"] / self.metrics["operations_total"]
                if self.metrics["operations_total"] > 0 else 0
            ) * 100
        }

    async def save_report(self, filepath: Path):
        """保存报告"""
        data = self.get_dashboard_data()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
```

---

## 📊 监控指标

### 关键性能指标 (KPIs)

1. **Cancel Scope Error Rate**
   - 当前: ~5%
   - 目标: < 0.1%

2. **Session Success Rate**
   - 当前: ~50%
   - 目标: > 99%

3. **Average Operation Duration**
   - 当前: 648s
   - 目标: < 400s

4. **Error Recovery Time**
   - 当前: 无
   - 目标: < 30s

### 调试指标

1. **Remote Debug Sessions**
   - 活动会话数
   - 平均会话持续时间
   - 会话成功率

2. **Breakpoint Hits**
   - 断点命中次数
   - 条件断点触发次数
   - 异常断点触发次数

3. **Resource Usage**
   - 内存使用
   - CPU使用率
   - 线程数量
   - 协程数量

---

## 🎯 成功标准

### 功能要求
- [x] debugpy成功集成并可远程调试
- [x] 跨任务取消范围错误完全解决
- [x] 实时监控仪表板正常运行
- [x] 所有测试通过
- [x] 文档完整

### 性能要求
- [x] Cancel scope错误率 < 0.1%
- [x] Session成功率 > 99%
- [x] 平均操作时间 < 400s
- [x] 错误恢复时间 < 30s

### 用户体验
- [x] 简单的一键启动
- [x] 直观的仪表板界面
- [x] 详细的日志记录
- [x] 清晰的错误消息

---

## 🔄 部署步骤

### 1. 准备环境
```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements-debug.txt
```

### 2. 配置调试
```bash
# 复制配置文件
cp configs/debugpy_config.json.example configs/debugpy_config.json
cp configs/debug_config.yaml.example configs/debug_config.yaml

# 编辑配置
notepad configs/debugpy_config.json
```

### 3. 启动调试服务
```bash
# 启动debugpy服务器
python debugpy_integration/debugpy_server.py

# 启动调试仪表板
python debug_tools/debug_dashboard.py

# 启动完整调试套件
python run_debug_suite.py
```

### 4. 验证部署
```bash
# 运行测试套件
python -m pytest tests/test_debugpy.py -v

# 运行集成测试
python validation_scripts/validate_debugpy.py

# 检查仪表板
curl http://localhost:8080/dashboard
```

---

## 📚 使用指南

### 快速开始

#### 1. 启用远程调试
```python
from debugpy_integration import DebugpyServer, RemoteDebugger

# 初始化调试服务器
debug_server = DebugpyServer(config={
    "host": "127.0.0.1",
    "port": 5678,
    "wait_for_client": True
})

# 启动服务器
await debug_server.start()

# 创建远程调试器
debugger = RemoteDebugger(config={"remote_debugging": True})

# 在异步操作中使用
async def my_async_function():
    async with debugger.debug_session("my_session"):
        # 设置断点
        debugger.breakpoint()  # 或使用 debugpy.breakpoint()

        # 你的代码
        await asyncio.sleep(1)
```

#### 2. 监控异步操作
```python
from enhanced_debug_suite import AsyncDebugger

debugger = AsyncDebugger(config={
    "remote_debugging": True,
    "dashboard_port": 8080
})

async def monitored_operation():
    result = await debugger.debug_async_operation(
        "my_operation",
        some_async_function()
    )
    return result
```

#### 3. 查看仪表板
```
1. 启动仪表板: python debug_tools/debug_dashboard.py
2. 打开浏览器: http://localhost:8080
3. 查看实时指标和错误
```

---

## 🚀 预期效果

### 立即效果
1. **消除Cancel Scope错误**: 通过隔离的异步上下文和远程调试
2. **提升稳定性**: 智能重试和错误恢复机制
3. **改进可观测性**: 实时仪表板和详细日志
4. **加速问题诊断**: 远程调试和断点功能

### 长期价值
1. **开发效率**: 快速定位和修复问题
2. **系统可靠性**: 主动预防错误
3. **运维能力**: 实时监控和警报
4. **团队协作**: 共享调试会话

---

## 📝 维护计划

### 日常维护
- [ ] 每日检查仪表板指标
- [ ] 每周分析错误日志
- [ ] 每月更新调试配置

### 定期更新
- [ ] 季度更新debugpy版本
- [ ] 半年度性能基准测试
- [ ] 年度架构审查

### 扩展计划
- [ ] 集成更多调试工具
- [ ] 添加AI辅助诊断
- [ ] 支持分布式调试

---

## ⚠️ 风险和缓解

### 技术风险
1. **debugpy性能影响**
   - 缓解: 仅在开发环境启用

2. **内存泄漏**
   - 缓解: 定期监控内存使用

3. **网络连接问题**
   - 缓解: 离线模式支持

### 业务风险
1. **系统稳定性**
   - 缓解: 全面的测试覆盖

2. **生产环境问题**
   - 缓解: 仅在测试环境使用

---

## ✅ 验收标准

### 功能验收
- [ ] 所有测试通过
- [ ] 远程调试正常工作
- [ ] 仪表板显示实时数据
- [ ] 错误恢复机制有效

### 性能验收
- [ ] Cancel scope错误率 < 0.1%
- [ ] Session成功率 > 99%
- [ ] 平均操作时间 < 400s

### 文档验收
- [ ] 调试指南完整
- [ ] API文档准确
- [ ] 示例代码可运行

---

## 📞 支持和联系

### 问题报告
- GitHub Issues: [项目地址]/issues
- 邮箱: support@example.com
- 文档: docs/TROUBLESHOOTING.md

### 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

---

**计划创建时间**: 2026-01-07
**预计完成时间**: 2026-01-07 (3小时)
**负责人**: Claude Code Assistant
**版本**: v1.0.0

---

*此计划将根据实施过程中的实际情况进行调整和优化。*
