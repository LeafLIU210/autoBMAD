# Pytest Agent 集成 Typeguard 详细改造方案

**文档版本**: v1.0  
**创建时间**: 2026-02-20  
**状态**: 待实施  
**关联报告**: 
- `PYTEST_TYPEGUARD_INTEGRATION_REPORT.md`
- `PYTEST_TYPEGUARD_AGENT_ANALYSIS.md`

---

## 一、改造目标

在现有的 pytest agent 中集成 typeguard 运行时类型检查功能，实现以下目标：

1. **增强类型安全**：在测试阶段捕获运行时类型错误
2. **提升 AI 修复精准度**：为 SDK 修复阶段提供详细的类型错误信息
3. **保持向后兼容**：不改变现有数据结构和返回值格式

---

## 二、涉及文件清单

| 序号 | 文件路径 | 修改类型 | 优先级 |
|------|----------|----------|--------|
| 1 | `agents/pytest_batch_executor.py` | 修改 | P0 |
| 2 | `agents/quality_agents.py` | 修改 | P0 |
| 3 | `controllers/pytest_controller.py` | 修改 | P1 |
| 4 | `pyproject.toml` (项目根目录) | 新增配置 | P2 |
| 5 | `requirements.txt` | 新增依赖 | P0 |

---

## 三、环境准备

### 3.1 安装 typeguard

```bash
pip install typeguard
```

添加到 `requirements.txt`:

```
typeguard>=4.0.0
```

### 3.2 验证 src 包可导入

```bash
python -c "import src; print('src package loaded successfully')"
```

如果失败，确保：
1. `src/__init__.py` 文件存在
2. 项目已通过 `pip install -e .` 安装

---

## 四、代码修改详情

### 4.1 PytestBatchExecutor 修改

**文件**: `agents/pytest_batch_executor.py`  
**修改位置**: `_build_command` 方法（第280-310行）

#### 4.1.1 修改前代码

```python
def _build_command(self, batch: BatchConfig) -> list[str]:
    """
    构建pytest命令

    Args:
        batch: 批次配置

    Returns:
        List[str]: 命令参数列表
    """
    cmd = ["pytest", batch.path]

    # 详细输出
    cmd.extend(["-v", "--tb=short"])

    # 并行执行
    if batch.parallel:
        if isinstance(batch.workers, int):
            cmd.extend(["-n", str(batch.workers)])
        else:
            cmd.extend(["-n", batch.workers])  # "auto"

    # 覆盖率（仅主批次）
    if batch.name in ["unit", "integration", "loose_tests"]:
        cmd.extend([f"--cov={self.source_dir}", "--cov-report=term-missing"])

    # 失败快速停止（阻断批次）
    if batch.blocking:
        cmd.append("--maxfail=5")

    return cmd
```

#### 4.1.2 修改后代码

```python
def _build_command(self, batch: BatchConfig) -> list[str]:
    """
    构建pytest命令

    Args:
        batch: 批次配置

    Returns:
        List[str]: 命令参数列表
    """
    cmd = ["pytest", batch.path]

    # 详细输出
    cmd.extend(["-v", "--tb=short"])

    # 并行执行
    if batch.parallel:
        if isinstance(batch.workers, int):
            cmd.extend(["-n", str(batch.workers)])
        else:
            cmd.extend(["-n", batch.workers])  # "auto"

    # 覆盖率和类型检查（仅主批次）
    if batch.name in ["unit", "integration", "loose_tests"]:
        cmd.extend([f"--cov={self.source_dir}", "--cov-report=term-missing"])
        # 新增：Typeguard 运行时类型检查
        cmd.extend(["--typeguard-packages", str(self.source_dir)])

    # 失败快速停止（阻断批次）
    if batch.blocking:
        cmd.append("--maxfail=5")

    return cmd
```

#### 4.1.3 差异说明

在覆盖率配置之后添加一行：
```python
cmd.extend(["--typeguard-packages", str(self.source_dir)])
```

---

### 4.2 PytestAgent 修改

**文件**: `agents/quality_agents.py`  
**修改位置**: 多处

#### 4.2.1 修改 `run_tests_sequential` 方法签名

