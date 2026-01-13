# Pytest 质量门控架构重构方案

**文档版本**: 1.0  
**创建日期**: 2026-01-13  
**适用范围**: autoBMAD/epic_automation 质量门控系统  

---

## 一、重构背景与目标

### 1.1 当前问题

现有 pytest 质量门控实现存在以下局限：

1. **批次级汇总，缺乏细粒度错误信息**：
   - 当前通过 `PytestBatchExecutor` 按目录批次执行，只能统计"多少批次通过/失败"；
   - 无法获取具体失败用例的详细信息（nodeid、错误类型、堆栈）；
   - 不支持基于失败信息的自动修复流程。

2. **无自动修复机制**：
   - pytest 失败后只记录错误，不进行任何修复尝试；
   - 历史存在的 `TestAutomationAgent + Claude SDK` 修复流程已从主线移除；
   - 质量门控变成"单向检测"而非"检测→修复→验证"的闭环。

3. **非阻断设计导致失败被忽略**：
   - 质量门控失败不会阻断 epic 流程；
   - 虽然记录了错误，但缺少后续跟踪和自动修复能力。

### 1.2 重构目标

1. **建立 pytest ↔ SDK 修复的闭环流程**：
   - 测试 → 收集失败详情 → SDK 修复 → 回归验证 → 循环直至通过或达到上限；
   - 每次 SDK 调用完成后正确触发取消管理器并等待确认。

2. **提供细粒度错误汇总**：
   - 按测试文件维度收集 FAIL/ERROR 信息；
   - 生成结构化 JSON，供 SDK 修复和人工审查使用。

3. **保持非阻断特性**：
   - 即使多轮修复后仍有失败，epic 流程仍能继续；
   - 但在结果中详细记录修复历史和最终失败状态。

4. **与现有架构无缝集成**：
   - 复用 SafeClaudeSDK、SDKExecutor、SDKCancellationManager 等成熟组件；
   - 保持 QualityGateOrchestrator 的总控职责不变。

---

## 二、架构设计总览

### 2.1 核心组件关系

```
QualityGateOrchestrator
    ↓ (Phase 3: Pytest)
PytestController (新增)
    ↓ 控制循环
    ├─→ PytestAgent (改造)
    │      ├─ run_tests_sequential() → 单文件 pytest 执行
    │      └─ run_sdk_fix_for_file() → 单文件 SDK 修复调用
    └─→ JSON 汇总管理
```

### 2.2 三阶段循环流程

```
┌─────────────────────────────────────────────────┐
│  Phase 1: 初始测试轮 (遍历全部测试文件)           │
│  - 递归枚举 tests/ 下所有 test_*.py             │
│  - 顺序执行 pytest -v --tb=short (timeout=10min)│
│  - 收集 FAIL/ERROR 信息 → 汇总 JSON             │
└────────────────┬────────────────────────────────┘
                 ↓
         [有失败文件?]
                 ↓ YES
┌─────────────────────────────────────────────────┐
│  Phase 2: SDK 修复轮                             │
│  - 遍历失败文件列表                              │
│  - 构造 Prompt (文件内容+失败信息)               │
│  - 调用 SafeClaudeSDK                           │
│  - 收到 ResultMessage → 触发取消 → 等待确认     │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│  Phase 3: 回归测试轮 (仅失败文件)                │
│  - 对上轮失败文件重新执行 pytest                 │
│  - 更新 failed_files 列表                       │
└────────────────┬────────────────────────────────┘
                 ↓
    [仍有失败 && cycle < max_cycles?]
                 ↓ YES: 回到 Phase 2
                 ↓ NO: 结束，返回结果
```

### 2.3 关键约束与配置

| 配置项 | 值 | 说明 |
|-------|-----|------|
| `max_cycles` | 3 | 最大修复循环次数 |
| `timeout_per_file` | 600秒 (10分钟) | 单个测试文件的 pytest 超时 |
| `summary_json_path` | `pytest_summary.json` | 汇总 JSON 文件路径 |
| `sdk_cancel_confirm` | 必须等待 | 每次 SDK 调用后必须确认取消成功 |

---

## 三、PytestController 详细设计

