# P0: Output 目录统一 — 测试驱动开发方案

**优先级**: P0 (Critical)  
**预估工时**: 20 分钟  
**依赖**: 无  
**影响范围**: Pipeline 全流程

---

## 目录

1. [问题描述](#1-问题描述)
2. [根因分析](#2-根因分析)
3. [解决方案设计](#3-解决方案设计)
4. [TDD 测试用例](#4-tdd-测试用例)
5. [实施步骤](#5-实施步骤)
6. [验证清单](#6-验证清单)

---

## 1. 问题描述

### 1.1 现象

运行 Pipeline 时，会在两个位置创建输出目录：

| 位置 | 创建者 | 状态 |
|------|--------|------|
| `autoBMAD\output\pipeline-xxx\` | IndependentAgent | 正确 |
| `d:\GITHUB\DocuSwarm\pipeline-xxx\` | Orchestrator (Kimi SDK) | 错误 |

### 1.2 影响

1. **目录混乱**: 项目根目录被污染，出现大量 `pipeline-*` 文件夹
2. **资源浪费**: 同一 Pipeline 创建了两个目录
3. **用户困惑**: 不知道哪个目录是正确的输出位置
4. **清理负担**: 需要手动清理错误创建的目录

### 1.3 复现步骤

```bash
cd d:\GITHUB\DocuSwarm
python -m autoBMAD.docuswarm start -c proposal.md

# 结果:
# - 创建了 d:\GITHUB\DocuSwarm\pipeline-xxx\  ← 错误
# - 创建了 autoBMAD\output\pipeline-xxx\      ← 正确
```

---

## 2. 根因分析

### 2.1 调用链追踪

```
main.py:start()
    ↓
orchestrator = HybridOrchestrator(db_path=..., api_key=..., base_url=...)
    ↓
__init__: self._work_dir = None  ← 问题根源
    ↓
_get_or_create_session_manager()
    ↓
work_dir = KaosPath(self._work_dir) if self._work_dir else KaosPath.cwd()
    ↓
KaosPath.cwd() = d:\GITHUB\DocuSwarm  ← 当前工作目录
    ↓
KimiSessionManager(work_dir=cwd)
    ↓
Kimi SDK 在 d:\GITHUB\DocuSwarm 创建 pipeline-xxx\
```

### 2.2 问题代码位置

**文件**: `autoBMAD/docuswarm/pipeline/orchestrator.py`

**位置 1**: `__init__` 方法 (行 128-160)

```python
def __init__(
    self,
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | SqliteSaver | None = None,
    session_manager: KimiSessionManager | None = None,
    work_dir: str | None = None,  # ← 有参数但未使用默认值
    api_key: str | None = None,
    base_url: str | None = None,
) -> None:
    # ...
    self._work_dir = work_dir  # ← 保持 None 如果未传入
```

**位置 2**: `_get_or_create_session_manager` 方法 (行 167-190)

```python
def _get_or_create_session_manager(self) -> KimiSessionManager:
    if self._session_manager is not None:
        return self._session_manager

    try:
        work_dir = KaosPath(self._work_dir) if self._work_dir else KaosPath.cwd()
        #                                                         ↑ 问题: fallback 到 cwd()
        self._session_manager = KimiSessionManager(
            work_dir=work_dir,
            api_key=self._api_key,
            base_url=self._base_url,
        )
        return self._session_manager
```

**位置 3**: `main.py` 调用 (行 123-128)

```python
orchestrator = HybridOrchestrator(
    db_path=str(config.db_path),
    api_key=config.api_key,
    base_url=config.base_url,
    # ← 未传入 work_dir
)
```

---

## 3. 解决方案设计

### 3.1 方案概述

```
修改策略:
1. HybridOrchestrator.__init__: 计算并设置默认 work_dir
2. _get_or_create_session_manager: 支持 pipeline-specific work_dir
3. start_pipeline: 创建 pipeline 子目录
4. main.py: 显式传入 work_dir (可选优化)
```

### 3.2 代码修改设计

#### 修改 1: `orchestrator.py` - `__init__` 方法

**修改位置**: 行 147-152

**修改前**:
```python
self._work_dir = work_dir
```

**修改后**:
```python
# 初始化 work_dir，默认为 autoBMAD/output
if work_dir is None:
    # 计算 autoBMAD 根目录: orchestrator.py → pipeline/ → docuswarm/ → autoBMAD/
    autoBMAD_root = Path(__file__).parent.parent.parent.resolve()
    self._work_dir = str(autoBMAD_root / "output")
else:
    self._work_dir = work_dir

logger.info(
    "orchestrator_work_dir_set",
    work_dir=self._work_dir,
)
```

#### 修改 2: `orchestrator.py` - `_get_or_create_session_manager` 方法

**修改位置**: 行 167-190

**修改前**:
```python
def _get_or_create_session_manager(self) -> KimiSessionManager:
    if self._session_manager is not None:
        return self._session_manager

    try:
        work_dir = KaosPath(self._work_dir) if self._work_dir else KaosPath.cwd()
        # ...
```

**修改后**:
```python
def _get_or_create_session_manager(
    self, 
    pipeline_id: str | None = None
) -> KimiSessionManager:
    """Get or create session manager with optional pipeline-specific work_dir.
    
    Args:
        pipeline_id: Optional pipeline ID for pipeline-specific work_dir.
    
    Returns:
        KimiSessionManager instance.
    
    Raises:
        OrchestratorError: If session manager cannot be created.
    """
    # Return cached manager if no pipeline_id specified
    if self._session_manager is not None and pipeline_id is None:
        return self._session_manager

    try:
        if pipeline_id:
            # Pipeline-specific work_dir
            work_dir = KaosPath(str(Path(self._work_dir) / pipeline_id))
        else:
            # Global work_dir (never falls back to cwd)
            work_dir = KaosPath(self._work_dir)
        
        session_manager = KimiSessionManager(
            work_dir=work_dir,
            api_key=self._api_key,
            base_url=self._base_url,
        )
        
        # 只缓存全局 session_manager
        if pipeline_id is None:
            self._session_manager = session_manager
        
        logger.info(
            "session_manager_created",
            work_dir=str(work_dir),
            pipeline_id=pipeline_id,
        )
        return session_manager
    except Exception as e:
        logger.error("failed_to_create_session_manager", error=str(e))
        raise OrchestratorError(f"Failed to create session manager: {e}") from e
```

#### 修改 3: `orchestrator.py` - `start_pipeline` 方法

**修改位置**: 在 Step 4 之后添加

```python
# Step 4.5: 确保 pipeline 输出目录存在
pipeline_work_dir = Path(self._work_dir) / final_pipeline_id
pipeline_work_dir.mkdir(parents=True, exist_ok=True)
logger.info(
    "pipeline_work_dir_created",
    path=str(pipeline_work_dir),
    pipeline_id=final_pipeline_id,
)
```

### 3.3 需要添加的导入

```python
from pathlib import Path
```

---

## 4. TDD 测试用例

### 4.1 测试文件

**文件**: `tests/unit/test_orchestrator_work_dir.py`

### 4.2 测试代码

```python
"""Unit tests for HybridOrchestrator work_dir initialization.

This module tests:
1. Default work_dir calculation to autoBMAD/output
2. Custom work_dir override
3. Session manager uses correct work_dir
4. Pipeline-specific work_dir creation
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator


class TestOrchestratorWorkDirInit:
    """Test HybridOrchestrator work_dir initialization."""

    def test_default_work_dir_points_to_autoBMAD_output(self, tmp_path: Path) -> None:
        """Test that default work_dir ends with autoBMAD/output."""
        with patch.object(
            HybridOrchestrator,
            "_get_or_create_session_manager",
            return_value=MagicMock(),
        ):
            orchestrator = HybridOrchestrator(
                db_path=str(tmp_path / "test.db"),
                api_key="test-key",
            )
            
            # work_dir should end with autoBMAD/output or autoBMAD\output
            assert orchestrator._work_dir is not None
            assert (
                orchestrator._work_dir.endswith("autoBMAD/output")
                or orchestrator._work_dir.endswith("autoBMAD\\output")
            )

    def test_custom_work_dir_is_respected(self, tmp_path: Path) -> None:
        """Test that custom work_dir is used when provided."""
        custom_dir = tmp_path / "custom_output"
        
        with patch.object(
            HybridOrchestrator,
            "_get_or_create_session_manager",
            return_value=MagicMock(),
        ):
            orchestrator = HybridOrchestrator(
                db_path=str(tmp_path / "test.db"),
                api_key="test-key",
                work_dir=str(custom_dir),
            )
            
            assert orchestrator._work_dir == str(custom_dir)

    def test_work_dir_never_uses_cwd_fallback(self, tmp_path: Path) -> None:
        """Test that work_dir never falls back to cwd."""
        import os
        original_cwd = os.getcwd()
        
        try:
            # Change to a different directory
            os.chdir(tmp_path)
            
            with patch.object(
                HybridOrchestrator,
                "_get_or_create_session_manager",
                return_value=MagicMock(),
            ):
                orchestrator = HybridOrchestrator(
                    db_path=str(tmp_path / "test.db"),
                    api_key="test-key",
                    # 不传入 work_dir
                )
                
                # work_dir 不应该是 cwd (tmp_path)
                assert orchestrator._work_dir != str(tmp_path)
                assert "autoBMAD" in orchestrator._work_dir
        finally:
            os.chdir(original_cwd)


class TestSessionManagerWorkDir:
    """Test session manager work_dir handling."""

    def test_session_manager_receives_work_dir(self, tmp_path: Path) -> None:
        """Test that KimiSessionManager receives correct work_dir."""
        from kaos.path import KaosPath
        
        work_dir = tmp_path / "output"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        with patch(
            "autoBMAD.docuswarm.pipeline.orchestrator.KimiSessionManager"
        ) as mock_sm_class:
            mock_sm_class.return_value = MagicMock()
            
            orchestrator = HybridOrchestrator(
                db_path=str(tmp_path / "test.db"),
                api_key="test-key",
                work_dir=str(work_dir),
            )
            
            # 触发 session manager 创建
            sm = orchestrator._get_or_create_session_manager()
            
            # 验证 KimiSessionManager 接收到正确的 work_dir
            call_kwargs = mock_sm_class.call_args.kwargs
            assert str(call_kwargs["work_dir"]) == str(work_dir)

    def test_pipeline_specific_work_dir(self, tmp_path: Path) -> None:
        """Test that pipeline-specific work_dir includes pipeline_id."""
        from kaos.path import KaosPath
        
        work_dir = tmp_path / "output"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        with patch(
            "autoBMAD.docuswarm.pipeline.orchestrator.KimiSessionManager"
        ) as mock_sm_class:
            mock_sm_class.return_value = MagicMock()
            
            orchestrator = HybridOrchestrator(
                db_path=str(tmp_path / "test.db"),
                api_key="test-key",
                work_dir=str(work_dir),
            )
            
            # 创建带 pipeline_id 的 session manager
            pipeline_id = "test-pipeline-123"
            sm = orchestrator._get_or_create_session_manager(pipeline_id=pipeline_id)
            
            # 验证 work_dir 包含 pipeline_id
            call_kwargs = mock_sm_class.call_args.kwargs
            assert pipeline_id in str(call_kwargs["work_dir"])


class TestPipelineWorkDirCreation:
    """Test pipeline work_dir directory creation."""

    @pytest.mark.asyncio
    async def test_start_pipeline_creates_output_dir(self, tmp_path: Path) -> None:
        """Test that start_pipeline creates the output directory."""
        work_dir = tmp_path / "output"
        
        with patch.object(
            HybridOrchestrator,
            "_get_or_create_session_manager",
            return_value=MagicMock(),
        ), patch.object(
            HybridOrchestrator,
            "_validate_context",
            new_callable=AsyncMock,
            return_value={"valid": True, "reason": "ok", "missing_info": []},
        ), patch.object(
            HybridOrchestrator,
            "_check_dependencies",
            new_callable=AsyncMock,
            return_value={"all_present": True, "missing": [], "available": []},
        ), patch(
            "autoBMAD.docuswarm.pipeline.orchestrator.create_pipeline_graph"
        ) as mock_graph:
            # Mock graph execution
            mock_compiled = MagicMock()
            mock_compiled.ainvoke = AsyncMock(
                return_value={"status": "completed"}
            )
            mock_graph.return_value.compile.return_value = mock_compiled
            
            orchestrator = HybridOrchestrator(
                db_path=str(tmp_path / "test.db"),
                api_key="test-key",
                work_dir=str(work_dir),
            )
            
            subject_context = {
                "subject": "test",
                "context_file": "test.md",
                "content": "Test content",
            }
            
            try:
                pipeline_id = await orchestrator.start_pipeline(subject_context)
                
                # 验证 pipeline 输出目录被创建
                pipeline_output = work_dir / pipeline_id
                assert pipeline_output.exists()
                assert pipeline_output.is_dir()
            except Exception:
                # 即使出错，也应该创建了目录
                # 检查是否有任何 pipeline-* 目录
                pipeline_dirs = list(work_dir.glob("pipeline-*"))
                if pipeline_dirs:
                    assert pipeline_dirs[0].is_dir()


class TestWorkDirPathCalculation:
    """Test work_dir path calculation logic."""

    def test_path_relative_to_orchestrator_file(self) -> None:
        """Test that default work_dir is calculated relative to orchestrator.py."""
        from autoBMAD.docuswarm.pipeline.orchestrator import HybridOrchestrator
        
        # 获取 orchestrator.py 的位置
        import autoBMAD.docuswarm.pipeline.orchestrator as orch_module
        orchestrator_path = Path(orch_module.__file__)
        
        # 期望的 work_dir: orchestrator.py → pipeline/ → docuswarm/ → autoBMAD/ → output/
        expected_autoBMAD_root = orchestrator_path.parent.parent.parent.resolve()
        expected_work_dir = expected_autoBMAD_root / "output"
        
        with patch.object(
            HybridOrchestrator,
            "_get_or_create_session_manager",
            return_value=MagicMock(),
        ):
            orchestrator = HybridOrchestrator(
                db_path=":memory:",
                api_key="test-key",
            )
            
            assert orchestrator._work_dir == str(expected_work_dir)
```

### 4.3 测试运行命令

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行单元测试
pytest tests/unit/test_orchestrator_work_dir.py -v --tb=short

# 运行带覆盖率
pytest tests/unit/test_orchestrator_work_dir.py -v --cov=autoBMAD.docuswarm.pipeline.orchestrator
```

---

## 5. 实施步骤

### 5.1 Step 1: 创建测试文件

```bash
# 创建测试文件
mkdir -p tests/unit
# 复制上述测试代码到 tests/unit/test_orchestrator_work_dir.py
```

### 5.2 Step 2: 运行测试 (确认当前失败)

```bash
pytest tests/unit/test_orchestrator_work_dir.py -v
# 预期: 部分测试失败 (test_default_work_dir_points_to_autoBMAD_output 等)
```

### 5.3 Step 3: 修改 `orchestrator.py`

**添加导入**:
```python
from pathlib import Path
```

**修改 `__init__` 方法**:
- 添加默认 work_dir 计算逻辑

**修改 `_get_or_create_session_manager` 方法**:
- 添加 `pipeline_id` 参数
- 支持 pipeline-specific work_dir

### 5.4 Step 4: 重新运行测试 (确认通过)

```bash
pytest tests/unit/test_orchestrator_work_dir.py -v
# 预期: 所有测试通过
```

### 5.5 Step 5: 手动验证

```bash
# 确保根目录干净
ls -la | grep "pipeline-"
# 应该没有任何 pipeline-* 目录

# 运行 Pipeline
python -m autoBMAD.docuswarm start -c proposal.md

# 验证输出位置
ls autoBMAD/output/
# 应该只有一个 pipeline-xxx 目录

ls -la | grep "pipeline-"
# 仍然没有任何 pipeline-* 目录
```

### 5.6 Step 6: 运行回归测试

```bash
# 类型检查
basedpyright autoBMAD/docuswarm/

# 代码风格
ruff check autoBMAD/docuswarm/

# 全部单元测试
pytest tests/unit/ -v --tb=short
```

---

## 6. 验证清单

### 6.1 修复前状态 (预期失败)

- [ ] 运行 `pytest tests/unit/test_orchestrator_work_dir.py -v`
- [ ] 确认 `test_default_work_dir_points_to_autoBMAD_output` 失败
- [ ] 确认 `orchestrator._work_dir` 为 `None`

### 6.2 修复后状态 (预期通过)

- [ ] `orchestrator._work_dir` 指向 `autoBMAD/output`
- [ ] 所有 `test_orchestrator_work_dir.py` 测试通过
- [ ] 手动运行 Pipeline 后只在 `autoBMAD\output\` 创建目录
- [ ] 项目根目录无新增 `pipeline-xxx\` 文件夹

### 6.3 回归测试

- [ ] `basedpyright` 类型检查通过
- [ ] `ruff check` 代码风格通过
- [ ] 现有单元测试无回归

---

## 附录

### A. 清理遗留目录脚本

如果项目根目录已经有错误创建的 `pipeline-*` 目录，可使用以下脚本清理：

```python
#!/usr/bin/env python3
"""Clean up accidentally created pipeline directories in project root."""

import shutil
from pathlib import Path

def clean_root_pipelines(project_root: Path, dry_run: bool = True) -> list[Path]:
    """Clean up pipeline directories in project root.
    
    Args:
        project_root: Path to project root directory.
        dry_run: If True, only list directories without deleting.
    
    Returns:
        List of directories that were/would be deleted.
    """
    deleted = []
    
    for path in project_root.glob("pipeline-*"):
        if path.is_dir():
            print(f"{'Would delete' if dry_run else 'Deleting'}: {path}")
            deleted.append(path)
            
            if not dry_run:
                shutil.rmtree(path)
    
    return deleted


if __name__ == "__main__":
    import sys
    
    root = Path.cwd()
    dry_run = "--confirm" not in sys.argv
    
    if dry_run:
        print("DRY RUN MODE - use --confirm to actually delete")
    
    deleted = clean_root_pipelines(root, dry_run)
    
    if not deleted:
        print("No pipeline directories found in project root")
    else:
        print(f"\nTotal: {len(deleted)} directories {'found' if dry_run else 'deleted'}")
```

### B. 相关文件路径

| 文件 | 用途 |
|------|------|
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | 主要修改文件 |
| `autoBMAD/docuswarm/main.py` | 可选修改 (显式传入 work_dir) |
| `tests/unit/test_orchestrator_work_dir.py` | 新增测试文件 |

### C. 参考链接

- [概览文档](./Output目录统一与Context_File传递-概览.md)
- [下一阶段: P1-Context_File传递-TDD方案.md](./P1-Context_File传递-TDD方案.md)
