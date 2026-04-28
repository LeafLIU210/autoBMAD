# DocuSwarm P0/P1 技术债务 TDD 执行摘要

> 创建日期: 2026-03-18
> 完整方案: [TDD 主方案](2026-03-18-docuswarm-p0-p1-tdd-master-plan.md)

---

## 快速导航

| 技术债务 | 严重级别 | 核心问题 | 测试文件 | 实施周期 |
|---------|---------|---------|---------|---------|
| TD-1 | P0 | state_json 重复表示 | `test_state_json_single_source.py` | Week 3-4 |
| TD-2 | P0 | Path.cwd() 依赖 | `test_output_dir_injection.py` | Week 1-2 |
| TD-3 | P1 | models 兼容层 | `test_models_deprecation.py` | Week 1-2 |
| TD-4 | P1 | 三套执行骨架 | `test_pipeline_adapter.py` | Month 2+ |
| TD-5 | P1 | CLI 过厚 | `test_commands_smoke.py` | Week 5-6 |

---

## 执行路线图

```
Week 1-2: 止血层
├── TD-2: 工具层 Path.cwd() 解耦
│   ├── CreateDeliverableTool(output_dir)
│   ├── CreateDocumentSetTool(output_dir)
│   └── 移除测试中的 os.chdir()
│
└── TD-3: models 兼容层清理
    ├── 查找所有 models 导入
    ├── 更新为 tools 直接导入
    └── 移除 models 模块

Week 3-4: 状态层
└── TD-1: state_json 唯一真相源
    ├── StateManager.create_pipeline() 写入完整 PipelineState
    ├── update_pipeline_status() 同步更新 state_json
    └── Orchestrator 从 state_json 恢复

Week 5-6: 控制层
└── TD-5: CLI 拆分
    ├── 创建 cli/commands/*.py
    ├── 创建 cli/services/*.py
    ├── main.py 变薄 (< 100行)
    └── Smoke tests

Month 2+: 架构层
└── TD-4: 执行骨架收敛
    ├── PipelineAdapter 边界层
    ├── 合成 ID 限制在 Adapter
    └── 逐步合并重复实现
```

---

## 关键测试清单

### TD-2: 工具层测试

```python
# 核心测试用例
test_tool_accepts_output_dir_parameter      # 接受 output_dir 参数
test_tool_uses_output_dir_instead_of_cwd    # 使用 output_dir 而非 Path.cwd()
test_tool_backward_compatibility            # 向后兼容
test_no_os_chdir_needed_in_tests            # 无需 os.chdir()
```

### TD-3: 兼容层测试

```python
# 核心测试用例
test_models_import_triggers_deprecation_warning    # 触发 DeprecationWarning
test_direct_tools_import_no_warning                # 直接导入无警告
test_models_module_not_importable                  # 模块不可导入（移除后）
```

### TD-1: 状态层测试

```python
# 核心测试用例
test_create_pipeline_writes_full_pipeline_state    # 写入完整 PipelineState
test_update_pipeline_state_updates_state_json      # 更新 state_json
test_state_json_is_source_of_truth_for_current_node # state_json 是唯一真相源
test_resume_uses_state_json_as_source              # 恢复使用 state_json
test_resume_state_consistency                      # 恢复状态一致性
```

### TD-5: CLI 测试

```python
# 核心测试用例
test_start_command_exists           # start 命令存在
test_status_command_exists          # status 命令存在
test_resume_command_exists          # resume 命令存在
test_service_start_creates_pipeline # Service 创建 pipeline
test_main_py_is_thin                # main.py < 100行
```

### TD-4: 架构层测试

```python
# 核心测试用例
test_adapter_creates_consistent_pipeline_id       # Adapter 创建一致 ID
test_no_synthetic_id_in_business_logic            # 业务逻辑无合成 ID
```

---

## 验收标准速查

### TD-1 (P0)
- [ ] `create_pipeline()` 写入完整 `PipelineState`
- [ ] `state_json` 包含所有必需字段
- [ ] `resume` 优先从 `state_json` 恢复
- [ ] 状态一致性测试通过

### TD-2 (P0)
- [ ] `CreateDeliverableTool` 接受 `output_dir`
- [ ] `CreateDocumentSetTool` 接受 `output_dir`
- [ ] 测试不再使用 `os.chdir()`
- [ ] 向后兼容

### TD-3 (P1)
- [ ] `models` 模块移除或惰性触发
- [ ] 所有代码直接使用 `tools` 导入
- [ ] DeprecationWarning 正确处理

### TD-4 (P1)
- [ ] 合成 ID 限制在 `PipelineAdapter`
- [ ] 业务逻辑无合成 ID 创建
- [ ] 新增平行模块被禁止

### TD-5 (P1)
- [ ] CLI 拆分为两层
- [ ] `main.py` < 100 行
- [ ] 所有命令有 Smoke tests
- [ ] Service 层有单元测试

---

## 运行测试

```bash
# 运行全部 TDD 测试
pytest tests/ -k "test_td" -v

# 运行特定 TD 测试
pytest tests/tools/test_output_dir_injection.py -v
pytest tests/unit/test_models_deprecation.py -v
pytest tests/storage/test_state_json_single_source.py -v
pytest tests/cli/test_commands_smoke.py -v

# 覆盖率报告
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=html
```

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 向后兼容破坏 | 高 | 保持默认参数，渐进式废弃 |
| 测试失败 | 中 | TDD 模式，测试先行 |
| 回归错误 | 中 | 每个 TD 独立分支，充分测试 |
| 周期过长 | 低 | 分阶段交付，独立验收 |

---

## 参考文档

- [完整 TDD 主方案](2026-03-18-docuswarm-p0-p1-tdd-master-plan.md)
- [技术债务深度研究报告](../research/2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md)
- [技术债务评估报告](../evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md)

---

*摘要生成时间: 2026-03-18*
