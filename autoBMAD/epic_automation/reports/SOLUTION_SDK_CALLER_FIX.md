# SDK 调用方统一修复方案

**文档版本**: v1.0  
**创建时间**: 2026-01-14  
**修复范围**: 仅调用方层面，SDK 执行层保持不动  
**遵循原则**: 奥卡姆剃刀 - 最简化路径统一

---

## 一、问题根因

### 1.1 核心错误

从日志 `epic_run_test.log` 提取的两类关键错误：

#### 错误 1: SDK options 类型不匹配
```
AttributeError: 'dict' object has no attribute 'can_use_tool'
位置: claude_agent_sdk/_internal/client.py:53 in process_query
```

**根本原因**:
- `PytestAgent._execute_sdk_call_with_cancel` 传递 `dict` 给 `SafeClaudeSDK.__init__(options={...})`
- `SafeClaudeSDK` 直接将此 dict 传给 `query(prompt, options=self.options)`
- Claude Agent SDK 期望 `options` 是 `ClaudeAgentOptions` 对象（带属性访问）
- 当 SDK 内部执行 `options.can_use_tool` 时，dict 无此属性导致异常

#### 错误 2: SDKResult 被误当作 dict 使用
```
AttributeError: 'SDKResult' object has no attribute 'get'
位置: quality_agents.py:845 in run_sdk_fix_for_file
```

**根本原因**:
- `SDKExecutor.execute()` 返回 `SDKResult` 对象
- `PytestAgent.run_sdk_fix_for_file()` 通过 `cast(dict[str, object], ...)` 强制类型断言
- 后续代码使用 `sdk_result.get("success", False)` 操作 dict 方法
- `SDKResult` 是 dataclass，没有 `.get()` 方法

### 1.2 设计不一致性

| 组件 | 当前调用模式 | options 类型 | 结果处理 | 是否符合规范 |
|------|-------------|-------------|---------|--------------|
| QualityCheckController | execute_sdk_call | ClaudeAgentOptions | SDKResult.is_success() | ✅ 符合 |
| SMAgent | 部分旧路径 | 混合 | 混合 | ⚠️ 待统一 |
| DevAgent | BaseAgent._execute_sdk_call | ClaudeAgentOptions | SDKResult | ✅ 符合 |
| QAAgent | BaseAgent._execute_sdk_call | ClaudeAgentOptions | SDKResult | ✅ 符合 |
| **PytestAgent** | **直接 new SafeClaudeSDK** | **dict** | **当 dict 用** | ❌ 不符合 |

---

## 二、修复策略

### 2.1 核心原则

**不可动层**:
- `SafeClaudeSDK` (sdk_wrapper.py)
- `SDKExecutor` (core/sdk_executor.py)
- `SDKResult` (core/sdk_result.py)
- `CancellationManager` (core/cancellation_manager.py)

**可修改层**:
- 所有 Agent 类中的 SDK 调用入口
- Controller 层对 SDK 结果的适配逻辑

### 2.2 统一路径设计

```
┌─────────────────────────────────────────────────────────┐
│                   Agent 调用层                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ BaseAgent._execute_sdk_call_with_config()        │  │
│  │         ↓                                         │  │
│  │ BaseAgent._execute_sdk_call()                    │  │
│  │         ↓                                         │  │
│  │ sdk_helper.execute_sdk_call()  ←← 统一入口      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              SDK 执行层 (不可修改)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. ClaudeAgentOptions 对象构造                   │  │
│  │ 2. query(prompt, options) → 异步生成器           │  │
│  │ 3. SDKExecutor.execute(sdk_func, target_pred)    │  │
│  │ 4. CancellationManager 跟踪与清理                │  │
│  │ 5. 返回 SDKResult                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   结果使用层                             │
│  • Agent 内部: 直接用 SDKResult 语义                   │
│    - result.is_success()                                │
│    - result.error_type                                  │
│    - result.get_error_summary()                         │
│  • Controller 边界: 转换为 dict (可选)                 │
│    - {"success": result.is_success(), ...}             │
└─────────────────────────────────────────────────────────┘
```

---

## 三、具体实施计划

### 3.1 PytestAgent 修复（优先级：🔴 P0）

#### 修改位置 1: `_execute_sdk_call_with_cancel` 方法

