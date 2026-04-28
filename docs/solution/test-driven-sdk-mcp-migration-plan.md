# 测试驱动方案：FastMCP 到 SDK MCP 迁移

**文档版本**: 1.0  
**创建日期**: 2026-04-05  
**目标项目**: @autoBMAD/docuswarm  
**迁移范围**: FastMCP → SDK MCP 格式  

---

## 1. 方案概述

### 1.1 背景

根据 `@docs/research/fastmcp-sdk-compatibility-issue.md` 和 `@docs/research/sdk-mcp-migration-plan-a.md` 的研究，当前 DocuSwarm 流水线因 FastMCP 与 Claude Agent SDK 的 JSON 序列化不兼容而完全阻塞。

### 1.2 测试驱动开发 (TDD) 策略

本方案采用 **先写测试，后实现代码** 的 TDD 策略，确保迁移过程的可验证性和可回滚性。

```
┌─────────────────────────────────────────────────────────────┐
│                    TDD 循环流程                              │
├─────────────────────────────────────────────────────────────┤
│  1. 编写失败测试 → 2. 实现最小代码 → 3. 测试通过 → 4. 重构   │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 方案架构

```
docs/solution/
├── test-driven-sdk-mcp-migration-plan.md    (本文档 - 总方案)
├── test-suite/
│   ├── test_file_tools_migration.py         (文件工具迁移测试)
│   ├── test_search_tools_migration.py       (搜索工具迁移测试)
│   ├── test_session_manager_integration.py  (会话管理集成测试)
│   ├── test_end_to_end_pipeline.py          (端到端流水线测试)
│   └── conftest.py                          (测试配置和夹具)
├── implementation/
│   ├── file_tools_sdk.py                    (SDK MCP 文件工具实现)
│   ├── search_tools_sdk.py                  (SDK MCP 搜索工具实现)
│   └── tool_filter_adapter.py               (工具过滤器适配器)
└── verification/
    └── migration_checklist.md               (迁移验证清单)
```

---

## 2. 测试策略设计

### 2.1 测试金字塔

```
                    /\
                   /  \
                  / E2E\          端到端测试 (1个)
                 /______\
                /        \
               / Integration\     集成测试 (3个)
              /______________\
             /                \
            /   Unit Tests      \  单元测试 (12个)
           /____________________\
```

### 2.2 测试分层

| 层级 | 测试类型 | 数量 | 目标 | 执行时间 |
|-----|---------|-----|------|---------|
| L1 | 单元测试 | 12 | 验证单个工具函数 | < 10s |
| L2 | 集成测试 | 3 | 验证组件间协作 | < 30s |
| L3 | 端到端测试 | 1 | 验证完整流水线 | < 2min |

---

## 3. 第一阶段：准备工作与环境搭建

### 3.1 创建测试目录结构

```bash
# 创建测试目录
mkdir -p docs/solution/test-suite
mkdir -p docs/solution/implementation
mkdir -p docs/solution/verification
```

### 3.2 测试配置 (conftest.py)

**文件**: `docs/solution/test-suite/conftest.py`

```python
"""测试配置和共享夹具"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

# 测试数据目录
TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestPaths:
    """测试路径管理"""
    
    @staticmethod
    def get_test_docs_dir() -> Path:
        """获取测试文档目录"""
        test_dir = TEST_DATA_DIR / "test_docs"
        test_dir.mkdir(parents=True, exist_ok=True)
        return test_dir
    
    @staticmethod
    def create_test_file(filename: str, content: str) -> Path:
        """创建测试文件"""
        file_path = TEST_DATA_DIR / "test_docs" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """创建临时测试目录"""
    temp_dir = Path(tempfile.mkdtemp(prefix="docuswarm_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_docs_dir(temp_test_dir: Path) -> Path:
    """创建示例文档目录结构"""
    docs_dir = temp_test_dir / "docs"
    docs_dir.mkdir()
    
    # 创建测试文件
    (docs_dir / "readme.md").write_text("# Test Project\n\nThis is a test.")
    (docs_dir / "guide.md").write_text("## Guide\n\nInstructions here.")
    
    subdir = docs_dir / "api"
    subdir.mkdir()
    (subdir / "reference.md").write_text("# API Reference\n\nAPI docs.")
    
    return docs_dir


@pytest.fixture
def allowed_dirs(sample_docs_dir: Path) -> list[str]:
    """返回允许访问的目录列表"""
    return [str(sample_docs_dir)]


@pytest.fixture
def node_id() -> str:
    """测试节点ID"""
    return "test-node-001"


# ==================== SDK MCP 兼容检查 ====================

@pytest.fixture
def check_sdk_available() -> bool:
    """检查 SDK 是否可用"""
    try:
        import claude_agent_sdk
        return True
    except ImportError:
        return False


@pytest.fixture
def skip_if_no_sdk(check_sdk_available: bool):
    """如果没有 SDK 则跳过测试"""
    if not check_sdk_available:
        pytest.skip("claude_agent_sdk not available")
```

---

## 4. 第二阶段：单元测试套件

### 4.1 文件工具迁移测试

**文件**: `docs/solution/test-suite/test_file_tools_migration.py`

```python
"""文件工具迁移测试 - TDD Phase 1

