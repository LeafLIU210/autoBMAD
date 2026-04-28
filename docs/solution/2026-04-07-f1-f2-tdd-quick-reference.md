# F1/F2 TDD 快速参考

**关联方案**: `docs/solution/2026-04-07-f1-f2-runtime-integrity-tdd-plan.md`

---

## 快速开始

```bash
# 1. 创建分支
git checkout -b fix/f1-f2-runtime-integrity

# 2. 首先运行分析工具确认问题
python tools/f1_f2_deep_dive_analyzer.py

# 3. 按顺序实施修复（先测试，后实现）
```

---

## 修复检查清单

### F2: 放行 submit_execution_report ⭐ P0

- [ ] **写测试** (`tests/test_tool_filter_unit.py`)
  ```python
  def test_get_allowed_tools_includes_submit_execution_report(self):
      filter_obj = NodeToolFilter(
          node_id="test-node",
          tool_permissions=NodeToolPermissions(),
          output_dir="/tmp/test"
      )
      allowed_tools = filter_obj.get_allowed_tools()
      assert "mcp__docuswarm-deliverable-test-node__submit_execution_report" in allowed_tools
  ```

- [ ] **运行测试** → 应该失败 ❌

- [ ] **实现修复** (`autoBMAD/docuswarm/llm/tool_filter.py:153-159`)
  ```python
  if self.output_dir:
      tools.append(MCP_TOOL_NAME_FORMAT.format(
          type="deliverable", node_id=self.node_id, tool_name="create_deliverable"
      ))
      # ADD THIS:
      tools.append(MCP_TOOL_NAME_FORMAT.format(
          type="deliverable", node_id=self.node_id, tool_name="submit_execution_report"
      ))
  ```

- [ ] **运行测试** → 应该通过 ✅

- [ ] **回归测试** `pytest tests/test_tool_filter.py -v`

---

### F1: 保留完整 tool_permissions ⭐ P0

- [ ] **写测试** (`tests/test_independent_agent_unit.py`)
  ```python
  def test_rebuild_preserves_skills_config(self):
      # 验证重建后的 tool_permissions 保留 skills
      assert tool_perms.skills.sdk_native == True
      assert "bmad-domain-research" in tool_perms.skills.whitelist
  ```

- [ ] **运行测试** → 应该失败 ❌

- [ ] **实现修复** (`autoBMAD/docuswarm/agents/independent.py:974-978`)
  ```python
  # BEFORE:
  full_tool_permissions = NodeToolPermissions(
      allowed_builtin_tools=node_config.tool_permissions.allowed_builtin_tools,
      file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
      search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
  )
  
  # AFTER:
  from dataclasses import replace
  full_tool_permissions = replace(
      node_config.tool_permissions,
      file_permissions=NodeFilePermissions(allowed_read_dirs=file_dirs),
      search_permissions=NodeSearchPermissions(search_dirs=search_dirs),
  )
  ```

- [ ] **运行测试** → 应该通过 ✅

- [ ] **回归测试** `pytest tests/test_independent_agent.py -v`

---

### F1: SessionManager 检查 sdk_native (P1)

- [ ] **写测试** (`tests/test_session_manager_unit.py`)
  ```python
  def test_build_allowed_tools_excludes_skill_when_sdk_native_false(self):
      sm = SessionManager(
          cwd=Path("/tmp"),
          node_id="test-node",
          tool_permissions=NodeToolPermissions(
              skills=NodeSkillsConfig(sdk_native=False)
          )
      )
      allowed_tools = sm._build_allowed_tools()
      assert "Skill" not in allowed_tools  # Should fail before fix
  ```

- [ ] **运行测试** → 应该失败 ❌

- [ ] **实现修复** (`autoBMAD/docuswarm/llm/session_manager.py:173-217`)
  ```python
  # BEFORE:
  tools.append("Skill")
  
  # AFTER:
  if (self._tool_permissions is not None and 
      self._tool_permissions.skills.sdk_native):
      tools.append("Skill")
  ```

- [ ] **运行测试** → 应该通过 ✅

- [ ] **回归测试** `pytest tests/test_session_manager.py -v`

---

### F1: 条件设置 setting_sources (P1)

- [ ] **写测试** (`tests/test_session_manager_unit.py`)
  ```python
  def test_create_options_excludes_setting_sources_when_sdk_native_false(self):
      sm = SessionManager(..., tool_permissions=NodeToolPermissions(
          skills=NodeSkillsConfig(sdk_native=False)
      ))
      options = sm._create_options(mode="agent", yolo=True)
      assert not hasattr(options, 'setting_sources')
  ```

- [ ] **运行测试** → 应该失败 ❌

- [ ] **实现修复** (`autoBMAD/docuswarm/llm/session_manager.py:238-243`)
  ```python
  # BEFORE:
  options_dict["setting_sources"] = ["project"]
  
  # AFTER:
  if (self._tool_permissions is not None and 
      self._tool_permissions.skills.sdk_native):
      options_dict["setting_sources"] = ["project"]
  ```

- [ ] **运行测试** → 应该通过 ✅

---

## 文件修改对照表

| 修复 | 文件 | 行号 | 变更类型 |
|------|------|------|---------|
| F2 | `tool_filter.py` | 153-159 | 添加 submit_execution_report |
| F1 | `independent.py` | 974-978 | 使用 dataclasses.replace |
| F1 | `session_manager.py` | 173-217 | 条件添加 "Skill" |
| F1 | `session_manager.py` | 238-243 | 条件设置 setting_sources |

---

## 测试运行速查

```bash
# 全部 F1/F2 测试
pytest tests/ -k "f1 or f2 or F1 or F2" -v

# 仅单元测试
pytest tests/test_*_unit.py -v

# 仅集成测试
pytest tests/test_*_integration.py -v

# 回归测试套件
pytest tests/test_tool_filter.py tests/test_independent_agent.py tests/test_session_manager.py -v

# 带覆盖率
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=term-missing
```

---

## 常见问题

### Q: 测试失败但代码看起来正确？
**A**: 检查是否使用了正确的 fixture 和 mock。确保 `NodeLoader.load` 被正确 mock。

### Q: 如何验证修复真的生效？
**A**: 运行端到端测试，检查实际的 `allowed_tools` 输出：
```python
print(f"Allowed tools: {allowed_tools}")
```

### Q: 回归测试失败？
**A**: 
1. 确认没有破坏现有接口
2. 检查默认行为是否一致
3. 使用 `git diff` 对比修改

---

## 验证清单

实施完成后，确认以下检查项：

- [ ] `pytest tests/ -k "f1 or f2"` 全部通过
- [ ] `python tools/f1_f2_deep_dive_analyzer.py` 不再报告 CRITICAL 问题
- [ ] 所有现有测试继续通过
- [ ] 代码审查通过
- [ ] 文档已更新

---

**最后更新**: 2026-04-07
