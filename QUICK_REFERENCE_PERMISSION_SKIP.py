#!/usr/bin/env python3
"""
Quick Reference: Skip Permission Commands in Claude SDK

This file contains ready-to-use examples for skipping permission commands
without using bypassPermissions mode.
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher


# Example 1: Skip all Bash commands
async def skip_all_bash():
    """Skip all Bash commands"""

    async def bash_permission_hook(input_data, tool_use_id, context):
        tool_name = input_data.get('tool_name', 'unknown')

        if tool_name == "Bash":
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Skipped all bash commands'
                }
            }
        return {}

    options = ClaudeAgentOptions(
        hooks={'PreToolUse': [HookMatcher(hooks=[bash_permission_hook])]},
        permission_mode="default",
        allowed_tools=["Read", "Grep", "Glob", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List files and show directory")
        async for message in client.receive_response():
            print(message)


# Example 2: Skip specific commands (ls, cat, rm)
async def skip_specific_commands():
    """Skip only ls, cat, and rm commands"""

    async def selective_hook(input_data, tool_use_id, context):
        tool_name = input_data.get('tool_name', 'unknown')

        if tool_name == "Bash":
            command = input_data.get('tool_input', {}).get('command', '').strip()

            skip_commands = ['ls ', 'cat ', 'rm ']
            if any(command.startswith(cmd) for cmd in skip_commands):
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': f'Skipped: {command[:30]}'
                    }
                }

        return {}

    options = ClaudeAgentOptions(
        hooks={'PreToolUse': [HookMatcher(hooks=[selective_hook])]},
        permission_mode="default",
        allowed_tools=["Read", "Grep", "Glob", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Execute: ls, cat, pwd, find")
        async for message in client.receive_response():
            print(message)


# Example 3: Skip dangerous commands only
async def skip_dangerous_only():
    """Skip only dangerous commands (rm -rf, format, etc.)"""

    async def danger_filter_hook(input_data, tool_use_id, context):
        tool_name = input_data.get('tool_name', 'unknown')

        if tool_name == "Bash":
            command = input_data.get('tool_input', {}).get('command', '')

            dangerous = ['rm -rf', 'format', 'del /s', 'mkfs']
            if any(d in command for d in dangerous):
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': 'Dangerous command blocked'
                    }
                }

        return {}

    options = ClaudeAgentOptions(
        hooks={'PreToolUse': [HookMatcher(hooks=[danger_filter_hook])]},
        permission_mode="default",
        allowed_tools=["Read", "Grep", "Glob", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Try: rm -rf /, ls, pwd")
        async for message in client.receive_response():
            print(message)


# Example 4: Skip file writes
async def skip_file_writes():
    """Skip all file write operations"""

    async def write_protection_hook(input_data, tool_use_id, context):
        tool_name = input_data.get('tool_name', 'unknown')

        if tool_name in ["Write", "Edit"]:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'File write protected'
                }
            }

        return {}

    options = ClaudeAgentOptions(
        hooks={'PreToolUse': [HookMatcher(hooks=[write_protection_hook])]},
        permission_mode="default",
        allowed_tools=["Read", "Write", "Edit", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Read a file and try to write a new file")
        async for message in client.receive_response():
            print(message)


# Example 5: Audit all tool usage
async def audit_tool_usage():
    """Log all tool usage without blocking"""

    async def audit_hook(input_data, tool_use_id, context):
        tool_name = input_data.get('tool_name', 'unknown')

        # Log but don't block
        print(f"[AUDIT] Tool used: {tool_name}")

        if tool_name == "Bash":
            command = input_data.get('tool_input', {}).get('command', '')
            print(f"[AUDIT] Command: {command[:100]}")

        # Always allow
        return {}

    options = ClaudeAgentOptions(
        hooks={'PreToolUse': [HookMatcher(hooks=[audit_hook])]},
        permission_mode="default",
        allowed_tools=["Read", "Grep", "Glob", "Bash"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List files and show directory")
        async for message in client.receive_response():
            print(message)


# Run examples
if __name__ == "__main__":
    print("Quick Reference: Permission Skip Examples")
    print("=" * 70)
    print("\nAvailable examples:")
    print("1. skip_all_bash() - Skip all Bash commands")
    print("2. skip_specific_commands() - Skip ls, cat, rm only")
    print("3. skip_dangerous_only() - Block dangerous commands")
    print("4. skip_file_writes() - Protect file writes")
    print("5. audit_tool_usage() - Log all tool usage")
    print("\nUncomment the example you want to run:")
    print()

    # Choose one to run:
    # asyncio.run(skip_all_bash())
    # asyncio.run(skip_specific_commands())
    # asyncio.run(skip_dangerous_only())
    # asyncio.run(skip_file_writes())
    # asyncio.run(audit_tool_usage())

    print("Example: To run skip_specific_commands(), uncomment the last line")