测试目标:
1. 验证 SDK MCP 格式的服务器创建
2. 验证工具命名约定正确
3. 验证返回值格式符合 SDK 规范
4. 验证路径验证功能正常工作
"""
import pytest
import asyncio
import json
from pathlib import Path
from typing import Any


class TestFileServerCreation:
    """测试文件服务器创建"""
    
    def test_create_file_server_returns_dict(self, allowed_dirs: list[str], node_id: str):
        """TEST-001: 创建的服务器必须是 dict 类型"""
        # Arrange & Act
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server(allowed_dirs, node_id)
        
        # Assert
        assert isinstance(server, dict), f"Expected dict, got {type(server)}"
    
    def test_file_server_has_required_keys(self, allowed_dirs: list[str], node_id: str):
        """TEST-002: 服务器必须包含必要的键"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server(allowed_dirs, node_id)
        
        required_keys = ['type', 'name', 'instance']
        for key in required_keys:
            assert key in server, f"Missing required key: {key}"
    
    def test_file_server_type_is_sdk(self, allowed_dirs: list[str], node_id: str):
        """TEST-003: 服务器类型必须是 'sdk'"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server(allowed_dirs, node_id)
        
        assert server['type'] == 'sdk'
    
    def test_file_server_name_format(self, allowed_dirs: list[str], node_id: str):
        """TEST-004: 服务器名称格式必须正确"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server(allowed_dirs, node_id)
        
        expected_name = f"docuswarm-files-{node_id}"
        assert server['name'] == expected_name


class TestReadDocumentTool:
    """测试 read_document 工具"""
    
    @pytest.mark.asyncio
    async def test_read_document_success(self, sample_docs_dir: Path, node_id: str):
        """TEST-005: 成功读取文档返回正确格式"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server([str(sample_docs_dir)], node_id)
        
        # 获取工具函数
        tools = server.get('tools', [])
        read_doc_tool = next((t for t in tools if t.name == 'read_document'), None)
        
        assert read_doc_tool is not None, "read_document tool not found"
        
        # 执行工具
        result = await read_doc_tool.func({'path': 'readme.md'})
        
        # 验证返回格式
        assert 'content' in result
        assert isinstance(result['content'], list)
        assert len(result['content']) > 0
        assert result['content'][0]['type'] == 'text'
        assert '# Test Project' in result['content'][0]['text']
    
    @pytest.mark.asyncio
    async def test_read_document_not_allowed_path(self, sample_docs_dir: Path, node_id: str):
        """TEST-006: 读取不允许的路径返回错误"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        read_doc_tool = next((t for t in tools if t.name == 'read_document'), None)
        
        # 尝试读取不允许的路径
        result = await read_doc_tool.func({'path': '/etc/passwd'})
        
        assert 'content' in result
        assert 'Error' in result['content'][0]['text']
    
    @pytest.mark.asyncio
    async def test_read_document_not_found(self, sample_docs_dir: Path, node_id: str):
        """TEST-007: 读取不存在的文件返回错误"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        read_doc_tool = next((t for t in tools if t.name == 'read_document'), None)
        
        result = await read_doc_tool.func({'path': 'nonexistent.md'})
        
        assert 'content' in result
        assert 'Error' in result['content'][0]['text']


class TestListDocumentsTool:
    """测试 list_documents 工具"""
    
    @pytest.mark.asyncio
    async def test_list_documents_non_recursive(self, sample_docs_dir: Path, node_id: str):
        """TEST-008: 非递归列出文档"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        list_tool = next((t for t in tools if t.name == 'list_documents'), None)
        
        result = await list_tool.func({'directory': '.', 'recursive': False})
        
        assert 'content' in result
        text = result['content'][0]['text']
        assert 'readme.md' in text or 'guide.md' in text
    
    @pytest.mark.asyncio
    async def test_list_documents_recursive(self, sample_docs_dir: Path, node_id: str):
        """TEST-009: 递归列出文档包含子目录"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        list_tool = next((t for t in tools if t.name == 'list_documents'), None)
        
        result = await list_tool.func({'directory': '.', 'recursive': True})
        
        assert 'content' in result
        text = result['content'][0]['text']
        # 应该包含子目录中的文件
        assert 'reference.md' in text or 'api/reference.md' in text


class TestFileToolsValidation:
    """测试输入验证"""
    
    def test_empty_node_id_raises_error(self, allowed_dirs: list[str]):
        """TEST-010: 空 node_id 应该抛出错误"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        with pytest.raises(ValueError, match="node_id is required"):
            create_file_read_server(allowed_dirs, "")
    
    def test_empty_allowed_dirs_raises_error(self, node_id: str):
        """TEST-011: 空 allowed_dirs 应该抛出错误"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        with pytest.raises(ValueError, match="At least one allowed directory"):
            create_file_read_server([], node_id)
    
    def test_nonexistent_dir_logs_warning(self, node_id: str, temp_test_dir: Path, caplog):
        """TEST-012: 不存在的目录应该记录警告"""
        import logging
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        nonexistent = str(temp_test_dir / "nonexistent")
        
        with caplog.at_level(logging.WARNING):
            create_file_read_server([nonexistent], node_id)
        
        assert "does not exist" in caplog.text
```

### 4.2 搜索工具迁移测试

**文件**: `docs/solution/test-suite/test_search_tools_migration.py`

```python
"""搜索工具迁移测试 - TDD Phase 2

