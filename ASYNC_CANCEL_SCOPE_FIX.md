# 异步取消范围错误深度修复方案

## 问题诊断

### 错误详情
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

### 错误位置
- **主要位置**: `anyio/_backends/_asyncio.py` - `cancel_scope.__exit__`
- **触发点**: `claude_agent_sdk/_internal/query.py` - 查询处理流程
- **传播路径**: SDK查询 → 异步生成器 → 消息处理 → 资源清理

### 根本原因分析
1. **任务隔离失败**: cancel scope 跨任务边界传播
2. **生成器生命周期**: 异步生成器的 `aclose()` 在错误的任务上下文中执行
3. **事件循环状态**: 多个 agent 共享事件循环时，cancel scope 状态管理混乱
4. **上下文管理**: `async with` 语句的进入和退出不在同一任务中

## 修复策略

### 1. 超安全异步生成器包装器

创建 `UltraSafeAsyncGenerator` 类，提供：
- 强制任务内执行
- 深度 cancel scope 隔离
- 零错误传播
- 智能清理机制

### 2. 任务局部上下文

使用 `asyncio.TaskLocal()` 确保：
- cancel scope 只在创建的任务内活动
- 防止跨任务传播
- 独立的状态管理

### 3. 深度错误抑制

在以下层次拦截错误：
- `anyio` 底层
- `asyncio` 事件循环
- `claude_agent_sdk` 内部

### 4. 零容忍清理

确保清理过程：
- 永不抛出异常
- 跨任务安全
- 自动恢复机制

## 实施计划

### 阶段1: 创建UltraSafeAsyncGenerator
- [ ] 实现任务局部 cancel scope
- [ ] 添加深度错误捕获
- [ ] 实现智能清理机制

### 阶段2: 重构SDK包装器
- [ ] 集成新的生成器包装器
- [ ] 移除易出错的 cancel scope 操作
- [ ] 增强错误恢复逻辑

### 阶段3: 会话管理器优化
- [ ] 确保每个会话独立的事件循环
- [ ] 实现 cancel scope 隔离
- [ ] 添加健康检查机制

### 阶段4: 测试验证
- [ ] 运行现有测试套件
- [ ] 验证 cancel scope 修复
- [ ] 确认性能无影响

## 成功标准

1. **零 cancel scope 错误**: 完全消除跨任务 cancel scope 错误
2. **稳定性提升**: 减少90%的异步相关错误
3. **向后兼容**: 不破坏现有API和功能
4. **性能保证**: 修复不影响执行性能

## 风险评估

### 低风险
- 错误捕获和抑制机制
- 额外的日志记录
- 增强的状态检查

### 中等风险
- 异步生成器包装器重构
- 上下文管理器修改
- 任务隔离机制

### 缓解措施
- 渐进式实施
- 全面测试覆盖
- 回滚机制准备
- 详细日志记录