### 3.1 类定义与对外接口

```python
class PytestController:
    """
    Pytest 质量门控控制器
    职责：
    - 控制 pytest ↔ SDK 修复 的多轮循环
    - 维护失败文件列表和汇总 JSON
    - 决定循环终止条件
    """
    
    def __init__(
        self,
        source_dir: str,
        test_dir: str,
        max_cycles: int = 3,
        summary_json_path: str | None = None,
    ):
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.max_cycles = max_cycles
        self.summary_json_path = summary_json_path or "pytest_summary.json"
        
        # 状态
        self.current_cycle: int = 0
        self.failed_files: list[str] = []
        self.initial_failed_files: list[str] = []
        self.sdk_fix_errors: list[dict[str, Any]] = []
        
        # Agent 实例
        self.pytest_agent = PytestAgent()
    
    async def run(self) -> dict[str, Any]:
        """
        主入口：执行完整的 pytest ↔ SDK 修复 循环
        
        Returns:
            {
                "status": "completed" | "failed",
                "cycles": int,  # 实际执行的循环次数
                "initial_failed_files": list[str],
                "final_failed_files": list[str],
                "summary_json": str,
                "sdk_fix_attempted": bool,
                "sdk_fix_errors": list[dict],
            }
        """
```

### 3.2 方法拆分

#### 3.2.1 主循环驱动：`run()`

```python
async def run(self) -> dict[str, Any]:
    # 1. 首轮全量测试
    self.current_cycle = 1
    failed_files = await self._run_test_phase_all_files(round_index=1)
    self.initial_failed_files = failed_files.copy()
    
    # 2. 无失败则直接成功
    if not failed_files:
        return self._build_success_result()
    
    # 3. 进入修复循环
    while failed_files and self.current_cycle <= self.max_cycles:
        # SDK 修复阶段
        await self._run_sdk_phase(failed_files, round_index=self.current_cycle)
        
        # 回归测试阶段
        failed_files = await self._run_test_phase_failed_files(
            failed_files, 
            round_index=self.current_cycle + 1
        )
        
        self.current_cycle += 1
    
    # 4. 构造最终结果
    self.failed_files = failed_files
    return self._build_final_result()
```

#### 3.2.2 阶段一：全量测试 `_run_test_phase_all_files()`

```python
async def _run_test_phase_all_files(self, round_index: int) -> list[str]:
    """
    遍历 tests/ 下所有测试文件，依次执行 pytest
    
    Args:
        round_index: 轮次索引（用于 JSON 记录）
    
    Returns:
        有 FAIL/ERROR 的测试文件路径列表
    """
    # 1. 递归枚举测试文件
    test_files = self._discover_test_files()
    
    # 2. 调用 pytest agent 顺序执行
    round_result = await self.pytest_agent.run_tests_sequential(
        test_files=test_files,
        timeout_per_file=600,
        round_index=round_index,
        round_type="initial",
    )
    
    # 3. 提取失败文件列表
    failed_files = [
        item["test_file"] 
        for item in round_result["files"] 
        if item["status"] in ["failed", "error", "timeout"]
    ]
    
    # 4. 写入汇总 JSON
    self._append_round_to_summary_json(
        round_index=round_index,
        round_type="initial",
        round_result=round_result,
    )
    
    return failed_files
```

#### 3.2.3 阶段三：失败文件回归测试 `_run_test_phase_failed_files()`

```python
async def _run_test_phase_failed_files(
    self,
    failed_files: list[str],
    round_index: int,
) -> list[str]:
    """
    仅对失败文件执行回归 pytest
    
    Args:
        failed_files: 上一轮失败的测试文件列表
        round_index: 轮次索引
    
    Returns:
        本轮仍然 FAIL/ERROR 的测试文件列表
    """
    # 逻辑与 _run_test_phase_all_files 相似
    # 只是输入为 failed_files，round_type="retry"
    
    round_result = await self.pytest_agent.run_tests_sequential(
        test_files=failed_files,
        timeout_per_file=600,
        round_index=round_index,
        round_type="retry",
    )
    
    new_failed_files = [
        item["test_file"]
        for item in round_result["files"]
        if item["status"] in ["failed", "error", "timeout"]
    ]
    
    self._append_round_to_summary_json(
        round_index=round_index,
        round_type="retry",
        round_result=round_result,
    )
    
    return new_failed_files
```

