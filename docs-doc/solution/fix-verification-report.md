# Pipeline Timeout 修复验证报告

**日期**: 2026-04-06  
**测试状态**: ✅ 全部通过

---

## 修复实施状态

| Fix | 优先级 | 描述 | 测试文件 | 状态 | 测试数 |
|-----|--------|------|----------|------|--------|
| Fix-1 | P0 | contract_builder._build_instructions_section() JSON 示例 | test_contract_builder_fix1.py | ✅ | 6/6 |
| Fix-2 | P0 | markdown_fallback 分支 + _extract_create_deliverable_result() | test_independent_agent_fix2.py | ✅ | 7/7 |
| Fix-3 | P1 | 超时诊断日志增强 | test_session_manager_fix3.py | ✅ | 3/3 |
| Fix-4 | P1 | CreateDeliverableTool output_dir 验证 | test_create_deliverable_fix4.py | ✅ | 4/4 |
| Fix-6 | P1 | system_prompt 路径对齐 | test_prompt_path_alignment_fix6.py | ✅ | 2/2 |
| - | - | 回归测试 | test_contract_builder_regression.py | ✅ | 3/3 |

**总计**: 25/25 测试通过 ✅

---

## 代码变更摘要

### Fix-1: contract_builder.py
**文件**: `autoBMAD/docuswarm/prompts/contract_builder.py`

**修改内容**:
- 在 `_build_instructions_section()` 的 JSON 示例中添加了 `file_path` 和 `sha256` 字段
- 添加了 IMPORTANT 提示，明确告知 LLM 必须从工具输出中获取这些字段
- 更新了 Execution Workflow 说明

**Before**:
```json
{
  "deliverable": {
    "title": "Brief title of what you created",
    "content": "Brief summary (1-2 sentences, NOT the full document)"
  },
  ...
}
```

**After**:
```json
{
  "deliverable": {
    "title": "Brief title of what you created",
    "content": "Brief summary (1-2 sentences, NOT the full document)",
    "file_path": "path/returned/by/create_deliverable/tool.md",
    "sha256": "hash_returned_by_create_deliverable_tool"
  },
  ...
}
```

### Fix-2: independent.py
**文件**: `autoBMAD/docuswarm/agents/independent.py`

**修改内容**:
1. 新增 `_extract_create_deliverable_result()` 方法
   - 从 messages 中提取 tool_result 的返回内容
   - 正确处理 JSON 字符串格式的 content（先 json.loads）
   - 跳过 is_error=True 的结果
   - 返回 (file_path, sha256) 元组

2. 修改 `_parse_response()` 中的 markdown_fallback 分支
   - 先调用 `_extract_create_deliverable_result()` 获取工具返回
   - 如果有工具返回，使用工具返回的 file_path/sha256 补全数据
   - 如果没有工具返回，抛出 ResponseParseAgentError 而不是静默失败

### Fix-3: session_manager.py
**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

**修改内容**:
- 在 `ClaudeSessionWrapper.prompt()` 中添加 `messages_received` 计数器
- 在超时日志中记录 `messages_received_before_timeout`

**Before**:
```python
except TimeoutError as e:
    self._logger.error(
        "prompt_timeout",
        timeout_seconds=effective_timeout,
        message_length=len(message),
    )
```

**After**:
```python
messages_received = 0
try:
    async with asyncio.timeout(effective_timeout):
        async for msg in self._client.receive_messages():
            messages_received += 1
            yield msg
except TimeoutError as e:
    self._logger.error(
        "prompt_timeout",
        timeout_seconds=effective_timeout,
        message_length=len(message),
        messages_received_before_timeout=messages_received,
    )
```

### Fix-4: CreateDeliverableTool
**文件**: `autoBMAD/docuswarm/tools/create_deliverable.py` (验证)

**状态**: 工具已支持 output_dir 参数，测试验证了功能正常

### Fix-6: 路径对齐
**状态**: 由 Fix-1 自动覆盖，测试验证了两条路径都包含 file_path/sha256 示例

---

## 测试执行命令

```bash
# 运行全部修复测试
python -m pytest tests/unit/prompts/ tests/unit/agents/ tests/unit/llm/ tests/unit/tools/ -v

# 运行单个 Fix 测试
python -m pytest tests/unit/prompts/test_contract_builder_fix1.py -v
python -m pytest tests/unit/agents/test_independent_agent_fix2.py -v
python -m pytest tests/unit/llm/test_session_manager_fix3.py -v
python -m pytest tests/unit/tools/test_create_deliverable_fix4.py -v
python -m pytest tests/unit/agents/test_prompt_path_alignment_fix6.py -v
python -m pytest tests/unit/prompts/test_contract_builder_regression.py -v
```

---

## 预期效果

实施这些修复后，Pipeline 超时与 MISSING_FILE_PATH 错误应该得到解决：

1. **Fix-1**: LLM 现在明确知道需要在 JSON 响应中包含 file_path 和 sha256
2. **Fix-2**: 即使 LLM 超时或返回 Markdown，也能从工具返回中提取 file_path/sha256
3. **Fix-3**: 更好的诊断日志，便于分析超时原因
4. **Fix-4**: 工具写入文件的目录可控
5. **Fix-6**: 两条 prompt 路径一致，避免行为差异

---

## 后续建议

1. **端到端测试**: 在真实 Pipeline 中运行验证
2. **监控**: 部署后监控是否还有 MISSING_FILE_PATH 错误
3. **性能**: 观察超时率是否下降
4. **Fix-5**: 状态保存与重试优化（P2 优先级，可选）

---

*报告生成时间*: 2026-04-06  
*测试环境*: Python 3.12.10, Windows  
*虚拟环境*: venv
