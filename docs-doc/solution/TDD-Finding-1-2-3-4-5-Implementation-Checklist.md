# Finding 1-5 TDD 实施检查清单

**用途**: 跟踪每个 Finding 的实施进度  
**对应文档**: `TDD-Finding-1-2-3-4-5-Comprehensive-Implementation-Plan.md`

---

## 使用说明

- [ ] 未开始
- [~] 进行中
- [x] 已完成
- [!] 阻塞/有问题

---

## Phase 0: 紧急修复 [P0]

### Finding 1: Session Manager 初始化故障

**分支**: `phase0/finding-1-session-manager-fix`

#### RED: 编写测试

- [ ] **Task 1.1**: 创建测试文件 `tests/unit/docuswarm/context/test_validator_finding1.py`
  - [ ] `test_context_validator_init_does_not_accept_session_manager`
  - [ ] `test_context_validator_init_without_params_succeeds`
  - [ ] `test_validate_context_with_llm_requires_session_manager_param`
  - [ ] `test_validate_context_with_llm_succeeds_with_session_manager`

- [ ] **Task 1.2**: 创建测试文件 `tests/unit/docuswarm/pipeline/test_orchestrator_finding1.py`
  - [ ] `test_orchestrator_init_without_context_validator_param`
  - [ ] `test_orchestrator_creates_context_validator_internally`
  - [ ] `test_session_manager_created_before_validation`
  - [ ] `test_orchestrator_start_pipeline_without_session_manager`

- [ ] **Task 1.3**: 运行测试确认失败
  ```bash
  pytest tests/unit/docuswarm/context/test_validator_finding1.py -v
  pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding1.py -v
  ```

#### GREEN: 实现代码

- [ ] **Task 1.4**: 修改 `ContextValidator.__init__`
  - [ ] 移除 `session_manager` 参数
  - [ ] 移除 `llm_validation_strategy` 参数
  - [ ] 删除 backward compatibility 代码
  - [ ] 运行测试: `pytest tests/unit/docuswarm/context/test_validator_finding1.py::TestContextValidatorInit -v`

- [ ] **Task 1.5**: 修改 `validate_context_with_llm` 签名
  - [ ] 添加 `session_manager: SessionManager` 必需参数
  - [ ] 移除 `self._session_manager` 检查
  - [ ] 在方法内创建 `LLMContextValidationStrategy`
  - [ ] 运行测试: `pytest tests/unit/docuswarm/context/test_validator_finding1.py::TestValidateContextWithLLM -v`

- [ ] **Task 1.6**: 修改 `HybridOrchestrator.__init__`
  - [ ] 移除 `context_validator` 参数
  - [ ] 修改 `ContextValidator()` 实例化（无参数）
  - [ ] 运行测试: `pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding1.py::TestOrchestratorInit -v`

- [ ] **Task 1.7**: 修改 `start_pipeline` 方法
  - [ ] 将 `session_manager = self._get_or_create_session_manager()` 移到验证前
  - [ ] 更新 `validate_context_with_llm` 调用，传入 `session_manager`
  - [ ] 运行测试: `pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding1.py::TestStartPipelineSessionManagerOrder -v`

#### REFACTOR: 清理代码

- [ ] **Task 1.8**: 删除遗留代码
  - [ ] 删除 `ContextValidator._session_manager` 实例变量
  - [ ] 删除 `ContextValidator._llm_validation_strategy` 实例变量
  - [ ] 删除所有 backward compatibility 代码块
  - [ ] 更新文档字符串

- [ ] **Task 1.9**: 验证所有测试通过
  ```bash
  pytest tests/unit/docuswarm/context/test_validator_finding1.py -v
  pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding1.py -v
  ```

#### 集成验证

- [ ] **Task 1.10**: 运行相关集成测试
  ```bash
  pytest tests/integration/test_pipeline_execution.py -v -k "test_full_pipeline"
  ```

---

### Finding 2: Pipeline ID 一致性

**分支**: `phase0/finding-2-pipeline-id-fix` (可与 F1 并行)

#### RED: 编写测试

- [ ] **Task 2.1**: 创建测试文件 `tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py`
  - [ ] `test_start_pipeline_does_not_accept_pipeline_id_param`
  - [ ] `test_created_pipeline_id_matches_returned_id`
  - [ ] `test_pipeline_status_update_uses_same_id`
  - [ ] `test_create_pipeline_does_not_accept_custom_id`

