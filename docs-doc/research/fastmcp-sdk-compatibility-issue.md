# FastMCP 与 Claude Agent SDK 兼容性问题研究报告

**研究日期**: 2026-04-05  
**问题状态**: 关键阻塞  
**影响范围**: DocuSwarm 流水线无法正常执行

---

## 1. 问题概述

### 1.1 错误现象

当启动 DocuSwarm 流水线时，所有节点执行均失败，错误信息如下：

```
TypeError: Object of type FastMCP is not JSON serializable
```

错误发生在 `ClaudeSDKClient.connect()` 调用期间，导致 Independent Agent 无法创建 LLM 会话。

### 1.2 问题影响

- **严重程度**: P0 - 完全阻塞
- **影响模块**: 所有使用 MCP 工具的节点执行
- **用户影响**: 流水线启动后立即失败，无法生成任何交付物

---

## 2. 根因分析

### 2.1 技术背景

DocuSwarm 使用两种不同的 MCP 服务器实现：

#### 2.1.1 FastMCP (当前实现)

来自 `mcp` 包，用于创建独立的 MCP 服务器：

```python
from mcp.server.fastmcp import FastMCP

server = FastMCP('server-name')

@server.tool()
async def my_tool(input: str) -> str:
    return f"Result: {input}"
```

**特点**:
- 类型: `<class 'mcp.server.fastmcp.server.FastMCP'>`
- 设计目标: 启动独立的 MCP 服务器进程
- 主要方法: `run()`, `run_stdio_async()`, `run_sse_async()`
- 序列化: **不支持 JSON 序列化**

#### 2.1.2 SDK MCP (SDK 期望格式)

来自 `claude_agent_sdk`，用于进程内工具执行：

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool('my_tool', 'Tool description', {'input': str})
async def my_tool_func(args):
    return {'content': [{'type': 'text', 'text': f"Result: {args}"}]}

server = create_sdk_mcp_server(
    name='server-name',
    version='1.0.0',
    tools=[my_tool_func]
)
```

**特点**:
- 类型: `<class 'dict'>`
- 结构: `{'type': 'sdk', 'name': 'server-name', 'instance': Server}`
- 设计目标: SDK 内部进程内执行
- 序列化: 由 SDK 内部处理

### 2.2 兼容性测试结果

| 测试场景 | FastMCP | SDK MCP |
|---------|---------|---------|
| `ClaudeAgentOptions(mcp_servers={...})` 创建 | ✓ 成功 | ✓ 成功 |
| `ClaudeSDKClient.connect()` | ✗ 失败 | ✓ 成功 |
| 错误信息 | `TypeError: Object of type FastMCP is not JSON serializable` | 无 |

### 2.3 问题根源

1. **SDK 内部通信机制**: Claude Agent SDK 使用子进程模式与 Claude Code CLI 通信
2. **序列化要求**: 传递给子进程的配置需要 JSON 序列化
3. **FastMCP 不兼容**: FastMCP 对象包含不可序列化的运行时状态

---

## 3. 代码路径分析

### 3.1 问题代码位置

```
autoBMAD/docuswarm/
├── tools/
│   ├── file_tools.py      # create_file_read_server() 返回 FastMCP
│   └── search_tools.py    # create_search_server() 返回 FastMCP
├── llm/
│   ├── session_manager.py # _create_options() 将 FastMCP 放入 mcp_servers
│   └── tool_filter.py     # NodeToolFilter.create_mcp_servers() 返回 FastMCP 列表
└── agents/
    └── independent.py     # 调用 session_manager.create_session() 触发错误
```

### 3.2 调用链

```
pipeline_service.start()
  └─> HybridOrchestrator.start_pipeline()
       └─> create_pipeline_graph(session_manager)
            └─> _create_integrated_node_executor()
                 └─> create_node_executor()
                      └─> create_dual_agent_node()
                           └─> node.execute_with_context()
                                └─> IndependentAgent.execute_with_input()
                                     └─> session_manager.create_session()
                                          └─> _create_options()
                                               └─> node_filter.create_mcp_servers()
                                                    └─> 返回 [FastMCP, FastMCP, ...]
                                               └─> options_dict["mcp_servers"] = {key: FastMCP}
                                          └─> ClaudeSDKClient(options)
                                               └─> client.connect()
                                                    └─> JSON 序列化失败!
```

---

## 4. 解决方案

### 4.1 方案 A: 迁移到 SDK MCP 格式 (推荐)

**修改范围**: `file_tools.py`, `search_tools.py`

**优点**:
- 完全兼容 SDK
- 进程内执行，性能更好
- 无需管理子进程

**缺点**:
- 需要重写工具定义格式
- `@tool` 装饰器语法与 FastMCP 不同

**示例迁移**:

```python
# Before (FastMCP)
from mcp.server.fastmcp import FastMCP

def create_file_read_server(allowed_dirs: list[str], node_id: str):
    server = FastMCP(f"mcp__docuswarm-files-{node_id}")
    
    @server.tool(name=f"{server.name}__read_document")
    async def mcp_read_document(path: str) -> str:
        # ... implementation
        pass
    
    return server

# After (SDK MCP)
from claude_agent_sdk import create_sdk_mcp_server, tool