测试目标:
1. 验证 grep_search 工具功能
2. 验证 glob_search 工具功能
3. 验证搜索结果返回格式
"""
import pytest
import json
from pathlib import Path


class TestSearchServerCreation:
    """测试搜索服务器创建"""
    
    def test_create_search_server_returns_dict(self, allowed_dirs: list[str], node_id: str):
        """TEST-013: 创建的服务器必须是 dict 类型"""
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        server = create_search_server(allowed_dirs, node_id)
        
        assert isinstance(server, dict)
    
    def test_search_server_name_format(self, allowed_dirs: list[str], node_id: str):
        """TEST-014: 服务器名称格式正确"""
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        server = create_search_server(allowed_dirs, node_id)
        
        expected_name = f"docuswarm-search-{node_id}"
        assert server['name'] == expected_name


class TestGrepSearchTool:
    """测试 grep_search 工具"""
    
    @pytest.mark.asyncio
    async def test_grep_search_finds_pattern(self, sample_docs_dir: Path, node_id: str):
        """TEST-015: grep_search 能找到匹配内容"""
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        server = create_search_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        grep_tool = next((t for t in tools if t.name == 'grep_search'), None)
        
        result = await grep_tool.func({
            'pattern': 'Test',
            'path': '.',
            'max_results': 10
        })
        
        assert 'content' in result
        # 结果应该是 JSON 格式
        results_data = json.loads(result['content'][0]['text'])
        assert len(results_data) > 0
    
    @pytest.mark.asyncio
    async def test_grep_search_respects_max_results(self, sample_docs_dir: Path, node_id: str):
        """TEST-016: grep_search 遵守 max_results 限制"""
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        # 创建包含多个匹配的文件
        for i in range(5):
            (sample_docs_dir / f"test{i}.md").write_text(f"Test content {i}")
        
        server = create_search_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        grep_tool = next((t for t in tools if t.name == 'grep_search'), None)
        
        result = await grep_tool.func({
            'pattern': 'Test',
            'path': '.',
            'max_results': 3
        })
        
        results_data = json.loads(result['content'][0]['text'])
        assert len(results_data) <= 3


class TestGlobSearchTool:
    """测试 glob_search 工具"""
    
    @pytest.mark.asyncio
    async def test_glob_search_finds_files(self, sample_docs_dir: Path, node_id: str):
        """TEST-017: glob_search 能找到匹配文件"""
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        server = create_search_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        glob_tool = next((t for t in tools if t.name == 'glob_search'), None)
        
        result = await glob_tool.func({
            'pattern': '*.md',
            'path': '.',
            'max_results': 10
        })
        
        assert 'content' in result
        text = result['content'][0]['text']
        assert '.md' in text
    
    @pytest.mark.asyncio
    async def test_glob_search_recursive_pattern(self, sample_docs_dir: Path, node_id: str):
        """TEST-018: glob_search 支持递归模式"""
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        server = create_search_server([str(sample_docs_dir)], node_id)
        tools = server.get('tools', [])
        glob_tool = next((t for t in tools if t.name == 'glob_search'), None)
        
        result = await glob_tool.func({
            'pattern': '**/*.md',
            'path': '.',
            'max_results': 10
        })
        
        text = result['content'][0]['text']
        # 应该包含子目录中的 .md 文件
        assert 'reference.md' in text or 'api' in text
```

---

## 5. 第三阶段：集成测试套件

### 5.1 会话管理集成测试

**文件**: `docs/solution/test-suite/test_session_manager_integration.py`

```python
"""会话管理集成测试 - TDD Phase 3

测试目标:
1. 验证 SDK MCP 服务器能正确配置到 ClaudeAgentOptions
2. 验证 ClaudeSDKClient 能成功创建会话
3. 验证工具过滤器与 SDK MCP 兼容
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Any


