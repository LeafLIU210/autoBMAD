# Python CLI: 计算 1+1 — Project Context

## Subject

创建一个极简 Python CLI 程序，计算并输出 1+1 的结果。

## Project Overview

本项目目的是通过一个最小化任务验证 DocuSwarm 文档流水线的端到端运行能力。
任务规模极小，便于快速观察各阶段代理的输出质量与流程正确性。

流水线应产出以下内容：
- 业务需求分析（analyst）
- 产品需求文档 PRD（pm）
- 界面交互设计（ux）
- 技术架构文档（architect）
- 产品 Backlog（po）

## Domain Context

**功能**: 计算 1+1 并在终端输出结果
**语言**: Python 3.11+
**目标用户**: 开发者验证 CLI 工具运行环境
**交付形式**: 单文件 Python 脚本，支持 `python calc.py` 直接运行

## Functional Requirements Summary

1. **核心计算**: 执行 `1 + 1` 并将结果输出到标准输出
2. **CLI 入口**: 脚本可通过 `python calc.py` 直接运行，无需参数
3. **输出格式**: 输出一行文本，格式为 `1 + 1 = 2`
4. **退出码**: 正常运行退出码为 0

## Non-Functional Requirements

- **简洁性**: 实现代码不超过 10 行
- **无依赖**: 仅使用 Python 标准库，无第三方依赖
- **可读性**: 代码应包含简短注释说明计算逻辑

## Constraints

- 不使用 `eval()` 或动态表达式求值
- 硬编码 `1 + 1` 运算，不做通用化计算器扩展
- 输出必须包含完整等式（`1 + 1 = 2`），不能只输出数字

## Success Criteria

流水线运行成功的判断标准：
1. Analyst 完成需求背景分析，识别出核心功能点
2. PM 产出包含验收标准的 PRD
3. UX 给出 CLI 输出格式的界面设计说明
4. Architect 给出模块结构与实现方案
5. PO 产出包含至少一个 Epic 和对应 Story 的 Backlog