**位置**: 第656-708行

**修改前**:
```python
async def run_tests_sequential(
    self,
    test_files: list[str],
    timeout_per_file: int,
    round_index: int,
    round_type: str,
) -> dict[str, object]:
```

**修改后**:
```python
async def run_tests_sequential(
    self,
    test_files: list[str],
    timeout_per_file: int,
    round_index: int,
    round_type: str,
    source_dir: str | None = None,
) -> dict[str, object]:
```

#### 4.2.2 修改 `run_tests_sequential` 方法内部调用

**位置**: 约第690行

**修改前**:
```python
file_result = await self._run_pytest_single_file(
    test_file=test_file,
    timeout=timeout_per_file,
)
```

**修改后**:
```python
file_result = await self._run_pytest_single_file(
    test_file=test_file,
    timeout=timeout_per_file,
    source_dir=source_dir,
)
```

#### 4.2.3 修改 `_run_pytest_single_file` 方法签名

**位置**: 第719-814行

**修改前**:
```python
async def _run_pytest_single_file(
    self,
    test_file: str,
    timeout: int,
) -> PytestFileResult:
```

**修改后**:
```python
async def _run_pytest_single_file(
    self,
    test_file: str,
    timeout: int,
    source_dir: str | None = None,
) -> PytestFileResult:
```

#### 4.2.4 修改命令构建

**位置**: 约第752-754行

**修改前**:
```python
cmd = f'pytest {test_file} -v --tb=short --json-report --json-report-file={tmp_json_path} -o addopts='
```

**修改后**:
```python
# 构建基础命令
base_cmd = f'pytest {test_file} -v --tb=short --json-report --json-report-file={tmp_json_path}'

# 添加 typeguard 参数（如果提供了 source_dir）
if source_dir:
    cmd = f'{base_cmd} --typeguard-packages={source_dir} -o addopts='
else:
    cmd = f'{base_cmd} -o addopts='
```

#### 4.2.5 新增类型错误识别辅助方法

**位置**: 在 `PytestAgent` 类末尾添加

```python
def _is_typeguard_error(self, failure: dict[str, Any]) -> bool:
    """
    判断是否为 typeguard 产生的类型错误
    
    Args:
        failure: 失败信息字典
        
    Returns:
        bool: 是否为类型错误
    """
    message = str(failure.get("message", ""))
    type_error_patterns = [
        "TypeError",
        "was expected, got",
        "type of argument",
    ]
    return any(pattern in message for pattern in type_error_patterns)
```

---

### 4.3 PytestController 修改

**文件**: `controllers/pytest_controller.py`  
**修改位置**: 多处

#### 4.3.1 修改 `_run_test_phase_all_files` 方法

**位置**: 第130-174行

**修改前**:
```python
round_result = await self.pytest_agent.run_tests_sequential(
    test_files=test_files,
    timeout_per_file=180,
    round_index=round_index,
    round_type="initial",
)
```

**修改后**:
```python
round_result = await self.pytest_agent.run_tests_sequential(
    test_files=test_files,
    timeout_per_file=180,
    round_index=round_index,
    round_type="initial",
    source_dir=self.source_dir,
)
```

#### 4.3.2 修改 `_run_test_phase_failed_files` 方法

**位置**: 第176-213行

**修改前**:
```python
round_result = await self.pytest_agent.run_tests_sequential(
    test_files=failed_files,
    timeout_per_file=600,
    round_index=round_index,
    round_type="retry",
)
```

**修改后**:
```python
round_result = await self.pytest_agent.run_tests_sequential(
    test_files=failed_files,
    timeout_per_file=600,
    round_index=round_index,
    round_type="retry",
    source_dir=self.source_dir,
)
```

---

### 4.4 pyproject.toml 配置（可选）

在项目根目录的 `pyproject.toml` 中添加 typeguard 默认配置：

```toml
[tool.pytest.ini_options]
# 现有配置保持不变...

# Typeguard 配置
typeguard-packages = "src"
typeguard-collection-check-strategy = "ALL_ITEMS"
```

**注意**: 由于 PytestAgent 使用 `-o addopts=` 覆盖配置，此处配置仅对 PytestBatchExecutor 生效。

