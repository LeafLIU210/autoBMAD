# P2: @docs 文档修改能力 — 测试驱动开发方案

**优先级**: P2 (Enhancement)  
**预估工时**: 90 分钟  
**依赖**: [P0](./P0-Output目录统一-TDD方案.md), [P1](./P1-Context_File传递-TDD方案.md)  
**影响范围**: Agent 文档操作能力

---

## 目录

1. [需求描述](#1-需求描述)
2. [技术设计](#2-技术设计)
3. [工具实现](#3-工具实现)
4. [TDD 测试用例](#4-tdd-测试用例)
5. [实施步骤](#5-实施步骤)
6. [安全考虑](#6-安全考虑)
7. [验证清单](#7-验证清单)

---

## 1. 需求描述

### 1.1 需求背景

当前 Agent 只能通过 `create_deliverable` 工具在 `autoBMAD/output/{pipeline_id}/` 目录创建新文档，无法读取或修改项目 `@docs` 目录下的现有文档。

### 1.2 应用场景

| 场景 | 描述 |
|------|------|
| 更新架构文档 | Agent 根据新的设计决策更新 `docs/architecture/` 下的文档 |
| 补充 API 文档 | 根据代码变更同步 API 规范文档 |
| 修订设计规范 | 更新设计约束和规范文档 |
| 同步代码与文档 | 确保文档与代码实现保持一致 |

### 1.3 功能需求

创建三个工具:

| 工具 | 功能 | 参数 |
|------|------|------|
| `read_docs_file` | 读取 @docs 目录文件 | `file_path` |
| `update_docs_file` | 更新 @docs 目录文件 | `file_path`, `old_content`, `new_content`, `create_backup` |
| `list_docs_files` | 列出 @docs 目录文件 | `directory`, `pattern`, `recursive` |

### 1.4 安全要求

- **路径隔离**: 只能访问 `docs/` 目录
- **路径穿越防护**: 防止 `../` 等路径穿越攻击
- **内容验证**: 更新前验证原内容匹配
- **自动备份**: 更新前自动创建备份
- **原子写入**: 使用临时文件 + 重命名保证原子性

---

## 2. 技术设计

### 2.1 工具架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent (IndependentAgent)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ ReadDocsFileTool│  │UpdateDocsFileTool│  │ListDocsFiles│  │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘  │
│           │                    │                   │         │
│           ▼                    ▼                   ▼         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Security Layer (Path Validation)           ││
│  │  - resolve() + startswith() check                       ││
│  │  - Symlink resolution                                   ││
│  └─────────────────────────────────────────────────────────┘│
│           │                    │                   │         │
│           ▼                    ▼                   ▼         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    docs/ Directory                       ││
│  │  ├── architecture/                                       ││
│  │  ├── api/                                               ││
│  │  └── .backups/  ← 自动备份目录                           ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
autoBMAD/docuswarm/tools/
├── __init__.py
├── create_deliverable.py     # 现有工具
├── update_context.py         # 现有工具
├── read_docs_file.py         # 新增
├── update_docs_file.py       # 新增
└── list_docs_files.py        # 新增
```

### 2.3 Kimi SDK 工具规范

根据 `kimi-agent-sdk` 的 `CallableTool2` 规范:

```python
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field

class ToolParams(BaseModel):
    """参数模型，使用 Pydantic 定义"""
    param1: str = Field(description="参数描述")

class MyTool(CallableTool2[ToolParams]):
    name: str = "tool_name"
    description: str = "工具描述"
    params: type[ToolParams] = ToolParams
    
    async def __call__(self, params: ToolParams) -> ToolReturnValue:
        # 返回 ToolOk(output="...") 或 ToolError(output="", message="...", brief="...")
        pass
```

---

## 3. 工具实现

### 3.1 ReadDocsFileTool

**文件**: `autoBMAD/docuswarm/tools/read_docs_file.py`

```python
"""ReadDocsFileTool - 读取 @docs 目录文件的工具.

This module provides a tool for reading files from the @docs directory
with security checks to prevent path traversal attacks.
"""

from __future__ import annotations

from pathlib import Path
from typing import override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class ReadDocsFileParams(BaseModel):
    """Parameters for reading docs file.
    
    Attributes:
        file_path: Relative path from docs root (e.g., 'architecture/system-design.md')
    """
    
    file_path: str = Field(
        description="Relative path from docs root, e.g., 'architecture/system-design.md'"
    )


class ReadDocsFileTool(CallableTool2[ReadDocsFileParams]):
    """Tool for reading files from @docs directory.
    
    This tool provides read-only access to project documentation.
    It only allows reading files within the docs/ directory for safety.
    
    Security features:
    - Path traversal prevention (resolve + startswith check)
    - Symlink resolution
    - File existence and type validation
    """
    
    name: str = "read_docs_file"
    description: str = "Read content from a file in the @docs directory"
    params: type[ReadDocsFileParams] = ReadDocsFileParams
    
    def __init__(self) -> None:
        """Initialize with computed project root."""
        super().__init__()
        # Compute docs root: tools/ → docuswarm/ → autoBMAD/ → DocuSwarm/ → docs/
        self.docs_root = self._compute_docs_root()
    
    def _compute_docs_root(self) -> Path:
        """Compute docs root directory.
        
        Returns:
            Path to docs/ directory.
        """
        current_file = Path(__file__)
        # Navigate: tools/ → docuswarm/ → autoBMAD/ → DocuSwarm/
        project_root = current_file.parent.parent.parent.parent
        return project_root / "docs"
    
    @override
    async def __call__(self, params: ReadDocsFileParams) -> ToolReturnValue:
        """Read file from docs directory.
        
        Args:
            params: Validated parameters with file_path.
        
        Returns:
            ToolOk with file content or ToolError if failed.
        """
        try:
            # Construct full path
            file_path = self.docs_root / params.file_path
            
            # Security check 1: Resolve symlinks and check it's under docs/
            resolved_path = file_path.resolve()
            docs_root_resolved = self.docs_root.resolve()
            
            if not str(resolved_path).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.file_path} is outside docs/ directory",
                    brief="Access denied - path traversal attempt"
                )
            
            # Security check 2: File must exist
            if not resolved_path.exists():
                return ToolError(
                    output="",
                    message=f"File not found: {params.file_path}",
                    brief="File not found"
                )
            
            # Security check 3: Must be a file (not directory)
            if not resolved_path.is_file():
                return ToolError(
                    output="",
                    message=f"Not a file: {params.file_path}",
                    brief="Not a file"
                )
            
            # Read file content
            async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
                content = await f.read()
            
            return ToolOk(output=f"Content of {params.file_path}:\n\n{content}")
            
        except PermissionError:
            return ToolError(
                output="",
                message=f"Permission denied: {params.file_path}",
                brief="Permission denied"
            )
        except UnicodeDecodeError:
            return ToolError(
                output="",
                message=f"Cannot decode file (not UTF-8): {params.file_path}",
                brief="Encoding error"
            )
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to read file"
            )
```

### 3.2 UpdateDocsFileTool

**文件**: `autoBMAD/docuswarm/tools/update_docs_file.py`

```python
"""UpdateDocsFileTool - 更新 @docs 目录文件的工具.

This module provides a tool for updating files in the @docs directory
with security checks, content verification, and automatic backup.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import override

import aiofiles
from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class UpdateDocsFileParams(BaseModel):
    """Parameters for updating docs file.
    
    Attributes:
        file_path: Relative path from docs root.
        old_content: Original content snippet for verification (first 500 chars).
        new_content: Complete new content to write.
        create_backup: Whether to create backup before updating.
    """
    
    file_path: str = Field(
        description="Relative path from docs root, e.g., 'architecture/system-design.md'"
    )
    old_content: str = Field(
        description="Original content snippet (for verification, should match file's first 500 chars)"
    )
    new_content: str = Field(
        description="Complete new content to write to the file"
    )
    create_backup: bool = Field(
        default=True,
        description="Whether to create a backup before updating"
    )


class UpdateDocsFileTool(CallableTool2[UpdateDocsFileParams]):
    """Tool for updating files in @docs directory.
    
    This tool provides controlled write access to project documentation.
    
    Safety features:
    - Path traversal prevention
    - Content verification before update
    - Automatic backup creation
    - Atomic write operation (temp file + rename)
    """
    
    name: str = "update_docs_file"
    description: str = "Update content of a file in the @docs directory"
    params: type[UpdateDocsFileParams] = UpdateDocsFileParams
    
    def __init__(self) -> None:
        """Initialize with computed project root."""
        super().__init__()
        # Compute docs root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        self.docs_root = project_root / "docs"
        self.backup_dir = self.docs_root / ".backups"
    
    @override
    async def __call__(self, params: UpdateDocsFileParams) -> ToolReturnValue:
        """Update file in docs directory.
        
        Args:
            params: Validated parameters.
        
        Returns:
            ToolOk if successful, ToolError if failed.
        """
        try:
            # Construct full path
            file_path = self.docs_root / params.file_path
            
            # Security check: Path traversal prevention
            resolved_path = file_path.resolve()
            docs_root_resolved = self.docs_root.resolve()
            
            if not str(resolved_path).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.file_path} is outside docs/",
                    brief="Access denied"
                )
            
            # Check file exists
            if not resolved_path.exists():
                return ToolError(
                    output="",
                    message=f"File not found: {params.file_path}",
                    brief="File not found"
                )
            
            if not resolved_path.is_file():
                return ToolError(
                    output="",
                    message=f"Not a file: {params.file_path}",
                    brief="Not a file"
                )
            
            # Read current content for verification
            async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
                current_content = await f.read()
            
            # Verify old_content matches (first 500 chars)
            current_preview = current_content[:500]
            if params.old_content not in current_preview:
                return ToolError(
                    output="",
                    message=(
                        "Content verification failed. "
                        "The file may have been modified by another process. "
                        "Please read the file again and retry."
                    ),
                    brief="Content verification failed"
                )
            
            # Create backup if requested
            backup_name = ""
            if params.create_backup:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
                backup_name = f"{Path(params.file_path).stem}_{timestamp}.bak"
                backup_path = self.backup_dir / backup_name
                
                async with aiofiles.open(backup_path, "w", encoding="utf-8") as f:
                    await f.write(current_content)
            
            # Atomic write: write to temp file, then rename
            temp_path = resolved_path.with_suffix(resolved_path.suffix + ".tmp")
            
            try:
                async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                    await f.write(params.new_content)
                
                # Atomic rename
                temp_path.replace(resolved_path)
                
                backup_info = f" (backup: {backup_name})" if backup_name else ""
                return ToolOk(
                    output=f"Successfully updated {params.file_path}{backup_info}"
                )
            finally:
                # Cleanup temp file if it still exists (on error)
                if temp_path.exists():
                    temp_path.unlink()
        
        except PermissionError:
            return ToolError(
                output="",
                message=f"Permission denied: {params.file_path}",
                brief="Permission denied"
            )
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to update file"
            )
```

### 3.3 ListDocsFilesTool

**文件**: `autoBMAD/docuswarm/tools/list_docs_files.py`

```python
"""ListDocsFilesTool - 列出 @docs 目录文件的工具.

This module provides a tool for listing files in the @docs directory
with glob pattern support.
"""

from __future__ import annotations

from pathlib import Path
from typing import override

from kimi_agent_sdk import CallableTool2, ToolError, ToolOk, ToolReturnValue
from pydantic import BaseModel, Field


class ListDocsFilesParams(BaseModel):
    """Parameters for listing docs files.
    
    Attributes:
        directory: Relative directory path from docs root.
        pattern: Glob pattern for filtering files.
        recursive: Whether to search recursively.
    """
    
    directory: str = Field(
        default=".",
        description="Relative directory path from docs root, e.g., 'architecture'"
    )
    pattern: str = Field(
        default="*.md",
        description="Glob pattern for filtering files, e.g., '*.md' or '*.yaml'"
    )
    recursive: bool = Field(
        default=True,
        description="Whether to search recursively in subdirectories"
    )


class ListDocsFilesTool(CallableTool2[ListDocsFilesParams]):
    """Tool for listing files in @docs directory.
    
    This tool helps agents discover available documentation files.
    
    Features:
    - Glob pattern support
    - Recursive/non-recursive search
    - Path traversal prevention
    """
    
    name: str = "list_docs_files"
    description: str = "List files in the @docs directory with glob pattern support"
    params: type[ListDocsFilesParams] = ListDocsFilesParams
    
    def __init__(self) -> None:
        """Initialize with computed project root."""
        super().__init__()
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        self.docs_root = project_root / "docs"
    
    @override
    async def __call__(self, params: ListDocsFilesParams) -> ToolReturnValue:
        """List files in docs directory.
        
        Args:
            params: Validated parameters.
        
        Returns:
            ToolOk with file list or ToolError if failed.
        """
        try:
            # Construct target directory
            target_dir = self.docs_root / params.directory
            
            # Security check: Path traversal prevention
            resolved_dir = target_dir.resolve()
            docs_root_resolved = self.docs_root.resolve()
            
            if not str(resolved_dir).startswith(str(docs_root_resolved)):
                return ToolError(
                    output="",
                    message=f"Access denied: {params.directory} is outside docs/",
                    brief="Access denied"
                )
            
            if not resolved_dir.exists():
                return ToolError(
                    output="",
                    message=f"Directory not found: {params.directory}",
                    brief="Directory not found"
                )
            
            if not resolved_dir.is_dir():
                return ToolError(
                    output="",
                    message=f"Not a directory: {params.directory}",
                    brief="Not a directory"
                )
            
            # Build glob pattern
            if params.recursive:
                glob_pattern = f"**/{params.pattern}"
            else:
                glob_pattern = params.pattern
            
            # Collect files
            files = sorted(resolved_dir.glob(glob_pattern))
            
            # Convert to relative paths from docs root
            relative_files = [
                str(f.relative_to(self.docs_root))
                for f in files
                if f.is_file()
            ]
            
            if not relative_files:
                return ToolOk(
                    output=f"No files found matching pattern '{params.pattern}' in {params.directory}"
                )
            
            file_list = "\n".join(f"- {f}" for f in relative_files)
            return ToolOk(
                output=f"Found {len(relative_files)} file(s) in {params.directory}:\n\n{file_list}"
            )
        
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to list files"
            )
```

### 3.4 工具注册

**文件**: `autoBMAD/docuswarm/tools/__init__.py`

```python
"""DocuSwarm tools package.

This package provides tools for document creation and manipulation.
"""

from autoBMAD.docuswarm.tools.create_deliverable import CreateDeliverableTool
from autoBMAD.docuswarm.tools.list_docs_files import ListDocsFilesTool
from autoBMAD.docuswarm.tools.read_docs_file import ReadDocsFileTool
from autoBMAD.docuswarm.tools.update_docs_file import UpdateDocsFileTool

__all__ = [
    "CreateDeliverableTool",
    "ListDocsFilesTool",
    "ReadDocsFileTool",
    "UpdateDocsFileTool",
]
```

---

## 4. TDD 测试用例

### 4.1 测试文件

**文件**: `tests/unit/test_docs_tools.py`

### 4.2 测试代码

```python
"""Unit tests for @docs directory tools.

This module tests:
1. ReadDocsFileTool - file reading with security checks
2. UpdateDocsFileTool - file updating with backup and verification
3. ListDocsFilesTool - file listing with glob patterns
4. Security: path traversal prevention
"""

import pytest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from autoBMAD.docuswarm.tools.read_docs_file import (
    ReadDocsFileTool,
    ReadDocsFileParams,
)
from autoBMAD.docuswarm.tools.update_docs_file import (
    UpdateDocsFileTool,
    UpdateDocsFileParams,
)
from autoBMAD.docuswarm.tools.list_docs_files import (
    ListDocsFilesTool,
    ListDocsFilesParams,
)


@pytest.fixture
def docs_structure(tmp_path: Path) -> Path:
    """Create a docs directory structure for testing."""
    docs = tmp_path / "docs"
    
    # Create directories
    (docs / "architecture").mkdir(parents=True)
    (docs / "api").mkdir()
    (docs / ".backups").mkdir()
    
    # Create files
    (docs / "README.md").write_text("# Documentation\n\nWelcome to docs.")
    (docs / "architecture" / "system-design.md").write_text(
        "# System Design\n\n## Overview\n\nSystem overview here."
    )
    (docs / "architecture" / "api-design.md").write_text(
        "# API Design\n\nAPI specifications."
    )
    (docs / "api" / "endpoints.yaml").write_text(
        "openapi: 3.0.0\npaths: {}"
    )
    
    return tmp_path


class TestReadDocsFileTool:
    """Tests for ReadDocsFileTool."""

    @pytest.mark.asyncio
    async def test_read_existing_file(self, docs_structure: Path) -> None:
        """Test reading an existing file successfully."""
        tool = ReadDocsFileTool()
        # Override docs_root for testing
        tool.docs_root = docs_structure / "docs"
        
        params = ReadDocsFileParams(file_path="README.md")
        result = await tool(params)
        
        assert hasattr(result, "output")
        assert "# Documentation" in result.output
        assert "Welcome to docs" in result.output

    @pytest.mark.asyncio
    async def test_read_nested_file(self, docs_structure: Path) -> None:
        """Test reading a file in subdirectory."""
        tool = ReadDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ReadDocsFileParams(file_path="architecture/system-design.md")
        result = await tool(params)
        
        assert "# System Design" in result.output
        assert "## Overview" in result.output

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, docs_structure: Path) -> None:
        """Test reading a file that doesn't exist."""
        tool = ReadDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ReadDocsFileParams(file_path="nonexistent.md")
        result = await tool(params)
        
        assert hasattr(result, "message")
        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_reject_path_traversal(self, docs_structure: Path) -> None:
        """Test that path traversal is rejected."""
        # Create a secret file outside docs/
        secret_file = docs_structure / "secret.txt"
        secret_file.write_text("SECRET DATA")
        
        tool = ReadDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        
        # Try to access parent directory
        params = ReadDocsFileParams(file_path="../secret.txt")
        result = await tool(params)
        
        assert hasattr(result, "message")
        assert "access denied" in result.message.lower()

    @pytest.mark.asyncio
    async def test_reject_absolute_path(self, docs_structure: Path) -> None:
        """Test that absolute paths are handled safely."""
        tool = ReadDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        
        # Try with absolute path component
        params = ReadDocsFileParams(file_path="../../etc/passwd")
        result = await tool(params)
        
        assert hasattr(result, "message")
        # Should either be "access denied" or "not found"
        assert "denied" in result.message.lower() or "not found" in result.message.lower()


class TestUpdateDocsFileTool:
    """Tests for UpdateDocsFileTool."""

    @pytest.mark.asyncio
    async def test_update_file_with_backup(self, docs_structure: Path) -> None:
        """Test updating a file with backup creation."""
        tool = UpdateDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        tool.backup_dir = docs_structure / "docs" / ".backups"
        
        original_content = (docs_structure / "docs" / "README.md").read_text()
        
        params = UpdateDocsFileParams(
            file_path="README.md",
            old_content="# Documentation",  # First part of file
            new_content="# Updated Documentation\n\nNew content here.",
            create_backup=True
        )
        result = await tool(params)
        
        # Check success
        assert hasattr(result, "output")
        assert "Successfully updated" in result.output
        
        # Check file was updated
        new_content = (docs_structure / "docs" / "README.md").read_text()
        assert new_content == "# Updated Documentation\n\nNew content here."
        
        # Check backup was created
        backup_files = list(tool.backup_dir.glob("README_*.bak"))
        assert len(backup_files) == 1
        assert backup_files[0].read_text() == original_content

    @pytest.mark.asyncio
    async def test_update_without_backup(self, docs_structure: Path) -> None:
        """Test updating a file without backup."""
        tool = UpdateDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        tool.backup_dir = docs_structure / "docs" / ".backups"
        
        params = UpdateDocsFileParams(
            file_path="README.md",
            old_content="# Documentation",
            new_content="# No Backup Update",
            create_backup=False
        )
        result = await tool(params)
        
        assert "Successfully updated" in result.output
        
        # No backup should be created
        backup_files = list(tool.backup_dir.glob("README_*.bak"))
        assert len(backup_files) == 0

    @pytest.mark.asyncio
    async def test_content_verification_failure(self, docs_structure: Path) -> None:
        """Test that wrong old_content is rejected."""
        tool = UpdateDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        tool.backup_dir = docs_structure / "docs" / ".backups"
        
        params = UpdateDocsFileParams(
            file_path="README.md",
            old_content="WRONG CONTENT",  # Doesn't match
            new_content="# New Content"
        )
        result = await tool(params)
        
        assert hasattr(result, "message")
        assert "verification failed" in result.message.lower()
        
        # File should be unchanged
        content = (docs_structure / "docs" / "README.md").read_text()
        assert "# Documentation" in content

    @pytest.mark.asyncio
    async def test_reject_path_traversal_on_update(
        self, docs_structure: Path
    ) -> None:
        """Test that path traversal is rejected for updates."""
        tool = UpdateDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        tool.backup_dir = docs_structure / "docs" / ".backups"
        
        params = UpdateDocsFileParams(
            file_path="../outside.txt",
            old_content="whatever",
            new_content="malicious content"
        )
        result = await tool(params)
        
        assert hasattr(result, "message")
        assert "denied" in result.message.lower()


class TestListDocsFilesTool:
    """Tests for ListDocsFilesTool."""

    @pytest.mark.asyncio
    async def test_list_all_markdown_files(self, docs_structure: Path) -> None:
        """Test listing all markdown files recursively."""
        tool = ListDocsFilesTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ListDocsFilesParams(
            directory=".",
            pattern="*.md",
            recursive=True
        )
        result = await tool(params)
        
        assert hasattr(result, "output")
        assert "README.md" in result.output
        assert "architecture/system-design.md" in result.output
        assert "architecture/api-design.md" in result.output
        # Should not include yaml files
        assert "endpoints.yaml" not in result.output

    @pytest.mark.asyncio
    async def test_list_files_in_subdirectory(self, docs_structure: Path) -> None:
        """Test listing files in a specific subdirectory."""
        tool = ListDocsFilesTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ListDocsFilesParams(
            directory="architecture",
            pattern="*.md",
            recursive=False
        )
        result = await tool(params)
        
        assert "system-design.md" in result.output
        assert "api-design.md" in result.output
        # README.md is not in architecture/
        assert "README.md" not in result.output

    @pytest.mark.asyncio
    async def test_list_yaml_files(self, docs_structure: Path) -> None:
        """Test listing yaml files."""
        tool = ListDocsFilesTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ListDocsFilesParams(
            directory=".",
            pattern="*.yaml",
            recursive=True
        )
        result = await tool(params)
        
        assert "endpoints.yaml" in result.output
        assert ".md" not in result.output

    @pytest.mark.asyncio
    async def test_list_empty_result(self, docs_structure: Path) -> None:
        """Test listing with no matches."""
        tool = ListDocsFilesTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ListDocsFilesParams(
            directory=".",
            pattern="*.nonexistent",
            recursive=True
        )
        result = await tool(params)
        
        assert "No files found" in result.output

    @pytest.mark.asyncio
    async def test_reject_path_traversal_on_list(
        self, docs_structure: Path
    ) -> None:
        """Test that path traversal is rejected for listing."""
        tool = ListDocsFilesTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ListDocsFilesParams(
            directory="../",
            pattern="*"
        )
        result = await tool(params)
        
        assert hasattr(result, "message")
        assert "denied" in result.message.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_directory(self, docs_structure: Path) -> None:
        """Test listing a directory that doesn't exist."""
        tool = ListDocsFilesTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ListDocsFilesParams(
            directory="nonexistent",
            pattern="*.md"
        )
        result = await tool(params)
        
        assert hasattr(result, "message")
        assert "not found" in result.message.lower()


class TestSecurityEdgeCases:
    """Test security edge cases across all tools."""

    @pytest.mark.asyncio
    async def test_symlink_resolution(self, docs_structure: Path) -> None:
        """Test that symlinks are properly resolved and validated."""
        # Create a symlink that points outside docs/
        secret_file = docs_structure / "secret.txt"
        secret_file.write_text("SECRET")
        
        symlink_path = docs_structure / "docs" / "sneaky_link.md"
        try:
            symlink_path.symlink_to(secret_file)
        except OSError:
            pytest.skip("Cannot create symlinks on this system")
        
        tool = ReadDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ReadDocsFileParams(file_path="sneaky_link.md")
        result = await tool(params)
        
        # Should be rejected because resolved path is outside docs/
        assert hasattr(result, "message")
        assert "denied" in result.message.lower() or "outside" in result.message.lower()

    @pytest.mark.asyncio
    async def test_double_dot_in_filename(self, docs_structure: Path) -> None:
        """Test that double dots in filename are handled correctly."""
        # Create a file with dots in name (legitimate)
        (docs_structure / "docs" / "file..name.md").write_text("Content")
        
        tool = ReadDocsFileTool()
        tool.docs_root = docs_structure / "docs"
        
        params = ReadDocsFileParams(file_path="file..name.md")
        result = await tool(params)
        
        # Should succeed - dots in filename are OK
        assert hasattr(result, "output")
        assert "Content" in result.output
```

### 4.3 测试运行命令

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行工具测试
pytest tests/unit/test_docs_tools.py -v --tb=short

# 运行带覆盖率
pytest tests/unit/test_docs_tools.py -v --cov=autoBMAD.docuswarm.tools
```

---

## 5. 实施步骤

### 5.1 Step 1: 创建测试文件

```bash
# 创建测试文件
mkdir -p tests/unit
# 复制测试代码到 tests/unit/test_docs_tools.py
```

### 5.2 Step 2: 运行测试 (确认当前失败)

```bash
pytest tests/unit/test_docs_tools.py -v
# 预期: ImportError (工具不存在)
```

### 5.3 Step 3: 创建工具文件

创建以下文件:
- `autoBMAD/docuswarm/tools/read_docs_file.py`
- `autoBMAD/docuswarm/tools/update_docs_file.py`
- `autoBMAD/docuswarm/tools/list_docs_files.py`

更新:
- `autoBMAD/docuswarm/tools/__init__.py`

### 5.4 Step 4: 重新运行测试 (确认通过)

```bash
pytest tests/unit/test_docs_tools.py -v
# 预期: 所有测试通过
```

### 5.5 Step 5: 类型检查

```bash
basedpyright autoBMAD/docuswarm/tools/
```

### 5.6 Step 6: 更新工具配置 (可选)

如果需要在 Agent YAML 中注册工具:

```yaml
# autoBMAD/docuswarm/agents/configs/independent_agent.yaml
version: 1
agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.update_context:UpdateContextTool"
    - "docuswarm.tools.read_docs_file:ReadDocsFileTool"
    - "docuswarm.tools.update_docs_file:UpdateDocsFileTool"
    - "docuswarm.tools.list_docs_files:ListDocsFilesTool"
```

---

## 6. 安全考虑

### 6.1 路径访问控制

```python
# 所有工具都使用此模式
resolved_path = file_path.resolve()
docs_root_resolved = self.docs_root.resolve()

if not str(resolved_path).startswith(str(docs_root_resolved)):
    return ToolError(message="Access denied")
```

### 6.2 自动备份

```python
# UpdateDocsFileTool 默认创建备份
backup_path = docs/.backups/{filename}_{timestamp}.bak
```

### 6.3 内容验证

```python
# 更新前验证原内容匹配
if params.old_content not in current_preview:
    return ToolError(message="Content verification failed")
```

### 6.4 原子写入

```python
# 使用临时文件 + 原子重命名
temp_path.write(new_content)
temp_path.replace(target_path)  # atomic on most filesystems
```

### 6.5 配置控制 (可选)

```python
# autoBMAD/docuswarm/config.py
@dataclass(frozen=True)
class Config:
    # @docs 修改权限控制
    enable_docs_modification: bool = field(default=False)
    docs_backup_enabled: bool = field(default=True)
```

---

## 7. 验证清单

### 7.1 功能验证

- [ ] `read_docs_file` 可以读取 docs/ 下的文件
- [ ] `update_docs_file` 可以更新 docs/ 下的文件
- [ ] `update_docs_file` 自动创建备份到 `.backups/`
- [ ] `list_docs_files` 可以列出 docs/ 下的文件
- [ ] 所有工具支持子目录操作

### 7.2 安全验证

- [ ] 路径穿越攻击被拒绝 (`../` 等)
- [ ] 符号链接正确解析和验证
- [ ] 内容验证失败时更新被拒绝
- [ ] 只能访问 docs/ 目录

### 7.3 测试验证

- [ ] `pytest tests/unit/test_docs_tools.py -v` 全部通过
- [ ] `basedpyright autoBMAD/docuswarm/tools/` 无错误
- [ ] `ruff check autoBMAD/docuswarm/tools/` 无错误

### 7.4 集成验证

- [ ] 工具可以在 IndependentAgent 中使用
- [ ] 工具与 Kimi SDK CallableTool2 规范兼容

---

## 附录

### A. 使用示例

**Agent Prompt 示例**:

```markdown
# Task

请更新架构文档 @docs/architecture/system-design.md:

1. 先使用 list_docs_files 列出 architecture 目录的文件
2. 使用 read_docs_file 读取 architecture/system-design.md
3. 在 "## 数据库设计" 章节后添加新的缓存层设计
4. 使用 update_docs_file 保存更新 (确保传入正确的 old_content)

同时创建一个新的交付物 architecture-update-summary.md 总结本次更新。
```

### B. 参考链接

- [概览文档](./Output目录统一与Context_File传递-概览.md)
- [前一阶段: P1-Context_File传递-TDD方案.md](./P1-Context_File传递-TDD方案.md)
- [下一阶段: P2-多文档创建能力-TDD方案.md](./P2-多文档创建能力-TDD方案.md)
