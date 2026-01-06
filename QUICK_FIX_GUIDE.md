# autoBMAD 工作流错误 - 快速修复指南

## 🚨 问题描述

**错误**：`RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`

**影响**：autoBMAD Epic Automation 工作流异常终止

**状态**：✅ **已修复**

---

## 🔧 修复方案

### 修改的文件
- `autoBMAD/epic_automation/sdk_wrapper.py`

### 主要修复点
1. **周期性显示任务** - 防止 `CancelledError` 传播
2. **SDK 执行方法** - 改进取消处理
3. **错误处理** - 捕获取消范围错误
4. **资源清理** - 确保异步生成器关闭

---

## ✅ 验证测试

### 运行测试
```bash
# 激活虚拟环境
.venv\Scripts\activate

# 运行验证测试
python test_sdk_wrapper_fix.py
```

### 预期结果
```
[SUCCESS] 所有测试通过！SDK Wrapper 修复验证成功！
```

---

## 📚 详细文档

- **修复总结**：[AUTOBMAD_FIX_SUMMARY.md](AUTOBMAD_FIX_SUMMARY.md)
- **完整报告**：[BUGFIX_REPORT.md](BUGFIX_REPORT.md)
- **测试脚本**：[test_sdk_wrapper_fix.py](test_sdk_wrapper_fix.py)

---

## 🚀 使用 autoBMAD

### 基本命令
```bash
# 运行单个故事
python -m autoBMAD.epic_automation.epic_driver \
    --epic-path "docs/stories/your-story.md" \
    --verbose

# 查看日志
tail -f autoBMAD/epic_automation/logs/epic_*.log
```

### 常见选项
- `--max-iterations N` - 最大迭代次数
- `--retry-failed` - 重试失败的故事
- `--skip-quality` - 跳过质量检查
- `--skip-tests` - 跳过测试

---

## 💡 关键改进

### 修复前 vs 修复后

| 方面 | 修复前 | 修复后 |
|------|--------|--------|
| 取消处理 | ❌ 抛出 RuntimeError | ✅ 优雅处理 |
| 任务清理 | ❌ 不完整 | ✅ 完整 |
| 错误传播 | ❌ 会传播 | ✅ 已阻断 |
| 稳定性 | ❌ 低 | ✅ 高 |

---

## 🎯 快速故障排除

### 如果仍遇到错误

1. **检查虚拟环境**
   ```bash
   .venv\Scripts\activate
   ```

2. **重新安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **检查日志文件**
   ```bash
   cat autoBMAD/epic_automation/logs/epic_*.log
   ```

4. **运行测试**
   ```bash
   python test_sdk_wrapper_fix.py
   ```

---

## 📞 需要帮助？

如果遇到问题：

1. 查看日志文件：`autoBMAD/epic_automation/logs/`
2. 检查详细报告：`BUGFIX_REPORT.md`
3. 运行测试验证：`test_sdk_wrapper_fix.py`

---

**最后更新**：2026-01-06
**状态**：✅ 已完成并验证