- [ ] **Task 2.2**: 运行测试确认失败
  ```bash
  pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py -v
  ```

#### GREEN: 实现代码

- [ ] **Task 2.3**: 修改 `start_pipeline` 签名
  - [ ] 移除 `pipeline_id: str | None = None` 参数
  - [ ] 更新文档字符串
  - [ ] 运行测试: `pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py::TestPipelineIdParameter -v`

- [ ] **Task 2.4**: 简化 ID 处理逻辑
  - [ ] 删除 `final_pipeline_id = pipeline_id or db_pipeline_id`
  - [ ] 直接使用 `db_pipeline_id` 或重命名为 `pipeline_id`
  - [ ] 更新所有 `final_pipeline_id` 引用为 `pipeline_id`
  - [ ] 运行测试: `pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py::TestPipelineIdConsistency -v`

- [ ] **Task 2.5**: 更新调用点
  - [ ] 修改 `cli/services/pipeline_service.py`
  - [ ] 移除 `pipeline_id=custom_id` 参数
  - [ ] 检查其他调用点

#### REFACTOR: 清理代码

- [ ] **Task 2.6**: 删除相关代码
  - [ ] 删除 `final_pipeline_id` 变量
  - [ ] 更新类型注解
  - [ ] 更新文档

- [ ] **Task 2.7**: 验证所有测试通过
  ```bash
  pytest tests/unit/docuswarm/pipeline/test_orchestrator_finding2.py -v
  ```

---

## Phase 1: 主干收敛 [P1]

### Finding 3: 统一节点执行器

**分支**: `phase1/finding-3-unify-executor` (依赖 Phase 0)

#### RED: 编写测试

- [ ] **Task 3.1**: 创建测试文件 `tests/unit/docuswarm/nodes/test_no_duplicate_executor.py`
  - [ ] `test_create_node_executor_not_in_dual_agent`
  - [ ] `test_execute_node_not_in_dual_agent`
  - [ ] `test_get_config_not_in_dual_agent`
  - [ ] `test_dual_agent_all_does_not_include_executor`
  - [ ] `test_graph_uses_node_execution_executor`

- [ ] **Task 3.2**: 创建测试文件 `tests/unit/docuswarm/node_execution/test_executor_is_unique.py`
  - [ ] `test_executor_uses_load_config`

- [ ] **Task 3.3**: 运行测试确认失败
  ```bash
  pytest tests/unit/docuswarm/nodes/test_no_duplicate_executor.py -v
  ```

#### GREEN: 实现代码

- [ ] **Task 3.4**: 删除重复函数
  - [ ] 删除 `create_node_executor()` (lines ~926-958)
  - [ ] 删除 `_execute_node()` (lines ~961-1058)
  - [ ] 删除 `_get_config()` (lines ~1061-1079)
  - [ ] 运行测试: `pytest tests/unit/docuswarm/nodes/test_no_duplicate_executor.py::TestNoDuplicateExecutor -v`

- [ ] **Task 3.5**: 删除 legacy 桥接代码
  - [ ] 删除 lines 204-249
  - [ ] 运行测试: `pytest tests/unit/docuswarm/nodes/test_no_duplicate_executor.py::TestNoLegacyBridge -v`

- [ ] **Task 3.6**: 更新 `__all__`
  - [ ] 从 `__all__` 中移除 `"create_node_executor"`
  - [ ] 运行测试: `pytest tests/unit/docuswarm/nodes/test_no_duplicate_executor.py::TestNoDuplicateExecutor -v`

#### REFACTOR: 验证统一性

- [ ] **Task 3.7**: 验证执行路径
  - [ ] 确认 `pipeline/graph.py` 使用正确的导入
  - [ ] 确认配置来源统一

- [ ] **Task 3.8**: 运行所有节点相关测试
  ```bash
  pytest tests/unit/docuswarm/nodes/ -v
  pytest tests/unit/docuswarm/node_execution/ -v
  ```

- [ ] **Task 3.9**: 统计代码行数变化
  ```bash
  wc -l autoBMAD/docuswarm/nodes/dual_agent.py
  # 应减少约 150 行
  ```

---

### Finding 4: 统一状态模型

**分支**: `phase1/finding-4-unify-state-model` (依赖 Phase 0，可与 F3 并行)

#### RED: 编写测试

