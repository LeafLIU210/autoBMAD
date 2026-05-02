# SummaryAgent Deep Research Report

Generated from: /home/leafliu/autoBMAD/autoBMAD/docuswarm
Log file: /home/leafliu/autoBMAD/logs/docuswarm-2026-05-01.log

---

## SUM-1: SummaryAgent 仍依赖裸 json.loads() 解析 LLM 文本，当前成功依赖重试运气
**Severity:** High

### Evidence
- Log confirms: SummaryAgent encountered 'Invalid JSON response' error.
- The LLM returned fenced JSON (```json ... ```), which json.loads() cannot parse.
- Retry attempt 1 failed due to fenced JSON. Second attempt returned bare JSON and succeeded.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/summary.py: Uses bare json.loads(summary_text) without fenced JSON handling.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/summary.py: single_prompt() is called WITHOUT output_format parameter, so structured output extraction is not used.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py: EvaluatorAgent already has structured output handling / fallback parser. SummaryAgent should align with this pattern.

### Code Snippets
**log excerpt**
```
```json
{
  "summary": "本文档定义了一个极简 Python CLI 项目（计算 1+1）的完整上下文，旨在作为验证 DocuSwarm 文档流水线端到端运行能力的最小化测试用例。文档涵盖了项目目标、领域背景、功能与非功能需求、约束条件以及流水线各阶段（Analyst、PM、UX、Architect、PO）的成功判定标准。",
  "key_points": [
    "项目目标是创建一个计算 1+1 并输出结果的单文件 Python CLI 脚本",
    "作为最小化任务验证 DocuSwarm 多代理文档流水线的端到端能力",
    "流水线需产出业务分析、PRD、交互设计、技术架构和 Backlog 五类文档",
    "功能需求包括核心计算、CLI 入口、特定输出格式 `1 + 1 = 2` 和退出码 0",
    "非功能需求强调代码不超过 10 行、无第三方依赖、包含简短注释",
    "约束条件禁止 eval()、禁止通用化扩展，要求输出完整等式",
    "成功标准覆盖五个代理角色各自产出的文档质量与完整性"
  ],
  "str
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/summary.py**
```
                        system_prompt=system_prompt,
                    ),
                    timeout=perf_config.timeout_per_document_seconds,
                )

                # Extract content from response
                summary_text = self._extract_text_from_response(response)
                if not summary_text:
                    raise LLMSummaryError("Empty response from LLM")

                # Parse JSON
                try:
                    data = json.loads(summary_text)
                except json.JSONDecodeError as e:
                    raise LLMSummaryError(f"Invalid JSON response: {e}") from e

                # Validate schema
                if not self._validate_summary_schema(data):
```

**Recommendation:** 最低限度: 把 json.loads(summary_text) 替换为 extract_json(summary_text)。推荐方案: 调用 single_prompt() 时传入 output_format=SUMMARY_OUTPUT_SCHEMA，并使用 _extract_structured_output() + extract_json() 双重 fallback。

---

## SUM-2: SummaryAgent 每次重新总结文档，缓存配置未真正形成可观察缓存语义
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/config/summary_agent.yaml: Config declares caching, but no cache key/ttl/hit-miss logic exists in code.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/summary.py: Mentions cache in code, but no persistent cache implementation found.
- Log: 1 summary starts, 1 completes. No cache_hit events found.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/config/summary_agent.yaml**
```
# Document summary caching settings (for future implementation in Story 36.6+)
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/config/summary_agent.yaml**
```
caching:
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/config/summary_agent.yaml**
```
# Enable/disable caching
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/config/summary_agent.yaml**
```
enable: true
```

**Recommendation:** 若暂不实现，把配置注释改为 reserved_for_future。若实现，以 path+sha256(content)+schema_version 为 cache key，记录 summary_cache_hit/miss，并支持跨 pipeline 持久化。

---

## SUM-3: EvaluatorAgent 与 SummaryAgent 在结构化输出处理上存在能力差距
**Severity:** Medium

### Evidence
- EvaluatorAgent capabilities: {'extract_structured': False, 'extract_json': True, 'output_format': True}
- SummaryAgent capabilities: {'extract_structured': False, 'extract_json': False, 'output_format': False}
- GAP CONFIRMED: SummaryAgent lacks structured output handling that EvaluatorAgent has.

**Recommendation:** 统一 Agent 基类或混入类，提供标准化的 LLM 响应解析流程: structured_output -> extract_json -> manual retry。

---
