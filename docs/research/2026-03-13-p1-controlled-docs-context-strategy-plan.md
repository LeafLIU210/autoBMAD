---
**文档状态**: ❌ 已废弃 (Superseded)  
**废弃日期**: 2026-03-17  
**替代决策**: F4 - docs-free  
**说明**: 本文档描述的受控 docs 上下文策略已被废弃。产品决策已改为工作流完全不读取 docs/ 目录。参见 `docs/research/2026-03-17-docs-free-workflow-dependency-research.md` 和 `docs/DECISIONS.md`。
---

# P1 Refactor Plan: Controlled Docs Context Expansion

## 1. Problem Statement

当前 docs 能力的问题不是“没有工具”，而是“没有策略”。

现在系统里已有:

- `list_docs_files`
- `read_docs_file`
- `update_docs_file`
- `create_document_set`

但没有定义:

- 哪些节点应该优先读哪些文档
- 什么时候读 docs
- 读多少
- 读完如何压缩进上下文
- 哪些工具默认不应该开放

## 2. 设计目标

把 docs 访问从“随缘工具调用”升级为“受控上下文扩展策略”。

最小目标:

1. 有入口策略
2. 有读取顺序
3. 有大小限制
4. 有节点级 allowlist
5. 有摘要化步骤

## 3. 备选方案

### 方案 A: 引入 `ContextResolver`，在 CLI 端直接解析所有 `@path`

优点:
- 用户可显式引用文档

缺点:
- 仍不能解决 token 膨胀和节点差异策略

### 方案 B: 在执行前增加 `DocsContextPolicy`

优点:
- 最符合当前系统结构
- 可按节点配置 allowlist
- 可与统一上下文协议对齐

缺点:
- 需要增加一个摘要阶段

### 方案 C: 完全交给 agent 自主决定读哪些 docs

缺点:
- 最不可控

推荐: 方案 B

## 4. 推荐流程

```text
NodeExecutionContextBuilder
  -> DocsContextPolicy.select(node_id, explicit_refs, default_refs)
  -> list eligible docs
  -> read selected docs
  -> summarize each doc into bounded note
  -> inject summaries into execution_context.docs_context
  -> expose read_docs_file as fallback tool only
```

## 5. 受控策略细节

### 节点默认 allowlist

- `analyst`: `docs/research`, `docs/plan`
- `pm`: `docs/plan`, `docs/research`, `docs/architecture`
- `ux`: `docs/plan`, `docs/design`
- `architect`: `docs/architecture`, `docs/research`
- `po`: `docs/plan`, `docs/architecture`, `docs/research`

### 大小限制

- 单文档摘要限制: 300-500 tokens 等价内容
- 单节点 docs_context 文档数限制: 3-5
- 原文只在 fallback 读取时按需使用，不直接整体注入 prompt

### 默认工具暴露策略

- `list_docs_files`: 保留
- `read_docs_file`: 保留
- `update_docs_file`: 从默认 IndependentAgent 工具集移出
- `create_document_set`: 仅在需要多文档输出的节点或模式中启用

## 6. 为什么不把整个 docs 目录灌进 prompt

因为这会直接放大当前系统最脆弱的问题:

- task 契约弱
- 状态协议不稳
- token 预算不可控

docs 只有在“上下文协议稳定”后，才能成为受控增强层。

## 7. 代码改动边界

- `autoBMAD/docuswarm/agents/configs/independent_agent.yaml`
- `autoBMAD/docuswarm/tools/read_docs_file.py`
- `autoBMAD/docuswarm/tools/list_docs_files.py`
- `autoBMAD/docuswarm/node_execution/context_builder.py`

新增建议:

- `autoBMAD/docuswarm/context/docs_policy.py`
- `autoBMAD/docuswarm/context/docs_summary.py`

## 8. 与 `@docs/...` 的关系

本方案不否定未来的 `@path` 注入。  
但建议顺序是:

1. 先建立 `DocsContextPolicy`
2. 再把 `@path` 解析接入该策略

而不是先做一个“看到 @path 就全量读取”的 resolver。

## 9. 验收标准

- 每个节点都有可解释的 docs 选择策略
- docs 进入 prompt 前都先被摘要化
- 默认工具集中不再暴露高风险或低必要性的 docs 写工具
- 用户显式引用的文档也会经过 allowlist 和摘要化边界

