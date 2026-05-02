# Evaluator Quality Gate Deep Research Report

Generated from: /home/leafliu/autoBMAD/autoBMAD/docuswarm
Output dir: /home/leafliu/autoBMAD/output/pipeline-1777610205512-d6ce6a21

---

## QG-1: 输出质量门对'批准但有明显事实错误/矛盾'的容忍度偏高
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py: Default APPROVED threshold appears to be >= 0.70 alignment_score.
- Log analysis: Found alignment scores: ['0.931', '0.931', '0.9375', '0.9375', '0.919', '0.919', '0.9534999999999999', '0.9534999999999999', '0.9199999999999999', '0.9199999999999999']. All appear to be above 0.90, which is well above the 0.70 threshold.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py: Evaluator mentions factual/error concepts, but no hard gate prevents APPROVED verdict when factual errors are present in issues_found.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py**
```python
    # P0 Fix: Default thresholds now serve as fallback only
    # Actual thresholds are loaded from node evaluator.yaml configuration
    DEFAULT_APPROVAL_THRESHOLD = 0.70
    DEFAULT_BLOCKED_THRESHOLD = 0.50

```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py**
```python

### Verdict Thresholds
- APPROVED: Alignment score >= 0.70
- NEEDS_REVISION: 0.50 < Alignment score < 0.70
- BLOCKED: Alignment score <= 0.50
```
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py**
```python
### Verdict Thresholds
- APPROVED: Alignment score >= 0.70
- NEEDS_REVISION: 0.50 < Alignment score < 0.70
- BLOCKED: Alignment score <= 0.50

```

**Recommendation:** 引入 hard gate: issues_found 中包含 factual error 且影响需求/技术决策时，最高 verdict 为 NEEDS_REVISION。存在 blocking question 时，node/pipeline 状态不得为 completed。

---

## QG-2: Evaluator 主要按加权均分判定，对离散缺陷缺少 hard gate
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py: Evaluator determines verdict, likely based on weighted criteria scores.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/evaluator.py**
```python
This module provides the EvaluatorAgent class which:
- Loads evaluation criteria from nodes/{node_id}/evaluator.yaml
- Calls LLM with Claude Thinking mode (temperature 0.5, max_tokens 8000)
- Scores deliverables against criteria (0.0-1.0 scale)
- Calculates weighted alignment score using criterion weights
- Returns verdict (APPROVED | NEEDS_REVISION | BLOCKED) based on thresholds
- Maintains context isolation - NO access to private_reasoning from Independent Agent
- Updated to support SessionManager (Story 7.3)
- Updated to use session_manager.single_prompt() SDK API (Story 7.5)
"""

from __future__ import annotations

```

**Recommendation:** 增加离散缺陷检查层: 在 score-based verdict 之后，遍历 issues_found 检查 是否存在 factual_error、blocking_question、ac_ambiguity 等标签，若有则强制降级为 NEEDS_REVISION 或 BLOCKED。

---

## QG-3: 交付物中中英文混排和编号体系不一致
**Severity:** Low

### Evidence
- analyst-report.md: Found ID patterns: ['FR-001(5)', 'FR-(34)']. Line count: 327.
- prd.md: Found ID patterns: ['FR-01(2)', 'FR-(11)']. Line count: 158.
- epics-stories.md: Found ID patterns: ['Story(47)', 'Epic(25)']. Line count: 281.

### File Samples
**epics-stories.md**
```markdown
# Python CLI: 计算 1+1 — 产品 Backlog (Epics & Stories)
```

**Recommendation:** 统一 ID 规范: FR-001、NFR-001、AC-001，并要求下游保留上游 ID。

---

## QG-4: 极简任务的架构输出过度展开
**Severity:** Low

### Evidence
- architecture.md: 236 lines for a 'compute 1+1' CLI task.
- Contains diagram types: ['Mermaid', 'C4', 'Sequence', 'Flowchart']. For a 10-line script, this is excessive.

### File Samples
**architecture.md**
```markdown
# Python CLI: 计算 1+1 — 技术架构文档
## 1. Architecture Vision
### 1.1 架构目标
### 1.2 架构原则
### 1.3 架构范围
## 2. System Components
### 2.1 组件清单
### 2.2 组件职责详述
#### `calc.py` — CLI 入口脚本
### 2.3 模块结构
## 3. Data Flow
### 3.1 执行流程图
### 3.2 数据流转说明
## 4. Technology Stack
### 4.1 运行时与语言
```

**Recommendation:** 为 trivial/minimal task 增加 lightweight architecture 模板: 目标与约束、文件结构、参考实现、验收命令、排除项。

---