**文件**: `autoBMAD/epic_automation/agents/quality_agents.py`  
**行号**: 856-887

**现状问题**:
```python
async def _execute_sdk_call_with_cancel(self, prompt: str) -> object:
    from ..sdk_wrapper import SafeClaudeSDK
    from ..core.sdk_executor import SDKExecutor
    
    sdk = SafeClaudeSDK(
        prompt=prompt,
        options={"model": "claude-3-5-sonnet-20241022"},  # ❌ dict
        timeout=300.0,
    )
    
    executor = SDKExecutor()
    result = await executor.execute(
        sdk_func=sdk.execute,
        target_predicate=lambda msg: msg.get("type") == "done" or "END_OF_PATCH" in str(msg),
        agent_name="PytestAgent",
    )
    return result  # 返回 SDKResult，但调用方当 dict 用
```

**修复方案**:
```python
async def _execute_sdk_call_with_cancel(self, prompt: str) -> SDKResult:
    """
    执行 SDK 调用并处理取消流程（重构为统一路径）
    
    修复点:
    1. 使用 execute_sdk_call 统一入口
    2. 自动处理 ClaudeAgentOptions 构造
    3. 返回类型明确为 SDKResult
    """
    from ..core.sdk_result import SDKResult
    from .sdk_helper import execute_sdk_call
    
    # 统一调用，自动处理 options 类型转换
    result = await execute_sdk_call(
        prompt=prompt,
        agent_name="PytestAgent",
        timeout=300.0,
        permission_mode="bypassPermissions"
    )
    
    return result
```

**修改影响**:
- 删除对 `SafeClaudeSDK` 和 `SDKExecutor` 的直接导入和实例化
- options 构造由 sdk_helper 内部完成（使用 ClaudeAgentOptions）
- target_predicate 由 sdk_helper 标准实现（检测非错误 ResultMessage）

#### 修改位置 2: `run_sdk_fix_for_file` 方法

**文件**: `autoBMAD/epic_automation/agents/quality_agents.py`  
**行号**: 789-854

**现状问题**:
```python
async def run_sdk_fix_for_file(
    self,
    test_file: str,
    source_dir: str,
    summary_json_path: str,
    round_index: int,
) -> dict[str, bool | str]:
    # ... 前置逻辑 ...
    
    # ❌ 错误的类型断言和使用方式
    sdk_result: dict[str, object] = cast(dict[str, object], await self._execute_sdk_call_with_cancel(prompt))
    
    return {
        "success": cast(bool, sdk_result.get("success", False)),  # ❌ SDKResult 无 .get()
        "error": None
    }
```

**修复方案**:
```python
async def run_sdk_fix_for_file(
    self,
    test_file: str,
    source_dir: str,
    summary_json_path: str,
    round_index: int,
) -> dict[str, bool | str]:
    """
    对单个测试文件发起 SDK 修复调用
    
    修复点:
    1. 使用 SDKResult 语义替代 dict 操作
    2. 正确处理成功/失败判断
    """
    self.logger.info(f"Starting SDK fix for {test_file} (round {round_index})")
    
    try:
        # 1. 读取失败信息
        failures: list[PytestTestCase] = self._load_failures_from_json(summary_json_path, test_file)
        
        if not failures:
            self.logger.warning(f"No failure information found for {test_file}")
            return {"success": False, "error": "No failure information available"}
        
        # 2. 读取测试文件内容
        with open(test_file, "r", encoding="utf-8") as f:
            test_content = f.read()
        
        # 3. 构造 Prompt
        prompt = self._build_fix_prompt(
            test_file=test_file,
            source_dir=source_dir,
            test_content=test_content,
            failures=failures,
        )
        
        # 4. 调用 SDK（返回 SDKResult）
        from ..core.sdk_result import SDKResult
        sdk_result: SDKResult = await self._execute_sdk_call_with_cancel(prompt)
        
        # 5. 使用 SDKResult 语义
        if sdk_result.is_success():
            self.logger.info(
                f"SDK fix succeeded for {test_file} "
                f"(duration: {sdk_result.duration_seconds:.2f}s)"
            )
            return {
                "success": True,
                "error": None
            }
        else:
            error_summary = sdk_result.get_error_summary()
            self.logger.error(
                f"SDK fix failed for {test_file}: {error_summary}"
            )
            return {
                "success": False,
                "error": error_summary
            }
    
    except Exception as e:
        self.logger.error(f"SDK fix failed for {test_file}: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
```