- [ ] **Task 4.1**: 创建测试文件 `tests/unit/docuswarm/storage/test_state_manager_finding4.py`
  - [ ] `test_state_manager_uses_pipeline_state_create_initial`
  - [ ] `test_create_pipeline_uses_create_initial_state`
  - [ ] `test_get_pipeline_returns_state_json_data`
  - [ ] `test_list_pipelines_returns_state_json_data`
  - [ ] `test_list_and_get_return_consistent_data`
  - [ ] `test_no_verify_state_consistency_method`
  - [ ] `test_update_only_modifies_state_json`

- [ ] **Task 4.2**: 运行测试确认失败
  ```bash
  pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py -v
  ```

#### GREEN: 实现代码

- [ ] **Task 4.3**: 添加导入
  - [ ] 在 `state_manager.py` 顶部添加 `from autoBMAD.docuswarm.pipeline.state import create_initial_state`
  - [ ] 运行测试确认导入正确

- [ ] **Task 4.4**: 删除 `_create_initial_state` 方法
  - [ ] 删除方法 (lines ~98-127)
  - [ ] 运行测试: `pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestNoDuplicateCreateInitialState -v`

- [ ] **Task 4.5**: 修改 `create_pipeline`
  - [ ] 使用 `create_initial_state` 替代 `_create_initial_state`
  - [ ] 运行测试: `pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestCreatePipelineUsesCreateInitialState -v`

- [ ] **Task 4.6**: 修改 `update_pipeline_status`
  - [ ] 改为只更新 `state_json`
  - [ ] 移除顶层列更新
  - [ ] 运行测试: `pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestUpdatePipelineStatusSimplification -v`

- [ ] **Task 4.7**: 修改 `get_pipeline`
  - [ ] 从 `state_json` 读取完整状态
  - [ ] 运行测试: `pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestStateJsonIsSingleSourceOfTruth::test_get_pipeline_returns_state_json_data -v`

- [ ] **Task 4.8**: 修改 `list_pipelines`
  - [ ] 从 `state_json` 读取状态
  - [ ] 运行测试: `pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestStateJsonIsSingleSourceOfTruth::test_list_pipelines_returns_state_json_data -v`

- [ ] **Task 4.9**: 删除 `_verify_state_consistency`
  - [ ] 删除整个方法 (lines ~167-209)
  - [ ] 运行测试: `pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestNoVerifyStateConsistency -v`

#### REFACTOR: 简化代码

- [ ] **Task 4.10**: 删除未使用的方法
  - [ ] 删除 `_update_state_json_partial`（如果不再使用）
  - [ ] 简化文档字符串

- [ ] **Task 4.11**: 验证一致性
  ```bash
  pytest tests/unit/docuswarm/storage/test_state_manager_finding4.py::TestStateJsonIsSingleSourceOfTruth::test_list_and_get_return_consistent_data -v
  ```

- [ ] **Task 4.12**: 运行所有存储相关测试
  ```bash
  pytest tests/unit/docuswarm/storage/ -v
  ```

---

## Phase 2: 清理漂移 [P1]

### Finding 5: 依赖和命名清理

**分支**: `phase2/finding-5-cleanup-drift` (依赖 Phase 0, 1)

#### RED: 编写测试

- [ ] **Task 5.1**: 创建测试文件 `tests/unit/test_finding5_dependency_cleanup.py`
  - [ ] `test_no_kaos_path_in_orchestrator`
  - [ ] `test_no_kimi_agent_sdk_in_approval`
  - [ ] `test_no_kimi_aggregator_in_session_manager`
  - [ ] `test_no_kimi_session_manager_alias`
  - [ ] `test_all_files_use_session_manager`
  - [ ] `test_pyproject_no_undeclared_dependencies`
  - [ ] `test_no_backward_compatibility_in_context_validator`
  - [ ] `test_no_legacy_in_dual_agent`

- [ ] **Task 5.2**: 运行测试确认失败
  ```bash
  pytest tests/unit/test_finding5_dependency_cleanup.py -v
  ```

#### GREEN: 实现代码

- [ ] **Task 5.3**: 移除 `kaos.path`
  - [ ] 修改 `orchestrator.py`: 替换 `from kaos.path import KaosPath` 为 `from pathlib import Path`
  - [ ] 替换所有 `KaosPath` 使用为 `Path`
  - [ ] 运行测试: `pytest tests/unit/test_finding5_dependency_cleanup.py::TestNoKaosPath -v`

