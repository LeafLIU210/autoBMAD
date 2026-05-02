# DocuSwarm F1-F5 测试驱动修复方案

本目录包含针对 `autoBMAD/docuswarm` F1-F5 问题的完整测试驱动修复方案。

## 📋 文档清单

| 文档 | 用途 | 说明 |
|------|------|------|
| `2026-04-08-docuswarm-f1-f5-test-driven-fix-plan.md` | **完整TDD方案** | 详细的测试用例、实现步骤、代码示例 |
| `2026-04-08-docuswarm-f1-f5-quick-implementation-guide.md` | **快速实施指南** | 按天划分的执行计划、命令行操作 |
| `README.md` | **本文件** | 方案概览和快速导航 |

## 🔬 测试文件清单

位于 `tests/docuswarm/` 下：

| 测试文件 | 对应问题 | 当前状态 |
|---------|---------|---------|
| `context/test_multi_document_validation.py` | F1 | 🔴 应失败 (未修复) |
| `llm/test_update_context_server_creation.py` | F2 | 🔴 应失败 (未修复) |
| `llm/test_sdk_skills_discovery.py` | F3 | 🔴 应失败 (未修复) |
| `prompts/test_template_mapping.py` | F4 | 🔴 应失败 (未修复) |
| `tools/test_update_context_allowed_keys.py` | F5 | 🔴 应失败 (未修复) |
| `integration/test_f1_f5_fixes.py` | 集成测试 | 🔴 应失败 (未修复) |

## 🚀 快速开始

### 1. 运行测试 (确认问题)

```bash
# 运行单个问题的测试
pytest tests/docuswarm/context/test_multi_document_validation.py -v
pytest tests/docuswarm/llm/test_update_context_server_creation.py -v
pytest tests/docuswarm/llm/test_sdk_skills_discovery.py -v
pytest tests/docuswarm/prompts/test_template_mapping.py -v
pytest tests/docuswarm/tools/test_update_context_allowed_keys.py -v

# 运行所有测试
pytest tests/docuswarm/ -v --tb=short
```

### 2. 按照快速实施指南执行修复

参考 `2026-04-08-docuswarm-f1-f5-quick-implementation-guide.md`，按天执行：

- **Day 1**: F1 - 多文档验证 (4h)
- **Day 2**: F2 - update_context 链路 (3h)
- **Day 3**: F3 - SDK Skills 路径 (2h)
- **Day 4-5**: F4 - 模板映射 (6h)
- **Day 5**: F5 - allowed_keys 传递 (2h)

### 3. 验证修复

```bash
# 运行调试工具验证
python tools/docuswarm_all_findings_runner.py

# 运行所有测试确认通过
pytest tests/docuswarm/ -v
```

## 📊 问题严重程度与优先级

| 问题 | 严重程度 | 优先级 | 预计工作量 |
|------|---------|--------|-----------|
| F1 - 多文档验证 | 🔴 Critical | P0 | 4h |
| F2 - update_context | 🟠 High | P0 | 3h |
| F3 - SDK Skills | 🟠 High | P0 | 2h |
| F4 - 模板映射 | 🟠 High | P1 | 6h |
| F5 - allowed_keys | 🟡 Medium | P1 | 2h |

## 🎯 修复目标

### F1: 多文档验证 (Critical)
- ✅ 多文档格式通过验证
- ✅ 不强制要求顶层 file_path/sha256
- ✅ 正确检测文档数量
- ✅ 验证每个子文档
- ✅ 单文档验证不受影响

### F2: update_context 链路 (High)
- ✅ `SessionManager` 接受 `pipeline_id` 参数
- ✅ `SessionManager._create_options()` 传递 `pipeline_id`
- ✅ `IndependentAgent` 传递 `pipeline_id`
- ✅ 默认运行时创建 `shared-context` MCP server

### F3: SDK Skills 发现 (High)
- ✅ `SessionManager` 支持独立的 `cwd` 和 `output_dir`
- ✅ `Orchestrator` 检测项目根目录
- ✅ `cwd` 指向项目根目录 (包含 `.claude/skills/`)
- ✅ SDK 原生 Skills 发现正常工作

### F4: 模板映射 (High)
- ✅ `template_mapping.yaml` 配置存在
- ✅ `ContractBuilder` 应用模板 ID 映射
- ✅ 所有节点 deliverable_type 都能匹配模板
- ✅ 匹配率达到 100%
- ✅ 多文档节点支持 template_mapping 配置

