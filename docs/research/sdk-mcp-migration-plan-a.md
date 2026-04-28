# 方案A: 迁移到 SDK MCP 格式 - 详细研究报告

**研究日期**: 2026-04-05  
**方案类型**: 架构迁移  
**目标**: 将 DocuSwarm 工具从 FastMCP 格式迁移到 SDK MCP 格式

---

## 1. 执行摘要

### 1.1 结论

**方案A 可行且推荐实施**。经过深度测试验证，SDK MCP 格式完全兼容 Claude Agent SDK，可以解决当前的 JSON 序列化问题。

### 1.2 关键发现

| 项目 | FastMCP | SDK MCP |
|-----|---------|---------|
| 类型 | `<class 'FastMCP'>` | `<class 'dict'>` |
| JSON 序列化 | ✗ 不支持 | ✓ 支持 |
| 会话创建 | ✗ 失败 | ✓ 成功 |
| 进程模式 | 独立进程 | 进程内执行 |
| 性能 | 较低 (IPC 开销) | 较高 (直接调用) |

### 1.3 迁移范围

- `file_tools.py`: 2 个工具 (read_document, list_documents)
- `search_tools.py`: 2 个工具 (grep_search, glob_search)
- `tool_filter.py`: 命名约定调整
- `session_manager.py`: 服务器配置格式调整

---

## 2. 技术对比

### 2.1 FastMCP 格式 (当前)

```python
from mcp.server.fastmcp import FastMCP

def create_file_read_server(allowed_dirs: list[str], node_id: str):
    server_name = f"mcp__docuswarm-files-{node_id}"
    server = FastMCP(server_name)
    
    @server.tool(name=f"{server_name}__read_document")
    async def mcp_read_document(path: str) -> str:
        result = read_document(path, validator=validator)
        if result.success:
            return str(result.result)
        return f"Error: {result.error}"
    
    return server  # 返回 FastMCP 对象
```

**问题**:
1. 返回 `FastMCP` 对象，无法 JSON 序列化
2. 工具命名包含完整 server name 前缀，导致 MCP 工具名重复 (`mcp__mcp__...`)

### 2.2 SDK MCP 格式 (目标)

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