class TestSDKMCPWithAgentOptions:
    """测试 SDK MCP 与 Agent Options 集成"""
    
    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('claude_agent_sdk'),
        reason="claude_agent_sdk not available"
    )
    def test_sdk_mcp_server_compatible_with_options(self, allowed_dirs: list[str], node_id: str):
        """TEST-019: SDK MCP 服务器与 ClaudeAgentOptions 兼容"""
        from claude_agent_sdk import ClaudeAgentOptions
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server(allowed_dirs, node_id)
        
        # 应该能成功创建 options，不抛出序列化错误
        options = ClaudeAgentOptions(
            mcp_servers={server['name']: server},
            max_turns=1
        )
        
        assert options is not None
        assert server['name'] in options.mcp_servers
    
    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('claude_agent_sdk'),
        reason="claude_agent_sdk not available"
    )
    @pytest.mark.asyncio
    async def test_sdk_mcp_client_connect_success(self, allowed_dirs: list[str], node_id: str):
        """TEST-020: SDK MCP 支持 ClaudeSDKClient 成功连接"""
        from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        
        server = create_file_read_server(allowed_dirs, node_id)
        
        options = ClaudeAgentOptions(
            mcp_servers={server['name']: server},
            max_turns=1
        )
        
        # 应该能成功创建客户端和连接，不抛出 TypeError
        client = ClaudeSDKClient(options=options)
        
        try:
            await client.connect()
            assert True, "Connection successful"
        except TypeError as e:
            if "not JSON serializable" in str(e):
                pytest.fail(f"JSON serialization error: {e}")
            raise
        finally:
            await client.close()


class TestToolFilterIntegration:
    """测试工具过滤器集成"""
    
    def test_tool_filter_returns_dict(self, allowed_dirs: list[str], node_id: str):
        """TEST-021: 工具过滤器返回 dict 而不是 list"""
        from autoBMAD.docuswarm.llm.tool_filter_sdk import NodeToolFilter
        from autoBMAD.docuswarm.context.permissions import (
            NodeToolPermissions,
            FilePermissions,
            SearchPermissions,
        )
        
        permissions = NodeToolPermissions(
            file_permissions=FilePermissions(allowed_read_dirs=allowed_dirs),
            search_permissions=SearchPermissions(search_dirs=allowed_dirs)
        )
        
        filter_obj = NodeToolFilter(node_id=node_id, tool_permissions=permissions)
        servers = filter_obj.create_mcp_servers()
        
        assert isinstance(servers, dict), f"Expected dict, got {type(servers)}"
    
    def test_tool_filter_server_names_correct(self, allowed_dirs: list[str], node_id: str):
        """TEST-022: 工具过滤器返回正确的服务器名称"""
        from autoBMAD.docuswarm.llm.tool_filter_sdk import NodeToolFilter
        from autoBMAD.docuswarm.context.permissions import (
            NodeToolPermissions,
            FilePermissions,
            SearchPermissions,
        )
        
        permissions = NodeToolPermissions(
            file_permissions=FilePermissions(allowed_read_dirs=allowed_dirs),
            search_permissions=SearchPermissions(search_dirs=allowed_dirs)
        )
        
        filter_obj = NodeToolFilter(node_id=node_id, tool_permissions=permissions)
        servers = filter_obj.create_mcp_servers()
        
        expected_file_server = f"docuswarm-files-{node_id}"
        expected_search_server = f"docuswarm-search-{node_id}"
        
        assert expected_file_server in servers
        assert expected_search_server in servers
    
    def test_tool_filter_mcp_tool_names(self, allowed_dirs: list[str], node_id: str):
        """TEST-023: 工具过滤器生成正确的 MCP 工具名"""
        from autoBMAD.docuswarm.llm.tool_filter_sdk import NodeToolFilter
        from autoBMAD.docuswarm.context.permissions import (
            NodeToolPermissions,
            FilePermissions,
            SearchPermissions,
        )
        
        permissions = NodeToolPermissions(
            file_permissions=FilePermissions(allowed_read_dirs=allowed_dirs),
            search_permissions=SearchPermissions(search_dirs=allowed_dirs)
        )
        
        filter_obj = NodeToolFilter(node_id=node_id, tool_permissions=permissions)
        tool_names = filter_obj.get_allowed_tools()
        
        # 验证 SDK MCP 工具命名格式: mcp__{server_name}__{tool_name}
        file_server = f"docuswarm-files-{node_id}"
        search_server = f"docuswarm-search-{node_id}"
        
        assert f"mcp__{file_server}__read_document" in tool_names
        assert f"mcp__{file_server}__list_documents" in tool_names
        assert f"mcp__{search_server}__grep_search" in tool_names
        assert f"mcp__{search_server}__glob_search" in tool_names
```

---

## 6. 第四阶段：端到端测试

### 6.1 完整流水线测试

**文件**: `docs/solution/test-suite/test_end_to_end_pipeline.py`

```python
"""端到端流水线测试 - TDD Phase 4

测试目标:
1. 验证完整流水线能正常启动
2. 验证节点能成功创建会话
3. 验证 MCP 工具在会话中可用
"""
import pytest
import asyncio
from pathlib import Path