---

## 五、实施步骤

### 步骤 1：环境准备（P0）

```bash
# 1. 安装 typeguard
pip install typeguard

# 2. 验证 src 包可导入
python -c "import src"

# 3. 更新 requirements.txt
echo "typeguard>=4.0.0" >> requirements.txt
```

### 步骤 2：修改 PytestBatchExecutor（P0）

1. 打开 `agents/pytest_batch_executor.py`
2. 定位到 `_build_command` 方法（约第280行）
3. 在覆盖率配置后添加 typeguard 参数
4. 保存文件

### 步骤 3：修改 PytestAgent（P0）

1. 打开 `agents/quality_agents.py`
2. 修改 `run_tests_sequential` 方法签名，添加 `source_dir` 参数
3. 修改内部的 `_run_pytest_single_file` 调用，传递 `source_dir`
4. 修改 `_run_pytest_single_file` 方法签名和命令构建
5. 添加 `_is_typeguard_error` 辅助方法
6. 保存文件

### 步骤 4：修改 PytestController（P1）

1. 打开 `controllers/pytest_controller.py`
2. 修改 `_run_test_phase_all_files` 方法的调用，添加 `source_dir` 参数
3. 修改 `_run_test_phase_failed_files` 方法的调用，添加 `source_dir` 参数
4. 保存文件

### 步骤 5：验证集成（P0）

```bash
# 1. 运行单个测试文件验证
pytest tests/unit/test_example.py -v --typeguard-packages=src

# 2. 运行完整测试套件
pytest tests/unit -v --typeguard-packages=src

# 3. 验证类型错误被正确捕获（需要有意构造类型错误的测试用例）
```

---

## 六、验证检查清单

### 6.1 功能验证

- [ ] typeguard 安装成功（`pip show typeguard`）
- [ ] src 包可正常导入
- [ ] PytestBatchExecutor 命令包含 `--typeguard-packages` 参数
- [ ] PytestAgent 单文件测试命令包含 `--typeguard-packages` 参数
- [ ] 类型错误被正确捕获并显示在输出中
- [ ] 现有测试套件正常运行（无回归问题）

### 6.2 性能验证

- [ ] 记录启用 typeguard 前的测试执行时间
- [ ] 记录启用 typeguard 后的测试执行时间
- [ ] 性能增加在可接受范围内（<30%）

### 6.3 集成验证

- [ ] SDK 修复阶段能够接收到类型错误信息
- [ ] AI 修复提示词包含类型错误详情
- [ ] 整体质量门禁流程正常运行

---

## 七、回滚方案

如果集成后出现问题，可以快速回滚：

### 7.1 快速回滚

1. 在 `_build_command` 方法中注释掉 typeguard 行：
```python
# cmd.extend(["--typeguard-packages", str(self.source_dir)])
```

2. 在 `_run_pytest_single_file` 方法中恢复原始命令构建

### 7.2 完全回滚

```bash
# 卸载 typeguard
pip uninstall typeguard

# 使用 git 恢复修改的文件
git checkout -- agents/pytest_batch_executor.py
git checkout -- agents/quality_agents.py
git checkout -- controllers/pytest_controller.py
```

---

## 八、后续优化建议

### 8.1 性能优化

如果性能影响显著，可以：
1. 使用 `typeguard-collection-check-strategy = "FIRST_ONLY"` 减少集合检查开销
2. 仅对关键模块启用 typeguard，排除第三方库

### 8.2 错误处理增强

可以在 `_parse_json_report` 方法中增加类型错误的特殊处理：
```python
if self._is_typeguard_error(failure):
    failure["error_category"] = "type_error"
```

### 8.3 Prompt 优化

可以根据错误类型优化 AI 修复 Prompt，为类型错误提供更具针对性的修复指导。

---

## 九、参考资料

- Typeguard 官方文档: https://typeguard.readthedocs.io/
- Typeguard pytest 插件: https://typeguard.readthedocs.io/en/latest/userguide.html#using-the-pytest-plugin
- pytest 命令行选项: https://docs.pytest.org/en/stable/reference/reference.html#command-line-flags

---

## 十、变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-02-20 | 初始版本 |
