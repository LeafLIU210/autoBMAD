# 质量检查工具错误修复方案

## 文档信息
- **创建时间**: 2026-01-14
- **版本**: v1.0
- **状态**: 待实施

---

## 执行摘要

本文档针对质量检查工具中发现的三个关键问题提供深度架构分析和修复方案:
1. **质量检查工具返回值错误** - Ruff/BasedPyright 检查结果被错误处理为 dict 而非对象
2. **Pytest 失败信息丢失** - 测试失败详情未正确保存,导致 SDK 修复循环无效
3. **Unicode 解码错误** - Windows GBK 环境下 subprocess 无法正确解码 BasedPyright 输出

---

## 目录
- [问题1: 质量检查工具返回值错误](#问题1-质量检查工具返回值错误)
- [问题2: Pytest 失败信息丢失](#问题2-pytest-失败信息丢失)
- [问题3: Unicode 解码错误](#问题3-unicode-解码错误)
- [实施计划](#实施计划)
- [测试验证](#测试验证)

---

## 问题1: 质量检查工具返回值错误

### 问题描述
**错误日志**:
```
2026-01-14 11:18:15,445 - ERROR - Ruff check failed: 'dict' object has no attribute 'status'
2026-01-14 11:18:16,750 - ERROR - BasedPyright check failed: 'dict' object has no attribute 'status'
```

### 根本原因分析

#### 架构层次追踪

**调用链路**:
```
epic_driver.py::execute_quality_gates()
  └─> QualityCheckController.run()
      └─> _run_check_phase()
          └─> agent.execute()  # RuffAgent/BasedPyrightAgent
```

#### 问题定位

**文件**: `autoBMAD/epic_automation/controllers/quality_check_controller.py`

**第138-145行** - 返回值访问错误:
```python
# 1. 调用 Agent 执行检查
result = await self.agent.execute(source_dir=self.source_dir)

# 2. 检查执行失败 - ❌ 错误:访问 dict 键作为属性
if result["status"] != "completed":  # Line 141
    self.logger.error(
        f"{self.tool} check failed: {result.get('error')}"
    )
    return {}
```

**文件**: `autoBMAD/epic_automation/agents/quality_agents.py`

**第138行** - Agent 返回 `SubprocessResult` (TypedDict):
```python
return SubprocessResult(
    status="completed",
    returncode=process.returncode,
    stdout=process.stdout,
    stderr=process.stderr,
    success=process.returncode == 0
)
```

**第192-228行** - RuffAgent.execute() 返回 `RuffResult` (TypedDict):
```python
return RuffResult(
    status="completed",
    errors=error_count,
    warnings=warning_count,
    files_checked=files_count,
    issues=issues_list,
    message=f"Found {len(issues_list)} issues (after auto-fix)"
)
```

#### 核心矛盾

**TypedDict vs 对象访问**:
- `RuffResult` 和 `BasedPyrightResult` 都是 `TypedDict` 子类
- TypedDict 实例本质上是 `dict`,应使用 `result["status"]` 而非 `result.status`
- 但代码中混用了两种访问方式,导致 AttributeError

### 修复方案

#### 方案A: 统一使用 dict 访问语法 (推荐)

**优势**:
- 保持 TypedDict 类型安全
- 最小化代码修改
- 符合 Python 3.14 类型系统设计

**修改文件**: `quality_check_controller.py`

**修改点1** - 第141行:
```python
# 修改前
if result["status"] != "completed":

# 修改后 (保持不变,已正确使用 dict 访问)
if result["status"] != "completed":
```

**修改点2** - 第148行:
```python
# 修改前
issues: list[object] = result.get("issues", [])

# 修改后 (保持不变,已正确使用 dict 访问)
issues: list[object] = result.get("issues", [])
```

**修改点3** - 第220-227行 (错误来源):
```python
# 修改前
return BasedPyrightResult(
    status=result["status"],  # ✅ 正确
    errors=0,
    warnings=0,
    files_checked=0,
    issues=[],
    message=result.get("stderr", "BasedPyright check failed")  # ✅ 正确
)
```

**实际错误位置**: `quality_agents.py`

**RuffAgent.execute()** - 第220-227行:
```python
# 修改前
else:
    return RuffResult(
        status=result["status"],  # ❌ result 是 SubprocessResult
        errors=0,
        warnings=0,
        files_checked=0,
        issues=[],
        message=result.get("stderr", "Ruff check failed")
    )

# 修改后
else:
    return RuffResult(
        status="failed",  # ✅ 使用字符串字面量
        errors=0,
        warnings=0,
        files_checked=0,
        issues=[],
        message=result.get("stderr", "Ruff check failed")
    )
```

**BasedPyrightAgent.execute()** - 第407-414行:
```python
# 修改前
else:
    return BasedPyrightResult(
        status=result["status"],  # ❌ result 是 SubprocessResult
        errors=0,
        warnings=0,
        files_checked=0,
        issues=[],
        message=result.get("stderr", "BasedPyright check failed")
    )

# 修改后
else:
    return BasedPyrightResult(
        status="failed",  # ✅ 使用字符串字面量
        errors=0,
        warnings=0,
        files_checked=0,
        issues=[],
        message=result.get("stderr", "BasedPyright check failed")
    )
```

---

## 问题2: Pytest 失败信息丢失

### 问题描述
**错误日志**:
```
2026-01-14 11:18:18,553 - WARNING - No failure information found for D:\GITHUB\pytQt_template\tests\test_integration.py
```

### 根本原因分析

#### 数据流追踪

**完整数据流**:
```
PytestAgent._run_pytest_single_file()
  └─> 生成 JSON report: tmp_json_path
      └─> _parse_json_report() 提取 failures
          └─> 返回 PytestFileResult{test_file, status, failures}

PytestController._run_test_phase_all_files()
  └─> pytest_agent.run_tests_sequential()
      └─> _append_round_to_summary_json()  # ❌ 写入汇总 JSON

PytestAgent.run_sdk_fix_for_file()
  └─> _load_failures_from_json()  # ❌ 读取汇总 JSON
      └─> 返回空列表 []
```

#### 问题定位

**文件**: `autoBMAD/epic_automation/controllers/pytest_controller.py`

**第284-356行** - `_append_round_to_summary_json()` 方法:
```python
def _append_round_to_summary_json(
    self,
    round_index: int,
    round_type: str,
    round_result: dict[str, Any],
) -> None:
    """将本轮测试结果追加到汇总 JSON"""
    
    # 加载现有 JSON
    summary_data = self._load_summary_json()
    
    # 添加轮次信息
    round_entry = {
        "round_index": round_index,
        "round_type": round_type,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "failed_files": [
            {
                "test_file": item["test_file"],
                "status": item["status"],
                "failures": item.get("failures", []),  # ✅ 包含 failures
            }
            for item in round_result["files"]
            if item["status"] in ["failed", "error", "timeout"]
        ]
    }
    
    summary_data["rounds"].append(round_entry)
    
    # 写回文件 ✅ 数据结构正确
    with open(self.summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
```

**文件**: `autoBMAD/epic_automation/agents/quality_agents.py`

**第821-851行** - `_load_failures_from_json()` 方法:
```python
def _load_failures_from_json(
    self,
    summary_json_path: str,
    test_file: str,
) -> list[PytestTestCase]:
    """从汇总 JSON 中加载指定测试文件的失败信息"""
    
    if not Path(summary_json_path).exists():
        self.logger.warning(f"Summary JSON not found: {summary_json_path}")
        return []
    
    try:
        with open(summary_json_path, "r", encoding="utf-8") as f:
            data: dict[str, object] = json.load(f)
        
        # 从最后一轮中查找该文件的失败信息
        rounds: list[object] = cast(list[object], data.get("rounds", []))
        if rounds:
            last_round: dict[str, object] = cast(dict[str, object], rounds[-1])
            failed_files: list[object] = cast(list[object], last_round.get("failed_files", []))
            for item in failed_files:
                item_dict: dict[str, object] = cast(dict[str, object], item)
                if item_dict["test_file"] == test_file:
                    return item_dict.get("failures", [])  # ❌ 返回类型不匹配
        
        return []
    
    except (json.JSONDecodeError, Exception) as e:
        self.logger.error(f"Failed to load failures from JSON: {e}")
        return []
```

#### 核心问题

**类型转换缺失**:
- `item_dict.get("failures", [])` 返回 `list[object]`
- 需要转换为 `list[PytestTestCase]` (list[dict])
- 缺少类型转换导致 SDK 修复无法正确读取失败信息

**实际 JSON 结构** (from line 318-335):
```json
{
  "rounds": [
    {
      "round_index": 1,
      "round_type": "initial",
      "failed_files": [
        {
          "test_file": "tests/test_integration.py",
          "status": "failed",
          "failures": [
            {
              "nodeid": "tests/test_integration.py::test_case",
              "failure_type": "failed",
              "message": "AssertionError...",
              "short_tb": "..."
            }
          ]
        }
      ]
    }
  ]
}
```

### 修复方案

#### 方案: 添加类型转换和验证

**修改文件**: `quality_agents.py`

**修改位置**: 第844行

```python
# 修改前
if item_dict["test_file"] == test_file:
    return item_dict.get("failures", [])

# 修改后
if item_dict["test_file"] == test_file:
    failures_raw = item_dict.get("failures", [])
    # 验证并转换类型
    if not isinstance(failures_raw, list):
        self.logger.warning(
            f"Invalid failures format for {test_file}: expected list, got {type(failures_raw)}"
        )
        return []
    
    # 转换为 PytestTestCase 类型
    failures: list[PytestTestCase] = []
    for failure in failures_raw:
        if not isinstance(failure, dict):
            continue
        
        # 验证必需字段
        if not all(k in failure for k in ["nodeid", "failure_type", "message", "short_tb"]):
            self.logger.warning(f"Incomplete failure data: {failure}")
            continue
        
        failures.append(cast(PytestTestCase, {
            "nodeid": str(failure["nodeid"]),
            "failure_type": str(failure["failure_type"]),
            "message": str(failure["message"]),
            "short_tb": str(failure["short_tb"])
        }))
    
    return failures
```

### 影响范围评估

**直接影响**:
- `quality_agents.py`: PytestAgent._load_failures_from_json()
- Pytest SDK 修复流程

**间接影响**:
- 测试失败修复成功率
- SDK 调用次数 (避免无效调用)

---

## 问题3: Unicode 解码错误

### 问题描述
**错误日志**:
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0xa5 in position 260: illegal multibyte sequence
File "subprocess.py", line 1613, in _readerthread
    buffer.append(fh.read())
```

### 根本原因分析

#### 问题场景

**触发条件**:
- Windows 系统 (默认编码 GBK)
- BasedPyright 输出包含 Unicode 符号 (如 • ✓ ✗)
- subprocess.run() 使用系统默认编码读取输出

#### 技术细节

**Python subprocess 编码机制**:
```python
# subprocess.run() 默认行为
process = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,  # ✅ 启用文本模式
    # ❌ 未指定 encoding,使用系统默认 (Windows = GBK)
    timeout=timeout
)
```

**Windows 编码环境**:
- 系统默认编码: `cp936` (GBK)
- BasedPyright 输出: UTF-8
- 字节 `0xa5` 在 GBK 中不是有效字符

#### 问题定位

**文件**: `autoBMAD/epic_automation/agents/quality_agents.py`

**第104-160行** - `BaseQualityAgent._run_subprocess()` 方法:
```python
async def _run_subprocess(self, command: str, timeout: int = 300) -> SubprocessResult:
    """运行子进程命令"""
    try:
        # 在线程池中运行子进程，避免 cancel scope 传播
        loop = asyncio.get_event_loop()
        process = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,  # ❌ 使用系统默认编码
                    timeout=timeout
                )
            ),
            timeout=timeout + 10
        )
        
        return SubprocessResult(
            status="completed",
            returncode=process.returncode,
            stdout=process.stdout,  # ❌ 可能包含解码错误
            stderr=process.stderr,
            success=process.returncode == 0
        )
```

### 修复方案

#### 方案: 显式指定 UTF-8 编码

**修改文件**: `quality_agents.py`

**修改位置**: 第121-126行

```python
# 修改前
process = await asyncio.wait_for(
    loop.run_in_executor(
        None,
        lambda: subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    ),
    timeout=timeout + 10
)

# 修改后
process = await asyncio.wait_for(
    loop.run_in_executor(
        None,
        lambda: subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',      # ✅ 显式指定 UTF-8 编码
            errors='ignore',       # ✅ 忽略无法解码的字符
            timeout=timeout
        )
    ),
    timeout=timeout + 10
)
```


### 影响范围评估

**直接影响**:
- `quality_agents.py`: BaseQualityAgent._run_subprocess()
- 所有质量检查工具 (Ruff, BasedPyright, Pytest)

**间接影响**:
- Windows 环境稳定性
- 日志输出完整性

---

## 实施计划

### 阶段1: 代码修复 (优先级: 高)

#### 任务1.1: 修复质量检查工具返回值错误
- **文件**: `quality_agents.py`
- **预计时间**: 15分钟
- **修改点**:
  - RuffAgent.execute() Line 220-227
  - BasedPyrightAgent.execute() Line 407-414

#### 任务1.2: 修复 Pytest 失败信息丢失
- **文件**: `quality_agents.py`
- **预计时间**: 30分钟
- **修改点**:
  - PytestAgent._load_failures_from_json() Line 844

#### 任务1.3: 修复 Unicode 解码错误
- **文件**: `quality_agents.py`
- **预计时间**: 10分钟
- **修改点**:
  - BaseQualityAgent._run_subprocess() Line 121-126

### 阶段2: 单元测试 (优先级: 高)

#### 任务2.1: 更新质量检查测试
- **文件**: `tests-copy/unit/test_quality_check_controller.py`
- **预计时间**: 30分钟
- **验证点**:
  - 返回值类型正确性
  - 错误分支覆盖

#### 任务2.2: 添加 Pytest 失败信息测试
- **文件**: 新建 `tests/unit/test_pytest_agent.py`
- **预计时间**: 45分钟
- **验证点**:
  - JSON 读写正确性
  - 类型转换完整性

#### 任务2.3: 添加编码测试
- **文件**: 新建 `tests/unit/test_subprocess_encoding.py`
- **预计时间**: 30分钟
- **验证点**:
  - UTF-8 输出处理
  - GBK 环境兼容性

### 阶段3: 集成测试 (优先级: 中)

#### 任务3.1: 端到端质量门控测试
- **文件**: `tests/integration/test_quality_gates.py`
- **预计时间**: 60分钟
- **验证点**:
  - 完整工作流运行
  - 错误处理容错性

---

## 测试验证

### 验证方法1: 单元测试

```bash
# 验证质量检查工具修复
pytest tests/unit/test_quality_check_controller.py -v