#### 3.2.4 阶段二：SDK 修复 `_run_sdk_phase()`

```python
async def _run_sdk_phase(
    self,
    failed_files: list[str],
    round_index: int,
) -> None:
    """
    针对失败文件，依次触发 SDK 修复调用
    
    核心流程（每个文件）：
    1. 构造 Prompt（文件内容 + 失败信息）
    2. 调用 SDK（通过 pytest_agent）
    3. 收到 ResultMessage（完成信号）
    4. 触发取消 SDK 调用
    5. 等待取消确认成功
    6. 处理下一个文件
    
    Args:
        failed_files: 需要修复的测试文件列表
        round_index: 当前循环轮次
    """
    for test_file in failed_files:
        try:
            # 调用 pytest agent 的 SDK 修复接口
            result = await self.pytest_agent.run_sdk_fix_for_file(
                test_file=test_file,
                summary_json_path=self.summary_json_path,
                round_index=round_index,
            )
            
            if not result.get("success"):
                # 记录 SDK 调用层面的错误
                self.sdk_fix_errors.append({
                    "test_file": test_file,
                    "error": result.get("error", "Unknown SDK error"),
                    "round_index": round_index,
                })
        
        except Exception as e:
            # 捕获意外异常，不中断后续文件的修复
            self.sdk_fix_errors.append({
                "test_file": test_file,
                "error": f"SDK phase exception: {str(e)}",
                "round_index": round_index,
            })
```

#### 3.2.5 辅助方法

```python
def _discover_test_files(self) -> list[str]:
    """递归枚举 test_dir 下所有测试文件，按字典序排序"""
    from pathlib import Path
    test_path = Path(self.test_dir)
    test_files = sorted(
        list(test_path.rglob("test_*.py")) + 
        list(test_path.rglob("*_test.py"))
    )
    return [str(f) for f in test_files]

def _append_round_to_summary_json(
    self,
    round_index: int,
    round_type: str,
    round_result: dict[str, Any],
) -> None:
    """
    将本轮测试结果追加到汇总 JSON
    
    JSON 结构：
    {
      "summary": {...},
      "rounds": [
        {
          "round_index": 1,
          "round_type": "initial" | "retry",
          "failed_files": [
            {
              "test_file": "...",
              "status": "failed" | "error" | "timeout",
              "failures": [
                {
                  "nodeid": "...",
                  "failure_type": "...",
                  "message": "...",
                  "short_tb": "..."
                }
              ]
            }
          ]
        }
      ]
    }
    """
    # 实现略：加载现有 JSON → 追加 round → 写回

def _build_success_result(self) -> dict[str, Any]:
    """构造成功结果结构"""
    return {
        "status": "completed",
        "cycles": self.current_cycle,
        "initial_failed_files": self.initial_failed_files,
        "final_failed_files": [],
        "summary_json": self.summary_json_path,
        "sdk_fix_attempted": False,
        "sdk_fix_errors": [],
    }

def _build_final_result(self) -> dict[str, Any]:
    """构造最终结果结构"""
    return {
        "status": "completed" if not self.failed_files else "failed",
        "cycles": self.current_cycle,
        "initial_failed_files": self.initial_failed_files,
        "final_failed_files": self.failed_files,
        "summary_json": self.summary_json_path,
        "sdk_fix_attempted": True,
        "sdk_fix_errors": self.sdk_fix_errors,
    }
```

---

## 四、PytestAgent 接口改造

### 4.1 新增接口：顺序执行测试