### F5: allowed_keys 传递 (Medium)
- ✅ `create_update_context_server()` 接受 `allowed_keys` 参数
- ✅ `NodeToolFilter.create_mcp_servers()` 传递 `allowed_keys`
- ✅ `UpdateContextTool` 接收并使用节点级白名单
- ✅ 节点级白名单与全局白名单合并

## 📝 关键代码变更文件

需要修改的文件清单：

```
autoBMAD/
├── docuswarm/
│   ├── context/
│   │   └── validator.py                    # F1
│   ├── llm/
│   │   ├── session_manager.py              # F2, F3
│   │   └── tool_filter.py                  # F2, F5
│   ├── agents/
│   │   └── independent.py                  # F2, F3
│   ├── pipeline/
│   │   └── orchestrator.py                 # F3
│   ├── prompts/
│   │   └── contract_builder.py             # F4
│   ├── tools/
│   │   └── update_context_sdk.py           # F5
│   └── templates/
│       └── template_mapping.yaml (new)     # F4
└── nodes/
    └── loader.py                           # F5 (确认支持)
```

## 🧪 测试执行示例

### 失败测试示例 (修复前)

```bash
$ pytest tests/docuswarm/context/test_multi_document_validation.py -v

tests/docuswarm/context/test_multi_document_validation.py::TestMultiDocumentValidation::test_multi_document_should_pass_validation FAILED
tests/docuswarm/context/test_multi_document_validation.py::TestMultiDocumentValidation::test_multi_document_should_detect_correct_document_count FAILED

========================= 2 failed in 0.50s =========================
```

### 通过测试示例 (修复后)

```bash
$ pytest tests/docuswarm/context/test_multi_document_validation.py -v

tests/docuswarm/context/test_multi_document_validation.py::TestMultiDocumentValidation::test_multi_document_should_pass_validation PASSED
tests/docuswarm/context/test_multi_document_validation.py::TestMultiDocumentValidation::test_multi_document_should_detect_correct_document_count PASSED

========================= 2 passed in 0.50s =========================
```

## 🔧 调试工具

运行现有调试工具验证问题状态：

```bash
python tools/docuswarm_f1_multidoc_validator_debugger.py
python tools/docuswarm_f2_update_context_debugger.py
python tools/docuswarm_f3_sdk_skills_debugger.py
python tools/docuswarm_f4_template_mapping_debugger.py
python tools/docuswarm_f5_allowed_keys_debugger.py

# 批量运行所有调试工具
python tools/docuswarm_all_findings_runner.py
```

## 📈 实施进度跟踪

复制以下清单跟踪修复进度：

```markdown
- [ ] F1 - 多文档验证
  - [ ] 编写失败测试
  - [ ] 修改 validator.py
  - [ ] 测试通过
  - [ ] 回归测试通过
- [ ] F2 - update_context
  - [ ] 编写失败测试
  - [ ] 修改 session_manager.py
  - [ ] 修改 independent.py
  - [ ] 测试通过
  - [ ] 回归测试通过
- [ ] F3 - SDK Skills
  - [ ] 编写失败测试
  - [ ] 修改 orchestrator.py
  - [ ] 修改 independent.py
  - [ ] 测试通过
  - [ ] 回归测试通过
- [ ] F4 - 模板映射
  - [ ] 编写失败测试
  - [ ] 创建 template_mapping.yaml
  - [ ] 修改 contract_builder.py
  - [ ] 测试通过
  - [ ] 匹配率达到 100%
- [ ] F5 - allowed_keys
  - [ ] 编写失败测试
  - [ ] 修改 update_context_sdk.py
  - [ ] 修改 tool_filter.py
  - [ ] 测试通过
- [ ] 集成测试
  - [ ] 所有集成测试通过
  - [ ] 全量回归测试通过
```

## 📚 参考文档

- [研究报告](../research/2026-04-08-docuswarm-implementation-gap-deep-research-report.md)
- [审计文档](../evaluation/2026-04-08-docuswarm-deep-reform-full-implementation-audit.md)
- [原始方案文档](../research/docuswarm-deep-reform/)

## 💡 提示与技巧

1. **先运行测试**: 每次修复前运行测试确认失败
2. **小步提交**: 每个问题修复后单独提交
3. **频繁测试**: 实现过程中频繁运行测试
4. **回归测试**: 修复后运行全量测试确保无回归
5. **使用调试工具**: 使用调试工具验证修复效果

## ⚠️ 注意事项

1. **备份**: 修改前备份关键文件
2. **兼容性**: 保持向后兼容，不破坏现有功能
3. **文档更新**: 修复后更新相关文档
4. **代码审查**: 提交前进行代码审查

---

*测试驱动修复方案 - 预计完成时间: 3-5 天*
