# Agent SDK Overview

Build autonomous AI agents with Claude that can use tools, execute commands, and interact with external systems

---

The Claude Agent SDK is a framework for building **autonomous AI agents** powered by Claude. Agents can use tools, execute commands, read and write files, browse the web, and interact with external systems to accomplish complex tasks.

**Key capabilities:**
- **Autonomous execution** - Agents work independently to complete tasks
- **Tool use** - Claude decides which tools to use and when
- **File operations** - Read, write, and edit files in the working directory
- **Command execution** - Run shell commands with configurable permissions
- **Session management** - Maintain context across multiple interactions
- **Custom tools** - Extend capabilities with your own functions
- **MCP integration** - Connect to databases, APIs, and external services

## Core concepts

### Agents vs. chat

| Aspect | Chat | Agents |
|--------|------|--------|
| **Interaction** | Conversational | Task-oriented |
| **Autonomy** | Responds to prompts | Acts independently |
| **Tools** | Manual tool calls | Automatic tool selection |
| **File access** | Via uploads | Direct filesystem access |
| **Commands** | Not supported | Bash execution |
| **Session** | Stateless | Persistent context |

### The agent loop

Agents operate in a continuous loop:

```
1. Receive task
2. Analyze what needs to be done
3. Decide which tools to use
4. Execute tools and observe results
5. Determine next steps
6. Repeat until complete
7. Return final result
```

## Quick start

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix bugs in utils.py",
  options: {
    allowedTools: ["Read", "Edit", "Glob"],
    permissionMode: "acceptEdits"
  }
})) {
  if (message.type === "assistant") {
    console.log(message.content);
  }
}
```

**Python:**
```python
from claude_agent_sdk import query

async for message in query(
    prompt="Find and fix bugs in utils.py",
    options={
        "allowed_tools": ["Read", "Edit", "Glob"],
        "permission_mode": "acceptEdits"
    }
):
    if message.type == "assistant":
        print(message.content)
```

## Core SDK functions

### query()

The main entry point for creating agents. It returns an async iterator that streams messages as Claude works.

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = query({
  prompt: "Your task here",
  options: { /* configuration */ }
});

for await (const message of messages) {
  // Process messages
}
```

**Python:**
```python
from claude_agent_sdk import query

async for message in query(
    prompt="Your task here",
    options={ /* configuration */ }
):
    # Process messages
    pass
```

### ClaudeSDKClient (Python)

Lower-level client for more control over sessions and message handling.

**Python:**
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Edit"],
        permission_mode="acceptEdits"
    )
) as client:
    await client.query("Your task")
    async for message in client.receive_response():
        print(message)
```

## Tool permissions

Control what Claude can do through `allowedTools`:

| Tools | Capabilities |
|-------|-------------|
| `Read`, `Glob`, `Grep` | Read-only analysis |
| `Read`, `Edit`, `Glob` | Analyze and modify code |
| `Read`, `Edit`, `Bash`, `Glob`, `Grep` | Full automation |

**TypeScript:**
```typescript
options: {
  allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"]
}
```

**Python:**
```python
options = {
    "allowed_tools": ["Read", "Edit", "Bash", "Glob", "Grep"]
}
```

## Permission modes

Control how file modifications are approved:

| Mode | Behavior | Use case |
|------|----------|----------|
| `acceptEdits` | Auto-approve edits | Trusted workflows |
| `bypassPermissions` | No prompts | CI/CD, automation |
| `default` | Prompt for approval | Human oversight |

**TypeScript:**
```typescript
options: {
  permissionMode: "acceptEdits"  // Auto-approve file edits
}
```

**Python:**
```python
options = {
    "permission_mode": "acceptEdits"  # Auto-approve file edits
}
```

## Message streaming

The SDK streams messages as Claude works:

**Message types:**
- `system` - Initialization and metadata
- `assistant` - Claude's reasoning and tool calls
- `tool_result` - Output from executed tools
- `result` - Final outcome

**TypeScript:**
```typescript
for await (const message of query({ prompt: "..." })) {
  if (message.type === "assistant") {
    // Claude is thinking or calling tools
  } else if (message.type === "tool_result") {
    // A tool has executed
  } else if (message.type === "result") {
    // Task completed
  }
}
```

**Python:**
```python
async for message in query(prompt="..."):
    if message.type == "assistant":
        # Claude is thinking or calling tools
        pass
    elif message.type == "tool_result":
        # A tool has executed
        pass
    elif message.type == "result":
        # Task completed
        pass
```

## Example agents

### Bug-fixing agent

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review utils.py for bugs that would cause crashes. Fix any issues you find.",
  options: {
    allowedTools: ["Read", "Edit", "Glob"],
    permissionMode: "acceptEdits"
  }
})) {
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}
```

**Python:**
```python
from claude_agent_sdk import query

async for message in query(
    prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
    options={
        "allowed_tools": ["Read", "Edit", "Glob"],
        "permission_mode": "acceptEdits"
    }
):
    if message.type == "assistant":
        print(message.content)
```

### Code analysis agent

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Analyze this codebase for performance issues and suggest improvements",
  options: {
    allowedTools: ["Read", "Grep", "Glob"],
    permissionMode: "acceptEdits"
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log("Analysis complete");
  }
}
```

**Python:**
```python
from claude_agent_sdk import query

async for message in query(
    prompt="Analyze this codebase for performance issues and suggest improvements",
    options={
        "allowed_tools": ["Read", "Grep", "Glob"],
        "permission_mode": "acceptEdits"
    }
):
    if hasattr(message, 'result'):
        print("Analysis complete")
```

## Next steps

**Learn the basics:**
- [Quickstart guide](/docs/en/agent-sdk/quickstart) - Build your first agent
- [TypeScript SDK reference](/docs/en/agent-sdk/typescript) - Complete TypeScript API
- [Python SDK reference](/docs/en/agent-sdk/python) - Complete Python API

**Extend capabilities:**
- [Custom tools](/docs/en/agent-sdk/custom-tools) - Build your own tools
- [MCP integration](/docs/en/agent-sdk/mcp) - Connect to external services
- [Subagents](/docs/en/agent-sdk/subagents) - Create specialized sub-agents

**Production deployment:**
- [Hosting the SDK](/docs/en/agent-sdk/hosting) - Deploy agents in production
- [Secure deployment](/docs/en/agent-sdk/secure-deployment) - Security hardening
- [Sessions](/docs/en/agent-sdk/sessions) - Manage persistent sessions

**Advanced features:**
- [File checkpointing](/docs/en/agent-sdk/file-checkpointing) - Undo file changes
- [Structured outputs](/docs/en/agent-sdk/structured-outputs) - Get validated JSON
- [Hooks](/docs/en/agent-sdk/hooks) - Execute custom code during agent runs