```python
class PytestAgent(BaseQualityAgent):
    """
    Pytest 测试执行 Agent（改造版）
    新增职责：
    - 支持按文件顺序执行 pytest
    - 支持基于失败信息调用 SDK 修复
    """
    
    async def run_tests_sequential(
        self,
        test_files: list[str],
        timeout_per_file: int,
        round_index: int,
        round_type: str,
    ) -> dict[str, Any]:
        """
        按文件顺序执行 pytest -v --tb=short
        
        Args:
            test_files: 测试文件列表
            timeout_per_file: 每个文件的超时时间（秒）
            round_index: 轮次索引
            round_type: "initial" | "retry"
        
        Returns:
            {
                "files": [
                    {
                        "test_file": "...",
                        "status": "passed" | "failed" | "error" | "timeout",
                        "failures": [...],  # 仅当 status != passed
                    }
                ]
            }
        """
        results = []
        
        for test_file in test_files:
            # 执行单个文件的 pytest
            file_result = await self._run_pytest_single_file(
                test_file=test_file,
                timeout=timeout_per_file,
            )
            results.append(file_result)
        
        return {"files": results}
    
    async def _run_pytest_single_file(
        self,
        test_file: str,
        timeout: int,
    ) -> dict[str, Any]:
        """
        执行单个测试文件的 pytest
        
        命令：pytest <test_file> -v --tb=short --json-report --json-report-file=<tmp>
        
        Returns:
            {
                "test_file": str,
                "status": str,
                "failures": list[dict],  # 从 json-report 提取
            }
        """
        # 1. 构造命令
        import tempfile
        tmp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        cmd = f"pytest {test_file} -v --tb=short --json-report --json-report-file={tmp_json.name}"
        
        # 2. 执行（复用 BaseQualityAgent._run_subprocess）
        result = await self._run_subprocess(cmd, timeout=timeout)
        
        # 3. 解析 json-report
        failures = self._parse_json_report(tmp_json.name, test_file)
        
        # 4. 判断状态
        if result.get("status") == "failed" and "Timeout" in result.get("error", ""):
            status = "timeout"
        elif result["returncode"] == 0:
            status = "passed"
        elif failures:
            status = "failed" if any(f["failure_type"] == "failed" for f in failures) else "error"
        else:
            status = "error"
        
        return {
            "test_file": test_file,
            "status": status,
            "failures": failures,
        }
    
    def _parse_json_report(
        self,
        json_path: str,
        test_file: str,
    ) -> list[dict[str, Any]]:
        """
        从 pytest-json-report 中提取失败信息
        
        Returns:
            [
                {
                    "nodeid": "...",
                    "failure_type": "failed" | "error",
                    "message": "...",
                    "short_tb": "...",
                }
            ]
        """
        import json
        from pathlib import Path
        
        if not Path(json_path).exists():
            return []
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        failures = []
        for test in data.get("tests", []):
            if test.get("outcome") in ["failed", "error"]:
                # 仅保留当前测试文件的用例
                if not test["nodeid"].startswith(test_file):
                    continue
                
                failures.append({
                    "nodeid": test["nodeid"],
                    "failure_type": test["outcome"],
                    "message": test.get("call", {}).get("longrepr", "Unknown error"),
                    "short_tb": self._extract_short_traceback(test),
                })
        
        return failures
    
    def _extract_short_traceback(self, test: dict) -> str:
        """从 test 对象中提取精简的堆栈信息"""
        # 实现略：提取关键行号和错误位置
        return "..."
```

### 4.2 新增接口：SDK 修复单文件

