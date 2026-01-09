# Windows 路径转换实现总结

## 问题
在 Windows 环境下使用 Git Bash 运行 epic_driver.py 时，`story_path` 会被注入到 Claude SDK 提示词中。需要将 Unix 风格路径转换为 Windows 风格路径。

## 解决方案
在 `EpicDriver` 类中实现了 `_convert_to_windows_path()` 方法，用于将 WSL/Unix 风格的路径转换为 Windows 绝对路径。

### 转换规则
- `/d/GITHUB/pytQt_template/...` → `D:\GITHUB\pytQt_template\...`
- 将所有 `/` 替换为 `\`
- 保持相对路径不变

## 实现修改

### 1. 新增辅助方法
在 `epic_driver.py` 中添加了 `_convert_to_windows_path()` 方法（第846-871行）。

### 2. 应用转换位置
在 `parse_epic()` 方法的两个位置应用转换：
- **第696行**：转换已找到的 story 文件路径
- **第717行**：转换新创建的 story 文件路径

## 测试验证
创建并运行了测试脚本 `test_windows_path_conversion.py`，测试结果显示：

```
测试结果: 6/6 通过
- [PASS] WSL/Unix 风格绝对路径转换
- [PASS] WSL/Unix C 盘路径转换
- [PASS] Windows 风格路径保持不变
- [PASS] 相对路径分隔符转换
- [PASS] 深层目录路径转换
- [PASS] 单级目录路径转换
```

## 转换示例

| 输入路径 | 输出路径 |
|---------|---------|
| `/d/GITHUB/pytQt_template/docs/stories/004.1-spec-parser-system.md` | `D:\GITHUB\pytQt_template\docs\stories\004.1-spec-parser-system.md` |
| `/c/Users/test/Documents/story.md` | `C:\Users\test\Documents\story.md` |
| `docs/stories/004.1-spec-parser-system.md` | `docs\stories\004.1-spec-parser-system.md` |

## 范围限制
- **仅转换** 故事文档路径 (`story['path']`)
- **不转换** 其他路径：
  - `source_dir`
  - `test_dir`
  - `epic_path`
  - 其他配置路径

## 影响的组件
- **EpicDriver 类**：`parse_epic()` 方法
- **Story 字典**：`story['path']` 字段
- **下游传递**：所有使用 `story_path` 的 Agent（SM、Dev、QA）

## 结果
✅ **成功实现**：Windows 路径转换功能已正确实现并通过测试验证。现在 `story_path` 将以 Windows 风格格式传递给 Claude SDK，更符合其预期格式。