**修改要点**:
- 移除 `cast(dict[str, object], ...)` 的错误类型断言
- 直接声明 `sdk_result: SDKResult`
- 使用 `sdk_result.is_success()` 判断
- 使用 `sdk_result.get_error_summary()` 获取错误信息
- 在 return 边界处转换为 dict（给 Controller 使用）

---

### 3.2 SMAgent 路径统一（优先级：🟡 P1）

#### 修改位置: `_fill_story_with_sdk` 方法

**文件**: `autoBMAD/epic_automation/agents/sm_agent.py`  
**预估行号**: 650-750（未完整展开，需确认）

**统一目标**:
```python
async def _fill_story_with_sdk(
    self,
    story_file: Path,
    story_id: str,
    epic_path: str,
    epic_content: str,
    manager: Any
) -> bool:
    """
    使用SDK填充故事文件内容
    
    修复点: 统一使用 execute_sdk_call 或 BaseAgent._execute_sdk_call
    """
    try:
        # 构造 Prompt
        prompt = self._build_sdk_prompt_for_story(
            story_id=story_id,
            story_file=story_file,
            epic_path=epic_path,
            epic_content=epic_content
        )
        
        # ✅ 统一路径：通过 BaseAgent 方法调用
        result = await self._execute_sdk_call_with_config(
            prompt=prompt,
            timeout=600.0,
            permission_mode="bypassPermissions"
        )
        
        # ✅ 使用 SDKResult 语义
        if result.is_success():
            self._log_execution(
                f"SDK filling succeeded for {story_id} "
                f"(duration: {result.duration_seconds:.2f}s)"
            )
            return True
        else:
            self._log_execution(
                f"SDK filling failed for {story_id}: {result.get_error_summary()}",
                "error"
            )
            return False
    
    except Exception as e:
        self._log_execution(f"SDK filling error for {story_id}: {e}", "error")
        return False
```

**检查要点**:
- 不再手工 new SafeClaudeSDK
- 不再手工 new SDKExecutor
- 通过 `self._execute_sdk_call[_with_config]` 统一调用
- 结果直接用 `SDKResult` 语义

---

### 3.3 质量门禁路径验证（优先级：🟢 P2）

#### 文件: `autoBMAD/epic_automation/controllers/quality_check_controller.py`

**当前状态**: ✅ 已符合规范

验证要点:
```python
async def _execute_sdk_fix(
    self,
    prompt: str,
    file_path: str,
) -> dict[str, Any]:
    """已正确使用 execute_sdk_call"""
    try:
        from ..agents.sdk_helper import execute_sdk_call
        
        # ✅ 正确使用统一入口
        result = await execute_sdk_call(
            prompt=prompt,
            agent_name=f"{self.tool.capitalize()}Agent",
            timeout=float(self.sdk_timeout),
            permission_mode="bypassPermissions"
        )
        
        # ✅ 正确使用 SDKResult 语义
        if result.is_success():
            return {
                "success": True,
                "result": result,
                "duration": result.duration_seconds
            }
        else:
            return {
                "success": False,
                "error": f"{result.error_type.value}: {', '.join(result.errors)}"
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**结论**: 无需修改，作为标准参考范例。

---

## 四、测试验证计划

### 4.1 单元验证（每个修改点）

#### PytestAgent 验证
```python
# 测试文件: tests/unit/test_pytest_agent_sdk_fix.py
import pytest
from autoBMAD.epic_automation.agents.quality_agents import PytestAgent
from autoBMAD.epic_automation.core.sdk_result import SDKResult

@pytest.mark.asyncio
async def test_execute_sdk_call_with_cancel_returns_sdk_result():
    """验证返回类型为 SDKResult"""
    agent = PytestAgent()
    
    result = await agent._execute_sdk_call_with_cancel("test prompt")
    
    assert isinstance(result, SDKResult)
    assert hasattr(result, "is_success")
    assert hasattr(result, "get_error_summary")

