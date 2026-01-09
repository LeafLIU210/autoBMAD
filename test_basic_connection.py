#!/usr/bin/env python3
"""
Basic test: Verify Claude SDK connection
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def main():
    """Basic connection test"""
    print("Basic Claude SDK Test")
    print("=" * 50)

    options = ClaudeAgentOptions(
        permission_mode="default",
        allowed_tools=["Read", "Grep", "Glob"]
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("Say 'Hello World'")

            count = 0
            async for message in client.receive_response():
                count += 1
                print(f"[{count}] {type(message).__name__}")
                if count >= 5:
                    break

        print("\nConnection successful!")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