class TestPipelineWithSDKMCP:
    """使用 SDK MCP 的流水线端到端测试"""
    
    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('claude_agent_sdk'),
        reason="claude_agent_sdk not available"
    )
    @pytest.mark.asyncio
    async def test_combined_servers_session_creation(self, sample_docs_dir: Path, node_id: str):
        """TEST-024: 组合服务器能成功创建会话"""
        from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        file_server = create_file_read_server([str(sample_docs_dir)], node_id)
        search_server = create_search_server([str(sample_docs_dir)], node_id)
        
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
        
        client = ClaudeSDKClient(options=options)
        
        try:
            await client.connect()
            print("✓ Combined session created successfully!")
        finally:
            await client.close()
    
    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('claude_agent_sdk'),
        reason="claude_agent_sdk not available"
    )
    @pytest.mark.asyncio
    async def test_session_manager_integration(self, sample_docs_dir: Path, node_id: str):
        """TEST-025: SessionManager 能使用 SDK MCP 创建会话"""
        from autoBMAD.docuswarm.llm.session_manager_sdk import SessionManager
        from autoBMAD.docuswarm.context.permissions import (
            NodeToolPermissions,
            FilePermissions,
            SearchPermissions,
        )
        
        permissions = NodeToolPermissions(
            file_permissions=FilePermissions(allowed_read_dirs=[str(sample_docs_dir)]),
            search_permissions=SearchPermissions(search_dirs=[str(sample_docs_dir)])
        )
        
        session_manager = SessionManager(
            node_id=node_id,
            tool_permissions=permissions,
            mode="sdk"  # 使用 SDK MCP 模式
        )
        
        # 应该能成功创建选项，不抛出 JSON 序列化错误
        options = session_manager._create_options()
        
        assert options is not None
        assert hasattr(options, 'mcp_servers')


class TestMigrationVerification:
    """迁移验证测试"""
    
    def test_no_fastmcp_in_sdk_mode(self, sample_docs_dir: Path, node_id: str):
        """TEST-026: SDK 模式下不使用 FastMCP 对象"""
        from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
        from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
        
        file_server = create_file_read_server([str(sample_docs_dir)], node_id)
        search_server = create_search_server([str(sample_docs_dir)], node_id)
        
        # 验证不是 FastMCP 类型
        fastmcp_module = 'mcp.server.fastmcp'
        fastmcp_class = 'FastMCP'
        
        assert type(file_server).__name__ == 'dict'
        assert type(search_server).__name__ == 'dict'
        
        assert file_server['type'] == 'sdk'
        assert search_server['type'] == 'sdk'