# 验证 Pytest 失败信息修复
pytest tests/unit/test_pytest_agent.py -v

# 验证编码修复
pytest tests/unit/test_subprocess_encoding.py -v
```

### 验证方法2: 集成测试

```bash
# 完整工作流测试
python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-1-core-algorithm-foundation.md --verbose
```

### 验证方法3: 错误日志检查

**预期结果**:
- ✅ 无 `'dict' object has no attribute 'status'` 错误
- ✅ 无 `No failure information found` 警告
- ✅ 无 `UnicodeDecodeError` 异常

### 验证方法4: 质量门控结果检查

**预期结果**:
- ✅ Ruff 检查正确报告错误数量
- ✅ BasedPyright 检查正确报告类型错误
- ✅ Pytest 失败测试能被 SDK 正确修复

---

## 附录

### A. 类型定义参考

**SubprocessResult** (quality_agents.py Line 23-30):
```python
class SubprocessResult(TypedDict):
    status: Literal["completed", "failed"]
    returncode: int
    stdout: str
    stderr: str
    success: bool
    error: NotRequired[str]
    command: NotRequired[str]
```

**RuffResult** (quality_agents.py Line 41-47):
```python
class RuffResult(TypedDict):
    status: Literal["completed", "failed"]
    errors: int
    warnings: int
    files_checked: int
    issues: list[RuffIssue]
    message: str