def create_file_read_server(allowed_dirs: list[str], node_id: str):
    validator = PathValidator(allowed_dirs)
    
    @tool('read_document', 'Read a document within allowed directories', {
        'type': 'object',
        'properties': {
            'path': {'type': 'string', 'description': 'Path to the file'}
        },
        'required': ['path']
    })
    async def read_document_tool(args):
        result = read_document(args['path'], validator=validator)
        if result.success:
            return {'content': [{'type': 'text', 'text': str(result.result)}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}
    
    return create_sdk_mcp_server(
        name=f"docuswarm-files-{node_id}",
        version="1.0.0",
        tools=[read_document_tool]
    )  # 返回 dict
```

**优势**:
1. 返回 `dict` 类型，SDK 内部处理序列化
2. 工具命名符合 SDK 约定: `mcp__{server_name}__{tool_name}`
3. 进程内执行，无 IPC 开销

---

## 3. 详细测试结果

### 3.1 @tool 装饰器签名

```
tool(name: str, description: str, input_schema: type | dict[str, Any], 
     annotations: ToolAnnotations | None = None) -> SdkMcpTool
```

**参数说明**:
- `name`: 工具名称 (不含 server 前缀)
- `description`: 工具描述
- `input_schema`: 参数模式，支持两种格式:
  - 简单类型映射: `{'path': str, 'count': int}`
  - JSON Schema: 完整的 JSON Schema 对象

### 3.2 参数格式测试

| 格式 | 示例 | 适用场景 |
|-----|------|---------|
| 简单类型 | `{'path': str, 'recursive': bool}` | 简单参数 |
| JSON Schema | `{'type': 'object', 'properties': {...}}` | 复杂验证 |

**简单类型映射**:
```python
@tool('read_document', 'Read a document', {'path': str})
```

**JSON Schema 格式**:
```python
@tool('grep_search', 'Search file contents', {
    'type': 'object',
    'properties': {
        'pattern': {'type': 'string', 'description': 'Regex pattern'},
        'path': {'type': 'string', 'description': 'Directory path'},
        'max_results': {'type': 'integer', 'default': 20, 'minimum': 1, 'maximum': 50}
    },
    'required': ['pattern', 'path']
})
```

### 3.3 返回值格式

所有 SDK MCP 工具必须返回以下格式:

```python
{
    'content': [
        {'type': 'text', 'text': '工具返回的文本内容'}
    ]
}
```

### 3.4 工具命名约定

**SDK 自动生成格式**: `mcp__{server_name}__{tool_name}`

| 组件 | FastMCP 当前 | SDK MCP 目标 |
|-----|-------------|-------------|
| Server name | `mcp__docuswarm-files-analyst` | `docuswarm-files-analyst` |
| Tool name | `mcp__docuswarm-files-analyst__read_document` | `read_document` |
| MCP 工具全名 | `mcp__mcp__docuswarm-files-analyst__read_document` (错误!) | `mcp__docuswarm-files-analyst__read_document` |

### 3.5 会话创建测试

```
=== Test: FastMCP ===
ClaudeSDKClient.connect() -> TypeError: Object of type FastMCP is not JSON serializable

=== Test: SDK MCP ===
ClaudeSDKClient.connect() -> SUCCESS
```

---

## 4. 迁移实施计划

### 4.1 file_tools.py 迁移

**当前代码结构**:
```
create_file_read_server()
  ├── validator = PathValidator(allowed_dirs)
  ├── server = FastMCP(f"mcp__docuswarm-files-{node_id}")
  ├── @server.tool(name=f"{server_name}__read_document")
  ├── @server.tool(name=f"{server_name}__list_documents")
  └── return server  # FastMCP 对象
```

**目标代码结构**:
```
create_file_read_server()
  ├── validator = PathValidator(allowed_dirs)
  ├── @tool('read_document', ...) -> read_document_tool
  ├── @tool('list_documents', ...) -> list_documents_tool
  ├── return create_sdk_mcp_server(
  │       name=f"docuswarm-files-{node_id}",
  │       version="1.0.0",
  │       tools=[read_document_tool, list_documents_tool]
  │     )  # dict
```

**详细修改**:

```python
# file_tools.py - 修改后

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Sequence

from autoBMAD.docuswarm.exceptions import FileToolError, PathNotAllowedError
from autoBMAD.docuswarm.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)

# ... (保持现有的常量和 PathValidator 类不变)

