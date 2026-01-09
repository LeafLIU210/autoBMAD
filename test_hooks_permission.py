#!/usr/bin/env python3
"""
Test: Using hooks to skip permission commands
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher


async def pre_tool_hook(input_data, tool_use_id, context):
    """
    Pre-tool use hook to intercept and potentially block tools

    Args:
        input_data: Hook-specific input data
        tool_use_id: Optional tool use identifier
        context: Hook context

    Returns:
        dict with hooks output
    """
    import sys

    # Get tool name from input data
    tool_name = input_data.get('tool_name', 'unknown')
    print(f"\n[HOOK] Tool called: {tool_name}", file=sys.stderr)

    if tool_name == "Bash":
        tool_input = input_data.get('tool_input', {})
        command = tool_input.get('command', '')
        print(f"[HOOK] Command: {command[:50]}", file=sys.stderr)
        print(f"[HOOK] Action: BLOCKING", file=sys.stderr)

        # Block this tool
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'Demo: blocked via hook'
            }
        }

    print(f"[HOOK] Action: ALLOWING", file=sys.stderr)
    return {}


async def main():
    """Main test using hooks"""
    print("=" * 70)
    print("TEST: Skip Permission Commands Using Hooks")
    print("=" * 70)
    print("This test uses PreToolUse hook to block Bash commands")
    print()

    # Configure hooks
    options = ClaudeAgentOptions(
        hooks={
            'PreToolUse': [
                HookMatcher(hooks=[pre_tool_hook])
            ]
        },
        allowed_tools=["Read", "Grep", "Glob", "Bash"]
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("List files using bash")

            count = 0
            async for message in client.receive_response():
                count += 1
                print(f"[{count}] {type(message).__name__}")
                if count >= 10:
                    break

        print("\n" + "=" * 70)
        print("Test completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
