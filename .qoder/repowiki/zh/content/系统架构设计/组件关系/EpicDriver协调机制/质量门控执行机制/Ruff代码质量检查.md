# Ruff代码质量检查

<cite>
**本文档引用文件**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py)
- [quality_check_controller.py](file://autoBMAD/epic_automation/controllers/quality_check_controller.py)
- [quality_agents.py](file://autoBMAD/epic_automation/agents/quality_agents.py)
- [RUFF_BASEDPYRIGHT_QUALITY_GATE_REFACTOR_PLAN.md](file://docs-copy/refactor/RUFF_BASEDPYRIGHT_QUALITY_GATE_REFACTOR_PLAN.md)
</cite>

## 更新摘要
**已做更改**
- 更新了execute_ruff_agent方法的实现，使用QualityCheckController进行多轮检查和修复
- 详细说明了RuffAgent类的实现机制，包括subprocess同步执行、JSON解析和错误处理
- 解释了--skip-quality CLI标志对质量检查的控制作用
- 添加了Ruff检查与QualityGateOrchestrator的集成方式

## 目录
- [Ruff代码质量检查](#ruff代码质量检查)
  - [更新摘要](#更新摘要)
  - [目录](#目录)
  - [Ruff质量门控架构](#ruff质量门控架构)
    - [QualityCheckController实现机制](#qualitycheckcontroller实现机制)
    - [RuffAgent执行流程](#ruffagent执行流程)
    - [--skip-quality CLI标志控制](#--skip-quality-cli标志控制)
    - [多轮检查与自动修复流程](#多轮检查与自动修复流程)
    - [结果聚合与进度跟踪](#结果聚合与进度跟踪)
    - [异常处理策略](#异常处理策略)

## Ruff质量门控架构

### QualityCheckController实现机制
QualityCheckController是通用质量检查控制器，负责控制检查与SDK修复的多轮循环，维护错误文件列表，并决定循环终止条件。

**控制器初始化参数**
- tool: 工具类型 ('ruff' 或 'basedpyright')
- agent: 对应的Agent实例
- source_dir: 源代码目录
- max_cycles: 最大循环次数（默认3次）
- sdk_call_delay: SDK调用间延时（秒）
- sdk_timeout: SDK超时时间（秒）

控制器通过_run_check_phase方法执行质量检查，返回按文件分组的错误。检查失败时返回空字典，无错误时直接返回成功结果。控制器支持最多3轮的修复循环，每轮包括SDK修复阶段和回归检查阶段。

**Section sources**
- [quality_check_controller.py](file://autoBMAD/epic_automation/controllers/quality_check_controller.py#L25-L323)

### RuffAgent执行流程
RuffAgent继承自BaseQualityAgent，负责执行Ruff代码风格检查。其核心是_execute_check方法，通过subprocess运行Ruff命令进行同步执行。

**执行步骤**
1. 构建Ruff命令：`ruff check --fix --output-format=json {source_dir}`
2. 调用_run_subprocess方法执行命令
3. 解析JSON输出，统计错误、警告和检查文件数量
4. 返回标准化的检查结果

RuffAgent使用_run_subprocess方法在独立线程池中运行子进程，避免cancel scope传播。该方法设置了超时保护（默认300秒），并捕获TimeoutError和常规异常。

**Section sources**
- [quality_agents.py](file://autoBMAD/epic_automation/agents/quality_agents.py#L163-L238)

### --skip-quality CLI标志控制
--skip-quality CLI标志用于控制是否跳过Ruff和BasedPyright质量检查。在QualityGateOrchestrator初始化时接收此标志，并在执行质量检查前进行判断。

当skip_quality为True时，execute_ruff_agent方法会直接返回跳过结果，不执行实际检查：
```python
if self.skip_quality:
    self.logger.info("Skipping Ruff quality check (--skip-quality flag)")
    return {"success": True, "skipped": True, "message": "Skipped via CLI flag"}
```

此机制允许用户在不需要代码风格检查时快速跳过相关步骤，提高工作流效率。

**Section sources**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L100-L115)

### 多轮检查与自动修复流程
Ruff质量门控采用多轮检查与自动修复的闭环流程：

1. **首轮全量检查**：执行Ruff检查，获取初始错误文件列表
2. **无错误判断**：若无错误则直接成功
3. **修复循环**：进入最多3轮的修复循环
   - SDK修复阶段：针对每个错误文件调用SDK进行修复
   - 回归检查阶段：重新执行Ruff检查验证修复效果
4. **结果构造**：根据最终错误文件列表构造结果

QualityCheckController通过_run_sdk_fix_phase方法实现SDK修复，对每个错误文件：
1. 读取文件内容
2. 构造修复Prompt
3. 调用SafeClaudeSDK
4. 等待ResultMessage完成信号
5. 触发取消并等待确认
6. 延时60秒后处理下一个文件

**Section sources**
- [quality_check_controller.py](file://autoBMAD/epic_automation/controllers/quality_check_controller.py#L73-L119)

### 结果聚合与进度跟踪
QualityGateOrchestrator负责聚合所有质量检查结果并跟踪执行进度。其results字典包含完整的执行信息：

**结果结构**
- success: 整体成功状态
- ruff: Ruff检查结果
- basedpyright: BasedPyright检查结果
- pytest: Pytest测试结果
- errors: 错误消息列表
- start_time/end_time: 开始/结束时间
- total_duration: 总耗时
- progress: 进度跟踪信息

进度跟踪包含各阶段的状态、开始时间和结束时间，用于监控质量门控流水线的执行情况。

**Section sources**
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L130-L164)

### 异常处理策略
系统采用多层次的异常处理策略确保稳定性：

**QualityCheckController异常处理**
- _run_check_phase：捕获超时和常规异常，返回失败结果
- _run_sdk_fix_phase：捕获文件读取、SDK调用等异常，记录错误并继续
- _execute_sdk_fix：捕获SDK执行异常，返回失败结果

**RuffAgent异常处理**
- _run_subprocess：捕获TimeoutError和常规异常，返回标准化失败结果
- execute方法：捕获执行过程中的异常，返回失败结果

**QualityGateOrchestrator异常处理**
- execute_ruff_agent：捕获控制器执行异常，更新进度为错误状态
- execute_quality_gates：捕获整个流水线异常，确保返回完整结果

所有异常都会被记录到日志中，并添加到results的errors列表中，但不会阻断整个质量门控流程。

**Section sources**
- [quality_check_controller.py](file://autoBMAD/epic_automation/controllers/quality_check_controller.py#L163-L245)
- [quality_agents.py](file://autoBMAD/epic_automation/agents/quality_agents.py#L104-L160)
- [epic_driver.py](file://autoBMAD/epic_automation/epic_driver.py#L247-L253)