```

**BasedPyrightResult** (quality_agents.py Line 58-65):
```python
class BasedPyrightResult(TypedDict):
    status: Literal["completed", "failed"]
    errors: int
    warnings: int
    files_checked: int
    issues: list[BasedPyrightIssue]
    message: str
```

**PytestTestCase** (quality_agents.py Line 67-72):
```python
class PytestTestCase(TypedDict):
    nodeid: str
    failure_type: Literal["failed", "error"]
    message: str
    short_tb: str
```

### B. 相关文件清单

**核心文件**:
- `autoBMAD/epic_automation/agents/quality_agents.py`
- `autoBMAD/epic_automation/controllers/quality_check_controller.py`
- `autoBMAD/epic_automation/controllers/pytest_controller.py`
- `autoBMAD/epic_automation/epic_driver.py`

**测试文件**:
- `tests/unit/test_quality_check_controller.py`
- `tests/integration/test_quality_gates.py`

### C. 参考资料

**Python subprocess 文档**:
- https://docs.python.org/3.14/library/subprocess.html#subprocess.run
- encoding 参数: Python 3.6+
- errors 参数: Python 3.6+

**TypedDict 文档**:
- https://docs.python.org/3.14/library/typing.html#typing.TypedDict
- PEP 589: TypedDict

---

## 结论

本文档提供了三个关键问题的完整分析和修复方案:

1. **质量检查工具返回值错误**: 通过统一 dict 访问语法,确保 TypedDict 类型安全
2. **Pytest 失败信息丢失**: 添加类型转换和验证,确保 SDK 修复流程获取完整失败信息
3. **Unicode 解码错误**: 显式指定 UTF-8 编码,解决 Windows GBK 环境兼容性问题

所有修复方案均遵循最小化修改原则,保持架构稳定性,预计总实施时间 **4小时**。