```

---

## 7. 第五阶段：实现代码

### 7.1 文件工具 SDK MCP 实现

**文件**: `docs/solution/implementation/file_tools_sdk.py`

```python
"""SDK MCP 格式的文件工具实现

实现目标:
1. 完全兼容 claude_agent_sdk 的 @tool 装饰器
2. 返回 dict 类型的服务器配置
3. 遵循 SDK MCP 工具命名约定
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Sequence

from autoBMAD.docuswarm.exceptions import FileToolError
from autoBMAD.docuswarm.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)

DEFAULT_ENCODING = "utf-8"
MAX_FILE_SIZE = 1024 * 1024  # 1MB


class PathValidator:
    """路径验证器 - 保持与原始实现一致"""
    
    def __init__(self, allowed_dirs: Sequence[str]):
        self.allowed_dirs = [os.path.abspath(os.path.expanduser(d)) for d in allowed_dirs]
    
    def validate(self, path: str) -> Path:
        """验证路径是否在允许目录内"""
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        for allowed in self.allowed_dirs:
            if abs_path.startswith(allowed):
                return Path(abs_path)
        
        raise FileToolError(f"Path not allowed: {path}")


def read_document(path: str, validator: PathValidator) -> ToolResult:
    """读取文档实现"""
    try:
        file_path = validator.validate(path)
        
        if not file_path.exists():
            return ToolResult(success=False, error=f"File not found: {path}")
        
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return ToolResult(success=False, error=f"File too large: {path}")
        
        content = file_path.read_text(encoding=DEFAULT_ENCODING)
        return ToolResult(success=True, result=content)
        
    except FileToolError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        return ToolResult(success=False, error=f"Read error: {e}")


def list_documents(directory: str, recursive: bool, validator: PathValidator) -> ToolResult:
    """列出文档实现"""
    try:
        dir_path = validator.validate(directory)
        
        if not dir_path.exists():
            return ToolResult(success=False, error=f"Directory not found: {directory}")
        
        if not dir_path.is_dir():
            return ToolResult(success=False, error=f"Not a directory: {directory}")
        
        files: list[str] = []
        
        if recursive:
            for item in dir_path.rglob("*"):
                if item.is_file():
                    # 返回相对于允许目录的路径
                    files.append(str(item.relative_to(dir_path)))
        else:
            for item in dir_path.iterdir():
                if item.is_file():
                    files.append(item.name)
        
        return ToolResult(success=True, result=sorted(files))
        
    except FileToolError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        return ToolResult(success=False, error=f"List error: {e}")


def create_file_read_server(
    allowed_dirs: Sequence[str],
    node_id: str,
) -> dict[str, Any]:
    """创建 SDK MCP 文件读取服务器
    
    Args:
        allowed_dirs: 允许访问的目录列表
        node_id: 节点唯一标识
        
    Returns:
        SDK MCP 服务器配置 dict
        
    Raises:
        ValueError: node_id 为空或 allowed_dirs 为空
        FileToolError: 没有有效的允许目录
    """
    if not node_id:
        raise ValueError("node_id is required")
    
    if not allowed_dirs:
        raise ValueError("At least one allowed directory must be provided")
    
    # 验证目录
    valid_dirs: list[str] = []
    for d in allowed_dirs:
        abs_path = os.path.abspath(os.path.expanduser(d))
        if not os.path.exists(abs_path):
            logger.warning(f"Allowed directory does not exist: {d}")
        valid_dirs.append(abs_path)
    
    if not valid_dirs:
        raise FileToolError("No valid allowed directories provided", allowed_dirs=list(allowed_dirs))
    
    # 导入 SDK MCP 工具
    from claude_agent_sdk import create_sdk_mcp_server, tool
    
    # 创建验证器
    validator = PathValidator(valid_dirs)
    
    # 服务器名称 (不含 mcp__ 前缀)
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
        """读取文档工具"""
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
        """列出文档工具"""
        recursive = args.get('recursive', False)
        result = list_documents(args['directory'], recursive=recursive, validator=validator)
        if result.success:
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

### 7.2 搜索工具 SDK MCP 实现

**文件**: `docs/solution/implementation/search_tools_sdk.py`

```python
"""SDK MCP 格式的搜索工具实现"""
from __future__ import annotations

import fnmatch
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from autoBMAD.docuswarm.exceptions import PathNotAllowedError, SearchToolError
from autoBMAD.docuswarm.tools.file_tools import PathValidator
from autoBMAD.docuswarm.tools.tool_result import ToolResult

logger = logging.getLogger(__name__)

MAX_RESULTS_DEFAULT = 20
MAX_RESULTS_LIMIT = 50


def grep_search(
    pattern: str,
    path: str,
    validator: PathValidator,
    max_results: int = MAX_RESULTS_DEFAULT
) -> ToolResult:
    """Grep 搜索实现"""
    try:
        search_path = validator.validate(path)
        
        if not search_path.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        
        results: list[dict] = []
        compiled_pattern = re.compile(pattern)
        
        files_to_search = search_path.rglob("*") if search_path.is_dir() else [search_path]
        
        for file_path in files_to_search:
            if not file_path.is_file():
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(content.splitlines(), 1):
                    if compiled_pattern.search(line):
                        results.append({
                            'file': str(file_path.relative_to(search_path)),
                            'line': i,
                            'content': line.strip()
                        })
                        if len(results) >= max_results:
                            return ToolResult(success=True, result=results)
            except Exception:
                continue
        
        return ToolResult(success=True, result=results)
        
    except Exception as e:
        return ToolResult(success=False, error=f"Search error: {e}")


def glob_search(
    pattern: str,
    path: str,
    validator: PathValidator,
    max_results: int = MAX_RESULTS_DEFAULT
) -> ToolResult:
    """Glob 搜索实现"""
    try:
        search_path = validator.validate(path)
        
        if not search_path.exists():
            return ToolResult(success=False, error=f"Path not found: {path}")
        
        results: list[str] = []
        
        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(search_path))
                if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                    results.append(relative_path)
                    if len(results) >= max_results:
                        break
        
        return ToolResult(success=True, result=sorted(results))
        
    except Exception as e:
        return ToolResult(success=False, error=f"Search error: {e}")


def create_search_server(
    search_dirs: list[str],
    node_id: str,
) -> dict[str, Any]:
    """创建 SDK MCP 搜索服务器"""
    if not node_id:
        raise ValueError("node_id is required")
    
    if not search_dirs:
        raise ValueError("At least one search directory must be provided")
    
    # 验证目录
    valid_dirs: list[str] = []
    for d in search_dirs:
        abs_path = os.path.abspath(os.path.expanduser(d))
        if not os.path.exists(abs_path):
            logger.warning(f"Search directory does not exist: {d}")
        valid_dirs.append(abs_path)
    
    if not valid_dirs:
        raise SearchToolError("No valid search directories provided", search_dirs=list(search_dirs))
    
    # 导入 SDK MCP 工具
    from claude_agent_sdk import create_sdk_mcp_server, tool
    
    validator = PathValidator(valid_dirs)
    server_name = f"docuswarm-search-{node_id}"
    
    @tool('grep_search', 'Search file contents using regex pattern', {
        'type': 'object',
        'properties': {
            'pattern': {
                'type': 'string',
                'description': 'Regex pattern to search for'
            },
            'path': {
                'type': 'string',
                'description': 'Directory path to search within'
            },
            'max_results': {
                'type': 'integer',
                'default': MAX_RESULTS_DEFAULT,
                'minimum': 1,
                'maximum': MAX_RESULTS_LIMIT,
                'description': 'Maximum number of results'
            }
        },
        'required': ['pattern', 'path']
    })
    async def grep_search_tool(args: dict[str, Any]) -> dict[str, Any]:
        max_results = min(args.get('max_results', MAX_RESULTS_DEFAULT), MAX_RESULTS_LIMIT)
        result = grep_search(
            pattern=args['pattern'],
            path=args['path'],
            validator=validator,
            max_results=max_results,
        )
        if result.success:
            return {'content': [{'type': 'text', 'text': json.dumps(result.result, indent=2)}]}
        return {'content': [{'type': 'text', 'text': f"Error: {result.error}"}]}
    
    @tool('glob_search', 'Search files using glob pattern matching', {
        'type': 'object',
        'properties': {
            'pattern': {
                'type': 'string',
                'description': 'Glob pattern to match (e.g., "**/*.md")'
            },
            'path': {
                'type': 'string',
                'description': 'Directory path to search within'
            },
            'max_results': {
                'type': 'integer',
                'default': MAX_RESULTS_DEFAULT,
                'minimum': 1,
                'maximum': MAX_RESULTS_LIMIT,
                'description': 'Maximum number of results'
            }
        },
        'required': ['pattern', 'path']
    })
    async def glob_search_tool(args: dict[str, Any]) -> dict[str, Any]:
        max_results = min(args.get('max_results', MAX_RESULTS_DEFAULT), MAX_RESULTS_LIMIT)
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

### 7.3 工具过滤器适配器

**文件**: `docs/solution/implementation/tool_filter_adapter.py`

```python
"""工具过滤器适配器 - SDK MCP 版本

