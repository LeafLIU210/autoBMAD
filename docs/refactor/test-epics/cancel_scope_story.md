# 测试Epic：Cancel Scope专项测试

**版本**: 1.0
**创建日期**: 2026-01-11
**测试类型**: P0 (Cancel Scope专项)

---

## Epic概述

这是一个专门用于测试Cancel Scope跨Task问题的Epic，这是重构的核心目标。

## 问题背景

当前系统存在Cancel Scope跨Task错误：
- 异步生成器在不同Task中清理
- SDK调用管理在跨Task执行时失败
- 错误模式：`RuntimeError: Cancel scope called from different task`

## 测试目标

1. 验证Cancel Scope不跨Task
2. 确认异步生成器正确清理
3. 验证SDK取消管理器的隔离机制
4. 测试重构后的TaskGroup管理

## 测试场景

### 场景1：Dev Agent → QA Agent转换
- **测试流程**:
  1. Dev Agent执行SDK调用
  2. Dev Agent完成，清理SDK会话
  3. QA Agent启动新的SDK调用
  4. 验证：无跨Task Cancel Scope错误

- **关键检查点**:
  - SafeAsyncGenerator清理在正确Task中
  - SDKCancellationManager正确跟踪执行
  - 无"different task"错误

### 场景2：连续SDK调用
- **测试流程**:
  1. 状态解析器执行SDK调用
  2. 调用完成，开始清理
  3. 立即启动下一个SDK调用
  4. 验证：清理和调用不冲突

- **关键检查点**:
  - 异步生成器正确标记关闭
  - 清理代码不阻塞新调用
  - 取消状态正确管理

### 场景3：异常取消场景
- **测试流程**:
  1. SDK调用执行中
  2. 外部取消触发
  3. 取消处理和清理
  4. 验证：系统稳定，无残留状态

- **关键检查点**:
  - CancelledError正确捕获
  - 清理逻辑完整执行
  - 状态机正确恢复

## 验收标准

### 必须满足 (P0)
- [ ] 无Cancel Scope跨Task错误
- [ ] 异步生成器正确清理
- [ ] SDK取消管理器稳定工作
- [ ] 错误恢复机制有效

### 期望达成 (P1)
- [ ] 性能提升 > 10%
- [ ] 确定性同步点，无需sleep等待
- [ ] 资源利用率优化

## 测试数据

**故事内容**:
```
# 测试故事：Cancel Scope验证

## 任务
执行一个需要多轮SDK调用的复杂任务，触发Cancel Scope问题场景。

## 开发阶段
- 实现字符串处理功能
- 集成日志系统
- 添加单元测试

## QA阶段
- 代码质量检查
- 安全性扫描
- 性能评估

## 质量门控
- Ruff检查：0个问题
- BasedPyright：0个错误
- 单元测试：> 80%覆盖率

## 取消测试点
在Dev→QA转换点插入取消信号，验证清理逻辑
```

## 监控指标

### Cancel Scope追踪
- `cross_task_cleanups`: 跨Task清理计数 (期望: 0)
- `sdk_cleanup_errors`: SDK清理错误 (期望: 0)
- `cancellation_wait_time`: 取消等待时间 (期望: < 0.5秒)

### 性能指标
- **总执行时间**: 期望 < 60秒
- **SDK调用次数**: 期望 10-15次
- **平均调用时间**: 期望 < 2秒/调用
- **内存峰值**: 期望 < 150MB

## 错误检测

### 关键错误模式
```
RuntimeError: Cancel scope called from different task
RuntimeError: Async generator cleanup happened in a different task
asyncio.CancelledError: Task was cancelled
```

### 检测脚本
```python
# 检查日志中的错误模式
import re
error_patterns = [
    r"Cancel scope called from different task",
    r"Async generator cleanup happened in a different task",
    r"CancelledError.*different task"
]
```

## 回滚计划

如果测试失败：
1. 记录错误堆栈
2. 恢复备份代码
3. 分析根本原因
4. 调整重构策略

**备份位置**: `git tag -a v1.0-backup -m "Pre-refactor backup"`