def create_file_read_server(
    allowed_dirs: Sequence[str],
    node_id: str,
) -> dict[str, Any]:
    """Create an SDK MCP server with file reading tools.
    
    Args:
        allowed_dirs: Sequence of directory paths that the node is allowed
                     to access.
        node_id: Unique identifier for the node.
    
    Returns:
        SDK MCP server dict compatible with ClaudeAgentOptions.
    """
    if not node_id:
        raise ValueError("node_id is required")

    if not allowed_dirs:
        raise ValueError("At least one allowed directory must be provided")

    # Validate all directories
    valid_dirs: list[str] = []
    for d in allowed_dirs:
        abs_path = os.path.abspath(os.path.expanduser(d))
        if not os.path.exists(abs_path):
            logger.warning(f"Allowed directory does not exist: {d}")
        valid_dirs.append(abs_path)

    if not valid_dirs:
        raise FileToolError(
            "No valid allowed directories provided", allowed_dirs=list(allowed_dirs)
        )

    # Import SDK MCP utilities
    from claude_agent_sdk import create_sdk_mcp_server, tool

    # Create validator instance
    validator = PathValidator(valid_dirs)

    # Server name (without mcp__ prefix)
    server_name = f"docuswarm-files-{node_id}"

    @tool('read_document', 'Read the content of a document within allowed directories', {
        'type': 'object',
        'properties': {
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path to the file'
            }
        },
        'required': ['path']
    })
    async def read_document_tool(args: dict[str, Any]) -> dict[str, Any]:
        result = read_document(args['path'], validator=validator)
        if result.success:
            return {'content': [{'type': 'text', 'text': str(result.result)}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}

    @tool('list_documents', 'List all documents in an allowed directory', {
        'type': 'object',
        'properties': {
            'directory': {
                'type': 'string',
                'description': 'Directory path to list'
            },
            'recursive': {
                'type': 'boolean',
                'default': False,
                'description': 'Whether to include subdirectories'
            }
        },
        'required': ['directory']
    })
    async def list_documents_tool(args: dict[str, Any]) -> dict[str, Any]:
        recursive = args.get('recursive', False)
        result = list_documents(args['directory'], recursive=recursive, validator=validator)
        if result.success:
            # Format list as newline-separated string
            files_str = '\n'.join(result.result) if result.result else 'No files found'
            return {'content': [{'type': 'text', 'text': files_str}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}

    logger.info(f"Created SDK MCP file server for node '{node_id}' with dirs: {valid_dirs}")

    return create_sdk_mcp_server(
        name=server_name,
        version="1.0.0",
        tools=[read_document_tool, list_documents_tool]
    )
```

### 4.2 search_tools.py 迁移

**详细修改**:

```python
# search_tools.py - 修改后

from __future__ import annotations

import fnmatch
import logging
import os
import re
from pathlib import Path
from typing import Any

from autoBMAD.docuswarm.exceptions import PathNotAllowedError, SearchToolError
from autoBMAD.docuswarm.tools.file_tools import PathValidator
from autoBMAD.docuswarm.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)

# ... (保持现有的常量和辅助函数不变)

def create_search_server(
    search_dirs: list[str],
    node_id: str,
) -> dict[str, Any]:
    """Create an SDK MCP server with search tools.
    
    Args:
        search_dirs: List of directory paths that the node is allowed
                     to search within.
        node_id: Unique identifier for the node.
    
    Returns:
        SDK MCP server dict compatible with ClaudeAgentOptions.
    """
    if not node_id:
        raise ValueError("node_id is required")

    if not search_dirs:
        raise ValueError("At least one search directory must be provided")

    # Validate all directories
    valid_dirs: list[str] = []
    for d in search_dirs:
        abs_path = os.path.abspath(os.path.expanduser(d))
        if not os.path.exists(abs_path):
            logger.warning(f"Search directory does not exist: {d}")
        valid_dirs.append(abs_path)

    if not valid_dirs:
        raise SearchToolError(
            "No valid search directories provided", search_dirs=list(search_dirs)
        )

    # Import SDK MCP utilities
    from claude_agent_sdk import create_sdk_mcp_server, tool

    # Create validator instance
    validator = PathValidator(valid_dirs)

    # Server name (without mcp__ prefix)
    server_name = f"docuswarm-search-{node_id}"

    @tool('grep_search', 'Search file contents using regex pattern within allowed directories', {
        'type': 'object',
        'properties': {
            'pattern': {
                'type': 'string',
                'description': 'Regex pattern to search for (e.g., "API", "def ", "class.*:")'
            },
            'path': {
                'type': 'string',
                'description': 'Directory path to search within'
            },
            'max_results': {
                'type': 'integer',
                'default': 20,
                'minimum': 1,
                'maximum': 50,
                'description': 'Maximum number of results to return'
            }
        },
        'required': ['pattern', 'path']
    })
    async def grep_search_tool(args: dict[str, Any]) -> dict[str, Any]:
        max_results = args.get('max_results', MAX_RESULTS_DEFAULT)
        result = grep_search(
            pattern=args['pattern'],
            path=args['path'],
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            import json
            return {'content': [{'type': 'text', 'text': json.dumps(result.result, indent=2)}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}

    @tool('glob_search', 'Search files using glob pattern matching within allowed directories', {
        'type': 'object',
        'properties': {
            'pattern': {
                'type': 'string',
                'description': 'Glob pattern to match (e.g., "**/*.md", "*.txt")'
            },
            'path': {
                'type': 'string',
                'description': 'Directory path to search within'
            },
            'max_results': {
                'type': 'integer',
                'default': 20,
                'minimum': 1,
                'maximum': 50,
                'description': 'Maximum number of results to return'
            }
        },
        'required': ['pattern', 'path']
    })
    async def glob_search_tool(args: dict[str, Any]) -> dict[str, Any]:
        max_results = args.get('max_results', MAX_RESULTS_DEFAULT)
        result = glob_search(
            pattern=args['pattern'],
            path=args['path'],
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            files_str = '\n'.join(result.result) if result.result else 'No files found'
            return {'content': [{'type': 'text', 'text': files_str}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}

    logger.info(f"Created SDK MCP search server for node '{node_id}' with dirs: {valid_dirs}")

    return create_sdk_mcp_server(
        name=server_name,
        version="1.0.0",
        tools=[grep_search_tool, glob_search_tool]
    )
```

### 4.3 tool_filter.py 修改

**当前命名约定**:
```python
MCP_TOOL_NAME_FORMAT = "mcp__docuswarm-{type}-{node_id}__{tool_name}"
FILE_SERVER_NAME_FORMAT = "docuswarm-files-{node_id}"
SEARCH_SERVER_NAME_FORMAT = "docuswarm-search-{node_id}"
```

**问题**: `create_mcp_servers()` 返回 `list[Any]` (FastMCP 列表)

**修改后**:
```python
# tool_filter.py - 修改后

def create_mcp_servers(self) -> dict[str, Any]:
    """Create SDK MCP servers dict based on configured permissions.
    
    Returns:
        Dict mapping server names to SDK MCP server dicts.
        Format: {server_name: sdk_mcp_server_dict}
    """
    servers: dict[str, Any] = {}

    # Create file read server if file permissions are configured
    file_dirs = self.tool_permissions.file_permissions.allowed_read_dirs
    if file_dirs:
        try:
            file_server = create_file_read_server(
                allowed_dirs=file_dirs,
                node_id=self.node_id,
            )
            # SDK MCP server is a dict with 'name' key
            server_name = file_server['name']
            servers[server_name] = file_server
            logger.info(
                f"Created file read server for node '{self.node_id}' with dirs: {file_dirs}"
            )
        except Exception as e:
            logger.error(f"Failed to create file read server for node '{self.node_id}': {e}")
            raise

    # Create search server if search permissions are configured
    search_dirs = self.tool_permissions.search_permissions.search_dirs
    if search_dirs:
        try:
            search_server = create_search_server(
                search_dirs=search_dirs,
                node_id=self.node_id,
            )
            server_name = search_server['name']
            servers[server_name] = search_server
            logger.info(
                f"Created search server for node '{self.node_id}' with dirs: {search_dirs}"
            )
        except Exception as e:
            logger.error(f"Failed to create search server for node '{self.node_id}': {e}")
            raise

    return servers
```

### 4.4 session_manager.py 修改

**当前代码**:
```python
# session_manager.py
mcp_servers_list = node_filter.create_mcp_servers()  # 返回 list
options_dict["mcp_servers"] = {server.name: server for server in mcp_servers_list}
```

**修改后**:
```python
# session_manager.py
mcp_servers_dict = node_filter.create_mcp_servers()  # 返回 dict
options_dict["mcp_servers"] = mcp_servers_dict  # 直接使用
```

---

## 5. 验证测试脚本

```python
# test_sdk_mcp_migration.py
"""验证 SDK MCP 迁移的测试脚本"""
import asyncio
import os
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

# 导入迁移后的模块
from autoBMAD.docuswarm.tools.file_tools import create_file_read_server
from autoBMAD.docuswarm.tools.search_tools import create_search_server


async def test_file_server():
    """测试文件服务器"""
    print("=== Test: File Server ===")
    
    allowed_dirs = [os.path.abspath("d:/GITHUB/DocuSwarm/docs")]
    server = create_file_read_server(allowed_dirs, "test-node")
    
    print(f"Server type: {type(server)}")
    print(f"Server keys: {server.keys()}")
    print(f"Server name: {server['name']}")
    
    # 验证 MCP 工具命名
    expected_tools = [
        f"mcp__{server['name']}__read_document",
        f"mcp__{server['name']}__list_documents",
    ]
    print(f"Expected MCP tools: {expected_tools}")
    
    # 创建会话
    options = ClaudeAgentOptions(
        mcp_servers={server['name']: server},
        allowed_tools=expected_tools,
        max_turns=1
    )
    
    try:
        client = ClaudeSDKClient(options=options)
        await client.connect()
        print("✓ Session created successfully!")
        return True
    except Exception as e:
        print(f"✗ Session creation failed: {e}")
        return False


async def test_search_server():
    """测试搜索服务器"""
    print("\n=== Test: Search Server ===")
    
    search_dirs = [os.path.abspath("d:/GITHUB/DocuSwarm/docs")]
    server = create_search_server(search_dirs, "test-node")
    
    print(f"Server type: {type(server)}")
    print(f"Server name: {server['name']}")
    
    expected_tools = [
        f"mcp__{server['name']}__grep_search",
        f"mcp__{server['name']}__glob_search",
    ]
    print(f"Expected MCP tools: {expected_tools}")
    
    options = ClaudeAgentOptions(
        mcp_servers={server['name']: server},
        allowed_tools=expected_tools,
        max_turns=1
    )
    
    try:
        client = ClaudeSDKClient(options=options)
        await client.connect()
        print("✓ Session created successfully!")
        return True
    except Exception as e:
        print(f"✗ Session creation failed: {e}")
        return False


async def test_combined_servers():
    """测试组合服务器"""
    print("\n=== Test: Combined Servers ===")
    
    allowed_dirs = [os.path.abspath("d:/GITHUB/DocuSwarm/docs")]
    
    file_server = create_file_read_server(allowed_dirs, "test-node")
    search_server = create_search_server(allowed_dirs, "test-node")
    
    options = ClaudeAgentOptions(
        mcp_servers={
            file_server['name']: file_server,
            search_server['name']: search_server,
        },
        allowed_tools=[
            f"mcp__{file_server['name']}__read_document",
            f"mcp__{file_server['name']}__list_documents",
            f"mcp__{search_server['name']}__grep_search",
            f"mcp__{search_server['name']}__glob_search",
        ],
        max_turns=1
    )
    
    try:
        client = ClaudeSDKClient(options=options)
        await client.connect()
        print("✓ Combined session created successfully!")
        return True
    except Exception as e:
        print(f"✗ Combined session failed: {e}")
        return False


async def main():
    results = []
    results.append(await test_file_server())
    results.append(await test_search_server())
    results.append(await test_combined_servers())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 风险评估

### 6.1 兼容性风险

| 风险项 | 级别 | 缓解措施 |
|-------|-----|---------|
| 工具参数格式变化 | 低 | JSON Schema 支持所有验证需求 |
| 返回值格式变化 | 低 | 统一使用 `{'content': [...]}` 格式 |
| 命名约定变化 | 中 | 更新 `get_allowed_tools()` 方法 |
| 依赖变更 | 低 | SDK 已包含 `claude_agent_sdk` |

### 6.2 回滚策略

保留原始 FastMCP 代码，通过配置切换:

```python
# 环境变量控制
USE_SDK_MCP = os.environ.get("DOCUSWARM_USE_SDK_MCP", "true").lower() == "true"

if USE_SDK_MCP:
    from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
else:
    from autoBMAD.docuswarm.tools.file_tools import create_file_read_server
```

---

## 7. 实施时间表

| 阶段 | 任务 | 预计时间 |
|-----|------|---------|
| 1 | 修改 `file_tools.py` | 2 小时 |
| 2 | 修改 `search_tools.py` | 2 小时 |
| 3 | 修改 `tool_filter.py` | 1 小时 |
| 4 | 修改 `session_manager.py` | 0.5 小时 |
| 5 | 编写验证测试 | 1 小时 |
| 6 | 集成测试 | 2 小时 |
| **总计** | | **8.5 小时** |

---

## 8. 附录

### 8.1 SDK MCP Server 结构

```python
{
    'type': 'sdk',                    # 固定值
    'name': 'docuswarm-files-analyst', # 服务器名称
    'instance': <Server object>       # MCP Server 实例
}
```

### 8.2 MCP 工具命名规范

```
格式: mcp__{server_name}__{tool_name}

示例:
  - mcp__docuswarm-files-analyst__read_document
  - mcp__docuswarm-search-analyst__grep_search
```

### 8.3 工具返回值规范

```python
# 成功
{'content': [{'type': 'text', 'text': '结果文本'}]}

# 错误
{'content': [{'type': 'text', 'text': 'Error: 错误信息'}]}

# 多个内容块
{'content': [
    {'type': 'text', 'text': '第一部分'},
    {'type': 'text', 'text': '第二部分'}
]}
```

### 8.4 相关文档

- [Claude Agent SDK - Custom Tools](https://platform.claude.com/docs/zh-CN/agent-sdk/custom-tools)
- [Claude Agent SDK - MCP](https://platform.claude.com/docs/zh-CN/agent-sdk/mcp)
- [MCP Specification](https://modelcontextprotocol.io/)

---

**报告作者**: AI Assistant  
**版本**: 1.0  
**最后更新**: 2026-04-05