```python
async def run_sdk_fix_for_file(
    self,
    test_file: str,
    summary_json_path: str,
    round_index: int,
) -> dict[str, Any]:
    """
    对单个测试文件发起 SDK 修复调用
    
    流程：
    1. 从汇总 JSON 中读取该文件的失败信息
    2. 读取测试文件内容
    3. 构造 Prompt（使用 Prompt 模板）
    4. 通过 SafeClaudeSDK 发起调用
    5. 收到 ResultMessage → 触发取消 → 等待确认
    6. 返回简单的成功/失败标志
    
    Args:
        test_file: 测试文件路径
        summary_json_path: 汇总 JSON 路径
        round_index: 当前轮次
    
    Returns:
        {
            "success": bool,
            "error": str | None,
        }
    """
    try:
        # 1. 读取失败信息
        failures = self._load_failures_from_json(summary_json_path, test_file)
        
        # 2. 读取测试文件内容
        with open(test_file, "r", encoding="utf-8") as f:
            test_content = f.read()
        
        # 3. 构造 Prompt
        prompt = self._build_fix_prompt(
            test_file=test_file,
            test_content=test_content,
            failures=failures,
        )
        
        # 4. 调用 SDK（通过 SafeClaudeSDK）
        sdk_result = await self._execute_sdk_call_with_cancel(prompt)
        
        return {"success": sdk_result.success}
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

async def _execute_sdk_call_with_cancel(self, prompt: str) -> Any:
    """
    执行 SDK 调用并处理取消流程
    
    关键步骤：
    1. 通过 SafeClaudeSDK 发起调用
    2. 通过 SDKExecutor 监听 ResultMessage
    3. 收到 ResultMessage 后，向 SDKCancellationManager 发出取消请求
    4. 等待取消确认
    5. 返回结果
    """
    from ..sdk_wrapper import SafeClaudeSDK
    from ..core.sdk_executor import SDKExecutor
    
    # 构造 SDK 包装器
    sdk = SafeClaudeSDK(
        prompt=prompt,
        options={"model": "claude-3-5-sonnet-20241022"},
        timeout=300.0,
    )
    
    # 通过 SDKExecutor 执行（内部会自动注册到 CancellationManager）
    executor = SDKExecutor()
    result = await executor.execute(
        sdk_func=sdk.execute,
        target_predicate=lambda msg: msg.get("type") == "done" or "END_OF_PATCH" in str(msg),
        agent_name="PytestAgent",
    )
    
    # 注意：SDKExecutor.execute() 内部已处理取消逻辑
    # 这里只需要返回结果即可
    return result

def _build_fix_prompt(
    self,
    test_file: str,
    test_content: str,
    failures: list[dict[str, Any]],
) -> str:
    """
    构造 SDK 修复提示词
    
    使用 Prompt 模板（见第五节）
    """
    # 实现略：按模板组装 system + user 指令
    return "..."
```

---

## 五、Prompt 结构模板

### 5.1 模板结构

```python
PROMPT_TEMPLATE = """
<system>
你是一名资深 Python 测试与代码修复专家。

目标：
- 根据给定的测试文件和失败信息，输出一个修复方案，使测试通过。
- 保持业务逻辑正确，避免无关重构。

约束：
- 只修改必要的代码（测试文件及相关源码）。
- 保持测试名称、语义和验收意图不变。
- 输出格式：先给出修改摘要，再给出每个文件的完整新版本。

输出格式示例：
## Summary of Changes
- 修复点 1
- 修复点 2

## Patched Files
### File: tests/unit/test_x.py
```python
# 完整修复后的测试文件内容
```

### File: src/module.py (如需修改源码)
```python
# 完整修复后的源码文件内容
```

<END_OF_PATCH>
</system>

<user>
## Test File Information
- **Test file path**: {test_file}
- **Project source dir**: {source_dir}

## Test File Content (Current)
```python
{test_content}
```

## Failures Summary
{failures_summary}

## Expected Result
修复导致上述失败的根因，使所有用例通过。若需要修改业务源码，请说明修改位置和原因。
</user>
"""

def _build_fix_prompt(
    self,
    test_file: str,
    test_content: str,
    failures: list[dict[str, Any]],
) -> str:
    """按模板构造 Prompt"""
    
    # 构造失败摘要部分
    failures_lines = []
    for i, failure in enumerate(failures, 1):
        failures_lines.append(f"""
### Case {i}
- **nodeid**: `{failure['nodeid']}`
- **type**: `{failure['failure_type']}`
- **message**: `{failure['message']}`
- **short traceback**: `{failure['short_tb']}`
        """.strip())
    
    failures_summary = "\n\n".join(failures_lines)
    
    # 填充模板
    prompt = PROMPT_TEMPLATE.format(
        test_file=test_file,
        source_dir=self.source_dir,
        test_content=test_content,
        failures_summary=failures_summary,
    )
    
    return prompt
```

### 5.2 Prompt 关键设计点

1. **明确角色与目标**：
   - system 指令定义"测试修复专家"角色；
   - 约束只修改必要代码，避免过度重构。

2. **结构化输入**：
   - 测试文件路径 + 完整内容；
   - 失败信息按用例分组，每个用例包含 nodeid、类型、消息、堆栈。

