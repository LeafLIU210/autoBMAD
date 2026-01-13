现在有了官方说明。Ralph Wiggum 是 Geoffrey Huntley 提出的迭代开发方法论。

核心原理

while :; do
  cat PROMPT.md | claude-code --continue
done
关键点： 同一个 prompt 被反复喂给 Claude，Claude 通过查看文件和 git 历史中自己之前的工作来迭代改进，而不是将输出作为输入。

Python SDK 实现 Ralph Loop
根据官方机制，修正后的实现：


import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

async def ralph_loop(
    prompt: str,
    max_iterations: int = 10,
    completion_promise: str = "DONE",
    cwd: str = "."
):
    """
    Ralph Wiggum 循环实现
    
    核心机制：同一个 prompt 反复执行，Claude 通过文件变化看到自己之前的工作
    """
    options = ClaudeAgentOptions(
        permission_mode="acceptEdits",
        cwd=cwd,
        setting_sources=["project"],
        system_prompt={
            "type": "preset",
            "preset": "claude_code"
        }
    )

    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*50}")
        print(f"=== Ralph Iteration {iteration}/{max_iterations} ===")
        print(f"{'='*50}")
        
        # 每次迭代使用新的会话，但发送相同的 prompt
        # Claude 通过读取文件来看到自己之前的工作
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            
            response_text = ""
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text
                            print(block.text, end="", flush=True)
                
                if isinstance(message, ResultMessage):
                    print(f"\n[Iteration {iteration} completed]")
            
            # 检查 <promise> 标签
            if f"<promise>{completion_promise}</promise>" in response_text:
                print(f"\n✅ Promise '{completion_promise}' detected! Task complete.")
                return True
    
    print(f"\n⚠️ Max iterations ({max_iterations}) reached")
    return False


if __name__ == "__main__":
    asyncio.run(ralph_loop(
        prompt='根据文档完成开发。完成后输出 <promise>DONE</promise>',
        max_iterations=10,
        completion_promise="DONE",
        cwd=r"d:\GITHUB\pytQt_template"
    ))
与之前实现的关键区别
方面	之前（错误）	修正后
会话	同一会话多轮	每次迭代新会话
Prompt	首次后用"继续"	每次相同 prompt
自引用	会话上下文	文件系统中的工作产物
完成检测	文本包含	<promise>TAG</promise> 标签
参考来源：

Ralph Wiggum 原始技术 https://ghuntley.com/ralph/
Ralph Orchestrator https://github.com/mikeyobrien/ralph-orchestrator