@pytest.mark.asyncio
async def test_run_sdk_fix_for_file_uses_sdk_result():
    """验证正确使用 SDKResult 语义"""
    agent = PytestAgent()
    
    # 使用 mock 避免实际 SDK 调用
    with patch.object(agent, '_execute_sdk_call_with_cancel') as mock_sdk:
        mock_sdk.return_value = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            session_id="test",
            agent_name="PytestAgent"
        )
        
        result = await agent.run_sdk_fix_for_file(
            test_file="tests/test_example.py",
            source_dir="src",
            summary_json_path="summary.json",
            round_index=1
        )
        
        assert result["success"] is True
        assert "error" in result
```

#### SMAgent 验证
```python
# 测试文件: tests/unit/test_sm_agent_sdk_unified.py
@pytest.mark.asyncio
async def test_sm_agent_uses_unified_sdk_call():
    """验证 SM Agent 使用统一 SDK 路径"""
    agent = SMAgent()
    
    # 验证 _execute_sdk_call 方法存在且正确
    assert hasattr(agent, "_execute_sdk_call")
    assert hasattr(agent, "_execute_sdk_call_with_config")
```

### 4.2 集成验证（端到端）

#### 测试场景 1: Pytest 失败修复流程
```bash
# 执行测试
pytest tests/test_cli.py -v --tb=short

# 预期:
# 1. 不再出现 "dict object has no attribute 'can_use_tool'"
# 2. 不再出现 "SDKResult object has no attribute 'get'"
# 3. SDK 调用日志显示正确的 options 类型
```

#### 测试场景 2: SM 从 Epic 创建故事
```python
# 运行 SM 阶段
epic_path = "docs/epics/epic-1-core-algorithm-foundation.md"
sm_agent = SMAgent()
success = await sm_agent.create_stories_from_epic(epic_path)

# 验证:
# 1. SDK 调用使用统一路径
# 2. 日志中不出现 options 类型错误
# 3. SDKResult 正确判断成功/失败
```

#### 测试场景 3: 质量门禁自动修复
```python
# 运行 Ruff 检查 + SDK 修复
controller = QualityCheckController(
    tool="ruff",
    agent=RuffAgent(),
    source_dir="src"
)
result = await controller.run()

# 验证:
# 1. SDK 调用路径与 PytestAgent 一致
# 2. 结果处理逻辑一致
# 3. 无 options 类型异常
```

### 4.3 回归验证

检查修改后不影响现有功能:
- [ ] CancellationManager 的取消/清理逻辑正常工作
- [ ] SafeClaudeSDK 的消息流处理无变化
- [ ] SDKExecutor 的 TaskGroup 隔离保持有效
- [ ] 各 Agent 的业务逻辑（非 SDK 部分）无破坏

---

## 五、修改检查清单

### 5.1 代码修改

- [ ] `quality_agents.py::PytestAgent._execute_sdk_call_with_cancel`
  - [ ] 移除直接 new SafeClaudeSDK
  - [ ] 移除直接 new SDKExecutor
  - [ ] 改用 `execute_sdk_call`
  - [ ] 返回类型声明为 `SDKResult`

- [ ] `quality_agents.py::PytestAgent.run_sdk_fix_for_file`
  - [ ] 移除 `cast(dict[str, object], ...)`
  - [ ] 使用 `sdk_result.is_success()` 判断
  - [ ] 使用 `sdk_result.get_error_summary()` 获取错误
  - [ ] 边界处转换为 dict 返回

- [ ] `sm_agent.py::SMAgent._fill_story_with_sdk`
  - [ ] 确认使用 `_execute_sdk_call_with_config`
  - [ ] 确认结果使用 `SDKResult` 语义
  - [ ] 移除任何手工构造 options 的代码

### 5.2 类型检查

```bash
# 运行类型检查器
basedpyright autoBMAD/epic_automation/agents/quality_agents.py
basedpyright autoBMAD/epic_automation/agents/sm_agent.py