def create_file_read_server(allowed_dirs: list[str], node_id: str):
    validator = PathValidator(allowed_dirs)
    
    @tool('read_document', 'Read a document', {'path': str})
    async def read_document(args):
        result = read_document_impl(args['path'], validator)
        if result.success:
            return {'content': [{'type': 'text', 'text': str(result.result)}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}
    
    @tool('list_documents', 'List documents in directory', {'directory': str, 'recursive': bool})
    async def list_documents(args):
        # ... implementation
        pass
    
    return create_sdk_mcp_server(
        name=f"docuswarm-files-{node_id}",
        version="1.0.0",
        tools=[read_document, list_documents]
    )
```

### 4.2 方案 B: 使用外部 MCP 服务器模式

**修改范围**: `session_manager.py`

**原理**: 将 FastMCP 服务器作为独立进程启动，通过 stdio 通信

**优点**:
- 保留现有 FastMCP 代码
- 标准化的 MCP 协议

**缺点**:
- 需要进程管理
- IPC 开销
- 部署复杂度增加

**示例配置**:

```python
# ClaudeAgentOptions 支持的外部服务器格式
options = ClaudeAgentOptions(
    mcp_servers={
        "file-server": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "autoBMAD.docuswarm.tools.file_server", "--node-id", "analyst"]
        }
    }
)
```

### 4.3 方案 C: 临时禁用 MCP 工具 (快速恢复)

**修改范围**: `session_manager.py`

**原理**: 暂时跳过 MCP 服务器配置

**优点**:
- 快速恢复流水线
- 最小代码变更

**缺点**:
- 丢失文件读取和搜索能力
- 仅作为临时措施

**示例修改**:

```python
# session_manager.py - _create_options()
# 在 MCP 配置代码块前添加条件跳过
if self._node_id and False:  # 临时禁用
    # ... MCP 配置代码
```

---

## 5. 推荐实施路径

### 5.1 短期 (P0 - 立即)

1. **实施方案 C** - 临时禁用 MCP 工具，恢复流水线基本功能
2. 验证流水线可以正常执行（仅使用内置工具）

### 5.2 中期 (P1 - 本周)

1. **实施方案 A** - 迁移 `file_tools.py` 和 `search_tools.py` 到 SDK MCP 格式
2. 更新 `tool_filter.py` 的工具命名约定
3. 完整测试所有节点

### 5.3 长期 (P2 - 下个迭代)

1. 考虑添加更多 SDK MCP 工具
2. 统一工具定义规范
3. 完善错误处理和日志

---

## 6. 测试验证

### 6.1 验证脚本

```python
# test_mcp_compatibility.py
import asyncio
from claude_agent_sdk import create_sdk_mcp_server, tool, ClaudeAgentOptions, ClaudeSDKClient

@tool('test_tool', 'A test tool', {'input': str})
async def test_tool(args):
    return {'content': [{'type': 'text', 'text': f"Result: {args['input']}"}]}

async def test():
    server = create_sdk_mcp_server(
        name='test-server',
        version='1.0.0',
        tools=[test_tool]
    )
    
    options = ClaudeAgentOptions(
        mcp_servers={'test': server},
        max_turns=1
    )
    
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Test the tool with input 'hello'")
        async for msg in client.receive_response():
            print(msg)

asyncio.run(test())
```

### 6.2 预期结果

- SDK MCP 格式：会话创建成功
- FastMCP 格式：`TypeError: Object of type FastMCP is not JSON serializable`

---

## 7. 相关文件清单

| 文件路径 | 当前格式 | 需要修改 |
|---------|---------|---------|
| `tools/file_tools.py` | FastMCP | 是 (方案 A) |
| `tools/search_tools.py` | FastMCP | 是 (方案 A) |
| `llm/tool_filter.py` | 返回 FastMCP 列表 | 是 (方案 A) |
| `llm/session_manager.py` | 使用 FastMCP | 是 (所有方案) |
| `agents/independent.py` | 调用 session_manager | 否 |

---

## 8. 附录

### 8.1 FastMCP 属性列表

```
['add_prompt', 'add_resource', 'add_tool', 'call_tool', 'completion', 
 'custom_route', 'dependencies', 'get_context', 'get_prompt', 'icons', 
 'instructions', 'list_prompts', 'list_resource_templates', 'list_resources', 
 'list_tools', 'name', 'prompt', 'read_resource', 'resource', 'run', 
 'run_sse_async', 'run_stdio_async', 'run_streamable_http_async', 'session_manager', 
 'settings', 'sse_app', 'streamable_http_app', 'tool', 'website_url']
```

### 8.2 SDK MCP 结构

```python
{
    'type': 'sdk',
    'name': 'server-name',
    'instance': <Server object>
}
```

### 8.3 参考文档

- [Claude Agent SDK GitHub](https://github.com/anthropics/claude-agent-sdk-python)
- [MCP Specification](https://modelcontextprotocol.io/)
- [SDK MCP Server Example](https://github.com/anthropics/claude-agent-sdk-python/blob/main/examples/mcp_calculator.py)

---

**报告作者**: AI Assistant  
**版本**: 1.0  
**最后更新**: 2026-04-05