适配目标:
1. 修改 create_mcp_servers() 返回 dict 而不是 list
2. 更新工具命名约定
3. 使用新的 SDK MCP 工具创建函数
"""
from __future__ import annotations

import logging
from typing import Any

from autoBMAD.docuswarm.context.permissions import NodeToolPermissions

logger = logging.getLogger(__name__)


class NodeToolFilter:
    """节点工具过滤器 - SDK MCP 版本"""
    
    def __init__(self, node_id: str, tool_permissions: NodeToolPermissions):
        self.node_id = node_id
        self.tool_permissions = tool_permissions
    
    def create_mcp_servers(self) -> dict[str, Any]:
        """创建 SDK MCP 服务器字典
        
        Returns:
            Dict mapping server names to SDK MCP server dicts.
            Format: {server_name: sdk_mcp_server_dict}
        """
        servers: dict[str, Any] = {}
        
        # 创建文件读取服务器
        file_dirs = self.tool_permissions.file_permissions.allowed_read_dirs
        if file_dirs:
            try:
                from autoBMAD.docuswarm.tools.file_tools_sdk import create_file_read_server
                
                file_server = create_file_read_server(
                    allowed_dirs=file_dirs,
                    node_id=self.node_id,
                )
                server_name = file_server['name']
                servers[server_name] = file_server
                logger.info(f"Created file read server for node '{self.node_id}' with dirs: {file_dirs}")
            except Exception as e:
                logger.error(f"Failed to create file read server for node '{self.node_id}': {e}")
                raise
        
        # 创建搜索服务器
        search_dirs = self.tool_permissions.search_permissions.search_dirs
        if search_dirs:
            try:
                from autoBMAD.docuswarm.tools.search_tools_sdk import create_search_server
                
                search_server = create_search_server(
                    search_dirs=search_dirs,
                    node_id=self.node_id,
                )
                server_name = search_server['name']
                servers[server_name] = search_server
                logger.info(f"Created search server for node '{self.node_id}' with dirs: {search_dirs}")
            except Exception as e:
                logger.error(f"Failed to create search server for node '{self.node_id}': {e}")
                raise
        
        return servers
    
    def get_allowed_tools(self) -> list[str]:
        """获取允许的工具列表
        
        Returns:
            完整的工具名称列表，格式: mcp__{server_name}__{tool_name}
        """
        tools: list[str] = []
        
        # 文件工具
        file_server_name = f"docuswarm-files-{self.node_id}"
        if self.tool_permissions.file_permissions.allowed_read_dirs:
            tools.extend([
                f"mcp__{file_server_name}__read_document",
                f"mcp__{file_server_name}__list_documents",
            ])
        
        # 搜索工具
        search_server_name = f"docuswarm-search-{self.node_id}"
        if self.tool_permissions.search_permissions.search_dirs:
            tools.extend([
                f"mcp__{search_server_name}__grep_search",
                f"mcp__{search_server_name}__glob_search",
            ])
        
        return tools
```

---

## 8. 第六阶段：迁移验证清单

**文件**: `docs/solution/verification/migration_checklist.md`

```markdown
# FastMCP → SDK MCP 迁移验证清单

## 前置条件检查

- [ ] Python 环境 >= 3.10
- [ ] claude_agent_sdk 已安装
- [ ] 原始 FastMCP 代码已备份
- [ ] 测试环境配置完成

## 第一阶段：单元测试验证

### 文件工具测试 (test_file_tools_migration.py)

- [ ] TEST-001: create_file_read_server 返回 dict 类型
- [ ] TEST-002: 服务器包含 type/name/instance 键
- [ ] TEST-003: 服务器 type 为 'sdk'
- [ ] TEST-004: 服务器名称格式正确 (docuswarm-files-{node_id})
- [ ] TEST-005: read_document 成功读取返回正确格式
- [ ] TEST-006: read_document 拒绝不允许的路径
- [ ] TEST-007: read_document 处理不存在的文件
- [ ] TEST-008: list_documents 非递归模式工作正常
- [ ] TEST-009: list_documents 递归模式工作正常
- [ ] TEST-010: 空 node_id 抛出 ValueError
- [ ] TEST-011: 空 allowed_dirs 抛出 ValueError
- [ ] TEST-012: 不存在的目录记录警告

### 搜索工具测试 (test_search_tools_migration.py)

- [ ] TEST-013: create_search_server 返回 dict 类型
- [ ] TEST-014: 服务器名称格式正确 (docuswarm-search-{node_id})
- [ ] TEST-015: grep_search 能找到匹配内容
- [ ] TEST-016: grep_search 遵守 max_results 限制
- [ ] TEST-017: glob_search 能找到匹配文件
- [ ] TEST-018: glob_search 支持递归模式

## 第二阶段：集成测试验证

### 会话管理集成 (test_session_manager_integration.py)

- [ ] TEST-019: SDK MCP 服务器与 ClaudeAgentOptions 兼容
- [ ] TEST-020: ClaudeSDKClient 能成功连接
- [ ] TEST-021: 工具过滤器返回 dict 类型
- [ ] TEST-022: 工具过滤器返回正确的服务器名称
- [ ] TEST-023: 工具过滤器生成正确的 MCP 工具名

## 第三阶段：端到端测试验证

### 完整流水线测试 (test_end_to_end_pipeline.py)

- [ ] TEST-024: 组合服务器能成功创建会话
- [ ] TEST-025: SessionManager 能使用 SDK MCP 创建会话
- [ ] TEST-026: SDK 模式下不使用 FastMCP 对象

## 性能验证

- [ ] 会话创建时间 < 2s
- [ ] 工具执行延迟 < 500ms (本地文件)
- [ ] 内存使用无异常增长

## 回滚准备

- [ ] 原始 FastMCP 代码已备份到 .backup/ 目录
- [ ] 环境变量切换机制已测试
- [ ] 回滚脚本已准备

## 文档更新

- [ ] API 文档已更新
- [ ] 部署指南已更新
- [ ] 故障排查文档已更新

## 最终确认

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 性能测试通过
- [ ] 文档已更新
- [ ] 回滚方案已验证
```

---

## 9. 实施路线图

### 9.1 时间线

```
Day 1: 准备工作
├── 创建测试目录结构
├── 编写 conftest.py
└── 编写所有测试用例 (预期失败)

Day 2: 文件工具迁移
├── 实现 file_tools_sdk.py
├── 运行单元测试 TEST-001 ~ TEST-012
└── 修复失败的测试

Day 3: 搜索工具迁移
├── 实现 search_tools_sdk.py
├── 运行单元测试 TEST-013 ~ TEST-018
└── 修复失败的测试

Day 4: 集成层迁移
├── 实现 tool_filter_adapter.py
├── 修改 session_manager.py
├── 运行集成测试 TEST-019 ~ TEST-023
└── 修复失败的测试

Day 5: 端到端验证
├── 运行端到端测试 TEST-024 ~ TEST-026
├── 性能验证
├── 完整流水线测试
└── 编写迁移报告
```

### 9.2 风险缓解

| 风险 | 影响 | 缓解措施 |
|-----|-----|---------|
| SDK API 变更 | 高 | 使用版本锁定，编写适配层 |
| 测试覆盖不足 | 中 | TDD 确保测试先行，覆盖率 > 90% |
| 性能退化 | 中 | 基准测试对比，回滚机制 |
| 依赖冲突 | 低 | 隔离测试环境，虚拟环境验证 |

---

## 10. 附录

### 10.1 快速命令参考

```bash
# 运行所有测试
pytest docs/solution/test-suite/ -v

# 运行特定测试文件
pytest docs/solution/test-suite/test_file_tools_migration.py -v

# 运行标记为失败的测试
pytest docs/solution/test-suite/ --tb=short

# 生成覆盖率报告
pytest docs/solution/test-suite/ --cov=autoBMAD.docuswarm --cov-report=html
```

### 10.2 环境变量配置

```bash
# 启用 SDK MCP 模式 (默认)
export DOCUSWARM_USE_SDK_MCP=true

# 回退到 FastMCP (临时)
export DOCUSWARM_USE_SDK_MCP=false

# 调试模式
export DOCUSWARM_DEBUG=1
```

### 10.3 相关文档链接

- [FastMCP 兼容性问题研究](../research/fastmcp-sdk-compatibility-issue.md)
- [SDK MCP 迁移方案 A](../research/sdk-mcp-migration-plan-a.md)
- [Claude Agent SDK 文档](https://platform.claude.com/docs/zh-CN/agent-sdk/mcp)

---

**方案制定**: AI Assistant  
**最后更新**: 2026-04-05