3. **标准化输出格式**：
   - 要求按"摘要 + 文件完整版本"输出；
   - 使用 `<END_OF_PATCH>` 作为完成标记，供 SDKExecutor 检测结束。

4. **与取消机制对接**：
   - Prompt 本身不关心取消逻辑；
   - 完成标记使 SDKExecutor 能正确判断"ResultMessage 已完成"；
   - PytestController 收到完成信号后触发取消流程。

---

## 六、与 QualityGateOrchestrator 集成

### 6.1 execute_pytest_agent() 改造

```python
# 文件：autoBMAD/epic_automation/epic_driver.py
# 类：QualityGateOrchestrator

async def execute_pytest_agent(self, test_dir: str) -> dict[str, Any]:
    """执行 Pytest 质量门（改造版：使用 PytestController）"""
    
    if self.skip_tests:
        self.logger.info("Skipping pytest execution (--skip-tests flag)")
        return {"success": True, "skipped": True, "message": "Skipped via CLI flag"}
    
    self.logger.info("=== Quality Gate 3/3: Pytest Execution with SDK Fix ===")
    self._update_progress("phase_3_pytest", "in_progress", start=True)
    
    try:
        # 前置检查（保持不变）
        # ... test_dir 存在性、测试文件检查、pytest 命令可用性 ...
        
        # 使用 PytestController 执行完整流程
        from .controllers.pytest_controller import PytestController
        
        controller = PytestController(
            source_dir=self.source_dir,
            test_dir=test_dir,
            max_cycles=3,
        )
        
        start_time = time.time()
        pytest_result = await controller.run()
        end_time = time.time()
        
        # 判断成功与否
        success = pytest_result["status"] == "completed"
        
        if success:
            self.logger.info(
                f"✓ Pytest quality gate PASSED after {pytest_result['cycles']} cycle(s) "
                f"in {self._calculate_duration(start_time, end_time)}s"
            )
            self._update_progress("phase_3_pytest", "completed", end=True)
            return {
                "success": True,
                "duration": self._calculate_duration(start_time, end_time),
                "result": pytest_result,
            }
        else:
            error_msg = (
                f"Pytest quality gate FAILED after {pytest_result['cycles']} cycle(s): "
                f"{len(pytest_result['final_failed_files'])} file(s) still failing"
            )
            self.logger.warning(f"✗ {error_msg}")
            self._update_progress("phase_3_pytest", "failed", end=True)
            self.results["errors"].append(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "duration": self._calculate_duration(start_time, end_time),
                "result": pytest_result,
            }
    
    except Exception as e:
        error_msg = f"Pytest execution error: {str(e)}"
        self.logger.error(error_msg)
        self._update_progress("phase_3_pytest", "error", end=True)
        self.results["errors"].append(error_msg)
        return {"success": False, "error": error_msg, "duration": 0.0}
```

### 6.2 非阻断特性保持

在 `EpicDriver.execute_quality_gates()` 中：

```python
async def execute_quality_gates(self) -> bool:
    """执行质量门控流水线（保持非阻断）"""
    
    # ... Ruff、BasedPyright 阶段 ...
    
    # Pytest 阶段
    if not self.skip_tests:
        pytest_result = await quality_orchestrator.execute_pytest_agent(self.test_dir)
        self.results["pytest"] = pytest_result
        
        if not pytest_result["success"]:
            self.results["success"] = False
            self.logger.warning("Quality gates completed with pytest failure")
            # 但仍然返回 True（非阻断设计）
    
    # 质量门控失败不阻断 epic 流程
    if not self.results.get("success"):
        self.logger.warning(
            "Quality gates failure is non-blocking - epic processing continues"
        )
    
    return True  # 始终返回 True
```

---

## 七、实施计划

### 7.1 阶段划分