- [ ] **Task 5.4**: 移除 `kimi_agent_sdk`
  - [ ] 修改 `approval.py`: 移除 `kimi_agent_sdk` 导入
  - [ ] 修改 `session_manager.py`: 移除 `kimi_agent_sdk` 和 `_aggregator` 导入
  - [ ] 运行测试: `pytest tests/unit/test_finding5_dependency_cleanup.py::TestNoKimiAgentSdk -v`

- [ ] **Task 5.5**: 删除别名并统一命名
  - [ ] 修改 `session_manager.py`: 删除 `KimiSessionManager = SessionManager` 行
  - [ ] 搜索替换所有 `KimiSessionManager` 为 `SessionManager`
    ```bash
    grep -r "KimiSessionManager" --include="*.py" autoBMAD/
    # 逐个文件修改
    ```
  - [ ] 运行测试: `pytest tests/unit/test_finding5_dependency_cleanup.py::TestNoKimiSessionManagerAlias -v`

- [ ] **Task 5.6**: 删除 deprecated/legacy 代码
  - [ ] 审查 `ContextValidator`: 删除 backward compatibility 代码
  - [ ] 审查 `dual_agent.py`: 删除 legacy 桥接（如还有残留）
  - [ ] 搜索并删除其他 deprecated 代码
  - [ ] 运行测试: `pytest tests/unit/test_finding5_dependency_cleanup.py::TestNoDeprecatedCode -v`

- [ ] **Task 5.7**: 更新 `pyproject.toml`
  - [ ] 确保所有运行时依赖已声明
  - [ ] 移除 `kimi-agent-sdk`（如存在）
  - [ ] 运行测试: `pytest tests/unit/test_finding5_dependency_cleanup.py::TestPyprojectDependencies -v`

#### REFACTOR: 验证清理

- [ ] **Task 5.8**: 全局验证
  ```bash
  # 验证无 kaos.path
  grep -r "from kaos.path" --include="*.py" autoBMAD/ || echo "PASS: No kaos.path imports"
  
  # 验证无 kimi_agent_sdk
  grep -r "kimi_agent_sdk" --include="*.py" autoBMAD/ || echo "PASS: No kimi_agent_sdk imports"
  
  # 验证无 KimiSessionManager
  grep -r "KimiSessionManager" --include="*.py" autoBMAD/ || echo "PASS: No KimiSessionManager usage"
  ```

- [ ] **Task 5.9**: 运行所有单元测试
  ```bash
  pytest tests/unit/ -v --tb=short
  ```

---

## 集成验证

### 集成测试

- [ ] **Task I.1**: 创建并运行集成测试
  ```bash
  pytest tests/integration/test_findings_1_to_5_integration.py -v
  ```

### 端到端测试

- [ ] **Task I.2**: 运行端到端测试
  ```bash
  pytest tests/e2e/ -v -k "pipeline" --timeout=300
  ```

### 覆盖率检查

- [ ] **Task I.3**: 检查覆盖率
  ```bash
  pytest tests/ --cov=autoBMAD.docuswarm --cov-report=term-missing
  # 目标: pipeline/*, node_execution/*, nodes/dual_agent.py 覆盖率 > 60%
  ```

---

## 最终验收

### 代码审查检查项

- [ ] 所有 Finding 的测试都已通过
- [ ] 代码审查完成（至少 1 人）
- [ ] 文档已更新
- [ ] CHANGELOG 已更新

### 性能验证

- [ ] 启动时间无明显增加
- [ ] 内存使用无明显增加
- [ ] 数据库查询次数未增加（或减少）

### 回滚准备

- [ ] 回滚步骤文档化
- [ ] 数据库迁移（如有）可回滚
- [ ] 发布标签已创建

---

## 实施时间表

| Phase | Finding | 预计时间 | 实际时间 | 状态 |
|-------|---------|---------|---------|------|
| 0 | F1 | 1 天 | | |
| 0 | F2 | 0.5 天 | | |
| 1 | F3 | 0.5 天 | | |
| 1 | F4 | 1 天 | | |
| 2 | F5 | 1 天 | | |
| - | 集成测试 | 0.5 天 | | |
| **总计** | | **4.5 天** | | |

---

## 问题跟踪

| ID | 日期 | Finding | 问题描述 | 解决方案 | 状态 |
|----|------|---------|---------|---------|------|
| | | | | | |

---

## 备注

- 每个 Finding 完成后，更新此检查清单
- 如遇阻塞，记录问题 ID 和解决方案
- 定期与团队同步进度
