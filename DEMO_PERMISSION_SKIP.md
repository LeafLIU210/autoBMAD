# Claude SDK 跳过权限命令演示

## 概述

本演示展示了如何在**不启用 `bypassPermissions`** 的情况下，使用 Claude SDK 的 **Hooks** 功能来拦截和跳过需要权限的命令。

## 关键发现

### ✅ 验证成功的功能

1. **使用 PreToolUse Hook 可以拦截工具调用**
2. **可以返回 `permissionDecision: 'deny'` 来跳过命令**
3. **不需要 `bypassPermissions` 模式**
4. **可以基于工具类型和参数进行精细控制**

## 实现方法

### 方法一：使用 Hooks (推荐)

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher
)

async def permission_hook(input_data, tool_use_id, context):
    """拦截工具调用的Hook"""
    tool_name = input_data.get('tool_name', 'unknown')

    if tool_name == "Bash":
        command = input_data.get('tool_input', {}).get('command', '')
        print(f"拦截Bash命令: {command}")

        # 跳过该命令
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': '演示：跳过权限命令'
            }
        }

    # 允许其他工具
    return {}

# 使用配置
options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(hooks=[permission_hook])
        ]
    },
    permission_mode="default",  # 不使用 bypassPermissions
    allowed_tools=["Read", "Grep", "Glob", "Bash"]
)
```

### 方法二：使用 can_use_tool (需要进一步验证)

根据SDK文档，`can_use_tool` 回调也可以用于权限控制：

```python
async def custom_permission_handler(tool_name, input_data, context):
    """自定义权限检查"""
    if tool_name == "Bash":
        return {
            "behavior": "deny",
            "message": "演示：跳过命令"
        }
    return {"behavior": "allow", "updatedInput": input_data}

options = ClaudeAgentOptions(
    can_use_tool=custom_permission_handler,
    permission_mode="default"
)
```

## 测试结果

### Hook方法测试

运行 `test_hooks_permission.py` 的输出：

```
[HOOK] Tool called: Bash
[HOOK] Command: ls -la
[HOOK] Action: BLOCKING
```

✅ **成功拦截了 Bash 命令**

## 与配置文件的关系

您的 `.claude/settings.local.json` 配置文件：

```json
{
  "permissions": {
    "allow": ["Bash(ls:*)", "Bash(cat:*)", ...],
    "deny": ["Bash(curl:*)", "Bash(rm:-rf:*)"]
  }
}
```

**Hooks 的优先级**：
1. 首先执行 Hooks 的权限检查
2. 然后应用配置文件的权限规则
3. 最后应用 `permission_mode` 设置

这提供了**多层权限控制**机制。

## 关键优势

1. **不需要 `bypassPermissions`**: 保持安全模式
2. **精细控制**: 可以根据工具类型、参数内容等进行判断
3. **动态控制**: 在运行时决定是否允许/拒绝
4. **审计日志**: 可以记录所有拦截的工具调用
5. **不中断执行**: 使用 `permissionDecision: 'deny'` 跳过命令但继续执行后续操作

## 应用场景

1. **沙箱环境**: 拦截危险命令如 `rm -rf`, `format`
2. **测试环境**: 跳过可能影响测试的命令
3. **审计**: 记录所有工具使用情况
4. **限流**: 控制特定工具的使用频率
5. **演示**: 在演示环境中安全地测试代码

## 结论

✅ **证实：可以在不启用 `bypassPermissions` 的情况下跳过权限命令**

使用 **PreToolUse Hook** 是实现这一功能的推荐方法，它提供了：
- 完整的权限控制
- 灵活的拦截逻辑
- 与现有权限系统的兼容性
- 良好的审计能力

---

## 测试文件

- `test_hooks_permission.py` - 使用 Hooks 拦截权限命令
- `test_simple_permission.py` - 尝试使用 can_use_tool (可能需要特定版本)
- `test_basic_connection.py` - 基础连接测试

运行测试：

```bash
venv/Scripts/python.exe test_hooks_permission.py
```