| 阶段 | 任务 | 预估工时 |
|-----|------|---------|
| **Phase 1** | PytestController 基础框架 | 2天 |
| | - 创建 `controllers/pytest_controller.py` | |
| | - 实现主循环逻辑与状态管理 | |
| | - 实现 JSON 汇总读写 | |
| **Phase 2** | PytestAgent 接口改造 | 2天 |
| | - 实现 `run_tests_sequential()` | |
| | - 实现 `_run_pytest_single_file()` | |
| | - 实现 JSON-report 解析 | |
| **Phase 3** | SDK 修复集成 | 2天 |
| | - 实现 `run_sdk_fix_for_file()` | |
| | - 实现 Prompt 模板与构造 | |
| | - 对接 SafeClaudeSDK + 取消管理器 | |
| **Phase 4** | QualityGateOrchestrator 集成 | 1天 |
| | - 改造 `execute_pytest_agent()` | |
| | - 验证非阻断特性 | |
| **Phase 5** | 单元测试与集成测试 | 2天 |
| | - PytestController 单元测试 | |
| | - 端到端集成测试 | |
| **Phase 6** | 文档与验收 | 1天 |

总计：**10 工作日**

### 7.2 风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| SDK 修复效果不理想 | 循环无效，仍然失败 | - 优化 Prompt 模板<br>- 增加人工审查环节 |
| 单文件 pytest 执行慢 | 总耗时过长 | - 可选启用 xdist 并行<br>- 优先测试关键文件 |
| 取消管理器兼容性 | SDK 调用阻塞 | - 复用现有成熟组件<br>- 充分单元测试 |
| JSON 汇总体积过大 | 性能问题 | - 只记录必要字段<br>- 定期清理历史轮次 |

---

## 八、验收标准

### 8.1 功能验收

- [ ] PytestController 能正确执行 3 轮"测试 → SDK 修复 → 回归"循环
- [ ] 汇总 JSON 结构完整，包含所有失败信息
- [ ] SDK 调用后能正确触发取消并等待确认
- [ ] 质量门控失败不阻断 epic 流程
- [ ] 所有失败文件在结果中正确记录

### 8.2 性能验收

- [ ] 单文件 pytest 执行不超过 10 分钟
- [ ] 单文件 SDK 修复不超过 5 分钟
- [ ] 完整 3 轮循环（假设 10 个失败文件）在 1 小时内完成

### 8.3 质量验收

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试覆盖完整流程
- [ ] 无 basedpyright 类型错误
- [ ] 无 ruff 代码风格问题

---

## 九、附录

### 9.1 汇总 JSON 完整示例

```json
{
  "summary": {
    "total_files": 120,
    "failed_files_initial": 5,
    "failed_files_final": 1
  },
  "rounds": [
    {
      "round_index": 1,
      "round_type": "initial",
      "timestamp": "2026-01-13T10:00:00Z",
      "failed_files": [
        {
          "test_file": "tests/unit/test_x.py",
          "status": "failed",
          "failures": [
            {
              "nodeid": "tests/unit/test_x.py::test_something",
              "failure_type": "failed",
              "message": "AssertionError: expected 1 == 2",
              "short_tb": "test_x.py:42: AssertionError"
            }
          ]
        }
      ]
    },
    {
      "round_index": 2,
      "round_type": "retry",
      "timestamp": "2026-01-13T10:15:00Z",
      "failed_files": [
        {
          "test_file": "tests/unit/test_x.py",
          "status": "failed",
          "failures": [
            {
              "nodeid": "tests/unit/test_x.py::test_another",
              "failure_type": "error",
              "message": "TypeError: unsupported operand type",
              "short_tb": "test_x.py:55: TypeError"
            }
          ]
        }
      ]
    }
  ]
}
```

### 9.2 相关文件清单

**新增文件**：
- `autoBMAD/epic_automation/controllers/pytest_controller.py`

**修改文件**：
- `autoBMAD/epic_automation/agents/quality_agents.py` (PytestAgent)
- `autoBMAD/epic_automation/epic_driver.py` (QualityGateOrchestrator.execute_pytest_agent)

**新增测试**：
- `tests/unit/test_pytest_controller.py`
- `tests/integration/test_pytest_sdk_fix_workflow.py`

### 9.3 配置项说明

在 `pyproject.toml` 或环境变量中可配置：

```toml
[tool.pytest_controller]
max_cycles = 3
timeout_per_file = 600
summary_json_path = "pytest_summary.json"
sdk_timeout = 300
```

---

**文档结束**