# 预期: 无 SDKResult 相关的类型错误
```

### 5.3 文档更新

- [ ] 更新 `agents/README.md`（如存在）说明统一 SDK 调用规范
- [ ] 在 `core/API_USAGE.md` 中补充"Agent 层 SDK 调用最佳实践"

---

## 六、风险评估与回滚

### 6.1 风险点

| 风险项 | 影响程度 | 缓解措施 |
|--------|---------|---------|
| PytestAgent 修改破坏测试修复流程 | 高 | 完整单元测试 + 手工验证 |
| SMAgent 修改影响故事创建 | 中 | 分支测试 + 逐步合并 |
| 引入新的类型不一致 | 低 | 代码审查 + basedpyright |

### 6.2 回滚方案

如果修改后出现严重问题:
1. 使用 Git 回滚到修改前的提交
2. 保留测试用例，用于验证后续修复
3. 重新评估修复策略，必要时采用渐进式修改

---

## 七、实施时间线

| 阶段 | 任务 | 预计时间 | 负责人 |
|------|------|---------|--------|
| Phase 1 | PytestAgent 修复 | 2h | - |
| Phase 2 | 单元测试编写与验证 | 1h | - |
| Phase 3 | SMAgent 路径统一 | 1.5h | - |
| Phase 4 | 集成测试与回归验证 | 2h | - |
| Phase 5 | 文档更新与代码审查 | 1h | - |
| **总计** | | **7.5h** | |

---

## 八、后续优化建议

修复完成后的增强方向（可选）:

1. **统一 SDK 配置管理**
   - 在 `sdk_helper` 中提供全局配置读取（如 model、timeout 默认值）
   - 各 Agent 可覆盖但保持接口一致

2. **增强 SDKResult 语义**
   - 添加 `to_dict()` 方法供 Controller 层使用
   - 避免每个 Controller 手工拼装 dict

3. **SDK 调用监控**
   - 在 `execute_sdk_call` 中统一记录指标（调用次数、成功率、平均耗时）
   - 用于后续性能优化和异常检测

4. **Agent SDK 调用规范文档**
   - 编写标准操作手册（SOP）
   - 新增 Agent 时强制遵循统一路径

---

## 附录 A: 关键代码片段对比

### PytestAgent 修改前后对比

#### 修改前（错误版本）
```python
# ❌ 问题代码
async def _execute_sdk_call_with_cancel(self, prompt: str) -> object:
    sdk = SafeClaudeSDK(
        prompt=prompt,
        options={"model": "claude-3-5-sonnet-20241022"},  # dict 类型
        timeout=300.0,
    )
    executor = SDKExecutor()
    result = await executor.execute(
        sdk_func=sdk.execute,
        target_predicate=lambda msg: msg.get("type") == "done",
        agent_name="PytestAgent",
    )
    return result

async def run_sdk_fix_for_file(...) -> dict[str, bool | str]:
    sdk_result: dict = cast(dict, await self._execute_sdk_call_with_cancel(prompt))
    return {"success": sdk_result.get("success", False)}  # ❌ SDKResult 无 .get()
```

#### 修改后（正确版本）
```python
# ✅ 修复后代码
async def _execute_sdk_call_with_cancel(self, prompt: str) -> SDKResult:
    from .sdk_helper import execute_sdk_call
    result = await execute_sdk_call(
        prompt=prompt,
        agent_name="PytestAgent",
        timeout=300.0,
        permission_mode="bypassPermissions"
    )
    return result

async def run_sdk_fix_for_file(...) -> dict[str, bool | str]:
    sdk_result: SDKResult = await self._execute_sdk_call_with_cancel(prompt)
    return {
        "success": sdk_result.is_success(),  # ✅ 正确使用 SDKResult API
        "error": None if sdk_result.is_success() else sdk_result.get_error_summary()
    }
```

---

## 附录 B: sdk_helper 标准使用示例

### 基础调用
```python
from autoBMAD.epic_automation.agents.sdk_helper import execute_sdk_call

result = await execute_sdk_call(
    prompt="Your task description here",
    agent_name="YourAgent",
    timeout=1800.0,
    permission_mode="bypassPermissions"
)

if result.is_success():
    print(f"成功: {result.target_message}")
else:
    print(f"失败: {result.get_error_summary()}")
```

### 在 BaseAgent 子类中使用
```python
class CustomAgent(BaseAgent):
    async def execute(self, task: str) -> bool:
        prompt = self._build_prompt(task)
        
        # 方式 1: 直接调用
        result = await self._execute_sdk_call(
            sdk_executor=None,  # 不再需要
            prompt=prompt,
            timeout=600.0
        )
        
        # 方式 2: 带配置
        result = await self._execute_sdk_call_with_config(
            prompt=prompt,
            timeout=600.0,
            permission_mode="bypassPermissions"
        )
        
        return result.is_success()
```

---

**文档结束**
